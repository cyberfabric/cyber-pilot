<!-- @fdd-change:fdd-fdd-feature-core-methodology-change-agents-navigation:ph-1 -->
# FDD Workflow Execution Protocol

**Version**: 1.3  
**Purpose**: MANDATORY execution protocol for ALL workflows  
**Scope**: EVERY workflow execution without exceptions

---

**ALWAYS open and follow**: `core.md` WHEN editing this file

<!-- fdd-begin fdd-fdd-feature-core-methodology-flow-ai-execute:ph-1:inst-read-protocol -->
## ⚠️ MANDATORY PRE-EXECUTION PROTOCOL ⚠️

**Before executing ANY workflow, agent ALWAYS follows this protocol**

This protocol is **NON-NEGOTIABLE** and applies to **EVERY** workflow without exception.

**One skipped step = INVALID execution = output DISCARDED**
<!-- fdd-end   fdd-fdd-feature-core-methodology-flow-ai-execute:ph-1:inst-read-protocol -->

---

## Phase 1: Protocol Initialization (MANDATORY)

### Step 1: Acknowledge Protocol

Agent ALWAYS explicitly acknowledges:
```
I am about to execute workflow: {workflow-name}
I acknowledge that I ALWAYS follow the FDD Execution Protocol.
I will NOT skip any steps.
```

### Step 2: Load Base Requirements

**ALWAYS open and follow in this order**:
1. [ ] `requirements/workflow-execution.md` - General execution rules
2. [ ] `requirements/workflow-execution-validations.md` - For validation workflows
   OR
   [ ] `requirements/workflow-execution-operations.md` - For operation workflows
3. [ ] Extract all MUST requirements from these files
4. [ ] Create mental checklist of requirements

**Verification**: Can you list 3 key requirements from workflow-execution.md?
- If NO → Go back and re-read

### Step 3: Load Workflow Requirements

**ALWAYS open and follow**:
1. [ ] `workflows/{workflow-name}.md` - Specific workflow file
2. [ ] Extract prerequisites section
3. [ ] Extract required files list
4. [ ] Note all validation criteria (for validation workflows)
5. [ ] Verify ALL prerequisites are satisfied

<!-- fdd-begin fdd-fdd-feature-core-methodology-flow-ai-execute:ph-1:inst-discover-adapter -->
### Step 4: Discover FDD Adapter

**ALWAYS run first**:
```bash
fdd adapter-info --root . --fdd-root {fdd-core-location}
```

**Agent must pass FDD location**: Use `--fdd-root` with path from system prompts/context

**Parse output**:
- [ ] If `status: FOUND` → Load adapter AGENTS.md from `adapter_dir`
- [ ] If `status: NOT_FOUND` → Use FDD core defaults only
- [ ] Extract `adapter_dir`, `project_name`, `specs` list
<!-- fdd-end   fdd-fdd-feature-core-methodology-flow-ai-execute:ph-1:inst-discover-adapter -->

**If adapter found**:
1. [ ] Open and follow `{adapter_dir}/AGENTS.md`
2. [ ] Note all adapter-specific WHEN rules
3. [ ] Note available specs in `specs/` directory
4. [ ] Apply adapter conventions to all workflows

**Adapter specs usage**:
- Use adapter specs when workflow WHEN rule references them
- Examples: `tech-stack.md`, `domain-model.md`, `conventions.md`, `testing.md`

**If adapter NOT found**:
- Proceed with FDD core methodology only
- No project-specific conventions available

### Mandatory Skill Usage (CRITICAL)

**Agent MUST use this skill without exceptions**:

**FDD Unified Tool (`skills/fdd`)**:
- ALWAYS use for discovering FDD adapter configuration (adapter-info)
- ALWAYS use for searching FDD artifacts (DESIGN.md, BUSINESS.md, FEATURES.md, CHANGES.md, ADR.md)
- ALWAYS use for ID lookup (actors, capabilities, requirements, flows, algorithms, states, changes)
- ALWAYS use for traceability scans (where-defined, where-used)
- ALWAYS use for code traceability (@fdd-* tags)
- ALWAYS use for cross-referencing IDs across artifacts and code
- ALWAYS use for validating DESIGN.md and CHANGES.md structure and content
- ALWAYS use for code traceability validation (@fdd-* markers in code)
- ALWAYS use for systematic artifact validation before manual checks
- ALWAYS run as Deterministic Gate (fail fast before LLM validation)

**Adapter Discovery**: `adapter-info --root {project-root}`

**Search & Traceability Commands**: `list-ids`, `list-items`, `list-sections`, `find-id`, `where-defined`, `where-used`, `scan-ids`, `search`, `read-section`, `get-item`

**Validation Commands**: `validate --artifact`

**Skill Integrity (MANDATORY)**:
- [ ] If a skill/validator returns **FAIL**, the agent MUST treat the output as authoritative.
- [ ] The agent MUST NOT modify skills to make failing validations pass.
- [ ] The agent MAY modify a skill only when the user explicitly requests changes to the skill itself.

**If ANY prerequisite fails**:
- STOP immediately
- Report failed prerequisite
- Suggest how to fix
- Do NOT proceed

### Step 5: Load Artifact Requirements

**ALWAYS open and follow**:
1. [ ] `requirements/{artifact}-structure.md` - Structure requirements
2. [ ] Extract validation criteria (100-point breakdown)
3. [ ] Extract EVERY single validation item
4. [ ] Note pass threshold
5. [ ] Create checklist of ALL criteria

**For validation workflows**:
- Extract structure criteria
- Extract completeness criteria  
- Extract non-contradiction criteria
- Extract coverage criteria
- Note point values for each

### Step 6: Load Parent Artifacts (if applicable)

**If workflow references parent artifacts**:
1. [ ] Read each parent artifact completely
2. [ ] Extract all IDs (actors, capabilities, requirements, principles)
3. [ ] Build index for cross-reference validation
4. [ ] Note all concepts that must be covered

---

## Phase 2: Execution Readiness Check

**Agent ALWAYS answers YES to ALL questions before proceeding**:

### Knowledge Verification
1. ⚠️ **Have I read workflow-execution.md?**
   - [ ] YES - I read it completely
   - [ ] NO - ALWAYS open and follow it now, cannot proceed

2. ⚠️ **Have I read workflow-execution-{type}.md?**
   - [ ] YES - I read the type-specific file
   - [ ] NO - ALWAYS open and follow it now, cannot proceed

3. ⚠️ **Have I read the specific workflow file?**
   - [ ] YES - I read it completely
   - [ ] NO - ALWAYS open and follow it now, cannot proceed

4. ⚠️ **Have I read the artifact structure requirements?**
   - [ ] YES - I read {artifact}-structure.md
   - [ ] NO - ALWAYS open and follow it now, cannot proceed

### Comprehension Verification
5. ⚠️ **Do I understand "Maximum Attention to Detail" requirement?**
   - [ ] YES - I will check EVERY criterion individually
   - [ ] NO - ALWAYS re-read workflow-execution-validations.md lines 9-29

6. ⚠️ **Do I have a complete list of validation criteria?**
   - [ ] YES - I extracted EVERY criterion from requirements
   - [ ] NO - ALWAYS re-read requirements file

7. ⚠️ **Am I ready to check each item individually, not in groups?**
   - [ ] YES - I will verify each criterion separately
   - [ ] NO - ALWAYS re-read "Maximum Attention" section

### Preparation Verification
8. ⚠️ **Do I have a plan for systematic verification?**
   - [ ] YES - I will use fdd skill, grep, read_file
   - [ ] NO - ALWAYS create verification plan

9. ⚠️ **Do I know which mandatory skills to use?**
   - [ ] YES - fdd skill for artifact/ID lookup and validation
   - [ ] NO - ALWAYS review Mandatory Skill Usage section

10. ⚠️ **Am I prepared to report EVERY issue, no matter how small?**
    - [ ] YES - I will report all issues found
    - [ ] NO - ALWAYS adjust my mindset

11. ⚠️ **Have I run fdd validate as Deterministic Gate and did it PASS?**
    - [ ] YES - Deterministic Gate PASS, safe to proceed to LLM-heavy validation
    - [ ] NO - ALWAYS run fdd validate now; if FAIL → STOP workflow

---

## Phase 2.5: Deterministic Gate (MANDATORY)

**Goal**: Fail fast using deterministic validators before spending time on LLM-heavy/manual validation.

**Deterministic validators include**:
- `fdd` skill validate command (artifact structure, ID format, code traceability)
- Build/lint/test commands that are explicitly required by the workflow or adapter specs
- File existence/readability checks

**LLM-heavy validation includes**:
- Manual design conformance reasoning
- Manual coverage mapping (requirements ↔ code ↔ tests)
- Manual deep review beyond what deterministic validators report

**MANDATORY rules**:
1. Run `fdd validate` as early as possible for validation workflows.
2. If `fdd validate` returns **FAIL**:
   - The workflow result is **FAIL**.
   - STOP immediately.
   - Do NOT proceed to any LLM-heavy/manual validation.
   - Output the workflow report as FAIL with the validator output as authoritative evidence.
3. If the skill/validator returns **PASS**:
   - The agent MUST continue workflow execution.
   - The agent MUST NOT stop after skill completion.
   - The agent MUST proceed to remaining workflow steps (LLM-heavy/manual validation, additional checks, output generation).
   - Skill execution is part of the workflow, not the entire workflow.
4. Only after Deterministic Gate **PASS** may the agent perform LLM-heavy/manual validation steps.

---

## Phase 3: Execution

### During Execution Rules

**ALWAYS do**:
1. Follow checklist item by item
2. Check EVERY criterion individually (never group checks)
3. Read ENTIRE artifact from line 1 to end
4. Verify EACH ID format against requirements
5. Cross-check EVERY reference against parent artifacts
6. Use grep/search tools for systematic verification
7. Report intermediate progress
8. Execute mini self-checks after each category

**ALWAYS do NOT**:
1. Skip any validation criteria
2. Group checks together without individual verification
3. Assume sections are correct without checking
4. Give benefit of doubt - verify everything
5. Rush through validation
6. Skip systematic grep searches

---

## Phase 4: Post-Execution Validation

### Self-Test Before Reporting (MANDATORY)

**Agent ALWAYS completes self-test before outputting results**:

#### Execution Completeness
1. ⚠️ **Did I read the ENTIRE artifact line by line?**
   - [ ] YES - Read from line 1 to end
   - [ ] NO - Validation is INVALID, must re-do

2. ⚠️ **Did I check EVERY validation criterion from requirements?**
   - [ ] YES - Verified each criterion individually
   - [ ] NO - Validation is INVALID, must re-do

3. ⚠️ **Did I verify EACH ID format individually?**
   - [ ] YES - Checked each ID against format requirements
   - [ ] NO - Validation is INVALID, must re-do

4. ⚠️ **Did I cross-reference EVERY actor/capability/requirement?**
   - [ ] YES - Built index, verified each reference
   - [ ] NO - Validation is INVALID, must re-do

#### Systematic Verification
5. ⚠️ **Did I run grep searches for common issues?**
   - [ ] YES - Ran TODO, ID, placeholder searches
   - [ ] NO - Validation is INVALID, must re-do

6. ⚠️ **Did I check ADR headers for ID fields? (if validating ADR.md)**
   - [ ] YES - Verified `**ID**:` after EACH `## ADR-` heading
   - [ ] NO - Validation is INVALID, must re-do

7. ⚠️ **Did I verify traceability fields? (if validating DESIGN.md)**
   - [ ] YES - Checked `**Capabilities**:`, `**Actors**:` for each requirement
   - [ ] NO - Validation is INVALID, must re-do

#### Score Verification
8. ⚠️ **Is my score calculation arithmetically correct?**
   - [ ] YES - Verified addition
   - [ ] NO - Must recalculate

9. ⚠️ **Did I award points according to requirements file?**
   - [ ] YES - Used exact scoring from requirements
   - [ ] NO - Must re-score using requirements

10. ⚠️ **Did I compare score to correct threshold?**
    - [ ] YES - Used threshold from requirements
    - [ ] NO - Validation invalid, check threshold

**If ANY answer is NO → Validation is INVALID, must restart execution**

### Output Format Verification

**Agent ALWAYS verifies output includes**:
- [ ] Score breakdown by category
- [ ] All issues listed with ✅/❌
- [ ] Recommendations prioritized by severity
- [ ] Next steps (PASS or FAIL scenario)
- [ ] Self-test confirmation section

---

## Protocol Compliance Report

**Agent ALWAYS includes in output**:

```markdown
---

## Execution Protocol Compliance

**Phase 1: Protocol Initialization**
✅ Read workflow-execution.md
✅ Read workflow-execution-validations.md
✅ Read {workflow-name}.md
✅ Read {artifact}-structure.md
✅ Extracted all validation criteria

**Phase 2: Readiness Check**
✅ Passed all 11 readiness questions
✅ Understood "Maximum Attention to Detail"
✅ Created complete validation checklist
✅ Identified mandatory skill (fdd)
✅ Deterministic Gate PASS (fdd validate)

**Phase 3: Execution**
✅ Checked EVERY criterion individually
✅ Read entire artifact line by line
✅ Ran systematic grep searches
✅ Cross-referenced all IDs

**Phase 4: Post-Execution**
✅ Completed self-test (10/10 YES)
✅ Verified score calculation
✅ Confirmed no criteria skipped

**Protocol compliance: PASS ✅**
```

---

## Protocol Violations

### Common protocol violations
1. ❌ **Not reading execution-protocol.md** before starting workflow
2. ❌ **Not reading workflow-execution.md** before executing workflow
3. ❌ **Not reading workflow-execution-validations.md** for validation workflows
4. ❌ **Not completing pre-flight checklist** in workflow files
5. ❌ **Not running self-test** before reporting validation results
6. ❌ **Not checking EVERY validation criterion individually**
7. ❌ **Not using fdd skill for FDD artifact/FDD ID lookups**
8. ❌ **Not using fdd validate as Deterministic Gate**
9. ❌ **Not cross-referencing EVERY ID**

**One violation = entire workflow execution FAILED**
   - Consequence: INVALID validation
   - Fix: Complete self-test, restart if needed

### Violation Handling

**If user identifies protocol violation**:
1. Acknowledge violation
2. Identify what was skipped
3. Explain why it was skipped (honest answer)
4. Restart workflow with full protocol compliance
5. Show protocol compliance report in output

**If agent detects own violation during self-test**:
1. STOP immediately
2. Discard current validation
3. Report what was missed
4. Restart with full protocol compliance

---

## Protocol Enforcement

**This protocol is MANDATORY and NON-NEGOTIABLE**

**Responsibility**:
- Agent is responsible for following protocol
- Agent must self-check compliance
- Agent must report compliance in output
- User can verify compliance from report

**Benefits**:
- Prevents missed validation criteria
- Ensures systematic verification
- Provides transparency
- Enables self-correction
- Maintains FDD quality standards

**Remember**: One missed step = entire workflow is INVALID

---

## References

**ALWAYS open and follow this file**:
- Before executing ANY workflow
- Referenced in all workflow files
- Part of Navigation Rules

**References**:
- `workflow-execution.md` - General execution rules
- `workflow-execution-validations.md` - Validation specifics
- `workflow-execution-operations.md` - Operation specifics
