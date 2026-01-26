"""
FDD Validator - Validation Modules

Validation logic for artifacts, FDL, and code traceability.
"""

from .traceability import (
    compute_excluded_line_ranges,
    is_line_excluded,
    is_effective_code_line,
    empty_fdd_tag_blocks_in_text,
    paired_inst_tags_in_text,
    unwrapped_inst_tag_hits_in_text,
    code_tag_hits,
    iter_code_files,
    extract_scope_ids,
)

from .fdl import (
    extract_fdl_instructions,
    extract_inst_tags_from_code,
    validate_fdl_code_to_design,
    validate_fdl_code_implementation,
)

from .artifacts import (
    validate,
    validate_feature_design,
    validate_overall_design,
    validate_prd,
    validate_adr,
    validate_features_manifest,
)

from .cascade import (
    ARTIFACT_DEPENDENCIES,
    find_artifact_path,
    resolve_dependencies,
    validate_with_dependencies,
)

__all__ = [
    # Traceability
    "compute_excluded_line_ranges",
    "is_line_excluded",
    "is_effective_code_line",
    "empty_fdd_tag_blocks_in_text",
    "paired_inst_tags_in_text",
    "unwrapped_inst_tag_hits_in_text",
    "code_tag_hits",
    "iter_code_files",
    "extract_scope_ids",
    
    # FDL
    "extract_fdl_instructions",
    "extract_inst_tags_from_code",
    "validate_fdl_code_to_design",
    "validate_fdl_code_implementation",
    
    # Artifacts
    "validate",
    "validate_feature_design",
    "validate_overall_design",
    "validate_prd",
    "validate_adr",
    "validate_features_manifest",
    
    # Cascade validation
    "ARTIFACT_DEPENDENCIES",
    "find_artifact_path",
    "resolve_dependencies",
    "validate_with_dependencies",
]
