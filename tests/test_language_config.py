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
    """Test language configuration loading from project config (core.toml)."""

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

    def _write_project_config(self, root: Path, core_toml_content: str) -> None:
        """Helper to set up AGENTS.md TOML block + config/core.toml."""
        (root / "AGENTS.md").write_text(
            '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "adapter"\n```\n',
            encoding="utf-8",
        )
        config_dir = root / "adapter" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "core.toml").write_text(core_toml_content, encoding="utf-8")

    def test_custom_config_overrides_defaults(self):
        """Verify custom config from core.toml overrides defaults."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Write custom config via TOML
            self._write_project_config(tmppath, '''
[code_scanning]
fileExtensions = [".php", ".rb"]
singleLineComments = ["#", "//"]
blockCommentPrefixes = ["*"]

[[code_scanning.multiLineComments]]
start = "/*"
end = "*/"
''')
            
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
            self._write_project_config(tmppath, '''
[code_scanning]
fileExtensions = [".kt", ".swift"]
''')
            
            config = load_language_config(tmppath)
            
            # Should use custom extensions
            self.assertEqual(config.file_extensions, {".kt", ".swift"})
            
            # Should fall back to defaults for comments
            self.assertIn("#", config.single_line_comments)
            self.assertIn("//", config.single_line_comments)

    def test_invalid_code_scanning_type_falls_back_to_defaults(self):
        """Cover: code_scanning exists but is not a dict (string in TOML is fine, just not useful)."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            self._write_project_config(tmppath, 'code_scanning = "not-a-dict"\n')

            config = load_language_config(tmppath)
            self.assertEqual(config.file_extensions, DEFAULT_FILE_EXTENSIONS)
            self.assertEqual(config.single_line_comments, DEFAULT_SINGLE_LINE_COMMENTS)

    def test_invalid_scanning_field_types_fall_back_to_defaults(self):
        """Cover: wrong types inside code_scanning for list-like fields."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            self._write_project_config(tmppath, '''
[code_scanning]
fileExtensions = "not-a-list"
singleLineComments = "not-a-list"
blockCommentPrefixes = 123

[code_scanning.multiLineComments]
start = "/*"
end = "*/"
''')

            config = load_language_config(tmppath)
            self.assertEqual(config.file_extensions, DEFAULT_FILE_EXTENSIONS)
            self.assertEqual(config.single_line_comments, DEFAULT_SINGLE_LINE_COMMENTS)
            # Note: in TOML, multiLineComments as a table is a dict, not a list
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


class TestCodebaseEntryCommentFields(unittest.TestCase):
    """Test CodebaseEntry parsing of singleLineComments / multiLineComments."""

    def test_from_dict_with_comment_fields(self):
        from cypilot.utils.artifacts_meta import CodebaseEntry

        entry = CodebaseEntry.from_dict({
            "path": "src",
            "extensions": [".py"],
            "singleLineComments": ["#"],
            "multiLineComments": [{"start": '"""', "end": '"""'}],
        })
        self.assertEqual(entry.single_line_comments, ["#"])
        self.assertEqual(entry.multi_line_comments, [{"start": '"""', "end": '"""'}])

    def test_from_dict_without_comment_fields(self):
        from cypilot.utils.artifacts_meta import CodebaseEntry

        entry = CodebaseEntry.from_dict({
            "path": "src",
            "extensions": [".ts"],
        })
        self.assertIsNone(entry.single_line_comments)
        self.assertIsNone(entry.multi_line_comments)

    def test_from_dict_empty_comment_lists(self):
        from cypilot.utils.artifacts_meta import CodebaseEntry

        entry = CodebaseEntry.from_dict({
            "path": "src",
            "extensions": [".css"],
            "singleLineComments": [],
            "multiLineComments": [],
        })
        # Explicit empty list = "no comments of this type" (valid override, not None)
        self.assertEqual(entry.single_line_comments, [])
        self.assertIsNone(entry.multi_line_comments)  # empty after filtering invalid items

    def test_from_dict_malformed_multiline_ignored(self):
        from cypilot.utils.artifacts_meta import CodebaseEntry

        entry = CodebaseEntry.from_dict({
            "path": "src",
            "extensions": [".py"],
            "multiLineComments": [{"start": "/*"}],  # missing 'end'
        })
        self.assertIsNone(entry.multi_line_comments)


class TestCommentDefaultsForExtensions(unittest.TestCase):
    """Test comment_defaults_for_extensions() utility."""

    def test_python_defaults(self):
        from cypilot.utils.language_config import comment_defaults_for_extensions

        slc, mlc = comment_defaults_for_extensions([".py"])
        self.assertEqual(slc, ["#"])
        self.assertEqual(mlc, [{"start": '"""', "end": '"""'}])

    def test_js_defaults(self):
        from cypilot.utils.language_config import comment_defaults_for_extensions

        slc, mlc = comment_defaults_for_extensions([".js"])
        self.assertEqual(slc, ["//"])
        self.assertEqual(mlc, [{"start": "/*", "end": "*/"}])

    def test_mixed_extensions_deduplicates(self):
        from cypilot.utils.language_config import comment_defaults_for_extensions

        slc, mlc = comment_defaults_for_extensions([".ts", ".tsx"])
        self.assertEqual(slc, ["//"])  # deduplicated
        self.assertEqual(len(mlc), 1)  # deduplicated

    def test_unknown_extension_returns_empty(self):
        from cypilot.utils.language_config import comment_defaults_for_extensions

        slc, mlc = comment_defaults_for_extensions([".xyz"])
        self.assertEqual(slc, [])
        self.assertEqual(mlc, [])


if __name__ == "__main__":
    unittest.main()
