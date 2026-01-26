---
fdd: true
type: workflow
name: Code
version: 1.0
purpose: Implement code directly from feature design
---

# Implement Code (Directly From Feature Design)

**Type**: Operation  
**Role**: Developer  
**Artifact**: Code files, tests

---

## Prerequisite Checklist

- [ ] Agent has read execution-protocol.md
- [ ] Agent has read workflow-execution.md
- [ ] Agent understands this workflow's purpose

---

## Overview

Implement a feature directly from feature `DESIGN.md`.

This workflow enforces **iterative** design ↔ code synchronization:
- Add instruction-level tags while implementing each step
- Update feature `DESIGN.md` checkboxes and requirement statuses during coding (not only at validation time)

---

ALWAYS open and follow `../requirements/workflow-execution.md` WHEN executing this workflow

## Requirements

**ALWAYS open and follow**:
- `../requirements/feature-design-structure.md` (feature design structure: flows/algos/states/tests with checkboxes)
- `{adapter-directory}/AGENTS.md` (code conventions)

Extract:
- Feature design checkbox semantics (FDL steps, requirement statuses, phases)
- Code conventions from adapter
- Testing requirements from adapter

---

## Prerequisites

**MUST validate**:
- [ ] Feature DESIGN.md exists and validated - validate: Score 100/100 + 100% completeness
- [ ] Adapter exists - validate: Check adapter AGENTS.md (REQUIRED for development)

**If adapter missing**: STOP, run `adapter` workflow first

---

## Steps

### 1. Select Feature

Ask user:
- What is the feature scope?
  - Project-level feature
  - Module-level feature
- Which feature to implement? (feature slug)
- Where is the feature directory?
  - Project-level default: `architecture/features/feature-{slug}/`
  - Module-level example: `src/modules/{module}/architecture/features/feature-{slug}/`
- What is the implementation scope?
  - Full feature
  - Subset of requirements (provide requirement IDs)

Store:
- Feature slug
- Feature directory path
- Scope (full or selected requirement IDs)

### 2. Read Feature Design (Traceability Source)

Open `{feature-dir}/DESIGN.md`.

Extract the authoritative IDs you must keep in sync while coding:
- Flow IDs (Section B)
- Algorithm IDs (Section C)
- State IDs (Section D)
- Requirement IDs + Status/Phases (Section F)
- Test scenario IDs (Section G)

**Rule**: You MUST update these checkboxes and statuses iteratively during implementation (not only during `code-validate`).

### 3. Read Adapter Conventions

Open `{adapter-directory}/AGENTS.md`.

Follow MUST WHEN instructions for:
- Code conventions
- Testing requirements
- Build requirements

### 3.1 Add FDD Tags (Code Traceability)

 **Action**: Tag code with `@fdd-*` markers.

 **Instruction-level traceability (mandatory)**:
 - When implementing a specific FDL step (flow/algo/state/test step) you MUST tag the corresponding code block using:
   - `fdd-{project}-feature-{feature}-[flow|algo|state|test]-{scope-name}:ph-{N}:inst-{local}`
   - The `{scope}` part MUST be the existing ID from DESIGN (do NOT invent a new scope prefix).
   - `{local}` is the local FDL instruction ID from the step line (e.g., `inst-load-raw-events`)

 **Open/close tags (mandatory for instruction tags)**:
 - For every FDL instruction step (`...:ph-{N}:inst-...`), you MUST use paired begin/end tags that wrap non-empty code:
   - `// fdd-begin fdd-...:ph-{N}:inst-...`
   - `// fdd-end   fdd-...:ph-{N}:inst-...`
 - Single-line instruction tags MUST NOT be used.

 **Tag placement rules (by implementation location)**:
 - **No empty blocks**: `fdd-begin`/`fdd-end` MUST NOT be adjacent with no effective code between them.
 - **Begin/end pairing**: Every `fdd-begin ...:inst-...` MUST have a matching `fdd-end ...:inst-...`.
 - **In-function logic**: If the step is implemented in the current function body, wrap the exact code that performs the step.
 - **External middleware / platform / third-party libraries**: If the step is implemented by middleware or external libraries, place the step tag on the integration point (imports and/or registration).

 **Scope tags (required when applicable)**:
 - Flow ID: `@fdd-flow:{flow-id}:ph-{N}` (Section B of DESIGN; phase postfix is mandatory)
 - Algorithm ID: `@fdd-algo:{algo-id}:ph-{N}` (Section C of DESIGN; phase postfix is mandatory)
 - State ID: `@fdd-state:{state-id}:ph-{N}` (Section D of DESIGN; phase postfix is mandatory)
 - Requirement ID: `@fdd-req:{req-id}:ph-{N}` (Section F of DESIGN; phase postfix is mandatory)
 - Test scenario ID: `@fdd-test:{test-id}:ph-{N}` (Section G of DESIGN; phase postfix is mandatory)

 **Tag placement**:
 - At the beginning of new/modified functions, methods, structs, or complex blocks implementing the logic
 - At the beginning of test modules/functions that code test scenarios
 - Prefer multiple tags when a block covers multiple IDs

 ### 3.2 Tag Verification (agent checklist)

 **ALWAYS verify** (before finishing implementation):
 - Search the codebase for ALL IDs from DESIGN (flow/algo/state/req/test)
 - Confirm tags exist in the files that code corresponding logic/tests
 - If any DESIGN ID has no code tag → report as gap and/or add tag

### 4. Implement Work Packages (Iterative)

Choose a work package order based on the feature design:
- Prefer implementing one requirement end-to-end, or
- One flow/algo/state section end-to-end, or
- One phase at a time if the feature design defines phases

Ask user to confirm the proposed order before coding.

**For each work package**:
1. Identify the exact design items to code (flows/algos/states/requirements/tests)
2. Implement according to adapter conventions
3. Add / update **instruction-level** tags (`...:ph-{N}:inst-...`) while implementing the exact step
4. Run the work package validation (tests, build, linters as required by adapter)
5. Update traceability state (MANDATORY mini-gate):
   - Update feature DESIGN.md (see Step 5) so design checkboxes and statuses reflect the work just done
6. Proceed to next work package

**After each work package**:
- Show progress: Work package {X}/{total} complete
- Ask: Continue to next work package? [yes/pause]

### 5. Sync Feature DESIGN.md (MANDATORY After Each Work Package)

**Goal**: Keep design checkboxes and requirement statuses aligned with code as you implement.

**Input**:
- The design IDs you implemented in code (flows/algos/states/req/tests)
- The instruction-level tags you added (`...:ph-{N}:inst-{local}`)

**Procedure**:
1. For each `...:ph-{N}:inst-{local}` you implemented:
   - Locate the owning scope entry in feature DESIGN.md by its base ID (flow/algo/state/test).
   - Within that scope entry, find the matching FDL step line containing `ph-{N}` and `inst-{local}`.
   - Mark its checkbox `- [ ]` → `- [x]`.
2. For each requirement ID implemented by this work package:
   - If this is the first completed work package for the requirement: set requirement `**Status**` to `🔄 IN_PROGRESS`.
   - Mark the corresponding `**Phases**` checkbox(es) as implemented when their instruction steps are complete.
   - When all phases (and required instruction steps) are complete: set requirement `**Status**` to `✅ IMPLEMENTED`.
3. For each test scenario ID affected:
   - Do NOT mark as implemented until the test exists and passes.

**Consistency rule**:
- Only mark a design checkbox as `[x]` if the corresponding code exists and is tagged.
- If code is tagged but design is not checked, you MUST update the design immediately (do not defer).

### 6. Run Tests

Run the project test suite.

After tests pass:
- Mark affected test scenario IDs in feature DESIGN.md as completed (`- [ ]` → `- [x]`) when their tests exist and pass.

---

## Validation

After implementing, run: `code-validate`

Expected:
- All feature code compiles/runs
- All tests pass (including test scenarios from DESIGN.md)
- All requirements implemented for the chosen scope

---

## Validation Criteria

- [ ] All workflow steps completed
- [ ] Output artifacts are valid

---

## Validation Checklist

- [ ] All prerequisites were met
- [ ] All steps were executed in order

---

## Next Steps

**If implementation is incomplete**:
- Continue this workflow (next work package)

**If implementation is complete**:
- Run `code-validate` to validate entire feature
- If validation passes: mark feature as IMPLEMENTED in FEATURES.md and {feature}/DESIGN.md
- If validation fails: Fix code, re-validate
