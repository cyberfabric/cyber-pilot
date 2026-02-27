"""
Cypilot validate-toc command — validate Table of Contents in Markdown files.

Checks that TOC exists, anchors point to real headings, all headings are
covered, and the TOC is not stale.  Thin CLI wrapper around
``cypilot.utils.toc.validate_toc``.
"""

import argparse
import json
from pathlib import Path
from typing import List

from ..utils.toc import validate_toc


def cmd_validate_toc(argv: List[str]) -> int:
    """Validate Table of Contents in markdown files."""
    p = argparse.ArgumentParser(
        prog="cypilot validate-toc",
        description="Validate Table of Contents in Markdown files",
    )
    p.add_argument(
        "files",
        nargs="+",
        help="Markdown file path(s) to validate",
    )
    p.add_argument(
        "--max-level",
        type=int,
        default=6,
        help="Maximum heading level to include (default: 6)",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Include full error details in output",
    )
    args = p.parse_args(argv)

    results = []
    total_errors = 0
    total_warnings = 0

    for filepath_str in args.files:
        filepath = Path(filepath_str).resolve()

        if not filepath.is_file():
            results.append({
                "file": str(filepath),
                "status": "ERROR",
                "message": "File not found",
            })
            total_errors += 1
            continue

        content = filepath.read_text(encoding="utf-8")
        report = validate_toc(
            content,
            artifact_path=filepath,
            max_heading_level=args.max_level,
        )

        errors = report.get("errors", [])
        warnings = report.get("warnings", [])
        total_errors += len(errors)
        total_warnings += len(warnings)

        file_result: dict = {
            "file": str(filepath),
            "status": "FAIL" if errors else ("WARN" if warnings else "PASS"),
            "error_count": len(errors),
            "warning_count": len(warnings),
        }

        if args.verbose or errors:
            file_result["errors"] = errors
        if args.verbose or warnings:
            file_result["warnings"] = warnings

        results.append(file_result)

    overall = "PASS"
    if total_errors:
        overall = "FAIL"
    elif total_warnings:
        overall = "WARN"

    output = {
        "status": overall,
        "files_validated": len(results),
        "error_count": total_errors,
        "warning_count": total_warnings,
        "results": results,
    }

    pretty = args.verbose or overall != "PASS"
    print(json.dumps(output, indent=2 if pretty else None, ensure_ascii=False))

    if total_errors:
        return 2
    return 0
