# Feature: Agent Integration & Workflows


<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1. Overview](#1-overview)
  - [2. Purpose](#2-purpose)
  - [3. Actors](#3-actors)
  - [4. References](#4-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Generate Agent Entry Points](#generate-agent-entry-points)
  - [Execute Generic Workflow](#execute-generic-workflow)
- [3. Processes / Business Logic (CDSL)](#3-processes-business-logic-cdsl)
  - [Discover Supported Agents](#discover-supported-agents)
  - [Generate Agent Shims](#generate-agent-shims)
  - [Compose SKILL.md](#compose-skillmd)
  - [List Workflow Files](#list-workflow-files)
- [4. States (CDSL)](#4-states-cdsl)
  - [Agent Entry Point State](#agent-entry-point-state)
- [5. Definitions of Done](#5-definitions-of-done)
  - [Agent Entry Point Generation](#agent-entry-point-generation)
  - [SKILL.md Composition](#skillmd-composition)
  - [Workflow Discovery](#workflow-discovery)
- [6. Implementation Modules](#6-implementation-modules)
- [7. Acceptance Criteria](#7-acceptance-criteria)

<!-- /toc -->

- [x] `p1` - **ID**: `cpt-cypilot-featstatus-agent-integration`

## 1. Feature Context

- [x] `p1` - `cpt-cypilot-feature-agent-integration`

### 1. Overview

Bridges Cypilot's unified skill system to diverse AI coding assistants by generating agent-native entry points, composing SKILL.md from kit `@cpt:skill` sections, and providing generic generate/analyze workflows. Each agent has its own file format and directory convention — this feature handles all the translation.

### 2. Purpose

Without this feature, users would need to manually create and maintain agent-specific files for each AI assistant. Addresses PRD requirements for multi-agent support (`cpt-cypilot-fr-core-agents`) and generic workflows (`cpt-cypilot-fr-core-workflows`).

### 3. Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Runs `cpt generate-agents` to generate/regenerate entry points |
| `cpt-cypilot-actor-ai-agent` | Consumes generated entry points, follows workflows |
| `cpt-cypilot-actor-cypilot-cli` | Executes agent generation command |

### 4. References

- **PRD**: [PRD.md](../PRD.md) — `cpt-cypilot-fr-core-agents`, `cpt-cypilot-fr-core-workflows`
- **Design**: [DESIGN.md](../DESIGN.md) — `cpt-cypilot-component-agent-generator`
- **Dependencies**: `cpt-cypilot-feature-blueprint-system`

## 2. Actor Flows (CDSL)

### Generate Agent Entry Points

- [x] `p1` - **ID**: `cpt-cypilot-flow-agent-integration-generate`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cpt generate-agents` → entry points generated for all supported agents (Windsurf, Cursor, Claude, Copilot, OpenAI)
- User runs `cpt generate-agents --agent windsurf` → entry points generated for single agent only
- User runs `cpt generate-agents --dry-run` → shows what would be generated without writing files

**Error Scenarios**:
- Cypilot not initialized → error with hint to run `cpt init`
- Kit has no `@cpt:workflow` markers → generates entry points without kit-specific workflows

**Steps**:
1. [x] - `p1` - User invokes `cpt generate-agents [--agent A] [--dry-run]` - `inst-user-agents`
2. [x] - `p1` - Resolve project root and cypilot directory - `inst-resolve-project`
3. [x] - `p1` - Ensure cypilot files are local to project (copy if external) - `inst-ensure-local`
4. - `p1` - Discover all workflow files from `.core/workflows/` and `.gen/kits/*/workflows/` - `inst-discover-workflows`
5. - `p1` - Collect `@cpt:skill` content from `.gen/kits/*/SKILL.md` - `inst-collect-skill`
6. - `p1` - Collect `@cpt:system-prompt` content from `.gen/AGENTS.md` - `inst-collect-sysprompt`
7. [x] - `p1` - **FOR EACH** supported agent (or filtered by `--agent`) - `inst-for-each-agent`
   1. - `p1` - Generate agent-native entry points (skill shims, workflow proxies, rules) - `inst-generate-entry-points`
   2. - `p1` - Write files to agent directory (e.g., `.windsurf/workflows/`, `.cursor/rules/`) - `inst-write-files`
8. - `p1` - Compose and write main SKILL.md from collected skill sections - `inst-compose-skill`
9. - `p1` - Inject managed block into root AGENTS.md - `inst-inject-agents`
10. [x] - `p1` - **RETURN** generation report (agents, files written, workflows discovered) - `inst-return-report`

### Execute Generic Workflow

- [x] `p1` - **ID**: `cpt-cypilot-flow-agent-integration-workflow`

**Actor**: `cpt-cypilot-actor-ai-agent`

**Success Scenarios**:
- Agent triggers generate workflow → loads SKILL.md, resolves kit, loads rules/template/checklist/example
- Agent triggers analyze workflow → loads SKILL.md, runs validation, presents report

**Steps**:
1. - `p1` - Agent loads SKILL.md navigation hub - `inst-load-skill`
2. - `p1` - Agent resolves workflow file from `.core/workflows/` or `.gen/kits/*/workflows/` - `inst-resolve-workflow`
3. - `p1` - Agent follows workflow execution protocol - `inst-follow-protocol`

## 3. Processes / Business Logic (CDSL)

### Discover Supported Agents

- [x] `p1` - **ID**: `cpt-cypilot-algo-agent-integration-discover-agents`

1. [x] - `p1` - Define agent registry: windsurf (`.windsurf/`), cursor (`.cursor/`), claude (`.claude/`), copilot (`.github/prompts/`), openai - `inst-define-registry`
2. - `p1` - **IF** `--agent` flag provided, filter to single agent - `inst-if-filter`
3. - `p1` - **RETURN** list of agents to generate for - `inst-return-agents`
4. [x] - `p1` - Resolve config/kits/ directory and registered kit dirs from core.toml for workflow/skill discovery - `inst-resolve-kits`
5. [x] - `p1` - Parse CLI arguments, resolve project root, cypilot root, load agent config (shared context for agents commands) - `inst-resolve-context`

### Generate Agent Shims

- [x] `p1` - **ID**: `cpt-cypilot-algo-agent-integration-generate-shims`

1. [x] - `p1` - For each workflow, create agent-native proxy file referencing the workflow path - `inst-create-proxy`
2. - `p1` - For each agent, create skill shim referencing composed SKILL.md - `inst-create-skill-shim`
3. - `p1` - Use `@/` project-root-relative paths in all references - `inst-use-relative-paths`
4. [x] - `p1` - Path helpers: compute `{cypilot_path}/`-prefixed relative paths and safe relpath for agent instructions - `inst-path-helpers`
5. [x] - `p1` - Ensure cypilot files are local: copy relevant subset into project when cypilot root is external - `inst-ensure-local-copy`
6. [x] - `p1` - Parse YAML frontmatter, strip/quote values, render agent-native templates with variable substitution - `inst-parse-frontmatter`
7. [x] - `p1` - Read-only `cmd_agents` command: list generated agent integration files per agent - `inst-cmd-agents-list`
8. [x] - `p1` - Build result dict and human-friendly formatters for generate-agents and agents commands - `inst-format-output`

### Compose SKILL.md

- [x] `p1` - **ID**: `cpt-cypilot-algo-agent-integration-compose-skill`

1. - `p1` - Read all `.gen/kits/*/SKILL.md` files - `inst-read-kit-skills`
2. - `p1` - Assemble core commands section + per-kit skill sections - `inst-assemble-sections`
3. - `p1` - Write composed SKILL.md to `.gen/SKILL.md` - `inst-write-skill`

### List Workflow Files

- [x] `p1` - **ID**: `cpt-cypilot-algo-agent-integration-list-workflows`

1. [x] - `p1` - Scan `.core/workflows/` for core workflows (analyze.md, generate.md) - `inst-scan-core-workflows`
2. - `p1` - Scan `.gen/kits/*/workflows/` for kit-generated workflows - `inst-scan-kit-workflows`
3. - `p1` - **RETURN** merged list with deduplication - `inst-return-workflows`

## 4. States (CDSL)

### Agent Entry Point State

- [x] `p1` - **ID**: `cpt-cypilot-state-agent-integration-entry-points`

```
[NOT_GENERATED] --agents--> [GENERATED] --agents--> [REGENERATED]
[GENERATED] --kit-install--> [STALE] --agents--> [REGENERATED]
```

## 5. Definitions of Done

### Agent Entry Point Generation

- [x] `p1` - **ID**: `cpt-cypilot-dod-agent-integration-entry-points`

- [x] - `p1` - `cpt generate-agents` generates entry points for all 5 supported agents
- [x] - `p1` - `cpt generate-agents --agent windsurf` generates only Windsurf entry points
- [x] - `p1` - Generated files use `@/` project-root-relative paths
- [x] - `p1` - Full overwrite on each invocation (no merge)
- [x] - `p1` - `--dry-run` flag shows what would be generated without writing

### SKILL.md Composition

- [x] `p1` - **ID**: `cpt-cypilot-dod-agent-integration-skill-composition`

- [x] - `p1` - Composed SKILL.md includes core commands section
- [x] - `p1` - Composed SKILL.md includes all `@cpt:skill` sections from installed kits
- [x] - `p1` - Composed SKILL.md written to `.gen/SKILL.md`

### Workflow Discovery

- [x] `p1` - **ID**: `cpt-cypilot-dod-agent-integration-workflow-discovery`

- [x] - `p1` - Core workflows discovered from `.core/workflows/`
- [x] - `p1` - Kit workflows discovered from `.gen/kits/*/workflows/`
- [x] - `p1` - Agent proxies route to correct workflow paths

## 6. Implementation Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| Agents Command | `skills/.../commands/agents.py` | Agent entry point generation, SKILL.md composition, workflow discovery |

## 7. Acceptance Criteria

- [x] `cpt generate-agents` produces valid entry points for Windsurf, Cursor, Claude, Copilot, and OpenAI
- [x] Agent entry points correctly reference SKILL.md and workflow files
- [x] SKILL.md composition includes all installed kit skill sections
- [x] `--dry-run` mode shows planned output without writing files
- [x] Re-running `cpt generate-agents` after kit install produces updated entry points
