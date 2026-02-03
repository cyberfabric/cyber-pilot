import pytest
from pathlib import Path

from skills.spider.scripts.spider.utils.template import (
    Artifact,
    Template,
    cross_validate_artifacts,
    load_template,
    validate_artifact_file_against_template,
)


def _write(path: Path, text: str) -> Path:
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def _sample_template_text(kind: str = "PRD") -> str:
    return f"""
---
spider-template:
  version:
    major: 1
    minor: 0
  kind: {kind}
  unknown_sections: warn
---

<!-- spd:id:item has="priority,task" repeat="one" covered_by="DESIGN" -->
- [ ] `p1` - **ID**: `spd-demo-item-1`
<!-- spd:id:item -->

<!-- spd:paragraph:summary -->
Some summary paragraph.
<!-- spd:paragraph:summary -->

<!-- spd:list:bullets -->
- a
- b
<!-- spd:list:bullets -->

<!-- spd:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- spd:table:data -->

<!-- spd:code:snippet -->
```
print('hi')
```
<!-- spd:code:snippet -->

<!-- spd:fdl:flow -->
1. [ ] - `ph-1` - Do step - `inst-step-1`
<!-- spd:fdl:flow -->

<!-- spd:id-ref:item-ref has="priority,task" -->
[x] `p1` - `spd-demo-item-1`
<!-- spd:id-ref:item-ref -->
"""


def _good_artifact_text() -> str:
    return """
<!-- spd:id:item -->
- [x] `p1` - **ID**: `spd-demo-item-1`
<!-- spd:id:item -->

<!-- spd:paragraph:summary -->
Some summary paragraph.
<!-- spd:paragraph:summary -->

<!-- spd:list:bullets -->
- a
- b
<!-- spd:list:bullets -->

<!-- spd:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- spd:table:data -->

<!-- spd:code:snippet -->
```
print('hi')
```
<!-- spd:code:snippet -->

<!-- spd:fdl:flow -->
1. [x] - `ph-1` - Do step - `inst-step-1`
<!-- spd:fdl:flow -->

<!-- spd:id-ref:item-ref -->
[x] `p1` - `spd-demo-item-1`
<!-- spd:id-ref:item-ref -->
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
    assert set(art.list_defined()) == {"spd-demo-item-1"}
    assert set(art.list_refs()) == {"spd-demo-item-1"}


def test_missing_required_block_fails(tmp_path: Path):
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text())
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "artifact.md", "<!-- spd:paragraph:summary -->\ntext\n<!-- spd:paragraph:summary -->")
    report = tmpl.validate(art_path)
    assert any(e.get("message") == "Required block missing" for e in report["errors"])


def test_invalid_id_ref_and_table_validation(tmp_path: Path):
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text())
    tmpl, _ = load_template(tmpl_path)
    bad_art = """
<!-- spd:id:item -->
- [ ] `p1` - **ID**: `not-an-id`
<!-- spd:id:item -->

<!-- spd:table:data -->
| h1 | h2 |
|----|
| onlyone |
<!-- spd:table:data -->
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
spider-template:
  version:
    major: 1
    minor: 0
  kind: DESIGN
  unknown_sections: warn
---

<!-- spd:id-ref:item has="priority,task" -->
[x] `p1` - `spd-demo-item-1`
<!-- spd:id-ref:item -->

<!-- spd:paragraph:summary -->
Summary
<!-- spd:paragraph:summary -->
"""
    tmpl_design_path = _write(tmp_path / "design.template.md", design_template)
    tmpl_prd, _ = load_template(tmpl_prd_path)
    tmpl_design, _ = load_template(tmpl_design_path)

    art_prd = tmpl_prd.parse(_write(tmp_path / "prd.md", _good_artifact_text()))
    art_design = tmpl_design.parse(
      _write(
        tmp_path / "design.md",
        """
<!-- spd:id-ref:item has="priority,task" -->
[x] `p1` - `spd-demo-item-1`
<!-- spd:id-ref:item -->

<!-- spd:paragraph:summary -->
Summary
<!-- spd:paragraph:summary -->
""",
        ),
    )

    report = cross_validate_artifacts([art_prd, art_design])
    assert report["errors"] == []

    # Missing ref for covered_by should fail
    art_design_empty = tmpl_design.parse(
      _write(tmp_path / "design-empty.md", "<!-- spd:paragraph:summary -->x<!-- spd:paragraph:summary -->"),
    )
    report2 = cross_validate_artifacts([art_prd, art_design_empty])
    assert any(e.get("message") == "ID not covered by required artifact kinds" for e in report2["errors"])

    # Ref done but def not done should fail
    art_prd_undone = tmpl_prd.parse(
      _write(
        tmp_path / "prd-undone.md",
        _good_artifact_text().replace("[x]", "[ ]", 1),
      ),
    )
    art_design_done_ref = tmpl_design.parse(
      _write(
        tmp_path / "design-done-ref.md",
        """
<!-- spd:id-ref:item has="priority,task" -->
[x] `p1` - `spd-demo-item-1`
<!-- spd:id-ref:item -->

<!-- spd:paragraph:summary -->
Summary
<!-- spd:paragraph:summary -->
""",
        ),
    )
    report3 = cross_validate_artifacts([art_prd_undone, art_design_done_ref])
    assert any(e.get("message") == "Reference marked done but definition not done" for e in report3["errors"])


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
    bad = _write(tmp_path / "bad.template.md", "---\nspider-template:\n  kind: X")
    tmpl, errs = load_template(bad)
    assert tmpl is None
    assert errs


def test_frontmatter_invalid_indentation(tmp_path: Path):
    """Cover invalid frontmatter indentation."""
    bad = _write(tmp_path / "bad.template.md", "---\nspider-template:\n   kind: X\n---")
    tmpl, errs = load_template(bad)
    assert tmpl is None
    assert any("indentation" in str(e.get("message", "")).lower() for e in errs)


def test_frontmatter_invalid_line(tmp_path: Path):
    """Cover invalid frontmatter line (no colon)."""
    bad = _write(tmp_path / "bad.template.md", "---\nspider-template:\n  invalid line no colon\n---")
    tmpl, errs = load_template(bad)
    assert tmpl is None


def test_frontmatter_comment_line_ignored(tmp_path: Path):
    """Cover frontmatter with comment lines."""
    text = """---
spider-template:
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
spider-template:
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
    """Cover template missing version."""
    text = """---
spider-template:
  kind: TEST
---
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, errs = load_template(tmpl_path)
    assert tmpl is None
    assert any("version" in str(e.get("message", "")).lower() for e in errs)


def test_template_invalid_unknown_sections(tmp_path: Path):
    """Cover invalid unknown_sections value."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
  unknown_sections: invalid
---
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, errs = load_template(tmpl_path)
    assert tmpl is None
    assert any("unknown_sections" in str(e.get("message", "")).lower() for e in errs)


def test_template_version_too_high(tmp_path: Path):
    """Cover template version higher than supported."""
    text = """---
spider-template:
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
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:paragraph:summary -->
Content without closing marker
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, errs = load_template(tmpl_path)
    assert tmpl is None
    assert any("unclosed" in str(e.get("message", "")).lower() for e in errs)


def test_template_unknown_marker_type(tmp_path: Path):
    """Cover unknown marker type in template - should fail loading."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:line:summary -->
Content with unknown type
<!-- spd:line:summary -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, errs = load_template(tmpl_path)
    assert tmpl is None
    assert any("unknown marker type" in str(e.get("message", "")).lower() for e in errs)
    assert any(e.get("marker_type") == "line" for e in errs)


def test_block_validation_free_type(tmp_path: Path):
    """Cover free block type (no validation)."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:free:anything -->
Any content here
<!-- spd:free:anything -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:free:anything -->\nstuff\n<!-- spd:free:anything -->")
    report = tmpl.validate(art_path)
    assert report["errors"] == []


def test_block_validation_id_empty(tmp_path: Path):
    """Cover ID block with empty content."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:id:item -->
- [ ] `p1` - **ID**: `spd-test-1`
<!-- spd:id:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:id:item -->\n<!-- spd:id:item -->")
    report = tmpl.validate(art_path)
    assert any("ID block missing content" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_id_ref_empty(tmp_path: Path):
    """Cover ID ref block with empty content."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:id-ref:item -->
[x] - `spd-test-1`
<!-- spd:id-ref:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:id-ref:item -->\n<!-- spd:id-ref:item -->")
    report = tmpl.validate(art_path)
    assert any("ID ref block missing content" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_id_ref_invalid_format(tmp_path: Path):
    """Cover ID ref with invalid format."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:id-ref:item -->
[x] - `spd-test-1`
<!-- spd:id-ref:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:id-ref:item -->\ninvalid-ref\n<!-- spd:id-ref:item -->")
    report = tmpl.validate(art_path)
    assert any("Invalid ID ref format" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_list_empty(tmp_path: Path):
    """Cover empty list block."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:list:items -->
- item
<!-- spd:list:items -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:list:items -->\n<!-- spd:list:items -->")
    report = tmpl.validate(art_path)
    assert any("List block empty" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_list_not_bullet(tmp_path: Path):
    """Cover list block without bullet format."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:list:items -->
- item
<!-- spd:list:items -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:list:items -->\nnot a bullet\n<!-- spd:list:items -->")
    report = tmpl.validate(art_path)
    assert any("Expected bullet list" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_numbered_list_invalid(tmp_path: Path):
    """Cover numbered-list with non-numbered content."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:numbered-list:steps -->
1. step
<!-- spd:numbered-list:steps -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:numbered-list:steps -->\nnot numbered\n<!-- spd:numbered-list:steps -->")
    report = tmpl.validate(art_path)
    assert any("Expected numbered list" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_task_list_invalid(tmp_path: Path):
    """Cover task-list with invalid format."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:task-list:tasks -->
- [ ] task
<!-- spd:task-list:tasks -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:task-list:tasks -->\nnot a task\n<!-- spd:task-list:tasks -->")
    report = tmpl.validate(art_path)
    assert any("Expected task list" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_task_list_missing_priority(tmp_path: Path):
    """Cover task-list with priority requirement but missing priority."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:task-list:tasks has="priority" -->
- [ ] `p1` task
<!-- spd:task-list:tasks -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:task-list:tasks -->\n- [ ] task without priority\n<!-- spd:task-list:tasks -->")
    report = tmpl.validate(art_path)
    assert any("Task item missing priority" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_table_too_few_rows(tmp_path: Path):
    """Cover table with less than 2 rows."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- spd:table:data -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:table:data -->\n| only header |\n<!-- spd:table:data -->")
    report = tmpl.validate(art_path)
    assert any("Table must have header and separator" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_table_invalid_header(tmp_path: Path):
    """Cover table with invalid header."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- spd:table:data -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:table:data -->\nno pipes\nalso no pipes\n<!-- spd:table:data -->")
    report = tmpl.validate(art_path)
    assert any("Invalid table" in str(e.get("message", "")) or "Table must have" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_table_no_data_rows(tmp_path: Path):
    """Cover table with no data rows."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- spd:table:data -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:table:data -->\n| h1 | h2 |\n|----|----|<!-- spd:table:data -->")
    report = tmpl.validate(art_path)
    # Should fail due to no data rows or format issues
    assert len(report["errors"]) > 0


def test_block_validation_table_row_mismatch(tmp_path: Path):
    """Cover table with row column mismatch."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- spd:table:data -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:table:data -->\n| h1 | h2 |\n|----|----|---|\n| v1 |\n<!-- spd:table:data -->")
    report = tmpl.validate(art_path)
    assert any("mismatch" in str(e.get("message", "")).lower() for e in report["errors"])


def test_block_validation_paragraph_empty(tmp_path: Path):
    """Cover empty paragraph block."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:paragraph:summary -->
Some text
<!-- spd:paragraph:summary -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:paragraph:summary -->\n\n<!-- spd:paragraph:summary -->")
    report = tmpl.validate(art_path)
    assert any("Paragraph block empty" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_code_no_fence(tmp_path: Path):
    """Cover code block without opening fence."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:code:snippet -->
```
code
```
<!-- spd:code:snippet -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:code:snippet -->\nnot a fence\n<!-- spd:code:snippet -->")
    report = tmpl.validate(art_path)
    assert any("Code block must start with" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_code_unclosed_fence(tmp_path: Path):
    """Cover code block with unclosed fence."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:code:snippet -->
```
code
```
<!-- spd:code:snippet -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:code:snippet -->\n```\ncode without closing\n<!-- spd:code:snippet -->")
    report = tmpl.validate(art_path)
    assert any("Code fence must be closed" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_heading(tmp_path: Path):
    """Cover heading block validation."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:##:section -->
## Heading
<!-- spd:##:section -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    # Wrong heading level
    art_path = _write(tmp_path / "art.md", "<!-- spd:##:section -->\n# Wrong level\n<!-- spd:##:section -->")
    report = tmpl.validate(art_path)
    assert any("Heading level mismatch" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_heading_empty(tmp_path: Path):
    """Cover empty heading block."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:##:section -->
## Heading
<!-- spd:##:section -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:##:section -->\n\n<!-- spd:##:section -->")
    report = tmpl.validate(art_path)
    assert any("Heading block empty" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_link_invalid(tmp_path: Path):
    """Cover invalid link block."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:link:ref -->
[text](url)
<!-- spd:link:ref -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:link:ref -->\nnot a link\n<!-- spd:link:ref -->")
    report = tmpl.validate(art_path)
    assert any("Invalid link" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_image_invalid(tmp_path: Path):
    """Cover invalid image block."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:image:pic -->
![alt](url)
<!-- spd:image:pic -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:image:pic -->\nnot an image\n<!-- spd:image:pic -->")
    report = tmpl.validate(art_path)
    assert any("Invalid image" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_fdl_empty(tmp_path: Path):
    """Cover empty FDL block."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:fdl:flow -->
1. [ ] - `ph-1` - Step - `inst-1`
<!-- spd:fdl:flow -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:fdl:flow -->\n\n<!-- spd:fdl:flow -->")
    report = tmpl.validate(art_path)
    assert any("FDL block empty" in str(e.get("message", "")) for e in report["errors"])


def test_block_validation_fdl_invalid_line(tmp_path: Path):
    """Cover FDL block with invalid line."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:fdl:flow -->
1. [ ] - `ph-1` - Step - `inst-1`
<!-- spd:fdl:flow -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:fdl:flow -->\ninvalid fdl line\n<!-- spd:fdl:flow -->")
    report = tmpl.validate(art_path)
    assert any("Invalid FDL line" in str(e.get("message", "")) for e in report["errors"])


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
    art_path = _write(tmp_path / "art.md", "<!-- spd:paragraph:summary -->\nunclosed")
    report = tmpl.validate(art_path)
    assert any("Unclosed marker" in str(e.get("message", "")) for e in report["errors"])


def test_artifact_unknown_marker_warning(tmp_path: Path):
    """Cover unknown marker producing error (unknown markers are always errors, regardless of unknown_sections policy)."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
  unknown_sections: warn
---
<!-- spd:paragraph:known -->
text
<!-- spd:paragraph:known -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:paragraph:known -->\ntext\n<!-- spd:paragraph:known -->\n<!-- spd:paragraph:unknown -->\ntext\n<!-- spd:paragraph:unknown -->")
    report = tmpl.validate(art_path)
    # Unknown markers are always errors (unknown_sections policy applies only to markdown sections without markers)
    assert any("Unknown marker" in str(e.get("message", "")) for e in report["errors"])


def test_artifact_unknown_marker_error(tmp_path: Path):
    """Cover unknown marker producing error when policy is error."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
  unknown_sections: error
---
<!-- spd:paragraph:known -->
text
<!-- spd:paragraph:known -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:paragraph:known -->\ntext\n<!-- spd:paragraph:known -->\n<!-- spd:paragraph:unknown -->\ntext\n<!-- spd:paragraph:unknown -->")
    report = tmpl.validate(art_path)
    assert any("Unknown marker" in str(e.get("message", "")) for e in report["errors"])


def test_artifact_block_repeat_once_violation(tmp_path: Path):
    """Cover block appearing more than once when repeat=one."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:paragraph:unique repeat="one" -->
text
<!-- spd:paragraph:unique -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:paragraph:unique -->\ntext\n<!-- spd:paragraph:unique -->\n<!-- spd:paragraph:unique -->\ntext2\n<!-- spd:paragraph:unique -->")
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
    result = art.get("spd-demo-item-1")
    assert result is not None
    assert "spd-demo-item-1" in result

    # Test get with nonexistent ID
    result2 = art.get("nonexistent-id")
    assert result2 is None

    # Test list method
    results = art.list(["spd-demo-item-1", "nonexistent"])
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
    assert "spd-demo-item-1" in ids


def test_id_task_status_all_done_but_id_not_marked(tmp_path: Path):
    """Cover ID task status validation - all tasks done but ID not marked."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:id:item has="task" -->
- [ ] `p1` - **ID**: `spd-test-1`
<!-- spd:task-list:tasks -->
- [x] task
<!-- spd:task-list:tasks -->
<!-- spd:id:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_text = """<!-- spd:id:item -->
- [ ] `p1` - **ID**: `spd-test-1`
<!-- spd:task-list:tasks -->
- [x] all done
<!-- spd:task-list:tasks -->
<!-- spd:id:item -->
"""
    art_path = _write(tmp_path / "art.md", art_text)
    report = tmpl.validate(art_path)
    assert any("All tasks done but ID not marked done" in str(e.get("message", "")) for e in report["errors"])


def test_id_task_status_id_done_but_tasks_not(tmp_path: Path):
    """Cover ID task status validation - ID marked done but tasks not all done."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:id:item has="task" -->
- [x] `p1` - **ID**: `spd-test-1`
<!-- spd:task-list:tasks -->
- [ ] task
<!-- spd:task-list:tasks -->
<!-- spd:id:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_text = """<!-- spd:id:item -->
- [x] `p1` - **ID**: `spd-test-1`
<!-- spd:task-list:tasks -->
- [ ] not done
<!-- spd:task-list:tasks -->
<!-- spd:id:item -->
"""
    art_path = _write(tmp_path / "art.md", art_text)
    report = tmpl.validate(art_path)
    assert any("ID marked done but tasks not all done" in str(e.get("message", "")) for e in report["errors"])


def test_cross_validate_ref_no_definition(tmp_path: Path):
    """Cover cross validation when reference has no definition."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:id-ref:item -->
[x] - `spd-test-1`
<!-- spd:id-ref:item -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", "<!-- spd:id-ref:item -->\n[x] - `spd-nonexistent`\n<!-- spd:id-ref:item -->")
    art = tmpl.parse(art_path)
    report = cross_validate_artifacts([art])
    assert any("Reference has no definition" in str(e.get("message", "")) for e in report["errors"])


def test_artifact_with_template_frontmatter_detected(tmp_path: Path):
    """Cover detection of template frontmatter in artifact (should error)."""
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text())
    tmpl, _ = load_template(tmpl_path)

    # Artifact should NOT have spider-template frontmatter
    bad_artifact = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- spd:paragraph:summary -->
Some content
<!-- spd:paragraph:summary -->
"""
    art_path = _write(tmp_path / "bad-artifact.md", bad_artifact)
    report = tmpl.validate(art_path)
    assert any("template frontmatter" in str(e.get("message", "")).lower() for e in report["errors"])


def test_artifact_without_template_frontmatter_ok(tmp_path: Path):
    """Cover that normal frontmatter (without spider-template) is OK."""
    tmpl_path = _write(tmp_path / "tmpl.template.md", _sample_template_text())
    tmpl, _ = load_template(tmpl_path)

    # Normal YAML frontmatter is fine
    ok_artifact = """---
title: My Document
author: Test
---
<!-- spd:id:item -->
- [x] `p1` - **ID**: `spd-demo-item-1`
<!-- spd:id:item -->
<!-- spd:paragraph:summary -->
Some content
<!-- spd:paragraph:summary -->
<!-- spd:list:bullets -->
- a
<!-- spd:list:bullets -->
<!-- spd:table:data -->
| h1 | h2 |
|----|----|
| v1 | v2 |
<!-- spd:table:data -->
<!-- spd:code:snippet -->
```
code
```
<!-- spd:code:snippet -->
<!-- spd:fdl:flow -->
1. [x] - `ph-1` - Step - `inst-step-1`
<!-- spd:fdl:flow -->
"""
    art_path = _write(tmp_path / "ok-artifact.md", ok_artifact)
    report = tmpl.validate(art_path)
    # Should not have the template frontmatter error
    assert not any("template frontmatter" in str(e.get("message", "")).lower() for e in report["errors"])


def test_cross_validate_external_system_ref_no_error(tmp_path: Path):
    """External system references should not error when registered_systems is provided."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:id:item -->
**ID**: `spd-myapp-item-1`
<!-- spd:id:item -->
<!-- spd:id-ref:ref -->
`spd-other-system-feature-auth`
<!-- spd:id-ref:ref -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", """<!-- spd:id:item -->
**ID**: `spd-myapp-item-1`
<!-- spd:id:item -->
<!-- spd:id-ref:ref -->
`spd-other-system-feature-auth`
<!-- spd:id-ref:ref -->
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
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- spd:id:item -->
**ID**: `spd-myapp-item-1`
<!-- spd:id:item -->
<!-- spd:id-ref:ref -->
`spd-myapp-missing-thing`
<!-- spd:id-ref:ref -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", """<!-- spd:id:item -->
**ID**: `spd-myapp-item-1`
<!-- spd:id:item -->
<!-- spd:id-ref:ref -->
`spd-myapp-missing-thing`
<!-- spd:id-ref:ref -->
""")
    art = tmpl.parse(art_path)
    # With registered_systems containing "myapp", internal ref without def should error
    report = cross_validate_artifacts([art], registered_systems={"myapp"})
    ref_errors = [e for e in report["errors"] if "Reference has no definition" in str(e.get("message", ""))]
    assert len(ref_errors) == 1
    assert "spd-myapp-missing-thing" in str(ref_errors[0])


def test_cross_validate_multi_word_system_external(tmp_path: Path):
    """Multi-word system names should be handled correctly."""
    text = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: FEATURE
---
<!-- spd:id:item -->
**ID**: `spd-account-server-feature-billing`
<!-- spd:id:item -->
<!-- spd:id-ref:ref -->
`spd-other-app-feature-auth`
<!-- spd:id-ref:ref -->
"""
    tmpl_path = _write(tmp_path / "tmpl.template.md", text)
    tmpl, _ = load_template(tmpl_path)
    art_path = _write(tmp_path / "art.md", """<!-- spd:id:item -->
**ID**: `spd-account-server-feature-billing`
<!-- spd:id:item -->
<!-- spd:id-ref:ref -->
`spd-other-app-feature-auth`
<!-- spd:id-ref:ref -->
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
spider-template:
  version:
    major: 1
    minor: 0
  kind: DEF
  unknown_sections: warn
---
<!-- spd:id:item has="priority,task" -->
- [ ] `p1` - **ID**: `spd-test-item-1`
<!-- spd:id:item -->
"""
    # Reference template WITHOUT has attribute (should pass - ref decides its own attrs)
    ref_tmpl_simple = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: REF
  unknown_sections: warn
---
<!-- spd:id-ref:item -->
`spd-test-item-1`
<!-- spd:id-ref:item -->
"""
    # Reference template WITH has attribute (should also pass)
    ref_tmpl_full = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: REF
  unknown_sections: warn
---
<!-- spd:id-ref:item has="priority,task" -->
[ ] `p1` - `spd-test-item-1`
<!-- spd:id-ref:item -->
"""
    def_tmpl_path = _write(tmp_path / "def.template.md", def_tmpl)
    ref_tmpl_simple_path = _write(tmp_path / "ref-simple.template.md", ref_tmpl_simple)
    ref_tmpl_full_path = _write(tmp_path / "ref-full.template.md", ref_tmpl_full)

    tmpl_def, _ = load_template(def_tmpl_path)
    tmpl_ref_simple, _ = load_template(ref_tmpl_simple_path)
    tmpl_ref_full, _ = load_template(ref_tmpl_full_path)

    art_def = tmpl_def.parse(
      _write(tmp_path / "def.md", """<!-- spd:id:item -->
- [ ] `p1` - **ID**: `spd-test-item-1`
<!-- spd:id:item -->"""),
    )

    # Reference without has attribute should pass (ref decides its own attrs)
    art_ref_simple = tmpl_ref_simple.parse(
      _write(tmp_path / "ref-simple.md", """<!-- spd:id-ref:item -->
`spd-test-item-1`
<!-- spd:id-ref:item -->"""),
    )
    report_simple = cross_validate_artifacts([art_def, art_ref_simple])
    assert not any("Reference missing" in str(e.get("message", "")) for e in report_simple["errors"])

    # Reference with has attribute should also pass
    art_ref_full = tmpl_ref_full.parse(
      _write(tmp_path / "ref-full.md", """<!-- spd:id-ref:item has="priority,task" -->
[ ] `p1` - `spd-test-item-1`
<!-- spd:id-ref:item -->"""),
    )
    report_full = cross_validate_artifacts([art_def, art_ref_full])
    assert not any("Reference missing" in str(e.get("message", "")) for e in report_full["errors"])


def test_nesting_validation_errors_on_wrong_parent(tmp_path: Path):
    """Nesting validation should error when artifact block has wrong parent."""
    # Template with nested structure: ##:outer contains ##:inner
    template_content = """---
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
  unknown_sections: warn
---
<!-- spd:##:outer -->
## Outer
<!-- spd:##:inner -->
### Inner
<!-- spd:##:inner -->
<!-- spd:##:outer -->
"""
    # Artifact with correct nesting
    artifact_correct = """<!-- spd:##:outer -->
## Outer
<!-- spd:##:inner -->
### Inner
<!-- spd:##:inner -->
<!-- spd:##:outer -->"""

    # Artifact with WRONG nesting (inner NOT inside outer)
    artifact_wrong = """<!-- spd:##:outer -->
## Outer
<!-- spd:##:outer -->
<!-- spd:##:inner -->
### Inner
<!-- spd:##:inner -->"""

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
spider-template:
  version:
    major: 1
    minor: 0
  kind: TEST
  unknown_sections: warn
---
<!-- spd:##:section repeat="many" -->
## Section
<!-- spd:paragraph:content -->
Content here
<!-- spd:paragraph:content -->
<!-- spd:##:section -->
"""
    # Artifact with different nesting (paragraph directly inside section is fine)
    artifact = """<!-- spd:##:section repeat="many" -->
## Section 1
<!-- spd:paragraph:content -->
Content here
<!-- spd:paragraph:content -->
<!-- spd:##:section -->"""

    tmpl_path = _write(tmp_path / "test.template.md", template_content)
    tmpl, _ = load_template(tmpl_path)

    art = tmpl.parse(
      _write(tmp_path / "art.md", artifact),
    )
    report = art.validate()
    nesting_errors = [e for e in report["errors"] if e.get("type") == "nesting"]
    # Should have no nesting errors because parent has repeat="many"
    assert len(nesting_errors) == 0
