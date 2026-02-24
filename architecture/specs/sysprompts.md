---
cypilot: true
type: spec
name: Project Extension Specification
version: 1.0
purpose: Define how projects extend Cypilot behavior through .cypilot/config/sysprompts and config/AGENTS.md with operation-scoped system prompts
drivers:
  - cpt-cypilot-fr-core-config
  - cpt-cypilot-fr-core-workflows
---

# Project Extension Specification

---

## Table of Contents

- [Project Extension Specification](#project-extension-specification)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Extension Directory](#extension-directory)
  - [Root AGENTS.md Entry](#root-agentsmd-entry)
  - [config/AGENTS.md](#configagentsmd)
    - [Required Structure](#required-structure)
    - [WHEN Rule Format](#when-rule-format)
  - [System Prompt Files](#system-prompt-files)
    - [Format](#format)
    - [Standard System Prompts](#standard-system-prompts)
    - [Content Principles](#content-principles)
  - [System Prompt Loading](#system-prompt-loading)
    - [When Prompts Are Loaded](#when-prompts-are-loaded)
    - [Loading Algorithm](#loading-algorithm)
    - [Interaction with Kit Prompts](#interaction-with-kit-prompts)
  - [System Prompt Discovery](#system-prompt-discovery)
  - [Validation](#validation)
    - [AGENTS.md Validation](#agentsmd-validation)
    - [System Prompt File Validation](#system-prompt-file-validation)
  - [Error Handling](#error-handling)
    - [System Prompt Not Found](#system-prompt-not-found)
    - [AGENTS.md Not Found](#agentsmd-not-found)
    - [Invalid WHEN Format](#invalid-when-format)
  - [Example](#example)
  - [References](#references)

---

## Overview

Projects extend Cypilot behavior by placing **system prompts** in `.cypilot/config/sysprompts/` and registering them via `config/AGENTS.md`. These prompts are loaded by workflows during generate, analyze, and code operations, providing project-specific context without modifying kit blueprints or core configuration.

**Key properties**:
- System prompts live in `.cypilot/config/sysprompts/*.md` — plain Markdown files
- `AGENTS.md` at `.cypilot/config/AGENTS.md` maps prompts to operations via `WHEN` rules
- Prompts are loaded at runtime — no code generation, no build step
- Project-specific: conventions, tech stack, domain model, patterns, etc.
- Complementary to kit blueprints: kit rules define artifact structure, project system prompts define project context

**What goes here vs. in kit blueprints**:

| Concern | Location |
|---------|----------|
| Artifact structure, ID kinds, heading rules | Kit blueprint (`@cpt:rules`, `@cpt:id`, `@cpt:heading`) |
| Project tech stack, naming conventions | `.cypilot/config/sysprompts/tech-stack.md` |
| Domain model, entity relationships | `.cypilot/config/sysprompts/domain-model.md` |
| API contract format | `.cypilot/config/sysprompts/api-contracts.md` |

---

## Extension Directory

```
.cypilot/
└── config/
    ├── AGENTS.md              # Navigation rules (WHEN → spec file)
    ├── core.toml              # Core config
    ├── artifacts.toml         # Artifact registry
    └── sysprompts/            # Project-specific system prompts
        ├── tech-stack.md
        ├── conventions.md
        ├── domain-model.md
        ├── patterns.md
        ├── testing.md
        └── ...
```

All sysprompt files are optional. Only files referenced in `AGENTS.md` are loaded.

---

## Root AGENTS.md Entry

Cypilot injects a managed block into the **project root** `AGENTS.md` that routes agents to `.cypilot/config/AGENTS.md`:

```markdown
<!-- @cpt:root-agents -->
ALWAYS open @/.cypilot/config/AGENTS.md FIRST
<!-- @/cpt:root-agents -->
```

**Behavior**:
- Inserted at the **beginning** of the root `AGENTS.md` file
- If the file does not exist, it is created
- The path reflects the actual install directory (e.g., `@/.cypilot/config/AGENTS.md`)
- Content between the `<!-- @cpt:root-agents -->` and `<!-- @/cpt:root-agents -->` markers is **fully managed** by Cypilot — overwritten on every check
- Manual edits inside the block are discarded

**Integrity check**: every Cypilot CLI invocation (not just `init`) verifies the block exists and the path is correct. If the block is missing or stale, it is silently re-injected.

This ensures any agent that opens the project is immediately routed to Cypilot's navigation entry point.

---

## config/AGENTS.md

**Location**: `.cypilot/config/AGENTS.md`

`.cypilot/config/AGENTS.md` is the project-level navigation file. It declares which system prompts to load for which operations. Agents reach this file via the root `AGENTS.md` entry above.

Kit workflow commands are **not** placed here — they are exposed via agent entry points (e.g., `.windsurf/workflows/cypilot-*.md`) generated from `@cpt:workflow` markers in kit blueprints (see [kit.md](./kit.md)).

### Required Structure

```markdown
# Cypilot: {Project Name}

ALWAYS open and follow `sysprompts/tech-stack.md` WHEN writing code, choosing technologies, or adding dependencies
ALWAYS open and follow `sysprompts/conventions.md` WHEN writing code, naming files/functions/variables, or reviewing code
ALWAYS open and follow `sysprompts/domain-model.md` WHEN working with entities, data structures, or business logic
ALWAYS open and follow `sysprompts/testing.md` WHEN writing tests, reviewing test coverage, or debugging
```

### WHEN Rule Format

```
ALWAYS open and follow `{sysprompt-path}` WHEN {action-description}
```

- `{sysprompt-path}` — relative to `.cypilot/config/` (e.g., `sysprompts/tech-stack.md`)
- `{action-description}` — action-based description of WHEN to load the system prompt

**Rules MUST be action-based** — they describe what the agent is doing, not which artifact kind is active:

| Correct | Incorrect |
|---------|-----------|
| `WHEN writing code, choosing technologies` | `WHEN generating DESIGN` |
| `WHEN working with entities, data structures` | `WHEN Cypilot uses kit cypilot-sdlc` |
| `WHEN writing tests, reviewing coverage` | `WHEN working on project` |

---

## System Prompt Files

System prompt files are plain Markdown documents in `.cypilot/config/sysprompts/`. Each file provides project-specific context that agents load during operations.

### Format

```markdown
# {Spec Name}

## Overview
{Brief description of what this spec covers and why it matters}

## {Content Sections}
{Domain-specific directives, constraints, and examples}

---
**Source**: {Where this knowledge was discovered — DESIGN.md, ADRs, codebase, etc.}
**Last Updated**: {Date}
```

### Standard System Prompts

| System Prompt | WHEN Rule | Contains |
|-----------|-----------|----------|
| `tech-stack.md` | writing code, choosing technologies, adding dependencies | Languages, frameworks, databases, infrastructure constraints |
| `conventions.md` | writing code, naming files/functions/variables, reviewing code | Naming conventions, code style, file organization |
| `project-structure.md` | creating files, adding modules, navigating codebase | Directory layout, module organization, entry points |
| `domain-model.md` | working with entities, data structures, business logic | Core concepts, entity relationships, invariants |
| `testing.md` | writing tests, reviewing test coverage, debugging | Test frameworks, patterns, coverage requirements |
| `patterns.md` | implementing features, designing components, refactoring | Architecture patterns, design patterns, state management |
| `api-contracts.md` | creating/consuming APIs, defining endpoints, handling requests | Contract format, endpoint patterns, protocols |
| `build-deploy.md` | building, deploying, configuring CI/CD | Build commands, CI/CD pipeline, deployment procedures |
| `security.md` | handling authentication, authorization, sensitive data | Auth mechanisms, data classification, encryption |
| `performance.md` | optimizing, caching, working with high-load components | SLAs, caching strategy, optimization patterns |
| `reliability.md` | handling errors, implementing retries, adding health checks | Error handling, recovery, circuit breakers |

Not all system prompts apply to all projects. Create only what is relevant.

### Content Principles

- **Actionable**: not just descriptions, but what to do
- **Project-specific**: conventions that differ from kit defaults
- **Source-referenced**: note where knowledge came from (DESIGN.md, ADRs, codebase)
- **No artifact content**: no PRD requirements, no ADR rationale — those belong in artifacts

---

## System Prompt Loading

### When Prompts Are Loaded

Workflows load project system prompts at specific points:

| Operation | Loaded System Prompts (via WHEN matching) |
|-----------|-------------------------------------------|
| `cypilot generate PRD` | Prompts matching "working with entities", "writing requirements" |
| `cypilot generate DESIGN` | Prompts matching "designing components", "choosing technologies" |
| `cypilot validate` | Prompts matching relevant artifact content |
| Code generation/review | `tech-stack.md`, `conventions.md`, `patterns.md` |

### Loading Algorithm

1. Determine current operation context (generate, analyze, code, etc.)
2. Read `.cypilot/config/AGENTS.md`
3. For each `WHEN` rule, match the action description against current context
4. Load matching system prompt files in declaration order
5. Inject content as system prompt context for the agent

### Interaction with Kit Prompts

Project system prompts are **additive** — they don't replace kit blueprint system prompts (`@cpt:system-prompt`). Loading order:

1. Kit `@cpt:system-prompt` (from blueprint) — artifact-kind-level directives
2. Project `.cypilot/config/sysprompts/*.md` (from AGENTS.md WHEN rules) — project-level context

If a project system prompt contradicts a kit prompt, the project system prompt takes precedence (project-specific overrides generic).

---

## System Prompt Discovery

For existing projects, Cypilot can auto-discover system prompt candidates:

```bash
cypilot init --discover
```

**Discovery process**:
1. Scan project for signals (config files, package manifests, CI configs, test directories)
2. Propose system prompt files based on findings
3. Generate draft system prompts with discovered information
4. User reviews and confirms

**Discovery signals**:

| Signal | Produces |
|--------|----------|
| `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml` | `tech-stack.md` |
| `.eslintrc`, `.prettierrc`, `ruff.toml`, `.editorconfig` | `conventions.md` |
| Test directories, `pytest.ini`, `jest.config.js` | `testing.md` |
| `Makefile`, `.github/workflows/`, `Dockerfile` | `build-deploy.md` |
| `openapi.yml`, `*.proto` | `api-contracts.md` |
| Schema/model directories, DESIGN.md domain section | `domain-model.md` |
| Auth middleware, security configs | `security.md` |

---

## Validation

### AGENTS.md Validation

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| A.1 | `.cypilot/config/AGENTS.md` exists | YES | File exists |
| A.2 | Has project name heading | YES | `# Cypilot: {name}` present |
| A.3 | All WHEN rules use action-based format | YES | Pattern: `WHEN {verb}ing ...` |
| A.4 | No orphaned WHEN rules | YES | All referenced system prompt files exist |

### System Prompt File Validation

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| S.1 | Has H1 heading | YES | `# {name}` present |
| S.2 | Has Overview section | YES | `## Overview` present |
| S.3 | Has Source reference | YES | `**Source**:` present |
| S.4 | No artifact content (PRD, ADR rationale) | YES | No requirement IDs, no decision rationale |
| S.5 | Content is actionable | YES | Contains directives, not just descriptions |

**Validation command**:
```bash
cypilot validate --sysprompts
```

---

## Error Handling

### System Prompt Not Found

```
⚠️ Orphaned WHEN rule: sysprompts/{name}.md not found
→ Referenced in: .cypilot/config/AGENTS.md
→ Fix: Create the sysprompt file OR remove the WHEN rule
```
**Action**: WARN — workflow continues without the missing spec.

### AGENTS.md Not Found

```
⚠️ Project AGENTS.md not found: .cypilot/config/AGENTS.md
→ No project-level system prompts will be loaded
→ Fix: Run `cypilot init` to create AGENTS.md
```
**Action**: WARN — workflows proceed with kit-level system prompts only.

### Invalid WHEN Format

```
⚠️ Invalid WHEN rule format in AGENTS.md
→ Line: "ALWAYS open and follow `specs/tech-stack.md` WHEN working on project"
→ Expected: action-based description (WHEN writing code, WHEN designing, etc.)
→ Fix: Use specific action verbs
```
**Action**: WARN — rule is skipped during loading.

---

## Example

A complete project extension for a TypeScript web application:

`.cypilot/config/AGENTS.md`:
```markdown
# Cypilot: MyApp

ALWAYS open and follow `sysprompts/tech-stack.md` WHEN writing code, choosing technologies, or adding dependencies
ALWAYS open and follow `sysprompts/conventions.md` WHEN writing code, naming files/functions/variables, or reviewing code
ALWAYS open and follow `sysprompts/domain-model.md` WHEN working with entities, data structures, or business logic
ALWAYS open and follow `sysprompts/testing.md` WHEN writing tests, reviewing test coverage, or debugging
ALWAYS open and follow `sysprompts/api-contracts.md` WHEN creating/consuming APIs, defining endpoints, or handling requests
```

`.cypilot/config/sysprompts/tech-stack.md`:
```markdown
# Tech Stack

## Overview
MyApp is a TypeScript monorepo using Next.js for the frontend and Fastify for the API.

## Languages
- **TypeScript** 5.x — all application code
- **SQL** — database migrations (raw SQL, no ORM)

## Frameworks
- **Next.js** 14 — frontend (App Router, Server Components)
- **Fastify** 4 — API server
- **Drizzle ORM** — database access

## Database
- **PostgreSQL** 16 — primary datastore
- **Redis** 7 — caching and sessions

## Infrastructure
- **Docker** — local development
- **Vercel** — frontend deployment
- **Fly.io** — API deployment

---
**Source**: DESIGN.md (Section 2.1 Technology Stack)
**Last Updated**: 2026-02-23
```

---

## References

- **Kit specification**: `specs/kit/blueprint.md` — blueprint `@cpt:system-prompt` and `@cpt:workflow` markers
- **Rules format**: `specs/kit/rules.md` — workflow entry point
- **CLI**: `specs/cli.md` — `init`, `agents`, `validate --sysprompts` commands
