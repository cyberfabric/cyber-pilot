<!-- fdd:#:design -->
# Technical Design: FDD

<!-- fdd:##:architecture-overview -->
## 1. Architecture Overview

<!-- fdd:###:architectural-vision -->
### Architectural Vision

<!-- fdd:architectural-vision-body -->
FDD employs a **layered architecture with plugin-based extensibility** to provide a technology-agnostic methodology framework. The core methodology layer defines universal workflows and validation rules, while the adapter layer enables project-specific customization without modifying core specifications. This separation ensures that FDD remains compatible with any technology stack while maintaining consistent design and validation patterns across all projects.

In this design, "FDD" means **Framework for Documentation and Development** (workflow-centered).

The architecture follows a **flow-driven approach** where users may start from design, implementation, or validation workflows. If required design artifacts are missing, workflows MUST bootstrap them interactively (ask the minimal set of questions needed) and then continue.

Once created, design artifacts become the authoritative traceability source. The validation layer uses a **deterministic gate pattern** where automated validators catch structural issues before expensive manual review, ensuring quality while maximizing efficiency.

AI agent integration is achieved through machine-readable specifications (AGENTS.md navigation, workflow files, requirements) and a skills-based tooling system. The WHEN clause pattern in AGENTS.md files creates a discoverable navigation system where AI agents can autonomously determine which specifications to follow based on the current workflow context.
<!-- fdd:architectural-vision-body -->
<!-- fdd:###:architectural-vision -->

<!-- fdd:###:architecture-drivers -->
### Architecture drivers

<!-- fdd:####:prd-requirements -->
#### Product requirements

<!-- fdd:fr-title repeat="many" -->
##### FR-001 Workflow-Driven Development

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p1` - `fdd-fdd-fr-workflow-execution`
<!-- fdd:id-ref:fr -->

**Solution**: Implement operation/validation workflows as Markdown files in `workflows/*.md`, executed under `requirements/execution-protocol.md`; drive deterministic tool entrypoint via `python3 skills/fdd/scripts/fdd.py <subcommand>`.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-002 Artifact Structure Validation

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p1` - `fdd-fdd-fr-validation`
<!-- fdd:id-ref:fr -->

**Solution**: Implement validators in `skills/fdd/scripts/fdd/validation/**`; expose via `python3 skills/fdd/scripts/fdd.py validate` with JSON output.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-003 Adapter Configuration System

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p1` - `fdd-fdd-fr-adapter-config`
<!-- fdd:id-ref:fr -->

**Solution**: Implement adapter discovery via `adapter-info`; apply adapter rules from `.adapter/AGENTS.md` + `.adapter/specs/*.md`.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-004 Adaptive Design Bootstrapping

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p1` - `fdd-fdd-fr-design-first`
<!-- fdd:id-ref:fr -->

**Solution**: Enforce prerequisites-first in workflow specs + execution protocol.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-005 Traceability Management

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p1` - `fdd-fdd-fr-traceability`
<!-- fdd:id-ref:fr -->

**Solution**: Implement ID scanning via `scan-ids`, `where-defined`, `where-used` subcommands; code traceability via `@fdd-*` tags.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-006 Quickstart Guides

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p2` - `fdd-fdd-fr-interactive-docs`
<!-- fdd:id-ref:fr -->

**Solution**: Provide CLI/agent-facing onboarding via `QUICKSTART.md` + `workflows/README.md`.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-007 Artifact Templates

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p1` - `fdd-fdd-fr-artifact-templates`
<!-- fdd:id-ref:fr -->

**Solution**: Provide templates in `rules/sdlc/artifacts/{KIND}/template.md`; workflows load rules packages via `rules` attribute in artifacts registry.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-008 Artifact Examples

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p2` - `fdd-fdd-fr-artifact-examples`
<!-- fdd:id-ref:fr -->

**Solution**: Provide canonical examples in `rules/sdlc/artifacts/{KIND}/examples/example.md`.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-009 ADR Management

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p2` - `fdd-fdd-fr-arch-decision-mgmt`
<!-- fdd:id-ref:fr -->

**Solution**: Store ADRs in adapter-defined location; validate via `rules/sdlc/artifacts/ADR/` rules package.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-010 PRD Management

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p1` - `fdd-fdd-fr-prd-mgmt`
<!-- fdd:id-ref:fr -->

**Solution**: Create/update PRD artifact (path defined by adapter registry) via `workflows/generate.md` using rules from `rules/sdlc/artifacts/PRD/`; enforce stable IDs.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-011 Overall Design Management

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p1` - `fdd-fdd-fr-overall-design-mgmt`
<!-- fdd:id-ref:fr -->

**Solution**: Create/update Overall Design artifact (path defined by adapter registry) via `workflows/generate.md` using rules from `rules/sdlc/artifacts/DESIGN/`.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-012 Feature Manifest Management

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p2` - `fdd-fdd-fr-feature-manifest-mgmt`
<!-- fdd:id-ref:fr -->

**Solution**: Create/update Feature Manifest artifact (path defined by adapter registry) via `workflows/generate.md` using rules from `rules/sdlc/artifacts/FEATURES/`.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-013 Feature Design Management

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p1` - `fdd-fdd-fr-feature-design-mgmt`
<!-- fdd:id-ref:fr -->

**Solution**: Create/update Feature Design artifact (path defined by adapter registry) via `workflows/generate.md` using rules from `rules/sdlc/artifacts/FEATURE/`.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-014 Feature Lifecycle Management

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p2` - `fdd-fdd-fr-feature-lifecycle`
<!-- fdd:id-ref:fr -->

**Solution**: Encode lifecycle via manifest status fields + validation gates.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-015 Code Generation from Design

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p2` - `fdd-fdd-fr-code-generation`
<!-- fdd:id-ref:fr -->

**Solution**: Implement "design-to-code" workflow via `workflows/generate.md` with adapter-defined code generation rules.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-016 Brownfield Support

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p2` - `fdd-fdd-fr-brownfield-support`
<!-- fdd:id-ref:fr -->

**Solution**: Support legacy projects via adapter discovery and auto-detection.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-017 FDL (FDD Description Language)

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p1` - `fdd-fdd-fr-fdl`
<!-- fdd:id-ref:fr -->

**Solution**: Use FDL markers in feature design with `ph-N`/`inst-*` tokens.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-018 IDE Integration and Tooling

<!-- fdd:id-ref:fr has="priority,task" -->
[ ] `p3` - `fdd-fdd-fr-ide-integration`
<!-- fdd:id-ref:fr -->

**Solution**: (Planned) VS Code extension with click-to-navigate for FDD IDs, inline validation, and autocomplete. Currently not implemented.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-019 Multi-Agent IDE Integration

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p2` - `fdd-fdd-fr-multi-agent-integration`
<!-- fdd:id-ref:fr -->

**Solution**: Generate agent-specific workflow proxies for Claude, Cursor, Windsurf, Copilot.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-020 Extensible Rules Package System

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p1` - `fdd-fdd-fr-rules-packages`
<!-- fdd:id-ref:fr -->

**Solution**: Support rules packages under `rules/` with `template.md`, `checklist.md`, `rules.md`.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-021 Template Quality Assurance

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p2` - `fdd-fdd-fr-template-qa`
<!-- fdd:id-ref:fr -->

**Solution**: Provide `self-check` command for template/example validation.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-022 Cross-Artifact Validation

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p1` - `fdd-fdd-fr-cross-artifact-validation`
<!-- fdd:id-ref:fr -->

**Solution**: Validate `covered_by` references, ID definitions, and checked consistency.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### FR-023 Hierarchical System Registry

<!-- fdd:id-ref:fr has="priority,task" -->
[x] `p2` - `fdd-fdd-fr-hierarchical-registry`
<!-- fdd:id-ref:fr -->

**Solution**: Support `system`, `parent`, `artifacts`, `codebase` in registry; expose via `adapter-info`.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:nfr-title repeat="many" -->
##### NFR-001 Validation Performance

<!-- fdd:id-ref:nfr has="priority,task" -->
[x] `p1` - `fdd-fdd-nfr-validation-performance`
<!-- fdd:id-ref:nfr -->

**Solution**: Use regex-based parsing, scoped filesystem scanning, registry-driven control.
<!-- fdd:nfr-title -->

<!-- fdd:nfr-title repeat="many" -->
##### NFR-002 Security Integrity

<!-- fdd:id-ref:nfr has="priority,task" -->
[x] `p1` - `fdd-fdd-nfr-security-integrity`
<!-- fdd:id-ref:nfr -->

**Solution**: Enforce strict parsing and treat unsafe behavior as hard failure.
<!-- fdd:nfr-title -->

<!-- fdd:nfr-title repeat="many" -->
##### NFR-003 Reliability Recoverability

<!-- fdd:id-ref:nfr has="priority,task" -->
[x] `p1` - `fdd-fdd-nfr-reliability-recoverability`
<!-- fdd:id-ref:nfr -->

**Solution**: Include paths/lines and deterministic remediation guidance.
<!-- fdd:nfr-title -->

<!-- fdd:nfr-title repeat="many" -->
##### NFR-004 Adoption Usability

<!-- fdd:id-ref:nfr has="priority,task" -->
[x] `p2` - `fdd-fdd-nfr-adoption-usability`
<!-- fdd:id-ref:nfr -->

**Solution**: Templates and validation messages minimize required context.
<!-- fdd:nfr-title -->
<!-- fdd:####:prd-requirements -->

<!-- fdd:####:adr-records -->
#### Architecture Decisions Records

<!-- fdd:adr-title -->
##### ADR-001 Initial Architecture

<!-- fdd:id-ref:adr has="priority,task" -->
[x] `p1` - `fdd-fdd-adr-initial-architecture-v1`
<!-- fdd:id-ref:adr -->

Establishes the initial layered architecture and repository structure for FDD, including the separation between methodology core, adapter-owned specs, workflows, and deterministic validation.
<!-- fdd:adr-title -->

<!-- fdd:adr-title -->
##### ADR-002 Adaptive Framework for Documentation and Development

<!-- fdd:id-ref:adr has="priority,task" -->
[x] `p1` - `fdd-fdd-adr-adaptive-fdd-flow-driven-development-v1`
<!-- fdd:id-ref:adr -->

Formalizes the "adaptive"/flow-driven execution model where workflows validate prerequisites, bootstrap missing artifacts, and then continue, rather than failing early.
<!-- fdd:adr-title -->

<!-- fdd:adr-title -->
##### ADR-003 Template-Centric Architecture

<!-- fdd:id-ref:adr has="priority,task" -->
[x] `p1` - `fdd-fdd-adr-template-centric-architecture-v1`
<!-- fdd:id-ref:adr -->

Introduces template-centric architecture where templates become self-contained packages with workflows, checklists, and requirements.
<!-- fdd:adr-title -->
<!-- fdd:####:adr-records -->
<!-- fdd:###:architecture-drivers -->

<!-- fdd:###:architecture-layers -->
### Architecture Layers

<!-- fdd:table:architecture-layers -->
| Layer | Responsibility | Technology |
|-------|---------------|------------|
| Methodology Core Layer | Defines universal FDD content requirements, workflow specifications, and base AGENTS.md navigation rules. Technology-agnostic and stable across all projects. | Markdown (specifications), Python 3 standard library (tooling) |
| Adapter Layer | Project-specific customization through adapter AGENTS.md with Extends mechanism. Contains tech stack definitions, domain model format specs, API contract formats, testing strategies, coding conventions, and the adapter-owned artifact registry for artifact discovery. | JSON (configuration), Markdown (specifications) |
| Validation Layer | Deterministic validators implemented in `fdd` skill for structural validation. Includes ID format checking, cross-reference validation, placeholder detection, and code traceability verification. | Python 3 standard library (validators), JSON (reports) |
| Workflow Layer | Executable procedures for creating and validating artifacts. Operation workflows (interactive) for artifact creation/update, validation workflows (automated) for quality checks. FDL provides plain-English algorithm descriptions. | Markdown (workflows), FDL (algorithms) |
| AI Integration Layer | WHEN clause navigation system, skills-based tooling, and deterministic gate pattern for AI agent execution. Enables autonomous workflow execution with minimal human intervention. | Markdown (AGENTS.md), Python 3 (skills), JSON (skill I/O) |
<!-- fdd:table:architecture-layers -->
<!-- fdd:###:architecture-layers -->
<!-- fdd:##:architecture-overview -->

---

<!-- fdd:##:principles-and-constraints -->
## 2. Principles & Constraints

<!-- fdd:###:principles -->
### 2.1: Design Principles

<!-- fdd:####:principle-title repeat="many" -->
#### Technology-agnostic core

<!-- fdd:id:principle has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-principle-tech-agnostic`

<!-- fdd:paragraph:principle-body -->
Keep the FDD core methodology and tooling independent of any particular programming language or framework. Project-specific technology choices belong in the adapter layer.
<!-- fdd:paragraph:principle-body -->
<!-- fdd:id:principle -->
<!-- fdd:####:principle-title -->

<!-- fdd:####:principle-title repeat="many" -->
#### Design before code

<!-- fdd:id:principle has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-principle-design-first`

<!-- fdd:paragraph:principle-body -->
Treat validated design artifacts as the single source of truth. Workflows must validate prerequisites before proceeding, and bootstrap missing prerequisites when appropriate.
<!-- fdd:paragraph:principle-body -->
<!-- fdd:id:principle -->
<!-- fdd:####:principle-title -->

<!-- fdd:####:principle-title repeat="many" -->
#### Machine-readable specifications

<!-- fdd:id:principle has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-principle-machine-readable`

<!-- fdd:paragraph:principle-body -->
Prefer formats and conventions that can be parsed deterministically (stable IDs, structured headings, tables, payload blocks) so validation and traceability can be automated.
<!-- fdd:paragraph:principle-body -->
<!-- fdd:id:principle -->
<!-- fdd:####:principle-title -->

<!-- fdd:####:principle-title repeat="many" -->
#### Deterministic gate

<!-- fdd:id:principle has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-principle-deterministic-gate`

<!-- fdd:paragraph:principle-body -->
Always run deterministic validation before manual review or implementation steps. Treat validator output as authoritative for structural correctness.
<!-- fdd:paragraph:principle-body -->
<!-- fdd:id:principle -->
<!-- fdd:####:principle-title -->

<!-- fdd:####:principle-title repeat="many" -->
#### Traceability by design

<!-- fdd:id:principle has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-principle-traceability`

<!-- fdd:paragraph:principle-body -->
Use stable IDs and cross-references across artifacts (and optional code tags) to support impact analysis and auditing from PRD to design to implementation.
<!-- fdd:paragraph:principle-body -->
<!-- fdd:id:principle -->
<!-- fdd:####:principle-title -->

<!-- fdd:####:principle-title repeat="many" -->
#### Prefer stable, machine-readable, text-based artifacts

<!-- fdd:id:principle has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-principle-machine-readable-artifacts`

<!-- fdd:paragraph:principle-body -->
Keep normative artifacts as stable, plain-text sources of truth that can be parsed deterministically. Prefer Markdown + structured conventions (IDs, tables, payload blocks) so both humans and tools can reliably consume and validate the content.
<!-- fdd:paragraph:principle-body -->
<!-- fdd:id:principle -->
<!-- fdd:####:principle-title -->

<!-- fdd:####:principle-title repeat="many" -->
#### Prefer variability isolation via adapters over core changes

<!-- fdd:id:principle has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-principle-adapter-variability-boundary`

<!-- fdd:paragraph:principle-body -->
Keep project-specific variability (tech stack, domain model format, API contracts, conventions) in the adapter layer. Avoid modifying core methodology/specs for project needs; instead, use Extends + adapter specs so the core remains generic and reusable.
<!-- fdd:paragraph:principle-body -->
<!-- fdd:id:principle -->
<!-- fdd:####:principle-title -->

<!-- fdd:####:principle-title repeat="many" -->
#### Prefer composable CLI+JSON interfaces

<!-- fdd:id:principle has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-principle-cli-json-composability`

<!-- fdd:paragraph:principle-body -->
Expose deterministic tooling via a CLI with stable JSON output for composition in CI/CD and IDE integrations. Prefer small, single-purpose commands that can be chained and automated.
<!-- fdd:paragraph:principle-body -->
<!-- fdd:id:principle -->
<!-- fdd:####:principle-title -->
<!-- fdd:###:principles -->

<!-- fdd:###:constraints -->
### 2.2: Constraints

<!-- fdd:####:constraint-title repeat="many" -->
#### Constraint 1: Python Standard Library Only

<!-- fdd:id:constraint has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-constraint-stdlib-only`

<!-- fdd:paragraph:constraint-body -->
The `fdd` validation tool MUST use only Python 3.6+ standard library. No external dependencies (pip packages) are permitted in core tooling. This constraint ensures FDD can run anywhere Python is available without complex installation or dependency management. Adapters may use any dependencies for project-specific code generation.
<!-- fdd:paragraph:constraint-body -->
<!-- fdd:id:constraint -->
<!-- fdd:####:constraint-title -->

<!-- fdd:####:constraint-title repeat="many" -->
#### Constraint 2: Markdown-Only Artifacts

<!-- fdd:id:constraint has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-constraint-markdown`

<!-- fdd:paragraph:constraint-body -->
All FDD artifacts (PRD, Overall Design, ADRs, Feature Manifest, etc.) MUST be plain Markdown. No binary formats, proprietary tools, or custom file formats permitted. This constraint ensures artifacts are version-controllable, diffable, and editable in any text editor. Domain models and API contracts referenced by artifacts may be in any format (specified by adapter).
<!-- fdd:paragraph:constraint-body -->
<!-- fdd:id:constraint -->
<!-- fdd:####:constraint-title -->

<!-- fdd:####:constraint-title repeat="many" -->
#### Constraint 3: Git-Based Workflow

<!-- fdd:id:constraint has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-constraint-git`

<!-- fdd:paragraph:constraint-body -->
FDD assumes Git version control for artifact history and collaboration. Change tracking relies on Git commits and diffs. Feature branches and pull requests are the collaboration model. This constraint aligns FDD with modern development practices but requires Git knowledge from users.
<!-- fdd:paragraph:constraint-body -->
<!-- fdd:id:constraint -->
<!-- fdd:####:constraint-title -->

<!-- fdd:####:constraint-title repeat="many" -->
#### Constraint 4: No Forced Tool Dependencies

<!-- fdd:id:constraint has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-constraint-no-forced-tools`

<!-- fdd:paragraph:constraint-body -->
FDD core MUST NOT require specific IDEs, editors, or development tools. Validation MUST run from command line without GUI tools. IDE integrations are optional enhancements, not requirements. This constraint ensures FDD works in any development environment (local, remote, CI/CD, etc.).
<!-- fdd:paragraph:constraint-body -->
<!-- fdd:id:constraint -->
<!-- fdd:####:constraint-title -->
<!-- fdd:###:constraints -->
<!-- fdd:##:principles-and-constraints -->

---

<!-- fdd:##:technical-architecture -->
## 3. Technical Architecture

<!-- fdd:###:domain-model -->
### 3.1: Domain Model

<!-- fdd:paragraph:domain-model -->
**Technology**: Markdown-based artifacts (not code-level types) + JSON Schema (machine-readable contracts)

**Specifications**:
- Rules packages (templates, checklists, rules, examples): [`rules/sdlc/artifacts/{KIND}/`](../rules/sdlc/artifacts/)
- Template syntax: [`requirements/template.md`](../requirements/template.md)
- Rules format: [`requirements/rules-format.md`](../requirements/rules-format.md)
- FDL (behavior language): [`requirements/FDL.md`](../requirements/FDL.md)
- Artifact registry: [`requirements/artifacts-registry.md`](../requirements/artifacts-registry.md)
- Code traceability: [`requirements/traceability.md`](../requirements/traceability.md)

**Schemas** (machine-readable):
- Artifact registry: [`schemas/artifacts.schema.json`](../schemas/artifacts.schema.json)
- Template frontmatter: [`schemas/fdd-template-frontmatter.schema.json`](../schemas/fdd-template-frontmatter.schema.json)

**CLI Tool**:
- CLISPEC: [`skills/fdd/fdd.clispec`](../skills/fdd/fdd.clispec)
- SKILL: [`skills/fdd/SKILL.md`](../skills/fdd/SKILL.md)

**Core Entities**:

**Artifacts**:
- PRD: Vision, Actors, Capabilities, Use Cases
- Overall Design: Architecture, Requirements, Technical Details
- ADRs: MADR-formatted decision records
- Feature Manifest: Feature list with status tracking
- Feature Design: Feature specifications with flows, algorithms, states

**IDs** (format: `fdd-{system}-{kind}-{slug}`):

*PRD Artifact*:
- Actor: `fdd-{system}-actor-{slug}`
- Use Case: `fdd-{system}-usecase-{slug}`
- Functional Requirement: `fdd-{system}-fr-{slug}`
- Non-Functional Requirement: `fdd-{system}-nfr-{slug}`

*DESIGN Artifact*:
- Principle: `fdd-{system}-principle-{slug}`
- Constraint: `fdd-{system}-constraint-{slug}`
- Component: `fdd-{system}-component-{slug}`
- Sequence: `fdd-{system}-seq-{slug}`
- DB Table: `fdd-{system}-dbtable-{slug}`
- Topology: `fdd-{system}-topology-{slug}`

*ADR Artifact*:
- ADR: `fdd-{system}-adr-{slug}`

*FEATURES Artifact*:
- Feature: `fdd-{system}-feature-{slug}`

*FEATURE Artifact* (nested under feature):
- Flow: `fdd-{system}-feature-{feature}-flow-{slug}`
- Algorithm: `fdd-{system}-feature-{feature}-algo-{slug}`
- State: `fdd-{system}-feature-{feature}-state-{slug}`
- Feature Requirement: `fdd-{system}-feature-{feature}-req-{slug}`
- Feature Context: `fdd-{system}-feature-{feature}-featurecontext-{slug}`

All IDs MAY be versioned by appending a `-vN` suffix (e.g., `fdd-{system}-adr-{slug}-v2`).

**Workflows**:
- Operation workflow (Type: Operation): Interactive artifact creation/update
- Validation workflow (Type: Validation): Automated quality checks

**Relationships**:
- PRD defines Actors, Use Cases, FRs, and NFRs
- Overall Design references FRs/NFRs/ADRs and defines Principles, Constraints, Components, Sequences
- Feature Manifest lists Features and references design elements
- Feature Design defines Flows, Algorithms, States for a specific Feature
- ADRs are referenced by DESIGN and document architectural decisions

**CRITICAL**: Domain model is expressed in Markdown artifacts, not programming language types. Validation checks artifacts against requirements files, not type compilation.
<!-- fdd:paragraph:domain-model -->
<!-- fdd:###:domain-model -->

<!-- fdd:###:component-model -->
### 3.2: Component Model

The FDD system consists of 6 core components + 1 external (Project) with the following interactions:

<!-- fdd:code:component-model -->
```mermaid
flowchart TB
    %% Entry point
    AGENT["Agent<br/>(LLM + System Prompts)"]

    %% Core components
    WF["Workflows<br/>workflows/*.md"]
    FDD["FDD Skill<br/>skills/fdd<br/>(validate • list-ids • where-* • traceability)"]
    RP["Rules Packages<br/>rules/sdlc/"]
    AS["Adapter System<br/>.adapter/"]
    MC["Methodology Core<br/>requirements/, workflows/"]

    %% External component
    PROJ["Project<br/>(artifacts, code, .fdd-config)"]
    style PROJ fill:#e8f4e8,stroke:#666,stroke-dasharray: 5 5

    %% Agent interactions
    AGENT -.->|follows| WF
    AGENT ==>|invokes| FDD
    AGENT -->|reads/writes| PROJ

    %% Workflows
    WF ==>|calls| FDD
    WF -->|reads config| AS
    WF -->|loads templates| RP
    WF -.->|follows| MC

    %% FDD Skill
    FDD -->|reads config| AS
    FDD -->|parses templates| RP
    FDD ==>|init| AS
    FDD -->|reads/validates| PROJ
    FDD ==>|registers workflows| AGENT

    %% Embedding into Project
    AS -.->|embedded in| PROJ
    MC -.->|embedded in| PROJ

    %% Rules packages
    MC -->|provides| RP
    RP -.->|extends| MC
    PROJ -->|provides| RP
```

**Legend**: `==>` invokes (runtime call) | `-->` reads (data flow) | `-.->` depends (design-time)
<!-- fdd:code:component-model -->

**Component Descriptions**:

<!-- fdd:####:component-title repeat="many" -->
#### 1. Methodology Core

<!-- fdd:id:component has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-component-methodology-core`

<!-- fdd:list:component-payload -->
- Contains universal FDD specifications (requirements files, workflow files, core AGENTS.md)
- Provides workflow templates (workflows/*.md)
- Technology-agnostic and stable across all projects
- Embedded in Project: copied or linked into project directory
- Location: configurable via adapter (typically `{project}/requirements/`, `{project}/workflows/`)
<!-- fdd:list:component-payload -->
<!-- fdd:id:component -->
<!-- fdd:####:component-title -->

<!-- fdd:####:component-title repeat="many" -->
#### 2. Adapter System

<!-- fdd:id:component has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-component-adapter-system`

<!-- fdd:list:component-payload -->
- Project-specific customization layer, embedded in Project
- Adapter AGENTS.md extends core AGENTS.md via **Extends** mechanism
- Spec files define tech stack, domain model format, API contracts, conventions
- Adapter-owned `artifacts.json` defines artifact discovery rules and can register project-specific rules packages
- Auto-detection capability for existing codebases
- Location: `<project>/.adapter/`
<!-- fdd:list:component-payload -->
<!-- fdd:id:component -->
<!-- fdd:####:component-title -->

<!-- fdd:####:component-title repeat="many" -->
#### 3. Rules Packages

<!-- fdd:id:component has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-component-rules-packages`

<!-- fdd:list:component-payload -->
- Template definitions for each artifact kind (`template.md`)
- Semantic validation checklists (`checklist.md`)
- Generation guidance (`rules.md`)
- Canonical examples (`examples/example.md`)
- **Extensible**: Projects can register custom rules packages via adapter
- Location: FDD distribution `rules/sdlc/artifacts/{KIND}/` + project-specific paths
<!-- fdd:list:component-payload -->
<!-- fdd:id:component -->
<!-- fdd:####:component-title -->

<!-- fdd:####:component-title repeat="many" -->
#### 4. FDD Skill

<!-- fdd:id:component has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-component-fdd-skill`

<!-- fdd:list:component-payload -->
- CLI tool providing all deterministic operations (`skills/fdd/scripts/fdd.py`)
- **Validation**: Structural checks, ID formats, cross-references, placeholders
- **Traceability**: ID scanning (`list-ids`, `where-defined`, `where-used`), code tags (`@fdd-*`)
- **Init**: Initializes adapter (`init`), generates workflow and skill proxies (`agents`)
- Reads artifacts via Adapter System, parses by Rules Packages
- Output is JSON for machine consumption
<!-- fdd:list:component-payload -->
<!-- fdd:id:component -->
<!-- fdd:####:component-title -->

<!-- fdd:####:component-title repeat="many" -->
#### 5. Workflows

<!-- fdd:id:component has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-component-workflows`

<!-- fdd:list:component-payload -->
- Operation workflows: Interactive artifact creation/update
- Validation workflows: Automated quality checks
- FDL processing: Plain-English algorithms with instruction markers
- Question-answer flow with context-based proposals
- Execution protocol: Prerequisites check → Specification reading → Interactive input → Content generation → Validation
<!-- fdd:list:component-payload -->
<!-- fdd:id:component -->
<!-- fdd:####:component-title -->

<!-- fdd:####:component-title repeat="many" -->
#### 6. Agent

<!-- fdd:id:component has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-component-agent`

<!-- fdd:list:component-payload -->
- LLM + system prompts (AGENTS.md navigation rules)
- WHEN clause rules determine which specs to follow
- Skills system: Claude-compatible tools (fdd skill, future extensions)
- Deterministic gate pattern: Automated validators run before manual review
- Machine-readable specifications enable autonomous execution
<!-- fdd:list:component-payload -->
<!-- fdd:id:component -->
<!-- fdd:####:component-title -->

#### 7. Project (External)

- Target system where FDD is applied
- Contains real artifacts (PRD, DESIGN, ADRs, FEATURES, FEATUREs)
- Contains implementation code with optional `@fdd-*` traceability tags
- Contains `.fdd-config` created by FDD Skill `init` command
- Agent reads artifacts and code to understand context
- Agent writes artifacts and code during workflow execution
- FDD Skill validates artifacts and scans code for traceability

#### Workflow Execution Model

FDD treats the primary user interaction as **workflow execution**.

The system provides two workflow types:
- **Operation workflows**: interactively create/update artifacts using a question-answer loop with proposals and explicit user confirmation before writing.
- **Validation workflows**: validate artifacts deterministically and output results to chat only (no file writes).

Execution sequence (conceptual, shared across workflows):
1. Resolve user intent to a workflow.
2. Discover adapter configuration (if present).
3. Validate prerequisites (required artifacts exist and are already validated to threshold).
4. Execute the workflow:
  - Operation: collect inputs → update artifact → run validation.
  - Validation: deterministic gate first → manual/LLM-heavy checks next.

The deterministic gate is provided by the `fdd` tool and MUST be treated as authoritative for structural validity.

#### Unix-way Alignment

FDD follows Unix-way principles for tooling:
- Prefer small, single-purpose commands (validate, list, search, trace).
- Prefer composable interfaces (CLI + JSON output) for CI/CD and IDE integrations.
- Keep stable, text-based, version-controlled inputs (Markdown artifacts, CLISPEC).
- Keep project-specific variability isolated in the adapter layer, not in the core.

#### `fdd` Tool Execution Model

The `fdd` tool is the deterministic interface used by workflows, CI, and IDE integrations.

Design contract:
- Single, agent-safe entrypoint: `python3 skills/fdd/scripts/fdd.py`.
- Command surface is specified in CLISPEC (`skills/fdd/fdd.clispec`).
- Output is JSON for machine consumption.
- The tool provides:
  - Deterministic validation of artifacts and cross-references.
  - Repository-wide search and traceability queries (`list-ids`, `where-defined`, `where-used`).
  - Adapter discovery (`adapter-info`).
<!-- fdd:###:component-model -->

<!-- fdd:###:api-contracts -->
### 3.3: API Contracts

<!-- fdd:paragraph:api-contracts -->
**Technology**: CLISPEC for command-line interface (fdd tool)

**Location**:
- Format specification: [`CLISPEC.md`](../CLISPEC.md)
- Command specification: [`skills/fdd/fdd.clispec`](../skills/fdd/fdd.clispec)
- Implementation: [`skills/fdd/scripts/fdd.py`](../skills/fdd/scripts/fdd.py)

**Commands Overview**:

**Validation**:
- `validate [--artifact <path>]`: Validate artifact structure against template
- `validate-rules [--rule <id>]`: Validate rules packages and templates
- `validate-code [path]`: Validate code traceability markers

**Search & Traceability**:
- `list-ids [--artifact <path>] [--pattern <str>] [--kind <str>]`: List all FDD IDs
- `list-id-kinds [--artifact <path>]`: List ID kinds with counts
- `get-content --artifact <path> --id <id>`: Get content block for ID
- `where-defined --id <id>`: Find where ID is defined
- `where-used --id <id>`: Find all references to ID

**Adapter & Agent Integration**:
- `adapter-info [--root <path>]`: Discover adapter configuration
- `init [--project-root <path>]`: Initialize FDD adapter
- `agents --agent <name>`: Generate agent workflow proxies and skill outputs
- `self-check [--rule <id>]`: Validate examples against templates

**CRITICAL**: API contracts are CLISPEC format (command-line interface specification), not REST/HTTP. All commands output JSON for machine consumption.
<!-- fdd:paragraph:api-contracts -->
<!-- fdd:###:api-contracts -->

<!-- fdd:###:interactions -->
### 3.4: Interactions & Sequences

<!-- fdd:####:sequence-title repeat="many" -->
#### Resolve user intent to a workflow (operation + deterministic gate)

<!-- fdd:id:seq has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-seq-intent-to-workflow`

<!-- fdd:code:sequences -->
```mermaid
sequenceDiagram
    participant User
    participant Agent as Agent (LLM + System Prompts)
    participant WF as Workflows
    participant RP as Rules Packages
    participant FDD as FDD Skill
    participant PROJ as Project

    User->>Agent: Request (intent)
    Agent->>Agent: Resolve intent via AGENTS.md navigation
    Agent->>WF: Read workflow spec
    WF->>RP: Load template + checklist
    Agent->>FDD: Validate prerequisites (deterministic gate)
    FDD->>PROJ: Read existing artifacts
    FDD-->>Agent: JSON report (PASS/FAIL)
    Agent-->>User: Ask questions / propose content
    User-->>Agent: Confirm proposal
    Agent->>PROJ: Write artifact
    Agent->>FDD: Validate updated artifact
    FDD->>RP: Parse against template
    FDD-->>Agent: JSON report (PASS/FAIL)
    Agent-->>User: Result + issues (if any)
```
<!-- fdd:code:sequences -->

<!-- fdd:paragraph:sequence-body -->
**Components**: Agent, Workflows, Rules Packages, FDD Skill, Project

**Actors**: `fdd-fdd-actor-product-manager`, `fdd-fdd-actor-architect`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-fdd-tool`
<!-- fdd:paragraph:sequence-body -->
<!-- fdd:id:seq -->
<!-- fdd:####:sequence-title -->

<!-- fdd:####:sequence-title repeat="many" -->
#### Discover adapter configuration (before applying project-specific conventions)

<!-- fdd:id:seq has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-seq-adapter-discovery`

<!-- fdd:code:sequences -->
```mermaid
sequenceDiagram
    participant User
    participant Agent as Agent (LLM + System Prompts)
    participant FDD as FDD Skill
    participant PROJ as Project
    participant AS as Adapter System

    User->>Agent: Start workflow execution
    Agent->>FDD: adapter-info --root <project>
    FDD->>PROJ: Read .fdd-config (if present)
    FDD->>AS: Discover adapter + AGENTS/specs
    AS-->>FDD: Adapter path + specs
    FDD-->>Agent: Adapter info (paths, capabilities)
    Agent-->>User: Proceed using adapter conventions
```
<!-- fdd:code:sequences -->

<!-- fdd:paragraph:sequence-body -->
**Components**: Agent, FDD Skill, Project, Adapter System

**Actors**: `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:paragraph:sequence-body -->
<!-- fdd:id:seq -->
<!-- fdd:####:sequence-title -->

<!-- fdd:####:sequence-title repeat="many" -->
#### Validate overall design against requirements (deterministic validation workflow)

<!-- fdd:id:seq has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-seq-validate-overall-design`

<!-- fdd:code:sequences -->
```mermaid
sequenceDiagram
    participant User
    participant FDD as FDD Skill
    participant RP as Rules Packages
    participant PROJ as Project

    User->>FDD: validate --artifact architecture/DESIGN.md
    FDD->>RP: Load DESIGN template
    FDD->>PROJ: Read DESIGN.md
    FDD->>FDD: Validate structure against template
    FDD->>PROJ: Read PRD.md (cross-reference check)
    FDD->>PROJ: Read ADRs (cross-reference check)
    FDD->>FDD: Validate cross-artifact references
    FDD-->>User: JSON report (status + errors + warnings)
```
<!-- fdd:code:sequences -->

<!-- fdd:paragraph:sequence-body -->
**Components**: FDD Skill, Rules Packages, Project

**Actors**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-fdd-tool`
<!-- fdd:paragraph:sequence-body -->
<!-- fdd:id:seq -->
<!-- fdd:####:sequence-title -->

<!-- fdd:####:sequence-title repeat="many" -->
#### Trace requirement/use case to implementation (repository-wide queries)

<!-- fdd:id:seq has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p1` - **ID**: `fdd-fdd-seq-traceability-query`

<!-- fdd:code:sequences -->
```mermaid
sequenceDiagram
    participant User
    participant FDD as FDD Skill
    participant AS as Adapter System
    participant PROJ as Project

    User->>FDD: where-defined --id <fdd-id>
    FDD->>AS: Get artifact registry
    FDD->>PROJ: Scan artifacts for ID definition
    PROJ-->>FDD: File + line location
    FDD-->>User: Definition location (JSON)
    User->>FDD: where-used --id <fdd-id>
    FDD->>PROJ: Scan artifacts for ID references
    FDD->>PROJ: Scan codebase for @fdd-* tags (if enabled)
    PROJ-->>FDD: Usages list
    FDD-->>User: Usage list (JSON)
```
<!-- fdd:code:sequences -->

<!-- fdd:paragraph:sequence-body -->
**Components**: FDD Skill, Adapter System, Project

**Actors**: `fdd-fdd-actor-developer`, `fdd-fdd-actor-fdd-tool`
<!-- fdd:paragraph:sequence-body -->
<!-- fdd:id:seq -->
<!-- fdd:####:sequence-title -->
<!-- fdd:###:interactions -->

<!-- fdd:###:database -->
### 3.5: Database schemas & tables (optional)

<!-- fdd:####:db-table-title repeat="many" -->
#### N/A

<!-- fdd:id:dbtable has="priority,task" covered_by="FEATURES,FEATURE" -->
- [x] `p3` - **ID**: `fdd-fdd-dbtable-na`

Not applicable — FDD is a methodology framework that does not maintain its own database. Artifact data is stored in plain Markdown files and JSON configuration.

<!-- fdd:table:db-table-schema -->
| Column | Type | Description |
|--------|------|-------------|
| N/A | N/A | No database tables |
<!-- fdd:table:db-table-schema -->

<!-- fdd:table:db-table-example -->
| N/A | N/A | N/A |
|-----|-----|-----|
| N/A | N/A | N/A |
<!-- fdd:table:db-table-example -->
<!-- fdd:id:dbtable -->
<!-- fdd:####:db-table-title -->
<!-- fdd:###:database -->

<!-- fdd:###:topology -->
### 3.6: Topology (optional)

<!-- fdd:id:topology has="task" -->
- [x] `p3` - **ID**: `fdd-fdd-topology-local`

<!-- fdd:free:topology-body -->
Not applicable — FDD runs locally on developer machines. No cloud infrastructure, containers, or distributed deployment required. The `fdd` CLI tool executes directly via Python interpreter.
<!-- fdd:free:topology-body -->
<!-- fdd:id:topology -->
<!-- fdd:###:topology -->

<!-- fdd:###:tech-stack -->
### 3.7: Tech stack (optional)

<!-- fdd:paragraph:status -->
**Status**: Accepted
<!-- fdd:paragraph:status -->

<!-- fdd:paragraph:tech-body -->
- **Runtime**: Python 3.6+ standard library only
- **Configuration**: JSON (artifacts.json, .fdd-config.json)
- **Documentation**: Markdown (all artifacts, workflows, specs)
- **Version Control**: Git (assumed for artifact history)
<!-- fdd:paragraph:tech-body -->
<!-- fdd:###:tech-stack -->
<!-- fdd:##:technical-architecture -->

---

<!-- fdd:##:design-context -->
## 4. Additional Context

<!-- fdd:free:design-context-body -->
Additional notes and rationale for the FDD overall design.

### Technology Selection Rationale

**Python 3 Standard Library Only**: Chosen for maximum portability and zero installation complexity. Python 3.6+ is available on most development machines. Standard library ensures no dependency management or version conflicts.

**Markdown for Artifacts**: Universal format compatible with all editors, version control systems, and documentation platforms. Plain text ensures longevity and accessibility. Syntax highlighting and rendering available in all modern development tools.

**CLISPEC for API**: Command-line interface is most compatible with CI/CD pipelines, remote development, and automation scripts. JSON output enables machine consumption and integration with other tools.

**GTS for FDD's Own Domain Model**: While FDD supports any domain model format via adapters, FDD itself uses GTS (Global Type System) for domain type definitions as a demonstration of machine-readable specifications.

### Implementation Considerations

**Incremental Adoption Path**:
 1. Start with adapter (minimal: just Extends line)
 2. Add PRD
 3. Add Overall Design
 4. Optionally add ADRs (decisions)
 5. Add Feature Manifest and Feature Designs
 6. Implement features using the primary implementation workflow
 7. Evolve adapter as patterns emerge

**Migration from Existing Projects**:
 - Use `adapter-from-sources` workflow to auto-detect tech stack
 - Reverse-engineer PRD content from existing requirements
 - Extract Overall Design patterns from code structure and documentation
 - Add traceability incrementally (new code first, legacy later)

**AI Agent Best Practices**:
 - Always run `fdd adapter-info` before starting any workflow
 - Use deterministic gate (fdd validate) before manual validation
 - Follow execution-protocol.md for all workflow executions
 - Use fdd skill for artifact search and ID lookup
 - Never skip prerequisites validation

### Artifact Lifecycle Map

The following table summarizes which rules packages provide templates and validation for each artifact kind. Artifact paths are defined by the adapter registry, not hardcoded.

| Artifact Kind | Rules Package | Create/Update | Validate |
|---|---|---|---|
| PRD | `rules/sdlc/artifacts/PRD/` | `workflows/generate.md` | `workflows/validate.md` |
| DESIGN | `rules/sdlc/artifacts/DESIGN/` | `workflows/generate.md` | `workflows/validate.md` |
| ADR | `rules/sdlc/artifacts/ADR/` | `workflows/generate.md` | `workflows/validate.md` |
| FEATURES | `rules/sdlc/artifacts/FEATURES/` | `workflows/generate.md` | `workflows/validate.md` |
| FEATURE | `rules/sdlc/artifacts/FEATURE/` | `workflows/generate.md` | `workflows/validate.md` |

All artifact kinds use the same generic workflows (`generate.md` for creation/update, `validate.md` for validation). The artifact kind and path are determined by the adapter registry and selected via the `/fdd` entrypoint.

### Global Specification Contracts

FDD avoids duplicating requirements across artifacts. The following files are the authoritative contracts that workflows and artifacts MUST follow:

 - Execution protocol: [requirements/execution-protocol.md](../requirements/execution-protocol.md)
 - Generate workflow: [workflows/generate.md](../workflows/generate.md)
 - Validate workflow: [workflows/validate.md](../workflows/validate.md)
 - Rules workflow: [workflows/rules.md](../workflows/rules.md)
 - Template syntax specification: [requirements/template.md](../requirements/template.md)
 - Rules packages (templates, checklists, rules, examples): [rules/sdlc/artifacts/](../rules/sdlc/artifacts/)

### Future Technical Improvements

**Performance Optimizations**:
 - Caching for repository-wide ID scans (currently re-scans on each query)
 - Incremental validation (only validate changed sections)
 - Parallel processing for multi-artifact validation

**Enhanced Traceability**:
 - Visual traceability graphs (actor → capability → requirement → code)
 - Impact analysis UI (show all affected artifacts when changing design)
 - Coverage metrics dashboard (% of requirements implemented, tested)

**IDE Integration Enhancements**:
 - Language server protocol (LSP) for real-time validation
 - Quick fixes for common validation errors
 - Hover tooltips showing ID definitions
 - Auto-completion for FDD IDs and references

**Adapter Ecosystem**:
 - Public adapter registry for common tech stacks
 - Adapter composition (extend multiple adapters)
 - Adapter versioning and compatibility checking
 - Community-contributed patterns and templates
<!-- fdd:free:design-context-body -->

<!-- fdd:paragraph:date -->
**Date**: 2025-01-17
<!-- fdd:paragraph:date -->
<!-- fdd:##:design-context -->
<!-- fdd:#:design -->