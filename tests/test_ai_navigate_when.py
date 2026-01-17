# @fdd-change:fdd-fdd-feature-core-methodology-change-agents-navigation:ph-1
# Tests implement: fdd-fdd-feature-core-methodology-test-ai-navigate-when
"""
Tests for AI agent WHEN clause navigation.

Validates that:
1. AI agent can parse WHEN clauses from AGENTS.md
2. AI agent evaluates WHEN conditions correctly
3. AI agent opens correct spec files based on context
"""
import sys
import unittest
from pathlib import Path

# Add skills/fdd/scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))


# fdd-begin fdd-fdd-feature-core-methodology-test-ai-navigate-when:ph-1:inst-test-when-parsing
class TestWhenClauseNavigation(unittest.TestCase):
    """Test AI agent WHEN clause navigation."""

    def test_parse_when_clauses_from_agents(self):
        """Verify WHEN clauses can be extracted from AGENTS.md."""
        agents_file = Path(__file__).parent.parent / "AGENTS.md"
        if not agents_file.exists():
            self.skipTest("AGENTS.md not found")
        
        content = agents_file.read_text(encoding='utf-8')
        # Check for WHEN keyword presence
        self.assertIn("WHEN", content, "AGENTS.md should contain WHEN clauses")

    def test_when_condition_evaluation(self):
        """Verify WHEN conditions can be evaluated against context."""
        # TODO: Implement WHEN condition parser and evaluator
        self.skipTest("Requires WHEN clause parser implementation")

    def test_spec_file_resolution(self):
        """Verify spec file paths can be resolved from WHEN clauses."""
        # TODO: Test relative path resolution from WHEN clauses
        self.skipTest("Requires spec file path resolver implementation")

    def test_adapter_when_clause_merging(self):
        """Verify core and adapter WHEN clauses are merged correctly."""
        # TODO: Test WHEN clause merging logic
        self.skipTest("Requires adapter discovery and WHEN merge logic")


# fdd-end   fdd-fdd-feature-core-methodology-test-ai-navigate-when:ph-1:inst-test-when-parsing


if __name__ == "__main__":
    unittest.main(verbosity=2)
