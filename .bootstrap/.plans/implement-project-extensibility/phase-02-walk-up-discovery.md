```toml
[phase]
plan = "implement-project-extensibility"
number = 2
total = 8
type = "implement"
title = "Walk-Up Layer Discovery"
depends_on = [1]
input_files = ["skills/cypilot/scripts/cypilot/utils/manifest.py", "skills/cypilot/scripts/cypilot/commands/agents.py"]
output_files = ["skills/cypilot/scripts/cypilot/utils/layer_discovery.py", "tests/test_layer_discovery.py"]
outputs = []
inputs = ["out/phase-01-types.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, input content,
and tool commands are included below. You do not need any prior context or
external files. Follow the instructions exactly, run any EXECUTE commands
as written, and report results against the acceptance criteria at the end.

## What

Create a new module `skills/cypilot/scripts/cypilot/utils/layer_discovery.py` that implements the walk-up layer discovery algorithm. This module discovers `manifest.toml` files at each layer boundary (kit, repo, master repo) by walking up the filesystem from the repo root. It detects master repo boundaries and returns a list of `ManifestLayer` objects in resolution order. This phase does NOT implement includes resolution (Phase 3) or merging (Phase 4).

## Prior Context

Phase 1 added these types to `manifest.py`:
- `ManifestV2` — parsed v2.0 manifest with component sections
- `ManifestLayer` — envelope with scope, path, manifest, state
- `ManifestLayerState` — enum (UNDISCOVERED, LOADED, PARSE_ERROR, INCLUDE_ERROR)
- `parse_manifest_v2()` — parses both v1.0 and v2.0 manifests
- `AgentEntry`, `SkillEntry`, `WorkflowEntry`, `RuleEntry`, `ComponentEntry` — component types

Read `out/phase-01-types.md` for the full list of types and fields from Phase 1.

Language: Python 3.11+, stdlib only. System slug: `cypilot`. Traceability: FULL.

## Rules

### Structure Rules
- New utility modules go in `skills/cypilot/scripts/cypilot/utils/`
- Use `@dataclass(frozen=True)` for value objects
- All function signatures use type hints with `Optional[X]`
- Export new public functions from `utils/__init__.py`

### Traceability Rules (FULL mode)
- Scope markers: `@cpt-algo:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1`
- Block markers: `@cpt-begin`/`@cpt-end` wrapping each CDSL instruction's implementation

### Engineering Rules
- TDD: Write failing test first, implement minimal code to pass, then refactor
- KISS: Prefer simplest correct solution
- Error handling: Fail explicitly with clear errors

### Testing Rules
- Test file: `tests/test_layer_discovery.py`
- Use `TemporaryDirectory` for file system tests — create mock directory trees
- Coverage: 90% per file minimum

### Forbidden
- MUST NOT implement includes resolution (Phase 3)
- MUST NOT implement component merging (Phase 4)
- MUST NOT modify `agents.py` (Phase 8 wires everything)
- MUST NOT add third-party dependencies

## Input

### CDSL: Walk-Up Layer Discovery Algorithm (from FEATURE spec)

```
ID: cpt-cypilot-algo-project-extensibility-walk-up-discovery

Input: repo_root (Path), cypilot_root (Path)
Output: List[ManifestLayer] in resolution order

Steps:
1. Load kit manifests from core.toml kit registrations (kit layer)
2. Load repo manifest from {cypilot_root}/config/manifest.toml (repo layer)
3. Walk up from repo_root parent directory
4. At each directory, check for manifest.toml
5. Detect master repo boundary: presence of CLAUDE.md + skills/ at same level,
   or presence of .git/ subdirectory
6. IF master repo detected, load its manifest.toml and stop walk-up
7. IF no master repo found, RETURN only kit + repo layers (backward compatible)
8. RETURN layers in resolution order: [kit, master, repo] (missing layers omitted)
```

### CDSL: DoD — Walk-Up Layer Discovery (from FEATURE spec)

```
ID: cpt-cypilot-dod-project-extensibility-walk-up-discovery

The system MUST walk up the filesystem from repo root, detecting the master
repo boundary and loading manifest.toml at each discovered layer. Master repo
detection uses: CLAUDE.md + skills/ at same level, or presence of .git/
subdirectory. Walk-up stops at master repo root. Missing layers are silently
omitted. For MVP, only Core, Kit, Master Repo, and Repo layers are supported.

Touches: layer_discovery.py (new), agents.py
```

### Resolution Order

Layers are returned in this order (outermost to innermost):
1. Kit layer — from `core.toml` kit registrations
2. Master Repo layer — discovered via walk-up (if found)
3. Repo layer — from `{cypilot_root}/config/manifest.toml`

Core layer is implicit (built from `_default_agents_config()` in agents.py) and is NOT part of this module's output.

## Task

1. Read `out/phase-01-types.md` for the new types added in Phase 1
2. Read `skills/cypilot/scripts/cypilot/utils/manifest.py` to understand `ManifestLayer`, `ManifestLayerState`, `parse_manifest_v2()`
3. Create `skills/cypilot/scripts/cypilot/utils/layer_discovery.py` with:
   - `discover_layers(repo_root: Path, cypilot_root: Path) -> List[ManifestLayer]`
   - `_load_kit_layers(cypilot_root: Path) -> List[ManifestLayer]` — reads core.toml kit registrations, loads kit manifests
   - `_load_repo_layer(cypilot_root: Path) -> Optional[ManifestLayer]` — loads config/manifest.toml
   - `_detect_master_repo(start_dir: Path) -> Optional[Path]` — walks up, checks boundary markers
   - `_is_master_repo_boundary(dir_path: Path) -> bool` — checks CLAUDE.md + skills/ or .git/
4. Add `@cpt-*` traceability markers (scope and block markers per CDSL steps)
5. Export `discover_layers` from `utils/__init__.py`
6. Write tests in `tests/test_layer_discovery.py`:
   - Test standalone repo (no master repo) returns kit + repo layers only
   - Test repo under master repo returns kit + master + repo layers
   - Test missing manifest at a layer results in layer omission (no error)
   - Test manifest parse error results in PARSE_ERROR state
   - Test master repo boundary detection (CLAUDE.md + skills/ pattern)
   - Test master repo boundary detection (.git/ pattern)
   - Test walk-up stops at master repo root
7. Run tests: `python3 -m pytest tests/test_layer_discovery.py -v`
8. Self-verify against acceptance criteria below

## Acceptance Criteria

- [ ] File `skills/cypilot/scripts/cypilot/utils/layer_discovery.py` exists
- [ ] Function `discover_layers(repo_root, cypilot_root)` returns `List[ManifestLayer]`
- [ ] Standalone repo (no master repo) returns only kit + repo layers
- [ ] Repo under master repo returns kit + master + repo layers in order
- [ ] Missing manifest at a layer is silently omitted (not an error)
- [ ] Parse errors result in `ManifestLayerState.PARSE_ERROR`
- [ ] Master repo detection works with CLAUDE.md + skills/ pattern
- [ ] Walk-up stops at master repo root (does not traverse beyond)
- [ ] `@cpt-algo:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1` marker present
- [ ] `@cpt-dod:cpt-cypilot-dod-project-extensibility-walk-up-discovery:p1` marker present
- [ ] File `tests/test_layer_discovery.py` exists with ≥6 test functions
- [ ] All tests pass: `python3.13 -m pytest tests/test_layer_discovery.py -v` exits 0
- [ ] No unresolved `{...}` template variables outside code fences

## Output Format

When complete, report results in this exact format:

```
PHASE 2/8 COMPLETE
Status: PASS | FAIL
Files created: skills/cypilot/scripts/cypilot/utils/layer_discovery.py, tests/test_layer_discovery.py
Files modified: skills/cypilot/scripts/cypilot/utils/__init__.py
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

Phase 2 is complete (PASS).
Please read the plan manifest, then execute Phase 4: "Multi-Layer Merging + Section Appending".
The phase file is: .bootstrap/.plans/implement-project-extensibility/phase-04-merge-append.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.

NOTE: Phase 3 (Includes Resolution) can run in parallel with Phase 2.
If Phase 3 is not yet complete, execute Phase 3 first before Phase 4.
```
