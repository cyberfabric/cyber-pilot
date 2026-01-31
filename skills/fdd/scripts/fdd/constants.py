"""
FDD Validator - Constants and Regex Patterns

All regular expressions and global constants used throughout the FDD validation system.
Extracted for easier maintenance and modification by both humans and AI agents.
"""

import re
from typing import Dict

# === PROJECT CONFIGURATION ===

PROJECT_CONFIG_FILENAME = ".fdd-config.json"
ARTIFACTS_REGISTRY_FILENAME = "artifacts.json"

# === ARTIFACT STRUCTURE PATTERNS ===

SECTION_RE = re.compile(r"^###\s+Section\s+([A-Z0-9]+):\s+(.+?)\s*$")
HEADING_ID_RE = re.compile(r"^#{1,6}\s+([A-Z])\.\s+.*$")
SECTION_FEATURE_RE = re.compile(r"^##\s+([A-H])\.\s+(.+?)\s*$")
SECTION_PRD_RE = re.compile(r"^##\s+(?:Section\s+)?([A-Z])\s*[:.]\s*(.+)?$", re.IGNORECASE)

# === FDD ID PATTERNS ===

# Core artifact IDs
REQ_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-req-[a-z0-9-]+\b")
NFR_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-nfr-[a-z0-9-]+\b")
ACTOR_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-actor-[a-z0-9-]+\b")
CAPABILITY_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-capability-[a-z0-9-]+\b")
PRD_FR_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-fr-[a-z0-9-]+\b")
USECASE_ID_RE = re.compile(r"\bfdd-[a-z0-9-]+-usecase-[a-z0-9-]+\b")

# ADR IDs
ADR_HEADING_RE = re.compile(r"^#{1,2}\s+(ADR-(\d{4})):\s+(.+?)\s*$", re.MULTILINE)

# === FDL (FDD Description Language) PATTERNS ===

FDL_STEP_LINE_RE = re.compile(r"^\s*(?:\d+\.|-)\s+\[[ xX]\]\s+-\s+`ph-\d+`\s+-\s+.+?\s+-\s+`inst-[a-z0-9-]+`\s*$")
FDL_SCOPE_ID_RE = re.compile(
    r"^\s*[-*]\s+\[[ xX]\]\s+\*\*ID\*\*:\s*`fdd-[a-z0-9-]+-feature-[a-z0-9-]+-(?:flow|algo|state)-[a-z0-9-]+`\s*$"
)

# === CODE TRACEABILITY PATTERNS ===

# @fdd-* tags in code comments
FDD_TAG_FLOW_RE = re.compile(r"@fdd-flow:(fdd-[a-z0-9-]+):ph-(\d+)")
FDD_TAG_ALGO_RE = re.compile(r"@fdd-algo:(fdd-[a-z0-9-]+):ph-(\d+)")
FDD_TAG_STATE_RE = re.compile(r"@fdd-state:(fdd-[a-z0-9-]+):ph-(\d+)")
FDD_TAG_REQ_RE = re.compile(r"@fdd-req:(fdd-[a-z0-9-]+):ph-(\d+)")
FDD_TAG_TEST_RE = re.compile(r"@fdd-test:(fdd-[a-z0-9-]+):ph-(\d+)")

# Unwrapped instruction tags (should be wrapped in fdd-begin/fdd-end)
UNWRAPPED_INST_TAG_RE = re.compile(r"(fdd-[a-z0-9-]+(?:-[a-z0-9-]+)*:ph-\d+:inst-[a-z0-9-]+)")

# === SCOPE ID PATTERNS BY KIND ===

SCOPE_ID_BY_KIND_RE: Dict[str, re.Pattern] = {
    "flow": re.compile(r"\bfdd-[a-z0-9-]+-feature-([a-z0-9-]+)-flow-[a-z0-9-]+\b"),
    "algo": re.compile(r"\bfdd-[a-z0-9-]+-feature-([a-z0-9-]+)-algo-[a-z0-9-]+\b"),
    "state": re.compile(r"\bfdd-[a-z0-9-]+-feature-([a-z0-9-]+)-state-[a-z0-9-]+\b"),
    "req": re.compile(r"\bfdd-[a-z0-9-]+-feature-([a-z0-9-]+)-req-[a-z0-9-]+\b"),
    "test": re.compile(r"\bfdd-[a-z0-9-]+-feature-([a-z0-9-]+)-test-[a-z0-9-]+\b"),
}

# === VALIDATION PATTERNS ===

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

MAX_LINE_COUNT_WARN = 3000
MAX_LINE_COUNT_FAIL = 6000

# ADR-specific patterns
ADR_DATE_RE = re.compile(r"\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})")
ADR_STATUS_RE = re.compile(r"\*\*Status\*\*:\s*(Proposed|Rejected|Accepted|Deprecated|Superseded)")
ADR_ID_LINE_RE = re.compile(r"\*\*ID\*\*\s*:?[\s]*`(fdd-[a-z0-9-]+-adr-[a-z0-9-]+)`", re.IGNORECASE)

# Feature heading pattern
FEATURE_HEADING_RE = re.compile(
    r"^###\s+(\d+)\.\s+\[(.+?)\]\((feature-[^)]+/)\)\s+([⏳📝📘🔄✅])\s+(CRITICAL|HIGH|MEDIUM|LOW)\s*$"
)

# Field header pattern
FIELD_HEADER_RE = re.compile(r"^\s*[-*]?\s*\*\*([^*]+)\*\*:\s*(.*)$")
# instead of hardcoded field names. Templates are the source of truth.
