"""
Cypilot Validator - CLI Entry Point

Allows running the package as: python -m cypilot
"""

import sys

# Import main from parent cypilot.py during migration
# This will be updated to import from cli.py after full migration
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from cypilot import main

if __name__ == "__main__":
    raise SystemExit(main())
