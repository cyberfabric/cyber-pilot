---
status: accepted
date: 2026-03-07
decision-makers: project maintainer
---

# ADR-0003: pipx as Global CLI Distribution Mechanism


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [pipx](#pipx)
  - [pip install --user](#pip-install-user)
  - [Platform package managers (Homebrew / apt)](#platform-package-managers-homebrew-apt)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-pipx-distribution`

## Context and Problem Statement

Cypilot needs a global installation mechanism that makes the CLI available system-wide as `cypilot` and `cpt` commands. The installation must be a single command, isolated from project dependencies, and work across platforms.

## Decision Drivers

* **Single-command install** — users expect `install X` and done
* **Dependency isolation** — global tool must not pollute or conflict with project virtualenvs
* **Python ecosystem** — core is Python (see `cpt-cypilot-adr-python-stdlib-only`), so Python-native distribution is natural
* **No system-level dependencies** — avoid requiring Homebrew, apt, or platform-specific package managers

## Considered Options

1. **pipx** — Python CLI installer with automatic isolation
2. **pip install --user** — global Python install without isolation
3. **Homebrew / apt / platform packages** — OS-specific package managers
4. **curl | sh installer script** — download and install manually
5. **npm / cargo** — cross-platform package managers from other ecosystems

## Decision Outcome

Chosen: **pipx** (`pipx install git+https://github.com/cyberfabric/cyber-pilot.git`).

### Consequences

* Good, because single command, automatic virtual environment isolation
* Good, because Python-native — no cross-ecosystem bridges
* Good, because works on Linux, macOS, Windows
* Good, because automatic PATH management for `cypilot` and `cpt` entry points
* Bad, because requires pipx to be pre-installed (mitigated: Python 3.12+ includes `pipx` via `pip install pipx`)
* Bad, because less discoverable than `brew install` or `npm install -g`
* Neutral, because pipx is recommended but not required — manual installation (clone + add to PATH) remains possible

### Confirmation

Confirmed by successful `pipx install` on Linux, macOS, and Windows with automatic `cypilot` and `cpt` entry point registration.

## Pros and Cons of the Options

### pipx

* Good, because single-command install with automatic isolation
* Good, because Python-native, works cross-platform
* Bad, because requires pipx pre-installed

### pip install --user

* Good, because no extra tool needed
* Bad, because no dependency isolation — pollutes global site-packages

### Platform package managers (Homebrew / apt)

* Good, because native discoverability (`brew install`)
* Bad, because per-platform maintenance burden
* Bad, because slower release cycle

## Traceability

- **PRD**: `cpt-cypilot-fr-core-installer`
- **DESIGN**: `cpt-cypilot-component-cli-proxy`
- **Depends on**: `cpt-cypilot-adr-python-stdlib-only`
