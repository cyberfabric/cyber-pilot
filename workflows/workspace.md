---
cypilot: true
type: workflow
name: cypilot-workspace
description: Multi-repo workspace setup — discover repos, configure sources, generate workspace config, validate
version: 1.0
purpose: Guide workspace federation setup for cross-repo traceability
---

# Cypilot Workspace Workflow

ALWAYS open and follow `{cypilot_path}/config/AGENTS.md` FIRST.
ALWAYS open and follow `{cypilot_path}/.gen/AGENTS.md` after config/AGENTS.md.

**Type**: Operation
**Role**: Any
**Output**: `.cypilot-workspace.toml` or inline `[workspace]` in `config/core.toml`

---

## Overview

This workflow guides multi-repo workspace setup — discovering repos in nested sub-directories, configuring source roles, generating workspace config, and validating cross-repo traceability.

### Routing

This workflow is invoked through the main Cypilot workflows or directly via workspace commands:

| User Intent | Route | Example |
|-------------|-------|---------|
| Create/configure workspace | **generate.md** → workspace.md | "setup multi-repo workspace", "add source repo" |
| Check workspace status | **analyze.md** (workspace target) | "check workspace", "show workspace sources" |

**Direct invocation** via workspace quick commands skips Protocol Guard.

---

## Table of Contents

1. [Phase 1: Discover](#phase-1-discover)
2. [Phase 2: Configure](#phase-2-configure)
3. [Phase 3: Generate](#phase-3-generate)
4. [Phase 4: Validate](#phase-4-validate)

---

## Prerequisite Checklist

- [ ] Agent has read SKILL.md
- [ ] Agent understands multi-repo workspace concepts
- [ ] Agent knows workspace can be standalone `.cypilot-workspace.toml` or inline in `config/core.toml`

---

## Phase 1: Discover

**Goal**: Scan the filesystem neighborhood for repos that could be workspace sources.

### Steps

1. **Identify current project root**
   ```bash
   python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json info
   ```

2. **Scan nested sub-directories** for repos with `.git` or `AGENTS.md` with `@cpt:root-agents` marker
   ```bash
   python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json workspace-init --dry-run
   ```

3. **Present discovered repos** to user with:
   - Repo name and path
   - Whether cypilot directory was found
   - Inferred role (artifacts / codebase / kits / full)

### Decision Point

- [ ] User confirms which repos to include as workspace sources
- [ ] User specifies preferred workspace location (super-root standalone file vs inline in current repo)

---

## Phase 2: Configure

**Goal**: Define source roles and workspace structure based on user preferences.

### Steps

1. **For each selected source**, confirm:
   - **Name**: Human-readable key for the source (e.g., "docs-repo", "shared-kits")
   - **Path**: Relative filesystem path from workspace file location
   - **Role**: What the source contributes (`artifacts`, `codebase`, `kits`, or `full`)
   - **Adapter**: Path to cypilot directory within the source (auto-discovered via AGENTS.md), or `null` if none

2. **Confirm traceability settings**:
   - Cross-repo traceability enabled? (`cross_repo`, default: yes) — enables workspace-aware path resolution
   - Resolve remote IDs? (`resolve_remote_ids`, default: yes) — expands remote source artifact IDs into the union set for cross-reference validation. Both must be true for remote IDs to be included.

3. **Confirm workspace location**:
   - Option A: Standalone `.cypilot-workspace.toml` at the current project root (auto-discovered), or at another path referenced explicitly from `config/core.toml`
   - Option B: Inline `[workspace]` section in current repo's `config/core.toml`

### Key Design Principle

> The **primary source** is always determined by which repo contains the current working directory. No `primary` field is needed in the workspace config.

---

## Phase 3: Generate

**Goal**: Write the workspace configuration file.

```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py workspace-init [--root <super-root>] [--output <path>] [--inline] [--force] [--dry-run]
```

- Without `--inline`: generates standalone `.cypilot-workspace.toml`
- With `--inline`: writes `[workspace]` section into `config/core.toml`

### Adding individual sources

```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py workspace-add --name <name> (--path <path> | --url <url>) [--branch <branch>] [--role <role>] [--adapter <path>] [--inline]
```

- Without `--inline`: adds to standalone workspace (auto-detects inline workspace and routes accordingly)
- With `--inline`: forces add to `config/core.toml` (Git URL sources not supported inline)

### Generated file structure

**Standalone `.cypilot-workspace.toml`:**
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
```

**Inline in `config/core.toml`:**
```toml
[workspace.sources.docs]
path = "../docs-repo"
role = "artifacts"

[workspace.sources.shared-kits]
path = "../shared-kits"
role = "kits"
```

---

## Phase 4: Validate

**Goal**: Verify all sources are reachable and adapters are valid.

### Steps

1. **Run workspace info**:
   ```bash
   python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json workspace-info
   ```

2. **Check each source**:
   - [ ] Path resolves to existing directory
   - [ ] Cypilot directory found (auto-discovered or explicit adapter)
   - [ ] artifacts.toml valid (if cypilot directory present)
   - [ ] At least one system registered (if cypilot directory present)

3. **Test cross-repo operations**:
   ```bash
   # List IDs across all sources
   python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json list-ids

   # Validate with cross-repo resolution
   python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json validate
   ```

4. **Report**:
   - Total sources: N
   - Reachable sources: N
   - Sources with cypilot directories: N
   - Cross-repo IDs available: N

### Graceful Degradation

When a source repo is not found on disk:
- **Warning** is emitted (not an error)
- Remaining sources continue to work
- Cross-repo IDs from missing sources are simply unavailable
- Artifacts with an explicit `source` pointing to an unreachable repo resolve to `None` and are skipped (no silent fallback to local)
- Scan failures on individual artifact files emit warnings to stderr but do not block the overall operation

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `workspace-init [--root <dir>] [--output <path>] [--inline] [--force] [--dry-run]` | Scan and generate workspace config (standalone or inline) |
| `workspace-add --name <name> [--path <path> \| --url <url>] [--branch <branch>] [--role <role>] [--adapter <path>] [--inline] [--force]` | Add source to workspace config (auto-detects type) |
| `workspace-info` | Show workspace status and sources |
| `workspace-sync [--source <name>] [--dry-run] [--force]` | Fetch and update Git URL source worktrees |
| `validate --local-only` | Validate without cross-repo resolution |
| `list-ids --source <name>` | List IDs from specific source only |

---

## Next Steps

**After successful workspace setup**:

- Run `validate` from each participating repo to verify cross-repo ID resolution works
- Use `list-ids` to confirm artifacts from all sources are visible
- Add `source` fields to `artifacts.toml` entries that reference remote repos
- Consider adding workspace setup to project onboarding documentation
