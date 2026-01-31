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
## A. Architecture Overview

<!-- fdd:###:architectural-vision -->
### Architectural Vision

<!-- fdd:paragraph:architectural-vision-body -->
{1-3 paragraphs describing the architecture at a high level.}

{Include:
- system boundaries
- major responsibilities
- what drives the chosen architecture}
<!-- fdd:paragraph:architectural-vision-body -->
<!-- fdd:###:architectural-vision -->

<!-- fdd:###:architecture-drivers -->
### Architecture drivers

<!-- fdd:####:prd-requirements -->
#### Product requirements

<!-- fdd:table:prd-requirements required="true" -->
| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-{project}-fr-{slug}` | {How the design addresses this requirement} |
| `fdd-{project}-nfr-{slug}` | {How the design addresses this NFR} |
<!-- fdd:table:prd-requirements -->
<!-- fdd:####:prd-requirements -->

<!-- fdd:####:adr-records -->
#### Architecture Decisions Records

<!-- fdd:table:adr-records required="true" -->
| FDD ADR ID | Summary |
|------------|---------|
| `fdd-{project}-adr-{slug}` | {2-4 sentences describing what decision was taken and why. Include key tradeoffs if relevant.} |
| `fdd-{project}-adr-{slug}` | {2-4 sentences describing what decision was taken and why. Include key tradeoffs if relevant.} |
<!-- fdd:table:adr-records -->
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
## B. Principles & Constraints

<!-- fdd:###:principles -->
### B.1: Design Principles

<!-- fdd:####:principle-title repeat="many" -->
#### {Principle Name}

<!-- fdd:id:principle has="priority,task" covered_by="features,feature" -->
**ID**: [ ] `p1` - `fdd-{project}-principle-{slug}`
<!-- fdd:id:principle -->

<!-- fdd:paragraph:principle-body -->
{Rationale and guidance.}
<!-- fdd:paragraph:principle-body -->
<!-- fdd:####:principle-title repeat="many" -->
<!-- fdd:###:principles -->

<!-- fdd:###:constraints -->
### B.2: Constraints

<!-- fdd:####:constraint-title repeat="many" -->
#### {Constraint Name}

<!-- fdd:id:constraint has="priority,task" covered_by="features,feature" -->
**ID**: [ ] `p1` - `fdd-{project}-constraint-{slug}`
<!-- fdd:id:constraint -->

<!-- fdd:paragraph:constraint-body -->
{What constraint exists and why.}
<!-- fdd:paragraph:constraint-body -->
<!-- fdd:####:constraint-title repeat="many" -->
<!-- fdd:###:constraints -->
<!-- fdd:##:principles-and-constraints -->

<!-- fdd:##:technical-architecture -->
## C. Technical Architecture

<!-- fdd:###:domain-model -->
### C.1: Domain Model

<!-- fdd:paragraph:domain-model -->
{Describe domain entities, invariants, and relationships.}
<!-- fdd:paragraph:domain-model -->
<!-- fdd:###:domain-model -->

<!-- fdd:###:component-model -->
### C.2: Component Model

<!-- fdd:code:component-model -->
```mermaid
%% Add component diagram here
```
<!-- fdd:code:component-model -->

<!-- fdd:####:component-title repeat="many" -->
#### {Component Name}

<!-- fdd:id:component has="priority,task" covered_by="features,feature" -->
**ID**: [ ] `p1` - `fdd-{project}-component-{component-slug}`
<!-- fdd:id:component -->

<!-- fdd:list:component-payload -->
- Responsibilities
- Boundaries
- Dependencies
- Key interfaces
<!-- fdd:list:component-payload -->
<!-- fdd:####:component-title repeat="many" -->
<!-- fdd:###:component-model -->

<!-- fdd:###:api-contracts -->
### C.3: API Contracts

<!-- fdd:paragraph:api-contracts -->
{Describe public APIs, contracts, and integration boundaries.}
<!-- fdd:paragraph:api-contracts -->
<!-- fdd:###:api-contracts -->

<!-- fdd:###:interactions -->
### C.4: Interactions & Sequences

<!-- fdd:####:sequence-title repeat="many" -->
#### {Sequence Name}

<!-- fdd:id:seq has="priority,task" covered_by="features,feature" -->
**ID**: [ ] `p1` - `fdd-{project}-seq-{slug}`
<!-- fdd:id:seq -->

<!-- fdd:code:sequences -->
```mermaid
%% Add sequence diagrams here
```
<!-- fdd:code:sequences -->

<!-- fdd:paragraph:sequence-body -->
{Explain the interaction, participants, and success/failure outcomes.}
<!-- fdd:paragraph:sequence-body -->
<!-- fdd:####:sequence-title repeat="many" -->
<!-- fdd:###:interactions -->

<!-- fdd:###:database -->
### C.5 Database schemas & tables (optional)

<!-- fdd:####:db-table-title repeat="many" -->
#### Table {name}

<!-- fdd:id:db-table has="priority,task" covered_by="features,feature" -->
**ID**: [ ] `p1` - `fdd-{project-name}-db-table-{slug}`
<!-- fdd:id:db-table -->

Schema
<!-- fdd:table:db-table-schema -->
| Column | Type | Description |
|--------|------|-------------|
<!-- fdd:table:db-table-schema -->

PK:

Constraints

Additional info

Example
<!-- fdd:table:db-table-example -->
| Col name A | B | C |
|------------|---|---|
| values     |   |   |
<!-- fdd:table:db-table-example -->
<!-- fdd:####:db-table-title repeat="many" -->
<!-- fdd:###:database -->

<!-- fdd:###:topology -->
### C.6: Topology (optional)

<!-- fdd:id:topology has="task" -->
**ID**: [ ] `fdd-{project-name}-topology-{slug}`
<!-- fdd:id:topology -->

<!-- fdd:paragraph:topology-body -->
Physical view, files, pods, containers, DC, virtual machines, etc.
<!-- fdd:paragraph:topology-body -->
<!-- fdd:###:topology -->

<!-- fdd:###:tech-stack -->
### C.7: Tech stack (optional)

<!-- fdd:paragraph:status -->
**Status**: Proposed | Rejected | Accepted | Deprecated | Superseded
<!-- fdd:paragraph:status -->

<!-- fdd:paragraph:tech-body -->
{Describe tech choices and rationale.}
<!-- fdd:paragraph:tech-body -->
<!-- fdd:###:tech-stack -->
<!-- fdd:##:technical-architecture -->

<!-- fdd:##:design-context -->
## D. Additional Context

<!-- fdd:paragraph:design-context-body -->
{Optional notes, rationale, trade-offs, and links.}
<!-- fdd:paragraph:design-context-body -->

<!-- fdd:paragraph:date -->
**Date**: {YYYY-MM-DD}
<!-- fdd:paragraph:date -->
<!-- fdd:##:design-context -->

<!-- fdd:#:design -->
