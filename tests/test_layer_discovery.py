"""Tests for Walk-Up Layer Discovery.

Covers: discover_layers(), _load_kit_layers(), _load_repo_layer(),
_detect_master_repo(), _is_master_repo_boundary().
"""
from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from cypilot.utils.layer_discovery import (
    discover_layers,
    _load_kit_layers,
    _load_master_layer,
    _load_repo_layer,
    _detect_master_repo,
    _is_master_repo_boundary,
)
from cypilot.utils.manifest import ManifestLayer, ManifestLayerState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_V2_MANIFEST = """\
[manifest]
version = "2.0"
"""

_INVALID_MANIFEST = """\
this is not valid toml ===
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _make_core_toml(config_dir: Path, kits: dict[str, Path]) -> None:
    """Write a core.toml with kit registrations pointing to given paths."""
    lines = ['version = "1.0"\n', "project_root = ..\n", "\n[kits]\n"]
    for slug, kit_path in kits.items():
        lines.append(f"[kits.{slug}]\n")
        lines.append(f'path = "{kit_path.as_posix()}"\n')
        lines.append('format = "Cypilot"\n')
        lines.append('version = "1.0.0"\n')
    (config_dir / "core.toml").write_text("".join(lines))


# ---------------------------------------------------------------------------
# _is_master_repo_boundary
# ---------------------------------------------------------------------------

class TestIsMasterRepoBoundary:
    def test_claude_md_and_skills_dir(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "CLAUDE.md").write_text("marker")
            (d / "skills").mkdir()
            assert _is_master_repo_boundary(d) is True

    def test_git_dir(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / ".git").mkdir()
            assert _is_master_repo_boundary(d) is True

    def test_only_claude_md_no_skills(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "CLAUDE.md").write_text("marker")
            assert _is_master_repo_boundary(d) is False

    def test_only_skills_no_claude_md(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "skills").mkdir()
            assert _is_master_repo_boundary(d) is False

    def test_empty_dir(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            assert _is_master_repo_boundary(d) is False


# ---------------------------------------------------------------------------
# _detect_master_repo
# ---------------------------------------------------------------------------

class TestDetectMasterRepo:
    def test_returns_none_when_no_master_repo(self):
        with TemporaryDirectory() as tmp:
            # sub/project structure but no .git, no CLAUDE.md+skills
            project = Path(tmp) / "sub" / "project"
            project.mkdir(parents=True)
            result = _detect_master_repo(project)
            assert result is None

    def test_finds_git_boundary_one_level_up(self):
        with TemporaryDirectory() as tmp:
            master = Path(tmp) / "master"
            master.mkdir()
            (master / ".git").mkdir()
            repo = master / "sub" / "project"
            repo.mkdir(parents=True)
            result = _detect_master_repo(repo)
            assert result == master

    def test_finds_claude_md_skills_boundary(self):
        with TemporaryDirectory() as tmp:
            master = Path(tmp) / "master"
            master.mkdir()
            (master / "CLAUDE.md").write_text("marker")
            (master / "skills").mkdir()
            repo = master / "inner" / "repo"
            repo.mkdir(parents=True)
            result = _detect_master_repo(repo)
            assert result == master

    def test_does_not_find_itself(self):
        """repo_root itself should not count as master repo."""
        with TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            (repo / ".git").mkdir()
            # repo is the start, walk starts from parent so .git in repo
            # itself should not be returned as master repo
            result = _detect_master_repo(repo)
            # Walk starts at repo.parent; if tmp has no markers, returns None
            assert result is None

    def test_stops_at_first_boundary(self):
        with TemporaryDirectory() as tmp:
            outer = Path(tmp) / "outer"
            outer.mkdir()
            (outer / ".git").mkdir()
            inner = outer / "inner"
            inner.mkdir()
            (inner / ".git").mkdir()
            repo = inner / "project"
            repo.mkdir(parents=True)
            # Walk from repo.parent=inner upward; inner has .git so stops there
            result = _detect_master_repo(repo)
            assert result == inner


# ---------------------------------------------------------------------------
# _load_repo_layer
# ---------------------------------------------------------------------------

class TestLoadRepoLayer:
    def test_returns_none_when_no_manifest(self):
        with TemporaryDirectory() as tmp:
            cypilot_root = Path(tmp)
            (cypilot_root / "config").mkdir()
            result = _load_repo_layer(cypilot_root)
            assert result is None

    def test_returns_loaded_layer_for_valid_manifest(self):
        with TemporaryDirectory() as tmp:
            cypilot_root = Path(tmp)
            config_dir = cypilot_root / "config"
            config_dir.mkdir()
            _write(config_dir / "manifest.toml", _VALID_V2_MANIFEST)
            result = _load_repo_layer(cypilot_root)
            assert result is not None
            assert result.scope == "repo"
            assert result.state == ManifestLayerState.LOADED
            assert result.manifest is not None

    def test_returns_parse_error_for_invalid_manifest(self):
        with TemporaryDirectory() as tmp:
            cypilot_root = Path(tmp)
            config_dir = cypilot_root / "config"
            config_dir.mkdir()
            _write(config_dir / "manifest.toml", _INVALID_MANIFEST)
            result = _load_repo_layer(cypilot_root)
            assert result is not None
            assert result.scope == "repo"
            assert result.state == ManifestLayerState.PARSE_ERROR
            assert result.manifest is None


# ---------------------------------------------------------------------------
# _load_kit_layers
# ---------------------------------------------------------------------------

class TestLoadKitLayers:
    def test_returns_empty_when_no_core_toml(self):
        with TemporaryDirectory() as tmp:
            cypilot_root = Path(tmp)
            (cypilot_root / "config").mkdir()
            result = _load_kit_layers(cypilot_root)
            assert result == []

    def test_loads_kit_layer_with_manifest(self):
        with TemporaryDirectory() as tmp:
            cypilot_root = Path(tmp) / "cypilot"
            kit_dir = Path(tmp) / "mykit"
            kit_dir.mkdir(parents=True)
            (cypilot_root / "config").mkdir(parents=True)
            _write(kit_dir / "manifest.toml", _VALID_V2_MANIFEST)

            # Write core.toml manually with absolute path
            core_content = f"""\
version = "1.0"

[kits]
[kits.mykit]
path = "{kit_dir.as_posix()}"
format = "Cypilot"
version = "1.0.0"
"""
            (cypilot_root / "config" / "core.toml").write_text(core_content)

            result = _load_kit_layers(cypilot_root)
            assert len(result) == 1
            assert result[0].scope == "kit"
            assert result[0].state == ManifestLayerState.LOADED

    def test_omits_kit_without_manifest(self):
        with TemporaryDirectory() as tmp:
            cypilot_root = Path(tmp) / "cypilot"
            kit_dir = Path(tmp) / "emptykit"
            kit_dir.mkdir(parents=True)
            (cypilot_root / "config").mkdir(parents=True)

            core_content = f"""\
version = "1.0"

[kits]
[kits.emptykit]
path = "{kit_dir.as_posix()}"
format = "Cypilot"
version = "1.0.0"
"""
            (cypilot_root / "config" / "core.toml").write_text(core_content)

            result = _load_kit_layers(cypilot_root)
            assert result == []

    def test_returns_empty_on_invalid_core_toml(self):
        """Invalid TOML in core.toml returns empty list (exception path)."""
        with TemporaryDirectory() as tmp:
            cypilot_root = Path(tmp) / "cypilot"
            (cypilot_root / "config").mkdir(parents=True)
            (cypilot_root / "config" / "core.toml").write_text("this is not === valid toml")

            result = _load_kit_layers(cypilot_root)
            assert result == []

    def test_returns_empty_when_kits_not_a_dict(self):
        """When kits section is not a dict (e.g., list), returns empty list."""
        with TemporaryDirectory() as tmp:
            cypilot_root = Path(tmp) / "cypilot"
            (cypilot_root / "config").mkdir(parents=True)
            # kits as a list instead of dict
            (cypilot_root / "config" / "core.toml").write_text('version = "1.0"\nkits = ["a", "b"]\n')

            result = _load_kit_layers(cypilot_root)
            assert result == []

    def test_skips_kit_entry_not_a_dict(self):
        """Kit entry that is not a dict is skipped."""
        with TemporaryDirectory() as tmp:
            cypilot_root = Path(tmp) / "cypilot"
            (cypilot_root / "config").mkdir(parents=True)
            # mykit entry is a string, not a table
            (cypilot_root / "config" / "core.toml").write_text('version = "1.0"\n[kits]\nmykit = "badentry"\n')

            result = _load_kit_layers(cypilot_root)
            assert result == []

    def test_skips_kit_entry_with_empty_path(self):
        """Kit entry with no path field is skipped."""
        with TemporaryDirectory() as tmp:
            cypilot_root = Path(tmp) / "cypilot"
            (cypilot_root / "config").mkdir(parents=True)
            (cypilot_root / "config" / "core.toml").write_text(
                'version = "1.0"\n[kits]\n[kits.mykit]\nformat = "Cypilot"\n'
            )

            result = _load_kit_layers(cypilot_root)
            assert result == []

    def test_returns_parse_error_for_invalid_kit_manifest(self):
        """Kit with invalid manifest.toml returns PARSE_ERROR layer."""
        with TemporaryDirectory() as tmp:
            cypilot_root = Path(tmp) / "cypilot"
            kit_dir = Path(tmp) / "badkit"
            kit_dir.mkdir(parents=True)
            (cypilot_root / "config").mkdir(parents=True)
            _write(kit_dir / "manifest.toml", _INVALID_MANIFEST)

            core_content = f"""\
version = "1.0"

[kits]
[kits.badkit]
path = "{kit_dir.as_posix()}"
format = "Cypilot"
version = "1.0.0"
"""
            (cypilot_root / "config" / "core.toml").write_text(core_content)

            result = _load_kit_layers(cypilot_root)
            assert len(result) == 1
            assert result[0].scope == "kit"
            assert result[0].state == ManifestLayerState.PARSE_ERROR
            assert result[0].manifest is None

    def test_resolves_relative_kit_path(self):
        """Kit path given as relative path is resolved against cypilot_root."""
        with TemporaryDirectory() as tmp:
            cypilot_root = Path(tmp) / "cypilot"
            kit_dir = cypilot_root / "kits" / "mykit"
            kit_dir.mkdir(parents=True)
            (cypilot_root / "config").mkdir(parents=True)
            _write(kit_dir / "manifest.toml", _VALID_V2_MANIFEST)

            # Use relative path in core.toml
            core_content = """\
version = "1.0"

[kits]
[kits.mykit]
path = "kits/mykit"
format = "Cypilot"
version = "1.0.0"
"""
            (cypilot_root / "config" / "core.toml").write_text(core_content)

            result = _load_kit_layers(cypilot_root)
            assert len(result) == 1
            assert result[0].scope == "kit"
            assert result[0].state == ManifestLayerState.LOADED


# ---------------------------------------------------------------------------
# _load_master_layer
# ---------------------------------------------------------------------------

class TestLoadMasterLayer:
    def test_returns_none_when_no_manifest(self):
        """Returns None if master repo has no manifest.toml."""
        with TemporaryDirectory() as tmp:
            master_root = Path(tmp)
            result = _load_master_layer(master_root)
            assert result is None

    def test_returns_loaded_layer_for_valid_manifest(self):
        """Returns LOADED layer for a valid manifest.toml at master root."""
        with TemporaryDirectory() as tmp:
            master_root = Path(tmp)
            _write(master_root / "manifest.toml", _VALID_V2_MANIFEST)
            result = _load_master_layer(master_root)
            assert result is not None
            assert result.scope == "master"
            assert result.state == ManifestLayerState.LOADED

    def test_returns_parse_error_for_invalid_manifest(self):
        """Returns PARSE_ERROR layer if master manifest.toml is invalid."""
        with TemporaryDirectory() as tmp:
            master_root = Path(tmp)
            _write(master_root / "manifest.toml", _INVALID_MANIFEST)
            result = _load_master_layer(master_root)
            assert result is not None
            assert result.scope == "master"
            assert result.state == ManifestLayerState.PARSE_ERROR
            assert result.manifest is None


# ---------------------------------------------------------------------------
# discover_layers — integration
# ---------------------------------------------------------------------------

class TestDiscoverLayers:
    def test_standalone_repo_returns_repo_only_no_kit(self):
        """Standalone repo with no master repo and no kits returns only repo layer."""
        with TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "project"
            repo_root.mkdir()
            cypilot_root = repo_root / ".bootstrap"
            config_dir = cypilot_root / "config"
            config_dir.mkdir(parents=True)
            _write(config_dir / "manifest.toml", _VALID_V2_MANIFEST)

            layers = discover_layers(repo_root, cypilot_root)
            scopes = [l.scope for l in layers]
            assert "repo" in scopes
            assert "master" not in scopes

    def test_repo_under_master_repo_returns_master_and_repo(self):
        """Repo under master repo returns master + repo layers in order."""
        with TemporaryDirectory() as tmp:
            master = Path(tmp) / "master"
            master.mkdir()
            (master / ".git").mkdir()
            _write(master / "manifest.toml", _VALID_V2_MANIFEST)

            repo_root = master / "inner" / "project"
            repo_root.mkdir(parents=True)
            cypilot_root = repo_root / ".bootstrap"
            config_dir = cypilot_root / "config"
            config_dir.mkdir(parents=True)
            _write(config_dir / "manifest.toml", _VALID_V2_MANIFEST)

            layers = discover_layers(repo_root, cypilot_root)
            scopes = [l.scope for l in layers]
            assert "master" in scopes
            assert "repo" in scopes
            # master comes before repo
            assert scopes.index("master") < scopes.index("repo")

    def test_missing_repo_manifest_silently_omitted(self):
        """Missing manifest at repo layer is silently omitted."""
        with TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "project"
            repo_root.mkdir()
            cypilot_root = repo_root / ".bootstrap"
            config_dir = cypilot_root / "config"
            config_dir.mkdir(parents=True)
            # No manifest.toml written

            layers = discover_layers(repo_root, cypilot_root)
            scopes = [l.scope for l in layers]
            assert "repo" not in scopes

    def test_parse_error_results_in_parse_error_state(self):
        """Parse error at repo manifest results in PARSE_ERROR state layer."""
        with TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "project"
            repo_root.mkdir()
            cypilot_root = repo_root / ".bootstrap"
            config_dir = cypilot_root / "config"
            config_dir.mkdir(parents=True)
            _write(config_dir / "manifest.toml", _INVALID_MANIFEST)

            layers = discover_layers(repo_root, cypilot_root)
            repo_layers = [l for l in layers if l.scope == "repo"]
            assert len(repo_layers) == 1
            assert repo_layers[0].state == ManifestLayerState.PARSE_ERROR

    def test_master_repo_boundary_detected_by_claude_md_and_skills(self):
        """Master repo detection works with CLAUDE.md + skills/ pattern."""
        with TemporaryDirectory() as tmp:
            master = Path(tmp) / "master"
            master.mkdir()
            (master / "CLAUDE.md").write_text("marker")
            (master / "skills").mkdir()
            _write(master / "manifest.toml", _VALID_V2_MANIFEST)

            repo_root = master / "sub" / "project"
            repo_root.mkdir(parents=True)
            cypilot_root = repo_root / ".bootstrap"
            (cypilot_root / "config").mkdir(parents=True)

            layers = discover_layers(repo_root, cypilot_root)
            scopes = [l.scope for l in layers]
            assert "master" in scopes

    def test_walk_up_stops_at_master_repo_root(self):
        """Walk-up stops at master repo root, does not traverse beyond."""
        with TemporaryDirectory() as tmp:
            # outer has a marker but master (closer) should be found first
            outer = Path(tmp) / "outer"
            outer.mkdir()
            (outer / ".git").mkdir()
            _write(outer / "manifest.toml", _VALID_V2_MANIFEST)

            master = outer / "master"
            master.mkdir()
            (master / ".git").mkdir()
            _write(master / "manifest.toml", _VALID_V2_MANIFEST)

            repo_root = master / "inner" / "project"
            repo_root.mkdir(parents=True)
            cypilot_root = repo_root / ".bootstrap"
            (cypilot_root / "config").mkdir(parents=True)

            layers = discover_layers(repo_root, cypilot_root)
            master_layers = [l for l in layers if l.scope == "master"]
            assert len(master_layers) == 1
            # The master layer found should be the closer one (master dir)
            assert master_layers[0].path == master / "manifest.toml"

    def test_resolution_order_kit_master_repo(self):
        """Resolution order is: kit, master, repo (outermost to innermost)."""
        with TemporaryDirectory() as tmp:
            master = Path(tmp) / "master"
            master.mkdir()
            (master / ".git").mkdir()
            _write(master / "manifest.toml", _VALID_V2_MANIFEST)

            repo_root = master / "project"
            repo_root.mkdir()
            cypilot_root = repo_root / ".bootstrap"
            config_dir = cypilot_root / "config"
            config_dir.mkdir(parents=True)
            _write(config_dir / "manifest.toml", _VALID_V2_MANIFEST)

            # Add a kit
            kit_dir = Path(tmp) / "mykit"
            kit_dir.mkdir()
            _write(kit_dir / "manifest.toml", _VALID_V2_MANIFEST)
            core_content = f"""\
version = "1.0"

[kits]
[kits.mykit]
path = "{kit_dir.as_posix()}"
format = "Cypilot"
version = "1.0.0"
"""
            (config_dir / "core.toml").write_text(core_content)

            layers = discover_layers(repo_root, cypilot_root)
            scopes = [l.scope for l in layers]
            assert scopes.index("kit") < scopes.index("master")
            assert scopes.index("master") < scopes.index("repo")
