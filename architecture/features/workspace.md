# Feature: Multi-Repo Workspace Federation


<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1. Overview](#1-overview)
  - [2. Purpose](#2-purpose)
  - [3. Actors](#3-actors)
  - [4. References](#4-references)
  - [5. Non-Applicability](#5-non-applicability)
  - [6. Out of Scope](#6-out-of-scope)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Workspace Initialization](#workspace-initialization)
  - [Workspace Source Management](#workspace-source-management)
  - [Workspace Info Display](#workspace-info-display)
  - [Workspace Sync](#workspace-sync)
- [3. Processes / Business Logic (CDSL)](#3-processes--business-logic-cdsl)
  - [Find Workspace Config](#find-workspace-config)
  - [Discover Nested Repos](#discover-nested-repos)
  - [Resolve Source Path](#resolve-source-path)
  - [Infer Source Role](#infer-source-role)
  - [Load Workspace Context](#load-workspace-context)
  - [Resolve Artifact Path](#resolve-artifact-path)
  - [Collect Cross-Repo IDs](#collect-cross-repo-ids)
  - [Resolve Git URL Source](#resolve-git-url-source)
  - [Sync Git Source](#sync-git-source)
  - [Resolve Source Adapter Context](#resolve-source-adapter-context)
  - [Determine Target Source](#determine-target-source)
- [4. States (CDSL)](#4-states-cdsl)
  - [Source Reachability](#source-reachability)
  - [Config Lifecycle](#config-lifecycle)
- [5. Definitions of Done](#5-definitions-of-done)
  - [Workspace Initialization and Config](#workspace-initialization-and-config)
  - [Source Management](#source-management)
  - [Cross-Repo Traceability](#cross-repo-traceability)
  - [Graceful Degradation](#graceful-degradation)
  - [Backward Compatibility](#backward-compatibility)
  - [Git URL Source Resolution](#git-url-source-resolution)
  - [Cross-Repo Editing](#cross-repo-editing)
  - [Workspace Sync](#workspace-sync-1)
- [6. Implementation Modules](#6-implementation-modules)
- [7. Acceptance Criteria](#7-acceptance-criteria)

<!-- /toc -->

- [x] `p1` - **ID**: `cpt-cypilot-featstatus-workspace`

## 1. Feature Context

- [x] `p1` - `cpt-cypilot-feature-workspace`

### 1. Overview

Multi-repo workspace federation enabling nested sub-directory repo discovery, source configuration (standalone or inline), cross-repo artifact traceability, and graceful degradation when sources are unreachable. Projects without workspace config continue operating in single-repo mode with zero behavioral changes.

### 2. Purpose

Enables teams working across multiple repositories to federate their Cypilot-managed artifacts — discovering repos in nested sub-directories, resolving cross-repo artifact paths, and collecting IDs across workspace boundaries — without merging adapters or modifying individual project configs. Addresses PRD requirement for workspace federation (`cpt-cypilot-fr-core-workspace`) and extends the core traceability system (`cpt-cypilot-fr-core-traceability`) with cross-repo resolution.

**Delegation context note**: When Cypilot delegates execution to an external executor (e.g., ralphex), the delegated execution uses the same workspace/source-resolved context as the primary Cypilot session. Workspace source paths, adapter bindings, and cross-repo artifact resolution remain authoritative for delegated tasks. This feature does not own delegation logic — that belongs to `cpt-cypilot-feature-ralphex-delegation` — but it provides the context foundation that delegation consumers rely on (see `cpt-cypilot-adr-ralphex-delegation-skill`).

### 3. Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Runs `workspace-init`, `workspace-add` (with `--inline` flag for inline mode), `workspace-info`, `workspace-sync`; uses `validate --local-only` and `list-ids --source` |
| `cpt-cypilot-actor-cypilot-cli` | Discovers workspace config during context loading, resolves cross-repo paths, loads source contexts |

### 4. References

- **PRD**: [PRD.md](../PRD.md) — `cpt-cypilot-fr-core-workspace`, `cpt-cypilot-fr-core-traceability`, `cpt-cypilot-fr-core-workspace-git-sources`, `cpt-cypilot-fr-core-workspace-cross-repo-editing`
- **Design**: [DESIGN.md](../DESIGN.md) — `cpt-cypilot-component-config-manager`, `cpt-cypilot-component-traceability-engine`
- **Design Principles**: `cpt-cypilot-principle-traceability-by-design`, `cpt-cypilot-principle-determinism-first`, `cpt-cypilot-principle-zero-harm`
- **Design Constraints**: `cpt-cypilot-constraint-python-stdlib`
- **CLI Spec**: [cli.md](../specs/cli.md)
- **Dependencies**: `cpt-cypilot-feature-core-infra`, `cpt-cypilot-feature-traceability-validation`

### 5. Non-Applicability

The following quality domains are not applicable to this feature:

- **Performance**: Core operations (init, add, info) are local filesystem reads/writes on small TOML configs. Git URL source resolution clones on first access only; subsequent reads reuse the cached checkout without network operations. Explicit updates via `workspace-sync` delegate to the user's git CLI with a 300-second (5 min) default timeout, configurable via `GIT_TIMEOUT` environment variable; no custom performance-sensitive code paths beyond subprocess delegation
- **Security**: Local-path mode has no network access. Git URL sources perform `git clone` (first access) and `git fetch` (only via explicit `workspace-sync`) using the user's existing Git CLI credentials — no custom authentication or credential handling. CLI arguments parsed by argparse with no untrusted input
- **Compliance**: No regulatory, privacy, or audit requirements
- **Usability (UI)**: CLI-only interaction with structured JSON output; no graphical UI
- **Operations**: No deployment, observability, or infrastructure concerns; standalone CLI commands

### 6. Out of Scope

- Workspace-level aggregate linting or test orchestration across sources
- Remote source authentication beyond Git CLI credentials
- Workspace-level dependency resolution between source packages
- Live file-watching or automatic re-discovery of sources
- Cross-source manifest layer discovery and component merging (belongs to [project-extensibility](./project-extensibility.md) — see "Relationship with Workspace Federation" in [PROJECT-EXTENSIBILITY guide](../../guides/PROJECT-EXTENSIBILITY.md#relationship-with-workspace-federation))

## 2. Actor Flows (CDSL)

### Workspace Initialization

- [x] `p1` - **ID**: `cpt-cypilot-flow-workspace-init`

**Actors**:

- `cpt-cypilot-actor-user`
- `cpt-cypilot-actor-cypilot-cli`

**Success Scenarios**:
- User runs `workspace-init` → nested sub-directories scanned for repos, workspace config generated with discovered sources
- User runs `workspace-init --inline` → workspace config written inline into `config/core.toml`
- User runs `workspace-init --dry-run` → shows what would be generated without writing

**Error Scenarios**:
- No project root found → error with instructions
- Scan root not found → error with path
- No repos discovered in nested sub-directories → creates empty workspace (sources: {})
- `--inline` with existing standalone workspace → error (prevents parallel configs)
- Standalone init with existing inline workspace → error (prevents parallel configs)
- Re-init without `--force` when workspace already exists → error suggesting `--force`

**Steps**:
1. [x] - `p1` - User invokes `cypilot workspace-init [--root DIR] [--output PATH] [--inline] [--force] [--max-depth N] [--dry-run]` - `inst-user-workspace-init`
2. [x] - `p1` - Find project root from current directory - `inst-find-project-root`
3. [x] - `p1` - **IF** no project root found **RETURN** error: "No project root found" (exit 1) - `inst-if-no-root`
4. [x] - `p1` - Determine scan root: `--root` argument or project root itself - `inst-determine-scan-root`
5. [x] - `p1` - **IF** scan root not found **RETURN** error (exit 1) - `inst-if-no-scan-root`
6. [x] - `p1` - Algorithm: discover repos in nested sub-directories using `cpt-cypilot-algo-workspace-discover-nested` (limited to `--max-depth` levels, default 3) - `inst-discover-nested`
7. [x] - `p1` - Build workspace data with version and discovered sources (may be empty) - `inst-build-workspace-data`
8. [x] - `p1` - **IF** `--dry-run` **RETURN** DRY_RUN status with workspace preview (exit 0) - `inst-if-dry-run`
9. [x] - `p1` - **IF** existing workspace config found: **IF** cross-type conflict (inline vs standalone) **RETURN** error (exit 1); **IF** same type and no `--force` **RETURN** error suggesting `--force` (exit 1) - `inst-if-existing-ws`
10. [x] - `p1` - **IF** `--inline` write workspace inline to core.toml - `inst-if-inline`
11. [x] - `p1` - **ELSE** write standalone `.cypilot-workspace.toml` - `inst-else-standalone`
12. [x] - `p1` - **RETURN** JSON: `{status: CREATED, config_path, sources_count, sources}` (exit 0) - `inst-return-init-ok`
13. [x] - `p1` - Implementation: write workspace config inline to core.toml - `inst-write-inline-impl`
14. [x] - `p1` - Implementation: write standalone `.cypilot-workspace.toml` file - `inst-write-standalone-impl`
15. [x] - `p1` - Helper functions: output directory resolution, existing workspace conflict detection - `inst-init-helpers`
16. [x] - `p1` - Human-friendly formatter for workspace init output - `inst-init-human-fmt`

### Workspace Source Management

- [x] `p1` - **ID**: `cpt-cypilot-flow-workspace-add`

**Actors**:

- `cpt-cypilot-actor-user`
- `cpt-cypilot-actor-cypilot-cli`

**Success Scenarios**:
- User runs `workspace-add --name N --path P` → local source added to standalone workspace config
- User runs `workspace-add --name N --url U [--branch B]` → Git URL source added to standalone workspace config
- User runs `workspace-add --inline --name N --path P` → source added inline to core.toml

**Error Scenarios**:
- No project root → error
- No workspace config found without `--inline` → error with init hint
- Source name already exists without `--force` → error: "Source '{name}' already exists. Use --force to replace."
- Git URL source with inline workspace → error (URLs not supported inline)
- `--inline` flag with existing standalone workspace → error (prevents parallel configs)

**Steps**:
1. [x] - `p1` - User invokes `workspace-add --name N (--path P | --url U) [--branch B] [--role R] [--adapter A] [--force]` or `workspace-add --inline --name N --path P [--role R] [--adapter A] [--force]` - `inst-user-workspace-add`
2. [x] - `p1` - Find project root - `inst-add-find-root`
3. [x] - `p1` - **IF** no project root **RETURN** error (exit 1) - `inst-add-if-no-root`
4. [x] - `p1` - **IF** `--inline` flag set: check for existing standalone workspace; **IF** standalone exists **RETURN** error (exit 1); **ELSE** add to inline config - `inst-add-if-inline-flag`
5. [x] - `p1` - **ELSE** find existing workspace config using `cpt-cypilot-algo-workspace-find-config` - `inst-add-find-ws`
6. [x] - `p1` - **IF** no workspace config found **RETURN** error: "Run workspace-init first" (exit 1) - `inst-add-if-no-ws`
7. [x] - `p1` - **IF** existing workspace is inline, auto-route to inline add (no `--inline` flag required) - `inst-add-auto-detect-inline`
8. [x] - `p1` - **IF** source name already exists **AND** `--force` not specified **RETURN** error: "Source '{name}' already exists. Use --force to replace." (exit 1) - `inst-add-check-collision`
9. [x] - `p1` - Add source entry to config - `inst-add-source`
10. [x] - `p1` - Save updated config - `inst-add-save`
11. [x] - `p1` - **RETURN** JSON: `{status: ADDED, source}` (exit 0) - `inst-add-return-ok`
12. [x] - `p1` - Implementation: inline source addition to core.toml - `inst-add-inline-impl`
13. [x] - `p1` - Human-friendly formatter for workspace add output - `inst-add-human-fmt`

### Workspace Info Display

- [x] `p1` - **ID**: `cpt-cypilot-flow-workspace-info`

**Actors**:

- `cpt-cypilot-actor-user`
- `cpt-cypilot-actor-cypilot-cli`

**Success Scenarios**:
- User runs `workspace-info` → workspace config displayed with per-source reachability, artifact counts, traceability settings

**Error Scenarios**:
- No project root → error
- No workspace config → ERROR status with hint
- Workspace config parse error → ERROR status

**Steps**:
1. [x] - `p1` - User invokes `cypilot workspace-info` - `inst-user-workspace-info`
2. [x] - `p1` - Find project root - `inst-info-find-root`
3. [x] - `p1` - **IF** no project root **RETURN** error (exit 1) - `inst-info-if-no-root`
4. [x] - `p1` - Find workspace config using `cpt-cypilot-algo-workspace-find-config` - `inst-info-find-ws`
5. [x] - `p1` - **IF** config error **RETURN** ERROR status (exit 1) - `inst-info-if-error`
6. [x] - `p1` - **IF** no workspace **RETURN** ERROR status with hint (exit 1) - `inst-info-if-no-ws`
7. [x] - `p1` - **FOR EACH** source build status info (path, reachability, adapter, artifact counts) - `inst-info-foreach-source`
8. [x] - `p1` - Load workspace context if available, enrich with cross-repo stats - `inst-info-load-context`
9. [x] - `p1` - **RETURN** JSON: `{status: OK, version, sources, traceability}` (exit 0) - `inst-info-return-ok`
10. [x] - `p1` - Helper functions: source adapter probing, status building, artifact counting - `inst-info-helpers`
11. [x] - `p1` - Build result dict with config path, sources info, traceability settings - `inst-info-build-result`
12. [x] - `p1` - Human-friendly formatter for workspace info output - `inst-info-human-fmt`

### Workspace Sync

- [x] `p1` - **ID**: `cpt-cypilot-flow-workspace-sync`

**Actors**:

- `cpt-cypilot-actor-user`
- `cpt-cypilot-actor-cypilot-cli`

**Success Scenarios**:
- User runs `workspace-sync` → all Git URL sources fetched and worktrees updated to match remote
- User runs `workspace-sync --source N` → only named source synced
- User runs `workspace-sync --dry-run` → shows which sources would be synced without network operations

**Error Scenarios**:
- No project root found → error with instructions
- No workspace config found → error with init hint
- Named source not found → error listing available sources
- Named source has no Git URL (local path only) → error explaining only Git URL sources can be synced
- Git fetch or update fails → warning per source, continue with remaining sources

**Steps**:
1. [x] - `p1` - User invokes `cypilot workspace-sync [--source NAME] [--dry-run]` - `inst-user-workspace-sync`
2. [x] - `p1` - Find project root from current directory - `inst-sync-find-root`
3. [x] - `p1` - **IF** no project root found **RETURN** error (exit 1) - `inst-sync-if-no-root`
4. [x] - `p1` - Find workspace config using `cpt-cypilot-algo-workspace-find-config` - `inst-sync-find-ws`
5. [x] - `p1` - **IF** no workspace config found **RETURN** error with init hint (exit 1) - `inst-sync-if-no-ws`
6. [x] - `p1` - Collect Git URL sources: **IF** `--source` is set, look up single source by name; **ELSE** collect all sources with `url` set - `inst-sync-collect-sources`
7. [x] - `p1` - **IF** `--source` set AND source not found **RETURN** error listing available sources (exit 1) - `inst-sync-if-source-not-found`
8. [x] - `p1` - **IF** `--source` set AND source has no URL **RETURN** error (exit 1) - `inst-sync-if-no-url`
9. [x] - `p1` - **IF** no Git URL sources found **RETURN** status with message "no git sources to sync" (exit 0) - `inst-sync-if-no-git-sources`
10. [x] - `p1` - **IF** `--dry-run` **RETURN** DRY_RUN status listing sources that would be synced (exit 0) - `inst-sync-if-dry-run`
11. [x] - `p1` - **FOR EACH** Git URL source: algorithm `cpt-cypilot-algo-workspace-sync-git-source`, collect per-source result - `inst-sync-foreach-source`
12. [x] - `p1` - **RETURN** JSON: `{status: OK, synced, failed, results: [{name, status, error?}]}` (exit 0, or exit 2 if all failed) - `inst-sync-return-ok`
13. [x] - `p1` - Human-friendly formatter for workspace sync output - `inst-sync-human-fmt`

## 3. Processes / Business Logic (CDSL)

### Find Workspace Config

- [x] `p1` - **ID**: `cpt-cypilot-algo-workspace-find-config`

**Input**: Project root path

**Output**: `(WorkspaceConfig, None)` or `(None, error_message)` or `(None, None)` if no workspace

**Steps**:
1. [x] - `p1` - Load project config from `core.toml` (via AGENTS.md cypilot_path) - `inst-find-load-project-config`
2. [x] - `p1` - **IF** project config not found: **IF** config file exists but failed to parse **RETURN** `(None, error)`; **ELSE** fall through to standalone auto-discovery (step 5) - `inst-find-if-no-config`
3. [x] - `p1` - **IF** project config has `workspace` key as string path - `inst-find-if-ws-string`
   1. [x] - `p1` - Resolve path relative to project root and load as standalone TOML - `inst-find-load-standalone`
   2. [x] - `p1` - **RETURN** `(WorkspaceConfig, None)` or `(None, error)` - `inst-find-return-standalone`
4. [x] - `p1` - **IF** project config has `workspace` key as dict - `inst-find-if-ws-dict`
   1. [x] - `p1` - Parse inline workspace config with `resolution_base` set to project root - `inst-find-parse-inline`
   2. [x] - `p1` - **RETURN** `(WorkspaceConfig, None)` - `inst-find-return-inline`
5. [x] - `p1` - **IF** `workspace` key absent or config not loaded: check for standalone `.cypilot-workspace.toml` at project root; **IF** file exists load and **RETURN** `(WorkspaceConfig, None)` or `(None, error)`; **ELSE RETURN** `(None, None)` — no workspace, single-repo mode - `inst-find-return-none`
6. [x] - `p1` - Data model: `WorkspaceConfig` class, factory methods, serialization - `inst-find-config-datamodel`
7. [x] - `p1` - Implementation: parse inline workspace from core.toml `[workspace]` section - `inst-find-parse-inline-impl`
8. [x] - `p1` - Implementation: discover standalone `.cypilot-workspace.toml` at project root - `inst-find-standalone-impl`

### Discover Nested Repos

- [x] `p1` - **ID**: `cpt-cypilot-algo-workspace-discover-nested`

**Input**: Scan root directory, output directory (for relative path computation), max_depth (default 3)

**Output**: Dict of source_name -> `{path, adapter?, role}`

**Steps**:
1. [x] - `p1` - **IF** current depth exceeds max_depth **RETURN** empty dict - `inst-disc-check-depth`
2. [x] - `p1` - List entries in scan root, sorted alphabetically - `inst-disc-list-entries`
3. [x] - `p1` - **FOR EACH** directory entry (skip hidden dirs and symlinks) - `inst-disc-foreach-entry`
   1. [x] - `p1` - Check if directory is a project (has `.git` or `AGENTS.md` with `@cpt:root-agents` marker) - `inst-disc-check-project`
   2. [x] - `p1` - **IF** not a project, recurse into subdirectory (depth + 1) and merge results, then skip to next entry - `inst-disc-if-not-project`
   3. [x] - `p1` - Find adapter path: read `cypilot_path` from AGENTS.md, fallback to `find_cypilot_directory` - `inst-disc-find-adapter`
   4. [x] - `p1` - **IF** no adapter found, skip directory - `inst-disc-if-no-adapter`
   5. [x] - `p1` - Compute relative source path from output location - `inst-disc-compute-path`
   6. [x] - `p1` - Algorithm: infer role using `cpt-cypilot-algo-workspace-infer-role` - `inst-disc-infer-role`
   7. [x] - `p1` - Add to discovered sources dict - `inst-disc-add-source`
4. [x] - `p1` - **RETURN** discovered sources - `inst-disc-return`
5. [x] - `p1` - Helper functions: project directory detection, adapter path finding, source path computation - `inst-disc-helpers`

### Resolve Source Path

- [x] `p1` - **ID**: `cpt-cypilot-algo-workspace-resolve-source`

**Input**: Source name, workspace config

**Output**: Absolute filesystem path or None

**Steps**:
1. [x] - `p1` - Look up source entry by name - `inst-resolve-lookup`
2. [x] - `p1` - **IF** source not found **RETURN** None - `inst-resolve-if-not-found`
3. [x] - `p1` - Determine base directory: `resolution_base` if set (inline mode), else workspace file's parent directory, else return None - `inst-resolve-determine-base`
4. [x] - `p1` - **IF** `source.path` is set **RETURN** `(base / source.path).resolve()` (`path` takes precedence over `url`) - `inst-resolve-return`
5. [x] - `p1` - **IF** `source.url` is set, delegate to `cpt-cypilot-algo-workspace-resolve-git-url` - `inst-resolve-git-url-delegate`
6. [x] - `p1` - **RETURN** None - `inst-resolve-fallback`
7. [x] - `p1` - Data model: `SourceEntry` class, workspace imports, constants - `inst-resolve-datamodel`

### Infer Source Role

- [x] `p1` - **ID**: `cpt-cypilot-algo-workspace-infer-role`

**Input**: Repository path

**Output**: Role string (`"artifacts"`, `"codebase"`, `"kits"`, `"full"`)

**Steps**:
1. [x] - `p1` - Check for source directories: `src/`, `lib/`, `app/`, `pkg/` - `inst-role-check-src`
2. [x] - `p1` - Check for documentation directories: `docs/`, `architecture/`, `requirements/` - `inst-role-check-docs`
3. [x] - `p1` - Check for kits directory: `kits/` - `inst-role-check-kits`
4. [x] - `p1` - **IF** multiple capabilities present (more than one of src/docs/kits) **RETURN** `"full"` - `inst-role-if-multi`
5. [x] - `p1` - **IF** has kits AND no source dirs **RETURN** `"kits"` - `inst-role-if-kits`
6. [x] - `p1` - **IF** has docs AND no source dirs **RETURN** `"artifacts"` - `inst-role-if-artifacts`
7. [x] - `p1` - **IF** has source dirs AND no docs **RETURN** `"codebase"` - `inst-role-if-codebase`
8. [x] - `p1` - **ELSE RETURN** `"full"` - `inst-role-return-full`

### Load Workspace Context

- [x] `p1` - **ID**: `cpt-cypilot-algo-workspace-load-context`

**Input**: Primary CypilotContext

**Output**: WorkspaceContext or None (if no workspace config found)

**Steps**:
1. [x] - `p1` - Find workspace config using `cpt-cypilot-algo-workspace-find-config` - `inst-ctx-find-config`
2. [x] - `p1` - **IF** config error, emit warning to stderr - `inst-ctx-if-error`
3. [x] - `p1` - **IF** no config found **RETURN** None - `inst-ctx-if-no-config`
4. [x] - `p1` - **FOR EACH** source in config - `inst-ctx-foreach-source`
   1. [x] - `p1` - Resolve source path - `inst-ctx-resolve-path`
   2. [x] - `p1` - **IF** path not found or not a directory, create unreachable SourceContext - `inst-ctx-if-unreachable`
   3. [x] - `p1` - **ELSE** find adapter directory, load ArtifactsMeta, extract registered systems - `inst-ctx-load-source-meta`
5. [x] - `p1` - Build WorkspaceContext with primary context, loaded sources, traceability settings - `inst-ctx-build`
6. [x] - `p1` - **RETURN** WorkspaceContext - `inst-ctx-return`

### Resolve Artifact Path

- [x] `p1` - **ID**: `cpt-cypilot-algo-workspace-resolve-artifact`

**Input**: Artifact (with optional `source` attribute), fallback root path

**Output**: Optional[Path] — resolved absolute path or None

**Steps**:
1. [x] - `p1` - Check if artifact has a `source` attribute naming a workspace source - `inst-art-check-source`
2. [x] - `p1` - **IF** source is set - `inst-art-if-source`
   1. [x] - `p1` - Look up SourceContext by name - `inst-art-lookup-source`
   2. [x] - `p1` - **IF** source reachable **RETURN** `(source.path / artifact.path).resolve()` - `inst-art-if-reachable`
   3. [x] - `p1` - **ELSE RETURN** None (prevent silent fallback to local path) - `inst-art-return-none`
3. [x] - `p1` - **ELSE RETURN** `(fallback_root / artifact.path).resolve()` - `inst-art-return-local`

### Collect Cross-Repo IDs

- [x] `p1` - **ID**: `cpt-cypilot-algo-workspace-collect-ids`

**Input**: WorkspaceContext

**Output**: Set of all definition IDs across primary and remote sources

**Steps**:
1. [x] - `p1` - Collect definition IDs from primary context artifacts - `inst-ids-collect-primary`
2. [x] - `p1` - **IF** `cross_repo` AND `resolve_remote_ids` are enabled - `inst-ids-if-cross-repo`
   1. [x] - `p1` - **FOR EACH** reachable source with loaded metadata **and role `artifacts` or `full`** - `inst-ids-foreach-source`
      1. [x] - `p1` - **FOR EACH** artifact in source, scan for ID definitions - `inst-ids-scan-source-artifacts`
      2. [x] - `p1` - Add discovered IDs to the set (emit warning on scan failure) - `inst-ids-add-with-warning`
3. [x] - `p1` - **RETURN** collected ID set - `inst-ids-return`

### Resolve Git URL Source

- [x] `p1` - **ID**: `cpt-cypilot-algo-workspace-resolve-git-url`

**Input**: `SourceEntry` (with `url` set), `ResolveConfig`, workspace file parent path

**Output**: Absolute filesystem path to the resolved local directory

**Steps**:
1. [x] - `p1` - Delegate from `resolve_source_path` when source has `url` set - `inst-resolve-git-url-delegate`
2. [x] - `p1` - Parse URL into host, org, repo components - `inst-git-parse-url`
3. [x] - `p1` - Look up namespace rule by exact host match in `resolve.namespace` - `inst-git-lookup-namespace`
4. [x] - `p1` - **IF** no matching rule, use default template `{org}/{repo}` - `inst-git-if-no-rule`
5. [x] - `p1` - Apply template substitution: replace `{org}` and `{repo}` placeholders - `inst-git-apply-template`
6. [x] - `p1` - Compute local path: `(workspace_parent / resolve.workdir / templated_path).resolve()` (default `resolve.workdir`: `.workspace-sources`) - `inst-git-compute-path`
7. [x] - `p1` - Determine branch: source `branch` field if set, else `"HEAD"` - `inst-git-determine-branch`
8. [x] - `p1` - **IF** local path exists AND is a git repo, **RETURN** local path (no network operation — use `workspace-sync` to update) - `inst-git-if-exists-fetch`
9. [x] - `p1` - **ELSE** run `git clone --branch {branch} {url} {local_path}` - `inst-git-else-clone`
10. [x] - `p1` - **IF** git command fails or times out (300s default, override via `GIT_TIMEOUT` env var), mark source as unreachable with error message - `inst-git-if-fail`
11. [x] - `p1` - **RETURN** resolved local path - `inst-git-return-path`
12. [x] - `p1` - Data model: `TraceabilityConfig`, `NamespaceRule`, `ResolveConfig` classes and URL patterns - `inst-git-datamodel`
13. [x] - `p1` - Clone or return existing local path via subprocess - `inst-git-clone-or-fetch`
14. [x] - `p1` - Run git command via subprocess with timeout - `inst-git-run-command`

### Sync Git Source

- [x] `p1` - **ID**: `cpt-cypilot-algo-workspace-sync-git-source`

**Input**: `SourceEntry` (with `url` set), `ResolveConfig`, workspace file parent path

**Output**: `{status: "synced"|"failed", error?}` — result of syncing one Git URL source

**Steps**:
1. [x] - `p1` - Resolve local path using `cpt-cypilot-algo-workspace-resolve-git-url` (clone-only, no fetch) - `inst-sync-resolve-path`
2. [x] - `p1` - **IF** resolved path is None **RETURN** `{status: "failed", error: "resolve failed"}` - `inst-sync-if-no-path`
3. [x] - `p1` - **IF** local path does not exist or is not a git repo **RETURN** `{status: "failed", error: "not a git repo"}` - `inst-sync-if-not-repo`
4. [x] - `p1` - Run `git fetch --quiet origin [branch]` - `inst-sync-fetch`
5. [x] - `p1` - **IF** fetch fails **RETURN** `{status: "failed", error}` - `inst-sync-if-fetch-fail`
6. [x] - `p1` - Determine branch: source `branch` field if set, else `"HEAD"` - `inst-sync-determine-branch`
7. [x] - `p1` - **IF** branch == "HEAD": run `git reset --hard FETCH_HEAD` - `inst-sync-if-head`
8. [x] - `p1` - **ELSE**: run `git checkout -B {branch} origin/{branch}` - `inst-sync-else-branch`
9. [x] - `p1` - **IF** update fails, emit warning **RETURN** `{status: "failed", error}` - `inst-sync-if-update-fail`
10. [x] - `p1` - **RETURN** `{status: "synced"}` - `inst-sync-return-ok`

### Resolve Source Adapter Context

- [x] `p1` - **ID**: `cpt-cypilot-algo-workspace-resolve-adapter-context`

**Input**: `SourceContext` (reachable, with `adapter_dir` set)

**Output**: `CypilotContext` loaded from the source's adapter, or `None`

**Steps**:
1. [x] - `p1` - **IF** source is not reachable **RETURN** None - `inst-adapter-if-unreachable`
2. [x] - `p1` - **IF** `adapter_dir` is None **RETURN** None - `inst-adapter-if-no-dir`
3. [x] - `p1` - Verify adapter directory exists: `source.adapter_dir` (already resolved to absolute path during source loading) - `inst-adapter-compute-path`
4. [x] - `p1` - **IF** adapter directory does not exist **RETURN** None with warning - `inst-adapter-if-missing`
5. [x] - `p1` - Load `CypilotContext` from the adapter path (config, kits, templates, rules, constraints) - `inst-adapter-load-context`
6. [x] - `p1` - **IF** loading fails, emit warning to stderr **RETURN** None - `inst-adapter-if-load-fail`
7. [x] - `p1` - Cache the loaded context on `SourceContext.adapter_context` - `inst-adapter-cache`
8. [x] - `p1` - **RETURN** loaded `CypilotContext` - `inst-adapter-return`
9. [x] - `p1` - Helper: return source meta with autodetect expanded; lazy-load full context via steps 1-8 on first access, return cached `adapter_context.meta` on repeat calls, fall back to raw `meta` when adapter unavailable - `inst-adapter-expand-meta`

### Determine Target Source

- [x] `p1` - **ID**: `cpt-cypilot-algo-workspace-determine-target`

**Input**: Target file path, `WorkspaceContext`

**Output**: `(SourceContext, CypilotContext)` for the source owning the target file, or `(None, primary_context)` if the file belongs to the primary repo

**Steps**:
1. [x] - `p1` - Resolve target file to absolute path - `inst-target-resolve-abs`
2. [x] - `p1` - **FOR EACH** source in `workspace.sources` (ordered by path length descending for longest-prefix match) - `inst-target-foreach-source`
   1. [x] - `p1` - **IF** target path starts with source absolute path - `inst-target-if-match`
      1. [x] - `p1` - Resolve adapter context using `cpt-cypilot-algo-workspace-resolve-adapter-context` - `inst-target-resolve-adapter`
      2. [x] - `p1` - **IF** adapter context loaded **RETURN** `(source, adapter_context)` - `inst-target-return-source`
      3. [x] - `p1` - **ELSE RETURN** `(source, primary_context)` — source matched but no adapter available - `inst-target-return-source-no-adapter`
3. [x] - `p1` - **RETURN** `(None, primary_context)` — file belongs to primary repo - `inst-target-return-primary`
4. [x] - `p1` - `validate --source` / `--artifact` override: narrow working context to the matched source adapter for registry and project root, while retaining the original `WorkspaceContext` for workspace-level operations (cross-repo path routing, ID expansion, config validation) - `inst-validate-source-flag`

## 4. States (CDSL)

### Source Reachability

- [x] `p1` - **ID**: `cpt-cypilot-state-workspace-source-reachability`

**States**: REACHABLE, UNREACHABLE

**Initial State**: UNREACHABLE (before path resolution)

**Transitions**:
1. [x] - `p1` - **FROM** UNREACHABLE **TO** REACHABLE **WHEN** resolved source path exists and is a directory - `inst-source-becomes-reachable`
2. [x] - `p1` - **FROM** REACHABLE **TO** UNREACHABLE **WHEN** source directory is removed or becomes inaccessible between invocations - `inst-source-becomes-unreachable`

### Config Lifecycle

- [x] `p1` - **ID**: `cpt-cypilot-state-workspace-config-lifecycle`

**States**: NO_WORKSPACE, STANDALONE, INLINE

**Initial State**: NO_WORKSPACE

**Transitions**:
1. [x] - `p1` - **FROM** NO_WORKSPACE **TO** STANDALONE **WHEN** `workspace-init` creates `.cypilot-workspace.toml` - `inst-config-create-standalone`
2. [x] - `p1` - **FROM** NO_WORKSPACE **TO** INLINE **WHEN** `workspace-init --inline` writes `[workspace]` section to `core.toml` - `inst-config-create-inline`
3. [x] - `p1` - **FROM** STANDALONE **TO** STANDALONE **WHEN** `workspace-add` updates existing standalone config - `inst-config-update-standalone`
4. [x] - `p1` - **FROM** INLINE **TO** INLINE **WHEN** `workspace-add --inline` updates existing inline config - `inst-config-update-inline`
5. [x] - `p1` - **FROM** STANDALONE **TO** STANDALONE **WHEN** `workspace-init --force` reinitializes existing standalone config - `inst-config-reinit-standalone`
6. [x] - `p1` - **FROM** INLINE **TO** INLINE **WHEN** `workspace-init --inline --force` reinitializes existing inline config - `inst-config-reinit-inline`
7. [x] - `p1` - Config utility methods: resolve_source_adapter, validate, add_source, save - `inst-config-methods`
8. [x] - `p1` - Implementation: inline config loading utility for workspace operations - `inst-config-load-inline-impl`

**Guards** (illegal transitions — always rejected):
- **FROM** STANDALONE **TO** INLINE — `workspace-init --inline` or `workspace-add --inline` when standalone exists
- **FROM** INLINE **TO** STANDALONE — `workspace-init` (no `--inline`) when inline exists

## 5. Definitions of Done

### Workspace Initialization and Config

- [x] `p1` - **ID**: `cpt-cypilot-dod-workspace-init`

The system **MUST** provide a `workspace-init` command that scans nested sub-directories for repositories (identified by `.git` or `AGENTS.md` with `@cpt:root-agents` marker), infers roles, discovers adapter paths, and generates workspace configuration. Scanning depth **MUST** be limited by a `--max-depth` parameter (default 3) to prevent unbounded filesystem traversal and symlink loops; symlinks **MUST** be skipped during directory iteration. The command **MUST** support standalone file output (`.cypilot-workspace.toml`), inline output (`--inline` into `config/core.toml`), dry-run preview (`--dry-run`), and forced reinitialization (`--force`). The command **MUST** reject cross-type conflicts (e.g., `--inline` when standalone exists) and **MUST** require `--force` to overwrite an existing same-type workspace config. Config discovery **MUST** first check `core.toml` `workspace` key (string path or inline dict), then fall back to well-known standalone file `.cypilot-workspace.toml` at the project root — no implicit parent directory traversal.

**Implements**:
- `cpt-cypilot-flow-workspace-init`
- `cpt-cypilot-algo-workspace-find-config`
- `cpt-cypilot-algo-workspace-discover-nested`
- `cpt-cypilot-algo-workspace-infer-role`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-workspace`

**Covers (DESIGN)**:
- `cpt-cypilot-component-config-manager`

### Source Management

- [x] `p1` - **ID**: `cpt-cypilot-dod-workspace-source-mgmt`

The system **MUST** provide a `workspace-add` command (with `--inline` flag for inline mode) to add sources to existing workspace configs. Each source entry **MUST** include name, path, optional adapter path, and role. `workspace-add` **MUST** operate on standalone config by default, and on inline config when `--inline` is specified. Type mismatches **MUST** produce errors directing users to the correct flag. If a source with the same name already exists, `workspace-add` **MUST** return an error unless `--force` is specified; with `--force`, the existing entry is silently replaced. All config writes **MUST** preserve existing entries and settings.

**Implements**:
- `cpt-cypilot-flow-workspace-add`
- `cpt-cypilot-algo-workspace-resolve-source`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-workspace`

**Covers (DESIGN)**:
- `cpt-cypilot-component-config-manager`

### Cross-Repo Traceability

- [x] `p1` - **ID**: `cpt-cypilot-dod-workspace-cross-repo`

The system **MUST** upgrade `CypilotContext` to `WorkspaceContext` when workspace config is found, loading `SourceContext` per source with reachability status. `resolve_artifact_path` **MUST** return `Optional[Path]` — `None` when a source is explicitly set but unreachable, preventing silent fallback. Two traceability settings (`cross_repo`, `resolve_remote_ids`) **MUST** independently control path resolution and remote ID expansion. `validate --local-only` **MUST** skip cross-repo resolution. `list-ids --source` **MUST** filter by source name.

**Implements**:
- `cpt-cypilot-algo-workspace-load-context`
- `cpt-cypilot-algo-workspace-resolve-artifact`
- `cpt-cypilot-algo-workspace-collect-ids`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-workspace`
- `cpt-cypilot-fr-core-traceability`

**Covers (DESIGN)**:
- `cpt-cypilot-component-traceability-engine`
- `cpt-cypilot-principle-traceability-by-design`
- `cpt-cypilot-principle-determinism-first`

### Graceful Degradation

- [x] `p1` - **ID**: `cpt-cypilot-dod-workspace-graceful-degradation`

The system **MUST** continue operating when workspace sources are unreachable. Unreachable sources **MUST** be marked with `reachable: false` in the source context. Scan failures for individual artifacts **MUST** emit warnings to stderr rather than terminating. Operations **MUST** proceed with available sources and produce valid results for the reachable subset.

**Implements**:
- `cpt-cypilot-algo-workspace-load-context`
- `cpt-cypilot-algo-workspace-collect-ids`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-workspace`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-zero-harm`

### Backward Compatibility

- [x] `p1` - **ID**: `cpt-cypilot-dod-workspace-backward-compat`

The system **MUST** operate identically for projects without workspace configuration. Context loading **MUST** return `CypilotContext` (not `WorkspaceContext`) when no workspace is found. All existing CLI commands **MUST** function without modification in single-repo mode. No workspace-related warnings **MUST** appear for non-workspace projects.

**Implements**:
- `cpt-cypilot-algo-workspace-find-config`
- `cpt-cypilot-algo-workspace-load-context`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-workspace`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-zero-harm`
- `cpt-cypilot-constraint-python-stdlib`

### Git URL Source Resolution

- [x] `p1` - **ID**: `cpt-cypilot-dod-workspace-git-url-sources`

The system **MUST** support Git URL sources in standalone workspace files (`.cypilot-workspace.toml`). `SourceEntry` **MUST** accept an optional `url` field for remote Git repositories and an optional `branch` field for ref pinning. An optional `[resolve]` section in workspace config **MAY** define the working directory and namespace resolution rules mapping Git URL host to local directory path templates. Namespace lookup **MUST** use exact host match. When no matching rule is found (or no `[resolve]` section exists), the system **MUST** fall back to the default template `{org}/{repo}` — producing `a/b` for `github.com/a/b.git` and `a/b/c/d/e` for `gitlab.example.com/a/b/c/d/e.git`. Source resolution **MUST** clone repos on first access and return existing local paths without network operations on subsequent accesses — use `workspace-sync` to update worktrees. Inline workspace definitions in `core.toml` **MUST** reject `url` fields during validation. Git operations **MUST** use `subprocess` calling the `git` CLI directly (stdlib-only constraint).

**Implements**:
- `cpt-cypilot-algo-workspace-resolve-git-url`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-workspace-git-sources`

**Covers (DESIGN)**:
- `cpt-cypilot-component-config-manager`
- `cpt-cypilot-constraint-python-stdlib`

### Cross-Repo Editing

- [x] `p1` - **ID**: `cpt-cypilot-dod-workspace-cross-repo-editing`

The system **MUST** load a remote source's own adapter context (rules, templates, constraints) when editing files in that source, instead of applying the primary repo's adapter. `SourceContext` **MUST** gain an `adapter_context` field populated lazily on first access. The system **MUST** determine which source owns a target file by matching file paths against resolved source paths (longest-prefix match) — auto-detection makes an explicit `--source` flag unnecessary for most operations. Validation commands **MAY** support an optional `--source` flag for explicit source targeting when auto-detection is not desired. When a remote source has no Cypilot adapter, the system **MUST** fall back to the primary repo's adapter for that source. The primary repo's adapter **MUST** remain active for workspace-level operations and its own files.

**Implements**:
- `cpt-cypilot-algo-workspace-resolve-adapter-context`
- `cpt-cypilot-algo-workspace-determine-target`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-workspace-cross-repo-editing`

**Covers (DESIGN)**:
- `cpt-cypilot-component-traceability-engine`
- `cpt-cypilot-component-validator`

### Workspace Sync

- [x] `p1` - **ID**: `cpt-cypilot-dod-workspace-sync`

The system **MUST** provide a `workspace-sync` command that explicitly fetches and updates worktrees for Git URL sources. The command **MUST** iterate all Git URL sources (or a single `--source` if specified) and for each: run `git fetch origin [branch]`, then update the worktree via `git checkout -B {branch} origin/{branch}` (or `git reset --hard FETCH_HEAD` for HEAD mode). The command **MUST** support `--dry-run` to preview without network operations. Source resolution (`resolve_source_path`) **MUST NOT** perform network operations for existing repos — it only clones on first access and returns local paths for subsequent accesses. This separation ensures read operations (`validate`, `list-ids`, `workspace-info`) are fast, deterministic, and work offline.

**Implements**:
- `cpt-cypilot-flow-workspace-sync`
- `cpt-cypilot-algo-workspace-sync-git-source`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-workspace-git-sources`

**Covers (DESIGN)**:
- `cpt-cypilot-component-config-manager`
- `cpt-cypilot-constraint-python-stdlib`

## 6. Implementation Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| Workspace Config | `skills/.../utils/workspace.py` | Data types (`SourceEntry`, `TraceabilityConfig`, `WorkspaceConfig`), config loading/saving, path resolution, validation |
| Workspace Context | `skills/.../utils/context.py` | `SourceContext`, `WorkspaceContext`, context upgrade, artifact path resolution, cross-repo ID collection |
| Workspace Init | `skills/.../commands/workspace_init.py` | `workspace-init` command: nested sub-directory scanning, role inference, config generation |
| Workspace Add | `skills/.../commands/workspace_add.py` | `workspace-add` command (with `--inline` flag for inline mode) |
| Workspace Info | `skills/.../commands/workspace_info.py` | `workspace-info` command: status display, per-source probe |
| Workspace Sync | `skills/.../commands/workspace_sync.py` | `workspace-sync` command: fetch and update Git URL source worktrees |
| Git Utils | `skills/.../utils/git_utils.py` | Git URL parsing, namespace resolution, clone operations, sync operations |
| Artifacts Meta | `skills/.../utils/artifacts_meta.py` | Source field support on `Artifact` dataclass |

## 7. Acceptance Criteria

- [x] `workspace-init` scans nested sub-directories and generates `.cypilot-workspace.toml` with discovered sources
- [x] `workspace-init --max-depth N` limits scanning depth (default 3); symlinks are skipped
- [x] `workspace-init --inline` writes workspace config into `config/core.toml` `[workspace]` section
- [x] `workspace-init --dry-run` shows preview without writing files
- [x] `workspace-add --name N --path P` adds a source to standalone workspace config
- [x] `workspace-add --inline --name N --path P` adds a source inline to `core.toml`
- [x] `workspace-add --name N --path P` with existing name N returns error without `--force`
- [x] `workspace-add --name N --path P --force` replaces existing source N
- [x] Type mismatch (standalone add on inline config) produces error with correct command hint
- [x] `workspace-info` displays workspace status with per-source reachability and artifact counts
- [x] Workspace config discovery checks `core.toml` `workspace` key first, then falls back to standalone `.cypilot-workspace.toml` at project root (no parent directory walk-up)
- [x] Source paths resolve relative to workspace file parent (standalone) or project root (inline)
- [x] Context loading upgrades to `WorkspaceContext` when workspace config is found
- [x] `resolve_artifact_path` returns `None` for unreachable sources (no silent fallback)
- [x] Unreachable sources emit stderr warnings; operations continue with available sources
- [x] Projects without workspace config operate in single-repo mode with zero behavioral changes
- [x] All workspace commands output JSON to stdout and use exit codes 0/1/2
- [x] Standalone workspace config supports Git URL sources with `url` field on `SourceEntry`
- [x] Workspace config supports `[resolve]` section with `workdir` and namespace resolution rules
- [x] Namespace rules map Git URL host/path to local directory paths (e.g., `gitlab.com/org/repo.git` → `org/repo`)
- [x] Per-source and workspace-level branch/ref configuration supported
- [x] Git URL sources are cloned on first access under the configured working directory; subsequent accesses return local path without network operations
- [x] Inline workspace config (`core.toml`) remains local-paths-only — Git URL sources not supported inline
- [x] Cross-repo editing applies the remote source's own adapter rules/templates/constraints, not the primary repo's
- [x] `SourceContext` resolves per-source adapter context independently for validation and generation
- [x] `validate --artifact` auto-detects which workspace source owns the artifact via `determine_target_source()` (longest-prefix path match) — no explicit `--source` flag required
- [x] `validate` uses `WorkspaceContext.get_all_artifact_ids()` for cross-repo ID expansion instead of inline aggregation
- [x] `where-defined` and `where-used` work transparently in workspace mode via `collect_artifacts_to_scan` — no per-command source flags needed
- [x] `WorkspaceConfig.resolve_source_adapter()` is used by context loading and `workspace-info` to resolve adapter paths centrally
- [x] `workspace-sync` fetches and updates worktrees for all Git URL sources
- [x] `workspace-sync --source N` syncs only the named source
- [x] `workspace-sync --dry-run` shows which sources would be synced without network operations
- [x] `workspace-sync` reports per-source sync results (synced/failed with error details)
- [x] `resolve_source_path` does not perform `git fetch` for existing repos (clone-only on first access)
