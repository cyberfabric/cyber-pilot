<!-- fdd:#:adr -->
# ADR-0001: Initial FDD Architecture

<!-- fdd:id:adr has="priority,task" covered_by="DESIGN" -->
- [x] `p1` - **ID**: `fdd-fdd-adr-initial-architecture-v1`

<!-- fdd:##:meta -->
## Meta

<!-- fdd:paragraph:adr-title -->
**Title**: ADR-0001 Initial FDD Architecture
<!-- fdd:paragraph:adr-title -->

<!-- fdd:paragraph:date -->
**Date**: 2025-01-17
<!-- fdd:paragraph:date -->

<!-- fdd:paragraph:status -->
**Status**: Accepted
<!-- fdd:paragraph:status -->
<!-- fdd:##:meta -->

<!-- fdd:##:body -->
## Body

<!-- fdd:context -->
**Context**:
FDD (Feature-Driven Design) is a universal methodology framework for building software systems with complete traceability from product requirements to implementation. The methodology must be technology-agnostic to support any tech stack, while providing structured workflows that can be executed by both human teams and AI coding assistants.

The architecture must enable incremental adoption, support design-first development, and maintain design-code coherence through systematic traceability.

Key requirements driving this decision:
* Support any programming language, framework, or technology stack
* Enable AI agents to execute workflows autonomously with minimal human intervention
* Provide deterministic validation to fail fast on structural issues
* Maintain complete traceability from product requirements through design to implementation
* Support incremental methodology adoption without disrupting existing projects
<!-- fdd:context -->

<!-- fdd:decision-drivers -->
**Decision Drivers**:
1. **Technology Agnostic Core** (from `fdd-fdd-principle-tech-agnostic`)
   - Methodology must work equally well for Python, Rust, JavaScript, Java, Go, or any language
   - No forced technology choices in core; all tech decisions in project adapters
   - Domain model formats and API contract formats must be configurable

2. **Design Before Code** (from `fdd-fdd-principle-design-first`)
   - All artifacts must be validated before implementation proceeds
   - Design is single source of truth; code follows design specifications
   - Validation gates prevent proceeding without passing quality thresholds

3. **Machine-Readable Specifications** (from `fdd-fdd-principle-machine-readable`)
   - Enable automation and AI agent execution
   - Reduce manual validation effort through deterministic checking
   - Support code generation from validated designs

4. **Incremental Adoption** (from `fdd-fdd-fr-brownfield-support`)
   - Projects must adopt FDD progressively without disruption
   - Support legacy system integration with minimal refactoring
   - Adapter-first approach enables starting with lightweight configuration

5. **Complete Traceability** (from `fdd-fdd-fr-traceability`)
   - Every design element needs unique ID for tracking
   - Code tags must link implementation to specifications
   - Support impact analysis when designs change
<!-- fdd:decision-drivers -->

<!-- fdd:options repeat="many" -->
**Considered Options**:
* Monolithic framework with built-in tech stack
* Configuration-heavy framework
* Layered architecture with plugin-based adapter system (chosen)

### Option 1: Monolithic Framework with Built-in Tech Stack

**Description**: Single unified framework with opinionated technology choices (e.g., Python + Django + PostgreSQL)

**Pros**:
* Simpler initial implementation
* Tighter integration between components
* Fewer configuration options to document

**Cons**:
* Forces technology choices on projects
* Cannot support polyglot architectures
* Limited to ecosystems where chosen tech stack works
* Migration from existing projects requires tech stack change

**Rejected**: Violates technology-agnostic core principle

### Option 2: Configuration-Heavy Framework

**Description**: Highly configurable framework with all options in central config file (e.g., YAML/JSON)

**Pros**:
* Centralized configuration management
* Standard config format (YAML/JSON)
* Single file to understand project setup

**Cons**:
* Configuration explosion (100+ options for all tech stacks)
* Difficult for AI agents to navigate large config files
* No incremental adoption (need full config upfront)
* Hard to extend with project-specific conventions

**Rejected**: Too complex for incremental adoption, poor AI agent discoverability

### Option 3: Layered Architecture with Plugin-Based Adapter System (SELECTED)

**Description**: Core methodology layer (universal) + Adapter layer (project-specific) + Plugin components (workflows, validation, ID management)

**Architecture**:

```text
AI Integration Layer (AGENTS.md, Skills, Deterministic Gate)
       ↓
Workflow Layer (Operation + Validation workflows)
       ↓
Validation Layer (Deterministic validators, Scoring system)
       ↓
ID Management Layer (Generation, Scanning, Traceability)
       ↓
Adapter Layer (Tech stack, Domain model format, Conventions)
       ↓
Methodology Core (Requirements files, Workflow specs, Core AGENTS.md)
```

**Pros**:
* Technology-agnostic core with zero dependencies
* Incremental adoption (start with minimal adapter)
* AI agents navigate via AGENTS.md WHEN clauses
* Project-specific conventions in isolated adapter directory
* Core updates propagate without breaking adapters (Extends mechanism)
* Plugin architecture supports future extensibility

**Cons**:
* Requires adapter setup before usage (mitigated by bootstrap workflow)
* More files to understand than monolithic approach (mitigated by progressive disclosure)

**Selected**: Best fit for all decision drivers
<!-- fdd:options -->

<!-- fdd:decision-outcome -->
**Decision Outcome**:
Chosen option: "Layered architecture with plugin-based adapter system", because it best satisfies technology-agnosticism, incremental adoption, and deterministic validation/traceability while remaining navigable for AI agents.

FDD uses **Layered Architecture with Plugin-Based Adapter System** with the following structure:

**Core Components** (6 components):
1. **Methodology Core** - Universal specifications (requirements, workflows, AGENTS.md)
2. **Adapter System** - Project-specific customization (tech stack, domain model, conventions)
3. **Workflow Engine** - Operation workflows (CREATE/UPDATE) and validation workflows
4. **Validation Engine** - Deterministic validators with 100-point scoring system
5. **ID Management** - FDD ID generation, qualified IDs, repository-wide scanning
6. **AI Integration Layer** - WHEN clause navigation, skills system, deterministic gate pattern

**Design Principles** (5 principles):
1. **Technology Agnostic Core** - Zero tech dependencies in core, all choices in adapters
2. **Design Before Code** - Artifacts validated before implementation proceeds
3. **Machine-Readable Specifications** - Parseable formats for automation
4. **Progressive Validation** - Deterministic gate pattern (fail fast before manual review)
5. **Traceability By Design** - Unique IDs for all design elements, code tags for implementation

**Key Architectural Patterns**:
* **AGENTS.md Navigation**: WHEN clause rules determine which specs to follow based on workflow context
* **Extends Mechanism**: Adapter AGENTS.md extends core without duplication
* **Deterministic Gate**: Automated validators run before expensive manual review
* **Layered Validation**: Deterministic → Manual → Peer review (sequential)
* **Incremental Adoption**: Adapter → PRD → Design → Features → Implementation

**Technology Choices for FDD Implementation**:
* **Core Tooling**: Python 3.6+ standard library only (no external dependencies)
* **Artifacts**: Plain Markdown (universal compatibility, version control friendly)
* **API Interface**: CLISPEC (command-line interface, JSON output for machine consumption)
* **Domain Model Format**: Markdown-based artifact structure (not code-level types)
<!-- fdd:decision-outcome -->

**Consequences**:
<!-- fdd:list:consequences -->
- Positive: FDD works with any tech stack through adapter system
- Positive: Projects can adopt incrementally without disruption
- Positive: AI agents can execute workflows autonomously via AGENTS.md navigation
- Positive: Core updates don't break project adapters (Extends mechanism)
- Positive: Deterministic validation catches structural issues immediately
- Positive: Complete traceability through FDD IDs and code tags
- Negative: Requires adapter setup before first use (addressed by bootstrap workflow)
- Negative: Multiple files to understand (addressed by progressive disclosure)
- Negative: Learning curve for WHEN clause pattern (addressed by concrete examples)
- Follow-up: None (initial decision)
<!-- fdd:list:consequences -->

**Links**:
<!-- fdd:list:links -->
- Related Actors: `fdd-fdd-actor-architect`, `fdd-fdd-actor-technical-lead`, `fdd-fdd-actor-ai-assistant`, `fdd-fdd-actor-developer`
- Related Capabilities: `fdd-fdd-fr-workflow-execution`, `fdd-fdd-fr-validation`, `fdd-fdd-fr-adapter-config`, `fdd-fdd-fr-design-first`, `fdd-fdd-fr-traceability`, `fdd-fdd-fr-brownfield-support`
- Related Principles: `fdd-fdd-principle-tech-agnostic`, `fdd-fdd-principle-design-first`, `fdd-fdd-principle-machine-readable`, `fdd-fdd-principle-deterministic-gate`, `fdd-fdd-principle-traceability`
- Supersedes: None (initial decision)
- Superseded by: None (current)
- Related ADRs: None yet (this is ADR-0001)
<!-- fdd:list:links -->
<!-- fdd:##:body -->
<!-- fdd:id:adr -->

<!-- fdd:#:adr -->
