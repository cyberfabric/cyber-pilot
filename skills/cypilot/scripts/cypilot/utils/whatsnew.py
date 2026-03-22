"""
Whatsnew Display Utilities

Shared helpers for displaying whatsnew entries from whatsnew.toml files.
Used by both `cpt update` (core) and `cpt kit update` (kit).
"""

import logging
import re
import sys
from pathlib import Path
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# @cpt-begin:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-whatsnew-format
_ANSI_ESCAPE_RE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|[@-Z\\-_])")
_BOLD_MARKUP_RE = re.compile(r"\*\*(.+?)\*\*")
_INLINE_CODE_RE = re.compile(r"`(.+?)`")
_ANSI_BOLD = "\033[1m"
_ANSI_CYAN = "\033[36m"
_ANSI_RESET = "\033[0m"


def strip_control_chars(text: str, *, preserve_newlines: bool = False) -> str:
    sanitized = _ANSI_ESCAPE_RE.sub("", str(text))
    sanitized = sanitized.replace("\x1b", "")
    if preserve_newlines:
        return re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", sanitized)
    return re.sub(r"[\x00-\x1f\x7f]", "", sanitized)


def _replace_bold_markup(match: re.Match[str]) -> str:
    return match.group(1)


def _replace_bold_markup_with_ansi(match: re.Match[str]) -> str:
    return f"{_ANSI_BOLD}{match.group(1)}{_ANSI_RESET}"


def _replace_inline_code_markup(match: re.Match[str]) -> str:
    return match.group(1)


def _replace_inline_code_markup_with_ansi(match: re.Match[str]) -> str:
    return f"{_ANSI_CYAN}{match.group(1)}{_ANSI_RESET}"

# @cpt-begin:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-whatsnew-version-cmp
def parse_semver(version: str) -> Tuple[int, ...]:
    """Parse semantic version string into tuple (major, minor, patch).

    Handles common formats: "1.2.3", "v1.2.3", "whatsnew.1.2.3".
    Returns (0, 0, 0) for unparseable versions.
    """
    # Strip common prefixes
    v = version.strip()
    if v.startswith("whatsnew."):
        v = v[9:]
    if v.startswith("v"):
        v = v[1:]

    prerelease = False
    if "-" in v:
        v, _, _ = v.partition("-")
        prerelease = True
    elif "+" in v:
        v, _, _ = v.partition("+")

    parts = v.split(".")
    numeric_parts = []
    found_numeric = False
    for part in parts[:3]:
        match = re.match(r"(\d+)", part)
        if match:
            numeric_parts.append(int(match.group(1)))
            found_numeric = True
        else:
            numeric_parts.append(0)
    while len(numeric_parts) < 3:
        numeric_parts.append(0)
    if not found_numeric:
        return (0, 0, 0)
    release_rank = 0 if prerelease else 1
    return (numeric_parts[0], numeric_parts[1], numeric_parts[2], release_rank)


def compare_versions(v1: str, v2: str) -> int:
    """Compare two version strings semantically.

    Returns:
        -1 if v1 < v2
         0 if v1 == v2
         1 if v1 > v2
    """
    t1 = parse_semver(v1)
    t2 = parse_semver(v2)
    if t1 < t2:
        return -1
    elif t1 > t2:
        return 1
    return 0
# @cpt-end:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-whatsnew-version-cmp


def stderr_supports_ansi() -> bool:
    """Check if stderr supports ANSI escape codes."""
    return hasattr(sys.stderr, "isatty") and sys.stderr.isatty()


def format_whatsnew_text(text: str, *, use_ansi: bool) -> str:
    """Format markdown-like text for terminal display.

    Converts **bold** and `code` to ANSI sequences when use_ansi=True,
    otherwise strips the markers.
    """
    if use_ansi:
        formatted = _BOLD_MARKUP_RE.sub(_replace_bold_markup_with_ansi, text)
        return _INLINE_CODE_RE.sub(_replace_inline_code_markup_with_ansi, formatted)
    plain = _BOLD_MARKUP_RE.sub(_replace_bold_markup, text)
    return _INLINE_CODE_RE.sub(_replace_inline_code_markup, plain)
# @cpt-end:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-whatsnew-format


def read_whatsnew(path: Path) -> Dict[str, Dict[str, str]]:
    """Read a whatsnew.toml file.

    Returns dict mapping version string to {summary, details}.
    Keys may be in format "whatsnew.X.Y.Z" (from TOML section) or just "X.Y.Z".
    """
    if not path.is_file():
        return {}
    try:
        import tomllib
    except ModuleNotFoundError as e:
        logger.debug("Failed to parse %s: %s", path, e)
        return {}
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except (FileNotFoundError, PermissionError, tomllib.TOMLDecodeError) as e:
        logger.debug("Failed to parse %s: %s", path, e)
        return {}

    result: Dict[str, Dict[str, str]] = {}

    # Handle whatsnew.toml format: [whatsnew."X.Y.Z"]
    whatsnew_section = data.get("whatsnew")
    if whatsnew_section is not None and isinstance(whatsnew_section, dict):
        for ver, entry in whatsnew_section.items():
            if isinstance(entry, dict):
                result[ver] = {
                    "summary": str(entry.get("summary", "")),
                    "details": str(entry.get("details", "")),
                }
    elif "whatsnew" not in data:
        # Fallback: direct version keys (legacy format)
        for key, entry in data.items():
            if isinstance(entry, dict):
                result[key] = {
                    "summary": str(entry.get("summary", "")),
                    "details": str(entry.get("details", "")),
                }

    return result


# @cpt-begin:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-display-entries
def _display_whatsnew_entries(
    entries: list,
    title: str,
    *,
    use_ansi: bool,
) -> None:
    """Display whatsnew entries to stderr.

    Args:
        entries: List of (version, {summary, details}) tuples, sorted ascending.
        title: Header title (e.g., "What's new in Cypilot" or "What's new in sdlc kit").
        use_ansi: Whether to use ANSI formatting.
    """
    sys.stderr.write(f"\n{'=' * 60}\n")
    sys.stderr.write(f"  {title}\n")
    sys.stderr.write(f"{'=' * 60}\n")

    for ver, entry in entries:
        ver = strip_control_chars(ver)
        summary_source = strip_control_chars(entry["summary"])
        details_source = strip_control_chars(entry["details"], preserve_newlines=True)
        summary = format_whatsnew_text(summary_source, use_ansi=use_ansi)
        # If summary wasn't changed by formatting, wrap version in bold
        if use_ansi and summary == summary_source:
            sys.stderr.write(f"\n  \033[1m{ver}: {summary_source}\033[0m\n")
        else:
            version_label = f"\033[1m{ver}:\033[0m" if use_ansi else f"{ver}:"
            sys.stderr.write(f"\n  {version_label} {summary}\n")

        if details_source:
            for line in details_source.splitlines():
                sys.stderr.write(
                    f"    {format_whatsnew_text(strip_control_chars(line), use_ansi=use_ansi)}\n"
                )

    sys.stderr.write(f"\n{'=' * 60}\n")
# @cpt-end:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-display-entries


# @cpt-begin:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-prompt-continue
def _prompt_continue(interactive: bool) -> bool:
    """Prompt user to continue or abort.

    Returns True if user acknowledged, False if aborted.
    Non-interactive mode always returns True.
    """
    if not interactive:
        return True

    sys.stderr.write("  Press Enter to continue with update (or 'q' to abort): ")
    sys.stderr.flush()
    try:
        response = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return response != "q"
# @cpt-end:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-prompt-continue


def show_core_whatsnew(
    cache_whatsnew: Dict[str, Dict[str, str]],
    installed_whatsnew: Dict[str, Dict[str, str]],
    *,
    interactive: bool = True,
) -> bool:
    """Display core whatsnew entries present in cache but missing from installed.

    Used by `cpt update` to show changes between cache and .core/ versions.

    Returns True if user acknowledged (or non-interactive), False if declined.
    """
    # Find entries in cache that are missing from installed
    missing = sorted(
        [(v, cache_whatsnew[v]) for v in cache_whatsnew if v not in installed_whatsnew],
        key=lambda t: parse_semver(t[0]),
    )
    if not missing:
        return True

    use_ansi = stderr_supports_ansi()
    _display_whatsnew_entries(missing, "What's new in Cypilot", use_ansi=use_ansi)
    return _prompt_continue(interactive)


# @cpt-begin:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-read-whatsnew
# @cpt-begin:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-read-installed-version
# @cpt-begin:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-filter-versions
# @cpt-begin:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-check-no-new
# @cpt-begin:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-sort-versions
# @cpt-begin:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-return-ack
def show_kit_whatsnew(
    kit_source_dir: Path,
    installed_version: str,
    kit_slug: str,
    *,
    interactive: bool = True,
) -> bool:
    """Display whatsnew entries for kit versions newer than installed.

    Used by `cpt kit update` to show changes between installed and source versions.

    Args:
        kit_source_dir: Path to kit source containing whatsnew.toml.
        installed_version: Currently installed version (e.g., "1.2.3").
        kit_slug: Kit identifier for display title.
        interactive: Whether to prompt for user confirmation.

    Returns:
        True if user acknowledged (or no entries to show), False if user aborted.
    """
    # Read whatsnew.toml from kit source
    whatsnew_path = kit_source_dir / "whatsnew.toml"
    whatsnew_data = read_whatsnew(whatsnew_path)

    if not whatsnew_data:
        return True  # No whatsnew file — proceed

    # Treat missing installed version as "0.0.0"
    if not installed_version:
        installed_version = "0.0.0"

    # Filter: keep versions > installed_version
    new_entries = []
    for ver, entry in whatsnew_data.items():
        if compare_versions(ver, installed_version) > 0:
            new_entries.append((ver, entry))

    if not new_entries:
        return True  # No new entries

    # Sort by version ascending
    new_entries.sort(key=lambda x: parse_semver(x[0]))

    # Display
    use_ansi = stderr_supports_ansi()
    _display_whatsnew_entries(
        new_entries,
        f"What's new in {kit_slug} kit",
        use_ansi=use_ansi,
    )
    return _prompt_continue(interactive)
# @cpt-end:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-return-ack
# @cpt-end:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-sort-versions
# @cpt-end:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-check-no-new
# @cpt-end:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-filter-versions
# @cpt-end:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-read-installed-version
# @cpt-end:cpt-cypilot-algo-kit-whatsnew-display:p1:inst-read-whatsnew
