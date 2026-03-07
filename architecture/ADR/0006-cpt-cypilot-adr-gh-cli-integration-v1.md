---
status: accepted
date: 2026-03-07
decision-makers: project maintainer
---

# ADR-0006: GitHub CLI (`gh`) for GitHub Integration


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [`gh` CLI](#gh-cli)
  - [Direct HTTP (urllib)](#direct-http-urllib)
  - [PyGithub / octokit](#pygithub-octokit)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-gh-cli-integration`

## Context and Problem Statement

Cypilot's SDLC kit needs to fetch PR diffs, metadata, comments, and CI status from GitHub for PR review and status workflows. The integration must work without adding HTTP client dependencies to the stdlib-only core.

## Decision Drivers

* **No pip dependencies** — core is stdlib-only (see `cpt-cypilot-adr-python-stdlib-only`); adding `requests` or `httpx` would violate this constraint
* **Authentication delegation** — GitHub authentication (tokens, SSH, OAuth) is complex; delegating to an existing tool avoids reimplementing it
* **API abstraction** — GitHub REST/GraphQL API changes are absorbed by `gh` CLI updates, not Cypilot code changes
* **Developer familiarity** — many developers already have `gh` installed and authenticated

## Considered Options

1. **`gh` CLI** — subprocess calls to GitHub's official CLI
2. **Direct HTTP** — `urllib.request` (stdlib) to GitHub REST API
3. **PyGithub / octokit** — third-party Python GitHub client

## Decision Outcome

Chosen: **`gh` CLI via subprocess** (`gh pr view`, `gh pr diff`, `gh api`).

### Consequences

* Good, because zero pip dependencies — uses subprocess only
* Good, because authentication is fully delegated to `gh auth`
* Good, because `gh` handles pagination, rate limiting, and API versioning
* Good, because `gh` is optional — Cypilot works without it; only PR workflows require it
* Bad, because `gh` must be pre-installed and authenticated — mitigated by `cpt doctor` checking availability
* Bad, because subprocess parsing is less robust than a typed API client — mitigated by using `--json` flag for structured output

### Confirmation

Confirmed by successful PR review and status workflows using `gh pr view --json` and `gh pr diff` across multiple repositories.

## Pros and Cons of the Options

### `gh` CLI

* Good, because zero pip dependencies, authentication delegated
* Good, because handles pagination and rate limiting
* Bad, because requires pre-installation

### Direct HTTP (urllib)

* Good, because no external tool dependency
* Bad, because must implement auth, pagination, rate limiting manually
* Bad, because token management complexity

### PyGithub / octokit

* Good, because typed API, rich features
* Bad, because pip dependency — violates stdlib-only constraint

## Traceability

- **PRD**: PR review and PR status capabilities (SDLC kit)
- **DESIGN**: `cpt-cypilot-component-kit-manager` (kits provide PR workflows)
- **Depends on**: `cpt-cypilot-adr-python-stdlib-only` (no pip dependencies constraint)
