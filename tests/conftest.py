from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    spider_scripts_dir = repo_root / "skills" / "spider" / "scripts"
    sys.path.insert(0, str(spider_scripts_dir))
