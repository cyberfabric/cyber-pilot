"""
Test workflow file parsing and structure validation.

Tests REAL workflow files from workflows/ directory.

"""
import unittest
 
try:
    import pytest  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    class _PytestShim:
        @staticmethod
        def fail(message: str = "") -> None:
            raise AssertionError(message)
 
    pytest = _PytestShim()  # type: ignore
from pathlib import Path


def test_parse_workflow_extracts_all_sections():
    """Parse REAL workflow files and verify structure."""
    workflows_dir = Path(__file__).parent.parent / "workflows"
    assert workflows_dir.exists(), "workflows/ directory not found"
    
    # Test prd.md workflow
    workflow_path = workflows_dir / "prd.md"
    assert workflow_path.exists(), f"{workflow_path} not found"
    
    # Load workflow file
    content = workflow_path.read_text(encoding='utf-8')
    
    # Extract required sections
    has_prerequisites = '## Prerequisites' in content
    has_steps = '## Steps' in content or '## Step' in content
    has_validation = '## Validation' in content
    
    # Verify all sections extracted successfully
    assert has_prerequisites, f"{workflow_path.name}: Prerequisites section not found"
    assert has_steps, f"{workflow_path.name}: Steps section not found"
    assert has_validation, f"{workflow_path.name}: Validation section not found"
    
    # Verify workflow has Type and Role metadata
    assert '**Type**:' in content, f"{workflow_path.name}: Type metadata not found"
    assert '**Role**:' in content, f"{workflow_path.name}: Role metadata not found"


def test_validate_all_workflows_have_required_structure():
    """Validate ALL workflow files have required sections."""
    workflows_dir = Path(__file__).parent.parent / "workflows"
    assert workflows_dir.exists(), "workflows/ directory not found"
    
    # Get all workflow markdown files, excluding non-workflow files
    all_files = list(workflows_dir.glob("*.md"))
    exclude_files = {'README.md', 'AGENTS.md', 'adapter.md'}
    workflow_files = [f for f in all_files if f.name not in exclude_files]
    assert len(workflow_files) > 0, "No workflow files found"
    
    required_sections = ['## Prerequisites', '## Steps', '## Validation']
    required_metadata = ['**Type**:', '**Role**:']
    
    errors = []
    
    for workflow_path in workflow_files:
        # Run structure validation on each workflow
        content = workflow_path.read_text(encoding='utf-8')
        
        # Check for required sections
        missing_sections = []
        for section in required_sections:
            # Allow variations like "## Step" or "## Steps"
            if section == '## Steps':
                if '## Steps' not in content and '## Step' not in content:
                    missing_sections.append(section)
            elif section not in content:
                missing_sections.append(section)
        
        # Check for required metadata
        missing_metadata = [m for m in required_metadata if m not in content]
        
        # Report errors for this workflow
        if missing_sections:
            errors.append(f"{workflow_path.name}: Missing sections: {', '.join(missing_sections)}")
        if missing_metadata:
            errors.append(f"{workflow_path.name}: Missing metadata: {', '.join(missing_metadata)}")
    
    # Verify validation passes for all workflows
    if errors:
        pytest.fail(f"Workflow structure validation failed:\n" + "\n".join(errors))
