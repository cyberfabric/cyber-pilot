"""
Cypilot Global CLI Proxy — allows running as: python -m cypilot_proxy

@cpt-dod:cpt-cypilot-dod-core-infra-global-package:p1
"""

from cypilot_proxy.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
