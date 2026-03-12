---
status: accepted
date: 2026-03-12
decision-makers: ainetx
---

# ADR-0015: Eliminate Version Duplication with Split Versioning Model


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [Split model — `pyproject.toml` for proxy, `git describe` for skill engine](#split-model--pyprojecttoml-for-proxy-git-describe-for-skill-engine)
  - [`setuptools-scm` for both components](#setuptools-scm-for-both-components)
  - [Single `VERSION` file at repo root](#single-version-file-at-repo-root)
  - [Status quo with automated bump tooling](#status-quo-with-automated-bump-tooling)
- [More Information](#more-information)
  - [Version Resolution Chain](#version-resolution-chain)
  - [Cache Version Storage](#cache-version-storage)
  - [Whatsnew Comparison](#whatsnew-comparison)
  - [Tag Naming Convention](#tag-naming-convention)
  - [Impact on Existing Files](#impact-on-existing-files)
  - [Migration Plan](#migration-plan)
  - [Not Applicable](#not-applicable)
  - [Review Cadence](#review-cadence)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-github-based-versioning`
## Context and Problem Statement

Cypilot has two independently versioned components in one repository: the **proxy** (pip package, installed via pipx) and the **skill engine** (Python scripts, run directly from git checkout or cache). Each component's version is currently hardcoded in multiple files that must be kept in sync manually.

**Proxy** duplicates its version in `pyproject.toml` and `src/cypilot_proxy/__init__.py`. When a user runs `pipx install git+https://...@v3.0.9-beta`, the installed version comes from `pyproject.toml` — not the git tag — so the tag and the package version can diverge.

**Skill engine** hardcodes `__version__` in `skills/cypilot/scripts/cypilot/__init__.py`. This file is not a pip package — it runs directly from a git checkout or from the `~/.cypilot/cache/` copy. The hardcoded string must be bumped manually on every release.

A CI check (`scripts/check_versions.py`) enforces cross-file consistency, but manual bumps are error-prone, create noise in diffs, and block PRs when forgotten.

## Decision Drivers

* Proxy version is duplicated in `pyproject.toml` and `src/cypilot_proxy/__init__.py`
* Skill engine version is hardcoded in `skills/cypilot/scripts/cypilot/__init__.py`
* Manual bumps are error-prone and create merge conflicts in parallel branches
* Proxy and skill engine are versioned independently — they have different release cadences
* `whatsnew.toml` comparison requires reliable version comparison between installed and cached states
* Self-hosted repos (`--source .`) need skill version derivation without GitHub releases
* ADR-0002 (`cpt-cypilot-adr-python-stdlib-only`) mandates zero third-party deps for the skill engine runtime

## Considered Options

* **Option 1: Split model — `pyproject.toml` for proxy, `git describe` for skill engine**
* **Option 2: `setuptools-scm` for both components**
* **Option 3: Single `VERSION` file at repo root**
* **Option 4: Status quo with automated bump tooling**

## Decision Outcome

Chosen option: **"Split model — `pyproject.toml` for proxy, `git describe` for skill engine"**, because each component uses its natural version source with zero duplication, zero new dependencies, and full compatibility with existing tooling.

- **Proxy**: `pyproject.toml` is the single source of truth. Runtime reads via `importlib.metadata.version("cypilot")`. No `__version__` hardcoded in `__init__.py`.
- **Skill engine**: Git tags (prefixed `skill-v*`) are the single source of truth. Runtime reads via `git describe --tags --match "skill-v*"`. No `__version__` hardcoded in `__init__.py`.

### Consequences

* Good, because each component has exactly one version source — no duplication
* Good, because no new build or runtime dependencies (stdlib only)
* Good, because skill dev versions automatically include commit distance and hash (`skill-v3.0.13-beta-3-gabc1234`)
* Good, because `check_versions.py` simplifies — proxy check becomes `pyproject.toml` ↔ `importlib.metadata`, skill check becomes bootstrap sync only
* Good, because proxy versioning stays compatible with standard Python packaging (`pip`, `pipx`)
* Bad, because CI needs `fetch-depth: 0` for skill version (shallow clones lack tags)
* Bad, because `whatsnew.toml` comparison needs a base-tag normalization function to strip dev suffixes
* Bad, because proxy version still requires a manual bump in `pyproject.toml` (one file, not two)

### Confirmation

Confirmed when:

- `src/cypilot_proxy/__init__.py` uses `importlib.metadata.version("cypilot")` instead of hardcoded `__version__`
- `skills/cypilot/scripts/cypilot/__init__.py` uses `git describe --tags --match "skill-v*"` instead of hardcoded `__version__`
- `pyproject.toml` remains the single version source for the proxy package
- `cpt info` correctly reports the skill version in all scenarios: tagged commit, post-tag dev commit, and cached copy
- `whatsnew.toml` entries display correctly when upgrading from one skill tag to another
- CI passes with `fetch-depth: 0`

## Pros and Cons of the Options

### Split model — `pyproject.toml` for proxy, `git describe` for skill engine

Proxy version lives in `pyproject.toml` (standard pip packaging). Skill engine version derived from prefixed git tags at runtime (`git describe --tags --match "skill-v*"`). Runtime reads: proxy via `importlib.metadata`, skill via subprocess to git.

* Good, because each component uses its natural version mechanism
* Good, because zero new dependencies — `importlib.metadata` and `subprocess` are stdlib
* Good, because proxy stays fully compatible with standard Python packaging
* Good, because skill dev versions are automatically unique: `skill-v3.0.13-beta-3-gabc1234`
* Good, because independent release cadences with no coupling
* Neutral, because proxy still requires a manual bump — but in one file only (`pyproject.toml`)
* Bad, because CI needs `fetch-depth: 0` for skill version tags
* Bad, because skill version unavailable without git (cached copies read version from `meta.toml`, written during `cpt update`)

### `setuptools-scm` for both components

Use `setuptools-scm` to derive both versions from git tags at build time.

* Good, because both versions derived from git tags — zero hardcoded strings
* Good, because mature, widely-adopted standard (used by pip, pytest)
* Bad, because new build dependency (`setuptools-scm`)
* Bad, because PEP 440 format (`3.0.12b0.dev3+gabc1234`) differs from project's `v3.0.12-beta` convention — requires custom `version_scheme`
* Bad, because shallow clones break builds (no tags → build failure)
* Bad, because editable installs freeze version at install time
* Bad, because skill engine is not a pip package — setuptools-scm integration is unnatural

### Single `VERSION` file at repo root

One plain-text file (`VERSION`) containing the version string. All other files read from it.

* Good, because simple to understand and implement
* Good, because no new build dependencies
* Good, because works without git (tarball distributions)
* Bad, because still requires a manual bump (just in one file instead of three)
* Bad, because merge conflicts still possible on the VERSION file in parallel branches
* Bad, because no automatic dev-version differentiation between commits
* Bad, because one VERSION file cannot serve two independently versioned components

### Status quo with automated bump tooling

Keep hardcoded versions but add pre-commit hooks or CI actions to automate bumps.

* Good, because no architectural change needed
* Good, because no new dependencies
* Bad, because automation adds complexity (bump scripts, CI config, pre-commit hooks)
* Bad, because version bumps still appear in diffs (even if automated)
* Bad, because doesn't solve the fundamental problem of multiple sources of truth
* Bad, because merge conflicts on version strings in parallel branches remain

## More Information

### Version Resolution Chain

**Proxy** (pip package):

| Context | Resolution method | Example output |
|---------|-------------------|----------------|
| `pipx install cypilot` | `importlib.metadata.version("cypilot")` | `3.0.9-beta` |
| `pipx install git+https://...` | `importlib.metadata.version("cypilot")` (from `pyproject.toml`) | `3.0.9-beta` |
| Dev (editable install) | `importlib.metadata.version("cypilot")` | `3.0.9-beta` |

**Skill engine** (git-based):

| Context | Resolution method | Example output |
|---------|-------------------|----------------|
| Dev (on tag) | `git describe --tags --match "skill-v*"` | `skill-v3.0.13-beta` |
| Dev (after tag) | `git describe --tags --match "skill-v*"` | `skill-v3.0.13-beta-3-gabc1234` |
| Dev (no tags) | `git describe --tags --always` | `abc1234` |
| `cpt update --source <dir>` | `git describe` in source dir | `skill-v3.0.13-beta` |
| `cpt update` (from GitHub) | Tag from release URL | `skill-v3.0.13-beta` |
| Cached copy (no git) | Read `version` from `~/.cypilot/cache/meta.toml` | `v3.0.13-beta` |
| Legacy cached copy (no git, no `meta.toml`) | Read `__version__` from `__init__.py` | `v3.0.12-beta` |

### Cache Version Storage

During `cpt update`, the resolved skill version is written to `~/.cypilot/cache/meta.toml`:

```toml
version = "v3.0.13-beta"
cached_at = "2026-03-12T12:00:00Z"
source = "github"  # or "local", "url"
```

`meta.toml` is the **authoritative version source** for cached copies (where `.git` is absent). The skill engine version fallback chain is:

1. `git describe --tags --match "skill-v*"` — if `.git` is present (dev checkout)
2. `meta.toml` `version` field — if running from cache (`~/.cypilot/cache/`)
3. `__version__` from `__init__.py` — legacy fallback for pre-migration cached copies (removed after one release cycle)
4. `"unknown"` — if none of the above are available (should not occur in normal operation)

### Whatsnew Comparison

Base-tag normalization strips dev suffixes for whatsnew lookup:

- `v3.0.12-beta` → `v3.0.12-beta` (no change)
- `v3.0.12-beta-3-gabc1234` → `v3.0.12-beta` (strip `-N-gHASH`)

Whatsnew entries between `core.toml` version (installed) and `meta.toml` version (cached) are displayed during `cpt update`.

### Tag Naming Convention

Two independent tag namespaces prevent `git describe` from matching the wrong component:

| Component | Tag format | Example |
|-----------|-----------|----------|
| Skill engine | `skill-v{major}.{minor}.{patch}-{pre}` | `skill-v3.0.13-beta` |
| Proxy | Standard semver (or no tag — version in `pyproject.toml`) | N/A |

Skill engine strips the `skill-` prefix when displaying: `skill-v3.0.13-beta` → `v3.0.13-beta`.

### Impact on Existing Files

| File | Current | After |
|------|---------|-------|
| `skills/cypilot/scripts/cypilot/__init__.py` | `__version__ = "v3.0.12-beta"` | `__version__` computed from `git describe --tags --match "skill-v*"` |
| `src/cypilot_proxy/__init__.py` | `__version__ = "v3.0.8-beta"` | `__version__ = importlib.metadata.version("cypilot")` |
| `pyproject.toml` | `version = "3.0.8-beta"` | `version = "3.0.9-beta"` (single source, no change in format) |
| `scripts/check_versions.py` | Cross-file sync (proxy ↔ `__init__`) + bootstrap sync | Bootstrap sync only; proxy `__init__` reads from metadata |

### Migration Plan

Transition from hardcoded versions to the split model:

1. **Create initial skill tag**: Tag current HEAD as `skill-v3.0.13-beta` (first `skill-v*` tag). Existing `v*` tags remain untouched for git history.
2. **Update skill `__init__.py`**: Replace hardcoded `__version__` with `git describe --tags --match "skill-v*"` + fallback to `meta.toml`. Ship in same commit as the tag.
3. **Update proxy `__init__.py`**: Replace hardcoded `__version__` with `importlib.metadata.version("cypilot")`. No tag needed — `pyproject.toml` already exists.
4. **Update `cpt update`**: Write resolved skill version to `meta.toml` during cache step.
5. **Simplify `check_versions.py`**: Remove proxy cross-file sync check (now reads metadata). Keep bootstrap sync check.
6. **CI**: Add `fetch-depth: 0` to all GitHub Actions workflows that run skill engine commands.

During the transition window (after step 1, before users update):

- Users on old cached copies still have hardcoded `__version__` — works as before.
- Users who run `cpt update` get the new skill engine with `meta.toml` fallback — works because `cpt update` writes `meta.toml`.
- `git describe --match "skill-v*"` works immediately because the initial tag exists.
- **Whatsnew during first update**: The new skill engine reads the OLD installed version via legacy `__version__` fallback (step 3 in the fallback chain). After `cpt update` completes, `meta.toml` exists and subsequent updates use it. The legacy fallback can be removed after one release cycle.

### Not Applicable

- **PERF**: Not applicable — versioning is a metadata concern with no performance impact
- **SEC**: Not applicable — no user data, authentication, or network security involved
- **REL**: Not applicable — local development tool, no SLAs or production uptime concerns
- **DATA**: Not applicable — no persistent data storage or migrations involved
- **INT**: Not applicable — no external API contracts affected
- **OPS**: Not applicable — no deployed services; only local CLI tool
- **TEST**: Addressed — `check_versions.py` simplifies to bootstrap sync only (see Impact on Existing Files)
- **BIZ**: Not applicable — internal tooling decision with no external business impact
- **UX**: Addressed — `cpt info` version display format unchanged for end users; only the source of the value changes
- **COMPL**: Not applicable — no regulated industry requirements

### Review Cadence

Revisit this decision if:

- Proxy moves to a separate repository (split model becomes unnecessary)
- A third independently-versioned component is added to the monorepo
- Python packaging standards change significantly (e.g., PEP replacing `importlib.metadata`)

## Traceability

- **PRD**: [PRD.md](../PRD.md)
- **DESIGN**: [DESIGN.md](../DESIGN.md)

This decision directly addresses the following requirements or design elements:

* `cpt-cypilot-adr-python-stdlib-only` (ADR-0002) — both components remain stdlib-only at runtime; no new dependencies
* `cpt-cypilot-adr-pipx-distribution` (ADR-0003) — proxy distribution via pipx unchanged; `pyproject.toml` remains version source
* `cpt-cypilot-feature-developer-experience` — `cpt info` version display and `whatsnew.toml` comparison affected
