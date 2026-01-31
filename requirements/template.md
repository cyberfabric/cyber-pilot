---
fdd: true
type: requirement
name: FDD Template Specification
version: 1.0
purpose: Define marker-based template syntax for FDD artifacts
---

# FDD Template Specification

## Prerequisite Checklist

- [ ] Agent has identified the artifact being validated
- [ ] Agent understands template marker syntax
- [ ] Agent has access to the template file for the artifact kind

---

## Overview

FDD templates use paired HTML comment markers to define structural blocks in markdown documents. This enables deterministic validation of artifacts against their templates.

**Supported Version**: `1.0`

---

## Template Frontmatter

Every template MUST begin with YAML frontmatter:

```yaml
---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: <KIND>
  unknown_sections: warn
---
```

**IMPORTANT**: This `fdd-template:` frontmatter is **template metadata only**. It MUST NOT be copied into generated artifacts. Artifacts may optionally have their own `fdd:` frontmatter for document metadata.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version.major` | integer | YES | Major version (breaking changes) |
| `version.minor` | integer | YES | Minor version (compatible changes) |
| `kind` | string | YES | Artifact kind (PRD, DESIGN, ADR, FEATURES, FEATURE) |
| `unknown_sections` | string | NO | How to handle markers not in template: `error`, `warn`, `allow`. Default: `warn` |

---

## Marker Syntax

### Basic Structure

```html
<!-- fdd:TYPE:NAME ATTRS -->
content goes here
<!-- fdd:TYPE:NAME -->
```

**Pattern**: `<!-- fdd:(?:TYPE:)?NAME ATTRS -->`

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
| `fdl` | FDL instruction list | Lines matching FDL format |

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
**ID**: `fdd-project-kind-slug`
**ID**: [ ] `fdd-project-kind-slug`
**ID**: [x] `p1` - `fdd-project-kind-slug`
**ID**: `p2` - `fdd-project-kind-slug`
```

**Pattern**:

```regex
^\*\*ID\*\*:\s*(?:(?:\[\s*[xX]?\s*\])\s*(?:`p\d+`\s*-\s*)?)?`fdd-[a-z0-9][a-z0-9-]+`\s*$
```

Components:
- `**ID**:` — literal prefix (required)
- `[ ]` or `[x]` — optional task checkbox
- `` `p1` `` - `` `p9` `` — optional priority
- `` `fdd-xxx` `` — the ID in backticks (required)

### ID Reference (`id-ref` block)

```
`fdd-project-kind-slug`
[ ] `fdd-project-kind-slug`
[x] `p1` - `fdd-project-kind-slug`
```

**Pattern**:

```regex
^(?:(?:\[\s*[xX]?\s*\])\s*(?:`p\d+`\s*-\s*)?)?`fdd-[a-z0-9][a-z0-9-]+`\s*$
```

### Inline ID Reference

Any `` `fdd-xxx` `` in content is treated as a reference.

**Pattern**:

```regex
`(fdd-[a-z0-9][a-z0-9-]+)`
```

### ID Naming Convention

```
fdd-{project}-{kind}-{slug}
```

- `fdd-` — literal prefix (required)
- `{project}` — project/system identifier (lowercase, alphanumeric, hyphens)
- `{kind}` — ID kind (actor, cap, req, flow, algo, state, test, etc.)
- `{slug}` — descriptive slug (lowercase, alphanumeric, hyphens)

**Examples**:
- `fdd-myapp-actor-admin-user`
- `fdd-myapp-cap-user-management`
- `fdd-myapp-req-must-authenticate`
- `fdd-myapp-flow-login-process`

---

## FDL Format (FDD Definition Language)

FDL is used in `fdl` blocks to define step-by-step instructions with traceability.

### FDL Line Format

```
N. [ ] - `ph-N` - Description - `inst-slug`
- [ ] - `ph-N` - Description - `inst-slug`
```

**Pattern**:

```regex
^\s*(?:\d+\.\s+|-\s+)\[\s*[xX ]\s*\]\s*-\s*`ph-\d+`\s*-\s*.+\s*-\s*`inst-[a-z0-9-]+`\s*$
```

Components:
- `N.` or `-` — list marker (numbered or bullet)
- `[ ]` or `[x]` — completion checkbox
- `` `ph-N` `` — phase number
- `Description` — what this step does
- `` `inst-slug` `` — instruction ID for code traceability

**Example**:
```markdown
1. [ ] - `ph-1` - Load configuration from environment - `inst-load-config`
2. [ ] - `ph-1` - Validate configuration schema - `inst-validate-config`
3. [ ] - `ph-2` - Initialize database connection - `inst-init-db`
```

---

## Template Example

```markdown
---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: FEATURE
  unknown_sections: error
---

# Feature: {Name}

<!-- fdd:##:overview -->
## Overview
<!-- fdd:##:overview -->

<!-- fdd:paragraph:description required="true" -->
Brief description of the feature.
<!-- fdd:paragraph:description -->

<!-- fdd:id:requirements required="true" repeat="many" covered_by="CODE" has="task" -->
**ID**: [ ] `fdd-project-req-xxx`
<!-- fdd:id:requirements -->

<!-- fdd:fdl:flow required="true" -->
1. [ ] - `ph-1` - Step description - `inst-step-name`
<!-- fdd:fdl:flow -->
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
| `fdl` | Each line matches FDL pattern |

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

## Validation Criteria

- [ ] Template has valid fdd-template frontmatter
- [ ] Template version is supported (≤ 1.0)
- [ ] All markers are properly paired (open/close)
- [ ] Artifact has all required blocks
- [ ] Block content matches type constraints
- [ ] ID formats are correct
- [ ] References resolve to definitions
- [ ] Task statuses are consistent

---

## Validation Checklist

- [ ] Template frontmatter is present and valid
- [ ] Template version is supported
- [ ] All markers are properly paired
- [ ] Required blocks are present in artifact
- [ ] Block content matches type constraints
- [ ] ID formats are correct
- [ ] All references resolve

---

## References

- **Schema**: `schemas/fdd-template-frontmatter.schema.json`
- **Implementation**: `skills/fdd/scripts/fdd/utils/template.py`
