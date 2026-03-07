# Vulture whitelist — false positives that should be ignored.
# Each entry is a dummy usage of the flagged name.

from cypilot.utils.ui import _UI
from cypilot.commands.kit import KIT_COPY_SUBDIRS, _compute_kit_hashes, _write_blueprint_hashes
from cypilot.commands.migrate import _copy_tree_contents

is_json = _UI.is_json  # staticmethod alias exposed on the ui singleton
KIT_COPY_SUBDIRS  # used by tests
_compute_kit_hashes  # used by tests
_write_blueprint_hashes  # used by tests
_copy_tree_contents  # used by tests
