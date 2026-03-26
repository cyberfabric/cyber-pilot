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
        prov = result.provenance["agents:my-agent"]
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
        assert result.provenance["agents:kit-agent"].winning_scope == "kit"
        assert result.provenance["agents:repo-agent"].winning_scope == "repo"


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
        prov = result.provenance["agents:shared"]
        assert prov.winning_scope == "repo"
        assert len(prov.overridden) == 1
        overridden_scopes = [scope for scope, _ in prov.overridden]
        assert "kit" in overridden_scopes

    def test_provenance_winning_path(self):
        agent = _agent("my-agent")
        layer = _make_layer("repo", agents=[agent], path="/repo/.bootstrap/config/manifest.toml")
        result = merge_components([layer])
        prov = result.provenance["agents:my-agent"]
        assert prov.winning_path == Path("/repo/.bootstrap/config/manifest.toml")

    def test_provenance_component_type(self):
        skill = _skill("my-skill")
        layer = _make_layer("repo", skills=[skill], path="/repo/manifest.toml")
        result = merge_components([layer])
        prov = result.provenance["skills:my-skill"]
        assert prov.component_type == "skills"

    def test_provenance_multiple_overridden(self):
        layer_a = _make_layer("kit", agents=[_agent("x", "a")], path="/a/manifest.toml")
        layer_b = _make_layer("master", agents=[_agent("x", "b")], path="/b/manifest.toml")
        layer_c = _make_layer("repo", agents=[_agent("x", "c")], path="/c/manifest.toml")
        result = merge_components([layer_a, layer_b, layer_c])
        prov = result.provenance["agents:x"]
        assert prov.winning_scope == "repo"
        assert len(prov.overridden) == 2


class TestProvenanceNamespacedBySectionType:
    """Provenance keys are namespaced by component type to avoid collisions
    when different sections share the same component ID."""

    def test_same_id_across_agents_and_skills_no_collision(self):
        """An agent and a skill with the same raw ID produce distinct provenance entries."""
        agent = _agent("shared-id", "I am an agent")
        skill = _skill("shared-id", "I am a skill")
        layer = _make_layer("repo", agents=[agent], skills=[skill])
        result = merge_components([layer])

        # Both components exist in their respective dicts
        assert "shared-id" in result.agents
        assert "shared-id" in result.skills

        # Provenance is keyed by "section:id", so both exist independently
        assert "agents:shared-id" in result.provenance
        assert "skills:shared-id" in result.provenance

        agent_prov = result.provenance["agents:shared-id"]
        skill_prov = result.provenance["skills:shared-id"]

        assert agent_prov.component_type == "agents"
        assert skill_prov.component_type == "skills"
        assert agent_prov.component_id == "shared-id"
        assert skill_prov.component_id == "shared-id"

    def test_same_id_across_all_four_sections(self):
        """Same ID in agents, skills, workflows, and rules produces four provenance entries."""
        layer = _make_layer(
            "repo",
            agents=[_agent("x")],
            skills=[_skill("x")],
            workflows=[_workflow("x")],
            rules=[_rule("x")],
        )
        result = merge_components([layer])

        assert len(result.provenance) == 4
        for section in ("agents", "skills", "workflows", "rules"):
            key = f"{section}:x"
            assert key in result.provenance, f"Missing provenance key {key}"
            assert result.provenance[key].component_type == section

    def test_same_id_across_sections_with_override(self):
        """Override tracking works independently per section even with same raw ID."""
        kit_layer = _make_layer(
            "kit",
            agents=[_agent("dup", "kit-agent")],
            skills=[_skill("dup", "kit-skill")],
            path="/kit/manifest.toml",
        )
        repo_layer = _make_layer(
            "repo",
            agents=[_agent("dup", "repo-agent")],
            skills=[_skill("dup", "repo-skill")],
            path="/repo/manifest.toml",
        )
        result = merge_components([kit_layer, repo_layer])

        agent_prov = result.provenance["agents:dup"]
        skill_prov = result.provenance["skills:dup"]

        # Both should show repo winning with kit overridden
        assert agent_prov.winning_scope == "repo"
        assert len(agent_prov.overridden) == 1
        assert agent_prov.overridden[0][0] == "kit"

        assert skill_prov.winning_scope == "repo"
        assert len(skill_prov.overridden) == 1
        assert skill_prov.overridden[0][0] == "kit"

    def test_provenance_key_format_is_section_colon_id(self):
        """Verify provenance keys follow the 'section:id' format for JSON serializability."""
        layer = _make_layer("repo", agents=[_agent("my-agent")])
        result = merge_components([layer])
        keys = list(result.provenance.keys())
        assert keys == ["agents:my-agent"]
        # Verify key is a plain string (JSON-serializable), not a tuple
        assert isinstance(keys[0], str)


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
    """Base content is unchanged when no components have append content."""

    def test_no_components_returns_base(self):
        result = apply_section_appends("base content", [], "my-agent")
        assert result == "base content"

    def test_component_without_append(self):
        agent = _agent("my-agent")
        result = apply_section_appends("base content", [agent], "my-agent")
        assert result == "base content"

    def test_append_for_different_id_ignored(self):
        agent_with_append = AgentEntry(id="other-agent", append="extra content")
        result = apply_section_appends("base content", [agent_with_append], "my-agent")
        assert result == "base content"


class TestApplySectionAppendsWithContent:
    """Section appending uses pre-merged append content from components."""

    def test_single_component_append(self):
        agent_with_append = AgentEntry(id="my-agent", append="appended line")
        result = apply_section_appends("base content", [agent_with_append], "my-agent")
        assert result == "base content\nappended line"

    def test_pre_merged_append_from_two_layers(self):
        """After merge_components, a single component has accumulated appends."""
        # Simulate what merge_components produces: a single component with
        # accumulated appends from two layers (outer first, inner second).
        merged_agent = AgentEntry(id="my-agent", append="kit append\nrepo append")
        result = apply_section_appends("base", [merged_agent], "my-agent")
        assert result == "base\nkit append\nrepo append"

    def test_appends_from_skill_component(self):
        skill_with_append = SkillEntry(id="my-skill", append="skill append")
        result = apply_section_appends("base", [skill_with_append], "my-skill")
        assert result == "base\nskill append"

    def test_resolution_order_preserved_in_pre_merged(self):
        """Pre-merged append field preserves resolution order (outer first)."""
        merged_agent = AgentEntry(id="agent", append="OUTER\nINNER")
        result = apply_section_appends("BASE", [merged_agent], "agent")
        lines = result.split("\n")
        assert lines[0] == "BASE"
        assert lines[1] == "OUTER"
        assert lines[2] == "INNER"

    def test_cross_type_id_collision_first_match_wins(self):
        """When multiple components share an ID, first match wins (break)."""
        agent = AgentEntry(id="shared-id", append="agent append")
        skill = SkillEntry(id="shared-id", append="skill append")
        # In a merged components list, agent appears before skill
        result = apply_section_appends("base", [agent, skill], "shared-id")
        assert result == "base\nagent append"

    def test_only_matching_id_appended(self):
        """Components with non-matching IDs are skipped."""
        agent = AgentEntry(id="shared-id", append="agent append")
        skill = SkillEntry(id="other-id", append="skill append")
        result = apply_section_appends("base", [agent, skill], "shared-id")
        assert result == "base\nagent append"


class TestApplySectionAppendsCrossTypeFiltering:
    """apply_section_appends with pre-merged component lists."""

    def test_agent_append_applied(self):
        """Agent component with matching ID has its append applied."""
        agent = AgentEntry(id="builder", append="agent-specific append")
        result = apply_section_appends(
            "base", [agent], "builder", component_type="agents",
        )
        assert "agent-specific append" in result

    def test_skill_append_applied(self):
        """Skill component with matching ID has its append applied."""
        skill = SkillEntry(id="builder", append="skill-specific append")
        result = apply_section_appends(
            "base", [skill], "builder", component_type="skills",
        )
        assert "skill-specific append" in result

    def test_first_match_wins_in_flat_list(self):
        """In a flat component list, first matching ID wins."""
        agent = AgentEntry(id="builder", append="agent-specific append")
        skill = SkillEntry(id="builder", append="skill-specific append")
        result = apply_section_appends("base", [agent, skill], "builder")
        assert "agent-specific append" in result

    def test_pre_merged_multi_layer_skill_append(self):
        """Pre-merged skill with accumulated multi-layer appends."""
        # After merge_components, a single skill entry has all layer appends
        merged_skill = SkillEntry(id="builder", append="kit skill append\nrepo skill append")
        result = apply_section_appends(
            "base", [merged_skill], "builder", component_type="skills",
        )
        assert "kit skill append" in result
        assert "repo skill append" in result
        # Resolution order preserved: kit before repo
        assert result.index("kit skill append") < result.index("repo skill append")
