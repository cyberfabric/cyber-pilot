# <p align="center"><img src="images/cypilot-kit.png" alt="Cypilot Banner" width="100%" /></p>
 
 [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
  ![Version](https://img.shields.io/badge/version-3.6.0--beta-green.svg)
  ![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
  [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=cyberfabric_cyber-pilot&metric=coverage)](https://sonarcloud.io/summary/new_code?id=cyberfabric_cyber-pilot)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cyberfabric_cyber-pilot&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=cyberfabric_cyber-pilot)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=cyberfabric_cyber-pilot&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=cyberfabric_cyber-pilot)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=cyberfabric_cyber-pilot&metric=bugs)](https://sonarcloud.io/summary/new_code?id=cyberfabric_cyber-pilot)
 
**Version**: 3.6.0-beta

**Status**: Active

**Audience**: Developers using AI coding tools, technical leads, engineering teams

## Cyber Pilot — tooling for traceable, reviewable AI-assisted software changes

It adds bounded phases, stable identifiers, and verifiable checks to AI-assisted work that has outgrown a single chat. It is **not** another coding model, IDE, or AI coding tool.

It works alongside tools such as Claude Code, Cursor, GitHub Copilot, OpenAI Codex, and Windsurf to keep larger changes reviewable and traceable to approved requirements and design.

Use it when a change spans multiple AI-assisted steps and you need evidence that the final code still lines up with approved requirements, design, tasks, and constraints.

It adds three controls that plain prompting does not preserve well at larger scope:

- **reuse the same stable identifiers from requirements and design through tasks, code, and checks so drift and missing links become visible**
- **break large or risky work into bounded, reviewable phases**
- **run deterministic checks on structure, references, consistency, and traceability**

The model itself is still **non-deterministic**. Cyber Pilot does not try to change that. Instead, it adds structure and checks around the parts of the workflow that *can* be made explicit and verifiable.

### Who this is for

Use Cyber Pilot if you already work with an AI coding tool and need more control over larger or riskier work.

- **Engineers** — to keep larger changes bounded, reviewable, and easier to continue safely
- **Tech leads and architects** — to reduce drift between approved requirements, design, and implementation
- **Product and delivery leads** — to see how approved scope maps to implementation and what review evidence supports it

Cyber Pilot is usually **not** the right starting point for tiny edits, throwaway spikes, or open-ended exploration where speed matters more than structure.

### What changes in practice

Without Cyber Pilot, larger AI-assisted tasks often collapse into one long mixed-purpose thread, making scope drift easier to miss and review harder to trust.

With Cyber Pilot, you split the work into explicit planning, generation, review, and traceability checks instead of one long mixed-purpose thread:

- **`plan`** — break large or risky work into bounded phases
- **`generate`** — implement or produce something within approved scope
- **`analyze`** — review, validate, compare, or look for gaps
- **traceability checks** — verify that requirements, design decisions, tasks, and code changes still line up through the same stable identifiers

In practice, this usually means:

- **fewer long mixed-purpose chats**
- **clearer implementation boundaries**
- **better alignment between approved docs and code**
- **earlier detection of drift and missing links**
- **more reliable review before merge**

### One practical path from idea or PoC to production

Cyber Pilot is strongest when an early idea or PoC needs to become a production-ready change without losing scope or design intent.

A typical path is: approve the requirement and design, split the change into bounded phases, implement one phase at a time, review each phase against the same identifiers, then verify before merge that the shipped code still traces back to the approved requirement, design, and tasks.

> **Convention**: 💬 = paste into AI coding tool chat. 🖥️ = run in terminal.

---

### Start here if you're evaluating Cyber Pilot

- **Use it when**
  - you have a larger change that needs planning, implementation, validation, or review across more than one step
  - you want the work to stay aligned from requirement or design through implementation and review

- **Do not start with it when**
  - the task is a tiny edit, throwaway spike, or open-ended exploration
  - speed matters more than structure and the shape of the work is still unclear

- **Who usually benefits most early**
  - engineers: safer larger changes, clearer review checkpoints, and better confidence before merging
  - tech leads and architects: clearer design-to-implementation flow, better review discipline, and visible traceability across stages
  - PMs and delivery readers: clearer visibility into whether the implemented work still matches the approved requirement and design

### What to expect after setup

After setup, you can start with one practical Cyber Pilot workflow from your AI coding tool, with the CLI supporting setup, validation, and repeatable workflows.

- **A structured analysis of an existing requirement or design doc** with 💬 `cypilot analyze: ...`
- **A bounded phase plan for a larger change** with 💬 `cypilot plan: ...`
- **A repeatable CLI path for setup and validation** through 🖥️ `cpt`

You do **not** need advanced features on day one; most first trials start with `analyze`, `plan`, and validation only.

### Where Cyber Pilot helps first

First value usually shows up in a few repeatable situations:

- **Turning an approved requirement or design into implementation** — while keeping implementation and review aligned with it
- **A bounded plan for a larger or riskier change** before coding starts
- **A validation pass before review or merge** instead of trusting one generation pass
- **A clearer picture of an unfamiliar area** before changing code in a brownfield system

### Prerequisites

For a first trial, you need Python 3.11+, Git, and one supported AI coding tool such as Claude Code, Cursor, Windsurf, GitHub Copilot, or OpenAI Codex.

`pipx` is recommended for installing the CLI globally. `gh` is optional for PR review and PR status workflows.

**Prefer to skim?** Jump to [Quick start](#quick-start), [What success looks like after 5 minutes](#5-what-success-looks-like-after-5-minutes), or [AI coding tool support at a glance](#ai-coding-tool-support-at-a-glance).

---

### Quick start

Goal: get Cyber Pilot working in your repository and produce one concrete result within a few minutes.

Cyber Pilot is the product.
Use 🖥️ `cpt` in your terminal for repo setup.
Use 💬 `cypilot ...` in your AI coding tool chat for workflows in that same repository.
Do **not** run 💬 `cypilot ...` in the terminal.
The generated setup folder is `cypilot/` by default, but you can choose a different name such as `.cpt/` during init.

#### 1. Install the CLI

🖥️ **Terminal**:
```bash
pipx install git+https://github.com/cyberfabric/cyber-pilot.git
```

Verify the CLI install with:

🖥️ **Terminal**:
```bash
cpt --version
```

If it prints a version, the CLI install worked.
If this works, skip the macOS and Windows notes below.
If `cpt` is not found, open a new terminal and try again.

**Only if needed on macOS**

Install `pipx` with **Homebrew**:

🖥️ **Terminal**:
```bash
brew install pipx
pipx ensurepath
```

Then open a new terminal, or reload the shell config that `pipx ensurepath` updated.
For example, with the default macOS `zsh` setup:

🖥️ **Terminal**:
```bash
source ~/.zshrc
```

**Only if needed on Windows**

Install `pipx` with **Scoop**:

🖥️ **Terminal**:
```bash
scoop install pipx
pipx ensurepath
```

Then open a new terminal so the updated `PATH` is picked up.

#### 2. Initialize a project

From your repository root, run:

🖥️ **Terminal**:

```bash
cpt init
cpt generate-agents
```

🖥️ `cpt init` is interactive. For a first trial, you can usually accept the default project root, keep the default setup directory unless you want a custom one, and accept the default SDLC kit if prompted.

🖥️ `cpt init` sets up Cyber Pilot in your repository.
🖥️ `cpt generate-agents` adds the AI coding tool integration files for this repository.

🖥️ `cpt generate-agents` may preview the files it will create and ask you to confirm before writing them.

After this step, your repository should contain a new Cyber Pilot setup folder such as `cypilot/` or `.cpt/`, plus generated AI coding tool integration files. You may also see host-specific folders such as `.windsurf/`, `.cursor/`, `.claude/`, `.github/`, `.codex/`, or `.agents/`, but you do not need to open or edit them for this trial.

If your AI coding tool is already open, reload the repository before continuing to step 3.

#### 3. Turn on Cyber Pilot in your AI coding tool

In the AI coding tool chat attached to the same repository or workspace you just initialized, run:

In some hosts, you may also see a generated `cypilot` command or `/cypilot-...` entrypoint in the chat UI. The portable default in this README remains 💬 `cypilot ...`.

💬 **AI coding tool chat**:

```text
cypilot on
```

If setup worked, the chat should end with a clear activation confirmation such as `Cypilot Mode Enabled`. If the chat replies like a normal assistant and does not confirm Cyber Pilot mode, activation did not happen; reopen the repository in the AI coding tool and try again. Some hosts may also show the resolved Cypilot path or loaded context.

#### 4. For your first 5-minute trial, start with `analyze` or `plan`

- start with `analyze` if you already have a requirement, design doc, or implementation plan
- start with `plan` if you have a larger change request but no plan yet
- leave `generate` for later, once the change is approved and tightly scoped

For this trial, use one small real input only: paste 5-15 lines of a requirement or change request, attach one short note or spec section, or point to one specific requirement, design, or change-request file in the same chat message. Do **not** ask for a repo-wide review or a broad plan with no concrete input attached.

**Analyze**

💬 **AI coding tool chat**:

```text
cypilot analyze: review the pasted requirement, the attached note, or docs/requirements.md. List the top 5 unclear, missing, or conflicting points, then end with the 3 questions that must be answered before implementation
```

**Plan**

💬 **AI coding tool chat**:

```text
cypilot plan: using the pasted change request, the attached note, or docs/change-request.md, break this work into 3-7 small reviewable phases. For each phase, give the goal, likely files affected, and the main risk
```

Skip 💬 `cypilot generate: ...` for your first 5-minute trial. Use it later, after the change is approved and tightly scoped.

#### 5. What success looks like after 5 minutes

After 5 minutes, success means you have both:

- a clear activation confirmation from `cypilot on`, such as `Cypilot Mode Enabled`
- one useful result you could act on immediately: either a numbered list of real gaps or blocking questions, or a phased implementation plan

The new setup folder and generated integration files are only a secondary sanity check. The goal is a useful result, not setup artifacts.

You can defer generated files, host-specific integration details, and advanced setup until later.

### AI coding tool support at a glance

Cypilot works across multiple AI coding tools, but some hosts support its structured workflows more fully than others.

| Host | Best first use | Notes |
|---|---|---|
| Claude Code | Best starting point for full workflow support | Strongest support for isolated task flow, subagents, and separate generation/review passes |
| Cursor | Good editor-first starting point | Strong everyday IDE choice, with a smoother general workflow than the more orchestration-heavy hosts |
| GitHub Copilot | Good for familiar editor and GitHub-centered workflows | Supports structured Cypilot use, but with less control over task orchestration than Claude Code |
| OpenAI Codex | Best for narrow, well-scoped tasks | Works best when task boundaries are tight and validation steps are clearly specified |
| Windsurf | Usable with manual workflow discipline | Works without subagents, but you should separate generation and review into different chats |

If you are unsure where to start, **Claude Code** currently gives the clearest first experience for the full Cypilot workflow.

For host-specific setup guidance, deeper tradeoffs, and the full support matrix, use **[guides/AGENT-TOOLS.md](guides/AGENT-TOOLS.md)**.

---

## Operating model

### Command surfaces at a glance

For most users, the main thing to remember is simple: in chat, Cyber Pilot is primarily used through the **`cypilot` skill** inside your AI coding tool.

| Surface | Form | Role |
|---|---|---|
| Primary AI surface | 💬 `cypilot <workflow>: <request>` | Main chat entry point for `plan`, `generate`, and `analyze` requests |
| Terminal surface | 🖥️ `cpt <command>` | Normal CLI surface for deterministic commands such as `init`, `validate`, `update`, and `toc` |
| Legacy chat aliases | 💬 `/cypilot-plan`, 💬 `/cypilot-generate`, 💬 `/cypilot-analyze` | Older host-specific slash aliases for the same workflows |

If you are unsure what to use in chat, start with the `cypilot` skill and write 💬 `cypilot <workflow>: ...`. Treat slash commands as legacy aliases for the same workflows.

### How to think about Cypilot

Cypilot is best understood as the **workflow, context, and validation layer around your AI coding tool**.

Your AI coding tool gives you the chat interface and model access. The agent does the reasoning and writing. Cypilot adds structured workflows, task-matched context, and deterministic checks around that work.

- **Use the agent for**
  - reasoning
  - writing
  - transformation
  - implementation judgment

- **Use Cypilot for**
  - workflow selection
  - task-matched context loading
  - templates, rules, and checklists
  - deterministic validation
  - keeping requirements, design, and code linked through the same identifiers
  - planning large tasks into bounded steps

- **What is deterministic?**
  - config and resource resolution
  - routing into workflows and specialized commands
  - validation of structure, IDs, cross-references, TOC, and traceability rules
  - file-backed plans and repeatable CLI checks

- **What is not deterministic?**
  - the agent's reasoning, writing quality, and implementation judgment
  - human review decisions

- **What tradeoff does Cypilot make?**
  - more process and context in exchange for more control, auditability, and repeatability

For the full fit / non-fit guidance, practical anti-patterns, planning heuristics, and workflow-choice rules, use **[guides/USAGE-GUIDE.md](guides/USAGE-GUIDE.md)**.

### What Cypilot provides

Cypilot has two main parts:

- **Core platform** - the chat-facing skill, deterministic CLI, and reusable guidance that make work more structured and repeatable
- **Kits** - optional add-ons that bring domain-specific templates, rules, workflows, and validation material

Most new users should start with the core platform and add a kit later only if they want a ready-made delivery model for a specific domain or way of working.

#### 1. Core platform

At a high level, the core platform gives you one main chat interface, one deterministic CLI, and reusable guidance that makes work more repeatable.

- **The `cypilot` skill** - the main chat entry point for using the right workflow and loading the right guidance for the task
- **The `cpt` CLI tool** - the terminal surface for deterministic commands such as `init`, `validate`, `update`, and `toc`
- **Workflows and supporting guidance** - reusable procedures, rules, templates, and validation checks that make work more repeatable

Use the core platform when you want Cypilot's control layer without committing to any one domain methodology.

#### 2. Kits

Kits are optional. Core Cypilot works without them.

Use a kit when you want a ready-made structured delivery model for a specific domain or workflow.

Kits sit on top of the core platform and add domain-specific templates, rules, examples, workflows, scripts, and validation constraints.

The official SDLC kit is one example. It adds a structured delivery model for requirements, design, decomposition, implementation, and review, along with reusable templates and validation guidance.

Repository: **[cyberfabric/cyber-pilot-kit-sdlc](https://github.com/cyberfabric/cyber-pilot-kit-sdlc)**

---

### Configuration at a glance

All user-editable configuration lives under `config/` inside your Cypilot directory.

You do not need to understand all of this on day one. Most new users can start with 🖥️ `cpt init`, use the three Cypilot workflows, and come back here later.

| File | What it controls |
|---|---|
| `core.toml` | Project settings, installed kits, and workspace-level configuration |
| `artifacts.toml` | How artifacts, systems, codebases, and traceability are mapped in the project |
| `AGENTS.md` | Task navigation rules that tell the agent which files to load for each job |
| `SKILL.md` | Always-on project instructions that apply across requests |
| `rules/*.md` | Optional topic-specific rules the agent loads for relevant tasks |

For full configuration details, see **[Configuration guide](guides/CONFIGURATION.md)**.

---

### Workflow model

Cypilot has three core workflows. Each has a portable chat form and, in some hosts, a matching slash-command alias.

| Workflow | Portable chat form | Matching alias in some hosts | Use it when |
|---|---|---|---|
| Plan | 💬 `cypilot plan: ...` | 💬 `/cypilot-plan` | the task is too large, risky, or context-heavy for one conversation |
| Generate | 💬 `cypilot generate: ...` | 💬 `/cypilot-generate` | you want to create, update, implement, or configure something |
| Analyze | 💬 `cypilot analyze: ...` | 💬 `/cypilot-analyze` | you want to validate, review, inspect, compare, or audit |

The portable 💬 `cypilot <workflow>: ...` form is the best default. Slash commands are host-specific aliases, not separate capabilities.

For default routing priorities and detailed workflow-choice advice, use **[guides/USAGE-GUIDE.md](guides/USAGE-GUIDE.md)**.

---

### Optional capabilities

You do not need these on day one. Add them when your use case justifies the extra surface area.

#### Multi-repo workspaces

Cypilot supports **multi-repo workspaces** so related docs, code, and shared kit assets can live in separate repositories and still stay aligned.

Use this when docs, code, or shared kit assets live in separate repos and still need to stay aligned.

For practical guidance, see **[guides/USAGE-GUIDE.md](guides/USAGE-GUIDE.md)**. For the full model and configuration rules, see **[requirements/workspace.md](requirements/workspace.md)**.

#### RalphEx delegation

RalphEx support is optional.

When available, Cyber Pilot can hand off selected execution work to RalphEx under human supervision.

Use this when you want supervised execution handoff for bounded tasks instead of keeping all work interactive inside the current AI coding tool.

For when to delegate and how human review fits, see **[guides/USAGE-GUIDE.md](guides/USAGE-GUIDE.md)**.

#### Project extensibility

Cypilot supports **project-level extensibility**, not just installable kits.

Cyber Pilot can also load project-defined skills, subagents, workflows, and rules, so teams can extend behavior without packaging everything as a kit.

For the full model and examples, see **[guides/PROJECT-EXTENSIBILITY.md](guides/PROJECT-EXTENSIBILITY.md)**.

---

### FAQ

- **Is Cypilot a replacement for Claude Code, Cursor, Copilot, or another AI coding tool?**

  No. Cypilot sits on top of those AI coding tools and adds workflow routing, context loading, validation, and traceability.

- **When is Cypilot a good fit, and when is it overkill?**

  It is a good fit for large, risky, multi-step work, structured transformations, repeatable review, brownfield understanding, and multi-repo coordination. It is overkill for tiny edits, loose ideation, throwaway spikes, or any task where speed matters more than control.

- **Do I need a kit to use Cypilot?**

  No. Core Cypilot works without kits. Start with core. Add a kit only when you want domain templates, rules, and review material.

- **What part is deterministic?**

  Config resolution, workflow routing, validation, TOC checks, ID and traceability checks, and file-backed plans are deterministic. The agent's reasoning and generation quality are not.

- **Which host is the best first experience?**

  Claude Code currently provides the highest-fidelity Cypilot experience, especially for subagents and isolation. Other supported hosts still work and may fit different team preferences.

- **What is the safest way to start if I am unsure?**

  Run 🖥️ `cpt init`, run 🖥️ `cpt generate-agents`, then try one focused 💬 `cypilot analyze: ...` request. Start with one workflow and one use case, not the whole system at once.

- **Can I use Cypilot on a brownfield project?**

  Yes. Start with 💬 `cypilot analyze: ...` to understand the area, use 💬 `cypilot plan: ...` for risky changes, and use 💬 `cypilot auto-config` when you need project-specific rules.

- **Do I need to use `plan`, `generate`, and `analyze` every time?**

  No. Use only the workflow that matches the job. Start with `plan` when the task spans multiple files, steps, constraints, or review cycles.

- **Can this replace testing, code review, or security tooling?**

  No. It strengthens the workflow around those activities; it does not replace specialized tools or human judgment.

---

## Further reading

- **Start here next**
  - **[Usage guide](guides/USAGE-GUIDE.md)**
  - **[Agent tools guide](guides/AGENT-TOOLS.md)**
  - **[Configuration guide](guides/CONFIGURATION.md)**
  - **[Story-driven walkthrough](guides/STORY.md)**

- **Deeper reference**
  - **[Workspace specification](requirements/workspace.md)**
  - **[Requirements and checklists](requirements/)**
  - **[Architecture and ADRs](architecture/)**

---

## Feedback and issues

If you think a workflow is unclear, instructions behave incorrectly, a script behaves incorrectly, or important corner cases are missing, please open a GitHub issue.

- **Issues list:** [github.com/cyberfabric/cyber-pilot/issues](https://github.com/cyberfabric/cyber-pilot/issues)
- **Create a new issue:** [github.com/cyberfabric/cyber-pilot/issues/new/choose](https://github.com/cyberfabric/cyber-pilot/issues/new/choose)

The most useful issue reports usually include:

- **A short summary**
- **Affected file, workflow, script, or exact command**
- **Minimal reproduction steps**
- **Expected vs actual behavior**
- **Evidence** such as exact command output, logs, validator output, screenshots, or a minimal prompt or plan slice
- **Environment details** such as OS, AI coding tool, model, and Cypilot version if known

---

## Bottom line

Cyber Pilot is best understood as a **deterministic structure, transformation, and validation layer for work done through AI coding tools**.

It is strongest when you need:

- **document-to-document and document-to-code transformation**
- **deterministic validation**
- **structured review**
- **keeping requirements, design, and code aligned**
- **planning for large tasks**

It is a poor fit when you want the lightest possible chat-to-edit loop, or when the underlying documents, review habits, and engineering judgment are not there yet.

Used correctly, it does not replace your stack.

It makes your stack work together more reliably.

---

## Contributing

If you want to contribute, start with **[CONTRIBUTING.md](CONTRIBUTING.md)**.

---

## License

Cyber Pilot is licensed under the **Apache License 2.0**. See **[LICENSE](LICENSE)** for details.
