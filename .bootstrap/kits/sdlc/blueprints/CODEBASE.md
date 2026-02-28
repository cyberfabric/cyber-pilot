> **`@cpt:blueprint`** — Blueprint metadata: artifact kind, kit slug, version. Internal; not output to any file.

`@cpt:blueprint`
```toml
# Blueprint version (semver)
version = 1
# Kit slug this blueprint belongs to
kit = "sdlc"
codebase = true
toc = false
```
`@/cpt:blueprint`

> **`@cpt:skill`** — Skill content. Agent-facing navigation and instructions. Output: `.gen/kits/{slug}/SKILL.md`.

`@cpt:skill`
```markdown
### CODE Commands
- `cypilot validate --artifact <code-path>` — validate code traceability and quality
- `cypilot where-defined --id <id>` — find where an ID is defined in artifacts
- `cypilot where-used --id <id>` — find where an ID is referenced in code via `@cpt-*` markers
### CODE Workflows
- **Generate CODE**: implement FEATURE design with optional `@cpt-*` traceability markers
- **Analyze CODE**: validate implementation coverage, traceability, tests, and quality
```
`@/cpt:skill`

> **`@cpt:rules`** — Rules skeleton. Defines section structure (prerequisites, requirements, tasks, validation, etc.) for `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rules`
```toml
# Prerequisite steps (load dependencies, read configs)
[prerequisites]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["load_dependencies"]

# Requirement sections (structural, semantic, constraints, etc.)
[requirements]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["structural", "traceability", "checkbox_cascade", "versioning", "engineering", "quality"]

# Task phases — step-by-step workflow for creating the artifact
[tasks]
# Ordered list of phase keys (each needs a matching @cpt:rule block)
phases = ["setup", "implementation", "markers", "sync_feature", "quality_check", "tag_verification"]
# Display names for non-obvious task phase keys
[tasks.names]
implementation = "Implementation (Work Packages)"
markers = "Cypilot Markers (Traceability Mode ON only)"
sync_feature = "Sync FEATURE (Traceability Mode ON only)"
tag_verification = "Tag Verification (Traceability Mode ON only)"

# Validation phases — ordered checks run after artifact is written
[validation]
# Ordered list of phase keys (each needs a matching @cpt:rule block)
phases = ["coverage", "traceability", "tests", "build_lint", "test_execution", "code_quality", "logic_consistency", "semantic_review"]
# Display names for non-obvious validation phase keys
[validation.names]
coverage = "Implementation Coverage"
traceability = "Traceability Validation (Mode ON only)"
tests = "Test Scenarios Validation"
build_lint = "Build and Lint Validation"
test_execution = "Test Execution"
code_quality = "Code Quality Validation"
logic_consistency = "Code Logic Consistency with Design"
semantic_review = "Semantic Expert Review (Always)"

# Next steps — recommended actions after completing the artifact
[next_steps]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["after_success", "after_issues", "no_design"]
```
`@/cpt:rules`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "prerequisites"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "load_dependencies"
```
```markdown
- [ ] Read project `AGENTS.md` for code conventions
- [ ] Load source artifact/description (FEATURE preferred)
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md` for quality guidance
- [ ] Load `{cypilot_path}/.core/requirements/code-checklist.md` for generic code quality checks
- [ ] If FEATURE source: identify all IDs with `to_code="true"` attribute
- [ ] Determine Traceability Mode (FULL vs DOCS-ONLY)
- [ ] If Traceability Mode FULL: load `{cypilot_path}/.core/architecture/specs/traceability.md`
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/constraints.toml` for kit-level constraints

**Source** (one of, in priority order):
1. FEATURE design — registered artifact with `to_code="true"` IDs
2. Other Cypilot artifact — PRD, DESIGN, ADR, DECOMPOSITION
3. Similar content — user-provided description, feature, or requirements
4. Prompt only — direct user instructions

**ALWAYS read** the FEATURE artifact being implemented (the source of `to_code="true"` IDs). The FEATURE contains flows, algorithms, states, and definition-of-done tasks that define what code must do.

**ALWAYS read** the system's DESIGN artifact (if registered in `artifacts.toml`) to understand overall architecture, components, principles, and constraints before implementing code.
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "structural"
```
```markdown
- [ ] Code implements FEATURE design requirements
- [ ] Code follows project conventions from config
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "traceability"
```
```markdown
**Reference**: `{cypilot_path}/.core/architecture/specs/traceability.md` for full specification

- [ ] Traceability Mode determined per feature (FULL vs DOCS-ONLY)
- [ ] If Mode ON: markers follow feature syntax (`@cpt-*`, `@cpt-begin`/`@cpt-end`)
- [ ] If Mode ON: all `to_code="true"` IDs have markers
- [ ] If Mode ON: every implemented CDSL instruction (`[x] ... \`inst-*\``) has a paired `@cpt-begin/.../@cpt-end` block marker in code
- [ ] If Mode ON: no orphaned/stale markers
- [ ] If Mode ON: design checkboxes synced with code
- [ ] If Mode OFF: no Cypilot markers in code
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "checkbox_cascade"
```
````markdown
CODE implementation triggers upstream checkbox updates through markers:

| Code Marker | FEATURE ID | Upstream Effect |
|-------------|-----------|-----------------|
| `@cpt-flow:{cpt-id}:p{N}` | kind: `flow` | When all pN markers exist → check `flow` ID in FEATURE |
| `@cpt-algo:{cpt-id}:p{N}` | kind: `algo` | When all pN markers exist → check `algo` ID in FEATURE |
| `@cpt-state:{cpt-id}:p{N}` | kind: `state` | When all pN markers exist → check `state` ID in FEATURE |
| `@cpt-dod:{cpt-id}:p{N}` | kind: `dod` | When all pN markers exist + evidence complete → check `dod` ID in FEATURE |

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

**When to Update Upstream Checkboxes**:
1. **After implementing CDSL instruction**: add block markers, mark step `[x]` in FEATURE
2. **After completing flow/algo/state/dod**: all steps `[x]` → mark ID `[x]` in FEATURE
3. **After completing FEATURE**: all IDs `[x]` → mark feature entry `[x]` in DECOMPOSITION
4. **After DECOMPOSITION updated**: check if all referenced IDs are `[x]` → mark in PRD/DESIGN

**Consistency rules (MANDATORY)**:
- [ ] Never mark CDSL instruction `[x]` unless corresponding code block markers exist and wrap non-empty implementation code
- [ ] Never add code block marker pair unless corresponding CDSL instruction exists in design (add it first if missing)
- [ ] Parent ID checkbox state MUST be consistent with all nested task-tracked items within its scope (as determined by heading boundaries)
- [ ] Task-tracked items include:
  - ID definitions with a task checkbox (e.g. `- [ ] p1 - **ID**: cpt-...`)
  - Task-checkbox references inside content (e.g. `- [ ] p1 - cpt-...`)
- [ ] If parent ID is `[x]` then ALL nested task-tracked items within its scope MUST be `[x]`
- [ ] If ALL nested task-tracked items within its scope are `[x]` then parent ID MUST be `[x]`
- [ ] Never mark a reference as `[x]` if its definition is still `[ ]` (cross-artifact consistency is validated)

**Validation Checks**:
- `cypilot validate` will warn if code marker exists but FEATURE checkbox is `[ ]`
- `cypilot validate` will warn if FEATURE checkbox is `[x]` but code marker is missing
- `cypilot validate` will report coverage: N% of FEATURE IDs have code markers
````
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "versioning"
```
```markdown
- [ ] When design ID versioned (`-v2`): update code markers to match
- [ ] Marker format with version: `@cpt-flow:{cpt-id}-v2:p{N}`
- [ ] Migration: update all markers when design version increments
- [ ] Keep old markers commented during transition (optional)
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "engineering"
```
```markdown
- [ ] **TDD**: Write failing test first, implement minimal code to pass, then refactor
- [ ] **SOLID**:
  - Single Responsibility: Each module/function focused on one reason to change
  - Open/Closed: Extend behavior via composition/configuration, not editing unrelated logic
  - Liskov Substitution: Implementations honor interface contract and invariants
  - Interface Segregation: Prefer small, purpose-driven interfaces over broad ones
  - Dependency Inversion: Depend on abstractions; inject dependencies for testability
- [ ] **DRY**: Remove duplication by extracting shared logic with clear ownership
- [ ] **KISS**: Prefer simplest correct solution matching design and project conventions
- [ ] **YAGNI**: No specs/abstractions not required by current design scope
- [ ] **Refactoring discipline**: Refactor only after tests pass; keep behavior unchanged
- [ ] **Testability**: Structure code so core logic is testable without heavy integration
- [ ] **Error handling**: Fail explicitly with clear errors; never silently ignore failures
- [ ] **Observability**: Log meaningful events at integration boundaries (no secrets)
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "quality"
```
```markdown
**Reference**: `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md` for detailed criteria

- [ ] Code passes quality checklist
- [ ] Functions/methods are appropriately sized
- [ ] Error handling is consistent
- [ ] Tests cover implemented requirements
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
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
- [ ] Read project `AGENTS.md` for code conventions
- [ ] Load source artifact/description
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md` for quality guidance
- [ ] Determine Traceability Mode
- [ ] Plan implementation order
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "implementation"
```
```markdown
**For each work package:**
1. Identify exact design items to code (flows/algos/states/requirements/tests)
2. Implement according to project conventions
3. If Traceability Mode ON: add `@cpt-begin`/`@cpt-end` markers **per CDSL instruction** while implementing — wrap only the specific lines that implement each instruction, not entire functions
4. Run work package validation (tests, build, linters per project config)
5. If Traceability Mode ON: update FEATURE.md checkboxes
6. Proceed to next work package
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "markers"
```
````markdown
**Traceability Mode ON only.**

Apply markers per feature:
- **Scope markers**: `@cpt-{kind}:{cpt-id}:p{N}` — single-line, at function/class entry point
- **Block markers**: `@cpt-begin:{cpt-id}:p{N}:inst-{local}` / `@cpt-end:...` — paired, wrapping **only the specific lines** that implement one CDSL instruction

**Granularity rules (MANDATORY)**:
1. Each `@cpt-begin`/`@cpt-end` pair wraps the **smallest code fragment** that implements its CDSL instruction
2. When a function implements multiple CDSL instructions, place **separate** begin/end pairs for each instruction inside the function body
3. Place markers as **close to the implementing code as possible** — directly above/below the relevant lines
4. Do NOT wrap an entire function body with a single begin/end pair when the function implements multiple instructions

**Correct** — each instruction wrapped individually:
```python
# @cpt-algo:cpt-system-algo-process:p1
def process_data(items):
    # @cpt-begin:cpt-system-algo-process:p1:inst-validate
    if not items:
        raise ValueError("Empty input")
    # @cpt-end:cpt-system-algo-process:p1:inst-validate

    # @cpt-begin:cpt-system-algo-process:p1:inst-transform
    result = [transform(item) for item in items]
    # @cpt-end:cpt-system-algo-process:p1:inst-transform

    # @cpt-begin:cpt-system-algo-process:p1:inst-return-result
    return result
    # @cpt-end:cpt-system-algo-process:p1:inst-return-result
```

**WRONG** — entire function wrapped with one pair (loses per-instruction traceability):
```python
# @cpt-begin:cpt-system-algo-process:p1:inst-validate
def process_data(items):
    if not items:
        raise ValueError("Empty input")
    result = [transform(item) for item in items]
    return result
# @cpt-end:cpt-system-algo-process:p1:inst-validate
```
````
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "sync_feature"
```
```markdown
**Traceability Mode ON only.**

After each work package, sync checkboxes:
1. Mark implemented CDSL steps `[x]` in FEATURE
2. When all steps done → mark flow/algo/state/dod `[x]` in FEATURE
3. When all IDs done → mark feature entry `[x]` in DECOMPOSITION
4. Update feature status: `⏳ PLANNED` → `🔄 IN_PROGRESS` → `✅ IMPLEMENTED`
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "quality_check"
```
```markdown
- [ ] Self-review against `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md`
- [ ] If Traceability Mode ON: verify all `to_code="true"` IDs have markers
- [ ] If Traceability Mode ON: ensure no orphaned markers
- [ ] Run tests to verify implementation
- [ ] Verify engineering best practices followed
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "tag_verification"
```
```markdown
**Traceability Mode ON only.**

- [ ] Search codebase for ALL IDs from FEATURE (flow/algo/state/dod)
- [ ] Confirm tags exist in files that implement corresponding logic/tests
- [ ] If any FEATURE ID has no code tag → report as gap and/or add tag
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "coverage"
```
```markdown
- [ ] Code files exist and contain implementation
- [ ] Code is not placeholder/stub (no TODO/FIXME/unimplemented!)
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "tests"
```
```markdown
- [ ] Test file exists for each test scenario from design
- [ ] Test contains scenario ID in comment for traceability
- [ ] Test is NOT ignored without justification
- [ ] Test actually validates scenario behavior
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "build_lint"
```
````markdown
- [ ] Build succeeds, no compilation errors
- [ ] Linter passes, no linter errors

**Report format**:
```
Code Quality Report
═══════════════════
Build: PASS/FAIL
Lint: PASS/FAIL
Tests: X/Y passed
Coverage: N%
Checklist: PASS/FAIL (N issues)
Issues:
- [SEVERITY] CHECKLIST-ID: Description
Logic Consistency: PASS/FAIL
- CRITICAL divergences: [...]
- MINOR divergences: [...]
```
````
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "test_execution"
```
```markdown
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All e2e tests pass (if applicable)
- [ ] Coverage meets project requirements
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "logic_consistency"
```
```markdown
**For each requirement marked IMPLEMENTED:**
- [ ] Read requirement specification
- [ ] Locate implementing code via @cpt-dod tags
- [ ] Verify code logic matches requirement (no contradictions)
- [ ] Verify no skipped mandatory steps
- [ ] Verify error handling matches design error specifications

**For each flow marked implemented:**
- [ ] All flow steps executed in correct order
- [ ] No steps bypassed that would change behavior
- [ ] Conditional logic matches design conditions
- [ ] Error paths match design error handling

**For each algorithm marked implemented:**
- [ ] Performance characteristics match design (O(n), O(1), etc.)
- [ ] Edge cases handled as designed
- [ ] No logic shortcuts that violate design constraints
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "semantic_review"
```
````markdown
Run expert panel review after producing validation output.

**Review Scope Selection**:

| Change Size | Review Mode | Experts |
|-------------|-------------|--------|
| <50 LOC, single concern | Abbreviated | Developer + 1 relevant expert |
| 50-200 LOC, multiple concerns | Standard | Developer, QA, Security, Architect |
| >200 LOC or architectural | Full | All 8 experts |

**Abbreviated Review** (for small, focused changes):
1. Developer reviews code quality and design alignment
2. Select ONE additional expert based on change type
3. Skip remaining experts with note: `Abbreviated review: {N} LOC, single concern`

**Full Expert Panel**: Developer, QA Engineer, Security Expert, Performance Engineer, DevOps Engineer, Architect, Monitoring Engineer, Database Architect/Data Engineer

**For EACH expert:**
1. Adopt role (write: `Role assumed: {expert}`)
2. Review actual code and tests in validation scope
3. If design artifact available: evaluate design-to-code alignment
4. Identify issues (contradictions, missing behavior, unclear intent, unnecessary complexity, missing non-functional concerns)
5. Provide concrete proposals (what to remove, add, rewrite)
6. Propose corrective workflow: `feature`, `design`, or `code`

**Expert review output format:**
```
**Review status**: COMPLETED
**Reviewed artifact**: Code ({scope})
- **Role assumed**: {expert}
- **Checklist completed**: YES
- **Findings**:
- **Proposed edits**:
**Recommended corrective workflow**: {feature | design | code}
```

**PASS only if:**
- Build/lint/tests pass per project config
- Coverage meets project requirements
- No CRITICAL divergences between code and design
- If Traceability Mode ON: required tags present and properly paired
````
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "next_steps"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "after_success"
```
```markdown
- [ ] Feature complete → update feature status to IMPLEMENTED in DECOMPOSITION
- [ ] All features done → `/cypilot-analyze DESIGN` — validate overall design completion
- [ ] New feature needed → `/cypilot-generate FEATURE` — design next feature
- [ ] Want expert review only → `/cypilot-analyze semantic` — semantic validation
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "next_steps"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "after_issues"
```
```markdown
- [ ] Design mismatch → `/cypilot-generate FEATURE` — update feature design
- [ ] Missing tests → continue `/cypilot-generate CODE` — add tests
- [ ] Code quality issues → continue `/cypilot-generate CODE` — refactor
```
`@/cpt:rule`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/codebase/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "next_steps"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "no_design"
```
```markdown
- [ ] Implementing new feature → `/cypilot-generate FEATURE` first
- [ ] Implementing from PRD → `/cypilot-generate DESIGN` then DECOMPOSITION
- [ ] Quick prototype → proceed without traceability, suggest FEATURE later
```
`@/cpt:rule`

> **`@cpt:checklist`** — Checklist preamble. Static markdown placed at the top of `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md` (standards, prerequisites, severity dictionary).

`@cpt:checklist`
```toml
group_by_kind = false

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

> **`@cpt:checklist_epilogue`** — Checklist epilogue. Static markdown appended at the end of `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md`.

`@cpt:checklist_epilogue`
````markdown
---

Use `{cypilot_path}/.core/requirements/code-checklist.md` for all generic code quality checks.
````
`@/cpt:checklist_epilogue`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEM-CODE-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEM"
# Human-readable check title
title = "Resolve Design Sources"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Resolve Feature design via `@cpt-*` markers using the `cypilot where-defined` or `cypilot where-used` skill
- [ ] If no `@cpt-*` markers exist, ask the user to provide the Feature design location before proceeding
- [ ] If the user is unsure, search the repository for candidate feature designs and present options for user selection
- [ ] Resolve Overall Design by following references from the Feature design (or ask the user for the design path)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEM-CODE-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEM"
# Human-readable check title
title = "Spec Context Semantics"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Confirm code behavior aligns with the Feature Overview, Purpose, and key assumptions
- [ ] Verify all referenced actors are represented by actual interfaces, entrypoints, or roles in code
- [ ] Ensure referenced ADRs and related specs do not conflict with current implementation choices
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEM-CODE-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEM"
# Human-readable check title
title = "Spec Flows Semantics"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Verify each implemented flow follows the ordered steps, triggers, and outcomes in Actor Flows
- [ ] Confirm conditionals, branching, and return paths match the flow logic
- [ ] Validate all flow steps marked with IDs are implemented and traceable
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEM-CODE-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEM"
# Human-readable check title
title = "Algorithms Semantics"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Validate algorithm steps match the Feature design algorithms (inputs, rules, outputs)
- [ ] Ensure data transformations and calculations match the described business rules
- [ ] Confirm loop/iteration behavior and validation rules align with algorithm steps
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEM-CODE-005"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEM"
# Human-readable check title
title = "State Semantics"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Confirm state transitions match the Feature design state machine
- [ ] Verify triggers and guards for transitions match defined conditions
- [ ] Ensure invalid transitions are prevented or handled explicitly
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEM-CODE-006"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEM"
# Human-readable check title
title = "Definition of Done Semantics"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEM-CODE-007"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEM"
# Human-readable check title
title = "Overall Design Consistency"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
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
