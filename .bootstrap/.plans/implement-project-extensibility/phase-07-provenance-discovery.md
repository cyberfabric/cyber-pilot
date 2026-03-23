```toml
[phase]
plan = "implement-project-extensibility"
number = 7
total = 8
type = "implement"
title = "Provenance Report + Auto-Discovery + CLI Flags"
depends_on = [4]
input_files = ["skills/cypilot/scripts/cypilot/commands/agents.py", "skills/cypilot/scripts/cypilot/utils/manifest.py"]
output_files = ["skills/cypilot/scripts/cypilot/commands/agents.py", "tests/test_provenance_discovery.py"]
outputs = []
inputs = ["out/phase-01-types.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, input content,
and tool commands are included below. You do not need any prior context or
external files. Follow the instructions exactly, run any EXECUTE commands
as written, and report results against the acceptance criteria at the end.

## What

Add provenance report building and component auto-discovery to `agents.py`. Implement `build_provenance_report()` which formats MergedComponents provenance into human-readable and JSON output. Implement `discover_components()` which scans conventional directories for agents, skills, and workflows. Add `--show-layers` and `--discover` argument parsing (but do NOT wire them into the main flow — Phase 8 handles that).

## Prior Context

Phase 1: Added `ManifestV2`, `ManifestLayer`, component types.
Phase 2: Added `discover_layers()`.
Phase 3: Added `resolve_includes()`.
Phase 4: Added `merge_components()` → `MergedComponents` with `ProvenanceRecord`.
Language: Python 3.11+, stdlib only. Traceability: FULL.

## Rules

### Structure Rules
- Add to existing `agents.py`
- All function signatures use type hints
- Provenance output should use existing `ui` module for human-readable output

### Traceability Rules (FULL mode)
- Scope markers for both algorithms
- Block markers per CDSL instruction step

### Engineering Rules
- TDD, SOLID, DRY, KISS, YAGNI
- Provenance report must be JSON-serializable
- Auto-discovery scans fixed conventional paths only

### Forbidden
- MUST NOT wire into `cmd_generate_agents` main flow (Phase 8)
- MUST NOT modify `manifest.py` (Phases 1-4 own that)
- MUST NOT add third-party dependencies

## Input

### CDSL: Build Provenance Report Algorithm

```
ID: cpt-cypilot-algo-project-extensibility-build-provenance

Input: MergedComponents with provenance metadata
Output: ProvenanceReport (per-component: winning layer, overridden layers, resolved paths)

Steps:
1. FOR EACH component type
   1.1 FOR EACH component ID in merged results
      1.1.1 Record: component ID, component type, winning layer (scope + manifest path),
            list of overridden layers (scope + manifest path each), final resolved source path,
            include origin if from an included manifest
2. Sort by component type, then by component ID
3. RETURN structured report (JSON-serializable)
```

### CDSL: Discover and Register Components Flow (Steps 2-4)

```
ID: cpt-cypilot-flow-project-extensibility-discover-register (partial)

Steps:
2. Scan conventional directories for components:
   - .claude/agents/*.md for agents
   - .claude/skills/*/SKILL.md for skills
   - .claude/commands/*.md for workflows
3. FOR EACH discovered component: generate manifest entry
4. Write component sections into the appropriate manifest.toml
```

### Provenance Report Format

Human-readable (--show-layers):
```
Layer Provenance Report
=======================
Agents:
  my-agent        Repo (.bootstrap/config/manifest.toml)    overrides: Kit
  review-agent    Kit (config/kits/sdlc/manifest.toml)

Skills:
  my-skill        Repo (.bootstrap/config/manifest.toml)
```

JSON (--show-layers --json):
```json
{
  "components": [
    {
      "id": "my-agent",
      "type": "agent",
      "winning_scope": "repo",
      "winning_path": ".bootstrap/config/manifest.toml",
      "overridden": [{"scope": "kit", "path": "config/kits/sdlc/manifest.toml"}]
    }
  ]
}
```

### Conventional Discovery Directories

| Component Type | Directory Pattern | ID Derivation |
|---------------|-------------------|---------------|
| agents | `.claude/agents/*.md` | filename stem |
| skills | `.claude/skills/*/SKILL.md` | parent directory name |
| workflows | `.claude/commands/*.md` | filename stem |

## Task

1. Read `out/phase-01-types.md` for types from Phase 1
2. Read current `agents.py` to understand existing patterns
3. Add `build_provenance_report(merged: MergedComponents, project_root: Path) -> Dict[str, Any]`:
   - Iterate all component types in merged result
   - Build structured report with winning layer, overridden layers, source paths
   - Sort by type then ID for deterministic output
   - Return JSON-serializable dict
4. Add `format_provenance_human(report: Dict[str, Any]) -> str`:
   - Format report as human-readable table
5. Add `discover_components(project_root: Path) -> Dict[str, List[Dict[str, str]]]`:
   - Scan conventional directories
   - Return dict of component_type → list of discovered entries
   - Each entry has id, source path, description (from frontmatter if available)
6. Add `write_discovered_manifest(discovered: Dict, manifest_path: Path) -> None`:
   - Write or update manifest.toml with discovered component sections
7. Add `@cpt-*` traceability markers
8. Write tests in `tests/test_provenance_discovery.py`:
   - Test provenance report with single layer
   - Test provenance report with overrides across layers
   - Test provenance report JSON serializability
   - Test human-readable provenance format
   - Test component discovery finds agents in .claude/agents/
   - Test component discovery finds skills in .claude/skills/
   - Test component discovery with empty directories
   - Test manifest writing from discovered components
9. Run tests: `python3 -m pytest tests/test_provenance_discovery.py -v`
10. Self-verify against acceptance criteria

## Acceptance Criteria

- [ ] `build_provenance_report()` function exists in `agents.py`
- [ ] Report includes winning_scope, winning_path, overridden layers per component
- [ ] Report is sorted by type then ID
- [ ] Report is JSON-serializable
- [ ] `format_provenance_human()` produces human-readable table
- [ ] `discover_components()` scans .claude/agents/*.md, .claude/skills/*/SKILL.md, .claude/commands/*.md
- [ ] Discovery returns component entries with id and source path
- [ ] `write_discovered_manifest()` writes valid manifest.toml
- [ ] `@cpt-algo:cpt-cypilot-algo-project-extensibility-build-provenance:p2` marker present
- [ ] `@cpt-flow:cpt-cypilot-flow-project-extensibility-discover-register:p2` marker present
- [ ] File `tests/test_provenance_discovery.py` exists with ≥7 test functions
- [ ] All tests pass: `python3.13 -m pytest tests/test_provenance_discovery.py -v` exits 0
- [ ] No unresolved `{...}` template variables outside code fences

## Output Format

When complete, report results in this exact format:

```
PHASE 7/8 COMPLETE
Status: PASS | FAIL
Files created: tests/test_provenance_discovery.py
Files modified: skills/cypilot/scripts/cypilot/commands/agents.py
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

Phase 7 is complete (PASS).
Please read the plan manifest, then execute Phase 8: "Integration + Backward Compatibility".
The phase file is: .bootstrap/.plans/implement-project-extensibility/phase-08-integration-compat.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.

NOTE: Phases 5, 6, and 7 can run in parallel (all depend only on Phase 4).
Verify Phases 5 and 6 are also complete before executing Phase 8.
```
