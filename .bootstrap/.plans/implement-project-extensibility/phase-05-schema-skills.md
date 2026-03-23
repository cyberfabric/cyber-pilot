```toml
[phase]
plan = "implement-project-extensibility"
number = 5
total = 8
type = "implement"
title = "Extended Agent Schema Translation + Skills Generation"
depends_on = [4]
input_files = ["skills/cypilot/scripts/cypilot/commands/agents.py", "skills/cypilot/scripts/cypilot/utils/manifest.py"]
output_files = ["skills/cypilot/scripts/cypilot/commands/agents.py", "tests/test_schema_translation.py"]
outputs = []
inputs = ["out/phase-01-types.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, input content,
and tool commands are included below. You do not need any prior context or
external files. Follow the instructions exactly, run any EXECUTE commands
as written, and report results against the acceptance criteria at the end.

## What

Add extended agent schema translation and skills generation to `agents.py`. Implement `translate_agent_schema()` which maps semantic agent fields (tools, disallowed_tools, color, memory_dir, model) to agent-native frontmatter for all five supported tools (Claude Code, Cursor, GitHub Copilot, OpenAI Codex, Windsurf). Implement `generate_manifest_skills()` which generates skill files from `[[skills]]` manifest entries. This phase does NOT wire into the main `cmd_generate_agents` flow (Phase 8).

## Prior Context

Phase 1: Added `ManifestV2`, `AgentEntry`, `SkillEntry`, `WorkflowEntry`, `RuleEntry`, `ComponentEntry`.
Phase 2: Added `discover_layers()` in `layer_discovery.py`.
Phase 3: Added `resolve_includes()` in `manifest.py`.
Phase 4: Added `merge_components()`, `apply_section_appends()`, `MergedComponents`, `ProvenanceRecord`.
Language: Python 3.11+, stdlib only. Traceability: FULL.

## Rules

### Structure Rules
- Add to existing `agents.py`
- All function signatures use type hints
- Use existing helper functions (`_write_or_skip`, `_render_template`, `_target_path_from_root`) where possible

### Traceability Rules (FULL mode)
- Scope markers for both algorithms
- Block markers per CDSL instruction step

### Engineering Rules
- TDD, SOLID, DRY, KISS, YAGNI
- Each per-tool translator is a separate function (existing pattern: `_agent_template_claude`, `_agent_template_cursor`, etc.)
- Reuse existing `_TOOL_AGENT_CONFIG` dict pattern

### Forbidden
- MUST NOT wire into `cmd_generate_agents` (Phase 8)
- MUST NOT modify `manifest.py` (Phases 1-4 own that)
- MUST NOT add third-party dependencies

## Input

### CDSL: Translate Extended Agent Schema Algorithm

```
ID: cpt-cypilot-algo-project-extensibility-translate-agent-schema

Input: semantic agent definition (from merged manifest), target agent tool
Output: agent-native frontmatter/config dict

Steps:
1. Validate mutual exclusivity of tools and disallowed_tools — error if both present
2. IF target is claude: build YAML frontmatter with all supported fields (tools, disallowedTools, model, isolation, color); inject memory_dir reference in prompt body if present
3. IF target is cursor: build YAML frontmatter with mode/model; tools field has limited mapping (grep, view, edit, bash) — custom MCP tools not supported
4. IF target is copilot: build YAML frontmatter with tools array; no model/isolation/color support
5. IF target is openai (Codex): build TOML config with sandbox_mode (from mode), model, developer_instructions; per-agent tool restrictions are not supported (managed at MCP server level)
6. IF target is windsurf: skip agent generation (no subagent support) with skip reason
7. RETURN translated config dict
```

### CDSL: Generate Skills Algorithm

```
ID: cpt-cypilot-algo-project-extensibility-generate-skills

Input: merged [[skills]] components, target agent, project root
Output: list of generated skill files

Steps:
1. FOR EACH skill in merged components where target agent is in agents list
   1.1 Read prompt_file (or source) content from the skill's resolved path
   1.2 Apply agent-specific frontmatter wrapper
   1.3 Determine output path using agent-native conventions
   1.4 Write skill file to output path
2. Track created/updated/unchanged in result dict
3. RETURN list of generated skill files with status
```

### Per-Tool Translation Table (from FEATURE spec)

| Semantic Field | Claude Code | Cursor | GitHub Copilot | OpenAI Codex |
|----------------|-------------|--------|----------------|--------------|
| `mode: readonly` | `disallowedTools: Write, Edit` | `readonly: true` | `tools: ["read","search"]` | `sandbox_mode = "read-only"` |
| `mode: readwrite` | `tools: Bash,Read,Write,Edit,Glob,Grep` | `tools: grep,view,edit,bash` | `tools: ["*"]` | `sandbox_mode = "workspace-write"` |
| `model` | direct passthrough to `model:` | `model:` field | n/a | `model` field |
| `isolation: true` | `isolation: worktree` | n/a | n/a | n/a (always sandboxed) |
| `tools` | `tools:` list | limited tool strings | `tools` JSON array | n/a (MCP server level) |
| `disallowed_tools` | `disallowedTools:` list | n/a (ignored) | n/a (ignored) | n/a (ignored) |
| `color` | `color:` in frontmatter | n/a (ignored) | n/a (ignored) | n/a (ignored) |
| `memory_dir` | injected in prompt body | n/a (ignored) | n/a (ignored) | n/a (ignored) |

### Skill Output Paths per Agent Tool

| Agent Tool | Skill Output Path |
|-----------|-------------------|
| claude | `.claude/skills/{id}/SKILL.md` |
| cursor | `.cursor/rules/{id}.mdc` |
| copilot | `.github/skills/{id}.md` |
| openai | `.agents/skills/{id}/SKILL.md` |
| windsurf | `.windsurf/skills/{id}/SKILL.md` |

### Existing Template Functions (in agents.py)

The existing `_agent_template_claude()`, `_agent_template_cursor()`, `_agent_template_copilot()` functions handle basic mode/isolation/model translation for kit-declared agents (from `agents.toml`). The new extended schema functions handle manifest-declared agents (from `[[agents]]` in `manifest.toml` v2.0) which have additional fields (tools, disallowed_tools, color, memory_dir).

## Task

1. Read `out/phase-01-types.md` for types from Phase 1
2. Read current `agents.py` to understand existing template functions and `_TOOL_AGENT_CONFIG`
3. Add `translate_agent_schema(agent: AgentEntry, target: str) -> Dict[str, Any]`:
   - Validate tools/disallowed_tools mutual exclusivity
   - Dispatch to per-tool translator based on target
   - Return dict with `frontmatter` (list of str), `body_prefix` (str), `skip` (bool), `skip_reason` (str)
4. Add per-tool translators:
   - `_translate_claude_schema(agent: AgentEntry) -> Dict[str, Any]` — full support for all fields
   - `_translate_cursor_schema(agent: AgentEntry) -> Dict[str, Any]` — mode/model only, limited tools
   - `_translate_copilot_schema(agent: AgentEntry) -> Dict[str, Any]` — tools array only
   - `_translate_codex_schema(agent: AgentEntry) -> Dict[str, Any]` — TOML config with sandbox_mode
   - `_translate_windsurf_schema(agent: AgentEntry) -> Dict[str, Any]` — skip with reason
5. Add `generate_manifest_skills(skills: Dict[str, SkillEntry], target: str, project_root: Path, dry_run: bool) -> Dict[str, Any]`:
   - Iterate skills where target is in skill's agents list
   - Read source content, apply frontmatter, write to output path
   - Use `_write_or_skip()` for file writing
   - Return result dict with created/updated/unchanged lists
6. Add `@cpt-*` traceability markers
7. Write tests in `tests/test_schema_translation.py`:
   - Test Claude translation with tools, color, memory_dir, model, isolation
   - Test Claude translation with disallowed_tools
   - Test tools + disallowed_tools mutual exclusivity error
   - Test Cursor translation (limited tool mapping)
   - Test Copilot translation (tools array)
   - Test Codex translation (sandbox_mode from mode)
   - Test Windsurf skip behavior
   - Test skill generation for Claude (writes SKILL.md)
   - Test skill generation filters by target agent
8. Run tests: `python3 -m pytest tests/test_schema_translation.py -v`
9. Self-verify against acceptance criteria

## Acceptance Criteria

- [ ] `translate_agent_schema()` function exists in `agents.py`
- [ ] Claude translation includes tools, disallowedTools, model, isolation, color, memory_dir
- [ ] Cursor translation maps mode to limited tool strings
- [ ] Copilot translation produces tools JSON array
- [ ] Codex translation produces sandbox_mode from mode field
- [ ] Windsurf returns skip=True with skip_reason
- [ ] tools + disallowed_tools raises ValueError
- [ ] `generate_manifest_skills()` function exists in `agents.py`
- [ ] Skills are generated only for matching target agent
- [ ] Claude skill output path is `.claude/skills/{id}/SKILL.md`
- [ ] `@cpt-algo:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1` marker present
- [ ] `@cpt-algo:cpt-cypilot-algo-project-extensibility-generate-skills:p1` marker present
- [ ] File `tests/test_schema_translation.py` exists with ≥8 test functions
- [ ] All tests pass: `python3.13 -m pytest tests/test_schema_translation.py -v` exits 0
- [ ] No unresolved `{...}` template variables outside code fences

## Output Format

When complete, report results in this exact format:

```
PHASE 5/8 COMPLETE
Status: PASS | FAIL
Files created: tests/test_schema_translation.py
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

Phase 5 is complete (PASS).
Please read the plan manifest, then execute Phase 8: "Integration + Backward Compatibility".
The phase file is: .bootstrap/.plans/implement-project-extensibility/phase-08-integration-compat.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.

NOTE: Phases 5, 6, and 7 can run in parallel (all depend only on Phase 4).
Verify Phases 6 and 7 are also complete before executing Phase 8.
```
