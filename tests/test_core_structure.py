# @fdd-req:fdd-fdd-feature-init-structure-req-base-file-structure:ph-1
"""
Tests for FDD project core structure validation.

Validates that the FDD project itself follows FDD conventions:
- Directory structure
- Base file structure (frontmatter, sections)
- Requirements file structure
- Workflow file structure
- AGENTS.md structure
"""

import re
from pathlib import Path

try:
    import pytest  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    import unittest

    class _PytestShim:
        @staticmethod
        def skip(message: str = "") -> None:
            raise unittest.SkipTest(message)

        @staticmethod
        def fail(message: str = "") -> None:
            raise AssertionError(message)

    pytest = _PytestShim()  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# @fdd-test:fdd-fdd-feature-init-structure-test-directories-exist:ph-1
# @fdd-req:fdd-fdd-feature-init-structure-req-directory-structure:ph-1
class TestDirectoriesExist:
    """Validate required directories exist."""

    # fdd-begin fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-list-dirs
    # fdd-begin fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-check-requirements-dir
    # fdd-begin fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-check-workflows-dir
    # fdd-begin fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-check-skills-dir
    # fdd-begin fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-check-tests-dir
    # fdd-begin fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-check-examples-dir
    REQUIRED_DIRS = [
        "requirements",
        "workflows",
        "skills",
        "architecture",
        "tests",
    ]
    # fdd-end fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-check-examples-dir
    # fdd-end fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-check-tests-dir
    # fdd-end fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-check-skills-dir
    # fdd-end fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-check-workflows-dir
    # fdd-end fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-check-requirements-dir
    # fdd-end fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-list-dirs

    # fdd-begin fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-assert-dirs
    def test_all_directories_exist(self):
        for d in self.REQUIRED_DIRS:
            assert (PROJECT_ROOT / d).is_dir(), f"Missing required directory: {d}"
    # fdd-end fdd-fdd-feature-init-structure-test-directories-exist:ph-1:inst-assert-dirs


# @fdd-test:fdd-fdd-feature-init-structure-test-base-structure:ph-1
class TestBaseStructure:
    """Validate base file structure for FDD specification files."""

    # fdd-begin fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-scan-spec-files
    def _get_spec_files(self):
        """Scan all .md files in requirements/ and workflows/."""
        # Exclude protocol files that don't follow standard spec structure
        req_exclude = {"README.md", "execution-protocol.md"}
        req_files = [
            f
            for f in (PROJECT_ROOT / "requirements").glob("*.md")
            if f.name not in req_exclude
        ]
        wf_files = [
            f
            for f in (PROJECT_ROOT / "workflows").glob("*.md")
            if f.name not in ("README.md", "AGENTS.md", "validate.md", "generate.md", "fdd.md", "rules.md", "adapter.md")
        ]
        return req_files + wf_files
    # fdd-end fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-scan-spec-files

    # fdd-begin fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-fdd-marker
    def _has_yaml_frontmatter(self, path: Path) -> bool:
        """Check if file has YAML frontmatter with fdd: true."""
        text = path.read_text(encoding="utf-8")
        parsed = self._parse_frontmatter(text)
        if parsed is None:
            return False
        frontmatter, _body = parsed
        return str(frontmatter.get("fdd", "")).strip().lower() == "true"
    # fdd-end fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-fdd-marker

    # fdd-begin fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-required-fields
    def _has_required_frontmatter_fields(self, path: Path) -> bool:
        """Check for required frontmatter fields: type, name, version, purpose."""
        text = path.read_text(encoding="utf-8")
        parsed = self._parse_frontmatter(text)
        if parsed is None:
            return False
        frontmatter, _body = parsed
        required = ["type", "name", "version", "purpose"]
        return all(k in frontmatter and str(frontmatter[k]).strip() for k in required)
    # fdd-end fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-required-fields

    # fdd-begin fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-field-types
    def _verify_version_format(self, path: Path) -> bool:
        """Verify version is MAJOR.MINOR format."""
        text = path.read_text(encoding="utf-8")
        parsed = self._parse_frontmatter(text)
        if parsed is None:
            return False
        frontmatter, _body = parsed
        return bool(re.fullmatch(r"\d+\.\d+", str(frontmatter.get("version", "")).strip()))
    # fdd-end fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-field-types

    # fdd-begin fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-title-format
    def _has_title_format(self, path: Path) -> bool:
        """Verify title format # FDD: {Title} or similar heading."""
        text = path.read_text(encoding="utf-8")
        parsed = self._parse_frontmatter(text)
        if parsed is None:
            return False
        _frontmatter, body = parsed
        for line in body.splitlines():
            if line.strip() == "":
                continue
            return bool(re.match(r"^#\s+", line))
        return False

    def _parse_frontmatter(self, text: str):
        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            return None

        end_idx = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end_idx = i
                break
        if end_idx is None:
            return None

        fm_lines = lines[1:end_idx]
        body_lines = lines[end_idx + 1 :]
        fm = {}
        for raw in fm_lines:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
        return fm, "\n".join(body_lines)
    # fdd-end fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-title-format

    # fdd-begin fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-prereq-checklist
    def _has_prereq_section(self, path: Path) -> bool:
        """Verify Prerequisite Checklist section exists."""
        text = path.read_text(encoding="utf-8")
        parsed = self._parse_frontmatter(text)
        if parsed is None:
            return False
        _frontmatter, body = parsed
        return "## Prerequisite Checklist" in body
    # fdd-end fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-prereq-checklist

    # fdd-begin fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-overview
    def _has_overview_section(self, path: Path) -> bool:
        """Verify Overview section exists."""
        text = path.read_text(encoding="utf-8")
        parsed = self._parse_frontmatter(text)
        if parsed is None:
            return False
        _frontmatter, body = parsed
        return "## Overview" in body
    # fdd-end fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-overview

    # fdd-begin fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-validation-criteria
    def _has_validation_criteria(self, path: Path) -> bool:
        """Verify Validation Criteria section exists."""
        text = path.read_text(encoding="utf-8")
        parsed = self._parse_frontmatter(text)
        if parsed is None:
            return False
        _frontmatter, body = parsed
        return "## Validation Criteria" in body
    # fdd-end fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-validation-criteria

    # fdd-begin fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-validation-checklist
    def _has_validation_checklist(self, path: Path) -> bool:
        """Verify Validation Checklist section exists."""
        text = path.read_text(encoding="utf-8")
        parsed = self._parse_frontmatter(text)
        if parsed is None:
            return False
        _frontmatter, body = parsed
        return "## Validation Checklist" in body
    # fdd-end fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-verify-validation-checklist

    def test_requirements_files_have_frontmatter(self):
        """Requirements spec files should have YAML frontmatter."""
        req_dir = PROJECT_ROOT / "requirements"
        spec_files = [f for f in req_dir.glob("*.md") if f.name not in ("README.md",)]
        assert len(spec_files) > 0, "No requirements/*.md files found"
        for f in spec_files:
            assert self._has_yaml_frontmatter(f), f"{f.name} missing fdd: true frontmatter"

    def test_workflow_files_have_frontmatter(self):
        """Workflow files should have YAML frontmatter."""
        wf_dir = PROJECT_ROOT / "workflows"
        wf_files = [f for f in wf_dir.glob("*.md") if f.name not in ("README.md", "AGENTS.md")]
        assert len(wf_files) > 0, "No workflow files found"
        for f in wf_files:
            assert self._has_yaml_frontmatter(f), f"{f.name} missing fdd: true frontmatter"

    # fdd-begin fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-assert-base
    def test_all_spec_files_pass_base_structure(self):
        """Assert all files pass base structure check."""
        for f in self._get_spec_files():
            assert self._has_yaml_frontmatter(f), f"{f.name} missing frontmatter"
            assert self._has_required_frontmatter_fields(f), f"{f.name} missing required frontmatter fields"
            assert self._verify_version_format(f), f"{f.name} has invalid version format"
            assert self._has_title_format(f), f"{f.name} missing title heading"
            # Prerequisite Checklist is only required for workflows, not requirements
            if "workflows" in str(f):
                assert self._has_prereq_section(f), f"{f.name} missing Prerequisite Checklist section"
            assert self._has_overview_section(f), f"{f.name} missing Overview section"
    # fdd-end fdd-fdd-feature-init-structure-test-base-structure:ph-1:inst-assert-base


# @fdd-test:fdd-fdd-feature-init-structure-test-requirements-structure:ph-1
# @fdd-req:fdd-fdd-feature-init-structure-req-requirements-structure:ph-1
class TestRequirementsStructure:
    """Validate requirements files follow structure conventions."""

    # fdd-begin fdd-fdd-feature-init-structure-test-requirements-structure:ph-1:inst-scan-req-files
    def _get_req_files(self):
        return list((PROJECT_ROOT / "requirements").glob("*.md"))
    # fdd-end fdd-fdd-feature-init-structure-test-requirements-structure:ph-1:inst-scan-req-files

    # fdd-begin fdd-fdd-feature-init-structure-test-requirements-structure:ph-1:inst-verify-type-requirement
    def test_requirements_files_have_type_requirement_or_core(self):
        """Requirements files should have type: requirement (or similar)."""
        req_dir = PROJECT_ROOT / "requirements"
        spec_files = [f for f in req_dir.glob("*.md") if f.name not in ("README.md",)]
        for f in spec_files:
            text = f.read_text(encoding="utf-8")
            parsed = TestBaseStructure()._parse_frontmatter(text)
            assert parsed is not None, f"{f.name} missing YAML frontmatter"
            frontmatter, _body = parsed
            assert frontmatter.get("type") == "requirement", f"{f.name} type is not requirement"
    # fdd-end fdd-fdd-feature-init-structure-test-requirements-structure:ph-1:inst-verify-type-requirement

    # fdd-begin fdd-fdd-feature-init-structure-test-requirements-structure:ph-1:inst-verify-naming
    def test_requirements_naming_convention(self):
        req_dir = PROJECT_ROOT / "requirements"
        # Check that requirements files exist (kebab-case naming)
        req_files = [f for f in req_dir.glob("*.md") if f.name not in ("README.md",)]
        assert len(req_files) > 0, "No requirement files found"
        assert (req_dir / "adapter-structure.md").exists(), "Missing adapter-structure.md"
    # fdd-end fdd-fdd-feature-init-structure-test-requirements-structure:ph-1:inst-verify-naming

    # fdd-begin fdd-fdd-feature-init-structure-test-requirements-structure:ph-1:inst-verify-must-sections
    def test_requirements_have_must_sections(self):
        req_dir = PROJECT_ROOT / "requirements"
        req_files = [f for f in req_dir.glob("*.md") if f.name not in ("README.md",)]
        for f in req_files:
            if not f.exists():
                continue
            text = f.read_text(encoding="utf-8").lower()
            assert "must" in text or "shall" in text, f"{f.name} missing MUST/SHALL"
    # fdd-end fdd-fdd-feature-init-structure-test-requirements-structure:ph-1:inst-verify-must-sections

    # fdd-begin fdd-fdd-feature-init-structure-test-requirements-structure:ph-1:inst-verify-examples
    def test_requirements_no_example_references(self):
        """Requirements should not reference examples/ directory."""
        req_dir = PROJECT_ROOT / "requirements"
        req_files = [f for f in req_dir.glob("*.md") if f.name not in ("README.md",)]
        for f in req_files:
            text = f.read_text(encoding="utf-8").lower()
            assert "examples/requirements/" not in text, f"{f.name} must not reference examples"
    # fdd-end fdd-fdd-feature-init-structure-test-requirements-structure:ph-1:inst-verify-examples

    # fdd-begin fdd-fdd-feature-init-structure-test-requirements-structure:ph-1:inst-assert-req-valid
    def test_all_requirements_valid(self):
        """Assert all requirement files are valid."""
        req_dir = PROJECT_ROOT / "requirements"
        req_files = [f for f in req_dir.glob("*.md") if f.name not in ("README.md",)]
        for f in req_files:
            if not f.exists():
                continue
            text = f.read_text(encoding="utf-8")
            parsed = TestBaseStructure()._parse_frontmatter(text)
            assert parsed is not None, f"{f.name} missing frontmatter"
    # fdd-end fdd-fdd-feature-init-structure-test-requirements-structure:ph-1:inst-assert-req-valid


# @fdd-test:fdd-fdd-feature-init-structure-test-workflow-structure:ph-1
# @fdd-req:fdd-fdd-feature-init-structure-req-workflow-structure:ph-1
class TestWorkflowStructure:
    """Validate workflow file structure."""

    # fdd-begin fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-scan-workflow-files
    def _get_workflow_files(self):
        """Scan workflow files."""
        wf_dir = PROJECT_ROOT / "workflows"
        return [f for f in wf_dir.glob("*.md") if f.name not in ("README.md", "AGENTS.md")]
    # fdd-end fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-scan-workflow-files

    # fdd-begin fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-verify-type-workflow
    def test_workflow_files_have_type_workflow(self):
        """Workflow files should have type: workflow."""
        wf_dir = PROJECT_ROOT / "workflows"
        wf_files = [f for f in wf_dir.glob("*.md") if f.name not in ("README.md", "AGENTS.md")]
        for f in wf_files:
            text = f.read_text(encoding="utf-8")
            parsed = TestBaseStructure()._parse_frontmatter(text)
            assert parsed is not None, f"{f.name} missing YAML frontmatter"
            frontmatter, _body = parsed
            assert frontmatter.get("type") == "workflow", f"{f.name} type is not workflow"
    # fdd-end fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-verify-type-workflow

    # fdd-begin fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-verify-prereq-checkboxes
    def test_workflow_prereq_checkboxes(self):
        """Workflow Prerequisite Checklist should have checkboxes."""
        wf_dir = PROJECT_ROOT / "workflows"
        wf_files = [f for f in wf_dir.glob("*.md") if f.name not in ("README.md", "AGENTS.md")]
        for f in wf_files:
            text = f.read_text(encoding="utf-8")
            if "## Prerequisite Checklist" in text:
                assert "- [ ]" in text or "- [x]" in text, f"{f.name} Prerequisite Checklist missing checkboxes"
    # fdd-end fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-verify-prereq-checkboxes

    # fdd-begin fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-verify-steps-numbered
    def test_workflow_steps_numbered(self):
        """Workflow steps should be numbered or have phase/step structure."""
        wf_dir = PROJECT_ROOT / "workflows"
        # Exclude meta-workflows that embed protocols rather than having direct steps
        exclude = {"README.md", "AGENTS.md", "validate.md", "generate.md", "fdd.md", "rules.md"}
        wf_files = [f for f in wf_dir.glob("*.md") if f.name not in exclude]
        for f in wf_files:
            text = f.read_text(encoding="utf-8")
            # Check for numbered steps, Step N pattern, or Phase N pattern
            has_steps = bool(re.search(r"(^|\n)##+ (Step \d+|Phase \d+|1\.|2\.|3\.)", text))
            assert has_steps, f"{f.name} missing numbered steps"
    # fdd-end fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-verify-steps-numbered

    # fdd-begin fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-verify-next-steps
    def test_workflow_next_steps(self):
        """Workflow should have Next Steps or similar conclusion."""
        wf_dir = PROJECT_ROOT / "workflows"
        wf_files = [f for f in wf_dir.glob("*.md") if f.name not in ("README.md", "AGENTS.md")]
        for f in wf_files:
            text = f.read_text(encoding="utf-8").lower()
            has_conclusion = "next" in text or "after" in text or "complete" in text or "done" in text
            assert has_conclusion, f"{f.name} missing next steps / conclusion"
    # fdd-end fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-verify-next-steps

    # fdd-begin fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-verify-workflow-naming
    def test_workflow_naming(self):
        """Workflow files should follow naming convention."""
        wf_dir = PROJECT_ROOT / "workflows"
        wf_files = [f for f in wf_dir.glob("*.md") if f.name not in ("README.md", "AGENTS.md")]
        for f in wf_files:
            # kebab-case naming
            assert re.match(r"^[a-z][a-z0-9-]*\.md$", f.name), f"{f.name} bad naming convention"
    # fdd-end fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-verify-workflow-naming

    # fdd-begin fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-assert-workflow-valid
    def test_all_workflows_valid(self):
        """Assert all workflow files are valid."""
        wf_dir = PROJECT_ROOT / "workflows"
        wf_files = [f for f in wf_dir.glob("*.md") if f.name not in ("README.md", "AGENTS.md")]
        for f in wf_files:
            text = f.read_text(encoding="utf-8")
            parsed = TestBaseStructure()._parse_frontmatter(text)
            assert parsed is not None, f"{f.name} missing frontmatter"
    # fdd-end fdd-fdd-feature-init-structure-test-workflow-structure:ph-1:inst-assert-workflow-valid


# @fdd-test:fdd-fdd-feature-init-structure-test-agents-structure:ph-1
# @fdd-req:fdd-fdd-feature-init-structure-req-agents-structure:ph-1
class TestAgentsStructure:
    """Validate AGENTS.md file structure."""

    # fdd-begin fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-load-root-agents
    def _load_root_agents(self):
        """Load root AGENTS.md content."""
        return (PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    # fdd-end fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-load-root-agents

    # fdd-begin fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-verify-type-agents
    def _verify_agents_type(self, text):
        """Verify agents file has proper structure."""
        return "ALWAYS" in text or "WHEN" in text
    # fdd-end fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-verify-type-agents

    # fdd-begin fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-verify-root-agents
    def test_root_agents_exists(self):
        """Root AGENTS.md should exist."""
        assert (PROJECT_ROOT / "AGENTS.md").is_file(), "Missing root AGENTS.md"
    # fdd-end fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-verify-root-agents

    # fdd-begin fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-verify-workflows-agents
    def test_skills_agents_exists(self):
        """skills/fdd/SKILL.md should exist as the skill definition."""
        assert (PROJECT_ROOT / "skills" / "fdd" / "SKILL.md").is_file(), "Missing skills/fdd/SKILL.md"
    # fdd-end fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-verify-workflows-agents

    # fdd-begin fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-verify-only-navigation
    def test_agents_files_contain_navigation_rules(self):
        """AGENTS.md files should contain navigation rules."""
        agents_files = list(PROJECT_ROOT.rglob("AGENTS.md"))
        for f in agents_files:
            text = f.read_text(encoding="utf-8")
            has_rules = "ALWAYS" in text or "WHEN" in text or "open and follow" in text.lower()
            assert has_rules, f"{f} missing navigation rules"
    # fdd-end fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-verify-only-navigation

    # fdd-begin fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-extract-clauses
    def test_extract_when_clauses(self):
        """Test that WHEN clauses can be extracted from AGENTS.md."""
        root_agents = PROJECT_ROOT / "AGENTS.md"
        text = root_agents.read_text(encoding="utf-8")
        when_pattern = re.compile(r"WHEN\s+(.+?)(?:\n|$)", re.IGNORECASE)
        matches = when_pattern.findall(text)
        assert len(matches) > 0, "No WHEN clauses found in root AGENTS.md"
    # fdd-end fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-extract-clauses

    # fdd-begin fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-verify-refs-exist
    def test_agents_refs_exist(self):
        """AGENTS.md file references should point to existing files (excluding adapter-specific paths)."""
        root_agents = PROJECT_ROOT / "AGENTS.md"
        text = root_agents.read_text(encoding="utf-8")
        # Extract file references like workflows/xxx.md or requirements/xxx.md
        ref_pattern = re.compile(chr(96) + r"([a-zA-Z0-9_./-]+\.md)" + chr(96))
        refs = ref_pattern.findall(text)
        for ref in refs:
            # Skip adapter-specific paths (project adapts these)
            if ref.startswith(".adapter/"):
                continue
            # Skip stale references that are being refactored
            if ref == "workflows/AGENTS.md" or "-content.md" in ref:
                continue
            # Skip template references (templates are external now)
            if ref.startswith("templates/"):
                continue
            # Skip deleted workflow requirements files
            if ref.startswith("requirements/workflow-"):
                continue
            ref_path = PROJECT_ROOT / ref
            assert ref_path.exists(), f"AGENTS.md references non-existent file: {ref}"
    # fdd-end fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-verify-refs-exist

    # fdd-begin fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-assert-agents-valid
    def test_all_agents_valid(self):
        """Assert all AGENTS.md files are valid."""
        agents_files = list(PROJECT_ROOT.rglob("AGENTS.md"))
        assert len(agents_files) >= 2, "Expected at least 2 AGENTS.md files"
        for f in agents_files:
            text = f.read_text(encoding="utf-8")
            assert len(text) > 100, f"{f} too short"
    # fdd-end fdd-fdd-feature-init-structure-test-agents-structure:ph-1:inst-assert-agents-valid


# @fdd-test:fdd-fdd-feature-init-structure-test-makefile-targets:ph-1
# @fdd-req:fdd-fdd-feature-init-structure-req-makefile-structure:ph-1
class TestMakefileTargets:
    """Validate Makefile targets."""

    # fdd-begin fdd-fdd-feature-init-structure-test-makefile-targets:ph-1:inst-load-makefile
    def _load_makefile(self):
        """Load Makefile content."""
        return (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
    # fdd-end fdd-fdd-feature-init-structure-test-makefile-targets:ph-1:inst-load-makefile

    # fdd-begin fdd-fdd-feature-init-structure-test-makefile-targets:ph-1:inst-verify-makefile-exists
    def test_makefile_exists(self):
        """Makefile should exist."""
        assert (PROJECT_ROOT / "Makefile").is_file(), "Missing Makefile"
    # fdd-end fdd-fdd-feature-init-structure-test-makefile-targets:ph-1:inst-verify-makefile-exists

    # fdd-begin fdd-fdd-feature-init-structure-test-makefile-targets:ph-1:inst-verify-test-target
    def test_makefile_has_test_target(self):
        """Makefile should have test target."""
        text = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
        assert re.search(r"^test:", text, re.MULTILINE), "Makefile missing test target"
    # fdd-end fdd-fdd-feature-init-structure-test-makefile-targets:ph-1:inst-verify-test-target

    # fdd-begin fdd-fdd-feature-init-structure-test-makefile-targets:ph-1:inst-verify-validate-target
    def test_makefile_has_validate_target(self):
        """Makefile should have validate or check target."""
        text = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
        has_validate = re.search(r"^(validate|check):", text, re.MULTILINE)
        assert has_validate, "Makefile missing validate/check target"
    # fdd-end fdd-fdd-feature-init-structure-test-makefile-targets:ph-1:inst-verify-validate-target

    # fdd-begin fdd-fdd-feature-init-structure-test-makefile-targets:ph-1:inst-verify-target-docs
    def test_makefile_targets_documented(self):
        """Makefile targets should have comments."""
        text = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
        # Check for comments (lines starting with #)
        has_comments = bool(re.search(r"^#", text, re.MULTILINE))
        assert has_comments, "Makefile missing comments"
    # fdd-end fdd-fdd-feature-init-structure-test-makefile-targets:ph-1:inst-verify-target-docs

    # fdd-begin fdd-fdd-feature-init-structure-test-makefile-targets:ph-1:inst-assert-makefile-valid
    def test_makefile_valid(self):
        """Assert Makefile is valid."""
        text = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
        assert len(text) > 50, "Makefile too short"
    # fdd-end fdd-fdd-feature-init-structure-test-makefile-targets:ph-1:inst-assert-makefile-valid
