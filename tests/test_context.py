"""
Tests for FddContext and related functions.

Tests cover:
- FddContext methods: get_template, get_all_templates, get_template_for_kind, get_all_kinds
- Global context functions: get_context, set_context, ensure_context
- Load errors property
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))

from fdd.utils.context import (
    FddContext,
    LoadedRule,
    get_context,
    set_context,
    ensure_context,
    _global_context,
)
from fdd.utils.artifacts_meta import ArtifactsMeta, Rule


def _make_mock_template(kind: str, blocks: list = None) -> MagicMock:
    """Create a mock Template with kind and blocks."""
    tmpl = MagicMock()
    tmpl.kind = kind
    tmpl.blocks = blocks or []
    return tmpl


def _make_mock_block(block_type: str, name: str) -> MagicMock:
    """Create a mock TemplateBlock."""
    block = MagicMock()
    block.type = block_type
    block.name = name
    return block


class TestFddContextMethods:
    """Tests for FddContext instance methods."""

    def _make_context(self) -> FddContext:
        """Create a mock FddContext with templates."""
        # Create mock templates
        prd_tmpl = _make_mock_template("PRD", [
            _make_mock_block("id", "fr"),
            _make_mock_block("id", "actor"),
        ])
        design_tmpl = _make_mock_template("DESIGN", [
            _make_mock_block("id", "component"),
            _make_mock_block("id", "seq"),
        ])
        feature_tmpl = _make_mock_template("FEATURE", [
            _make_mock_block("id", "flow"),
            _make_mock_block("id", "algo"),
        ])

        # Create rules
        rule1 = Rule(rule_id="fdd-sdlc", format="FDD", path="rules/sdlc")
        rule2 = Rule(rule_id="custom", format="FDD", path="rules/custom")

        loaded_rule1 = LoadedRule(
            rule=rule1,
            templates={"PRD": prd_tmpl, "DESIGN": design_tmpl},
        )
        loaded_rule2 = LoadedRule(
            rule=rule2,
            templates={"FEATURE": feature_tmpl},
        )

        # Create mock meta
        meta = MagicMock(spec=ArtifactsMeta)
        meta.project_root = ".."

        return FddContext(
            adapter_dir=Path("/fake/adapter"),
            project_root=Path("/fake/project"),
            meta=meta,
            rules={"fdd-sdlc": loaded_rule1, "custom": loaded_rule2},
            registered_systems={"myapp", "test-system"},
            _errors=["error1", "error2"],
        )

    def test_get_template_found(self):
        """get_template returns template when rule and kind exist."""
        ctx = self._make_context()
        tmpl = ctx.get_template("fdd-sdlc", "PRD")
        assert tmpl is not None
        assert tmpl.kind == "PRD"

    def test_get_template_rule_not_found(self):
        """get_template returns None when rule doesn't exist."""
        ctx = self._make_context()
        result = ctx.get_template("nonexistent-rule", "PRD")
        assert result is None

    def test_get_template_kind_not_found(self):
        """get_template returns None when kind doesn't exist in rule."""
        ctx = self._make_context()
        result = ctx.get_template("fdd-sdlc", "NONEXISTENT")
        assert result is None

    def test_get_all_templates(self):
        """get_all_templates returns all templates from all rules."""
        ctx = self._make_context()
        all_tmpls = ctx.get_all_templates()
        assert len(all_tmpls) == 3  # PRD, DESIGN, FEATURE
        assert "PRD" in all_tmpls
        assert "DESIGN" in all_tmpls
        assert "FEATURE" in all_tmpls

    def test_get_template_for_kind_found(self):
        """get_template_for_kind finds template from any rule."""
        ctx = self._make_context()
        # FEATURE is in 'custom' rule
        tmpl = ctx.get_template_for_kind("FEATURE")
        assert tmpl is not None
        assert tmpl.kind == "FEATURE"

    def test_get_template_for_kind_not_found(self):
        """get_template_for_kind returns None when kind not in any rule."""
        ctx = self._make_context()
        result = ctx.get_template_for_kind("NONEXISTENT")
        assert result is None

    def test_get_all_kinds(self):
        """get_all_kinds returns lowercase set of all artifact kinds."""
        ctx = self._make_context()
        kinds = ctx.get_all_kinds()
        assert kinds == {"prd", "design", "feature"}

    def test_get_known_id_kinds(self):
        """get_known_id_kinds extracts id kinds from template markers."""
        ctx = self._make_context()
        id_kinds = ctx.get_known_id_kinds()
        # PRD has fr, actor; DESIGN has component, seq; FEATURE has flow, algo
        assert id_kinds == {"fr", "actor", "component", "seq", "flow", "algo"}

    def test_load_errors(self):
        """load_errors returns errors collected during loading."""
        ctx = self._make_context()
        assert ctx.load_errors == ["error1", "error2"]


class TestGlobalContextFunctions:
    """Tests for global context getter/setter functions."""

    def teardown_method(self, method):
        """Reset global context after each test."""
        set_context(None)

    def test_get_context_initially_none(self):
        """get_context returns None when not set."""
        set_context(None)
        assert get_context() is None

    def test_set_and_get_context(self):
        """set_context stores context retrievable by get_context."""
        mock_ctx = MagicMock(spec=FddContext)
        set_context(mock_ctx)
        assert get_context() is mock_ctx

    def test_set_context_to_none(self):
        """set_context(None) clears the context."""
        mock_ctx = MagicMock(spec=FddContext)
        set_context(mock_ctx)
        set_context(None)
        assert get_context() is None

    @patch("fdd.utils.context.FddContext.load")
    def test_ensure_context_loads_when_none(self, mock_load):
        """ensure_context loads context when global is None."""
        set_context(None)
        mock_ctx = MagicMock(spec=FddContext)
        mock_load.return_value = mock_ctx

        result = ensure_context()

        mock_load.assert_called_once_with(None)
        assert result is mock_ctx
        assert get_context() is mock_ctx

    @patch("fdd.utils.context.FddContext.load")
    def test_ensure_context_passes_start_path(self, mock_load):
        """ensure_context passes start_path to FddContext.load."""
        set_context(None)
        mock_ctx = MagicMock(spec=FddContext)
        mock_load.return_value = mock_ctx
        start = Path("/some/path")

        result = ensure_context(start)

        mock_load.assert_called_once_with(start)

    def test_ensure_context_returns_existing(self):
        """ensure_context returns existing context without reloading."""
        existing_ctx = MagicMock(spec=FddContext)
        set_context(existing_ctx)

        with patch("fdd.utils.context.FddContext.load") as mock_load:
            result = ensure_context()
            mock_load.assert_not_called()
            assert result is existing_ctx


class TestFddContextLoad:
    """Tests for FddContext.load() method."""

    def teardown_method(self, method):
        """Reset global context after each test."""
        set_context(None)

    @patch("fdd.utils.files.find_adapter_directory")
    def test_load_returns_none_when_no_adapter(self, mock_find):
        """load returns None when adapter directory not found."""
        mock_find.return_value = None
        result = FddContext.load()
        assert result is None

    @patch("fdd.utils.context.load_artifacts_meta")
    @patch("fdd.utils.files.find_adapter_directory")
    def test_load_returns_none_on_meta_error(self, mock_find, mock_load_meta):
        """load returns None when artifacts.json fails to load."""
        mock_find.return_value = Path("/fake/adapter")
        mock_load_meta.return_value = (None, "Some error")

        result = FddContext.load()
        assert result is None
