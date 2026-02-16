# Testing Guidelines

## Test Framework

- **Framework**: pytest
- **Coverage**: pytest-cov
- **Threshold**: 90% per file minimum

## Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
pytest tests/test_cli_integration.py -v

# Run specific test
pytest tests/test_cli_integration.py::TestValidateCommand -v
```

---

## Test File Organization

| File | Coverage Area |
|------|---------------|
| `test_cli_integration.py` | CLI command integration (156KB) |
| `test_template_utils.py` | Template parsing and validation |
| `test_codebase.py` | Code file parsing, markers |
| `test_parse_sid.py` | Cypilot ID parsing |
| `test_artifacts_meta.py` | artifacts.json parsing |
| `test_files_utils.py` | File operations |
| `test_cli_helpers.py` | CLI helper functions |
| `test_context.py` | CypilotContext, LoadedKit |
| `test_core_structure.py` | Project structure validation |
| `test_cli_py_coverage.py` | Coverage gap tests |
| `test_language_config.py` | Language configuration |
| `test_parsing_utils.py` | Markdown parsing |
| `test_validate.py` | Validation utilities |
| `test_adapter_info.py` | Adapter discovery |
| `test_workflow_parsing.py` | Workflow file parsing |
| `test_design_validation.py` | DESIGN.md validation |
| `test_ai_navigate_when.py` | WHEN clause parsing |

---

## Test Patterns

### 1. Temporary Directory Tests

```python
from tempfile import TemporaryDirectory
from pathlib import Path

def test_something():
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Create test files
        (root / "test.md").write_text("content")
        # Run test
        result = function_under_test(root)
        assert result == expected
```

### 2. CLI Command Tests

```python
import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout
from cypilot.cli import main

def test_cli_command():
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _bootstrap_project_root(root)

        cwd = os.getcwd()
        try:
            os.chdir(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["command", "--flag"])
            assert exit_code == 0
            out = json.loads(stdout.getvalue())
            assert out["status"] == "PASS"
        finally:
            os.chdir(cwd)
```

### 3. Mocking Tests

```python
from unittest.mock import patch, MagicMock
from cypilot.utils.context import CypilotContext

def test_with_mock():
    mock_ctx = MagicMock(spec=CypilotContext)
    with patch("cypilot.utils.context.CypilotContext.load", return_value=mock_ctx):
        result = function_that_uses_context()
        assert result is not None
```

### 4. Bootstrap Helpers

```python
def _bootstrap_project_root(root: Path, adapter_rel: str = "adapter") -> Path:
    """Create minimal project structure for tests."""
    (root / ".git").mkdir()
    (root / ".cypilot-config.json").write_text(
        json.dumps({"cypilotAdapterPath": adapter_rel}),
        encoding="utf-8",
    )
    adapter = root / adapter_rel
    adapter.mkdir(parents=True, exist_ok=True)
    (adapter / "AGENTS.md").write_text("# Test adapter\n")
    return adapter
```

---

## Coverage Requirements

### Per-File Threshold: 90%

```
skills/cypilot/scripts/cypilot/cli.py          90%+
skills/cypilot/scripts/cypilot/utils/*.py      90%+
```

### Checking Coverage

```bash
# Run coverage check
make test-coverage

# View HTML report
open htmlcov/index.html
```

### Coverage Exclusions

```ini
# .coveragerc
[run]
omit =
    */cypilot/__main__.py
    */__main__.py
```

---

## Test Naming Conventions

```python
class TestClassName:
    def test_method_behavior_when_condition(self):
        """Description of what is being tested."""
        pass

# Examples:
def test_validate_returns_pass_for_valid_artifact(self):
def test_scan_ids_finds_all_defined_ids(self):
def test_init_creates_adapter_directory(self):
def test_context_load_returns_none_when_no_adapter(self):
```

---

## Common Test Fixtures

### Valid Template

```python
VALID_TEMPLATE = '''---
cypilot-template:
  kind: req
  version:
    major: 1
    minor: 0
---

'''
```

### Valid artifacts.json

```python
VALID_REGISTRY = {
    "version": "1.1",
    "project_root": "..",
    "kits": {
        "cypilot-sdlc": {
            "format": "Cypilot",
            "path": "kits/sdlc"
        }
    },
    "systems": [
        {
            "name": "Test",
            "slug": "test",
            "kit": "cypilot-sdlc",
            "autodetect": [],
        }
    ],
}
```

---

## CI Integration

Tests run on every commit via Makefile:

```makefile
test:
    pytest tests/ -v

test-coverage:
    pytest tests/ -v --cov=skills/cypilot/scripts/cypilot \
        --cov-report=html --cov-report=json --cov-report=term
    python scripts/check_coverage.py
```

---

**Source**: Test suite analysis
**Last Updated**: 2026-02-03
