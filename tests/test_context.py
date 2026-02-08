"""
Tests for CypilotContext and related functions.

Tests cover:
- CypilotContext methods: get_template, get_template_for_kind, get_known_id_kinds
- Global context functions: get_context, set_context, ensure_context
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.utils.context import (
    CypilotContext,
    LoadedKit,
    get_context,
    set_context,
    ensure_context,
    _global_context,
)
from cypilot.utils.artifacts_meta import ArtifactsMeta, Kit


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


class TestCypilotContextMethods:
    """Tests for CypilotContext instance methods."""

    def _make_context(self) -> CypilotContext:
        """Create a mock CypilotContext with templates."""
        # Create mock templates
        prd_tmpl = _make_mock_template("PRD", [
            _make_mock_block("id", "fr"),
            _make_mock_block("id", "actor"),
        ])
        design_tmpl = _make_mock_template("DESIGN", [
            _make_mock_block("id", "component"),
            _make_mock_block("id", "seq"),
        ])
        spec_tmpl = _make_mock_template("SPEC", [
            _make_mock_block("id", "flow"),
            _make_mock_block("id", "algo"),
        ])

        # Create kits
        kit1 = Kit(kit_id="cypilot-sdlc", format="Cypilot", path="kits/sdlc")
        kit2 = Kit(kit_id="custom", format="Cypilot", path="kits/custom")

        loaded_kit1 = LoadedKit(
            kit=kit1,
            templates={"PRD": prd_tmpl, "DESIGN": design_tmpl},
        )
        loaded_kit2 = LoadedKit(
            kit=kit2,
            templates={"SPEC": spec_tmpl},
        )

        # Create mock meta
        meta = MagicMock(spec=ArtifactsMeta)
        meta.project_root = ".."

        return CypilotContext(
            adapter_dir=Path("/fake/adapter"),
            project_root=Path("/fake/project"),
            meta=meta,
            kits={"cypilot-sdlc": loaded_kit1, "custom": loaded_kit2},
            registered_systems={"myapp", "test-system"},
            _errors=[{"type": "context", "message": "error1"}, {"type": "context", "message": "error2"}],
        )

    def test_get_template_found(self):
        """get_template returns template when kit and kind exist."""
        ctx = self._make_context()
        tmpl = ctx.get_template("cypilot-sdlc", "PRD")
        assert tmpl is not None
        assert tmpl.kind == "PRD"

    def test_get_template_kit_not_found(self):
        """get_template returns None when kit doesn't exist."""
        ctx = self._make_context()
        result = ctx.get_template("nonexistent-kit", "PRD")
        assert result is None

    def test_get_template_kind_not_found(self):
        """get_template returns None when kind doesn't exist in kit."""
        ctx = self._make_context()
        result = ctx.get_template("cypilot-sdlc", "NONEXISTENT")
        assert result is None

    def test_get_template_for_kind_found(self):
        """get_template_for_kind finds template from any kit."""
        ctx = self._make_context()
        # SPEC is in 'custom' kit
        tmpl = ctx.get_template_for_kind("SPEC")
        assert tmpl is not None
        assert tmpl.kind == "SPEC"

    def test_get_template_for_kind_not_found(self):
        """get_template_for_kind returns None when kind not in any kit."""
        ctx = self._make_context()
        result = ctx.get_template_for_kind("NONEXISTENT")
        assert result is None

    def test_get_known_id_kinds(self):
        """get_known_id_kinds extracts id kinds from template markers."""
        ctx = self._make_context()
        id_kinds = ctx.get_known_id_kinds()
        # PRD has fr, actor; DESIGN has component, seq; SPEC has flow, algo
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
        mock_ctx = MagicMock(spec=CypilotContext)
        set_context(mock_ctx)
        assert get_context() is mock_ctx

    def test_set_context_to_none(self):
        """set_context(None) clears the context."""
        mock_ctx = MagicMock(spec=CypilotContext)
        set_context(mock_ctx)
        set_context(None)
        assert get_context() is None

    @patch("cypilot.utils.context.CypilotContext.load")
    def test_ensure_context_loads_when_none(self, mock_load):
        """ensure_context loads context when global is None."""
        set_context(None)
        mock_ctx = MagicMock(spec=CypilotContext)
        mock_load.return_value = mock_ctx

        result = ensure_context()

        mock_load.assert_called_once_with(None)
        assert result is mock_ctx
        assert get_context() is mock_ctx

    @patch("cypilot.utils.context.CypilotContext.load")
    def test_ensure_context_passes_start_path(self, mock_load):
        """ensure_context passes start_path to CypilotContext.load."""
        set_context(None)
        mock_ctx = MagicMock(spec=CypilotContext)
        mock_load.return_value = mock_ctx
        start = Path("/some/path")

        result = ensure_context(start)

        mock_load.assert_called_once_with(start)

    def test_ensure_context_returns_existing(self):
        """ensure_context returns existing context without reloading."""
        existing_ctx = MagicMock(spec=CypilotContext)
        set_context(existing_ctx)

        with patch("cypilot.utils.context.CypilotContext.load") as mock_load:
            result = ensure_context()
            mock_load.assert_not_called()
            assert result is existing_ctx


class TestCypilotContextLoad:
    """Tests for CypilotContext.load() method."""

    def teardown_method(self, method):
        """Reset global context after each test."""
        set_context(None)

    @patch("cypilot.utils.files.find_adapter_directory")
    def test_load_returns_none_when_no_adapter(self, mock_find):
        """load returns None when adapter directory not found."""
        mock_find.return_value = None
        result = CypilotContext.load()
        assert result is None

    @patch("cypilot.utils.context.load_artifacts_meta")
    @patch("cypilot.utils.files.find_adapter_directory")
    def test_load_returns_none_on_meta_error(self, mock_find, mock_load_meta):
        """load returns None when artifacts.json fails to load."""
        mock_find.return_value = Path("/fake/adapter")
        mock_load_meta.return_value = (None, "Some error")

        result = CypilotContext.load()
        assert result is None
