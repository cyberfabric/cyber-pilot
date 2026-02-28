"""Spec coverage command — measure CDSL marker coverage in code.

@cpt-flow:cpt-cypilot-flow-spec-coverage-report:p1
@cpt-dod:cpt-cypilot-dod-spec-coverage-percentage:p1
@cpt-dod:cpt-cypilot-dod-spec-coverage-granularity:p1
@cpt-dod:cpt-cypilot-dod-spec-coverage-report:p1
"""
import argparse
import json
from pathlib import Path
from typing import List

from ..utils.coverage import FileCoverage, calculate_metrics, generate_report, scan_file_coverage


def cmd_spec_coverage(argv: List[str]) -> int:
    """Run spec coverage analysis on registered codebase files."""
    from ..utils.context import get_context

    # Parse arguments
    p = argparse.ArgumentParser(
        prog="spec-coverage",
        description="Measure CDSL marker coverage in codebase files",
    )
    p.add_argument("--min-coverage", type=float, default=None, help="Minimum coverage percentage (0-100). Exit 2 if below.")
    p.add_argument("--min-granularity", type=float, default=None, help="Minimum granularity score (0-1). Exit 2 if below.")
    p.add_argument("--verbose", action="store_true", help="Include per-file marker details and line ranges")
    p.add_argument("--output", default=None, help="Write report to file instead of stdout")
    args = p.parse_args(argv)

    # Load context
    ctx = get_context()
    if not ctx:
        print(json.dumps({"status": "ERROR", "message": "Cypilot not initialized. Run 'cypilot init' first."}, ensure_ascii=False))
        return 1

    meta = ctx.meta
    project_root = ctx.project_root

    # Resolve all code files from registered codebase entries
    code_files_to_scan: List[Path] = []

    def resolve_code_path(pth: str) -> Path:
        return (project_root / pth).resolve()

    def collect_codebase_files(system_node: object) -> None:
        for cb_entry in getattr(system_node, "codebase", []):
            path_str = getattr(cb_entry, "path", "") if not isinstance(cb_entry, dict) else cb_entry.get("path", "")
            extensions = (getattr(cb_entry, "extensions", None) if not isinstance(cb_entry, dict) else cb_entry.get("extensions", None)) or [".py"]

            code_path = resolve_code_path(path_str)
            if not code_path.exists():
                continue

            if code_path.is_file():
                code_files_to_scan.append(code_path)
            else:
                for ext in extensions:
                    code_files_to_scan.extend(code_path.rglob(f"*{ext}"))

        for child in getattr(system_node, "children", []):
            collect_codebase_files(child)

    for system_node in meta.systems:
        collect_codebase_files(system_node)

    # Filter out ignored files
    filtered_files: List[Path] = []
    for fp in code_files_to_scan:
        try:
            rel = fp.resolve().relative_to(project_root).as_posix()
        except ValueError:
            rel = None
        if rel and meta.is_ignored(rel):
            continue
        filtered_files.append(fp)

    if not filtered_files:
        out = {
            "status": "PASS",
            "summary": {
                "total_files": 0,
                "covered_files": 0,
                "coverage_pct": 0.0,
                "granularity_score": 0.0,
            },
            "message": "No codebase files found in registry",
        }
        _output(out, args)
        return 0

    # Scan each file
    file_coverages: List[FileCoverage] = []
    for fp in sorted(set(filtered_files)):
        fc = scan_file_coverage(fp)
        if fc is not None:
            file_coverages.append(fc)

    # Calculate aggregate metrics
    report = calculate_metrics(file_coverages)

    # Generate JSON report
    json_report = generate_report(report, verbose=args.verbose)

    # Determine status
    status = "PASS"
    threshold_failures: List[str] = []

    if args.min_coverage is not None and report.coverage_pct < args.min_coverage:
        status = "FAIL"
        threshold_failures.append(f"coverage {report.coverage_pct:.2f}% < {args.min_coverage:.2f}%")

    if args.min_granularity is not None and report.granularity_score < args.min_granularity:
        status = "FAIL"
        threshold_failures.append(f"granularity {report.granularity_score:.4f} < {args.min_granularity:.4f}")

    json_report["status"] = status
    if threshold_failures:
        json_report["threshold_failures"] = threshold_failures

    _output(json_report, args)

    return 0 if status == "PASS" else 2


def _output(data: dict, args: argparse.Namespace) -> None:
    """Output JSON report to stdout or file."""
    indent = 2 if getattr(args, "verbose", False) else None
    text = json.dumps(data, indent=indent, ensure_ascii=False)
    if indent:
        text += "\n"
    if getattr(args, "output", None):
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)
