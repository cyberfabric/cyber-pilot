# Cypilot Kit: SDLC (`cypilot-sdlc`)

Agent quick reference.

## What it is

Artifact-first SDLC pipeline (PRD → ADR + DESIGN → DECOMPOSITION → FEATURE → CODE) with templates, checklists, examples, and `{cypilot_path}/.gen/kits/sdlc/artifacts/{KIND}/rules.md` for deterministic validation + traceability.

## Artifact kinds

| Kind | Semantic intent (when to use) | References |
| --- | --- | --- |
| PRD | Product intent: actors + problems + FR/NFR + use cases + success criteria. | `{cypilot_path}/.gen/kits/sdlc/artifacts/PRD/rules.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/PRD/template.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/PRD/checklist.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/PRD/examples/example.md` |
| ADR | Decision log: why an architecture choice was made (context/options/decision/consequences). | `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/rules.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/template.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/checklist.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/examples/example.md` |
| DESIGN | System blueprint: architecture, components, boundaries, interfaces, drivers, principles/constraints. | `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/rules.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/template.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/checklist.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/examples/example.md` |
| DECOMPOSITION | Executable plan: FEATURE list, ordering, dependencies, and coverage links back to PRD/DESIGN. | `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/examples/example.md` |
| FEATURE | Precise behavior + DoD: CDSL flows/algos/states + test scenarios for implementability. | `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`, `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/task-crud.md` |
| CODE | Implementation of FEATURE with optional `@cpt-*` markers and checkbox cascade/coverage validation. | `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`, `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md` |