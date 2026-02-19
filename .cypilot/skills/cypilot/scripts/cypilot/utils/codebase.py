"""Codebase parsing/validation for Cypilot traceability markers.

This module provides a deterministic, stdlib-only parser for code files with
Cypilot traceability markers. Similar interface to template.py but for code.

Marker types supported:
- Scope markers: @cpt-{kind}:{id}:p{N}
- Block markers: @cpt-begin:{id}:p{N}:inst-{local} / @cpt-end:...

Key difference from artifacts: code can only REFERENCE IDs (not define them).
IDs in code that don't exist in artifacts = validation FAIL.
"""
from __future__ import annotations

import re

from . import error_codes as EC
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

# Scope marker: @cpt-{kind}:{full-id}:p{N}
# {kind} is kit-defined; parser accepts any lowercase slug.
_SCOPE_MARKER_RE = re.compile(
    r"@cpt-(?!begin:)(?!end:)(?P<kind>[a-z][a-z0-9-]*):(?P<id>cpt-[a-z0-9][a-z0-9-]+):(?:p|ph-)(?P<phase>\d+)"
)

# Block begin marker: @cpt-begin:{full-id}:ph-{N}:inst-{local}
_BLOCK_BEGIN_RE = re.compile(
    r"@cpt-begin:(?P<id>cpt-[a-z0-9][a-z0-9-]+):(?:p|ph-)(?P<phase>\d+):inst-(?P<inst>[a-z0-9-]+)"
)

# Block end marker: @cpt-end:{full-id}:ph-{N}:inst-{local}
_BLOCK_END_RE = re.compile(
    r"@cpt-end:(?P<id>cpt-[a-z0-9][a-z0-9-]+):(?:p|ph-)(?P<phase>\d+):inst-(?P<inst>[a-z0-9-]+)"
)

# Generic SID reference (backticked or in markers)
_SID_RE = re.compile(r"cpt-[a-z0-9][a-z0-9-]+")

def error(kind: str, message: str, *, path: Path, line: int = 1, code: Optional[str] = None, **extra) -> Dict[str, object]:
    """Uniform error factory for code validation."""
    path_s = str(path)
    out: Dict[str, object] = {"type": kind, "message": message, "line": int(line), "path": path_s}
    if code:
        out["code"] = code
    out["location"] = f"{path_s}:{int(line)}" if (path_s and not path_s.startswith("<")) else path_s
    extra = {k: v for k, v in extra.items() if v is not None}
    out.update(extra)
    return out


@dataclass(frozen=True)
class ScopeMarker:
    """A scope marker like @cpt-flow:{id}:p{N}."""
    kind: str  # flow, algo, state, req, test
    id: str  # full Cypilot ID
    phase: int
    line: int
    raw: str  # original line content


@dataclass(frozen=True)
class BlockMarker:
    """A block marker pair @cpt-begin/end:{id}:p{N}:inst-{local}."""
    id: str  # full Cypilot ID
    phase: int
    inst: str  # instruction slug
    start_line: int
    end_line: int
    content: Tuple[str, ...]  # lines between begin/end


@dataclass(frozen=True)
class CodeReference:
    """A reference to an Cypilot ID found in code."""
    id: str
    line: int
    kind: Optional[str]  # flow, algo, state, req, test, or None for generic
    phase: Optional[int]
    inst: Optional[str]
    marker_type: str  # "scope", "block", "inline"


@dataclass
class CodeFile:
    """Parsed code file with Cypilot traceability markers.

    Similar interface to Artifact from template.py but for code files.
    Code can only REFERENCE IDs (not define them).
    """
    path: Path
    scope_markers: List[ScopeMarker] = field(default_factory=list)
    block_markers: List[BlockMarker] = field(default_factory=list)
    references: List[CodeReference] = field(default_factory=list)
    _errors: List[Dict[str, object]] = field(default_factory=list)
    _loaded: bool = False

    @classmethod
    def from_path(cls, code_path: Path) -> Tuple[Optional["CodeFile"], List[Dict[str, object]]]:
        """Load and parse a code file, returning (CodeFile, errors)."""
        cf = cls(path=code_path)
        errs = cf.load()
        if errs:
            return None, errs
        return cf, []

    def load(self) -> List[Dict[str, object]]:
        """Load and parse the code file."""
        if self._loaded:
            return list(self._errors)

        try:
            text = self.path.read_text(encoding="utf-8")
        except Exception as e:
            err = error("file", f"Failed to read `{self.path}`: {e}", code=EC.FILE_READ_ERROR, path=self.path, line=1)
            self._errors.append(err)
            return [err]

        lines = text.splitlines()
        self._parse_markers(lines)
        self._loaded = True
        return list(self._errors)

    def _parse_markers(self, lines: List[str]) -> None:
        """Parse all Cypilot markers from code lines."""
        # Track open block markers for pairing
        open_blocks: Dict[str, Tuple[int, str, int, str]] = {}  # key -> (line, id, phase, inst)

        for idx, line in enumerate(lines):
            line_no = idx + 1

            # Check for scope markers
            for m in _SCOPE_MARKER_RE.finditer(line):
                marker = ScopeMarker(
                    kind=m.group("kind"),
                    id=m.group("id"),
                    phase=int(m.group("phase")),
                    line=line_no,
                    raw=line,
                )
                self.scope_markers.append(marker)
                self.references.append(CodeReference(
                    id=m.group("id"),
                    line=line_no,
                    kind=m.group("kind"),
                    phase=int(m.group("phase")),
                    inst=None,
                    marker_type="scope",
                ))

            # Check for block begin markers
            for m in _BLOCK_BEGIN_RE.finditer(line):
                key = f"{m.group('id')}:{m.group('phase')}:{m.group('inst')}"
                if key in open_blocks:
                    self._errors.append(error(
                        "marker",
                        f"Duplicate @cpt-begin for `{m.group('id')}` inst `{m.group('inst')}` at line {line_no} in `{self.path.name}` — previous @cpt-begin not closed",
                        code=EC.MARKER_DUP_BEGIN,
                        path=self.path,
                        line=line_no,
                        id=m.group("id"),
                        inst=m.group("inst"),
                    ))
                else:
                    open_blocks[key] = (line_no, m.group("id"), int(m.group("phase")), m.group("inst"))

            # Check for block end markers
            for m in _BLOCK_END_RE.finditer(line):
                key = f"{m.group('id')}:{m.group('phase')}:{m.group('inst')}"
                if key not in open_blocks:
                    self._errors.append(error(
                        "marker",
                        f"@cpt-end for `{m.group('id')}` inst `{m.group('inst')}` at line {line_no} in `{self.path.name}` has no matching @cpt-begin",
                        code=EC.MARKER_END_NO_BEGIN,
                        path=self.path,
                        line=line_no,
                        id=m.group("id"),
                        inst=m.group("inst"),
                    ))
                else:
                    start_line, cpt, phase, inst = open_blocks.pop(key)
                    content = tuple(lines[start_line:idx])  # lines between begin/end

                    if not content or all(not ln.strip() for ln in content):
                        self._errors.append(error(
                            "marker",
                            f"Empty block for `{cpt}` inst `{inst}` (lines {start_line}–{line_no}) in `{self.path.name}` — no code between markers",
                            code=EC.MARKER_EMPTY_BLOCK,
                            path=self.path,
                            line=start_line,
                            id=cpt,
                            inst=inst,
                        ))

                    block = BlockMarker(
                        id=cpt,
                        phase=phase,
                        inst=inst,
                        start_line=start_line,
                        end_line=line_no,
                        content=content,
                    )
                    self.block_markers.append(block)
                    self.references.append(CodeReference(
                        id=cpt,
                        line=start_line,
                        kind=None,
                        phase=phase,
                        inst=inst,
                        marker_type="block",
                    ))

        # Report unclosed blocks
        for key, (start_line, cpt, phase, inst) in open_blocks.items():
            self._errors.append(error(
                "marker",
                f"@cpt-begin for `{cpt}` inst `{inst}` at line {start_line} in `{self.path.name}` was never closed with @cpt-end",
                code=EC.MARKER_BEGIN_NO_END,
                path=self.path,
                line=start_line,
                id=cpt,
                inst=inst,
            ))

    def list_ids(self) -> List[str]:
        """List all unique Cypilot IDs referenced in this code file."""
        ids: Set[str] = set()
        for ref in self.references:
            ids.add(ref.id)
        return sorted(ids)

    def get(self, id_value: str) -> Optional[str]:
        """Get the code content associated with an Cypilot ID.

        Returns the content of the first matching scope or block marker.
        """
        # Check block markers first (they have content)
        for block in self.block_markers:
            if block.id == id_value:
                return "\n".join(block.content)

        # For scope markers, return the line
        for scope in self.scope_markers:
            if scope.id == id_value:
                return scope.raw

        return None

    def list(self, ids: Sequence[str]) -> List[Optional[str]]:
        """Get content for multiple IDs."""
        return [self.get(i) for i in ids]

    def get_by_inst(self, inst: str) -> Optional[str]:
        """Get code content by instruction ID."""
        for block in self.block_markers:
            if block.inst == inst:
                return "\n".join(block.content)
        return None

    def validate(self) -> Dict[str, List[Dict[str, object]]]:
        """Validate the code file structure (marker pairing, etc).

        Note: Does NOT validate against artifacts - use cross_validate_code for that.
        """
        errors = list(self._errors)
        warnings: List[Dict[str, object]] = []

        # Check for duplicate scope markers with same ID
        seen_scopes: Dict[str, int] = {}
        for scope in self.scope_markers:
            key = f"{scope.kind}:{scope.id}:{scope.phase}"
            if key in seen_scopes:
                errors.append(error(
                    "marker",
                    f"Duplicate scope marker `{scope.kind}:{scope.id}:p{scope.phase}` in `{self.path.name}` at line {scope.line} — first seen at line {seen_scopes[key]}",
                    code=EC.MARKER_DUP_SCOPE,
                    path=self.path,
                    line=scope.line,
                    id=scope.id,
                    first_occurrence=seen_scopes[key],
                ))
            else:
                seen_scopes[key] = scope.line

        return {"errors": errors, "warnings": warnings}


def cross_validate_code(
    code_files: Sequence[CodeFile],
    artifact_ids: Set[str],
    to_code_ids: Set[str],
    forbidden_code_ids: Optional[Set[str]] = None,
    traceability: str = "FULL",
    artifact_instances: Optional[Dict[str, Set[str]]] = None,
) -> Dict[str, List[Dict[str, object]]]:
    """Cross-validate code files against artifact IDs.

    Args:
        code_files: Parsed code files to validate
        artifact_ids: All IDs defined in artifacts
        to_code_ids: IDs with to_code="true" that MUST have code markers
        traceability: "FULL" or "DOCS-ONLY"
        artifact_instances: Mapping of ID -> set of instruction slugs from CDSL steps

    Returns:
        Dict with "errors" and "warnings" lists
    """
    errors: List[Dict[str, object]] = []
    warnings: List[Dict[str, object]] = []

    if traceability == "DOCS-ONLY":
        # In DOCS-ONLY mode, code markers are prohibited
        for cf in code_files:
            if cf.scope_markers or cf.block_markers:
                errors.append(error(
                    "traceability",
                    f"@cpt markers found in `{cf.path.name}` but traceability mode is DOCS-ONLY — remove all markers or switch to FULL",
                    code=EC.CODE_DOCS_ONLY,
                    path=cf.path,
                    line=1,
                ))
        return {"errors": errors, "warnings": warnings}

    # FULL traceability mode

    # Collect all IDs referenced in code
    code_ids: Set[str] = set()
    for cf in code_files:
        code_ids.update(cf.list_ids())

    # Check for orphaned markers (code refs IDs not in artifacts)
    first_forbidden: Dict[str, Tuple[Path, int]] = {}
    for cf in code_files:
        for ref in cf.references:
            if forbidden_code_ids and ref.id in forbidden_code_ids and ref.id not in first_forbidden:
                first_forbidden[ref.id] = (cf.path, int(ref.line))
            if ref.id not in artifact_ids:
                errors.append(error(
                    "traceability",
                    f"Code marker references `{ref.id}` in `{cf.path.name}` at line {ref.line} but this ID is not defined in any artifact",
                    code=EC.CODE_ORPHAN_REF,
                    path=cf.path,
                    line=ref.line,
                    id=ref.id,
                ))

    if forbidden_code_ids:
        for fid in sorted(first_forbidden.keys()):
            p, ln = first_forbidden[fid]
            errors.append(error(
                "structure",
                f"`{fid}` is marked to_code=\"true\" and referenced in code at line {ln} but its task checkbox is not checked in the artifact",
                code=EC.CODE_TASK_UNCHECKED,
                path=p,
                line=ln,
                id=fid,
            ))

    # Check for missing markers (to_code IDs without code markers)
    missing_ids = to_code_ids - code_ids
    for missing_id in sorted(missing_ids):
        errors.append(error(
            "coverage",
            f"`{missing_id}` is marked to_code=\"true\" but no @cpt marker referencing it exists in the codebase",
            code=EC.CODE_NO_MARKER,
            path=Path("."),
            line=1,
            id=missing_id,
        ))

    # Instruction-level cross-validation
    if artifact_instances:
        # Collect code instructions per ID from block markers
        code_inst_by_id: Dict[str, Dict[str, Tuple[Path, int]]] = {}
        for cf in code_files:
            for bm in cf.block_markers:
                code_inst_by_id.setdefault(bm.id, {})[bm.inst] = (cf.path, bm.start_line)

        for cid, art_insts in sorted(artifact_instances.items()):
            code_insts = set(code_inst_by_id.get(cid, {}).keys())

            # Artifact instruction not in code → missing implementation
            for inst in sorted(art_insts - code_insts):
                errors.append(error(
                    "coverage",
                    f"CDSL instruction `{inst}` of `{cid}` is defined in artifact but has no @cpt-begin/@cpt-end block in code",
                    code=EC.CODE_INST_MISSING,
                    path=Path("."),
                    line=1,
                    id=cid,
                    inst=inst,
                ))

            # Code instruction not in artifact → orphaned marker
            for inst in sorted(code_insts - art_insts):
                loc_path, loc_line = code_inst_by_id[cid][inst]
                errors.append(error(
                    "traceability",
                    f"Code block `inst-{inst}` of `{cid}` in `{loc_path.name}` at line {loc_line} has no matching CDSL step in the artifact",
                    code=EC.CODE_INST_ORPHAN,
                    path=loc_path,
                    line=loc_line,
                    id=cid,
                    inst=inst,
                ))

    return {"errors": errors, "warnings": warnings}


def load_code_file(code_path: Path) -> Tuple[Optional[CodeFile], List[Dict[str, object]]]:
    """Convenience wrapper returning (CodeFile|None, errors)."""
    return CodeFile.from_path(code_path)


def validate_code_file(code_path: Path) -> Dict[str, List[Dict[str, object]]]:
    """Validate a single code file's marker structure."""
    cf, errs = CodeFile.from_path(code_path)
    if errs or cf is None:
        return {"errors": errs or [error("file", f"Failed to load code file `{code_path}`", code=EC.FILE_LOAD_ERROR, path=code_path, line=1)], "warnings": []}
    return cf.validate()


__all__ = [
    "CodeFile",
    "ScopeMarker",
    "BlockMarker",
    "CodeReference",
    "load_code_file",
    "validate_code_file",
    "cross_validate_code",
]
