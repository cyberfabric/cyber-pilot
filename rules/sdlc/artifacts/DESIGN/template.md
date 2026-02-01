---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: DESIGN
  unknown_sections: warn
---

<!-- fdd:#:design -->
# Technical Design: {PROJECT_NAME}

<!-- fdd:##:architecture-overview -->
## 1. Architecture Overview

<!-- fdd:###:architectural-vision -->
### Architectural Vision

<!-- fdd:architectural-vision-body -->
{1-3 paragraphs describing the architecture at a high level.}

{Include:
- system boundaries
- major responsibilities
- what drives the chosen architecture}
<!-- fdd:architectural-vision-body -->
<!-- fdd:###:architectural-vision -->

<!-- fdd:###:architecture-drivers -->
### Architecture drivers

<!-- fdd:####:prd-requirements -->
#### Product requirements

<!-- fdd:fr-title repeat="many" -->
##### {FR Name}

<!-- fdd:id-ref:fr has="priority,task" -->
[ ] `p1` - `fdd-{system}-fr-{slug}`
<!-- fdd:id-ref:fr -->

**Solution**: {How the design addresses this requirement}
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:nfr-title repeat="many" -->
##### {NFR Name}

<!-- fdd:id-ref:nfr has="priority,task" -->
[ ] `p1` - `fdd-{system}-nfr-{slug}`
<!-- fdd:id-ref:nfr -->

**Solution**: {How the design addresses this NFR}
<!-- fdd:nfr-title -->
<!-- fdd:####:prd-requirements -->

<!-- fdd:####:adr-records -->
#### Architecture Decisions Records

<!-- fdd:adr-title repeat="many" -->
##### {ADR Title}

<!-- fdd:id-ref:adr has="priority,task" -->
[ ] `p1` - `fdd-{system}-adr-{slug}`
<!-- fdd:id-ref:adr -->

{2-4 sentences describing what decision was taken and why. Include key tradeoffs if relevant.}
<!-- fdd:adr-title -->
<!-- fdd:####:adr-records -->
<!-- fdd:###:architecture-drivers -->

<!-- fdd:###:architecture-layers -->
### Architecture Layers

<!-- TODO: Add architecture diagram (draw.io, Mermaid, or embedded image) -->

<!-- fdd:table:architecture-layers -->
| Layer | Responsibility | Technology |
|-------|---------------|------------|
| {layer} | {responsibility} | {tech} |
<!-- fdd:table:architecture-layers -->
<!-- fdd:###:architecture-layers -->
<!-- fdd:##:architecture-overview -->

<!-- fdd:##:principles-and-constraints -->
## 2. Principles & Constraints

<!-- fdd:###:principles -->
### 2.1: Design Principles

<!-- fdd:####:principle-title repeat="many" -->
#### {Principle Name}

<!-- fdd:id:principle has="priority,task" covered_by="FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-{system}-principle-{slug}`

<!-- fdd:paragraph:principle-body -->
{Rationale and guidance.}
<!-- fdd:paragraph:principle-body -->
<!-- fdd:id:principle -->
<!-- fdd:####:principle-title repeat="many" -->
<!-- fdd:###:principles -->

<!-- fdd:###:constraints -->
### 2.2: Constraints

<!-- fdd:####:constraint-title repeat="many" -->
#### {Constraint Name}

<!-- fdd:id:constraint has="priority,task" covered_by="FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-{system}-constraint-{slug}`

<!-- fdd:paragraph:constraint-body -->
{What constraint exists and why.}
<!-- fdd:paragraph:constraint-body -->
<!-- fdd:id:constraint -->
<!-- fdd:####:constraint-title repeat="many" -->
<!-- fdd:###:constraints -->
<!-- fdd:##:principles-and-constraints -->

<!-- fdd:##:technical-architecture -->
## 3. Technical Architecture

<!-- fdd:###:domain-model -->
### 3.1: Domain Model

<!-- fdd:paragraph:domain-model -->
{Describe domain entities, invariants, and relationships.}
<!-- fdd:paragraph:domain-model -->
<!-- fdd:###:domain-model -->

<!-- fdd:###:component-model -->
### 3.2: Component Model

<!-- fdd:code:component-model -->
```mermaid
%% Add component diagram here
```
<!-- fdd:code:component-model -->

<!-- fdd:####:component-title repeat="many" -->
#### {Component Name}

<!-- fdd:id:component has="priority,task" covered_by="FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-{system}-component-{component-slug}`

<!-- fdd:list:component-payload -->
- Responsibilities
- Boundaries
- Dependencies
- Key interfaces
<!-- fdd:list:component-payload -->
<!-- fdd:id:component -->
<!-- fdd:####:component-title repeat="many" -->
<!-- fdd:###:component-model -->

<!-- fdd:###:api-contracts -->
### 3.3: API Contracts

<!-- fdd:paragraph:api-contracts -->
{Describe public APIs, contracts, and integration boundaries.}
<!-- fdd:paragraph:api-contracts -->
<!-- fdd:###:api-contracts -->

<!-- fdd:###:interactions -->
### 3.4: Interactions & Sequences

<!-- fdd:####:sequence-title repeat="many" -->
#### {Sequence Name}

<!-- fdd:id:seq has="priority,task" covered_by="FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-{system}-seq-{slug}`

<!-- fdd:code:sequences -->
```mermaid
%% Add sequence diagrams here
```
<!-- fdd:code:sequences -->

<!-- fdd:paragraph:sequence-body -->
{Explain the interaction, participants, and success/failure outcomes.}
<!-- fdd:paragraph:sequence-body -->
<!-- fdd:id:seq -->
<!-- fdd:####:sequence-title repeat="many" -->
<!-- fdd:###:interactions -->

<!-- fdd:###:database -->
### 3.5 Database schemas & tables (optional)

<!-- fdd:####:db-table-title repeat="many" -->
#### Table {name}

<!-- fdd:id:dbtable has="priority,task" covered_by="FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-{system}-dbtable-{slug}`

**Schema**
<!-- fdd:table:db-table-schema -->
| Column | Type | Description |
|--------|------|-------------|
<!-- fdd:table:db-table-schema -->

**PK**: { Primary key or composite key (if composite, list columns) }

**Constraints**: { Any constraints (unique, check, etc.) }

**Additional info**: { Any additional info }

**Example**
<!-- fdd:table:db-table-example -->
| Col name A | B | C |
|------------|---|---|
| values     |   |   |
<!-- fdd:table:db-table-example -->
<!-- fdd:id:dbtable -->
<!-- fdd:####:db-table-title repeat="many" -->
<!-- fdd:###:database -->

<!-- fdd:###:topology -->
### 3.6: Topology (optional)

<!-- fdd:id:topology has="task" -->
- [ ] **ID**: `fdd-{system}-topology-{slug}`

<!-- fdd:free:topology-body -->
{ Physical view, files, pods, containers, DC, virtual machines, etc. }
<!-- fdd:free:topology-body -->
<!-- fdd:id:topology -->
<!-- fdd:###:topology -->

<!-- fdd:###:tech-stack -->
### 3.7: Tech stack (optional)

<!-- fdd:paragraph:status -->
**Status**: Proposed | Rejected | Accepted | Deprecated | Superseded
<!-- fdd:paragraph:status -->

<!-- fdd:paragraph:tech-body -->
{Describe tech choices and rationale.}
<!-- fdd:paragraph:tech-body -->
<!-- fdd:###:tech-stack -->
<!-- fdd:##:technical-architecture -->

<!-- fdd:##:design-context -->
## 4. Additional Context

<!-- fdd:free:design-context-body -->
{Optional notes, rationale, trade-offs, and links.}
<!-- fdd:free:design-context-body -->

<!-- fdd:paragraph:date -->
**Date**: {YYYY-MM-DD}
<!-- fdd:paragraph:date -->
<!-- fdd:##:design-context -->

<!-- fdd:#:design -->
