# ADR-0001: Initial FDD Architecture

**Date**: 2025-01-17

**Status**: Accepted

**ADR ID**: `fdd-fdd-adr-initial-architecture-v1`

## Context and Problem Statement

FDD (Feature-Driven Design) is a universal methodology framework for building software systems with complete traceability from product requirements to implementation. The methodology must be technology-agnostic to support any tech stack, while providing structured workflows that can be executed by both human teams and AI coding assistants.

The architecture must enable incremental adoption, support design-first development, and maintain design-code coherence through systematic traceability.

Key requirements driving this decision:
* Support any programming language, framework, or technology stack
* Enable AI agents to execute workflows autonomously with minimal human intervention
* Provide deterministic validation to fail fast on structural issues
* Maintain complete traceability from product requirements through design to implementation
* Support incremental methodology adoption without disrupting existing projects

## Decision Drivers

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

4. **Incremental Adoption** (from `fdd-fdd-fr-brownfield-support`, `fdd-fdd-req-migration`)
   - Projects must adopt FDD progressively without disruption
   - Support legacy system integration with minimal refactoring
   - Adapter-first approach enables starting with lightweight configuration

5. **Complete Traceability** (from `fdd-fdd-fr-traceability`, `fdd-fdd-req-traceability`)
   - Every design element needs unique ID for tracking
   - Code tags must link implementation to specifications
   - Support impact analysis when designs change

## Considered Options

* Monolithic framework with built-in tech stack
* Configuration-heavy framework
* Layered architecture with plugin-based adapter system (chosen)

## Pros and Cons of the Options

### Option 1: Monolithic Framework with Built-in Tech Stack

**Description**: Single unified framework with opinionated technology choices (e.g., Python + Django + PostgreSQL)

**Pros**:
* Simpler initial implementation
* Tighter integration between components
* Fewer configuration options to document

**Cons**:
* ❌ Forces technology choices on projects
* ❌ Cannot support polyglot architectures
* ❌ Limited to ecosystems where chosen tech stack works
* ❌ Migration from existing projects requires tech stack change

**Rejected**: Violates technology-agnostic core principle

### Option 2: Configuration-Heavy Framework

**Description**: Highly configurable framework with all options in central config file (e.g., YAML/JSON)

**Pros**:
* Centralized configuration management
* Standard config format (YAML/JSON)
* Single file to understand project setup

**Cons**:
* ❌ Configuration explosion (100+ options for all tech stacks)
* ❌ Difficult for AI agents to navigate large config files
* ❌ No incremental adoption (need full config upfront)
* ❌ Hard to extend with project-specific conventions

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
* ✅ Technology-agnostic core with zero dependencies
* ✅ Incremental adoption (start with minimal adapter)
* ✅ AI agents navigate via AGENTS.md WHEN clauses
* ✅ Project-specific conventions in isolated adapter directory
* ✅ Core updates propagate without breaking adapters (Extends mechanism)
* ✅ Plugin architecture supports future extensibility

**Cons**:
* Requires adapter setup before usage (mitigated by bootstrap workflow)
* More files to understand than monolithic approach (mitigated by progressive disclosure)

**Selected**: Best fit for all decision drivers

## Decision Outcome

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

### Consequences

* Good, because the core methodology remains stable and tech-agnostic while project-specific conventions live in adapters.
* Bad, because adopting FDD requires an initial adapter setup and introduces additional files and concepts to learn.

#### Positive

* ✅ FDD works with any tech stack through adapter system
* ✅ Projects can adopt incrementally without disruption
* ✅ AI agents can execute workflows autonomously via AGENTS.md navigation
* ✅ Core updates don't break project adapters (Extends mechanism)
* ✅ Deterministic validation catches structural issues immediately
* ✅ Complete traceability through FDD IDs and code tags

#### Negative

* ⚠️ Requires adapter setup before first use (addressed by bootstrap workflow)
* ⚠️ Multiple files to understand (addressed by progressive disclosure: README → QUICKSTART → AGENTS.md)
* ⚠️ Learning curve for WHEN clause pattern (addressed by concrete examples in documentation)

#### Trade-offs

* **Flexibility vs Simplicity**: Chose flexibility (adapter system) over simplicity (monolithic). Justification: Supporting any tech stack is core mission.
* **Discoverability vs Configuration**: Chose discoverability (AGENTS.md files) over central config. Justification: Better for AI agents and incremental adoption.
* **Automation vs Manual**: Chose automated deterministic validation with manual fallback. Justification: Fail fast on obvious errors, human review for design quality.

## Related Design Elements

**Actors**:
* `fdd-fdd-actor-architect` - Designs system architecture using these patterns
* `fdd-fdd-actor-technical-lead` - Sets up adapters based on this architecture
* `fdd-fdd-actor-ai-assistant` - Executes workflows following this architecture
* `fdd-fdd-actor-developer` - Implements features following design-first approach

**Capabilities**:
* `fdd-fdd-fr-workflow-execution` - Enabled by workflow engine component
* `fdd-fdd-fr-validation` - Enabled by validation engine component
* `fdd-fdd-fr-adapter-config` - Enabled by adapter system component
* `fdd-fdd-fr-design-first` - Enforced by validation gates
* `fdd-fdd-fr-traceability` - Enabled by ID management component
* `fdd-fdd-fr-brownfield-support` - Enabled by incremental adoption support

**Requirements**:
* `fdd-fdd-req-executable-workflows` - Implemented by workflow engine
* `fdd-fdd-req-deterministic-validation` - Implemented by validation engine
* `fdd-fdd-req-adapter-configuration` - Implemented by adapter system
* `fdd-fdd-req-design-first` - Enforced by architecture design
* `fdd-fdd-req-traceability` - Implemented by ID management

**Principles**:
* `fdd-fdd-principle-tech-agnostic` - Core architectural principle
* `fdd-fdd-principle-design-first` - Core architectural principle
* `fdd-fdd-principle-machine-readable` - Core architectural principle
* `fdd-fdd-principle-deterministic-gate` - Core architectural principle
* `fdd-fdd-principle-traceability` - Core architectural principle

## More Information

**Notes**:

This is the foundational architectural decision for FDD. All subsequent ADRs will reference this decision as the baseline architecture. Future ADRs may refine specific components or patterns but should maintain compatibility with this layered architecture and the five core design principles.

The architecture is designed for evolution: new components can be added as plugins, new adapter specs can be defined without core changes, and new skills can extend the AI integration layer. However, the core principles (technology agnostic, design-first, machine-readable, deterministic gate, traceability) are fundamental and should not be compromised in future decisions.

**Supersedes**: None (initial decision)

**Superseded by**: None (current)

**Related ADRs**: None yet (this is ADR-0001)
