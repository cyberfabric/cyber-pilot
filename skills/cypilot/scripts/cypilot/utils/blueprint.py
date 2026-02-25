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
    """Build rules.md from @cpt:rules skeleton + @cpt:rule entries.

    Per spec (architecture/specs/kit/rules.md):
    1. Parse @cpt:rules TOML to build section skeleton
    2. Collect all @cpt:rule blocks, group by kind → section
    3. Emit sections in fixed order: prerequisites → requirements → tasks →
       validation → error_handling → next_steps
    4. Within each section, emit sub-sections with collected rules
    """
    # Fixed section order per spec
    SECTION_ORDER = [
        "prerequisites", "requirements", "tasks",
        "validation", "error_handling", "next_steps",
    ]
    SECTION_TITLES = {
        "prerequisites": "Prerequisites",
        "requirements": "Requirements",
        "tasks": "Tasks",
        "validation": "Validation",
        "error_handling": "Error Handling",
        "next_steps": "Next Steps",
    }

    # Parse @cpt:rules skeleton
    skeleton: Dict[str, List[str]] = {}
    for mk in bp.markers:
        if mk.marker_type == "rules":
            td = mk.toml_data
            for kind_key in SECTION_ORDER:
                if kind_key in td:
                    subs = td[kind_key].get("sections", []) or td[kind_key].get("phases", [])
                    skeleton[kind_key] = subs if isinstance(subs, list) else []

    # Group @cpt:rule entries by kind → section (preserving order)
    from collections import OrderedDict
    rules_by_kind: Dict[str, Dict[str, List[str]]] = {}
    for mk in bp.markers:
        if mk.marker_type == "rule":
            td = mk.toml_data
            kind = td.get("kind", "")
            section = td.get("section", "")
            content = mk.markdown_content
            if kind and section and content:
                rules_by_kind.setdefault(kind, OrderedDict()).setdefault(section, []).append(content)

    if not skeleton and not rules_by_kind:
        return ""

    # Build output
    kind_label = bp.artifact_kind.upper() if bp.artifact_kind else "CODEBASE"
    kit = bp.kit_slug or "sdlc"
    parts: List[str] = []

    # Header
    parts.append(f"# {kind_label} Rules")
    parts.append("")
    parts.append(f"**Artifact**: {kind_label}")
    parts.append(f"**Kit**: {kit}")
    parts.append("")
    parts.append("**Dependencies**:")
    parts.append("- `template.md` — structural reference")
    parts.append("- `checklist.md` — semantic quality criteria")
    parts.append("- `examples/example.md` — reference implementation")
    parts.append("")

    # Sections in fixed order
    for kind_key in SECTION_ORDER:
        sub_sections = skeleton.get(kind_key, [])
        kind_rules = rules_by_kind.get(kind_key, {})
        if not sub_sections and not kind_rules:
            continue

        parts.append("---")
        parts.append("")
        parts.append(f"## {SECTION_TITLES.get(kind_key, kind_key.replace('_', ' ').title())}")
        parts.append("")

        # Use skeleton order for sub-sections; fall back to rule order
        seen: set = set()
        ordered_subs = list(sub_sections)
        for s in kind_rules:
            if s not in seen and s not in ordered_subs:
                ordered_subs.append(s)
            seen.add(s)

        for sub in ordered_subs:
            sub_title = sub.replace("_", " ").title()
            parts.append(f"### {sub_title}")
            rule_items = kind_rules.get(sub, [])
            for item in rule_items:
                parts.append(item)
            parts.append("")

    if len(parts) <= 8:  # Only header, no sections
        return ""
    return "\n".join(parts)


def _collect_checklist(bp: ParsedBlueprint) -> str:
    """Build checklist.md from @cpt:checklist skeleton + @cpt:check entries.

    Per spec (architecture/specs/kit/checklist.md):
    1. Parse @cpt:checklist TOML for domains, severity levels, review priority
    2. Collect all @cpt:check blocks, group by domain → kind
    3. For each domain: emit header + standards, MUST HAVE, MUST NOT HAVE
    4. Checks sorted by severity (CRITICAL first) within each kind
    """
    # Parse @cpt:checklist skeleton
    severity_levels: List[str] = []
    review_priority: List[str] = []
    domains: List[Dict[str, Any]] = []

    for mk in bp.markers:
        if mk.marker_type == "checklist":
            td = mk.toml_data
            severity_levels = td.get("severity", {}).get("levels", [])
            review_priority = td.get("review", {}).get("priority", [])
            domains = td.get("domain", [])
            if isinstance(domains, dict):
                domains = [domains]

    # Build domain lookup: abbr → domain info
    domain_map: Dict[str, Dict[str, Any]] = {}
    domain_order: List[str] = []
    for d in domains:
        abbr = d.get("abbr", "")
        if abbr:
            domain_map[abbr] = d
            domain_order.append(abbr)

    # Collect @cpt:check entries grouped by domain → kind
    checks_by_domain: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for mk in bp.markers:
        if mk.marker_type == "check":
            td = mk.toml_data
            domain = td.get("domain", "")
            kind = td.get("kind", "must_have")
            content = mk.markdown_content
            if domain and content:
                entry = {
                    "id": td.get("id", ""),
                    "title": td.get("title", ""),
                    "severity": td.get("severity", "MEDIUM"),
                    "ref": td.get("ref", ""),
                    "belongs_to": td.get("belongs_to", ""),
                    "applicable_when": td.get("applicable_when", ""),
                    "not_applicable_when": td.get("not_applicable_when", ""),
                    "content": content,
                }
                checks_by_domain.setdefault(domain, {}).setdefault(kind, []).append(entry)

    if not checks_by_domain:
        return ""

    # Severity sort key
    sev_order = {s: i for i, s in enumerate(severity_levels)} if severity_levels else {}

    # Build output
    kind_label = bp.artifact_kind.upper() if bp.artifact_kind else "CODEBASE"
    kit = bp.kit_slug or "sdlc"
    parts: List[str] = []

    # Header
    parts.append(f"# {kind_label} Quality Checklist")
    parts.append("")
    parts.append(f"**Artifact**: {kind_label}")
    parts.append(f"**Kit**: {kit}")
    parts.append("")
    if severity_levels:
        parts.append(f"**Severity levels**: {' > '.join(severity_levels)}")
    if review_priority:
        parts.append(f"**Review priority**: {' → '.join(review_priority)}")
    parts.append("")

    # Domain sections in defined order; append any undeclared domains at end
    all_domains = list(domain_order)
    for d in checks_by_domain:
        if d not in all_domains:
            all_domains.append(d)

    for abbr in all_domains:
        domain_checks = checks_by_domain.get(abbr)
        if not domain_checks:
            continue

        d_info = domain_map.get(abbr, {})
        d_name = d_info.get("name", abbr)
        d_standards = d_info.get("standards", [])

        parts.append("---")
        parts.append("")
        parts.append(f"## {abbr} — {d_name}")
        parts.append("")
        if d_standards:
            parts.append(f"**Standards**: {', '.join(d_standards)}")
            parts.append("")

        for kind_key, kind_title in [("must_have", "MUST HAVE"), ("must_not_have", "MUST NOT HAVE")]:
            items = domain_checks.get(kind_key, [])
            if not items:
                continue

            # Sort by severity
            items.sort(key=lambda x: sev_order.get(x["severity"], 99))

            parts.append(f"### {kind_title}")
            parts.append("")

            for item in items:
                check_id = item["id"]
                title = item["title"]
                severity = item["severity"]
                parts.append(f"#### {check_id} — {title} [{severity}]")
                parts.append("")
                parts.append(item["content"])
                parts.append("")
                if item["ref"]:
                    parts.append(f"> **Ref**: {item['ref']}")
                    parts.append("")
                if item["belongs_to"]:
                    parts.append(f"> **Belongs to**: {item['belongs_to']}")
                    parts.append("")

    return "\n".join(parts)


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

    Per spec (architecture/specs/kit/constraints.md):
    1. For each blueprint with artifact key: collect @cpt:heading → [[artifacts.KIND.headings]]
    2. Collect @cpt:id → [artifacts.KIND.identifiers.kind] with [ref.TARGET] sub-tables
    3. Serialize as TOML with deterministic key ordering

    Returns:
        (written_path or None, errors) tuple.
    """
    errors: List[str] = []

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-init-constraints
    # Per-artifact data: kind → { headings: [...], identifiers: { id_kind: {...} } }
    artifacts_data: Dict[str, Dict[str, Any]] = {}
    kit_slug = ""
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-init-constraints

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-foreach-bp-constraints
    for bp in blueprints:
        # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-extract-kind-constraint
        # Only artifact blueprints contribute (not codebase)
        has_artifact_key = any(
            m.marker_type == "blueprint" and m.toml_data.get("artifact")
            for m in bp.markers
        )
        if not has_artifact_key:
            continue
        kind = bp.artifact_kind.upper() if bp.artifact_kind else ""
        if not kind:
            continue
        if not kit_slug and bp.kit_slug:
            kit_slug = bp.kit_slug
        # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-extract-kind-constraint

        art = artifacts_data.setdefault(kind, {"headings": [], "identifiers": {}})

        for mk in bp.markers:
            # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-foreach-heading
            if mk.marker_type == "heading":
                td = mk.toml_data
                heading_id = td.get("id", "")
                if not heading_id:
                    continue
                entry: Dict[str, Any] = {"id": heading_id, "level": td.get("level", 2)}
                if "required" in td:
                    entry["required"] = td["required"]
                if "multiple" in td:
                    entry["multiple"] = td["multiple"]
                if "numbered" in td:
                    entry["numbered"] = td["numbered"]
                if td.get("pattern"):
                    entry["pattern"] = td["pattern"]
                if td.get("description"):
                    entry["description"] = td["description"]
                art["headings"].append(entry)
            # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-foreach-heading

            # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-foreach-id
            elif mk.marker_type == "id":
                td = mk.toml_data
                id_kind = td.get("kind", "")
                if not id_kind:
                    continue
                id_entry: Dict[str, Any] = {}
                for key in ("name", "description", "template"):
                    if td.get(key):
                        id_entry[key] = td[key]
                for bool_key in ("required", "task", "priority", "to_code"):
                    if bool_key in td:
                        id_entry[bool_key] = td[bool_key]
                if td.get("headings"):
                    id_entry["headings"] = td["headings"]
                # Collect [ref.ARTIFACT] sub-tables
                refs: Dict[str, Dict[str, Any]] = {}
                if "ref" in td and isinstance(td["ref"], dict):
                    for target, ref_data in td["ref"].items():
                        ref_entry: Dict[str, Any] = {}
                        if isinstance(ref_data, dict):
                            for rk in ("coverage", "task", "priority"):
                                if rk in ref_data:
                                    ref_entry[rk] = ref_data[rk]
                            if ref_data.get("headings"):
                                ref_entry["headings"] = ref_data["headings"]
                        refs[target] = ref_entry
                if refs:
                    id_entry["ref"] = refs
                art["identifiers"][id_kind] = id_entry
            # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-foreach-id
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-foreach-bp-constraints

    if not artifacts_data:
        return None, errors

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-constraints:p1:inst-write-constraints
    lines: List[str] = [
        "# Auto-generated from all kit blueprints — do not edit manually",
        f'kit = "{kit_slug or "sdlc"}"',
        "",
    ]

    def _toml_val(v: Any) -> str:
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, int):
            return str(v)
        if isinstance(v, str):
            escaped = v.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        if isinstance(v, list):
            items = ", ".join(
                f'"{i.replace(chr(92), chr(92)*2).replace(chr(34), chr(92)+chr(34))}"'
                if isinstance(i, str) else str(i)
                for i in v
            )
            return f"[{items}]"
        return str(v)

    for art_kind in sorted(artifacts_data.keys()):
        art = artifacts_data[art_kind]

        # Heading constraints
        if art["headings"]:
            lines.append(f"# ── {art_kind} Heading outline {'─' * max(1, 50 - len(art_kind))}")
            lines.append("")
            for h in art["headings"]:
                lines.append(f"[[artifacts.{art_kind}.headings]]")
                for hk in ("id", "level", "required", "multiple", "numbered", "pattern", "description"):
                    if hk in h:
                        lines.append(f"{hk} = {_toml_val(h[hk])}")
                lines.append("")

        # ID kind constraints
        if art["identifiers"]:
            lines.append(f"# ── {art_kind} ID kinds {'─' * max(1, 50 - len(art_kind))}")
            lines.append("")
            for id_kind in sorted(art["identifiers"].keys()):
                id_data = art["identifiers"][id_kind]
                refs = id_data.pop("ref", {})
                lines.append(f"[artifacts.{art_kind}.identifiers.{id_kind}]")
                for ik in ("name", "description", "required", "task", "priority", "to_code", "template", "headings"):
                    if ik in id_data:
                        lines.append(f"{ik} = {_toml_val(id_data[ik])}")
                lines.append("")
                # Reference sub-tables
                for target in sorted(refs.keys()):
                    ref_data = refs[target]
                    lines.append(f"[artifacts.{art_kind}.identifiers.{id_kind}.ref.{target}]")
                    for rk in ("coverage", "task", "priority", "headings"):
                        if rk in ref_data:
                            lines.append(f"{rk} = {_toml_val(ref_data[rk])}")
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
