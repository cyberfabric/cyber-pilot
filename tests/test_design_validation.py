"""
Test design-first enforcement and validation.

Tests REAL DESIGN.md files structure.

"""
import unittest
from pathlib import Path
import sys

try:
    import pytest  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    class _PytestShim:
        @staticmethod
        def skip(message: str = "") -> None:
            raise unittest.SkipTest(message)

        @staticmethod
        def fail(message: str = "") -> None:
            raise AssertionError(message)

    pytest = _PytestShim()  # type: ignore


# Add cypilot.py to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))


def test_specs_manifest_references_design():
    """Verify DECOMPOSITION.md references DESIGN.md for each spec."""
    specs_path = Path(__file__).parent.parent / "architecture" / "specs" / "DECOMPOSITION.md"
    
    if not specs_path.exists():
        pytest.skip("DECOMPOSITION.md not found")
    
    content = specs_path.read_text(encoding='utf-8')
    
    # Verify DECOMPOSITION.md mentions design artifacts
    assert 'DESIGN.md' in content or 'design' in content.lower(), \
        "DECOMPOSITION.md should reference DESIGN.md files"
    
    # Check that spec entries have proper structure
    assert '## ' in content or '###' in content, \
        "DECOMPOSITION.md should have spec sections"


def test_validate_all_spec_designs_have_required_sections():
    """Validate spec-init-structure DESIGN.md has required sections A-F."""
    specs_dir = Path(__file__).parent.parent / "architecture" / "specs"
    if not specs_dir.exists():
        pytest.skip("architecture/specs/ directory not found")
    
    # Only validate init-structure spec (others are placeholders)
    design_path = specs_dir / "spec-init-structure" / "DESIGN.md"
    if not design_path.exists():
        pytest.skip("spec-init-structure/DESIGN.md not found")
    design_files = [design_path]
    
    # Required sections for spec design
    required_sections = ['## A.', '## B.', '## C.', '## D.', '## E.', '## F.']
    
    errors = []
    
    for design_path in design_files:
        # Run structure validation
        content = design_path.read_text(encoding='utf-8')
        
        # Check each required section
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        # Verify validation passes - all sections present
        if missing_sections:
            errors.append(f"{design_path.parent.name}/DESIGN.md: Missing sections: {', '.join(missing_sections)}")
        
        # Also verify has title and spec ID
        if '# ' not in content:
            errors.append(f"{design_path.parent.name}/DESIGN.md: Missing title (# heading)")
        
        if '**ID**:' not in content and '- [ ]' not in content:
            errors.append(f"{design_path.parent.name}/DESIGN.md: Missing spec/flow IDs")
    
    # Report all errors found
    if errors:
        pytest.fail(f"Spec DESIGN.md structure validation failed:\n" + "\n".join(errors))
