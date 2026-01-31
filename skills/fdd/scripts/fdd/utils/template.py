"""Template and artifact parsing/validation per templates/SPEC.md (marker-based).

This module provides a deterministic, stdlib-only parser that can be reused by
CLI, cascade validation, and search utilities. It parses templates (paired fdd
markers), produces an object model, parses artifacts against templates, and
validates structure/content including FDL blocks.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

SUPPORTED_VERSION = {"major": 1, "minor": 0}

_MARKER_RE = re.compile(r"<!--\s*fdd:(?:(?P<type>[^:\s>]+):)?(?P<name>[^>\s]+)(?P<attrs>[^>]*)-->")
_ATTR_RE = re.compile(r'([a-zA-Z0-9_-]+)\s*=\s*"([^"]*)"')
_ID_DEF_RE = re.compile(r"^\*\*ID\*\*:\s*(?:(?P<task>\[\s*[xX]?\s*\])\s*(?:`(?P<priority>p\d+)`\s*-\s*|\-\s*)|`(?P<priority_only>p\d+)`\s*-\s*)?`(?P<id>fdd-[a-z0-9][a-z0-9-]+)`\s*$")
_ID_REF_RE = re.compile(r"^(?:(?P<task>\[\s*[xX]?\s*\])\s*(?:`(?P<priority>p\d+)`\s*-\s*|\-\s*)|`(?P<priority_only>p\d+)`\s*-\s*)?`(?P<id>fdd-[a-z0-9][a-z0-9-]+)`\s*$")
_BACKTICK_ID_RE = re.compile(r"`(fdd-[a-z0-9][a-z0-9-]+)`")
_HEADING_RE = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*$")
_ORDERED_NUMERIC_RE = re.compile(r"^\s*\d+[\.)]\s+")
_CODE_FENCE_RE = re.compile(r"^\s*```")
_FDL_LINE_RE = re.compile(r"^\s*(?:\d+\.\s+|-\s+)\[\s*[xX ]\s*\]\s*-\s*`ph-\d+`\s*-\s*.+\s*-\s*`inst-[a-z0-9-]+`\s*$")


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
    policy: Optional[TemplatePolicy] = None
    blocks: List[TemplateBlock] = None  # populated on load()
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

        try:
            fm, _fm_end = Template.parse_frontmatter_yaml(text)
        except Exception as e:
            return [Template.error("template", f"Invalid template frontmatter: {e}", path=self.path, line=1)]
        if not isinstance(fm, dict) or "fdd-template" not in fm:
            return [Template.error("template", "Missing required fdd-template frontmatter", path=self.path, line=1)]
        ft = fm.get("fdd-template")
        if not isinstance(ft, dict):
            return [Template.error("template", "Invalid fdd-template frontmatter", path=self.path, line=1)]

        kind = ft.get("kind")
        ver = ft.get("version")
        unknown_sections = ft.get("unknown_sections", "warn")
        if not isinstance(kind, str) or not kind.strip():
            return [Template.error("template", "Template frontmatter missing 'kind'", path=self.path, line=1)]
        if not isinstance(ver, dict) or not isinstance(ver.get("major"), int) or not isinstance(ver.get("minor"), int):
            return [Template.error("template", "Template frontmatter missing version.major/minor", path=self.path, line=1)]
        if unknown_sections not in {"error", "warn", "allow"}:
            return [Template.error("template", "Invalid unknown_sections value", path=self.path, line=1)]

        template_version = TemplateVersion(int(ver["major"]), int(ver["minor"]))
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
        """Parse paired fdd markers into TemplateBlock objects with spans and attrs."""
        blocks: List[TemplateBlock] = []
        errors: List[Dict[str, object]] = []
        stack: List[Tuple[str, str, Dict[str, str], int]] = []
        for idx0, line in enumerate(lines):
            line_no = idx0 + 1
            for m in _MARKER_RE.finditer(line):
                m_type = m.group("type") or "free"
                name = m.group("name")
                attrs = Template.parse_attrs(m.group("attrs") or "")
                if stack and stack[-1][0] == m_type and stack[-1][1] == name:
                    open_type, open_name, open_attrs, open_line = stack.pop()
                    req_val = str(open_attrs.get("required", "true")).strip().lower()
                    rep_val = str(open_attrs.get("repeat", "one")).strip().lower() or "one"
                    required = req_val != "false"
                    if rep_val not in {"one", "many"}:
                        errors.append(Template.error("template", "Invalid repeat", line=open_line, id=open_name, marker_type=open_type))
                        rep_val = "one"
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
            for line in content:
                if not _ID_DEF_RE.match(line.strip()):
                    errors.append(Template.error("structure", "Invalid ID format", path=artifact_path, line=inst.start_line, id=tpl.name))
                    return
                if require_priority and "`p" not in line:
                    errors.append(Template.error("structure", "ID definition missing priority", path=artifact_path, line=inst.start_line, id=tpl.name))
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
                for part in [p.strip() for p in line.split(",")]:
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
        if tpl.type == "fdl":
            if not content or not first:
                errors.append(Template.error("structure", "FDL block empty", path=artifact_path, line=inst.start_line, id=tpl.name))
                return
            for line in content:
                if not line.strip():
                    continue
                if not _FDL_LINE_RE.match(line):
                    errors.append(Template.error("structure", "Invalid FDL line", path=artifact_path, line=inst.start_line, id=tpl.name, value=line.strip()))
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
    artifact_kind: str
    to_code: bool = False  # from template attr to_code="true"


@dataclass
class IdReference:
    id: str
    line: int
    checked: bool
    priority: Optional[str]
    block: ArtifactBlock
    artifact_path: Path
    artifact_kind: str


@dataclass
class ArtifactBlock:
    template_block: TemplateBlock
    content: List[str]
    start_line: int
    end_line: int

    def text(self) -> str:
        return "\n".join(self.content).strip()


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

    @classmethod
    def from_template(cls, template: Template, artifact_path: Path) -> "Artifact":
        art = cls(template, artifact_path, [], [])
        art.load()
        return art

    def load(self) -> None:
        """Parse artifact markers into blocks; accumulate structural errors."""
        if self.blocks:
            return
        try:
            text = self.path.read_text(encoding="utf-8")
        except Exception:
            self._errors.append(Template.error("file", "Failed to read artifact", path=self.path, line=1))
            return

        lines = text.splitlines()
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

        # Extract IDs/refs/tasks for status cross-checks inside artifact
        self._extract_ids_and_refs()
        self._validate_id_task_statuses(errors)

        if self.template.policy.unknown_sections != "allow":
            for key, inst_list in art_by_key.items():
                if key not in tpl_by_key:
                    msg = Template.error("structure", "Unknown marker", path=self.path, line=inst_list[0].start_line, marker_type=key[0], id=key[1])
                    if self.template.policy.unknown_sections == "error":
                        errors.append(msg)
                    else:
                        warnings.append(msg)

        return {"errors": errors, "warnings": warnings}

    def _extract_ids_and_refs(self) -> None:
        if self.id_definitions or self.id_references:
            return
        for blk in self.blocks:
            if blk.template_block.type == "id":
                to_code = str(blk.template_block.attrs.get("to_code", "false")).strip().lower() == "true"
                for rel_idx, line in enumerate(blk.content, start=0):
                    m = _ID_DEF_RE.match(line.strip())
                    if not m:
                        continue
                    checked = (m.group("task") or "").lower().find("x") != -1
                    priority = m.group("priority") or m.group("priority_only")
                    self.id_definitions.append(
                        IdDefinition(
                            id=m.group("id"),
                            line=blk.start_line + rel_idx,
                            checked=checked,
                            priority=priority,
                            block=blk,
                            artifact_path=self.path,
                            artifact_kind=self.template.kind,
                            to_code=to_code,
                        )
                    )
            if blk.template_block.type == "id-ref":
                for rel_idx, line in enumerate(blk.content, start=0):
                    m = _ID_REF_RE.match(line.strip())
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
                            artifact_kind=self.template.kind,
                        )
                    )
            else:
                # generic backticked refs anywhere
                for rel_idx, line in enumerate(blk.content, start=0):
                    for mm in _BACKTICK_ID_RE.finditer(line):
                        self.id_references.append(
                            IdReference(
                                id=mm.group(1),
                                line=blk.start_line + rel_idx,
                                checked=False,
                                priority=None,
                                block=blk,
                                artifact_path=self.path,
                                artifact_kind=self.template.kind,
                            )
                        )
            if blk.template_block.type == "task-list":
                for rel_idx, line in enumerate(blk.content, start=0):
                    line_stripped = line.strip()
                    if not line_stripped or not line_stripped.startswith("- ["):
                        continue
                    checked = "[x" in line_stripped.lower()
                    self.task_statuses.append((checked, blk))
            if blk.template_block.type == "fdl":
                for rel_idx, line in enumerate(blk.content, start=0):
                    if not line.strip():
                        continue
                    if _FDL_LINE_RE.match(line):
                        checked = "[x" in line.lower()
                        self.task_statuses.append((checked, blk))

    def _validate_id_task_statuses(self, errors: List[Dict[str, object]]):
        """Enforce task completion consistency between tasks and ID definitions."""
        if not self.id_definitions:
            return
        all_tasks = self.task_statuses
        if not all_tasks:
            return
        all_done = all(checked for checked, _ in all_tasks)
        for d in self.id_definitions:
            has_task_attr = "task" in (d.block.template_block.attrs.get("has", "") or "")
            if not has_task_attr:
                continue
            if all_done and not d.checked:
                errors.append(Template.error("structure", "All tasks done but ID not marked done", path=self.path, line=d.line, id=d.id))
            if not all_done and d.checked:
                errors.append(Template.error("structure", "ID marked done but tasks not all done", path=self.path, line=d.line, id=d.id))


def cross_validate_artifacts(artifacts: Sequence[Artifact]) -> Dict[str, List[Dict[str, object]]]:
    """Cross-artifact validation: covered_by presence and refs to defs.

    - For each ID definition with covered_by attr: ensure at least one reference exists
      in artifacts whose template.kind is in covered_by list.
    - For each reference: ensure a definition exists somewhere.
    - For task sync across refs: if a ref is checked and refers to a definable ID with task,
      ensure corresponding definition is checked.
    """
    errors: List[Dict[str, object]] = []
    warnings: List[Dict[str, object]] = []

    id_defs: Dict[str, List[IdDefinition]] = {}
    id_refs: List[IdReference] = []
    defs_by_kind: Dict[str, List[IdDefinition]] = {}
    refs_by_kind: Dict[str, List[IdReference]] = {}

    for art in artifacts:
        art._extract_ids_and_refs()
        for d in art.id_definitions:
            id_defs.setdefault(d.id, []).append(d)
            defs_by_kind.setdefault(art.template.kind, []).append(d)
        for r in art.id_references:
            id_refs.append(r)
            refs_by_kind.setdefault(art.template.kind, []).append(r)

    # covered_by check
    for art in artifacts:
        for blk in art.blocks:
            if blk.template_block.type != "id":
                continue
            covered = blk.template_block.attrs.get("covered_by", "").strip()
            if not covered:
                continue
            target_kinds = [c.strip() for c in covered.split(",") if c.strip()]
            if not target_kinds:
                continue
            # find ids defined in this block
            for d in art.id_definitions:
                if d.block is not blk:
                    continue
                found = False
                for tk in target_kinds:
                    refs_in_kind = refs_by_kind.get(tk, [])
                    if any(r.id == d.id for r in refs_in_kind):
                        found = True
                        break
                if not found:
                    errors.append(Template.error("structure", "ID not covered by required artifact kinds", path=art.path, line=d.line, id=d.id, covered_by=target_kinds))

    # refs must have definitions
    for r in id_refs:
        if r.id not in id_defs:
            errors.append(Template.error("structure", "Reference has no definition", path=r.artifact_path, line=r.line, id=r.id))

    # checked ref implies checked def (if def has task)
    for r in id_refs:
        if not r.checked:
            continue
        defs = id_defs.get(r.id, [])
        if not defs:
            continue
        for d in defs:
            if d.checked:
                continue
            errors.append(Template.error("structure", "Reference marked done but definition not done", path=r.artifact_path, line=r.line, id=r.id))

    return {"errors": errors, "warnings": warnings}


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
    "load_template",
    "validate_artifact_file_against_template",
    "cross_validate_artifacts",
]
