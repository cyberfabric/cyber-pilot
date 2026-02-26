`@cpt:blueprint`
```toml
version = 1
kit = "sdlc"
codebase = true
```
`@/cpt:blueprint`

`@cpt:skill`
```markdown
### CODE Commands
- `cypilot validate --artifact <code-path>` — validate code traceability and quality
- `cypilot where-defined <id>` — find where an ID is defined in artifacts
- `cypilot where-used <id>` — find where an ID is referenced in code via `@cpt-*` markers
### CODE Workflows
- **Generate CODE**: implement FEATURE design with optional `@cpt-*` traceability markers
- **Analyze CODE**: validate implementation coverage, traceability, tests, and quality
```
`@/cpt:skill`

`@cpt:rules`
```toml
[prerequisites]
sections = ["load_dependencies"]

[requirements]
sections = ["structural", "traceability", "checkbox_cascade", "versioning", "engineering", "quality"]

[tasks]
phases = ["setup", "implementation", "markers", "sync_feature", "quality_check", "tag_verification"]

[validation]
sections = ["coverage", "traceability", "tests", "build_lint", "test_execution", "code_quality", "logic_consistency", "semantic_review"]

[next_steps]
sections = ["after_success", "after_issues", "no_design"]
```
`@/cpt:rules`

`@cpt:rule`
```toml
kind = "prerequisites"
section = "load_dependencies"
```
```markdown
- [ ] Read adapter `AGENTS.md` for code conventions
- [ ] Load source artifact/description (FEATURE preferred)
- [ ] Load `checklist.md` for quality guidance
- [ ] Load `{cypilot_path}/.core/requirements/code-checklist.md` for generic code quality checks
- [ ] If FEATURE source: identify all IDs with `to_code="true"` attribute
- [ ] Determine Traceability Mode (FULL vs DOCS-ONLY)
- [ ] If Traceability Mode FULL: load `{cypilot_path}/.core/architecture/specs/traceability.md`
- [ ] Load `{cypilot_path}/config/kits/sdlc/constraints.toml` for kit-level constraints
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "requirements"
section = "structural"
```
```markdown
- [ ] Code implements FEATURE design requirements
- [ ] Code follows project conventions from adapter
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "requirements"
section = "traceability"
```
```markdown
**Reference**: `{cypilot_path}/.core/architecture/specs/traceability.md` for full specification

- [ ] Traceability Mode determined per feature (FULL vs DOCS-ONLY)
- [ ] If Mode ON: markers follow syntax (`@cpt-*`, `@cpt-begin`/`@cpt-end`)
- [ ] If Mode ON: all `to_code="true"` IDs have markers
- [ ] If Mode ON: every implemented CDSL instruction has paired block markers in code
- [ ] If Mode ON: no orphaned/stale markers
- [ ] If Mode ON: design checkboxes synced with code
- [ ] If Mode OFF: no Cypilot markers in code
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "requirements"
section = "checkbox_cascade"
```
```markdown
**Full Cascade Chain**:
```
CODE markers exist
    ↓
FEATURE: flow/algo/state/dod IDs → [x]
    ↓
DECOMPOSITION: feature entry [x]
    ↓
PRD/DESIGN: referenced IDs [x] when ALL downstream refs [x]
```

**Consistency rules (MANDATORY)**:
- [ ] Never mark CDSL instruction `[x]` unless corresponding code block markers exist
- [ ] Never add code block marker pair unless corresponding CDSL instruction exists in design
- [ ] Parent ID checkbox state MUST be consistent with all nested task-tracked items
- [ ] Never mark a reference as `[x]` if its definition is still `[ ]`
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "requirements"
section = "versioning"
```
```markdown
- [ ] When design ID versioned (`-v2`): update code markers to match
- [ ] Marker format with version: `@cpt-flow:{cpt-id}-v2:p{N}`
- [ ] Migration: update all markers when design version increments
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "requirements"
section = "engineering"
```
```markdown
- [ ] **TDD**: Write failing test first, implement minimal code to pass, then refactor
- [ ] **SOLID**: SRP, OCP, LSP, ISP, DIP
- [ ] **DRY**: Remove duplication by extracting shared logic
- [ ] **KISS**: Prefer simplest correct solution
- [ ] **YAGNI**: No specs/abstractions not required by current design scope
- [ ] **Refactoring discipline**: Refactor only after tests pass
- [ ] **Testability**: Structure code so core logic is testable without heavy integration
- [ ] **Error handling**: Fail explicitly with clear errors
- [ ] **Observability**: Log meaningful events at integration boundaries
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "requirements"
section = "quality"
```
```markdown
**Reference**: `checklist.md` for detailed criteria

- [ ] Code passes quality checklist
- [ ] Functions/methods are appropriately sized
- [ ] Error handling is consistent
- [ ] Tests cover implemented requirements
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "tasks"
section = "setup"
```
```markdown
**Resolve Source** (priority order):
1. FEATURE design (registered) — Traceability FULL possible
2. Other Cypilot artifact (PRD/DESIGN/ADR) — DOCS-ONLY
3. User-provided description — DOCS-ONLY
4. Prompt only — DOCS-ONLY
5. None — suggest `/cypilot-generate FEATURE` first

**Load Context**:
- [ ] Read adapter `AGENTS.md` for code conventions
- [ ] Load source artifact/description
- [ ] Load `checklist.md` for quality guidance
- [ ] Determine Traceability Mode
- [ ] Plan implementation order
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "tasks"
section = "implementation"
```
```markdown
**For each work package:**
1. Identify exact design items to code (flows/algos/states/requirements/tests)
2. Implement according to adapter conventions
3. If Traceability Mode ON: add instruction-level tags while implementing
4. Run work package validation (tests, build, linters per adapter)
5. If Traceability Mode ON: update FEATURE.md checkboxes
6. Proceed to next work package
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "tasks"
section = "markers"
```
```markdown
**Traceability Mode ON only.**

Apply markers per feature:
- Scope markers: `@cpt-{kind}:{cpt-id}:p{N}` at function/class entry
- Block markers: `@cpt-begin:{cpt-id}:p{N}:inst-{local}` / `@cpt-end:...` wrapping CDSL steps
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "tasks"
section = "sync_feature"
```
```markdown
**Traceability Mode ON only.**

After each work package, sync checkboxes:
1. Mark implemented CDSL steps `[x]` in FEATURE
2. When all steps done → mark flow/algo/state/dod `[x]` in FEATURE
3. When all IDs done → mark feature entry `[x]` in DECOMPOSITION
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "tasks"
section = "quality_check"
```
```markdown
- [ ] Self-review against `checklist.md`
- [ ] If Traceability Mode ON: verify all `to_code="true"` IDs have markers
- [ ] If Traceability Mode ON: ensure no orphaned markers
- [ ] Run tests to verify implementation
- [ ] Verify engineering best practices followed
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "tasks"
section = "tag_verification"
```
```markdown
**Traceability Mode ON only.**

- [ ] Search codebase for ALL IDs from FEATURE (flow/algo/state/dod)
- [ ] Confirm tags exist in files that implement corresponding logic/tests
- [ ] If any FEATURE ID has no code tag → report as gap and/or add tag
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "validation"
section = "coverage"
```
```markdown
- [ ] Code files exist and contain implementation
- [ ] Code is not placeholder/stub (no TODO/FIXME/unimplemented!)
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "validation"
section = "traceability"
```
```markdown
**Mode ON only.** Reference: `{cypilot_path}/.core/architecture/specs/traceability.md`

- [ ] Marker format valid
- [ ] All begin/end pairs matched
- [ ] No empty blocks
- [ ] All `to_code="true"` IDs have markers
- [ ] No orphaned/stale markers
- [ ] Design checkboxes synced with code markers
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "validation"
section = "tests"
```
```markdown
- [ ] Test file exists for each test scenario from design
- [ ] Test contains scenario ID in comment for traceability
- [ ] Test is NOT ignored without justification
- [ ] Test actually validates scenario behavior
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "validation"
section = "build_lint"
```
```markdown
- [ ] Build succeeds, no compilation errors
- [ ] Linter passes, no linter errors
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "validation"
section = "test_execution"
```
```markdown
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All e2e tests pass (if applicable)
- [ ] Coverage meets adapter requirements
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "validation"
section = "code_quality"
```
```markdown
- [ ] No TODO/FIXME/XXX/HACK in domain/service layers
- [ ] No unimplemented!/todo! in business logic
- [ ] No bare unwrap() or panic in production code
- [ ] TDD: New/changed behavior covered by tests
- [ ] SOLID: Responsibilities separated; dependencies injectable
- [ ] DRY: No copy-paste duplication
- [ ] KISS: No unnecessary complexity
- [ ] YAGNI: No speculative abstractions
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "validation"
section = "logic_consistency"
```
```markdown
- [ ] Code logic matches requirement specification (no contradictions)
- [ ] Flow steps executed in correct order
- [ ] Algorithm logic matches design specification
- [ ] State transitions match design state machine
- [ ] Error handling matches design error specifications
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "validation"
section = "semantic_review"
```
```markdown
Expert panel review after producing validation output.

| Change Size | Review Mode | Experts |
|-------------|-------------|---------|
| <50 LOC | Abbreviated | Developer + 1 relevant expert |
| 50-200 LOC | Standard | Developer, QA, Security, Architect |
| >200 LOC or architectural | Full | All experts |
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "next_steps"
section = "after_success"
```
```markdown
- [ ] Feature complete → update feature status to IMPLEMENTED in DECOMPOSITION
- [ ] All features done → `/cypilot-analyze DESIGN` — validate overall design completion
- [ ] New feature needed → `/cypilot-generate FEATURE` — design next feature
- [ ] Want expert review only → `/cypilot-analyze semantic` — semantic validation
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "next_steps"
section = "after_issues"
```
```markdown
- [ ] Design mismatch → `/cypilot-generate FEATURE` — update feature design
- [ ] Missing tests → continue `/cypilot-generate CODE` — add tests
- [ ] Code quality issues → continue `/cypilot-generate CODE` — refactor
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "next_steps"
section = "no_design"
```
```markdown
- [ ] Implementing new feature → `/cypilot-generate FEATURE` first
- [ ] Implementing from PRD → `/cypilot-generate DESIGN` then DECOMPOSITION
- [ ] Quick prototype → proceed without traceability, suggest FEATURE later
```
`@/cpt:rule`

`@cpt:checklist`
```toml
group_by_kind = false

postamble = """---

Use `{cypilot_path}/.core/requirements/code-checklist.md` for all generic code quality checks."""

[severity]
levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

[review]
priority = ["SEM"]

[[domain]]
abbr = "SEM"
name = "Semantic Alignment"
header = "Semantic Alignment (SEM)"
preamble = "These checks are **Cypilot SDLC-specific** because they require Cypilot artifacts (Feature design, Overall Design, ADRs, PRD/DESIGN coverage) and/or Cypilot markers."
standards = []
```
````markdown
# Cypilot SDLC Code Checklist (Kit-Specific)

ALWAYS open and follow `{cypilot_path}/.core/requirements/code-checklist.md` FIRST

**Artifact**: Code Implementation (Cypilot SDLC)
**Version**: 1.0
**Purpose**: Kit-specific checks that require Cypilot SDLC artifacts (PRD/DESIGN/DECOMPOSITION/FEATURE/ADR) and/or Cypilot traceability.

---

## Table of Contents

1. [Traceability Preconditions](#traceability-preconditions)
2. [Semantic Alignment (SEM)](#semantic-alignment-sem)

---

## Traceability Preconditions

Before running the SDLC-specific checks:

- [ ] Determine traceability mode from `artifacts.toml` for the relevant system/artifact: `FULL` vs `DOCS-ONLY`
- [ ] If `FULL`: identify the design source(s) to trace (Feature design is preferred)
- [ ] If `DOCS-ONLY`: skip traceability requirements and validate semantics against provided design sources
````
`@/cpt:checklist`

`@cpt:check`
```toml
id = "SEM-CODE-001"
domain = "SEM"
title = "Resolve Design Sources"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Resolve Feature design via `@cpt-*` markers using the `cypilot where-defined` or `cypilot where-used` skill
- [ ] If no `@cpt-*` markers exist, ask the user to provide the Feature design location before proceeding
- [ ] If the user is unsure, search the repository for candidate feature designs and present options for user selection
- [ ] Resolve Overall Design by following references from the Feature design (or ask the user for the design path)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEM-CODE-002"
domain = "SEM"
title = "Spec Context Semantics"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Confirm code behavior aligns with the Feature Overview, Purpose, and key assumptions
- [ ] Verify all referenced actors are represented by actual interfaces, entrypoints, or roles in code
- [ ] Ensure referenced ADRs and related specs do not conflict with current implementation choices
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEM-CODE-003"
domain = "SEM"
title = "Spec Flows Semantics"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Verify each implemented flow follows the ordered steps, triggers, and outcomes in Actor Flows
- [ ] Confirm conditionals, branching, and return paths match the flow logic
- [ ] Validate all flow steps marked with IDs are implemented and traceable
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEM-CODE-004"
domain = "SEM"
title = "Algorithms Semantics"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Validate algorithm steps match the Feature design algorithms (inputs, rules, outputs)
- [ ] Ensure data transformations and calculations match the described business rules
- [ ] Confirm loop/iteration behavior and validation rules align with algorithm steps
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEM-CODE-005"
domain = "SEM"
title = "State Semantics"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Confirm state transitions match the Feature design state machine
- [ ] Verify triggers and guards for transitions match defined conditions
- [ ] Ensure invalid transitions are prevented or handled explicitly
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEM-CODE-006"
domain = "SEM"
title = "Definition of Done Semantics"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Verify each requirement in Definition of Done is implemented and testable
- [ ] Confirm implementation details (API, DB, domain entities) match the requirement section
- [ ] Validate requirement mappings to flows and algorithms are satisfied
- [ ] Ensure PRD coverage (FR/NFR) is preserved in implementation outcomes
- [ ] Ensure Design coverage (principles, constraints, components, sequences, db tables) is satisfied
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEM-CODE-007"
domain = "SEM"
title = "Overall Design Consistency"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Confirm architecture vision and system boundaries are respected
- [ ] Validate architecture drivers (FR/NFR) are still satisfied by implementation
- [ ] Verify ADR decisions are reflected in code choices or explicitly overridden
- [ ] Confirm principles and constraints are enforced in implementation
- [ ] Validate domain model entities and invariants are respected by code
- [ ] Confirm component responsibilities, boundaries, and dependencies match the component model
- [ ] Validate API contracts and integration boundaries are honored
- [ ] Verify interactions and sequences are implemented as described
- [ ] Ensure database schemas, constraints, and access patterns align with design
- [ ] Confirm topology and tech stack choices are not contradicted
- [ ] Document any deviation with a rationale and approval
```
`@/cpt:check`
