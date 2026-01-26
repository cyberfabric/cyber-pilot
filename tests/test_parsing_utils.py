"""
Unit tests for utils/parsing.py functions.

Tests parsing utilities for markdown structure extraction and field parsing.
"""

import unittest
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))

from fdd.utils.parsing import (
    parse_required_sections,
    find_present_section_ids,
    split_by_section_letter,
    split_by_feature_section_letter,
    split_by_prd_section_letter,
    field_block,
    has_list_item,
    extract_backticked_ids,
)
from fdd.constants import (
    SECTION_FEATURE_RE,
    SECTION_PRD_RE,
    ACTOR_ID_RE,
    CAPABILITY_ID_RE,
)


class TestFindPresentSectionIds(unittest.TestCase):
    """Test find_present_section_ids function."""

    def test_find_single_section(self):
        """Test finding single section."""
        text = """
# Document

## A. First Section

Content here
"""
        
        sections = find_present_section_ids(text)
        
        self.assertIn("A", sections)

    def test_find_multiple_sections(self):
        """Test finding multiple sections."""
        text = """
# Document

## A. First Section

Content

## B. Second Section

More content

## C. Third Section

Even more
"""
        
        sections = find_present_section_ids(text)
        
        self.assertIn("A", sections)
        self.assertIn("B", sections)
        self.assertIn("C", sections)

    def test_find_no_sections(self):
        """Test finding no sections."""
        text = "Just plain text with no sections"
        
        sections = find_present_section_ids(text)
        
        self.assertEqual(len(sections), 0)


class TestSplitBySectionLetter(unittest.TestCase):
    """Test split_by_section_letter function."""

    def test_split_simple_sections(self):
        """Test splitting document into sections."""
        text = """
## A. First Section

Content A

## B. Second Section

Content B
"""
        section_re = re.compile(r"^##\s+([A-E])\.\s+(.+)?$", re.IGNORECASE)
        
        order, sections = split_by_section_letter(text, section_re)
        
        self.assertEqual(order, ["A", "B"])
        self.assertIn("A", sections)
        self.assertIn("B", sections)
        self.assertIn("Content A", "\n".join(sections["A"]))
        self.assertIn("Content B", "\n".join(sections["B"]))

    def test_split_with_preamble(self):
        """Test splitting with preamble before sections."""
        text = """
# Document Title

Some preamble text

## A. First Section

Content A
"""
        section_re = re.compile(r"^##\s+([A-E])\.\s+(.+)?$", re.IGNORECASE)
        
        order, sections = split_by_section_letter(text, section_re)
        
        self.assertEqual(order, ["A"])
        self.assertIn("A", sections)


class TestSplitByFeatureSectionLetter(unittest.TestCase):
    """Test split_by_feature_section_letter function."""

    def test_split_feature_sections(self):
        """Test splitting feature DESIGN.md."""
        text = """
## A. Overview

Feature overview

## B. Requirements

Requirements here

## C. Design

Design details
"""
        
        order, sections = split_by_feature_section_letter(text)
        
        self.assertEqual(order, ["A", "B", "C"])
        self.assertIn("A", sections)
        self.assertIn("B", sections)
        self.assertIn("C", sections)


class TestSplitByPRDSectionLetter(unittest.TestCase):
    """Test split_by_prd_section_letter function."""

    def test_split_prd_sections(self):
        """Test splitting PRD.md."""
        text = """
## A. PRD

Context

## B. Actors

Actors list

## C. Capabilities

Capabilities
"""
        
        order, sections = split_by_prd_section_letter(text)
        
        self.assertEqual(order, ["A", "B", "C"])
        self.assertIn("A", sections)
        self.assertIn("B", sections)


class TestFieldBlock(unittest.TestCase):
    """Test field_block function."""

    def test_extract_simple_field(self):
        """Test extracting field with value."""
        lines = [
            "Some text",
            "**Status**: Active",
            "More text",
        ]
        
        block = field_block(lines, "Status")
        
        self.assertIsNotNone(block)
        self.assertEqual(block["value"], "Active")
        self.assertEqual(block["index"], 1)

    def test_extract_field_with_tail(self):
        """Test extracting field with tail lines."""
        lines = [
            "**Description**: This is",
            "a multi-line",
            "description",
            "**Next Field**: value",
        ]
        
        block = field_block(lines, "Description")
        
        self.assertIsNotNone(block)
        self.assertEqual(block["value"], "This is")
        self.assertIn("a multi-line", block["tail"])
        self.assertIn("description", block["tail"])

    def test_field_not_found(self):
        """Test when field is not found."""
        lines = [
            "Some text",
            "**Other**: value",
        ]
        
        block = field_block(lines, "Missing")
        
        self.assertIsNone(block)

    def test_field_stops_at_next_field(self):
        """Test that tail stops at next known field."""
        lines = [
            "**Status**: Active",
            "Extra line 1",
            "Extra line 2",
            "**Priority**: High",
            "After priority",
        ]
        
        block = field_block(lines, "Status")
        
        self.assertIsNotNone(block)
        # Tail includes lines until next field is found
        self.assertGreater(len(block["tail"]), 0)
        # Should contain extra lines
        self.assertIn("Extra line 1", block["tail"])


class TestHasListItem(unittest.TestCase):
    """Test has_list_item function."""

    def test_has_dash_list(self):
        """Test detecting dash list items."""
        lines = [
            "Some text",
            "- List item 1",
            "- List item 2",
        ]
        
        has_list = has_list_item(lines)
        
        self.assertTrue(has_list)

    def test_has_asterisk_list(self):
        """Test detecting asterisk list items."""
        lines = [
            "Some text",
            "* List item 1",
            "* List item 2",
        ]
        
        has_list = has_list_item(lines)
        
        self.assertTrue(has_list)

    def test_no_list(self):
        """Test detecting no list items."""
        lines = [
            "Just plain text",
            "No list items here",
        ]
        
        has_list = has_list_item(lines)
        
        self.assertFalse(has_list)

    def test_indented_list(self):
        """Test detecting indented list items."""
        lines = [
            "Some text",
            "  - Indented item",
        ]
        
        has_list = has_list_item(lines)
        
        self.assertTrue(has_list)


class TestExtractBacktickedIds(unittest.TestCase):
    """Test extract_backticked_ids function."""

    def test_extract_single_id(self):
        """Test extracting single backticked ID."""
        line = "Actor: `fdd-test-actor-user`"
        
        ids = extract_backticked_ids(line, ACTOR_ID_RE)
        
        self.assertEqual(len(ids), 1)
        self.assertEqual(ids[0], "fdd-test-actor-user")

    def test_extract_multiple_ids(self):
        """Test extracting multiple backticked IDs."""
        line = "Actors: `fdd-test-actor-user`, `fdd-test-actor-admin`"
        
        ids = extract_backticked_ids(line, ACTOR_ID_RE)
        
        self.assertEqual(len(ids), 2)
        self.assertIn("fdd-test-actor-user", ids)
        self.assertIn("fdd-test-actor-admin", ids)

    def test_extract_no_match(self):
        """Test extracting when pattern doesn't match."""
        line = "Capability: `fdd-test-capability-login`"
        
        ids = extract_backticked_ids(line, ACTOR_ID_RE)
        
        self.assertEqual(len(ids), 0)

    def test_extract_with_spaces(self):
        """Test extracting IDs with spaces around them."""
        line = "ID: `  fdd-test-actor-user  `"
        
        ids = extract_backticked_ids(line, ACTOR_ID_RE)
        
        self.assertEqual(len(ids), 1)
        self.assertEqual(ids[0], "fdd-test-actor-user")

    def test_extract_capability_ids(self):
        """Test extracting capability IDs."""
        line = "**Capabilities**: `fdd-test-capability-login`, `fdd-test-capability-logout`"
        
        ids = extract_backticked_ids(line, CAPABILITY_ID_RE)
        
        self.assertEqual(len(ids), 2)


class TestFieldBlockEdgeCases(unittest.TestCase):
    """Test edge cases for field_block function."""

    def test_field_at_end_of_lines(self):
        """Test extracting field at end of lines."""
        lines = [
            "Some text",
            "**Status**: Final",
        ]
        
        block = field_block(lines, "Status")
        
        self.assertIsNotNone(block)
        self.assertEqual(block["value"], "Final")
        self.assertEqual(len(block["tail"]), 0)

    def test_empty_field_value(self):
        """Test extracting field with empty value."""
        lines = [
            "**Status**: ",
            "Next line",
        ]
        
        block = field_block(lines, "Status")
        
        self.assertIsNotNone(block)
        self.assertEqual(block["value"], "")


if __name__ == "__main__":
    unittest.main()
