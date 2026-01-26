"""
FDD Validator - Constants and Regex Patterns

All regular expressions and global constants used throughout the FDD validation system.
Extracted for easier maintenance and modification by both humans and AI agents.
"""

import re
from typing import Dict

# === PROJECT CONFIGURATION ===

PROJECT_CONFIG_FILENAME = ".fdd-config.json"

# === ARTIFACT STRUCTURE PATTERNS ===

SECTION_RE = re.compile(r"^###\s+Section\s+([A-Z0-9]+):\s+(.+?)\s*$")
HEADING_ID_RE = re.compile(r"^#{1,6}\s+([A-Z])\.\s+.*$")
SECTION_FEATURE_RE = re.compile(r"^##\s+([A-H])\.\s+(.+?)\s*$")
SECTION_PRD_RE = re.compile(r"^##\s+(?:Section\s+)?([A-Z])\s*[:.]\s*(.+)?$", re.IGNORECASE)

# === FDD ID PATTERNS ===

# Generic FDD ID
FDD_ANY_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+\b")

# Core artifact IDs
REQ_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-req-[a-z0-9-]+\b")
NFR_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-nfr-[a-z0-9-]+\b")
PRINCIPLE_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-principle-[a-z0-9-]+\b")
CONSTRAINT_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-constraint-[a-z0-9-]+\b")
ACTOR_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-actor-[a-z0-9-]+\b")
CAPABILITY_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-capability-[a-z0-9-]+\b")
PRD_FR_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-fr-[a-z0-9-]+\b")
USECASE_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-usecase-[a-z0-9-]+\b")
PRD_CONTEXT_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-prd-context-[a-z0-9-]+\b")

# Feature-specific IDs
FEATURE_FLOW_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-feature-([a-z0-9-]+)-flow-[a-z0-9-]+\b")
FEATURE_ALGO_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-feature-([a-z0-9-]+)-algo-[a-z0-9-]+\b")
FEATURE_STATE_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-feature-([a-z0-9-]+)-state-[a-z0-9-]+\b")
FEATURE_REQ_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-feature-([a-z0-9-]+)-req-[a-z0-9-]+\b")
FEATURE_TEST_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-feature-([a-z0-9-]+)-test-[a-z0-9-]+\b")
FEATURE_CONTEXT_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-feature-([a-z0-9-]+)-context-[a-z0-9-]+\b")

# ADR IDs
ADR_NUM_RE = re.compile(r"\bADR-(\d{4})\b")
FDD_ADR_NUM_RE = re.compile(r"\bfdd-[a-z0-9-]+-adr-(\d{4})\b")
ADR_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-adr-[a-z0-9-]+\b")
ADR_HEADING_RE = re.compile(r"^#{1,2}\s+(ADR-(\d{4})):\s+(.+?)\s*$", re.MULTILINE)

# === FDL (FDD Description Language) PATTERNS ===

FDL_STEP_LINE_RE = re.compile(r"^\s*(?:\d+\.|-)\s+\[[ xX]\]\s+-\s+`ph-\d+`\s+-\s+.+?\s+-\s+`inst-[a-z0-9-]+`\s*$")
FDL_SCOPE_ID_RE = re.compile(
    r"^\s*[-*]\s+\[[ xX]\]\s+\*\*ID\*\*:\s*`fdd-[a-z0-9-]+-feature-[a-z0-9-]+-(?:flow|algo|state)-[a-z0-9-]+`\s*$"
)
PHASE_TOKEN_RE = re.compile(r"\bph-(\d+)\b")

# === CODE TRACEABILITY PATTERNS ===

# @fdd-* tags in code comments
FDD_TAG_FLOW_RE = re.compile(r"@fdd-flow:(fdd-[a-z0-9-]+):ph-(\d+)")
FDD_TAG_ALGO_RE = re.compile(r"@fdd-algo:(fdd-[a-z0-9-]+):ph-(\d+)")
FDD_TAG_STATE_RE = re.compile(r"@fdd-state:(fdd-[a-z0-9-]+):ph-(\d+)")
FDD_TAG_REQ_RE = re.compile(r"@fdd-req:(fdd-[a-z0-9-]+):ph-(\d+)")
FDD_TAG_TEST_RE = re.compile(r"@fdd-test:(fdd-[a-z0-9-]+):ph-(\d+)")

# fdd-begin/fdd-end block markers
FDD_BEGIN_LINE_RE = re.compile(r"^\s*(?:#|//|<!--|/\*|\*)\s*(?:!no-fdd\s+)?fdd-begin\s+([^\s]+)")
FDD_END_LINE_RE = re.compile(r"^\s*(?:#|//|<!--|/\*|\*)\s*(?:!no-fdd\s+)?fdd-end\s+([^\s]+)")

# Unwrapped instruction tags (should be wrapped in fdd-begin/fdd-end)
UNWRAPPED_INST_TAG_RE = re.compile(r"(fdd-[a-z0-9-]+(?:-[a-z0-9-]+)*:ph-\d+:inst-[a-z0-9-]+)")

# Block exclusion markers (!no-fdd-begin/!no-fdd-end)
NO_FDD_BLOCK_BEGIN_RE = re.compile(r"^\s*(?:#|//|<!--|/\*|\*).*!no-fdd-begin")
NO_FDD_BLOCK_END_RE = re.compile(r"^\s*(?:#|//|<!--|/\*|\*).*!no-fdd-end")

# === SCOPE ID PATTERNS BY KIND ===

SCOPE_ID_BY_KIND_RE: Dict[str, re.Pattern] = {
    "flow": FEATURE_FLOW_ID_RE,
    "algo": FEATURE_ALGO_ID_RE,
    "state": FEATURE_STATE_ID_RE,
    "req": FEATURE_REQ_ID_RE,
    "test": FEATURE_TEST_ID_RE,
}

# === VALIDATION PATTERNS ===

PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|TBF|TBC|TBA|FIXME|XXX)\b", re.IGNORECASE)
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
DISALLOWED_LINK_TOKEN_RE = re.compile(r"(@/|@DESIGN\.md|@PRD\.md|@ADR\.md)")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
BRACE_PLACEHOLDER_RE = re.compile(r"\{[A-Za-z0-9_-]+\}")
SIZE_HARD_LIMIT_RE = re.compile(r"Hard limit:\s*≤?\s*(\d+)\s*lines", re.IGNORECASE)
ID_LINE_RE = re.compile(r"\*\*ID\*\*:\s*(.+)$")

# ADR-specific patterns
ADR_DATE_RE = re.compile(r"\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})")
ADR_STATUS_RE = re.compile(r"\*\*Status\*\*:\s*(Proposed|Rejected|Accepted|Deprecated|Superseded)")
ADR_ID_LINE_RE = re.compile(r"\*\*ADR\s+ID\*\*:\s*`(fdd-[a-z0-9-]+-adr-[a-z0-9-]+)`", re.IGNORECASE)

# Status overview pattern
STATUS_OVERVIEW_RE = re.compile(
    r"\*\*Status Overview\*\*:\s*(\d+)\s+features\s+total\s*\(\s*"
    r"(\d+)\s+(?:completed|implemented),\s*"
    r"(\d+)\s+(?:in progress|in development),\s*"
    r"(?:(\d+)\s+design ready,\s*(\d+)\s+in design,\s*)?"
    r"(\d+)\s+not started\s*\)"
)

# Feature heading pattern
FEATURE_HEADING_RE = re.compile(
    r"^###\s+(\d+)\.\s+\[(.+?)\]\((feature-[^)]+/)\)\s+([⏳📝📘🔄✅])\s+(CRITICAL|HIGH|MEDIUM|LOW)\s*$"
)

# Field header pattern
FIELD_HEADER_RE = re.compile(r"^\s*[-*]?\s*\*\*([^*]+)\*\*:\s*(.*)$")

# === KNOWN FIELD NAMES ===

KNOWN_FIELD_NAMES = {
    "Purpose",
    "Status",
    "Description",
    "Implementation details",
    "References",
    "Implements",
    "Phases",
    "Depends On",
    "Blocks",
    "Scope",
    "Requirements Covered",
    "Principles Covered",
    "Constraints Affected",
    "Actors",
    "Capabilities",
    "Use Cases",
    "ADRs",
    "Testing Scenarios (FDL)",
    "Testing Scenarios",
    "Acceptance Criteria",
}
