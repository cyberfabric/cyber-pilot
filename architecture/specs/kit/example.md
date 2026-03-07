---
cypilot: true
type: spec
name: Example Specification
version: 1.0
purpose: Define the format, structure, and usage of example.md kit files
drivers:
  - cpt-cypilot-fr-core-kits
---

# Example Specification (example.md)


<!-- toc -->

- [Overview](#overview)
- [Location](#location)
- [File Structure](#file-structure)
- [File Format](#file-format)
- [Example](#example)
- [Usage](#usage)
- [Error Handling](#error-handling)

<!-- /toc -->

---
---

## Overview

`example.md` is a kit file that provides a concrete, complete example artifact for a given kind. It is authored by kit authors and user-editable after installation.

**Key properties**:
- Kit file — user-editable, preserved across kit updates via file-level diff
- Contains a realistic, complete example of an artifact
- Used by generate workflows as style and content reference

---

## Location

**Per-artifact**: `{cypilot_path}/config/kits/<slug>/artifacts/<KIND>/examples/example.md`

---

## File Structure

> **Legacy note**: In the previous blueprint-based model, `example.md` was generated from `@cpt:heading` and `@cpt:example` markers. In the current model, `example.md` is authored directly by kit authors. See [blueprint.md](blueprint.md) (DEPRECATED) for legacy marker reference.

`example.md` is a complete, realistic sample artifact. Kit authors maintain this file directly.

---

## File Format

A valid `example.md` is a pure Markdown file that looks like a real artifact:

```markdown
# PRD — Overwork Alert

## 1. Overview

### 1.1 Purpose

Overwork Alert is a system that monitors employee work hours across the organization
and sends automated alerts when individuals exceed configurable weekly thresholds.
The system integrates with existing time tracking tools and provides real-time
dashboards for management oversight.

### 1.2 Background / Problem Statement

Currently, managers rely on manual timesheet reviews to identify employees at risk of
burnout. This process is error-prone, delayed by up to two weeks, and provides no
real-time visibility. Several incidents of employee burnout in Q3 2025 were only
detected after the fact, resulting in extended medical leave and project delays.

### 1.3 Goals (Business Outcomes)

- Reduce burnout incidents by 60% within 6 months of deployment
- Provide real-time alerts within 1 hour of threshold breach
- Achieve 90% manager adoption within first quarter
```

**Rules**:
- Heading text comes from the first entry in `@cpt:heading.examples`
- Body content is verbatim from `@cpt:example` ` ```markdown ` blocks
- No `@cpt:` markers or metadata in the output
- Sections are ordered by heading definition order in the artifact kind

---

## Example

Example excerpt from an `example.md` for a PRD artifact kind:

```markdown
# PRD — Overwork Alert

Overwork Alert is a system that monitors employee work hours...
```

---

## Usage

- **Generate workflows**: load `example.md` as style and content reference when creating a new artifact
- **Analyze workflows**: compare artifact content style against `example.md` for consistency guidance
- **Agent context**: agents use `example.md` to understand the expected tone, detail level, and format

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `EXAMPLE_NOT_FOUND` | `example.md` missing from kit | Run `cpt kit install` or `cpt kit update --force` to restore |
| `EXAMPLE_NO_CONTENT` | `example.md` has no meaningful content | Add realistic example content to the file |
