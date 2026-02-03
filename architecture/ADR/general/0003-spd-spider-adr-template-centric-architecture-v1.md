<!-- spd:#:adr -->
# ADR-0003: Template-Centric Architecture and Workflow Consolidation

<!-- spd:id:adr has="priority,task" covered_by="DESIGN" -->
- [x] `p1` - **ID**: `spd-spider-adr-template-centric-architecture-v1`

<!-- spd:##:meta -->
## Meta

<!-- spd:paragraph:adr-title -->
**Title**: ADR-0003 Template-Centric Architecture and Workflow Consolidation
<!-- spd:paragraph:adr-title -->

<!-- spd:paragraph:date -->
**Date**: 2026-01-31
<!-- spd:paragraph:date -->

<!-- spd:paragraph:status -->
**Status**: Proposed
<!-- spd:paragraph:status -->
<!-- spd:##:meta -->

<!-- spd:##:body -->
## Body

<!-- spd:context -->
**Context**:
The current Spider architecture has grown organically with many separate workflow files (`prd.md`, `design.md`, `features.md`, `feature.md`, `adr.md`, `code.md` plus their `-validate` variants) and content requirements scattered across `requirements/*-content.md` files. This creates several problems:

1. **Maintenance burden**: Changes to common patterns require updates in multiple files
2. **Customization difficulty**: Adding a new artifact type requires creating multiple files (workflow, validate workflow, requirements, checklist)
3. **Scattered documentation**: Requirements, checklists, and workflows for one artifact type live in different directories
4. **No content versioning**: When an Spider ID's content changes, references to that ID cannot detect the change, leading to stale cross-references
5. **Naming confusion**: "Spider" has evolved beyond "Feature-Driven Design" and needs a name that reflects its broader scope as a documentation and development framework

In this ADR, "Spider" is interpreted as **Framework for Documentation and Development** (working title).
<!-- spd:context -->

<!-- spd:decision-drivers -->
**Decision Drivers**:
- Enable high customizability of the documentation platform without core modifications
- Templates should be self-contained units with their own generation and validation logic
- Reduce workflow proliferation and simplify the entry points
- Provide Spider ID versioning to detect stale references
- Consolidate type-specific documentation (requirements, checklists, workflows) with templates
- Support the "start anywhere" adaptive execution model established in ADR-0002
<!-- spd:decision-drivers -->

<!-- spd:options repeat="many" -->
**Considered Options**:

### Option 1: Keep Current Structure

Maintain the existing structure with many separate workflow files and scattered requirements.

**Pros**: No migration needed
**Cons**: Growing complexity, difficult customization, maintenance burden

### Option 2: Template-Centric Architecture with Consolidated Workflows (SELECTED)

Make templates the foundation of everything. Each template type becomes a self-contained package with:
- The template file itself
- Type-specific generate workflow
- Type-specific validate workflow
- Content requirements (embedded or adjacent)
- Checklists

Consolidate main workflows to just 5:
- `spider.md` - Entrypoint and orchestrator
- `generate.md` - Universal artifact/code generation (dispatches to template-specific generate)
- `validate.md` - Universal validation (dispatches to template-specific validate)
- `adapter.md` - Adapter management
- `rules.md` - Rules management (templates, checklists, examples)

### Option 3: Full Monolithic Approach

Single generate workflow with all logic inline, single validate workflow with all logic inline.

**Pros**: Simple structure
**Cons**: Monolithic files become unmaintainable, no customization per type
<!-- spd:options -->

<!-- spd:decision-outcome -->
**Decision Outcome**:
Chosen option: **Template-Centric Architecture with Consolidated Workflows**, because it provides the best balance of simplicity at the orchestration level while enabling deep customization at the template level.

### What Changes

#### 1. Template Package Structure

Each template package will contain:

```
templates/
├── PRD/
│   ├── template.md              # The template itself
│   ├── workflows/
│   │   ├── generate.md          # Type-specific generation workflow
│   │   └── validate.md          # Type-specific validation workflow
│   ├── checklists/
│   │   └── checklist.md         # Pre/post-generation checklists
│   └── examples/
│       └── example.md           # Canonical example
├── DESIGN/
│   └── ...
├── ADR/
│   └── ...
├── DECOMPOSITION/
│   └── ...
└── FEATURE/
    └── ...
```

#### 2. Consolidated Main Workflows

Only 5 main workflows remain in `workflows/`:

| Workflow | Purpose |
|----------|---------|
| `spider.md` | Entrypoint - determines intent and dispatches to appropriate workflow |
| `generate.md` | Universal generation - asks for artifact type, system, format; dispatches to template-specific generate workflow |
| `validate.md` | Universal validation - determines artifact type from path/registry; dispatches to template-specific validate workflow |
| `adapter.md` | Adapter management - initialization, bootstrap, manual/auto configuration |
| `rules.md` | Rules management - create rules, add templates, validate rule configuration |

**`generate.md` and `validate.md`** are orchestrators that:
1. Resolve artifact type from user input or `artifacts.json`
2. Load the appropriate template package
3. Execute the template-specific workflow

**`rules.md`** enables rule management:
1. Create new rules (configuration in `artifacts.json`)
2. Add templates to existing rules (`{rule.path}/{KIND}.template.md`)
3. Create checklists for templates (`checklists/{KIND}.md`)
4. Validate rule configuration and template structure
5. Generate examples for templates

#### 3. Spider ID Versioning

Introduce version suffix to Spider IDs to enable content change detection:

**Format**: `spd-{system}-{type}-{name}[-v{N}]`

**Rules**:
- Version suffix is optional for backward compatibility
- When content of an ID block changes materially, increment the version
- References to an ID without version match any version (loose)
- References to an ID with version require exact match (strict)
- Validation can warn about version mismatches

**Example**:
```markdown
**ID**: `spd-myapp-req-auth-v2`
<!-- Content here has changed from v1 -->
```

#### 4. Requirements Restructuring

`requirements/` folder will contain only universal execution rules:

| File | Content |
|------|---------|
| `execution-protocol.md` | Core execution protocol for all workflows |
| `SDSL.md` | Spider DSL (SDSL) specification |

Content requirements (what goes into each artifact type) move to the template package.

#### 5. Rebranding

Spider is rebranded to **Framework for Documentation and Development**:
- Reflects broader scope beyond "features"
- Maintains the "Spider" acronym for continuity
- Better describes the platform's purpose
<!-- spd:decision-outcome -->

**Consequences**:
<!-- spd:list:consequences -->
- Positive: Better modularity - each template type is self-contained
- Positive: Easier customization - add/modify template packages without touching core
- Positive: Cleaner navigation - fewer main workflows, clearer dispatch
- Positive: Version tracking - detect stale cross-references
- Positive: Consistent structure - all template packages follow same pattern
- Negative: Migration effort - existing content and workflows need restructuring
- Negative: Learning curve - new structure requires documentation update
- Negative: Tooling updates - `spider` CLI needs updates for template package discovery
- Follow-up: Update `artifacts.json` schema to reference template packages
- Follow-up: Migrate existing templates to new package structure
- Follow-up: Update `spider` CLI for template package workflow dispatch
- Follow-up: Implement `rules.md` workflow for rule and template management
- Follow-up: Create migration guide for existing Spider users
- Follow-up: Document template marker syntax and semantics
<!-- spd:list:consequences -->

**Links**:
<!-- spd:list:links -->
- Related Actors: `spd-spider-actor-technical-lead`, `spd-spider-actor-ai-assistant`, `spd-spider-actor-architect`
- Related Capabilities: `spd-spider-fr-workflow-execution`, `spd-spider-fr-validation`, `spd-spider-fr-adapter-config`, `spd-spider-fr-artifact-templates`, `spd-spider-fr-brownfield-support`
- Related Principles: `spd-spider-principle-adapter-variability-boundary`, `spd-spider-principle-tech-agnostic`, `spd-spider-principle-machine-readable`, `spd-spider-principle-traceability`
- Related ADRs: ADR-0001 (Initial Spider Architecture), ADR-0002 (Adaptive Spider)
<!-- spd:list:links -->
<!-- spd:##:body -->
<!-- spd:id:adr -->

<!-- spd:#:adr -->
