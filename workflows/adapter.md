---
fdd: true
type: workflow
name: fdd-adapter
description: Create/update project FDD adapter - scan structure, configure rules, generate AGENTS.md and artifacts.json
version: 1.0
purpose: Unified FDD adapter workflow - scan, configure, validate
---

# FDD Adapter Workflow

**Type**: Operation
**Role**: Any
**Artifact**: `{adapter-directory}/AGENTS.md` + `artifacts.json` + specs

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
2. **Configure** - Propose hierarchy, rules packages, traceability settings
3. **Generate** - Create/update adapter files
4. **Integrate** - Configure AI agent integration
5. **Validate** - Verify adapter completeness

---

ALWAYS open and follow `../requirements/execution-protocol.md` WHEN executing this workflow

## Requirements

**ALWAYS open and follow**: `../requirements/adapter-structure.md`

**ALWAYS open and follow**: `../schemas/artifacts.schema.json` WHEN generating artifacts.json

**ALWAYS open and follow**: `../requirements/reverse-engineering.md` WHEN scanning project structure (Phase 1)

Extract:
- Adapter structure requirements
- artifacts.json schema

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
  1. .fdd-config.json (explicit FDD project)
  2. .git directory (git repository root)
  3. package.json, pyproject.toml, Cargo.toml, go.mod (language markers)
```

Store as: `PROJECT_ROOT`

### 1.2 Check Existing Adapter

Search for existing adapter:
```yaml
Check in order:
  1. .fdd-config.json → fddAdapterPath
  2. Common locations: FDD-Adapter/, .adapter/, spec/FDD-Adapter/, docs/FDD-Adapter/

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
Search for FDD artifacts:
  - PRD.md (product requirements)
  - DESIGN.md (architecture design)
  - FEATURES.md (features manifest)
  - ADR/ directory (architecture decisions)
  - features/ directory (feature designs)

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

Store scan results as: `SCAN_RESULTS`

---

## Phase 2: Configuration Proposal

### 2.1 Present Scan Summary

Display discovered information:

```
═══════════════════════════════════════════════════════════════════════════════
FDD Adapter: Project Scan Results
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
  1. .adapter/ (recommended - hidden, clean)
  2. FDD-Adapter/ (visible, explicit)
  3. docs/FDD-Adapter/ (documentation-focused)
  4. Custom path

Choice: [1-4]
```

Store as: `ADAPTER_DIR`

### 2.3 Configure Rules Package

Ask user about rules preference:

```
Rules Package

FDD supports multiple rules packages:

  1. fdd-sdlc (Recommended)
     - Full FDD tooling support
     - Code traceability
     - Complete validation rules
     - Templates, checklists, examples included

  2. Custom
     - Define your own rules
     - Use existing project conventions
     - Must follow rules.md format

Choice: [1-2]
```

Store as: `RULES_PACKAGE`

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
│   │   └── FEATURES.md
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

  FULL - Full code traceability (FDD markers in code)
         Best for: New code, active development

  DOCS-ONLY - Documentation only (no code markers)
              Best for: Existing codebases, documentation focus

Artifact traceability:
  - PRD.md: [FULL] [DOCS-ONLY]
  - DESIGN.md: [FULL] [DOCS-ONLY]
  - FEATURES.md: [FULL] [DOCS-ONLY]
```

Store as: `TRACEABILITY_CONFIG`

### 2.6 Cancellation Handling

**If user cancels** (selects "Cancel", provides no response, or explicitly declines):
- Do NOT create any files
- Inform user: "Adapter setup cancelled. Run `/fdd-adapter` to restart."
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
  "rules": {
    "fdd-sdlc": {
      "format": "FDD",
      "path": "{fdd_core}/rules/sdlc"
    }
  },
  "systems": [
    {
      "name": "{SYSTEM_NAME}",
      "rules": "fdd-sdlc",
      "artifacts": [
        { "name": "Product Requirements", "path": "{artifacts_dir}/PRD.md", "kind": "PRD", "traceability": "{TRACEABILITY}" },
        { "name": "Overall Design", "path": "{artifacts_dir}/DESIGN.md", "kind": "DESIGN", "traceability": "{TRACEABILITY}" },
        { "name": "Features Manifest", "path": "{artifacts_dir}/features/FEATURES.md", "kind": "FEATURES", "traceability": "{TRACEABILITY}" }
      ],
      "codebase": [
        { "name": "{codebase_name}", "path": "{src_dir}", "extensions": ["{extensions}"] }
      ],
      "children": []
    }
  ]
}
```

### 3.3 Generate AGENTS.md

Create `{ADAPTER_DIR}/AGENTS.md`:

```markdown
# FDD Adapter: {PROJECT_NAME}

**Extends**: `{relative_path_to_fdd}/AGENTS.md`

**Version**: 1.0
**Last Updated**: {DATE}
**Tech Stack**: {TECH_STACK_SUMMARY}

---

## Project Structure

{HIERARCHY_OVERVIEW}

---

## Navigation Rules

ALWAYS open and follow `specs/tech-stack.md` WHEN FDD follows rules `{RULES_ID}` for artifact kinds: DESIGN, ADR OR codebase

ALWAYS open and follow `specs/domain-model.md` WHEN FDD follows rules `{RULES_ID}` for artifact kinds: DESIGN, FEATURES, FEATURE OR codebase

ALWAYS open and follow `specs/api-contracts.md` WHEN FDD follows rules `{RULES_ID}` for artifact kinds: DESIGN, ADR, FEATURE OR codebase

ALWAYS open and follow `specs/patterns.md` WHEN FDD follows rules `{RULES_ID}` for artifact kinds: DESIGN, ADR, FEATURE OR codebase

ALWAYS open and follow `specs/conventions.md` WHEN FDD follows rules `{RULES_ID}` for codebase

ALWAYS open and follow `specs/build-deploy.md` WHEN FDD follows rules `{RULES_ID}` for codebase

ALWAYS open and follow `specs/testing.md` WHEN FDD follows rules `{RULES_ID}` for codebase

---

## Artifacts Registry

See `artifacts.json` for complete artifact configuration including:
- Rules packages
- System hierarchy
- Traceability settings
```

**Note**: `{RULES_ID}` is the rules package identifier from artifacts.json (e.g., `fdd-sdlc`)

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

#### specs/domain-model.md (if detected)
```markdown
# Domain Model

**Format**: {detected_format}
**Location**: {detected_location}

**Source**: Auto-detected from project scan
```

### 3.5 Create .fdd-config.json

At project root:

```json
{
  "fddAdapterPath": "{relative_adapter_path}",
  "fddCorePath": "{relative_fdd_core_path}"
}
```

### 3.6 Error Recovery

**If generation fails mid-phase**:
1. Note which files were created successfully
2. Delete partially created files (incomplete AGENTS.md, malformed JSON, etc.)
3. Log error to user with specific failure point
4. Suggest: "Run `/fdd-adapter` again to restart from Phase 1"

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

Would you like to configure FDD integration?

This will:
  - Add FDD workflow commands
  - Configure adapter references
  - Enable FDD skill invocation

Configure {agent_name}? [Yes] [No] [Later]
```

### 4.3 Generate Agent Config

For each confirmed agent, run:

```bash
fdd agent-workflows --agent {agent}
fdd agent-skills --agent {agent}
```

**If CLI command fails**:
- Log error output to user
- Note which agent configuration failed
- Suggest manual configuration or `/fdd` to verify setup
- Continue with other agents if multiple configured

---

## Phase 5: Validation

### 5.1 Run Adapter Validation

Execute validation checks:

```yaml
Validate:
  1. .fdd-config.json
     - Exists at project root
     - Valid JSON
     - Contains fddAdapterPath
     - Path points to valid adapter

  2. AGENTS.md
     - Exists in adapter directory
     - Contains Extends declaration
     - Contains project name

  3. artifacts.json
     - Valid against schema
     - All paths resolve correctly
     - Rules packages configured
     - Systems hierarchy valid

  4. Spec files
     - Referenced specs exist
     - Have required structure
```

### 5.2 Display Validation Report

```
═══════════════════════════════════════════════════════════════════════════════
FDD Adapter: Validation Report
═══════════════════════════════════════════════════════════════════════════════

Status: PASS ✅ | FAIL ❌

───────────────────────────────────────────────────────────────────────────────
CONFIGURATION
───────────────────────────────────────────────────────────────────────────────
✅ .fdd-config.json valid
✅ fddAdapterPath correct
✅ fddCorePath correct (if set)

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
- `/fdd-generate PRD` — Define product requirements
- `/fdd-generate DESIGN` — Create architecture design
- `/fdd-generate FEATURES` — Create features manifest

**For existing projects**:
- Review detected artifacts
- Update traceability settings as needed
- Configure additional AI agents

---

## References

**Requirements**: `../requirements/adapter-structure.md`
**Schema**: `../schemas/artifacts.schema.json`
**Methodology**: `../requirements/reverse-engineering.md`
