"""
Resource Diff Engine for Cypilot.

Compares a source kit directory against the user's installed copy,
classifies files, shows unified diffs, and prompts per file with
[a]ccept / [d]ecline / [A]ccept all / [D]ecline all / [m]odify.
Entry point: ``file_level_kit_update()``.

"""

# @cpt-begin:cpt-cypilot-algo-kit-diff-display:p1:inst-diff-datamodel
import difflib
import os
import re
import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class DiffReport:
    """Result of comparing two directory states."""
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    modified: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)
# @cpt-end:cpt-cypilot-algo-kit-diff-display:p1:inst-diff-datamodel


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

# @cpt-algo:cpt-cypilot-algo-kit-diff-display:p1
def show_file_diff(
    rel_path: str,
    old_content: bytes,
    new_content: bytes,
    prefix: str = "        ",
) -> None:
    """Show unified diff for a single file to stderr."""
    # @cpt-begin:cpt-cypilot-algo-kit-diff-display:p1:inst-show-file-diff
    try:
        old_lines = old_content.decode("utf-8").splitlines(keepends=True)
        new_lines = new_content.decode("utf-8").splitlines(keepends=True)
    except UnicodeDecodeError:
        sys.stderr.write(f"{prefix}(binary file \u2014 diff not shown)\n")
        return

    diff = list(difflib.unified_diff(
        old_lines, new_lines,
        fromfile=f"old/{rel_path}",
        tofile=f"new/{rel_path}",
        lineterm="",
    ))
    if not diff:
        return
    for line in diff:
        line_s = line.rstrip("\n")
        if line_s.startswith("+++") or line_s.startswith("---"):
            sys.stderr.write(f"{prefix}{line_s}\n")
        elif line_s.startswith("+"):
            sys.stderr.write(f"{prefix}\033[32m{line_s}\033[0m\n")
        elif line_s.startswith("-"):
            sys.stderr.write(f"{prefix}\033[31m{line_s}\033[0m\n")
        elif line_s.startswith("@@"):
            sys.stderr.write(f"{prefix}\033[36m{line_s}\033[0m\n")
    # @cpt-end:cpt-cypilot-algo-kit-diff-display:p1:inst-show-file-diff


# @cpt-begin:cpt-cypilot-algo-kit-conflict-merge:p1:inst-merge-datamodel
def _get_editor() -> str:
    """Return the user's preferred editor: $VISUAL → $EDITOR → vi."""
    return os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi"


_CONFLICT_MARKER_OURS = "<<<<<<< installed (yours)"
_CONFLICT_MARKER_SEP = "======="
_CONFLICT_MARKER_THEIRS = ">>>>>>> upstream (source)"
# @cpt-end:cpt-cypilot-algo-kit-conflict-merge:p1:inst-merge-datamodel


# @cpt-algo:cpt-cypilot-algo-kit-conflict-merge:p1
def _has_conflict_markers(text: str) -> bool:
    """Return True if *text* still contains unresolved git conflict markers.

    Uses line-start matching to avoid false positives from ``=======``
    appearing as markdown content mid-line.
    """
    # @cpt-begin:cpt-cypilot-algo-kit-conflict-merge:p1:inst-detect-markers
    for line in text.splitlines():
        if (
            line.startswith("<<<<<<<")
            or line.startswith("=======")
            or line.startswith(">>>>>>>")
        ):
            return True
    return False
    # @cpt-end:cpt-cypilot-algo-kit-conflict-merge:p1:inst-detect-markers


def _build_conflict_content(
    rel_path: str,
    old_text: str,
    new_text: str,
) -> str:
    """Build file content with git-style conflict markers.

    For each differing hunk the output contains::

        <<<<<<< installed (yours)
        ... user lines ...
        =======
        ... upstream lines ...
        >>>>>>> upstream (source)

    Identical regions are emitted as-is.  The result is valid input for
    any editor with merge-conflict resolution UI (VS Code, IntelliJ,
    Vim fugitive, etc.).
    """
    # @cpt-begin:cpt-cypilot-algo-kit-conflict-merge:p1:inst-build-conflicts
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    sm = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    parts: List[str] = []

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            parts.extend(old_lines[i1:i2])
        elif tag == "replace":
            parts.append(_CONFLICT_MARKER_OURS + "\n")
            parts.extend(old_lines[i1:i2])
            parts.append(_CONFLICT_MARKER_SEP + "\n")
            parts.extend(new_lines[j1:j2])
            parts.append(_CONFLICT_MARKER_THEIRS + "\n")
        elif tag == "delete":
            parts.append(_CONFLICT_MARKER_OURS + "\n")
            parts.extend(old_lines[i1:i2])
            parts.append(_CONFLICT_MARKER_SEP + "\n")
            parts.append(_CONFLICT_MARKER_THEIRS + "\n")
        elif tag == "insert":
            parts.append(_CONFLICT_MARKER_OURS + "\n")
            parts.append(_CONFLICT_MARKER_SEP + "\n")
            parts.extend(new_lines[j1:j2])
            parts.append(_CONFLICT_MARKER_THEIRS + "\n")

    return "".join(parts)
    # @cpt-end:cpt-cypilot-algo-kit-conflict-merge:p1:inst-build-conflicts


def _prompt_unresolved(rel_path: str) -> str:
    """Prompt user when conflict markers remain after editing.

    Returns one of: ``"retry"``, ``"accept"``, ``"decline"``.
    """
    # @cpt-begin:cpt-cypilot-algo-kit-conflict-merge:p1:inst-prompt-unresolved
    sys.stderr.write(
        f"    \033[33m\u26a0 {rel_path}: unresolved conflict markers remain\033[0m\n"
        "      \033[1m[r]\033[0metry editing  "
        "\033[1m[a]\033[0mccept upstream  "
        "\033[1m[d]\033[0mecline (keep yours)  "
    )
    sys.stderr.flush()
    try:
        response = input().strip().lower()
    except EOFError:
        return "decline"
    if response == "r":
        return "retry"
    if response == "a":
        return "accept"
    return "decline"
    # @cpt-end:cpt-cypilot-algo-kit-conflict-merge:p1:inst-prompt-unresolved


def _open_editor_for_file(
    rel_path: str,
    old_content: bytes,
    new_content: bytes,
) -> Optional[bytes]:
    """Open editor for manual file merge using git conflict markers.

    Writes a file with ``<<<<<<<``/``=======``/``>>>>>>>`` markers for
    every differing region.  After the editor closes:

    - If no conflict markers remain → return the resolved content.
    - If markers still present → re-prompt: retry / accept upstream / decline.
    - Empty file → abort (return None).

    Returns edited bytes, *new_content* (accept upstream), or None (decline).
    """
    # @cpt-begin:cpt-cypilot-algo-kit-conflict-merge:p1:inst-open-editor
    try:
        old_text = old_content.decode("utf-8")
        new_text = new_content.decode("utf-8")
    except UnicodeDecodeError:
        sys.stderr.write("    (binary file \u2014 cannot edit)\n")
        return None

    conflict_text = _build_conflict_content(rel_path, old_text, new_text)
    editor = _get_editor()
    suffix = Path(rel_path).suffix or ".md"

    while True:
        tmp_path: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=suffix,
                prefix="cypilot-merge-",
                delete=False, encoding="utf-8",
            ) as tmp:
                tmp.write(conflict_text)
                tmp_path = tmp.name

            cmd = shlex.split(editor)
            subprocess.check_call(cmd + [tmp_path])

            with open(tmp_path, encoding="utf-8") as f:
                edited = f.read()
        except FileNotFoundError:
            sys.stderr.write(f"    editor not found: {editor}\n")
            return None
        except Exception as exc:
            sys.stderr.write(f"    editor failed: {exc}\n")
            return None
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

        if not edited.strip():
            return None

        # @cpt-begin:cpt-cypilot-algo-kit-conflict-merge:p1:inst-resolve-loop
        if not _has_conflict_markers(edited):
            return edited.encode("utf-8")

        decision = _prompt_unresolved(rel_path)
        if decision == "retry":
            conflict_text = edited
            continue
        if decision == "accept":
            return new_content
        return None
        # @cpt-end:cpt-cypilot-algo-kit-conflict-merge:p1:inst-resolve-loop
    # @cpt-end:cpt-cypilot-algo-kit-conflict-merge:p1:inst-open-editor


# ---------------------------------------------------------------------------
# Kit file-level update  (cpt-cypilot-algo-kit-file-update)
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-kit-file-enumerate:p1:inst-enum-datamodel
_KIT_EXCLUDE_FILES = frozenset({"conf.toml", "blueprint_hashes.toml"})
_KIT_EXCLUDE_DIRS = frozenset({"blueprints", "__pycache__", ".prev"})

# Default content items when no explicit filter is provided
_DEFAULT_CONTENT_DIRS: Optional[Tuple[str, ...]] = None
_DEFAULT_CONTENT_FILES: Optional[Tuple[str, ...]] = None
# @cpt-end:cpt-cypilot-algo-kit-file-enumerate:p1:inst-enum-datamodel


# @cpt-algo:cpt-cypilot-algo-kit-file-enumerate:p1
# @cpt-algo:cpt-cypilot-algo-kit-snapshot:p1
def _enumerate_kit_files(
    dir_path: Path,
    *,
    exclude_files: frozenset = _KIT_EXCLUDE_FILES,
    exclude_dirs: frozenset = _KIT_EXCLUDE_DIRS,
    content_dirs: Optional[Tuple[str, ...]] = None,
    content_files: Optional[Tuple[str, ...]] = None,
) -> Dict[str, bytes]:
    """Enumerate files in a kit directory.

    Returns ``{relative_posix_path: content_bytes}``.

    When *content_dirs* / *content_files* are provided, **only** files whose
    top-level directory is in *content_dirs* or whose name matches a
    *content_files* entry are included (include-only mode).  Otherwise the
    legacy exclude-based filtering is applied.
    """
    # @cpt-begin:cpt-cypilot-algo-kit-file-enumerate:p1:inst-walk-dir
    # @cpt-begin:cpt-cypilot-algo-kit-snapshot:p1:inst-read-files
    files: Dict[str, bytes] = {}
    if not dir_path.is_dir():
        return files

    use_include = content_dirs is not None or content_files is not None
    include_dirs = set(content_dirs) if content_dirs else set()
    include_files = set(content_files) if content_files else set()

    for f in sorted(dir_path.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(dir_path)

        # @cpt-begin:cpt-cypilot-algo-kit-file-enumerate:p1:inst-include-filter
        if use_include:
            # Include-only: top-level dir must be in content_dirs,
            # or file at root must be in content_files.
            top = rel.parts[0] if len(rel.parts) > 1 else None
            if top and top in include_dirs:
                pass  # included via directory
            elif len(rel.parts) == 1 and rel.name in include_files:
                pass  # included via file name
            else:
                continue
        # @cpt-end:cpt-cypilot-algo-kit-file-enumerate:p1:inst-include-filter
        else:
            # @cpt-begin:cpt-cypilot-algo-kit-file-enumerate:p1:inst-exclude-filter
            if rel.name in exclude_files:
                continue
            if any(part in exclude_dirs for part in rel.parts):
                continue
            # @cpt-end:cpt-cypilot-algo-kit-file-enumerate:p1:inst-exclude-filter

        # @cpt-begin:cpt-cypilot-algo-kit-file-enumerate:p1:inst-read-bytes
        try:
            files[str(rel)] = f.read_bytes()
        except OSError:
            pass
        # @cpt-end:cpt-cypilot-algo-kit-file-enumerate:p1:inst-read-bytes
    return files
    # @cpt-end:cpt-cypilot-algo-kit-snapshot:p1:inst-read-files
    # @cpt-end:cpt-cypilot-algo-kit-file-enumerate:p1:inst-walk-dir


# @cpt-algo:cpt-cypilot-algo-kit-file-classify:p1
def _classify_kit_files(
    source_files: Dict[str, bytes],
    user_files: Dict[str, bytes],
) -> DiffReport:
    """Classify files between source and user kit directories.

    Returns a DiffReport with added/removed/modified/unchanged lists.
    """
    # @cpt-begin:cpt-cypilot-algo-kit-file-classify:p1:inst-classify
    report = DiffReport()
    all_paths = sorted(set(source_files) | set(user_files))
    for p in all_paths:
        in_source = p in source_files
        in_user = p in user_files
        if in_source and not in_user:
            report.added.append(p)
        elif in_user and not in_source:
            report.removed.append(p)
        elif source_files[p] == user_files[p]:
            report.unchanged.append(p)
        else:
            report.modified.append(p)
    return report
    # @cpt-end:cpt-cypilot-algo-kit-file-classify:p1:inst-classify


# @cpt-algo:cpt-cypilot-algo-kit-interactive-review:p1
def _prompt_kit_file(
    rel_path: str,
    state: Dict[str, bool],
) -> str:
    """Interactive prompt for kit file review.

    Returns one of: ``"accept"``, ``"decline"``, ``"modify"``.

    Respects ``accept_all`` / ``decline_all`` flags in *state* to skip
    prompting for remaining files.
    """
    # @cpt-begin:cpt-cypilot-algo-kit-interactive-review:p1:inst-check-bulk
    if state.get("accept_all"):
        return "accept"

    if state.get("decline_all"):
        return "decline"
    # @cpt-end:cpt-cypilot-algo-kit-interactive-review:p1:inst-check-bulk

    # @cpt-begin:cpt-cypilot-algo-kit-interactive-review:p1:inst-prompt
    sys.stderr.write(
        f"    {rel_path}  "
        "\033[1m[a]\033[0mccept  "
        "\033[1m[d]\033[0mecline  "
        "\033[1m[A]\033[0mccept all  "
        "\033[1m[D]\033[0mecline all  "
        "\033[1m[m]\033[0modify  "
    )
    sys.stderr.flush()
    try:
        response = input().strip()
    except EOFError:
        return "decline"

    if response == "a":
        return "accept"

    if response == "d":
        return "decline"

    if response == "A":
        state["accept_all"] = True
        return "accept"

    if response == "D":
        state["decline_all"] = True
        return "decline"

    if response == "m":
        return "modify"

    return "decline"
    # @cpt-end:cpt-cypilot-algo-kit-interactive-review:p1:inst-prompt


def _show_kit_update_summary(report: DiffReport, prefix: str = "    ") -> None:
    """Print kit update summary to stderr with colour coding."""
    # @cpt-begin:cpt-cypilot-algo-kit-diff-display:p1:inst-show-summary
    counts = []
    if report.added:
        counts.append(f"\033[32m{len(report.added)} added\033[0m")
    if report.removed:
        counts.append(f"\033[31m{len(report.removed)} removed\033[0m")
    if report.modified:
        counts.append(f"\033[33m{len(report.modified)} modified\033[0m")
    counts.append(f"{len(report.unchanged)} unchanged")
    sys.stderr.write(f"{prefix}Kit files: {', '.join(counts)}\n")

    for p in report.added:
        sys.stderr.write(f"{prefix}  \033[32m+ {p}\033[0m  (new)\n")
    for p in report.removed:
        sys.stderr.write(f"{prefix}  \033[31m- {p}\033[0m  (deleted upstream)\n")
    for p in report.modified:
        sys.stderr.write(f"{prefix}  \033[33m~ {p}\033[0m\n")
    # @cpt-end:cpt-cypilot-algo-kit-diff-display:p1:inst-show-summary


# ---------------------------------------------------------------------------
# TOC handling for kit file diffs
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-kit-toc-handling:p1:inst-toc-datamodel
_TOC_MARKER_START = "<!-- toc -->"
_TOC_MARKER_END = "<!-- /toc -->"
_TOC_HEADING_RE = re.compile(r"^##\s+Table of Contents\s*$")
_HEADING_RE_TOC = re.compile(r"^#{1,6}\s")
# @cpt-end:cpt-cypilot-algo-kit-toc-handling:p1:inst-toc-datamodel


# @cpt-algo:cpt-cypilot-algo-kit-toc-handling:p1
def _strip_toc_for_diff(content: bytes) -> Tuple[bytes, str]:
    """Strip TOC sections from file content for cleaner diff comparison.

    Returns ``(stripped_content, toc_format)`` where *toc_format* is:

    - ``"markers"`` — ``<!-- toc -->`` / ``<!-- /toc -->`` block was stripped
    - ``"heading"`` — ``## Table of Contents`` section was stripped
    - ``""`` — no TOC found
    """
    # @cpt-begin:cpt-cypilot-algo-kit-toc-handling:p1:inst-strip-toc
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return content, ""

    lines = text.split("\n")

    # 1. Check for marker-based TOC
    start_idx = end_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == _TOC_MARKER_START and start_idx is None:
            start_idx = i
        elif stripped == _TOC_MARKER_END and start_idx is not None:
            end_idx = i
            break

    if start_idx is not None and end_idx is not None:
        s, e = start_idx, end_idx + 1
        while s > 0 and lines[s - 1].strip() == "":
            s -= 1
        while e < len(lines) and lines[e].strip() == "":
            e += 1
        new_lines = lines[:s] + lines[e:]
        return "\n".join(new_lines).encode("utf-8"), "markers"

    # 2. Check for heading-based TOC
    for i, line in enumerate(lines):
        if _TOC_HEADING_RE.match(line):
            toc_end = None
            for j in range(i + 1, len(lines)):
                if _HEADING_RE_TOC.match(lines[j]) or lines[j].strip() == "---":
                    toc_end = j
                    break
            if toc_end is None:
                toc_end = len(lines)

            s, e = i, toc_end
            while s > 0 and lines[s - 1].strip() == "":
                s -= 1
            while e < len(lines) and lines[e].strip() == "":
                e += 1
            new_lines = lines[:s] + lines[e:]
            return "\n".join(new_lines).encode("utf-8"), "heading"

    return content, ""
    # @cpt-end:cpt-cypilot-algo-kit-toc-handling:p1:inst-strip-toc


def _prompt_toc_regen(rel_path: str) -> str:
    """Ask user whether to regenerate TOC for a file.

    Returns ``"yes"`` or ``"no"``.
    """
    # @cpt-begin:cpt-cypilot-algo-kit-toc-handling:p1:inst-prompt-regen
    sys.stderr.write(
        f"\n      TOC detected in \033[1m{rel_path}\033[0m. "
        f"Regenerate? [\033[32my\033[0m]es / [\033[31mn\033[0m]o: "
    )
    sys.stderr.flush()
    try:
        answer = input().strip().lower()
    except EOFError:
        return "no"
    if answer in ("y", "yes"):
        return "yes"
    return "no"
    # @cpt-end:cpt-cypilot-algo-kit-toc-handling:p1:inst-prompt-regen


def _prompt_toc_error_continue(rel_path: str, err: Exception) -> bool:
    """After TOC regen fails, ask user whether to continue or stop.

    Returns True to continue processing, False to stop.
    """
    # @cpt-begin:cpt-cypilot-algo-kit-toc-handling:p1:inst-handle-error
    sys.stderr.write(
        f"\n      \033[31mTOC regeneration failed for {rel_path}: {err}\033[0m\n"
        f"      Previous content restored. "
        f"[\033[32mc\033[0m]ontinue / [\033[31ms\033[0m]top: "
    )
    sys.stderr.flush()
    try:
        answer = input().strip().lower()
    except EOFError:
        return False
    return answer != "s"
    # @cpt-end:cpt-cypilot-algo-kit-toc-handling:p1:inst-handle-error


def _regenerate_toc(content: bytes, toc_format: str) -> bytes:
    """Regenerate TOC in file content based on detected format.

    Uses ``insert_toc_markers`` for marker-based TOC and
    ``insert_toc_heading`` for heading-based TOC.

    Raises on failure (caller handles rollback).
    """
    # @cpt-begin:cpt-cypilot-algo-kit-toc-handling:p1:inst-regenerate
    from .toc import insert_toc_markers, insert_toc_heading

    text = content.decode("utf-8")
    if toc_format == "markers":
        result = insert_toc_markers(text, max_level=3)
    else:  # "heading"
        result = insert_toc_heading(text, max_heading_level=3, numbered=True)
    return result.encode("utf-8")
    # @cpt-end:cpt-cypilot-algo-kit-toc-handling:p1:inst-regenerate


# @cpt-algo:cpt-cypilot-algo-kit-file-update:p1
def file_level_kit_update(
    source_dir: Path,
    user_dir: Path,
    *,
    interactive: bool = True,
    auto_approve: bool = False,
    force: bool = False,
    dry_run: bool = False,
    content_dirs: Optional[Tuple[str, ...]] = None,
    content_files: Optional[Tuple[str, ...]] = None,
    resource_bindings: Optional[Dict[str, Path]] = None,
    source_to_resource_id: Optional[Dict[str, str]] = None,
    resource_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Compare source kit against user's installed copy and apply updates.

    Implements ``cpt-cypilot-algo-kit-file-update``.

    Args:
        source_dir:    Kit source directory (from cache).
        user_dir:      User's installed kit config directory.
        interactive:   Prompt user per changed file (default True).
        auto_approve:  Accept all changes without prompts.
        force:         Overwrite all files without prompts (alias).
        dry_run:       Show what would be done without writing.
        content_dirs:  If given, only include files under these top-level dirs.
        content_files: If given, only include root-level files matching these names.
        resource_bindings: For manifest-driven kits, maps resource_id -> absolute target path.
        source_to_resource_id: Maps source file rel_path -> resource_id.
        resource_info: Maps resource_id -> ResourceInfo (type, source_base).

    Returns dict::

        {
            "status": "current" | "updated",
            "added": [{"path": ..., "action": ...}, ...],
            "removed": [...],
            "modified": [...],
            "unchanged_count": N,
            "accepted": [paths ...],
            "declined": [paths ...],
            "unchanged": N,
        }
    """
    # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-enumerate-files
    enum_kw: Dict[str, Any] = {}
    if content_dirs is not None:
        enum_kw["content_dirs"] = content_dirs
    if content_files is not None:
        enum_kw["content_files"] = content_files

    source_files = _enumerate_kit_files(source_dir, **enum_kw)
    # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-enumerate-files

    # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-build-target-mapping
    # Build target path mapping for resource bindings
    target_mapping: Dict[str, Path] = {}  # source_rel_path -> absolute target path
    if resource_bindings and source_to_resource_id and resource_info:
        for src_rel_path in source_files:
            res_id = source_to_resource_id.get(src_rel_path)
            if res_id and res_id in resource_bindings:
                binding_path = resource_bindings[res_id]
                info = resource_info.get(res_id)
                if info and info.type == "directory":
                    # For directory resources, append relative path within directory
                    source_base = info.source_base
                    if src_rel_path.startswith(source_base + "/"):
                        rel_within_dir = src_rel_path[len(source_base) + 1:]
                        target_mapping[src_rel_path] = binding_path / rel_within_dir
                    else:
                        # Fallback: try to compute relative path within directory
                        try:
                            rel_within_dir = Path(src_rel_path).relative_to(info.source_base).as_posix()
                            target_mapping[src_rel_path] = binding_path / rel_within_dir
                        except ValueError:
                            # Cannot compute relative path, use filename as last resort
                            sys.stderr.write(
                                f"    [debug] directory resource fallback: "
                                f"source_base={info.source_base}, src_rel_path={src_rel_path}, "
                                f"binding_path={binding_path}\n"
                            )
                            target_mapping[src_rel_path] = binding_path / src_rel_path.split("/")[-1]
                else:
                    # File resource: binding path is the target file
                    # But if binding path is a directory, append the filename
                    if binding_path.is_dir():
                        sys.stderr.write(
                            f"    [warn] file resource binding is a directory: "
                            f"binding_path={binding_path}, src_rel_path={src_rel_path}\n"
                        )
                        filename = src_rel_path.split("/")[-1]
                        target_mapping[src_rel_path] = binding_path / filename
                    else:
                        target_mapping[src_rel_path] = binding_path
            else:
                # No binding: default to user_dir / rel_path
                target_mapping[src_rel_path] = user_dir / src_rel_path
    else:
        # No resource bindings: all files go to user_dir
        for src_rel_path in source_files:
            target_mapping[src_rel_path] = user_dir / src_rel_path
    # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-build-target-mapping

    # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-enumerate-bound-user-files
    # Enumerate user files from target paths (may be outside user_dir)
    user_files: Dict[str, bytes] = {}
    # First, read files at bound target paths (for files that exist in source)
    for src_rel_path, target_path in target_mapping.items():
        if target_path.is_file():
            try:
                user_files[src_rel_path] = target_path.read_bytes()
            except (OSError, IOError):
                pass
    # For directory resources and file resources with directory bindings,
    # enumerate existing files to detect files in user's bound path
    if resource_bindings and resource_info:
        for res_id, binding_path in resource_bindings.items():
            info = resource_info.get(res_id)
            if not info:
                continue
            if info.type == "directory" and binding_path.is_dir():
                # Directory resource: enumerate all files
                source_base = info.source_base
                for fpath in binding_path.rglob("*"):
                    if fpath.is_file():
                        rel_within_dir = fpath.relative_to(binding_path).as_posix()
                        src_rel_path = f"{source_base}/{rel_within_dir}"
                        if src_rel_path not in user_files:
                            try:
                                user_files[src_rel_path] = fpath.read_bytes()
                                target_mapping[src_rel_path] = fpath
                            except (OSError, IOError):
                                pass
            elif info.type == "file" and binding_path.is_dir():
                # File resource but binding points to directory: check for file with same name
                filename = info.source_base.split("/")[-1]
                fpath = binding_path / filename
                # Compute the source-relative path this file would have
                src_rel_path = info.source_base
                if fpath.is_file() and src_rel_path not in user_files:
                    try:
                        user_files[src_rel_path] = fpath.read_bytes()
                        target_mapping[src_rel_path] = fpath
                    except (OSError, IOError):
                        pass
    # Also enumerate user_dir to detect removed files (files in user but not in source)
    user_dir_files = _enumerate_kit_files(user_dir, **enum_kw)
    for rel_path, content in user_dir_files.items():
        if rel_path not in user_files:
            user_files[rel_path] = content
            # Add to target_mapping for deletion
            if rel_path not in target_mapping:
                target_mapping[rel_path] = user_dir / rel_path
    # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-enumerate-bound-user-files

    # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-strip-toc
    # Strip TOC from both sides so diffs only show content changes.
    # TOC is regenerated post-write if the user agrees.
    source_stripped: Dict[str, bytes] = {}
    user_stripped: Dict[str, bytes] = {}
    toc_formats: Dict[str, str] = {}

    for k, v in source_files.items():
        stripped, fmt = _strip_toc_for_diff(v)
        source_stripped[k] = stripped
        if fmt:
            toc_formats[k] = fmt

    for k, v in user_files.items():
        stripped, fmt = _strip_toc_for_diff(v)
        user_stripped[k] = stripped
        if fmt and k not in toc_formats:
            toc_formats[k] = fmt
    # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-strip-toc

    # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-classify-changes
    # Classify using raw content so TOC-only differences are detected.
    # Stripped content is used only for diff display (less noise).
    report = _classify_kit_files(source_files, user_files)
    # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-classify-changes

    # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-check-no-changes
    if not report.has_changes:
        return {
            "status": "current",
            "added": [],
            "removed": [],
            "modified": [],
            "unchanged_count": len(report.unchanged),
            "accepted": [],
            "declined": [],
            "unchanged": len(report.unchanged),
        }
    # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-check-no-changes

    # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-show-summary
    _show_kit_update_summary(report)
    # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-show-summary

    # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-update-datamodel
    result_added: List[Dict[str, str]] = []
    result_removed: List[Dict[str, str]] = []
    result_modified: List[Dict[str, str]] = []

    review_state: Dict[str, bool] = {}

    changed = sorted(
        [(p, "added") for p in report.added]
        + [(p, "removed") for p in report.removed]
        + [(p, "modified") for p in report.modified]
    )
    # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-update-datamodel

    for rel_path, change_type in changed:
        # Stripped content for diff display, raw content for writing
        old_content = user_stripped.get(rel_path, b"")
        new_content = source_stripped.get(rel_path, b"")
        raw_new_content = source_files.get(rel_path, b"")
        toc_fmt = toc_formats.get(rel_path, "")

        if force or auto_approve:
            action = "accepted"
        elif not interactive:
            action = "declined"
        else:
            # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-show-change-context
            if change_type == "added":
                sys.stderr.write(
                    f"\n    \033[32m+ {rel_path}\033[0m  (new file, "
                    f"{len(new_content)} bytes)\n"
                )
            elif change_type == "removed":
                sys.stderr.write(
                    f"\n    \033[31m- {rel_path}\033[0m  (deleted upstream, "
                    f"{len(old_content)} bytes in your copy)\n"
                )
            else:
                sys.stderr.write(f"\n    \033[33m~ {rel_path}\033[0m\n")
                show_file_diff(rel_path, old_content, new_content, prefix="      ")
            # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-show-change-context

            # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-prompt-decision
            decision = _prompt_kit_file(rel_path, review_state)

            if decision == "accept":
                action = "accepted"
            elif decision == "decline":
                action = "declined"
            # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-editor-merge
            elif decision == "modify":
                edited = _open_editor_for_file(rel_path, old_content, new_content)
                if edited is not None:
                    new_content = edited
                    action = "modified"
                else:
                    action = "declined"
            # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-editor-merge
            else:
                action = "declined"
            # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-prompt-decision

        # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-apply-changes
        entry = {"path": rel_path, "action": action}
        wrote_file = False
        wrote_raw = False
        dest = target_mapping.get(rel_path, user_dir / rel_path)

        if change_type == "added":
            if action in ("accepted", "modified") and not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                write_data = new_content if action == "modified" else raw_new_content
                dest.write_bytes(write_data)
                wrote_file = True
                wrote_raw = action == "accepted"
            result_added.append(entry)

        elif change_type == "removed":
            if action in ("accepted",) and not dry_run and dest.is_file():
                dest.unlink()
            result_removed.append(entry)

        elif change_type == "modified":
            if action in ("accepted", "modified") and not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                write_data = new_content if action == "modified" else raw_new_content
                dest.write_bytes(write_data)
                wrote_file = True
                wrote_raw = action == "accepted"
            result_modified.append(entry)
        # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-apply-changes

        # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-toc-regen
        # Skip TOC regen if we wrote raw source content (already has correct TOC)
        if wrote_file and toc_fmt and not wrote_raw:
            should_regen = auto_approve or force
            if interactive and not should_regen:
                should_regen = _prompt_toc_regen(rel_path) == "yes"
            if should_regen:
                pre_toc_content = dest.read_bytes()
                try:
                    regenerated = _regenerate_toc(pre_toc_content, toc_fmt)
                    dest.write_bytes(regenerated)
                except Exception as exc:
                    dest.write_bytes(user_files.get(rel_path, pre_toc_content))
                    if interactive:
                        if not _prompt_toc_error_continue(rel_path, exc):
                            break
        # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-toc-regen

    # @cpt-begin:cpt-cypilot-algo-kit-file-update:p1:inst-build-result
    all_entries = result_added + result_removed + result_modified
    accepted = [e["path"] for e in all_entries if e["action"] in ("accepted", "modified")]
    declined = [e["path"] for e in all_entries if e["action"] == "declined"]
    return {
        "status": "updated",
        "added": result_added,
        "removed": result_removed,
        "modified": result_modified,
        "unchanged_count": len(report.unchanged),
        "accepted": accepted,
        "declined": declined,
        "unchanged": len(report.unchanged),
    }
    # @cpt-end:cpt-cypilot-algo-kit-file-update:p1:inst-build-result
