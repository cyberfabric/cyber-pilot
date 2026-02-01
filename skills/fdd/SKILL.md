---
name: fdd
description: Framework for Documentation and Development - AI agent toolkit. Use when user works with PRD, DESIGN, FEATURES, ADR, feature specs, architecture documentation, requirements, or mentions FDD/workflow/artifact/adapter/traceability. Provides structured artifact templates, validation, design-to-code traceability, and guided code implementation with traceability markers. Opt-in - suggest enabling when design/architecture activities detected.
---

# FDD Unified Tool

## Goal

Provides comprehensive FDD artifact management and implementation:
1. **Template-Based Validation**: Validates artifacts against FDD templates with marker parsing
2. **Cross-Reference Validation**: Validates references between artifacts (PRD → DESIGN → FEATURES → feature designs)
3. **Code Traceability**: Codebase scanning to verify implemented items are tagged in code
4. **Search**: ID lookup and traceability across FDD artifacts
5. **Design-to-Code Implementation**: Guided code generation from design specs with `@fdd-*` traceability markers

## Table of Contents

1. [Preconditions](#preconditions)
2. [🛡️ Protocol Guard (MANDATORY)](#️-protocol-guard-mandatory)
3. [Agent-Safe Invocation](#agent-safe-invocation-mandatory)
4. [Command Reference](#command-reference)
   - [Validation Commands](#validation-commands)
   - [Search Commands](#search-commands)
   - [Traceability Commands](#traceability-commands)
   - [Adapter & Agent Integration](#adapter--agent-integration)
5. [Project Configuration](#project-configuration)
6. [AI Agent Integration (Opt-In)](#ai-agent-integration-opt-in)

## Out of Scope

FDD does **NOT**:
- Replace code review (validates structure, not logic)
- Manage version control (Git operations are user responsibility)
- Enforce coding style (use linters/formatters for that)
- Provide IDE features (syntax highlighting, autocomplete)

FDD **DOES** support code generation via `/fdd-generate` with `KIND=CODE` using `rules/sdlc/codebase/rules.md`.

## Preconditions

1. ALWAYS follow `../SKILLS.md` Toolchain Preflight
2. `python3` is available
3. Target paths exist and are readable

---

## 🛡️ Protocol Guard (MANDATORY)

**BEFORE any FDD workflow action**, agent MUST complete this checklist:

### Protocol Guard Checklist

- [ ] Ran `fdd adapter-info` command
- [ ] Checked adapter status (FOUND/NOT_FOUND)
- [ ] If FOUND: Read `{adapter_dir}/AGENTS.md`
- [ ] If FOUND: Parsed WHEN clauses for current target
- [ ] Listed loaded specs in response

```
┌─────────────────────────────────────────────────────────┐
│ FDD PROTOCOL CHECK                                      │
│                                                         │
│ 1. Run: fdd adapter-info                                │
│ 2. IF adapter FOUND:                                    │
│    → Read {adapter_dir}/AGENTS.md                       │
│    → Parse WHEN clauses for current target              │
│    → Load ALL matched specs BEFORE proceeding           │
│ 3. List loaded specs in response                        │
│                                                         │
│ VIOLATION: Editing codebase without listing loaded      │
│ specs = protocol failure. STOP and re-run check.        │
└─────────────────────────────────────────────────────────┘
```

**Why this matters**:
- Context may be lost after conversation compaction
- AGENTS.md contains critical project-specific rules
- Skipping specs = inconsistent output quality

**Self-verification template** (MUST include in response when editing code):
```
FDD Context:
- Adapter: {path}
- Target: {artifact|codebase}
- Specs loaded: {list paths or "none required"}
```

**If specs NOT loaded but should be**: STOP, load them, THEN proceed.

### Error Recovery

**If adapter-info fails**:
```
⚠ FDD initialization error: {error}
→ Check python3 is available: python3 --version
→ Check FDD path: ls {FDD_ROOT}/skills/fdd/scripts/
→ Report issue if persists
```

**If AGENTS.md cannot be read**:
```
⚠ Adapter found but AGENTS.md missing/corrupted
→ Run /fdd-adapter to regenerate
→ Continue with FDD core defaults
```

### What NOT To Do

❌ **Skip Protocol Guard**: "I already checked earlier" - context may be compacted
❌ **Assume adapter exists**: Run adapter-info every time
❌ **Proceed without listing specs**: Always include FDD Context block
❌ **Guess spec paths**: Read AGENTS.md, don't assume

---

## Agent-Safe Invocation (MANDATORY)

**MUST** prefer invoking this tool via the script entrypoint (avoids `cwd`/`PYTHONPATH` issues):
```bash
python3 <FDD_ROOT>/skills/fdd/scripts/fdd.py <subcommand> [options]
```

**MUST NOT** use `python3 -m fdd.cli` unless the current working directory is `<FDD_ROOT>/skills/fdd/scripts`.

**Pattern arguments**:
- If a value starts with `-`, **MUST** pass it using `=` form (example: `--pattern=-req-`).

## Command Reference

### Validation Commands

#### validate

Validate FDD artifacts using template-based parsing.

```bash
python3 scripts/fdd.py validate [--artifact <path>] [--verbose] [--output <path>]
```

**Options**:
- `--artifact` — Path to specific artifact (if omitted, validates all registered artifacts)
- `--verbose` — Print full validation report
- `--output` — Save report to file

**Exit codes**: 0 = PASS, 1 = filesystem error, 2 = FAIL

#### validate-rules

Validate FDD rules configuration and template files.

```bash
python3 scripts/fdd.py validate-rules [--rule <id>] [--template <path>] [--verbose]
```

**Options**:
- `--rule` — Rule ID to validate (if omitted, validates all rules)
- `--template` — Path to specific template file

**Exit codes**: 0 = PASS, 1 = filesystem error, 2 = FAIL

#### validate-code

```bash
python3 scripts/fdd.py validate-code [path] [--system <name>] [--verbose] [--output <path>]
```

**Options**:
- `path` — Code file or directory (defaults to codebase entries from artifacts.json)
- `--system` — System name to validate
- `--verbose` — Print full report

**Exit codes**: 0 = PASS, 1 = filesystem error, 2 = FAIL

### Search Commands

#### list-ids

List all FDD IDs from artifacts using template-based parsing.

```bash
python3 scripts/fdd.py list-ids [--artifact <path>] [--pattern <string>] [--regex] [--kind <string>] [--all] [--include-code]
```

**Options**:
- `--artifact` — Specific artifact (if omitted, scans all registered artifacts)
- `--pattern` — Filter IDs by substring or regex
- `--regex` — Treat pattern as regular expression
- `--kind` — Filter by ID kind (requirement, feature, actor, etc.)
- `--all` — Include duplicate IDs
- `--include-code` — Also scan code files for FDD markers

#### list-id-kinds

List ID kinds that exist in artifacts.

```bash
python3 scripts/fdd.py list-id-kinds [--artifact <path>]
```

**Output**: kinds found, counts per kind, mapping to templates

#### get-content

Get content block for a specific FDD ID.

```bash
python3 scripts/fdd.py get-content (--artifact <path> | --code <path>) --id <string> [--inst <string>]
```

**Options**:
- `--artifact` — FDD artifact file (mutually exclusive with --code)
- `--code` — Code file (mutually exclusive with --artifact)
- `--id` — FDD ID to retrieve
- `--inst` — Instruction ID for code blocks

**Exit codes**: 0 = found, 1 = filesystem error, 2 = ID not found

### Traceability Commands

#### where-defined

Find where an FDD ID is defined.

```bash
python3 scripts/fdd.py where-defined --id <id> [--artifact <path>]
```

**Options**:
- `--id` — FDD ID to find definition for
- `--artifact` — Limit search to specific artifact

**Exit codes**: 0 = exactly one definition, 1 = filesystem error, 2 = not found or ambiguous

#### where-used

Find all references to an FDD ID.

```bash
python3 scripts/fdd.py where-used --id <id> [--artifact <path>] [--include-definitions]
```

**Options**:
- `--id` — FDD ID to find references for
- `--artifact` — Limit search to specific artifact
- `--include-definitions` — Include definitions in results

### Adapter & Agent Integration

#### adapter-info

Discover FDD adapter configuration in a project.

```bash
python3 scripts/fdd.py adapter-info [--root <path>] [--fdd-root <path>]
```

**Output** (JSON):
- `status`: FOUND or NOT_FOUND
- `adapter_dir`: Full path to adapter directory
- `project_name`: Project name from adapter
- `specs`: Available spec files
- `rules`: Registered rules packages

#### init

Initialize FDD config and adapter for a project.

```bash
python3 scripts/fdd.py init [--project-root <path>] [--adapter-path <path>] [--yes] [--dry-run] [--force]
```

**Options**:
- `--project-root` — Project root directory
- `--adapter-path` — Adapter directory path (default: FDD-Adapter)
- `--yes` — Non-interactive mode
- `--dry-run` — Compute changes without writing
- `--force` — Overwrite existing files

#### agents

Generate agent-specific workflow proxies and skill outputs.

```bash
python3 scripts/fdd.py agents --agent <name> [--root <path>] [--fdd-root <path>] [--config <path>] [--dry-run]
```

**Supported agents**: windsurf, cursor, claude, copilot

**Options**:
- `--agent` — Agent/IDE key (required)
- `--config` — Path to fdd-agents.json config (default: project root)
- `--dry-run` — Compute changes without writing

#### self-check

Validate example artifacts against their templates (template QA).

```bash
python3 scripts/fdd.py self-check [--rule <id>] [--verbose]
```

**Options**:
- `--rule` — Rule ID to check (if omitted, checks all rules)
- `--verbose` — Print detailed report

## Project Configuration

Optional `.fdd-config.json` at project root:

```json
{
  "fddCorePath": ".fdd",
  "fddAdapterPath": "FDD-Adapter"
}
```

## Output

All commands output JSON to stdout for machine consumption.

## Usage Examples

```bash
# Full validation (all artifacts)
python3 scripts/fdd.py validate

# Validate specific artifact
python3 scripts/fdd.py validate --artifact architecture/PRD.md --verbose

# Validate code traceability
python3 scripts/fdd.py validate-code

# Validate rules and templates
python3 scripts/fdd.py validate-rules

# List all IDs
python3 scripts/fdd.py list-ids

# Find actor IDs
python3 scripts/fdd.py list-ids --pattern "-actor-"

# Find where ID is defined
python3 scripts/fdd.py where-defined --id fdd-myapp-req-auth

# Find all usages of ID
python3 scripts/fdd.py where-used --id fdd-myapp-feature-auth

# Get content for ID
python3 scripts/fdd.py get-content --artifact architecture/PRD.md --id fdd-myapp-actor-admin

# Discover adapter
python3 scripts/fdd.py adapter-info

# Initialize project
python3 scripts/fdd.py init --yes

# Generate agent proxies (workflows + skill)
python3 scripts/fdd.py agents --agent windsurf
```

---

## AI Agent Integration (Opt-In)

FDD provides structured workflows for AI agents to help with design and architecture tasks. FDD is **strictly opt-in** - it will never activate automatically.

### Activation Triggers

Agent SHOULD suggest enabling FDD when detecting these patterns:

**File patterns**:
- User creates/edits: `PRD.md`, `DESIGN.md`, `FEATURES.md`, `ADR/*.md`
- User creates/edits: `**/feature-*/DESIGN.md`, `architecture/**/*.md`
- User opens/edits: `AGENTS.md`, `artifacts.json`, `workflows/*.md`
- Project contains: `.fdd-config.json` (FDD-enabled project)

**FDD terminology** (strong signal):
- User mentions: "fdd", "FDD", "framework for documentation"
- User mentions: "workflow", "artifact", "adapter" in context of documentation/design
- User mentions: "rules package", "template", "checklist" in context of validation
- User mentions: `fdd validate`, `fdd generate`, `fdd-` commands

**Design/architecture patterns** (soft signal):
- User mentions: "design document", "PRD", "product requirements", "architecture"
- User mentions: "feature spec", "technical design", "ADR", "decision record"
- User asks to: "structure the project", "plan the implementation", "document requirements"
- User asks to: "create a feature", "design a feature", "spec out"

**Development patterns** (when in FDD repo):
- User asks to modify: workflows, templates, validation rules
- User asks about: artifact structure, ID format, traceability

### Auto-Detection in FDD Projects

If project contains `.fdd-config.json`:
- FDD is available but still opt-in
- Agent SHOULD mention FDD availability on first relevant interaction
- Example: "This project has FDD configured. Would you like to enable FDD mode?"

### Soft Activation

When trigger detected AND FDD not already enabled:

```
Agent detects: User is creating architecture/DESIGN.md

Agent suggests:
"I notice you're working on architecture documentation.
Would you like to enable FDD mode for structured workflow support?

FDD provides:
- Artifact templates (PRD, DESIGN, FEATURES, ADR, Feature)
- Validation against best practices
- Traceability between design and code

[Enable FDD] [No thanks] [What is FDD?]"
```

**If user agrees**: Follow the "Enable FDD Mode" steps below

**If user declines**: Continue as normal assistant, do not suggest again in this session

### FDD Mode States

| State | Description |
|-------|-------------|
| **OFF** (default) | Normal assistant, no FDD workflows |
| **ON** | FDD workflows available, adapter discovered |

**Enable**: `/fdd` or user agrees to suggestion

**Disable**: `/fdd off` or user explicitly requests

### Enable FDD Mode

When user invokes `/fdd` or agrees to enable FDD:

**Step 1: Discover Adapter**

Run `adapter-info` to discover project adapter.

- If adapter **FOUND**: Open and follow `{adapter_dir}/AGENTS.md`
- If adapter **NOT_FOUND**: Continue with FDD core defaults only

**Step 2: Display Status**

Show adapter status and available workflows:

```
FDD Mode Enabled

Adapter: {FOUND at path | NOT_FOUND}

Available workflows:
| Command                 | Description |
|-------------------------|-------------|
| /fdd-generate           | Create/update artifacts or implement code |
| /fdd-validate           | Validate artifacts or code (deterministic + semantic) |
| /fdd-validate semantic  | Semantic-only validation (skip deterministic gate) |
| /fdd-adapter            | Create/update project adapter |

What would you like to do?
```

### Success Criteria

FDD mode is successfully enabled when ALL of these are true:
- [ ] `adapter-info` command executed and returned valid JSON
- [ ] Adapter status determined (FOUND or NOT_FOUND)
- [ ] If FOUND: `{adapter_dir}/AGENTS.md` read successfully
- [ ] Status output displayed to user (showing adapter status)
- [ ] Available workflows listed

**Verification**: Agent MUST confirm these criteria before proceeding with any workflow.

### Available Workflows (when FDD ON)

| Command | Workflow | Description |
|---------|----------|-------------|
| `/fdd` | (this skill) | Enable FDD mode, show status |
| `/fdd-generate` | `workflows/generate.md` | Create/update artifacts or implement code |
| `/fdd-validate` | `workflows/validate.md` | Validate artifacts or code (deterministic + semantic) |
| `/fdd-validate semantic` | `workflows/validate.md` | Semantic-only validation (skip deterministic gate) |
| `/fdd-adapter` | `workflows/adapter.md` | Create/update project adapter |

### Workflow Navigation

When FDD is ON and user requests a workflow:

```
ALWAYS follow this skill's "Enable FDD Mode" steps WHEN user invokes `/fdd`

ALWAYS open and follow `workflows/generate.md` WHEN user invokes `/fdd-generate` OR user asks to create/update FDD artifacts

ALWAYS open and follow `workflows/validate.md` WHEN user invokes `/fdd-validate` OR user asks to validate FDD artifacts

ALWAYS open and follow `workflows/adapter.md` WHEN user invokes `/fdd-adapter` OR user asks to setup/update FDD adapter
```

### Integration with Project Adapter

See [🛡️ Protocol Guard (MANDATORY)](#️-protocol-guard-mandatory) for the required adapter discovery steps.

### Quick Reference

```bash
# Check if FDD is available in project
python3 scripts/fdd.py adapter-info

# Initialize FDD for new project
python3 scripts/fdd.py init --yes

# Validate all artifacts
python3 scripts/fdd.py validate
```
