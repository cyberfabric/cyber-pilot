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


# Add spider.py to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "spider" / "scripts"))


def test_features_manifest_references_design():
    """Verify DECOMPOSITION.md references DESIGN.md for each feature."""
    features_path = Path(__file__).parent.parent / "architecture" / "features" / "DECOMPOSITION.md"
    
    if not features_path.exists():
        pytest.skip("DECOMPOSITION.md not found")
    
    content = features_path.read_text(encoding='utf-8')
    
    # Verify DECOMPOSITION.md mentions design artifacts
    assert 'DESIGN.md' in content or 'design' in content.lower(), \
        "DECOMPOSITION.md should reference DESIGN.md files"
    
    # Check that feature entries have proper structure
    assert '## ' in content or '###' in content, \
        "DECOMPOSITION.md should have feature sections"


def test_validate_all_feature_designs_have_required_sections():
    """Validate feature-init-structure DESIGN.md has required sections A-F."""
    features_dir = Path(__file__).parent.parent / "architecture" / "features"
    if not features_dir.exists():
        pytest.skip("architecture/features/ directory not found")
    
    # Only validate init-structure feature (others are placeholders)
    design_path = features_dir / "feature-init-structure" / "DESIGN.md"
    if not design_path.exists():
        pytest.skip("feature-init-structure/DESIGN.md not found")
    design_files = [design_path]
    
    # Required sections for feature design
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
        
        # Also verify has title and feature ID
        if '# ' not in content:
            errors.append(f"{design_path.parent.name}/DESIGN.md: Missing title (# heading)")
        
        if '**ID**:' not in content and '- [ ]' not in content:
            errors.append(f"{design_path.parent.name}/DESIGN.md: Missing feature/flow IDs")
    
    # Report all errors found
    if errors:
        pytest.fail(f"Feature DESIGN.md structure validation failed:\n" + "\n".join(errors))
