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

import argparse
import json
import pytest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.utils import toml_utils

from cypilot.utils.workspace import (
    SourceEntry,
    TraceabilityConfig,
    NamespaceRule,
    ResolveConfig,
    WorkspaceConfig,
    find_workspace_config,
    validate_source_name,
    VALID_ROLES,
)
from cypilot.utils.context import (
    CypilotContext,
    WorkspaceContext,
    SourceContext,
    resolve_adapter_context,
    get_expanded_meta,
    determine_target_source,
    set_context,
    get_context,
    is_workspace,
    get_primary_context,
    _load_reachable_source,
)
from cypilot.utils.artifacts_meta import ArtifactsMeta, Kit

from cypilot.utils.git_utils import (
    is_worktree_dirty,
    _parse_git_url,
    _apply_template,
    _lookup_namespace,
    _redact_url,
    _run_git,
    resolve_git_source,
    sync_git_source,
)
from cypilot.commands.workspace_init import (
    _is_project_dir,
    _find_adapter_path,
    _compute_source_path,
    _infer_role,
    _sanitize_source_name,
    _scan_nested_repos,
    _write_standalone,
    _write_inline,
    _check_existing_workspace,
    _human_workspace_init,
    cmd_workspace_init,
)
from cypilot.commands.workspace_info import (
    _probe_source_adapter,
    _build_source_info,
    _enrich_with_artifact_counts,
    _human_workspace_info,
    cmd_workspace_info,
)
from cypilot.commands.workspace_add import (
    _add_to_standalone,
    _add_to_inline,
    _human_workspace_add,
    cmd_workspace_add,
)
from cypilot.commands.workspace_sync import (
    _human_workspace_sync,
    cmd_workspace_sync,
)


# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------

def _make_mock_meta(project_root: str = "..") -> MagicMock:
    """Create a standard ArtifactsMeta mock for tests."""
    meta = MagicMock(spec=ArtifactsMeta)
    meta.project_root = project_root
    meta.kits = {}
    meta.systems = []
    meta.get_all_system_prefixes.return_value = set()
    meta.iter_all_artifacts.return_value = []
    return meta


def _make_mock_ctx(tmpdir: Path, *, project_root_meta: str = "..") -> CypilotContext:
    """Create a standard CypilotContext with mock meta."""
    return CypilotContext(
        adapter_dir=tmpdir / "adapter",
        project_root=tmpdir,
        meta=_make_mock_meta(project_root_meta),
        kits={},
        registered_systems=set(),
    )


def _setup_config_dir(root: Path, content: str = "") -> Path:
    """Create cypilot/config/core.toml scaffold, return config_dir."""
    config_dir = root / "cypilot" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "core.toml").write_text(content)
    return config_dir


def _clone_side_effect(args, cwd=None):
    """Simulate successful git clone by creating directory + .git."""
    if args[0] == "clone":
        clone_path = Path(args[-1])
        clone_path.mkdir(parents=True, exist_ok=True)
        (clone_path / ".git").mkdir()
    return (0, "", "")


def _parse_json(capsys) -> dict:
    """Parse JSON from captured stdout."""
    return json.loads(capsys.readouterr().out)


def _make_inline_args(name: str = "x", path: str = "../x", role: str = "full",
                      adapter=None, force: bool = False, **kwargs) -> argparse.Namespace:
    """Create argparse.Namespace for _add_to_inline tests."""
    return argparse.Namespace(name=name, path=path, role=role, adapter=adapter, force=force, **kwargs)


def _make_ws_cfg(tmpdir, sources_dict=None):
    """Create a WorkspaceConfig with sources and workspace_file set."""
    if sources_dict is None:
        sources_dict = {"docs": SourceEntry(name="docs", path=str(tmpdir / "repo"), role="artifacts")}
    return WorkspaceConfig(
        sources=sources_dict,
        workspace_file=Path(tmpdir) / ".cypilot-workspace.toml",
    )


def _make_standalone_ws_mock(tmpdir):
    """Create a MagicMock representing a standalone workspace config."""
    ws = MagicMock()
    ws.is_inline = False
    ws.workspace_file = Path(tmpdir) / ".cypilot-workspace.toml"
    ws.save.return_value = None
    return ws


def _make_git_source(url="https://gitlab.com/team/lib.git", branch="main"):
    """Create a SourceEntry for git source tests."""
    return SourceEntry(name="r", path="", url=url, branch=branch)


def _make_gitlab_resolve_cfg(workdir=".ws"):
    """Create a ResolveConfig with gitlab.com namespace rule."""
    return ResolveConfig(
        workdir=workdir,
        namespace=[NamespaceRule(host="gitlab.com", template="{org}/{repo}")],
    )


def _run_workspace_info(capsys, ws_cfg, tmpdir, *, ctx_return=None):
    """Run cmd_workspace_info with mocked project root, config, adapter, and context."""
    with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
        with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
            with patch("cypilot.commands.workspace_info._probe_source_adapter", return_value=None):
                with patch("cypilot.utils.context.get_context", return_value=ctx_return):
                    rc = cmd_workspace_info([])
                    data = json.loads(capsys.readouterr().out)
                    return rc, data


def _make_docs_ws_cfg(tmpdir, src_dir):
    """Create a WorkspaceConfig with a single 'docs' source."""
    return WorkspaceConfig(
        sources={"docs": SourceEntry(name="docs", path=str(src_dir), role="artifacts")},
        workspace_file=Path(tmpdir) / ".cypilot-workspace.toml",
    )


def _setup_repo_with_adapter(root: Path, name: str = "sub-repo") -> Path:
    """Create a sub-repo directory with .git and cypilot adapter."""
    repo = root / name
    repo.mkdir()
    (repo / ".git").mkdir()
    adapter = repo / "cypilot"
    adapter.mkdir()
    (adapter / "config").mkdir()
    return repo



class TestValidateSourceName:
    """Tests for validate_source_name()."""

    def test_valid_simple(self):
        assert validate_source_name("my-repo") is None

    def test_valid_with_dots_and_underscores(self):
        assert validate_source_name("my.repo_v2") is None

    def test_valid_numeric_start(self):
        assert validate_source_name("2fast") is None

    def test_empty_name(self):
        assert validate_source_name("") is not None

    def test_path_separator(self):
        assert validate_source_name("foo/bar") is not None

    def test_backslash(self):
        assert validate_source_name("foo\\bar") is not None

    def test_double_dot(self):
        assert validate_source_name("foo..bar") is not None

    def test_leading_dot(self):
        assert validate_source_name(".hidden") is not None

    def test_leading_hyphen(self):
        assert validate_source_name("-bad") is not None

    def test_space_in_name(self):
        assert validate_source_name("my repo") is not None

    def test_special_chars(self):
        assert validate_source_name("repo@v1") is not None
        assert validate_source_name("repo[0]") is not None


class TestSanitizeSourceName:
    """Tests for _sanitize_source_name()."""

    def test_clean_name_unchanged(self):
        assert _sanitize_source_name("my-repo") == "my-repo"

    def test_spaces_replaced(self):
        assert _sanitize_source_name("my repo") == "my-repo"

    def test_slashes_replaced(self):
        assert _sanitize_source_name("org/repo") == "org-repo"

    def test_leading_special_stripped(self):
        assert _sanitize_source_name(".hidden") == "hidden"

    def test_consecutive_hyphens_collapsed(self):
        assert _sanitize_source_name("a@#b") == "a-b"

    def test_empty_fallback(self):
        assert _sanitize_source_name("@#$") == "source"


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

    def test_from_dict_invalid_role_raises(self):
        with pytest.raises(ValueError, match="invalid role"):
            SourceEntry.from_dict("x", {"path": "../x", "role": "invalid"})

    def test_constructor_invalid_role_raises(self):
        with pytest.raises(ValueError, match="invalid role"):
            SourceEntry(name="x", path="../x", role="invalid")

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

    def test_post_init_normalizes_empty_path_to_none(self):
        """Direct SourceEntry(path='') should normalize to None, matching from_dict behavior."""
        entry = SourceEntry(name="x", path="")
        assert entry.path is None

    def test_post_init_normalizes_whitespace_path_to_none(self):
        entry = SourceEntry(name="x", path="   ")
        assert entry.path is None

    def test_post_init_normalizes_empty_url_to_none(self):
        entry = SourceEntry(name="x", path="../x", url="")
        assert entry.url is None

    def test_post_init_normalizes_empty_branch_to_none(self):
        entry = SourceEntry(name="x", url="https://example.com/repo.git", branch="")
        assert entry.branch is None

    def test_post_init_strips_path_whitespace(self):
        entry = SourceEntry(name="x", path="  ../x  ")
        assert entry.path == "../x"

    def test_post_init_preserves_valid_values(self):
        entry = SourceEntry(name="x", path="../x", url="https://example.com/repo.git", branch="main")
        assert entry.path == "../x"
        assert entry.url == "https://example.com/repo.git"
        assert entry.branch == "main"


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

    def test_from_dict_sources_not_mapping_raises(self):
        with pytest.raises(ValueError, match="'sources' must be a mapping"):
            WorkspaceConfig.from_dict({"version": "1.0", "sources": 42})

    def test_from_dict_source_entry_not_table_raises(self):
        with pytest.raises(ValueError, match="Source 'bad' must be a table, got str"):
            WorkspaceConfig.from_dict({
                "version": "1.0",
                "sources": {"bad": "not-a-table"},
            })

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

    def test_validate_empty_sources_ok(self):
        """Empty workspace is valid — sources can be added later via workspace-add."""
        cfg = WorkspaceConfig(sources={})
        errors = cfg.validate()
        assert errors == []

    def test_validate_empty_path(self):
        cfg = WorkspaceConfig(sources={"x": SourceEntry(name="x", path="")})
        errors = cfg.validate()
        assert any("must have either" in e.lower() for e in errors)

    def test_validate_path_with_branch_rejected(self):
        """path + branch is forbidden — branch only valid with url (schema oneOf)."""
        cfg = WorkspaceConfig(sources={"x": SourceEntry(name="x", path="../foo", branch="main")})
        errors = cfg.validate()
        assert any("path" in e and "branch" in e for e in errors)

    def test_validate_url_with_branch_ok(self):
        """url + branch is allowed by schema."""
        cfg = WorkspaceConfig(sources={"x": SourceEntry(name="x", url="https://example.com/repo.git", branch="main")})
        errors = cfg.validate()
        assert not any("branch" in e for e in errors)

    def test_add_source(self):
        cfg = WorkspaceConfig()
        cfg.add_source("new-repo", "../new-repo", role="codebase", adapter=".adapter")
        assert "new-repo" in cfg.sources
        assert cfg.sources["new-repo"].path == "../new-repo"
        assert cfg.sources["new-repo"].role == "codebase"

    def test_load_valid_file(self):
        with TemporaryDirectory() as tmpdir:
            ws_path = Path(tmpdir) / ".cypilot-workspace.toml"
            toml_utils.dump({
                "version": "1.0",
                "sources": {"test": {"path": "."}},
            }, ws_path)

            cfg, err = WorkspaceConfig.load(ws_path)
            assert err is None
            assert cfg is not None
            assert cfg.version == "1.0"
            assert "test" in cfg.sources

    def test_load_missing_file(self):
        cfg, err = WorkspaceConfig.load(Path("/nonexistent/.cypilot-workspace.toml"))
        assert cfg is None
        assert "not found" in err.lower()

    def test_load_invalid_toml(self):
        with TemporaryDirectory() as tmpdir:
            ws_path = Path(tmpdir) / ".cypilot-workspace.toml"
            ws_path.write_text("[invalid\nbroken toml =", encoding="utf-8")
            cfg, err = WorkspaceConfig.load(ws_path)
            assert cfg is None
            assert err is not None

    def test_load_invalid_role_returns_error(self):
        """load() catches ValueError from invalid role in source."""
        with TemporaryDirectory() as tmpdir:
            ws_path = Path(tmpdir) / ".cypilot-workspace.toml"
            toml_utils.dump({
                "version": "1.0",
                "sources": {"bad": {"path": "../bad", "role": "bogus"}},
            }, ws_path)
            cfg, err = WorkspaceConfig.load(ws_path)
            assert cfg is None
            assert "invalid role" in err.lower()

    def test_save_inline_rejects_invalid_existing_config(self):
        """save() for inline workspace returns error when existing file is not a dict."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "core.toml"
            # Write a bare value (not a table) — toml_utils wraps it, but
            # we can simulate by writing raw TOML that parses to a non-dict
            # via a direct file write.
            config_path.write_text('"just a string"', encoding="utf-8")
            cfg = WorkspaceConfig(
                sources={"x": SourceEntry(name="x", path="../x")},
                workspace_file=config_path,
                is_inline=True,
            )
            err = cfg.save()
            assert err is not None

    def test_save_and_reload(self):
        with TemporaryDirectory() as tmpdir:
            ws_path = Path(tmpdir) / ".cypilot-workspace.toml"
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

    def test_save_inline_preserves_other_sections(self):
        """Saving an inline workspace must not clobber other core.toml sections."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "core.toml"
            # Seed core.toml with non-workspace sections
            toml_utils.dump(
                {
                    "project_root": "..",
                    "kits": [{"name": "sdlc", "version": "1.0"}],
                    "ignore": ["node_modules"],
                },
                config_path,
            )
            cfg = WorkspaceConfig(
                sources={"docs": SourceEntry(name="docs", path="../docs", role="artifacts")},
                workspace_file=config_path,
                is_inline=True,
            )
            err = cfg.save()
            assert err is None

            # Reload full file and verify all sections survived
            reloaded = toml_utils.load(config_path)
            assert reloaded["project_root"] == ".."
            assert reloaded["kits"] == [{"name": "sdlc", "version": "1.0"}]
            assert reloaded["ignore"] == ["node_modules"]
            # Workspace section is present
            assert "workspace" in reloaded
            assert "docs" in reloaded["workspace"]["sources"]

    def test_resolve_source_path(self):
        with TemporaryDirectory() as tmpdir:
            ws_file = Path(tmpdir) / ".cypilot-workspace.toml"
            cfg = WorkspaceConfig(
                sources={"repo": SourceEntry(name="repo", path="sub/repo")},
                workspace_file=ws_file,
            )
            resolved = cfg.resolve_source_path("repo")
            assert resolved == (Path(tmpdir) / "sub" / "repo").resolve()

    def test_resolve_source_path_unknown(self):
        with TemporaryDirectory() as tmpdir:
            cfg = WorkspaceConfig(workspace_file=Path(tmpdir) / "ws.toml")
            assert cfg.resolve_source_path("nonexistent") is None

    def test_resolve_source_adapter_returns_path(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo = tmp / "repo"
            repo.mkdir()
            adapter = repo / ".my-adapter"
            adapter.mkdir()

            cfg = WorkspaceConfig(
                sources={"repo": SourceEntry(name="repo", path="repo", adapter=".my-adapter")},
                workspace_file=tmp / "ws.toml",
            )
            result = cfg.resolve_source_adapter("repo")
            assert result == adapter.resolve()

    def test_resolve_source_adapter_none_when_no_adapter(self):
        with TemporaryDirectory() as tmpdir:
            cfg = WorkspaceConfig(
                sources={"repo": SourceEntry(name="repo", path="repo")},
                workspace_file=Path(tmpdir) / "ws.toml",
            )
            assert cfg.resolve_source_adapter("repo") is None

    def test_resolve_source_adapter_none_for_unknown_source(self):
        cfg = WorkspaceConfig()
        assert cfg.resolve_source_adapter("nonexistent") is None


class TestFindWorkspaceConfig:
    """Tests for find_workspace_config() discovery."""

    def test_no_workspace_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            cfg, err = find_workspace_config(Path(tmpdir))
            assert cfg is None
            assert err is None

    def _setup_v3_project(self, project_root: Path, core_toml_data: dict) -> None:
        """Helper: create a v3-style project with AGENTS.md + config/core.toml."""
        import tomllib  # noqa: F401 - just to verify availability

        # Create AGENTS.md with root-agents marker and cypilot_path
        agents_md = project_root / "AGENTS.md"
        agents_md.write_text(
            "<!-- @cpt:root-agents -->\n"
            "# Project\n\n"
            "```toml\n"
            'cypilot_path = ".cypilot"\n'
            "```\n"
            "<!-- @cpt:root-agents -->\n",
            encoding="utf-8",
        )

        # Create config/core.toml
        config_dir = project_root / ".cypilot" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)


        toml_utils.dump(core_toml_data, config_dir / "core.toml")

    def test_inline_dict_workspace(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            self._setup_v3_project(tmp, {
                "workspace": {
                    "version": "1.0",
                    "sources": {"docs": {"path": "../docs"}},
                },
            })

            cfg, err = find_workspace_config(tmp)
            assert err is None
            assert cfg is not None
            assert cfg.is_inline is True
            assert "docs" in cfg.sources

    def test_inline_workspace_invalid_role_returns_error(self):
        """Inline workspace with invalid role returns error instead of silently defaulting."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            self._setup_v3_project(tmp, {
                "workspace": {
                    "version": "1.0",
                    "sources": {"bad": {"path": "../bad", "role": "bogus"}},
                },
            })

            cfg, err = find_workspace_config(tmp)
            assert cfg is None
            assert err is not None
            assert "invalid role" in err.lower()

    def test_inline_workspace_resolves_relative_to_project_root(self):
        """CR-2: Inline workspace source paths must resolve relative to project root,
        not relative to core.toml's parent directory."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            # Create nested docs dir
            docs_dir = tmp / "docs"
            docs_dir.mkdir()

            project_dir = tmp / "code"
            project_dir.mkdir()
            self._setup_v3_project(project_dir, {
                "workspace": {
                    "version": "1.0",
                    "sources": {"docs": {"path": "../docs"}},
                },
            })

            cfg, err = find_workspace_config(project_dir)
            assert err is None
            assert cfg is not None
            assert cfg.is_inline is True
            # Path should resolve relative to project root (code/), not core.toml parent
            resolved = cfg.resolve_source_path("docs")
            assert resolved == docs_dir.resolve()

    def test_string_ref_workspace(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)

            # Create the workspace file one level up
            ws_path = tmp / "workspace.toml"
            toml_utils.dump({
                "version": "1.0",
                "sources": {"code": {"path": "./code"}},
            }, ws_path)

            # Create v3 project config referencing external workspace file
            project_dir = tmp / "code"
            project_dir.mkdir()
            self._setup_v3_project(project_dir, {
                "workspace": "../workspace.toml",
            })

            cfg, err = find_workspace_config(project_dir)
            assert err is None
            assert cfg is not None
            assert cfg.is_inline is False
            assert "code" in cfg.sources

    def test_parse_failure_returns_error(self):
        """Malformed core.toml returns (None, error_message) instead of silent (None, None)."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            agents_md = tmp / "AGENTS.md"
            agents_md.write_text(
                "<!-- @cpt:root-agents -->\n"
                "```toml\n"
                'cypilot_path = ".cypilot"\n'
                "```\n"
                "<!-- @cpt:root-agents -->\n",
                encoding="utf-8",
            )
            config_dir = tmp / ".cypilot" / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            (config_dir / "core.toml").write_text("{{invalid toml", encoding="utf-8")

            cfg, err = find_workspace_config(tmp)
            assert cfg is None
            assert err is not None
            assert "Failed to parse" in err

    def test_standalone_file_discovered_at_project_root(self):
        """Standalone .cypilot-workspace.toml at project root is discovered without core.toml reference."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            ws_path = tmp / ".cypilot-workspace.toml"
            toml_utils.dump({
                "version": "1.0",
                "sources": {"lib": {"path": "../lib"}},
            }, ws_path)

            cfg, err = find_workspace_config(tmp)
            assert err is None
            assert cfg is not None
            assert cfg.is_inline is False
            assert "lib" in cfg.sources

    def test_standalone_file_not_discovered_at_parent(self):
        """Standalone .cypilot-workspace.toml one level above project root is NOT discovered (no parent walk-up)."""
        with TemporaryDirectory() as tmpdir:
            parent = Path(tmpdir)
            ws_path = parent / ".cypilot-workspace.toml"
            toml_utils.dump({
                "version": "1.0",
                "sources": {"docs": {"path": "./docs"}},
            }, ws_path)

            project_dir = parent / "repo-a"
            project_dir.mkdir()

            cfg, err = find_workspace_config(project_dir)
            assert err is None
            assert cfg is None

    def test_core_toml_workspace_takes_precedence_over_standalone(self):
        """core.toml workspace key takes priority over standalone file on disk."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)

            # Create standalone file with "stale" source
            toml_utils.dump({
                "version": "1.0",
                "sources": {"stale": {"path": "../stale"}},
            }, tmp / ".cypilot-workspace.toml")

            # Create core.toml with inline workspace
            self._setup_v3_project(tmp, {
                "workspace": {
                    "version": "1.0",
                    "sources": {"primary": {"path": "../primary"}},
                },
            })

            cfg, err = find_workspace_config(tmp)
            assert err is None
            assert cfg is not None
            assert cfg.is_inline is True
            assert "primary" in cfg.sources
            assert "stale" not in cfg.sources

    def test_malformed_workspace_value_returns_error(self):
        """Non-string, non-dict workspace value returns config error instead of silent fallback."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            self._setup_v3_project(tmp, {"workspace": 42})

            cfg, err = find_workspace_config(tmp)
            assert cfg is None
            assert err is not None
            assert "Malformed" in err
            assert "42" in err

    def test_empty_string_workspace_returns_error(self):
        """workspace = '' is malformed, not absent."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            self._setup_v3_project(tmp, {"workspace": ""})

            cfg, err = find_workspace_config(tmp)
            assert cfg is None
            assert err is not None
            assert "Malformed" in err


class TestWorkspaceContext:
    """Tests for WorkspaceContext."""

    def teardown_method(self, method):
        set_context(None)

    @staticmethod
    def _make_primary_context(tmpdir: Path) -> CypilotContext:
        meta = _make_mock_meta()
        meta.get_all_system_prefixes.return_value = {"myapp"}
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
                workspace_file=tmp / ".cypilot-workspace.toml",
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
                workspace_file=tmp / ".cypilot-workspace.toml",
            )
            mock_find.return_value = (ws_cfg, None)

            ctx = self._make_primary_context(tmp)
            ws = WorkspaceContext.load(ctx)
            assert ws is not None
            sc = ws.sources["missing"]
            assert sc.reachable is False
            assert sc.name == "missing"
            assert sc.error is not None
            assert "does-not-exist" in sc.error

    def test_primary_properties_delegate(self):
        with TemporaryDirectory() as tmpdir:
            ctx = self._make_primary_context(Path(tmpdir))
            ws = WorkspaceContext(primary=ctx)
            assert ws.adapter_dir == ctx.adapter_dir
            assert ws.project_root == ctx.project_root
            assert ws.meta is ctx.meta
            assert ws.registered_systems == ctx.registered_systems

    def test_resolve_artifact_path_no_source(self):
        """Artifact without source resolves relative to fallback_root."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            ctx = self._make_primary_context(tmp)
            ws = WorkspaceContext(primary=ctx)

            artifact = MagicMock()
            artifact.path = "docs/DESIGN.md"
            artifact.source = None

            result = ws.resolve_artifact_path(artifact, tmp)
            assert result == (tmp / "docs/DESIGN.md").resolve()

    def test_resolve_artifact_path_reachable_source(self):
        """Artifact with source pointing to a reachable source resolves via that source."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source_dir = tmp / "other-repo"
            source_dir.mkdir()

            ctx = self._make_primary_context(tmp)
            sc = SourceContext(
                name="other",
                path=source_dir,
                role="full",
                reachable=True,
            )
            ws = WorkspaceContext(primary=ctx, sources={"other": sc})

            artifact = MagicMock()
            artifact.path = "docs/DESIGN.md"
            artifact.source = "other"

            result = ws.resolve_artifact_path(artifact, tmp)
            assert result == (source_dir / "docs/DESIGN.md").resolve()

    def test_resolve_artifact_path_missing_source_returns_none(self):
        """Artifact with source not in workspace returns None instead of falling back."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            ctx = self._make_primary_context(tmp)
            ws = WorkspaceContext(primary=ctx, sources={})

            artifact = MagicMock()
            artifact.path = "docs/DESIGN.md"
            artifact.source = "nonexistent"

            result = ws.resolve_artifact_path(artifact, tmp)
            assert result is None

    def test_resolve_artifact_path_unreachable_source_returns_none(self):
        """Artifact with source pointing to an unreachable source returns None."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            ctx = self._make_primary_context(tmp)
            sc = SourceContext(
                name="down",
                path=tmp / "missing-dir",
                role="full",
                reachable=False,
                error="Source directory not found",
            )
            ws = WorkspaceContext(primary=ctx, sources={"down": sc})

            artifact = MagicMock()
            artifact.path = "docs/DESIGN.md"
            artifact.source = "down"

            result = ws.resolve_artifact_path(artifact, tmp)
            assert result is None

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

    def test_resolve_remote_ids_false_skips_remote_sources(self):
        """get_all_artifact_ids must ignore remote sources when resolve_remote_ids=False."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)

            # Create a primary artifact file with a definition
            (tmp / "PRIMARY.md").write_text("**ID**: `cpt-primary-id`\n", encoding="utf-8")

            # Create a remote artifact file with a different definition
            remote_dir = tmp / "remote"
            remote_dir.mkdir()
            (remote_dir / "REMOTE.md").write_text("**ID**: `cpt-remote-id`\n", encoding="utf-8")

            # Primary context with one artifact pointing to PRIMARY.md
            primary_artifact = MagicMock()
            primary_artifact.path = "PRIMARY.md"
            primary_artifact.source = None

            meta = _make_mock_meta(".")
            meta.iter_all_artifacts.return_value = [(primary_artifact, None)]

            primary_ctx = CypilotContext(
                adapter_dir=tmp / "adapter", project_root=tmp,
                meta=meta, kits={}, registered_systems=set(),
            )

            # Remote source with one artifact pointing to REMOTE.md
            remote_artifact = MagicMock()
            remote_artifact.path = "REMOTE.md"
            remote_meta = MagicMock(spec=ArtifactsMeta)
            remote_meta.iter_all_artifacts.return_value = [(remote_artifact, None)]

            remote_sc = SourceContext(
                name="remote",
                path=remote_dir,
                role="full",
                reachable=True,
                meta=remote_meta,
                registered_systems=set(),
            )

            # Case 1: resolve_remote_ids=True — both IDs collected
            ws_enabled = WorkspaceContext(
                primary=primary_ctx,
                sources={"remote": remote_sc},
                cross_repo=True,
                resolve_remote_ids=True,
            )
            ids_enabled = ws_enabled.get_all_artifact_ids()
            assert "cpt-primary-id" in ids_enabled
            assert "cpt-remote-id" in ids_enabled

            # Case 2: resolve_remote_ids=False — only primary IDs
            ws_disabled = WorkspaceContext(
                primary=primary_ctx,
                sources={"remote": remote_sc},
                cross_repo=True,
                resolve_remote_ids=False,
            )
            ids_disabled = ws_disabled.get_all_artifact_ids()
            assert "cpt-primary-id" in ids_disabled
            assert "cpt-remote-id" not in ids_disabled

    def test_scan_failure_does_not_crash_get_all_artifact_ids(self):
        """get_all_artifact_ids must continue when scan_cpt_ids raises for a file."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)

            # Create two artifact files: one good, one that will trigger scan failure
            (tmp / "GOOD.md").write_text("**ID**: `cpt-good-id`\n", encoding="utf-8")
            (tmp / "BAD.md").write_text("**ID**: `cpt-bad-id`\n", encoding="utf-8")

            good_artifact = MagicMock()
            good_artifact.path = "GOOD.md"
            good_artifact.source = None
            bad_artifact = MagicMock()
            bad_artifact.path = "BAD.md"
            bad_artifact.source = None

            meta = _make_mock_meta(".")
            meta.iter_all_artifacts.return_value = [
                (bad_artifact, None),
                (good_artifact, None),
            ]

            primary_ctx = CypilotContext(
                adapter_dir=tmp / "adapter", project_root=tmp,
                meta=meta, kits={}, registered_systems=set(),
            )
            ws = WorkspaceContext(primary=primary_ctx)

            from cypilot.utils.document import scan_cpt_ids as real_scan

            def _mock_scan(path):
                if path.name == "BAD.md":
                    raise OSError("Simulated read failure")
                return real_scan(path)

            # _scan_definition_ids imports scan_cpt_ids from .document each call
            with patch("cypilot.utils.document.scan_cpt_ids", side_effect=_mock_scan):
                ids = ws.get_all_artifact_ids()

            assert "cpt-good-id" in ids
            assert "cpt-bad-id" not in ids


    @patch("cypilot.utils.workspace.find_workspace_config")
    def test_load_uses_resolve_source_adapter(self, mock_find):
        """WorkspaceContext.load resolves adapter dir via WorkspaceConfig.resolve_source_adapter."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source_dir = tmp / "other-repo"
            source_dir.mkdir()
            adapter_dir = source_dir / ".custom-adapter"
            adapter_dir.mkdir()
            (adapter_dir / "AGENTS.md").write_text("# Adapter\n")
            (adapter_dir / "config").mkdir()
            (adapter_dir / "config" / "artifacts.toml").write_text("")

            ws_cfg = WorkspaceConfig(
                sources={"other": SourceEntry(name="other", path="other-repo", adapter=".custom-adapter")},
                workspace_file=tmp / ".cypilot-workspace.toml",
            )
            mock_find.return_value = (ws_cfg, None)

            ctx = self._make_primary_context(tmp)
            ws = WorkspaceContext.load(ctx)
            assert ws is not None
            sc = ws.sources["other"]
            assert sc.reachable is True
            assert sc.adapter_dir == adapter_dir.resolve()


class TestIsWorkspace:
    """Tests for is_workspace() helper."""

    def teardown_method(self, method):
        set_context(None)

    @staticmethod
    def _fake_ctx() -> CypilotContext:
        return _make_mock_ctx(Path("/fake"))

    def test_is_workspace_false_when_cypilot_context(self):
        ctx = self._fake_ctx()
        set_context(ctx)
        assert is_workspace() is False

    def test_is_workspace_true_when_workspace_context(self):
        ctx = self._fake_ctx()
        ws = WorkspaceContext(primary=ctx)
        set_context(ws)
        assert is_workspace() is True

    def test_get_primary_context_from_workspace(self):
        ctx = self._fake_ctx()
        ws = WorkspaceContext(primary=ctx)
        set_context(ws)
        assert get_primary_context() is ctx

    def test_get_primary_context_from_cypilot(self):
        ctx = self._fake_ctx()
        set_context(ctx)
        assert get_primary_context() is ctx


class TestSourceEntryGitFields:
    """Tests for SourceEntry url/branch fields."""

    def test_from_dict_with_url_and_branch(self):
        entry = SourceEntry.from_dict("remote", {
            "url": "https://gitlab.com/team/lib.git",
            "branch": "main",
            "role": "codebase",
        })
        assert entry.url == "https://gitlab.com/team/lib.git"
        assert entry.branch == "main"
        assert entry.path is None
        assert entry.role == "codebase"

    def test_from_dict_url_only(self):
        entry = SourceEntry.from_dict("remote", {"url": "git@gitlab.com:team/lib.git"})
        assert entry.url == "git@gitlab.com:team/lib.git"
        assert entry.branch is None

    def test_from_dict_no_url(self):
        entry = SourceEntry.from_dict("local", {"path": "../lib"})
        assert entry.url is None
        assert entry.branch is None

    def test_to_dict_with_url_and_branch(self):
        entry = SourceEntry(name="r", path="", url="https://x.com/a/b.git", branch="dev", role="codebase")
        d = entry.to_dict()
        assert d["url"] == "https://x.com/a/b.git"
        assert d["branch"] == "dev"
        assert d["role"] == "codebase"

    def test_to_dict_without_url(self):
        entry = SourceEntry(name="r", path="../lib")
        d = entry.to_dict()
        assert "url" not in d
        assert "branch" not in d
        assert d["path"] == "../lib"

    def test_roundtrip_url_source(self):
        original = {"url": "https://gitlab.com/org/repo.git", "branch": "v2", "role": "artifacts"}
        entry = SourceEntry.from_dict("x", original)
        d = entry.to_dict()
        assert d["url"] == original["url"]
        assert d["branch"] == original["branch"]
        assert d["role"] == original["role"]


class TestNamespaceRule:
    """Tests for NamespaceRule dataclass."""

    def test_to_dict(self):
        rule = NamespaceRule(host="github.com", template="{org}/{repo}")
        d = rule.to_dict()
        assert d == {"host": "github.com", "template": "{org}/{repo}"}


class TestResolveConfig:
    """Tests for ResolveConfig dataclass."""

    def test_from_dict_defaults(self):
        cfg = ResolveConfig.from_dict({})
        assert cfg.workdir == ".workspace-sources"
        assert cfg.namespace == []

    def test_from_dict_full(self):
        cfg = ResolveConfig.from_dict({
            "workdir": ".repos",
            "namespace": {
                "gitlab.com": "{org}/{repo}",
                "github.com": "gh/{org}/{repo}",
            },
        })
        assert cfg.workdir == ".repos"
        assert len(cfg.namespace) == 2
        assert cfg.namespace[0].host == "gitlab.com"
        assert cfg.namespace[1].host == "github.com"

    def test_to_dict(self):
        cfg = ResolveConfig(
            workdir=".repos",
            namespace=[NamespaceRule(host="x.com", template="{org}/{repo}")],
        )
        d = cfg.to_dict()
        assert d["workdir"] == ".repos"
        assert d["namespace"] == {"x.com": "{org}/{repo}"}

    def test_to_dict_no_namespace(self):
        cfg = ResolveConfig()
        d = cfg.to_dict()
        assert "namespace" not in d

    def test_workspace_config_roundtrip_with_resolve(self):
        data = {
            "version": "1.0",
            "sources": {"remote-lib": {"url": "https://gitlab.com/team/lib.git", "branch": "main", "role": "codebase"}},
            "resolve": {
                "workdir": ".workspace-sources",
                "namespace": {"gitlab.com": "{org}/{repo}"},
            },
        }
        cfg = WorkspaceConfig.from_dict(data)
        assert cfg.resolve is not None
        assert cfg.resolve.workdir == ".workspace-sources"
        assert len(cfg.resolve.namespace) == 1

        d = cfg.to_dict()
        assert "resolve" in d
        assert d["resolve"]["workdir"] == ".workspace-sources"
        assert d["resolve"]["namespace"] == {"gitlab.com": "{org}/{repo}"}


class TestValidateRejectsInlineUrls:
    """Inline workspaces must reject url fields."""

    def test_inline_with_url_produces_error(self):
        cfg = WorkspaceConfig(
            sources={"r": SourceEntry(name="r", path="", url="https://x.com/a/b.git")},
            is_inline=True,
        )
        errors = cfg.validate()
        assert any("inline" in e.lower() and "url" in e.lower() for e in errors)

    def test_standalone_with_url_no_error(self):
        cfg = WorkspaceConfig(
            sources={"r": SourceEntry(name="r", path="", url="https://x.com/a/b.git")},
            is_inline=False,
        )
        errors = cfg.validate()
        # Should not have the inline-url error
        assert not any("inline" in e.lower() for e in errors)


class TestRedactUrl:
    """Tests for _redact_url credential stripping."""

    def test_plain_https_unchanged(self):
        assert _redact_url("https://gitlab.com/org/repo.git") == "https://gitlab.com/org/repo.git"

    def test_ssh_shorthand_redacted(self):
        assert _redact_url("git@gitlab.com:org/repo.git") == "***@gitlab.com:org/repo.git"

    def test_strips_user_password(self):
        url = "https://user:token@gitlab.com/org/repo.git"  # noqa: S105  # NOSONAR
        result = _redact_url(url)
        assert result == "https://gitlab.com/org/repo.git"

    def test_strips_token_only(self):
        url = "https://x-access-token:ghp_abc123@github.com/org/repo.git"  # noqa: S105  # NOSONAR
        result = _redact_url(url)
        assert result == "https://github.com/org/repo.git"

    def test_preserves_port(self):
        url = "https://user:pass@gitlab.example.com:8443/org/repo.git"  # noqa: S105  # NOSONAR
        result = _redact_url(url)
        assert result == "https://gitlab.example.com:8443/org/repo.git"


class TestGitUrlParsing:
    """Tests for _parse_git_url."""

    def test_https_url(self):

        result = _parse_git_url("https://gitlab.com/team/lib.git")
        assert result == ("gitlab.com", "team", "lib")

    def test_https_url_without_dot_git(self):

        result = _parse_git_url("https://gitlab.com/team/lib")
        assert result == ("gitlab.com", "team", "lib")

    def test_ssh_shorthand(self):

        result = _parse_git_url("git@gitlab.com:team/lib.git")
        assert result == ("gitlab.com", "team", "lib")

    def test_ssh_url(self):

        result = _parse_git_url("ssh://git@gitlab.com/team/lib.git")
        assert result == ("gitlab.com", "team", "lib")

    def test_nested_org(self):

        result = _parse_git_url("https://gitlab.com/org/sub/repo.git")
        assert result == ("gitlab.com", "org/sub", "repo")

    def test_invalid_url_returns_none(self):

        assert _parse_git_url("not-a-url") is None
        assert _parse_git_url("") is None


class TestResolveGitSource:
    """Tests for resolve_git_source with mocked git commands."""

    def test_clone_new_repo(self):

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            src = _make_git_source()
            resolve_cfg = _make_gitlab_resolve_cfg()
            with patch("cypilot.utils.git_utils._run_git", side_effect=_clone_side_effect):
                result = resolve_git_source(src, resolve_cfg, tmp)
                assert result is not None
                assert result == (tmp / ".ws" / "team" / "lib").resolve()

    def test_existing_repo_returns_path_without_network(self):

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            # Pre-create the repo directory
            repo_dir = tmp / ".ws" / "team" / "lib"
            repo_dir.mkdir(parents=True)
            (repo_dir / ".git").mkdir()

            src = _make_git_source()
            resolve_cfg = _make_gitlab_resolve_cfg()
            with patch("cypilot.utils.git_utils._run_git") as mock_git:
                mock_git.return_value = (0, "", "")
                result = resolve_git_source(src, resolve_cfg, tmp)
                assert result is not None
                # Should NOT call any git commands for existing repos
                mock_git.assert_not_called()

    def test_clone_failure_returns_none(self):

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            src = _make_git_source(branch=None)
            resolve_cfg = _make_gitlab_resolve_cfg()
            with patch("cypilot.utils.git_utils._run_git") as mock_git:
                mock_git.return_value = (1, "", "fatal: repo not found")
                result = resolve_git_source(src, resolve_cfg, tmp)
                assert result is None

    def test_no_namespace_rule_uses_default_template(self):

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            src = _make_git_source()
            resolve_cfg = ResolveConfig(namespace=[])  # No rules — uses default {org}/{repo}
            with patch("cypilot.utils.git_utils._run_git", side_effect=_clone_side_effect):
                result = resolve_git_source(src, resolve_cfg, tmp)
                assert result is not None
                assert result == (tmp / ".workspace-sources" / "team" / "lib").resolve()

    def test_unmatched_host_uses_default_fallback(self):
        """When no namespace rule matches the host, default {org}/{repo} template is used."""

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            src = SourceEntry(name="r", path="", url="https://myprivate.gitlab.com/org/sub/repo.git", branch="main")
            resolve_cfg = ResolveConfig(
                workdir=".ws",
                namespace=[NamespaceRule(host="github.com", template="gh/{repo}")],  # No match for myprivate.gitlab.com
            )
            with patch("cypilot.utils.git_utils._run_git", side_effect=_clone_side_effect):
                result = resolve_git_source(src, resolve_cfg, tmp)
                assert result is not None
                # Default fallback: {org}/{repo} → org/sub/repo
                assert result == (tmp / ".ws" / "org/sub" / "repo").resolve()

    def test_deep_path_default_fallback(self):

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            src = SourceEntry(name="r", path="", url="https://mygitlab.example.com/a/b/c/d/e.git", branch="main")
            resolve_cfg = ResolveConfig(namespace=[])  # No rules
            with patch("cypilot.utils.git_utils._run_git", side_effect=_clone_side_effect):
                result = resolve_git_source(src, resolve_cfg, tmp)
                assert result is not None
                # a/b/c/d = org, e = repo → a/b/c/d/e
                assert result == (tmp / ".workspace-sources" / "a" / "b" / "c" / "d" / "e").resolve()


class TestLookupNamespace:
    """Tests for _lookup_namespace exact host matching."""

    def test_exact_match(self):

        rules = [NamespaceRule(host="github.com", template="gh/{repo}")]
        assert _lookup_namespace("github.com", rules).host == "github.com"

    def test_no_match(self):

        rules = [NamespaceRule(host="github.com", template="gh/{repo}")]
        assert _lookup_namespace("gitlab.com", rules) is None

    def test_empty_rules(self):

        assert _lookup_namespace("github.com", []) is None


class TestResolveAdapterContext:
    """Tests for resolve_adapter_context."""

    def test_unreachable_returns_none(self):
        sc = SourceContext(name="x", path=Path("/fake"), role="full", reachable=False)
        assert resolve_adapter_context(sc) is None

    def test_no_adapter_dir_returns_none(self):
        sc = SourceContext(name="x", path=Path("/fake"), role="full", reachable=True, adapter_dir=None)
        assert resolve_adapter_context(sc) is None

    def test_cache_hit(self):
        mock_ctx = MagicMock(spec=CypilotContext)
        sc = SourceContext(
            name="x", path=Path("/fake"), role="full", reachable=True,
            adapter_dir=Path("/fake/.bootstrap"),
            adapter_context=mock_ctx,
            _adapter_resolved=True,
        )
        result = resolve_adapter_context(sc)
        assert result is mock_ctx

    def test_load_failure_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            adapter_dir = Path(tmpdir) / ".bootstrap"
            adapter_dir.mkdir()
            sc = SourceContext(
                name="x", path=Path(tmpdir), role="full", reachable=True,
                adapter_dir=adapter_dir,
            )
            with patch.object(CypilotContext, "load_from_dir", return_value=None):
                result = resolve_adapter_context(sc)
                assert result is None
                assert sc._adapter_resolved is True

    def test_success(self):
        with TemporaryDirectory() as tmpdir:
            adapter_dir = Path(tmpdir) / ".bootstrap"
            adapter_dir.mkdir()
            mock_ctx = MagicMock(spec=CypilotContext)
            sc = SourceContext(
                name="x", path=Path(tmpdir), role="full", reachable=True,
                adapter_dir=adapter_dir,
            )
            with patch.object(CypilotContext, "load_from_dir", return_value=mock_ctx):
                result = resolve_adapter_context(sc)
                assert result is mock_ctx
                assert sc.adapter_context is mock_ctx
                assert sc._adapter_resolved is True


class TestDetermineTargetSource:
    """Tests for determine_target_source."""

    @staticmethod
    def _make_ws_ctx(tmpdir: Path, sources: dict) -> WorkspaceContext:
        primary = _make_mock_ctx(tmpdir, project_root_meta=".")
        return WorkspaceContext(primary=primary, sources=sources)

    def test_file_in_source(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source_dir = tmp / "other-repo"
            source_dir.mkdir()
            target = source_dir / "src" / "main.py"

            sc = SourceContext(name="other", path=source_dir, role="full", reachable=True, _adapter_resolved=True)
            ws = self._make_ws_ctx(tmp, {"other": sc})

            result_sc, result_ctx = determine_target_source(target, ws)
            assert result_sc is sc
            assert result_ctx is ws.primary  # No adapter, falls back

    def test_file_in_primary(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            target = tmp / "src" / "main.py"

            ws = self._make_ws_ctx(tmp, {})
            result_sc, result_ctx = determine_target_source(target, ws)
            assert result_sc is None
            assert result_ctx is ws.primary

    def test_longest_prefix_match(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            outer = tmp / "repos"
            outer.mkdir()
            inner = tmp / "repos" / "specific"
            inner.mkdir()
            target = inner / "file.py"

            sc_outer = SourceContext(name="outer", path=outer, role="full", reachable=True, _adapter_resolved=True)
            sc_inner = SourceContext(name="inner", path=inner, role="full", reachable=True, _adapter_resolved=True)
            ws = self._make_ws_ctx(tmp, {"outer": sc_outer, "inner": sc_inner})

            result_sc, _ = determine_target_source(target, ws)
            assert result_sc is sc_inner  # Inner wins (longer prefix)

    def test_unreachable_source_skipped(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source_dir = tmp / "other"
            source_dir.mkdir()
            target = source_dir / "file.py"

            sc = SourceContext(name="other", path=source_dir, role="full", reachable=False)
            ws = self._make_ws_ctx(tmp, {"other": sc})

            result_sc, _ = determine_target_source(target, ws)
            assert result_sc is None  # Unreachable source skipped

    def test_source_with_adapter_context(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source_dir = tmp / "other"
            source_dir.mkdir()
            adapter_dir = source_dir / ".bootstrap"
            adapter_dir.mkdir()
            target = source_dir / "file.py"

            mock_adapter_ctx = MagicMock(spec=CypilotContext)
            sc = SourceContext(
                name="other", path=source_dir, role="full", reachable=True,
                adapter_dir=adapter_dir,
                adapter_context=mock_adapter_ctx,
                _adapter_resolved=True,
            )
            ws = self._make_ws_ctx(tmp, {"other": sc})

            result_sc, result_ctx = determine_target_source(target, ws)
            assert result_sc is sc
            assert result_ctx is mock_adapter_ctx


# ---------------------------------------------------------------------------
# Tests for _load_reachable_source — error propagation
# ---------------------------------------------------------------------------

class TestLoadReachableSourceMetaError:
    """Ensure broken remote registries record errors on SourceContext."""

    def test_meta_load_error_propagated(self):
        """When load_artifacts_meta returns an error, SourceContext.error must be set."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source_dir = tmp / "remote"
            source_dir.mkdir()
            adapter_dir = source_dir / ".bootstrap"
            adapter_dir.mkdir()
            (adapter_dir / "config").mkdir()

            src = SourceEntry(name="broken", path=str(source_dir))
            with patch(
                "cypilot.utils.context.load_artifacts_meta",
                return_value=(None, "parse error in artifacts.toml"),
            ):
                sc = _load_reachable_source("broken", src, source_dir, adapter_dir)
            assert sc.error is not None
            assert "parse error" in sc.error
            assert sc.meta is None

    def test_meta_load_success_no_error(self):
        """When load_artifacts_meta succeeds, SourceContext.error stays None."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source_dir = tmp / "remote"
            source_dir.mkdir()
            adapter_dir = source_dir / ".bootstrap"
            adapter_dir.mkdir()
            (adapter_dir / "config").mkdir()

            mock_meta = MagicMock(spec=ArtifactsMeta)
            mock_meta.get_all_system_prefixes.return_value = {"sys"}
            src = SourceEntry(name="ok", path=str(source_dir))
            with patch(
                "cypilot.utils.context.load_artifacts_meta",
                return_value=(mock_meta, None),
            ):
                sc = _load_reachable_source("ok", src, source_dir, adapter_dir)
            assert sc.error is None
            assert sc.meta is mock_meta

    def test_invalid_explicit_adapter_no_autodiscovery(self):
        """When explicit_adapter is provided but invalid, must NOT auto-discover."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source_dir = tmp / "remote"
            source_dir.mkdir()

            # Create a valid discoverable adapter inside source_dir
            discoverable = source_dir / ".bootstrap"
            discoverable.mkdir()
            (discoverable / "config").mkdir()

            # Explicit adapter points to a non-existent directory
            bad_adapter = tmp / "bad-adapter"

            src = SourceEntry(name="pinned", path=str(source_dir), adapter=".bad-adapter")
            sc = _load_reachable_source("pinned", src, source_dir, bad_adapter)

            assert sc.error is not None
            assert "Pinned adapter" in sc.error
            assert "pinned" in sc.error
            # Must NOT have picked up the discoverable adapter
            assert sc.adapter_dir is None
            assert sc.meta is None

    def test_meta_error_mentions_adapter_path(self):
        """When load_artifacts_meta fails, error message includes adapter path."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source_dir = tmp / "remote"
            source_dir.mkdir()
            adapter_dir = source_dir / ".bootstrap"
            adapter_dir.mkdir()
            (adapter_dir / "config").mkdir()

            src = SourceEntry(name="broken", path=str(source_dir))
            with patch(
                "cypilot.utils.context.load_artifacts_meta",
                return_value=(None, "bad toml"),
            ):
                sc = _load_reachable_source("broken", src, source_dir, adapter_dir)
            assert sc.error is not None
            assert "adapter:" in sc.error
            assert str(adapter_dir) in sc.error


# ---------------------------------------------------------------------------
# Tests for git_utils — additional coverage
# ---------------------------------------------------------------------------

class TestGitUrlParsingSingleSegment:
    """Cover the single-segment (no org) branch of _parse_git_url."""

    def test_single_segment_returns_empty_org(self):

        result = _parse_git_url("https://gitlab.com/repo.git")
        assert result == ("gitlab.com", "", "repo")


class TestApplyTemplatePathTraversal:
    """Ensure _apply_template rejects unsafe path results."""

    def test_dotdot_in_org_raises(self):
        with pytest.raises(ValueError, match="Unsafe path template"):
            _apply_template("{org}/{repo}", "../../etc", "passwd")

    def test_dotdot_in_repo_raises(self):
        with pytest.raises(ValueError, match="Unsafe path template"):
            _apply_template("{org}/{repo}", "org", "../escape")

    def test_dotdot_in_template_raises(self):
        with pytest.raises(ValueError, match="Unsafe path template"):
            _apply_template("../{repo}", "org", "repo")

    def test_empty_result_raises(self):
        with pytest.raises(ValueError, match="Unsafe path template"):
            _apply_template("{org}", "", "repo")

    def test_normal_template_succeeds(self):
        assert _apply_template("{org}/{repo}", "team", "lib") == "team/lib"

    def test_single_segment_template_succeeds(self):
        assert _apply_template("{repo}", "", "myrepo") == "myrepo"

    def test_empty_org_default_template_strips_slash(self):
        assert _apply_template("{org}/{repo}", "", "myrepo") == "myrepo"


class TestResolveGitSourcePathTraversal:
    """Ensure resolve_git_source rejects URLs that would escape workspace."""

    def test_dotdot_in_url_org_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            src = _make_git_source(url="https://evil.com/../../etc/passwd.git")
            resolve_cfg = ResolveConfig()
            result = resolve_git_source(src, resolve_cfg, tmp)
            assert result is None


class TestRunGit:
    """Tests for _run_git error branches."""

    def test_file_not_found(self):

        with patch("cypilot.utils.git_utils.subprocess.run", side_effect=FileNotFoundError):
            rc, _, err = _run_git(["status"])
            assert rc == 1
            assert "not found" in err

    def test_timeout(self):
        import subprocess as _sp

        with patch("cypilot.utils.git_utils.subprocess.run", side_effect=_sp.TimeoutExpired("git", 120)):
            rc, _, err = _run_git(["clone", "x"])
            assert rc == 1
            assert "timed out" in err


class TestResolveGitSourceEdgeCases:
    """Cover edge-case branches of resolve_git_source."""

    def test_no_url_returns_none(self):

        src = SourceEntry(name="x", path="../local")
        result = resolve_git_source(src, ResolveConfig(), Path("/fake"))
        assert result is None

    def test_unparseable_url_returns_none(self):

        src = SourceEntry(name="x", path="", url="not-a-valid-url")
        result = resolve_git_source(src, ResolveConfig(), Path("/fake"))
        assert result is None

    def test_existing_repo_returns_path_no_git_calls(self):
        """Existing repo returns path without any git commands (no fetch)."""

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_dir = tmp / ".workspace-sources" / "team" / "lib"
            repo_dir.mkdir(parents=True)
            (repo_dir / ".git").mkdir()

            src = _make_git_source()
            resolve_cfg = ResolveConfig()
            with patch("cypilot.utils.git_utils._run_git") as mock_git:
                result = resolve_git_source(src, resolve_cfg, tmp)
                assert result is not None
                assert result == repo_dir.resolve()
                mock_git.assert_not_called()

    def test_existing_repo_with_branch_returns_path_no_git_calls(self):
        """Existing repo with specific branch returns path without git commands."""

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_dir = tmp / ".workspace-sources" / "team" / "lib"
            repo_dir.mkdir(parents=True)
            (repo_dir / ".git").mkdir()

            src = _make_git_source(branch="develop")
            resolve_cfg = ResolveConfig()
            with patch("cypilot.utils.git_utils._run_git") as mock_git:
                result = resolve_git_source(src, resolve_cfg, tmp)
                assert result is not None
                mock_git.assert_not_called()

    def test_default_branch_fallback(self):
        """When source has no branch, use HEAD."""

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            src = _make_git_source(branch=None)
            resolve_cfg = ResolveConfig()
            with patch("cypilot.utils.git_utils._run_git", side_effect=_clone_side_effect) as mock_git:
                result = resolve_git_source(src, resolve_cfg, tmp)
                assert result is not None
                # With branch == HEAD, clone should not have --branch flag
                clone_call = mock_git.call_args_list[0]
                assert "--branch" not in clone_call[0][0]

    def test_single_segment_repo_stays_inside_workspace(self):
        """Empty org must not produce an absolute path that escapes workspace_parent."""

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir).resolve()
            # Single-segment URL → org="" repo="myrepo"
            src = _make_git_source(url="https://gitlab.com/myrepo.git")
            resolve_cfg = ResolveConfig()
            with patch("cypilot.utils.git_utils._run_git", side_effect=_clone_side_effect):
                result = resolve_git_source(src, resolve_cfg, tmp)
                assert result is not None
                # Path must be inside workspace_parent, not an absolute /myrepo
                assert str(result).startswith(str(tmp))


# ---------------------------------------------------------------------------
# Tests for workspace_init command
# ---------------------------------------------------------------------------

class TestIsProjectDir:
    """Tests for workspace_init._is_project_dir."""

    def test_with_git_dir(self):

        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / ".git").mkdir()
            assert _is_project_dir(d) is True

    def test_with_agents_md_marker(self):

        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "AGENTS.md").write_text("<!-- @cpt:root-agents -->\nsome content")
            assert _is_project_dir(d) is True

    def test_agents_md_without_marker(self):

        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "AGENTS.md").write_text("no marker here")
            assert _is_project_dir(d) is False

    def test_no_git_no_agents(self):

        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            assert _is_project_dir(d) is False

    def test_agents_md_not_a_file(self):

        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "AGENTS.md").mkdir()  # directory, not file
            assert _is_project_dir(d) is False


class TestFindAdapterPath:
    """Tests for workspace_init._find_adapter_path."""

    def test_with_cypilot_var(self):

        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            adapter = d / "cypilot"
            adapter.mkdir()
            (adapter / "config").mkdir()
            with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                result = _find_adapter_path(d)
                assert result == "cypilot"

    def test_fallback_find_cypilot_directory(self):

        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            bootstrap = d / ".bootstrap"
            bootstrap.mkdir()
            with patch("cypilot.utils.files._read_cypilot_var", return_value=None):
                with patch("cypilot.utils.files.find_cypilot_directory", return_value=bootstrap):
                    result = _find_adapter_path(d)
                    assert result == ".bootstrap"

    def test_no_adapter_found(self):

        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            with patch("cypilot.utils.files._read_cypilot_var", return_value=None):
                with patch("cypilot.utils.files.find_cypilot_directory", return_value=None):
                    result = _find_adapter_path(d)
                    assert result is None


class TestComputeSourcePath:
    """Tests for workspace_init._compute_source_path."""

    def test_relative(self):

        result = _compute_source_path(Path("/ws/repo-a"), Path("/ws"))
        assert result == "repo-a"

    def test_not_relative(self):

        result = _compute_source_path(Path("/other/repo"), Path("/ws"))
        assert result == "../other/repo"


class TestInferRole:
    """Tests for workspace_init._infer_role."""

    def test_kits_role(self):

        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "kits").mkdir()
            assert _infer_role(d) == "kits"

    def test_artifacts_role(self):

        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "docs").mkdir()
            assert _infer_role(d) == "artifacts"

    def test_codebase_role(self):

        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "src").mkdir()
            assert _infer_role(d) == "codebase"

    def test_full_role(self):

        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "src").mkdir()
            (d / "docs").mkdir()
            assert _infer_role(d) == "full"

    def test_kits_and_docs_returns_full(self):
        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "kits").mkdir()
            (d / "docs").mkdir()
            assert _infer_role(d) == "full"

    def test_kits_and_src_returns_full(self):
        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "kits").mkdir()
            (d / "src").mkdir()
            assert _infer_role(d) == "full"

    def test_empty_dir_full(self):

        with TemporaryDirectory() as tmpdir:
            assert _infer_role(Path(tmpdir)) == "full"


class TestScanNestedRepos:
    """Tests for workspace_init._scan_nested_repos."""

    def test_discovers_repo_with_git_and_adapter(self):

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo = root / "my-repo"
            repo.mkdir()
            (repo / ".git").mkdir()
            adapter = repo / "cypilot"
            adapter.mkdir()
            (adapter / "config").mkdir()
            with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                result = _scan_nested_repos(root, root)
                assert "my-repo" in result
                assert result["my-repo"]["adapter"] == "cypilot"

    def test_skips_hidden_dirs(self):

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            hidden = root / ".hidden"
            hidden.mkdir()
            (hidden / ".git").mkdir()
            result = _scan_nested_repos(root, root)
            assert ".hidden" not in result

    def test_skips_dirs_without_adapter(self):

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo = root / "bare-repo"
            repo.mkdir()
            (repo / ".git").mkdir()
            with patch("cypilot.utils.files._read_cypilot_var", return_value=None):
                with patch("cypilot.utils.files.find_cypilot_directory", return_value=None):
                    result = _scan_nested_repos(root, root)
                    assert "bare-repo" not in result

    def test_empty_dir(self):

        with TemporaryDirectory() as tmpdir:
            result = _scan_nested_repos(Path(tmpdir), Path(tmpdir))
            assert result == {}


class TestWriteStandalone:
    """Tests for workspace_init._write_standalone."""

    def test_success_with_dir(self):

        with TemporaryDirectory() as tmpdir:
            exit_code, data = _write_standalone(Path(tmpdir), {"version": "1.0", "sources": {"a": {"path": "a"}}})
            assert exit_code == 0
            assert data["status"] == "CREATED"
            assert data["sources_count"] == 1

    def test_success_with_file_path(self):

        with TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "ws.toml"
            exit_code, _ = _write_standalone(out, {"version": "1.0", "sources": {}})
            assert exit_code == 0
            assert out.is_file()

    def test_write_error(self):

        exit_code, data = _write_standalone(Path("/nonexistent/dir/ws.toml"), {"sources": {}})
        assert exit_code == 1
        assert data["status"] == "ERROR"


class TestWriteInline:
    """Tests for workspace_init._write_inline."""

    def test_no_cypilot_var(self):

        with TemporaryDirectory() as tmpdir:
            with patch("cypilot.utils.files._read_cypilot_var", return_value=None):
                exit_code, data = _write_inline(Path(tmpdir), {"sources": {}})
                assert exit_code == 1
                assert "cypilot_path" in data.get("message", "")

    def test_success(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_config_dir(root, "[project]\nname = \"test\"\n")
            with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                exit_code, data = _write_inline(root, {"sources": {"a": {"path": "a"}}})
                assert exit_code == 0
                assert data["status"] == "CREATED"



class TestCmdWorkspaceInit:
    """Tests for cmd_workspace_init entry point."""

    def test_no_project_root(self, capsys):

        with patch("cypilot.utils.files.find_project_root", return_value=None):
            rc = cmd_workspace_init([])
            assert rc == 1
            out = capsys.readouterr().out
            assert "ERROR" in out

    def test_scan_root_not_found(self, capsys):

        with TemporaryDirectory() as tmpdir:
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                rc = cmd_workspace_init(["--root", "/nonexistent/path/xyz"])
                assert rc == 1
                out = capsys.readouterr().out
                assert "not found" in out

    def test_no_sources_creates_empty_workspace(self, capsys):

        with TemporaryDirectory() as tmpdir:
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                rc = cmd_workspace_init(["--root", tmpdir])
                assert rc == 0
                out = capsys.readouterr().out
                result = json.loads(out)
                assert result["status"] == "CREATED"
                assert result["sources_count"] == 0

    def test_dry_run(self, capsys):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_repo_with_adapter(root)
            with patch("cypilot.utils.files.find_project_root", return_value=root):
                with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                    rc = cmd_workspace_init(["--root", str(root), "--dry-run"])
                    assert rc == 0
                    out = capsys.readouterr().out
                    assert "DRY_RUN" in out

    def test_standalone_success(self, capsys):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_repo_with_adapter(root)
            with patch("cypilot.utils.files.find_project_root", return_value=root):
                with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                    rc = cmd_workspace_init(["--root", str(root)])
                    assert rc == 0
                    out = capsys.readouterr().out
                    assert "CREATED" in out

    def test_inline_success(self, capsys):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_repo_with_adapter(root)
            with patch("cypilot.utils.files.find_project_root", return_value=root):
                with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                    with patch("cypilot.commands.workspace_init._write_inline", return_value=(0, {"status": "CREATED"})):
                        rc = cmd_workspace_init(["--root", str(root), "--inline"])
                        assert rc == 0

    def test_inline_and_output_mutually_exclusive(self, capsys):

        with TemporaryDirectory() as tmpdir:
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                rc = cmd_workspace_init(["--inline", "--output", str(Path(tmpdir) / "ws.toml")])
                assert rc == 1
                out = capsys.readouterr().out
                assert "mutually exclusive" in out

    def test_write_inline_oserror(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_config_dir(root)
            with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                with patch("cypilot.utils.toml_utils.dump", side_effect=OSError("disk full")):
                    code, data = _write_inline(root, {"version": "1.0", "sources": {}})
                    assert code == 1
                    assert data["status"] == "ERROR"

    def test_output_with_file_path(self, capsys):
        """--output pointing to a file path (not dir) uses parent for relative path computation."""

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            out_file = root / "subdir" / "ws.toml"
            out_file.parent.mkdir(parents=True)
            with patch("cypilot.utils.files.find_project_root", return_value=root):
                rc = cmd_workspace_init(["--root", str(root), "--output", str(out_file)])
                assert rc == 0
                out = capsys.readouterr().out
                assert "CREATED" in out



class TestCmdWorkspaceInitConflictGuard:
    """Tests for workspace-init parallel config and re-init guards."""

    @staticmethod
    def _run_init_with_existing_ws(capsys, argv, *, is_inline=False):
        """Run cmd_workspace_init with a pre-existing workspace mock."""
        with TemporaryDirectory() as tmpdir:
            mock_ws = MagicMock()
            mock_ws.is_inline = is_inline
            mock_ws.workspace_file = Path(tmpdir) / ".cypilot-workspace.toml"
            root = Path(tmpdir)
            with patch("cypilot.utils.files.find_project_root", return_value=root):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(mock_ws, None)):
                    rc = cmd_workspace_init(["--root", str(root)] + argv)
                    out = capsys.readouterr().out
                    return rc, out

    def test_inline_blocked_when_standalone_exists(self, capsys):
        """--inline MUST be rejected when standalone workspace exists (STANDALONE->INLINE illegal)."""
        rc, out = self._run_init_with_existing_ws(capsys, ["--inline"])
        assert rc == 1
        assert "parallel configs" in out
        assert "standalone" in out.lower()

    def test_standalone_blocked_when_inline_exists(self, capsys):
        """Standalone init MUST be rejected when inline workspace exists (INLINE->STANDALONE illegal)."""
        rc, out = self._run_init_with_existing_ws(capsys, [], is_inline=True)
        assert rc == 1
        assert "parallel configs" in out
        assert "inline" in out.lower()

    def test_reinit_blocked_without_force(self, capsys):
        """Re-init of same type MUST be rejected without --force."""
        rc, out = self._run_init_with_existing_ws(capsys, [])
        assert rc == 1
        assert "--force" in out

    def test_reinit_allowed_with_force(self, capsys):
        """Re-init of same type MUST succeed with --force."""
        rc, out = self._run_init_with_existing_ws(capsys, ["--force"])
        assert rc == 0
        assert "CREATED" in out

    def test_cross_type_blocked_even_with_force(self, capsys):
        """Cross-type conflict MUST be rejected even with --force (STANDALONE->INLINE)."""
        rc, out = self._run_init_with_existing_ws(capsys, ["--inline", "--force"])
        assert rc == 1
        assert "parallel configs" in out

    def test_dry_run_skips_guard(self, capsys):
        """--dry-run MUST skip the conflict guard (returns before guard runs)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with patch("cypilot.utils.files.find_project_root", return_value=root):
                rc = cmd_workspace_init(["--root", str(root), "--dry-run"])
                assert rc == 0
                out = capsys.readouterr().out
                assert "DRY_RUN" in out


class TestScanEdgeCases:
    """Edge case tests for workspace_init internal helpers."""

    def test_is_project_dir_agents_oserror(self):

        with TemporaryDirectory() as tmpdir:
            entry = Path(tmpdir)
            agents = entry / "AGENTS.md"
            agents.write_text("<!-- @cpt:root-agents -->")
            with patch.object(Path, "read_text", side_effect=OSError("permission denied")):
                assert _is_project_dir(entry) is False

    def test_find_adapter_path_relative_to_valueerror(self):

        found = Path("/completely/different/path")
        with patch("cypilot.utils.files._read_cypilot_var", return_value=None):
            with patch("cypilot.utils.files.find_cypilot_directory", return_value=found):
                result = _find_adapter_path(Path("/some/entry"))
                assert result == str(found)

    def test_scan_nested_repos_iterdir_oserror(self):

        bad_path = Path("/nonexistent/unreadable")
        result = _scan_nested_repos(bad_path, bad_path)
        assert result == {}

    def test_scan_skips_non_project_dirs(self):

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Create a plain dir (not a project — no .git, no AGENTS.md)
            (root / "plain-dir").mkdir()
            result = _scan_nested_repos(root, root)
            assert "plain-dir" not in result


# ---------------------------------------------------------------------------
# Tests for workspace_info command
# ---------------------------------------------------------------------------

class TestProbeSourceAdapter:
    """Tests for workspace_info._probe_source_adapter."""

    def test_found_by_auto_discovery(self):

        mock_dir = Path("/fake/adapter")
        with patch("cypilot.utils.files.find_cypilot_directory", return_value=mock_dir):
            result = _probe_source_adapter(Path("/fake"), None)
            assert result == mock_dir

    def test_fallback_to_explicit_adapter(self):

        with TemporaryDirectory() as tmpdir:
            adapter = Path(tmpdir) / ".bootstrap"
            adapter.mkdir()
            (adapter / "config").mkdir()
            with patch("cypilot.utils.files.find_cypilot_directory", return_value=None):
                result = _probe_source_adapter(Path(tmpdir), adapter)
                assert result == adapter

    def test_none_found(self):

        with patch("cypilot.utils.files.find_cypilot_directory", return_value=None):
            result = _probe_source_adapter(Path("/fake"), None)
            assert result is None


class TestBuildSourceInfo:
    """Tests for workspace_info._build_source_info."""

    def test_reachable_source(self):

        with TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / "repo"
            src_dir.mkdir()
            ws_cfg = _make_docs_ws_cfg(tmpdir, src_dir)
            with patch("cypilot.commands.workspace_info._probe_source_adapter", return_value=None):
                info = _build_source_info(ws_cfg, "docs")
                assert info["reachable"] is True
                assert info["adapter_found"] is False

    def test_unreachable_source(self):

        ws_cfg = WorkspaceConfig(
            sources={"x": SourceEntry(name="x", path="/nonexistent/repo", role="full")},
            workspace_file=Path("/fake/.cypilot-workspace.toml"),
        )
        info = _build_source_info(ws_cfg, "x")
        assert info["reachable"] is False
        assert "warning" in info

    def test_source_with_url_and_branch(self):

        ws_cfg = WorkspaceConfig(
            sources={"r": SourceEntry(name="r", path="/nonexistent", url="https://x.com/a/b.git", branch="main", role="codebase")},
            workspace_file=Path("/fake/.cypilot-workspace.toml"),
        )
        info = _build_source_info(ws_cfg, "r")
        assert info["url"] == "https://x.com/a/b.git"
        assert info["branch"] == "main"


class TestEnrichWithArtifactCounts:
    """Tests for workspace_info._enrich_with_artifact_counts."""

    def test_success(self):

        mock_meta = MagicMock()
        mock_meta.iter_all_artifacts.return_value = [1, 2, 3]
        mock_meta.systems = ["sys1"]
        with patch("cypilot.utils.artifacts_meta.load_artifacts_meta", return_value=(mock_meta, None)):
            info: dict = {}
            _enrich_with_artifact_counts(info, Path("/fake"))
            assert info["artifact_count"] == 3
            assert info["system_count"] == 1

    def test_exception_ignored(self):

        with patch("cypilot.utils.artifacts_meta.load_artifacts_meta", side_effect=RuntimeError("boom")):
            info: dict = {}
            _enrich_with_artifact_counts(info, Path("/fake"))
            assert "artifact_count" not in info
            assert info["metadata_error"] == "boom"



class TestCmdWorkspaceInfo:
    """Tests for cmd_workspace_info entry point."""

    def test_no_project_root(self, capsys):

        with patch("cypilot.utils.files.find_project_root", return_value=None):
            rc = cmd_workspace_info([])
            assert rc == 1
            out = capsys.readouterr().out
            assert "No project root" in out

    def test_workspace_error(self, capsys):

        with TemporaryDirectory() as tmpdir:
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(None, "parse error")):
                    rc = cmd_workspace_info([])
                    assert rc == 1
                    out = capsys.readouterr().out
                    assert "parse error" in out

    def test_no_workspace(self, capsys):

        with TemporaryDirectory() as tmpdir:
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(None, None)):
                    rc = cmd_workspace_info([])
                    assert rc == 1
                    out = capsys.readouterr().out
                    assert '"status": "ERROR"' in out

    def test_workspace_found(self, capsys):

        with TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / "repo"
            src_dir.mkdir()
            ws_cfg = _make_docs_ws_cfg(tmpdir, src_dir)
            rc, data = _run_workspace_info(capsys, ws_cfg, tmpdir)
            assert rc == 0
            assert data["status"] == "OK"
            assert data["sources_count"] == 1
            assert data["context_loaded"] is False


# ---------------------------------------------------------------------------
# Tests for workspace_add command
# ---------------------------------------------------------------------------


class TestCmdWorkspaceAddValidation:
    """Tests for cmd_workspace_add argument validation."""

    def test_missing_path_and_url(self):

        with pytest.raises(SystemExit) as exc_info:
            cmd_workspace_add(["--name", "test"])
        assert exc_info.value.code == 2

    def test_inline_with_url_rejected(self, capsys):

        rc = cmd_workspace_add(["--name", "test", "--url", "https://x.com/a/b.git", "--inline"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "not supported in inline" in out

    def test_no_project_root(self, capsys):

        with patch("cypilot.utils.files.find_project_root", return_value=None):
            rc = cmd_workspace_add(["--name", "test", "--path", "../repo"])
            assert rc == 1
            out = capsys.readouterr().out
            assert "No project root" in out

    def test_invalid_source_name_rejected(self, capsys):
        rc = cmd_workspace_add(["--name", "foo/bar", "--path", "../repo"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "Invalid source name" in out

    def test_source_name_with_spaces_rejected(self, capsys):
        rc = cmd_workspace_add(["--name", "my repo", "--path", "../repo"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "Invalid source name" in out


class TestCmdWorkspaceAddStandalone:
    """Tests for workspace-add with standalone workspace."""

    def test_add_to_standalone_success(self, capsys):
        with TemporaryDirectory() as tmpdir:
            ws_cfg = _make_standalone_ws_mock(tmpdir)
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    rc = cmd_workspace_add(["--name", "docs", "--path", "../docs", "--role", "artifacts"])
                    assert rc == 0
                    data = _parse_json(capsys)
                    assert data["status"] == "ADDED"
                    assert data["source"]["name"] == "docs"

    def test_add_standalone_save_error(self, capsys):
        with TemporaryDirectory() as tmpdir:
            ws_cfg = _make_standalone_ws_mock(tmpdir)
            ws_cfg.save.return_value = "write failed"
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    rc = cmd_workspace_add(["--name", "x", "--path", "../x"])
                    assert rc == 1
                    out = capsys.readouterr().out
                    assert "write failed" in out

    def test_add_with_url_and_branch(self, capsys):
        with TemporaryDirectory() as tmpdir:
            ws_cfg = _make_standalone_ws_mock(tmpdir)
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    rc = cmd_workspace_add(["--name", "lib", "--url", "https://x.com/a/b.git", "--branch", "main"])
                    assert rc == 0
                    data = _parse_json(capsys)
                    assert data["source"]["url"] == "https://x.com/a/b.git"
                    assert data["source"]["branch"] == "main"

    def test_no_workspace_found(self, capsys):

        with TemporaryDirectory() as tmpdir:
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(None, None)):
                    rc = cmd_workspace_add(["--name", "x", "--path", "../x"])
                    assert rc == 1
                    out = capsys.readouterr().out
                    assert "workspace-init" in out



class TestCmdWorkspaceAddInline:
    """Tests for workspace-add with inline workspace."""

    def test_inline_flag_with_existing_standalone_rejected(self, capsys):
        with TemporaryDirectory() as tmpdir:
            ws_cfg = _make_standalone_ws_mock(tmpdir)
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    rc = cmd_workspace_add(["--name", "x", "--path", "../x", "--inline"])
                    assert rc == 1
                    out = capsys.readouterr().out
                    assert "Standalone workspace already exists" in out

    def test_inline_flag_no_existing_ws(self, capsys):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_config_dir(root)
            with patch("cypilot.utils.files.find_project_root", return_value=root):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(None, None)):
                    with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                        rc = cmd_workspace_add(["--name", "docs", "--path", "../docs", "--inline"])
                        assert rc == 0
                        data = _parse_json(capsys)
                        assert data["status"] == "ADDED"

    def test_auto_detect_inline_workspace(self, capsys):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_config_dir(root)
            ws_cfg = MagicMock()
            ws_cfg.is_inline = True
            with patch("cypilot.utils.files.find_project_root", return_value=root):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                        rc = cmd_workspace_add(["--name", "docs", "--path", "../docs"])
                        assert rc == 0

    def test_auto_detect_inline_rejects_url(self, capsys):

        with TemporaryDirectory() as tmpdir:
            ws_cfg = MagicMock()
            ws_cfg.is_inline = True
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    rc = cmd_workspace_add(["--name", "x", "--url", "https://x.com/a/b.git"])
                    assert rc == 1
                    out = capsys.readouterr().out
                    assert "not supported in inline" in out



class TestAddToInline:
    """Tests for workspace_add._add_to_inline."""

    def test_rejects_url_args(self, capsys):
        args = _make_inline_args(path="", url="https://github.com/org/repo.git")
        with TemporaryDirectory() as tmpdir:
            rc = _add_to_inline(args, Path(tmpdir))
            assert rc == 1
            data = _parse_json(capsys)
            assert data["status"] == "ERROR"
            assert "not supported in inline" in data["message"]

    def test_no_cypilot_var(self, capsys):
        args = _make_inline_args()
        with TemporaryDirectory() as tmpdir:
            with patch("cypilot.utils.files._read_cypilot_var", return_value=None):
                rc = _add_to_inline(args, Path(tmpdir))
                assert rc == 1
                out = capsys.readouterr().out
                assert "cypilot_path" in out

    def test_workspace_as_string_reference(self, capsys):
        args = _make_inline_args()
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cd = _setup_config_dir(root)
            toml_utils.dump({"workspace": "../ws.toml"}, cd / "core.toml")
            with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                rc = _add_to_inline(args, root)
                assert rc == 1
                out = capsys.readouterr().out
                assert "external file reference" in out

    def test_success_with_non_full_role(self, capsys):
        args = _make_inline_args(name="docs", path="../docs", role="artifacts", adapter=".boot")
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_config_dir(root)
            with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                rc = _add_to_inline(args, root)
                assert rc == 0
                data = _parse_json(capsys)
                assert data["source"]["role"] == "artifacts"

    def test_replace_existing_source_requires_force(self, capsys):
        args = _make_inline_args(name="docs", path="../docs", force=False)
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cd = _setup_config_dir(root)
            toml_utils.dump({"workspace": {"version": "1.0", "sources": {"docs": {"path": "../old"}}}}, cd / "core.toml")
            with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                rc = _add_to_inline(args, root)
                assert rc == 1
                data = _parse_json(capsys)
                assert data["status"] == "ERROR"
                assert "already exists" in data["message"]
                assert "--force" in data["message"]

    def test_replace_existing_source_with_force_and_branch(self, capsys):
        args = _make_inline_args(name="docs", path="../docs", branch="main", force=True)
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cd = _setup_config_dir(root)
            toml_utils.dump({"workspace": {"version": "1.0", "sources": {"docs": {"path": "../old"}}}}, cd / "core.toml")
            with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                rc = _add_to_inline(args, root)
                assert rc == 0
                data = _parse_json(capsys)
                assert data["status"] == "ADDED"
                assert data["replaced"] is True
                assert data["source"]["branch"] == "main"

    def test_fallback_to_core_toml_no_config_dir(self, capsys):
        """When config/core.toml doesn't exist, falls back to {adapter}/core.toml."""
        args = _make_inline_args()
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "cypilot").mkdir()
            with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                rc = _add_to_inline(args, root)
                assert rc == 0

    def test_malformed_workspace_sources_type(self, capsys):
        """Malformed workspace.sources (not dict) in core.toml returns error."""
        args = _make_inline_args()
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cd = _setup_config_dir(root)
            toml_utils.dump({"workspace": {"version": "1.0", "sources": 42}}, cd / "core.toml")
            with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                rc = _add_to_inline(args, root)
                assert rc == 1
                out = capsys.readouterr().out
                assert "Malformed" in out
                assert "workspace.sources" in out

    def test_workspace_not_dict_type(self, capsys):
        """When workspace key is not string/dict but some other type, return error."""
        args = _make_inline_args()
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cd = _setup_config_dir(root)
            toml_utils.dump({"workspace": 42}, cd / "core.toml")
            with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                rc = _add_to_inline(args, root)
                assert rc == 1
                out = capsys.readouterr().out
                assert "Malformed" in out

    def test_toml_dump_oserror(self, capsys):
        """OSError when writing toml returns error."""


        args = _make_inline_args()
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_config_dir(root)
            with patch("cypilot.utils.files._read_cypilot_var", return_value="cypilot"):
                with patch("cypilot.utils.toml_utils.dump", side_effect=OSError("disk full")):
                    rc = _add_to_inline(args, root)
                    assert rc == 1
                    out = capsys.readouterr().out
                    assert "Failed to write" in out



class TestAddToStandaloneEdgeCases:
    """Edge case tests for _add_to_standalone."""

    def test_replace_existing_source_requires_force(self, capsys):
        """Replacing an existing source without --force returns error."""
        ws_cfg = MagicMock()
        ws_cfg.sources = {"docs": SourceEntry(name="docs", path="../old")}
        args = argparse.Namespace(name="docs", path="../new-docs", role="full", adapter=None, url=None, branch=None, force=False)
        rc = _add_to_standalone(args, ws_cfg)
        assert rc == 1
        data = _parse_json(capsys)
        assert data["status"] == "ERROR"
        assert "already exists" in data["message"]
        assert "--force" in data["message"]

    def test_replace_existing_source_with_force(self, capsys):
        """Replacing an existing source with --force marks replaced=True."""
        ws_cfg = MagicMock()
        ws_cfg.sources = {"docs": SourceEntry(name="docs", path="../old")}
        ws_cfg.save.return_value = None
        ws_cfg.workspace_file = Path("/fake/ws.toml")
        args = argparse.Namespace(name="docs", path="../new-docs", role="full", adapter=None, url=None, branch=None, force=True)
        rc = _add_to_standalone(args, ws_cfg)
        assert rc == 0
        data = _parse_json(capsys)
        assert data["replaced"] is True
        assert "updated in" in data["message"]


# ---------------------------------------------------------------------------
# Human-friendly formatter tests
# ---------------------------------------------------------------------------

class TestHumanWorkspaceInfo:
    """Tests for _human_workspace_info formatter."""

    def test_ok_status(self):

        data = {
            "status": "OK",
            "config_path": "/fake/ws.toml",
            "version": "1.0",
            "is_inline": False,
            "sources_count": 2,
            "traceability": {"cross_repo": True, "resolve_remote_ids": False},
            "context_loaded": True,
            "reachable_sources": 1,
            "total_registered_systems": 3,
            "sources": [
                {
                    "name": "docs",
                    "role": "artifacts",
                    "reachable": True,
                    "url": "https://x.com/a.git",
                    "path": "../docs",
                    "adapter": ".bootstrap",
                    "artifact_count": 5,
                    "system_count": 2,
                },
                {
                    "name": "code",
                    "role": "full",
                    "reachable": False,
                    "path": "../code",
                    "warning": "Source directory not reachable",
                },
            ],
            "config_warnings": ["duplicate source name"],
        }
        # Should not raise
        _human_workspace_info(data)

    def test_error_status(self):

        data = {
            "status": "ERROR",
            "message": "No workspace found",
            "sources": [],
        }
        _human_workspace_info(data)

    def test_unknown_status(self):

        data = {"status": "UNKNOWN", "sources": []}
        _human_workspace_info(data)

    def test_inline_type(self):

        data = {
            "status": "OK",
            "is_inline": True,
            "sources_count": 0,
            "sources": [],
            "traceability": {},
        }
        _human_workspace_info(data)

    def test_no_context_loaded(self):

        data = {
            "status": "OK",
            "sources": [],
            "context_loaded": False,
        }
        _human_workspace_info(data)


class TestHumanWorkspaceAdd:
    """Tests for _human_workspace_add formatter."""

    def test_added_status(self):

        data = {
            "status": "ADDED",
            "message": "Source 'docs' added to workspace",
            "config_path": "/fake/ws.toml",
            "source": {
                "name": "docs",
                "path": "../docs",
                "role": "artifacts",
                "adapter": ".bootstrap",
                "branch": "main",
            },
        }
        _human_workspace_add(data)

    def test_replaced_status(self):

        data = {
            "status": "ADDED",
            "message": "Source 'docs' updated in workspace",
            "replaced": True,
            "source": {"name": "docs", "url": "https://x.com/a.git"},
        }
        _human_workspace_add(data)

    def test_error_status(self):

        data = {
            "status": "ERROR",
            "message": "No workspace found",
            "source": {},
        }
        _human_workspace_add(data)

    def test_unknown_status(self):

        data = {"status": "UNKNOWN", "message": "something", "source": {}}
        _human_workspace_add(data)

    def test_no_source_no_config(self):

        data = {"status": "ADDED", "message": "ok"}
        _human_workspace_add(data)


class TestHumanWorkspaceInit:
    """Tests for _human_workspace_init formatter."""

    def test_created_status(self):

        data = {
            "status": "CREATED",
            "message": "Workspace config created at /fake/ws.toml",
            "config_path": "/fake/ws.toml",
            "sources_count": 2,
            "sources": ["repo-a", "repo-b"],
            "workspace": {
                "sources": {
                    "repo-a": {"path": "repo-a", "role": "full"},
                    "repo-b": {"path": "repo-b", "role": "codebase"},
                },
            },
        }
        _human_workspace_init(data)

    def test_dry_run_status(self):

        data = {
            "status": "DRY_RUN",
            "message": "Would generate workspace config",
            "sources_count": 1,
            "sources": ["repo-a"],
            "workspace": {"sources": {"repo-a": {"path": "repo-a", "role": "full"}}},
        }
        _human_workspace_init(data)

    def test_error_status(self):

        data = {
            "status": "ERROR",
            "message": "No project root found",
            "sources": [],
        }
        _human_workspace_init(data)

    def test_unknown_status(self):

        data = {"status": "UNKNOWN", "message": "hmm", "sources": []}
        _human_workspace_init(data)

    def test_no_sources(self):

        data = {
            "status": "CREATED",
            "message": "Empty workspace",
            "config_path": "/fake/ws.toml",
            "sources_count": 0,
            "sources": [],
        }
        _human_workspace_init(data)


# ---------------------------------------------------------------------------
# Additional coverage for workspace_info cmd edge cases
# ---------------------------------------------------------------------------


class TestCmdWorkspaceInfoEdgeCases:
    """Additional edge-case tests for cmd_workspace_info."""

    def teardown_method(self):
        set_context(None)

    def test_workspace_with_config_warnings(self, capsys):
        """Config validation warnings are included in output."""

        with TemporaryDirectory() as tmpdir:
            ws_cfg = WorkspaceConfig(
                sources={"bad": SourceEntry(name="bad", path="", role="full")},
                workspace_file=Path(tmpdir) / ".cypilot-workspace.toml",
            )
            rc, data = _run_workspace_info(capsys, ws_cfg, tmpdir)
            assert rc == 0
            assert "config_warnings" in data

    def test_workspace_with_workspace_context(self, capsys):
        """When get_context returns WorkspaceContext, context_loaded=True."""

        with TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / "repo"
            src_dir.mkdir()
            ws_cfg = _make_docs_ws_cfg(tmpdir, src_dir)
            primary = _make_mock_ctx(Path(tmpdir), project_root_meta=".")
            sc = SourceContext(name="repo", path=src_dir, role="full", reachable=True, registered_systems={"sys1"})
            ws_ctx = WorkspaceContext(primary=primary, sources={"repo": sc})
            rc, data = _run_workspace_info(capsys, ws_cfg, tmpdir, ctx_return=ws_ctx)
            assert rc == 0
            assert data["context_loaded"] is True
            assert data["reachable_sources"] == 1

    def test_build_source_info_with_adapter_found(self):
        """_build_source_info enriches info when adapter is found."""

        with TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / "repo"
            src_dir.mkdir()
            adapter = src_dir / ".bootstrap"
            adapter.mkdir()
            ws_cfg = _make_docs_ws_cfg(tmpdir, src_dir)
            mock_meta = MagicMock()
            mock_meta.iter_all_artifacts.return_value = [1, 2]
            mock_meta.systems = ["s1"]
            with patch("cypilot.commands.workspace_info._probe_source_adapter", return_value=adapter):
                with patch("cypilot.utils.artifacts_meta.load_artifacts_meta", return_value=(mock_meta, None)):
                    info = _build_source_info(ws_cfg, "docs")
                    assert info["adapter_found"] is True
                    assert info["artifact_count"] == 2

    def test_enrich_with_artifact_counts_meta_error(self):
        """_enrich_with_artifact_counts handles meta error (err set)."""

        with patch("cypilot.utils.artifacts_meta.load_artifacts_meta", return_value=(None, "parse error")):
            info: dict = {}
            _enrich_with_artifact_counts(info, Path("/fake"))
            assert "artifact_count" not in info
            assert info["metadata_error"] == "parse error"


# ---------------------------------------------------------------------------
# Tests for sync_git_source
# ---------------------------------------------------------------------------

class TestSyncGitSource:
    """Tests for sync_git_source."""

    def test_sync_success_with_branch(self):
        """Sync fetches and checks out branch."""

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_dir = tmp / ".workspace-sources" / "team" / "lib"
            repo_dir.mkdir(parents=True)
            (repo_dir / ".git").mkdir()

            src = _make_git_source(branch="main")
            resolve_cfg = ResolveConfig()

            def side_effect(args, cwd=None):
                if args[0] == "clone":
                    Path(args[-1]).mkdir(parents=True, exist_ok=True)
                    (Path(args[-1]) / ".git").mkdir(exist_ok=True)
                return (0, "", "")

            with patch("cypilot.utils.git_utils._run_git", side_effect=side_effect) as mock_git:
                result = sync_git_source(src, resolve_cfg, tmp)
                assert result["status"] == "synced"
                # Verify fetch was called with origin and branch
                calls = [c[0][0] for c in mock_git.call_args_list]
                assert any("fetch" in args and "origin" in args for args in calls)
                # Verify checkout -B was called
                assert any("checkout" in args and "-B" in args for args in calls)

    def test_sync_success_head_mode(self):
        """Sync with HEAD uses reset --hard FETCH_HEAD."""

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_dir = tmp / ".workspace-sources" / "team" / "lib"
            repo_dir.mkdir(parents=True)
            (repo_dir / ".git").mkdir()

            src = _make_git_source(branch=None)
            resolve_cfg = ResolveConfig()

            with patch("cypilot.utils.git_utils._run_git") as mock_git:
                mock_git.return_value = (0, "", "")
                result = sync_git_source(src, resolve_cfg, tmp)
                assert result["status"] == "synced"
                calls = [c[0][0] for c in mock_git.call_args_list]
                assert any("reset" in args and "FETCH_HEAD" in args for args in calls)

    def test_sync_fetch_failure(self):
        """Sync reports failure when fetch fails."""

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_dir = tmp / ".workspace-sources" / "team" / "lib"
            repo_dir.mkdir(parents=True)
            (repo_dir / ".git").mkdir()

            src = _make_git_source()
            resolve_cfg = ResolveConfig()

            def side_effect(args, cwd=None):
                if "status" in args and "--porcelain" in args:
                    return (0, "", "")
                return (1, "", "network error")

            with patch("cypilot.utils.git_utils._run_git", side_effect=side_effect):
                result = sync_git_source(src, resolve_cfg, tmp)
                assert result["status"] == "failed"
                assert "fetch failed" in result["error"]

    def test_sync_update_failure(self):
        """Sync reports failure when checkout -B fails."""

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_dir = tmp / ".workspace-sources" / "team" / "lib"
            repo_dir.mkdir(parents=True)
            (repo_dir / ".git").mkdir()

            src = _make_git_source(branch="main")
            resolve_cfg = ResolveConfig()

            def side_effect(args, cwd=None):
                if "status" in args and "--porcelain" in args:
                    return (0, "", "")
                if "fetch" in args:
                    return (0, "", "")
                return (1, "", "checkout error")

            with patch("cypilot.utils.git_utils._run_git", side_effect=side_effect):
                result = sync_git_source(src, resolve_cfg, tmp)
                assert result["status"] == "failed"
                assert "update failed" in result["error"]

    def test_sync_resolve_failure(self):
        """Sync reports failure when URL cannot be resolved."""

        src = SourceEntry(name="x", path="", url="not-a-valid-url")
        result = sync_git_source(src, ResolveConfig(), Path("/fake"))
        assert result["status"] == "failed"
        assert "resolve failed" in result["error"]

    def test_sync_no_url(self):
        """Sync reports failure when source has no URL."""

        src = SourceEntry(name="x", path="../local")
        result = sync_git_source(src, ResolveConfig(), Path("/fake"))
        assert result["status"] == "failed"

    def test_sync_aborts_on_dirty_worktree(self):
        """Sync aborts with error when worktree has uncommitted changes."""

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_dir = tmp / ".workspace-sources" / "team" / "lib"
            repo_dir.mkdir(parents=True)
            (repo_dir / ".git").mkdir()

            src = _make_git_source(branch="main")
            resolve_cfg = ResolveConfig()

            def side_effect(args, cwd=None):
                if "status" in args and "--porcelain" in args:
                    return (0, " M dirty-file.txt\n", "")
                if args[0] == "clone":
                    Path(args[-1]).mkdir(parents=True, exist_ok=True)
                    (Path(args[-1]) / ".git").mkdir(exist_ok=True)
                return (0, "", "")

            with patch("cypilot.utils.git_utils._run_git", side_effect=side_effect):
                result = sync_git_source(src, resolve_cfg, tmp)
                assert result["status"] == "failed"
                assert "dirty worktree" in result["error"]

    def test_sync_force_bypasses_dirty_check(self):
        """Sync proceeds when worktree is dirty and force=True."""

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_dir = tmp / ".workspace-sources" / "team" / "lib"
            repo_dir.mkdir(parents=True)
            (repo_dir / ".git").mkdir()

            src = _make_git_source(branch="main")
            resolve_cfg = ResolveConfig()

            def side_effect(args, cwd=None):
                if "status" in args and "--porcelain" in args:
                    return (0, " M dirty-file.txt\n", "")
                if args[0] == "clone":
                    Path(args[-1]).mkdir(parents=True, exist_ok=True)
                    (Path(args[-1]) / ".git").mkdir(exist_ok=True)
                return (0, "", "")

            with patch("cypilot.utils.git_utils._run_git", side_effect=side_effect):
                result = sync_git_source(src, resolve_cfg, tmp, force=True)
                assert result["status"] == "synced"

    def test_sync_clean_worktree_proceeds(self):
        """Sync proceeds when worktree is clean without force."""

        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo_dir = tmp / ".workspace-sources" / "team" / "lib"
            repo_dir.mkdir(parents=True)
            (repo_dir / ".git").mkdir()

            src = _make_git_source(branch="main")
            resolve_cfg = ResolveConfig()

            def side_effect(args, cwd=None):
                if "status" in args and "--porcelain" in args:
                    return (0, "", "")
                if args[0] == "clone":
                    Path(args[-1]).mkdir(parents=True, exist_ok=True)
                    (Path(args[-1]) / ".git").mkdir(exist_ok=True)
                return (0, "", "")

            with patch("cypilot.utils.git_utils._run_git", side_effect=side_effect):
                result = sync_git_source(src, resolve_cfg, tmp)
                assert result["status"] == "synced"


class TestIsWorktreeDirty:
    """Tests for is_worktree_dirty helper."""

    def test_clean_worktree(self):
        with patch("cypilot.utils.git_utils._run_git", return_value=(0, "", "")):
            assert not is_worktree_dirty(Path("/fake"))

    def test_dirty_worktree(self):
        with patch("cypilot.utils.git_utils._run_git", return_value=(0, " M file.txt\n", "")):
            assert is_worktree_dirty(Path("/fake"))

    def test_git_error_assumes_dirty(self):
        with patch("cypilot.utils.git_utils._run_git", return_value=(1, "", "error")):
            assert is_worktree_dirty(Path("/fake"))


# ---------------------------------------------------------------------------
# Tests for workspace-sync command
# ---------------------------------------------------------------------------

def _make_git_ws_cfg(tmpdir, sources=None):
    """Create a WorkspaceConfig with git URL sources for sync tests."""
    if sources is None:
        sources = {
            "remote-repo": SourceEntry(name="remote-repo", path="", url="https://gitlab.com/team/lib.git", branch="main"),
        }
    ws_file = Path(tmpdir) / ".cypilot-workspace.toml"
    ws_file.touch()
    return WorkspaceConfig(sources=sources, workspace_file=ws_file)


class TestCmdWorkspaceSync:
    """Tests for cmd_workspace_sync command."""

    def test_no_project_root(self, capsys):
        with patch("cypilot.utils.files.find_project_root", return_value=None):
            rc = cmd_workspace_sync([])
        assert rc == 1
        data = _parse_json(capsys)
        assert data["status"] == "ERROR"

    def test_no_workspace(self, capsys):
        with TemporaryDirectory() as tmpdir:
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(None, None)):
                    rc = cmd_workspace_sync([])
        assert rc == 1
        data = _parse_json(capsys)
        assert data["status"] == "ERROR"

    def test_source_not_found(self, capsys):
        with TemporaryDirectory() as tmpdir:
            ws_cfg = _make_git_ws_cfg(tmpdir)
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    rc = cmd_workspace_sync(["--source", "nonexistent"])
        assert rc == 1
        data = _parse_json(capsys)
        assert data["status"] == "ERROR"
        assert "available" in data

    def test_source_no_url(self, capsys):
        with TemporaryDirectory() as tmpdir:
            sources = {"local": SourceEntry(name="local", path="../local", role="full")}
            ws_cfg = _make_git_ws_cfg(tmpdir, sources=sources)
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    rc = cmd_workspace_sync(["--source", "local"])
        assert rc == 1
        data = _parse_json(capsys)
        assert "no Git URL" in data["message"]

    def test_no_git_sources(self, capsys):
        with TemporaryDirectory() as tmpdir:
            sources = {"local": SourceEntry(name="local", path="../local", role="full")}
            ws_cfg = _make_git_ws_cfg(tmpdir, sources=sources)
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    rc = cmd_workspace_sync([])
        assert rc == 0
        data = _parse_json(capsys)
        assert data["synced"] == 0

    def test_dry_run(self, capsys):
        with TemporaryDirectory() as tmpdir:
            ws_cfg = _make_git_ws_cfg(tmpdir)
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    rc = cmd_workspace_sync(["--dry-run"])
        assert rc == 0
        data = _parse_json(capsys)
        assert data["status"] == "DRY_RUN"
        assert len(data["sources"]) == 1

    def test_sync_success(self, capsys):
        with TemporaryDirectory() as tmpdir:
            ws_cfg = _make_git_ws_cfg(tmpdir)
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    with patch("cypilot.utils.git_utils.sync_git_source", return_value={"status": "synced"}):
                        rc = cmd_workspace_sync([])
        assert rc == 0
        data = _parse_json(capsys)
        assert data["status"] == "OK"
        assert data["synced"] == 1
        assert data["failed"] == 0

    def test_sync_failure(self, capsys):
        with TemporaryDirectory() as tmpdir:
            ws_cfg = _make_git_ws_cfg(tmpdir)
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    with patch("cypilot.utils.git_utils.sync_git_source", return_value={"status": "failed", "error": "network error"}):
                        rc = cmd_workspace_sync([])
        assert rc == 2
        data = _parse_json(capsys)
        assert data["status"] == "FAIL"
        assert data["failed"] == 1

    def test_sync_single_source(self, capsys):
        with TemporaryDirectory() as tmpdir:
            sources = {
                "repo1": SourceEntry(name="repo1", path="", url="https://gitlab.com/t/a.git", branch="main"),
                "repo2": SourceEntry(name="repo2", path="", url="https://gitlab.com/t/b.git", branch="dev"),
            }
            ws_cfg = _make_git_ws_cfg(tmpdir, sources=sources)
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    with patch("cypilot.utils.git_utils.sync_git_source", return_value={"status": "synced"}) as mock_sync:
                        rc = cmd_workspace_sync(["--source", "repo1"])
        assert rc == 0
        # Only one call to sync
        assert mock_sync.call_count == 1

    def test_workspace_error_message(self, capsys):
        with TemporaryDirectory() as tmpdir:
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(None, "parse error")):
                    rc = cmd_workspace_sync([])
        assert rc == 1
        data = _parse_json(capsys)
        assert data["status"] == "ERROR"
        assert "parse error" in data["message"]

    def test_sync_mixed_results(self, capsys):
        with TemporaryDirectory() as tmpdir:
            sources = {
                "good": SourceEntry(name="good", path="", url="https://gitlab.com/t/a.git", branch="main"),
                "bad": SourceEntry(name="bad", path="", url="https://gitlab.com/t/b.git", branch="dev"),
            }
            ws_cfg = _make_git_ws_cfg(tmpdir, sources=sources)

            def sync_side_effect(src, cfg, base, **kwargs):
                if getattr(src, "name", "") == "good":
                    return {"status": "synced"}
                return {"status": "failed", "error": "network error"}

            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    with patch("cypilot.utils.git_utils.sync_git_source", side_effect=sync_side_effect):
                        rc = cmd_workspace_sync([])
        assert rc == 0
        data = _parse_json(capsys)
        assert data["status"] == "OK"
        assert data["synced"] == 1
        assert data["failed"] == 1

    def test_force_flag_passed_to_sync(self, capsys):
        """The --force flag is forwarded to sync_git_source."""
        with TemporaryDirectory() as tmpdir:
            ws_cfg = _make_git_ws_cfg(tmpdir)
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    with patch("cypilot.utils.git_utils.sync_git_source", return_value={"status": "synced"}) as mock_sync:
                        rc = cmd_workspace_sync(["--force"])
        assert rc == 0
        # Verify force=True was passed
        assert mock_sync.call_args[1]["force"] is True

    def test_no_force_flag_default(self, capsys):
        """Without --force, force=False is passed to sync_git_source."""
        with TemporaryDirectory() as tmpdir:
            ws_cfg = _make_git_ws_cfg(tmpdir)
            with patch("cypilot.utils.files.find_project_root", return_value=Path(tmpdir)):
                with patch("cypilot.utils.workspace.find_workspace_config", return_value=(ws_cfg, None)):
                    with patch("cypilot.utils.git_utils.sync_git_source", return_value={"status": "synced"}) as mock_sync:
                        rc = cmd_workspace_sync([])
        assert rc == 0
        assert mock_sync.call_args[1]["force"] is False


class TestHumanWorkspaceSync:
    """Tests for _human_workspace_sync formatter."""

    def test_dry_run_status(self):

        data = {
            "status": "DRY_RUN",
            "message": "Would sync the following Git URL sources",
            "sources": [
                {"name": "repo-a", "url": "https://gitlab.com/t/a.git", "branch": "main"},
                {"name": "repo-b", "url": "https://gitlab.com/t/b.git", "branch": None},
            ],
        }
        _human_workspace_sync(data)

    def test_ok_status_with_results(self):

        data = {
            "status": "OK",
            "synced": 2,
            "failed": 0,
            "results": [
                {"name": "repo-a", "status": "synced"},
                {"name": "repo-b", "status": "synced"},
            ],
        }
        _human_workspace_sync(data)

    def test_fail_status(self):

        data = {
            "status": "FAIL",
            "synced": 0,
            "failed": 1,
            "results": [
                {"name": "repo-a", "status": "failed", "error": "network error"},
            ],
        }
        _human_workspace_sync(data)

    def test_mixed_results(self):

        data = {
            "status": "OK",
            "synced": 1,
            "failed": 1,
            "results": [
                {"name": "repo-a", "status": "synced"},
                {"name": "repo-b", "status": "failed", "error": "git fetch failed"},
            ],
        }
        _human_workspace_sync(data)

    def test_no_results_with_message(self):

        data = {
            "status": "OK",
            "message": "No Git URL sources to sync",
            "synced": 0,
            "failed": 0,
            "results": [],
        }
        _human_workspace_sync(data)


# ---------------------------------------------------------------------------
# Tests for peek_git_source_path
# ---------------------------------------------------------------------------

from cypilot.utils.git_utils import peek_git_source_path


class TestPeekGitSourcePath:
    """Tests for peek_git_source_path (no network I/O)."""

    def test_happy_path_returns_expected_local_path(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            src = _make_git_source()
            result = peek_git_source_path(src, ResolveConfig(), tmp)
            assert result is not None
            assert "team/lib" in str(result)

    def test_no_url_returns_none(self):
        src = SourceEntry(name="x", path="../local")
        result = peek_git_source_path(src, ResolveConfig(), Path("/fake"))
        assert result is None

    def test_unparseable_url_returns_none(self):
        src = SourceEntry(name="x", path="", url="not-a-url")
        result = peek_git_source_path(src, ResolveConfig(), Path("/fake"))
        assert result is None

    def test_unsafe_template_returns_none(self):
        src = _make_git_source(url="https://evil.com/../../etc/passwd.git")
        result = peek_git_source_path(src, ResolveConfig(), Path("/fake"))
        assert result is None

    def test_with_namespace_rule(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            src = _make_git_source()
            resolve_cfg = _make_gitlab_resolve_cfg(workdir=".ws")
            result = peek_git_source_path(src, resolve_cfg, tmp)
            assert result is not None
            assert ".ws" in str(result)

    def test_single_segment_repo(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            src = _make_git_source(url="https://gitlab.com/myrepo.git")
            result = peek_git_source_path(src, ResolveConfig(), tmp)
            assert result is not None
            assert "myrepo" in str(result)


# ---------------------------------------------------------------------------
# Tests for _clone_if_missing edge cases
# ---------------------------------------------------------------------------

from cypilot.utils.git_utils import _clone_if_missing


class TestCloneOrFetchEdgeCases:
    """Cover _clone_if_missing branches not reached via resolve_git_source."""

    def test_unparseable_url_returns_none(self):
        with TemporaryDirectory() as td:
            result = _clone_if_missing("not-a-url", Path(td) / "nonexistent", "HEAD")
        assert result is None

    def test_clone_failure_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "repo"
            with patch("cypilot.utils.git_utils._run_git", return_value=(1, "", "clone error")):
                result = _clone_if_missing("https://gitlab.com/org/repo.git", target, "main")
                assert result is None


# ---------------------------------------------------------------------------
# Tests for _run_git success path
# ---------------------------------------------------------------------------


class TestRunGitSuccess:
    """Cover the happy path of _run_git (subprocess.run succeeds)."""

    def test_success_returns_output(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"
        mock_result.stderr = ""
        with patch("cypilot.utils.git_utils.subprocess.run", return_value=mock_result):
            rc, out, err = _run_git(["status"])
            assert rc == 0
            assert out == "ok"
            assert err == ""


# ---------------------------------------------------------------------------
# Tests for sync_git_source — not a git repo
# ---------------------------------------------------------------------------


class TestSyncGitSourceNotRepo:
    """Cover sync_git_source when resolved path exists but is not a git repo."""

    def test_dir_without_git_returns_failed(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            no_git_dir = tmp / "not-a-repo"
            no_git_dir.mkdir(parents=True)
            # No .git directory — should hit "not a git repo" branch

            src = _make_git_source()
            resolve_cfg = ResolveConfig()
            with patch("cypilot.utils.git_utils.resolve_git_source", return_value=no_git_dir):
                result = sync_git_source(src, resolve_cfg, tmp)
                assert result["status"] == "failed"
                assert "not a git repo" in result["error"]


class TestDetermineTargetSourcePrefixMatching:
    """Tests for determine_target_source() — longest-prefix path matching."""

    @staticmethod
    def _make_ws(tmpdir, sources_spec):
        """Build a WorkspaceContext with given sources.

        sources_spec: list of (name, relative_path, reachable, has_adapter) tuples.
        """
        primary = _make_mock_ctx(tmpdir)
        sources = {}
        for name, rel, reachable, has_adapter in sources_spec:
            p = (tmpdir / rel).resolve()
            p.mkdir(parents=True, exist_ok=True)
            sc = SourceContext(
                name=name,
                path=p,
                reachable=reachable,
                adapter_dir=p / ".bootstrap" if has_adapter else None,
            )
            # Pre-set _adapter_resolved so resolve_adapter_context won't hit filesystem
            sc._adapter_resolved = True
            if has_adapter:
                sc.adapter_context = CypilotContext(
                    adapter_dir=p / ".bootstrap",
                    project_root=p,
                    meta=_make_mock_meta(".."),
                    kits={},
                    registered_systems=set(),
                )
            sources[name] = sc
        return WorkspaceContext(primary=primary, sources=sources)

    def test_exact_match(self, tmp_path):
        """Target at source root matches that source."""
        ws = self._make_ws(tmp_path, [("repo", "repo", True, False)])
        target = tmp_path / "repo" / "file.md"
        target.touch()
        sc, _ = determine_target_source(target, ws)
        assert sc is not None
        assert sc.name == "repo"

    def test_prefix_match(self, tmp_path):
        """Target nested inside source matches that source."""
        ws = self._make_ws(tmp_path, [("repo", "repo", True, False)])
        sub = tmp_path / "repo" / "sub" / "deep"
        sub.mkdir(parents=True)
        target = sub / "file.md"
        target.touch()
        sc, _ = determine_target_source(target, ws)
        assert sc is not None
        assert sc.name == "repo"

    def test_no_match_returns_primary(self, tmp_path):
        """Target outside all sources returns (None, primary)."""
        ws = self._make_ws(tmp_path, [("repo", "repo", True, False)])
        other = tmp_path / "unrelated"
        other.mkdir()
        target = other / "file.md"
        target.touch()
        sc, ctx = determine_target_source(target, ws)
        assert sc is None
        assert ctx is ws.primary

    def test_longest_prefix_wins(self, tmp_path):
        """Overlapping sources: longer path wins."""
        ws = self._make_ws(tmp_path, [
            ("parent", "org/repo", True, False),
            ("child", "org/repo/sub", True, False),
        ])
        target = tmp_path / "org" / "repo" / "sub" / "file.md"
        target.touch()
        sc, _ = determine_target_source(target, ws)
        assert sc is not None
        assert sc.name == "child"

    def test_unreachable_source_skipped(self, tmp_path):
        """Unreachable sources are skipped, fallback to primary."""
        ws = self._make_ws(tmp_path, [("repo", "repo", False, False)])
        target = tmp_path / "repo" / "file.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
        sc, ctx = determine_target_source(target, ws)
        assert sc is None
        assert ctx is ws.primary

    def test_none_path_source_skipped(self, tmp_path):
        """Sources with path=None are skipped."""
        primary = _make_mock_ctx(tmp_path)
        sc_none = SourceContext(name="ghost", path=None, reachable=True)
        ws = WorkspaceContext(primary=primary, sources={"ghost": sc_none})
        target = tmp_path / "anything.md"
        target.touch()
        matched, ctx = determine_target_source(target, ws)
        assert matched is None
        assert ctx is ws.primary

    def test_adapter_context_returned_when_present(self, tmp_path):
        """When source has adapter, returns adapter context instead of primary."""
        ws = self._make_ws(tmp_path, [("repo", "repo", True, True)])
        target = tmp_path / "repo" / "file.md"
        target.touch()
        sc, ctx = determine_target_source(target, ws)
        assert sc is not None
        assert sc.name == "repo"
        assert ctx is sc.adapter_context
        assert ctx is not ws.primary

    def test_no_adapter_returns_primary(self, tmp_path):
        """When source has no adapter, returns primary context."""
        ws = self._make_ws(tmp_path, [("repo", "repo", True, False)])
        target = tmp_path / "repo" / "file.md"
        target.touch()
        sc, ctx = determine_target_source(target, ws)
        assert sc is not None
        assert ctx is ws.primary


# =========================================================================
# get_expanded_meta — None return path (RL-010)
# =========================================================================

class TestGetExpandedMetaNone:
    """get_expanded_meta returns None when adapter resolution fails."""

    def test_returns_none_when_adapter_resolved_but_no_context_and_no_meta(self):
        """When adapter was already resolved to None and meta is None, returns None."""
        sc = SourceContext(
            name="broken",
            path=Path("/nonexistent"),
            reachable=True,
            meta=None,
            role="full",
        )
        sc._adapter_resolved = True
        sc.adapter_context = None
        result = get_expanded_meta(sc)
        assert result is None

    def test_returns_meta_when_adapter_resolved_but_no_context(self):
        """When adapter resolved to None but source has meta, returns source meta."""
        mock_meta = MagicMock(spec=ArtifactsMeta)
        sc = SourceContext(
            name="partial",
            path=Path("/some/path"),
            reachable=True,
            meta=mock_meta,
            role="full",
        )
        sc._adapter_resolved = True
        sc.adapter_context = None
        result = get_expanded_meta(sc)
        assert result is mock_meta

    def test_returns_adapter_meta_when_adapter_context_exists(self):
        """When adapter context exists, returns its meta."""
        adapter_meta = MagicMock(spec=ArtifactsMeta)
        adapter_ctx = MagicMock()
        adapter_ctx.meta = adapter_meta
        sc = SourceContext(
            name="good",
            path=Path("/some/path"),
            reachable=True,
            meta=MagicMock(spec=ArtifactsMeta),
            role="full",
        )
        sc._adapter_resolved = True
        sc.adapter_context = adapter_ctx
        result = get_expanded_meta(sc)
        assert result is adapter_meta
