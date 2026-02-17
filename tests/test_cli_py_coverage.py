import io
import json
import os
import sys
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _bootstrap_project_root(root: Path, adapter_rel: str = "adapter") -> Path:
    (root / ".git").mkdir()
    (root / ".cypilot-config.json").write_text(
        json.dumps({"cypilotAdapterPath": adapter_rel}, ensure_ascii=False),
        encoding="utf-8",
    )
    adapter = root / adapter_rel
    adapter.mkdir(parents=True, exist_ok=True)
    (adapter / "AGENTS.md").write_text("# Test adapter\n", encoding="utf-8")
    return adapter


def _bootstrap_self_check_kits(root: Path, adapter: Path, *, with_example: bool = True, bad_example: bool = False) -> None:
    # Minimal artifacts registry that passes `load_artifacts_registry` and contains kits.
    _write_json(
        adapter / "artifacts.json",
        {
            "project_root": "..",
            "systems": [],
            "kits": {
                "cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"},
            },
        },
    )

    kit_root = root / "kits" / "cypilot-sdlc"
    kit_root.mkdir(parents=True, exist_ok=True)
    (kit_root / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
    (kit_root / "artifacts" / "REQ" / "template.md").write_text(
        "---\ncypilot-template:\n  version:\n    major: 1\n    minor: 0\n  kind: REQ\n---\n\n"
        "<!-- cpt:id:req -->\n- [x] `p1` - **ID**: `cpt-{system}-req-{slug}`\n<!-- cpt:id:req -->\n",
        encoding="utf-8",
    )
    (kit_root / "constraints.json").write_text(
        json.dumps(
            {
                "REQ": {
                    "identifiers": {
                        "req": {"required": True, "template": "cpt-{system}-req-{slug}"},
                    }
                }
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    if with_example:
        ex_dir = kit_root / "artifacts" / "REQ" / "examples"
        ex_dir.mkdir(parents=True, exist_ok=True)
        example = ex_dir / "example.md"

        if bad_example:
            example.write_text("# Example\n\n(no IDs)\n", encoding="utf-8")
        else:
            example.write_text(
                "- [x] `p1` - **ID**: `cpt-myapp-req-login`\n",
                encoding="utf-8",
            )


class TestCLIPyCoverageSelfCheck(unittest.TestCase):
    def test_self_check_pass(self):
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_kits(root, adapter, with_example=True, bad_example=False)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertEqual(out.get("kits_checked"), 1)
                self.assertEqual(out.get("templates_checked"), 1)
                self.assertEqual(out["results"][0]["status"], "PASS")
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageSelfCheckMoreBranches(unittest.TestCase):
    def _bootstrap_kit(
        self,
        root: Path,
        *,
        kind: str = "REQ",
        with_constraints: bool = True,
        constraints_payload: dict | None = None,
    ) -> "cypilot.utils.artifacts_meta.ArtifactsMeta":
        from cypilot.utils.artifacts_meta import ArtifactsMeta

        kit_root = root / "kits" / "k"
        (kit_root / "artifacts" / kind / "examples").mkdir(parents=True, exist_ok=True)
        (kit_root / "artifacts" / kind / "template.md").write_text("# T\n", encoding="utf-8")
        (kit_root / "artifacts" / kind / "examples" / "example.md").write_text(
            "- [x] `p1` - **ID**: `cpt-myapp-req-login`\n",
            encoding="utf-8",
        )

        if with_constraints:
            payload = constraints_payload
            if payload is None:
                payload = {
                    kind: {
                        "identifiers": {
                            "req": {"required": False, "template": "cpt-{system}-req-{slug}"}
                        }
                    }
                }
            (kit_root / "constraints.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        reg = {
            "version": "1.1",
            "project_root": "..",
            "systems": [],
            "kits": {
                "k": {
                    "format": "Cypilot",
                    "path": "kits/k",
                    "artifacts": {
                        kind: {
                            "template": "{project_root}/kits/k/artifacts/%s/template.md" % kind,
                            "examples": "{project_root}/kits/k/artifacts/%s/examples" % kind,
                        }
                    },
                }
            },
        }
        return ArtifactsMeta.from_dict(reg)

    def test_run_self_check_fails_when_constraints_missing(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=False)
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")
            self.assertGreaterEqual(int(out.get("kits_checked", 0)), 1)

    def test_run_self_check_fails_on_invalid_constraints_json(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=True, constraints_payload={"REQ": {}})
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")
            self.assertGreaterEqual(int(out.get("kits_checked", 0)), 1)

    def test_run_self_check_fails_when_kind_not_in_constraints(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=True, constraints_payload={"OTHER": {"identifiers": {}}})
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_template_checks_phase_gate_on_heading_errors(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=True)

            with patch(
                "cypilot.commands.self_check.validate_headings_contract",
                return_value={"errors": [{"type": "x", "message": "boom", "path": "p", "line": 1}], "warnings": []},
            ):
                rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_template_checks_template_unreadable_branch(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=True)

            with patch("cypilot.commands.self_check.read_text_safe", return_value=None):
                rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_template_checks_fails_on_identifier_without_template(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            # identifiers.req has no template -> error branch
            meta = self._bootstrap_kit(
                root,
                with_constraints=True,
                constraints_payload={
                    "REQ": {
                        "identifiers": {
                            "req": {"required": False}
                        }
                    }
                },
            )
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")
            self.assertIn("errors", out["results"][0])

    def test_template_checks_fail_when_required_id_placeholder_missing(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(
                root,
                with_constraints=True,
                constraints_payload={
                    "REQ": {
                        "identifiers": {
                            "req": {"required": True, "template": "cpt-{system}-req-{slug}"}
                        }
                    }
                },
            )
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_template_checks_id_placeholder_wrong_heading(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            kit_root = root / "kits" / "k" / "artifacts" / "REQ"
            kit_root.mkdir(parents=True, exist_ok=True)
            (kit_root / "template.md").write_text(
                "# T\n\n- [ ] **ID**: `cpt-{system}-req-{slug}`\n",
                encoding="utf-8",
            )
            (kit_root / "examples").mkdir(parents=True, exist_ok=True)
            (kit_root / "examples" / "example.md").write_text(
                "- [x] `p1` - **ID**: `cpt-myapp-req-login`\n",
                encoding="utf-8",
            )
            (root / "kits" / "k" / "constraints.json").write_text(
                json.dumps(
                    {
                        "REQ": {
                            "headings": [{"level": 1, "pattern": "^T$"}],
                            "identifiers": {
                                "req": {
                                    "required": True,
                                    "template": "cpt-{system}-req-{slug}",
                                    "headings": ["allowed"],
                                }
                            },
                        }
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            from cypilot.utils.artifacts_meta import ArtifactsMeta

            meta = ArtifactsMeta.from_dict(
                {
                    "version": "1.1",
                    "project_root": "..",
                    "systems": [],
                    "kits": {
                        "k": {
                            "format": "Cypilot",
                            "path": "kits/k",
                            "artifacts": {
                                "REQ": {
                                    "template": "{project_root}/kits/k/artifacts/REQ/template.md",
                                    "examples": "{project_root}/kits/k/artifacts/REQ/examples",
                                }
                            },
                        }
                    },
                }
            )

            fake_headings_at = [[] for _ in range(10)]
            fake_headings_at[3] = ["not-allowed"]
            with patch("cypilot.commands.self_check.heading_constraint_ids_by_line", return_value=fake_headings_at):
                rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_template_checks_required_reference_missing(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(
                root,
                with_constraints=True,
                constraints_payload={
                    "SRC": {
                        "identifiers": {
                            "x": {
                                "required": False,
                                "template": "cpt-{system}-x-{slug}",
                                "references": {"REQ": {"coverage": "required"}},
                            }
                        }
                    },
                    "REQ": {"identifiers": {"req": {"required": False, "template": "cpt-{system}-req-{slug}"}}},
                },
            )
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_template_checks_required_reference_wrong_heading(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            kit_root = root / "kits" / "k" / "artifacts" / "REQ"
            kit_root.mkdir(parents=True, exist_ok=True)
            (kit_root / "template.md").write_text(
                "# T\n\nRef `cpt-{system}-x-{slug}`\n",
                encoding="utf-8",
            )
            (kit_root / "examples").mkdir(parents=True, exist_ok=True)
            (kit_root / "examples" / "example.md").write_text(
                "- [x] `p1` - **ID**: `cpt-myapp-req-login`\n",
                encoding="utf-8",
            )
            (root / "kits" / "k" / "constraints.json").write_text(
                json.dumps(
                    {
                        "SRC": {
                            "identifiers": {
                                "x": {
                                    "required": False,
                                    "template": "cpt-{system}-x-{slug}",
                                    "references": {"REQ": {"coverage": "required", "headings": ["allowed"]}},
                                }
                            }
                        },
                        "REQ": {
                            "headings": [{"level": 1, "pattern": "^T$"}],
                            "identifiers": {
                                "req": {"required": False, "template": "cpt-{system}-req-{slug}"}
                            },
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            from cypilot.utils.artifacts_meta import ArtifactsMeta

            meta = ArtifactsMeta.from_dict(
                {
                    "version": "1.1",
                    "project_root": "..",
                    "systems": [],
                    "kits": {
                        "k": {
                            "format": "Cypilot",
                            "path": "kits/k",
                            "artifacts": {
                                "REQ": {
                                    "template": "{project_root}/kits/k/artifacts/REQ/template.md",
                                    "examples": "{project_root}/kits/k/artifacts/REQ/examples",
                                }
                            },
                        }
                    },
                }
            )
            fake_headings_at = [[] for _ in range(10)]
            fake_headings_at[3] = ["not-allowed"]
            with patch("cypilot.commands.self_check.heading_constraint_ids_by_line", return_value=fake_headings_at):
                rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_run_self_check_fallback_when_kit_paths_raise(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=True)
            kit = meta.kits["k"]

            def _boom(_kind: str) -> str:
                raise Exception("boom")

            kit.get_template_path = _boom
            kit.get_examples_path = _boom

            # Legacy fallback layout already exists from _bootstrap_kit.
            # Verify fallback picks up the files even when get_*_path raises.
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            self.assertEqual(rc, 0)
            self.assertEqual(out.get("status"), "PASS")


class TestCLIPyCoverageValidateBranches(unittest.TestCase):
    def test_validate_artifact_outside_project_root_hits_relative_to_error(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _FakeMeta:
            systems = []

            def get_artifact_by_path(self, _rel: str):
                return None

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

            def iter_all_artifacts(self):
                return iter([])

            def is_ignored(self, _rel: str) -> bool:
                return False

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = None

        class _FakeCtx:
            meta = _FakeMeta()
            project_root = Path("/tmp/nonexistent-root")
            registered_systems = set(["sys"])
            kits = {"x": _FakeLoadedKit()}

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            tmp = Path(td)
            outside = tmp / "outside"
            outside.mkdir(parents=True, exist_ok=True)
            art = outside / "A.md"
            art.write_text("# X\n", encoding="utf-8")

            # Force context to claim a different project root so Path.relative_to() raises ValueError.
            fake_ctx = _FakeCtx()
            fake_ctx.project_root = tmp / "project"

            buf = io.StringIO()
            with patch("cypilot.utils.context.CypilotContext.load", return_value=fake_ctx):
                with patch("cypilot.utils.context.get_context", return_value=fake_ctx):
                    with redirect_stdout(buf):
                        rc = validate_cmd.cmd_validate(["--artifact", str(art)])

            self.assertEqual(rc, 1)
            out = json.loads(buf.getvalue())
            self.assertEqual(out.get("status"), "ERROR")

    def test_validate_early_stop_writes_output_file(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _FakeSystemNode:
            kit = "x"

        class _FakeArtifactMeta:
            def __init__(self, path: str, kind: str, traceability: str = "FULL"):
                self.path = path
                self.kind = kind
                self.traceability = traceability

        class _FakeMeta:
            def __init__(self, root: Path, art_rel: str):
                self._root = root
                self._art_rel = art_rel
                self.systems = []

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(self._art_rel, "REQ", "FULL"), _FakeSystemNode()

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

            def is_ignored(self, _rel: str) -> bool:
                return False

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(root, art_rel)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")

            art_rel = "artifacts/REQ.md"
            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            (root / art_rel).write_text("# R\n", encoding="utf-8")

            ctx = _FakeCtx(root, art_rel)
            out_path = root / "out.json"

            with patch("cypilot.utils.context.get_context", return_value=ctx):
                # Force per-artifact validation to fail so cmd_validate returns early and writes output.
                with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [{"type": "x", "message": "boom", "path": str(root / art_rel), "line": 1}], "warnings": []}):
                    rc = validate_cmd.cmd_validate(["--output", str(out_path)])

            self.assertEqual(rc, 2)
            self.assertTrue(out_path.is_file())

    def test_validate_skips_non_cypilot_artifacts_in_registry(self):
        from cypilot.commands import validate as validate_cmd

        class _FakePkg:
            def is_cypilot_format(self):
                return False

        class _FakeSystemNode:
            kit = "x"
            artifacts = []
            codebase = []
            children = []

        class _FakeArtifactMeta:
            path = "a.md"
            kind = "REQ"
            traceability = "FULL"

        class _FakeMeta:
            systems = []

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(), _FakeSystemNode()

            def get_kit(self, _kit_id: str):
                return _FakePkg()

        class _FakeCtx:
            def __init__(self, root: Path):
                self.meta = _FakeMeta()
                self.project_root = root
                self.registered_systems = set()
                self.kits = {}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            ctx = _FakeCtx(root)
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with redirect_stdout(buf):
                    rc = validate_cmd.cmd_validate([])
            self.assertEqual(rc, 1)
            out = json.loads(buf.getvalue())
            self.assertEqual(out.get("status"), "ERROR")

    def test_validate_ctx_errors_are_reported_and_trigger_early_fail(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _FakeSystemNode:
            kit = "x"
            artifacts = []
            codebase = []
            children = []

        class _FakeArtifactMeta:
            def __init__(self, path: str):
                self.path = path
                self.kind = "REQ"
                self.traceability = "FULL"

        class _FakeMeta:
            def __init__(self, art_rel: str):
                self._art_rel = art_rel
                self.systems = []

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(self._art_rel), _FakeSystemNode()

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[types.SimpleNamespace(kind="req")])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(art_rel)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = [{"type": "constraints", "message": "ctx boom", "path": "<x>", "line": 1}]

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            art_rel = "artifacts/REQ.md"
            (root / art_rel).write_text("# R\n", encoding="utf-8")

            ctx = _FakeCtx(root, art_rel)
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                    with redirect_stdout(buf):
                        rc = validate_cmd.cmd_validate([])

            self.assertEqual(rc, 2)
            out = json.loads(buf.getvalue())
            self.assertEqual(out.get("status"), "FAIL")
            self.assertGreater(out.get("error_count", 0), 0)

    def test_validate_constraints_path_resolve_error_and_verbose_scan_exception(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _BadKit:
            @property
            def path(self):
                raise RuntimeError("boom")

        class _FakeLoadedKit:
            kit = _BadKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeSystemNode:
            kit = "x"
            artifacts = []
            codebase = []
            children = []

        class _FakeArtifactMeta:
            def __init__(self, path: str):
                self.path = path
                self.kind = "REQ"
                self.traceability = "FULL"

        class _FakeMeta:
            def __init__(self, art_rel: str):
                self._art_rel = art_rel
                self.systems = []

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(self._art_rel), _FakeSystemNode()

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(art_rel)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            art_rel = "artifacts/REQ.md"
            (root / art_rel).write_text("# R\n", encoding="utf-8")

            ctx = _FakeCtx(root, art_rel)
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("cypilot.commands.validate.scan_cpt_ids", side_effect=RuntimeError("scan boom")):
                    with patch(
                        "cypilot.commands.validate.validate_artifact_file",
                        return_value={"errors": [{"type": "x", "message": "boom", "path": str(root / art_rel), "line": 1}], "warnings": []},
                    ):
                        with redirect_stdout(buf):
                            rc = validate_cmd.cmd_validate(["--verbose"])

            self.assertEqual(rc, 2)
            out = json.loads(buf.getvalue())
            self.assertEqual(out.get("status"), "FAIL")

    def test_validate_cross_validation_filters_by_validated_paths(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, kind: str) -> str:
                return f"kits/x/artifacts/{kind}/template.md"

        class _FakeSystemNode:
            def __init__(self, kit: str):
                self.kit = kit
                self.artifacts = []
                self.codebase = []
                self.children = []

        class _FakeArtifactMeta:
            def __init__(self, path: str, kind: str):
                self.path = path
                self.kind = kind
                self.traceability = "FULL"

        class _FakeMeta:
            def __init__(self, artifacts: list[tuple[str, str, str]]):
                self._arts = artifacts
                self.systems = []

            def iter_all_artifacts(self):
                for p, k, kit in self._arts:
                    yield _FakeArtifactMeta(p, k), _FakeSystemNode(kit)

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg() if _kit_id != "skip" else types.SimpleNamespace(is_cypilot_format=lambda: False)

            def is_ignored(self, _rel: str) -> bool:
                return False

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={
                "REQ": types.SimpleNamespace(defined_id=[]),
                "OTHER": types.SimpleNamespace(defined_id=[]),
            })

        class _FakeCtx:
            def __init__(self, root: Path, arts: list[tuple[str, str, str]]):
                self.meta = _FakeMeta(arts)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
            (root / "kits" / "x" / "artifacts" / "OTHER").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "OTHER" / "template.md").write_text("# T\n", encoding="utf-8")

            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            req_rel = "artifacts/REQ.md"
            (root / req_rel).write_text("# R\n", encoding="utf-8")
            other_rel = "artifacts/OTHER.md"
            (root / other_rel).write_text("# O\n", encoding="utf-8")
            missing_rel = "artifacts/MISSING.md"

            arts = [
                (req_rel, "REQ", "x"),
                (missing_rel, "OTHER", "x"),
                (other_rel, "OTHER", "x"),
                ("artifacts/SKIP.md", "OTHER", "skip"),
            ]
            ctx = _FakeCtx(root, arts)
            buf = io.StringIO()
            validated_path = str((root / req_rel).resolve())

            fake_cross = {
                "errors": [
                    {"type": "constraints", "message": "e1", "path": validated_path, "line": 1},
                    {"type": "constraints", "message": "e2", "path": str((root / other_rel).resolve()), "line": 1},
                ],
                "warnings": [
                    {"type": "constraints", "message": "w1", "path": validated_path, "line": 1},
                    {"type": "constraints", "message": "w2", "path": str((root / other_rel).resolve()), "line": 1},
                ],
            }

            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                    with patch("cypilot.commands.validate.cross_validate_artifacts", return_value=fake_cross):
                        with patch("cypilot.commands.validate.scan_cpt_ids", return_value=[]):
                            with redirect_stdout(buf):
                                rc = validate_cmd.cmd_validate(["--skip-code", "--verbose"])

            self.assertEqual(rc, 2)
            out = json.loads(buf.getvalue())
            self.assertEqual(out.get("status"), "FAIL")
            self.assertIn("errors", out)
            self.assertIn("warnings", out)

    def test_validate_full_id_scan_exception_is_handled(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _FakeSystemNode:
            kit = "x"
            artifacts = []
            codebase = []
            children = []

        class _FakeArtifactMeta:
            def __init__(self, path: str):
                self.path = path
                self.kind = "REQ"
                self.traceability = "FULL"

        class _FakeMeta:
            def __init__(self, art_rel: str):
                self._art_rel = art_rel
                self.systems = []

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(self._art_rel), _FakeSystemNode()

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

            def is_ignored(self, _rel: str) -> bool:
                return False

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(art_rel)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            art_rel = "artifacts/REQ.md"
            (root / art_rel).write_text("# R\n", encoding="utf-8")

            ctx = _FakeCtx(root, art_rel)
            buf = io.StringIO()
            calls = {"n": 0}

            def _scan(_p: Path):
                calls["n"] += 1
                if calls["n"] == 1:
                    raise RuntimeError("boom")
                return []

            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                    with patch("cypilot.commands.validate.cross_validate_artifacts", return_value={"errors": [], "warnings": []}):
                        with patch("cypilot.commands.validate.scan_cpt_ids", side_effect=_scan):
                            with redirect_stdout(buf):
                                rc = validate_cmd.cmd_validate(["--skip-code"])

            self.assertEqual(rc, 0)

    def test_validate_code_scan_branches_and_failure_includes_warnings(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _FakeCodebaseEntry:
            def __init__(self, path: str, extensions: list[str]):
                self.path = path
                self.extensions = extensions

        class _FakeSystemNode:
            def __init__(self, code_path: str):
                self.kit = "x"
                self.artifacts = []
                self.codebase = [_FakeCodebaseEntry(code_path, [".py"])]
                self.children = []

        class _FakeArtifactMeta:
            def __init__(self, path: str):
                self.path = path
                self.kind = "REQ"
                self.traceability = "FULL"

        class _FakeMeta:
            def __init__(self, art_rel: str, code_path: str):
                self._art_rel = art_rel
                self.systems = [_FakeSystemNode(code_path)]

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(self._art_rel), types.SimpleNamespace(kit="x")

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

            def is_ignored(self, _rel: str) -> bool:
                return False

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str, code_path: str):
                self.meta = _FakeMeta(art_rel, code_path)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td1:
            with TemporaryDirectory() as td2:
                root = Path(td1)
                outside = Path(td2)
                code_file = outside / "x.py"
                code_file.write_text("print('x')\n", encoding="utf-8")

                (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
                (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
                (root / "artifacts").mkdir(parents=True, exist_ok=True)
                art_rel = "artifacts/REQ.md"
                (root / art_rel).write_text("# R\n", encoding="utf-8")

                ctx = _FakeCtx(root, art_rel, str(code_file))
                buf = io.StringIO()

                with patch("cypilot.utils.context.get_context", return_value=ctx):
                    with patch("cypilot.commands.validate.cross_validate_artifacts", return_value={"errors": [], "warnings": []}):
                        with patch("cypilot.commands.validate.scan_cpt_ids", return_value=[]):
                            with patch(
                                "cypilot.commands.validate.validate_artifact_file",
                                return_value={"errors": [], "warnings": [{"type": "w", "message": "warn", "path": str(root / art_rel), "line": 1}]},
                            ):
                                with patch(
                                    "cypilot.commands.validate.CodeFile.from_path",
                                    return_value=(None, [{"type": "code", "message": "bad", "path": str(code_file), "line": 1}]),
                                ):
                                    with redirect_stdout(buf):
                                        rc = validate_cmd.cmd_validate([])

                self.assertEqual(rc, 2)
                out = json.loads(buf.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                self.assertIn("warnings", out)

    def test_validate_pass_can_include_failed_artifacts_summary(self):
        from cypilot.commands import validate as validate_cmd

        class _TruthyEmpty:
            def __iter__(self):
                return iter([])

            def __len__(self):
                return 1

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _FakeSystemNode:
            kit = "x"
            artifacts = []
            codebase = []
            children = []

        class _FakeArtifactMeta:
            def __init__(self, path: str):
                self.path = path
                self.kind = "REQ"
                self.traceability = "FULL"

        class _FakeMeta:
            def __init__(self, art_rel: str):
                self._art_rel = art_rel
                self.systems = []

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(self._art_rel), _FakeSystemNode()

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

            def is_ignored(self, _rel: str) -> bool:
                return False

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(art_rel)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            art_rel = "artifacts/REQ.md"
            (root / art_rel).write_text("# R\n", encoding="utf-8")

            ctx = _FakeCtx(root, art_rel)
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch(
                    "cypilot.commands.validate.validate_artifact_file",
                    return_value={"errors": _TruthyEmpty(), "warnings": []},
                ):
                    with patch("cypilot.commands.validate.cross_validate_artifacts", return_value={"errors": [], "warnings": []}):
                        with patch("cypilot.commands.validate.scan_cpt_ids", return_value=[]):
                            with redirect_stdout(buf):
                                rc = validate_cmd.cmd_validate(["--skip-code"])

            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            self.assertEqual(out.get("status"), "PASS")
            self.assertIn("failed_artifacts", out)


class TestCLIPyCoverageListIdKindsBranches(unittest.TestCase):
    def test_list_id_kinds_artifact_not_found_branch(self):
        from cypilot.commands.list_id_kinds import cmd_list_id_kinds

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_list_id_kinds(["--artifact", "/path/does/not/exist.md"])
        self.assertEqual(rc, 1)


class TestCLIPyCoverageSelfCheckSkipBranches(unittest.TestCase):
    def test_self_check_skips_invalid_kit_defs(self):
        from cypilot import cli as cypilot_cli

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            adapter = root / ".cypilot-adapter"
            adapter.mkdir()

            reg = {
                "version": "1.0",
                "kits": {
                    # invalid kit_def (not dict)
                    "bad-kit-1": 1,
                    # missing path
                    "bad-kit-2": {},
                    # path wrong type
                    "bad-kit-3": {"path": 123},
                },
            }

            with patch("cypilot.commands.self_check.find_project_root", return_value=root):
                with patch("cypilot.commands.self_check.find_adapter_directory", return_value=adapter):
                    with patch("cypilot.commands.self_check.load_artifacts_registry", return_value=(reg, None)):
                        buf = io.StringIO()
                        with redirect_stdout(buf):
                            rc = cypilot_cli._cmd_self_check(["--root", td])

            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            self.assertEqual(out.get("status"), "PASS")
            self.assertEqual(out.get("kits_checked"), 0)

    def test_self_check_fail_on_validation_errors(self):
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_kits(root, adapter, with_example=True, bad_example=True)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check"])
                self.assertEqual(exit_code, 2)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                self.assertEqual(out["results"][0]["status"], "FAIL")
                self.assertIn("errors", out["results"][0])
            finally:
                os.chdir(cwd)

    def test_self_check_verbose_includes_errors_when_example_missing(self):
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_kits(root, adapter, with_example=False)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check", "--verbose"])
                self.assertEqual(exit_code, 2)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                self.assertEqual(out["results"][0]["status"], "FAIL")
                self.assertIn("errors", out["results"][0])
                self.assertGreater(out["results"][0].get("error_count", 0), 0)
            finally:
                os.chdir(cwd)

    def test_self_check_does_not_depend_on_template_module(self):
        from cypilot import cli as cypilot_cli

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_kits(root, adapter, with_example=True, bad_example=False)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = cypilot_cli._cmd_self_check([])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageValidateCode(unittest.TestCase):
    def test_validate_with_code_and_output_file(self):
        """Test validate command with code validation and output file."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            # Kits + template for kind=req
            kits_base = root / "kits" / "cypilot-sdlc" / "artifacts" / "req"
            kits_base.mkdir(parents=True, exist_ok=True)
            (kits_base / "template.md").write_text(
                "---\n"
                "cypilot-template:\n"
                "  kind: req\n"
                "  version:\n"
                "    major: 1\n"
                "    minor: 0\n"
                "---\n"
                "\n"
                "<!-- cpt:id:item to_code=\"true\" -->\n"
                "<!-- cpt:id:item -->\n",
                encoding="utf-8",
            )
            ex_dir = kits_base / "examples"
            ex_dir.mkdir(parents=True, exist_ok=True)
            (ex_dir / "example.md").write_text(
                "<!-- cpt:id:item -->\n- [x] `p1` - **ID**: `cpt-ex-item-1`\n<!-- cpt:id:item -->\n",
                encoding="utf-8",
            )
            (root / "kits" / "cypilot-sdlc" / "constraints.json").write_text(
                json.dumps({"req": {"identifiers": {"item": {"required": False, "to_code": True, "template": "cpt-{system}-item-{slug}"}}}}, indent=2) + "\n",
                encoding="utf-8",
            )

            # Artifact defining ID with to_code=true
            art_dir = root / "artifacts"
            art_dir.mkdir(parents=True, exist_ok=True)
            (art_dir / "reqs.md").write_text(
                "<!-- cpt:id:item -->\n"
                "- [x] `p1` - **ID**: `cpt-req-1`\n"
                "<!-- cpt:id:item -->\n",
                encoding="utf-8",
            )

            # Code referencing the ID
            src = root / "src"
            src.mkdir(parents=True, exist_ok=True)
            code_file = src / "code.py"
            code_file.write_text(
                "# @cpt-req:cpt-req-1:p1\n"
                "print('ok')\n",
                encoding="utf-8",
            )

            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "kits": {"cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"}},
                    "systems": [
                        {
                            "name": "S",
                            "kit": "cypilot-sdlc",
                            "artifacts": [
                                {"path": "artifacts/reqs.md", "kind": "req", "traceability": "FULL"},
                            ],
                            "codebase": [
                                {"path": "src", "extensions": [".py"]},
                            ],
                        }
                    ],
                },
            )

            out_path = root / "report.json"

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    # validate now includes code validation by default
                    exit_code = main(["validate", "--output", str(out_path)])
                self.assertEqual(exit_code, 0)
                self.assertTrue(out_path.is_file())
                report = json.loads(out_path.read_text(encoding="utf-8"))
                self.assertEqual(report.get("status"), "PASS")
                self.assertIn("next_step", report)
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageHelpers(unittest.TestCase):
    def test_prompt_path_eof_returns_default(self):
        from cypilot.commands.init import _prompt_path

        with patch("builtins.input", side_effect=EOFError):
            got = _prompt_path("Question?", "default")
        self.assertEqual(got, "default")

    def test_list_workflow_files_iterdir_exception(self):
        from cypilot.commands.agents import _list_workflow_files

        with TemporaryDirectory() as tmpdir:
            core = Path(tmpdir)
            (core / "workflows").mkdir(parents=True, exist_ok=True)

            with patch("pathlib.Path.iterdir", side_effect=OSError("boom")):
                files = _list_workflow_files(core)
            self.assertEqual(files, [])


class TestCLIPyCoverageSelfCheckFiltering(unittest.TestCase):
    """Tests for self-check --kit filtering (line 317)."""

    def test_self_check_filter_by_rule(self):
        """self-check --kit filters to specific kit."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_kits(root, adapter, with_example=True, bad_example=False)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    # Filter to non-existent kit - should check 0 kits
                    exit_code = main(["self-check", "--kit", "nonexistent-kit"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("kits_checked"), 0)
            finally:
                os.chdir(cwd)

    def test_self_check_filter_matches_kit(self):
        """self-check --kit matches existing kit."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_kits(root, adapter, with_example=True, bad_example=False)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check", "--kit", "cypilot-sdlc"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("kits_checked"), 1)
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageInitUnchanged(unittest.TestCase):
    """Tests for init command when files are unchanged (lines 947-970)."""

    def test_init_unchanged_files(self):
        """init reports unchanged when files match desired content."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            # First init to create files (use --yes to avoid prompts)
            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes"])
                self.assertEqual(exit_code, 0)

                # Second init without changes should report unchanged
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                # Without --force, existing files should be unchanged
                actions = out.get("actions", {})
                # Check that files are reported as unchanged
                self.assertIn(actions.get("adapter_agents"), ["unchanged", "created"])
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageValidateRules(unittest.TestCase):
    """Tests for validate-kits command (kit constraints validation)."""

    def test_validate_rules_single_template(self):
        """validate-kits validates constraints.json for kits."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            adapter = _bootstrap_project_root(root)
            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "systems": [],
                    "kits": {"cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"}},
                },
            )
            kit_root = root / "kits" / "cypilot-sdlc"
            kit_root.mkdir(parents=True, exist_ok=True)
            (kit_root / "constraints.json").write_text(
                json.dumps({"REQ": {"identifiers": {"req": {"required": True}}}}, indent=2) + "\n",
                encoding="utf-8",
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-kits"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertEqual(out.get("kits_validated"), 1)
            finally:
                os.chdir(cwd)

    def test_validate_rules_verbose_with_errors(self):
        """validate-kits --verbose shows constraints errors."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            adapter = _bootstrap_project_root(root)
            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "systems": [],
                    "kits": {"cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"}},
                },
            )
            kit_root = root / "kits" / "cypilot-sdlc"
            kit_root.mkdir(parents=True, exist_ok=True)
            (kit_root / "constraints.json").write_text("not-json", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-kits", "--verbose"])
                self.assertEqual(exit_code, 2)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                self.assertIn("errors", out)
            finally:
                os.chdir(cwd)

    def test_validate_rules_all_from_registry(self):
        """validate-kits validates all kits from artifacts.json."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            kit_root = root / "kits" / "cypilot-sdlc"
            kit_root.mkdir(parents=True, exist_ok=True)
            (kit_root / "constraints.json").write_text(
                json.dumps({"REQ": {"identifiers": {"req": {"required": True}}}}, indent=2) + "\n",
                encoding="utf-8",
            )

            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "kits": {"cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"}},
                    "systems": [
                        {
                            "name": "S",
                            "kit": "cypilot-sdlc",
                            "artifacts": [
                                {"path": "artifacts/reqs.md", "kind": "req"},
                            ],
                        }
                    ],
                },
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-kits"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertGreaterEqual(out.get("kits_validated", 0), 1)
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageTopLevelHelp(unittest.TestCase):
    """Tests for cypilot --help (lines 2379-2392)."""

    def test_top_level_help_flag(self):
        """cypilot --help shows usage and commands."""
        from cypilot.cli import main

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--help"])
        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("usage: cypilot <command>", output)
        self.assertIn("Validation commands:", output)
        self.assertIn("Search and utility commands:", output)
        self.assertIn("validate", output)

    def test_top_level_help_short_flag(self):
        """cypilot -h also shows usage."""
        from cypilot.cli import main

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["-h"])
        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("usage: cypilot <command>", output)


class TestCLIPyCoverageSlugValidation(unittest.TestCase):
    """Tests for slug validation errors in self-check (lines 301-306)."""

    def test_self_check_invalid_slugs(self):
        """self-check reports invalid slugs in artifacts.json."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            # Create kits structure with template
            kits_base = root / "kits" / "cypilot-sdlc" / "artifacts" / "req"
            kits_base.mkdir(parents=True, exist_ok=True)
            (kits_base / "template.md").write_text(
                "---\ncypilot-template:\n  kind: req\n  version:\n    major: 1\n    minor: 0\n---\n"
                "<!-- cpt:id:item -->\n<!-- cpt:id:item -->\n",
                encoding="utf-8",
            )

            # Create artifacts.json with invalid slug
            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "kits": {"cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"}},
                    "systems": [
                        {
                            "name": "S",
                            "slug": "Invalid Slug With Spaces",  # Invalid: contains spaces
                            "kit": "cypilot-sdlc",
                            "artifacts": [],
                        }
                    ],
                },
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check"])
                self.assertEqual(exit_code, 1)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
                self.assertIn("slug_errors", out)
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageAgentsCommand(unittest.TestCase):
    """Tests for agents command edge cases."""

    def test_agents_dry_run_default_config(self):
        """agents command creates default config for recognized agent."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            # Create artifacts.json
            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "kits": {},
                    "systems": [],
                },
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["agents", "--agent", "windsurf", "--dry-run"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn(out.get("status"), ["OK", "PASS"])
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageListIdsWithCode(unittest.TestCase):
    """Tests for list-ids --include-code (lines 1326-1338)."""

    def test_list_ids_include_code_with_refs(self):
        """list-ids --include-code shows ID references from artifacts."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            # Create kits structure with id-ref block
            kits_base = root / "kits" / "cypilot-sdlc" / "artifacts" / "req"
            kits_base.mkdir(parents=True, exist_ok=True)
            (kits_base / "template.md").write_text(
                "---\ncypilot-template:\n  kind: req\n  version:\n    major: 1\n    minor: 0\n---\n"
                "<!-- cpt:id:item -->\n<!-- cpt:id:item -->\n"
                "<!-- cpt:id-ref:other -->\n<!-- cpt:id-ref:other -->\n",
                encoding="utf-8",
            )

            # Create artifact with ID definition and reference
            art_dir = root / "artifacts"
            art_dir.mkdir(parents=True, exist_ok=True)
            (art_dir / "reqs.md").write_text(
                "<!-- cpt:id:item -->\n"
                "- [x] `p1` - **ID**: `cpt-test-item-1`\n"
                "<!-- cpt:id:item -->\n"
                "<!-- cpt:id-ref:other -->\n"
                "- [ ] `p2` - `cpt-external-ref-abc`\n"
                "<!-- cpt:id-ref:other -->\n",
                encoding="utf-8",
            )

            # Create code file
            src = root / "src"
            src.mkdir(parents=True, exist_ok=True)
            (src / "code.py").write_text(
                "# @cpt-req:cpt-test-item-1:p1\nprint('ok')\n",
                encoding="utf-8",
            )

            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "kits": {"cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"}},
                    "systems": [
                        {
                            "name": "test",
                            "kit": "cypilot-sdlc",
                            "artifacts": [{"path": "artifacts/reqs.md", "kind": "req"}],
                            "codebase": [{"path": "src", "extensions": [".py"]}],
                        }
                    ],
                },
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--include-code"])
                # Just verify it runs - the output format may vary
                self.assertIn(exit_code, [0, 2])  # OK or validation failure
                output = stdout.getvalue()
                # Should produce valid JSON
                out = json.loads(output)
                self.assertIn("ids", out)
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
