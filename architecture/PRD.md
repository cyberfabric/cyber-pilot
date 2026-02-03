<!-- spd:#:prd -->
# PRD (Product Requirements Document): Spider

<!-- spd:##:overview -->
## 1. Overview

<!-- spd:paragraph:purpose -->
**Purpose**: Spider is a methodology and productized system for guiding software development through stable artifacts, deterministic validation, and repeatable workflows.
<!-- spd:paragraph:purpose -->

<!-- spd:paragraph:context -->
In this project, "Spider" means **Framework for Documentation and Development**: the project is developed by running workflows (flows), using skills/tools for deterministic checks, and iterating interactively with AI agents.
<!-- spd:paragraph:context -->

**Target Users**:
<!-- spd:list:target-users required="true" -->
- Development Teams - Building software with clear design documentation
- Technical Leads & Architects - Defining system architecture and technical decisions
- Product Managers - Capturing product requirements and use cases
- AI Coding Assistants - Executing workflows and validating artifacts
- QA Engineers - Verifying implementation matches design
- Documentation Writers - Creating comprehensive technical documentation
<!-- spd:list:target-users -->

**Key Problems Solved**:
<!-- spd:list:key-problems required="true" -->
- **Design-Code Disconnect**: Code diverges from design without single source of truth, leading to outdated documentation
- **Lack of Traceability**: Cannot track product requirements through design to implementation, making impact analysis difficult
- **Unstructured Development**: No repeatable process for design and implementation, causing inconsistent quality
- **AI Integration Challenges**: AI agents cannot follow methodology without structured guidance and machine-readable specifications
- **Validation Complexity**: Manual design reviews are time-consuming and miss structural issues
<!-- spd:list:key-problems -->

**Success Criteria**:
<!-- spd:list:success-criteria required="true" -->
- A new user can complete adapter initialization and reach a first passing PRD validation (`spider validate --artifact {project-root}/architecture/PRD.md`) in ≤ 60 minutes. (Baseline: not measured; Target: v1.0)
- Deterministic validation of the PRD completes in ≤ 3 seconds on a typical developer laptop. (Baseline: ~1s current; Target: v1.0)
- 100% of `spd-spider-actor-*` IDs defined in the PRD are resolvable via deterministic search (`spider where-defined`) without ambiguity. (Baseline: 100% current; Target: v1.0)
- CI validation feedback for PRD changes is produced in ≤ 2 minutes from push to default branch. (Baseline: not measured; Target: v1.0)
- Users can apply a small PRD update (single section change) via `/spider-prd` in ≤ 10 minutes end-to-end, including re-validation. (Baseline: not measured; Target: v1.0)
<!-- spd:list:success-criteria -->

**Capabilities**:
<!-- spd:list:capabilities required="true" -->
- Execute workflows to create/update/validate artifacts
- Provide deterministic validation and traceability scanning
- Support adapter-driven configuration for different projects and tech stacks
<!-- spd:list:capabilities -->
<!-- spd:##:overview -->

---

<!-- spd:##:actors -->
## 2. Actors

<!-- spd:###:actor-title repeat="many" -->
### Product Manager

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-product-manager`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Defines product requirements, captures use cases, and documents PRD content using Spider workflows
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### Architect

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-architect`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Designs system architecture, creates overall design documentation, and defines technical patterns
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### Developer

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-developer`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Implements features according to validated designs, adds traceability tags to code
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### QA Engineer

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-qa-engineer`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Validates implementation against design specifications and ensures test coverage
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### Technical Lead

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-technical-lead`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Sets up project adapters, configures Spider for project-specific conventions
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### Project Manager

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-project-manager`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Monitors development progress, ensures workflows are followed, tracks feature completion
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### Documentation Writer

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-documentation-writer`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Creates and maintains project documentation using Spider artifacts as source
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### DevOps Engineer

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-devops-engineer`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Configures CI/CD pipelines, uses adapter specs for build and deployment automation
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### Security Engineer

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-security-engineer`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Conducts security review of design and code, validates security requirements implementation
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### Business Analyst

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-prd-analyst`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Analyzes product requirements and translates them into Spider format for Product Manager
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### UX Designer

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-ux-designer`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Designs user interfaces based on actor flows from feature design
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### Performance Engineer

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-performance-engineer`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Defines performance targets, reviews designs for performance risks, and validates performance requirements implementation
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### Database Architect

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-database-architect`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Designs data models and storage strategies, reviews domain model impacts, and validates database-related constraints
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### Release Manager

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-release-manager`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Manages releases and tracks feature readiness using Spider artifacts (for example via a Feature Manifest when used)
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### AI Coding Assistant

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-ai-assistant`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Executes Spider workflows interactively, generates artifacts, and validates against requirements
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### Spider Validation Tool

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-spider-tool`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Automated validation engine that checks artifact structure, ID formats, and traceability
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### CI/CD Pipeline

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-ci-pipeline`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Automatically validates Spider artifacts on every commit through GitHub Actions or GitLab CI
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->

<!-- spd:###:actor-title repeat="many" -->
### Documentation Generator

<!-- spd:id:actor -->
**ID**: `spd-spider-actor-doc-generator`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: Automatically generates external documentation from Spider artifacts (API docs, architecture diagrams)
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->
<!-- spd:##:actors -->

---

<!-- spd:##:frs -->
## 3. Functional Requirements

<!-- spd:###:fr-title repeat="many" -->
### FR-001 Workflow-Driven Development

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p1` - **ID**: `spd-spider-fr-workflow-execution`

<!-- spd:free:fr-summary -->
The system MUST provide a clear, documented workflow catalog that users and AI agents can execute. Artifact locations MUST be adapter-defined; workflows MUST NOT hardcode repository paths. The core workflow set MUST cover at least: Adapter bootstrap and configuration, PRD creation/update, Overall design creation/update, ADR creation/update, Feature design creation/update, Feature implementation (`implement` as the primary implementation workflow), and Deterministic validation workflows for the above artifacts and for code traceability (when enabled). The system MUST provide a unified agent entrypoint workflow (`/spider`) that selects and executes the appropriate workflow (create/update/validate) based on context, or runs `spider` tool commands when requested. This includes interactive question-answer flow with AI agents, automated validation after artifact creation, step-by-step guidance for complex operations, and independent workflows (no forced sequence).
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-product-manager`, `spd-spider-actor-architect`, `spd-spider-actor-technical-lead`, `spd-spider-actor-project-manager`, `spd-spider-actor-release-manager`, `spd-spider-actor-developer`, `spd-spider-actor-qa-engineer`, `spd-spider-actor-security-engineer`, `spd-spider-actor-performance-engineer`, `spd-spider-actor-database-architect`, `spd-spider-actor-devops-engineer`, `spd-spider-actor-documentation-writer`, `spd-spider-actor-prd-analyst`, `spd-spider-actor-ux-designer`, `spd-spider-actor-ai-assistant`, `spd-spider-actor-spider-tool`, `spd-spider-actor-ci-pipeline`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-002 Artifact Structure Validation

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p1` - **ID**: `spd-spider-fr-validation`

<!-- spd:free:fr-summary -->
Deterministic validators for structural checks (sections, IDs, format). Deterministic content validation for semantic quality and boundaries: Content MUST be internally consistent (no contradictions), Content MUST NOT include information that belongs in other artifacts, Content MUST include required information expected for the artifact kind, Content MUST be semantically consistent with upstream/downstream artifacts (no cross-artifact contradictions), Content MUST not omit critical details that are explicitly defined in other artifacts. Deterministic validation for key artifacts defined by the adapter (no hardcoded repository paths). 100-point scoring system with category breakdown. Pass/fail thresholds (typically ≥90 or 100/100). Cross-reference validation (actor/capability IDs). Placeholder detection (incomplete markers). Detailed issue reporting with recommendations.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-architect`, `spd-spider-actor-technical-lead`, `spd-spider-actor-developer`, `spd-spider-actor-qa-engineer`, `spd-spider-actor-security-engineer`, `spd-spider-actor-performance-engineer`, `spd-spider-actor-database-architect`, `spd-spider-actor-ai-assistant`, `spd-spider-actor-spider-tool`, `spd-spider-actor-ci-pipeline`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-003 Adapter Configuration System

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p1` - **ID**: `spd-spider-fr-adapter-config`

<!-- spd:free:fr-summary -->
Technology-agnostic core methodology. Project-specific adapter specifications. Adapter MUST define an explicit registry of artifacts and their properties (for example: locations, scope, normative vs context-only). Adapter MUST support per-artifact configuration, including enabling/disabling code traceability checks. Tech stack definition (languages, frameworks, tools). Domain model format specification. API contract format specification. Adapter MUST be able to define deterministic tools/commands used to validate domain model sources and API contract sources. Testing strategy and build tool configuration. Auto-detection from existing codebase.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-technical-lead`, `spd-spider-actor-architect`, `spd-spider-actor-database-architect`, `spd-spider-actor-performance-engineer`, `spd-spider-actor-devops-engineer`, `spd-spider-actor-developer`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-004 Adaptive Design Bootstrapping

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p1` - **ID**: `spd-spider-fr-design-first`

<!-- spd:free:fr-summary -->
Users MAY start implementation without having pre-existing design artifacts. When a workflow needs a traceability source and design artifacts are missing, the workflow MUST bootstrap the minimum viable design interactively and then continue. Once created, design artifacts become the single source of truth (code follows design). Design iteration MUST be workflow-driven and MUST be followed by deterministic validation. Clear separation between PRD, overall design, ADRs, and feature designs. Behavioral specifications MUST use Spider DSL (SDSL) (plain-English algorithms).
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-product-manager`, `spd-spider-actor-architect`, `spd-spider-actor-developer`, `spd-spider-actor-prd-analyst`, `spd-spider-actor-ux-designer`, `spd-spider-actor-security-engineer`, `spd-spider-actor-performance-engineer`, `spd-spider-actor-database-architect`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-005 Traceability Management

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p1` - **ID**: `spd-spider-fr-traceability`

<!-- spd:free:fr-summary -->
Unique ID system for all design elements using structured format. Code tags (@spider-*) linking implementation to design. Traceability validation MUST be configurable per artifact (enabled/disabled via adapter). Spider-ID MAY be versioned by appending a `-vN` suffix (example: `<base-id>-v2`). When an identifier is replaced (REPLACE), the new identifier version MUST be incremented: If the prior identifier has no version suffix, the new identifier MUST end with `-v1`; If the prior identifier ends with `-vN`, the new identifier MUST increment the version by 1 (example: `-v1` → `-v2`). Once an identifier becomes versioned, the version suffix MUST NOT be removed in future references. When an identifier is replaced (REPLACE), all references MUST be updated (all artifacts and all code traceability tags, including qualified `:ph-N:inst-*` references). Qualified IDs for phases and instructions (:ph-N:inst-*). Repository-wide ID scanning and search. where-defined and where-used commands. Design-to-code validation (implemented items must have code tags).
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-developer`, `spd-spider-actor-qa-engineer`, `spd-spider-actor-spider-tool`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-006 Quickstart Guides

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p2` - **ID**: `spd-spider-fr-interactive-docs`

<!-- spd:free:fr-summary -->
QUICKSTART guides with copy-paste prompts. Progressive disclosure (human-facing overview docs, AI navigation rules for agents).
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-documentation-writer`, `spd-spider-actor-product-manager`, `spd-spider-actor-release-manager`, `spd-spider-actor-ai-assistant`, `spd-spider-actor-doc-generator`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-007 Artifact Templates

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p1` - **ID**: `spd-spider-fr-artifact-templates`

<!-- spd:free:fr-summary -->
The system MUST provide an artifact template catalog for core Spider artifacts (PRD, Overall Design, ADRs, Feature Manifest, Feature Designs). Agents MUST be able to use these templates during workflow execution.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-documentation-writer`, `spd-spider-actor-ai-assistant`, `spd-spider-actor-doc-generator`, `spd-spider-actor-technical-lead`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-008 Artifact Examples

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p2` - **ID**: `spd-spider-fr-artifact-examples`

<!-- spd:free:fr-summary -->
The system MUST provide an artifact example catalog for core Spider artifacts (PRD, Overall Design, ADRs, Feature Manifest, Feature Designs). Agents MUST be able to use these examples during workflow execution.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-documentation-writer`, `spd-spider-actor-ai-assistant`, `spd-spider-actor-doc-generator`, `spd-spider-actor-technical-lead`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-009 ADR Management

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p2` - **ID**: `spd-spider-fr-arch-decision-mgmt`

<!-- spd:free:fr-summary -->
Create and track architecture decisions with structured format. Link ADRs to affected design sections and feature IDs. Decision status tracking (PROPOSED, ACCEPTED, DEPRECATED, SUPERSEDED). Impact analysis when ADR changes affect multiple features. Search ADRs by status, date, or affected components. Version history for decision evolution.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-architect`, `spd-spider-actor-technical-lead`, `spd-spider-actor-security-engineer`, `spd-spider-actor-performance-engineer`, `spd-spider-actor-database-architect`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-010 PRD Management

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p1` - **ID**: `spd-spider-fr-prd-mgmt`

<!-- spd:free:fr-summary -->
Create and update PRD content through workflows. Enforce stable IDs for actors and capabilities. PRD deterministic validation integration.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-product-manager`, `spd-spider-actor-prd-analyst`, `spd-spider-actor-ai-assistant`, `spd-spider-actor-spider-tool`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-011 Overall Design Management

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p1` - **ID**: `spd-spider-fr-overall-design-mgmt`

<!-- spd:free:fr-summary -->
Create and update Overall Design through workflows. Link requirements to PRD actors and capabilities. Deterministic validation integration for Overall Design.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-architect`, `spd-spider-actor-technical-lead`, `spd-spider-actor-ai-assistant`, `spd-spider-actor-spider-tool`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-012 Feature Manifest Management

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p2` - **ID**: `spd-spider-fr-feature-manifest-mgmt`

<!-- spd:free:fr-summary -->
Create and update Feature Manifest through workflows. Maintain stable IDs for features and tracking fields. Deterministic validation integration for Feature Manifest.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-project-manager`, `spd-spider-actor-release-manager`, `spd-spider-actor-ai-assistant`, `spd-spider-actor-spider-tool`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-013 Feature Design Management

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p1` - **ID**: `spd-spider-fr-feature-design-mgmt`

<!-- spd:free:fr-summary -->
Create and update Feature Design through workflows. Maintain stable IDs for flows, algorithms, and requirements. Deterministic validation integration for Feature Design.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-architect`, `spd-spider-actor-ai-assistant`, `spd-spider-actor-spider-tool`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-014 Feature Lifecycle Management

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p2` - **ID**: `spd-spider-fr-feature-lifecycle`

<!-- spd:free:fr-summary -->
Track feature status from NOT_STARTED through IN_DESIGN, DESIGNED, READY, IN_PROGRESS to DONE. Track progress using the project's selected feature tracking approach (for example a feature manifest when used). Feature dependency management and blocking detection. Milestone tracking and release planning integration. Historical feature completion metrics and velocity tracking. Status transition validation (cannot skip states).
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-project-manager`, `spd-spider-actor-release-manager`, `spd-spider-actor-developer`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-015 Code Generation from Design

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p2` - **ID**: `spd-spider-fr-code-generation`

<!-- spd:free:fr-summary -->
Provide an implementation process that is adapter-aware and works with any programming language. Apply general best practices that are applicable across languages. Prefer TDD where feasible and follow SOLID principles. Use adapter-defined domain model and API contract sources when present. Add traceability tags when traceability is enabled for the relevant artifacts.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-developer`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-016 Brownfield Support

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p2` - **ID**: `spd-spider-fr-brownfield-support`

<!-- spd:free:fr-summary -->
Add Spider to existing projects without disruption. Auto-detect existing architecture from code and configs. Reverse-engineer the PRD from requirements documentation. Extract Overall Design patterns from implementation. Incremental Spider adoption (start with adapter, add artifacts gradually). Legacy system integration with minimal refactoring.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-technical-lead`, `spd-spider-actor-architect`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-017 Spider DSL (SDSL)

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p1` - **ID**: `spd-spider-fr-fdl`

<!-- spd:free:fr-summary -->
Plain English algorithm description language for actor flows (Spider DSL, abbreviated SDSL). Structured numbered lists with bold keywords (**IF**, **ELSE**, **WHILE**, **FOR EACH**). Instruction markers with checkboxes (- [ ] Inst-label: description). Phase-based organization (ph-1, ph-2, etc.) for implementation tracking. Readable by non-programmers for validation and review. Translates directly to code with traceability tags. Keywords: **AND**, **OR**, **NOT**, **MUST**, **REQUIRED**, **OPTIONAL**. Actor-centric (steps start with **Actor** or **System**).
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-architect`, `spd-spider-actor-developer`, `spd-spider-actor-prd-analyst`, `spd-spider-actor-ux-designer`, `spd-spider-actor-product-manager`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-018 IDE Integration and Tooling

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [ ] `p3` - **ID**: `spd-spider-fr-ide-integration`

<!-- spd:free:fr-summary -->
VS Code extension for Spider artifact editing. Click-to-navigate for Spider IDs (jump to definition). where-used and where-defined commands in IDE. Inline validation errors and warnings. Autocomplete for Spider IDs and section references. Syntax highlighting for Spider DSL (SDSL). Integration with `spider` skill commands. Code lens showing traceability status.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-developer`, `spd-spider-actor-architect`, `spd-spider-actor-devops-engineer`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-019 Multi-Agent IDE Integration

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p2` - **ID**: `spd-spider-fr-multi-agent-integration`

<!-- spd:free:fr-summary -->
The system MUST provide a unified `agents` command to generate and maintain agent-specific workflow proxy files and skill entry points for multiple AI coding assistants. Supported agents MUST include Claude, Cursor, Windsurf, and Copilot. The `agents` command MUST generate workflow entry points in each agent's native format (e.g., `.claude/commands/`, `.cursor/commands/`, `.windsurf/workflows/`, `.github/prompts/`) and skill/rule entry points that point to the core Spider skill. Configuration MUST be externalized to a unified JSON file (`spider-agents.json`) with sensible defaults for recognized agents.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-technical-lead`, `spd-spider-actor-devops-engineer`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-020 Extensible Weaver Package System

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p1` - **ID**: `spd-spider-fr-rules-packages`

<!-- spd:free:fr-summary -->
The system MUST support extensible weaver packages that define templates, checklists, and validation rules for artifact types. Each weaver package MUST be identified in the adapter registry and MUST contain a `template.md` file with Spider markers for each artifact kind. Weaver packages MAY contain `checklist.md` for semantic validation criteria and `rules.md` for generation guidance. The `validate-weavers` command MUST validate that weaver packages are structurally correct and that templates follow the spider-template frontmatter specification.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-technical-lead`, `spd-spider-actor-spider-tool`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-021 Template Quality Assurance

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p2` - **ID**: `spd-spider-fr-template-qa`

<!-- spd:free:fr-summary -->
The system MUST provide a `self-check` command that validates example artifacts against their templates. The adapter registry MAY define `templates` entries with `template_path`, `example_path`, and `validation_level` properties. When `validation_level` is `STRICT`, the self-check command MUST validate that the example artifact passes all template validation rules. This ensures that templates and examples remain synchronized and that templates are valid.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-technical-lead`, `spd-spider-actor-spider-tool`, `spd-spider-actor-documentation-writer`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-022 Cross-Artifact Validation

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p1` - **ID**: `spd-spider-fr-cross-artifact-validation`

<!-- spd:free:fr-summary -->
The system MUST validate cross-artifact relationships when multiple artifacts are validated together. ID blocks with `covered_by` attributes MUST have at least one reference in artifacts whose template kind matches the covered_by list. All ID references MUST resolve to a definition in some artifact. When a reference is marked as checked (`[x]`), the corresponding definition MUST also be marked as checked. Cross-artifact validation MUST be deterministic and report all consistency violations with line numbers and artifact paths.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-spider-tool`, `spd-spider-actor-ci-pipeline`, `spd-spider-actor-architect`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->

<!-- spd:###:fr-title repeat="many" -->
### FR-023 Hierarchical System Registry

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p2` - **ID**: `spd-spider-fr-hierarchical-registry`

<!-- spd:free:fr-summary -->
The system MUST support hierarchical organization of systems in the artifacts registry. Each system MUST have a `name`, `rules` reference, and lists of `artifacts` and optional `codebase` entries. Systems MAY have `children` arrays for nested subsystems. Each artifact entry MUST specify `name`, `path`, `kind`, and `traceability` level (`FULL` or `DOCS-ONLY`). Each codebase entry MUST specify `name`, `path`, and `extensions` for code scanning. The `adapter-info` command MUST display the resolved hierarchical structure.
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-technical-lead`, `spd-spider-actor-spider-tool`, `spd-spider-actor-architect`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->
<!-- spd:##:frs -->

---

<!-- spd:##:usecases -->
## 4. Use Cases

<!-- spd:###:uc-title repeat="many" -->
### UC-001 Bootstrap New Project with Spider

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-bootstrap-project`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-technical-lead`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Project repository exists with Git initialized
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Technical Lead initiates Spider setup by requesting AI Assistant to add the Spider framework
2. AI Assistant establishes minimal adapter configuration (uses capability `spd-spider-fr-adapter-config`)
3. If adapter is missing, the system offers to bootstrap it; the user MAY decline and continue with reduced automation
4. The system confirms that adapter discovery is possible when the adapter exists
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Project has working Spider adapter, ready for PRD and design workflows
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-002 Create PRD

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-create-prd`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-product-manager`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Project context exists; adapter may or may not exist
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Product Manager runs `/spider-prd` and asks AI Assistant to create or refine PRD
2. AI Assistant asks questions about vision, target users, and problems solved
3. Product Manager answers; AI Assistant proposes PRD content based on available context
4. AI Assistant defines actors and capabilities with stable IDs (uses capability `spd-spider-fr-traceability`)
5. AI Assistant updates the PRD according to answers
6. Product Manager validates PRD by running `/spider-prd-validate` (see `spd-spider-usecase-validate-prd`)
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Valid PRD exists, project ready for overall design workflow
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-003 Design Feature with AI Assistance

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-design-feature`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-architect`, `spd-spider-actor-ai-assistant`, `spd-spider-actor-database-architect`, `spd-spider-actor-performance-engineer`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: PRD and Overall Design validated, feature scope identified (from backlog, ticket, or code context)
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Architect runs `/spider-feature` and specifies the feature scope and desired outcomes
2. AI Assistant helps define actor flows in Spider DSL (SDSL) (uses capability `spd-spider-fr-design-first`)
3. Architect defines requirements, constraints, and interfaces at feature scope
4. Architect runs `/spider-feature-validate`; the system validates the Feature Design deterministically (uses capability `spd-spider-fr-validation`)
5. Validation reports 100/100 score (required for feature design)
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Feature Design validated at 100/100, ready for implementation
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-004 Validate Design Against Requirements - Overall Design

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-validate-design`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-architect`, `spd-spider-actor-spider-tool`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Overall Design exists with requirements, actors, and capabilities defined
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Architect runs `/spider-design-validate` to request deterministic validation of overall design
2. The system validates structure, required content, and cross-artifact consistency (uses capability `spd-spider-fr-validation`)
3. The system validates ID formats and cross-references (uses capability `spd-spider-fr-traceability`)
4. The system reports a score breakdown with actionable issues
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Validation report shows PASS (≥90/100) or FAIL with actionable issues, Architect fixes issues or proceeds to next workflow
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-005 Trace Requirement to Implementation

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-trace-requirement`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-developer`, `spd-spider-actor-spider-tool`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Feature Design exists; implementation exists (partial or complete); traceability tags are present when traceability is enabled
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Developer selects a requirement ID to verify
2. The system locates the normative definition and where it is used (uses capability `spd-spider-fr-traceability`)
3. The system reports traceability coverage and gaps
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Developer confirms requirement is fully implemented with proper traceability, or identifies missing implementation
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-006 Update Existing Feature Design

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-update-feature-design`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-architect`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Feature Design exists and previously validated at 100/100 (triggers `spd-spider-usecase-design-feature`)
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Architect identifies need to add new algorithm to existing feature
2. AI Assistant runs `/spider-feature` in update mode, loads existing feature design, and presents current content
3. AI Assistant asks: "What to update?" with options (Add actor flow, Edit algorithm, Add requirement, etc.)
4. Architect selects "Add new algorithm" option
5. Architect specifies new algorithm details in Spider DSL (SDSL) (uses capability `spd-spider-fr-design-first`)
6. AI Assistant updates Feature Design while preserving unchanged sections
7. AI Assistant generates new algorithm ID following format `spd-<project>-feature-<feature>-algo-<name>` (uses capability `spd-spider-fr-traceability`)
8. Spider Validation Tool re-validates the updated design by running `/spider-feature-validate` (uses capability `spd-spider-fr-validation`)
9. Validation confirms 100/100 score maintained
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Feature Design updated with new algorithm, fully validated, ready for implementation
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-007 Implement Feature

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-plan-implementation`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-developer`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Feature Design exists with a sufficiently clear traceability source (validated when possible)
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Developer requests to code the feature
2. AI Assistant executes `/spider-code` workflow (uses capability `spd-spider-fr-workflow-execution`)
3. The system uses Feature Design to extract the minimal implementation scope
4. AI Assistant and Developer code iteratively, keeping design and code aligned
5. Developer adds code traceability tags where used (uses capability `spd-spider-fr-traceability`)
6. Spider Validation Tool validates implementation and traceability by running `/spider-code-validate` (uses capability `spd-spider-fr-validation`)
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Feature implemented with traceability where used, and validation indicates completeness
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-009 Validate Feature Implementation

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-validate-implementation`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-qa-engineer`, `spd-spider-actor-spider-tool`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Feature implementation exists (partial or complete)
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. QA Engineer runs `/spider-code-validate` to request validation of feature implementation
2. Spider Validation Tool validates codebase traceability when enabled (uses capability `spd-spider-fr-validation`)
3. Tool validates prerequisite design artifacts first
4. For each `[x]` marked scope in design, tool expects matching tags in code when traceability is enabled (uses capability `spd-spider-fr-traceability`)
5. For each `[x]` marked Spider DSL (SDSL) instruction, tool expects instruction-level tag in code when traceability is enabled
6. Tool reports missing tags, extra tags, and format issues
7. Tool checks build passes and tests run successfully
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Validation report shows full traceability or lists missing/incorrect tags, QA Engineer confirms implementation complete or requests fixes
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-010 Auto-Generate Adapter from Codebase

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-auto-generate-adapter`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-technical-lead`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Project has existing codebase with code, configs, and documentation
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Technical Lead wants to add Spider to existing project
2. AI Assistant runs `/spider-adapter-auto` to analyze existing codebase (uses capability `spd-spider-fr-workflow-execution`)
3. AI Assistant scans project for documentation (README, ARCHITECTURE, CONTRIBUTING) (uses capability `spd-spider-fr-adapter-config`)
4. AI Assistant analyzes config files (package.json, requirements.txt, Cargo.toml, etc.)
5. AI Assistant detects tech stack (languages, frameworks, versions)
6. AI Assistant analyzes code structure and naming conventions
7. AI Assistant discovers domain model format from code (TypeScript types, JSON Schema, etc.)
8. AI Assistant discovers API format from definitions (OpenAPI, GraphQL schema, etc.)
9. AI Assistant proposes adapter specifications (tech stack, domain model format, conventions, etc.)
10. Technical Lead reviews and approves proposed specs
11. AI Assistant updates adapter specs in the adapter specifications area
12. AI Assistant updates the adapter's AI navigation rules with WHEN rules for each spec
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Adapter with auto-generated specs from existing codebase, validated and ready for Spider workflows
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-011 Configure CI/CD Pipeline for Spider Validation

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-configure-cicd`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-devops-engineer`, `spd-spider-actor-ci-pipeline`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Project has Spider adapter configured (triggers `spd-spider-usecase-bootstrap-project`)
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. DevOps Engineer wants to automate Spider artifact validation in CI/CD
2. DevOps Engineer reads the adapter build/deploy specification for test and build commands (uses capability `spd-spider-fr-adapter-config`)
3. DevOps Engineer creates GitHub Actions workflow or GitLab CI config
4. Workflow configured to run `/spider validate` on changed artifacts in pull requests
5. CI/CD Pipeline executes validation automatically on every commit (uses capability `spd-spider-fr-validation`)
6. Pipeline reports validation results as PR status checks
7. Pipeline blocks merge if any artifact validation fails (uses capability `spd-spider-fr-validation`)
8. DevOps Engineer configures notifications for validation failures
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: CI/CD Pipeline automatically validates all Spider artifacts, prevents invalid designs from being merged
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-012 Security Review of Feature Design

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-security-review`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-security-engineer`, `spd-spider-actor-architect`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Feature Design exists and validated (triggers `spd-spider-usecase-design-feature`)
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Security Engineer receives notification that new feature design ready for review
2. Security Engineer reviews feature design content to identify data flows, trust boundaries, and sensitive data handling (uses capability `spd-spider-fr-design-first`)
3. Security Engineer reviews authentication and authorization expectations
4. Security Engineer identifies missing security controls or vulnerabilities (uses capability `spd-spider-fr-validation`)
5. Security Engineer adds security requirements with stable IDs `spd-<project>-feature-<feature>-req-security-*`
6. Architect updates the feature design based on security feedback (triggers `spd-spider-usecase-update-feature-design`)
7. Security Engineer approves design after security requirements are added
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Feature design includes comprehensive security requirements, ready for secure implementation
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-013 Product Requirements Analysis

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-prd-analysis`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-prd-analyst`, `spd-spider-actor-product-manager`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Stakeholder requirements gathered but not yet documented in Spider format
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Business Analyst collects raw requirements from stakeholders (interviews, documents, meetings)
2. Business Analyst analyzes requirements and identifies actors (human and system)
3. Business Analyst groups related requirements into capabilities (uses capability `spd-spider-fr-design-first`)
4. Business Analyst creates draft structure for the PRD with actors and capabilities
5. Business Analyst works with Product Manager to refine vision and success criteria
6. Product Manager runs `/spider-prd` with Business Analyst's draft (uses capability `spd-spider-fr-workflow-execution`)
7. AI Assistant updates the PRD based on analyzed requirements
8. Business Analyst reviews generated PRD for completeness and accuracy (uses capability `spd-spider-fr-validation`)
9. Business Analyst confirms all stakeholder requirements covered by capabilities
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Well-structured PRD capturing all stakeholder requirements in Spider format (triggers `spd-spider-usecase-create-prd`)
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-014 Design User Interface from Flows

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-design-ui`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-ux-designer`, `spd-spider-actor-architect`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Feature design exists with documented actor flows (triggers `spd-spider-usecase-design-feature`)
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. UX Designer reviews the feature design actor flows to understand user journeys (uses capability `spd-spider-fr-design-first`)
2. UX Designer identifies UI screens needed for each flow step
3. UX Designer creates wireframes mapping each Spider DSL (SDSL) instruction to UI element
4. For each flow phase (ph-1, ph-2, etc.), UX Designer designs corresponding screen state
5. UX Designer validates that UI covers all actor interactions from flows (uses capability `spd-spider-fr-traceability`)
6. UX Designer creates UI mockups with annotations linking to flow IDs (e.g., "Implements `spd-<project>-feature-<feature>-flow-<name>:ph-1`")
7. Architect reviews UI mockups against the feature design to ensure completeness
8. UX Designer updates UI based on feedback if flows were unclear
9. Architect may update the feature design actor flows if UI reveals missing flow steps (triggers `spd-spider-usecase-update-feature-design`)
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: UI mockups fully aligned with feature flows, developers can code UI following both mockups and feature design
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-015 Plan Release with Feature Tracking

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-plan-release`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-release-manager`, `spd-spider-actor-project-manager`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Overall Design exists and needs to be decomposed into feature-level scope
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Architect and Project Manager review Overall Design to identify feature boundaries
2. Team defines feature list and assigns initial statuses (NOT_STARTED, IN_DESIGN)
3. Architect designs features iteratively (IN_DESIGN → DESIGNED → READY)
4. Developers code features (IN_PROGRESS → DONE)
5. Validation is run after each meaningful update (uses capability `spd-spider-fr-validation`)
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Clear visibility into feature progress, automated status tracking, dependency validation, historical metrics for planning
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-016 Record Architecture Decision

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-record-adr`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-architect`, `spd-spider-actor-technical-lead`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Architecture decision needs to be documented
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Architect identifies significant technical decision requiring documentation
2. Architect runs `/spider-adr` to create new ADR (uses capability `spd-spider-fr-workflow-execution`)
3. AI Assistant assigns sequential ADR ID (e.g., ADR-0001, ADR-0002)
4. Architect documents decision context, considered options, and chosen solution (uses capability `spd-spider-fr-arch-decision-mgmt`)
5. ADR is created with status ACCEPTED
6. AI Assistant updates affected design sections to reference ADR (uses capability `spd-spider-fr-traceability`)
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Architecture decision documented with full context, linked to affected design elements, searchable by status and component
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-017 Generate Code from Feature Design

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-generate-code`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-developer`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Feature scope is known (feature design may or may not exist)
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Developer wants to generate initial code scaffolding
2. If feature design is missing, AI Assistant bootstraps the minimal feature design (uses capability `spd-spider-fr-design-first`)
3. AI Assistant reads adapter specs for language-specific patterns and project conventions (uses capability `spd-spider-fr-adapter-config`)
4. AI Assistant uses adapter-defined domain model and API contract sources when present (uses capability `spd-spider-fr-code-generation`)
5. AI Assistant generates code scaffolding and test scaffolding following best practices (uses capability `spd-spider-fr-code-generation`)
6. AI Assistant adds traceability tags when enabled (uses capability `spd-spider-fr-traceability`)
7. Developer runs `/spider-code` to continue implementation from the validated feature design
8. Developer reviews generated code and adjusts as needed
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Code scaffolding generated with proper structure and traceability tags when enabled, developer can focus on business logic implementation
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-018 Navigate Traceability in IDE

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-ide-navigation`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-developer`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: VS Code Spider extension installed, project has Spider artifacts
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Developer opens Feature Design in VS Code
2. Developer sees Spider ID `spd-spider-seq-intent-to-workflow` highlighted with syntax coloring (uses capability `spd-spider-fr-ide-integration`)
3. Developer Cmd+Click (or Ctrl+Click) on flow ID to jump to definition in same file
4. Developer right-clicks on flow ID and selects "Find where-used" from context menu
5. IDE shows list of references in design docs and code files (uses capability `spd-spider-fr-traceability`)
6. Developer clicks on code reference to navigate to implementation file
7. Developer sees inline validation errors if ID format is incorrect
8. Developer uses autocomplete to insert valid Spider IDs when editing
9. Code lens above function shows traceability status (✅ tagged or ⚠️ missing tags)
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Developer can navigate between design and code instantly, maintain traceability without manual searching
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-019 Migrate Existing Project to Spider

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-migrate-project`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-technical-lead`, `spd-spider-actor-ai-assistant`, `spd-spider-actor-documentation-writer`, `spd-spider-actor-doc-generator`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Existing project with code but no Spider artifacts
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Technical Lead wants to adopt Spider for legacy project
2. AI Assistant runs `/spider-adapter-auto` to analyze existing codebase (uses capability `spd-spider-fr-brownfield-support`)
3. AI Assistant scans existing project documentation for PRD content
4. AI Assistant proposes PRD content based on discovered information
5. Technical Lead reviews and refines proposed PRD content
6. AI Assistant analyzes code structure to extract architectural patterns
7. AI Assistant proposes Overall Design content from implementation patterns
8. Technical Lead identifies which features to document first (incremental adoption)
9. AI Assistant creates or updates Feature Design for priority features using the adapter-defined locations
10. Developer adds traceability tags to existing code incrementally (uses capability `spd-spider-fr-traceability`)
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Legacy project has Spider artifacts documenting current state, team can use Spider workflows for new features while preserving existing code
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-020 Track Feature Progress Through Lifecycle

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-track-feature-lifecycle`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-project-manager`, `spd-spider-actor-developer`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: A Feature Manifest exists (when used) with multiple features at various stages
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Project Manager opens a feature manifest to review current status (uses capability `spd-spider-fr-feature-lifecycle`)
2. Project Manager sees feature statuses: ⏳ NOT_STARTED, 🔄 IN_PROGRESS, ✅ DONE
3. Developer marks feature as 🔄 IN_PROGRESS when starting implementation work
4. System validates feature has Feature Design at 100/100 before allowing IN_PROGRESS status
5. As developer completes implementation work, system suggests status update
6. Developer runs final validation before marking feature ✅ DONE (uses capability `spd-spider-fr-validation`)
7. Project Manager tracks velocity by counting completed features per sprint
8. Project Manager identifies blocking dependencies (Feature B depends on Feature A)
9. System alerts if Feature B IN_PROGRESS but Feature A still NOT_STARTED
10. Project Manager generates progress report showing feature completion timeline
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Clear visibility into feature progress, automated status tracking, dependency validation, historical metrics for planning
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-022 Write Actor Flow in Spider DSL (SDSL)

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-write-fdl-flow`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-architect`, `spd-spider-actor-prd-analyst`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Feature Design exists, architect needs to document actor flow
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Architect opens the feature design and navigates to the actor flows
2. Architect creates new flow: "Login Flow" with ID `spd-spider-seq-intent-to-workflow` (uses capability `spd-spider-fr-design-first`)
3. Architect writes flow in Spider DSL (SDSL) using plain English with bold keywords (uses capability `spd-spider-fr-fdl`)
4. Business Analyst reviews the Spider DSL (SDSL) flow and confirms it matches product requirements
5. Business Analyst identifies missing case: "What if user forgot password?"
6. Architect adds step with **OPTIONAL** path to password reset
7. UX Designer reads flow and creates UI mockups matching each step and instruction
8. Architect marks instructions with phases for implementation: ph-1 (validation), ph-2 (authentication), ph-3 (session)
9. Developer reads the Spider DSL (SDSL) flow and understands exact implementation requirements without ambiguity
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Actor flow documented in plain English readable by all stakeholders, directly translatable to code with instruction-level traceability
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-024 Validate PRD

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-validate-prd`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-product-manager`, `spd-spider-actor-spider-tool`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: PRD exists
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Product Manager runs `/spider-prd-validate` to request PRD validation
2. Spider Validation Tool validates structure, cross-references, and semantic boundaries (uses capability `spd-spider-fr-validation`)
3. Tool reports PASS/FAIL with actionable issues
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: PRD validation status is known; issues are ready for remediation
<!-- spd:paragraph:postconditions -->

**Alternative Flows**:
<!-- spd:list:alternative-flows -->
- **Validation fails**: If step 3 reports FAIL, Product Manager reviews issues, edits PRD to fix them, and re-runs validation (loop to step 1)
<!-- spd:list:alternative-flows -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-025 Create Overall Design

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-create-overall-design`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-architect`, `spd-spider-actor-technical-lead`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: PRD exists and is deterministically validated
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Architect runs `/spider-design` and defines system-level scope, constraints, and key requirements
2. Technical Lead provides project-specific technical context via adapter (uses capability `spd-spider-fr-adapter-config`)
3. AI Assistant drafts Overall Design with stable IDs and cross-references to PRD actors and capabilities
4. Spider Validation Tool runs deterministic validation for Overall Design by running `/spider-design-validate` (uses capability `spd-spider-fr-validation`)
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Overall Design exists and is deterministically validated
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-026 Update Overall Design

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-update-overall-design`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-architect`, `spd-spider-actor-technical-lead`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: Overall Design exists
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Architect runs `/spider-design` in update mode and identifies what system-level decision, requirement, or constraint must change
2. AI Assistant proposes updates while preserving stable IDs where appropriate
3. Technical Lead checks alignment with project conventions and adapter configuration
4. Spider Validation Tool re-validates Overall Design by running `/spider-design-validate` (uses capability `spd-spider-fr-validation`)
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Overall Design updated and deterministically validated
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-027 Validate ADRs

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-validate-adrs`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-architect`, `spd-spider-actor-technical-lead`, `spd-spider-actor-spider-tool`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: One or more ADRs exist
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Team runs `/spider-adr-validate` to request deterministic validation of ADRs
2. Spider Validation Tool checks required ADR fields, IDs, and cross-references (uses capability `spd-spider-fr-validation`)
3. Tool reports PASS/FAIL with issues
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: ADR validation status is known; issues are ready for remediation
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->

---

<!-- spd:###:uc-title repeat="many" -->
### UC-028 Create Feature Manifest

<!-- spd:id:usecase -->
**ID**: `spd-spider-usecase-create-feature-manifest`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-spider-actor-project-manager`, `spd-spider-actor-release-manager`, `spd-spider-actor-ai-assistant`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: PRD and Overall Design exist
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**:
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. Project Manager runs `/spider-features` and defines the initial feature list and statuses
2. Release Manager defines readiness expectations for releases
3. AI Assistant creates the Feature Manifest with stable IDs and deterministic status values (uses capability `spd-spider-fr-feature-lifecycle`)
4. Spider Validation Tool validates the Feature Manifest structure and references by running `/spider-features-validate` (uses capability `spd-spider-fr-validation`)
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: Feature Manifest exists and is deterministically validated
<!-- spd:paragraph:postconditions -->
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->
<!-- spd:##:usecases -->

---

<!-- spd:##:nfrs -->
## 5. Non-functional requirements

<!-- spd:###:nfr-title repeat="many" -->
### Validation performance

<!-- spd:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p2` - **ID**: `spd-spider-nfr-validation-performance`

<!-- spd:list:nfr-statements -->
- Deterministic validation SHOULD complete in ≤ 10 seconds for typical repositories (≤ 50k LOC).
- Validation output MUST be clear and actionable.
<!-- spd:list:nfr-statements -->
<!-- spd:id:nfr -->
<!-- spd:###:nfr-title repeat="many" -->

<!-- spd:###:nfr-title repeat="many" -->
### Security and integrity

<!-- spd:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p1` - **ID**: `spd-spider-nfr-security-integrity`

<!-- spd:list:nfr-statements -->
- Validation MUST NOT execute untrusted code from artifacts.
- Validation MUST produce deterministic results given the same repository state.
<!-- spd:list:nfr-statements -->
<!-- spd:id:nfr -->
<!-- spd:###:nfr-title repeat="many" -->

<!-- spd:###:nfr-title repeat="many" -->
### Reliability and recoverability

<!-- spd:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p2` - **ID**: `spd-spider-nfr-reliability-recoverability`

<!-- spd:list:nfr-statements -->
- Validation failures MUST include enough context to remediate without reverse-engineering the validator.
- The system SHOULD provide actionable guidance for common failure modes (missing sections, invalid IDs, missing cross-references).
<!-- spd:list:nfr-statements -->
<!-- spd:id:nfr -->
<!-- spd:###:nfr-title repeat="many" -->

<!-- spd:###:nfr-title repeat="many" -->
### Adoption and usability

<!-- spd:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [x] `p2` - **ID**: `spd-spider-nfr-adoption-usability`

<!-- spd:list:nfr-statements -->
- Workflow instructions SHOULD be executable by a new user without prior Spider context, with ≤ 3 clarifying questions per workflow on average.
- Documentation SHOULD prioritize discoverability of next steps and prerequisites.
<!-- spd:list:nfr-statements -->
<!-- spd:id:nfr -->
<!-- spd:###:nfr-title repeat="many" -->

<!-- spd:###:intentional-exclusions -->
### Intentional Exclusions

<!-- spd:list:exclusions -->
- **Authentication/Authorization** (SEC-PRD-001/002): Not applicable — Spider is a local CLI tool and methodology, not a multi-user system requiring access control.
- **Availability/Recovery** (REL-PRD-001/002): Not applicable — Spider runs locally as a CLI, not as a service requiring uptime guarantees.
- **Scalability** (ARCH-PRD-003): Not applicable — Spider processes single repositories locally; traditional user/data volume scaling does not apply.
- **Throughput/Capacity** (PERF-PRD-002/003): Not applicable — Spider is a local development tool, not a high-throughput system.
- **Accessibility/Internationalization** (UX-PRD-002/003): Not applicable — CLI tool for developers; English-only is acceptable for developer tooling.
- **Regulatory/Legal** (COMPL-PRD-001/002/003): Not applicable — Spider is a methodology with no user data or regulated industry context.
- **Data Ownership/Lifecycle** (DATA-PRD-001/003): Not applicable — Spider does not persist user data; artifacts are owned by the project.
- **Support Requirements** (MAINT-PRD-002): Not applicable — Spider is an open methodology; support is community-driven.
- **Deployment/Monitoring** (OPS-PRD-001/002): Not applicable — Spider is installed locally via pip; no server deployment or monitoring required.
<!-- spd:list:exclusions -->
<!-- spd:###:intentional-exclusions -->
<!-- spd:##:nfrs -->

---

<!-- spd:##:nongoals -->
## 6. Non-Goals & Risks

<!-- spd:###:nongoals-title -->
### Non-Goals

<!-- spd:list:nongoals -->
- Spider does NOT replace project management tools (Jira, Linear, etc.) — it complements them by providing design artifacts that can be referenced from tickets.
- Spider does NOT enforce specific programming languages or frameworks — it is technology-agnostic and works with any stack via adapters.
- Spider does NOT require full coverage — teams can adopt incrementally, starting with PRD and adding artifacts as needed.
- Spider does NOT generate production code automatically — it provides design specifications that developers implement.
- Spider does NOT replace code review — it provides design review capabilities that complement code review.
<!-- spd:list:nongoals -->
<!-- spd:###:nongoals-title -->

<!-- spd:###:risks-title -->
### Risks

<!-- spd:list:risks -->
- **AI agent variability**: Different AI agents may interpret workflows differently, leading to inconsistent artifact quality. Mitigation: deterministic validation catches structural issues.
- **Adoption resistance**: Teams may resist adding design documentation overhead. Mitigation: Spider supports incremental adoption and provides immediate validation value.
- **Template rigidity**: Fixed templates may not fit all project types. Mitigation: adapters allow customization of artifact locations and optional sections.
<!-- spd:list:risks -->
<!-- spd:###:risks-title -->
<!-- spd:##:nongoals -->

---

<!-- spd:##:assumptions -->
## 7. Assumptions & Open Questions

<!-- spd:###:assumptions-title -->
### Assumptions

<!-- spd:list:assumptions -->
- AI coding assistants (Claude Code, Cursor, etc.) can follow structured markdown workflows with embedded instructions.
- Developers have access to Python 3.6+ for running the `spider` CLI tool.
- Projects use Git for version control (adapter discovery relies on `.git` directory).
- Teams are willing to maintain design artifacts as part of their development workflow.
<!-- spd:list:assumptions -->
<!-- spd:###:assumptions-title -->

<!-- spd:###:open-questions-title -->
### Open Questions

<!-- spd:list:open-questions -->
- None at this time.
<!-- spd:list:open-questions -->
<!-- spd:###:open-questions-title -->
<!-- spd:##:assumptions -->

---

<!-- spd:##:context -->
## 8. Additional context

<!-- spd:###:context-title repeat="many" -->
### Terminology

<!-- spd:free:prd-context-notes -->
This PRD uses "Spider" to mean Framework for Documentation and Development.
<!-- spd:free:prd-context-notes -->
<!-- spd:###:context-title repeat="many" -->
<!-- spd:##:context -->
<!-- spd:#:prd -->
