# FDD SDLC Rule Package

**ID**: `fdd-sdlc`
**Purpose**: Software Development Lifecycle artifacts for FDD projects

---

## Artifact Kinds

| Kind | Description | Template | Checklist | Example |
|------|-------------|----------|-----------|---------|
| PRD | Product Requirements Document | `PRD/template.md` | `PRD/checklist.md` | `PRD/examples/example.md` |
| DESIGN | Overall System Design | `DESIGN/template.md` | `DESIGN/checklist.md` | `DESIGN/examples/example.md` |
| ADR | Architecture Decision Record | `ADR/template.md` | `ADR/checklist.md` | `ADR/examples/example.md` |
| FEATURES | Feature Manifest | `FEATURES/template.md` | `FEATURES/checklist.md` | `FEATURES/examples/example.md` |
| FEATURE | Feature Design | `FEATURE/template.md` | `FEATURE/checklist.md` | `FEATURE/examples/example.md` |

---

## Structure

```
rules/sdlc/
├── README.md           # This file
├── PRD/
│   ├── template.md     # PRD template with FDD markers
│   ├── checklist.md    # Expert review checklist
│   └── examples/
│       └── example.md  # Valid PRD example
├── DESIGN/
│   ├── template.md
│   ├── checklist.md
│   └── examples/
│       └── example.md
├── ADR/
│   ├── template.md
│   ├── checklist.md
│   └── examples/
│       └── example.md
├── FEATURES/
│   ├── template.md
│   ├── checklist.md
│   └── examples/
│       └── example.md
└── FEATURE/
    ├── template.md
    ├── checklist.md
    └── examples/
        └── example.md
```

---

## Usage

### In execution-protocol.md

Dependencies resolved as:
```
template:  rules/sdlc/{KIND}/template.md
checklist: rules/sdlc/{KIND}/checklist.md
example:   rules/sdlc/{KIND}/examples/example.md
```

### In artifacts.json

```json
{
  "rules": {
    "fdd-sdlc": {
      "path": "rules/sdlc",
      "artifacts": ["PRD", "DESIGN", "ADR", "FEATURES", "FEATURE"]
    }
  }
}
```

---

## Artifact Hierarchy

```
PRD
 └── DESIGN
      ├── ADR (optional, per decision)
      └── FEATURES
           └── FEATURE (per feature)
```

Each child artifact references IDs from parent artifacts for traceability.
