"""Tests for resolve_includes() — Phase 3: Includes Resolution.

Covers:
- Empty includes (no-op)
- Single-level include (basic merge)
- Recursive includes (two levels)
- Circular include detection
- Max depth exceeded
- ID collision between includer and includee (includer wins silently)
- ID collision between two includees (error)
- prompt_file / source path rewriting
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from cypilot.utils.manifest import (
    ManifestV2,
    parse_manifest_v2,
    resolve_includes,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_manifest(directory: Path, content: str) -> Path:
    """Write *content* to ``manifest.toml`` in *directory* and return the path."""
    path = directory / "manifest.toml"
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# Test: empty includes array (no-op)
# ---------------------------------------------------------------------------

def test_empty_includes_returns_manifest_unchanged():
    """resolve_includes returns the original manifest when includes is empty."""
    with TemporaryDirectory() as tmpdir:
        mdir = Path(tmpdir)
        mpath = _write_manifest(mdir, """\
[manifest]
version = "2.0"

[[agents]]
id = "base-agent"
description = "Base agent"
""")
        manifest = parse_manifest_v2(mpath)
        result = resolve_includes(manifest, mdir)

        assert result is manifest  # same object — no copy needed
        assert len(result.agents) == 1
        assert result.agents[0].id == "base-agent"


# ---------------------------------------------------------------------------
# Test: single-level include
# ---------------------------------------------------------------------------

def test_single_level_include_merges_components():
    """resolve_includes loads one sub-manifest and merges its components."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        sub = root / "sub"
        sub.mkdir()

        # Sub-manifest
        _write_manifest(sub, """\
[manifest]
version = "2.0"

[[skills]]
id = "sub-skill"
description = "A skill from sub"
""")

        # Root manifest includes sub
        mpath = _write_manifest(root, """\
[manifest]
version = "2.0"
includes = ["sub/manifest.toml"]

[[agents]]
id = "root-agent"
description = "Root agent"
""")

        manifest = parse_manifest_v2(mpath)
        result = resolve_includes(manifest, root)

        assert len(result.agents) == 1
        assert result.agents[0].id == "root-agent"
        assert len(result.skills) == 1
        assert result.skills[0].id == "sub-skill"


# ---------------------------------------------------------------------------
# Test: recursive includes (two levels)
# ---------------------------------------------------------------------------

def test_recursive_includes_two_levels():
    """resolve_includes handles two levels of nesting (A → B → C)."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        level1 = root / "level1"
        level2 = root / "level1" / "level2"
        level1.mkdir()
        level2.mkdir()

        # Level-2 manifest (no further includes)
        _write_manifest(level2, """\
[manifest]
version = "2.0"

[[rules]]
id = "deep-rule"
description = "A rule from depth 2"
""")

        # Level-1 manifest includes level-2
        _write_manifest(level1, """\
[manifest]
version = "2.0"
includes = ["level2/manifest.toml"]

[[workflows]]
id = "mid-workflow"
description = "Workflow at depth 1"
""")

        # Root manifest includes level-1
        mpath = _write_manifest(root, """\
[manifest]
version = "2.0"
includes = ["level1/manifest.toml"]

[[agents]]
id = "root-agent"
description = "Root agent"
""")

        manifest = parse_manifest_v2(mpath)
        result = resolve_includes(manifest, root)

        agent_ids = {a.id for a in result.agents}
        workflow_ids = {w.id for w in result.workflows}
        rule_ids = {r.id for r in result.rules}

        assert "root-agent" in agent_ids
        assert "mid-workflow" in workflow_ids
        assert "deep-rule" in rule_ids


# ---------------------------------------------------------------------------
# Test: circular include detection
# ---------------------------------------------------------------------------

def test_circular_include_raises_value_error():
    """resolve_includes raises ValueError when A includes B and B includes A."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        other = root / "other"
        other.mkdir()

        # 'other' manifest includes back to root
        _write_manifest(other, """\
[manifest]
version = "2.0"
includes = ["../manifest.toml"]

[[skills]]
id = "other-skill"
""")

        # Root includes 'other'
        mpath = _write_manifest(root, """\
[manifest]
version = "2.0"
includes = ["other/manifest.toml"]

[[agents]]
id = "root-agent"
""")

        manifest = parse_manifest_v2(mpath)
        with pytest.raises(ValueError, match="[Cc]ircular"):
            resolve_includes(manifest, root)


# ---------------------------------------------------------------------------
# Test: max depth exceeded
# ---------------------------------------------------------------------------

def test_max_depth_exceeded_raises_value_error():
    """resolve_includes raises ValueError when include chain depth exceeds 3."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Build 4 levels deep: root -> d1 -> d2 -> d3 -> d4
        dirs = [root]
        for i in range(1, 5):
            d = root / f"d{i}"
            d.mkdir()
            dirs.append(d)

        # d4 — leaf, no includes
        _write_manifest(dirs[4], """\
[manifest]
version = "2.0"

[[rules]]
id = "deep-rule"
""")

        # d3 includes d4
        _write_manifest(dirs[3], """\
[manifest]
version = "2.0"
includes = ["../d4/manifest.toml"]

[[rules]]
id = "d3-rule"
""")

        # d2 includes d3
        _write_manifest(dirs[2], """\
[manifest]
version = "2.0"
includes = ["../d3/manifest.toml"]

[[rules]]
id = "d2-rule"
""")

        # d1 includes d2
        _write_manifest(dirs[1], """\
[manifest]
version = "2.0"
includes = ["../d2/manifest.toml"]

[[rules]]
id = "d1-rule"
""")

        # root includes d1 (depth 0 -> 1 -> 2 -> 3 -> 4 exceeds limit of 3)
        mpath = _write_manifest(root, """\
[manifest]
version = "2.0"
includes = ["d1/manifest.toml"]

[[agents]]
id = "root-agent"
""")

        manifest = parse_manifest_v2(mpath)
        with pytest.raises(ValueError, match="[Mm]ax.*depth|depth.*exceeded"):
            resolve_includes(manifest, root)


# ---------------------------------------------------------------------------
# Test: ID collision between includer and includee — includer wins
# ---------------------------------------------------------------------------

def test_id_collision_includer_wins():
    """resolve_includes lets the includer's definition win when it shares an ID
    with an included manifest — no error is raised and only the includer's
    version of the component appears in the result."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        sub = root / "sub"
        sub.mkdir()

        # Sub-manifest with an agent whose ID collides with root's agent
        _write_manifest(sub, """\
[manifest]
version = "2.0"

[[agents]]
id = "shared-id"
description = "Agent in sub"
""")

        mpath = _write_manifest(root, """\
[manifest]
version = "2.0"
includes = ["sub/manifest.toml"]

[[agents]]
id = "shared-id"
description = "Agent in root"
""")

        manifest = parse_manifest_v2(mpath)
        # Should not raise — includer wins silently
        result = resolve_includes(manifest, root)

        matching = [a for a in result.agents if a.id == "shared-id"]
        assert len(matching) == 1, "Expected exactly one 'shared-id' agent"
        assert matching[0].description == "Agent in root", (
            "Includer's definition should take priority"
        )


# ---------------------------------------------------------------------------
# Test: ID collision between two includees — still an error
# ---------------------------------------------------------------------------

def test_id_collision_between_includees_raises_value_error():
    """resolve_includes raises ValueError when two different included manifests
    both declare the same component ID."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        sub_a = root / "sub_a"
        sub_b = root / "sub_b"
        sub_a.mkdir()
        sub_b.mkdir()

        # Both sub-manifests declare the same ID
        _write_manifest(sub_a, """\
[manifest]
version = "2.0"

[[skills]]
id = "shared-skill"
description = "Skill in sub_a"
""")

        _write_manifest(sub_b, """\
[manifest]
version = "2.0"

[[skills]]
id = "shared-skill"
description = "Skill in sub_b"
""")

        mpath = _write_manifest(root, """\
[manifest]
version = "2.0"
includes = ["sub_a/manifest.toml", "sub_b/manifest.toml"]
""")

        manifest = parse_manifest_v2(mpath)
        with pytest.raises(ValueError, match="[Cc]ollision|shared-skill"):
            resolve_includes(manifest, root)


# ---------------------------------------------------------------------------
# Test: prompt_file / source path rewriting
# ---------------------------------------------------------------------------

def test_prompt_file_and_source_paths_rewritten_to_included_dir():
    """resolve_includes rewrites prompt_file/source relative to included manifest dir."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        sub = root / "sub"
        sub.mkdir()

        # Sub-manifest with relative prompt_file and source
        _write_manifest(sub, """\
[manifest]
version = "2.0"

[[agents]]
id = "sub-agent"
prompt_file = "prompts/sub.md"
source = "src/sub.py"
""")

        mpath = _write_manifest(root, """\
[manifest]
version = "2.0"
includes = ["sub/manifest.toml"]
""")

        manifest = parse_manifest_v2(mpath)
        result = resolve_includes(manifest, root)

        assert len(result.agents) == 1
        agent = result.agents[0]

        # Paths must be absolute and resolve relative to sub/
        expected_prompt = str((sub / "prompts/sub.md").resolve())
        expected_source = str((sub / "src/sub.py").resolve())

        assert agent.prompt_file == expected_prompt, (
            f"Expected prompt_file={expected_prompt!r}, got {agent.prompt_file!r}"
        )
        assert agent.source == expected_source, (
            f"Expected source={expected_source!r}, got {agent.source!r}"
        )


# ---------------------------------------------------------------------------
# Test: already-absolute paths not double-resolved
# ---------------------------------------------------------------------------

def test_absolute_paths_not_double_resolved():
    """resolve_includes leaves already-absolute prompt_file/source paths unchanged."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        sub = root / "sub"
        sub.mkdir()

        abs_path = "/absolute/path/to/prompt.md"

        _write_manifest(sub, f"""\
[manifest]
version = "2.0"

[[skills]]
id = "abs-skill"
prompt_file = "{abs_path}"
""")

        mpath = _write_manifest(root, """\
[manifest]
version = "2.0"
includes = ["sub/manifest.toml"]
""")

        manifest = parse_manifest_v2(mpath)
        result = resolve_includes(manifest, root)

        assert len(result.skills) == 1
        assert result.skills[0].prompt_file == abs_path


# ---------------------------------------------------------------------------
# Test: path traversal blocked
# ---------------------------------------------------------------------------

def test_path_traversal_blocked():
    """resolve_includes raises ValueError when an include escapes the trusted root."""
    with TemporaryDirectory() as outer:
        outer_path = Path(outer)
        project = outer_path / "project"
        project.mkdir()
        sub = project / "sub"
        sub.mkdir()

        # Write a manifest in the outer dir (outside the project)
        _write_manifest(outer_path, """\
[manifest]
version = "2.0"

[[skills]]
id = "outside-skill"
""")

        # sub/manifest.toml tries to include ../manifest.toml (escapes project/)
        _write_manifest(sub, """\
[manifest]
version = "2.0"
includes = ["../../manifest.toml"]

[[agents]]
id = "sub-agent"
""")

        mpath = _write_manifest(project, """\
[manifest]
version = "2.0"
includes = ["sub/manifest.toml"]
""")

        manifest = parse_manifest_v2(mpath)
        with pytest.raises(ValueError, match="[Pp]ath traversal|escapes"):
            resolve_includes(manifest, project)
