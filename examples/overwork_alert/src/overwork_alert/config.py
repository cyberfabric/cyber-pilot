"""Configuration loading for Overwork Alert.

Config is optional; missing/invalid values fall back to safe defaults.
"""

from __future__ import annotations

import json
import logging
from dataclasses import replace
from pathlib import Path
from typing import Any

from .models import Config

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "overwork-alert" / "config.json"


def _parse_positive_int(value: Any) -> int | None:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    if n <= 0:
        return None
    return n


# @cpt-dod:cpt-ex-ovwa-dod-tracker-core-config-defaults:p1
def load_config(config_path: Path | None = None) -> Config:
    """Load effective config (defaults + validation) from a JSON file."""
    path = config_path or DEFAULT_CONFIG_PATH

    cfg = Config()
    if not path.exists():
        return cfg

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.warning("Config unreadable; using defaults", exc_info=True)
        return cfg

    if not isinstance(raw, dict):
        return cfg

    limit_seconds = _parse_positive_int(raw.get("limit_seconds"))
    idle_threshold_seconds = _parse_positive_int(raw.get("idle_threshold_seconds"))
    repeat_interval_seconds = _parse_positive_int(raw.get("repeat_interval_seconds"))
    tick_interval_seconds = _parse_positive_int(raw.get("tick_interval_seconds"))
    max_tick_delta_seconds = _parse_positive_int(raw.get("max_tick_delta_seconds"))
    control_socket_path = raw.get("control_socket_path")

    if limit_seconds is not None:
        cfg = replace(cfg, limit_seconds=limit_seconds)
    if idle_threshold_seconds is not None:
        cfg = replace(cfg, idle_threshold_seconds=idle_threshold_seconds)
    if repeat_interval_seconds is not None:
        cfg = replace(cfg, repeat_interval_seconds=repeat_interval_seconds)
    if tick_interval_seconds is not None:
        cfg = replace(cfg, tick_interval_seconds=tick_interval_seconds)

    if max_tick_delta_seconds is not None:
        cfg = replace(cfg, max_tick_delta_seconds=max_tick_delta_seconds)
    else:
        cfg = replace(cfg, max_tick_delta_seconds=cfg.tick_interval_seconds * 2)

    if isinstance(control_socket_path, str) and control_socket_path:
        cfg = replace(cfg, control_socket_path=control_socket_path)

    return cfg
