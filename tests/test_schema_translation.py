"""
Tests for extended agent schema translation and skill generation.

Covers translate_agent_schema() per-tool translators and generate_manifest_skills()
implemented in agents.py for manifest v2.0 [[agents]] and [[skills]] components.

@cpt-algo:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1
@cpt-algo:cpt-cypilot-algo-project-extensibility-generate-skills:p1
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.commands.agents import (
    translate_agent_schema,
    generate_manifest_skills,
    _translate_claude_schema,
    _translate_cursor_schema,
    _translate_copilot_schema,
    _translate_codex_schema,
    _translate_windsurf_schema,
)
from cypilot.utils.manifest import AgentEntry, SkillEntry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_agent(**kwargs) -> AgentEntry:
    """Create an AgentEntry with sensible defaults."""
    defaults = {
        "id": "test-agent",
        "description": "A test agent",
        "prompt_file": "agents/test-agent.md",
        "source": "",
        "agents": [],
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


def _make_skill(**kwargs) -> SkillEntry:
    """Create a SkillEntry with sensible defaults."""
    defaults = {
        "id": "test-skill",
        "description": "A test skill",
        "prompt_file": "",
        "source": "",
        "agents": ["claude"],
        "append": None,
    }
    defaults.update(kwargs)
    return SkillEntry(**defaults)


# ---------------------------------------------------------------------------
# Test: Claude translation
# ---------------------------------------------------------------------------

class TestTranslateClaudeSchema(unittest.TestCase):

    def test_claude_readwrite_mode(self):
        agent = _make_agent(mode="readwrite")
        result = _translate_claude_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn("tools:", frontmatter)
        self.assertIn("Write", frontmatter)
        self.assertFalse(result["skip"])

    def test_claude_readonly_mode(self):
        agent = _make_agent(mode="readonly")
        result = _translate_claude_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn("disallowedTools:", frontmatter)
        self.assertIn("Write", frontmatter)

    def test_claude_with_tools_list(self):
        agent = _make_agent(tools=["Bash", "Read", "WebSearch"])
        result = _translate_claude_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn("tools:", frontmatter)
        self.assertIn("WebSearch", frontmatter)

    def test_claude_with_disallowed_tools(self):
        agent = _make_agent(disallowed_tools=["Bash", "Write"])
        result = _translate_claude_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn("disallowedTools:", frontmatter)
        self.assertIn("Bash", frontmatter)

    def test_claude_with_model(self):
        agent = _make_agent(model="claude-opus-4-5")
        result = _translate_claude_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn("model: claude-opus-4-5", frontmatter)

    def test_claude_with_isolation(self):
        agent = _make_agent(isolation=True)
        result = _translate_claude_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn("isolation: worktree", frontmatter)

    def test_claude_with_color(self):
        agent = _make_agent(color="blue")
        result = _translate_claude_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn("color: blue", frontmatter)

    def test_claude_with_memory_dir(self):
        agent = _make_agent(memory_dir=".memory/agent")
        result = _translate_claude_schema(agent)
        # memory_dir is appended as a note in body_suffix, not frontmatter or body_prefix
        self.assertEqual(result["body_prefix"], "")
        self.assertIn(".memory/agent", result["body_suffix"])
        self.assertIn("---", result["body_suffix"])

    def test_claude_no_memory_dir_no_body_prefix(self):
        agent = _make_agent()
        result = _translate_claude_schema(agent)
        self.assertEqual(result["body_prefix"], "")

    def test_claude_mcp_tools_filtered_from_tools(self):
        """mcp__* entries are stripped from tools: frontmatter."""
        agent = _make_agent(tools=["Bash", "mcp__standctl__standctl_deploy", "Read"])
        result = _translate_claude_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn("tools:", frontmatter)
        self.assertIn("Bash", frontmatter)
        self.assertIn("Read", frontmatter)
        self.assertNotIn("mcp__", frontmatter)

    def test_claude_mcp_tools_only_omits_tools_field(self):
        """When tools list contains only mcp__* entries, tools: field is omitted and mode default applies."""
        agent = _make_agent(tools=["mcp__standctl__standctl_deploy"], mode="readwrite")
        result = _translate_claude_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        # Field must not contain mcp__ tools; mode default readwrite applies
        self.assertNotIn("mcp__", frontmatter)
        # Falls through to readwrite default
        self.assertIn("tools:", frontmatter)
        self.assertIn("Write", frontmatter)

    def test_claude_mcp_tools_filtered_from_disallowed_tools(self):
        """mcp__* entries are stripped from disallowedTools: frontmatter."""
        agent = _make_agent(disallowed_tools=["Write", "mcp__standctl__standctl_deploy"])
        result = _translate_claude_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn("disallowedTools:", frontmatter)
        self.assertIn("Write", frontmatter)
        self.assertNotIn("mcp__", frontmatter)

    def test_claude_mcp_tools_only_disallowed_omits_field(self):
        """When disallowed_tools contains only mcp__* entries, disallowedTools: field is omitted and mode default applies."""
        agent = _make_agent(disallowed_tools=["mcp__standctl__standctl_deploy"], mode="readwrite")
        result = _translate_claude_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertNotIn("mcp__", frontmatter)
        # Falls through to readwrite default
        self.assertIn("tools:", frontmatter)
        self.assertIn("Write", frontmatter)


# ---------------------------------------------------------------------------
# Test: tools + disallowed_tools mutual exclusivity
# ---------------------------------------------------------------------------

class TestMutualExclusivity(unittest.TestCase):

    def test_tools_and_disallowed_tools_raises(self):
        agent = _make_agent(tools=["Bash"], disallowed_tools=["Write"])
        with self.assertRaises(ValueError) as ctx:
            translate_agent_schema(agent, "claude")
        self.assertIn("mutually exclusive", str(ctx.exception).lower())

    def test_tools_only_valid(self):
        agent = _make_agent(tools=["Bash", "Read"])
        result = translate_agent_schema(agent, "claude")
        self.assertFalse(result["skip"])

    def test_disallowed_tools_only_valid(self):
        agent = _make_agent(disallowed_tools=["Write"])
        result = translate_agent_schema(agent, "claude")
        self.assertFalse(result["skip"])


# ---------------------------------------------------------------------------
# Test: Cursor translation
# ---------------------------------------------------------------------------

class TestTranslateCursorSchema(unittest.TestCase):

    def test_cursor_readwrite_mode(self):
        agent = _make_agent(mode="readwrite")
        result = _translate_cursor_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn("tools:", frontmatter)
        self.assertIn("edit", frontmatter)
        self.assertFalse(result["skip"])

    def test_cursor_readonly_mode(self):
        agent = _make_agent(mode="readonly")
        result = _translate_cursor_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn("readonly: true", frontmatter)

    def test_cursor_model_passthrough(self):
        agent = _make_agent(model="gpt-4o")
        result = _translate_cursor_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn("model: gpt-4o", frontmatter)

    def test_cursor_ignores_color(self):
        agent = _make_agent(color="red")
        result = _translate_cursor_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertNotIn("color", frontmatter)

    def test_cursor_ignores_memory_dir(self):
        agent = _make_agent(memory_dir=".memory/agent")
        result = _translate_cursor_schema(agent)
        self.assertEqual(result["body_prefix"], "")


# ---------------------------------------------------------------------------
# Test: Copilot translation
# ---------------------------------------------------------------------------

class TestTranslateCopilotSchema(unittest.TestCase):

    def test_copilot_readwrite_tools_star(self):
        agent = _make_agent(mode="readwrite")
        result = _translate_copilot_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn('"*"', frontmatter)
        self.assertFalse(result["skip"])

    def test_copilot_readonly_tools_array(self):
        agent = _make_agent(mode="readonly")
        result = _translate_copilot_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn('"read"', frontmatter)
        self.assertIn('"search"', frontmatter)

    def test_copilot_explicit_tools_array(self):
        agent = _make_agent(tools=["read", "write"])
        result = _translate_copilot_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertIn("tools:", frontmatter)

    def test_copilot_no_model_support(self):
        agent = _make_agent(model="claude-opus-4-5")
        result = _translate_copilot_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertNotIn("model:", frontmatter)


# ---------------------------------------------------------------------------
# Test: Codex (OpenAI) translation
# ---------------------------------------------------------------------------

class TestTranslateCodexSchema(unittest.TestCase):

    def test_codex_readonly_sandbox_mode(self):
        agent = _make_agent(mode="readonly")
        result = _translate_codex_schema(agent)
        self.assertIn("sandbox_mode", result)
        self.assertEqual(result["sandbox_mode"], "read-only")
        self.assertFalse(result["skip"])

    def test_codex_readwrite_sandbox_mode(self):
        agent = _make_agent(mode="readwrite")
        result = _translate_codex_schema(agent)
        self.assertEqual(result["sandbox_mode"], "workspace-write")

    def test_codex_model_passthrough(self):
        agent = _make_agent(model="gpt-4o")
        result = _translate_codex_schema(agent)
        self.assertEqual(result["model"], "gpt-4o")

    def test_codex_developer_instructions_field(self):
        agent = _make_agent(description="My codex agent")
        result = _translate_codex_schema(agent)
        self.assertIn("developer_instructions", result)


# ---------------------------------------------------------------------------
# Test: Windsurf translation (skip)
# ---------------------------------------------------------------------------

class TestTranslateWindsurfSchema(unittest.TestCase):

    def test_windsurf_skip_true(self):
        agent = _make_agent()
        result = _translate_windsurf_schema(agent)
        self.assertTrue(result["skip"])

    def test_windsurf_skip_reason_present(self):
        agent = _make_agent()
        result = _translate_windsurf_schema(agent)
        self.assertIn("skip_reason", result)
        self.assertIsInstance(result["skip_reason"], str)
        self.assertGreater(len(result["skip_reason"]), 0)

    def test_windsurf_via_translate_agent_schema(self):
        agent = _make_agent()
        result = translate_agent_schema(agent, "windsurf")
        self.assertTrue(result["skip"])


# ---------------------------------------------------------------------------
# Test: translate_agent_schema dispatch
# ---------------------------------------------------------------------------

class TestTranslateAgentSchemaDispatch(unittest.TestCase):

    def test_dispatch_to_claude(self):
        agent = _make_agent()
        result = translate_agent_schema(agent, "claude")
        self.assertIn("frontmatter", result)
        self.assertFalse(result["skip"])

    def test_dispatch_to_cursor(self):
        agent = _make_agent()
        result = translate_agent_schema(agent, "cursor")
        self.assertIn("frontmatter", result)

    def test_dispatch_to_copilot(self):
        agent = _make_agent()
        result = translate_agent_schema(agent, "copilot")
        self.assertIn("frontmatter", result)

    def test_dispatch_to_openai(self):
        agent = _make_agent()
        result = translate_agent_schema(agent, "openai")
        self.assertIn("sandbox_mode", result)

    def test_dispatch_unknown_tool_raises(self):
        agent = _make_agent()
        with self.assertRaises(ValueError):
            translate_agent_schema(agent, "unknown-tool")


# ---------------------------------------------------------------------------
# Test: generate_manifest_skills
# ---------------------------------------------------------------------------

class TestGenerateManifestSkills(unittest.TestCase):

    def test_skill_generated_for_matching_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            # Create source skill file
            src = project_root / "skills" / "my-skill.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Skill\nDo something useful.", encoding="utf-8")

            skills = {
                "my-skill": SkillEntry(
                    id="my-skill",
                    description="A test skill",
                    prompt_file="",
                    source=str(src),
                    agents=["claude"],
                )
            }
            result = generate_manifest_skills(skills, "claude", project_root, dry_run=False)
            self.assertGreater(len(result["created"]) + len(result["updated"]), 0)
            # Verify output file exists
            out_path = project_root / ".claude" / "skills" / "my-skill" / "SKILL.md"
            self.assertTrue(out_path.exists(), f"Expected {out_path} to exist")

    def test_skill_not_generated_for_non_matching_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "skills" / "my-skill.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Skill", encoding="utf-8")

            skills = {
                "my-skill": SkillEntry(
                    id="my-skill",
                    description="A test skill",
                    prompt_file="",
                    source=str(src),
                    agents=["cursor"],  # only cursor, not claude
                )
            }
            result = generate_manifest_skills(skills, "claude", project_root, dry_run=False)
            self.assertEqual(len(result["created"]), 0)
            self.assertEqual(len(result["updated"]), 0)

    def test_skill_empty_agents_list_generates_for_all_targets(self):
        """Skills with empty agents list are generated for all targets (consistent with agents)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "skills" / "my-skill.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Skill", encoding="utf-8")

            skills = {
                "my-skill": SkillEntry(
                    id="my-skill",
                    description="A test skill",
                    prompt_file="",
                    source=str(src),
                    agents=[],  # empty = all targets
                )
            }
            result = generate_manifest_skills(skills, "claude", project_root, dry_run=False)
            # With empty agents list, skill is generated for all targets
            self.assertGreater(len(result["created"]) + len(result["updated"]), 0)

    def test_skill_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "skills" / "my-skill.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Skill", encoding="utf-8")

            skills = {
                "my-skill": SkillEntry(
                    id="my-skill",
                    description="A test skill",
                    prompt_file="",
                    source=str(src),
                    agents=["claude"],
                )
            }
            generate_manifest_skills(skills, "claude", project_root, dry_run=True)
            out_path = project_root / ".claude" / "skills" / "my-skill" / "SKILL.md"
            self.assertFalse(out_path.exists(), "dry_run=True must not write files")

    def test_skill_output_path_cursor(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "skills" / "cursor-skill.md"
            src.parent.mkdir(parents=True)
            src.write_text("# Cursor Skill", encoding="utf-8")

            skills = {
                "cursor-skill": SkillEntry(
                    id="cursor-skill",
                    description="A cursor skill",
                    prompt_file="",
                    source=str(src),
                    agents=["cursor"],
                )
            }
            generate_manifest_skills(skills, "cursor", project_root, dry_run=False)
            out_path = project_root / ".cursor" / "rules" / "cursor-skill.mdc"
            self.assertTrue(out_path.exists(), f"Expected {out_path} to exist")

    def test_skill_result_dict_has_required_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result = generate_manifest_skills({}, "claude", project_root, dry_run=False)
            self.assertIn("created", result)
            self.assertIn("updated", result)
            self.assertIn("unchanged", result)

    def test_claude_skill_has_yaml_frontmatter(self):
        """Claude skill output includes YAML frontmatter with name and description."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "skills" / "standctl.md"
            src.parent.mkdir(parents=True)
            src.write_text("# Standctl\nMCP tools guide.", encoding="utf-8")

            skills = {
                "standctl": SkillEntry(
                    id="standctl",
                    description="Standctl MCP tools usage guide",
                    prompt_file="",
                    source=str(src),
                    agents=["claude"],
                )
            }
            generate_manifest_skills(skills, "claude", project_root, dry_run=False)
            out_path = project_root / ".claude" / "skills" / "standctl" / "SKILL.md"
            content = out_path.read_text(encoding="utf-8")
            # Claude skills must have YAML frontmatter
            self.assertTrue(content.startswith("---"), "Claude skill must start with ---")
            self.assertIn("name: standctl", content)
            self.assertIn('description: "Standctl MCP tools usage guide"', content)
            # Prompt body must also appear after frontmatter
            self.assertIn("# Standctl", content)

    def test_non_claude_skill_has_no_yaml_frontmatter(self):
        """Non-Claude skill output does not get YAML frontmatter injected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "skills" / "my-rule.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Rule\nFollow this.", encoding="utf-8")

            skills = {
                "my-rule": SkillEntry(
                    id="my-rule",
                    description="A cursor rule",
                    prompt_file="",
                    source=str(src),
                    agents=["cursor"],
                )
            }
            generate_manifest_skills(skills, "cursor", project_root, dry_run=False)
            out_path = project_root / ".cursor" / "rules" / "my-rule.mdc"
            content = out_path.read_text(encoding="utf-8")
            # Cursor skill: content is passed through as-is (no injected frontmatter)
            self.assertTrue(content.startswith("# My Rule"), "Cursor skill must not have injected frontmatter")


# ---------------------------------------------------------------------------
# Test: memory_dir body_suffix format (G3)
# ---------------------------------------------------------------------------

class TestMemoryDirBodySuffix(unittest.TestCase):

    def test_memory_dir_appended_as_suffix_not_prefix(self):
        """memory_dir appears in body_suffix, body_prefix is empty."""
        agent = _make_agent(memory_dir=".claude/agent-memory/my-agent")
        result = _translate_claude_schema(agent)
        self.assertEqual(result["body_prefix"], "")
        self.assertIn(".claude/agent-memory/my-agent", result["body_suffix"])

    def test_memory_dir_suffix_format(self):
        """body_suffix uses the proposal's markdown HR + italic format."""
        agent = _make_agent(memory_dir=".claude/agent-memory/my-agent")
        result = _translate_claude_schema(agent)
        suffix = result["body_suffix"]
        # Must contain a markdown HR separator and italic note
        self.assertIn("---", suffix)
        self.assertIn("*Agent memory directory:", suffix)
        self.assertIn("`", suffix)

    def test_no_memory_dir_no_suffix(self):
        agent = _make_agent()
        result = _translate_claude_schema(agent)
        self.assertEqual(result.get("body_suffix", ""), "")

    def test_memory_dir_not_in_frontmatter(self):
        """memory_dir must NOT appear as a frontmatter field."""
        agent = _make_agent(memory_dir=".claude/agent-memory/my-agent")
        result = _translate_claude_schema(agent)
        frontmatter = "\n".join(result["frontmatter"])
        self.assertNotIn("memory:", frontmatter)
        self.assertNotIn("memory_dir", frontmatter)


if __name__ == "__main__":
    unittest.main()
