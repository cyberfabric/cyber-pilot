```toml
[phase]
plan = "implement-project-extensibility"
number = 3
total = 8
type = "implement"
title = "Includes Resolution"
depends_on = [1]
input_files = ["skills/cypilot/scripts/cypilot/utils/manifest.py"]
output_files = ["skills/cypilot/scripts/cypilot/utils/manifest.py", "tests/test_manifest_includes.py"]
outputs = []
inputs = ["out/phase-01-types.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, input content,
and tool commands are included below. You do not need any prior context or
external files. Follow the instructions exactly, run any EXECUTE commands
as written, and report results against the acceptance criteria at the end.

## What

Add includes resolution logic to `skills/cypilot/scripts/cypilot/utils/manifest.py`. Implement `resolve_includes()` which processes the `includes` array in v2.0 manifests, loading subdirectory manifests at the same layer as the includer. Handles circular detection, max depth (3), ID collision checks, and path rewriting. This phase does NOT implement layer discovery (Phase 2) or merging (Phase 4).

## Prior Context

Phase 1 added `ManifestV2` with an `includes: List[str]` field, plus `parse_manifest_v2()`.
Read `out/phase-01-types.md` for the full list of types.
Language: Python 3.11+, stdlib only. System slug: `cypilot`. Traceability: FULL.

## Rules

### Structure Rules
- Extend existing `manifest.py` — do not create a new module for this
- Use `@dataclass(frozen=True)` for any new value objects
- All function signatures use type hints with `Optional[X]`

### Traceability Rules (FULL mode)
- Scope marker: `@cpt-algo:cpt-cypilot-algo-project-extensibility-resolve-includes:p1`
- Block markers per CDSL instruction step

### Engineering Rules
- TDD, SOLID, DRY, KISS, YAGNI
- Error handling: Raise clear errors for circular includes, depth exceeded, ID collision

### Forbidden
- MUST NOT implement layer discovery (Phase 2)
- MUST NOT implement merging (Phase 4)
- MUST NOT add third-party dependencies
- MUST NOT break existing v1.0 manifest functions

## Input

### CDSL: Resolve Manifest Includes Algorithm (from FEATURE spec)

```
ID: cpt-cypilot-algo-project-extensibility-resolve-includes

Input: manifest (parsed TOML dict), manifest_dir (Path), include_chain (set of absolute paths)
Output: augmented manifest with included components merged in

Steps:
1. Read includes array from manifest (default empty)
2. FOR EACH include path in includes:
   2.1 Resolve path relative to manifest_dir
   2.2 IF resolved path is in include_chain, RAISE circular include error with chain
   2.3 IF include chain depth > 3, RAISE max depth exceeded error
   2.4 Parse included manifest.toml
   2.5 Recursively resolve includes in the included manifest (add current path to chain)
   2.6 Rewrite prompt_file and source paths in included components to be relative to the
       *included* manifest's directory (not the includer's)
   2.7 FOR EACH component in included manifest: IF component ID already exists in includer,
       RAISE collision error
   2.8 Merge included components into the includer's component lists
3. RETURN augmented manifest
```

### CDSL: DoD — Manifest Includes (from FEATURE spec)

```
ID: cpt-cypilot-dod-project-extensibility-includes

The system MUST support an includes array in manifest.toml v2.0 that loads
subdirectory manifests at the same layer as the includer. Include paths are
relative to the including manifest's directory. prompt_file and source paths
in included manifests resolve relative to the *included* manifest's directory.
The system MUST detect and reject circular includes, enforce a max depth of 3,
and error on component ID collisions between includer and includee.
Included manifests' own includes arrays are processed recursively within the
depth limit.

Touches: manifest.py, agents.py
```

## Task

1. Read `out/phase-01-types.md` for types from Phase 1
2. Read current `skills/cypilot/scripts/cypilot/utils/manifest.py`
3. Add `resolve_includes(manifest: ManifestV2, manifest_dir: Path, include_chain: Optional[Set[Path]] = None) -> ManifestV2` function:
   - If `manifest.includes` is empty, return manifest unchanged
   - For each include path: resolve relative to `manifest_dir`
   - Detect circular includes (path already in chain) → raise ValueError with chain
   - Enforce max depth of 3 → raise ValueError
   - Parse included manifest via `parse_manifest_v2()`
   - Recursively resolve includes in the included manifest
   - Rewrite `prompt_file` and `source` paths to be absolute or relative to the included manifest's dir
   - Check for ID collisions between includer and includee → raise ValueError
   - Merge included components into includer's lists
4. Add `@cpt-*` traceability markers per CDSL steps
5. Write tests in `tests/test_manifest_includes.py`:
   - Test basic includes (one level)
   - Test recursive includes (two levels)
   - Test circular include detection (A includes B, B includes A)
   - Test max depth exceeded (depth > 3)
   - Test ID collision between includer and includee
   - Test prompt_file/source path rewriting
   - Test empty includes array (no-op)
6. Run tests: `python3 -m pytest tests/test_manifest_includes.py -v`
7. Self-verify against acceptance criteria below

## Acceptance Criteria

- [ ] Function `resolve_includes()` exists in `manifest.py`
- [ ] Empty includes array returns manifest unchanged
- [ ] Single-level include loads and merges components correctly
- [ ] Recursive includes (depth 2) work correctly
- [ ] Circular includes raise ValueError with include chain in message
- [ ] Depth > 3 raises ValueError
- [ ] ID collision between includer and includee raises ValueError
- [ ] `prompt_file` and `source` paths are rewritten relative to included manifest's directory
- [ ] `@cpt-algo:cpt-cypilot-algo-project-extensibility-resolve-includes:p1` marker present
- [ ] `@cpt-dod:cpt-cypilot-dod-project-extensibility-includes:p1` marker present
- [ ] File `tests/test_manifest_includes.py` exists with ≥6 test functions
- [ ] All tests pass: `python3.13 -m pytest tests/test_manifest_includes.py -v` exits 0
- [ ] No unresolved `{...}` template variables outside code fences

## Output Format

When complete, report results in this exact format:

```
PHASE 3/8 COMPLETE
Status: PASS | FAIL
Files created: tests/test_manifest_includes.py
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

Phase 3 is complete (PASS).
Please read the plan manifest, then execute Phase 4: "Multi-Layer Merging + Section Appending".
The phase file is: .bootstrap/.plans/implement-project-extensibility/phase-04-merge-append.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.

NOTE: Phase 4 depends on both Phase 2 and Phase 3.
Verify both are complete before executing Phase 4.
```
