"""
Tests for cache filtering — issue #110.

Verifies that copy_from_local() and download_and_cache() exclude
non-distributable content (ADR/, PRD.md, DESIGN.md, etc.) from the cache,
and that only specs/ and features/ survive under architecture/.
"""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from cypilot_proxy.cache import (
    _ARCHITECTURE_DISTRIBUTABLE,
    _CACHE_COPY_NAMES,
    _prune_architecture,
    copy_from_local,
)


class TestPruneArchitecture:
    """Tests for _prune_architecture() helper."""

    def test_removes_adr_directory(self) -> None:
        """Verify ADR/ directory is removed from architecture/."""
        with TemporaryDirectory() as tmpdir:
            cache = Path(tmpdir)
            adr = cache / "architecture" / "ADR"
            adr.mkdir(parents=True)
            (adr / "0001-some-decision.md").write_text("# ADR")

            _prune_architecture(cache)

            assert not adr.exists(), "ADR/ should be removed"

    def test_removes_internal_files(self) -> None:
        """Verify all Cypilot-internal files are removed from architecture/."""
        with TemporaryDirectory() as tmpdir:
            cache = Path(tmpdir)
            arch = cache / "architecture"
            arch.mkdir(parents=True)
            for name in ("PRD.md", "DESIGN.md", "DECOMPOSITION.md", "AUDIT-REPORT.md"):
                (arch / name).write_text(f"# {name}")

            _prune_architecture(cache)

            for name in ("PRD.md", "DESIGN.md", "DECOMPOSITION.md", "AUDIT-REPORT.md"):
                assert not (arch / name).exists(), f"{name} should be removed"

    def test_preserves_specs_directory(self) -> None:
        """Verify specs/ is kept intact after pruning."""
        with TemporaryDirectory() as tmpdir:
            cache = Path(tmpdir)
            specs = cache / "architecture" / "specs"
            specs.mkdir(parents=True)
            (specs / "CLISPEC.md").write_text("# CLI Spec")

            _prune_architecture(cache)

            assert specs.is_dir(), "specs/ should be preserved"
            assert (specs / "CLISPEC.md").exists(), "specs/CLISPEC.md should be preserved"

    def test_preserves_features_directory(self) -> None:
        """Verify features/ is kept intact after pruning."""
        with TemporaryDirectory() as tmpdir:
            cache = Path(tmpdir)
            features = cache / "architecture" / "features"
            features.mkdir(parents=True)
            (features / "core.md").write_text("# Core Feature")

            _prune_architecture(cache)

            assert features.is_dir(), "features/ should be preserved"
            assert (features / "core.md").exists(), "features/core.md should be preserved"

    def test_skips_when_no_architecture_dir(self) -> None:
        """Verify no error when architecture/ does not exist."""
        with TemporaryDirectory() as tmpdir:
            cache = Path(tmpdir)
            _prune_architecture(cache)

    def test_handles_mixed_content(self) -> None:
        """Verify only specs/ and features/ remain when mixed content exists."""
        with TemporaryDirectory() as tmpdir:
            cache = Path(tmpdir)
            arch = cache / "architecture"
            # Distributable
            (arch / "specs").mkdir(parents=True)
            (arch / "specs" / "CLISPEC.md").write_text("# spec")
            (arch / "features").mkdir(parents=True)
            (arch / "features" / "core.md").write_text("# feature")
            # Non-distributable
            (arch / "ADR").mkdir(parents=True)
            (arch / "ADR" / "0001.md").write_text("# adr")
            (arch / "PRD.md").write_text("# prd")

            _prune_architecture(cache)

            remaining = sorted(item.name for item in arch.iterdir())
            assert remaining == ["features", "specs"], (
                f"Only specs/ and features/ should remain, got: {remaining}"
            )


class TestCopyFromLocalFiltering:
    """Tests for copy_from_local() filtering behavior."""

    def _make_source(self, root: Path, dirs: list, files: list | None = None) -> None:
        """Create a fake source directory with given dirs and files."""
        for d in dirs:
            (root / d).mkdir(parents=True, exist_ok=True)
            (root / d / "README.md").write_text(f"# {d}")
        for f in (files or []):
            (root / f).write_text(f"# {f}")

    def test_excludes_non_distributable_dirs(self) -> None:
        """Verify directories not in _CACHE_COPY_NAMES are excluded from cache."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "source"
            cache = tmp / "cache"
            version_file = tmp / ".version"

            self._make_source(source, ["tests", "examples", ".git", "docs"])

            with (
                patch("cypilot_proxy.cache.get_cache_dir", return_value=cache),
                patch("cypilot_proxy.cache.get_version_file", return_value=version_file),
            ):
                ok, msg = copy_from_local(str(source), force=True)

            assert ok, f"copy_from_local failed: {msg}"
            for name in ("tests", "examples", ".git", "docs"):
                assert not (cache / name).exists(), f"{name} should NOT be in cache"

    def test_copies_distributable_dirs(self) -> None:
        """Verify all COPY_DIRS directories are present in cache after copy."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "source"
            cache = tmp / "cache"
            version_file = tmp / ".version"

            self._make_source(
                source,
                ["architecture", "requirements", "schemas", "workflows", "skills"],
            )

            with (
                patch("cypilot_proxy.cache.get_cache_dir", return_value=cache),
                patch("cypilot_proxy.cache.get_version_file", return_value=version_file),
            ):
                ok, msg = copy_from_local(str(source), force=True)

            assert ok, f"copy_from_local failed: {msg}"
            for name in ("architecture", "requirements", "schemas", "workflows", "skills"):
                assert (cache / name).is_dir(), f"{name} should be in cache"

    def test_prunes_architecture_after_copy(self) -> None:
        """Verify architecture/ is pruned to specs/ and features/ only after copy."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "source"
            cache = tmp / "cache"
            version_file = tmp / ".version"

            # Create architecture with mixed content
            arch = source / "architecture"
            (arch / "ADR").mkdir(parents=True)
            (arch / "ADR" / "0001.md").write_text("# adr")
            (arch / "specs").mkdir(parents=True)
            (arch / "specs" / "CLISPEC.md").write_text("# spec")
            (arch / "PRD.md").write_text("# prd")

            with (
                patch("cypilot_proxy.cache.get_cache_dir", return_value=cache),
                patch("cypilot_proxy.cache.get_version_file", return_value=version_file),
            ):
                ok, msg = copy_from_local(str(source), force=True)

            assert ok, f"copy_from_local failed: {msg}"
            assert (cache / "architecture" / "specs").is_dir(), "specs/ should exist"
            assert not (cache / "architecture" / "ADR").exists(), "ADR/ should be pruned"
            assert not (cache / "architecture" / "PRD.md").exists(), "PRD.md should be pruned"

    def test_copies_build_metadata_files(self) -> None:
        """Verify build metadata files like pyproject.toml are cached."""
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "source"
            cache = tmp / "cache"
            version_file = tmp / ".version"

            source.mkdir(parents=True)
            (source / "pyproject.toml").write_text("[build-system]\n")

            with (
                patch("cypilot_proxy.cache.get_cache_dir", return_value=cache),
                patch("cypilot_proxy.cache.get_version_file", return_value=version_file),
            ):
                ok, msg = copy_from_local(str(source), force=True)

            assert ok, f"copy_from_local failed: {msg}"
            assert (cache / "pyproject.toml").is_file(), "pyproject.toml should be in cache"


class TestConstants:
    """Tests for cache filtering constants."""

    def test_cache_copy_names_contains_copy_dirs(self) -> None:
        """Verify _CACHE_COPY_NAMES is a superset of the downstream COPY_DIRS."""
        required = {"architecture", "requirements", "schemas", "workflows", "skills"}
        assert required.issubset(_CACHE_COPY_NAMES), (
            f"_CACHE_COPY_NAMES must contain all COPY_DIRS. Missing: {required - _CACHE_COPY_NAMES}"
        )

    def test_architecture_distributable_is_specs_and_features(self) -> None:
        """Verify _ARCHITECTURE_DISTRIBUTABLE contains exactly specs and features."""
        assert _ARCHITECTURE_DISTRIBUTABLE == {"specs", "features"}, (
            f"Expected {{specs, features}}, got {_ARCHITECTURE_DISTRIBUTABLE}"
        )
