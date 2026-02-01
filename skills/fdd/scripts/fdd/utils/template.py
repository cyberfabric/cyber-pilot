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
_ID_DEF_RE = re.compile(
    r"^(?:"
    r"\*\*ID\*\*:\s*`(?P<id>fdd-[a-z0-9][a-z0-9-]+)`"
    r"|"
    r"`(?P<priority_only>p\d+)`\s*-\s*\*\*ID\*\*:\s*`(?P<id2>fdd-[a-z0-9][a-z0-9-]+)`"
    r"|"
    r"[-*]\s+(?P<task>\[\s*[xX]?\s*\])\s*(?:`(?P<priority>p\d+)`\s*-\s*)?\*\*ID\*\*:\s*`(?P<id3>fdd-[a-z0-9][a-z0-9-]+)`"
    r")\s*$"
)
_ID_LABEL_RE = re.compile(r"\*\*ID\*\*:")
_ID_REF_RE = re.compile(r"^(?:(?P<task>\[\s*[xX]?\s*\])\s*(?:`(?P<priority>p\d+)`\s*-\s*|\-\s*)|`(?P<priority_only>p\d+)`\s*-\s*)?`(?P<id>fdd-[a-z0-9][a-z0-9-]+)`\s*$")
_BACKTICK_ID_RE = re.compile(r"`(fdd-[a-z0-9][a-z0-9-]+)`")
_HEADING_RE = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*$")
_ORDERED_NUMERIC_RE = re.compile(r"^\s*\d+[\.)]\s+")
_CODE_FENCE_RE = re.compile(r"^\s*```")
_FDL_LINE_RE = re.compile(r"^\s*(?:\d+\.\s+|-\s+)\[\s*[xX ]\s*\]\s*-\s*`p[a-z0-9-]+`\s*-\s*.+\s*-\s*`inst-[a-z0-9-]+`\s*$")

# Valid marker types (must match validate_block_content handlers)
VALID_MARKER_TYPES = frozenset({
    "free", "id", "id-ref",
    "list", "numbered-list", "task-list",
    "table", "paragraph", "code",
    "#", "##", "###", "####", "#####", "######",
    "link", "image", "fdl",
})


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
class ParsedFddId:
    """Result of parsing an FDD ID."""
    system: str
    kind: str
    slug: str
    prefix_id: Optional[str] = None  # for composite IDs like fdd-sys-feature-x-algo-y


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

        # Detect template frontmatter in artifact (should only be in templates, not artifacts)
        lines = text.splitlines()
        if lines and lines[0].strip() == "---":
            for i, ln in enumerate(lines[1:], start=2):
                if ln.strip() == "---":
                    break
                if "fdd-template:" in ln:
                    self._errors.append(Template.error(
                        "structure",
                        "Artifact contains template frontmatter (fdd-template:) - this belongs only in template files, not artifacts",
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

        # Unknown markers are always errors (markers in artifact not defined in template)
        for key, inst_list in art_by_key.items():
            if key not in tpl_by_key:
                errors.append(Template.error("structure", "Unknown marker", path=self.path, line=inst_list[0].start_line, marker_type=key[0], id=key[1]))

        return {"errors": errors, "warnings": warnings}

    def _extract_ids_and_refs(self) -> None:
        if self.id_definitions or self.id_references:
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
                            artifact_kind=self.template.kind,
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
                            artifact_kind=self.template.kind,
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
        """Enforce task completion consistency between tasks and ID definitions.

        For each ID definition with has="task", find all tasks within that ID block's
        line range and validate that their completion status is consistent with the ID's status.

        Also enforces cascade logic for nested ID definitions (e.g., id:status → id:feature in FEATURES).
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
            # E.g., id:status contains id:feature blocks in FEATURES manifest
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


def cross_validate_artifacts(
    artifacts: Sequence[Artifact],
    registered_systems: Optional[Iterable[str]] = None,
    known_kinds: Optional[Iterable[str]] = None,
) -> Dict[str, List[Dict[str, object]]]:
    """Cross-artifact validation: covered_by presence and refs to defs.

    Args:
        artifacts: Sequence of parsed Artifact objects to validate
        registered_systems: Set of known system names from artifacts.json.
            If provided, references to unknown systems are treated as external
            and not flagged as errors.
        known_kinds: Set of known kind identifiers from templates (e.g., {"feature", "algo", "fr"}).
            Used for validating ID structure and kind existence.

    Validates:
    - For each ID definition with covered_by attr: ensure at least one reference exists
      in artifacts whose template.kind is in covered_by list.
    - For each reference: ensure a definition exists somewhere (unless external system).
    - For task sync across refs: if a ref is checked and refers to a definable ID with task,
      ensure corresponding definition is checked.
    """
    errors: List[Dict[str, object]] = []
    warnings: List[Dict[str, object]] = []

    # Normalize known_kinds to lowercase set (if provided)
    kinds_set: Optional[set] = None
    if known_kinds is not None:
        kinds_set = {k.lower() for k in known_kinds}

    id_defs: Dict[str, List[IdDefinition]] = {}
    id_refs: List[IdReference] = []
    defs_by_kind: Dict[str, List[IdDefinition]] = {}
    refs_by_kind: Dict[str, List[IdReference]] = {}

    present_kinds: set[str] = set()
    for art in artifacts:
        art._extract_ids_and_refs()
        kind = art.template.kind
        present_kinds.add(kind)
        for d in art.id_definitions:
            id_defs.setdefault(d.id, []).append(d)
            defs_by_kind.setdefault(kind, []).append(d)
        for r in art.id_references:
            id_refs.append(r)
            refs_by_kind.setdefault(kind, []).append(r)

    # covered_by check (case-sensitive kind matching)
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
            # Check if any target kind is present in validation scope
            kinds_in_scope = [tk for tk in target_kinds if tk in present_kinds]
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
                    # If no target artifacts exist in scope, warn instead of error
                    if not kinds_in_scope:
                        warnings.append(Template.error("structure", "ID not covered (target artifact kinds not in scope)", path=art.path, line=d.line, id=d.id, covered_by=target_kinds))
                    else:
                        errors.append(Template.error("structure", "ID not covered by required artifact kinds", path=art.path, line=d.line, id=d.id, covered_by=target_kinds))

    # Normalize registered_systems to lowercase set for matching
    systems_set: set[str] = set()
    if registered_systems is not None:
        systems_set = {s.lower() for s in registered_systems}

    # Helper to check if a reference's system is registered
    def _is_external_system_ref(fdd_id: str) -> bool:
        """Check if this ID references an external (non-registered) system.

        If no registered_systems provided, we cannot determine external refs,
        so treat all as internal (will error if no definition).
        """
        if not systems_set:
            return False  # no systems known, can't distinguish external
        if not fdd_id.lower().startswith("fdd-"):
            return False
        # Try to find if any registered system matches as prefix
        for sys in systems_set:
            prefix = f"fdd-{sys}-"
            if fdd_id.lower().startswith(prefix):
                return False  # system is registered, not external
        return True  # no registered system matched → external

    # Helper to extract kind from FDD ID (first segment after system)
    def _extract_kind_from_id(fdd_id: str) -> Optional[str]:
        """Extract the kind segment from an FDD ID."""
        if not fdd_id.lower().startswith("fdd-"):
            return None
        # Find matching system (longest match)
        matched_sys: Optional[str] = None
        for sys in systems_set:
            prefix = f"fdd-{sys}-"
            if fdd_id.lower().startswith(prefix.lower()):
                if matched_sys is None or len(sys) > len(matched_sys):
                    matched_sys = sys
        if matched_sys is None:
            return None
        prefix_len = len(f"fdd-{matched_sys}-")
        remainder = fdd_id[prefix_len:]
        if not remainder:
            return None
        return remainder.split("-", 1)[0].lower()

    # Validate ID kinds against known_kinds (if provided)
    if kinds_set:
        for d in id_defs.values():
            for defn in d:
                kind = _extract_kind_from_id(defn.id)
                if kind and kind not in kinds_set:
                    warnings.append(Template.error(
                        "structure",
                        f"ID uses unknown kind '{kind}'",
                        path=defn.artifact_path,
                        line=defn.line,
                        id=defn.id,
                        unknown_kind=kind,
                    ))

    # refs must have definitions (but only error if system is registered)
    for r in id_refs:
        if r.id not in id_defs:
            if _is_external_system_ref(r.id):
                # External system reference - not an error
                continue
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

    # Note: References decide their own has= attributes (task, priority).
    # A reference without has="task" is valid even if the definition has it.
    # This allows flexible cross-artifact references where downstream artifacts
    # may not need to track task status for upstream IDs.

    return {"errors": errors, "warnings": warnings}


def parse_fdd_id(
    fdd_id: str,
    expected_kind: str,
    registered_systems: Iterable[str],
    where_defined: Optional[callable] = None,
    known_kinds: Optional[Iterable[str]] = None,
) -> Optional[ParsedFddId]:
    """Parse an FDD ID and extract system, kind, slug, and optional prefix_id.

    Algorithm:
    1. Check fdd- prefix (case-insensitive)
    2. Find system by matching registered systems as prefix (longest match wins, case-insensitive)
    3. Extract first kind after system
    4. Validate kind against known_kinds if provided
    5. If first kind matches expected_kind → simple ID
    6. Otherwise, look for composite ID by finding `-{expected_kind}-` separator
    7. For composite IDs, validate that parent (left part) exists via where_defined

    Args:
        fdd_id: The FDD ID string to parse (e.g., "fdd-myapp-feature-auth-algo-hash")
        expected_kind: The kind we're looking for (e.g., "algo")
        registered_systems: Set/list of known system names (e.g., {"myapp", "account-server"})
        where_defined: Optional callable(id) -> bool to check if parent ID exists
        known_kinds: Optional set/list of known kind identifiers (e.g., {"feature", "algo", "fr"}).
            If provided, the kind in the ID is validated against this set.

    Returns:
        ParsedFddId with system, kind, slug, and optional prefix_id; or None if not parseable

    Examples:
        >>> parse_fdd_id("fdd-myapp-feature-auth", "feature", {"myapp"})
        ParsedFddId(system="myapp", kind="feature", slug="auth", prefix_id=None)

        >>> parse_fdd_id("fdd-myapp-feature-auth-algo-hash", "algo", {"myapp"}, lambda x: x == "fdd-myapp-feature-auth")
        ParsedFddId(system="myapp", kind="algo", slug="hash", prefix_id="fdd-myapp-feature-auth")

        >>> parse_fdd_id("fdd-myapp-feature-auth", "feature", {"myapp"}, known_kinds={"feature", "algo"})
        ParsedFddId(system="myapp", kind="feature", slug="auth", prefix_id=None)
    """
    if not fdd_id or not fdd_id.lower().startswith("fdd-"):
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
        prefix = f"fdd-{sys}-"
        if fdd_id.lower().startswith(prefix.lower()):
            if system is None or len(sys) > len(system):
                system = sys

    if system is None:
        return None  # unknown system — not a recognized FDD ID

    # 2. Remove prefix, get remainder
    prefix_len = len(f"fdd-{system}-")
    remainder = fdd_id[prefix_len:]

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
        return ParsedFddId(system=system, kind=expected_kind, slug=slug, prefix_id=None)

    # 6. Composite ID — look for `-{expected_kind}-` separator
    # Also validate expected_kind is known (if known_kinds provided)
    if kinds_set is not None and expected_kind.lower() not in kinds_set:
        return None  # expected kind is not valid

    separator = f"-{expected_kind}-"
    fdd_id_lower = fdd_id.lower()
    separator_lower = separator.lower()

    if separator_lower not in fdd_id_lower:
        return None  # expected kind not found

    idx = fdd_id_lower.index(separator_lower)
    left = fdd_id[:idx]  # parent ID (preserve original case)
    slug = fdd_id[idx + len(separator):]  # everything after separator

    # 7. Validate parent exists (if where_defined provided)
    if where_defined is not None and not where_defined(left):
        return None  # parent doesn't exist

    return ParsedFddId(system=system, kind=expected_kind, slug=slug, prefix_id=left)


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
    "ParsedFddId",
    "load_template",
    "validate_artifact_file_against_template",
    "cross_validate_artifacts",
    "parse_fdd_id",
]
