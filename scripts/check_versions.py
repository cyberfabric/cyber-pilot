#!/usr/bin/env python3
"""Version consistency checker for Cypilot CI.

Checks:
1. Kit version bump: if kits/{slug}/ files changed vs base branch, conf.toml
   version must be higher than on the base branch.

Proxy version is read at runtime via importlib.metadata and skill version
is resolved dynamically via git tags / meta.toml (ADR-0015). Neither
requires a cross-file consistency check.

Usage:
    python3 scripts/check_versions.py [--base origin/main]
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def _read_py_version(path: Path) -> str | None:
    """Extract __version__ = '...' from a Python file."""
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("__version__"):
            m = re.search(r"""['"]([^'"]+)['"]""", line)
            if m:
                return m.group(1)
    return None


def _read_toml_version(path: Path) -> str | None:
    """Extract version = '...' from a TOML file (simple regex, no tomllib needed)."""
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("version") and "=" in line:
            val = line.split("=", 1)[1].strip().strip('"').strip("'")
            return val
    return None


def _normalize_version(v: str) -> str:
    """Strip leading 'v' for comparison."""
    return v.lstrip("v")


def _git_diff_names(base: str, path_prefix: str) -> list[str]:
    """Return list of changed files under path_prefix relative to base."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base, "--", path_prefix],
            capture_output=True, text=True, check=True,
        )
        return [f for f in result.stdout.strip().splitlines() if f]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def _git_show_file(base: str, filepath: str) -> str | None:
    """Read file content from a git ref."""
    try:
        result = subprocess.run(
            ["git", "show", f"{base}:{filepath}"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _extract_version_from_content(content: str) -> str | None:
    """Extract version = N from TOML content string."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("version") and "=" in line:
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def check_kit_version_bump(root: Path, base: str) -> list[str]:
    """Check that kit conf.toml version is bumped when kit files change."""
    errors: list[str] = []

    kits_dir = root / "kits"
    if not kits_dir.is_dir():
        return errors

    for kit_dir in sorted(kits_dir.iterdir()):
        if not kit_dir.is_dir():
            continue
        slug = kit_dir.name
        kit_prefix = f"kits/{slug}/"

        changed = _git_diff_names(base, kit_prefix)
        if not changed:
            continue

        # Filter out conf.toml itself and non-content files
        content_changes = [
            f for f in changed
            if f != f"kits/{slug}/conf.toml"
            and not f.endswith("/example/")
            and "/example/" not in f
        ]
        if not content_changes:
            continue

        # Compare conf.toml versions
        current_version = _read_toml_version(kit_dir / "conf.toml")
        if current_version is None:
            errors.append(f"Kit '{slug}': cannot read version from kits/{slug}/conf.toml")
            continue

        base_content = _git_show_file(base, f"kits/{slug}/conf.toml")
        if base_content is None:
            # New kit, no base version — OK
            continue

        base_version = _extract_version_from_content(base_content)
        if base_version is None:
            continue

        try:
            cur_int = int(current_version)
            base_int = int(base_version)
        except ValueError:
            errors.append(
                f"Kit '{slug}': non-integer version "
                f"(current={current_version}, base={base_version})"
            )
            continue

        if cur_int <= base_int:
            errors.append(
                f"Kit '{slug}': files changed but conf.toml version not bumped "
                f"(current={cur_int}, base={base_int}). "
                f"Changed files: {', '.join(content_changes[:5])}"
                + (f" (+{len(content_changes) - 5} more)" if len(content_changes) > 5 else "")
            )

    return errors


def main() -> int:
    p = argparse.ArgumentParser(
        description="Check version consistency across Cypilot components",
    )
    p.add_argument(
        "--base", default="origin/main",
        help="Git ref to compare kit changes against (default: origin/main)",
    )
    args = p.parse_args()

    root = Path(__file__).resolve().parent.parent

    all_errors: list[str] = []

    print(f"Checking kit version bumps (vs {args.base})...")
    all_errors.extend(check_kit_version_bump(root, args.base))

    if all_errors:
        print()
        print(f"FAIL: {len(all_errors)} version issue(s) found:")
        for err in all_errors:
            print(f"  ✗ {err}")
        return 1

    print()
    print("PASS: all version checks OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
