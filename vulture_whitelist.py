# Vulture whitelist — false positives that should be ignored.
# Each entry is a dummy usage of the flagged name.

from cypilot.utils.ui import _UI

is_json = _UI.is_json  # staticmethod alias exposed on the ui singleton
