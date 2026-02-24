"""
Root AGENTS.md Integrity Check

Verifies and re-injects the managed block in root AGENTS.md on every invocation.

@cpt-algo:cpt-cypilot-algo-core-infra-inject-root-agents:p1
@cpt-dod:cpt-cypilot-dod-core-infra-agents-integrity:p1
"""

import re
from pathlib import Path
from typing import Optional

MARKER_START = "<!-- @cpt:root-agents -->"
MARKER_END = "<!-- /@cpt:root-agents -->"

# Regex to extract {cypilot} variable value from the managed block table
_CYPILOT_VAR_RE = re.compile(
    r"\|\s*`\{cypilot\}`\s*\|\s*`([^`]+)`\s*\|"
)


def compute_managed_block(install_dir: str) -> str:
    """Compute the managed block content for root AGENTS.md."""
    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-compute-block
    return (
        f"{MARKER_START}\n"
        f"# Cypilot AI Agent Navigation\n"
        f"\n"
        f"**Version**: 1.2\n"
        f"\n"
        f"---\n"
        f"\n"
        f"## Variables\n"
        f"\n"
        f"| Variable | Value | Description |\n"
        f"|----------|-------|-------------|\n"
        f"| `{{cypilot}}` | `@/{install_dir}` | Cypilot install directory |\n"
        f"\n"
        f"## Navigation Rules\n"
        f"\n"
        f"ALWAYS open and follow `{{cypilot}}/config/AGENTS.md` FIRST\n"
        f"\n"
        f"{MARKER_END}"
    )
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-compute-block


def read_cypilot_path(project_root: Path) -> Optional[str]:
    """
    Read the {cypilot} variable from root AGENTS.md managed block.

    Returns the install directory path (relative to project root, e.g. '.cypilot')
    or None if AGENTS.md doesn't exist or doesn't contain the variable.
    """
    agents_file = project_root / "AGENTS.md"
    if not agents_file.is_file():
        return None
    try:
        content = agents_file.read_text(encoding="utf-8")
    except OSError:
        return None
    if MARKER_START not in content:
        return None
    m = _CYPILOT_VAR_RE.search(content)
    if m is None:
        return None
    value = m.group(1).strip()
    # Strip @/ prefix — it means "relative to project root"
    if value.startswith("@/"):
        value = value[2:]
    return value


def find_project_root(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Find the project root by walking up looking for AGENTS.md with @cpt:root-agents marker."""
    current = (start_dir or Path.cwd()).resolve()
    for parent in [current, *current.parents]:
        agents_file = parent / "AGENTS.md"
        if agents_file.is_file():
            try:
                head = agents_file.read_text(encoding="utf-8")[:512]
            except OSError:
                continue
            if MARKER_START in head:
                return parent
    return None


# Regex to extract install dir from old-format navigation rule
_OLD_NAV_RE = re.compile(
    r"ALWAYS open and follow `@/([^`/]+)/config/AGENTS\.md`"
)


def find_install_dir(project_root: Path) -> Optional[str]:
    """
    Determine the Cypilot install directory relative to project root.

    Resolution order:
    1. Read {cypilot} variable from AGENTS.md managed block (new format)
    2. Parse old-format navigation rule from AGENTS.md
    3. Scan for common install directory names
    """
    # 1. New format: {cypilot} variable
    from_var = read_cypilot_path(project_root)
    if from_var is not None:
        return from_var

    # 2. Old format: parse ALWAYS open and follow `@/.cypilot/config/AGENTS.md`
    agents_file = project_root / "AGENTS.md"
    if agents_file.is_file():
        try:
            content = agents_file.read_text(encoding="utf-8")
        except OSError:
            content = ""
        m = _OLD_NAV_RE.search(content)
        if m is not None:
            return m.group(1)

    # 3. Fallback: scan for common install dir names
    for candidate in (".cypilot", "cypilot", ".cpt"):
        if (project_root / candidate / "skills").is_dir():
            return candidate

    return None


def verify_and_inject(project_root: Optional[Path] = None) -> bool:
    """
    Verify root AGENTS.md managed block exists and is correct.
    Re-inject if missing or stale. Silent operation.

    Returns True if block is now correct, False if not in a project.
    """
    if project_root is None:
        project_root = find_project_root()
    if project_root is None:
        return False

    install_dir = find_install_dir(project_root)
    if install_dir is None:
        return False

    agents_file = project_root / "AGENTS.md"
    expected_block = compute_managed_block(install_dir)

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-if-no-agents
    if not agents_file.is_file():
        # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-create-agents-file
        try:
            agents_file.write_text(expected_block + "\n", encoding="utf-8")
        except OSError:
            return False
        return True
        # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-create-agents-file
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-if-no-agents

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-read-existing
    try:
        content = agents_file.read_text(encoding="utf-8")
    except OSError:
        return False
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-read-existing

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-if-markers-exist
    if MARKER_START in content and MARKER_END in content:
        start_idx = content.index(MARKER_START)
        end_idx = content.index(MARKER_END) + len(MARKER_END)
        current_block = content[start_idx:end_idx]
        if current_block == expected_block.strip():
            return True  # Already correct
        # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-replace-block
        new_content = content[:start_idx] + expected_block + content[end_idx:]
        # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-replace-block
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-if-markers-exist
    else:
        # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-insert-block
        new_content = expected_block + "\n\n" + content
        # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-insert-block

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-write-agents
    try:
        agents_file.write_text(new_content, encoding="utf-8")
    except OSError:
        return False
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-write-agents

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-return-agents-path
    return True
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-return-agents-path
