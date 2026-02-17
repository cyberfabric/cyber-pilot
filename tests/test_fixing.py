"""Tests for cypilot.utils.fixing — validation output enrichment.

Covers:
- enrich_issues: cypilot: prefix, path stripping, fixing_prompt generation
- _rel_loc: absolute → relative path conversion
- _headings_hint: heading context in prompts
- All major error message categories
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pytest

from cypilot.utils import error_codes as EC
from cypilot.utils.fixing import enrich_issues


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_issue(
    msg: str,
    *,
    code: str = "",
    path: str = "/project/architecture/PRD.md",
    line: int = 42,
    **extra,
) -> Dict[str, object]:
    """Build a minimal issue dict matching the error() factory output."""
    out: Dict[str, object] = {
        "type": extra.pop("type", "constraints"),
        "message": msg,
        "line": line,
        "path": path,
        "location": f"{path}:{line}",
    }
    if code:
        out["code"] = code
    extra = {k: v for k, v in extra.items() if v is not None}
    out.update(extra)
    return out


PROJECT_ROOT = Path("/project")


# ---------------------------------------------------------------------------
# enrich_issues: basic behaviour
# ---------------------------------------------------------------------------

class TestEnrichIssuesBasic:
    def test_adds_cypilot_prefix(self):
        issues = [_make_issue("Reference has no definition", code=EC.REF_NO_DEFINITION, id="cpt-x-y")]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert issues[0]["fixing_prompt"].startswith("cypilot: ")

    def test_strips_path_key(self):
        issues = [_make_issue("Reference has no definition", code=EC.REF_NO_DEFINITION, id="cpt-x-y")]
        assert "path" in issues[0]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "path" not in issues[0]

    def test_location_preserved(self):
        issues = [_make_issue("Reference has no definition", code=EC.REF_NO_DEFINITION, id="cpt-x-y")]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert issues[0]["location"] == "/project/architecture/PRD.md:42"

    def test_line_preserved(self):
        issues = [_make_issue("Reference has no definition", code=EC.REF_NO_DEFINITION, id="cpt-x-y")]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert issues[0]["line"] == 42

    def test_no_fixing_prompt_for_unknown_message(self):
        issues = [_make_issue("Some totally unknown error message")]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "fixing_prompt" not in issues[0]
        # path should still be stripped
        assert "path" not in issues[0]

    def test_multiple_issues_enriched(self):
        issues = [
            _make_issue("Reference has no definition", code=EC.REF_NO_DEFINITION, id="cpt-a-b"),
            _make_issue("Reference marked done but definition not done", code=EC.REF_DONE_DEF_NOT_DONE, id="cpt-c-d"),
        ]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert all("fixing_prompt" in i for i in issues)
        assert all(i["fixing_prompt"].startswith("cypilot: ") for i in issues)

    def test_without_project_root_uses_absolute_path(self):
        issues = [_make_issue("Reference has no definition", code=EC.REF_NO_DEFINITION, id="cpt-x-y")]
        enrich_issues(issues, project_root=None)
        prompt = issues[0]["fixing_prompt"]
        assert "/project/architecture/PRD.md:42" in prompt


# ---------------------------------------------------------------------------
# Relative path conversion
# ---------------------------------------------------------------------------

class TestRelativePaths:
    def test_absolute_path_becomes_relative(self):
        issues = [_make_issue("Reference has no definition", code=EC.REF_NO_DEFINITION, id="cpt-x-y")]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "architecture/PRD.md:42" in prompt
        assert "/project/" not in prompt

    def test_path_outside_project_root_unchanged(self):
        issues = [_make_issue(
            "Reference has no definition",
            code=EC.REF_NO_DEFINITION,
            path="/other/place/file.md",
            line=10,
            id="cpt-x-y",
        )]
        issues[0]["location"] = "/other/place/file.md:10"
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "/other/place/file.md:10" in prompt

    def test_pseudo_path_no_crash(self):
        """Paths like <constraints.json> should not crash."""
        issues = [_make_issue(
            "Missing constraints for artifact kinds",
            code=EC.MISSING_CONSTRAINTS,
            path="<constraints.json>",
            line=1,
            kinds=["FOO"],
        )]
        issues[0]["location"] = "<constraints.json>"
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "fixing_prompt" in issues[0]


# ---------------------------------------------------------------------------
# Headings hint
# ---------------------------------------------------------------------------

class TestHeadingsHint:
    def test_headings_included_in_required_ref(self):
        issues = [_make_issue(
            "ID not referenced from required artifact kind",
            code=EC.REF_MISSING_FROM_KIND,
            id="cpt-sys-fr-login",
            artifact_kind="PRD",
            target_kind="DESIGN",
            id_kind="fr",
            target_headings=["design-capabilities"],
            target_headings_info=[{"id": "design-capabilities", "description": "Capabilities"}],
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "Under section:" in prompt
        assert "`design-capabilities` (Capabilities)" in prompt

    def test_headings_included_in_missing_id_kind(self):
        issues = [_make_issue(
            "Required ID kind missing in artifact (Usecase)",
            code=EC.REQUIRED_ID_KIND_MISSING,
            path="/project/architecture/PRD.md",
            line=1,
            artifact_kind="PRD",
            id_kind="usecase",
            target_headings=["prd-use-cases"],
            target_headings_info=[{"id": "prd-use-cases", "description": "Use Cases"}],
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "Under section:" in prompt
        assert "`prd-use-cases` (Use Cases)" in prompt

    def test_headings_included_in_definition_placement(self):
        issues = [_make_issue(
            "ID definition not under required headings (Feature)",
            code=EC.DEF_WRONG_HEADINGS,
            id="cpt-sys-fr-x",
            artifact_kind="PRD",
            id_kind="fr",
            headings=["prd-capabilities"],
            headings_info=[{"id": "prd-capabilities", "description": "Functional Requirements"}],
            found_headings=["prd-overview"],
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "Under section:" in prompt
        assert "`prd-capabilities` (Functional Requirements)" in prompt
        assert "prd-overview" in prompt

    def test_headings_included_in_reference_placement(self):
        issues = [_make_issue(
            "ID reference not under required headings",
            code=EC.REF_WRONG_HEADINGS,
            id="cpt-sys-fr-x",
            artifact_kind="PRD",
            target_kind="DESIGN",
            id_kind="fr",
            headings=["design-reqs"],
            headings_info=[{"id": "design-reqs", "description": "Requirements Mapping"}],
            found_headings=["design-overview"],
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "Under section:" in prompt
        assert "`design-reqs` (Requirements Mapping)" in prompt

    def test_no_headings_no_hint(self):
        issues = [_make_issue(
            "ID not referenced from required artifact kind",
            code=EC.REF_MISSING_FROM_KIND,
            id="cpt-sys-fr-login",
            artifact_kind="PRD",
            target_kind="DESIGN",
            id_kind="fr",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "Under section:" not in prompt

    def test_headings_without_description(self):
        issues = [_make_issue(
            "ID not referenced from required artifact kind",
            code=EC.REF_MISSING_FROM_KIND,
            id="cpt-sys-fr-login",
            artifact_kind="PRD",
            target_kind="DESIGN",
            id_kind="fr",
            target_headings=["some-heading"],
            target_headings_info=[{"id": "some-heading", "description": None}],
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "`some-heading`" in prompt
        # No parenthetical description
        assert "(None)" not in prompt

    def test_multiple_headings(self):
        issues = [_make_issue(
            "ID not referenced from required artifact kind",
            code=EC.REF_MISSING_FROM_KIND,
            id="cpt-sys-fr-login",
            artifact_kind="PRD",
            target_kind="DESIGN",
            id_kind="fr",
            target_headings=["h1", "h2"],
            target_headings_info=[
                {"id": "h1", "description": "First"},
                {"id": "h2", "description": "Second"},
            ],
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "`h1` (First)" in prompt
        assert "`h2` (Second)" in prompt


# ---------------------------------------------------------------------------
# Structure errors — fixing prompts
# ---------------------------------------------------------------------------

class TestStructurePrompts:
    def test_cdsl_unchecked(self):
        issues = [_make_issue(
            "CDSL step is unchecked but parent ID is checked",
            code=EC.CDSL_STEP_UNCHECKED,
            type="structure", id="cpt-sys-fr-x",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "checked `[x]`" in issues[0]["fixing_prompt"]

    def test_parent_unchecked(self):
        issues = [_make_issue(
            "Parent ID is unchecked but all nested task-tracked items are checked",
            code=EC.PARENT_UNCHECKED_ALL_DONE,
            type="structure", id="cpt-sys-fr-x",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "check parent" in issues[0]["fixing_prompt"]

    def test_parent_checked_nested_unchecked(self):
        issues = [_make_issue(
            "Parent ID is checked but some nested task-tracked items are unchecked",
            code=EC.PARENT_CHECKED_NESTED_UNCHECKED,
            type="structure", id="cpt-sys-fr-x", parent_id="cpt-sys-fr-parent",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "cpt-sys-fr-parent" in issues[0]["fixing_prompt"]

    def test_reference_no_definition(self):
        issues = [_make_issue("Reference has no definition", code=EC.REF_NO_DEFINITION, type="structure", id="cpt-sys-fr-x")]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "add a definition" in issues[0]["fixing_prompt"]

    def test_reference_done_definition_not(self):
        issues = [_make_issue("Reference marked done but definition not done", code=EC.REF_DONE_DEF_NOT_DONE, type="structure", id="cpt-sys-fr-x")]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "uncheck" in issues[0]["fixing_prompt"]

    def test_reference_task_no_definition_task(self):
        issues = [_make_issue("Reference has task checkbox but definition has no task checkbox", code=EC.REF_TASK_DEF_NO_TASK, type="structure", id="cpt-sys-fr-x")]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "remove the task checkbox" in issues[0]["fixing_prompt"]

    def test_id_not_referenced(self):
        issues = [_make_issue(
            "ID not referenced from other artifact kinds",
            code=EC.ID_NOT_REFERENCED,
            type="structure", id="cpt-sys-fr-x",
            other_kinds=["DESIGN", "DECOMPOSITION"],
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "`DESIGN`" in prompt
        assert "`DECOMPOSITION`" in prompt

    def test_heading_numbering_not_consecutive(self):
        issues = [_make_issue(
            "Heading numbering is not consecutive",
            code=EC.HEADING_NUMBER_NOT_CONSECUTIVE,
            type="structure",
            expected_prefix="3",
            previous_prefix="1",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "expected `3`" in issues[0]["fixing_prompt"]


# ---------------------------------------------------------------------------
# Constraint errors — fixing prompts
# ---------------------------------------------------------------------------

class TestConstraintPrompts:
    def test_id_kind_not_allowed(self):
        issues = [_make_issue(
            "ID kind not allowed by constraints (Feature)",
            code=EC.ID_KIND_NOT_ALLOWED,
            id="cpt-sys-feat-x", id_kind="feat",
            allowed=["fr", "usecase"],
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "feat" in issues[0]["fixing_prompt"]
        assert "allowed" in issues[0]["fixing_prompt"]

    def test_missing_task_checkbox(self):
        issues = [_make_issue(
            "ID definition missing required task checkbox (Usecase)",
            code=EC.DEF_MISSING_TASK,
            id="cpt-sys-usecase-x", id_kind="usecase", artifact_kind="PRD",
            id_kind_template="cpt-{sys}-usecase-{slug}",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "`- [ ]`" in prompt
        assert "Template:" in prompt

    def test_prohibited_task_checkbox(self):
        issues = [_make_issue(
            "ID definition has prohibited task checkbox",
            code=EC.DEF_PROHIBITED_TASK,
            id="cpt-sys-fr-x", id_kind="fr",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "remove the task checkbox" in issues[0]["fixing_prompt"]

    def test_missing_priority(self):
        issues = [_make_issue(
            "ID definition missing required priority",
            code=EC.DEF_MISSING_PRIORITY,
            id="cpt-sys-fr-x", id_kind="fr", artifact_kind="PRD",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "priority marker" in issues[0]["fixing_prompt"]

    def test_prohibited_priority(self):
        issues = [_make_issue(
            "ID definition has prohibited priority",
            code=EC.DEF_PROHIBITED_PRIORITY,
            id="cpt-sys-fr-x", id_kind="fr",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "remove the priority" in issues[0]["fixing_prompt"]

    def test_heading_missing(self):
        issues = [_make_issue(
            "Required heading missing in artifact (expected after ...)",
            code=EC.HEADING_MISSING,
            path="/project/architecture/PRD.md", line=1,
            heading_level=2, heading_pattern="Actors", artifact_kind="PRD",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "level-2" in prompt
        assert "`Actors`" in prompt

    def test_heading_prohibits_multiple(self):
        issues = [_make_issue("Heading constraint prohibits multiple occurrences", code=EC.HEADING_PROHIBITS_MULTIPLE)]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "duplicate heading" in issues[0]["fixing_prompt"]

    def test_heading_requires_multiple(self):
        issues = [_make_issue("Heading constraint requires multiple occurrences", code=EC.HEADING_REQUIRES_MULTIPLE)]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "at least 2" in issues[0]["fixing_prompt"]

    def test_heading_numbering_mismatch(self):
        issues = [_make_issue("Heading numbering does not match constraint", code=EC.HEADING_NUMBERING_MISMATCH, numbered="required")]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "required but missing" in issues[0]["fixing_prompt"]


# ---------------------------------------------------------------------------
# Cross-reference errors — fixing prompts
# ---------------------------------------------------------------------------

class TestCrossRefTargetArtifactPath:
    """Tests for the 3 target artifact path cases in 'ID not referenced' prompt."""

    def test_existing_artifact_path_in_prompt(self):
        issues = [_make_issue(
            "ID not referenced from required artifact kind",
            code=EC.REF_MISSING_FROM_KIND,
            id="cpt-sys-fr-login",
            artifact_kind="PRD",
            target_kind="DESIGN",
            id_kind="fr",
            target_artifact_path="/project/architecture/DESIGN.md",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "in `architecture/DESIGN.md`" in prompt
        assert "create" not in prompt
        assert "ask user" not in prompt

    def test_suggested_path_creates_artifact(self):
        issues = [_make_issue(
            "ID not referenced from required artifact kind",
            code=EC.REF_MISSING_FROM_KIND,
            id="cpt-sys-fr-login",
            artifact_kind="PRD",
            target_kind="DESIGN",
            id_kind="fr",
            target_artifact_suggested_path="architecture/DESIGN.md",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "create `architecture/DESIGN.md`" in prompt
        assert "`DESIGN` artifact missing" in prompt

    def test_no_path_asks_user(self):
        issues = [_make_issue(
            "ID not referenced from required artifact kind",
            code=EC.REF_MISSING_FROM_KIND,
            id="cpt-sys-fr-login",
            artifact_kind="PRD",
            target_kind="DESIGN",
            id_kind="fr",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "ask user for the artifact path" in prompt

    def test_existing_artifact_path_with_headings(self):
        issues = [_make_issue(
            "ID not referenced from required artifact kind",
            code=EC.REF_MISSING_FROM_KIND,
            id="cpt-sys-fr-login",
            artifact_kind="PRD",
            target_kind="DESIGN",
            id_kind="fr",
            target_artifact_path="/project/architecture/DESIGN.md",
            target_headings=["design-capabilities"],
            target_headings_info=[{"id": "design-capabilities", "description": "Capabilities"}],
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "in `architecture/DESIGN.md`" in prompt
        assert "Under section:" in prompt
        assert "`design-capabilities` (Capabilities)" in prompt

    def test_suggested_path_with_headings(self):
        issues = [_make_issue(
            "ID not referenced from required artifact kind",
            code=EC.REF_MISSING_FROM_KIND,
            id="cpt-sys-fr-login",
            artifact_kind="PRD",
            target_kind="DESIGN",
            id_kind="fr",
            target_artifact_suggested_path="architecture/DESIGN.md",
            target_headings=["design-capabilities"],
            target_headings_info=[{"id": "design-capabilities", "description": "Capabilities"}],
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        prompt = issues[0]["fixing_prompt"]
        assert "create `architecture/DESIGN.md`" in prompt
        assert "Under section:" in prompt


class TestCrossRefPrompts:
    def test_required_ref_target_not_in_scope(self):
        issues = [_make_issue(
            "Required reference target kind not in scope",
            code=EC.REF_TARGET_NOT_IN_SCOPE,
            id="cpt-sys-fr-x", target_kind="DESIGN",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "`DESIGN`" in issues[0]["fixing_prompt"]
        assert "exists in scope" in issues[0]["fixing_prompt"]

    def test_ref_missing_task_for_tracked_def(self):
        issues = [_make_issue(
            "ID reference missing required task checkbox for task-tracked definition",
            code=EC.REF_MISSING_TASK_FOR_TRACKED,
            id="cpt-sys-fr-x", artifact_kind="DESIGN",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "task-tracked" in issues[0]["fixing_prompt"]

    def test_ref_from_prohibited_kind(self):
        issues = [_make_issue(
            "ID referenced from prohibited artifact kind",
            code=EC.REF_FROM_PROHIBITED_KIND,
            id="cpt-sys-fr-x", target_kind="DECOMPOSITION",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "prohibited" in issues[0]["fixing_prompt"]

    def test_ref_missing_task(self):
        issues = [_make_issue("ID reference missing required task checkbox", code=EC.REF_MISSING_TASK, id="cpt-sys-fr-x")]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "`- [ ]`" in issues[0]["fixing_prompt"]

    def test_ref_prohibited_task(self):
        issues = [_make_issue("ID reference has prohibited task checkbox", code=EC.REF_PROHIBITED_TASK, id="cpt-sys-fr-x")]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "remove task checkbox" in issues[0]["fixing_prompt"]

    def test_ref_missing_priority(self):
        issues = [_make_issue("ID reference missing required priority", code=EC.REF_MISSING_PRIORITY, id="cpt-sys-fr-x")]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "priority marker" in issues[0]["fixing_prompt"]

    def test_ref_prohibited_priority(self):
        issues = [_make_issue("ID reference has prohibited priority", code=EC.REF_PROHIBITED_PRIORITY, id="cpt-sys-fr-x")]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "remove priority" in issues[0]["fixing_prompt"]


# ---------------------------------------------------------------------------
# Code traceability errors — fixing prompts
# ---------------------------------------------------------------------------

class TestCodePrompts:
    def test_duplicate_begin(self):
        issues = [_make_issue(
            "Duplicate @cpt-begin without matching @cpt-end",
            code=EC.MARKER_DUP_BEGIN,
            type="marker", id="cpt-sys-fr-x",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "@cpt-end" in issues[0]["fixing_prompt"]

    def test_end_without_begin(self):
        issues = [_make_issue(
            "@cpt-end without matching @cpt-begin",
            code=EC.MARKER_END_NO_BEGIN,
            type="marker", id="cpt-sys-fr-x",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "@cpt-begin" in issues[0]["fixing_prompt"]

    def test_empty_block(self):
        issues = [_make_issue(
            "Empty block (no code between @cpt-begin and @cpt-end)",
            code=EC.MARKER_EMPTY_BLOCK,
            type="marker", id="cpt-sys-fr-x",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "implementation code" in issues[0]["fixing_prompt"]

    def test_begin_without_end(self):
        issues = [_make_issue(
            "@cpt-begin without matching @cpt-end",
            code=EC.MARKER_BEGIN_NO_END,
            type="marker", id="cpt-sys-fr-x",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "@cpt-end" in issues[0]["fixing_prompt"]

    def test_duplicate_scope(self):
        issues = [_make_issue(
            "Duplicate scope marker",
            code=EC.MARKER_DUP_SCOPE,
            type="marker", id="cpt-sys-fr-x",
            first_occurrence=10,
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "line 10" in issues[0]["fixing_prompt"]

    def test_docs_only_markers(self):
        issues = [_make_issue(
            "Cypilot markers found in code but traceability is DOCS-ONLY",
            code=EC.CODE_DOCS_ONLY,
            type="traceability",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "DOCS-ONLY" in issues[0]["fixing_prompt"]

    def test_orphan_code_ref(self):
        issues = [_make_issue(
            "Code marker references ID not defined in any artifact",
            code=EC.CODE_ORPHAN_REF,
            type="traceability", id="cpt-sys-fr-x",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "define" in issues[0]["fixing_prompt"]

    def test_to_code_unchecked(self):
        issues = [_make_issue(
            'ID marked to_code="true" is referenced from code but task checkbox is not checked',
            code=EC.CODE_TASK_UNCHECKED,
            type="structure", id="cpt-sys-fr-x",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "checkbox `[x]`" in issues[0]["fixing_prompt"]

    def test_to_code_no_marker(self):
        issues = [_make_issue(
            'ID marked to_code="true" has no code marker',
            code=EC.CODE_NO_MARKER,
            type="coverage", id="cpt-sys-fr-x",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "@cpt-*:" in issues[0]["fixing_prompt"]


# ---------------------------------------------------------------------------
# Warnings — fixing prompts
# ---------------------------------------------------------------------------

class TestWarningPrompts:
    def test_id_not_referenced_no_other_kinds(self):
        issues = [_make_issue(
            "ID not referenced (no other artifact kinds in scope)",
            code=EC.ID_NOT_REFERENCED_NO_SCOPE,
            id="cpt-sys-fr-x",
        )]
        enrich_issues(issues, project_root=PROJECT_ROOT)
        assert "no references" in issues[0]["fixing_prompt"]
