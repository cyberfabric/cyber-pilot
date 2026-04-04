import importlib
import sys
import types

import pytest


MODULE_PATH = "cypilot.utils._tomllib_compat"


def _reload_module():
    # Ensure fresh import
    sys.modules.pop(MODULE_PATH, None)
    return importlib.import_module(MODULE_PATH)


def test_stdlib_tomllib(monkeypatch):
    dummy = types.ModuleType("tomllib")
    dummy.DUMMY_FLAG = "stdlib"

    # Simulate Python >= 3.11 and a stdlib tomllib present
    monkeypatch.setitem(sys.modules, "tomllib", dummy)
    monkeypatch.setattr(sys, "version_info", (3, 11))

    mod = _reload_module()
    assert hasattr(mod, "tomllib")
    assert mod.tomllib is dummy
    assert mod.__all__ == ["tomllib"]


def test_tomli_fallback(monkeypatch):
    dummy = types.ModuleType("tomli")
    dummy.DUMMY_FLAG = "tomli"

    # Simulate Python < 3.11 and tomli installed
    monkeypatch.setattr(sys, "version_info", (3, 10))
    monkeypatch.setitem(sys.modules, "tomli", dummy)

    mod = _reload_module()
    assert hasattr(mod, "tomllib")
    # When tomli is used, the compat module aliases it as tomllib
    assert mod.tomllib is dummy
    assert mod.__all__ == ["tomllib"]


def test_no_tomli_exits_with_error(monkeypatch, capsys):
    # Simulate Python < 3.11 and tomli NOT installed
    monkeypatch.setattr(sys, "version_info", (3, 10))
    # Ensure tomli and tomllib are not present
    monkeypatch.delitem(sys.modules, "tomli", raising=False)
    monkeypatch.delitem(sys.modules, "tomllib", raising=False)
    # Also ensure our target module is not cached
    sys.modules.pop(MODULE_PATH, None)
    # Force ImportError for tomli/tomllib even if installed in this environment
    import builtins

    real_import = builtins.__import__

    def _fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in ("tomli", "tomllib"):
            raise ImportError
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _fake_import)

    with pytest.raises(SystemExit) as ei:
        importlib.import_module(MODULE_PATH)

    # The compat module calls sys.exit(1) on missing dependency
    assert ei.value.code == 1
    captured = capsys.readouterr()
    assert "ERROR: tomllib/tomli not available" in captured.err

