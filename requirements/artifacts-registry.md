---
cypilot: true
type: requirement
name: Artifacts Registry
version: 1.0
purpose: Define structure and usage of artifacts.json for agent operations
---

# Cypilot Artifacts Registry Specification

---

## Table of Contents

- [Agent Instructions](#agent-instructions)
- [Overview](#overview)
- [Schema Version](#schema-version)
- [Root Structure](#root-structure)
- [Kits](#kits)
- [Systems](#systems)
- [Artifacts](#artifacts)
- [Codebase](#codebase)
- [Autodetect (Proposed)](#autodetect-proposed)
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
ALWAYS open and follow `{cypilot_path}/requirements/artifacts-registry.md` WHEN working with artifacts.json
```
Where `{cypilot_path}` is resolved from the adapter's `**Extends**:` declaration.

**ALWAYS use**: `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py adapter-info` to discover adapter location

**ALWAYS use**: `cypilot.py` CLI commands for artifact operations (list-ids, where-defined, where-used, validate)

**Prerequisite**: Agent confirms understanding before proceeding:
- [ ] Agent has read and understood this requirement
- [ ] Agent knows where artifacts.json is located (via adapter-info)
- [ ] Agent will use CLI commands, not direct file manipulation

---

## Overview

**What**: `artifacts.json` is the Cypilot artifact registry - a JSON file that declares all Cypilot artifacts, their templates, and codebase locations.

**Location**: `{adapter-directory}/artifacts.json`

**Purpose**:
- Maps artifacts to their templates for validation and parsing
- Defines system hierarchy (systems → subsystems → components)
- Specifies codebase directories for traceability
- Enables CLI tools to discover and process artifacts automatically

---

## Schema Version

Current version: `1.0`

Proposed version: `1.1` (adds `autodetect`)

Schema file: `../schemas/artifacts.schema.json`

Notes:

- Registry files with `version: "1.0"` MUST continue to work.
- If `autodetect` is used, the registry version SHOULD be set to `"1.1"` and the JSON Schema MUST be updated accordingly.

---

## Root Structure

```json
{
  "version": "1.0",
  "project_root": "..",
  "kits": { ... },
  "ignore": [ ... ],
  "systems": [ ... ]
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | YES | Schema version (currently "1.0") |
| `project_root` | string | NO | Relative path from artifacts.json to project root. Default: `".."` |
| `kits` | object | YES | Kit package registry |
| `ignore` | array | NO | Global ignore rules (visibility filter) applied to all CLI operations and autodetect scanning. |
| `systems` | array | YES | Root-level system nodes |

### Root Ignore (Visibility Filter)

If `ignore` is present at the registry root, it defines paths that are **globally invisible** to:

- Autodetect directory scanning
- Codebase traceability scanning
- CLI commands that traverse artifacts/codebase (`validate`, `list-ids`, `where-defined`, `where-used`)

Ignore items are blocks with:

- `reason` (string)
- `patterns` (array of glob strings, resolved relative to `project_root`)

This is a hard filter: the tool behaves as if ignored paths do not exist.

---

## Kits

**Purpose**: Define kit packages that can be referenced by systems.

**Structure**:
```json
{
  "kits": {
    "kit-id": {
      "format": "Cypilot",
      "path": "kits/sdlc",
      "artifacts": {
        "PRD": {
          "template": "{project_root}/kits/sdlc/artifacts/PRD/template.md",
          "examples": "{project_root}/kits/sdlc/artifacts/PRD/examples"
        }
      }
    }
  }
}
```

### Kit Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `format` | string | YES | Template format. `"Cypilot"` = full tooling support. Other values = custom (LLM-only) |
| `path` | string | YES | Path to kit package directory (relative to project_root). Contains `artifacts/` and `codebase/` subdirectories. |
| `artifacts` | object | NO | Optional explicit artifact template/example locations. Mapping `KIND -> {template, examples}`. Supports `{project_root}` token. |

### Template Resolution

Template file path resolution (precedence order):

1. If `kits[kit-id].artifacts[KIND].template` is present, use it.
2. Otherwise, resolve as: `{kit.path}/artifacts/{KIND}/template.md`

Examples directory resolution (precedence order):

1. If `kits[kit-id].artifacts[KIND].examples` is present, use it.
2. Otherwise, resolve as: `{kit.path}/artifacts/{KIND}/examples`

`{project_root}` token:

- In `kits[*].artifacts[*].template/examples`, `{project_root}` expands to the project root directory.
- These paths are still resolved relative to the actual project root (it is effectively a convenience prefix).

**Example**: For artifact with `kind: "PRD"` and kit with `path: "kits/sdlc"`:
- Template path: `{project-root}/kits/sdlc/artifacts/PRD/template.md`
- Checklist path: `{project-root}/kits/sdlc/artifacts/PRD/checklist.md`
- Example path: `{project-root}/kits/sdlc/artifacts/PRD/examples/example.md`

### Format Values

| Format | Meaning |
|--------|---------|
| `"Cypilot"` | Full Cypilot tooling support: validation, parsing, ID extraction |
| Other | Custom format: LLM-only semantic processing, no CLI validation |

**Agent behavior**:
- `format: "Cypilot"` → Use `cypilot validate`, `list-ids`, `where-defined`, etc.
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
      "slug": "system-name",
      "kit": "kit-id",
      "artifacts_dir": "architecture",
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
| `name` | string | YES | Human-readable system/subsystem/component name |
| `slug` | string | YES | Machine-readable identifier (lowercase, no spaces, hyphen-separated). Used for hierarchical ID generation. Pattern: `^[a-z0-9]+(-[a-z0-9]+)*$` |
| `kit` | string | YES | Reference to kit ID from `kits` section |
| `artifacts_dir` | string | NO | Default base directory for NEW artifacts (default: `architecture`). Subdirectories defined by kit. |
| `artifacts` | array | NO | Artifacts belonging to this node. Paths are FULL paths relative to `project_root`. |
| `codebase` | array | NO | Source code directories for this node |
| `autodetect` | array | NO | Autodetect configs for this system node. Proposed for `version >= 1.1`. |
| `children` | array | NO | Nested child systems (subsystems, components) |

### Slug Convention

Slugs are machine-readable identifiers used for:
- Hierarchical ID generation: `{parent-slug}-{child-slug}-{TYPE}-{N}`
- System lookup and validation
- Cross-reference tracing

**Rules:**
- Lowercase letters, numbers, and hyphens only
- No spaces, no leading/trailing hyphens
- Must be unique within sibling systems

**Examples:**
- `"name": "Core Banking"` → `"slug": "core"`
- `"name": "Auth Service"` → `"slug": "auth"`
- `"name": "E-Commerce Platform"` → `"slug": "ecommerce"`

### Hierarchy Usage

```
System (root)
├── artifacts_dir: "architecture"     (default for NEW artifacts)
├── artifacts: [...]                  (FULL paths, can be anywhere)
│   ├── "architecture/PRD.md"
│   ├── "architecture/specs/auth.md"   (subdir defined by kit)
│   └── "docs/custom/DESIGN.md"           (user can place anywhere!)
├── codebase (source directories)
└── children
    └── Subsystem
        └── ...
```

**Agent behavior**:
- Iterate systems recursively to find all artifacts
- Resolve artifact paths: `{project_root}/{artifact.path}` (paths are FULL)
- For NEW artifacts: use `artifacts_dir` as base, subdirectories defined by kit
- Respect system boundaries for traceability

---

## Artifacts

**Purpose**: Declare documentation artifacts (PRD, DESIGN, ADR, DECOMPOSITION, SPEC).

**Structure** (paths are FULL paths relative to `project_root`):
```json
{
  "artifacts": [
    {
      "name": "Product Requirements",
      "path": "architecture/PRD.md",
      "kind": "PRD",
      "traceability": "FULL"
    },
    {
      "path": "architecture/specs/auth.md",
      "kind": "SPEC",
      "traceability": "FULL"
    },
    {
      "path": "docs/custom-location/DESIGN.md",
      "kind": "DESIGN",
      "traceability": "FULL"
    }
  ]
}
```

**Note**: Users can place artifacts anywhere — `artifacts_dir` only affects where NEW artifacts are created by default.

### Artifact Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | NO | - | Human-readable name (for display) |
| `path` | string | YES | - | FULL path to artifact file (relative to `project_root`) |
| `kind` | string | YES | - | Artifact kind (PRD, DESIGN, ADR, DECOMPOSITION, SPEC) |
| `traceability` | string | NO | `"FULL"` | Traceability level |

### Path Resolution

Artifact paths are resolved as: `{project_root}/{artifact.path}`

**Example**:
```
project_root: ".."
artifact path: "architecture/PRD.md"
→ Resolved: ../architecture/PRD.md

artifact path: "docs/custom/DESIGN.md"
→ Resolved: ../docs/custom/DESIGN.md
```

**Default directory for NEW artifacts**:
- `artifacts_dir` — base directory (default: `architecture`)
- Subdirectories for specific artifact kinds (`specs/`, `ADR/`) are defined by the kit

### Path Requirements

**CRITICAL**: `path` MUST be a file path, NOT a directory.

**Valid**:

```text
PRD.md
ADR/0001-initial-architecture.md
specs/auth.md
```

**Invalid**:

```text
ADR/        # directory
specs    # no extension = likely directory
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
| `PRD` | `{kit.path}/artifacts/PRD/template.md` | Product Requirements Document |
| `DESIGN` | `{kit.path}/artifacts/DESIGN/template.md` | Overall Design (system-level) |
| `ADR` | `{kit.path}/artifacts/ADR/template.md` | Architecture Decision Record |
| `DECOMPOSITION` | `{kit.path}/artifacts/DECOMPOSITION/template.md` | Spec breakdown and dependencies |
| `SPEC` | `{kit.path}/artifacts/SPEC/template.md` | Spec Design (spec-level) |

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

---

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

## Autodetect (Proposed)

This section defines a proposed extension for `artifacts.json` that allows **pattern-based auto-discovery** of:

- Artifacts (docs)
- Codebase entries
- Child systems (optional)

The goal is to reduce manual registry maintenance in repos where documentation and code follow a predictable structure.

### Principles

- `autodetect` MUST be optional.
- When `autodetect` is present, explicit `artifacts`/`codebase` entries are still allowed and remain authoritative.
- Autodetected results MUST be deterministic and reproducible.

### Location

`autodetect` MAY exist only inside `systems[]` nodes (and their `children[]` nodes).

Discovery/merge order:

1. Scan directories and build a detected set (artifacts/codebase/children).
2. Apply static config (`artifacts`, `codebase`, `children`) from `artifacts.json` and override detected entries by `path`.

Multiple autodetect rules:

- `system_node.autodetect` is a list of autodetect rules applied in-order.
- A node's effective autodetect rules are the concatenation of inherited parent rules and the node's own rules.

### Placeholders

Autodetect patterns support placeholder expansion.

- `{system}`: current system node `slug`

Path template placeholders:

- `{project_root}`: resolved registry `project_root` value
- `{system_root}`: resolved `autodetect.system_root`
- `{parent_root}`: resolved parent scope `system_root`

Notes:

- Placeholders are expanded BEFORE glob evaluation.
- Globs are evaluated relative to `project_root`.

### Autodetect Object

```json
{
  "kit": "cypilot-sdlc",
  "system_root": "{project_root}/subsystems/{system}",
  "artifacts_root": "{system_root}/docs",
  "aliases": {
    "core": {"slug": "platform", "name": "Platform", "description": "Core platform module"}
  },
  "artifacts": {
    "PRD": {"pattern": "PRD.md", "traceability": "FULL", "required": true},
    "DESIGN": {"pattern": "DESIGN.md", "traceability": "FULL"},
    "ADR": {"pattern": "ADR/*.md", "traceability": "DOCS-ONLY", "required": false},
    "FEATURE": {"pattern": "features/*.md", "traceability": "DOCS-ONLY", "required": false},
    "DECOMPOSITION": {"pattern": "DECOMPOSITION.md", "traceability": "FULL"}
  },
  "codebase": [
    {"path": "tests/{system}", "extensions": [".rs", ".py"]},
    {"path": "{system_root}/src", "extensions": [".rs", ".py"]}
  ],
  "validation": {
    "require_kind_registered_in_kit": true,
    "require_md_extension": true,
    "fail_on_unmatched_markdown": true
  },
  "children": [
    {
      "kit": "cypilot-sdlc",
      "system_root": "{parent_root}/modules/{system}",
      "artifacts_root": "{system_root}/specs",
      "aliases": {
        "core": {"slug": "platform", "name": "Platform", "description": "Core platform module"}
      },
      "artifacts": {
        "PRD": {"pattern": "PRD.md", "traceability": "FULL"},
        "DESIGN": {"pattern": "DESIGN.md", "traceability": "FULL"}
      },
      "codebase": [
        {"path": "{system_root}/src", "extensions": [".rs", ".py"]}
      ]
    }
  ]
}
```

Field semantics:

- `kit` (string): kit ID to use for autodetected artifacts. If omitted, defaults to `system_node.kit`.
- `system_root` (string): base directory for system-scoped resolution. It MAY use placeholders (e.g. `{project_root}`, `{parent_root}`, `{system}`).
- `artifacts_root` (string): base directory where artifact include patterns are resolved. If omitted, include patterns are treated as project-root-relative.
- `aliases` (object): mapping from discovered directory token (`{system}` value) to system metadata overrides.
- `artifacts` (object): map `KIND -> { pattern: string, traceability, required }`.
- `codebase` (array): list of codebase entries (same shape as system `codebase` entries).
- `validation` (object): strictness rules.
- `children` (array): nested autodetect rules applied recursively. Each item has the exact same structure as an autodetect rule.

Recursive rule:

- `autodetect` is applied at the current system node scope.
- If any autodetect rule has `children`, the concatenated `children` rules become the inherited autodetect rules for the next nesting level.

### Artifact Mapping Rules

- Each `pattern` MUST be a single string (file path or glob) that resolves to zero or more files.
- Each matched file becomes an artifact entry with:
  - `path`: resolved relative to `project_root`
  - `kind`: the map key (e.g., `"PRD"`)
  - `traceability`: from the mapping entry (default: `FULL`)

`required` behavior:

- Each artifact mapping MAY include `required: true|false`.
- Default: `required: true`.
- If `required: true` and `pattern` resolves to zero files (after global ignore), validation MUST fail.

### Validation Rules

The `validation` object defines how strict autodetect is.

- `require_kind_registered_in_kit` (bool): if true, any autodetected `kind` MUST be registered by the system's selected kit.
- `require_md_extension` (bool): if true, autodetected artifact paths MUST end with `.md`.
- `fail_on_unmatched_markdown` (bool): if true, then any `.md` file under `artifacts_root` (after global ignore) that does not match ANY `pattern` MUST fail.

`artifacts_root` placeholder rule:

- If `artifacts_root` is present:
  - It MAY contain `{system}` and/or `{system_root}`.
  - If neither `artifacts_root` nor `system_root` contains `{system}`, the rule still applies to the current system node (where `{system}` is the node's `slug`) and the resulting paths are treated as system-scoped.

`system_root` placeholder rule:

- If `system_root` is present, it MAY omit `{system}`.
- If `{system}` is omitted in `system_root`, it is interpreted as the root directory for the current system node only (the `{system}` value is still taken from `system_node.slug` for any other templated fields like `tests/{system}`).

Kind registration rule:

- A `kind` is considered registered in the kit if its template is resolvable at:
  - `{kit.path}/artifacts/{KIND}/template.md`

If the kit format does not use templates, it MUST still define an authoritative set of known kinds and the registry validator MUST validate autodetected kinds against it.

### Ignore Rules

- Ignore patterns are defined at the registry root in `ignore`.
- Ignore patterns are a global visibility filter applied to ALL artifact/code scanning/traversal.
- Ignore evaluation occurs before validation.

### Merge & Precedence

When both explicit and autodetected entries exist:

- Explicit `artifacts`/`codebase` entries always win.
- Autodetected entries are appended.
- If two entries resolve to the same `path`:
  - If `kind` differs, validation MUST fail.
  - If `kind` matches, the explicit entry wins and the autodetected duplicate is ignored.

---

## Path Resolution

### Artifact Paths (Existing)

Artifact paths in `artifacts` array are FULL paths, resolved directly: `{project_root}/{artifact.path}`

**Example**:
```
project_root: ".."
artifact path: "architecture/PRD.md"
→ Resolved: ../architecture/PRD.md

artifact path: "docs/custom/DESIGN.md"
→ Resolved: ../docs/custom/DESIGN.md
```

### Default Paths (New Artifacts)

When creating NEW artifacts:
- Base directory: `artifacts_dir` (default: `architecture`)
- Subdirectories for specific artifact kinds are defined by the kit

**Example** (cypilot-sdlc kit):
```
artifacts_dir: "architecture"
spec slug: "auth"

→ New SPEC created at: architecture/specs/auth.md (subdir defined by kit)
→ Registered in artifacts array with FULL path: "architecture/specs/auth.md"
```

### Codebase Paths

Codebase paths are resolved directly: `{project_root}/{codebase.path}`

---

## CLI Commands

**Note**: All commands use `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py` where `{cypilot_path}` is the Cypilot installation path. Examples below use `cypilot.py` as shorthand.

### Discovery

```bash
# Find adapter and registry
cypilot.py adapter-info --root /project
```

### Artifact Operations

```bash
# List all IDs from registered Cypilot artifacts
cypilot.py list-ids

# List IDs from specific artifact
cypilot.py list-ids --artifact architecture/PRD.md

# Find where ID is defined
cypilot.py where-defined --id "myapp-actor-user"

# Find where ID is referenced
cypilot.py where-used --id "myapp-actor-user"

# Validate artifact against template
cypilot.py validate --artifact architecture/PRD.md

# Validate all registered artifacts
cypilot.py validate

# Validate kits and templates
cypilot.py validate-kits
```

---

## Agent Operations

### Finding the Registry

1. Run `adapter-info` to discover adapter location
2. Registry is at `{cypilot_adapter_path}/artifacts.json`
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
# For artifact with kind="PRD" in system with kit="cypilot-sdlc"
kit = registry.kits["cypilot-sdlc"]
template_path = f"{kit.path}/artifacts/{artifact.kind}/template.md"
# → "kits/sdlc/artifacts/PRD/template.md"
```

### Checking Format

```python
kit = registry.kits[system.kit]
if kit.format == "Cypilot":
    # Use CLI validation
    run("cypilot validate --artifact {path}")
else:
    # Custom format - LLM-only processing
    process_semantically(artifact)
```

---

## Error Handling

### artifacts.json Not Found

**If artifacts.json doesn't exist at adapter location**:
```
⚠️ Registry not found: {cypilot_adapter_path}/artifacts.json
→ Adapter exists but registry not initialized
→ Fix: Run /cypilot-adapter to create registry
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

### Missing Kit Reference

**If system references non-existent kit**:
```
⚠️ Invalid kit reference: system "MyApp" references kit "custom-kit" not in kits section
→ Fix: Add kit to kits section OR change system.kit to an existing kit ID
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
⚠️ Template not found: kits/sdlc/artifacts/PRD/template.md
→ Kind "PRD" registered but template missing
→ Fix: Create template OR use different kit package
```
**Action**:

- Use a synthetic template and continue validation using artifact scanning.
- If `constraints.json` defines constraints for this kind, attach them to the synthetic template.
- WARN and continue validation.

---

## Example Registry

```json
{
  "version": "1.1",
  "project_root": "..",
  "kits": {
    "cypilot-sdlc": {
      "format": "Cypilot",
      "path": "kits/sdlc"
    }
  },
  "ignore": [
    {"reason": "Text", "patterns": ["modules/my_module/*"]}
  ],
  "systems": [
    {
      "name": "MyApp",
      "slug": "myapp",
      "kit": "cypilot-sdlc",
      "artifacts_dir": "architecture",
      "autodetect": [
        {
          "kit": "cypilot-sdlc",
          "system_root": "{project_root}/subsystems/{system}",
          "artifacts_root": "{system_root}/docs",
          "aliases": {
            "core": {"slug": "platform", "name": "Platform", "description": "Core platform module"}
          },
          "artifacts": {
            "PRD": {"pattern": "PRD.md", "traceability": "FULL"},
            "DESIGN": {"pattern": "DESIGN.md", "traceability": "FULL"},
            "ADR": {"pattern": "ADR/*.md", "traceability": "DOCS-ONLY", "required": false},
            "FEATURE": {"pattern": "features/*.md", "traceability": "DOCS-ONLY", "required": false},
            "DECOMPOSITION": {"pattern": "DECOMPOSITION.md", "traceability": "FULL"}
          },
          "codebase": [
            {"path": "tests/{system}", "extensions": [".rs", ".py"]},
            {"path": "{system_root}/src", "extensions": [".rs", ".py"]}
          ],
          "validation": {
            "require_kind_registered_in_kit": true,
            "require_md_extension": true,
            "fail_on_unmatched_markdown": true
          },
          "children": [
            {
              "kit": "cypilot-sdlc",
              "system_root": "{parent_root}/modules/{system}",
              "artifacts_root": "{system_root}/specs",
              "artifacts": {
                "PRD": {"pattern": "PRD.md", "traceability": "FULL"},
                "DESIGN": {"pattern": "DESIGN.md", "traceability": "FULL"}
              },
              "codebase": [
                {"path": "{system_root}/src", "extensions": [".rs", ".py"]}
              ]
            }
          ]
        }
      ],
      "artifacts": [
        { "name": "Product Requirements", "path": "architecture/PRD.md", "kind": "PRD", "traceability": "DOCS-ONLY" },
        { "name": "Overall Design", "path": "architecture/DESIGN.md", "kind": "DESIGN", "traceability": "FULL" },
        { "name": "Initial Architecture", "path": "architecture/ADR/0001-initial-architecture.md", "kind": "ADR", "traceability": "DOCS-ONLY" },
        { "name": "Design Decomposition", "path": "architecture/DECOMPOSITION.md", "kind": "DECOMPOSITION", "traceability": "DOCS-ONLY" },
        { "name": "Custom Location Example", "path": "docs/specs/custom-spec.md", "kind": "SPEC", "traceability": "FULL" }
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
          "slug": "auth",
          "kit": "cypilot-sdlc",
          "artifacts_dir": "modules/auth/architecture",
          "artifacts": [
            { "path": "modules/auth/architecture/PRD.md", "kind": "PRD", "traceability": "DOCS-ONLY" },
            { "path": "modules/auth/architecture/specs/sso.md", "kind": "SPEC", "traceability": "FULL" }
          ],
          "codebase": [
            { "name": "Auth Module", "path": "src/modules/auth", "extensions": [".ts"] }
          ],
          "children": []
        }
      ]
    }
  ]
}
```

**Note**: Artifact paths are FULL paths relative to `project_root`. The `artifacts_dir` defines the default base directory for NEW artifacts — subdirectories for specific kinds (`specs/`, `ADR/`) are defined by the kit.

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| "Artifact not in Cypilot registry" | Path not registered | Add artifact to system's `artifacts` array |
| "Could not find template" | Missing template file | Create template at `{kit.path}/artifacts/{KIND}/template.md` |
| "Invalid kit reference" | System references non-existent kit | Add kit to `kits` section or fix `kit` field |
| "Path is a directory" | Artifact path ends with `/` or has no extension | Change to specific file path |

---

## References

**Schema**: `../schemas/artifacts.schema.json`

**CLI**: `skills/cypilot/cypilot.clispec`

**Related**:
- `adapter-structure.md` - Adapter AGENTS.md requirements
- `execution-protocol.md` - Workflow execution protocol

---

## Consolidated Validation Checklist

**Use this single checklist for all artifacts.json validation.**

### Registry Structure (R)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| R.1 | artifacts.json exists at adapter location | YES | File exists at `{cypilot_adapter_path}/artifacts.json` |
| R.2 | JSON parses without errors | YES | `json.loads()` succeeds |
| R.3 | `version` field present and non-empty | YES | Field exists and is string |
| R.4 | `kits` object present with ≥1 kit | YES | Object with at least one key |
| R.5 | `systems` array present | YES | Array (may be empty) |
| R.6 | Each kit has `format` and `path` fields | YES | Both fields exist per kit |
| R.7 | Each system has `name`, `slug`, and `kit` fields | YES | All three fields exist per system |
| R.8 | System `kit` references exist in `kits` section | YES | Lookup succeeds |
| R.9 | `artifacts_dir` is valid path (if specified) | CONDITIONAL | Non-empty string |
| R.10 | `slug` matches pattern `^[a-z0-9]+(-[a-z0-9]+)*$` | YES | Lowercase, no spaces, hyphen-separated |
| R.11 | `slug` is unique among siblings | YES | No duplicate slugs at same level |
| R.12 | `autodetect` (if present) is only used when `version >= 1.1` | CONDITIONAL | `version` is "1.1"+ when any system node has non-null `autodetect` |
| R.13 | `autodetect` (if present) has valid basic shape | CONDITIONAL | `kit` is string (optional); `artifacts_root` string; `artifacts` map; `ignore` list; `validation` object |

### Artifact Entries (A)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| A.1 | Each artifact has `path` and `kind` fields | YES | Both fields exist |
| A.2 | Artifact paths are files, not directories | YES | Path has extension, doesn't end with `/` |
| A.3 | Artifact kinds are valid | YES | One of: PRD, DESIGN, ADR, DECOMPOSITION, SPEC |
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
| F.1 | All Registry Structure checks pass | YES | R.1-R.11 verified |
| F.2 | All Artifact Entries checks pass | YES | A.1-A.4 verified |
| F.3 | All Codebase Entries checks pass | YES | C.1-C.4 verified |
