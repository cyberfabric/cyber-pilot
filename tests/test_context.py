"""
Tests for SpiderContext and related functions.

Tests cover:
- SpiderContext methods: get_template, get_template_for_kind, get_known_id_kinds
- Global context functions: get_context, set_context, ensure_context
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "spider" / "scripts"))

from spider.utils.context import (
    SpiderContext,
    LoadedWeaver,
    get_context,
    set_context,
    ensure_context,
    _global_context,
)
from spider.utils.artifacts_meta import ArtifactsMeta, Weaver


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


class TestSpiderContextMethods:
    """Tests for SpiderContext instance methods."""

    def _make_context(self) -> SpiderContext:
        """Create a mock SpiderContext with templates."""
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

        # Create weavers
        weaver1 = Weaver(weaver_id="spider-sdlc", format="Spider", path="weavers/sdlc")
        weaver2 = Weaver(weaver_id="custom", format="Spider", path="weavers/custom")

        loaded_weaver1 = LoadedWeaver(
            weaver=weaver1,
            templates={"PRD": prd_tmpl, "DESIGN": design_tmpl},
        )
        loaded_weaver2 = LoadedWeaver(
            weaver=weaver2,
            templates={"FEATURE": feature_tmpl},
        )

        # Create mock meta
        meta = MagicMock(spec=ArtifactsMeta)
        meta.project_root = ".."

        return SpiderContext(
            adapter_dir=Path("/fake/adapter"),
            project_root=Path("/fake/project"),
            meta=meta,
            weavers={"spider-sdlc": loaded_weaver1, "custom": loaded_weaver2},
            registered_systems={"myapp", "test-system"},
            _errors=["error1", "error2"],
        )

    def test_get_template_found(self):
        """get_template returns template when weaver and kind exist."""
        ctx = self._make_context()
        tmpl = ctx.get_template("spider-sdlc", "PRD")
        assert tmpl is not None
        assert tmpl.kind == "PRD"

    def test_get_template_weaver_not_found(self):
        """get_template returns None when weaver doesn't exist."""
        ctx = self._make_context()
        result = ctx.get_template("nonexistent-weaver", "PRD")
        assert result is None

    def test_get_template_kind_not_found(self):
        """get_template returns None when kind doesn't exist in weaver."""
        ctx = self._make_context()
        result = ctx.get_template("spider-sdlc", "NONEXISTENT")
        assert result is None

    def test_get_template_for_kind_found(self):
        """get_template_for_kind finds template from any weaver."""
        ctx = self._make_context()
        # FEATURE is in 'custom' weaver
        tmpl = ctx.get_template_for_kind("FEATURE")
        assert tmpl is not None
        assert tmpl.kind == "FEATURE"

    def test_get_template_for_kind_not_found(self):
        """get_template_for_kind returns None when kind not in any weaver."""
        ctx = self._make_context()
        result = ctx.get_template_for_kind("NONEXISTENT")
        assert result is None

    def test_get_known_id_kinds(self):
        """get_known_id_kinds extracts id kinds from template markers."""
        ctx = self._make_context()
        id_kinds = ctx.get_known_id_kinds()
        # PRD has fr, actor; DESIGN has component, seq; FEATURE has flow, algo
        assert id_kinds == {"fr", "actor", "component", "seq", "flow", "algo"}


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
        mock_ctx = MagicMock(spec=SpiderContext)
        set_context(mock_ctx)
        assert get_context() is mock_ctx

    def test_set_context_to_none(self):
        """set_context(None) clears the context."""
        mock_ctx = MagicMock(spec=SpiderContext)
        set_context(mock_ctx)
        set_context(None)
        assert get_context() is None

    @patch("spider.utils.context.SpiderContext.load")
    def test_ensure_context_loads_when_none(self, mock_load):
        """ensure_context loads context when global is None."""
        set_context(None)
        mock_ctx = MagicMock(spec=SpiderContext)
        mock_load.return_value = mock_ctx

        result = ensure_context()

        mock_load.assert_called_once_with(None)
        assert result is mock_ctx
        assert get_context() is mock_ctx

    @patch("spider.utils.context.SpiderContext.load")
    def test_ensure_context_passes_start_path(self, mock_load):
        """ensure_context passes start_path to SpiderContext.load."""
        set_context(None)
        mock_ctx = MagicMock(spec=SpiderContext)
        mock_load.return_value = mock_ctx
        start = Path("/some/path")

        result = ensure_context(start)

        mock_load.assert_called_once_with(start)

    def test_ensure_context_returns_existing(self):
        """ensure_context returns existing context without reloading."""
        existing_ctx = MagicMock(spec=SpiderContext)
        set_context(existing_ctx)

        with patch("spider.utils.context.SpiderContext.load") as mock_load:
            result = ensure_context()
            mock_load.assert_not_called()
            assert result is existing_ctx


class TestSpiderContextLoad:
    """Tests for SpiderContext.load() method."""

    def teardown_method(self, method):
        """Reset global context after each test."""
        set_context(None)

    @patch("spider.utils.files.find_adapter_directory")
    def test_load_returns_none_when_no_adapter(self, mock_find):
        """load returns None when adapter directory not found."""
        mock_find.return_value = None
        result = SpiderContext.load()
        assert result is None

    @patch("spider.utils.context.load_artifacts_meta")
    @patch("spider.utils.files.find_adapter_directory")
    def test_load_returns_none_on_meta_error(self, mock_find, mock_load_meta):
        """load returns None when artifacts.json fails to load."""
        mock_find.return_value = Path("/fake/adapter")
        mock_load_meta.return_value = (None, "Some error")

        result = SpiderContext.load()
        assert result is None
