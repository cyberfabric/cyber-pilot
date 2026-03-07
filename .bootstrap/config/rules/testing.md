---
cypilot: true
type: project-rule
topic: testing
generated-by: auto-config
version: 1.0
---

# Testing Guidelines


<!-- toc -->

- [Test Framework](#test-framework)
- [Running Tests](#running-tests)
- [Test File Organization](#test-file-organization)
- [Test Patterns](#test-patterns)
  - [1. Temporary Directory Tests](#1-temporary-directory-tests)
  - [2. CLI Command Tests](#2-cli-command-tests)
  - [3. Mocking Tests](#3-mocking-tests)
  - [4. Bootstrap Helpers](#4-bootstrap-helpers)
- [Test Naming Conventions](#test-naming-conventions)
- [Coverage Requirements](#coverage-requirements)
  - [Per-File Threshold: 90%](#per-file-threshold-90)
  - [Checking Coverage](#checking-coverage)

<!-- /toc -->

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

## Test File Organization

35 test modules in `tests/`:

| File | Coverage Area |
|------|---------------|
| `test_adapter_info.py` | Adapter discovery |
| `test_agents_coverage.py` | Agent integration coverage |
| `test_ai_navigate_when.py` | WHEN clause parsing |
| `test_artifacts_meta.py` | artifacts.toml parsing |
| `test_blueprint_coverage.py` | Blueprint system coverage |
| `test_cli_helpers.py` | CLI helper functions |
| `test_cli_integration.py` | CLI command integration |
| `test_cli_py_coverage.py` | Coverage gap tests |
| `test_codebase.py` | Code file parsing, markers |
| `test_constraints_utils.py` | constraints.toml parsing |
| `test_context.py` | CypilotContext, LoadedKit |
| `test_core_structure.py` | Project structure validation |
| `test_coverage_utils.py` | Coverage utility functions |
| `test_cypilot_package_init.py` | Package init, version |
| `test_design_validation.py` | DESIGN.md validation |
| `test_diff_engine.py` | Three-way merge diff engine |
| `test_files_utils.py` | File operations |
| `test_fixing.py` | Auto-fix utilities |
| `test_hash_detection.py` | Blueprint hash detection |
| `test_kit.py` | Kit install/update/migrate |
| `test_language_config.py` | Language configuration |
| `test_migrate.py` | v2→v3 migration |
| `test_overwork_alert_*.py` | Example project tests (4 files) |
| `test_parse_sid.py` | Cypilot ID parsing |
| `test_parsing_utils.py` | Markdown parsing |
| `test_quickstart_bootstrap.py` | Bootstrap quickstart flow |
| `test_spec_coverage.py` | Spec coverage measurement |
| `test_toc.py` | TOC generation/validation |
| `test_ui_human_mode.py` | Human-friendly output mode |
| `test_update.py` | Update pipeline |
| `test_validate.py` | Validation utilities |
| `test_workflow_parsing.py` | Workflow file parsing |

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
def _bootstrap_project_root(root: Path, adapter_rel: str = "cypilot") -> Path:
    """Create minimal project structure for tests."""
    (root / ".git").mkdir()
    agents = root / "AGENTS.md"
    agents.write_text("<!-- @cpt:root-agents -->\n```toml\ncypilot_path = \"" + adapter_rel + "\"\n```\n")
    adapter = root / adapter_rel
    adapter.mkdir(parents=True, exist_ok=True)
    (adapter / "config").mkdir(exist_ok=True)
    (adapter / "config" / "AGENTS.md").write_text("# Cypilot Adapter: Test\n")
    return adapter
```

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
