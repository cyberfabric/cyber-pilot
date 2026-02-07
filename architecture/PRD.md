<!-- cpt:#:prd -->
# PRD (Product Requirements Document): Cypilot

<!-- cpt:##:overview -->
## 1. Overview

<!-- cpt:paragraph:purpose -->
**Purpose**: Cypilot is a methodology and productized system for guiding software development through stable artifacts, deterministic validation, and repeatable workflows.
<!-- cpt:paragraph:purpose -->

<!-- cpt:paragraph:context -->
In this project, "Cypilot" means **Framework for Documentation and Development**: the project is developed by running workflows (flows), using skills/tools for deterministic checks, and iterating interactively with AI agents.
<!-- cpt:paragraph:context -->

**Target Users**:
<!-- cpt:list:target-users required="true" -->
- Development Teams - Building software with clear design documentation
- Technical Leads & Architects - Defining system architecture and technical decisions
- Product Managers - Capturing product requirements and use cases
- AI Coding Assistants - Executing workflows and validating artifacts
- QA Engineers - Verifying implementation matches design
- Documentation Writers - Creating comprehensive technical documentation
<!-- cpt:list:target-users -->

**Key Problems Solved**:
<!-- cpt:list:key-problems required="true" -->
- **Design-Code Disconnect**: Code diverges from design without single source of truth, leading to outdated documentation
- **Lack of Traceability**: Cannot track product requirements through design to implementation, making impact analysis difficult
- **Unstructured Development**: No repeatable process for design and implementation, causing inconsistent quality
- **AI Integration Challenges**: AI agents cannot follow methodology without structured guidance and machine-readable specifications
- **Validation Complexity**: Manual design reviews are time-consuming and miss structural issues
<!-- cpt:list:key-problems -->

**Success Criteria**:
<!-- cpt:list:success-criteria required="true" -->
- A new user can complete adapter initialization and reach a first passing PRD validation (`cypilot validate --artifact {project-root}/architecture/PRD.md`) in ≤ 60 minutes. (Baseline: not measured; Target: v1.0)
- Deterministic validation of the PRD completes in ≤ 3 seconds on a typical developer laptop. (Baseline: ~1s current; Target: v1.0)
- 100% of `cpt-cypilot-actor-*` IDs defined in the PRD are resolvable via deterministic search (`cypilot where-defined`) without ambiguity. (Baseline: 100% current; Target: v1.0)
- CI validation feedback for PRD changes is produced in ≤ 2 minutes from push to default branch. (Baseline: not measured; Target: v1.0)
- Users can apply a small PRD update (single section change) via `/cypilot-prd` in ≤ 10 minutes end-to-end, including re-validation. (Baseline: not measured; Target: v1.0)
<!-- cpt:list:success-criteria -->

**Capabilities**:
<!-- cpt:list:capabilities required="true" -->
- Execute workflows to create/update/validate artifacts
- Provide deterministic validation and traceability scanning
- Support adapter-driven configuration for different projects and tech stacks
<!-- cpt:list:capabilities -->
<!-- cpt:##:overview -->

---

<!-- cpt:##:actors -->
## 2. Actors

<!-- cpt:###:actor-title repeat="many" -->
### Product Manager

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-product-manager`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Defines product requirements, captures use cases, and documents PRD content using Cypilot workflows
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Architect

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-architect`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Designs system architecture, creates overall design documentation, and defines technical patterns
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Developer

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-developer`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Implements specs according to validated designs, adds traceability tags to code
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### QA Engineer

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-qa-engineer`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Validates implementation against design specifications and ensures test coverage
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Technical Lead

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-technical-lead`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Sets up project adapters, configures Cypilot for project-specific conventions
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Project Manager

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-project-manager`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Monitors development progress, ensures workflows are followed, tracks spec completion
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Documentation Writer

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-documentation-writer`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Creates and maintains project documentation using Cypilot artifacts as source
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### DevOps Engineer

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-devops-engineer`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Configures CI/CD pipelines, uses adapter specs for build and deployment automation
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Security Engineer

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-security-engineer`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Conducts security review of design and code, validates security requirements implementation
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Business Analyst

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-prd-analyst`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Analyzes product requirements and translates them into Cypilot format for Product Manager
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### UX Designer

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-ux-designer`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Designs user interfaces based on actor flows from spec design
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Performance Engineer

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-performance-engineer`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Defines performance targets, reviews designs for performance risks, and validates performance requirements implementation
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Database Architect

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-database-architect`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Designs data models and storage strategies, reviews domain model impacts, and validates database-related constraints
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Release Manager

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-release-manager`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Manages releases and tracks spec readiness using Cypilot artifacts (for example via a Spec Manifest when used)
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### AI Coding Assistant

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-ai-assistant`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Executes Cypilot workflows interactively, generates artifacts, and validates against requirements
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Cypilot Validation Tool

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-cypilot-tool`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Automated validation engine that checks artifact structure, ID formats, and traceability
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### CI/CD Pipeline

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-ci-pipeline`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Automatically validates Cypilot artifacts on every commit through GitHub Actions or GitLab CI
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Documentation Generator

<!-- cpt:id:actor -->
**ID**: `cpt-cypilot-actor-doc-generator`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Automatically generates external documentation from Cypilot artifacts (API docs, architecture diagrams)
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->
<!-- cpt:##:actors -->

---

<!-- cpt:##:frs -->
## 3. Functional Requirements

<!-- cpt:###:fr-title repeat="many" -->
### FR-001 Workflow-Driven Development

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-cypilot-fr-workflow-execution`

<!-- cpt:free:fr-summary -->
The system MUST provide a clear, documented workflow catalog that users and AI agents can execute. Artifact locations MUST be adapter-defined; workflows MUST NOT hardcode repository paths. The core workflow set MUST cover at least: Adapter bootstrap and configuration, PRD creation/update, Overall design creation/update, ADR creation/update, Spec design creation/update, Spec implementation (`implement` as the primary implementation workflow), and Deterministic validation workflows for the above artifacts and for code traceability (when enabled). The system MUST provide a unified agent entrypoint workflow (`/cypilot`) that selects and executes the appropriate workflow (create/update/validate) based on context, or runs `cypilot` tool commands when requested. This includes interactive question-answer flow with AI agents, automated validation after artifact creation, step-by-step guidance for complex operations, and independent workflows (no forced sequence).
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-product-manager`, `cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-project-manager`, `cpt-cypilot-actor-release-manager`, `cpt-cypilot-actor-developer`, `cpt-cypilot-actor-qa-engineer`, `cpt-cypilot-actor-security-engineer`, `cpt-cypilot-actor-performance-engineer`, `cpt-cypilot-actor-database-architect`, `cpt-cypilot-actor-devops-engineer`, `cpt-cypilot-actor-documentation-writer`, `cpt-cypilot-actor-prd-analyst`, `cpt-cypilot-actor-ux-designer`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-cypilot-tool`, `cpt-cypilot-actor-ci-pipeline`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-002 Artifact Structure Validation

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-cypilot-fr-validation`

<!-- cpt:free:fr-summary -->
Deterministic validators for structural checks (sections, IDs, format). Deterministic content validation for semantic quality and boundaries: Content MUST be internally consistent (no contradictions), Content MUST NOT include information that belongs in other artifacts, Content MUST include required information expected for the artifact kind, Content MUST be semantically consistent with upstream/downstream artifacts (no cross-artifact contradictions), Content MUST not omit critical details that are explicitly defined in other artifacts. Deterministic validation for key artifacts defined by the adapter (no hardcoded repository paths). 100-point scoring system with category breakdown. Pass/fail thresholds (typically ≥90 or 100/100). Cross-reference validation (actor/capability IDs). Placeholder detection (incomplete markers). Detailed issue reporting with recommendations.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-developer`, `cpt-cypilot-actor-qa-engineer`, `cpt-cypilot-actor-security-engineer`, `cpt-cypilot-actor-performance-engineer`, `cpt-cypilot-actor-database-architect`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-cypilot-tool`, `cpt-cypilot-actor-ci-pipeline`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-003 Adapter Configuration System

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-cypilot-fr-adapter-config`

<!-- cpt:free:fr-summary -->
Technology-agnostic core methodology. Project-specific adapter specifications. Adapter MUST define an explicit registry of artifacts and their properties (for example: locations, scope, normative vs context-only). Adapter MUST support per-artifact configuration, including enabling/disabling code traceability checks. Tech stack definition (languages, frameworks, tools). Domain model format specification. API contract format specification. Adapter MUST be able to define deterministic tools/commands used to validate domain model sources and API contract sources. Testing strategy and build tool configuration. Auto-detection from existing codebase.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-architect`, `cpt-cypilot-actor-database-architect`, `cpt-cypilot-actor-performance-engineer`, `cpt-cypilot-actor-devops-engineer`, `cpt-cypilot-actor-developer`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-004 Adaptive Design Bootstrapping

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-cypilot-fr-design-first`

<!-- cpt:free:fr-summary -->
Users MAY start implementation without having pre-existing design artifacts. When a workflow needs a traceability source and design artifacts are missing, the workflow MUST bootstrap the minimum viable design interactively and then continue. Once created, design artifacts become the single source of truth (code follows design). Design iteration MUST be workflow-driven and MUST be followed by deterministic validation. Clear separation between PRD, overall design, ADRs, and spec designs. Behavioral specifications MUST use Cypilot DSL (CDSL) (plain-English algorithms).
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-product-manager`, `cpt-cypilot-actor-architect`, `cpt-cypilot-actor-developer`, `cpt-cypilot-actor-prd-analyst`, `cpt-cypilot-actor-ux-designer`, `cpt-cypilot-actor-security-engineer`, `cpt-cypilot-actor-performance-engineer`, `cpt-cypilot-actor-database-architect`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-005 Traceability Management

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-cypilot-fr-traceability`

<!-- cpt:free:fr-summary -->
Unique ID system for all design elements using structured format. Code tags (@cpt-*) linking implementation to design. Traceability validation MUST be configurable per artifact (enabled/disabled via adapter). Cypilot-ID MAY be versioned by appending a `-vN` suffix (example: `<base-id>-v2`). When an identifier is replaced (REPLACE), the new identifier version MUST be incremented: If the prior identifier has no version suffix, the new identifier MUST end with `-v1`; If the prior identifier ends with `-vN`, the new identifier MUST increment the version by 1 (example: `-v1` → `-v2`). Once an identifier becomes versioned, the version suffix MUST NOT be removed in future references. When an identifier is replaced (REPLACE), all references MUST be updated (all artifacts and all code traceability tags, including qualified `:ph-N:inst-*` references). Qualified IDs for phases and instructions (:ph-N:inst-*). Repository-wide ID scanning and search. where-defined and where-used commands. Design-to-code validation (implemented items must have code tags).
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-developer`, `cpt-cypilot-actor-qa-engineer`, `cpt-cypilot-actor-cypilot-tool`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-006 Quickstart Guides

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-cypilot-fr-interactive-docs`

<!-- cpt:free:fr-summary -->
QUICKSTART guides with copy-paste prompts. Progressive disclosure (human-facing overview docs, AI navigation rules for agents).
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-documentation-writer`, `cpt-cypilot-actor-product-manager`, `cpt-cypilot-actor-release-manager`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-doc-generator`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-007 Artifact Templates

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-cypilot-fr-artifact-templates`

<!-- cpt:free:fr-summary -->
The system MUST provide an artifact template catalog for core Cypilot artifacts (PRD, Overall Design, ADRs, Spec Manifest, Spec Designs). Agents MUST be able to use these templates during workflow execution.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-documentation-writer`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-doc-generator`, `cpt-cypilot-actor-technical-lead`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-008 Artifact Examples

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-cypilot-fr-artifact-examples`

<!-- cpt:free:fr-summary -->
The system MUST provide an artifact example catalog for core Cypilot artifacts (PRD, Overall Design, ADRs, Spec Manifest, Spec Designs). Agents MUST be able to use these examples during workflow execution.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-documentation-writer`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-doc-generator`, `cpt-cypilot-actor-technical-lead`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-009 ADR Management

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-cypilot-fr-arch-decision-mgmt`

<!-- cpt:free:fr-summary -->
Create and track architecture decisions with structured format. Link ADRs to affected design sections and spec IDs. Decision status tracking (PROPOSED, ACCEPTED, DEPRECATED, SUPERSEDED). Impact analysis when ADR changes affect multiple specs. Search ADRs by status, date, or affected components. Version history for decision evolution.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-security-engineer`, `cpt-cypilot-actor-performance-engineer`, `cpt-cypilot-actor-database-architect`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-010 PRD Management

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-cypilot-fr-prd-mgmt`

<!-- cpt:free:fr-summary -->
Create and update PRD content through workflows. Enforce stable IDs for actors and capabilities. PRD deterministic validation integration.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-product-manager`, `cpt-cypilot-actor-prd-analyst`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-cypilot-tool`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-011 Overall Design Management

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-cypilot-fr-overall-design-mgmt`

<!-- cpt:free:fr-summary -->
Create and update Overall Design through workflows. Link requirements to PRD actors and capabilities. Deterministic validation integration for Overall Design.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-cypilot-tool`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-012 Spec Manifest Management

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-cypilot-fr-spec-manifest-mgmt`

<!-- cpt:free:fr-summary -->
Create and update Spec Manifest (DECOMPOSITION) through workflows. Maintain stable IDs for specs and tracking fields. Deterministic validation integration for Spec Manifest.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-project-manager`, `cpt-cypilot-actor-release-manager`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-cypilot-tool`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-013 Spec Design Management

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-cypilot-fr-spec-design-mgmt`

<!-- cpt:free:fr-summary -->
Create and update Spec Design through workflows. Maintain stable IDs for flows, algorithms, and requirements. Deterministic validation integration for Spec Design.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-cypilot-tool`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-014 Spec Lifecycle Management

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-cypilot-fr-spec-lifecycle`

<!-- cpt:free:fr-summary -->
Track spec status from NOT_STARTED through IN_DESIGN, DESIGNED, READY, IN_PROGRESS to DONE. Track progress using the project's selected spec tracking approach (for example a spec manifest when used). Spec dependency management and blocking detection. Milestone tracking and release planning integration. Historical spec completion metrics and velocity tracking. Status transition validation (cannot skip states).
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-project-manager`, `cpt-cypilot-actor-release-manager`, `cpt-cypilot-actor-developer`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-015 Code Generation from Design

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-cypilot-fr-code-generation`

<!-- cpt:free:fr-summary -->
Provide an implementation process that is adapter-aware and works with any programming language. Apply general best practices that are applicable across languages. Prefer TDD where feasible and follow SOLID principles. Use adapter-defined domain model and API contract sources when present. Add traceability tags when traceability is enabled for the relevant artifacts.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-developer`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-016 Brownfield Support

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-cypilot-fr-brownfield-support`

<!-- cpt:free:fr-summary -->
Add Cypilot to existing projects without disruption. Auto-detect existing architecture from code and configs. Reverse-engineer the PRD from requirements documentation. Extract Overall Design patterns from implementation. Incremental Cypilot adoption (start with adapter, add artifacts gradually). Legacy system integration with minimal refactoring.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-architect`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-017 Cypilot DSL (CDSL)

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-cypilot-fr-cdsl`

<!-- cpt:free:fr-summary -->
Plain English algorithm description language for actor flows (Cypilot DSL, abbreviated CDSL). Structured numbered lists with bold keywords (**IF**, **ELSE**, **WHILE**, **FOR EACH**). Instruction markers with checkboxes (- [ ] Inst-label: description). Phase-based organization (p1, p2, etc.) for implementation tracking. Readable by non-programmers for validation and review. Translates directly to code with traceability tags. Keywords: **AND**, **OR**, **NOT**, **MUST**, **REQUIRED**, **OPTIONAL**. Actor-centric (steps start with **Actor** or **System**).
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-developer`, `cpt-cypilot-actor-prd-analyst`, `cpt-cypilot-actor-ux-designer`, `cpt-cypilot-actor-product-manager`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-018 IDE Integration and Tooling

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [ ] `p3` - **ID**: `cpt-cypilot-fr-ide-integration`

<!-- cpt:free:fr-summary -->
VS Code extension for Cypilot artifact editing. Click-to-navigate for Cypilot IDs (jump to definition). where-used and where-defined commands in IDE. Inline validation errors and warnings. Autocomplete for Cypilot IDs and section references. Syntax highlighting for Cypilot DSL (CDSL). Integration with `cypilot` skill commands. Code lens showing traceability status.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-developer`, `cpt-cypilot-actor-architect`, `cpt-cypilot-actor-devops-engineer`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-019 Multi-Agent IDE Integration

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-cypilot-fr-multi-agent-integration`

<!-- cpt:free:fr-summary -->
The system MUST provide a unified `agents` command to generate and maintain agent-specific workflow proxy files and skill entry points for multiple AI coding assistants. Supported agents MUST include Claude, Cursor, Windsurf, and Copilot. The `agents` command MUST generate workflow entry points in each agent's native format (e.g., `.claude/commands/`, `.cursor/commands/`, `.windsurf/workflows/`, `.github/prompts/`) and skill/rule entry points that point to the core Cypilot skill. Configuration MUST be externalized to a unified JSON file (`cypilot-agents.json`) with sensible defaults for recognized agents.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-devops-engineer`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-020 Extensible Kit Package System

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-cypilot-fr-rules-packages`

<!-- cpt:free:fr-summary -->
The system MUST support extensible kit packages that define templates, checklists, and validation rules for artifact types. Each kit package MUST be identified in the adapter registry and MUST contain a `template.md` file with Cypilot markers for each artifact kind. Kit packages MAY contain `checklist.md` for semantic validation criteria and `rules.md` for generation guidance. The `validate-kits` command MUST validate that kit packages are structurally correct and that templates follow the cypilot-template frontmatter specification.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-cypilot-tool`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-021 Template Quality Assurance

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-cypilot-fr-template-qa`

<!-- cpt:free:fr-summary -->
The system MUST provide a `self-check` command that validates example artifacts against their templates. The adapter registry MAY define `templates` entries with `template_path`, `example_path`, and `validation_level` properties. When `validation_level` is `STRICT`, the self-check command MUST validate that the example artifact passes all template validation rules. This ensures that templates and examples remain synchronized and that templates are valid.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-cypilot-tool`, `cpt-cypilot-actor-documentation-writer`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-022 Cross-Artifact Validation

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-cypilot-fr-cross-artifact-validation`

<!-- cpt:free:fr-summary -->
The system MUST validate cross-artifact relationships when multiple artifacts are validated together. ID blocks with `covered_by` attributes MUST have at least one reference in artifacts whose template kind matches the covered_by list. All ID references MUST resolve to a definition in some artifact. When a reference is marked as checked (`[x]`), the corresponding definition MUST also be marked as checked. Cross-artifact validation MUST be deterministic and report all consistency violations with line numbers and artifact paths.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-cypilot-tool`, `cpt-cypilot-actor-ci-pipeline`, `cpt-cypilot-actor-architect`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-023 Hierarchical System Registry

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-cypilot-fr-hierarchical-registry`

<!-- cpt:free:fr-summary -->
The system MUST support hierarchical organization of systems in the artifacts registry. Each system MUST have a `name`, `rules` reference, and lists of `artifacts` and optional `codebase` entries. Systems MAY have `children` arrays for nested subsystems. Each artifact entry MUST specify `name`, `path`, `kind`, and `traceability` level (`FULL` or `DOCS-ONLY`). Each codebase entry MUST specify `name`, `path`, and `extensions` for code scanning. The `adapter-info` command MUST display the resolved hierarchical structure.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-cypilot-tool`, `cpt-cypilot-actor-architect`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->
<!-- cpt:##:frs -->

---

<!-- cpt:##:usecases -->
## 4. Use Cases

<!-- cpt:###:uc-title repeat="many" -->
### UC-001 Bootstrap New Project with Cypilot

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-bootstrap-project`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Project repository exists with Git initialized
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Technical Lead initiates Cypilot setup by requesting AI Assistant to add the Cypilot framework
2. AI Assistant establishes minimal adapter configuration (uses capability `cpt-cypilot-fr-adapter-config`)
3. If adapter is missing, the system offers to bootstrap it; the user MAY decline and continue with reduced automation
4. The system confirms that adapter discovery is possible when the adapter exists
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Project has working Cypilot adapter, ready for PRD and design workflows
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-002 Create PRD

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-create-prd`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-product-manager`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Project context exists; adapter may or may not exist
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Product Manager runs `/cypilot-prd` and asks AI Assistant to create or refine PRD
2. AI Assistant asks questions about vision, target users, and problems solved
3. Product Manager answers; AI Assistant proposes PRD content based on available context
4. AI Assistant defines actors and capabilities with stable IDs (uses capability `cpt-cypilot-fr-traceability`)
5. AI Assistant updates the PRD according to answers
6. Product Manager validates PRD by running `/cypilot-prd-validate` (see `cpt-cypilot-usecase-validate-prd`)
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Valid PRD exists, project ready for overall design workflow
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-003 Design Spec with AI Assistance

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-design-spec`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-database-architect`, `cpt-cypilot-actor-performance-engineer`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: PRD and Overall Design validated, spec scope identified (from backlog, ticket, or code context)
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Architect runs `/cypilot-spec` and specifies the spec scope and desired outcomes
2. AI Assistant helps define actor flows in Cypilot DSL (CDSL) (uses capability `cpt-cypilot-fr-design-first`)
3. Architect defines requirements, constraints, and interfaces at spec scope
4. Architect runs `/cypilot-spec-validate`; the system validates the Spec Design deterministically (uses capability `cpt-cypilot-fr-validation`)
5. Validation reports 100/100 score (required for spec design)
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Spec Design validated at 100/100, ready for implementation
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-004 Validate Design Against Requirements - Overall Design

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-validate-design`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-cypilot-tool`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Overall Design exists with requirements, actors, and capabilities defined
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Architect runs `/cypilot-design-validate` to request deterministic validation of overall design
2. The system validates structure, required content, and cross-artifact consistency (uses capability `cpt-cypilot-fr-validation`)
3. The system validates ID formats and cross-references (uses capability `cpt-cypilot-fr-traceability`)
4. The system reports a score breakdown with actionable issues
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Validation report shows PASS (≥90/100) or FAIL with actionable issues, Architect fixes issues or proceeds to next workflow
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-005 Trace Requirement to Implementation

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-trace-requirement`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-developer`, `cpt-cypilot-actor-cypilot-tool`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Spec Design exists; implementation exists (partial or complete); traceability tags are present when traceability is enabled
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Developer selects a requirement ID to verify
2. The system locates the normative definition and where it is used (uses capability `cpt-cypilot-fr-traceability`)
3. The system reports traceability coverage and gaps
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Developer confirms requirement is fully implemented with proper traceability, or identifies missing implementation
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-006 Update Existing Spec Design

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-update-spec-design`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Spec Design exists and previously validated at 100/100 (triggers `cpt-cypilot-usecase-design-spec`)
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Architect identifies need to add new algorithm to existing spec
2. AI Assistant runs `/cypilot-spec` in update mode, loads existing spec design, and presents current content
3. AI Assistant asks: "What to update?" with options (Add actor flow, Edit algorithm, Add requirement, etc.)
4. Architect selects "Add new algorithm" option
5. Architect specifies new algorithm details in Cypilot DSL (CDSL) (uses capability `cpt-cypilot-fr-design-first`)
6. AI Assistant updates Spec Design while preserving unchanged sections
7. AI Assistant generates new algorithm ID following format `cpt-<project>-spec-<spec>-algo-<name>` (uses capability `cpt-cypilot-fr-traceability`)
8. Cypilot Validation Tool re-validates the updated design by running `/cypilot-spec-validate` (uses capability `cpt-cypilot-fr-validation`)
9. Validation confirms 100/100 score maintained
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Spec Design updated with new algorithm, fully validated, ready for implementation
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-007 Implement Spec

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-plan-implementation`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-developer`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Spec Design exists with a sufficiently clear traceability source (validated when possible)
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Developer requests to code the spec
2. AI Assistant executes `/cypilot-code` workflow (uses capability `cpt-cypilot-fr-workflow-execution`)
3. The system uses Spec Design to extract the minimal implementation scope
4. AI Assistant and Developer code iteratively, keeping design and code aligned
5. Developer adds code traceability tags where used (uses capability `cpt-cypilot-fr-traceability`)
6. Cypilot Validation Tool validates implementation and traceability by running `/cypilot-code-validate` (uses capability `cpt-cypilot-fr-validation`)
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Spec implemented with traceability where used, and validation indicates completeness
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-009 Validate Spec Implementation

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-validate-implementation`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-qa-engineer`, `cpt-cypilot-actor-cypilot-tool`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Spec implementation exists (partial or complete)
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. QA Engineer runs `/cypilot-code-validate` to request validation of spec implementation
2. Cypilot Validation Tool validates codebase traceability when enabled (uses capability `cpt-cypilot-fr-validation`)
3. Tool validates prerequisite design artifacts first
4. For each `[x]` marked scope in design, tool expects matching tags in code when traceability is enabled (uses capability `cpt-cypilot-fr-traceability`)
5. For each `[x]` marked Cypilot DSL (CDSL) instruction, tool expects instruction-level tag in code when traceability is enabled
6. Tool reports missing tags, extra tags, and format issues
7. Tool checks build passes and tests run successfully
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Validation report shows full traceability or lists missing/incorrect tags, QA Engineer confirms implementation complete or requests fixes
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-010 Auto-Generate Adapter from Codebase

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-auto-generate-adapter`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Project has existing codebase with code, configs, and documentation
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
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
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Adapter with auto-generated specs from existing codebase, validated and ready for Cypilot workflows
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-011 Configure CI/CD Pipeline for Cypilot Validation

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-configure-cicd`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-devops-engineer`, `cpt-cypilot-actor-ci-pipeline`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Project has Cypilot adapter configured (triggers `cpt-cypilot-usecase-bootstrap-project`)
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. DevOps Engineer wants to automate Cypilot artifact validation in CI/CD
2. DevOps Engineer reads the adapter build/deploy specification for test and build commands (uses capability `cpt-cypilot-fr-adapter-config`)
3. DevOps Engineer creates GitHub Actions workflow or GitLab CI config
4. Workflow configured to run `/cypilot analyze` on changed artifacts in pull requests
5. CI/CD Pipeline executes validation automatically on every commit (uses capability `cpt-cypilot-fr-validation`)
6. Pipeline reports validation results as PR status checks
7. Pipeline blocks merge if any artifact validation fails (uses capability `cpt-cypilot-fr-validation`)
8. DevOps Engineer configures notifications for validation failures
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: CI/CD Pipeline automatically validates all Cypilot artifacts, prevents invalid designs from being merged
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-012 Security Review of Spec Design

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-security-review`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-security-engineer`, `cpt-cypilot-actor-architect`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Spec Design exists and validated (triggers `cpt-cypilot-usecase-design-spec`)
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Security Engineer receives notification that new spec design ready for review
2. Security Engineer reviews spec design content to identify data flows, trust boundaries, and sensitive data handling (uses capability `cpt-cypilot-fr-design-first`)
3. Security Engineer reviews authentication and authorization expectations
4. Security Engineer identifies missing security controls or vulnerabilities (uses capability `cpt-cypilot-fr-validation`)
5. Security Engineer adds security requirements with stable IDs `cpt-<project>-spec-<spec>-req-security-*`
6. Architect updates the spec design based on security feedback (triggers `cpt-cypilot-usecase-update-spec-design`)
7. Security Engineer approves design after security requirements are added
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Spec design includes comprehensive security requirements, ready for secure implementation
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-013 Product Requirements Analysis

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-prd-analysis`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-prd-analyst`, `cpt-cypilot-actor-product-manager`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Stakeholder requirements gathered but not yet documented in Cypilot format
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Business Analyst collects raw requirements from stakeholders (interviews, documents, meetings)
2. Business Analyst analyzes requirements and identifies actors (human and system)
3. Business Analyst groups related requirements into capabilities (uses capability `cpt-cypilot-fr-design-first`)
4. Business Analyst creates draft structure for the PRD with actors and capabilities
5. Business Analyst works with Product Manager to refine vision and success criteria
6. Product Manager runs `/cypilot-prd` with Business Analyst's draft (uses capability `cpt-cypilot-fr-workflow-execution`)
7. AI Assistant updates the PRD based on analyzed requirements
8. Business Analyst reviews generated PRD for completeness and accuracy (uses capability `cpt-cypilot-fr-validation`)
9. Business Analyst confirms all stakeholder requirements covered by capabilities
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Well-structured PRD capturing all stakeholder requirements in Cypilot format (triggers `cpt-cypilot-usecase-create-prd`)
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-014 Design User Interface from Flows

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-design-ui`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-ux-designer`, `cpt-cypilot-actor-architect`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Spec design exists with documented actor flows (triggers `cpt-cypilot-usecase-design-spec`)
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. UX Designer reviews the spec design actor flows to understand user journeys (uses capability `cpt-cypilot-fr-design-first`)
2. UX Designer identifies UI screens needed for each flow step
3. UX Designer creates wireframes mapping each Cypilot DSL (CDSL) instruction to UI element
4. For each flow phase (p1, p2, etc.), UX Designer designs corresponding screen state
5. UX Designer validates that UI covers all actor interactions from flows (uses capability `cpt-cypilot-fr-traceability`)
6. UX Designer creates UI mockups with annotations linking to flow IDs (e.g., "Implements `cpt-<project>-spec-<spec>-flow-<name>:p1`")
7. Architect reviews UI mockups against the spec design to ensure completeness
8. UX Designer updates UI based on feedback if flows were unclear
9. Architect may update the spec design actor flows if UI reveals missing flow steps (triggers `cpt-cypilot-usecase-update-spec-design`)
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: UI mockups fully aligned with spec flows, developers can code UI following both mockups and spec design
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-015 Plan Release with Spec Tracking

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-plan-release`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-release-manager`, `cpt-cypilot-actor-project-manager`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Overall Design exists and needs to be decomposed into spec-level scope
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Architect and Project Manager review Overall Design to identify spec boundaries
2. Team defines spec list and assigns initial statuses (NOT_STARTED, IN_DESIGN)
3. Architect designs specs iteratively (IN_DESIGN → DESIGNED → READY)
4. Developers code specs (IN_PROGRESS → DONE)
5. Validation is run after each meaningful update (uses capability `cpt-cypilot-fr-validation`)
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Clear visibility into spec progress, automated status tracking, dependency validation, historical metrics for planning
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-016 Record Architecture Decision

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-record-adr`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Architecture decision needs to be documented
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Architect identifies significant technical decision requiring documentation
2. Architect runs `/cypilot-adr` to create new ADR (uses capability `cpt-cypilot-fr-workflow-execution`)
3. AI Assistant assigns sequential ADR ID (e.g., ADR-0001, ADR-0002)
4. Architect documents decision context, considered options, and chosen solution (uses capability `cpt-cypilot-fr-arch-decision-mgmt`)
5. ADR is created with status ACCEPTED
6. AI Assistant updates affected design sections to reference ADR (uses capability `cpt-cypilot-fr-traceability`)
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Architecture decision documented with full context, linked to affected design elements, searchable by status and component
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-017 Generate Code from Spec Design

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-generate-code`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-developer`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Spec scope is known (spec design may or may not exist)
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Developer wants to generate initial code scaffolding
2. If spec design is missing, AI Assistant bootstraps the minimal spec design (uses capability `cpt-cypilot-fr-design-first`)
3. AI Assistant reads adapter specs for language-specific patterns and project conventions (uses capability `cpt-cypilot-fr-adapter-config`)
4. AI Assistant uses adapter-defined domain model and API contract sources when present (uses capability `cpt-cypilot-fr-code-generation`)
5. AI Assistant generates code scaffolding and test scaffolding following best practices (uses capability `cpt-cypilot-fr-code-generation`)
6. AI Assistant adds traceability tags when enabled (uses capability `cpt-cypilot-fr-traceability`)
7. Developer runs `/cypilot-code` to continue implementation from the validated spec design
8. Developer reviews generated code and adjusts as needed
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Code scaffolding generated with proper structure and traceability tags when enabled, developer can focus on business logic implementation
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-018 Navigate Traceability in IDE

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-ide-navigation`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-developer`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: VS Code Cypilot extension installed, project has Cypilot artifacts
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Developer opens Spec Design in VS Code
2. Developer sees Cypilot ID `cpt-cypilot-seq-intent-to-workflow` highlighted with syntax coloring (uses capability `cpt-cypilot-fr-ide-integration`)
3. Developer Cmd+Click (or Ctrl+Click) on flow ID to jump to definition in same file
4. Developer right-clicks on flow ID and selects "Find where-used" from context menu
5. IDE shows list of references in design docs and code files (uses capability `cpt-cypilot-fr-traceability`)
6. Developer clicks on code reference to navigate to implementation file
7. Developer sees inline validation errors if ID format is incorrect
8. Developer uses autocomplete to insert valid Cypilot IDs when editing
9. Code lens above function shows traceability status (✅ tagged or ⚠️ missing tags)
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Developer can navigate between design and code instantly, maintain traceability without manual searching
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-019 Migrate Existing Project to Cypilot

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-migrate-project`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-ai-assistant`, `cpt-cypilot-actor-documentation-writer`, `cpt-cypilot-actor-doc-generator`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Existing project with code but no Cypilot artifacts
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
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
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Legacy project has Cypilot artifacts documenting current state, team can use Cypilot workflows for new specs while preserving existing code
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-020 Track Spec Progress Through Lifecycle

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-track-spec-lifecycle`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-project-manager`, `cpt-cypilot-actor-developer`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: A Spec Manifest exists (when used) with multiple specs at various stages
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
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
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Clear visibility into spec progress, automated status tracking, dependency validation, historical metrics for planning
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-022 Write Actor Flow in Cypilot DSL (CDSL)

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-write-cdsl-flow`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-prd-analyst`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Spec Design exists, architect needs to document actor flow
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Architect opens the spec design and navigates to the actor flows
2. Architect creates new flow: "Login Flow" with ID `cpt-cypilot-seq-intent-to-workflow` (uses capability `cpt-cypilot-fr-design-first`)
3. Architect writes flow in Cypilot DSL (CDSL) using plain English with bold keywords (uses capability `cpt-cypilot-fr-cdsl`)
4. Business Analyst reviews the Cypilot DSL (CDSL) flow and confirms it matches product requirements
5. Business Analyst identifies missing case: "What if user forgot password?"
6. Architect adds step with **OPTIONAL** path to password reset
7. UX Designer reads flow and creates UI mockups matching each step and instruction
8. Architect marks instructions with phases for implementation: p1 (validation), p2 (authentication), p3 (session)
9. Developer reads the Cypilot DSL (CDSL) flow and understands exact implementation requirements without ambiguity
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Actor flow documented in plain English readable by all stakeholders, directly translatable to code with instruction-level traceability
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-024 Validate PRD

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-validate-prd`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-product-manager`, `cpt-cypilot-actor-cypilot-tool`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: PRD exists
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Product Manager runs `/cypilot-prd-validate` to request PRD validation
2. Cypilot Validation Tool validates structure, cross-references, and semantic boundaries (uses capability `cpt-cypilot-fr-validation`)
3. Tool reports PASS/FAIL with actionable issues
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: PRD validation status is known; issues are ready for remediation
<!-- cpt:paragraph:postconditions -->

**Alternative Flows**:
<!-- cpt:list:alternative-flows -->
- **Validation fails**: If step 3 reports FAIL, Product Manager reviews issues, edits PRD to fix them, and re-runs validation (loop to step 1)
<!-- cpt:list:alternative-flows -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-025 Create Overall Design

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-create-overall-design`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: PRD exists and is deterministically validated
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Architect runs `/cypilot-design` and defines system-level scope, constraints, and key requirements
2. Technical Lead provides project-specific technical context via adapter (uses capability `cpt-cypilot-fr-adapter-config`)
3. AI Assistant drafts Overall Design with stable IDs and cross-references to PRD actors and capabilities
4. Cypilot Validation Tool runs deterministic validation for Overall Design by running `/cypilot-design-validate` (uses capability `cpt-cypilot-fr-validation`)
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Overall Design exists and is deterministically validated
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-026 Update Overall Design

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-update-overall-design`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: Overall Design exists
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Architect runs `/cypilot-design` in update mode and identifies what system-level decision, requirement, or constraint must change
2. AI Assistant proposes updates while preserving stable IDs where appropriate
3. Technical Lead checks alignment with project conventions and adapter configuration
4. Cypilot Validation Tool re-validates Overall Design by running `/cypilot-design-validate` (uses capability `cpt-cypilot-fr-validation`)
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Overall Design updated and deterministically validated
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-027 Validate ADRs

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-validate-adrs`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-architect`, `cpt-cypilot-actor-technical-lead`, `cpt-cypilot-actor-cypilot-tool`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: One or more ADRs exist
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Team runs `/cypilot-adr-validate` to request deterministic validation of ADRs
2. Cypilot Validation Tool checks required ADR fields, IDs, and cross-references (uses capability `cpt-cypilot-fr-validation`)
3. Tool reports PASS/FAIL with issues
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: ADR validation status is known; issues are ready for remediation
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

---

<!-- cpt:###:uc-title repeat="many" -->
### UC-028 Create Spec Manifest

<!-- cpt:id:usecase -->
**ID**: `cpt-cypilot-usecase-create-spec-manifest`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-cypilot-actor-project-manager`, `cpt-cypilot-actor-release-manager`, `cpt-cypilot-actor-ai-assistant`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: PRD and Overall Design exist
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**:
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Project Manager runs `/cypilot-specs` and defines the initial spec list and statuses
2. Release Manager defines readiness expectations for releases
3. AI Assistant creates the Spec Manifest with stable IDs and deterministic status values (uses capability `cpt-cypilot-fr-spec-lifecycle`)
4. Cypilot Validation Tool validates the Spec Manifest structure and references by running `/cypilot-specs-validate` (uses capability `cpt-cypilot-fr-validation`)
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Spec Manifest exists and is deterministically validated
<!-- cpt:paragraph:postconditions -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->
<!-- cpt:##:usecases -->

---

<!-- cpt:##:nfrs -->
## 5. Non-functional requirements

<!-- cpt:###:nfr-title repeat="many" -->
### Validation performance

<!-- cpt:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-cypilot-nfr-validation-performance`

<!-- cpt:list:nfr-statements -->
- Deterministic validation SHOULD complete in ≤ 10 seconds for typical repositories (≤ 50k LOC).
- Validation output MUST be clear and actionable.
<!-- cpt:list:nfr-statements -->
<!-- cpt:id:nfr -->
<!-- cpt:###:nfr-title repeat="many" -->

<!-- cpt:###:nfr-title repeat="many" -->
### Security and integrity

<!-- cpt:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-cypilot-nfr-security-integrity`

<!-- cpt:list:nfr-statements -->
- Validation MUST NOT execute untrusted code from artifacts.
- Validation MUST produce deterministic results given the same repository state.
<!-- cpt:list:nfr-statements -->
<!-- cpt:id:nfr -->
<!-- cpt:###:nfr-title repeat="many" -->

<!-- cpt:###:nfr-title repeat="many" -->
### Reliability and recoverability

<!-- cpt:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-cypilot-nfr-reliability-recoverability`

<!-- cpt:list:nfr-statements -->
- Validation failures MUST include enough context to remediate without reverse-engineering the validator.
- The system SHOULD provide actionable guidance for common failure modes (missing sections, invalid IDs, missing cross-references).
<!-- cpt:list:nfr-statements -->
<!-- cpt:id:nfr -->
<!-- cpt:###:nfr-title repeat="many" -->

<!-- cpt:###:nfr-title repeat="many" -->
### Adoption and usability

<!-- cpt:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-cypilot-nfr-adoption-usability`

<!-- cpt:list:nfr-statements -->
- Workflow instructions SHOULD be executable by a new user without prior Cypilot context, with ≤ 3 clarifying questions per workflow on average.
- Documentation SHOULD prioritize discoverability of next steps and prerequisites.
<!-- cpt:list:nfr-statements -->
<!-- cpt:id:nfr -->
<!-- cpt:###:nfr-title repeat="many" -->

<!-- cpt:###:intentional-exclusions -->
### Intentional Exclusions

<!-- cpt:list:exclusions -->
- **Authentication/Authorization** (SEC-PRD-001/002): Not applicable — Cypilot is a local CLI tool and methodology, not a multi-user system requiring access control.
- **Availability/Recovery** (REL-PRD-001/002): Not applicable — Cypilot runs locally as a CLI, not as a service requiring uptime guarantees.
- **Scalability** (ARCH-PRD-003): Not applicable — Cypilot processes single repositories locally; traditional user/data volume scaling does not apply.
- **Throughput/Capacity** (PERF-PRD-002/003): Not applicable — Cypilot is a local development tool, not a high-throughput system.
- **Accessibility/Internationalization** (UX-PRD-002/003): Not applicable — CLI tool for developers; English-only is acceptable for developer tooling.
- **Regulatory/Legal** (COMPL-PRD-001/002/003): Not applicable — Cypilot is a methodology with no user data or regulated industry context.
- **Data Ownership/Lifecycle** (DATA-PRD-001/003): Not applicable — Cypilot does not persist user data; artifacts are owned by the project.
- **Support Requirements** (MAINT-PRD-002): Not applicable — Cypilot is an open methodology; support is community-driven.
- **Deployment/Monitoring** (OPS-PRD-001/002): Not applicable — Cypilot is installed locally via pip; no server deployment or monitoring required.
<!-- cpt:list:exclusions -->
<!-- cpt:###:intentional-exclusions -->
<!-- cpt:##:nfrs -->

---

<!-- cpt:##:nongoals -->
## 6. Non-Goals & Risks

<!-- cpt:###:nongoals-title -->
### Non-Goals

<!-- cpt:list:nongoals -->
- Cypilot does NOT replace project management tools (Jira, Linear, etc.) — it complements them by providing design artifacts that can be referenced from tickets.
- Cypilot does NOT enforce specific programming languages or frameworks — it is technology-agnostic and works with any stack via adapters.
- Cypilot does NOT require full coverage — teams can adopt incrementally, starting with PRD and adding artifacts as needed.
- Cypilot does NOT generate production code automatically — it provides design specifications that developers implement.
- Cypilot does NOT replace code review — it provides design review capabilities that complement code review.
<!-- cpt:list:nongoals -->
<!-- cpt:###:nongoals-title -->

<!-- cpt:###:risks-title -->
### Risks

<!-- cpt:list:risks -->
- **AI agent variability**: Different AI agents may interpret workflows differently, leading to inconsistent artifact quality. Mitigation: deterministic validation catches structural issues.
- **Adoption resistance**: Teams may resist adding design documentation overhead. Mitigation: Cypilot supports incremental adoption and provides immediate validation value.
- **Template rigidity**: Fixed templates may not fit all project types. Mitigation: adapters allow customization of artifact locations and optional sections.
<!-- cpt:list:risks -->
<!-- cpt:###:risks-title -->
<!-- cpt:##:nongoals -->

---

<!-- cpt:##:assumptions -->
## 7. Assumptions & Open Questions

<!-- cpt:###:assumptions-title -->
### Assumptions

<!-- cpt:list:assumptions -->
- AI coding assistants (Claude Code, Cursor, etc.) can follow structured markdown workflows with embedded instructions.
- Developers have access to Python 3.6+ for running the `cypilot` CLI tool.
- Projects use Git for version control (adapter discovery relies on `.git` directory).
- Teams are willing to maintain design artifacts as part of their development workflow.
<!-- cpt:list:assumptions -->
<!-- cpt:###:assumptions-title -->

<!-- cpt:###:open-questions-title -->
### Open Questions

<!-- cpt:list:open-questions -->
- None at this time.
<!-- cpt:list:open-questions -->
<!-- cpt:###:open-questions-title -->
<!-- cpt:##:assumptions -->

---

<!-- cpt:##:context -->
## 8. Additional context

<!-- cpt:###:context-title repeat="many" -->
### Terminology

<!-- cpt:free:prd-context-notes -->
This PRD uses "Cypilot" to mean Framework for Documentation and Development.
<!-- cpt:free:prd-context-notes -->
<!-- cpt:###:context-title repeat="many" -->
<!-- cpt:##:context -->
<!-- cpt:#:prd -->
