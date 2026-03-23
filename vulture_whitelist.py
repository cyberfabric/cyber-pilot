# Vulture whitelist — false positives that should be ignored.
# Each entry is a dummy usage of the flagged name.

from cypilot.utils.ui import _UI
from cypilot.commands.kit import KIT_COPY_SUBDIRS, _compute_kit_hashes, _write_blueprint_hashes
from cypilot.commands.migrate import _copy_tree_contents
from cypilot.commands.agents import _AgentEntry, _SkillEntry, _MergedComponents, _ProvenanceRecord
from cypilot.commands.resolve_vars import assemble_component
from cypilot.utils.manifest import ManifestLayerState

is_json = _UI.is_json  # staticmethod alias exposed on the ui singleton
KIT_COPY_SUBDIRS  # used by tests
_compute_kit_hashes  # used by tests
_write_blueprint_hashes  # used by tests
_copy_tree_contents  # used by tests
_AgentEntry  # used as string type hint in agents.py
_SkillEntry  # used as string type hint in agents.py
_MergedComponents  # used as string type hint in agents.py
_ProvenanceRecord  # used as string type hint in agents.py
assemble_component  # public API for future use
INCLUDE_ERROR = ManifestLayerState.INCLUDE_ERROR  # valid enum value for future use
