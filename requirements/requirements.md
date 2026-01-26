---
fdd: true
type: requirement
name: Common Requirements
version: 1.0
purpose: Define common requirements shared across FDD structure requirements
---

# Common Requirements Structure Requirements

## Prerequisite Checklist

- [ ] Agent has identified which artifact type is being validated
- [ ] Agent understands that these are SHARED requirements across all structure files

---

## Overview

This file defines requirements that are shared across multiple `*-structure.md` requirements files.

**Goal**: Avoid duplication across structure requirements.

**Applies to**:
- Artifact docs:
  - `architecture/PRD.md`
  - `architecture/DESIGN.md`
  - `architecture/ADR/`
  - `architecture/features/FEATURES.md`
  - `architecture/features/feature-{slug}/DESIGN.md`
- Adapter spec docs:
  - `{adapter-directory}/specs/*.md`

**Does NOT apply to**:
- Agent instruction files (AGENTS.md, workflow navigation files)

---

## Structure

### Links (Artifacts)

**MUST**:
- Use standard Markdown links for file references in artifact docs: `[label]({relative-path})`
- Use relative paths (do not use absolute filesystem paths)
- Ensure links to repository files point to existing files
- Use relative paths that work in standard Markdown renderers

**MUST NOT**:
- Use IDE-specific link notations:
  - `@/path/to/file`
  - `@DESIGN.md`
  - `@PRD.md`
  - `@ADR/`

### Links (Adapter Spec Docs)

**MUST**:
- Use standard Markdown links for file references in adapter spec docs: `[label]({relative-path})`
- Use relative paths (do not use absolute filesystem paths)
- Ensure links to repository files point to existing files

**MUST NOT**:
- Use IDE-specific link notations:
  - `@/path/to/file`
  - `@DESIGN.md`
  - `@PRD.md`
  - `@ADR/`

### Link Target Validity (Artifacts)

**MUST**:
- Ensure all file links are clickable and navigable in standard Markdown viewers
- Ensure links do not create broken references

### Placeholders (Artifacts)

**MUST NOT**:
- Use TODO placeholders in artifact docs (e.g., `TODO`, `[TODO]`)
- Use TBD placeholders in artifact docs (e.g., `TBD`, `[TBD]`)
- Use FIXME placeholders in artifact docs (e.g., `FIXME`)
- Use `XXX` markers in artifact docs
- Use HTML comment placeholders in artifact docs (e.g., `<!-- TODO: ... -->`)
- Leave `{placeholder}` content in artifact docs

### Placeholders (Adapter Spec Docs)

**MUST NOT**:
- Use TODO placeholders in adapter spec docs (e.g., `TODO`, `[TODO]`)
- Use TBD placeholders in adapter spec docs (e.g., `TBD`, `[TBD]`)
- Use FIXME placeholders in adapter spec docs (e.g., `FIXME`)
- Use `XXX` markers in adapter spec docs
- Use HTML comment placeholders in adapter spec docs (e.g., `<!-- TODO: ... -->`)
- Leave `{placeholder}` content in adapter spec docs

### Markdown Validity (Artifacts)

**MUST**:
- Use valid Markdown that renders correctly in standard Markdown viewers

**MUST NOT**:
- Use malformed Markdown

### Content Presence (Artifacts)

**MUST**:
- Provide substantive content (not placeholder-only)

**MUST NOT**:
- Leave artifact docs empty
- Leave artifact docs placeholder-only

### Size Limits (Artifacts)

**MUST**:
- Follow size limits defined by the applicable `*-structure.md` requirements file

**MUST** define size limits in a consistent format in the corresponding structure requirements:
- `**Size limits**:` section
- `- Recommended: ...`
- `- Hard limit: ...`

### ID Conventions (FDD IDs)

**Applies to**: Any FDD-scoped ID that starts with `fdd-` in artifact docs and adapter spec docs.

**MUST**:
- Use kebab-case for `fdd-...` IDs
- Keep `fdd-...` IDs unique within the document scope where they are defined
- Wrap `fdd-...` ID values in backticks when written in markdown (e.g., `**ID**: \`fdd-...\``)

**MUST NOT**:
- Use non-kebab-case variants for `fdd-...` IDs
- Use unwrapped (non-backticked) `fdd-...` IDs when written as ID values

### ID Placement (Artifacts)

**Applies to**: Any artifact doc section where a heading is followed by an `**ID**:` line.

**MUST**:
- Insert exactly one blank line between the heading and the `**ID**:` line
- Use `**ID**: \`fdd-...\`` format

**MUST NOT**:
- Place the `**ID**:` line immediately after the heading (no blank line)

### ID Payload Blocks (Artifacts)

**Applies to**: Any artifact doc line that defines an FDD ID using `**ID**: \`fdd-...\``.

**MUST**:
- Include a deterministic payload block delimited by `<!-- fdd-id-content -->` immediately after the `**ID**:` line (allowing optional blank lines)
- Close the payload block with a matching `<!-- fdd-id-content -->` line
- Keep the payload block content inside the delimiters (payload MAY be empty)
  - Ensure the payload block contains all content of the enclosing element
    - Enclosing element content MUST be computed as all lines after the element heading until the next heading of the same level or higher
    - Enclosing element content MAY contain multiple `**ID**:` blocks; each `**ID**:` starts a new element
    - For each element: no non-empty lines are allowed outside the payload block until the next `**ID**:` line or the enclosing element boundary

**MUST NOT**:
- Place any content for an `**ID**:` outside the payload block
- Use unmatched payload delimiters

### Section Heading Format (Artifacts)

**Applies to**: Artifact docs that use lettered top-level sections (A, B, C, ...).

**MUST**:
- Use `## {LETTER}. {Title}` for top-level sections (e.g., `## A. Vision`)

**MUST NOT**:
- Use the `## Section {LETTER}: {Title}` format (e.g., `## Section A: Vision`)

### Validation Scoring (Structure Requirements)

**Applies to**: Any `*-structure.md` file that defines a scoring system for validating an artifact.

**MUST**:
- Use a 100-point scoring scale when scoring is used
- Declare pass threshold in `/100` terms (e.g., `≥90/100`)

### Validation Report Format (Structure Validators)

**Applies to**: Any workflow validator output that reports validation results for artifacts.

**MUST**:
- Include an `Issues` section listing missing/invalid items
- Include a `Recommendations` section describing what to fix

**MUST** include these fields when they are part of the validation model:
- `Score: X/100`
- `Completeness: X%`

### Section Ordering (Structure Requirements)

**Applies to**: Any `*-structure.md` file that defines an ordered set of top-level sections (e.g., A/B/C, 1/2/3).

**MUST**:
- Define the required top-level section order as a single ordered sequence (e.g., `A → B → C`)
- Explicitly state which sections are optional (if any) and where they are allowed to appear in the sequence

**MUST NOT**:
- Allow ambiguous ordering rules

---

## Validation Criteria

### Link Format (Artifacts)

**Check**:
- [ ] No occurrences of `@/` in artifact docs
- [ ] No occurrences of `@DESIGN.md` in artifact docs
- [ ] No occurrences of `@PRD.md` in artifact docs
- [ ] No occurrences of `@ADR/` in artifact docs

### Link Target Validity (Artifacts)

**Check**:
- [ ] All Markdown links to files point to existing files
- [ ] No broken references from file links

### Link Format (Adapter Specs)

**Check**:
- [ ] No occurrences of `@/` in adapter spec docs under `{adapter-directory}/specs/`
- [ ] No occurrences of `@DESIGN.md` in adapter spec docs under `{adapter-directory}/specs/`
- [ ] No occurrences of `@PRD.md` in adapter spec docs under `{adapter-directory}/specs/`
- [ ] No occurrences of `@ADR/` in adapter spec docs under `{adapter-directory}/specs/`

### Placeholders (Adapter Spec Docs)

**Check**:
- [ ] No occurrences of `TODO` in adapter spec docs under `{adapter-directory}/specs/`
- [ ] No occurrences of `[TODO]` in adapter spec docs under `{adapter-directory}/specs/`
- [ ] No occurrences of `TBD` in adapter spec docs under `{adapter-directory}/specs/`
- [ ] No occurrences of `[TBD]` in adapter spec docs under `{adapter-directory}/specs/`
- [ ] No occurrences of `FIXME` in adapter spec docs under `{adapter-directory}/specs/`
- [ ] No occurrences of `XXX` in adapter spec docs under `{adapter-directory}/specs/`
- [ ] No occurrences of `{placeholder}` content in adapter spec docs under `{adapter-directory}/specs/`
- [ ] No occurrences of HTML comment placeholders in adapter spec docs under `{adapter-directory}/specs/`

### Placeholders (Artifacts)

**Check**:
- [ ] No occurrences of `TODO` in artifact docs
- [ ] No occurrences of `[TODO]` in artifact docs
- [ ] No occurrences of `TBD` in artifact docs
- [ ] No occurrences of `[TBD]` in artifact docs
- [ ] No occurrences of `FIXME` in artifact docs
- [ ] No occurrences of `XXX` in artifact docs
- [ ] No occurrences of `{placeholder}` content in artifact docs
- [ ] No occurrences of HTML comment placeholders in artifact docs (e.g., `<!-- TODO: ... -->`)

### Markdown Validity (Artifacts)

**Check**:
- [ ] No occurrences of malformed Markdown in artifact docs

### Content Presence (Artifacts)

**Check**:
- [ ] No artifact doc is empty
- [ ] No artifact doc is placeholder-only

### Size Limits (Artifacts)

**Check**:
- [ ] Artifact docs do not exceed their hard size limits as defined by their structure requirements

### ID Conventions (FDD IDs)

**Check**:
- [ ] All `fdd-...` IDs are kebab-case
- [ ] All `fdd-...` ID values are wrapped in backticks

### ID Placement (Artifacts)

**Check**:
- [ ] All `**ID**:` lines appear after exactly one blank line following their headings

### ID Payload Blocks (Artifacts)

**Check**:
- [ ] For every FDD ID definition line ``**ID**: `fdd-...` ``, the next non-empty line is exactly the literal HTML comment line `<!-- fdd-id-content -->` (without surrounding backticks)
- [ ] The payload block is closed by a matching literal HTML comment line `<!-- fdd-id-content -->` (without surrounding backticks) before the next element boundary (next heading of same-or-higher level, or next `**ID**:` line)
- [ ] No non-empty lines exist outside the payload block between the `**ID**:` line and the end of the element (except an optional Markdown horizontal rule line `---` after the payload close)

### Section Heading Format (Artifacts)

**Check**:
- [ ] No occurrences of `## Section {LETTER}:` in artifact docs

### Validation Scoring (Structure Requirements)

**Check**:
- [ ] If scoring is used, it uses a 100-point scale and defines a pass threshold in `/100` terms

### Validation Report Format (Structure Validators)

**Check**:
- [ ] Validator reports include Issues and Recommendations
- [ ] If scoring is used, reports include `Score: X/100`
- [ ] If completeness is used, reports include `Completeness: X%`

### Section Ordering (Structure Requirements)

**Check**:
- [ ] If a structure file defines an ordered section sequence, it declares a strict order and defines optional sections and allowed positions

---

## Examples

**Valid**:
```markdown
See [PRD.md](PRD.md)
See [ADR](ADR/)
See [api.json](../../../docs/api/api.json)
```

**Invalid**:
```markdown
See `@/architecture/PRD.md`
See `@ADR/`
```

---

## Validation Checklist

- [ ] All links use standard Markdown format
- [ ] No IDE-specific link notations used
- [ ] No placeholder content remains
- [ ] All FDD IDs are kebab-case and backticked
- [ ] ID payload blocks properly delimited

---

## References

- `../.adapter/specs/conventions.md` - Core formatting and requirement semantics
- `../.adapter/specs/patterns.md` - Requirements file structure and duplication rules
