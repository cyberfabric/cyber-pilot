# Testing

**Version**: 1.0  
**Last Updated**: 2025-01-17  
**Purpose**: Define testing strategy and practices for FDD project

---

## Test Framework

**Framework**: `unittest` (Python standard library)

**Why unittest**:
- Part of Python standard library (no dependencies)
- Mature and well-documented
- Sufficient for project needs

---

## Test Structure

### Test Location

```
skills/fdd/tests/
├── test_validate.py      # 59 validation tests
├── test_list_api.py      # List/search API tests
└── test_read_search.py   # Read operations tests
```

### Test Files

**test_validate.py** (59 tests):
- Artifact validation (BUSINESS.md, DESIGN.md, etc.)
- Code traceability scanning
- ID format validation
- Cross-reference checks

**test_list_api.py** (23 tests):
- list-ids command
- list-items command
- list-sections command
- Pattern matching and filtering

**test_read_search.py**:
- read-section command
- get-item command
- find-id command
- Text search operations

---

## Running Tests

### Run All Tests

```bash
cd skills/fdd
python3 -m unittest discover -s tests -p 'test_*.py'
```

### Run Specific Test File

```bash
python3 -m unittest tests.test_validate
python3 -m unittest tests.test_list_api
python3 -m unittest tests.test_read_search
```

### Run Specific Test Case

```bash
python3 -m unittest tests.test_validate.TestFeatureDesignValidation
python3 -m unittest tests.test_validate.TestFeatureDesignValidation.test_valid_minimal
```

---

## Test Coverage

**Current Status**: ✅ 82/82 tests passing (100%)

**Coverage Areas**:
- ✅ All validation functions
- ✅ All search/traceability commands
- ✅ Code traceability scanning
- ✅ Error handling
- ✅ Edge cases

**Production Tested**:
- Validated on real project (hyperspot/modules/analytics)
- 24 FDD artifacts validated
- 263 IDs scanned
- 36 code tags verified

---

## Test Writing Guidelines

### Test Class Structure

```python
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

class TestFeatureValidation(unittest.TestCase):
    def setUp(self):
        # Common setup for all tests
        pass
    
    def test_valid_feature_design(self):
        # Test valid input
        result = validate_feature_design(valid_text)
        self.assertEqual(result["status"], "PASS")
    
    def test_invalid_missing_section(self):
        # Test error handling
        result = validate_feature_design(invalid_text)
        self.assertEqual(result["status"], "FAIL")
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
self.assertEqual(result["status"], "PASS")
self.assertIn("error", result)
self.assertTrue(len(result["errors"]) > 0)
self.assertIsNone(result["data"])
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
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

---

## Source

**Discovered from**:
- `skills/fdd/tests/` directory
- `skills/fdd/README.md` - Test statistics
- Test file analysis

---

## Validation Checklist

Agent MUST verify before implementation:
- [ ] Tests use `unittest` framework
- [ ] Test files follow `test_*.py` naming
- [ ] Test methods start with `test_`
- [ ] Tests are in `skills/fdd/tests/` directory
- [ ] Tests can run with standard `python3 -m unittest`

**Self-test**:
- [ ] Did I check all criteria?
- [ ] Are test commands correct for this project?
- [ ] Do examples match actual test structure?
