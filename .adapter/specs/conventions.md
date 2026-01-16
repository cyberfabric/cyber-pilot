# Code Conventions

**Version**: 1.0  
**Last Updated**: 2025-01-17  
**Purpose**: Define coding style and conventions for FDD project

---

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
- `test_list_api.py` - List/search tests
- `test_read_search.py` - Read operations

### Test Structure

**unittest framework**:
```python
import unittest
from pathlib import Path

class TestValidation(unittest.TestCase):
    def test_feature_design_valid(self):
        result = validate_feature_design(text)
        self.assertEqual(result["status"], "PASS")
```

### Test Organization

- One test class per major feature
- Descriptive test method names: `test_{what}_{condition}`
- Use `setUp()` for common fixtures
- 82+ tests covering all functionality

---

## Source

**Discovered from**:
- `skills/fdd/scripts/fdd.py` - Main implementation
- `skills/fdd/tests/*.py` - Test files
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
