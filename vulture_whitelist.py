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

# trace_graph.py — public API / dataclass fields used by external callers
from cypilot.utils.trace_graph import (
    StructuralAnchor,
    AnchoredHit,
    IndexCache,
    NodeType,
    EdgeType,
    TraceGraph,
    SessionIndex,
    compute_py_containers,
    compute_code_containers_regex,
    build_doc_anchored_hits,
    compute_code_fingerprints,
    git_changed_files,
)
_ = StructuralAnchor
_.container  # StructuralAnchor.container
_ = AnchoredHit
_.to_legacy_row  # AnchoredHit.to_legacy_row
compute_py_containers  # public API
compute_code_containers_regex  # public API
build_doc_anchored_hits  # public API
compute_code_fingerprints  # public API
_ = IndexCache
_.changed_files  # IndexCache.changed_files
git_changed_files  # public API
_ = NodeType
_.SECTION  # NodeType.SECTION
_.CODE_FILE  # NodeType.CODE_FILE
_ = EdgeType
_.CONTAINS  # EdgeType.CONTAINS
_ = TraceGraph
_.references_for_id  # TraceGraph.references_for_id
_.implementations_for_id  # TraceGraph.implementations_for_id
_ = SessionIndex
_.refresh_file  # SessionIndex.refresh_file
