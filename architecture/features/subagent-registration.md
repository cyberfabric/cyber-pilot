# Feature: Subagent Registration


<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1.1 Overview](#11-overview)
  - [1.2 Purpose](#12-purpose)
  - [1.3 Actors](#13-actors)
  - [1.4 References](#14-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Generate Subagent Definitions](#generate-subagent-definitions)
  - [Invoke Cypilot Subagent](#invoke-cypilot-subagent)
- [3. Processes / Business Logic (CDSL)](#3-processes--business-logic-cdsl)
  - [Detect Tool Subagent Capability](#detect-tool-subagent-capability)
  - [Resolve Subagent Template](#resolve-subagent-template)
  - [Generate Subagent Files](#generate-subagent-files)
- [4. States (CDSL)](#4-states-cdsl)
  - [Subagent Registration State](#subagent-registration-state)
- [5. Definitions of Done](#5-definitions-of-done)
  - [Subagent Generation for Claude Code](#subagent-generation-for-claude-code)
  - [Subagent Generation for Cursor](#subagent-generation-for-cursor)
  - [Subagent Generation for GitHub Copilot](#subagent-generation-for-github-copilot)
  - [Subagent Generation for OpenAI Codex](#subagent-generation-for-openai-codex)
  - [Built-in Defaults with Config Override](#built-in-defaults-with-config-override)
  - [Windsurf Graceful Skip](#windsurf-graceful-skip)
  - [Dry Run Support](#dry-run-support)
- [6. Acceptance Criteria](#6-acceptance-criteria)
- [Additional Context](#additional-context)

<!-- /toc -->

- [ ] `p1` - **ID**: `cpt-cypilot-featstatus-subagent-registration`

## 1. Feature Context

- [x] `p2` - `cpt-cypilot-feature-subagent-registration`

### 1.1 Overview

Extend cypilot's multi-agent integration to generate two purpose-built subagent definitions for tools that support isolated agent contexts: Claude Code (`.claude/agents/`), Cursor (`.cursor/agents/`), GitHub Copilot (`.github/agents/`), and OpenAI Codex (`.codex/agents/`). Currently `cypilot agents --agent <name>` generates only skills, commands, and workflow proxies — missing the subagent integration surface that four of five supported tools now provide.

Problem: Cypilot workflows cannot run as isolated subagents with scoped tools, model selection, and dedicated prompts.
Primary value: Users get two cypilot subagents (`cypilot-codegen` for fully-specified code generation, `cypilot-pr-review` for isolated PR review) that their IDE/agent tool can auto-delegate to, with appropriate read/write restrictions per workflow.
Key assumptions: Subagent formats across tools have stabilized sufficiently for code generation. Windsurf does not support subagents and is excluded from this feature. Subagents are purpose-built — not mirrors of existing skills.

### 1.2 Purpose

Enable `cypilot agents` to generate tool-specific subagent definitions so that two purpose-built workflows (`cypilot-codegen` and `cypilot-pr-review`) run as isolated subagents with appropriate tool restrictions, model selection, and custom prompts.

### 1.3 Actors

| Actor | Role in Feature |
|-------|-----------------|
| Developer | Runs `cypilot agents --agent <name>` to generate subagent definitions |
| AI Assistant | Main IDE/agent session delegates to cypilot subagents |

### 1.4 References

- **PRD**: [PRD.md](../PRD.md)
- **Design**: [DESIGN.md](../DESIGN.md)

## 2. Actor Flows (CDSL)

### Generate Subagent Definitions

- [ ] `p1` - **ID**: `cpt-cypilot-flow-subagent-reg-generate`

**Actor**: Developer

**Success Scenarios**:
- Developer runs `cypilot generate-agents --agent claude` and two subagent files (`cypilot-codegen.md`, `cypilot-pr-review.md`) are generated in `.claude/agents/` alongside existing skills/commands
- Developer runs `cypilot generate-agents --agent copilot` and two subagent files are generated in `.github/agents/` with `.agent.md` extension
- Developer runs with `--dry-run` and sees planned output without file writes

**Error Scenarios**:
- Target tool does not support subagents (Windsurf) — info message logged, subagent generation skipped, other outputs (skills/workflows) still generated
- `agents.toml` missing or malformed in all discovery sources — subagent generation skipped with reason or parse warning
- Output directory not writable — filesystem error reported

**Steps**:
1. [ ] - `p1` - Developer invokes `cypilot generate-agents --agent <name>` - `inst-invoke`
2. [ ] - `p1` - Discover semantic subagent definitions from kit/core `agents.toml` files - `inst-load-config`
3. [ ] - `p1` - Resolve tool output behavior from built-in `_TOOL_AGENT_CONFIG` - `inst-detect`
4. [ ] - `p1` - **IF** tool has no subagent config (Windsurf, unknown tools) - `inst-check-support`
   1. [ ] - `p1` - Mark subagent generation as skipped with reason - `inst-skip-info`
   2. [ ] - `p1` - Continue with existing skills/workflows generation - `inst-continue-existing`
5. [ ] - `p1` - Resolve subagent proxy templates — replace `{target_agent_path}` in per-tool proxy output with resolved shared agent file path, render via `_render_template()` - `inst-resolve`
6. [ ] - `p1` - Generate subagent files using format-specific rendering (Markdown+YAML or TOML) - `inst-generate`
7. [ ] - `p1` - **RETURN** JSON summary of generated files (subagents + skills + workflows) - `inst-return-summary`

### Invoke Cypilot Subagent

- [ ] `p2` - **ID**: `cpt-cypilot-flow-subagent-reg-invoke`

**Actor**: AI Assistant

**Success Scenarios**:
- Main session auto-delegates code generation to `cypilot-codegen` subagent when requirements are fully specified
- Main session delegates PR review to `cypilot-pr-review` subagent for isolated checklist-based analysis

**Error Scenarios**:
- Subagent files not generated yet — main session falls back to skill invocation
- Subagent prompt references missing SKILL.md — agent reports dependency error

**Steps**:
1. [ ] - `p2` - Main session receives task matching a cypilot subagent description - `inst-match-task`
2. [ ] - `p2` - Host tool spawns isolated subagent context with scoped tools and prompt - `inst-spawn`
3. [ ] - `p2` - Subagent reads referenced SKILL.md and follows workflow entry point - `inst-read-skill`
4. [ ] - `p2` - Subagent completes work within isolated context - `inst-complete`
5. [ ] - `p2` - **RETURN** results/summary to main session - `inst-return-results`

## 3. Processes / Business Logic (CDSL)

### Detect Tool Subagent Capability

- [ ] `p1` - **ID**: `cpt-cypilot-algo-subagent-reg-detect-capability`

**Input**: Tool name (string: `claude`, `cursor`, `copilot`, `openai`, `windsurf`)

**Output**: Subagent config dict or None (from `_TOOL_AGENT_CONFIG` lookup)

**Steps**:
1. [ ] - `p1` - Discover subagent definitions from kit/core `agents.toml` files via `_discover_kit_agents()` - `inst-check-override`
2. [ ] - `p1` - Look up tool-specific output config in `_TOOL_AGENT_CONFIG` built-in map - `inst-lookup-defaults`
3. [ ] - `p1` - **IF** tool is `claude` **RETURN** config with output_dir=`.claude/agents`, format=markdown, two definitions - `inst-claude`
4. [ ] - `p1` - **IF** tool is `cursor` **RETURN** config with output_dir=`.cursor/agents`, format=markdown, two definitions - `inst-cursor`
5. [ ] - `p1` - **IF** tool is `copilot` **RETURN** config with output_dir=`.github/agents`, filename_format=`{name}.agent.md`, two definitions - `inst-copilot`
6. [ ] - `p1` - **IF** tool is `openai` **RETURN** config with output_dir=`.codex/agents`, format=toml, two definitions - `inst-openai`
7. [ ] - `p1` - **IF** tool is `windsurf` or unknown **RETURN** None (no subagent support) - `inst-windsurf`

### Resolve Subagent Template

- [ ] `p1` - **ID**: `cpt-cypilot-algo-subagent-reg-resolve-template`

**Input**: Subagent definition (name, template, optional description/prompt_lines), shared definitions, target agent path

**Output**: Rendered subagent proxy content (string)

**Steps**:
1. [ ] - `p1` - Look up shared description and prompt_lines from `_shared` map by subagent name - `inst-load-def`
2. [ ] - `p1` - Replace `{target_agent_path}` in prompt lines with resolved shared agent file path - `inst-resolve-paths`
3. [ ] - `p1` - **IF** format is markdown (claude, cursor, copilot) - `inst-check-md-yaml`
   1. [ ] - `p1` - Render via `_render_template()` with name, description, prompt, target_agent_path variables - `inst-render-yaml`
4. [ ] - `p1` - **IF** format is `toml` (openai) - `inst-check-toml`
   1. [ ] - `p1` - Render via `_render_toml_agents()` with `[agents.<name>]` sections containing description and developer_instructions - `inst-render-toml`
5. [ ] - `p1` - **RETURN** rendered content - `inst-return-content`

### Generate Subagent Files

- [ ] `p1` - **ID**: `cpt-cypilot-algo-subagent-reg-generate-files`

**Input**: Resolved subagent config (definitions, output_dir, filename_format, format), project root, dry_run flag

**Output**: List of written file paths (or planned paths if dry_run)

**Steps**:
1. [ ] - `p1` - Determine output directory from subagent config - `inst-get-dir`
2. [ ] - `p1` - **IF** format is `toml` - `inst-check-toml`
   1. [ ] - `p1` - Render all definitions into single `cypilot-agents.toml` file - `inst-render-toml-file`
   2. [ ] - `p1` - Write or compare against existing file - `inst-write-toml`
3. [ ] - `p1` - **ELSE** (markdown format) - `inst-check-md`
   1. [ ] - `p1` - **FOR EACH** subagent definition - `inst-loop-agents`
      1. [ ] - `p1` - Determine filename from name and filename_format - `inst-determine-filename`
      2. [ ] - `p1` - Render template with resolved variables - `inst-render-content`
      3. [ ] - `p1` - **IF** dry_run, collect planned path; **ELSE** write file (create or update) - `inst-write-file`
4. [ ] - `p1` - **RETURN** list of created/updated file paths and actions - `inst-return-paths`

## 4. States (CDSL)

### Subagent Registration State

Not applicable because this is a stateless code generation feature. The `cypilot agents` command produces output files in a single invocation with no lifecycle transitions or persistent state between runs.

## 5. Definitions of Done

### Subagent Generation for Claude Code

- [ ] `p1` - **ID**: `cpt-cypilot-dod-subagent-reg-claude`

The system **MUST** generate two proxy files in `.claude/agents/` when `cypilot generate-agents --agent claude` is invoked:
- `cypilot-codegen.md` — YAML frontmatter with tools (Bash, Read, Write, Edit, Glob, Grep), model (inherit), isolation (worktree), and prompt referencing the shared agent file via `{target_agent_path}` for code generation workflow
- `cypilot-pr-review.md` — YAML frontmatter with tools (Bash, Read, Glob, Grep), disallowedTools (Write, Edit), model (sonnet), and prompt referencing the shared agent file via `{target_agent_path}` for PR review workflow

**Implements**:
- `cpt-cypilot-flow-subagent-reg-generate`
- `cpt-cypilot-algo-subagent-reg-resolve-template`
- `cpt-cypilot-algo-subagent-reg-generate-files`


### Subagent Generation for Cursor

- [ ] `p1` - **ID**: `cpt-cypilot-dod-subagent-reg-cursor`

The system **MUST** generate two proxy files in `.cursor/agents/` when `cypilot generate-agents --agent cursor` is invoked:
- `cypilot-codegen.md` — YAML frontmatter with tools (grep, view, edit, bash), model (inherit), and prompt referencing the shared agent file via `{target_agent_path}` for code generation workflow
- `cypilot-pr-review.md` — YAML frontmatter with tools (grep, view, bash), readonly (true), model (fast), and prompt referencing the shared agent file via `{target_agent_path}` for PR review workflow

**Implements**:
- `cpt-cypilot-flow-subagent-reg-generate`
- `cpt-cypilot-algo-subagent-reg-resolve-template`


### Subagent Generation for GitHub Copilot

- [ ] `p1` - **ID**: `cpt-cypilot-dod-subagent-reg-copilot`

The system **MUST** generate two proxy files in `.github/agents/` with `.agent.md` extension when `cypilot generate-agents --agent copilot` is invoked:
- `cypilot-codegen.agent.md` — YAML frontmatter with tools (["*"]) and prompt referencing the shared agent file via `{target_agent_path}` for code generation workflow
- `cypilot-pr-review.agent.md` — YAML frontmatter with tools (["read", "search"]) and prompt referencing the shared agent file via `{target_agent_path}` for PR review workflow

**Implements**:
- `cpt-cypilot-flow-subagent-reg-generate`
- `cpt-cypilot-algo-subagent-reg-resolve-template`


### Subagent Generation for OpenAI Codex

- [ ] `p1` - **ID**: `cpt-cypilot-dod-subagent-reg-openai`

The system **MUST** generate a single `cypilot-agents.toml` file in `.codex/agents/` with two `[agents.<name>]` sections (cypilot_codegen and cypilot_pr_review) containing description and developer_instructions when `cypilot agents --agent openai` is invoked.

**Implements**:
- `cpt-cypilot-flow-subagent-reg-generate`
- `cpt-cypilot-algo-subagent-reg-resolve-template`


### Built-in Defaults with Config Override

- [ ] `p1` - **ID**: `cpt-cypilot-dod-subagent-reg-config`

The system **MUST** provide built-in per-tool output mapping via `_TOOL_AGENT_CONFIG` for all four supported tools. Semantic subagent definitions are discovered from `agents.toml` (kit/core precedence). Existing `workflows` and `skills` sections **MUST** remain unchanged (backward compatible).

**Implements**:
- `cpt-cypilot-algo-subagent-reg-detect-capability`


### Windsurf Graceful Skip

- [ ] `p2` - **ID**: `cpt-cypilot-dod-subagent-reg-windsurf-skip`

The system **MUST** mark subagent generation as skipped with a reason when `cypilot generate-agents --agent windsurf` is invoked, without affecting existing workflow/skill generation for Windsurf.

**Implements**:
- `cpt-cypilot-flow-subagent-reg-generate`
- `cpt-cypilot-algo-subagent-reg-detect-capability`


### Dry Run Support

- [ ] `p2` - **ID**: `cpt-cypilot-dod-subagent-reg-dry-run`

The system **MUST** support `--dry-run` for subagent generation, showing planned file paths and content summaries without writing files, consistent with existing `--dry-run` behavior for skills/workflows.

**Implements**:
- `cpt-cypilot-algo-subagent-reg-generate-files`


## 6. Acceptance Criteria

- [ ] `cypilot generate-agents --agent claude` generates two files in `.claude/agents/` (`cypilot-codegen.md`, `cypilot-pr-review.md`) with correct YAML frontmatter
- [ ] `cypilot generate-agents --agent cursor` generates two files in `.cursor/agents/` with correct YAML frontmatter including readonly for pr-review
- [ ] `cypilot generate-agents --agent copilot` generates two files in `.github/agents/` with `.agent.md` extension
- [ ] `cypilot generate-agents --agent openai` generates single `cypilot-agents.toml` with two agent sections in TOML format
- [ ] `cypilot generate-agents --agent windsurf` skips subagent generation with skip reason in JSON output
- [ ] Existing skills/commands/workflows generation is unchanged for all tools
- [ ] `--dry-run` shows planned subagent files without writing
- [ ] Generated subagent proxies correctly reference the shared agent file via `{target_agent_path}` resolution
- [ ] Tool-specific properties (disallowedTools, readonly, isolation, model) are rendered per tool format
- [ ] `cypilot-codegen` subagent has write tools and isolation; `cypilot-pr-review` subagent is read-only
- [ ] Built-in defaults from `_TOOL_AGENT_CONFIG` are used; subagent definitions discovered from `agents.toml`

## Additional Context

**Subagent definitions**:

| Subagent | Purpose | Write Access | Isolation |
|----------|---------|-------------|-----------|
| `cypilot-codegen` | Code generation when requirements are 100% clear — no back-and-forth | Yes (full tools) | Yes (worktree on Claude Code) |
| `cypilot-pr-review` | Structured PR review in isolated context — keeps detailed analysis separate | No (read-only) | No |

**Tool-specific property mapping**:

| Property | Claude Code | Cursor | GitHub Copilot | OpenAI Codex |
|----------|------------|--------|----------------|--------------|
| Read-only enforcement | `disallowedTools: Write, Edit` | `readonly: true` | Tool list excludes write tools | Not supported |
| Model selection | `model: sonnet` / `model: inherit` | `model: fast` / `model: inherit` | N/A | N/A |
| Isolation | `isolation: worktree` | Not supported | Not supported | Not supported |
| File extension | `.md` | `.md` | `.agent.md` | `.toml` (single file) |
| Config format | Markdown + YAML frontmatter | Markdown + YAML frontmatter | Markdown + YAML frontmatter | TOML |

**Non-applicable checklist domains**:
- PERF: Not applicable because this is a one-shot file generation command with no performance-sensitive paths
- SEC: Not applicable because generated files contain only prompt text and tool lists, no secrets or user data
- REL: Not applicable because file generation is atomic per file with no retry/recovery requirements
- DATA: Not applicable because no persistent data storage; output is static files
- INT: Not applicable because no external API calls; reads local config and writes local files
- OPS: Not applicable because CLI command with JSON output, no runtime observability needed
- COMPL: Not applicable because no regulatory or privacy concerns in generated agent definition files
- UX: Not applicable because CLI command, no UI
