import pytest
from pathlib import Path

from skills.cypilot.scripts.cypilot.utils.template import (
    Artifact,
    Template,
    apply_kind_constraints,
    cross_validate_artifacts,
    load_template,
    validate_artifact_file_against_template,
)

from skills.cypilot.scripts.cypilot.utils.constraints import parse_kit_constraints


def _write(path: Path, text: str) -> Path:
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def _sample_template_text(kind: str = "PRD") -> str:
    return f"""
---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: {kind}
  unknown_sections: warn
---

<!-- cpt:id:item has="priority,task" repeat="one" covered_by="DESIGN" -->
- [ ] `p1` - **ID**: `cpt-demo-item-1`
<!-- cpt:id:item -->

<!-- cpt:paragraph:summary -->
Some summary paragraph.
<!-- cpt:paragraph:summary -->

<!-- cpt:list:bullets -->
- a
- b
<!-- cpt:list:bullets -->

<!-- cpt:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- cpt:table:data -->

<!-- cpt:code:snippet -->
```
print('hi')
```
<!-- cpt:code:snippet -->

<!-- cpt:cdsl:flow -->
1. [ ] - `p1` - Do step - `inst-step-1`
<!-- cpt:cdsl:flow -->

<!-- cpt:id-ref:item-ref has="priority,task" -->
- [x] `p1` - `cpt-demo-item-1`
<!-- cpt:id-ref:item-ref -->
"""


def _good_artifact_text() -> str:
    return """
<!-- cpt:id:item -->
- [x] `p1` - **ID**: `cpt-demo-item-1`
<!-- cpt:id:item -->

<!-- cpt:paragraph:summary -->
Some summary paragraph.
<!-- cpt:paragraph:summary -->

<!-- cpt:list:bullets -->
- a
- b
<!-- cpt:list:bullets -->

<!-- cpt:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- cpt:table:data -->

<!-- cpt:code:snippet -->
```
print('hi')
```
<!-- cpt:code:snippet -->

<!-- cpt:cdsl:flow -->
1. [x] - `p1` - Do step - `inst-step-1`
<!-- cpt:cdsl:flow -->

<!-- cpt:id-ref:item-ref -->
- [x] `p1` - `cpt-demo-item-1`
<!-- cpt:id-ref:item-ref -->
"""


def test_template_build_errors_on_frontmatter(tmp_path: Path):
    bad = _write(tmp_path / "bad.template.md", "not yaml")
    tmpl, errs = load_template(bad)
    assert tmpl is None
    assert errs and errs[0]["type"] == "template"


def test_template_parses_and_validates_happy_path(tmp_path: Path):
    tmpl_path = _write(tmp_path / "ok.template.md", _sample_template_text())
    tmpl, errs = load_template(tmpl_path)
    assert errs == []
    assert isinstance(tmpl, Template)

    art_path = _write(tmp_path / "artifact.md", _good_artifact_text())
    report = tmpl.validate(art_path)
    assert report["errors"] == []

    art = tmpl.parse(art_path)
    assert set(art.list_defined()) == {"cpt-demo-item-1"}
    assert set(art.list_refs()) == {"cpt-demo-item-1"}


def test_missing_required_block_fails(tmp_path: Path):
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text())
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "artifact.md", "<!-- cpt:paragraph:summary -->\ntext\n<!-- cpt:paragraph:summary -->")
    report = tmpl.validate(art_path)
    assert any(e.get("message") == "Required block missing" for e in report["errors"])


def test_invalid_id_ref_and_table_validation(tmp_path: Path):
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text())
    tmpl, _ = load_template(tmpl_path)
    bad_art = """
<!-- cpt:id:item -->
- [ ] `p1` - **ID**: `not-an-id`
<!-- cpt:id:item -->

<!-- cpt:table:data -->
| h1 | h2 |
|----|
| onlyone |
<!-- cpt:table:data -->
"""
    art_path = _write(tmp_path / "bad.md", bad_art)
    report = tmpl.validate(art_path)
    msgs = {e.get("message") for e in report["errors"]}
    assert "Invalid ID format" in msgs or "Invalid ID ref format" in msgs
    assert "Table separator column count mismatch" in msgs or "Table row column count mismatch" in msgs or "Table must have header and separator" in msgs


def test_cross_validate_covered_by_and_refs(tmp_path: Path):
    tmpl_prd_path = _write(tmp_path / "prd.template.md", _sample_template_text("PRD"))
    # DESIGN template needs id-ref:item with has="priority,task" to match definition
    design_template = """
---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: DESIGN
  unknown_sections: warn
---

<!-- cpt:id-ref:item has="priority,task" -->
[x] `p1` - `cpt-demo-item-1`
<!-- cpt:id-ref:item -->

<!-- cpt:paragraph:summary -->
Summary
<!-- cpt:paragraph:summary -->
"""
    tmpl_design_path = _write(tmp_path / "design.template.md", design_template)
    tmpl_prd, _ = load_template(tmpl_prd_path)
    tmpl_design, _ = load_template(tmpl_design_path)

    kc, kerrs = parse_kit_constraints({
        "PRD": {
            "defined-id": [{
                "kind": "item",
                "references": {"DESIGN": {"coverage": "required"}},
            }],
        },
        "DESIGN": {
            "defined-id": [],
        },
    })
    assert kerrs == []
    assert apply_kind_constraints(tmpl_prd, kc.by_kind["PRD"]) == []
    assert apply_kind_constraints(tmpl_design, kc.by_kind["DESIGN"]) == []

    art_prd = tmpl_prd.parse(_write(tmp_path / "prd.md", _good_artifact_text()))
    art_design = tmpl_design.parse(
      _write(
        tmp_path / "design.md",
        """
<!-- cpt:id-ref:item has="priority,task" -->
[x] `p1` - `cpt-demo-item-1`
<!-- cpt:id-ref:item -->

<!-- cpt:paragraph:summary -->
Summary
<!-- cpt:paragraph:summary -->
""",
        ),
    )

    report = cross_validate_artifacts([art_prd, art_design])
    assert report["errors"] == []

    # Missing ref for covered_by should fail when DESIGN exists for same system
    # DESIGN must have at least one ID from the same system to be "in scope"
    art_design_wrong_ref = tmpl_design.parse(
      _write(
        tmp_path / "design-wrong-ref.md",
        """
<!-- cpt:id-ref:item has="priority,task" -->
[x] `p1` - `cpt-demo-item-other`
<!-- cpt:id-ref:item -->

<!-- cpt:paragraph:summary -->
Summary
<!-- cpt:paragraph:summary -->
""",
      ),
    )
    report2 = cross_validate_artifacts([art_prd, art_design_wrong_ref])
    assert any(e.get("message") == "ID not referenced from required artifact kind" for e in report2["errors"])

    # Empty DESIGN (no IDs from same system) results in warning, not error
    art_design_empty = tmpl_design.parse(
      _write(tmp_path / "design-empty.md", "<!-- cpt:paragraph:summary -->x<!-- cpt:paragraph:summary -->"),
    )
    report3 = cross_validate_artifacts([art_prd, art_design_empty])
    assert report3["errors"] == []
    assert any(w.get("message") == "Required reference target kind not in scope" for w in report3["warnings"])


def test_constraints_override_marker_attrs(tmp_path: Path):
    tmpl_text = """
---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
  unknown_sections: warn
---

<!-- cpt:id:item has="task" -->
- [ ] **ID**: `cpt-demo-item-1`
<!-- cpt:id:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.md", tmpl_text)
    tmpl, errs = load_template(tmpl_path)
    assert errs == []

    constraints_json = {
        "PRD": {
            "defined-id": [
                {
                    "kind": "item",
                    "priority": True,
                    "task": True,
                    "to_code": True,
                    "references": {
                        "DESIGN": {"coverage": "required"},
                        "SPEC": {"coverage": "required"},
                    },
                }
            ],
        }
    }
    kc, kerrs = parse_kit_constraints(constraints_json)
    assert kerrs == []
    cerrs = apply_kind_constraints(tmpl, kc.by_kind["PRD"])
    assert cerrs == []

    id_block = [b for b in tmpl.blocks if b.type == "id" and b.name == "item"][0]
    assert "priority" in (id_block.attrs.get("has") or "")
    assert "task" in (id_block.attrs.get("has") or "")
    assert id_block.attrs.get("to_code") == "true"
    assert id_block.attrs.get("covered_by") in (None, "")


def test_constraints_contradiction_reports_error(tmp_path: Path):
    tmpl_text = """
---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
  unknown_sections: warn
---

<!-- cpt:id:item has="priority" to_code="false" -->
- [ ] `p1` - **ID**: `cpt-demo-item-1`
<!-- cpt:id:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.md", tmpl_text)
    tmpl, errs = load_template(tmpl_path)
    assert errs == []

    constraints_json = {
        "PRD": {
            "defined-id": [{"kind": "item", "priority": False, "to_code": True}],
        }
    }
    kc, kerrs = parse_kit_constraints(constraints_json)
    assert kerrs == []
    cerrs = apply_kind_constraints(tmpl, kc.by_kind["PRD"])
    assert any(e.get("type") == "constraints" and e.get("message") == "Constraint contradicts template marker" for e in cerrs)


def test_cross_validate_reference_done_but_definition_not_done(tmp_path: Path):
    tmpl_prd_path = _write(tmp_path / "prd.template.md", _sample_template_text("PRD"))
    design_template = """
---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: DESIGN
  unknown_sections: warn
---

<!-- cpt:id-ref:item has="priority,task" -->
[x] `p1` - `cpt-demo-item-1`
<!-- cpt:id-ref:item -->

<!-- cpt:paragraph:summary -->
Summary
<!-- cpt:paragraph:summary -->
"""
    tmpl_design_path = _write(tmp_path / "design.template.md", design_template)
    tmpl_prd, _ = load_template(tmpl_prd_path)
    tmpl_design, _ = load_template(tmpl_design_path)

    art_prd_undone = tmpl_prd.parse(
        _write(tmp_path / "prd-undone.md", _good_artifact_text().replace("[x]", "[ ]", 1)),
    )
    art_design_done_ref = tmpl_design.parse(
        _write(
            tmp_path / "design-done-ref.md",
            """
<!-- cpt:id-ref:item has=\"priority,task\" -->
[x] `p1` - `cpt-demo-item-1`
<!-- cpt:id-ref:item -->

<!-- cpt:paragraph:summary -->
Summary
<!-- cpt:paragraph:summary -->
""",
        ),
    )
    report = cross_validate_artifacts([art_prd_undone, art_design_done_ref])
    assert any(e.get("message") == "Reference marked done but definition not done" for e in report["errors"])


def test_constraints_strict_rejects_unknown_id_kind_in_artifact(tmp_path: Path):
    tmpl_text = """
---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
  unknown_sections: warn
---

<!-- cpt:id:item -->
- [ ] **ID**: `cpt-demo-item-1`
<!-- cpt:id:item -->

<!-- cpt:id:extra -->
- [ ] **ID**: `cpt-demo-extra-1`
<!-- cpt:id:extra -->
"""
    tmpl_path = _write(tmp_path / "tmpl.md", tmpl_text)
    tmpl, errs = load_template(tmpl_path)
    assert errs == []

    kc, kerrs = parse_kit_constraints({"PRD": {"defined-id": [{"kind": "item"}]}})
    assert kerrs == []
    cerrs = apply_kind_constraints(tmpl, kc.by_kind["PRD"])
    assert cerrs == []

    art_path = _write(tmp_path / "artifact.md", _good_artifact_text() + "\n<!-- cpt:id:extra -->\n- [ ] **ID**: `cpt-demo-extra-1`\n<!-- cpt:id:extra -->\n")
    report = tmpl.validate(art_path)
    assert any(e.get("type") == "constraints" and e.get("message") == "ID kind not allowed by constraints" for e in report["errors"])


def test_constraints_strict_requires_presence_of_each_constrained_kind(tmp_path: Path):
    tmpl_text = """
---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
  unknown_sections: warn
---

<!-- cpt:id:item -->
- [ ] **ID**: `cpt-demo-item-1`
<!-- cpt:id:item -->

<!-- cpt:id:actor -->
- [ ] **ID**: `cpt-demo-actor-1`
<!-- cpt:id:actor -->
"""
    tmpl_path = _write(tmp_path / "tmpl.md", tmpl_text)
    tmpl, errs = load_template(tmpl_path)
    assert errs == []

    kc, kerrs = parse_kit_constraints({"PRD": {"defined-id": [{"kind": "item"}, {"kind": "actor"}]}})
    assert kerrs == []
    cerrs = apply_kind_constraints(tmpl, kc.by_kind["PRD"])
    assert cerrs == []

    art_path = _write(
        tmp_path / "artifact.md",
        """
<!-- cpt:id:item -->
- [ ] **ID**: `cpt-demo-item-1`
<!-- cpt:id:item -->
""",
    )
    report = tmpl.validate(art_path)
    assert any(e.get("type") == "constraints" and e.get("message") == "Required ID kind missing in artifact" and e.get("id_kind") == "actor" for e in report["errors"])


def test_constraints_strict_headings_scope_for_definitions(tmp_path: Path):
    tmpl_text = """
---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
  unknown_sections: warn
---

<!-- cpt:id:item -->
- [ ] **ID**: `cpt-demo-item-1`
<!-- cpt:id:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.md", tmpl_text)
    tmpl, errs = load_template(tmpl_path)
    assert errs == []

    kc, kerrs = parse_kit_constraints({"PRD": {"defined-id": [{"kind": "item", "headings": ["Good"]}]}})
    assert kerrs == []
    cerrs = apply_kind_constraints(tmpl, kc.by_kind["PRD"])
    assert cerrs == []

    art_path = _write(
        tmp_path / "artifact.md",
        """
# Bad

<!-- cpt:id:item -->
- [ ] **ID**: `cpt-demo-item-1`
<!-- cpt:id:item -->
""",
    )
    report = tmpl.validate(art_path)
    assert any(e.get("type") == "constraints" and e.get("message") == "ID definition not under required headings" for e in report["errors"])


# === Additional coverage tests ===


def test_parse_scalar_boolean_and_int():
    """Cover parse_scalar with true/false and integers."""
    assert Template.parse_scalar("true") is True
    assert Template.parse_scalar("false") is False
    assert Template.parse_scalar("42") == 42
    assert Template.parse_scalar("-5") == -5
    assert Template.parse_scalar("hello") == "hello"


def test_first_nonempty_all_empty():
    """Cover first_nonempty returning None."""
    result = Template.first_nonempty(["", "   ", "\t"])
    assert result is None


def test_frontmatter_no_closing_marker(tmp_path: Path):
    """Cover frontmatter without closing ---."""
    bad = _write(tmp_path / "bad.template.md", "---\ncypilot-template:\n  kind: X")
    tmpl, errs = load_template(bad)
    assert tmpl is None
    assert errs


def test_frontmatter_invalid_indentation(tmp_path: Path):
    """Cover invalid frontmatter indentation."""
    bad = _write(tmp_path / "bad.template.md", "---\ncypilot-template:\n   kind: X\n---")
    tmpl, errs = load_template(bad)
    assert tmpl is None
    assert any("indentation" in str(e.get("message", "")).lower() for e in errs)


def test_frontmatter_invalid_line(tmp_path: Path):
    """Cover invalid frontmatter line (no colon)."""
    bad = _write(tmp_path / "bad.template.md", "---\ncypilot-template:\n  invalid line no colon\n---")
    tmpl, errs = load_template(bad)
    assert tmpl is None


def test_frontmatter_comment_line_ignored(tmp_path: Path):
    """Cover frontmatter with comment lines."""
    text = """---
cypilot-template:
  # this is a comment
  version:
    major: 1
    minor: 0
  kind: TEST
---
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, errs = load_template(tmpl_path)
    assert errs == []
    assert tmpl is not None


def test_template_missing_kind(tmp_path: Path):
    """Cover template missing kind."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
---
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, errs = load_template(tmpl_path)
    assert tmpl is None
    assert any("kind" in str(e.get("message", "")).lower() for e in errs)


def test_template_missing_version(tmp_path: Path):
    """Cover template missing version - now uses default version."""
    text = """---
cypilot-template:
  kind: TEST
---
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, errs = load_template(tmpl_path)
    # Now succeeds with default version (frontmatter is optional, version defaults to SUPPORTED_VERSION)
    assert tmpl is not None
    assert errs == []
    assert tmpl.kind == "TEST"
    assert tmpl.version.major == 2  # default from SUPPORTED_VERSION
    assert tmpl.version.minor == 0


def test_template_invalid_unknown_sections(tmp_path: Path):
    """Cover invalid unknown_sections value - now falls back to 'warn'."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
  unknown_sections: invalid
---
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, errs = load_template(tmpl_path)
    # Now succeeds with fallback to 'warn' (frontmatter values are optional)
    assert tmpl is not None
    assert errs == []
    assert tmpl.kind == "TEST"
    assert tmpl.policy.unknown_sections == "warn"  # fallback value


def test_template_version_too_high(tmp_path: Path):
    """Cover template version higher than supported."""
    text = """---
cypilot-template:
  version:
    major: 99
    minor: 0
  kind: TEST
---
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, errs = load_template(tmpl_path)
    assert tmpl is None
    assert any("version" in str(e.get("message", "")).lower() for e in errs)


def test_template_unclosed_marker(tmp_path: Path):
    """Cover unclosed marker in template."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:paragraph:summary -->
Content without closing marker
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, errs = load_template(tmpl_path)
    assert tmpl is None
    assert any("unclosed" in str(e.get("message", "")).lower() for e in errs)


def test_template_unknown_marker_type(tmp_path: Path):
    """Cover unknown marker type in template - should fail loading."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:line:summary -->
Content with unknown type
<!-- cpt:line:summary -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, errs = load_template(tmpl_path)
    assert tmpl is None
    assert any("unknown marker type" in str(e.get("message", "")).lower() for e in errs)
    assert any(e.get("marker_type") == "line" for e in errs)


def test_block_validation_free_type(tmp_path: Path):
    """Cover free block type (no validation)."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:free:anything -->
Any content here
<!-- cpt:free:anything -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:free:anything -->\nstuff\n<!-- cpt:free:anything -->")
    report = tmpl.validate(art_path)
    assert report["errors"] == []


def test_block_validation_id_empty(tmp_path: Path):
    """Cover ID block with empty content."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:id:item -->
- [ ] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:id:item -->\n<!-- cpt:id:item -->")
    report = tmpl.validate(art_path)
    assert any("ID block missing content" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_id_ref_empty(tmp_path: Path):
    """Cover ID ref block with empty content."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:id-ref:item -->
[x] - `cpt-test-1`
<!-- cpt:id-ref:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:id-ref:item -->\n<!-- cpt:id-ref:item -->")
    report = tmpl.validate(art_path)
    assert any("ID ref block missing content" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_id_ref_invalid_format(tmp_path: Path):
    """Cover ID ref with invalid format."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:id-ref:item -->
[x] - `cpt-test-1`
<!-- cpt:id-ref:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:id-ref:item -->\ninvalid-ref\n<!-- cpt:id-ref:item -->")
    report = tmpl.validate(art_path)
    assert any("Invalid ID ref format" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_list_empty(tmp_path: Path):
    """Cover empty list block."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:list:items -->
- item
<!-- cpt:list:items -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:list:items -->\n<!-- cpt:list:items -->")
    report = tmpl.validate(art_path)
    assert any("List block empty" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_list_not_bullet(tmp_path: Path):
    """Cover list block without bullet format."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:list:items -->
- item
<!-- cpt:list:items -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:list:items -->\nnot a bullet\n<!-- cpt:list:items -->")
    report = tmpl.validate(art_path)
    assert any("Expected bullet list" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_numbered_list_invalid(tmp_path: Path):
    """Cover numbered-list with non-numbered content."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:numbered-list:steps -->
1. step
<!-- cpt:numbered-list:steps -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:numbered-list:steps -->\nnot numbered\n<!-- cpt:numbered-list:steps -->")
    report = tmpl.validate(art_path)
    assert any("Expected numbered list" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_task_list_invalid(tmp_path: Path):
    """Cover task-list with invalid format."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:task-list:tasks -->
- [ ] task
<!-- cpt:task-list:tasks -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:task-list:tasks -->\nnot a task\n<!-- cpt:task-list:tasks -->")
    report = tmpl.validate(art_path)
    assert any("Expected task list" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_task_list_missing_priority(tmp_path: Path):
    """Cover task-list with priority requirement but missing priority."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:task-list:tasks has="priority" -->
- [ ] `p1` task
<!-- cpt:task-list:tasks -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:task-list:tasks -->\n- [ ] task without priority\n<!-- cpt:task-list:tasks -->")
    report = tmpl.validate(art_path)
    assert any("Task item missing priority" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_table_too_few_rows(tmp_path: Path):
    """Cover table with less than 2 rows."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- cpt:table:data -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:table:data -->\n| only header |\n<!-- cpt:table:data -->")
    report = tmpl.validate(art_path)
    assert any("Table must have header and separator" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_table_invalid_header(tmp_path: Path):
    """Cover table with invalid header."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- cpt:table:data -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:table:data -->\nno pipes\nalso no pipes\n<!-- cpt:table:data -->")
    report = tmpl.validate(art_path)
    assert any("Invalid table" in str(e.get("message", "")) or "Table must have" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_table_no_data_rows(tmp_path: Path):
    """Cover table with no data rows."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- cpt:table:data -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:table:data -->\n| h1 | h2 |\n|----|----|<!-- cpt:table:data -->")
    report = tmpl.validate(art_path)
    # Should fail due to no data rows or format issues
    assert len(report["errors"]) > 0


def test_block_validation_table_row_mismatch(tmp_path: Path):
    """Cover table with row column mismatch."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- cpt:table:data -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:table:data -->\n| h1 | h2 |\n|----|----|---|\n| v1 |\n<!-- cpt:table:data -->")
    report = tmpl.validate(art_path)
    assert any("mismatch" in str(e.get("message", "")).lower() for e in report["errors"])


def test_block_validation_paragraph_empty(tmp_path: Path):
    """Cover empty paragraph block."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:paragraph:summary -->
Some text
<!-- cpt:paragraph:summary -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:paragraph:summary -->\n\n<!-- cpt:paragraph:summary -->")
    report = tmpl.validate(art_path)
    assert any("Paragraph block empty" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_code_no_fence(tmp_path: Path):
    """Cover code block without opening fence."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:code:snippet -->
```
code
```
<!-- cpt:code:snippet -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:code:snippet -->\nnot a fence\n<!-- cpt:code:snippet -->")
    report = tmpl.validate(art_path)
    assert any("Code block must start with" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_code_unclosed_fence(tmp_path: Path):
    """Cover code block with unclosed fence."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:code:snippet -->
```
code
```
<!-- cpt:code:snippet -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:code:snippet -->\n```\ncode without closing\n<!-- cpt:code:snippet -->")
    report = tmpl.validate(art_path)
    assert any("Code fence must be closed" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_heading(tmp_path: Path):
    """Cover heading block validation."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:##:section -->
## Heading
<!-- cpt:##:section -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    # Wrong heading level
    art_path = _write(tmp_path / "art.md", "<!-- cpt:##:section -->\n# Wrong level\n<!-- cpt:##:section -->")
    report = tmpl.validate(art_path)
    assert any("Heading level mismatch" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_heading_empty(tmp_path: Path):
    """Cover empty heading block."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:##:section -->
## Heading
<!-- cpt:##:section -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:##:section -->\n\n<!-- cpt:##:section -->")
    report = tmpl.validate(art_path)
    assert any("Heading block empty" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_link_invalid(tmp_path: Path):
    """Cover invalid link block."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:link:ref -->
[text](url)
<!-- cpt:link:ref -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:link:ref -->\nnot a link\n<!-- cpt:link:ref -->")
    report = tmpl.validate(art_path)
    assert any("Invalid link" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_image_invalid(tmp_path: Path):
    """Cover invalid image block."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:image:pic -->
![alt](url)
<!-- cpt:image:pic -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:image:pic -->\nnot an image\n<!-- cpt:image:pic -->")
    report = tmpl.validate(art_path)
    assert any("Invalid image" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_cdsl_empty(tmp_path: Path):
    """Cover empty CDSL block."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:cdsl:flow -->
1. [ ] - `p1` - Step - `inst-1`
<!-- cpt:cdsl:flow -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:cdsl:flow -->\n\n<!-- cpt:cdsl:flow -->")
    report = tmpl.validate(art_path)
    assert any("CDSL block empty" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_cdsl_invalid_line(tmp_path: Path):
    """Cover CDSL block with invalid line."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:cdsl:flow -->
1. [ ] - `p1` - Step - `inst-1`
<!-- cpt:cdsl:flow -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:cdsl:flow -->\ninvalid cdsl line\n<!-- cpt:cdsl:flow -->")
    report = tmpl.validate(art_path)
    assert any("Invalid CDSL line" in str(e.get("message", "")) for e in report["errors"])


def test_validate_artifact_file_against_template_success(tmp_path: Path):
    """Cover validate_artifact_file_against_template success."""
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text())
    art_path = _write(tmp_path / "art.md", _good_artifact_text())
    report = validate_artifact_file_against_template(art_path, tmpl_path)
    assert report["errors"] == []


def test_validate_artifact_file_against_template_kind_mismatch(tmp_path: Path):
    """Cover validate_artifact_file_against_template kind mismatch."""
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text("PRD"))
    art_path = _write(tmp_path / "art.md", _good_artifact_text())
    report = validate_artifact_file_against_template(art_path, tmpl_path, expected_kind="DESIGN")
    assert any("Kind mismatch" in str(e.get("message", "")) for e in report["errors"])


def test_validate_artifact_file_against_template_bad_template(tmp_path: Path):
    """Cover validate_artifact_file_against_template with bad template."""
    tmpl_path = _write(tmp_path / "bad.template.md", "not a template")
    art_path = _write(tmp_path / "art.md", "anything")
    report = validate_artifact_file_against_template(art_path, tmpl_path)
    assert len(report["errors"]) > 0


def test_artifact_unclosed_marker(tmp_path: Path):
    """Cover unclosed marker in artifact."""
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text())
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:paragraph:summary -->\nunclosed")
    report = tmpl.validate(art_path)
    assert any("Unclosed marker" in str(e.get("message", "")) for e in report["errors"])


def test_artifact_unknown_marker_warning(tmp_path: Path):
    """Cover unknown marker producing error (unknown markers are always errors, regardless of unknown_sections policy)."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
  unknown_sections: warn
---
<!-- cpt:paragraph:known -->
text
<!-- cpt:paragraph:known -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:paragraph:known -->\ntext\n<!-- cpt:paragraph:known -->\n<!-- cpt:paragraph:unknown -->\ntext\n<!-- cpt:paragraph:unknown -->")
    report = tmpl.validate(art_path)
    # Unknown markers are always errors (unknown_sections policy applies only to markdown sections without markers)
    assert any("Unknown marker" in str(e.get("message", "")) for e in report["errors"])


def test_artifact_unknown_marker_error(tmp_path: Path):
    """Cover unknown marker producing error when policy is error."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
  unknown_sections: error
---
<!-- cpt:paragraph:known -->
text
<!-- cpt:paragraph:known -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:paragraph:known -->\ntext\n<!-- cpt:paragraph:known -->\n<!-- cpt:paragraph:unknown -->\ntext\n<!-- cpt:paragraph:unknown -->")
    report = tmpl.validate(art_path)
    assert any("Unknown marker" in str(e.get("message", "")) for e in report["errors"])


def test_artifact_block_repeat_once_violation(tmp_path: Path):
    """Cover block appearing more than once when repeat=one."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:paragraph:unique repeat="one" -->
text
<!-- cpt:paragraph:unique -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:paragraph:unique -->\ntext\n<!-- cpt:paragraph:unique -->\n<!-- cpt:paragraph:unique -->\ntext2\n<!-- cpt:paragraph:unique -->")
    report = tmpl.validate(art_path)
    assert any("Block must appear once" in str(e.get("message", "")) for e in report["errors"])


def test_artifact_read_failure(tmp_path: Path):
    """Cover artifact read failure."""
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text())
    tmpl, _ = load_template(tmpl_path)
    nonexistent = tmp_path / "nonexistent.md"
    report = tmpl.validate(nonexistent)
    assert any("Failed to read" in str(e.get("message", "")) for e in report["errors"])


def test_template_read_failure(tmp_path: Path):
    """Cover template file read failure."""
    nonexistent = tmp_path / "nonexistent.template.md"
    tmpl, errs = load_template(nonexistent)
    assert tmpl is None
    assert any("Failed to read" in str(e.get("message", "")) for e in errs)


def test_artifact_get_and_list_methods(tmp_path: Path):
    """Cover Artifact.get and Artifact.list methods."""
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text())
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", _good_artifact_text())
    art = tmpl.parse(art_path)

    # Test get method
    result = art.get("cpt-demo-item-1")
    assert result is not None
    assert "cpt-demo-item-1" in result

    # Test get with nonexistent ID
    result2 = art.get("nonexistent-id")
    assert result2 is None

    # Test list method
    results = art.list(["cpt-demo-item-1", "nonexistent"])
    assert len(results) == 2
    assert results[0] is not None
    assert results[1] is None


def test_artifact_list_ids(tmp_path: Path):
    """Cover Artifact.list_ids method."""
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text())
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", _good_artifact_text())
    art = tmpl.parse(art_path)

    ids = art.list_ids()
    assert "cpt-demo-item-1" in ids


def test_id_task_status_all_done_but_id_not_marked(tmp_path: Path):
    """Cover ID task status validation - all tasks done but ID not marked."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:id:item has="task" -->
- [ ] `p1` - **ID**: `cpt-test-1`
<!-- cpt:task-list:tasks -->
- [x] task
<!-- cpt:task-list:tasks -->
<!-- cpt:id:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_text = """<!-- cpt:id:item -->
- [ ] `p1` - **ID**: `cpt-test-1`
<!-- cpt:task-list:tasks -->
- [x] all done
<!-- cpt:task-list:tasks -->
<!-- cpt:id:item -->
"""
    art_path = _write(tmp_path / "art.md", art_text)
    report = tmpl.validate(art_path)
    assert any("All tasks done but ID not marked done" in str(e.get("message", "")) for e in report["errors"])


def test_id_task_status_id_done_but_tasks_not(tmp_path: Path):
    """Cover ID task status validation - ID marked done but tasks not all done."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:id:item has="task" -->
- [x] `p1` - **ID**: `cpt-test-1`
<!-- cpt:task-list:tasks -->
- [ ] task
<!-- cpt:task-list:tasks -->
<!-- cpt:id:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_text = """<!-- cpt:id:item -->
- [x] `p1` - **ID**: `cpt-test-1`
<!-- cpt:task-list:tasks -->
- [ ] not done
<!-- cpt:task-list:tasks -->
<!-- cpt:id:item -->
"""
    art_path = _write(tmp_path / "art.md", art_text)
    report = tmpl.validate(art_path)
    assert any("ID marked done but tasks not all done" in str(e.get("message", "")) for e in report["errors"])


def test_cross_validate_ref_no_definition(tmp_path: Path):
    """Cover cross validation when reference has no definition."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:id-ref:item -->
[x] - `cpt-test-1`
<!-- cpt:id-ref:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- cpt:id-ref:item -->\n[x] - `cpt-nonexistent`\n<!-- cpt:id-ref:item -->")
    art = tmpl.parse(art_path)
    report = cross_validate_artifacts([art])
    assert any("Reference has no definition" in str(e.get("message", "")) for e in report["errors"])


def test_artifact_with_template_frontmatter_detected(tmp_path: Path):
    """Cover detection of template frontmatter in artifact (should error)."""
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text())
    tmpl, _ = load_template(tmpl_path)

    # Artifact should NOT have cypilot-template frontmatter
    bad_artifact = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:paragraph:summary -->
Some content
<!-- cpt:paragraph:summary -->
"""
    art_path = _write(tmp_path / "bad-artifact.md", bad_artifact)
    report = tmpl.validate(art_path)
    assert any("template frontmatter" in str(e.get("message", "")).lower() for e in report["errors"])


def test_artifact_without_template_frontmatter_ok(tmp_path: Path):
    """Cover that normal frontmatter (without cypilot-template) is OK."""
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text())
    tmpl, _ = load_template(tmpl_path)

    # Normal YAML frontmatter is fine
    ok_artifact = """---
title: My Document
author: Test
---
<!-- cpt:id:item -->
- [x] `p1` - **ID**: `cpt-demo-item-1`
<!-- cpt:id:item -->
<!-- cpt:paragraph:summary -->
Some content
<!-- cpt:paragraph:summary -->
<!-- cpt:list:bullets -->
- a
<!-- cpt:list:bullets -->
<!-- cpt:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- cpt:table:data -->
<!-- cpt:code:snippet -->
```
code
```
<!-- cpt:code:snippet -->
<!-- cpt:cdsl:flow -->
1. [x] - `p1` - Step - `inst-step-1`
<!-- cpt:cdsl:flow -->
"""
    art_path = _write(tmp_path / "ok-artifact.md", ok_artifact)
    report = tmpl.validate(art_path)
    # Should not have the template frontmatter error
    assert not any("template frontmatter" in str(e.get("message", "")).lower() for e in report["errors"])


def test_cross_validate_external_system_ref_no_error(tmp_path: Path):
    """External system references should not error when registered_systems is provided."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:id:item -->
**ID**: `cpt-myapp-item-1`
<!-- cpt:id:item -->
<!-- cpt:id-ref:ref -->
`cpt-other-system-spec-auth`
<!-- cpt:id-ref:ref -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", """<!-- cpt:id:item -->
**ID**: `cpt-myapp-item-1`
<!-- cpt:id:item -->
<!-- cpt:id-ref:ref -->
`cpt-other-system-spec-auth`
<!-- cpt:id-ref:ref -->
""")
    art = tmpl.parse(art_path)
    # With registered_systems containing only "myapp", "other-system" is external
    report = cross_validate_artifacts([art], registered_systems={"myapp"})
    # Should NOT have "Reference has no definition" error for external system
    ref_errors = [e for e in report["errors"] if "Reference has no definition" in str(e.get("message", ""))]
    assert len(ref_errors) == 0


def test_cross_validate_internal_system_ref_errors(tmp_path: Path):
    """Internal system references without definition should error."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- cpt:id:item -->
**ID**: `cpt-myapp-item-1`
<!-- cpt:id:item -->
<!-- cpt:id-ref:ref -->
`cpt-myapp-missing-thing`
<!-- cpt:id-ref:ref -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", """<!-- cpt:id:item -->
**ID**: `cpt-myapp-item-1`
<!-- cpt:id:item -->
<!-- cpt:id-ref:ref -->
`cpt-myapp-missing-thing`
<!-- cpt:id-ref:ref -->
""")
    art = tmpl.parse(art_path)
    # With registered_systems containing "myapp", internal ref without def should error
    report = cross_validate_artifacts([art], registered_systems={"myapp"})
    ref_errors = [e for e in report["errors"] if "Reference has no definition" in str(e.get("message", ""))]
    assert len(ref_errors) == 1
    assert "cpt-myapp-missing-thing" in str(ref_errors[0])


def test_cross_validate_multi_word_system_external(tmp_path: Path):
    """Multi-word system names should be handled correctly."""
    text = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: SPEC
---
<!-- cpt:id:item -->
**ID**: `cpt-account-server-spec-billing`
<!-- cpt:id:item -->
<!-- cpt:id-ref:ref -->
`cpt-other-app-spec-auth`
<!-- cpt:id-ref:ref -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", """<!-- cpt:id:item -->
**ID**: `cpt-account-server-spec-billing`
<!-- cpt:id:item -->
<!-- cpt:id-ref:ref -->
`cpt-other-app-spec-auth`
<!-- cpt:id-ref:ref -->
""")
    art = tmpl.parse(art_path)
    # "account-server" is registered, "other-app" is external
    report = cross_validate_artifacts([art], registered_systems={"account-server"})
    ref_errors = [e for e in report["errors"] if "Reference has no definition" in str(e.get("message", ""))]
    assert len(ref_errors) == 0  # external ref should not error


def test_cross_validate_ref_has_attribute_is_optional(tmp_path: Path):
    """Reference decides its own has= attributes; not required to match definition."""
    # Definition template with has="priority,task"
    def_tmpl = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: DEF
  unknown_sections: warn
---
<!-- cpt:id:item has="priority,task" -->
- [ ] `p1` - **ID**: `cpt-test-item-1`
<!-- cpt:id:item -->
"""
    # Reference template WITHOUT has attribute (should pass - ref decides its own attrs)
    ref_tmpl_simple = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: REF
  unknown_sections: warn
---
<!-- cpt:id-ref:item -->
`cpt-test-item-1`
<!-- cpt:id-ref:item -->
"""
    # Reference template WITH has attribute (should also pass)
    ref_tmpl_full = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: REF
  unknown_sections: warn
---
<!-- cpt:id-ref:item has="priority,task" -->
[ ] `p1` - `cpt-test-item-1`
<!-- cpt:id-ref:item -->
"""
    def_tmpl_path = _write(tmp_path / "def.template.md", def_tmpl)
    ref_tmpl_simple_path = _write(tmp_path / "ref-simple.template.md", ref_tmpl_simple)
    ref_tmpl_full_path = _write(tmp_path / "ref-full.template.md", ref_tmpl_full)

    tmpl_def, _ = load_template(def_tmpl_path)
    tmpl_ref_simple, _ = load_template(ref_tmpl_simple_path)
    tmpl_ref_full, _ = load_template(ref_tmpl_full_path)

    art_def = tmpl_def.parse(
      _write(tmp_path / "def.md", """<!-- cpt:id:item -->
- [ ] `p1` - **ID**: `cpt-test-item-1`
<!-- cpt:id:item -->"""),
    )

    # Reference without has attribute should pass (ref decides its own attrs)
    art_ref_simple = tmpl_ref_simple.parse(
      _write(tmp_path / "ref-simple.md", """<!-- cpt:id-ref:item -->
`cpt-test-item-1`
<!-- cpt:id-ref:item -->"""),
    )
    report_simple = cross_validate_artifacts([art_def, art_ref_simple])
    assert not any("Reference missing" in str(e.get("message", "")) for e in report_simple["errors"])

    # Reference with has attribute should also pass
    art_ref_full = tmpl_ref_full.parse(
      _write(tmp_path / "ref-full.md", """<!-- cpt:id-ref:item has="priority,task" -->
[ ] `p1` - `cpt-test-item-1`
<!-- cpt:id-ref:item -->"""),
    )
    report_full = cross_validate_artifacts([art_def, art_ref_full])
    assert not any("Reference missing" in str(e.get("message", "")) for e in report_full["errors"])


def test_nesting_validation_errors_on_wrong_parent(tmp_path: Path):
    """Nesting validation should error when artifact block has wrong parent."""
    # Template with nested structure: ##:outer contains ##:inner
    template_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
  unknown_sections: warn
---
<!-- cpt:##:outer -->
## Outer
<!-- cpt:##:inner -->
### Inner
<!-- cpt:##:inner -->
<!-- cpt:##:outer -->
"""
    # Artifact with correct nesting
    artifact_correct = """<!-- cpt:##:outer -->
## Outer
<!-- cpt:##:inner -->
### Inner
<!-- cpt:##:inner -->
<!-- cpt:##:outer -->"""

    # Artifact with WRONG nesting (inner NOT inside outer)
    artifact_wrong = """<!-- cpt:##:outer -->
## Outer
<!-- cpt:##:outer -->
<!-- cpt:##:inner -->
### Inner
<!-- cpt:##:inner -->"""

    tmpl_path = _write(tmp_path / "test.template.md", template_content)
    tmpl, _ = load_template(tmpl_path)

    # Correct nesting should pass with no nesting errors
    art_correct = tmpl.parse(
      _write(tmp_path / "correct.md", artifact_correct),
    )
    report_correct = art_correct.validate()
    nesting_errors = [e for e in report_correct["errors"] if e.get("type") == "nesting"]
    assert len(nesting_errors) == 0

    # Wrong nesting should produce nesting errors
    art_wrong = tmpl.parse(
      _write(tmp_path / "wrong.md", artifact_wrong),
    )
    report_wrong = art_wrong.validate()
    nesting_errors_wrong = [e for e in report_wrong["errors"] if e.get("type") == "nesting"]
    assert len(nesting_errors_wrong) > 0
    assert any("must be nested inside" in str(e.get("message", "")) for e in nesting_errors_wrong)


def test_nesting_validation_skips_repeat_many_parents(tmp_path: Path):
    """Nesting validation should skip blocks inside repeat='many' parents."""
    # Template with repeat="many" outer block
    template_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: TEST
  unknown_sections: warn
---
<!-- cpt:##:section repeat="many" -->
## Section
<!-- cpt:paragraph:content -->
Content here
<!-- cpt:paragraph:content -->
<!-- cpt:##:section -->
"""
    # Artifact with different nesting (paragraph directly inside section is fine)
    artifact = """<!-- cpt:##:section repeat="many" -->
## Section 1
<!-- cpt:paragraph:content -->
Content here
<!-- cpt:paragraph:content -->
<!-- cpt:##:section -->"""

    tmpl_path = _write(tmp_path / "test.template.md", template_content)
    tmpl, _ = load_template(tmpl_path)

    art = tmpl.parse(
      _write(tmp_path / "art.md", artifact),
    )
    report = art.validate()
    nesting_errors = [e for e in report["errors"] if e.get("type") == "nesting"]
    # Should have no nesting errors because parent has repeat="many"
    assert len(nesting_errors) == 0
