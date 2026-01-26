# Testing

**Version**: 1.0  
**Last Updated**: 2025-01-17  
**Purpose**: Define testing strategy and practices for FDD project

---

## Test Framework

**Framework**: `pytest` (executed via `pipx`)

**Why pytest**:
- The repository test suite under `tests/` is written for `pytest`
- Matches `Makefile` targets (`make test`, `make test-coverage`)

**Notes**:
- Some tests import `unittest` utilities (for example, `unittest.SkipTest`) for compatibility shims, but the suite is executed by `pytest`

**Agent Permission**:
- `pipx` commands are **pre-approved** - agents MUST NOT ask user permission to run `pipx` commands

---

## Test Structure

### Test Location

```
tests/
├── test_validate.py
├── test_design_validation.py
├── test_core_structure.py
└── test_workflow_parsing.py
```

### Test Files

**test_validate.py**:
- Artifact validation (PRD.md, DESIGN.md, etc.)
- Code traceability scanning
- ID format validation
- Cross-reference checks

**test_design_validation.py**:
- Design-first enforcement checks on real artifacts

**test_core_structure.py**:
- Base structure checks for requirements/workflows/AGENTS

**test_workflow_parsing.py**:
- Workflow parsing and required section checks

---

## Running Tests

### Run All Tests

```bash
make test
```

### Run All Tests (Direct)

```bash
pipx run --spec pytest pytest tests/ -v --tb=short
```

### Run Specific Test File

```bash
pipx run --spec pytest pytest tests/test_validate.py -v --tb=short
```

### Run Specific Test Case

```bash
pipx run --spec pytest pytest tests/test_validate.py -k "TestFeatureDesignValidation and test_valid_minimal" -v --tb=short
```

---

## Test Coverage

**Coverage Areas**:
- Artifact structure validation
- Workflow parsing and structure checks
- Traceability scanning and ID validation

**Production Tested**:
- Validated on real project (hyperspot/modules/analytics)
- 24 FDD artifacts validated
- 263 IDs scanned
- 36 code tags verified

---

## Test Writing Guidelines

### Mandatory Coverage Check

**MUST**: Agent MUST run `make test-coverage` after writing or modifying tests to verify:
- All tests pass
- Coverage meets project requirements

```bash
make test-coverage
```

### Test Class Structure

```python
from pathlib import Path
from tempfile import TemporaryDirectory

def test_valid_feature_design():
    result = validate_feature_design(valid_text)
    assert result["status"] == "PASS"

def test_invalid_missing_section():
    result = validate_feature_design(invalid_text)
    assert result["status"] == "FAIL"
```

### Naming Convention

**Test methods**: `test_{what}_{condition}`

Examples:
- `test_valid_minimal` - Test minimal valid input
- `test_invalid_missing_id` - Test missing ID error
- `test_empty_input` - Test empty input handling

### Assertions

**Common patterns**:
```python
assert result["status"] == "PASS"
assert "error" in result
assert len(result["errors"]) > 0
assert result["data"] is None
```

---

## Test Data

### Temporary Files

Use `TemporaryDirectory` for file-based tests:
```python
with TemporaryDirectory() as tmpdir:
    test_file = Path(tmpdir) / "test.md"
    test_file.write_text("content")
    result = validate(test_file)
```

### Sample Data

Create helper functions for test data:
```python
def _valid_feature_design() -> str:
    return """
# Feature Design: Test
## A. Overview
...
"""
```

---

## CI/CD Integration

**Current**: Manual test execution

**Future**:
- GitHub Actions workflow
- Pre-commit hooks
- Coverage reporting

**Command for CI**:
```bash
pipx run --spec pytest pytest tests/ -v --tb=short
```

---

## Source

**Discovered from**:
- `tests/` directory
- `Makefile` targets (`test`, `test-coverage`)
- Test file analysis

---

## Validation Checklist

Agent MUST verify before implementation:
- [ ] Tests use `pytest` framework
- [ ] Test files follow `test_*.py` naming
- [ ] Test methods start with `test_`
- [ ] Tests are in `tests/` directory
- [ ] Tests can run via `make test` (preferred) or `pipx run --spec pytest pytest`

**Self-test**:
- [ ] Did I check all criteria?
- [ ] Are test commands correct for this project?
- [ ] Do examples match actual test structure?
