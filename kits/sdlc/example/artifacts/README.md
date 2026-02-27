# Cypilot SDLC Rule Package

**ID**: `cypilot-sdlc`
**Purpose**: Software Development Lifecycle artifacts for Cypilot projects

---

## Artifact Kinds

| Kind | Description | Template | Checklist | Example |
| --- | --- | --- | --- | --- |
| PRD | Product Requirements Document | `{cypilot_path}/.gen/kits/sdlc/artifacts/PRD/template.md` | `{cypilot_path}/.gen/kits/sdlc/artifacts/PRD/checklist.md` | `{cypilot_path}/.gen/kits/sdlc/artifacts/PRD/examples/example.md` |
| DESIGN | Overall System Design | `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/template.md` | `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/checklist.md` | `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/examples/example.md` |
| ADR | Architecture Decision Record | `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/template.md` | `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/checklist.md` | `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/examples/example.md` |
| DECOMPOSITION | Design Decomposition | `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md` | `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md` | `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/examples/example.md` |
| FEATURE | Feature Design | `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md` | `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md` | `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/task-crud.md` |

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
template:  {cypilot_path}/.gen/kits/sdlc/artifacts/{KIND}/template.md
checklist: {cypilot_path}/.gen/kits/sdlc/artifacts/{KIND}/checklist.md
example:   {cypilot_path}/.gen/kits/sdlc/artifacts/{KIND}/examples/example.md
```

### In artifacts.toml

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
