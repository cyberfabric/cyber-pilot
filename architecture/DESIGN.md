# Technical Design — Cypilot

## 1. Architecture Overview

### 1.1 Architectural Vision

Cypilot employs a **layered architecture with plugin-based extensibility** to provide a technology-agnostic methodology framework. The core methodology layer defines universal workflows and validation rules, while the adapter layer enables project-specific customization without modifying core specifications. This separation ensures that Cypilot remains compatible with any technology stack while maintaining consistent design and validation patterns across all projects.

In this design, "Cypilot" means **Framework for Documentation and Development** (workflow-centered).

The architecture follows a **flow-driven approach** where users may start from design, implementation, or validation workflows. If required design artifacts are missing, workflows MUST bootstrap them interactively (ask the minimal set of questions needed) and then continue.

Once created, design artifacts become the authoritative traceability source. The validation layer uses a **deterministic gate pattern** where automated validators catch structural issues before expensive manual review, ensuring quality while maximizing efficiency.

AI agent integration is achieved through machine-readable specifications (AGENTS.md navigation, workflow files, requirements) and a skills-based tooling system. The WHEN clause pattern in AGENTS.md files creates a discoverable navigation system where AI agents can autonomously determine which specifications to follow based on the current workflow context.

### 1.2 Architecture Drivers

#### Product requirements

##### FR-001 Workflow-Driven Development

- [x] `p1` - `cpt-cypilot-fr-workflow-execution`

**Solution**: Implement operation/validation workflows as Markdown files in `workflows/*.md`, executed under [`requirements/execution-protocol.md`](../requirements/execution-protocol.md); drive deterministic tool entrypoint via `python3 skills/cypilot/scripts/cypilot.py <subcommand>`.

##### FR-002 Artifact Structure Validation

- [x] `p1` - `cpt-cypilot-fr-validation`

**Solution**: Implement validators in `skills/cypilot/scripts/cypilot/validation/**`; expose via `python3 skills/cypilot/scripts/cypilot.py validate` with JSON output.

##### FR-003 Adapter Configuration System

- [x] `p1` - `cpt-cypilot-fr-adapter-config`

**Solution**: Implement adapter discovery via `adapter-info`; apply adapter rules from `{project-root}/.cypilot-adapter/AGENTS.md` + `{project-root}/.cypilot-adapter/specs/*.md`.

##### FR-004 Adaptive Design Bootstrapping

- [x] `p1` - `cpt-cypilot-fr-design-first`

**Solution**: Enforce prerequisites-first in workflow specs + execution protocol.

##### FR-005 Traceability Management

- [x] `p1` - `cpt-cypilot-fr-traceability`

**Solution**: Implement ID scanning via `scan-ids`, `where-defined`, `where-used` subcommands; code traceability via `@cpt-*` tags.

##### FR-006 Quickstart Guides

- [x] `p2` - `cpt-cypilot-fr-interactive-docs`

**Solution**: Provide CLI/agent-facing onboarding via `QUICKSTART.md` + [`workflows/README.md`](../workflows/README.md).

##### FR-007 Artifact Templates

- [x] `p1` - `cpt-cypilot-fr-artifact-templates`

**Solution**: Provide templates in `kits/sdlc/artifacts/{KIND}/template.md`; workflows load kit packages via `kit` attribute in the artifacts registry.

##### FR-008 Artifact Examples

- [x] `p2` - `cpt-cypilot-fr-artifact-examples`

**Solution**: Provide canonical examples in `kits/sdlc/artifacts/{KIND}/examples/example.md`.

##### FR-009 ADR Management

- [x] `p2` - `cpt-cypilot-fr-arch-decision-mgmt`

**Solution**: Store ADRs in adapter-defined location; validate via `kits/sdlc/artifacts/ADR/` kit package.

##### FR-010 PRD Management

- [x] `p1` - `cpt-cypilot-fr-prd-mgmt`

**Solution**: Create/update PRD artifact (path defined by adapter registry) via [`workflows/generate.md`](../workflows/generate.md) using kit guidance from `kits/sdlc/artifacts/PRD/`; enforce stable IDs.

##### FR-011 Overall Design Management

- [x] `p1` - `cpt-cypilot-fr-overall-design-mgmt`

**Solution**: Create/update Overall Design artifact (path defined by adapter registry) via [`workflows/generate.md`](../workflows/generate.md) using rules from `kits/sdlc/artifacts/DESIGN/`.

##### FR-012 Spec Manifest Management

- [x] `p2` - `cpt-cypilot-fr-spec-manifest-mgmt`

**Solution**: Create/update DECOMPOSITION artifact (path defined by adapter registry) via [`workflows/generate.md`](../workflows/generate.md) using rules from `kits/sdlc/artifacts/DECOMPOSITION/`.

##### FR-013 Spec Design Management

- [x] `p1` - `cpt-cypilot-fr-spec-design-mgmt`

**Solution**: Create/update FEATURE artifact (path defined by adapter registry) via [`workflows/generate.md`](../workflows/generate.md) using rules from `kits/sdlc/artifacts/FEATURE/`.

##### FR-014 Spec Lifecycle Management

- [x] `p2` - `cpt-cypilot-fr-spec-lifecycle`

**Solution**: Encode lifecycle via manifest status fields + validation gates.

##### FR-015 Code Generation from Design

- [x] `p2` - `cpt-cypilot-fr-code-generation`

**Solution**: Implement "design-to-code" workflow via [`workflows/generate.md`](../workflows/generate.md) with adapter-defined code generation rules.

##### FR-016 Brownfield Support

- [x] `p2` - `cpt-cypilot-fr-brownfield-support`

**Solution**: Support legacy projects via adapter discovery and auto-detection.

##### FR-017 Cypilot DSL (CDSL)

- [x] `p1` - `cpt-cypilot-fr-cdsl`

**Solution**: Use Cypilot DSL (CDSL) instruction markers in FEATURE artifacts with `pN`/`inst-*` tokens.

##### FR-018 IDE Integration and Tooling

- [ ] `p3` - `cpt-cypilot-fr-ide-integration`

**Solution**: (Planned) VS Code extension with click-to-navigate for Cypilot IDs, inline validation, and autocomplete. Currently not implemented.

##### FR-019 Multi-Agent IDE Integration

- [x] `p2` - `cpt-cypilot-fr-multi-agent-integration`

**Solution**: Generate agent-specific workflow proxies for Claude, Cursor, Windsurf, Copilot.

##### FR-020 Extensible Kit Package System

- [x] `p1` - `cpt-cypilot-fr-rules-packages`

**Solution**: Support kit packages under `kits/` with `template.md`, `checklist.md`, `rules.md`.

##### FR-021 Template Quality Assurance

- [x] `p2` - `cpt-cypilot-fr-template-qa`

**Solution**: Provide `self-check` command for template/example validation.

##### FR-022 Cross-Artifact Validation

- [x] `p1` - `cpt-cypilot-fr-cross-artifact-validation`

**Solution**: Validate `covered_by` references, ID definitions, and checked consistency.

##### FR-023 Hierarchical System Registry

- [x] `p2` - `cpt-cypilot-fr-hierarchical-registry`

**Solution**: Support `system`, `parent`, `artifacts`, `codebase` in registry; expose via `adapter-info`.

##### NFR-001 Validation Performance

- [x] `p1` - `cpt-cypilot-nfr-validation-performance`

**Solution**: Use regex-based parsing, scoped filesystem scanning, registry-driven control.

##### NFR-002 Security Integrity

- [x] `p1` - `cpt-cypilot-nfr-security-integrity`

**Solution**: Enforce strict parsing and treat unsafe behavior as hard failure.

##### NFR-003 Reliability Recoverability

- [x] `p1` - `cpt-cypilot-nfr-reliability-recoverability`

**Solution**: Include paths/lines and deterministic remediation guidance.

##### NFR-004 Adoption Usability

- [x] `p2` - `cpt-cypilot-nfr-adoption-usability`

**Solution**: Templates and validation messages minimize required context.

#### Architecture Decisions Records

##### ADR-001 Initial Architecture

`cpt-cypilot-adr-initial-architecture-v1`

Establishes the initial layered architecture and repository structure for Cypilot, including the separation between methodology core, adapter-owned specs, workflows, and deterministic validation.

##### ADR-002 Adaptive Framework for Documentation and Development

- `cpt-cypilot-adr-adaptive-cypilot-flow-driven-development-v1`

Formalizes the "adaptive"/flow-driven execution model where workflows validate prerequisites, bootstrap missing artifacts, and then continue, rather than failing early.

##### ADR-003 Template-Centric Architecture

- `cpt-cypilot-adr-template-centric-architecture-v1`

Introduces template-centric architecture where templates become self-contained packages with workflows, checklists, and requirements.

### 1.3 Architecture Layers

| Layer | Responsibility | Technology |
|-------|---------------|------------|
| Methodology Core Layer | Defines universal Cypilot content requirements, workflow specifications, and base AGENTS.md navigation rules. Technology-agnostic and stable across all projects. | Markdown (specifications), Python 3 standard library (tooling) |
| Adapter Layer | Project-specific customization through adapter AGENTS.md with Extends mechanism. Contains tech stack definitions, domain model format specs, API contract formats, testing strategies, coding conventions, and the adapter-owned artifact registry for artifact discovery. | JSON (configuration), Markdown (specifications) |
| Validation Layer | Deterministic validators implemented in `cypilot` skill for structural validation. Includes ID format checking, cross-reference validation, placeholder detection, and code traceability verification. | Python 3 standard library (validators), JSON (reports) |
| Workflow Layer | Executable procedures for creating and validating artifacts. Operation workflows (interactive) for artifact creation/update, validation workflows (automated) for quality checks. Cypilot DSL (CDSL) provides plain-English algorithm descriptions. | Markdown (workflows), Cypilot DSL (CDSL) (algorithms) |
| AI Integration Layer | WHEN clause navigation system, skills-based tooling, and deterministic gate pattern for AI agent execution. Enables autonomous workflow execution with minimal human intervention. | Markdown (AGENTS.md), Python 3 (skills), JSON (skill I/O) |

---

## 2. Principles & Constraints

### 2.1 Design Principles

#### Technology-agnostic core

- [x] `p1` - **ID**: `cpt-cypilot-principle-tech-agnostic`

Keep the Cypilot core methodology and tooling independent of any particular programming language or framework. Project-specific technology choices belong in the adapter layer.

#### Design before code

- [x] `p1` - **ID**: `cpt-cypilot-principle-design-first`

Treat validated design artifacts as the single source of truth. Workflows must validate prerequisites before proceeding, and bootstrap missing prerequisites when appropriate.

#### Machine-readable specifications

- [x] `p1` - **ID**: `cpt-cypilot-principle-machine-readable`

Prefer formats and conventions that can be parsed deterministically (stable IDs, structured headings, tables, payload blocks) so validation and traceability can be automated.

#### Deterministic gate

- [x] `p1` - **ID**: `cpt-cypilot-principle-deterministic-gate`

Always run deterministic validation before manual review or implementation steps. Treat validator output as authoritative for structural correctness.

#### Traceability by design

- [x] `p1` - **ID**: `cpt-cypilot-principle-traceability`

Use stable IDs and cross-references across artifacts (and optional code tags) to support impact analysis and auditing from PRD to design to implementation.

#### Prefer stable, machine-readable, text-based artifacts

- [x] `p1` - **ID**: `cpt-cypilot-principle-machine-readable-artifacts`

Keep normative artifacts as stable, plain-text sources of truth that can be parsed deterministically. Prefer Markdown + structured conventions (IDs, tables, payload blocks) so both humans and tools can reliably consume and validate the content.

#### Prefer variability isolation via adapters over core changes

- [x] `p1` - **ID**: `cpt-cypilot-principle-adapter-variability-boundary`

Keep project-specific variability (tech stack, domain model format, API contracts, conventions) in the adapter layer. Avoid modifying core methodology/specs for project needs; instead, use Extends + adapter specs so the core remains generic and reusable.

#### Prefer composable CLI+JSON interfaces

- [x] `p1` - **ID**: `cpt-cypilot-principle-cli-json-composability`

Expose deterministic tooling via a CLI with stable JSON output for composition in CI/CD and IDE integrations. Prefer small, single-purpose commands that can be chained and automated.

### 2.2 Constraints

#### Constraint 1: Python Standard Library Only

- [x] `p1` - **ID**: `cpt-cypilot-constraint-stdlib-only`

The `cypilot` validation tool MUST use only Python 3.6+ standard library. No external dependencies (pip packages) are permitted in core tooling. This constraint ensures Cypilot can run anywhere Python is available without complex installation or dependency management. Adapters may use any dependencies for project-specific code generation.

#### Constraint 2: Markdown-Only Artifacts

- [x] `p1` - **ID**: `cpt-cypilot-constraint-markdown`

All Cypilot artifacts (PRD, Overall Design, ADRs, Spec Manifest, etc.) MUST be plain Markdown. No binary formats, proprietary tools, or custom file formats permitted. This constraint ensures artifacts are version-controllable, diffable, and editable in any text editor. Domain models and API contracts referenced by artifacts may be in any format (specified by adapter).

#### Constraint 3: Git-Based Workflow

- [x] `p1` - **ID**: `cpt-cypilot-constraint-git`

Cypilot assumes Git version control for artifact history and collaboration. Change tracking relies on Git commits and diffs. Spec branches and pull requests are the collaboration model. This constraint aligns Cypilot with modern development practices but requires Git knowledge from users.

#### Constraint 4: No Forced Tool Dependencies

- [x] `p1` - **ID**: `cpt-cypilot-constraint-no-forced-tools`

Cypilot core MUST NOT require specific IDEs, editors, or development tools. Validation MUST run from command line without GUI tools. IDE integrations are optional enhancements, not requirements. This constraint ensures Cypilot works in any development environment (local, remote, CI/CD, etc.).

---

## 3. Technical Architecture

### 3.1 Domain Model

**Technology**: Markdown-based artifacts (not code-level types) + JSON Schema (machine-readable contracts)

**Specifications**:
- Kit packages (templates, checklists, rules, examples): [`kits/sdlc/artifacts/{KIND}/`](../kits/sdlc/artifacts/)
- Artifact identifiers: [`requirements/identifiers.md`](../requirements/identifiers.md)
- Rules format: [`requirements/rules-format.md`](../requirements/rules-format.md)
- Cypilot DSL (CDSL) (behavior language): [`requirements/CDSL.md`](../requirements/CDSL.md)
- Artifact registry: [`requirements/artifacts-registry.md`](../requirements/artifacts-registry.md)
- Code traceability: [`requirements/traceability.md`](../requirements/traceability.md)

**Schemas** (machine-readable):
- Artifact registry: [`schemas/artifacts.schema.json`](../schemas/artifacts.schema.json)
- Template frontmatter: [`schemas/cypilot-template-frontmatter.schema.json`](../schemas/cypilot-template-frontmatter.schema.json)

**CLI Tool**:
- CLISPEC: [`skills/cypilot/cypilot.clispec`](../skills/cypilot/cypilot.clispec)
- SKILL: [`skills/cypilot/SKILL.md`](../skills/cypilot/SKILL.md)

**Core Entities**:

**Artifacts**:
- PRD: Vision, Actors, Capabilities, Use Cases
- Overall Design: Architecture, Requirements, Technical Details
- ADRs: MADR-formatted decision records
- DECOMPOSITION: Feature list with status tracking and dependency ordering
- FEATURE: Feature details with flows, algorithms, states, and Definition of Done

**IDs** (format: `cpt-{system}-{kind}-{slug}`):

*PRD Artifact*:
- Actor: `cpt-{system}-actor-{slug}`
- Use Case: `cpt-{system}-usecase-{slug}`
- Functional Requirement: `cpt-{system}-fr-{slug}`
- Non-Functional Requirement: `cpt-{system}-nfr-{slug}`

*DESIGN Artifact*:
- Principle: `cpt-{system}-principle-{slug}`
- Constraint: `cpt-{system}-constraint-{slug}`
- Component: `cpt-{system}-component-{slug}`
- Sequence: `cpt-{system}-seq-{slug}`
- DB Table: `cpt-{system}-dbtable-{slug}`
- Topology: `cpt-{system}-topology-{slug}`

*ADR Artifact*:
- ADR: `cpt-{system}-adr-{slug}`

*DECOMPOSITION Artifact*:
- Feature entry: `cpt-{system}-feature-{slug}`

*FEATURE Artifact*:
- Flow: `cpt-{system}-flow-{slug}`
- Algorithm: `cpt-{system}-algo-{slug}`
- State: `cpt-{system}-state-{slug}`
- Definition of Done: `cpt-{system}-dod-{slug}`
- Feature Context: `cpt-{system}-featurecontext-{slug}`

All IDs MAY be versioned by appending a `-vN` suffix (e.g., `cpt-{system}-adr-{slug}-v2`).

**Workflows**:
- Operation workflow (Type: Operation): Interactive artifact creation/update
- Validation workflow (Type: Validation): Automated quality checks

**Relationships**:
- PRD defines Actors, Use Cases, FRs, and NFRs
- Overall Design references FRs/NFRs/ADRs and defines Principles, Constraints, Components, Sequences
- DECOMPOSITION lists Features and references design elements
- FEATURE defines Flows, Algorithms, States, and DoD for a specific Feature
- ADRs are referenced by DESIGN and document architectural decisions

**CRITICAL**: Domain model is expressed in Markdown artifacts, not programming language types. Validation checks artifacts against requirements files, not type compilation.

### 3.2 Component Model

The Cypilot system consists of 6 core components + 1 external (Project) with the following interactions:

```mermaid
flowchart TB
    %% Entry point
    AGENT["Agent<br/>(LLM + System Prompts)"]

    %% Core components
    WF["Workflows<br/>workflows/*.md"]
    Cypilot["Cypilot Skill<br/>skills/cypilot<br/>(validate • list-ids • where-* • traceability)"]
    RP["Kit Packages<br/>kits/sdlc/"]
    AS["Adapter System<br/>.cypilot-adapter/"]
    MC["Methodology Core<br/>requirements/, workflows/"]

    %% External component
    PROJ["Project<br/>(artifacts, code, .cypilot-config)"]
    style PROJ fill:#e8f4e8,stroke:#666,stroke-dasharray: 5 5

    %% Agent interactions
    AGENT -.->|follows| WF
    AGENT ==>|invokes| Cypilot
    AGENT -->|reads/writes| PROJ

    %% Workflows
    WF ==>|calls| Cypilot
    WF -->|reads config| AS
    WF -->|loads templates| RP
    WF -.->|follows| MC

    %% Cypilot Skill
    Cypilot -->|reads config| AS
    Cypilot -->|parses templates| RP
    Cypilot ==>|init| AS
    Cypilot -->|reads/validates| PROJ
    Cypilot ==>|registers workflows| AGENT

    %% Embedding into Project
    AS -.->|embedded in| PROJ
    MC -.->|embedded in| PROJ

    %% Kit packages
    MC -->|provides| RP
    RP -.->|extends| MC
    PROJ -->|provides| RP
```

**Legend**: `==>` invokes (runtime call) | `-->` reads (data flow) | `-.->` depends (design-time)

**Component Descriptions**:

#### 1. Methodology Core

- [x] `p1` - **ID**: `cpt-cypilot-component-methodology-core`

- Contains universal Cypilot specifications (requirements files, workflow files, core AGENTS.md)
- Provides workflow templates (workflows/*.md)
- Technology-agnostic and stable across all projects
- Embedded in Project: copied or linked into project directory
- Location: configurable via adapter (typically `{project}/requirements/`, `{project}/workflows/`)

#### 2. Adapter System

- [x] `p1` - **ID**: `cpt-cypilot-component-adapter-system`

- Project-specific customization layer, embedded in Project
- Adapter AGENTS.md extends core AGENTS.md via **Extends** mechanism
- Spec files define tech stack, domain model format, API contracts, conventions
- Adapter-owned `artifacts.json` defines artifact discovery rules and can register project-specific kit packages
- Auto-detection capability for existing codebases
- Location: `<project>/.cypilot-adapter/`

#### 3. Kit Packages

- [x] `p1` - **ID**: `cpt-cypilot-component-rules-packages`

- Template definitions for each artifact kind (`template.md`)
- Semantic validation checklists (`checklist.md`)
- Generation guidance (`rules.md`)
- Canonical examples (`kits/sdlc/artifacts/{KIND}/examples/example.md`)
- **Extensible**: Projects can register custom kit packages via adapter
- Location: Cypilot distribution `kits/sdlc/artifacts/{KIND}/` + project-specific paths

#### 4. Cypilot Skill

- [x] `p1` - **ID**: `cpt-cypilot-component-cypilot-skill`

- CLI tool providing all deterministic operations (`skills/cypilot/scripts/cypilot.py`)
- **Validation**: Structural checks, ID formats, cross-references, placeholders
- **Traceability**: ID scanning (`list-ids`, `where-defined`, `where-used`), code tags (`@cpt-*`)
- **Init**: Initializes adapter (`init`), generates workflow and skill proxies (`agents`)
- Reads artifacts via Adapter System, parses by Kit Packages
- Output is JSON for machine consumption

#### 5. Workflows

- [x] `p1` - **ID**: `cpt-cypilot-component-workflows`

- Operation workflows: Interactive artifact creation/update
- Validation workflows: Automated quality checks
- CDSL processing: Plain-English algorithms with instruction markers
- Question-answer flow with context-based proposals
- Execution protocol: Prerequisites check → Specification reading → Interactive input → Content generation → Validation

#### 6. Agent

- [x] `p1` - **ID**: `cpt-cypilot-component-agent`

- LLM + system prompts (AGENTS.md navigation rules)
- WHEN clause rules determine which specs to follow
- Skills system: Claude-compatible tools (cypilot skill, future extensions)
- Deterministic gate pattern: Automated validators run before manual review
- Machine-readable specifications enable autonomous execution

#### 7. Project (External)

- Target system where Cypilot is applied
- Contains real artifacts (PRD, DESIGN, ADRs, DECOMPOSITION, SPECs)
- Contains implementation code with optional `@cpt-*` traceability tags
- Contains `.cypilot-config` created by Cypilot Skill `init` command
- Agent reads artifacts and code to understand context
- Agent writes artifacts and code during workflow execution
- Cypilot Skill validates artifacts and scans code for traceability

#### Workflow Execution Model

Cypilot treats the primary user interaction as **workflow execution**.

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

The deterministic gate is provided by the `cypilot` tool and MUST be treated as authoritative for structural validity.

#### Unix-way Alignment

Cypilot follows Unix-way principles for tooling:
- Prefer small, single-purpose commands (validate, list, search, trace).
- Prefer composable interfaces (CLI + JSON output) for CI/CD and IDE integrations.
- Keep stable, text-based, version-controlled inputs (Markdown artifacts, CLISPEC).
- Keep project-specific variability isolated in the adapter layer, not in the core.

#### `cypilot` Tool Execution Model

The `cypilot` tool is the deterministic interface used by workflows, CI, and IDE integrations.

Design contract:
- Single, agent-safe entrypoint: `python3 skills/cypilot/scripts/cypilot.py`.
- Command surface is specified in CLISPEC (`skills/cypilot/cypilot.clispec`).
- Output is JSON for machine consumption.
- The tool provides:
  - Deterministic validation of artifacts and cross-references.
  - Repository-wide search and traceability queries (`list-ids`, `where-defined`, `where-used`).
  - Adapter discovery (`adapter-info`).

### 3.3 API Contracts

**Technology**: CLISPEC for command-line interface (cypilot tool)

**Location**:
- Format specification: [`CLISPEC.md`](../CLISPEC.md)
- Command specification: [`skills/cypilot/cypilot.clispec`](../skills/cypilot/cypilot.clispec)
- Implementation: [`skills/cypilot/scripts/cypilot.py`](../skills/cypilot/scripts/cypilot.py)

**Commands Overview**:

**Validation**:
- `validate [--artifact <path>]`: Validate artifact structure against template
- `validate-kits [--kit <id>]`: Validate kit packages and templates
- `validate-code [path]`: Validate code traceability markers

**Search & Traceability**:
- `list-ids [--artifact <path>] [--pattern <str>] [--kind <str>]`: List all Cypilot IDs
- `list-id-kinds [--artifact <path>]`: List ID kinds with counts
- `get-content --artifact <path> --id <id>`: Get content block for ID
- `where-defined --id <id>`: Find where ID is defined
- `where-used --id <id>`: Find all references to ID

**Adapter & Agent Integration**:
- `adapter-info [--root <path>]`: Discover adapter configuration
- `init [--project-root <path>]`: Initialize Cypilot adapter
- `agents --agent <name>`: Generate agent workflow proxies and skill outputs
- `self-check [--kit <id>]`: Validate examples against templates

**CRITICAL**: API contracts are CLISPEC format (command-line interface specification), not REST/HTTP. All commands output JSON for machine consumption.

### 3.4 Internal Dependencies

None.

### 3.5 External Dependencies

None.

### 3.6 Interactions & Sequences

#### Resolve user intent to a workflow (operation + deterministic gate)

- [x] `p1` - **ID**: `cpt-cypilot-seq-intent-to-workflow`

```mermaid
sequenceDiagram
    participant User
    participant Agent as Agent (LLM + System Prompts)
    participant WF as Workflows
    participant RP as Kit Packages
    participant Cypilot as Cypilot Skill
    participant PROJ as Project

    User->>Agent: Request (intent)
    Agent->>Agent: Resolve intent via AGENTS.md navigation
    Agent->>WF: Read workflow spec
    WF->>RP: Load template + checklist
    Agent->>Cypilot: Validate prerequisites (deterministic gate)
    Cypilot->>PROJ: Read existing artifacts
    Cypilot-->>Agent: JSON report (PASS/FAIL)
    Agent-->>User: Ask questions / propose content
    User-->>Agent: Confirm proposal
    Agent->>PROJ: Write artifact
    Agent->>Cypilot: Validate updated artifact
    Cypilot->>RP: Parse against template
    Cypilot-->>Agent: JSON report (PASS/FAIL)
    Agent-->>User: Result + issues (if any)
```

**Components**: Agent, Workflows, Kit Packages, Cypilot Skill, Project

**Failure modes / error paths**:
- If adapter navigation prerequisites are missing (e.g., no `{project-root}/.cypilot-adapter/AGENTS.md`), the Agent MUST stop and ask the user to initialize or point to the correct project root.
- If the deterministic gate returns `FAIL`, the Agent MUST NOT write artifacts; it reports the validator errors and requests confirmation before re-running.
- If a required workflow or kit file is missing or unreadable, the Agent reports the missing dependency and does not continue the workflow.

**Actors**: `cpt-cypilot-actor-product-manager`, `cpt-cypilot-actor-architect`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-cypilot-tool`

#### Discover adapter configuration (before applying project-specific conventions)

- [x] `p1` - **ID**: `cpt-cypilot-seq-adapter-discovery`

```mermaid
sequenceDiagram
    participant User
    participant Agent as Agent (LLM + System Prompts)
    participant Cypilot as Cypilot Skill
    participant PROJ as Project
    participant AS as Adapter System

    User->>Agent: Start workflow execution
    Agent->>Cypilot: adapter-info --root <project>
    Cypilot->>PROJ: Read .cypilot-config (if present)
    Cypilot->>AS: Discover adapter + AGENTS/specs
    AS-->>Cypilot: Adapter path + specs
    Cypilot-->>Agent: Adapter info (paths, capabilities)
    Agent-->>User: Proceed using adapter conventions
```

**Components**: Agent, Cypilot Skill, Project, Adapter System

**Failure modes / error paths**:
- If no adapter is found, `adapter-info` returns a `NOT_FOUND` status; the Agent proceeds only with explicit user confirmation (no silent assumptions about conventions).
- If adapter registry files are malformed (e.g., invalid JSON), `adapter-info` returns an error; the Agent stops and requests the registry be fixed before continuing.
- If the selected root is wrong, the Agent asks the user to confirm the intended project root and re-runs discovery.

**Actors**: `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-ai-assistant`

#### Validate overall design against requirements (deterministic validation workflow)

- [x] `p1` - **ID**: `cpt-cypilot-seq-validate-overall-design`

```mermaid
sequenceDiagram
    participant User
    participant Cypilot as Cypilot Skill
    participant RP as Kit Packages
    participant PROJ as Project

    User->>Cypilot: validate --artifact architecture/DESIGN.md
    Cypilot->>RP: Load DESIGN template
    Cypilot->>PROJ: Read DESIGN.md
    Cypilot->>Cypilot: Validate structure against template
    Cypilot->>PROJ: Read PRD.md (cross-reference check)
    Cypilot->>PROJ: Read ADRs (cross-reference check)
    Cypilot->>Cypilot: Validate cross-artifact references
    Cypilot-->>User: JSON report (status + errors + warnings)
```

**Components**: Cypilot Skill, Kit Packages, Project

**Failure modes / error paths**:
- If the artifact does not match the template (missing required sections/markers), validation returns `FAIL` with a structured error list.
- If cross-artifact references are missing (e.g., referenced IDs/paths not found), validation returns `FAIL` with the unresolved references.
- If the kit package or template cannot be loaded, validation returns `FAIL` (missing dependency) and does not attempt partial validation.

**Actors**: `cpt-cypilot-actor-architect`, `cpt-cypilot-actor-cypilot-tool`

#### Trace requirement/use case to implementation (repository-wide queries)

- [x] `p1` - **ID**: `cpt-cypilot-seq-traceability-query`

```mermaid
sequenceDiagram
    participant User
    participant Cypilot as Cypilot Skill
    participant AS as Adapter System
    participant PROJ as Project

    User->>Cypilot: where-defined --id <cpt>
    Cypilot->>AS: Get artifact registry
    Cypilot->>PROJ: Scan artifacts for ID definition
    PROJ-->>Cypilot: File + line location
    Cypilot-->>User: Definition location (JSON)
    User->>Cypilot: where-used --id <cpt>
    Cypilot->>PROJ: Scan artifacts for ID references
    Cypilot->>PROJ: Scan codebase for @cpt-* tags (if enabled)
    PROJ-->>Cypilot: Usages list
    Cypilot-->>User: Usage list (JSON)
```

**Components**: Cypilot Skill, Adapter System, Project

**Failure modes / error paths**:
- If the adapter registry is missing/unreadable, queries return an error (no silent fallback for registry-scoped lookups).
- If an ID is not found, the command returns an empty result set (or explicit "not found" status), allowing callers to distinguish absence from errors.
- If code scanning is disabled or unsupported for the project, `where-used` omits code references and reports only artifact references.

**Actors**: `cpt-cypilot-actor-developer`, `cpt-cypilot-actor-cypilot-tool`

### 3.7 Database schemas & tables

#### N/A

- [x] `p3` - **ID**: `cpt-cypilot-dbtable-na`

Not applicable — Cypilot is a methodology framework that does not maintain its own database. Artifact data is stored in plain Markdown files and JSON configuration.

| Column | Type | Description |
|--------|------|-------------|
| N/A | N/A | No database tables |

| N/A | N/A | N/A |
|-----|-----|-----|
| N/A | N/A | N/A |

### 3.8 Topology

**ID**: `cpt-cypilot-topology-local`

Not applicable — Cypilot runs locally on developer machines. No cloud infrastructure, containers, or distributed deployment required. The `cypilot` CLI tool executes directly via Python interpreter.

### 3.9 Tech stack

**Status**: Accepted

- **Runtime**: Python 3.6+ standard library only
- **Configuration**: JSON (artifacts.json, .cypilot-config.json)
- **Documentation**: Markdown (all artifacts, workflows, specs)
- **Version Control**: Git (assumed for artifact history)

---

## 4. Additional Context

Additional notes and rationale for the Cypilot overall design.

### Technology Selection Rationale

**Python 3 Standard Library Only**: Chosen for maximum portability and zero installation complexity. Python 3.6+ is available on most development machines. Standard library ensures no dependency management or version conflicts.

**Markdown for Artifacts**: Universal format compatible with all editors, version control systems, and documentation platforms. Plain text ensures longevity and accessibility. Syntax highlighting and rendering available in all modern development tools.

**CLISPEC for API**: Command-line interface is most compatible with CI/CD pipelines, remote development, and automation scripts. JSON output enables machine consumption and integration with other tools.

**GTS for Cypilot's Own Domain Model**: While Cypilot supports any domain model format via adapters, Cypilot itself uses GTS (Global Type System) for domain type definitions as a demonstration of machine-readable specifications.

### Domain Applicability (Checklist)

This DESIGN describes a local CLI tool / methodology framework. Domains that are not applicable are explicitly marked with rationale so reviewers can distinguish "not applicable" from "omitted".

| Domain | Disposition | Notes / Where Addressed |
|---|---|---|
| ARCH | Addressed | Sections 1–3 (overview, components, contracts, sequences) |
| MAINT | Addressed | Sections 2–3 + Tech stack rationale (Section 3.7 + this section) |
| TEST | Addressed | Deterministic validation workflow (3.4) + repository tests (`tests/`) |
| DATA | Addressed (no DB) | DB explicitly N/A (3.5); artifacts are Markdown + JSON config (3.7) |
| INT | Addressed (repo-local) | Adapter discovery + registry-driven conventions (3.4) |
| SEC | Addressed (local-only) | No network service; no runtime dependency execution; failure paths + deterministic validation (3.4) |
| REL | Addressed (tool-level) | Deterministic validation + explicit failure modes (3.4) |
| PERF | Limited / non-goal | Not applicable for throughput/latency SLAs because this is a local CLI tool; performance considerations are limited to repo scan cost (noted in Future Improvements) |
| OPS | Not applicable | Not applicable — there is no deployed service topology (3.6). No runtime operations, paging, or SRE on-call model applies. |
| COMPL | Not applicable | Not applicable — Cypilot does not process regulated or personal customer data; artifacts are project documentation stored in-repo. |
| UX | Addressed (CLI) | CLI contracts + JSON output for automation (3.3); human UX is via editor/terminal tooling |
| BIZ | Addressed | PRD/requirements linkage and traceability intent (Sections 1–3) |

### Implementation Considerations

**Incremental Adoption Path**:
- Teams commonly start with a minimal adapter (`Extends: ...`) and then add PRD + DESIGN to establish shared intent and a deterministic validation target.
- ADRs and DECOMPOSITION/SPEC artifacts can be introduced later as decisions and traceability needs grow.
- Adapter conventions typically evolve over time as repeatable patterns emerge.

**Migration from Existing Projects**:
- Use `adapter-from-sources` to bootstrap a starting adapter from the existing repository.
- Capture product intent in PRD from the current requirements source of truth.
- Summarize the current architecture in DESIGN, focusing on stable components, interfaces, and invariants.
- Expand traceability incrementally (new/changed areas first), without blocking on full backfill.

**AI Agent Best Practices**:
 - Always run `cypilot adapter-info` before starting any workflow
 - Use deterministic gate (cypilot validate) before manual validation
 - Follow execution-protocol.md for all workflow executions
 - Use cypilot skill for artifact search and ID lookup
 - Never skip prerequisites validation

### Artifact Lifecycle Map

The following table summarizes which kit packages provide templates and validation for each artifact kind. Artifact paths are defined by the adapter registry, not hardcoded.

| Artifact Kind | Kit Package | Create/Update | Validate |
|---|---|---|---|
| PRD | `kits/sdlc/artifacts/PRD/` | [`workflows/generate.md`](../workflows/generate.md) | [`workflows/analyze.md`](../workflows/analyze.md) |
| DESIGN | `kits/sdlc/artifacts/DESIGN/` | [`workflows/generate.md`](../workflows/generate.md) | [`workflows/analyze.md`](../workflows/analyze.md) |
| ADR | `kits/sdlc/artifacts/ADR/` | [`workflows/generate.md`](../workflows/generate.md) | [`workflows/analyze.md`](../workflows/analyze.md) |
| DECOMPOSITION | `kits/sdlc/artifacts/DECOMPOSITION/` | [`workflows/generate.md`](../workflows/generate.md) | [`workflows/analyze.md`](../workflows/analyze.md) |
| FEATURE | `kits/sdlc/artifacts/FEATURE/` | [`workflows/generate.md`](../workflows/generate.md) | [`workflows/analyze.md`](../workflows/analyze.md) |

All artifact kinds use the same generic workflows (`generate.md` for creation/update, `analyze.md` for validation/analysis). The artifact kind and path are determined by the adapter registry and selected via the `/cypilot` entrypoint.

### Global Specification Contracts

Cypilot avoids duplicating requirements across artifacts. The following files are the authoritative contracts that workflows and artifacts MUST follow:

 - Execution protocol: [requirements/execution-protocol.md](../requirements/execution-protocol.md)
 - Generate workflow: [workflows/generate.md](../workflows/generate.md)
 - Validate workflow: [workflows/analyze.md](../workflows/analyze.md)
 - Rules format: [requirements/rules-format.md](../requirements/rules-format.md)
 - Artifact identifiers specification: [requirements/identifiers.md](../requirements/identifiers.md)
 - Kit packages (templates, checklists, rules, examples): [kits/sdlc/artifacts/](../kits/sdlc/artifacts/)

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
 - Auto-completion for Cypilot IDs and references

**Adapter Ecosystem**:
 - Public adapter registry for common tech stacks
 - Adapter composition (extend multiple adapters)
 - Adapter versioning and compatibility checking
 - Community-contributed patterns and templates

## 5. Traceability

- **PRD**: [PRD.md](./PRD.md)
- **ADRs**: [ADR/](./ADR/)
- **Features**: [specs/](./specs/)

**Date**: 2026-01-17
