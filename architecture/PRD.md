# PRD — Cypilot

## 1. Overview

### 1.1 Purpose

Cypilot is a methodology and productized system for guiding software development through stable artifacts, deterministic validation, and repeatable workflows.

In this project, "Cypilot" means **Framework for Documentation and Development**: the project is developed by running workflows (flows), using skills/tools for deterministic checks, and iterating interactively with AI agents.

### 1.2 Background / Problem Statement

**Target Users**:
- Development Teams - Building software with clear design documentation
- Technical Leads & Architects - Defining system architecture and technical decisions
- Product Managers - Capturing product requirements and use cases
- AI Coding Assistants - Executing workflows and validating artifacts
- QA Engineers - Verifying implementation matches design
- Documentation Writers - Creating comprehensive technical documentation

**Key Problems Solved**:
- **Design-Code Disconnect**: Code diverges from design without single source of truth, leading to outdated documentation
- **Lack of Traceability**: Cannot track product requirements through design to implementation, making impact analysis difficult
- **Unstructured Development**: No repeatable process for design and implementation, causing inconsistent quality
- **AI Integration Challenges**: AI agents cannot follow methodology without structured guidance and machine-readable specifications
- **Validation Complexity**: Manual design reviews are time-consuming and miss structural issues

### 1.3 Goals (Business Outcomes)

**Success Criteria**:
- A new user can complete adapter initialization and reach a first passing PRD validation (`cypilot validate --artifact {project-root}/architecture/PRD.md`) in ≤ 60 minutes. (Baseline: not measured; Target: v1.0)
- Deterministic validation of the PRD completes in ≤ 3 seconds on a typical developer laptop. (Baseline: ~1s current; Target: v1.0)
- 100% of `cpt-cypilot-actor-*` IDs defined in the PRD are resolvable via deterministic search (`cypilot where-defined`) without ambiguity. (Baseline: 100% current; Target: v1.0)
- CI validation feedback for PRD changes is produced in ≤ 2 minutes from push to default branch. (Baseline: not measured; Target: v1.0)
- Users can apply a small PRD update (single section change) via `/cypilot-prd` in ≤ 10 minutes end-to-end, including re-validation. (Baseline: not measured; Target: v1.0)

**Capabilities**:
- Execute workflows to create/update/validate artifacts
- Provide deterministic validation and traceability scanning
- Support adapter-driven configuration for different projects and tech stacks

### 1.4 Glossary

| Term | Definition |
|------|------------|
| Cypilot | Artifact-first SDLC methodology + deterministic validator + workflows |
| Adapter | Project-specific customization layer (`.cypilot-adapter/`) |
| Kit package | Templates/rules/checklists/examples for an artifact kind |

---

## 2. Actors

### 2.1 Human Actors

#### Product Manager

**ID**: `cpt-cypilot-actor-product-manager`

**Role**: Defines product requirements, captures use cases, and documents PRD content using Cypilot workflows

#### Architect

**ID**: `cpt-cypilot-actor-architect`

**Role**: Designs system architecture, creates overall design documentation, and defines technical patterns

#### Developer

**ID**: `cpt-cypilot-actor-developer`

**Role**: Implements specs according to validated designs, adds traceability tags to code

#### QA Engineer

**ID**: `cpt-cypilot-actor-qa-engineer`

**Role**: Validates implementation against design specifications and ensures test coverage

#### Technical Lead

**ID**: `cpt-cypilot-actor-technical-lead`

**Role**: Sets up project adapters, configures Cypilot for project-specific conventions

#### Project Manager

**ID**: `cpt-cypilot-actor-project-manager`

**Role**: Monitors development progress, ensures workflows are followed, tracks spec completion

#### Documentation Writer

**ID**: `cpt-cypilot-actor-documentation-writer`

**Role**: Creates and maintains project documentation using Cypilot artifacts as source

#### DevOps Engineer

**ID**: `cpt-cypilot-actor-devops-engineer`

**Role**: Configures CI/CD pipelines, uses adapter specs for build and deployment automation

#### Security Engineer

**ID**: `cpt-cypilot-actor-security-engineer`

**Role**: Conducts security review of design and code, validates security requirements implementation

#### Business Analyst

**ID**: `cpt-cypilot-actor-prd-analyst`

**Role**: Analyzes product requirements and translates them into Cypilot format for Product Manager

#### UX Designer

**ID**: `cpt-cypilot-actor-ux-designer`

**Role**: Designs user interfaces based on actor flows from feature specification

#### Performance Engineer

**ID**: `cpt-cypilot-actor-performance-engineer`

**Role**: Defines performance targets, reviews designs for performance risks, and validates performance requirements implementation

#### Database Architect

**ID**: `cpt-cypilot-actor-database-architect`

**Role**: Designs data models and storage strategies, reviews domain model impacts, and validates database-related constraints

#### Release Manager

**ID**: `cpt-cypilot-actor-release-manager`

**Role**: Manages releases and tracks feature readiness using Cypilot artifacts (for example via a DECOMPOSITION when used)

#### AI Coding Assistant

**ID**: `cpt-cypilot-actor-ai-assistant`

**Role**: Executes Cypilot workflows interactively, generates artifacts, and validates against requirements

### 2.2 System Actors

#### Cypilot Validation Tool

**ID**: `cpt-cypilot-actor-cypilot-tool`

**Role**: Automated validation engine that checks artifact structure, ID formats, and traceability

#### CI/CD Pipeline

**ID**: `cpt-cypilot-actor-ci-pipeline`

**Role**: Automatically validates Cypilot artifacts on every commit through GitHub Actions or GitLab CI

#### Documentation Generator

**ID**: `cpt-cypilot-actor-doc-generator`

**Role**: Automatically generates external documentation from Cypilot artifacts (API docs, architecture diagrams)

---

## 3. Operational Concept & Environment

### 3.1 Module-Specific Environment Constraints

None.

## 4. Scope

### 4.1 In Scope

- Execute workflows to create/update/validate artifacts
- Deterministic validation and traceability scanning
- Adapter-driven configuration for project-specific conventions

### 4.2 Out of Scope

- Replacing project management tools (Jira, Linear, etc.)
- Automatically generating production-quality code without human review

---

## 5. Functional Requirements

### FR-001 Workflow-Driven Development

- [x] `p1` - **ID**: `cpt-cypilot-fr-workflow-execution`

The system MUST provide a clear, documented workflow catalog that users and AI agents can execute. Artifact locations MUST be adapter-defined; workflows MUST NOT hardcode repository paths. The core workflow set MUST cover at least: Adapter bootstrap and configuration, PRD creation/update, Overall design creation/update, ADR creation/update, Spec design creation/update, Spec implementation (`implement` as the primary implementation workflow), and Deterministic validation workflows for the above artifacts and for code traceability (when enabled). The system MUST provide a unified agent entrypoint workflow (`/cypilot`) that selects and executes the appropriate workflow (create/update/validate) based on context, or runs `cypilot` tool commands when requested. This includes interactive question-answer flow with AI agents, automated validation after artifact creation, step-by-step guidance for complex operations, and independent workflows (no forced sequence).

**Actors**:
`cpt-cypilot-actor-product-manager`, `cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-project-manager`, `cpt-cypilot-actor-release-manager`, `cpt-cypilot-actor-developer`, `cpt-cypilot-actor-qa-engineer`, `cpt-cypilot-actor-security-engineer`, `cpt-cypilot-actor-performance-engineer`, `cpt-cypilot-actor-database-architect`, `cpt-cypilot-actor-devops-engineer`, `cpt-cypilot-actor-documentation-writer`, `cpt-cypilot-actor-prd-analyst`, `cpt-cypilot-actor-ux-designer`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-cypilot-tool`, `cpt-cypilot-actor-ci-pipeline`

### FR-002 Artifact Structure Validation

- [x] `p1` - **ID**: `cpt-cypilot-fr-validation`

Deterministic validators for structural checks (sections, IDs, format). Deterministic content validation for semantic quality and boundaries: Content MUST be internally consistent (no contradictions), Content MUST NOT include information that belongs in other artifacts, Content MUST include required information expected for the artifact kind, Content MUST be semantically consistent with upstream/downstream artifacts (no cross-artifact contradictions), Content MUST not omit critical details that are explicitly defined in other artifacts. Deterministic validation for key artifacts defined by the adapter (no hardcoded repository paths). 100-point scoring system with category breakdown. Pass/fail thresholds (typically ≥90 or 100/100). Cross-reference validation (actor/capability IDs). Placeholder detection (incomplete markers). Detailed issue reporting with recommendations.

**Actors**:
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-developer`, `cpt-cypilot-actor-qa-engineer`, `cpt-cypilot-actor-security-engineer`, `cpt-cypilot-actor-performance-engineer`, `cpt-cypilot-actor-database-architect`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-cypilot-tool`, `cpt-cypilot-actor-ci-pipeline`

### FR-003 Adapter Configuration System

- [x] `p1` - **ID**: `cpt-cypilot-fr-adapter-config`

Technology-agnostic core methodology. Project-specific adapter specifications. Adapter MUST define an explicit registry of artifacts and their properties (for example: locations, scope, normative vs context-only). Adapter MUST support per-artifact configuration, including enabling/disabling code traceability checks. Tech stack definition (languages, frameworks, tools). Domain model format specification. API contract format specification. Adapter MUST be able to define deterministic tools/commands used to validate domain model sources and API contract sources. Testing strategy and build tool configuration. Auto-detection from existing codebase.

**Actors**:
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-architect`, `cpt-cypilot-actor-database-architect`, `cpt-cypilot-actor-performance-engineer`, `cpt-cypilot-actor-devops-engineer`, `cpt-cypilot-actor-developer`, `cpt-cypilot-actor-ai-assistant`

### FR-004 Adaptive Design Bootstrapping

- [x] `p1` - **ID**: `cpt-cypilot-fr-design-first`

Users MAY start implementation without having pre-existing design artifacts. When a workflow needs a traceability source and design artifacts are missing, the workflow MUST bootstrap the minimum viable design interactively and then continue. Once created, design artifacts become the single source of truth (code follows design). Design iteration MUST be workflow-driven and MUST be followed by deterministic validation. Clear separation between PRD, overall design, ADRs, and spec designs. Behavioral specifications MUST use Cypilot DSL (CDSL) (plain-English algorithms).

**Actors**:
`cpt-cypilot-actor-product-manager`, `cpt-cypilot-actor-architect`, `cpt-cypilot-actor-developer`, `cpt-cypilot-actor-prd-analyst`, `cpt-cypilot-actor-ux-designer`, `cpt-cypilot-actor-security-engineer`, `cpt-cypilot-actor-performance-engineer`, `cpt-cypilot-actor-database-architect`

### FR-005 Traceability Management

- [x] `p1` - **ID**: `cpt-cypilot-fr-traceability`

Unique ID system for all design elements using structured format. Code tags (@cpt-*) linking implementation to design. Traceability validation MUST be configurable per artifact (enabled/disabled via adapter). Cypilot-ID MAY be versioned by appending a `-vN` suffix (example: `<base-id>-v2`). When an identifier is replaced (REPLACE), the new identifier version MUST be incremented: If the prior identifier has no version suffix, the new identifier MUST end with `-v1`; If the prior identifier ends with `-vN`, the new identifier MUST increment the version by 1 (example: `-v1` → `-v2`). Once an identifier becomes versioned, the version suffix MUST NOT be removed in future references. When an identifier is replaced (REPLACE), all references MUST be updated (all artifacts and all code traceability tags, including qualified `:ph-N:inst-*` references). Qualified IDs for phases and instructions (:ph-N:inst-*). Repository-wide ID scanning and search. where-defined and where-used commands. Design-to-code validation (implemented items must have code tags).

**Actors**:
`cpt-cypilot-actor-developer`, `cpt-cypilot-actor-qa-engineer`, `cpt-cypilot-actor-cypilot-tool`

### FR-006 Quickstart Guides

- [x] `p2` - **ID**: `cpt-cypilot-fr-interactive-docs`

QUICKSTART guides with copy-paste prompts. Progressive disclosure (human-facing overview docs, AI navigation rules for agents).

**Actors**:
`cpt-cypilot-actor-documentation-writer`, `cpt-cypilot-actor-product-manager`, `cpt-cypilot-actor-release-manager`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-doc-generator`

### FR-007 Artifact Templates

- [x] `p1` - **ID**: `cpt-cypilot-fr-artifact-templates`

The system MUST provide an artifact template catalog for core Cypilot artifacts (PRD, Overall Design, ADRs, DECOMPOSITION, FEATURE). Agents MUST be able to use these templates during workflow execution.


**Actors**:
`cpt-cypilot-actor-documentation-writer`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-doc-generator`, `cpt-cypilot-actor-technical-lead`

### FR-008 Artifact Examples

- [x] `p2` - **ID**: `cpt-cypilot-fr-artifact-examples`

The system MUST provide an artifact example catalog for core Cypilot artifacts (PRD, Overall Design, ADRs, DECOMPOSITION, FEATURE). Agents MUST be able to use these examples during workflow execution.

**Actors**:
`cpt-cypilot-actor-documentation-writer`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-doc-generator`, `cpt-cypilot-actor-technical-lead`

### FR-009 ADR Management

- [x] `p2` - **ID**: `cpt-cypilot-fr-arch-decision-mgmt`

Create and track architecture decisions with structured format. Link ADRs to affected design sections and feature IDs. Decision status tracking (PROPOSED, ACCEPTED, DEPRECATED, SUPERSEDED). Impact analysis when ADR changes affect multiple features. Search ADRs by status, date, or affected components. Version history for decision evolution.

**Actors**:
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-security-engineer`, `cpt-cypilot-actor-performance-engineer`, `cpt-cypilot-actor-database-architect`

### FR-010 PRD Management

- [x] `p1` - **ID**: `cpt-cypilot-fr-prd-mgmt`

Create and update PRD content through workflows. Enforce stable IDs for actors and capabilities. PRD deterministic validation integration.

**Actors**:
`cpt-cypilot-actor-product-manager`, `cpt-cypilot-actor-prd-analyst`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-cypilot-tool`

### FR-011 Overall Design Management

- [x] `p1` - **ID**: `cpt-cypilot-fr-overall-design-mgmt`

Create and update Overall Design through workflows. Link requirements to PRD actors and capabilities. Deterministic validation integration for Overall Design.

**Actors**:
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-cypilot-tool`

### FR-012 Spec Manifest Management

- [x] `p2` - **ID**: `cpt-cypilot-fr-spec-manifest-mgmt`

Create and update DECOMPOSITION through workflows. Maintain stable IDs for features and tracking fields. Deterministic validation integration for DECOMPOSITION.

**Actors**:
`cpt-cypilot-actor-project-manager`, `cpt-cypilot-actor-release-manager`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-cypilot-tool`

### FR-013 Spec Design Management

- [x] `p1` - **ID**: `cpt-cypilot-fr-spec-design-mgmt`

Create and update FEATURE through workflows. Maintain stable IDs for flows, algorithms, states, and DoD. Deterministic validation integration for FEATURE.

**Actors**:
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-cypilot-tool`

### FR-014 Spec Lifecycle Management

- [x] `p2` - **ID**: `cpt-cypilot-fr-spec-lifecycle`

Track feature status from NOT_STARTED through IN_DESIGN, DESIGNED, READY, IN_PROGRESS to DONE. Track progress using the project's selected feature tracking approach (for example a decomposition when used). Feature dependency management and blocking detection. Milestone tracking and release planning integration. Historical feature completion metrics and velocity tracking. Status transition validation (cannot skip states).

**Actors**:
`cpt-cypilot-actor-project-manager`, `cpt-cypilot-actor-release-manager`, `cpt-cypilot-actor-developer`, `cpt-cypilot-actor-ai-assistant`

### FR-015 Code Generation from Design

- [x] `p2` - **ID**: `cpt-cypilot-fr-code-generation`

Provide an implementation process that is adapter-aware and works with any programming language. Apply general best practices that are applicable across languages. Prefer TDD where feasible and follow SOLID principles. Use adapter-defined domain model and API contract sources when present. Add traceability tags when traceability is enabled for the relevant artifacts.

**Actors**:
`cpt-cypilot-actor-developer`, `cpt-cypilot-actor-ai-assistant`

### FR-016 Brownfield Support

- [x] `p2` - **ID**: `cpt-cypilot-fr-brownfield-support`

Add Cypilot to existing projects without disruption. Auto-detect existing architecture from code and configs. Reverse-engineer the PRD from requirements documentation. Extract Overall Design patterns from implementation. Incremental Cypilot adoption (start with adapter, add artifacts gradually). Legacy system integration with minimal refactoring.

**Actors**:
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-architect`, `cpt-cypilot-actor-ai-assistant`

### FR-017 Cypilot DSL (CDSL)

- [x] `p1` - **ID**: `cpt-cypilot-fr-cdsl`

Plain English algorithm description language for actor flows (Cypilot DSL, abbreviated CDSL). Structured numbered lists with bold keywords (**IF**, **ELSE**, **WHILE**, **FOR EACH**). Instruction markers with checkboxes (- [ ] Inst-label: description). Phase-based organization (p1, p2, etc.) for implementation tracking. Readable by non-programmers for validation and review. Translates directly to code with traceability tags. Keywords: **AND**, **OR**, **NOT**, **MUST**, **REQUIRED**, **OPTIONAL**. Actor-centric (steps start with **Actor** or **System**).

**Actors**:
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-developer`, `cpt-cypilot-actor-prd-analyst`, `cpt-cypilot-actor-ux-designer`, `cpt-cypilot-actor-product-manager`

### FR-018 IDE Integration and Tooling

- [ ] `p3` - **ID**: `cpt-cypilot-fr-ide-integration`

VS Code extension for Cypilot artifact editing. Click-to-navigate for Cypilot IDs (jump to definition). where-used and where-defined commands in IDE. Inline validation errors and warnings. Autocomplete for Cypilot IDs and section references. Syntax highlighting for Cypilot DSL (CDSL). Integration with `cypilot` skill commands. Code lens showing traceability status.

**Actors**:
`cpt-cypilot-actor-developer`, `cpt-cypilot-actor-architect`, `cpt-cypilot-actor-devops-engineer`

### FR-019 Multi-Agent IDE Integration

- [x] `p2` - **ID**: `cpt-cypilot-fr-multi-agent-integration`

The system MUST provide a unified `agents` command to generate and maintain agent-specific workflow proxy files and skill entry points for multiple AI coding assistants. Supported agents MUST include Claude, Cursor, Windsurf, and Copilot. The `agents` command MUST generate workflow entry points in each agent's native format (e.g., `.claude/commands/`, `.cursor/commands/`, `.windsurf/workflows/`, `.github/prompts/`) and skill/rule entry points that point to the core Cypilot skill. Configuration MUST be externalized to a unified JSON file (`cypilot-agents.json`) with sensible defaults for recognized agents.

**Actors**:
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-devops-engineer`, `cpt-cypilot-actor-ai-assistant`

### FR-020 Extensible Kit Package System

- [x] `p1` - **ID**: `cpt-cypilot-fr-rules-packages`

The system MUST support extensible kit packages that define templates, checklists, and validation rules for artifact types. Each kit package MUST be identified in the adapter registry and MUST contain a `template.md` file with Cypilot markers for each artifact kind. Kit packages MAY contain `checklist.md` for semantic validation criteria and `rules.md` for generation guidance. The `validate-kits` command MUST validate that kit packages are structurally correct and that templates follow the cypilot-template frontmatter specification.

**Actors**:
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-cypilot-tool`, `cpt-cypilot-actor-ai-assistant`

### FR-021 Template Quality Assurance

- [x] `p2` - **ID**: `cpt-cypilot-fr-template-qa`

The system MUST provide a `self-check` command that validates example artifacts against their templates. The adapter registry MAY define `templates` entries with `template_path`, `example_path`, and `validation_level` properties. When `validation_level` is `STRICT`, the self-check command MUST validate that the example artifact passes all template validation rules. This ensures that templates and examples remain synchronized and that templates are valid.

**Actors**:
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-cypilot-tool`, `cpt-cypilot-actor-documentation-writer`

### FR-022 Cross-Artifact Validation

- [x] `p1` - **ID**: `cpt-cypilot-fr-cross-artifact-validation`

The system MUST validate cross-artifact relationships when multiple artifacts are validated together. ID blocks with `covered_by` attributes MUST have at least one reference in artifacts whose template kind matches the covered_by list. All ID references MUST resolve to a definition in some artifact. When a reference is marked as checked (`[x]`), the corresponding definition MUST also be marked as checked. Cross-artifact validation MUST be deterministic and report all consistency violations with line numbers and artifact paths.

**Actors**:
`cpt-cypilot-actor-cypilot-tool`, `cpt-cypilot-actor-ci-pipeline`, `cpt-cypilot-actor-architect`

### FR-023 Hierarchical System Registry

- [x] `p2` - **ID**: `cpt-cypilot-fr-hierarchical-registry`

The system MUST support hierarchical organization of systems in the artifacts registry. Each system MUST have a `name`, `rules` reference, and lists of `artifacts` and optional `codebase` entries. Systems MAY have `children` arrays for nested subsystems. Each artifact entry MUST specify `name`, `path`, `kind`, and `traceability` level (`FULL` or `DOCS-ONLY`). Each codebase entry MUST specify `name`, `path`, and `extensions` for code scanning. The `adapter-info` command MUST display the resolved hierarchical structure.

**Actors**:
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-cypilot-tool`, `cpt-cypilot-actor-architect`

---

## 6. Non-Functional Requirements

### 6.1 Module-Specific NFRs

#### Validation performance

- [x] `p2` - **ID**: `cpt-cypilot-nfr-validation-performance`

- Deterministic validation SHOULD complete in ≤ 10 seconds for typical repositories (≤ 50k LOC).
- Validation output MUST be clear and actionable.

#### Security and integrity

- [x] `p1` - **ID**: `cpt-cypilot-nfr-security-integrity`

- Validation MUST NOT execute untrusted code from artifacts.
- Validation MUST produce deterministic results given the same repository state.

#### Reliability and recoverability

- [x] `p2` - **ID**: `cpt-cypilot-nfr-reliability-recoverability`

- Validation failures MUST include enough context to remediate without reverse-engineering the validator.
- The system SHOULD provide actionable guidance for common failure modes (missing sections, invalid IDs, missing cross-references).

#### Adoption and usability

- [x] `p2` - **ID**: `cpt-cypilot-nfr-adoption-usability`

- Workflow instructions SHOULD be executable by a new user without prior Cypilot context, with ≤ 3 clarifying questions per workflow on average.
- Documentation SHOULD prioritize discoverability of next steps and prerequisites.

### 6.2 NFR Exclusions

- **Authentication/Authorization** (SEC-PRD-001/002): Not applicable — Cypilot is a local CLI tool and methodology, not a multi-user system requiring access control.
- **Availability/Recovery** (REL-PRD-001/002): Not applicable — Cypilot runs locally as a CLI, not as a service requiring uptime guarantees.
- **Scalability** (ARCH-PRD-003): Not applicable — Cypilot processes single repositories locally; traditional user/data volume scaling does not apply.
- **Throughput/Capacity** (PERF-PRD-002/003): Not applicable — Cypilot is a local development tool, not a high-throughput system.
- **Accessibility/Internationalization** (UX-PRD-002/003): Not applicable — CLI tool for developers; English-only is acceptable for developer tooling.
- **Regulatory/Legal** (COMPL-PRD-001/002/003): Not applicable — Cypilot is a methodology with no user data or regulated industry context.
- **Data Ownership/Lifecycle** (DATA-PRD-001/003): Not applicable — Cypilot does not persist user data; artifacts are owned by the project.
- **Support Requirements** (MAINT-PRD-002): Not applicable — Cypilot is an open methodology; support is community-driven.
- **Deployment/Monitoring** (OPS-PRD-001/002): Not applicable — Cypilot is installed locally via pip; no server deployment or monitoring required.

---

## 7. Public Library Interfaces

### 7.1 Public API Surface

None.

### 7.2 External Integration Contracts

None.

---

## 8. Use Cases

### UC-001 Bootstrap New Project with Cypilot

**ID**: `cpt-cypilot-usecase-bootstrap-project`

**Actors**:
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-ai-assistant`

**Preconditions**: Project repository exists with Git initialized

**Flow**:

1. Technical Lead initiates Cypilot setup by requesting AI Assistant to add the Cypilot framework
2. AI Assistant establishes minimal adapter configuration (uses capability `cpt-cypilot-fr-adapter-config`)
3. If adapter is missing, the system offers to bootstrap it; the user MAY decline and continue with reduced automation
4. The system confirms that adapter discovery is possible when the adapter exists

**Postconditions**: Project has working Cypilot adapter, ready for PRD and design workflows

---

### UC-002 Create PRD

**ID**: `cpt-cypilot-usecase-create-prd`

**Actors**:
`cpt-cypilot-actor-product-manager`, `cpt-cypilot-actor-ai-assistant`

**Preconditions**: Project context exists; adapter may or may not exist

**Flow**:

1. Product Manager runs `/cypilot-prd` and asks AI Assistant to create or refine PRD
2. AI Assistant asks questions about vision, target users, and problems solved
3. Product Manager answers; AI Assistant proposes PRD content based on available context
4. AI Assistant defines actors and capabilities with stable IDs (uses capability `cpt-cypilot-fr-traceability`)
5. AI Assistant updates the PRD according to answers
6. Product Manager validates PRD by running `/cypilot-prd-validate` (see `cpt-cypilot-usecase-validate-prd`)

**Postconditions**: Valid PRD exists, project ready for overall design workflow

---

### UC-003 Design Spec with AI Assistance

**ID**: `cpt-cypilot-usecase-design-spec`

**Actors**:
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-database-architect`, `cpt-cypilot-actor-performance-engineer`

**Preconditions**: PRD and Overall Design validated, feature scope identified (from backlog, ticket, or code context)

**Flow**:

1. Architect runs `/cypilot` and specifies the feature scope and desired outcomes
2. AI Assistant helps define actor flows in Cypilot DSL (CDSL) (uses capability `cpt-cypilot-fr-design-first`)
3. Architect defines requirements, constraints, and interfaces at feature scope
4. Architect runs `/cypilot`; the system validates the FEATURE deterministically (uses capability `cpt-cypilot-fr-validation`)
5. Validation reports 100/100 score (required for feature specification)

**Postconditions**: FEATURE validated at 100/100, ready for implementation

---

### UC-004 Validate Design Against Requirements - Overall Design

**ID**: `cpt-cypilot-usecase-validate-design`

**Actors**:
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-cypilot-tool`

**Preconditions**: Overall Design exists with requirements, actors, and capabilities defined

**Flow**:

1. Architect runs `/cypilot-design-validate` to request deterministic validation of overall design
2. The system validates structure, required content, and cross-artifact consistency (uses capability `cpt-cypilot-fr-validation`)
3. The system validates ID formats and cross-references (uses capability `cpt-cypilot-fr-traceability`)
4. The system reports a score breakdown with actionable issues

**Postconditions**: Validation report shows PASS (≥90/100) or FAIL with actionable issues, Architect fixes issues or proceeds to next workflow

---

### UC-005 Trace Requirement to Implementation

**ID**: `cpt-cypilot-usecase-trace-requirement`

**Actors**:
`cpt-cypilot-actor-developer`, `cpt-cypilot-actor-cypilot-tool`

**Preconditions**: FEATURE exists; implementation exists (partial or complete); traceability tags are present when traceability is enabled

**Flow**:

1. Developer selects a requirement ID to verify
2. The system locates the normative definition and where it is used (uses capability `cpt-cypilot-fr-traceability`)
3. The system reports traceability coverage and gaps

**Postconditions**: Developer confirms requirement is fully implemented with proper traceability, or identifies missing implementation

---

### UC-006 Update Existing Spec Design

**ID**: `cpt-cypilot-usecase-update-spec-design`

**Actors**:
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-ai-assistant`

**Preconditions**: FEATURE exists and previously validated at 100/100 (triggers `cpt-cypilot-usecase-design-spec`)

**Flow**:

1. Architect identifies need to add new algorithm to existing spec
2. AI Assistant runs `/cypilot` in update mode, loads existing FEATURE, and presents current content
3. AI Assistant asks: "What to update?" with options (Add actor flow, Edit algorithm, Add requirement, etc.)
4. Architect selects "Add new algorithm" option
5. Architect specifies new algorithm details in Cypilot DSL (CDSL) (uses capability `cpt-cypilot-fr-design-first`)
6. AI Assistant updates FEATURE while preserving unchanged sections
7. AI Assistant generates new algorithm ID following format `cpt-<project>-algo-<name>` (uses capability `cpt-cypilot-fr-traceability`)
8. Cypilot Validation Tool re-validates the updated FEATURE by running `/cypilot` (uses capability `cpt-cypilot-fr-validation`)
9. Validation confirms 100/100 score maintained

**Postconditions**: FEATURE updated with new algorithm, fully validated, ready for implementation

---

### UC-007 Implement Spec

**ID**: `cpt-cypilot-usecase-plan-implementation`

**Actors**:
`cpt-cypilot-actor-developer`, `cpt-cypilot-actor-ai-assistant`

**Preconditions**: FEATURE exists with a sufficiently clear traceability source (validated when possible)

**Flow**:

1. Developer requests to code the spec
2. AI Assistant executes `/cypilot-code` workflow (uses capability `cpt-cypilot-fr-workflow-execution`)
3. The system uses FEATURE to extract the minimal implementation scope
4. AI Assistant and Developer code iteratively, keeping design and code aligned
5. Developer adds code traceability tags where used (uses capability `cpt-cypilot-fr-traceability`)
6. Cypilot Validation Tool validates implementation and traceability by running `/cypilot-code-validate` (uses capability `cpt-cypilot-fr-validation`)

**Postconditions**: Spec implemented with traceability where used, and validation indicates completeness

---

### UC-009 Validate Spec Implementation

**ID**: `cpt-cypilot-usecase-validate-implementation`

**Actors**:
`cpt-cypilot-actor-qa-engineer`, `cpt-cypilot-actor-cypilot-tool`

**Preconditions**: Spec implementation exists (partial or complete)

**Flow**:

1. QA Engineer runs `/cypilot-code-validate` to request validation of spec implementation
2. Cypilot Validation Tool validates codebase traceability when enabled (uses capability `cpt-cypilot-fr-validation`)
3. Tool validates prerequisite design artifacts first
4. For each `[x]` marked scope in design, tool expects matching tags in code when traceability is enabled (uses capability `cpt-cypilot-fr-traceability`)
5. For each `[x]` marked Cypilot DSL (CDSL) instruction, tool expects instruction-level tag in code when traceability is enabled
6. Tool reports missing tags, extra tags, and format issues
7. Tool checks build passes and tests run successfully

**Postconditions**: Validation report shows full traceability or lists missing/incorrect tags, QA Engineer confirms implementation complete or requests fixes

---

### UC-010 Auto-Generate Adapter from Codebase

**ID**: `cpt-cypilot-usecase-auto-generate-adapter`

**Actors**:
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-ai-assistant`

**Preconditions**: Project has existing codebase with code, configs, and documentation

**Flow**:

1. Technical Lead wants to add Cypilot to existing project
2. AI Assistant runs `/cypilot-adapter-auto` to analyze existing codebase (uses capability `cpt-cypilot-fr-workflow-execution`)
3. AI Assistant scans project for documentation (README, ARCHITECTURE, CONTRIBUTING) (uses capability `cpt-cypilot-fr-adapter-config`)
4. AI Assistant analyzes config files (package.json, requirements.txt, Cargo.toml, etc.)
5. AI Assistant detects tech stack (languages, frameworks, versions)
6. AI Assistant analyzes code structure and naming conventions
7. AI Assistant discovers domain model format from code (TypeScript types, JSON Schema, etc.)
8. AI Assistant discovers API format from definitions (OpenAPI, GraphQL schema, etc.)
9. AI Assistant proposes adapter specifications (tech stack, domain model format, conventions, etc.)
10. Technical Lead reviews and approves proposed specs
11. AI Assistant updates adapter specs in the adapter specifications area
12. AI Assistant updates the adapter's AI navigation rules with WHEN rules for each spec

**Postconditions**: Adapter with auto-generated specs from existing codebase, validated and ready for Cypilot workflows

---

### UC-011 Configure CI/CD Pipeline for Cypilot Validation

**ID**: `cpt-cypilot-usecase-configure-cicd`

**Actors**:
`cpt-cypilot-actor-devops-engineer`, `cpt-cypilot-actor-ci-pipeline`

**Preconditions**: Project has Cypilot adapter configured (triggers `cpt-cypilot-usecase-bootstrap-project`)

**Flow**:

1. DevOps Engineer wants to automate Cypilot artifact validation in CI/CD
2. DevOps Engineer reads the adapter build/deploy specification for test and build commands (uses capability `cpt-cypilot-fr-adapter-config`)
3. DevOps Engineer creates GitHub Actions workflow or GitLab CI config
4. Workflow configured to run `/cypilot analyze` on changed artifacts in pull requests
5. CI/CD Pipeline executes validation automatically on every commit (uses capability `cpt-cypilot-fr-validation`)
6. Pipeline reports validation results as PR status checks
7. Pipeline blocks merge if any artifact validation fails (uses capability `cpt-cypilot-fr-validation`)
8. DevOps Engineer configures notifications for validation failures

**Postconditions**: CI/CD Pipeline automatically validates all Cypilot artifacts, prevents invalid designs from being merged

---

### UC-012 Security Review of Spec Design

**ID**: `cpt-cypilot-usecase-security-review`

**Actors**:
`cpt-cypilot-actor-security-engineer`, `cpt-cypilot-actor-architect`

**Preconditions**: Spec Design exists and validated (triggers `cpt-cypilot-usecase-design-spec`)

**Flow**:

1. Security Engineer receives notification that new spec design ready for review
2. Security Engineer reviews spec design content to identify data flows, trust boundaries, and sensitive data handling (uses capability `cpt-cypilot-fr-design-first`)
3. Security Engineer reviews authentication and authorization expectations
4. Security Engineer identifies missing security controls or vulnerabilities (uses capability `cpt-cypilot-fr-validation`)
5. Security Engineer adds security requirements with stable IDs `cpt-<project>-spec-<spec>-req-security-*`
6. Architect updates the spec design based on security feedback (triggers `cpt-cypilot-usecase-update-spec-design`)
7. Security Engineer approves design after security requirements are added

**Postconditions**: Spec design includes comprehensive security requirements, ready for secure implementation

---

### UC-013 Product Requirements Analysis

**ID**: `cpt-cypilot-usecase-prd-analysis`

**Actors**:
`cpt-cypilot-actor-prd-analyst`, `cpt-cypilot-actor-product-manager`

**Preconditions**: Stakeholder requirements gathered but not yet documented in Cypilot format

**Flow**:

1. Business Analyst collects raw requirements from stakeholders (interviews, documents, meetings)
2. Business Analyst analyzes requirements and identifies actors (human and system)
3. Business Analyst groups related requirements into capabilities (uses capability `cpt-cypilot-fr-design-first`)
4. Business Analyst creates draft structure for the PRD with actors and capabilities
5. Business Analyst works with Product Manager to refine vision and success criteria
6. Product Manager runs `/cypilot-prd` with Business Analyst's draft (uses capability `cpt-cypilot-fr-workflow-execution`)
7. AI Assistant updates the PRD based on analyzed requirements
8. Business Analyst reviews generated PRD for completeness and accuracy (uses capability `cpt-cypilot-fr-validation`)
9. Business Analyst confirms all stakeholder requirements covered by capabilities

**Postconditions**: Well-structured PRD capturing all stakeholder requirements in Cypilot format (triggers `cpt-cypilot-usecase-create-prd`)

---

### UC-014 Design User Interface from Flows

**ID**: `cpt-cypilot-usecase-design-ui`

**Actors**:
`cpt-cypilot-actor-ux-designer`, `cpt-cypilot-actor-architect`

**Preconditions**: Spec design exists with documented actor flows (triggers `cpt-cypilot-usecase-design-spec`)

**Flow**:

1. UX Designer reviews the spec design actor flows to understand user journeys (uses capability `cpt-cypilot-fr-design-first`)
2. UX Designer identifies UI screens needed for each flow step
3. UX Designer creates wireframes mapping each Cypilot DSL (CDSL) instruction to UI element
4. For each flow phase (p1, p2, etc.), UX Designer designs corresponding screen state
5. UX Designer validates that UI covers all actor interactions from flows (uses capability `cpt-cypilot-fr-traceability`)
6. UX Designer creates UI mockups with annotations linking to flow IDs (e.g., "Implements `cpt-<project>-spec-<spec>-flow-<name>:p1`")
7. Architect reviews UI mockups against the spec design to ensure completeness
8. UX Designer updates UI based on feedback if flows were unclear
9. Architect may update the spec design actor flows if UI reveals missing flow steps (triggers `cpt-cypilot-usecase-update-spec-design`)

**Postconditions**: UI mockups fully aligned with spec flows, developers can code UI following both mockups and spec design

---

### UC-015 Plan Release with Spec Tracking

**ID**: `cpt-cypilot-usecase-plan-release`

**Actors**:
`cpt-cypilot-actor-release-manager`, `cpt-cypilot-actor-project-manager`

**Preconditions**: Overall Design exists and needs to be decomposed into spec-level scope

**Flow**:

1. Architect and Project Manager review Overall Design to identify spec boundaries
2. Team defines spec list and assigns initial statuses (NOT_STARTED, IN_DESIGN)
3. Architect designs specs iteratively (IN_DESIGN → DESIGNED → READY)
4. Developers code specs (IN_PROGRESS → DONE)
5. Validation is run after each meaningful update (uses capability `cpt-cypilot-fr-validation`)

**Postconditions**: Clear visibility into spec progress, automated status tracking, dependency validation, historical metrics for planning

---

### UC-016 Record Architecture Decision

**ID**: `cpt-cypilot-usecase-record-adr`

**Actors**:
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`

**Preconditions**: Architecture decision needs to be documented

**Flow**:

1. Architect identifies significant technical decision requiring documentation
2. Architect runs `/cypilot-adr` to create new ADR (uses capability `cpt-cypilot-fr-workflow-execution`)
3. AI Assistant assigns sequential ADR ID (e.g., ADR-0001, ADR-0002)
4. Architect documents decision context, considered options, and chosen solution (uses capability `cpt-cypilot-fr-arch-decision-mgmt`)
5. ADR is created with status ACCEPTED
6. AI Assistant updates affected design sections to reference ADR (uses capability `cpt-cypilot-fr-traceability`)

**Postconditions**: Architecture decision documented with full context, linked to affected design elements, searchable by status and component

---

### UC-017 Generate Code from Spec Design

**ID**: `cpt-cypilot-usecase-generate-code`

**Actors**:
`cpt-cypilot-actor-developer`, `cpt-cypilot-actor-ai-assistant`

**Preconditions**: Spec scope is known (spec design may or may not exist)

**Flow**:

1. Developer wants to generate initial code scaffolding
2. If spec design is missing, AI Assistant bootstraps the minimal spec design (uses capability `cpt-cypilot-fr-design-first`)
3. AI Assistant reads adapter specs for language-specific patterns and project conventions (uses capability `cpt-cypilot-fr-adapter-config`)
4. AI Assistant uses adapter-defined domain model and API contract sources when present (uses capability `cpt-cypilot-fr-code-generation`)
5. AI Assistant generates code scaffolding and test scaffolding following best practices (uses capability `cpt-cypilot-fr-code-generation`)
6. AI Assistant adds traceability tags when enabled (uses capability `cpt-cypilot-fr-traceability`)
7. Developer runs `/cypilot-code` to continue implementation from the validated spec design
8. Developer reviews generated code and adjusts as needed

**Postconditions**: Code scaffolding generated with proper structure and traceability tags when enabled, developer can focus on business logic implementation

---

### UC-018 Navigate Traceability in IDE

**ID**: `cpt-cypilot-usecase-ide-navigation`

**Actors**:
`cpt-cypilot-actor-developer`

**Preconditions**: VS Code Cypilot extension installed, project has Cypilot artifacts

**Flow**:

1. Developer opens Spec Design in VS Code
2. Developer sees Cypilot ID cpt-cypilot-seq-intent-to-workflow highlighted with syntax coloring (uses capability `cpt-cypilot-fr-ide-integration`)
3. Developer Cmd+Click (or Ctrl+Click) on flow ID to jump to definition in same file
4. Developer right-clicks on flow ID and selects "Find where-used" from context menu
5. IDE shows list of references in design docs and code files (uses capability `cpt-cypilot-fr-traceability`)
6. Developer clicks on code reference to navigate to implementation file
7. Developer sees inline validation errors if ID format is incorrect
8. Developer uses autocomplete to insert valid Cypilot IDs when editing
9. Code lens above function shows traceability status (✅ tagged or ⚠️ missing tags)

**Postconditions**: Developer can navigate between design and code instantly, maintain traceability without manual searching

---

### UC-019 Migrate Existing Project to Cypilot

**ID**: `cpt-cypilot-usecase-migrate-project`

**Actors**:
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-documentation-writer`, `cpt-cypilot-actor-doc-generator`

**Preconditions**: Existing project with code but no Cypilot artifacts

**Flow**:

1. Technical Lead wants to adopt Cypilot for legacy project
2. AI Assistant runs `/cypilot-adapter-auto` to analyze existing codebase (uses capability `cpt-cypilot-fr-brownfield-support`)
3. AI Assistant scans existing project documentation for PRD content
4. AI Assistant proposes PRD content based on discovered information
5. Technical Lead reviews and refines proposed PRD content
6. AI Assistant analyzes code structure to extract architectural patterns
7. AI Assistant proposes Overall Design content from implementation patterns
8. Technical Lead identifies which specs to document first (incremental adoption)
9. AI Assistant creates or updates Spec Design for priority specs using the adapter-defined locations
10. Developer adds traceability tags to existing code incrementally (uses capability `cpt-cypilot-fr-traceability`)

**Postconditions**: Legacy project has Cypilot artifacts documenting current state, team can use Cypilot workflows for new specs while preserving existing code

---

### UC-020 Track Spec Progress Through Lifecycle

**ID**: `cpt-cypilot-usecase-track-spec-lifecycle`

**Actors**:
`cpt-cypilot-actor-project-manager`, `cpt-cypilot-actor-developer`

**Preconditions**: A Spec Manifest exists (when used) with multiple specs at various stages

**Flow**:

1. Project Manager opens a spec manifest to review current status (uses capability `cpt-cypilot-fr-spec-lifecycle`)
2. Project Manager sees spec statuses: ⏳ NOT_STARTED, 🔄 IN_PROGRESS, ✅ DONE
3. Developer marks spec as 🔄 IN_PROGRESS when starting implementation work
4. System validates spec has Spec Design at 100/100 before allowing IN_PROGRESS status
5. As developer completes implementation work, system suggests status update
6. Developer runs final validation before marking spec ✅ DONE (uses capability `cpt-cypilot-fr-validation`)
7. Project Manager tracks velocity by counting completed specs per sprint
8. Project Manager identifies blocking dependencies (Spec B depends on Spec A)
9. System alerts if Spec B IN_PROGRESS but Spec A still NOT_STARTED
10. Project Manager generates progress report showing spec completion timeline

**Postconditions**: Clear visibility into spec progress, automated status tracking, dependency validation, historical metrics for planning

---

### UC-022 Write Actor Flow in Cypilot DSL (CDSL)

**ID**: `cpt-cypilot-usecase-write-cdsl-flow`

**Actors**:
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-prd-analyst`

**Preconditions**: Spec Design exists, architect needs to document actor flow

**Flow**:

1. Architect opens the spec design and navigates to the actor flows
2. Architect creates new flow: "Login Flow" with ID cpt-cypilot-seq-intent-to-workflow (uses capability `cpt-cypilot-fr-design-first`)
3. Architect writes flow in Cypilot DSL (CDSL) using plain English with bold keywords (uses capability `cpt-cypilot-fr-cdsl`)
4. Business Analyst reviews the Cypilot DSL (CDSL) flow and confirms it matches product requirements
5. Business Analyst identifies missing case: "What if user forgot password?"
6. Architect adds step with **OPTIONAL** path to password reset
7. UX Designer reads flow and creates UI mockups matching each step and instruction
8. Architect marks instructions with phases for implementation: p1 (validation), p2 (authentication), p3 (session)
9. Developer reads the Cypilot DSL (CDSL) flow and understands exact implementation requirements without ambiguity

**Postconditions**: Actor flow documented in plain English readable by all stakeholders, directly translatable to code with instruction-level traceability

---

### UC-024 Validate PRD

**ID**: `cpt-cypilot-usecase-validate-prd`

**Actors**:
`cpt-cypilot-actor-product-manager`, `cpt-cypilot-actor-cypilot-tool`

**Preconditions**: PRD exists

**Flow**:

1. Product Manager runs `/cypilot-prd-validate` to request PRD validation
2. Cypilot Validation Tool validates structure, cross-references, and semantic boundaries (uses capability `cpt-cypilot-fr-validation`)
3. Tool reports PASS/FAIL with actionable issues

**Postconditions**: PRD validation status is known; issues are ready for remediation

**Alternative Flows**:
- **Validation fails**: If step 3 reports FAIL, Product Manager reviews issues, edits PRD to fix them, and re-runs validation (loop to step 1)

---

### UC-025 Create Overall Design

**ID**: `cpt-cypilot-usecase-create-overall-design`

**Actors**:
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-ai-assistant`

**Preconditions**: PRD exists and is deterministically validated

**Flow**:

1. Architect runs `/cypilot-design` and defines system-level scope, constraints, and key requirements
2. Technical Lead provides project-specific technical context via adapter (uses capability `cpt-cypilot-fr-adapter-config`)
3. AI Assistant drafts Overall Design with stable IDs and cross-references to PRD actors and capabilities
4. Cypilot Validation Tool runs deterministic validation for Overall Design by running `/cypilot-design-validate` (uses capability `cpt-cypilot-fr-validation`)

**Postconditions**: Overall Design exists and is deterministically validated

---

### UC-026 Update Overall Design

**ID**: `cpt-cypilot-usecase-update-overall-design`

**Actors**:
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-ai-assistant`

**Preconditions**: Overall Design exists

**Flow**:

1. Architect runs `/cypilot-design` in update mode and identifies what system-level decision, requirement, or constraint must change
2. AI Assistant proposes updates while preserving stable IDs where appropriate
3. Technical Lead checks alignment with project conventions and adapter configuration
4. Cypilot Validation Tool re-validates Overall Design by running `/cypilot-design-validate` (uses capability `cpt-cypilot-fr-validation`)

**Postconditions**: Overall Design updated and deterministically validated

---

### UC-027 Validate ADRs

**ID**: `cpt-cypilot-usecase-validate-adrs`

**Actors**:
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-cypilot-tool`

**Preconditions**: One or more ADRs exist

**Flow**:

1. Team runs `/cypilot-adr-validate` to request deterministic validation of ADRs
2. Cypilot Validation Tool checks required ADR fields, IDs, and cross-references (uses capability `cpt-cypilot-fr-validation`)
3. Tool reports PASS/FAIL with issues

**Postconditions**: ADR validation status is known; issues are ready for remediation

---

### UC-028 Create Spec Manifest

**ID**: `cpt-cypilot-usecase-create-spec-manifest`

**Actors**:
`cpt-cypilot-actor-project-manager`, `cpt-cypilot-actor-release-manager`, `cpt-cypilot-actor-ai-assistant`

**Preconditions**: PRD and Overall Design exist

**Flow**:

1. Project Manager runs `/cypilot-specs` and defines the initial spec list and statuses
2. Release Manager defines readiness expectations for releases
3. AI Assistant creates the Spec Manifest with stable IDs and deterministic status values (uses capability `cpt-cypilot-fr-spec-lifecycle`)
4. Cypilot Validation Tool validates the Spec Manifest structure and references by running `/cypilot-specs-validate` (uses capability `cpt-cypilot-fr-validation`)

**Postconditions**: Spec Manifest exists and is deterministically validated


## 9. Acceptance Criteria

- Deterministic validation output is actionable (clear file/line/pointer for every issue)
- A new user can complete adapter initialization and reach a first passing PRD validation within a reasonable onboarding session

## 10. Dependencies

| Dependency | Description | Criticality |
|------------|-------------|-------------|
| None | N/A | N/A |

## 11. Assumptions

- AI coding assistants (Claude Code, Cursor, etc.) can follow structured markdown workflows with embedded instructions.
- Developers have access to Python 3.6+ for running the `cypilot` CLI tool.
- Projects use Git for version control (adapter discovery relies on `.git` directory).
- Teams are willing to maintain design artifacts as part of their development workflow.

## 12. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI agent variability | Inconsistent artifact quality | Deterministic validation catches structural issues |
| Adoption resistance | Low adoption / bypassing the workflow | Incremental adoption + immediate validation value |
| Template rigidity | Template does not fit some project types | Adapters allow customization of artifact locations and optional sections |
