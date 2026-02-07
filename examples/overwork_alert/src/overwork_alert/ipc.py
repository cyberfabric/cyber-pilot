"""Local-only control channel (Unix domain socket + JSON request/response)."""

from __future__ import annotations

import json
import os
import socket
import socketserver
import threading
from dataclasses import dataclass
from typing import Any, Callable


class ControlChannelError(RuntimeError):
    """Raised when the CLI cannot communicate with the daemon."""

    pass


@dataclass(frozen=True)
class ControlRequest:
    """Validated control request payload."""

    cmd: str


def _read_all(rfile) -> bytes:
    chunks: list[bytes] = []
    while True:
        buf = rfile.read(4096)
        if not buf:
            break
        chunks.append(buf)
    return b"".join(chunks)


class _ControlHandler(socketserver.StreamRequestHandler):
    """Socket handler for a single request/response."""

    # @cpt-state:cpt-overwork-alert-spec-cli-control-state-request-lifecycle:p1
    def handle(self) -> None:
        raw = _read_all(self.rfile)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.wfile.write(json.dumps({"ok": False, "error": "invalid_json"}).encode("utf-8"))
            return

        if not isinstance(data, dict):
            self.wfile.write(json.dumps({"ok": False, "error": "invalid_request"}).encode("utf-8"))
            return

        cmd = data.get("cmd")
        if not isinstance(cmd, str) or not cmd:
            self.wfile.write(json.dumps({"ok": False, "error": "invalid_command"}).encode("utf-8"))
            return

        # @cpt-begin:cpt-overwork-alert-spec-cli-control-state-request-lifecycle:p1:inst-transition-validated
        req = ControlRequest(cmd=cmd)
        # @cpt-end:cpt-overwork-alert-spec-cli-control-state-request-lifecycle:p1:inst-transition-validated

        handler: Callable[[ControlRequest], dict[str, Any]] = self.server.request_handler  # type: ignore[attr-defined]
        resp = handler(req)

        # @cpt-begin:cpt-overwork-alert-spec-cli-control-state-request-lifecycle:p1:inst-transition-responded
        self.wfile.write(json.dumps(resp).encode("utf-8"))
        # @cpt-end:cpt-overwork-alert-spec-cli-control-state-request-lifecycle:p1:inst-transition-responded


class _ThreadingUnixStreamServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


class ControlServer:
    """Threaded Unix socket server providing local control commands."""

    def __init__(
        self,
        *,
        socket_path: str,
        request_handler: Callable[[ControlRequest], dict[str, Any]],
    ) -> None:
        self._socket_path = socket_path
        self._request_handler = request_handler
        self._server: _ThreadingUnixStreamServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def socket_path(self) -> str:
        return self._socket_path

    def start(self) -> None:
        """Start the control server in a background thread."""
        self._cleanup_stale_socket()

        server = _ThreadingUnixStreamServer(self._socket_path, _ControlHandler)
        server.request_handler = self._request_handler  # type: ignore[attr-defined]
        os.chmod(self._socket_path, 0o600)

        self._server = server
        self._thread = threading.Thread(target=server.serve_forever, name="overwork-alert-ipc", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the control server and remove its socket file."""
        if not self._server:
            return

        self._server.shutdown()
        self._server.server_close()
        self._server = None
        self._cleanup_stale_socket()

    def _cleanup_stale_socket(self) -> None:
        try:
            st = os.stat(self._socket_path)
        except FileNotFoundError:
            return
        except OSError:
            return

        if not stat_is_socket(st.st_mode):
            return

        try:
            os.unlink(self._socket_path)
        except OSError:
            return


def stat_is_socket(mode: int) -> bool:
    """Return True if the given st_mode indicates a Unix domain socket."""
    return (mode & 0o170000) == 0o140000


def send_request(*, socket_path: str, payload: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    """Send one JSON request to the daemon and return the decoded response."""
    data = json.dumps(payload).encode("utf-8")

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.settimeout(timeout_seconds)
        s.connect(socket_path)
        s.sendall(data)
        try:
            s.shutdown(socket.SHUT_WR)
        except OSError:
            pass

        resp_chunks: list[bytes] = []
        while True:
            buf = s.recv(4096)
            if not buf:
                break
            resp_chunks.append(buf)

        resp_raw = b"".join(resp_chunks)
        try:
            resp = json.loads(resp_raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise ControlChannelError("Invalid response JSON") from e

        if not isinstance(resp, dict):
            raise ControlChannelError("Invalid response payload")

        return resp
    except (OSError, TimeoutError) as e:
        raise ControlChannelError("Daemon unreachable") from e
    finally:
        try:
            s.close()
        except OSError:
            pass
