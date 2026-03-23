```toml
[phase]
plan = "implement-project-extensibility"
number = 8
total = 8
type = "implement"
title = "Integration + Backward Compatibility"
depends_on = [5, 6, 7]
input_files = ["skills/cypilot/scripts/cypilot/commands/agents.py", "skills/cypilot/scripts/cypilot/utils/manifest.py", "skills/cypilot/scripts/cypilot/utils/layer_discovery.py", "skills/cypilot/scripts/cypilot/commands/resolve_vars.py"]
output_files = ["skills/cypilot/scripts/cypilot/commands/agents.py", "tests/test_integration_compat.py"]
outputs = []
inputs = ["out/phase-01-types.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, input content,
and tool commands are included below. You do not need any prior context or
external files. Follow the instructions exactly, run any EXECUTE commands
as written, and report results against the acceptance criteria at the end.

## What

Wire all previous phases together in `cmd_generate_agents()`. Modify the main flow to: discover layers, resolve includes, merge components, translate schemas, generate skills, resolve layer variables, assemble components deterministically, and optionally show provenance or discover components. Ensure backward compatibility: standalone repos with no `manifest.toml` produce identical output to current behavior. Expand `_VALID_MODELS` to accept passthrough model strings. Add `--show-layers` and `--discover` CLI flags.

## Prior Context

Phase 1: `ManifestV2`, `ManifestLayer`, component types, `parse_manifest_v2()` in `manifest.py`.
Phase 2: `discover_layers()` in `layer_discovery.py`.
Phase 3: `resolve_includes()` in `manifest.py`.
Phase 4: `merge_components()`, `apply_section_appends()`, `MergedComponents`, `ProvenanceRecord` in `manifest.py`.
Phase 5: `translate_agent_schema()`, `generate_manifest_skills()` in `agents.py`.
Phase 6: `add_layer_variables()`, `assemble_component()` in `resolve_vars.py`.
Phase 7: `build_provenance_report()`, `format_provenance_human()`, `discover_components()`, `write_discovered_manifest()` in `agents.py`.
Language: Python 3.11+, stdlib only. Traceability: FULL.

### Current cmd_generate_agents flow (simplified)

```python
def cmd_generate_agents(argv):
    # 1. Parse args (--agent, --dry-run, --json, --all)
    # 2. Find project root and cypilot root
    # 3. Load agents config from _default_agents_config()
    # 4. For each agent tool: generate workflows, skills, subagents
    # 5. Return result
```

### Current _discover_kit_agents() flow

```python
def _discover_kit_agents(cypilot_root, project_root):
    # 1. Load agents.toml from config/kits/*/
    # 2. Load agents.toml from core skill area
    # 3. Validate mode, model (ONLY "inherit" and "fast" currently)
    # 4. Return list of agent dicts
```

## Rules

### Structure Rules
- Modify existing `cmd_generate_agents()` in `agents.py`
- Keep backward compatibility path: if no manifest.toml v2.0 exists, use existing `_discover_kit_agents()` flow
- New flow: discover_layers → resolve_includes → merge_components → translate/generate/assemble

### Traceability Rules (FULL mode)
- Scope marker for the main flow
- Block markers per CDSL instruction step

### Engineering Rules
- TDD, SOLID, DRY, KISS, YAGNI
- Backward compatibility is critical: existing repos MUST produce identical output
- `_VALID_MODELS` must accept any string (passthrough) while keeping `inherit` and `fast` as known values
- `agents.toml` is read as fallback when `[[agents]]` is not present in manifest v2.0

### Forbidden
- MUST NOT break existing behavior for repos without manifest.toml
- MUST NOT add third-party dependencies
- MUST NOT modify manifest.py or layer_discovery.py (those are complete)

## Input

### CDSL: Generate with Multi-Layer Discovery Flow (from FEATURE spec)

```
ID: cpt-cypilot-flow-project-extensibility-generate-with-multi-layer

Steps:
1. Developer invokes cpt generate-agents --agent <agent>
2. Determine current repo root via find_project_root()
3. Walk up filesystem to discover manifest.toml at each layer boundary
4. Load kit manifest.toml files from core.toml kit registrations
5. FOR EACH discovered manifest: resolve includes array
6. Build base config from _default_agents_config() (core layer)
7. FOR EACH layer in resolution order: collect components, inner layer wins on ID collision
8. FOR EACH merged agent: translate extended schema fields to agent-native frontmatter
9. FOR EACH merged skill: generate skill files in agent-native format
10. FOR EACH component with append content: apply section appending
11. Build provenance report
12. RETURN generation report with per-layer provenance
```

### CDSL: DoD — Backward Compatibility

```
ID: cpt-cypilot-dod-project-extensibility-backward-compat

The system MUST produce identical output for standalone repos (no master repo) with no
manifest.toml. Existing agents.toml for kit agents MUST be read as fallback when [[agents]]
is not present in manifest.toml. The _VALID_MODELS set MUST be expanded to accept passthrough
model strings while maintaining backward compatibility with inherit and fast.
```

### New CLI Flags

| Flag | Description |
|------|-------------|
| `--show-layers` | Display provenance report instead of generating |
| `--discover` | Scan conventional dirs and populate manifest.toml before generating |
| `--json` | (existing) Output JSON; also applies to --show-layers |

### Integration Flow Pseudocode

```python
def cmd_generate_agents(argv):
    # Parse args (add --show-layers, --discover)
    # Find project root, cypilot root

    # NEW: Try multi-layer discovery
    layers = discover_layers(repo_root, cypilot_root)

    if layers_have_v2_manifests(layers):
        # NEW PATH: Multi-layer pipeline
        for layer in layers:
            if layer.manifest and layer.manifest.includes:
                layer = resolve_includes(layer.manifest, layer.path.parent)

        merged = merge_components(layers)

        if args.show_layers:
            report = build_provenance_report(merged, project_root)
            # output report and return

        if args.discover:
            discovered = discover_components(project_root)
            write_discovered_manifest(discovered, ...)
            # re-run discovery after writing

        # Add layer variables
        variables = add_layer_variables(existing_vars, layers, repo_root)

        # Generate for each target agent
        for agent_entry in merged.agents.values():
            translated = translate_agent_schema(agent_entry, target)
            # ... assemble and write

        for skill_entry in merged.skills.values():
            generate_manifest_skills(...)

    else:
        # EXISTING PATH: Legacy agents.toml flow (unchanged)
        kit_agents = _discover_kit_agents(cypilot_root, project_root)
        # ... existing flow unchanged
```

## Task

1. Read `out/phase-01-types.md` for types
2. Read current `agents.py` fully — especially `cmd_generate_agents()` and `_discover_kit_agents()`
3. Add `--show-layers` and `--discover` argparse flags to `cmd_generate_agents()`
4. Modify `_VALID_MODELS` handling:
   - Currently `_VALID_MODELS = {"inherit", "fast"}` with strict validation
   - Change to accept any string (passthrough), keep `inherit` and `fast` as documented values
   - Emit warning for unknown models (not error)
5. Add manifest v2.0 detection: check if any layer has a v2.0 manifest
6. Add the multi-layer pipeline path in `cmd_generate_agents()`:
   - Call `discover_layers()` to get layers
   - Call `resolve_includes()` for each layer's manifest
   - Call `merge_components()` to get merged result
   - Handle `--show-layers`: call `build_provenance_report()` and output
   - Handle `--discover`: call `discover_components()`, `write_discovered_manifest()`
   - Call `add_layer_variables()` to extend variables
   - For each merged agent: call `translate_agent_schema()`, assemble, write
   - For merged skills: call `generate_manifest_skills()`
7. Keep existing legacy path unchanged (when no v2.0 manifests found)
8. Prefer manifest v2.0 `[[agents]]` over separate `agents.toml` when both exist
9. Add `@cpt-*` traceability markers
10. Write tests in `tests/test_integration_compat.py`:
    - Test backward compat: no manifest.toml produces same output as before
    - Test v2.0 manifest with agents produces correct output
    - Test v2.0 manifest with skills produces skill files
    - Test --show-layers flag produces provenance report
    - Test --discover flag scans directories
    - Test passthrough model strings (not just inherit/fast)
    - Test agents.toml fallback when no [[agents]] in manifest
    - Test v2.0 preferred over agents.toml when both exist
11. Run tests: `python3 -m pytest tests/test_integration_compat.py -v`
12. Run ALL previous test files to verify no regressions:
    `python3 -m pytest tests/test_manifest_v2.py tests/test_layer_discovery.py tests/test_manifest_includes.py tests/test_merge_components.py tests/test_schema_translation.py tests/test_layer_vars.py tests/test_provenance_discovery.py tests/test_integration_compat.py -v`
13. Self-verify against acceptance criteria

## Acceptance Criteria

- [ ] `cmd_generate_agents()` supports `--show-layers` flag
- [ ] `cmd_generate_agents()` supports `--discover` flag
- [ ] Standalone repo (no manifest.toml, no master repo) produces identical output to current behavior
- [ ] V2.0 manifest with `[[agents]]` produces agent files with extended schema fields
- [ ] V2.0 manifest with `[[skills]]` produces skill files
- [ ] `agents.toml` is read as fallback when `[[agents]]` not in manifest
- [ ] V2.0 `[[agents]]` is preferred over separate `agents.toml`
- [ ] `_VALID_MODELS` accepts passthrough model strings (warning, not error)
- [ ] `--show-layers` displays provenance report
- [ ] `--discover` scans conventional directories and populates manifest
- [ ] Multi-layer pipeline: layers discovered → includes resolved → components merged → output generated
- [ ] `@cpt-flow:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1` marker present
- [ ] `@cpt-dod:cpt-cypilot-dod-project-extensibility-backward-compat:p1` marker present
- [ ] File `tests/test_integration_compat.py` exists with ≥7 test functions
- [ ] All tests pass (this phase + all previous phases): exit 0
- [ ] No unresolved `{...}` template variables outside code fences

## Output Format

When complete, report results in this exact format:

```
PHASE 8/8 COMPLETE
Status: PASS | FAIL
Files created: tests/test_integration_compat.py
Files modified: skills/cypilot/scripts/cypilot/commands/agents.py
Acceptance criteria:
  [x] Criterion 1 — PASS
  ...
Line count: {actual}/{budget}
Notes: {any issues or decisions made}
```

Then report final status:

```
PLAN COMPLETE: implement-project-extensibility
All 8 phases: PASS
Total files created: 5
Total files modified: 4
```
