"""
Cypilot CLI output utilities — dual-mode (human / JSON) rendering.

@cpt-algo:cpt-cypilot-algo-core-infra-display-info:p1

Default mode (no flag): human-friendly output with colors, progress, explanations.
With ``--json``: machine-readable JSON on stdout (for AI agents).

Usage in commands::

    from ..utils.ui import ui

    # Progress messages (always go to stderr, suppressed in --json mode)
    ui.header("Cypilot Init")
    ui.step("Copying core files...")
    ui.success("Initialized!")
    ui.error("Cache not found")

    # Final result — JSON or human summary
    ui.result(data_dict, human_fn=_format_init)
"""

import json
import os
import sys
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Global output mode
# ---------------------------------------------------------------------------

_json_mode: bool = False


def set_json_mode(enabled: bool) -> None:
    global _json_mode
    _json_mode = enabled


def is_json_mode() -> bool:
    return _json_mode


# ---------------------------------------------------------------------------
# ANSI helpers (stdlib only, no deps)
# ---------------------------------------------------------------------------

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BLUE = "\033[34m"
_CYAN = "\033[36m"
_MAGENTA = "\033[35m"
_WHITE = "\033[37m"


def _has_color() -> bool:
    return hasattr(sys.stderr, "isatty") and sys.stderr.isatty()


def _c(code: str, text: str) -> str:
    if _has_color():
        return f"{code}{text}{_RESET}"
    return text


# ---------------------------------------------------------------------------
# Public API — progress messages (stderr, suppressed in JSON mode)
# ---------------------------------------------------------------------------

def header(title: str) -> None:
    """Print a bold section header."""
    if _json_mode:
        return
    sys.stderr.write(f"\n  {_c(_BOLD, title)}\n")


def step(msg: str) -> None:
    """Print a step indicator."""
    if _json_mode:
        return
    sys.stderr.write(f"  {_c(_CYAN, '▸')} {msg}\n")


def substep(msg: str) -> None:
    """Print an indented sub-step."""
    if _json_mode:
        return
    sys.stderr.write(f"    {msg}\n")


def success(msg: str) -> None:
    """Print a success message."""
    if _json_mode:
        return
    sys.stderr.write(f"\n  {_c(_GREEN, '✓')} {_c(_GREEN, msg)}\n")


def error(msg: str) -> None:
    """Print an error message."""
    if _json_mode:
        return
    sys.stderr.write(f"\n  {_c(_RED, '✗')} {_c(_RED, msg)}\n")


def warn(msg: str) -> None:
    """Print a warning message."""
    if _json_mode:
        return
    sys.stderr.write(f"  {_c(_YELLOW, '⚠')} {msg}\n")


def info(msg: str) -> None:
    """Print an informational line."""
    if _json_mode:
        return
    sys.stderr.write(f"  {msg}\n")


def detail(key: str, value: str) -> None:
    """Print a key: value detail line."""
    if _json_mode:
        return
    sys.stderr.write(f"    {_c(_DIM, key + ':')} {value}\n")


def hint(msg: str) -> None:
    """Print a dim hint/suggestion."""
    if _json_mode:
        return
    sys.stderr.write(f"    {_c(_DIM, msg)}\n")


def blank() -> None:
    """Print a blank line."""
    if _json_mode:
        return
    sys.stderr.write("\n")


def divider() -> None:
    """Print a thin divider."""
    if _json_mode:
        return
    sys.stderr.write(f"  {_c(_DIM, '─' * 50)}\n")


def table(headers: List[str], rows: List[List[str]], indent: int = 4) -> None:
    """Print a simple aligned table to stderr."""
    if _json_mode:
        return
    if not rows:
        return
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))
            else:
                widths.append(len(cell))
    prefix = " " * indent
    # Header
    hdr = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    sys.stderr.write(f"{prefix}{_c(_BOLD, hdr)}\n")
    sys.stderr.write(f"{prefix}{_c(_DIM, '─' * len(hdr))}\n")
    # Rows
    for row in rows:
        line = "  ".join(
            (row[i] if i < len(row) else "").ljust(widths[i])
            for i in range(len(widths))
        )
        sys.stderr.write(f"{prefix}{line}\n")


def file_action(path: str, action: str) -> None:
    """Print a file action (created/updated/unchanged)."""
    if _json_mode:
        return
    icons = {
        "created": _c(_GREEN, "+"),
        "updated": _c(_YELLOW, "~"),
        "unchanged": _c(_DIM, "="),
        "skipped": _c(_DIM, "-"),
        "deleted": _c(_RED, "×"),
        "missing_in_cache": _c(_RED, "!"),
        "preserved": _c(_DIM, "="),
        "dry_run": _c(_BLUE, "?"),
    }
    icon = icons.get(action, " ")
    sys.stderr.write(f"    {icon} {path} {_c(_DIM, f'({action})')}\n")


# ---------------------------------------------------------------------------
# Result output — the main dual-mode function
# ---------------------------------------------------------------------------

def result(
    data: Dict[str, Any],
    *,
    human_fn: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> None:
    """Output command result: JSON to stdout (--json) or human summary (default).

    Args:
        data: The result dict (always printed as JSON in --json mode).
        human_fn: Optional formatter that renders *data* as human-friendly text
                  to stderr. If None, a generic fallback is used.
    """
    if _json_mode:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    if human_fn is not None:
        human_fn(data)
        return

    # Generic fallback
    status = data.get("status", "")
    message = data.get("message", "")
    if status in ("PASS", "OK", "DRY_RUN"):
        success(f"Done ({status})" + (f" — {message}" if message else ""))
    elif status in ("FAIL", "ERROR"):
        error(message or status)
    elif status == "ABORTED":
        warn(f"Aborted" + (f": {message}" if message else ""))
    else:
        info(f"Status: {status}" + (f" — {message}" if message else ""))


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def relpath(path: str) -> str:
    """Return *path* relative to cwd, falling back to the original on error."""
    try:
        return os.path.relpath(path)
    except ValueError:
        return path


# ---------------------------------------------------------------------------
# Convenience singleton
# ---------------------------------------------------------------------------

class _UI:
    """Namespace object so commands can do ``from ..utils.ui import ui``."""
    header = staticmethod(header)
    step = staticmethod(step)
    substep = staticmethod(substep)
    success = staticmethod(success)
    error = staticmethod(error)
    warn = staticmethod(warn)
    info = staticmethod(info)
    detail = staticmethod(detail)
    hint = staticmethod(hint)
    blank = staticmethod(blank)
    divider = staticmethod(divider)
    table = staticmethod(table)
    file_action = staticmethod(file_action)
    result = staticmethod(result)
    is_json = staticmethod(is_json_mode)
    relpath = staticmethod(relpath)


ui = _UI()
