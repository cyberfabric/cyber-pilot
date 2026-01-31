<!-- fdd:#:prd -->
# PRD (Product Requirements Document): FDD

<!-- fdd:##:vision -->
## A. Vision

<!-- fdd:paragraph:purpose -->
**Purpose**: FDD is a methodology and productized system for guiding software development through stable artifacts, deterministic validation, and repeatable workflows.
<!-- fdd:paragraph:purpose -->

<!-- fdd:paragraph:context -->
In this project, "FDD" means **Flow-Driven Development**: the project is developed by running workflows (flows), using skills/tools for deterministic checks, and iterating interactively with AI agents.
<!-- fdd:paragraph:context -->

**Target Users**:
<!-- fdd:list:target-users required="true" -->
- Development Teams - Building software with clear design documentation
- Technical Leads & Architects - Defining system architecture and technical decisions
- Product Managers - Capturing product requirements and use cases
- AI Coding Assistants - Executing workflows and validating artifacts
- QA Engineers - Verifying implementation matches design
- Documentation Writers - Creating comprehensive technical documentation
<!-- fdd:list:target-users -->

**Key Problems Solved**:
<!-- fdd:list:key-problems required="true" -->
- **Design-Code Disconnect**: Code diverges from design without single source of truth, leading to outdated documentation
- **Lack of Traceability**: Cannot track product requirements through design to implementation, making impact analysis difficult
- **Unstructured Development**: No repeatable process for design and implementation, causing inconsistent quality
- **AI Integration Challenges**: AI agents cannot follow methodology without structured guidance and machine-readable specifications
- **Validation Complexity**: Manual design reviews are time-consuming and miss structural issues
<!-- fdd:list:key-problems -->

**Success Criteria**:
<!-- fdd:list:success-criteria required="true" -->
- A new user can complete adapter initialization and reach a first passing PRD validation (`fdd validate --artifact architecture/PRD.md`) in ≤ 60 minutes. (Baseline: not measured; Target: v1.0)
- Deterministic validation of the PRD completes in ≤ 3 seconds on a typical developer laptop. (Baseline: ~1s current; Target: v1.0)
- 100% of `fdd-fdd-actor-*` IDs defined in the PRD are resolvable via deterministic search (`fdd where-defined`) without ambiguity. (Baseline: 100% current; Target: v1.0)
- CI validation feedback for PRD changes is produced in ≤ 2 minutes from push to default branch. (Baseline: not measured; Target: v1.0)
- Users can apply a small PRD update (single section change) via `/fdd-prd` in ≤ 10 minutes end-to-end, including re-validation. (Baseline: not measured; Target: v1.0)
<!-- fdd:list:success-criteria -->

**Capabilities**:
<!-- fdd:list:capabilities required="true" -->
- Execute workflows to create/update/validate artifacts
- Provide deterministic validation and traceability scanning
- Support adapter-driven configuration for different projects and tech stacks
<!-- fdd:list:capabilities -->
<!-- fdd:##:vision -->

---

<!-- fdd:##:actors -->
## B. Actors

<!-- fdd:###:actor-title repeat="many" -->
### Product Manager

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-product-manager`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Defines product requirements, captures use cases, and documents PRD content using FDD workflows
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### Architect

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-architect`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Designs system architecture, creates overall design documentation, and defines technical patterns
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### Developer

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-developer`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Implements features according to validated designs, adds traceability tags to code
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### QA Engineer

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-qa-engineer`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Validates implementation against design specifications and ensures test coverage
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### Technical Lead

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-technical-lead`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Sets up project adapters, configures FDD for project-specific conventions
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### Project Manager

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-project-manager`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Monitors development progress, ensures workflows are followed, tracks feature completion
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### Documentation Writer

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-documentation-writer`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Creates and maintains project documentation using FDD artifacts as source
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### DevOps Engineer

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-devops-engineer`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Configures CI/CD pipelines, uses adapter specs for build and deployment automation
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### Security Engineer

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-security-engineer`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Conducts security review of design and code, validates security requirements implementation
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### Business Analyst

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-prd-analyst`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Analyzes product requirements and translates them into FDD format for Product Manager
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### UX Designer

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-ux-designer`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Designs user interfaces based on actor flows from feature design
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### Performance Engineer

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-performance-engineer`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Defines performance targets, reviews designs for performance risks, and validates performance requirements implementation
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### Database Architect

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-database-architect`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Designs data models and storage strategies, reviews domain model impacts, and validates database-related constraints
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### Release Manager

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-release-manager`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Manages releases and tracks feature readiness using FDD artifacts (for example via a Feature Manifest when used)
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### AI Coding Assistant

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-ai-assistant`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Executes FDD workflows interactively, generates artifacts, and validates against requirements
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### FDD Validation Tool

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-fdd-tool`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Automated validation engine that checks artifact structure, ID formats, and traceability
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### CI/CD Pipeline

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-ci-pipeline`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Automatically validates FDD artifacts on every commit through GitHub Actions or GitLab CI
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### Documentation Generator

<!-- fdd:id:actor has="task" -->
**ID**: [ ] - `fdd-fdd-actor-doc-generator`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: Automatically generates external documentation from FDD artifacts (API docs, architecture diagrams)
<!-- fdd:line:actor-role -->
<!-- fdd:###:actor-title repeat="many" -->
<!-- fdd:##:actors -->

---

<!-- fdd:##:frs -->
## C. Functional Requirements

<!-- fdd:###:fr-title repeat="many" -->
### FR-001 Workflow-Driven Development

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p1` - `fdd-fdd-fr-workflow-execution`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
The system MUST provide a clear, documented workflow catalog that users and AI agents can execute. Artifact locations MUST be adapter-defined; workflows MUST NOT hardcode repository paths. The core workflow set MUST cover at least: Adapter bootstrap and configuration, PRD creation/update, Overall design creation/update, ADR creation/update, Feature design creation/update, Feature implementation (`implement` as the primary implementation workflow), and Deterministic validation workflows for the above artifacts and for code traceability (when enabled). The system MUST provide a unified agent entrypoint workflow (`/fdd`) that selects and executes the appropriate workflow (create/update/validate) based on context, or runs `fdd` tool commands when requested. This includes interactive question-answer flow with AI agents, automated validation after artifact creation, step-by-step guidance for complex operations, and independent workflows (no forced sequence).
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-product-manager`, `fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-project-manager`, `fdd-fdd-actor-release-manager`, `fdd-fdd-actor-developer`, `fdd-fdd-actor-qa-engineer`, `fdd-fdd-actor-security-engineer`, `fdd-fdd-actor-performance-engineer`, `fdd-fdd-actor-database-architect`, `fdd-fdd-actor-devops-engineer`, `fdd-fdd-actor-documentation-writer`, `fdd-fdd-actor-prd-analyst`, `fdd-fdd-actor-ux-designer`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-fdd-tool`, `fdd-fdd-actor-ci-pipeline`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-002 Artifact Structure Validation

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p1` - `fdd-fdd-fr-validation`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
Deterministic validators for structural checks (sections, IDs, format). Deterministic content validation for semantic quality and boundaries: Content MUST be internally consistent (no contradictions), Content MUST NOT include information that belongs in other artifacts, Content MUST include required information expected for the artifact kind, Content MUST be semantically consistent with upstream/downstream artifacts (no cross-artifact contradictions), Content MUST not omit critical details that are explicitly defined in other artifacts. Deterministic validation for key artifacts defined by the adapter (no hardcoded repository paths). 100-point scoring system with category breakdown. Pass/fail thresholds (typically ≥90 or 100/100). Cross-reference validation (actor/capability IDs). Placeholder detection (incomplete markers). Detailed issue reporting with recommendations.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-developer`, `fdd-fdd-actor-qa-engineer`, `fdd-fdd-actor-security-engineer`, `fdd-fdd-actor-performance-engineer`, `fdd-fdd-actor-database-architect`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-fdd-tool`, `fdd-fdd-actor-ci-pipeline`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-003 Adapter Configuration System

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p1` - `fdd-fdd-fr-adapter-config`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
Technology-agnostic core methodology. Project-specific adapter specifications. Adapter MUST define an explicit registry of artifacts and their properties (for example: locations, scope, normative vs context-only). Adapter MUST support per-artifact configuration, including enabling/disabling code traceability checks. Tech stack definition (languages, frameworks, tools). Domain model format specification. API contract format specification. Adapter MUST be able to define deterministic tools/commands used to validate domain model sources and API contract sources. Testing strategy and build tool configuration. Auto-detection from existing codebase.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-architect`, `fdd-fdd-actor-database-architect`, `fdd-fdd-actor-performance-engineer`, `fdd-fdd-actor-devops-engineer`, `fdd-fdd-actor-developer`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-004 Adaptive Design Bootstrapping

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p1` - `fdd-fdd-fr-design-first`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
Users MAY start implementation without having pre-existing design artifacts. When a workflow needs a traceability source and design artifacts are missing, the workflow MUST bootstrap the minimum viable design interactively and then continue. Once created, design artifacts become the single source of truth (code follows design). Design iteration MUST be workflow-driven and MUST be followed by deterministic validation. Clear separation between PRD, overall design, ADRs, and feature designs. Behavioral specifications MUST use FDL (plain-English algorithms).
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-product-manager`, `fdd-fdd-actor-architect`, `fdd-fdd-actor-developer`, `fdd-fdd-actor-prd-analyst`, `fdd-fdd-actor-ux-designer`, `fdd-fdd-actor-security-engineer`, `fdd-fdd-actor-performance-engineer`, `fdd-fdd-actor-database-architect`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-005 Traceability Management

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p1` - `fdd-fdd-fr-traceability`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
Unique ID system for all design elements using structured format. Code tags (@fdd-*) linking implementation to design. Traceability validation MUST be configurable per artifact (enabled/disabled via adapter). FDD-ID MAY be versioned by appending a `-vN` suffix (example: `<base-id>-v2`). When an identifier is replaced (REPLACE), the new identifier version MUST be incremented: If the prior identifier has no version suffix, the new identifier MUST end with `-v1`; If the prior identifier ends with `-vN`, the new identifier MUST increment the version by 1 (example: `-v1` → `-v2`). Once an identifier becomes versioned, the version suffix MUST NOT be removed in future references. When an identifier is replaced (REPLACE), all references MUST be updated (all artifacts and all code traceability tags, including qualified `:ph-N:inst-*` references). Qualified IDs for phases and instructions (:ph-N:inst-*). Repository-wide ID scanning and search. where-defined and where-used commands. Design-to-code validation (implemented items must have code tags).
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-developer`, `fdd-fdd-actor-qa-engineer`, `fdd-fdd-actor-fdd-tool`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-006 Quickstart Guides

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p2` - `fdd-fdd-fr-interactive-docs`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
QUICKSTART guides with copy-paste prompts. Progressive disclosure (human-facing overview docs, AI navigation rules for agents).
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-documentation-writer`, `fdd-fdd-actor-product-manager`, `fdd-fdd-actor-release-manager`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-doc-generator`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-007 Artifact Templates

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p1` - `fdd-fdd-fr-artifact-templates`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
The system MUST provide an artifact template catalog for core FDD artifacts (PRD, Overall Design, ADRs, Feature Manifest, Feature Designs). Agents MUST be able to use these templates during workflow execution.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-documentation-writer`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-doc-generator`, `fdd-fdd-actor-technical-lead`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-008 Artifact Examples

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p2` - `fdd-fdd-fr-artifact-examples`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
The system MUST provide an artifact example catalog for core FDD artifacts (PRD, Overall Design, ADRs, Feature Manifest, Feature Designs). Agents MUST be able to use these examples during workflow execution.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-documentation-writer`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-doc-generator`, `fdd-fdd-actor-technical-lead`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-009 ADR Management

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p2` - `fdd-fdd-fr-arch-decision-mgmt`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
Create and track architecture decisions with structured format. Link ADRs to affected design sections and feature IDs. Decision status tracking (PROPOSED, ACCEPTED, DEPRECATED, SUPERSEDED). Impact analysis when ADR changes affect multiple features. Search ADRs by status, date, or affected components. Version history for decision evolution.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-security-engineer`, `fdd-fdd-actor-performance-engineer`, `fdd-fdd-actor-database-architect`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-010 PRD Management

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p1` - `fdd-fdd-fr-prd-mgmt`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
Create and update PRD content through workflows. Enforce stable IDs for actors and capabilities. PRD deterministic validation integration.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-product-manager`, `fdd-fdd-actor-prd-analyst`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-fdd-tool`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-011 Overall Design Management

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p1` - `fdd-fdd-fr-overall-design-mgmt`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
Create and update Overall Design through workflows. Link requirements to PRD actors and capabilities. Deterministic validation integration for Overall Design.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-fdd-tool`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-012 Feature Manifest Management

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p2` - `fdd-fdd-fr-feature-manifest-mgmt`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
Create and update Feature Manifest through workflows. Maintain stable IDs for features and tracking fields. Deterministic validation integration for Feature Manifest.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-project-manager`, `fdd-fdd-actor-release-manager`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-fdd-tool`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-013 Feature Design Management

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p1` - `fdd-fdd-fr-feature-design-mgmt`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
Create and update Feature Design through workflows. Maintain stable IDs for flows, algorithms, and requirements. Deterministic validation integration for Feature Design.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-architect`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-fdd-tool`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-014 Feature Lifecycle Management

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p2` - `fdd-fdd-fr-feature-lifecycle`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
Track feature status from NOT_STARTED through IN_DESIGN, DESIGNED, READY, IN_PROGRESS to DONE. Track progress using the project's selected feature tracking approach (for example a feature manifest when used). Feature dependency management and blocking detection. Milestone tracking and release planning integration. Historical feature completion metrics and velocity tracking. Status transition validation (cannot skip states).
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-project-manager`, `fdd-fdd-actor-release-manager`, `fdd-fdd-actor-developer`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-015 Code Generation from Design

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p2` - `fdd-fdd-fr-code-generation`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
Provide an implementation process that is adapter-aware and works with any programming language. Apply general best practices that are applicable across languages. Prefer TDD where feasible and follow SOLID principles. Use adapter-defined domain model and API contract sources when present. Add traceability tags when traceability is enabled for the relevant artifacts.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-developer`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-016 Brownfield Support

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p2` - `fdd-fdd-fr-brownfield-support`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
Add FDD to existing projects without disruption. Auto-detect existing architecture from code and configs. Reverse-engineer the PRD from requirements documentation. Extract Overall Design patterns from implementation. Incremental FDD adoption (start with adapter, add artifacts gradually). Legacy system integration with minimal refactoring.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-architect`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-017 FDL (FDD Description Language)

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p1` - `fdd-fdd-fr-fdl`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
Plain English algorithm description language for actor flows (recursive acronym: FDD Description Language). Structured numbered lists with bold keywords (**IF**, **ELSE**, **WHILE**, **FOR EACH**). Instruction markers with checkboxes (- [ ] Inst-label: description). Phase-based organization (ph-1, ph-2, etc.) for implementation tracking. Readable by non-programmers for validation and review. Translates directly to code with traceability tags. Keywords: **AND**, **OR**, **NOT**, **MUST**, **REQUIRED**, **OPTIONAL**. Actor-centric (steps start with **Actor** or **System**).
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-architect`, `fdd-fdd-actor-developer`, `fdd-fdd-actor-prd-analyst`, `fdd-fdd-actor-ux-designer`, `fdd-fdd-actor-product-manager`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-018 IDE Integration and Tooling

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p3` - `fdd-fdd-fr-ide-integration`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
VS Code extension for FDD artifact editing. Click-to-navigate for FDD IDs (jump to definition). where-used and where-defined commands in IDE. Inline validation errors and warnings. Autocomplete for FDD IDs and section references. Syntax highlighting for FDL (FDD Description Language). Integration with `fdd` skill commands. Code lens showing traceability status.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-developer`, `fdd-fdd-actor-architect`, `fdd-fdd-actor-devops-engineer`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-019 Multi-Agent IDE Integration

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p2` - `fdd-fdd-fr-multi-agent-integration`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
The system MUST provide commands to generate and maintain agent-specific workflow proxy files for multiple AI coding assistants. Supported agents MUST include Claude, Cursor, Windsurf, and Copilot. The `agent-workflows` command MUST generate workflow entry points in each agent's native format (e.g., `.claude/commands/`, `.cursor/commands/`, `.windsurf/workflows/`, `.github/prompts/`). The `agent-skills` command MUST generate skill/rule entry points that point to the core FDD skill. Configuration MUST be externalized to JSON files (`fdd-agent-workflows.json`, `fdd-agent-skills.json`) with sensible defaults for recognized agents.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-devops-engineer`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-020 Extensible Rules Package System

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p1` - `fdd-fdd-fr-rules-packages`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
The system MUST support extensible rules packages that define templates, checklists, and validation rules for artifact types. Each rules package MUST be identified in the adapter registry and MUST contain a `template.md` file with FDD markers for each artifact kind. Rules packages MAY contain `checklist.md` for semantic validation criteria and `rules.md` for generation guidance. The `validate-rules` command MUST validate that rules packages are structurally correct and that templates follow the fdd-template frontmatter specification.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-fdd-tool`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-021 Template Quality Assurance

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p2` - `fdd-fdd-fr-template-qa`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
The system MUST provide a `self-check` command that validates example artifacts against their templates. The adapter registry MAY define `templates` entries with `template_path`, `example_path`, and `validation_level` properties. When `validation_level` is `STRICT`, the self-check command MUST validate that the example artifact passes all template validation rules. This ensures that templates and examples remain synchronized and that templates are valid.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-fdd-tool`, `fdd-fdd-actor-documentation-writer`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-022 Cross-Artifact Validation

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p1` - `fdd-fdd-fr-cross-artifact-validation`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
The system MUST validate cross-artifact relationships when multiple artifacts are validated together. ID blocks with `covered_by` attributes MUST have at least one reference in artifacts whose template kind matches the covered_by list. All ID references MUST resolve to a definition in some artifact. When a reference is marked as checked (`[x]`), the corresponding definition MUST also be marked as checked. Cross-artifact validation MUST be deterministic and report all consistency violations with line numbers and artifact paths.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-fdd-tool`, `fdd-fdd-actor-ci-pipeline`, `fdd-fdd-actor-architect`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-023 Hierarchical System Registry

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [x] `p2` - `fdd-fdd-fr-hierarchical-registry`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
The system MUST support hierarchical organization of systems in the artifacts registry. Each system MUST have a `name`, `rules` reference, and lists of `artifacts` and optional `codebase` entries. Systems MAY have `children` arrays for nested subsystems. Each artifact entry MUST specify `name`, `path`, `kind`, and `traceability` level (`FULL` or `DOCS-ONLY`). Each codebase entry MUST specify `name`, `path`, and `extensions` for code scanning. The `adapter-info` command MUST display the resolved hierarchical structure.
<!-- fdd:paragraph:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-fdd-tool`, `fdd-fdd-actor-architect`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->
<!-- fdd:##:frs -->

---

<!-- fdd:##:usecases -->
## D. Use Cases

<!-- fdd:###:uc-title repeat="many" -->
### UC-001 Bootstrap New Project with FDD

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-bootstrap-project`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Project repository exists with Git initialized
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Technical Lead initiates FDD setup by requesting AI Assistant to add the FDD framework
2. AI Assistant establishes minimal adapter configuration (uses capability `fdd-fdd-fr-adapter-config`)
3. If adapter is missing, the system offers to bootstrap it; the user MAY decline and continue with reduced automation
4. The system confirms that adapter discovery is possible when the adapter exists
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Project has working FDD adapter, ready for PRD and design workflows
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-002 Create PRD

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-create-prd`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-product-manager`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Project context exists; adapter may or may not exist
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Product Manager runs `/fdd-prd` and asks AI Assistant to create or refine PRD
2. AI Assistant asks questions about vision, target users, and problems solved
3. Product Manager answers; AI Assistant proposes PRD content based on available context
4. AI Assistant defines actors and capabilities with stable IDs (uses capability `fdd-fdd-fr-traceability`)
5. AI Assistant updates the PRD according to answers
6. Product Manager validates PRD by running `/fdd-prd-validate` (see `fdd-fdd-usecase-validate-prd`)
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Valid PRD exists, project ready for overall design workflow
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-003 Design Feature with AI Assistance

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-design-feature`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-architect`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-database-architect`, `fdd-fdd-actor-performance-engineer`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: PRD and Overall Design validated, feature scope identified (from backlog, ticket, or code context)
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Architect runs `/fdd-feature` and specifies the feature scope and desired outcomes
2. AI Assistant helps define actor flows in FDL (uses capability `fdd-fdd-fr-design-first`)
3. Architect defines requirements, constraints, and interfaces at feature scope
4. Architect runs `/fdd-feature-validate`; the system validates the Feature Design deterministically (uses capability `fdd-fdd-fr-validation`)
5. Validation reports 100/100 score (required for feature design)
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Feature Design validated at 100/100, ready for implementation
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-004 Validate Design Against Requirements - Overall Design

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-validate-design`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-architect`, `fdd-fdd-actor-fdd-tool`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Overall Design exists with requirements, actors, and capabilities defined
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Architect runs `/fdd-design-validate` to request deterministic validation of overall design
2. The system validates structure, required content, and cross-artifact consistency (uses capability `fdd-fdd-fr-validation`)
3. The system validates ID formats and cross-references (uses capability `fdd-fdd-fr-traceability`)
4. The system reports a score breakdown with actionable issues
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Validation report shows PASS (≥90/100) or FAIL with actionable issues, Architect fixes issues or proceeds to next workflow
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-005 Trace Requirement to Implementation

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-trace-requirement`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-developer`, `fdd-fdd-actor-fdd-tool`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Feature Design exists; implementation exists (partial or complete); traceability tags are present when traceability is enabled
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Developer selects a requirement ID to verify
2. The system locates the normative definition and where it is used (uses capability `fdd-fdd-fr-traceability`)
3. The system reports traceability coverage and gaps
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Developer confirms requirement is fully implemented with proper traceability, or identifies missing implementation
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-006 Update Existing Feature Design

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-update-feature-design`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-architect`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Feature Design exists and previously validated at 100/100 (triggers `fdd-fdd-usecase-design-feature`)
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Architect identifies need to add new algorithm to existing feature
2. AI Assistant runs `/fdd-feature` in update mode, loads existing feature design, and presents current content
3. AI Assistant asks: "What to update?" with options (Add actor flow, Edit algorithm, Add requirement, etc.)
4. Architect selects "Add new algorithm" option
5. Architect specifies new algorithm details in FDL (uses capability `fdd-fdd-fr-design-first`)
6. AI Assistant updates Feature Design while preserving unchanged sections
7. AI Assistant generates new algorithm ID following format `fdd-<project>-feature-<feature>-algo-<name>` (uses capability `fdd-fdd-fr-traceability`)
8. FDD Validation Tool re-validates the updated design by running `/fdd-feature-validate` (uses capability `fdd-fdd-fr-validation`)
9. Validation confirms 100/100 score maintained
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Feature Design updated with new algorithm, fully validated, ready for implementation
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-007 Implement Feature

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-plan-implementation`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-developer`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Feature Design exists with a sufficiently clear traceability source (validated when possible)
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Developer requests to code the feature
2. AI Assistant executes `/fdd-code` workflow (uses capability `fdd-fdd-fr-workflow-execution`)
3. The system uses Feature Design to extract the minimal implementation scope
4. AI Assistant and Developer code iteratively, keeping design and code aligned
5. Developer adds code traceability tags where used (uses capability `fdd-fdd-fr-traceability`)
6. FDD Validation Tool validates implementation and traceability by running `/fdd-code-validate` (uses capability `fdd-fdd-fr-validation`)
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Feature implemented with traceability where used, and validation indicates completeness
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-009 Validate Feature Implementation

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-validate-implementation`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-qa-engineer`, `fdd-fdd-actor-fdd-tool`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Feature implementation exists (partial or complete)
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. QA Engineer runs `/fdd-code-validate` to request validation of feature implementation
2. FDD Validation Tool validates codebase traceability when enabled (uses capability `fdd-fdd-fr-validation`)
3. Tool validates prerequisite design artifacts first
4. For each `[x]` marked scope in design, tool expects matching tags in code when traceability is enabled (uses capability `fdd-fdd-fr-traceability`)
5. For each `[x]` marked FDL instruction, tool expects instruction-level tag in code when traceability is enabled
6. Tool reports missing tags, extra tags, and format issues
7. Tool checks build passes and tests run successfully
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Validation report shows full traceability or lists missing/incorrect tags, QA Engineer confirms implementation complete or requests fixes
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-010 Auto-Generate Adapter from Codebase

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-auto-generate-adapter`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Project has existing codebase with code, configs, and documentation
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Technical Lead wants to add FDD to existing project
2. AI Assistant runs `/fdd-adapter-auto` to analyze existing codebase (uses capability `fdd-fdd-fr-workflow-execution`)
3. AI Assistant scans project for documentation (README, ARCHITECTURE, CONTRIBUTING) (uses capability `fdd-fdd-fr-adapter-config`)
4. AI Assistant analyzes config files (package.json, requirements.txt, Cargo.toml, etc.)
5. AI Assistant detects tech stack (languages, frameworks, versions)
6. AI Assistant analyzes code structure and naming conventions
7. AI Assistant discovers domain model format from code (TypeScript types, JSON Schema, etc.)
8. AI Assistant discovers API format from definitions (OpenAPI, GraphQL schema, etc.)
9. AI Assistant proposes adapter specifications (tech stack, domain model format, conventions, etc.)
10. Technical Lead reviews and approves proposed specs
11. AI Assistant updates adapter specs in the adapter specifications area
12. AI Assistant updates the adapter's AI navigation rules with WHEN rules for each spec
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Adapter with auto-generated specs from existing codebase, validated and ready for FDD workflows
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-011 Configure CI/CD Pipeline for FDD Validation

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-configure-cicd`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-devops-engineer`, `fdd-fdd-actor-ci-pipeline`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Project has FDD adapter configured (triggers `fdd-fdd-usecase-bootstrap-project`)
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. DevOps Engineer wants to automate FDD artifact validation in CI/CD
2. DevOps Engineer reads the adapter build/deploy specification for test and build commands (uses capability `fdd-fdd-fr-adapter-config`)
3. DevOps Engineer creates GitHub Actions workflow or GitLab CI config
4. Workflow configured to run `/fdd validate` on changed artifacts in pull requests
5. CI/CD Pipeline executes validation automatically on every commit (uses capability `fdd-fdd-fr-validation`)
6. Pipeline reports validation results as PR status checks
7. Pipeline blocks merge if any artifact validation fails (uses capability `fdd-fdd-fr-validation`)
8. DevOps Engineer configures notifications for validation failures
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: CI/CD Pipeline automatically validates all FDD artifacts, prevents invalid designs from being merged
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-012 Security Review of Feature Design

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-security-review`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-security-engineer`, `fdd-fdd-actor-architect`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Feature Design exists and validated (triggers `fdd-fdd-usecase-design-feature`)
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Security Engineer receives notification that new feature design ready for review
2. Security Engineer reviews feature design content to identify data flows, trust boundaries, and sensitive data handling (uses capability `fdd-fdd-fr-design-first`)
3. Security Engineer reviews authentication and authorization expectations
4. Security Engineer identifies missing security controls or vulnerabilities (uses capability `fdd-fdd-fr-validation`)
5. Security Engineer adds security requirements with stable IDs `fdd-<project>-feature-<feature>-req-security-*`
6. Architect updates the feature design based on security feedback (triggers `fdd-fdd-usecase-update-feature-design`)
7. Security Engineer approves design after security requirements are added
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Feature design includes comprehensive security requirements, ready for secure implementation
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-013 Product Requirements Analysis

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-prd-analysis`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-prd-analyst`, `fdd-fdd-actor-product-manager`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Stakeholder requirements gathered but not yet documented in FDD format
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Business Analyst collects raw requirements from stakeholders (interviews, documents, meetings)
2. Business Analyst analyzes requirements and identifies actors (human and system)
3. Business Analyst groups related requirements into capabilities (uses capability `fdd-fdd-fr-design-first`)
4. Business Analyst creates draft structure for the PRD with actors and capabilities
5. Business Analyst works with Product Manager to refine vision and success criteria
6. Product Manager runs `/fdd-prd` with Business Analyst's draft (uses capability `fdd-fdd-fr-workflow-execution`)
7. AI Assistant updates the PRD based on analyzed requirements
8. Business Analyst reviews generated PRD for completeness and accuracy (uses capability `fdd-fdd-fr-validation`)
9. Business Analyst confirms all stakeholder requirements covered by capabilities
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Well-structured PRD capturing all stakeholder requirements in FDD format (triggers `fdd-fdd-usecase-create-prd`)
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-014 Design User Interface from Flows

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-design-ui`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-ux-designer`, `fdd-fdd-actor-architect`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Feature design exists with documented actor flows (triggers `fdd-fdd-usecase-design-feature`)
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. UX Designer reviews the feature design actor flows to understand user journeys (uses capability `fdd-fdd-fr-design-first`)
2. UX Designer identifies UI screens needed for each flow step
3. UX Designer creates wireframes mapping each FDL instruction to UI element
4. For each flow phase (ph-1, ph-2, etc.), UX Designer designs corresponding screen state
5. UX Designer validates that UI covers all actor interactions from flows (uses capability `fdd-fdd-fr-traceability`)
6. UX Designer creates UI mockups with annotations linking to flow IDs (e.g., "Implements `fdd-<project>-feature-<feature>-flow-<name>:ph-1`")
7. Architect reviews UI mockups against the feature design to ensure completeness
8. UX Designer updates UI based on feedback if flows were unclear
9. Architect may update the feature design actor flows if UI reveals missing flow steps (triggers `fdd-fdd-usecase-update-feature-design`)
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: UI mockups fully aligned with feature flows, developers can code UI following both mockups and feature design
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-015 Plan Release with Feature Tracking

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-plan-release`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-release-manager`, `fdd-fdd-actor-project-manager`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Overall Design exists and needs to be decomposed into feature-level scope
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Architect and Project Manager review Overall Design to identify feature boundaries
2. Team defines feature list and assigns initial statuses (NOT_STARTED, IN_DESIGN)
3. Architect designs features iteratively (IN_DESIGN → DESIGNED → READY)
4. Developers code features (IN_PROGRESS → DONE)
5. Validation is run after each meaningful update (uses capability `fdd-fdd-fr-validation`)
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Clear visibility into feature progress, automated status tracking, dependency validation, historical metrics for planning
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-016 Record Architecture Decision

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-record-adr`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Architecture decision needs to be documented
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Architect identifies significant technical decision requiring documentation
2. Architect runs `/fdd-adr` to create new ADR (uses capability `fdd-fdd-fr-workflow-execution`)
3. AI Assistant assigns sequential ADR ID (e.g., ADR-0001, ADR-0002)
4. Architect documents decision context, considered options, and chosen solution (uses capability `fdd-fdd-fr-arch-decision-mgmt`)
5. ADR is created with status ACCEPTED
6. AI Assistant updates affected design sections to reference ADR (uses capability `fdd-fdd-fr-traceability`)
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Architecture decision documented with full context, linked to affected design elements, searchable by status and component
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-017 Generate Code from Feature Design

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-generate-code`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-developer`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Feature scope is known (feature design may or may not exist)
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Developer wants to generate initial code scaffolding
2. If feature design is missing, AI Assistant bootstraps the minimal feature design (uses capability `fdd-fdd-fr-design-first`)
3. AI Assistant reads adapter specs for language-specific patterns and project conventions (uses capability `fdd-fdd-fr-adapter-config`)
4. AI Assistant uses adapter-defined domain model and API contract sources when present (uses capability `fdd-fdd-fr-code-generation`)
5. AI Assistant generates code scaffolding and test scaffolding following best practices (uses capability `fdd-fdd-fr-code-generation`)
6. AI Assistant adds traceability tags when enabled (uses capability `fdd-fdd-fr-traceability`)
7. Developer runs `/fdd-code` to continue implementation from the validated feature design
8. Developer reviews generated code and adjusts as needed
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Code scaffolding generated with proper structure and traceability tags when enabled, developer can focus on business logic implementation
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-018 Navigate Traceability in IDE

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-ide-navigation`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-developer`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: VS Code FDD extension installed, project has FDD artifacts
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Developer opens Feature Design in VS Code
2. Developer sees FDD ID `fdd-fdd-seq-intent-to-workflow` highlighted with syntax coloring (uses capability `fdd-fdd-fr-ide-integration`)
3. Developer Cmd+Click (or Ctrl+Click) on flow ID to jump to definition in same file
4. Developer right-clicks on flow ID and selects "Find where-used" from context menu
5. IDE shows list of references in design docs and code files (uses capability `fdd-fdd-fr-traceability`)
6. Developer clicks on code reference to navigate to implementation file
7. Developer sees inline validation errors if ID format is incorrect
8. Developer uses autocomplete to insert valid FDD IDs when editing
9. Code lens above function shows traceability status (✅ tagged or ⚠️ missing tags)
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Developer can navigate between design and code instantly, maintain traceability without manual searching
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-019 Migrate Existing Project to FDD

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-migrate-project`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-documentation-writer`, `fdd-fdd-actor-doc-generator`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Existing project with code but no FDD artifacts
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Technical Lead wants to adopt FDD for legacy project
2. AI Assistant runs `/fdd-adapter-auto` to analyze existing codebase (uses capability `fdd-fdd-fr-brownfield-support`)
3. AI Assistant scans existing project documentation for PRD content
4. AI Assistant proposes PRD content based on discovered information
5. Technical Lead reviews and refines proposed PRD content
6. AI Assistant analyzes code structure to extract architectural patterns
7. AI Assistant proposes Overall Design content from implementation patterns
8. Technical Lead identifies which features to document first (incremental adoption)
9. AI Assistant creates or updates Feature Design for priority features using the adapter-defined locations
10. Developer adds traceability tags to existing code incrementally (uses capability `fdd-fdd-fr-traceability`)
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Legacy project has FDD artifacts documenting current state, team can use FDD workflows for new features while preserving existing code
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-020 Track Feature Progress Through Lifecycle

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-track-feature-lifecycle`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-project-manager`, `fdd-fdd-actor-developer`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: A Feature Manifest exists (when used) with multiple features at various stages
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Project Manager opens a feature manifest to review current status (uses capability `fdd-fdd-fr-feature-lifecycle`)
2. Project Manager sees feature statuses: ⏳ NOT_STARTED, 🔄 IN_PROGRESS, ✅ DONE
3. Developer marks feature as 🔄 IN_PROGRESS when starting implementation work
4. System validates feature has Feature Design at 100/100 before allowing IN_PROGRESS status
5. As developer completes implementation work, system suggests status update
6. Developer runs final validation before marking feature ✅ DONE (uses capability `fdd-fdd-fr-validation`)
7. Project Manager tracks velocity by counting completed features per sprint
8. Project Manager identifies blocking dependencies (Feature B depends on Feature A)
9. System alerts if Feature B IN_PROGRESS but Feature A still NOT_STARTED
10. Project Manager generates progress report showing feature completion timeline
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Clear visibility into feature progress, automated status tracking, dependency validation, historical metrics for planning
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-022 Write Actor Flow in FDL

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-write-fdl-flow`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-architect`, `fdd-fdd-actor-prd-analyst`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Feature Design exists, architect needs to document actor flow
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Architect opens the feature design and navigates to the actor flows
2. Architect creates new flow: "Login Flow" with ID `fdd-fdd-seq-intent-to-workflow` (uses capability `fdd-fdd-fr-design-first`)
3. Architect writes flow in FDL using plain English with bold keywords (uses capability `fdd-fdd-fr-fdl`)
4. Business Analyst reviews FDL flow and confirms it matches product requirements
5. Business Analyst identifies missing case: "What if user forgot password?"
6. Architect adds step with **OPTIONAL** path to password reset
7. UX Designer reads flow and creates UI mockups matching each step and instruction
8. Architect marks instructions with phases for implementation: ph-1 (validation), ph-2 (authentication), ph-3 (session)
9. Developer reads FDL flow and understands exact implementation requirements without ambiguity
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Actor flow documented in plain English readable by all stakeholders, directly translatable to code with instruction-level traceability
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-024 Validate PRD

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-validate-prd`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-product-manager`, `fdd-fdd-actor-fdd-tool`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: PRD exists
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Product Manager runs `/fdd-prd-validate` to request PRD validation
2. FDD Validation Tool validates structure, cross-references, and semantic boundaries (uses capability `fdd-fdd-fr-validation`)
3. Tool reports PASS/FAIL with actionable issues
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: PRD validation status is known; issues are ready for remediation
<!-- fdd:paragraph:postconditions -->

**Alternative Flows**:
<!-- fdd:list:alternative-flows -->
- **Validation fails**: If step 3 reports FAIL, Product Manager reviews issues, edits PRD to fix them, and re-runs validation (loop to step 1)
<!-- fdd:list:alternative-flows -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-025 Create Overall Design

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-create-overall-design`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: PRD exists and is deterministically validated
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Architect runs `/fdd-design` and defines system-level scope, constraints, and key requirements
2. Technical Lead provides project-specific technical context via adapter (uses capability `fdd-fdd-fr-adapter-config`)
3. AI Assistant drafts Overall Design with stable IDs and cross-references to PRD actors and capabilities
4. FDD Validation Tool runs deterministic validation for Overall Design by running `/fdd-design-validate` (uses capability `fdd-fdd-fr-validation`)
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Overall Design exists and is deterministically validated
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-026 Update Overall Design

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-update-overall-design`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: Overall Design exists
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Architect runs `/fdd-design` in update mode and identifies what system-level decision, requirement, or constraint must change
2. AI Assistant proposes updates while preserving stable IDs where appropriate
3. Technical Lead checks alignment with project conventions and adapter configuration
4. FDD Validation Tool re-validates Overall Design by running `/fdd-design-validate` (uses capability `fdd-fdd-fr-validation`)
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Overall Design updated and deterministically validated
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-027 Validate ADRs

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-validate-adrs`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-fdd-tool`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: One or more ADRs exist
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Team runs `/fdd-adr-validate` to request deterministic validation of ADRs
2. FDD Validation Tool checks required ADR fields, IDs, and cross-references (uses capability `fdd-fdd-fr-validation`)
3. Tool reports PASS/FAIL with issues
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: ADR validation status is known; issues are ready for remediation
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->

---

<!-- fdd:###:uc-title repeat="many" -->
### UC-028 Create Feature Manifest

<!-- fdd:id:usecase -->
**ID**: `fdd-fdd-usecase-create-feature-manifest`
<!-- fdd:id:usecase -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-fdd-actor-project-manager`, `fdd-fdd-actor-release-manager`, `fdd-fdd-actor-ai-assistant`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: PRD and Overall Design exist
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**:
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Project Manager runs `/fdd-features` and defines the initial feature list and statuses
2. Release Manager defines readiness expectations for releases
3. AI Assistant creates the Feature Manifest with stable IDs and deterministic status values (uses capability `fdd-fdd-fr-feature-lifecycle`)
4. FDD Validation Tool validates the Feature Manifest structure and references by running `/fdd-features-validate` (uses capability `fdd-fdd-fr-validation`)
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Feature Manifest exists and is deterministically validated
<!-- fdd:paragraph:postconditions -->
<!-- fdd:###:uc-title repeat="many" -->
<!-- fdd:##:usecases -->

---

<!-- fdd:##:nfrs -->
## E. Non-functional requirements

<!-- fdd:###:nfr-title repeat="many" -->
### Validation performance

<!-- fdd:id:nfr has="priority,task" covered_by="design" -->
**ID**: [x] `p2` - `fdd-fdd-nfr-validation-performance`
<!-- fdd:id:nfr -->

<!-- fdd:list:nfr-statements -->
- Deterministic validation SHOULD complete in ≤ 10 seconds for typical repositories (≤ 50k LOC).
- Validation output MUST be clear and actionable.
<!-- fdd:list:nfr-statements -->
<!-- fdd:###:nfr-title repeat="many" -->

<!-- fdd:###:nfr-title repeat="many" -->
### Security and integrity

<!-- fdd:id:nfr has="priority,task" covered_by="design" -->
**ID**: [x] `p1` - `fdd-fdd-nfr-security-integrity`
<!-- fdd:id:nfr -->

<!-- fdd:list:nfr-statements -->
- Validation MUST NOT execute untrusted code from artifacts.
- Validation MUST produce deterministic results given the same repository state.
<!-- fdd:list:nfr-statements -->
<!-- fdd:###:nfr-title repeat="many" -->

<!-- fdd:###:nfr-title repeat="many" -->
### Reliability and recoverability

<!-- fdd:id:nfr has="priority,task" covered_by="design" -->
**ID**: [x] `p2` - `fdd-fdd-nfr-reliability-recoverability`
<!-- fdd:id:nfr -->

<!-- fdd:list:nfr-statements -->
- Validation failures MUST include enough context to remediate without reverse-engineering the validator.
- The system SHOULD provide actionable guidance for common failure modes (missing sections, invalid IDs, missing cross-references).
<!-- fdd:list:nfr-statements -->
<!-- fdd:###:nfr-title repeat="many" -->

<!-- fdd:###:nfr-title repeat="many" -->
### Adoption and usability

<!-- fdd:id:nfr has="priority,task" covered_by="design" -->
**ID**: [x] `p2` - `fdd-fdd-nfr-adoption-usability`
<!-- fdd:id:nfr -->

<!-- fdd:list:nfr-statements -->
- Workflow instructions SHOULD be executable by a new user without prior FDD context, with ≤ 3 clarifying questions per workflow on average.
- Documentation SHOULD prioritize discoverability of next steps and prerequisites.
<!-- fdd:list:nfr-statements -->
<!-- fdd:###:nfr-title repeat="many" -->

<!-- fdd:###:intentional-exclusions -->
### Intentional Exclusions

<!-- fdd:list:exclusions -->
- **Authentication/Authorization** (SEC-PRD-001/002): Not applicable — FDD is a local CLI tool and methodology, not a multi-user system requiring access control.
- **Availability/Recovery** (REL-PRD-001/002): Not applicable — FDD runs locally as a CLI, not as a service requiring uptime guarantees.
- **Scalability** (ARCH-PRD-003): Not applicable — FDD processes single repositories locally; traditional user/data volume scaling does not apply.
- **Throughput/Capacity** (PERF-PRD-002/003): Not applicable — FDD is a local development tool, not a high-throughput system.
- **Accessibility/Internationalization** (UX-PRD-002/003): Not applicable — CLI tool for developers; English-only is acceptable for developer tooling.
- **Regulatory/Legal** (COMPL-PRD-001/002/003): Not applicable — FDD is a methodology with no user data or regulated industry context.
- **Data Ownership/Lifecycle** (DATA-PRD-001/003): Not applicable — FDD does not persist user data; artifacts are owned by the project.
- **Support Requirements** (MAINT-PRD-002): Not applicable — FDD is an open methodology; support is community-driven.
- **Deployment/Monitoring** (OPS-PRD-001/002): Not applicable — FDD is installed locally via pip; no server deployment or monitoring required.
<!-- fdd:list:exclusions -->
<!-- fdd:###:intentional-exclusions -->
<!-- fdd:##:nfrs -->

---

<!-- fdd:##:nongoals -->
## F. Non-Goals & Risks

<!-- fdd:###:nongoals-title -->
### Non-Goals

<!-- fdd:list:nongoals -->
- FDD does NOT replace project management tools (Jira, Linear, etc.) — it complements them by providing design artifacts that can be referenced from tickets.
- FDD does NOT enforce specific programming languages or frameworks — it is technology-agnostic and works with any stack via adapters.
- FDD does NOT require full coverage — teams can adopt incrementally, starting with PRD and adding artifacts as needed.
- FDD does NOT generate production code automatically — it provides design specifications that developers implement.
- FDD does NOT replace code review — it provides design review capabilities that complement code review.
<!-- fdd:list:nongoals -->
<!-- fdd:###:nongoals-title -->

<!-- fdd:###:risks-title -->
### Risks

<!-- fdd:list:risks -->
- **AI agent variability**: Different AI agents may interpret workflows differently, leading to inconsistent artifact quality. Mitigation: deterministic validation catches structural issues.
- **Adoption resistance**: Teams may resist adding design documentation overhead. Mitigation: FDD supports incremental adoption and provides immediate validation value.
- **Template rigidity**: Fixed templates may not fit all project types. Mitigation: adapters allow customization of artifact locations and optional sections.
<!-- fdd:list:risks -->
<!-- fdd:###:risks-title -->
<!-- fdd:##:nongoals -->

---

<!-- fdd:##:assumptions -->
## G. Assumptions & Open Questions

<!-- fdd:###:assumptions-title -->
### Assumptions

<!-- fdd:list:assumptions -->
- AI coding assistants (Claude Code, Cursor, etc.) can follow structured markdown workflows with embedded instructions.
- Developers have access to Python 3.10+ for running the `fdd` CLI tool.
- Projects use Git for version control (adapter discovery relies on `.git` directory).
- Teams are willing to maintain design artifacts as part of their development workflow.
<!-- fdd:list:assumptions -->
<!-- fdd:###:assumptions-title -->

<!-- fdd:###:open-questions-title -->
### Open Questions

<!-- fdd:list:open-questions -->
- None at this time.
<!-- fdd:list:open-questions -->
<!-- fdd:###:open-questions-title -->
<!-- fdd:##:assumptions -->

---

<!-- fdd:##:context -->
## H. Additional context

<!-- fdd:###:context-title repeat="many" -->
### Terminology

<!-- fdd:id:prd-context has="task" -->
**ID**: [ ] - `fdd-fdd-prd-context-terminology`
<!-- fdd:id:prd-context -->

<!-- fdd:list:prd-context-notes -->
- This PRD uses "FDD" to mean Flow-Driven Development.
<!-- fdd:list:prd-context-notes -->
<!-- fdd:###:context-title repeat="many" -->
<!-- fdd:##:context -->
<!-- fdd:#:prd -->
