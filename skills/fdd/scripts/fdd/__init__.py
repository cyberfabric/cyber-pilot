"""
FDD Validator - Python Package

Entry point for the FDD validation CLI tool.
"""

# Import from modular components
from .constants import *
from .utils import *

# Import CLI entry point
from .cli import main

__version__ = "1.0.0-modular"

__all__ = [
    # Main entry point
    "main",
    # Utils
    "detect_requirements",
]
