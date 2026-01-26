# FDD Taxonomy

This guide defines what each FDD artifact is, why it exists, and how it helps both humans and AI agents.

**Language**: This guide is intentionally written in English to match the FDD framework conventions.

## Core Concepts

- **Artifact**: A Markdown document with a stable path and a deterministic validator.
- **Workflow**: A repeatable procedure that creates/updates/validates artifacts.
- **Layer**: A dependency level in the FDD chain. Higher layers must not contradict lower layers.
- **Deterministic gate**: A tool-based validation step that must pass before proceeding.

## How to Use This Guide

- Use the **Artifact Index** to jump to the artifact you are about to create/update.
- Use the **What it is / What it is not** sections to choose the right artifact.
- Use the **Templates & Examples** section to start from a known-good structure.
- Use the **deterministic gate** (`fdd validate`) before moving to the next layer.

## Layers and Dependency Graph

FDD artifacts form a dependency chain. The higher layer is allowed to be more specific, but must not contradict lower layers.

```
AGENTS/Adapter
  -> PRD
    -> ADR
      -> DESIGN
        -> FEATURES
          -> feature DESIGN
            -> code (traceability)
```

**Practical rule**:
- If the code contradicts a feature design, update the design first and re-validate.
- If a feature design contradicts overall design, update overall design (or add ADR) first.

## Artifact Index

- [FDD Taxonomy](#fdd-taxonomy)
  - [Core Concepts](#core-concepts)
  - [How to Use This Guide](#how-to-use-this-guide)
  - [Layers and Dependency Graph](#layers-and-dependency-graph)
  - [Artifact Index](#artifact-index)
  - [AGENTS.md](#agentsmd)
  - [Project Adapter (FDD-Adapter)](#project-adapter-fdd-adapter)
  - [PRD.md](#prdmd)
  - [DESIGN.md](#designmd)
  - [ADR](#adr)
  - [FEATURES.md](#featuresmd)
  - [Feature DESIGN.md](#feature-designmd)
  - [Templates & Examples](#templates--examples)
  - [Validation (Deterministic Gate)](#validation-deterministic-gate)
  - [Mapping to Common Document Names](#mapping-to-common-document-names)
  - [Why Many Small Artifacts (Not One Big Doc)](#why-many-small-artifacts-not-one-big-doc)

---

<a id="agentsmd"></a>
## AGENTS.md

**Path**:
- `AGENTS.md`
- `workflows/AGENTS.md`
- `{adapter-directory}/AGENTS.md`

**Templates**:
- None (navigation-only)

**Examples**:
- [core](../AGENTS.md)
- [workflow navigation](../workflows/AGENTS.md)
- [adapter (this repo)](../.adapter/AGENTS.md)

**Purpose**:
- Provide navigation rules for AI agents.
- Point to authoritative workflow and requirement files.

**What it is**:
- A navigation-only entrypoint that tells agents what to read and in what order.
- A set of deterministic rules (MUST/ALWAYS) for routing requests to workflows and requirements.

**What it is not**:
- Not a specification document (do not duplicate requirements/workflows here).
- Not a project architecture document.
- Not a tutorial.

**Should contain**:
- Pointers to authoritative workflow and requirement files.
- Deterministic navigation rules (MUST/ALWAYS) and routing rules.
- Minimal, stable links that help agents find the right source of truth.

**Should not contain**:
- Architecture specifications or decisions.
- Templates or example content (keep those in `templates/` and `examples/`).
- Long-form tutorials (use [**`guides/ADAPTER.md`**](../guides/ADAPTER.md) for tutorials).

**Why this helps**:
- **Agent**: deterministic navigation; fewer hallucinations; lower search cost.
- **Human**: one place to understand how the agent will behave.

---

<a id="artifact-adapter"></a>
## Project Adapter (FDD-Adapter)

**Typical path**:
- `FDD-Adapter/AGENTS.md` (for projects using FDD)

**In this repository**:
- `.adapter/AGENTS.md` (adapter for developing FDD itself)

**Template**:
- [templates/adapter-AGENTS.template.md](../templates/adapter-AGENTS.template.md)

**Examples**:
- [valid](../examples/requirements/adapter/valid.md)
- [invalid](../examples/requirements/adapter/invalid.md)

**Purpose**:
- Specify project-specific conventions (tech stack, domain model format, API contracts, testing).

**What it is**:
- A project-specific overlay that extends core FDD navigation and defaults.
- The source of truth for where to find domain model, API contracts, conventions, and validation expectations.

**What it is not**:
- Not the overall system design (that lives in `architecture/DESIGN.md`).
- Not a dumping ground for general documentation.
- Not a replacement for ADRs.

**Should contain**:
- `**Extends**: ...` back to core `AGENTS.md`.
- Project-specific conventions:
  - Tech stack/tooling constraints.
  - Domain model format and location.
  - API contract format and location.
  - Validation/CI expectations.

**Should not contain**:
- PRD (use `architecture/PRD.md`).
- Architecture decisions rationale (use ADRs).
- Feature specs or implementation plans.

**Why this helps**:
- **Agent**: removes ambiguity about formats, locations, and conventions.
- **Human**: makes decisions explicit and reviewable.

---

<a id="artifact-prd"></a>
## PRD.md

**Path**:
- `architecture/PRD.md`

**Template**:
- [templates/PRD.template.md](../templates/PRD.template.md)

**Examples**:
- [valid](../examples/requirements/prd/valid.md)
- [invalid](../examples/requirements/prd/invalid.md)

**Purpose**:
- Define the PRD: vision, actors, capabilities.

**What it is**:
- Stable prd vocabulary with IDs (actors, capabilities, and optionally use cases).
- The baseline that downstream design and features reference for scope and meaning.

**What it is not**:
- Not a technical architecture document.
- Not a feature backlog.
- Not an implementation plan.

**Should contain**:
- Vision, actors, capabilities (and optionally use cases) with stable IDs.
- Business vocabulary that downstream artifacts can reference without reinterpretation.

**Should not contain**:
- Technical architecture (use `architecture/DESIGN.md`).
- Implementation steps or tasks.
- API endpoint specs or schemas.

**Inputs** (typical):
- PRD/BRD or product notes.
- Existing system behavior (brownfield: code is allowed to be the source of truth).

**Outputs** (what downstream artifacts rely on):
- Stable actor IDs and capability IDs.

**Why this helps**:
- **Agent**: stable actor/capability IDs; constraints for design and features.
- **Human**: aligns stakeholders and engineering on what is being built.

---

<a id="artifact-design"></a>
## DESIGN.md

**Path**:
- `architecture/DESIGN.md`

**Template**:
- [templates/DESIGN.template.md](../templates/DESIGN.template.md)

**Examples**:
- [valid](../examples/requirements/overall-design/valid.md)
- [invalid](../examples/requirements/overall-design/invalid.md)

**Purpose**:
- Define the overall system architecture.
- Define domain model and API contracts at the system level.
- Establish principles and constraints used by all features.

**What it is**:
- A system-level architecture baseline (constraints, principles, shared concepts, and contracts).
- The parent document that feature designs must not contradict.

**What it is not**:
- Not a per-feature behavioral spec (use feature `DESIGN.md`).
- Not an implementation task list.
- Not a code tutorial.

**Should contain**:
- System-level constraints and principles.
- Shared concepts/types/contracts that features must not redefine.
- References to domain model and API contract sources.

**Should not contain**:
- Feature-level flows/algorithms/states (use feature `DESIGN.md`).
- Implementation tasks.
- Decision rationale debates (use ADRs).

**Typical structure inside**:
- Requirements/principles with stable IDs.
- Domain model and API contract references.
- Technical architecture decisions that features must obey.

**Why this helps**:
- **Agent**: single source of truth for types/contracts; prevents type redefinition across features.
- **Human**: reviewable architecture; stable baseline for refactoring.

---

<a id="artifact-adr"></a>
## ADR

**Path**:
- `architecture/ADR/**`

**Template**:
- [templates/ADR.template.md](../templates/ADR.template.md)

**Examples**:
- [valid](../examples/requirements/adr/valid.md)
- [invalid](../examples/requirements/adr/invalid.md)

**Purpose**:
- Capture architectural decisions and trade-offs.

**What it is**:
- A decision record: context, options, outcome, and consequences.
- A durable rationale that future changes can reference.

**What it is not**:
- Not the primary place to describe architecture (use `architecture/DESIGN.md`).
- Not meeting notes or a scratchpad.
- Not a feature spec.

**Should contain**:
- Context/problem statement.
- Considered options (short, comparable).
- Decision outcome and consequences.
- Links to related design elements (IDs).

**Should not contain**:
- Full architecture description (keep that in `architecture/DESIGN.md`).
- Detailed implementation steps.
- Broad product requirements.

**Anti-pattern**:
- Do not use ADRs for operational runbooks or temporary notes.

**Why this helps**:
- **Agent**: reduces re-litigation of decisions; provides constraints for future changes.
- **Human**: preserves reasoning; improves maintainability.

---

<a id="artifact-features"></a>
## FEATURES.md

**Path**:
- `architecture/features/FEATURES.md`

**Template**:
- [templates/FEATURES.template.md](../templates/FEATURES.template.md)

**Examples**:
- [valid](../examples/requirements/features-manifest/valid.md)
- [invalid](../examples/requirements/features-manifest/invalid.md)

**Purpose**:
- Maintain the feature list, priorities, statuses, and dependencies.

**What it is**:
- A manifest/index of features: status, dependencies, and coverage of requirement IDs.
- A routing surface for humans and agents (“what exists”, “what is next”).

**What it is not**:
- Not the detailed feature behavior spec (use feature `DESIGN.md`).
- Not a task board.
- Not a narrative roadmap document.

**Should contain**:
- Feature list with stable IDs, status, priority.
- Dependencies/blocks and coverage of requirement IDs.
- High-level scope bullets (not detailed design).

**Should not contain**:
- Feature flows/algorithms/states.
- Task breakdowns.
- Code-level details.

**Key responsibilities**:
- Track feature status consistently with feature `DESIGN.md`.
- Declare dependencies and the requirement IDs covered.

**Why this helps**:
- **Agent**: objective routing for “what to work on next”; status-driven validation.
- **Human**: roadmap and dependency map in one place.

---

<a id="artifact-feature-design"></a>
## Feature DESIGN.md

**Path**:
- `architecture/features/feature-{slug}/DESIGN.md`

**Template**:
- [templates/feature-DESIGN.template.md](../templates/feature-DESIGN.template.md)

**Examples**:
- [valid](../examples/requirements/feature-design/valid.md)
- [invalid](../examples/requirements/feature-design/invalid.md)

**Purpose**:
- Specify a single feature in detail (flows, algorithms, technical details, requirements).

**What it is**:
- An executable specification for one feature (FDL flows/algorithms/states + requirements + test scenarios).
- The source of truth for acceptance criteria and edge cases.

**What it is not**:
- Not a system-wide architecture baseline.
- Not an implementation plan.
- Not the code.

**Should contain**:
- Feature context, references, and boundaries.
- FDL content:
  - Actor flows
  - Algorithms
  - States
- Feature requirements, phases, acceptance criteria.
- Test scenarios and edge cases.

**Should not contain**:
- Sprint/task breakdowns.
- System-level type redefinitions (use `architecture/DESIGN.md`).
- Code diffs or code snippets.

**Where SCENARIOS live**:
- Test scenarios belong in the feature design (commonly in the dedicated “Test Scenarios” section).

**Why this helps**:
- **Agent**: executable spec for implementation and traceability checks.
- **Human**: reviewable behavior and edge cases before coding.

**Notes**:
- Prefer keeping feature-level behavior and acceptance criteria here.

---

## Mapping to Common Document Names

FDD does not require you to create BRD/PRD as separate artifacts.

- **BRD/PRD**: typically maps to `architecture/PRD.md` and the requirements/principles part of `architecture/DESIGN.md`.
- **ADR**: maps to `architecture/ADR/**`.
- **SCENARIOS**: live inside feature `DESIGN.md` (feature-level acceptance criteria and edge cases).

---

<a id="templates--examples"></a>
## Templates & Examples

Use templates for **authoritative structure** and examples for **minimal valid content**.

**Templates** (structure source of truth):
- `templates/README.md`: [Template index](../templates/README.md)
- PRD: [template](../templates/PRD.template.md)
- Overall DESIGN: [template](../templates/DESIGN.template.md)
- ADR: [template](../templates/ADR.template.md)
- FEATURES: [template](../templates/FEATURES.template.md)
- Feature DESIGN: [template](../templates/feature-DESIGN.template.md)
- Adapter AGENTS: [template](../templates/adapter-AGENTS.template.md)

**Examples** (minimal “valid/invalid” snapshots):
- Adapter: [valid](../examples/requirements/adapter/valid.md), [invalid](../examples/requirements/adapter/invalid.md)
- PRD: [valid](../examples/requirements/prd/valid.md), [invalid](../examples/requirements/prd/invalid.md)
- Overall DESIGN: [valid](../examples/requirements/overall-design/valid.md), [invalid](../examples/requirements/overall-design/invalid.md)
- ADR: [valid](../examples/requirements/adr/valid.md), [invalid](../examples/requirements/adr/invalid.md)
- FEATURES: [valid](../examples/requirements/features-manifest/valid.md), [invalid](../examples/requirements/features-manifest/invalid.md)
- Feature DESIGN: [valid](../examples/requirements/feature-design/valid.md), [invalid](../examples/requirements/feature-design/invalid.md)

**Real artifacts in this repository (as reference implementations)**:
- PRD: [architecture/PRD.md](../architecture/PRD.md)
- Overall DESIGN: [architecture/DESIGN.md](../architecture/DESIGN.md)
- ADRs: [architecture/ADR/general/](../architecture/ADR/general/)
- Features manifest: [architecture/features/FEATURES.md](../architecture/features/FEATURES.md)
- Example feature (DESIGN):
  - [architecture/features/feature-init-structure/DESIGN.md](../architecture/features/feature-init-structure/DESIGN.md)

---

<a id="validation-deterministic-gate"></a>
## Validation (Deterministic Gate)

FDD assumes you validate artifacts deterministically before moving “up” the chain.

**What to run**:
- `python3 skills/fdd/scripts/fdd.py validate --artifact .` (full project)
- `python3 skills/fdd/scripts/fdd.py validate --artifact {path}` (single artifact)

**What validation catches early**:
- Missing required sections.
- Placeholder markers (`TODO`, `TBD`, etc.).
- Broken cross-references.
- Invalid ID formats.

**Practical interpretation**:
- If validation fails: fix the artifact first, do not proceed to the next layer.

## Why Many Small Artifacts (Not One Big Doc)

- **Avoid conflicts**: each layer has a clear owner and validator.
- **Avoid a monolith**: each doc stays reviewable.
- **Prevent drift**: validation and traceability keep artifacts consistent with each other and with code.
- **Reduce LLM context drift**: smaller, scoped artifacts reduce accidental overwrites and “semantic blending” when an agent holds too much unrelated context.
- **Lower retrieval ambiguity**: search/where-defined/where-used results are cleaner when each concept has one obvious home.
- **Enable deterministic gates**: validators can target a specific artifact kind with stable structure expectations.
- **Minimize blast radius**: a change to one feature plan or ADR does not force rewriting the entire architecture narrative.
- **Preserve abstraction boundaries**: prd vs architecture vs feature behavior vs implementation plan stay separated and auditable.
- **Improve review ergonomics**: diffs are smaller, code review is faster, and regression risk is easier to reason about.
- **Support parallel work**: multiple contributors (or agents) can work on different artifacts without stepping on each other.
