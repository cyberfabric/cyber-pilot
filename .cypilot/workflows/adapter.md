---
cypilot: true
type: workflow
name: cypilot-adapter
description: Create/update project Cypilot adapter - scan structure, configure rules, generate AGENTS.md and artifacts.json
version: 1.0
purpose: Unified Cypilot adapter workflow - scan, configure, validate
---

ALWAYS open and follow `{cypilot_path}/skills/cypilot/SKILL.md` FIRST WHEN {cypilot_mode} is `off`

# Cypilot Adapter Workflow

**Type**: Operation
**Role**: Any
**Artifact**: `{adapter-directory}/AGENTS.md` + `artifacts.json` + specs

---

## Routing

This workflow is invoked through the main Cypilot workflows:

| User Intent | Route | Example |
|-------------|-------|---------|
| Create/modify adapter | **generate.md** → adapter.md | "setup adapter", "update adapter" |
| Check/validate adapter | **analyze.md** (adapter target) | "check adapter", "verify adapter" |

**Direct invocation** via `/cypilot-adapter` routes to **generate.md** (assumes write intent).

---

## Table of Contents

1. [Phase 1: Project Scan](#phase-1-project-scan)
2. [Phase 2: Configuration Proposal](#phase-2-configuration-proposal)
3. [Phase 3: Generation](#phase-3-generation)
4. [Phase 4: Agent Integration](#phase-4-agent-integration)
5. [Phase 5: Validation](#phase-5-validation)
6. [Quick Actions](#quick-actions)

---

## Prerequisite Checklist

- [ ] Agent has read execution-protocol.md
- [ ] Agent understands this workflow's purpose

---

## Overview

Unified adapter workflow that handles the complete lifecycle:
1. **Scan** - Discover project structure, existing artifacts, tech stack
2. **Configure** - Propose hierarchy, kit packages, traceability settings
3. **Generate** - Create/update adapter files
4. **Integrate** - Configure AI agent integration
5. **Validate** - Verify adapter completeness

---

ALWAYS open and follow `{cypilot_path}/requirements/execution-protocol.md` WHEN executing this workflow

## Requirements

**ALWAYS open and follow**: `{cypilot_path}/requirements/adapter-structure.md`

**ALWAYS open and follow**: `{cypilot_path}/schemas/artifacts.schema.json` WHEN generating artifacts.json

**ALWAYS open and follow**: `{cypilot_path}/requirements/reverse-engineering.md` WHEN scanning project structure (Phase 1)

Extract:
- Adapter structure requirements
- artifacts.json schema
- Spec-to-artifact-kind mapping from each kit

---

## Prerequisites

**Prerequisites**:
- [ ] Project repository exists - validate: Check .git directory exists
- [ ] Write permissions - validate: Can create directories and files

---

## Phase 1: Project Scan

### 1.1 Detect Project Root

Search for project root:
```yaml
Markers (in priority order):
  1. .cypilot-config.json (explicit Cypilot project)
  2. .git directory (git repository root)
  3. package.json, pyproject.toml, Cargo.toml, go.mod (language markers)
```

Store as: `PROJECT_ROOT`

### 1.2 Check Existing Adapter

Search for existing adapter:
```yaml
Check in order:
  1. .cypilot-config.json → cypilotAdapterPath
  2. Common locations: .cypilot-adapter/, spec/.cypilot-adapter/, docs/.cypilot-adapter/

If found:
  ADAPTER_EXISTS = true
  ADAPTER_DIR = {path}
  Load existing artifacts.json if present

If not found:
  ADAPTER_EXISTS = false
```

### 1.3 Scan Project Structure

Run comprehensive project scan following `reverse-engineering.md` methodology:

**Use Layers 1-3** from reverse engineering spec:
- Layer 1: Surface Reconnaissance (repository structure, languages, documentation)
- Layer 2: Entry Point Analysis (main entry points, bootstrap sequence)
- Layer 3: Structural Decomposition (architecture pattern, module boundaries)

#### Directory Structure Analysis
```yaml
Scan for:
  - Source directories: src/, app/, lib/, pkg/, internal/, cmd/
  - Test directories: tests/, test/, __tests__/, spec/
  - Documentation: docs/, doc/, README.md, ARCHITECTURE.md
  - Architecture: architecture/, ADR/, adr/, decisions/
  - Config files: package.json, pyproject.toml, Cargo.toml, go.mod, pom.xml
```

#### Tech Stack Detection
```yaml
Detect:
  - Languages: .ts, .js, .py, .rs, .go, .java, .cs, .rb
  - Frameworks: Django, FastAPI, Express, Next.js, Spring, etc.
  - Databases: docker-compose.yml, .env, config files
  - Infrastructure: Dockerfile, k8s/, terraform/
```

#### Existing Artifacts Detection
```yaml
Search for Cypilot artifacts:
  - PRD.md (product requirements)
  - DESIGN.md (architecture design)
  - DECOMPOSITION.md (specs manifest)
  - ADR/ directory (architecture decisions)
  - specs/ directory (spec designs)

Search for related docs:
  - README.md, CONTRIBUTING.md
  - API specs: openapi.yml, swagger.json, *.proto
  - Schemas: *.schema.json, types/, models/
```

#### Hierarchy Detection
```yaml
Identify potential hierarchy:
  - Monolith: Single system at root
  - Monorepo: packages/*, apps/*, services/*
  - Microservices: Each service directory
  - Library: lib/*, modules/*

Propose level structure:
  - system (top-level)
  - subsystem (optional)
  - component (optional)
  - module (optional)
```

### 1.4 Spec Discovery Scan

**Reference**: `{cypilot_path}/requirements/adapter-structure.md` → Spec Discovery Guide

Scan for domain-specific knowledge following the 12-domain model from Cypilot checklists:

#### Core Specs (Always Scan)

| Spec | Discovery Signals | Look In |
|------|-------------------|---------|
| `tech-stack.md` | Languages, frameworks, dependencies | `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, configs |
| `project-structure.md` | Directory layout, entry points | Root structure, README, module organization |
| `conventions.md` | Code style, naming, linting | `.eslintrc`, `.prettierrc`, `ruff.toml`, `.editorconfig`, CONTRIBUTING.md |
| `testing.md` | Test framework, patterns, coverage | Test directories, `pytest.ini`, `jest.config.js`, CI configs |
| `build-deploy.md` | Build commands, CI/CD | `Makefile`, scripts, `.github/workflows/`, `Dockerfile` |

#### Conditional Specs (Scan if Applicable)

| Spec | Trigger Condition | Discovery Signals |
|------|-------------------|-------------------|
| `domain-model.md` | DESIGN.md exists OR models/ directory | Types, schemas, entity definitions |
| `api-contracts.md` | API specs exist OR routes/ directory | OpenAPI, Swagger, Proto files, API docs |
| `patterns.md` | ADRs exist OR complex architecture | Design patterns, abstractions, ADR decisions |
| `security.md` | Auth middleware OR handles user data | Auth configs, encryption, security middleware |
| `data-governance.md` | Database migrations OR data models | Migration files, retention configs, privacy docs |
| `performance.md` | Performance tests OR caching configs | Cache configs, SLA docs, load tests |
| `reliability.md` | Health checks OR retry configs | Error handlers, circuit breakers, runbooks |
| `compliance.md` | Regulated industry markers | Compliance docs, audit logs, legal references |

#### Discovery Process

For each applicable spec:

1. **Locate signals** — Find files/patterns indicating the domain exists
2. **Extract knowledge** — Read configs, docs, and code to understand patterns
3. **Synthesize** — Create actionable guidance, not just description
4. **Reference sources** — Document where information came from

Store spec discovery results as: `SPEC_DISCOVERY_RESULTS`
Store scan results as: `SCAN_RESULTS`

---

## Phase 2: Configuration Proposal

### 2.1 Present Scan Summary

Display discovered information:

```
═══════════════════════════════════════════════════════════════════════════════
Cypilot Adapter: Project Scan Results
═══════════════════════════════════════════════════════════════════════════════

Project: {PROJECT_NAME}
Root: {PROJECT_ROOT}
Adapter: {ADAPTER_EXISTS ? "Found at " + ADAPTER_DIR : "Not found"}

───────────────────────────────────────────────────────────────────────────────
TECH STACK DETECTED
───────────────────────────────────────────────────────────────────────────────
Languages: {languages}
Frameworks: {frameworks}
Databases: {databases}
Infrastructure: {infrastructure}

───────────────────────────────────────────────────────────────────────────────
EXISTING ARTIFACTS
───────────────────────────────────────────────────────────────────────────────
Found:
  {list of found artifacts with paths}

Missing:
  {list of recommended but missing artifacts}

───────────────────────────────────────────────────────────────────────────────
PROPOSED HIERARCHY
───────────────────────────────────────────────────────────────────────────────
{hierarchy visualization}

───────────────────────────────────────────────────────────────────────────────
AI AGENTS DETECTED
───────────────────────────────────────────────────────────────────────────────
{detected agent configs: .cursor/, .windsurf/, .claude/, .github/copilot}

═══════════════════════════════════════════════════════════════════════════════
```

### 2.2 Configure Adapter Location

If adapter doesn't exist, ask user:

```
Adapter Location

Choose adapter directory:
  1. .cypilot-adapter/ (recommended - hidden, clean)
  2. .cypilot-adapter/ (visible, explicit)
  3. docs/.cypilot-adapter/ (documentation-focused)
  4. Custom path

Choice: [1-4]
```

Store as: `ADAPTER_DIR`

### 2.3 Configure Kit Package

Ask user about kit preference:

```
Kit Package

Cypilot supports multiple kit packages:

  1. cypilot-sdlc (Recommended)
     - Full Cypilot tooling support
     - Code traceability
     - Complete validation rules
     - Templates, checklists, examples included

  2. Custom
      - Define your own kit
     - Use existing project conventions
     - Must follow rules.md format

Choice: [1-2]
```

Store as: `KIT_PACKAGE`

### 2.4 Configure Hierarchy

Based on scan results, propose hierarchy:

```
System Hierarchy

Based on scan, proposed structure:

{PROJECT_NAME}/
├── {system-name}/ (system)
│   ├── artifacts:
│   │   ├── PRD.md
│   │   ├── DESIGN.md
│   │   └── DECOMPOSITION.md
│   ├── codebase:
│   │   └── src/ [.ts, .tsx]
│   └── children:
│       ├── {subsystem-1}/ (subsystem)
│       │   └── ...
│       └── {subsystem-2}/ (subsystem)

Accept this structure? [Yes] [Modify] [Manual]
```

Store as: `HIERARCHY_CONFIG`

### 2.5 Configure Traceability

For each artifact, ask about traceability:

```
Traceability Configuration

For each artifact, choose traceability level:

  FULL - Full code traceability (Cypilot markers in code)
         Best for: New code, active development

  DOCS-ONLY - Documentation only (no code markers)
              Best for: Existing codebases, documentation focus

Artifact traceability:
  - PRD.md: [FULL] [DOCS-ONLY]
  - DESIGN.md: [FULL] [DOCS-ONLY]
  - DECOMPOSITION.md: [FULL] [DOCS-ONLY]
```

Store as: `TRACEABILITY_CONFIG`

### 2.6 Cancellation Handling

**If user cancels** (selects "Cancel", provides no response, or explicitly declines):
- Do NOT create any files
- Inform user: "Adapter setup cancelled. Run `/cypilot-adapter` to restart."
- Return to normal assistant mode
- Do NOT partially save configuration

---

## Phase 3: Generation

### 3.1 Create Adapter Directory

```bash
mkdir -p {ADAPTER_DIR}/specs
```

### 3.2 Generate artifacts.json

Create `{ADAPTER_DIR}/artifacts.json` following schema:

```json
{
  "version": "1.0",
  "project_root": "{relative_path_to_project_root}",
  "kits": {
    "cypilot-sdlc": {
      "format": "Cypilot",
      "path": "{cypilot_core}/kits/sdlc"
    }
  },
  "systems": [
    {
      "name": "{SYSTEM_NAME}",
      "slug": "{system-slug}",
      "kit": "cypilot-sdlc",
      "artifacts_dir": "{artifacts_dir}",
      "artifacts": [
        { "name": "Product Requirements", "path": "{artifacts_dir}/PRD.md", "kind": "PRD", "traceability": "{TRACEABILITY}" },
        { "name": "Overall Design", "path": "{artifacts_dir}/DESIGN.md", "kind": "DESIGN", "traceability": "{TRACEABILITY}" },
        { "name": "Design Decomposition", "path": "{artifacts_dir}/DECOMPOSITION.md", "kind": "DECOMPOSITION", "traceability": "{TRACEABILITY}" }
      ],
      "codebase": [
        { "name": "{codebase_name}", "path": "{src_dir}", "extensions": ["{extensions}"] }
      ],
      "children": []
    }
  ]
}
```

**Note**: The `slug` field is required and must be lowercase with hyphens only (pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`). Example: `"name": "My App"` → `"slug": "my-app"`

**Directory configuration**:
- `artifacts_dir` — Default base directory for NEW artifacts (default: `architecture`)
- Subdirectories for specific artifact kinds (`specs/`, `ADR/`) are defined by the kit
- Individual artifact `path` values are FULL paths relative to `project_root` (user can place artifacts anywhere)


### 3.3 Generate AGENTS.md

**For each spec file discovered**:
1. Match spec name to Universal WHEN Rule from table below
2. Generate action-based WHEN rule (not tied to kit/artifact kind)

#### Universal WHEN Rules Table

| Spec File | Universal WHEN Rule |
|-----------|---------------------|
| `tech-stack.md` | WHEN writing code, choosing technologies, or adding dependencies |
| `conventions.md` | WHEN writing code, naming files/functions/variables, or reviewing code |
| `project-structure.md` | WHEN creating files, adding modules, or navigating codebase |
| `domain-model.md` | WHEN working with entities, data structures, or business logic |
| `testing.md` | WHEN writing tests, reviewing test coverage, or debugging |
| `build-deploy.md` | WHEN building, deploying, or configuring CI/CD |
| `patterns.md` | WHEN implementing features, designing components, or refactoring |
| `api-contracts.md` | WHEN creating/consuming APIs, defining endpoints, or handling requests |
| `security.md` | WHEN handling authentication, authorization, or sensitive data |
| `data-governance.md` | WHEN storing user data, handling PII, or managing data lifecycle |
| `performance.md` | WHEN optimizing, caching, or working with high-load components |
| `reliability.md` | WHEN handling errors, implementing retries, or adding health checks |
| `compliance.md` | WHEN handling regulated data, audit logging, or legal requirements |

Create `{ADAPTER_DIR}/AGENTS.md`:

```markdown
# Cypilot Adapter: {PROJECT_NAME}

**Extends**: `{relative_path_to_cypilot}/AGENTS.md`

**Version**: 1.0
**Last Updated**: {DATE}

---

## Project Overview

{PROJECT_DESCRIPTION}

---

## Navigation Rules

### Project Specs

{FOR_EACH_SPEC in adapter/specs/}
ALWAYS open and follow `specs/{SPEC_NAME}` {UNIVERSAL_WHEN_RULE}
{/FOR_EACH_SPEC}

---

## Quick Reference

- **Adapter**: `{ADAPTER_DIR}/`
- **Specs**: `{ADAPTER_DIR}/specs/`
```

**Key principle**: Rules are action-based, not kit-based. Agent loads specs when the action matches, regardless of which workflow or artifact type is active.

### 3.4 Generate Spec Files

Based on scan results, create initial spec files:

#### specs/tech-stack.md
```markdown
# Tech Stack

**Languages**: {languages}
**Frameworks**: {frameworks}
**Databases**: {databases}
**Infrastructure**: {infrastructure}

**Source**: Auto-detected from project scan
```

#### specs/conventions.md
```markdown
# Code Conventions

**File Naming**: {detected_pattern}
**Code Style**: {detected_linter_config}
**Project Structure**: {detected_structure}

**Source**: Auto-detected from project scan
```

#### specs/project-structure.md
```markdown
# Project Structure

## Directory Layout

{directory_tree}

## Key Directories

| Directory | Purpose |
|-----------|---------|
| {dir} | {purpose} |

---

**Source**: Auto-detected from project scan
**Last Updated**: {DATE}
```

#### specs/domain-model.md (if detected)
```markdown
# Domain Model

## Core Concepts

{extracted_concepts}

## Key Data Structures

{data_structures}

---

**Source**: {DESIGN.md, schemas, types directories}
**Last Updated**: {DATE}
```

#### specs/testing.md (if detected)
```markdown
# Testing Guidelines

## Test Framework

- **Framework**: {detected_framework}
- **Coverage**: {coverage_tool}
- **Threshold**: {if_detected}

## Running Tests

{detected_commands}

## Test Patterns

{detected_patterns}

---

**Source**: Auto-detected from project scan
**Last Updated**: {DATE}
```

#### Conditional Spec Files

Generate these only if discovery signals found:

| Spec | Generate When | Content |
|------|---------------|---------|
| `security.md` | Auth configs found | Auth mechanism, authorization model, data classification |
| `api-contracts.md` | OpenAPI/routes found | API patterns, contract format, versioning |
| `patterns.md` | ADRs or patterns found | Architecture patterns, design patterns |
| `data-governance.md` | Migrations/models found | Data lifecycle, retention, privacy |
| `performance.md` | Perf configs found | SLAs, caching, optimization patterns |
| `reliability.md` | Health checks found | Error handling, recovery, circuit breakers |
| `compliance.md` | Regulatory markers found | Regulations, standards, audit |

### 3.5 Create .cypilot-config.json

At project root:

```json
{
  "cypilotAdapterPath": "{relative_adapter_path}",
  "cypilotCorePath": "{relative_cypilot_core_path}"
}
```

### 3.6 Error Recovery

**If generation fails mid-phase**:
1. Note which files were created successfully
2. Delete partially created files (incomplete AGENTS.md, malformed JSON, etc.)
3. Log error to user with specific failure point
4. Suggest: "Run `/cypilot-adapter` again to restart from Phase 1"

**Do NOT leave adapter in inconsistent state** — either complete all files or rollback to previous state.

---

## Phase 4: Agent Integration

### 4.1 Detect AI Agents

Check for AI agent configurations:

```yaml
Search for:
  - .cursor/rules (Cursor)
  - .windsurfrules (Windsurf)
  - CLAUDE.md or .claude/ (Claude)
  - .github/copilot-instructions.md (Copilot)
```

### 4.2 Offer Integration

For each detected agent:

```
AI Agent Integration

Detected: {agent_name}

Would you like to configure Cypilot integration?

This will:
  - Add Cypilot workflow commands
  - Configure adapter references
  - Enable Cypilot skill invocation

Configure {agent_name}? [Yes] [No] [Later]
```

### 4.3 Generate Agent Config

For each confirmed agent, run:

```bash
cypilot agent-workflows --agent {agent}
cypilot agent-skills --agent {agent}
```

**If CLI command fails**:
- Log error output to user
- Note which agent configuration failed
- Suggest manual configuration or `/cypilot` to verify setup
- Continue with other agents if multiple configured

---

## Phase 5: Validation

### 5.1 Run Adapter Validation

Execute validation checks:

```yaml
Validate:
  1. .cypilot-config.json
     - Exists at project root
     - Valid JSON
     - Contains cypilotAdapterPath
     - Path points to valid adapter

  2. AGENTS.md
     - Exists in adapter directory
     - Contains Extends declaration
     - Contains project name

  3. artifacts.json
     - Valid against schema
     - All paths resolve correctly
      - Kit packages configured
     - Systems hierarchy valid

  4. Spec files
     - Referenced specs exist
     - Have required structure
```

### 5.2 Display Validation Report

```
═══════════════════════════════════════════════════════════════════════════════
Cypilot Adapter: Validation Report
═══════════════════════════════════════════════════════════════════════════════

Status: PASS ✅ | FAIL ❌

───────────────────────────────────────────────────────────────────────────────
CONFIGURATION
───────────────────────────────────────────────────────────────────────────────
✅ .cypilot-config.json valid
✅ cypilotAdapterPath correct
✅ cypilotCorePath correct (if set)

───────────────────────────────────────────────────────────────────────────────
ADAPTER FILES
───────────────────────────────────────────────────────────────────────────────
✅ AGENTS.md exists
✅ Extends declaration valid
✅ artifacts.json valid

───────────────────────────────────────────────────────────────────────────────
SPEC FILES
───────────────────────────────────────────────────────────────────────────────
✅ specs/tech-stack.md
✅ specs/conventions.md
⚠️ specs/domain-model.md (optional, not created)

───────────────────────────────────────────────────────────────────────────────
AGENT INTEGRATION
───────────────────────────────────────────────────────────────────────────────
✅ Claude configured
⚠️ Cursor detected but not configured

═══════════════════════════════════════════════════════════════════════════════
```

---

## Quick Actions

⚠️ **Quick Actions modify adapter state.** Always run Phase 5 validation after any Quick Action to ensure adapter consistency.

### Rescan Project

Re-run scan to detect changes:
```
Run adapter workflow with --rescan flag
```

### Update Specs

Update existing specs from detected patterns:
```
Run adapter workflow with --update-specs flag
```

### Add System

Add new system to hierarchy:
```
Run adapter workflow with --add-system {name}
```

### Configure Agent

Configure specific AI agent:
```
Run adapter workflow with --agent {windsurf|cursor|claude|copilot}
```

---

## Validation Criteria

- [ ] All workflow steps completed
- [ ] artifacts.json valid against schema
- [ ] AGENTS.md follows template
- [ ] All referenced paths exist

---

## Validation Checklist

- [ ] All prerequisites were met
- [ ] All steps were executed in order
- [ ] User confirmed configuration choices
- [ ] Validation passed

---

## Next Steps

**After successful adapter setup**:
- `/cypilot-generate PRD` — Define product requirements
- `/cypilot-generate DESIGN` — Create architecture design
- `/cypilot-generate DECOMPOSITION` — Create specs manifest

**For existing projects**:
- Review detected artifacts
- Update traceability settings as needed
- Configure additional AI agents

---

## References

**Requirements**: `{cypilot_path}/requirements/adapter-structure.md`
**Schema**: `{cypilot_path}/schemas/artifacts.schema.json`
**Methodology**: `{cypilot_path}/requirements/reverse-engineering.md`
