# SDLC Pipeline

## Overview

**Spider SDLC** is an artifact-first pipeline that turns intent into implementation through a fixed sequence of document layers, with deterministic validation gates and end-to-end traceability.

- **Layered transformation**: PRD → ADR + DESIGN → DECOMPOSITION → FEATURE → CODE.
- **Deterministic gates**: templates, IDs, cross-references, and task/acceptance criteria are validated at every step.
- **Behavior spec**: the **FEATURE** layer expresses behavior as **Spider DSL (SDSL)** flows/algorithms that can be implemented directly.
- **Traceability chain**: each downstream artifact references upstream IDs, and code keeps links via tags/markers.

## Pipeline Diagram

![**Spider** SDLC pipeline: PRD → DESIGN → DECOMPOSITION → FEATURE → CODE, with validation gates and ID traceability between layers](pipeline.drawio.svg)

Each layer **transforms** the previous artifact into a new form while **preserving traceability through IDs and references**:

| From | To | Transformation |
|------|-----|----------------|
| **PRD** | ADR + DESIGN | WHAT → HOW (architecture decisions and design) |
| **DESIGN** | DECOMPOSITION | Architecture → decomposition to features |
| **DECOMPOSITION** | FEATURE | Features → detailed specification and definitions of done |
| **FEATURE** | CODE | Detailed specification → implementation, source code |

The LLM reads the upstream artifact, understands its intent, and generates a downstream artifact of a **different kind** with explicit ID references back to the source. This creates a **traceable chain** from requirements to implementation.

---
## 🚀 Quick Start

**New to** **Spider SDLC**? Start here: **[QUICKSTART.md](../../QUICKSTART.md)**

Learn **Spider** in 10 minutes with:
- **Exact prompts to copy-paste** into your AI chat
- **Complete example**: Task management API from start to finish
- **Common scenarios**: What to do when requirements change
- **Working with existing docs**: Use what you already have

**Live example**: [Taskman (example project)](https://github.com/cyberfabric/spider-examples-taskman) — a complete task management project with a full artifact set and implementation.

## The 6-Layer SDLC Pipeline

| Artifact | Generation | Deterministic Validation | Feedback | Acceptance |
|----------|------------|--------------------------|----------|------------|
| **PRD** | Drafted from stakeholder input + market context with required IDs | Template structure, ID format | Semantic review vs industry best practices | Product Managers & Architects alignment |
| **ADR** | Captures key architecture decisions with rationale | Template structure, ID format | Semantic review vs industry best practices | Architects alignment |
| **DESIGN** | Derived from PRD with architecture decisions | Cross reference ID and tasks validation | Semantic review vs PRD + ADR + industry best practices | Architects alignment |
| **DECOMPOSITION** | Decomposed from DESIGN into implementable feature scope | Cross reference ID and tasks validation | Semantic review vs DESIGN + industry best practices | Architects alignment |
| **FEATURE** | Expanded from DECOMPOSITION into **Spider DSL** (**SDSL**) flows/algorithms plus implementation requirements | Cross reference ID and tasks validation | Semantic review vs DESIGN + DECOMPOSITION + industry best practices | Architects & Developers alignment |
| **CODE** | Implemented from FEATURE specs with traceability in code comments | Cross reference ID and tasks validation | Semantic review vs FEATURE + DESIGN + DECOMPOSITION + industry best practices | Developers & QA alignment |

## Spider SDLC vs Popular SDD Methodologies

For a comprehensive comparison of **Spider SDLC** with other AI-assisted development methodologies, see:

**[SDD_COMPARISON.md](../../SDD_COMPARISON.md)**

This document provides:
- Detailed cross-capability matrix with quantitative scoring
- Deep comparison across multiple dimensions
- Best-fit use cases for each framework
- Practical interoperability patterns

## What SDLC weaver provides

**Structured Templates** — Templates in spider format for each artifact kind.

**Semantic Checklists** — Expert review criteria for quality gates for each kind of artifact and source code. Agents self-review before output.

**Examples** — Canonical examples for each artifact kind.

**Rules specifications** — A set of tasks and acceptance criteria applicable for Spider workflows to generate and validate each artifact kind and source code.

## References

- [Rules Format Specification](../../requirements/rules-format.md) — how to structure rules.md files
- [Template Specification](../../requirements/template.md) — Marker syntax and validation
- [Semantic Checklists](codebase/checklist.md) — Code quality review criteria
- [Traceability Specification](../../requirements/traceability.md) — Code-to-design linking
- [**Spider DSL** Specification](../../requirements/SDSL.md) — Behavior description language
- [Prompt Engineering](../../requirements/prompt-engineering.md) — 9-layer methodology

## Documentation

**Quick Start**:
- [QUICKSTART.md](../../QUICKSTART.md) — 5-minute guide with examples

**Implementation Guides**:
- [GREENFIELD.md](guides/GREENFIELD.md) — Starting new projects
- [BROWNFIELD.md](guides/BROWNFIELD.md) — Integrating with existing codebases
- [MONOLITH.md](guides/MONOLITH.md) — Working with monolithic applications
- [TAXONOMY.md](guides/TAXONOMY.md) — **Spider** terminology and concepts
