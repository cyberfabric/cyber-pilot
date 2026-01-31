---
fdd: true
type: requirement
name: Artifacts Registry
version: 1.0
purpose: Define structure and usage of artifacts.json for agent operations
---

# FDD Artifacts Registry Specification

---

## Agent Instructions

**Add to adapter AGENTS.md**:
```
ALWAYS open and follow `../requirements/artifacts-registry.md` WHEN working with artifacts.json
```

**ALWAYS use**: `fdd.py adapter-info` to discover adapter location

**ALWAYS use**: `fdd.py` CLI commands for artifact operations (list-ids, where-defined, where-used, validate)

---

## Prerequisite Checklist

- [ ] Agent has read and understood this requirement
- [ ] Agent knows where artifacts.json is located (via adapter-info)
- [ ] Agent will use CLI commands, not direct file manipulation

---

## Overview

**What**: `artifacts.json` is the FDD artifact registry - a JSON file that declares all FDD artifacts, their templates, and codebase locations.

**Location**: `{adapter-directory}/artifacts.json`

**Purpose**:
- Maps artifacts to their templates for validation and parsing
- Defines system hierarchy (systems → subsystems → components)
- Specifies codebase directories for traceability
- Enables CLI tools to discover and process artifacts automatically

---

## Schema Version

Current version: `1.0`

Schema file: `schemas/artifacts.schema.json`

---

## Root Structure

```json
{
  "version": "1.0",
  "project_root": "..",
  "rules": { ... },
  "systems": [ ... ]
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | YES | Schema version (currently "1.0") |
| `project_root` | string | NO | Relative path from artifacts.json to project root. Default: `".."` |
| `rules` | object | YES | Template rules registry |
| `systems` | array | YES | Root-level system nodes |

---

## Rules

**Purpose**: Define template configurations that can be referenced by systems.

**Structure**:
```json
{
  "rules": {
    "rule-id": {
      "format": "FDD",
      "path": "rules/sdlc"
    }
  }
}
```

### Rule Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `format` | string | YES | Template format. `"FDD"` = full tooling support. Other values = custom (LLM-only) |
| `path` | string | YES | Path to rules package directory (relative to project_root). Contains `artifacts/` and `codebase/` subdirectories. |

### Template Resolution

Template file path is resolved as: `{rule.path}/artifacts/{KIND}/template.md`

**Example**: For artifact with `kind: "PRD"` and rule with `path: "rules/sdlc"`:
- Template path: `rules/sdlc/artifacts/PRD/template.md`
- Checklist path: `rules/sdlc/artifacts/PRD/checklist.md`
- Example path: `rules/sdlc/artifacts/PRD/examples/example.md`

### Format Values

| Format | Meaning |
|--------|---------|
| `"FDD"` | Full FDD tooling support: validation, parsing, ID extraction |
| Other | Custom format: LLM-only semantic processing, no CLI validation |

**Agent behavior**:
- `format: "FDD"` → Use `fdd validate`, `list-ids`, `where-defined`, etc.
- Other format → Skip CLI validation, process semantically

---

## Systems

**Purpose**: Define hierarchical structure of the project.

**Structure**:
```json
{
  "systems": [
    {
      "name": "SystemName",
      "rules": "rule-id",
      "artifacts": [ ... ],
      "codebase": [ ... ],
      "children": [ ... ]
    }
  ]
}
```

### System Node Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | YES | System/subsystem/component name |
| `rules` | string | YES | Reference to rule ID from `rules` section |
| `artifacts` | array | NO | Artifacts belonging to this node |
| `codebase` | array | NO | Source code directories for this node |
| `children` | array | NO | Nested child systems (subsystems, components) |

### Hierarchy Usage

```
System (root)
├── artifacts (system-level PRD, DESIGN, etc.)
├── codebase (system-level source directories)
└── children
    └── Subsystem
        ├── artifacts (subsystem-level docs)
        ├── codebase (subsystem source)
        └── children
            └── Component
                └── ...
```

**Agent behavior**:
- Iterate systems recursively to find all artifacts
- Use system name for context in reports
- Respect system boundaries for traceability

---

## Artifacts

**Purpose**: Declare documentation artifacts (PRD, DESIGN, ADR, FEATURES, FEATURE).

**Structure**:
```json
{
  "artifacts": [
    {
      "name": "Product Requirements",
      "path": "architecture/PRD.md",
      "kind": "PRD",
      "traceability": "FULL"
    }
  ]
}
```

### Artifact Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | NO | - | Human-readable name (for display) |
| `path` | string | YES | - | Path to artifact file (relative to project_root) |
| `kind` | string | YES | - | Artifact kind (PRD, DESIGN, ADR, FEATURES, FEATURE) |
| `traceability` | string | NO | `"FULL"` | Traceability level |

### Path Requirements

**CRITICAL**: `path` MUST be a file path, NOT a directory.

**Valid**:
- `architecture/PRD.md`
- `architecture/ADR/0001-initial-architecture.md`

**Invalid**:
- `architecture/ADR/` (directory)
- `architecture/ADR` (no extension = likely directory)

### Traceability Values

| Value | Meaning | Agent Behavior |
|-------|---------|----------------|
| `"FULL"` | Full traceability to codebase | Validate code markers, cross-reference IDs |
| `"DOCS-ONLY"` | Documentation-only tracing | Skip codebase traceability checks |

**Default**: `"FULL"` - assume full traceability unless explicitly set otherwise.

### Artifact Kinds

| Kind | Template Path | Description |
|------|---------------|-------------|
| `PRD` | `artifacts/PRD/template.md` | Product Requirements Document |
| `DESIGN` | `artifacts/DESIGN/template.md` | Overall Design (system-level) |
| `ADR` | `artifacts/ADR/template.md` | Architecture Decision Record |
| `FEATURES` | `artifacts/FEATURES/template.md` | Features Manifest |
| `FEATURE` | `artifacts/FEATURE/template.md` | Feature Design (feature-level) |

---

## Codebase

**Purpose**: Declare source code directories for traceability scanning.

**Structure**:
```json
{
  "codebase": [
    {
      "name": "Source Code",
      "path": "src",
      "extensions": [".ts", ".tsx"]
    }
  ]
}
```

### Codebase Entry Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | NO | Human-readable name (for display) |
| `path` | string | YES | Path to source directory (relative to project_root) |
| `extensions` | array | YES | File extensions to include (e.g., `[".py", ".ts"]`) |

### Extension Format

Extensions MUST start with a dot and contain only alphanumeric characters.

**Valid**: `.py`, `.ts`, `.tsx`, `.rs`

**Invalid**: `py`, `*.py`, `.foo-bar`

---

## Path Resolution

All paths in artifacts and codebase are resolved relative to `project_root`.

**Resolution formula**: `{adapter_dir}/{project_root}/{path}`

**Example**:
```
artifacts.json location: /project/.adapter/artifacts.json
project_root: ".."
artifact path: "architecture/PRD.md"

Resolved: /project/.adapter/../architecture/PRD.md
       → /project/architecture/PRD.md
```

---

## CLI Commands

### Discovery

```bash
# Find adapter and registry
python3 scripts/fdd.py adapter-info --root /project
```

### Artifact Operations

```bash
# List all IDs from registered FDD artifacts
python3 scripts/fdd.py list-ids

# List IDs from specific artifact
python3 scripts/fdd.py list-ids --artifact architecture/PRD.md

# Find where ID is defined
python3 scripts/fdd.py where-defined --id "myapp-actor-user"

# Find where ID is referenced
python3 scripts/fdd.py where-used --id "myapp-actor-user"

# Validate artifact against template
python3 scripts/fdd.py validate --artifact architecture/PRD.md

# Validate all registered artifacts
python3 scripts/fdd.py validate

# Validate rules and templates
python3 scripts/fdd.py validate-rules
```

---

## Agent Operations

### Finding the Registry

1. Run `adapter-info` to discover adapter location
2. Registry is at `{adapter_dir}/artifacts.json`
3. Parse JSON to get registry data

### Iterating Artifacts

```python
# Pseudocode for agent logic
for system in registry.systems:
    for artifact in system.artifacts:
        process(artifact, system)
    for child in system.children:
        recurse(child)
```

### Resolving Template Path

```python
# For artifact with kind="PRD" in system with rules="fdd-sdlc"
rule = registry.rules["fdd-sdlc"]
template_path = f"{rule.path}/artifacts/{artifact.kind}/template.md"
# → "rules/sdlc/artifacts/PRD/template.md"
```

### Checking Format

```python
rule = registry.rules[system.rules]
if rule.format == "FDD":
    # Use CLI validation
    run("fdd validate --artifact {path}")
else:
    # Custom format - LLM-only processing
    process_semantically(artifact)
```

---

## Validation Criteria

### Registry Structure

- [ ] `version` field present and non-empty
- [ ] `rules` object present with at least one rule
- [ ] `systems` array present (may be empty)
- [ ] Each rule has `format` and `path` fields
- [ ] Each system has `name` and `rules` fields
- [ ] Each system's `rules` references existing rule ID

### Artifact Entries

- [ ] Each artifact has `path` and `kind` fields
- [ ] Artifact paths are files, not directories
- [ ] Artifact paths have file extensions
- [ ] Artifact kinds match expected values (PRD, DESIGN, ADR, FEATURES, FEATURE)

### Codebase Entries

- [ ] Each codebase entry has `path` and `extensions` fields
- [ ] Extensions array is non-empty
- [ ] Each extension starts with `.`

---

## Example Registry

```json
{
  "version": "1.0",
  "project_root": "..",
  "rules": {
    "fdd-sdlc": {
      "format": "FDD",
      "path": "rules/sdlc"
    }
  },
  "systems": [
    {
      "name": "MyApp",
      "rules": "fdd-sdlc",
      "artifacts": [
        { "name": "Product Requirements", "path": "architecture/PRD.md", "kind": "PRD", "traceability": "DOCS-ONLY" },
        { "name": "Overall Design", "path": "architecture/DESIGN.md", "kind": "DESIGN", "traceability": "FULL" },
        { "name": "Initial Architecture", "path": "architecture/ADR/0001-initial-architecture.md", "kind": "ADR", "traceability": "DOCS-ONLY" },
        { "name": "Features Manifest", "path": "architecture/features/FEATURES.md", "kind": "FEATURES", "traceability": "DOCS-ONLY" }
      ],
      "codebase": [
        { "name": "Source Code", "path": "src", "extensions": [".ts", ".tsx"] }
      ],
      "children": [
        {
          "name": "Auth",
          "rules": "fdd-sdlc",
          "artifacts": [
            { "path": "modules/auth/architecture/PRD.md", "kind": "PRD", "traceability": "DOCS-ONLY" },
            { "path": "modules/auth/architecture/features/feature-sso/DESIGN.md", "kind": "FEATURE", "traceability": "FULL" }
          ],
          "children": []
        }
      ]
    }
  ]
}
```

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| "Artifact not in FDD registry" | Path not registered | Add artifact to system's artifacts array |
| "Could not find template" | Missing template file | Create template at `{rules.path}/artifacts/{KIND}/template.md` |
| "Invalid rule reference" | System references non-existent rule | Add rule to `rules` section |
| "Path is a directory" | Artifact path ends with `/` or has no extension | Change to specific file path |

---

## References

**Schema**: `schemas/artifacts.schema.json`

**CLI**: `skills/fdd/fdd.clispec`

**Related**:
- `adapter-structure.md` - Adapter AGENTS.md requirements
- `execution-protocol.md` - Workflow execution protocol

---

## Validation Checklist

- [ ] artifacts.json exists at `{adapter-directory}/artifacts.json`
- [ ] JSON parses without errors
- [ ] Version field is present and non-empty
- [ ] At least one rule is defined
- [ ] Each rule has format and path fields
- [ ] Each system has name and rules fields
- [ ] System rules references exist in rules section
- [ ] Artifact paths are files (not directories)
- [ ] Artifact kinds are valid (PRD, DESIGN, ADR, FEATURES, FEATURE)
- [ ] Codebase extensions start with dot
