---
spider: true
type: requirement
name: Artifacts Registry
version: 1.0
purpose: Define structure and usage of artifacts.json for agent operations
---

# Spider Artifacts Registry Specification

---

## Table of Contents

- [Agent Instructions](#agent-instructions)
- [Overview](#overview)
- [Schema Version](#schema-version)
- [Root Structure](#root-structure)
- [Rules](#rules)
- [Systems](#systems)
- [Artifacts](#artifacts)
- [Codebase](#codebase)
- [Path Resolution](#path-resolution)
- [CLI Commands](#cli-commands)
- [Agent Operations](#agent-operations)
- [Error Handling](#error-handling)
- [Example Registry](#example-registry)
- [Common Issues](#common-issues)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)
- [References](#references)

---

## Agent Instructions

**Add to adapter AGENTS.md** (path relative to adapter directory):
```
ALWAYS open and follow `{Spider}/requirements/artifacts-registry.md` WHEN working with artifacts.json
```
Where `{Spider}` is resolved from the adapter's `**Extends**:` declaration.

**ALWAYS use**: `python3 {Spider}/skills/spider/scripts/spider.py adapter-info` to discover adapter location

**ALWAYS use**: `spider.py` CLI commands for artifact operations (list-ids, where-defined, where-used, validate)

**Prerequisite**: Agent confirms understanding before proceeding:
- [ ] Agent has read and understood this requirement
- [ ] Agent knows where artifacts.json is located (via adapter-info)
- [ ] Agent will use CLI commands, not direct file manipulation

---

## Overview

**What**: `artifacts.json` is the Spider artifact registry - a JSON file that declares all Spider artifacts, their templates, and codebase locations.

**Location**: `{adapter-directory}/artifacts.json`

**Purpose**:
- Maps artifacts to their templates for validation and parsing
- Defines system hierarchy (systems → subsystems → components)
- Specifies codebase directories for traceability
- Enables CLI tools to discover and process artifacts automatically

---

## Schema Version

Current version: `1.0`

Schema file: `../schemas/artifacts.schema.json`

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
| `weavers` | object | YES | Weaver package registry |
| `systems` | array | YES | Root-level system nodes |

---

## Weavers

**Purpose**: Define weaver packages that can be referenced by systems.

**Structure**:
```json
{
  "weavers": {
    "weaver-id": {
      "format": "Spider",
      "path": "weavers/sdlc"
    }
  }
}
```

### Weaver Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `format` | string | YES | Template format. `"Spider"` = full tooling support. Other values = custom (LLM-only) |
| `path` | string | YES | Path to weaver package directory (relative to project_root). Contains `artifacts/` and `codebase/` subdirectories. |

### Template Resolution

Template file path is resolved as: `{weaver.path}/artifacts/{KIND}/template.md`

**Example**: For artifact with `kind: "PRD"` and weaver with `path: "weavers/sdlc"`:
- Template path: `{project-root}/weavers/sdlc/artifacts/PRD/template.md`
- Checklist path: `{project-root}/weavers/sdlc/artifacts/PRD/checklist.md`
- Example path: `{project-root}/weavers/sdlc/artifacts/PRD/examples/example.md`

### Format Values

| Format | Meaning |
|--------|---------|
| `"Spider"` | Full Spider tooling support: validation, parsing, ID extraction |
| Other | Custom format: LLM-only semantic processing, no CLI validation |

**Agent behavior**:
- `format: "Spider"` → Use `spider validate`, `list-ids`, `where-defined`, etc.
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
      "weaver": "weaver-id",
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
| `weaver` | string | YES | Reference to weaver ID from `weavers` section |
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

**Purpose**: Declare documentation artifacts (PRD, DESIGN, ADR, DECOMPOSITION, FEATURE).

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
| `kind` | string | YES | - | Artifact kind (PRD, DESIGN, ADR, DECOMPOSITION, FEATURE) |
| `traceability` | string | NO | `"FULL"` | Traceability level |

### Path Requirements

**CRITICAL**: `path` MUST be a file path, NOT a directory.

**Valid**:

```text
architecture/PRD.md
architecture/ADR/0001-initial-architecture.md
```

**Invalid**:

```text
architecture/ADR/    # directory
architecture/ADR     # no extension = likely directory
```

### Traceability Values

| Value | Meaning | Agent Behavior |
|-------|---------|----------------|
| `"FULL"` | Full traceability to codebase | Validate code markers, cross-reference IDs |
| `"DOCS-ONLY"` | Documentation-only tracing | Skip codebase traceability checks |

**Default**: `"FULL"` - assume full traceability unless explicitly set otherwise.

### Artifact Kinds

| Kind | Template Path | Description |
|------|---------------|-------------|
| `PRD` | `{weaver.path}/artifacts/PRD/template.md` | Product Requirements Document |
| `DESIGN` | `{weaver.path}/artifacts/DESIGN/template.md` | Overall Design (system-level) |
| `ADR` | `{weaver.path}/artifacts/ADR/template.md` | Architecture Decision Record |
| `FEATURES` | `{weaver.path}/artifacts/DECOMPOSITION/template.md` | Features Manifest |
| `FEATURE` | `{weaver.path}/artifacts/FEATURE/template.md` | Feature Design (feature-level) |

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
      "extensions": [".ts", ".tsx"],
      "singleLineComments": ["//"],
      "multiLineComments": [{"start": "/*", "end": "*/"}]
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
| `singleLineComments` | array | NO | Single-line comment prefixes (e.g., `["#", "//"]`). Defaults based on file extension. |
| `multiLineComments` | array | NO | Multi-line comment delimiters. Each item has `start` and `end` properties. Defaults based on file extension. |

### Extension Format

Extensions MUST start with a dot and contain only alphanumeric characters.

**Valid**: `.py`, `.ts`, `.tsx`, `.rs`

**Invalid**: `py`, `*.py`, `.foo-bar`

### Comment Syntax Configuration

Comment syntax can be explicitly configured per codebase entry, or left to default based on file extension.

**Multi-line comment structure**:
```json
{
  "start": "/*",
  "end": "*/"
}
```

**Common configurations**:

| Language | Single-line | Multi-line |
|----------|-------------|------------|
| Python | `["#"]` | `[{"start": "\"\"\"", "end": "\"\"\""}]` |
| JavaScript/TypeScript | `["//"]` | `[{"start": "/*", "end": "*/"}]` |
| Rust | `["//"]` | `[{"start": "/*", "end": "*/"}]` |
| HTML | — | `[{"start": "<!--", "end": "-->"}]` |
| CSS | — | `[{"start": "/*", "end": "*/"}]` |

**When to configure explicitly**:
- Non-standard file extensions
- Mixed-language files
- Custom comment syntax
- Overriding defaults for specific directories

---

## Path Resolution

All paths in artifacts and codebase are resolved relative to `project_root`.

**Resolution formula**: `{adapter_dir}/{project_root}/{path}`

**Example**:
```
artifacts.json location: /project/.spider-adapter/artifacts.json
project_root: ".."
artifact path: "architecture/PRD.md"

Resolved: /project/.spider-adapter/../architecture/PRD.md
       → /project/architecture/PRD.md
```

---

## CLI Commands

**Note**: All commands use `python3 {Spider}/skills/spider/scripts/spider.py` where `{Spider}` is the Spider installation path. Examples below use `spider.py` as shorthand.

### Discovery

```bash
# Find adapter and registry
spider.py adapter-info --root /project
```

### Artifact Operations

```bash
# List all IDs from registered Spider artifacts
spider.py list-ids

# List IDs from specific artifact
spider.py list-ids --artifact architecture/PRD.md

# Find where ID is defined
spider.py where-defined --id "myapp-actor-user"

# Find where ID is referenced
spider.py where-used --id "myapp-actor-user"

# Validate artifact against template
spider.py validate --artifact architecture/PRD.md

# Validate all registered artifacts
spider.py validate

# Validate weavers and templates
spider.py validate-weavers
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
# For artifact with kind="PRD" in system with weaver="spider-sdlc"
weaver = registry.weavers["spider-sdlc"]
template_path = f"{weaver.path}/artifacts/{artifact.kind}/template.md"
# → "weavers/sdlc/artifacts/PRD/template.md"
```

### Checking Format

```python
weaver = registry.weavers[system.weaver]
if weaver.format == "Spider":
    # Use CLI validation
    run("spider validate --artifact {path}")
else:
    # Custom format - LLM-only processing
    process_semantically(artifact)
```

---

## Error Handling

### artifacts.json Not Found

**If artifacts.json doesn't exist at adapter location**:
```
⚠️ Registry not found: {adapter_dir}/artifacts.json
→ Adapter exists but registry not initialized
→ Fix: Run /spider-adapter to create registry
```
**Action**: STOP — cannot process artifacts without registry.

### JSON Parse Error

**If artifacts.json contains invalid JSON**:
```
⚠️ Invalid JSON in artifacts.json: {parse error}
→ Check for trailing commas, missing quotes, or syntax errors
→ Fix: Validate JSON with online validator or IDE
```
**Action**: STOP — cannot process malformed registry.

### Missing Weaver Reference

**If system references non-existent weaver**:
```
⚠️ Invalid weaver reference: system "MyApp" references weaver "custom-weaver" not in weavers section
→ Fix: Add weaver to weavers section OR change system.weaver to an existing weaver ID
```
**Action**: FAIL validation for that system, continue with others.

### Artifact File Not Found

**If registered artifact file doesn't exist**:
```
⚠️ Artifact not found: architecture/PRD.md
→ Registered in artifacts.json but file missing
→ Fix: Create file OR remove from registry
```
**Action**: WARN and skip artifact, continue with others.

### Template Not Found

**If template for artifact kind doesn't exist**:
```
⚠️ Template not found: weavers/sdlc/artifacts/PRD/template.md
→ Kind "PRD" registered but template missing
→ Fix: Create template OR use different weaver package
```
**Action**: FAIL validation for that artifact, continue with others.

---

## Example Registry

```json
{
  "version": "1.0",
  "project_root": "..",
  "rules": {
    "spider-sdlc": {
      "format": "Spider",
      "path": "weavers/sdlc"
    }
  },
  "systems": [
    {
      "name": "MyApp",
      "rules": "spider-sdlc",
      "artifacts": [
        { "name": "Product Requirements", "path": "architecture/PRD.md", "kind": "PRD", "traceability": "DOCS-ONLY" },
        { "name": "Overall Design", "path": "architecture/DESIGN.md", "kind": "DESIGN", "traceability": "FULL" },
        { "name": "Initial Architecture", "path": "architecture/ADR/0001-initial-architecture.md", "kind": "ADR", "traceability": "DOCS-ONLY" },
        { "name": "Design Decomposition", "path": "architecture/DECOMPOSITION.md", "kind": "DECOMPOSITION", "traceability": "DOCS-ONLY" }
      ],
      "codebase": [
        {
          "name": "Source Code",
          "path": "src",
          "extensions": [".ts", ".tsx"],
          "singleLineComments": ["//"],
          "multiLineComments": [{"start": "/*", "end": "*/"}]
        }
      ],
      "children": [
        {
          "name": "Auth",
          "rules": "spider-sdlc",
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
| "Artifact not in Spider registry" | Path not registered | Add artifact to system's artifacts array |
| "Could not find template" | Missing template file | Create template at `{rules.path}/artifacts/{KIND}/template.md` |
| "Invalid rule reference" | System references non-existent rule | Add rule to `rules` section |
| "Path is a directory" | Artifact path ends with `/` or has no extension | Change to specific file path |

---

## References

**Schema**: `../schemas/artifacts.schema.json`

**CLI**: `skills/spider/spider.clispec`

**Related**:
- `adapter-structure.md` - Adapter AGENTS.md requirements
- `execution-protocol.md` - Workflow execution protocol

---

## Consolidated Validation Checklist

**Use this single checklist for all artifacts.json validation.**

### Registry Structure (R)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| R.1 | artifacts.json exists at adapter location | YES | File exists at `{adapter_dir}/artifacts.json` |
| R.2 | JSON parses without errors | YES | `json.loads()` succeeds |
| R.3 | `version` field present and non-empty | YES | Field exists and is string |
| R.4 | `rules` object present with ≥1 rule | YES | Object with at least one key |
| R.5 | `systems` array present | YES | Array (may be empty) |
| R.6 | Each rule has `format` and `path` fields | YES | Both fields exist per rule |
| R.7 | Each system has `name` and `rules` fields | YES | Both fields exist per system |
| R.8 | System `rules` references exist in rules section | YES | Lookup succeeds |

### Artifact Entries (A)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| A.1 | Each artifact has `path` and `kind` fields | YES | Both fields exist |
| A.2 | Artifact paths are files, not directories | YES | Path has extension, doesn't end with `/` |
| A.3 | Artifact kinds are valid | YES | One of: PRD, DESIGN, ADR, DECOMPOSITION, FEATURE |
| A.4 | Artifact files exist (if validating content) | CONDITIONAL | File exists at resolved path |

### Codebase Entries (C)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| C.1 | Each codebase entry has `path` and `extensions` | YES | Both fields exist |
| C.2 | Extensions array is non-empty | YES | Array length > 0 |
| C.3 | Each extension starts with `.` | YES | Regex: `^\.[a-zA-Z0-9]+$` |
| C.4 | Comment syntax format valid (if specified) | CONDITIONAL | Arrays of strings, multi-line has start/end |

### Final (F)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| F.1 | All Registry Structure checks pass | YES | R.1-R.8 verified |
| F.2 | All Artifact Entries checks pass | YES | A.1-A.4 verified |
| F.3 | All Codebase Entries checks pass | YES | C.1-C.4 verified |
