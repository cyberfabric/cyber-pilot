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
- Scope: Applies to all projects

**Level 2: Adapter AGENTS.md**
- Location: `{adapter-directory}/AGENTS.md` (e.g., `.adapter/AGENTS.md`)
- Purpose: Project-specific conventions
- Mechanism: **Extends** core AGENTS.md

### WHEN Clause Format

**Pattern**: `ALWAYS open and follow {file} WHEN {condition}`

**Examples**:
```markdown
ALWAYS open and follow `requirements/core.md` WHEN editing this file

ALWAYS open and follow `specs/tech-stack.md` WHEN executing workflows: design.md, feature-change-implement.md

ALWAYS open and follow `specs/conventions.md` WHEN executing workflows: adapter-validate.md, feature-code-validate.md
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

**ALWAYS open and follow**: `../requirements/core.md` WHEN editing this file

ALWAYS open and follow `../requirements/workflow-execution.md` WHEN executing this workflow

## Purpose
{What this workflow does}

## Requirements
**ALWAYS open and follow**: `../requirements/{artifact}-structure.md`

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
**Layer 1**: Business context (actors, capabilities)
**Layer 2**: Overall design (architecture, domain model)
**Layer 3**: Features (feature list)
**Layer 4**: Feature designs (detailed specs)
**Layer 5**: Changes (implementation plans)
**Layer 6**: Code (implementation)

**Rule**: Each layer validated before proceeding to next

### Feature Directory Pattern

```
architecture/features/
├── FEATURES.md              # Feature manifest
└── feature-{slug}/          # One directory per feature
    ├── DESIGN.md           # Feature specification
    ├── CHANGES.md          # Current implementation plan
    └── archive/            # Historical changes
        └── YYYY-MM-DD-CHANGES.md
```

---

## Source

**Discovered from**:
- `AGENTS.md` - WHEN clause patterns
- `requirements/core.md` - FDD principles
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
