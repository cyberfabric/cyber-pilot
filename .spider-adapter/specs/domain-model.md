# Domain Model

## Core Concepts

### Spider Framework
Spider (Framework for Documentation and Development) is a workflow-centered methodology framework for AI-assisted software development with design-to-code traceability.

### Weaver
A **weaver** is a package containing templates, rules, checklists, and examples for artifact validation. Located at `weavers/{weaver-id}/`.

```
weavers/sdlc/
├── artifacts/
│   ├── PRD/          # Product Requirements Document
│   ├── DESIGN/       # Technical Design
│   ├── DECOMPOSITION/     # Features Manifest
│   ├── FEATURE/      # Individual Feature Design
│   └── ADR/          # Architecture Decision Record
├── codebase/
│   ├── rules.md
│   └── checklist.md
└── guides/
```

### Adapter
A **project-specific adapter** in `.spider-adapter/` that configures Spider for a project:
- `AGENTS.md` - Navigation rules (WHEN clauses)
- `artifacts.json` - Registry of systems, artifacts, codebase
- `specs/*.md` - Project-specific specifications

### Artifact
A **design document** tracked by Spider (PRD, DESIGN, DECOMPOSITION, FEATURE, ADR). Each artifact:
- Has a `kind` matching a weaver template
- Has a `path` in the project
- Has `traceability` level (FULL or DOCS-ONLY)

### Spider ID
A **unique identifier** in format `spd-{system}-{kind}-{number}`:
- `spd-spider-fr-1` - Functional requirement
- `spd-spider-component-1` - Component definition
- `spd-spider-flow-1` - Flow definition

### Spider Marker
**Code traceability markers** linking code to design:
- `@spider-{kind}:{id}:{phase}` - Reference marker
- `# @spider-fr:spd-spider-fr-1:impl` - Implementation marker

### Traceability Levels
- **FULL** - Code must have Spider markers linking to artifact IDs
- **DOCS-ONLY** - Documentation traceability only, no code markers

---

## System Hierarchy

```
artifacts.json
└── systems[]
    ├── name: "Spider"
    ├── weaver: "spider-sdlc"
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
- `get_weaver(id)` → Weaver
- `get_artifact_by_path(path)` → (Artifact, SystemNode)
- `iter_all_artifacts()` → Iterator
- `iter_all_codebase()` → Iterator

### SpiderContext
Global context loaded at CLI startup:
- `adapter_dir` - Path to adapter
- `project_root` - Path to project root
- `meta` - ArtifactsMeta instance
- `weavers` - Dict of LoadedWeaver (templates loaded)
- `registered_systems` - Set of system names

### Template
Parsed template from `template.md`:
- `kind` - Artifact kind (PRD, DESIGN, etc.)
- `version` - Template version (major.minor)
- `blocks` - List of TemplateBlock markers

### CodeFile
Parsed source file with Spider markers:
- `path` - File path
- `references` - List of CodeReference
- `scope_markers` - List of ScopeMarker

---

## Workflows

### generate.md
Creates/updates artifacts following template rules.

### validate.md
Validates artifacts against templates and traceability rules.

### adapter.md
Creates/updates project adapter configuration.

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize Spider config and adapter |
| `adapter-info` | Show adapter discovery information |
| `validate` | Validate artifact against template |
| `validate-code` | Validate code file traceability |
| `validate-weavers` | Validate weaver templates |
| `scan-ids` | Scan and list all Spider IDs |
| `where-defined` | Find where an ID is defined |
| `where-used` | Find where an ID is referenced |
| `refs` | Search for ID references |
| `self-check` | Validate weaver package integrity |

---

**Source**: Extracted from architecture/DESIGN.md and codebase analysis
**Last Updated**: 2026-02-03
