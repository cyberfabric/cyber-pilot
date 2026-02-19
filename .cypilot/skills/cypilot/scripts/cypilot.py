#!/usr/bin/env python3
"""
Cypilot Validator - Main Entry Point

This is a thin wrapper that imports from the modular cypilot package.
For backward compatibility, all functions are re-exported at module level.

Legacy monolithic implementation preserved in legacy.py.
"""

# Re-export everything from the cypilot package for backward compatibility
from cypilot import *
from cypilot import __all__

# CLI entry point
if __name__ == "__main__":
    from cypilot import main
    raise SystemExit(main())
