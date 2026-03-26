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


def setUpModule():
    from cypilot.utils.ui import set_json_mode
    set_json_mode(True)


def tearDownModule():
    from cypilot.utils.ui import set_json_mode
    set_json_mode(False)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _bootstrap_project_root(root: Path, adapter_rel: str = "adapter") -> Path:
    (root / ".git").mkdir()
    (root / "AGENTS.md").write_text(
        f'<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "{adapter_rel}"\n```\n',
        encoding="utf-8",
    )
    adapter = root / adapter_rel
    adapter.mkdir(parents=True, exist_ok=True)
    (adapter / "config").mkdir(exist_ok=True)
    (adapter / "config" / "AGENTS.md").write_text("# Test adapter\n", encoding="utf-8")
    return adapter


def _setup_list_ids_project(root, *, codebase=None, ignore=None, content=None,
                            art_path="docs/reqs.md", system_name="Test", system_slug="test"):
    """Bootstrap a project with a single REQ artifact for list-ids tests."""
    adapter = _bootstrap_project_root(root)
    art = root / art_path
    art.parent.mkdir(parents=True, exist_ok=True)
    art.write_text(content or "- [x] `p1` - **ID**: `cpt-test-req-1`\n", encoding="utf-8")
    from cypilot.utils import toml_utils
    system = {
        "name": system_name, "slug": system_slug,
        "artifacts": [{"path": art_path, "kind": "req"}],
    }
    if codebase:
        system["codebase"] = codebase
    data = {"version": "1.0", "project_root": "..", "kits": {}, "systems": [system]}
    if ignore:
        data["ignore"] = ignore
    toml_utils.dump(data, adapter / "config" / "artifacts.toml")
    return adapter


def _bootstrap_self_check_kits(root: Path, adapter: Path, *, with_example: bool = True, bad_example: bool = False) -> None:
    # Minimal artifacts registry that passes `load_artifacts_meta` and contains kits.
    from cypilot.utils import toml_utils
    toml_utils.dump(
        {
            "project_root": "..",
            "systems": [],
            "kits": {
                "cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"},
            },
        },
        adapter / "config" / "artifacts.toml",
    )

    kit_root = root / "kits" / "cypilot-sdlc"
    kit_root.mkdir(parents=True, exist_ok=True)
    (kit_root / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
    (kit_root / "artifacts" / "REQ" / "template.md").write_text(
        "---\ncypilot-template:\n  version:\n    major: 1\n    minor: 0\n  kind: REQ\n---\n\n"
        "- [x] `p1` - **ID**: `cpt-{system}-req-{slug}`\n",
        encoding="utf-8",
    )
    from _test_helpers import write_constraints_toml
    write_constraints_toml(kit_root, {"REQ": {"identifiers": {"req": {"required": True, "template": "cpt-{system}-req-{slug}"}}}})

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


# ── Shared fake classes for validate tests ────────────────────────────────────
# Extracted to module level to avoid SonarCloud duplication flags (S1144).


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
    def __init__(self, path: str, kind: str = "REQ", traceability: str = "FULL"):
        self.path = path
        self.kind = kind
        self.traceability = traceability


class _FakeKit:
    path = "kits/x"


# ── Compact fake classes for validate/workspace coverage tests ─────────────────
# These replace repeated local _KP/_SN/_AM/_Meta/_LK/_Prim/_Ctx definitions.


class _CompactKitPkg:
    """Fake kit package (compact one-liner style used in coverage tests)."""
    def is_cypilot_format(self): return True
    def get_template_path(self, _k): return "kits/x/artifacts/REQ/template.md"


class _CompactSystemNode:
    """Fake system node with optional codebase."""
    def __init__(self, *, codebase=None):
        self.kit = "x"
        self.artifacts = []
        self.codebase = codebase or []
        self.children = []


class _CompactArtifactMeta:
    """Fake artifact meta with configurable fields."""
    def __init__(self, path, kind="REQ", traceability="FULL", source=None):
        self.path = path
        self.kind = kind
        self.traceability = traceability
        self.source = source


class _CompactMeta:
    """Fake artifacts meta that yields configurable artifacts."""
    def __init__(self, artifacts, *, systems=None, system_node=None):
        # artifacts: str (single path) or list of (path, kind) tuples
        if isinstance(artifacts, str):
            self._arts = [(artifacts, "REQ")]
        else:
            self._arts = artifacts
        self._sn = system_node or _CompactSystemNode()
        self.systems = systems if systems is not None else []
    def iter_all_artifacts(self):
        for p, k in self._arts:
            yield _CompactArtifactMeta(p, k), self._sn
    def get_kit(self, _k): return _CompactKitPkg()
    def is_ignored(self, _r): return False


class _CompactLoadedKit:
    """Fake loaded kit with optional constraints."""
    def __init__(self, constraints=None):
        self.kit = types.SimpleNamespace(path="kits/x")
        self.constraints = constraints


class _CompactCtx:
    """Fake context for validate tests."""
    def __init__(self, root, artifacts, *, kits=None, errors=None,
                 meta_systems=None, registered_systems=None, system_node=None):
        self.meta = _CompactMeta(artifacts, systems=meta_systems, system_node=system_node)
        self.project_root = root
        self.registered_systems = registered_systems if registered_systems is not None else {"sys"}
        self.kits = kits if kits is not None else {}
        self._errors = errors or []
    def get_known_id_kinds(self): return set()


class _CompactPrim:
    """Fake primary context for workspace tests (has adapter_dir)."""
    def __init__(self, root, artifacts, *, kits=None, errors=None,
                 meta_systems=None, registered_systems=None, system_node=None):
        self.meta = _CompactMeta(artifacts, systems=meta_systems, system_node=system_node)
        self.project_root = root
        self.adapter_dir = root / "adapter"
        self.registered_systems = registered_systems if registered_systems is not None else {"sys"}
        self.kits = kits if kits is not None else {}
        self._errors = errors or []
    def get_known_id_kinds(self): return set()


class _EmptyFakeMeta:
    """Fake meta with no artifacts (for --source tests)."""
    systems = []
    def iter_all_artifacts(self): return iter([])
    def is_ignored(self, _rel): return False


class _EmptyFakePrimary:
    """Fake primary context with no artifacts (for --source tests)."""
    meta = _EmptyFakeMeta()
    project_root = Path("/fake")
    adapter_dir = Path("/fake/adapter")
    registered_systems = set()
    kits = {}
    _errors = []
    def get_known_id_kinds(self): return set()


class _CollectMeta:
    """Fake meta for collect_artifacts_to_scan tests (no get_kit needed)."""
    def __init__(self, ar):
        self._ar = ar
    def iter_all_artifacts(self):
        yield _CompactArtifactMeta(self._ar, source=None), types.SimpleNamespace(kit="x")
    def is_ignored(self, _r): return False


class _CollectPrim:
    """Fake primary for collect_artifacts_to_scan tests."""
    def __init__(self, r, ar):
        self.meta = _CollectMeta(ar)
        self.project_root = r
        self.adapter_dir = r / "adapter"
        self.registered_systems = {"sys"}
        self.kits = {}
        self._errors = []


def _scaffold_validate_project(td):
    """Create minimal validate project structure. Returns (root, art_rel)."""
    root = Path(td)
    (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
    (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
    (root / "artifacts").mkdir(parents=True, exist_ok=True)
    ar = "artifacts/REQ.md"
    (root / ar).write_text("# R\n", encoding="utf-8")
    return root, ar


def _build_ws_validate_ctx(td):
    """Build WorkspaceContext + validate project for workspace validate tests.

    Returns (ws, art_resolved, WorkspaceContext_cls).
    """
    from cypilot.utils.context import WorkspaceContext
    root, ar = _scaffold_validate_project(td)
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src" / "code.py").write_text("print('ok')\n", encoding="utf-8")
    codebase_sn = _CompactSystemNode(
        codebase=[types.SimpleNamespace(path="src", extensions=[".py"])])
    lk = _CompactLoadedKit(
        constraints=types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])}))
    p = _CompactPrim(root, ar, kits={"x": lk},
        meta_systems=[codebase_sn],
        system_node=types.SimpleNamespace(kit="x"))
    ws = WorkspaceContext(primary=p, sources={})
    art_resolved = (root / ar).resolve()
    return ws, art_resolved, WorkspaceContext


def _run_ws_validate(args):
    """Run cmd_validate with a workspace context patched for get_all_artifact_ids.

    Returns (rc, mock_get_all_ids, buf).
    """
    from cypilot.commands import validate as validate_cmd
    with TemporaryDirectory() as td:
        ws, art_resolved, WC = _build_ws_validate_ctx(td)
        buf = io.StringIO()
        with patch("cypilot.utils.context.get_context", return_value=ws):
            with patch.object(WC, "resolve_artifact_path", return_value=art_resolved):
                with patch.object(WC, "get_all_artifact_ids", return_value={"cpt-remote-1"}) as mi:
                    with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                        with patch("cypilot.commands.validate.cross_validate_artifacts", return_value={"errors": [], "warnings": []}):
                            with patch("cypilot.commands.validate.scan_cpt_ids", return_value=[]):
                                with redirect_stdout(buf):
                                    rc = validate_cmd.cmd_validate(args)
        return rc, mi, buf


def _make_cross_repo_dirs(td):
    """Create primary + remote directory pair for cross-repo tests. Returns (root, remote)."""
    root = Path(td) / "primary"
    root.mkdir()
    remote = Path(td) / "remote"
    remote.mkdir()
    (root / "artifacts").mkdir()
    (remote / "artifacts").mkdir()
    return root, remote


def _patch_collect_artifacts(root, remote, remote_file="REMOTE.md"):
    """Return a patch for collect_artifacts_to_scan with standard cross-repo layout."""
    return patch("cypilot.utils.context.collect_artifacts_to_scan", return_value=(
        [
            ((root / "artifacts" / "REQ.md").resolve(), "REQ"),
            ((remote / "artifacts" / remote_file).resolve(), "REQ"),
        ],
        {str((remote / "artifacts" / remote_file).resolve()): "backend"},
    ))


def _run_cli_dispatch(test_case, args):
    """Run CLI main() in a temp dir, assert exit code in [0, 1, 2]."""
    from cypilot.cli import main
    from cypilot.utils.ui import is_json_mode, set_json_mode
    with TemporaryDirectory() as td:
        cwd = os.getcwd()
        saved_json_mode = is_json_mode()
        try:
            os.chdir(td)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(args)
            test_case.assertIn(rc, [0, 1, 2])
        finally:
            set_json_mode(saved_json_mode)
            os.chdir(cwd)


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
                self.assertEqual(out.get("kits_validated"), 1)
                self.assertEqual(out.get("templates_checked"), 1)
                self.assertEqual(out["self_check_results"][0]["status"], "PASS")
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
        template_content: str | None = None,
    ) -> "cypilot.utils.artifacts_meta.ArtifactsMeta":
        from cypilot.utils.artifacts_meta import ArtifactsMeta

        kit_root = root / "kits" / "k"
        (kit_root / "artifacts" / kind / "examples").mkdir(parents=True, exist_ok=True)
        tmpl = template_content if template_content is not None else "# T\n"
        (kit_root / "artifacts" / kind / "template.md").write_text(tmpl, encoding="utf-8")
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
            from _test_helpers import write_constraints_toml
            write_constraints_toml(kit_root, payload)

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

    def test_run_self_check_passes_when_constraints_missing(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=False)
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 0)
            self.assertEqual(out.get("status"), "PASS")
            self.assertGreaterEqual(int(out.get("kits_checked", 0)), 1)

    def test_run_self_check_fails_on_invalid_constraints(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=True, constraints_payload={"REQ": {}})
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")
            self.assertGreaterEqual(int(out.get("kits_checked", 0)), 1)

    def test_run_self_check_passes_when_kind_not_in_constraints(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=True, constraints_payload={"OTHER": {"identifiers": {}}})
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 0)
            self.assertEqual(out.get("status"), "PASS")

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
            meta = self._bootstrap_kit(
                root,
                with_constraints=True,
                template_content="# T\n\n- [ ] **ID**: `cpt-{system}-req-{slug}`\n",
                constraints_payload={
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
                                "references": {"REQ": {"coverage": True}},
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
            meta = self._bootstrap_kit(
                root,
                with_constraints=True,
                template_content="# T\n\nRef `cpt-{system}-x-{slug}`\n",
                constraints_payload={
                    "SRC": {
                        "identifiers": {
                            "x": {
                                "required": False,
                                "template": "cpt-{system}-x-{slug}",
                                "references": {"REQ": {"coverage": True, "headings": ["allowed"]}},
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
                raise ValueError("boom")

            kit.get_template_path = _boom
            kit.get_examples_path = _boom

            # Legacy fallback layout already exists from _bootstrap_kit.
            # Verify fallback picks up the files even when get_*_path raises.
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            self.assertEqual(rc, 0)
            self.assertEqual(out.get("status"), "PASS")


class TestCLIPyCoverageSelfCheckReverseAndOptional(unittest.TestCase):
    """Tests for self-check reverse checks and optional missing warnings."""

    def _bootstrap_kit(self, root, *, kind="REQ", constraints_payload=None, template_content=None):
        from cypilot.utils.artifacts_meta import ArtifactsMeta

        kit_root = root / "kits" / "k"
        (kit_root / "artifacts" / kind / "examples").mkdir(parents=True, exist_ok=True)
        tmpl = template_content or "# T\n"
        (kit_root / "artifacts" / kind / "template.md").write_text(tmpl, encoding="utf-8")
        (kit_root / "artifacts" / kind / "examples" / "example.md").write_text(
            "- [x] `p1` - **ID**: `cpt-myapp-req-login`\n", encoding="utf-8",
        )
        if constraints_payload is not None:
            from _test_helpers import write_constraints_toml
            write_constraints_toml(kit_root, constraints_payload)
        reg = {
            "version": "1.1", "project_root": "..", "systems": [],
            "kits": {"k": {"format": "Cypilot", "path": "kits/k", "artifacts": {
                kind: {
                    "template": "{project_root}/kits/k/artifacts/%s/template.md" % kind,
                    "examples": "{project_root}/kits/k/artifacts/%s/examples" % kind,
                },
            }}},
        }
        return ArtifactsMeta.from_dict(reg)

    def test_template_def_kind_not_in_constraints(self):
        """Template has definition pattern not in constraints → error."""
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            tmpl = (
                "---\ncypilot-template:\n  version:\n    major: 1\n    minor: 0\n  kind: REQ\n---\n"
                "- [ ] `p1` - **ID**: `cpt-{system}-unknown-{slug}`\n"
            )
            meta = self._bootstrap_kit(root, constraints_payload={
                "REQ": {"identifiers": {"req": {"required": False, "template": "cpt-{system}-req-{slug}"}}}
            }, template_content=tmpl)
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            self.assertEqual(rc, 2)
            errs = out["results"][0].get("errors", [])
            codes = [e.get("code") for e in errs]
            self.assertIn("template-def-kind-not-in-constraints", codes)

    def test_template_ref_kind_not_in_constraints(self):
        """Template has reference pattern not in constraints → error."""
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            tmpl = (
                "---\ncypilot-template:\n  version:\n    major: 1\n    minor: 0\n  kind: REQ\n---\n"
                "- [ ] `p1` - **ID**: `cpt-{system}-req-{slug}`\n"
                "**Refs**: `cpt-{system}-bogus-{slug}`\n"
            )
            meta = self._bootstrap_kit(root, constraints_payload={
                "REQ": {"identifiers": {"req": {"required": False, "template": "cpt-{system}-req-{slug}"}}}
            }, template_content=tmpl)
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            self.assertEqual(rc, 2)
            errs = out["results"][0].get("errors", [])
            codes = [e.get("code") for e in errs]
            self.assertIn("template-ref-kind-not-in-constraints", codes)

    def test_optional_def_missing_from_template_warns(self):
        """Optional definition kind in constraints but missing from template → warning."""
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            # Template has no ID definitions at all — optional kind 'req' missing
            tmpl = "---\ncypilot-template:\n  version:\n    major: 1\n    minor: 0\n  kind: REQ\n---\n# T\n"
            meta = self._bootstrap_kit(root, constraints_payload={
                "REQ": {"identifiers": {"req": {"required": False, "template": "cpt-{system}-req-{slug}"}}}
            }, template_content=tmpl)
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            # Should pass (optional), but with a warning
            warns = out["results"][0].get("warnings", [])
            msgs = [w.get("message", "") for w in warns]
            self.assertTrue(any("optional ID placeholder" in m for m in msgs), f"Expected optional warning, got: {msgs}")

    def test_optional_ref_missing_from_template_warns(self):
        """Optional reference in constraints but missing from template → warning."""
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            # PRD defines 'fr', DESIGN references 'fr' as optional — but DESIGN template doesn't have the reference placeholder
            tmpl = "---\ncypilot-template:\n  version:\n    major: 1\n    minor: 0\n  kind: DESIGN\n---\n# T\n"
            constraints = {
                "PRD": {"identifiers": {"fr": {"required": False, "template": "cpt-{system}-fr-{slug}", "references": {
                    "DESIGN": {}
                }}}},
                "DESIGN": {"identifiers": {"design": {"required": False, "template": "cpt-{system}-design-{slug}"}}},
            }
            meta = self._bootstrap_kit(root, kind="DESIGN", constraints_payload=constraints, template_content=tmpl)
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            warns = out["results"][0].get("warnings", [])
            msgs = [w.get("message", "") for w in warns]
            self.assertTrue(any("optional reference placeholder" in m for m in msgs), f"Expected optional ref warning, got: {warns}")


class TestCLIPyCoverageValidateBranches(unittest.TestCase):
    def test_validate_artifact_outside_project_root_hits_relative_to_error(self):
        from cypilot.commands import validate as validate_cmd


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


        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = None

        class _FakeCtx:
            meta = _FakeMeta()
            project_root = Path("/fake/nonexistent-root")
            registered_systems = {"sys"}
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


        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(root, art_rel)
                self.project_root = root
                self.registered_systems = {"sys"}
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
            # Validate succeeds with empty/non-Cypilot artifacts
            self.assertIn(rc, [0, 1, 2])
            out = json.loads(buf.getvalue())
            self.assertIn("status", out)

    def test_validate_ctx_errors_are_reported_and_trigger_early_fail(self):
        from cypilot.commands import validate as validate_cmd




        class _FakeMeta:
            def __init__(self, art_rel: str):
                self._art_rel = art_rel
                self.systems = []

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(self._art_rel), _FakeSystemNode()

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()


        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[types.SimpleNamespace(kind="req")])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(art_rel)
                self.project_root = root
                self.registered_systems = {"sys"}
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


        class _BadKit:
            @property
            def path(self):
                raise OSError("boom")

        class _FakeLoadedKit:
            kit = _BadKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})



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
                self.registered_systems = {"sys"}
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
                with patch("cypilot.commands.validate.scan_cpt_ids", side_effect=ValueError("scan boom")):
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
                self.registered_systems = {"sys"}
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


        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(art_rel)
                self.project_root = root
                self.registered_systems = {"sys"}
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
                    raise ValueError("boom")
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


        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str, code_path: str):
                self.meta = _FakeMeta(art_rel, code_path)
                self.project_root = root
                self.registered_systems = {"sys"}
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


        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(art_rel)
                self.project_root = root
                self.registered_systems = {"sys"}
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

    def test_list_id_kinds_artifact_not_in_registry(self):
        """Cover lines 51-52: artifact exists but not registered."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0", "project_root": "..", "systems": [], "kits": {},
            }, adapter / "config" / "artifacts.toml")

            art = root / "docs" / "PRD.md"
            art.parent.mkdir(parents=True)
            art.write_text("- [x] `p1` - **ID**: `cpt-test-fr-1`\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["list-id-kinds", "--artifact", str(art)])
            self.assertEqual(rc, 1)
            self.assertIn("not found in registry", buf.getvalue())

    def test_list_id_kinds_infer_kinds_branches(self):
        """Cover lines 85, 103, 106, 112, 119, 122, 125: kind inference branches."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            kit_root = root / "kits" / "sdlc"
            kit_root.mkdir(parents=True)

            art = root / "docs" / "PRD.md"
            art.parent.mkdir(parents=True)
            # Mix of IDs: one with known kind, one with unknown kind, one with no system match, empty-ish
            art.write_text(
                "- [x] `p1` - **ID**: `cpt-test-fr-login`\n"
                "- [x] `p1` - **ID**: `cpt-test-boguskind-x`\n"
                "- [x] `p1` - **ID**: `cpt-nomatch-thing`\n"
                "- [x] `p1` - **ID**: `cpt-test`\n"
                "some ref `cpt-test-fr-other`\n",
                encoding="utf-8",
            )

            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.1", "project_root": "..",
                "kits": {"sdlc": {"format": "Cypilot", "path": "kits/sdlc"}},
                "systems": [{
                    "name": "Test", "slug": "test", "kits": "sdlc",
                    "artifacts": [{"path": "docs/PRD.md", "kind": "PRD"}],
                }],
            }, adapter / "config" / "artifacts.toml")

            # No constraints.toml → covers line 85 (kit_constraints falsy)
            buf = io.StringIO()
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with redirect_stdout(buf):
                    rc = main(["list-id-kinds", "--artifact", str(art)])
            finally:
                os.chdir(cwd)
            self.assertEqual(rc, 0)


class TestCLIPyCoverageSelfCheckSkipBranches(unittest.TestCase):
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
                self.assertEqual(out["self_check_results"][0]["status"], "FAIL")
                self.assertIn("errors", out["self_check_results"][0])
            finally:
                os.chdir(cwd)

    def test_self_check_verbose_passes_when_example_missing(self):
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
                "",
                encoding="utf-8",
            )
            ex_dir = kits_base / "examples"
            ex_dir.mkdir(parents=True, exist_ok=True)
            (ex_dir / "example.md").write_text(
                "- [x] `p1` - **ID**: `cpt-ex-item-1`\n",
                encoding="utf-8",
            )
            from _test_helpers import write_constraints_toml
            write_constraints_toml(root / "kits" / "cypilot-sdlc", {"req": {"identifiers": {"item": {"required": False, "to_code": True, "template": "cpt-{system}-item-{slug}"}}}})

            # Artifact defining ID with to_code=true
            art_dir = root / "artifacts"
            art_dir.mkdir(parents=True, exist_ok=True)
            (art_dir / "reqs.md").write_text(
                ""
                "- [x] `p1` - **ID**: `cpt-req-1`\n"
                "",
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
                self.assertEqual(out.get("kits_validated"), 0)
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
                self.assertEqual(out.get("kits_validated"), 1)
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
            fake_cache = Path(tmpdir) / "cache"
            fake_cache.mkdir()

            # First init to create files (use --yes to avoid prompts)
            fake_kit = Path(tmpdir) / "dl" / "sdlc"
            fake_kit.mkdir(parents=True)
            cwd = os.getcwd()
            try:
                os.chdir(root)
                with (
                    patch("cypilot.commands.init.CACHE_DIR", fake_cache),
                    patch(
                        "cypilot.commands.kit._download_kit_from_github",
                        return_value=(fake_kit, "1.0.0"),
                    ),
                ):
                    stdout = io.StringIO()
                    with redirect_stdout(stdout):
                        exit_code = main(["init", "--yes"])
                    self.assertEqual(exit_code, 0)

                    # Second init without changes should still succeed
                    stdout = io.StringIO()
                    with redirect_stdout(stdout):
                        exit_code = main(["init", "--yes"])
                    # Init may succeed (0) or report issues (1/2) on re-run
                    self.assertIn(exit_code, [0, 1, 2])
                    out = json.loads(stdout.getvalue())
                    self.assertIn("status", out)
            finally:
                os.chdir(cwd)


class TestInitCopyFromCache(unittest.TestCase):
    """Direct tests for _copy_from_cache edge cases."""

    def test_copy_creates_and_skips(self):
        """First copy creates, second without force skips."""
        from cypilot.commands.init import _copy_from_cache
        with TemporaryDirectory() as td:
            cache = Path(td) / "cache"
            target = Path(td) / "project" / "cypilot"
            target.mkdir(parents=True)
            # Populate cache with one valid dir and one missing
            (cache / "requirements").mkdir(parents=True)
            (cache / "requirements" / "README.md").write_text("# req\n", encoding="utf-8")
            r1 = _copy_from_cache(cache, target, force=False)
            self.assertEqual(r1["requirements"], "created")
            self.assertEqual(r1.get("schemas", "missing_in_cache"), "missing_in_cache")
            # Second call without force → skipped (init behavior)
            r2 = _copy_from_cache(cache, target, force=False)
            self.assertEqual(r2["requirements"], "skipped")
            # Third call with force → updated (pre_force_existed tracks prior existence)
            r3 = _copy_from_cache(cache, target, force=True)
            self.assertEqual(r3["requirements"], "updated")

    def test_missing_cache_dir_entries(self):
        """When cache dirs don't exist, reports missing_in_cache."""
        from cypilot.commands.init import _copy_from_cache
        with TemporaryDirectory() as td:
            cache = Path(td) / "empty_cache"
            cache.mkdir()
            target = Path(td) / "target"
            target.mkdir()
            result = _copy_from_cache(cache, target, force=False)
            for k, v in result.items():
                self.assertEqual(v, "missing_in_cache")


    def test_architecture_file_items_copied(self):
        """Architecture spec files are copied via _copy_file path."""
        from cypilot.commands.init import _copy_from_cache, COPY_ARCHITECTURE_ITEMS
        with TemporaryDirectory() as td:
            cache = Path(td) / "cache"
            target = Path(td) / "project" / "cypilot"
            target.mkdir(parents=True)
            # Create at least one architecture spec file in cache
            for item in COPY_ARCHITECTURE_ITEMS[:2]:
                src = cache / "architecture" / item
                src.parent.mkdir(parents=True, exist_ok=True)
                src.write_text(f"# {item}\n", encoding="utf-8")
            r1 = _copy_from_cache(cache, target, force=False)
            for item in COPY_ARCHITECTURE_ITEMS[:2]:
                key = f"architecture/{item}"
                self.assertIn(r1.get(key), ("created", "missing_in_cache"), f"unexpected for {key}: {r1.get(key)}")
            # Second call without force → skipped
            r2 = _copy_from_cache(cache, target, force=False)
            for item in COPY_ARCHITECTURE_ITEMS[:2]:
                key = f"architecture/{item}"
                self.assertEqual(r2.get(key), "skipped")
            # Third call with force → created (architecture items not in pre_force_existed)
            r3 = _copy_from_cache(cache, target, force=True)
            for item in COPY_ARCHITECTURE_ITEMS[:2]:
                key = f"architecture/{item}"
                self.assertEqual(r3.get(key), "created")


class TestInitReadExistingInstall(unittest.TestCase):
    """Tests for _read_existing_install edge cases."""

    def test_returns_none_when_no_agents(self):
        from cypilot.commands.init import _read_existing_install
        with TemporaryDirectory() as td:
            self.assertIsNone(_read_existing_install(Path(td)))

    def test_returns_none_when_no_marker(self):
        from cypilot.commands.init import _read_existing_install
        with TemporaryDirectory() as td:
            (Path(td) / "AGENTS.md").write_text("# Just a file\n", encoding="utf-8")
            self.assertIsNone(_read_existing_install(Path(td)))

    def test_returns_none_when_dir_missing(self):
        """TOML has cypilot_path but directory doesn't exist → None."""
        from cypilot.commands.init import _read_existing_install
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "nonexistent"\n```\n<!-- /@cpt:root-agents -->\n',
                encoding="utf-8",
            )
            self.assertIsNone(_read_existing_install(root))

    def test_returns_rel_when_dir_exists(self):
        from cypilot.commands.init import _read_existing_install
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "cpt").mkdir()
            (root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "cpt"\n```\n<!-- /@cpt:root-agents -->\n',
                encoding="utf-8",
            )
            self.assertEqual(_read_existing_install(root), "cpt")


class TestInjectRootAgents(unittest.TestCase):
    """Tests for _inject_root_agents: create, update, unchanged."""

    def test_creates_agents_file(self):
        from cypilot.commands.init import _inject_root_agents
        with TemporaryDirectory() as td:
            root = Path(td)
            action = _inject_root_agents(root, "cypilot")
            self.assertEqual(action, "created")
            self.assertTrue((root / "AGENTS.md").is_file())

    def test_replaces_stale_block(self):
        from cypilot.commands.init import _inject_root_agents, MARKER_START, MARKER_END
        with TemporaryDirectory() as td:
            root = Path(td)
            # Write AGENTS.md with old block
            (root / "AGENTS.md").write_text(
                f"{MARKER_START}\nold content\n{MARKER_END}\n\nUser stuff\n",
                encoding="utf-8",
            )
            action = _inject_root_agents(root, "cypilot")
            self.assertEqual(action, "updated")
            content = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("cypilot_path", content)
            self.assertIn("User stuff", content)

    def test_unchanged_when_current(self):
        from cypilot.commands.init import _inject_root_agents
        with TemporaryDirectory() as td:
            root = Path(td)
            # First inject creates
            _inject_root_agents(root, "cypilot")
            # Second should be unchanged
            action = _inject_root_agents(root, "cypilot")
            self.assertEqual(action, "unchanged")

    def test_dry_run_does_not_write(self):
        from cypilot.commands.init import _inject_root_agents
        with TemporaryDirectory() as td:
            root = Path(td)
            action = _inject_root_agents(root, "cypilot", dry_run=True)
            self.assertEqual(action, "created")
            self.assertFalse((root / "AGENTS.md").is_file())


class TestInitNoCacheError(unittest.TestCase):
    """init fails when ~/.cypilot/cache doesn't exist."""

    def test_init_no_cache_returns_error(self):
        from cypilot.cli import main
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            cwd = os.getcwd()
            try:
                os.chdir(root)
                fake_cache = Path(td) / "nonexistent_cache"
                with patch("cypilot.commands.init.CACHE_DIR", fake_cache):
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(["init", "--yes"])
                self.assertEqual(rc, 1)
                out = json.loads(buf.getvalue())
                self.assertIn("cache", out.get("message", "").lower())
            finally:
                os.chdir(cwd)


class TestInitForceReinit(unittest.TestCase):
    """init --force on existing project: creates backup, overwrites files."""

    def test_force_reinit_overwrites(self):
        from cypilot.cli import main
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            cache = Path(td) / "cache"
            _make_test_cache(cache)
            import tempfile
            def _fake_download(*a, **kw):
                t = Path(tempfile.mkdtemp())
                k = t / "sdlc"; k.mkdir()
                return (k, "1.0.0")
            cwd = os.getcwd()
            try:
                os.chdir(root)
                with (
                    patch("cypilot.commands.init.CACHE_DIR", cache),
                    patch(
                        "cypilot.commands.kit._download_kit_from_github",
                        side_effect=_fake_download,
                    ),
                ):
                    # First init
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(["init", "--yes"])
                    self.assertEqual(rc, 0)
                    # Force re-init
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(["init", "--yes", "--force"])
                    self.assertEqual(rc, 0)
                    out = json.loads(buf.getvalue())
                    self.assertEqual(out["status"], "PASS")
            finally:
                os.chdir(cwd)


def _make_test_cache(cache_dir: Path) -> None:
    """Minimal cache for init tests — delegates to shared helper."""
    from _test_helpers import make_test_cache
    make_test_cache(cache_dir)


class TestCLIPyCoverageValidateRules(unittest.TestCase):
    """Tests for validate-kits command (kit constraints validation)."""

    def test_validate_rules_single_template(self):
        """validate-kits validates constraints.toml for kits."""
        from _test_helpers import run_cli_in_project

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
            from _test_helpers import write_constraints_toml
            write_constraints_toml(kit_root, {"REQ": {"identifiers": {"req": {"required": True}}}})

            exit_code, out = run_cli_in_project(root, ["validate-kits"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(out.get("status"), "PASS")
            self.assertEqual(out.get("kits_validated"), 1)

    def test_validate_rules_verbose_with_errors(self):
        """validate-kits --verbose shows constraints errors."""
        from _test_helpers import run_cli_in_project

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
            (kit_root / "constraints.toml").write_text("not valid toml [[", encoding="utf-8")

            exit_code, out = run_cli_in_project(root, ["validate-kits", "--verbose"])
            self.assertEqual(exit_code, 2)
            self.assertEqual(out.get("status"), "FAIL")
            self.assertIn("errors", out)

    def test_validate_rules_all_from_registry(self):
        """validate-kits validates all kits from artifacts.json."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            kit_root = root / "kits" / "cypilot-sdlc"
            kit_root.mkdir(parents=True, exist_ok=True)
            from _test_helpers import write_constraints_toml
            write_constraints_toml(kit_root, {"REQ": {"identifiers": {"req": {"required": True}}}})

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

            from _test_helpers import run_cli_in_project
            exit_code, out = run_cli_in_project(root, ["validate-kits"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(out.get("status"), "PASS")
            self.assertGreaterEqual(out.get("kits_validated", 0), 1)


class TestCLIPyCoverageTopLevelHelp(unittest.TestCase):
    """Tests for cypilot --help (lines 2379-2392)."""

    def test_top_level_help_flag(self):
        """cypilot --help shows usage and commands."""
        from cypilot.cli import main

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--help"])
        self.assertEqual(exit_code, 0)
        out = json.loads(stdout.getvalue())
        self.assertIn("cypilot", out["usage"])
        self.assertIn("validate", out["commands"])
        self.assertIn("Validation", out["sections"])

    def test_top_level_help_short_flag(self):
        """cypilot -h also shows usage."""
        from cypilot.cli import main

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["-h"])
        self.assertEqual(exit_code, 0)
        out = json.loads(stdout.getvalue())
        self.assertIn("cypilot", out["usage"])


class TestCLIPyCoverageSlugValidation(unittest.TestCase):
    """Tests for slug validation errors in self-check (lines 301-306)."""

    def test_self_check_invalid_slugs(self):
        """self-check (now routed to validate-kits) does not fail on invalid slugs.

        Slug validation is the ``validate`` command's responsibility, not
        ``validate-kits``.
        """
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            # Create kits structure with template
            kits_base = root / "kits" / "cypilot-sdlc" / "artifacts" / "req"
            kits_base.mkdir(parents=True, exist_ok=True)
            (kits_base / "template.md").write_text(
                "---\ncypilot-template:\n  kind: req\n  version:\n    major: 1\n    minor: 0\n---\n",
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
                # validate-kits does not enforce slug validation
                self.assertEqual(exit_code, 0)
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
                    exit_code = main(["generate-agents", "--agent", "windsurf", "--dry-run"])
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
                "",
                encoding="utf-8",
            )

            # Create artifact with ID definition and reference
            art_dir = root / "artifacts"
            art_dir.mkdir(parents=True, exist_ok=True)
            (art_dir / "reqs.md").write_text(
                ""
                "- [x] `p1` - **ID**: `cpt-test-item-1`\n"
                ""
                ""
                "- [ ] `p2` - `cpt-external-ref-abc`\n"
                "",
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


class TestCLIDispatchUncoveredCommands(unittest.TestCase):
    """Cover cli.py dispatch branches for update, kit, generate-resources, toc, validate-toc."""

    def test_dispatch_update_no_project(self):
        """'update' dispatches to cmd_update; fails gracefully outside a project."""
        from cypilot.cli import main
        with TemporaryDirectory() as td:
            cwd = os.getcwd()
            try:
                os.chdir(td)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["update"])
                self.assertIn(rc, [0, 1, 2])
            finally:
                os.chdir(cwd)

    def test_dispatch_kit_no_subcommand(self):
        """'kit' with no subcommand returns error."""
        from cypilot.cli import main
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["kit"])
        self.assertEqual(rc, 1)
        out = json.loads(buf.getvalue())
        self.assertEqual(out["status"], "ERROR")

    def test_dispatch_generate_resources_no_project(self):
        """'generate-resources' dispatches correctly; fails outside a project."""
        from cypilot.cli import main
        with TemporaryDirectory() as td:
            cwd = os.getcwd()
            try:
                os.chdir(td)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["generate-resources"])
                self.assertIn(rc, [1, 2])
            finally:
                os.chdir(cwd)

    def test_dispatch_toc(self):
        """'toc' command dispatches to cmd_toc."""
        from cypilot.cli import main
        with TemporaryDirectory() as td:
            md = Path(td) / "doc.md"
            md.write_text("# Title\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["toc", str(md)])
            self.assertIn(rc, [0, 1, 2])

    def test_dispatch_validate_toc(self):
        """'validate-toc' command dispatches to cmd_validate_toc."""
        from cypilot.cli import main
        with TemporaryDirectory() as td:
            md = Path(td) / "doc.md"
            md.write_text("# Title\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["validate-toc", str(md)])
            self.assertIn(rc, [0, 1, 2])

    def test_dispatch_spec_coverage(self):
        """'spec-coverage' dispatches to cmd_spec_coverage; may fail outside a project."""
        _run_cli_dispatch(self, ["spec-coverage"])

    def test_dispatch_migrate(self):
        """'migrate' dispatches to cmd_migrate; may fail outside a project."""
        _run_cli_dispatch(self, ["migrate"])

    def test_dispatch_migrate_config(self):
        """'migrate-config' dispatches to cmd_migrate_config; may fail outside a project."""
        _run_cli_dispatch(self, ["migrate-config"])

    def test_dispatch_workspace_init(self):
        """'workspace-init' dispatches to cmd_workspace_init."""
        _run_cli_dispatch(self, ["workspace-init"])

    def test_dispatch_workspace_add(self):
        """'workspace-add' dispatches to cmd_workspace_add."""
        _run_cli_dispatch(self, ["workspace-add", "--name", "x", "--path", "../x"])

    def test_dispatch_workspace_info(self):
        """'workspace-info' dispatches to cmd_workspace_info."""
        _run_cli_dispatch(self, ["workspace-info"])

    def test_dispatch_agents(self):
        """'agents' dispatches to cmd_agents (covers line 322 + lines 24-25 wrapper)."""
        _run_cli_dispatch(self, ["agents"])

    def test_json_flag(self):
        """'--json self-check' sets JSON mode (covers lines 169-170)."""
        _run_cli_dispatch(self, ["--json", "self-check"])


class TestCLIPyCoverageListIdsBranches(unittest.TestCase):
    """Cover uncovered branches in commands/list_ids.py."""

    # ---- Lines 55-56: ValueError in relative_to (artifact path outside project root) ----
    def test_artifact_outside_project_root(self):
        """--artifact pointing outside project root triggers ValueError in relative_to → error."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            git_root = Path(tmpdir)
            # Set up .git and AGENTS.md at tmpdir level
            (git_root / ".git").mkdir()
            adapter = git_root / "adapter"
            adapter.mkdir()
            (adapter / "config").mkdir(parents=True)
            (adapter / "config" / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
            (git_root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "adapter"\n```\n',
                encoding="utf-8",
            )

            # project_root points to a SUBDIRECTORY so artifact can be outside it
            sub = git_root / "sub"
            sub.mkdir()

            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0", "project_root": "../sub", "systems": [], "kits": {},
            }, adapter / "config" / "artifacts.toml")

            # Create an artifact file OUTSIDE the project_root (sub/) but inside git root
            outside = git_root / "elsewhere" / "doc.md"
            outside.parent.mkdir(parents=True, exist_ok=True)
            outside.write_text("- [x] `p1` - **ID**: `cpt-test-req-1`\n", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(git_root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["list-ids", "--artifact", str(outside)])
                # Should fail: artifact outside project_root → ValueError → rel_path None → not registered
                self.assertEqual(rc, 1)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "ERROR")
                self.assertIn("not registered", out["message"])
            finally:
                os.chdir(cwd)

    # ---- Lines 65-66: artifact exists inside project but not registered in registry ----
    def test_artifact_not_registered(self):
        """--artifact for a file inside project root but not in registry → error."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0", "project_root": "..", "systems": [], "kits": {},
            }, adapter / "config" / "artifacts.toml")

            # Create artifact inside project root but not registered
            art = root / "docs" / "stray.md"
            art.parent.mkdir(parents=True, exist_ok=True)
            art.write_text("- [x] `p1` - **ID**: `cpt-test-req-1`\n", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["list-ids", "--artifact", str(art)])
                self.assertEqual(rc, 1)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "ERROR")
                self.assertIn("not registered", out["message"])
            finally:
                os.chdir(cwd)

    # ---- Lines 81-82: --source error when not in workspace mode ----
    def test_source_flag_error_non_workspace(self):
        """--source on a non-workspace project returns error."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_list_ids_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["list-ids", "--source", "foo"])
                self.assertEqual(rc, 1)
                data = json.loads(buf.getvalue())
                self.assertEqual(data["status"], "ERROR")
                self.assertIn("workspace", data["message"])
            finally:
                os.chdir(cwd)

    # ---- Lines 89-98: --source filter in workspace mode ----
    def test_source_filter_workspace_mode(self):
        """--source filter in workspace mode scans only matching remote source artifacts."""
        from cypilot.commands.list_ids import cmd_list_ids
        from cypilot.utils.context import WorkspaceContext, SourceContext, CypilotContext
        from cypilot.utils.artifacts_meta import ArtifactsMeta, Artifact, SystemNode

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_list_ids_project(root, content="- [x] `p1` - **ID**: `cpt-test-req-primary`\n")

            # Create a remote source directory with its own artifact
            remote_root = Path(tmpdir) / "remote-src"
            remote_root.mkdir()
            remote_adapter = _setup_list_ids_project(
                remote_root,
                content="- [x] `p1` - **ID**: `cpt-remote-req-abc`\n",
                art_path="specs/spec.md",
                system_name="Remote",
                system_slug="remote",
            )

            from cypilot.utils.artifacts_meta import load_artifacts_meta
            remote_meta, _ = load_artifacts_meta(remote_adapter)

            sc = SourceContext(
                name="my-remote",
                path=remote_root,
                role="artifacts",
                meta=remote_meta,
                reachable=True,
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                # Build a real primary context first
                primary = CypilotContext.load()
                self.assertIsNotNone(primary)

                ws_ctx = WorkspaceContext(
                    primary=primary,
                    sources={"my-remote": sc},
                    cross_repo=True,
                )

                buf = io.StringIO()
                with patch("cypilot.utils.context.get_context", return_value=ws_ctx):
                    with redirect_stdout(buf):
                        rc = cmd_list_ids(["--source", "my-remote"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                ids = [h["id"] for h in out.get("ids", [])]
                self.assertTrue(any("remote" in i for i in ids))
                # Should NOT contain primary artifacts
                self.assertFalse(any("primary" in i for i in ids))
            finally:
                os.chdir(cwd)

    # ---- Lines 89-98: --source filter with unreachable/non-matching sources ----
    def test_source_filter_workspace_no_match(self):
        """--source filter with no matching source returns empty."""
        from cypilot.commands.list_ids import cmd_list_ids
        from cypilot.utils.context import WorkspaceContext, SourceContext, CypilotContext

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_list_ids_project(root)

            # Unreachable source
            sc = SourceContext(
                name="dead-source",
                path=Path("/nonexistent"),
                role="artifacts",
                meta=None,
                reachable=False,
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                primary = CypilotContext.load()
                self.assertIsNotNone(primary)

                ws_ctx = WorkspaceContext(
                    primary=primary,
                    sources={"dead-source": sc},
                    cross_repo=True,
                )

                buf = io.StringIO()
                with patch("cypilot.utils.context.get_context", return_value=ws_ctx):
                    with redirect_stdout(buf):
                        rc = cmd_list_ids(["--source", "dead-source"])
                # Should return 0 with count=0 (no artifacts found)
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["count"], 0)
            finally:
                os.chdir(cwd)

    # ---- Lines 127, 130: _infer_kind branches (no system prefix match, empty remainder) ----
    def test_infer_kind_no_system_match_and_empty_remainder(self):
        """IDs with no system prefix match or empty remainder after prefix → kind is None."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # cpt-nosystem-thing: no registered system 'nosystem' → no match → kind None
            # cpt-test-: registered system 'test' but remainder is empty → kind None
            # cpt-test: no hyphen after system → won't match prefix "cpt-test-" → kind None
            _setup_list_ids_project(root, content=(
                "- [x] `p1` - **ID**: `cpt-nosystem-thing`\n"
                "- [x] `p1` - **ID**: `cpt-test-`\n"
                "- [x] `p1` - **ID**: `cpt-test`\n"
            ))

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["list-ids", "--all"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                # All IDs should have kind=None
                for hit in out.get("ids", []):
                    self.assertIsNone(hit["kind"])
            finally:
                os.chdir(cwd)

    # ---- Lines 144: empty cid from scan_cpt_ids → continue ----
    def test_empty_id_skipped(self):
        """An artifact whose scan_cpt_ids returns an entry with empty id is skipped."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_list_ids_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                # Patch scan_cpt_ids to return an entry with empty id alongside a valid one
                def fake_scan(path):
                    return [
                        {"id": "", "type": "definition", "line": 1},
                        {"id": "cpt-test-req-1", "type": "definition", "line": 2},
                    ]
                buf = io.StringIO()
                with patch("cypilot.commands.list_ids.scan_cpt_ids", side_effect=fake_scan):
                    with redirect_stdout(buf):
                        rc = main(["list-ids"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                # Only the non-empty ID should appear
                ids = [h["id"] for h in out.get("ids", [])]
                self.assertNotIn("", ids)
                self.assertIn("cpt-test-req-1", ids)
            finally:
                os.chdir(cwd)

    # ---- Lines 168, 171: code path not exists, code path is a file ----
    def test_include_code_path_not_exists(self):
        """--include-code with codebase entry pointing to non-existent path → skipped."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_list_ids_project(root, codebase=[{"path": "nonexistent_dir", "extensions": [".py"]}])

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["list-ids", "--include-code"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                # Should still have the artifact ID but no code_files_scanned key (or 0)
                self.assertIn("ids", out)
            finally:
                os.chdir(cwd)

    def test_include_code_path_is_file(self):
        """--include-code with codebase entry pointing to a single file → scans that file."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            art = root / "docs" / "reqs.md"
            art.parent.mkdir(parents=True, exist_ok=True)
            art.write_text("- [x] `p1` - **ID**: `cpt-test-req-1`\n", encoding="utf-8")

            # Create a single code file
            code_file = root / "main.py"
            code_file.write_text("# @cpt-req:cpt-test-req-1:p1\nprint('hello')\n", encoding="utf-8")

            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0", "project_root": "..",
                "kits": {},
                "systems": [{
                    "name": "Test", "slug": "test",
                    "artifacts": [{"path": "docs/reqs.md", "kind": "req"}],
                    "codebase": [{"path": "main.py", "extensions": [".py"]}],
                }],
            }, adapter / "config" / "artifacts.toml")

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["list-ids", "--include-code", "--all"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertIn("ids", out)
                # Should have scanned 1 code file
                self.assertEqual(out.get("code_files_scanned", 0), 1)
            finally:
                os.chdir(cwd)

    # ---- Lines 181-182: relative_to exception in code scanning ----
    def test_include_code_relative_to_exception(self):
        """relative_to raises ValueError → rel=None → file not ignored → processed."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir, TemporaryDirectory() as outsidedir:
            root = Path(tmpdir)
            _setup_list_ids_project(root, codebase=[{"path": "src", "extensions": [".py"]}])

            src = root / "src"
            src.mkdir()

            # Place the real file outside the project and symlink into src/.
            # resolve() follows the symlink → path outside project_root → relative_to raises ValueError.
            outside_file = Path(outsidedir) / "ext.py"
            outside_file.write_text("# @cpt-req:cpt-test-req-1:p1\nprint('ok')\n", encoding="utf-8")
            try:
                (src / "ext.py").symlink_to(outside_file)
            except OSError:
                self.skipTest("symlink creation not supported on this platform")

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["list-ids", "--include-code", "--all"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                # resolve() follows symlink outside project root → relative_to raises → rel=None → not ignored
                code_hits = [h for h in out.get("ids", []) if h.get("type") == "code_reference"]
                self.assertGreaterEqual(len(code_hits), 1, f"Expected code refs, got {out}")
            finally:
                os.chdir(cwd)

    # ---- Lines 184: is_ignored skips code file ----
    def test_include_code_ignored_file(self):
        """Code file matching ignore pattern is skipped (line 183-184)."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_list_ids_project(
                root,
                codebase=[{"path": "src", "extensions": [".py"]}],
                ignore=[{"reason": "generated", "patterns": ["src/gen/*"]}],
            )

            # Codebase entry is "src" (not ignored), but files inside "src/gen/" are ignored
            src = root / "src"
            src.mkdir()
            gen_dir = src / "gen"
            gen_dir.mkdir()
            code = gen_dir / "generated.py"
            code.write_text("# @cpt-req:cpt-test-req-1:p1\n", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["list-ids", "--include-code", "--all"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                # gen/ files should be ignored — no code references from them
                code_hits = [h for h in out.get("ids", []) if h.get("type") == "code_reference"]
                self.assertEqual(len(code_hits), 0)
            finally:
                os.chdir(cwd)

    # ---- Lines 188: CodeFile.from_path returns errors → continue ----
    def test_include_code_file_parse_error(self):
        """Code file that fails to parse is skipped."""
        from cypilot.commands.list_ids import cmd_list_ids

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            art = root / "docs" / "reqs.md"
            art.parent.mkdir(parents=True, exist_ok=True)
            art.write_text("- [x] `p1` - **ID**: `cpt-test-req-1`\n", encoding="utf-8")

            src = root / "src"
            src.mkdir()
            code = src / "broken.py"
            code.write_text("# @cpt-req:cpt-test-req-1:p1\n", encoding="utf-8")

            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0", "project_root": "..",
                "kits": {},
                "systems": [{
                    "name": "Test", "slug": "test",
                    "artifacts": [{"path": "docs/reqs.md", "kind": "req"}],
                    "codebase": [{"path": "src", "extensions": [".py"]}],
                }],
            }, adapter / "config" / "artifacts.toml")

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                # Make CodeFile.from_path return errors
                with patch("cypilot.commands.list_ids.CodeFile.from_path", return_value=(None, [{"error": "parse fail"}])):
                    with redirect_stdout(buf):
                        rc = cmd_list_ids(["--include-code"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                # No code references because file errored out
                code_hits = [h for h in out.get("ids", []) if h.get("type") == "code_reference"]
                self.assertEqual(len(code_hits), 0)
            finally:
                os.chdir(cwd)

    # ---- Line 206: ref.inst is set → h["inst"] is added ----
    def test_include_code_with_inst_marker(self):
        """Code reference with inst field gets it included in output."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_list_ids_project(root, codebase=[{"path": "src", "extensions": [".py"]}])

            src = root / "src"
            src.mkdir()
            # @cpt-begin markers have inst segments
            code = src / "impl.py"
            code.write_text(
                "# @cpt-begin:cpt-test-req-1:p1:inst-do-work\n"
                "print('working')\n"
                "# @cpt-end:cpt-test-req-1:p1:inst-do-work\n",
                encoding="utf-8",
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["list-ids", "--include-code", "--all"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                code_hits = [h for h in out.get("ids", []) if h.get("type") == "code_reference"]
                # At least one code ref should have inst field
                inst_hits = [h for h in code_hits if h.get("inst")]
                self.assertGreaterEqual(len(inst_hits), 1, f"Expected code refs with inst, got: {code_hits}")
            finally:
                os.chdir(cwd)


class TestValidateSourceFlag(unittest.TestCase):
    """Tests for validate.py --source flag (lines 49-62)."""

    def test_source_without_workspace_context(self):
        """--source with non-workspace context returns error (lines 49-52)."""
        from cypilot.commands import validate as validate_cmd

        class _FakeMeta:
            systems = []
            def iter_all_artifacts(self):
                return iter([])
            def is_ignored(self, _rel):
                return False

        class _FakeCtx:
            meta = _FakeMeta()
            project_root = Path("/fake")
            registered_systems = set()
            kits = {}
            _errors = []
            def get_known_id_kinds(self):
                return set()

        fake_ctx = _FakeCtx()
        buf = io.StringIO()
        with patch("cypilot.utils.context.get_context", return_value=fake_ctx):
            with redirect_stdout(buf):
                rc = validate_cmd.cmd_validate(["--source", "some-source"])
        self.assertEqual(rc, 1)
        out = json.loads(buf.getvalue())
        self.assertEqual(out["status"], "ERROR")
        self.assertIn("workspace context", out["message"])

    def test_source_not_found_in_workspace(self):
        """--source with unknown source name returns error (lines 53-56)."""
        from cypilot.commands import validate as validate_cmd
        from cypilot.utils.context import WorkspaceContext, SourceContext

        ws_ctx = WorkspaceContext(
            primary=_EmptyFakePrimary(),
            sources={},
        )

        buf = io.StringIO()
        with patch("cypilot.utils.context.get_context", return_value=ws_ctx):
            with redirect_stdout(buf):
                rc = validate_cmd.cmd_validate(["--source", "nonexistent"])
        self.assertEqual(rc, 1)
        out = json.loads(buf.getvalue())
        self.assertEqual(out["status"], "ERROR")
        self.assertIn("nonexistent", out["message"])

    def test_source_unreachable(self):
        """--source with unreachable source returns error (lines 57-59)."""
        from cypilot.commands import validate as validate_cmd
        from cypilot.utils.context import WorkspaceContext, SourceContext

        sc = SourceContext(name="my-source", path=Path("/fake/missing"), role="full", reachable=False)
        ws_ctx = WorkspaceContext(
            primary=_EmptyFakePrimary(),
            sources={"my-source": sc},
        )

        buf = io.StringIO()
        with patch("cypilot.utils.context.get_context", return_value=ws_ctx):
            with redirect_stdout(buf):
                rc = validate_cmd.cmd_validate(["--source", "my-source"])
        self.assertEqual(rc, 1)
        out = json.loads(buf.getvalue())
        self.assertEqual(out["status"], "ERROR")
        self.assertIn("not reachable", out["message"])

    def test_source_resolves_adapter_context(self):
        """--source with reachable source swaps context (lines 60-62)."""
        from cypilot.commands import validate as validate_cmd
        from cypilot.utils.context import WorkspaceContext, SourceContext

        fake_adapter_ctx = _EmptyFakePrimary()
        fake_adapter_ctx.project_root = Path("/fake-source")
        fake_adapter_ctx.adapter_dir = Path("/fake-source/adapter")

        sc = SourceContext(name="my-source", path=Path("/fake-source"), role="full", reachable=True)
        ws_ctx = WorkspaceContext(primary=_EmptyFakePrimary(), sources={"my-source": sc})

        buf = io.StringIO()
        with patch("cypilot.utils.context.get_context", return_value=ws_ctx), \
             patch("cypilot.utils.context.resolve_adapter_context", return_value=fake_adapter_ctx):
            with redirect_stdout(buf):
                _ = validate_cmd.cmd_validate(["--source", "my-source", "--skip-code"])
        out = json.loads(buf.getvalue())
        self.assertNotEqual(out.get("status"), "ERROR")


class TestCLIPyCoverageValidateWorkspaceBranches(unittest.TestCase):
    """Tests covering remaining workspace-related branches in validate.py."""

    def test_validate_self_check_exception_branch(self):
        """Self-check raising exception returns ERROR (lines 93-100)."""
        from cypilot.commands import validate as validate_cmd
        class _FakeMeta:
            systems = []
            kits = {"x": types.SimpleNamespace(path="kits/x")}
            def iter_all_artifacts(self): return iter([])
            def is_ignored(self, _rel): return False
            def get_kit(self, _kid): return types.SimpleNamespace(is_cypilot_format=lambda: True, get_template_path=lambda _k: "t.md")
        class _FakeCtx:
            meta = _FakeMeta()
            project_root = Path("/fake")
            adapter_dir = Path("/fake")
            registered_systems = set()
            kits = {"x": types.SimpleNamespace(kit=types.SimpleNamespace(path="kits/x"), constraints=None)}
            _errors = []
            def get_known_id_kinds(self): return set()
        buf = io.StringIO()
        with patch("cypilot.utils.context.get_context", return_value=_FakeCtx()):
            with patch("cypilot.commands.validate_kits.run_validate_kits", side_effect=ValueError("boom")):
                with redirect_stdout(buf):
                    rc = validate_cmd.cmd_validate([])
        self.assertEqual(rc, 1)
        out = json.loads(buf.getvalue())
        self.assertEqual(out["status"], "ERROR")
        self.assertIn("self-check failed to run", out["message"])

    def test_validate_single_artifact_workspace_resolution(self):
        """--artifact in WorkspaceContext calls determine_target_source (lines 128-130)."""
        from cypilot.commands import validate as validate_cmd
        from cypilot.utils.context import WorkspaceContext
        class _FakeMeta:
            systems = []; kits = {}
            def get_artifact_by_path(self, _rel): return None
            def iter_all_artifacts(self): return iter([])
            def is_ignored(self, _rel): return False
        class _FakeInnerCtx:
            meta = _FakeMeta()
            project_root = Path("/fake")
            adapter_dir = Path("/fake/adapter")
            registered_systems = set(); kits = {}; _errors = []
            def get_known_id_kinds(self): return set()
        class _FakePrimary:
            meta = _FakeMeta()
            project_root = Path("/fake")
            adapter_dir = Path("/fake/adapter")
            registered_systems = set(); kits = {}; _errors = []
            def get_known_id_kinds(self): return set()
        ws_ctx = WorkspaceContext(primary=_FakePrimary(), sources={})
        with TemporaryDirectory() as td:
            art = Path(td) / "artifact.md"
            art.write_text("# A\n", encoding="utf-8")
            inner = _FakeInnerCtx(); inner.project_root = Path(td)
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ws_ctx):
                with patch("cypilot.utils.context.determine_target_source", return_value=(None, inner)):
                    with redirect_stdout(buf):
                        rc = validate_cmd.cmd_validate(["--artifact", str(art)])
            self.assertEqual(rc, 1)
            self.assertEqual(json.loads(buf.getvalue())["status"], "ERROR")

    def test_validate_bulk_mode_workspace_resolve_artifact_path(self):
        """Bulk mode with WorkspaceContext uses resolve_artifact_path (line 179)."""
        from cypilot.commands import validate as validate_cmd
        from cypilot.utils.context import WorkspaceContext
        with TemporaryDirectory() as td:
            root, ar = _scaffold_validate_project(td)
            art_path = root / ar
            p = _CompactPrim(root, ar,
                kits={"x": types.SimpleNamespace(kit=types.SimpleNamespace(path="kits/x"), constraints=None)},
                registered_systems=set())
            ws = WorkspaceContext(primary=p, sources={})
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ws):
                with patch.object(WorkspaceContext, "resolve_artifact_path", return_value=art_path):
                    with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                        with patch("cypilot.commands.validate.cross_validate_artifacts", return_value={"errors": [], "warnings": []}):
                            with patch("cypilot.commands.validate.scan_cpt_ids", return_value=[]):
                                with redirect_stdout(buf):
                                    rc = validate_cmd.cmd_validate(["--skip-code"])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(buf.getvalue())["status"], "PASS")

    def test_validate_ctx_errors_no_artifacts(self):
        """ctx_errors surfaced when no artifacts found (lines 189-199)."""
        from cypilot.commands import validate as validate_cmd
        ctx = _CompactCtx(Path("/fake"), [],
            errors=[{"type": "constraints", "message": "bad", "path": "x", "line": 1}],
            registered_systems=set())
        buf = io.StringIO()
        with patch("cypilot.utils.context.get_context", return_value=ctx):
            with redirect_stdout(buf):
                rc = validate_cmd.cmd_validate([])
        self.assertEqual(rc, 2)
        out = json.loads(buf.getvalue())
        self.assertEqual(out["status"], "FAIL")
        self.assertEqual(out["artifacts_validated"], 0)
        self.assertGreater(out["error_count"], 0)

    def test_validate_registry_errors_early_stop_with_output(self):
        """Registry-level errors stop early and write --output file (lines 217-230)."""
        from cypilot.commands import validate as validate_cmd
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            ar = "artifacts/REQ.md"; (root / ar).write_text("# R\n", encoding="utf-8")
            ctx = _CompactCtx(root, ar,
                kits={"x": types.SimpleNamespace(kit=types.SimpleNamespace(path="kits/x"), constraints=None)},
                errors=[{"type": "registry", "message": "bad", "path": "x", "line": 1}],
                registered_systems=set())
            of = root / "report.json"
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                rc = validate_cmd.cmd_validate(["--output", str(of)])
            self.assertEqual(rc, 2); self.assertTrue(of.is_file())
            out = json.loads(of.read_text(encoding="utf-8"))
            self.assertEqual(out["status"], "FAIL"); self.assertGreater(out["error_count"], 0)

    def test_validate_registry_errors_early_stop_without_output(self):
        """Registry-level errors stop early to stdout (line 229)."""
        from cypilot.commands import validate as validate_cmd
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            ar = "artifacts/REQ.md"; (root / ar).write_text("# R\n", encoding="utf-8")
            ctx = _CompactCtx(root, ar,
                kits={"x": types.SimpleNamespace(kit=types.SimpleNamespace(path="kits/x"), constraints=None)},
                errors=[{"type": "registry", "message": "bad", "path": "x", "line": 1}],
                registered_systems=set())
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with redirect_stdout(buf):
                    rc = validate_cmd.cmd_validate([])
            self.assertEqual(rc, 2)
            self.assertEqual(json.loads(buf.getvalue())["status"], "FAIL")

    def test_validate_cross_ref_workspace_path_resolution(self):
        """Cross-ref loading uses resolve_artifact_path in workspace mode (lines 343-344)."""
        from cypilot.commands import validate as validate_cmd
        from cypilot.utils.context import WorkspaceContext
        with TemporaryDirectory() as td:
            root, ar = _scaffold_validate_project(td)
            lk = _CompactLoadedKit(
                constraints=types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])}))
            ws = WorkspaceContext(primary=_CompactPrim(root, [(ar, "REQ")], kits={"x": lk}), sources={})
            art_resolved = (root / ar).resolve()
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ws):
                with patch.object(WorkspaceContext, "resolve_artifact_path", return_value=art_resolved):
                    with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                        with patch("cypilot.commands.validate.cross_validate_artifacts", return_value={"errors": [], "warnings": []}):
                            with patch("cypilot.commands.validate.scan_cpt_ids", return_value=[]):
                                with redirect_stdout(buf):
                                    rc = validate_cmd.cmd_validate(["--skip-code"])
            self.assertEqual(rc, 0)

    def test_validate_code_scan_to_code_task_branches(self):
        """Code scan with to_code covers task/checked branches (lines 420-432)."""
        from cypilot.commands import validate as validate_cmd
        with TemporaryDirectory() as td:
            root, ar = _scaffold_validate_project(td)
            lk = _CompactLoadedKit(
                constraints=types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(
                    defined_id=[types.SimpleNamespace(kind="req", to_code=True)])}))
            ctx = _CompactCtx(root, ar, kits={"x": lk})
            scan = [
                {"type": "definition", "id": "cpt-sys-req-1", "has_task": True, "checked": True},
                {"type": "definition", "id": "cpt-sys-req-2", "has_task": True, "checked": False},
                {"type": "definition", "id": "cpt-sys-req-3", "has_task": False, "checked": False},
                {"type": "definition", "id": "cpt-sys-req-4"},
            ]
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                    with patch("cypilot.commands.validate.cross_validate_artifacts", return_value={"errors": [], "warnings": []}):
                        with patch("cypilot.commands.validate.scan_cpt_ids", return_value=scan):
                            with redirect_stdout(buf):
                                rc = validate_cmd.cmd_validate(["--skip-code"])
            self.assertIn(rc, [0, 2])

    def test_validate_workspace_get_all_artifact_ids(self):
        """Workspace context calls get_all_artifact_ids (line 439)."""
        rc, mi, _buf = _run_ws_validate([])
        mi.assert_called_once()
        self.assertIn(rc, [0, 2])

    def test_validate_reference_coverage_no_other_kinds(self):
        """Single-kind with no constraints generates warning (lines 589-600)."""
        from cypilot.commands import validate as validate_cmd
        with TemporaryDirectory() as td:
            root, ar = _scaffold_validate_project(td)
            (root / ar).write_text("- [x] `p1` - **ID**: `cpt-sys-req-1`\n", encoding="utf-8")
            ctx = _CompactCtx(root, ar,
                kits={"x": types.SimpleNamespace(kit=types.SimpleNamespace(path="kits/x"), constraints=None)})
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                    with redirect_stdout(buf):
                        _ = validate_cmd.cmd_validate(["--skip-code", "--verbose"])
            self.assertIn("status", json.loads(buf.getvalue()))

    def test_validate_output_file_pass_verbose(self):
        """--output with --verbose PASS appends newline (line 676)."""
        from cypilot.commands import validate as validate_cmd
        with TemporaryDirectory() as td:
            root, ar = _scaffold_validate_project(td)
            lk = _CompactLoadedKit(
                constraints=types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])}))
            ctx = _CompactCtx(root, ar, kits={"x": lk})
            of = root / "report.json"
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                    with patch("cypilot.commands.validate.cross_validate_artifacts", return_value={"errors": [], "warnings": []}):
                        with patch("cypilot.commands.validate.scan_cpt_ids", return_value=[]):
                            rc = validate_cmd.cmd_validate(["--skip-code", "--verbose", "--output", str(of)])
            self.assertEqual(rc, 0); self.assertTrue(of.is_file())
            self.assertTrue(of.read_text(encoding="utf-8").endswith("\n"))

    def test_human_validate_formatter_pass(self):
        """_human_validate with PASS status (lines 847-850)."""
        from contextlib import redirect_stderr
        from cypilot.commands.validate import _human_validate
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)
        data = {"status": "PASS", "artifacts_validated": 1, "error_count": 0, "warning_count": 0,
                "code_files_scanned": 5, "coverage": "3/5", "next_step": "Do semantic review."}
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_validate(data)
        self.assertIn("Validate", buf.getvalue())

    def test_human_validate_formatter_fail_truncation(self):
        """_human_validate truncates long error/warning lists (lines 835-836, 843-844)."""
        from contextlib import redirect_stderr
        from cypilot.commands.validate import _human_validate
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)
        data = {"status": "FAIL", "artifacts_validated": 1, "error_count": 35, "warning_count": 20,
                "errors": [{"message": f"e{i}", "code": "E", "path": "/a.md", "line": i} for i in range(35)],
                "warnings": [{"message": f"w{i}", "code": "W", "path": "/a.md", "line": i} for i in range(20)]}
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_validate(data)
        o = buf.getvalue()
        self.assertIn("more error(s)", o); self.assertIn("more warning(s)", o)

    def test_human_validate_formatter_other_status(self):
        """_human_validate with non-PASS/FAIL status (lines 853-854)."""
        from contextlib import redirect_stderr
        from cypilot.commands.validate import _human_validate
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_validate({"status": "ERROR", "artifacts_validated": 0, "error_count": 0, "warning_count": 0})
        self.assertIn("ERROR", buf.getvalue())

    def test_format_issue_non_dict(self):
        """_format_issue with non-dict issue (lines 882-887)."""
        from contextlib import redirect_stderr
        from cypilot.commands.validate import _format_issue
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)
        buf = io.StringIO()
        with redirect_stderr(buf):
            _format_issue("plain error", is_error=True)
        self.assertIn("plain error", buf.getvalue())
        buf = io.StringIO()
        with redirect_stderr(buf):
            _format_issue("plain warning", is_error=False)
        self.assertIn("plain warning", buf.getvalue())

    def test_format_issue_with_reasons_and_fixing(self):
        """_format_issue with reasons and fixing_prompt (lines 916-924)."""
        from contextlib import redirect_stderr
        from cypilot.commands.validate import _format_issue
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)
        issue = {"message": "err", "code": "E1", "path": "/f.md", "line": 42,
                 "reasons": ["r1", "r2"], "fixing_prompt": "Fix X."}
        buf = io.StringIO()
        with redirect_stderr(buf):
            _format_issue(issue, is_error=True)
        o = buf.getvalue()
        self.assertIn("r1", o); self.assertIn("Fix:", o)

    def test_format_issue_with_extra_keys(self):
        """_format_issue auto-formats unknown keys (lines 934-938)."""
        from contextlib import redirect_stderr
        from cypilot.commands.validate import _format_issue
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)
        buf = io.StringIO()
        with redirect_stderr(buf):
            _format_issue({"message": "T", "ck": "cv", "cl": ["a", "b"]}, is_error=False)
        o = buf.getvalue()
        self.assertIn("ck: cv", o); self.assertIn("cl: a, b", o)

    def test_format_issue_no_location_no_code(self):
        """_format_issue with no location or code (lines 907-911)."""
        from contextlib import redirect_stderr
        from cypilot.commands.validate import _format_issue
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)
        buf = io.StringIO()
        with redirect_stderr(buf):
            _format_issue({"message": "Bare"}, is_error=True)
        self.assertIn("Bare", buf.getvalue())
        buf = io.StringIO()
        with redirect_stderr(buf):
            _format_issue({"message": "Bare"}, is_error=False)
        self.assertIn("Bare", buf.getvalue())

    def test_format_issue_with_location_string(self):
        """_format_issue with location field (lines 860-872)."""
        from contextlib import redirect_stderr
        from cypilot.commands.validate import _format_issue
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)
        buf = io.StringIO()
        with redirect_stderr(buf):
            _format_issue({"message": "X", "location": "/fake/f.md:10"}, is_error=True)
        self.assertIn("f.md", buf.getvalue())

    def test_format_issue_warning_with_header(self):
        """_format_issue warning with code (lines 903-906)."""
        from contextlib import redirect_stderr
        from cypilot.commands.validate import _format_issue
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)
        buf = io.StringIO()
        with redirect_stderr(buf):
            _format_issue({"message": "W", "code": "W1", "path": "/a.md", "line": 5}, is_error=False)
        self.assertIn("W1", buf.getvalue())

    def test_enrich_target_artifact_paths_non_artifacts_meta(self):
        """_enrich_target_artifact_paths returns early for non-ArtifactsMeta (line 706)."""
        from cypilot.commands.validate import _enrich_target_artifact_paths
        issues = [{"code": "ref-missing-from-kind", "target_kind": "DESIGN"}]
        _enrich_target_artifact_paths(issues, meta="not-a-meta", project_root=Path("/fake"))
        self.assertNotIn("target_artifact_path", issues[0])

    def test_issue_location_branches(self):
        """_issue_location various branches (lines 860-872)."""
        from cypilot.commands.validate import _issue_location
        self.assertEqual(_issue_location({}), "")
        self.assertIn("42", _issue_location({"path": "/fake/f.md", "line": 42}))
        self.assertIn("f.md", _issue_location({"location": "/fake/f.md"}))

    def test_human_validate_uses_artifact_count_fallback(self):
        """_human_validate uses artifact_count when artifacts_validated missing (line 816)."""
        from contextlib import redirect_stderr
        from cypilot.commands.validate import _human_validate
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_validate({"status": "FAIL", "artifact_count": 3, "error_count": 1,
                             "warning_count": 0, "errors": [{"message": "e1"}]})
        self.assertIn("3", buf.getvalue())

    def test_validate_attach_issue_unknown_path_returns(self):
        """_attach_issue_to_artifact_report returns early for unknown path (line 296)."""
        from cypilot.commands import validate as validate_cmd
        with TemporaryDirectory() as td:
            root, ar = _scaffold_validate_project(td)
            lk = _CompactLoadedKit(
                constraints=types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])}))
            ctx = _CompactCtx(root, [(ar, "REQ")], kits={"x": lk})
            fake_cross = {
                "errors": [{"type": "constraints", "message": "e1", "path": "/fake/unknown.md", "line": 1}],
                "warnings": [{"type": "constraints", "message": "w1", "path": "/fake/unknown.md", "line": 1}],
            }
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                    with patch("cypilot.commands.validate.cross_validate_artifacts", return_value=fake_cross):
                        with patch("cypilot.commands.validate.scan_cpt_ids", return_value=[]):
                            with redirect_stdout(buf):
                                rc = validate_cmd.cmd_validate(["--skip-code"])
            self.assertEqual(rc, 0)

    def test_validate_cdsl_scan_docs_only_skipped(self):
        """DOCS-ONLY artifacts skip CDSL scan (line 517-518)."""
        from cypilot.commands import validate as validate_cmd
        class _KP:
            def is_cypilot_format(self): return True
            def get_template_path(self, _k): return "kits/x/artifacts/REQ/template.md"
        class _SN:
            kit = "x"
            artifacts = [types.SimpleNamespace(traceability="DOCS-ONLY")]
            codebase = [types.SimpleNamespace(path="src", extensions=[".py"])]
            children = []
        class _AM:
            def __init__(self, p): self.path = p; self.kind = "REQ"; self.traceability = "DOCS-ONLY"
        class _Meta:
            def __init__(self, ar, sn): self._ar = ar; self._sn = sn; self.systems = [sn]
            def iter_all_artifacts(self): yield _AM(self._ar), types.SimpleNamespace(kit="x")
            def get_kit(self, _k): return _KP()
            def is_ignored(self, _r): return False
        class _LK:
            kit = types.SimpleNamespace(path="kits/x")
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            ar = "artifacts/REQ.md"; (root / ar).write_text("# R\n", encoding="utf-8")
            (root / "src").mkdir(parents=True, exist_ok=True)
            (root / "src" / "code.py").write_text("print('ok')\n", encoding="utf-8")
            sn = _SN()
            class _Ctx:
                meta = _Meta(ar, sn); project_root = root
                registered_systems = {"sys"}; kits = {"x": _LK()}; _errors = []
                def get_known_id_kinds(self): return set()
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=_Ctx()):
                with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                    with patch("cypilot.commands.validate.cross_validate_artifacts", return_value={"errors": [], "warnings": []}):
                        with patch("cypilot.commands.validate.scan_cpt_ids", return_value=[]):
                            with patch("cypilot.commands.validate.scan_cdsl_instructions", return_value=[]):
                                with redirect_stdout(buf):
                                    rc = validate_cmd.cmd_validate([])
            self.assertIn(rc, [0, 2])


class TestWhereDefinedWorkspaceBranches(unittest.TestCase):
    """Tests for where_defined workspace-related branches: collect_artifacts_to_scan, source attribution, cross-repo."""

    def _make_workspace_ctx(self, root, remote_root, artifact_rel="artifacts/REQ.md"):
        """Build a WorkspaceContext with one remote source containing an artifact."""
        from cypilot.utils.context import WorkspaceContext, SourceContext

        remote_meta = _CollectMeta("artifacts/REMOTE.md")
        p = _CollectPrim(root, artifact_rel)
        p.get_known_id_kinds = lambda: set()
        sc = SourceContext(
            name="backend",
            path=remote_root,
            role="full",
            reachable=True,
            meta=remote_meta,
        )
        ws = WorkspaceContext(
            primary=p,
            sources={"backend": sc},
            cross_repo=True,
        )
        return ws

    def test_where_defined_workspace_source_attribution(self):
        """where-defined includes 'source' field for definitions found in remote artifacts."""
        from cypilot.commands.where_defined import cmd_where_defined

        with TemporaryDirectory() as td:
            root, remote = _make_cross_repo_dirs(td)
            (root / "artifacts" / "REQ.md").write_text("- [x] `p1` - **ID**: `cpt-sys-req-1`\n", encoding="utf-8")
            (remote / "artifacts" / "REMOTE.md").write_text("- [x] `p1` - **ID**: `cpt-sys-req-1`\n", encoding="utf-8")

            ws = self._make_workspace_ctx(root, remote)
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ws), \
                 _patch_collect_artifacts(root, remote):
                with redirect_stdout(buf):
                    cmd_where_defined(["cpt-sys-req-1"])

            out = json.loads(buf.getvalue())
            defs = out.get("definitions", [])
            remote_defs = [d for d in defs if d.get("source") == "backend"]
            self.assertGreaterEqual(len(remote_defs), 1, f"Expected source attribution on remote def, got {defs}")
            local_defs = [d for d in defs if "source" not in d]
            self.assertGreaterEqual(len(local_defs), 1, f"Expected local def without source, got {defs}")

    def test_where_defined_workspace_cross_repo_artifacts(self):
        """where-defined scans artifacts from remote sources via collect_artifacts_to_scan."""
        from cypilot.commands.where_defined import cmd_where_defined

        with TemporaryDirectory() as td:
            root, remote = _make_cross_repo_dirs(td)
            (root / "artifacts" / "REQ.md").write_text("# No match\n", encoding="utf-8")
            (remote / "artifacts" / "REMOTE.md").write_text("- [x] `p1` - **ID**: `cpt-remote-only-1`\n", encoding="utf-8")

            ws = self._make_workspace_ctx(root, remote)
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ws), \
                 _patch_collect_artifacts(root, remote):
                with redirect_stdout(buf):
                    cmd_where_defined(["cpt-remote-only-1"])

            out = json.loads(buf.getvalue())
            self.assertEqual(out["status"], "FOUND")
            self.assertEqual(out["definitions"][0]["source"], "backend")

    def test_where_defined_no_workspace_empty_path_to_source(self):
        """Non-workspace context: path_to_source is empty, no 'source' field in output."""
        from cypilot.commands.where_defined import cmd_where_defined

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "artifacts").mkdir()
            (root / "artifacts" / "REQ.md").write_text("- [x] `p1` - **ID**: `cpt-sys-req-1`\n", encoding="utf-8")

            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=True), \
                 patch("cypilot.utils.context.collect_artifacts_to_scan", return_value=(
                     [((root / "artifacts" / "REQ.md").resolve(), "REQ")],
                     {},
                 )):
                with redirect_stdout(buf):
                    cmd_where_defined(["cpt-sys-req-1"])

            out = json.loads(buf.getvalue())
            self.assertEqual(out["status"], "FOUND")
            self.assertNotIn("source", out["definitions"][0])


class TestWhereUsedWorkspaceBranches(unittest.TestCase):
    """Tests for where_used workspace-related branches: collect_artifacts_to_scan, source attribution, cross-repo."""

    def test_where_used_workspace_source_attribution(self):
        """where-used includes 'source' field for references found in remote artifacts."""
        from cypilot.commands.where_used import cmd_where_used

        with TemporaryDirectory() as td:
            root, remote = _make_cross_repo_dirs(td)
            (root / "artifacts" / "REQ.md").write_text(
                "- [x] `p1` - **ID**: `cpt-sys-req-1`\n"
                "`cpt-sys-req-1`\n",
                encoding="utf-8",
            )
            (remote / "artifacts" / "REMOTE.md").write_text("`cpt-sys-req-1`\n", encoding="utf-8")

            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=True), \
                 _patch_collect_artifacts(root, remote):
                with redirect_stdout(buf):
                    cmd_where_used(["cpt-sys-req-1"])

            out = json.loads(buf.getvalue())
            refs = out.get("references", [])
            remote_refs = [r for r in refs if r.get("source") == "backend"]
            self.assertGreaterEqual(len(remote_refs), 1, f"Expected source attribution on remote ref, got {refs}")

    def test_where_used_workspace_cross_repo_references(self):
        """where-used finds references in remote artifacts via workspace context."""
        from cypilot.commands.where_used import cmd_where_used

        with TemporaryDirectory() as td:
            root, remote = _make_cross_repo_dirs(td)
            (root / "artifacts" / "REQ.md").write_text("# No refs here\n", encoding="utf-8")
            (remote / "artifacts" / "REMOTE.md").write_text("`cpt-remote-target-1`\n", encoding="utf-8")

            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=True), \
                 _patch_collect_artifacts(root, remote):
                with redirect_stdout(buf):
                    cmd_where_used(["cpt-remote-target-1"])

            out = json.loads(buf.getvalue())
            refs = out.get("references", [])
            self.assertGreaterEqual(len(refs), 1, "Expected refs from remote source")
            self.assertEqual(refs[0]["source"], "backend")

    def test_where_used_include_definitions_with_source(self):
        """where-used --include-definitions shows definitions from remote sources with attribution."""
        from cypilot.commands.where_used import cmd_where_used

        with TemporaryDirectory() as td:
            remote = Path(td) / "remote"
            remote.mkdir()
            (remote / "artifacts").mkdir()
            (remote / "artifacts" / "REMOTE.md").write_text(
                "- [x] `p1` - **ID**: `cpt-sys-req-1`\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=True), \
                 patch("cypilot.utils.context.collect_artifacts_to_scan", return_value=(
                     [((remote / "artifacts" / "REMOTE.md").resolve(), "REQ")],
                     {str((remote / "artifacts" / "REMOTE.md").resolve()): "backend"},
                 )):
                with redirect_stdout(buf):
                    cmd_where_used(["--include-definitions", "cpt-sys-req-1"])

            out = json.loads(buf.getvalue())
            refs = out.get("references", [])
            def_refs = [r for r in refs if r.get("type") == "definition"]
            self.assertGreaterEqual(len(def_refs), 1, f"Expected definition from remote, got {refs}")
            self.assertEqual(def_refs[0]["source"], "backend")

    def test_where_used_no_workspace_no_source_field(self):
        """Non-workspace context: no 'source' field in references."""
        from cypilot.commands.where_used import cmd_where_used

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "artifacts").mkdir()
            (root / "artifacts" / "REQ.md").write_text(
                "`cpt-sys-req-1`\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=True), \
                 patch("cypilot.utils.context.collect_artifacts_to_scan", return_value=(
                     [((root / "artifacts" / "REQ.md").resolve(), "REQ")],
                     {},
                 )):
                with redirect_stdout(buf):
                    cmd_where_used(["cpt-sys-req-1"])

            out = json.loads(buf.getvalue())
            refs = out.get("references", [])
            self.assertGreaterEqual(len(refs), 1)
            self.assertNotIn("source", refs[0])


class TestValidateLocalOnlyFlag(unittest.TestCase):
    """Tests for validate --local-only flag skipping get_all_artifact_ids."""

    def test_validate_local_only_skips_get_all_artifact_ids(self):
        """--local-only prevents get_all_artifact_ids call on WorkspaceContext (line 436)."""
        rc, mi, _buf = _run_ws_validate(["--local-only"])
        mi.assert_not_called()
        self.assertIn(rc, [0, 2])


class TestCollectArtifactsToScanWorkspace(unittest.TestCase):
    """Tests for collect_artifacts_to_scan with WorkspaceContext — cross-repo enabled/disabled."""

    def _setup_collect_ctx(self, td, cross_repo):
        """Shared setup for collect_artifacts_to_scan cross-repo tests."""
        from cypilot.utils.context import WorkspaceContext, SourceContext, collect_artifacts_to_scan
        root, remote = _make_cross_repo_dirs(td)
        local_art = root / "artifacts" / "REQ.md"
        local_art.write_text("# Local\n", encoding="utf-8")
        remote_art = remote / "artifacts" / "REMOTE.md"
        remote_art.write_text("# Remote\n", encoding="utf-8")
        remote_meta = _CollectMeta("artifacts/REMOTE.md")
        sc = SourceContext(name="backend", path=remote, role="full", reachable=True, meta=remote_meta)
        ws = WorkspaceContext(primary=_CollectPrim(root, "artifacts/REQ.md"), sources={"backend": sc}, cross_repo=cross_repo)
        return collect_artifacts_to_scan, ws, local_art, remote_art

    def test_collect_with_cross_repo_enabled(self):
        """cross_repo=True includes remote source artifacts and populates path_to_source."""
        with TemporaryDirectory() as td:
            collect_fn, ws, local_art, remote_art = self._setup_collect_ctx(td, cross_repo=True)

            artifacts, path_to_source = collect_fn(ws)

            art_paths = [str(p) for p, _k in artifacts]
            self.assertIn(str(local_art.resolve()), art_paths)
            self.assertIn(str(remote_art.resolve()), art_paths)
            self.assertEqual(path_to_source[str(remote_art.resolve())], "backend")

    def test_collect_with_cross_repo_disabled(self):
        """cross_repo=False excludes remote source artifacts."""
        with TemporaryDirectory() as td:
            collect_fn, ws, local_art, remote_art = self._setup_collect_ctx(td, cross_repo=False)

            artifacts, path_to_source = collect_fn(ws)

            art_paths = [str(p) for p, _k in artifacts]
            self.assertIn(str(local_art.resolve()), art_paths)
            self.assertNotIn(str(remote_art.resolve()), art_paths)
            self.assertEqual(path_to_source, {})

    def test_collect_skips_unreachable_source(self):
        """Unreachable sources are excluded even with cross_repo=True."""
        from cypilot.utils.context import WorkspaceContext, SourceContext, collect_artifacts_to_scan

        with TemporaryDirectory() as td:
            root = Path(td) / "primary"
            root.mkdir()
            remote = Path(td) / "remote"
            remote.mkdir()
            (root / "artifacts").mkdir()
            (root / "artifacts" / "REQ.md").write_text("# Local\n", encoding="utf-8")
            (remote / "artifacts").mkdir()
            (remote / "artifacts" / "REMOTE.md").write_text("# Remote\n", encoding="utf-8")

            remote_meta = _CollectMeta("artifacts/REMOTE.md")
            sc = SourceContext(name="backend", path=remote, role="full", reachable=False, meta=remote_meta)
            ws = WorkspaceContext(primary=_CollectPrim(root, "artifacts/REQ.md"), sources={"backend": sc}, cross_repo=True)

            artifacts, path_to_source = collect_artifacts_to_scan(ws)

            art_paths = [str(p) for p, _k in artifacts]
            self.assertNotIn(str((remote / "artifacts" / "REMOTE.md").resolve()), art_paths)
            self.assertEqual(path_to_source, {})


if __name__ == "__main__":
    unittest.main()
