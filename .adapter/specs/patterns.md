# Patterns

**Version**: 1.0  
**Last Updated**: 2025-01-17  
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

**Pattern**: `ALWAYS open and follow {file} WHEN {condition}`

**Examples**:
```markdown
ALWAYS open and follow `specs/tech-stack.md` WHEN executing workflows: design.md, code.md

ALWAYS open and follow `specs/conventions.md` WHEN executing workflows: adapter-validate.md, code-validate.md
```

**Rules**:
- Start with `ALWAYS open and follow`
- Reference specific file path
- Use `WHEN` clause with specific conditions
- Conditions list specific workflows (not generic phrases)

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
**ALWAYS open and follow**: `../requirements/{artifact}-content.md`

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
python3 skills/fdd/scripts/fdd.py validate --artifact {code-root}
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
- Each navigation rule MUST use a WHEN clause that is ONLY a list of FDD workflows
- Canonical form:
  - `ALWAYS open and follow {spec-file} WHEN executing workflows: {workflow1.md}, {workflow2.md}, ...`
- The workflow names MUST match files under `/workflows/`

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
- `workflows/*.md` - Workflow structure
- `README.md` - FDD overview

---

## Validation Checklist

Agent MUST verify before implementation:
- [ ] WHEN clauses list specific workflows (not generic conditions)
- [ ] FDL uses bold keywords and numbered lists
- [ ] Code tags use qualified ID format
- [ ] Workflows follow standard structure
- [ ] Validation runs deterministic gate first

**Self-test**:
- [ ] Did I check all criteria?
- [ ] Are pattern examples from actual FDD files?
- [ ] Do patterns match current implementation?
