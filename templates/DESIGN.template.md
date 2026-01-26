# Technical Design: {PROJECT_NAME}

## A. Architecture Overview

### Architectural Vision

{2-3 paragraphs describing the technical approach, key architectural decisions, and design philosophy}

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-{project-name}-{kind}-{slug}` | {short description of how to solve} |

### Architecture Layers

<!-- TODO: Add architecture diagram (draw.io, Mermaid, or embedded image) -->

| Layer | Responsibility | Technology |
|-------|---------------|------------|
| Presentation | {description} | {tech} |
| Application | {description} | {tech} |
| Domain | {description} | {tech} |
| Infrastructure | {description} | {tech} |

## B. Principles & Constraints

### B.1: Design Principles

#### {Principle Name}

**ID**: `fdd-{project-name}-principle-{principle-slug}`

<!-- fdd-id-content -->
**ADRs**: `fdd-{project-name}-adr-{adr-slug}`

{Description of the principle and why it matters}
<!-- fdd-id-content -->

<!-- TODO: Add more design principles as needed -->

### B.2: Constraints

#### {Constraint Name}

**ID**: `fdd-{project-name}-constraint-{constraint-slug}`

<!-- fdd-id-content -->
**ADRs**: `fdd-{project-name}-adr-{adr-slug}`

{Description of the constraint and its impact}
<!-- fdd-id-content -->

<!-- TODO: Add more constraints as needed -->

## C. Technical Architecture

### C.1: Domain Model

**Technology**: {GTS | JSON Schema | OpenAPI | TypeScript}
**Location**: [{domain-model-file}]({path/to/domain-model})

**Core Entities**:
- [{EntityName}]({path/to/entity.schema}) - {Description}

**Relationships**:
- {Entity1} → {Entity2}: {Relationship description}

### C.2: Component Model

<!-- TODO: Add component diagram (draw.io, Mermaid, or ASCII) -->

**Components**:
- **{Component 1}**: {Purpose and responsibility}
- **{Component 2}**: {Purpose and responsibility}

**Interactions**:
- {Component 1} → {Component 2}: {Description of interaction}

### C.3: API Contracts

**Technology**: {REST/OpenAPI | GraphQL | gRPC | CLISPEC}
**Location**: [{api-spec-file}]({path/to/api-spec})

**Endpoints Overview**:
- `{METHOD} {/path}` - {Description}

### C.4: Interactions & Sequences

Sequence diagrams for the most important flows.

Use cases: FDD ID from PRD.

Actors: FDD ID from PRD.

### C.5 Database schemas & tables (optional)

#### Table {name}

ID: `fdd-{project-name}-db-table-{slug}`

Schema

| Column | Type | Description |
|--------|------|-------------|

PK:

Constraints

Additional info

Example

| Col name A | B | C |
|------------|---|---|
| values     |   |   |

### C.6: Topology (optional)

Physical view, files, pods, containers, DC, virtual machines, etc.

**ID**: `fdd-{project-name}-topology-{slug}`

### C.7: Tech stack (optional)

**ID**: `fdd-{project-name}-tech-{slug}`

## D. Additional Context

**ID**: `fdd-{project-name}-design-context-{slug}`

<!-- TODO: Add any additional technical context, architect notes, rationale, etc. -->
<!-- This section is optional and not validated by FDD -->
