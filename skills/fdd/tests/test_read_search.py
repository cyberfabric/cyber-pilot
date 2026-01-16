import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


class TestFddArtifactEditorReadSearch(unittest.TestCase):
    def _script_path(self) -> Path:
        return (Path(__file__).resolve().parents[1] / "scripts" / "fdd.py").resolve()

    def _run(self, *, td: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
        cmd = [sys.executable, str(self._script_path()), *args]
        return subprocess.run(cmd, cwd=str(td), text=True, capture_output=True)

    def test_list_sections_features_manifest(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            features_path = td / "architecture" / "features" / "FEATURES.md"
            features_path.parent.mkdir(parents=True, exist_ok=True)
            features_path.write_text(
                "\n".join(
                    [
                        "# Features: example",
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
                        "- **Requirements Covered**:",
                        "  - fdd-example-req-alpha",
                        "- **Phases**:",
                        "  - `ph-1`: ⏳ NOT_STARTED — Default",
                        "- **Scope**:",
                        "  - One",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            proc = self._run(td=td, args=["list-sections", "--artifact", str(features_path)])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

            payload = json.loads(proc.stdout)
            self.assertEqual(payload["kind"], "features-manifest")
            self.assertEqual(len(payload["entries"]), 1)
            self.assertEqual(payload["entries"][0]["feature_id"], "fdd-example-feature-alpha")

    def test_read_section_lettered(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            p = td / "architecture" / "BUSINESS.md"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(
                "\n".join(
                    [
                        "# Business Context",
                        "",
                        "## A. VISION",
                        "",
                        "**Purpose**: P.",
                        "",
                        "## B. Actors",
                        "",
                        "**Human Actors**:",
                    ]
                ),
                encoding="utf-8",
            )

            proc = self._run(td=td, args=["read-section", "--artifact", str(p), "--section", "A"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "FOUND")
            self.assertEqual(payload["section"], "A")
            self.assertIn("## A. VISION", payload["text"])
            self.assertNotIn("## B. Actors", payload["text"])

    def test_find_id_returns_block(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            p = td / "doc.md"
            p.write_text(
                "\n".join(
                    [
                        "# Doc",
                        "",
                        "## A. One",
                        "",
                        "Line.",
                        "",
                        "**ID**: `fdd-example-req-abc`",
                        "",
                        "More.",
                        "",
                        "## B. Two",
                        "",
                        "End.",
                    ]
                ),
                encoding="utf-8",
            )

            proc = self._run(td=td, args=["find-id", "--artifact", str(p), "--id", "fdd-example-req-abc"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "FOUND")
            self.assertEqual(payload["id"], "fdd-example-req-abc")
            self.assertIn("## A. One", payload["text"])
            self.assertNotIn("## B. Two", payload["text"])

    def test_search_literal(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            p = td / "doc.md"
            p.write_text("a\nneedle\nb\nneedle\n", encoding="utf-8")

            proc = self._run(td=td, args=["search", "--artifact", str(p), "--query", "needle"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)

            payload = json.loads(proc.stdout)
            self.assertEqual(payload["count"], 2)
            self.assertEqual(payload["hits"][0]["line"], 2)
            self.assertEqual(payload["hits"][1]["line"], 4)

    def test_where_used_finds_across_docs_and_code(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "docs").mkdir(parents=True)
            (td / "src").mkdir(parents=True)

            fid = "fdd-example-feature-x-req-do-thing"
            (td / "docs" / "DESIGN.md").write_text(f"**ID**: `{fid}`\n", encoding="utf-8")
            (td / "src" / "lib.rs").write_text(f"// @fdd-req:{fid}:ph-1\n", encoding="utf-8")

            proc = self._run(td=td, args=["where-used", "--root", str(td), "--id", fid])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["id"], fid)
            paths = [h["path"] for h in payload["hits"]]
            self.assertIn("docs/DESIGN.md", paths)
            self.assertIn("src/lib.rs", paths)

    def test_where_defined_is_normative_docs_only_by_default(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "architecture" / "features" / "feature-x").mkdir(parents=True)
            (td / "src").mkdir(parents=True)

            fid = "fdd-example-feature-x-req-do-thing"
            (td / "architecture" / "features" / "feature-x" / "DESIGN.md").write_text(
                f"- [ ] **ID**: {fid}\n",
                encoding="utf-8",
            )
            (td / "src" / "lib.rs").write_text(f"// @fdd-req:{fid}:ph-1\n", encoding="utf-8")

            proc = self._run(td=td, args=["where-defined", "--root", str(td), "--id", fid])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "FOUND")
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["definitions"][0]["path"], "architecture/features/feature-x/DESIGN.md")

    def test_where_defined_can_include_tags(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "architecture" / "features" / "feature-x").mkdir(parents=True)
            (td / "src").mkdir(parents=True)

            fid = "fdd-example-feature-x-req-do-thing"
            (td / "architecture" / "features" / "feature-x" / "DESIGN.md").write_text(
                f"- [ ] **ID**: {fid}\n",
                encoding="utf-8",
            )
            (td / "src" / "lib.rs").write_text(f"// @fdd-req:{fid}:ph-1\n", encoding="utf-8")

            proc = self._run(td=td, args=["where-defined", "--root", str(td), "--id", fid, "--include-tags"])
            self.assertNotEqual(proc.returncode, 0)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "AMBIGUOUS")
            self.assertEqual(payload["count"], 2)

    def test_scan_ids_directory(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "docs").mkdir(parents=True)
            (td / "src").mkdir(parents=True)

            (td / "docs" / "doc.md").write_text("**ID**: `fdd-example-actor-user`\n", encoding="utf-8")
            (td / "src" / "lib.rs").write_text("// @fdd-change:fdd-example-feature-x-change-a:ph-1\n", encoding="utf-8")

            proc = self._run(td=td, args=["scan-ids", "--root", str(td)])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            ids = [h["id"] for h in payload["ids"]]
            self.assertIn("fdd-example-actor-user", ids)
            self.assertIn("fdd-example-feature-x-change-a", ids)

    def test_scan_ids_file_with_pattern(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            p = td / "doc.md"
            p.write_text("fdd-example-actor-user\nfdd-example-capability-view\n", encoding="utf-8")

            proc = self._run(td=td, args=["scan-ids", "--root", str(p), "--pattern=-actor-"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            ids = [h["id"] for h in payload["ids"]]
            self.assertEqual(ids, ["fdd-example-actor-user"])

    def test_where_defined_qualified_inst_in_feature_design_block(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "architecture" / "features" / "feature-x").mkdir(parents=True)

            base = "fdd-example-feature-x-algo-do-thing"
            inst = "inst-return-ok"
            art = td / "architecture" / "features" / "feature-x" / "DESIGN.md"
            art.write_text(
                "\n".join(
                    [
                        "# Feature: X",
                        "",
                        "## A. Feature Context",
                        "### 1. Overview",
                        "ok.",
                        "### 2. Purpose",
                        "ok.",
                        "### 3. Actors",
                        "- `fdd-example-actor-user`",
                        "### 4. References",
                        "- None",
                        "",
                        "---",
                        "",
                        "## B. Actor Flows (FDL)",
                        "",
                        "---",
                        "",
                        "## C. Algorithms (FDL)",
                        "### Algo",
                        "",
                        f"- [ ] **ID**: {base}",
                        "",
                        "1. [ ] - `ph-1` - **RETURN** ok - `inst-return-ok`",
                        "",
                        "---",
                        "",
                        "## D. States (FDL)",
                        "",
                        "---",
                        "",
                        "## E. Technical Details",
                        "ok.",
                        "",
                        "---",
                        "",
                        "## F. Requirements",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            q = f"{base}:ph-1:{inst}"
            proc = self._run(td=td, args=["where-defined", "--root", str(td), "--id", q])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "FOUND")
            self.assertEqual(payload["base_id"], base)
            self.assertEqual(payload["phase"], "ph-1")
            self.assertEqual(payload["inst"], inst)
            self.assertEqual(payload["definitions"][0]["path"], "architecture/features/feature-x/DESIGN.md")
            self.assertIn(inst, payload["definitions"][0]["text"])

    def test_where_used_excludes_definitions_for_base_id(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "architecture" / "features" / "feature-x").mkdir(parents=True)
            (td / "src").mkdir(parents=True)

            base = "fdd-example-feature-x-algo-do-thing"
            art = td / "architecture" / "features" / "feature-x" / "DESIGN.md"
            art.write_text(f"- [ ] **ID**: {base}\n", encoding="utf-8")
            (td / "src" / "lib.rs").write_text(f"// @fdd-algo:{base}:ph-1\n", encoding="utf-8")

            proc = self._run(td=td, args=["where-used", "--root", str(td), "--id", base])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            paths = [h["path"] for h in payload["hits"]]
            self.assertIn("src/lib.rs", paths)
            self.assertNotIn("architecture/features/feature-x/DESIGN.md", paths)

    def test_where_defined_business_actor_only_in_section_b_and_heading_block(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "architecture").mkdir(parents=True)

            actor_id = "fdd-example-actor-analyst"
            cap_id = "fdd-example-capability-view"

            p = td / "architecture" / "BUSINESS.md"
            p.write_text(
                "\n".join(
                    [
                        "# Business Context",
                        "",
                        "## A. VISION",
                        "Text.",
                        "",
                        "## B. Actors",
                        "",
                        "#### Analyst",
                        "",
                        f"**ID**: `{actor_id}`",
                        "**Role**: Reads.",
                        "",
                        "## C. Capabilities",
                        "",
                        "#### View",
                        "",
                        f"**ID**: `{cap_id}`",
                        "- Does.",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            proc = self._run(td=td, args=["where-defined", "--root", str(td), "--id", actor_id])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "FOUND")
            self.assertEqual(payload["definitions"][0]["path"], "architecture/BUSINESS.md")

            proc_cap = self._run(td=td, args=["where-defined", "--root", str(td), "--id", cap_id])
            self.assertEqual(proc_cap.returncode, 0, msg=proc_cap.stdout + "\n" + proc_cap.stderr)
            payload_cap = json.loads(proc_cap.stdout)
            self.assertEqual(payload_cap["status"], "FOUND")
            self.assertEqual(payload_cap["definitions"][0]["path"], "architecture/BUSINESS.md")

    def test_where_defined_design_requirement_only_in_section_b(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "architecture").mkdir(parents=True)
            req_id = "fdd-example-req-one"
            actor_id = "fdd-example-actor-analyst"
            cap_id = "fdd-example-capability-view"

            p = td / "architecture" / "DESIGN.md"
            p.write_text(
                "\n".join(
                    [
                        "# Design",
                        "",
                        "## A. Architecture Overview",
                        "Text.",
                        "",
                        "## B. Requirements & Principles",
                        "",
                        "### 1. System Requirements & Constraints",
                        "",
                        "**Performance Requirements**:",
                        f"**ID**: `{req_id}`",
                        f"**Capabilities**: `{cap_id}`",
                        f"**Actors**: `{actor_id}`",
                        "- Ok",
                        "",
                        "## C. Technical Architecture",
                        "Text.",
                        "",
                        "## D. Additional Context",
                        "Ref `fdd-example-req-one`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            proc = self._run(td=td, args=["where-defined", "--root", str(td), "--id", req_id])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "FOUND")
            self.assertEqual(payload["definitions"][0]["path"], "architecture/DESIGN.md")

            proc_used = self._run(td=td, args=["where-used", "--root", str(td), "--id", req_id])
            self.assertEqual(proc_used.returncode, 0, msg=proc_used.stdout + "\n" + proc_used.stderr)
            payload_used = json.loads(proc_used.stdout)
            used_paths = [h["path"] for h in payload_used["hits"]]
            # usage in Section D must appear; definition in Section B must not
            self.assertIn("architecture/DESIGN.md", used_paths)
            self.assertNotEqual(payload_used["count"], 0)


if __name__ == "__main__":
    unittest.main()
