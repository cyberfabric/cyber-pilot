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
- [Configuration](#configuration)
- [Source Entries](#source-entries)
- [Discovery and Path Resolution](#discovery-and-path-resolution)
- [Cross-Repo Traceability](#cross-repo-traceability)
- [Operations](#operations)
- [Compatibility and Degradation](#compatibility-and-degradation)
- [Git URL Sources](#git-url-sources)
- [Cross-Repo Editing](#cross-repo-editing)
- [Examples](#examples)

<!-- /toc -->

## Overview
Cypilot workspaces provide an opt-in federation layer for multi-repo projects. Each repo keeps its own adapter; the workspace maps named sources so artifacts, code, and kits can resolve across repos without merging adapters.
**Project root** = the repository root containing the adapter directory (for example `.bootstrap/` or `cypilot/`).
| Principle | Requirement |
|---|---|
| `cwd determines primary` | The primary source MUST be the repo containing the current working directory; there is no `primary` field. |
| Remote adapter context | A remote source with its own adapter MUST use that adapter's rules/templates/constraints. |
| Opt-in | No workspace config MUST preserve exact single-repo behavior. |
| Local paths first | Inline config supports local paths only; standalone config supports local paths and Git URLs. |
| Graceful degradation | Missing sources MUST warn but MUST NOT block available sources. |
## Configuration
Workspaces can be standalone or inline.
**Standalone** (`.cypilot-workspace.toml`):
```toml
version = "1.0"
[sources.docs-repo]
path = "../docs-repo"
adapter = "cypilot"
role = "artifacts"
[traceability]
cross_repo = true
resolve_remote_ids = true
```
**Inline** (`config/core.toml`):
```toml
workspace = "../.cypilot-workspace.toml"
[workspace.sources.docs]
path = "../docs-repo"
[workspace.sources.shared-kits]
path = "../shared-kits"
role = "kits"
```
## Source Entries
`adapter` means the source's Cypilot directory containing `.core/`, `.gen/`, and `config/`. If omitted, Cypilot auto-discovers it from the source's `AGENTS.md`.
| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `path` | string | Yes unless `url` is set | — | Local path; if both exist, `path` wins over `url`. |
| `url` | string | No; standalone only | — | HTTPS/SSH Git remote; forbidden in inline config. |
| `branch` | string | No; only with `url` | remote default | Rejected on path-only sources. |
| `adapter` | string | No | auto-discover | Path to adapter directory in the source repo. |
| `role` | string | No | `full` | Contribution scope. |
Roles: `artifacts`, `codebase`, `kits`, `full`.
## Discovery and Path Resolution
Discovery order:
1. Check `workspace` in `config/core.toml`.
   - string → external `.cypilot-workspace.toml`, resolved relative to project root
   - table → inline workspace definition, source paths resolved relative to project root
2. If absent, check for `.cypilot-workspace.toml` at project root.
3. If still absent, use single-repo mode.
No implicit parent traversal is allowed.

Resolution rules:
- external workspace path in `core.toml` resolves relative to project root
- standalone source `path` resolves relative to the workspace file's parent
- inline source `path` resolves relative to project root
- artifact/codebase/kit entries with `source` resolve relative to the named source root
- entries without `source` resolve locally for backward compatibility

`artifacts.toml` v1.2 adds optional `source` on artifacts, codebase entries, and kits. When absent, v1.0/v1.1 behavior remains unchanged.

## Cross-Repo Traceability

When `traceability.cross_repo = true`:
- `validate` collects IDs from reachable sources and accepts remote `@cpt-*` references
- `where-defined`, `where-used`, and `list-ids` operate across reachable sources
- `validate --local-only` restricts validation to the current repo

| Setting | Default | Effect |
|---|---|---|
| `cross_repo` | `true` | Enable workspace-aware ID collection and path resolution |
| `resolve_remote_ids` | `true` | Expand remote IDs into the validation union set |

Both settings must be `true` to include remote IDs.

`resolve_artifact_path` contract:
- no `source` → resolve relative to local project root
- reachable `source` → resolve relative to named source root
- missing/unreachable `source` → return `None`; never silently fall back to local

Scan failures MUST emit:
```text
Warning: failed to scan IDs from <path>: <reason>
```
and continue.

## Operations

| Command | Purpose |
|---|---|
| `workspace-init` | Scan nested repos and generate standalone workspace config |
| `workspace-init --inline` | Initialize inline workspace in `config/core.toml` |
| `workspace-add --name N --path P` | Add a local source; auto-detect standalone vs inline |
| `workspace-add --name N --url U` | Add a Git URL source to standalone config |
| `workspace-info` | Show config and per-source reachability/adapter status |
| `workspace-sync [--source <name>] [--dry-run] [--force]` | Fetch/update Git URL source worktrees |
| `validate --local-only` | Skip cross-repo ID resolution |
| `validate --source <name>` / `list-ids --source <name>` | Scope operations to one source |

Sync rules:
- URL sources clone on first access; later network updates require explicit `workspace-sync`
- local path sources are skipped during sync
- `workspace-sync --force` is **DESTRUCTIVE** and may discard uncommitted changes or local commits

There is no `workspace-remove`; edit the config directly, then run `workspace-info`.
To switch between standalone and inline, delete the current config, rerun `workspace-init` or `workspace-init --inline`, then re-add sources.

## Compatibility and Degradation

- No workspace config means exact current single-repo behavior.
- Existing v1.0/v1.1 registries without `source` fields remain valid.
- Workspace imports stay lazy inside functions.
- Global context may be `CypilotContext` or `WorkspaceContext`; `is_workspace()` distinguishes them.

When a source is missing, Cypilot warns in `workspace-info`, marks `reachable: false`, continues with available sources, skips remote IDs and unresolved explicit-source artifacts, and treats the condition as non-fatal with no error exit caused solely by the missing repo.

## Git URL Sources

Git URL sources are supported only in standalone `.cypilot-workspace.toml`.

```toml
version = "1.0"
[resolve]
workdir = ".workspace-sources"
[resolve.namespace]
"gitlab.com" = "{org}/{repo}"
[sources.backend]
url = "https://gitlab.com/myteam/backend.git"
branch = "main"
role = "codebase"
```

Rules:
- Git URLs are forbidden in inline workspace config.
- Namespace rules match exact host names; missing rules fall back to `{org}/{repo}`.
- Missing `branch` uses the remote default branch.
- Existing clones MUST NOT fetch during ordinary resolution; only `workspace-sync` may update them.
- `resolve.workdir` resolves relative to the standalone workspace file's parent.
- Resolved clone paths MUST pass containment checks and reject traversal/symlink escape.

## Cross-Repo Editing

Validation and generation targeting a remote source MUST use that source's adapter when present. If the remote source has no adapter, fall back to the primary repo's adapter. The primary repo's adapter remains active for its own files and workspace-level operations.

## Examples

### Example: Inline docs source from code repo

```text
workspace/
├── docs-repo/      (AGENTS.md, cypilot/config/artifacts.toml)
├── code-repo/      (AGENTS.md, .bootstrap/config/core.toml)  ← cwd
└── shared-kits/    (kits/sdlc)
```

Running `cypilot validate` from `code-repo/` loads `code-repo/.bootstrap`, discovers the workspace in `config/core.toml`, loads `docs-repo` artifacts, and accepts `@cpt-*` references to IDs defined there.

### Example: Parent workspace with nested repos

```text
parent/
├── .cypilot-workspace.toml
├── frontend/
├── backend/
└── docs/
```

Running `cypilot workspace-init` from `parent/` will discover `frontend`, `backend`, and `docs` as nested sub-directories and generate the workspace config.
