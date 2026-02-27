---
cypilot: true
type: requirement
name: Auto-Configuration Methodology
version: 1.0
purpose: Systematic methodology for scanning brownfield projects and generating project-specific agent rules
---

# Auto-Configuration Methodology


<!-- toc -->

- [Table of Contents](#table-of-contents)
- [Agent Instructions](#agent-instructions)
- [Overview](#overview)
  - [What Auto-Config Produces](#what-auto-config-produces)
  - [How It Uses Existing Methodologies](#how-it-uses-existing-methodologies)
- [Preconditions](#preconditions)
  - [Trigger Conditions (ANY of these)](#trigger-conditions-any-of-these)
  - [Pre-checks](#pre-checks)
- [Phase 1: Project Scan](#phase-1-project-scan)
  - [1.1 Surface Reconnaissance (RE Layer 1)](#11-surface-reconnaissance-re-layer-1)
  - [1.2 Entry Point Analysis (RE Layer 2)](#12-entry-point-analysis-re-layer-2)
  - [1.3 Structural Decomposition (RE Layer 3)](#13-structural-decomposition-re-layer-3)
  - [1.4 Pattern Recognition (RE Layer 8)](#14-pattern-recognition-re-layer-8)
  - [1.5 Scan Checkpoint](#15-scan-checkpoint)
- [Phase 1.5: Documentation Discovery](#phase-15-documentation-discovery)
  - [1.5.1 Documentation Scan](#151-documentation-scan)
  - [1.5.2 Documentation Analysis](#152-documentation-analysis)
  - [1.5.3 TOC Generation](#153-toc-generation)
  - [1.5.4 Documentation Map](#154-documentation-map)
- [Phase 2: System Detection](#phase-2-system-detection)
  - [2.1 System Identification](#21-system-identification)
  - [2.2 System Boundary Detection](#22-system-boundary-detection)
  - [2.3 Subsystem Detection](#23-subsystem-detection)
  - [2.4 System Map](#24-system-map)
  - [2.5 Topic Detection](#25-topic-detection)
    - [Standard Topic Catalog](#standard-topic-catalog)
    - [Topic Selection Rules](#topic-selection-rules)
    - [Topic Map Checkpoint](#topic-map-checkpoint)
- [Phase 3: Rule Generation](#phase-3-rule-generation)
  - [3.1 Rule File Structure](#31-rule-file-structure)
    - [Per-Topic Template Guidelines](#per-topic-template-guidelines)
    - [Critical Files Section](#critical-files-section)
  - [3.2 Rule Quality Checklist](#32-rule-quality-checklist)
  - [3.3 Rule Generation Protocol](#33-rule-generation-protocol)
- [Phase 4: AGENTS.md Integration](#phase-4-agentsmd-integration)
  - [4.1 One File = One WHEN Rule Principle](#41-one-file-one-when-rule-principle)
  - [4.2 WHEN Rules for Generated Rule Files](#42-when-rules-for-generated-rule-files)
  - [4.3 WHEN Rules for Existing Project Documentation](#43-when-rules-for-existing-project-documentation)
  - [4.4 WHEN Condition Design](#44-when-condition-design)
  - [4.5 AGENTS.md Update](#45-agentsmd-update)
- [Phase 5: Registry Update](#phase-5-registry-update)
  - [5.1 Systems Registration](#51-systems-registration)
  - [5.2 Codebase Entries](#52-codebase-entries)
  - [5.3 Registry Validation](#53-registry-validation)
- [Phase 6: Validation](#phase-6-validation)
  - [6.1 Structural Validation](#61-structural-validation)
  - [6.2 Quality Validation](#62-quality-validation)
  - [6.3 Functional Validation](#63-functional-validation)
  - [6.4 Validation Report](#64-validation-report)
- [Output Specification](#output-specification)
  - [Directory Structure](#directory-structure)
  - [Output JSON (for scripted invocation)](#output-json-for-scripted-invocation)
- [Rule File Format](#rule-file-format)
  - [Frontmatter (required)](#frontmatter-required)
  - [Table of Contents (MANDATORY)](#table-of-contents-mandatory)
  - [Content Guidelines](#content-guidelines)
- [WHEN Rule Patterns](#when-rule-patterns)
  - [Valid WHEN Conditions](#valid-when-conditions)
  - [WHEN Rule Quality](#when-rule-quality)
- [Error Handling](#error-handling)
  - [No Source Code Found](#no-source-code-found)
  - [Existing Rules Found](#existing-rules-found)
  - [Scan Incomplete](#scan-incomplete)
  - [Large Codebase](#large-codebase)
- [References](#references)

<!-- /toc -->

**Scope**: Brownfield projects where Cypilot is installed but no project-specific rules or specs exist yet

**Out of scope**: Greenfield projects (no code to scan), projects that already have configured specs/rules

---

## Table of Contents

- [Agent Instructions](#agent-instructions)
- [Overview](#overview)
- [Preconditions](#preconditions)
- [Phase 1: Project Scan](#phase-1-project-scan)
- [Phase 1.5: Documentation Discovery](#phase-15-documentation-discovery)
- [Phase 2: System Detection](#phase-2-system-detection)
- [Phase 3: Rule Generation](#phase-3-rule-generation)
- [Phase 4: AGENTS.md Integration](#phase-4-agentsmd-integration)
- [Phase 5: Registry Update](#phase-5-registry-update)
- [Phase 6: Validation](#phase-6-validation)
- [Output Specification](#output-specification)
- [Rule File Format](#rule-file-format)
- [WHEN Rule Patterns](#when-rule-patterns)
- [Error Handling](#error-handling)
- [References](#references)

---

## Agent Instructions

**ALWAYS open and follow**: This file WHEN user requests to configure Cypilot for their project, OR when auto-config workflow is triggered

**ALWAYS open and follow**: `{cypilot_path}/.core/requirements/reverse-engineering.md` for project scanning methodology (Layers 1-3, 8)

**ALWAYS open and follow**: `{cypilot_path}/.core/requirements/prompt-engineering.md` for rule quality validation

**Prerequisite**: Agent confirms understanding before proceeding:
- [ ] Agent has read and understood this methodology
- [ ] Agent has access to source code repository
- [ ] Agent will follow phases in order 1-6
- [ ] Agent will checkpoint findings after each phase
- [ ] Agent will NOT write files without user confirmation

---

## Overview

Auto-configuration scans a brownfield project and generates project-specific agent rules that teach Cypilot how to work with the codebase. The output is a set of **per-topic** rule files in `{cypilot_path}/config/rules/` and corresponding WHEN rules in `{cypilot_path}/config/AGENTS.md`. Files are split **semantically by topic** (conventions, architecture, patterns, etc.) — not by system or codebase — so each file is loaded only when the agent is doing work relevant to that topic.

**Core Principle**: Extract conventions from code, not impose them. The auto-configurator observes what the project already does and codifies those patterns into agent-consumable rules.

### What Auto-Config Produces

| Output | Location | Purpose |
|--------|----------|---------|
| Per-topic rule files | `{cypilot_path}/config/rules/{topic}.md` | Focused rules per semantic topic (conventions, architecture, patterns, etc.) |
| Doc navigation rules | `{cypilot_path}/config/AGENTS.md` | WHEN rules pointing to existing project guides/docs (with heading anchors) |
| AGENTS.md WHEN rules | `{cypilot_path}/config/AGENTS.md` | Navigation rules that load rule files contextually |
| Registry entries | `{cypilot_path}/config/artifacts.toml` | Detected systems with source paths |
| TOC updates | Existing doc files + generated rule files | Table of Contents for navigability |

### How It Uses Existing Methodologies

- **Reverse Engineering** (Layers 1-3, 8): Surface scan, entry points, structural decomposition, pattern recognition — provides raw data about the project
- **Prompt Engineering** (Layers 2, 5, 6): Clarity/specificity, anti-pattern detection, context engineering — ensures generated rules are high-quality agent instructions

---

## Preconditions

### Trigger Conditions (ANY of these)

1. **Automatic**: Brownfield project detected + no project specs in config
   - `cypilot.py info` reports `specs: []` or no specs directory
   - Existing source code directories detected
2. **Manual**: User invokes `cypilot auto-config` or asks Cypilot to configure itself
3. **Rescan**: User invokes `cypilot init --rescan` or asks to reconfigure

### Pre-checks

- [ ] Cypilot is initialized (`cypilot.py info` returns `FOUND`)
- [ ] Source code repository is accessible
- [ ] `{cypilot_path}/config/` directory exists and is writable
- [ ] No existing rules in `{cypilot_path}/config/rules/` (or `--force` flag used)

---

## Phase 1: Project Scan

**Goal**: Extract raw project data using reverse-engineering methodology

**Use**: `{cypilot_path}/.core/requirements/reverse-engineering.md` — Layers 1, 2, 3, and 8

### 1.1 Surface Reconnaissance (RE Layer 1)

Execute Layer 1 from reverse-engineering.md, focusing on:

- [ ] Repository structure scan (1.1.1-1.1.3)
- [ ] Language detection (1.2.1-1.2.2)
- [ ] Documentation inventory (1.3.1-1.3.2)

**Capture**: `project_surface` — structure, languages, docs, git patterns

### 1.2 Entry Point Analysis (RE Layer 2)

Execute Layer 2 from reverse-engineering.md, focusing on:

- [ ] Application entry points (2.1.1-2.1.2)
- [ ] Request entry points for services (2.2.1-2.2.3)
- [ ] Bootstrap sequence (2.3.1)

**Capture**: `entry_points` — main files, HTTP routes, CLI commands, workers

### 1.3 Structural Decomposition (RE Layer 3)

Execute Layer 3 from reverse-engineering.md, focusing on:

- [ ] Architectural pattern recognition (3.1.1)
- [ ] Module/package boundaries (3.1.2)
- [ ] Code organization patterns (3.2.1-3.2.2)
- [ ] Component inventory (3.3.1-3.3.2)

**Capture**: `structure` — architecture style, modules, boundaries, components

### 1.4 Pattern Recognition (RE Layer 8)

Execute Layer 8 from reverse-engineering.md, focusing on:

- [ ] Code patterns (8.1.1-8.1.3)
- [ ] Project conventions (8.2.1-8.2.3)
- [ ] Testing conventions (8.3.1-8.3.2)

**Capture**: `conventions` — naming, style, error handling, testing patterns

### 1.5 Scan Checkpoint

After completing phases 1.1-1.4, produce a scan summary:

```markdown
### Auto-Config Scan Summary

**Project**: {name}
**Languages**: {primary}, {secondary}
**Architecture**: {pattern}
**Entry points**: {count} ({types})
**Modules**: {count} ({list})
**Key conventions**:
- Naming: {convention}
- Error handling: {pattern}
- Testing: {pattern}
- File organization: {pattern}

**Systems detected**: {count}
```

Present to user for confirmation before proceeding.

---

## Phase 1.5: Documentation Discovery

**Goal**: Find existing project guides, documentation, and specs; analyze their content; generate TOC where missing; create heading-level navigation rules

### 1.5.1 Documentation Scan

Search for existing documentation in the project:

- [ ] Scan for documentation directories: `docs/`, `documentation/`, `guides/`, `wiki/`, `.github/`
- [ ] Scan for standalone guide files: `CONTRIBUTING.md`, `ARCHITECTURE.md`, `STYLE_GUIDE.md`, `CODING_STANDARDS.md`, `API.md`, `SETUP.md`, `DEPLOYMENT.md`
- [ ] Scan for ADR directories: `adr/`, `decisions/`, `architecture/decisions/`
- [ ] Scan for API docs: `openapi.yml`, `swagger.json`, `api/`, `postman/`
- [ ] Check README.md for links to other documentation
- [ ] Check for `.cypilot-adapter/specs/` (existing Cypilot specs)

**Capture**: `docs_inventory` — list of all documentation files with:
- Path
- Title (from first H1 heading)
- Has TOC (yes/no)
- Heading count
- Estimated topic/scope

### 1.5.2 Documentation Analysis

For each found document:

- [ ] Parse headings structure (H1-H4)
- [ ] Identify document scope/topic from headings and content
- [ ] Classify document type:
  - **Guide**: How-to, setup, contributing, deployment
  - **Reference**: API docs, architecture, data model
  - **Standard**: Coding standards, style guide, conventions
  - **Decision**: ADRs, RFCs, design decisions
- [ ] Determine relevant WHEN condition (when should agent load this doc?)
- [ ] Identify key headings that are most useful for agent navigation

### 1.5.3 TOC Generation

For each document **without a Table of Contents**:

- [ ] Offer to generate TOC using `cypilot toc`:

```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py toc {doc_path}
```

- [ ] Present list of docs missing TOC:

```markdown
The following project documents have no Table of Contents:

| # | File | Headings | Topic |
|---|------|----------|-------|
| 1 | `docs/architecture.md` | 12 | System architecture |
| 2 | `CONTRIBUTING.md` | 8 | Contribution guide |

→ Generate TOC for these files? [yes/no/select]
```

- [ ] If user confirms: run `cypilot toc` for each selected file
- [ ] Verify TOC was generated successfully

### 1.5.4 Documentation Map

Produce documentation inventory:

```markdown
### Project Documentation Found

| # | File | Type | Has TOC | Key Sections | WHEN Condition |
|---|------|------|---------|-------------|----------------|
| 1 | `docs/architecture.md` | Reference | ✓ | System Overview, Components, Data Flow | writing architecture code |
| 2 | `CONTRIBUTING.md` | Guide | ✓ (generated) | Setup, Code Style, PR Process | contributing or submitting PRs |
| 3 | `docs/api/endpoints.md` | Reference | ✓ | Auth, Users, Billing | writing API endpoints |

### Proposed Navigation Rules

ALWAYS open and follow `docs/architecture.md#system-overview` WHEN modifying system architecture or adding new components

ALWAYS open and follow `CONTRIBUTING.md#code-style` WHEN writing any code

ALWAYS open and follow `docs/api/endpoints.md#authentication` WHEN writing authentication code
```

Present to user for confirmation.

---

## Phase 2: System Detection

**Goal**: Identify logical systems and subsystems from project structure

### 2.1 System Identification

Based on Phase 1 scan, identify systems:

- [ ] **Monolith**: Single system with subsystems (modules/packages)
- [ ] **Monorepo**: Multiple systems in subdirectories
- [ ] **Microservices**: Multiple services in separate directories
- [ ] **Library**: Single system, possibly with examples/tests

### 2.2 System Boundary Detection

For each detected system:

- [ ] **Name**: Human-readable name derived from directory/package name
- [ ] **Slug**: Kebab-case identifier (`auth-service`, `billing-api`, `core-lib`)
- [ ] **Root path**: Directory containing the system's source code
- [ ] **Language**: Primary language of the system
- [ ] **Type**: `service`, `library`, `cli`, `worker`, `frontend`, `monolith`
- [ ] **Dependencies**: Other detected systems it depends on

### 2.3 Subsystem Detection

Within each system, identify major subsystems:

- [ ] **Domain modules** (bounded contexts, feature areas)
- [ ] **Infrastructure modules** (database, messaging, HTTP)
- [ ] **Shared modules** (utilities, common types)

### 2.4 System Map

```markdown
### Detected Systems

| # | Name | Slug | Root | Language | Type |
|---|------|------|------|----------|------|
| 1 | {name} | {slug} | {path} | {lang} | {type} |
| 2 | ... | ... | ... | ... | ... |

### Subsystems

**{system-name}**:
- {subsystem}: {path} — {description}
- ...
```

Present to user for confirmation and naming adjustments.

### 2.5 Topic Detection

**Goal**: Group scan findings into semantic topics. Each topic becomes a separate rule file.

From the Phase 1 scan data and Phase 2 system map, identify distinct **topics** — coherent clusters of related conventions, patterns, or constraints. Topics are semantic, not structural: they group by *what kind of work the agent is doing*, not by which directory it's in.

#### Standard Topic Catalog

The following topics are the default starting set. Not all will apply to every project — only generate files for topics where the scan found **concrete, project-specific content**. Skip topics that would be empty or generic.

| Topic slug | Scope | WHEN condition (typical) | Content focus |
|------------|-------|--------------------------|---------------|
| `conventions` | Naming, code style, imports, file organization | writing or reviewing code | File naming, variable naming, import order, module layout |
| `architecture` | System design, module boundaries, data flow | modifying architecture, adding components, or refactoring module boundaries | Package design, dependency rules, communication patterns, key abstractions |
| `patterns` | Recurring implementation patterns | implementing features or writing business logic | Error handling, data access, state management, DI, common idioms |
| `testing` | Test conventions, fixtures, coverage | writing or running tests | Test structure, naming, bootstrap helpers, mocking patterns, coverage rules |
| `api-contracts` | API shape, serialization, error format | writing API endpoints or CLI commands | Request/response format, error codes, output contracts, versioning |
| `infrastructure` | Build, deploy, CI/CD, dependencies | building, deploying, or configuring CI/CD | Build system, dependency management, environment setup, release process |
| `security` | Auth, secrets, input validation | writing security-sensitive code or handling user input | Auth patterns, secret management, input sanitization, permission checks |
| `anti-patterns` | What NOT to do | reviewing code or refactoring | Project-specific prohibitions with rationale |

#### Topic Selection Rules

- [ ] **Minimum content**: Only generate a topic file if the scan found ≥3 distinct, project-specific rules for it
- [ ] **No overlap with specs**: If `config/specs/` already has a file covering a topic (e.g., `testing.md`), the rule file must **complement** it (implementation-level rules), not duplicate it (high-level guidance)
- [ ] **Merge small topics**: If a topic would have <3 rules, merge it into the closest related topic
- [ ] **Split large topics**: If a topic exceeds ~120 lines, consider splitting into subtopics (e.g., `patterns-error-handling.md`, `patterns-data-access.md`)
- [ ] **Custom topics allowed**: Projects may have domain-specific topics not in the catalog (e.g., `ml-pipeline`, `event-sourcing`, `graphql-schema`)

#### Topic Map Checkpoint

```markdown
### Proposed Rule Files

| # | Topic | File | Rules | WHEN condition |
|---|-------|------|-------|----------------|
| 1 | Conventions | `rules/conventions.md` | ~{n} rules | writing or reviewing code |
| 2 | Architecture | `rules/architecture.md` | ~{n} rules | modifying architecture or module boundaries |
| 3 | Patterns | `rules/patterns.md` | ~{n} rules | implementing features |
| ...

→ Confirm topic split before generating? [yes / adjust]
```

Present to user for confirmation before proceeding to Phase 3.

---

## Phase 3: Rule Generation

**Goal**: Generate project-specific rule files from scan data

**Quality gate**: Apply `{cypilot_path}/.core/requirements/prompt-engineering.md` Layer 2 (Clarity & Specificity) and Layer 5 (Anti-Pattern Detection) to every generated rule.

### 3.1 Rule File Structure

For each topic from the Phase 2.5 topic map, generate `{cypilot_path}/config/rules/{topic}.md`:

```markdown
---
cypilot: true
type: project-rule
topic: {topic-slug}
generated-by: auto-config
version: 1.0
---

# {Topic Title}

{One-paragraph scope statement: what this file covers and when to use it}

## {Rule Group 1}

### {Rule Name}

{Imperative rule statement}

Evidence: `{file}:{line}` — {what was observed}

### {Rule Name}

...

## {Rule Group 2}

...
```

#### Per-Topic Template Guidelines

Each topic file has its own natural structure. Do NOT force all topics into the same template. Instead:

- **`conventions.md`**: Group by category (Naming, Imports, File Organization, Code Style). Each rule = one convention.
- **`architecture.md`**: Group by concern (Package Design, Module Boundaries, Communication Patterns, Key Abstractions). Include a Source Layout section.
- **`patterns.md`**: Group by pattern type (Error Handling, Data Access, State Management). Each pattern = name + when to use + evidence.
- **`testing.md`**: Group by concern (Structure, Naming, Fixtures, Coverage). Include bootstrap helper examples.
- **`api-contracts.md`**: Group by contract (Output Format, Error Codes, Exit Codes, Versioning).
- **`anti-patterns.md`**: Flat list. Each anti-pattern = name + what NOT to do + why + what to do instead.

#### Critical Files Section

One of the topic files (typically `architecture.md`) MUST include a **Critical Files** table listing the most important files to understand. This table is project-wide, not per-topic:

```markdown
## Critical Files

| File | Why it matters |
|------|---------------|
| `{path}` | {one-line explanation} |
```

### 3.2 Rule Quality Checklist

For each generated rule file, verify:

- [ ] **Focused**: File covers exactly one topic — no cross-topic content
- [ ] **Has TOC**: Table of Contents present at top of file (after frontmatter)
- [ ] **Specific**: No vague qualifiers ("appropriate", "suitable") — use exact names
- [ ] **Observable**: Every rule can be verified by inspecting code
- [ ] **Grounded**: Every claim backed by evidence from the scan (file paths, code patterns)
- [ ] **Actionable**: Agent knows exactly what to do when the topic is relevant
- [ ] **Concise**: Under 120 lines per rule file (smaller files = more focused loading)
- [ ] **No hallucination**: Only patterns actually observed in the codebase
- [ ] **No overlap**: No rule appears in more than one topic file

### 3.3 Rule Generation Protocol

For each topic in the topic map:

1. **Filter** scan data to rules belonging to this topic only
2. **Skip** if fewer than 3 project-specific rules found (merge into closest topic)
3. **Synthesize** into agent-consumable rule file using the topic's natural structure
4. **Validate** against prompt-engineering.md anti-patterns:
   - No AP-VAGUE (ambiguous language)
   - No AP-CONTEXT-BLOAT (excessive detail)
   - No AP-HALLUCINATION-PRONE (unverified claims)
5. **Present** all topic files to user as a batch for review
6. **Write** all files after confirmation
7. **Run `cypilot toc`** on each written file:
   ```bash
   python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py toc {rule_file_path}
   ```

---

## Phase 4: AGENTS.md Integration

**Goal**: Generate WHEN rules that load rule files and project docs contextually, using heading-level anchors for precision

### 4.1 One File = One WHEN Rule Principle

Since rule files are split by topic (not by system), each file is already focused on a single concern. Therefore, each topic file gets **one WHEN rule** pointing to the **whole file** — no heading anchors needed.

This is the key benefit of per-topic splitting: the WHEN condition is the file's **topic**, not a section within a monolith.

### 4.2 WHEN Rules for Generated Rule Files

For each generated topic file, create one WHEN rule using the topic's natural WHEN condition from the topic catalog (Phase 2.5):

```markdown
ALWAYS open and follow `{cypilot_path}/config/rules/conventions.md` WHEN writing or reviewing code

ALWAYS open and follow `{cypilot_path}/config/rules/architecture.md` WHEN modifying architecture, adding components, or refactoring module boundaries

ALWAYS open and follow `{cypilot_path}/config/rules/patterns.md` WHEN implementing features or writing business logic

ALWAYS open and follow `{cypilot_path}/config/rules/testing.md` WHEN writing or running tests

ALWAYS open and follow `{cypilot_path}/config/rules/api-contracts.md` WHEN writing API endpoints or CLI commands

ALWAYS open and follow `{cypilot_path}/config/rules/anti-patterns.md` WHEN reviewing code or refactoring
```

**Exception**: If a topic file exceeds ~120 lines (edge case after merge), use heading anchors to split the WHEN rules within that file.

### 4.3 WHEN Rules for Existing Project Documentation

For each discovered project document (from Phase 1.5), create WHEN rules pointing to **relevant headings**:

```markdown
ALWAYS open and follow `{doc-path}#code-style` WHEN writing any code

ALWAYS open and follow `{doc-path}#pr-process` WHEN creating or reviewing pull requests

ALWAYS open and follow `{doc-path}#deployment` WHEN deploying or configuring CI/CD

ALWAYS open and follow `{doc-path}#authentication` WHEN writing authentication code
```

**Rules for doc navigation**:
- [ ] Point to the most specific heading, not the entire doc
- [ ] Only create rules for headings that contain actionable guidance
- [ ] Skip headings that are purely informational (e.g., "History", "Credits")
- [ ] Group related WHEN rules together by topic

### 4.4 WHEN Condition Design

WHEN conditions for topic files should describe the **activity**, not the **location**:

- **Good**: `WHEN writing or reviewing code` (activity-based)
- **Bad**: `WHEN writing code in src/` (location-based — that's system-level, not topic-level)

For multi-system projects (monorepos), topic files may be scoped to a system. In that case, combine activity + scope:

```markdown
ALWAYS open and follow `{cypilot_path}/config/rules/auth-patterns.md` WHEN implementing features in the auth service
```

For single-system projects, activity alone is sufficient:

```markdown
ALWAYS open and follow `{cypilot_path}/config/rules/patterns.md` WHEN implementing features or writing business logic
```

### 4.5 AGENTS.md Update

Append generated WHEN rules to `{cypilot_path}/config/AGENTS.md`:

```markdown
## Project Documentation (auto-configured)

<!-- auto-config:docs:start -->
{WHEN rules for existing project docs, with heading anchors}
<!-- auto-config:docs:end -->

## Project Rules (auto-configured)

<!-- auto-config:rules:start -->
{WHEN rules for generated rule files, with heading anchors}
<!-- auto-config:rules:end -->
```

**MUST preserve** any existing user-written content in `config/AGENTS.md`.

---

## Phase 5: Registry Update

**Goal**: Register detected systems in artifacts registry

### 5.1 Systems Registration

For each detected system, add to `{cypilot_path}/config/artifacts.toml`:

```toml
[[systems]]
name = "{System Name}"
slug = "{slug}"
kits = "cypilot-sdlc"
source_paths = ["{path1}", "{path2}"]
```

### 5.2 Codebase Entries

For each system with source code, register codebase entries:

```toml
[[systems.artifacts]]
path = "{source-root}"
kind = "CODEBASE"
```

### 5.3 Registry Validation

- [ ] All system slugs are unique
- [ ] All source paths exist and are readable
- [ ] No duplicate entries
- [ ] Valid TOML syntax

---

## Phase 6: Validation

**Goal**: Verify auto-config output is correct and useful

### 6.1 Structural Validation

- [ ] All rule files exist at declared paths
- [ ] All WHEN rules reference existing rule files
- [ ] Registry entries point to existing directories
- [ ] TOML files are valid

### 6.2 Quality Validation

Apply prompt-engineering.md to each rule file:

- [ ] Layer 2 (Clarity): No ambiguous instructions
- [ ] Layer 5 (Anti-Patterns): No AP-VAGUE, AP-CONTEXT-BLOAT, AP-HALLUCINATION-PRONE
- [ ] Layer 6 (Context): Under 200 lines, efficient token usage

### 6.3 Functional Validation

- [ ] Agent can load rule files via WHEN rules
- [ ] Rules contain actionable, project-specific guidance
- [ ] No generic/boilerplate content that adds no value

### 6.4 Validation Report

```markdown
## Auto-Config Validation

**Systems detected**: {count}
**Topic files generated**: {count} ({list of topic slugs})
**WHEN rules added**: {count} (topic rules + doc rules)
**Registry entries added**: {count}

### Quality
- Topic file quality: {PASS|WARN} (focused, <120 lines, no overlap)
- WHEN rule validity: {PASS|FAIL}
- Registry validity: {PASS|FAIL}

### Files written
- {path}: {status}
- ...
```

---

## Output Specification

### Directory Structure

```
{cypilot_path}/config/
├── AGENTS.md          # Updated with WHEN rules (one per topic file)
├── artifacts.toml     # Updated with systems
├── rules/
│   ├── conventions.md # Per-topic: naming, code style, imports
│   ├── architecture.md# Per-topic: system design, module boundaries
│   ├── patterns.md    # Per-topic: error handling, data access, idioms
│   ├── testing.md     # Per-topic: test structure, fixtures, coverage
│   ├── api-contracts.md # Per-topic: output format, error codes
│   └── anti-patterns.md # Per-topic: what NOT to do
```

Not all topic files will be generated — only those where the scan found ≥3 project-specific rules.

Existing project docs (TOC added where missing):
```
{project-root}/
├── docs/architecture.md    # TOC generated if missing
├── CONTRIBUTING.md         # TOC generated if missing
└── ...                     # Existing docs preserved, only TOC added
```

### Output JSON (for scripted invocation)

```json
{
  "status": "PASS",
  "systems_detected": 2,
  "topics_generated": ["conventions", "architecture", "patterns", "testing"],
  "agents_rules_added": 4,
  "registry_entries_added": 2,
  "files_written": [
    "{cypilot_path}/config/rules/conventions.md",
    "{cypilot_path}/config/rules/architecture.md",
    "{cypilot_path}/config/rules/patterns.md",
    "{cypilot_path}/config/rules/testing.md"
  ],
  "docs_found": 3,
  "docs_toc_generated": 2,
  "doc_navigation_rules_added": 5
}
```

---

## Rule File Format

### Frontmatter (required)

```yaml
---
cypilot: true
type: project-rule
topic: {topic-slug}
generated-by: auto-config
version: 1.0
---
```

### Table of Contents (MANDATORY)

Every rule file MUST include a Table of Contents after the frontmatter. Generate with `cypilot toc`:

- [ ] TOC placed immediately after frontmatter and H1 title
- [ ] TOC covers all H2 and H3 headings
- [ ] TOC uses GitHub-style anchor links
- [ ] After writing, validate/update TOC with:
  ```bash
  python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py toc {rule_file_path}
  ```

### Content Guidelines

- **Max 120 lines** per topic file (smaller = more focused loading; split if exceeding)
- **Imperative mood**: "Use snake_case for functions" not "Functions should use snake_case"
- **Specific references**: Include file paths, not just descriptions
- **Evidence-based**: Every pattern claim must cite at least one file where it was observed
- **No boilerplate**: If a convention is language-default (e.g., PEP 8 for Python), don't repeat it — only document project-specific additions or deviations
- **No cross-topic content**: Each file stays within its topic boundary. If a rule fits two topics, place it in the more specific one

---

## WHEN Rule Patterns

### Valid WHEN Conditions

Activity-based conditions for topic files:

```
WHEN writing or reviewing code
WHEN modifying architecture, adding components, or refactoring module boundaries
WHEN implementing features or writing business logic
WHEN writing or running tests
WHEN writing API endpoints or CLI commands
WHEN reviewing code or refactoring
WHEN building, deploying, or configuring CI/CD
WHEN writing security-sensitive code or handling user input
```

For multi-system projects, add scope qualifier:

```
WHEN writing or reviewing code in the {system-name}
WHEN implementing features for {system-name}
```

Heading-anchor conditions for project documentation (Phase 1.5):

```
WHEN {doc-specific-activity}
```

### WHEN Rule Quality

- [ ] Condition describes an **activity** (what the agent is doing), not a **location** (which directory)
- [ ] Condition is specific enough to avoid loading unrelated topic files
- [ ] Condition is broad enough to catch all work relevant to the topic
- [ ] No overlapping conditions that load the same content twice
- [ ] Each topic file has exactly one WHEN rule (exception: files >120 lines may use heading anchors)
- [ ] Doc navigation rules use heading anchors for precision

---

## Error Handling

### No Source Code Found

```
⚠️ No source code detected in project
→ Auto-config requires existing source code to scan
→ Use 'cypilot generate' for greenfield projects instead
```
**Action**: STOP — auto-config is not applicable.

### Existing Rules Found

```
⚠️ Existing rules found in {cypilot_path}/config/rules/
→ {list existing files}
→ Use --force to overwrite, or manually merge
```
**Action**: STOP unless `--force` — preserve user customizations.

### Scan Incomplete

```
⚠️ Project scan incomplete: {reason}
→ Completed: {list}
→ Skipped: {list}
→ Rules will be generated from partial scan data
```
**Action**: WARN and continue with available data.

### Large Codebase

```
⚠️ Large codebase detected ({file_count} files)
→ Scanning top-level structure only (depth-limited)
→ Run auto-config per-system for deeper analysis: cypilot auto-config --system {slug}
```
**Action**: Limit scan depth, offer per-system deep scan.

---

## References

- Reverse Engineering: `{cypilot_path}/.core/requirements/reverse-engineering.md`
- Prompt Engineering: `{cypilot_path}/.core/requirements/prompt-engineering.md`
- Execution Protocol: `{cypilot_path}/.core/requirements/execution-protocol.md`
- Generate Workflow: `{cypilot_path}/.core/workflows/generate.md` (triggers auto-config in Brownfield prerequisite)
