---
status: accepted
date: 2026-01-17
---

# ADR-0001: Initial Cypilot Architecture

**ID**: `cpt-cypilot-adr-initial-architecture-v1`

## Context and Problem Statement

Cypilot (Spec-Driven Design) is a universal methodology framework for building software systems with complete traceability from product requirements to implementation. The methodology must be technology-agnostic to support any tech stack, while providing structured workflows that can be executed by both human teams and AI coding assistants.

The architecture must enable incremental adoption, support design-first development, and maintain design-code coherence through systematic traceability.

Key requirements driving this decision:
* Support any programming language, framework, or technology stack
* Enable AI agents to execute workflows autonomously with minimal human intervention
* Provide deterministic validation to fail fast on structural issues
* Maintain complete traceability from product requirements through design to implementation
* Support incremental methodology adoption without disrupting existing projects

## Decision Drivers

1. **Technology Agnostic Core** (from `cpt-cypilot-principle-tech-agnostic`)
   - Methodology must work equally well for Python, Rust, JavaScript, Java, Go, or any language
   - No forced technology choices in core; all tech decisions in project adapters
   - Domain model formats and API contract formats must be configurable

2. **Design Before Code** (from `cpt-cypilot-principle-design-first`)
   - All artifacts must be validated before implementation proceeds
   - Design is single source of truth; code follows design specifications
   - Validation gates prevent proceeding without passing quality thresholds

3. **Machine-Readable Specifications** (from `cpt-cypilot-principle-machine-readable`)
   - Enable automation and AI agent execution
   - Reduce manual validation effort through deterministic checking
   - Support code generation from validated designs

4. **Incremental Adoption** (from `cpt-cypilot-fr-brownfield-support`)
   - Projects must adopt Cypilot progressively without disruption
   - Support legacy system integration with minimal refactoring
   - Adapter-first approach enables starting with lightweight configuration

5. **Complete Traceability** (from `cpt-cypilot-fr-traceability`)
   - Every design element needs unique ID for tracking
   - Code tags must link implementation to specifications
   - Support impact analysis when designs change

## Considered Options

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

## Decision Outcome

Chosen option: "Layered architecture with plugin-based adapter system", because it best satisfies technology-agnosticism, incremental adoption, and deterministic validation/traceability while remaining navigable for AI agents.

Cypilot uses **Layered Architecture with Plugin-Based Adapter System** with the following structure:

**Core Components** (6 components):
1. **Methodology Core** - Universal specifications (requirements, workflows, AGENTS.md)
2. **Adapter System** - Project-specific customization (tech stack, domain model, conventions)
3. **Workflow Engine** - Operation workflows (CREATE/UPDATE) and validation workflows
4. **Validation Engine** - Deterministic validators with 100-point scoring system
5. **ID Management** - Cypilot ID generation, qualified IDs, repository-wide scanning
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
* **Incremental Adoption**: Adapter → PRD → Design → Specs → Implementation

**Technology Choices for Cypilot Implementation**:
* **Core Tooling**: Python 3.6+ standard library only (no external dependencies)
* **Artifacts**: Plain Markdown (universal compatibility, version control friendly)
* **API Interface**: CLISPEC (command-line interface, JSON output for machine consumption)
* **Domain Model Format**: Markdown-based artifact structure (not code-level types)

### Consequences

- Positive: Cypilot works with any tech stack through adapter system
- Positive: Projects can adopt incrementally without disruption
- Positive: AI agents can execute workflows autonomously via AGENTS.md navigation
- Positive: Core updates don't break project adapters (Extends mechanism)
- Positive: Deterministic validation catches structural issues immediately
- Positive: Complete traceability through Cypilot IDs and code tags
- Negative: Requires adapter setup before first use (addressed by bootstrap workflow)
- Negative: Multiple files to understand (addressed by progressive disclosure)
- Negative: Learning curve for WHEN clause pattern (addressed by concrete examples)
- Follow-up: None (initial decision)

### Confirmation

Confirmed by deterministic validation of core artifacts (`make validate`) and by maintaining template compliance across PRD/DESIGN/ADR.

## Pros and Cons of the Options

### Option 1: Monolithic Framework with Built-in Tech Stack

**Description**: Single unified framework with opinionated technology choices (e.g., Python + Django + PostgreSQL)

* Good, because simpler initial implementation
* Bad, because forces technology choices on projects

### Option 2: Configuration-Heavy Framework

**Description**: Highly configurable framework with all options in central config file (e.g., YAML/JSON)

* Good, because centralized configuration management
* Bad, because configuration explosion and poor AI agent discoverability

### Option 3: Layered Architecture with Plugin-Based Adapter System

**Description**: Core methodology layer (universal) + Adapter layer (project-specific) + Plugin components (workflows, validation, ID management)

* Good, because best fit for technology-agnosticism + incremental adoption
* Bad, because requires adapter setup before first use

## Traceability

- **PRD**: [PRD.md](../../PRD.md)
- **DESIGN**: [DESIGN.md](../../DESIGN.md)

This decision directly addresses the following requirements or design elements:

* `cpt-cypilot-fr-workflow-execution`
* `cpt-cypilot-fr-validation`
* `cpt-cypilot-fr-adapter-config`
* `cpt-cypilot-fr-design-first`
* `cpt-cypilot-fr-traceability`
* `cpt-cypilot-fr-brownfield-support`

