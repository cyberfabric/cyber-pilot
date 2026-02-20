# Cypilot Kit: SDLC (`cypilot-sdlc`)

Agent quick reference.

## What it is

Artifact-first SDLC pipeline (PRD → ADR + DESIGN → DECOMPOSITION → FEATURE → CODE) with templates, checklists, examples, and `rules.md` for deterministic validation + traceability.

## Artifact kinds

| Kind | Semantic intent (when to use) | References |
| --- | --- | --- |
| PRD | Product intent: actors + problems + FR/NFR + use cases + success criteria. | `artifacts/PRD/rules.md`, `artifacts/PRD/template.md`, `artifacts/PRD/checklist.md`, `artifacts/PRD/examples/example.md` |
| ADR | Decision log: why an architecture choice was made (context/options/decision/consequences). | `artifacts/ADR/rules.md`, `artifacts/ADR/template.md`, `artifacts/ADR/checklist.md`, `artifacts/ADR/examples/example.md` |
| DESIGN | System blueprint: architecture, components, boundaries, interfaces, drivers, principles/constraints. | `artifacts/DESIGN/rules.md`, `artifacts/DESIGN/template.md`, `artifacts/DESIGN/checklist.md`, `artifacts/DESIGN/examples/example.md` |
| DECOMPOSITION | Executable plan: FEATURE list, ordering, dependencies, and coverage links back to PRD/DESIGN. | `artifacts/DECOMPOSITION/rules.md`, `artifacts/DECOMPOSITION/template.md`, `artifacts/DECOMPOSITION/checklist.md`, `artifacts/DECOMPOSITION/examples/example.md` |
| FEATURE | Precise behavior + DoD: CDSL flows/algos/states + test scenarios for implementability. | `artifacts/FEATURE/rules.md`, `artifacts/FEATURE/template.md`, `artifacts/FEATURE/checklist.md`, `artifacts/FEATURE/examples/task-crud.md` |
| CODE | Implementation of FEATURE with optional `@cpt-*` markers and checkbox cascade/coverage validation. | `codebase/rules.md`, `codebase/checklist.md` |