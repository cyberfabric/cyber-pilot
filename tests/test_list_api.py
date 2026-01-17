import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


class TestFddArtifactEditorListApi(unittest.TestCase):
    def _script_path(self) -> Path:
        return (Path(__file__).resolve().parent.parent / "skills" / "fdd" / "scripts" / "fdd.py").resolve()

    def _run(self, *, td: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
        cmd = [sys.executable, str(self._script_path()), *args]
        return subprocess.run(cmd, cwd=str(td), text=True, capture_output=True)

    def _minimal_features_manifest(self) -> str:
        return "\n".join(
            [
                "# Features: Example",
                "",
                "**Status Overview**: 1 features total (0 completed, 0 in progress, 1 not started)",
                "",
                "**Meaning**:",
                "- ⏳ NOT_STARTED",
                "- 🔄 IN_PROGRESS",
                "- ✅ IMPLEMENTED",
                "",
                "---",
                "",
                "## Features List",
                "",
                "### 1. [fdd-example-feature-alpha](feature-alpha/) ⏳ HIGH",
                "- **Purpose**: Example",
                "- **Status**: NOT_STARTED",
                "- **Depends On**: None",
                "- **Blocks**: None",
                "- **Phases**:",
                "  - `ph-1`: ⏳ NOT_STARTED — Default phase",
                "- **Scope**:",
                "  - One",
                "- **Requirements Covered**:",
                "  - fdd-example-req-1",
                "",
            ]
        )

    def _minimal_changes(self) -> str:
        return "\n".join(
            [
                "# Implementation Plan: Example",
                "",
                "**Feature**: `x`",
                "**Version**: 0.1",
                "**Last Updated**: 2026-01-01",
                "**Status**: ⏳ NOT_STARTED",
                "**Feature DESIGN**: [DESIGN](DESIGN.md)",
                "",
                "## Summary",
                "",
                "**Total Changes**: 1",
                "**Completed**: 0",
                "**In Progress**: 0",
                "**Not Started**: 1",
                "",
                "## Change 1: First",
                "",
                "**ID**: `fdd-example-feature-x-change-first`",
                "**Status**: ⏳ NOT_STARTED",
                "**Priority**: HIGH",
                "**Effort**: S",
                "**Implements**: `fdd-example-feature-x-req-do-thing`",
                "**Phases**: ph-1",
                "",
                "### Objective",
                "Do.",
                "",
                "### Requirements Coverage",
                "- `fdd-example-feature-x-req-do-thing`",
                "",
                "### Tasks",
                "- [ ] 1.1 Implement something in code",
                "- [ ] 1.2 Add required FDD comment tags: `@fdd-change:fdd-example-feature-x-change-first:ph-1`",
                "",
                "### Specification",
                "- Update docs.",
                "",
                "### Dependencies",
                "**Depends on**: None",
                "**Blocks**: None",
                "",
                "### Testing",
                "- Run tests.",
                "",
            ]
        )

    def _minimal_business(self) -> str:
        return "\n".join(
            [
                "# Business Context",
                "",
                "## A. VISION",
                "",
                "Text.",
                "",
                "## B. Actors",
                "",
                "#### Analyst",
                "",
                "**ID**: `fdd-example-actor-analyst`",
                "**Role**: Reads.",
                "",
                "## C. Capabilities",
                "",
                "#### View",
                "",
                "**ID**: `fdd-example-capability-view`",
                "**Actors**: `fdd-example-actor-analyst`",
                "",
            ]
        )

    def _minimal_adr(self) -> str:
        return "\n".join(
            [
                "# Architecture Decision Records",
                "",
                "## ADR-0001: One",
                "",
                "**Date**: 2026-01-01",
                "**Status**: Proposed",
                "**Deciders**: Team",
                "",
                "### Context and Problem Statement",
                "Text.",
                "",
            ]
        )

    def _minimal_overall_design(self) -> str:
        return "\n".join(
            [
                "# Overall Design",
                "",
                "## A. Overview",
                "Text.",
                "",
                "## B. Requirements",
                "",
                "### B.1 Functional Requirements",
                "",
                "#### Requirement",
                "",
                "- [ ] **ID**: fdd-example-req-do-thing",
                "**Description**: Must do.",
                "**Capabilities**: `fdd-example-capability-view`",
                "**Actors**: `fdd-example-actor-analyst`",
                "",
                "### B.3 Design Principles",
                "",
                "#### Principle",
                "",
                "**ID**: `fdd-example-principle-simple`",
                "**Description**: Keep it simple.",
                "",
                "## C. Architecture",
                "",
                "### C.1: One",
                "x",
            ]
        )

    def _minimal_feature_design(self) -> str:
        return "\n".join(
            [
                "# Feature Design: Example",
                "",
                "## A. Feature Context",
                "Text.",
                "",
                "## B. Actor Flows (FDL)",
                "",
                "### Flow",
                "",
                "- [ ] **ID**: fdd-example-feature-x-flow-do-thing",
                "",
                "1. [ ] - `ph-1` - **RETURN** ok - `inst-return-ok`",
                "",
            ]
        )

    def test_list_ids_filters_by_pattern(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            p = td / "doc.md"
            p.write_text("a fdd-example-actor-analyst b\nADR-0001\n", encoding="utf-8")

            proc = self._run(td=td, args=["list-ids", "--artifact", str(p), "--pattern", "actor-"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["ids"][0]["id"], "fdd-example-actor-analyst")

    def test_list_items_features_manifest(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            features_path = td / "architecture" / "features" / "FEATURES.md"
            features_path.parent.mkdir(parents=True, exist_ok=True)
            features_path.write_text(self._minimal_features_manifest(), encoding="utf-8")

            proc = self._run(td=td, args=["list-items", "--artifact", str(features_path), "--type", "feature", "--lod", "summary"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["items"][0]["id"], "fdd-example-feature-alpha")

    def test_list_items_changes(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            feat = td / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "CHANGES.md"
            art.write_text(self._minimal_changes(), encoding="utf-8")

            proc = self._run(td=td, args=["list-items", "--artifact", str(art), "--type", "change", "--lod", "summary"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["items"][0]["change"], 1)

    def test_list_items_business(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            art = td / "architecture" / "BUSINESS.md"
            art.parent.mkdir(parents=True, exist_ok=True)
            art.write_text(self._minimal_business(), encoding="utf-8")

            proc = self._run(td=td, args=["list-items", "--artifact", str(art), "--lod", "summary"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            ids = [it["id"] for it in payload["items"]]
            self.assertIn("fdd-example-actor-analyst", ids)
            self.assertIn("fdd-example-capability-view", ids)

    def test_list_items_adr(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            art = td / "architecture" / "ADR.md"
            art.parent.mkdir(parents=True, exist_ok=True)
            art.write_text(self._minimal_adr(), encoding="utf-8")

            proc = self._run(td=td, args=["list-items", "--artifact", str(art), "--type", "adr", "--lod", "summary"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["items"][0]["id"], "ADR-0001")

    def test_list_items_overall_design(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            art = td / "architecture" / "DESIGN.md"
            art.parent.mkdir(parents=True, exist_ok=True)
            art.write_text(self._minimal_overall_design(), encoding="utf-8")

            proc = self._run(td=td, args=["list-items", "--artifact", str(art), "--type", "requirement", "--lod", "summary"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["items"][0]["id"], "fdd-example-req-do-thing")

    def test_under_heading_flow_overall_design(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            art = td / "architecture" / "DESIGN.md"
            art.parent.mkdir(parents=True, exist_ok=True)
            art.write_text(self._minimal_overall_design(), encoding="utf-8")

            proc = self._run(td=td, args=["list-sections", "--artifact", str(art), "--under-heading", "B. Requirements"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            titles = [e["title"] for e in payload["entries"]]
            self.assertIn("B.1 Functional Requirements", titles)
            self.assertIn("B.3 Design Principles", titles)

            proc = self._run(
                td=td,
                args=[
                    "list-items",
                    "--artifact",
                    str(art),
                    "--under-heading",
                    "B.1 Functional Requirements",
                    "--type",
                    "requirement",
                    "--lod",
                    "summary",
                ],
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            ids = [it["id"] for it in payload["items"]]
            self.assertIn("fdd-example-req-do-thing", ids)
            self.assertNotIn("fdd-example-principle-simple", ids)

    def test_list_ids_under_heading(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            art = td / "doc.md"
            art.write_text("# Doc\n\n## A\n\n**ID**: `fdd-example-a`\n\n## B\n\n**ID**: `fdd-example-b`\n", encoding="utf-8")

            proc = self._run(td=td, args=["list-ids", "--artifact", str(art), "--under-heading", "A"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            ids = [x["id"] for x in payload["ids"]]
            self.assertEqual(ids, ["fdd-example-a"])

    def test_list_items_feature_design(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            feat = td / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            art = feat / "DESIGN.md"
            art.write_text(self._minimal_feature_design(), encoding="utf-8")

            proc = self._run(td=td, args=["list-items", "--artifact", str(art), "--type", "flow", "--lod", "summary"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["items"][0]["id"], "fdd-example-feature-x-flow-do-thing")

    def test_get_item_by_id(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            art = td / "doc.md"
            art.write_text("# Doc\n\n## A\n\n**ID**: `fdd-example-req-a`\n\nX\n", encoding="utf-8")

            proc = self._run(td=td, args=["get-item", "--artifact", str(art), "--id", "fdd-example-req-a"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "FOUND")
            self.assertIn("fdd-example-req-a", payload["text"])


if __name__ == "__main__":
    unittest.main()
