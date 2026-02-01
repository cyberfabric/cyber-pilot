# SDLC Rules Package

**Package ID**: `sdlc`  
**Purpose**: Production-ready Software Development Lifecycle pipeline for FDD projects

---

## Overview

The SDLC Rules Package implements a complete 6-layer development pipeline (PRD → ADR → DESIGN → FEATURES → FEATURE → CODE) with deterministic validation gates and semantic review checklists.

**Key Components**:
- **Artifact Templates** ([`artifacts/`](artifacts/)) — Structured templates for PRD, DESIGN, ADR, FEATURES, FEATURE
- **Semantic Checklists** ([`artifacts/*/checklist.md`](artifacts/)) — Expert review criteria for each artifact
- **Code Rules** ([`codebase/rules.md`](codebase/rules.md)) — Implementation and validation protocol
- **Code Quality Checklist** ([`codebase/checklist.md`](codebase/checklist.md)) — Engineering best practices

---

## The 6-Layer Pipeline

```
PRD → ADR → DESIGN → FEATURES → FEATURE → CODE
```

Each layer includes:
1. **Template** — Deterministic structure with FDD markers
2. **Checklist** — Semantic review criteria
3. **Example** — Valid artifact reference

---

## Artifact Types

| Artifact | Purpose | Path |
|----------|---------|------|
| **PRD** | Product Requirements Document | [`artifacts/PRD/`](artifacts/PRD/) |
| **ADR** | Architecture Decision Record | [`artifacts/ADR/`](artifacts/ADR/) |
| **DESIGN** | Overall System Design | [`artifacts/DESIGN/`](artifacts/DESIGN/) |
| **FEATURES** | Feature Manifest | [`artifacts/FEATURES/`](artifacts/FEATURES/) |
| **FEATURE** | Feature Design | [`artifacts/FEATURE/`](artifacts/FEATURE/) |
| **CODE** | Implementation Rules | [`codebase/`](codebase/) |

---

## Validation Gates

Each artifact passes through **3 validation stages**:

1. **Deterministic Validation** — Template structure, ID format, cross-references
2. **Semantic Feedback** — Review against upstream artifacts + industry best practices
3. **Acceptance** — Role-based sign-off (Product Manager, Architect, Developer, QA)

See [README.md](../../README.md#the-5-layer-sdlc-pipeline) for full pipeline details.

---

## Usage

This package is used by:
- **`/fdd-generate`** workflow — Artifact generation from templates
- **`/fdd-validate`** workflow — Deterministic + semantic validation
- **FDD CLI** — `fdd generate`, `fdd validate` commands

---

## Customization

To create your own rules package:

1. Study this SDLC package structure
2. Read [Prompt Engineering Specification](../../requirements/prompt-engineering.md)
3. Follow [Template Specification](../../requirements/template.md) for markers
4. Use [Rules Format Specification](../../requirements/rules-format.md) for structure

The SDLC package demonstrates FDD's extensibility — you can create domain-specific pipelines (e.g., data science, ML ops, compliance) using the same methodology.
