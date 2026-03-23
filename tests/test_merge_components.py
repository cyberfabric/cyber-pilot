"""
Tests for merge_components() and apply_section_appends() in manifest.py.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from cypilot.utils.manifest import (
    AgentEntry,
    ManifestLayer,
    ManifestLayerState,
    ManifestV2,
    MergedComponents,
    ProvenanceRecord,
    RuleEntry,
    SkillEntry,
    WorkflowEntry,
    apply_section_appends,
    merge_components,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_layer(
    scope: str,
    agents=None,
    skills=None,
    workflows=None,
    rules=None,
    path: str = "/fake/manifest.toml",
    state: ManifestLayerState = ManifestLayerState.LOADED,
) -> ManifestLayer:
    manifest = ManifestV2(
        version="2.0",
        agents=agents or [],
        skills=skills or [],
        workflows=workflows or [],
        rules=rules or [],
    )
    return ManifestLayer(
        scope=scope,
        path=Path(path),
        manifest=manifest,
        state=state,
    )


def _agent(id: str, description: str = "") -> AgentEntry:
    return AgentEntry(id=id, description=description)


def _skill(id: str, description: str = "") -> SkillEntry:
    return SkillEntry(id=id, description=description)


def _workflow(id: str, description: str = "") -> WorkflowEntry:
    return WorkflowEntry(id=id, description=description)


def _rule(id: str, description: str = "") -> RuleEntry:
    return RuleEntry(id=id, description=description)


# ---------------------------------------------------------------------------
# Tests: merge_components
# ---------------------------------------------------------------------------

class TestMergeComponentsSingleLayer:
    """Test that a single layer produces the expected merged result."""

    def test_single_layer_agents_present(self):
        agent = _agent("my-agent", "desc")
        layer = _make_layer("repo", agents=[agent])
        result = merge_components([layer])
        assert "my-agent" in result.agents
        assert result.agents["my-agent"] is agent

    def test_single_layer_skills_present(self):
        skill = _skill("my-skill")
        layer = _make_layer("repo", skills=[skill])
        result = merge_components([layer])
        assert "my-skill" in result.skills
        assert result.skills["my-skill"] is skill

    def test_single_layer_workflows_present(self):
        wf = _workflow("my-workflow")
        layer = _make_layer("repo", workflows=[wf])
        result = merge_components([layer])
        assert "my-workflow" in result.workflows

    def test_single_layer_rules_present(self):
        rule = _rule("my-rule")
        layer = _make_layer("repo", rules=[rule])
        result = merge_components([layer])
        assert "my-rule" in result.rules

    def test_single_layer_provenance_no_overridden(self):
        agent = _agent("my-agent")
        layer = _make_layer("repo", agents=[agent])
        result = merge_components([layer])
        prov = result.provenance["my-agent"]
        assert prov.component_id == "my-agent"
        assert prov.winning_scope == "repo"
        assert prov.overridden == []


class TestMergeComponentsNonOverlapping:
    """Two layers with different component IDs — no collision."""

    def test_both_agents_present(self):
        layer_kit = _make_layer("kit", agents=[_agent("kit-agent")], path="/kit/manifest.toml")
        layer_repo = _make_layer("repo", agents=[_agent("repo-agent")], path="/repo/manifest.toml")
        result = merge_components([layer_kit, layer_repo])
        assert "kit-agent" in result.agents
        assert "repo-agent" in result.agents

    def test_mixed_component_types(self):
        layer_kit = _make_layer("kit", agents=[_agent("base-agent")], path="/kit/manifest.toml")
        layer_repo = _make_layer("repo", skills=[_skill("extra-skill")], path="/repo/manifest.toml")
        result = merge_components([layer_kit, layer_repo])
        assert "base-agent" in result.agents
        assert "extra-skill" in result.skills

    def test_provenance_correct_scopes(self):
        layer_kit = _make_layer("kit", agents=[_agent("kit-agent")], path="/kit/manifest.toml")
        layer_repo = _make_layer("repo", agents=[_agent("repo-agent")], path="/repo/manifest.toml")
        result = merge_components([layer_kit, layer_repo])
        assert result.provenance["kit-agent"].winning_scope == "kit"
        assert result.provenance["repo-agent"].winning_scope == "repo"


class TestMergeComponentsInnerScopeWins:
    """Later (inner/higher-priority) layer wins on same component ID."""

    def test_inner_scope_overwrites_outer(self):
        outer_agent = _agent("shared-agent", "from kit")
        inner_agent = _agent("shared-agent", "from repo")
        layer_kit = _make_layer("kit", agents=[outer_agent], path="/kit/manifest.toml")
        layer_repo = _make_layer("repo", agents=[inner_agent], path="/repo/manifest.toml")
        result = merge_components([layer_kit, layer_repo])
        assert result.agents["shared-agent"].description == "from repo"

    def test_inner_scope_wins_three_layers(self):
        core_agent = _agent("agent", "core")
        master_agent = _agent("agent", "master")
        repo_agent = _agent("agent", "repo")
        layer_core = _make_layer("core", agents=[core_agent], path="/core/manifest.toml")
        layer_master = _make_layer("master", agents=[master_agent], path="/master/manifest.toml")
        layer_repo = _make_layer("repo", agents=[repo_agent], path="/repo/manifest.toml")
        result = merge_components([layer_core, layer_master, layer_repo])
        assert result.agents["agent"].description == "repo"

    def test_only_loaded_layers_are_merged(self):
        good_agent = _agent("agent-a")
        error_layer = _make_layer(
            "kit",
            agents=[_agent("agent-b")],
            path="/broken/manifest.toml",
            state=ManifestLayerState.PARSE_ERROR,
        )
        good_layer = _make_layer("repo", agents=[good_agent], path="/repo/manifest.toml")
        result = merge_components([error_layer, good_layer])
        assert "agent-a" in result.agents
        assert "agent-b" not in result.agents


class TestMergeComponentsProvenance:
    """Provenance correctly identifies winning layer and overridden layers."""

    def test_provenance_records_overridden_layers(self):
        outer_agent = _agent("shared", "outer")
        inner_agent = _agent("shared", "inner")
        layer_kit = _make_layer("kit", agents=[outer_agent], path="/kit/manifest.toml")
        layer_repo = _make_layer("repo", agents=[inner_agent], path="/repo/manifest.toml")
        result = merge_components([layer_kit, layer_repo])
        prov = result.provenance["shared"]
        assert prov.winning_scope == "repo"
        assert len(prov.overridden) == 1
        overridden_scopes = [scope for scope, _ in prov.overridden]
        assert "kit" in overridden_scopes

    def test_provenance_winning_path(self):
        agent = _agent("my-agent")
        layer = _make_layer("repo", agents=[agent], path="/repo/.bootstrap/config/manifest.toml")
        result = merge_components([layer])
        prov = result.provenance["my-agent"]
        assert prov.winning_path == Path("/repo/.bootstrap/config/manifest.toml")

    def test_provenance_component_type(self):
        skill = _skill("my-skill")
        layer = _make_layer("repo", skills=[skill], path="/repo/manifest.toml")
        result = merge_components([layer])
        prov = result.provenance["my-skill"]
        assert prov.component_type == "skills"

    def test_provenance_multiple_overridden(self):
        layer_a = _make_layer("kit", agents=[_agent("x", "a")], path="/a/manifest.toml")
        layer_b = _make_layer("master", agents=[_agent("x", "b")], path="/b/manifest.toml")
        layer_c = _make_layer("repo", agents=[_agent("x", "c")], path="/c/manifest.toml")
        result = merge_components([layer_a, layer_b, layer_c])
        prov = result.provenance["x"]
        assert prov.winning_scope == "repo"
        assert len(prov.overridden) == 2


class TestMergeComponentsEmptyInput:
    """Edge cases: empty layers list and layers with no components."""

    def test_empty_layers_returns_empty_result(self):
        result = merge_components([])
        assert result.agents == {}
        assert result.skills == {}
        assert result.workflows == {}
        assert result.rules == {}
        assert result.provenance == {}

    def test_layer_with_no_manifest_skipped(self):
        layer = ManifestLayer(
            scope="repo",
            path=Path("/fake/manifest.toml"),
            manifest=None,
            state=ManifestLayerState.UNDISCOVERED,
        )
        result = merge_components([layer])
        assert result.agents == {}

    def test_returns_merged_components_type(self):
        result = merge_components([])
        assert isinstance(result, MergedComponents)


# ---------------------------------------------------------------------------
# Tests: apply_section_appends
# ---------------------------------------------------------------------------

class TestApplySectionAppendsNoAppends:
    """Base content is unchanged when no layers have append content."""

    def test_no_layers_returns_base(self):
        result = apply_section_appends("base content", [], "my-agent")
        assert result == "base content"

    def test_layers_without_append_for_id(self):
        layer = _make_layer("repo", agents=[_agent("my-agent")])
        result = apply_section_appends("base content", [layer], "my-agent")
        assert result == "base content"

    def test_append_for_different_id_ignored(self):
        agent_with_append = AgentEntry(id="other-agent", append="extra content")
        layer = _make_layer("repo", agents=[agent_with_append])
        result = apply_section_appends("base content", [layer], "my-agent")
        assert result == "base content"


class TestApplySectionAppendsWithContent:
    """Section appending stacks content in resolution order."""

    def test_single_layer_append(self):
        agent_with_append = AgentEntry(id="my-agent", append="appended line")
        layer = _make_layer("repo", agents=[agent_with_append])
        result = apply_section_appends("base content", [layer], "my-agent")
        assert result == "base content\nappended line"

    def test_two_layers_append_in_order(self):
        kit_agent = AgentEntry(id="my-agent", append="kit append")
        repo_agent = AgentEntry(id="my-agent", append="repo append")
        layer_kit = _make_layer("kit", agents=[kit_agent], path="/kit/manifest.toml")
        layer_repo = _make_layer("repo", agents=[repo_agent], path="/repo/manifest.toml")
        result = apply_section_appends("base", [layer_kit, layer_repo], "my-agent")
        assert result == "base\nkit append\nrepo append"

    def test_appends_from_different_component_types(self):
        skill_with_append = SkillEntry(id="my-skill", append="skill append")
        layer = _make_layer("repo", skills=[skill_with_append])
        result = apply_section_appends("base", [layer], "my-skill")
        assert result == "base\nskill append"

    def test_append_only_from_loaded_layers(self):
        agent_with_append = AgentEntry(id="my-agent", append="broken append")
        broken_layer = _make_layer(
            "kit",
            agents=[agent_with_append],
            path="/broken/manifest.toml",
            state=ManifestLayerState.PARSE_ERROR,
        )
        result = apply_section_appends("base", [broken_layer], "my-agent")
        assert result == "base"

    def test_resolution_order_preserved(self):
        """Outermost (first in list) append appears before innermost."""
        outer_agent = AgentEntry(id="agent", append="OUTER")
        inner_agent = AgentEntry(id="agent", append="INNER")
        layer_outer = _make_layer("kit", agents=[outer_agent], path="/kit/manifest.toml")
        layer_inner = _make_layer("repo", agents=[inner_agent], path="/repo/manifest.toml")
        result = apply_section_appends("BASE", [layer_outer, layer_inner], "agent")
        lines = result.split("\n")
        assert lines[0] == "BASE"
        assert lines[1] == "OUTER"
        assert lines[2] == "INNER"
