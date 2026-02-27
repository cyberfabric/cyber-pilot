"""
Cypilot Validator - Utility Functions

Utility modules for file operations and markdown parsing.
"""

from .files import (
    cfg_get_str,
    find_project_root,
    load_project_config,
    cypilot_root_from_project_config,
    find_cypilot_directory,
    load_cypilot_config,
    load_artifacts_registry,
    iter_registry_entries,
    cypilot_root_from_this_file,
    load_text,
)

from .parsing import (
    parse_required_sections,
    find_present_section_ids,
    split_by_section_letter,
    split_by_section_letter_with_offsets,
    field_block,
    has_list_item,
    extract_backticked_ids,
)

from .language_config import (
    LanguageConfig,
    load_language_config,
    build_cypilot_begin_regex,
    build_cypilot_end_regex,
    build_no_cypilot_begin_regex,
    build_no_cypilot_end_regex,
    DEFAULT_FILE_EXTENSIONS,
    EXTENSION_COMMENT_DEFAULTS,
    comment_defaults_for_extensions,
)

from .artifacts_meta import (
    ArtifactsMeta,
    SystemNode,
    Artifact,
    CodebaseEntry,
    Kit,
    load_artifacts_meta,
)

from .codebase import (
    CodeFile,
    ScopeMarker,
    BlockMarker,
    CodeReference,
    load_code_file,
    validate_code_file,
    cross_validate_code,
)

from .context import (
    CypilotContext,
    LoadedKit,
    get_context,
    set_context,
    ensure_context,
)

__all__ = [
    # File operations
    "cfg_get_str",
    "find_project_root",
    "load_project_config",
    "cypilot_root_from_project_config",
    "find_cypilot_directory",
    "load_cypilot_config",
    "load_artifacts_registry",
    "iter_registry_entries",
    "cypilot_root_from_this_file",
    "load_text",
    # Parsing utilities
    "parse_required_sections",
    "find_present_section_ids",
    "split_by_section_letter",
    "split_by_section_letter_with_offsets",
    "field_block",
    "has_list_item",
    "extract_backticked_ids",
    # Language configuration
    "LanguageConfig",
    "load_language_config",
    "build_cypilot_begin_regex",
    "build_cypilot_end_regex",
    "build_no_cypilot_begin_regex",
    "build_no_cypilot_end_regex",
    "DEFAULT_FILE_EXTENSIONS",
    "EXTENSION_COMMENT_DEFAULTS",
    "comment_defaults_for_extensions",
    # Artifacts metadata
    "ArtifactsMeta",
    "SystemNode",
    "Artifact",
    "CodebaseEntry",
    "Kit",
    "load_artifacts_meta",
    # Codebase parsing
    "CodeFile",
    "ScopeMarker",
    "BlockMarker",
    "CodeReference",
    "load_code_file",
    "validate_code_file",
    "cross_validate_code",
    # Context
    "CypilotContext",
    "LoadedKit",
    "get_context",
    "set_context",
    "ensure_context",
]
