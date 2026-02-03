---
name: spider
description: Framework for Documentation and Development - AI agent toolkit. Use when user works with PRD, DESIGN, DECOMPOSITION, ADR, feature specs, architecture documentation, requirements, or mentions Spider/workflow/artifact/adapter/traceability. Provides structured artifact templates, validation, design-to-code traceability, and guided code implementation with traceability markers. Opt-in - suggest enabling when design/architecture activities detected.
---

# Spider Unified Tool

## Goal

Provides comprehensive Spider artifact management and implementation:
1. **Template-Based Validation**: Validates artifacts against Spider templates with marker parsing
2. **Cross-Reference Validation**: Validates references between artifacts (PRD → DESIGN → DECOMPOSITION → feature designs)
3. **Code Traceability**: Codebase scanning to verify implemented items are tagged in code
4. **Search**: ID lookup and traceability across Spider artifacts
5. **Design-to-Code Implementation**: Guided code generation from design specs with `@spider-*` traceability markers

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

Spider does **NOT**:
- Replace code review (validates structure, not logic)
- Manage version control (Git operations are user responsibility)
- Enforce coding style (use linters/formatters for that)
- Provide IDE features (syntax highlighting, autocomplete)

Spider **DOES** support code generation via `/spider-generate` with `KIND=CODE` using `../../weavers/sdlc/codebase/rules.md`.

## Preconditions

1. ALWAYS follow `../SKILLS.md` Toolchain Preflight
2. `python3` is available
3. Target paths exist and are readable

---

## 🛡️ Protocol Guard (MANDATORY)

**BEFORE any Spider workflow action**, agent MUST complete this checklist:

### Protocol Guard Checklist

- [ ] Ran `python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py adapter-info`
- [ ] Checked adapter status (FOUND/NOT_FOUND)
- [ ] If FOUND: Read `{adapter_dir}/AGENTS.md`
- [ ] If FOUND: Parsed WHEN clauses for current target
- [ ] Listed loaded specs in response

**WHAT counts as a “WHEN clause”**:
- A navigation rule line of the form: `ALWAYS open and follow <path> WHEN <condition>`.
- Treat `<condition>` as a gate: only open that dependency when the current task/target matches the described condition (artifact kind/path or codebase).

```
┌─────────────────────────────────────────────────────────┐
│ Spider PROTOCOL CHECK                                      │
│                                                         │
│ 1. Run: python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py│
│         adapter-info                                        │
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
Spider Context:
- Adapter: {path}
- Target: {artifact|codebase}
- Specs loaded: {list paths or "none required"}
```

**If specs NOT loaded but should be**: STOP, load them, THEN proceed.

### Error Recovery

**If adapter-info fails**:
```
⚠ Spider initialization error: {error}
→ Check python3 is available: python3 --version
→ Check Spider path: ls {SPIDER_ROOT}/skills/spider/scripts/
→ Report issue if persists
```

**If AGENTS.md cannot be read**:
```
⚠ Adapter found but AGENTS.md missing/corrupted
→ Run /spider-adapter to regenerate
→ Continue with Spider core defaults
```

### What NOT To Do

❌ **Skip Protocol Guard**: "I already checked earlier" - context may be compacted
❌ **Assume adapter exists**: Run adapter-info every time
❌ **Proceed without listing specs**: Always include Spider Context block
❌ **Guess spec paths**: Read AGENTS.md, don't assume

---

## Agent-Safe Invocation (MANDATORY)

**Canonical variables**:
- `{SPIDER_ROOT}`: Directory that contains `skills/spider/scripts/spider.py`.

**MUST** prefer invoking this tool via the script entrypoint (avoids `cwd`/`PYTHONPATH` issues):
```bash
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py <subcommand> [options]
```

If no `<subcommand>` is provided, the CLI defaults to `validate`.

**Context budget note**: Do not paste this entire file into an always-on system prompt. Load only the relevant section(s) (Protocol Guard + the specific command/workflow) to avoid starving task context.

**Avoid** `python3 -m spider` unless the `spider` package is importable in your environment (installed or `PYTHONPATH` configured). The wrapper entrypoint above is the most reliable.

**Pattern arguments**:
- If a value starts with `-`, **MUST** pass it using `=` form (example: `--pattern=-req-`).

## Command Reference

### Validation Commands

#### validate

Validate Spider artifacts using template-based parsing.

```bash
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py validate [--artifact <path>] [--verbose] [--output <path>]
```

**Options**:
- `--artifact` — Path to specific artifact (if omitted, validates all registered artifacts)
- `--verbose` — Print full validation report (still JSON; includes per-artifact detail)
- `--output` — Write JSON report to file (suppresses stdout)

**Exit codes**: 0 = PASS, 1 = filesystem error, 2 = FAIL

#### validate-weavers

Validate Spider weaver configuration and template files.

```bash
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py validate-weavers [--weaver <id>] [--template <path>] [--verbose]
```

**Options**:
- `--weaver` — Weaver ID to validate (if omitted, validates all weavers)
- `--template` — Path to specific template file

**Exit codes**: 0 = PASS, 1 = filesystem error, 2 = FAIL

#### validate-code

```bash
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py validate-code [path] [--system <name>] [--verbose] [--output <path>]
```

**Options**:
- `path` — Code file or directory (defaults to codebase entries from artifacts.json)
- `--system` — System name to validate
- `--verbose` — Print full report (still JSON)

**Exit codes**: 0 = PASS, 1 = filesystem error, 2 = FAIL

### Search Commands

#### list-ids

List all Spider IDs from artifacts using template-based parsing.

```bash
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py list-ids [--artifact <path>] [--pattern <string>] [--regex] [--kind <string>] [--all] [--include-code]
```

**Options**:
- `--artifact` — Specific artifact (if omitted, scans all registered artifacts)
- `--pattern` — Filter IDs by substring or regex
- `--regex` — Treat pattern as regular expression
- `--kind` — Filter by ID kind (requirement, feature, actor, etc.)
- `--all` — Include duplicate IDs
- `--include-code` — Also scan code files for Spider markers

#### list-id-kinds

List ID kinds that exist in artifacts.

```bash
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py list-id-kinds [--artifact <path>]
```

**Output**: kinds found, counts per kind, mapping to templates

#### get-content

Get content block for a specific Spider ID.

```bash
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py get-content (--artifact <path> | --code <path>) --id <string> [--inst <string>]
```

**Options**:
- `--artifact` — Spider artifact file (mutually exclusive with --code)
- `--code` — Code file (mutually exclusive with --artifact)
- `--id` — Spider ID to retrieve
- `--inst` — Instruction ID for code blocks

**Exit codes**: 0 = found, 1 = filesystem error, 2 = ID not found

### Traceability Commands

#### where-defined

Find where a Spider ID is defined.

```bash
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py where-defined --id <id> [--artifact <path>]
```

**Options**:
- `--id` — Spider ID to find definition for
- `--artifact` — Limit search to specific artifact

**Exit codes**: 0 = exactly one definition, 1 = filesystem error, 2 = not found or ambiguous

#### where-used

Find all references to a Spider ID.

```bash
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py where-used --id <id> [--artifact <path>] [--include-definitions]
```

**Options**:
- `--id` — Spider ID to find references for
- `--artifact` — Limit search to specific artifact
- `--include-definitions` — Include definitions in results

### Adapter & Agent Integration

#### adapter-info

Discover Spider adapter configuration in a project.

```bash
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py adapter-info [--root <path>] [--spider-root <path>]
```

**Output** (JSON):
- `status`: FOUND or NOT_FOUND
- `adapter_dir`: Full path to adapter directory
- `project_name`: Project name from adapter
- `specs`: Available spec files
- `weavers`: Registered weaver packages

#### init

Initialize Spider config and adapter for a project.

```bash
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py init [--project-root <path>] [--adapter-path <path>] [--yes] [--dry-run] [--force]
```

**Options**:
- `--project-root` — Project root directory
- `--adapter-path` — Adapter directory path (default: .spider-adapter)
- `--yes` — Non-interactive mode
- `--dry-run` — Compute changes without writing
- `--force` — Overwrite existing files

#### agents

Generate agent-specific workflow proxies and skill outputs.

```bash
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py agents --agent <name> [--root <path>] [--spider-root <path>] [--config <path>] [--dry-run]
```

**Supported agents**: windsurf, cursor, claude, copilot

**Options**:
- `--agent` — Agent/IDE key (required)
- `--config` — Path to spider-agents.json config (default: project root)
- `--dry-run` — Compute changes without writing

#### self-check

Validate example artifacts against their templates (template QA).

```bash
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py self-check [--weaver <id>] [--verbose]
```

**Options**:
- `--weaver` — Weaver ID to check (if omitted, checks all weavers)
- `--verbose` — Print detailed report (still JSON)

## Project Configuration

Optional `{project-root}/.spider-config.json` at project root:

```json
{
  "spiderCorePath": ".spider",
  "spiderAdapterPath": ".spider-adapter"
}
```

## Output

All commands output JSON to stdout for machine consumption.

Notes:
- Some commands support `--output` to write the JSON report to a file; when used, stdout may be suppressed (by command).
- `--verbose` increases JSON detail (it does not switch to plain text).

## Usage Examples

```bash
# Full validation (all artifacts)
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py validate

# Validate specific artifact
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py validate --artifact architecture/PRD.md --verbose

# Validate code traceability
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py validate-code

# Validate rules and templates
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py validate-weavers

# List all IDs
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py list-ids

# Find actor IDs
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py list-ids --pattern "-actor-"

# Find where ID is defined
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py where-defined --id spd-myapp-req-auth

# Find all usages of ID
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py where-used --id spd-myapp-feature-auth

# Get content for ID
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py get-content --artifact architecture/PRD.md --id spd-myapp-actor-admin

# Discover adapter
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py adapter-info

# Initialize project
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py init --yes

# Generate agent proxies (workflows + skill)
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py agents --agent windsurf
```

---

## AI Agent Integration (Opt-In)

Spider provides structured workflows for AI agents to help with design and architecture tasks. Spider is **strictly opt-in** - it will never activate automatically.

### Activation Triggers

Agent SHOULD suggest enabling Spider when detecting these patterns:

**File patterns**:
- User creates/edits: `PRD.md`, `DESIGN.md`, `DECOMPOSITION.md`, `ADR/*.md`
- User creates/edits: `**/feature-*/DESIGN.md`, `architecture/**/*.md`
- User opens/edits: `AGENTS.md`, `artifacts.json`, `workflows/*.md`
- Project contains: `{project-root}/.spider-config.json` (Spider-enabled project)

**Spider terminology** (strong signal):
- User mentions: "spider", "Spider", "framework for documentation"
- User mentions: "workflow", "artifact", "adapter" in context of documentation/design
- User mentions: "weaver package", "template", "checklist" in context of validation
- User mentions: `spider validate`, `spider generate`, `spd-` commands

**Design/architecture patterns** (soft signal):
- User mentions: "design document", "PRD", "product requirements", "architecture"
- User mentions: "feature spec", "technical design", "ADR", "decision record"
- User asks to: "structure the project", "plan the implementation", "document requirements"
- User asks to: "create a feature", "design a feature", "spec out"

**Development patterns** (when in Spider repo):
- User asks to modify: workflows, templates, validation rules
- User asks about: artifact structure, ID format, traceability

### Auto-Detection in Spider Projects

If project contains `{project-root}/.spider-config.json`:
- Spider is available but still opt-in
- Agent SHOULD mention Spider availability on first relevant interaction
- Example: "This project has Spider configured. Would you like to enable Spider mode?"

### Soft Activation

When trigger detected AND Spider not already enabled:

```
Agent detects: User is creating architecture/DESIGN.md

Agent suggests:
"I notice you're working on architecture documentation.
Would you like to enable Spider mode for structured workflow support?

Spider provides:
- Artifact templates (PRD, DESIGN, DECOMPOSITION, ADR, Feature)
- Validation against best practices
- Traceability between design and code

[Enable Spider] [No thanks] [What is Spider?]"
```

**If user agrees**: Follow the "Enable Spider Mode" steps below

**If user declines**: Continue as normal assistant, do not suggest again in this session

### Spider Mode States

| State | Description |
|-------|-------------|
| **OFF** (default) | Normal assistant, no Spider workflows |
| **ON** | Spider workflows available, adapter discovered |

**Enable**: `/spider` or user agrees to suggestion

**Disable**: `/spider off` or user explicitly requests

### Enable Spider Mode

When user invokes `/spider` or agrees to enable Spider:

**Step 1: Discover Adapter**

Run `adapter-info` to discover project adapter.

- If adapter **FOUND**: Open and follow `{adapter_dir}/AGENTS.md`
- If adapter **NOT_FOUND**: Continue with Spider core defaults only

**Step 2: Display Status**

Show adapter status and available workflows:

```
Spider Mode Enabled

Adapter: {FOUND at path | NOT_FOUND}

Available workflows:
| Command                 | Description |
|-------------------------|-------------|
| /spider-generate           | Create/update artifacts or implement code |
| /spider-validate           | Validate artifacts or code (deterministic + semantic) |
| /spider-validate semantic  | Semantic-only validation (skip deterministic gate) |
| /spider-adapter            | Create/update project adapter |

What would you like to do?
```

### Success Criteria

Spider mode is successfully enabled when ALL of these are true:
- [ ] `adapter-info` command executed and returned valid JSON
- [ ] Adapter status determined (FOUND or NOT_FOUND)
- [ ] If FOUND: `{adapter_dir}/AGENTS.md` read successfully
- [ ] Status output displayed to user (showing adapter status)
- [ ] Available workflows listed

**Verification**: Agent MUST confirm these criteria before proceeding with any workflow.

### Available Workflows (when Spider ON)

| Command | Workflow | Description |
|---------|----------|-------------|
| `/spider` | (this skill) | Enable Spider mode, show status |
| `/spider-generate` | `../../workflows/generate.md` | Create/update artifacts or implement code |
| `/spider-validate` | `../../workflows/validate.md` | Validate artifacts or code (deterministic + semantic) |
| `/spider-validate semantic` | `../../workflows/validate.md` | Semantic-only validation (skip deterministic gate) |
| `/spider-adapter` | `../../workflows/adapter.md` | Create/update project adapter |

### Tracked Files Detection

**Before processing any modification request**, agent MUST check if target files/folders are tracked in `artifacts.json`:

```
1. Run: python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py adapter-info
2. Read: {adapter_dir}/artifacts.json
3. Check if request target matches:
   - artifacts[].path (exact match or parent directory)
   - codebase[].path (exact match or subdirectory)
4. If MATCH → trigger generate workflow
```

**Matching logic**:
- Artifact paths: exact match (e.g., "architecture/PRD.md")
- Codebase paths: prefix match (e.g., "skills/spider/scripts/spider/cli.py" matches codebase path "skills/spider/scripts/spider")

### Workflow Navigation

When Spider is ON and user requests a workflow:

```
ALWAYS follow this skill's "Enable Spider Mode" steps WHEN user invokes `/spider`

ALWAYS open and follow `../../workflows/generate.md` WHEN ANY of:
  - user invokes `/spider-generate`
  - user asks to create/update Spider artifacts
  - user asks to CREATE files/folders that are tracked in artifacts.json
  - user asks to EDIT files/folders that are tracked in artifacts.json
  - user asks to FIX files/folders that are tracked in artifacts.json
  - user asks to ADD content to files/folders that are tracked in artifacts.json
  - user asks to DELETE content from files/folders that are tracked in artifacts.json
  - user asks to REFACTOR files/folders that are tracked in artifacts.json
  - user asks to IMPLEMENT features in codebase tracked in artifacts.json

ALWAYS open and follow `../../workflows/validate.md` WHEN user invokes `/spider-validate` OR user asks to validate Spider artifacts

ALWAYS open and follow `../../workflows/adapter.md` WHEN user invokes `/spider-adapter` OR user asks to setup/update Spider adapter
```

### Modification Detection Keywords

Agent SHOULD trigger generate workflow when user request contains these action words targeting tracked files:

| Action Category | Keywords |
|-----------------|----------|
| **Create** | create, write, add file, new, generate, make |
| **Edit** | edit, modify, change, update, alter |
| **Fix** | fix, repair, correct, patch, resolve, debug |
| **Add** | add, insert, append, include, extend |
| **Delete** | delete, remove, clear, drop, clean up |
| **Refactor** | refactor, rewrite, restructure, reorganize, improve |
| **Implement** | implement, code, develop, build |

### Detection Examples

**Example 1: Direct artifact reference**
```
User: "Update the PRD with new requirements"
Agent:
1. Detects keyword "update" → modification action
2. Identifies target "PRD" → maps to artifacts[].kind="PRD"
3. Finds match: artifacts.json contains {path: "architecture/PRD.md", kind: "PRD"}
4. → Triggers generate workflow
```

**Example 2: Code file in tracked codebase**
```
User: "Fix the bug in cli.py"
Agent:
1. Detects keyword "fix" → modification action
2. Searches for "cli.py" → finds "skills/spider/scripts/spider/cli.py"
3. Checks against codebase[].path → matches "skills/spider/scripts/spider"
4. → Triggers generate workflow
```

**Example 3: New file in tracked directory**
```
User: "Create a new utility function in spider/utils"
Agent:
1. Detects keyword "create" → modification action
2. Target path "spider/utils" → resolves to "skills/spider/scripts/spider/utils"
3. Checks against codebase[].path → matches "skills/spider/scripts/spider"
4. → Triggers generate workflow
```

**Example 4: Untracked file (NO trigger)**
```
User: "Edit the README.md"
Agent:
1. Detects keyword "edit" → modification action
2. Target "README.md" → project root README
3. Checks artifacts.json → NOT in artifacts[] or codebase[]
4. → Does NOT trigger generate workflow (proceeds as normal assistant)
```

### Integration with Project Adapter

See [🛡️ Protocol Guard (MANDATORY)](#️-protocol-guard-mandatory) for the required adapter discovery steps.

### Quick Reference

```bash
# Check if Spider is available in project
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py adapter-info

# Initialize Spider for new project
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py init --yes

# Validate all artifacts
python3 {SPIDER_ROOT}/skills/spider/scripts/spider.py validate
```
