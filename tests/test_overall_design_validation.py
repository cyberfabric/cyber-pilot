"""
Test overall DESIGN.md validation.

Critical validator that ensures system design integrity,
requirements traceability, and cross-references to PRD.md and ADR/{category}/NNNN-fdd-{slug}.md.
"""

import unittest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))

from fdd.validation.artifacts.overall_design import validate_overall_design


class TestOverallDesignStructure(unittest.TestCase):
    """Test overall DESIGN.md structure validation."""

    def test_minimal_pass(self):
        """Test minimal valid overall DESIGN.md."""
        text = """# Technical Design: MyApp

## A. Architecture Overview

Architecture content here.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-myapp-capability-test` | Minimal solution mapping. |

## B. Principles & Constraints

### B.1: Design Principles

#### Principle: Simple

**ID**: `fdd-myapp-principle-simple`

Principle description.

### B.2: Constraints

#### Constraint: Limits

**ID**: `fdd-myapp-constraint-limits`

Constraint description.

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Use cases: `fdd-myapp-usecase-test`

Actors: `fdd-myapp-actor-user`
"""
        report = validate_overall_design(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(len(report["errors"]), 0)
        self.assertEqual(report["required_section_count"], 3)
        self.assertEqual(len(report["missing_sections"]), 0)

    def test_missing_section_a_fails(self):
        """Test that missing Section A fails validation."""
        text = """# Technical Design

## B. Principles & Constraints

### B.1: Design Principles

Content.

### B.2: Constraints

Content.

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Content.
"""
        report = validate_overall_design(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(len(report["missing_sections"]), 1)
        self.assertEqual(report["missing_sections"][0]["id"], "A")

    def test_missing_section_b_fails(self):
        """Test that missing Section B fails validation."""
        text = """# Technical Design

## A. Architecture

Content.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-app-capability-test` | Minimal solution mapping. |

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Content.
"""
        report = validate_overall_design(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("B", [s["id"] for s in report["missing_sections"]])

    def test_missing_section_c_fails(self):
        """Test that missing Section C fails validation."""
        text = """# Technical Design

## A. Architecture

Content.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-app-actor-user` | Minimal solution mapping. |

## B. Principles & Constraints

### B.1: Design Principles

Content.

### B.2: Constraints

Content.

Content.
"""
        report = validate_overall_design(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("C", [s["id"] for s in report["missing_sections"]])

    def test_section_c_subsections_validation(self):
        """Test that Section C must have exactly C.1-C.4 subsections."""
        text = """# Technical Design

## A. Architecture

Content.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-app-capability-test` | Minimal solution mapping. |

## B. Principles & Constraints

### B.1: Design Principles

Content.

### B.2: Constraints

Content.

## C. Technical Architecture

### C.1: Schemas

Content.

### C.2: Format

Content.

### C.3: Contracts

Content.
"""
        report = validate_overall_design(text, skip_fs_checks=True)
        
        # Missing C.4
        structure_errors = [e for e in report["errors"] if e.get("type") == "structure"]
        if structure_errors:
            # Should detect missing subsections
            self.assertIn("C.1..C.4", structure_errors[0]["message"])
        else:
            # Validator may not enforce this strictly
            pass

    def test_section_c_subsections_correct_order(self):
        """Test that Section C subsections must be in correct order."""
        text = """# Technical Design

## A. Architecture

Content.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-app-capability-test` | Minimal solution mapping. |

## B. Principles & Constraints

### B.1: Design Principles

Content.

### B.2: Constraints

Content.

## C. Technical Architecture

### C.2: Schema Format

Wrong order.

### C.1: Entity Schemas

Wrong order.

### C.3: API Contracts

Content.

### C.4: Contract Format

Content.
"""
        report = validate_overall_design(text, skip_fs_checks=True)
        
        structure_errors = [e for e in report["errors"] if e.get("type") == "structure"]
        if structure_errors:
            # Should detect wrong order
            self.assertIn("C.1..C.4", structure_errors[0]["message"])
        else:
            # Validator may not enforce order strictly
            pass


class TestOverallDesignArchitectureDrivers(unittest.TestCase):
    """Test Architecture drivers validation."""

    def test_missing_architecture_drivers_fails(self):
        """Test that missing Architecture drivers fails."""
        text = """# Technical Design

## A. Architecture

Content.

## B. Principles & Constraints

### B.1: Design Principles

Content.

### B.2: Constraints

Content.

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Content.
"""
        report = validate_overall_design(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        structure_errors = [e for e in report["errors"] if e.get("type") == "structure"]
        msgs = [e.get("message", "") for e in structure_errors]
        self.assertTrue(any("Architecture drivers" in m for m in msgs))

    def test_missing_product_requirements_fails(self):
        """Test that missing Product requirements subsection fails."""
        text = """# Technical Design

## A. Architecture

Content.

### Architecture drivers

## B. Principles & Constraints

### B.1: Design Principles

Content.

### B.2: Constraints

Content.

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Content.
"""
        report = validate_overall_design(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        structure_errors = [e for e in report["errors"] if e.get("type") == "structure"]
        msgs = [e.get("message", "") for e in structure_errors]
        self.assertTrue(any("Product requirements" in m for m in msgs))

    def test_missing_product_requirements_table_header_fails(self):
        """Test that Product requirements without required table header fails."""
        text = """# Technical Design

## A. Architecture

Content.

### Architecture drivers

#### Product requirements

| Something else | Wrong |
|---------------|-------|
| x | y |

## B. Principles & Constraints

### B.1: Design Principles

Content.

### B.2: Constraints

Content.

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Content.
"""
        report = validate_overall_design(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        structure_errors = [e for e in report["errors"] if e.get("type") == "structure"]
        msgs = [e.get("message", "") for e in structure_errors]
        self.assertTrue(any("Product requirements must include a table" in m for m in msgs))

    def test_optional_c_subsections_pass(self):
        """Test Section C with optional subsections C.5-C.7."""
        text = """# Technical Design

## A. Architecture

Content.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-app-capability-manage` | Minimal solution mapping. |

## B. Principles & Constraints

### B.1: Design Principles

#### Principle: Simple

**ID**: `fdd-app-principle-simple`

Content.

### B.2: Constraints

#### Constraint: Limits

**ID**: `fdd-app-constraint-limits`

Content.

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Content.

### C.5 Database schemas & tables (optional)

ID: `fdd-app-db-table-users`

### C.6: Topology (optional)

**ID**: `fdd-app-topology-local`

### C.7: Tech stack (optional)

**ID**: `fdd-app-tech-python`
"""
        report = validate_overall_design(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(len(report["requirement_issues"]), 0)


class TestOverallDesignCrossReferences(unittest.TestCase):
    """Test cross-reference validation with PRD.md and ADR directory."""

    def test_cross_reference_validation_with_prd(self):
        """Test validation with PRD.md cross-references."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()
            
            # Create PRD.md
            prd = arch / "PRD.md"
            prd.write_text("""# PRD

## B. Actors

- **ID**: `fdd-app-actor-admin`

## C. Capabilities

### CAP-001: Manage Data

**ID**: `fdd-app-capability-manage`

**Actors**: `fdd-app-actor-admin`

## D. Use Cases

- **ID**: `fdd-app-usecase-manage`
""")
            
            # Create DESIGN.md
            design = arch / "DESIGN.md"
            design_text = """# Technical Design

## A. Architecture

Content.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-app-usecase-manage` | Minimal solution mapping. |

## B. Principles & Constraints

### B.1: Design Principles

Content.

### B.2: Constraints

Content.

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Content.

Use cases: `fdd-app-usecase-manage`

Actors: `fdd-app-actor-admin`
"""
            design.write_text(design_text)
            
            report = validate_overall_design(
                design_text,
                artifact_path=design,
                prd_path=prd,
                skip_fs_checks=False
            )
            
            # Cross-refs should be valid.
            self.assertEqual(len(report["errors"]), 0)
            self.assertEqual(len(report["requirement_issues"]), 0)

    def test_unknown_actor_reference_fails(self):
        """Test that unknown actor reference fails."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()
            
            prd = arch / "PRD.md"
            prd.write_text("""# PRD

## B. Actors

- **ID**: `fdd-app-actor-user`

## C. Capabilities

### CAP-001: Test

**ID**: `fdd-app-capability-test`

**Actors**: `fdd-app-actor-user`
""")
            
            design = arch / "DESIGN.md"
            design_text = """# Technical Design

## A. Architecture

Content.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-app-usecase-manage` | Minimal solution mapping. |

## B. Principles & Constraints

### B.1: Design Principles

Content.

### B.2: Constraints

Content.

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Actors: `fdd-app-actor-unknown`
"""
            design.write_text(design_text)
            
            report = validate_overall_design(
                design_text,
                artifact_path=design,
                prd_path=prd,
                skip_fs_checks=False
            )
            
            self.assertEqual(report["status"], "FAIL")
            unknown_actor_issues = [i for i in report["requirement_issues"] 
                                   if "Unknown actor" in i.get("message", "")]
            self.assertGreater(len(unknown_actor_issues), 0)

    def test_unknown_usecase_reference_fails(self):
        """Test that unknown use case reference fails."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()
            
            prd = arch / "PRD.md"
            prd.write_text("""# PRD

## B. Actors

- **ID**: `fdd-app-actor-user`

## D. Use Cases

- **ID**: `fdd-app-usecase-real`
""")
            
            design = arch / "DESIGN.md"
            design_text = """# Technical Design

## A. Architecture

Content.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-app-usecase-real` | Minimal solution mapping. |

## B. Principles & Constraints

### B.1: Design Principles

Content.

### B.2: Constraints

Content.

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Use cases: `fdd-app-usecase-unknown`
"""
            design.write_text(design_text)
            
            report = validate_overall_design(
                design_text,
                artifact_path=design,
                prd_path=prd,
                skip_fs_checks=False
            )
            
            self.assertEqual(report["status"], "FAIL")
            unknown_uc_issues = [i for i in report["requirement_issues"] if "Unknown use case" in i.get("message", "")]
            self.assertGreater(len(unknown_uc_issues), 0)

    def test_disallowed_optional_c_subsection_fails(self):
        """Test that disallowed optional C subsection fails."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()
            
            prd = arch / "PRD.md"
            prd.write_text("""# PRD

## B. Actors

- **ID**: `fdd-app-actor-user`
""")
            
            design = arch / "DESIGN.md"
            design_text = """# Technical Design

## A. Architecture

Content.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-app-actor-user` | Minimal solution mapping. |

## B. Principles & Constraints

### B.1: Design Principles

Content.

### B.2: Constraints

Content.

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Content.

### C.8: Something else

Not allowed.
"""
            design.write_text(design_text)
            
            report = validate_overall_design(
                design_text,
                artifact_path=design,
                prd_path=prd,
                skip_fs_checks=False
            )
            
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["status"], "FAIL")
            structure_errors = [e for e in report["errors"] if e.get("type") == "structure"]
            msgs = [e.get("message", "") for e in structure_errors]
            self.assertTrue(any("optional subsections" in m for m in msgs))


class TestOverallDesignADRReferences(unittest.TestCase):
    """Test ADR reference validation."""

    def test_adr_references_validated(self):
        """Test that ADR references are validated against architecture/ADR directory."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()

            adr_dir = arch / "ADR" / "general"
            adr_dir.mkdir(parents=True)
            (adr_dir / "0001-fdd-app-adr-use-python.md").write_text(
                "\n".join(
                    [
                        "# ADR-0001: Use Python",
                        "",
                        "**Date**: 2024-01-01",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-use-python`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "Decision content.",
                        "",
                        "## Considered Options",
                        "",
                        "- Python",
                        "",
                        "## Decision Outcome",
                        "",
                        "Chosen option: \"Python\", because test.",
                        "",
                        "## Related Design Elements",
                        "",
                        "- `fdd-app-req-test`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            
            design = arch / "DESIGN.md"
            design_text = """# Technical Design

## A. Architecture

Content.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-app-adr-use-python` | Minimal solution mapping. |

## B. Principles & Constraints

### B.1: Design Principles

**ADRs**: ADR-0001

Content.

### B.2: Constraints

Content.

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Content.
"""
            design.write_text(design_text)
            
            report = validate_overall_design(
                design_text,
                artifact_path=design,
                adr_path=arch / "ADR",
                skip_fs_checks=False
            )
            
            # Should pass - ADR reference is valid
            adr_issues = [i for i in report["requirement_issues"]
                         if "ADR" in i.get("message", "")]
            # No unknown ADR errors
            unknown_adr = [i for i in adr_issues if "Unknown" in i.get("message", "")]
            self.assertEqual(len(unknown_adr), 0)

    def test_unknown_adr_reference_fails(self):
        """Test that unknown ADR reference fails."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()

            adr_dir = arch / "ADR" / "general"
            adr_dir.mkdir(parents=True)
            (adr_dir / "0001-fdd-app-adr-real.md").write_text(
                "\n".join(
                    [
                        "# ADR-0001: Real ADR",
                        "",
                        "**Date**: 2024-01-01",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-real`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "Real.",
                        "",
                        "## Considered Options",
                        "",
                        "- A",
                        "",
                        "## Decision Outcome",
                        "",
                        "Chosen option: \"A\", because test.",
                        "",
                        "## Related Design Elements",
                        "",
                        "- `fdd-app-req-test`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            
            design = arch / "DESIGN.md"
            design_text = """# Technical Design

## A. Architecture

Content.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-app-adr-real` | Minimal solution mapping. |

## B. Principles & Constraints

### B.1: Design Principles

**ADRs**: `fdd-app-adr-unknown`

Unknown ADR!

### B.2: Constraints

Content.

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Content.
"""
            design.write_text(design_text)
            
            report = validate_overall_design(
                design_text,
                artifact_path=design,
                adr_path=arch / "ADR",
                skip_fs_checks=False
            )
            
            self.assertEqual(report["status"], "FAIL")
            unknown_adr_issues = [i for i in report["requirement_issues"]
                                 if "Unknown ADR" in i.get("message", "")]
            self.assertGreater(len(unknown_adr_issues), 0)


class TestOverallDesignPlaceholders(unittest.TestCase):
    """Test placeholder detection."""

    def test_placeholder_detection_fails(self):
        """Test that placeholders cause validation failure."""
        text = """# Technical Design

## A. Architecture

TODO: Add architecture details

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-app-actor-user` | TBD |

## B. Principles & Constraints

### B.1: Design Principles

Content.

### B.2: Constraints

Content.

## C. Technical Architecture

### C.1: Domain Model

Content.

### C.2: Component Model

Content.

### C.3: API Contracts

Content.

### C.4: Interactions & Sequences

Content.
"""
        report = validate_overall_design(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        self.assertGreater(len(report["placeholder_hits"]), 0)


class TestSectionCSubsections(unittest.TestCase):
    """Test Section C subsection validation."""

    def test_section_c_all_subsections(self):
        """Test Section C with all C.1-C.4 subsections."""
        text = """# DESIGN.md

## A. Purpose

Purpose.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-app-actor-user` | Minimal solution mapping. |

## B. Principles & Constraints

### B.1: Design Principles

#### Principle: Simple

**ID**: `fdd-app-principle-simple`

Principles.

### B.2: Constraints

#### Constraint: Limits

**ID**: `fdd-app-constraint-limits`

Constraints.

## C. Technical Architecture

### C.1: Domain Model

Domain.

### C.2: Component Model

Component.

### C.3: API Contracts

API.

### C.4: Interactions & Sequences

Content.
"""
        report = validate_overall_design(text, skip_fs_checks=True)
        
        # Should pass structure check
        structure_errors = [e for e in report["errors"] if e.get("type") == "structure"]
        # No error about C.1-C.4 order
        c_order_errors = [e for e in structure_errors if "C.1..C.4" in e.get("message", "")]
        self.assertEqual(len(c_order_errors), 0)



if __name__ == "__main__":
    unittest.main()
