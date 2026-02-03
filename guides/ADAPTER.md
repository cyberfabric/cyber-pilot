# Spider Adapter Creation Guide

## Core Principle

Adapters extend Spider with project-specific context. Start files with:

```text
Extends: ../Spider/path/to/file.md
```

**You can override/add anything EXCEPT the immutable rules below.**

---

## Immutable Rules (NEVER Override)

These are validated by tooling and cannot be changed:

### 1. Design Hierarchy
```
ADAPTER → PRD CONTEXT → OVERALL DESIGN → FEATURE DESIGN → CODE
```
Must reference parent level, never contradict.

- **ADAPTER**: Defines tech stack, formats, conventions (first step, required)
- **PRD CONTEXT**: Defines actors, capabilities, product requirements
- **OVERALL DESIGN**: Architecture, domain model, API contracts
- **FEATURE DESIGN**: Actor flows, algorithms, requirements
- **CODE**: Implementation following feature design

### 2. Mandatory Spider Rules
- Actor Flows (Section B) are PRIMARY - always start from what actors do
- Use Spider DSL (SDSL) for flows/algorithms/states - NEVER code in DESIGN.md
- Never redefine types - reference domain model from Overall Design
- Validate before proceeding (Overall ≥90/100, Feature 100/100)
- Feature size limits: ≤3000 lines (recommended), ≤4000 (hard limit)
- Design is source of truth - if code contradicts design, fix design first

### 3. File Structure
```
architecture/
├── DESIGN.md                    # Overall Design
└── features/
    ├── DECOMPOSITION.md              # Feature manifest
    └── feature-{slug}/
        ├── DESIGN.md            # Feature Design
```

### 4. DESIGN.md Sections
**Overall Design**:
- Section A: PRD
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
- Section F: Requirements (formalized scope + Testing Scenarios in Spider DSL (SDSL))

### 5. Validation Scores
- Overall Design: ≥90/100
- Feature Design: 100/100 + 100% completeness

---

## What Adapters Define

Everything else is adapter-specific. Define as needed:

**Note**: All Spider operation workflows now support **CREATE and UPDATE modes**. Adapters can be created once and updated anytime as project evolves. Use `adapter.md` workflow to create or update your adapter.

### Tech Stack

Example location (in your adapter):

```text
.spider-adapter/specs/tech-stack.md
```
- Primary language and version
- Frameworks (backend, frontend)
- Database type and version
- Additional services (cache, message queue, search)
- Development tools (package manager, build tool, linter, formatter)

### Domain Model Format

Example location (in your adapter):

```text
.spider-adapter/specs/domain-model.md
```
- Technology (TypeScript, JSON Schema, Protobuf, GTS, etc.)
- Location (`architecture/domain-model/`, per-feature, etc.)
- DML syntax (`@DomainModel.TypeName` for clickable references)
- Validation commands
- Naming conventions
- Traceability requirements (clickable links from Feature→Overall)

### API Contract Format

Example location (in your adapter):

```text
.spider-adapter/specs/api-contracts.md
```
- Technology (OpenAPI, GraphQL, gRPC, CLISPEC, etc.)
- Location (`architecture/api-specs/`, `architecture/cli-specs/`, etc.)
- Linking syntax (`@API.GET:/path`, `@CLI.command-name`, `@Feature.{slug}` for clickable references)
- Validation commands
- API conventions
- Traceability requirements (clickable links from Feature→Overall)

**Note**: For CLI tools, consider using **CLISPEC** - a built-in, simple format for CLI command documentation. See `../CLISPEC.md`.

### Patterns & Architecture

Example location (in your adapter):

```text
.spider-adapter/specs/patterns.md
```
- Architecture style (layered, hexagonal, microservices, etc.)
- Core design patterns (DI, repository, error handling, etc.)
- Anti-patterns to avoid
- Module organization guidelines

### Code Conventions

Example location (in your adapter):

```text
.spider-adapter/specs/conventions.md
```
- Naming conventions (files, directories, variables, functions, classes)
- Code style (indentation, line length, braces, imports)
- Documentation requirements
- Error handling patterns

### Testing Strategy

Example location (in your adapter):

```text
.spider-adapter/specs/testing.md
```
- Test frameworks (unit, integration, E2E)
- Test organization and structure
- Coverage requirements
- Mocking strategy
- Test commands

### Build & Deployment

Example location (in your adapter):

```text
.spider-adapter/specs/build-deploy.md
```
- Build tool and commands
- Development environment setup
- CI/CD pipeline configuration
- Deployment strategy and environments
- Database migrations

### Linting

Example location (in your adapter):

```text
.spider-adapter/specs/linting.md
```
- Linter configuration
- Formatting tools
- Pre-commit hooks
- CI integration
- Custom lint rules

### Security

Example location (in your adapter):

```text
.spider-adapter/specs/security.md
```
- Authentication and authorization strategy
- Input validation requirements
- Data protection (encryption, sensitive data handling)
- API security (rate limiting, CORS, headers)
- Secrets management
- Security testing

### Performance

Example location (in your adapter):

```text
.spider-adapter/specs/performance.md
```
- Performance requirements and SLAs
- Benchmarking strategy and tools
- Profiling guidelines
- Optimization best practices
- Caching strategies
- Resource usage limits

### Project Structure

Example location (in your adapter):

```text
.spider-adapter/specs/project-structure.md
```
- Directory organization
- File naming conventions
- Spider artifact locations
- Source code structure
- Test and documentation locations

### Additional Specs (as needed)

Examples (in your adapter):

```text
.spider-adapter/specs/rest-api-guidelines.md
.spider-adapter/specs/graphql-guidelines.md
.spider-adapter/specs/architectural-lints.md
.spider-adapter/specs/module-creation.md
.spider-adapter/specs/rust-guidelines.md
.spider-adapter/specs/typescript-guidelines.md
```

**Required in all spec files**:
- **Validation checklist**: Agent self-verification criteria
- **Examples**: Valid ✅ and invalid ❌ examples
- **Commands**: Concrete, cross-platform verification commands

**Validation output format**: MUST be chat output only, NO report files

### Behavior Description Language (Optional Override)
- **Default**: Spider DSL (SDSL) for flows/algorithms/states
- **Can override**: Create custom behavior specification in `{adapter-directory}/`
- **Example**:

```text
Replace: {Spider}/requirements/SDSL.md
With:    {project-root}/.spider-adapter/CustomBDL.md
```
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
{project-root}/
├── .spider-adapter/                 # Your project-specific extensions (at root level)
│   ├── AGENTS.md                # Navigation rules (WHEN executing workflows: ...)
│   └── specs/                   # Detailed specifications
│       ├── tech-stack.md        # Languages, frameworks, databases, versions
│       ├── domain-model.md      # Domain model format and location
│       ├── api-contracts.md     # API contract format and location
│       ├── patterns.md          # Architecture patterns and design principles
│       ├── conventions.md       # Coding standards and naming rules
│       ├── testing.md           # Testing frameworks and commands
│       ├── build-deploy.md      # Build and deployment commands
│       ├── linting.md           # Linting rules and tools
│       ├── security.md          # Security requirements and practices
│       ├── performance.md       # Performance requirements and optimization
│       └── project-structure.md # Directory structure and organization
└── Spider/                         # Core Spider (as git submodule or direct copy)
```

**Important**: .spider-adapter MUST be at project root level, discoverable from `{project-root}/.spider-adapter/`

**Alternative locations** (if needed):
- `{project-root}/guidelines/.spider-adapter/`
- `{project-root}/spec/.spider-adapter/`
- `{project-root}/docs/.spider-adapter/`

**Avoid**: Deep nesting like `{project-root}/guidelines/subfolder/.spider-adapter/` ❌

**Common spec files** (create as needed):
- **Core**: tech-stack, domain-model, api-contracts, conventions, testing, build-deploy
- **Quality**: linting, security, performance, architectural-lints
- **Structure**: project-structure, patterns, module-creation
- **API-specific**: rest-api-guidelines, graphql-guidelines, cli-spec

---

## Template: AGENTS.md

```markdown
# Spider Adapter: {Project Name}

**Extends**: `../../Spider/AGENTS.md`

**Version**: 1.0  
**Status**: COMPLETE  
**Last Updated**: YYYY-MM-DD

---

ALWAYS open and follow `specs/domain-model.md` WHEN executing workflows: design.md, design-validate.md, adr.md, adr-validate.md, features.md, features-validate.md, feature.md, feature-validate.md, code-validate.md

ALWAYS open and follow `specs/api-contracts.md` WHEN executing workflows: design.md, design-validate.md, adr.md, adr-validate.md, feature.md, feature-validate.md, code-validate.md

ALWAYS open and follow `specs/testing.md` WHEN executing workflows: code-validate.md

ALWAYS open and follow `specs/build-deploy.md` WHEN executing workflows: code-validate.md

ALWAYS open and follow `specs/project-structure.md` WHEN executing workflows: adapter.md, adapter-auto.md, adapter-manual.md, adapter-bootstrap.md, adapter-agents.md, adapter-validate.md, prd.md, prd-validate.md, design.md, design-validate.md, adr.md, adr-validate.md, features.md, features-validate.md, feature.md, feature-validate.md

ALWAYS open and follow `specs/conventions.md` WHEN executing workflows: adapter.md, adapter-auto.md, adapter-manual.md, adapter-bootstrap.md, adapter-validate.md, code-validate.md
```

**Example spec file** (in your adapter):

```text
.spider-adapter/specs/domain-model.md
```
```markdown
# Domain Model Specification

**Technology**: TypeScript  
**Location**: `architecture/domain-model/types.ts`  
**Format**: TypeScript interfaces and types

## Type Identifier Syntax

Use `@DomainModel.TypeName` for clickable references in DESIGN.md files.

**Example**:
```typescript
export interface User {
  id: string;
  name: string;
}
```

Reference as: `@DomainModel.User`

## Validation

**Command**: `tsc --noEmit`  
**Expected**: No type errors

## Traceability

All Feature DESIGN.md files MUST use clickable links to domain model types.
```

**Example spec file** (`specs/tech-stack.md`):
```markdown
# Tech Stack Specification

**Primary Language**: Rust 1.75+  
**Backend Framework**: Axum 0.7  
**Database**: PostgreSQL 15 with SQLx  
**Caching**: Redis 7

## Testing Tools
- Unit tests: `cargo test`
- Integration tests: `cargo test --test '*'`
- E2E tests: Custom test framework

## Build Commands
- Build: `cargo build --release`
- Lint: `cargo clippy -- -D warnings`
- Format: `cargo fmt --check`
```

---
