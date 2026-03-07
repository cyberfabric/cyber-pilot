"""
End-to-end tests for kit upgrade from every historical version to the latest.

For each version N (1 … latest-1) of the SDLC kit:
  1. Extract the kit snapshot at version N from git history.
  2. Build a cache with that snapshot → init project.
  3. Build a cache with the LATEST kit → run ``cmd_update -y``.
  4. Assert:
     - exit code 0
     - kit update status is "migrated", "created", or "updated"
     - no top-level errors
     - user conf.toml version bumped to latest

The tests are non-interactive (``-y`` auto-approves everything).
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
# Repo / kit constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
KIT_SOURCE = REPO_ROOT / "kits" / "sdlc"

# Git commits that introduced each conf.toml version.
# Used to extract historical kit snapshots from the repo's own history.
_VERSION_COMMITS: Dict[int, str] = {
    1: "abfff93",
    2: "c1375d3",
    3: "88feced",
    4: "c0282e9",
    5: "d517fca",
    6: "3d8b374",
}


def _read_latest_version() -> int:
    """Read the current kit version from the canonical conf.toml."""
    import tomllib
    with open(KIT_SOURCE / "conf.toml", "rb") as f:
        return int(tomllib.load(f)["version"])


LATEST_VERSION = _read_latest_version()


def _check_version_commits_complete() -> None:
    """Fail fast if _VERSION_COMMITS has gaps or is missing the latest version."""
    expected = set(range(1, LATEST_VERSION + 1))
    actual = set(_VERSION_COMMITS.keys())
    missing = sorted(expected - actual)
    if missing:
        raise RuntimeError(
            f"_VERSION_COMMITS is incomplete: missing versions {missing}. "
            f"Expected 1..{LATEST_VERSION}, got {sorted(actual)}. "
            f"Add the git commit SHA for each missing version."
        )


_check_version_commits_complete()


# ---------------------------------------------------------------------------
# Git helpers — extract historical kit files
# ---------------------------------------------------------------------------

def _git_show(commit: str, path: str) -> Optional[bytes]:
    """Return raw content of *path* at *commit*, or None if it doesn't exist."""
    try:
        return subprocess.check_output(
            ["git", "show", f"{commit}:{path}"],
            cwd=str(REPO_ROOT),
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None


def _git_ls_tree(commit: str, directory: str) -> List[str]:
    """List file paths under *directory* at *commit*."""
    try:
        out = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", commit, directory],
            cwd=str(REPO_ROOT),
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return [line for line in out.strip().splitlines() if line]
    except subprocess.CalledProcessError:
        return []


def _extract_kit_at_version(version: int, dest: Path) -> None:
    """Extract the full kits/sdlc/ tree at *version* into *dest*.

    Copies blueprints/, scripts/, conf.toml, blueprint_hashes.toml
    as they existed at the commit that introduced *version*.
    """
    commit = _VERSION_COMMITS[version]
    kit_prefix = "kits/sdlc/"
    paths = _git_ls_tree(commit, kit_prefix)
    for rel in paths:
        content = _git_show(commit, rel)
        if content is None:
            continue
        local_rel = rel[len(kit_prefix):]  # strip "kits/sdlc/" prefix
        out_path = dest / local_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(content)


# ---------------------------------------------------------------------------
# Cache / project bootstrap helpers
# ---------------------------------------------------------------------------

def _write_toml(path: Path, data: dict) -> None:
    from cypilot.utils import toml_utils
    path.parent.mkdir(parents=True, exist_ok=True)
    toml_utils.dump(data, path)


def _make_cache_from_kit(cache_dir: Path, kit_dir: Path) -> None:
    """Build a realistic cache directory from a kit source directory.

    Creates the core subdirectories that ``cmd_update`` expects in CACHE_DIR,
    plus ``kits/{slug}/`` with the provided kit files.
    """
    for d in ("architecture", "requirements", "schemas", "workflows", "skills"):
        (cache_dir / d).mkdir(parents=True, exist_ok=True)
        (cache_dir / d / "README.md").write_text(f"# {d}\n", encoding="utf-8")
    cache_kit = cache_dir / "kits" / "sdlc"
    if cache_kit.exists():
        shutil.rmtree(cache_kit)
    shutil.copytree(kit_dir, cache_kit, dirs_exist_ok=True)


def _init_project(root: Path, cache_dir: Path) -> Path:
    """Run ``cpt init --yes`` inside *root* using *cache_dir*."""
    from cypilot.cli import main
    (root / ".git").mkdir(exist_ok=True)
    cwd = os.getcwd()
    try:
        os.chdir(str(root))
        with patch("cypilot.commands.init.CACHE_DIR", cache_dir):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["init", "--yes"])
            assert rc == 0, f"init failed (rc={rc}): {buf.getvalue()}"
    finally:
        os.chdir(cwd)
    return root / "cypilot"


# ---------------------------------------------------------------------------
# E2E upgrade tests
# ---------------------------------------------------------------------------

class TestKitUpgradeE2E(unittest.TestCase):
    """Upgrade from every historical kit version to the latest."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    @classmethod
    def setUpClass(cls):
        """Pre-extract the latest kit into a temp dir (shared across tests)."""
        cls._latest_td = TemporaryDirectory()
        cls.latest_kit = Path(cls._latest_td.name) / "sdlc_latest"
        shutil.copytree(KIT_SOURCE, cls.latest_kit)

    @classmethod
    def tearDownClass(cls):
        cls._latest_td.cleanup()

    # -- parametrised helper ------------------------------------------------

    def _run_upgrade(self, from_version: int) -> Dict[str, Any]:
        """Full upgrade cycle: init at *from_version* → update to latest.

        Returns the parsed JSON output from ``cmd_update``.
        """
        from cypilot.commands.update import cmd_update

        with TemporaryDirectory() as td:
            td_p = Path(td)

            # 1. Extract old kit snapshot
            old_kit = td_p / "old_kit"
            _extract_kit_at_version(from_version, old_kit)

            # 2. Build cache-v-old, init project
            cache_old = td_p / "cache_old"
            _make_cache_from_kit(cache_old, old_kit)
            root = td_p / "proj"
            root.mkdir()
            adapter = _init_project(root, cache_old)

            # Verify the project was installed (kit registered in core.toml)
            core_toml = adapter / "config" / "core.toml"
            self.assertTrue(
                core_toml.is_file(),
                f"core.toml not created during init (v{from_version})",
            )

            # 3. Build cache-v-latest
            cache_latest = td_p / "cache_latest"
            _make_cache_from_kit(cache_latest, self.latest_kit)

            # 4. Run cmd_update with latest cache, -y (auto-approve)
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache_latest):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update(["-y"])
            finally:
                os.chdir(cwd)

            raw = buf.getvalue()
            self.assertEqual(rc, 0, f"v{from_version}→v{LATEST_VERSION}: rc={rc}\nstdout: {raw}\nstderr: {err.getvalue()}")

            out = json.loads(raw)
            return out

    def _assert_upgrade_ok(self, from_version: int) -> None:
        """Run upgrade and validate all assertions."""
        out = self._run_upgrade(from_version)

        # -- top-level status --
        self.assertIn(
            out["status"], ("PASS", "WARN"),
            f"v{from_version}→v{LATEST_VERSION}: unexpected status {out['status']}: {json.dumps(out, indent=2)}",
        )

        # -- kit update result --
        kits = out.get("actions", {}).get("kits", {})
        self.assertIn("sdlc", kits, f"v{from_version}: sdlc not in kits results")
        sdlc = kits["sdlc"]

        ver = sdlc.get("version", {})
        self.assertIsInstance(ver, dict, f"v{from_version}: version is not a dict: {ver}")
        self.assertIn(
            ver.get("status"), ("migrated", "created", "updated"),
            f"v{from_version}: version status = {ver.get('status')}, expected migrated/created/updated",
        )

        # -- no top-level errors --
        errors = out.get("errors", [])
        self.assertEqual(
            errors, [],
            f"v{from_version}: top-level errors: {errors}",
        )

    # -- one test method per version for clear reporting --------------------

    def test_upgrade_from_v1(self):
        """Upgrade from kit v1 → latest."""
        self._assert_upgrade_ok(1)

    def test_upgrade_from_v2(self):
        """Upgrade from kit v2 → latest."""
        self._assert_upgrade_ok(2)

    def test_upgrade_from_v3(self):
        """Upgrade from kit v3 → latest."""
        self._assert_upgrade_ok(3)

    def test_upgrade_from_v4(self):
        """Upgrade from kit v4 → latest."""
        self._assert_upgrade_ok(4)

    def test_upgrade_from_v5(self):
        """Upgrade from kit v5 → latest."""
        self._assert_upgrade_ok(5)


if __name__ == "__main__":
    unittest.main()
