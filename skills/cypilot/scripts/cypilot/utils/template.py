"""Template and artifact parsing/validation per templates/SPEC.md (marker-based).

This module provides a deterministic, stdlib-only parser that can be reused by
CLI, cascade validation, and search utilities. It parses templates (paired cypilot
markers), produces an object model, parses artifacts against templates, and
validates structure/content including CDSL blocks.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

SUPPORTED_VERSION = {"major": 2, "minor": 0}

_MARKER_RE = re.compile(r"<!--\s*cpt:(?:(?P<type>[^:\s>]+):)?(?P<name>[^>\s]+)(?P<attrs>[^>]*)-->")
_ATTR_RE = re.compile(r'([a-zA-Z0-9_-]+)\s*=\s*"([^"]*)"')
_ID_DEF_RE = re.compile(
    r"^(?:"
    r"\*\*ID\*\*:\s*`(?P<id>cpt-[a-z0-9][a-z0-9-]+)`"
    r"|"
    r"`(?P<priority_only>p\d+)`\s*-\s*\*\*ID\*\*:\s*`(?P<id2>cpt-[a-z0-9][a-z0-9-]+)`"
    r"|"
    r"[-*]\s+(?P<task>\[\s*[xX]?\s*\])\s*(?:`(?P<priority>p\d+)`\s*-\s*)?\*\*ID\*\*:\s*`(?P<id3>cpt-[a-z0-9][a-z0-9-]+)`"
    r")\s*$"
)
_ID_LABEL_RE = re.compile(r"\*\*ID\*\*:")
_ID_REF_RE = re.compile(r"^(?:(?P<task>\[\s*[xX]?\s*\])\s*(?:`(?P<priority>p\d+)`\s*-\s*|\-\s*)|`(?P<priority_only>p\d+)`\s*-\s*)?`(?P<id>cpt-[a-z0-9][a-z0-9-]+)`\s*$")
_BACKTICK_ID_RE = re.compile(r"`(cpt-[a-z0-9][a-z0-9-]+)`")
_HEADING_RE = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*$")
_ORDERED_NUMERIC_RE = re.compile(r"^\s*\d+[\.)]\s+")
_CODE_FENCE_RE = re.compile(r"^\s*```")
_CDSL_LINE_RE = re.compile(r"^\s*(?:\d+\.\s+|-\s+)\[\s*[xX ]\s*\]\s*-\s*`p[a-z0-9-]+`\s*-\s*.+\s*-\s*`inst-[a-z0-9-]+`\s*$")
_CDSL_PHASE_RE = re.compile(r"`p(?P<phase>\d+)`")
_CDSL_INST_RE = re.compile(r"`inst-(?P<inst>[a-z0-9-]+)`")

# Valid marker types (must match validate_block_content handlers)
VALID_MARKER_TYPES = frozenset({
    "free", "id", "id-ref",
    "list", "numbered-list", "task-list",
    "table", "paragraph", "code",
    "#", "##", "###", "####", "#####", "######",
    "link", "image", "cdsl",
})


def apply_kind_constraints(template: "Template", constraints: "ArtifactKindConstraints") -> List[Dict[str, object]]:
    """Apply kit constraints to a loaded Template.

    Constraints have higher priority than marker attrs. If a constraint contradicts an
    explicitly defined marker attribute, this returns a validation error.
    """
    from .constraints import ArtifactKindConstraints  # noqa: F401

    errors: List[Dict[str, object]] = []

    def _normalize_has(raw: str) -> set[str]:
        return {p.strip() for p in str(raw or "").split(",") if p.strip()}

    def _write_has(attrs: Dict[str, str], tokens: set[str]) -> None:
        if not tokens:
            attrs.pop("has", None)
            return
        attrs["has"] = ",".join(sorted(tokens))

    def _bool_attr(raw: Optional[str]) -> Optional[bool]:
        if raw is None:
            return None
        v = str(raw).strip().lower()
        if v in {"true", "false"}:
            return v == "true"
        return None

    def _apply_one(block: TemplateBlock, c: "IdConstraint", section: str) -> None:
        from .constraints import IdConstraint  # noqa: F401

        attrs = block.attrs

        # has= (priority, task)
        if c.priority is not None or c.task is not None:
            existing_tokens = _normalize_has(attrs.get("has", ""))
            desired_tokens = set(existing_tokens)

            if c.priority is not None:
                marker_val = "priority" in existing_tokens
                if marker_val and not bool(c.priority):
                    errors.append(Template.error(
                        "constraints",
                        "Constraint contradicts template marker",
                        path=template.path,
                        line=block.start_line,
                        artifact_kind=template.kind,
                        id_kind=c.kind,
                        section=section,
                        field="priority",
                        marker=marker_val,
                        constraint=bool(c.priority),
                    ))
                if c.priority:
                    desired_tokens.add("priority")
                else:
                    desired_tokens.discard("priority")

            if c.task is not None:
                marker_val = "task" in existing_tokens
                if marker_val and not bool(c.task):
                    errors.append(Template.error(
                        "constraints",
                        "Constraint contradicts template marker",
                        path=template.path,
                        line=block.start_line,
                        artifact_kind=template.kind,
                        id_kind=c.kind,
                        section=section,
                        field="task",
                        marker=marker_val,
                        constraint=bool(c.task),
                    ))
                if c.task:
                    desired_tokens.add("task")
                else:
                    desired_tokens.discard("task")

            _write_has(attrs, desired_tokens)

        # to_code=
        if c.to_code is not None:
            if "to_code" in attrs:
                marker_val = _bool_attr(attrs.get("to_code"))
                if marker_val is not None and marker_val != bool(c.to_code):
                    errors.append(Template.error(
                        "constraints",
                        "Constraint contradicts template marker",
                        path=template.path,
                        line=block.start_line,
                        artifact_kind=template.kind,
                        id_kind=c.kind,
                        section=section,
                        field="to_code",
                        marker=marker_val,
                        constraint=bool(c.to_code),
                    ))
            attrs["to_code"] = "true" if c.to_code else "false"

        # headings=
        if c.headings is not None:
            attrs["headings"] = json.dumps(list(c.headings), ensure_ascii=False)

    # Apply defined-id constraints to id blocks
    for c in constraints.defined_id:
        matches = [b for b in (template.blocks or []) if b.type == "id" and b.name.lower() == c.kind.lower()]
        if not matches:
            errors.append(Template.error(
                "constraints",
                "Constraint references missing template block",
                path=template.path,
                line=1,
                artifact_kind=template.kind,
                id_kind=c.kind,
                section="defined-id",
            ))
            continue
        for b in matches:
            _apply_one(b, c, "defined-id")

    # Attach constraints to template for strict artifact-time checks.
    try:
        object.__setattr__(template, "constraints", constraints)
    except Exception:
        pass

    return errors


def filter_code_fences(lines: List[str]) -> List[str]:
    """Filter out lines that are inside fenced code blocks (```...```)."""
    result: List[str] = []
    in_fence = False
    for line in lines:
        if _CODE_FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            result.append(line)
    return result


def enumerate_outside_code_fences(lines: List[str]) -> Iterable[Tuple[int, str]]:
    """Enumerate lines that are NOT inside fenced code blocks, preserving original indices."""
    in_fence = False
    for idx, line in enumerate(lines):
        if _CODE_FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield idx, line


@dataclass(frozen=True)
class ParsedCypilotId:
    """Result of parsing an Cypilot ID."""
    system: str
    kind: str
    slug: str
    prefix_id: Optional[str] = None  # noqa: for composite IDs like cpt-sys-spec-x-algo-y


@dataclass(frozen=True)
class TemplatePolicy:
    unknown_sections: str  # error|warn|allow


@dataclass(frozen=True)
class TemplateVersion:
    major: int
    minor: int


@dataclass(frozen=True)
class TemplateBlock:
    type: str
    name: str
    required: bool
    repeat: str
    attrs: Dict[str, str]
    start_line: int
    end_line: int


@dataclass(frozen=True)
class Template:
    """Parsed template model built from a template file.

    Holds structural metadata (kind, policy) and the ordered list of TemplateBlock
    spans (opening/closing markers). Use `from_path` to construct, then
    `parse/validate` to work with artifacts.
    """

    path: Path
    kind: str = ""
    version: Optional[TemplateVersion] = None
    policy: Optional[TemplatePolicy] = None  # noqa
    blocks: List[TemplateBlock] = None  # populated on load()
    constraints: Optional["ArtifactKindConstraints"] = None
    _loaded: bool = False

    @staticmethod
    def first_nonempty(lines: List[str]) -> Optional[Tuple[int, str]]:
        """Return first non-empty (idx, line) or None."""
        for idx, line in enumerate(lines):
            if line.strip():
                return idx, line
        return None

    @staticmethod
    def error(kind: str, message: str, *, path: Path | int, line: int = 1, **extra) -> Dict[str, object]:
        """Uniform error factory used across template/artifact validation."""
        out: Dict[str, object] = {"type": kind, "message": message, "line": int(line)}
        if isinstance(path, Path):
            out["path"] = str(path)
        extra = {k: v for k, v in extra.items() if v is not None}
        out.update(extra)
        return out

    @staticmethod
    def parse_attrs(raw: str) -> Dict[str, str]:
        """Parse key="value" pairs in marker attribute section."""
        out: Dict[str, str] = {}
        for m in _ATTR_RE.finditer(raw):
            out[m.group(1)] = m.group(2)
        return out

    @staticmethod
    def parse_scalar(v: str) -> object:
        vv = str(v).strip()
        if vv in {"true", "false"}:
            return vv == "true"
        if re.fullmatch(r"-?\d+", vv):
            try:
                return int(vv)
            except Exception:
                return vv
        return vv

    @staticmethod
    def parse_frontmatter_yaml(text: str) -> Tuple[Optional[dict], int]:
        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            return None, -1
        end = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
        if end == -1:
            return None, -1

        root: Dict[str, object] = {}
        stack: List[Tuple[int, Dict[str, object]]] = [(0, root)]
        for raw in lines[1:end]:
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            if indent % 2 != 0:
                raise ValueError("Invalid frontmatter indentation (must be multiple of 2 spaces)")
            m = re.match(r"^\s*([^:#]+?)\s*:\s*(.*?)\s*$", raw)
            if not m:
                raise ValueError("Invalid frontmatter line")
            key = m.group(1).strip()
            val_raw = m.group(2).strip()
            while stack and indent < stack[-1][0]:
                stack.pop()
            if not stack:
                raise ValueError("Invalid frontmatter indentation")
            if indent > stack[-1][0] and indent != stack[-1][0] + 2:
                raise ValueError("Invalid frontmatter indentation jump")
            cur = stack[-1][1]
            if val_raw == "":
                child: Dict[str, object] = {}
                cur[key] = child
                stack.append((indent + 2, child))
                continue
            cur[key] = Template.parse_scalar(val_raw)
        return root, end

    @classmethod
    def from_path(cls, template_path: Path) -> Tuple[Optional["Template"], List[Dict[str, object]]]:
        """Convenience: instantiate Template and load immediately."""
        tmpl = cls(template_path)
        errs = tmpl.load()
        if errs:
            return None, errs
        return tmpl, []

    def load(self) -> List[Dict[str, object]]:
        """Load and parse the template file if not already loaded."""
        if self._loaded:
            return []
        try:
            text = self.path.read_text(encoding="utf-8")
        except Exception:
            return [Template.error("template", "Failed to read template file", path=self.path, line=1)]

        # Frontmatter is optional - if present, use it; otherwise infer from path
        kind: Optional[str] = None
        template_version = TemplateVersion(int(SUPPORTED_VERSION["major"]), int(SUPPORTED_VERSION["minor"]))
        unknown_sections = "warn"

        try:
            fm, _fm_end = Template.parse_frontmatter_yaml(text)
        except Exception as e:
            return [Template.error("template", f"Invalid template frontmatter: {e}", path=self.path, line=1)]

        if isinstance(fm, dict):
            # Check for cypilot-template key (legacy format)
            ft = fm.get("cypilot-template")
            if isinstance(ft, dict):
                kind = ft.get("kind")
                ver = ft.get("version")
                unknown_sections = ft.get("unknown_sections", "warn")
                if ver and isinstance(ver, dict) and isinstance(ver.get("major"), int) and isinstance(ver.get("minor"), int):
                    template_version = TemplateVersion(int(ver["major"]), int(ver["minor"]))

        # Infer kind from path if not in frontmatter
        # Path pattern: .../artifacts/{KIND}/template.md
        if not kind:
            parts = self.path.parts
            for i, part in enumerate(parts):
                if part == "artifacts" and i + 1 < len(parts):
                    kind = parts[i + 1].upper()
                    break

        if not kind:
            return [Template.error("template", "Cannot determine template kind (no frontmatter and path doesn't match .../artifacts/{KIND}/template.md)", path=self.path, line=1)]

        if unknown_sections not in {"error", "warn", "allow"}:
            unknown_sections = "warn"

        supported = TemplateVersion(int(SUPPORTED_VERSION["major"]), int(SUPPORTED_VERSION["minor"]))
        if template_version.major > supported.major or (
            template_version.major == supported.major and template_version.minor > supported.minor
        ):
            return [Template.error("template", "Template version is higher than supported", path=self.path, line=1)]

        blocks, errs = Template.parse_blocks(text.splitlines())
        if errs:
            out = []
            for e in errs:
                ee = dict(e)
                ee.setdefault("path", str(self.path))
                out.append(ee)
            return out

        object.__setattr__(self, "kind", kind.strip())
        object.__setattr__(self, "version", template_version)
        object.__setattr__(self, "policy", TemplatePolicy(unknown_sections=unknown_sections))
        object.__setattr__(self, "blocks", blocks)
        object.__setattr__(self, "_loaded", True)
        return []

    def parse(self, artifact_path: Path) -> "Artifact":
        # Ensure template is loaded before parsing artifact.
        errs = self.load()
        if errs:
            return Artifact(self, artifact_path, [], errs)
        art = Artifact(self, artifact_path, [], [])
        art.load()
        return art

    def validate(self, artifact_path: Path) -> Dict[str, List[Dict[str, object]]]:
        """Validate an artifact file against this template (structure/content)."""
        artifact = self.parse(artifact_path)
        return artifact.validate()

    @staticmethod
    def parse_blocks(lines: List[str]) -> Tuple[List[TemplateBlock], List[Dict[str, object]]]:
        """Parse paired cypilot markers into TemplateBlock objects with spans and attrs."""
        blocks: List[TemplateBlock] = []
        errors: List[Dict[str, object]] = []
        stack: List[Tuple[str, str, Dict[str, str], int]] = []
        for idx0, line in enumerate(lines):
            line_no = idx0 + 1
            for m in _MARKER_RE.finditer(line):
                m_type = m.group("type") or "free"
                name = m.group("name")
                attrs = Template.parse_attrs(m.group("attrs") or "")
                # Validate marker type
                if m_type not in VALID_MARKER_TYPES:
                    errors.append(Template.error("template", f"Unknown marker type '{m_type}'", path=0, line=line_no, id=name, marker_type=m_type))
                    continue
                if stack and stack[-1][0] == m_type and stack[-1][1] == name:
                    open_type, open_name, open_attrs, open_line = stack.pop()
                    req_val = str(open_attrs.get("required", "true")).strip().lower()
                    rep_val = str(open_attrs.get("repeat", "one")).strip().lower() or "one"
                    required = req_val != "false"
                    if rep_val not in {"one", "many"}:
                        errors.append(Template.error("template", "Invalid repeat", line=open_line, id=open_name, marker_type=open_type))
                        rep_val = "one"
                    # Validate kind names for id blocks: must be single word (no hyphens)
                    if open_type == "id" and "-" in open_name:
                        errors.append(Template.error(
                            "template",
                            f"ID kind '{open_name}' must be single word (no hyphens)",
                            line=open_line,
                            id=open_name,
                            marker_type=open_type,
                        ))
                    blocks.append(
                        TemplateBlock(
                            type=open_type,
                            name=open_name,
                            required=required,
                            repeat=rep_val,
                            attrs=open_attrs,
                            start_line=open_line,
                            end_line=line_no,
                        )
                    )
                else:
                    stack.append((m_type, name, attrs, line_no))
        for open_type, open_name, _attrs, open_line in stack:
            errors.append(Template.error("template", "Unclosed marker", path=0, line=open_line, id=open_name, marker_type=open_type))
        return blocks, errors

    @staticmethod
    def validate_block_content(artifact_path: Path, tpl: TemplateBlock, inst: ArtifactBlock, errors: List[Dict[str, object]]):
        """Validate an artifact block's content against its template block type."""
        content = inst.content
        first = Template.first_nonempty(content)
        if tpl.type == "free":
            return
        if tpl.type == "id":
            if not content:
                errors.append(Template.error("structure", "ID block missing content", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            has_attr = tpl.attrs.get("has", "")
            require_priority = "priority" in has_attr
            # Only check lines that start with **ID**: (ID blocks may wrap additional content)
            # Filter out content inside code fences (examples shouldn't trigger validation)
            filtered_content = filter_code_fences(content)
            id_candidates = [line for line in filtered_content if _ID_LABEL_RE.search(line)]
            if not id_candidates:
                errors.append(Template.error("structure", "ID block missing **ID**: line", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            id_lines = [line for line in id_candidates if _ID_DEF_RE.match(line.strip())]
            if not id_lines:
                errors.append(Template.error("structure", "Invalid ID format", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            for line in id_lines:
                if require_priority and "`p" not in line:
                    errors.append(Template.error("structure", "ID definition missing priority", path=artifact_path, line=inst.start_line, id=tpl.name))
                    return
                # If line has a checkbox, it must be a list item
                stripped = line.lstrip()
                has_checkbox = stripped.startswith("[") or "[ ]" in stripped or "[x]" in stripped.lower()
                if has_checkbox:
                    is_list_item = stripped.startswith("- ") or stripped.startswith("* ") or _ORDERED_NUMERIC_RE.match(stripped)
                    if not is_list_item:
                        errors.append(Template.error("structure", "Task checkbox must be in a list item", path=artifact_path, line=inst.start_line, id=tpl.name))
                        return
            return
        if tpl.type == "id-ref":
            if not content:
                errors.append(Template.error("structure", "ID ref block missing content", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            has_attr = tpl.attrs.get("has", "")
            require_priority = "priority" in has_attr
            tokens: List[str] = []
            for line in content:
                # Strip list markers (- or *) before processing
                stripped = line.lstrip()
                is_list_item = stripped.startswith("- ") or stripped.startswith("* ") or _ORDERED_NUMERIC_RE.match(stripped)
                # If line has a checkbox, it must be a list item
                has_checkbox = "[ ]" in stripped or "[x]" in stripped.lower()
                if has_checkbox and not is_list_item:
                    errors.append(Template.error("structure", "Task checkbox must be in a list item", path=artifact_path, line=inst.start_line, id=tpl.name))
                    return
                if stripped.startswith("- "):
                    stripped = stripped[2:]
                elif stripped.startswith("* "):
                    stripped = stripped[2:]
                for part in [p.strip() for p in stripped.split(",")]:
                    if part:
                        tokens.append(part)
            for tok in tokens:
                if not _ID_REF_RE.match(tok):
                    errors.append(Template.error("structure", "Invalid ID ref format", path=artifact_path, line=inst.start_line, id=tpl.name, value=tok))
                    return
                if require_priority and "`p" not in tok:
                    errors.append(Template.error("structure", "ID ref missing priority", path=artifact_path, line=inst.start_line, id=tpl.name, value=tok))
                    return
            return
        if tpl.type in {"list", "numbered-list", "task-list"}:
            if not content or not first:
                errors.append(Template.error("structure", "List block empty", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            for line in content:
                if not line.strip():
                    continue
                if tpl.type == "list" and not (line.lstrip().startswith("- ") or line.lstrip().startswith("* ")):
                    errors.append(Template.error("structure", "Expected bullet list", path=artifact_path, line=inst.start_line, id=tpl.name))
                    return
                if tpl.type == "numbered-list" and not _ORDERED_NUMERIC_RE.match(line.lstrip()):
                    errors.append(Template.error("structure", "Expected numbered list", path=artifact_path, line=inst.start_line, id=tpl.name))
                    return
                if tpl.type == "task-list":
                    if not line.lstrip().startswith("- ["):
                        errors.append(Template.error("structure", "Expected task list", path=artifact_path, line=inst.start_line, id=tpl.name))
                        return
                    if tpl.attrs.get("has", "").find("priority") != -1 and "`p" not in line:
                        errors.append(Template.error("structure", "Task item missing priority", path=artifact_path, line=inst.start_line, id=tpl.name))
                        return
            return
        if tpl.type == "table":
            nonempty = [ln for ln in content if ln.strip()]
            if len(nonempty) < 2:
                errors.append(Template.error("structure", "Table must have header and separator", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            header = nonempty[0]
            sep = nonempty[1] if len(nonempty) > 1 else ""
            header_cols = header.count("|") - 1 if "|" in header else 0
            if header_cols < 1 or "|" not in sep:
                errors.append(Template.error("structure", "Invalid table header/separator", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            # separator must have same columns and dashes
            sep_cells = [p.strip() for p in sep.strip().strip("|").split("|")]
            if len(sep_cells) != header_cols or any(not set(c) <= set("-:") for c in sep_cells):
                errors.append(Template.error("structure", "Table separator column count mismatch", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            data_rows = 0
            for ln in nonempty[2:]:
                if ln.strip().startswith("|"):
                    cells = [p.strip() for p in ln.strip().strip("|").split("|")]
                    if len(cells) != header_cols:
                        errors.append(Template.error("structure", "Table row column count mismatch", path=artifact_path, line=inst.start_line, id=tpl.name))
                        return
                    data_rows += 1
            if data_rows == 0:
                errors.append(Template.error("structure", "Table must have at least one data row", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            return
        if tpl.type == "paragraph":
            if not first:
                errors.append(Template.error("structure", "Paragraph block empty", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            return
        if tpl.type == "code":
            if not first or not _CODE_FENCE_RE.match(first[1]):
                errors.append(Template.error("structure", "Code block must start with ```", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            closing = False
            for line in content[1:]:
                if _CODE_FENCE_RE.match(line):
                    closing = True
                    break
            if not closing:
                errors.append(Template.error("structure", "Code fence must be closed", path=artifact_path, line=inst.start_line, id=tpl.name))
            return
        if tpl.type in {"#", "##", "###", "####", "#####", "######"}:
            level = len(tpl.type)
            if not first:
                errors.append(Template.error("structure", "Heading block empty", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            if not first[1].lstrip().startswith("#" * level + " "):
                errors.append(Template.error("structure", "Heading level mismatch", path=artifact_path, line=inst.start_line, id=tpl.name))
            return
        if tpl.type == "link":
            if not first or "[" not in first[1] or "](" not in first[1]:
                errors.append(Template.error("structure", "Invalid link", path=artifact_path, line=inst.start_line, id=tpl.name))
            return
        if tpl.type == "image":
            if not first or not first[1].lstrip().startswith("!"):
                errors.append(Template.error("structure", "Invalid image", path=artifact_path, line=inst.start_line, id=tpl.name))
            return
        if tpl.type == "cdsl":
            if not content or not first:
                errors.append(Template.error("structure", "CDSL block empty", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            for line in content:
                if not line.strip():
                    continue
                if not _CDSL_LINE_RE.match(line):
                    errors.append(Template.error("structure", "Invalid CDSL line", path=artifact_path, line=inst.start_line, id=tpl.name, value=line.strip()))
                    return
            return


@dataclass
class IdDefinition:
    id: str
    line: int
    checked: bool
    priority: Optional[str]
    block: ArtifactBlock
    artifact_path: Path
    to_code: bool = False  # from template attr to_code="true"


@dataclass
class IdReference:
    id: str
    line: int
    checked: bool
    priority: Optional[str]
    block: ArtifactBlock
    artifact_path: Path


@dataclass
class ArtifactBlock:
    template_block: TemplateBlock
    content: List[str]
    start_line: int
    end_line: int

    def text(self) -> str:
        return "\n".join(self.content).strip()


@dataclass(frozen=True)
class CdslInstruction:
    checked: bool
    phase: Optional[int]
    inst: str
    line: int
    block: ArtifactBlock


class Artifact:
    """Artifact parsed against a Template; holds block spans and extracted IDs/refs."""
    def __init__(self, template: Template, path: Path, blocks: List[ArtifactBlock], errors: List[Dict[str, object]]):
        self.template = template
        self.path = path
        self.blocks = blocks
        self._errors = errors
        self.id_definitions: List[IdDefinition] = []
        self.id_references: List[IdReference] = []
        self.task_statuses: List[Tuple[bool, ArtifactBlock]] = []  # (checked?, block)
        self.cdsl_instructions: List[CdslInstruction] = []

    def load(self) -> None:
        """Parse artifact markers into blocks; accumulate structural errors."""
        if self.blocks:
            return
        try:
            text = self.path.read_text(encoding="utf-8")
        except Exception:
            self._errors.append(Template.error("file", "Failed to read artifact", path=self.path, line=1))
            return

        # Detect template frontmatter in artifact (should only be in templates, not artifacts)
        lines = text.splitlines()
        if lines and lines[0].strip() == "---":
            for i, ln in enumerate(lines[1:], start=2):
                if ln.strip() == "---":
                    break
                if "cypilot-template:" in ln:
                    self._errors.append(Template.error(
                        "structure",
                        "Artifact contains template frontmatter (cypilot-template:) - this belongs only in template files, not artifacts",
                        path=self.path,
                        line=i,
                    ))
                    break
        art_blocks: List[ArtifactBlock] = []
        stack: List[Tuple[TemplateBlock, int]] = []

        tpl_by_key: Dict[Tuple[str, str], List[TemplateBlock]] = {}
        for b in self.template.blocks:
            tpl_by_key.setdefault((b.type, b.name), []).append(b)

        for idx0, line in enumerate(lines):
            line_no = idx0 + 1
            for m in _MARKER_RE.finditer(line):
                m_type = m.group("type") or "free"
                name = m.group("name")
                attrs = Template.parse_attrs(m.group("attrs") or "")
                key = (m_type, name)
                matching_tpl = tpl_by_key.get(key, [])
                tpl_ref = matching_tpl[0] if matching_tpl else TemplateBlock(m_type, name, True, "one", attrs, line_no, line_no)

                if stack and stack[-1][0].type == m_type and stack[-1][0].name == name:
                    open_tpl, open_idx = stack.pop()
                    content = lines[open_idx + 1 : idx0]
                    art_blocks.append(
                        ArtifactBlock(
                            template_block=open_tpl,
                            content=content,
                            start_line=open_idx + 2,  # first content line
                            end_line=line_no,
                        )
                    )
                else:
                    stack.append((tpl_ref, idx0))

        for open_tpl, open_idx in stack:
            self._errors.append(Template.error("structure", "Unclosed marker in artifact", path=self.path, line=open_idx + 1, id=open_tpl.name, marker_type=open_tpl.type))

        self.blocks.extend(art_blocks)

    def list_ids(self) -> List[str]:
        return sorted(set(self.list_defined() + self.list_refs()))

    def list_refs(self) -> List[str]:
        if not self.id_references:
            self._extract_ids_and_refs()
        return sorted({r.id for r in self.id_references})

    def list_defined(self) -> List[str]:
        if not self.id_definitions:
            self._extract_ids_and_refs()
        return sorted({d.id for d in self.id_definitions})

    def get(self, id_value: str) -> Optional[str]:
        for blk in self.blocks:
            if blk.template_block.type == "id":
                for line in blk.content:
                    if id_value in line:
                        return blk.text()
            for line in blk.content:
                if id_value in line:
                    return blk.text()
        return None

    def get_with_location(self, id_value: str) -> Optional[Tuple[str, int, int]]:
        """Get content containing id_value along with start and end line numbers.

        Returns:
            Tuple of (text, start_line, end_line) or None if not found.
        """
        for blk in self.blocks:
            if blk.template_block.type == "id":
                for line in blk.content:
                    if id_value in line:
                        return (blk.text(), blk.start_line, blk.end_line)
            for line in blk.content:
                if id_value in line:
                    return (blk.text(), blk.start_line, blk.end_line)
        return None

    def list(self, ids: Sequence[str]) -> List[Optional[str]]:
        return [self.get(i) for i in ids]

    def validate(self) -> Dict[str, List[Dict[str, object]]]:
        errors: List[Dict[str, object]] = list(self._errors)
        warnings: List[Dict[str, object]] = []
        art_by_key: Dict[Tuple[str, str], List[ArtifactBlock]] = {}
        for b in self.blocks:
            art_by_key.setdefault((b.template_block.type, b.template_block.name), []).append(b)

        tpl_by_key: Dict[Tuple[str, str], List[TemplateBlock]] = {}
        for b in self.template.blocks:
            tpl_by_key.setdefault((b.type, b.name), []).append(b)

        # Get all repeat="many" blocks as potential parent containers
        repeat_many_blocks = [b for b in self.blocks if b.template_block.repeat == "many"]

        def find_parent_repeat_block(blk: ArtifactBlock) -> Optional[ArtifactBlock]:
            """Find the innermost repeat=many block containing this block."""
            best: Optional[ArtifactBlock] = None
            for parent in repeat_many_blocks:
                # parent contains blk if parent.start_line < blk.start_line < blk.end_line < parent.end_line
                if parent.start_line < blk.start_line and blk.end_line < parent.end_line:
                    if best is None or parent.start_line > best.start_line:
                        best = parent
            return best

        def find_template_parent(tpl_blk: TemplateBlock) -> Optional[TemplateBlock]:
            """Find the innermost template block containing this block."""
            best: Optional[TemplateBlock] = None
            for other in self.template.blocks:
                if other is tpl_blk:
                    continue
                if other.start_line < tpl_blk.start_line and tpl_blk.end_line < other.end_line:
                    if best is None or other.start_line > best.start_line:
                        best = other
            return best

        def find_artifact_parent(art_blk: ArtifactBlock) -> Optional[ArtifactBlock]:
            """Find the innermost artifact block containing this block."""
            best: Optional[ArtifactBlock] = None
            for other in self.blocks:
                if other is art_blk:
                    continue
                if other.start_line < art_blk.start_line and art_blk.end_line < other.end_line:
                    if best is None or other.start_line > best.start_line:
                        best = other
            return best

        for key, tpl_list in tpl_by_key.items():
            instances = art_by_key.get(key, [])
            for tpl in tpl_list:
                if tpl.required and not instances:
                    errors.append(Template.error("structure", "Required block missing", path=self.path, line=tpl.start_line, id=tpl.name, marker_type=tpl.type))
                    continue
                if tpl.repeat == "one" and len(instances) > 1:
                    # Group instances by their containing repeat="many" parent
                    by_parent: Dict[Optional[int], List[ArtifactBlock]] = {}
                    for inst in instances:
                        parent = find_parent_repeat_block(inst)
                        parent_key = parent.start_line if parent else None
                        by_parent.setdefault(parent_key, []).append(inst)
                    # Only error if multiple instances within the same parent
                    for parent_key, group in by_parent.items():
                        if len(group) > 1:
                            errors.append(Template.error("structure", "Block must appear once", path=self.path, line=group[1].start_line, id=tpl.name, marker_type=tpl.type))
                for inst in instances:
                    Template.validate_block_content(self.path, tpl, inst, errors)

        # Validate nesting structure: artifact blocks must be nested inside the same parent type as in template
        # Skip nesting validation for blocks inside repeat="many" parents (structure varies by instance)
        for art_blk in self.blocks:
            tpl_blk = art_blk.template_block

            # Skip nesting check if this block type appears multiple times in template
            # (can't reliably match which occurrence an artifact block corresponds to)
            key = (tpl_blk.type, tpl_blk.name)
            if len(tpl_by_key.get(key, [])) > 1:
                continue

            tpl_parent = find_template_parent(tpl_blk)

            # Skip nesting check if parent has repeat="many" (flexible structure)
            if tpl_parent is not None and tpl_parent.repeat == "many":
                continue

            if tpl_parent is None:
                # Template block is at root level - artifact block should also be at root
                art_parent = find_artifact_parent(art_blk)
                if art_parent is not None:
                    # Only error if artifact parent is NOT a repeat="many" block
                    if art_parent.template_block.repeat != "many":
                        errors.append(Template.error(
                            "nesting",
                            f"Block should be at root level, not nested inside {art_parent.template_block.type}:{art_parent.template_block.name}",
                            path=self.path,
                            line=art_blk.start_line,
                            id=tpl_blk.name,
                            marker_type=tpl_blk.type,
                        ))
            else:
                # Template block is nested - find artifact parent and check type matches
                art_parent = find_artifact_parent(art_blk)
                if art_parent is None:
                    errors.append(Template.error(
                        "nesting",
                        f"Block must be nested inside {tpl_parent.type}:{tpl_parent.name}",
                        path=self.path,
                        line=art_blk.start_line,
                        id=tpl_blk.name,
                        marker_type=tpl_blk.type,
                        expected_parent=f"{tpl_parent.type}:{tpl_parent.name}",
                    ))
                elif (art_parent.template_block.type, art_parent.template_block.name) != (tpl_parent.type, tpl_parent.name):
                    errors.append(Template.error(
                        "nesting",
                        f"Block nested inside wrong parent: expected {tpl_parent.type}:{tpl_parent.name}, got {art_parent.template_block.type}:{art_parent.template_block.name}",
                        path=self.path,
                        line=art_blk.start_line,
                        id=tpl_blk.name,
                        marker_type=tpl_blk.type,
                        expected_parent=f"{tpl_parent.type}:{tpl_parent.name}",
                        actual_parent=f"{art_parent.template_block.type}:{art_parent.template_block.name}",
                    ))

        # Extract IDs/refs/tasks for status cross-checks inside artifact
        self._extract_ids_and_refs()
        self._validate_id_task_statuses(errors)
        self._validate_spec_filename(errors)
        self._validate_constraints_strict(errors)

        # Unknown markers are always errors (markers in artifact not defined in template)
        for key, inst_list in art_by_key.items():
            if key not in tpl_by_key:
                errors.append(Template.error("structure", "Unknown marker", path=self.path, line=inst_list[0].start_line, marker_type=key[0], id=key[1]))

        return {"errors": errors, "warnings": warnings}

    def _validate_constraints_strict(self, errors: List[Dict[str, object]]) -> None:
        """Strict constraints validation.

        When a template has kit constraints attached, artifacts must:
        - only contain ID kinds that are listed in constraints
        - contain at least one instance for each constrained kind
        - respect headings scoping when specified
        """
        constraints = getattr(self.template, "constraints", None)
        if constraints is None:
            return

        allowed_defs = {c.kind.strip().lower() for c in constraints.defined_id}
        allowed_refs = set(allowed_defs)

        defs_by_kind: Dict[str, List[IdDefinition]] = {}
        for d in self.id_definitions:
            k = str(getattr(d.block.template_block, "name", "") or "").strip().lower()
            if not k or k == "markerless":
                continue
            defs_by_kind.setdefault(k, []).append(d)
            if k not in allowed_defs:
                errors.append(Template.error(
                    "constraints",
                    "ID kind not allowed by constraints",
                    path=self.path,
                    line=d.line,
                    artifact_kind=self.template.kind,
                    id_kind=k,
                    id=d.id,
                    section="defined-id",
                    allowed=sorted(allowed_defs),
                ))

        refs_by_kind: Dict[str, List[IdReference]] = {}
        for r in self.id_references:
            k = str(getattr(r.block.template_block, "name", "") or "").strip().lower()
            if not k or k == "markerless":
                continue
            refs_by_kind.setdefault(k, []).append(r)
            if k not in allowed_refs:
                errors.append(Template.error(
                    "constraints",
                    "ID ref kind not allowed by constraints",
                    path=self.path,
                    line=r.line,
                    artifact_kind=self.template.kind,
                    id_kind=k,
                    id=r.id,
                    section="referenced-id",
                    allowed=sorted(allowed_refs),
                ))

        # Required presence: every constrained kind must appear at least once.
        for c in constraints.defined_id:
            k = c.kind.strip().lower()
            if k and k not in defs_by_kind:
                errors.append(Template.error(
                    "constraints",
                    "Required ID kind missing in artifact",
                    path=self.path,
                    line=1,
                    artifact_kind=self.template.kind,
                    id_kind=k,
                    section="defined-id",
                ))

        # Headings scoping.
        # Build active heading titles per line (1-indexed), outside code fences.
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except Exception:
            return

        headings_at: List[List[str]] = [[] for _ in range(len(lines) + 1)]
        stack: List[Tuple[int, str]] = []  # (level, title)
        in_fence = False
        for idx0, raw in enumerate(lines):
            line_no = idx0 + 1
            if _CODE_FENCE_RE.match(raw):
                in_fence = not in_fence
                headings_at[line_no] = [t for _, t in stack]
                continue
            if not in_fence:
                m = _HEADING_RE.match(raw)
                if m:
                    level = len(m.group(1))
                    title = str(m.group(2) or "").strip()
                    while stack and stack[-1][0] >= level:
                        stack.pop()
                    stack.append((level, title))
            headings_at[line_no] = [t for _, t in stack]

        def _check_headings_for_defs(c) -> None:
            if not c.headings:
                return
            k = c.kind.strip().lower()
            allowed = {h.strip() for h in c.headings if isinstance(h, str) and h.strip()}
            if not allowed:
                return
            defs = defs_by_kind.get(k, [])
            found_ok = False
            for d in defs:
                active = headings_at[d.line] if 0 <= d.line < len(headings_at) else []
                ok = any(h in allowed for h in active)
                if not ok:
                    errors.append(Template.error(
                        "constraints",
                        "ID definition not under required headings",
                        path=self.path,
                        line=d.line,
                        artifact_kind=self.template.kind,
                        id_kind=k,
                        id=d.id,
                        section="defined-id",
                        headings=sorted(allowed),
                        found_headings=active,
                    ))
                else:
                    found_ok = True
            if defs and not found_ok:
                errors.append(Template.error(
                    "constraints",
                    "Required headings contain no ID definitions",
                    path=self.path,
                    line=1,
                    artifact_kind=self.template.kind,
                    id_kind=k,
                    section="defined-id",
                    headings=sorted(allowed),
                ))

        for c in constraints.defined_id:
            _check_headings_for_defs(c)

    def _extract_ids_and_refs(self) -> None:
        if self.id_definitions or self.id_references:
            return
        try:
            from .document import file_has_cypilot_markers, scan_cpt_ids_without_markers
        except Exception:
            file_has_cypilot_markers = None  # type: ignore[assignment]
            scan_cpt_ids_without_markers = None  # type: ignore[assignment]

        if file_has_cypilot_markers is not None and scan_cpt_ids_without_markers is not None:
            if not file_has_cypilot_markers(self.path):
                hits = scan_cpt_ids_without_markers(self.path)
                if hits:
                    dummy_tpl = TemplateBlock(
                        type="free",
                        name="markerless",
                        required=False,
                        repeat="one",
                        attrs={},
                        start_line=1,
                        end_line=1,
                    )
                    dummy_blk = ArtifactBlock(
                        template_block=dummy_tpl,
                        content=[],
                        start_line=1,
                        end_line=1,
                    )
                    for h in hits:
                        h_type = str(h.get("type", ""))
                        h_id = str(h.get("id", "")).strip()
                        if not h_id:
                            continue
                        line = int(h.get("line", 1) or 1)
                        checked = bool(h.get("checked", False))
                        priority = h.get("priority")
                        prio = str(priority) if priority is not None else None
                        if h_type == "definition":
                            self.id_definitions.append(
                                IdDefinition(
                                    id=h_id,
                                    line=line,
                                    checked=checked,
                                    priority=prio,
                                    block=dummy_blk,
                                    artifact_path=self.path,
                                    to_code=False,
                                )
                            )
                        elif h_type == "reference":
                            self.id_references.append(
                                IdReference(
                                    id=h_id,
                                    line=line,
                                    checked=checked,
                                    priority=prio,
                                    block=dummy_blk,
                                    artifact_path=self.path,
                                )
                            )
                    return
        for blk in self.blocks:
            if blk.template_block.type == "id":
                to_code = str(blk.template_block.attrs.get("to_code", "false")).strip().lower() == "true"
                # Skip lines inside code fences (examples shouldn't be extracted as real IDs)
                for rel_idx, line in enumerate_outside_code_fences(blk.content):
                    m = _ID_DEF_RE.match(line.strip())
                    if not m:
                        continue
                    checked = (m.group("task") or "").lower().find("x") != -1
                    priority = m.group("priority") or m.group("priority_only")
                    id_value = m.group("id") or m.group("id2") or m.group("id3")
                    self.id_definitions.append(
                        IdDefinition(
                            id=id_value,
                            line=blk.start_line + rel_idx,
                            checked=checked,
                            priority=priority,
                            block=blk,
                            artifact_path=self.path,
                            to_code=to_code,
                        )
                    )
            if blk.template_block.type == "id-ref":
                # Skip lines inside code fences
                for rel_idx, line in enumerate_outside_code_fences(blk.content):
                    stripped = line.strip()
                    if stripped.startswith("- "):
                        stripped = stripped[2:]
                    elif stripped.startswith("* "):
                        stripped = stripped[2:]
                    m = _ID_REF_RE.match(stripped)
                    if not m:
                        continue
                    checked = (m.group("task") or "").lower().find("x") != -1
                    priority = m.group("priority") or m.group("priority_only")
                    self.id_references.append(
                        IdReference(
                            id=m.group("id"),
                            line=blk.start_line + rel_idx,
                            checked=checked,
                            priority=priority,
                            block=blk,
                            artifact_path=self.path,
                        )
                    )
            elif blk.template_block.type not in {"id", "id-ref"}:
                # generic backticked refs anywhere (except id/id-ref blocks which are handled above)
                # Skip lines inside code fences
                for rel_idx, line in enumerate_outside_code_fences(blk.content):
                    for mm in _BACKTICK_ID_RE.finditer(line):
                        self.id_references.append(
                            IdReference(
                                id=mm.group(1),
                                line=blk.start_line + rel_idx,
                                checked=False,
                                priority=None,
                                block=blk,
                                artifact_path=self.path,
                            )
                        )
            if blk.template_block.type == "task-list":
                for rel_idx, line in enumerate(blk.content, start=0):
                    line_stripped = line.strip()
                    if not line_stripped or not line_stripped.startswith("- ["):
                        continue
                    checked = "[x" in line_stripped.lower()
                    self.task_statuses.append((checked, blk))
            if blk.template_block.type == "cdsl":
                for rel_idx, line in enumerate(blk.content, start=0):
                    if not line.strip():
                        continue
                    if _CDSL_LINE_RE.match(line):
                        checked = "[x" in line.lower()
                        self.task_statuses.append((checked, blk))

                        m_phase = _CDSL_PHASE_RE.search(line)
                        phase: Optional[int] = int(m_phase.group("phase")) if m_phase else None
                        m_inst = _CDSL_INST_RE.search(line)
                        if m_inst:
                            self.cdsl_instructions.append(CdslInstruction(
                                checked=checked,
                                phase=phase,
                                inst=m_inst.group("inst"),
                                line=blk.start_line + rel_idx,
                                block=blk,
                            ))

    def _validate_id_task_statuses(self, errors: List[Dict[str, object]]):
        """Enforce task completion consistency between tasks and ID definitions.

        For each ID definition with has="task", find all tasks within that ID block's
        line range and validate that their completion status is consistent with the ID's status.

        Also enforces cascade logic for nested ID definitions (e.g., id:status → id:spec in DECOMPOSITION).
        """
        if not self.id_definitions:
            return

        for d in self.id_definitions:
            has_task_attr = "task" in (d.block.template_block.attrs.get("has", "") or "")
            if not has_task_attr:
                continue

            # Find all tasks within this ID block's line range
            id_start = d.block.start_line
            id_end = d.block.end_line
            tasks_in_block: List[bool] = []

            for checked, task_blk in self.task_statuses:
                # Task block is within ID block if its start is between ID's start and end
                if id_start <= task_blk.start_line <= id_end:
                    tasks_in_block.append(checked)

            # Also find nested ID definitions within this ID block's range (cascade validation)
            # E.g., id:status contains id:spec blocks in DECOMPOSITION artifact
            nested_ids: List[bool] = []
            for other_d in self.id_definitions:
                if other_d is d:
                    continue
                # Check if other_d is nested within d's range (but not the same block)
                if id_start < other_d.block.start_line and other_d.block.end_line < id_end:
                    # Only consider IDs with has="task" for cascade
                    other_has_task = "task" in (other_d.block.template_block.attrs.get("has", "") or "")
                    if other_has_task:
                        nested_ids.append(other_d.checked)

            # Combine tasks and nested IDs for cascade validation
            all_children = tasks_in_block + nested_ids
            if not all_children:
                continue

            all_done = all(all_children)

            if all_done and not d.checked:
                errors.append(Template.error("structure", "All tasks done but ID not marked done", path=self.path, line=d.line, id=d.id))
            if not all_done and d.checked:
                errors.append(Template.error("structure", "ID marked done but tasks not all done", path=self.path, line=d.line, id=d.id))

    def _validate_spec_filename(self, errors: List[Dict[str, object]]):
        """Validate that SPEC artifact filename matches the spec ID slug.

        For SPEC kind artifacts, the filename (without .md) should match the
        spec slug in the main spec ID. E.g., file `template-system.md` should have
        ID `cpt-{system}-spec-template-system`.

        Checks both id definitions and id-ref:spec references (the top-level spec ref).
        Skips nested IDs like flow, algo, state, req.
        """
        if self.template.kind != "SPEC":
            return

        filename = self.path.stem  # filename without extension

        # Sub-ID suffixes that indicate nested IDs within a spec
        nested_suffixes = ("-flow-", "-algo-", "-state-", "-req-")

        def check_spec_id(id_value: str, line: int):
            # Check if this is a spec ID (contains "-spec-")
            if "-spec-" not in id_value:
                return
            # Skip nested IDs (flows, algos, states, requirements)
            if any(suffix in id_value for suffix in nested_suffixes):
                return
            # Extract the slug after "-spec-"
            parts = id_value.split("-spec-", 1)
            if len(parts) != 2:
                return
            spec_slug = parts[1]
            if spec_slug != filename:
                errors.append(Template.error(
                    "structure",
                    "Spec filename does not match ID slug",
                    path=self.path,
                    line=line,
                    id=id_value,
                    expected_filename=f"{spec_slug}.md",
                    actual_filename=f"{filename}.md",
                ))

        # Check id definitions
        for d in self.id_definitions:
            check_spec_id(d.id, d.line)

        # Check id-ref:spec references (the main spec reference at top of file)
        for r in self.id_references:
            # Only check references in id-ref:spec blocks
            if r.block.template_block.name == "spec":
                check_spec_id(r.id, r.line)


def cross_validate_artifacts(
    artifacts: Sequence[Artifact],
    registered_systems: Optional[Iterable[str]] = None,
    known_kinds: Optional[Iterable[str]] = None,
) -> Dict[str, List[Dict[str, object]]]:
    """Cross-artifact validation (markerless-first).

    The validator intentionally ignores template markers and performs a markerless
    scan of all artifacts (even if markers are present). This yields a stable set of
    ID definitions and references.

    Primary rules are derived from `constraints.json` attached to templates.
    """
    errors: List[Dict[str, object]] = []
    warnings: List[Dict[str, object]] = []

    # Normalize known_kinds to lowercase set (if provided)
    kinds_set: Optional[set] = None
    if known_kinds is not None:
        kinds_set = {k.lower() for k in known_kinds}

    from .document import headings_by_line_markerless, scan_cpt_ids_markerless

    # Collected markerless hits
    defs_by_id: Dict[str, List[Dict[str, object]]] = {}
    refs_by_id: Dict[str, List[Dict[str, object]]] = {}

    # Per-system scoping
    present_kinds_by_system: Dict[str, set[str]] = {}
    refs_by_system_kind: Dict[str, Dict[str, List[Dict[str, object]]]] = {}
    defs_by_system_kind: Dict[str, Dict[str, List[Dict[str, object]]]] = {}

    # Constraints by artifact kind
    constraints_by_artifact_kind: Dict[str, object] = {}
    missing_constraints_kinds: set[str] = set()
    all_constrained_id_kinds: set[str] = set()

    # Normalize registered_systems to lowercase for matching
    systems_set: set[str] = set()
    if registered_systems is not None:
        systems_set = {str(s).lower() for s in registered_systems}

    def _match_system_from_id(cpt: str) -> Optional[str]:
        """Match system slug using registered systems (longest prefix match)."""
        if not cpt.lower().startswith("cpt-"):
            return None
        if not systems_set:
            # Fallback: best-effort second segment
            parts = cpt.split("-")
            return parts[1].lower() if len(parts) >= 3 else None

        matched: Optional[str] = None
        for sys in systems_set:
            prefix = f"cpt-{sys}-"
            if cpt.lower().startswith(prefix):
                if matched is None or len(sys) > len(matched):
                    matched = sys
        return matched

    def _extract_kind_from_id(cpt: str, system: Optional[str]) -> Optional[str]:
        if not cpt.lower().startswith("cpt-"):
            return None
        if system is None:
            return None
        prefix = f"cpt-{system}-"
        if not cpt.lower().startswith(prefix.lower()):
            return None
        remainder = cpt[len(prefix):]
        if not remainder:
            return None
        return remainder.split("-", 1)[0].lower()

    # Collect constraints and build global set of known ID kinds from constraints
    for art in artifacts:
        ak = str(art.template.kind)
        c = getattr(art.template, "constraints", None)
        if c is None:
            missing_constraints_kinds.add(ak)
            continue
        constraints_by_artifact_kind[ak] = c
        for ic in getattr(c, "defined_id", []) or []:
            try:
                all_constrained_id_kinds.add(str(getattr(ic, "kind", "")).strip().lower())
            except Exception:
                pass

    if missing_constraints_kinds:
        errors.append(Template.error(
            "constraints",
            "Missing constraints for artifact kinds",
            path=Path("<constraints.json>"),
            line=1,
            kinds=sorted(missing_constraints_kinds),
        ))

    # Build markerless indexes
    headings_cache: Dict[str, List[List[str]]] = {}
    for art in artifacts:
        kind = str(art.template.kind)
        hits = scan_cpt_ids_markerless(art.path)
        hkey = str(art.path)
        if hkey not in headings_cache:
            headings_cache[hkey] = headings_by_line_markerless(art.path)
        headings_at = headings_cache[hkey]

        for h in hits:
            hid = str(h.get("id", "")).strip()
            if not hid:
                continue
            line = int(h.get("line", 1) or 1)
            checked = bool(h.get("checked", False))
            system = _match_system_from_id(hid)
            id_kind = _extract_kind_from_id(hid, system)
            active_headings = headings_at[line] if 0 <= line < len(headings_at) else []

            row = {
                "id": hid,
                "line": line,
                "checked": checked,
                "priority": h.get("priority"),
                "artifact_kind": kind,
                "artifact_path": art.path,
                "system": system,
                "id_kind": id_kind,
                "headings": active_headings,
            }

            if str(h.get("type")) == "definition":
                defs_by_id.setdefault(hid, []).append(row)
                if system:
                    present_kinds_by_system.setdefault(system, set()).add(kind)
                    defs_by_system_kind.setdefault(system, {}).setdefault(kind, []).append(row)
            elif str(h.get("type")) == "reference":
                refs_by_id.setdefault(hid, []).append(row)
                if system:
                    present_kinds_by_system.setdefault(system, set()).add(kind)
                    refs_by_system_kind.setdefault(system, {}).setdefault(kind, []).append(row)

    # Helper to check if a reference's system is registered
    def _is_external_system_ref(cpt: str) -> bool:
        """Check if this ID references an external (non-registered) system.

        If no registered_systems provided, we cannot determine external refs,
        so treat all as internal (will error if no definition).
        """
        if not systems_set:
            return False  # no systems known, can't distinguish external
        if not cpt.lower().startswith("cpt-"):
            return False
        # Try to find if any registered system matches as prefix
        for sys in systems_set:
            prefix = f"cpt-{sys}-"
            if cpt.lower().startswith(prefix):
                return False  # system is registered, not external
        return True  # no registered system matched → external

    # Helper to extract kind from Cypilot ID (first segment after system)
    def _extract_kind_from_id(cpt: str) -> Optional[str]:
        """Extract the kind segment from an Cypilot ID."""
        if not cpt.lower().startswith("cpt-"):
            return None
        # Find matching system (longest match)
        matched_sys: Optional[str] = None
        for sys in systems_set:
            prefix = f"cpt-{sys}-"
            if cpt.lower().startswith(prefix.lower()):
                if matched_sys is None or len(sys) > len(matched_sys):
                    matched_sys = sys
        if matched_sys is None:
            return None
        prefix_len = len(f"cpt-{matched_sys}-")
        remainder = cpt[prefix_len:]
        if not remainder:
            return None
        return remainder.split("-", 1)[0].lower()

    # Validate ID kinds against constraints (authoritative) and known_kinds (secondary)
    for did, rows in defs_by_id.items():
        for r in rows:
            sys = r.get("system")
            if sys is None:
                continue
            k = r.get("id_kind")
            if k and all_constrained_id_kinds and str(k).lower() not in all_constrained_id_kinds:
                errors.append(Template.error(
                    "constraints",
                    "ID uses kind not defined in constraints",
                    path=r.get("artifact_path"),
                    line=int(r.get("line", 1) or 1),
                    id=did,
                    unknown_kind=k,
                ))

    for rid, rows in refs_by_id.items():
        for r in rows:
            sys = r.get("system")
            if sys is None:
                continue
            k = r.get("id_kind")
            if k and all_constrained_id_kinds and str(k).lower() not in all_constrained_id_kinds:
                errors.append(Template.error(
                    "constraints",
                    "Reference uses kind not defined in constraints",
                    path=r.get("artifact_path"),
                    line=int(r.get("line", 1) or 1),
                    id=rid,
                    unknown_kind=k,
                ))

    if kinds_set:
        for did, rows in defs_by_id.items():
            for r in rows:
                k = r.get("id_kind")
                if k and str(k).lower() not in kinds_set:
                    warnings.append(Template.error(
                        "structure",
                        f"ID uses unknown kind '{k}'",
                        path=r.get("artifact_path"),
                        line=int(r.get("line", 1) or 1),
                        id=did,
                        unknown_kind=k,
                    ))

    # refs must have definitions (but only error if system is registered)
    for rid, rows in refs_by_id.items():
        if rid not in defs_by_id:
            if _is_external_system_ref(rid):
                continue
            for r in rows:
                errors.append(Template.error(
                    "structure",
                    "Reference has no definition",
                    path=r.get("artifact_path"),
                    line=int(r.get("line", 1) or 1),
                    id=rid,
                ))

    # checked ref implies checked def
    for rid, rows in refs_by_id.items():
        for r in rows:
            if not bool(r.get("checked", False)):
                continue
            defs = defs_by_id.get(rid, [])
            for d in defs:
                if bool(d.get("checked", False)):
                    continue
                errors.append(Template.error(
                    "structure",
                    "Reference marked done but definition not done",
                    path=r.get("artifact_path"),
                    line=int(r.get("line", 1) or 1),
                    id=rid,
                ))

    # Constraints: per-artifact kind strict definition requirements and headings scoping.
    for art in artifacts:
        ak = str(art.template.kind)
        c = constraints_by_artifact_kind.get(ak)
        if c is None:
            continue

        allowed_kinds = {str(getattr(ic, "kind", "")).strip().lower() for ic in getattr(c, "defined_id", []) or []}
        defs_in_file = [r for r in defs_by_id.values() for r in r if str(r.get("artifact_path")) == str(art.path) and r.get("system") is not None]
        seen_kinds: set[str] = set()
        for d in defs_in_file:
            k = str(d.get("id_kind") or "").lower()
            if k:
                seen_kinds.add(k)
                if allowed_kinds and k not in allowed_kinds:
                    errors.append(Template.error(
                        "constraints",
                        "ID kind not allowed by constraints",
                        path=art.path,
                        line=int(d.get("line", 1) or 1),
                        artifact_kind=ak,
                        id_kind=k,
                        id=str(d.get("id")),
                    ))

        for ic in getattr(c, "defined_id", []) or []:
            k = str(getattr(ic, "kind", "")).strip().lower()
            if k and k not in seen_kinds:
                errors.append(Template.error(
                    "constraints",
                    "Required ID kind missing in artifact",
                    path=art.path,
                    line=1,
                    artifact_kind=ak,
                    id_kind=k,
                ))

            # heading scope for definitions
            allowed_headings = set([h.strip() for h in (getattr(ic, "headings", None) or []) if isinstance(h, str) and h.strip()])
            if not allowed_headings:
                continue
            defs_of_kind = [d for d in defs_in_file if str(d.get("id_kind") or "").lower() == k]
            if not defs_of_kind:
                continue
            ok_any = False
            for d in defs_of_kind:
                active = d.get("headings") or []
                ok = any(h in allowed_headings for h in active)
                if ok:
                    ok_any = True
                else:
                    errors.append(Template.error(
                        "constraints",
                        "ID definition not under required headings",
                        path=art.path,
                        line=int(d.get("line", 1) or 1),
                        artifact_kind=ak,
                        id_kind=k,
                        id=str(d.get("id")),
                        headings=sorted(allowed_headings),
                        found_headings=active,
                    ))
            if not ok_any:
                errors.append(Template.error(
                    "constraints",
                    "Required headings contain no ID definitions",
                    path=art.path,
                    line=1,
                    artifact_kind=ak,
                    id_kind=k,
                    headings=sorted(allowed_headings),
                ))

    # Constraints: reference coverage rules (required|optional|prohibited)
    for ak, c in constraints_by_artifact_kind.items():
        for ic in getattr(c, "defined_id", []) or []:
            id_kind = str(getattr(ic, "kind", "")).strip().lower()
            refs_rules = getattr(ic, "references", None) or {}
            if not isinstance(refs_rules, dict):
                continue

            # Iterate definitions of this kind
            for did, rows in defs_by_id.items():
                for drow in rows:
                    if str(drow.get("artifact_kind")) != ak:
                        continue
                    if str(drow.get("id_kind") or "").lower() != id_kind:
                        continue
                    system = drow.get("system")
                    if system is None:
                        continue

                    system_present_kinds = present_kinds_by_system.get(system, set())
                    system_refs_by_kind = refs_by_system_kind.get(system, {})

                    for target_kind, rule in refs_rules.items():
                        tk = str(target_kind).strip().upper()
                        cov = str(getattr(rule, "coverage", "optional")).strip().lower()
                        allowed_headings = set([h.strip() for h in (getattr(rule, "headings", None) or []) if isinstance(h, str) and h.strip()])

                        refs_in_kind = [r for r in system_refs_by_kind.get(tk, []) if str(r.get("id")) == did]

                        if cov == "required":
                            if tk not in system_present_kinds:
                                warnings.append(Template.error(
                                    "constraints",
                                    "Required reference target kind not in scope",
                                    path=drow.get("artifact_path"),
                                    line=int(drow.get("line", 1) or 1),
                                    id=did,
                                    artifact_kind=ak,
                                    target_kind=tk,
                                ))
                                continue
                            if not refs_in_kind:
                                errors.append(Template.error(
                                    "constraints",
                                    "ID not referenced from required artifact kind",
                                    path=drow.get("artifact_path"),
                                    line=int(drow.get("line", 1) or 1),
                                    id=did,
                                    artifact_kind=ak,
                                    target_kind=tk,
                                ))
                                continue

                        if cov == "prohibited" and refs_in_kind:
                            first = refs_in_kind[0]
                            errors.append(Template.error(
                                "constraints",
                                "ID referenced from prohibited artifact kind",
                                path=first.get("artifact_path"),
                                line=int(first.get("line", 1) or 1),
                                id=did,
                                artifact_kind=ak,
                                target_kind=tk,
                            ))
                            continue

                        if allowed_headings and refs_in_kind:
                            ok_any = False
                            for rr in refs_in_kind:
                                active = rr.get("headings") or []
                                ok = any(h in allowed_headings for h in active)
                                if ok:
                                    ok_any = True
                                else:
                                    errors.append(Template.error(
                                        "constraints",
                                        "ID reference not under required headings",
                                        path=rr.get("artifact_path"),
                                        line=int(rr.get("line", 1) or 1),
                                        id=did,
                                        artifact_kind=ak,
                                        target_kind=tk,
                                        headings=sorted(allowed_headings),
                                        found_headings=active,
                                    ))
                            if cov == "required" and not ok_any:
                                errors.append(Template.error(
                                    "constraints",
                                    "Required headings contain no ID references",
                                    path=drow.get("artifact_path"),
                                    line=int(drow.get("line", 1) or 1),
                                    id=did,
                                    artifact_kind=ak,
                                    target_kind=tk,
                                    headings=sorted(allowed_headings),
                                ))

    # Note: References decide their own has= attributes (task, priority).
    # A reference without has="task" is valid even if the definition has it.
    # This allows flexible cross-artifact references where downstream artifacts
    # may not need to track task status for upstream IDs.

    return {"errors": errors, "warnings": warnings}


def parse_cpt(
    cpt: str,
    expected_kind: str,
    registered_systems: Iterable[str],
    where_defined: Optional[callable] = None,
    known_kinds: Optional[Iterable[str]] = None,
) -> Optional[ParsedCypilotId]:
    """Parse an Cypilot ID and extract system, kind, slug, and optional prefix_id.

    Algorithm:
    1. Check cpt- prefix (case-insensitive)
    2. Find system by matching registered systems as prefix (longest match wins, case-insensitive)
    3. Extract first kind after system
    4. Validate kind against known_kinds if provided
    5. If first kind matches expected_kind → simple ID
    6. Otherwise, look for composite ID by finding `-{expected_kind}-` separator
    7. For composite IDs, validate that parent (left part) exists via where_defined

    Args:
        cpt: The Cypilot ID string to parse (e.g., "cpt-myapp-spec-auth-algo-hash")
        expected_kind: The kind we're looking for (e.g., "algo")
        registered_systems: Set/list of known system names (e.g., {"myapp", "account-server"})
        where_defined: Optional callable(id) -> bool to check if parent ID exists
        known_kinds: Optional set/list of known kind identifiers (e.g., {"spec", "algo", "fr"}).
            If provided, the kind in the ID is validated against this set.

    Returns:
        ParsedCypilotId with system, kind, slug, and optional prefix_id; or None if not parseable

    Examples:
        >>> parse_cpt("cpt-myapp-spec-auth", "spec", {"myapp"})
        ParsedCypilotId(system="myapp", kind="spec", slug="auth", prefix_id=None)

        >>> parse_cpt("cpt-myapp-spec-auth-algo-hash", "algo", {"myapp"}, lambda x: x == "cpt-myapp-spec-auth")
        ParsedCypilotId(system="myapp", kind="algo", slug="hash", prefix_id="cpt-myapp-spec-auth")

        >>> parse_cpt("cpt-myapp-spec-auth", "spec", {"myapp"}, known_kinds={"spec", "algo"})
        ParsedCypilotId(system="myapp", kind="spec", slug="auth", prefix_id=None)
    """
    if not cpt or not cpt.lower().startswith("cpt-"):
        return None

    # Convert to set for O(1) membership checks
    systems_set = set(registered_systems) if not isinstance(registered_systems, set) else registered_systems

    # Convert known_kinds to lowercase set (if provided)
    kinds_set: Optional[set] = None
    if known_kinds is not None:
        kinds_set = {k.lower() for k in known_kinds}

    # 1. Find system by checking each registered system as prefix (case-insensitive)
    # Use longest match to handle multi-word systems like "account-server"
    system: Optional[str] = None
    for sys in systems_set:
        prefix = f"cpt-{sys}-"
        if cpt.lower().startswith(prefix.lower()):
            if system is None or len(sys) > len(system):
                system = sys

    if system is None:
        return None  # unknown system — not a recognized Cypilot ID

    # 2. Remove prefix, get remainder
    prefix_len = len(f"cpt-{system}-")
    remainder = cpt[prefix_len:]

    if not remainder:
        return None  # no kind/slug after system

    # 3. Extract first kind
    parts = remainder.split("-", 1)
    first_kind = parts[0]

    # 4. Validate first_kind against known_kinds (if provided)
    if kinds_set is not None and first_kind.lower() not in kinds_set:
        return None  # unknown kind

    # 5. If first_kind == expected_kind → simple ID
    if first_kind.lower() == expected_kind.lower():
        slug = parts[1] if len(parts) > 1 else ""
        return ParsedCypilotId(system=system, kind=expected_kind, slug=slug, prefix_id=None)

    # 6. Composite ID — look for `-{expected_kind}-` separator
    # Also validate expected_kind is known (if known_kinds provided)
    if kinds_set is not None and expected_kind.lower() not in kinds_set:
        return None  # expected kind is not valid

    separator = f"-{expected_kind}-"
    cpt_lower = cpt.lower()
    separator_lower = separator.lower()

    if separator_lower not in cpt_lower:
        return None  # expected kind not found

    idx = cpt_lower.index(separator_lower)
    left = cpt[:idx]  # parent ID (preserve original case)
    slug = cpt[idx + len(separator):]  # everything after separator

    # 7. Validate parent exists (if where_defined provided)
    if where_defined is not None and not where_defined(left):
        return None  # parent doesn't exist

    return ParsedCypilotId(system=system, kind=expected_kind, slug=slug, prefix_id=left)


def load_template(template_path: Path) -> Tuple[Optional[Template], List[Dict[str, object]]]:
    """Convenience wrapper returning (Template|None, errors)."""
    tmpl = Template(template_path)
    errs = tmpl.load()
    if errs:
        return None, errs
    return tmpl, []


def validate_artifact_file_against_template(
    artifact_path: Path,
    template_path: Path,
    expected_kind: Optional[str] = None,
) -> Dict[str, List[Dict[str, object]]]:
    """Validate artifact file against template (backward-compatible wrapper).

    Args:
        artifact_path: Path to the artifact file to validate
        template_path: Path to the template file
        expected_kind: Optional expected kind to check against template kind

    Returns:
        Dict with "errors" and "warnings" lists
    """
    tmpl, errs = load_template(template_path)
    if errs or tmpl is None:
        return {
            "errors": errs or [{"type": "template", "message": "Failed to load template", "path": str(template_path), "line": 1}],
            "warnings": [],
        }

    if expected_kind and tmpl.kind != expected_kind:
        return {
            "errors": [{"type": "kind", "message": f"Kind mismatch: expected {expected_kind}, got {tmpl.kind}", "path": str(artifact_path), "line": 1}],
            "warnings": [],
        }

    return tmpl.validate(artifact_path)


__all__ = [
    "Template",
    "Artifact",
    "ParsedCypilotId",
    "apply_kind_constraints",
    "load_template",
    "validate_artifact_file_against_template",
    "cross_validate_artifacts",
    "parse_cpt",
]
