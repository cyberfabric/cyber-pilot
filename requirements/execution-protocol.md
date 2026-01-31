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

**If adapter not found**:
```
⚠ Adapter not found
→ Run /fdd-adapter to bootstrap
```

---

## Validation Criteria

- [ ] FDD mode detected
- [ ] Adapter discovery executed
- [ ] artifacts.json read and understood
- [ ] Rules directories explored
- [ ] Target type clarified (artifact or code)
- [ ] Artifact type determined (PRD, DESIGN, etc.)
- [ ] Rules.md loaded from correct path
- [ ] Dependencies parsed and loaded (template, checklist, example)
- [ ] Requirements confirmed
- [ ] Rules context clarified (if applicable)
- [ ] System context clarified (if using rules)
- [ ] Cross-reference context understood
