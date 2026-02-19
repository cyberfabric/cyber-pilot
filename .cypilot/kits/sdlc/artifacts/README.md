# Cypilot SDLC Rule Package

**ID**: `cypilot-sdlc`
**Purpose**: Software Development Lifecycle artifacts for Cypilot projects

---

## Artifact Kinds

| Kind | Description | Template | Checklist | Example |
| --- | --- | --- | --- | --- |
| PRD | Product Requirements Document | `artifacts/PRD/template.md` | `artifacts/PRD/checklist.md` | `artifacts/PRD/examples/example.md` |
| DESIGN | Overall System Design | `artifacts/DESIGN/template.md` | `artifacts/DESIGN/checklist.md` | `artifacts/DESIGN/examples/example.md` |
| ADR | Architecture Decision Record | `artifacts/ADR/template.md` | `artifacts/ADR/checklist.md` | `artifacts/ADR/examples/example.md` |
| DECOMPOSITION | Design Decomposition | `artifacts/DECOMPOSITION/template.md` | `artifacts/DECOMPOSITION/checklist.md` | `artifacts/DECOMPOSITION/examples/example.md` |
| FEATURE | Feature Design | `artifacts/FEATURE/template.md` | `artifacts/FEATURE/checklist.md` | `artifacts/FEATURE/examples/task-crud.md` |

---

## Structure

```text
kits/sdlc/
├── README.md           # This file
├── artifacts/
│   ├── PRD/
│   │   ├── template.md     # PRD template with Cypilot markers
│   │   ├── checklist.md    # Expert review checklist
│   │   └── examples/
│   │       └── example.md  # Valid PRD example
│   ├── DESIGN/
│   │   ├── template.md
│   │   ├── checklist.md
│   │   └── examples/
│   │       └── example.md
│   ├── ADR/
│   │   ├── template.md
│   │   ├── checklist.md
│   │   └── examples/
│   │       └── example.md
│   ├── DECOMPOSITION/
│   │   ├── template.md
│   │   ├── checklist.md
│   │   └── examples/
│   │       └── example.md
│   └── FEATURE/
│       ├── template.md
│       ├── checklist.md
│       └── examples/
│           └── task-crud.md
└── codebase/
    ├── rules.md            # Code generation/validation rules
    └── checklist.md        # Kit-specific code checklist
```

---

## Usage

### In execution-protocol.md

Dependencies resolved as:

```text
template:  kits/sdlc/artifacts/{KIND}/template.md
checklist: kits/sdlc/artifacts/{KIND}/checklist.md
example:   kits/sdlc/artifacts/{KIND}/examples/example.md
```

### In artifacts.json

```json
{
  "rules": {
    "cypilot-sdlc": {
      "path": "kits/sdlc",
      "artifacts": ["PRD", "DESIGN", "ADR", "DECOMPOSITION", "FEATURE"]
    }
  }
}
```

---

## Artifact Hierarchy

```text
PRD
 └── DESIGN
      ├── ADR (optional, per decision)
      └── DECOMPOSITION
           └── FEATURE (per feature)
```

Each child artifact references IDs from parent artifacts for traceability.
