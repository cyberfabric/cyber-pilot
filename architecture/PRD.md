# PRD (Product Requirements Document): FDD

## A. Vision

**Purpose**: FDD is a methodology and productized system for guiding software development through stable artifacts, deterministic validation, and repeatable workflows.

In this project, “FDD” means **Flow-Driven Development**: the project is developed by running workflows (flows), using skills/tools for deterministic checks, and iterating interactively with AI agents.

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

**Success Criteria**:
- Teams can adopt FDD incrementally in new or existing codebases without reorganizing the repository
- Users can start from any stage (PRD, design, implementation, validation) and still make progress
- PRD, ADRs, and designs stay discoverable, consistent, and auditable over time
- Deterministic validation catches structural and semantic issues early (before manual review)
- Traceability is practical and maintainable (IDs in docs, tags in code when enabled)
- The methodology works with any tech stack through adapters (no forced technology choices)
- AI-assisted execution is predictable and repeatable (users can reproduce results)

**Capabilities**:
- Execute workflows to create/update/validate artifacts
- Provide deterministic validation and traceability scanning
- Support adapter-driven configuration for different projects and tech stacks

---

## B. Actors

**Human Actors**:

#### Product Manager

**ID**: `fdd-fdd-actor-product-manager`  
<!-- fdd-id-content -->
**Role**: Defines product requirements, captures use cases, and documents PRD content using FDD workflows

<!-- fdd-id-content -->
#### Architect

**ID**: `fdd-fdd-actor-architect`  
<!-- fdd-id-content -->
**Role**: Designs system architecture, creates overall design documentation, and defines technical patterns

<!-- fdd-id-content -->
#### Developer

**ID**: `fdd-fdd-actor-developer`  
<!-- fdd-id-content -->
**Role**: Implements features according to validated designs, adds traceability tags to code

<!-- fdd-id-content -->
#### QA Engineer

**ID**: `fdd-fdd-actor-qa-engineer`  
<!-- fdd-id-content -->
**Role**: Validates implementation against design specifications and ensures test coverage

<!-- fdd-id-content -->
#### Technical Lead

**ID**: `fdd-fdd-actor-technical-lead`  
<!-- fdd-id-content -->
**Role**: Sets up project adapters, configures FDD for project-specific conventions

<!-- fdd-id-content -->
#### Project Manager

**ID**: `fdd-fdd-actor-project-manager`  
<!-- fdd-id-content -->
**Role**: Monitors development progress, ensures workflows are followed, tracks feature completion

<!-- fdd-id-content -->
#### Documentation Writer

**ID**: `fdd-fdd-actor-documentation-writer`  
<!-- fdd-id-content -->
**Role**: Creates and maintains project documentation using FDD artifacts as source

<!-- fdd-id-content -->
#### DevOps Engineer

**ID**: `fdd-fdd-actor-devops-engineer`  
<!-- fdd-id-content -->
**Role**: Configures CI/CD pipelines, uses adapter specs for build and deployment automation

<!-- fdd-id-content -->
#### Security Engineer

**ID**: `fdd-fdd-actor-security-engineer`  
<!-- fdd-id-content -->
**Role**: Conducts security review of design and code, validates security requirements implementation

<!-- fdd-id-content -->
#### Business Analyst

**ID**: `fdd-fdd-actor-prd-analyst`  
<!-- fdd-id-content -->
**Role**: Analyzes product requirements and translates them into FDD format for Product Manager

<!-- fdd-id-content -->
#### UX Designer

**ID**: `fdd-fdd-actor-ux-designer`  
<!-- fdd-id-content -->
**Role**: Designs user interfaces based on actor flows from feature design

<!-- fdd-id-content -->
#### Performance Engineer

**ID**: `fdd-fdd-actor-performance-engineer`  
<!-- fdd-id-content -->
**Role**: Defines performance targets, reviews designs for performance risks, and validates performance requirements implementation

<!-- fdd-id-content -->
#### Database Architect

**ID**: `fdd-fdd-actor-database-architect`  
<!-- fdd-id-content -->
**Role**: Designs data models and storage strategies, reviews domain model impacts, and validates database-related constraints

<!-- fdd-id-content -->
#### Release Manager

**ID**: `fdd-fdd-actor-release-manager`  
<!-- fdd-id-content -->
**Role**: Manages releases and tracks feature readiness using FDD artifacts (for example via a Feature Manifest when used)

**System Actors**:

<!-- fdd-id-content -->
#### AI Coding Assistant

**ID**: `fdd-fdd-actor-ai-assistant`  
<!-- fdd-id-content -->
**Role**: Executes FDD workflows interactively, generates artifacts, and validates against requirements

<!-- fdd-id-content -->
#### FDD Validation Tool

**ID**: `fdd-fdd-actor-fdd-tool`  
<!-- fdd-id-content -->
**Role**: Automated validation engine that checks artifact structure, ID formats, and traceability

<!-- fdd-id-content -->
#### CI/CD Pipeline

**ID**: `fdd-fdd-actor-ci-pipeline`  
<!-- fdd-id-content -->
**Role**: Automatically validates FDD artifacts on every commit through GitHub Actions or GitLab CI

<!-- fdd-id-content -->
#### Documentation Generator

**ID**: `fdd-fdd-actor-doc-generator`  
<!-- fdd-id-content -->
**Role**: Automatically generates external documentation from FDD artifacts (API docs, architecture diagrams)
<!-- fdd-id-content -->

---

## C. Functional Requirements

#### Workflow-Driven Development

**ID**: `fdd-fdd-fr-workflow-execution`  
<!-- fdd-id-content -->
- The system MUST provide a clear, documented workflow catalog that users and AI agents can execute.
- Artifact locations MUST be adapter-defined; workflows MUST NOT hardcode repository paths.
- The core workflow set MUST cover at least:
  - Adapter bootstrap and configuration
  - PRD creation/update
  - Overall design creation/update
  - ADR creation/update
  - Feature design creation/update
  - Feature implementation (`implement` as the primary implementation workflow)
  - Deterministic validation workflows for the above artifacts and for code traceability (when enabled)
 - The system MUST provide a unified agent entrypoint workflow (`/fdd`) that selects and executes the appropriate workflow (create/update/validate) based on context, or runs `fdd` tool commands when requested.
 - Interactive question-answer flow with AI agents
 - Automated validation after artifact creation
 - Step-by-step guidance for complex operations
 - Independent workflows (no forced sequence)

**Actors**: `fdd-fdd-actor-product-manager`, `fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-project-manager`, `fdd-fdd-actor-release-manager`, `fdd-fdd-actor-developer`, `fdd-fdd-actor-qa-engineer`, `fdd-fdd-actor-security-engineer`, `fdd-fdd-actor-performance-engineer`, `fdd-fdd-actor-database-architect`, `fdd-fdd-actor-devops-engineer`, `fdd-fdd-actor-documentation-writer`, `fdd-fdd-actor-prd-analyst`, `fdd-fdd-actor-ux-designer`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-fdd-tool`, `fdd-fdd-actor-ci-pipeline`

<!-- fdd-id-content -->
 #### Artifact Structure Validation
 
 **ID**: `fdd-fdd-fr-validation`  
 <!-- fdd-id-content -->
 - Deterministic validators for structural checks (sections, IDs, format)
 - Deterministic content validation for semantic quality and boundaries
  - Content MUST be internally consistent (no contradictions)
  - Content MUST NOT include information that belongs in other artifacts
  - Content MUST include required information expected for the artifact kind
  - Content MUST be semantically consistent with upstream/downstream artifacts (no cross-artifact contradictions)
  - Content MUST not omit critical details that are explicitly defined in other artifacts
  - Deterministic validation for key artifacts defined by the adapter (no hardcoded repository paths)
  - 100-point scoring system with category breakdown
  - Pass/fail thresholds (typically ≥90 or 100/100)
  - Cross-reference validation (actor/capability IDs)
  - Placeholder detection (incomplete markers)
  - Detailed issue reporting with recommendations

**Actors**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-developer`, `fdd-fdd-actor-qa-engineer`, `fdd-fdd-actor-security-engineer`, `fdd-fdd-actor-performance-engineer`, `fdd-fdd-actor-database-architect`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-fdd-tool`, `fdd-fdd-actor-ci-pipeline`

<!-- fdd-id-content -->
 #### Adapter Configuration System
 
 **ID**: `fdd-fdd-fr-adapter-config`  
 <!-- fdd-id-content -->
  - Technology-agnostic core methodology
  - Project-specific adapter specifications
  - Adapter MUST define an explicit registry of artifacts and their properties (for example: locations, scope, normative vs context-only)
  - Adapter MUST support per-artifact configuration, including enabling/disabling code traceability checks
  - Tech stack definition (languages, frameworks, tools)
  - Domain model format specification
  - API contract format specification
  - Adapter MUST be able to define deterministic tools/commands used to validate domain model sources and API contract sources
  - Testing strategy and build tool configuration
  - Auto-detection from existing codebase

**Actors**: `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-architect`, `fdd-fdd-actor-database-architect`, `fdd-fdd-actor-performance-engineer`, `fdd-fdd-actor-devops-engineer`, `fdd-fdd-actor-developer`, `fdd-fdd-actor-ai-assistant`

<!-- fdd-id-content -->
 #### Adaptive Design Bootstrapping

**ID**: `fdd-fdd-fr-design-first`  
<!-- fdd-id-content -->
- Users MAY start implementation without having pre-existing design artifacts
- When a workflow needs a traceability source and design artifacts are missing, the workflow MUST bootstrap the minimum viable design interactively and then continue
- Once created, design artifacts become the single source of truth (code follows design)
 - Design iteration MUST be workflow-driven and MUST be followed by deterministic validation
 - Clear separation between PRD, overall design, ADRs, and feature designs
- Behavioral specifications MUST use FDL (plain-English algorithms)

**Actors**: `fdd-fdd-actor-product-manager`, `fdd-fdd-actor-architect`, `fdd-fdd-actor-developer`, `fdd-fdd-actor-prd-analyst`, `fdd-fdd-actor-ux-designer`, `fdd-fdd-actor-security-engineer`, `fdd-fdd-actor-performance-engineer`, `fdd-fdd-actor-database-architect`

<!-- fdd-id-content -->
 #### Traceability Management
 
 **ID**: `fdd-fdd-fr-traceability`  
 <!-- fdd-id-content -->
  - Unique ID system for all design elements using structured format
  - Code tags (@fdd-*) linking implementation to design
  - Traceability validation MUST be configurable per artifact (enabled/disabled via adapter)
  - FDD-ID MAY be versioned by appending a `-vN` suffix (example: `<base-id>-v2`)
  - When an identifier is replaced (REPLACE), the new identifier version MUST be incremented:
  - If the prior identifier has no version suffix, the new identifier MUST end with `-v1`
  - If the prior identifier ends with `-vN`, the new identifier MUST increment the version by 1 (example: `-v1` → `-v2`)
 - Once an identifier becomes versioned (e.g., after a REPLACE produces `-v1`), the version suffix MUST NOT be removed in future references (artifacts and code tags)
 - When an identifier is replaced (REPLACE), all references MUST be updated (all artifacts and all code traceability tags, including qualified `:ph-N:inst-*` references)
 - Qualified IDs for phases and instructions (:ph-N:inst-*)
 - Repository-wide ID scanning and search
- where-defined and where-used commands
- Design-to-code validation (implemented items must have code tags)

**Actors**: `fdd-fdd-actor-developer`, `fdd-fdd-actor-qa-engineer`, `fdd-fdd-actor-fdd-tool`

<!-- fdd-id-content -->
#### Quickstart Guides
 
 **ID**: `fdd-fdd-fr-interactive-docs`  
 <!-- fdd-id-content -->
 - QUICKSTART guides with copy-paste prompts
 - Progressive disclosure (human-facing overview docs, AI navigation rules for agents)
 
 **Actors**: `fdd-fdd-actor-documentation-writer`, `fdd-fdd-actor-product-manager`, `fdd-fdd-actor-release-manager`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-doc-generator`

<!-- fdd-id-content -->
#### Artifact Templates
 
 **ID**: `fdd-fdd-fr-artifact-templates`  
 <!-- fdd-id-content -->
 - The system MUST provide an artifact template catalog for core FDD artifacts (PRD, Overall Design, ADRs, Feature Manifest, Feature Designs)
 - Agents MUST be able to use these templates during workflow execution
 
 **Actors**: `fdd-fdd-actor-documentation-writer`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-doc-generator`, `fdd-fdd-actor-technical-lead`

<!-- fdd-id-content -->
#### Artifact Examples
 
 **ID**: `fdd-fdd-fr-artifact-examples`  
 <!-- fdd-id-content -->
 - The system MUST provide an artifact example catalog for core FDD artifacts (PRD, Overall Design, ADRs, Feature Manifest, Feature Designs)
 - Agents MUST be able to use these examples during workflow execution
 
 **Actors**: `fdd-fdd-actor-documentation-writer`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-doc-generator`, `fdd-fdd-actor-technical-lead`

<!-- fdd-id-content -->
 #### ADR Management
 
 **ID**: `fdd-fdd-fr-arch-decision-mgmt`  
 <!-- fdd-id-content -->
- Create and track architecture decisions with structured format
- Link ADRs to affected design sections and feature IDs
- Decision status tracking (PROPOSED, ACCEPTED, DEPRECATED, SUPERSEDED)
- Impact analysis when ADR changes affect multiple features
- Search ADRs by status, date, or affected components
- Version history for decision evolution

**Actors**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-security-engineer`, `fdd-fdd-actor-performance-engineer`, `fdd-fdd-actor-database-architect`

<!-- fdd-id-content -->
#### PRD Management

**ID**: `fdd-fdd-fr-prd-mgmt`  
<!-- fdd-id-content -->
- Create and update PRD content through workflows
- Enforce stable IDs for actors and capabilities
- PRD deterministic validation integration

**Actors**: `fdd-fdd-actor-product-manager`, `fdd-fdd-actor-prd-analyst`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-fdd-tool`

<!-- fdd-id-content -->
#### Overall Design Management

**ID**: `fdd-fdd-fr-overall-design-mgmt`  
<!-- fdd-id-content -->
- Create and update Overall Design through workflows
- Link requirements to PRD actors and capabilities
- Deterministic validation integration for Overall Design

**Actors**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-fdd-tool`

<!-- fdd-id-content -->
#### Feature Manifest Management

**ID**: `fdd-fdd-fr-feature-manifest-mgmt`  
<!-- fdd-id-content -->
- Create and update Feature Manifest through workflows
- Maintain stable IDs for features and tracking fields
- Deterministic validation integration for Feature Manifest

**Actors**: `fdd-fdd-actor-project-manager`, `fdd-fdd-actor-release-manager`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-fdd-tool`

<!-- fdd-id-content -->
#### Feature Design Management

**ID**: `fdd-fdd-fr-feature-design-mgmt`  
<!-- fdd-id-content -->
- Create and update Feature Design through workflows
- Maintain stable IDs for flows, algorithms, and requirements
- Deterministic validation integration for Feature Design

**Actors**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-fdd-tool`

<!-- fdd-id-content -->
#### Feature Lifecycle Management

**ID**: `fdd-fdd-fr-feature-lifecycle`  
<!-- fdd-id-content -->
- Track feature status from NOT_STARTED through IN_DESIGN, DESIGNED, READY, IN_PROGRESS to DONE
  - Track progress using the project's selected feature tracking approach (for example a feature manifest when used)
  - Feature dependency management and blocking detection
  - Milestone tracking and release planning integration
  - Historical feature completion metrics and velocity tracking
  - Status transition validation (cannot skip states)

**Actors**: `fdd-fdd-actor-project-manager`, `fdd-fdd-actor-release-manager`, `fdd-fdd-actor-developer`, `fdd-fdd-actor-ai-assistant`

<!-- fdd-id-content -->
#### Code Generation from Design

**ID**: `fdd-fdd-fr-code-generation`  
<!-- fdd-id-content -->
- Provide an implementation process that is adapter-aware and works with any programming language
- Apply general best practices that are applicable across languages
- Prefer TDD where feasible and follow SOLID principles
- Use adapter-defined domain model and API contract sources when present
- Add traceability tags when traceability is enabled for the relevant artifacts

**Actors**: `fdd-fdd-actor-developer`, `fdd-fdd-actor-ai-assistant`

<!-- fdd-id-content -->
#### Brownfield Support

 **ID**: `fdd-fdd-fr-brownfield-support`  
 <!-- fdd-id-content -->
 - Add FDD to existing projects without disruption
 - Auto-detect existing architecture from code and configs
 - Reverse-engineer the PRD from requirements documentation
 - Extract Overall Design patterns from implementation
 - Incremental FDD adoption (start with adapter, add artifacts gradually)
 - Legacy system integration with minimal refactoring

**Actors**: `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-architect`, `fdd-fdd-actor-ai-assistant`

<!-- fdd-id-content -->
#### FDL (FDD Description Language)

**ID**: `fdd-fdd-fr-fdl`  
<!-- fdd-id-content -->
- Plain English algorithm description language for actor flows (recursive acronym: FDD Description Language)
- Structured numbered lists with bold keywords (**IF**, **ELSE**, **WHILE**, **FOR EACH**)
- Instruction markers with checkboxes (- [ ] Inst-label: description)
- Phase-based organization (ph-1, ph-2, etc.) for implementation tracking
- Readable by non-programmers for validation and review
- Translates directly to code with traceability tags
- Keywords: **AND**, **OR**, **NOT**, **MUST**, **REQUIRED**, **OPTIONAL**
- Actor-centric (steps start with **Actor** or **System**)

**Actors**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-developer`, `fdd-fdd-actor-prd-analyst`, `fdd-fdd-actor-ux-designer`, `fdd-fdd-actor-product-manager`

<!-- fdd-id-content -->
#### IDE Integration and Tooling

**ID**: `fdd-fdd-fr-ide-integration`  
<!-- fdd-id-content -->
- VS Code extension for FDD artifact editing
- Click-to-navigate for FDD IDs (jump to definition)
- where-used and where-defined commands in IDE
- Inline validation errors and warnings
- Autocomplete for FDD IDs and section references
- Syntax highlighting for FDL (FDD Description Language)
- Integration with `fdd` skill commands
- Code lens showing traceability status

**Actors**: `fdd-fdd-actor-developer`, `fdd-fdd-actor-architect`, `fdd-fdd-actor-devops-engineer`

<!-- fdd-id-content -->
## D. Use Cases
 
#### UC-001: Bootstrap New Project with FDD
 
 **ID**: `fdd-fdd-usecase-bootstrap-project`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`
 
 **Preconditions**: Project repository exists with Git initialized
 
 **Flow**:
 1. Technical Lead initiates FDD setup by requesting AI Assistant to add the FDD framework
 2. AI Assistant establishes minimal adapter configuration (uses capability `fdd-fdd-fr-adapter-config`)
 3. If adapter is missing, the system offers to bootstrap it; the user MAY decline and continue with reduced automation
 4. The system confirms that adapter discovery is possible when the adapter exists

 **Postconditions**: Project has working FDD adapter, ready for PRD and design workflows
 
---
 
<!-- fdd-id-content -->
 #### UC-002: Create PRD
 
 **ID**: `fdd-fdd-usecase-create-prd`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-product-manager`, `fdd-fdd-actor-ai-assistant`
 
 **Preconditions**: Project context exists; adapter may or may not exist
 
 **Flow**:
 1. Product Manager runs `/fdd-prd` and asks AI Assistant to create or refine PRD
 2. AI Assistant asks questions about vision, target users, and problems solved
 3. Product Manager answers; AI Assistant proposes PRD content based on available context 
 4. AI Assistant defines actors and capabilities with stable IDs (uses capability `fdd-fdd-fr-traceability`)
 5. AI Assistant updates the PRD according to answers
 6. Product Manager validates PRD by running `/fdd-prd-validate` (see `fdd-fdd-usecase-validate-prd`)
 
 **Postconditions**: Valid PRD exists, project ready for overall design workflow
 
 ---
 
<!-- fdd-id-content -->
 #### UC-003: Design Feature with AI Assistance
 
 **ID**: `fdd-fdd-usecase-design-feature`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-database-architect`, `fdd-fdd-actor-performance-engineer`
 
 **Preconditions**: PRD and Overall Design validated, feature scope identified (from backlog, ticket, or code context)
 
 **Flow**:
 1. Architect runs `/fdd-feature` and specifies the feature scope and desired outcomes
 2. AI Assistant helps define actor flows in FDL (uses capability `fdd-fdd-fr-design-first`)
 3. Architect defines requirements, constraints, and interfaces at feature scope
 4. Architect runs `/fdd-feature-validate`; the system validates the Feature Design deterministically (uses capability `fdd-fdd-fr-validation`)
 5. Validation reports 100/100 score (required for feature design)
 
 **Postconditions**: Feature Design validated at 100/100, ready for implementation planning via `fdd-fdd-usecase-plan-implementation`
 
 ---
 
<!-- fdd-id-content -->
 #### UC-004: Validate Design Against Requirements - Overall Design
 
 **ID**: `fdd-fdd-usecase-validate-design`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-fdd-tool`
 
 **Preconditions**: Overall Design exists with requirements, actors, and capabilities defined
 
 **Flow**:
 1. Architect runs `/fdd-design-validate` to request deterministic validation of overall design
 2. The system validates structure, required content, and cross-artifact consistency (uses capability `fdd-fdd-fr-validation`)
 3. The system validates ID formats and cross-references (uses capability `fdd-fdd-fr-traceability`)
 4. The system reports a score breakdown with actionable issues
 
 **Postconditions**: Validation report shows PASS (≥90/100) or FAIL with actionable issues, Architect fixes issues or proceeds to next workflow
 
 ---
 
<!-- fdd-id-content -->
 #### UC-005: Trace Requirement to Implementation
 
 **ID**: `fdd-fdd-usecase-trace-requirement`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-developer`, `fdd-fdd-actor-fdd-tool`
 
 **Preconditions**: Feature Design exists; implementation exists (partial or complete); traceability tags are present when traceability is enabled
 
 **Flow**:
 1. Developer selects a requirement ID to verify
 2. The system locates the normative definition and where it is used (uses capability `fdd-fdd-fr-traceability`)
 3. The system reports traceability coverage and gaps
 
 **Postconditions**: Developer confirms requirement is fully implemented with proper traceability, or identifies missing implementation
 
 ---
 
<!-- fdd-id-content -->
 #### UC-006: Update Existing Feature Design
 
 **ID**: `fdd-fdd-usecase-update-feature-design`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-ai-assistant`
 
 **Preconditions**: Feature Design exists and previously validated at 100/100 (triggers `fdd-fdd-usecase-design-feature`)
 
 **Flow**:
 1. Architect identifies need to add new algorithm to existing feature
 2. AI Assistant runs `/fdd-feature` in update mode, loads existing feature design, and presents current content
 3. AI Assistant asks: "What to update?" with options (Add actor flow, Edit algorithm, Add requirement, etc.)
 4. Architect selects "Add new algorithm" option
 5. Architect specifies new algorithm details in FDL (uses capability `fdd-fdd-fr-design-first`)
 6. AI Assistant updates Feature Design while preserving unchanged sections
 7. AI Assistant generates new algorithm ID following format `fdd-<project>-feature-<feature>-algo-<name>` (uses capability `fdd-fdd-fr-traceability`)
 8. FDD Validation Tool re-validates the updated design by running `/fdd-feature-validate` (uses capability `fdd-fdd-fr-validation`)
 9. Validation confirms 100/100 score maintained
 
 **Postconditions**: Feature Design updated with new algorithm, fully validated, ready for implementation
 
 ---
 
<!-- fdd-id-content -->
 #### UC-007: Implement Feature
 
 **ID**: `fdd-fdd-usecase-plan-implementation`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-developer`, `fdd-fdd-actor-ai-assistant`
 
 **Preconditions**: Feature Design exists with a sufficiently clear traceability source (validated when possible)
 
 **Flow**:
 1. Developer requests to code the feature
 2. AI Assistant executes `/fdd-code` workflow (uses capability `fdd-fdd-fr-workflow-execution`)
 3. The system uses Feature Design to extract the minimal implementation scope
 4. AI Assistant and Developer code code iteratively, keeping design and code aligned
 5. Developer adds code traceability tags where used (uses capability `fdd-fdd-fr-traceability`)
 6. FDD Validation Tool validates implementation and traceability by running `/fdd-code-validate` (uses capability `fdd-fdd-fr-validation`)
 
 **Postconditions**: Feature implemented with traceability where used, and validation indicates completeness
 
 ---
 
 <!-- fdd-id-content -->
 #### UC-009: Validate Feature Implementation
 
 **ID**: `fdd-fdd-usecase-validate-implementation`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-qa-engineer`, `fdd-fdd-actor-fdd-tool`
 
 **Preconditions**: Feature implementation exists (partial or complete)
 
 **Flow**:
 1. QA Engineer runs `/fdd-code-validate` to request validation of feature implementation
 2. FDD Validation Tool validates codebase traceability when enabled (uses capability `fdd-fdd-fr-validation`)
 3. Tool validates prerequisite design artifacts first
 4. For each `[x]` marked scope in design, tool expects matching tags in code when traceability is enabled (uses capability `fdd-fdd-fr-traceability`)
 5. For each `[x]` marked FDL instruction, tool expects instruction-level tag in code when traceability is enabled
 6. Tool reports missing tags, extra tags, and format issues
 7. Tool checks build passes and tests run successfully
 
 **Postconditions**: Validation report shows full traceability or lists missing/incorrect tags, QA Engineer confirms implementation complete or requests fixes
 
 ---
 
<!-- fdd-id-content -->
 #### UC-010: Auto-Generate Adapter from Codebase
 
 **ID**: `fdd-fdd-usecase-auto-generate-adapter`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`
 
 **Preconditions**: Project has existing codebase with code, configs, and documentation
 
 **Flow**:
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
 
 **Postconditions**: Adapter with auto-generated specs from existing codebase, validated and ready for FDD workflows
 
 ---
 
<!-- fdd-id-content -->
 #### UC-011: Configure CI/CD Pipeline for FDD Validation
 
 **ID**: `fdd-fdd-usecase-configure-cicd`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-devops-engineer`, `fdd-fdd-actor-ci-pipeline`
 
 **Preconditions**: Project has FDD adapter configured (triggers `fdd-fdd-usecase-bootstrap-project`)
 
 **Flow**:
 1. DevOps Engineer wants to automate FDD artifact validation in CI/CD
 2. DevOps Engineer reads the adapter build/deploy specification for test and build commands (uses capability `fdd-fdd-fr-adapter-config`)
 3. DevOps Engineer creates GitHub Actions workflow or GitLab CI config
 4. Workflow configured to run `/fdd validate` on changed artifacts in pull requests
 5. CI/CD Pipeline executes validation automatically on every commit (uses capability `fdd-fdd-fr-validation`)
 6. Pipeline reports validation results as PR status checks
 7. Pipeline blocks merge if any artifact validation fails (uses capability `fdd-fdd-fr-validation`)
 8. DevOps Engineer configures notifications for validation failures
 
 **Postconditions**: CI/CD Pipeline automatically validates all FDD artifacts, prevents invalid designs from being merged
 
 ---
 
<!-- fdd-id-content -->
 #### UC-012: Security Review of Feature Design
 
 **ID**: `fdd-fdd-usecase-security-review`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-security-engineer`, `fdd-fdd-actor-architect`
 
 **Preconditions**: Feature Design exists and validated (triggers `fdd-fdd-usecase-design-feature`)
 
 **Flow**:
 1. Security Engineer receives notification that new feature design ready for review
 2. Security Engineer reviews feature design content to identify data flows, trust boundaries, and sensitive data handling (uses capability `fdd-fdd-fr-design-first`)
 3. Security Engineer reviews authentication and authorization expectations
 4. Security Engineer identifies missing security controls or vulnerabilities (uses capability `fdd-fdd-fr-validation`)
 5. Security Engineer adds security requirements with stable IDs `fdd-<project>-feature-<feature>-req-security-*`
 6. Architect updates the feature design based on security feedback (triggers `fdd-fdd-usecase-update-feature-design`)
 7. Security Engineer approves design after security requirements are added
 
 **Postconditions**: Feature design includes comprehensive security requirements, ready for secure implementation
 
 ---
 
<!-- fdd-id-content -->
 #### UC-013: Product Requirements Analysis
 
 **ID**: `fdd-fdd-usecase-prd-analysis`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-prd-analyst`, `fdd-fdd-actor-product-manager`
 
 **Preconditions**: Stakeholder requirements gathered but not yet documented in FDD format
 
 **Flow**:
 1. Business Analyst collects raw requirements from stakeholders (interviews, documents, meetings)
 2. Business Analyst analyzes requirements and identifies actors (human and system)
 3. Business Analyst groups related requirements into capabilities (uses capability `fdd-fdd-fr-design-first`)
 4. Business Analyst creates draft structure for the PRD with actors and capabilities
 5. Business Analyst works with Product Manager to refine vision and success criteria
 6. Product Manager runs `/fdd-prd` with Business Analyst's draft (uses capability `fdd-fdd-fr-workflow-execution`)
 7. AI Assistant updates the PRD based on analyzed requirements
 8. Business Analyst reviews generated PRD for completeness and accuracy (uses capability `fdd-fdd-fr-validation`)
 9. Business Analyst confirms all stakeholder requirements covered by capabilities
 
 **Postconditions**: Well-structured PRD capturing all stakeholder requirements in FDD format (triggers `fdd-fdd-usecase-create-prd`)
 
 ---
 
<!-- fdd-id-content -->
 #### UC-014: Design User Interface from Flows
 
 **ID**: `fdd-fdd-usecase-design-ui`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-ux-designer`, `fdd-fdd-actor-architect`
 
 **Preconditions**: Feature design exists with documented actor flows (triggers `fdd-fdd-usecase-design-feature`)
 
 **Flow**:
 1. UX Designer reviews the feature design actor flows to understand user journeys (uses capability `fdd-fdd-fr-design-first`)
 2. UX Designer identifies UI screens needed for each flow step
 3. UX Designer creates wireframes mapping each FDL instruction to UI element
 4. For each flow phase (ph-1, ph-2, etc.), UX Designer designs corresponding screen state
 5. UX Designer validates that UI covers all actor interactions from flows (uses capability `fdd-fdd-fr-traceability`)
 6. UX Designer creates UI mockups with annotations linking to flow IDs (e.g., "Implements `fdd-<project>-feature-<feature>-flow-<name>:ph-1`")
 7. Architect reviews UI mockups against the feature design to ensure completeness
 8. UX Designer updates UI based on feedback if flows were unclear
 9. Architect may update the feature design actor flows if UI reveals missing flow steps (triggers `fdd-fdd-usecase-update-feature-design`)
 
 **Postconditions**: UI mockups fully aligned with feature flows, developers can code UI following both mockups and feature design
 
 ---
 
<!-- fdd-id-content -->
 #### UC-015: Plan Release with Feature Tracking
 
 **ID**: `fdd-fdd-usecase-plan-release`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-release-manager`, `fdd-fdd-actor-project-manager`
 
 **Preconditions**: Overall Design exists and needs to be decomposed into feature-level scope
 
 **Flow**:
  1. Architect and Project Manager review Overall Design to identify feature boundaries
  2. Team defines feature list and assigns initial statuses (NOT_STARTED, IN_DESIGN)
  3. Architect designs features iteratively (IN_DESIGN → DESIGNED → READY)
  4. Developers code features (IN_PROGRESS → DONE)
  5. Validation is run after each meaningful update (uses capability `fdd-fdd-fr-validation`)
 
 **Postconditions**: Clear visibility into feature progress, automated status tracking, dependency validation, historical metrics for planning
 
 ---
 
<!-- fdd-id-content -->
 #### UC-016: Record Architecture Decision
 
 **ID**: `fdd-fdd-usecase-record-adr`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`
 
 **Preconditions**: Architecture decision needs to be documented
 
 **Flow**:
 1. Architect identifies significant technical decision requiring documentation
 2. Architect runs `/fdd-adr` to create new ADR (uses capability `fdd-fdd-fr-workflow-execution`)
 3. AI Assistant assigns sequential ADR ID (e.g., ADR-0001, ADR-0002)
 4. Architect documents decision context, considered options, and chosen solution (uses capability `fdd-fdd-fr-arch-decision-mgmt`)
 5. ADR is created with status ACCEPTED
 6. AI Assistant updates affected design sections to reference ADR (uses capability `fdd-fdd-fr-traceability`)
 
 **Postconditions**: Architecture decision documented with full context, linked to affected design elements, searchable by status and component
 
 ---
 
<!-- fdd-id-content -->
 #### UC-017: Generate Code from Feature Design
 
 **ID**: `fdd-fdd-usecase-generate-code`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-developer`, `fdd-fdd-actor-ai-assistant`
 
 **Preconditions**: Feature scope is known (feature design may or may not exist)
 
 **Flow**:
 1. Developer wants to generate initial code scaffolding
 2. If feature design is missing, AI Assistant bootstraps the minimal feature design (uses capability `fdd-fdd-fr-design-first`)
 3. AI Assistant reads adapter specs for language-specific patterns and project conventions (uses capability `fdd-fdd-fr-adapter-config`)
 4. AI Assistant uses adapter-defined domain model and API contract sources when present (uses capability `fdd-fdd-fr-code-generation`)
 5. AI Assistant generates code scaffolding and test scaffolding following best practices (uses capability `fdd-fdd-fr-code-generation`)
 6. AI Assistant adds traceability tags when enabled (uses capability `fdd-fdd-fr-traceability`)
 7. Developer runs `/fdd-code` to continue implementation from the validated feature design
 8. Developer reviews generated code and adjusts as needed
 
 **Postconditions**: Code scaffolding generated with proper structure and traceability tags when enabled, developer can focus on business logic implementation
 
 ---
 
<!-- fdd-id-content -->
 #### UC-018: Navigate Traceability in IDE
 
 **ID**: `fdd-fdd-usecase-ide-navigation`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-developer`
 
 **Preconditions**: VS Code FDD extension installed, project has FDD artifacts
 
 **Flow**:
 1. Developer opens Feature Design in VS Code
 2. Developer sees FDD ID `fdd-myapp-feature-auth-flow-login` highlighted with syntax coloring (uses capability `fdd-fdd-fr-ide-integration`)
 3. Developer Cmd+Click (or Ctrl+Click) on flow ID to jump to definition in same file
 4. Developer right-clicks on flow ID and selects "Find where-used" from context menu
 5. IDE shows list of references in design docs and code files (uses capability `fdd-fdd-fr-traceability`)
 6. Developer clicks on code reference to navigate to implementation file
 7. Developer sees inline validation errors if ID format is incorrect
 8. Developer uses autocomplete to insert valid FDD IDs when editing
 9. Code lens above function shows traceability status (✅ tagged or ⚠️ missing tags)
 
 **Postconditions**: Developer can navigate between design and code instantly, maintain traceability without manual searching
 
 ---
 
<!-- fdd-id-content -->
 #### UC-019: Migrate Existing Project to FDD
 
 **ID**: `fdd-fdd-usecase-migrate-project`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`
 
 **Actor**: `fdd-fdd-actor-documentation-writer`, `fdd-fdd-actor-doc-generator`
 
 **Preconditions**: Existing project with code but no FDD artifacts
 
 **Flow**:
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
 
 **Postconditions**: Legacy project has FDD artifacts documenting current state, team can use FDD workflows for new features while preserving existing code
 
 ---
 
<!-- fdd-id-content -->
 #### UC-020: Track Feature Progress Through Lifecycle
 
 **ID**: `fdd-fdd-usecase-track-feature-lifecycle`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-project-manager`, `fdd-fdd-actor-developer`
 
 **Preconditions**: A Feature Manifest exists (when used) with multiple features at various stages
 
 **Flow**:
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
 
 **Postconditions**: Clear visibility into feature progress, automated status tracking, dependency validation, historical metrics for planning
 
 ---
 
<!-- fdd-id-content -->
 #### UC-022: Write Actor Flow in FDL
 
 **ID**: `fdd-fdd-usecase-write-fdl-flow`
 
<!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-prd-analyst`
 
 **Preconditions**: Feature Design exists, architect needs to document actor flow
 
 **Flow**:
 1. Architect opens the feature design and navigates to the actor flows
 2. Architect creates new flow: "Login Flow" with ID `fdd-myapp-feature-auth-flow-login` (uses capability `fdd-fdd-fr-design-first`)
 3. Architect writes flow in FDL using plain English with bold keywords (uses capability `fdd-fdd-fr-fdl`):
    ```
    1. **User** enters username and password in login form
    2. **User** clicks "Login" button
    3. **System** validates input format
    4. **IF** input is invalid:
       - [ ] Inst-show-error: **System** displays validation error message
       - **GOTO** step 1
    5. **System** queries database for user credentials
    6. **IF** credentials are valid **AND** account is active:
       - [ ] Inst-create-session: **System** creates user session with JWT token
       - [ ] Inst-redirect: **System** redirects to dashboard
    7. **ELSE IF** account is locked:
       - [ ] Inst-show-locked: **System** displays "Account locked" message
    8. **ELSE**:
       - [ ] Inst-show-invalid: **System** displays "Invalid credentials" error
       - **GOTO** step 1
    ```
 4. Business Analyst reviews FDL flow and confirms it matches product requirements
 5. Business Analyst identifies missing case: "What if user forgot password?"
 6. Architect adds step with **OPTIONAL** path to password reset
 7. UX Designer reads flow and creates UI mockups matching each step and instruction
 8. Architect marks instructions with phases for implementation: ph-1 (validation), ph-2 (authentication), ph-3 (session)
 9. Developer reads FDL flow and understands exact implementation requirements without ambiguity
 
 **Postconditions**: Actor flow documented in plain English readable by all stakeholders, directly translatable to code with instruction-level traceability
 <!-- fdd-id-content -->
 
 ---
 
 <!-- fdd-id-content -->
 #### UC-024: Validate PRD
 
 **ID**: `fdd-fdd-usecase-validate-prd`
 
 <!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-product-manager`, `fdd-fdd-actor-fdd-tool`
 
 **Preconditions**: PRD exists
 
 **Flow**:
 1. Product Manager runs `/fdd-prd-validate` to request PRD validation
 2. FDD Validation Tool validates structure, cross-references, and semantic boundaries (uses capability `fdd-fdd-fr-validation`)
 3. Tool reports PASS/FAIL with actionable issues
 
 **Postconditions**: PRD validation status is known; issues are ready for remediation
 <!-- fdd-id-content -->
 
 ---
 
 <!-- fdd-id-content -->
 #### UC-025: Create Overall Design
 
 **ID**: `fdd-fdd-usecase-create-overall-design`
 
 <!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`
 
 **Preconditions**: PRD exists and is deterministically validated
 
 **Flow**:
 1. Architect runs `/fdd-design` and defines system-level scope, constraints, and key requirements
 2. Technical Lead provides project-specific technical context via adapter (uses capability `fdd-fdd-fr-adapter-config`)
 3. AI Assistant drafts Overall Design with stable IDs and cross-references to PRD actors and capabilities
 4. FDD Validation Tool runs deterministic validation for Overall Design by running `/fdd-design-validate` (uses capability `fdd-fdd-fr-validation`)
 
 **Postconditions**: Overall Design exists and is deterministically validated
 <!-- fdd-id-content -->
 
 ---
 
 <!-- fdd-id-content -->
 #### UC-026: Update Overall Design
 
 **ID**: `fdd-fdd-usecase-update-overall-design`
 
 <!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`
 
 **Preconditions**: Overall Design exists
 
 **Flow**:
 1. Architect runs `/fdd-design` in update mode and identifies what system-level decision, requirement, or constraint must change
 2. AI Assistant proposes updates while preserving stable IDs where appropriate
 3. Technical Lead checks alignment with project conventions and adapter configuration
 4. FDD Validation Tool re-validates Overall Design by running `/fdd-design-validate` (uses capability `fdd-fdd-fr-validation`)
 
 **Postconditions**: Overall Design updated and deterministically validated
 <!-- fdd-id-content -->
 
 ---
 
 <!-- fdd-id-content -->
 #### UC-027: Validate ADRs
 
 **ID**: `fdd-fdd-usecase-validate-adrs`
 
 <!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-fdd-tool`
 
 **Preconditions**: One or more ADRs exist
 
 **Flow**:
 1. Team runs `/fdd-adr-validate` to request deterministic validation of ADRs
 2. FDD Validation Tool checks required ADR fields, IDs, and cross-references (uses capability `fdd-fdd-fr-validation`)
 3. Tool reports PASS/FAIL with issues
 
 **Postconditions**: ADR validation status is known; issues are ready for remediation
 <!-- fdd-id-content -->
 
 ---
 
 <!-- fdd-id-content -->
 #### UC-028: Create Feature Manifest
 
 **ID**: `fdd-fdd-usecase-create-feature-manifest`
 
 <!-- fdd-id-content -->
 **Actor**: `fdd-fdd-actor-project-manager`, `fdd-fdd-actor-release-manager`, `fdd-fdd-actor-ai-assistant`
 
 **Preconditions**: PRD and Overall Design exist
 
 **Flow**:
 1. Project Manager runs `/fdd-features` and defines the initial feature list and statuses
 2. Release Manager defines readiness expectations for releases
 3. AI Assistant creates the Feature Manifest with stable IDs and deterministic status values (uses capability `fdd-fdd-fr-feature-lifecycle`)
 4. FDD Validation Tool validates the Feature Manifest structure and references by running `/fdd-features-validate` (uses capability `fdd-fdd-fr-validation`)
 
 **Postconditions**: Feature Manifest exists and is deterministically validated
 <!-- fdd-id-content -->
 
 ---

## E. Non-functional requirements

#### Validation performance

**ID**: `fdd-fdd-nfr-validation-performance`

<!-- fdd-id-content -->
- Deterministic validation SHOULD complete quickly for typical repositories.
- Validation output MUST be clear and actionable.
<!-- fdd-id-content -->

## F. Additional context

#### Terminology

**ID**: `fdd-fdd-prd-context-terminology`

<!-- fdd-id-content -->
- This PRD uses “FDD” to mean Flow-Driven Development.
<!-- fdd-id-content -->
