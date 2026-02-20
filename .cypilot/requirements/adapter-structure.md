---
cypilot: true
type: requirement
name: Adapter Structure
version: 1.1
purpose: Define validation rules for Cypilot adapter files
---

# Cypilot Adapter Structure Requirements

---

## Table of Contents

- [Agent Instructions](#agent-instructions)
- [Overview](#overview)
- [Content Boundaries](#content-boundaries)
- [Required Files](#required-files)
- [Two-Phase Validation](#two-phase-validation)
- [Spec File Structure](#spec-file-structure)
- [Error Handling](#error-handling)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)
- [Common Issues](#common-issues)
- [References](#references)

---

## Agent Instructions

**ALWAYS open and follow**: `../workflows/adapter.md` WHEN executing workflow

**ALWAYS open**: `../.cypilot-adapter/AGENTS.md` WHEN reviewing a valid adapter AGENTS.md example (this repository)

**Prerequisite**: Agent confirms understanding before proceeding:
- [ ] Agent has read and understood this requirement
- [ ] Agent will follow the rules defined here

---

## Overview

- **This file defines**: Validation rules — see [Consolidated Validation Checklist](#consolidated-validation-checklist)
- **Template defines**: Structure for generation (HOW to create)
- **Workflow defines**: Process (STEP by STEP)

**Cypilot Adapter** — Dynamic project-specific configuration that evolves with the project

**Philosophy**: 
- Adapter specs derive from design decisions, not predefined templates
- Technical decisions appear during design → captured in adapter
- Existing projects → adapter discovers patterns from code/docs/ADRs
- Greenfield projects → adapter starts minimal, grows with design

**Lifecycle**:
1. **Bootstrap**: Minimal AGENTS.md with `Extends` only
2. **Discovery**: Scan code/docs/ADRs → propose specs
3. **Evolution**: Design decisions → update adapter specs
4. **Refinement**: Code patterns → update adapter specs

---

## Content Boundaries

**Should contain**:
- `**Extends**: ...` back to core `AGENTS.md`.
- Project-specific conventions and pointers:
  - Tech stack/tooling constraints.
  - Domain model format and location.
  - API contract format and location.
  - Validation/CI expectations.

**Should not contain**:
- PRD content (use PRD artifact).
- Architecture decisions rationale (use ADRs).
- Spec specs or implementation plans.

---

## Required Files

### .cypilot-config.json

**Location**: `{project-root}/.cypilot-config.json`

**Mandatory fields**:
```json
{
  "cypilotAdapterPath": ".cypilot-adapter"
}
```

**Validation**:
- [ ] File exists at project root
- [ ] Valid JSON format
- [ ] `cypilotAdapterPath` field present
- [ ] Path points to existing directory with AGENTS.md

### AGENTS.md

**Location**: `{adapter-directory}/AGENTS.md`

**WHEN clause format** (mandatory for adapter navigation rules):
```
ALWAYS open and follow `{spec-file}` WHEN {action-description}
```

**Action-based rules**: Rules describe WHAT the agent is doing, not which kit or artifact kind is active. This makes rules universal and easier to match.

#### Universal WHEN Rules

| Spec File | WHEN Rule |
|-----------|-----------|
| `tech-stack.md` | WHEN writing code, choosing technologies, or adding dependencies |
| `conventions.md` | WHEN writing code, naming files/functions/variables, or reviewing code |
| `project-structure.md` | WHEN creating files, adding modules, or navigating codebase |
| `domain-model.md` | WHEN working with entities, data structures, or business logic |
| `testing.md` | WHEN writing tests, reviewing test coverage, or debugging |
| `build-deploy.md` | WHEN building, deploying, or configuring CI/CD |
| `patterns.md` | WHEN implementing features, designing components, or refactoring |
| `api-contracts.md` | WHEN creating/consuming APIs, defining endpoints, or handling requests |
| `security.md` | WHEN handling authentication, authorization, or sensitive data |
| `data-governance.md` | WHEN storing user data, handling PII, or managing data lifecycle |
| `performance.md` | WHEN optimizing, caching, or working with high-load components |
| `reliability.md` | WHEN handling errors, implementing retries, or adding health checks |
| `compliance.md` | WHEN handling regulated data, audit logging, or legal requirements |

**Valid examples** ✅:
```markdown
ALWAYS open and follow `specs/tech-stack.md` WHEN writing code, choosing technologies, or adding dependencies

ALWAYS open and follow `specs/conventions.md` WHEN writing code, naming files/functions/variables, or reviewing code

ALWAYS open and follow `specs/testing.md` WHEN writing tests, reviewing test coverage, or debugging
```

**Invalid examples** ❌:
```markdown
# Too vague - doesn't describe specific action
ALWAYS open and follow `specs/tech-stack.md` WHEN working on project
→ FIX: Be specific about the action

# Tied to kit (legacy format)
ALWAYS open and follow `specs/tech-stack.md` WHEN Cypilot uses kit `cypilot-sdlc` for codebase
→ FIX: Use action-based format: WHEN writing code, choosing technologies, or adding dependencies

# Tied to artifact kind (legacy format)
ALWAYS open and follow `specs/domain-model.md` WHEN generating DESIGN
→ FIX: Use action-based format: WHEN working with entities, data structures, or business logic
```

---

## Two-Phase Validation

### Phase 1: Bootstrap (Minimal)

**When**: New project, no design yet

**Required content**:
```markdown
# Cypilot Adapter: {Project Name}

**Extends**: `{path}/Cypilot/AGENTS.md`
```

### Phase 2: Evolved Adapter

**When**: Project with DESIGN.md OR discovered codebase

**Additional required fields**:
- Version
- Last Updated
- Tech Stack

**Required spec files** (created by `/cypilot-adapter` during Discovery phase or manually):

| Spec File | Contains | Created When |
|-----------|----------|--------------|
| `tech-stack.md` | Languages, frameworks, databases | DESIGN.md references tech stack |
| `domain-model.md` | Schema format, entity structure | DESIGN.md defines domain entities |
| `api-contracts.md` | Contract format, endpoint patterns | DESIGN.md includes API specs |
| `patterns.md` | Architecture patterns | ADR or DESIGN references patterns |
| `conventions.md` | Naming, style, file organization | Codebase exists OR DESIGN defines conventions |
| `build-deploy.md` | Build commands, CI/CD | Project has build/deploy config |
| `testing.md` | Test frameworks, structure | Project has test infrastructure |
| `project-structure.md` | Directory layout, package organization | Codebase exists |
| `security.md` | Auth mechanisms, data classification | Security-sensitive project |
| `data-governance.md` | Data lifecycle, retention, privacy | Data-intensive project |
| `performance.md` | SLAs, caching, optimization | Performance-critical project |
| `reliability.md` | Error handling, recovery, fallbacks | Production system |
| `compliance.md` | Regulations, standards, audit | Regulated industry |

**Creation trigger**: Run `/cypilot-adapter --rescan` to auto-detect and propose spec files based on project state.

---

## Spec Discovery Guide

This section defines **what to look for** and **where to find it** when discovering project-specific knowledge for adapter specs. The domains are derived from the expertise areas in Cypilot checklists (PRD, DESIGN, DECOMPOSITION, ADR, SPEC, and codebase).

### Discovery Methodology

Follow the layers from `reverse-engineering.md`:
1. **Surface Reconnaissance** → tech-stack.md, project-structure.md
2. **Entry Point Analysis** → conventions.md, patterns.md
3. **Structural Decomposition** → domain-model.md, api-contracts.md
4. **Data Flow Tracing** → data-governance.md, security.md
5. **Dependency Mapping** → tech-stack.md (dependencies section)
6. **State Management Analysis** → patterns.md (state patterns)
7. **Integration Boundary Scan** → api-contracts.md, reliability.md
8. **Pattern Recognition** → patterns.md, conventions.md
9. **Knowledge Synthesis** → All specs consolidated

### Spec Discovery Matrix

| Spec File | Domain | What to Discover | Where to Look |
|-----------|--------|------------------|---------------|
| `tech-stack.md` | ARCH/OPS | Languages, frameworks, databases, infrastructure | `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `docker-compose.yml`, `.env.example`, config files |
| `project-structure.md` | ARCH | Directory layout, module organization, entry points | Root directories, `src/`, `lib/`, `pkg/`, README structure |
| `domain-model.md` | BIZ/DATA | Core concepts, entities, relationships, invariants | Types/models directories, schemas, DESIGN.md, glossary |
| `api-contracts.md` | INT | Endpoints, protocols, request/response formats | `openapi.yml`, `swagger.json`, `*.proto`, API docs |
| `patterns.md` | ARCH | Architecture patterns, design patterns, state management | DESIGN.md, ADRs, code structure, existing abstractions |
| `conventions.md` | MAINT | Code style, naming, file organization, commit style | `.eslintrc`, `.prettierrc`, `ruff.toml`, `.editorconfig`, CONTRIBUTING.md |
| `build-deploy.md` | OPS | Build commands, CI/CD, deployment procedures | `Makefile`, `package.json` scripts, `.github/workflows/`, `Dockerfile` |
| `testing.md` | TEST | Test framework, patterns, coverage rules, fixtures | Test directories, `pytest.ini`, `jest.config.js`, test files |
| `security.md` | SEC | Auth mechanisms, data classification, encryption | Auth configs, security middleware, encryption configs, security ADRs |
| `data-governance.md` | DATA/COMPL | Data lifecycle, retention, privacy, classification | Privacy policies, data models, migration scripts, compliance docs |
| `performance.md` | PERF | SLAs, caching strategy, optimization patterns | Caching configs, performance tests, monitoring dashboards, ADRs |
| `reliability.md` | REL | Error handling, recovery, fallbacks, circuit breakers | Error handling patterns, retry configs, health checks, runbooks |
| `compliance.md` | COMPL | Regulations, standards, audit requirements | Compliance docs, audit logs, regulatory references |

### Discovery Signals by Domain

#### ARCH (Architecture)
**Signals to look for**:
- Directory structure patterns (layered, hexagonal, clean architecture)
- Module boundaries and dependencies
- Component organization
- Service boundaries (monolith vs microservices)

**Discovery locations**:
- Root directory structure
- Package/module definitions
- Import patterns
- DESIGN.md, ADRs

#### PERF (Performance)
**Signals to look for**:
- Caching configurations (Redis, Memcached, in-memory)
- Database indexes and query optimization
- Response time SLAs
- Batch processing patterns

**Discovery locations**:
- Cache configurations
- Database migration files
- Performance tests
- Monitoring dashboards
- Load testing configs

#### SEC (Security)
**Signals to look for**:
- Authentication mechanism (JWT, OAuth, sessions)
- Authorization model (RBAC, ABAC)
- Data encryption (at-rest, in-transit)
- Audit logging

**Discovery locations**:
- Auth middleware/services
- Security configurations
- Environment variables (patterns, not values)
- Security-related ADRs
- Input validation schemas

#### REL (Reliability)
**Signals to look for**:
- Error handling patterns
- Retry logic and circuit breakers
- Health check endpoints
- Graceful degradation strategies

**Discovery locations**:
- Error handlers
- HTTP client configurations
- Health check routes
- Observability setup
- Runbooks/playbooks

#### DATA (Data)
**Signals to look for**:
- Data models and schemas
- Migration patterns
- Data validation rules
- Storage technologies

**Discovery locations**:
- Schema definitions
- Migration files
- Model/entity directories
- Database configurations
- ORM configurations

#### INT (Integration)
**Signals to look for**:
- API contracts (REST, GraphQL, gRPC)
- Message formats (JSON, Protobuf)
- External service integrations
- Webhook patterns

**Discovery locations**:
- OpenAPI/Swagger specs
- Proto files
- API route definitions
- Integration tests
- Client SDK configurations

#### OPS (Operations)
**Signals to look for**:
- Build and deployment processes
- CI/CD pipelines
- Monitoring and alerting
- Logging patterns

**Discovery locations**:
- Makefile, package.json scripts
- CI/CD configs (.github/workflows/, .gitlab-ci.yml)
- Docker/Kubernetes configs
- Monitoring configurations

#### MAINT (Maintainability)
**Signals to look for**:
- Code style and linting rules
- Naming conventions
- File organization patterns
- Documentation standards

**Discovery locations**:
- Linter configurations
- Editor configurations
- CONTRIBUTING.md
- Code comments and docstrings
- Existing documentation

#### TEST (Testing)
**Signals to look for**:
- Test framework and runners
- Test organization patterns
- Coverage requirements
- Test fixtures and factories

**Discovery locations**:
- Test directories
- Test configuration files
- CI test stages
- Coverage reports
- Test utilities

#### COMPL (Compliance)
**Signals to look for**:
- Regulatory requirements (GDPR, HIPAA, SOC2)
- Industry standards
- Audit trail requirements
- Data retention policies

**Discovery locations**:
- Compliance documentation
- Privacy policies
- Audit log implementations
- Data retention configs
- Legal/compliance ADRs

#### UX (Usability)
**Signals to look for**:
- UI component libraries
- Accessibility patterns
- Internationalization setup
- User feedback mechanisms

**Discovery locations**:
- UI component directories
- Accessibility tests
- i18n configurations
- User-facing error messages

#### BIZ (Business)
**Signals to look for**:
- Domain terminology
- Business rules and logic
- Entity relationships
- Invariants and constraints

**Discovery locations**:
- Domain model documentation
- Business logic implementations
- Validation rules
- Glossaries
- PRD/requirements docs

### Conditional Spec Creation

Not all specs apply to all projects. Use these rules:

| Spec | Create When | Skip When |
|------|-------------|-----------|
| `security.md` | Handles user data, auth, or sensitive info | Internal tool, no user data |
| `compliance.md` | Regulated industry, PII, financial data | Internal dev tool |
| `performance.md` | User-facing with SLAs, high-load system | Internal tool, no SLAs |
| `reliability.md` | Production system, uptime requirements | Prototype, dev tool |
| `data-governance.md` | Stores user data, has retention needs | Stateless service |
| `api-contracts.md` | Exposes or consumes APIs | Self-contained tool |

### Spec File Quality Criteria

Each spec file MUST include:
1. **Source reference**: Where the information came from
2. **Last Updated date**: When the spec was last verified
3. **Scope**: What systems/components this spec applies to
4. **Actionable guidance**: Not just description, but what to do

**Minimal spec structure**:
```markdown
# {Spec Name}

## Overview
{Brief description of what this spec covers}

## {Content Sections}
{Domain-specific content}

---

**Source**: {Where this was discovered/derived from}
**Last Updated**: {Date}
```

---

## Validation Criteria

**See [Consolidated Validation Checklist](#consolidated-validation-checklist)** for complete validation criteria.

Quick reference:
- **Phase 1 (Bootstrap)**: Checks 1.1-1.10
- **Phase 2 (Evolved)**: Checks 2.1-2.15
- **Final**: Checks F.1-F.4

---

## Spec File Structure

Each spec file MUST include:

1. **Header**: Version, Purpose, Scope
2. **Content sections**: Specific to spec type
3. **Validation criteria**: Checklist for agent self-verification
4. **Examples**: Valid/invalid examples with checkmarks

---

## Error Handling

### Missing Referenced Files

**If adapter example file not found** (`../.cypilot-adapter/AGENTS.md`):
```
⚠️ Example not found: {path}
→ Proceed without example (reduced quality assurance)
```
**Action**: WARN and continue.

**If spec file referenced in AGENTS.md doesn't exist**:
```
⚠️ Orphaned WHEN rule: {spec-file} not found
→ Create spec file OR remove WHEN rule from AGENTS.md
```
**Action**: Validation FAIL — orphaned references must be resolved.

### Validation Failures

**If Phase 1 validation fails**:
1. Check AGENTS.md exists at adapter path
2. Verify `**Extends**:` declaration present
3. Verify Extends path points to valid Cypilot AGENTS.md

**If Phase 2 validation fails**:
1. Identify which spec files are missing
2. Run `/cypilot-adapter --rescan` to regenerate
3. For each failed check, see [Consolidated Validation Checklist](#consolidated-validation-checklist)

**Recovery**: After fixing issues, re-run `/cypilot-analyze` to confirm resolution.

---

## Consolidated Validation Checklist

**Use this single checklist for all adapter validation** (replaces scattered criteria above).

### Phase 1: Bootstrap (Minimal Adapter)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| 1.1 | `{project-root}/.cypilot-config.json` exists at project root | YES | File exists check |
| 1.2 | `{project-root}/.cypilot-config.json` is valid JSON | YES | JSON parse succeeds |
| 1.3 | `cypilotAdapterPath` field present | YES | Field exists in JSON |
| 1.4 | Adapter path points to directory with AGENTS.md | YES | Path + `AGENTS.md` exists |
| 1.5 | AGENTS.md has project name heading | YES | `# Cypilot Adapter: {name}` present |
| 1.6 | AGENTS.md has `**Extends**:` declaration | YES | Pattern match |
| 1.7 | Extends path resolves to valid file | YES | File exists at path |
| 1.8 | No PRD content in adapter | YES | No problem/solution/scope sections |
| 1.9 | No ADR rationale in adapter | YES | No decision rationale sections |
| 1.10 | No spec specs in adapter | YES | No requirement IDs or flows |

### Phase 2: Evolved Adapter (with specs)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| 2.1 | All Phase 1 checks pass | YES | Run Phase 1 first |
| 2.2 | Version field present | YES | `**Version**:` in AGENTS.md |
| 2.3 | Last Updated field present | YES | `**Last Updated**:` in AGENTS.md |
| 2.4 | Project Overview section present | YES | Project description exists |
| 2.5 | WHEN rules use action-based format | YES | Pattern: `WHEN {verb}ing ...` (action description) |
| 2.6 | No orphaned WHEN rules | YES | All referenced specs exist |
| 2.7 | tech-stack.md complete | CONDITIONAL | If tech stack defined in DESIGN |
| 2.8 | domain-model.md complete | CONDITIONAL | If domain model in DESIGN |
| 2.9 | api-contracts.md complete | CONDITIONAL | If API defined in DESIGN |
| 2.10 | patterns.md has ≥1 pattern | CONDITIONAL | If patterns in DESIGN/ADR |
| 2.11 | conventions.md complete | CONDITIONAL | If codebase exists |
| 2.12 | build-deploy.md complete | CONDITIONAL | If build config exists |
| 2.13 | testing.md complete | CONDITIONAL | If test infra exists |
| 2.14 | Each spec has source reference | YES | "Source:" field in each spec |
| 2.15 | Consistent with DESIGN.md | YES | Cross-reference check |

### Final Verification

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| F.1 | Agent used template for generation | YES | Template path appears in agent context/logs |
| F.2 | Agent referenced example for validation | YES | Example path appears in agent context/logs |
| F.3 | Phase-appropriate validation applied | YES | Phase 1 OR Phase 2 checklist completed |
| F.4 | All applicable checks pass | YES | No FAIL status in checklist results |

---

## Common Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Missing Extends | Validation fails at 1.6 | Add `**Extends**: \`{path}/Cypilot/AGENTS.md\`` |
| Legacy WHEN format | Validation fails at 2.5 | Convert to action-based: `WHEN writing code, ...` |
| Orphaned WHEN rules | Validation fails at 2.6 | Create missing spec OR remove rule |
| Inconsistent tech refs | Spec conflicts with DESIGN | Update spec to match DESIGN source of truth |
| Missing spec files | Validation fails at 2.7-2.13 | Run `/cypilot-adapter --rescan` to generate |
| PRD content in adapter | Validation fails at 1.8 | Move to PRD artifact |

---

## References

**Example (this repo)**: `../.cypilot-adapter/AGENTS.md`

**Related**:
- `../AGENTS.md` — Core Cypilot requirements
- `workflow-requirements.md` — Workflow structure requirements
