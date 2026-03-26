"""
Tests for provenance report building and component auto-discovery.

Covers build_provenance_report(), format_provenance_human(),
discover_components(), and write_discovered_manifest() added to agents.py
in Phase 7 of the project-extensibility implementation plan.

@cpt-algo:cpt-cypilot-algo-project-extensibility-build-provenance:p2
@cpt-flow:cpt-cypilot-flow-project-extensibility-discover-register:p2
"""

from __future__ import annotations

import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.commands.agents import (
    _format_toml_entry,
    build_provenance_report,
    discover_components,
    format_provenance_human,
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
    WorkflowEntry,
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


def _agent(id: str, description: str = "", source: str = "") -> AgentEntry:
    return AgentEntry(id=id, description=description, source=source)


def _skill(id: str, description: str = "", source: str = "") -> SkillEntry:
    return SkillEntry(id=id, description=description, source=source)


def _workflow(id: str, description: str = "") -> WorkflowEntry:
    return WorkflowEntry(id=id, description=description)


# ---------------------------------------------------------------------------
# Tests: build_provenance_report — single layer
# ---------------------------------------------------------------------------

class TestBuildProvenanceReportSingleLayer:
    """Provenance report with a single layer (no overrides)."""

    def test_single_layer_agent_in_report(self):
        layers = [_make_layer("repo", agents=[_agent("my-agent")], path="/project/.bootstrap/config/manifest.toml")]
        merged = merge_components(layers)
        report = build_provenance_report(merged, Path("/project"))

        assert "components" in report
        assert len(report["components"]) == 1
        rec = report["components"][0]
        assert rec["id"] == "my-agent"
        assert rec["type"] == "agents"
        assert rec["winning_scope"] == "repo"
        assert rec["overridden"] == []

    def test_single_layer_winning_path_in_report(self):
        layers = [_make_layer("kit", skills=[_skill("my-skill")], path="/project/kits/foo/manifest.toml")]
        merged = merge_components(layers)
        report = build_provenance_report(merged, Path("/project"))

        rec = report["components"][0]
        assert rec["type"] == "skills"
        # Path should be relative to project root
        assert "kits/foo/manifest.toml" in rec["winning_path"]

    def test_single_layer_no_overrides(self):
        layers = [_make_layer("repo", workflows=[_workflow("deploy")], path="/p/manifest.toml")]
        merged = merge_components(layers)
        report = build_provenance_report(merged, Path("/p"))

        assert report["components"][0]["overridden"] == []


# ---------------------------------------------------------------------------
# Tests: build_provenance_report — overrides across layers
# ---------------------------------------------------------------------------

class TestBuildProvenanceReportOverrides:
    """Provenance report with multiple layers causing overrides."""

    def test_override_recorded_in_overridden_list(self):
        kit_layer = _make_layer("kit", agents=[_agent("review-agent")], path="/project/kits/sdlc/manifest.toml")
        repo_layer = _make_layer("repo", agents=[_agent("review-agent")], path="/project/.bootstrap/config/manifest.toml")
        merged = merge_components([kit_layer, repo_layer])
        report = build_provenance_report(merged, Path("/project"))

        rec = report["components"][0]
        assert rec["id"] == "review-agent"
        assert rec["winning_scope"] == "repo"
        assert len(rec["overridden"]) == 1
        assert rec["overridden"][0]["scope"] == "kit"

    def test_overridden_path_present(self):
        kit_layer = _make_layer("kit", agents=[_agent("shared-agent")], path="/project/kits/foo/manifest.toml")
        repo_layer = _make_layer("repo", agents=[_agent("shared-agent")], path="/project/config/manifest.toml")
        merged = merge_components([kit_layer, repo_layer])
        report = build_provenance_report(merged, Path("/project"))

        rec = report["components"][0]
        assert "path" in rec["overridden"][0]

    def test_multiple_component_types_sorted(self):
        layers = [
            _make_layer(
                "repo",
                agents=[_agent("z-agent"), _agent("a-agent")],
                skills=[_skill("b-skill")],
                path="/project/manifest.toml",
            )
        ]
        merged = merge_components(layers)
        report = build_provenance_report(merged, Path("/project"))

        ids_by_type: dict = {}
        for r in report["components"]:
            ids_by_type.setdefault(r["type"], []).append(r["id"])

        # Within agents section, IDs must be sorted
        assert ids_by_type["agents"] == sorted(ids_by_type["agents"])


# ---------------------------------------------------------------------------
# Tests: build_provenance_report — JSON serializability
# ---------------------------------------------------------------------------

class TestBuildProvenanceReportJsonSerializable:
    """Provenance report must be JSON-serializable (no Path objects, etc.)."""

    def test_report_is_json_serializable_single_layer(self):
        layers = [_make_layer("repo", agents=[_agent("my-agent")], path="/p/manifest.toml")]
        merged = merge_components(layers)
        report = build_provenance_report(merged, Path("/p"))

        # Should not raise
        serialized = json.dumps(report)
        assert "my-agent" in serialized

    def test_report_is_json_serializable_with_overrides(self):
        kit = _make_layer("kit", agents=[_agent("shared")], path="/p/kit/manifest.toml")
        repo = _make_layer("repo", agents=[_agent("shared")], path="/p/config/manifest.toml")
        merged = merge_components([kit, repo])
        report = build_provenance_report(merged, Path("/p"))

        serialized = json.dumps(report)
        data = json.loads(serialized)
        assert data["components"][0]["overridden"][0]["scope"] == "kit"

    def test_report_roundtrip_preserves_structure(self):
        layers = [
            _make_layer(
                "repo",
                agents=[_agent("a1"), _agent("a2")],
                skills=[_skill("s1")],
                path="/root/manifest.toml",
            )
        ]
        merged = merge_components(layers)
        report = build_provenance_report(merged, Path("/root"))

        data = json.loads(json.dumps(report))
        assert len(data["components"]) == 3
        component_ids = [c["id"] for c in data["components"]]
        assert "a1" in component_ids
        assert "s1" in component_ids


# ---------------------------------------------------------------------------
# Tests: format_provenance_human
# ---------------------------------------------------------------------------

class TestFormatProvenanceHuman:
    """Human-readable provenance format matches spec."""

    def test_header_present(self):
        layers = [_make_layer("repo", agents=[_agent("my-agent")], path="/p/manifest.toml")]
        merged = merge_components(layers)
        report = build_provenance_report(merged, Path("/p"))
        output = format_provenance_human(report)

        assert "Layer Provenance Report" in output
        assert "===" in output

    def test_agent_section_labeled(self):
        layers = [_make_layer("repo", agents=[_agent("my-agent")], path="/p/manifest.toml")]
        merged = merge_components(layers)
        report = build_provenance_report(merged, Path("/p"))
        output = format_provenance_human(report)

        assert "Agents:" in output
        assert "my-agent" in output

    def test_override_annotation_present(self):
        kit = _make_layer("kit", agents=[_agent("review-agent")], path="/p/kit/manifest.toml")
        repo = _make_layer("repo", agents=[_agent("review-agent")], path="/p/config/manifest.toml")
        merged = merge_components([kit, repo])
        report = build_provenance_report(merged, Path("/p"))
        output = format_provenance_human(report)

        assert "overrides:" in output
        assert "Kit" in output

    def test_skills_section_labeled(self):
        layers = [_make_layer("repo", skills=[_skill("my-skill")], path="/p/manifest.toml")]
        merged = merge_components(layers)
        report = build_provenance_report(merged, Path("/p"))
        output = format_provenance_human(report)

        assert "Skills:" in output
        assert "my-skill" in output

    def test_empty_report_has_header(self):
        report = {"components": []}
        output = format_provenance_human(report)
        assert "Layer Provenance Report" in output


# ---------------------------------------------------------------------------
# Tests: discover_components — agents
# ---------------------------------------------------------------------------

class TestDiscoverComponentsAgents:
    """Component discovery finds agents in .claude/agents/."""

    def test_discovers_agent_md_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".claude" / "agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "my-agent.md").write_text("# My Agent\n", encoding="utf-8")
            (agents_dir / "review-agent.md").write_text("# Review\n", encoding="utf-8")

            result = discover_components(root)

            ids = [e["id"] for e in result["agents"]]
            assert "my-agent" in ids
            assert "review-agent" in ids

    def test_agent_source_path_is_absolute(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".claude" / "agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "test-agent.md").write_text("# Test\n", encoding="utf-8")

            result = discover_components(root)

            entry = result["agents"][0]
            assert Path(entry["source"]).is_absolute()

    def test_agent_description_extracted_from_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            agents_dir = root / ".claude" / "agents"
            agents_dir.mkdir(parents=True)
            content = '---\ndescription: "Handles code review"\n---\n# Agent\n'
            (agents_dir / "reviewer.md").write_text(content, encoding="utf-8")

            result = discover_components(root)

            entry = result["agents"][0]
            assert entry["description"] == "Handles code review"

    def test_empty_agents_dir_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".claude" / "agents").mkdir(parents=True)

            result = discover_components(root)

            assert result["agents"] == []

    def test_missing_agents_dir_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            result = discover_components(root)
            assert result["agents"] == []


# ---------------------------------------------------------------------------
# Tests: discover_components — skills
# ---------------------------------------------------------------------------

class TestDiscoverComponentsSkills:
    """Component discovery finds skills in .claude/skills/*/SKILL.md."""

    def test_discovers_skill_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / ".claude" / "skills" / "my-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Skill\n", encoding="utf-8")

            result = discover_components(root)

            ids = [e["id"] for e in result["skills"]]
            assert "my-skill" in ids

    def test_skill_id_is_parent_directory_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / ".claude" / "skills" / "code-review"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Skill\n", encoding="utf-8")

            result = discover_components(root)

            assert result["skills"][0]["id"] == "code-review"

    def test_skill_source_points_to_skill_md(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / ".claude" / "skills" / "test-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Skill\n", encoding="utf-8")

            result = discover_components(root)

            entry = result["skills"][0]
            assert entry["source"].endswith("SKILL.md")

    def test_empty_skills_dir_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".claude" / "skills").mkdir(parents=True)

            result = discover_components(root)

            assert result["skills"] == []

    def test_missing_skills_dir_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            result = discover_components(root)
            assert result["skills"] == []


# ---------------------------------------------------------------------------
# Tests: discover_components — empty directories
# ---------------------------------------------------------------------------

class TestDiscoverComponentsEmpty:
    """Discovery returns empty lists when directories are missing or empty."""

    def test_all_empty_when_no_claude_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            result = discover_components(root)

            assert result["agents"] == []
            assert result["skills"] == []
            assert result["workflows"] == []

    def test_workflows_empty_when_commands_dir_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".claude" / "agents").mkdir(parents=True)
            result = discover_components(root)
            assert result["workflows"] == []


# ---------------------------------------------------------------------------
# Tests: write_discovered_manifest
# ---------------------------------------------------------------------------

class TestWriteDiscoveredManifest:
    """write_discovered_manifest() writes valid manifest.toml."""

    def test_manifest_written_to_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "manifest.toml"
            discovered = {
                "agents": [{"id": "my-agent", "source": "/p/.claude/agents/my-agent.md", "description": "Test agent"}],
                "skills": [],
                "workflows": [],
            }
            write_discovered_manifest(discovered, out_path)
            assert out_path.is_file()

    def test_manifest_has_version_2(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "manifest.toml"
            write_discovered_manifest({"agents": [], "skills": [], "workflows": []}, out_path)
            data = tomllib.loads(out_path.read_text())
            assert data["manifest"]["version"] == "2.0"

    def test_manifest_contains_agent_section(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "manifest.toml"
            discovered = {
                "agents": [{"id": "my-agent", "source": "/p/.claude/agents/my-agent.md", "description": ""}],
                "skills": [],
                "workflows": [],
            }
            write_discovered_manifest(discovered, out_path)
            data = tomllib.loads(out_path.read_text())
            assert "agents" in data
            assert data["agents"][0]["id"] == "my-agent"

    def test_manifest_contains_skill_section(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "manifest.toml"
            discovered = {
                "agents": [],
                "skills": [{"id": "code-review", "source": "/p/.claude/skills/code-review/SKILL.md", "description": "Reviews code"}],
                "workflows": [],
            }
            write_discovered_manifest(discovered, out_path)
            data = tomllib.loads(out_path.read_text())
            assert "skills" in data
            assert data["skills"][0]["id"] == "code-review"
            assert data["skills"][0]["description"] == "Reviews code"

    def test_manifest_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "subdir" / "nested" / "manifest.toml"
            write_discovered_manifest({"agents": [], "skills": [], "workflows": []}, out_path)
            assert out_path.is_file()

    def test_manifest_preserves_existing_on_empty_input(self):
        # write_discovered_manifest is append-only: with no new entries to add,
        # an existing file must be left untouched.
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "manifest.toml"
            out_path.write_text("old content", encoding="utf-8")
            write_discovered_manifest({"agents": [], "skills": [], "workflows": []}, out_path)
            content = out_path.read_text()
            assert content == "old content"

    def test_manifest_roundtrip_via_tomllib(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "manifest.toml"
            discovered = {
                "agents": [
                    {"id": "agent-a", "source": "/p/a.md", "description": "Agent A"},
                    {"id": "agent-b", "source": "/p/b.md", "description": ""},
                ],
                "skills": [{"id": "my-skill", "source": "/p/SKILL.md", "description": ""}],
                "workflows": [{"id": "deploy", "source": "/p/deploy.md", "description": "Deploy workflow"}],
            }
            write_discovered_manifest(discovered, out_path)
            data = tomllib.loads(out_path.read_text())

            agent_ids = [a["id"] for a in data.get("agents", [])]
            assert "agent-a" in agent_ids
            assert "agent-b" in agent_ids
            skill_ids = [s["id"] for s in data.get("skills", [])]
            assert "my-skill" in skill_ids
            workflow_ids = [w["id"] for w in data.get("workflows", [])]
            assert "deploy" in workflow_ids

    def test_manifest_appends_new_entries_to_existing_file(self):
        # Append-only mode: existing IDs kept, new ones added.
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "manifest.toml"
            out_path.write_text('[manifest]\nversion = "2.0"\n\n', encoding="utf-8")
            discovered = {
                "agents": [{"id": "new-agent", "source": "/p/new.md", "description": "New"}],
                "skills": [],
                "workflows": [],
            }
            write_discovered_manifest(discovered, out_path)
            content = out_path.read_text()
            assert "new-agent" in content
            assert '[manifest]' in content  # original header preserved

    def test_manifest_skips_already_present_ids(self):
        # IDs already in the file must not be duplicated.
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "manifest.toml"
            initial = '[manifest]\nversion = "2.0"\n\n[[agents]]\nid = "existing"\nsource = "/p/e.md"\n\n'
            out_path.write_text(initial, encoding="utf-8")
            discovered = {
                "agents": [{"id": "existing", "source": "/p/e.md", "description": ""}],
                "skills": [],
                "workflows": [],
            }
            write_discovered_manifest(discovered, out_path)
            content = out_path.read_text()
            # Should be a no-op — only one occurrence of the ID
            assert content.count('id = "existing"') == 1


# ---------------------------------------------------------------------------
# Tests: discover_components workflow discovery and description extraction
# ---------------------------------------------------------------------------

class TestDiscoverComponentsWorkflows:
    """discover_components() picks up .claude/commands/*.md as workflows."""

    def test_finds_workflow_from_commands_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            commands_dir = root / ".claude" / "commands"
            commands_dir.mkdir(parents=True)
            (commands_dir / "deploy.md").write_text(
                "---\ndescription: Deploy workflow\n---\nContent.", encoding="utf-8"
            )
            result = discover_components(root)
            wf_ids = [w["id"] for w in result["workflows"]]
            assert "deploy" in wf_ids
            deploy = next(w for w in result["workflows"] if w["id"] == "deploy")
            assert deploy["description"] == "Deploy workflow"

    def test_description_empty_when_no_description_key(self):
        # Frontmatter present but no description: key → description is empty string.
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            commands_dir = root / ".claude" / "commands"
            commands_dir.mkdir(parents=True)
            (commands_dir / "nodesc.md").write_text(
                "---\nname: nodesc\n---\nBody.", encoding="utf-8"
            )
            result = discover_components(root)
            wf = next(w for w in result["workflows"] if w["id"] == "nodesc")
            assert wf["description"] == ""

    def test_description_empty_when_no_frontmatter(self):
        # File without --- frontmatter → description is empty string.
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            commands_dir = root / ".claude" / "commands"
            commands_dir.mkdir(parents=True)
            (commands_dir / "plain.md").write_text("Just plain content.", encoding="utf-8")
            result = discover_components(root)
            wf = next(w for w in result["workflows"] if w["id"] == "plain")
            assert wf["description"] == ""


# ---------------------------------------------------------------------------
# Tests: _escape_toml_basic_string / _format_toml_entry TOML safety
# ---------------------------------------------------------------------------

class TestTomlEscaping:
    """_format_toml_entry produces valid TOML for descriptions with special chars."""

    def test_newlines_in_description_escaped(self):
        """Newlines in description are escaped, producing a valid single-line TOML string."""
        entry = {"id": "agent-a", "description": "line1\nline2", "source": "/a.md"}
        lines = _format_toml_entry("agents", entry)
        toml_text = "\n".join(lines)
        assert "\\n" in toml_text
        assert "\nline2" not in toml_text
        # Round-trip: parse the generated TOML
        import tomllib
        data = tomllib.loads(toml_text)
        assert data["agents"][0]["description"] == "line1\nline2"

    def test_tabs_in_source_escaped(self):
        entry = {"id": "s", "source": "path\tto\tfile"}
        lines = _format_toml_entry("skills", entry)
        toml_text = "\n".join(lines)
        assert "\\t" in toml_text
        import tomllib
        data = tomllib.loads(toml_text)
        assert data["skills"][0]["source"] == "path\tto\tfile"

    def test_quotes_and_backslash_in_description(self):
        entry = {"id": "q", "description": 'say "hello\\world"'}
        lines = _format_toml_entry("agents", entry)
        toml_text = "\n".join(lines)
        import tomllib
        data = tomllib.loads(toml_text)
        assert data["agents"][0]["description"] == 'say "hello\\world"'
