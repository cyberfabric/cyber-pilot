# Greenfield Guide

Use this guide when you are starting a new project from scratch.

All prompts work through the `cypilot` skill — enable it with `cypilot on` and use natural language prompts.

## Goal

Create a validated baseline (PRD + architecture) before writing code.

## What You Will Produce

Cypilot artifacts registered in `.cypilot-adapter/artifacts.toml` ([taxonomy](TAXONOMY.md)):

| Artifact | Default Location |
|----------|------------------|
| PRD | `architecture/PRD.md` |
| ADR | `architecture/ADR/*.md` |
| DESIGN | `architecture/DESIGN.md` |
| DECOMPOSITION | `architecture/DECOMPOSITION.md` |
| FEATURE | `architecture/features/{slug}.md` |

**Customizing artifact locations:**

| Prompt | What happens |
|--------|--------------|
| `cypilot set artifacts_dir to docs/design/` | Changes default base directory for new artifacts |
| `cypilot move PRD to docs/requirements/PRD.md` | Moves artifact to new location |
| `cypilot register PRD at docs/requirements/product-requirements.md` | Registers existing file as PRD artifact |
| `cypilot show artifact locations` | Displays current paths from `artifacts.toml` |

You can also edit `.cypilot-adapter/artifacts.toml` directly:
- `artifacts_dir` — Default base directory for new artifacts (default: `architecture`)
- Subdirectories for FEATUREs (`features/`) and ADRs (`ADR/`) are defined by the kit
- Artifact paths in `artifacts` array are FULL paths — you can place artifacts anywhere

## How to Provide Context

Each prompt can include additional context. Recommended:

- Current state (what exists, what is missing)
- Links/paths to existing docs (README, features, diagrams)
- Constraints (security, compliance, performance)
- Non-goals and out-of-scope items

**Example format:**
```
cypilot make DESIGN for taskman
Context:
- Repo: taskman - task management CLI tool
- Existing docs: README.md
- Constraints: SQLite storage, offline-first
```

The agent will read inputs, ask targeted questions, propose answers, and produce artifacts.

---

## Workflow Sequence

### 1. PRD

**Create**

| Prompt | What happens |
|--------|--------------|
| `cypilot make PRD` | Creates PRD interactively |
| `cypilot make PRD for taskman` | Creates PRD with context |
| `cypilot draft PRD from README` | Extracts initial PRD from README |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot update PRD` | Updates PRD interactively |
| `cypilot extend PRD with task labels` | Adds capability to existing PRD |
| `cypilot update PRD actors` | Updates actors section |
| `cypilot update PRD requirements` | Updates requirements section |

**Provide context:** product vision, target users, key capabilities, existing PRD/BRD.

**Example:**
```
cypilot make PRD for taskman
Context:
- Product: taskman - CLI task management tool
- Users: developers, solo users
- Key capabilities: create tasks, list tasks, mark done, due dates, priorities
- Storage: SQLite local database
```

### 2. Validate PRD

| Prompt | What happens |
|--------|--------------|
| `cypilot validate PRD` | Full validation (300+ criteria) |
| `cypilot validate PRD semantic` | Semantic only (content quality) |
| `cypilot validate PRD structural` | Structural only (format, IDs) |
| `cypilot validate PRD quick` | Fast check (critical issues) |

### 3. ADR + DESIGN

**Create DESIGN**

| Prompt | What happens |
|--------|--------------|
| `cypilot make DESIGN` | Creates DESIGN interactively |
| `cypilot make DESIGN from PRD` | Transforms PRD into architecture |

**Update DESIGN**

| Prompt | What happens |
|--------|--------------|
| `cypilot update DESIGN` | Updates DESIGN interactively |
| `cypilot extend DESIGN with sync-service` | Adds component to DESIGN |
| `cypilot update DESIGN components` | Updates components section |
| `cypilot update DESIGN data model` | Updates data model section |

**Create ADR**

| Prompt | What happens |
|--------|--------------|
| `cypilot make ADR for SQLite` | Creates ADR for technology choice |
| `cypilot make ADR for CLI vs TUI` | Creates ADR comparing approaches |

**Update ADR**

| Prompt | What happens |
|--------|--------------|
| `cypilot update ADR 0001` | Updates specific ADR |
| `cypilot supersede ADR 0001 with 0002` | Creates new ADR superseding old |

**Provide context:** architecture constraints, existing domain model, API contracts.

**Example:**
```
cypilot make DESIGN for taskman
Context:
- Tech: CLI tool, SQLite storage
- Constraints: offline-first, single binary, cross-platform
- Language: Go or Rust
```

### 4. Validate DESIGN + ADR

| Prompt | What happens |
|--------|--------------|
| `cypilot validate DESIGN` | Full validation (380+ criteria) |
| `cypilot validate DESIGN semantic` | Semantic only (consistency) |
| `cypilot validate DESIGN structural` | Structural only (format) |
| `cypilot validate DESIGN refs` | Cross-references to PRD |
| `cypilot validate ADR` | Validates all ADRs |
| `cypilot validate ADR 0001` | Validates specific ADR |
| `cypilot validate ADR semantic` | Semantic only (rationale quality) |

### 5. DECOMPOSITION

**Create**

| Prompt | What happens |
|--------|--------------|
| `cypilot decompose` | Creates DECOMPOSITION interactively |
| `cypilot decompose into features` | Creates ordered feature list |
| `cypilot decompose by capability` | Groups by business capability |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot add feature labels` | Adds new feature entry |
| `cypilot update feature task-crud status` | Updates feature status |
| `cypilot update feature task-crud priority` | Updates feature priority |
| `cypilot reorder features` | Changes feature order |

**Provide context:** feature boundaries, grouping preferences.

**Example:**
```
cypilot decompose taskman into features
Context:
- Split by capability: task-crud, task-list, task-search, labels, sync
```

### 6. Validate DECOMPOSITION

| Prompt | What happens |
|--------|--------------|
| `cypilot validate DECOMPOSITION` | Full validation (130+ criteria) |
| `cypilot validate DECOMPOSITION semantic` | Semantic only (coverage) |
| `cypilot validate DECOMPOSITION structural` | Structural only (format) |
| `cypilot validate DECOMPOSITION refs` | Cross-references to DESIGN |

### 7. FEATURE

**Create**

| Prompt | What happens |
|--------|--------------|
| `cypilot make FEATURE for task-crud` | Creates feature design |
| `cypilot make FEATURE for task-list` | Creates detailed feature design |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot update FEATURE task-crud` | Updates feature design |
| `cypilot extend FEATURE task-crud with bulk-delete` | Adds scenario to feature |
| `cypilot update FEATURE task-crud flows` | Updates flows section |
| `cypilot update FEATURE task-crud algorithms` | Updates algorithms section |

**Provide context:** feature slug, acceptance criteria, edge cases, error handling.

**Example:**
```
cypilot make FEATURE for task-crud
Context:
- Include scenarios: create, update, delete, bulk operations
- Edge cases: duplicate titles, invalid dates, missing required fields
```

### 8. Validate FEATURE

| Prompt | What happens |
|--------|--------------|
| `cypilot validate FEATURE task-crud` | Full validation (380+ criteria) |
| `cypilot validate FEATURE task-crud semantic` | Semantic only (flows, edge cases) |
| `cypilot validate FEATURE task-crud structural` | Structural only (CDSL, IDs) |
| `cypilot validate FEATURE task-crud refs` | Cross-references to DESIGN |

### 9. CODE

**Implement from scratch**

| Prompt | What happens |
|--------|--------------|
| `cypilot implement task-crud` | Generates code from FEATURE |
| `cypilot implement feature task-crud` | Same, explicit feature keyword |
| `cypilot implement task-crud step by step` | Implements with user confirmation at each step |
| `cypilot implement task-crud tests first` | Generates tests first, then implementation |

**Implement specific parts**

| Prompt | What happens |
|--------|--------------|
| `cypilot implement task-crud flow create` | Implements specific flow only |
| `cypilot implement task-crud algorithm validate` | Implements specific algorithm only |
| `cypilot implement task-crud api` | Implements API layer only |
| `cypilot implement task-crud data layer` | Implements data/repository layer only |
| `cypilot implement task-crud tests` | Generates tests only |

**Continue / update**

| Prompt | What happens |
|--------|--------------|
| `cypilot continue implementing task-crud` | Continues partial implementation |
| `cypilot sync code with FEATURE task-crud` | Updates code to match FEATURE changes |
| `cypilot implement task-crud remaining` | Implements only unimplemented parts |
| `cypilot refactor task-crud` | Refactors implementation keeping markers |

**Add markers to existing code**

| Prompt | What happens |
|--------|--------------|
| `cypilot add markers to cmd/task.go` | Adds `@cpt-*` markers to existing code |
| `cypilot add markers for task-crud` | Adds markers matching FEATURE |
| `cypilot fix markers in cmd/` | Fixes incorrect/incomplete markers |

**Provide context:** feature slug, code paths if non-standard.

### 10. Validate Code

**Full validation**

| Prompt | What happens |
|--------|--------------|
| `cypilot validate code` | Validates all code markers |
| `cypilot validate code for task-crud` | Validates specific feature |
| `cypilot validate code in cmd/` | Validates code in specific path |

**Coverage**

| Prompt | What happens |
|--------|--------------|
| `cypilot validate code coverage` | Reports implementation coverage % |
| `cypilot validate code coverage for task-crud` | Coverage for specific feature |
| `cypilot show uncovered flows` | Lists flows without implementation |
| `cypilot show uncovered algorithms` | Lists algorithms without implementation |

**Traceability**

| Prompt | What happens |
|--------|--------------|
| `cypilot validate code orphans` | Finds markers referencing non-existent IDs |
| `cypilot validate code refs` | Validates all marker references |
| `cypilot validate code markers` | Checks marker format correctness |
| `cypilot list code markers` | Lists all markers in codebase |
| `cypilot list code markers for task-crud` | Lists markers for specific feature |

**Consistency**

| Prompt | What happens |
|--------|--------------|
| `cypilot compare code to FEATURE task-crud` | Shows drift between code and feature |
| `cypilot validate code consistency` | Checks code matches FEATURE |
| `cypilot find missing implementations` | Lists FEATURE elements without code |

---

## Iteration Rules

- If a change impacts behavior, update the relevant design first (DESIGN or FEATURE)
- Re-run validation for the modified artifact before continuing
- If code contradicts design, update design first, then re-validate

## Quick Reference

| Step | Generate | Validate |
|------|----------|----------|
| 1 | `cypilot make PRD for taskman` | `cypilot validate PRD` |
| 2 | `cypilot make DESIGN` | `cypilot validate DESIGN` |
| 3 | `cypilot make ADR for SQLite` | `cypilot validate ADR` |
| 4 | `cypilot decompose` | `cypilot validate DECOMPOSITION` |
| 5 | `cypilot make FEATURE for task-crud` | `cypilot validate FEATURE task-crud` |
| 6 | `cypilot implement task-crud` | `cypilot validate code for task-crud` |

**Validation modes** (append to any `validate` command):
- `semantic` — content quality, completeness, clarity
- `structural` — format, IDs, template compliance
- `refs` — cross-references to other artifacts
- `quick` — critical issues only (fast)
