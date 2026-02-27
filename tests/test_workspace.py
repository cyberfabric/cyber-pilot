"""
Tests for multi-repo workspace support.

Tests cover:
- WorkspaceConfig loading and validation
- SourceEntry parsing
- find_workspace_config() discovery
- WorkspaceConfig.save() / add_source() mutations
- WorkspaceContext loading
- is_workspace() helper
- Source path resolution
- Cross-repo ID aggregation
"""

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.utils.workspace import (
    SourceEntry,
    TraceabilityConfig,
    WorkspaceConfig,
    find_workspace_config,
    VALID_ROLES,
)
from cypilot.utils.context import (
    CypilotContext,
    WorkspaceContext,
    SourceContext,
    set_context,
    get_context,
    is_workspace,
    get_primary_context,
)
from cypilot.utils.artifacts_meta import ArtifactsMeta, Kit


class TestSourceEntry:
    """Tests for SourceEntry dataclass."""

    def test_from_dict_basic(self):
        entry = SourceEntry.from_dict("docs", {"path": "../docs-repo", "role": "artifacts"})
        assert entry.name == "docs"
        assert entry.path == "../docs-repo"
        assert entry.role == "artifacts"
        assert entry.adapter is None

    def test_from_dict_with_adapter(self):
        entry = SourceEntry.from_dict("code", {
            "path": "../code-repo",
            "adapter": ".cypilot-adapter",
            "role": "codebase",
        })
        assert entry.adapter == ".cypilot-adapter"
        assert entry.role == "codebase"

    def test_from_dict_null_adapter(self):
        entry = SourceEntry.from_dict("kits", {"path": "../kits", "adapter": None})
        assert entry.adapter is None

    def test_from_dict_invalid_role_defaults_full(self):
        entry = SourceEntry.from_dict("x", {"path": "../x", "role": "invalid"})
        assert entry.role == "full"

    def test_from_dict_missing_role_defaults_full(self):
        entry = SourceEntry.from_dict("x", {"path": "../x"})
        assert entry.role == "full"

    def test_to_dict_minimal(self):
        entry = SourceEntry(name="x", path="../x")
        d = entry.to_dict()
        assert d == {"path": "../x"}

    def test_to_dict_with_adapter_and_role(self):
        entry = SourceEntry(name="x", path="../x", adapter=".adapter", role="kits")
        d = entry.to_dict()
        assert d == {"path": "../x", "adapter": ".adapter", "role": "kits"}


class TestWorkspaceConfig:
    """Tests for WorkspaceConfig."""

    def test_from_dict_basic(self):
        data = {
            "version": "1.0",
            "sources": {
                "docs": {"path": "../docs", "role": "artifacts"},
                "code": {"path": "../code"},
            },
        }
        cfg = WorkspaceConfig.from_dict(data)
        assert cfg.version == "1.0"
        assert len(cfg.sources) == 2
        assert "docs" in cfg.sources
        assert cfg.sources["docs"].role == "artifacts"
        assert cfg.sources["code"].role == "full"

    def test_from_dict_with_traceability(self):
        data = {
            "version": "1.0",
            "sources": {"a": {"path": "."}},
            "traceability": {"cross_repo": False, "resolve_remote_ids": False},
        }
        cfg = WorkspaceConfig.from_dict(data)
        assert cfg.traceability.cross_repo is False
        assert cfg.traceability.resolve_remote_ids is False

    def test_from_dict_empty_sources(self):
        cfg = WorkspaceConfig.from_dict({"version": "1.0", "sources": {}})
        assert len(cfg.sources) == 0

    def test_to_dict_roundtrip(self):
        original = {
            "version": "1.0",
            "sources": {
                "docs": {"path": "../docs", "role": "artifacts"},
            },
        }
        cfg = WorkspaceConfig.from_dict(original)
        result = cfg.to_dict()
        assert result["version"] == "1.0"
        assert "docs" in result["sources"]
        assert result["sources"]["docs"]["role"] == "artifacts"

    def test_validate_no_sources(self):
        cfg = WorkspaceConfig(sources={})
        errors = cfg.validate()
        assert any("no sources" in e.lower() for e in errors)

    def test_validate_empty_path(self):
        cfg = WorkspaceConfig(sources={"x": SourceEntry(name="x", path="")})
        errors = cfg.validate()
        assert any("empty path" in e.lower() for e in errors)

    def test_add_source(self):
        cfg = WorkspaceConfig()
        cfg.add_source("new-repo", "../new-repo", role="codebase", adapter=".adapter")
        assert "new-repo" in cfg.sources
        assert cfg.sources["new-repo"].path == "../new-repo"
        assert cfg.sources["new-repo"].role == "codebase"

    def test_load_valid_file(self):
        with TemporaryDirectory() as tmpdir:
            ws_path = Path(tmpdir) / ".cypilot-workspace.json"
            ws_path.write_text(json.dumps({
                "version": "1.0",
                "sources": {"test": {"path": "."}},
            }), encoding="utf-8")

            cfg, err = WorkspaceConfig.load(ws_path)
            assert err is None
            assert cfg is not None
            assert cfg.version == "1.0"
            assert "test" in cfg.sources

    def test_load_missing_file(self):
        cfg, err = WorkspaceConfig.load(Path("/nonexistent/.cypilot-workspace.json"))
        assert cfg is None
        assert "not found" in err.lower()

    def test_load_invalid_json(self):
        with TemporaryDirectory() as tmpdir:
            ws_path = Path(tmpdir) / ".cypilot-workspace.json"
            ws_path.write_text("not json", encoding="utf-8")
            cfg, err = WorkspaceConfig.load(ws_path)
            assert cfg is None
            assert err is not None

    def test_save_and_reload(self):
        with TemporaryDirectory() as tmpdir:
            ws_path = Path(tmpdir) / ".cypilot-workspace.json"
            cfg = WorkspaceConfig(
                sources={"docs": SourceEntry(name="docs", path="../docs", role="artifacts")},
                workspace_file=ws_path,
            )
            err = cfg.save()
            assert err is None

            loaded, load_err = WorkspaceConfig.load(ws_path)
            assert load_err is None
            assert loaded is not None
            assert "docs" in loaded.sources

    def test_resolve_source_path(self):
        with TemporaryDirectory() as tmpdir:
            ws_file = Path(tmpdir) / ".cypilot-workspace.json"
            cfg = WorkspaceConfig(
                sources={"repo": SourceEntry(name="repo", path="sub/repo")},
                workspace_file=ws_file,
            )
            resolved = cfg.resolve_source_path("repo")
            assert resolved == (Path(tmpdir) / "sub" / "repo").resolve()

    def test_resolve_source_path_unknown(self):
        cfg = WorkspaceConfig(workspace_file=Path("/tmp/ws.json"))
        assert cfg.resolve_source_path("nonexistent") is None

    def test_get_reachable_sources(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            real_dir = tmp / "real"
            real_dir.mkdir()

            cfg = WorkspaceConfig(
                sources={
                    "real": SourceEntry(name="real", path="real"),
                    "missing": SourceEntry(name="missing", path="not-here"),
                },
                workspace_file=tmp / "ws.json",
            )
            reachable = cfg.get_reachable_sources()
            assert "real" in reachable
            assert "missing" not in reachable


class TestFindWorkspaceConfig:
    """Tests for find_workspace_config() discovery."""

    def test_no_workspace_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            cfg, err = find_workspace_config(Path(tmpdir))
            assert cfg is None
            assert err is None

    def test_inline_dict_workspace(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            config_path = tmp / ".cypilot-config.json"
            config_path.write_text(json.dumps({
                "cypilotAdapterPath": ".adapter",
                "workspace": {
                    "sources": {"docs": {"path": "../docs"}},
                },
            }), encoding="utf-8")

            cfg, err = find_workspace_config(tmp)
            assert err is None
            assert cfg is not None
            assert cfg.is_inline is True
            assert "docs" in cfg.sources

    def test_string_ref_workspace(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)

            # Create the workspace file one level up
            ws_path = tmp / "workspace.json"
            ws_path.write_text(json.dumps({
                "version": "1.0",
                "sources": {"code": {"path": "./code"}},
            }), encoding="utf-8")

            # Create project config referencing it
            project_dir = tmp / "code"
            project_dir.mkdir()
            config_path = project_dir / ".cypilot-config.json"
            config_path.write_text(json.dumps({
                "workspace": "../workspace.json",
            }), encoding="utf-8")

            cfg, err = find_workspace_config(project_dir)
            assert err is None
            assert cfg is not None
            assert cfg.is_inline is False
            assert "code" in cfg.sources

    def test_walk_up_finds_workspace(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)

            # Create workspace file at root
            ws_path = tmp / ".cypilot-workspace.json"
            ws_path.write_text(json.dumps({
                "version": "1.0",
                "sources": {"backend": {"path": "./backend"}},
            }), encoding="utf-8")

            # Project is nested below
            project_dir = tmp / "backend"
            project_dir.mkdir()

            cfg, err = find_workspace_config(project_dir)
            assert err is None
            assert cfg is not None
            assert "backend" in cfg.sources


class TestWorkspaceContext:
    """Tests for WorkspaceContext."""

    def teardown_method(self, method):
        set_context(None)

    def _make_primary_context(self, tmpdir: Path) -> CypilotContext:
        meta = MagicMock(spec=ArtifactsMeta)
        meta.project_root = ".."
        meta.kits = {}
        meta.systems = []
        meta.get_all_system_prefixes.return_value = {"myapp"}
        meta.iter_all_artifacts.return_value = []
        return CypilotContext(
            adapter_dir=tmpdir / "adapter",
            project_root=tmpdir,
            meta=meta,
            kits={},
            registered_systems={"myapp"},
        )

    @patch("cypilot.utils.workspace.find_workspace_config")
    def test_load_returns_none_no_workspace(self, mock_find):
        mock_find.return_value = (None, None)
        with TemporaryDirectory() as tmpdir:
            ctx = self._make_primary_context(Path(tmpdir))
            ws = WorkspaceContext.load(ctx)
            assert ws is None

    @patch("cypilot.utils.workspace.find_workspace_config")
    def test_load_with_workspace(self, mock_find):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source_dir = tmp / "other-repo"
            source_dir.mkdir()

            ws_cfg = WorkspaceConfig(
                sources={"other": SourceEntry(name="other", path="other-repo")},
                workspace_file=tmp / ".cypilot-workspace.json",
            )
            mock_find.return_value = (ws_cfg, None)

            ctx = self._make_primary_context(tmp)
            ws = WorkspaceContext.load(ctx)
            assert ws is not None
            assert "other" in ws.sources
            assert ws.sources["other"].reachable is True

    @patch("cypilot.utils.workspace.find_workspace_config")
    def test_unreachable_source(self, mock_find):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            ws_cfg = WorkspaceConfig(
                sources={"missing": SourceEntry(name="missing", path="does-not-exist")},
                workspace_file=tmp / ".cypilot-workspace.json",
            )
            mock_find.return_value = (ws_cfg, None)

            ctx = self._make_primary_context(tmp)
            ws = WorkspaceContext.load(ctx)
            assert ws is not None
            assert ws.sources["missing"].reachable is False

    def test_primary_properties_delegate(self):
        with TemporaryDirectory() as tmpdir:
            ctx = self._make_primary_context(Path(tmpdir))
            ws = WorkspaceContext(primary=ctx)
            assert ws.adapter_dir == ctx.adapter_dir
            assert ws.project_root == ctx.project_root
            assert ws.meta is ctx.meta
            assert ws.registered_systems == ctx.registered_systems

    def test_get_all_registered_systems(self):
        with TemporaryDirectory() as tmpdir:
            ctx = self._make_primary_context(Path(tmpdir))
            sc = SourceContext(
                name="other",
                path=Path(tmpdir) / "other",
                role="full",
                reachable=True,
                registered_systems={"other-system"},
            )
            ws = WorkspaceContext(primary=ctx, sources={"other": sc})
            all_systems = ws.get_all_registered_systems()
            assert "myapp" in all_systems
            assert "other-system" in all_systems


class TestIsWorkspace:
    """Tests for is_workspace() helper."""

    def teardown_method(self, method):
        set_context(None)

    def test_is_workspace_false_when_cypilot_context(self):
        meta = MagicMock(spec=ArtifactsMeta)
        meta.project_root = ".."
        ctx = CypilotContext(
            adapter_dir=Path("/fake"),
            project_root=Path("/fake"),
            meta=meta,
            kits={},
            registered_systems=set(),
        )
        set_context(ctx)
        assert is_workspace() is False

    def test_is_workspace_true_when_workspace_context(self):
        meta = MagicMock(spec=ArtifactsMeta)
        meta.project_root = ".."
        ctx = CypilotContext(
            adapter_dir=Path("/fake"),
            project_root=Path("/fake"),
            meta=meta,
            kits={},
            registered_systems=set(),
        )
        ws = WorkspaceContext(primary=ctx)
        set_context(ws)
        assert is_workspace() is True

    def test_get_primary_context_from_workspace(self):
        meta = MagicMock(spec=ArtifactsMeta)
        meta.project_root = ".."
        ctx = CypilotContext(
            adapter_dir=Path("/fake"),
            project_root=Path("/fake"),
            meta=meta,
            kits={},
            registered_systems=set(),
        )
        ws = WorkspaceContext(primary=ctx)
        set_context(ws)
        assert get_primary_context() is ctx

    def test_get_primary_context_from_cypilot(self):
        meta = MagicMock(spec=ArtifactsMeta)
        meta.project_root = ".."
        ctx = CypilotContext(
            adapter_dir=Path("/fake"),
            project_root=Path("/fake"),
            meta=meta,
            kits={},
            registered_systems=set(),
        )
        set_context(ctx)
        assert get_primary_context() is ctx
