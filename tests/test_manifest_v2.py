"""Tests for Manifest V2 schema parsing.

Covers: ManifestV2, AgentEntry, SkillEntry, WorkflowEntry, RuleEntry,
ManifestLayer, ManifestLayerState, and parse_manifest_v2().
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from cypilot.utils.manifest import (
    AgentEntry,
    ComponentEntry,
    ManifestLayer,
    ManifestLayerState,
    ManifestV2,
    RuleEntry,
    SkillEntry,
    WorkflowEntry,
    load_manifest,
    parse_manifest_v2,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_V2_FULL = """\
[manifest]
version = "2.0"
includes = ["../parent/manifest.toml"]

[[agents]]
id = "reviewer"
description = "Code reviewer agent"
prompt_file = "prompts/reviewer.md"
mode = "readonly"
isolation = true
model = "opus"
tools = ["Read", "Grep"]
color = "#FF0000"
memory_dir = ".memory/reviewer"
agents = ["claude"]

[[skills]]
id = "deploy"
description = "Deployment skill"
prompt_file = "skills/deploy.md"

[[workflows]]
id = "release"
description = "Release workflow"
prompt_file = "workflows/release.md"

[[rules]]
id = "no-console-log"
description = "Ban console.log in production"
source = "rules/no-console-log.md"

[[hooks]]
id = "pre-commit"
command = "lint"

[[permissions]]
id = "fs-read"
scope = "project"
"""

_V1_COMPAT = """\
[manifest]
version = "1.0"
root = "{cypilot_path}/config/kits/test"

[[resources]]
id = "agents_md"
source = "agents/AGENTS.md"
default_path = "config/AGENTS.md"
type = "file"
description = "Agent definitions"
user_modifiable = true
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_parse_v2_full_manifest():
    """parse_manifest_v2 parses v2.0 with all component sections."""
    with TemporaryDirectory() as tmpdir:
        mpath = Path(tmpdir) / "manifest.toml"
        mpath.write_text(_V2_FULL)

        result = parse_manifest_v2(mpath)

        assert isinstance(result, ManifestV2)
        assert result.version == "2.0"
        assert result.includes == ["../parent/manifest.toml"]

        # Agents
        assert len(result.agents) == 1
        agent = result.agents[0]
        assert isinstance(agent, AgentEntry)
        assert agent.id == "reviewer"
        assert agent.mode == "readonly"
        assert agent.isolation is True
        assert agent.model == "opus"
        assert agent.tools == ["Read", "Grep"]
        assert agent.disallowed_tools == []
        assert agent.color == "#FF0000"
        assert agent.memory_dir == ".memory/reviewer"
        assert agent.agents == ["claude"]

        # Skills
        assert len(result.skills) == 1
        assert isinstance(result.skills[0], SkillEntry)
        assert result.skills[0].id == "deploy"

        # Workflows
        assert len(result.workflows) == 1
        assert isinstance(result.workflows[0], WorkflowEntry)
        assert result.workflows[0].id == "release"

        # Rules
        assert len(result.rules) == 1
        assert isinstance(result.rules[0], RuleEntry)
        assert result.rules[0].id == "no-console-log"


def test_parse_v1_backward_compatibility():
    """parse_manifest_v2 wraps v1.0 manifests as ManifestV2 with resources only."""
    with TemporaryDirectory() as tmpdir:
        mpath = Path(tmpdir) / "manifest.toml"
        mpath.write_text(_V1_COMPAT)

        result = parse_manifest_v2(mpath)

        assert isinstance(result, ManifestV2)
        assert result.version == "1.0"
        assert result.agents == []
        assert result.skills == []
        assert result.workflows == []
        assert result.rules == []
        assert len(result.resources) == 1
        assert result.resources[0].id == "agents_md"
        assert result.resources[0].type == "file"


def test_v1_load_manifest_still_works():
    """Existing load_manifest() function continues to work for v1 manifests."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        mpath = root / "manifest.toml"
        mpath.write_text(_V1_COMPAT)

        result = load_manifest(root)

        assert result is not None
        assert result.version == "1.0"
        assert len(result.resources) == 1
        assert result.resources[0].id == "agents_md"


def test_extended_agent_schema_fields():
    """AgentEntry supports tools, color, memory_dir, model, disallowed_tools."""
    toml_content = """\
[manifest]
version = "2.0"

[[agents]]
id = "helper"
description = "Helper agent"
model = "fast"
disallowed_tools = ["Bash", "Write"]
color = "blue"
memory_dir = ".mem/helper"
"""
    with TemporaryDirectory() as tmpdir:
        mpath = Path(tmpdir) / "manifest.toml"
        mpath.write_text(toml_content)

        result = parse_manifest_v2(mpath)

        agent = result.agents[0]
        assert agent.model == "fast"
        assert agent.disallowed_tools == ["Bash", "Write"]
        assert agent.tools == []
        assert agent.color == "blue"
        assert agent.memory_dir == ".mem/helper"


def test_tools_disallowed_tools_mutual_exclusivity():
    """parse_manifest_v2 raises ValueError when both tools and disallowed_tools set."""
    toml_content = """\
[manifest]
version = "2.0"

[[agents]]
id = "bad-agent"
tools = ["Read"]
disallowed_tools = ["Write"]
"""
    with TemporaryDirectory() as tmpdir:
        mpath = Path(tmpdir) / "manifest.toml"
        mpath.write_text(toml_content)

        try:
            parse_manifest_v2(mpath)
            assert False, "Should have raised ValueError"
        except ValueError as exc:
            assert "mutually exclusive" in str(exc)
            assert "bad-agent" in str(exc)


def test_hooks_and_permissions_accepted_and_ignored():
    """parse_manifest_v2 accepts [[hooks]] and [[permissions]] without error."""
    with TemporaryDirectory() as tmpdir:
        mpath = Path(tmpdir) / "manifest.toml"
        mpath.write_text(_V2_FULL)

        result = parse_manifest_v2(mpath)

        # No hooks or permissions fields on ManifestV2 — they are silently ignored
        assert not hasattr(result, "hooks")
        assert not hasattr(result, "permissions")
        # Parsing succeeded without error
        assert result.version == "2.0"


def test_parse_error_missing_version():
    """parse_manifest_v2 raises ValueError with path info on missing version."""
    toml_content = """\
[manifest]
"""
    with TemporaryDirectory() as tmpdir:
        mpath = Path(tmpdir) / "manifest.toml"
        mpath.write_text(toml_content)

        try:
            parse_manifest_v2(mpath)
            assert False, "Should have raised ValueError"
        except ValueError as exc:
            assert "version" in str(exc)
            assert str(mpath) in str(exc)


def test_parse_error_invalid_toml():
    """parse_manifest_v2 raises ValueError on invalid TOML content."""
    with TemporaryDirectory() as tmpdir:
        mpath = Path(tmpdir) / "manifest.toml"
        mpath.write_text("this is not valid toml [[[")

        try:
            parse_manifest_v2(mpath)
            assert False, "Should have raised ValueError"
        except ValueError as exc:
            assert "TOML parse error" in str(exc)


def test_parse_error_file_not_found():
    """parse_manifest_v2 raises ValueError when file does not exist."""
    try:
        parse_manifest_v2(Path("/nonexistent/manifest.toml"))
        assert False, "Should have raised ValueError"
    except ValueError as exc:
        assert "not found" in str(exc)


def test_parse_error_unsupported_version():
    """parse_manifest_v2 raises ValueError for unsupported version."""
    toml_content = """\
[manifest]
version = "3.0"
"""
    with TemporaryDirectory() as tmpdir:
        mpath = Path(tmpdir) / "manifest.toml"
        mpath.write_text(toml_content)

        try:
            parse_manifest_v2(mpath)
            assert False, "Should have raised ValueError"
        except ValueError as exc:
            assert "unsupported" in str(exc)
            assert "3.0" in str(exc)


def test_parse_error_invalid_agent_id():
    """parse_manifest_v2 raises ValueError for invalid agent id."""
    toml_content = """\
[manifest]
version = "2.0"

[[agents]]
id = "Bad-Agent!"
"""
    with TemporaryDirectory() as tmpdir:
        mpath = Path(tmpdir) / "manifest.toml"
        mpath.write_text(toml_content)

        try:
            parse_manifest_v2(mpath)
            assert False, "Should have raised ValueError"
        except ValueError as exc:
            assert "Bad-Agent!" in str(exc)


def test_manifest_layer_state_enum():
    """ManifestLayerState enum has all expected values."""
    assert ManifestLayerState.UNDISCOVERED.value == "UNDISCOVERED"
    assert ManifestLayerState.LOADED.value == "LOADED"
    assert ManifestLayerState.PARSE_ERROR.value == "PARSE_ERROR"
    assert ManifestLayerState.INCLUDE_ERROR.value == "INCLUDE_ERROR"


def test_manifest_layer_dataclass():
    """ManifestLayer holds scope, path, manifest, and state."""
    layer = ManifestLayer(
        scope="project",
        path=Path("/some/path"),
        manifest=None,
        state=ManifestLayerState.UNDISCOVERED,
    )
    assert layer.scope == "project"
    assert layer.path == Path("/some/path")
    assert layer.manifest is None
    assert layer.state == ManifestLayerState.UNDISCOVERED


def test_v2_empty_component_sections():
    """parse_manifest_v2 handles v2.0 with no component sections."""
    toml_content = """\
[manifest]
version = "2.0"
"""
    with TemporaryDirectory() as tmpdir:
        mpath = Path(tmpdir) / "manifest.toml"
        mpath.write_text(toml_content)

        result = parse_manifest_v2(mpath)

        assert result.version == "2.0"
        assert result.agents == []
        assert result.skills == []
        assert result.workflows == []
        assert result.rules == []
        assert result.includes == []


def test_component_entry_inheritance():
    """AgentEntry, SkillEntry, WorkflowEntry, RuleEntry all inherit ComponentEntry."""
    assert issubclass(AgentEntry, ComponentEntry)
    assert issubclass(SkillEntry, ComponentEntry)
    assert issubclass(WorkflowEntry, ComponentEntry)
    assert issubclass(RuleEntry, ComponentEntry)
