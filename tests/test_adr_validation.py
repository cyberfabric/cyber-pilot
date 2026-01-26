"""
Test ADR validation.

Critical validator for architectural decision records.
Ensures proper structure, metadata, required sections, and cross-references.
"""

import unittest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest.mock

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))

from fdd.validation.artifacts.adr import validate_adr


class TestADRStructure(unittest.TestCase):
    def _single_adr_text(
        self,
        *,
        num: int = 1,
        title: str = "Test",
        date: str | None = "2024-01-15",
        status: str | None = "Accepted",
        adr_id: str | None = "fdd-app-adr-test",
        include_context: bool = True,
        include_options: bool = True,
        include_outcome: bool = True,
        include_related: bool = True,
        chosen_option: bool = True,
        related_lines: list[str] | None = None,
    ) -> str:
        nnnn = f"{num:04d}"
        lines: list[str] = [f"# ADR-{nnnn}: {title}", ""]
        if date is not None:
            lines.extend([f"**Date**: {date}", ""])
        if status is not None:
            lines.extend([f"**Status**: {status}", ""])
        if adr_id is not None:
            lines.extend([f"**ADR ID**: `{adr_id}`", ""])

        if include_context:
            lines.extend(["## Context and Problem Statement", "", "Context.", ""])
        if include_options:
            lines.extend(["## Considered Options", "", "- A", ""])
        if include_outcome:
            lines.extend(["## Decision Outcome", ""])
            if chosen_option:
                lines.extend(["Chosen option: \"A\", because test.", ""])
            else:
                lines.extend(["Outcome.", ""])
        if include_related:
            lines.extend(["## Related Design Elements", ""])
            if related_lines is None:
                related_lines = ["- `fdd-app-req-test`"]
            lines.extend(related_lines)
            lines.append("")

        return "\n".join(lines)

    def test_minimal_valid_single_record_passes(self):
        text = self._single_adr_text()
        report = validate_adr(text, skip_fs_checks=True)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(len(report["errors"]), 0)
        self.assertEqual(len(report["adr_issues"]), 0)

    def test_missing_date_fails(self):
        text = self._single_adr_text(date=None)
        report = validate_adr(text, skip_fs_checks=True)
        self.assertEqual(report["status"], "FAIL")
        date_issues = [i for i in report["adr_issues"] if "Date" in i.get("message", "")]
        self.assertGreater(len(date_issues), 0)

    def test_missing_status_fails(self):
        text = self._single_adr_text(status=None)
        report = validate_adr(text, skip_fs_checks=True)
        self.assertEqual(report["status"], "FAIL")
        status_issues = [i for i in report["adr_issues"] if "Status" in i.get("message", "")]
        self.assertGreater(len(status_issues), 0)

    def test_missing_adr_id_fails(self):
        text = self._single_adr_text(adr_id=None)
        report = validate_adr(text, skip_fs_checks=True)
        self.assertEqual(report["status"], "FAIL")
        id_issues = [i for i in report["adr_issues"] if "ADR ID" in i.get("message", "")]
        self.assertGreater(len(id_issues), 0)

    def test_missing_chosen_option_fails(self):
        text = self._single_adr_text(chosen_option=False)
        report = validate_adr(text, skip_fs_checks=True)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("Chosen option" in str(i.get("message")) for i in report.get("adr_issues", [])))

    def test_related_elements_requires_id(self):
        text = self._single_adr_text(related_lines=["No IDs here."])
        report = validate_adr(text, skip_fs_checks=True)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("Related Design Elements" in str(i.get("message")) for i in report.get("adr_issues", [])))


class TestADRDirectoryMode(unittest.TestCase):
    def test_directory_mode_skips_entry_without_path(self):
        from fdd.validation.artifacts import adr as adr_mod

        with TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            with unittest.mock.patch.object(adr_mod, "load_adr_entries", return_value=([{"ref": "ADR-0001"}], [])):
                report = adr_mod.validate_adr("", artifact_path=td, skip_fs_checks=True)
        self.assertIn(report.get("status"), ("PASS", "FAIL"))

    def test_directory_mode_read_failure_adds_issue(self):
        from fdd.validation.artifacts import adr as adr_mod

        with TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            bad_path = td / "0001-fdd-app-adr-x.md"

            def _raise(_self, *a, **k):
                raise OSError("nope")

            with unittest.mock.patch.object(adr_mod, "load_adr_entries", return_value=([{"ref": "ADR-0001", "path": str(bad_path)}], [])):
                with unittest.mock.patch.object(Path, "read_text", _raise):
                    report = adr_mod.validate_adr("", artifact_path=td, skip_fs_checks=True)

        self.assertEqual(report.get("status"), "FAIL")
        self.assertTrue(any("Failed to read ADR file" in str(i.get("message")) for i in report.get("adr_issues", [])))

    def test_directory_mode_requires_h1(self):
        from fdd.validation.artifacts import adr as adr_mod

        with TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            f = td / "0001-fdd-app-adr-x.md"
            f.write_text(
                "\n".join(
                    [
                        "## ADR-0001: X",
                        "",
                        "**Date**: 2025-01-01",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-x`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "X",
                        "",
                        "## Considered Options",
                        "",
                        "- X",
                        "",
                        "## Decision Outcome",
                        "",
                        "Chosen option: \"X\", because X.",
                        "",
                        "## Related Design Elements",
                        "",
                        "- `fdd-app-req-x`",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with unittest.mock.patch.object(
                adr_mod,
                "load_adr_entries",
                return_value=([{"ref": "ADR-0001", "path": str(f)}], []),
            ):
                report = adr_mod.validate_adr("", artifact_path=td, skip_fs_checks=True)

        self.assertEqual(report.get("status"), "FAIL")
        self.assertTrue(any("exactly one H1" in str(i.get("message")) for i in report.get("adr_issues", [])))


class TestADRAdditionalBranches(unittest.TestCase):
    def test_missing_adr_id_fails(self):
        text = """# ADR-0001: X

**Date**: 2025-01-01

**Status**: Accepted

## Context and Problem Statement

X

## Considered Options

- X

## Decision Outcome

Chosen option: "X", because X.

## Related Design Elements

- `fdd-app-req-x`
"""
        report = validate_adr(text, skip_fs_checks=True)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("ADR ID" in str(i.get("message")) for i in report.get("adr_issues", [])))

    def test_single_record_missing_metadata_and_sections(self):
        text = """# ADR-0001: X

**Date**: 2025-01-01

**ADR ID**: `fdd-app-adr-x`

## Context and Problem Statement

X

## Considered Options

- X

## Related Design Elements

- `fdd-app-req-x`
"""
        report = validate_adr(text, skip_fs_checks=True)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("Status" in str(i.get("message")) for i in report.get("adr_issues", [])))
        self.assertFalse(any("ADR ID" in str(i.get("message")) for i in report.get("adr_issues", [])))
        self.assertTrue(any("Decision Outcome" in str(i.get("message")) for i in report.get("adr_issues", [])))

    def test_single_record_related_elements_without_ids(self):
        text = """# ADR-0001: X

**Date**: 2025-01-01
**Status**: Accepted
**ADR ID**: `fdd-app-adr-x`

## Context and Problem Statement

X

## Considered Options

- X

## Decision Outcome

X

## Related Design Elements

No IDs here.
"""
        report = validate_adr(text, skip_fs_checks=True)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("at least one ID" in str(i.get("message")) for i in report.get("adr_issues", [])))

    def test_single_record_unknown_ids_with_fs_checks(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            arch = root / "architecture"
            arch.mkdir()

            prd = arch / "PRD.md"
            prd.write_text(
                "\n".join(
                    [
                        "# PRD",
                        "",
                        "## B. Actors",
                        "",
                        "- **ID**: `fdd-app-actor-user`",
                        "",
                        "## C. Capabilities",
                        "",
                        "- **ID**: `fdd-app-capability-login`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            design = arch / "DESIGN.md"
            design.write_text(
                "\n".join(
                    [
                        "# Technical Design",
                        "",
                        "## B. Requirements",
                        "",
                        "- **ID**: `fdd-app-req-auth`",
                        "",
                        "## C. Principles",
                        "",
                        "- **ID**: `fdd-app-principle-secure`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            adr_dir = arch / "ADR" / "general"
            adr_dir.mkdir(parents=True)
            adr_file = adr_dir / "0001-fdd-app-adr-x.md"
            adr_file.write_text(
                "\n".join(
                    [
                        "# ADR-0001: X",
                        "",
                        "**Date**: 2025-01-01",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-x`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "X",
                        "",
                        "## Considered Options",
                        "",
                        "- X",
                        "",
                        "## Decision Outcome",
                        "",
                        "Chosen option: \"X\", because X.",
                        "",
                        "## Related Design Elements",
                        "",
                        "- `fdd-app-actor-unknown`",
                        "- `fdd-app-capability-unknown`",
                        "- `fdd-app-req-unknown`",
                        "- `fdd-app-principle-unknown`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            report = validate_adr(
                "",
                artifact_path=arch / "ADR",
                prd_path=prd,
                design_path=design,
                skip_fs_checks=False,
            )

        self.assertEqual(report["status"], "FAIL")
        msgs = [str(i.get("message")) for i in report.get("adr_issues", [])]
        self.assertTrue(any("Unknown actor" in m for m in msgs))
        self.assertTrue(any("Unknown PRD IDs" in m for m in msgs))
        self.assertTrue(any("Unknown requirement" in m for m in msgs))
        self.assertTrue(any("Unknown principle" in m for m in msgs))

    def test_invalid_status_value_fails(self):
        """Test that invalid status value fails."""
        text = """# ADR-0001: Test Decision

**Date**: 2024-01-15

**Status**: Invalid

**ADR ID**: `fdd-app-adr-test`

## Context and Problem Statement

Context.

## Considered Options

- Option A

## Decision Outcome

Chosen option: "A", because test.

## Related Design Elements

- `fdd-app-req-test`
"""
        report = validate_adr(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        # Invalid status should be caught
        status_issues = [i for i in report["adr_issues"] if "Status" in i.get("message", "")]
        self.assertGreater(len(status_issues), 0)


class TestADRRequiredSections(unittest.TestCase):
    """Test ADR required sections validation."""

    def test_missing_context_section_fails(self):
        """Test that missing Context section fails."""
        text = """# ADR-0001: Test Decision

**Date**: 2024-01-15

**Status**: Accepted

**ADR ID**: `fdd-app-adr-test`

## Considered Options

- Option A

## Decision Outcome

Chosen option: "A", because test.

## Related Design Elements

- `fdd-app-req-test`
"""
        report = validate_adr(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        section_issues = [i for i in report["adr_issues"] 
                         if "Context and Problem Statement" in i.get("message", "")]
        self.assertGreater(len(section_issues), 0)

    def test_missing_options_section_fails(self):
        """Test that missing Considered Options section fails."""
        text = """# ADR-0001: Test Decision

**Date**: 2024-01-15

**Status**: Accepted

**ADR ID**: `fdd-app-adr-test`

## Context and Problem Statement

Context.

## Decision Outcome

Chosen option: "A", because test.

## Related Design Elements

- `fdd-app-req-test`
"""
        report = validate_adr(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        section_issues = [i for i in report["adr_issues"] if "Considered Options" in i.get("message", "")]
        self.assertGreater(len(section_issues), 0)

    def test_missing_outcome_section_fails(self):
        """Test that missing Decision Outcome section fails."""
        text = """# ADR-0001: Test Decision

**Date**: 2024-01-15

**Status**: Accepted

**ADR ID**: `fdd-app-adr-test`

## Context and Problem Statement

Context.

## Considered Options

- Option A

## Related Design Elements

- `fdd-app-req-test`
"""
        report = validate_adr(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        section_issues = [i for i in report["adr_issues"]
                         if "Decision Outcome" in i.get("message", "")]
        self.assertGreater(len(section_issues), 0)

    def test_missing_related_elements_section_fails(self):
        """Test that missing Related Design Elements section fails."""
        text = """# ADR-0001: Test Decision

**Date**: 2024-01-15

**Status**: Accepted

**ADR ID**: `fdd-app-adr-test`

## Context and Problem Statement

Context.

## Considered Options

- Option A

## Decision Outcome

Chosen option: "A", because test.
"""
        report = validate_adr(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        section_issues = [i for i in report["adr_issues"]
                         if "Related Design Elements" in i.get("message", "")]
        self.assertGreater(len(section_issues), 0)

    def test_all_sections_present_passes(self):
        """Test that ADR with all sections passes."""
        text = """# ADR-0001: Complete ADR

**Date**: 2024-01-15

**Status**: Accepted

**ADR ID**: `fdd-app-adr-complete`

## Context and Problem Statement

We need to decide something important.

## Considered Options

1. Option A
2. Option B
3. Option C

## Decision Outcome

Chosen option: "Option B", because test.

## Related Design Elements

- `fdd-app-req-performance`
- `fdd-app-principle-maintainability`
"""
        report = validate_adr(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "PASS")


class TestADRRelatedElements(unittest.TestCase):
    """Test ADR Related Design Elements validation."""

    def test_empty_related_elements_fails(self):
        """Test that empty Related Design Elements fails."""
        text = """# ADR-0001: Test Decision

**Date**: 2024-01-15

**Status**: Accepted

**ADR ID**: `fdd-app-adr-test-decision`

## Context and Problem Statement

Context.

## Considered Options

- Option A

## Decision Outcome

Chosen option: "A", because test.

## Related Design Elements

No IDs here.
"""
        report = validate_adr(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        related_issues = [i for i in report["adr_issues"]
                         if "at least one ID" in i.get("message", "")]
        self.assertGreater(len(related_issues), 0)

    def test_related_elements_with_valid_ids_passes(self):
        """Test that Related Elements with valid IDs passes."""
        text = """# ADR-0001: Test Decision

**Date**: 2024-01-15

**Status**: Accepted

**ADR ID**: `fdd-app-adr-test-decision`

## Context and Problem Statement

Context.

## Considered Options

- Option A

## Decision Outcome

Chosen option: "A", because test.

## Related Design Elements

- `fdd-app-req-authentication`
- `fdd-app-capability-secure-login`
- `fdd-app-actor-admin`
"""
        report = validate_adr(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "PASS")


class TestADRCrossReferences(unittest.TestCase):
    """Test ADR cross-reference validation."""

    def test_cross_reference_with_prd_and_design(self):
        """Test ADR validates against PRD.md and DESIGN.md."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()
            
            # Create PRD.md
            prd = arch / "PRD.md"
            prd.write_text("""# PRD

## B. Actors

- **ID**: `fdd-app-actor-user`

## C. Capabilities

### CAP-001: Login

**ID**: `fdd-app-capability-login`

**Actors**: `fdd-app-actor-user`
""")
            
            # Create DESIGN.md
            design = arch / "DESIGN.md"
            design.write_text("""# Technical Design

## B. Requirements

### FR-001: Authentication

**ID**: `fdd-app-req-auth`

**Capabilities**: `fdd-app-capability-login`

**Actors**: `fdd-app-actor-user`
""")
            
            adr_dir = arch / "ADR" / "general"
            adr_dir.mkdir(parents=True)
            adr_file = adr_dir / "0001-fdd-app-adr-use-jwt.md"
            adr_file.write_text(
                "\n".join(
                    [
                        "# ADR-0001: Use JWT",
                        "",
                        "**Date**: 2024-01-15",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-use-jwt`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "Choose auth mechanism.",
                        "",
                        "## Considered Options",
                        "",
                        "- JWT",
                        "- Sessions",
                        "",
                        "## Decision Outcome",
                        "",
                        "Chosen option: \"JWT\", because security.",
                        "",
                        "## Related Design Elements",
                        "",
                        "- Implements: `fdd-app-req-auth`",
                        "- Impacts: `fdd-app-actor-user`",
                        "- Supports: `fdd-app-capability-login`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            report = validate_adr(
                "",
                artifact_path=arch / "ADR",
                prd_path=prd,
                design_path=design,
                skip_fs_checks=False,
            )
            
            # Should pass with valid cross-references
            self.assertEqual(report["status"], "PASS")

    def test_unknown_actor_reference_fails(self):
        """Test that unknown actor in Related Elements fails."""
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
            design.write_text("""# Technical Design

## B. Requirements

### FR-001: Test

**ID**: `fdd-app-req-test`
""")
            
            adr_dir = arch / "ADR" / "general"
            adr_dir.mkdir(parents=True)
            adr_file = adr_dir / "0001-fdd-app-adr-test.md"
            adr_file.write_text(
                "\n".join(
                    [
                        "# ADR-0001: Test",
                        "",
                        "**Date**: 2024-01-15",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-test`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "Context.",
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
                        "- Impacts: `fdd-app-actor-unknown`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            report = validate_adr(
                "",
                artifact_path=arch / "ADR",
                prd_path=prd,
                design_path=design,
                skip_fs_checks=False,
            )
            
            self.assertEqual(report["status"], "FAIL")
            unknown_actor = [i for i in report["adr_issues"]
                           if "Unknown actor" in i.get("message", "")]
            self.assertGreater(len(unknown_actor), 0)


class TestADRMultipleEntries(unittest.TestCase):
    def test_multiple_adrs_all_valid_passes(self):
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()

            adr_dir = arch / "ADR" / "general"
            adr_dir.mkdir(parents=True)

            (adr_dir / "0001-fdd-app-adr-first-decision.md").write_text(
                "\n".join(
                    [
                        "# ADR-0001: First Decision",
                        "",
                        "**Date**: 2024-01-15",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-first-decision`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "First context.",
                        "",
                        "## Considered Options",
                        "",
                        "- Option A",
                        "",
                        "## Decision Outcome",
                        "",
                        "Chosen option: \"Option A\", because test.",
                        "",
                        "## Related Design Elements",
                        "",
                        "- `fdd-app-req-first`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            (adr_dir / "0002-fdd-app-adr-second-decision.md").write_text(
                "\n".join(
                    [
                        "# ADR-0002: Second Decision",
                        "",
                        "**Date**: 2024-01-20",
                        "",
                        "**Status**: Proposed",
                        "",
                        "**ADR ID**: `fdd-app-adr-second-decision`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "Second context.",
                        "",
                        "## Considered Options",
                        "",
                        "- Option B",
                        "",
                        "## Decision Outcome",
                        "",
                        "Chosen option: \"Option B\", because test.",
                        "",
                        "## Related Design Elements",
                        "",
                        "- `fdd-app-req-second`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            report = validate_adr("", artifact_path=arch / "ADR", skip_fs_checks=True)
            self.assertEqual(report["status"], "PASS")

    def test_multiple_adrs_some_invalid_fails(self):
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()

            adr_dir = arch / "ADR" / "general"
            adr_dir.mkdir(parents=True)

            (adr_dir / "0001-fdd-app-adr-valid.md").write_text(
                "\n".join(
                    [
                        "# ADR-0001: Valid",
                        "",
                        "**Date**: 2024-01-15",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-valid`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "Context.",
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

            (adr_dir / "0002-fdd-app-adr-invalid.md").write_text(
                "\n".join(
                    [
                        "# ADR-0002: Invalid",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-invalid`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "Context.",
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

            report = validate_adr("", artifact_path=arch / "ADR", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            adr_0002_issues = [i for i in report["adr_issues"] if i.get("adr") == "ADR-0002"]
            self.assertGreater(len(adr_0002_issues), 0)


class TestADRPlaceholders(unittest.TestCase):
    def test_placeholders_detected(self):
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()

            adr_dir = arch / "ADR" / "general"
            adr_dir.mkdir(parents=True)

            (adr_dir / "0001-fdd-app-adr-placeholders.md").write_text(
                "\n".join(
                    [
                        "# ADR-0001: Placeholders",
                        "",
                        "**Date**: 2024-01-15",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-placeholders`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "TODO: Add context",
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

            report = validate_adr("", artifact_path=arch / "ADR", skip_fs_checks=True)
            self.assertEqual(report["status"], "FAIL")
            self.assertGreater(len(report["placeholder_hits"]), 0)


class TestADRFileSystemChecks(unittest.TestCase):
    """Test ADR validation with file system checks."""

    def test_missing_prd_file_adds_error(self):
        """Test that missing PRD.md file adds cross-reference error."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()

            adr_dir = arch / "ADR" / "general"
            adr_dir.mkdir(parents=True)
            (adr_dir / "0001-fdd-app-adr-test.md").write_text(
                "\n".join(
                    [
                        "# ADR-0001: Test",
                        "",
                        "**Date**: 2024-01-15",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-test`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "Context.",
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

            report = validate_adr("", artifact_path=arch / "ADR", skip_fs_checks=False)
            
            # Should have cross-reference error for missing PRD.md
            cross_errors = [e for e in report["errors"] if e.get("type") == "cross"]
            self.assertGreater(len(cross_errors), 0)

    def test_missing_design_file_adds_error(self):
        """Test that missing DESIGN.md file adds cross-reference error."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()
            
            # Create ADR directory and PRD.md but no DESIGN.md
            prd = arch / "PRD.md"
            prd.write_text("# PRD\n\n## B. Actors\n\n- **ID**: `fdd-app-actor-user`")
            
            adr_dir = arch / "ADR" / "general"
            adr_dir.mkdir(parents=True)
            (adr_dir / "0001-fdd-app-adr-test.md").write_text(
                "\n".join(
                    [
                        "# ADR-0001: Test",
                        "",
                        "**Date**: 2024-01-15",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-test`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "Context.",
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
                        "- `fdd-app-actor-user`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            report = validate_adr("", artifact_path=arch / "ADR", skip_fs_checks=False)
            
            # Should have cross-reference error for missing DESIGN.md
            cross_errors = [e for e in report["errors"] if e.get("type") == "cross"]
            self.assertGreater(len(cross_errors), 0)

    def test_unknown_capability_reference_fails(self):
        """Test that unknown capability in Related Elements fails."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()
            
            prd = arch / "PRD.md"
            prd.write_text("""# PRD

## B. Actors

- **ID**: `fdd-app-actor-user`

## C. Capabilities

### CAP-001: Real Capability

**ID**: `fdd-app-capability-real`

**Actors**: `fdd-app-actor-user`
""")
            
            design = arch / "DESIGN.md"
            design.write_text("""# Technical Design

## B. Requirements

### FR-001: Test

**ID**: `fdd-app-req-test`
""")

            adr_dir = arch / "ADR" / "general"
            adr_dir.mkdir(parents=True)
            (adr_dir / "0001-fdd-app-adr-test.md").write_text(
                "\n".join(
                    [
                        "# ADR-0001: Test",
                        "",
                        "**Date**: 2024-01-15",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-test`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "Context.",
                        "",
                        "## Considered Options",
                        "",
                        "- Option A",
                        "",
                        "## Decision Outcome",
                        "",
                        "Chosen option: \"Option A\", because test.",
                        "",
                        "## Related Design Elements",
                        "",
                        "- Supports: `fdd-app-capability-unknown`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            report = validate_adr(
                "",
                artifact_path=arch / "ADR",
                prd_path=prd,
                design_path=design,
                skip_fs_checks=False,
            )
            
            self.assertEqual(report["status"], "FAIL")
            unknown_prd = [i for i in report["adr_issues"] if "Unknown PRD IDs" in i.get("message", "")]
            self.assertGreater(len(unknown_prd), 0)

    def test_unknown_requirement_reference_fails(self):
        """Test that unknown requirement in Related Elements fails."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()
            
            prd = arch / "PRD.md"
            prd.write_text("# PRD\n\n## B. Actors\n\n- **ID**: `fdd-app-actor-user`")
            
            design = arch / "DESIGN.md"
            design.write_text("""# Technical Design

## B. Requirements

### FR-001: Real Requirement

**ID**: `fdd-app-req-real`
""")

            adr_dir = arch / "ADR" / "general"
            adr_dir.mkdir(parents=True)
            (adr_dir / "0001-fdd-app-adr-test.md").write_text(
                "\n".join(
                    [
                        "# ADR-0001: Test",
                        "",
                        "**Date**: 2024-01-15",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-test`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "Context.",
                        "",
                        "## Considered Options",
                        "",
                        "- Option A",
                        "",
                        "## Decision Outcome",
                        "",
                        "Chosen option: \"Option A\", because test.",
                        "",
                        "## Related Design Elements",
                        "",
                        "- Implements: `fdd-app-req-unknown`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            report = validate_adr(
                "",
                artifact_path=arch / "ADR",
                prd_path=prd,
                design_path=design,
                skip_fs_checks=False,
            )
            
            self.assertEqual(report["status"], "FAIL")
            unknown_req = [i for i in report["adr_issues"]
                          if "Unknown requirement" in i.get("message", "")]
            self.assertGreater(len(unknown_req), 0)

    def test_unknown_principle_reference_fails(self):
        """Test that unknown principle in Related Elements fails."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir()
            
            prd = arch / "PRD.md"
            prd.write_text("# PRD\n\n## B. Actors\n\n- **ID**: `fdd-app-actor-user`")
            
            design = arch / "DESIGN.md"
            design.write_text("""# Technical Design

## B. Requirements

**ID**: `fdd-app-principle-real`

Real principle.
""")

            adr_dir = arch / "ADR" / "general"
            adr_dir.mkdir(parents=True)
            (adr_dir / "0001-fdd-app-adr-test.md").write_text(
                "\n".join(
                    [
                        "# ADR-0001: Test",
                        "",
                        "**Date**: 2024-01-15",
                        "",
                        "**Status**: Accepted",
                        "",
                        "**ADR ID**: `fdd-app-adr-test`",
                        "",
                        "## Context and Problem Statement",
                        "",
                        "Context.",
                        "",
                        "## Considered Options",
                        "",
                        "- Option A",
                        "",
                        "## Decision Outcome",
                        "",
                        "Chosen option: \"Option A\", because test.",
                        "",
                        "## Related Design Elements",
                        "",
                        "- Supports: `fdd-app-principle-unknown`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            report = validate_adr(
                "",
                artifact_path=arch / "ADR",
                prd_path=prd,
                design_path=design,
                skip_fs_checks=False,
            )
            
            self.assertEqual(report["status"], "FAIL")
            unknown_principle = [i for i in report["adr_issues"]
                                if "Unknown principle" in i.get("message", "")]
            self.assertGreater(len(unknown_principle), 0)


class TestADRDateValidation(unittest.TestCase):
    """Test ADR date validation."""

    def test_adr_with_valid_date_passes(self):
        """Test ADR with properly formatted date."""
        text = """# ADR-0001: Test Decision

**Date**: 2024-01-15

**Status**: Accepted

**ADR ID**: `fdd-app-adr-test-decision`

## Context and Problem Statement

Context here.

## Considered Options

- Option A

## Decision Outcome

Chosen option: "Option A", because test.

## Related Design Elements

- `fdd-app-req-test`
"""
        report = validate_adr(text, skip_fs_checks=True)
        
        date_issues = [i for i in report["adr_issues"] if "Date" in i.get("message", "")]
        self.assertEqual(len(date_issues), 0)

    def test_adr_missing_date_fails(self):
        """Test ADR without Date field fails."""
        text = """# ADR-0001: Test Decision

**Status**: Accepted

**ADR ID**: `fdd-app-adr-test-decision`

## Context and Problem Statement

Context.

## Considered Options

- Option A

## Decision Outcome

Chosen option: "Option A", because test.

## Related Design Elements

- `fdd-app-req-test`
"""
        report = validate_adr(text, skip_fs_checks=True)
        
        self.assertEqual(report["status"], "FAIL")
        date_issues = [i for i in report["adr_issues"] if "Date" in i.get("message", "")]
        self.assertGreater(len(date_issues), 0)


class TestADRStatusValidation(unittest.TestCase):
    """Test ADR status validation."""

    def test_adr_with_proposed_status(self):
        """Test ADR with Proposed status."""
        text = """# ADR-0001: Test

**Date**: 2024-01-15

**Status**: Proposed

**ADR ID**: `fdd-app-adr-test`

## Context and Problem Statement

Context.

## Considered Options

- A

## Decision Outcome

Chosen option: "A", because test.

## Related Design Elements

- `fdd-app-req-test`
"""
        report = validate_adr(text, skip_fs_checks=True)
        
        status_issues = [i for i in report["adr_issues"] if "Status" in i.get("message", "")]
        self.assertEqual(len(status_issues), 0)

    def test_adr_with_deprecated_status(self):
        """Test ADR with Deprecated status."""
        text = """# ADR-0001: Test

**Date**: 2024-01-15

**Status**: Deprecated

**ADR ID**: `fdd-app-adr-test`

## Context and Problem Statement

Context.

## Considered Options

- A

## Decision Outcome

Chosen option: "A", because test.

## Related Design Elements

- `fdd-app-req-test`
"""
        report = validate_adr(text, skip_fs_checks=True)
        
        status_issues = [i for i in report["adr_issues"] if "Status" in i.get("message", "")]
        self.assertEqual(len(status_issues), 0)

    def test_adr_with_superseded_status(self):
        """Test ADR with Superseded status."""
        text = """# ADR-0001: Test

**Date**: 2024-01-15

**Status**: Superseded

**ADR ID**: `fdd-app-adr-test`

## Context and Problem Statement

Context.

## Considered Options

- A

## Decision Outcome

Chosen option: "A", because test.

## Related Design Elements

- `fdd-app-req-test`
"""
        report = validate_adr(text, skip_fs_checks=True)
        
        status_issues = [i for i in report["adr_issues"] if "Status" in i.get("message", "")]
        self.assertEqual(len(status_issues), 0)


class TestADRCoverageBranches(unittest.TestCase):
    def test_file_mode_fs_checks_prd_missing_design_present(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir(parents=True)

            adr_file = arch / "ADR-single.md"
            adr_text = "\n".join(
                [
                    "# ADR-0001: Test",
                    "",
                    "**Date**: 2024-01-15",
                    "",
                    "**Status**: Accepted",
                    "",
                    "**ADR ID**: `fdd-app-adr-test`",
                    "",
                    "## Context and Problem Statement",
                    "",
                    "Context.",
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
            )
            adr_file.write_text(adr_text, encoding="utf-8")

            (arch / "DESIGN.md").write_text(
                "\n".join(
                    [
                        "# Technical Design",
                        "",
                        "## B. Requirements",
                        "",
                        "### FR-001: Test",
                        "",
                        "**ID**: `fdd-app-req-test`",
                        "",
                        "**ID**: `fdd-app-principle-real`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            report = validate_adr(
                adr_text,
                artifact_path=adr_file,
                skip_fs_checks=False,
            )
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "cross" for e in report.get("errors", [])))

    def test_file_mode_fs_checks_prd_present_design_missing(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            arch = tmppath / "architecture"
            arch.mkdir(parents=True)

            adr_file = arch / "ADR-single.md"
            adr_text = "\n".join(
                [
                    "# ADR-0001: Test",
                    "",
                    "**Date**: 2024-01-15",
                    "",
                    "**Status**: Accepted",
                    "",
                    "**ADR ID**: `fdd-app-adr-test`",
                    "",
                    "## Context and Problem Statement",
                    "",
                    "Context.",
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
            )
            adr_file.write_text(adr_text, encoding="utf-8")

            (arch / "PRD.md").write_text(
                "\n".join(
                    [
                        "# PRD",
                        "",
                        "## B. Actors",
                        "",
                        "- **ID**: `fdd-app-actor-user`",
                        "",
                        "## C. Capabilities",
                        "",
                        "- **ID**: `fdd-app-capability-test`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            report = validate_adr(
                adr_text,
                artifact_path=adr_file,
                skip_fs_checks=False,
            )
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any(e.get("type") == "cross" for e in report.get("errors", [])))

    def test_related_elements_h3_heading_branch_is_handled(self) -> None:
        text = "\n".join(
            [
                "# ADR-0001: Test",
                "",
                "**Date**: 2024-01-15",
                "",
                "**Status**: Accepted",
                "",
                "**ADR ID**: `fdd-app-adr-test`",
                "",
                "## Context and Problem Statement",
                "",
                "Context.",
                "",
                "## Considered Options",
                "",
                "- A",
                "",
                "## Decision Outcome",
                "",
                "Chosen option: \"A\", because test.",
                "",
                "### Related Design Elements",
                "",
                "- `fdd-app-req-test`",
                "",
            ]
        )
        report = validate_adr(text, skip_fs_checks=True)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report.get("adr_issues"), [])

    def test_validate_single_adr_text_no_h1_when_not_required(self) -> None:
        from fdd.validation.artifacts.adr import _validate_single_adr_text

        issues = _validate_single_adr_text(
            "No ADR headings here\n",
            adr_ref=None,
            require_h1=False,
        )
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
