"""
Tests for generate_manifest_agents() — the manifest v2.0 agent file generation function.

Covers generate_manifest_agents() implemented in agents.py for manifest v2.0
[[agents]] components. Symmetric counterpart to generate_manifest_skills().

@cpt-algo:cpt-cypilot-algo-project-extensibility-generate-agents:p1
@cpt-dod:cpt-cypilot-dod-project-extensibility-agents-generation:p1
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.commands.agents import generate_manifest_agents
from cypilot.utils.manifest import AgentEntry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_agent(**kwargs) -> AgentEntry:
    """Create an AgentEntry with sensible defaults."""
    defaults = {
        "id": "test-agent",
        "description": "A test agent",
        "prompt_file": "",
        "source": "",
        "agents": ["claude"],
        "append": None,
        "mode": "readwrite",
        "isolation": False,
        "model": "",
        "tools": [],
        "disallowed_tools": [],
        "color": "",
        "memory_dir": "",
    }
    defaults.update(kwargs)
    return AgentEntry(**defaults)


# ---------------------------------------------------------------------------
# Test: agent generated for matching target (claude)
# ---------------------------------------------------------------------------

class TestGenerateManifestAgentsBasic(unittest.TestCase):

    def test_agent_generated_for_matching_target_claude(self):
        """Agent is generated when target is in agents list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Agent\nDo something useful.", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    description="A test agent",
                    source=str(src),
                    agents=["claude"],
                )
            }
            result = generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            self.assertGreater(len(result["created"]) + len(result["updated"]), 0)
            out_path = project_root / ".claude" / "agents" / "my-agent.md"
            self.assertTrue(out_path.exists(), f"Expected {out_path} to exist")

    def test_agent_not_generated_for_non_matching_target(self):
        """Agent is skipped when target is not in agents list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Agent", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    source=str(src),
                    agents=["cursor"],  # only cursor, not claude
                )
            }
            result = generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            self.assertEqual(len(result["created"]), 0)
            self.assertEqual(len(result["updated"]), 0)

    def test_agent_skipped_when_translate_returns_skip_true(self):
        """Windsurf target causes translate_agent_schema to return skip=True — agent skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Agent", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    source=str(src),
                    agents=["windsurf"],
                )
            }
            result = generate_manifest_agents(agents, "windsurf", project_root, dry_run=False)
            self.assertEqual(len(result["created"]), 0)
            self.assertEqual(len(result["updated"]), 0)


# ---------------------------------------------------------------------------
# Test: Correct output paths per target
# ---------------------------------------------------------------------------

class TestGenerateManifestAgentsOutputPaths(unittest.TestCase):

    def _run_with_target(self, target: str, tmpdir: str) -> Path:
        project_root = Path(tmpdir)
        src = project_root / "agents" / "my-agent.md"
        src.parent.mkdir(parents=True)
        src.write_text("# My Agent", encoding="utf-8")

        agents = {
            "my-agent": _make_agent(
                id="my-agent",
                source=str(src),
                agents=[target],
            )
        }
        generate_manifest_agents(agents, target, project_root, dry_run=False)
        return project_root

    def test_output_path_claude(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = self._run_with_target("claude", tmpdir)
            out_path = project_root / ".claude" / "agents" / "my-agent.md"
            self.assertTrue(out_path.exists(), f"Expected {out_path} to exist")

    def test_output_path_cursor(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = self._run_with_target("cursor", tmpdir)
            out_path = project_root / ".cursor" / "agents" / "my-agent.mdc"
            self.assertTrue(out_path.exists(), f"Expected {out_path} to exist")

    def test_output_path_copilot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = self._run_with_target("copilot", tmpdir)
            out_path = project_root / ".github" / "agents" / "my-agent.md"
            self.assertTrue(out_path.exists(), f"Expected {out_path} to exist")

    def test_output_path_openai(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = self._run_with_target("openai", tmpdir)
            out_path = project_root / ".agents" / "my-agent" / "agent.toml"
            self.assertTrue(out_path.exists(), f"Expected {out_path} to exist")


# ---------------------------------------------------------------------------
# Test: created/updated/unchanged tracking
# ---------------------------------------------------------------------------

class TestGenerateManifestAgentsTracking(unittest.TestCase):

    def test_result_dict_has_required_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result = generate_manifest_agents({}, "claude", project_root, dry_run=False)
            self.assertIn("created", result)
            self.assertIn("updated", result)
            self.assertIn("unchanged", result)
            self.assertIn("outputs", result)

    def test_created_tracking(self):
        """New agent file is tracked in created list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Agent", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    source=str(src),
                    agents=["claude"],
                )
            }
            result = generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            self.assertEqual(len(result["created"]), 1)
            self.assertEqual(len(result["updated"]), 0)

    def test_updated_tracking(self):
        """Existing agent file with changed content is tracked in updated list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Agent", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    source=str(src),
                    agents=["claude"],
                )
            }
            # First run — creates
            generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            # Modify source so content changes
            src.write_text("# My Agent Updated", encoding="utf-8")
            result = generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            self.assertEqual(len(result["updated"]), 1)
            self.assertEqual(len(result["created"]), 0)

    def test_unchanged_tracking(self):
        """Existing agent file with identical content is tracked in unchanged list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Agent", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    source=str(src),
                    agents=["claude"],
                )
            }
            # First run — creates
            generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            # Second run — unchanged
            result = generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            self.assertEqual(len(result["unchanged"]), 1)
            self.assertEqual(len(result["created"]), 0)
            self.assertEqual(len(result["updated"]), 0)


# ---------------------------------------------------------------------------
# Test: dry_run mode
# ---------------------------------------------------------------------------

class TestGenerateManifestAgentsDryRun(unittest.TestCase):

    def test_dry_run_does_not_write_files(self):
        """dry_run=True computes actions but does not write files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Agent", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    source=str(src),
                    agents=["claude"],
                )
            }
            result = generate_manifest_agents(agents, "claude", project_root, dry_run=True)
            out_path = project_root / ".claude" / "agents" / "my-agent.md"
            self.assertFalse(out_path.exists(), "dry_run=True must not write files")
            # Still tracks the would-be created action
            self.assertEqual(len(result["created"]), 1)


# ---------------------------------------------------------------------------
# Test: missing prompt_file handled gracefully
# ---------------------------------------------------------------------------

class TestGenerateManifestAgentsMissingSource(unittest.TestCase):

    def test_agent_with_no_source_or_prompt_file_skipped(self):
        """Agent with no source or prompt_file is skipped gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            agents = {
                "no-source": _make_agent(
                    id="no-source",
                    source="",
                    prompt_file="",
                    agents=["claude"],
                )
            }
            # Should not raise — just skip
            result = generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            self.assertEqual(len(result["created"]), 0)

    def test_agent_with_missing_prompt_file_skipped(self):
        """Agent with nonexistent prompt_file path is skipped gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            agents = {
                "missing-file": _make_agent(
                    id="missing-file",
                    source="",
                    prompt_file="agents/does-not-exist.md",
                    agents=["claude"],
                )
            }
            result = generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            self.assertEqual(len(result["created"]), 0)


# ---------------------------------------------------------------------------
# Test: assembled file contains frontmatter
# ---------------------------------------------------------------------------

class TestGenerateManifestAgentsFileContent(unittest.TestCase):

    def test_assembled_file_contains_yaml_frontmatter(self):
        """Output file contains YAML frontmatter block with name and description."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Agent\nDo something.", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    description="A described agent",
                    source=str(src),
                    agents=["claude"],
                )
            }
            generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            out_path = project_root / ".claude" / "agents" / "my-agent.md"
            content = out_path.read_text(encoding="utf-8")
            self.assertIn("---", content)
            self.assertIn("name:", content)
            self.assertIn("description:", content)

    def test_assembled_file_contains_prompt_body(self):
        """Output file contains the original prompt content after frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("My unique prompt content.", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    source=str(src),
                    agents=["claude"],
                )
            }
            generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            out_path = project_root / ".claude" / "agents" / "my-agent.md"
            content = out_path.read_text(encoding="utf-8")
            self.assertIn("My unique prompt content.", content)

    def test_assembled_file_uses_prompt_file_fallback(self):
        """Output file uses prompt_file when source is not set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("Prompt file content.", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    source="",
                    prompt_file=str(src),
                    agents=["claude"],
                )
            }
            generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            out_path = project_root / ".claude" / "agents" / "my-agent.md"
            self.assertTrue(out_path.exists())
            content = out_path.read_text(encoding="utf-8")
            self.assertIn("Prompt file content.", content)

    def test_body_prefix_injected_when_memory_dir_set(self):
        """When Claude translation produces body_prefix (memory_dir), it appears in output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("Prompt.", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    source=str(src),
                    agents=["claude"],
                    memory_dir=".memory/my-agent",
                )
            }
            generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            out_path = project_root / ".claude" / "agents" / "my-agent.md"
            content = out_path.read_text(encoding="utf-8")
            self.assertIn(".memory/my-agent", content)


# ---------------------------------------------------------------------------
# Test: path traversal prevention in _write_or_skip
# ---------------------------------------------------------------------------

class TestGenerateManifestAgentsPathTraversal(unittest.TestCase):

    def test_path_traversal_agent_id_skipped(self):
        """Agent ID with ../ sequences is skipped due to invalid TOML key validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "bad.md"
            src.parent.mkdir(parents=True)
            src.write_text("content", encoding="utf-8")
            agents = {
                "../../../outside": _make_agent(
                    id="../../../outside",
                    description="bad agent",
                    source=str(src),
                    agents=["openai"],
                    model="claude-opus",
                )
            }
            result = generate_manifest_agents(agents, "openai", project_root, dry_run=False)
            # Agent should be skipped — no outputs generated
            self.assertEqual(result["created"], [])
            self.assertEqual(result["outputs"], [])


# ---------------------------------------------------------------------------
# Test: OpenAI/Codex TOML format edge cases
# ---------------------------------------------------------------------------

class TestGenerateManifestAgentsOpenAI(unittest.TestCase):

    def _make_src(self, project_root: Path) -> Path:
        src = project_root / "agents" / "my-agent.md"
        src.parent.mkdir(parents=True)
        src.write_text("Agent prompt content.", encoding="utf-8")
        return src

    def test_openai_model_written_when_set(self):
        """OpenAI TOML output includes model line when agent.model is set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = self._make_src(project_root)
            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    description="Test agent",
                    source=str(src),
                    agents=["openai"],
                    model="claude-opus-4",
                )
            }
            generate_manifest_agents(agents, "openai", project_root, dry_run=False)
            out = project_root / ".agents" / "my-agent" / "agent.toml"
            self.assertTrue(out.exists())
            content = out.read_text()
            self.assertIn('model = "claude-opus-4"', content)

    def test_openai_variables_substituted(self):
        """OpenAI TOML output substitutes layer variables."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "sub-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("Hello {project_name}.", encoding="utf-8")
            agents = {
                "sub-agent": _make_agent(
                    id="sub-agent",
                    description="Agent with {project_name}",
                    source=str(src),
                    agents=["openai"],
                )
            }
            generate_manifest_agents(
                agents, "openai", project_root, dry_run=False,
                variables={"project_name": "MyProject"},
            )
            out = project_root / ".agents" / "sub-agent" / "agent.toml"
            content = out.read_text()
            self.assertIn("MyProject", content)

    def test_openai_developer_instructions_contains_source_body(self):
        """OpenAI TOML developer_instructions must contain the source prompt body, not just description."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            prompt_body = "You are an expert code reviewer.\nAnalyze all files carefully."
            src.write_text(prompt_body, encoding="utf-8")
            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    description="Code review agent",
                    source=str(src),
                    agents=["openai"],
                )
            }
            generate_manifest_agents(agents, "openai", project_root, dry_run=False)
            out = project_root / ".agents" / "my-agent" / "agent.toml"
            self.assertTrue(out.exists())
            content = out.read_text()
            # The source prompt body must appear in developer_instructions, not just the description
            self.assertIn("You are an expert code reviewer.", content)
            self.assertIn("Analyze all files carefully.", content)

    def test_openai_append_included_in_output(self):
        """OpenAI TOML output includes agent.append content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = self._make_src(project_root)
            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    description="Test agent",
                    source=str(src),
                    agents=["openai"],
                    append="# extra section",
                )
            }
            generate_manifest_agents(agents, "openai", project_root, dry_run=False)
            out = project_root / ".agents" / "my-agent" / "agent.toml"
            content = out.read_text()
            self.assertIn("# extra section", content)


# ---------------------------------------------------------------------------
# Test: translate_agent_schema ValueError is caught and logged
# ---------------------------------------------------------------------------

class TestGenerateManifestAgentsTranslateError(unittest.TestCase):

    def test_conflicting_tools_skips_agent(self):
        """Agent with both tools and disallowed_tools is skipped (ValueError caught)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "conflict.md"
            src.parent.mkdir(parents=True)
            src.write_text("content", encoding="utf-8")
            agents = {
                "conflict": _make_agent(
                    id="conflict",
                    description="conflicting agent",
                    source=str(src),
                    agents=["claude"],
                    tools=["read"],
                    disallowed_tools=["write"],
                )
            }
            result = generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            # No file should be created — agent was skipped
            self.assertEqual(result["created"], [])
            self.assertIn("errors", result)


if __name__ == "__main__":
    unittest.main()
