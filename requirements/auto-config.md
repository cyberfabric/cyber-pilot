---
cypilot: true
type: requirement
name: Auto-Configuration Methodology
version: 1.0
purpose: Systematic methodology for scanning brownfield projects and generating project-specific agent rules
---

# Auto-Configuration Methodology

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

Auto-configuration scans a brownfield project and generates project-specific agent rules that teach Cypilot how to work with the codebase. The output is a set of rule files in `{cypilot_path}/config/rules/` and corresponding WHEN rules in `{cypilot_path}/config/AGENTS.md`.

**Core Principle**: Extract conventions from code, not impose them. The auto-configurator observes what the project already does and codifies those patterns into agent-consumable rules.

### What Auto-Config Produces

| Output | Location | Purpose |
|--------|----------|---------|
| Per-system rule files | `{cypilot_path}/config/rules/{slug}.md` | Project-specific coding rules, conventions, patterns |
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

---

## Phase 3: Rule Generation

**Goal**: Generate project-specific rule files from scan data

**Quality gate**: Apply `{cypilot_path}/.core/requirements/prompt-engineering.md` Layer 2 (Clarity & Specificity) and Layer 5 (Anti-Pattern Detection) to every generated rule.

### 3.1 Rule File Structure

For each detected system, generate `{cypilot_path}/config/rules/{slug}.md`:

```markdown
---
cypilot: true
type: project-rule
system: {slug}
generated-by: auto-config
version: 1.0
---

# {System Name} — Project Rules

## Table of Contents

<!-- TOC is MANDATORY for all rule files -->
<!-- Generate with: cypilot toc {this-file} -->

- [Overview](#overview)
- [Source Layout](#source-layout)
- [Conventions](#conventions)
- [Architecture](#architecture)
- [Key Patterns](#key-patterns)
- [Critical Files](#critical-files)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

## Overview

{One-paragraph description of the system: purpose, architecture, key technologies}

## Source Layout

{Directory structure relevant to this system}

## Conventions

### Naming
{Extracted naming conventions: files, variables, functions, classes}

### Code Style
{Extracted style conventions: indentation, imports, line length}

### Error Handling
{Extracted error handling patterns}

## Architecture

### Pattern
{Identified architecture pattern with evidence}

### Module Boundaries
{Key modules and their responsibilities}

### Dependencies
{How modules depend on each other, DI patterns}

## Key Patterns

### Data Flow
{How data moves through the system}

### State Management
{How state is managed}

### Testing
{Test organization, naming, patterns}

## Critical Files

{Most important files to understand — entry points, configuration, core abstractions}

## Anti-Patterns to Avoid

{Project-specific things NOT to do, based on existing patterns}
```

### 3.2 Rule Quality Checklist

For each generated rule file, verify:

- [ ] **Has TOC**: Table of Contents present at top of file (after frontmatter)
- [ ] **Specific**: No vague qualifiers ("appropriate", "suitable") — use exact names
- [ ] **Observable**: Every rule can be verified by inspecting code
- [ ] **Grounded**: Every claim backed by evidence from the scan (file paths, code patterns)
- [ ] **Actionable**: Agent knows exactly what to do when writing code for this system
- [ ] **Concise**: Under 200 lines per rule file (prompt-engineering.md 6.1.3 budget)
- [ ] **No hallucination**: Only patterns actually observed in the codebase

### 3.3 Rule Generation Protocol

For each system:

1. **Extract** raw data from Phase 1 scan relevant to this system
2. **Synthesize** patterns into agent-consumable rules
3. **Generate TOC** for the rule file (mandatory)
4. **Validate** against prompt-engineering.md anti-patterns:
   - No AP-VAGUE (ambiguous language)
   - No AP-CONTEXT-BLOAT (excessive detail)
   - No AP-HALLUCINATION-PRONE (unverified claims)
5. **Present** draft to user for review
6. **Write** after confirmation
7. **Run `cypilot toc`** on written file to ensure TOC is formatted and linked correctly:
   ```bash
   python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py toc {rule_file_path}
   ```

---

## Phase 4: AGENTS.md Integration

**Goal**: Generate WHEN rules that load rule files and project docs contextually, using heading-level anchors for precision

### 4.1 Heading-Level Navigation Principle

**MUST** use heading anchors (`#section-name`) in WHEN rules wherever possible, instead of pointing to entire files. This:
- Reduces context load (agent reads specific section, not entire file)
- Increases precision (agent gets exactly the relevant guidance)
- Works with TOC navigation (agent can scan TOC first, then jump to section)

**Anchor format**: GitHub-style slugs — lowercase, spaces→hyphens, strip special chars.

### 4.2 WHEN Rules for Generated Rule Files

For each generated rule file, create WHEN rules pointing to **specific headings**:

```markdown
ALWAYS open and follow `{cypilot_path}/config/rules/{slug}.md#conventions` WHEN writing code in {system-root-path}

ALWAYS open and follow `{cypilot_path}/config/rules/{slug}.md#architecture` WHEN modifying architecture or adding components in {system-root-path}

ALWAYS open and follow `{cypilot_path}/config/rules/{slug}.md#testing` WHEN writing tests for {system-name}

ALWAYS open and follow `{cypilot_path}/config/rules/{slug}.md#anti-patterns-to-avoid` WHEN reviewing code in {system-root-path}
```

For small rule files (<50 lines), a single rule pointing to the whole file is acceptable:
```markdown
ALWAYS open and follow `{cypilot_path}/config/rules/{slug}.md` WHEN writing code in {system-root-path}
```

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

### 4.4 WHEN Rule Patterns by System Type

Choose the most appropriate WHEN condition based on system type:

| System Type | WHEN Pattern |
|-------------|-------------|
| Monolith (single system) | `WHEN writing any code` |
| Service in monorepo | `WHEN writing code in {service-path}/` |
| Frontend app | `WHEN writing frontend code OR modifying UI components` |
| API service | `WHEN writing API code OR modifying endpoints in {path}/` |
| Library | `WHEN writing or modifying {library-name} library code` |
| CLI tool | `WHEN writing CLI commands OR modifying {tool-name}` |
| Worker/background | `WHEN writing background jobs OR workers in {path}/` |

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

**Systems configured**: {count}
**Rule files generated**: {count}
**WHEN rules added**: {count}
**Registry entries added**: {count}

### Quality
- Rule file quality: {PASS|WARN}
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
├── AGENTS.md          # Updated with WHEN rules (heading-level anchors)
├── artifacts.toml     # Updated with systems
├── rules/
│   ├── {slug-1}.md    # Per-system rules (with TOC)
│   ├── {slug-2}.md    # Per-system rules (with TOC)
│   └── ...
```

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
  "systems_detected": 3,
  "rules_generated": ["auth-service", "billing-api", "shared-lib"],
  "agents_rules_added": 3,
  "registry_entries_added": 3,
  "files_written": [
    "{cypilot_path}/config/rules/auth-service.md",
    "{cypilot_path}/config/rules/billing-api.md",
    "{cypilot_path}/config/rules/shared-lib.md"
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
system: {slug}
generated-by: auto-config
version: 1.0
---
```

### Table of Contents (MANDATORY)

Every rule file MUST include a Table of Contents after the frontmatter. This enables heading-level WHEN rules in AGENTS.md.

- [ ] TOC placed immediately after frontmatter and H1 title
- [ ] TOC covers all H2 and H3 headings
- [ ] TOC uses GitHub-style anchor links
- [ ] After writing, validate/update TOC with:
  ```bash
  python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py toc {rule_file_path}
  ```

### Content Guidelines

- **Max 200 lines** per rule file (context budget)
- **Imperative mood**: "Use snake_case for functions" not "Functions should use snake_case"
- **Specific references**: Include file paths, not just descriptions
- **Evidence-based**: Every pattern claim must cite at least one file where it was observed
- **No boilerplate**: If a convention is language-default (e.g., PEP 8 for Python), don't repeat it — only document project-specific additions or deviations

---

## WHEN Rule Patterns

### Valid WHEN Conditions

```
WHEN writing any code
WHEN writing code in {path}/
WHEN writing, reviewing, or modifying code in {path}/
WHEN creating or updating {kind} artifacts
WHEN implementing features for {system-name}
WHEN debugging or fixing issues in {path}/
WHEN writing tests for {system-name}
```

### WHEN Rule Quality

- [ ] Condition is specific enough to avoid loading unnecessary rules
- [ ] Condition is broad enough to catch all relevant work
- [ ] No overlapping conditions that load the same content twice
- [ ] Uses heading anchors (`#section`) where the target file has a TOC
- [ ] Heading anchors are valid (match actual heading slugs in target file)
- [ ] Each rule file has at least one WHEN rule; large files may have multiple heading-level rules

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
