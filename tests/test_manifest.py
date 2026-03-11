"""Tests for cypilot.utils.manifest — kit manifest parser and validator."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from cypilot.utils.manifest import Manifest, ManifestResource, load_manifest, validate_manifest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_manifest(kit_dir: Path, content: str) -> Path:
    """Write manifest.toml into *kit_dir* and return the path."""
    manifest_path = kit_dir / "manifest.toml"
    manifest_path.write_text(textwrap.dedent(content), encoding="utf-8")
    return manifest_path


def _make_kit_with_manifest(tmp_path: Path) -> Path:
    """Create a minimal kit directory with a valid manifest and source files."""
    kit = tmp_path / "kit-source"
    kit.mkdir()

    # Source resources
    (kit / "artifacts" / "ADR").mkdir(parents=True)
    (kit / "artifacts" / "ADR" / "template.md").write_text("# ADR\n", encoding="utf-8")
    (kit / "constraints.toml").write_text('[artifacts]\n', encoding="utf-8")

    _write_manifest(kit, """\
        [manifest]
        version = "1.0"
        root = "{cypilot_path}/config/kits/{slug}"
        user_modifiable = true

        [[resources]]
        id = "adr_artifacts"
        description = "ADR artifact definitions"
        source = "artifacts/ADR"
        default_path = "artifacts/ADR"
        type = "directory"
        user_modifiable = true

        [[resources]]
        id = "constraints"
        description = "Kit structural constraints"
        source = "constraints.toml"
        default_path = "constraints.toml"
        type = "file"
        user_modifiable = false
    """)
    return kit


# ---------------------------------------------------------------------------
# load_manifest
# ---------------------------------------------------------------------------

class TestLoadManifest:
    """Tests for load_manifest()."""

    def test_valid_manifest_parses(self, tmp_path: Path) -> None:
        kit = _make_kit_with_manifest(tmp_path)
        m = load_manifest(kit)

        assert m is not None
        assert isinstance(m, Manifest)
        assert m.version == "1.0"
        assert m.root == "{cypilot_path}/config/kits/{slug}"
        assert m.user_modifiable is True
        assert len(m.resources) == 2

        r0 = m.resources[0]
        assert r0.id == "adr_artifacts"
        assert r0.source == "artifacts/ADR"
        assert r0.default_path == "artifacts/ADR"
        assert r0.type == "directory"
        assert r0.user_modifiable is True

        r1 = m.resources[1]
        assert r1.id == "constraints"
        assert r1.type == "file"
        assert r1.user_modifiable is False

    def test_missing_manifest_returns_none(self, tmp_path: Path) -> None:
        kit = tmp_path / "empty-kit"
        kit.mkdir()
        assert load_manifest(kit) is None

    def test_manifest_missing_version_raises(self, tmp_path: Path) -> None:
        kit = tmp_path / "bad-kit"
        kit.mkdir()
        _write_manifest(kit, """\
            [manifest]

            [[resources]]
            id = "foo"
            source = "foo.md"
            default_path = "foo.md"
            type = "file"
        """)
        with pytest.raises(ValueError, match="version"):
            load_manifest(kit)

    def test_manifest_empty_resources_raises(self, tmp_path: Path) -> None:
        kit = tmp_path / "no-res"
        kit.mkdir()
        _write_manifest(kit, """\
            [manifest]
            version = "1.0"
        """)
        with pytest.raises(ValueError, match="resources"):
            load_manifest(kit)

    def test_manifest_invalid_type_raises(self, tmp_path: Path) -> None:
        kit = tmp_path / "bad-type"
        kit.mkdir()
        _write_manifest(kit, """\
            [manifest]
            version = "1.0"

            [[resources]]
            id = "foo"
            source = "foo.md"
            default_path = "foo.md"
            type = "symlink"
        """)
        with pytest.raises(ValueError, match="type"):
            load_manifest(kit)

    def test_manifest_invalid_id_raises(self, tmp_path: Path) -> None:
        kit = tmp_path / "bad-id"
        kit.mkdir()
        _write_manifest(kit, """\
            [manifest]
            version = "1.0"

            [[resources]]
            id = "123invalid"
            source = "foo.md"
            default_path = "foo.md"
            type = "file"
        """)
        with pytest.raises(ValueError, match="id"):
            load_manifest(kit)

    def test_manifest_malformed_toml_raises(self, tmp_path: Path) -> None:
        kit = tmp_path / "bad-toml"
        kit.mkdir()
        (kit / "manifest.toml").write_text("[manifest\nbroken", encoding="utf-8")
        with pytest.raises(ValueError, match="manifest.toml"):
            load_manifest(kit)

    def test_defaults_applied(self, tmp_path: Path) -> None:
        """Manifest with only required fields gets correct defaults."""
        kit = tmp_path / "min-kit"
        kit.mkdir()
        (kit / "readme.md").write_text("hi\n", encoding="utf-8")
        _write_manifest(kit, """\
            [manifest]
            version = "1.0"

            [[resources]]
            id = "readme"
            source = "readme.md"
            default_path = "readme.md"
            type = "file"
        """)
        m = load_manifest(kit)
        assert m is not None
        assert m.root == "{cypilot_path}/config/kits/{slug}"
        assert m.user_modifiable is True
        assert m.resources[0].user_modifiable is True
        assert m.resources[0].description == ""


# ---------------------------------------------------------------------------
# validate_manifest
# ---------------------------------------------------------------------------

class TestValidateManifest:
    """Tests for validate_manifest()."""

    def test_valid_manifest_no_errors(self, tmp_path: Path) -> None:
        kit = _make_kit_with_manifest(tmp_path)
        m = load_manifest(kit)
        assert m is not None
        errors = validate_manifest(m, kit)
        assert errors == []

    def test_duplicate_ids(self, tmp_path: Path) -> None:
        kit = tmp_path / "dup"
        kit.mkdir()
        (kit / "a.md").write_text("a\n", encoding="utf-8")
        (kit / "b.md").write_text("b\n", encoding="utf-8")

        m = Manifest(
            version="1.0",
            root="{cypilot_path}/config/kits/{slug}",
            user_modifiable=True,
            resources=[
                ManifestResource(id="foo", source="a.md", default_path="a.md", type="file"),
                ManifestResource(id="foo", source="b.md", default_path="b.md", type="file"),
            ],
        )
        errors = validate_manifest(m, kit)
        assert len(errors) == 1
        assert "Duplicate" in errors[0]
        assert "foo" in errors[0]

    def test_missing_source_path(self, tmp_path: Path) -> None:
        kit = tmp_path / "nosrc"
        kit.mkdir()

        m = Manifest(
            version="1.0",
            root="{cypilot_path}/config/kits/{slug}",
            user_modifiable=True,
            resources=[
                ManifestResource(
                    id="missing",
                    source="does_not_exist.md",
                    default_path="out.md",
                    type="file",
                ),
            ],
        )
        errors = validate_manifest(m, kit)
        assert len(errors) == 1
        assert "does not exist" in errors[0]

    def test_type_mismatch_file_is_directory(self, tmp_path: Path) -> None:
        kit = tmp_path / "typemis"
        kit.mkdir()
        (kit / "somedir").mkdir()

        m = Manifest(
            version="1.0",
            root="{cypilot_path}/config/kits/{slug}",
            user_modifiable=True,
            resources=[
                ManifestResource(
                    id="bad",
                    source="somedir",
                    default_path="somedir",
                    type="file",
                ),
            ],
        )
        errors = validate_manifest(m, kit)
        assert len(errors) == 1
        assert "type is 'file'" in errors[0]
        assert "is a directory" in errors[0]

    def test_type_mismatch_directory_is_file(self, tmp_path: Path) -> None:
        kit = tmp_path / "typemis2"
        kit.mkdir()
        (kit / "afile.md").write_text("x\n", encoding="utf-8")

        m = Manifest(
            version="1.0",
            root="{cypilot_path}/config/kits/{slug}",
            user_modifiable=True,
            resources=[
                ManifestResource(
                    id="bad",
                    source="afile.md",
                    default_path="afile.md",
                    type="directory",
                ),
            ],
        )
        errors = validate_manifest(m, kit)
        assert len(errors) == 1
        assert "type is 'directory'" in errors[0]
        assert "is a file" in errors[0]

    def test_default_path_absolute_rejected(self, tmp_path: Path) -> None:
        kit = tmp_path / "abspath"
        kit.mkdir()
        (kit / "f.md").write_text("f\n", encoding="utf-8")

        m = Manifest(
            version="1.0",
            root="{cypilot_path}/config/kits/{slug}",
            user_modifiable=True,
            resources=[
                ManifestResource(
                    id="abs",
                    source="f.md",
                    default_path="/etc/passwd",
                    type="file",
                ),
            ],
        )
        errors = validate_manifest(m, kit)
        assert any("relative path" in e for e in errors)

    def test_default_path_traversal_rejected(self, tmp_path: Path) -> None:
        kit = tmp_path / "traverse"
        kit.mkdir()
        (kit / "f.md").write_text("f\n", encoding="utf-8")

        m = Manifest(
            version="1.0",
            root="{cypilot_path}/config/kits/{slug}",
            user_modifiable=True,
            resources=[
                ManifestResource(
                    id="escape",
                    source="f.md",
                    default_path="../../etc/passwd",
                    type="file",
                ),
            ],
        )
        errors = validate_manifest(m, kit)
        assert any(".." in e for e in errors)

    def test_multiple_errors_collected(self, tmp_path: Path) -> None:
        """Multiple validation issues are all reported."""
        kit = tmp_path / "multi"
        kit.mkdir()

        m = Manifest(
            version="1.0",
            root="{cypilot_path}/config/kits/{slug}",
            user_modifiable=True,
            resources=[
                ManifestResource(
                    id="dup", source="missing1", default_path="a", type="file",
                ),
                ManifestResource(
                    id="dup", source="missing2", default_path="b", type="file",
                ),
            ],
        )
        errors = validate_manifest(m, kit)
        # At least: 1 duplicate id + 2 missing source
        assert len(errors) >= 3


# ---------------------------------------------------------------------------
# _validate_against_schema — edge cases for per-file coverage
# ---------------------------------------------------------------------------

from cypilot.utils.manifest import _validate_against_schema


class TestValidateAgainstSchema:
    """Edge-case tests for schema-level structural validation."""

    def test_missing_manifest_section(self) -> None:
        """No [manifest] table → error and early return."""
        errors = _validate_against_schema({"resources": [{"id": "x"}]})
        assert any("Missing or invalid [manifest]" in e for e in errors)

    def test_manifest_root_empty_string(self) -> None:
        """[manifest].root present but whitespace-only → error."""
        errors = _validate_against_schema({
            "manifest": {"version": "1.0", "root": "  "},
            "resources": [{"id": "a", "source": "a", "default_path": "a", "type": "file"}],
        })
        assert any("root" in e for e in errors)

    def test_manifest_user_modifiable_not_bool(self) -> None:
        """[manifest].user_modifiable is a string instead of bool → error."""
        errors = _validate_against_schema({
            "manifest": {"version": "1.0", "user_modifiable": "yes"},
            "resources": [{"id": "a", "source": "a", "default_path": "a", "type": "file"}],
        })
        assert any("user_modifiable" in e and "boolean" in e for e in errors)

    def test_resource_not_a_table(self) -> None:
        """Resource entry is a string instead of a table → error."""
        errors = _validate_against_schema({
            "manifest": {"version": "1.0"},
            "resources": ["not_a_table"],
        })
        assert any("must be a table" in e for e in errors)

    def test_resource_id_missing(self) -> None:
        """Resource without id field → error."""
        errors = _validate_against_schema({
            "manifest": {"version": "1.0"},
            "resources": [{"source": "a.md", "default_path": "a.md", "type": "file"}],
        })
        assert any(".id is required" in e for e in errors)

    def test_resource_source_missing(self) -> None:
        """Resource without source field → error."""
        errors = _validate_against_schema({
            "manifest": {"version": "1.0"},
            "resources": [{"id": "a", "default_path": "a.md", "type": "file"}],
        })
        assert any(".source is required" in e for e in errors)

    def test_resource_default_path_missing(self) -> None:
        """Resource without default_path field → error."""
        errors = _validate_against_schema({
            "manifest": {"version": "1.0"},
            "resources": [{"id": "a", "source": "a.md", "type": "file"}],
        })
        assert any(".default_path is required" in e for e in errors)

    def test_resource_description_not_string(self) -> None:
        """Resource description is an int instead of string → error."""
        errors = _validate_against_schema({
            "manifest": {"version": "1.0"},
            "resources": [{"id": "a", "source": "a", "default_path": "a", "type": "file", "description": 42}],
        })
        assert any("description" in e and "string" in e for e in errors)

    def test_resource_user_modifiable_not_bool(self) -> None:
        """Resource user_modifiable is a string instead of bool → error."""
        errors = _validate_against_schema({
            "manifest": {"version": "1.0"},
            "resources": [{"id": "a", "source": "a", "default_path": "a", "type": "file", "user_modifiable": "yes"}],
        })
        assert any("user_modifiable" in e and "boolean" in e for e in errors)


# ---------------------------------------------------------------------------
# build_source_to_resource_mapping
# ---------------------------------------------------------------------------

class TestBuildSourceToResourceMapping:
    """Tests for build_source_to_resource_mapping function."""

    def test_no_manifest_returns_empty(self, tmp_path: Path) -> None:
        """Kit without manifest.toml returns empty dicts."""
        from cypilot.utils.manifest import build_source_to_resource_mapping

        kit = tmp_path / "kit"
        kit.mkdir()
        (kit / "SKILL.md").write_text("# Skill\n", encoding="utf-8")

        source_map, resource_info = build_source_to_resource_mapping(kit)
        assert source_map == {}
        assert resource_info == {}

    def test_file_resource_mapping(self, tmp_path: Path) -> None:
        """File resources are mapped directly."""
        from cypilot.utils.manifest import build_source_to_resource_mapping, ResourceInfo

        kit = tmp_path / "kit"
        kit.mkdir()
        (kit / "template.md").write_text("# Template\n", encoding="utf-8")

        _write_manifest(kit, """\
            [manifest]
            version = "1.0"

            [[resources]]
            id = "my_template"
            source = "template.md"
            default_path = "template.md"
            type = "file"
        """)

        source_map, resource_info = build_source_to_resource_mapping(kit)

        assert source_map == {"template.md": "my_template"}
        assert "my_template" in resource_info
        assert resource_info["my_template"].type == "file"
        assert resource_info["my_template"].source_base == "template.md"

    def test_directory_resource_expands_files(self, tmp_path: Path) -> None:
        """Directory resources expand to all files within."""
        from cypilot.utils.manifest import build_source_to_resource_mapping, ResourceInfo

        kit = tmp_path / "kit"
        kit.mkdir()
        (kit / "artifacts" / "ADR").mkdir(parents=True)
        (kit / "artifacts" / "ADR" / "template.md").write_text("# ADR\n", encoding="utf-8")
        (kit / "artifacts" / "ADR" / "checklist.md").write_text("# Check\n", encoding="utf-8")
        (kit / "artifacts" / "ADR" / "examples").mkdir()
        (kit / "artifacts" / "ADR" / "examples" / "example.md").write_text("# Ex\n", encoding="utf-8")

        _write_manifest(kit, """\
            [manifest]
            version = "1.0"

            [[resources]]
            id = "adr_artifacts"
            source = "artifacts/ADR"
            default_path = "artifacts/ADR"
            type = "directory"
        """)

        source_map, resource_info = build_source_to_resource_mapping(kit)

        # All files in directory should map to same resource id
        assert source_map["artifacts/ADR/template.md"] == "adr_artifacts"
        assert source_map["artifacts/ADR/checklist.md"] == "adr_artifacts"
        assert source_map["artifacts/ADR/examples/example.md"] == "adr_artifacts"

        # Resource info should have directory type
        assert resource_info["adr_artifacts"].type == "directory"
        assert resource_info["adr_artifacts"].source_base == "artifacts/ADR"

    def test_mixed_file_and_directory_resources(self, tmp_path: Path) -> None:
        """Both file and directory resources are handled correctly."""
        from cypilot.utils.manifest import build_source_to_resource_mapping

        kit = tmp_path / "kit"
        kit.mkdir()
        (kit / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
        (kit / "artifacts" / "ADR").mkdir(parents=True)
        (kit / "artifacts" / "ADR" / "template.md").write_text("# ADR\n", encoding="utf-8")

        _write_manifest(kit, """\
            [manifest]
            version = "1.0"

            [[resources]]
            id = "skill_file"
            source = "SKILL.md"
            default_path = "SKILL.md"
            type = "file"

            [[resources]]
            id = "adr_dir"
            source = "artifacts/ADR"
            default_path = "artifacts/ADR"
            type = "directory"
        """)

        source_map, resource_info = build_source_to_resource_mapping(kit)

        assert source_map["SKILL.md"] == "skill_file"
        assert source_map["artifacts/ADR/template.md"] == "adr_dir"
        assert resource_info["skill_file"].type == "file"
        assert resource_info["adr_dir"].type == "directory"


# ---------------------------------------------------------------------------
# file_level_kit_update integration
# ---------------------------------------------------------------------------

class TestFileLevelKitUpdateIntegration:
    """Integration tests for file_level_kit_update with manifest-driven bindings."""

    def test_file_and_directory_resources_written_to_bound_paths(self, tmp_path: Path) -> None:
        """Both file and directory resources are written to their registered bound paths."""
        from cypilot.utils.diff_engine import file_level_kit_update
        from cypilot.utils.manifest import build_source_to_resource_mapping

        kit = tmp_path / "kit"
        kit.mkdir()
        user_dir = tmp_path / "user"
        user_dir.mkdir()
        bound_skill = tmp_path / "bound" / "skill.md"
        bound_adr = tmp_path / "bound" / "adr"
        bound_skill.parent.mkdir(parents=True)
        bound_adr.mkdir(parents=True)

        # Create kit source with file resource (SKILL.md) and directory resource (artifacts/ADR)
        (kit / "SKILL.md").write_text("# Skill File\n", encoding="utf-8")
        (kit / "artifacts" / "ADR").mkdir(parents=True)
        (kit / "artifacts" / "ADR" / "template.md").write_text("# ADR Template\n", encoding="utf-8")
        (kit / "artifacts" / "ADR" / "checklist.md").write_text("# ADR Checklist\n", encoding="utf-8")

        _write_manifest(kit, """\
            [manifest]
            version = "1.0"

            [[resources]]
            id = "skill_file"
            source = "SKILL.md"
            default_path = "SKILL.md"
            type = "file"

            [[resources]]
            id = "adr_dir"
            source = "artifacts/ADR"
            default_path = "artifacts/ADR"
            type = "directory"
        """)

        # Build mappings from manifest
        source_to_resource_id, resource_info = build_source_to_resource_mapping(kit)

        # Resource bindings redirect to custom locations
        resource_bindings = {
            "skill_file": bound_skill,
            "adr_dir": bound_adr,
        }

        result = file_level_kit_update(
            kit,
            user_dir,
            auto_approve=True,
            source_to_resource_id=source_to_resource_id,
            resource_info=resource_info,
            resource_bindings=resource_bindings,
        )

        # Verify file resource written to bound path
        assert bound_skill.is_file(), "skill_file should be written to bound path"
        assert bound_skill.read_text(encoding="utf-8") == "# Skill File\n"

        # Verify directory resource files written to bound directory
        assert (bound_adr / "template.md").is_file(), "adr_dir/template.md should be written"
        assert (bound_adr / "checklist.md").is_file(), "adr_dir/checklist.md should be written"
        assert (bound_adr / "template.md").read_text(encoding="utf-8") == "# ADR Template\n"
        assert (bound_adr / "checklist.md").read_text(encoding="utf-8") == "# ADR Checklist\n"

        # Verify files NOT written to user_dir (they went to bound paths)
        assert not (user_dir / "SKILL.md").exists()
        assert not (user_dir / "artifacts" / "ADR" / "template.md").exists()

        # Verify result reports added files
        assert result["status"] == "updated"
        added_paths = [e["path"] for e in result["added"]]
        assert "SKILL.md" in added_paths
        assert "artifacts/ADR/template.md" in added_paths
        assert "artifacts/ADR/checklist.md" in added_paths
