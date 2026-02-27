"""
Cypilot Validator - Constants and Regex Patterns

All regular expressions and global constants used throughout the Cypilot validation system.
Extracted for easier maintenance and modification by both humans and AI agents.
"""

import re

# === PROJECT CONFIGURATION ===

PROJECT_CONFIG_FILENAME = ".cypilot-config.json"
ARTIFACTS_REGISTRY_FILENAME = "artifacts.json"
WORKSPACE_CONFIG_FILENAME = ".cypilot-workspace.json"

# === ARTIFACT STRUCTURE PATTERNS ===

SECTION_RE = re.compile(r"^###\s+Section\s+([A-Z0-9]+):\s+(.+?)\s*$")
HEADING_ID_RE = re.compile(r"^#{1,6}\s+([A-Z])\.\s+.*$")

# Field header pattern
FIELD_HEADER_RE = re.compile(r"^\s*[-*]?\s*\*\*([^*]+)\*\*:\s*(.*)$")
# instead of hardcoded field names. Templates are the source of truth.
