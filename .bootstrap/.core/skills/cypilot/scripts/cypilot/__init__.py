"""
Cypilot Validator - Python Package

Entry point for the Cypilot validation CLI tool.
"""

from typing import List, Optional

# Import from modular components
from .constants import *
from .utils import *

# Import CLI entry point
def main(argv: Optional[List[str]] = None) -> int:
    from .cli import main as _main
    return _main(argv)

__version__ = "v3.0.2-beta"

__all__ = [
    # Main entry point
    "main",
]
