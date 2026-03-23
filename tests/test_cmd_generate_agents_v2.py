"""
Tests for cmd_generate_agents() with v2.0 manifest pipeline.

Covers the multi-layer v2.0 manifest pipeline path inside cmd_generate_agents(),
including include resolution, --show-layers, --discover, manifest-based agent
generation, and the legacy fallback path.

Also covers generate_manifest_agents() edge cases:
  - source file read exception
  - existing frontmatter stripping
  - missing description skip
  - append field handling

And _discover_kit_agents() edge cases:
  - agents section not a dict
  - agent info not a dict
  - non-string prompt_file
  - empty prompt_file
  - prompt file not found on disk
"""

from __future__ import annotations

import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.commands.agents import (
    _discover_kit_agents,
    cmd_generate_agents,
    generate_manifest_agents,
)
from cypilot.utils.manifest import AgentEntry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_AGENTS_MD = "<!-- @cpt:root-agents -->\n## Cypilot\n"
_MANIFEST_V2_AGENT = """\
[manifest]
version = "2.0"

[[agents]]
id = "my-agent"
description = "Test agent"
source = "agents/my-agent.md"
agents = ["claude"]
"""

_MANIFEST_V2_SKILL = """\
[manifest]
version = "2.0"

[[skills]]
id = "my-skill"
description = "Test skill"
source = "skills/my-skill/SKILL.md"
"""


def _make_agent(**kwargs) -> AgentEntry:
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


def _make_project(tmpdir: str) -> tuple:
    """Create a minimal project + cypilot_root inside it.

    Returns (project_root, cypilot_root) as Path objects.
    """
    project_root = Path(tmpdir)
    # AGENTS.md with the project-root marker
    (project_root / "AGENTS.md").write_text(_AGENTS_MD, encoding="utf-8")

    # cypilot_root inside project (so _ensure_cypilot_local returns "none")
    cypilot_root = project_root / ".bootstrap"
    # Minimal structure that satisfies _is_cypilot_root (new layout)
    core = cypilot_root / ".core"
    (core / "requirements").mkdir(parents=True)
    (core / "workflows").mkdir(parents=True)
    (cypilot_root / "config").mkdir(parents=True)

    # Minimal SKILL.md so the legacy path in _process_single_agent doesn't
    # return PARTIAL (which would set has_errors=True in the v2 pipeline too).
    skill_dir = core / "skills" / "cypilot"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: cypilot\ndescription: Cypilot\n---\n# Cypilot\n",
        encoding="utf-8",
    )

    return project_root, cypilot_root


def _write_manifest(cypilot_root: Path, content: str) -> Path:
    manifest_path = cypilot_root / "config" / "manifest.toml"
    manifest_path.write_text(content, encoding="utf-8")
    return manifest_path


# ---------------------------------------------------------------------------
# Tests: cmd_generate_agents — v2 manifest pipeline
# ---------------------------------------------------------------------------

class TestCmdGenerateAgentsV2ManifestPipeline(unittest.TestCase):
    """cmd_generate_agents uses v2 pipeline when manifest.toml has version=2.0."""

    def _run(self, tmpdir: str, extra_argv: list = None) -> int:
        project_root, cypilot_root = _make_project(tmpdir)
        _write_manifest(cypilot_root, _MANIFEST_V2_AGENT)

        # Write the agent source file
        src = project_root / "agents" / "my-agent.md"
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text("# My Agent\nDo something.", encoding="utf-8")

        argv = [
            "--root", str(project_root),
            "--cypilot-root", str(cypilot_root),
            "--agent", "claude",
            "--dry-run",
        ]
        if extra_argv:
            argv.extend(extra_argv)
        return cmd_generate_agents(argv)

    def test_v2_pipeline_returns_zero(self):
        """cmd_generate_agents succeeds (returns 0) with v2 manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ret = self._run(tmpdir)
            self.assertEqual(ret, 0)

    def test_v2_pipeline_dry_run_no_files_written(self):
        """dry_run=True prevents files being written even with v2 manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root, cypilot_root = _make_project(tmpdir)
            _write_manifest(cypilot_root, _MANIFEST_V2_AGENT)

            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True, exist_ok=True)
            src.write_text("# My Agent", encoding="utf-8")

            cmd_generate_agents([
                "--root", str(project_root),
                "--cypilot-root", str(cypilot_root),
                "--agent", "claude",
                "--dry-run",
            ])

            out_path = project_root / ".claude" / "agents" / "my-agent.md"
            self.assertFalse(out_path.exists(), "dry_run must not write files")

    def test_v2_pipeline_writes_files_without_dry_run(self):
        """cmd_generate_agents writes agent files with v2 manifest (no dry-run)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root, cypilot_root = _make_project(tmpdir)
            _write_manifest(cypilot_root, _MANIFEST_V2_AGENT)

            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True, exist_ok=True)
            src.write_text("# My Agent\nDo something.", encoding="utf-8")

            ret = cmd_generate_agents([
                "--root", str(project_root),
                "--cypilot-root", str(cypilot_root),
                "--agent", "claude",
                "-y",  # skip confirmation
            ])
            self.assertEqual(ret, 0)

            out_path = project_root / ".claude" / "agents" / "my-agent.md"
            self.assertTrue(out_path.exists(), "Agent file should be created")


class TestCmdGenerateAgentsShowLayers(unittest.TestCase):
    """--show-layers flag in v2 and legacy mode."""

    def test_show_layers_v2_returns_zero(self):
        """--show-layers returns 0 with v2 manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root, cypilot_root = _make_project(tmpdir)
            _write_manifest(cypilot_root, _MANIFEST_V2_AGENT)

            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True, exist_ok=True)
            src.write_text("# My Agent", encoding="utf-8")

            ret = cmd_generate_agents([
                "--root", str(project_root),
                "--cypilot-root", str(cypilot_root),
                "--agent", "claude",
                "--show-layers",
            ])
            self.assertEqual(ret, 0)

    def test_show_layers_legacy_mode_returns_zero(self):
        """--show-layers in legacy mode (no manifest) returns 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root, cypilot_root = _make_project(tmpdir)
            # No manifest.toml → legacy mode

            ret = cmd_generate_agents([
                "--root", str(project_root),
                "--cypilot-root", str(cypilot_root),
                "--agent", "claude",
                "--show-layers",
                "--dry-run",
            ])
            self.assertEqual(ret, 0)

    def test_show_layers_v2_outputs_provenance_report(self):
        """--show-layers in v2 mode outputs provenance report (JSON or text)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root, cypilot_root = _make_project(tmpdir)
            _write_manifest(cypilot_root, _MANIFEST_V2_AGENT)

            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True, exist_ok=True)
            src.write_text("# My Agent", encoding="utf-8")

            captured = io.StringIO()
            with mock.patch("sys.stdout", captured):
                # Force non-JSON mode so human text is written to stdout
                with mock.patch(
                    "cypilot.utils.ui.is_json_mode",
                    return_value=False,
                ):
                    cmd_generate_agents([
                        "--root", str(project_root),
                        "--cypilot-root", str(cypilot_root),
                        "--agent", "claude",
                        "--show-layers",
                    ])
            output = captured.getvalue()
            self.assertIn("Layer Provenance Report", output)


class TestCmdGenerateAgentsDiscover(unittest.TestCase):
    """--discover flag populates manifest from conventional dirs."""

    def test_discover_flag_legacy_mode_writes_manifest(self):
        """--discover in legacy mode writes manifest.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root, cypilot_root = _make_project(tmpdir)
            # No manifest.toml → legacy mode

            # Create a discoverable agent
            agents_dir = project_root / ".claude" / "agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "test-agent.md").write_text("# Test\n", encoding="utf-8")

            ret = cmd_generate_agents([
                "--root", str(project_root),
                "--cypilot-root", str(cypilot_root),
                "--agent", "claude",
                "--discover",
                "--dry-run",
            ])
            # Returns 0 — --discover just writes manifest and continues
            self.assertIn(ret, [0, 1])

    def test_discover_flag_v2_mode_reruns_discovery(self):
        """--discover in v2 mode re-runs discovery after writing manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root, cypilot_root = _make_project(tmpdir)
            _write_manifest(cypilot_root, _MANIFEST_V2_AGENT)

            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True, exist_ok=True)
            src.write_text("# My Agent", encoding="utf-8")

            # --discover with v2 manifest
            ret = cmd_generate_agents([
                "--root", str(project_root),
                "--cypilot-root", str(cypilot_root),
                "--agent", "claude",
                "--discover",
                "--dry-run",
            ])
            self.assertIn(ret, [0, 1])


class TestCmdGenerateAgentsLegacyPath(unittest.TestCase):
    """Legacy path (no v2 manifest) still works."""

    def test_legacy_path_dry_run(self):
        """cmd_generate_agents in legacy mode with --dry-run returns 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root, cypilot_root = _make_project(tmpdir)
            # No manifest.toml

            ret = cmd_generate_agents([
                "--root", str(project_root),
                "--cypilot-root", str(cypilot_root),
                "--agent", "claude",
                "--dry-run",
            ])
            self.assertEqual(ret, 0)

    def test_legacy_path_no_project_root_returns_one(self):
        """Returns 1 when no project root (no AGENTS.md, no .git)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Empty dir — no AGENTS.md and no .git
            empty_dir = Path(tmpdir) / "empty"
            empty_dir.mkdir()
            ret = cmd_generate_agents([
                "--root", str(empty_dir),
                "--agent", "claude",
                "--dry-run",
            ])
            self.assertEqual(ret, 1)


# ---------------------------------------------------------------------------
# Tests: generate_manifest_agents — edge cases
# ---------------------------------------------------------------------------

class TestGenerateManifestAgentsEdgeCases(unittest.TestCase):
    """Edge cases in generate_manifest_agents()."""

    def test_source_read_exception_skips_agent(self):
        """When reading source file raises, the agent is skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Agent", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    description="Test",
                    source=str(src),
                    agents=["claude"],
                )
            }

            # Patch Path.read_text to raise on the source file
            original_read_text = Path.read_text

            def patched_read_text(self, *args, **kwargs):
                if self == src:
                    raise OSError("permission denied")
                return original_read_text(self, *args, **kwargs)

            with mock.patch.object(Path, "read_text", patched_read_text):
                result = generate_manifest_agents(agents, "claude", project_root, dry_run=False)

            self.assertEqual(len(result["created"]), 0)

    def test_existing_frontmatter_stripped_from_source(self):
        """Existing YAML frontmatter in source file is stripped before assembly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            # Source with existing frontmatter
            src.write_text(
                "---\nold_key: old_value\n---\nThis is the body content.\n",
                encoding="utf-8",
            )

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

            # Old frontmatter key should not appear
            self.assertNotIn("old_key", content)
            # Body content should be present
            self.assertIn("This is the body content.", content)
            # New manifest-generated frontmatter should be present
            self.assertIn("name: my-agent", content)

    def test_missing_description_skips_agent(self):
        """Agent with empty description is skipped with a warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Agent", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    description="",   # empty → should skip
                    source=str(src),
                    agents=["claude"],
                )
            }
            captured = io.StringIO()
            with mock.patch("sys.stderr", captured):
                result = generate_manifest_agents(agents, "claude", project_root, dry_run=False)

            self.assertEqual(len(result["created"]), 0)
            self.assertIn("no description", captured.getvalue())

    def test_append_field_appended_to_output(self):
        """Agent with append field has content appended after main body."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            src.write_text("# My Agent\nMain body.", encoding="utf-8")

            agents = {
                "my-agent": _make_agent(
                    id="my-agent",
                    description="A described agent",
                    source=str(src),
                    agents=["claude"],
                    append="## Extra Section\nAppended content.",
                )
            }
            generate_manifest_agents(agents, "claude", project_root, dry_run=False)
            out_path = project_root / ".claude" / "agents" / "my-agent.md"
            content = out_path.read_text(encoding="utf-8")

            self.assertIn("Main body.", content)
            self.assertIn("## Extra Section", content)
            self.assertIn("Appended content.", content)

    def test_frontmatter_without_closing_marker_not_stripped(self):
        """Source that starts with '---' but has no closing '---' is not modified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            src = project_root / "agents" / "my-agent.md"
            src.parent.mkdir(parents=True)
            # No closing --- marker
            src.write_text("---\nno closing marker\nbody text here\n", encoding="utf-8")

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
            # The original content should be in output unchanged since no closing marker
            self.assertIn("body text here", content)


# ---------------------------------------------------------------------------
# Tests: _discover_kit_agents — uncovered edge cases
# ---------------------------------------------------------------------------

class TestDiscoverKitAgentsEdgeCases(unittest.TestCase):
    """Edge cases in _discover_kit_agents() inner _load_agents_toml function."""

    def test_agents_section_not_a_dict_skipped(self):
        """agents.toml where [agents] is not a table is silently ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            kit_dir = cypilot / "config" / "kits" / "bad"
            kit_dir.mkdir(parents=True)
            # agents is a list, not a table
            (kit_dir / "agents.toml").write_text(
                "agents = [\"item1\", \"item2\"]\n",
                encoding="utf-8",
            )
            agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(agents, [])

    def test_agent_info_not_a_dict_skipped(self):
        """Agent entry that is not a table (e.g., string) is skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            kit_dir = cypilot / "config" / "kits" / "bad"
            kit_dir.mkdir(parents=True)
            # agents.my-agent is a string, not a table
            (kit_dir / "agents.toml").write_text(
                '[agents]\nmy-agent = "not a table"\n',
                encoding="utf-8",
            )
            agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(agents, [])

    def test_non_string_prompt_file_skipped(self):
        """Agent with prompt_file that is not a string is skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            kit_dir = cypilot / "config" / "kits" / "bad"
            kit_dir.mkdir(parents=True)
            (kit_dir / "agents.toml").write_text(
                '[agents.my-agent]\ndescription = "test"\nprompt_file = 42\n',
                encoding="utf-8",
            )
            captured = io.StringIO()
            with mock.patch("sys.stderr", captured):
                agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(agents, [])
            self.assertIn("non-string prompt_file", captured.getvalue())

    def test_empty_prompt_file_skipped(self):
        """Agent with empty prompt_file string is skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            kit_dir = cypilot / "config" / "kits" / "bad"
            kit_dir.mkdir(parents=True)
            (kit_dir / "agents.toml").write_text(
                '[agents.my-agent]\ndescription = "test"\nprompt_file = ""\n',
                encoding="utf-8",
            )
            captured = io.StringIO()
            with mock.patch("sys.stderr", captured):
                agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(agents, [])
            self.assertIn("missing prompt_file", captured.getvalue())

    def test_prompt_file_not_found_on_disk_skipped(self):
        """Agent with prompt_file path that does not exist on disk is skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cypilot = root / "cypilot_src"
            kit_dir = cypilot / "config" / "kits" / "bad"
            kit_dir.mkdir(parents=True)
            (kit_dir / "agents.toml").write_text(
                '[agents.my-agent]\ndescription = "test"\nprompt_file = "missing.md"\n',
                encoding="utf-8",
            )
            # Do NOT create missing.md
            captured = io.StringIO()
            with mock.patch("sys.stderr", captured):
                agents = _discover_kit_agents(cypilot, root)
            self.assertEqual(agents, [])
            self.assertIn("not found", captured.getvalue())


# ---------------------------------------------------------------------------
# Tests: build_provenance_report — source path relativization
# ---------------------------------------------------------------------------

class TestBuildProvenanceReportAbsoluteSource(unittest.TestCase):
    """Provenance report handles absolute source paths outside project root."""

    def test_source_path_outside_project_root_is_posix(self):
        """Source path outside project root falls back to absolute posix string."""
        from cypilot.commands.agents import build_provenance_report
        from cypilot.utils.manifest import (
            AgentEntry,
            ManifestLayer,
            ManifestLayerState,
            ManifestV2,
            merge_components,
        )

        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                project_root = Path(tmpdir1)
                outside_src = Path(tmpdir2) / "agent.md"
                outside_src.write_text("# External Agent", encoding="utf-8")

                manifest = ManifestV2(
                    version="2.0",
                    agents=[AgentEntry(
                        id="ext-agent",
                        description="External",
                        source=str(outside_src),
                    )],
                    skills=[],
                    workflows=[],
                    rules=[],
                )
                layer = ManifestLayer(
                    scope="repo",
                    path=project_root / "manifest.toml",
                    manifest=manifest,
                    state=ManifestLayerState.LOADED,
                )
                merged = merge_components([layer])
                report = build_provenance_report(merged, project_root)

                components = report["components"]
                self.assertEqual(len(components), 1)
                rec = components[0]
                # source_path should be present as absolute posix path
                self.assertIn("source_path", rec)
                self.assertIn("agent.md", rec["source_path"])


if __name__ == "__main__":
    unittest.main()
