"""
Test workflow file parsing and structure validation.

Tests REAL workflow files from workflows/ directory.

"""
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

    # Test generate.md workflow (main generation workflow with phases)
    workflow_path = workflows_dir / "generate.md"
    assert workflow_path.exists(), f"{workflow_path} not found"

    content = workflow_path.read_text(encoding='utf-8')

    # generate.md uses phase-based structure with Prerequisite checks
    has_prerequisites = 'Prerequisite' in content
    has_phases = '## Phase' in content

    assert has_prerequisites, f"{workflow_path.name}: Prerequisite section not found"
    assert has_phases, f"{workflow_path.name}: Phase section not found"
    assert '**Type**:' in content, f"{workflow_path.name}: Type metadata not found"


def test_validate_all_workflows_have_required_structure():
    """Validate ALL workflow files have required sections."""
    workflows_dir = Path(__file__).parent.parent / "workflows"
    assert workflows_dir.exists(), "workflows/ directory not found"

    # Get all workflow markdown files, excluding non-workflow files
    all_files = list(workflows_dir.glob("*.md"))
    # Exclude non-workflow files
    exclude_files = {'README.md', 'AGENTS.md'}
    workflow_files = [f for f in all_files if f.name not in exclude_files]
    assert len(workflow_files) > 0, "No workflow files found"

    errors = []

    for workflow_path in workflow_files:
        content = workflow_path.read_text(encoding='utf-8')

        # All workflows must have **Type**: metadata
        if '**Type**:' not in content:
            errors.append(f"{workflow_path.name}: Missing **Type**: metadata")

        # All workflows must have some form of steps/phases
        has_steps = any(s in content for s in ['## Steps', '## Step', '## Phase'])
        if not has_steps:
            errors.append(f"{workflow_path.name}: Missing Steps/Phase section")

        # All workflows must have fdd: true frontmatter
        if 'fdd: true' not in content:
            errors.append(f"{workflow_path.name}: Missing fdd: true frontmatter")

    if errors:
        pytest.fail(f"Workflow structure validation failed:\n" + "\n".join(errors))


def test_generate_workflow_has_template_resolution():
    """Verify generate.md workflow has template resolution logic."""
    workflows_dir = Path(__file__).parent.parent / "workflows"
    workflow_path = workflows_dir / "generate.md"
    assert workflow_path.exists(), f"{workflow_path} not found"

    content = workflow_path.read_text(encoding="utf-8")

    # generate.md should have template-related content
    assert "template" in content.lower(), "generate.md should reference templates"
    assert "artifact" in content.lower(), "generate.md should reference artifacts"
    # generate.md uses Phase structure instead of Steps
    assert "## Phase" in content, "generate.md should use Phase structure"
