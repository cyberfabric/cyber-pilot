"""
Self-contained tests for blueprint.py to ensure CI coverage ≥90%.

These tests create blueprint files with all marker types in temp dirs,
so they don't depend on ~/.cypilot/cache or any local state.
"""

import sys
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.utils.blueprint import (
    parse_blueprint,
    generate_artifact_outputs,
    generate_constraints,
    process_kit,
    _collect_rules,
    _collect_checklist,
    _collect_template,
    _collect_example,
)


def _write_bp(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Full blueprint with all marker types
# ---------------------------------------------------------------------------
FULL_BLUEPRINT = """\
    `@cpt:blueprint`
    ```toml
    artifact = "REQ"
    kit = "sdlc"
    version = 1
    toc = true
    template_frontmatter = "type: requirement"
    example_frontmatter = "type: requirement-example"
    ```
    `@/cpt:blueprint`

    `@cpt:heading`
    ```toml
    id = "h-title"
    level = 1
    pattern = "Product Requirements*"
    template = "Product Requirements"
    required = true
    examples = ["# Product Requirements: Acme"]
    ```
    `@/cpt:heading`

    `@cpt:heading`
    ```toml
    id = "h-scope"
    level = 2
    template = "Scope"
    numbered = true
    examples = ["## 1. Scope"]
    ```
    `@/cpt:heading`

    `@cpt:heading`
    ```toml
    id = "h-goals"
    level = 2
    template = "Goals"
    numbered = true
    examples = ["## 2. Goals"]
    ```
    `@/cpt:heading`

    `@cpt:prompt`
    ```markdown
    Describe the project scope and boundaries.
    ```
    `@/cpt:prompt`

    `@cpt:example`
    ```markdown
    The scope covers the REST API and admin panel.
    ```
    `@/cpt:example`

    `@cpt:id`
    ```toml
    kind = "feature"
    name = "Feature"
    required = true
    task = true
    to_code = true
    template = "cpt-{system}-feature-{slug}"
    headings = ["h-scope"]
    [references.DESIGN]
    coverage = true
    task = true
    headings = ["decomposition-entry"]
    ```
    `@/cpt:id`

    `@cpt:rules`
    ```toml
    [tasks]
    phases = ["load", "write"]
    [validation]
    phases = ["structural", "semantic"]
    ```
    `@/cpt:rules`

    `@cpt:rule`
    ```toml
    kind = "tasks"
    section = "load"
    ```
    ```markdown
    - [ ] Load template and checklist
    ```
    `@/cpt:rule`

    `@cpt:rule`
    ```toml
    kind = "tasks"
    section = "write"
    ```
    ```markdown
    - [ ] Write content following template
    ```
    `@/cpt:rule`

    `@cpt:rule`
    ```toml
    kind = "validation"
    section = "structural"
    ```
    ```markdown
    - [ ] All required headings present
    ```
    `@/cpt:rule`

    `@cpt:checklist`
    ```toml
    group_by_kind = true
    must_not_preamble = "Avoid these anti-patterns."
    [severity]
    levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    [[domain]]
    abbr = "COMP"
    name = "Completeness"
    header = "Completeness (COMP)"
    standards = ["ISO-25010"]
    [[domain]]
    abbr = "CLAR"
    name = "Clarity"
    header = "Clarity (CLAR)"
    standards_text = "> Must be unambiguous"
    [sections]
    format_check = "FORMAT VALIDATION"
    ```
    ```markdown
    This checklist validates REQ artifacts.
    ```
    `@/cpt:checklist`

    `@cpt:check`
    ```toml
    id = "CK-COMP-01"
    title = "All sections filled"
    severity = "CRITICAL"
    domain = "COMP"
    kind = "must_have"
    ref = "ISO-25010 §4.1"
    ```
    ```markdown
    Every required section must have substantive content.
    ```
    `@/cpt:check`

    `@cpt:check`
    ```toml
    id = "CK-CLAR-01"
    title = "No ambiguous terms"
    severity = "HIGH"
    domain = "CLAR"
    kind = "must_have"
    ```
    ```markdown
    Requirements must not use vague terms like "should" or "maybe".
    ```
    `@/cpt:check`

    `@cpt:check`
    ```toml
    id = "CK-NEG-01"
    title = "No implementation details"
    severity = "MEDIUM"
    kind = "must_not_have"
    ```
    ```markdown
    Requirements must not specify implementation.
    ```
    `@/cpt:check`

    `@cpt:check`
    ```toml
    id = "CK-FMT-01"
    title = "Heading format correct"
    severity = "LOW"
    domain = "COMP"
    kind = "format_check"
    ```
    ```markdown
    Headings must follow the template structure.
    ```
    `@/cpt:check`

    `@cpt:skill`
    ```markdown
    Use this skill for requirement artifacts.
    ```
    `@/cpt:skill`

    `@cpt:sysprompt`
    ```markdown
    You are a requirements engineer.
    ```
    `@/cpt:sysprompt`

    `@cpt:workflow`
    ```toml
    name = "req-review"
    description = "Review requirements"
    version = "1"
    purpose = "Validate PRD quality"
    ```
    ```markdown
    ## Steps
    1. Load the PRD
    2. Run checklist
    ```
    `@/cpt:workflow`
"""

# ---------------------------------------------------------------------------
# Codebase blueprint (no artifact key, group_by_kind=false)
# ---------------------------------------------------------------------------
CODEBASE_BLUEPRINT = """\
    `@cpt:blueprint`
    ```toml
    kit = "sdlc"
    version = 1
    ```
    `@/cpt:blueprint`

    `@cpt:rules`
    ```toml
    [tasks]
    phases = ["review"]
    ```
    `@/cpt:rules`

    `@cpt:rule`
    ```toml
    kind = "tasks"
    section = "review"
    ```
    ```markdown
    - [ ] Review code quality
    ```
    `@/cpt:rule`

    `@cpt:checklist`
    ```toml
    group_by_kind = false
    [[domain]]
    abbr = "SEC"
    name = "Security"
    header = "Security (SEC)"
    preamble = "Check for common vulnerabilities."
    ```
    `@/cpt:checklist`

    `@cpt:check`
    ```toml
    id = "CB-SEC-01"
    title = "No hardcoded secrets"
    severity = "CRITICAL"
    domain = "SEC"
    kind = "must_have"
    ```
    ```markdown
    Source files must not contain API keys or passwords.
    ```
    `@/cpt:check`

    `@cpt:check`
    ```toml
    id = "CB-SEC-02"
    title = "No eval usage"
    severity = "HIGH"
    domain = "SEC"
    kind = "must_not_have"
    ```
    ```markdown
    Do not use eval() or exec().
    ```
    `@/cpt:check`

    `@cpt:checklist_epilogue`
    ```markdown
    ## Summary
    Review complete.
    ```
    `@/cpt:checklist_epilogue`
"""


class TestParseBlueprint(unittest.TestCase):
    def test_parse_full_blueprint(self):
        with TemporaryDirectory() as td:
            bp_file = _write_bp(Path(td), "REQ.md", FULL_BLUEPRINT)
            bp = parse_blueprint(bp_file)
            self.assertEqual(bp.artifact_kind, "REQ")
            self.assertEqual(bp.kit_slug, "sdlc")
            self.assertTrue(bp.toc)
            self.assertFalse(bp.errors)
            types = {m.marker_type for m in bp.markers}
            self.assertIn("checklist", types)
            self.assertIn("check", types)
            self.assertIn("heading", types)
            self.assertIn("prompt", types)
            self.assertIn("example", types)
            self.assertIn("id", types)
            self.assertIn("rules", types)
            self.assertIn("rule", types)
            self.assertIn("skill", types)
            self.assertIn("sysprompt", types)
            self.assertIn("workflow", types)

    def test_parse_unreadable_file(self):
        bp = parse_blueprint(Path("/nonexistent/path/to/file.md"))
        self.assertTrue(bp.errors)
        self.assertIn("Cannot read", bp.errors[0])

    def test_parse_unclosed_marker(self):
        with TemporaryDirectory() as td:
            bp_file = _write_bp(Path(td), "BAD.md", """\
                `@cpt:blueprint`
                ```toml
                artifact = "X"
                ```
            """)
            bp = parse_blueprint(bp_file)
            self.assertTrue(bp.errors)
            self.assertIn("unclosed marker", bp.errors[0])

    def test_parse_unclosed_fence(self):
        with TemporaryDirectory() as td:
            bp_file = _write_bp(Path(td), "BAD2.md", """\
                `@cpt:blueprint`
                ```toml
                artifact = "X"
                `@/cpt:blueprint`
            """)
            bp = parse_blueprint(bp_file)
            self.assertTrue(bp.errors)
            self.assertIn("unclosed fenced block", bp.errors[0])

    def test_parse_invalid_toml(self):
        with TemporaryDirectory() as td:
            bp_file = _write_bp(Path(td), "BAD3.md", """\
                `@cpt:blueprint`
                ```toml
                {{invalid toml
                ```
                `@/cpt:blueprint`
            """)
            bp = parse_blueprint(bp_file)
            self.assertTrue(bp.errors)
            self.assertIn("invalid TOML", bp.errors[0])


class TestCollectChecklist(unittest.TestCase):
    def test_checklist_grouped_by_kind(self):
        with TemporaryDirectory() as td:
            bp = parse_blueprint(_write_bp(Path(td), "REQ.md", FULL_BLUEPRINT))
            result = _collect_checklist(bp)
            self.assertIn("MUST HAVE", result)
            self.assertIn("MUST NOT HAVE", result)
            self.assertIn("Completeness (COMP)", result)
            self.assertIn("Clarity (CLAR)", result)
            self.assertIn("CK-COMP-01", result)
            self.assertIn("CK-NEG-01", result)
            self.assertIn("FORMAT VALIDATION", result)
            self.assertIn("CK-FMT-01", result)
            self.assertIn("Avoid these anti-patterns.", result)
            self.assertIn("ISO-25010", result)
            self.assertIn("Must be unambiguous", result)
            # Preamble
            self.assertIn("This checklist validates REQ artifacts.", result)
            # Validation epilogue should be appended for group_by_kind=True
            self.assertIn("Reporting", result)

    def test_checklist_not_grouped(self):
        with TemporaryDirectory() as td:
            bp = parse_blueprint(_write_bp(Path(td), "CODEBASE.md", CODEBASE_BLUEPRINT))
            result = _collect_checklist(bp)
            self.assertIn("Security (SEC)", result)
            self.assertIn("CB-SEC-01", result)
            self.assertIn("Check for common vulnerabilities.", result)
            # Epilogue from @cpt:checklist_epilogue
            self.assertIn("Review complete.", result)
            # Should NOT have MUST HAVE/MUST NOT HAVE H1 headers
            self.assertNotIn("# MUST HAVE", result)

    def test_empty_checklist_returns_empty(self):
        with TemporaryDirectory() as td:
            bp = parse_blueprint(_write_bp(Path(td), "EMPTY.md", """\
                `@cpt:blueprint`
                ```toml
                artifact = "EMPTY"
                kit = "sdlc"
                ```
                `@/cpt:blueprint`
            """))
            self.assertEqual(_collect_checklist(bp), "")


class TestCollectRules(unittest.TestCase):
    def test_rules_with_phases(self):
        with TemporaryDirectory() as td:
            bp = parse_blueprint(_write_bp(Path(td), "REQ.md", FULL_BLUEPRINT))
            result = _collect_rules(bp)
            self.assertIn("REQ Rules", result)
            self.assertIn("Phase 1:", result)
            self.assertIn("Load template and checklist", result)
            self.assertIn("Dependencies", result)
            self.assertIn("template.md", result)
            self.assertIn("checklist.md", result)

    def test_codebase_rules(self):
        with TemporaryDirectory() as td:
            bp = parse_blueprint(_write_bp(Path(td), "CODEBASE.md", CODEBASE_BLUEPRINT))
            result = _collect_rules(bp)
            self.assertIn("CODEBASE Rules", result)
            self.assertIn("Review code quality", result)


class TestCollectTemplate(unittest.TestCase):
    def test_template_with_frontmatter_and_toc(self):
        with TemporaryDirectory() as td:
            bp = parse_blueprint(_write_bp(Path(td), "REQ.md", FULL_BLUEPRINT))
            result = _collect_template(bp)
            self.assertIn("type: requirement", result)
            self.assertIn("Product Requirements", result)
            self.assertIn("Table of Contents", result)
            # Numbered headings
            self.assertIn("1.", result)

    def test_template_pattern_fallback(self):
        """When template is empty, pattern is used if not regex."""
        with TemporaryDirectory() as td:
            bp = parse_blueprint(_write_bp(Path(td), "T.md", """\
                `@cpt:blueprint`
                ```toml
                artifact = "T"
                kit = "k"
                ```
                `@/cpt:blueprint`

                `@cpt:heading`
                ```toml
                id = "h1"
                level = 2
                pattern = "Simple Heading"
                ```
                `@/cpt:heading`
            """))
            result = _collect_template(bp)
            self.assertIn("Simple Heading", result)

    def test_template_prompt_under_heading(self):
        with TemporaryDirectory() as td:
            bp = parse_blueprint(_write_bp(Path(td), "REQ.md", FULL_BLUEPRINT))
            result = _collect_template(bp)
            self.assertIn("Describe the project scope", result)


class TestCollectExample(unittest.TestCase):
    def test_example_with_frontmatter(self):
        with TemporaryDirectory() as td:
            bp = parse_blueprint(_write_bp(Path(td), "REQ.md", FULL_BLUEPRINT))
            result = _collect_example(bp)
            self.assertIn("type: requirement-example", result)
            self.assertIn("Acme", result)
            self.assertIn("REST API", result)

    def test_empty_example_returns_empty(self):
        with TemporaryDirectory() as td:
            bp = parse_blueprint(_write_bp(Path(td), "E.md", """\
                `@cpt:blueprint`
                ```toml
                artifact = "E"
                kit = "k"
                ```
                `@/cpt:blueprint`
            """))
            self.assertEqual(_collect_example(bp), "")


class TestGenerateArtifactOutputs(unittest.TestCase):
    def test_full_artifact_generates_all_files(self):
        with TemporaryDirectory() as td:
            tmp = Path(td)
            bp = parse_blueprint(_write_bp(tmp, "REQ.md", FULL_BLUEPRINT))
            out_dir = tmp / "out" / "artifacts" / "REQ"
            written, errors = generate_artifact_outputs(bp, out_dir)
            self.assertFalse(errors)
            self.assertGreater(len(written), 0)
            self.assertTrue((out_dir / "rules.md").is_file())
            self.assertTrue((out_dir / "checklist.md").is_file())
            self.assertTrue((out_dir / "template.md").is_file())
            self.assertTrue((out_dir / "examples" / "example.md").is_file())

    def test_codebase_generates_into_codebase_subdir(self):
        with TemporaryDirectory() as td:
            tmp = Path(td)
            bp = parse_blueprint(_write_bp(tmp, "CODEBASE.md", CODEBASE_BLUEPRINT))
            out_dir = tmp / "out"
            written, errors = generate_artifact_outputs(bp, out_dir)
            self.assertFalse(errors)
            self.assertTrue((out_dir / "codebase" / "rules.md").is_file())
            self.assertTrue((out_dir / "codebase" / "checklist.md").is_file())


class TestGenerateConstraints(unittest.TestCase):
    def test_generates_heading_and_id_constraints(self):
        with TemporaryDirectory() as td:
            tmp = Path(td)
            bp = parse_blueprint(_write_bp(tmp, "REQ.md", FULL_BLUEPRINT))
            out_path = tmp / "constraints.toml"
            result_path, errors = generate_constraints([bp], out_path)
            self.assertFalse(errors)
            self.assertIsNotNone(result_path)
            content = out_path.read_text(encoding="utf-8")
            self.assertIn("[[artifacts.REQ.headings]]", content)
            self.assertIn('[artifacts.REQ.identifiers.feature]', content)
            self.assertIn("coverage = true", content)
            self.assertIn('kit = "sdlc"', content)

    def test_skips_non_artifact_blueprints(self):
        with TemporaryDirectory() as td:
            tmp = Path(td)
            bp = parse_blueprint(_write_bp(tmp, "CB.md", CODEBASE_BLUEPRINT))
            out_path = tmp / "constraints.toml"
            result_path, errors = generate_constraints([bp], out_path)
            # No artifact key → skipped, returns None
            self.assertIsNone(result_path)

    def test_toml_val_list_and_bool(self):
        """Exercises _toml_val with list values via heading constraints."""
        with TemporaryDirectory() as td:
            tmp = Path(td)
            bp = parse_blueprint(_write_bp(tmp, "R.md", """\
                `@cpt:blueprint`
                ```toml
                artifact = "R"
                kit = "k"
                toc = false
                ```
                `@/cpt:blueprint`

                `@cpt:heading`
                ```toml
                id = "h1"
                level = 1
                required = true
                multiple = false
                numbered = true
                pattern = "Title"
                description = "Main title"
                ```
                `@/cpt:heading`

                `@cpt:id`
                ```toml
                kind = "req"
                name = "Requirement"
                required = true
                headings = ["h1"]
                ```
                `@/cpt:id`
            """))
            out_path = tmp / "constraints.toml"
            result_path, errors = generate_constraints([bp], out_path)
            content = out_path.read_text(encoding="utf-8")
            self.assertIn("toc = false", content)
            self.assertIn("required = true", content)
            self.assertIn("multiple = false", content)
            self.assertIn("numbered = true", content)
            self.assertIn('headings = ["h1"]', content)


class TestProcessKit(unittest.TestCase):
    def test_process_kit_with_multiple_blueprints(self):
        with TemporaryDirectory() as td:
            tmp = Path(td)
            bp_dir = tmp / "blueprints"
            bp_dir.mkdir()
            _write_bp(bp_dir, "REQ.md", FULL_BLUEPRINT)
            _write_bp(bp_dir, "CODEBASE.md", CODEBASE_BLUEPRINT)
            config_kits = tmp / "gen_kits"
            summary, errors = process_kit("sdlc", bp_dir, config_kits)
            self.assertGreater(summary["files_written"], 0)
            self.assertIn("REQ", summary["artifact_kinds"])
            # Should have skill and workflow content from FULL_BLUEPRINT
            self.assertTrue(summary.get("skill_content", ""))
            self.assertTrue(summary.get("workflows", []))
            # Constraints should be generated
            self.assertTrue((config_kits / "sdlc" / "constraints.toml").is_file())

    def test_process_kit_no_blueprints(self):
        with TemporaryDirectory() as td:
            tmp = Path(td)
            bp_dir = tmp / "empty_bps"
            bp_dir.mkdir()
            summary, errors = process_kit("sdlc", bp_dir, tmp / "gen")
            self.assertEqual(summary["files_written"], 0)
            self.assertTrue(errors)

    def test_process_kit_with_parse_errors(self):
        with TemporaryDirectory() as td:
            tmp = Path(td)
            bp_dir = tmp / "blueprints"
            bp_dir.mkdir()
            # Blueprint with unclosed marker → parse error
            _write_bp(bp_dir, "BAD.md", """\
                `@cpt:blueprint`
                ```toml
                artifact = "BAD"
                ```
            """)
            summary, errors = process_kit("sdlc", bp_dir, tmp / "gen")
            self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
