"""
Blueprint Parser and Output Generators

Parses blueprint .md files containing `@cpt:` markers and generates
kit resources (rules.md, checklist.md, template.md, example.md, constraints.toml).

Uses only Python 3.11+ stdlib.

@cpt-algo:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1
@cpt-algo:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1
@cpt-algo:cpt-cypilot-algo-blueprint-system-generate-constraints:p1
@cpt-algo:cpt-cypilot-algo-blueprint-system-process-kit:p1
@cpt-dod:cpt-cypilot-dod-blueprint-system-parsing:p1
@cpt-dod:cpt-cypilot-dod-blueprint-system-artifact-gen:p1
@cpt-dod:cpt-cypilot-dod-blueprint-system-constraints-gen:p1
@cpt-dod:cpt-cypilot-dod-blueprint-system-regenerate:p1
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Marker:
    """A parsed `@cpt:TYPE` marker from a blueprint file."""
    marker_type: str          # e.g. "blueprint", "heading", "rule", "check", ...
    raw_content: str          # full text between open/close tags
    toml_data: Dict[str, Any] = field(default_factory=dict)   # parsed TOML block (if any)
    markdown_content: str = ""    # parsed markdown block (if any)
    line_start: int = 0
    line_end: int = 0


@dataclass
class ParsedBlueprint:
    """Result of parsing a single blueprint .md file."""
    path: Path
    markers: List[Marker] = field(default_factory=list)
    artifact_kind: str = ""       # from @cpt:blueprint 'artifact' key or filename
    kit_slug: str = ""            # from @cpt:blueprint 'kit' key
    version: str = ""             # from @cpt:blueprint 'version' key
    errors: List[str] = field(default_factory=list)


# Regex for opening/closing marker tags (backtick-delimited)
_OPEN_RE = re.compile(r"^`@cpt:(\w[\w-]*)` *$")
_CLOSE_RE = re.compile(r"^`@/cpt:(\w[\w-]*)` *$")

# Regex for fenced code blocks inside marker content
_FENCE_OPEN_RE = re.compile(r"^```(\w+)\s*$")
_FENCE_CLOSE_RE = re.compile(r"^```\s*$")


# ---------------------------------------------------------------------------
# Blueprint Parser
# ---------------------------------------------------------------------------

def parse_blueprint(path: Path) -> ParsedBlueprint:
    """Parse a blueprint .md file, extracting all `@cpt:` markers.

    Args:
        path: Path to the blueprint file.

    Returns:
        ParsedBlueprint with markers, metadata, and any errors.
    """
    result = ParsedBlueprint(path=path)

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-read-file
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        result.errors.append(f"Cannot read {path}: {e}")
        return result
    # @cpt-end:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-read-file

    lines = text.splitlines()
    markers: List[Marker] = []
    i = 0

    while i < len(lines):
        # @cpt-begin:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-scan-open
        line = lines[i].strip()
        m_open = _OPEN_RE.match(line)
        if not m_open:
            i += 1
            continue
        # @cpt-end:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-scan-open

        # @cpt-begin:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-foreach-marker
        marker_type = m_open.group(1)
        open_line = i + 1  # 1-indexed
        # @cpt-end:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-foreach-marker

        # @cpt-begin:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-find-close
        j = i + 1
        found_close = False
        while j < len(lines):
            close_line_text = lines[j].strip()
            m_close = _CLOSE_RE.match(close_line_text)
            if m_close and m_close.group(1) == marker_type:
                found_close = True
                break
            j += 1
        # @cpt-end:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-find-close

        # @cpt-begin:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-if-unclosed
        if not found_close:
            result.errors.append(
                f"{path}:{open_line}: unclosed marker `@cpt:{marker_type}` — "
                f"expected `@/cpt:{marker_type}` before end of file"
            )
            i += 1
            continue
        # @cpt-end:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-if-unclosed

        # @cpt-begin:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-extract-content
        close_line = j + 1  # 1-indexed
        content_lines = lines[i + 1: j]
        raw_content = "\n".join(content_lines)
        # @cpt-end:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-extract-content

        # @cpt-begin:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-parse-metadata
        toml_data: Dict[str, Any] = {}
        markdown_content = ""
        _extract_fenced_blocks(content_lines, toml_data, marker_type, result, open_line)
        markdown_content = _extract_markdown_block(content_lines)
        # @cpt-end:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-parse-metadata

        # @cpt-begin:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-validate-flat
        marker = Marker(
            marker_type=marker_type,
            raw_content=raw_content,
            toml_data=toml_data,
            markdown_content=markdown_content,
            line_start=open_line,
            line_end=close_line,
        )
        markers.append(marker)
        i = j + 1
        # @cpt-end:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-validate-flat

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-return-parsed
    result.markers = markers

    for mk in markers:
        if mk.marker_type == "blueprint":
            result.artifact_kind = mk.toml_data.get("artifact", "")
            result.kit_slug = mk.toml_data.get("kit", "")
            result.version = mk.toml_data.get("version", "")
            break

    if not result.artifact_kind:
        result.artifact_kind = path.stem

    return result
    # @cpt-end:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-return-parsed


def _extract_fenced_blocks(
    content_lines: List[str],
    toml_data: Dict[str, Any],
    marker_type: str,
    result: ParsedBlueprint,
    marker_line: int,
) -> None:
    """Extract fenced code blocks (```toml, ```markdown) from marker content."""
    i = 0
    while i < len(content_lines):
        line = content_lines[i].strip()
        m_fence = _FENCE_OPEN_RE.match(line)
        if not m_fence:
            i += 1
            continue

        lang = m_fence.group(1).lower()
        j = i + 1
        while j < len(content_lines):
            if _FENCE_CLOSE_RE.match(content_lines[j].strip()):
                break
            j += 1

        if j >= len(content_lines):
            result.errors.append(
                f"{result.path}:{marker_line}: unclosed fenced block "
                f"(```{lang}) inside `@cpt:{marker_type}`"
            )
            i += 1
            continue

        block_text = "\n".join(content_lines[i + 1: j])

        if lang == "toml" and not toml_data:
            try:
                import tomllib
                parsed = tomllib.loads(block_text)
                toml_data.update(parsed)
            except Exception as e:
                result.errors.append(
                    f"{result.path}:{marker_line}: invalid TOML in "
                    f"`@cpt:{marker_type}`: {e}"
                )

        i = j + 1


def _extract_markdown_block(content_lines: List[str]) -> str:
    """Extract the first ```markdown fenced block from content lines."""
    i = 0
    while i < len(content_lines):
        line = content_lines[i].strip()
        m_fence = _FENCE_OPEN_RE.match(line)
        if m_fence and m_fence.group(1).lower() == "markdown":
            j = i + 1
            while j < len(content_lines):
                if _FENCE_CLOSE_RE.match(content_lines[j].strip()):
                    return "\n".join(content_lines[i + 1: j])
                j += 1
        i += 1
    return ""



# ---------------------------------------------------------------------------
# Per-Artifact Output Generators
# ---------------------------------------------------------------------------

def generate_artifact_outputs(
    bp: ParsedBlueprint,
    output_dir: Path,
    *,
    dry_run: bool = False,
) -> Tuple[List[str], List[str]]:
    """Generate per-artifact output files from a parsed blueprint.

    Args:
        bp: Parsed blueprint.
        output_dir: Directory to write outputs (e.g. config/kits/{slug}/artifacts/{KIND}/).
        dry_run: If True, don't write files.

    Returns:
        (written_paths, errors) tuple.
    """
    written: List[str] = []
    errors: List[str] = []

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-if-codebase
    is_codebase = not bp.artifact_kind or not any(
        m.marker_type == "blueprint" and m.toml_data.get("artifact")
        for m in bp.markers
    )
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-if-codebase

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-gen-codebase
    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-mkdir-output
    if is_codebase:
        target_dir = output_dir / "codebase"
    else:
        target_dir = output_dir

    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-mkdir-output
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-gen-codebase

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-gen-rules
    rules_content = _collect_rules(bp)
    if rules_content:
        p = target_dir / "rules.md"
        if not dry_run:
            p.write_text(rules_content, encoding="utf-8")
        written.append(p.as_posix())
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-gen-rules

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-gen-checklist
    checklist_content = _collect_checklist(bp)
    if checklist_content:
        p = target_dir / "checklist.md"
        if not dry_run:
            p.write_text(checklist_content, encoding="utf-8")
        written.append(p.as_posix())
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-gen-checklist

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-write-outputs
    if not is_codebase:
        # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-gen-template
        template_content = _collect_template(bp)
        if template_content:
            p = target_dir / "template.md"
            if not dry_run:
                p.write_text(template_content, encoding="utf-8")
            written.append(p.as_posix())
        # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-gen-template

        # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-gen-example
        example_content = _collect_example(bp)
        if example_content:
            examples_dir = target_dir / "examples"
            if not dry_run:
                examples_dir.mkdir(parents=True, exist_ok=True)
            p = examples_dir / "example.md"
            if not dry_run:
                p.write_text(example_content, encoding="utf-8")
            written.append(p.as_posix())
        # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-gen-example
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-write-outputs

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-return-outputs
    return written, errors
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-artifact-outputs:p1:inst-return-outputs


def _collect_rules(bp: ParsedBlueprint) -> str:
    """Collect rules content from @cpt:rules and @cpt:rule markers."""
    sections: List[str] = []

    for mk in bp.markers:
        if mk.marker_type == "rules":
            # Main rules block — use markdown content or raw
            content = mk.markdown_content or mk.raw_content.strip()
            if content:
                sections.append(content)
        elif mk.marker_type == "rule":
            content = mk.markdown_content or mk.raw_content.strip()
            if content:
                sections.append(content)

    if not sections:
        return ""
    return "\n\n".join(sections) + "\n"


def _collect_checklist(bp: ParsedBlueprint) -> str:
    """Collect checklist content from @cpt:checklist and @cpt:check markers."""
    sections: List[str] = []

    for mk in bp.markers:
        if mk.marker_type == "checklist":
            content = mk.markdown_content or mk.raw_content.strip()
            if content:
                sections.append(content)
        elif mk.marker_type == "check":
            content = mk.markdown_content or mk.raw_content.strip()
            if content:
                sections.append(content)

    if not sections:
        return ""
    return "\n\n".join(sections) + "\n"


def _collect_template(bp: ParsedBlueprint) -> str:
    """Build template.md from @cpt:heading markers.

    Uses the 'template' key (with placeholder syntax) from heading TOML.
    Falls back to 'pattern' when 'template' is empty (if pattern is not a regex).
    Preserves @cpt:prompt content as writing instructions under headings.
    Strips metadata markers from template output.
    """
    parts: List[str] = []

    heading_markers = [m for m in bp.markers if m.marker_type == "heading"]
    prompt_markers = [m for m in bp.markers if m.marker_type == "prompt"]

    # Section counters for numbered headings: level → counter
    section_counters: Dict[int, int] = {}
    last_numbered_level = 0

    for idx, hm in enumerate(heading_markers):
        td = hm.toml_data
        level = int(td.get("level", 2))
        template_text = td.get("template", "")
        pattern = td.get("pattern", "")
        numbered = td.get("numbered", False)

        # Determine heading text: template > pattern (if not regex)
        heading_text = template_text
        if not heading_text and pattern:
            # Strip trailing glob-style * (means "optional suffix" in heading matching)
            clean_pattern = pattern.rstrip("*").rstrip()
            # Skip actual regex patterns (backslash sequences, char classes, anchors)
            if clean_pattern and not re.search(r"[\\{}\[\]|^$]|[+?]", clean_pattern):
                heading_text = clean_pattern

        if not heading_text:
            continue

        # Build section number for numbered headings
        section_num = ""
        if numbered:
            # Reset deeper counters when a new section at this level starts
            for lv in list(section_counters.keys()):
                if lv > level:
                    del section_counters[lv]
            section_counters[level] = section_counters.get(level, 0) + 1
            # Build hierarchical number (e.g., "1", "1.1", "1.1.1")
            num_parts = []
            for lv in sorted(section_counters.keys()):
                if lv <= level:
                    num_parts.append(str(section_counters[lv]))
            section_num = ".".join(num_parts)
            last_numbered_level = level

        prefix = "#" * level
        if section_num:
            parts.append(f"{prefix} {section_num} {heading_text}")
        else:
            parts.append(f"{prefix} {heading_text}")

        # Find prompts between this heading's end and the next heading's start
        next_heading_start = (
            heading_markers[idx + 1].line_start
            if idx + 1 < len(heading_markers)
            else float("inf")
        )
        for pm in prompt_markers:
            if hm.line_end < pm.line_start < next_heading_start:
                prompt_text = pm.markdown_content or pm.raw_content.strip()
                if prompt_text:
                    parts.append("")
                    parts.append(prompt_text)

        parts.append("")

    if not parts:
        return ""
    return "\n".join(parts) + "\n"


def _collect_example(bp: ParsedBlueprint) -> str:
    """Build example.md from @cpt:heading 'examples' arrays and @cpt:example blocks.

    Per spec: headings use the first entry from the 'examples' array
    (already formatted with # prefix), then @cpt:example content follows.
    """
    parts: List[str] = []

    heading_markers = [m for m in bp.markers if m.marker_type == "heading"]
    example_markers = [m for m in bp.markers if m.marker_type == "example"]

    for idx, hm in enumerate(heading_markers):
        td = hm.toml_data
        examples = td.get("examples", [])

        # Use the first example entry as the heading line (already has # prefix)
        heading_line = ""
        if examples and isinstance(examples, list) and len(examples) > 0:
            heading_line = str(examples[0])

        # Find example blocks between this heading and the next
        next_heading_start = (
            heading_markers[idx + 1].line_start
            if idx + 1 < len(heading_markers)
            else float("inf")
        )
        section_examples: List[str] = []
        for em in example_markers:
            if hm.line_end < em.line_start < next_heading_start:
                content = em.markdown_content or em.raw_content.strip()
                if content:
                    section_examples.append(content)

        # Only emit heading + content if there's example content
        if section_examples:
            if heading_line:
                parts.append(heading_line)
                parts.append("")
            parts.extend(section_examples)
            parts.append("")
        elif heading_line:
            # Heading example without body content — still emit for structure
            parts.append(heading_line)
            parts.append("")

    if not parts:
        return ""
    return "\n".join(parts) + "\n"



# ---------------------------------------------------------------------------
# Kit-Wide Constraints Generator
# ---------------------------------------------------------------------------

def generate_constraints(
    blueprints: List[ParsedBlueprint],
    output_path: Path,
    *,
    dry_run: bool = False,
) -> Tuple[Optional[str], List[str]]:
    """Generate kit-wide constraints.toml from all blueprints.

    Args:
        blueprints: List of parsed blueprints for a kit.
        output_path: Path to write constraints.toml.
        dry_run: If True, don't write file.

    Returns:
        (written_path or None, errors) tuple.
    """
    errors: List[str] = []

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-init-constraints
    id_kinds: Dict[str, Dict[str, Any]] = {}
    headings: Dict[str, List[Dict[str, Any]]] = {}
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-init-constraints

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-foreach-bp-constraints
    for bp in blueprints:
        # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-extract-kind-constraint
        kind = bp.artifact_kind.upper() if bp.artifact_kind else ""
        # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-extract-kind-constraint

        for mk in bp.markers:
            # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-foreach-heading
            if mk.marker_type == "heading":
                td = mk.toml_data
                pattern = td.get("pattern", "")
                # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-add-heading-pattern
                if pattern and kind:
                    headings.setdefault(kind, []).append({
                        "title": td.get("title", ""),
                        "pattern": pattern,
                        "required": td.get("required", False),
                    })
                # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-add-heading-pattern
            # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-foreach-heading

            # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-foreach-id
            elif mk.marker_type == "id":
                td = mk.toml_data
                id_name = td.get("name", td.get("kind", ""))
                if id_name:
                    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-extract-id-kind
                    id_entry: Dict[str, Any] = {
                        "to_code": td.get("to_code", False),
                    }
                    defined_in = td.get("defined_in", [])
                    referenced_in = td.get("referenced_in", [])
                    if defined_in:
                        id_entry["defined_in"] = defined_in
                    if referenced_in:
                        id_entry["referenced_in"] = referenced_in
                    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-extract-id-kind

                    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-add-id-kind
                    if id_name in id_kinds:
                        existing = id_kinds[id_name]
                        for key in ("defined_in", "referenced_in"):
                            if key in id_entry:
                                old = existing.get(key, [])
                                new = id_entry[key]
                                merged = list(dict.fromkeys(old + new))
                                existing[key] = merged
                    else:
                        id_kinds[id_name] = id_entry
                    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-add-id-kind
            # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-foreach-id
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-foreach-bp-constraints

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-write-constraints
    lines: List[str] = [
        "# Kit constraints (generated from blueprints)",
        "# Do not edit manually — regenerate with: cypilot generate-resources",
        "",
        'version = "1.0"',
        "",
    ]

    if id_kinds:
        lines.append("[id_kinds]")
        lines.append("")
        for name, entry in sorted(id_kinds.items()):
            lines.append(f"[id_kinds.{name}]")
            lines.append(f"to_code = {'true' if entry.get('to_code') else 'false'}")
            for list_key in ("defined_in", "referenced_in"):
                if list_key in entry:
                    vals = entry[list_key]
                    vals_str = ", ".join(f'"{ v}"' for v in vals)
                    lines.append(f"{list_key} = [{vals_str}]")
            lines.append("")

    if headings:
        lines.append("[headings]")
        lines.append("")
        for kind_name, heading_list in sorted(headings.items()):
            lines.append(f"[[headings.{kind_name}]]")
            for h in heading_list:
                lines.append(f'title = "{h["title"]}"')
                lines.append(f'pattern = "{h["pattern"]}"')
                lines.append(f'required = {"true" if h.get("required") else "false"}')
                lines.append("")

    content = "\n".join(lines)

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-write-constraints

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-return-constraints
    return output_path.as_posix(), errors
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-return-constraints


# ---------------------------------------------------------------------------
# Process Kit (orchestrator)
# ---------------------------------------------------------------------------

def process_kit(
    kit_slug: str,
    blueprints_dir: Path,
    config_kits_dir: Path,
    *,
    dry_run: bool = False,
) -> Tuple[Dict[str, Any], List[str]]:
    """Process all blueprints in a kit and generate outputs.

    Args:
        kit_slug: Kit identifier (e.g. "sdlc").
        blueprints_dir: Path to kit's blueprints/ directory.
        config_kits_dir: Base path for config/kits/{slug}/ outputs.
        dry_run: If True, don't write files.

    Returns:
        (summary dict, errors list) tuple.
    """
    errors: List[str] = []
    all_written: List[str] = []
    all_blueprints: List[ParsedBlueprint] = []
    artifact_kinds: List[str] = []

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-list-blueprints
    bp_files = sorted(blueprints_dir.glob("*.md"))
    if not bp_files:
        errors.append(f"No .md files found in {blueprints_dir}")
        return {"files_written": 0, "artifact_kinds": []}, errors
    # @cpt-end:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-list-blueprints

    kit_output_dir = config_kits_dir / kit_slug

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-foreach-bp
    for bp_file in bp_files:
        # @cpt-begin:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-parse-bp
        bp = parse_blueprint(bp_file)
        all_blueprints.append(bp)
        # @cpt-end:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-parse-bp

        if bp.errors:
            errors.extend(bp.errors)
            continue

        # @cpt-begin:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-extract-kind
        kind = bp.artifact_kind
        artifact_kinds.append(kind)
        # @cpt-end:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-extract-kind

        # @cpt-begin:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-gen-artifact
        has_artifact_key = any(
            m.marker_type == "blueprint" and m.toml_data.get("artifact")
            for m in bp.markers
        )
        if has_artifact_key:
            artifact_out = kit_output_dir / "artifacts" / kind.upper()
        else:
            artifact_out = kit_output_dir

        written, gen_errors = generate_artifact_outputs(
            bp, artifact_out, dry_run=dry_run,
        )
        all_written.extend(written)
        errors.extend(gen_errors)
        # @cpt-end:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-gen-artifact
    # @cpt-end:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-foreach-bp

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-gen-constraints
    constraints_path = kit_output_dir / "constraints.toml"
    c_path, c_errors = generate_constraints(
        all_blueprints, constraints_path, dry_run=dry_run,
    )
    if c_path:
        all_written.append(c_path)
    errors.extend(c_errors)
    # @cpt-end:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-gen-constraints

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-return-generated
    summary: Dict[str, Any] = {
        "files_written": len(all_written),
        "artifact_kinds": artifact_kinds,
        "files": all_written,
    }
    return summary, errors
    # @cpt-end:cpt-cypilot-algo-blueprint-system-process-kit:p1:inst-return-generated
