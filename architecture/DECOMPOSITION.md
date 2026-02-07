<!-- cpt:#:decomposition -->
# Decomposition: Cypilot

<!-- cpt:##:overview -->
## 1. Overview

Cypilot specs are organized around **architectural components** with explicit dependencies. Foundation specs (Methodology Core, Adapter System) enable higher-level specs (Kit Packages, CLI Tool, Workflows). The decomposition follows the component model from DESIGN.md, ensuring each spec maps to one or more components and covers related functional requirements.

<!-- cpt:##:overview -->

<!-- cpt:##:entries -->
## 2. Entries

**Overall implementation status:**
<!-- cpt:id:status has="priority,task" -->
- [x] `p1` - **ID**: `cpt-cypilot-status-overall`

<!-- cpt:###:spec-title repeat="many" -->
### 1. [Methodology Core](spec-methodology-core/) ✅ HIGH

<!-- cpt:id:spec has="priority,task" -->
- [x] `p1` - **ID**: `cpt-cypilot-spec-methodology-core`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: Provide universal Cypilot specifications including requirements, CDSL language, and base template syntax that all projects share.
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: None
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - Requirements specifications (`requirements/*.md`)
  - CDSL (Cypilot Description Language) specification
  - Template marker syntax specification
  - Execution protocol definition
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - Project-specific customization
  - Concrete templates for artifact kinds
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-fr-artifact-templates`
  - [x] `p2` - `cpt-cypilot-fr-artifact-examples`
  - [x] `p1` - `cpt-cypilot-fr-cdsl`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-principle-tech-agnostic`
  - [x] `p1` - `cpt-cypilot-principle-machine-readable`
  - [x] `p1` - `cpt-cypilot-principle-machine-readable-artifacts`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-constraint-markdown`
  - [x] `p1` - `cpt-cypilot-constraint-no-forced-tools`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - Artifact
  - Workflow
  - CDSL
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-component-methodology-core`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - Specifications only, no CLI commands
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-seq-intent-to-workflow`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [x] `p3` - `cpt-cypilot-dbtable-na`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:###:spec-title repeat="many" -->
### 2. [Adapter System](spec-adapter-system/) ✅ HIGH

<!-- cpt:id:spec has="priority,task" -->
- [x] `p1` - **ID**: `cpt-cypilot-spec-adapter-system`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: Enable project-specific customization without modifying core methodology through adapter configuration and hierarchical artifact registry.
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: None
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - Adapter discovery (`adapter-info` command)
  - `artifacts.json` registry with hierarchical systems
  - `.cypilot-adapter/` directory structure
  - Spec files (tech-stack, conventions, etc.)
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - Actual project artifacts
  - Kit packages
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-fr-adapter-config`
  - [x] `p2` - `cpt-cypilot-fr-hierarchical-registry`
  - [x] `p2` - `cpt-cypilot-fr-brownfield-support`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-principle-tech-agnostic`
  - [x] `p1` - `cpt-cypilot-principle-adapter-variability-boundary`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-constraint-git`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - Adapter
  - ArtifactRegistry
  - System
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-component-adapter-system`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - `cypilot adapter-info`
  - `cypilot init`
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-seq-adapter-discovery`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [x] `p3` - `cpt-cypilot-dbtable-na`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:###:spec-title repeat="many" -->
### 3. [Kit Packages](spec-rules-packages/) ✅ HIGH

<!-- cpt:id:spec has="priority,task" -->
- [x] `p1` - **ID**: `cpt-cypilot-spec-rules-packages`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: Provide templates, checklists, rules, and examples for each artifact kind with validation and self-check capabilities.
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: `cpt-cypilot-spec-methodology-core`
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - Template definitions (`template.md` per kind)
  - Semantic checklists (`checklist.md` per kind)
  - Generation rules (`rules.md` per kind)
  - Canonical examples (`kits/sdlc/artifacts/{KIND}/examples/example.md`)
  - Kit validation (`validate-kits`)
  - Template QA (`self-check`)
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - Custom project rules
  - Code generation rules
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-fr-rules-packages`
  - [x] `p2` - `cpt-cypilot-fr-template-qa`
  - [x] `p1` - `cpt-cypilot-fr-artifact-templates`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-principle-machine-readable`
  - [x] `p1` - `cpt-cypilot-principle-deterministic-gate`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-constraint-markdown`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - Template
  - Checklist
  - Rules
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-component-rules-packages`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - `cypilot validate-kits`
  - `cypilot self-check`
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-seq-validate-overall-design`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [x] `p3` - `cpt-cypilot-dbtable-na`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:###:spec-title repeat="many" -->
### 4. [Cypilot CLI Tool](spec-cypilot-cli/) ✅ HIGH

<!-- cpt:id:spec has="priority,task" -->
- [x] `p1` - **ID**: `cpt-cypilot-spec-cypilot-cli`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: Provide deterministic validation, ID management, and traceability commands via a Python stdlib-only CLI tool.
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: `cpt-cypilot-spec-adapter-system`, `cpt-cypilot-spec-rules-packages`
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - Artifact validation (`validate --artifact`)
  - Code validation (`validate-code`)
  - Cross-artifact validation
  - ID management (`list-ids`, `where-defined`, `where-used`)
  - JSON output for machine consumption
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - IDE-specific integrations
  - Interactive workflows
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-fr-validation`
  - [x] `p1` - `cpt-cypilot-fr-traceability`
  - [x] `p1` - `cpt-cypilot-fr-cross-artifact-validation`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-principle-deterministic-gate`
  - [x] `p1` - `cpt-cypilot-principle-traceability`
  - [x] `p1` - `cpt-cypilot-principle-cli-json-composability`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-constraint-stdlib-only`
  - [x] `p1` - `cpt-cypilot-constraint-no-forced-tools`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - ValidationResult
  - CypilotId
  - CrossReference
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-component-cypilot-skill`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - `cypilot validate`
  - `cypilot list-ids`
  - `cypilot where-defined`
  - `cypilot where-used`
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-seq-validate-overall-design`
  - [x] `p1` - `cpt-cypilot-seq-traceability-query`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [x] `p3` - `cpt-cypilot-dbtable-na`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:###:spec-title repeat="many" -->
### 5. [Workflow Engine](spec-workflow-engine/) ✅ HIGH

<!-- cpt:id:spec has="priority,task" -->
- [x] `p1` - **ID**: `cpt-cypilot-spec-workflow-engine`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: Provide interactive artifact creation/update workflows and validation workflows with execution protocol.
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: `cpt-cypilot-spec-cypilot-cli`, `cpt-cypilot-spec-rules-packages`
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - Generate workflow (`../workflows/generate.md`)
  - Validate workflow (`../workflows/analyze.md`)
  - Execution protocol
  - Artifact management (PRD, DESIGN, ADR, DECOMPOSITION, SPEC)
  - Question-answer flow with proposals
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - Code generation
  - IDE integrations
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-fr-workflow-execution`
  - [x] `p1` - `cpt-cypilot-fr-design-first`
  - [x] `p1` - `cpt-cypilot-fr-prd-mgmt`
  - [x] `p1` - `cpt-cypilot-fr-overall-design-mgmt`
  - [x] `p1` - `cpt-cypilot-fr-spec-design-mgmt`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-principle-design-first`
  - [x] `p1` - `cpt-cypilot-principle-deterministic-gate`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-constraint-git`
  - [x] `p1` - `cpt-cypilot-constraint-markdown`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - Workflow
  - ExecutionProtocol
  - WorkflowPhase
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-component-workflows`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - `/cypilot`
  - `/cypilot-generate`
  - `/cypilot-analyze`
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-seq-intent-to-workflow`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [x] `p3` - `cpt-cypilot-dbtable-na`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:###:spec-title repeat="many" -->
### 6. [Agent Compliance](spec-agent-compliance/) ✅ MEDIUM

<!-- cpt:id:spec has="priority,task" -->
- [x] `p2` - **ID**: `cpt-cypilot-spec-agent-compliance`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: Enforce workflow quality through anti-pattern detection, evidence requirements, and STRICT/RELAXED mode.
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: `cpt-cypilot-spec-workflow-engine`
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - Anti-patterns documentation (8 patterns)
  - Evidence requirements for validation
  - STRICT vs RELAXED mode
  - Agent self-test protocol (6 questions)
  - Agent compliance protocol
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - Specific AI agent implementations
  - Automated enforcement
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [x] `p2` - `cpt-cypilot-fr-multi-agent-integration`
  - [x] `p1` - `cpt-cypilot-nfr-security-integrity`
  - [x] `p1` - `cpt-cypilot-nfr-reliability-recoverability`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-principle-deterministic-gate`
  - [x] `p1` - `cpt-cypilot-principle-traceability`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-constraint-no-forced-tools`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - AntiPattern
  - EvidenceRequirement
  - RulesMode
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-component-agent`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - `cypilot agent-workflows`
  - `cypilot agent-skills`
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [x] `p1` - `cpt-cypilot-seq-intent-to-workflow`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [x] `p3` - `cpt-cypilot-dbtable-na`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:###:spec-title repeat="many" -->
### 7. [Template System](specs/template-system.md) ✅ HIGH

<!-- cpt:id:spec has="priority,task" -->
- [x] `p1` - **ID**: `cpt-cypilot-spec-template-system`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: Provide marker-based template parsing and validation engine for deterministic artifact structure validation.
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: `cpt-cypilot-spec-methodology-core`
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - Template parsing with Cypilot markers (cpt:type:name format)
  - Artifact validation against templates
  - ID extraction and validation
  - Cross-artifact reference validation
  - Block content type validation (paragraph, list, table, cdsl, etc.)
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - Semantic validation (handled by checklists)
  - Code traceability (handled by codebase module)
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [ ] `p1` - `cpt-cypilot-fr-artifact-templates`
  - [ ] `p1` - `cpt-cypilot-fr-validation`
  - [ ] `p1` - `cpt-cypilot-fr-cross-artifact-validation`
  - [ ] `p2` - `cpt-cypilot-fr-template-qa`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [ ] `p1` - `cpt-cypilot-principle-machine-readable`
  - [ ] `p1` - `cpt-cypilot-principle-deterministic-gate`
  - [ ] `p1` - `cpt-cypilot-principle-machine-readable-artifacts`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [ ] `p1` - `cpt-cypilot-constraint-markdown`
  - [ ] `p1` - `cpt-cypilot-constraint-stdlib-only`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - Template
  - TemplateBlock
  - Artifact
  - ArtifactBlock
  - IdDefinition
  - IdReference
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [ ] `p1` - `cpt-cypilot-component-cypilot-skill`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - `Template.from_path(path)`
  - `Template.validate(artifact_path)`
  - `Artifact.validate()`
  - `cross_validate_artifacts()`
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [ ] `p1` - `cpt-cypilot-seq-validate-overall-design`
  - [ ] `p1` - `cpt-cypilot-seq-traceability-query`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [ ] `p3` - `cpt-cypilot-dbtable-na`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:id:status -->
<!-- cpt:##:entries -->
<!-- cpt:#:decomposition -->
