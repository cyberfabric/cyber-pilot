# Features: FDD

## A. Status Overview

**Status Overview**: 6 features total (0 implemented, 0 in development, 0 design ready, 0 in design, 6 not started)

**Meaning**:
- ⏳ NOT_STARTED
- 📝 IN_DESIGN
- 📘 DESIGN_READY
- 🔄 IN_DEVELOPMENT
- ✅ IMPLEMENTED

---

## B. Entries

### 1. [Adapter System](feature-adapter-system/) ⏳ HIGH

**ID**: `fdd-fdd-feature-adapter-system`

- **Purpose**: Adapter discovery, registry-driven artifact resolution, and project-specific conventions boundary.
- **Status**: NOT_STARTED
- **Depends On**: None
- **Blocks**: None
- **Scope**:
  - Adapter discovery and adapter root resolution.
  - Artifacts registry loading and path normalization.
  - Adapter spec application boundaries (no core hardcoded paths).
- **Requirements Covered**:
  - `fdd-fdd-fr-adapter-config`
  - `fdd-fdd-fr-brownfield-support`
- **Design Principles Covered**:
  - `fdd-fdd-principle-tech-agnostic`
  - `fdd-fdd-principle-adapter-variability-boundary`
- **Design Constraints Covered**:
  - `fdd-fdd-constraint-markdown`
- **Domain Model Entities**:
  - artifacts registry entries (kind: PRD/DESIGN/ADR/FEATURES/FEATURE)
  - adapter specs (AGENTS.md + specs/*.md)
- **Design Components**:
  - `fdd-fdd-component-adapter-system`
- **API**:
  - adapter-info
  - list-ids
- **Sequences**:
  - `fdd-fdd-seq-adapter-discovery`
- **Data**:
  - None
- **Phases**:
  - `ph-1`: ⏳ NOT_STARTED — adapter discovery and registry resolution
  - `ph-2`: ⏳ NOT_STARTED — adapter spec-driven behavior in workflows/validation

---

### 2. [Workflow Execution Engine](feature-workflow-execution-engine/) ⏳ CRITICAL

**ID**: `fdd-fdd-feature-workflow-execution-engine`

- **Purpose**: Workflow execution engine for operation and validation workflows with prerequisite handling.
- **Status**: NOT_STARTED
- **Depends On**:
  - [fdd-fdd-feature-adapter-system](feature-adapter-system/)
- **Blocks**: None
- **Scope**:
  - Workflow intent resolution and mode selection.
  - Operation workflows: interactive Q/A loop and confirmation gates.
  - Validation workflows: deterministic, chat-only output.
- **Requirements Covered**:
  - `fdd-fdd-fr-workflow-execution`
  - `fdd-fdd-fr-design-first`
  - `fdd-fdd-fr-interactive-docs`
  - `fdd-fdd-fr-ide-integration`
- **Design Principles Covered**:
  - `fdd-fdd-principle-design-first`
  - `fdd-fdd-principle-deterministic-gate`
- **Design Constraints Covered**:
  - `fdd-fdd-constraint-no-forced-tools`
- **Domain Model Entities**:
  - workflows (operation/validation)
  - requirements files
- **Design Components**:
  - `fdd-fdd-component-workflow-engine`
- **API**:
  - validate
  - list-sections
- **Sequences**:
  - `fdd-fdd-seq-intent-to-workflow`
- **Data**:
  - None
- **Phases**:
  - `ph-1`: ⏳ NOT_STARTED — intent resolution and workflow routing
  - `ph-2`: ⏳ NOT_STARTED — operation workflow execution loop
  - `ph-3`: ⏳ NOT_STARTED — validation workflow execution mode

---

### 3. [Deterministic Validation](feature-deterministic-validation/) ⏳ CRITICAL

**ID**: `fdd-fdd-feature-deterministic-validation`

- **Purpose**: Deterministic validation engine for artifacts and cross-artifact checks.
- **Status**: NOT_STARTED
- **Depends On**:
  - [fdd-fdd-feature-adapter-system](feature-adapter-system/)
- **Blocks**:
  - [fdd-fdd-feature-traceability-and-id-management](feature-traceability-and-id-management/)
  - [fdd-fdd-feature-feature-planning-and-lifecycle](feature-feature-planning-and-lifecycle/)
- **Scope**:
  - Artifact structure validation with scoring and actionable errors.
  - Cross-artifact consistency checks (PRD/ADR/DESIGN/FEATURES/feature DESIGN).
  - Deterministic gate behavior and validator-first execution.
- **Requirements Covered**:
  - `fdd-fdd-fr-validation`
  - `fdd-fdd-nfr-validation-performance`
  - `fdd-fdd-nfr-security-integrity`
  - `fdd-fdd-nfr-reliability-recoverability`
  - `fdd-fdd-nfr-adoption-usability`
- **Design Principles Covered**:
  - `fdd-fdd-principle-deterministic-gate`
  - `fdd-fdd-principle-machine-readable`
- **Design Constraints Covered**:
  - `fdd-fdd-constraint-stdlib-only`
- **Domain Model Entities**:
  - validators
  - validation reports
- **Design Components**:
  - `fdd-fdd-component-validation-engine`
- **API**:
  - validate
- **Sequences**:
  - `fdd-fdd-seq-validate-overall-design`
- **Data**:
  - None
- **Phases**:
  - `ph-1`: ⏳ NOT_STARTED — core artifact validators + scoring model
  - `ph-2`: ⏳ NOT_STARTED — cascading validation and compact JSON output

---

### 4. [Traceability & ID Management](feature-traceability-and-id-management/) ⏳ HIGH

**ID**: `fdd-fdd-feature-traceability-and-id-management`

- **Purpose**: Stable ID system, traceability scanning, and repository-wide queries.
- **Status**: NOT_STARTED
- **Depends On**:
  - [fdd-fdd-feature-deterministic-validation](feature-deterministic-validation/)
- **Blocks**: None
- **Scope**:
  - ID formats and qualified IDs (`:ph-N`, `:inst-*`).
  - Repository-wide search commands (`scan-ids`, `where-defined`, `where-used`).
  - Optional code traceability via `@fdd-*` tags.
- **Requirements Covered**:
  - `fdd-fdd-fr-traceability`
  - `fdd-fdd-fr-fdl`
- **Design Principles Covered**:
  - `fdd-fdd-principle-traceability`
  - `fdd-fdd-principle-cli-json-composability`
- **Design Constraints Covered**:
  - `fdd-fdd-constraint-git`
- **Domain Model Entities**:
  - IDs
  - qualified IDs
- **Design Components**:
  - `fdd-fdd-component-id-management`
- **API**:
  - scan-ids
  - where-defined
  - where-used
- **Sequences**:
  - `fdd-fdd-seq-traceability-query`
- **Data**:
  - None
- **Phases**:
  - `ph-1`: ⏳ NOT_STARTED — ID scanning and where-defined/where-used
  - `ph-2`: ⏳ NOT_STARTED — qualified IDs and code tag expectations

---

### 5. [Artifact Authoring Kit](feature-artifact-authoring-kit/) ⏳ MEDIUM

**ID**: `fdd-fdd-feature-artifact-authoring-kit`

- **Purpose**: Templates and canonical examples for authoring FDD artifacts consistently.
- **Status**: NOT_STARTED
- **Depends On**:
  - [fdd-fdd-feature-workflow-execution-engine](feature-workflow-execution-engine/)
- **Blocks**: None
- **Scope**:
  - Templates for core artifacts.
  - Canonical examples for each artifact kind.
  - Workflow references to templates/examples as the generation contract.
- **Requirements Covered**:
  - `fdd-fdd-fr-artifact-templates`
  - `fdd-fdd-fr-artifact-examples`
- **Design Principles Covered**:
  - `fdd-fdd-principle-machine-readable-artifacts`
- **Design Constraints Covered**:
  - `fdd-fdd-constraint-markdown`
- **Domain Model Entities**:
  - templates
  - examples
- **Design Components**:
  - `fdd-fdd-component-methodology-core`
- **API**:
  - read-section
  - get-item
- **Sequences**:
  - `fdd-fdd-seq-intent-to-workflow`
- **Data**:
  - None
- **Phases**:
  - `ph-1`: ⏳ NOT_STARTED — templates inventory and workflow references
  - `ph-2`: ⏳ NOT_STARTED — examples inventory and review consistency

---

### 6. [Feature Planning & Lifecycle](feature-feature-planning-and-lifecycle/) ⏳ HIGH

**ID**: `fdd-fdd-feature-feature-planning-and-lifecycle`

- **Purpose**: Feature manifest + feature design lifecycle, gating, and status transitions.
- **Status**: NOT_STARTED
- **Depends On**:
  - [fdd-fdd-feature-workflow-execution-engine](feature-workflow-execution-engine/)
  - [fdd-fdd-feature-deterministic-validation](feature-deterministic-validation/)
  - [fdd-fdd-feature-traceability-and-id-management](feature-traceability-and-id-management/)
- **Blocks**: None
- **Scope**:
  - Feature manifest management and validation.
  - Feature design management and validation.
  - Status lifecycle rules and transition validation.
- **Requirements Covered**:
  - `fdd-fdd-fr-feature-manifest-mgmt`
  - `fdd-fdd-fr-feature-design-mgmt`
  - `fdd-fdd-fr-feature-lifecycle`
  - `fdd-fdd-fr-code-generation`
  - `fdd-fdd-fr-overall-design-mgmt`
  - `fdd-fdd-fr-prd-mgmt`
  - `fdd-fdd-fr-arch-decision-mgmt`
- **Design Principles Covered**:
  - `fdd-fdd-principle-deterministic-gates`
  - `fdd-fdd-principle-machine-readable`
- **Design Constraints Covered**:
  - `fdd-fdd-constraint-markdown`
  - `fdd-fdd-constraint-git`
- **Domain Model Entities**:
  - features
  - feature designs
- **Design Components**:
  - `fdd-fdd-component-ai-integration-layer`
- **API**:
  - validate
  - list-items
- **Sequences**:
  - `fdd-fdd-seq-validate-overall-design`
- **Data**:
  - None
- **Phases**:
  - `ph-1`: ⏳ NOT_STARTED — FEATURES manifest management + validation
  - `ph-2`: ⏳ NOT_STARTED — feature design management + validation
  - `ph-3`: ⏳ NOT_STARTED — lifecycle gating across artifacts
