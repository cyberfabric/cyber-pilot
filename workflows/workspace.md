---
cypilot: true
type: workflow
name: cypilot-workspace
description: Multi-repo workspace setup — discover repos, configure sources, generate workspace config, validate
version: 1.0
purpose: Guide workspace federation setup for cross-repo traceability
---

# Cypilot Workspace Workflow

ALWAYS open and follow `{cypilot_path}/skills/cypilot/SKILL.md` FIRST WHEN {cypilot_mode} is `off`

**Type**: Operation
**Role**: Any
**Output**: `.cypilot-workspace.json` or inline `[workspace]` in `config/core.toml`

---

## Overview

This workflow guides multi-repo workspace setup — discovering sibling repos, configuring source roles, generating workspace config, and validating cross-repo traceability.

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
- [ ] Agent knows workspace can be standalone `.cypilot-workspace.json` or inline in `config/core.toml`

---

## Phase 1: Discover

**Goal**: Scan the filesystem neighborhood for repos that could be workspace sources.

### Steps

1. **Identify current project root**
   ```bash
   python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py info
   ```

2. **Scan sibling directories** for repos with `.git` or `AGENTS.md` with `@cpt:root-agents` marker
   ```bash
   python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py workspace-init --dry-run
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
   - Cross-repo traceability enabled? (default: yes)
   - Resolve remote IDs? (default: yes)

3. **Confirm workspace location**:
   - Option A: Standalone `.cypilot-workspace.json` at super-root (parent of repos)
   - Option B: Inline `[workspace]` section in current repo's `config/core.toml`

### Key Design Principle

> The **primary source** is always determined by which repo contains the current working directory. No `primary` field is needed in the workspace config.

---

## Phase 3: Generate

**Goal**: Write the workspace configuration file.

### Option A: Standalone file

```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py workspace-init [--root <super-root>] [--output <path>]
```

### Option B: Inline in config

```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py workspace-init --inline
```

### Adding individual sources

```bash
# Add to standalone workspace file
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py workspace-add --name <name> --path <path> [--role <role>] [--adapter <adapter-path>]

# Add inline to core.toml
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py workspace-add-inline --name <name> --path <path> [--role <role>]
```

### Generated file structure

**Standalone `.cypilot-workspace.json`:**
```json
{
  "version": "1.0",
  "sources": {
    "docs-repo": {
      "path": "../docs-repo",
      "adapter": "cypilot",
      "role": "artifacts"
    },
    "code-repo": {
      "path": "../code-repo",
      "adapter": ".bootstrap",
      "role": "codebase"
    }
  }
}
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
   python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py workspace-info
   ```

2. **Check each source**:
   - [ ] Path resolves to existing directory
   - [ ] Cypilot directory found (auto-discovered or explicit adapter)
   - [ ] artifacts.toml valid (if cypilot directory present)
   - [ ] At least one system registered (if cypilot directory present)

3. **Test cross-repo operations**:
   ```bash
   # List IDs across all sources
   python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py list-ids

   # Validate with cross-repo resolution
   python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate
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

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `workspace-init` | Scan and generate workspace config |
| `workspace-init --inline` | Generate inline workspace in core.toml |
| `workspace-init --dry-run` | Preview without writing files |
| `workspace-add --name N --path P` | Add source to standalone workspace |
| `workspace-add-inline --name N --path P` | Add source inline to core.toml |
| `workspace-info` | Show workspace status and sources |
| `validate --local-only` | Validate without cross-repo resolution |
| `list-ids --source <name>` | List IDs from specific source only |

---

## Next Steps

**After successful workspace setup**:

- Run `validate` from each participating repo to verify cross-repo ID resolution works
- Use `list-ids` to confirm artifacts from all sources are visible
- Add `source` fields to `artifacts.toml` entries that reference remote repos
- Consider adding workspace setup to project onboarding documentation
