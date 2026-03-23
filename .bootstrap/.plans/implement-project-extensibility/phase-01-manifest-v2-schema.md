```toml
[phase]
plan = "implement-project-extensibility"
number = 1
total = 8
type = "implement"
title = "Scaffolding + Manifest V2 Schema Parsing"
depends_on = []
input_files = ["skills/cypilot/scripts/cypilot/utils/manifest.py", "architecture/features/project-extensibility.md"]
output_files = ["skills/cypilot/scripts/cypilot/utils/manifest.py", "tests/test_manifest_v2.py"]
outputs = ["out/phase-01-types.md"]
inputs = []
```

## Preamble

This is a self-contained phase file. All rules, constraints, input content,
and tool commands are included below. You do not need any prior context or
external files. Follow the instructions exactly, run any EXECUTE commands
as written, and report results against the acceptance criteria at the end.

## What

Extend `skills/cypilot/scripts/cypilot/utils/manifest.py` with Manifest V2 data types and parsing. Add dataclasses for `ManifestV2`, `ComponentEntry`, `AgentEntry`, `SkillEntry`, `WorkflowEntry`, `RuleEntry`, and the `ManifestLayer` envelope. Add a `parse_manifest_v2()` function that parses `manifest.toml` files with `version = "2.0"` containing `[[agents]]`, `[[skills]]`, `[[workflows]]`, and `[[rules]]` component sections. Version `"1.0"` manifests MUST continue to work unchanged. This phase does NOT implement includes resolution, merging, or layer discovery — those are in later phases.

## Prior Context

Project: Cypilot — a workflow-centered methodology framework for AI-assisted software development.
Target module: `skills/cypilot/scripts/cypilot/utils/manifest.py` (383 lines currently).
This module currently handles v1.0 kit manifests (resources-only). We are extending it for v2.0 with component sections.
Language: Python 3.11+ (stdlib only — `tomllib`, `dataclasses`, `pathlib`, `typing`).
System slug: `cypilot`. Traceability: FULL.

## User Decisions

### Already Decided (pre-resolved during planning)

- **System slug**: `cypilot`
- **Traceability mode**: FULL — add `@cpt-*` markers to implementation code
- **Tech stack**: Python 3.11+, stdlib only (no third-party dependencies)
- **Test framework**: pytest with `TemporaryDirectory` pattern
- **Coverage threshold**: 90% per file

## Rules

### Structure Rules
- Add new commands in `commands/{name}.py` with `cmd_{name}(argv)` entry. Register in `cli.py`.
- Use `snake_case.py` for all Python modules.
- Use `@dataclass(frozen=True)` for value objects and domain types.
- All function signatures use type hints. Use `Optional[X]` (not `X | None`).

### Traceability Rules (FULL mode)
- Scope markers: `@cpt-{kind}:{cpt-id}:p{N}` at function/class entry point
- Block markers: `@cpt-begin:{cpt-id}:p{N}:inst-{local}` / `@cpt-end:...` wrapping specific implementation lines
- Each `@cpt-begin`/`@cpt-end` pair wraps the **smallest code fragment** implementing its CDSL instruction
- When a function implements multiple CDSL instructions, place **separate** begin/end pairs for each
- Never mark CDSL instruction `[x]` unless corresponding code block markers exist

### Engineering Rules
- TDD: Write failing test first, implement minimal code to pass, then refactor
- SOLID: Each module/function focused on one reason to change
- DRY: Remove duplication by extracting shared logic with clear ownership
- KISS: Prefer simplest correct solution matching design and project conventions
- YAGNI: No specs/abstractions not required by current design scope
- Error handling: Fail explicitly with clear errors; never silently ignore failures

### Testing Rules
- Test files mirror source structure in `tests/`
- Test methods named `test_{behavior_being_tested}`
- Use `TemporaryDirectory` for file system tests
- Coverage: 90% per file minimum

### Forbidden
- MUST NOT add third-party dependencies
- MUST NOT break v1.0 manifest parsing (backward compatibility)
- MUST NOT implement includes resolution (Phase 3)
- MUST NOT implement layer discovery (Phase 2)
- MUST NOT implement merging (Phase 4)

## Input

### CDSL: Manifest Layer State Machine (from FEATURE spec)

```
ID: cpt-cypilot-state-project-extensibility-manifest-layer

States: UNDISCOVERED, LOADED, PARSE_ERROR, INCLUDE_ERROR

Initial State: UNDISCOVERED

Transitions:
1. FROM UNDISCOVERED TO LOADED WHEN manifest.toml found and parsed successfully
2. FROM UNDISCOVERED TO UNDISCOVERED WHEN no manifest.toml at this layer (silently omitted)
3. FROM UNDISCOVERED TO PARSE_ERROR WHEN manifest.toml found but fails to parse
4. FROM UNDISCOVERED TO INCLUDE_ERROR WHEN manifest.toml parsed but includes entry fails
```

### CDSL: DoD — Manifest V2 Schema Parsing (from FEATURE spec)

```
ID: cpt-cypilot-dod-project-extensibility-manifest-v2-schema

The system MUST parse manifest.toml files with version = "2.0" containing
[[agents]], [[skills]], [[workflows]], and [[rules]] component sections,
plus an optional includes array. The [[agents]] schema MUST support extended
fields: tools, disallowed_tools, color, memory_dir, and passthrough model
values beyond inherit/fast. The schema reserves [[hooks]] and [[permissions]]
for follow-up features; the parser SHOULD accept but ignore them.
Version "1.0" manifests (resources-only) MUST continue to work unchanged.

Implements:
- cpt-cypilot-flow-project-extensibility-generate-with-multi-layer
- cpt-cypilot-algo-project-extensibility-merge-components

Touches: manifest.py
```

### Extended Agent Schema Fields (from FEATURE spec)

```
| Field              | Type      | Description                                    |
|--------------------|-----------|------------------------------------------------|
| id                 | string    | Unique agent identifier (^[a-z][a-z0-9_-]*$)  |
| description        | string    | Human-readable description                     |
| prompt_file        | string    | Path to prompt file (relative to manifest dir) |
| source             | string    | Alternative: path to existing agent file       |
| mode               | string    | readwrite or readonly                          |
| isolation          | bool      | Isolated context (tool-dependent)              |
| model              | string    | Model selection — passthrough string           |
| tools              | string[]  | Explicit tool allowlist                        |
| disallowed_tools   | string[]  | Explicit tool denylist                         |
| color              | string    | Agent color (Claude Code only)                 |
| memory_dir         | string    | Persistent memory directory path               |
| agents             | string[]  | Which tools to generate for                    |
```

### Current manifest.py structure (existing dataclasses)

```python
@dataclass(frozen=True)
class ManifestResource:
    id: str
    source: str
    default_path: str
    type: str  # "file" or "directory"
    description: str = ""
    user_modifiable: bool = True

@dataclass(frozen=True)
class Manifest:
    version: str
    root: str
    user_modifiable: bool
    resources: List[ManifestResource] = field(default_factory=list)
```

Existing functions: `load_manifest()`, `validate_manifest()`, `resolve_resource_bindings()`, `build_source_to_resource_mapping()`. All must continue to work for v1.0 manifests.

## Task

1. Read `skills/cypilot/scripts/cypilot/utils/manifest.py` to understand current structure
2. Add new dataclasses below the existing `Manifest` class:
   - `ComponentEntry` — base with `id`, `description`, `prompt_file`, `source`, `agents` (list), `append` (optional str)
   - `AgentEntry(ComponentEntry)` — adds `mode`, `isolation`, `model`, `tools`, `disallowed_tools`, `color`, `memory_dir`
   - `SkillEntry(ComponentEntry)` — skill-specific fields
   - `WorkflowEntry(ComponentEntry)` — workflow-specific fields
   - `RuleEntry(ComponentEntry)` — rule-specific fields
   - `ManifestV2` — version, includes (list of str), agents/skills/workflows/rules lists, plus resources for backward compat
   - `ManifestLayerState` — enum with UNDISCOVERED, LOADED, PARSE_ERROR, INCLUDE_ERROR
   - `ManifestLayer` — scope (str), path (Path), manifest (ManifestV2 | None), state (ManifestLayerState)
3. Add `parse_manifest_v2(path: Path) -> ManifestV2` function that:
   - Reads and parses the TOML file
   - For version "2.0": parses component sections, validates agent schema (tools/disallowed_tools mutual exclusivity)
   - For version "1.0": returns a ManifestV2 with only resources populated (backward compat wrapper)
   - Accepts but ignores `[[hooks]]` and `[[permissions]]` sections
   - Raises ValueError on parse errors with path and details
4. Add `@cpt-*` traceability markers:
   - Scope marker: `@cpt-state:cpt-cypilot-state-project-extensibility-manifest-layer:p1`
   - Scope marker: `@cpt-dod:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1`
   - Block markers around each implementation step
5. Write tests in `tests/test_manifest_v2.py`:
   - Test v2.0 parsing with all component sections
   - Test v1.0 backward compatibility (existing Manifest still works)
   - Test extended agent schema fields (tools, color, memory_dir, model)
   - Test tools + disallowed_tools mutual exclusivity error
   - Test [[hooks]] and [[permissions]] are accepted and ignored
   - Test parse error handling with clear error messages
6. Save a summary of the new types to `out/phase-01-types.md` (listing all new dataclass names and their fields) for later phases to reference
7. Run tests: `python3 -m pytest tests/test_manifest_v2.py -v`
8. Self-verify against acceptance criteria below

## Acceptance Criteria

- [ ] File `skills/cypilot/scripts/cypilot/utils/manifest.py` contains `ManifestV2` dataclass
- [ ] File `skills/cypilot/scripts/cypilot/utils/manifest.py` contains `AgentEntry` dataclass with `tools`, `disallowed_tools`, `color`, `memory_dir`, `model` fields
- [ ] File `skills/cypilot/scripts/cypilot/utils/manifest.py` contains `ManifestLayer` dataclass with `scope`, `path`, `manifest`, `state` fields
- [ ] File `skills/cypilot/scripts/cypilot/utils/manifest.py` contains `ManifestLayerState` enum with UNDISCOVERED, LOADED, PARSE_ERROR, INCLUDE_ERROR
- [ ] Function `parse_manifest_v2()` exists and parses v2.0 TOML with component sections
- [ ] v1.0 manifests continue to parse via existing `load_manifest()` function (no regressions)
- [ ] `parse_manifest_v2()` raises ValueError when both `tools` and `disallowed_tools` are set on an agent
- [ ] `parse_manifest_v2()` accepts and ignores `[[hooks]]` and `[[permissions]]`
- [ ] `@cpt-state:cpt-cypilot-state-project-extensibility-manifest-layer:p1` marker present
- [ ] `@cpt-dod:cpt-cypilot-dod-project-extensibility-manifest-v2-schema:p1` marker present
- [ ] File `tests/test_manifest_v2.py` exists with ≥6 test functions
- [ ] All tests pass: `python3.13 -m pytest tests/test_manifest_v2.py -v` exits 0
- [ ] File `out/phase-01-types.md` exists and lists all new dataclass names with fields
- [ ] No unresolved `{...}` template variables outside code fences

## Output Format

When complete, report results in this exact format:

```
PHASE 1/8 COMPLETE
Status: PASS | FAIL
Files created: tests/test_manifest_v2.py, out/phase-01-types.md
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

Phase 1 is complete (PASS).
Please read the plan manifest, then execute Phase 2: "Walk-Up Layer Discovery".
The phase file is: .bootstrap/.plans/implement-project-extensibility/phase-02-walk-up-discovery.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.
```
