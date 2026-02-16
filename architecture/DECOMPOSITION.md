# Decomposition: Cypilot

## 1. Overview

Cypilot features are organized around **architectural components** with explicit dependencies. Foundation features (Methodology Core, Adapter System) enable higher-level features (Kit Packages, CLI Tool, Workflows). The decomposition follows the component model from DESIGN.md, ensuring each feature maps to one or more components and covers related functional requirements.


## 2. Entries

**Overall implementation status:**
- [x] `p1` - **ID**: `cpt-cypilot-status-overall`

### 1. [Methodology Core](features/methodology-core.md) ✅ HIGH

- [x] `p1` - **ID**: `cpt-cypilot-feature-methodology-core`

- **Purpose**: Provide universal Cypilot specifications including requirements, CDSL language, and base template syntax that all projects share.

- **Depends On**: None

- **Scope**:
  - Requirements specifications (`requirements/*.md`)
  - CDSL (Cypilot Description Language) specification
  - ID formats and naming specification
  - Execution protocol definition

- **Out of scope**:
  - Project-specific customization
  - Concrete templates for artifact kinds

- **Requirements Covered**:
  - [x] `p1` - `cpt-cypilot-fr-artifact-templates`
  - [x] `p2` - `cpt-cypilot-fr-artifact-examples`
  - [x] `p1` - `cpt-cypilot-fr-cdsl`

- **Design Principles Covered**:
  - [x] `p1` - `cpt-cypilot-principle-tech-agnostic`
  - [x] `p1` - `cpt-cypilot-principle-machine-readable`
  - [x] `p1` - `cpt-cypilot-principle-machine-readable-artifacts`

- **Design Constraints Covered**:
  - [x] `p1` - `cpt-cypilot-constraint-markdown`
  - [x] `p1` - `cpt-cypilot-constraint-no-forced-tools`

- **Domain Model Entities**:
  - Artifact
  - Workflow
  - CDSL

- **Design Components**:
  - [x] `p1` - `cpt-cypilot-component-methodology-core`

- **API**:
  - Specifications only, no CLI commands

- **Sequences**:
  - [x] `p1` - `cpt-cypilot-seq-intent-to-workflow`

- **Data**:
  - [x] `p3` - `cpt-cypilot-dbtable-na`


### 2. [Adapter System](features/adapter-system.md) ✅ HIGH

- [x] `p1` - **ID**: `cpt-cypilot-feature-adapter-system`

- **Purpose**: Enable project-specific customization without modifying core methodology through adapter configuration and hierarchical artifact registry.

- **Depends On**: None

- **Scope**:
  - Adapter discovery (`adapter-info` command)
  - `artifacts.json` registry with hierarchical systems
  - `.cypilot-adapter/` directory structure
  - Spec files (tech-stack, conventions, etc.)

- **Out of scope**:
  - Actual project artifacts
  - Kit packages

- **Requirements Covered**:
  - [x] `p1` - `cpt-cypilot-fr-adapter-config`
  - [x] `p2` - `cpt-cypilot-fr-hierarchical-registry`
  - [x] `p2` - `cpt-cypilot-fr-brownfield-support`

- **Design Principles Covered**:
  - [x] `p1` - `cpt-cypilot-principle-tech-agnostic`
  - [x] `p1` - `cpt-cypilot-principle-adapter-variability-boundary`

- **Design Constraints Covered**:
  - [x] `p1` - `cpt-cypilot-constraint-git`

- **Domain Model Entities**:
  - Adapter
  - ArtifactRegistry
  - System

- **Design Components**:
  - [x] `p1` - `cpt-cypilot-component-adapter-system`

- **API**:
  - `cypilot adapter-info`
  - `cypilot init`

- **Sequences**:
  - [x] `p1` - `cpt-cypilot-seq-adapter-discovery`

- **Data**:
  - [x] `p3` - `cpt-cypilot-dbtable-na`


### 3. [Kit Packages](features/rules-packages.md) ✅ HIGH

- [x] `p1` - **ID**: `cpt-cypilot-feature-rules-packages`

- **Purpose**: Provide templates, checklists, rules, and examples for each artifact kind with validation and self-check capabilities.

- **Depends On**: `cpt-cypilot-feature-methodology-core`

- **Scope**:
  - Template definitions (`template.md` per kind)
  - Semantic checklists (`checklist.md` per kind)
  - Generation rules (`rules.md` per kind)
  - Canonical examples (`kits/sdlc/artifacts/{KIND}/examples/example.md`)
  - Kit validation (`validate-kits`)
  - Template QA (`self-check`)

- **Out of scope**:
  - Custom project rules
  - Code generation rules

- **Requirements Covered**:
  - [x] `p1` - `cpt-cypilot-fr-rules-packages`
  - [x] `p2` - `cpt-cypilot-fr-template-qa`
  - [x] `p1` - `cpt-cypilot-fr-artifact-templates`

- **Design Principles Covered**:
  - [x] `p1` - `cpt-cypilot-principle-machine-readable`
  - [x] `p1` - `cpt-cypilot-principle-deterministic-gate`

- **Design Constraints Covered**:
  - [x] `p1` - `cpt-cypilot-constraint-markdown`

- **Domain Model Entities**:
  - Template
  - Checklist
  - Rules

- **Design Components**:
  - [x] `p1` - `cpt-cypilot-component-rules-packages`

- **API**:
  - `cypilot validate-kits`
  - `cypilot self-check`

- **Sequences**:
  - [x] `p1` - `cpt-cypilot-seq-validate-overall-design`

- **Data**:
  - [x] `p3` - `cpt-cypilot-dbtable-na`


### 4. [Cypilot CLI Tool](features/cypilot-cli.md) ✅ HIGH

- [x] `p1` - **ID**: `cpt-cypilot-feature-cypilot-cli`

- **Purpose**: Provide deterministic validation, ID management, and traceability commands via a Python stdlib-only CLI tool.

- **Depends On**: `cpt-cypilot-feature-adapter-system`, `cpt-cypilot-feature-rules-packages`

- **Scope**:
  - Artifact validation (`validate --artifact`)
  - Code validation (`validate-code`)
  - Cross-artifact validation
  - ID management (`list-ids`, `where-defined`, `where-used`)
  - JSON output for machine consumption

- **Out of scope**:
  - IDE-specific integrations
  - Interactive workflows

- **Requirements Covered**:
  - [x] `p1` - `cpt-cypilot-fr-validation`
  - [x] `p1` - `cpt-cypilot-fr-traceability`
  - [x] `p1` - `cpt-cypilot-fr-cross-artifact-validation`

- **Design Principles Covered**:
  - [x] `p1` - `cpt-cypilot-principle-deterministic-gate`
  - [x] `p1` - `cpt-cypilot-principle-traceability`
  - [x] `p1` - `cpt-cypilot-principle-cli-json-composability`

- **Design Constraints Covered**:
  - [x] `p1` - `cpt-cypilot-constraint-stdlib-only`
  - [x] `p1` - `cpt-cypilot-constraint-no-forced-tools`

- **Domain Model Entities**:
  - ValidationResult
  - CypilotId
  - CrossReference

- **Design Components**:
  - [x] `p1` - `cpt-cypilot-component-cypilot-skill`

- **API**:
  - `cypilot validate`
  - `cypilot list-ids`
  - `cypilot where-defined`
  - `cypilot where-used`

- **Sequences**:
  - [x] `p1` - `cpt-cypilot-seq-validate-overall-design`
  - [x] `p1` - `cpt-cypilot-seq-traceability-query`

- **Data**:
  - [x] `p3` - `cpt-cypilot-dbtable-na`


### 5. [Workflow Engine](features/workflow-engine.md) ✅ HIGH

- [x] `p1` - **ID**: `cpt-cypilot-feature-workflow-engine`

- **Purpose**: Provide interactive artifact creation/update workflows and validation workflows with execution protocol.

- **Depends On**: `cpt-cypilot-feature-cypilot-cli`, `cpt-cypilot-feature-rules-packages`

- **Scope**:
  - Generate workflow (`../workflows/generate.md`)
  - Validate workflow (`../workflows/analyze.md`)
  - Execution protocol
  - Artifact management (PRD, DESIGN, ADR, DECOMPOSITION, FEATURE)
  - Question-answer flow with proposals

- **Out of scope**:
  - Code generation
  - IDE integrations

- **Requirements Covered**:
  - [x] `p1` - `cpt-cypilot-fr-workflow-execution`
  - [x] `p1` - `cpt-cypilot-fr-design-first`
  - [x] `p1` - `cpt-cypilot-fr-prd-mgmt`
  - [x] `p1` - `cpt-cypilot-fr-overall-design-mgmt`
  - [x] `p1` - `cpt-cypilot-fr-spec-design-mgmt`

- **Design Principles Covered**:
  - [x] `p1` - `cpt-cypilot-principle-design-first`
  - [x] `p1` - `cpt-cypilot-principle-deterministic-gate`

- **Design Constraints Covered**:
  - [x] `p1` - `cpt-cypilot-constraint-git`
  - [x] `p1` - `cpt-cypilot-constraint-markdown`

- **Domain Model Entities**:
  - Workflow
  - ExecutionProtocol
  - WorkflowPhase

- **Design Components**:
  - [x] `p1` - `cpt-cypilot-component-workflows`

- **API**:
  - `/cypilot`
  - `/cypilot-generate`
  - `/cypilot-analyze`

- **Sequences**:
  - [x] `p1` - `cpt-cypilot-seq-intent-to-workflow`

- **Data**:
  - [x] `p3` - `cpt-cypilot-dbtable-na`


### 6. [Agent Compliance](features/agent-compliance.md) ✅ MEDIUM

- [x] `p2` - **ID**: `cpt-cypilot-feature-agent-compliance`

- **Purpose**: Enforce workflow quality through anti-pattern detection, evidence requirements, and STRICT/RELAXED mode.

- **Depends On**: `cpt-cypilot-feature-workflow-engine`

- **Scope**:
  - Anti-patterns documentation (8 patterns)
  - Evidence requirements for validation
  - STRICT vs RELAXED mode
  - Agent self-test protocol (6 questions)
  - Agent compliance protocol

- **Out of scope**:
  - Specific AI agent implementations
  - Automated enforcement

- **Requirements Covered**:
  - [x] `p2` - `cpt-cypilot-fr-multi-agent-integration`
  - [x] `p1` - `cpt-cypilot-nfr-security-integrity`
  - [x] `p1` - `cpt-cypilot-nfr-reliability-recoverability`

- **Design Principles Covered**:
  - [x] `p1` - `cpt-cypilot-principle-deterministic-gate`
  - [x] `p1` - `cpt-cypilot-principle-traceability`

- **Design Constraints Covered**:
  - [x] `p1` - `cpt-cypilot-constraint-no-forced-tools`

- **Domain Model Entities**:
  - AntiPattern
  - EvidenceRequirement
  - RulesMode

- **Design Components**:
  - [x] `p1` - `cpt-cypilot-component-agent`

- **API**:
  - `cypilot agent-workflows`
  - `cypilot agent-skills`

- **Sequences**:
  - [x] `p1` - `cpt-cypilot-seq-intent-to-workflow`

- **Data**:
  - [x] `p3` - `cpt-cypilot-dbtable-na`


### 7. [Template System](features/template-system.md) ✅ HIGH

- [x] `p1` - **ID**: `cpt-cypilot-feature-template-system`

- **Purpose**: Provide deterministic artifact parsing and validation engine for ID extraction and cross-artifact consistency.

- **Depends On**: `cpt-cypilot-feature-methodology-core`

- **Scope**:
  - Artifact parsing and validation
  - ID extraction and validation
  - Cross-artifact reference validation
  - Block content type validation (paragraph, list, table, cdsl, etc.)

- **Out of scope**:
  - Semantic validation (handled by checklists)
  - Code traceability (handled by codebase module)

- **Requirements Covered**:
  - [x] `p1` - `cpt-cypilot-fr-artifact-templates`
  - [x] `p1` - `cpt-cypilot-fr-validation`
  - [x] `p1` - `cpt-cypilot-fr-cross-artifact-validation`
  - [x] `p2` - `cpt-cypilot-fr-template-qa`

- **Design Principles Covered**:
  - [x] `p1` - `cpt-cypilot-principle-machine-readable`
  - [x] `p1` - `cpt-cypilot-principle-deterministic-gate`
  - [x] `p1` - `cpt-cypilot-principle-machine-readable-artifacts`

- **Design Constraints Covered**:
  - [x] `p1` - `cpt-cypilot-constraint-markdown`
  - [x] `p1` - `cpt-cypilot-constraint-stdlib-only`

- **Domain Model Entities**:
  - Template
  - TemplateBlock
  - Artifact
  - ArtifactBlock
  - IdDefinition
  - IdReference

- **Design Components**:
  - [x] `p1` - `cpt-cypilot-component-cypilot-skill`

- **API**:
  - `Template.from_path(path)`
  - `Template.validate(artifact_path)`
  - `Artifact.validate()`
  - `cross_validate_artifacts()`

- **Sequences**:
  - [x] `p1` - `cpt-cypilot-seq-validate-overall-design`
  - [x] `p1` - `cpt-cypilot-seq-traceability-query`

- **Data**:
  - [x] `p3` - `cpt-cypilot-dbtable-na`


## 3. Feature Dependencies

None.


