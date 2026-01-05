# AI Agent Instructions for FDD

**READ THIS FIRST**: This document defines FDD core methodology for AI agents. For implementation details and step-by-step procedures, see `workflows/` directory.

---

## ⚠️ PREREQUISITE: FDD ADAPTER REQUIRED

**FDD CANNOT WORK WITHOUT A PROJECT-SPECIFIC ADAPTER**

Before doing ANY FDD work, you **MUST** verify that a project adapter exists:

**Check for adapter**:
1. Look for `{adapter-directory}/FDD-Adapter/AGENTS.md` that extends `../FDD/AGENTS.md`
2. Common locations:
   - `spec/FDD-Adapter/AGENTS.md`
   - `guidelines/FDD-Adapter/AGENTS.md`
   - `docs/FDD-Adapter/AGENTS.md`

**If adapter NOT found**:
```
❌ STOP: FDD adapter not found.

FDD requires a project-specific adapter before any work can begin.

Would you like to create an adapter now? (recommended)
→ Run Workflow: adapter-config (workflows/adapter-config.md)

This will guide you through:
- Domain model technology selection
- API contract format
- Testing and build tools
- Project-specific conventions
```

**If adapter found but INCOMPLETE**:
```
⚠️ WARNING: Adapter is marked as INCOMPLETE.

Missing specifications:
{List from adapter AGENTS.md}

ALL workflows are BLOCKED.

Please complete the adapter by adding missing specifications.
```

**Only proceed with FDD workflows if**:
- ✅ Adapter exists
- ✅ Adapter extends FDD AGENTS.md
- ✅ Adapter status is COMPLETE (or user acknowledges INCOMPLETE status)

---

## How Extends Works

**When file has `**Extends**: base-file.md`**: Load base file first, then apply modifications from current file. Merge = base instructions + modifications. Never skip base, never replace base rules.

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
1. ✅ **Actor Flows are PRIMARY** - Section B drives everything, document all flows first
2. ✅ **Use FDL for flows/algorithms/states** - NEVER write code in DESIGN.md, only plain English FDL
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


## 🤖 AI AGENT INTERACTIVE MODE

**Workflows use dialog mode**: AI proposes answers based on context, user reviews/approves.

**Interactive Questions**:
1. Analyze user's prompt - extract intent and context
2. Propose specific answers (not open-ended questions)
3. Present for review - user approves/modifies/rejects
4. Iterate in dialog until approved

**Domain Model & API Specs - CRITICAL**:
- Must ensure COMPLETE specifications for validation
- All types/schemas/objects defined in machine-readable format (GTS, JSON Schema, OpenAPI, etc.)
- Never accept vague specs ("use JSON" ❌) - require specific paths and formats

**Auto-Validation After Workflow** (MANDATORY):
- Workflows with validation: 01→02, 03→04, 05→06, 09→12
- After workflow completes, automatically run validation
- If passes: suggest next workflow
- If fails: propose fixes, iterate until passes

**Validation Output** (CRITICAL):
- ❌ **DO NOT create validation report files** (e.g., `VALIDATION_REPORT.md`, `FEATURE_VALIDATION_REPORT.md`, `OPENSPEC_VALIDATION_REPORT.md`)
- ✅ **Output all validation results directly in chat** with comprehensive information
- ✅ Include: scores, findings, issues, recommendations, next steps
- ✅ Format clearly using markdown (sections, tables, lists, code blocks)
- **Rationale**: Report files clutter workspace and get deleted; chat output is immediately visible and actionable

**Suggest Next Workflow** (MANDATORY):
- After every workflow + validation, suggest next logical step
- Progression paths: New Project (01→02→03→04→05), New Feature (05→06→09→10→11→07), Fix (08→02/06)

**Rules**:
- ✅ Propose answers (not just ask), show reasoning, batch questions, track context
- ❌ Never accept incomplete specs, skip validation, or leave user unsure what's next

---

## OpenSpec Integration (REQUIRED)

**CRITICAL**: Before using any OpenSpec commands (workflows 09-13), **you MUST read the full OpenSpec specification** at `spec/FDD/openspec/AGENTS.md`

### Core OpenSpec Principles

**What is OpenSpec**:
- Atomic change management system for feature implementation
- Each change is self-contained, traceable, and deployable
- Single project-level OpenSpec at `openspec/` (project root)
- Changes tracked in `openspec/changes/`, merged to `openspec/specs/`

**Key Rules**:
1. **Use `openspec` CLI tool** - All operations through CLI, not manual scripts
2. **Single OpenSpec location** - `openspec/` at project root, NOT per-feature
3. **Feature grouping** - Specs organized by feature: `specs/{project-name}-{feature-slug}/spec.md`
4. **Always run from openspec root** - OpenSpec commands MUST run from `openspec/` directory
5. **Always use non-interactive mode** - Agents MUST use appropriate flags to avoid prompts: specify item explicitly (`show <change-name>`, `validate <change-name>`), use `--all --no-interactive` for bulk validate, use `-y` for archive
6. **Changes are atomic** - One change = one deployable unit (implements 1-5 requirements)
7. **Changes created manually** - Create directory structure manually (no `openspec init` command)
8. **Required files** - Every change has `proposal.md`, `tasks.md`, `specs/{feature-slug}/spec.md`, optional `design.md`
9. **Source of truth** - `openspec/specs/` contains merged specifications

**OpenSpec Commands**:
- `openspec list` - List active changes
- `openspec list --specs` - List specifications
- `openspec show <item>` - Show change or spec details (non-interactive if item specified)
- `openspec validate <item>` - Validate specific change or spec (non-interactive)
- `openspec validate <item> --strict` - Comprehensive validation of specific item
- `openspec validate --all --no-interactive` - Validate all without prompts (recommended for automation)
- `openspec archive <change-name>` - Archive completed change (interactive)
- `openspec archive <change-name> -y` - Archive without confirmation (non-interactive)
- `openspec archive <change-name> --skip-specs -y` - Archive without spec updates (non-interactive)
- `openspec archive <change-name> --no-validate -y` - Archive without validation (not recommended)

**Non-Interactive Mode**: 
- Commands with specific item argument (`show <item>`, `validate <item>`) are automatically non-interactive
- For bulk `validate`: Use `--all --no-interactive` to validate everything without prompts
- For `archive`: Use `-y` or `--yes` flag to skip confirmation prompts

**Project Structure**:
```
project-root/
├── architecture/
│   ├── DESIGN.md                      # Overall Design
│   └── features/
│       └── feature-{slug}/
│           └── DESIGN.md
│               Section B: Actor Flows (FDL)
│               Section C: Algorithms (FDL)
│               Section D: States (FDL)
│               Section E: Technical Details
│               Section F: Validation & Implementation
│               Section G: Requirements (references to B-E)
│               Section H: Implementation Plan (changes with status)
├── openspec/                          # ← SINGLE project-level OpenSpec
│   ├── project.md                     # Project conventions
│   ├── specs/                         # Source of truth (merged specs)
│   │   └── fdd-{project-name}-feature-{feature-slug}/  # ← FDD prefix + project + feature
│   │       └── spec.md                # ← Requirements from DESIGN.md Section G
│   └── changes/                       # Active and archived changes
│       ├── {change-name}/             # Active change (kebab-case)
│       │   ├── proposal.md            # Why, what, impact
│       │   ├── tasks.md               # Implementation checklist
│       │   ├── design.md              # Technical decisions (optional)
│       │   └── specs/                 # Delta specifications
│       │       └── fdd-{project-name}-feature-{feature-slug}/  # ← FDD prefix + project + feature
│       │           └── spec.md        # ← ADDED/MODIFIED/REMOVED
│       └── archive/                   # Completed changes
│           └── YYYY-MM-DD-{change-name}/
└── spec/
```

**Feature Design Integration**:
- **Section G**: Requirements (formalized scope, references to flows/algorithms/states)
- **Section H**: Implementation Plan (changes implementing 1-5 requirements each, with status)
- Workflows 09-13 are OpenSpec workflows
- Use after Feature Design validated (workflow 06)

**Workflows**:
- Create change (first or next) → `workflows/09-openspec-change-next.md`
- Implement change → `workflows/10-openspec-change-implement.md`
- Complete change → `workflows/11-openspec-change-complete.md`
- Validate specs → `workflows/12-openspec-validate.md`

**Resources**:
- **Full Specification**: `spec/FDD/openspec/AGENTS.md` ⚠️ READ BEFORE USE
- **Website**: https://openspec.dev
- **GitHub**: https://github.com/Fission-AI/OpenSpec
- **Install**: `npm install -g @fission-ai/openspec@latest`

---

## Design Levels

**OVERALL DESIGN** (`architecture/DESIGN.md`, ≤5000 lines, ≥90/100):
- Section A: Business Context, Section B: Requirements & Principles, Section C: Technical Architecture
- Defines: architecture, domain model, API contracts, actors
- Workflows: 01-init-project, 02-validate-architecture

**FEATURE DESIGN** (`architecture/features/feature-{slug}/DESIGN.md`, ≤4000 lines, 100/100):
- Section A: Overview (purpose, actors, references)
- Section B: Actor Flows (in FDL)
- Section C: Algorithms (in FDL)
- Section D: States (in FDL, state machines if needed)
- Section E: Technical Details (DB, API, security)
- Section F: Validation & Implementation (test scenarios)
- **Section G: Requirements** (formalized scope, references B-E via markdown anchors)
- **Section H: Implementation Plan** (OpenSpec changes implementing requirements, with status)
- Uses FDL for flows/algorithms/states, references Overall Design types
- Workflows: 05-init-feature, 06-validate-feature, 08-fix-design

**OpenSpec CHANGES** (`openspec/changes/{change-name}/`):
- Files: proposal.md, tasks.md, specs/{feature-slug}/spec.md, design.md (optional)
- Atomic units implementing 1-5 requirements
- Workflows: 09-openspec-init, 10-implement, 11-complete, 12-next, 13-validate

**FEATURES.md** (`architecture/features/FEATURES.md`):
- Status: ⏳ NOT_STARTED, 🔄 IN_PROGRESS, ✅ IMPLEMENTED
- Workflows: 03-init-features, 04-validate-features

**Adapters** (`{adapter-directory}/FDD-Adapter/`):
- Define: domain model format, API contracts, implementation details
- Cannot override: design hierarchy, mandatory rules, file structure, validation scores
- See: `ADAPTER_GUIDE.md`
- Note: `{adapter-directory}` is configured by project owner (spec/, guidelines/, docs/, etc.)

---

## Quick Reference

**Starting FDD Work**:
1. Check for FDD Adapter (REQUIRED) → Look for `{adapter-dir}/AGENTS.md`
2. Read `workflows/AGENTS.md` for workflow selection
3. Read `FDL.md` for syntax

**Key Files**: `architecture/DESIGN.md`, `architecture/features/FEATURES.md`, `architecture/features/feature-{slug}/DESIGN.md`, `openspec/`

**Remember**: Requirements PRIMARY (B), FDL for flows/algorithms, reference types (never redefine), validate before proceeding