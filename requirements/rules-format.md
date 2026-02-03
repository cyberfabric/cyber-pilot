---
spider: true
type: requirement
name: Spider Rules Format Specification
version: 1.0
purpose: Define rules.md format and workflow interaction protocol
---

# Spider Rules Format Specification

---

## Table of Contents

- [Agent Instructions](#agent-instructions)
- [Overview](#overview)
- [Weaver Packages](#weaver-packages)
- [Weaver Discovery](#weaver-discovery)
- [Rules.md Format](#rulesmd-format)
- [Workflow Interaction Protocol](#workflow-interaction-protocol)
- [Parsing Rules.md](#parsing-rulesmd)
- [Workflow Bootstrap](#workflow-bootstrap)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)
- [References](#references)

---

## Agent Instructions

**ALWAYS open and follow**: This file WHEN creating or modifying rules.md files

**ALWAYS open and follow**: `execution-protocol.md` WHEN loading rules for workflows

**Prerequisite**: Agent confirms understanding before proceeding:
- [ ] Agent has read and understood this specification
- [ ] Agent understands rules.md is the single entry point for artifact/code types
- [ ] Agent will follow the required sections format
- [ ] Agent will parse Dependencies, Requirements, Tasks, and Validation sections correctly

---

## Overview

`rules.md` is the single entry point for each artifact/code type. It contains all requirements, tasks, and validation criteria that workflows need to generate or validate.

**Location** (path from `artifacts.json`):
- Artifacts: `{WEAVER_BASE}/artifacts/{ARTIFACT_TYPE}/rules.md`
- Codebase: `{WEAVER_BASE}/codebase/rules.md`

---

## Weaver Packages

Weaver packages are defined in `artifacts.json`:

```json
{
   "weavers": {
    "spider-sdlc": {
      "format": "Spider",
      "path": "weavers/sdlc"
    },
  },
  "systems": [
    {
      "name": "MySystem",
         "weaver": "spider-sdlc",  // ← references weaver package
      ...
    }
  ]
}
```

**Package resolution**:
1. Find system for target artifact in `artifacts.json`
2. Get `weaver` name from system (e.g., `"spider-sdlc"`)
3. Look up path from `weavers` section (e.g., `"weavers/sdlc"`)
4. Build full path: `{weaver_path}/artifacts/{ARTIFACT_TYPE}/rules.md`

---

## Weaver Discovery

### Path Resolution

Path comes from `artifacts.json`:
```
WEAVER_BASE = artifacts.json.weavers[{weaver_name}].path
```

**Directory structure** (relative to WEAVER_BASE):
```
{WEAVER_BASE}/
├── artifacts/
│   ├── {ARTIFACT_TYPE}/
│   │   ├── rules.md
│   │   ├── template.md
│   │   ├── checklist.md
│   │   └── examples/
│   │       └── example.md
│   └── ...
└── codebase/
    ├── rules.md
    └── checklist.md
```

**Example** (if `weavers["spider-sdlc"].path = "weavers/sdlc"`):
```
weavers/sdlc/
├── artifacts/
│   ├── PRD/rules.md
│   ├── DESIGN/rules.md
│   ├── ADR/rules.md
│   ├── DECOMPOSITION/rules.md
│   └── FEATURE/rules.md
└── codebase/rules.md
```

### Artifact Type Detection

Workflow determines artifact type from:

1. **Explicit parameter**: `spider generate PRD`
2. **From artifacts.json**: lookup artifact by path → get `kind`
   ```json
   { "path": "architecture/PRD.md", "kind": "PRD" }
   ```
3. **Codebase**: if path matches `codebase[].path` → CODE

---

## Rules.md Format

### Required Sections

```markdown
# {ARTIFACT} Rules

**Artifact**: {NAME}
**Purpose**: {description}

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation

---

## Requirements

### Structural Requirements
- [ ] requirement 1
- [ ] requirement 2

### Versioning Requirements
- [ ] versioning rule 1

### Semantic Requirements
**Reference**: `checklist.md` for detailed criteria
- [ ] semantic requirement 1

### Traceability Requirements (optional)
- [ ] traceability rule 1

---

## Tasks

### Phase 1: Setup
- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style

### Phase 2: Content Creation
- [ ] task 1
- [ ] task 2

### Phase 3: IDs and Structure
- [ ] Generate IDs
- [ ] Verify uniqueness

### Phase 4: Quality Check
- [ ] Self-review against checklist

---

## Validation

### Phase 1: Structural Validation
- [ ] validation check 1

### Phase 2: Semantic Validation
- [ ] validation check 2

### Validation Report
{report format}
```

---

## Workflow Interaction Protocol

### Generate Workflow

```
1. DETECT artifact type
   ↓
2. RESOLVE weaver package:
   - Find system in artifacts.json
   - Get weaver name (e.g., "spider-sdlc")
   - Look up path (e.g., "weavers/sdlc")
   ↓
3. LOAD rules.md from {rules_path}/artifacts/{TYPE}/rules.md
   ↓
4. PARSE Dependencies section
   ↓
5. LOAD each dependency:
   - template.md → structural reference
   - checklist.md → semantic guidance
   - examples/example.md → style reference
   ↓
6. CONFIRM Requirements section
   - Agent reads and confirms understanding
   - Checkboxes are confirmation markers
   ↓
7. EXECUTE Tasks section
   - Phase 1: Setup (load files)
   - Phase 2: Content Creation
   - Phase 3: IDs and Structure
   - Phase 4: Quality Check
   ↓
8. OUTPUT artifact
```

### Validate Workflow

```
1. DETECT artifact type from target file
   ↓
2. RESOLVE weaver package:
   - Find system in artifacts.json
   - Get weaver name (e.g., "spider-sdlc")
   - Look up path (e.g., "weavers/sdlc")
   ↓
3. LOAD rules.md from {rules_path}/artifacts/{TYPE}/rules.md
   ↓
4. PARSE Dependencies section
   ↓
5. LOAD each dependency:
   - template.md → for structural validation
   - checklist.md → for semantic validation
   - examples/example.md → for quality baseline
   ↓
6. EXECUTE Validation section
   - Phase 1: Structural Validation (deterministic)
   - Phase 2: Semantic Validation (checklist-based)
   - Phase 3: Traceability Validation (if applicable)
   ↓
7. OUTPUT Validation Report
```

---

## Parsing Rules.md

### Dependencies Extraction

```regex
^\*\*Dependencies\*\*:\s*$
```

Following lines until `---`:
```regex
^-\s+`([^`]+)`\s+—\s+(.+)$
```
- Group 1: relative path
- Group 2: description

### Requirements Extraction

Sections starting with `### *Requirements`:
- Each `- [ ]` line is a requirement
- Agent must confirm understanding

### Tasks Extraction

Sections starting with `### Phase N:`:
- Each `- [ ]` line is a task to execute
- Execute in order

### Validation Extraction

Sections starting with `### Phase N:` under `## Validation`:
- Each `- [ ]` line is a validation check
- Report pass/fail for each

---

## Workflow Bootstrap

When workflow starts, it should:

1. **Check context**: Is this an Spider-managed project?
   - Look for `.spider-adapter/` directory
   - Read `.spider-adapter/artifacts.json`

2. **If Spider context detected**:
   - Parse `weavers` section from artifacts.json
   - Find system for target artifact
   - Resolve `WEAVER_BASE` from system's weaver reference
   - Load appropriate rules.md
   - Follow interaction protocol

3. **If no Spider context**:
   - Proceed with standard workflow
   - No rules.md loading

---

## Example: Generate PRD

```
User: spider generate PRD

Workflow:
1. Artifact type: PRD (explicit)
2. Resolve weaver:
   - System "Spider" uses weaver "spider-sdlc"
   - weavers["spider-sdlc"].path = "weavers/sdlc"
3. Load: weavers/sdlc/artifacts/PRD/rules.md
4. Parse Dependencies:
   - template.md
   - checklist.md
   - examples/example.md
5. Load all dependencies
6. Confirm Requirements:
   "I understand the following requirements:
   - PRD follows template.md structure
   - All IDs follow spd-{system}-{kind}-{slug} convention
   ..."
7. Execute Tasks:
   - Phase 1: Load template, checklist, example
   - Phase 2: Create content using example as reference
   - Phase 3: Generate actor/capability IDs
   - Phase 4: Self-review against checklist
8. Output: architecture/PRD.md
```

---

## Example: Validate FEATURE

```
User: spider validate architecture/features/auth.md

Workflow:
1. Artifact type: FEATURE (from path)
2. Resolve weaver:
   - Find system containing artifact
   - System "Spider" uses weaver "spider-sdlc"
   - weavers["spider-sdlc"].path = "weavers/sdlc"
3. Load: weavers/sdlc/artifacts/FEATURE/rules.md
4. Parse Dependencies
5. Load: template.md, checklist.md, examples/example.md
6. Execute Validation:
   - Phase 1: Structural (template compliance)
   - Phase 2: Semantic (checklist criteria)
   - Phase 3: Traceability (to_code markers)
7. Output: Validation Report
```

---

## Error Handling

### Weaver Package Not Found

**If weaver package path doesn't exist**:
```
⚠️ Weaver package not found: {weaver_path}
→ Referenced in: artifacts.json weavers["{name}"].path
→ Expected at: {WEAVER_BASE}
→ Fix: Create weaver package OR correct path in artifacts.json
```
**Action**: STOP — cannot load rules.md without package.

### Rules.md Parse Error

**If rules.md cannot be parsed**:
```
⚠️ Cannot parse rules.md: {path}
→ Error: {parse error description}
→ Check: Required sections present (Dependencies, Requirements, Tasks, Validation)
→ Check: Markdown syntax is valid
```
**Action**: STOP — cannot execute workflow without valid rules.

### Missing Dependency File

**If file referenced in Dependencies section doesn't exist**:
```
⚠️ Dependency not found: {dependency_path}
→ Referenced in: {rules_path}/rules.md Dependencies section
→ Expected at: {resolved_path}
→ Fix: Create dependency file OR remove from Dependencies
```
**Action**: STOP — cannot proceed without required dependencies.

### Malformed Section

**If required section is malformed**:
```
⚠️ Malformed section in rules.md: {section_name}
→ Location: {rules_path}
→ Expected format: {expected format description}
→ Found: {actual content}
```
**Action**: STOP — section must follow required format.

### Unknown Artifact Type

**If artifact type has no rules.md**:
```
⚠️ No rules found for artifact type: {ARTIFACT_TYPE}
→ Searched: {WEAVER_BASE}/artifacts/{ARTIFACT_TYPE}/rules.md
→ Available types: {list from directory}
→ Fix: Create rules.md for type OR use existing type
```
**Action**: STOP — cannot generate/validate without rules.

---

## Consolidated Validation Checklist

**Use this single checklist for all rules.md validation.**

### Structure (S)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| S.1 | rules.md exists at correct path | YES | File exists at `{WEAVER_BASE}/artifacts/{KIND}/rules.md` |
| S.2 | Has valid markdown frontmatter | YES | Artifact and Purpose fields present |
| S.3 | Dependencies section present | YES | `**Dependencies**:` heading exists |
| S.4 | Requirements section present | YES | `## Requirements` heading exists |
| S.5 | Tasks section present | YES | `## Tasks` heading exists |
| S.6 | Validation section present | YES | `## Validation` heading exists |

### Dependencies (D)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| D.1 | template.md referenced | YES | Listed in Dependencies section |
| D.2 | checklist.md referenced | YES | Listed in Dependencies section |
| D.3 | example.md referenced | YES | Listed in Dependencies section |
| D.4 | All referenced files exist | YES | Each path resolves to existing file |
| D.5 | Dependencies use correct format | YES | Matches `` `path` — description`` pattern |

### Requirements (R)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| R.1 | Structural Requirements subsection exists | YES | `### Structural Requirements` present |
| R.2 | Semantic Requirements subsection exists | YES | `### Semantic Requirements` present |
| R.3 | Each requirement is checkable | YES | Format: `- [ ] requirement text` |
| R.4 | Versioning Requirements present | CONDITIONAL | If artifact has versioning |
| R.5 | Traceability Requirements present | CONDITIONAL | If artifact has traceability |

### Tasks (T)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| T.1 | Phase 1: Setup subsection exists | YES | `### Phase 1: Setup` present |
| T.2 | Phase 2: Content Creation exists | YES | `### Phase 2: Content Creation` present |
| T.3 | Phase 3: IDs and Structure exists | YES | `### Phase 3: IDs and Structure` present |
| T.4 | Phase 4: Quality Check exists | YES | `### Phase 4: Quality Check` present |
| T.5 | Each task is checkable | YES | Format: `- [ ] task text` |
| T.6 | Tasks reference dependencies | YES | Setup phase loads template/checklist/example |

### Validation (V)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| V.1 | Phase 1: Structural Validation exists | YES | Subsection present |
| V.2 | Phase 2: Semantic Validation exists | YES | Subsection present |
| V.3 | Validation Report format defined | YES | `### Validation Report` present |
| V.4 | Each validation check is checkable | YES | Format: `- [ ] check text` |

### Final (F)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| F.1 | All Structure checks pass | YES | S.1-S.6 verified |
| F.2 | All Dependencies checks pass | YES | D.1-D.5 verified |
| F.3 | All Requirements checks pass | YES | R.1-R.5 verified (conditionals where applicable) |
| F.4 | All Tasks checks pass | YES | T.1-T.6 verified |
| F.5 | All Validation checks pass | YES | V.1-V.4 verified |

---

## References

- **Rules registry**: `{adapter_dir}/artifacts.json` → `rules` section
- **Artifact rules**: `{rules_path}/artifacts/{KIND}/rules.md`
- **Codebase rules**: `{rules_path}/codebase/rules.md`
- **Template spec**: `requirements/template.md`
- **Execution protocol**: `requirements/execution-protocol.md`
