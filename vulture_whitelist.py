# Vulture whitelist — false positives that should be ignored.
# Each entry is a dummy usage of the flagged name.

from cypilot.utils.ui import _UI
from cypilot.ralphex_export import (
    read_handoff_status,
    check_completed_plans,
    run_validation_commands,
    report_handoff,
)
from cypilot.commands.agents import _AgentEntry, _SkillEntry, _MergedComponents, _ProvenanceRecord
from cypilot.commands.resolve_vars import assemble_component
from cypilot.utils.manifest import ManifestLayerState

is_json = _UI.is_json  # staticmethod alias exposed on the ui singleton

# Agent-facing handoff API: called by the cypilot-ralphex agent prompt,
# not by production code paths directly. See skills/cypilot/agents/cypilot-ralphex.md.
read_handoff_status
check_completed_plans
run_validation_commands
report_handoff

_AgentEntry  # used as string type hint in agents.py
_SkillEntry  # used as string type hint in agents.py
_MergedComponents  # used as string type hint in agents.py
_ProvenanceRecord  # used as string type hint in agents.py
assemble_component  # public API for future use
INCLUDE_ERROR = ManifestLayerState.INCLUDE_ERROR  # valid enum value for future use
