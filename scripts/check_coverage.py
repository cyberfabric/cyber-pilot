#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from typing import Any


def _iter_covered_files(data: dict[str, Any]):
    files = data.get("files") or {}
    if not isinstance(files, dict):
        return []
    return list(files.items())


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("coverage_json", help="Path to coverage JSON report (pytest-cov --cov-report=json:...) ")
    p.add_argument("--root", default="skills/cypilot/scripts/cypilot", help="Only enforce threshold for files under this directory")
    p.add_argument("--min", dest="min_percent", type=float, default=90.0, help="Minimum required per-file coverage percent")
    args = p.parse_args()

    report_path = Path(args.coverage_json)
    data = json.loads(report_path.read_text(encoding="utf-8"))

    root = Path(args.root).resolve()
    threshold = float(args.min_percent)

    below: list[tuple[str, float]] = []

    for fname, info in _iter_covered_files(data):
        try:
            pth = Path(fname)
        except Exception:
            continue

        if pth.suffix != ".py":
            continue

        try:
            rp = pth.resolve()
        except Exception:
            continue

        if root not in rp.parents and rp != root:
            continue

        summary = (info or {}).get("summary") or {}
        pc = summary.get("percent_covered")
        if pc is None:
            continue

        pc = float(pc)
        if pc < threshold:
            below.append((str(pth), pc))

    if below:
        below.sort(key=lambda x: x[1])
        print(f"ERROR: per-file coverage below {threshold:.0f}%")
        for path, pc in below:
            print(f"  {pc:6.2f}%  {path}")
        return 1

    print(f"OK: all files under {root} have coverage >= {threshold:.0f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
