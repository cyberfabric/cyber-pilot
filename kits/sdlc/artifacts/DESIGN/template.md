<!-- cpt:#:design -->
# Technical Design: {PROJECT_NAME}

<!-- cpt:##:architecture-overview -->
## 1. Architecture Overview

<!-- cpt:###:architectural-vision -->
### Architectural Vision

<!-- cpt:architectural-vision-body -->
{1-3 paragraphs describing the architecture at a high level.}

{Include:
- system boundaries
- major responsibilities
- what drives the chosen architecture}
<!-- cpt:architectural-vision-body -->
<!-- cpt:###:architectural-vision -->

<!-- cpt:###:architecture-drivers -->
### Architecture drivers

<!-- cpt:####:prd-requirements -->
#### Product requirements

<!-- cpt:fr-title repeat="many" -->
##### {FR Name 1}

<!-- cpt:id-ref:fr has="priority,task" -->
- [ ] `p1` - `cpt-{system}-fr-{slug}`
<!-- cpt:id-ref:fr -->

**Solution**: {How the design addresses this requirement}
<!-- cpt:fr-title repeat="many" -->

<!-- cpt:fr-title repeat="many" -->
##### {FR Name 2}

<!-- cpt:id-ref:fr has="priority,task" -->
- [ ] `p2` - `cpt-{system}-fr-{slug}`
<!-- cpt:id-ref:fr -->

**Solution**: {How the design addresses this requirement}
<!-- cpt:fr-title repeat="many" -->

<!-- cpt:nfr-title repeat="many" -->
##### {NFR Name 1}

<!-- cpt:id-ref:nfr has="priority,task" -->
- [ ] `p1` - `cpt-{system}-nfr-{slug}`
<!-- cpt:id-ref:nfr -->

**Solution**: {How the design addresses this NFR}
<!-- cpt:nfr-title repeat="many" -->

<!-- cpt:nfr-title repeat="many" -->
##### {NFR Name 2}

<!-- cpt:id-ref:nfr has="priority,task" -->
- [ ] `p2` - `cpt-{system}-nfr-{slug}`
<!-- cpt:id-ref:nfr -->

**Solution**: {How the design addresses this NFR}
<!-- cpt:nfr-title repeat="many" -->

<!-- cpt:####:prd-requirements -->

<!-- cpt:####:adr-records -->
#### Architecture Decisions Records

<!-- cpt:adr-title repeat="many" -->
##### {ADR Title 1}

<!-- cpt:id-ref:adr has="priority,task" -->
- [ ] `p1` - `cpt-{system}-adr-{slug}`
<!-- cpt:id-ref:adr -->

{2-4 sentences describing what decision was taken and why. Include key tradeoffs if relevant.}
<!-- cpt:adr-title repeat="many" -->

<!-- cpt:adr-title repeat="many" -->
##### {ADR Title 2}

<!-- cpt:id-ref:adr has="priority,task" -->
- [ ] `p2` - `cpt-{system}-adr-{slug}`
<!-- cpt:id-ref:adr -->

{2-4 sentences describing what decision was taken and why. Include key tradeoffs if relevant.}
<!-- cpt:adr-title repeat="many" -->

<!-- cpt:####:adr-records -->
<!-- cpt:###:architecture-drivers -->

<!-- cpt:###:architecture-layers -->
### Architecture Layers

<!-- cpt:table:architecture-layers -->
| Layer | Responsibility | Technology |
|-------|---------------|------------|
| {layer 1} | {responsibility} | {tech} |
| {layer 2} | {responsibility} | {tech} |
| {layer 3} | {responsibility} | {tech} |
<!-- cpt:table:architecture-layers -->
<!-- cpt:###:architecture-layers -->
<!-- cpt:##:architecture-overview -->

<!-- cpt:##:principles-and-constraints -->
## 2. Principles & Constraints

<!-- cpt:###:principles -->
### 2.1: Design Principles

<!-- cpt:####:principle-title repeat="many" -->
#### {Principle Name 1}

<!-- cpt:id:principle has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `cpt-{system}-principle-{slug}`

<!-- cpt:paragraph:principle-body -->
{Rationale and guidance for this principle.}
<!-- cpt:paragraph:principle-body -->
<!-- cpt:id:principle -->
<!-- cpt:####:principle-title repeat="many" -->

<!-- cpt:####:principle-title repeat="many" -->
#### {Principle Name 2}

<!-- cpt:id:principle has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p2` - **ID**: `cpt-{system}-principle-{slug}`

<!-- cpt:paragraph:principle-body -->
{Rationale and guidance for this principle.}
<!-- cpt:paragraph:principle-body -->
<!-- cpt:id:principle -->
<!-- cpt:####:principle-title repeat="many" -->

<!-- cpt:###:principles -->

<!-- cpt:###:constraints -->
### 2.2: Constraints

<!-- cpt:####:constraint-title repeat="many" -->
#### {Constraint Name 1}

<!-- cpt:id:constraint has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `cpt-{system}-constraint-{slug}`

<!-- cpt:paragraph:constraint-body -->
{What constraint exists and why.}
<!-- cpt:paragraph:constraint-body -->
<!-- cpt:id:constraint -->
<!-- cpt:####:constraint-title repeat="many" -->

<!-- cpt:####:constraint-title repeat="many" -->
#### {Constraint Name 2}

<!-- cpt:id:constraint has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p2` - **ID**: `cpt-{system}-constraint-{slug}`

<!-- cpt:paragraph:constraint-body -->
{What constraint exists and why.}
<!-- cpt:paragraph:constraint-body -->
<!-- cpt:id:constraint -->
<!-- cpt:####:constraint-title repeat="many" -->

<!-- cpt:###:constraints -->
<!-- cpt:##:principles-and-constraints -->

<!-- cpt:##:technical-architecture -->
## 3. Technical Architecture

<!-- cpt:###:domain-model -->
### 3.1: Domain Model

<!-- cpt:paragraph:domain-model -->
{Describe domain entities, invariants, and relationships.}
<!-- cpt:paragraph:domain-model -->
<!-- cpt:###:domain-model -->

<!-- cpt:###:component-model -->
### 3.2: Component Model

<!-- cpt:code:component-model -->
```mermaid
%% Add component diagram here
```
<!-- cpt:code:component-model -->

<!-- cpt:####:component-title repeat="many" -->
#### {Component Name 1}

<!-- cpt:id:component has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `cpt-{system}-component-{slug}`

<!-- cpt:list:component-payload -->
- **Responsibilities**: {what this component does}
- **Boundaries**: {what is in/out of scope}
- **Dependencies**: {other components it depends on}
- **Key interfaces**: {public API or contracts}
<!-- cpt:list:component-payload -->
<!-- cpt:id:component -->
<!-- cpt:####:component-title repeat="many" -->

<!-- cpt:####:component-title repeat="many" -->
#### {Component Name 2}

<!-- cpt:id:component has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p2` - **ID**: `cpt-{system}-component-{slug}`

<!-- cpt:list:component-payload -->
- **Responsibilities**: {what this component does}
- **Boundaries**: {what is in/out of scope}
- **Dependencies**: {other components it depends on}
- **Key interfaces**: {public API or contracts}
<!-- cpt:list:component-payload -->
<!-- cpt:id:component -->
<!-- cpt:####:component-title repeat="many" -->

<!-- cpt:###:component-model -->

<!-- cpt:###:api-contracts -->
### 3.3: API Contracts

<!-- cpt:paragraph:api-contracts -->
{Describe public APIs, contracts, and integration boundaries.}
<!-- cpt:paragraph:api-contracts -->
<!-- cpt:###:api-contracts -->

<!-- cpt:###:interactions -->
### 3.4: Interactions & Sequences

<!-- cpt:####:sequence-title repeat="many" -->
#### {Sequence Name 1}

<!-- cpt:id:seq has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `cpt-{system}-seq-{slug}`

<!-- cpt:code:sequences -->
```mermaid
sequenceDiagram
    participant A as Actor
    participant S as System
    A->>S: Request
    S-->>A: Response
```
<!-- cpt:code:sequences -->

<!-- cpt:paragraph:sequence-body -->
{Explain the interaction, participants, and success/failure outcomes.}
<!-- cpt:paragraph:sequence-body -->
<!-- cpt:id:seq -->
<!-- cpt:####:sequence-title repeat="many" -->

<!-- cpt:####:sequence-title repeat="many" -->
#### {Sequence Name 2}

<!-- cpt:id:seq has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p2` - **ID**: `cpt-{system}-seq-{slug}`

<!-- cpt:code:sequences -->
```mermaid
sequenceDiagram
    participant U as User
    participant API as API
    participant DB as Database
    U->>API: Request
    API->>DB: Query
    DB-->>API: Result
    API-->>U: Response
```
<!-- cpt:code:sequences -->

<!-- cpt:paragraph:sequence-body -->
{Explain the interaction, participants, and success/failure outcomes.}
<!-- cpt:paragraph:sequence-body -->
<!-- cpt:id:seq -->
<!-- cpt:####:sequence-title repeat="many" -->

<!-- cpt:###:interactions -->

<!-- cpt:###:database -->
### 3.5 Database schemas & tables (optional)

<!-- cpt:####:db-table-title repeat="many" -->
#### Table {name 1}

<!-- cpt:id:dbtable has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `cpt-{system}-dbtable-{slug}`

**Schema**
<!-- cpt:table:db-table-schema -->
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Display name |
| created_at | TIMESTAMP | Creation timestamp |
<!-- cpt:table:db-table-schema -->

**PK**: id

**Constraints**: name must be unique

**Additional info**: {Any additional info}

**Example**
<!-- cpt:table:db-table-example -->
| id | name | created_at |
|----|------|------------|
| abc-123 | Example | 2024-01-01 |
<!-- cpt:table:db-table-example -->
<!-- cpt:id:dbtable -->
<!-- cpt:####:db-table-title repeat="many" -->

<!-- cpt:####:db-table-title repeat="many" -->
#### Table {name 2}

<!-- cpt:id:dbtable has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p2` - **ID**: `cpt-{system}-dbtable-{slug}`

**Schema**
<!-- cpt:table:db-table-schema -->
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| status | VARCHAR(50) | Current status |
| updated_at | TIMESTAMP | Last update |
<!-- cpt:table:db-table-schema -->

**PK**: id

**Constraints**: status must be one of: active, inactive, pending

**Additional info**: {Any additional info}

**Example**
<!-- cpt:table:db-table-example -->
| id | status | updated_at |
|----|--------|------------|
| xyz-456 | active | 2024-01-15 |
<!-- cpt:table:db-table-example -->
<!-- cpt:id:dbtable -->
<!-- cpt:####:db-table-title repeat="many" -->

<!-- cpt:###:database -->

<!-- cpt:###:topology -->
### 3.6: Topology (optional)

<!-- cpt:id:topology has="task" -->
- [ ] **ID**: `cpt-{system}-topology-{slug}`

<!-- cpt:free:topology-body -->
{ Physical view, files, pods, containers, DC, virtual machines, etc. }
<!-- cpt:free:topology-body -->
<!-- cpt:id:topology -->
<!-- cpt:###:topology -->

<!-- cpt:###:tech-stack -->
### 3.7: Tech stack (optional)

<!-- cpt:paragraph:status -->
**Status**: Proposed | Rejected | Accepted | Deprecated | Superseded
<!-- cpt:paragraph:status -->

<!-- cpt:paragraph:tech-body -->
{Describe tech choices and rationale.}
<!-- cpt:paragraph:tech-body -->
<!-- cpt:###:tech-stack -->
<!-- cpt:##:technical-architecture -->

<!-- cpt:##:design-context -->
## 4. Additional Context

<!-- cpt:free:design-context-body -->
{Optional notes, rationale, trade-offs, and links.}
<!-- cpt:free:design-context-body -->

<!-- cpt:paragraph:date -->
**Date**: {YYYY-MM-DD}
<!-- cpt:paragraph:date -->
<!-- cpt:##:design-context -->

<!-- cpt:#:design -->
