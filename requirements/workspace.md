---
cypilot: true
type: requirement
name: Multi-Repo Workspace
version: 1.0
purpose: Define workspace federation for multi-repo traceability
---

# Cypilot Workspace Specification

---

## Table of Contents

- [Overview](#overview)
- [Design Principles](#design-principles)
- [Workspace Configuration](#workspace-configuration)
  - [Standalone File](#standalone-file)
  - [Inline in Config](#inline-in-config)
- [Source Entries](#source-entries)
- [Discovery Order](#discovery-order)
- [Path Resolution](#path-resolution)
- [Cross-Repo Traceability](#cross-repo-traceability)
- [Artifacts Registry v1.2](#artifacts-registry-v12)
- [CLI Commands](#cli-commands)
- [Backward Compatibility](#backward-compatibility)
- [Graceful Degradation](#graceful-degradation)
- [Examples](#examples)

---

## Overview

Cypilot workspaces provide a **federation layer** for multi-repo projects. Each repo keeps its own independent adapter. The workspace configuration maps named sources (repos) and their roles, enabling cross-repo artifact traceability without merging adapters.

**Use cases:**
- PM defines PRDs in a docs repo, design in another, code in yet another
- Shared kit packages live in a separate repo
- Mono-repo with submodules (existing pattern) AND multi-repo with sibling directories
- Working from repo1 while referencing artifacts in repo2

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **cwd determines primary** | The primary source MUST always be determined by which repo contains the current working directory. No `primary` field. |
| **Federation, not merging** | Each repo MUST own its adapter config. Implementations MUST NOT merge rules or templates across repos. |
| **Opt-in** | Absence of workspace config MUST produce exact current single-repo behavior. Zero changes for existing setups. |
| **Local paths only** | Source paths MUST be local filesystem only. Implementations MUST NOT resolve Git URLs at runtime. |
| **Graceful degradation** | Missing source repos MUST emit warnings but MUST NOT block operations on available sources. |

---

## Workspace Configuration

### Standalone File

File: `.cypilot-workspace.toml`

Can be placed at a **super-root** (parent directory containing multiple repos) or anywhere reachable by the discovery algorithm.

```toml
version = "1.0"

[sources.docs-repo]
path = "../docs-repo"
adapter = "cypilot"
role = "artifacts"

[sources.code-repo]
path = "../code-repo"
adapter = ".bootstrap"
role = "codebase"

[sources.shared-kits]
path = "../shared-kits"
role = "kits"

[traceability]
cross_repo = true
resolve_remote_ids = true
```

### Inline in Config

A repo can declare workspace participation from within its own `config/core.toml`.

**Reference to external workspace file (in core.toml):**
```toml
workspace = "../.cypilot-workspace.toml"
```

**Inline workspace definition (in core.toml):**
```toml
[workspace.sources.docs]
path = "../docs-repo"

[workspace.sources.shared-kits]
path = "../shared-kits"
role = "kits"
```

---

## Source Entries

Each source entry has the following fields:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `path` | string | Yes | — | Local filesystem path, resolved relative to workspace file location |
| `adapter` | string | No | _(omitted)_ | Path to adapter directory within the source repo |
| `role` | string | No | `"full"` | Constrains what the source contributes |

### Roles

| Role | Contributes |
|------|-------------|
| `artifacts` | Only artifact documents for cross-referencing |
| `codebase` | Only source code directories |
| `kits` | Only kit template packages |
| `full` | Everything (artifacts + codebase + kits) |

---

## Discovery Order

When Cypilot initializes, workspace configuration is discovered in this order:

1. **Check `workspace` key** in `config/core.toml` (discovered via AGENTS.md `cypilot_path`)
   - If string → treat as path to external `.cypilot-workspace.toml` (resolved relative to project root)
   - If table → treat as inline workspace definition (source paths resolve relative to project root)
2. **Walk up** from project root looking for `.cypilot-workspace.toml`
3. **Check parent directory** of project root for `.cypilot-workspace.toml`

If no workspace configuration is found, Cypilot operates in single-repo mode (backward compatible).

---

## Path Resolution

- **External workspace file reference** (`workspace = "../.cypilot-workspace.toml"` in core.toml): the string is resolved **relative to the project root** (consistent with how other core.toml path values work)
- **Source `path` values** in a **standalone** `.cypilot-workspace.toml`: resolved **relative to the workspace file's parent directory**
- **Source `path` values** in an **inline** `[workspace]` definition in core.toml: resolved **relative to the project root**
- Artifact `path` values with a `source` field are resolved relative to the named source's root
- Artifact `path` values without a `source` field resolve locally (backward compatible)
- Kit `path` values with a `source` field are resolved relative to the named source's root

---

## Cross-Repo Traceability

When workspace is active and `traceability.cross_repo` is true:

- `validate` collects artifact IDs from **all** reachable workspace sources, building a union set for cross-reference resolution
- `where-defined` and `where-used` scan artifacts from **all** reachable sources
- `list-ids` iterates artifacts from all sources (filterable with `--source`)
- Code traceability accepts `@cpt-*` markers referencing IDs defined in remote artifacts

Use `validate --local-only` to restrict validation to the current repo only.

---

## Artifacts Registry v1.2

Artifacts registry v1.2 (`artifacts.toml`) adds an optional `source` field to artifacts, codebase entries, and kits:

```toml
version = "1.2"

[[systems]]
name = "MyApp"
slug = "myapp"
kit = "shared-sdlc"

[[systems.artifacts]]
path = "architecture/DESIGN.md"
kind = "DESIGN"
traceability = "FULL"

[[systems.artifacts]]
path = "requirements/PRD.md"
kind = "PRD"
source = "docs-repo"

[[systems.codebase]]
name = "Backend"
path = "src"
extensions = [".rs"]

[[systems.codebase]]
name = "Frontend"
path = "src"
extensions = [".ts"]
source = "frontend-repo"

[kits.shared-sdlc]
format = "Cypilot"
path = "kits/sdlc"
source = "shared-kits"
```

When `source` is absent, paths resolve locally (backward compatible). v1.0/v1.1 registries remain fully valid.

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `workspace-init` | Initialize workspace: scan sibling dirs, generate `.cypilot-workspace.toml` |
| `workspace-init --inline` | Initialize workspace inline in `config/core.toml` |
| `workspace-init --dry-run` | Preview without writing files |
| `workspace-add --name N --path P` | Add source to standalone workspace file |
| `workspace-add-inline --name N --path P` | Add source inline to `config/core.toml` |
| `workspace-info` | Display workspace config and per-source status |
| `validate --local-only` | Validate without cross-repo ID resolution |
| `list-ids --source <name>` | Filter IDs by workspace source |

---

## Backward Compatibility

- No `.cypilot-workspace.toml` and no `[workspace]` in core.toml = **exact current behavior**
- v1.0/v1.1 `artifacts.toml` without `source` fields = **no change**
- All workspace imports are lazy (inside functions), matching existing patterns
- The global context can be either `CypilotContext` or `WorkspaceContext`; `is_workspace()` tests this
- Existing mono-repo setups are completely unaffected

---

## Graceful Degradation

When a source repo path does not exist on disk:

1. **Warning** is emitted in `workspace-info` output
2. Source is marked as `reachable: false`
3. All operations continue with available sources
4. Cross-repo IDs from missing sources are simply unavailable
5. No error exit codes — missing sources are expected (repos may not always be cloned)

---

## Examples

### Scenario: Working from code-repo referencing docs-repo

```text
workspace/
├── docs-repo/
│   ├── AGENTS.md              (cypilot_path = "cypilot")
│   └── cypilot/
│       └── config/
│           └── artifacts.toml
├── code-repo/                  ← cwd
│   ├── AGENTS.md              (cypilot_path = ".bootstrap")
│   ├── .bootstrap/
│   │   └── config/
│   │       ├── core.toml      ([workspace.sources.docs] path = "../docs-repo")
│   │       └── artifacts.toml
│   └── src/
└── shared-kits/
    └── kits/sdlc/
```

Running `cypilot validate` from `code-repo/` will:
1. Load primary context from `code-repo/.bootstrap`
2. Detect workspace from `config/core.toml`
3. Load `docs-repo` artifacts for cross-repo ID resolution
4. Accept `@cpt-*` markers referencing IDs defined in `docs-repo`

### Scenario: Super-root workspace

```text
parent/
├── .cypilot-workspace.toml
├── frontend/
│   ├── AGENTS.md
│   ├── .cypilot/
│   └── src/
├── backend/
│   ├── AGENTS.md
│   ├── .bootstrap/
│   └── src/
└── docs/
    ├── AGENTS.md
    ├── cypilot/
    └── architecture/
```

Running `cypilot workspace-init` from `parent/frontend/` will discover `backend` and `docs` as siblings and generate the workspace config.
