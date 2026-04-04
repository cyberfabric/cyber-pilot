"""
Compatibility shim for tomllib (Python 3.11+) / tomli (Python < 3.11).

Import this module instead of importing tomllib directly:

    from cypilot.utils._tomllib_compat import tomllib

@cpt-algo:cpt-cypilot-algo-core-infra-config-management:p1
"""

import sys

# Python 3.11+ has tomllib in stdlib, earlier versions need tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        print(
            "ERROR: tomllib/tomli not available.\n"
            "Please either:\n"
            "  1. Use Python 3.11+ (tomllib is included in stdlib), or\n"
            "  2. Install tomli: pip install tomli\n",
            file=sys.stderr,
        )
        sys.exit(1)

__all__ = ["tomllib"]
