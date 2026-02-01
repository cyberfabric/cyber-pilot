# Framework for Documentation and Development (FDD)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0-green.svg)]()
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()

**Version**: 2.0 | **Status**: Active | **Language**: English

**Audience**: Development teams, technical leads, architects, product managers, project managers, quality assurance engineers, data engineers, data scientists, and any other team members who need to build software.

> **TL;DR**: FDD is a framework for building software with full traceability from requirements to code. Design in plain English (FDL), validate before coding, use any tech stack. Works great with AI assistants.

Framework for Documentation and Development is a **universal framework** for building software systems with clear traceability from requirements to implementation.

**Built for modern development**: FDD works with AI coding assistants, supports any tech stack, and provides structured workflows that teams can follow manually or automate.

---

## Table of Contents

- [Framework for Documentation and Development (FDD)](#framework-for-documentation-and-development-fdd)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [🚀 Quick Start](#-quick-start)
  - [What is FDD?](#what-is-fdd)
  - [FDD SDLC Overview](#fdd-sdlc-overview)
    - [How It Works: LLM Context Transformation](#how-it-works-llm-context-transformation)
    - [The 5-Layer SDLC Pipeline](#the-5-layer-sdlc-pipeline)
    - [What SDLC Rules Provide](#what-sdlc-rules-provide)
    - [References](#references)
  - [Agent Skills \& Workflows Foundation](#agent-skills--workflows-foundation)
  - [Key Strengths](#key-strengths)
    - [1. Structured Workflows \& Skills System](#1-structured-workflows--skills-system)
    - [2. Powerful Validation Methodologies](#2-powerful-validation-methodologies)
    - [3. FDD vs OpenSpec vs Spec Kit vs MCAF](#3-fdd-vs-openspec-vs-spec-kit-vs-mcaf)
    - [3. FDL (FDD Description Language) - Plain English Logic](#3-fdl-fdd-description-language---plain-english-logic)
  - [Why Use FDD?](#why-use-fdd)
  - [Documentation](#documentation)
  - [Contributing](#contributing)

---

## Prerequisites

Before using FDD, ensure you have:

- **Python 3.8+** — Required for `fdd` skill execution
- **Git** — For version control and submodule installation (recommended)
- **AI Assistant** — Claude, GPT-4, or compatible AI coding assistant (recommended but optional)

---

## 🚀 Quick Start

**New to FDD?** Start here: **[QUICKSTART.md](QUICKSTART.md)**

Learn FDD in 10 minutes with:
- **Exact prompts to copy-paste** into your AI chat
- **Complete example**: Task management API from start to finish
- **Common scenarios**: What to do when requirements change
- **Working with existing docs**: Use what you already have

**Live example**: [Taskman (FDD example project)](https://github.com/cyberfabric/fdd-examples-taskman) — a complete task management project with the full FDD artifact set and implementation.

---

## What is FDD?

FDD helps teams build software by:

1. **Designing before coding**: Document what you're building in clear, reviewable formats
2. **Breaking work into features**: Each feature is independent and testable
3. **Using plain English**: Algorithms described in FDL (not code), reviewable by non-programmers
4. **Ensuring traceability**: Requirements remain traceable to implementation
5. **Validating designs**: Catch issues before implementation

---

## FDD SDLC Overview

FDD is an **extensible framework** - you can create any pipeline with custom rules packages for your specific needs. However, we've already done the heavy lifting and provide a production-ready **SDLC Rules Package** at [`rules/sdlc`](rules/sdlc) that implements a complete software development lifecycle.

![FDD 5-layer SDLC pipeline: PRD → DESIGN → FEATURES → FEATURE → CODE, with validation gates and ID traceability between layers](fdd-flow-layers.drawio.svg)

### How It Works: LLM Context Transformation

Each layer **transforms** the previous artifact into a new form while **preserving traceability through IDs and references**:

| From | To | Transformation |
|------|-----|----------------|
| **PRD** | DESIGN | WHAT → HOW (architecture) |
| **DESIGN** | FEATURES | Architecture → implementation plan |
| **FEATURES** | FEATURE | Plan → detailed FDL specification |
| **FEATURE** | CODE | FDL specification → implementation |

The LLM reads the upstream artifact, understands its intent, and generates a downstream artifact of a **different kind** with explicit ID references back to the source. This creates a **traceable chain** from requirements to implementation.

### The 5-Layer SDLC Pipeline

| Artifact | Generation | Deterministic Validation | Feedback | Acceptance |
|----------|------------|--------------------------|----------|------------|
| **PRD** | Drafted from stakeholder input + market context with required IDs | Template structure, ID format | Semantic review vs industry best practices | Product Manager sign-off, stakeholder alignment |
| **ADR** | Captures key architecture decisions with rationale | Template structure, ID format | Semantic review vs industry best practices | Architect approval of decision rationale |
| **DESIGN** | Derived from PRD with architecture decisions | Cross reference ID and tasks validation | Semantic review vs PRD + ADR + industry best practices | Architect approval of architecture direction |
| **FEATURES** | Decomposed from DESIGN into implementable feature scope | Cross reference ID and tasks validation | Semantic review vs DESIGN + industry best practices | Architect acceptance of decomposition and scope |
| **FEATURE** | Expanded from FEATURES into FDL flows/algorithms plus implementation requirements | Cross reference ID and tasks validation | Semantic review vs DESIGN + FEATURES + industry best practices | Developer agreement on implementability |
| **CODE** | Implemented from FEATURE specs with traceability in code comments | Cross reference ID and tasks validation | Semantic review vs FEATURE + DESIGN + FEATURES + industry best practices | QA acceptance of test results and quality |

### What SDLC Rules Provide

**Structured Templates** — Marker-based templates define exact artifact structure.

**Semantic Checklists** — Expert review criteria for quality gates. Agents self-review before output.

**Code Traceability** — `@fdd-*` markers link code to design.

**Prompt Engineering** — 9-layer methodology for generation rules.

**FDL** — Plain English behavior descriptions that map to code.

### References

- [Rules Format Specification](requirements/rules-format.md) — How to structure rules.md files
- [Template Specification](requirements/template.md) — Marker syntax and validation
- [Semantic Checklists](rules/sdlc/codebase/checklist.md) — Code quality review criteria
- [Traceability Specification](requirements/traceability.md) — Code-to-design linking
- [FDL Specification](requirements/FDL.md) — Behavior description language
- [Prompt Engineering](requirements/prompt-engineering.md) — 9-layer methodology

---

## Agent Skills & Workflows Foundation

FDD is built on **Agent Skills + Workflows** registered through the `fdd` tool in your IDE. This architecture provides deterministic execution and eliminates ambiguity in AI-assisted development.

**Core components**:
1. **Agent Skills** ([`skills/fdd/SKILL.md`](skills/fdd/SKILL.md)) — FDD methodology knowledge and rules
2. **Workflows** ([`workflows/generate.md`](workflows/generate.md)) — Step-by-step executable procedures
3. **FDD Tool** — IDE integration that registers skills and workflows as commands

**Key benefits**:
- **More deterministic** — Workflows follow structured steps, reducing interpretation variance
- **IDE-native** — Skills and workflows appear as native IDE commands
- **Version controlled** — Track methodology changes via git
- **Composable** — Core skills + project-specific adapters
- **No context search** — Skills provide complete methodology in structured format

When an AI agent encounters FDD, it loads the `fdd` skill → reads workflow specifications → executes deterministic steps with full methodology context.

---

## Key Strengths

### 1. Structured Workflows & Skills System

FDD provides **4 core workflows** registered both as **skills** (AI tool invocation) and **workflows** (step-by-step execution):

- **`/fdd`** — Entrypoint skill that routes to other workflows
- **`/fdd-generate`** — Generate or update FDD artifacts
- **`/fdd-validate`** — Validate artifacts against rules and checklists
- **`/fdd-adapter`** — Configure project-specific adapter

**Skill capabilities**:
- **Validation**: Validate artifacts registered in `{adapter-dir}/artifacts.json`
- **Search**: List sections, IDs, and items in any artifact
- **Traceability**: Find where IDs are defined or used (repo-wide)
- **Code Integration**: Scan codebase for `@fdd-*` traceability markers

**Execution modes**:
- **`/fdd-generate` & `/fdd-validate`** — Standardized execution protocol
  - Support both CREATE and UPDATE modes automatically
  - Preserve existing content when updating
  - Validate each step before proceeding
- **`/fdd-adapter`** — Specialized brownfield analysis
  - Analyzes existing projects to extract conventions
  - Fine-tunes FDD integration for established codebases

**Why this matters**:
- **Consistent** — Same structure and quality every time
- **Iterative** — Update artifacts as project evolves
- **AI-friendly** — Reduced ambiguity through structured protocols
- **Human-readable** — Anyone can execute manually if needed

### 2. Powerful Validation Methodologies

FDD provides **two specialized methodologies** for semantic validation and project analysis:

**1. Prompt Engineering Methodology** ([`requirements/prompt-engineering.md`](requirements/prompt-engineering.md))
- Framework for creating custom system prompts, skills, and workflows
- Foundation for building custom pipelines on top of FDD (like the SDLC pipeline)
- Works on top of deterministic template format ([`requirements/template.md`](requirements/template.md))
- Includes traceability methodology between artifacts and code ([`requirements/traceability.md`](requirements/traceability.md))
- **Example**: [SDLC Rules Package](rules/sdlc/README.md) — production-ready 6-layer pipeline (PRD → ADR → DESIGN → FEATURES → FEATURE → CODE)

**2. Brownfield Analysis Methodology** ([`requirements/reverse-engineering.md`](requirements/reverse-engineering.md))
- Analyzes existing projects to extract conventions and patterns
- Used by `/fdd-adapter` to configure FDD for established codebases
- Enables gradual FDD adoption without rewriting existing systems

### 3. FDD vs OpenSpec vs Spec Kit vs MCAF

For a comprehensive comparison of FDD with other AI-assisted development methodologies, see:

**[SDD_COMPARISON.md](SDD_COMPARISON.md)**

This document provides:
- Detailed cross-capability matrix with quantitative scoring
- Deep comparison across multiple dimensions
- Best-fit use cases for each framework
- Practical interoperability patterns

### 3. FDL (FDD Description Language) - Plain English Logic

FDD uses **FDL** to describe behavior in plain English - no code syntax, just numbered markdown lists with bold keywords.

**Why**: Reviewable by anyone (stakeholders, QA, developers). Design stays valid across languages. Perfect for AI code generation.

**Example - User Authentication**:

```markdown
1. [x] - `ph-1` - User submits login form - `inst-submit-form`
2. [x] - `ph-1` - System validates credentials - `inst-validate-creds`
   1. [x] - `ph-1` - **IF** invalid: - `inst-if-invalid`
      1. [x] - `ph-1` - Show error - `inst-show-error`
      2. [x] - `ph-1` - **RETURN** error - `inst-return-error`
3. [ ] - `ph-2` - **TRY**: - `inst-try`
   1. [ ] - `ph-2` - Create session token - `inst-create-token`
   2. [ ] - `ph-2` - Store in database - `inst-store-db`
4. [ ] - `ph-2` - **CATCH** DatabaseError: - `inst-catch`
   1. [ ] - `ph-2` - Log error - `inst-log-error`
   2. [ ] - `ph-2` - **RETURN** 500 error - `inst-return-500`
```

**Keywords**: **IF**/ELSE, **FOR EACH**, **WHILE**, **TRY**/CATCH, **PARALLEL**, **RETURN**, **MATCH**

**FDD strictly prohibits code** in DESIGN.md files (enforced by validation):
- No `if (x > 5) { ... }` syntax
- No function definitions
- Only FDL plain English

**Full syntax**: See [FDL Specification](requirements/FDL.md)

---

## Why Use FDD?

**For Single Expert / Architect**:
- AI automates design → validation → implementation pipeline
- Living documentation stays in sync with code (enforced by validation)
- Full traceability from requirements to implementation
- Catch issues early through validation before coding

**For Teams**:
- Stakeholders review plain English flows (no code knowledge needed)
- Feature designs are complete specs, not ambiguous tickets
- Progress tracking via FEATURES.md
- Consistent standards enforced through workflows

**For Business**:
- Lower costs through less rework and fewer bugs
- Predictability with complete designs before implementation
- Risk reduction via early validation
- Audit trail for every change

**What FDD Prevents**:

| Without FDD | With FDD |
|-------------|----------|
| Scattered requirements in tickets | Complete design in one place |
| Non-reviewable logic | Plain English flows |
| Duplicated type definitions | Single domain model |
| Outdated documentation | Validated against code |
| Ambiguous specs | Unambiguous feature designs |
| Inconsistent AI output | Workflow-enforced patterns |

---

## Documentation

**Quick Start**:
- [QUICKSTART.md](QUICKSTART.md) — 5-minute guide with examples

**Implementation Guides**:
- [ADAPTER.md](guides/ADAPTER.md) — Creating project adapters
- [GREENFIELD.md](guides/GREENFIELD.md) — Starting new projects
- [BROWNFIELD.md](guides/BROWNFIELD.md) — Integrating with existing codebases
- [MONOLITH.md](guides/MONOLITH.md) — Working with monolithic applications
- [TAXONOMY.md](guides/TAXONOMY.md) — FDD terminology and concepts

---

## Contributing

We welcome contributions to FDD.

**How to contribute**:

1. **Report issues**: Use GitHub Issues for bugs, feature requests, or questions
2. **Submit pull requests**: Fork the repository, create a branch, submit PR with description
3. **Follow FDD methodology**: Use FDD workflows when making changes to FDD itself
4. **Update documentation**: Include doc updates for any user-facing changes

**Guidelines**:
- Follow existing code style and conventions
- Update workflows with real-world examples when possible
- Maintain backward compatibility
- Document breaking changes in version history
- Add tests for new functionality

**Development setup**:
```bash
git clone <fdd-repo-url>
cd FDD
python3 -m pytest tests/  # Run tests
```