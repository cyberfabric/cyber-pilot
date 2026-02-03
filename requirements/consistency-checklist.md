---
spider: true
type: requirement
name: Documentation Consistency Expert Checklist (Code-Excluded)
version: 1.0
purpose: Technology-agnostic methodology for semantic consistency and contradiction detection across non-code project documents
---

# Documentation Consistency Expert Checklist (Code-Excluded)

## Overview

This checklist defines a **two-phase**, technology-agnostic methodology for detecting **inconsistencies, contradictions, outdated statements, and style/terminology drift** across a project's **non-code** documentation.

**Goal**: a reviewer can confidently say “these documents do not contradict each other, and they tell one coherent story.”

**Non-goal**: validate the implementation or runtime behavior (all source code is excluded).

**Output contract**:
- Produce an **issues-only** report using the formats in [Reporting](#reporting).
- Every issue MUST include: checklist ID, severity, evidence (quotes), locations, why it matters, and a concrete fix.

---

## Table of Contents

- [Documentation Consistency Expert Checklist (Code-Excluded)](#documentation-consistency-expert-checklist-code-excluded)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Agent Instructions](#agent-instructions)
  - [Scope \& Exclusions](#scope--exclusions)
    - [What is in scope](#what-is-in-scope)
    - [What is excluded (default)](#what-is-excluded-default)
  - [Prerequisites](#prerequisites)
  - [Definitions](#definitions)
  - [Two-Phase Methodology](#two-phase-methodology)
    - [Phase 1 — Deterministic Project Scan](#phase-1--deterministic-project-scan)
    - [Phase 2 — Dependency Graph](#phase-2--dependency-graph)
    - [Phase 3 — File-by-File Semantic Validation](#phase-3--file-by-file-semantic-validation)
    - [Phase 4 — Dependency Validation](#phase-4--dependency-validation)
  - [Severity Dictionary](#severity-dictionary)
- [MUST HAVE](#must-have)
  - [Inventory \& Structure (INV)](#inventory--structure-inv)
    - [INV-DOC-001: Complete inventory (configured scope)](#inv-doc-001-complete-inventory-configured-scope)
    - [INV-DOC-002: Document type classification](#inv-doc-002-document-type-classification)
  - [Dependency Graph (DEP)](#dependency-graph-dep)
    - [DEP-DOC-001: Graph built before deep review](#dep-doc-001-graph-built-before-deep-review)
    - [DEP-DOC-002: Canonical sources defined](#dep-doc-002-canonical-sources-defined)
  - [Terminology \& Naming (TERM)](#terminology--naming-term)
    - [TERM-DOC-001: Stable term glossary (implicit or explicit)](#term-doc-001-stable-term-glossary-implicit-or-explicit)
    - [TERM-DOC-002: Command and file names are exact](#term-doc-002-command-and-file-names-are-exact)
  - [Claims \& Consistency (CLAIM)](#claims--consistency-claim)
    - [CLAIM-DOC-001: No cross-document contradictions](#claim-doc-001-no-cross-document-contradictions)
    - [CLAIM-DOC-002: Normative statements have a source](#claim-doc-002-normative-statements-have-a-source)
  - [Link \& Reference Integrity (LINK)](#link--reference-integrity-link)
    - [LINK-DOC-001: All references resolve](#link-doc-001-all-references-resolve)
    - [LINK-DOC-002: Reference hierarchy is explicit](#link-doc-002-reference-hierarchy-is-explicit)
  - [Staleness \& Drift (STALE)](#staleness--drift-stale)
    - [STALE-DOC-001: Stale statements are flagged](#stale-doc-001-stale-statements-are-flagged)
    - [STALE-DOC-002: Duplicated content is controlled](#stale-doc-002-duplicated-content-is-controlled)
  - [Style \& Language Quality (STYLE)](#style--language-quality-style)
    - [STYLE-DOC-001: Voice and tone are consistent](#style-doc-001-voice-and-tone-are-consistent)
    - [STYLE-DOC-002: Accessibility and readability basics](#style-doc-002-accessibility-and-readability-basics)
- [MUST NOT HAVE](#must-not-have)
  - [Validation Summary](#validation-summary)
  - [Reporting](#reporting)
    - [Issues-only format](#issues-only-format)
    - [Optional deliverables (recommended)](#optional-deliverables-recommended)
  - [References](#references)

---

## Agent Instructions

**ALWAYS open and follow** this file WHEN user requests documentation consistency / contradiction review.

**Critical discipline**:
- Start with a **deterministic scan** of the whole repo (Phase 1) before reading deeply.
- Build a **dependency graph** before making consistency claims.
- Then validate **file-by-file** and **edge-by-edge** with evidence.

**Anti-patterns** (INVALID output):
- “Everything looks consistent” without inventory + evidence.
- Skipping files because they “seem irrelevant” (must be explicitly excluded with rationale).

---

## Scope & Exclusions

### What is in scope

“Documents” are any **human-authored, non-code** files that define behavior, workflows, policies, conventions, or domain meaning.

Typical inclusions (project-dependent):
- `README*`, `CHANGELOG*`, `CONTRIBUTING*`
- `docs/`, `guides/`, `requirements/`, `workflows/`
- templates/specs written in Markdown/Asciidoc/RST/text
- JSON/YAML/TOML configuration **only when it is documentation-like** (e.g., registries, schemas, examples)

### What is excluded (default)

**Exclude all source code and tests**. Exclusion is by **directory + extension**.

Default directory excludes (customize per project):
- `.git/`, `.github/`, `.venv/`, `node_modules/`, `dist/`, `build/`, `target/`, `out/`
- `tests/`, `test/`, `__tests__/`, `spec/`
- tool implementation code directories (project-specific)

Default extension excludes (non-exhaustive):
- Code: `*.py`, `*.js`, `*.ts`, `*.go`, `*.rs`, `*.java`, `*.cs`, `*.c`, `*.cpp`, `*.kt`, `*.swift`, `*.rb`, `*.php`

**Rule**: excluded paths MUST be listed in the report header so the reader can audit what was skipped.

---

## Prerequisites

Before starting the review, confirm:

- [ ] I understand this checklist is **code-excluded** and evaluates **documentation consistency**
- [ ] I will run Phase 1 deterministic scan before deep reading
- [ ] I will build a dependency graph and validate it
- [ ] I will produce an issues-only report with evidence

---

## Definitions

- **Document**: any in-scope file (see Scope) treated as an authored knowledge artifact.
- **Claim**: a verifiable statement that can conflict with other statements (e.g., “Python 3.13+ required”, “Command outputs JSON”).
- **Term**: a named concept that should be stable (product names, commands, file paths, IDs, artifact kinds).
- **Dependency edge**: a reference from one document to another (link, “see …”, “ALWAYS open …”, “Extends: …”, path mention).
- **Canonical source**: the single document that owns a concept; other docs should link to it rather than restate it.

---

## Two-Phase Methodology

### Phase 1 — Deterministic Project Scan

**Outcome**: a complete, reproducible inventory of in-scope documents and a short description of each.

1. **Select roots**: choose documentation roots (e.g., repo root, `docs/`, `guides/`, `requirements/`, `workflows/`).
2. **Apply exclusions** (directories + extensions). Do not “mentally exclude”; make it explicit.
3. **Produce an inventory table**:

| Path | Type | 1–2 sentence purpose | Key owned concepts |
|---|---|---|---|

4. **Extract global term candidates**:
- project name(s)
- command names
- artifact kinds / spec names
- directory names used as concepts

5. **Extract global claim candidates**:
- supported platforms/versions
- CLI contracts (inputs/outputs)
- workflow ordering (“always do X before Y”)
- invariants and “MUST” statements

**Determinism requirements**:
- Sorting is stable (alphabetical paths).
- Inventory is complete for the configured roots.

### Phase 2 — Dependency Graph

**Outcome**: a graph $G=(V,E)$ where $V$ are documents and $E$ are references.

For each document in the inventory:
1. Parse and record edges:
   - Markdown links: `[text](relative/path.md)`
   - File path mentions in backticks: `` `path/to/file.md` ``
   - “open and follow …” / “see …” / “extends …” directives
2. Normalize each edge:
   - resolve relative paths
   - classify edge type: `link`, `directive`, `conceptual`, `schema/config`
3. Record edge intent:
   - `normative` (MUST follow)
   - `informational`

Graph deliverables:
- adjacency list (from → to)
- list of **canonical sources** (where concepts are defined)
- cycle report (cycles are not always wrong, but must be justified)

### Phase 3 — File-by-File Semantic Validation

**Outcome**: per-document findings with evidence, plus extracted structured summaries.

For each document (stable order):
1. Write a **structured summary**:
   - Purpose (1 sentence)
   - Owned concepts (bullets)
   - External dependencies (links)
   - Claims (bullets)
2. Validate **local consistency**:
   - headings match content intent
   - terms used consistently within the doc
   - claims don’t conflict internally
3. Validate **style consistency**:
   - tone and voice consistent with project style
   - avoid overclaiming (absolute/unverifiable statements)

### Phase 4 — Dependency Validation

**Outcome**: verify that dependencies are correct and consistent.

For each edge (from → to):
1. **Integrity**: target exists and is the intended document.
2. **Authority**: referenced target is the canonical source for the referenced concept (or the source is explicitly delegated).
3. **Semantic agreement**: shared terms and claims match.
4. **No contradictory duplication**: if the source doc duplicates target content, it must match exactly or be replaced with a link.

---

## Severity Dictionary

- **CRITICAL**: Contradiction that misleads usage/compliance; broken dependency edge; incompatible requirements.
- **HIGH**: Strong inconsistency or major ambiguity; likely to cause wrong decisions.
- **MEDIUM**: Drift, duplication, outdated details, inconsistent terms.
- **LOW**: Style/grammar issues that reduce clarity but don’t change meaning.

---

# MUST HAVE

---

## Inventory & Structure (INV)

### INV-DOC-001: Complete inventory (configured scope)
**Severity**: CRITICAL
- [ ] All included roots were scanned
- [ ] All exclusions are explicitly listed
- [ ] Inventory is stable-sorted and reproducible
- [ ] Each included file has a 1–2 sentence purpose

### INV-DOC-002: Document type classification
**Severity**: HIGH
- [ ] Each doc is classified (tutorial/how-to/reference/explanation or project-native types)
- [ ] Doc structure matches its type (avoid mixing “how-to” with “reference”)

(Heuristic inspired by Diátaxis: keep doc intents distinct.)

---

## Dependency Graph (DEP)

### DEP-DOC-001: Graph built before deep review
**Severity**: CRITICAL
- [ ] A dependency graph exists (adjacency list or table)
- [ ] Edge types are classified (link/directive/conceptual)
- [ ] Normative edges (“must follow”) are identified

### DEP-DOC-002: Canonical sources defined
**Severity**: HIGH
- [ ] Each major concept has one canonical source
- [ ] Other documents link to the canonical source rather than restating it

---

## Terminology & Naming (TERM)

### TERM-DOC-001: Stable term glossary (implicit or explicit)
**Severity**: HIGH
- [ ] Project/product names used consistently
- [ ] Key nouns are stable (no “rule/weaver”-style drift without migration notes)
- [ ] Acronyms expanded on first use (unless globally obvious)

### TERM-DOC-002: Command and file names are exact
**Severity**: HIGH
- [ ] Command names match actual interface names used elsewhere
- [ ] File paths use correct casing and separators
- [ ] No stale renamed paths

---

## Claims & Consistency (CLAIM)

### CLAIM-DOC-001: No cross-document contradictions
**Severity**: CRITICAL
- [ ] Requirements/constraints don’t conflict (versions, ordering, contracts)
- [ ] “MUST/SHOULD” statements align across docs
- [ ] If two docs describe the same process, steps and outcomes match

### CLAIM-DOC-002: Normative statements have a source
**Severity**: HIGH
- [ ] “MUST/ALWAYS/NEVER” statements either:
  - [ ] live in a canonical policy/protocol doc, or
  - [ ] link to that doc

---

## Link & Reference Integrity (LINK)

### LINK-DOC-001: All references resolve
**Severity**: CRITICAL
- [ ] All relative links point to existing targets
- [ ] All referenced anchors/headings exist

### LINK-DOC-002: Reference hierarchy is explicit
**Severity**: MEDIUM
- [ ] If multiple style guides exist, a precedence order exists (project > primary style guide > external)

---

## Staleness & Drift (STALE)

### STALE-DOC-001: Stale statements are flagged
**Severity**: HIGH
- [ ] Any “coming soon”, TODO-ish doc promises are either removed or tracked
- [ ] Old version requirements are aligned with the actual declared requirements elsewhere
- [ ] Deprecated workflows/commands are labeled and linked to replacements

### STALE-DOC-002: Duplicated content is controlled
**Severity**: MEDIUM
- [ ] Duplicated definitions are either eliminated or explicitly synchronized
- [ ] Canonical sources are used for definitions and contracts

---

## Style & Language Quality (STYLE)

### STYLE-DOC-001: Voice and tone are consistent
**Severity**: LOW
- [ ] Writing is direct, clear, and avoids unnecessary hype
- [ ] Imperatives are used consistently in procedures

### STYLE-DOC-002: Accessibility and readability basics
**Severity**: LOW
- [ ] Headings are descriptive and scannable
- [ ] Lists are parallel and not overly nested
- [ ] Sentences are not excessively long

---

# MUST NOT HAVE

- **DOC-NO-001 (CRITICAL)**: Silent skipping of files in scope
- **DOC-NO-002 (HIGH)**: Uncited contradictions (claiming mismatch without quoting both sides)
- **DOC-NO-003 (HIGH)**: “Bulk PASS” language without evidence
- **DOC-NO-004 (MEDIUM)**: Multiple competing “sources of truth” for the same concept without explicit precedence

---

## Validation Summary

Before reporting results, confirm:
- [ ] Inventory table produced (with exclusions)
- [ ] Dependency graph produced
- [ ] Every in-scope file reviewed in order OR explicitly excluded with rationale
- [ ] Every reported issue includes evidence and a fix

---

## Reporting

### Issues-only format

Use this table for the report:

| Severity | Checklist ID | Location(s) | Evidence | Problem | Fix |
|---|---|---|---|---|---|

**Evidence requirements**:
- Quote the exact contradictory statements (2+ locations) for contradiction issues.
- For link issues, include the broken path/anchor and the intended target.

### Optional deliverables (recommended)

- Inventory table (Phase 1)
- Dependency adjacency list (Phase 2)
- Canonical sources list
- Term list (top 20)

---

## References

These references inform the methodology (do not copy them verbatim; use them as principles):
- Diátaxis framework (doc intent separation): https://diataxis.fr/
- Google developer documentation style guide (consistency, reference hierarchy, voice/tone): https://developers.google.com/style
- Microsoft Writing Style Guide (clarity, voice): https://learn.microsoft.com/en-us/style-guide/
- Write the Docs — Docs as Code (treat docs with engineering discipline): https://www.writethedocs.org/guide/docs-as-code/
