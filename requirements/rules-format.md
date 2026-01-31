---
fdd: true
type: requirement
name: FDD Rules Format Specification
version: 1.0
purpose: Define rules.md format and workflow interaction protocol
---

# FDD Rules Format Specification

## Overview

`rules.md` is the single entry point for each artifact/code type. It contains all requirements, tasks, and validation criteria that workflows need to generate or validate.

**Location** (path from `artifacts.json`):
- Artifacts: `{RULES_BASE}/artifacts/{ARTIFACT_TYPE}/rules.md`
- Codebase: `{RULES_BASE}/codebase/rules.md`

---

## Rules Packages

Rules packages are defined in `artifacts.json`:

```json
{
  "rules": {
    "fdd-sdlc": {
      "format": "FDD",
      "path": "rules/sdlc"
    },
    "fdd-core": {
      "format": "FDD",
      "path": "rules/core"
    }
  },
  "systems": [
    {
      "name": "MySystem",
      "rules": "fdd-sdlc",  // ← references rules package
      ...
    }
  ]
}
```

**Package resolution**:
1. Find system for target artifact in `artifacts.json`
2. Get `rules` name from system (e.g., `"fdd-sdlc"`)
3. Look up path from `rules` section (e.g., `"rules/sdlc"`)
4. Build full path: `{rules_path}/artifacts/{ARTIFACT_TYPE}/rules.md`

---

## Rules Discovery

### Path Resolution

Path comes from `artifacts.json`:
```
RULES_BASE = artifacts.json.rules[{rules_name}].path
```

**Directory structure** (relative to RULES_BASE):
```
{RULES_BASE}/
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

**Example** (if `rules["fdd-sdlc"].path = "rules/sdlc"`):
```
rules/sdlc/
├── artifacts/
│   ├── PRD/rules.md
│   ├── DESIGN/rules.md
│   ├── ADR/rules.md
│   ├── FEATURES/rules.md
│   └── FEATURE/rules.md
└── codebase/rules.md
```

### Artifact Type Detection

Workflow determines artifact type from:

1. **Explicit parameter**: `fdd generate PRD`
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
2. RESOLVE rules package:
   - Find system in artifacts.json
   - Get rules name (e.g., "fdd-sdlc")
   - Look up path (e.g., "rules/sdlc")
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
2. RESOLVE rules package:
   - Find system in artifacts.json
   - Get rules name (e.g., "fdd-sdlc")
   - Look up path (e.g., "rules/sdlc")
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

1. **Check context**: Is this an FDD-managed project?
   - Look for `.adapter/` directory
   - Read `.adapter/artifacts.json`

2. **If FDD context detected**:
   - Parse `rules` section from artifacts.json
   - Find system for target artifact
   - Resolve `RULES_BASE` from system's rules reference
   - Load appropriate rules.md
   - Follow interaction protocol

3. **If no FDD context**:
   - Proceed with standard workflow
   - No rules.md loading

---

## Example: Generate PRD

```
User: fdd generate PRD

Workflow:
1. Artifact type: PRD (explicit)
2. Resolve rules:
   - System "FDD" uses rules "fdd-sdlc"
   - rules["fdd-sdlc"].path = "rules/sdlc"
3. Load: rules/sdlc/artifacts/PRD/rules.md
4. Parse Dependencies:
   - template.md
   - checklist.md
   - examples/example.md
5. Load all dependencies
6. Confirm Requirements:
   "I understand the following requirements:
   - PRD follows template.md structure
   - All IDs follow fdd-{project}-{kind}-{slug} convention
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
User: fdd validate architecture/features/auth.md

Workflow:
1. Artifact type: FEATURE (from path)
2. Resolve rules:
   - Find system containing artifact
   - System "FDD" uses rules "fdd-sdlc"
   - rules["fdd-sdlc"].path = "rules/sdlc"
3. Load: rules/sdlc/artifacts/FEATURE/rules.md
4. Parse Dependencies
5. Load: template.md, checklist.md, examples/example.md
6. Execute Validation:
   - Phase 1: Structural (template compliance)
   - Phase 2: Semantic (checklist criteria)
   - Phase 3: Traceability (to_code markers)
7. Output: Validation Report
```

---

## References

- **Rules registry**: `{adapter_dir}/artifacts.json` → `rules` section
- **Artifact rules**: `{rules_path}/artifacts/{KIND}/rules.md`
- **Codebase rules**: `{rules_path}/codebase/rules.md`
- **Template spec**: `requirements/template.md`
