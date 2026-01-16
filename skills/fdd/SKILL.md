---
name: fdd
description: Unified FDD tool for validation and search. Validates FDD artifacts (BUSINESS.md, DESIGN.md, ADR.md, FEATURES.md, feature DESIGN.md, feature CHANGES.md) against FDD requirements. Provides read-only search and traceability for FDD artifacts and FDD/ADR IDs with repo-wide scanning capabilities. Supports optional project-level configuration via .fdd-config.json (e.g., fddCorePath).
---

# FDD Unified Tool

## Goal

Provides comprehensive FDD artifact management:
1. **Validation**: Deterministic validation reports for FDD artifacts using requirements/*-structure.md files
2. **Search**: Read-only search and traceability across FDD artifacts and IDs
3. **Traceability**: Codebase traceability scanning to verify implemented DESIGN/CHANGES items are tagged in code

## Preconditions

1. ALWAYS follow `../SKILLS.md` Toolchain Preflight
2. `python3` is available
3. Target paths exist and are readable

## Command Structure

The unified tool uses subcommands for different operations:

```bash
python3 scripts/fdd.py <subcommand> [options]
```

## Project Configuration

This tool optionally reads a project-level configuration file located at the project root:
- `.fdd-config.json`

If present, it can override where the FDD core (requirements/workflows/AGENTS.md) is located.

**Example**:
```json
{
  "fddCorePath": ".fdd",
  "adapterPath": ".fdd-adapter"
}
```

**Supported fields**:
- **`fddCorePath`**: Relative path from project root to the FDD core directory.
- **`adapterPath`**: Reserved for future use (adapter discovery). Not used by this tool yet.

**Discovery rules**:
- The tool searches upwards from the current working directory.
- The first directory that contains `.fdd-config.json` is treated as the project root.
- If `.fdd-config.json` is not present, the tool falls back to marker-based FDD core detection.

## Validation Commands

### Artifact Validation

```bash
# Validate any FDD artifact (auto-detects type)
python3 scripts/fdd.py validate --artifact {path}

# Validate with explicit requirements file
python3 scripts/fdd.py validate --artifact {path} --requirements {path}

# Validate with cross-references
python3 scripts/fdd.py validate --artifact {path} --design {path} --business {path} --adr {path}

# Skip filesystem checks
python3 scripts/fdd.py validate --artifact {path} --skip-fs-checks

# Save validation report
python3 scripts/fdd.py validate --artifact {path} --output {path}
```

### Codebase Traceability Scan

```bash
# Code-root mode (recommended)
python3 scripts/fdd.py validate --artifact {code-root}
# {code-root} MUST contain `architecture/features/feature-*/DESIGN.md`

# Optional filtering by feature slugs
python3 scripts/fdd.py validate --artifact {code-root} --features gts-core,init-module

# Feature-dir mode (backwards compatible)
python3 scripts/fdd.py validate --artifact {feature-dir}
# Expects `{feature-dir}/DESIGN.md`
```

### What Validation Checks

**Artifact Structure**:
- Required sections (derived from requirements/*-structure.md)
- Placeholder markers: `TODO`, `TBD`, `FIXME`, `XXX`, `TBA`
- Cross-references between artifacts
- ID format and uniqueness

**Codebase Traceability**:
- Validates DESIGN.md and CHANGES.md first
- For each implemented scope (`- [x] **ID**: ...`), expects `@fdd-{kind}:...:ph-{N}` tag in code
- For each implemented FDL step line (`[x] ... - `inst-...``), expects instruction-level marker
- For each completed change (`**Status**: ✅ COMPLETED`), expects `@fdd-change:...:ph-{N}` tag

## Search Commands

### List Sections/Headings

```bash
python3 scripts/fdd.py list-sections --artifact {path}
python3 scripts/fdd.py list-sections --artifact {path} --under-heading "{Exact Heading}"
```

### List IDs

```bash
python3 scripts/fdd.py list-ids --artifact {path}
python3 scripts/fdd.py list-ids --artifact {path} --pattern "{substring}"
python3 scripts/fdd.py list-ids --artifact {path} --pattern "{regex}" --regex
python3 scripts/fdd.py list-ids --artifact {path} --under-heading "{Exact Heading}"
python3 scripts/fdd.py list-ids --artifact {path} --all  # Include duplicates
```

### List Items

```bash
python3 scripts/fdd.py list-items --artifact {path}
python3 scripts/fdd.py list-items --artifact {path} --type {actor|capability|usecase|requirement|feature|flow|algo|state|test|change|adr}
python3 scripts/fdd.py list-items --artifact {path} --lod {id|summary}
python3 scripts/fdd.py list-items --artifact {path} --pattern "{substring}"
python3 scripts/fdd.py list-items --artifact {path} --under-heading "{Exact Heading}"
```

### Read Sections

```bash
python3 scripts/fdd.py read-section --artifact {path} --section {A|B|C}
python3 scripts/fdd.py read-section --artifact {path} --heading "{Exact Heading}"
python3 scripts/fdd.py read-section --artifact {path-to-FEATURES.md} --feature-id {fdd-...-feature-...}
python3 scripts/fdd.py read-section --artifact {path-to-CHANGES.md} --change {N}
python3 scripts/fdd.py read-section --artifact {path} --id {any-id-substring}
```

### Get Item

```bash
python3 scripts/fdd.py get-item --artifact {path} --id {any-id-substring}
python3 scripts/fdd.py get-item --artifact {path} --heading "{Exact Heading}"
python3 scripts/fdd.py get-item --artifact {path} --section {A|B|C}
```

### Find ID

```bash
python3 scripts/fdd.py find-id --artifact {path} --id {any-id-substring}
```

### Text Search

```bash
python3 scripts/fdd.py search --artifact {path} --query "{literal}"
python3 scripts/fdd.py search --artifact {path} --query "{regex}" --regex
```

## Adapter Discovery

### Adapter Info

Discover FDD adapter configuration in a project:

```bash
# Discover adapter from current directory
python3 scripts/fdd.py adapter-info

# Discover adapter from specific project root
python3 scripts/fdd.py adapter-info --root {project-root}
```

**Output** (JSON):
- `status`: `FOUND` or `NOT_FOUND`
- `adapter_dir`: Full path to FDD-Adapter directory
- `relative_path`: Relative path from project root
- `project_name`: Project name from adapter AGENTS.md
- `specs`: List of available spec files in specs/ directory

**Common adapter locations searched**:
- `FDD-Adapter/`
- `spec/FDD-Adapter/`
- `docs/FDD-Adapter/`
- `guidelines/FDD-Adapter/`

## Traceability Commands

### Scan IDs

```bash
# Scan IDs under a root (file or directory)
python3 scripts/fdd.py scan-ids --root {file-or-dir}
python3 scripts/fdd.py scan-ids --root {file-or-dir} --pattern "{substring}"
python3 scripts/fdd.py scan-ids --root {file-or-dir} --pattern "{regex}" --regex

# Filter by ID kind
python3 scripts/fdd.py scan-ids --root {file-or-dir} --kind {all|fdd|adr}
python3 scripts/fdd.py scan-ids --root {file-or-dir} --all  # Include duplicates

# Path filtering
python3 scripts/fdd.py scan-ids --root {file-or-dir} --include "**/*.rs" --include "**/*.md"
python3 scripts/fdd.py scan-ids --root {file-or-dir} --exclude "target/**" --exclude "node_modules/**"
python3 scripts/fdd.py scan-ids --root {file-or-dir} --max-bytes 5000000

# IMPORTANT: if pattern starts with '-', use '=' form:
python3 scripts/fdd.py scan-ids --root {file-or-dir} --pattern=-actor-
```

### Where Defined

```bash
# Find where an ID is DEFINED (normative)
python3 scripts/fdd.py where-defined --root {repo-root} --id {fdd-id-or-ADR-0001}

# Qualified IDs (phase/instruction): base -> ph -> inst
python3 scripts/fdd.py where-defined --root {repo-root} --id {base-id}:ph-1
python3 scripts/fdd.py where-defined --root {repo-root} --id {base-id}:ph-1:inst-some-job

# Optionally treat @fdd-* code tags as definitions too
python3 scripts/fdd.py where-defined --root {repo-root} --id {base-id}:ph-1 --include-tags

# Path filtering
python3 scripts/fdd.py where-defined --root {repo-root} --id {id} --include "modules/**"
python3 scripts/fdd.py where-defined --root {repo-root} --id {id} --exclude "target/**"
```

### Where Used

```bash
# Find where an ID is USED (all occurrences EXCEPT normative definitions)
python3 scripts/fdd.py where-used --root {repo-root} --id {fdd-id-or-qualified-id}

# Path filtering
python3 scripts/fdd.py where-used --root {repo-root} --id {id} --include "**/*.rs"
python3 scripts/fdd.py where-used --root {repo-root} --id {id} --exclude "target/**"
python3 scripts/fdd.py where-used --root {repo-root} --id {id} --max-bytes 5000000
```

## Artifact Type Auto-Detection

When `--requirements` is not provided, the tool automatically selects the appropriate requirements file:

- `BUSINESS.md` → `requirements/business-context-structure.md`
- `ADR.md` → `requirements/adr-structure.md`
- `FEATURES.md` → `requirements/features-manifest-structure.md`
- `DESIGN.md` (feature scope) → `requirements/feature-design-structure.md`
- `CHANGES.md` → `requirements/feature-changes-structure.md`
- `DESIGN.md` (non-feature scope) → `requirements/overall-design-structure.md`

## Traceability Semantics

### where-defined
- Resolves **normative** definition location based on ID type
- Searches only in expected artifacts by default
- Supports both root-level `architecture/...` and module-local `modules/*/architecture/...` layouts
- Supports qualified queries `{base-id}:ph-{N}:inst-{name}`
- Output fields: `status` (`FOUND`/`AMBIGUOUS`/`NOT_FOUND`), `definitions`, `context_definitions`, `base_id`, `phase`, `inst`
- Exit codes: `0` if exactly one definition, `2` if ambiguous, `1` if not found

### where-used
- Returns all occurrences of the query **excluding** normative definition lines
- Output fields: `hits`, `base_id`, `phase`, `inst`

## Output

All commands output JSON to stdout for machine consumption:
- Validation reports suitable for CI logs
- Search results with stable ordering
- Traceability data for cross-referencing

## Progressive Disclosure

- Use this skill to generate machine reports
- Use the referenced `requirements/*-structure.md` files only for deeper manual inspection

## Usage Examples

```bash
# Discover FDD adapter in project
python3 scripts/fdd.py adapter-info --root .

# Validate a feature DESIGN.md
python3 scripts/fdd.py validate --artifact architecture/features/feature-auth/DESIGN.md

# Find all actor IDs in BUSINESS.md
python3 scripts/fdd.py list-ids --artifact architecture/BUSINESS.md --pattern "-actor-"

# Scan all FDD IDs in the codebase
python3 scripts/fdd.py scan-ids --root . --kind fdd

# Find where a requirement is defined
python3 scripts/fdd.py where-defined --root . --id fdd-myapp-req-user-auth

# Find all usages of a feature flow
python3 scripts/fdd.py where-used --root . --id fdd-myapp-feature-auth-flow-login

# Validate codebase traceability for all features
python3 scripts/fdd.py validate --artifact .

# Validate specific features only
python3 scripts/fdd.py validate --artifact . --features auth,payment
```

## Read-Only Guarantee

Search and traceability commands (all except `validate`) are **read-only** and MUST NOT write or edit any artifact.
