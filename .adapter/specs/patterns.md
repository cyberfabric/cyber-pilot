# Patterns

**Version**: 2.0
**Last Updated**: 2026-02-01  
**Purpose**: Define architectural patterns and conventions used in FDD

---

## AGENTS.md Pattern

### Core Principle

**Single source of truth for AI agents** - All methodology, workflows, and conventions in one discoverable file.

### Two-Level Hierarchy

**Level 1: Core AGENTS.md**
- Location: `FDD/AGENTS.md`
- Purpose: Universal FDD methodology
- Scope: Applies only when FDD is enabled (opt-in)

**Level 2: Adapter AGENTS.md**
- Location: `{adapter-directory}/AGENTS.md` (e.g., `.adapter/AGENTS.md`)
- Purpose: Project-specific conventions
- Mechanism: **Extends** core AGENTS.md

### WHEN Clause Format

**Three types of WHEN clauses**:

1. **Rules-based** (for adapter navigation):
```markdown
ALWAYS open and follow `specs/tech-stack.md` WHEN FDD follows rules `fdd-sdlc` for artifact kinds: DESIGN, ADR OR codebase

ALWAYS open and follow `specs/conventions.md` WHEN FDD follows rules `fdd-sdlc` for codebase
```

2. **File-context** (for file-specific guidance):
```markdown
ALWAYS open and follow `artifacts.json` WHEN working with artifacts.json
```

3. **Pattern-based** (for recognizing patterns):
```markdown
ALWAYS do X WHEN you see {pattern}
```

**Rules**:
- Start with `ALWAYS open and follow`, `ALWAYS do`, or `ALWAYS execute`
- Reference specific file path
- Use rules-based format for adapter specs (reference rule ID and artifact kinds)
- Valid artifact kinds: PRD, DESIGN, FEATURES, ADR, FEATURE
- Use `OR codebase` when spec applies to code validation/generation

### Extends Mechanism

**Pattern**:
```markdown
# FDD Adapter: {Project Name}

**Extends**: `../AGENTS.md`
```

**Purpose**: Inherit core methodology without duplication

**Benefits**:
- No content duplication
- Core updates propagate automatically
- Project customizations stay isolated

---

## Workflow Pattern

### Operation vs Validation

**Operation Workflows**:
- Interactive (ask questions)
- Create/modify artifacts
- Wait for user confirmation
- Run validation after creation

**Validation Workflows**:
- Fully automated
- Read-only (no file creation)
- Output to chat only
- Use deterministic validators

### Workflow File Structure

```markdown
# {Workflow Name}

**Type**: Operation | Validation
**Role**: Any | Architect | Developer
**Artifact**: {Target artifact path}

---

ALWAYS open and follow `../requirements/execution-protocol.md` WHEN executing this workflow

## Purpose
{What this workflow does}

## Requirements
**Load rules package**: `../rules/sdlc/artifacts/{ARTIFACT_KIND}/`

## Prerequisites
- [ ] Prerequisite 1
- [ ] Prerequisite 2

## Steps
### 1. {Step Name}
{Step description}

### 2. {Step Name}
{Step description}

## Validation
{How to validate results}

## Next Steps
{Recommended next workflow}
```

---

## FDL (Flow Description Language)

### Purpose

**Plain English algorithm description** - Reviewable by non-programmers, executable by developers.

### Syntax

**Numbered list in Markdown**:
```markdown
1. **Actor** performs action
2. **System** validates input
3. **IF** condition is true:
   - [ ] Inst-label: **System** processes data
   - [ ] Inst-label: **System** stores result
4. **ELSE**:
   - [ ] Inst-label: **System** returns error
5. **System** sends response
```

**Keywords** (always bold):
- **IF**, **ELSE**, **WHILE**, **FOR EACH**
- **AND**, **OR**, **NOT**
- **MUST**, **REQUIRED**, **OPTIONAL**

**Instruction markers**:
- `- [ ]` for unimplemented steps
- `- [x]` for implemented steps  
- `Inst-{label}:` for traceability

### Not Allowed in FDL

❌ **Code syntax**:
```markdown
<!-- WRONG -->
if user.authenticated:
    session.create()
```

✅ **Plain English**:
```markdown
<!-- CORRECT -->
3. **IF** user is authenticated:
   - [ ] Inst-create-session: **System** creates session
```

---

## Validation Pattern

### Deterministic Gate

**Principle**: Fail fast with automated validators before manual review

**Pattern**:
```markdown
1. Run `fdd validate --artifact {path}` (deterministic)
2. If FAIL → Stop, report issues
3. If PASS → Continue to manual validation
```

**Benefits**:
- Catches structural errors immediately
- Saves time on manual review
- Provides consistent validation

### Validation Score System

**100-point scoring**:
- Structure (20-30 points)
- Completeness (20-30 points)
- Clarity (15-20 points)
- Integration (20-30 points)

**Pass thresholds**:
- Operation workflows: ≥90/100
- Validation workflows: 100/100
- Adapter specs: ≥80/100

---

## Traceability Pattern

### Design → Code Traceability

**Code tags**:
```python
# @fdd-flow:fdd-myapp-flow-login:ph-1
def handle_login(username, password):
    # @fdd-flow:fdd-myapp-flow-login:ph-1:inst-validate
    if not validate_credentials(username, password):
        return error("Invalid credentials")
    # @fdd-flow-end
    
    # @fdd-flow:fdd-myapp-flow-login:ph-2:inst-create-session
    session = create_session(username)
    # @fdd-flow-end
    return success(session)
```

**Validation**:
```bash
python3 skills/fdd/scripts/fdd/cli.py validate --artifact {code-root}
```

**Expected**: For each `[x]` marked item in DESIGN.md, corresponding `@fdd-*` tag exists in code.

---

## File Organization Pattern

### Layered Structure

**Layer 0**: Adapter (tech stack, conventions)
**Layer 1**: PRD (actors, capabilities)
**Layer 2**: Overall design (architecture, domain model)
**Layer 3**: Features (feature list)
**Layer 4**: Feature designs (detailed specs)
**Layer 5**: Code (implementation)

**Rule**: Each layer validated before proceeding to next

### Feature Directory Pattern

```
architecture/features/
├── FEATURES.md              # Feature manifest
└── feature-{slug}/          # One directory per feature
    ├── DESIGN.md           # Feature specification
    └── src/                # Implementation
```

---

## Reverse Engineering Pattern

### Purpose

**Technology-agnostic project analysis** - Systematic methodology for understanding any software project before generating artifacts or code.

### When to Use

- Adapter workflow: Project scanning (Phase 1)
- Generate workflow: When working with existing codebase
- Brownfield projects: Understanding before modification

### Analysis Layers

**9-layer progressive analysis** (each builds on previous):

| Layer | Goal | Adapter Use |
|-------|------|-------------|
| 1. Surface Reconnaissance | Repository structure, languages, docs | ✅ Phase 1 |
| 2. Entry Point Analysis | Main entry points, bootstrap sequence | ✅ Phase 1 |
| 3. Structural Decomposition | Architecture pattern, module boundaries | ✅ Phase 1 |
| 4. Data Flow Tracing | How data moves through system | Generate |
| 5. Dependency Mapping | Internal/external dependencies | Generate |
| 6. State Management | State creation, modification, persistence | Generate |
| 7. Integration Boundaries | External touchpoints | Generate |
| 8. Pattern Recognition | Conventions, idioms | Generate |
| 9. Knowledge Synthesis | Consolidate findings | Generate |

### Integration with Workflows

**Adapter workflow** (`workflows/adapter.md`):
```markdown
ALWAYS open and follow `../requirements/reverse-engineering.md` WHEN scanning project structure (Phase 1)
```

Uses Layers 1-3 for:
- Directory structure analysis
- Tech stack detection
- Hierarchy detection

**Generate workflow** (`workflows/generate.md`):
```markdown
ALWAYS open and follow `../requirements/reverse-engineering.md` WHEN user requests to analyze codebase, search in code, search in project documentation, or generate artifacts or code based on existing project structure
```

Uses all layers when:
- Analyzing existing codebase
- Searching in code/documentation
- Generating from existing project

### Prerequisite Check

Before generating artifacts/code for existing projects:

1. Check if adapter has project analysis (`specs/` populated)
2. If no analysis → suggest `/fdd-adapter --rescan` first
3. After scan → continue with original task

### Reference

**Full specification**: `requirements/reverse-engineering.md`

---

## FDD Framework Requirements (Migrated)

### Source of Truth

When requirements in this spec conflict with `architecture/features/feature-init-structure/DESIGN.md`, follow `architecture/features/feature-init-structure/DESIGN.md`.

### AGENTS.md Requirements

**AGENTS.md MUST contain ONLY**:
- Navigation instructions in one of these formats:
  - `ALWAYS open and follow {file} WHEN {trigger}`
  - `ALWAYS execute {workflow} WHEN {trigger}`
  - `ALWAYS do {action} WHEN {trigger}`
- No duplicated requirements/spec content from referenced files

**Exception (core FDD only)**:
- `AGENTS.md` MAY include mandatory instruction semantics and enforcement sections

**Adapter AGENTS.md WHEN rule (mandatory)**:
- Each navigation rule MUST use rules-based WHEN clause format
- Canonical form:
  - `ALWAYS open and follow {spec-file} WHEN FDD follows rules `{rule-id}` for artifact kinds: {KIND1}, {KIND2} [OR codebase]`
- Valid artifact kinds: PRD, DESIGN, FEATURES, ADR, FEATURE
- Use `OR codebase` when spec applies to code validation/generation

### Workflow File Requirements

**Workflow files MUST have**:
1. YAML frontmatter
2. `# {Workflow Name}` title
3. Prerequisites section with `- [ ]` checkboxes and validation method
4. Steps section with sequentially numbered `### {n}. {Action Verb} {Object}` steps
5. Next Steps section with explicit success/failure paths and exact workflow filenames

**Workflow files MUST NOT**:
- Use OS-specific commands
- Omit validation method for prerequisites

### Operation Workflow Content Requirements

Operation workflows MUST:
- Ask questions with proposed answers
- Include user confirmation points before file creation/modification
- Include a Validation section that runs the relevant validation workflow

Operation workflows MUST NOT:
- Create or modify files without user confirmation
- Ask open-ended questions without proposals

### Validation Workflow Content Requirements

Validation workflows MUST:
- Be fully automated (no user interaction)
- Read the relevant requirements/specs and validate the artifact
- Calculate a deterministic score and print to chat only

Validation workflows MUST NOT:
- Create or modify files
- Invent new validation criteria

---

## Source

**Discovered from**:
- `AGENTS.md` - WHEN clause patterns
- `.adapter/specs/conventions.md` - FDD principles
- `requirements/FDL.md` - FDL specification
- `requirements/reverse-engineering.md` - RE methodology
- `workflows/*.md` - Workflow structure
- `README.md` - FDD overview

---

## Validation Checklist

Agent MUST verify before implementation:
- [ ] WHEN clauses use rules-based format (reference rule ID and artifact kinds)
- [ ] FDL uses bold keywords and numbered lists
- [ ] Code tags use qualified ID format
- [ ] Workflows follow standard structure
- [ ] Validation runs deterministic gate first
- [ ] RE methodology used for brownfield projects (Layers 1-3 minimum)

**Self-test**:
- [ ] Did I check all criteria?
- [ ] Are pattern examples from actual FDD files?
- [ ] Do patterns match current implementation?
