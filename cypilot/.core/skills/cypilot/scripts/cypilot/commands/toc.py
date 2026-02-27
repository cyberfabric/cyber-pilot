"""
Cypilot TOC Command — Generate Table of Contents for Markdown files.

Thin CLI wrapper around the unified ``cypilot.utils.toc`` module.
"""

import argparse
import json
from pathlib import Path
from typing import List

from cypilot.utils.toc import (
    github_anchor as _slugify,
    parse_headings as _parse_headings,
    build_toc as _build_toc,
    process_file as _process_file,
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
    args = p.parse_args(argv)

    results = []
    for filepath_str in args.files:
        filepath = Path(filepath_str).resolve()
        result = _process_file(
            filepath,
            max_level=args.max_level,
            dry_run=args.dry_run,
            indent_size=args.indent,
        )
        results.append(result)

    output = {
        "status": "OK",
        "files_processed": len(results),
        "results": results,
    }

    # Set status based on results
    if any(r["status"] == "ERROR" for r in results):
        output["status"] = "PARTIAL" if len(results) > 1 else "ERROR"

    print(json.dumps(output, indent=2, ensure_ascii=False))

    return 1 if output["status"] == "ERROR" else 0
