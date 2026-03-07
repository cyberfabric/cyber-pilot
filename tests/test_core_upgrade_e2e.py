"""
End-to-end tests for cypilot core upgrade from every historical version to HEAD.

For each v3.x git tag:
  1. Extract the cache snapshot (architecture/, requirements/, schemas/,
     workflows/, skills/, kits/, whatsnew.toml) as it existed at that tag.
  2. ``cpt init --yes`` a fresh project using that old cache.
  3. ``cpt update -y`` with the CURRENT (HEAD) cache.
  4. Assert:
     - exit code 0
     - status PASS or WARN (no hard errors)
     - .core/ files replaced
     - kit updated / migrated / installed
     - no top-level errors

All operations are non-interactive (``--yes`` auto-approves everything).
"""

import io
import json
import os
import shutil
import subprocess
import sys
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

# ---------------------------------------------------------------------------
# Repo constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories that constitute a valid cache (copied into .core/ by _copy_from_cache).
_CACHE_DIRS = ["architecture", "requirements", "schemas", "workflows", "skills"]
# Extra top-level files that may exist in cache.
_CACHE_FILES = ["whatsnew.toml"]

# Git tags for each v3.x release.  Update this dict when a new tag is cut.
_VERSION_TAGS: Dict[str, str] = {
    "v3.0.0-beta": "v3.0.0-beta",
    "v3.0.1-beta": "v3.0.1-beta",
    "v3.0.2-beta": "v3.0.2-beta",
    "v3.0.3-beta": "v3.0.3-beta",
    "v3.0.4-beta": "v3.0.4-beta",
    "v3.0.5-beta": "v3.0.5-beta",
    "v3.0.6-beta": "v3.0.6-beta",
    "v3.0.7-beta": "v3.0.7-beta",
    "v3.0.8-beta": "v3.0.8-beta",
}


def _get_all_v3_tags() -> List[str]:
    """Return sorted list of all v3.* git tags in the repo."""
    out = subprocess.check_output(
        ["git", "tag", "--list", "v3.*", "--sort=version:refname"],
        cwd=str(REPO_ROOT),
        text=True,
    )
    return [t.strip() for t in out.strip().splitlines() if t.strip()]


def _check_version_tags_complete() -> None:
    """Fail fast if _VERSION_TAGS is missing any v3.x git tag."""
    actual_tags = set(_get_all_v3_tags())
    registered = set(_VERSION_TAGS.keys())
    missing = sorted(actual_tags - registered)
    if missing:
        raise RuntimeError(
            f"_VERSION_TAGS is incomplete: missing tags {missing}. "
            f"Registered: {sorted(registered)}. "
            f"Add the missing git tags to _VERSION_TAGS."
        )


_check_version_tags_complete()


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _git_show(ref: str, path: str) -> Optional[bytes]:
    """Return raw content of *path* at *ref*, or None if missing."""
    try:
        return subprocess.check_output(
            ["git", "show", f"{ref}:{path}"],
            cwd=str(REPO_ROOT),
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None


def _git_ls_tree(ref: str, directory: str) -> List[str]:
    """List file paths under *directory* at *ref*."""
    try:
        out = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", ref, directory],
            cwd=str(REPO_ROOT),
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return [line for line in out.strip().splitlines() if line]
    except subprocess.CalledProcessError:
        return []


def _extract_cache_at_tag(tag: str, dest: Path) -> None:
    """Extract a cache-like directory tree from *tag* into *dest*.

    Copies: architecture/, requirements/, schemas/, workflows/, skills/,
    kits/, and whatsnew.toml (if present).
    """
    # Core dirs + kits
    for directory in _CACHE_DIRS + ["kits"]:
        paths = _git_ls_tree(tag, f"{directory}/")
        for rel in paths:
            content = _git_show(tag, rel)
            if content is None:
                continue
            out_path = dest / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(content)
    # Top-level files
    for fname in _CACHE_FILES:
        content = _git_show(tag, fname)
        if content is not None:
            (dest / fname).write_bytes(content)


def _build_head_cache(dest: Path) -> None:
    """Build a cache from the current working tree (HEAD)."""
    for directory in _CACHE_DIRS + ["kits"]:
        src = REPO_ROOT / directory
        if src.is_dir():
            shutil.copytree(src, dest / directory, dirs_exist_ok=True)
    for fname in _CACHE_FILES:
        src = REPO_ROOT / fname
        if src.is_file():
            shutil.copy2(src, dest / fname)


# ---------------------------------------------------------------------------
# Project helpers
# ---------------------------------------------------------------------------

def _init_project(root: Path, cache_dir: Path) -> Path:
    """Run ``cpt init --yes`` inside *root* using *cache_dir*.

    Returns the adapter directory (root / "cypilot").
    """
    from cypilot.commands.init import cmd_init
    (root / ".git").mkdir(exist_ok=True)
    cwd = os.getcwd()
    try:
        os.chdir(str(root))
        with patch("cypilot.commands.init.CACHE_DIR", cache_dir):
            buf = io.StringIO()
            err = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(err):
                rc = cmd_init(["--yes"])
            assert rc == 0, (
                f"init failed (rc={rc})\nstdout: {buf.getvalue()}\nstderr: {err.getvalue()}"
            )
    finally:
        os.chdir(cwd)
    return root / "cypilot"


# ---------------------------------------------------------------------------
# E2E upgrade tests
# ---------------------------------------------------------------------------

class TestCoreUpgradeE2E(unittest.TestCase):
    """Upgrade from every historical cypilot release to HEAD."""

    @classmethod
    def setUpClass(cls):
        """Pre-build the HEAD cache (shared across tests)."""
        cls._head_td = TemporaryDirectory()
        cls.head_cache = Path(cls._head_td.name) / "head_cache"
        _build_head_cache(cls.head_cache)

    @classmethod
    def tearDownClass(cls):
        cls._head_td.cleanup()

    # -- parametrised helper ------------------------------------------------

    def _run_upgrade(self, tag: str) -> Dict[str, Any]:
        """Init project at *tag*, update to HEAD.  Returns parsed JSON output."""
        from cypilot.commands.update import cmd_update

        with TemporaryDirectory() as td:
            td_p = Path(td)

            # 1. Extract old cache from tag
            old_cache = td_p / "old_cache"
            _extract_cache_at_tag(tag, old_cache)

            # 2. Init project with old cache
            root = td_p / "proj"
            root.mkdir()
            adapter = _init_project(root, old_cache)
            self.assertTrue(adapter.is_dir(), f"adapter dir not created for {tag}")

            # 3. Run cmd_update -y with HEAD cache
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", self.head_cache):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update(["-y"])
            finally:
                os.chdir(cwd)

            raw = buf.getvalue()
            self.assertEqual(
                rc, 0,
                f"{tag}→HEAD: rc={rc}\nstdout: {raw}\nstderr: {err.getvalue()}",
            )
            return json.loads(raw)

    def _assert_upgrade_ok(self, tag: str) -> None:
        """Run upgrade and validate all assertions."""
        out = self._run_upgrade(tag)

        # -- top-level status --
        self.assertIn(
            out["status"], ("PASS", "WARN"),
            f"{tag}: unexpected status {out['status']}: {json.dumps(out, indent=2)}",
        )

        # -- no top-level errors --
        errors = out.get("errors", [])
        self.assertEqual(errors, [], f"{tag}: top-level errors: {errors}")

        # -- core update happened --
        actions = out.get("actions", {})
        core_update = actions.get("core_update", {})
        self.assertIsInstance(core_update, dict, f"{tag}: core_update missing")
        for name, action in core_update.items():
            self.assertIn(
                action, ("created", "updated"),
                f"{tag}: core dir '{name}' action = '{action}', expected created/updated",
            )

        # -- kit results --
        kits = actions.get("kits", {})
        self.assertIn("sdlc", kits, f"{tag}: sdlc not in kit results")
        sdlc = kits["sdlc"]
        gen_errors = sdlc.get("gen_errors", [])
        self.assertEqual(gen_errors, [], f"{tag}: kit gen_errors: {gen_errors}")

    # -- one test per tag for clear reporting --------------------------------

    def test_upgrade_from_v3_0_0(self):
        self._assert_upgrade_ok("v3.0.0-beta")

    def test_upgrade_from_v3_0_1(self):
        self._assert_upgrade_ok("v3.0.1-beta")

    def test_upgrade_from_v3_0_2(self):
        self._assert_upgrade_ok("v3.0.2-beta")

    def test_upgrade_from_v3_0_3(self):
        self._assert_upgrade_ok("v3.0.3-beta")

    def test_upgrade_from_v3_0_4(self):
        self._assert_upgrade_ok("v3.0.4-beta")

    def test_upgrade_from_v3_0_5(self):
        self._assert_upgrade_ok("v3.0.5-beta")

    def test_upgrade_from_v3_0_6(self):
        self._assert_upgrade_ok("v3.0.6-beta")

    def test_upgrade_from_v3_0_7(self):
        self._assert_upgrade_ok("v3.0.7-beta")

    def test_upgrade_from_v3_0_8(self):
        self._assert_upgrade_ok("v3.0.8-beta")


if __name__ == "__main__":
    unittest.main()
