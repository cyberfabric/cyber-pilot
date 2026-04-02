"""
Unit tests for cypilot_proxy.telemetry module.
"""

import json
import os
import sys
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cypilot_proxy.telemetry import (
    _append_log,
    _build_otlp_logs,
    _collect_git_info,
    _log_error,
    _rotate_logs,
    _send_http,
    _str_attr,
    track_invocation,
)


class TestTrackInvocation(unittest.TestCase):
    """Test the top-level track_invocation function."""

    def test_disabled_by_env(self):
        """When CYPILOT_TELEMETRY=0, no thread is spawned."""
        with patch.dict(os.environ, {"CYPILOT_TELEMETRY": "0"}):
            with patch("cypilot_proxy.telemetry.threading") as mock_threading:
                track_invocation(["validate"])
                mock_threading.Thread.assert_not_called()

    def test_enabled_spawns_daemon_thread(self):
        """When enabled, a daemon thread is spawned and started."""
        env = os.environ.copy()
        env.pop("CYPILOT_TELEMETRY", None)
        with patch.dict(os.environ, env, clear=True):
            with patch("cypilot_proxy.telemetry.threading") as mock_threading:
                mock_thread = MagicMock()
                mock_threading.Thread.return_value = mock_thread
                track_invocation(["validate"])
                mock_threading.Thread.assert_called_once()
                call_kwargs = mock_threading.Thread.call_args
                self.assertTrue(call_kwargs.kwargs.get("daemon"))
                self.assertEqual(call_kwargs.kwargs["args"], ("validate",))
                mock_thread.start.assert_called_once()

    def test_empty_args_command(self):
        """Empty args should pass empty string as command."""
        env = os.environ.copy()
        env.pop("CYPILOT_TELEMETRY", None)
        with patch.dict(os.environ, env, clear=True):
            with patch("cypilot_proxy.telemetry.threading") as mock_threading:
                mock_thread = MagicMock()
                mock_threading.Thread.return_value = mock_thread
                track_invocation([])
                call_kwargs = mock_threading.Thread.call_args
                self.assertEqual(call_kwargs.kwargs["args"], ("",))

    def test_skips_version_command(self):
        """Should not spawn thread for --version."""
        env = os.environ.copy()
        env.pop("CYPILOT_TELEMETRY", None)
        with patch.dict(os.environ, env, clear=True):
            with patch("cypilot_proxy.telemetry.threading") as mock_threading:
                track_invocation(["--version"])
                mock_threading.Thread.assert_not_called()

    def test_skips_help_command(self):
        """Should not spawn thread for --help."""
        env = os.environ.copy()
        env.pop("CYPILOT_TELEMETRY", None)
        with patch.dict(os.environ, env, clear=True):
            with patch("cypilot_proxy.telemetry.threading") as mock_threading:
                track_invocation(["--help"])
                mock_threading.Thread.assert_not_called()

    def test_skips_short_help(self):
        """Should not spawn thread for -h."""
        env = os.environ.copy()
        env.pop("CYPILOT_TELEMETRY", None)
        with patch.dict(os.environ, env, clear=True):
            with patch("cypilot_proxy.telemetry.threading") as mock_threading:
                track_invocation(["-h"])
                mock_threading.Thread.assert_not_called()


class TestCollectGitInfo(unittest.TestCase):
    """Test git info collection."""

    def test_returns_dict(self):
        """Should return a dict with git config values."""
        mock_result = MagicMock()
        mock_result.stdout = "user.name Test\nuser.email test@test.com"
        with patch("cypilot_proxy.telemetry.subprocess.run", return_value=mock_result):
            info = _collect_git_info()
            self.assertIsInstance(info, dict)
            self.assertEqual(info["user.name"], "Test")

    def test_parses_git_output(self):
        """Should parse git config --get-regexp output correctly."""
        mock_result = MagicMock()
        mock_result.stdout = "user.name Test User\nuser.email test@example.com\nremote.origin.url https://example.com/repo.git"
        with patch("cypilot_proxy.telemetry.subprocess.run", return_value=mock_result):
            info = _collect_git_info()
            self.assertEqual(info["user.name"], "Test User")
            self.assertEqual(info["user.email"], "test@example.com")
            self.assertEqual(info["remote.origin.url"], "https://example.com/repo.git")

    def test_handles_subprocess_failure(self):
        """Should return empty dict on subprocess error."""
        with patch("cypilot_proxy.telemetry.subprocess.run", side_effect=OSError("git not found")):
            info = _collect_git_info()
            self.assertEqual(info, {})

    def test_handles_timeout(self):
        """Should return empty dict on timeout."""
        import subprocess
        with patch("cypilot_proxy.telemetry.subprocess.run", side_effect=subprocess.TimeoutExpired("git", 3)):
            info = _collect_git_info()
            self.assertEqual(info, {})

    def test_handles_empty_output(self):
        """Should return empty dict when git returns nothing."""
        mock_result = MagicMock()
        mock_result.stdout = ""
        with patch("cypilot_proxy.telemetry.subprocess.run", return_value=mock_result):
            info = _collect_git_info()
            self.assertEqual(info, {})

    def test_handles_malformed_lines(self):
        """Should skip lines without a space separator."""
        mock_result = MagicMock()
        mock_result.stdout = "user.name Test User\nbadline\nremote.origin.url https://example.com"
        with patch("cypilot_proxy.telemetry.subprocess.run", return_value=mock_result):
            info = _collect_git_info()
            self.assertEqual(len(info), 2)
            self.assertNotIn("badline", info)


class TestAppendLog(unittest.TestCase):
    """Test local log file writing."""

    def test_creates_log_file(self):
        """Should create a new log file and return True."""
        with TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            with patch("cypilot_proxy.telemetry.LOG_DIR", log_dir):
                record = {"timestamp": "2026-04-02T12:00:00Z", "command": "validate"}
                is_new = _append_log(record)
                self.assertTrue(is_new)
                log_files = list(log_dir.glob("*.log"))
                self.assertEqual(len(log_files), 1)
                content = log_files[0].read_text()
                data = json.loads(content.strip())
                self.assertEqual(data["command"], "validate")

    def test_appends_to_existing_file(self):
        """Should append to existing file and return False."""
        with TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            log_dir.mkdir()
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            log_file = log_dir / f"{today}.log"
            log_file.write_text('{"existing": true}\n')
            with patch("cypilot_proxy.telemetry.LOG_DIR", log_dir):
                record = {"timestamp": "2026-04-02T12:00:00Z", "command": "init"}
                is_new = _append_log(record)
                self.assertFalse(is_new)
                lines = log_file.read_text().strip().split("\n")
                self.assertEqual(len(lines), 2)


class TestRotateLogs(unittest.TestCase):
    """Test log file rotation."""

    def test_deletes_old_files(self):
        """Should delete files older than retention period."""
        with TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            log_dir.mkdir()
            old_file = log_dir / "2020-01-01.log"
            old_file.write_text("old")
            os.utime(old_file, (0, 0))
            new_file = log_dir / "2026-04-02.log"
            new_file.write_text("new")
            with patch("cypilot_proxy.telemetry.LOG_DIR", log_dir):
                with patch.dict(os.environ, {"CYPILOT_TELEMETRY_RETENTION_DAYS": "5"}):
                    _rotate_logs()
            self.assertFalse(old_file.exists())
            self.assertTrue(new_file.exists())

    def test_keeps_recent_files(self):
        """Should keep files within retention period."""
        with TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            log_dir.mkdir()
            recent_file = log_dir / "2026-04-01.log"
            recent_file.write_text("recent")
            with patch("cypilot_proxy.telemetry.LOG_DIR", log_dir):
                with patch.dict(os.environ, {"CYPILOT_TELEMETRY_RETENTION_DAYS": "5"}):
                    _rotate_logs()
            self.assertTrue(recent_file.exists())

    def test_invalid_retention_days_uses_default(self):
        """Invalid CYPILOT_TELEMETRY_RETENTION_DAYS falls back to default."""
        with TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            log_dir.mkdir()
            old_file = log_dir / "2020-01-01.log"
            old_file.write_text("old")
            os.utime(old_file, (0, 0))
            with patch("cypilot_proxy.telemetry.LOG_DIR", log_dir):
                with patch.dict(os.environ, {"CYPILOT_TELEMETRY_RETENTION_DAYS": "not_a_number"}):
                    _rotate_logs()
            self.assertFalse(old_file.exists())

    def test_zero_retention_clamped_to_one(self):
        """RETENTION_DAYS=0 should be clamped to 1, not delete today's log."""
        with TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            log_dir.mkdir()
            today_file = log_dir / datetime.now(timezone.utc).strftime("%Y-%m-%d.log")
            today_file.write_text("today")
            with patch("cypilot_proxy.telemetry.LOG_DIR", log_dir):
                with patch.dict(os.environ, {"CYPILOT_TELEMETRY_RETENTION_DAYS": "0"}):
                    _rotate_logs()
            self.assertTrue(today_file.exists())


class TestBuildOtlpLogs(unittest.TestCase):
    """Test OTLP Logs JSON payload construction."""

    def test_structure(self):
        """Should produce valid OTLP Logs JSON structure."""
        record = {
            "git_user_name": "Test User",
            "git_user_email": "test@example.com",
            "git_remote": "https://example.com/repo.git",
            "command": "validate",
        }
        payload = _build_otlp_logs(record, "1234567890000000000", "3.5.1")

        self.assertIn("resourceLogs", payload)
        resource_logs = payload["resourceLogs"]
        self.assertEqual(len(resource_logs), 1)

        resource = resource_logs[0]["resource"]
        attrs = {a["key"]: a["value"]["stringValue"] for a in resource["attributes"]}
        self.assertEqual(attrs["service.name"], "cypilot")
        self.assertEqual(attrs["service.version"], "3.5.1")

        log_record = resource_logs[0]["scopeLogs"][0]["logRecords"][0]
        self.assertEqual(log_record["timeUnixNano"], "1234567890000000000")
        self.assertEqual(log_record["severityNumber"], 9)
        self.assertEqual(log_record["severityText"], "INFO")
        self.assertEqual(log_record["body"]["stringValue"], "cpt.invocation")

        log_attrs = {a["key"]: a["value"]["stringValue"] for a in log_record["attributes"]}
        self.assertEqual(log_attrs["enduser.name"], "Test User")
        self.assertEqual(log_attrs["enduser.email"], "test@example.com")
        self.assertEqual(log_attrs["vcs.repository.url.full"], "https://example.com/repo.git")
        self.assertEqual(log_attrs["cypilot.command"], "validate")

    def test_missing_fields_default_to_empty(self):
        """Should handle missing fields gracefully."""
        record = {}
        payload = _build_otlp_logs(record, "0", "1.0")
        log_record = payload["resourceLogs"][0]["scopeLogs"][0]["logRecords"][0]
        log_attrs = {a["key"]: a["value"]["stringValue"] for a in log_record["attributes"]}
        self.assertEqual(log_attrs["enduser.name"], "")
        self.assertEqual(log_attrs["cypilot.command"], "")


class TestStrAttr(unittest.TestCase):
    """Test OTLP string attribute builder."""

    def test_format(self):
        result = _str_attr("key", "value")
        self.assertEqual(result, {"key": "key", "value": {"stringValue": "value"}})


class TestSendHttp(unittest.TestCase):
    """Test HTTP sending with error logging."""

    def test_successful_send(self):
        """Should POST JSON payload to the URL."""
        mock_resp = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("cypilot_proxy.telemetry.urlopen", return_value=mock_resp) as mock_urlopen:
            _send_http("http://localhost:4318/v1/logs", {"test": True})
            mock_urlopen.assert_called_once()
            req = mock_urlopen.call_args[0][0]
            self.assertEqual(req.full_url, "http://localhost:4318/v1/logs")
            self.assertEqual(req.get_header("Content-type"), "application/json")

    def test_http_error_logs_to_file(self):
        """Should call _log_error on HTTP failure."""
        from urllib.error import URLError
        with patch("cypilot_proxy.telemetry.urlopen", side_effect=URLError("connection refused")):
            with patch("cypilot_proxy.telemetry._log_error") as mock_log_error:
                _send_http("http://localhost:4318/v1/logs", {"test": True})
                mock_log_error.assert_called_once()
                self.assertIn("connection refused", mock_log_error.call_args[0][0])


class TestLogError(unittest.TestCase):
    """Test error logging to file."""

    def test_writes_error_record(self):
        """Should append ERROR-level JSONL record."""
        with TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            with patch("cypilot_proxy.telemetry.LOG_DIR", log_dir):
                _log_error("test error message")
                log_files = list(log_dir.glob("*.log"))
                self.assertEqual(len(log_files), 1)
                data = json.loads(log_files[0].read_text().strip())
                self.assertEqual(data["level"], "ERROR")
                self.assertEqual(data["message"], "test error message")


class TestTelemetryWorkerIntegration(unittest.TestCase):
    """Integration test: full telemetry worker flow."""

    def test_full_flow(self):
        """Worker should collect info, write log, and attempt HTTP."""
        with TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            mock_git = MagicMock()
            mock_git.stdout = "user.name Test\nuser.email test@test.com\nremote.origin.url https://example.com"
            with patch("cypilot_proxy.telemetry.LOG_DIR", log_dir), \
                 patch("cypilot_proxy.telemetry.subprocess.run", return_value=mock_git), \
                 patch.dict(os.environ, {"CYPILOT_TELEMETRY_URL": "http://localhost:4318/v1/logs"}), \
                 patch("cypilot_proxy.telemetry.urlopen") as mock_urlopen, \
                 patch("cypilot_proxy.__version__", "3.5.1-test"):
                mock_resp = MagicMock()
                mock_resp.__enter__ = MagicMock(return_value=mock_resp)
                mock_resp.__exit__ = MagicMock(return_value=False)
                mock_urlopen.return_value = mock_resp

                from cypilot_proxy.telemetry import _telemetry_worker
                _telemetry_worker("validate")

                log_files = list(log_dir.glob("*.log"))
                self.assertEqual(len(log_files), 1)
                data = json.loads(log_files[0].read_text().strip())
                self.assertEqual(data["command"], "validate")
                self.assertEqual(data["git_user_name"], "Test")
                self.assertEqual(data["git_user_email"], "test@test.com")
                self.assertEqual(data["git_remote"], "https://example.com")
                self.assertEqual(data["cypilot_version"], "3.5.1-test")
                mock_urlopen.assert_called_once()

    def test_no_http_when_url_not_set(self):
        """Worker should skip HTTP when CYPILOT_TELEMETRY_URL is not set."""
        with TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            mock_git = MagicMock()
            mock_git.stdout = "user.name Test\nuser.email test@test.com"
            env = os.environ.copy()
            env.pop("CYPILOT_TELEMETRY_URL", None)
            with patch("cypilot_proxy.telemetry.LOG_DIR", log_dir), \
                 patch("cypilot_proxy.telemetry.subprocess.run", return_value=mock_git), \
                 patch.dict(os.environ, env, clear=True), \
                 patch("cypilot_proxy.telemetry.urlopen") as mock_urlopen, \
                 patch("cypilot_proxy.__version__", "3.5.1-test"):

                from cypilot_proxy.telemetry import _telemetry_worker
                _telemetry_worker("info")

                log_files = list(log_dir.glob("*.log"))
                self.assertEqual(len(log_files), 1)
                mock_urlopen.assert_not_called()

    def test_rejects_invalid_url_scheme(self):
        """Worker should reject non-http(s) URLs and log error."""
        with TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            mock_git = MagicMock()
            mock_git.stdout = "user.name Test\nuser.email test@test.com"
            with patch("cypilot_proxy.telemetry.LOG_DIR", log_dir), \
                 patch("cypilot_proxy.telemetry.subprocess.run", return_value=mock_git), \
                 patch.dict(os.environ, {"CYPILOT_TELEMETRY_URL": "file:///etc/passwd"}), \
                 patch("cypilot_proxy.telemetry.urlopen") as mock_urlopen, \
                 patch("cypilot_proxy.__version__", "3.5.1-test"):

                from cypilot_proxy.telemetry import _telemetry_worker
                _telemetry_worker("validate")

                mock_urlopen.assert_not_called()
                log_files = list(log_dir.glob("*.log"))
                self.assertEqual(len(log_files), 1)
                lines = log_files[0].read_text().strip().split("\n")
                error_line = json.loads(lines[-1])
                self.assertEqual(error_line["level"], "ERROR")
                self.assertIn("scheme must be", error_line["message"])

    def test_worker_error_logged_to_file(self):
        """Worker exceptions should be logged, not swallowed silently."""
        with TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            with patch("cypilot_proxy.telemetry.LOG_DIR", log_dir), \
                 patch("cypilot_proxy.telemetry._collect_git_info", side_effect=RuntimeError("boom")):

                from cypilot_proxy.telemetry import _telemetry_worker
                _telemetry_worker("validate")

                log_files = list(log_dir.glob("*.log"))
                self.assertEqual(len(log_files), 1)
                data = json.loads(log_files[0].read_text().strip())
                self.assertEqual(data["level"], "ERROR")
                self.assertIn("boom", data["message"])


if __name__ == "__main__":
    unittest.main()
