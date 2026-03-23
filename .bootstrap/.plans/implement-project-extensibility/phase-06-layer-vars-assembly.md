```toml
[phase]
plan = "implement-project-extensibility"
number = 6
total = 8
type = "implement"
title = "Layer Variables + Deterministic Assembly"
depends_on = [4]
input_files = ["skills/cypilot/scripts/cypilot/commands/resolve_vars.py", "skills/cypilot/scripts/cypilot/utils/manifest.py"]
output_files = ["skills/cypilot/scripts/cypilot/commands/resolve_vars.py", "tests/test_layer_vars.py"]
outputs = []
inputs = ["out/phase-01-types.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, input content,
and tool commands are included below. You do not need any prior context or
external files. Follow the instructions exactly, run any EXECUTE commands
as written, and report results against the acceptance criteria at the end.

## What

Extend `resolve_vars.py` with layer path variables (`{base_dir}`, `{master_repo}`, `{repo}`) derived from walk-up discovery. Add `assemble_component()` which deterministically assembles a component from merged data — loading source, applying section appends, substituting variables, and writing output. The entire pipeline must be a pure function of filesystem inputs (no LLM calls, no randomness, no timestamps).

## Prior Context

Phase 1: Added `ManifestV2`, `ManifestLayer`, component types.
Phase 2: Added `discover_layers()` which returns `List[ManifestLayer]` with scope info.
Phase 3: Added `resolve_includes()`.
Phase 4: Added `merge_components()`, `apply_section_appends()`, `MergedComponents`, `ProvenanceRecord`.
Language: Python 3.11+, stdlib only. Traceability: FULL.

### Current resolve_vars.py structure

```python
def _merge_with_collision_tracking(system_vars, kit_vars) -> Tuple[Dict, List]:
    """First-writer-wins collision tracking."""

def _resolve_kit_variables(adapter_dir, core_kit) -> Dict[str, str]:
    """Resolve resource bindings for a single kit."""

def _collect_all_variables(project_root, adapter_dir, core_data) -> Dict[str, Any]:
    """Collect all template variables: system + kit resources."""
    # Returns {system: {...}, kits: {...}, variables: {...flat...}}
```

## Rules

### Structure Rules
- Add to existing `resolve_vars.py`
- All function signatures use type hints
- Deterministic assembly function can go in `resolve_vars.py` or a new `assembly.py` — prefer `resolve_vars.py` to minimize new files

### Traceability Rules (FULL mode)
- Scope markers for both algorithms
- Block markers per CDSL instruction step

### Engineering Rules
- TDD, SOLID, DRY, KISS, YAGNI
- Pure function: same inputs → identical outputs. No timestamps, no randomness.
- Reuse existing `_merge_with_collision_tracking()` for variable merging

### Forbidden
- MUST NOT wire into `cmd_generate_agents` or `cmd_resolve_vars` CLI entry points (Phase 8)
- MUST NOT add third-party dependencies
- MUST NOT introduce non-determinism (no datetime, no random, no uuid)

## Input

### CDSL: Resolve Layer Variables Algorithm

```
ID: cpt-cypilot-algo-project-extensibility-resolve-layer-variables

Input: layers (List[ManifestLayer]), existing variables from resolve-vars
Output: flat dict of variable to absolute path

Steps:
1. Start with existing variables from _collect_all_variables() (cypilot_path, project_root, kit resource bindings)
2. Add layer path variables from discovered layers: {base_dir}, {master_repo}, {repo}
3. FOR EACH layer, resolve source paths relative to that layer's manifest directory
4. RETURN merged variable dict
```

### CDSL: Deterministic Component Assembly Algorithm

```
ID: cpt-cypilot-algo-project-extensibility-deterministic-assembly

Input: merged components, resolved variables, append sections
Output: agent-native files (deterministic)

Steps:
1. FOR EACH component in merged results where target agent matches
   1.1 Load source content for this component
   1.2 Apply section appends from all layers in order
   1.3 Translate agent schema fields to agent-native format
   1.4 Substitute all {variable} references using resolved variable dict
   1.5 Determine output path using agent-native path conventions
   1.6 Write file content (sorted, deterministic — no timestamps, no randomness)
2. RETURN list of written files with provenance
```

### Layer Variable Mapping

| Variable | Source | Description |
|----------|--------|-------------|
| `{base_dir}` | `discover_layers()` | Outermost discovered layer root (master repo if found, else repo root) |
| `{master_repo}` | `discover_layers()` | Master repo root path (empty string if no master repo) |
| `{repo}` | `discover_layers()` | Current repo root path |

## Task

1. Read `out/phase-01-types.md` for types from Phase 1
2. Read current `resolve_vars.py` to understand `_collect_all_variables()` and merging pattern
3. Add `add_layer_variables(variables: Dict[str, str], layers: List[ManifestLayer], repo_root: Path) -> Dict[str, str]`:
   - Extract layer paths from ManifestLayer objects
   - Set `{base_dir}` to outermost layer root
   - Set `{master_repo}` to master repo path (empty string if none)
   - Set `{repo}` to repo_root
   - Merge into existing variables (layer vars should not override system/kit vars)
4. Add `assemble_component(component_id: str, source_content: str, layers: List[ManifestLayer], variables: Dict[str, str], target: str) -> str`:
   - Apply section appends via `apply_section_appends()` (from Phase 4)
   - Substitute `{variable}` references using `str.format_map()`
   - Return assembled content (no file I/O — caller handles writing)
5. Add `@cpt-*` traceability markers
6. Write tests in `tests/test_layer_vars.py`:
   - Test layer variables with master repo present
   - Test layer variables without master repo (standalone)
   - Test layer variables don't override system variables
   - Test deterministic assembly (same inputs → same output)
   - Test variable substitution in assembled content
   - Test assembly with section appends
7. Run tests: `python3 -m pytest tests/test_layer_vars.py -v`
8. Self-verify against acceptance criteria

## Acceptance Criteria

- [ ] `add_layer_variables()` function exists in `resolve_vars.py`
- [ ] `{base_dir}` variable is set to outermost layer root
- [ ] `{master_repo}` variable is set correctly (path or empty string)
- [ ] `{repo}` variable is set to repo root
- [ ] Layer variables don't override existing system/kit variables
- [ ] `assemble_component()` function exists
- [ ] Assembly is deterministic (pure function of inputs)
- [ ] Variable substitution works in assembled content
- [ ] `@cpt-algo:cpt-cypilot-algo-project-extensibility-resolve-layer-variables:p1` marker present
- [ ] `@cpt-algo:cpt-cypilot-algo-project-extensibility-deterministic-assembly:p1` marker present
- [ ] File `tests/test_layer_vars.py` exists with ≥6 test functions
- [ ] All tests pass: `python3.13 -m pytest tests/test_layer_vars.py -v` exits 0
- [ ] No unresolved `{...}` template variables outside code fences

## Output Format

When complete, report results in this exact format:

```
PHASE 6/8 COMPLETE
Status: PASS | FAIL
Files created: tests/test_layer_vars.py
Files modified: skills/cypilot/scripts/cypilot/commands/resolve_vars.py
Acceptance criteria:
  [x] Criterion 1 — PASS
  ...
Line count: {actual}/{budget}
Notes: {any issues or decisions made}
```

Then generate a **copy-pasteable prompt** for the next phase inside a single code fence:

```
I have a Cypilot execution plan at:
  .bootstrap/.plans/implement-project-extensibility/plan.toml

Phase 6 is complete (PASS).
Please read the plan manifest, then execute Phase 8: "Integration + Backward Compatibility".
The phase file is: .bootstrap/.plans/implement-project-extensibility/phase-08-integration-compat.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.

NOTE: Phases 5, 6, and 7 can run in parallel (all depend only on Phase 4).
Verify Phases 5 and 7 are also complete before executing Phase 8.
```
