"""Shared test helpers for Cypilot tests."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def write_constraints_toml(path: Path, data: Dict[str, Any]) -> None:
    """Write a constraints dict (artifact-kind-keyed) as constraints.toml.

    *path* is the kit root directory (constraints.toml is created inside it).
    *data* maps artifact kinds to their constraint dicts, e.g.
    ``{"PRD": {"identifiers": {"fr": {"required": True}}}}``.
    """
    from cypilot.utils.toml_utils import dumps
    (path / "constraints.toml").write_text(
        dumps({"artifacts": data}), encoding="utf-8",
    )
