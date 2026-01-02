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
- Section D: Project-Specific Details (optional)

**Feature Design**:
- Section A: Feature Overview
- Section B: Actor Flows (PRIMARY)
- Section C: Algorithms
- Section D: States (optional)
- Section E: Technical Details
- Section F: Validation & Implementation

### 5. Validation Scores
- Overall Design: ≥90/100
- Feature Design: 100/100 + 100% completeness

### 6. OpenSpec Structure
Must follow OpenSpec specification exactly (see `openspec/AGENTS.md`).

---

## What Adapters Define

Everything else is adapter-specific. Define as needed:

### Domain Model Format
- Technology (TypeScript, JSON Schema, Protobuf, etc.)
- Location (`architecture/domain-model/`, per-feature, etc.)
- DML syntax (`@DomainModel.TypeName`)
- Validation commands
- Naming conventions

### API Contract Format
- Technology (OpenAPI, GraphQL, gRPC, etc.)
- Location (`architecture/api-specs/`, per-feature, etc.)
- Linking syntax (`@API.GET:/path`, `@Feature.{slug}`)
- Validation commands
- API conventions

### Implementation Details
- Database technology and patterns
- Authentication/authorization approach
- Error handling patterns
- Testing strategy (frameworks, locations)
- Build/deployment commands
- Code style and linting rules

### Additional Artifacts
- Diagrams location and format
- Documentation structure
- CI/CD configuration
- Any project-specific tooling

---

## Adapter Structure

```bash
guidelines/
├── FDD/                         # Core (immutable rules)
└── {project}-adapter/           # Your extensions
    ├── AGENTS.md                # Extends: ../FDD/AGENTS.md
    └── workflows/
        ├── AGENTS.md            # Extends: ../FDD/workflows/AGENTS.md
        └── *.md                 # Extend specific workflows as needed
```

---

## Template: AGENTS.md

```markdown
# AI Agent Instructions for {Project Name}

**Extends**: `../FDD/AGENTS.md`

---

## Domain Model

**Technology**: TypeScript
**Location**: `architecture/domain-model/types.ts`
**DML Syntax**: `@DomainModel.TypeName`
**Validation**: `tsc --noEmit`

## API Contracts

**Technology**: OpenAPI 3.1
**Location**: `architecture/api-specs/openapi.yaml`
**Linking**: `@API.GET:/path`
**Validation**: `openapi validate`

## Implementation

**Database**: Prisma
**Auth**: JWT + refresh tokens
**Testing**: Jest (unit), Playwright (e2e)
**Commands**: `npm test`, `npm run build`
```

---

## Template: workflows/AGENTS.md

```markdown
# Workflow Instructions for {Project Name}

**Extends**: `../FDD/workflows/AGENTS.md`

---

## Pre-Workflow Checks
- [ ] npm dependencies installed
- [ ] Database running

## Validation
- Domain model: `tsc --noEmit`
- API specs: `openapi validate`
```
