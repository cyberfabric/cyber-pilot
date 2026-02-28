"""Tests for coverage.py — spec coverage analysis utilities."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.utils.coverage import (
    CoverageReport,
    FileCoverage,
    _build_ranges,
    _is_blank_or_comment,
    calculate_metrics,
    generate_report,
    scan_file_coverage,
)


class TestIsBlankOrComment(unittest.TestCase):
    def test_blank_line(self):
        self.assertTrue(_is_blank_or_comment("", ".py"))
        self.assertTrue(_is_blank_or_comment("   ", ".py"))

    def test_python_comment(self):
        self.assertTrue(_is_blank_or_comment("# comment", ".py"))
        self.assertTrue(_is_blank_or_comment("  # indented comment", ".py"))

    def test_python_code(self):
        self.assertFalse(_is_blank_or_comment("x = 1", ".py"))
        self.assertFalse(_is_blank_or_comment("  print('hi')", ".py"))

    def test_js_comment(self):
        self.assertTrue(_is_blank_or_comment("// comment", ".js"))
        self.assertTrue(_is_blank_or_comment("/* block */", ".js"))

    def test_unknown_extension(self):
        self.assertFalse(_is_blank_or_comment("# not a comment", ".xyz"))
        self.assertTrue(_is_blank_or_comment("", ".xyz"))

    def test_multiline_comment_start(self):
        self.assertTrue(_is_blank_or_comment('"""docstring', ".py"))


class TestBuildRanges(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(_build_ranges([]), [])

    def test_single(self):
        self.assertEqual(_build_ranges([5]), [(5, 5)])

    def test_contiguous(self):
        self.assertEqual(_build_ranges([1, 2, 3, 4]), [(1, 4)])

    def test_gaps(self):
        self.assertEqual(_build_ranges([1, 2, 5, 6, 7, 10]), [(1, 2), (5, 7), (10, 10)])

    def test_non_contiguous_singles(self):
        self.assertEqual(_build_ranges([3, 7, 11]), [(3, 3), (7, 7), (11, 11)])


class TestScanFileCoverage(unittest.TestCase):
    def test_unreadable_file(self):
        result = scan_file_coverage(Path("/nonexistent/file.py"))
        self.assertIsNone(result)

    def test_empty_file(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "empty.py"
            p.write_text("", encoding="utf-8")
            fc = scan_file_coverage(p)
            self.assertIsNotNone(fc)
            self.assertEqual(fc.effective_lines, 0)
            self.assertEqual(fc.coverage_pct, 0.0)

    def test_blank_lines_only(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "blank.py"
            p.write_text("\n\n\n", encoding="utf-8")
            fc = scan_file_coverage(p)
            self.assertIsNotNone(fc)
            self.assertEqual(fc.effective_lines, 0)

    def test_scope_marker_only(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "scope.py"
            p.write_text(
                "# @cpt-algo:cpt-my-algo:p1\n"
                "x = 1\n"
                "y = 2\n",
                encoding="utf-8",
            )
            fc = scan_file_coverage(p)
            self.assertIsNotNone(fc)
            self.assertTrue(fc.has_scope_only)
            self.assertEqual(fc.scope_marker_count, 1)
            self.assertEqual(fc.block_marker_count, 0)
            # Scope-only: all effective lines are covered
            self.assertEqual(fc.covered_lines, fc.effective_lines)
            self.assertEqual(fc.granularity, 0.0)

    def test_block_markers(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "blocks.py"
            p.write_text(
                "# @cpt-begin:cpt-my-algo:p1:inst-do-stuff\n"
                "x = 1\n"
                "y = 2\n"
                "# @cpt-end:cpt-my-algo:p1:inst-do-stuff\n"
                "z = 3\n",
                encoding="utf-8",
            )
            fc = scan_file_coverage(p)
            self.assertIsNotNone(fc)
            self.assertFalse(fc.has_scope_only)
            self.assertEqual(fc.block_marker_count, 1)
            # Lines 1-4 are covered (begin, x=1, y=2, end); z=3 is not
            self.assertGreater(fc.covered_lines, 0)
            self.assertLess(fc.covered_lines, fc.effective_lines)
            self.assertGreater(fc.coverage_pct, 0.0)
            self.assertLess(fc.coverage_pct, 100.0)

    def test_no_markers(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "plain.py"
            p.write_text("x = 1\ny = 2\n", encoding="utf-8")
            fc = scan_file_coverage(p)
            self.assertIsNotNone(fc)
            self.assertEqual(fc.covered_lines, 0)
            self.assertEqual(fc.coverage_pct, 0.0)
            self.assertFalse(fc.has_scope_only)

    def test_multiple_blocks(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "multi.py"
            lines = []
            for i in range(5):
                lines.append(f"# @cpt-begin:cpt-my-algo:p1:inst-block-{i}")
                lines.append(f"val_{i} = {i}")
                lines.append(f"# @cpt-end:cpt-my-algo:p1:inst-block-{i}")
            p.write_text("\n".join(lines), encoding="utf-8")
            fc = scan_file_coverage(p)
            self.assertEqual(fc.block_marker_count, 5)
            self.assertEqual(fc.coverage_pct, 100.0)
            self.assertGreater(fc.granularity, 0.0)

    def test_unclosed_block_ignored(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "unclosed.py"
            p.write_text(
                "# @cpt-begin:cpt-my-algo:p1:inst-open\n"
                "x = 1\n",
                encoding="utf-8",
            )
            fc = scan_file_coverage(p)
            self.assertIsNotNone(fc)
            self.assertEqual(fc.block_marker_count, 0)


class TestCalculateMetrics(unittest.TestCase):
    def test_empty_list(self):
        report = calculate_metrics([])
        self.assertEqual(report.total_files, 0)
        self.assertEqual(report.coverage_pct, 0.0)
        self.assertEqual(report.granularity_score, 0.0)

    def test_single_file(self):
        fc = FileCoverage(
            path="test.py",
            total_lines=20,
            effective_lines=15,
            covered_lines=10,
            covered_ranges=[(1, 10)],
            uncovered_ranges=[(11, 15)],
            scope_marker_count=0,
            block_marker_count=2,
            has_scope_only=False,
            coverage_pct=66.67,
            granularity=0.5,
        )
        report = calculate_metrics([fc])
        self.assertEqual(report.total_files, 1)
        self.assertEqual(report.covered_files, 1)
        self.assertEqual(report.uncovered_files, 0)
        self.assertEqual(report.total_lines, 15)
        self.assertEqual(report.covered_lines, 10)
        self.assertAlmostEqual(report.coverage_pct, 66.67, places=1)

    def test_flagged_files(self):
        fc_low = FileCoverage(
            path="low_gran.py", total_lines=100, effective_lines=80,
            covered_lines=60, covered_ranges=[], uncovered_ranges=[],
            scope_marker_count=0, block_marker_count=1, has_scope_only=False,
            coverage_pct=75.0, granularity=0.1,
        )
        fc_high = FileCoverage(
            path="high_gran.py", total_lines=100, effective_lines=80,
            covered_lines=80, covered_ranges=[], uncovered_ranges=[],
            scope_marker_count=0, block_marker_count=10, has_scope_only=False,
            coverage_pct=100.0, granularity=1.0,
        )
        report = calculate_metrics([fc_low, fc_high])
        self.assertIn("low_gran.py", report.flagged_files)
        self.assertNotIn("high_gran.py", report.flagged_files)

    def test_uncovered_file_not_counted(self):
        fc = FileCoverage(
            path="uncov.py", total_lines=10, effective_lines=5,
            covered_lines=0, covered_ranges=[], uncovered_ranges=[],
            scope_marker_count=0, block_marker_count=0, has_scope_only=False,
            coverage_pct=0.0, granularity=0.0,
        )
        report = calculate_metrics([fc])
        self.assertEqual(report.covered_files, 0)
        self.assertEqual(report.uncovered_files, 1)
        self.assertEqual(report.granularity_score, 0.0)


class TestGenerateReport(unittest.TestCase):
    def _make_report(self, per_file=None, flagged=None):
        per_file = per_file or []
        flagged = flagged or []
        return CoverageReport(
            total_files=len(per_file),
            covered_files=sum(1 for f in per_file if f.covered_lines > 0),
            uncovered_files=sum(1 for f in per_file if f.covered_lines == 0),
            total_lines=sum(f.effective_lines for f in per_file),
            covered_lines=sum(f.covered_lines for f in per_file),
            coverage_pct=80.0,
            granularity_score=0.75,
            per_file=per_file,
            flagged_files=flagged,
        )

    def test_empty_report(self):
        report = self._make_report()
        result = generate_report(report)
        self.assertIn("summary", result)
        self.assertIn("files", result)
        self.assertEqual(result["summary"]["total_files"], 0)

    def test_with_project_root(self):
        with TemporaryDirectory() as d:
            fc = FileCoverage(
                path=str(Path(d) / "src" / "test.py"),
                total_lines=10, effective_lines=8, covered_lines=6,
                covered_ranges=[(1, 6)], uncovered_ranges=[(7, 8)],
                scope_marker_count=0, block_marker_count=1,
                has_scope_only=False, coverage_pct=75.0, granularity=0.5,
            )
            report = self._make_report([fc])
            result = generate_report(report, project_root=Path(d))
            # Path should be relative
            self.assertIn("src/test.py", result["files"])

    def test_verbose_includes_ranges(self):
        fc = FileCoverage(
            path="/tmp/test.py",
            total_lines=20, effective_lines=15, covered_lines=10,
            covered_ranges=[(1, 10)], uncovered_ranges=[(11, 15)],
            scope_marker_count=1, block_marker_count=2,
            has_scope_only=False, coverage_pct=66.67, granularity=0.5,
        )
        report = self._make_report([fc])
        result = generate_report(report, verbose=True)
        entry = result["files"]["/tmp/test.py"]
        self.assertIn("scope_markers", entry)
        self.assertIn("block_markers", entry)
        self.assertIn("covered_ranges", entry)
        self.assertIn("uncovered_ranges", entry)

    def test_non_verbose_excludes_ranges(self):
        fc = FileCoverage(
            path="/tmp/test.py",
            total_lines=20, effective_lines=15, covered_lines=10,
            covered_ranges=[(1, 10)], uncovered_ranges=[(11, 15)],
            scope_marker_count=1, block_marker_count=2,
            has_scope_only=False, coverage_pct=66.67, granularity=0.5,
        )
        report = self._make_report([fc])
        result = generate_report(report, verbose=False)
        entry = result["files"]["/tmp/test.py"]
        self.assertNotIn("scope_markers", entry)
        self.assertNotIn("covered_ranges", entry)

    def test_scope_only_flag(self):
        fc = FileCoverage(
            path="/tmp/scope.py",
            total_lines=10, effective_lines=8, covered_lines=8,
            covered_ranges=[(1, 8)], uncovered_ranges=[],
            scope_marker_count=1, block_marker_count=0,
            has_scope_only=True, coverage_pct=100.0, granularity=0.0,
        )
        report = self._make_report([fc])
        result = generate_report(report)
        entry = result["files"]["/tmp/scope.py"]
        self.assertTrue(entry.get("scope_only"))

    def test_uncovered_files_listed(self):
        fc = FileCoverage(
            path="/tmp/no_markers.py",
            total_lines=10, effective_lines=8, covered_lines=0,
            covered_ranges=[], uncovered_ranges=[],
            scope_marker_count=0, block_marker_count=0,
            has_scope_only=False, coverage_pct=0.0, granularity=0.0,
        )
        report = self._make_report([fc])
        result = generate_report(report)
        self.assertIn("uncovered_files", result)
        self.assertIn("/tmp/no_markers.py", result["uncovered_files"])

    def test_flagged_files_listed(self):
        report = self._make_report(flagged=["/tmp/low.py"])
        result = generate_report(report)
        self.assertIn("flagged_files", result)
        self.assertIn("/tmp/low.py", result["flagged_files"])

    def test_flagged_count_in_summary(self):
        report = self._make_report(flagged=["/tmp/low.py"])
        result = generate_report(report)
        self.assertEqual(result["summary"]["flagged_files_count"], 1)

    def test_relative_path_fallback(self):
        fc = FileCoverage(
            path="/other/root/file.py",
            total_lines=5, effective_lines=3, covered_lines=1,
            covered_ranges=[], uncovered_ranges=[],
            scope_marker_count=0, block_marker_count=0,
            has_scope_only=False, coverage_pct=33.0, granularity=0.0,
        )
        report = self._make_report([fc])
        result = generate_report(report, project_root=Path("/different/root"))
        # Can't relativize → falls back to absolute
        self.assertIn("/other/root/file.py", result["files"])


if __name__ == "__main__":
    unittest.main()
