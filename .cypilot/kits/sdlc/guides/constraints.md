# Constraints (cypilot-sdlc)

Source: `kits/sdlc/constraints.json`

## Legend

- `required` / `optional`: whether the identifier is required in the artifact
- `task`: whether a Task checkbox is required/allowed/prohibited
- `priority`: whether a priority marker is required/allowed/prohibited
- `to_code`: whether the identifier is expected to be carried into CODE
- `references`: downstream constraints (coverage + optional headings anchors)

## Contents

- [PRD](#prd)
- [ADR](#adr)
- [DESIGN](#design)
- [DECOMPOSITION](#decomposition)
- [FEATURE](#feature)

## PRD

**Name**: PRD constraints (cypilot-sdlc)
**Description**: Allowed ID kinds in PRD and required/optional downstream references

### Headings

| id | level | pattern | required | multiple | numbered | description |
| --- | --- | --- | --- | --- | --- | --- |
| prd-h1-title | 1 |  | True | prohibited | allow | PRD document title (H1). |
| prd-overview | 2 | Overview | True | prohibited | allow | High-level overview of the product and problem. |
| prd-overview-purpose | 3 | Purpose | True | prohibited | allow | Purpose of the PRD and the product. |
| prd-overview-background | 3 | Background / Problem Statement | True | prohibited | allow | Background and problem statement. |
| prd-overview-goals | 3 | Goals \(Business Outcomes\) | True | prohibited | allow | Business outcomes and goals. |
| prd-overview-glossary | 3 | Glossary | True | prohibited | allow | Definitions of key terms. |
| prd-actors | 2 | Actors | True | prohibited | allow | Actors (human and system) that interact with the product. |
| prd-actors-human | 3 | Human Actors | True | prohibited | allow | Human actors |
| prd-actors-system | 3 | System Actors | True | prohibited | allow | System and external actors. |
| prd-operational-concept | 2 | Operational Concept & Environment | True | prohibited | allow | Operational concept and environment constraints. |
| prd-scope | 2 | Scope | True | prohibited | allow | Scope of the product and release. |
| prd-scope-in | 3 | In Scope | True | prohibited | allow | In-scope items. |
| prd-scope-out | 3 | Out of Scope | True | prohibited | allow | Out-of-scope items. |
| prd-fr | 2 | Functional Requirements | True | prohibited | allow | Functional requirements section. |
| prd-fr-entry | 3 |  | True | allow | allow | Functional requirement entry heading. |
| prd-nfr | 2 | Non-Functional Requirements | True | prohibited | allow | Non-functional requirements section. |
| prd-nfr-exclusions | 3 | NFR Exclusions | True | prohibited | allow | Explicit non-functional requirement exclusions. |
| prd-public-interfaces | 2 | Public Library Interfaces | True | prohibited | allow | Public library interfaces and integration contracts. |
| prd-public-interfaces-api | 3 | Public API Surface | True | prohibited | allow | Public API surface. |
| prd-public-interfaces-external-contracts | 3 | External Integration Contracts | True | prohibited | allow | External integration contracts. |
| prd-use-cases | 2 | Use Cases | True | prohibited | allow | Use cases section. |
| prd-acceptance-criteria | 2 | Acceptance Criteria | True | prohibited | allow | Acceptance criteria for delivery. |
| prd-dependencies | 2 | Dependencies | True | prohibited | allow | Dependencies required to deliver the PRD. |
| prd-assumptions | 2 | Assumptions | True | prohibited | allow | Assumptions that must hold. |
| prd-risks | 2 | Risks | True | prohibited | allow | Risks and mitigations. |

### Identifiers

| key | kind | name | required | task | priority | to_code | template | headings | references | examples | description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| actor | actor | Actor | False | prohibited | prohibited | false | cpt-{system}-actor-{slug} | prd-actors |  | cpt-cypilot-actor-ai-assistant, cpt-overwork-alert-actor-user, cpt-overwork-alert-actor-macos | An entity (human or system) that interacts with the product; used in PRD, and referenced by requirements/use cases. |
| fr | fr | Functional Requirement | True | allowed | required | false | cpt-{system}-fr-{slug} | prd-fr | DESIGN: coverage=required; task=allowed; priority=allowed; headings=[design-arch-overview-drivers]<br>DECOMPOSITION: coverage=optional; task=allowed; priority=allowed; headings=[decomposition-entry]<br>FEATURE: coverage=optional; task=allowed; priority=allowed; headings=[feature-context-purpose] | cpt-cypilot-fr-validation, cpt-overwork-alert-fr-track-active-time, cpt-overwork-alert-fr-cli-controls | A testable statement of required system behavior (WHAT the system must do). |
| nfr | nfr | Non-functional Requirement | True | allowed | required | false | cpt-{system}-nfr-{slug} | prd-nfr | DESIGN: coverage=required; task=allowed; priority=allowed; headings=[design-arch-overview-drivers]<br>DECOMPOSITION: coverage=optional; task=allowed; priority=allowed; headings=[decomposition-entry]<br>FEATURE: coverage=optional; task=allowed; priority=allowed; headings=[feature-context-purpose] | cpt-cypilot-nfr-validation-performance, cpt-overwork-alert-nfr-privacy-local-only, cpt-overwork-alert-nfr-low-overhead | A measurable quality attribute requirement (performance, security, reliability, usability, etc.). |
| usecase | usecase | Use Case | True | allowed | allowed | false | cpt-{system}-usecase-{slug} | prd-use-cases | DESIGN: coverage=optional; task=allowed; priority=allowed; headings=[design-tech-arch-seq]<br>FEATURE: coverage=optional; task=allowed; priority=allowed; headings=[feature-actor-flow] | cpt-overwork-alert-usecase-run-and-alert, cpt-overwork-alert-usecase-configure-limit, cpt-overwork-alert-usecase-control-session | An end-to-end interaction scenario (actor + goal + flow) that clarifies behavior beyond individual requirements. |
| interface | interface | Public Interface | False | allowed | allowed | false | cpt-{system}-interface-{slug} | prd-public-interfaces | DESIGN: coverage=required; task=allowed; priority=allowed; headings=[design-tech-arch-api-contracts] | cpt-cypilot-interface-cli-json, cpt-overwork-alert-interface-cli, cpt-overwork-alert-interface-ipc-protocol | A public API surface (library interface, protocol, CLI contract) provided by the system. |
| contract | contract | Integration Contract | False | allowed | allowed | false | cpt-{system}-contract-{slug} | prd-public-interfaces | DESIGN: coverage=required; task=allowed; priority=allowed; headings=[design-tech-arch-api-contracts] | cpt-overwork-alert-contract-macos-notification-center, cpt-overwork-alert-contract-launchd, cpt-cypilot-contract-openai-api | An external integration contract (data format/protocol/compatibility expectations) with another system. |

## ADR

**Name**: ADR constraints (cypilot-sdlc)
**Description**: Allowed ID kinds in ADR and required references from DESIGN

### Headings

| id | level | pattern | required | multiple | numbered | description |
| --- | --- | --- | --- | --- | --- | --- |
| adr-h1-title | 1 |  | True | prohibited | allow | ADR document title (H1). |
| adr-context | 2 | Context and Problem Statement | True | prohibited | allow | Problem context and motivating forces. |
| adr-decision-drivers | 2 | Decision Drivers | True | prohibited | allow | Key decision drivers and constraints. |
| adr-considered-options | 2 | Considered Options | True | prohibited | allow | Options that were considered. |
| adr-decision-outcome | 2 | Decision Outcome | True | prohibited | allow | Selected decision and outcome. |
| adr-decision-outcome-consequences | 3 | Consequences | True | prohibited | allow | Consequences of the decision. |
| adr-decision-outcome-confirmation | 3 | Confirmation | True | prohibited | allow | How/when the decision will be confirmed. |
| adr-pros-cons | 2 | Pros and Cons of the Options | True | prohibited | allow | Pros and cons analysis for the options. |
| adr-pros-cons-entry | 3 |  | True | required | allow | A single option evaluation entry (pros/cons). |
| adr-more-info | 2 | More Information | False | prohibited | allow | Optional additional information and links. |
| adr-traceability | 2 | Traceability | False | prohibited | allow | Optional traceability links back to requirements/decisions. |

### Identifiers

| key | kind | name | required | task | priority | to_code | template | headings | references | examples | description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| adr | adr | Architecture Decision Record | True | prohibited | prohibited | false | cpt-{system}-adr-{slug} | adr-h1-title | PRD: coverage=prohibited<br>DESIGN: coverage=required; task=allowed; priority=allowed; headings=[design-arch-overview-drivers] | cpt-cypilot-adr-template-centric-architecture, cpt-overwork-alert-adr-cli-daemon-launchagent, cpt-cypilot-adr-markdown-contract | A documented architecture decision with context, options, outcome, and consequences; referenced from DESIGN. |

## DESIGN

**Name**: DESIGN constraints (cypilot-sdlc)
**Description**: Allowed ID kinds in DESIGN

### Headings

| id | level | pattern | required | multiple | numbered | description |
| --- | --- | --- | --- | --- | --- | --- |
| design-h1-title | 1 |  | True | prohibited | allow | DESIGN document title (H1). |
| design-arch-overview | 2 | Architecture Overview | True | prohibited | allow | Architecture overview section. |
| design-arch-overview-vision | 3 | Architectural Vision | True | prohibited | allow | High-level architectural vision. |
| design-arch-overview-drivers | 3 | Architecture Drivers | True | prohibited | allow | Architecture drivers: requirements, constraints, and ADR links. |
| design-arch-overview-layers | 3 | Architecture Layers | True | prohibited | allow | Architecture layering and responsibilities. |
| design-principles-constraints | 2 | Principles & Constraints | True | prohibited | allow | Principles and constraints section. |
| design-principles | 3 | Design Principles | True | prohibited | allow | Design principles list. |
| design-constraints | 3 | Constraints | True | prohibited | allow | Design constraints list. |
| design-tech-arch | 2 | Technical Architecture | True | prohibited | allow | Technical architecture section. |
| design-tech-arch-domain | 3 | Domain Model | True | prohibited | allow | Domain model. |
| design-tech-arch-component-model | 3 | Component Model | True | prohibited | allow | Component model and responsibilities. |
| design-tech-arch-api-contracts | 3 | API Contracts | True | prohibited | allow | API contracts and external interfaces. |
| design-tech-arch-internal-deps | 3 | Internal Dependencies | True | prohibited | allow | Internal dependencies. |
| design-tech-arch-external-deps | 3 | External Dependencies | True | prohibited | allow | External dependencies. |
| design-tech-arch-seq | 3 | Interactions & Sequences | True | prohibited | allow | Interactions and sequences. |
| design-tech-arch-db | 3 | Database schemas & tables | True | prohibited | allow | Database schemas and tables. |
| design-additional-context | 2 | Additional context | False | prohibited | allow | Optional additional context. |
| design-traceability | 2 | Traceability | False | prohibited | allow | Optional traceability links. |

### Identifiers

| key | kind | name | required | task | priority | to_code | template | headings | references | examples | description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| design | design | Design Element (legacy prefix) | False | allowed | allowed | false | cpt-{system}-design-{slug} | design-h1-title | PRD: coverage=prohibited | cpt-cypilot-design-core-architecture, cpt-cypilot-design-validation-pipeline, cpt-overwork-alert-design-cli-daemon | Legacy/compatibility design identifier (prefer more specific kinds like principle/constraint/component/seq). |
| principle | principle | Design Principle | True | allowed | allowed | false | cpt-{system}-principle-{slug} | design-principles | PRD: coverage=prohibited<br>DECOMPOSITION: coverage=required; task=allowed; priority=allowed; headings=[decomposition-entry]<br>FEATURE: coverage=optional; task=allowed; priority=allowed; headings=[feature-context-purpose] | cpt-cypilot-principle-deterministic-gate, cpt-cypilot-principle-traceability, cpt-cypilot-principle-machine-readable | A guiding design rule (why/what to prefer) that shapes architecture and implementation decisions. |
| constraint | constraint | Design Constraint | True | allowed | allowed | false | cpt-{system}-constraint-{slug} | design-constraints | PRD: coverage=prohibited<br>DECOMPOSITION: coverage=required; task=allowed; priority=allowed; headings=[decomposition-entry]<br>FEATURE: coverage=optional; task=allowed; priority=allowed; headings=[feature-dod-entry] | cpt-cypilot-constraint-markdown, cpt-cypilot-constraint-stdlib-only, cpt-cypilot-constraint-no-weakening-rules | A hard boundary (technical/organizational/regulatory) that the design must satisfy. |
| component | component | Component | True | allowed | allowed | false | cpt-{system}-component-{slug} | design-tech-arch-component-model | DECOMPOSITION: coverage=required; task=allowed; priority=allowed; headings=[decomposition-entry]<br>PRD: coverage=prohibited | cpt-cypilot-component-cypilot-skill, cpt-cypilot-component-validator, cpt-overwork-alert-component-daemon | A logical architecture component/module with clear responsibilities and interfaces. |
| interface | interface | External Interface / Protocol | False | allowed | allowed | false | cpt-{system}-interface-{slug} | design-tech-arch-api-contracts | PRD: coverage=prohibited | cpt-cypilot-interface-cli-json, cpt-overwork-alert-interface-cli, cpt-overwork-alert-interface-ipc-protocol | A system boundary interface or protocol contract (e.g., CLI, IPC, REST endpoints) described in DESIGN. |
| seq | seq | Sequence | True | allowed | allowed | false | cpt-{system}-seq-{slug} | design-tech-arch-seq | PRD: coverage=prohibited | cpt-cypilot-seq-validate-overall-design, cpt-cypilot-seq-traceability-query, cpt-overwork-alert-seq-cli-to-daemon | A key interaction sequence (message flow) between components/actors, documented as a sequence diagram. |
| db | db | Database (legacy db-table prefix) | False | allowed | allowed | false | cpt-{system}-db-{slug} | design-tech-arch-db | PRD: coverage=prohibited<br>DECOMPOSITION: coverage=optional; task=allowed; priority=allowed; headings=[decomposition-entry] | cpt-cypilot-db-sqlite, cpt-cypilot-db-postgres, cpt-overwork-alert-db-local | Legacy/compatibility database identifier; prefer explicit table identifiers via dbtable when applicable. |
| dbtable | dbtable | Database Table | False | allowed | allowed | false | cpt-{system}-dbtable-{slug} | design-tech-arch-db | PRD: coverage=prohibited<br>DECOMPOSITION: coverage=required; task=allowed; priority=allowed; headings=[decomposition-entry] | cpt-cypilot-dbtable-na, cpt-cypilot-dbtable-artifacts, cpt-cypilot-dbtable-systems, cpt-overwork-alert-dbtable-config | A concrete database schema/table entity with columns, keys, and constraints documented in DESIGN. |
| topology | topology | Topology | False | allowed | allowed | false | cpt-{system}-topology-{slug} | design-tech-arch | PRD: coverage=prohibited | cpt-cypilot-topology-single-process, cpt-cypilot-topology-cli-daemon, cpt-overwork-alert-topology-launchagent | Deployment/runtime topology descriptor (processes/nodes/tiers) for the system or module. |
| tech | tech | Tech Stack | False | allowed | allowed | false | cpt-{system}-tech-{slug} | design-arch-overview-layers | PRD: coverage=prohibited | cpt-cypilot-tech-python-stdlib, cpt-cypilot-tech-markdown, cpt-cypilot-tech-json | A technology choice used in the architecture (language, framework, tool, storage, protocol). |

## DECOMPOSITION

**Name**: DECOMPOSITION constraints (cypilot-sdlc)
**Description**: Allowed ID kinds in DECOMPOSITION

### Headings

| id | level | pattern | required | multiple | numbered | description |
| --- | --- | --- | --- | --- | --- | --- |
| decomposition-h1-title | 1 |  | True | prohibited | allow | DECOMPOSITION document title (H1). |
| decomposition-overview | 2 | Overview | True | prohibited | allow | Overview of decomposition strategy. |
| decomposition-entries | 2 | Entries | True | prohibited | allow | List of feature entries. |
| decomposition-entry | 3 |  | True | allow | allow | A single feature entry. |
| decomposition-feature-deps | 2 | Feature Dependencies | True | prohibited | allow | Cross-feature dependency overview. |

### Identifiers

| key | kind | name | required | task | priority | to_code | template | headings | references | examples | description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| status | status | Overall Status | False | allowed | allowed | false | cpt-{system}-status-overall | decomposition-entries |  | cpt-cypilot-status-overall, cpt-overwork-alert-status-overall, cpt-cypilot-status-overall | A decomposition-level status indicator used to summarize overall progress/state. |
| feature | feature | Feature Entry | True | allowed | allowed | false | cpt-{system}-feature-{slug} | decomposition-entry | FEATURE: coverage=required; task=allowed; priority=allowed; headings=[feature-h1-title] | cpt-cypilot-feature-template-system, cpt-cypilot-feature-adapter-system, cpt-overwork-alert-feature-tracker-core | A DECOMPOSITION entry representing a FEATURE spec, including dependency and coverage links. |

## FEATURE

**Name**: FEATURE constraints (cypilot-sdlc)
**Description**: Allowed ID kinds in FEATURE

### Headings

| id | level | pattern | required | multiple | numbered | description |
| --- | --- | --- | --- | --- | --- | --- |
| feature-h1-title | 1 |  | True | prohibited | allow | FEATURE document title (H1). |
| feature-context | 2 | Feature Context | True | prohibited | allow | Feature context section. |
| feature-context-overview | 3 | Overview | True | prohibited | allow | Feature overview. |
| feature-context-purpose | 3 | Purpose | True | prohibited | allow | Feature purpose. |
| feature-context-actors | 3 | Actors | True | prohibited | allow | Actors involved in the feature. |
| feature-context-references | 3 | References | True | prohibited | allow | References to related artifacts. |
| feature-actor-flows | 2 | Actor Flows* | True | prohibited | allow | Actor flows section. |
| feature-actor-flow | 3 |  | True | allow | allow | A single actor flow. |
| feature-processes | 2 | Processes / Business Logic* | True | prohibited | allow | Processes / business logic section. |
| feature-process | 3 |  | True | allow | allow | A single process/algorithm. |
| feature-states | 2 | States* | True | prohibited | allow | States section. |
| feature-state | 3 |  | True | allow | allow | A single state machine. |
| feature-dod | 2 | Definitions of Done | True | prohibited | allow | Definitions of done section. |
| feature-dod-entry | 3 |  | True | allow | allow | A single definition of done entry. |
| feature-acceptance-criteria | 2 | Acceptance Criteria | True | prohibited | allow | Acceptance criteria for the feature. |

### Identifiers

| key | kind | name | required | task | priority | to_code | template | headings | references | examples | description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| featstatus | featstatus | Feature Status | True | required | allowed | false | cpt-{system}-featstatus-{feature-slug} | feature-h1-title | PRD: coverage=prohibited<br>DESIGN: coverage=prohibited | cpt-cypilot-featstatus-template-system, cpt-overwork-alert-featstatus-tracker-core, cpt-todo-app-featstatus-task-storage-foundation | A feature-level status/anchor marker used in FEATURE context. |
| flow | flow | Flow | False | allowed | allowed | true | cpt-{system}-flow-{feature-slug}-{slug} | feature-actor-flow | PRD: coverage=prohibited | cpt-cypilot-flow-template-system-load, cpt-cypilot-flow-template-system-validate, cpt-overwork-alert-flow-run-tracker | An actor-facing CDSL flow describing a user/system interaction end-to-end. |
| algo | algo | Algorithm | False | allowed | allowed | true | cpt-{system}-algo-{feature-slug}-{slug} | feature-processes | PRD: coverage=prohibited | cpt-cypilot-algo-template-system-extract-ids, cpt-cypilot-algo-methodology-core-apply-constraints, cpt-overwork-alert-algo-track-active-time | A reusable internal process described in CDSL (business logic not directly initiated by an actor). |
| state | state | State Machine | False | allowed | allowed | true | cpt-{system}-state-{feature-slug}-{slug} | feature-state | PRD: coverage=prohibited | cpt-cypilot-state-template-system-lifecycle, cpt-cypilot-state-methodology-core-validation-outcome, cpt-overwork-alert-state-daemon-lifecycle | A lifecycle/state machine definition for an entity or subsystem, described in CDSL transitions. |
| dod | dod | Definition of Done | True | required | required | true | cpt-{system}-dod-{feature-slug}-{slug} | feature-dod-entry | PRD: coverage=prohibited | cpt-cypilot-dod-template-system-validation, cpt-cypilot-dod-methodology-core, cpt-overwork-alert-dod-launchagent-autostart | A concrete implementation task derived from flows/processes/states, with required traceability. |
