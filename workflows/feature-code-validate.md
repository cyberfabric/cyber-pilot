---
description: Validate feature code implementation against feature design
---

# Validate Feature Code

**Type**: Validation  
**Role**: Developer, QA  
**Artifact**: Validation report (output to chat)

---

**ALWAYS open and follow**: `../requirements/core.md` WHEN editing this file

ALWAYS open and follow `../requirements/workflow-execution.md` WHEN executing this workflow

## ⚠️ PRE-FLIGHT CHECKLIST (ALWAYS Complete Before Proceeding)

**Agent ALWAYS verifies before starting this workflow**:

**Navigation Rules Compliance**:
- [ ] ✅ Open and follow `../requirements/execution-protocol.md` (MANDATORY BASE)
- [ ] ✅ Open and follow `../requirements/workflow-execution.md` (General execution)
- [ ] ✅ Open and follow `../requirements/workflow-execution-validations.md` (Validation specifics)

**Workflow-Specific Requirements**:
- [ ] ✅ Open and follow `../requirements/feature-design-structure.md` (Feature design requirements)
- [ ] ✅ Open and follow `../requirements/feature-changes-structure.md` (Changes structure) — optional when CHANGES are absent; still read for format awareness
- [ ] ✅ Open and follow adapter specs/testing.md (Test requirements)
- [ ] ✅ Open and follow adapter specs/feature-status-validation.md (Status validation)
- [ ] ✅ Check adapter initialization (FDD-Adapter/AGENTS.md exists)
- [ ] ✅ Validate all prerequisites from Prerequisites section below

**Self-Check**:
- [ ] ✅ I have read ALL files listed above
- [ ] ✅ I understand "Maximum Attention to Detail" requirement
- [ ] ✅ I am ready to check EVERY validation criterion individually
- [ ] ✅ I will verify tests pass and build succeeds
- [ ] ✅ I will complete self-test before reporting results

**⚠️ If ANY checkbox is unchecked → STOP and read missing files first**

---

## Overview

**Purpose**: Validate complete feature implementation against feature design using changes for code identification

**Scope**: 
- All code implementing requirements marked as implemented in CHANGES.md
- All test scenarios from feature DESIGN.md Section F
- Complete feature codebase quality

**Key Principle**: Validate the ENTIRE feature code against the feature design, not individual changes

---

## Requirements

**ALWAYS open and follow**:
- `../requirements/feature-design-structure.md` (feature design structure)
- `../requirements/feature-changes-structure.md` (changes structure) — read for format; if CHANGES are absent or intentionally skipped, apply only relevant parts
- `{adapter-directory}/specs/testing.md` (test requirements)
- `{adapter-directory}/specs/feature-status-validation.md` (status validation)

Extract:
- Testing scenario requirements from feature DESIGN.md
- Requirements marked as implemented in CHANGES.md
- Adapter build and test commands
- Code quality requirements

---

## Prerequisites

**MUST validate**:
- [ ] Feature DESIGN.md exists and validated (100/100 + 100%)
- [ ] CHANGES source available **OR** explicitly recorded as “CHANGES not provided / skipped by author”
- [ ] Adapter exists - validate: Required for validation

**CHANGES source selection (when available)**:
- **Preferred**: Use active `CHANGES.md` in the feature directory.
- **Fallback**: If active `CHANGES.md` does not exist, use the most recent archived changes file in `archive/`.
  - Choose the newest `YYYY-MM-DD-CHANGES.md` (lexicographically latest date).
**If no CHANGES are provided**:
- Document “CHANGES unavailable; change-based checks skipped” and proceed with design-only validation.

---

## Steps

### 1. Identify Feature Scope

**Read feature artifacts**:
1. Open feature DESIGN.md
2. If CHANGES are available: Open feature CHANGES source (active `CHANGES.md` or latest archived `archive/YYYY-MM-DD-CHANGES.md`)
3. Extract feature slug from paths

**Extract validation scope**:
- All requirements from DESIGN.md Section F
- All testing scenarios from DESIGN.md Section F
- If CHANGES exist: All changes from CHANGES source (to identify code locations). If CHANGES are absent, note “change map skipped”.

### 2. Build Codebase Map

**If CHANGES exist, use them to identify code**:
1. Extract all file paths from all changes (tasks section)
2. Extract all @fdd-change tags used
3. Build list of files implementing feature requirements

**Locate feature code by tags**:
- Search for `@fdd-change:fdd-{project}-{feature}-change-` across the codebase scope defined by the adapter.
- Collect all files containing these tags.

**Result**: Complete list of files implementing this feature (or “change map skipped” if no CHANGES provided)

### 3. Validate Requirements Implementation

**For each requirement in DESIGN.md Section F marked as IMPLEMENTED**:

**If CHANGES are available**:
- Find which change(s) implement this requirement (via **Implements**: field)
- Verify change status is COMPLETED
- If any implementing change is NOT_STARTED or IN_PROGRESS → requirement is NOT implemented

**If CHANGES are absent**:
- Document “CHANGES absent; requirement implementation traced via DESIGN.md and code inspection only”.

**Verify code exists**:
- Check that files specified in change tasks exist (when CHANGES exist)
- Check that @fdd-change tags exist in code (when CHANGES exist)
- Verify code is not placeholder/stub (no TODO/FIXME/unimplemented!)

**Validation**:
- ✅ Requirement ID found in CHANGES.md **Implements**: field (if CHANGES exist)
- ✅ All implementing changes have status COMPLETED (if CHANGES exist)
- ✅ Code files exist and contain implementation
- ✅ No TODO/FIXME in implementation code
- ✅ No unimplemented!() in business logic

### 4. Validate Design Conformance (Flows / Algorithms / States / Technical Details)

**Collect design IDs**:
- Flows: Section B IDs (`fdd-{project}-feature-{feature-slug}-flow-*`)
- Algorithms: Section C IDs (`...-algo-*`)
- States (if present): Section D IDs (`...-state-*`)
- Requirements & tests: Section F IDs (`...-req-*`, `...-test-*`)
- Phases: `ph-{N}` from requirement `**Phases**` lists in feature DESIGN.md and from FDL step lines

**Check implementation and non-deviation**:
- Search the codebase for all `@fdd-` tags and verify EVERY occurrence includes a phase postfix `:ph-{N}` (N is an integer).
- For each Flow ID: locate code tagged with `@fdd-flow:{id}:ph-{N}` and verify the control flow matches the described steps (no skipped/extra steps that change behavior).
- For each Algorithm ID: locate code tagged with `@fdd-algo:{id}:ph-{N}` and verify logic matches described algorithm; no TODO/unimplemented!/panic/unwrap stubs; performance/complexity expectations respected.
- For each State ID (if any): locate code tagged with `@fdd-state:{id}:ph-{N}` and verify state transitions match the design; forbidden states/transitions absent.
- Technical details (Section E): verify endpoints, security, error handling, OData parameters, and delegation points align with design and adapter specs (`modkit-rest-integration.md`, `patterns.md`, `conventions.md`); ensure OperationBuilder usage and api_gateway integration are intact (no direct axum routes, no custom middleware).

**Validation**:
- ✅ All `@fdd-*` code tags include mandatory phase postfix `:ph-{N}`
- ✅ All design IDs (flows/algorithms/states/requirements/tests) found in code and mapped to implementations
- ✅ Implementations follow design steps/logic; no divergent behavior
- ✅ No missing or extra endpoints/paths versus design Section E
- ✅ No placeholder/stub code in mapped implementations

### 5. Validate Test Scenarios Implementation

**CRITICAL**: All testing scenarios from DESIGN.md Section F MUST be implemented

**For each testing scenario in DESIGN.md Section F**:

**Check test exists**:
1. Extract testing scenario ID: `fdd-{project}-feature-{feature-slug}-test-{scenario-name}`
2. Search for test referencing this scenario ID:
    - Search within test locations defined by the adapter (unit, integration, e2e).

**Verify test implementation**:
- ✅ Test file exists (unit/integration/e2e per adapter)
- ✅ Test contains scenario ID in comment for traceability
- ✅ Test is NOT #[ignore] without justification
- ✅ Test actually validates scenario behavior (not placeholder)
- ✅ Test follows adapter testing conventions

**Validation**:
- ✅ Test scenario ID found in test file
- ✅ Test implements scenario logic
- ✅ Test is not ignored or placeholder
- ✅ Test can be executed

### 6. Execute Build Validation

**Run build**:
- Execute the build command from `{adapter-directory}/specs/build-deploy.md`.

**Check**:
- ✅ Build succeeds
- ✅ No compilation errors
- ✅ No compiler warnings (or acceptable per adapter)

**Score**: 15 points

### 7. Execute Linter Validation

**Run linters**:
- Execute the lint command(s) from `{adapter-directory}/specs/conventions.md` or `{adapter-directory}/specs/build-deploy.md`.

**Check**:
- ✅ Linter passes
- ✅ No linter errors
- ✅ No linter warnings (or acceptable per adapter)

**Score**: 10 points

### 8. Execute Test Validation

**Run all tests**:
- Execute the test command(s) from `{adapter-directory}/specs/testing.md`.

**Check**:
- All unit tests pass
- All integration tests pass
- All e2e tests pass (if applicable)
- No ignored tests without justification
- Coverage meets adapter threshold

**Score**: 30 points

### 9. Code Quality Validation

**Check for incomplete work**:
- Search the feature code set (identified via `@fdd-change` tags) for incomplete work markers: `TODO`, `FIXME`, `XXX`, `HACK`.
- Search feature business logic code (domain/service layers per adapter) for incomplete implementation markers: `unimplemented!`, `todo!`.
- Search test code for ignored tests (e.g. `#[ignore]`) and validate justification per adapter rules.

**Check per adapter feature-status-validation.md**:
- No TODO/FIXME in domain/service layers
- No unimplemented!() in business logic
- No bare unwrap() or panic in production code
- Error handling complete
- No ignored tests without documented reason
- No placeholder tests (assert!(true))

**Score**: 15 points

### 10. Validate Code Logic Consistency with Design

**Purpose**: Verify code logic does not contradict design specifications

**After all technical checks pass (build/lint/tests), perform deep design-code consistency check**:

**For each requirement in DESIGN.md Section F marked IMPLEMENTED**:
1. Read requirement specification carefully
2. Locate implementing code via @fdd-req or @fdd-change tags
3. Analyze code logic and compare with requirement description
4. Check for contradictions:
   - ❌ Code does opposite of what design specifies
   - ❌ Code skips mandatory steps from design
   - ❌ Code adds behavior not in design that changes semantics
   - ❌ Code uses different algorithm/approach that violates design constraints
   - ❌ Error handling contradicts design error specifications

**For each flow in DESIGN.md Section B marked implemented**:
1. Read flow steps and control logic
2. Locate flow implementation via @fdd-flow tags
3. Trace execution path through code
4. Verify:
   - ✅ All flow steps executed in correct order
   - ✅ No steps bypassed that would change behavior
   - ✅ Conditional logic matches design conditions
   - ✅ Error paths match design error handling

**For each algorithm in DESIGN.md Section C marked implemented**:
1. Read algorithm specification and complexity requirements
2. Locate algorithm implementation via @fdd-algo tags
3. Analyze implementation logic
4. Verify:
   - ✅ Algorithm logic matches design specification
   - ✅ Performance characteristics match design (O(n), O(1), etc.)
   - ✅ Edge cases handled as designed
   - ✅ No logic shortcuts that violate design constraints

**For technical details in DESIGN.md Section E**:
1. Read endpoint specifications, security requirements, OData parameters
2. Verify code implementation matches specifications:
   - ✅ Endpoints match paths/methods from design
   - ✅ Security checks match design requirements
   - ✅ Query parameters match OData specifications
   - ✅ Response formats match design schemas
   - ✅ Delegation points implemented as designed

**Validation**:
- ✅ No contradictions found between code logic and design
- ✅ All requirements implemented as specified (not diverged)
- ✅ Flows execute exactly as designed
- ✅ Algorithms match design specifications
- ✅ Technical implementation matches Section E specs

**Documentation**:
- List any logic divergences found
- Categorize: CRITICAL (contradicts design) vs MINOR (style deviation)
- CRITICAL divergences = validation FAIL

**Score**: 20 points

### 11. Calculate Score

**Scoring breakdown**:
- Requirements Implementation (30 pts): All requirements marked IMPLEMENTED actually implemented
- Design Conformance (20 pts): Flows/algorithms/states/technical details from DESIGN implemented without deviation
- Test Scenarios Implementation (20 pts): All test scenarios from DESIGN.md implemented
- Build Success (15 pts): Build succeeds without errors
- Linter Pass (10 pts): Linter succeeds without errors
- Test Pass (30 pts): All tests pass, coverage meets threshold
- Code Quality (15 pts): No TODO/FIXME/unimplemented in business logic
- Code Logic Consistency (20 pts): Code logic does not contradict design specifications
- Code Tagging (10 pts): All feature code tagged with @fdd-change

**Total**: 150 points
**Pass threshold**: ≥128/150 (≈85%)

### 12. Output Results to Chat

**Format**:
```markdown
## Validation: Feature Code ({feature-slug})

**Score**: {X}/150  
**Status**: PASS | FAIL  
**Threshold**: ≥128/150

---

### Findings

**Requirements Implementation** ({X}/30):
✅ | ❌ Requirement {req-id}: {status} (Change {change-id}: {change-status})

**Test Scenarios Implementation** ({X}/20):
✅ | ❌ Test scenario {test-id}: {implemented | NOT IMPLEMENTED}
  - Test file: {path} or NOT FOUND
  - Test status: {pass | fail | ignored | placeholder}

**Build Status** ({X}/15):
✅ | ❌ Build: {success | failed}
✅ | ❌ Compiler warnings: {count}

**Linter Status** ({X}/10):
✅ | ❌ Linter: {success | failed}
✅ | ❌ Linter warnings: {count}

**Test Execution** ({X}/30):
✅ | ❌ Unit tests: {X}/{total} passed
✅ | ❌ Integration tests: {X}/{total} passed
✅ | ❌ E2E tests: {X}/{total} passed
✅ | ❌ Coverage: {X}% (threshold: {Y}%)

**Code Quality** ({X}/15):
✅ | ❌ No TODO/FIXME in domain/service: {found count}
✅ | ❌ No unimplemented! in business logic: {found count}
✅ | ❌ No ignored tests without reason: {found count}
✅ | ❌ Error handling complete

**Code Logic Consistency** ({X}/20):
✅ | ❌ Requirements logic matches design specifications
✅ | ❌ Flow execution matches design steps
✅ | ❌ Algorithm implementation matches design specifications
✅ | ❌ Technical details match Section E specifications
✅ | ❌ No CRITICAL divergences found
  - List of divergences: {CRITICAL: [...] | MINOR: [...]}

**Code Tagging** ({X}/10):
✅ | ❌ All feature code tagged with (phase is always a postfix, no standalone phase tags):
   - @fdd-change:{change-id}:ph-{N} (from CHANGES source)
   - @fdd-flow:{flow-id}:ph-{N}, @fdd-algo:{algo-id}:ph-{N}, @fdd-state:{state-id}:ph-{N}, @fdd-req:{req-id}:ph-{N}, @fdd-test:{test-id}:ph-{N} (from feature DESIGN.md)
✅ | ❌ Validator searched code for ALL IDs from DESIGN.md (Sections B/C/D/F) and CHANGES source

---

### Recommendations

**Critical**:
1. {Fix}

**High Priority**:
1. {Fix}

**Medium Priority**:
1. {Fix}

---

### Next Steps

**If PASS**:
✅ Feature code validated! Update feature status as COMPLETE in FEATURES.md
✅ Proceed to next feature

**If FAIL**: Fix issues above, re-run `feature-code-validate`

---

### Self-Test Confirmation

**Agent confirms**:
✅ Read execution-protocol.md before starting
✅ Read all required files from pre-flight checklist
✅ Checked EVERY requirement individually
✅ Checked EVERY test scenario individually
✅ Ran build, lint, and test commands
✅ Checked for TODO/FIXME/unimplemented systematically
✅ Verified code logic consistency with design specifications
✅ Analyzed code for contradictions with design
✅ Used adapter commands for systematic verification
✅ Completed self-test before reporting

Self-test passed: YES

---

## Validation

Self-validating workflow

---

## Next Steps

**If PASS**:
- Update FEATURES.md: Mark feature status as COMPLETE
- If more features exist: Design next feature
- If all features complete: Project complete 

**If FAIL**: 
- Fix code issues
- Re-run `feature-code-validate`
- Do NOT mark feature as COMPLETE until PASS

---

## Difference from Previous Per-Change Validation

**OLD**: Validated individual change implementations  
**NEW**: Validates ENTIRE feature code against feature design

**Key differences**:
1. **Scope**: Entire feature vs single change
2. **Test scenarios**: ALL scenarios from DESIGN.md must be implemented
3. **Requirements**: ALL requirements marked IMPLEMENTED must be coded
4. **Code identification**: Uses CHANGES.md to find feature code
5. **Quality**: Complete feature quality checks (build, lint, tests, TODO/FIXME)

**Why better**:
- Validates feature as a whole (not fragmented)
- Ensures test scenarios are implemented (not just specified)
- Catches cross-change integration issues
- Validates complete feature quality before completion
- Single validation for entire feature code

---

## References

- ALWAYS execute `feature-validate.md` WHEN validating a feature DESIGN.md before code work
- ALWAYS execute `feature-changes-validate.md` WHEN validating a feature CHANGES.md before implementation
- ALWAYS execute `feature-change-implement.md` WHEN implementing a specific change from CHANGES.md

- ALWAYS open and follow `feature-design-structure.md` WHEN interpreting feature DESIGN.md IDs and sections
- ALWAYS open and follow `feature-changes-structure.md` WHEN interpreting change entry structure and tagging rules
- ALWAYS open and follow `{adapter-directory}/specs/testing.md` WHEN executing tests
- ALWAYS open and follow `{adapter-directory}/specs/feature-status-validation.md` WHEN validating code quality/status consistency
