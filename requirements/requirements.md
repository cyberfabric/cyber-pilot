---
fdd: true
type: requirement
name: Common Requirements
version: 1.0
purpose: Define common requirements shared across FDD requirements
---

# Common Requirements

## Prerequisite Checklist

- [ ] Agent has identified which artifact type is being validated
- [ ] Agent understands that these are shared requirements across multiple requirements files

---

## Overview

This file defines requirements that are shared across multiple FDD requirements files.

**Goal**: Avoid duplication across requirements.

**Applies to**:
- Artifact docs:
  - FDD artifacts registered in `{adapter-dir}/artifacts.json`
- Adapter spec docs:
  - `{adapter-directory}/specs/*.md`

**Does NOT apply to**:
- Agent instruction files (AGENTS.md, workflow navigation files)

---

## Shared Content and Quality Requirements

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

### ID Conventions (FDD IDs)

**Applies to**: Any FDD-scoped ID that starts with `fdd-` in artifact docs and adapter spec docs.

**MUST**:
- Use kebab-case for `fdd-...` IDs
- Keep `fdd-...` IDs unique within the document scope where they are defined
- Wrap `fdd-...` ID values in backticks when written in markdown (e.g., `**ID**: \`fdd-...\``)

**MUST NOT**:
- Use non-kebab-case variants for `fdd-...` IDs
- Use unwrapped (non-backticked) `fdd-...` IDs when written as ID values

### Validation Report Format (Validators)

**Applies to**: Any workflow validator output that reports validation results for artifacts.

**MUST**:
- Include an `Issues` section listing missing/invalid items
- Include a `Recommendations` section describing what to fix

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

### ID Conventions (FDD IDs)

**Check**:
- [ ] All `fdd-...` IDs are kebab-case
- [ ] All `fdd-...` ID values are wrapped in backticks

### ID Placement (Artifacts)

**Check**:
- [ ] All `**ID**:` lines appear after exactly one blank line following their headings

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
See `@/some/path/to/PRD.md`
See `@ADR/`
```

---

## Validation Checklist

- [ ] All links use standard Markdown format
- [ ] No IDE-specific link notations used
- [ ] No placeholder content remains
- [ ] All FDD IDs are kebab-case and backticked


---

## References

- `../.adapter/specs/conventions.md` - Core formatting and requirement semantics
- `../.adapter/specs/patterns.md` - Requirements file structure and duplication rules
