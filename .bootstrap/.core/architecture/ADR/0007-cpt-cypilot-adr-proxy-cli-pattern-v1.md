---
status: accepted
date: 2026-03-07
decision-makers: project maintainer
---

# ADR-0007: Stateless Proxy Pattern for Global CLI


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [Stateless proxy](#stateless-proxy)
  - [Monolith](#monolith)
  - [Client-server](#client-server)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-proxy-cli-pattern`

## Context and Problem Statement

Cypilot's global CLI must work both inside projects (using the project-installed skill version) and outside projects (using a cached version). The tool must support version coexistence — different projects can have different Cypilot versions — and updates must not break existing projects.

## Decision Drivers

* **Version coexistence** — projects must be able to pin their Cypilot version independently
* **Zero built-in logic** — if the proxy contained commands, it would need to stay in sync with the skill version, creating coupling
* **Offline capability** — once installed, the tool must work without network access
* **Non-blocking updates** — version checks must not slow down command execution

## Considered Options

1. **Stateless proxy** — global CLI is a thin shell that delegates everything to project or cached skill
2. **Monolith** — global CLI contains all commands; project install is optional
3. **Client-server** — global daemon with project-specific plugins

## Decision Outcome

Chosen: **Stateless proxy pattern**. The global CLI (`cypilot` / `cpt`) contains zero command logic. On every invocation it: (1) ensures a cached skill bundle exists, (2) resolves whether to use the project-installed or cached skill, (3) forwards the command. Version checks run in the background without blocking.

### Consequences

* Good, because each project controls its own skill version — no forced upgrades
* Good, because the proxy never needs updating when commands change
* Good, because offline-first — cache is populated once, then everything works locally
* Bad, because first-ever invocation requires network access to populate the cache
* Bad, because two copies of the skill exist (cache + project) — mitigated by small footprint (~500KB)

### Confirmation

Confirmed by proxy CLI containing zero command handlers and successfully forwarding all commands to both project-installed and cached skill engines.

## Pros and Cons of the Options

### Stateless proxy

* Good, because version coexistence — each project controls its own skill version
* Good, because proxy never needs updating when commands change
* Bad, because first invocation requires network to populate cache

### Monolith

* Good, because simpler single binary
* Bad, because version coupling — global CLI must match project expectations
* Bad, because forced upgrades break existing projects

### Client-server

* Good, because shared state and caching
* Bad, because daemon complexity and resource usage
* Bad, because violates offline-first requirement

## Traceability

- **PRD**: `cpt-cypilot-fr-core-installer`
- **DESIGN**: `cpt-cypilot-component-cli-proxy`
- **Depends on**: `cpt-cypilot-adr-pipx-distribution` (global installation)
