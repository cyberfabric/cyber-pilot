"""Tests for the cypilot toc command and unified TOC module."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from cypilot.commands.toc import (
    _build_toc,
    _parse_headings,
    _process_file,
    _slugify,
    cmd_toc,
)
from cypilot.commands.validate_toc import cmd_validate_toc
from cypilot.utils.toc import (
    build_toc,
    github_anchor,
    insert_toc_heading,
    insert_toc_markers,
    parse_headings,
    validate_toc,
)


# ---------------------------------------------------------------------------
# _slugify
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_simple(self):
        assert _slugify("Overview") == "overview"

    def test_spaces_to_hyphens(self):
        assert _slugify("Quick Reference") == "quick-reference"

    def test_special_chars_stripped(self):
        assert _slugify("Part I — Identifiers") == "part-i-identifiers"

    def test_backticks_removed(self):
        assert _slugify("`code` stuff") == "code-stuff"

    def test_markdown_link(self):
        assert _slugify("[WCAG 2.2](https://example.com)") == "wcag-22"

    def test_bold_italic_removed(self):
        assert _slugify("**Bold** and *italic*") == "bold-and-italic"

    def test_ampersand_stripped(self):
        assert _slugify("Scope & Boundaries") == "scope-boundaries"


# ---------------------------------------------------------------------------
# _parse_headings
# ---------------------------------------------------------------------------

class TestParseHeadings:
    def test_basic(self):
        lines = ["# Title", "## Section", "### Sub"]
        result = _parse_headings(lines, min_level=2)
        assert result == [(2, "Section"), (3, "Sub")]

    def test_skips_fenced_code(self):
        lines = [
            "## Real",
            "```",
            "## Fake inside fence",
            "```",
            "## Also Real",
        ]
        result = _parse_headings(lines, min_level=2)
        assert len(result) == 2
        assert result[0] == (2, "Real")
        assert result[1] == (2, "Also Real")

    def test_max_level(self):
        lines = ["## L2", "### L3", "#### L4"]
        result = _parse_headings(lines, min_level=2, max_level=3)
        assert len(result) == 2

    def test_empty(self):
        assert _parse_headings([]) == []

    def test_no_headings(self):
        lines = ["Just text", "More text"]
        assert _parse_headings(lines) == []


# ---------------------------------------------------------------------------
# _build_toc
# ---------------------------------------------------------------------------

class TestBuildToc:
    def test_flat(self):
        headings = [(2, "A"), (2, "B")]
        toc = _build_toc(headings)
        assert toc == "- [A](#a)\n- [B](#b)"

    def test_nested(self):
        headings = [(2, "Parent"), (3, "Child")]
        toc = _build_toc(headings)
        lines = toc.split("\n")
        assert lines[0] == "- [Parent](#parent)"
        assert lines[1] == "  - [Child](#child)"

    def test_duplicate_slugs(self):
        headings = [(2, "Overview"), (2, "Overview")]
        toc = _build_toc(headings)
        assert "(#overview)" in toc
        assert "(#overview-1)" in toc

    def test_empty(self):
        assert _build_toc([]) == ""

    def test_custom_indent(self):
        headings = [(2, "Parent"), (3, "Child")]
        toc = _build_toc(headings, indent_size=4)
        lines = toc.split("\n")
        assert lines[1].startswith("    - ")


# ---------------------------------------------------------------------------
# _process_file
# ---------------------------------------------------------------------------

class TestProcessFile:
    def test_file_not_found(self, tmp_path: Path):
        result = _process_file(tmp_path / "nope.md")
        assert result["status"] == "ERROR"

    def test_no_headings(self, tmp_path: Path):
        f = tmp_path / "empty.md"
        f.write_text("Just text\n", encoding="utf-8")
        result = _process_file(f)
        assert result["status"] == "SKIP"

    def test_inserts_toc_after_h1(self, tmp_path: Path):
        f = tmp_path / "doc.md"
        f.write_text("# Title\n\n## Section A\n\n## Section B\n", encoding="utf-8")
        result = _process_file(f)
        assert result["status"] == "UPDATED"
        content = f.read_text(encoding="utf-8")
        assert "<!-- toc -->" in content
        assert "<!-- /toc -->" in content
        assert "[Section A](#section-a)" in content
        assert "[Section B](#section-b)" in content

    def test_updates_existing_markers(self, tmp_path: Path):
        f = tmp_path / "doc.md"
        f.write_text(
            "# Title\n\n<!-- toc -->\nold toc\n<!-- /toc -->\n\n## New\n",
            encoding="utf-8",
        )
        result = _process_file(f)
        assert result["status"] == "UPDATED"
        content = f.read_text(encoding="utf-8")
        assert "old toc" not in content
        assert "[New](#new)" in content

    def test_dry_run(self, tmp_path: Path):
        f = tmp_path / "doc.md"
        original = "# Title\n\n## Section\n"
        f.write_text(original, encoding="utf-8")
        result = _process_file(f, dry_run=True)
        assert result["status"] == "WOULD_UPDATE"
        assert f.read_text(encoding="utf-8") == original

    def test_unchanged(self, tmp_path: Path):
        f = tmp_path / "doc.md"
        f.write_text("# Title\n\n## Section\n", encoding="utf-8")
        # First run: insert
        _process_file(f)
        # Second run: should be unchanged
        result = _process_file(f)
        assert result["status"] == "UNCHANGED"

    def test_max_level(self, tmp_path: Path):
        f = tmp_path / "doc.md"
        f.write_text("# T\n\n## L2\n\n### L3\n\n#### L4\n", encoding="utf-8")
        _process_file(f, max_level=3)
        content = f.read_text(encoding="utf-8")
        assert "[L2]" in content
        assert "[L3]" in content
        assert "[L4]" not in content


# ---------------------------------------------------------------------------
# cmd_toc (integration)
# ---------------------------------------------------------------------------

class TestCmdToc:
    def test_basic(self, tmp_path: Path, capsys):
        f = tmp_path / "test.md"
        f.write_text("# Doc\n\n## A\n\n## B\n", encoding="utf-8")
        rc = cmd_toc([str(f)])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "OK"
        assert out["results"][0]["status"] == "UPDATED"

    def test_multiple_files(self, tmp_path: Path, capsys):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("# A\n\n## X\n", encoding="utf-8")
        f2.write_text("# B\n\n## Y\n", encoding="utf-8")
        rc = cmd_toc([str(f1), str(f2)])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["files_processed"] == 2

    def test_dry_run_flag(self, tmp_path: Path, capsys):
        f = tmp_path / "test.md"
        original = "# Doc\n\n## A\n"
        f.write_text(original, encoding="utf-8")
        rc = cmd_toc(["--dry-run", str(f)])
        assert rc == 0
        assert f.read_text(encoding="utf-8") == original

    def test_missing_file(self, tmp_path: Path, capsys):
        rc = cmd_toc([str(tmp_path / "nope.md")])
        assert rc == 1
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "ERROR"


# ---------------------------------------------------------------------------
# Unified module: github_anchor
# ---------------------------------------------------------------------------

class TestGithubAnchor:
    def test_strikethrough_removed(self):
        assert github_anchor("~~deleted~~ text") == "deleted-text"

    def test_double_star_removed(self):
        assert github_anchor("**Bold** title") == "bold-title"

    def test_link_text_kept(self):
        assert github_anchor("[Link](http://example.com) here") == "link-here"

    def test_consecutive_hyphens_collapsed(self):
        assert github_anchor("A — B") == "a-b"

    def test_unicode_preserved(self):
        assert github_anchor("Привет мир") == "привет-мир"


# ---------------------------------------------------------------------------
# Unified module: parse_headings (skip_first, skip_toc_heading)
# ---------------------------------------------------------------------------

class TestParseHeadingsUnified:
    def test_skip_first(self):
        lines = ["# Title", "## A", "## B"]
        result = parse_headings(lines, skip_first=True)
        assert result == [(2, "A"), (2, "B")]

    def test_skip_toc_heading(self):
        lines = ["## Table of Contents", "## Real Section"]
        result = parse_headings(lines, skip_toc_heading=True)
        assert result == [(2, "Real Section")]

    def test_skip_toc_heading_case_insensitive(self):
        lines = ["## TOC", "## Section"]
        result = parse_headings(lines, skip_toc_heading=True)
        assert result == [(2, "Section")]

    def test_skip_first_and_toc(self):
        lines = ["# Doc Title", "## Table of Contents", "## Overview"]
        result = parse_headings(lines, skip_first=True, skip_toc_heading=True)
        assert result == [(2, "Overview")]

    def test_tilde_fences_skipped(self):
        lines = ["## Real", "~~~", "## Fake", "~~~", "## Also Real"]
        result = parse_headings(lines)
        assert result == [(2, "Real"), (2, "Also Real")]

    def test_four_backtick_fence(self):
        lines = ["## Before", "````", "## Inside", "````", "## After"]
        result = parse_headings(lines)
        assert result == [(2, "Before"), (2, "After")]


# ---------------------------------------------------------------------------
# Unified module: build_toc (numbered mode)
# ---------------------------------------------------------------------------

class TestBuildTocNumbered:
    def test_numbered_top_level(self):
        headings = [(2, "First"), (2, "Second"), (2, "Third")]
        toc = build_toc(headings, numbered=True)
        lines = toc.split("\n")
        assert lines[0] == "1. [First](#first)"
        assert lines[1] == "2. [Second](#second)"
        assert lines[2] == "3. [Third](#third)"

    def test_numbered_with_children(self):
        headings = [(2, "Parent"), (3, "Child A"), (3, "Child B"), (2, "Next")]
        toc = build_toc(headings, numbered=True, indent_size=3)
        lines = toc.split("\n")
        assert lines[0] == "1. [Parent](#parent)"
        assert lines[1] == "   - [Child A](#child-a)"
        assert lines[2] == "   - [Child B](#child-b)"
        assert lines[3] == "2. [Next](#next)"

    def test_numbered_deep_nesting(self):
        headings = [(2, "L2"), (3, "L3"), (4, "L4")]
        toc = build_toc(headings, numbered=True, indent_size=3)
        lines = toc.split("\n")
        assert lines[0] == "1. [L2](#l2)"
        assert lines[1] == "   - [L3](#l3)"
        assert lines[2] == "      - [L4](#l4)"

    def test_numbered_duplicate_slugs(self):
        headings = [(2, "Intro"), (2, "Intro")]
        toc = build_toc(headings, numbered=True)
        assert "1. [Intro](#intro)" in toc
        assert "2. [Intro](#intro-1)" in toc


# ---------------------------------------------------------------------------
# Unified module: insert_toc_markers
# ---------------------------------------------------------------------------

class TestInsertTocMarkers:
    def test_inserts_after_h1(self):
        content = "# Title\n\n## A\n\n## B\n"
        result = insert_toc_markers(content)
        assert "<!-- toc -->" in result
        assert "<!-- /toc -->" in result
        assert "[A](#a)" in result

    def test_replaces_between_markers(self):
        content = "# Title\n\n<!-- toc -->\nold\n<!-- /toc -->\n\n## New\n"
        result = insert_toc_markers(content)
        assert "old" not in result
        assert "[New](#new)" in result

    def test_no_headings_returns_unchanged(self):
        content = "# Only title\n\nSome text.\n"
        assert insert_toc_markers(content) == content

    def test_respects_max_level(self):
        content = "# T\n\n## L2\n\n### L3\n\n#### L4\n"
        result = insert_toc_markers(content, max_level=2)
        assert "[L2]" in result
        assert "[L3]" not in result


# ---------------------------------------------------------------------------
# Unified module: insert_toc_heading (blueprint-style)
# ---------------------------------------------------------------------------

class TestInsertTocHeading:
    def test_inserts_heading_section(self):
        content = "# Blueprint\n\n---\n\n## Rules\n\n## Checks\n"
        result = insert_toc_heading(content)
        assert "## Table of Contents" in result
        assert "[Rules](#rules)" in result
        assert "[Checks](#checks)" in result

    def test_replaces_existing_toc_heading(self):
        content = (
            "# Blueprint\n\n"
            "## Table of Contents\n\nold toc\n\n"
            "## Rules\n\n## Checks\n"
        )
        result = insert_toc_heading(content)
        assert "old toc" not in result
        assert "[Rules](#rules)" in result

    def test_skips_first_heading(self):
        content = "# Title\n\n## Section\n"
        result = insert_toc_heading(content)
        # Title should not appear in TOC
        assert "[Title]" not in result
        assert "[Section](#section)" in result

    def test_numbered_by_default(self):
        content = "# Title\n\n## A\n\n## B\n"
        result = insert_toc_heading(content)
        assert "1. [A](#a)" in result
        assert "2. [B](#b)" in result

    def test_max_heading_level(self):
        content = "# T\n\n## L2\n\n### L3\n"
        result = insert_toc_heading(content, max_heading_level=2)
        assert "[L2]" in result
        assert "[L3]" not in result

    def test_no_headings_returns_unchanged(self):
        content = "# Only Title\n"
        assert insert_toc_heading(content) == content

    def test_frontmatter_handling(self):
        content = "---\ntitle: Test\n---\n\n# Title\n\n---\n\n## Section\n"
        result = insert_toc_heading(content)
        assert "## Table of Contents" in result
        assert "[Section](#section)" in result


# ---------------------------------------------------------------------------
# Unified module: validate_toc
# ---------------------------------------------------------------------------

class TestValidateToc:
    def test_no_headings_no_errors(self):
        content = "# Only Title\n\nSome text.\n"
        result = validate_toc(content)
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_missing_toc(self):
        content = "# Title\n\n## Section A\n\n## Section B\n"
        result = validate_toc(content)
        assert len(result["errors"]) == 1
        assert result["errors"][0]["code"] == "toc-missing"

    def test_valid_heading_based_toc(self):
        content = (
            "# Title\n\n"
            "## Table of Contents\n\n"
            "1. [Section A](#section-a)\n"
            "2. [Section B](#section-b)\n\n"
            "---\n\n"
            "## Section A\n\n"
            "## Section B\n"
        )
        result = validate_toc(content, max_heading_level=2)
        assert result["errors"] == []

    def test_valid_marker_based_toc(self):
        content = (
            "# Title\n\n"
            "<!-- toc -->\n\n"
            "- [Section A](#section-a)\n"
            "- [Section B](#section-b)\n\n"
            "<!-- /toc -->\n\n"
            "## Section A\n\n"
            "## Section B\n"
        )
        result = validate_toc(content)
        assert result["errors"] == []

    def test_broken_anchor(self):
        content = (
            "# Title\n\n"
            "## Table of Contents\n\n"
            "1. [Old Name](#old-name)\n\n"
            "---\n\n"
            "## New Name\n"
        )
        result = validate_toc(content, max_heading_level=2)
        errors = result["errors"]
        codes = [e["code"] for e in errors]
        assert "toc-anchor-broken" in codes
        assert "toc-heading-not-in-toc" in codes

    def test_heading_not_in_toc(self):
        content = (
            "# Title\n\n"
            "## Table of Contents\n\n"
            "1. [Section A](#section-a)\n\n"
            "---\n\n"
            "## Section A\n\n"
            "## Section B\n"
        )
        result = validate_toc(content, max_heading_level=2)
        errors = result["errors"]
        assert any(e["code"] == "toc-heading-not-in-toc" for e in errors)
        missing = [e for e in errors if e["code"] == "toc-heading-not-in-toc"]
        assert missing[0]["heading_text"] == "Section B"

    def test_stale_toc_warning(self):
        # Valid TOC but with wrong ordering/numbering
        content = (
            "# Title\n\n"
            "## Table of Contents\n\n"
            "1. [Section B](#section-b)\n"
            "2. [Section A](#section-a)\n\n"
            "---\n\n"
            "## Section A\n\n"
            "## Section B\n"
        )
        result = validate_toc(content, max_heading_level=2)
        # No hard errors (all anchors are valid), but staleness warning
        assert result["errors"] == []
        assert any(w["code"] == "toc-stale" for w in result["warnings"])

    def test_duplicate_headings_handled(self):
        content = (
            "# Title\n\n"
            "## Table of Contents\n\n"
            "1. [Intro](#intro)\n"
            "2. [Intro](#intro-1)\n\n"
            "---\n\n"
            "## Intro\n\n"
            "## Intro\n"
        )
        result = validate_toc(content, max_heading_level=2)
        assert result["errors"] == []

    def test_error_has_line_number(self):
        content = "# Title\n\n## Section A\n\n## Section B\n"
        result = validate_toc(content)
        assert result["errors"][0]["line"] == 1

    def test_broken_anchor_has_line_number(self):
        content = (
            "# Title\n\n"
            "## Table of Contents\n\n"
            "1. [Gone](#gone)\n\n"
            "---\n\n"
            "## Actual\n"
        )
        result = validate_toc(content, max_heading_level=2)
        broken = [e for e in result["errors"] if e["code"] == "toc-anchor-broken"]
        assert broken[0]["line"] == 5  # line of the broken TOC entry


# ---------------------------------------------------------------------------
# cmd_validate_toc (integration)
# ---------------------------------------------------------------------------

class TestCmdValidateToc:
    def test_pass(self, tmp_path: Path, capsys):
        f = tmp_path / "good.md"
        f.write_text(
            "# Title\n\n"
            "## Table of Contents\n\n"
            "1. [A](#a)\n\n"
            "---\n\n"
            "## A\n",
            encoding="utf-8",
        )
        rc = cmd_validate_toc([str(f), "--max-level", "2"])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "PASS"

    def test_fail_missing_toc(self, tmp_path: Path, capsys):
        f = tmp_path / "bad.md"
        f.write_text("# Title\n\n## Section\n", encoding="utf-8")
        rc = cmd_validate_toc([str(f)])
        assert rc == 2
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "FAIL"
        assert out["error_count"] == 1

    def test_missing_file(self, tmp_path: Path, capsys):
        rc = cmd_validate_toc([str(tmp_path / "nope.md")])
        assert rc == 2
        out = json.loads(capsys.readouterr().out)
        assert out["results"][0]["status"] == "ERROR"

    def test_multiple_files(self, tmp_path: Path, capsys):
        good = tmp_path / "good.md"
        good.write_text(
            "# T\n\n## Table of Contents\n\n1. [A](#a)\n\n---\n\n## A\n",
            encoding="utf-8",
        )
        bad = tmp_path / "bad.md"
        bad.write_text("# T\n\n## Section\n", encoding="utf-8")
        rc = cmd_validate_toc([str(good), str(bad)])
        assert rc == 2
        out = json.loads(capsys.readouterr().out)
        assert out["files_validated"] == 2
        assert out["error_count"] == 1

    def test_verbose_flag(self, tmp_path: Path, capsys):
        f = tmp_path / "doc.md"
        f.write_text(
            "# T\n\n## Table of Contents\n\n1. [A](#a)\n\n---\n\n## A\n",
            encoding="utf-8",
        )
        rc = cmd_validate_toc(["--verbose", "--max-level", "2", str(f)])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert "errors" in out["results"][0]
        assert "warnings" in out["results"][0]

    def test_warn_stale_toc(self, tmp_path: Path, capsys):
        f = tmp_path / "stale.md"
        f.write_text(
            "# T\n\n"
            "## Table of Contents\n\n"
            "1. [B](#b)\n"
            "2. [A](#a)\n\n"
            "---\n\n"
            "## A\n\n"
            "## B\n",
            encoding="utf-8",
        )
        rc = cmd_validate_toc(["--max-level", "2", str(f)])
        assert rc == 0  # warnings don't cause failure
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "WARN"
        assert out["warning_count"] >= 1


# ---------------------------------------------------------------------------
# Blueprint toc flag: rules.md injection + constraints
# ---------------------------------------------------------------------------

from cypilot.utils.blueprint import (
    ParsedBlueprint,
    parse_blueprint,
    _collect_rules,
    generate_artifact_outputs,
    generate_constraints,
)


class TestBlueprintTocFlag:
    def _make_blueprint(self, tmp_path: Path, toc: bool = True) -> Path:
        """Create a minimal blueprint file with toc flag."""
        toc_str = "true" if toc else "false"
        content = textwrap.dedent(f"""\
            `@cpt:blueprint`
            ```toml
            artifact = "TEST"
            kit = "test-kit"
            version = "1.0"
            toc = {toc_str}
            ```
            `@/cpt:blueprint`

            `@cpt:rules`
            ```toml
            [tasks]
            phases = ["setup"]

            [validation]
            phases = ["structural"]
            ```
            `@/cpt:rules`

            `@cpt:rule`
            ```toml
            kind = "tasks"
            section = "setup"
            ```
            ```markdown
            - [ ] Load template
            ```
            `@/cpt:rule`

            `@cpt:rule`
            ```toml
            kind = "validation"
            section = "structural"
            ```
            ```markdown
            - [ ] Check headings
            ```
            `@/cpt:rule`
        """)
        bp_file = tmp_path / "TEST.md"
        bp_file.write_text(content, encoding="utf-8")
        return bp_file

    def test_parse_toc_true_default(self, tmp_path: Path):
        content = textwrap.dedent("""\
            `@cpt:blueprint`
            ```toml
            artifact = "X"
            kit = "k"
            ```
            `@/cpt:blueprint`
        """)
        f = tmp_path / "X.md"
        f.write_text(content, encoding="utf-8")
        bp = parse_blueprint(f)
        assert bp.toc is True

    def test_parse_toc_false(self, tmp_path: Path):
        bp_file = self._make_blueprint(tmp_path, toc=False)
        bp = parse_blueprint(bp_file)
        assert bp.toc is False

    def test_rules_inject_toc_phases_when_true(self, tmp_path: Path):
        bp_file = self._make_blueprint(tmp_path, toc=True)
        bp = parse_blueprint(bp_file)
        rules_md = _collect_rules(bp)
        assert "Table of Contents" in rules_md
        assert "cypilot toc" in rules_md
        assert "cypilot validate-toc" in rules_md

    def test_rules_no_toc_phases_when_false(self, tmp_path: Path):
        bp_file = self._make_blueprint(tmp_path, toc=False)
        bp = parse_blueprint(bp_file)
        rules_md = _collect_rules(bp)
        assert "cypilot toc" not in rules_md
        assert "cypilot validate-toc" not in rules_md

    def test_constraints_toc_default_true(self, tmp_path: Path):
        bp_file = self._make_blueprint(tmp_path, toc=True)
        bp = parse_blueprint(bp_file)
        # Add minimal heading/id markers for constraints generation
        out_path = tmp_path / "constraints.toml"
        # Generate constraints — toc=true should NOT emit toc=false
        generate_constraints([bp], out_path)
        content = out_path.read_text(encoding="utf-8")
        assert "toc = false" not in content

    def test_constraints_toc_false_emitted(self, tmp_path: Path):
        bp_file = self._make_blueprint(tmp_path, toc=False)
        bp = parse_blueprint(bp_file)
        out_path = tmp_path / "constraints.toml"
        generate_constraints([bp], out_path)
        content = out_path.read_text(encoding="utf-8")
        assert "toc = false" in content

    def test_constraints_emit_references(self, tmp_path: Path):
        content = textwrap.dedent("""\
            `@cpt:blueprint`
            ```toml
            artifact = "PRD"
            kit = "sdlc"
            ```
            `@/cpt:blueprint`

            `@cpt:id`
            ```toml
            kind = "fr"
            name = "Functional Requirement"
            required = true
            template = "cpt-{system}-fr-{slug}"
            headings = ["prd-fr"]

            [references.DECOMPOSITION]
            headings = ["decomposition-entry"]

            [references.DESIGN]
            coverage = true
            headings = ["design-drivers"]
            ```
            `@/cpt:id`
        """)
        f = tmp_path / "PRD.md"
        f.write_text(content, encoding="utf-8")
        bp = parse_blueprint(f)
        out_path = tmp_path / "constraints.toml"
        generate_constraints([bp], out_path)
        toml_content = out_path.read_text(encoding="utf-8")
        assert "[artifacts.PRD.identifiers.fr.references.DECOMPOSITION]" in toml_content
        assert "[artifacts.PRD.identifiers.fr.references.DESIGN]" in toml_content
        assert 'headings = ["decomposition-entry"]' in toml_content
        assert "coverage = true" in toml_content

    def _make_blueprint_with_example(self, tmp_path: Path, toc: bool) -> Path:
        toc_str = "true" if toc else "false"
        content = textwrap.dedent(f"""\
            `@cpt:blueprint`
            ```toml
            artifact = "EX"
            kit = "test-kit"
            version = "1.0"
            toc = {toc_str}
            ```
            `@/cpt:blueprint`

            `@cpt:heading`
            ```toml
            id = "ex-overview"
            level = 1
            pattern = "Example"
            examples = ["# Example Document"]
            ```
            `@/cpt:heading`

            `@cpt:heading`
            ```toml
            id = "ex-section-a"
            level = 2
            pattern = "Section A"
            examples = ["## Section A"]
            ```
            `@/cpt:heading`

            `@cpt:heading`
            ```toml
            id = "ex-section-b"
            level = 2
            pattern = "Section B"
            examples = ["## Section B"]
            ```
            `@/cpt:heading`

            `@cpt:example`
            ```markdown
            Content of section A.
            ```
            `@/cpt:example`

            `@cpt:example`
            ```markdown
            Content of section B.
            ```
            `@/cpt:example`
        """)
        bp_file = tmp_path / "EX.md"
        bp_file.write_text(content, encoding="utf-8")
        return bp_file

    def test_example_has_toc_when_true(self, tmp_path: Path):
        bp_file = self._make_blueprint_with_example(tmp_path, toc=True)
        bp = parse_blueprint(bp_file)
        out_dir = tmp_path / "out" / "artifacts" / "EX"
        generate_artifact_outputs(bp, out_dir)
        example = (out_dir / "examples" / "example.md").read_text(encoding="utf-8")
        assert "Table of Contents" in example

    def test_example_no_toc_when_false(self, tmp_path: Path):
        bp_file = self._make_blueprint_with_example(tmp_path, toc=False)
        bp = parse_blueprint(bp_file)
        out_dir = tmp_path / "out" / "artifacts" / "EX"
        generate_artifact_outputs(bp, out_dir)
        example = (out_dir / "examples" / "example.md").read_text(encoding="utf-8")
        assert "Table of Contents" not in example

    def test_template_has_toc_placeholder_when_true(self, tmp_path: Path):
        bp_file = self._make_blueprint_with_example(tmp_path, toc=True)
        bp = parse_blueprint(bp_file)
        out_dir = tmp_path / "out" / "artifacts" / "EX"
        generate_artifact_outputs(bp, out_dir)
        template = (out_dir / "template.md").read_text(encoding="utf-8")
        assert "## Table of Contents" in template
        assert "cypilot toc" in template

    def test_template_no_toc_placeholder_when_false(self, tmp_path: Path):
        bp_file = self._make_blueprint_with_example(tmp_path, toc=False)
        bp = parse_blueprint(bp_file)
        out_dir = tmp_path / "out" / "artifacts" / "EX"
        generate_artifact_outputs(bp, out_dir)
        template = (out_dir / "template.md").read_text(encoding="utf-8")
        assert "## Table of Contents" not in template

    def test_rules_always_has_toc_even_when_false(self, tmp_path: Path):
        bp_file = self._make_blueprint(tmp_path, toc=False)
        bp = parse_blueprint(bp_file)
        out_dir = tmp_path / "out" / "artifacts" / "TEST"
        generate_artifact_outputs(bp, out_dir)
        rules = (out_dir / "rules.md").read_text(encoding="utf-8")
        assert "Table of Contents" in rules


class TestArtifactKindConstraintsToc:
    def test_toc_default_true(self):
        from cypilot.utils.constraints import ArtifactKindConstraints
        c = ArtifactKindConstraints(name=None, description=None, defined_id=[])
        assert c.toc is True

    def test_parse_toc_false(self):
        from cypilot.utils.constraints import parse_kit_constraints
        data = {
            "TEST": {
                "toc": False,
                "identifiers": {},
            }
        }
        kc, errs = parse_kit_constraints(data)
        assert not errs
        assert kc is not None
        assert kc.by_kind["TEST"].toc is False

    def test_parse_toc_absent_defaults_true(self):
        from cypilot.utils.constraints import parse_kit_constraints
        data = {
            "TEST": {
                "identifiers": {},
            }
        }
        kc, errs = parse_kit_constraints(data)
        assert not errs
        assert kc is not None
        assert kc.by_kind["TEST"].toc is True
