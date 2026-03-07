---
status: accepted
date: 2026-03-07
decision-makers: project maintainer
---

# ADR-0012: Git-Style Conflict Markers for Interactive Kit Merge


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [Git-style conflict markers](#git-style-conflict-markers)
  - [Side-by-side diff view](#side-by-side-diff-view)
  - [Custom merge format](#custom-merge-format)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-git-style-conflict-markers`

## Context and Problem Statement

When kit files are updated and the user's version differs from the new version, the "modify" resolution mode needs a format for presenting both versions inline so the user can manually merge. The format must be familiar to developers and supported by common editors and diff tools.

## Decision Drivers

* **Developer familiarity** — developers already know git merge conflict markers from daily workflow
* **Editor support** — VS Code, IntelliJ, vim, and other editors highlight and provide UI for resolving git conflict markers
* **Deterministic detection** — the tool must verify that all conflicts are resolved before accepting the file; markers must be unambiguous
* **Simplicity** — avoid inventing a custom format when a universal standard exists

## Considered Options

1. **Git-style conflict markers** — standard `<<<<<<<` / `=======` / `>>>>>>>` markers
2. **Side-by-side diff view** — show both versions in separate sections
3. **Custom merge format** — purpose-built markers for kit merge

## Decision Outcome

Chosen: **Standard git merge conflict markers**.

### Consequences

```
<<<<<<< installed (yours)
{user's content}
=======
{upstream content}
>>>>>>> upstream (source)
```

The tool writes conflict markers, opens the user's editor ($VISUAL → $EDITOR → vi), and re-validates that no markers remain after editing. Unresolved markers trigger a retry prompt.

* Good, because universal developer familiarity
* Good, because editor support is automatic (syntax highlighting, merge UI)
* Good, because deterministic detection — regex for `<<<<<<<`, `=======`, `>>>>>>>`
* Bad, because conflict markers don't work well for binary files — mitigated by kit files being text-only (Markdown, TOML)

### Confirmation

Confirmed by interactive kit update using conflict markers with automatic editor invocation and unresolved-marker detection.

## Pros and Cons of the Options

### Git-style conflict markers

* Good, because universal developer familiarity
* Good, because editor support is automatic
* Bad, because not suitable for binary files

### Side-by-side diff view

* Good, because visually clear comparison
* Bad, because requires terminal UI or external tool
* Bad, because no in-file editing

### Custom merge format

* Good, because could be optimized for kit files
* Bad, because learning curve — no editor support
* Bad, because reinventing an existing standard

## Traceability

- **PRD**: `cpt-cypilot-fr-core-resource-diff`
- **DESIGN**: `cpt-cypilot-component-kit-manager`, Resource Diff Engine
- **Related**: `cpt-cypilot-adr-remove-blueprint-system` (ADR-0001, file-level diff replaces three-way merge)
