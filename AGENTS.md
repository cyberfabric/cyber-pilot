# AI Agent Instructions for FDD

**READ THIS FIRST**: This document defines FDD core methodology for AI agents. For implementation details and step-by-step procedures, see `workflows/` directory.

---

## CRITICAL RULES - NEVER VIOLATE

**Design Hierarchy** (strict order, no violations):
```
OVERALL DESIGN (architecture + domain model + API contracts)
    ↓ must reference, never contradict
FEATURE DESIGN (actor flows + algorithms in FDL + implementation plan)
    ↓ must reference, never contradict
OpenSpec CHANGES (atomic implementation specs)
    ↓ must implement exactly
CODE (implementation)
```

**Mandatory Rules**:
1. ✅ **Actor Flows are PRIMARY** - Section B drives everything, always start from what actors do
2. ✅ **Use FDL for Actor Flows, Algorithms, and States** - NEVER write code in DESIGN.md, only plain English FDL
3. ✅ **Never redefine types** - Reference domain model from Overall Design, never duplicate
4. ✅ **Validate before proceeding** - Overall Design must score ≥90/100, Feature Design must score 100/100 + 100%
5. ✅ **Feature size limits** - ≤3000 lines recommended, ≤4000 hard limit
6. ✅ **OpenSpec changes are atomic** - One change = one deployable unit
7. ✅ **Design is source of truth** - If code contradicts design, fix design first, then re-validate

**If Contradiction Found**:
1. **STOP implementation immediately**
2. Identify which level has the issue (Overall/Feature/Change/Code)
3. Fix design at that level → Use `workflows/08-fix-design.md`
4. Re-validate affected levels → Use `workflows/02-validate-architecture.md` or `workflows/06-validate-feature.md`
5. Update dependent levels
6. Resume only after validation passes

---

## OpenSpec Integration (REQUIRED)

**CRITICAL**: Before using any OpenSpec commands (workflows 09-12), **you MUST read the full OpenSpec specification** at `openspec/AGENTS.md`

### Core OpenSpec Principles

**What is OpenSpec**:
- Atomic change management system for feature implementation
- Each change is self-contained, traceable, and deployable
- Changes tracked in `openspec/changes/`, merged to `openspec/specs/`

**Key Rules**:
1. **Use `openspec` CLI tool** - All operations through CLI, not manual scripts
2. **Changes are atomic** - One change = one deployable unit
3. **Changes created manually** - Create directory structure manually (no `create` command)
4. **Required files** - Every change has `proposal.md`, `tasks.md`, `specs/`, optional `design.md`
5. **Source of truth** - `openspec/specs/` contains merged specifications

**OpenSpec Commands**:
- `openspec init [path]` - Initialize OpenSpec structure
- `openspec list` - List active changes
- `openspec list --specs` - List specifications
- `openspec show [item]` - Show change or spec details
- `openspec validate [item]` - Validate changes or specs
- `openspec validate [item] --strict` - Comprehensive validation
- `openspec archive <change-id>` - Archive completed change
- `openspec archive <change-id> --skip-specs --yes` - Archive without spec updates

**Change Structure**:
```
feature-{slug}/
└── openspec/
    ├── project.md       # Project conventions
    ├── specs/           # Source of truth (merged specs)
    │   └── [capability]/
    │       ├── spec.md
    │       └── design.md
    └── changes/         # Active and archived changes
        ├── [change-name]/        # Active change (kebab-case)
        │   ├── proposal.md       # Why, what, impact
        │   ├── tasks.md          # Implementation checklist
        │   ├── design.md         # Technical decisions (optional)
        │   └── specs/            # Delta specifications
        │       └── [capability]/
        │           └── spec.md   # ADDED/MODIFIED/REMOVED
        └── archive/              # Completed changes
            └── YYYY-MM-DD-[change-name]/
```

**Three-Stage Workflow**:
```
1. Creating Changes - Scaffold proposal, tasks, design (optional), delta specs
2. Implementing Changes - Read docs, implement sequentially, update checklist
3. Archiving Changes - Use `openspec archive <change-id>`, moves to archive/
```

**When to Use OpenSpec**:
- Workflows 09-12 are OpenSpec workflows
- Use after Feature Design is validated (workflow 06)
- Each feature breaks into multiple OpenSpec changes
- Changes implement code according to Feature Design

**Workflows**:
- Initialize OpenSpec → `workflows/09-openspec-init.md`
- Implement change → `workflows/10-openspec-change-implement.md`
- Complete change → `workflows/11-openspec-change-complete.md`
- Validate specs → `workflows/12-openspec-validate.md`

**Resources**:
- **Full Specification**: `openspec/AGENTS.md` ⚠️ READ BEFORE USE
- **Website**: https://openspec.dev
- **GitHub**: https://github.com/Fission-AI/OpenSpec
- **Install**: `npm install -g @fission-ai/openspec@latest`

---

## Design Levels - When to Use What

**OVERALL DESIGN** - Create ONCE per module/service:
- ✅ System architecture and layers
- ✅ Domain model types (all entities, value objects)
- ✅ API contract specification (all endpoints)
- ✅ Actors, roles, capabilities, principles
- ❌ HOW things work (that's Feature Design)
- ❌ Implementation details (that's OpenSpec Changes)

**Workflows**:
- Initialize → `workflows/01-init-project.md`
- Validate → `workflows/02-validate-architecture.md`

---

**FEATURE DESIGN** - Create for EACH feature:
- ✅ Actor flows (what each actor does)
- ✅ Algorithms in FDL (how system processes)
- ✅ OpenSpec changes plan (breakdown)
- ✅ Testing scenarios
- ❌ Type definitions (reference Overall Design)
- ❌ API endpoints (reference Overall Design)

**Workflows**:
- Initialize feature → `workflows/05-init-feature.md`
- Validate feature → `workflows/06-validate-feature.md`
- Fix design issues → `workflows/08-fix-design.md`

---

**OpenSpec CHANGES** - Create for EACH atomic implementation:
- ✅ Proposal (why this change)
- ✅ Tasks checklist (implementation steps)
- ✅ Delta specs (what changes in code)
- ❌ Design rationale (that's in Feature Design)
- ❌ Architecture changes (that's in Overall Design)

**Workflows**: See OpenSpec Integration section above

---

## OVERALL DESIGN

**File**: `architecture/DESIGN.md`  
**Size**: ≤5000 lines  
**Score**: ≥90/100

**What Goes Here**:
- Section A: Business Context (vision, actors, capabilities)
- Section B: Requirements & Principles
- Section C: Technical Architecture (architecture overview, domain model, API contracts)
- Section D: Project-Specific Details (optional, not validated - integrations, future plans, etc.)

**What's Defined by Adapter**:
- DML (Domain Model Language) - how to reference types
- Feature Linking - how to link between features and Overall Design
- External artifact locations (domain model specs, API specs, diagrams)

**Workflows**:
- Create structure and templates → `workflows/01-init-project.md`
- Validate completeness → `workflows/02-validate-architecture.md`

---

## FEATURE DESIGN

**File**: `architecture/features/feature-{slug}/DESIGN.md`  
**Size**: ≤3000 lines (recommended), ≤4000 (hard limit)  
**Score**: 100/100 + 100% completeness

**What Goes Here**:
- Section A: Feature Overview (purpose, scope, references to Overall Design)
- **Section B: Actor Flows** ⚠️ PRIMARY - use FDL, design this first!
- Section C: Algorithms - use FDL, never code
- Section D: States (optional) - use FDL for state machines
- Section E: Technical Details (DB schema, operations, access control, error handling)
- Section F: Validation & Implementation (testing scenarios, OpenSpec changes plan)

**What's NOT Here**:
- ❌ Type definitions (reference Overall Design)
- ❌ API endpoints (reference Overall Design)
- ❌ Code examples (use FDL only)

**What's Defined by Adapter**:
- DML (Domain Model Language) - how to reference types
- Feature Linking - how to link between features and Overall Design
- Format for technical details sections

**Workflows**:
- Create feature structure and template → `workflows/05-init-feature.md`
- Validate feature completeness → `workflows/06-validate-feature.md`
- Fix design issues → `workflows/08-fix-design.md`

---

## FEATURES.md Manifest

**Location**: `architecture/features/FEATURES.md`

**Purpose**: Central registry tracking all features with dependencies and status

**Status Values**:
- ⏳ **NOT_STARTED** - DESIGN.md created, design in progress
- 🔄 **IN_PROGRESS** - OpenSpec initialized, implementation started
- ✅ **IMPLEMENTED** - All OpenSpec changes completed

**Content**: Feature list with slug, status, folder/DESIGN links (clickable), dependencies (depends on / blocks)

**Workflows**:
- Generate from Overall Design → `workflows/03-init-features.md`
- Validate manifest → `workflows/04-validate-features.md`

---

## Adapters - Project-Specific Extensions

**Purpose**: Adapters extend FDD with project-specific context without changing core methodology.

**Location**: `guidelines/{project-name}-adapter/`

### Immutable Rules (Adapters CANNOT Override)

These rules are validated by tooling and must never be changed:

1. **Design Hierarchy**: OVERALL DESIGN → FEATURE DESIGN → OpenSpec CHANGES → CODE
2. **Mandatory FDD Rules**: Actor Flows PRIMARY, FDL only, no type redefinition, validate before proceeding
3. **File Structure**: `architecture/DESIGN.md`, `architecture/features/`, OpenSpec structure
4. **DESIGN.md Sections**: Section A-C (Overall), Section A-F (Feature) - structure is fixed
5. **Validation Scores**: Overall ≥90/100, Feature 100/100 + 100% completeness
6. **OpenSpec Structure**: Must follow OpenSpec specification exactly

### What Adapters Define

Everything else is adapter-specific:

- **Domain Model Format**: Technology, location, DML syntax, validation commands
- **API Contract Format**: Technology, location, linking syntax, validation commands
- **Implementation Details**: Database, auth, error handling, testing, build/deploy
- **Additional Artifacts**: Diagrams, documentation, CI/CD, tooling

**See**: `ADAPTER_GUIDE.md` for creating adapters

---

## Quick Reference

**When Starting FDD Work**:
1. Read `AGENTS.md` (this file) - Core methodology
2. Read `workflows/AGENTS.md` - Workflow selection guide
3. Read `FDL.md` - FDL syntax reference

**Key Files**:
- `architecture/DESIGN.md` - Overall Design (≤5000 lines, ≥90/100)
- `architecture/features/FEATURES.md` - Feature manifest
- `architecture/features/feature-{slug}/DESIGN.md` - Feature Design (≤4000 lines, 100/100)
- `architecture/features/feature-{slug}/openspec/` - OpenSpec changes

**Workflow Selection**:
- See `workflows/AGENTS.md` for decision tree and complete workflow list

**Remember**:
- ✅ Actor Flows (Section B) are PRIMARY - start design here
- ✅ Use FDL for flows/algorithms/states - NEVER write code in DESIGN.md
- ✅ Reference types from Overall Design - NEVER redefine
- ✅ Validate before proceeding (Overall ≥90/100, Feature 100/100)
- ✅ If contradiction found - STOP, fix design, re-validate