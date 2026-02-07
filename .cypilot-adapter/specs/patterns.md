# Architecture Patterns

## Core Patterns

### 1. Template-Centric Architecture (ADR-0003)

**Pattern**: Make templates the foundation of everything. Each artifact type becomes a self-contained package.

**Structure**:
```
kits/sdlc/artifacts/{KIND}/
├── template.md       # The template with markers
├── rules.md          # Generation and validation rules
├── checklist.md      # Quality checklist
└── examples/         # Canonical examples
```

**Key Decisions**:
- Templates are self-contained units with their own generation and validation logic
- Consolidated workflows: `generate.md`, `analyze.md`, `adapter.md`
- Kit packages contain all rules, templates, checklists, and examples

### 2. Adaptive Workflow Model (ADR-0002)

**Pattern**: Enable "start anywhere" adoption where users can begin from any point (design, implementation, or validation).

**Key Decisions**:
- Adapter-owned `artifacts.json` registry for artifact discovery
- Support hierarchical project scopes (system → subsystem → module)
- Per-artifact traceability configuration (FULL vs DOCS-ONLY)
- Ask user when dependencies are missing instead of hard failure

### 3. Kit Package Pattern

**Pattern**: Validation rules and templates are packaged together as "kits" that can be reused across projects.

**Structure**:
```
kits/{kit-id}/
├── artifacts/        # Artifact templates (PRD, DESIGN, etc.)
├── codebase/         # Code rules and checklists
└── guides/           # Usage guides
```

**Benefits**:
- Single source of truth for artifact validation
- Easy to customize by creating custom kits
- Shareable across multiple projects

## Design Patterns in CLI

### 4. Context Loading Pattern

**Pattern**: Global `CypilotContext` loaded at CLI startup, providing access to adapter, kits, and registry.

**Implementation**: [context.py](skills/cypilot/scripts/cypilot/utils/context.py)

### 5. Template Marker Pattern

**Pattern**: Templates use HTML comments as markers for structure validation.

**Format**: `<!-- cpt:marker:type -->`

**Implementation**: [template.py](skills/cypilot/scripts/cypilot/utils/template.py)

### 6. Cypilot ID Pattern

**Pattern**: Unique identifiers for traceability in format `cpt-{system}-{kind}-{slug}`.

**Examples**:
- `cpt-cypilot-fr-1` — Functional requirement
- `cpt-cypilot-component-1` — Component definition
- `cpt-cypilot-flow-1` — Flow definition

**Implementation**: [parsing.py](skills/cypilot/scripts/cypilot/utils/parsing.py)

---

**Source**: ADR-0002, ADR-0003, DESIGN.md
**Last Updated**: 2026-02-03
