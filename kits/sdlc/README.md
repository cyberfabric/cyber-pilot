# SDLC Kit

## Overview

**Cypilot SDLC** is a blueprint-based kit that provides an artifact-first pipeline, turning intent into implementation through a fixed sequence of document layers with deterministic validation gates and end-to-end traceability.

- **Layered transformation**: PRD → ADR + DESIGN → DECOMPOSITION → FEATURE → CODE
- **Deterministic gates**: templates, IDs, cross-references, and task/acceptance criteria are validated by the skill engine at every step
- **Behavior spec**: the **FEATURE** layer expresses behavior as **Cypilot DSL (CDSL)** flows/algorithms/states plus definitions of done that can be implemented directly
- **Traceability chain**: each downstream artifact references upstream IDs; code keeps links via `@cpt-*` markers
- **Blueprint-driven**: all kit resources (templates, rules, checklists, examples, workflows) are generated from blueprint files using `@cpt:` markers

## Pipeline Diagram

![**Cypilot** SDLC pipeline: PRD → ADR + DESIGN → DECOMPOSITION → FEATURE → CODE, with validation gates and ID traceability between layers](pipeline.drawio.svg)

Each layer **transforms** the previous artifact into a new form while **preserving traceability through IDs and references**:

| From | To | Transformation |
|------|-----|----------------|
| **PRD** | ADR + DESIGN | WHAT → HOW (architecture decisions and design) |
| **DESIGN** | DECOMPOSITION | Architecture → decomposition to features |
| **DECOMPOSITION** | FEATURE | Features → detailed behavior + definitions of done |
| **FEATURE** | CODE | Detailed behavior + DoD → implementation, source code |

The LLM reads the upstream artifact, understands its intent, and generates a downstream artifact of a **different kind** with explicit ID references back to the source. This creates a **traceable chain** from requirements to implementation.

---
## Quick Start

**New to Cypilot SDLC?** Start here: **[QUICKSTART.md](guides/QUICKSTART.md)**

Learn Cypilot in 10 minutes with:
- **Exact prompts to copy-paste** into your AI chat
- **Complete example**: Task management API from start to finish
- **Common scenarios**: What to do when requirements change
- **Working with existing docs**: Use what you already have

**Live example**: [Taskman (example project)](https://github.com/cyberfabric/cyber-pilot-examples-taskman) — a complete task management project with a full artifact set and implementation.

## The SDLC Pipeline

| Artifact | Generation | Deterministic Validation | Feedback | Acceptance |
|----------|------------|--------------------------|----------|------------|
| **PRD** | Drafted from stakeholder input with required IDs | Template structure, ID format | Semantic review vs industry best practices | Product Managers & Architects alignment |
| **ADR** | Captures key architecture decisions with rationale | Template structure, ID format | Semantic review vs industry best practices | Architects alignment |
| **DESIGN** | Derived from PRD with architecture decisions | Cross reference ID and tasks validation | Semantic review vs PRD + ADR + industry best practices | Architects alignment |
| **DECOMPOSITION** | Decomposed from DESIGN into implementable feature scope | Cross reference ID and tasks validation | Semantic review vs DESIGN + industry best practices | Architects alignment |
| **FEATURE** | Expanded from DECOMPOSITION into **Cypilot DSL** (**CDSL**) flows/algorithms/states plus definitions of done | Cross reference ID and tasks validation | Semantic review vs DESIGN + DECOMPOSITION + industry best practices | Architects & Developers alignment |
| **CODE** | Implemented from FEATURE with traceability in code comments | Cross reference ID and tasks validation | Semantic review vs FEATURE + DESIGN + DECOMPOSITION + industry best practices | Developers & QA alignment |

## What the SDLC Kit Provides

All resources below are **generated from blueprints** in `config/kits/sdlc/blueprints/` via `@cpt:` markers:

- **Structured Templates** (`template.md`) — templates for each artifact kind, generated from `@cpt:prompt` markers
- **Semantic Checklists** (`checklist.md`) — expert review criteria for quality gates, generated from `@cpt:checklist` + `@cpt:check` markers
- **Examples** (`examples/`) — canonical examples for each artifact kind, generated from `@cpt:example` markers
- **Rules** (`rules.md`) — tasks and acceptance criteria for generation and validation, generated from `@cpt:rules` + `@cpt:rule` markers
- **Constraints** (`constraints.toml`) — heading and ID constraints for deterministic validation, generated from `@cpt:heading` + `@cpt:id` markers
- **Workflows** (`workflows/`) — kit-specific workflows (PR review, PR status), generated from `@cpt:workflow` markers
- **Skill Extensions** — kit-specific skill content injected into `.gen/SKILL.md`, from `@cpt:skill` markers

## References

- [Rules Specification](../../architecture/specs/kit/rules.md) — how to structure rules.md files
- [Identifiers & Traceability](../../architecture/specs/traceability.md) — ID formats, naming, and code traceability
- [Code Quality Checklist](codebase/checklist.md) — code review criteria
- [CDSL Specification](../../architecture/specs/CDSL.md) — behavior description language for FEATURE artifacts
- [Prompt Engineering](../../requirements/prompt-engineering.md) — 9-layer methodology
- [Blueprint Constraints](guides/constraints.md) — heading and ID constraint format

## Documentation

**Quick Start**:
- [QUICKSTART.md](guides/QUICKSTART.md) — 10-minute guide with real prompts and examples

**Implementation Guides**:
- [GREENFIELD.md](guides/GREENFIELD.md) — starting new projects from scratch
- [BROWNFIELD.md](guides/BROWNFIELD.md) — integrating with existing codebases (start anywhere)
- [MONOLITH.md](guides/MONOLITH.md) — working with modular monoliths
- [TAXONOMY.md](guides/TAXONOMY.md) — artifact taxonomy and terminology
