# FDD Core Rules

This directory contains the **meta-rules** for FDD - the rules that generate and validate all other rules.

## Self-Bootstrapping Architecture

The core rules are **self-referential**: they can generate and validate themselves, similar to compiler bootstrapping.

```
rules/core/
├── validate/       # Rules for validation workflows
├── generate/       # Rules for generation workflows
├── checklist/      # Rules for checklists
├── template/       # Rules for templates
└── examples/       # Rules for examples
```

Each folder represents a **KIND** of rule artifact:

| KIND | Description | Produces |
|------|-------------|----------|
| `VALIDATE-WORKFLOW` | Validation workflow rules | `*-validate.md` workflows |
| `GENERATE-WORKFLOW` | Generation workflow rules | `*.md` generation workflows |
| `CHECKLIST` | Checklist rules | `checklists/*.md` |
| `TEMPLATE` | Template rules | `*.template.md` |
| `EXAMPLE` | Example rules | `examples/*.md` |

## How It Works

Each KIND folder contains:
- `template.md` - The FDD template with markers
- `checklist.md` - Validation checklist
- `workflows/generate.md` - How to create this KIND
- `workflows/validate.md` - How to validate this KIND

### To Generate Rules for KIND=X

```bash
# Execute the generate workflow for KIND
fdd-generate @rules/core/{X}/workflows/generate.md
```

Example - generate a new validation workflow:
```bash
fdd-generate @rules/core/validate/workflows/generate.md
```

### To Validate Rules for KIND=X

```bash
# Execute the validate workflow for KIND
fdd-validate @rules/core/{X}/workflows/validate.md
```

## Bootstrap Sequence

To bootstrap the core rules themselves:

1. **Templates first** - Generate template templates
   ```bash
   fdd-generate @rules/core/template/workflows/generate.md
   ```

2. **Checklists** - Generate checklist for each kind
   ```bash
   fdd-generate @rules/core/checklist/workflows/generate.md
   ```

3. **Workflows** - Generate generation and validation workflows
   ```bash
   fdd-generate @rules/core/generate/workflows/generate.md
   fdd-generate @rules/core/validate/workflows/generate.md
   ```

4. **Validate all** - Ensure consistency
   ```bash
   fdd-validate @rules/core/template/workflows/validate.md
   fdd-validate @rules/core/checklist/workflows/validate.md
   fdd-validate @rules/core/generate/workflows/validate.md
   fdd-validate @rules/core/validate/workflows/validate.md
   ```

## Key Principles

1. **Everything is a KIND** - Templates, checklists, workflows are all artifact kinds
2. **Rules generate rules** - Use generate workflows to create new rules
3. **Rules validate rules** - Use validate workflows to ensure conformance
4. **Self-consistency** - Core rules must pass their own validation

## Path Resolution

Within core rules, paths follow this pattern:

| Context | Path |
|---------|------|
| Template for KIND | `rules/core/{kind}/template.md` |
| Checklist for KIND | `rules/core/{kind}/checklist.md` |
| Generate workflow | `rules/core/{kind}/workflows/generate.md` |
| Validate workflow | `rules/core/{kind}/workflows/validate.md` |

## Usage in artifacts.json

```json
{
  "rules": {
    "fdd-core": {
      "format": "FDD",
      "path": "rules/core"
    }
  }
}
```
