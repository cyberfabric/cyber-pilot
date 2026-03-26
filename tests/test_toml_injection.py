"""
Comprehensive tests for TOML injection prevention in agent generation.

Covers:
  - _escape_toml_basic_string: backslash, quote, control-char escaping
  - _escape_toml_multiline_string: backslash and triple-quote escaping
  - _render_toml_agent: multi-line developer_instructions round-trip
  - _build_openai_agent_file: full pipeline round-trip with dangerous content
  - _format_toml_entry: basic-string fields round-trip
  - model field escaping in _build_openai_agent_file
  - variable substitution inside multi-line strings
"""

from __future__ import annotations

import sys
import tomllib
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.commands.agents import (
    _build_openai_agent_file,
    _escape_toml_basic_string,
    _escape_toml_multiline_string,
    _format_toml_entry,
    _render_toml_agent,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_semantic_agent(name: str, description: str = "test agent") -> dict:
    return {"name": name, "description": description, "model": "inherit"}


@dataclass
class _FakeAgentEntry:
    id: str
    description: str = ""
    append: str = ""


def _roundtrip_toml(toml_text: str) -> dict:
    """Parse TOML text and return the resulting dict.  Raises on invalid TOML."""
    return tomllib.loads(toml_text)


# ===========================================================================
# _escape_toml_basic_string
# ===========================================================================

class TestEscapeTomlBasicString(unittest.TestCase):
    """Unit tests for escaping inside TOML basic (single-line) strings."""

    def test_plain_text_unchanged(self):
        self.assertEqual(_escape_toml_basic_string("hello world"), "hello world")

    def test_backslash_doubled(self):
        self.assertEqual(_escape_toml_basic_string("a\\b"), "a\\\\b")

    def test_double_quote_escaped(self):
        self.assertEqual(_escape_toml_basic_string('say "hi"'), 'say \\"hi\\"')

    def test_newline_escaped(self):
        self.assertEqual(_escape_toml_basic_string("a\nb"), "a\\nb")

    def test_carriage_return_escaped(self):
        self.assertEqual(_escape_toml_basic_string("a\rb"), "a\\rb")

    def test_tab_escaped(self):
        self.assertEqual(_escape_toml_basic_string("a\tb"), "a\\tb")

    def test_combined_special_chars(self):
        raw = 'path\\to\\"file"\n\t'
        escaped = _escape_toml_basic_string(raw)
        # Round-trip: wrap in quotes and parse
        toml_text = f'val = "{escaped}"'
        data = _roundtrip_toml(toml_text)
        self.assertEqual(data["val"], raw)

    def test_roundtrip_all_toml_escapes(self):
        """Every TOML basic-string escape sequence round-trips correctly."""
        raw = '\\\t\n\r"'
        escaped = _escape_toml_basic_string(raw)
        data = _roundtrip_toml(f'v = "{escaped}"')
        self.assertEqual(data["v"], raw)


# ===========================================================================
# _escape_toml_multiline_string
# ===========================================================================

class TestEscapeTomlMultilineString(unittest.TestCase):
    """Unit tests for escaping inside TOML multi-line basic strings."""

    def test_plain_text_unchanged(self):
        self.assertEqual(_escape_toml_multiline_string("hello"), "hello")

    def test_backslash_doubled(self):
        self.assertEqual(_escape_toml_multiline_string("a\\b"), "a\\\\b")

    def test_triple_quote_escaped(self):
        result = _escape_toml_multiline_string('before"""after')
        self.assertNotIn('"""a', result)
        # Verify round-trip
        toml_text = f'v = """\n{result}\n"""'
        data = _roundtrip_toml(toml_text)
        self.assertEqual(data["v"], 'before"""after\n')

    def test_backslash_before_triple_quote(self):
        """A backslash immediately before triple-quote must not create an escape ambiguity."""
        raw = 'end\\"""start'
        result = _escape_toml_multiline_string(raw)
        toml_text = f'v = """\n{result}\n"""'
        data = _roundtrip_toml(toml_text)
        self.assertEqual(data["v"], raw + "\n")

    def test_literal_backslash_n_preserved(self):
        """Literal \\n in source markdown must NOT become a newline in parsed TOML."""
        raw = r"Use \n to separate items"
        result = _escape_toml_multiline_string(raw)
        toml_text = f'v = """\n{result}\n"""'
        data = _roundtrip_toml(toml_text)
        self.assertEqual(data["v"], raw + "\n")

    def test_literal_backslash_t_preserved(self):
        raw = r"Use \t for tabs"
        result = _escape_toml_multiline_string(raw)
        toml_text = f'v = """\n{result}\n"""'
        data = _roundtrip_toml(toml_text)
        self.assertEqual(data["v"], raw + "\n")

    def test_literal_backslash_u_preserved(self):
        """\\uXXXX in source must not be interpreted as a TOML unicode escape."""
        raw = r"emoji: \u2603"
        result = _escape_toml_multiline_string(raw)
        toml_text = f'v = """\n{result}\n"""'
        data = _roundtrip_toml(toml_text)
        self.assertEqual(data["v"], raw + "\n")

    def test_invalid_toml_escape_no_longer_crashes(self):
        """Previously, \\p in source caused a TOML parse error. Now it round-trips."""
        raw = r"regex: \p{L}+"
        result = _escape_toml_multiline_string(raw)
        toml_text = f'v = """\n{result}\n"""'
        # Must not raise
        data = _roundtrip_toml(toml_text)
        self.assertEqual(data["v"], raw + "\n")

    def test_multiple_backslashes(self):
        raw = "a\\\\b"  # Two literal backslashes
        result = _escape_toml_multiline_string(raw)
        toml_text = f'v = """\n{result}\n"""'
        data = _roundtrip_toml(toml_text)
        self.assertEqual(data["v"], raw + "\n")

    def test_newlines_preserved_in_multiline(self):
        """Real newlines in multi-line strings are allowed and preserved."""
        raw = "line1\nline2\nline3"
        result = _escape_toml_multiline_string(raw)
        toml_text = f'v = """\n{result}\n"""'
        data = _roundtrip_toml(toml_text)
        self.assertEqual(data["v"], raw + "\n")

    def test_injection_attempt_via_triple_quote_closure(self):
        """Malicious content trying to close the multi-line string and inject keys."""
        raw = '"""\ninjected_key = "evil"\nmore = """'
        result = _escape_toml_multiline_string(raw)
        toml_text = f'[t]\nv = """\n{result}\n"""'
        data = _roundtrip_toml(toml_text)
        # The injected_key must NOT appear as a real key
        self.assertNotIn("injected_key", data.get("t", {}))
        self.assertIn("injected_key", data["t"]["v"])


# ===========================================================================
# _render_toml_agent (per-agent TOML)
# ===========================================================================

class TestRenderTomlAgentInjection(unittest.TestCase):
    """TOML injection tests for _render_toml_agent per-file rendering."""

    def test_backslash_in_agent_path_roundtrips(self):
        """Agent paths with backslashes produce valid TOML."""
        agent = _make_semantic_agent("t")
        result = _render_toml_agent(agent, "path\\to\\agent.md")
        data = _roundtrip_toml(result)
        self.assertIn("path\\to\\agent.md", data["developer_instructions"])

    def test_triple_quote_in_agent_path_roundtrips(self):
        agent = _make_semantic_agent("t")
        result = _render_toml_agent(agent, 'before"""after.md')
        data = _roundtrip_toml(result)
        self.assertIn('before"""after.md', data["developer_instructions"])

    def test_backslash_n_in_description_roundtrips(self):
        """Literal \\n in description must not become a newline."""
        agent = _make_semantic_agent("t", description=r"use \n here")
        result = _render_toml_agent(agent, "@/t.md")
        data = _roundtrip_toml(result)
        self.assertEqual(data["description"], r"use \n here")


# ===========================================================================
# _build_openai_agent_file
# ===========================================================================

class TestBuildOpenaiAgentFileInjection(unittest.TestCase):
    """End-to-end TOML injection tests for the v2 OpenAI agent builder."""

    def _build(
        self,
        source: str = "# Hello",
        append: str = "",
        model: str = "",
        variables: Optional[Dict[str, str]] = None,
        agent_id: str = "test-agent",
        description: str = "desc",
    ) -> str:
        agent = _FakeAgentEntry(id=agent_id, description=description, append=append)
        translated: Dict = {"sandbox_mode": "workspace-write"}
        if model:
            translated["model"] = model
        content, rel_out = _build_openai_agent_file(
            agent_id, agent, translated, source, ".codex/agents/{id}.md", variables,
        )
        return content

    def _build_and_parse(self, **kwargs) -> dict:
        content = self._build(**kwargs)
        self.assertTrue(content, "Expected non-empty TOML content")
        return _roundtrip_toml(content)

    # -- backslash in source content --

    def test_literal_backslash_n_in_source(self):
        data = self._build_and_parse(source=r"Use \n to separate items")
        instructions = data["agents"]["test_agent"]["developer_instructions"]
        self.assertIn(r"\n", instructions)
        self.assertNotIn("\x00", instructions)  # no corruption

    def test_literal_backslash_t_in_source(self):
        data = self._build_and_parse(source=r"col1\tcol2")
        instructions = data["agents"]["test_agent"]["developer_instructions"]
        self.assertIn(r"\t", instructions)

    def test_literal_backslash_u_in_source(self):
        data = self._build_and_parse(source=r"emoji \u2603 here")
        instructions = data["agents"]["test_agent"]["developer_instructions"]
        self.assertIn(r"\u2603", instructions)

    def test_invalid_escape_sequence_in_source(self):
        """\\p is not a valid TOML escape — must not crash the parser."""
        data = self._build_and_parse(source=r"regex: \p{L}+")
        self.assertIn(r"\p{L}+", data["agents"]["test_agent"]["developer_instructions"])

    def test_triple_quote_in_source_no_injection(self):
        data = self._build_and_parse(source='before"""\nevil = "injected"\n"""after')
        instructions = data["agents"]["test_agent"]["developer_instructions"]
        self.assertIn('"""', instructions)
        self.assertNotIn("evil", data["agents"]["test_agent"].get("evil", ""))

    def test_windows_path_in_source(self):
        data = self._build_and_parse(source=r"C:\Users\me\file.txt")
        self.assertIn(r"C:\Users\me\file.txt",
                       data["agents"]["test_agent"]["developer_instructions"])

    # -- backslash in append content --

    def test_backslash_in_append(self):
        data = self._build_and_parse(
            source="main content",
            append=r"appended path: C:\data\out",
        )
        instructions = data["agents"]["test_agent"]["developer_instructions"]
        self.assertIn(r"C:\data\out", instructions)

    def test_triple_quote_in_append_no_injection(self):
        data = self._build_and_parse(
            source="main",
            append='"""\nfoo = "bar"',
        )
        instructions = data["agents"]["test_agent"]["developer_instructions"]
        self.assertIn('"""', instructions)

    # -- model field escaping --

    def test_model_with_quotes_roundtrips(self):
        data = self._build_and_parse(model='gpt-4"turbo')
        self.assertEqual(data["agents"]["test_agent"]["model"], 'gpt-4"turbo')

    def test_model_with_backslash_roundtrips(self):
        data = self._build_and_parse(model="org\\model")
        self.assertEqual(data["agents"]["test_agent"]["model"], "org\\model")

    # -- variable substitution inside multi-line strings --

    def test_variable_with_backslash_roundtrips(self):
        data = self._build_and_parse(
            source="root is {cypilot_path}",
            variables={"cypilot_path": r"C:\projects\root"},
        )
        instructions = data["agents"]["test_agent"]["developer_instructions"]
        self.assertIn(r"C:\projects\root", instructions)

    def test_variable_with_triple_quote_no_injection(self):
        data = self._build_and_parse(
            source="val is {cypilot_path}",
            variables={"cypilot_path": '"""injected = true\n'},
        )
        instructions = data["agents"]["test_agent"]["developer_instructions"]
        self.assertNotIn("injected", data["agents"]["test_agent"].get("injected", ""))

    # -- combined stress test --

    def test_all_dangerous_chars_combined(self):
        """Source with every dangerous pattern still produces valid, correct TOML."""
        nasty_source = (
            'Line with \\backslash and "quotes"\n'
            "Tab\there and \\n literal newline ref\n"
            '""" triple-quote break attempt """\n'
            r"Unicode \u0041 and regex \p{L}+" + "\n"
            "end"
        )
        data = self._build_and_parse(source=nasty_source)
        instructions = data["agents"]["test_agent"]["developer_instructions"]
        # All content must survive the round-trip
        self.assertIn("\\backslash", instructions)
        self.assertIn('"quotes"', instructions)
        self.assertIn('"""', instructions)
        self.assertIn(r"\u0041", instructions)
        self.assertIn(r"\p{L}+", instructions)


# ===========================================================================
# _format_toml_entry (provenance / basic-string fields)
# ===========================================================================

class TestFormatTomlEntryInjection(unittest.TestCase):
    """Round-trip tests for _format_toml_entry with special characters."""

    def _entry_roundtrip(self, entry: dict, section: str = "agents") -> dict:
        lines = _format_toml_entry(section, entry)
        toml_text = "\n".join(lines)
        return _roundtrip_toml(toml_text)

    def test_backslash_in_all_fields(self):
        entry = {"id": "a", "description": "path\\to\\thing", "source": "dir\\file.md"}
        data = self._entry_roundtrip(entry)
        self.assertEqual(data["agents"][0]["description"], "path\\to\\thing")
        self.assertEqual(data["agents"][0]["source"], "dir\\file.md")

    def test_quotes_in_description(self):
        entry = {"id": "b", "description": 'say "hello"', "source": "/b.md"}
        data = self._entry_roundtrip(entry)
        self.assertEqual(data["agents"][0]["description"], 'say "hello"')

    def test_newline_in_description(self):
        entry = {"id": "c", "description": "line1\nline2"}
        data = self._entry_roundtrip(entry)
        self.assertEqual(data["agents"][0]["description"], "line1\nline2")


if __name__ == "__main__":
    unittest.main()
