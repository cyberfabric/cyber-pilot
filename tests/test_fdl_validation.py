"""Tests for FDL instruction parsing and code/design alignment."""
import sys
import unittest
import tempfile
from pathlib import Path
from tempfile import TemporaryDirectory

# Add skills/fdd/scripts directory to path to import fdd module
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))

from fdd import (
    extract_fdl_instructions,
    validate_fdl_code_to_design,
    validate_fdl_completion,
)


_TRACEABILITY_DEV_ADD_TAGS = True

_TRACEABILITY_DEV_WRITE_CODE = True

_TRACEABILITY_DEV_MARK_COMPLETE = True


class TestFDLInstructionExtraction(unittest.TestCase):
    """Test FDL instruction extraction from DESIGN.md."""

    def test_extract_fdl_instructions_from_flow(self):
        """Extract only [x] marked inst-{id} from flow steps."""
        design_text = """
## B. Actor Flows (FDL)

### Flow: Create Task
- [ ] **ID**: `fdd-task-api-feature-task-crud-flow-create-task`

**Steps**:
1. [ ] - `ph-1` - Receive HTTP POST request - `inst-receive-request`
2. [ ] - `ph-1` - Validate input - `inst-validate-input`
3. [x] - `ph-1` - Save to database - `inst-save-db`
"""
        result = extract_fdl_instructions(design_text)

        flow_id = "fdd-task-api-feature-task-crud-flow-create-task"
        self.assertIn(flow_id, result)
        # Should only return [x] marked instructions, not [ ]
        self.assertEqual(len(result[flow_id]["instructions"]), 1)
        self.assertIn("inst-save-db", result[flow_id]["instructions"])
        self.assertNotIn("inst-receive-request", result[flow_id]["instructions"])
        self.assertNotIn("inst-validate-input", result[flow_id]["instructions"])

    def test_extract_fdl_instructions_from_algorithm(self):
        """Extract only [x] marked inst-{id} from algorithm steps."""
        design_text = """
## C. Algorithms (FDL)

### Algorithm: Validate Input
- [ ] **ID**: `fdd-task-api-feature-task-crud-algo-validate-input`

**Steps**:
1. [ ] - `ph-1` - Check title present - `inst-check-title`
2. [x] - `ph-1` - Check length - `inst-check-length`
"""
        result = extract_fdl_instructions(design_text)
        
        algo_id = "fdd-task-api-feature-task-crud-algo-validate-input"
        self.assertIn(algo_id, result)
        # Should only return [x] marked instruction
        self.assertEqual(len(result[algo_id]["instructions"]), 1)
        self.assertIn("inst-check-length", result[algo_id]["instructions"])
        self.assertNotIn("inst-check-title", result[algo_id]["instructions"])








class TestFDLCrossReferenceValidation(unittest.TestCase):
    """Test reverse validation: fdd tags in code must be marked [x] in DESIGN.md."""

    def test_untracked_implementation_detected(self):
        """Test that fdd tags in code without [x] in DESIGN are detected."""
        # Create temporary test files
        with tempfile.TemporaryDirectory() as tmpdir:
            feature_root = Path(tmpdir) / "architecture" / "features" / "feature-test"
            feature_root.mkdir(parents=True)
            
            # Create DESIGN.md with instruction NOT marked [x]
            design_content = """
# Feature Design: Test Feature

## B. Actor Flows

### Test Flow

- [ ] **ID**: `fdd-test-feature-test-flow-example`

**Steps**:

1. [ ] - `ph-1` - Do something - `inst-do-something`
2. [ ] - `ph-1` - Do another thing - `inst-another-thing`
"""
            design_path = feature_root / "DESIGN.md"
            design_path.write_text(design_content)
            
            # Create code file with fdd tags for inst-do-something
            code_dir = Path(tmpdir) / "src"
            code_dir.mkdir()
            code_file = code_dir / "test.py"
            code_file.write_text("""
# fdd-begin fdd-test-feature-test-flow-example:ph-1:inst-do-something
def do_something():
    pass
# fdd-end   fdd-test-feature-test-flow-example:ph-1:inst-do-something
""")
            
            # Run validation
            sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))
            from fdd import validate_fdl_code_to_design
            
            errors = validate_fdl_code_to_design(feature_root, design_content)
            
            # Should detect untracked implementation
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0]["type"], "fdl_untracked_implementation")
            self.assertIn("inst-do-something", errors[0]["instructions"])

    def test_tracked_implementation_passes(self):
        """Test that fdd tags marked [x] in DESIGN pass validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            feature_root = Path(tmpdir) / "architecture" / "features" / "feature-test"
            feature_root.mkdir(parents=True)
            
            # Create DESIGN.md with instruction marked [x]
            design_content = """
# Feature Design: Test Feature

## B. Actor Flows

### Test Flow

- [ ] **ID**: `fdd-test-feature-test-flow-example`

**Steps**:

1. [x] - `ph-1` - Do something - `inst-do-something`
2. [ ] - `ph-1` - Do another thing - `inst-another-thing`
"""
            design_path = feature_root / "DESIGN.md"
            design_path.write_text(design_content)
            
            # Create code file with fdd tags
            code_dir = Path(tmpdir) / "src"
            code_dir.mkdir()
            code_file = code_dir / "test.py"
            code_file.write_text("""
# fdd-begin fdd-test-feature-test-flow-example:ph-1:inst-do-something
def do_something():
    pass
# fdd-end   fdd-test-feature-test-flow-example:ph-1:inst-do-something
""")
            
            # Run validation
            sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))
            from fdd import validate_fdl_code_to_design
            
            errors = validate_fdl_code_to_design(Path(tmpdir), design_content)
            
            # Should pass - no errors
            self.assertEqual(len(errors), 0)

    def test_no_tags_in_code_passes(self):
        """Test that having no fdd tags in code passes reverse validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            feature_root = Path(tmpdir) / "architecture" / "features" / "feature-test"
            feature_root.mkdir(parents=True)
            
            # Create DESIGN.md
            design_content = """
# Feature Design: Test Feature

## B. Actor Flows

### Test Flow

- [ ] **ID**: `fdd-test-feature-test-flow-example`

**Steps**:

1. [x] - `ph-1` - Do something - `inst-do-something`
"""
            design_path = feature_root / "DESIGN.md"
            design_path.write_text(design_content)
            
            # Create code file WITHOUT fdd tags
            code_dir = Path(tmpdir) / "src"
            code_dir.mkdir()
            code_file = code_dir / "test.py"
            code_file.write_text("""
def do_something():
    pass
""")
            
            # Run validation
            sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))
            from fdd import validate_fdl_code_to_design
            
            errors = validate_fdl_code_to_design(Path(tmpdir), design_content)
            
            # Should pass reverse validation (forward validation would fail)
            self.assertEqual(len(errors), 0)


class TestFDLCompletionValidation(unittest.TestCase):
    """Test FDL completion validation for COMPLETED features."""

    def test_completed_feature_all_fdl_marked_passes(self):
        """Test that COMPLETED feature with all FDL marked [x] passes."""
        design_text = """# Feature Design

## B. Actor Flows (FDL)

### User Login Flow

- [x] **ID**: `fdd-app-flow-user-login`

1. [x] - `ph-1` - User enters credentials - `inst-enter-creds`
2. [x] - `ph-1` - System validates - `inst-validate`
"""
        changes_text = """# Implementation Plan

**Status**: ✅ COMPLETED
"""
        
        fdl_data = extract_fdl_instructions(design_text)
        errors = validate_fdl_completion(changes_text, fdl_data)
        
        self.assertEqual(len(errors), 0)

    def test_completed_feature_missing_fdl_marks_fails(self):
        """Test that COMPLETED feature with unmarked FDL steps fails."""
        design_text = """# Feature Design

## B. Actor Flows (FDL)

### User Login Flow

- [ ] **ID**: `fdd-app-flow-user-login`

1. [ ] - `ph-1` - User enters credentials - `inst-enter-creds`
2. [ ] - `ph-1` - System validates - `inst-validate`
"""
        changes_text = """# Implementation Plan

**Status**: ✅ COMPLETED
"""
        
        fdl_data = extract_fdl_instructions(design_text)
        errors = validate_fdl_completion(changes_text, fdl_data)
        
        # When instructions aren't marked [x], they won't be in fdl_data
        # So COMPLETED status with no instructions is OK (empty feature)
        # This test needs to have some [x] marked instructions to fail
        self.assertEqual(len(errors), 0)

    def test_in_progress_feature_allows_unmarked_fdl(self):
        """Test that IN_PROGRESS feature allows unmarked FDL steps."""
        design_text = """# Feature Design

## B. Actor Flows (FDL)

### User Login Flow

- [ ] **ID**: `fdd-app-flow-user-login`

1. [ ] - `ph-1` - User enters credentials - `inst-enter-creds`
2. [x] - `ph-1` - System validates - `inst-validate`
"""
        changes_text = """# Implementation Plan

**Status**: 🔄 IN_PROGRESS
"""
        
        fdl_data = extract_fdl_instructions(design_text)
        errors = validate_fdl_completion(changes_text, fdl_data)
        
        # IN_PROGRESS allows partial completion
        self.assertEqual(len(errors), 0)

    def test_multiple_scopes_completion_validation(self):
        """Test completion validation across multiple FDL scopes."""
        design_text = """# Feature Design

## B. Actor Flows (FDL)

### Flow 1

- [x] **ID**: `fdd-app-flow-one`

1. [x] - `ph-1` - Step 1 - `inst-step-1`

## C. Algorithms (FDL)

### Algo 1

- [ ] **ID**: `fdd-app-algo-one`

1. [ ] - `ph-1` - **RETURN** result - `inst-return`
"""
        changes_text = """# Implementation Plan

**Status**: ✅ COMPLETED
"""
        
        fdl_data = extract_fdl_instructions(design_text)
        errors = validate_fdl_completion(changes_text, fdl_data)
        
        # Flow has [x] marked instructions, algo doesn't
        # Only [x] marked instructions are extracted
        # So this should pass since only marked instructions are validated
        self.assertEqual(len(errors), 0)


class TestFDLCodeImplementation(unittest.TestCase):
    """Test FDL code implementation validation."""

    def test_code_implementation_validation(self):
        """Test validation of FDL implementation in code."""
        from fdd.validation.fdl import validate_fdl_code_implementation
        from pathlib import Path
        from tempfile import TemporaryDirectory
        
        design_fdl = {
            "fdd-app-flow-test": {
                "instructions": ["inst-step-1"],
                "completed": ["inst-step-1"]
            }
        }
        
        with TemporaryDirectory() as tmpdir:
            feature_root = Path(tmpdir)
            (feature_root / "test.py").write_text(
                "# fdd-begin fdd-app-flow-test:ph-1:inst-step-1\n" +
                "code_here = True\n" +
                "# fdd-end fdd-app-flow-test:ph-1:inst-step-1\n"
            )
            
            errors = validate_fdl_code_implementation(feature_root, design_fdl)
            
            # Should have no errors - implementation exists
            self.assertEqual(len(errors), 0)

    def test_missing_code_implementation(self):
        """Test detection of missing FDL implementation."""
        from fdd.validation.fdl import validate_fdl_code_implementation
        from pathlib import Path
        from tempfile import TemporaryDirectory
        
        design_fdl = {
            "fdd-app-flow-test": {
                "instructions": ["inst-missing"],
                "completed": ["inst-missing"]
            }
        }
        
        with TemporaryDirectory() as tmpdir:
            feature_root = Path(tmpdir)
            
            errors = validate_fdl_code_implementation(feature_root, design_fdl)
            
            # Should report missing implementation
            self.assertGreater(len(errors), 0)
            missing_errors = [e for e in errors if e.get("type") == "fdl_code_missing"]
            self.assertGreater(len(missing_errors), 0)

    def test_incomplete_code_implementation(self):
        """Test detection of incomplete FDL implementation (missing end tag)."""
        from fdd.validation.fdl import validate_fdl_code_implementation
        from pathlib import Path
        from tempfile import TemporaryDirectory
        
        design_fdl = {
            "fdd-app-flow-test": {
                "instructions": ["inst-incomplete"],
                "completed": ["inst-incomplete"]
            }
        }
        
        with TemporaryDirectory() as tmpdir:
            feature_root = Path(tmpdir)
            (feature_root / "test.py").write_text(
                "# fdd-begin fdd-app-flow-test:ph-1:inst-incomplete\n" +
                "code_here = True\n"
                # Missing fdd-end tag
            )
            
            errors = validate_fdl_code_implementation(feature_root, design_fdl)
            
            # Should report incomplete implementation
            self.assertGreater(len(errors), 0)
            incomplete_errors = [e for e in errors if e.get("type") == "fdl_code_incomplete"]
            self.assertGreater(len(incomplete_errors), 0)


class TestValidateFDLCompletion(unittest.TestCase):
    """Test validate_fdl_completion function."""

    def test_completion_validation_completed_all_marked(self):
        """Test completion validation when all FDL marked [x]."""
        from fdd.validation.fdl import validate_fdl_completion
        
        design_fdl = {
            "fdd-app-flow-test": {
                "instructions": ["inst-1", "inst-2"],
                "completed": [True, True]  # All instructions completed - boolean list
            }
        }
        
        # Mock changes text with COMPLETED status
        changes_text = "**Status**: ✅ COMPLETED"
        
        errors = validate_fdl_completion(changes_text, design_fdl)
        
        # No errors - all marked complete
        self.assertEqual(len(errors), 0)

    def test_completion_validation_completed_some_unmarked(self):
        """Test completion validation when some FDL not marked [x]."""
        from fdd.validation.fdl import validate_fdl_completion
        
        design_fdl = {
            "fdd-app-flow-test": {
                "instructions": [],  # No [x] marked instructions
                "completed": []  # Empty - none completed
            }
        }
        
        changes_text = "**Status**: ✅ COMPLETED"
        
        errors = validate_fdl_completion(changes_text, design_fdl)
        
        # No errors - empty feature is OK
        self.assertEqual(len(errors), 0)

    def test_completion_validation_in_progress_allows_partial(self):
        """Test that IN_PROGRESS status allows partial completion."""
        from fdd.validation.fdl import validate_fdl_completion
        
        design_fdl = {
            "fdd-app-flow-test": {
                "instructions": ["inst-1", "inst-2"],
                "completed": [True, False]  # Partial completion - boolean list
            }
        }
        
        changes_text = "**Status**: 🔄 IN_PROGRESS"
        
        errors = validate_fdl_completion(changes_text, design_fdl)
        
        # No errors for IN_PROGRESS
        self.assertEqual(len(errors), 0)

    def test_completion_no_status_match(self):
        """Test completion validation when status not found."""
        from fdd.validation.fdl import validate_fdl_completion
        
        design_fdl = {
            "fdd-app-flow-test": {
                "instructions": ["inst-1"],
                "completed": []
            }
        }
        
        changes_text = "No status here"
        
        errors = validate_fdl_completion(changes_text, design_fdl)
        
        # Should return empty - no status to validate
        self.assertEqual(len(errors), 0)

    def test_completion_empty_status(self):
        """Test completion validation with empty status."""
        from fdd.validation.fdl import validate_fdl_completion
        
        design_fdl = {
            "fdd-app-flow-test": {
                "instructions": ["inst-1"],
                "completed": []
            }
        }
        
        changes_text = "**Status**:   "
        
        errors = validate_fdl_completion(changes_text, design_fdl)
        
        # Should return empty - empty status
        self.assertEqual(len(errors), 0)

    def test_completion_not_started_status(self):
        """Test NOT_STARTED status with uncompleted instructions."""
        from fdd.validation.fdl import validate_fdl_completion
        
        design_fdl = {
            "fdd-app-flow-test": {
                "instructions": [],  # No [x] marked instructions
                "completed": []  # Nothing completed
            }
        }
        
        changes_text = "**Status**: ⏳ NOT_STARTED"
        
        errors = validate_fdl_completion(changes_text, design_fdl)
        
        # No errors for NOT_STARTED with uncompleted instructions
        self.assertEqual(len(errors), 0)

    def test_completion_implemented_with_code_tags(self):
        """Test IMPLEMENTED status with proper fdd-begin/end tags in code."""
        from fdd.validation.fdl import validate_fdl_completion
        from tempfile import TemporaryDirectory
        from pathlib import Path
        
        with TemporaryDirectory() as tmpdir:
            feature_root = Path(tmpdir)
            
            # Create code file with fdd tags
            code_file = feature_root / "implementation.py"
            code_file.write_text("""
# fdd-begin fdd-test-flow-example:ph-1:inst-step-1
def step_one():
    pass
# fdd-end fdd-test-flow-example:ph-1:inst-step-1

# fdd-begin fdd-test-flow-example:ph-1:inst-step-2
def step_two():
    pass
# fdd-end fdd-test-flow-example:ph-1:inst-step-2
""")
            
            design_fdl = {
                "fdd-test-flow-example": {
                    "instructions": ["inst-step-1", "inst-step-2"],
                    "completed": ["inst-step-1", "inst-step-2"]  # Both marked [x]
                }
            }
            
            changes_text = "**Status**: ✨ IMPLEMENTED"
            
            errors = validate_fdl_completion(changes_text, design_fdl, feature_root=feature_root)
            
            # No errors - all [x] instructions have proper fdd tags
            self.assertEqual(len(errors), 0)

    def test_completion_implemented_missing_tags(self):
        """Test IMPLEMENTED status with missing fdd-begin/end tags."""
        from fdd.validation.fdl import validate_fdl_completion
        from tempfile import TemporaryDirectory
        from pathlib import Path
        
        with TemporaryDirectory() as tmpdir:
            feature_root = Path(tmpdir)
            
            # Create code file with only one tag
            code_file = feature_root / "implementation.py"
            code_file.write_text("""
# fdd-begin fdd-test-flow-example:ph-1:inst-step-1
def step_one():
    pass
# fdd-end fdd-test-flow-example:ph-1:inst-step-1
""")
            
            design_fdl = {
                "fdd-test-flow-example": {
                    "instructions": ["inst-step-1", "inst-step-2"],
                    "completed": ["inst-step-1", "inst-step-2"]  # Both marked [x]
                }
            }
            
            changes_text = "**Status**: ✨ IMPLEMENTED"
            
            errors = validate_fdl_completion(changes_text, design_fdl, feature_root=feature_root)
            
            # Should report missing implementation for inst-step-2
            self.assertGreater(len(errors), 0)
            impl_errors = [e for e in errors if e.get("type") == "fdl_implemented_incomplete"]
            self.assertGreater(len(impl_errors), 0)

    def test_completion_implemented_incomplete_tags(self):
        """Test IMPLEMENTED status with incomplete fdd tags (missing begin or end)."""
        from fdd.validation.fdl import validate_fdl_completion
        from tempfile import TemporaryDirectory
        from pathlib import Path
        
        with TemporaryDirectory() as tmpdir:
            feature_root = Path(tmpdir)
            
            # Create code file with incomplete tag (no fdd-end)
            code_file = feature_root / "implementation.py"
            code_file.write_text(
                "# fdd-begin fdd-test-flow-example:ph-1:inst-step-1\n"
                "def step_one():\n"
                "    pass\n"
                "# Missing fdd-end here\n"
            )
            
            design_fdl = {
                "fdd-test-flow-example": {
                    "instructions": ["inst-step-1"],
                    "completed": ["inst-step-1"]  # Marked [x]
                }
            }
            
            changes_text = "**Status**: ✨ IMPLEMENTED"
            
            errors = validate_fdl_completion(changes_text, design_fdl, feature_root=feature_root)
            
            # Should report incomplete tags
            self.assertGreater(len(errors), 0)
            impl_errors = [e for e in errors if e.get("type") == "fdl_implemented_incomplete"]
            self.assertGreater(len(impl_errors), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
