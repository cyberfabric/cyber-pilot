<!-- fdd:#:features -->
# Features: FDD

<!-- fdd:##:overview -->
## 1. Overview

FDD features are organized around **architectural components** with explicit dependencies. Foundation features (Methodology Core, Adapter System) enable higher-level features (Rules Packages, CLI Tool, Workflows). The decomposition follows the component model from DESIGN.md, ensuring each feature maps to one or more components and covers related functional requirements.

<!-- fdd:##:overview -->

<!-- fdd:##:entries -->
## 2. Entries

**Overall implementation status:**
<!-- fdd:id:status has="priority,task" -->
- [x] `p1` - **ID**: `fdd-fdd-status-overall`

<!-- fdd:###:feature-title repeat="many" -->
### 1. [Methodology Core](feature-methodology-core/) ✅ HIGH

<!-- fdd:id:feature has="priority,task" -->
- [x] `p1` - **ID**: `fdd-fdd-feature-methodology-core`

<!-- fdd:paragraph:feature-purpose required="true" -->
- **Purpose**: Provide universal FDD specifications including requirements, FDL language, and base template syntax that all projects share.
<!-- fdd:paragraph:feature-purpose -->

<!-- fdd:paragraph:feature-depends -->
- **Depends On**: None
<!-- fdd:paragraph:feature-depends -->

<!-- fdd:list:feature-scope -->
- **Scope**:
  - Requirements specifications (`requirements/*.md`)
  - FDL (FDD Description Language) specification
  - Template marker syntax specification
  - Execution protocol definition
<!-- fdd:list:feature-scope -->

<!-- fdd:list:feature-out-scope -->
- **Out of scope**:
  - Project-specific customization
  - Concrete templates for artifact kinds
<!-- fdd:list:feature-out-scope -->

- **Requirements Covered**:
<!-- fdd:id-ref:fr has="priority,task" -->
  - [x] `p1` - `fdd-fdd-fr-artifact-templates`
  - [x] `p2` - `fdd-fdd-fr-artifact-examples`
  - [x] `p1` - `fdd-fdd-fr-fdl`
<!-- fdd:id-ref:fr -->

- **Design Principles Covered**:
<!-- fdd:id-ref:principle has="priority,task" -->
  - [x] `p1` - `fdd-fdd-principle-tech-agnostic`
  - [x] `p1` - `fdd-fdd-principle-machine-readable`
  - [x] `p1` - `fdd-fdd-principle-machine-readable-artifacts`
<!-- fdd:id-ref:principle -->

- **Design Constraints Covered**:
<!-- fdd:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `fdd-fdd-constraint-markdown`
  - [x] `p1` - `fdd-fdd-constraint-no-forced-tools`
<!-- fdd:id-ref:constraint -->

<!-- fdd:list:feature-domain-entities -->
- **Domain Model Entities**:
  - Artifact
  - Workflow
  - FDL
<!-- fdd:list:feature-domain-entities -->

- **Design Components**:
<!-- fdd:id-ref:component has="priority,task" -->
  - [x] `p1` - `fdd-fdd-component-methodology-core`
<!-- fdd:id-ref:component -->

<!-- fdd:list:feature-api -->
- **API**:
  - Specifications only, no CLI commands
<!-- fdd:list:feature-api -->

- **Sequences**:
<!-- fdd:id-ref:seq has="priority,task" -->
  - [x] `p1` - `fdd-fdd-seq-intent-to-workflow`
<!-- fdd:id-ref:seq -->

- **Data**:
<!-- fdd:id-ref:dbtable has="priority,task" -->
  - [x] `p3` - `fdd-fdd-dbtable-na`
<!-- fdd:id-ref:dbtable -->

<!-- fdd:id:feature -->
<!-- fdd:###:feature-title repeat="many" -->

<!-- fdd:###:feature-title repeat="many" -->
### 2. [Adapter System](feature-adapter-system/) ✅ HIGH

<!-- fdd:id:feature has="priority,task" -->
- [x] `p1` - **ID**: `fdd-fdd-feature-adapter-system`

<!-- fdd:paragraph:feature-purpose required="true" -->
- **Purpose**: Enable project-specific customization without modifying core methodology through adapter configuration and hierarchical artifact registry.
<!-- fdd:paragraph:feature-purpose -->

<!-- fdd:paragraph:feature-depends -->
- **Depends On**: None
<!-- fdd:paragraph:feature-depends -->

<!-- fdd:list:feature-scope -->
- **Scope**:
  - Adapter discovery (`adapter-info` command)
  - `artifacts.json` registry with hierarchical systems
  - `.adapter/` directory structure
  - Spec files (tech-stack, conventions, etc.)
<!-- fdd:list:feature-scope -->

<!-- fdd:list:feature-out-scope -->
- **Out of scope**:
  - Actual project artifacts
  - Rules packages
<!-- fdd:list:feature-out-scope -->

- **Requirements Covered**:
<!-- fdd:id-ref:fr has="priority,task" -->
  - [x] `p1` - `fdd-fdd-fr-adapter-config`
  - [x] `p2` - `fdd-fdd-fr-hierarchical-registry`
  - [x] `p2` - `fdd-fdd-fr-brownfield-support`
<!-- fdd:id-ref:fr -->

- **Design Principles Covered**:
<!-- fdd:id-ref:principle has="priority,task" -->
  - [x] `p1` - `fdd-fdd-principle-tech-agnostic`
  - [x] `p1` - `fdd-fdd-principle-adapter-variability-boundary`
<!-- fdd:id-ref:principle -->

- **Design Constraints Covered**:
<!-- fdd:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `fdd-fdd-constraint-git`
<!-- fdd:id-ref:constraint -->

<!-- fdd:list:feature-domain-entities -->
- **Domain Model Entities**:
  - Adapter
  - ArtifactRegistry
  - System
<!-- fdd:list:feature-domain-entities -->

- **Design Components**:
<!-- fdd:id-ref:component has="priority,task" -->
  - [x] `p1` - `fdd-fdd-component-adapter-system`
<!-- fdd:id-ref:component -->

<!-- fdd:list:feature-api -->
- **API**:
  - `fdd adapter-info`
  - `fdd init`
<!-- fdd:list:feature-api -->

- **Sequences**:
<!-- fdd:id-ref:seq has="priority,task" -->
  - [x] `p1` - `fdd-fdd-seq-adapter-discovery`
<!-- fdd:id-ref:seq -->

- **Data**:
<!-- fdd:id-ref:dbtable has="priority,task" -->
  - [x] `p3` - `fdd-fdd-dbtable-na`
<!-- fdd:id-ref:dbtable -->

<!-- fdd:id:feature -->
<!-- fdd:###:feature-title repeat="many" -->

<!-- fdd:###:feature-title repeat="many" -->
### 3. [Rules Packages](feature-rules-packages/) ✅ HIGH

<!-- fdd:id:feature has="priority,task" -->
- [x] `p1` - **ID**: `fdd-fdd-feature-rules-packages`

<!-- fdd:paragraph:feature-purpose required="true" -->
- **Purpose**: Provide templates, checklists, rules, and examples for each artifact kind with validation and self-check capabilities.
<!-- fdd:paragraph:feature-purpose -->

<!-- fdd:paragraph:feature-depends -->
- **Depends On**: `fdd-fdd-feature-methodology-core`
<!-- fdd:paragraph:feature-depends -->

<!-- fdd:list:feature-scope -->
- **Scope**:
  - Template definitions (`template.md` per kind)
  - Semantic checklists (`checklist.md` per kind)
  - Generation rules (`rules.md` per kind)
  - Canonical examples (`examples/example.md`)
  - Rules validation (`validate-rules`)
  - Template QA (`self-check`)
<!-- fdd:list:feature-scope -->

<!-- fdd:list:feature-out-scope -->
- **Out of scope**:
  - Custom project rules
  - Code generation rules
<!-- fdd:list:feature-out-scope -->

- **Requirements Covered**:
<!-- fdd:id-ref:fr has="priority,task" -->
  - [x] `p1` - `fdd-fdd-fr-rules-packages`
  - [x] `p2` - `fdd-fdd-fr-template-qa`
  - [x] `p1` - `fdd-fdd-fr-artifact-templates`
<!-- fdd:id-ref:fr -->

- **Design Principles Covered**:
<!-- fdd:id-ref:principle has="priority,task" -->
  - [x] `p1` - `fdd-fdd-principle-machine-readable`
  - [x] `p1` - `fdd-fdd-principle-deterministic-gate`
<!-- fdd:id-ref:principle -->

- **Design Constraints Covered**:
<!-- fdd:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `fdd-fdd-constraint-markdown`
<!-- fdd:id-ref:constraint -->

<!-- fdd:list:feature-domain-entities -->
- **Domain Model Entities**:
  - Template
  - Checklist
  - Rules
<!-- fdd:list:feature-domain-entities -->

- **Design Components**:
<!-- fdd:id-ref:component has="priority,task" -->
  - [x] `p1` - `fdd-fdd-component-rules-packages`
<!-- fdd:id-ref:component -->

<!-- fdd:list:feature-api -->
- **API**:
  - `fdd validate-rules`
  - `fdd self-check`
<!-- fdd:list:feature-api -->

- **Sequences**:
<!-- fdd:id-ref:seq has="priority,task" -->
  - [x] `p1` - `fdd-fdd-seq-validate-overall-design`
<!-- fdd:id-ref:seq -->

- **Data**:
<!-- fdd:id-ref:dbtable has="priority,task" -->
  - [x] `p3` - `fdd-fdd-dbtable-na`
<!-- fdd:id-ref:dbtable -->

<!-- fdd:id:feature -->
<!-- fdd:###:feature-title repeat="many" -->

<!-- fdd:###:feature-title repeat="many" -->
### 4. [FDD CLI Tool](feature-fdd-cli/) ✅ HIGH

<!-- fdd:id:feature has="priority,task" -->
- [x] `p1` - **ID**: `fdd-fdd-feature-fdd-cli`

<!-- fdd:paragraph:feature-purpose required="true" -->
- **Purpose**: Provide deterministic validation, ID management, and traceability commands via a Python stdlib-only CLI tool.
<!-- fdd:paragraph:feature-purpose -->

<!-- fdd:paragraph:feature-depends -->
- **Depends On**: `fdd-fdd-feature-adapter-system`, `fdd-fdd-feature-rules-packages`
<!-- fdd:paragraph:feature-depends -->

<!-- fdd:list:feature-scope -->
- **Scope**:
  - Artifact validation (`validate --artifact`)
  - Code validation (`validate-code`)
  - Cross-artifact validation
  - ID management (`list-ids`, `where-defined`, `where-used`)
  - JSON output for machine consumption
<!-- fdd:list:feature-scope -->

<!-- fdd:list:feature-out-scope -->
- **Out of scope**:
  - IDE-specific integrations
  - Interactive workflows
<!-- fdd:list:feature-out-scope -->

- **Requirements Covered**:
<!-- fdd:id-ref:fr has="priority,task" -->
  - [x] `p1` - `fdd-fdd-fr-validation`
  - [x] `p1` - `fdd-fdd-fr-traceability`
  - [x] `p1` - `fdd-fdd-fr-cross-artifact-validation`
<!-- fdd:id-ref:fr -->

- **Design Principles Covered**:
<!-- fdd:id-ref:principle has="priority,task" -->
  - [x] `p1` - `fdd-fdd-principle-deterministic-gate`
  - [x] `p1` - `fdd-fdd-principle-traceability`
  - [x] `p1` - `fdd-fdd-principle-cli-json-composability`
<!-- fdd:id-ref:principle -->

- **Design Constraints Covered**:
<!-- fdd:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `fdd-fdd-constraint-stdlib-only`
  - [x] `p1` - `fdd-fdd-constraint-no-forced-tools`
<!-- fdd:id-ref:constraint -->

<!-- fdd:list:feature-domain-entities -->
- **Domain Model Entities**:
  - ValidationResult
  - FddId
  - CrossReference
<!-- fdd:list:feature-domain-entities -->

- **Design Components**:
<!-- fdd:id-ref:component has="priority,task" -->
  - [x] `p1` - `fdd-fdd-component-fdd-skill`
<!-- fdd:id-ref:component -->

<!-- fdd:list:feature-api -->
- **API**:
  - `fdd validate`
  - `fdd list-ids`
  - `fdd where-defined`
  - `fdd where-used`
<!-- fdd:list:feature-api -->

- **Sequences**:
<!-- fdd:id-ref:seq has="priority,task" -->
  - [x] `p1` - `fdd-fdd-seq-validate-overall-design`
  - [x] `p1` - `fdd-fdd-seq-traceability-query`
<!-- fdd:id-ref:seq -->

- **Data**:
<!-- fdd:id-ref:dbtable has="priority,task" -->
  - [x] `p3` - `fdd-fdd-dbtable-na`
<!-- fdd:id-ref:dbtable -->

<!-- fdd:id:feature -->
<!-- fdd:###:feature-title repeat="many" -->

<!-- fdd:###:feature-title repeat="many" -->
### 5. [Workflow Engine](feature-workflow-engine/) ✅ HIGH

<!-- fdd:id:feature has="priority,task" -->
- [x] `p1` - **ID**: `fdd-fdd-feature-workflow-engine`

<!-- fdd:paragraph:feature-purpose required="true" -->
- **Purpose**: Provide interactive artifact creation/update workflows and validation workflows with execution protocol.
<!-- fdd:paragraph:feature-purpose -->

<!-- fdd:paragraph:feature-depends -->
- **Depends On**: `fdd-fdd-feature-fdd-cli`, `fdd-fdd-feature-rules-packages`
<!-- fdd:paragraph:feature-depends -->

<!-- fdd:list:feature-scope -->
- **Scope**:
  - Generate workflow (`workflows/generate.md`)
  - Validate workflow (`workflows/validate.md`)
  - Execution protocol
  - Artifact management (PRD, DESIGN, ADR, FEATURES, FEATURE)
  - Question-answer flow with proposals
<!-- fdd:list:feature-scope -->

<!-- fdd:list:feature-out-scope -->
- **Out of scope**:
  - Code generation
  - IDE integrations
<!-- fdd:list:feature-out-scope -->

- **Requirements Covered**:
<!-- fdd:id-ref:fr has="priority,task" -->
  - [x] `p1` - `fdd-fdd-fr-workflow-execution`
  - [x] `p1` - `fdd-fdd-fr-design-first`
  - [x] `p1` - `fdd-fdd-fr-prd-mgmt`
  - [x] `p1` - `fdd-fdd-fr-overall-design-mgmt`
  - [x] `p1` - `fdd-fdd-fr-feature-design-mgmt`
<!-- fdd:id-ref:fr -->

- **Design Principles Covered**:
<!-- fdd:id-ref:principle has="priority,task" -->
  - [x] `p1` - `fdd-fdd-principle-design-first`
  - [x] `p1` - `fdd-fdd-principle-deterministic-gate`
<!-- fdd:id-ref:principle -->

- **Design Constraints Covered**:
<!-- fdd:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `fdd-fdd-constraint-git`
  - [x] `p1` - `fdd-fdd-constraint-markdown`
<!-- fdd:id-ref:constraint -->

<!-- fdd:list:feature-domain-entities -->
- **Domain Model Entities**:
  - Workflow
  - ExecutionProtocol
  - WorkflowPhase
<!-- fdd:list:feature-domain-entities -->

- **Design Components**:
<!-- fdd:id-ref:component has="priority,task" -->
  - [x] `p1` - `fdd-fdd-component-workflows`
<!-- fdd:id-ref:component -->

<!-- fdd:list:feature-api -->
- **API**:
  - `/fdd`
  - `/fdd-generate`
  - `/fdd-validate`
<!-- fdd:list:feature-api -->

- **Sequences**:
<!-- fdd:id-ref:seq has="priority,task" -->
  - [x] `p1` - `fdd-fdd-seq-intent-to-workflow`
<!-- fdd:id-ref:seq -->

- **Data**:
<!-- fdd:id-ref:dbtable has="priority,task" -->
  - [x] `p3` - `fdd-fdd-dbtable-na`
<!-- fdd:id-ref:dbtable -->

<!-- fdd:id:feature -->
<!-- fdd:###:feature-title repeat="many" -->

<!-- fdd:###:feature-title repeat="many" -->
### 6. [Agent Compliance](feature-agent-compliance/) ✅ MEDIUM

<!-- fdd:id:feature has="priority,task" -->
- [x] `p2` - **ID**: `fdd-fdd-feature-agent-compliance`

<!-- fdd:paragraph:feature-purpose required="true" -->
- **Purpose**: Enforce workflow quality through anti-pattern detection, evidence requirements, and STRICT/RELAXED mode.
<!-- fdd:paragraph:feature-purpose -->

<!-- fdd:paragraph:feature-depends -->
- **Depends On**: `fdd-fdd-feature-workflow-engine`
<!-- fdd:paragraph:feature-depends -->

<!-- fdd:list:feature-scope -->
- **Scope**:
  - Anti-patterns documentation (8 patterns)
  - Evidence requirements for validation
  - STRICT vs RELAXED mode
  - Agent self-test protocol (6 questions)
  - Agent compliance protocol
<!-- fdd:list:feature-scope -->

<!-- fdd:list:feature-out-scope -->
- **Out of scope**:
  - Specific AI agent implementations
  - Automated enforcement
<!-- fdd:list:feature-out-scope -->

- **Requirements Covered**:
<!-- fdd:id-ref:fr has="priority,task" -->
  - [x] `p2` - `fdd-fdd-fr-multi-agent-integration`
  - [x] `p1` - `fdd-fdd-nfr-security-integrity`
  - [x] `p1` - `fdd-fdd-nfr-reliability-recoverability`
<!-- fdd:id-ref:fr -->

- **Design Principles Covered**:
<!-- fdd:id-ref:principle has="priority,task" -->
  - [x] `p1` - `fdd-fdd-principle-deterministic-gates`
  - [x] `p1` - `fdd-fdd-principle-traceability`
<!-- fdd:id-ref:principle -->

- **Design Constraints Covered**:
<!-- fdd:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `fdd-fdd-constraint-no-forced-tools`
<!-- fdd:id-ref:constraint -->

<!-- fdd:list:feature-domain-entities -->
- **Domain Model Entities**:
  - AntiPattern
  - EvidenceRequirement
  - RulesMode
<!-- fdd:list:feature-domain-entities -->

- **Design Components**:
<!-- fdd:id-ref:component has="priority,task" -->
  - [x] `p1` - `fdd-fdd-component-agent`
<!-- fdd:id-ref:component -->

<!-- fdd:list:feature-api -->
- **API**:
  - `fdd agent-workflows`
  - `fdd agent-skills`
<!-- fdd:list:feature-api -->

- **Sequences**:
<!-- fdd:id-ref:seq has="priority,task" -->
  - [x] `p1` - `fdd-fdd-seq-intent-to-workflow`
<!-- fdd:id-ref:seq -->

- **Data**:
<!-- fdd:id-ref:dbtable has="priority,task" -->
  - [x] `p3` - `fdd-fdd-dbtable-na`
<!-- fdd:id-ref:dbtable -->

<!-- fdd:id:feature -->
<!-- fdd:###:feature-title repeat="many" -->

<!-- fdd:id:status -->
<!-- fdd:##:entries -->
<!-- fdd:#:features -->
