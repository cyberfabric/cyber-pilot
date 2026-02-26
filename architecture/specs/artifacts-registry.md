---
cypilot: true
type: requirement
name: Artifacts Registry
version: 2.0
purpose: Define structure and usage of artifacts.toml for agent operations
---

# Cypilot Artifacts Registry Specification

---

## Table of Contents

- [Agent Instructions](#agent-instructions)
- [Overview](#overview)
- [Schema Version](#schema-version)
- [Root Structure](#root-structure)
- [Systems](#systems)
- [Artifacts](#artifacts)
- [Codebase](#codebase)
- [Autodetect](#autodetect)
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
ALWAYS open and follow `{cypilot_path}/.core/requirements/artifacts-registry.md` WHEN working with artifacts.toml
```
Where `{cypilot_path}` is resolved from the adapter's `**Extends**:` declaration.

**ALWAYS use**: `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py adapter-info` to discover adapter location

**ALWAYS use**: `cypilot.py` CLI commands for artifact operations (list-ids, where-defined, where-used, validate)

**Prerequisite**: Agent confirms understanding before proceeding:
- [ ] Agent has read and understood this requirement
- [ ] Agent knows where artifacts.toml is located (via adapter-info)
- [ ] Agent will use CLI commands, not direct file manipulation

---

## Overview

**What**: `artifacts.toml` is the Cypilot artifact registry — a TOML file that declares all systems, their artifacts, and codebase locations.

**Location**: `.cypilot/config/artifacts.toml`

**Purpose**:
- Declares system hierarchy (systems → subsystems → components)
- Registers artifact files and their kinds for validation and parsing
- Specifies codebase directories for traceability
- Defines global ignore rules for scanning
- Enables CLI tools to discover and process artifacts automatically

**Not in this file**: kit definitions (format, path, template locations) live in `config/core.toml`. Systems reference kits by ID; the tool resolves kit details from `core.toml`.

---

## Schema Version

Current version: `2.0`

Schema file: `../schemas/artifacts-registry.schema.json`

Notes:

- Version `2.0` uses TOML format. Legacy `1.x` JSON registries are supported via `cypilot migrate-config`.

---

## Root Structure

`version` and `project_root` are defined in `config/core.toml` (authoritative source). They may appear in `artifacts.toml` for standalone or legacy use; the tool merges them at load time.

```toml
# artifacts.toml — systems and ignore only (version/project_root in core.toml)

[[ignore]]
reason = "Third-party code"
patterns = ["vendor/*", "node_modules/*"]

# Systems defined below as [[systems]] array
```

### Field Reference

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `version` | string | NO | Schema version. Normally in `core.toml`; may appear here for legacy/standalone use. |
| `project_root` | string | NO | Relative path to project root. Normally in `core.toml`; may appear here for legacy/standalone use. Default: `".."` |
| `ignore` | array of tables | NO | Global ignore rules (visibility filter) |
| `systems` | array of tables | YES | Root-level system nodes |

### Root Ignore (Visibility Filter)

If `[[ignore]]` entries are present, they define paths that are **globally invisible** to:

- Autodetect directory scanning
- Codebase traceability scanning
- CLI commands that traverse artifacts/codebase (`validate`, `list-ids`, `where-defined`, `where-used`)

Each `[[ignore]]` entry has:

| Key | Type | Description |
|-----|------|-------------|
| `reason` | string | Why these paths are ignored |
| `patterns` | array of strings | Glob patterns resolved relative to `project_root` |

This is a hard filter: the tool behaves as if ignored paths do not exist.

---

## Systems

**Purpose**: Define hierarchical structure of the project.

**Structure**:
```toml
[[systems]]
name = "SystemName"
slug = "system-name"
kit = "kit-id"
artifacts_dir = "architecture"

# artifacts, codebase, children defined as nested arrays of tables
```

### System Node Fields

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `name` | string | YES | Human-readable system/subsystem/component name |
| `slug` | string | YES | Machine-readable identifier (lowercase, no spaces, hyphen-separated). Used for hierarchical ID generation. Pattern: `^[a-z0-9]+(-[a-z0-9]+)*$` |
| `kit` | string | YES | Reference to kit ID registered in `config/core.toml` |
| `artifacts_dir` | string | NO | Default base directory for NEW artifacts (default: `architecture`). Subdirectories defined by kit. |
| `artifacts` | array of tables | NO | Artifacts belonging to this node. Paths are FULL paths relative to `project_root`. |
| `codebase` | array of tables | NO | Source code directories for this node |
| `autodetect` | array of tables | NO | Autodetect configs for this system node. |
| `children` | array of tables | NO | Nested child systems (subsystems, components) |

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
│   ├── "architecture/features/auth.md"   (subdir defined by kit)
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

**Purpose**: Declare documentation artifacts (PRD, DESIGN, ADR, DECOMPOSITION, FEATURE).

**Structure** (paths are FULL paths relative to `project_root`):
```toml
[[systems.artifacts]]
name = "Product Requirements"
path = "architecture/PRD.md"
kind = "PRD"
traceability = "FULL"

[[systems.artifacts]]
path = "architecture/features/auth.md"
kind = "FEATURE"

[[systems.artifacts]]
path = "docs/custom-location/DESIGN.md"
kind = "DESIGN"
```

**Note**: Users can place artifacts anywhere — `artifacts_dir` only affects where NEW artifacts are created by default.

### Artifact Fields

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `name` | string | NO | - | Human-readable name (for display) |
| `path` | string | YES | - | FULL path to artifact file (relative to `project_root`) |
| `kind` | string | YES | - | Artifact kind (PRD, DESIGN, ADR, DECOMPOSITION, FEATURE) |
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
- Subdirectories for specific artifact kinds (`features/`, `ADR/`) are defined by the kit

### Path Requirements

**CRITICAL**: `path` MUST be a file path, NOT a directory.

**Valid**:

```text
PRD.md
ADR/0001-initial-architecture.md
features/auth.md
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
| `DECOMPOSITION` | `{kit.path}/artifacts/DECOMPOSITION/template.md` | Feature breakdown and dependencies |
| `FEATURE` | `{kit.path}/artifacts/FEATURE/template.md` | Feature Design (feature-level) |

---

## Codebase

**Purpose**: Declare source code directories for traceability scanning.

**Structure**:
```toml
[[systems.codebase]]
name = "Source Code"
path = "src"
extensions = [".ts", ".tsx"]
single_line_comments = ["//"]

[[systems.codebase.multi_line_comments]]
start = "/*"
end = "*/"
```

### Codebase Entry Fields

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `name` | string | NO | Human-readable name (for display) |
| `path` | string | YES | Path to source directory (relative to project_root) |
| `extensions` | array of strings | YES | File extensions to include (e.g., `[".py", ".ts"]`) |
| `single_line_comments` | array of strings | NO | Single-line comment prefixes (e.g., `["#", "//"]`). Defaults based on file extension. |
| `multi_line_comments` | array of tables | NO | Multi-line comment delimiters. Each entry has `start` and `end` keys. Defaults based on file extension. |

---

### Extension Format

Extensions MUST start with a dot and contain only alphanumeric characters.

**Valid**: `.py`, `.ts`, `.tsx`, `.rs`

**Invalid**: `py`, `*.py`, `.foo-bar`

### Comment Syntax Configuration

Comment syntax can be explicitly configured per codebase entry, or left to default based on file extension.

**Multi-line comment structure**:
```toml
[[systems.codebase.multi_line_comments]]
start = "/*"
end = "*/"
```

**Common configurations**:

| Language | Single-line | Multi-line |
|----------|-------------|------------|
| Python | `["#"]` | `start = '"""'`, `end = '"""'` |
| JavaScript/TypeScript | `["//"]` | `start = "/*"`, `end = "*/"` |
| Rust | `["//"]` | `start = "/*"`, `end = "*/"` |
| HTML | — | `start = "<!--"`, `end = "-->"` |
| CSS | — | `start = "/*"`, `end = "*/"` |

**When to configure explicitly**:
- Non-standard file extensions
- Mixed-language files
- Custom comment syntax
- Overriding defaults for specific directories

---

## Autodetect

Autodetect allows **pattern-based auto-discovery** of:

- Artifacts (docs)
- Codebase entries
- Child systems (optional)

The goal is to reduce manual registry maintenance in repos where documentation and code follow a predictable structure.

### Principles

- `autodetect` MUST be optional.
- When `autodetect` is present, explicit `artifacts`/`codebase` entries are still allowed and remain authoritative.
- Autodetected results MUST be deterministic and reproducible.

### Location

`autodetect` MAY exist only inside `[[systems]]` nodes (and their `[[systems.children]]` nodes).

Discovery/merge order:

1. Scan directories and build a detected set (artifacts/codebase/children).
2. Apply static config (`artifacts`, `codebase`, `children`) from `artifacts.toml` and override detected entries by `path`.

Multiple autodetect rules:

- `systems.autodetect` is an array of tables applied in-order.
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

```toml
[[systems.autodetect]]
kit = "cypilot-sdlc"
system_root = "{project_root}/subsystems/{system}"
artifacts_root = "{system_root}/docs"

[systems.autodetect.aliases.core]
slug = "platform"
name = "Platform"
description = "Core platform module"

[systems.autodetect.artifacts.PRD]
pattern = "PRD.md"
traceability = "FULL"
required = true

[systems.autodetect.artifacts.DESIGN]
pattern = "DESIGN.md"
traceability = "FULL"

[systems.autodetect.artifacts.ADR]
pattern = "ADR/*.md"
traceability = "DOCS-ONLY"
required = false

[systems.autodetect.artifacts.FEATURE]
pattern = "features/*.md"
traceability = "DOCS-ONLY"
required = false

[systems.autodetect.artifacts.DECOMPOSITION]
pattern = "DECOMPOSITION.md"
traceability = "FULL"

[[systems.autodetect.codebase]]
path = "tests/{system}"
extensions = [".rs", ".py"]

[[systems.autodetect.codebase]]
path = "{system_root}/src"
extensions = [".rs", ".py"]

[systems.autodetect.validation]
require_kind_registered_in_kit = true
require_md_extension = true
fail_on_unmatched_markdown = true

[[systems.autodetect.children]]
kit = "cypilot-sdlc"
system_root = "{parent_root}/modules/{system}"
artifacts_root = "{system_root}/specs"

[systems.autodetect.children.artifacts.PRD]
pattern = "PRD.md"
traceability = "FULL"

[systems.autodetect.children.artifacts.DESIGN]
pattern = "DESIGN.md"
traceability = "FULL"

[[systems.autodetect.children.codebase]]
path = "{system_root}/src"
extensions = [".rs", ".py"]
```

Field semantics:

- `kit` (string): kit ID to use for autodetected artifacts. If omitted, defaults to `system_node.kit`.
- `system_root` (string): base directory for system-scoped resolution. It MAY use placeholders (e.g. `{project_root}`, `{parent_root}`, `{system}`).
- `artifacts_root` (string): base directory where artifact include patterns are resolved. If omitted, include patterns are treated as project-root-relative.
- `aliases` (table of tables): mapping from discovered directory token (`{system}` value) to system metadata overrides.
- `artifacts` (table of tables): map `KIND -> { pattern, traceability, required }`.
- `codebase` (array of tables): list of codebase entries (same shape as system `codebase` entries).
- `validation` (table): strictness rules.
- `children` (array of tables): nested autodetect rules applied recursively. Each item has the exact same structure as an autodetect rule.

Recursive rule:

- `autodetect` is applied at the current system node scope.
- If any autodetect rule has `children`, the concatenated `children` rules become the inherited autodetect rules for the next nesting level.

### System Slug Detection from IDs (Autodetect)

When a child system is discovered via autodetect (directory matching `$system` in `system_root`), the initial slug is derived from the **folder name**. However, the folder name may differ from the slug actually used in Cypilot identifiers (e.g. folder `super-chat/` but IDs use `cpt-cf-chat-fr-...`).

To resolve the authoritative slug, the validator applies the following algorithm after discovering all artifacts for the child system.

#### Inputs

- **Definition IDs**: all `cpt-*` definition IDs scanned from the child system's artifacts.
- **Parent prefix**: the hierarchy prefix of the parent system node (e.g. `cf`). Empty string if parent has no slug.
- **Kind tokens**: the set of all ID kind tokens registered in the kit's constraints (e.g. `{fr, state, dod, flow, algo, ...}`).

#### ID structure

Every definition ID follows the template:

```
cpt-{parent_prefix}-{system_slug}-{kind}-{rest}
```

If parent prefix is empty:

```
cpt-{system_slug}-{kind}-{rest}
```

#### Algorithm

For each definition ID:

1. Strip the `cpt-` prefix.
2. Strip the parent hierarchy prefix (if non-empty) + trailing hyphen.
3. The remainder has the form `{system_slug}-{kind}-{rest}`.
4. For **every** known kind token, search for **all** occurrences of `-{kind}-` in the remainder.
5. Each match at position `idx > 0` yields a slug candidate: `remainder[:idx]`.
6. Collect all unique candidates for this ID.

Classify each ID:

- **Unambiguous**: exactly 1 candidate → the slug is determined.
- **Ambiguous**: multiple candidates (a kind token collides with part of the system slug) → skip this ID.

#### Decision

| Unambiguous slugs | Result |
|---|---|
| Exactly 1 unique slug | Use it as the system slug (override folder-based slug) |
| Multiple different slugs | **Error**: `Inconsistent system slugs in IDs` |
| None (all IDs ambiguous) | **Error**: `Cannot determine system slug from IDs` |

If no definition IDs exist in the system's artifacts, the folder-based slug is kept unchanged.

#### Why ambiguous IDs are skipped

A kind token may appear as a hyphen-delimited segment inside the system slug itself. For example, system `my-db-service` with kind token `db`:

```
cpt-my-db-service-fr-auth
         ^              ^
         |-db-|         |-fr-|
         ambiguous      unambiguous
```

The ID `cpt-my-db-service-fr-auth` produces two candidates: `my` (from `-db-`) and `my-db-service` (from `-fr-`). Since there are multiple candidates, this ID is ambiguous and skipped.

Other IDs in the same system that use a kind token NOT present in the slug (e.g. `-fr-`, `-state-`, `-dod-`) will be unambiguous and correctly yield `my-db-service`.

#### Scope

This algorithm applies **only to autodetected child systems**. Systems with an explicitly configured `slug` in `artifacts.toml` (non-autodetect) use the configured value as-is.

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

→ New FEATURE created at: architecture/features/auth.md (subdir defined by kit)
→ Registered in artifacts array with FULL path: "architecture/features/auth.md"
```

### Codebase Paths

Codebase paths are resolved directly: `{project_root}/{codebase.path}`

---

## CLI Commands

**Note**: All commands use `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py` where `{cypilot_path}` is the Cypilot installation path. Examples below use `cypilot.py` as shorthand.

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

1. Run `adapter-info` to discover project location
2. Registry is at `.cypilot/config/artifacts.toml`
3. Parse TOML to get registry data

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
# Kit details resolved from config/core.toml
kit = core_config.kits["cypilot-sdlc"]
template_path = f"config/kits/{kit.slug}/artifacts/{artifact.kind}/template.md"
# → "config/kits/sdlc/artifacts/PRD/template.md"
```

### Checking Format

```python
# Kit format resolved from config/core.toml
kit = core_config.kits[system.kit]
if kit.format == "Cypilot":
    # Use CLI validation
    run("cypilot validate --artifact {path}")
else:
    # Custom format - LLM-only processing
    process_semantically(artifact)
```

---

## Error Handling

### artifacts.toml Not Found

**If artifacts.toml doesn't exist**:
```
⚠️ Registry not found: .cypilot/config/artifacts.toml
→ Registry not initialized
→ Fix: Run `cypilot init` to create registry
```
**Action**: STOP — cannot process artifacts without registry.

### TOML Parse Error

**If artifacts.toml contains invalid TOML**:
```
⚠️ Invalid TOML in artifacts.toml: {parse error}
→ Check for syntax errors
→ Fix: Validate TOML syntax in IDE
```
**Action**: STOP — cannot process malformed registry.

### Missing Kit Reference

**If system references kit not registered in core.toml**:
```
⚠️ Invalid kit reference: system "MyApp" references kit "custom-kit" not in core.toml
→ Fix: Register kit in config/core.toml OR change system.kit to an existing kit ID
```
**Action**: FAIL validation for that system, continue with others.

### Artifact File Not Found

**If registered artifact file doesn't exist**:
```
⚠️ Artifact not found: architecture/PRD.md
→ Registered in artifacts.toml but file missing
→ Fix: Create file OR remove from registry
```
**Action**: WARN and skip artifact, continue with others.

### Template Not Found

**If template for artifact kind doesn't exist**:
```
⚠️ Template not found: config/kits/sdlc/artifacts/PRD/template.md
→ Kind "PRD" registered but template missing
→ Fix: Create template OR use different kit package
```
**Action**:

- Use a synthetic template and continue validation using artifact scanning.
- If `constraints.toml` defines constraints for this kind, attach them to the synthetic template.
- WARN and continue validation.

---

## Example Registry

```toml
# version and project_root are in core.toml

[[ignore]]
reason = "Third-party module"
patterns = ["modules/my_module/*"]

# ── Root system ──────────────────────────────────────────────

[[systems]]
name = "MyApp"
slug = "myapp"
kit = "cypilot-sdlc"
artifacts_dir = "architecture"

# Autodetect rules for child system discovery
[[systems.autodetect]]
kit = "cypilot-sdlc"
system_root = "{project_root}/subsystems/{system}"
artifacts_root = "{system_root}/docs"

[systems.autodetect.aliases.core]
slug = "platform"
name = "Platform"
description = "Core platform module"

[systems.autodetect.artifacts.PRD]
pattern = "PRD.md"
traceability = "FULL"

[systems.autodetect.artifacts.DESIGN]
pattern = "DESIGN.md"
traceability = "FULL"

[systems.autodetect.artifacts.ADR]
pattern = "ADR/*.md"
traceability = "DOCS-ONLY"
required = false

[systems.autodetect.artifacts.FEATURE]
pattern = "features/*.md"
traceability = "DOCS-ONLY"
required = false

[systems.autodetect.artifacts.DECOMPOSITION]
pattern = "DECOMPOSITION.md"
traceability = "FULL"

[[systems.autodetect.codebase]]
path = "tests/{system}"
extensions = [".rs", ".py"]

[[systems.autodetect.codebase]]
path = "{system_root}/src"
extensions = [".rs", ".py"]

[systems.autodetect.validation]
require_kind_registered_in_kit = true
require_md_extension = true
fail_on_unmatched_markdown = true

[[systems.autodetect.children]]
kit = "cypilot-sdlc"
system_root = "{parent_root}/modules/{system}"
artifacts_root = "{system_root}/specs"

[systems.autodetect.children.artifacts.PRD]
pattern = "PRD.md"
traceability = "FULL"

[systems.autodetect.children.artifacts.DESIGN]
pattern = "DESIGN.md"
traceability = "FULL"

[[systems.autodetect.children.codebase]]
path = "{system_root}/src"
extensions = [".rs", ".py"]

# Explicit artifacts (FULL paths relative to project_root)
[[systems.artifacts]]
name = "Product Requirements"
path = "architecture/PRD.md"
kind = "PRD"
traceability = "DOCS-ONLY"

[[systems.artifacts]]
name = "Overall Design"
path = "architecture/DESIGN.md"
kind = "DESIGN"
traceability = "FULL"

[[systems.artifacts]]
name = "Initial Architecture"
path = "architecture/ADR/0001-initial-architecture.md"
kind = "ADR"
traceability = "DOCS-ONLY"

[[systems.artifacts]]
name = "Design Decomposition"
path = "architecture/DECOMPOSITION.md"
kind = "DECOMPOSITION"
traceability = "DOCS-ONLY"

[[systems.artifacts]]
name = "Custom Location Example"
path = "docs/features/custom-feature.md"
kind = "FEATURE"
traceability = "FULL"

# Codebase
[[systems.codebase]]
name = "Source Code"
path = "src"
extensions = [".ts", ".tsx"]
single_line_comments = ["//"]

[[systems.codebase.multi_line_comments]]
start = "/*"
end = "*/"

# ── Child system ─────────────────────────────────────────────

[[systems.children]]
name = "Auth"
slug = "auth"
kit = "cypilot-sdlc"
artifacts_dir = "modules/auth/architecture"

[[systems.children.artifacts]]
path = "modules/auth/architecture/PRD.md"
kind = "PRD"
traceability = "DOCS-ONLY"

[[systems.children.artifacts]]
path = "modules/auth/architecture/features/sso.md"
kind = "FEATURE"
traceability = "FULL"

[[systems.children.codebase]]
name = "Auth Module"
path = "src/modules/auth"
extensions = [".ts"]
```

**Note**: Artifact paths are FULL paths relative to `project_root`. The `artifacts_dir` defines the default base directory for NEW artifacts — subdirectories for specific kinds (`features/`, `ADR/`) are defined by the kit. Kit definitions (format, path, templates) are resolved from `config/core.toml`.

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| "Artifact not in Cypilot registry" | Path not registered | Add artifact to system's `artifacts` array |
| "Could not find template" | Missing template file | Create template at `{kit.path}/artifacts/{KIND}/template.md` |
| "Invalid kit reference" | System references kit not in `core.toml` | Register kit in `config/core.toml` or fix `kit` field |
| "Path is a directory" | Artifact path ends with `/` or has no extension | Change to specific file path |

---

## References

**Schema**: `../schemas/artifacts-registry.schema.json`

**CLI**: `skills/cypilot/cypilot.clispec`

**Related**:
- `sysprompts.md` - Project system prompts (.cypilot/config/sysprompts + config/AGENTS.md)
- `execution-protocol.md` - Workflow execution protocol

---

## Consolidated Validation Checklist

**Use this single checklist for all artifacts.toml validation.**

### Registry Structure (R)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| R.1 | `artifacts.toml` exists at `.cypilot/config/` | YES | File exists at `.cypilot/config/artifacts.toml` |
| R.2 | TOML parses without errors | YES | `tomllib.loads()` succeeds |
| R.3 | `version` field resolvable (from `core.toml` or `artifacts.toml`) | YES | Field exists in at least one source and is string |
| R.4 | `systems` array present | YES | Array (may be empty) |
| R.5 | Each system has `name`, `slug`, and `kit` fields | YES | All three fields exist per system |
| R.6 | System `kit` references exist in `config/core.toml` | YES | Lookup succeeds |
| R.7 | `artifacts_dir` is valid path (if specified) | CONDITIONAL | Non-empty string |
| R.8 | `slug` matches pattern `^[a-z0-9]+(-[a-z0-9]+)*$` | YES | Lowercase, no spaces, hyphen-separated |
| R.9 | `slug` is unique among siblings | YES | No duplicate slugs at same level |
| R.10 | `autodetect` (if present) has valid structure | CONDITIONAL | `kit` is string (optional); `artifacts_root` string; `artifacts` table; `validation` table |

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
| C.4 | Comment syntax format valid (if specified) | CONDITIONAL | Arrays of strings, multi-line has `start`/`end` |

### Final (F)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| F.1 | All Registry Structure checks pass | YES | R.1-R.9 verified |
| F.2 | All Artifact Entries checks pass | YES | A.1-A.4 verified |
| F.3 | All Codebase Entries checks pass | YES | C.1-C.4 verified |
