"""
Unit tests for PR review helper script.

Tests the pr.py script functions for PR review, status reporting, and metadata fetching.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, Mock, patch, call

# Add pr.py to path (it lives in skills/scripts/)
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "scripts"))

import pr


class TestFindProjectRoot(unittest.TestCase):
    """Test _find_project_root function."""

    def test_find_project_root_via_git(self):
        """Test finding project root via git rev-parse."""
        with TemporaryDirectory() as tmpdir:
            expected_root = str(Path(tmpdir).resolve())
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = expected_root + "\n"

            with patch("subprocess.run", return_value=mock_result):
                root = pr._find_project_root()
                self.assertEqual(root, expected_root)

    def test_find_project_root_fallback_when_not_git_repo(self):
        """Test fallback to script path when git fails."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            root = pr._find_project_root()
            # Should return a path (fallback to script location)
            self.assertIsInstance(root, str)
            self.assertTrue(len(root) > 0)

    def test_find_project_root_fallback_when_git_not_found(self):
        """Test fallback when git command doesn't exist."""
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            root = pr._find_project_root()
            # Should return a path (fallback to script location)
            self.assertIsInstance(root, str)
            self.assertTrue(len(root) > 0)


class TestLoadPrConfig(unittest.TestCase):
    """Test _load_pr_config function."""

    def test_load_pr_config_default_when_no_config(self):
        """Test loading config returns empty dict when files don't exist."""
        with TemporaryDirectory() as tmpdir:
            with patch.object(pr, "ROOT", tmpdir):
                config = pr._load_pr_config()
                self.assertEqual(config, {})

    def test_load_pr_config_reads_from_adapter_path(self):
        """Test loading config from adapter directory."""
        with TemporaryDirectory() as tmpdir:
            # Create .cypilot/.cypilot-config.json
            cypilot_dir = Path(tmpdir) / ".cypilot"
            cypilot_dir.mkdir()
            config_file = cypilot_dir / ".cypilot-config.json"
            config_file.write_text(json.dumps({
                "cypilotAdapterPath": ".custom-adapter"
            }))

            # Create pr-review.json in custom adapter path
            adapter_dir = Path(tmpdir) / ".custom-adapter"
            adapter_dir.mkdir()
            pr_review_file = adapter_dir / "pr-review.json"
            pr_review_config = {"dataDir": ".custom-prs"}
            pr_review_file.write_text(json.dumps(pr_review_config))

            # Mock _CYPILOT_CONFIG_PATH to point to our temp config
            with patch("pr._CYPILOT_CONFIG_PATH", str(config_file)):
                # Also need to patch ROOT for path resolution
                with patch.object(pr, "ROOT", tmpdir):
                    # Reload the config by calling the function directly
                    config = pr._load_pr_config()
                    self.assertEqual(config, pr_review_config)


class TestLoadExcludeList(unittest.TestCase):
    """Test _load_exclude_list function."""

    def test_load_exclude_list_empty_when_no_file(self):
        """Test exclude list is empty when config file doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            with patch.object(pr, "CONFIG_PATH", os.path.join(tmpdir, "config.yaml")):
                excludes = pr._load_exclude_list()
                self.assertEqual(excludes, set())

    def test_load_exclude_list_parses_yaml_section(self):
        """Test parsing exclude_prs section from YAML."""
        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text(
                "exclude_prs:\n"
                "  - 123\n"
                "  - '456'\n"
                "  - \"789\"\n"
                "other_section:\n"
                "  - should_not_include\n"
            )

            with patch.object(pr, "CONFIG_PATH", str(config_file)):
                excludes = pr._load_exclude_list()
                self.assertEqual(excludes, {"123", "456", "789"})

    def test_load_exclude_list_stops_at_next_section(self):
        """Test that parsing stops at next YAML section."""
        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text(
                "exclude_prs:\n"
                "  - 100\n"
                "next_section:\n"
                "  - 200\n"
            )

            with patch.object(pr, "CONFIG_PATH", str(config_file)):
                excludes = pr._load_exclude_list()
                self.assertIn("100", excludes)
                self.assertNotIn("200", excludes)


class TestListOpenPrs(unittest.TestCase):
    """Test _list_open_prs function."""

    def test_list_open_prs_success(self):
        """Test successful PR listing."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps([
            {"number": 1, "title": "Test PR", "author": {"login": "user1"}, "state": "OPEN", "url": "https://github.com/repo/pull/1"}
        ])

        with patch.object(pr, "_run", return_value=mock_result):
            prs = pr._list_open_prs()
            self.assertEqual(len(prs), 1)
            self.assertEqual(prs[0]["number"], 1)

    def test_list_open_prs_failure_exits(self):
        """Test that listing failure causes exit."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "gh: not authenticated"

        with patch.object(pr, "_run", return_value=mock_result):
            with self.assertRaises(SystemExit) as cm:
                pr._list_open_prs()
            self.assertEqual(cm.exception.code, 1)


class TestOwnerRepo(unittest.TestCase):
    """Test _owner_repo function."""

    def test_owner_repo_success(self):
        """Test successful owner/repo extraction."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "owner/repo\n"

        with patch.object(pr, "_run", return_value=mock_result):
            owner, repo = pr._owner_repo()
            self.assertEqual(owner, "owner")
            self.assertEqual(repo, "repo")

    def test_owner_repo_failure(self):
        """Test failure returns None, None."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch.object(pr, "_run", return_value=mock_result):
            owner, repo = pr._owner_repo()
            self.assertIsNone(owner)
            self.assertIsNone(repo)

    def test_owner_repo_malformed_output(self):
        """Test malformed output returns None, None."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "malformed\n"

        with patch.object(pr, "_run", return_value=mock_result):
            owner, repo = pr._owner_repo()
            # Should handle single part gracefully
            self.assertTrue(owner is None or repo is None)


class TestIsBot(unittest.TestCase):
    """Test _is_bot function."""

    def test_is_bot_known_bots(self):
        """Test recognition of known bot accounts."""
        self.assertTrue(pr._is_bot("coderabbitai"))
        self.assertTrue(pr._is_bot("coderabbitai[bot]"))
        self.assertTrue(pr._is_bot("github-actions[bot]"))
        self.assertTrue(pr._is_bot("dependabot[bot]"))

    def test_is_bot_human_accounts(self):
        """Test human accounts are not flagged as bots."""
        self.assertFalse(pr._is_bot("john"))
        self.assertFalse(pr._is_bot("alice"))

    def test_is_bot_generic_bot_pattern(self):
        """Test generic [bot] suffix detection."""
        self.assertTrue(pr._is_bot("random-bot[bot]"))
        self.assertFalse(pr._is_bot("notabot"))


class TestQuote(unittest.TestCase):
    """Test _quote function."""

    def test_quote_simple_text(self):
        """Test quoting simple text."""
        result = pr._quote("Hello world")
        self.assertEqual(result, "> Hello world")

    def test_quote_multiline_text(self):
        """Test quoting multiline text."""
        result = pr._quote("Line 1\nLine 2\nLine 3")
        expected = "> Line 1\n> Line 2\n> Line 3"
        self.assertEqual(result, expected)

    def test_quote_empty_text(self):
        """Test quoting empty text."""
        result = pr._quote("")
        self.assertEqual(result, "> (empty)")

    def test_quote_none_text(self):
        """Test quoting None."""
        result = pr._quote(None)
        self.assertEqual(result, "> (empty)")


class TestHasQuoteMatch(unittest.TestCase):
    """Test _has_quote_match function."""

    def test_has_quote_match_positive(self):
        """Test detecting quote match."""
        original = "This is the original comment text."
        reply = "> original comment\nHere is my reply."
        self.assertTrue(pr._has_quote_match(original, reply))

    def test_has_quote_match_negative(self):
        """Test no quote match."""
        original = "Original text here."
        reply = "Completely different reply."
        self.assertFalse(pr._has_quote_match(original, reply))

    def test_has_quote_match_empty_quote(self):
        """Test no match when no quotes in reply."""
        original = "Original text."
        reply = "No quotes here."
        self.assertFalse(pr._has_quote_match(original, reply))

    def test_has_quote_match_ignores_mentions(self):
        """Test that @ mentions in quotes are ignored."""
        original = "Check this code."
        reply = "> @user\nReply text."
        self.assertFalse(pr._has_quote_match(original, reply))


class TestDetectPrReplies(unittest.TestCase):
    """Test _detect_pr_replies function."""

    def test_detect_pr_replies_identifies_replied_comments(self):
        """Test identifying replied comments via quote matching."""
        comments = [
            {
                "author": {"login": "reviewer1"},
                "body": "What about edge case X?",
                "url": "http://comment1"
            },
            {
                "author": {"login": "pr_author"},
                "body": "> edge case X\nGood point, I'll fix it.",
                "url": "http://reply1"
            }
        ]

        replied = pr._detect_pr_replies(comments, "pr_author")
        self.assertIn("http://comment1", replied)

    def test_detect_pr_replies_ignores_bots(self):
        """Test that bot comments are filtered out."""
        comments = [
            {
                "author": {"login": "github-actions[bot]"},
                "body": "CI passed.",
                "url": "http://bot"
            },
            {
                "author": {"login": "user1"},
                "body": "LGTM",
                "url": "http://human"
            }
        ]

        replied = pr._detect_pr_replies(comments, "pr_author")
        # Bot comments should be filtered, so no replies detected
        self.assertEqual(len(replied), 0)


class TestFormatConversation(unittest.TestCase):
    """Test _format_conversation function."""

    def test_format_conversation_with_diff_hunk(self):
        """Test formatting conversation with code context."""
        comments = [
            {
                "author": {"login": "user1"},
                "createdAt": "2024-01-01T12:00:00Z",
                "body": "This looks wrong."
            }
        ]
        diff_hunk = "+ added line\n- removed line"

        result = pr._format_conversation(comments, diff_hunk)
        result_text = "\n".join(result)

        self.assertIn("```diff", result_text)
        self.assertIn("+ added line", result_text)
        self.assertIn("**@user1**", result_text)
        self.assertIn("This looks wrong.", result_text)

    def test_format_conversation_without_diff_hunk(self):
        """Test formatting conversation without code context."""
        comments = [
            {
                "author": {"login": "user1"},
                "createdAt": "2024-01-01T12:00:00Z",
                "body": "Question here."
            }
        ]

        result = pr._format_conversation(comments)
        result_text = "\n".join(result)

        self.assertNotIn("```diff", result_text)
        self.assertIn("**@user1**", result_text)

    def test_format_conversation_truncates_long_hunks(self):
        """Test that long diff hunks are truncated."""
        comments = [
            {
                "author": {"login": "user1"},
                "createdAt": "2024-01-01T12:00:00Z",
                "body": "Comment"
            }
        ]
        # Create a diff hunk with 20 lines
        diff_hunk = "\n".join([f"+ line {i}" for i in range(20)])

        result = pr._format_conversation(comments, diff_hunk)
        result_text = "\n".join(result)

        # Should include ellipsis for truncation
        self.assertIn("...", result_text)


class TestLoadDiffHunks(unittest.TestCase):
    """Test _load_diff_hunks function."""

    def test_load_diff_hunks_builds_lookup(self):
        """Test building URL to diff_hunk lookup."""
        with TemporaryDirectory() as tmpdir:
            pr_dir = Path(tmpdir)
            rc_file = pr_dir / "review_comments.json"
            rc_file.write_text(json.dumps([
                {
                    "html_url": "http://comment1",
                    "diff_hunk": "@@ -1,3 +1,4 @@\n line1"
                },
                {
                    "html_url": "http://comment2",
                    "diff_hunk": "@@ -5,2 +5,3 @@\n line5"
                }
            ]))

            hunks = pr._load_diff_hunks(str(pr_dir))
            self.assertEqual(len(hunks), 2)
            self.assertIn("http://comment1", hunks)
            self.assertIn("line1", hunks["http://comment1"])

    def test_load_diff_hunks_returns_empty_when_no_file(self):
        """Test returns empty dict when file doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            hunks = pr._load_diff_hunks(str(tmpdir))
            self.assertEqual(hunks, {})


class TestLoadReviewThreads(unittest.TestCase):
    """Test _load_review_threads function."""

    def test_load_review_threads_success(self):
        """Test loading review threads from GraphQL data."""
        with TemporaryDirectory() as tmpdir:
            pr_dir = Path(tmpdir)
            threads_file = pr_dir / "review_threads.json"
            threads_data = {
                "data": {
                    "repository": {
                        "pullRequest": {
                            "reviewThreads": {
                                "nodes": [
                                    {"id": "thread1", "isResolved": False},
                                    {"id": "thread2", "isResolved": True}
                                ]
                            }
                        }
                    }
                }
            }
            threads_file.write_text(json.dumps(threads_data))

            threads = pr._load_review_threads(str(pr_dir))
            self.assertEqual(len(threads), 2)
            self.assertEqual(threads[0]["id"], "thread1")

    def test_load_review_threads_returns_empty_when_no_file(self):
        """Test returns empty list when file doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            threads = pr._load_review_threads(str(tmpdir))
            self.assertEqual(threads, [])

    def test_load_review_threads_handles_malformed_data(self):
        """Test handles malformed JSON structure."""
        with TemporaryDirectory() as tmpdir:
            pr_dir = Path(tmpdir)
            threads_file = pr_dir / "review_threads.json"
            threads_file.write_text(json.dumps({"data": {}}))

            threads = pr._load_review_threads(str(pr_dir))
            self.assertEqual(threads, [])


class TestReviewerTable(unittest.TestCase):
    """Test _reviewer_table function."""

    def test_reviewer_table_deduplicates_reviewers(self):
        """Test that latest review state wins for each reviewer."""
        meta = {
            "author": {"login": "pr_author"},
            "reviews": [
                {"author": {"login": "reviewer1"}, "state": "COMMENTED"},
                {"author": {"login": "reviewer1"}, "state": "APPROVED"}
            ],
            "reviewRequests": []
        }

        reviewers = pr._reviewer_table(meta)
        self.assertEqual(reviewers["reviewer1"], "APPROVED")

    def test_reviewer_table_excludes_pr_author(self):
        """Test that PR author's reviews are excluded."""
        meta = {
            "author": {"login": "pr_author"},
            "reviews": [
                {"author": {"login": "pr_author"}, "state": "COMMENTED"}
            ],
            "reviewRequests": []
        }

        reviewers = pr._reviewer_table(meta)
        self.assertNotIn("pr_author", reviewers)

    def test_reviewer_table_includes_pending_requests(self):
        """Test that pending review requests are included."""
        meta = {
            "author": {"login": "pr_author"},
            "reviews": [],
            "reviewRequests": [
                {"login": "reviewer2"}
            ]
        }

        reviewers = pr._reviewer_table(meta)
        self.assertEqual(reviewers["reviewer2"], "PENDING")

    def test_reviewer_table_pending_not_overriding_existing(self):
        """Test that pending request doesn't override existing review."""
        meta = {
            "author": {"login": "pr_author"},
            "reviews": [
                {"author": {"login": "reviewer1"}, "state": "APPROVED"}
            ],
            "reviewRequests": [
                {"login": "reviewer1"}
            ]
        }

        reviewers = pr._reviewer_table(meta)
        self.assertEqual(reviewers["reviewer1"], "APPROVED")


class TestCiSummary(unittest.TestCase):
    """Test _ci_summary function."""

    def test_ci_summary_empty_checks(self):
        """Test summary with no CI checks."""
        meta = {"statusCheckRollup": []}
        summary = pr._ci_summary(meta)
        self.assertEqual(summary, "—")

    def test_ci_summary_with_various_states(self):
        """Test summary with mixed CI states."""
        meta = {
            "statusCheckRollup": [
                {"conclusion": "SUCCESS"},
                {"conclusion": "SUCCESS"},
                {"state": "FAILURE"},
                {"status": "PENDING"}
            ]
        }

        summary = pr._ci_summary(meta)
        self.assertIn("SUCCESS: 2", summary)
        self.assertIn("FAILURE: 1", summary)
        self.assertIn("PENDING: 1", summary)


class TestFetch(unittest.TestCase):
    """Test fetch function."""

    def test_fetch_creates_pr_directory(self):
        """Test that fetch creates PR directory structure."""
        with TemporaryDirectory() as tmpdir:
            with patch.object(pr, "PRS_DIR", tmpdir):
                with patch.object(pr, "ROOT", tmpdir):
                    # Mock all gh commands
                    mock_meta = Mock(returncode=0, stdout=json.dumps({"number": 123}))
                    mock_diff = Mock(returncode=0, stdout="diff content")
                    mock_comments = Mock(returncode=0, stdout=json.dumps([]))

                    with patch.object(pr, "_run", side_effect=[mock_meta, mock_diff, mock_comments]):
                        with patch.object(pr, "_owner_repo", return_value=(None, None)):
                            pr.fetch("123")

                    pr_dir = Path(tmpdir) / "123"
                    self.assertTrue(pr_dir.exists())
                    self.assertTrue((pr_dir / "meta.json").exists())
                    self.assertTrue((pr_dir / "diff.patch").exists())

    def test_fetch_handles_meta_failure(self):
        """Test fetch exits on metadata fetch failure."""
        with TemporaryDirectory() as tmpdir:
            with patch.object(pr, "PRS_DIR", tmpdir):
                mock_result = Mock(returncode=1, stderr="Not found")

                with patch.object(pr, "_run", return_value=mock_result):
                    with self.assertRaises(SystemExit):
                        pr.fetch("999")


class TestReorder(unittest.TestCase):
    """Test reorder function."""

    def test_reorder_exits_when_no_report(self):
        """Test reorder exits when status report doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            with patch.object(pr, "PRS_DIR", tmpdir):
                with self.assertRaises(SystemExit) as cm:
                    pr.reorder("123")
                self.assertEqual(cm.exception.code, 1)

    def test_reorder_sorts_by_severity(self):
        """Test that reorder sorts comments by severity."""
        with TemporaryDirectory() as tmpdir:
            pr_dir = Path(tmpdir) / "123"
            pr_dir.mkdir()
            report_file = pr_dir / "status.md"

            # Create report with comments in wrong order
            report_content = """# PR #123

## Unreplied Code Comments

### [file1:10](url1)
- **Severity**: LOW

---

### [file2:20](url2)
- **Severity**: CRITICAL

---

## Unreplied PR Comments

None.

## Suspicious Resolutions
"""
            report_file.write_text(report_content)

            with patch.object(pr, "PRS_DIR", tmpdir):
                pr.reorder("123")

            # Read reordered content
            reordered = report_file.read_text()

            # CRITICAL should come before LOW
            critical_pos = reordered.find("CRITICAL")
            low_pos = reordered.find("LOW")
            self.assertLess(critical_pos, low_pos)


class TestMain(unittest.TestCase):
    """Test main function."""

    def test_main_no_args_exits(self):
        """Test main exits with error when no command provided."""
        with patch("sys.argv", ["pr.py"]):
            with self.assertRaises(SystemExit) as cm:
                pr.main()
            self.assertEqual(cm.exception.code, 1)

    def test_main_unknown_command_exits(self):
        """Test main exits with error on unknown command."""
        with patch("sys.argv", ["pr.py", "unknown"]):
            with self.assertRaises(SystemExit) as cm:
                pr.main()
            self.assertEqual(cm.exception.code, 1)

    def test_main_list_command(self):
        """Test main handles list command."""
        mock_prs = [
            {"number": 1, "author": {"login": "user1"}, "title": "Test PR"}
        ]

        with patch("sys.argv", ["pr.py", "list"]):
            with patch.object(pr, "_list_open_prs", return_value=mock_prs):
                with patch.object(pr, "_load_exclude_list", return_value=set()):
                    # Should not raise
                    pr.main()

    def test_main_fetch_command_without_pr_number(self):
        """Test main exits when fetch called without PR number."""
        with patch("sys.argv", ["pr.py", "fetch"]):
            with self.assertRaises(SystemExit) as cm:
                pr.main()
            self.assertEqual(cm.exception.code, 1)

    def test_main_status_command_without_pr_number(self):
        """Test main exits when status called without PR number."""
        with patch("sys.argv", ["pr.py", "status"]):
            with self.assertRaises(SystemExit) as cm:
                pr.main()
            self.assertEqual(cm.exception.code, 1)

    def test_main_reorder_command_without_pr_number(self):
        """Test main exits when reorder called without PR number."""
        with patch("sys.argv", ["pr.py", "reorder"]):
            with self.assertRaises(SystemExit) as cm:
                pr.main()
            self.assertEqual(cm.exception.code, 1)


class TestRun(unittest.TestCase):
    """Test _run function."""

    def test_run_captures_output(self):
        """Test that _run captures command output."""
        result = pr._run(["echo", "hello"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("hello", result.stdout)

    def test_run_with_check_exits_on_failure(self):
        """Test that check=True raises CalledProcessError on failure."""
        # subprocess.run with check=True raises CalledProcessError
        from subprocess import CalledProcessError
        with self.assertRaises(CalledProcessError):
            pr._run(["python3", "-c", "import sys; sys.exit(1)"], check=True)

    def test_run_uses_correct_cwd(self):
        """Test that _run uses ROOT as cwd."""
        with TemporaryDirectory() as tmpdir:
            with patch.object(pr, "ROOT", tmpdir):
                # Create a test file in tmpdir
                test_file = Path(tmpdir) / "test.txt"
                test_file.write_text("test")

                result = pr._run(["ls", "test.txt"])
                self.assertEqual(result.returncode, 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_empty_comment_body_handling(self):
        """Test handling of None/empty comment bodies."""
        quoted = pr._quote(None)
        self.assertIn("empty", quoted)

    def test_missing_author_in_comment(self):
        """Test handling missing author field."""
        comments = [{"body": "text", "url": "http://x"}]
        # Should not crash
        replied = pr._detect_pr_replies(comments, "author")
        self.assertIsInstance(replied, set)

    def test_malformed_review_thread_comments(self):
        """Test handling malformed thread structure."""
        with TemporaryDirectory() as tmpdir:
            pr_dir = Path(tmpdir)
            threads_file = pr_dir / "review_threads.json"
            # Missing expected nested structure
            threads_file.write_text(json.dumps({"nodes": []}))

            threads = pr._load_review_threads(str(pr_dir))
            # Should return empty list, not crash
            self.assertEqual(threads, [])

    def test_diff_hunk_with_missing_fields(self):
        """Test diff hunk loading with missing URL or hunk."""
        with TemporaryDirectory() as tmpdir:
            pr_dir = Path(tmpdir)
            rc_file = pr_dir / "review_comments.json"
            rc_file.write_text(json.dumps([
                {"html_url": "http://url1"},  # Missing diff_hunk
                {"diff_hunk": "hunk"},  # Missing html_url
                {}  # Missing both
            ]))

            hunks = pr._load_diff_hunks(str(pr_dir))
            # Should handle gracefully
            self.assertEqual(len(hunks), 0)


class TestStatusIntegration(unittest.TestCase):
    """Integration tests for status function."""

    def test_status_generates_complete_report(self):
        """Test that status generates all expected sections."""
        with TemporaryDirectory() as tmpdir:
            pr_dir = Path(tmpdir) / "123"
            pr_dir.mkdir()

            # Create minimal meta.json
            meta_file = pr_dir / "meta.json"
            meta_data = {
                "number": 123,
                "title": "Test PR",
                "author": {"login": "author1"},
                "state": "OPEN",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-02T00:00:00Z",
                "url": "http://pr",
                "reviews": [],
                "reviewRequests": [],
                "comments": [],
                "statusCheckRollup": []
            }
            meta_file.write_text(json.dumps(meta_data))

            with patch.object(pr, "PRS_DIR", tmpdir):
                with patch.object(pr, "ROOT", tmpdir):
                    with patch.object(pr, "fetch"):  # Mock fetch call
                        pr.status("123")

            # Check report was created
            report_file = pr_dir / "status.md"
            self.assertTrue(report_file.exists())

            report_content = report_file.read_text()
            # Check for expected sections
            self.assertIn("# PR #123", report_content)
            # PR Description is optional (only shown when body is non-empty)
            self.assertIn("## Reviewers", report_content)
            self.assertIn("## Action Items", report_content)
            self.assertIn("## Unreplied Code Comments", report_content)
            self.assertIn("## Unreplied PR Comments", report_content)
            self.assertIn("## Suspicious Resolutions", report_content)
            self.assertIn("## Resolved Comments (Audit Required)", report_content)


class TestRegressionAndBoundary(unittest.TestCase):
    """Additional regression and boundary tests for enhanced coverage."""

    def test_fetch_with_review_threads_but_no_owner_repo(self):
        """Test fetch continues gracefully when GraphQL threads can't be fetched."""
        with TemporaryDirectory() as tmpdir:
            with patch.object(pr, "PRS_DIR", tmpdir):
                with patch.object(pr, "ROOT", tmpdir):
                    mock_meta = Mock(returncode=0, stdout=json.dumps({"number": 456}))
                    mock_diff = Mock(returncode=0, stdout="diff")
                    mock_comments = Mock(returncode=0, stdout=json.dumps([]))

                    with patch.object(pr, "_run", side_effect=[mock_meta, mock_diff, mock_comments]):
                        with patch.object(pr, "_owner_repo", return_value=(None, None)):
                            pr.fetch("456")

                    # Should complete without error
                    pr_dir = Path(tmpdir) / "456"
                    self.assertTrue(pr_dir.exists())
                    # Threads file should not be created
                    self.assertFalse((pr_dir / "review_threads.json").exists())

    def test_status_with_pr_author_reviews_filtered_out(self):
        """Regression test: PR author's own reviews should not appear in reviewer table."""
        with TemporaryDirectory() as tmpdir:
            pr_dir = Path(tmpdir) / "789"
            pr_dir.mkdir()

            meta_file = pr_dir / "meta.json"
            meta_data = {
                "number": 789,
                "title": "Self Review PR",
                "author": {"login": "self_reviewer"},
                "state": "OPEN",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-02T00:00:00Z",
                "url": "http://pr789",
                "reviews": [
                    {"author": {"login": "self_reviewer"}, "state": "APPROVED"}
                ],
                "reviewRequests": [],
                "comments": [],
                "statusCheckRollup": []
            }
            meta_file.write_text(json.dumps(meta_data))

            with patch.object(pr, "PRS_DIR", tmpdir):
                with patch.object(pr, "ROOT", tmpdir):
                    with patch.object(pr, "fetch"):
                        pr.status("789")

            report_file = pr_dir / "status.md"
            report_content = report_file.read_text()
            # Should say "No reviewers assigned" since PR author is filtered
            self.assertIn("No reviewers assigned", report_content)

    def test_quote_preserves_whitespace_in_lines(self):
        """Boundary test: ensure quote preserves leading/trailing spaces in lines."""
        text = "  indented line  \n\tnext line\t"
        result = pr._quote(text)
        # Each line should have "> " prefix but preserve original spacing
        lines = result.split("\n")
        self.assertTrue(lines[0].startswith(">"))
        self.assertIn("indented", lines[0])

    def test_reorder_handles_report_with_no_severity_markers(self):
        """Boundary test: reorder should handle reports without severity markers."""
        with TemporaryDirectory() as tmpdir:
            pr_dir = Path(tmpdir) / "999"
            pr_dir.mkdir()
            report_file = pr_dir / "status.md"

            # Report with no severity markers
            report_content = """# PR #999

## Unreplied Code Comments

### [file:10](url)
No severity here.

---

## Unreplied PR Comments

None.
"""
            report_file.write_text(report_content)

            with patch.object(pr, "PRS_DIR", tmpdir):
                # Should not crash
                pr.reorder("999")

            # File should still exist
            self.assertTrue(report_file.exists())

    def test_format_conversation_handles_missing_author_gracefully(self):
        """Boundary test: format conversation with malformed comment structure."""
        comments = [
            {"createdAt": "2024-01-01T00:00:00Z", "body": "Comment without author"}
        ]

        result = pr._format_conversation(comments)
        result_text = "\n".join(result)

        # Should handle missing author field gracefully
        self.assertIn("**@?**", result_text)  # Default to "?"

    def test_ci_summary_handles_unknown_states(self):
        """Boundary test: CI summary with unrecognized state values."""
        meta = {
            "statusCheckRollup": [
                {"conclusion": "UNKNOWN_STATE"},
                {"state": "WEIRD_VALUE"}
            ]
        }

        summary = pr._ci_summary(meta)
        # Should not crash and return some summary
        self.assertIsInstance(summary, str)
        self.assertTrue(len(summary) > 0)

    def test_main_fetch_all_respects_exclude_list(self):
        """Regression test: fetch ALL should skip excluded PRs."""
        mock_prs = [
            {"number": 1, "title": "PR 1"},
            {"number": 2, "title": "PR 2"},
            {"number": 3, "title": "PR 3"}
        ]

        with patch("sys.argv", ["pr.py", "fetch", "ALL"]):
            with patch.object(pr, "_list_open_prs", return_value=mock_prs):
                with patch.object(pr, "_load_exclude_list", return_value={"2"}):
                    with patch.object(pr, "fetch") as mock_fetch:
                        pr.main()

                        # Should have called fetch for 1 and 3, but not 2
                        calls = [call("1"), call("3")]
                        mock_fetch.assert_has_calls(calls, any_order=True)
                        # Verify 2 was not fetched
                        self.assertNotIn(call("2"), mock_fetch.call_args_list)

    def test_has_quote_match_case_insensitive(self):
        """Boundary test: quote matching should be case-insensitive."""
        original = "Check THE CODE here."
        reply = "> the code\nFixed."
        self.assertTrue(pr._has_quote_match(original, reply))

    def test_load_exclude_list_handles_empty_lines_and_comments(self):
        """Boundary test: exclude list parsing handles empty lines and comments."""
        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text(
                "exclude_prs:\n"
                "  # This is a comment\n"
                "  - 100\n"
                "  \n"  # Empty line
                "  - 200\n"
                "  # Another comment\n"
            )

            with patch.object(pr, "CONFIG_PATH", str(config_file)):
                excludes = pr._load_exclude_list()
                self.assertEqual(excludes, {"100", "200"})

    def test_reviewer_table_handles_team_review_requests(self):
        """Boundary test: team review requests (no login, only name)."""
        meta = {
            "author": {"login": "author"},
            "reviews": [],
            "reviewRequests": [
                {"login": "user1"},  # User request
                {"name": "team-reviewers"}  # Team request (no login)
            ]
        }

        reviewers = pr._reviewer_table(meta)
        self.assertIn("user1", reviewers)
        self.assertIn("team-reviewers", reviewers)


if __name__ == "__main__":
    unittest.main()