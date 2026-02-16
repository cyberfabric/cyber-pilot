"""
Test language configuration loading and dynamic regex building.

Validates that language_config module correctly:
- Loads configuration from .cypilot-config.json
- Falls back to defaults when config missing
- Builds correct regex patterns for different comment styles
"""

import unittest
import sys
import json
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.utils import (
    load_language_config,
    build_cypilot_begin_regex,
    build_cypilot_end_regex,
    build_no_cypilot_begin_regex,
    build_no_cypilot_end_regex,
    LanguageConfig,
    DEFAULT_FILE_EXTENSIONS,
)

from cypilot.utils.language_config import (
    DEFAULT_SINGLE_LINE_COMMENTS,
    DEFAULT_MULTI_LINE_COMMENTS,
    DEFAULT_BLOCK_COMMENT_PREFIXES,
)


class TestLanguageConfigLoading(unittest.TestCase):
    """Test language configuration loading from .cypilot-config.json."""

    def test_default_config_when_no_project_config(self):
        """Verify default config is used when no .cypilot-config.json exists."""
        with TemporaryDirectory() as tmpdir:
            config = load_language_config(Path(tmpdir))
            
            # Should have default extensions
            self.assertEqual(config.file_extensions, DEFAULT_FILE_EXTENSIONS)
            self.assertIn(".py", config.file_extensions)
            self.assertIn(".js", config.file_extensions)
            self.assertIn(".rs", config.file_extensions)
            
            # Should have default comment styles
            self.assertIn("#", config.single_line_comments)
            self.assertIn("//", config.single_line_comments)
            self.assertIn("--", config.single_line_comments)

    def test_custom_config_overrides_defaults(self):
        """Verify custom config from .cypilot-config.json overrides defaults."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Write custom config
            config_file = tmppath / ".cypilot-config.json"
            config_file.write_text(json.dumps({
                "cypilotAdapterPath": "adapter",
                "codeScanning": {
                    "fileExtensions": [".php", ".rb"],
                    "singleLineComments": ["#", "//"],
                    "multiLineComments": [
                        {"start": "/*", "end": "*/"}
                    ],
                    "blockCommentPrefixes": ["*"]
                }
            }))
            
            config = load_language_config(tmppath)
            
            # Should use custom extensions
            self.assertEqual(config.file_extensions, {".php", ".rb"})
            self.assertNotIn(".py", config.file_extensions)
            
            # Should use custom comments
            self.assertEqual(config.single_line_comments, ["#", "//"])

    def test_partial_config_falls_back_to_defaults(self):
        """Verify partial config uses defaults for missing fields."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Write config with only fileExtensions
            config_file = tmppath / ".cypilot-config.json"
            config_file.write_text(json.dumps({
                "cypilotAdapterPath": "adapter",
                "codeScanning": {
                    "fileExtensions": [".kt", ".swift"]
                }
            }))
            
            config = load_language_config(tmppath)
            
            # Should use custom extensions
            self.assertEqual(config.file_extensions, {".kt", ".swift"})
            
            # Should fall back to defaults for comments
            self.assertIn("#", config.single_line_comments)
            self.assertIn("//", config.single_line_comments)

    def test_invalid_code_scanning_type_falls_back_to_defaults(self):
        """Cover: codeScanning exists but is not a dict."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / ".cypilot-config.json").write_text(
                json.dumps({
                    "cypilotAdapterPath": "adapter",
                    "codeScanning": "not-a-dict",
                })
            )

            config = load_language_config(tmppath)
            self.assertEqual(config.file_extensions, DEFAULT_FILE_EXTENSIONS)
            self.assertEqual(config.single_line_comments, DEFAULT_SINGLE_LINE_COMMENTS)

    def test_invalid_scanning_field_types_fall_back_to_defaults(self):
        """Cover: wrong types inside codeScanning for list-like fields."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / ".cypilot-config.json").write_text(
                json.dumps({
                    "cypilotAdapterPath": "adapter",
                    "codeScanning": {
                        "fileExtensions": "not-a-list",
                        "singleLineComments": "not-a-list",
                        "multiLineComments": {"start": "/*", "end": "*/"},
                        "blockCommentPrefixes": 123,
                    },
                })
            )

            config = load_language_config(tmppath)
            self.assertEqual(config.file_extensions, DEFAULT_FILE_EXTENSIONS)
            self.assertEqual(config.single_line_comments, DEFAULT_SINGLE_LINE_COMMENTS)
            self.assertEqual(config.multi_line_comments, DEFAULT_MULTI_LINE_COMMENTS)
            self.assertEqual(config.block_comment_prefixes, DEFAULT_BLOCK_COMMENT_PREFIXES)


class TestRegexPatternBuilding(unittest.TestCase):
    """Test dynamic regex pattern building from language config."""

    def test_cypilot_begin_regex_matches_python_style(self):
        """Verify cpt-begin regex matches Python # comments."""
        config = LanguageConfig(
            file_extensions={".py"},
            single_line_comments=["#"],
            multi_line_comments=[],
            block_comment_prefixes=[]
        )
        
        regex = build_cypilot_begin_regex(config)
        
        # Should match Python comment
        self.assertIsNotNone(regex.match("# cpt-begin cpt-test-feature-x-flow-y:p1:inst-step"))
        self.assertIsNotNone(regex.match("  # cpt-begin cpt-test-feature-x-flow-y:p1:inst-step"))
        
        # Should extract tag
        match = regex.match("# cpt-begin cpt-test-feature-x-flow-y:p1:inst-step")
        self.assertEqual(match.group(1), "cpt-test-feature-x-flow-y:p1:inst-step")

    def test_cypilot_begin_regex_matches_javascript_style(self):
        """Verify cpt-begin regex matches JavaScript // comments."""
        config = LanguageConfig(
            file_extensions={".js"},
            single_line_comments=["//"],
            multi_line_comments=[],
            block_comment_prefixes=[]
        )
        
        regex = build_cypilot_begin_regex(config)
        
        # Should match JS comment
        self.assertIsNotNone(regex.match("// cpt-begin cpt-test-feature-x-flow-y:p1:inst-step"))
        self.assertIsNotNone(regex.match("  // cpt-begin cpt-test-feature-x-flow-y:p1:inst-step"))

    def test_cypilot_begin_regex_matches_sql_style(self):
        """Verify cpt-begin regex matches SQL -- comments."""
        config = LanguageConfig(
            file_extensions={".sql"},
            single_line_comments=["--"],
            multi_line_comments=[],
            block_comment_prefixes=[]
        )
        
        regex = build_cypilot_begin_regex(config)
        
        # Should match SQL comment
        self.assertIsNotNone(regex.match("-- cpt-begin cpt-test-feature-x-flow-y:p1:inst-step"))

    def test_cypilot_begin_regex_matches_html_comment(self):
        """Verify cpt-begin regex matches HTML <!-- comments."""
        config = LanguageConfig(
            file_extensions={".html"},
            single_line_comments=[],
            multi_line_comments=[{"start": "<!--", "end": "-->"}],
            block_comment_prefixes=[]
        )
        
        regex = build_cypilot_begin_regex(config)
        
        # Should match HTML comment
        self.assertIsNotNone(regex.match("<!-- cpt-begin cpt-test-feature-x-flow-y:p1:inst-step"))

    def test_cypilot_begin_regex_matches_multiple_styles(self):
        """Verify cpt-begin regex matches multiple comment styles."""
        config = LanguageConfig(
            file_extensions={".py", ".js", ".sql"},
            single_line_comments=["#", "//", "--"],
            multi_line_comments=[{"start": "/*", "end": "*/"}],
            block_comment_prefixes=["*"]
        )
        
        regex = build_cypilot_begin_regex(config)
        
        # Should match all styles
        self.assertIsNotNone(regex.match("# cpt-begin cpt-test-feature-x-flow-y:p1:inst-step"))
        self.assertIsNotNone(regex.match("// cpt-begin cpt-test-feature-x-flow-y:p1:inst-step"))
        self.assertIsNotNone(regex.match("-- cpt-begin cpt-test-feature-x-flow-y:p1:inst-step"))
        self.assertIsNotNone(regex.match("/* cpt-begin cpt-test-feature-x-flow-y:p1:inst-step"))
        self.assertIsNotNone(regex.match("* cpt-begin cpt-test-feature-x-flow-y:p1:inst-step"))

    def test_cypilot_end_regex_matches_same_styles_as_begin(self):
        """Verify cpt-end regex matches same styles as cpt-begin."""
        config = LanguageConfig(
            file_extensions={".py", ".js"},
            single_line_comments=["#", "//"],
            multi_line_comments=[],
            block_comment_prefixes=[]
        )
        
        end_regex = build_cypilot_end_regex(config)
        
        # Should match both styles
        self.assertIsNotNone(end_regex.match("# cpt-end cpt-test-feature-x-flow-y:p1:inst-step"))
        self.assertIsNotNone(end_regex.match("// cpt-end cpt-test-feature-x-flow-y:p1:inst-step"))

    def test_no_cypilot_begin_regex_matches_exclusion_marker(self):
        """Verify !no-cpt-begin regex matches exclusion markers."""
        config = LanguageConfig(
            file_extensions={".py"},
            single_line_comments=["#"],
            multi_line_comments=[{"start": "<!--", "end": "-->"}],
            block_comment_prefixes=[]
        )
        
        regex = build_no_cypilot_begin_regex(config)
        
        # Should match exclusion markers
        self.assertIsNotNone(regex.match("# !no-cpt-begin"))
        self.assertIsNotNone(regex.match("# Some text !no-cpt-begin"))
        self.assertIsNotNone(regex.match("<!-- !no-cpt-begin -->"))

    def test_no_cypilot_end_regex_matches_exclusion_marker(self):
        """Verify !no-cpt-end regex matches exclusion end markers."""
        config = LanguageConfig(
            file_extensions={".py"},
            single_line_comments=["#"],
            multi_line_comments=[{"start": "<!--", "end": "-->"}],
            block_comment_prefixes=[]
        )
        
        regex = build_no_cypilot_end_regex(config)
        
        # Should match exclusion end markers
        self.assertIsNotNone(regex.match("# !no-cpt-end"))
        self.assertIsNotNone(regex.match("<!-- !no-cpt-end -->"))


class TestCommentPatternBuilding(unittest.TestCase):
    """Test comment pattern building for regex."""

    def test_build_comment_pattern_escapes_special_chars(self):
        """Verify special regex characters are properly escaped."""
        config = LanguageConfig(
            file_extensions={".py"},
            single_line_comments=["#", "//"],
            multi_line_comments=[{"start": "/*", "end": "*/"}],
            block_comment_prefixes=["*"]
        )
        
        pattern = config.build_comment_pattern()
        
        # Should contain escaped versions
        self.assertIn(r"\#", pattern)
        self.assertIn(r"//", pattern)
        self.assertIn(r"/\*", pattern)
        self.assertIn(r"\*", pattern)
        
        # Should be wrapped in non-capturing group
        self.assertTrue(pattern.startswith("(?:"))
        self.assertTrue(pattern.endswith(")"))

    def test_build_comment_pattern_includes_all_prefixes(self):
        """Verify all comment prefixes are included in pattern."""
        config = LanguageConfig(
            file_extensions={".py"},
            single_line_comments=["#", "//", "--"],
            multi_line_comments=[{"start": "<!--", "end": "-->"}],
            block_comment_prefixes=["*"]
        )
        
        pattern = config.build_comment_pattern()
        
        # Should include all single-line styles (some escaped)
        self.assertIn("#", pattern)
        self.assertIn("//", pattern)
        self.assertIn("\\-\\-", pattern)  # -- gets escaped to \-\-
        
        # Should include multi-line start markers (escaped)
        self.assertIn("<!\\-\\-", pattern)  # <!-- gets escaped
        
        # Should include block prefixes
        self.assertIn("*", pattern)


if __name__ == "__main__":
    unittest.main()
