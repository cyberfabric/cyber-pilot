"""
TOML utilities for Cypilot config files.

- Reading: stdlib ``tomllib`` (Python 3.11+)
- Writing: minimal serializer for the subset Cypilot uses
- Markdown: extract ``toml`` fenced code blocks from AGENTS.md

@cpt-algo:cpt-cypilot-algo-core-infra-config-management:p1
"""

import re
import tomllib
from pathlib import Path
from typing import Any, Dict, List, Optional

TomlData = Dict[str, Any]

_BARE_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_TOML_FENCE_RE = re.compile(
    r"```toml\s*\n(.*?)```",
    re.DOTALL,
)


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-core-infra-toml-utils:p1:inst-toml-parse
def loads(text: str) -> TomlData:
    """Parse a TOML string using stdlib tomllib."""
    return tomllib.loads(text)


def load(path: Path) -> TomlData:
    """Read and parse a TOML file."""
    with open(path, "rb") as f:
        return tomllib.load(f)
# @cpt-end:cpt-cypilot-algo-core-infra-toml-utils:p1:inst-toml-parse


# @cpt-begin:cpt-cypilot-algo-core-infra-toml-utils:p1:inst-toml-from-markdown
def parse_toml_from_markdown(text: str) -> TomlData:
    """
    Extract and merge all ``toml`` fenced code blocks from markdown text.

    Used to read config variables embedded in AGENTS.md, e.g.::

        ```toml
        cypilot = ".cypilot-adapter"
        ```

    If multiple blocks exist, later blocks override earlier keys.
    Returns empty dict if no TOML blocks found.
    """
    merged: TomlData = {}
    for m in _TOML_FENCE_RE.finditer(text):
        try:
            data = tomllib.loads(m.group(1))
            _deep_merge(merged, data)
        except tomllib.TOMLDecodeError:
            continue
    return merged
# @cpt-end:cpt-cypilot-algo-core-infra-toml-utils:p1:inst-toml-from-markdown


def _deep_merge(base: TomlData, override: TomlData) -> None:
    """Merge *override* into *base* in place (nested dicts are merged)."""
    for key, val in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(val, dict):
            _deep_merge(base[key], val)
        else:
            base[key] = val


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-core-infra-toml-utils:p1:inst-toml-serialize
def dumps(data: TomlData, header_comment: Optional[str] = None) -> str:
    """Serialize a nested dict to TOML format.

    Supports tables (``[table]``) and arrays of tables (``[[table]]``).
    """
    lines: List[str] = []
    if header_comment:
        for cl in header_comment.splitlines():
            lines.append(f"# {cl}" if cl else "#")
        lines.append("")

    _write_body(lines, data, prefix=[])

    # Strip trailing blank lines, ensure single trailing newline
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def dump(data: TomlData, path: Path, header_comment: Optional[str] = None) -> None:
    """Serialize and write a TOML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(data, header_comment), encoding="utf-8")


def _is_array_of_tables(value: Any) -> bool:
    """True if *value* is a non-empty list where every element is a dict."""
    return isinstance(value, list) and len(value) > 0 and all(isinstance(v, dict) for v in value)


def _write_body(lines: List[str], data: TomlData, prefix: List[str]) -> None:
    """Write key-value pairs, then sub-tables, then arrays of tables."""
    # Phase 1: scalars and simple arrays
    wrote_scalar = False
    for key, value in data.items():
        if isinstance(value, dict) or _is_array_of_tables(value):
            continue
        lines.append(_format_kv(key, value))
        wrote_scalar = True
    if wrote_scalar:
        lines.append("")

    # Phase 2: regular tables (dict values)
    for key, value in data.items():
        if not isinstance(value, dict):
            continue
        full = prefix + [key]
        lines.append(f"[{_join_prefix(full)}]")
        _write_body(lines, value, full)

    # Phase 3: arrays of tables (list-of-dict values)
    for key, value in data.items():
        if not _is_array_of_tables(value):
            continue
        full = prefix + [key]
        for item in value:
            lines.append(f"[[{_join_prefix(full)}]]")
            _write_body(lines, item, full)


def _join_prefix(parts: List[str]) -> str:
    return ".".join(_quote_key(k) for k in parts)


def _quote_key(key: str) -> str:
    if _BARE_KEY_RE.match(key):
        return key
    return f'"{key}"'


def _format_kv(key: str, value: Any) -> str:
    return f"{_quote_key(key)} = {_format_value(value)}"


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, list):
        items = ", ".join(_format_value(v) for v in value)
        return f"[{items}]"
    raise TypeError(f"Unsupported TOML value type: {type(value).__name__}")
# @cpt-end:cpt-cypilot-algo-core-infra-toml-utils:p1:inst-toml-serialize
