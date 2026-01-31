"""
FDD Validator - Utility Functions

Utility modules for file operations and markdown parsing.
"""

from .files import (
    cfg_get_str,
    find_project_root,
    load_project_config,
    fdd_root_from_project_config,
    find_adapter_directory,
    load_adapter_config,
    load_artifacts_registry,
    iter_registry_entries,
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
    split_by_section_letter_with_offsets,
    split_by_feature_section_letter_with_offsets,
    split_by_prd_section_letter_with_offsets,
    field_block,
    has_list_item,
    extract_backticked_ids,
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

from .artifacts_meta import (
    ArtifactsMeta,
    SystemNode,
    Artifact,
    CodebaseEntry,
    load_artifacts_meta,
)

from .codebase import (
    CodeFile,
    ScopeMarker,
    BlockMarker,
    CodeReference,
    load_code_file,
    validate_code_file,
    scan_directory as scan_code_directory,
    cross_validate_code,
)

__all__ = [
    # File operations
    "cfg_get_str",
    "find_project_root",
    "load_project_config",
    "fdd_root_from_project_config",
    "find_adapter_directory",
    "load_adapter_config",
    "load_artifacts_registry",
    "iter_registry_entries",
    "fdd_root_from_this_file",
    "detect_requirements",
    "load_text",
    # Parsing utilities
    "parse_required_sections",
    "find_present_section_ids",
    "split_by_section_letter",
    "split_by_feature_section_letter",
    "split_by_prd_section_letter",
    "split_by_section_letter_with_offsets",
    "split_by_feature_section_letter_with_offsets",
    "split_by_prd_section_letter_with_offsets",
    "field_block",
    "has_list_item",
    "extract_backticked_ids",
    # Language configuration
    "LanguageConfig",
    "load_language_config",
    "build_fdd_begin_regex",
    "build_fdd_end_regex",
    "build_no_fdd_begin_regex",
    "build_no_fdd_end_regex",
    "DEFAULT_FILE_EXTENSIONS",
    # Artifacts metadata
    "ArtifactsMeta",
    "SystemNode",
    "Artifact",
    "CodebaseEntry",
    "load_artifacts_meta",
    # Codebase parsing
    "CodeFile",
    "ScopeMarker",
    "BlockMarker",
    "CodeReference",
    "load_code_file",
    "validate_code_file",
    "scan_code_directory",
    "cross_validate_code",
]
