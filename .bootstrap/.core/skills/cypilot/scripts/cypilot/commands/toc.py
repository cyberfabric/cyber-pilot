"""
Cypilot TOC Command — Generate Table of Contents for Markdown files.

Thin CLI wrapper around the unified ``cypilot.utils.toc`` module.
"""

import argparse
import json
from pathlib import Path
from typing import List

from cypilot.utils.toc import (
    process_file as _process_file,
    validate_toc as _validate_toc,
)


def cmd_toc(argv: List[str]) -> int:
    """Generate/update Table of Contents in markdown files."""
    p = argparse.ArgumentParser(
        prog="cypilot toc",
        description="Generate or update Table of Contents in Markdown files",
    )
    p.add_argument(
        "files",
        nargs="+",
        help="Markdown file path(s) to process",
    )
    p.add_argument(
        "--max-level",
        type=int,
        default=6,
        help="Maximum heading level to include (default: 6)",
    )
    p.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indent spaces per nesting level (default: 2)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files",
    )
    p.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip post-generation validation",
    )
    args = p.parse_args(argv)

    results = []
    validation_errors = 0
    for filepath_str in args.files:
        filepath = Path(filepath_str).resolve()
        result = _process_file(
            filepath,
            max_level=args.max_level,
            dry_run=args.dry_run,
            indent_size=args.indent,
        )

        # Auto-validate after generation (unless skipped or dry-run)
        if (not args.skip_validate
                and not args.dry_run
                and filepath.is_file()
                and result.get("status") not in ("ERROR", "SKIP")):
            content = filepath.read_text(encoding="utf-8")
            report = _validate_toc(
                content,
                artifact_path=filepath,
                max_heading_level=args.max_level,
            )
            errs = report.get("errors", [])
            warns = report.get("warnings", [])
            if errs or warns:
                result["validation"] = {
                    "status": "FAIL" if errs else "WARN",
                    "errors": len(errs),
                    "warnings": len(warns),
                    "details": errs + warns,
                }
                validation_errors += len(errs)
            else:
                result["validation"] = {"status": "PASS"}

        results.append(result)

    output = {
        "status": "OK",
        "files_processed": len(results),
        "results": results,
    }

    if validation_errors:
        output["status"] = "VALIDATION_FAIL"
    elif any(r["status"] == "ERROR" for r in results):
        output["status"] = "PARTIAL" if len(results) > 1 else "ERROR"

    print(json.dumps(output, indent=2, ensure_ascii=False))

    if validation_errors:
        return 2
    return 1 if output["status"] == "ERROR" else 0
