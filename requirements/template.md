---
spider: true
type: requirement
name: Spider Template Specification
version: 1.1
purpose: Define marker-based template syntax for Spider artifacts
---

# Spider Template Specification

## Table of Contents

- [Spider Template Specification](#spider-template-specification)
  - [Table of Contents](#table-of-contents)
  - [Quick Reference](#quick-reference)
  - [Prerequisite Checklist](#prerequisite-checklist)
  - [Overview](#overview)
  - [Template Frontmatter](#template-frontmatter)
    - [Fields](#fields)
  - [Marker Syntax](#marker-syntax)
    - [Basic Structure](#basic-structure)
    - [Marker Types](#marker-types)
    - [Marker Attributes](#marker-attributes)
  - [ID Formats](#id-formats)
    - [ID Definition (`id` block)](#id-definition-id-block)
    - [ID Reference (`id-ref` block)](#id-reference-id-ref-block)
    - [Inline ID Reference](#inline-id-reference)
    - [ID Naming Convention](#id-naming-convention)
  - [Spider DSL (SDSL) Format](#spider-dsl-sdsl-format)
    - [SDSL Line Format](#sdsl-line-format)
  - [Template Example](#template-example)
  - [Artifact Validation](#artifact-validation)
    - [Structure Validation](#structure-validation)
    - [Content Validation](#content-validation)
    - [Cross-Validation](#cross-validation)
  - [Error Types](#error-types)
    - [Error Format](#error-format)
  - [Agent Workflow](#agent-workflow)
    - [When to Use This Spec](#when-to-use-this-spec)
    - [Template Creation Workflow](#template-creation-workflow)
    - [Validation Workflow](#validation-workflow)
    - [Common Tasks](#common-tasks)
  - [Validation Checklist](#validation-checklist)
  - [References](#references)

---

## Quick Reference

**Marker syntax**:
```html
<!-- spd:TYPE:NAME ATTRS -->
content
<!-- spd:TYPE:NAME -->
```

**Common marker types**: `free`, `id`, `id-ref`, `list`, `table`, `paragraph`, `sdsl`, `#`-`######`

**ID format**: `` `spd-{hierarchy-prefix}-{kind}-{slug}` `` (see [ID Naming Convention](#id-naming-convention))

**Validate template**:
```bash
python3 {spider_path}/skills/spider/scripts/spider.py validate --artifact <path>
```

---

## Prerequisite Checklist

- [ ] Agent has identified the artifact being validated
- [ ] Agent understands template marker syntax
- [ ] Agent has access to the template file for the artifact kind

---

## Overview

Spider templates use paired HTML comment markers to define structural blocks in markdown documents. This enables deterministic validation of artifacts against their templates.

**Supported Version**: `1.0`

---

## Template Frontmatter

Templates MAY optionally begin with YAML frontmatter. If frontmatter is absent, the `kind` is inferred from the template path (`.../artifacts/{KIND}/template.md`).

```yaml
---
spider-template:
  version:
    major: 2
    minor: 0
  kind: <KIND>
  unknown_sections: warn
---
```

**NOTE**: Frontmatter is optional. When omitted:
- `kind` is inferred from path pattern `.../artifacts/{KIND}/template.md`
- `version` defaults to the current supported version (2.0)
- `unknown_sections` defaults to `warn`

Artifacts may optionally have their own `spd:` frontmatter for document metadata.

### Fields (when frontmatter is present)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version.major` | integer | NO | Major version (defaults to current) |
| `version.minor` | integer | NO | Minor version (defaults to current) |
| `kind` | string | NO | Artifact kind (inferred from path if absent) |
| `unknown_sections` | string | NO | How to handle markers not in template: `error`, `warn`, `allow`. Default: `warn` |

---

## Marker Syntax

### Basic Structure

```html
<!-- spd:TYPE:NAME ATTRS -->
content goes here
<!-- spd:TYPE:NAME -->
```

**Pattern**: `<!-- spd:(?:TYPE:)?NAME ATTRS -->`

- `TYPE` — block type (optional, defaults to `free`)
- `NAME` — unique identifier within the template
- `ATTRS` — space-separated `key="value"` pairs

### Marker Types

| Type | Description | Content Requirements |
|------|-------------|---------------------|
| `free` | Freeform content | Any content |
| `id` | ID definition block | Lines matching ID definition format |
| `id-ref` | ID reference block | Lines matching ID reference format |
| `list` | Bullet list | Lines starting with `- ` or `* ` |
| `numbered-list` | Numbered list | Lines starting with `1. `, `2)`, etc. |
| `task-list` | Task/checkbox list | Lines starting with `- [ ]` or `- [x]` |
| `table` | Markdown table | Header + separator + data rows |
| `paragraph` | Non-empty text | At least one non-empty line |
| `code` | Fenced code block | Must start with ``` and be closed |
| `#` - `######` | Heading (level 1-6) | First line must be heading of specified level |
| `link` | Markdown link | Must contain `[text](url)` |
| `image` | Markdown image | Must start with `!` |
| `sdsl` | SDSL instruction list | Lines matching SDSL format |

### Marker Attributes

| Attribute | Values | Default | Applies to | Description |
|-----------|--------|---------|------------|-------------|
| `required` | `"true"`, `"false"` | `"true"` | all | Block must be present in artifact |
| `repeat` | `"one"`, `"many"` | `"one"` | all | Block can appear multiple times |
| `covered_by` | `"KIND,KIND,..."` | - | `id` | IDs must be referenced by artifacts of these kinds |
| `has` | `"task"` | - | `id` | Enable task consistency: if all tasks `[x]` → ID must be `[x]` |
| `has` | `"priority"` | - | `id`, `id-ref`, `task-list` | Each item must have priority (`` `p1` ``-`` `p9` ``) |
| `to_code` | `"true"`, `"false"` | `"false"` | `id` | ID must be traced to code implementation |

**Note**: The `has` attribute controls **validation behavior**, not format support. Both `id` and `id-ref` blocks **always** support task checkboxes (`[ ]`/`[x]`) and priorities (`` `p1` ``-`` `p9` ``) in their format — see ID Formats section below.

---

## ID Formats

### ID Definition (`id` block)

```
**ID**: `spd-myapp-fr-must-authenticate`
- [ ] **ID**: `spd-myapp-actor-admin-user`
- [x] `p1` - **ID**: `spd-myapp-core-comp-api-gateway`
`p2` - **ID**: `spd-myapp-core-auth-flow-login`
```

**Pattern**:

```regex
^(?:\*\*ID\*\*:\s*`spd-[a-z0-9][a-z0-9-]+`|`p\d+`\s*-\s*\*\*ID\*\*:\s*`spd-[a-z0-9][a-z0-9-]+`|[-*]\s+\[\s*[xX]?\s*\]\s*(?:`p\d+`\s*-\s*)?\*\*ID\*\*:\s*`spd-[a-z0-9][a-z0-9-]+`)\s*$
```

Components:
- `**ID**:` — literal prefix (required)
- `- [ ]` or `- [x]` — optional task checkbox (task list item)
- `` `p1` `` - `` `p9` `` — optional priority
- `` `spd-{hierarchy-prefix}-{kind}-{slug}` `` — the ID in backticks (required)

### ID Reference (`id-ref` block)

```
`spd-myapp-fr-must-authenticate`
[ ] `spd-myapp-core-comp-api-gateway`
[x] `p1` - `spd-myapp-core-auth-flow-login`
```

**Pattern**:

```regex
^(?:(?:\[\s*[xX]?\s*\])\s*(?:`p\d+`\s*-\s*)?)?`spd-[a-z0-9][a-z0-9-]+`\s*$
```

### Inline ID Reference

Any `` `spd-xxx` `` in content is treated as a reference.

**Pattern**:

```regex
`(spd-[a-z0-9][a-z0-9-]+)`
```

### ID Naming Convention

IDs are built by concatenating **slugs** through the hierarchy chain (from `artifacts.json`), followed by the element kind and a descriptive slug.

```
spd-{hierarchy-prefix}-{kind}-{slug}
```

Where:
- `spd-` — literal prefix (required)
- `{hierarchy-prefix}` — concatenated slugs from system → subsystem → component (e.g., `myapp-core-auth`)
- `{kind}` — element kind in lowercase (actor, cap, fr, nfr, comp, flow, algo, state, req, etc.)
- `{slug}` — descriptive slug (lowercase, alphanumeric, hyphens)

**What is a slug?**

A **slug** is a machine-readable identifier derived from a human name. Slugs are URL-safe, lowercase strings used for stable references.

| Human Name | Slug |
|------------|------|
| "My Cool App" | `my-cool-app` |
| "User Authentication" | `user-auth` |
| "API Gateway v2" | `api-gateway-v2` |

**Slug rules**: lowercase letters, numbers, hyphens only. No spaces, no leading/trailing hyphens. Pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`

**Hierarchy Examples** (from `artifacts.json`):

| Hierarchy Level | ID Pattern | Example |
|-----------------|------------|---------|
| System | `spd-{system}-{kind}-{slug}` | `spd-saas-fr-user-auth` |
| Subsystem | `spd-{system}-{subsystem}-{kind}-{slug}` | `spd-saas-core-comp-api-gateway` |
| Component | `spd-{system}-{subsystem}-{component}-{kind}-{slug}` | `spd-saas-core-auth-flow-login` |

**Element Kind Examples**:
- `spd-myapp-actor-admin-user` — Actor at system level
- `spd-myapp-cap-user-management` — Capability at system level
- `spd-myapp-fr-must-authenticate` — Functional requirement
- `spd-myapp-core-comp-api-gateway` — Component at subsystem level
- `spd-myapp-core-auth-flow-login` — Flow at component level
- `spd-myapp-core-auth-algo-password-hash` — Algorithm at component level

---

## Spider DSL (SDSL) Format

Spider DSL (SDSL) is used in `sdsl` blocks to define step-by-step instructions with traceability.

### SDSL Line Format

```
N. [ ] - `pN` - Description - `inst-slug`
- [ ] - `pN` - Description - `inst-slug`
```

**Pattern**:

```regex
^\s*(?:\d+\.\s+|-\s+)\[\s*[xX ]\s*\]\s*-\s*`ph-\d+`\s*-\s*.+\s*-\s*`inst-[a-z0-9-]+`\s*$
```

Components:
- `N.` or `-` — list marker (numbered or bullet)
- `[ ]` or `[x]` — completion checkbox
- `` `pN` `` — phase number (e.g., `p1`, `p2`)
- `Description` — what this step does
- `` `inst-slug` `` — instruction ID for code traceability

**Example**:
```markdown
1. [ ] - `p1` - Load configuration from environment - `inst-load-config`
2. [ ] - `p1` - Validate configuration schema - `inst-validate-config`
3. [ ] - `p2` - Initialize database connection - `inst-init-db`
```

---

## Template Example

```markdown
---
spider-template:
  version:
    major: 1
    minor: 0
  kind: SPEC
  unknown_sections: error
---

# Spec: {Name}

<!-- spd:##:overview -->
## Overview
<!-- spd:##:overview -->

<!-- spd:paragraph:description required="true" -->
Brief description of the spec.
<!-- spd:paragraph:description -->

<!-- spd:id:requirements required="true" repeat="many" covered_by="CODE" has="task" -->
- [ ] **ID**: `spd-system-req-xxx`
<!-- spd:id:requirements -->

<!-- spd:sdsl:flow required="true" -->
1. [ ] - `p1` - Step description - `inst-step-name`
<!-- spd:sdsl:flow -->
```

---

## Artifact Validation

### Structure Validation

1. **Required blocks**: All `required="true"` blocks must be present
2. **Repeat constraint**: `repeat="one"` blocks can appear at most once
3. **Content type**: Block content must match its type requirements
4. **Unknown sections**: Handled per `unknown_sections` policy

### Content Validation

| Block Type | Validation |
|------------|------------|
| `id` | Each line matches ID definition pattern |
| `id-ref` | Each line matches ID reference pattern |
| `list` | Lines start with `- ` or `* ` |
| `numbered-list` | Lines start with `N. ` or `N)` |
| `task-list` | Lines start with `- [ ]` or `- [x]` |
| `table` | Has header row, separator row, at least one data row |
| `paragraph` | At least one non-empty line |
| `code` | Starts with ``` and has closing ``` |
| `#`-`######` | First line is heading of correct level |
| `link` | Contains `[text](url)` |
| `image` | Starts with `!` |
| `sdsl` | Each line matches SDSL pattern |

### Cross-Validation

1. **covered_by**: IDs must be referenced in artifacts of specified kinds
2. **Reference integrity**: All referenced IDs must be defined somewhere
3. **Task consistency**: If all tasks done, ID checkbox should be done (and vice versa)

---

## Error Types

| Type | Description |
|------|-------------|
| `template` | Template parsing/loading error |
| `structure` | Artifact structure doesn't match template |
| `kind` | Artifact kind doesn't match expected |
| `file` | File read error |

### Error Format

```json
{
  "type": "structure",
  "message": "Required block missing",
  "path": "path/to/file.md",
  "line": 42,
  "id": "block-name",
  "marker_type": "id"
}
```

---

## Agent Workflow

### When to Use This Spec

1. **Creating templates**: When defining new artifact kinds
2. **Validating artifacts**: When checking artifact structure against templates
3. **Debugging validation errors**: When interpreting error messages

### Template Creation Workflow

1. Define artifact kind in frontmatter
2. Add required markers with appropriate types
3. Set attributes (`required`, `repeat`, `covered_by`, etc.)
4. Test with example artifact

### Validation Workflow

1. Load template for artifact kind
2. Parse artifact markers
3. Check structure against template
4. Validate content per marker type
5. Report errors with line numbers

### Common Tasks

| Task | Command |
|------|---------|
| Validate artifact | `python3 {spider_path}/skills/spider/scripts/spider.py validate --artifact <path>` |
| List IDs | `python3 {spider_path}/skills/spider/scripts/spider.py list-ids` |
| Check references | `python3 {spider_path}/skills/spider/scripts/spider.py check-refs` |

---

## Validation Checklist

- [ ] Template has valid frontmatter OR kind can be inferred from path
- [ ] Template version is supported (≤ 2.0)
- [ ] All markers are properly paired (open/close)
- [ ] Artifact has all required blocks
- [ ] Block content matches type constraints
- [ ] ID formats are correct
- [ ] All references resolve to definitions
- [ ] Task statuses are consistent (if `has="task"`)

---

## References

- **Schema**: `schemas/spider-template-frontmatter.schema.json`
- **Implementation**: `skills/spider/scripts/spider/utils/template.py`
- **CLI**: `python3 {spider_path}/skills/spider/scripts/spider.py validate --artifact <path>`
