---
cypilot: true
type: requirement
name: Multi-Repo Workspace
version: 1.0
purpose: Define workspace federation for multi-repo traceability
---

# Cypilot Workspace Specification

<!-- toc -->

- [Overview](#overview)
- [Design Principles](#design-principles)
- [Workspace Configuration](#workspace-configuration)
  - [Standalone File](#standalone-file)
  - [Inline in Config](#inline-in-config)
- [Source Entries](#source-entries)
  - [Roles](#roles)
- [Discovery Order](#discovery-order)
- [Path Resolution](#path-resolution)
- [Cross-Repo Traceability](#cross-repo-traceability)
  - [Traceability Settings](#traceability-settings)
  - [Artifact Path Resolution Contract](#artifact-path-resolution-contract)
  - [Scan Warning Logging](#scan-warning-logging)
- [Artifacts Registry v1.2](#artifacts-registry-v12)
- [CLI Commands](#cli-commands)
  - [Syncing Sources](#syncing-sources)
  - [Removing Sources](#removing-sources)
  - [Switching Workspace Type](#switching-workspace-type)
- [Backward Compatibility](#backward-compatibility)
- [Graceful Degradation](#graceful-degradation)
- [Git URL Sources](#git-url-sources)
- [Cross-Repo Editing](#cross-repo-editing)
- [Examples](#examples)
  - [Scenario: Working from code-repo referencing docs-repo](#scenario-working-from-code-repo-referencing-docs-repo)
  - [Scenario: Parent workspace with nested repos](#scenario-parent-workspace-with-nested-repos)

<!-- /toc -->

---

## Overview

Cypilot workspaces provide a **federation layer** for multi-repo projects. Each repo keeps its own independent adapter.
The workspace configuration maps named sources (repos) and their roles, enabling cross-repo artifact traceability
without merging adapters.

**Project root**: the repository root directory that contains the Cypilot adapter directory (e.g., the directory containing `.bootstrap/` or `cypilot/`). All adapter-relative paths resolve from this directory.

**Use cases:**

- PM defines PRDs in a docs repo, design in another, code in yet another
- Shared kit packages live in a separate repo
- Mono-repo with submodules (existing pattern) AND multi-repo with nested sub-directories
- Working from a parent directory while referencing artifacts in nested repos

---

## Design Principles

| Principle                                  | Description                                                                                                                                                                     |
|--------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **cwd determines primary**                 | The primary source MUST always be determined by which repo contains the current working directory. No `primary` field.                                                          |
| **Federation with remote adapter context** | Each repo MUST own its adapter config. When editing files in a remote source that has its own Cypilot adapter, the remote source's adapter rules/templates MUST be applied — not the primary repo's adapter. Sources without an adapter fall back to the primary repo's adapter context. |
| **Opt-in**                                 | Absence of workspace config MUST produce exact current single-repo behavior. Zero changes for existing setups.                                                                  |
| **Local paths first**                      | Inline workspace config (`core.toml`) source paths MUST be local filesystem only. Standalone workspace configs support both local paths and Git URL sources.                    |
| **Git URL sources**                        | Standalone workspace config (`.cypilot-workspace.toml`) MUST support Git URL sources with working directory configuration, namespace resolution rules, and branch pinning.      |
| **Graceful degradation**                   | Missing source repos MUST emit warnings but MUST NOT block operations on available sources.                                                                                     |

---

## Workspace Configuration

### Standalone File

File: `.cypilot-workspace.toml`

Can be placed at the **project root** (directory containing nested repo sub-directories) or anywhere reachable by the
discovery algorithm.

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

Each source entry has the following fields. The `adapter` field refers to the source's **Cypilot directory** — the directory containing `.core/`, `.gen/`, and `config/` (e.g., `cypilot/`, `.bootstrap/`). When omitted, Cypilot auto-discovers it via the source's `AGENTS.md`.

| Field    | Type   | Required                          | Default     | Description                                                                                                     |
|----------|--------|-----------------------------------|-------------|-----------------------------------------------------------------------------------------------------------------|
| `path`   | string | Yes (unless `url` is set)         | —           | Local filesystem path, resolved relative to workspace file location. Takes precedence over `url` when both set. |
| `url`    | string | No (standalone workspace only)    | —           | Git remote URL (HTTPS or SSH). Only supported in standalone `.cypilot-workspace.toml`, not inline config.       |
| `branch` | string | No (only with `url`)              | _(omitted)_ | Git branch/ref to checkout. Only valid on URL sources; rejected on path-only sources. Defaults to the remote repository's default branch when omitted. |
| `adapter`| string | No                                | _(omitted)_ | Path to adapter directory within the source repo.                                                               |
| `role`   | string | No                                | `"full"`    | Constrains what the source contributes.                                                                         |

### Roles

| Role        | Contributes                                   |
|-------------|-----------------------------------------------|
| `artifacts` | Only artifact documents for cross-referencing |
| `codebase`  | Only source code directories                  |
| `kits`      | Only kit template packages                    |
| `full`      | Everything (artifacts + codebase + kits)      |

---

## Discovery Order

When Cypilot initializes, workspace configuration is discovered in the following order:

1. **Check `workspace` key** in `config/core.toml` (discovered via AGENTS.md `cypilot_path`):
   - If string → treat as path to external `.cypilot-workspace.toml` (resolved relative to project root)
   - If table → treat as inline workspace definition (source paths resolve relative to project root)
2. **If no `workspace` key** (or `core.toml` not found) → check for a standalone `.cypilot-workspace.toml` at the **project root**
3. **If neither is found** → single-repo mode (backward compatible)

No implicit parent directory traversal — discovery is limited to the project root.

---

## Path Resolution

- **External workspace file reference** (`workspace = "../.cypilot-workspace.toml"` in core.toml): the string is
  resolved **relative to the project root** (consistent with how other core.toml path values work)
- **Source `path` values** in a **standalone** `.cypilot-workspace.toml`: resolved **relative to the workspace file's
  parent directory**
- **Source `path` values** in an **inline** `[workspace]` definition in core.toml: resolved **relative to the project
  root**
- Artifact `path` values with a `source` field are resolved relative to the named source's root
- Artifact `path` values without a `source` field resolve locally (backward compatible)
- Kit `path` values with a `source` field are resolved relative to the named source's root

---

## Cross-Repo Traceability

When workspace is active and `traceability.cross_repo` is true:

- `validate` collects artifact IDs from **all** reachable workspace sources, building a union set for cross-reference
  resolution
- `where-defined` and `where-used` scan artifacts from **all** reachable sources
- `list-ids` iterates artifacts from all sources (filterable with `--source`)
- Code traceability accepts `@cpt-*` markers referencing IDs defined in remote artifacts

Use `validate --local-only` to restrict validation to the current repo only.

### Traceability Settings

| Setting              | Default | Description                                              |
|----------------------|---------|----------------------------------------------------------|
| `cross_repo`         | `true`  | Enable cross-repo ID collection and reference resolution |
| `resolve_remote_ids` | `true`  | Expand remote source artifact IDs into the union set     |

Both `cross_repo` **and** `resolve_remote_ids` must be true for remote artifact IDs to be included. Setting
`resolve_remote_ids = false` while keeping `cross_repo = true` allows workspace-aware path resolution without pulling in
remote IDs.

### Artifact Path Resolution Contract

`resolve_artifact_path` routes artifact paths through workspace sources:

- **No `source` field** → path resolves relative to the local project root (backward compatible)
- **`source` field set, source reachable** → path resolves relative to the named source's root directory
- **`source` field set, source missing or unreachable** → returns `None` (no silent fallback to local)

When an artifact's path cannot be resolved (returns `None`), callers skip that artifact. This prevents stale local files
from masquerading as remote artifacts.

### Scan Warning Logging

When scanning artifact files for definition IDs fails (e.g., malformed file, permission error), a warning is emitted to
stderr rather than silently swallowing the error:

```text
Warning: failed to scan IDs from <path>: <reason>
```

Operations continue with the IDs that were successfully collected.

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

| Command                                  | Description                                                                    |
|------------------------------------------|--------------------------------------------------------------------------------|
| `workspace-init`                         | Initialize workspace: scan nested sub-dirs, generate `.cypilot-workspace.toml` |
| `workspace-init --inline`                | Initialize workspace inline in `config/core.toml`                              |
| `workspace-init --dry-run`               | Preview without writing files                                                  |
| `workspace-add --name N --path P`        | Add source to workspace (auto-detects standalone vs inline)                    |
| `workspace-add --name N --url U`           | Add Git URL source to standalone workspace                                     |
| `workspace-add --inline --name N --path P` | Force add source inline to `config/core.toml`                                  |
| `workspace-add --force --name N ...`       | Overwrite existing source with the same name                                   |
| `workspace-info`                         | Display workspace config and per-source status                                 |
| `workspace-sync`                         | Fetch and update worktrees for all Git URL sources                             |
| `workspace-sync --source <name>`         | Sync a single Git URL source                                                   |
| `workspace-sync --dry-run`               | Preview sync operations without network access                                 |
| `workspace-sync --force`                 | Sync discarding uncommitted changes (**DESTRUCTIVE**)                          |
| `validate --local-only`                  | Validate without cross-repo ID resolution                                      |
| `validate --source <name>`               | Validate using a specific workspace source's adapter context                   |
| `list-ids --source <name>`               | Filter IDs by workspace source                                                 |

### Syncing Sources

Git URL sources are cloned on first access (e.g., during `workspace-add --url` or the first operation that resolves a URL source). Subsequent updates require an **explicit** `workspace-sync` invocation — source resolution does not perform network operations for existing repos.

`workspace-sync` fetches the configured branch (or remote default) and fast-forwards the local worktree. Use `--source <name>` to limit sync to a single source. Local path sources are skipped.

**`--force` is DESTRUCTIVE**: it runs `git reset --hard` and `git checkout -B`, discarding uncommitted changes and potentially losing local commits. Without `--force`, the command refuses to sync a dirty worktree.

### Removing Sources

There is no `workspace-remove` CLI command. To remove a source, edit the workspace config file directly:

- **Standalone** (`.cypilot-workspace.toml`): delete the `[sources.<name>]` section
- **Inline** (`config/core.toml`): delete the `[workspace.sources.<name>]` section

Then run `workspace-info` to verify the updated config.

### Switching Workspace Type

Cross-type transitions (standalone → inline or inline → standalone) are intentionally blocked to prevent
parallel configs. To switch workspace type:

1. Delete the existing config:
   - **Standalone → Inline**: delete `.cypilot-workspace.toml` (and remove any `workspace` key from `core.toml`)
   - **Inline → Standalone**: remove the `[workspace]` section from `config/core.toml`
2. Re-initialize: `workspace-init` (standalone) or `workspace-init --inline` (inline)
3. Re-add sources as needed with `workspace-add`

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
6. Artifacts with an explicit `source` pointing to an unreachable repo resolve to `None` — they are skipped rather than
   silently falling back to local paths
7. Scan failures on individual artifact files emit warnings to stderr but do not block the overall operation

---

## Git URL Sources

Standalone workspace configuration (`.cypilot-workspace.toml`) MUST support Git URL sources in addition to local paths. This enables workspace setups where not all repos are pre-cloned locally.

**Configuration**:

```toml
version = "1.0"

[resolve]
workdir = ".workspace-sources"  # Working directory for cloned repos (default: ".workspace-sources")

[resolve.namespace]
# Maps Git URL host to local directory template (exact host match).
"gitlab.com" = "{org}/{repo}"    # gitlab.com/myteam/backend.git → myteam/backend
"github.com" = "{org}/{repo}"    # github.com/acme/docs.git → acme/docs

[sources.backend]
url = "https://gitlab.com/myteam/backend.git"
branch = "main"
role = "codebase"

[sources.docs]
url = "https://gitlab.com/myteam/docs.git"
branch = "develop"
role = "artifacts"

[sources.local-kits]
path = "./shared-kits"  # Local paths still supported alongside URLs
role = "kits"
```

**Rules**:

- Git URL sources MUST only be supported in standalone workspace files — NOT in inline `config/core.toml` workspace definitions
- Namespace resolution rules MUST map Git URL host to local directory path template via exact host match
- When no namespace rule matches the Git URL host, the system MUST fall back to the default template `{org}/{repo}` — e.g., `https://gitlab.com/team/lib.git` → `team/lib` under `resolve.workdir`
- Branch/ref configuration MUST default to the remote repository's default branch when no per-source `branch` field is set. Each source MAY override the branch via its `branch` field
- The system MUST clone URL sources on first access and cache them locally under the working directory. Subsequent fetches MUST only occur via explicit `workspace-sync` invocation — source resolution MUST NOT perform network operations for already-cloned repos
- `resolve.workdir` MUST be resolved relative to the workspace file's parent directory (standalone only — Git URL sources are not supported in inline mode). The resulting directory is auto-created on first clone
- The resolved clone path (`workdir / templated`) MUST pass a containment check — paths that escape the working directory (via symlinks or path traversal) MUST be rejected

---

## Cross-Repo Editing

When working from a primary repository (e.g., a docs repo) and editing files in a remote source (e.g., backend or frontend), the system MUST apply the remote source's own adapter rules, templates, and constraints — not the primary repo's adapter.

**Example**: User works from `docs-repo/` and edits `backend/src/api.py`. The system loads `backend/.bootstrap/` adapter context (rules, templates, constraints) for validation and generation targeting that file.

**Rules**:

- Each source's adapter context MUST be resolved independently via `SourceContext.adapter_dir`
- Validation and generation operations targeting a specific source MUST use that source's adapter
- When a remote source has no Cypilot adapter, the system MUST fall back to the primary repo's adapter (current directory) for that source
- The primary repo's adapter MUST remain active for its own files and for workspace-level operations

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

### Scenario: Parent workspace with nested repos

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

Running `cypilot workspace-init` from `parent/` will discover `frontend`, `backend`, and `docs` as nested
sub-directories and generate the workspace config.
