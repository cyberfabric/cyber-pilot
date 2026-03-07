"""
Cypilot validate-toc command — validate Table of Contents in Markdown files.

Checks that TOC exists, anchors point to real headings, all headings are
covered, and the TOC is not stale.  Thin CLI wrapper around
``cypilot.utils.toc.validate_toc``.

@cpt-flow:cpt-cypilot-flow-traceability-validation-validate:p1
@cpt-dod:cpt-cypilot-dod-traceability-validation-structure:p1
"""

# @cpt-begin:cpt-cypilot-algo-traceability-validation-validate-toc:p1:inst-toc-imports
import argparse
import json
from pathlib import Path
from typing import List

from ..utils.toc import validate_toc
from ..utils.ui import ui
# @cpt-end:cpt-cypilot-algo-traceability-validation-validate-toc:p1:inst-toc-imports

def cmd_validate_toc(argv: List[str]) -> int:
    """Validate Table of Contents in markdown files."""
    # @cpt-begin:cpt-cypilot-algo-traceability-validation-validate-toc:p1:inst-toc-parse-args
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
        default=3,
        help="Maximum heading level to include (default: 3)",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Include full error details in output",
    )
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-algo-traceability-validation-validate-toc:p1:inst-toc-parse-args

    results = []
    total_errors = 0
    total_warnings = 0

    # @cpt-begin:cpt-cypilot-algo-traceability-validation-validate-toc:p1:inst-toc-resolve-files
    files_to_validate = [Path(f).resolve() for f in args.files]
    # @cpt-end:cpt-cypilot-algo-traceability-validation-validate-toc:p1:inst-toc-resolve-files

    # @cpt-begin:cpt-cypilot-algo-traceability-validation-validate-toc:p1:inst-toc-foreach-file
    for filepath in files_to_validate:

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
    # @cpt-end:cpt-cypilot-algo-traceability-validation-validate-toc:p1:inst-toc-foreach-file

    # @cpt-begin:cpt-cypilot-algo-traceability-validation-validate-toc:p1:inst-toc-return
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

    ui.result(output, human_fn=lambda d: _human_validate_toc(d))

    if total_errors:
        return 2
    return 0
    # @cpt-end:cpt-cypilot-algo-traceability-validation-validate-toc:p1:inst-toc-return

# @cpt-begin:cpt-cypilot-algo-traceability-validation-validate-toc:p1:inst-toc-format
def _human_validate_toc(data: dict) -> None:
    ui.header("Validate TOC")
    for r in data.get("results", []):
        path = r.get("file", "?")
        status = r.get("status", "?")
        errs = r.get("error_count", 0)
        warns = r.get("warning_count", 0)
        if status == "PASS":
            ui.file_action(path, "unchanged")
        elif status == "FAIL":
            ui.warn(f"{path}: {errs} error(s), {warns} warning(s)")
            for e in r.get("errors", []):
                ui.substep(f"  ✗ {e}")
            for w in r.get("warnings", []):
                ui.substep(f"  ⚠ {w}")
        else:
            ui.substep(f"{path}: {status}")
    overall = data.get("status", "")
    n = data.get("files_validated", 0)
    if overall == "PASS":
        ui.success(f"{n} file(s) validated, all TOCs correct.")
    elif overall == "FAIL":
        ui.error(f"{n} file(s) validated, {data.get('error_count', 0)} error(s) found.")
    else:
        ui.warn(f"{n} file(s) validated ({overall}).")
    ui.blank()
# @cpt-end:cpt-cypilot-algo-traceability-validation-validate-toc:p1:inst-toc-format
