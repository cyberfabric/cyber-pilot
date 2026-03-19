---
cypilot: true
type: requirement
name: Documentation Consistency Expert Checklist (Code-Excluded)
version: 1.0
purpose: Technology-agnostic methodology for semantic consistency and contradiction detection across non-code project documents
---

# Documentation Consistency Expert Checklist (Code-Excluded)


<!-- toc -->

- [Procedure](#procedure)
- [Scope Notes](#scope-notes)
- [Severity](#severity)
- [Inventory & Structure (INV)](#inventory--structure-inv)
- [Dependency Graph (DEP)](#dependency-graph-dep)
- [Terminology & Naming (TERM)](#terminology--naming-term)
- [Claims & Consistency (CLAIM)](#claims--consistency-claim)
- [Link & Reference Integrity (LINK)](#link--reference-integrity-link)
- [Staleness & Drift (STALE)](#staleness--drift-stale)
- [Style & Language Quality (STYLE)](#style--language-quality-style)
- [Validation Summary](#validation-summary)
- [Reporting](#reporting)

<!-- /toc -->

## Procedure

- [ ] Define in-scope roots and explicit exclusions.
- [ ] List exclusions in the report header.
- [ ] Run a deterministic scan before deep reading.
- [ ] Build a dependency graph before making consistency claims.
- [ ] Validate each document, then each dependency edge, with evidence.
- [ ] Report issues only; each issue includes checklist ID, severity, locations, evidence, why it matters, and a concrete fix.

## Scope Notes

- In scope: human-authored, non-code docs such as `README*`, `CHANGELOG*`, `CONTRIBUTING*`, `docs/`, `guides/`, `requirements/`, `workflows/`, templates/specs, and documentation-like JSON/YAML/TOML.
- Out of scope by default: source code and tests, excluded by explicit directory and extension rules.
- Definitions: document = in-scope authored file; claim = verifiable statement; term = stable named concept; dependency edge = link/directive/path reference; canonical source = single owner of a concept.

## Severity

- CRITICAL: contradiction that misleads usage/compliance, broken dependency edge, or incompatible requirements.
- HIGH: strong inconsistency or major ambiguity likely to cause wrong decisions.
- MEDIUM: drift, duplication, outdated detail, or inconsistent terminology.
- LOW: style/grammar issue that reduces clarity without changing meaning.

# MUST HAVE

## Inventory & Structure (INV)

### INV-DOC-001: Complete inventory (configured scope) [CRITICAL]
- [ ] All included roots were scanned.
- [ ] All exclusions are explicitly listed.
- [ ] Inventory is stable-sorted and reproducible.
- [ ] Each included file has a 1–2 sentence purpose.

### INV-DOC-002: Document type classification [HIGH]
- [ ] Each document is classified by type.
- [ ] Document structure matches its type.
- [ ] Tutorial/how-to/reference/explanation intents are not mixed carelessly.

## Dependency Graph (DEP)

### DEP-DOC-001: Graph built before deep review [CRITICAL]
- [ ] A dependency graph exists before deep review.
- [ ] Edge types are classified.
- [ ] Normative edges are identified.

### DEP-DOC-002: Canonical sources defined [HIGH]
- [ ] Each major concept has one canonical source.
- [ ] Other documents link to the canonical source instead of restating it.

## Terminology & Naming (TERM)

### TERM-DOC-001: Stable term glossary (implicit or explicit) [HIGH]
- [ ] Project and product names stay consistent.
- [ ] Key nouns do not drift without migration notes.
- [ ] Acronyms are expanded on first use unless globally obvious.

### TERM-DOC-002: Command and file names are exact [HIGH]
- [ ] Command names match actual interfaces.
- [ ] File paths use correct casing and separators.
- [ ] Renamed paths are not left stale.

## Claims & Consistency (CLAIM)

### CLAIM-DOC-001: No cross-document contradictions [CRITICAL]
- [ ] Requirements and constraints do not conflict.
- [ ] Versions, ordering, and contracts do not conflict.
- [ ] `MUST/SHOULD` statements align across documents.
- [ ] Duplicate process descriptions match in steps and outcomes.

### CLAIM-DOC-002: Normative statements have a source [HIGH]
- [ ] `MUST/ALWAYS/NEVER` statements live in a canonical policy or protocol doc, or
- [ ] they link to that canonical doc.

## Link & Reference Integrity (LINK)

### LINK-DOC-001: All references resolve [CRITICAL]
- [ ] All relative links resolve to existing targets.
- [ ] All referenced anchors and headings exist.

### LINK-DOC-002: Reference hierarchy is explicit [MEDIUM]
- [ ] When multiple style guides exist, precedence is explicit (`project > primary style guide > external`).

## Staleness & Drift (STALE)

### STALE-DOC-001: Stale statements are flagged [HIGH]
- [ ] “Coming soon” or TODO-like promises are removed or tracked.
- [ ] Old version requirements match current declared requirements.
- [ ] Deprecated workflows and commands are labeled.
- [ ] Deprecated workflows and commands link to replacements.

### STALE-DOC-002: Duplicated content is controlled [MEDIUM]
- [ ] Duplicated definitions are eliminated or explicitly synchronized.
- [ ] Canonical sources are used for definitions and contracts.

## Style & Language Quality (STYLE)

### STYLE-DOC-001: Voice and tone are consistent [LOW]
- [ ] Writing is direct and clear.
- [ ] Writing avoids unnecessary hype.
- [ ] Imperatives are used consistently in procedures.

### STYLE-DOC-002: Accessibility and readability basics [LOW]
- [ ] Headings are descriptive and scannable.
- [ ] Lists stay parallel.
- [ ] Lists are not excessively nested.
- [ ] Sentences are not excessively long.

# MUST NOT HAVE

### DOC-NO-001: Silent skipping of files in scope [CRITICAL]
- [ ] No in-scope file is skipped without explicit exclusion rationale.

### DOC-NO-002: Uncited contradictions [HIGH]
- [ ] No contradiction is claimed without quoting both sides.

### DOC-NO-003: “Bulk PASS” language without evidence [HIGH]
- [ ] No broad pass claim is made without inventory and evidence.

### DOC-NO-004: Multiple competing “sources of truth” without precedence [MEDIUM]
- [ ] No concept has multiple sources of truth unless explicit precedence is documented.

## Validation Summary

- [ ] Inventory table with exclusions is produced.
- [ ] Dependency graph is produced.
- [ ] Every in-scope file is reviewed in order or explicitly excluded with rationale.
- [ ] Every reported issue includes evidence.
- [ ] Every reported issue includes a fix.

## Reporting

- Use issues-only table: `| Severity | Checklist ID | Location(s) | Evidence | Problem | Fix |`.
- For contradictions, quote the exact conflicting statements from 2+ locations.
- For link issues, include the broken path or anchor and the intended target.
- Recommended deliverables: inventory table, dependency adjacency list, canonical-source list, and top-term list.
