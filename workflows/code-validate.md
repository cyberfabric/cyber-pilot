---
fdd: true
type: workflow
name: Code Validate
version: 1.0
purpose: Validate code implementation against feature design
---

# Validate Code

**Type**: Validation  
**Role**: Developer, QA  
**Artifact**: Validation report (output to chat)

---

## Prerequisite Checklist

- [ ] Agent has read execution-protocol.md
- [ ] Agent has read workflow-execution.md
- [ ] Agent understands this workflow's purpose

---


ALWAYS open and follow `../requirements/workflow-execution.md` WHEN executing this workflow

## ⚠️ PRE-FLIGHT CHECKLIST (ALWAYS Complete Before Proceeding)

**Agent ALWAYS verifies before starting this workflow**:

**Navigation Rules Compliance**:
- [ ] ✅ Open and follow `../requirements/execution-protocol.md` (MANDATORY BASE)
- [ ] ✅ Open and follow `../requirements/workflow-execution.md` (General execution)
- [ ] ✅ Open and follow `../requirements/workflow-execution-validations.md` (Validation specifics)

**Workflow-Specific Requirements**:
- [ ] ✅ Open and follow `../requirements/feature-design-structure.md` (Feature design requirements)
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

**Purpose**: Validate complete feature implementation against feature design

**Scope**: 
- All code implementing requirements marked as implemented in feature DESIGN.md
- All test scenarios from feature DESIGN.md Section F
- Complete feature codebase quality

**Key Principle**: Validate the ENTIRE feature code against the feature design, not individual changes

---

## Requirements

**ALWAYS open and follow**:
- `../requirements/feature-design-structure.md` (feature design structure)
- `{adapter-directory}/specs/testing.md` (test requirements)
- `{adapter-directory}/specs/feature-status-validation.md` (status validation)

Extract:
- Testing scenario requirements from feature DESIGN.md
- Requirements marked as implemented in feature DESIGN.md
- Adapter build and test commands
- Code quality requirements

---

## Prerequisites

**MUST validate**:
- [ ] Feature DESIGN.md exists and validated (100/100 + 100%)
- [ ] Adapter exists - validate: Required for validation

---

## Steps

### 1. Identify Feature Scope

**Read feature artifacts**:
1. Open feature DESIGN.md
2. Extract feature slug from paths

**Extract validation scope**:
- All requirements from DESIGN.md Section F
- All testing scenarios from DESIGN.md Section F

### 2. Build Codebase Map

**Locate feature code by tags**:
- Search for all `@fdd-` tags corresponding to the feature DESIGN.md scope across the codebase scope defined by the adapter:
  - `@fdd-flow:`, `@fdd-algo:`, `@fdd-state:`, `@fdd-req:`, `@fdd-test:`
- Collect all files containing these tags.

**Result**: Complete list of files implementing this feature

### 3. Validate Requirements Implementation

**For each requirement in DESIGN.md Section F marked as IMPLEMENTED**:

**Verify code exists**:
- Verify code is not placeholder/stub (no TODO/FIXME/unimplemented!)

**Validation**:
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
- Search the feature code set (identified via feature DESIGN.md IDs and `@fdd-*` tags) for incomplete work markers: `TODO`, `FIXME`, `XXX`, `HACK`.
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
2. Locate implementing code via @fdd-req tags (or @fdd-flow/@fdd-algo/@fdd-state tags when relevant).
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
- Code Tagging (10 pts): Feature code tagged with relevant feature DESIGN.md IDs (`@fdd-flow`, `@fdd-algo`, `@fdd-state`, `@fdd-req`, `@fdd-test`)

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
✅ | ❌ All feature code tagged with relevant feature DESIGN.md IDs (phase is always a postfix, no standalone phase tags):
   - @fdd-flow:{flow-id}:ph-{N}, @fdd-algo:{algo-id}:ph-{N}, @fdd-state:{state-id}:ph-{N}, @fdd-req:{req-id}:ph-{N}, @fdd-test:{test-id}:ph-{N}

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

**If FAIL**: Fix issues above, re-run `code-validate`

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
- Re-run `code-validate`
- Do NOT mark feature as COMPLETE until PASS

---

## Validation Criteria

- [ ] All workflow steps completed
- [ ] Output artifacts are valid

---


## Validation Checklist

- [ ] All prerequisites were met
- [ ] All steps were executed in order

---

## References

- ALWAYS execute `feature-validate.md` WHEN validating a feature DESIGN.md before code work
- ALWAYS execute `code.md` WHEN implementing directly from feature DESIGN.md
- ALWAYS open and follow `feature-design-structure.md` WHEN interpreting feature DESIGN.md IDs and sections
- ALWAYS open and follow `{adapter-directory}/specs/testing.md` WHEN executing tests
- ALWAYS open and follow `{adapter-directory}/specs/feature-status-validation.md` WHEN validating code quality/status consistency
