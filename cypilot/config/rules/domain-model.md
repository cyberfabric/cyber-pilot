---
cypilot: true
type: project-rule
topic: domain-model
generated-by: auto-config
version: 1.0
---

# Domain Model


<!-- toc -->

- [Core Concepts](#core-concepts)
  - [Cypilot Framework](#cypilot-framework)
  - [Kit](#kit)
  - [Adapter](#adapter)
  - [Artifact](#artifact)
  - [Cypilot ID](#cypilot-id)
  - [Cypilot Marker](#cypilot-marker)
  - [Traceability Levels](#traceability-levels)
- [System Hierarchy](#system-hierarchy)
- [Key Data Structures](#key-data-structures)
  - [ArtifactsMeta](#artifactsmeta)
  - [CypilotContext](#cypilotcontext)
  - [Template](#template)
  - [CodeFile](#codefile)
- [Workflows](#workflows)
  - [generate.md](#generatemd)
  - [analyze.md](#analyzemd)
- [CLI Commands](#cli-commands)

<!-- /toc -->

## Core Concepts

### Cypilot Framework
Cypilot is a workflow-centered methodology framework for AI-assisted software development with design-to-code traceability.

### Kit
A **kit** is a package containing templates, rules, checklists, and examples for artifact validation. Located at `kits/{kit-id}/`.

```
kits/sdlc/
├── artifacts/
│   ├── PRD/          # Product Requirements Document
│   ├── DESIGN/       # Technical Design
│   ├── DECOMPOSITION/     # Specs Manifest
│   ├── FEATURE/      # Feature Design
│   └── ADR/          # Architecture Decision Record
├── codebase/
│   ├── rules.md
│   └── checklist.md
└── guides/
```

### Adapter
A **project-specific configuration** in `cypilot/config/` that configures Cypilot for a project:
- `AGENTS.md` - Custom navigation rules (WHEN clauses)
- `artifacts.toml` - Registry of systems, artifacts, codebase
- `rules/*.md` - Project-specific rules (per-topic)
- `core.toml` - Project settings (system name, kit references)

### Artifact
A **design document** tracked by Cypilot (PRD, DESIGN, DECOMPOSITION, FEATURE, ADR). Each artifact:
- Has a `kind` matching a kit template
- Has a `path` in the project
- Has `traceability` level (FULL or DOCS-ONLY)

### Cypilot ID
A **unique identifier** in format `cpt-{hierarchy-prefix}-{kind}-{slug}`:
- `cpt-cypilot-fr-must-authenticate` - Functional requirement
- `cpt-cypilot-core-comp-api-gateway` - Component definition
- `cpt-cypilot-core-auth-flow-login` - Flow definition

### Cypilot Marker
**Code traceability markers** linking code to design:
- `@cpt-{kind}:{cpt-id}:p{N}` - Scope marker
- `@cpt-begin:{cpt-id}:p{N}:inst-{local}` / `@cpt-end:{cpt-id}:p{N}:inst-{local}` - Block markers

### Traceability Levels
- **FULL** - Code markers are allowed and validated
- **DOCS-ONLY** - Documentation traceability only, no code markers

## System Hierarchy

```
artifacts.toml
└── systems[]
    ├── name: "Cypilot"
    ├── kit: "cypilot-sdlc"
    ├── artifacts[]
    │   └── {path, kind, traceability}
    ├── codebase[]
    │   └── {path, extensions, comments}
    └── children[]  (nested subsystems)
```

## Key Data Structures

### ArtifactsMeta
Parses `artifacts.toml` and provides lookups:
- `get_kit(id)` → Kit
- `get_artifact_by_path(path)` → (Artifact, SystemNode)
- `iter_all_artifacts()` → Iterator
- `iter_all_codebase()` → Iterator

### CypilotContext
Global context loaded at CLI startup:
- `adapter_dir` - Path to adapter
- `project_root` - Path to project root
- `meta` - ArtifactsMeta instance
- `kits` - Dict of LoadedKit (templates loaded)
- `registered_systems` - Set of system names

### Template
Parsed template from `template.md`:
- `kind` - Artifact kind (PRD, DESIGN, etc.)
- `version` - Template version (major.minor)
- `blocks` - List of TemplateBlock markers

### CodeFile
Parsed source file with Cypilot markers:
- `path` - File path
- `references` - List of CodeReference
- `scope_markers` - List of ScopeMarker

## Workflows

### generate.md
Creates/updates artifacts following template rules.

### analyze.md
Validates artifacts against templates and traceability rules.

## CLI Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize Cypilot config and adapter |
| `info` | Show adapter discovery information |
| `validate` | Validate artifact against template |
| `validate-kits` | Validate kit templates |
| `list-ids` | Scan and list all Cypilot IDs |
| `where-defined` | Find where an ID is defined |
| `where-used` | Find where an ID is referenced |
| `self-check` | Validate kit package integrity |
| `update` | Update skill cache from GitHub or local source |
