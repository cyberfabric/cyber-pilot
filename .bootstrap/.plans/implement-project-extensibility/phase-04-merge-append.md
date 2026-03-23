```toml
[phase]
plan = "implement-project-extensibility"
number = 4
total = 8
type = "implement"
title = "Multi-Layer Merging + Section Appending"
depends_on = [2, 3]
input_files = ["skills/cypilot/scripts/cypilot/utils/manifest.py", "skills/cypilot/scripts/cypilot/utils/layer_discovery.py"]
output_files = ["skills/cypilot/scripts/cypilot/utils/manifest.py", "tests/test_merge_components.py"]
outputs = []
inputs = ["out/phase-01-types.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, input content,
and tool commands are included below. You do not need any prior context or
external files. Follow the instructions exactly, run any EXECUTE commands
as written, and report results against the acceptance criteria at the end.

## What

Add multi-layer component merging and section appending to `manifest.py`. Implement `merge_components()` which takes a list of `ManifestLayer` objects (from Phase 2's `discover_layers()`, with includes resolved by Phase 3's `resolve_includes()`), iterates in resolution order, and applies inner-scope-wins semantics. Also implement `apply_section_appends()` for the section appending template composition model.

## Prior Context

Phase 1: Added `ManifestV2`, `ManifestLayer`, `AgentEntry`, `SkillEntry`, etc.
Phase 2: Added `discover_layers()` in `layer_discovery.py` — returns `List[ManifestLayer]`.
Phase 3: Added `resolve_includes()` in `manifest.py` — augments manifests with included components.
Language: Python 3.11+, stdlib only. Traceability: FULL.

## Rules

### Structure Rules
- Add to existing `manifest.py`
- Use `@dataclass(frozen=True)` for MergedComponents result type
- All function signatures use type hints

### Traceability Rules (FULL mode)
- Scope markers for both algorithms
- Block markers per CDSL instruction step

### Engineering Rules
- TDD, SOLID, DRY, KISS, YAGNI
- Inner-scope-wins: last writer (innermost layer) wins on ID collision across layers
- Record provenance metadata for each component (winning layer, overridden layers)

### Forbidden
- MUST NOT implement agent schema translation (Phase 5)
- MUST NOT implement skills generation (Phase 5)
- MUST NOT add third-party dependencies

## Input

### CDSL: Merge Components Algorithm

```
ID: cpt-cypilot-algo-project-extensibility-merge-components

Input: List[ManifestLayer]
Output: MergedComponents (dict of component_type to dict of id to component)

Steps:
1. Initialize empty merged dict for each component type (agents, skills, workflows, rules)
2. FOR EACH layer in resolution order (Core, Kit, Master Repo, Repo):
   2.1 FOR EACH component in layer's manifest (after includes resolved):
       2.1.1 Overwrite merged[type][id] with this component (last-writer-wins)
       2.1.2 Record provenance: layer scope, manifest path, whether it overwrote
3. RETURN merged components with provenance metadata
```

### CDSL: Section Appending Algorithm

```
ID: cpt-cypilot-algo-project-extensibility-section-appending

Input: base_content (str), append_sections from layers (list of content strings)
Output: composed_content (str)

Steps:
1. Start with base content from the winning component definition
2. FOR EACH layer in resolution order that declares append content for this component ID:
   2.1 Append the layer's content after the base content, separated by a newline
3. RETURN composed content
```

## Task

1. Read `out/phase-01-types.md` for types from Phase 1
2. Read current `manifest.py` to see Phase 1 and Phase 3 additions
3. Add a `MergedComponents` dataclass (or use a typed dict) with:
   - `agents: Dict[str, AgentEntry]`
   - `skills: Dict[str, SkillEntry]`
   - `workflows: Dict[str, WorkflowEntry]`
   - `rules: Dict[str, RuleEntry]`
   - `provenance: Dict[str, ProvenanceRecord]` (component_id → winning layer info)
4. Add `ProvenanceRecord` dataclass: `component_id`, `component_type`, `winning_scope`, `winning_path`, `overridden: List[Tuple[str, Path]]`
5. Add `merge_components(layers: List[ManifestLayer]) -> MergedComponents`:
   - Iterate layers in order (they should already be in resolution order from discover_layers)
   - For each layer with state LOADED, iterate its components
   - Inner-scope-wins: later layers overwrite earlier ones on same ID
   - Record provenance for each overwrite
6. Add `apply_section_appends(base_content: str, layers: List[ManifestLayer], component_id: str) -> str`:
   - Collect `append` content for the given component_id from all layers
   - Stack appends in resolution order (outermost first)
7. Add `@cpt-*` traceability markers
8. Write tests in `tests/test_merge_components.py`:
   - Test single layer (no merging needed)
   - Test two layers with non-overlapping components
   - Test two layers with same component ID (inner scope wins)
   - Test provenance records correctly which layer won
   - Test section appending with content from multiple layers
   - Test section appending with no appends (base content unchanged)
9. Run tests: `python3 -m pytest tests/test_merge_components.py -v`
10. Self-verify against acceptance criteria

## Acceptance Criteria

- [ ] `MergedComponents` dataclass exists with agents, skills, workflows, rules dicts
- [ ] `ProvenanceRecord` dataclass exists with winning_scope, winning_path, overridden fields
- [ ] `merge_components()` returns inner-scope-wins merged result
- [ ] Provenance is recorded for each component (winning layer + overridden layers)
- [ ] `apply_section_appends()` stacks appends in resolution order
- [ ] `@cpt-algo:cpt-cypilot-algo-project-extensibility-merge-components:p1` marker present
- [ ] `@cpt-algo:cpt-cypilot-algo-project-extensibility-section-appending:p1` marker present
- [ ] File `tests/test_merge_components.py` exists with ≥5 test functions
- [ ] All tests pass: `python3.13 -m pytest tests/test_merge_components.py -v` exits 0
- [ ] No unresolved `{...}` template variables outside code fences

## Output Format

When complete, report results in this exact format:

```
PHASE 4/8 COMPLETE
Status: PASS | FAIL
Files created: tests/test_merge_components.py
Files modified: skills/cypilot/scripts/cypilot/utils/manifest.py
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

Phase 4 is complete (PASS).
Please read the plan manifest, then execute Phase 5: "Extended Agent Schema + Skills Generation".
The phase file is: .bootstrap/.plans/implement-project-extensibility/phase-05-schema-skills.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.

NOTE: Phases 5, 6, and 7 can run in parallel (all depend only on Phase 4).
```
