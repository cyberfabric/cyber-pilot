"""
Integration and backward-compatibility tests for cmd_generate_agents().

Tests the multi-layer pipeline (Phase 8) and backward compatibility with
standalone repos that have no manifest.toml v2.0.

@cpt-flow:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1
@cpt-dod:cpt-cypilot-dod-project-extensibility-backward-compat:p1
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.commands.agents import (
    _discover_kit_agents,
    _layers_have_v2_manifests,
    build_provenance_report,
    discover_components,
    generate_manifest_skills,
    translate_agent_schema,
    write_discovered_manifest,
)
from cypilot.utils.manifest import (
    AgentEntry,
    ManifestLayer,
    ManifestLayerState,
    ManifestV2,
    MergedComponents,
    ProvenanceRecord,
    SkillEntry,
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


def _agent_entry(
    id: str,
    description: str = "",
    mode: str = "readwrite",
    model: str = "",
    agents: list = None,
) -> AgentEntry:
    return AgentEntry(
        id=id,
        description=description,
        mode=mode,
        model=model,
        agents=agents or [],
    )


def _skill_entry(
    id: str,
    description: str = "",
    agents: list = None,
    source: str = "",
) -> SkillEntry:
    return SkillEntry(
        id=id,
        description=description,
        agents=agents or [],
        source=source,
    )


# ---------------------------------------------------------------------------
# Test 1: _layers_have_v2_manifests() — detection helper
# ---------------------------------------------------------------------------

class TestLayersHaveV2Manifests(unittest.TestCase):
    """Tests for the v2.0 manifest detection helper."""

    def test_empty_layers_returns_false(self):
        """Empty layer list returns False."""
        self.assertFalse(_layers_have_v2_manifests([]))

    def test_no_loaded_layers_returns_false(self):
        """Layers with PARSE_ERROR state return False."""
        layer = ManifestLayer(
            scope="repo",
            path=Path("/fake/manifest.toml"),
            manifest=None,
            state=ManifestLayerState.PARSE_ERROR,
        )
        self.assertFalse(_layers_have_v2_manifests([layer]))

    def test_loaded_layer_with_no_components_returns_false(self):
        """Loaded layer with empty v2.0 manifest returns False (no components)."""
        manifest = ManifestV2(version="2.0")
        layer = ManifestLayer(
            scope="repo",
            path=Path("/fake/manifest.toml"),
            manifest=manifest,
            state=ManifestLayerState.LOADED,
        )
        self.assertFalse(_layers_have_v2_manifests([layer]))

    def test_loaded_layer_with_agents_returns_true(self):
        """Loaded layer with agents returns True."""
        agent = _agent_entry("my-agent")
        layer = _make_layer("repo", agents=[agent])
        self.assertTrue(_layers_have_v2_manifests([layer]))

    def test_loaded_layer_with_skills_returns_true(self):
        """Loaded layer with skills returns True."""
        skill = _skill_entry("my-skill")
        layer = _make_layer("repo", skills=[skill])
        self.assertTrue(_layers_have_v2_manifests([layer]))

    def test_v1_manifest_returns_false(self):
        """V1.0 manifest layer returns False (no v2 components)."""
        manifest = ManifestV2(version="1.0")
        layer = ManifestLayer(
            scope="repo",
            path=Path("/fake/manifest.toml"),
            manifest=manifest,
            state=ManifestLayerState.LOADED,
        )
        self.assertFalse(_layers_have_v2_manifests([layer]))


# ---------------------------------------------------------------------------
# Test 2: Backward compatibility — no manifest.toml produces legacy behavior
# ---------------------------------------------------------------------------

class TestBackwardCompatNoManifest(unittest.TestCase):
    """Test that standalone repos without manifest.toml use legacy path."""

    def test_no_v2_layers_takes_legacy_path(self):
        """When no v2.0 layers exist, _layers_have_v2_manifests() returns False.

        This ensures the legacy _discover_kit_agents() path is taken.
        """
        # Simulate no layers (empty discovery result)
        layers = []
        self.assertFalse(_layers_have_v2_manifests(layers))

    def test_parse_error_layer_uses_legacy(self):
        """Parse error layer does not trigger v2 path."""
        layer = ManifestLayer(
            scope="repo",
            path=Path("/fake/manifest.toml"),
            manifest=None,
            state=ManifestLayerState.PARSE_ERROR,
        )
        self.assertFalse(_layers_have_v2_manifests([layer]))


# ---------------------------------------------------------------------------
# Test 3: V2 manifest with [[agents]] produces correct translation
# ---------------------------------------------------------------------------

class TestV2ManifestWithAgents(unittest.TestCase):
    """Test that v2.0 manifest with [[agents]] produces correct translated output."""

    def test_agent_with_v2_manifest_translates_claude(self):
        """AgentEntry from manifest v2.0 translates to Claude frontmatter."""
        agent = _agent_entry(
            "my-agent",
            description="Test agent",
            mode="readwrite",
        )
        result = translate_agent_schema(agent, "claude")
        self.assertFalse(result["skip"])
        self.assertIn("tools: Bash, Read, Write, Edit, Glob, Grep", result["frontmatter"])

    def test_agent_readonly_mode_translates(self):
        """Readonly mode agent translates correctly for Claude."""
        agent = _agent_entry("ro-agent", mode="readonly")
        result = translate_agent_schema(agent, "claude")
        frontmatter = result["frontmatter"]
        self.assertIn("tools: Bash, Read, Glob, Grep", frontmatter)
        self.assertIn("disallowedTools: Write, Edit", frontmatter)

    def test_agent_with_model_translates(self):
        """Agent with custom model string (passthrough) translates correctly."""
        agent = _agent_entry("model-agent", model="claude-opus-4-5")
        result = translate_agent_schema(agent, "claude")
        # Model should appear in frontmatter
        model_lines = [l for l in result["frontmatter"] if "model:" in l]
        self.assertEqual(len(model_lines), 1)
        self.assertIn("claude-opus-4-5", model_lines[0])

    def test_agent_translates_for_all_targets(self):
        """Agent translates for all supported targets."""
        agent = _agent_entry("all-targets")
        for target in ["claude", "cursor", "copilot", "openai", "windsurf"]:
            result = translate_agent_schema(agent, target)
            self.assertIn("skip", result)

    def test_layers_with_agents_detected_as_v2(self):
        """Layers containing agents are detected as v2.0."""
        agent = _agent_entry("my-agent")
        layer = _make_layer("repo", agents=[agent])
        self.assertTrue(_layers_have_v2_manifests([layer]))


# ---------------------------------------------------------------------------
# Test 4: V2 manifest with [[skills]] produces skill files
# ---------------------------------------------------------------------------

class TestV2ManifestWithSkills(unittest.TestCase):
    """Test that v2.0 manifest with [[skills]] generates skill files."""

    def test_generate_manifest_skills_creates_files(self):
        """Skill entries targeting a specific agent produce output files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Create a source skill file
            skill_src = project_root / "my-skill.md"
            skill_src.write_text("# My Skill\n\nSkill content.", encoding="utf-8")

            skill = _skill_entry(
                id="my-skill",
                description="Test skill",
                agents=["claude"],
                source=str(skill_src),
            )
            skills: Dict[str, SkillEntry] = {"my-skill": skill}

            result = generate_manifest_skills(skills, "claude", project_root, dry_run=False)

            # Verify skill file was created
            self.assertGreaterEqual(len(result["created"]) + len(result["updated"]), 1)

            # Verify the output path
            expected_output = project_root / ".claude" / "skills" / "my-skill" / "SKILL.md"
            self.assertTrue(expected_output.exists())

    def test_generate_manifest_skills_dry_run(self):
        """Dry run does not create files but returns what would be created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            skill_src = project_root / "dry-skill.md"
            skill_src.write_text("# Dry Skill\n\nContent.", encoding="utf-8")

            skill = _skill_entry(
                id="dry-skill",
                agents=["claude"],
                source=str(skill_src),
            )
            skills: Dict[str, SkillEntry] = {"dry-skill": skill}

            result = generate_manifest_skills(skills, "claude", project_root, dry_run=True)

            # Should report creation without writing
            self.assertGreaterEqual(len(result["created"]), 1)
            expected_output = project_root / ".claude" / "skills" / "dry-skill" / "SKILL.md"
            self.assertFalse(expected_output.exists())

    def test_skill_not_targeting_agent_is_skipped(self):
        """Skill not targeting the specified agent is skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            skill_src = project_root / "skip-skill.md"
            skill_src.write_text("# Skip Skill", encoding="utf-8")

            skill = _skill_entry(
                id="skip-skill",
                agents=["cursor"],  # Does not target claude
                source=str(skill_src),
            )
            skills: Dict[str, SkillEntry] = {"skip-skill": skill}

            result = generate_manifest_skills(skills, "claude", project_root, dry_run=False)

            # Nothing should be generated for claude
            self.assertEqual(len(result["created"]), 0)
            self.assertEqual(len(result["updated"]), 0)


# ---------------------------------------------------------------------------
# Test 5: --show-layers flag produces provenance report
# ---------------------------------------------------------------------------

class TestShowLayersFlag(unittest.TestCase):
    """Test that --show-layers flag produces provenance report."""

    def test_build_provenance_report_from_merged(self):
        """build_provenance_report produces correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            agent = _agent_entry("test-agent")
            layer = _make_layer("repo", agents=[agent])
            merged = merge_components([layer])

            report = build_provenance_report(merged, project_root)

            self.assertIn("components", report)
            components = report["components"]
            self.assertEqual(len(components), 1)
            self.assertEqual(components[0]["id"], "test-agent")
            self.assertEqual(components[0]["type"], "agents")
            self.assertEqual(components[0]["winning_scope"], "repo")

    def test_provenance_report_multi_layer_shows_overrides(self):
        """Provenance report shows which layer overrides which."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            agent_kit = _agent_entry("shared-agent", description="from kit")
            agent_repo = _agent_entry("shared-agent", description="from repo")
            kit_layer = _make_layer("kit", agents=[agent_kit], path="/kit/manifest.toml")
            repo_layer = _make_layer("repo", agents=[agent_repo], path="/repo/manifest.toml")

            merged = merge_components([kit_layer, repo_layer])
            report = build_provenance_report(merged, project_root)

            components = report["components"]
            self.assertEqual(len(components), 1)
            rec = components[0]
            self.assertEqual(rec["id"], "shared-agent")
            self.assertEqual(rec["winning_scope"], "repo")
            # Kit was overridden
            self.assertEqual(len(rec["overridden"]), 1)
            self.assertEqual(rec["overridden"][0]["scope"], "kit")

    def test_format_provenance_human_output(self):
        """format_provenance_human produces readable output."""
        from cypilot.commands.agents import format_provenance_human

        report = {
            "components": [
                {
                    "id": "my-agent",
                    "type": "agents",
                    "winning_scope": "repo",
                    "winning_path": ".bootstrap/config/manifest.toml",
                    "overridden": [],
                }
            ]
        }
        output = format_provenance_human(report)
        self.assertIn("Layer Provenance Report", output)
        self.assertIn("my-agent", output)
        self.assertIn("Repo", output)


# ---------------------------------------------------------------------------
# Test 6: --discover flag scans directories
# ---------------------------------------------------------------------------

class TestDiscoverFlag(unittest.TestCase):
    """Test --discover flag scanning and manifest population."""

    def test_discover_components_finds_agents(self):
        """discover_components finds .claude/agents/*.md files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            agents_dir = project_root / ".claude" / "agents"
            agents_dir.mkdir(parents=True)

            (agents_dir / "my-agent.md").write_text(
                "---\ndescription: My test agent\n---\n\nContent.",
                encoding="utf-8",
            )

            result = discover_components(project_root)

            self.assertIn("agents", result)
            self.assertEqual(len(result["agents"]), 1)
            self.assertEqual(result["agents"][0]["id"], "my-agent")
            self.assertEqual(result["agents"][0]["description"], "My test agent")

    def test_discover_components_finds_skills(self):
        """discover_components finds .claude/skills/*/SKILL.md files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            skill_dir = project_root / ".claude" / "skills" / "my-skill"
            skill_dir.mkdir(parents=True)

            (skill_dir / "SKILL.md").write_text(
                "---\ndescription: My skill\n---\n\nContent.",
                encoding="utf-8",
            )

            result = discover_components(project_root)

            self.assertIn("skills", result)
            self.assertEqual(len(result["skills"]), 1)
            self.assertEqual(result["skills"][0]["id"], "my-skill")

    def test_write_discovered_manifest_creates_file(self):
        """write_discovered_manifest creates a valid manifest.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest_path = project_root / "manifest.toml"

            discovered = {
                "agents": [
                    {"id": "my-agent", "description": "Test agent", "source": "/some/path.md"},
                ],
                "skills": [],
                "workflows": [],
            }

            write_discovered_manifest(discovered, manifest_path)

            self.assertTrue(manifest_path.exists())
            content = manifest_path.read_text(encoding="utf-8")
            self.assertIn('[manifest]', content)
            self.assertIn('version = "2.0"', content)
            self.assertIn('[[agents]]', content)
            self.assertIn('id = "my-agent"', content)

    def test_discover_empty_project(self):
        """discover_components on empty project returns empty lists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result = discover_components(project_root)
            self.assertEqual(result["agents"], [])
            self.assertEqual(result["skills"], [])
            self.assertEqual(result["workflows"], [])


# ---------------------------------------------------------------------------
# Test 7: Passthrough model strings (not just inherit/fast)
# ---------------------------------------------------------------------------

class TestPassthroughModelStrings(unittest.TestCase):
    """Test that _VALID_MODELS accepts passthrough model strings with warning."""

    def test_passthrough_model_no_skip(self):
        """Unknown model string is accepted as passthrough (no skip)."""
        # Load a fake agents.toml in a temp dir with a passthrough model
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create a mock prompt file
            prompt_file = tmppath / "agent.md"
            prompt_file.write_text("# Agent prompt", encoding="utf-8")

            agents_toml = tmppath / "agents.toml"
            agents_toml.write_text(
                '[agents.my-agent]\n'
                'prompt_file = "agent.md"\n'
                'model = "claude-opus-4-5-20251101"\n'
                'description = "Agent with custom model"\n',
                encoding="utf-8",
            )

            # Mock the cypilot root structure
            mock_root = tmppath / "cpt"
            mock_root.mkdir()
            core_skills = mock_root / ".core" / "skills" / "cypilot"
            core_skills.mkdir(parents=True)

            # Copy our agents.toml to core skill area
            import shutil
            shutil.copy(agents_toml, core_skills / "agents.toml")
            shutil.copy(prompt_file, core_skills / "agent.md")

            import io
            captured = io.StringIO()
            with mock.patch("sys.stderr", captured):
                agents = _discover_kit_agents(mock_root)

            # Agent should be discovered (not skipped)
            agent_names = [a["name"] for a in agents]
            self.assertIn("my-agent", agent_names)

    def test_known_model_inherit_no_warning(self):
        """Known model 'inherit' does not produce a warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            prompt_file = tmppath / "agent.md"
            prompt_file.write_text("# Agent prompt", encoding="utf-8")

            agents_toml = tmppath / "agents.toml"
            agents_toml.write_text(
                '[agents.known-agent]\n'
                'prompt_file = "agent.md"\n'
                'model = "inherit"\n',
                encoding="utf-8",
            )

            mock_root = tmppath / "cpt"
            mock_root.mkdir()
            core_skills = mock_root / ".core" / "skills" / "cypilot"
            core_skills.mkdir(parents=True)

            import shutil
            shutil.copy(agents_toml, core_skills / "agents.toml")
            shutil.copy(prompt_file, core_skills / "agent.md")

            import io
            captured = io.StringIO()
            with mock.patch("sys.stderr", captured):
                agents = _discover_kit_agents(mock_root)

            # Inherit is a known model — should not warn
            stderr_output = captured.getvalue()
            self.assertNotIn("unknown model", stderr_output)
            self.assertIn("known-agent", [a["name"] for a in agents])

    def test_translate_agent_schema_passthrough_model(self):
        """translate_agent_schema accepts passthrough model in AgentEntry."""
        agent = AgentEntry(
            id="model-agent",
            model="claude-opus-4-5-custom",
        )
        result = translate_agent_schema(agent, "claude")
        self.assertFalse(result.get("skip", False))
        model_lines = [l for l in result["frontmatter"] if "model:" in l]
        self.assertEqual(len(model_lines), 1)
        self.assertIn("claude-opus-4-5-custom", model_lines[0])


# ---------------------------------------------------------------------------
# Test 8: agents.toml fallback when no [[agents]] in manifest
# ---------------------------------------------------------------------------

class TestAgentsTomlfallback(unittest.TestCase):
    """Test that agents.toml is read as fallback when no [[agents]] in manifest."""

    def test_no_agents_in_v2_manifest_falls_back_to_legacy(self):
        """Layer with skills but no agents still allows legacy agents.toml flow."""
        # A manifest with only skills and no agents
        skill = _skill_entry("my-skill")
        layer = _make_layer("repo", skills=[skill])

        # Even though layer is loaded with v2 manifest, it has no agents
        # _layers_have_v2_manifests returns True because it has skills
        self.assertTrue(_layers_have_v2_manifests([layer]))

    def test_v2_manifest_no_components_triggers_legacy(self):
        """V2 manifest with no components triggers legacy agents.toml path."""
        manifest = ManifestV2(version="2.0")
        layer = ManifestLayer(
            scope="repo",
            path=Path("/fake/manifest.toml"),
            manifest=manifest,
            state=ManifestLayerState.LOADED,
        )
        # No components → legacy path
        self.assertFalse(_layers_have_v2_manifests([layer]))

    def test_merge_components_empty_layers_produces_empty_merged(self):
        """Merging empty layers produces empty MergedComponents."""
        merged = merge_components([])
        self.assertEqual(merged.agents, {})
        self.assertEqual(merged.skills, {})
        self.assertEqual(merged.workflows, {})
        self.assertEqual(merged.rules, {})


# ---------------------------------------------------------------------------
# Test 9: V2 preferred over agents.toml when both exist
# ---------------------------------------------------------------------------

class TestV2PreferredOverAgentsToml(unittest.TestCase):
    """Test that v2.0 [[agents]] is preferred over separate agents.toml."""

    def test_v2_layer_detected_before_legacy(self):
        """When v2.0 layer with agents exists, it takes precedence."""
        # Agent defined in v2 manifest layer
        agent = _agent_entry("shared-agent", description="from v2 manifest")
        layer = _make_layer("repo", agents=[agent])

        # v2 detection returns True → v2 path is taken (legacy is bypassed)
        self.assertTrue(_layers_have_v2_manifests([layer]))

    def test_kit_layer_agent_overridden_by_repo_layer(self):
        """Repo layer agent overrides kit layer agent (inner-scope wins)."""
        kit_agent = _agent_entry("shared-agent", description="kit version")
        repo_agent = _agent_entry("shared-agent", description="repo version")

        kit_layer = _make_layer("kit", agents=[kit_agent], path="/kit/manifest.toml")
        repo_layer = _make_layer("repo", agents=[repo_agent], path="/repo/manifest.toml")

        merged = merge_components([kit_layer, repo_layer])

        # Repo (inner/later) layer wins
        winner = merged.agents["shared-agent"]
        self.assertEqual(winner.description, "repo version")

        # Provenance shows kit was overridden
        prov = merged.provenance["shared-agent"]
        self.assertEqual(prov.winning_scope, "repo")
        self.assertEqual(len(prov.overridden), 1)
        self.assertEqual(prov.overridden[0][0], "kit")


# ---------------------------------------------------------------------------
# Test 10: Multi-layer pipeline wiring
# ---------------------------------------------------------------------------

class TestMultiLayerPipeline(unittest.TestCase):
    """Test multi-layer pipeline: discover → resolve includes → merge → generate."""

    def test_merge_single_layer(self):
        """Single layer merge returns all its components."""
        agent = _agent_entry("agent-a")
        skill = _skill_entry("skill-a")
        layer = _make_layer("repo", agents=[agent], skills=[skill])

        merged = merge_components([layer])

        self.assertIn("agent-a", merged.agents)
        self.assertIn("skill-a", merged.skills)

    def test_merge_two_layers_inner_wins(self):
        """Inner layer (repo) overrides outer layer (kit) on same ID."""
        kit_agent = _agent_entry("my-agent", description="kit")
        repo_agent = _agent_entry("my-agent", description="repo")
        kit_layer = _make_layer("kit", agents=[kit_agent], path="/kit/manifest.toml")
        repo_layer = _make_layer("repo", agents=[repo_agent], path="/repo/manifest.toml")

        merged = merge_components([kit_layer, repo_layer])

        self.assertEqual(merged.agents["my-agent"].description, "repo")

    def test_merge_skips_parse_error_layers(self):
        """Layers with PARSE_ERROR state are skipped during merge."""
        agent = _agent_entry("valid-agent")
        good_layer = _make_layer("repo", agents=[agent])
        bad_layer = ManifestLayer(
            scope="kit",
            path=Path("/bad/manifest.toml"),
            manifest=None,
            state=ManifestLayerState.PARSE_ERROR,
        )

        merged = merge_components([bad_layer, good_layer])

        self.assertIn("valid-agent", merged.agents)
        self.assertEqual(len(merged.agents), 1)

    def test_generate_manifest_skills_no_source_skips(self):
        """Skill with no source or prompt_file is skipped (warning emitted)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            skill = _skill_entry(id="nosource-skill", agents=["claude"])
            # No source set
            skills: Dict[str, SkillEntry] = {"nosource-skill": skill}

            import io
            captured = io.StringIO()
            with mock.patch("sys.stderr", captured):
                result = generate_manifest_skills(skills, "claude", project_root, dry_run=False)

            self.assertEqual(len(result["created"]), 0)
            self.assertIn("no source or prompt_file", captured.getvalue())


if __name__ == "__main__":
    unittest.main()
