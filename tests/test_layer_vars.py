"""
Tests for add_layer_variables() and assemble_component() in resolve_vars.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.commands.resolve_vars import add_layer_variables, assemble_component
from cypilot.utils.manifest import (
    AgentEntry,
    ManifestLayer,
    ManifestLayerState,
    ManifestV2,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_layer(
    scope: str,
    path: str,
    state: ManifestLayerState = ManifestLayerState.LOADED,
    agents=None,
) -> ManifestLayer:
    manifest = ManifestV2(
        version="2.0",
        agents=agents or [],
    )
    return ManifestLayer(
        scope=scope,
        path=Path(path),
        manifest=manifest,
        state=state,
    )


def _make_master_layer(master_root: str) -> ManifestLayer:
    """Create a loaded master-scope layer at master_root/manifest.toml."""
    return _make_layer("master", f"{master_root}/manifest.toml")


def _make_repo_layer(cypilot_root: str) -> ManifestLayer:
    """Create a loaded repo-scope layer at cypilot_root/config/manifest.toml."""
    return _make_layer("repo", f"{cypilot_root}/config/manifest.toml")


# ---------------------------------------------------------------------------
# add_layer_variables — with master repo present
# ---------------------------------------------------------------------------

class TestAddLayerVariablesWithMasterRepo:
    """Layer variables when master repo is in the layer list."""

    def test_base_dir_is_master_repo_root(self):
        """base_dir points to the master repo root when master layer present."""
        layers = [
            _make_master_layer("/workspace/master"),
            _make_repo_layer("/workspace/master/child-repo/.bootstrap"),
        ]
        repo_root = Path("/workspace/master/child-repo")
        result = add_layer_variables({}, layers, repo_root)
        assert result["base_dir"] == "/workspace/master"

    def test_master_repo_set_to_master_root(self):
        """master_repo is set to the master repo directory."""
        layers = [
            _make_master_layer("/workspace/master"),
            _make_repo_layer("/workspace/master/child-repo/.bootstrap"),
        ]
        repo_root = Path("/workspace/master/child-repo")
        result = add_layer_variables({}, layers, repo_root)
        assert result["master_repo"] == "/workspace/master"

    def test_repo_set_to_repo_root(self):
        """repo variable always reflects the resolved repo_root."""
        layers = [
            _make_master_layer("/workspace/master"),
        ]
        repo_root = Path("/workspace/master/child-repo")
        result = add_layer_variables({}, layers, repo_root)
        assert result["repo"] == repo_root.resolve().as_posix()


# ---------------------------------------------------------------------------
# add_layer_variables — without master repo (standalone)
# ---------------------------------------------------------------------------

class TestAddLayerVariablesStandalone:
    """Layer variables when no master repo layer is present."""

    def test_base_dir_falls_back_to_repo_root(self):
        """base_dir equals repo root when no master layer."""
        layers = [
            _make_repo_layer("/home/user/myproject/.bootstrap"),
        ]
        repo_root = Path("/home/user/myproject")
        result = add_layer_variables({}, layers, repo_root)
        assert result["base_dir"] == repo_root.resolve().as_posix()

    def test_master_repo_is_empty_string_when_absent(self):
        """master_repo is empty string when no master layer is discovered."""
        layers = [
            _make_repo_layer("/home/user/myproject/.bootstrap"),
        ]
        repo_root = Path("/home/user/myproject")
        result = add_layer_variables({}, layers, repo_root)
        assert result["master_repo"] == ""

    def test_empty_layers_still_sets_repo(self):
        """Even with no layers, repo variable is set from repo_root."""
        repo_root = Path("/home/user/standalone")
        result = add_layer_variables({}, [], repo_root)
        assert result["repo"] == repo_root.resolve().as_posix()
        assert result["master_repo"] == ""
        assert result["base_dir"] == repo_root.resolve().as_posix()


# ---------------------------------------------------------------------------
# add_layer_variables — layer vars don't override system variables
# ---------------------------------------------------------------------------

class TestLayerVarsDoNotOverrideSystem:
    """Existing system/kit variables take priority over layer-derived vars."""

    def test_existing_repo_not_overridden(self):
        """Pre-existing 'repo' key is preserved (first-writer-wins)."""
        existing_vars = {"repo": "/already/set/repo"}
        layers = [_make_repo_layer("/some/bootstrap")]
        repo_root = Path("/other/path")
        result = add_layer_variables(existing_vars, layers, repo_root)
        assert result["repo"] == "/already/set/repo"

    def test_existing_base_dir_not_overridden(self):
        """Pre-existing 'base_dir' key is preserved."""
        existing_vars = {"base_dir": "/pinned/base"}
        layers = [_make_master_layer("/master")]
        repo_root = Path("/child")
        result = add_layer_variables(existing_vars, layers, repo_root)
        assert result["base_dir"] == "/pinned/base"

    def test_other_system_vars_preserved(self):
        """Unrelated system variables (cypilot_path, project_root) are untouched."""
        existing_vars = {
            "cypilot_path": "/project/.bootstrap",
            "project_root": "/project",
        }
        layers = [_make_repo_layer("/project/.bootstrap")]
        repo_root = Path("/project")
        result = add_layer_variables(existing_vars, layers, repo_root)
        assert result["cypilot_path"] == "/project/.bootstrap"
        assert result["project_root"] == "/project"


# ---------------------------------------------------------------------------
# assemble_component — determinism
# ---------------------------------------------------------------------------

class TestAssembleComponentDeterminism:
    """assemble_component() is a pure function."""

    def test_same_inputs_produce_same_output(self):
        """Calling assemble_component() twice with same args returns identical strings."""
        layers = [_make_repo_layer("/proj/.bootstrap")]
        variables = {"repo": "/proj", "base_dir": "/proj"}
        source = "Hello from {repo}."

        result1 = assemble_component("my-agent", source, layers, variables, "claude")
        result2 = assemble_component("my-agent", source, layers, variables, "claude")
        assert result1 == result2

    def test_empty_layers_no_appends(self):
        """With no layers, content is returned unchanged (after substitution)."""
        result = assemble_component("c1", "base content", [], {}, "agent")
        assert result == "base content"


# ---------------------------------------------------------------------------
# assemble_component — variable substitution
# ---------------------------------------------------------------------------

class TestAssembleComponentVariableSubstitution:
    """Variable substitution in assembled content."""

    def test_variable_substituted(self):
        """Template variables are replaced by their values."""
        variables = {"repo": "/home/user/project"}
        result = assemble_component("c1", "Repo is at {repo}.", [], variables, "agent")
        assert result == "Repo is at /home/user/project."

    def test_multiple_variables_substituted(self):
        """Multiple distinct variables all substituted."""
        variables = {"base_dir": "/base", "repo": "/base/child"}
        result = assemble_component(
            "c1", "{base_dir} contains {repo}.", [], variables, "agent"
        )
        assert result == "/base contains /base/child."

    def test_unknown_variable_left_intact(self):
        """Unknown {variable} references are left as-is (no KeyError)."""
        variables = {"known": "value"}
        result = assemble_component("c1", "{known} and {unknown}.", [], variables, "agent")
        assert result == "value and {unknown}."

    def test_no_variables_content_unchanged(self):
        """Content with no template markers is returned unchanged."""
        result = assemble_component("c1", "Plain content.", [], {}, "agent")
        assert result == "Plain content."


# ---------------------------------------------------------------------------
# assemble_component — section appends
# ---------------------------------------------------------------------------

class TestAssembleComponentSectionAppends:
    """Section appends from layers are incorporated."""

    def _layer_with_append(self, scope: str, component_id: str, append_text: str) -> ManifestLayer:
        agent = AgentEntry(id=component_id, append=append_text)
        return ManifestLayer(
            scope=scope,
            path=Path(f"/{scope}/manifest.toml"),
            manifest=ManifestV2(version="2.0", agents=[agent]),
            state=ManifestLayerState.LOADED,
        )

    def test_single_layer_append(self):
        """Append content from a single layer is added after base content."""
        layer = self._layer_with_append("repo", "my-agent", "## Additional Section")
        result = assemble_component(
            "my-agent", "# Base Content", [layer], {}, "claude"
        )
        assert result == "# Base Content\n## Additional Section"

    def test_multiple_layers_appended_in_order(self):
        """Appends from multiple layers appear in resolution order (outer first)."""
        outer = self._layer_with_append("master", "my-agent", "outer append")
        inner = self._layer_with_append("repo", "my-agent", "inner append")
        result = assemble_component(
            "my-agent", "base", [outer, inner], {}, "claude"
        )
        assert result == "base\nouter append\ninner append"

    def test_append_with_variable_substitution(self):
        """Variables in appended content are also substituted."""
        layer = self._layer_with_append("repo", "agent-x", "Repo root: {repo}")
        variables = {"repo": "/my/project"}
        result = assemble_component(
            "agent-x", "Header.", [layer], variables, "claude"
        )
        assert result == "Header.\nRepo root: /my/project"

    def test_append_only_for_matching_component(self):
        """Appends are only applied for the component with matching ID."""
        layer = self._layer_with_append("repo", "other-agent", "should not appear")
        result = assemble_component(
            "my-agent", "base", [layer], {}, "claude"
        )
        assert result == "base"
