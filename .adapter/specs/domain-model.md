# Domain Model

**Version**: 1.0  
**Last Updated**: 2025-01-17  
**Purpose**: Define FDD artifact structures and ID formats

---

## Overview

FDD uses **Markdown-based artifacts** for design documentation, not code-level type definitions.

**Key principle**: Design is described in plain language, validated against structure requirements, not compiled into types.

---

## FDD Artifacts

### Artifact Types

| Artifact | Location | Purpose |
|----------|----------|---------|
| `BUSINESS.md` | `architecture/` | Business context, actors, capabilities |
| `DESIGN.md` | `architecture/` | Overall system design |
| `ADR.md` | `architecture/` | Architecture Decision Records |
| `FEATURES.md` | `architecture/` | Feature manifest |
| `DESIGN.md` | `architecture/features/feature-{slug}/` | Feature design |
| `CHANGES.md` | `architecture/features/feature-{slug}/` | Implementation changes |

### Validation Requirements

Each artifact type has structure requirements in:
```
requirements/
├── business-context-structure.md
├── overall-design-structure.md
├── adr-structure.md
├── features-manifest-structure.md
├── feature-design-structure.md
└── feature-changes-structure.md
```

---

## ID Format System

### FDD ID Pattern

**Format**: `` `fdd-{project}-{kind}-{name}` ``

**Rules**:
- Always wrapped in backticks in Markdown
- Lowercase kebab-case
- Unique within artifact type
- Descriptive name (not sequential numbers)

### ID Kinds

**Actors**: `fdd-{project}-actor-{name}`
```markdown
**ID**: `fdd-myapp-actor-admin`
```

**Capabilities**: `fdd-{project}-capability-{name}`
```markdown
**ID**: `fdd-myapp-capability-user-management`
```

**Use Cases**: `fdd-{project}-usecase-{name}`
```markdown
**ID**: `fdd-myapp-usecase-login`
```

**Requirements**: `fdd-{project}-req-{name}`
```markdown
**ID**: `fdd-myapp-req-user-auth`
```

**Features**: `fdd-{project}-feature-{name}`
```markdown
**ID**: `fdd-myapp-feature-authentication`
```

**Flows**: `fdd-{project}-feature-{feature}-flow-{name}`
```markdown
**ID**: `fdd-myapp-feature-auth-flow-login`
```

**Algorithms**: `fdd-{project}-feature-{feature}-algo-{name}`
```markdown
**ID**: `fdd-myapp-feature-auth-algo-hash-password`
```

**States**: `fdd-{project}-feature-{feature}-state-{name}`
```markdown
**ID**: `fdd-myapp-feature-auth-state-user-session`
```

**Changes**: Numeric within CHANGES.md
```markdown
## Change 1
**ID**: 1
```

### Qualified IDs (Code Traceability)

**Phase qualifiers**: `{base-id}:ph-{N}`
```
fdd-myapp-flow-login:ph-1
fdd-myapp-flow-login:ph-2
```

**Instruction qualifiers**: `{base-id}:ph-{N}:inst-{name}`
```
fdd-myapp-flow-login:ph-1:inst-validate-credentials
fdd-myapp-flow-login:ph-2:inst-create-session
```

**Used in code tags**:
```python
# @fdd-flow:fdd-myapp-flow-login:ph-1
def validate_credentials(username, password):
    # @fdd-flow:fdd-myapp-flow-login:ph-1:inst-validate-credentials
    ...
    # @fdd-flow-end
```

---

## ADR ID Format

**Format**: `ADR-{NNNN}`

**Pattern**: Four-digit sequential number

**Examples**:
```markdown
## ADR-0001: Choose Python for Tooling
**ID**: ADR-0001
**Status**: ACCEPTED

## ADR-0002: Use Markdown for Documentation  
**ID**: ADR-0002
**Status**: ACCEPTED
```

---

## Structure Patterns

### Business Context (BUSINESS.md)

```markdown
# Business Context: {Project Name}

## Section A: Vision
{Vision statement}

## Section B: Actors
### {Actor Name}
**ID**: `fdd-{project}-actor-{name}`
{Actor description}

## Section C: Capabilities
### {Capability Name}
**ID**: `fdd-{project}-capability-{name}`
{Capability description}
```

### Feature Design (DESIGN.md)

```markdown
# Feature Design: {Feature Name}

## Section A: Overview
**ID**: `fdd-{project}-feature-{name}`

## Section B: Actor Flows
### {Flow Name}
**ID**: `fdd-{project}-feature-{feature}-flow-{name}`

1. **Actor** performs action
2. **System** responds
   - [ ] Inst-label: Step description

## Section C: Algorithms
### {Algorithm Name}
**ID**: `fdd-{project}-feature-{feature}-algo-{name}`

## Section D: States & Data
### {State Name}
**ID**: `fdd-{project}-feature-{feature}-state-{name}`

## Section E: API Contracts
{API specifications}

## Section F: Requirements & Constraints
### {Requirement Name}
**ID**: `fdd-{project}-feature-{feature}-req-{name}`
```

---

## Validation

### FDD Tool Commands

**Validate artifact structure**:
```bash
python3 skills/fdd/scripts/fdd.py validate --artifact {path}
```

**List all IDs in artifact**:
```bash
python3 skills/fdd/scripts/fdd.py list-ids --artifact {path}
```

**Find ID definition**:
```bash
python3 skills/fdd/scripts/fdd.py where-defined --root . --id {id}
```

**Scan IDs in codebase**:
```bash
python3 skills/fdd/scripts/fdd.py scan-ids --root . --kind fdd
```

---

## Source

**Discovered from**:
- `requirements/*-structure.md` files
- FDD artifact examples in documentation
- `skills/fdd/scripts/fdd.py` - ID regex patterns
- README.md - FDD ID format descriptions

---

## Validation Checklist

Agent MUST verify before implementation:
- [ ] IDs use format `fdd-{project}-{kind}-{name}`
- [ ] IDs wrapped in backticks in Markdown
- [ ] IDs are lowercase kebab-case
- [ ] Qualified IDs use `:ph-N` and `:inst-name` format
- [ ] ADR IDs use `ADR-{NNNN}` format
- [ ] Artifacts follow structure requirements

**Self-test**:
- [ ] Did I check all criteria?
- [ ] Are ID examples valid format?
- [ ] Do patterns match actual artifacts?
