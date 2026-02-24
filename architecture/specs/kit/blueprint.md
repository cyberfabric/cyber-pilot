---
cypilot: true
type: spec
name: Blueprint Specification
version: 1.0
purpose: Define blueprint format, marker syntax, marker reference, placeholder syntax, parsing algorithm, update model, validation rules, and examples
drivers:
  - cpt-cypilot-fr-core-blueprint
  - cpt-cypilot-component-blueprint-processor
---

# Blueprint Specification

---

## Table of Contents

- [Blueprint Specification](#blueprint-specification)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Blueprint File Structure](#blueprint-file-structure)
  - [Marker Syntax](#marker-syntax)
    - [General Rules](#general-rules)
    - [Content Blocks](#content-blocks)
    - [Marker Summary](#marker-summary)
    - [Kit-Registered Markers (p2)](#kit-registered-markers-p2)
  - [Marker Reference](#marker-reference)
    - [cpt:blueprint](#cptblueprint)
    - [cpt:skill](#cptskill)
    - [cpt:system-prompt](#cptsystem-prompt)
    - [cpt:workflow](#cptworkflow)
    - [cpt:rules](#cptrules)
    - [cpt:rule](#cptrule)
    - [cpt:checklist](#cptchecklist)
    - [cpt:check](#cptcheck)
    - [cpt:heading](#cptheading)
    - [cpt:id](#cptid)
    - [cpt:prompt](#cptprompt)
    - [cpt:example](#cptexample)
  - [Placeholder Syntax](#placeholder-syntax)
    - [Placeholder Format](#placeholder-format)
    - [Pattern Validation](#pattern-validation)
    - [Example Derivation](#example-derivation)
    - [Template Derivation](#template-derivation)
  - [Generated Outputs Summary](#generated-outputs-summary)
  - [Parsing Algorithm](#parsing-algorithm)
  - [Update Model](#update-model)
    - [Reference Principle](#reference-principle)
    - [Initial Installation](#initial-installation)
    - [Update Modes](#update-modes)
      - [Force Update](#force-update)
      - [Additive Update (default)](#additive-update-default)
    - [Conflict Resolution](#conflict-resolution)
  - [Blueprint Examples](#blueprint-examples)
  - [Error Handling](#error-handling)
  - [Blueprint Validation Rules](#blueprint-validation-rules)

---

## Overview

An **Artifact Blueprint** is a single-source-of-truth Markdown file per artifact kind from which all kit resources are generated. The blueprint IS the template — a standard Markdown document enriched with inline `@cpt:` markers that carry structured metadata in fenced TOML blocks and content in fenced Markdown blocks.

Blueprints with an `artifact` key in `@cpt:blueprint` define artifact kinds (e.g., PRD, DESIGN). Blueprints without an `artifact` key define codebase-level resources (rules, checklists for code).

**Blueprint properties**:
- One `<KIND>.md` file per artifact kind per kit
- No YAML frontmatter — all metadata lives in `@cpt:` marker TOML blocks
- `` `@cpt:type` `` / `` `@/cpt:type` `` backtick-delimited markers for all annotations
- Each marker contains zero or more fenced code blocks (` ```toml ` for config, ` ```markdown ` for content)
- Both humans and machines can read and edit the blueprint naturally

**File location**:
- Source: `kits/<kit-slug>/blueprints/<KIND>.md`
- Installed (user-editable): `config/kits/<slug>/blueprints/<KIND>.md`

**Generated outputs** (see individual specs for format details):

| Output | Location | Spec |
|--------|----------|------|
| `rules.md` | `config/kits/<slug>/artifacts/<KIND>/` | [rules.md](rules.md) |
| `checklist.md` | `config/kits/<slug>/artifacts/<KIND>/` | [checklist.md](checklist.md) |
| `template.md` | `config/kits/<slug>/artifacts/<KIND>/` | [template.md](template.md) |
| `example.md` | `config/kits/<slug>/artifacts/<KIND>/` | [example.md](example.md) |
| `constraints.toml` | `config/kits/<slug>/` (kit-wide) | [constraints.md](constraints.md) |
| codebase `rules.md` | `config/kits/<slug>/codebase/` | [rules.md](rules.md) |
| codebase `checklist.md` | `config/kits/<slug>/codebase/` | [checklist.md](checklist.md) |

---

## Blueprint File Structure

A blueprint file is a sequence of `@cpt:` marker blocks. There is **no YAML frontmatter**. The file layout follows this order:

1. **`@cpt:blueprint`** — identity and metadata (required, exactly once, first marker)
2. **`@cpt:skill`** — SKILL.md extension content (optional)
3. **`@cpt:system-prompt`** — concise agent directives (optional)
4. **`@cpt:workflow` blocks** — workflow definitions generating kit workflow files + agent entry points (zero or more)
5. **`@cpt:rules`** — rules.md structure definition (optional)
6. **`@cpt:rule` blocks** — individual rule entries grouped by kind/section
7. **`@cpt:checklist`** — checklist.md structure definition (optional)
8. **`@cpt:check` blocks** — individual checklist items grouped by domain/kind
9. **`@cpt:heading` blocks** — heading constraint definitions
10. **`@cpt:id` blocks** — ID kind definitions with cross-artifact references
11. **`@cpt:prompt` blocks** — writing instructions placed under headings in template.md
12. **`@cpt:example` blocks** — concrete example content for sections

See [examples/blueprint-structure.md](examples/blueprint-structure.md) for a complete file layout showing all marker types.

---

## Marker Syntax

### General Rules

1. **Opening tag**: `` `@cpt:type` `` — backtick-delimited, must be the entire line
2. **Closing tag**: `` `@/cpt:type` `` — backtick-delimited, must be the entire line
3. **Content** between tags consists of zero or more **fenced code blocks** (` ```toml `, ` ```markdown `). Fences may use 3 or more backticks (e.g., ```````` for content that itself contains ``` fences)
4. **No inline attributes** — all configuration lives in fenced ` ```toml ` blocks
5. **No bare content** inside `@cpt:` blocks outside fenced code blocks
6. Markers MUST NOT be nested
7. All markers are **visible** in rendered Markdown (rendered as inline code + fenced blocks)
8. **Free text outside markers is ignored** — any content outside `@cpt:` blocks is not processed and can be used as comments, documentation, or human-readable descriptions of the blueprint. This allows blueprints to be self-documenting files.

### Content Blocks

Each marker may contain two types of fenced code blocks:

| Block type | Purpose | Format |
|------------|---------|--------|
| ` ```toml ` | Structured configuration (TOML) | Key-value pairs, tables, arrays |
| ` ```markdown ` | Content (rules, checks, examples, prompts) | Strict task lists, prose, etc. |

**Extended fences**: content blocks may use 4 or more backticks (```````` , `` ````` ``, etc.) when the content itself contains standard ``` fences. The processor matches the closing fence to the opening fence by backtick count (standard CommonMark behavior). This is especially useful for `@cpt:example` blocks where example content contains code fences.

**Ordering**: when both are present, the TOML block comes first, then the Markdown block.

### Marker Summary

| Marker | Content Blocks | Owner | Description | Generates |
|--------|---------------|-------|-------------|-----------|
| `@cpt:blueprint` | toml | core | Blueprint identity and metadata | — |
| `@cpt:skill` | markdown | core | SKILL.md extension content | → SKILL.md |
| `@cpt:system-prompt` | markdown | core | Agent directives (ALWAYS/WHEN) | → AGENTS.md |
| `@cpt:workflow` | toml + markdown | core | Workflow definition | → `workflows/{name}.md` + agent entry points |
| `@cpt:rules` | toml | core | rules.md structure skeleton | → rules.md |
| `@cpt:rule` | toml + markdown | core | Individual rule entry | → rules.md |
| `@cpt:checklist` | toml | core | checklist.md structure skeleton | → checklist.md |
| `@cpt:check` | toml + markdown | core | Individual checklist item | → checklist.md |
| `@cpt:heading` | toml | core | Heading constraint definition | → template.md + kit-wide constraints.toml |
| `@cpt:id` | toml | core | ID kind definition with refs | → kit-wide constraints.toml |
| `@cpt:prompt` | markdown | core | Writing instruction for section (placed under heading in template) | → template.md |
| `@cpt:example` | markdown | core | Example content for section | → example.md |

### Kit-Registered Markers (p2)

Kits register custom markers with the Blueprint Processor at load time. The core does not know about kit-specific markers — it delegates parsing and generation to the kit's registered handlers.

---

## Marker Reference

### cpt:blueprint

**Type**: block (required, exactly once, must be the first marker)

Contains a single ` ```toml ` block with blueprint identity.

````markdown
`@cpt:blueprint`
```toml
version = 1
kit = "sdlc"
artifact = "PRD"
description = "Product Requirements Document — actors, problems, FR/NFR, use cases, success criteria"
codebase = false
```
`@/cpt:blueprint`
````

| TOML Key | Required | Description |
|----------|----------|-------------|
| `version` | yes | Blueprint schema version (integer) |
| `kit` | yes | Kit slug that owns this blueprint |
| `artifact` | no | Artifact kind (e.g., PRD, DESIGN, ADR). When omitted, the blueprint is not associated with any artifact kind |
| `description` | no | Human-readable description of the artifact kind or codebase concern. Used in `taxonomy.md` generation and SKILL.md listings |
| `codebase` | no | Whether this blueprint relates to a codebase (`true`/`false`, default `false`) |

---

### cpt:skill

**Type**: block (optional, at most one per file)

Contains a single ` ```markdown ` block with SKILL.md extension content.

````markdown
`@cpt:skill`
```markdown
### PRD Commands
- `cypilot validate --artifact <PRD.md>` — validate PRD
### PRD Workflows
- **Generate PRD**: create a new PRD from template with guided prompts
- **Analyze PRD**: validate structure then semantic quality
```
`@/cpt:skill`
````

Content is collected by the core and composed into the main SKILL.md during agent entry point generation (`cypilot agents`). This ensures AI agents discover kit capabilities automatically.

---

### cpt:system-prompt

**Type**: block (optional, at most one per file)

Contains a single ` ```markdown ` block with concise agent directives. Should contain 1–5 `ALWAYS ... WHEN ...` rules.

````markdown
`@cpt:system-prompt`
```markdown
ALWAYS load `{cypilot_path}/specs/traceability.md` BEFORE generating or validating a PRD
ALWAYS describe WHAT the system does, NEVER HOW — implementation details belong in DESIGN
ALWAYS use observable behavior language (MUST/MUST NOT/SHOULD) WHEN writing functional requirements
```
`@/cpt:system-prompt`
````

Content is loaded by generate and analyze workflows when processing this artifact kind. Provides additional agent context without manual prompt management.

---

### cpt:workflow

**Type**: block (zero or more per file)

Contains a ` ```toml ` header block and a ` ```markdown ` content block defining a workflow that agents can execute. The Blueprint Processor generates a workflow `.md` file in the kit's `workflows/` directory; `cypilot agents` then creates agent entry points (e.g., `.windsurf/workflows/`) that reference these generated files.

````markdown
`@cpt:workflow`
```toml
name = "pr-review"
description = "Review a GitHub PR against configurable checklists and prompts"
```
```markdown
## Prerequisites
- `gh` CLI authenticated
- PR number provided by user

## Steps
1. Fetch PR diff and metadata via `gh`
2. Load review prompt and checklist from kit config
3. Analyze changes against checklist criteria
4. Analyze existing reviewer comments
5. Write structured review report to `.prs/{ID}/review.md`
```
`@/cpt:workflow`
````

| TOML Key | Required | Description |
|----------|----------|-------------|
| `name` | yes | Workflow slug (used as filename: `{name}.md`) |
| `description` | yes | Human-readable description of what the workflow does |

**Multiple workflows per blueprint**: a single blueprint may register several workflows (e.g., generate, validate, review for the same artifact kind).

**Generates**: two outputs per workflow:

1. **Kit workflow file**: `config/kits/<slug>/workflows/{name}.md` — the full workflow definition assembled from the ` ```markdown ` content block, with frontmatter metadata.
2. **Agent entry points**: during `cypilot agents`, each workflow gets an entry point in every agent's native format that references the kit workflow file:
   - Windsurf: `.windsurf/workflows/cypilot-{name}.md`
   - Cursor: `.cursor/rules/cypilot-{name}.md`
   - Claude: `.claude/commands/cypilot-{name}.md`
   - Copilot: `.github/prompts/cypilot-{name}.md`

**Generated kit workflow file** (`config/kits/sdlc/workflows/pr-review.md`):
```markdown
---
name: pr-review
kit: sdlc
description: Review a GitHub PR against configurable checklists and prompts
---

## Prerequisites
- `gh` CLI authenticated
- PR number provided by user

## Steps
1. Fetch PR diff and metadata via `gh`
...
```

**Generated agent entry point** (`.windsurf/workflows/cypilot-pr-review.md`):
```markdown
---
name: Cypilot PR Review
description: Review a GitHub PR against configurable checklists and prompts
---

Follow the workflow defined in `{cypilot_path}/config/kits/sdlc/workflows/pr-review.md`
```

Agent entry points are fully overwritten on every `cypilot agents` run. Kit workflow files are regenerated from blueprints on `cypilot generate-resources`.

---

### cpt:rules

**Type**: block (optional, at most one per file)

Contains a single ` ```toml ` block defining the structure skeleton for `rules.md`. Each top-level TOML table defines a section kind; the value lists sub-sections or phases.

````markdown
`@cpt:rules`
```toml
[prerequisites]
sections = ["load_dependencies"]

[requirements]
sections = ["structural", "versioning", "semantic", "traceability", "constraints"]

[tasks]
phases = ["setup", "content_creation", "ids_and_structure", "quality_check"]

[validation]
sections = ["structural", "semantic"]

[error_handling]
sections = ["missing_dependencies", "missing_adapter", "escalation"]

[next_steps]
sections = ["options"]
```
`@/cpt:rules`
````

| TOML Table | Description |
|------------|-------------|
| `[prerequisites]` | What must be loaded/checked before starting |
| `[requirements]` | Structural and semantic rules grouped by topic |
| `[tasks]` | Step-by-step phases for artifact creation |
| `[validation]` | How to validate the generated artifact |
| `[error_handling]` | What to do when things go wrong |
| `[next_steps]` | Available actions after completion |

Individual rule entries are defined in separate `@cpt:rule` blocks. Their order within each `kind`/`section` determines the order in the generated `rules.md`.

See [rules.md spec](rules.md) for the full format of the generated file.

---

### cpt:rule

**Type**: block (zero or more per file)

Contains a ` ```toml ` header block (with `kind` and `section`) followed by a ` ```markdown ` block with **strict task-list** content.

````markdown
`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
- [ ] Purpose MUST be ≤ 2 paragraphs
- [ ] Purpose MUST NOT contain implementation details
- [ ] Vision MUST explain WHY the product exists
  - VALID: "Enables developers to validate artifacts" (explains purpose)
  - INVALID: "A tool for Cypilot" (doesn't explain why it matters)
```
`@/cpt:rule`
````

| TOML Key | Required | Description |
|----------|----------|-------------|
| `kind` | yes | Section kind from `@cpt:rules` (prerequisites, requirements, tasks, validation, error_handling, next_steps) |
| `section` | yes | Sub-section within the kind (must match a value in the `@cpt:rules` definition) |

**Content format**: strictly task lists (`- [ ] ...`). May include `VALID`/`INVALID` labels as sub-items for semantic rules.

**Placement**: global rules go before `@cpt:heading` markers; section-scoped rules go after the relevant `@cpt:heading`.

**Generates**: entries in `rules.md`, ordered by kind → section → definition order.

---

### cpt:checklist

**Type**: block (optional, at most one per file)

Contains a single ` ```toml ` block defining the structure skeleton for `checklist.md`: severity levels, review priority, and expertise domains.

````markdown
`@cpt:checklist`
```toml
[severity]
levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
# CRITICAL — blocks downstream work
# HIGH     — fix before approval
# MEDIUM   — fix when feasible
# LOW      — optional improvement

[review]
priority = ["BIZ", "ARCH", "SEC", "TEST"]

# Domain order defines section sequence in generated checklist.md
[[domain]]
abbr = "BIZ"
name = "Business"
standards = ["ISO/IEC/IEEE 29148:2018 §6.2 (StRS), §6.4 (SRS)"]

[[domain]]
abbr = "ARCH"
name = "Architecture"
standards = ["ISO/IEC 25010:2023 §4.2.7–8", "ISO/IEC/IEEE 29148 §6.3"]
```
`@/cpt:checklist`
````

| TOML Table/Key | Description |
|----------------|-------------|
| `[severity].levels` | Severity levels in descending order |
| `[review].priority` | Recommended domain review order |
| `[[domain]]` | Array of expertise domains (order = section sequence) |
| `[[domain]].abbr` | Domain abbreviation (referenced by `@cpt:check` blocks) |
| `[[domain]].name` | Full domain name |
| `[[domain]].standards` | Referenced standards for the domain header |

Individual check items are defined in separate `@cpt:check` blocks.

See [checklist.md spec](checklist.md) for the full format of the generated file.

---

### cpt:check

**Type**: block (zero or more per file)

Contains a ` ```toml ` header block followed by a ` ```markdown ` block with task-list check items.

````markdown
`@cpt:check`
```toml
id = "BIZ-PRD-001"
domain = "BIZ"
title = "Vision Clarity"
severity = "CRITICAL"
ref = "ISO/IEC/IEEE 29148 §5.2.5"
kind = "must_have"
# applicable_when = "..."       # omit = always applicable
# not_applicable_when = "..."   # omit = always applicable
```
```markdown
- [ ] Purpose statement explains WHY the product exists
- [ ] Target users clearly identified with specificity (not just "users")
- [ ] Key problems solved are concrete and measurable
```
`@/cpt:check`
````

For `must_not_have` items:

````markdown
`@cpt:check`
```toml
id = "ARCH-PRD-NO-001"
domain = "ARCH"
title = "No Technical Implementation Details"
severity = "CRITICAL"
kind = "must_not_have"
belongs_to = "DESIGN"
```
```markdown
- [ ] No database schema definitions
- [ ] No API endpoint specifications
- [ ] No technology stack decisions
```
`@/cpt:check`
````

| TOML Key | Required | Description |
|----------|----------|-------------|
| `id` | yes | Unique check ID (`{DOMAIN}-{ARTIFACT}-{NNN}` or `{DOMAIN}-{ARTIFACT}-NO-{NNN}`) |
| `domain` | yes | Domain abbreviation (must match a `[[domain]].abbr` in `@cpt:checklist`) |
| `title` | yes | Human-readable check title |
| `severity` | yes | `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW` |
| `kind` | yes | `must_have` or `must_not_have` |
| `ref` | no | Standard/specification reference |
| `applicable_when` | no | When this check applies (omit = always) |
| `not_applicable_when` | no | When this check does not apply (omit = always) |
| `belongs_to` | no | For `must_not_have`: where the content belongs instead |

**Generates**: entries in `checklist.md`, organized by domain and kind.

---

### cpt:heading

**Type**: block (zero or more)

Contains a single ` ```toml ` block defining heading constraints. No content between tags — heading text is defined via the `examples` and `template` TOML keys.

````markdown
`@cpt:heading`
```toml
id = "prd-overview-purpose"
level = 3
required = true
numbered = true
multiple = false
pattern = "Purpose"
description = "What the product is and what problem it solves."
template = "Purpose"
examples = ["### 1.1 Purpose"]
```
`@/cpt:heading`
````

Heading with placeholder:

````markdown
`@cpt:heading`
```toml
id = "prd-h1-title"
level = 1
required = true
template = "PRD — {Title of product}"
examples = ["# PRD — Overwork Alert"]
```
`@/cpt:heading`
````

The text inside `{...}` in the `template` key serves as the prompt — it tells the author what to fill in. No separate `prompt` key is needed.

| TOML Key | Required | Default | Description |
|----------|----------|---------|-------------|
| `id` | yes | — | Unique heading identifier within the blueprint |
| `level` | yes | — | Heading level (1–6) |
| `required` | no | `true` | Whether this heading must be present |
| `numbered` | no | `true` | Whether heading has a numbered prefix (e.g., "1.1") |
| `multiple` | no | (omit) | `true` = required multiple, `false` = prohibited, omit = allowed |
| `pattern` | no | — | Regex to match heading text. If omitted, heading text is not validated by regex |
| `description` | no | — | Human-readable description of the section |
| `template` | no | — | Heading text template with `{prompt}` placeholders — the text inside `{...}` serves as the writing prompt |
| `examples` | no | — | Array of concrete heading examples |

**Generates**: entries in kit-wide `constraints.toml` → `[[artifacts.<KIND>.headings]]` array. See [constraints.md spec](constraints.md).

---

### cpt:id

**Type**: block (zero or more)

Contains a single ` ```toml ` block defining an ID kind and its cross-artifact reference rules. Uses `[ref.ARTIFACT]` sub-tables for references.

**Placement**: after the `@cpt:heading` where this ID kind is defined (e.g., `@cpt:id` for actors goes after the Actors heading).

````markdown
`@cpt:id`
```toml
kind = "fr"
name = "Functional Requirement"
description = "Describes observable system behavior"
required = true
# task = true|false      # optional by default
priority = true           # true = required | false = prohibited
template = "cpt-{system}-fr-{slug}"
examples = ["cpt-cypilot-fr-validation", "cpt-ex-ovwa-fr-track-active-time"]
to_code = false
headings = ["prd-fr"]

[ref.DESIGN]
coverage = true
headings = ["design-arch-overview-drivers"]

[ref.DECOMPOSITION]
# coverage = true|false  # optional by default
headings = ["decomposition-entry"]

[ref.FEATURE]
# coverage = true|false  # optional by default
headings = ["feature-context-purpose"]
```
`@/cpt:id`
````

**Top-level TOML keys**:

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `kind` | yes | — | ID kind slug (e.g., `fr`, `actor`, `nfr`, `usecase`) |
| `name` | no | — | Human-readable name |
| `description` | no | — | What this ID kind represents |
| `required` | no | `true` | Whether at least one ID of this kind must exist |
| `task` | no | (omit) | `true` = required, `false` = prohibited, omit = optional |
| `priority` | no | (omit) | `true` = required, `false` = prohibited, omit = optional |
| `template` | yes | — | ID template pattern (e.g., `cpt-{system}-fr-{slug}`) |
| `examples` | no | — | Array of example IDs |
| `to_code` | no | `false` | Whether IDs trace to `@cpt-*` code markers |
| `headings` | no | — | Array of heading IDs where this kind can be defined |

**Boolean convention**: `true` = required, `false` = prohibited, omit = optional/allowed. Use TOML comments for clarity:
```toml
# task = true|false    # optional by default
priority = true        # true = required | false = prohibited
```

**`[ref.ARTIFACT]` sub-tables**:

| Key | Description |
|-----|-------------|
| `coverage` | `true` = required, `false` = prohibited, omit = optional |
| `headings` | Array of heading IDs in the referenced artifact where this ID appears |

**Generates**: entries in kit-wide `constraints.toml` → `[artifacts.<KIND>.identifiers]` object with full reference rules. See [constraints.md spec](constraints.md).

---

### cpt:prompt

**Type**: block (zero or more)

Contains a single ` ```markdown ` block with a writing instruction for the nearest preceding `@cpt:heading`. The content is placed under the heading in the generated `template.md` to guide the author on what to write in that section.

````markdown
`@cpt:prompt`
```markdown
Write 1-2 paragraphs: what is this system/module and what problem does it solve.
Reference the system name from adapter config.
Do NOT include implementation details.
```
`@/cpt:prompt`
````

**Placement**: after the `@cpt:heading` it applies to, before any `@cpt:rule`, `@cpt:example`, or next `@cpt:heading`.

**Generates**: prompt text under the corresponding heading in `template.md`.

---

### cpt:example

**Type**: block (zero or more)

Contains a ` ```markdown ` (or ` ````markdown `) block with concrete example content for the nearest preceding `@cpt:heading`. Use 4+ backtick fences when the example content itself contains ``` code fences.

Plain example:

````markdown
`@cpt:example`
```markdown
Overwork Alert is a system that monitors employee work hours across the organization
and sends automated alerts when individuals exceed configurable thresholds. The system
integrates with existing time tracking tools and provides dashboards for management.
```
`@/cpt:example`
````

Example with code fences inside (uses ```````` ):

`````markdown
`@cpt:example`
````markdown
Here is a sample config file:

```toml
[server]
port = 8080
```
````
`@/cpt:example`
`````

**Placement**: after the section's `@cpt:prompt` and `@cpt:rule` markers. Associates with the nearest preceding `@cpt:heading`.

**Generates**: sections in `example.md`, composed in heading order. See [example.md spec](example.md).

---

## Placeholder Syntax

Blueprints use **placeholders** in `@cpt:heading` TOML `template` keys and in `@cpt:example` content to mark variable parts.

### Placeholder Format

```
{descriptive text}
```

The text inside `{...}` serves as the **prompt** — it tells the author what to fill in. No separate `prompt` key is needed.

Used in `template` keys inside `@cpt:heading` TOML blocks:
```toml
template = "PRD — {Title of product}"
examples = ["# PRD — TaskFlow", "# PRD — Overwork Alert"]
```

Here `{Title of product}` is both the placeholder marker AND the writing guidance.

### Pattern Validation

The `pattern` key on `@cpt:heading` is an optional regex used for heading text validation. If omitted, the heading text is not validated by regex.

```toml
pattern = "PRD\\s*[—–-]\\s*.+"
```

### Example Derivation

`example.md` is generated by:

1. **Headings**: use the first entry from the `examples` array in the `@cpt:heading` TOML
2. **Body content**: use `@cpt:example` ` ```markdown ` block content for each section
3. **Sections without `@cpt:example`**: omit

**Example**:
```
@cpt:heading examples = ["# PRD — TaskFlow"]  →  example.md: # PRD — TaskFlow
@cpt:example content                          →  example.md: (content verbatim)
```

### Template Derivation

`template.md` is generated by:

1. Walk all `@cpt:heading` blocks in order
2. For each heading, emit a Markdown heading at the declared `level` using the `template` key text
3. For each `@cpt:prompt` following a heading, emit the prompt content under the heading as a writing instruction
4. Strip all other marker tags and metadata content (`@cpt:rule`, `@cpt:example`, `@cpt:id`)
5. Result is a template with headings and writing instructions

**Example**:
```
@cpt:heading template = "PRD — {Title of product}"  level = 1  →  # PRD — {Title of product}
@cpt:heading template = "Purpose"                    level = 3  →  ### Purpose
@cpt:prompt "Write 1-2 paragraphs..."                            →  Write 1-2 paragraphs...
```

---

## Generated Outputs Summary

The Blueprint Processor parses all markers and invokes output generators. All outputs are core-defined — kits do not define custom output generators in p1.

| Output File | Source Markers | Description |
|------------|---------------|-------------|
| `rules.md` | `@cpt:rules` + `@cpt:rule` | Structured rules document (prerequisites → requirements → tasks → validation → error handling → next steps) |
| `checklist.md` | `@cpt:checklist` + `@cpt:check` | Quality checklist organized by expertise domain (MUST HAVE + MUST NOT HAVE) |
| `template.md` | `@cpt:heading` + `@cpt:prompt` | Heading structure with `{placeholder}` variables and writing instructions |
| `constraints.toml` | `@cpt:heading` + `@cpt:id` | Kit-wide structural constraints with patterns and ID reference rules (aggregated from all artifact blueprints) |
| `example.md` | `@cpt:heading` (examples) + `@cpt:example` | Concrete example artifact assembled from heading examples and example blocks |

**Determinism guarantee**: same blueprint content → identical output files (byte-for-byte). The processor sorts, formats, and serializes deterministically.

---

## Parsing Algorithm

1. Read the blueprint file as UTF-8 text.
2. Scan for lines matching `` `@cpt:TYPE` `` (opening) or `` `@/cpt:TYPE` `` (closing).
3. For each opening tag:
   a. Extract the marker type (word after `@cpt:`).
   b. Collect all fenced code blocks between the opening and closing tags.
   c. Parse ` ```toml ` blocks as TOML configuration.
   d. Collect ` ```markdown ` blocks as content.
4. Validate:
   a. `@cpt:blueprint` must be present and be the first marker.
   b. Every opening tag must have a matching closing tag.
   c. No nested markers.
   d. All marker types must be registered (core or kit).
   e. TOML blocks must parse without errors.
   f. Required TOML keys must be present for each marker type.
5. Group markers by type.
6. Invoke output generators.

**Template extraction** (for template.md):
1. Walk all `@cpt:heading` blocks in order.
2. For each heading: emit Markdown heading at declared `level` using `template` text.
3. For each `@cpt:prompt` following a heading: emit prompt content as writing instruction.
4. Collapse resulting blank lines (max 2 consecutive).
5. Result is `template.md`.

---

## Update Model

### Reference Principle

The **installed kit** in `{cypilot}/kits/{slug}/` serves as the reference for all update operations. When a kit is installed, its source is saved to `{cypilot}/kits/{slug}/` — this is the reference copy. User-editable blueprints live in `config/kits/{slug}/blueprints/`.

### Initial Installation

When a kit is installed (`cypilot init` or `cypilot kit install`):

1. The tool saves the kit source to `{cypilot}/kits/{slug}/` (reference copy).
2. Blueprints are copied from `{cypilot}/kits/{slug}/blueprints/` to `config/kits/{slug}/blueprints/` (user-editable).
3. All output files are generated from the user blueprints.
4. The kit version is recorded in `config/core.toml`.

### Update Modes

#### Force Update

**Command**: `cypilot kit update --force`

Overwrites all user blueprints from the reference and regenerates all outputs. User edits are discarded.

1. Update `{cypilot}/kits/{slug}/` with new kit version.
2. Copy all blueprints from `{cypilot}/kits/{slug}/blueprints/` → `config/kits/{slug}/blueprints/` (overwrite).
3. Regenerate all outputs.
4. Update kit version in `config/core.toml`.

Use when: starting fresh, after breaking edits, or when you want to fully sync with the upstream kit.

#### Additive Update (default)

**Command**: `cypilot kit update`

Three-way diff using the **current reference** in `{cypilot}/kits/{slug}/` as the base:

```
{cypilot}/kits/{slug}/ (current)  ── the reference
    ↕ diff A: detect user modifications
config/kits/{slug}/blueprints/    ── user’s version

{cypilot}/kits/{slug}/ (current)  ── the reference
    ↕ diff B: detect kit upstream changes
new kit version                   ── the updated upstream
```

The reference is always available in `{cypilot}/kits/{slug}/`. After a successful merge, the reference is replaced with the new version.

**Merge rules**:

| Condition | Action |
|-----------|--------|
| Section unchanged by user (current == previous source) | Update to new version |
| Section modified by user (current ≠ previous source) | **Preserve** user version |
| New marker in new version (not in previous source) | **Insert** into blueprint |
| Marker deleted by user (in previous source, not in current) | **Respect** deletion — do not re-add |
| Both user and kit modified same section | **Conflict** — flag for manual resolution |

### Conflict Resolution

When conflicts are detected during additive update:

1. The tool writes a `<KIND>.md.conflicts` file listing all conflicts with both versions.
2. The tool outputs a warning with conflict count and file path.
3. The user resolves conflicts manually in the blueprint file.
4. Running `cypilot generate-resources` regenerates outputs from the resolved blueprint.

---

## Blueprint Examples

- [Minimal Blueprint](examples/blueprint-minimal.md) — MEMO artifact with one heading, shows minimal required structure
- [PRD Blueprint (SDLC Kit)](examples/blueprint-prd.md) — full PRD blueprint with skills, workflows, rules, checklist, and template markers

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `BLUEPRINT_NOT_FOUND` | No `<KIND>.md` in `config/kits/<slug>/blueprints/` | Create blueprint or check kit installation |
| `BLUEPRINT_NO_HEADER` | Missing `@cpt:blueprint` marker | Add `` `@cpt:blueprint` `` with TOML block as first marker |
| `BLUEPRINT_UNKNOWN_MARKER` | Marker type not registered by core or any kit | Check marker spelling, ensure kit is installed |
| `BLUEPRINT_UNCLOSED_BLOCK` | Block marker without matching close tag | Add `` `@/cpt:type` `` closing tag |
| `BLUEPRINT_NESTED_BLOCKS` | Block marker inside another block | Restructure to avoid nesting |
| `BLUEPRINT_TOML_PARSE_ERROR` | Invalid TOML in a ` ```toml ` block | Fix TOML syntax |
| `BLUEPRINT_MISSING_KEY` | Required TOML key missing (e.g., `id` on `@cpt:heading`) | Add the required key |
| `BLUEPRINT_DUPLICATE_HEADING_ID` | Two `@cpt:heading` markers with same `id` | Use unique IDs |
| `BLUEPRINT_DUPLICATE_CHECK_ID` | Two `@cpt:check` markers with same `id` | Use unique IDs |
| `BLUEPRINT_DUPLICATE_WORKFLOW` | Two `@cpt:workflow` markers with same `name` across all blueprints | Use unique workflow names |
| `BLUEPRINT_UPDATE_CONFLICT` | Both user and kit modified the same section during additive update | Resolve conflicts in `<KIND>.md.conflicts`, then run `cypilot generate-resources` |

---

## Blueprint Validation Rules

The Blueprint Processor validates blueprints before generation:

1. **Structure**: `@cpt:blueprint` marker present and is the first marker.
2. **Completeness**: every `` `@cpt:type` `` has a matching `` `@/cpt:type` ``.
3. **No nesting**: no markers inside other markers.
4. **Known markers**: all marker types are registered (core or kit).
5. **TOML validity**: all ` ```toml ` blocks parse without errors.
6. **Required keys**: required TOML keys present for each marker type (e.g., `id`, `level` for headings).
7. **Boolean convention**: `task`, `priority`, `coverage`, `multiple` use `true`/`false` or are omitted (no string values).
8. **Unique IDs**: heading IDs (`@cpt:heading.id`) and check IDs (`@cpt:check.id`) are unique within the blueprint.
9. **Domain references**: `@cpt:check.domain` must match a `[[domain]].abbr` defined in `@cpt:checklist`.
10. **Rule references**: `@cpt:rule.kind` and `@cpt:rule.section` must match entries in `@cpt:rules`.
11. **Workflow uniqueness**: `@cpt:workflow.name` values are unique across all blueprints in all installed kits.
12. **Version compatibility**: blueprint version is supported by the current processor.

Validation runs automatically before generation. Errors abort generation with actionable messages.
