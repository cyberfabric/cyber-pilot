---
cypilot: true
type: spec
name: Template Specification
version: 1.0
purpose: Define the format, structure, and usage of template.md kit files
drivers:
  - cpt-cypilot-fr-core-kits
---

# Template Specification (template.md)


<!-- toc -->

- [Overview](#overview)
- [Location](#location)
- [File Structure](#file-structure)
- [File Format](#file-format)
- [Placeholder Variables](#placeholder-variables)
- [Example](#example)
- [Usage](#usage)
- [Error Handling](#error-handling)

<!-- /toc -->

---
---

## Overview

`template.md` is a kit file that provides the clean heading structure for an artifact kind. It is authored by kit authors and user-editable after installation.

**Key properties**:
- Kit file — user-editable, preserved across kit updates via file-level diff
- Clean Markdown with no `@cpt:` markers
- Contains heading structure with `{placeholder}` variables
- Used by generate workflows as structural reference for artifact creation

---

## Location

**Per-artifact**: `{cypilot_path}/config/kits/<slug>/artifacts/<KIND>/template.md`

---

## File Structure

> **Legacy note**: In the previous blueprint-based model, `template.md` was generated from `@cpt:heading` and `@cpt:prompt` markers. In the current model, `template.md` is authored directly by kit authors. See [blueprint.md](blueprint.md) (DEPRECATED) for legacy marker reference.

`template.md` contains only headings and optional placeholder text. Kit authors maintain this file directly.

---

## File Format

A valid `template.md` is a pure Markdown file containing only headings and optional placeholder text:

```markdown
# PRD — {Title of product}

## 1. Overview

### 1.1 Purpose

### 1.2 Background / Problem Statement

### 1.3 Goals (Business Outcomes)

## 2. Functional Requirements

## 3. Non-functional Requirements

## 4. Actors & Use Cases

### 4.1 Actors

### 4.2 Use Cases
```

**Rules**:
- Each heading defines one position in the artifact outline
- Heading levels use standard Markdown `#` syntax
- Numbered headings include numbering prefixes consistent with their hierarchy
- `{placeholder}` variables appear in heading text as prompts for what to fill in
- No other content between headings (body content is for the user to fill in)

---

## Placeholder Variables

Placeholders use the `{name}` format in heading text:

```markdown
# PRD — {Title of product}
```

- Placeholders are preserved literally in `template.md`
- Generate workflows replace placeholders with actual values during artifact creation
- The text inside `{...}` serves as the writing prompt — it tells the author what to fill in

---

## Example

Example `template.md` for a PRD artifact kind:

```markdown
# PRD — {Title of product}

## 1. Overview

### 1.1 Purpose
```

---

## Usage

- **Generate workflows**: load `template.md` as structural reference when creating a new artifact
- **Validate workflows**: compare artifact headings against `template.md` structure (via constraints.toml)
- **Agent context**: agents use `template.md` to understand required sections

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `TEMPLATE_NOT_FOUND` | `template.md` missing from kit | Run `cpt kit install` or `cpt kit update --force` to restore |
| `TEMPLATE_NO_HEADINGS` | `template.md` has no heading lines | Add at least one Markdown heading to `template.md` |
