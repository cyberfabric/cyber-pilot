# Code Conventions

**Version**: 2.0
**Last Updated**: 2026-02-01  
**Purpose**: Define coding style and conventions for FDD project

---

## FDD Core Principles (Migrated)

When requirements in this spec conflict with `architecture/features/feature-init-structure/DESIGN.md`, follow `architecture/features/feature-init-structure/DESIGN.md`.

### Framework Development Guardrails

When modifying FDD framework sources (requirements, workflows, AGENTS, and the `fdd` tool), the agent MUST apply the following guardrails.

**Requirements and workflows** (`requirements/*.md`, `workflows/*.md`):
- **MUST** preserve YAML frontmatter and required fields for all FDD spec files.
- **MUST** keep file naming conventions (requirements: `kebab-case.md`, workflows: `kebab-case.md`).
- **MUST** run deterministic validation using `python3 skills/fdd/scripts/fdd/cli.py validate --artifact .` after edits.

**AGENTS.md files** (`AGENTS.md`, `workflows/AGENTS.md`, `.adapter/AGENTS.md`):
- **MUST** keep these files navigation-only (no spec duplication).
- **MUST** keep WHEN clauses rules-based (reference rule IDs and artifact kinds, not workflow names).
- **MUST** run `python3 skills/fdd/scripts/fdd/cli.py validate --artifact .` after edits.

**Skills / tooling** (`skills/fdd/**`):
- **MUST** keep runtime Python dependencies standard-library only.
- **MUST** update `skills/fdd/fdd.clispec` when the CLI surface changes.
- **MUST** run `python3 skills/fdd/scripts/fdd/cli.py validate --artifact .` after edits.

**Validation gates** (Makefile, validators, coverage checks):
- **MUST NOT** bypass validation gates by weakening thresholds, adding exclusions, or changing checks to avoid failures.
- **MUST** make gates pass by improving tests and/or fixing implementation.

### English Language Only

**MUST** write all content in English.

### Brevity

**MUST** use concise language and avoid redundancy.

### Imperative Style

**MUST** use command form and start instructions with action verbs.

### Agent-Centric Design

**MUST** structure content for AI parsing:
- Use consistent formatting
- Provide clear steps
- Make prerequisites explicit

### OS Agnostic

**MUST** use cross-platform descriptions and forward slashes in paths.

**MUST NOT** rely on OS-specific commands.

### Formatting Rules

**MUST** use valid Markdown.

**MUST** ensure metadata-like lines render as separate lines:
- Prefer Markdown lists for metadata fields
- Or end each metadata line with two spaces (`  `)

**MUST NOT** use TODO/TBD/FIXME/XXX placeholders in spec/requirements artifacts.

## Python Code Style

### Naming Conventions

**Functions and variables**: `snake_case`
```python
def validate_feature_design(artifact_text: str) -> Dict[str, object]:
    placeholder_hits = find_placeholders(artifact_text)
```

**Constants**: `SCREAMING_SNAKE_CASE`
```python
PROJECT_CONFIG_FILENAME = ".fdd-config.json"
PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|FIXME|XXX|TBA)\b")
```

**Classes**: `PascalCase` (when used)
```python
class ValidationReport:
    pass
```

**Private functions**: Prefix with `_`
```python
def _find_project_root(start: Path) -> Optional[Path]:
    pass
```

### Type Hints

**Required** for all function signatures:
```python
from typing import Dict, List, Optional, Tuple

def parse_required_sections(requirements_path: Path) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    return sections
```

**Common types**:
- `Dict[str, object]` for flexible dictionaries
- `List[str]` for string lists
- `Optional[Path]` for nullable paths
- `Tuple[str, str]` for pairs

### Docstrings

**Multi-line docstrings** for complex functions:
```python
def _find_adapter_directory(start: Path, fdd_root: Optional[Path] = None) -> Optional[Path]:
    """
    Find FDD-Adapter directory starting from project root.
    Uses smart recursive search to find adapter in ANY location within project.
    
    Search strategy:
    1. Check .fdd-config.json for configured path
    2. Search common locations (FDD-Adapter, spec/FDD-Adapter, etc.)
    3. Recursive search if not found
    
    Returns adapter directory or None if not found.
    """
```

### Import Organization

**Standard library first**, alphabetically:
```python
import argparse
import fnmatch
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
```

**No external dependencies** - Only standard library imports

---

## Markdown Documentation Style

### File Naming

- Core documentation: `SCREAMING_SNAKE.md` (README.md, AGENTS.md)
- Requirements: `kebab-case-structure.md`
- Workflows: `kebab-case.md`
- Specifications: `kebab-case.md`

### Heading Conventions

**Hierarchical structure**:
```markdown
# Top Level (Title)

## Major Section

### Subsection

#### Detail Level
```

**Section letters** (in requirements/workflows):
```markdown
### Section A: Vision
### Section B: Actors
### Section C: Capabilities
```

### FDD ID Format

**Pattern**: `` `fdd-{project}-{kind}-{name}` ``

**Examples**:
- `` `fdd-myapp-actor-admin` ``
- `` `fdd-myapp-req-user-auth` ``
- `` `fdd-myapp-flow-login` ``

**Always wrapped in backticks** in Markdown

---

## Test Conventions

### Test File Naming

**Pattern**: `test_*.py`

**Examples**:
- `test_validate.py` - Validation tests
- `test_design_validation.py` - Design validation tests
- `test_core_structure.py` - Core structure tests

### Test Structure

**pytest framework**:
```python
def test_feature_design_valid():
    result = validate_feature_design(text)
    assert result["status"] == "PASS"
```

### Test Organization

- One test class per major feature
- Descriptive test method names: `test_{what}_{condition}`
- Use `setUp()` for common fixtures
- 82+ tests covering all functionality

---

## Source

**Discovered from**:
- `skills/fdd/scripts/fdd/cli.py` - Main CLI implementation
- Code analysis (function names, type hints, imports)

---

## Validation Checklist

Agent MUST verify before implementation:
- [ ] Function names use `snake_case`
- [ ] Type hints present on all functions
- [ ] Constants use `SCREAMING_SNAKE_CASE`
- [ ] Imports are standard library only
- [ ] Tests follow `test_*.py` naming
- [ ] FDD IDs wrapped in backticks in Markdown

**Self-test**:
- [ ] Did I check all criteria?
- [ ] Are examples from actual codebase?
- [ ] Do naming rules match existing code?
