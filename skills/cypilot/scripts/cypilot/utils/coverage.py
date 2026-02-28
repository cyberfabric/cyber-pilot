"""Spec coverage analysis for CDSL markers in code.

Measures two metrics:
1. Coverage percentage: ratio of lines within @cpt-begin/@cpt-end blocks
   to total effective lines (non-blank, non-comment).
2. Granularity score: instruction density — ideally 1 block marker pair
   per 10 lines of code. Files with only scope markers get granularity 0.

@cpt-algo:cpt-cypilot-algo-spec-coverage-scan:p1
@cpt-algo:cpt-cypilot-algo-spec-coverage-metrics:p1
@cpt-algo:cpt-cypilot-algo-spec-coverage-granularity:p1
@cpt-algo:cpt-cypilot-algo-spec-coverage-report:p1
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .codebase import CodeFile, _SCOPE_MARKER_RE, _BLOCK_BEGIN_RE, _BLOCK_END_RE
from .language_config import EXTENSION_COMMENT_DEFAULTS


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class FileCoverage:
    """Coverage record for a single code file."""
    path: str
    total_lines: int  # all lines in file
    effective_lines: int  # non-blank, non-comment
    covered_lines: int  # lines within marker scope
    covered_ranges: List[Tuple[int, int]]  # (start, end) 1-indexed inclusive
    uncovered_ranges: List[Tuple[int, int]]
    scope_marker_count: int
    block_marker_count: int  # number of begin/end pairs
    has_scope_only: bool  # has scope markers but no block markers
    coverage_pct: float
    granularity: float


@dataclass
class CoverageReport:
    """Aggregated coverage report."""
    total_files: int
    covered_files: int
    uncovered_files: int
    total_lines: int
    covered_lines: int
    coverage_pct: float
    granularity_score: float
    per_file: List[FileCoverage]
    flagged_files: List[str]  # files with granularity < 0.5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_blank_or_comment(line: str, ext: str) -> bool:
    """Check if a line is blank or a comment for the given file extension."""
    stripped = line.strip()
    if not stripped:
        return True

    comment_info = EXTENSION_COMMENT_DEFAULTS.get(ext)
    if not comment_info:
        return False

    single_line, multi_line, block_prefixes = comment_info

    for prefix in single_line:
        if stripped.startswith(prefix):
            return True

    for prefix in block_prefixes:
        if stripped.startswith(prefix):
            return True

    for mlc in multi_line:
        if stripped.startswith(mlc["start"]):
            return True

    return False


# ---------------------------------------------------------------------------
# Scan a single file
# ---------------------------------------------------------------------------

def scan_file_coverage(path: Path) -> Optional[FileCoverage]:
    """Scan a code file and calculate its coverage metrics.

    Returns None if the file cannot be read.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None

    lines = text.splitlines()
    total_lines = len(lines)
    ext = path.suffix.lower()

    # @cpt-begin:cpt-cypilot-algo-spec-coverage-scan:p1:inst-scan-count-lines
    effective_lines = 0
    effective_line_set: Set[int] = set()
    for idx, line in enumerate(lines):
        line_no = idx + 1
        if not _is_blank_or_comment(line, ext):
            effective_lines += 1
            effective_line_set.add(line_no)
    # @cpt-end:cpt-cypilot-algo-spec-coverage-scan:p1:inst-scan-count-lines

    if effective_lines == 0:
        return FileCoverage(
            path=str(path),
            total_lines=total_lines,
            effective_lines=0,
            covered_lines=0,
            covered_ranges=[],
            uncovered_ranges=[],
            scope_marker_count=0,
            block_marker_count=0,
            has_scope_only=False,
            coverage_pct=0.0,
            granularity=0.0,
        )

    # @cpt-begin:cpt-cypilot-algo-spec-coverage-scan:p1:inst-scan-scope-markers
    scope_markers: List[int] = []
    # @cpt-end:cpt-cypilot-algo-spec-coverage-scan:p1:inst-scan-scope-markers
    # @cpt-begin:cpt-cypilot-algo-spec-coverage-scan:p1:inst-scan-block-markers
    block_ranges: List[Tuple[int, int]] = []
    open_blocks: Dict[str, int] = {}
    # @cpt-end:cpt-cypilot-algo-spec-coverage-scan:p1:inst-scan-block-markers

    for idx, line in enumerate(lines):
        line_no = idx + 1

        for m in _SCOPE_MARKER_RE.finditer(line):
            scope_markers.append(line_no)

        for m in _BLOCK_BEGIN_RE.finditer(line):
            key = f"{m.group('id')}:{m.group('phase')}:{m.group('inst')}"
            if key not in open_blocks:
                open_blocks[key] = line_no

        for m in _BLOCK_END_RE.finditer(line):
            key = f"{m.group('id')}:{m.group('phase')}:{m.group('inst')}"
            if key in open_blocks:
                start = open_blocks.pop(key)
                block_ranges.append((start, line_no))

    scope_count = len(scope_markers)
    block_count = len(block_ranges)
    has_scope_only = scope_count > 0 and block_count == 0

    # @cpt-begin:cpt-cypilot-algo-spec-coverage-scan:p1:inst-scan-calc-ranges
    covered_set: Set[int] = set()

    if has_scope_only:
        covered_set = set(effective_line_set)
    else:
        for start, end in block_ranges:
            for ln in range(start, end + 1):
                if ln in effective_line_set:
                    covered_set.add(ln)
        for ln in scope_markers:
            if ln in effective_line_set:
                covered_set.add(ln)

    covered_lines = len(covered_set)
    coverage_pct = (covered_lines / effective_lines * 100.0) if effective_lines > 0 else 0.0

    covered_ranges = _build_ranges(sorted(covered_set))
    uncovered_effective = sorted(effective_line_set - covered_set)
    uncovered_ranges = _build_ranges(uncovered_effective)

    if has_scope_only:
        granularity = 0.0
    elif block_count == 0:
        granularity = 0.0
    else:
        ideal_blocks = max(1.0, effective_lines / 10.0)
        granularity = min(1.0, block_count / ideal_blocks)
    # @cpt-end:cpt-cypilot-algo-spec-coverage-scan:p1:inst-scan-calc-ranges

    # @cpt-begin:cpt-cypilot-algo-spec-coverage-scan:p1:inst-scan-return
    return FileCoverage(
        path=str(path),
        total_lines=total_lines,
        effective_lines=effective_lines,
        covered_lines=covered_lines,
        covered_ranges=covered_ranges,
        uncovered_ranges=uncovered_ranges,
        scope_marker_count=scope_count,
        block_marker_count=block_count,
        has_scope_only=has_scope_only,
        coverage_pct=round(coverage_pct, 2),
        granularity=round(granularity, 4),
    )
    # @cpt-end:cpt-cypilot-algo-spec-coverage-scan:p1:inst-scan-return


def _build_ranges(sorted_lines: List[int]) -> List[Tuple[int, int]]:
    """Build contiguous ranges from sorted line numbers."""
    if not sorted_lines:
        return []
    ranges: List[Tuple[int, int]] = []
    start = sorted_lines[0]
    end = start
    for ln in sorted_lines[1:]:
        if ln == end + 1:
            end = ln
        else:
            ranges.append((start, end))
            start = ln
            end = ln
    ranges.append((start, end))
    return ranges


# ---------------------------------------------------------------------------
# Aggregate metrics
# ---------------------------------------------------------------------------

def calculate_metrics(file_coverages: List[FileCoverage]) -> CoverageReport:
    """Calculate aggregate coverage metrics from per-file data."""
    # @cpt-begin:cpt-cypilot-algo-spec-coverage-metrics:p1:inst-metrics-sum-total
    total_files = len(file_coverages)
    covered_files = sum(1 for fc in file_coverages if fc.covered_lines > 0)
    uncovered_files = total_files - covered_files
    total_lines = sum(fc.effective_lines for fc in file_coverages)
    # @cpt-end:cpt-cypilot-algo-spec-coverage-metrics:p1:inst-metrics-sum-total

    # @cpt-begin:cpt-cypilot-algo-spec-coverage-metrics:p1:inst-metrics-sum-covered
    covered_lines = sum(fc.covered_lines for fc in file_coverages)
    # @cpt-end:cpt-cypilot-algo-spec-coverage-metrics:p1:inst-metrics-sum-covered

    # @cpt-begin:cpt-cypilot-algo-spec-coverage-metrics:p1:inst-metrics-calc-pct
    coverage_pct = (covered_lines / total_lines * 100.0) if total_lines > 0 else 0.0
    # @cpt-end:cpt-cypilot-algo-spec-coverage-metrics:p1:inst-metrics-calc-pct

    # @cpt-begin:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-foreach
    gran_num = 0.0
    gran_den = 0
    flagged_files: List[str] = []
    # @cpt-end:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-foreach

    for fc in file_coverages:
        if fc.covered_lines > 0:
            # @cpt-begin:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-count-blocks
            gran_num += fc.granularity * fc.effective_lines
            gran_den += fc.effective_lines
            # @cpt-end:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-count-blocks

            # @cpt-begin:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-ideal
            # ideal is effective_lines / 10 — already computed in per-file granularity
            # @cpt-end:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-ideal

            # @cpt-begin:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-calc
            # per-file granularity = min(1.0, actual_blocks / ideal_blocks) — already in fc.granularity
            # @cpt-end:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-calc

            # @cpt-begin:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-flag
            if fc.granularity < 0.5:
                flagged_files.append(fc.path)
            # @cpt-end:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-flag

    # @cpt-begin:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-overall
    granularity_score = (gran_num / gran_den) if gran_den > 0 else 0.0
    # @cpt-end:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-overall
    # @cpt-begin:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-return
    # granularity_score returned as part of CoverageReport below
    # @cpt-end:cpt-cypilot-algo-spec-coverage-granularity:p1:inst-gran-return

    # @cpt-begin:cpt-cypilot-algo-spec-coverage-metrics:p1:inst-metrics-return
    return CoverageReport(
        total_files=total_files,
        covered_files=covered_files,
        uncovered_files=uncovered_files,
        total_lines=total_lines,
        covered_lines=covered_lines,
        coverage_pct=round(coverage_pct, 2),
        granularity_score=round(granularity_score, 4),
        per_file=file_coverages,
        flagged_files=flagged_files,
    )
    # @cpt-end:cpt-cypilot-algo-spec-coverage-metrics:p1:inst-metrics-return


# ---------------------------------------------------------------------------
# Report generation (coverage.py JSON format)
# ---------------------------------------------------------------------------

def generate_report(report: CoverageReport, *, verbose: bool = False, project_root: Optional[Path] = None) -> Dict:
    """Generate JSON report matching coverage.py structure."""
    def _rel(p: str) -> str:
        if project_root is not None:
            try:
                return str(Path(p).relative_to(project_root))
            except ValueError:
                pass
        return p

    # @cpt-begin:cpt-cypilot-algo-spec-coverage-report:p1:inst-report-summary
    summary = {
        "total_files": report.total_files,
        "covered_files": report.covered_files,
        "uncovered_files": report.uncovered_files,
        "total_lines": report.total_lines,
        "covered_lines": report.covered_lines,
        "coverage_pct": report.coverage_pct,
        "granularity_score": report.granularity_score,
    }

    if report.flagged_files:
        summary["flagged_files_count"] = len(report.flagged_files)
    # @cpt-end:cpt-cypilot-algo-spec-coverage-report:p1:inst-report-summary

    # @cpt-begin:cpt-cypilot-algo-spec-coverage-report:p1:inst-report-per-file
    files: Dict[str, Dict] = {}
    uncovered_file_list: List[str] = []

    for fc in report.per_file:
        entry: Dict = {
            "total_lines": fc.effective_lines,
            "covered_lines": fc.covered_lines,
            "coverage_pct": fc.coverage_pct,
            "granularity": fc.granularity,
        }

        if fc.covered_lines == 0:
            uncovered_file_list.append(_rel(fc.path))

        if fc.has_scope_only:
            entry["scope_only"] = True

        # @cpt-begin:cpt-cypilot-algo-spec-coverage-report:p1:inst-report-verbose
        if verbose:
            entry["scope_markers"] = fc.scope_marker_count
            entry["block_markers"] = fc.block_marker_count
            if fc.uncovered_ranges:
                entry["uncovered_ranges"] = [[s, e] for s, e in fc.uncovered_ranges]
            if fc.covered_ranges:
                entry["covered_ranges"] = [[s, e] for s, e in fc.covered_ranges]
        # @cpt-end:cpt-cypilot-algo-spec-coverage-report:p1:inst-report-verbose

        files[_rel(fc.path)] = entry
    # @cpt-end:cpt-cypilot-algo-spec-coverage-report:p1:inst-report-per-file

    # @cpt-begin:cpt-cypilot-algo-spec-coverage-report:p1:inst-report-return
    result: Dict = {
        "summary": summary,
        "files": files,
    }

    if uncovered_file_list:
        result["uncovered_files"] = uncovered_file_list

    if report.flagged_files:
        result["flagged_files"] = [_rel(f) for f in report.flagged_files]

    return result
    # @cpt-end:cpt-cypilot-algo-spec-coverage-report:p1:inst-report-return
