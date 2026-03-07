---
status: accepted
date: 2026-03-07
decision-makers: project maintainer
---

# ADR-0010: SKILL.md as Single Agent Entry Point


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [SKILL.md as canonical entry point](#skillmd-as-canonical-entry-point)
  - [Per-agent native files](#per-agent-native-files)
  - [JSON/YAML manifest](#jsonyaml-manifest)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-skill-md-entry-point`

## Context and Problem Statement

Multiple AI coding assistants (Windsurf, Cursor, Claude, Copilot, OpenAI) need to discover Cypilot's capabilities — commands, workflows, conventions, and execution protocol. Each agent has its own file format for skills/rules, but the content is the same. The system needs a single source of truth for agent instructions.

## Decision Drivers

* **Single source of truth** — tool capabilities must be defined once, not duplicated per agent
* **Agent-native discovery** — each agent must find Cypilot through its native mechanism (`.windsurf/workflows/`, `.cursor/rules/`, etc.)
* **Composability** — kits must be able to extend the agent-facing documentation with kit-specific commands and workflows
* **No runtime dependency** — agents read static files; no API or service needed

## Considered Options

1. **SKILL.md as canonical entry point** — single Markdown file with per-agent generated shims
2. **Per-agent native files** — maintain separate files for each agent format directly
3. **JSON/YAML manifest** — structured capability manifest parsed by agents

## Decision Outcome

Chosen: **SKILL.md as the canonical agent entry point**, with generated per-agent shims that reference it.

### Consequences

Architecture:
- `{cypilot_path}/.gen/SKILL.md` — composed from core + kit SKILL.md extensions
- `{cypilot_path}/config/AGENTS.md` — WHEN rules for conditional loading (system prompts, kit rules)
- Per-agent entry points (`.windsurf/workflows/`, `.cursor/rules/`, etc.) — generated shims that point to SKILL.md

SKILL.md contains: command reference, workflow routing, execution protocol, and variable definitions. It is the single document an agent needs to operate Cypilot.

* Good, because one source of truth — change SKILL.md, all agents get the update
* Good, because kits extend SKILL.md through composition (kit SKILL.md → `.gen/SKILL.md`)
* Good, because agent shims are auto-generated and fully overwritten on each `cpt agents` invocation
* Bad, because SKILL.md can become large — mitigated by AGENTS.md WHEN rules for conditional loading
* Bad, because agent-specific format quirks require per-agent template maintenance

### Confirmation

Confirmed by successful agent integration across Windsurf, Cursor, Claude, and Copilot using generated shims that reference the single SKILL.md source.

## Pros and Cons of the Options

### SKILL.md as canonical entry point

* Good, because single source of truth for all agents
* Good, because kits extend via composition
* Bad, because SKILL.md can become large

### Per-agent native files

* Good, because format-native for each agent
* Bad, because N× duplication of content
* Bad, because drift between agent files

### JSON/YAML manifest

* Good, because machine-parseable
* Bad, because agents expect natural language instructions, not structured data
* Bad, because not renderable on GitHub

## Traceability

- **PRD**: `cpt-cypilot-fr-core-agents`, `cpt-cypilot-fr-core-skill-engine`
- **DESIGN**: `cpt-cypilot-component-agent-generator`, `cpt-cypilot-principle-skill-documented`
