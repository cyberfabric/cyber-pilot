# Spider SDLC Rule Package

**ID**: `spider-sdlc`
**Purpose**: Software Development Lifecycle artifacts for Spider projects

---

## Artifact Kinds

| Kind | Description | Template | Checklist | Example |
|------|-------------|----------|-----------|---------|
| PRD | Product Requirements Document | `PRD/template.md` | `PRD/checklist.md` | `PRD/examples/example.md` |
| DESIGN | Overall System Design | `DESIGN/template.md` | `DESIGN/checklist.md` | `DESIGN/examples/example.md` |
| ADR | Architecture Decision Record | `ADR/template.md` | `ADR/checklist.md` | `ADR/examples/example.md` |
| DECOMPOSITION | Design Decomposition | `DECOMPOSITION/template.md` | `DECOMPOSITION/checklist.md` | `DECOMPOSITION/examples/example.md` |
| FEATURE | Feature Design | `FEATURE/template.md` | `FEATURE/checklist.md` | `FEATURE/examples/example.md` |

---

## Structure

```
weavers/sdlc/
├── README.md           # This file
├── PRD/
│   ├── template.md     # PRD template with Spider markers
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
├── DECOMPOSITION/
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
template:  weavers/sdlc/{KIND}/template.md
checklist: weavers/sdlc/{KIND}/checklist.md
example:   weavers/sdlc/{KIND}/examples/example.md
```

### In artifacts.json

```json
{
  "rules": {
    "spider-sdlc": {
      "path": "weavers/sdlc",
      "artifacts": ["PRD", "DESIGN", "ADR", "DECOMPOSITION", "FEATURE"]
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
      └── DECOMPOSITION
           └── FEATURE (per feature)
```

Each child artifact references IDs from parent artifacts for traceability.
