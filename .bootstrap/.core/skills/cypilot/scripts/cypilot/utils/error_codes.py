"""Stable error codes for Cypilot validation.

Every validation error/warning carries a ``code`` field from this module.
Fixing prompts and downstream consumers match on codes, not messages.

@cpt-algo:cpt-cypilot-algo-traceability-validation-validate-structure:p1
@cpt-dod:cpt-cypilot-dod-traceability-validation-structure:p1
"""

# @cpt-begin:cpt-cypilot-algo-traceability-validation-validate-structure:p1:inst-check-headings
# ---------------------------------------------------------------------------
# Structure — task / checkbox consistency
# ---------------------------------------------------------------------------
CDSL_STEP_UNCHECKED = "cdsl-step-unchecked"
PARENT_UNCHECKED_ALL_DONE = "parent-unchecked-all-done"
PARENT_CHECKED_NESTED_UNCHECKED = "parent-checked-nested-unchecked"

# ---------------------------------------------------------------------------
# Structure — references
# ---------------------------------------------------------------------------
REF_NO_DEFINITION = "ref-no-definition"
REF_DONE_DEF_NOT_DONE = "ref-done-def-not-done"
DEF_DONE_REF_NOT_DONE = "def-done-ref-not-done"
REF_TASK_DEF_NO_TASK = "ref-task-def-no-task"

# ---------------------------------------------------------------------------
# Structure — heading numbering
# ---------------------------------------------------------------------------
HEADING_NUMBER_NOT_CONSECUTIVE = "heading-number-not-consecutive"

# ---------------------------------------------------------------------------
# Structure — cross-artifact ID coverage (validate.py)
# ---------------------------------------------------------------------------
ID_NOT_REFERENCED = "id-not-referenced"
ID_NOT_REFERENCED_NO_SCOPE = "id-not-referenced-no-scope"

# ---------------------------------------------------------------------------
# Constraints — ID kind presence
# ---------------------------------------------------------------------------
MISSING_CONSTRAINTS = "missing-constraints"
ID_SYSTEM_UNRECOGNIZED = "id-system-unrecognized"
ID_KIND_NOT_ALLOWED = "id-kind-not-allowed"
REQUIRED_ID_KIND_MISSING = "required-id-kind-missing"
TEMPLATE_DEF_KIND_NOT_IN_CONSTRAINTS = "template-def-kind-not-in-constraints"
TEMPLATE_REF_KIND_NOT_IN_CONSTRAINTS = "template-ref-kind-not-in-constraints"

# ---------------------------------------------------------------------------
# Constraints — task / priority on definitions
# ---------------------------------------------------------------------------
DEF_MISSING_TASK = "def-missing-task"
DEF_PROHIBITED_TASK = "def-prohibited-task"
DEF_MISSING_PRIORITY = "def-missing-priority"
DEF_PROHIBITED_PRIORITY = "def-prohibited-priority"

# ---------------------------------------------------------------------------
# Constraints — heading placement for definitions
# ---------------------------------------------------------------------------
DEF_WRONG_HEADINGS = "def-wrong-headings"

# ---------------------------------------------------------------------------
# Constraints — heading contract
# ---------------------------------------------------------------------------
HEADING_MISSING = "heading-missing"
HEADING_PROHIBITS_MULTIPLE = "heading-prohibits-multiple"
HEADING_REQUIRES_MULTIPLE = "heading-requires-multiple"
HEADING_NUMBERING_MISMATCH = "heading-numbering-mismatch"

# ---------------------------------------------------------------------------
# Constraints — cross-reference coverage
# ---------------------------------------------------------------------------
REF_TARGET_NOT_IN_SCOPE = "ref-target-not-in-scope"
REF_MISSING_FROM_KIND = "ref-missing-from-kind"
REF_WRONG_HEADINGS = "ref-wrong-headings"
REF_MISSING_TASK_FOR_TRACKED = "ref-missing-task-for-tracked"
REF_FROM_PROHIBITED_KIND = "ref-from-prohibited-kind"
REF_MISSING_TASK = "ref-missing-task"
REF_PROHIBITED_TASK = "ref-prohibited-task"
REF_MISSING_PRIORITY = "ref-missing-priority"
REF_PROHIBITED_PRIORITY = "ref-prohibited-priority"

# ---------------------------------------------------------------------------
# Code traceability — marker errors
# ---------------------------------------------------------------------------
MARKER_DUP_BEGIN = "marker-dup-begin"
MARKER_END_NO_BEGIN = "marker-end-no-begin"
MARKER_EMPTY_BLOCK = "marker-empty-block"
MARKER_BEGIN_NO_END = "marker-begin-no-end"
MARKER_DUP_SCOPE = "marker-dup-scope"

# ---------------------------------------------------------------------------
# Code traceability — cross-validation
# ---------------------------------------------------------------------------
CODE_DOCS_ONLY = "code-docs-only"
CODE_ORPHAN_REF = "code-orphan-ref"
CODE_TASK_UNCHECKED = "code-task-unchecked"
CODE_NO_MARKER = "code-no-marker"
CODE_INST_MISSING = "code-inst-missing"
CODE_INST_ORPHAN = "code-inst-orphan"

# ---------------------------------------------------------------------------
# TOC (Table of Contents) validation
# ---------------------------------------------------------------------------
TOC_MISSING = "toc-missing"
TOC_ANCHOR_BROKEN = "toc-anchor-broken"
TOC_HEADING_NOT_IN_TOC = "toc-heading-not-in-toc"
TOC_STALE = "toc-stale"

# ---------------------------------------------------------------------------
# File errors
# ---------------------------------------------------------------------------
FILE_READ_ERROR = "file-read-error"
FILE_LOAD_ERROR = "file-load-error"
# @cpt-end:cpt-cypilot-algo-traceability-validation-validate-structure:p1:inst-check-headings
