"""
FDD Validator - Utility Functions

Utility modules for text processing, file operations, and markdown parsing.
"""

from .text import (
    slugify_anchor,
    find_placeholders,
)

from .files import (
    cfg_get_str,
    find_project_root,
    load_project_config,
    fdd_root_from_project_config,
    find_adapter_directory,
    load_adapter_config,
    fdd_root_from_this_file,
    detect_requirements,
    load_text,
)

from .parsing import (
    parse_required_sections,
    find_present_section_ids,
    split_by_section_letter,
    split_by_feature_section_letter,
    split_by_prd_section_letter,
    field_block,
    has_list_item,
    extract_backticked_ids,
)

from .helpers import (
    parse_prd_model,
    parse_prd_capability_statuses,
    load_adr_entries,
    scan_adr_directory,
    parse_design_requirement_statuses,
)

from .language_config import (
    LanguageConfig,
    load_language_config,
    build_fdd_begin_regex,
    build_fdd_end_regex,
    build_no_fdd_begin_regex,
    build_no_fdd_end_regex,
    DEFAULT_FILE_EXTENSIONS,
)

__all__ = [
    # Text utilities
    "slugify_anchor",
    "find_placeholders",
    # File operations
    "cfg_get_str",
    "find_project_root",
    "load_project_config",
    "fdd_root_from_project_config",
    "find_adapter_directory",
    "load_adapter_config",
    "fdd_root_from_this_file",
    "detect_requirements",
    "load_text",
    # Parsing utilities
    "parse_required_sections",
    "find_present_section_ids",
    "split_by_section_letter",
    "split_by_feature_section_letter",
    "split_by_prd_section_letter",
    "field_block",
    "has_list_item",
    "extract_backticked_ids",
    # Helper functions
    "parse_prd_model",
    "parse_prd_capability_statuses",
    "load_adr_entries",
    "scan_adr_directory",
    "parse_design_requirement_statuses",
    # Language configuration
    "LanguageConfig",
    "load_language_config",
    "build_fdd_begin_regex",
    "build_fdd_end_regex",
    "build_no_fdd_begin_regex",
    "build_no_fdd_end_regex",
    "DEFAULT_FILE_EXTENSIONS",
]
