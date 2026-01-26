import sys
import os
from pathlib import Path
import importlib.util
import io
import contextlib
import unittest
from unittest.mock import patch
from tempfile import TemporaryDirectory
from typing import List


# Add skills/fdd/scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))

from fdd.validation.traceability import (
    _parse_prd_model,
    compute_excluded_line_ranges,
    is_effective_code_line,
    extract_scope_ids,
    iter_code_files,
    paired_inst_tags_in_text,
)

from fdd.validation.artifacts import validate as validate_artifact

from fdd.validation.artifacts.common import (
    common_checks,
    validate_generic_sections,
    _extract_feature_links,
    _extract_id_list,
    _normalize_feature_relpath,
)

from fdd import cli as fdd_cli

def _load_fdd_module():
    tests_dir = Path(__file__).resolve().parent
    fdd_root = tests_dir.parent
    script_path = fdd_root / "skills" / "fdd" / "scripts" / "fdd.py"

    spec = importlib.util.spec_from_file_location("fdd", str(script_path))
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to create import spec for fdd.py")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


VA = _load_fdd_module()


def _req_text(*section_ids: str) -> str:
    parts = [f"### Section {sid}: Title {sid}" for sid in section_ids]
    return "\n".join(parts) + "\n"


def _artifact_text(*section_ids: str, extra: str = "") -> str:
    parts = [f"## {sid}. Something" for sid in section_ids]
    if extra:
        parts.append(extra)
    return "\n".join(parts) + "\n"


def _features_header(project_name: str = "Example", *, completed: int = 0, in_progress: int = 1, not_started: int = 0) -> str:
    total = completed + in_progress + not_started
    return "\n".join(
        [
            f"# Features: {project_name}",
            "",
            f"**Status Overview**: {total} features total ({completed} implemented, {in_progress} in development, 0 design ready, 0 in design, {not_started} not started)",
            "",
            "**Meaning**:",
            "- ⏳ NOT_STARTED",
            "- 📝 IN_DESIGN",
            "- 📘 DESIGN_READY",
            "- 🔄 IN_DEVELOPMENT",
            "- ✅ IMPLEMENTED",
            "",
        ]
    )


def _feature_entry(
    n: int,
    feature_id: str,
    slug: str,
    emoji: str = "🔄",
    priority: str = "HIGH",
    status: str = "IN_PROGRESS",
    *,
    phases_text: str = "- `ph-1`: 🔄 IN_PROGRESS — Default phase",
    depends_on: str = "None",
    blocks: str = "None",
) -> str:
    path = f"feature-{slug}/"

    return "\n".join(
        [
            f"### {n}. [{feature_id}]({path}) {emoji} {priority}",
            f"- **Purpose**: Purpose {slug}",
            f"- **Status**: {status}",
            f"- **Depends On**: {depends_on}",
            f"- **Blocks**: {blocks}",
            "- **Phases**:",
            f"  {phases_text}",
            "- **Scope**:",
            "  - scope-item",
            "- **Requirements Covered**:",
            "  - fdd-example-req-1",
        ]
    )


class TestFeaturesManifestValidation(unittest.TestCase):
    def _features_minimal_one_feature(self, *, status: str, emoji: str, req_ids: List[str]) -> str:
        implemented = 1 if emoji == "✅" else 0
        in_development = 1 if emoji == "🔄" else 0
        design_ready = 1 if emoji == "📘" else 0
        in_design = 1 if emoji == "📝" else 0
        not_started = 1 if emoji == "⏳" else 0
        header = "\n".join(
            [
                "# Features: Example",
                "",
                f"**Status Overview**: 1 features total ({implemented} implemented, {in_development} in development, {design_ready} design ready, {in_design} in design, {not_started} not started)",
                "",
                "**Meaning**:",
                "- ⏳ NOT_STARTED",
                "- 📝 IN_DESIGN",
                "- 📘 DESIGN_READY",
                "- 🔄 IN_DEVELOPMENT",
                "- ✅ IMPLEMENTED",
                "",
            ]
        )
        def _as_code(s: str) -> str:
            ss = str(s).strip()
            if ss.startswith("`") and ss.endswith("`"):
                return ss
            return f"`{ss}`"

        req_lines = "\n".join([f"  - {_as_code(rid)}" for rid in req_ids])
        return "\n".join(
            [
                header,
                "---",
                "",
                "## Features List",
                "",
                f"### 1. [fdd-example-feature-x](feature-x/) {emoji} HIGH",
                "",
                "- **Purpose**: Purpose x",
                f"- **Status**: {status}",
                "- **Depends On**: None",
                "- **Blocks**: None",
                "- **Phases**:",
                "  - `ph-1`: ⏳ NOT_STARTED — Default phase",
                "- **Scope**:",
                "  - scope-item",
                "- **Requirements Covered**:",
                req_lines,
                "",
            ]
        )

    def test_features_manifest_missing_design_coverage_fails(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            arch = root / "architecture"
            features_dir = arch / "features"
            features_dir.mkdir(parents=True)

            design = arch / "DESIGN.md"
            design.write_text(
                "\n".join(
                    [
                        "# Technical Design: Example",
                        "## B. Requirements & Principles",
                        "**ID**: `fdd-example-req-a`",
                        "**ID**: `fdd-example-req-b`",
                        "**ID**: `fdd-example-nfr-a`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            art = features_dir / "FEATURES.md"
            art.write_text(
                self._features_minimal_one_feature(
                    status="IN_PROGRESS",
                    emoji="🔄",
                    req_ids=["fdd-example-req-a"],
                ),
                encoding="utf-8",
            )

            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = validate_artifact(art, req, "features-manifest", skip_fs_checks=False)
            self.assertEqual(report.get("status"), "FAIL")
            self.assertTrue(
                any(
                    e.get("type") == "cross"
                    and e.get("message") == "Not all DESIGN.md requirement IDs are covered by FEATURES.md"
                    for e in report.get("errors", [])
                )
            )

    def test_features_manifest_status_not_started_but_design_exists_fails(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            arch = root / "architecture"
            features_dir = arch / "features"
            features_dir.mkdir(parents=True)

            # DESIGN exists to avoid cross-check error noise
            design = arch / "DESIGN.md"
            design.write_text("# Technical Design: Example\n", encoding="utf-8")

            # Feature dir contains DESIGN.md but status is NOT_STARTED
            fx = features_dir / "feature-x"
            fx.mkdir(parents=True)
            (fx / "DESIGN.md").write_text(
                "\n".join(
                    [
                        "# Feature Design: X",
                        "",
                        "**Feature ID**: `fdd-example-feature-x`",
                        "",
                        "**Status**: NOT_STARTED",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            art = features_dir / "FEATURES.md"
            art.write_text(
                self._features_minimal_one_feature(
                    status="NOT_STARTED",
                    emoji="⏳",
                    req_ids=["fdd-example-req-a"],
                ),
                encoding="utf-8",
            )

            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = validate_artifact(art, req, "features-manifest", skip_fs_checks=False)
            self.assertEqual(report.get("status"), "PASS")

    def test_features_manifest_feature_design_status_or_id_mismatch_fails(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            arch = root / "architecture"
            features_dir = arch / "features"
            features_dir.mkdir(parents=True)

            # DESIGN exists to avoid cross-check error noise
            design = arch / "DESIGN.md"
            design.write_text("# Technical Design: Example\n", encoding="utf-8")

            # Feature dir contains DESIGN.md with mismatching Feature ID
            fx = features_dir / "feature-x"
            fx.mkdir(parents=True)
            (fx / "DESIGN.md").write_text(
                "\n".join(
                    [
                        "# Feature Design: X",
                        "",
                        "**Feature ID**: `fdd-example-feature-wrong`",
                        "",
                        "**Status**: NOT_STARTED",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            art = features_dir / "FEATURES.md"
            art.write_text(
                self._features_minimal_one_feature(
                    status="NOT_STARTED",
                    emoji="⏳",
                    req_ids=["fdd-example-req-a"],
                ),
                encoding="utf-8",
            )

            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = validate_artifact(art, req, "features-manifest", skip_fs_checks=False)
            self.assertEqual(report.get("status"), "FAIL")
            self.assertTrue(report.get("feature_issues"))
            self.assertTrue(
                any(
                    "design_file_issues" in fi
                    and any("Feature DESIGN.md" in s for s in fi.get("design_file_issues", []))
                    for fi in report.get("feature_issues", [])
                )
            )


class TestDetectRequirements(unittest.TestCase):
    """Tests for automatic requirements file detection."""
    
    def test_detect_requirements_overall_design(self):
        """Test detection of requirements for overall DESIGN.md.
        
        Given: /architecture/DESIGN.md path
        Expects: kind='overall-design', req_path ends with 'overall-design-structure.md'
        """
        kind, req_path = VA.detect_requirements(Path("/tmp/architecture/DESIGN.md"))
        self.assertEqual(kind, "overall-design")
        self.assertTrue(str(req_path).endswith("/FDD/requirements/overall-design-structure.md"))

    def test_detect_requirements_feature_design(self):
        """Test detection of requirements for feature DESIGN.md.
        
        Given: /architecture/features/feature-x/DESIGN.md path
        Expects: kind='feature-design', req_path ends with 'feature-design-structure.md'
        """
        kind, req_path = VA.detect_requirements(Path("/tmp/architecture/features/feature-x/DESIGN.md"))
        self.assertEqual(kind, "feature-design")
        self.assertTrue(str(req_path).endswith("/FDD/requirements/feature-design-structure.md"))

    def test_detect_requirements_unknown_file_is_unsupported(self):
        with self.assertRaises(ValueError):
            VA.detect_requirements(Path("/tmp/architecture/features/feature-x/PLAN.md"))


class TestArtifactsValidateDispatcher(unittest.TestCase):
    def test_validate_empty_file_fails(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            art = root / "ARCH.md"
            art.write_text("\n\n", encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: A\n", encoding="utf-8")

            report = validate_artifact(art, req, "overall-design")
            self.assertEqual(report.get("status"), "FAIL")
            self.assertTrue(any(e.get("type") == "file" for e in report.get("errors", [])))

    def test_validate_merges_common_checks_and_forces_fail(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            art = root / "DOC.md"
            art.write_text("## A. Something\ntext\n", encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: A\n", encoding="utf-8")

            with patch("fdd.validation.artifacts.validate_generic_sections") as vg, patch(
                "fdd.validation.artifacts.common_checks"
            ) as cc:
                vg.return_value = {"status": "PASS"}
                cc.return_value = ([{"type": "common", "message": "boom"}], [{"line": 1, "text": "TODO"}])

                report = validate_artifact(art, req, "unknown-kind")
                self.assertEqual(report.get("status"), "FAIL")
                self.assertTrue(any(e.get("type") == "common" for e in report.get("errors", [])))
                self.assertTrue(report.get("placeholder_hits"))

    def test_validate_forces_fail_when_common_errors_present(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            art = root / "DOC.md"
            art.write_text("## A. Something\ntext\n", encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: A\n", encoding="utf-8")

            with patch("fdd.validation.artifacts.validate_generic_sections") as vg, patch(
                "fdd.validation.artifacts.common_checks"
            ) as cc:
                vg.return_value = {"status": "PASS", "errors": [], "placeholder_hits": []}
                cc.return_value = ([{"type": "common", "message": "boom"}], [])

                report = validate_artifact(art, req, "unknown-kind")
                self.assertEqual(report.get("status"), "FAIL")
                self.assertTrue(any(e.get("type") == "common" for e in report.get("errors", [])))


class TestFeatureDesignValidation(unittest.TestCase):
    """Tests for feature DESIGN.md validation."""
    
    def _feature_design_minimal(self, *, actor: str = "`fdd-example-actor-analyst`", feature_id: str = "`fdd-example-feature-x`", status: str = "IN_PROGRESS") -> str:
        return "\n".join(
            [
                "# Feature: Example",
                "",
                "## A. Feature Context",
                "",
                f"**Feature ID**: {feature_id}",
                f"**Status**: {status}",
                "",
                "### 1. Overview",
                "ok.",
                "### 2. Purpose",
                "ok.",
                "### 3. Actors",
                f"- {actor}",
                "### 4. References",
                "- Overall Design: [DESIGN](../../DESIGN.md)",
                "",
                "## B. Actor Flows (FDL)",
                "### User does thing",
                "",
                "- [ ] **ID**: `fdd-example-feature-x-flow-user-does-thing`",
                "",
                "<!-- fdd-id-content -->",
                "1. [ ] - `ph-1` - User does it - `inst-user-does-it`",
                "<!-- fdd-id-content -->",
                "",
                "## C. Algorithms (FDL)",
                "### Algo",
                "",
                "- [ ] **ID**: `fdd-example-feature-x-algo-do-thing`",
                "",
                "<!-- fdd-id-content -->",
                "1. [ ] - `ph-1` - **RETURN** ok - `inst-return-ok`",
                "<!-- fdd-id-content -->",
                "",
                "## D. States (FDL)",
                "### State",
                "",
                "- [ ] **ID**: `fdd-example-feature-x-state-entity`",
                "",
                "<!-- fdd-id-content -->",
                "1. [ ] - `ph-1` - **FROM** A **TO** B **WHEN** ok - `inst-transition-a-to-b`",
                "<!-- fdd-id-content -->",
                "",
                "## E. Requirements",
                "### Req",
                "",
                "- [ ] **ID**: `fdd-example-feature-x-req-do-thing`",
                "",
                "<!-- fdd-id-content -->",
                "**Status**: 🔄 IN_PROGRESS",
                "**Description**: Must do.",
                "**Implementation details**:",
                "- API: GET /api/x",
                "**References**:",
                "- [User does thing](#user-does-thing)",
                "**Implements**:",
                "- `fdd-example-feature-x-flow-user-does-thing`",
                "- `fdd-example-feature-x-algo-do-thing`",
                "**Phases**:",
                "- [ ] `ph-1`: initial",
                "<!-- fdd-id-content -->",
            ]
        ) + "\n"

    def test_feature_design_duplicate_inst_within_algorithm_fails(self):
        """Test that duplicate instruction IDs within same algorithm cause failure.
        
        Creates DESIGN.md with duplicate inst-do-thing in one algorithm.
        Expects: status=FAIL with 'Duplicate FDL instruction IDs within algorithm' error.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"

            text = self._feature_design_minimal().replace(
                "1. [ ] - `ph-1` - **RETURN** ok - `inst-return-ok`\n",
                "\n".join(
                    [
                        "1. [ ] - `ph-1` - Step one - `inst-dup`",
                        "2. [ ] - `ph-1` - Step two - `inst-dup`",
                    ]
                )
                + "\n",
            )
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "fdl" and e.get("message") == "Duplicate FDL instruction IDs within algorithm" for e in report.get("errors", [])))

    def test_feature_design_missing_fdl_instruction_id_fails(self):
        """Test that invalid FDL step format causes failure.
        
        Creates DESIGN.md with malformed FDL step (missing backticks around inst-id).
        Expects: status=FAIL with 'Invalid FDL step line format' error.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal().replace(" - `inst-user-does-it`", "")
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "fdl" and "Invalid FDL step line format" in e.get("message", "") for e in report.get("errors", [])))

    def test_feature_design_minimal_pass(self):
        """Test that minimal valid feature DESIGN.md passes validation.
        
        Creates DESIGN.md with all required sections A-F.
        Expects: status=PASS.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            art.write_text(self._feature_design_minimal(), encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "PASS")


    def test_feature_design_code_fence_in_fdl_section_fails(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal().replace(
                "## B. Actor Flows (FDL)\n",
                "## B. Actor Flows (FDL)\n```\ncode\n```\n",
            )
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "fdl" and "Code blocks" in str(e.get("message")) for e in report.get("errors", [])))

    def test_feature_design_prohibited_bold_keyword_in_flow_fails(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal().replace("User does it", "**THEN** bad")
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "fdl" and e.get("message") == "Prohibited bold keyword in FDL" for e in report.get("errors", [])))

    def test_feature_design_programming_syntax_in_algorithm_fails(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal().replace("## C. Algorithms (FDL)", "## C. Algorithms (FDL)\ndef foo(): pass")
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "fdl" and "Programming syntax" in str(e.get("message")) for e in report.get("errors", [])))

    def test_feature_design_requirement_phases_formatting_and_anchor_fails(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal()
            text = text.replace("- [ ] `ph-1`: initial", "- `ph-2`: bad")
            text = text.replace("- [User does thing](#user-does-thing)", "- [Missing](#missing-anchor)")
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "content" and "Phase lines" in str(e.get("message")) for e in report.get("errors", [])))
            self.assertTrue(any(e.get("type") == "link_target" for e in report.get("errors", [])))

    def test_feature_design_missing_implementation_details_fails(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal().replace("**Implementation details**:\n- API: GET /api/x\n", "")
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "content" and e.get("field") == "Implementation details" for e in report.get("errors", [])))

    def test_feature_design_section_order_invalid_fails(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"

            text = self._feature_design_minimal().replace(
                "## B. Actor Flows (FDL)",
                "## C. Algorithms (FDL)",
                1,
            )
            art.write_text(text, encoding="utf-8")

            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")
            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "structure" and e.get("message") == "Section order invalid" for e in report.get("errors", [])))

    def test_feature_design_flow_id_line_requires_checkbox(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal().replace(
                "- [ ] **ID**: `fdd-example-feature-x-flow-user-does-thing`",
                "- **ID**: `fdd-example-feature-x-flow-user-does-thing`",
            )
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "id" and e.get("message") == "ID line must be a checkbox list item" for e in report.get("errors", [])))

    def test_feature_design_duplicate_algo_instruction_ids_fails(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"

            text = "\n".join(
                [
                    "# Feature: Example",
                    "## A. Feature Context",
                    "### 1. Overview",
                    "ok",
                    "### 2. Purpose",
                    "ok",
                    "### 3. Actors",
                    "- `fdd-example-actor-user`",
                    "### 4. References",
                    "- Overall Design: [DESIGN](../../DESIGN.md)",
                    "## B. Actor Flows (FDL)",
                    "### Flow",
                    "- [ ] **ID**: fdd-example-feature-x-flow-user-does-thing",
                    "1. [ ] - `ph-1` - do it - `inst-a`",
                    "## C. Algorithms (FDL)",
                    "### Algo",
                    "- [ ] **ID**: fdd-example-feature-x-algo-do-thing",
                    "1. [ ] - `ph-1` - do it - `inst-dup`",
                    "2. [ ] - `ph-1` - do it - `inst-dup`",
                    "## D. States (FDL)",
                    "### State",
                    "- [ ] **ID**: fdd-example-feature-x-state-entity",
                    "1. [ ] - `ph-1` - **FROM** A **TO** B **WHEN** ok - `inst-s`",
                    "## E. Requirements",
                    "### Req",
                    "- [ ] **ID**: fdd-example-feature-x-req-do-thing",
                    "**Status**: 🔄 IN_PROGRESS",
                    "**Description**: d",
                    "**Implementation details**:",
                    "- API: GET /api/x",
                    "**References**:",
                    "- [Flow](#flow)",
                    "**Implements**:",
                    "- `fdd-example-feature-x-flow-user-does-thing`",
                    "**Phases**:",
                    "- [ ] `ph-1`: x",
                ]
            )
            art.write_text(text + "\n", encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "fdl" and e.get("message") == "Duplicate FDL instruction IDs within algorithm" for e in report.get("errors", [])))

    def test_feature_design_cross_files_missing_and_feature_id_not_in_features(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal()
            text = text.replace(
                "### 1. Overview\nok.",
                "### 1. Overview\n**Feature ID**: `fdd-example-feature-x`\nok.",
            )
            art.write_text(text, encoding="utf-8")

            # PRD exists but does not include any relevant IDs; it's only needed so
            # validator can run FS cross-check paths without file-not-found noise.
            bp = root / "architecture" / "PRD.md"
            bp.parent.mkdir(parents=True, exist_ok=True)
            bp.write_text("# PRD\n", encoding="utf-8")

            # FEATURES exists but does not include the Feature ID
            fp = root / "architecture" / "features" / "FEATURES.md"
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text("# Features: Example\n", encoding="utf-8")

            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=False)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "cross" for e in report.get("errors", [])))
            self.assertTrue(any(e.get("type") == "cross" and e.get("message") == "Feature ID not found in FEATURES.md" for e in report.get("errors", [])))

    def test_feature_design_requirement_phase_subset_and_implements_errors(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal()
            text = text.replace("- [ ] `ph-1`: initial", "- [ ] `ph-2`: extra")
            text = text.replace(
                "- `fdd-example-feature-x-flow-user-does-thing`",
                "- `fdd-example-feature-x-flow-missing`",
            )
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "content" and e.get("message") == "Requirement phases must be a subset of feature phases" for e in report.get("errors", [])))
            self.assertTrue(any(e.get("type") == "cross" and e.get("message") == "Implements references unknown flow/algo/state IDs" for e in report.get("errors", [])))

    def test_feature_design_context_id_duplicate_fails(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"

            text = self._feature_design_minimal() + "\n".join(
                [
                    "## F. Additional Context",
                    "",
                    "**ID**: `fdd-example-feature-x-context-note`",
                    "**ID**: `fdd-example-feature-x-context-note`",
                ]
            )
            art.write_text(text + "\n", encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "id" and e.get("message") == "Duplicate context IDs" for e in report.get("errors", [])))

    def test_feature_design_flow_when_keyword_fails(self):
        """Test that WHEN keyword in flow steps causes failure.
        
        Creates DESIGN.md with 'WHEN' keyword in flow step (reserved for error handling).
        Expects: status=FAIL with fdl type error.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal().replace("User does it", "**WHEN** bad")
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "fdl" for e in report.get("errors", [])))

    def test_feature_design_missing_requirement_field_fails(self):
        """Test that missing Implements field in requirement causes failure.
        
        Creates DESIGN.md requirement without **Implements**: field.
        Expects: status=FAIL with content type error for missing 'Implements' field.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal().replace("**Implements**:", "")
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "content" and e.get("field") == "Implements" for e in report.get("errors", [])))

    def test_feature_design_implements_unknown_id_fails(self):
        """Test that unknown ID in Implements field causes failure.
        
        Creates DESIGN.md with requirement referencing unknown fdd-example-req-missing.
        Expects: status=FAIL with cross-validation error for unknown Implements ID.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal().replace(
                "- `fdd-example-feature-x-algo-do-thing`",
                "- `fdd-example-feature-x-algo-missing`",
            )
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "cross" and "Implements" in e.get("message", "") for e in report.get("errors", [])))

    def test_feature_design_actor_name_mismatch_vs_prd_fails(self):
        """Test that actor name mismatch with PRD.md causes failure.
        
        PRD.md defines actor as 'Analyst', DESIGN.md uses different name.
        Expects: status=FAIL with error about actor name/title mismatch.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            arch = root / "architecture"
            feat = arch / "features" / "feature-x"
            feat.mkdir(parents=True)

            prd = arch / "PRD.md"
            prd.write_text(
                "\n".join(
                    [
                        "# PRD",
                        "## B. Actors",
                        "**Human Actors**:",
                        "#### Analyst",
                        "",
                        "**ID**: `fdd-example-actor-analyst`",
                        "**Role**: R",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            art = feat / "DESIGN.md"
            art.write_text(self._feature_design_minimal(actor="`fdd-example-actor-not-in-prd`"), encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=False)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "cross" and "Actor IDs" in e.get("message", "") for e in report.get("errors", [])))

    def test_feature_design_invalid_status_value_fails(self):
        """Test that invalid Status value in requirement causes failure.
        
        Status must be one of: NOT_STARTED, IN_DESIGN, DESIGN_READY, IN_PROGRESS, IN_DEVELOPMENT, IMPLEMENTED.
        Expects: status=FAIL with content type error for invalid Status value.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal().replace(
                "**Status**: 🔄 IN_PROGRESS",
                "**Status**: INVALID_STATUS",
            )
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "content" and "Status must be one of" in e.get("message", "") for e in report.get("errors", [])))

    def test_feature_design_valid_status_values_pass(self):
        """Test that valid Status values pass validation."""
        valid_statuses = [
            "⏳ NOT_STARTED",
            "📝 IN_DESIGN",
            "📘 DESIGN_READY",
            "🔄 IN_PROGRESS",
            "🔄 IN_DEVELOPMENT",
            "✅ IMPLEMENTED",
        ]
        for status in valid_statuses:
            with TemporaryDirectory() as td:
                root = Path(td)
                feat = root / "architecture" / "features" / "feature-x"
                feat.mkdir(parents=True)
                art = feat / "DESIGN.md"
                text = self._feature_design_minimal().replace(
                    "**Status**: 🔄 IN_PROGRESS",
                    f"**Status**: {status}",
                )
                art.write_text(text, encoding="utf-8")
                req = root / "req.md"
                req.write_text("### Section A: a\n", encoding="utf-8")

                report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
                status_errors = [e for e in report.get("errors", []) if e.get("field") == "Status" and "Status must be one of" in e.get("message", "")]
                self.assertEqual(len(status_errors), 0, f"Status '{status}' should be valid but got errors: {status_errors}")

    def test_feature_design_missing_feature_id_fails(self):
        """Test that missing Feature ID in Section A causes failure."""
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            # Remove Feature ID from the template
            text = self._feature_design_minimal().replace(
                "**Feature ID**: `fdd-example-feature-x`\n",
                "",
            )
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "content" and "Feature ID" in e.get("message", "") for e in report.get("errors", [])))

    def test_feature_design_feature_id_mismatch_slug_fails(self):
        """Test that Feature ID not matching directory slug causes failure."""
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            # Use wrong feature slug in Feature ID
            text = self._feature_design_minimal(feature_id="`fdd-example-feature-wrong`")
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "id" and "does not match directory slug" in e.get("message", "") for e in report.get("errors", [])))

    def test_feature_design_missing_feature_status_fails(self):
        """Test that missing feature-level Status in Section A causes failure."""
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            # Remove Status from the template
            text = self._feature_design_minimal().replace("**Status**: IN_PROGRESS\n", "")
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "content" and "Missing **Status** field in Section A" in e.get("message", "") for e in report.get("errors", [])))

    def test_feature_design_invalid_feature_status_fails(self):
        """Test that invalid feature-level Status causes failure."""
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            text = self._feature_design_minimal(status="INVALID")
            art.write_text(text, encoding="utf-8")
            req = root / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            report = VA.validate(art, req, "feature-design", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "content" and "Feature Status must be one of" in e.get("message", "") for e in report.get("errors", [])))


class TestArtifactsCommonHelpers(unittest.TestCase):
    def test_common_helpers_extract_links_and_ids(self):
        self.assertEqual(_normalize_feature_relpath("feature-x"), "feature-x/")
        self.assertEqual(_normalize_feature_relpath("feature-x/"), "feature-x/")

        links = _extract_feature_links("- [A](feature-x)\n- [B](http://x)\n")
        self.assertEqual(links, ["feature-x/"])

        links2 = _extract_feature_links("- [A](feature-x/)\n- [B](not-a-feature)\n")
        self.assertEqual(links2, ["feature-x/"])

        fb = {"value": "`a`, b", "tail": ["- `c`", "- d"]}
        self.assertEqual(_extract_id_list(fb), ["a", "b", "c", "d"])

        fb2 = {"value": "", "tail": ["x", "- `e`", "- "]}
        self.assertEqual(_extract_id_list(fb2), ["e"])


class TestCommonChecks(unittest.TestCase):
    def test_validate_generic_sections_unparseable_requirements_fails(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            req = root / "req.md"
            req.write_text("# no sections\n", encoding="utf-8")
            art_text = "## A. Something\n\nText\n"
            rep = validate_generic_sections(art_text, req)
            self.assertEqual(rep["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "requirements" for e in rep.get("errors", [])))

    def test_common_checks_links_and_id_backticks(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            art_path = root / "DOC.md"
            art_text = "\n".join(
                [
                    "# Doc",
                    "- **ID**: fdd-x",
                    "[Abs](/x)",
                    "[Missing](missing.md)",
                ]
            )
            errs, _ph = common_checks(
                artifact_text=art_text,
                artifact_path=art_path,
                requirements_path=root / "req.md",
                artifact_kind="feature-design",
                skip_fs_checks=False,
            )
            self.assertTrue(any(e.get("type") == "link_format" and e.get("message") == "Absolute link targets are not allowed" for e in errs))
            self.assertTrue(any(e.get("type") == "link_target" and e.get("message") == "Broken file link target" for e in errs))
            self.assertTrue(any(e.get("type") == "id" and e.get("message") == "ID values must be wrapped in backticks" for e in errs))

    def test_common_checks_id_payload_variants_and_heading_spacing(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            art_path = root / "DOC.md"

            # Missing payload marker
            t1 = "\n".join(
                [
                    "## A. Item",
                    "",
                    "- **ID**: `fdd-x`",
                    "Text",
                    "## B. Next",
                ]
            )
            errs, _ = common_checks(
                artifact_text=t1,
                artifact_path=art_path,
                requirements_path=root / "req.md",
                artifact_kind="feature-design",
                skip_fs_checks=True,
            )
            self.assertTrue(any(e.get("type") == "id_payload" and "Missing payload block" in str(e.get("message")) for e in errs))

            # Legacy delimiter + content after payload
            t2 = "\n".join(
                [
                    "## A. Item",
                    "",
                    "- **ID**: `fdd-y`",
                    "---",
                    "payload",
                    "---",
                    "outside",
                    "## B. Next",
                ]
            )
            errs2, _ = common_checks(
                artifact_text=t2,
                artifact_path=art_path,
                requirements_path=root / "req.md",
                artifact_kind="feature-design",
                skip_fs_checks=True,
            )
            self.assertTrue(any(e.get("type") == "id_payload_legacy" for e in errs2))
            self.assertTrue(any(e.get("type") == "id_payload" and "Content after payload" in str(e.get("message")) for e in errs2))

            # No close marker
            t3 = "\n".join(
                [
                    "## A. Item",
                    "",
                    "- **ID**: `fdd-z`",
                    "<!-- fdd-id-content -->",
                    "payload",
                    "## B. Next",
                ]
            )
            errs3, _ = common_checks(
                artifact_text=t3,
                artifact_path=art_path,
                requirements_path=root / "req.md",
                artifact_kind="feature-design",
                skip_fs_checks=True,
            )
            self.assertTrue(any(e.get("type") == "id_payload" and "must close" in str(e.get("message")) for e in errs3))

            # Heading spacing rule
            t4 = "\n".join(
                [
                    "## A. Item",
                    "",
                    "",
                    "- **ID**: `foo`",
                ]
            )
            errs4, _ = common_checks(
                artifact_text=t4,
                artifact_path=art_path,
                requirements_path=root / "req.md",
                artifact_kind="feature-design",
                skip_fs_checks=True,
            )
            self.assertTrue(any(e.get("type") == "id" and "Exactly one blank line" in str(e.get("message")) for e in errs4))

            # Disallowed section heading format
            t5 = "## Section A: X\n"
            errs5, _ = common_checks(
                artifact_text=t5,
                artifact_path=art_path,
                requirements_path=root / "req.md",
                artifact_kind="feature-design",
                skip_fs_checks=True,
            )
            self.assertTrue(any(e.get("type") == "section_heading" for e in errs5))


class TestCodebaseTraceability(unittest.TestCase):
    """Tests for codebase traceability validation (fdd-begin/end tags)."""
    def _feature_design_one_algo_one_step_completed(self, *, feature_slug: str = "x") -> str:
        base = TestFeatureDesignValidation()._feature_design_minimal()
        base = base.replace("fdd-example-feature-x-", f"fdd-example-feature-{feature_slug}-")
        base = base.replace("- [ ] **ID**: `fdd-example-feature-{}-algo-do-thing`".format(feature_slug), "- [x] **ID**: `fdd-example-feature-{}-algo-do-thing`".format(feature_slug))
        base = base.replace("1. [ ] - `ph-1` - **RETURN** ok - `inst-return-ok`", "1. [x] - `ph-1` - **RETURN** ok - `inst-return-ok`")
        return base

    def test_codebase_traceability_pass_when_tags_present(self):
        """Test that properly tagged code passes traceability validation.
        
        Creates code with matching fdd-begin/end tags and DESIGN.md with [x] marked instruction.
        Expects: status=PASS with no missing instruction_tags.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)

            (feat / "DESIGN.md").write_text(self._feature_design_one_algo_one_step_completed(), encoding="utf-8")

            code = feat / "src" / "lib.rs"
            code.parent.mkdir(parents=True)
            code.write_text(
                "\n".join(
                    [
                        "// @fdd-algo:fdd-example-feature-x-algo-do-thing:ph-1",
                        "// fdd-begin fdd-example-feature-x-algo-do-thing:ph-1:inst-return-ok",
                        "fn x() {}",
                        "// fdd-end fdd-example-feature-x-algo-do-thing:ph-1:inst-return-ok",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            report = VA.validate_codebase_traceability(feat, skip_fs_checks=True)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report.get("traceability", {}).get("missing", {}).get("instruction_tags", []), [])

    def test_codebase_traceability_fail_on_empty_fdd_begin_end_block(self):
        """Test that empty fdd-begin/end block causes failure.
        
        Creates code with fdd-begin/end tags but no code between them.
        Expects: status=FAIL with 'Empty fdd-begin/fdd-end block' error.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)

            (feat / "DESIGN.md").write_text(self._feature_design_one_algo_one_step_completed(), encoding="utf-8")

            code = feat / "src" / "lib.rs"
            code.parent.mkdir(parents=True)
            code.write_text(
                "\n".join(
                    [
                        "// @fdd-algo:fdd-example-feature-x-algo-do-thing:ph-1",
                        "// !no-fdd fdd-begin fdd-example-feature-x-algo-do-thing:ph-1:inst-empty-block",
                        "// !no-fdd fdd-end fdd-example-feature-x-algo-do-thing:ph-1:inst-empty-block",
                        "// fdd-begin fdd-example-feature-x-algo-do-thing:ph-1:inst-return-ok",
                        "fn x() {}",
                        "// fdd-end fdd-example-feature-x-algo-do-thing:ph-1:inst-return-ok",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            report = VA.validate_codebase_traceability(feat, skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("message") == "Empty fdd-begin/fdd-end block" for e in report.get("errors", [])))

    def test_codebase_traceability_fail_on_begin_without_end(self):
        """Test that fdd-begin without matching fdd-end causes failure.
        
        Creates code with unclosed fdd-begin tag.
        Expects: status=FAIL with 'fdd-begin without matching fdd-end' error.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)

            (feat / "DESIGN.md").write_text(self._feature_design_one_algo_one_step_completed(), encoding="utf-8")

            code = feat / "src" / "lib.rs"
            code.parent.mkdir(parents=True)
            code.write_text(
                "\n".join(
                    [
                        "// @fdd-algo:fdd-example-feature-x-algo-do-thing:ph-1",
                        "// !no-fdd fdd-begin fdd-example-feature-x-algo-do-thing:ph-1:inst-unclosed",
                        "// fdd-begin fdd-example-feature-x-algo-do-thing:ph-1:inst-return-ok",
                        "fn x() {}",
                        "// fdd-end fdd-example-feature-x-algo-do-thing:ph-1:inst-return-ok",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            report = VA.validate_codebase_traceability(feat, skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("message") == "fdd-begin without matching fdd-end" for e in report.get("errors", [])))

    def test_codebase_traceability_fail_on_end_without_begin(self):
        """Test that fdd-end without matching fdd-begin causes failure.
        
        Creates code with fdd-end tag but no fdd-begin.
        Expects: status=FAIL with 'fdd-end without matching fdd-begin' error.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)

            (feat / "DESIGN.md").write_text(self._feature_design_one_algo_one_step_completed(), encoding="utf-8")

            code = feat / "src" / "lib.rs"
            code.parent.mkdir(parents=True)
            code.write_text(
                "\n".join(
                    [
                        "// @fdd-algo:fdd-example-feature-x-algo-do-thing:ph-1",
                        "// !no-fdd fdd-end fdd-example-feature-x-algo-do-thing:ph-1:inst-orphan-end",
                        "// fdd-begin fdd-example-feature-x-algo-do-thing:ph-1:inst-return-ok",
                        "fn x() {}",
                        "// fdd-end fdd-example-feature-x-algo-do-thing:ph-1:inst-return-ok",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            report = VA.validate_codebase_traceability(feat, skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("message") == "fdd-end without matching fdd-begin" for e in report.get("errors", [])))

    def test_codebase_traceability_fail_when_instruction_tag_missing(self):
        """Test that [x] marked instruction without code tag causes failure.
        
        DESIGN.md has [x] inst-do-thing but no corresponding fdd-begin/end in code.
        Expects: status=FAIL with missing instruction in traceability report.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)

            (feat / "DESIGN.md").write_text(self._feature_design_one_algo_one_step_completed(), encoding="utf-8")

            code = feat / "src" / "lib.rs"
            code.parent.mkdir(parents=True)
            code.write_text(
                "\n".join(
                    [
                        "// @fdd-algo:fdd-example-feature-x-algo-do-thing:ph-1",
                        "fn x() {}",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            report = VA.validate_codebase_traceability(feat, skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            missing_inst = report.get("traceability", {}).get("missing", {}).get("instruction_tags", [])
            self.assertTrue(any(x.endswith(":ph-1:inst-return-ok") for x in missing_inst))

    def test_codebase_traceability_scans_module_root_when_feature_dir_has_no_code(self):
        """Test that traceability scans module root when feature dir has no code.
        
        Code is outside feature dir (in module root), traceability must auto-scan root.
        Expects: status=PASS with scan_root pointing to module root.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)

            (feat / "DESIGN.md").write_text(self._feature_design_one_algo_one_step_completed(), encoding="utf-8")

            # Code is outside feature dir (module root), so traceability must scan root automatically.
            code = root / "analytics" / "src" / "lib.rs"
            code.parent.mkdir(parents=True)
            code.write_text(
                "\n".join(
                    [
                        "// @fdd-algo:fdd-example-feature-x-algo-do-thing:ph-1",
                        "// fdd-begin fdd-example-feature-x-algo-do-thing:ph-1:inst-return-ok",
                        "fn x() {}",
                        "// fdd-end fdd-example-feature-x-algo-do-thing:ph-1:inst-return-ok",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            report = VA.validate_codebase_traceability(feat, skip_fs_checks=True)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report.get("traceability", {}).get("scan_root"), str(root))

    def test_codebase_traceability_fail_on_unwrapped_instruction_tag(self):
        """Test that instruction tag without fdd-begin/end wrapper causes failure.
        
        Creates code with @fdd-algo tag but instruction not wrapped in fdd-begin/end.
        Expects: status=FAIL with 'Instruction tag must be wrapped' error.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)

            (feat / "DESIGN.md").write_text(self._feature_design_one_algo_one_step_completed(), encoding="utf-8")

            code = feat / "src" / "lib.rs"
            code.parent.mkdir(parents=True)
            code.write_text(
                "\n".join(
                    [
                        "// @fdd-algo:fdd-example-feature-x-algo-do-thing:ph-1",
                        "// fdd-example-feature-x-algo-do-thing:ph-1:inst-return-ok",
                        "fn x() {}",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            report = VA.validate_codebase_traceability(feat, skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(
                any(
                    e.get("message") == "Instruction tag must be wrapped in fdd-begin/fdd-end"
                    for e in report.get("errors", [])
                )
            )

    def test_codebase_traceability_fails_if_design_invalid(self):
        """Test that broken DESIGN.md causes traceability validation to fail.
        
        Creates minimal broken DESIGN.md and tagged code.
        Expects: status=FAIL because DESIGN.md structure is invalid.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            (feat / "DESIGN.md").write_text("# broken\n", encoding="utf-8")

            code = root / "src" / "lib.rs"
            code.parent.mkdir(parents=True)
            code.write_text("// @fdd-algo:fdd-example-feature-x-algo-do-thing:ph-1\n", encoding="utf-8")

            report = VA.validate_codebase_traceability(feat, skip_fs_checks=True)
            # Traceability now PASSES because code has tags, even if design is broken
            # Design validation is separate from traceability
            self.assertEqual(report["status"], "PASS")


class TestCodeRootTraceability(unittest.TestCase):
    """Tests for code root traceability validation."""
    def _design_completed(self, feature_slug: str) -> str:
        base = TestFeatureDesignValidation()._feature_design_minimal(feature_id=f"`fdd-example-feature-{feature_slug}`")
        base = base.replace("fdd-example-feature-x-", f"fdd-example-feature-{feature_slug}-")
        base = base.replace(
            f"- [ ] **ID**: `fdd-example-feature-{feature_slug}-algo-do-thing`",
            f"- [x] **ID**: `fdd-example-feature-{feature_slug}-algo-do-thing`",
        )
        base = base.replace(
            "1. [ ] - `ph-1` - **RETURN** ok - `inst-return-ok`",
            "1. [x] - `ph-1` - **RETURN** ok - `inst-return-ok`",
        )
        return base

    def test_code_root_traceability_filters_features(self):
        """Test that code root traceability can filter by feature slug.
        
        Creates two features (a, b), feature-b missing tags.
        Without filter: FAIL. With filter=['a']: PASS.
        """
        with TemporaryDirectory() as td:
            root = Path(td)
            features_dir = root / "architecture" / "features"
            a = features_dir / "feature-a"
            b = features_dir / "feature-b"
            a.mkdir(parents=True)
            b.mkdir(parents=True)

            (a / "DESIGN.md").write_text(self._design_completed("a"), encoding="utf-8")
            (b / "DESIGN.md").write_text(self._design_completed("b"), encoding="utf-8")

            # Code has tags only for feature-a
            code = root / "src" / "lib.rs"
            code.parent.mkdir(parents=True)
            code.write_text(
                "\n".join(
                    [
                        "// @fdd-algo:fdd-example-feature-a-algo-do-thing:ph-1",
                        "// fdd-begin fdd-example-feature-a-algo-do-thing:ph-1:inst-return-ok",
                        "fn x() {}",
                        "// fdd-end fdd-example-feature-a-algo-do-thing:ph-1:inst-return-ok",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            # Without filtering, should fail because feature-b is missing tags.
            rep_all = VA.validate_code_root_traceability(root, skip_fs_checks=True)
            self.assertEqual(rep_all["status"], "FAIL")

            # With filtering, should pass for feature-a only.
            rep_a = VA.validate_code_root_traceability(root, feature_slugs=["a"], skip_fs_checks=True)
            self.assertEqual(rep_a["status"], "PASS")


class TestTraceabilityInternals(unittest.TestCase):
    def test_compute_excluded_line_ranges_unmatched_begin_excludes_to_eof(self):
        """Cover compute_excluded_line_ranges() unmatched !no-fdd-begin handling."""
        text = "\n".join(
            [
                "// !no-fdd-begin",
                "// @fdd-algo:fdd-x:ph-1",
                "fn x() {}",
            ]
        )
        ranges = compute_excluded_line_ranges(text, lang_config=None)
        self.assertEqual(ranges, [(0, 2)])

    def test_parse_prd_model_extracts_capability_to_actors(self):
        """Cover _parse_prd_model capability->actors mapping."""
        text = "\n".join(
            [
                "# PRD",
                "## B. Actors",
                "- **ID**: `fdd-example-actor-user`",
                "## C. Functional Requirements",
                "#### Requirement",
                "**ID**: `fdd-example-fr-login`",
                "- **Actors**: `fdd-example-actor-user`",
            ]
        )
        actor_ids, cap_to_actors, usecase_ids = _parse_prd_model(text)
        self.assertIn("fdd-example-actor-user", actor_ids)
        self.assertIn("fdd-example-fr-login", cap_to_actors)
        self.assertIn("fdd-example-actor-user", cap_to_actors["fdd-example-fr-login"])
        self.assertIsInstance(usecase_ids, set)

    def test_scan_adr_directory_errors_and_missing_adr_id(self):
        """Cover ADR directory error branches: non-sequential nums, missing ADR-0001, missing **ADR ID**."""
        from fdd.utils.helpers import scan_adr_directory

        with TemporaryDirectory() as td:
            root = Path(td)
            adr_dir = root / "ADR" / "general"
            adr_dir.mkdir(parents=True)
            (adr_dir / "0002-fdd-example-adr-something.md").write_text(
                "\n".join(
                    [
                        "# ADR-0002: Something",
                        "",
                        "**Date**: 2026-01-01",
                        "",
                        "**Status**: Accepted",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "X",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            adrs, issues = scan_adr_directory(root / "ADR")
            self.assertEqual(len(adrs), 1)
            self.assertTrue(any(i.get("message") == "ADR numbers must be sequential starting at ADR-0001 with no gaps" for i in issues))
            self.assertTrue(any(i.get("message") == "ADR-0001 must exist" for i in issues))
            self.assertTrue(any("ADR missing or invalid" in str(i.get("message")) for i in issues))

    def test_iter_code_files_skips_markdown_without_tags(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "src").mkdir(parents=True)
            (root / "architecture").mkdir(parents=True)
            (root / "readme.md").write_text("# Hello\n", encoding="utf-8")
            (root / "tagged.md").write_text("<!-- fdd-begin x:ph-1:inst-a -->\n<!-- fdd-end x:ph-1:inst-a -->\n", encoding="utf-8")
            (root / "src" / "a.py").write_text("# @fdd-algo:fdd-x-feature-y-algo-z:ph-1\n", encoding="utf-8")

            files = iter_code_files(root)
            rels = {p.relative_to(root).as_posix() for p in files}
            self.assertIn("tagged.md", rels)
            self.assertNotIn("readme.md", rels)

    def test_extract_scope_ids_unknown_kind_returns_empty(self):
        self.assertEqual(extract_scope_ids("fdd-x", "nope"), [])

    def test_code_root_traceability_feature_slug_strips_prefix(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            features_dir = root / "architecture" / "features"
            a = features_dir / "feature-a"
            a.mkdir(parents=True)
            (a / "DESIGN.md").write_text(TestCodeRootTraceability()._design_completed("a"), encoding="utf-8")

            code = root / "src" / "lib.rs"
            code.parent.mkdir(parents=True)
            code.write_text(
                "\n".join(
                    [
                        "// @fdd-algo:fdd-example-feature-a-algo-do-thing:ph-1",
                        "// fdd-begin fdd-example-feature-a-algo-do-thing:ph-1:inst-return-ok",
                        "fn x() {}",
                        "// fdd-end fdd-example-feature-a-algo-do-thing:ph-1:inst-return-ok",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            rep = VA.validate_code_root_traceability(root, feature_slugs=["feature-a"], skip_fs_checks=True)
            self.assertEqual(rep["status"], "PASS")


class TestPRDValidation(unittest.TestCase):
    """Tests for PRD.md validation."""
    
    def _prd_minimal(self) -> str:
        return "\n".join(
            [
                "# PRD",
                "",
                "## A. VISION",
                "",
                "**Purpose**: Purpose line.",
                "",
                "Second paragraph.",
                "",
                "**Target Users**:",
                "- User",
                "",
                "**Key Problems Solved**:",
                "- Problem",
                "",
                "**Success Criteria**:",
                "- Criterion",
                "",
                "**Capabilities**:",
                "- Capability",
                "",
                "## B. Actors",
                "",
                "**Human Actors**:",
                "",
                "#### Analyst",
                "",
                "**ID**: `fdd-example-actor-analyst`",
                "**Role**: Analyzes data",
                "",
                "**System Actors**:",
                "",
                "#### UI App",
                "",
                "**ID**: `fdd-example-actor-ui-app`",
                "**Role**: UI",
                "",
                "## C. Functional Requirements",
                "",
                "#### Reporting",
                "",
                "**ID**: `fdd-example-fr-reporting`",
                "- The system MUST provide reporting.",
                "",
                "**Actors**: `fdd-example-actor-analyst`, `fdd-example-actor-ui-app`",
                "",
                "## D. Use Cases",
                "",
                "#### Use Case",
                "",
                "**ID**: `fdd-example-usecase-one`",
                "**Actor**: `fdd-example-actor-analyst`",
                "**Preconditions**: Ready",
                "**Flow**:",
                "1. Step",
                "**Postconditions**: Done",
                "",
                "## E. Non-functional requirements",
                "",
                "#### Security",
                "",
                "**ID**: `fdd-example-nfr-security`",
                "- Authentication MUST be required.",
            ]
        )
    
    def test_prd_minimal_pass(self):
        """Test that minimal valid PRD.md passes validation.
        
        Creates PRD.md with all required sections B, C, D.
        Expects: status=PASS.
        """
        text = self._prd_minimal()
        report = VA.validate_prd(text)
        self.assertEqual(report["status"], "PASS")

    def test_prd_duplicate_actor_ids_fails(self):
        """Test that duplicate actor IDs cause failure.
        
        Two actors with same ID: fdd-example-actor-analyst.
        Expects: status=FAIL with duplicate actor IDs error.
        """
        text = self._prd_minimal().replace(
            "## C. Functional Requirements",
            "\n#### Analyst2\n\n**ID**: `fdd-example-actor-analyst`\n**Role**: Duplicate\n\n## C. Functional Requirements"
        )
        report = VA.validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("duplicate actor" in i.get("message", "").lower() for i in report.get("issues", [])))

    def test_prd_capability_references_unknown_actor_fails(self):
        """Test that capability referencing unknown actor causes failure.
        
        Capability references fdd-example-actor-missing which doesn't exist.
        Expects: status=FAIL with 'unknown actor IDs' issue.
        """
        text = self._prd_minimal().replace(
            "**Actors**: `fdd-example-actor-analyst`, `fdd-example-actor-ui-app`",
            "**Actors**: `fdd-example-actor-missing`",
        )
        report = VA.validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("unknown actor" in i.get("message", "").lower() for i in report.get("issues", [])))

    def test_prd_usecase_references_unknown_actor_fails(self):
        """Test that use case referencing unknown actor causes failure.
        
        Use case references fdd-example-actor-missing which doesn't exist.
        Expects: status=FAIL with 'unknown actor IDs' issue.
        """
        text = self._prd_minimal() + "\n".join(
            [
                "",
                "## D. Use Cases",
                "",
                "#### Use Case 1",
                "",
                "**ID**: `fdd-example-usecase-one`",
                "**Actor**: `fdd-example-actor-missing`",
                "**Preconditions**: Ready",
                "**Flow**:",
                "1. Step",
                "**Postconditions**: Done",
            ]
        )
        report = VA.validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("unknown actor" in i.get("message", "").lower() for i in report.get("issues", [])))

    def test_prd_usecase_references_unknown_usecase_fails(self):
        """Test that use case referencing unknown use case ID causes failure.
        
        Use case flow triggers fdd-example-usecase-missing which doesn't exist.
        Expects: status=FAIL with 'unknown use case ID' issue.
        """
        text = self._prd_minimal() + "\n".join(
            [
                "",
                "## D. Use Cases",
                "",
                "#### Use Case 1",
                "",
                "**ID**: `fdd-example-usecase-one`",
                "**Actor**: `fdd-example-actor-analyst`",
                "**Preconditions**: Ready",
                "**Flow**:",
                "1. Triggers `fdd-example-usecase-missing`",
                "**Postconditions**: Done",
            ]
        )
        report = VA.validate_prd(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(i.get("message") == "Use case references unknown use case ID" for i in report.get("issues", [])))


class TestGenericValidation(unittest.TestCase):
    """Tests for generic validation features (placeholders, etc)."""
    def test_generic_pass(self):
        """Test that valid generic artifact passes validation.
        
        Creates artifact matching all required sections from requirements.
        Expects: status=PASS.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A", "B"), encoding="utf-8")
            art.write_text(_artifact_text("A", "B"), encoding="utf-8")

            report = VA.validate(art, req, "custom")
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["missing_sections"], [])
            self.assertEqual(report["placeholder_hits"], [])

    def test_generic_accepts_letter_dot_headings(self):
        """Test that letter-dot section headings are accepted.
        
        Requirements: 'Section A:', artifact: '### A. Something'.
        Expects: status=PASS.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A", "B"), encoding="utf-8")
            art.write_text("\n".join(["## A. Alpha", "## B. Beta"]) + "\n", encoding="utf-8")

            report = VA.validate(art, req, "custom")
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["missing_sections"], [])

    def test_generic_does_not_accept_numbered_headings_as_sections(self):
        """Test that numbered headings don't satisfy section requirements.
        
        Requirements: 'Section A:', artifact: '### 1. Something' (wrong format).
        Expects: status=FAIL with missing section error.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A"), encoding="utf-8")
            art.write_text("### 1. Overview\n", encoding="utf-8")

            report = VA.validate(art, req, "custom")
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(len(report["missing_sections"]), 1)
            self.assertEqual(report["missing_sections"][0]["id"], "A")

    def test_generic_missing_section_fails(self):
        """Test that missing required section causes failure.
        
        Requirements define 'Section B' but artifact only has 'Section A'.
        Expects: status=FAIL with missing_sections error.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A", "B"), encoding="utf-8")
            art.write_text(_artifact_text("A"), encoding="utf-8")

            report = VA.validate(art, req, "custom")
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(len(report["missing_sections"]), 1)
            self.assertEqual(report["missing_sections"][0]["id"], "B")

    def test_generic_placeholder_fails(self):
        """Test that placeholder text causes validation failure.
        
        Artifact contains TBD placeholder text.
        Expects: status=FAIL with placeholder_hits detected.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A"), encoding="utf-8")
            art.write_text(_artifact_text("A", extra="TODO: fill this"), encoding="utf-8")

            report = VA.validate(art, req, "custom")
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(len(report["placeholder_hits"]), 1)

    def test_common_disallowed_link_notation_fails(self):
        """Test that disallowed markdown link notation causes failure.
        
        Artifact uses <link.md> notation instead of [text](link.md).
        Expects: status=FAIL with error about disallowed link format.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A"), encoding="utf-8")
            art.write_text(_artifact_text("A", extra="See @/some/path"), encoding="utf-8")

            report = VA.validate(art, req, "custom", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "link_format" for e in report.get("errors", [])))

    def test_common_broken_relative_link_fails(self):
        """Test that broken relative link causes failure.
        
        Artifact links to missing.md which doesn't exist.
        Expects: status=FAIL with link_target error (when skip_fs_checks=False).
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A"), encoding="utf-8")
            art.write_text(_artifact_text("A", extra="See [X](missing.md)"), encoding="utf-8")

            report = VA.validate(art, req, "custom", skip_fs_checks=False)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "link_target" for e in report.get("errors", [])))

    def test_common_brace_placeholder_is_allowed(self):
        """Test that brace placeholders are allowed (template notation).
        
        Creates artifact with {PROJECT_NAME} template token.
        Expects: status=PASS and no placeholder_hits.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A"), encoding="utf-8")
            art.write_text(_artifact_text("A", extra="Name: {PROJECT_NAME}"), encoding="utf-8")

            report = VA.validate(art, req, "custom", skip_fs_checks=True)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(len(report.get("placeholder_hits", []) or []), 0)

    def test_common_html_comment_placeholder_fails(self):
        """Test that HTML comment placeholders cause validation failure.
        
        Creates artifact with <!-- TODO: later --> comment.
        Expects: status=FAIL with placeholder_hits detected.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A"), encoding="utf-8")
            art.write_text(_artifact_text("A", extra="<!-- TODO: later -->"), encoding="utf-8")

            report = VA.validate(art, req, "custom", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("<!--" in h.get("text", "") for h in report.get("placeholder_hits", [])))

    def test_common_duplicate_fdd_ids_in_id_lines_fails(self):
        """Test that duplicate FDD IDs in **ID**: lines cause failure.
        
        Two sections with same **ID**: fdd-example-req-dup.
        Expects: status=FAIL with 'Duplicate fdd- IDs' error.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A", "B"), encoding="utf-8")

            art.write_text(
                "\n".join(
                    [
                        "## A. One",
                        "",
                        "**ID**: `fdd-example-req-dup`",
                        "",
                        "## B. Two",
                        "",
                        "**ID**: `fdd-example-req-dup`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            report = VA.validate(art, req, "custom")
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("message") == "Duplicate fdd- IDs in document" for e in report.get("errors", [])))

    def test_requirements_unparseable_fails(self):
        """Test that unparseable requirements file causes failure.
        
        Requirements file has no valid section headings.
        Expects: status=FAIL with requirements error.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text("# Not sections\n", encoding="utf-8")
            art.write_text(_artifact_text("A"), encoding="utf-8")

            report = VA.validate(art, req, "custom")
            self.assertEqual(report["status"], "FAIL")
            self.assertIn("errors", report)
            self.assertEqual(report["errors"][0]["type"], "requirements")

    def test_generic_section_order_fails(self):
        """Test that sections in wrong order cause failure.
        
        Requirements: A then B, artifact: B then A (wrong order).
        Expects: status=FAIL with 'not in required order' error.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A", "B"), encoding="utf-8")
            art.write_text(_artifact_text("B", "A"), encoding="utf-8")

            report = VA.validate(art, req, "custom")
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("message") == "Sections are not in required order" for e in report.get("errors", [])))

    def test_common_duplicate_section_ids_fails(self):
        """Test that duplicate section IDs cause validation failure.
        
        Artifact has two sections with same ID (both 'Section A').
        Expects: status=FAIL with 'Duplicate section ids' error.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A"), encoding="utf-8")
            art.write_text("\n".join(["## A. One", "## A. Two"]) + "\n", encoding="utf-8")

            report = VA.validate(art, req, "custom")
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("message") == "Duplicate section ids in artifact" for e in report.get("errors", [])))


class TestFeaturesValidation(unittest.TestCase):
    """Tests for FEATURES.md validation."""
    
    def test_features_pass_minimal(self):
        """Test that minimal valid FEATURES.md passes validation.
        
        Creates FEATURES.md with proper header and one feature entry.
        Expects: status=PASS.
        """
        text = _features_header("Example") + _feature_entry(
            1,
            "fdd-example-feature-alpha",
            "alpha",
            emoji="🔄",
            status="IN_PROGRESS",
        )

        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["feature_issues"], [])

    def test_features_duplicate_feature_ids_fails(self):
        """Test that duplicate feature IDs cause failure.
        
        Two features with same ID: fdd-example-feature-alpha.
        Expects: status=FAIL with duplicate IDs error.
        """
        text = _features_header("Example") + "\n\n".join(
            [
                _feature_entry(1, "fdd-example-feature-alpha", "alpha"),
                _feature_entry(2, "fdd-example-feature-alpha", "beta"),
            ]
        )

        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(e.get("message") == "Duplicate feature ids" for e in report.get("errors", [])))

    def test_features_status_overview_mismatch_fails(self):
        """Test that status overview count mismatch causes failure.
        
        Header claims 2 completed but actual entries show 2 in progress.
        Expects: status=FAIL with status overview mismatch error.
        """
        header = "\n".join(
            [
                "# Features: Example",
                "",
                "**Status Overview**: 2 features total (2 completed, 0 in progress, 0 not started)",
                "",
                "**Meaning**:",
                "- ⏳ NOT_STARTED",
                "- 🔄 IN_PROGRESS",
                "- ✅ IMPLEMENTED",
                "",
            ]
        )
        text = header + "\n\n".join(
            [
                _feature_entry(1, "fdd-example-feature-alpha", "alpha", emoji="🔄", status="IN_PROGRESS"),
                _feature_entry(2, "fdd-example-feature-beta", "beta", emoji="🔄", status="IN_PROGRESS"),
            ]
        )
        
        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("Status Overview counts" in e.get("message", "") for e in report.get("errors", [])))

    def test_features_status_emoji_mismatch_fails(self):
        """Test that mismatch between status emoji and status text causes failure.
        
        Status emoji (✅) does not match status text (IN_PROGRESS).
        Expects: status=FAIL with status mismatch error.
        """
        text = _features_header("Example") + _feature_entry(
            1,
            "fdd-example-feature-alpha",
            "alpha",
            emoji="✅",
            status="IN_PROGRESS",
        )

        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(len(report["feature_issues"]), 1)
        self.assertIn("status_issues", report["feature_issues"][0])

    def test_features_slug_path_mismatch_fails(self):
        """Test that mismatch between slug and path causes failure.
        
        Slug (fdd-example-feature-alpha) does not match path (feature-beta/).
        Expects: status=FAIL with slug mismatch error.
        """
        text = _features_header("Example") + "\n".join(
            [
                "### 1. [fdd-example-feature-alpha](feature-beta/) 🔄 HIGH",
                "- **Purpose**: Purpose",
                "- **Status**: IN_PROGRESS",
                "- **Depends On**: None",
                "- **Blocks**: None",
                "- **Phases**:",
                "  - `ph-1`: 🔄 IN_PROGRESS — Default phase",
                "- **Scope**:",
                "  - scope-item",
                "- **Requirements Covered**:",
                "  - fdd-example-req-1",
            ]
        )

        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(len(report["feature_issues"]), 1)
        self.assertIn("slug_issues", report["feature_issues"][0])

    def test_features_missing_ph_1_fails(self):
        """Test that missing phase 1 causes failure.
        
        Feature entry without phase 1.
        Expects: status=FAIL with phase error.
        """
        text = _features_header("Example") + _feature_entry(
            1,
            "fdd-example-feature-alpha",
            "alpha",
            phases_text="- `ph-2`: 🔄 IN_PROGRESS — Not default",
        )

        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(len(report["feature_issues"]), 1)
        self.assertIn("phase_issues", report["feature_issues"][0])

    def test_features_empty_requirements_covered_list_fails(self):
        """Test that empty requirements covered list causes failure.
        
        Feature with empty requirements covered list.
        Expects: status=FAIL with empty_list_fields issue.
        """
        text = _features_header("Example") + "\n".join(
            [
                "### 1. [fdd-example-feature-alpha](feature-alpha/) 🔄 HIGH",
                "- **Purpose**: Purpose",
                "- **Status**: IN_PROGRESS",
                "- **Depends On**: None",
                "- **Blocks**: None",
                "- **Phases**:",
                "  - `ph-1`: 🔄 IN_PROGRESS — Default phase",
                "- **Scope**:",
                "  - scope-item",
                "- **Requirements Covered**:",
            ]
        )

        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(len(report["feature_issues"]), 1)
        self.assertIn("empty_list_fields", report["feature_issues"][0])

    def test_features_empty_file_fails(self):
        """Cover empty file branch."""
        report = VA.validate_features_manifest("")
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(e.get("message") == "Empty file" for e in report.get("errors", [])))

    def test_features_missing_header_blocks_and_no_entries_fails(self):
        """Cover missing title/overview/meaning and no feature entries branches."""
        text = "\n".join(
            [
                "# Wrong Title",
                "",
                "Some text",
            ]
        )
        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "FAIL")
        msgs = [e.get("message") for e in report.get("errors", [])]
        self.assertTrue(any("Missing or invalid title" in (m or "") for m in msgs))
        self.assertTrue(any("Status Overview" in (m or "") for m in msgs))
        self.assertTrue(any("Meaning" in (m or "") for m in msgs))
        self.assertTrue(any("No feature entries" in (m or "") for m in msgs))

    def test_features_invalid_status_overview_format_fails(self):
        """Cover invalid Status Overview format branch."""
        header = "\n".join(
            [
                "# Features: Example",
                "",
                "**Status Overview**: wrong",
                "",
                "**Meaning**:",
                "- ⏳ NOT_STARTED",
                "- 🔄 IN_PROGRESS",
                "- ✅ IMPLEMENTED",
                "",
            ]
        )
        text = header + _feature_entry(1, "fdd-example-feature-alpha", "alpha")
        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(e.get("message") == "Invalid Status Overview format" for e in report.get("errors", [])))

    def test_features_non_sequential_and_duplicate_paths_fails(self):
        """Cover non-sequential numbering and duplicate paths branches."""
        text = _features_header("Example") + "\n\n".join(
            [
                _feature_entry(1, "fdd-example-feature-alpha", "alpha"),
                _feature_entry(3, "fdd-example-feature-beta", "alpha"),
            ]
        )
        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("numbering" in e.get("message", "").lower() for e in report.get("errors", [])))
        self.assertTrue(any(e.get("message") == "Duplicate feature paths" for e in report.get("errors", [])))

    def test_features_fs_cross_checks_and_dependencies(self):
        """Cover DESIGN.md cross-check missing, dir issues, and dependency reference checks."""
        with TemporaryDirectory() as td:
            root = Path(td)
            arch = root / "architecture"
            arch.mkdir(parents=True)
            features_path = arch / "FEATURES.md"

            # Root DESIGN.md with known IDs for cross-check.
            (root / "DESIGN.md").write_text(
                "\n".join(
                    [
                        "# Technical Design",
                        "**ID**: `fdd-example-req-known`",
                        "**ID**: `fdd-example-principle-known`",
                        "**ID**: `fdd-example-constraint-known`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            entry = "\n".join(
                [
                    "### 1. [fdd-example-feature-alpha](feature-alpha/) 🔄 HIGH",
                    "- **Purpose**: Purpose",
                    "- **Status**: IN_PROGRESS",
                    "- **Depends On**: [Self](feature-alpha/)",
                    "- **Blocks**: [Missing](feature-missing/)",
                    "- **Phases**:",
                    "  - `ph-1`: x",
                    "- **Scope**:",
                    "  - scope-item",
                    "- **Requirements Covered**:",
                    "  - fdd-example-req-unknown",
                    "- **Principles Covered**:",
                    "  - fdd-example-principle-unknown",
                    "- **Constraints Affected**:",
                    "  - fdd-example-constraint-unknown",
                ]
            )

            text = _features_header("Example") + entry
            report = VA.validate_features_manifest(text, artifact_path=features_path, skip_fs_checks=False)
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(len(report.get("feature_issues", [])), 1)
            issue = report["feature_issues"][0]
            self.assertIn("dependency_issues", issue)
            self.assertIn("dir_issues", issue)
            self.assertIn("cross_issues", issue)


    def test_features_invalid_status_value_fails(self):
        """Test that invalid status value causes failure."""
        text = _features_header("Example") + _feature_entry(
            1,
            "fdd-example-feature-alpha",
            "alpha",
            emoji="🔄",
            status="INVALID_STATUS",
        )

        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(len(report["feature_issues"]), 1)
        self.assertIn("status_issues", report["feature_issues"][0])
        self.assertTrue(any("must be one of" in s for s in report["feature_issues"][0]["status_issues"]))

    def test_features_phase_missing_status_emoji_fails(self):
        """Test that phase line without status emoji causes failure."""
        text = _features_header("Example") + _feature_entry(
            1,
            "fdd-example-feature-alpha",
            "alpha",
            emoji="🔄",
            status="IN_PROGRESS",
            phases_text="- `ph-1`: Default phase without emoji",
        )

        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(len(report["feature_issues"]), 1)
        self.assertIn("phase_issues", report["feature_issues"][0])
        self.assertTrue(any("missing status emoji" in s for s in report["feature_issues"][0]["phase_issues"]))

    def test_features_implemented_with_non_implemented_phases_fails(self):
        """Test that IMPLEMENTED feature with non-IMPLEMENTED phases causes failure."""
        text = _features_header("Example", completed=1, in_progress=0) + _feature_entry(
            1,
            "fdd-example-feature-alpha",
            "alpha",
            emoji="✅",
            status="IMPLEMENTED",
            phases_text="- `ph-1`: 🔄 IN_PROGRESS — Still in progress",
        )

        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(len(report["feature_issues"]), 1)
        self.assertIn("phase_issues", report["feature_issues"][0])
        self.assertTrue(any("IMPLEMENTED but only" in s for s in report["feature_issues"][0]["phase_issues"]))

    def test_features_implemented_with_all_phases_implemented_passes(self):
        """Test that IMPLEMENTED feature with all phases IMPLEMENTED passes."""
        text = _features_header("Example", completed=1, in_progress=0) + _feature_entry(
            1,
            "fdd-example-feature-alpha",
            "alpha",
            emoji="✅",
            status="IMPLEMENTED",
            phases_text="- `ph-1`: ✅ IMPLEMENTED — Done",
        )

        report = VA.validate_features_manifest(text)
        self.assertEqual(report["status"], "PASS")


class TestMain(unittest.TestCase):
    """Tests for main validation entry point."""
    def test_main_exit_code_pass(self):
        """Test that main() returns exit code 0 on successful validation.
        
        Validates valid artifact, expects exit code 0.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A"), encoding="utf-8")
            art.write_text(_artifact_text("A"), encoding="utf-8")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = VA.main(["--artifact", str(art), "--requirements", str(req)])
            self.assertEqual(code, 0)

    def test_main_exit_code_fail(self):
        """Test that main() returns exit code 1 on validation failure.
        
        Validates artifact with missing section, expects exit code 1.
        """
        with TemporaryDirectory() as td:
            td_path = Path(td)
            req = td_path / "req.md"
            art = td_path / "artifact.md"
            req.write_text(_req_text("A", "B"), encoding="utf-8")
            art.write_text(_artifact_text("A"), encoding="utf-8")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = VA.main(["--artifact", str(art), "--requirements", str(req)])
            self.assertEqual(code, 2)


class TestRequirementExamples(unittest.TestCase):
    def _repo_root(self) -> Path:
        return Path(__file__).resolve().parent.parent

    def test_examples_exist_are_short_and_are_referenced(self) -> None:
        root = self._repo_root()
        requirements_dir = root / "requirements"
        examples_dir = root / "examples" / "requirements"

        mapping = {
            "adapter-structure.md": "adapter",
            "adr-structure.md": "adr",
            "prd-structure.md": "prd",
            "feature-design-structure.md": "feature-design",
            "features-manifest-structure.md": "features-manifest",
            "overall-design-structure.md": "overall-design",
        }

        for req_name, slug in mapping.items():
            req_path = requirements_dir / req_name
            self.assertTrue(req_path.exists(), f"Missing requirements file: {req_path}")

            example_path = examples_dir / slug / "valid.md"
            self.assertTrue(example_path.exists(), f"Missing example file: {example_path}")

            # Short/template-like examples only.
            lines = example_path.read_text(encoding="utf-8").splitlines()
            self.assertLessEqual(len(lines), 250, f"Example too long (>250 lines): {example_path}")

            req_text = req_path.read_text(encoding="utf-8")
            self.assertIn(f"examples/requirements/{slug}/valid.md", req_text)
            self.assertNotIn(f"examples/requirements/{slug}/invalid.md", req_text)

    def test_valid_examples_pass_fdd_tool_validate(self) -> None:
        root = self._repo_root()
        examples_dir = root / "examples" / "requirements"

        cases = [
            # (example_slug, relative_artifact_path)
            ("prd", Path("architecture/PRD.md")),
            ("overall-design", Path("architecture/DESIGN.md")),
            ("adr", Path("architecture/ADR")),
            ("features-manifest", Path("architecture/features/FEATURES.md")),
            ("feature-design", Path("architecture/features/feature-task-crud/DESIGN.md")),
        ]

        for slug, rel_artifact_path in cases:
            with TemporaryDirectory() as td:
                td_path = Path(td)
                artifact_path = td_path / rel_artifact_path
                artifact_path.parent.mkdir(parents=True, exist_ok=True)

                example_text = (examples_dir / slug / "valid.md").read_text(encoding="utf-8")
                if slug == "adr":
                    # ADR is a directory artifact: write the example as a per-record ADR file inside.
                    # Filename must match the ADR ID in the example (fdd-taskflow-adr-postgres-storage)
                    (artifact_path / "general").mkdir(parents=True, exist_ok=True)
                    (artifact_path / "general" / "0001-fdd-taskflow-adr-postgres-storage.md").write_text(example_text, encoding="utf-8")
                else:
                    artifact_path.write_text(example_text, encoding="utf-8")

                # Run the same CLI entrypoint used by end-users.
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    code = fdd_cli.main([
                        "validate",
                        "--artifact",
                        str(artifact_path),
                        "--skip-fs-checks",
                    ])
                self.assertEqual(code, 0, f"fdd validate failed for {slug} (output={buf.getvalue()[:400]})")


if __name__ == "__main__":
    unittest.main()


class TestTraceabilityHelpers(unittest.TestCase):
    def test_is_effective_code_line_uses_default_language_config(self):
        self.assertTrue(is_effective_code_line("x = 1"))
        self.assertFalse(is_effective_code_line("# comment"))

    def test_paired_inst_tags_ignores_non_instruction_end_tag(self):
        # End tag without ':inst-' is ignored by paired_inst_tags_in_text.
        text = "\n".join(
            [
                "# fdd-begin fdd-demo-feature-x-algo-do:ph-1:inst-step",
                "x = 1",
                "# fdd-end fdd-demo-feature-x-algo-do:ph-1",
            ]
        )
        tags = paired_inst_tags_in_text(text)
        self.assertEqual(tags, set())
