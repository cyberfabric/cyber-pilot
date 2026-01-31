---
name: fdd
description: Unified FDD tool for validation and search. Validates FDD artifacts registered in `{adapter-dir}/artifacts.json` against FDD requirements with cascading dependency validation. Provides read-only search and traceability for FDD artifacts and FDD/ADR IDs with repo-wide scanning capabilities. Supports optional project-level configuration via .fdd-config.json.
---

# FDD Unified Tool

## Goal

Provides comprehensive FDD artifact management:
1. **Cascading Validation**: Automatically discovers and validates all artifact dependencies
2. **Cross-Reference Validation**: Validates references between artifacts (PRD → ADR → DESIGN → FEATURES → feature designs)
3. **Code Traceability**: Codebase scanning to verify implemented DESIGN items are tagged in code
4. **Search**: Read-only search and traceability across FDD artifacts and IDs

## Preconditions

1. ALWAYS follow `../SKILLS.md` Toolchain Preflight
2. `python3` is available
3. Target paths exist and are readable

## Agent-Safe Invocation (MANDATORY)

**MUST** prefer invoking this tool via the script entrypoint (avoids `cwd`/`PYTHONPATH` issues):
```bash
python3 <FDD_ROOT>/skills/fdd/scripts/fdd.py <subcommand> [options]
```

**MUST NOT** use `python3 -m fdd.cli` unless the current working directory is `<FDD_ROOT>/skills/fdd/scripts`.

**Pattern arguments**:
- If a value starts with `-`, **MUST** pass it using `=` form (example: `--pattern=-req-`).

## Command Structure

The unified tool uses subcommands for different operations:

```bash
python3 scripts/fdd.py <subcommand> [options]
```

## Agent Integration (Workflows and Skills)

This tool can generate agent/IDE integration files that point back to existing FDD workflows and this skill.

### Initialize a Project (Bootstrap)

Create a minimal project configuration and adapter scaffold so other commands (like `agent-workflows`) can locate your project root.

```bash
python3 scripts/fdd.py init
```

**Behavior**:
- Interactively asks where to create `.fdd-config.json` (default: parent directory of the detected FDD core folder)
- Interactively asks where to create the adapter directory (default: `FDD-Adapter` under project root)
- Writes `.fdd-config.json` with `fddCorePath` and `fddAdapterPath`
- Creates an adapter `AGENTS.md` that **Extends** the FDD core `AGENTS.md`

**Non-interactive**:
```bash
python3 scripts/fdd.py init --yes
python3 scripts/fdd.py init --project-root . --adapter-path FDD-Adapter --yes
```

**Safety flags**:
- `--dry-run`: compute changes without writing files
- `--force`: overwrite/merge existing `.fdd-config.json` and adapter `AGENTS.md`

**Supported agents (built-in defaults)**:
- `windsurf`
- `cursor`
- `claude`
- `copilot`

### Generate Agent Workflow Proxies

Create or update agent-specific workflow proxy files (example: Windsurf `.windsurf/workflows/*.md`).

```bash
python3 scripts/fdd.py agent-workflows --agent windsurf
python3 scripts/fdd.py agent-workflows --agent windsurf --dry-run
```

**Behavior**:
- Creates/updates workflow proxy files (one per FDD workflow)
- Renames misnamed proxy files to the canonical `fdd-{workflow}.md` naming where safe
- Deletes stale proxy files that point to workflows that no longer exist

**Config**:
- Default file: `fdd-agent-workflows.json`
- If the agent is unknown, the tool creates a stub config and exits with `CONFIG_INCOMPLETE` until you fill in the required fields.

### Generate Agent Skills

Create or update agent-specific skill outputs (example: Windsurf `.windsurf/skills/fdd/SKILL.md`).

```bash
python3 scripts/fdd.py agent-skills --agent windsurf
python3 scripts/fdd.py agent-skills --agent windsurf --dry-run
```

**Config**:
- Default file: `fdd-agent-skills.json`

**Schema**:
- Preferred: `outputs[]` (array of output files)
- Legacy: a single skill folder schema (`skills_dir`, `skill_name`, `entry_filename`, `template`) is still supported for backward compatibility

For each output, the generated content is a proxy that instructs the agent to open and follow this canonical file.

### Unknown Agent Behavior

For both `agent-workflows` and `agent-skills`:
- If the config file does not exist, it is created with an empty stub for the requested agent.
- If required fields are missing, the command exits with `CONFIG_INCOMPLETE` (exit code `2`).
- No agent files are generated until the config is completed.

## Project Configuration

This tool optionally reads a project-level configuration file located at the project root:
- `.fdd-config.json`

If present, it can configure FDD core location, adapter path, and language-specific settings.

**Example**:
```json
{
  "fddCorePath": ".fdd",
  "fddAdapterPath": "FDD-Adapter",
  "skipCodeTraceability": false,
  "codeScanning": {
    "fileExtensions": [".py", ".js", ".ts", ".go", ".rs"],
    "singleLineComments": ["#", "//", "--"],
    "multiLineComments": [
      {"start": "/*", "end": "*/"},
      {"start": "<!--", "end": "-->"}
    ],
    "blockCommentPrefixes": ["*"]
  }
}
```

**Supported fields**:
- **`fddCorePath`**: Relative path from project root to the FDD core directory.
- **`fddAdapterPath`**: Relative path to the FDD adapter directory (e.g., `FDD-Adapter`, `.fdd-adapter`).
- **`skipCodeTraceability`**: Skip code traceability validation (`true`/`false`). Artifact validation and cross-references still work.
- **`codeScanning`**: Language-specific configuration for code traceability scanning (optional).
  - **`fileExtensions`**: Array of file extensions to scan (e.g., `[".py", ".js", ".go"]`).
  - **`singleLineComments`**: Array of single-line comment prefixes (e.g., `["#", "//", "--"]`).
  - **`multiLineComments`**: Array of multi-line comment marker objects with `start` and `end` fields.
  - **`blockCommentPrefixes`**: Array of continuation markers inside comment blocks (e.g., `["*"]`).

**Language Configuration**:
- Enables FDD to work with **any programming language** by configuring comment styles.
- If `codeScanning` is omitted, defaults are used (Python, JS/TS, Go, Rust, Java, C#, SQL, etc.).
- Custom languages (PHP, Ruby, Kotlin, Swift, etc.) can be configured via this section.

**Discovery rules**:
- The tool searches upwards from the current working directory.
- The first directory that contains `.fdd-config.json` is treated as the project root.
- If `.fdd-config.json` is not present, the tool falls back to marker-based FDD core detection.

## Validation Commands

### Full Validation (Default)

```bash
# Validate everything (artifacts + code traceability)
python3 scripts/fdd.py validate

# Same as above, explicit current directory
python3 scripts/fdd.py validate --artifact .
```

**Output**:
- Default output is a **compact JSON summary** focused on failures.
- Use `--verbose` to print the full report.

This performs **cascading validation**:
1. **PRD.md** — validates PRD structure
2. **ADR (directory)** — validates ADR structure, cross-refs to PRD
3. **DESIGN.md** — validates overall design, cross-refs to PRD.md and ADRs
4. **FEATURES.md** — validates features manifest, cross-refs to DESIGN.md requirements
5. **Feature DESIGN.md** — validates each feature design, cross-refs to overall DESIGN.md
6. **Code Traceability** — scans code for `@fdd-` tags matching implemented scopes

### Artifact-Only Validation (Skip Code Tracing)

```bash
# Code traceability is controlled by the artifacts registry.
# Configure `{adapter-dir}/artifacts.json` entries (kind: SRC) using `traceability_enabled`.
python3 scripts/fdd.py validate
```

### Single Artifact Validation

```bash
# Validate specific artifact with cascading dependencies
python3 scripts/fdd.py validate --artifact {feature_design_path_from_artifacts_json}

# Validate with explicit requirements file (no cascading)
python3 scripts/fdd.py validate --artifact {path} --requirements {path}

# Skip filesystem checks
python3 scripts/fdd.py validate --artifact {path} --skip-fs-checks

# Print full report (includes traceability expected/found details when applicable)
python3 scripts/fdd.py validate --artifact {path} --verbose

# Save validation report
python3 scripts/fdd.py validate --artifact {path} --output {path}
```

### Feature Filtering

```bash
# Validate only specific features' code traceability
python3 scripts/fdd.py validate --features auth,payment
```

### Artifact Dependency Graph

When validating any artifact, the tool automatically discovers and validates its dependencies:

```
feature-design → features-manifest → overall-design → (prd, adr)
                                                             adr → prd
```

### What Validation Checks

**Artifact Structure**:
- Required sections (derived from requirements/*-content.md)
- Placeholder markers: `TODO`, `TBD`, `FIXME`, `XXX`, `TBA`
- Cross-references between artifacts
- ID format and uniqueness

**Cross-Reference Validation**:
- FEATURES.md covers all DESIGN.md requirement IDs
- Feature DESIGN.md status matches FEATURES.md status
- ADR references valid PRD items

**Code Traceability** (when enabled):
- For each implemented scope (`- [x] **ID**: ...`), expects `@fdd-{kind}:...:ph-{N}` tag in code
- For each implemented FDL step line (`[x] ... - `inst-...``), expects instruction-level marker
- File extensions for scanning are configured via `.fdd-config.json` → `codeScanning.fileExtensions`
- Default extensions: `.py`, `.md`, `.js`, `.ts`, `.tsx`, `.go`, `.rs`, `.java`, `.cs`, `.sql`

## Search Commands

### List IDs

```bash
python3 scripts/fdd.py list-ids  # Scan all FDD artifacts from adapter
python3 scripts/fdd.py list-ids --artifact {path}  # Scan specific artifact
python3 scripts/fdd.py list-ids --pattern "{substring}"
python3 scripts/fdd.py list-ids --pattern "{regex}" --regex
python3 scripts/fdd.py list-ids --kind {requirement|feature|actor|...}  # Filter by ID kind
python3 scripts/fdd.py list-ids --all  # Include duplicates
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

# Agent usage: pass FDD location for enhanced validation
python3 scripts/fdd.py adapter-info --root {project-root} --fdd-root {fdd-core-path}
```

**Output** (JSON):
- `status`: `FOUND` or `NOT_FOUND`
- `adapter_dir`: Full path to FDD-Adapter directory
- `relative_path`: Relative path from project root
- `project_name`: Project name from adapter AGENTS.md
- `specs`: List of available spec files in specs/ directory
- `has_config`: Whether .fdd-config.json exists
- `config_hint`: Suggested config content (if config missing)

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

- `PRD.md` → `requirements/prd-content.md`
- `ADR/` → `requirements/adr-content.md`
- `FEATURES.md` → `requirements/features-manifest-content.md`
- `DESIGN.md` (feature scope) → `requirements/feature-design-content.md`
- `DESIGN.md` (non-feature scope) → `requirements/overall-design-content.md`

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
- Use the referenced `requirements/*-content.md` files only for deeper manual inspection

## Usage Examples

```bash
# Full validation (all artifacts + code traceability)
python3 scripts/fdd.py validate

# Artifact-only validation (skip code tracing)
python3 scripts/fdd.py validate --skip-code-traceability

# Validate specific artifact with cascading dependencies
python3 scripts/fdd.py validate --artifact {feature_design_path_from_artifacts_json}

# Validate specific features' code traceability only
python3 scripts/fdd.py validate --features auth,payment

# Discover FDD adapter in project
python3 scripts/fdd.py adapter-info --root .

# Find all actor IDs in PRD.md
python3 scripts/fdd.py list-ids --artifact {prd_path_from_artifacts_json} --pattern "-actor-"

# Scan all FDD IDs in the codebase
python3 scripts/fdd.py scan-ids --root . --kind fdd

# Find where a requirement is defined
python3 scripts/fdd.py where-defined --root . --id fdd-myapp-req-user-auth

# Find all usages of a feature flow
python3 scripts/fdd.py where-used --root . --id fdd-myapp-feature-auth-flow-login
```

## Validation Output

Default validation output is a compact JSON summary. It includes high-level status and counts, and only includes detailed lists when something fails.

```json
{
  "status": "PASS|FAIL",
  "artifact_kind": "codebase-trace",
  "code_root": "/path/to/repo",
  "artifact_validation": { "pass_count": 25, "fail_count": 0 },
  "feature_reports": { "feature_count": 20, "pass_count": 20, "fail_count": 0, "failures": [] }
}
```

Full validation output (`--verbose`) prints the complete report (including per-artifact sections and traceability `expected`/`found` details).

## Read-Only Guarantee

Search and traceability commands (all except `validate`) are **read-only** and MUST NOT write or edit any artifact.
