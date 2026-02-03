"""
Spider Validator - Constants and Regex Patterns

All regular expressions and global constants used throughout the Spider validation system.
Extracted for easier maintenance and modification by both humans and AI agents.
"""

import re

# === PROJECT CONFIGURATION ===

PROJECT_CONFIG_FILENAME = ".spider-config.json"
ARTIFACTS_REGISTRY_FILENAME = "artifacts.json"

# === ARTIFACT STRUCTURE PATTERNS ===

SECTION_RE = re.compile(r"^###\s+Section\s+([A-Z0-9]+):\s+(.+?)\s*$")
HEADING_ID_RE = re.compile(r"^#{1,6}\s+([A-Z])\.\s+.*$")
SECTION_FEATURE_RE = re.compile(r"^##\s+([A-H])\.\s+(.+?)\s*$")
SECTION_PRD_RE = re.compile(r"^##\s+(?:Section\s+)?([A-Z])\s*[:.]\s*(.+)?$", re.IGNORECASE)

# Field header pattern
FIELD_HEADER_RE = re.compile(r"^\s*[-*]?\s*\*\*([^*]+)\*\*:\s*(.*)$")
# instead of hardcoded field names. Templates are the source of truth.
