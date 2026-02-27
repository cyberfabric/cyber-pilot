"""
Cypilot Validator - Language Configuration

Load and provide language-specific settings from project config.
Supports dynamic file extensions and comment patterns for any language.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .files import find_project_root, load_project_config


# Default configuration (fallback if no project config)
DEFAULT_FILE_EXTENSIONS = {".py", ".md", ".js", ".ts", ".tsx", ".go", ".rs", ".java", ".cs", ".sql"}
DEFAULT_SINGLE_LINE_COMMENTS = ["#", "//", "--"]
DEFAULT_MULTI_LINE_COMMENTS = [
    {"start": "/*", "end": "*/"},
    {"start": "<!--", "end": "-->"},
]
DEFAULT_BLOCK_COMMENT_PREFIXES = ["*"]

# Extension-based comment format defaults.
# Each entry: (single_line_comments, multi_line_comments, block_comment_prefixes)
EXTENSION_COMMENT_DEFAULTS: Dict[str, Tuple[List[str], List[Dict[str, str]], List[str]]] = {
    ".py":   (["#"],        [{'start': '"""', 'end': '"""'}], []),
    ".pyi":  (["#"],        [{'start': '"""', 'end': '"""'}], []),
    ".rb":   (["#"],        [{'start': '=begin', 'end': '=end'}], []),
    ".sh":   (["#"],        [],                               []),
    ".bash": (["#"],        [],                               []),
    ".zsh":  (["#"],        [],                               []),
    ".yml":  (["#"],        [],                               []),
    ".yaml": (["#"],        [],                               []),
    ".toml": (["#"],        [],                               []),
    ".r":    (["#"],        [],                               []),
    ".pl":   (["#"],        [{'start': '=pod', 'end': '=cut'}], []),
    ".js":   (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".jsx":  (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".ts":   (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".tsx":  (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".mjs":  (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".mts":  (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".go":   (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".rs":   (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".java": (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".kt":   (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".kts":  (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".scala":(["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".c":    (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".h":    (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".cpp":  (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".hpp":  (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".cs":   (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".swift":(["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".dart": (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".php":  (["//", "#"],  [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".sql":  (["--"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".lua":  (["--"],       [{'start': '--[[', 'end': ']]'}], []),
    ".hs":   (["--"],       [{'start': '{-', 'end': '-}'}],  []),
    ".md":   ([],           [{'start': '<!--', 'end': '-->'}], []),
    ".html": ([],           [{'start': '<!--', 'end': '-->'}], []),
    ".xml":  ([],           [{'start': '<!--', 'end': '-->'}], []),
    ".svg":  ([],           [{'start': '<!--', 'end': '-->'}], []),
    ".vue":  (["//"],       [{'start': '/*', 'end': '*/'}, {'start': '<!--', 'end': '-->'}], ["*"]),
    ".svelte":(["//"],      [{'start': '/*', 'end': '*/'}, {'start': '<!--', 'end': '-->'}], ["*"]),
    ".css":  ([],           [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".scss": (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".less": (["//"],       [{'start': '/*', 'end': '*/'}],  ["*"]),
    ".ex":   (["#"],        [],                               []),
    ".exs":  (["#"],        [],                               []),
    ".erl":  (["%"],        [],                               []),
    ".clj":  ([";"],        [],                               []),
    ".lisp": ([";"],        [{'start': '#|', 'end': '|#'}],  []),
}


class LanguageConfig:
    """Language configuration for code scanning."""
    
    def __init__(
        self,
        file_extensions: Set[str],
        single_line_comments: List[str],
        multi_line_comments: List[Dict[str, str]],
        block_comment_prefixes: List[str],
    ):
        self.file_extensions = file_extensions
        self.single_line_comments = single_line_comments
        self.multi_line_comments = multi_line_comments
        self.block_comment_prefixes = block_comment_prefixes

    def build_comment_pattern(self) -> str:
        r"""
        Build regex pattern for matching comment prefixes.
        Returns pattern like: (?:#|//|<!--|/\*|\*)
        """
        patterns = []
        
        # Single-line comments
        for prefix in self.single_line_comments:
            patterns.append(re.escape(prefix))
        
        # Multi-line comment starts
        for mlc in self.multi_line_comments:
            patterns.append(re.escape(mlc["start"]))
        
        # Block comment prefixes
        for prefix in self.block_comment_prefixes:
            patterns.append(re.escape(prefix))
        
        return "(?:" + "|".join(patterns) + ")"


def load_language_config(start_path: Optional[Path] = None) -> LanguageConfig:
    """
    Load language configuration from project config.
    Falls back to defaults if not configured.
    
    Args:
        start_path: Starting directory for project search (defaults to cwd)
    
    Returns:
        LanguageConfig with project-specific or default settings
    """
    if start_path is None:
        start_path = Path.cwd()
    
    project_root = find_project_root(start_path)
    if project_root is None:
        return _default_language_config()
    
    config = load_project_config(project_root)
    if config is None:
        return _default_language_config()

    scanning = config.get("codeScanning") or config.get("code_scanning")
    if not isinstance(scanning, dict):
        return _default_language_config()
    
    # Extract file extensions
    file_exts = scanning.get("fileExtensions", DEFAULT_FILE_EXTENSIONS)
    if isinstance(file_exts, list):
        file_extensions = set(file_exts)
    else:
        file_extensions = DEFAULT_FILE_EXTENSIONS
    
    # Extract single-line comments
    single_line = scanning.get("singleLineComments", DEFAULT_SINGLE_LINE_COMMENTS)
    if not isinstance(single_line, list):
        single_line = DEFAULT_SINGLE_LINE_COMMENTS
    
    # Extract multi-line comments
    multi_line = scanning.get("multiLineComments", DEFAULT_MULTI_LINE_COMMENTS)
    if not isinstance(multi_line, list):
        multi_line = DEFAULT_MULTI_LINE_COMMENTS
    
    # Extract block comment prefixes
    block_prefixes = scanning.get("blockCommentPrefixes", DEFAULT_BLOCK_COMMENT_PREFIXES)
    if not isinstance(block_prefixes, list):
        block_prefixes = DEFAULT_BLOCK_COMMENT_PREFIXES
    
    return LanguageConfig(
        file_extensions=file_extensions,
        single_line_comments=single_line,
        multi_line_comments=multi_line,
        block_comment_prefixes=block_prefixes,
    )


def _default_language_config() -> LanguageConfig:
    """Return default language configuration."""
    return LanguageConfig(
        file_extensions=DEFAULT_FILE_EXTENSIONS,
        single_line_comments=DEFAULT_SINGLE_LINE_COMMENTS,
        multi_line_comments=DEFAULT_MULTI_LINE_COMMENTS,
        block_comment_prefixes=DEFAULT_BLOCK_COMMENT_PREFIXES,
    )


def comment_defaults_for_extensions(extensions: List[str]) -> Tuple[List[str], List[Dict[str, str]]]:
    """Return (single_line_comments, multi_line_comments) defaults for a list of file extensions.

    Merges defaults from all given extensions, deduplicating.
    Returns ([], []) if no extensions match.
    """
    merged_slc: List[str] = []
    merged_mlc: List[Dict[str, str]] = []
    seen_slc: Set[str] = set()
    seen_mlc: Set[str] = set()
    for ext in extensions:
        defaults = EXTENSION_COMMENT_DEFAULTS.get(ext.lower())
        if not defaults:
            continue
        d_slc, d_mlc, _ = defaults
        for s in d_slc:
            if s not in seen_slc:
                seen_slc.add(s)
                merged_slc.append(s)
        for m in d_mlc:
            key = m["start"] + m["end"]
            if key not in seen_mlc:
                seen_mlc.add(key)
                merged_mlc.append(m)
    return merged_slc, merged_mlc


def build_cypilot_begin_regex(lang_config: LanguageConfig) -> re.Pattern:
    """Build cpt-begin regex pattern using language config."""
    comment_pattern = lang_config.build_comment_pattern()
    return re.compile(rf"^\s*{comment_pattern}\s*(?:!no-cpt\s+)?cpt-begin\s+([^\s]+)")


def build_cypilot_end_regex(lang_config: LanguageConfig) -> re.Pattern:
    """Build cpt-end regex pattern using language config."""
    comment_pattern = lang_config.build_comment_pattern()
    return re.compile(rf"^\s*{comment_pattern}\s*(?:!no-cpt\s+)?cpt-end\s+([^\s]+)")


def build_no_cypilot_begin_regex(lang_config: LanguageConfig) -> re.Pattern:
    """Build !no-cpt-begin regex pattern using language config."""
    comment_pattern = lang_config.build_comment_pattern()
    return re.compile(rf"^\s*{comment_pattern}.*!no-cpt-begin")


def build_no_cypilot_end_regex(lang_config: LanguageConfig) -> re.Pattern:
    """Build !no-cpt-end regex pattern using language config."""
    comment_pattern = lang_config.build_comment_pattern()
    return re.compile(rf"^\s*{comment_pattern}.*!no-cpt-end")


__all__ = [
    "LanguageConfig",
    "load_language_config",
    "build_cypilot_begin_regex",
    "build_cypilot_end_regex",
    "build_no_cypilot_begin_regex",
    "build_no_cypilot_end_regex",
    "DEFAULT_FILE_EXTENSIONS",
    "DEFAULT_SINGLE_LINE_COMMENTS",
    "EXTENSION_COMMENT_DEFAULTS",
    "comment_defaults_for_extensions",
]
