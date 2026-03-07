---
status: accepted
date: 2026-03-07
decision-makers: project maintainer
---

# ADR-0002: Python 3.11+ with Standard Library Only


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [Python 3.11+ stdlib-only](#python-311-stdlib-only)
  - [Python + pip dependencies](#python-pip-dependencies)
  - [Go / Rust compiled binary](#go-rust-compiled-binary)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-python-stdlib-only`

## Context and Problem Statement

Cypilot needs a runtime platform for its deterministic skill engine and CLI tool. The tool must work cross-platform (Linux, macOS, Windows), install with minimal dependencies, and avoid conflicts with project dependencies. The skill engine is copied into each project's install directory and must run without a virtual environment or pip install step.

## Decision Drivers

* **Zero dependency conflicts** — the tool lives inside user projects; any pip dependency could conflict with the project's own dependencies
* **Cross-platform** — must work identically on Linux, macOS, and Windows without platform-specific workarounds
* **Minimal installation footprint** — no `pip install` step for the skill; just copy files and run
* **`tomllib` availability** — Python 3.11+ includes `tomllib` in stdlib, which Cypilot needs for TOML config parsing (see `cpt-cypilot-adr-toml-json-formats`)

## Considered Options

1. **Python 3.11+ stdlib-only** — single-directory distribution, no external dependencies
2. **Python + pip dependencies** — standard Python with third-party packages (click, requests, etc.)
3. **Go / Rust compiled binary** — compiled single-binary distribution

## Decision Outcome

Chosen: **Python 3.11+ with standard library only** for the core skill engine. No third-party pip dependencies in core.

### Consequences

* Good, because zero dependency conflicts with user projects
* Good, because the skill is a self-contained directory of `.py` files — copy and run
* Good, because Python is already available on most developer machines and CI environments
* Good, because `tomllib` (3.11+) eliminates the need for a third-party TOML parser
* Bad, because Python is slower than compiled languages (Go, Rust) — mitigated by single-pass algorithms and ≤3s validation target
* Bad, because Python 3.11+ excludes users on older Python versions — mitigated by 3.11 being widely available since Oct 2022
* Neutral, because kit plugins (p2) MAY declare their own pip dependencies, managed separately from core

### Confirmation

Confirmed by successful deployment of stdlib-only skill engine across Linux, macOS, and Windows CI environments without any pip install step.

## Pros and Cons of the Options

### Python 3.11+ stdlib-only

* Good, because zero dependency conflicts
* Good, because `tomllib` in stdlib eliminates TOML parser dependency
* Bad, because slower than compiled languages

### Python + pip dependencies

* Good, because access to rich ecosystem (click, requests, rich)
* Bad, because dependency conflicts with user projects
* Bad, because requires pip install or virtual environment

### Go / Rust compiled binary

* Good, because fast, single-binary distribution
* Bad, because cross-compilation complexity
* Bad, because less accessible to Python-first teams

## Traceability

- **PRD**: `cpt-cypilot-nfr-simplicity` (minimal installation dependencies)
- **DESIGN**: `cpt-cypilot-constraint-python-stdlib`, `cpt-cypilot-constraint-cross-platform`
