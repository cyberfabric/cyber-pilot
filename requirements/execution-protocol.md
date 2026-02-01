---
fdd: true
type: requirement
name: Execution Protocol
version: 2.0
purpose: Common protocol executed by generate.md and validate.md workflows
---

# Execution Protocol

**Type**: Protocol (embedded in other workflows)

---

## Table of Contents

- [Overview](#overview)
- [Execution Protocol Violations](#-execution-protocol-violations)
- [Compaction Recovery](#-compaction-recovery)
- [FDD Mode Detection](#fdd-mode-detection)
- [Rules Mode Detection](#rules-mode-detection)
- [Discover Adapter](#discover-adapter)
- [Understand Registry](#understand-registry)
- [Clarify Intent](#clarify-intent)
- [Load Rules](#load-rules)
- [Cross-Reference Awareness](#cross-reference-awareness)
- [Context Usage](#context-usage)
- [Error Handling](#error-handling)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)

---

## Overview

Common steps shared by `generate.md` and `validate.md`. Both workflows MUST execute this protocol before their specific logic.

---
## ⚠️ Execution Protocol Violations

**If agent skips execution-protocol.md**:
- Workflow execution is AUTOMATICALLY INVALID
- All output must be DISCARDED
- User should point out violation
- Agent must restart with protocol compliance

**Common protocol violations**:
1. ❌ **Not reading execution-protocol.md** before starting workflow
2. ❌ **Not running fdd adapter-info** to discover project adapter
3. ❌ **Not following workflow-specific rules** (generate.md, validate.md)

**One violation = entire workflow execution FAILED**

**Agent responsibility**:
- Follow execution-protocol.md for EVERY workflow
- Self-identify violations if discovered

**User responsibility**:
- Point out violations when detected
- Request protocol compliance report
- Ask agent to restart with full compliance

**Recovery from violation**:
1. Acknowledge the violation
2. Identify what was skipped
3. Explain why (honest answer)
4. Discard invalid output
5. Restart workflow with full protocol compliance
6. Show protocol compliance report in new output

---

## 🔄 Compaction Recovery

**Problem**: After context compaction (conversation summarization), agent may lose:
- Knowledge that FDD workflow was active
- List of loaded specs
- Current workflow phase

**Detection signals** (agent should suspect compaction occurred):
- Conversation starts with "This session is being continued from a previous conversation"
- Summary mentions `/fdd-generate`, `/fdd-validate`, or other FDD commands
- Todo list contains FDD-related tasks in progress

**Recovery protocol**:

1. **Check summary for FDD triggers**:
   - If summary mentions `/fdd-*` command → FDD workflow was active
   - If summary mentions editing codebase in FDD project → specs were required

2. **Re-establish context**:
   ```
   ⚠️ Detected: FDD workflow continuation after compaction
   → Re-running protocol check...
   → Running: fdd adapter-info
   → Loading required specs from AGENTS.md
   ```

3. **Announce recovery**:
   ```
   FDD Context Restored:
   - Workflow: {from summary}
   - Target: {from summary}
   - Specs loaded: {list}
   ```

4. **Continue workflow** with full context

**Agent MUST NOT**:
- Continue FDD work without re-loading specs after compaction
- Assume specs are "still loaded" from before compaction
- Skip protocol because "it was already done"

---

## FDD Mode Detection

**Default behavior**:
- Treat request as workflow execution ONLY when FDD is enabled
- User invoking FDD workflow (`/fdd`, `/prd`, `/design`, etc.) = FDD enabled
- User requesting `/fdd off` = FDD disabled for conversation
- When disabled, behave as normal coding assistant

**Announce FDD mode** (non-blocking):
```
FDD mode: ENABLED. To disable: /fdd off
```

---

## Rules Mode Detection

After adapter discovery, determine **Rules Mode**:

### Rules Mode: STRICT (FDD rules enabled)

**Condition**: `artifacts.json` found AND contains `rules` section AND target artifact/code matches registered system.

**Behavior**:
- Full protocol enforcement
- Mandatory semantic validation
- Evidence requirements enforced
- Anti-pattern detection active
- Agent compliance protocol applies (see `agent-compliance.md`)

**Announce**:
```
Rules Mode: STRICT (fdd-sdlc rules loaded)
→ Full validation protocol enforced
```

### Rules Mode: RELAXED (no FDD rules)

**Condition**: No adapter OR no `rules` in artifacts.json OR target not in registered system.

**Before proceeding, agent MUST explain trade-offs**:

```markdown
⚠️ Rules Mode: RELAXED (no FDD rules detected)

Working without FDD rules means:
- No template enforcement → structure may be inconsistent
- No checklist validation → quality criteria undefined
- No evidence requirements → validation may be superficial
- No anti-pattern detection → common agent mistakes undetected

**Why this matters (real examples)**:
1. Without checklist: agent may report "PASS" without checking semantic quality
2. Without template: generated artifact may miss required sections
3. Without evidence requirements: agent may validate from memory, not actual file
4. Without anti-patterns: agent may skip tedious work and claim completion

**Options**:
1. **Provide rules** — specify path to rules package or checklist
2. **Continue without rules** — workflow will execute with best effort (no guarantees)
3. **Bootstrap rules** — run `/fdd-adapter` to set up FDD rules for project
```

**User must explicitly choose** before workflow continues.

**If user chooses "Continue without rules"**:
- Agent proceeds with best effort
- Output includes disclaimer: `⚠️ Validated without FDD rules (reduced rigor)`
- No enforcement of evidence or anti-patterns

### Rules Mode Summary

| Aspect | STRICT | RELAXED |
|--------|--------|---------|
| Template enforcement | ✓ Required | ✗ Best effort |
| Checklist validation | ✓ Mandatory | ✗ Skipped |
| Evidence requirements | ✓ Enforced | ✗ Not required |
| Anti-pattern detection | ✓ Active | ✗ Inactive |
| Semantic validation | ✓ Mandatory | ✗ Optional |
| Output guarantee | High confidence | No guarantees |

---

## Discover Adapter

```bash
python3 {FDD}/skills/fdd/scripts/fdd.py adapter-info --root {PROJECT_ROOT} --fdd-root {FDD}
```

**Parse output**:
```json
{
  "status": "FOUND | NOT_FOUND",
  "adapter_dir": "/path/to/.adapter",
  "project_name": "MyProject",
  "project_root": "/path/to/project",
  "specs": ["conventions", "domain-model", ...],
  "rules": { "fdd-sdlc": {...}, "fdd-core": {...} }
}
```

**If FOUND**: Load `{adapter_dir}/AGENTS.md` for navigation rules

**If NOT_FOUND**: Suggest running `/fdd-adapter` to bootstrap

---

## Understand Registry

**MUST read** `{adapter_dir}/artifacts.json`:

1. **Rules**: What rule packages exist (`fdd-sdlc`, `fdd-core`, etc.)
2. **Systems**: What systems are registered and their hierarchy
3. **Artifacts**: What artifacts exist, their kinds, and traceability settings
4. **Codebase**: What code directories are tracked

**MUST browse** rules directories:
- `{rules-path}/artifacts/` — available artifact kinds (PRD, DESIGN, ADR, etc.)
- `{rules-path}/codebase/` — available code checklists

**Store context**:
- Available rules and their paths
- Registered artifact kinds
- Registered systems and their structure
- Traceability requirements

---

## Clarify Intent

**If unclear from context, ask user**:

### 1. Rules Context
```
Do you want to work within registered FDD rules?
- Yes, use rules: {list available rules from artifacts.json}
- No, provide dependencies manually
```

### 2. Target Type
```
What are we working with?
- Artifact (e.g. document: PRD, SYSTEM DESIGN)
- Code (implementation)
- ???
```

### 3. Specific System (if using rules)
```
Which system does this belong to?
- {list systems from artifacts.json}
- New system (will need to register)
```

**If context is clear**: proceed silently, don't ask unnecessary questions.

---

## Load Rules

**After determining target type**:

### 1. Resolve Rules Package

From `artifacts.json`:

```
1. Find system containing target artifact
2. Get rules name: system.rules (e.g., "fdd-sdlc")
3. Look up path: artifacts.json.rules[rules_name].path
4. RULES_BASE = resolved path (could be anything: "rules/sdlc", "my-rules", etc.)
```

**Example**:
```json
{
  "rules": {
    "fdd-sdlc": { "path": "rules/sdlc" }
  },
  "systems": [{
    "name": "MySystem",
    "rules": "fdd-sdlc"
  }]
}
```
→ `RULES_BASE = "rules/sdlc"`

### 2. Determine Artifact Type

From explicit parameter or artifacts.json lookup:

| Source | Resolution |
|--------|------------|
| `fdd generate PRD` | Explicit: PRD |
| `fdd validate {path}` | Lookup: `artifacts.json.systems[].artifacts[path].kind` |
| Path in `codebase[]` | CODE |

### 3. Load Rules.md

```
RULES_PATH = {RULES_BASE}/artifacts/{ARTIFACT_TYPE}/rules.md
```

For CODE:
```
RULES_PATH = {RULES_BASE}/codebase/rules.md
```

**MUST read rules.md** and parse:
- **Dependencies** section → files to load
- **Requirements** section → confirm understanding
- **Tasks** section (for generate) → execution steps
- **Validation** section (for validate) → validation checks

### 4. Load Dependencies from Rules

Parse Dependencies section:
```markdown
**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation
```

For each dependency:
1. Resolve path relative to rules.md location
2. Load file content
3. Store for workflow use

### 5. Confirm Requirements

Agent reads Requirements section and confirms:
```
I understand the following requirements for {ARTIFACT_TYPE}:
- Structural: {list}
- Semantic: {list}
- Versioning: {list}
- Traceability: {list}
```

**Store loaded context**:
- `RULES_BASE` — base path from artifacts.json
- `RULES_PATH` — full path to rules.md
- `TEMPLATE` — loaded template content
- `CHECKLIST` — loaded checklist content
- `EXAMPLE` — loaded example content
- `REQUIREMENTS` — parsed requirements from rules

### 6. Load Adapter Specs

**After rules loaded and target type determined**, load applicable adapter specs:

**Read adapter AGENTS.md** at `{adapter_dir}/AGENTS.md`

**Parse WHEN clauses** matching current context:

```
For each line matching: ALWAYS open and follow `{spec}` WHEN FDD follows rules `{rule}` for {target}
  IF {rule} == loaded rules ID (e.g., "fdd-sdlc"):
    IF target includes current artifact kind:
      → Open and follow {spec}
    IF target includes "codebase" AND working on code:
      → Open and follow {spec}
```

**Example resolution**:
- Loaded rules: `fdd-sdlc`
- Current target: artifact kind `DESIGN`
- Adapter AGENTS.md contains:
  ```
  ALWAYS open and follow `specs/tech-stack.md` WHEN FDD follows rules `fdd-sdlc` for artifact kinds: DESIGN, ADR OR codebase
  ALWAYS open and follow `specs/domain-model.md` WHEN FDD follows rules `fdd-sdlc` for artifact kinds: DESIGN, FEATURES, FEATURE
  ```
- Matched specs: `specs/tech-stack.md`, `specs/domain-model.md`
- Agent opens and follows both spec files

**Store loaded adapter specs**:
- `ADAPTER_SPECS` — list of loaded spec paths
- Specs content available for workflow guidance

**Backward compatibility**: If adapter uses legacy format (`WHEN executing workflows: ...`), map workflow names to artifact kinds internally.

---

## Cross-Reference Awareness

**Before proceeding, understand**:
- Parent artifacts that might be referenced
- Child artifacts that depend on target
- Related code that implements target (if artifact)
- Related artifacts that code implements (if code)

---

## Context Usage

**MUST**:
- Use current project context for proposals
- Reference existing artifacts when relevant
- Show reasoning for proposals

**MUST NOT**:
- Make up information
- Assume without context
- Proceed without user confirmation (operations)

---

## Error Handling

### Adapter Not Found

**If adapter not found**:
```
⚠️ Adapter not found
→ Run /fdd-adapter to bootstrap
```
**Action**: STOP — cannot proceed without adapter. Suggest bootstrap.

### artifacts.json Parse Error

**If artifacts.json is malformed**:
```
⚠️ Cannot parse artifacts.json: {parse error}
→ Fix JSON syntax errors in {adapter_dir}/artifacts.json
→ Validate with: python3 -m json.tool artifacts.json
```
**Action**: STOP — cannot determine rules or systems without valid registry.

### Rules.md Not Found

**If rules.md cannot be loaded**:
```
⚠️ Rules file not found: {RULES_PATH}
→ Verify rules package exists at {RULES_BASE}
→ Check artifacts.json rules section has correct path
→ Run /fdd-adapter --rescan to regenerate
```
**Action**: STOP — cannot load dependencies or validate without rules.

### Template/Checklist Not Found

**If dependency from rules.md not found**:
```
⚠️ Dependency not found: {dependency_path}
→ Referenced in: {RULES_PATH}
→ Expected at: {resolved_path}
→ Verify rules package is complete
```
**Action**: STOP — cannot generate/validate without required dependencies.

### System Not Registered

**If target artifact's system not in artifacts.json**:
```
⚠️ System not found: {system_name}
→ Registered systems: {list from artifacts.json}
→ Options:
  1. Register system via /fdd-adapter
  2. Use existing system
  3. Continue in RELAXED mode (no rules enforcement)
```
**Action**: Prompt user to choose before proceeding.

### Artifact Kind Not Supported

**If artifact kind not in rules package**:
```
⚠️ Unsupported artifact kind: {KIND}
→ Available kinds in {RULES_BASE}: {list}
→ Options:
  1. Use supported kind
  2. Create custom rules for {KIND}
  3. Continue in RELAXED mode
```
**Action**: Prompt user to choose before proceeding.

---

## Consolidated Validation Checklist

**Use this single checklist for all execution-protocol validation.**

### Detection (D)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| D.1 | FDD mode detected | YES | Agent announced "FDD mode: ENABLED" |
| D.2 | Rules mode determined (STRICT/RELAXED) | YES | Agent announced rules mode with reason |

### Discovery (DI)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| DI.1 | Adapter discovery executed | YES | `fdd adapter-info` command was run |
| DI.2 | artifacts.json read and understood | YES | Agent listed systems/rules from registry |
| DI.3 | Rules directories explored | YES | Agent listed available artifact kinds |

### Clarification (CL)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| CL.1 | Target type clarified (artifact or code) | YES | Agent stated target type |
| CL.2 | Artifact type determined (PRD, DESIGN, etc.) | YES | Agent stated artifact kind |
| CL.3 | System context clarified | CONDITIONAL | If using rules, agent stated system |
| CL.4 | Rules context clarified | CONDITIONAL | If multiple rules, agent stated which |

### Loading (L)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| L.1 | Rules.md loaded from correct path | YES | Agent stated `RULES_PATH` value |
| L.2 | Dependencies parsed and loaded | YES | Agent confirmed template/checklist/example loaded |
| L.3 | Requirements confirmed | YES | Agent listed understood requirements |
| L.4 | Adapter specs loaded | CONDITIONAL | Agent listed matched WHEN clauses and specs |

### Context (C)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| C.1 | Cross-reference context understood | YES | Agent identified parent/child/related artifacts |
| C.2 | Project context available | YES | Agent can reference project-specific information |

### Final (F)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| F.1 | All Detection checks pass | YES | D.1-D.2 verified |
| F.2 | All Discovery checks pass | YES | DI.1-DI.3 verified |
| F.3 | All Clarification checks pass | YES | CL.1-CL.4 verified (conditionals where applicable) |
| F.4 | All Loading checks pass | YES | L.1-L.4 verified (conditionals where applicable) |
| F.5 | All Context checks pass | YES | C.1-C.2 verified |
| F.6 | Ready to proceed to workflow-specific logic | YES | Agent has all required context loaded |
