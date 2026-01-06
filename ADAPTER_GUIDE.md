# FDD Adapter Creation Guide

## Core Principle

Adapters extend FDD with project-specific context. Start files with `Extends: ../FDD/path/to/file.md`.

**You can override/add anything EXCEPT the immutable rules below.**

---

## Immutable Rules (NEVER Override)

These are validated by tooling and cannot be changed:

### 1. Design Hierarchy
```
OVERALL DESIGN → FEATURE DESIGN → OpenSpec CHANGES → CODE
```
Must reference parent level, never contradict.

### 2. Mandatory FDD Rules
- Actor Flows (Section B) are PRIMARY - always start from what actors do
- Use FDL for flows/algorithms/states - NEVER code in DESIGN.md
- Never redefine types - reference domain model from Overall Design
- Validate before proceeding (Overall ≥90/100, Feature 100/100)
- Feature size limits: ≤3000 lines (recommended), ≤4000 (hard limit)
- OpenSpec changes are atomic - one change = one deployable unit
- Design is source of truth - if code contradicts design, fix design first

### 3. File Structure
```
architecture/
├── DESIGN.md                    # Overall Design
└── features/
    ├── FEATURES.md              # Feature manifest
    └── feature-{slug}/
        ├── DESIGN.md            # Feature Design
        └── openspec/            # OpenSpec changes
```

### 4. DESIGN.md Sections
**Overall Design**:
- Section A: Business Context
- Section B: Requirements & Principles
- Section C: Technical Architecture
- Section D: Architecture Decision Records (ADR) - REQUIRED, MADR format
- Section E: Project-Specific Details (optional)

**Feature Design**:
- Section A: Feature Overview
- Section B: Actor Flows (PRIMARY)
- Section C: Algorithms
- Section D: States (optional)
- Section E: Technical Details
- Section F: Requirements (formalized scope + Testing Scenarios in FDL)
- Section G: Implementation Plan (OpenSpec changes with status)

### 5. Validation Scores
- Overall Design: ≥90/100
- Feature Design: 100/100 + 100% completeness

### 6. OpenSpec Structure
Must follow OpenSpec specification exactly (see `openspec/AGENTS.md`).

---

## What Adapters Define

Everything else is adapter-specific. Define as needed:

### Domain Model Format
- Technology (TypeScript, JSON Schema, Protobuf, GTS, etc.)
- Location (`architecture/domain-model/`, per-feature, etc.)
- DML syntax (`@DomainModel.TypeName` for clickable references)
- Validation commands
- Naming conventions
- Traceability requirements (clickable links from Feature→Overall)

### API Contract Format
- Technology (OpenAPI, GraphQL, gRPC, CLISPEC, etc.)
- Location (`architecture/api-specs/`, `architecture/cli-specs/`, etc.)
- Linking syntax (`@API.GET:/path`, `@CLI.command-name`, `@Feature.{slug}` for clickable references)
- Validation commands
- API conventions
- Traceability requirements (clickable links from Feature→Overall)

**Note**: For CLI tools, consider using **CLISPEC** - a built-in, simple format for CLI command documentation. See `CLISPEC.md` for specification.

### Implementation Details
- Database technology and patterns
- Authentication/authorization approach
- Error handling patterns
- Testing strategy (frameworks, locations)
- Build/deployment commands
- Code style and linting rules
- Validation output format (MUST be chat output only, NO report files)

### Behavior Description Language (Optional Override)
- **Default**: FDL (Flow Description Language) for flows/algorithms/states
- **Can override**: Create custom behavior specification in `{adapter-directory}/FDD-Adapter/`
- **Example**: Replace `../FDL.md` with `../FDD-Adapter/CustomBDL.md`
- **Requirements**: Define control flow keywords, syntax rules, validation criteria
- **Note**: Must update workflows 05 and 06 to reference custom spec

### Additional Artifacts
- Diagrams location and format
- Documentation structure
- CI/CD configuration
- Any project-specific tooling

---

## Adapter Structure

```bash
{adapter-directory}/             # Configurable: spec/, guidelines/, docs/
├── FDD/                         # Core (immutable rules)
└── FDD-Adapter/                 # Your project-specific extensions
    ├── AGENTS.md                # Extends: ../FDD/AGENTS.md
    └── workflows/
        ├── AGENTS.md            # Extends: ../FDD/workflows/AGENTS.md
        └── *.md                 # Extend specific workflows as needed
```

**Note**: `{adapter-directory}` is configured by project owner (commonly `spec/`, `guidelines/`, or `docs/`)

---

## Template: AGENTS.md

```markdown
# AI Agent Instructions for {Project Name}

**Extends**: `../FDD/AGENTS.md`
**Status**: COMPLETE

---

## Domain Model

**Technology**: TypeScript
**Location**: `architecture/domain-model/types.ts`
**DML Syntax**: `@DomainModel.TypeName` (clickable references)
**Validation**: `tsc --noEmit`
**Traceability**: All Feature DESIGN.md must use clickable links to domain model

## API Contracts

**Technology**: OpenAPI 3.1
**Location**: `architecture/api-specs/openapi.yaml`
**Linking**: `@API.GET:/path` (clickable references)
**Validation**: `openapi validate`
**Traceability**: All Feature DESIGN.md must use clickable links to API specs

## Behavior Description Language

**Language**: FDL (default, see `../FDL.md`)
**Override**: Not used (keep default FDL)

## Implementation

**Database**: Prisma
**Auth**: JWT + refresh tokens
**Testing**: Jest (unit), Playwright (e2e)
**Commands**: `npm test`, `npm run build`
**Validation Output**: Chat only (NO report files)
```

---

## Template: workflows/AGENTS.md

```markdown
# Workflow Instructions for {Project Name}

**Extends**: `../../FDD/workflows/AGENTS.md`

---

## Pre-Workflow Checks
- [ ] npm dependencies installed
- [ ] Database running

## Validation
- Domain model: `tsc --noEmit`
- API specs: `openapi validate`
- Validation output: Chat only (NO report files)

## Traceability
- All Feature DESIGN.md Section F must use clickable links to Overall DESIGN.md
- All OpenSpec changes must reference Feature DESIGN.md sections
```
