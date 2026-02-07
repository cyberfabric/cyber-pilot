# Domain Model

## Core Concepts

### Cypilot Framework
Cypilot (Framework for Documentation and Development) is a workflow-centered methodology framework for AI-assisted software development with design-to-code traceability.

### Kit
A **kit** is a package containing templates, rules, checklists, and examples for artifact validation. Located at `kits/{kit-id}/`.

```
kits/sdlc/
├── artifacts/
│   ├── PRD/          # Product Requirements Document
│   ├── DESIGN/       # Technical Design
│   ├── DECOMPOSITION/     # Specs Manifest
│   ├── SPEC/      # Individual Spec Design
│   └── ADR/          # Architecture Decision Record
├── codebase/
│   ├── rules.md
│   └── checklist.md
└── guides/
```

### Adapter
A **project-specific adapter** in `.cypilot-adapter/` that configures Cypilot for a project:
- `AGENTS.md` - Navigation rules (WHEN clauses)
- `artifacts.json` - Registry of systems, artifacts, codebase
- `specs/*.md` - Project-specific specifications

### Artifact
A **design document** tracked by Cypilot (PRD, DESIGN, DECOMPOSITION, SPEC, ADR). Each artifact:
- Has a `kind` matching a kit template
- Has a `path` in the project
- Has `traceability` level (FULL or DOCS-ONLY)

### Cypilot ID
A **unique identifier** in format `cpt-{system}-{kind}-{number}`:
- `cpt-cypilot-fr-1` - Functional requirement
- `cpt-cypilot-component-1` - Component definition
- `cpt-cypilot-flow-1` - Flow definition

### Cypilot Marker
**Code traceability markers** linking code to design:
- `@cpt-{kind}:{id}:{phase}` - Reference marker
- `# @cpt-fr:cpt-cypilot-fr-1:impl` - Implementation marker

### Traceability Levels
- **FULL** - Code must have Cypilot markers linking to artifact IDs
- **DOCS-ONLY** - Documentation traceability only, no code markers

---

## System Hierarchy

```
artifacts.json
└── systems[]
    ├── name: "Cypilot"
    ├── kit: "cypilot-sdlc"
    ├── artifacts[]
    │   └── {path, kind, traceability}
    ├── codebase[]
    │   └── {path, extensions, comments}
    └── children[]  (nested subsystems)
```

---

## Key Data Structures

### ArtifactsMeta
Parses `artifacts.json` and provides lookups:
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

---

## Workflows

### generate.md
Creates/updates artifacts following template rules.

### analyze.md
Validates artifacts against templates and traceability rules.

### adapter.md
Creates/updates project adapter configuration.

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize Cypilot config and adapter |
| `adapter-info` | Show adapter discovery information |
| `validate` | Validate artifact against template |
| `validate-code` | Validate code file traceability |
| `validate-kits` | Validate kit templates |
| `scan-ids` | Scan and list all Cypilot IDs |
| `where-defined` | Find where an ID is defined |
| `where-used` | Find where an ID is referenced |
| `refs` | Search for ID references |
| `self-check` | Validate kit package integrity |

---

**Source**: Extracted from architecture/DESIGN.md and codebase analysis
**Last Updated**: 2026-02-03
