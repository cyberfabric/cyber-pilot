---
status: accepted
date: 2026-03-07
decision-makers: project maintainer
---

# ADR-0005: Markdown as Universal Contract Format


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [Markdown](#markdown)
  - [YAML](#yaml)
  - [Custom DSL](#custom-dsl)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-markdown-contract`

## Context and Problem Statement

Cypilot needs a format for artifacts (PRD, DESIGN, ADR, FEATURE, etc.), workflows, templates, checklists, and rules. The format must be readable by humans, renderable by development platforms (GitHub, IDEs), and parseable by both deterministic scripts and AI agents.

## Decision Drivers

* **Universal readability** — developers already know Markdown; no learning curve
* **Platform rendering** — GitHub, GitLab, VS Code, and all major IDEs render Markdown natively
* **AI agent compatibility** — all LLMs understand Markdown structure (headings, lists, code blocks)
* **Deterministic parsing** — headings, lists, and structured patterns (IDs, checkboxes) can be parsed with regex without a full Markdown AST
* **Version control friendly** — plain text diffs work well in Git

## Considered Options

1. **Markdown** — plain text with lightweight formatting, universal platform support
2. **YAML** — structured data format with human readability
3. **Custom DSL** — purpose-built language for artifact definitions

## Decision Outcome

Chosen: **Markdown as the contract format** for all artifacts, workflows, templates, checklists, rules, and agent entry points.

### Consequences

Structured elements are embedded in standard Markdown:
- IDs use bold + backtick pattern: `**ID**: \`cpt-...\``
- Checklists use `- [ ]` / `- [x]` checkboxes
- Priorities use backtick markers: `` `p1` ``, `` `p2` ``
- TOC uses HTML comments: `<!-- toc -->` / `<!-- /toc -->`

* Good, because zero learning curve for developers
* Good, because renders natively on GitHub, GitLab, IDEs
* Good, because AI agents parse Markdown structure reliably
* Good, because deterministic validation can use line-by-line scanning with regex
* Bad, because Markdown has no formal schema — structural validation relies on conventions, not grammar
* Bad, because complex nested structures (e.g., constraint definitions) are harder to express than in YAML/TOML — mitigated by using TOML for structured data (see `cpt-cypilot-adr-toml-json-formats`)

### Confirmation

Confirmed by all architecture artifacts (PRD, DESIGN, ADR, FEATURE) being authored, reviewed, and validated as Markdown files with deterministic regex-based parsing.

## Pros and Cons of the Options

### Markdown

* Good, because zero learning curve, universal platform rendering
* Good, because AI agents parse Markdown structure reliably
* Bad, because no formal schema — relies on conventions

### YAML

* Good, because structured and schema-validatable
* Bad, because not renderable on GitHub as documentation
* Bad, because no stdlib parser in Python

### Custom DSL

* Good, because precise grammar and validation
* Bad, because learning curve for developers
* Bad, because no platform rendering support

## Traceability

- **PRD**: `cpt-cypilot-fr-core-traceability` (template structure compliance)
- **DESIGN**: `cpt-cypilot-constraint-markdown-contract`
