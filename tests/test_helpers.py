"""Test helper functions for parsing artifacts."""

import unittest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))

from fdd.utils.helpers import (
    find_present_section_ids,
    parse_prd_model,
    load_adr_entries,
    scan_adr_directory,
)

from fdd.utils.markdown import (
    prd_block_bounds,
    design_item_block_bounds,
    extract_id_payload_block,
    extract_heading_block,
    extract_payload_block,
    find_anchor_idx_for_id,
    list_items,
    list_section_entries,
    read_feature_entry,
    read_heading_block_by_title,
    read_letter_section,
    resolve_heading,
    resolve_under_heading,
)

from fdd.utils.search import (
    compile_trace_regex,
    _match_phase_inst_in_line,
    definition_hits_in_file,
    iter_candidate_definition_files,
    parse_trace_query,
    scan_ids,
    where_defined_internal,
    where_used,
)


class TestFindPresentSectionIds(unittest.TestCase):
    """Test find_present_section_ids function."""

    def test_find_section_ids_single_section(self):
        """Test finding single section ID."""
        text = """# Document

## A. First Section

Some content here.
"""
        result = find_present_section_ids(text)
        self.assertEqual(result, ["A"])

    def test_find_section_ids_multiple_sections(self):
        """Test finding multiple section IDs."""
        text = """# Document

## A. First Section

Content A

## B. Second Section

Content B

## C. Third Section

Content C
"""
        result = find_present_section_ids(text)
        self.assertEqual(result, ["A", "B", "C"])

    def test_find_section_ids_with_subsections(self):
        """Test that subsections (###) are not captured as section IDs."""
        text = """# Document

## A. First Section

### A.1 Subsection

Content

## B. Second Section

### B.1 Subsection
"""
        result = find_present_section_ids(text)
        self.assertEqual(result, ["A", "B"])

    def test_find_section_ids_empty_text(self):
        """Test with empty text."""
        result = find_present_section_ids("")
        self.assertEqual(result, [])

    def test_find_section_ids_no_sections(self):
        """Test with text that has no sections."""
        text = """# Document

Some content without sections.

More content.
"""
        result = find_present_section_ids(text)
        self.assertEqual(result, [])

    def test_find_section_ids_preserves_order(self):
        """Test that section order is preserved."""
        text = """## C. Third
## A. First
## B. Second
"""
        result = find_present_section_ids(text)
        self.assertEqual(result, ["C", "A", "B"])


class TestParsePRDModel(unittest.TestCase):
    """Test parse_prd_model function."""

    def test_parse_prd_model_basic(self):
        """Test basic parsing of actors, functional requirements, and use cases."""
        text = """# PRD

## B. Actors

- **ID**: `fdd-app-actor-admin`
- **ID**: `fdd-app-actor-user`

## C. Functional Requirements

### FR-001: Manage Users

**ID**: `fdd-app-fr-manage-users`

**Actors**: `fdd-app-actor-admin`

### FR-002: View Dashboard

**ID**: `fdd-app-fr-view-dashboard`

**Actors**: `fdd-app-actor-user`, `fdd-app-actor-admin`

## D. Use Cases

- **ID**: `fdd-app-usecase-login`
- **ID**: `fdd-app-usecase-logout`
"""
        actors, capabilities, usecases = parse_prd_model(text)
        
        # Verify actors
        self.assertIn("fdd-app-actor-admin", actors)
        self.assertIn("fdd-app-actor-user", actors)
        self.assertEqual(len(actors), 2)
        
        # Verify functional requirements
        self.assertIn("fdd-app-fr-manage-users", capabilities)
        self.assertIn("fdd-app-fr-view-dashboard", capabilities)
        
        # Verify functional requirement-actor mappings
        self.assertIn("fdd-app-actor-admin", capabilities["fdd-app-fr-manage-users"])
        self.assertIn("fdd-app-actor-user", capabilities["fdd-app-fr-view-dashboard"])
        self.assertIn("fdd-app-actor-admin", capabilities["fdd-app-fr-view-dashboard"])
        
        # Verify use cases
        self.assertIn("fdd-app-usecase-login", usecases)
        self.assertIn("fdd-app-usecase-logout", usecases)
        self.assertEqual(len(usecases), 2)

    def test_parse_prd_model_empty(self):
        """Test parsing empty text."""
        actors, capabilities, usecases = parse_prd_model("")
        
        self.assertEqual(len(actors), 0)
        self.assertEqual(len(capabilities), 0)
        self.assertEqual(len(usecases), 0)

    def test_parse_prd_model_section_c_variations(self):
        """Test that both 'Section C' and 'C. Functional Requirements' are recognized."""
        text1 = """## C. Functional Requirements

**ID**: `fdd-app-fr-test`

**Actors**: `fdd-app-actor-test`
"""
        
        text2 = """## Section C: Functional Requirements

**ID**: `fdd-app-fr-test`

**Actors**: `fdd-app-actor-test`
"""
        
        _, caps1, _ = parse_prd_model(text1)
        _, caps2, _ = parse_prd_model(text2)
        
        self.assertIn("fdd-app-fr-test", caps1)
        self.assertIn("fdd-app-fr-test", caps2)

    def test_parse_prd_model_capability_without_actors(self):
        """Test functional requirement that doesn't reference any actors."""
        text = """## C. Functional Requirements

### FR-001: Generic Requirement

**ID**: `fdd-app-fr-generic`

No actors referenced.
"""
        _, capabilities, _ = parse_prd_model(text)
        
        self.assertIn("fdd-app-fr-generic", capabilities)
        self.assertEqual(len(capabilities["fdd-app-fr-generic"]), 0)

    def test_parse_prd_model_multiple_actors_per_capability(self):
        """Test functional requirement with multiple actor references."""
        text = """## C. Functional Requirements

### FR-001: Multi-Actor Requirement

**ID**: `fdd-app-fr-multi`

**Actors**: `fdd-app-actor-one`, `fdd-app-actor-two`, `fdd-app-actor-three`

Additional line: `fdd-app-actor-four`
"""
        _, capabilities, _ = parse_prd_model(text)
        
        cap_actors = capabilities["fdd-app-fr-multi"]
        self.assertEqual(len(cap_actors), 4)
        self.assertIn("fdd-app-actor-one", cap_actors)
        self.assertIn("fdd-app-actor-two", cap_actors)
        self.assertIn("fdd-app-actor-three", cap_actors)
        self.assertIn("fdd-app-actor-four", cap_actors)

    def test_parse_prd_model_stops_at_next_section(self):
        """Test that capability parsing stops at next section."""
        text = """## C. Functional Requirements

**ID**: `fdd-app-fr-test`

**Actors**: `fdd-app-actor-test`

## D. Use Cases

**ID**: `fdd-app-fr-not-in-c`

**Actors**: `fdd-app-actor-not-in-c`
"""
        _, capabilities, _ = parse_prd_model(text)
        
        self.assertIn("fdd-app-fr-test", capabilities)
        self.assertNotIn("fdd-app-fr-not-in-c", capabilities)


class TestAdrDirectoryHelpers(unittest.TestCase):
    def test_load_adr_entries_missing_path(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            adrs, issues = load_adr_entries(td / "ADR")
            self.assertEqual(adrs, [])
            self.assertGreater(len(issues), 0)

    def test_load_adr_entries_file_rejected(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            p = td / "adr-file.md"
            p.write_text("# ADR-0001: X\n", encoding="utf-8")
            adrs, issues = load_adr_entries(p)
            self.assertEqual(adrs, [])
            self.assertTrue(any("must be a directory" in str(i.get("message")) for i in issues))

    def test_scan_adr_directory_no_files(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            td.mkdir(parents=True, exist_ok=True)
            adrs, issues = scan_adr_directory(td)
            self.assertEqual(adrs, [])
            self.assertGreater(len(issues), 0)

    def test_scan_adr_directory_skips_invalid_filenames(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "bad.md").write_text("# ADR-0001: X\n", encoding="utf-8")
            adrs, issues = scan_adr_directory(td)
            self.assertEqual(adrs, [])
            self.assertGreater(len(issues), 0)

    def test_scan_adr_directory_multiple_headings_fails(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            p = td / "0001-fdd-app-adr-test.md"
            p.write_text("# ADR-0001: A\n# ADR-0001: B\n", encoding="utf-8")
            adrs, issues = scan_adr_directory(td)
            self.assertEqual(adrs, [])
            self.assertTrue(any("must contain exactly one ADR heading" in str(i.get("message")) for i in issues))

    def test_scan_adr_directory_heading_must_be_h1(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            p = td / "0001-fdd-app-adr-test.md"
            p.write_text("## ADR-0001: A\n**ADR ID**: `fdd-app-adr-test`\n", encoding="utf-8")
            adrs, issues = scan_adr_directory(td)
            self.assertEqual(len(adrs), 1)
            self.assertTrue(any("H1" in str(i.get("message")) for i in issues))

    def test_scan_adr_directory_id_mismatch_and_sequential_checks(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            p1 = td / "0001-fdd-app-adr-one.md"
            p1.write_text("# ADR-0001: One\n**ADR ID**: `fdd-app-adr-two`\n", encoding="utf-8")
            p3 = td / "0003-fdd-app-adr-three.md"
            p3.write_text("# ADR-0003: Three\n**ADR ID**: `fdd-app-adr-three`\n", encoding="utf-8")
            adrs, issues = scan_adr_directory(td)
            self.assertEqual(len(adrs), 2)
            self.assertTrue(any("must match filename" in str(i.get("message")) for i in issues))
            self.assertTrue(any("sequential" in str(i.get("message")) for i in issues))


class TestMarkdownUtils(unittest.TestCase):
    def test_extract_heading_block_from_body_line(self) -> None:
        lines = [
            "# Top\n",
            "intro\n",
            "## Section B\n",
            "b1\n",
            "### Inner\n",
            "inner text\n",
            "## Section C\n",
            "c1\n",
        ]

        start, end = extract_heading_block(lines, 5)
        self.assertEqual(start, 4)
        self.assertEqual(end, 6)

    def test_resolve_under_heading_returns_bounds_and_level(self) -> None:
        lines = [
            "# Top\n",
            "intro\n",
            "## Section B\n",
            "b1\n",
            "### Inner\n",
            "inner text\n",
            "## Section C\n",
            "c1\n",
        ]

        resolved = resolve_under_heading(lines, "Section B")
        self.assertIsNotNone(resolved)
        assert resolved is not None
        start, end, level = resolved
        self.assertEqual((start, end, level), (2, 6, 2))

    def test_find_anchor_idx_for_id_prefers_id_line(self) -> None:
        fid = "fdd-example-feature-x-req-do-thing"
        lines = [
            "# Doc\n",
            f"- **ID**: `{fid}`\n",
            f"## {fid}\n",
        ]

        idx = find_anchor_idx_for_id(lines, fid)
        self.assertEqual(idx, 1)

    def test_find_anchor_idx_for_id_falls_back_to_heading(self) -> None:
        fid = "fdd-example-feature-x-req-do-thing"
        lines = [
            "# Doc\n",
            f"## {fid}\n",
            "body\n",
        ]
        idx = find_anchor_idx_for_id(lines, fid)
        self.assertEqual(idx, 1)

    def test_find_anchor_idx_for_id_falls_back_to_plain_line(self) -> None:
        fid = "fdd-example-feature-x-req-do-thing"
        lines = [
            "# Doc\n",
            f"some {fid} in body\n",
        ]
        idx = find_anchor_idx_for_id(lines, fid)
        self.assertEqual(idx, 1)

    def test_prd_block_bounds_returns_enclosing_heading_block(self) -> None:
        lines = [
            "## B. Actors\n",
            "\n",
            "#### Admin\n",
            "**ID**: `fdd-app-actor-admin`\n",
            "extra\n",
            "#### User\n",
            "**ID**: `fdd-app-actor-user`\n",
        ]

        bounds = prd_block_bounds(lines, section_start=0, section_end=len(lines), id_idx=3)
        self.assertEqual(bounds, (2, 5))

    def test_design_item_block_bounds_respects_boundaries(self) -> None:
        lines = [
            "## A. Section\n",
            "\n",
            "#### Item One\n",
            "some text\n",
            "- **ID**: `fdd-example-item-one`\n",
            "more text\n",
            "**Outputs**:\n",
            "- ok\n",
            "#### Item Two\n",
        ]

        start, end = design_item_block_bounds(lines, start=0, end=len(lines), id_idx=4)
        self.assertEqual((start, end), (2, 6))

    def test_read_feature_entry_finds_bounds(self) -> None:
        fid = "fdd-app-feature-x"
        lines = [
            "# Features\n",
            f"### 1. [{fid}](feature-x/) ✅ HIGH\n",
            "a\n",
            "### 2. [fdd-app-feature-y](feature-y/) ✅ HIGH\n",
            "b\n",
        ]
        b = read_feature_entry(lines, fid)
        self.assertEqual(b, (1, 3))

    def test_read_heading_block_by_title_not_found_returns_none(self) -> None:
        lines = ["# Top\n", "x\n"]
        self.assertIsNone(read_heading_block_by_title(lines, "Missing"))

    def test_resolve_heading_found_and_not_found(self) -> None:
        lines = [
            "# Top\n",
            "x\n",
            "## Section\n",
            "y\n",
            "## Other\n",
        ]
        self.assertIsNone(resolve_heading(lines, "Nope"))
        resolved = resolve_heading(lines, "Section")
        self.assertIsNotNone(resolved)
        assert resolved is not None
        idx, level, end = resolved
        self.assertEqual((idx, level, end), (2, 2, 4))

    def test_extract_payload_block_edge_cases(self) -> None:
        lines = ["<!-- fdd-id-content -->\n", "a\n"]
        self.assertIsNone(extract_payload_block(lines, start_idx=-1))
        self.assertIsNone(extract_payload_block(lines, start_idx=10))
        self.assertIsNone(extract_payload_block(lines, start_idx=1))
        self.assertIsNone(extract_payload_block(lines, start_idx=0))

        lines2 = ["<!-- fdd-id-content -->\n", "a\n", "<!-- fdd-id-content -->\n"]
        self.assertEqual(extract_payload_block(lines2, start_idx=0), (0, 2))

    def test_extract_id_payload_block_none_and_found(self) -> None:
        lines = [
            "**ID**: `fdd-x`\n",
            "x\n",
        ]
        self.assertIsNone(extract_id_payload_block(lines, id_idx=0))

        lines2 = [
            "**ID**: `fdd-x`\n",
            "\n",
            "<!-- fdd-id-content -->\n",
            "p\n",
            "<!-- fdd-id-content -->\n",
        ]
        payload = extract_id_payload_block(lines2, id_idx=0)
        self.assertIsNotNone(payload)
        assert payload is not None
        self.assertEqual(payload.get("open_idx"), 2)
        self.assertEqual(payload.get("close_idx"), 4)
        self.assertEqual(payload.get("text"), "p")

    def test_list_items_features_manifest_and_filtering(self) -> None:
        lines = [
            "# Features\n",
            "### 1. [fdd-app-feature-a](feature-a/) ✅ HIGH\n",
            "### 2. [fdd-app-feature-b](feature-b/) ✅ HIGH\n",
        ]
        items = list_items(
            kind="features-manifest",
            artifact_name="FEATURES.md",
            lines=lines,
            active_lines=lines,
            base_offset=0,
            lod="summary",
            pattern="feature-b",
            regex=False,
            type_filter="feature",
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], "fdd-app-feature-b")

        items_rx = list_items(
            kind="features-manifest",
            artifact_name="FEATURES.md",
            lines=lines,
            active_lines=lines,
            base_offset=0,
            lod="summary",
            pattern=r"feature-[ab]$",
            regex=True,
            type_filter=None,
        )
        self.assertEqual(len(items_rx), 2)

    def test_read_letter_section_is_case_insensitive(self) -> None:
        lines = [
            "# Doc\n",
            "## A. First\n",
            "a\n",
            "## B. Second\n",
            "b\n",
        ]

        sec = read_letter_section(lines, "b")
        self.assertEqual(sec, (3, 5))

    def test_list_section_entries_features_manifest(self) -> None:
        lines = [
            "# Features\n",
            "\n",
            "### 1. [Feature One](feature-one/) ✅ HIGH\n",
            "### 2. [Feature Two](feature-two/) ⏳ MEDIUM\n",
        ]

        entries = list_section_entries(lines, kind="features-manifest")
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["line"], 3)
        self.assertEqual(entries[0]["feature_id"], "Feature One")
        self.assertEqual(entries[0]["dir"], "feature-one/")
        self.assertEqual(entries[0]["emoji"], "✅")
        self.assertEqual(entries[0]["priority"], "HIGH")

    def test_list_items_generic_adr_summary(self) -> None:
        # ADR is directory-based; this helper does not have filesystem context.
        # Ensure it behaves deterministically and does not crash.
        items = list_items(
            kind="adr",
            artifact_name="ADR",
            lines=[],
            active_lines=[],
            base_offset=0,
            lod="summary",
            pattern=None,
            regex=False,
            type_filter=None,
        )
        self.assertEqual(items, [])

    def test_list_items_generic_prd_summary(self) -> None:
        a1 = "fdd-app-actor-admin"
        c1 = "fdd-app-fr-manage"
        u1 = "fdd-app-usecase-login"
        lines = [
            "# PRD\n",
            "\n",
            "## B. Actors\n",
            "\n",
            "#### Admin\n",
            f"**ID**: `{a1}`\n",
            "\n",
            "## C. Functional Requirements\n",
            "\n",
            "#### Manage\n",
            f"**ID**: `{c1}`\n",
            "\n",
            "## D. Use Cases\n",
            "\n",
            "#### Login\n",
            f"**ID**: `{u1}`\n",
        ]

        items = list_items(
            kind="generic",
            artifact_name="PRD.md",
            lines=lines,
            active_lines=lines,
            base_offset=0,
            lod="summary",
            pattern=None,
            regex=False,
            type_filter=None,
        )

        self.assertEqual([it["type"] for it in items], ["actor", "functional-requirement", "usecase"])
        self.assertEqual([it["id"] for it in items], [a1, c1, u1])
        self.assertEqual(items[0]["title"], "Admin")
        self.assertEqual(items[0]["section"], "B")

    def test_list_items_overall_design_checked_and_title(self) -> None:
        rid = "fdd-app-req-login"
        lines = [
            "# Overall Design\n",
            "\n",
            "## A. Requirements\n",
            "- [x] **ID**: `fdd-app-req-login`\n",
        ]

        items = list_items(
            kind="overall-design",
            artifact_name="DESIGN.md",
            lines=lines,
            active_lines=lines,
            base_offset=0,
            lod="summary",
            pattern=None,
            regex=False,
            type_filter=None,
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], rid)
        self.assertEqual(items[0]["type"], "requirement")
        self.assertEqual(items[0]["checked"], True)
        self.assertEqual(items[0]["title"], "A. Requirements")

    def test_list_items_feature_design_checked_and_title(self) -> None:
        fid = "fdd-app-feature-x-algo-do-thing"
        lines = [
            "# Feature: X\n",
            "\n",
            "## C. Algorithms (FDL)\n",
            "### Algo\n",
            "- [ ] **ID**: `fdd-app-feature-x-algo-do-thing`\n",
        ]

        items = list_items(
            kind="feature-design",
            artifact_name="DESIGN.md",
            lines=lines,
            active_lines=lines,
            base_offset=0,
            lod="summary",
            pattern=None,
            regex=False,
            type_filter=None,
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], fid)
        self.assertEqual(items[0]["type"], "algo")
        self.assertEqual(items[0]["checked"], False)
        self.assertEqual(items[0]["title"], "Algo")


class TestSearchUtils(unittest.TestCase):
    def test_compile_trace_regex_matches_variants(self) -> None:
        base = "fdd-app-feature-x-algo-do-thing"
        rx = compile_trace_regex(base, "ph-1", "inst-ok")

        self.assertIsNotNone(rx.search(f"// {base}:ph-1:inst-ok"))
        self.assertIsNotNone(rx.search(f"// {base} `ph-1` `inst-ok`"))
        self.assertIsNotNone(rx.search(f"// {base} :ph-1 :inst-ok"))

    def test_parse_trace_query_variants(self) -> None:
        base, ph, inst = parse_trace_query("@fdd-x-flow-y:ph-1:inst-a")
        self.assertEqual((base, ph, inst), ("fdd-x-flow-y", "ph-1", "inst-a"))

        base, ph, inst = parse_trace_query("fdd-x:fdd-y:ph-1")
        self.assertEqual((base, ph, inst), ("fdd-y", "ph-1", None))

        base, ph, inst = parse_trace_query("fdd-x:inst-a:ph-1")
        self.assertEqual((base, ph, inst), ("fdd-x", "ph-1", "inst-a"))

    def test_match_phase_inst_in_line_rules(self) -> None:
        self.assertIsNone(_match_phase_inst_in_line("x", phase=None, inst=None))
        self.assertIsNone(_match_phase_inst_in_line("x", phase="ph-1", inst=None))

        seg = _match_phase_inst_in_line("do :ph-1 now", phase="ph-1", inst=None)
        self.assertEqual(seg, ("phase", 3))

        seg = _match_phase_inst_in_line("ok inst-a", phase=None, inst="inst-a")
        self.assertEqual(seg, ("inst", 3))

        self.assertIsNone(_match_phase_inst_in_line("inst-a then ph-1", phase="ph-1", inst="inst-a"))

    def test_definition_hits_in_file_adr_heading(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "architecture").mkdir(parents=True)
            adr_dir = td / "architecture" / "ADR" / "general"
            adr_dir.mkdir(parents=True)
            p = adr_dir / "0001-fdd-app-adr-title.md"
            p.write_text("# ADR-0001: Title\n\ntext\n", encoding="utf-8")
            hits = definition_hits_in_file(path=p, root=td, needle="ADR-0001", include_tags=False)
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["match"], "adr_heading")

    def test_definition_hits_in_file_include_tags(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            p = td / "src.py"
            needle = "fdd-app-feature-x-algo-do-thing"
            p.write_text(f"// @fdd-flow:{needle}:ph-1\n", encoding="utf-8")
            hits = definition_hits_in_file(path=p, root=td, needle=needle, include_tags=True)
            self.assertTrue(any(h.get("match") == "tag" for h in hits))

    def test_scan_ids_filters_by_kind_pattern_and_all_ids(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            p = td / "doc.md"
            p.write_text("**ID**: `fdd-app-actor-a`\nADR-0001\n", encoding="utf-8")

            hits_fdd = scan_ids(
                root=p,
                pattern="actor",
                regex=False,
                kind="fdd",
                include=None,
                exclude=None,
                max_bytes=1_000_000,
                all_ids=True,
            )
            self.assertEqual(len(hits_fdd), 1)
            self.assertEqual(hits_fdd[0]["kind"], "fdd")

            hits_adr = scan_ids(
                root=p,
                pattern=r"ADR-\\d{4}",
                regex=True,
                kind="adr",
                include=None,
                exclude=None,
                max_bytes=1_000_000,
                all_ids=True,
            )
            self.assertEqual(len(hits_adr), 1)
            self.assertEqual(hits_adr[0]["id"], "ADR-0001")

    def test_iter_candidate_definition_files_prefers_expected_files(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "architecture" / "features" / "feature-x").mkdir(parents=True)
            (td / "architecture" / "features").mkdir(parents=True, exist_ok=True)

            (td / "architecture" / "PRD.md").write_text("# Biz\n", encoding="utf-8")
            (td / "architecture" / "DESIGN.md").write_text("# Design\n", encoding="utf-8")
            (td / "architecture" / "ADR" / "general").mkdir(parents=True, exist_ok=True)
            (td / "architecture" / "ADR" / "general" / "0001-fdd-app-adr-0001.md").write_text("# ADR-0001: X\n\n**ADR ID**: `fdd-app-adr-0001`\n\n## Context and Problem Statement\n\nX\n\n## Considered Options\n\nX\n\n## Decision Outcome\n\nChosen option: \"X\", because X.\n\n## Related Design Elements\n\n- `fdd-app-req-login`\n", encoding="utf-8")
            (td / "architecture" / "features" / "FEATURES.md").write_text("# Features\n", encoding="utf-8")
            (td / "architecture" / "features" / "feature-x" / "DESIGN.md").write_text("# Feature\n", encoding="utf-8")

            actor = "fdd-app-actor-admin"
            req = "fdd-app-req-login"
            adr = "ADR-0001"
            f_adr = "fdd-app-adr-0001"
            algo = "fdd-app-feature-x-algo-do-thing"

            actor_files = iter_candidate_definition_files(td, needle=actor)
            self.assertTrue(any(str(p).endswith("architecture/PRD.md") for p in actor_files))

            req_files = iter_candidate_definition_files(td, needle=req)
            self.assertTrue(any(str(p).endswith("architecture/DESIGN.md") for p in req_files))

            adr_files = iter_candidate_definition_files(td, needle=adr)
            self.assertTrue(any("/architecture/ADR/" in str(p).replace("\\", "/") for p in adr_files))

            fadr_files = iter_candidate_definition_files(td, needle=f_adr)
            self.assertTrue(any("/architecture/ADR/" in str(p).replace("\\", "/") for p in fadr_files))

            algo_files = iter_candidate_definition_files(td, needle=algo)
            self.assertTrue(any("architecture/features/" in str(p) and str(p).endswith("/DESIGN.md") for p in algo_files))

    def test_definition_hits_in_file_prd_filters_by_section(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "architecture").mkdir(parents=True)
            p = td / "architecture" / "PRD.md"
            fid = "fdd-app-actor-admin"
            p.write_text(
                "\n".join(
                    [
                        "# Biz",
                        "",
                        "## B. Actors",
                        "",
                        "#### Admin",
                        f"**ID**: `{fid}`",
                        "",
                        "## C. Capabilities",
                        "",
                        f"**ID**: `{fid}`",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            hits = definition_hits_in_file(path=p, root=td, needle=fid, include_tags=False)
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["match"], "id_line")
            self.assertEqual(hits[0]["path"], "architecture/PRD.md")

    def test_definition_hits_in_file_design_filters_by_subsection(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "architecture").mkdir(parents=True)
            p = td / "architecture" / "DESIGN.md"
            rid = "fdd-app-req-login"
            p.write_text(
                "\n".join(
                    [
                        "# Design",
                        "",
                        "## A. Overview",
                        "",
                        "## B. Requirements",
                        "",
                        "### 1. Functional Requirements",
                        f"- [ ] **ID**: `{rid}`",
                        "",
                        "### 2. NFR",
                        f"- [ ] **ID**: `fdd-app-nfr-fast`",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            hits = definition_hits_in_file(path=p, root=td, needle=rid, include_tags=False)
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["match"], "id_line")
            self.assertEqual(hits[0]["path"], "architecture/DESIGN.md")

    def test_where_defined_internal_returns_segment_defs_for_phase_inst(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "architecture" / "features" / "feature-x").mkdir(parents=True)

            base = "fdd-app-feature-x-algo-do-thing"
            inst = "inst-return-ok"
            (td / "architecture" / "features" / "feature-x" / "DESIGN.md").write_text(
                "\n".join(
                    [
                        "# Feature: X",
                        "",
                        "## C. Algorithms (FDL)",
                        "### Algo",
                        "",
                        f"- [ ] **ID**: `{base}`",
                        "",
                        f"1. [ ] - `ph-1` - RETURN ok - `{inst}`",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            raw = f"{base}:ph-1:{inst}"
            _, defs, ctx_defs = where_defined_internal(
                root=td,
                raw_id=raw,
                include_tags=False,
                includes=None,
                excludes=None,
                max_bytes=1_000_000,
            )

            self.assertTrue(len(ctx_defs) >= 1)
            self.assertTrue(any(d.get("segment") == "inst" for d in defs))

    def test_where_used_excludes_definition_lines(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "architecture" / "features" / "feature-x").mkdir(parents=True)
            (td / "src").mkdir(parents=True)

            base = "fdd-app-feature-x-algo-do-thing"
            inst = "inst-return-ok"
            (td / "architecture" / "features" / "feature-x" / "DESIGN.md").write_text(
                "\n".join(
                    [
                        "# Feature: X",
                        "",
                        "## C. Algorithms (FDL)",
                        "### Algo",
                        "",
                        f"- [ ] **ID**: `{base}`",
                        "",
                        f"1. [ ] - `ph-1` - RETURN ok - `{inst}`",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (td / "src" / "lib.rs").write_text(
                f"// usage {base}:ph-1:{inst}\n",
                encoding="utf-8",
            )

            raw = f"{base}:ph-1:{inst}"
            _base, _ph, _inst, hits = where_used(root=td, raw_id=raw, include=None, exclude=None, max_bytes=1_000_000)
            paths = [h["path"] for h in hits]
            self.assertIn("src/lib.rs", paths)
            self.assertNotIn("architecture/features/feature-x/DESIGN.md", paths)

    def test_scan_ids_deduplicates_by_default(self) -> None:
        with TemporaryDirectory() as tds:
            td = Path(tds)
            p = td / "doc.md"
            p.write_text(
                "\n".join(
                    [
                        "**ID**: `fdd-app-actor-admin`",
                        "**ID**: `fdd-app-actor-admin`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            hits = scan_ids(
                root=p,
                pattern=None,
                regex=False,
                kind="fdd",
                include=None,
                exclude=None,
                max_bytes=1_000_000,
                all_ids=False,
            )
            self.assertEqual(len(hits), 1)


if __name__ == "__main__":
    unittest.main()
