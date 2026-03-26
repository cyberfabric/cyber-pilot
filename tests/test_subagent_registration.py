"""
Tests for subagent registration in the agents command.

Covers _discover_kit_agents(), _render_toml_agents(), per-tool template
functions, and subagent generation integration via _process_single_agent()
for all supported tools.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.commands.agents import (
    _agent_template_claude,
    _agent_template_copilot,
    _agent_template_cursor,
    _default_agents_config,
    _discover_kit_agents,
    _process_single_agent,
    _render_toml_agent,
    _TOOL_AGENT_CONFIG,
)


# ── Helpers ─────────────────────────────────────────────────────────

_AGENTS_TOML = """\
[agents.cypilot-codegen]
description = "Cypilot code generator. Implements fully-specified requirements."
prompt_file = "agents/cypilot-codegen.md"
mode = "readwrite"
isolation = true
model = "inherit"

[agents.cypilot-pr-review]
description = "Cypilot PR reviewer. Checklist-based review in isolated context."
prompt_file = "agents/cypilot-pr-review.md"
mode = "readonly"
isolation = false
model = "fast"
"""


def _make_kit(kit_dir: Path) -> None:
    """Create a minimal SDLC kit with agents.toml and agent prompt files."""
    kit_dir.mkdir(parents=True, exist_ok=True)
    (kit_dir / "agents.toml").write_text(_AGENTS_TOML, encoding="utf-8")
    agents_dir = kit_dir / "agents"
    agents_dir.mkdir(exist_ok=True)
    (agents_dir / "cypilot-codegen.md").write_text(
        "You are a Cypilot code generation agent.\n", encoding="utf-8",
    )
    (agents_dir / "cypilot-pr-review.md").write_text(
        "You are a Cypilot PR review agent.\n", encoding="utf-8",
    )


def _make_semantic_agent(
    name: str = "test-agent",
    description: str = "Test agent",
    mode: str = "readwrite",
    isolation: bool = False,
    model: str = "inherit",
) -> dict:
    return {
        "name": name,
        "description": description,
        "prompt_file_abs": Path(tempfile.gettempdir()) / "agents" / f"{name}.md",
        "mode": mode,
        "isolation": isolation,
        "model": model,
        "source_dir": Path(tempfile.gettempdir()) / "kit",
    }


# ── Discovery tests ────────────────────────────────────────────────

class TestDiscoverKitAgents(unittest.TestCase):
    """Tests for _discover_kit_agents() — core skill + kit discovery."""

    def _make_core_tree(self, root: Path) -> Path:
        """Build cypilot tree with agents in core skill area."""
        cypilot = root / "cypilot_src"
        skill_dir = cypilot / "skills" / "cypilot"
        _make_kit(skill_dir)
        return cypilot

    def _make_kit_tree(self, root: Path, kit_name: str = "sdlc") -> Path:
        """Build cypilot tree with agents in a kit."""
        cypilot = root / "cypilot_src"
        kit_dir = cypilot / "config" / "kits" / kit_name
        _make_kit(kit_dir)
        return cypilot

    def test_discovers_agents_from_core_skill(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._make_core_tree(root)
            agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(len(agents), 2)
            names = {a["name"] for a in agents}
            self.assertEqual(names, {"cypilot-codegen", "cypilot-pr-review"})

    def test_discovers_agents_from_kit(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._make_kit_tree(root)
            agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(len(agents), 2)
            names = {a["name"] for a in agents}
            self.assertEqual(names, {"cypilot-codegen", "cypilot-pr-review"})

    def test_agents_have_semantic_fields(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._make_core_tree(root)
            agents = _discover_kit_agents(cypilot, root)
            codegen = next(a for a in agents if a["name"] == "cypilot-codegen")
            self.assertEqual(codegen["mode"], "readwrite")
            self.assertTrue(codegen["isolation"])
            self.assertEqual(codegen["model"], "inherit")
            self.assertIsNotNone(codegen["prompt_file_abs"])
            self.assertTrue(str(codegen["prompt_file_abs"]).endswith("cypilot-codegen.md"))

    def test_pr_review_is_readonly_fast(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._make_core_tree(root)
            agents = _discover_kit_agents(cypilot, root)
            pr = next(a for a in agents if a["name"] == "cypilot-pr-review")
            self.assertEqual(pr["mode"], "readonly")
            self.assertFalse(pr["isolation"])
            self.assertEqual(pr["model"], "fast")

    def test_no_agents_returns_empty(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            (cypilot / "skills" / "cypilot").mkdir(parents=True)
            (cypilot / "config" / "kits").mkdir(parents=True)
            agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(agents, [])

    def test_malformed_toml_skipped(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            kit_dir = cypilot / "config" / "kits" / "bad"
            kit_dir.mkdir(parents=True)
            (kit_dir / "agents.toml").write_text("not valid [toml", encoding="utf-8")
            agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(agents, [])

    def test_prompt_file_path_traversal_rejected(self):
        """Agent with prompt_file escaping source dir is skipped."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            kit_dir = cypilot / "config" / "kits" / "evil"
            kit_dir.mkdir(parents=True)
            (kit_dir / "agents.toml").write_text(
                '[agents.bad-agent]\ndescription = "escape"\n'
                'prompt_file = "../../../etc/passwd"\nmode = "readonly"\n',
                encoding="utf-8",
            )
            agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(agents, [])

    def test_agent_name_with_path_separator_rejected(self):
        """Agent name containing path separators is skipped."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            kit_dir = cypilot / "config" / "kits" / "evil"
            kit_dir.mkdir(parents=True)
            (kit_dir / "agents.toml").write_text(
                '[agents."../etc/shadow"]\ndescription = "escape"\nprompt_file = "x.md"\n',
                encoding="utf-8",
            )
            agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(agents, [])

    def test_invalid_mode_rejected(self):
        """Agent with unrecognized mode is skipped."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            kit_dir = cypilot / "config" / "kits" / "bad"
            kit_dir.mkdir(parents=True)
            (kit_dir / "agents.toml").write_text(
                '[agents.my-agent]\ndescription = "test"\n'
                'prompt_file = "x.md"\nmode = "read_only"\n',
                encoding="utf-8",
            )
            (kit_dir / "x.md").write_text("prompt\n", encoding="utf-8")
            agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(agents, [])

    def test_unknown_model_passthrough(self):
        """Agent with unrecognized model is allowed as passthrough (warn, not skip)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            kit_dir = cypilot / "config" / "kits" / "bad"
            kit_dir.mkdir(parents=True)
            (kit_dir / "agents.toml").write_text(
                '[agents.my-agent]\ndescription = "test"\n'
                'prompt_file = "x.md"\nmodel = "turbo"\n',
                encoding="utf-8",
            )
            (kit_dir / "x.md").write_text("prompt\n", encoding="utf-8")
            agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(len(agents), 1)
            self.assertEqual(agents[0]["model"], "turbo")

    def test_kit_wins_over_core_duplicate(self):
        """Kit agents take precedence over core skill agents with same name."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            # Core agent
            skill_dir = cypilot / "skills" / "cypilot"
            skill_dir.mkdir(parents=True)
            (skill_dir / "x.md").write_text("core prompt", encoding="utf-8")
            (skill_dir / "agents.toml").write_text(
                '[agents.my-agent]\ndescription = "from core"\nprompt_file = "x.md"\n',
                encoding="utf-8",
            )
            # Kit agent with same name
            kit_dir = cypilot / "config" / "kits" / "sdlc"
            kit_dir.mkdir(parents=True)
            (kit_dir / "x.md").write_text("kit prompt", encoding="utf-8")
            (kit_dir / "agents.toml").write_text(
                '[agents.my-agent]\ndescription = "from kit"\nprompt_file = "x.md"\n',
                encoding="utf-8",
            )
            agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(len(agents), 1)
            self.assertEqual(agents[0]["description"], "from kit")

    def test_kit_duplicate_names_first_wins(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            # Kit "aaa" comes first alphabetically
            kit_a = cypilot / "config" / "kits" / "aaa"
            kit_a.mkdir(parents=True)
            (kit_a / "x.md").write_text("aaa prompt", encoding="utf-8")
            (kit_a / "agents.toml").write_text(
                '[agents.my-agent]\ndescription = "from aaa"\nprompt_file = "x.md"\n',
                encoding="utf-8",
            )
            kit_b = cypilot / "config" / "kits" / "bbb"
            kit_b.mkdir(parents=True)
            (kit_b / "x.md").write_text("bbb prompt", encoding="utf-8")
            (kit_b / "agents.toml").write_text(
                '[agents.my-agent]\ndescription = "from bbb"\nprompt_file = "x.md"\n',
                encoding="utf-8",
            )
            agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(len(agents), 1)
            self.assertEqual(agents[0]["description"], "from aaa")

    def test_invalid_registered_kit_dirs_value_is_ignored(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._make_kit_tree(root)
            with patch("cypilot.commands.agents._registered_kit_dirs", return_value=object()):
                agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(len(agents), 2)
            names = {a["name"] for a in agents}
            self.assertEqual(names, {"cypilot-codegen", "cypilot-pr-review"})


# ── Per-tool template tests ─────────────────────────────────────────

class TestToolTemplates(unittest.TestCase):
    """Tests for per-tool template rendering functions."""

    def test_claude_readwrite_with_isolation(self):
        agent = _make_semantic_agent(mode="readwrite", isolation=True, model="inherit")
        lines = _agent_template_claude(agent)
        text = "\n".join(lines)
        self.assertIn("tools: Bash, Read, Write, Edit, Glob, Grep", text)
        self.assertNotIn("disallowedTools", text)
        self.assertIn("isolation: worktree", text)
        self.assertIn("model: inherit", text)

    def test_claude_readonly_no_isolation(self):
        agent = _make_semantic_agent(mode="readonly", isolation=False, model="fast")
        lines = _agent_template_claude(agent)
        text = "\n".join(lines)
        self.assertIn("tools: Bash, Read, Glob, Grep", text)
        self.assertIn("disallowedTools: Write, Edit", text)
        self.assertNotIn("isolation:", text)
        self.assertIn("model: sonnet", text)  # fast -> sonnet for Claude

    def test_cursor_readwrite(self):
        agent = _make_semantic_agent(mode="readwrite", model="inherit")
        lines = _agent_template_cursor(agent)
        text = "\n".join(lines)
        self.assertIn("tools: grep, view, edit, bash", text)
        self.assertNotIn("readonly", text)

    def test_cursor_readonly(self):
        agent = _make_semantic_agent(mode="readonly", model="fast")
        lines = _agent_template_cursor(agent)
        text = "\n".join(lines)
        self.assertIn("tools: grep, view, bash", text)
        self.assertIn("readonly: true", text)
        self.assertIn("model: fast", text)

    def test_copilot_readwrite(self):
        agent = _make_semantic_agent(mode="readwrite")
        lines = _agent_template_copilot(agent)
        text = "\n".join(lines)
        self.assertIn('tools: ["*"]', text)

    def test_copilot_readonly(self):
        agent = _make_semantic_agent(mode="readonly")
        lines = _agent_template_copilot(agent)
        text = "\n".join(lines)
        self.assertIn('tools: ["read", "search"]', text)

    def test_all_templates_have_target_agent_path(self):
        agent = _make_semantic_agent()
        for fn in (_agent_template_claude, _agent_template_cursor, _agent_template_copilot):
            text = "\n".join(fn(agent))
            self.assertIn("{target_agent_path}", text, f"{fn.__name__} missing target_agent_path")

    def test_tool_config_has_four_tools(self):
        self.assertEqual(set(_TOOL_AGENT_CONFIG.keys()), {"claude", "cursor", "copilot", "openai"})

    def test_openai_config_has_toml_format(self):
        self.assertEqual(_TOOL_AGENT_CONFIG["openai"].get("format"), "toml")


# ── TOML rendering tests ───────────────────────────────────────────

class TestRenderTomlAgent(unittest.TestCase):
    """Tests for _render_toml_agent() per-file TOML rendering."""

    def test_has_top_level_name(self):
        agent = _make_semantic_agent("cypilot-codegen")
        result = _render_toml_agent(agent, "@/agents/cypilot-codegen.md")
        self.assertIn('name = "cypilot-codegen"', result)

    def test_has_top_level_description(self):
        agent = _make_semantic_agent("cypilot-codegen", description="Cypilot code generator.")
        result = _render_toml_agent(agent, "@/agents/cypilot-codegen.md")
        self.assertIn('description = "Cypilot code generator."', result)

    def test_has_developer_instructions_with_pointer(self):
        agent = _make_semantic_agent("cypilot-codegen")
        result = _render_toml_agent(agent, "@/agents/cypilot-codegen.md")
        self.assertIn('developer_instructions = """', result)
        self.assertIn("ALWAYS open and follow", result)
        self.assertIn("agents/cypilot-codegen.md", result)

    def test_no_nested_agents_sections(self):
        agent = _make_semantic_agent("cypilot-codegen")
        result = _render_toml_agent(agent, "@/agents/cypilot-codegen.md")
        self.assertNotIn("[agents.", result)

    def test_ends_with_newline(self):
        agent = _make_semantic_agent("test")
        result = _render_toml_agent(agent, "@/test.md")
        self.assertTrue(result.endswith("\n"))

    def test_escapes_backslash_in_description(self):
        agent = _make_semantic_agent("t", description="path\\to\\file")
        result = _render_toml_agent(agent, "@/t.md")
        self.assertIn("path\\\\to\\\\file", result)

    def test_escapes_quotes_in_description(self):
        agent = _make_semantic_agent("t", description='say "hello"')
        result = _render_toml_agent(agent, "@/t.md")
        self.assertIn('say \\"hello\\"', result)

    def test_collapses_multiline_description(self):
        agent = _make_semantic_agent("t", description="line one\nline two\n  line three")
        result = _render_toml_agent(agent, "@/t.md")
        self.assertIn('description = "line one line two line three"', result)


# ── Integration tests ───────────────────────────────────────────────

class TestSubagentIntegration(unittest.TestCase):
    """Integration tests for subagent generation via _process_single_agent()."""

    def _setup_cypilot_tree(self, root: Path) -> Path:
        """Create minimal cypilot structure with core skill agents."""
        (root / ".git").mkdir(exist_ok=True)
        cypilot = root / "cypilot_src"
        skill_dir = cypilot / "skills" / "cypilot"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: cypilot\ndescription: Cypilot core skill\n---\n\nSkill content.\n",
            encoding="utf-8",
        )
        # Core agents in skills/cypilot/
        _make_kit(skill_dir)
        (cypilot / "workflows").mkdir()
        (cypilot / "workflows" / "generate.md").write_text(
            "---\nname: cypilot-generate\ndescription: Generate things\n---\n\nContent.\n",
            encoding="utf-8",
        )
        (cypilot / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
        return cypilot

    def _run_agents(self, root: Path, cypilot: Path, agent: str, dry_run: bool = False) -> dict:
        cfg = _default_agents_config()
        return _process_single_agent(agent, root, cypilot, cfg, None, dry_run=dry_run)

    def test_claude_generates_two_subagent_files(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._setup_cypilot_tree(root)
            result = self._run_agents(root, cypilot, "claude")

            self.assertEqual(result["status"], "PASS")
            subagents = result["subagents"]
            self.assertFalse(subagents["skipped"])
            total = subagents["counts"]["created"] + subagents["counts"]["updated"]
            self.assertEqual(total, 2)

            codegen_path = root / ".claude" / "agents" / "cypilot-codegen.md"
            pr_review_path = root / ".claude" / "agents" / "cypilot-pr-review.md"
            self.assertTrue(codegen_path.exists())
            self.assertTrue(pr_review_path.exists())

            codegen_content = codegen_path.read_text(encoding="utf-8")
            self.assertIn("name: cypilot-codegen", codegen_content)
            self.assertIn("isolation: worktree", codegen_content)
            self.assertIn("ALWAYS open and follow", codegen_content)
            self.assertNotIn("{target_agent_path}", codegen_content)

            pr_content = pr_review_path.read_text(encoding="utf-8")
            self.assertIn("name: cypilot-pr-review", pr_content)
            self.assertIn("disallowedTools: Write, Edit", pr_content)
            self.assertIn("model: sonnet", pr_content)

    def test_cursor_generates_two_subagent_files(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._setup_cypilot_tree(root)
            result = self._run_agents(root, cypilot, "cursor")

            self.assertEqual(result["status"], "PASS")
            subagents = result["subagents"]
            self.assertFalse(subagents["skipped"])

            pr_review_path = root / ".cursor" / "agents" / "cypilot-pr-review.md"
            self.assertTrue(pr_review_path.exists())
            pr_content = pr_review_path.read_text(encoding="utf-8")
            self.assertIn("readonly: true", pr_content)

    def test_copilot_generates_agent_md_extension(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._setup_cypilot_tree(root)
            result = self._run_agents(root, cypilot, "copilot")

            self.assertEqual(result["status"], "PASS")
            codegen_path = root / ".github" / "agents" / "cypilot-codegen.agent.md"
            pr_path = root / ".github" / "agents" / "cypilot-pr-review.agent.md"
            self.assertTrue(codegen_path.exists())
            self.assertTrue(pr_path.exists())

    def test_openai_generates_per_agent_toml_files(self):
        """Issue #125: Codex CLI expects one TOML file per agent with top-level fields."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._setup_cypilot_tree(root)
            result = self._run_agents(root, cypilot, "openai")

            self.assertEqual(result["status"], "PASS")
            agents_dir = root / ".codex" / "agents"

            # Each agent gets its own .toml file
            codegen_toml = agents_dir / "cypilot-codegen.toml"
            pr_review_toml = agents_dir / "cypilot-pr-review.toml"
            self.assertTrue(codegen_toml.exists(), "cypilot-codegen.toml not created")
            self.assertTrue(pr_review_toml.exists(), "cypilot-pr-review.toml not created")

            # Combined file must NOT exist (it causes Codex CLI warnings)
            combined = agents_dir / "cypilot-agents.toml"
            self.assertFalse(combined.exists(), "combined cypilot-agents.toml must not be created")

            # Each file has top-level fields (not nested under [agents.*])
            for toml_path in (codegen_toml, pr_review_toml):
                content = toml_path.read_text(encoding="utf-8")
                self.assertIn('name = "', content)
                self.assertIn('description = "', content)
                self.assertIn('developer_instructions = """', content)
                self.assertIn("ALWAYS open and follow", content)
                self.assertNotIn("[agents.", content,
                    f"{toml_path.name} must use top-level fields, not [agents.*] sections")

    def test_windsurf_skips_subagent_generation(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._setup_cypilot_tree(root)
            result = self._run_agents(root, cypilot, "windsurf")

            self.assertEqual(result["status"], "PASS")
            subagents = result["subagents"]
            self.assertTrue(subagents["skipped"])
            self.assertEqual(subagents["counts"]["created"], 0)
            self.assertEqual(subagents["counts"]["updated"], 0)

    def test_dry_run_does_not_write_subagent_files(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._setup_cypilot_tree(root)
            result = self._run_agents(root, cypilot, "claude", dry_run=True)

            self.assertEqual(result["status"], "PASS")
            subagents = result["subagents"]
            self.assertEqual(subagents["counts"]["created"], 2)

            codegen_path = root / ".claude" / "agents" / "cypilot-codegen.md"
            self.assertFalse(codegen_path.exists())

    def test_idempotent_second_run_no_updates(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._setup_cypilot_tree(root)

            result1 = self._run_agents(root, cypilot, "claude")
            self.assertEqual(result1["subagents"]["counts"]["created"], 2)

            result2 = self._run_agents(root, cypilot, "claude")
            self.assertEqual(result2["subagents"]["counts"]["created"], 0)
            self.assertEqual(result2["subagents"]["counts"]["updated"], 0)
            self.assertEqual(len(result2["subagents"]["outputs"]), 2)
            for out in result2["subagents"]["outputs"]:
                self.assertEqual(out["action"], "unchanged")

    def test_existing_skills_workflows_unchanged_with_subagents(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._setup_cypilot_tree(root)
            result = self._run_agents(root, cypilot, "claude")

            self.assertIn("workflows", result)
            self.assertIn("skills", result)
            self.assertIn("subagents", result)

    def test_unknown_tool_skips_subagents(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = self._setup_cypilot_tree(root)
            result = self._run_agents(root, cypilot, "unknown-tool")

            subagents = result["subagents"]
            self.assertTrue(subagents["skipped"])

    def test_no_agents_skips_generation(self):
        """Tool with agent support but no agents.toml anywhere skips gracefully."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            (root / ".git").mkdir()
            (cypilot / "skills" / "cypilot").mkdir(parents=True)
            (cypilot / "skills" / "cypilot" / "SKILL.md").write_text(
                "---\nname: cypilot\ndescription: test\n---\n\nContent.\n",
                encoding="utf-8",
            )
            (cypilot / "config" / "kits").mkdir(parents=True)
            (cypilot / "workflows").mkdir()
            (cypilot / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")

            cfg = _default_agents_config()
            result = _process_single_agent("claude", root, cypilot, cfg, None, dry_run=False)
            subagents = result["subagents"]
            self.assertTrue(subagents["skipped"])
            self.assertIn("no agents discovered", subagents.get("skip_reason", ""))


if __name__ == "__main__":
    unittest.main()
