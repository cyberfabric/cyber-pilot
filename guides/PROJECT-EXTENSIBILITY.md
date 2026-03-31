# Project-Level Extensibility Guide

This guide explains how Cypilot's manifest hierarchy enables projects and orchestrator repos to declare their own skills, agents, workflows, and rules — all discoverable by `cpt generate-agents`.

## Table of Contents

- [Project-Level Extensibility Guide](#project-level-extensibility-guide)
  - [Table of Contents](#table-of-contents)
  - [The Problem](#the-problem)
  - [The Orchestrator Repo Pattern](#the-orchestrator-repo-pattern)
  - [Four-Layer Manifest Hierarchy](#four-layer-manifest-hierarchy)
    - [Filesystem Layout](#filesystem-layout)
    - [Resolution Semantics](#resolution-semantics)
  - [Manifest Format](#manifest-format)
    - [Component Sections](#component-sections)
    - [Includes Directive](#includes-directive)
    - [Agent Definitions](#agent-definitions)
    - [Extended Agent Fields](#extended-agent-fields)
    - [Skill Definitions](#skill-definitions)
    - [Workflow Definitions](#workflow-definitions)
    - [Rule Definitions](#rule-definitions)
    - [Hook Definitions (Future)](#hook-definitions-future)
    - [Permissions (Future)](#permissions-future)
  - [Section Appending](#section-appending)
  - [Cross-Agent Translation](#cross-agent-translation)
  - [Examples](#examples)
    - [Standalone Repo](#standalone-repo)
    - [Multi-Repo Hierarchy with Includes](#multi-repo-hierarchy-with-includes)
    - [The standctl Case](#the-standctl-case)
  - [Discovery Mode](#discovery-mode)
  - [Backward Compatibility](#backward-compatibility)
  - [Relationship with Workspace Federation](#relationship-with-workspace-federation)
    - [How They Compose](#how-they-compose)
    - [Orchestrator Repo with Sub-Projects](#orchestrator-repo-with-sub-projects)
    - [Current Limitations](#current-limitations)
    - [Potential Improvements](#potential-improvements)
  - [Future Work](#future-work)

---

## The Problem

Cypilot generates agent entry points (skills, workflows, subagents) for five AI coding tools from a built-in registry. Without project-level extensibility, there is no mechanism for individual projects to:

1. **Add their own skills** — a project that defines custom skills, agents, or workflows cannot register them through `cpt generate-agents`
2. **Extend base templates** — projects cannot augment Cypilot's generated SKILL.md or workflow proxies with project-specific content
3. **Register custom agents/subagents** — project-level agents live outside Cypilot's awareness
4. **Include component packages** — tools like standctl that distribute agents and skills as subdirectories within a repo have no way to participate in generation

The result: project-level components work as standalone agent features but aren't portable across agent tools and aren't managed by `cpt generate-agents`.

---

## The Orchestrator Repo Pattern

Cypilot supports an **orchestrator repo** pattern — a parent repository that organizes and coordinates many independent project repos. This provides monorepo-like discoverability with multi-repo isolation.

The orchestrator repo holds:
- Organization-wide skills, agents, and rules (available to all child repos)
- Shared templates and conventions (inherited via manifest hierarchy)
- The filesystem structure that `cpt generate-agents` walks to discover what applies where

Each child repo remains an independent git repository with its own CI, permissions, and history. When Cypilot runs inside a child repo, it walks up the filesystem to discover what the orchestrator provides — and merges those contributions into the generated output.

This follows a git/golang-style convention for repo organization:

```text
{base_dir}/orchestrator-repo/git/{host}/{project}/{repo}
```

Where `{base_dir}` defaults to `~` or `~/code` and is configurable via:
- Environment variable: `CYPILOT_BASE_DIR`
- Master repo config: `[manifest] base_dir = "~/code"`
- Explicit flag: `cpt generate-agents --base-dir ~/code`

---

## Four-Layer Manifest Hierarchy

When `cpt generate-agents` runs, it resolves components from four layers. Innermost scope wins on conflicts:

```text
┌─────────────────────────────────────────────────────────────────┐
│  4. Repo Layer                                                  │
│     .bootstrap/config/manifest.toml                             │
│     Repo-specific agents, skills, rules                         │
├─────────────────────────────────────────────────────────────────┤
│  3. Master Repo Layer                                           │
│     {base_dir}/orchestrator/manifest.toml                       │
│     Shared across all repos in the orchestrator                 │
├─────────────────────────────────────────────────────────────────┤
│  2. Kit Layer                                                   │
│     manifest.toml in installed kit package                      │
│     [[resources]], [[agents]], etc.                              │
├─────────────────────────────────────────────────────────────────┤
│  1. Core Layer (cyber-pilot)                                    │
│     Built-in workflows, SKILL.md, AGENTS.md                     │
└─────────────────────────────────────────────────────────────────┘
```

> **Future**: Organization (git host root) and Project (parent of repo dir) layers will be added in a follow-up, expanding to six layers.

### Filesystem Layout

```text
~/code/                                  # base_dir
└── orchestrator-repo/                   # Layer 3: Master repo
    ├── manifest.toml
    ├── skills/
    ├── standctl/                        # Included via includes directive
    │   ├── manifest.toml
    │   └── agents/
    └── git/
        └── git.example.com/
            └── my-project/
                ├── service-a/          # Layer 4: Repo
                │   ├── .bootstrap/config/
                │   │   └── manifest.toml
                │   └── ...
                └── service-b/
                    └── ...
```

### Resolution Semantics

**Walk-up discovery**: When `cpt generate-agents` runs inside a repo, it walks up the directory tree looking for the master repo boundary:

- **Repo**: presence of `.bootstrap/` or `.cypilot-config.json`
- **Master repo**: `CLAUDE.md` + `skills/` at same level, or presence of `git/` subdirectory

**Merge order**: Innermost scope wins for the same component ID:
```text
Core → Kit → Master Repo → Repo
                             ↑ wins
```

**Section appending** stacks across layers — each layer can append content to generated templates.

Walk-up discovery stops at the master repo root. If no master repo is found, only Core + Kit + Repo layers apply — this is the standalone-repo case, fully backward compatible.

---

## Manifest Format

All layers use the same `manifest.toml` format. Version `"2.0"` enables component sections; version `"1.0"` manifests (resources-only) continue to work unchanged.

```toml
[manifest]
version = "2.0"
scope = "repo"    # "kit", "master", "repo"
```

The `scope` field is informational — layer identity is determined by filesystem position during walk-up discovery.

### Component Sections

A manifest can declare any combination of components:

```toml
[[agents]]      # Agent/subagent definitions
[[skills]]      # Skill definitions
[[workflows]]   # Workflow definitions
[[rules]]       # Rule definitions
[[hooks]]       # Hook definitions (reserved — not yet implemented)
[[permissions]] # MCP tool allowlisting (reserved — not yet implemented)
[[resources]]   # Kit resource bindings (kit layer only)
```

### Includes Directive

Manifests can include subdirectory manifests using the `includes` array. This enables component packages (like standctl) to live as subdirectories within a repo while participating in generation:

```toml
[manifest]
version = "2.0"
scope = "repo"

includes = [
  "standctl/manifest.toml",
  "another-tool/manifest.toml",
]
```

**Semantics**:
- Paths are relative to the directory containing the including manifest
- Included manifests are loaded at the **same layer** as the includer (they don't create a new layer)
- `prompt_file` and `source` paths in included manifests resolve relative to the *included* manifest's directory (not the includer's)
- Component ID collisions between includer and includee are **errors** (not silent overrides)
- Circular includes are detected and rejected
- Includes are processed recursively (an included manifest can have its own `includes`), max depth: 3

**Why `includes` over alternatives**:

| Alternative | Why not |
|---|---|
| Flatten everything into root manifest | Breaks modularity — standctl's definitions belong with standctl's content |
| Register subdirs as "kits" | Kits are installable packages with versioning; standctl is just a folder |
| Convention-based scanning (`**/manifest.toml`) | Expensive, implicit, fragile |
| Symlinks | Platform-dependent, git doesn't handle well |

### Agent Definitions

Agent definitions use an extended semantic schema that translates to tool-native frontmatter:

```toml
[[agents]]
id = "go-stand-deployer"
description = "Build and deploy Go projects to test stands"
prompt_file = "agents/go-stand-deployer.md"    # relative to manifest dir
mode = "readwrite"                              # "readwrite" or "readonly"
isolation = false                               # worktree isolation (Claude Code)
model = "sonnet"                                # any string: inherit, fast, sonnet, haiku, opus, etc.
agents = ["claude", "cursor", "copilot"]        # which tools to generate for
```

### Extended Agent Fields

Beyond the base fields, agents can declare tool-specific properties:

```toml
[[agents]]
id = "go-stand-deployer"
description = "Build and deploy Go projects to test stands"
prompt_file = "agents/go-stand-deployer.md"
mode = "readwrite"
isolation = false
model = "sonnet"

# Extended fields
color = "pink"                                              # Claude Code only
memory_dir = ".claude/agent-memory/go-stand-deployer"       # Persistent memory path
tools = [                                                   # Explicit tool allowlist
  "mcp__standctl__standctl_login",
  "mcp__standctl__standctl_deploy",
  "mcp__standctl__standctl_pods",
  "Bash", "Read", "Write", "Edit", "Glob", "Grep",
]
# disallowed_tools = ["Write", "Edit"]                      # Alternative: denylist (mutually exclusive with tools)

agents = ["claude", "cursor", "copilot", "openai"]
```

| Field | Type | Description | Claude | Cursor | Copilot | Codex |
|-------|------|-------------|--------|--------|---------|-------|
| `tools` | string[] | Explicit tool allowlist | `tools:` list | limited | `tools` array | n/a (MCP level) |
| `disallowed_tools` | string[] | Explicit tool denylist | `disallowedTools:` | n/a | n/a | n/a |
| `color` | string | Agent color | `color:` | n/a | n/a | n/a |
| `memory_dir` | string | Persistent memory path | prompt body | n/a | n/a | n/a |
| `model` | string | Model selection (passthrough) | `model:` | `model:` | n/a | `model` |
| `mode` | string | Access level | tools/disallowed | `readonly:` | tools | `sandbox_mode` |
| `isolation` | bool | Isolated context | `isolation: worktree` | n/a | n/a | n/a |

**Codex-specific mapping**: `mode: readonly` → `sandbox_mode = "read-only"`, `mode: readwrite` → `sandbox_mode = "workspace-write"`. Per-agent tool restrictions are not supported in Codex (managed at MCP server level).

**`tools` and `disallowed_tools` are mutually exclusive** — specifying both on the same agent is an error.

### Skill Definitions

```toml
[[skills]]
id = "standctl"
description = "Standctl MCP tools usage guide for test stand management"
prompt_file = "skills/standctl/SKILL.md"    # relative to manifest dir
agents = ["claude", "cursor", "windsurf"]
```

Skills generate agent-native skill files. For Claude Code: `.claude/skills/{id}/SKILL.md`. For Cursor: `.cursor/rules/{id}.mdc`. Manifest skills coexist with kit-composed skills (the `@cpt:skill` mechanism) — they use different code paths and output directories.

### Workflow Definitions

```toml
[[workflows]]
id = "deploy"
description = "Build, push, and deploy to a test stand"
source = "skills/deploy.py"
agents = ["claude", "cursor", "windsurf"]
```

### Rule Definitions

```toml
[[rules]]
id = "standctl-conventions"
description = "Conventions for interacting with test stands"
source = "guidelines/standctl.md"
agents = ["claude", "cursor", "windsurf"]
```

### Hook Definitions (Future)

> **Note**: Hook support is reserved in the schema but not yet implemented. The `[[hooks]]` section will be supported in a follow-up feature.

```toml
# Example (not yet supported):
[[hooks]]
event = "SessionEnd"
command = "standctl review-session --hook"
agents = ["claude"]
```

### Permissions (Future)

> **Note**: Permissions support is reserved in the schema but not yet implemented. This is an important follow-up — granting MCP tool permissions is currently a manual, time-consuming process for projects using MCP servers.

```toml
# Example (not yet supported):
[[permissions]]
id = "standctl-mcp-tools"
description = "Allow standctl MCP tools for stand management"
target_agent = "claude"
allow = [
  "mcp__standctl__standctl_curl",
  "mcp__standctl__standctl_pods",
  "mcp__standctl__standctl_logs",
  # ... (17 tools total for standctl)
]
```

When implemented, `cpt generate-agents` will merge `allow` entries into `.claude/settings.local.json` (additive, idempotent). Without this, importing a tool like standctl via cypilot still requires manually running the tool's own setup command just for the permissions side-effect.

---

## Section Appending

For MVP, template composition uses section appending — inner layers can append content to generated templates. Each component can declare `append` content that is added after the base content.

```toml
# Master repo manifest — append standctl tools to the skill
[[skills]]
id = "standctl"
description = "Standctl MCP tools"
prompt_file = "skills/standctl/SKILL.md"
agents = ["claude"]
append = """

## Stand Management Quick Reference
- `standctl pods` — List pods
- `standctl logs` — View logs
- `standctl deploy` — Deploy image
"""
```

Appends from multiple layers stack in resolution order (outermost first, innermost last).

> **Future**: Full block-based template composition with `<!-- @block:NAME -->` markers and operations (replace, prepend, append, delete, insert_after, insert_before) will be added in a follow-up feature.

---

## Cross-Agent Translation

Each component type maps to agent-native formats. `cpt generate-agents` handles the translation:

| Component | Claude | Cursor | Windsurf | Copilot | Codex |
|-----------|--------|--------|----------|---------|-------|
| Skill | `.claude/skills/*/SKILL.md` | `.cursor/rules/*.mdc` | `.windsurf/skills/*/SKILL.md` | `.github/prompts/*.prompt.md` | — |
| Workflow | `.claude/commands/*.md` | `.cursor/commands/*.md` | `.windsurf/workflows/*.md` | `.github/prompts/*.prompt.md` | — |
| Agent | `.claude/agents/*.md` (YAML frontmatter) | `.cursor/agents/*.md` (YAML frontmatter) | — (no subagents) | `.github/agents/*.agent.md` (YAML frontmatter) | `.codex/agents/` (TOML config) |
| Hook | `.claude/settings.json` | — | — | — | — |
| Rule | `CLAUDE.md` managed block | `.cursor/rules/*.mdc` | `.windsurf/rules/*.md` | `.github/copilot-instructions.md` | — |

Where a tool doesn't support a component type natively, Cypilot either embeds it in the nearest equivalent or skips it with a note in the generation report.

**Codex agent format**:

Unlike the markdown-based tools, Codex uses TOML configuration:

```toml
[agents.go_stand_deployer]
description = "Build and deploy Go projects to test stands"
sandbox_mode = "workspace-write"
model = "gpt-5-codex"
developer_instructions = """
ALWAYS open and follow `.bootstrap/config/agents/go-stand-deployer.md`
"""
```

Key differences: `mode` maps to `sandbox_mode`, per-agent tool restrictions are managed at MCP server level (not in agent config), and `color`/`memory_dir` have no Codex equivalent.

---

## Examples

### Standalone Repo

For repos not inside an orchestrator hierarchy, only Core + Kit + Repo layers apply. Add a `manifest.toml` to your adapter config:

```toml
# .bootstrap/config/manifest.toml
[manifest]
version = "2.0"
scope = "repo"

[[skills]]
id = "my-custom-skill"
description = "Project-specific skill"
prompt_file = ".claude/skills/custom/SKILL.md"
agents = ["claude"]

[[agents]]
id = "test-runner"
description = "Run and analyze test failures"
prompt_file = ".claude/agents/test-runner.md"
mode = "readwrite"
isolation = true
model = "inherit"
agents = ["claude", "cursor"]
```

Then regenerate:

```bash
cpt generate-agents --agent claude
```

Your custom skill and agent appear alongside Cypilot's built-in outputs.

### Multi-Repo Hierarchy with Includes

A full orchestrator setup showing the `includes` directive for component packages:

**Master repo** (`orchestrator/manifest.toml`):
```toml
[manifest]
version = "2.0"
scope = "master"
base_dir = "~/code"

# Include component packages from subdirectories
includes = [
  "standctl/manifest.toml",
]

[[skills]]
id = "org-conventions"
description = "Organization-wide coding conventions"
prompt_file = "skills/org-conventions/SKILL.md"
agents = ["claude", "cursor", "windsurf"]
```

**Included standctl package** (`orchestrator/standctl/manifest.toml`):
```toml
[manifest]
version = "2.0"

[[agents]]
id = "go-stand-deployer"
description = "Build and deploy Go projects to Acronis test stands"
prompt_file = "agents/go-stand-deployer.md"
mode = "readwrite"
isolation = false
model = "sonnet"
color = "pink"
memory_dir = ".claude/agent-memory/go-stand-deployer"
tools = [
  "mcp__standctl__standctl_login",
  "mcp__standctl__standctl_deploy",
  "mcp__standctl__standctl_pods",
  "mcp__standctl__standctl_logs",
  "Bash", "Read", "Write", "Edit", "Glob", "Grep",
]
agents = ["claude", "cursor", "copilot", "openai"]

[[agents]]
id = "stand-log-investigator"
description = "Analyze logs and debug issues on Acronis test stands"
prompt_file = "agents/stand-log-investigator.md"
mode = "readonly"
isolation = false
model = "haiku"
color = "orange"
memory_dir = ".claude/agent-memory/stand-log-investigator"
tools = [
  "mcp__standctl__standctl_pods",
  "mcp__standctl__standctl_logs",
  "mcp__standctl__standctl_configmap",
  "Read", "Glob", "Grep",
]
agents = ["claude"]

[[skills]]
id = "standctl"
description = "Standctl MCP tools usage guide for test stand management"
prompt_file = "skills/standctl/SKILL.md"
agents = ["claude", "cursor", "windsurf"]
```

Note: `prompt_file` paths in `standctl/manifest.toml` resolve relative to `orchestrator/standctl/` (the included manifest's directory), not `orchestrator/`.

**Repo** (`my-project/service-a/.bootstrap/config/manifest.toml`):
```toml
[manifest]
version = "2.0"
scope = "repo"

[[agents]]
id = "log-investigator"
description = "Investigate service-a logs for pipeline issues"
prompt_file = ".claude/agents/log-investigator.md"
mode = "readonly"
isolation = false
model = "fast"
agents = ["claude"]
```

Running `cpt generate-agents --agent claude` inside `service-a/` produces merged output from all layers:
- Kit agents (`cypilot-codegen`, `cypilot-pr-review`)
- Master repo skill (`org-conventions`), included standctl agents + skill
- Repo agent (`log-investigator`)

### The standctl Case

The standctl integration is the motivating use case for this feature. standctl is a Go CLI that distributes agents, skills, and MCP tool permissions into consuming projects. With project-level extensibility:

**Before** (manual, per-tool):
```bash
standctl agent go-stand-deployer    # installs agent for current tool
standctl agent stand-log-investigator
standctl skill                       # installs skill
standctl agent                       # sets up permissions
```

**After** (declarative, all tools at once):
```bash
cpt generate-agents --agent claude   # generates everything from manifest
```

The standctl `manifest.toml` (shown in the multi-repo example above) declares all three agents and the skill. `cpt generate-agents` translates them to each target tool's native format. Permissions remain manual for now (see [Future Work](#future-work)).

---

## Discovery Mode

For projects that don't want to manually enumerate components, use auto-discovery:

```bash
cpt generate-agents --agent claude --discover
```

Discovery scans conventional directories:
- `.claude/agents/*.md` → project agents
- `.claude/skills/*/SKILL.md` → project skills
- `.claude/commands/*.md` → project workflows

Discovery writes found components into the project `manifest.toml`. Subsequent runs read it declaratively — similar to how `cpt kit install` writes resource bindings into `core.toml`.

---

## Backward Compatibility

- **v1 manifests**: `manifest.version = "1.0"` manifests (resources-only) continue to work unchanged
- **`agents.toml` fallback**: `_discover_kit_agents()` checks `manifest.toml` `[[agents]]` first, falls back to `agents.toml` if present
- **Standalone repos**: without an orchestrator hierarchy, only Core + Kit + Repo layers apply — identical to the previous behavior
- **No new CLI commands**: everything extends the existing `cpt generate-agents`
- **Model passthrough**: existing `inherit` and `fast` values continue to work; new model names (e.g., `sonnet`, `haiku`) are accepted as passthrough strings

---

## Relationship with Workspace Federation

Cypilot has two complementary multi-repo mechanisms that address different dimensions of working across repositories:

| | Project Extensibility (this feature) | Workspace Federation |
|---|---|---|
| **Direction** | Vertical — walks *up* the filesystem from repo to orchestrator | Horizontal — federates *across* sibling repositories |
| **Config file** | `manifest.toml` at each layer boundary | `.cypilot-workspace.toml` or inline in `core.toml` |
| **Discovery** | `discover_layers()` — finds manifest layers by walking parent directories to a master repo boundary | `find_workspace_config()` — finds workspace config at project root, then resolves named sources |
| **Merge model** | Component merging with innermost-wins precedence and provenance tracking | No merging — each source keeps its own independent adapter context |
| **Primary use case** | Agent/skill/workflow generation via `cpt generate-agents` | Cross-repo artifact traceability via `cpt validate`, `cpt list-ids`, `cpt where-defined` |
| **Runtime type** | `ManifestLayer`, `MergedComponents` | `WorkspaceContext`, `SourceContext` |

### How They Compose

The two features operate on independent axes and do not conflict:

```text
                    Workspace Federation (horizontal)
                    ┌──────────┬──────────┬──────────┐
                    │ source-a │ source-b │ source-c │
                    └────┬─────┴────┬─────┴────┬─────┘
                         │          │          │
Project Extensibility    │          │          │
(vertical, per-source)   ▼          ▼          ▼
                    ┌─────────┐┌─────────┐┌─────────┐
                    │ Repo    ││ Repo    ││ Repo    │
                    │ Master  ││ Master  ││ Master  │
                    │ Kit     ││ Kit     ││ Kit     │
                    │ Core    ││ Core    ││ Core    │
                    └─────────┘└─────────┘└─────────┘
```

- **Workspace commands** (`workspace-init`, `workspace-add`, `validate --source`) manage cross-repo source federation and artifact traceability. They use `WorkspaceContext` and `SourceContext`.
- **Extensibility commands** (`generate-agents`, `generate-agents --show-layers`) manage per-repo agent/skill generation from the manifest layer hierarchy. They use `discover_layers()` and `merge_components()`.

### Orchestrator Repo with Sub-Projects

A common deployment pattern is a quasi-mono-repo: an orchestration repository that contains many sub-projects for specific aspects of a system — services, libraries, infrastructure, documentation, etc. Each sub-project may be a Git submodule, a nested repository, or simply a subdirectory with its own Cypilot adapter. The orchestration repo itself holds shared configuration, organization-wide rules, and cross-cutting agents, while each sub-project maintains its own independent adapter.

```text
orchestrator-repo/                          ← the orchestration repo (has .git/, CLAUDE.md, skills/)
├── manifest.toml                           ← master layer: org-wide agents, rules
├── .cypilot-workspace.toml                 ← workspace config federating sub-projects
├── service-a/                              ← sub-project with its own .bootstrap/
│   └── .bootstrap/config/manifest.toml     ← repo layer for service-a
├── service-b/
│   └── .bootstrap/config/manifest.toml
└── infra/
    └── .bootstrap/config/manifest.toml
```

This structure supports two distinct working modes, each engaging different combinations of the two features:

#### Mode 1: Multi-Project Scope (working from the orchestration repo root)

The developer opens or branches the orchestration repo itself — their working directory is the orchestration repo root. This is common for cross-cutting changes that span multiple sub-projects, or for reviewing the system as a whole.

**What activates**:

- **Workspace federation**: if the orchestration repo has a `.cypilot-workspace.toml` (or inline `[workspace]` in `core.toml`), context loading upgrades to `WorkspaceContext`. Each sub-project becomes a named source with its own `SourceContext`, enabling cross-repo traceability — `cpt validate`, `cpt list-ids`, and `cpt where-defined` resolve artifacts across all federated sources.
- **Layer discovery**: `discover_layers()` runs from the orchestration repo's own `.bootstrap/` root. It finds the orchestration repo's kit layers and repo-layer manifest. Since the orchestration repo *is* the master repo boundary (it has `.git/`), the walk-up stops there — no master layer is added above it.

**Net effect**: traceability spans the full workspace; agent generation uses the orchestration repo's own manifest hierarchy. Sub-project manifests are not merged into the orchestration repo's agent generation — each sub-project's agents are generated independently (see [Current Limitations](#current-limitations)).

#### Mode 2: Single-Project Scope (working from within a sub-project)

The developer's working directory is inside a specific sub-project — e.g., `orchestrator-repo/service-a/`. This is the common case for feature work scoped to one service.

**What activates**:

- **Layer discovery**: `discover_layers()` runs from `service-a/.bootstrap/`. It loads the kit layers and repo-layer manifest from `service-a/.bootstrap/config/manifest.toml`. It then walks up from `service-a/` and finds the orchestration repo as a master repo boundary (via `.git/` or `CLAUDE.md` + `skills/`). If the orchestration repo has a `manifest.toml` at its root, that becomes the **master layer** — its agents, skills, and rules merge into service-a's generation with the repo layer winning on conflicts.
- **Workspace federation**: if `service-a` has its own workspace config, it activates independently. More commonly, the sub-project has no workspace config and operates in single-repo mode — `CypilotContext` without `WorkspaceContext`.

**Net effect**: the sub-project inherits organization-wide agents and rules from the orchestration repo's master-layer manifest, while its own repo-layer manifest can override or extend them. Cross-repo traceability is not active unless the sub-project has its own workspace config.

#### Choosing Between Modes

| Concern | Multi-Project (orchestration root) | Single-Project (sub-project) |
|---|---|---|
| Cross-repo artifact traceability | Yes — via workspace federation | No (unless sub-project has own workspace) |
| Inherited org-wide agents/rules | Only from orchestration repo's own layers | Yes — via master layer walk-up |
| Agent generation scope | Orchestration repo only | Submodule + orchestration master layer |
| Typical use case | System-wide reviews, cross-cutting changes, workspace-info | Feature development within one service |

### Current Limitations

Layer discovery and workspace federation operate independently. This means:

- `cpt generate-agents` does not discover or merge manifests from workspace sources — it runs within the primary repo's layer hierarchy only
- Workspace sources with their own `manifest.toml` files must run `cpt generate-agents` independently within each source
- There is no cross-source component merging — each source's manifest hierarchy is self-contained

These boundaries are intentional for the MVP. Cross-source manifest merging would require precedence rules for component conflicts across sources and is tracked as future work.

### Potential Improvements

1. **Workspace-aware agent generation** — extend `cpt generate-agents` to optionally iterate workspace sources and run layer discovery within each, generating agents for all sources in a single invocation
2. **Cross-source component visibility** — allow a workspace source's manifest to reference components defined in another source (e.g., a shared skill defined in an infra repo, consumed by a service repo)
3. **Unified provenance** — extend `--show-layers` to include workspace source attribution alongside layer provenance, so the developer can see both *which layer* and *which source* contributed each component

---

## Future Work

These items are deferred from the MVP but planned for follow-up features:

1. **Organization and Project layers** — expand from 4 to 6 layers with git host and project group detection
2. **Full template composition** — block-based `<!-- @block:NAME -->` markers with replace/prepend/delete/insert operations
3. **`[[permissions]]` generation** — merge MCP tool permissions into `.claude/settings.local.json` (additive, idempotent); this is an important follow-up as manual permission setup is a significant time sink
4. **`[[hooks]]` generation** — session hooks into agent-native config (e.g., `.claude/settings.json`)
5. **Custom section preservation** — detect and preserve `<!-- *:custom -->` markers during regeneration
6. **Workspace-aware layer discovery** — extend `discover_layers()` to optionally run within each workspace source, enabling cross-source component awareness in `cpt generate-agents`
