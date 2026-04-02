# <p align="center"><img src="images/cypilot-kit.png" alt="Cypilot Banner" width="100%" /></p>

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.6-green.svg)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)]()
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=cyberfabric_cyber-pilot&metric=coverage)](https://sonarcloud.io/summary/new_code?id=cyberfabric_cyber-pilot)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cyberfabric_cyber-pilot&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=cyberfabric_cyber-pilot)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=cyberfabric_cyber-pilot&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=cyberfabric_cyber-pilot)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=cyberfabric_cyber-pilot&metric=bugs)](https://sonarcloud.io/summary/new_code?id=cyberfabric_cyber-pilot)

**Version**: 3.6

**Status**: Active

**Audience**: Developers using AI coding assistants, technical leads, engineering teams

## Cyber Pilot — Deterministic orchestration for AI agents

Cyber Pilot (*Cypilot*) is **not another coding model or AI agent**.

Cyber Pilot is a **deterministic orchestration and validation layer** that sits on top of AI agents and helps them transform one kind of document into another, or into code, while preserving strict format, structural consistency, and cross-artifact alignment through identifiers.

A delivery chain such as **requirements -> design -> decomposition -> implementation -> validation** is one important example of that broader idea.

In practice, this means Cyber Pilot helps you:

- **Transform artifacts** from one stage into the next, such as `PRD -> DESIGN -> DECOMPOSITION -> FEATURE -> CODE`.
- **Enforce structure** with templates, constraints, workflows, and deterministic checks.
- **Keep traceability** between documents, decisions, tasks, and code.
- **Work across repositories and extensible project boundaries** through workspace and multi-repo support.
- **Reduce context drift** on large tasks by turning them into executable plans.
- **Use existing AI tools better** instead of pretending to replace them.

> **Convention**: 💬 = paste into AI agent chat. 🖥️ = run in terminal.

---

## Table of Contents

<!-- toc -->

- [Cyber Pilot — Deterministic orchestration for AI agents](#cyber-pilot--deterministic-orchestration-for-ai-agents)
- [Table of Contents](#table-of-contents)
- [Why Cyber Pilot exists](#why-cyber-pilot-exists)
- [What Cypilot is and is not](#what-cypilot-is-and-is-not)
  - [What it is](#what-it-is)
  - [What it is not](#what-it-is-not)
  - [Where it is strongest / weakest](#where-it-is-strongest--weakest)
- [Expectation setting](#expectation-setting)
  - [What Cypilot is excellent at](#what-cypilot-is-excellent-at)
  - [What Cypilot helps with, but does not solve alone](#what-cypilot-helps-with-but-does-not-solve-alone)
  - [What Cypilot is not the best entry point for today](#what-cypilot-is-not-the-best-entry-point-for-today)
- [A critical clarification about IDs and code generation](#a-critical-clarification-about-ids-and-code-generation)
- [The core mental model](#the-core-mental-model)
  - [The LLM is used for](#the-llm-is-used-for)
  - [Cypilot is used for](#cypilot-is-used-for)
- [Why plans matter so much](#why-plans-matter-so-much)
- [How to think about Cypilot with other tools](#how-to-think-about-cypilot-with-other-tools)
- [What Cypilot does not replace](#what-cypilot-does-not-replace)
- [What Cypilot provides](#what-cypilot-provides)
  - [1. Core platform](#1-core-platform)
  - [2. SDLC kit](#2-sdlc-kit)
- [How to use Cypilot correctly](#how-to-use-cypilot-correctly)
  - [Start with the right request shape](#start-with-the-right-request-shape)
  - [Give Cypilot structured inputs](#give-cypilot-structured-inputs)
  - [Use deterministic validation early](#use-deterministic-validation-early)
  - [Treat Cypilot as a system, not just a prompt prefix](#treat-cypilot-as-a-system-not-just-a-prompt-prefix)
- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
  - [1. Install the CLI](#1-install-the-cli)
  - [2. Initialize a project](#2-initialize-a-project)
  - [2.5 Update an existing installation](#25-update-an-existing-installation)
  - [3. Enable Cypilot mode in your AI tool](#3-enable-cypilot-mode-in-your-ai-tool)
  - [4. Start with one of the three main workflows](#4-start-with-one-of-the-three-main-workflows)
- [Configuration at a glance](#configuration-at-a-glance)
- [Workflow model](#workflow-model)
- [Example prompts](#example-prompts)
  - [Setup and project understanding](#setup-and-project-understanding)
  - [Artifact generation and transformation](#artifact-generation-and-transformation)
  - [Planning and phased execution](#planning-and-phased-execution)
  - [Validation and review](#validation-and-review)
- [Agent integrations and subagents](#agent-integrations-and-subagents)
- [Multi-repo workspaces](#multi-repo-workspaces)
- [RalphEx delegation](#ralphex-delegation)
- [Extensibility](#extensibility)
- [When to reach for Cypilot](#when-to-reach-for-cypilot)
- [When not to reach for Cypilot first](#when-not-to-reach-for-cypilot-first)
- [Further reading](#further-reading)
- [Bottom line](#bottom-line)

<!-- /toc -->


## Why Cyber Pilot exists

The main problem Cyber Pilot solves is **not** “how to get more raw code out of an LLM.”

The main problem it solves is this:

When work becomes larger than a single prompt, teams need a reliable way to transform one artifact into another, or into code, without losing structure, meaning, and consistency.

That usually breaks down in four places:

- **Cross-stage transformation breaks**
  
  One document does not cleanly become the next, or code diverges from the documents that should guide it.

- **LLMs lose structural discipline**
  
  A model may write plausible content, but it does not reliably preserve required sections, traceability, checklist coverage, or consistent conventions across a long chain of artifacts.

- **Large tasks overflow context**
  
  As soon as a task becomes multi-step, the working context gets noisy and brittle. Important details are dropped, repeated, or contradicted.

- **Tooling is fragmented**
  
  Teams use Claude Code, Cursor, Windsurf, Copilot, terminal commands, CI, templates, reviews, and custom conventions. Without a common layer, every workflow becomes ad hoc.

Cyber Pilot exists to add a missing layer between the human intent and the agent output:

- **Structured workflows with deterministic routing and gates**
  
  The task is routed through a defined workflow, with fixed checkpoints and explicit rules for when the next step is allowed.
- **Deterministic validation**
  
  Anything that can be checked by scripts instead of model judgment is validated the same way every time.
- **Deterministic structure**
  
  Templates, constraints, and required sections keep documents and outputs in a predictable shape.
- **Deterministic traceability**
  
  Identifiers and references make it possible to reliably connect requirements, design, tasks, and code.

The LLM still does the reasoning and writing.

Cyber Pilot makes the surrounding process far more controlled.

This is also what makes Cyber Pilot different from most AI coding tools, which are strongest at **local generation**:

- **Controlled artifact transformation**
  
  Cyber Pilot is built around moving from one artifact to another, or from artifacts into code, in a controlled way, not just answering one prompt well.

- **Deterministic enforcement where possible**
  
  If something can be validated without an LLM, Cyber Pilot pushes it into scripts and rules instead of leaving it to model judgment.

- **Templates, checklists, constraints, and IDs as first-class tools**
  
  The structure layer is not a side feature. It is the product.

- **Multi-repo support and project extensibility**
  
  Cyber Pilot can work across repository boundaries through workspaces and extensible project configuration instead of assuming everything lives in one local repo.

- **Plans for context preservation**
  
  For large tasks, Cyber Pilot can split work into smaller executable phases so the agent does not have to carry everything in one overflowing conversation.

- **Complementary architecture**
  
  Cyber Pilot is meant to work with Claude Code, Cursor, Copilot, Windsurf, OpenAI tools, CI, and optional delegation systems like RalphEx.

---

## What Cypilot is and is not

### What it is

| Statement | Explanation |
|---|---|
| Cypilot is a structured transformation, validation, and coordination layer for AI agents | It adds workflows, validation, traceability, workspaces, and execution planning around existing agents. |
| Cypilot is primarily a system for transforming structured artifacts into other artifacts or into code | Its core value is controlled document-to-document and document-to-code transformation. |
| Cypilot is a way to make AI-assisted work more controlled where deterministic rules are possible | It pushes validation, structure, and routing into scripts, constraints, and workflow logic wherever possible. |
| Cypilot is a coordination layer, not just a prompt prefix | Its value comes from workflows, kits, validation, traceability, context loading, planning, and workspace support working together. |

### What it is not

| Statement | Explanation |
|---|---|
| Cypilot is not a replacement for Claude Code, Cursor, Copilot, Windsurf, or other coding agents | It is designed to work through those tools, not replace them. |
| Cypilot is not a magic code generator | It can improve artifact-to-code flows, but it does not turn vague intent into perfect code by itself. |
| Cypilot does not replace good source documents | Weak requirements, weak design, or weak decomposition still produce weak downstream results. |
| Cypilot does not make code good just because identifiers exist | IDs improve traceability and consistency control, not architecture quality or implementation judgment. |
| Cypilot does not replace human architecture judgment | It helps structure and validate decisions; it does not eliminate the need for good thinking. |
| Cypilot does not replace human review | It improves consistency and catches many classes of issues, but review responsibility still remains with people. |
| Cypilot does not replace specialized tools in your stack | It complements your IDE, coding agent, CI, review tools, design workflows, and other supporting systems. |

### Where it is strongest / weakest

| Statement | Explanation |
|---|---|
| Cypilot is strongest where the workflow can be made structured and partially deterministic | This is where templates, constraints, checklists, IDs, validators, and routing rules provide the most leverage. |
| Cypilot is especially useful for large tasks because plans preserve context | Planning reduces context overflow, keeps tasks bounded, and makes progress easier to inspect. |
| Cypilot is more about process reliability than raw generation speed | Its main advantage is controlled transformation and validation, not maximal speed of first-draft output. |
| Cypilot is not the best first tool for highly ambiguous visual or frontend exploration | If the task is still open-ended and the structure is not yet clear, freer exploration is often a better first step. |

---

## Expectation setting

This section is the most important one for new users.

### What Cypilot is excellent at

| Use case | Fit | Why |
|---|---|---|
| Transforming one structured artifact into another, such as `PRD -> DESIGN -> DECOMPOSITION -> FEATURE` | Excellent | This is one of the central strengths of the product. |
| Enforcing document structure and required sections | Excellent | Deterministic constraints are a core capability. |
| Running checklist-based reviews | Excellent | Cypilot provides structured analysis and validation flows. |
| Maintaining traceability across artifacts and code | Excellent | IDs and validators make this a first-class workflow. |
| Splitting large work into phases | Excellent | Planning preserves context and reduces drift. |
| Standardizing AI workflows across tools | Strong | One methodology can be projected into multiple agent environments. |
| PR review and PR status workflows | Strong | Structured, repeatable review flows are a natural fit. |

### What Cypilot helps with, but does not solve alone

| Use case | Fit | Reality |
|---|---|---|
| Code generation from already-good specs | Strong | Cypilot helps a lot when the inputs are already structured and reviewable. |
| Brownfield project work | Strong | Auto-config and rules help, but project complexity still matters. |
| Multi-repo development | Strong | Workspace support helps, but repo boundaries and ownership still matter. |
| Team-level process standardization | Strong | Cypilot can encode conventions, but adoption discipline is still needed. |

### What Cypilot is not the best entry point for today

This is the section many users should read first.

Cyber Pilot is intentionally optimized for **control, structure, traceability, and repeatability**.

That also means it often has **more overhead** than lighter approaches. In many situations, lightweight methods such as OpenSpec, BMAD, spec-kit, Super Power Skill, or even direct agent prompting can be a better starting point.

| Use case | Fit | Why |
|---|---|---|
| Tiny tasks, one-file edits, and low-risk fixes | Poor | The workflow, structure, and validation overhead can cost more than the task itself. |
| Fast PoCs, spikes, and throwaway prototypes | Poor | When speed of exploration matters more than structure and traceability, Cyber Pilot is often too heavy. |
| Token-constrained work | Poor | Cyber Pilot tends to consume more tokens because it loads workflow context, rules, structure, and validation logic. |
| Raw first-draft speed | Limited | Cyber Pilot is optimized more for controlled transformation than for the fastest possible first output. |
| Vague free-form “just build something amazing” prompts | Limited | Cyber Pilot is built for structure, not for purely open-ended ideation. |
| Early product discovery, brainstorming, or market exploration | Limited | Lighter discovery-oriented approaches often work better before the artifact structure is clear. |
| Quick spec drafting with minimal ceremony | Limited | Lightweight spec-first approaches such as OpenSpec, BMAD, spec-kit, or Super Power Skill can often produce an initial draft faster with less process overhead. |
| Pure visual frontend exploration | Limited today | If you are still discovering UI direction, a design-first or UI-first workflow is usually the better starting point. |
| Small single-repo projects with little need for traceability | Limited | If you do not need IDs, structure, workspaces, validation, or planning, Cyber Pilot can be unnecessarily heavy. |
| Highly iterative exploration with many disposable alternatives | Limited | Cyber Pilot is not optimized for endlessly branching trial-and-error loops with very low commitment to structure. |
| Replacing architecture thinking with IDs or templates | Poor | IDs improve traceability, not product judgment. |
| Replacing code review with automation alone | Poor | Deterministic checks help, but they are not the full review process. |

This is intentional.

Cyber Pilot is designed to trade some speed, token efficiency, and spontaneity for more control, stronger structure, better traceability, and more repeatable multi-step execution.

Part of that tradeoff is visible in the implementation shape itself: Cyber Pilot has a lot of orchestration logic in scripts and a lot of behavioral instructions in Markdown. That is a known cost of making workflows, validation, routing, and traceability more explicit and reproducible.

For smaller projects, that can look like real overhead. The point is not that the overhead is imaginary; the point is that it is the price paid for the benefits above.

---

## A critical clarification about IDs and code generation

One common misunderstanding is:

“If the system has identifiers and traceability, then the generated code should automatically be good.”

That is **not** what identifiers do.

Identifiers help with:

- **Linking artifacts together**
- **Tracking what was specified**
- **Tracking what was implemented**
- **Running deterministic consistency checks**
- **Finding gaps and drift**

Identifiers do **not** automatically guarantee:

- **good requirements**
- **good design**
- **good code architecture**
- **good frontend design**
- **good implementation decisions**

Traceability improves control.

It does not replace quality thinking.

---

## The core mental model

The easiest way to understand Cypilot is this split:

### The LLM is used for

- **Reasoning**
- **Writing**
- **Transformation**
- **Interpretation**
- **Review with judgment**

### Cypilot is used for

- **Routing** the request to the right workflow
- **Loading** the right context
- **Applying** project rules and kit resources
- **Validating** structure and traceability deterministically
- **Planning** large tasks into smaller phases
- **Keeping** the workflow consistent across tools and sessions

That separation is the whole idea.

---

## Why plans matter so much

For large tasks, the plan system is one of Cypilot’s highest-leverage features.

Instead of forcing one giant conversation to hold everything, Cypilot can break the work into phases.

This matters because:

- **Context stays smaller**
  
  Each phase works on a bounded subset of the task.

- **Instructions become more stable**
  
  The agent has less room to drift or forget hidden assumptions.

- **Progress becomes inspectable**
  
  You can review phase outputs, validate them, and continue deliberately.

- **Long tasks become operational**
  
  Instead of “do everything,” you get a controlled execution sequence.

If a task is large enough that the chat will quickly fill up with requirements, dependencies, and follow-up constraints, planning is usually the right move.

---

## How to think about Cypilot with other tools

Cypilot should usually be viewed as a **coordination layer**, not as a competitor.

| Tool / actor | What it is good at | What Cypilot adds |
|---|---|---|
| Claude Code / Cursor / Windsurf / Copilot / Codex | Local coding, editing, reasoning, interactive implementation | Structured workflow routing, context discipline, deterministic validation, traceability, plans |
| Human engineer | Judgment, tradeoffs, business understanding, architecture responsibility | A repeatable structure around those decisions |
| Human reviewer | Nuanced review, organizational context, product risk awareness | Repeatable checklists and deterministic gates before or alongside review |
| CI pipeline | Reproducible automation | Cypilot-compatible validation, status, and workflow outputs |
| RalphEx | Optional delegated execution | Structured handoff through plan-driven flows |

---

## What Cypilot does not replace

- **Good initial problem framing**
  
  If the task is underspecified, the result will still be underspecified.

- **Good source documents**
  
  Cypilot can help improve them, but it does not eliminate the need for clear requirements and design.

- **Other specialized tools**
  
  It does not replace your IDE, your coding agent, your review tool, your design tool, or your deployment stack.

- **Review discipline**
  
  You should still validate important changes with human judgment.

- **Product discovery**
  
  If you are exploring what should be built at a highly ambiguous level, Cypilot is usually not the very first tool to reach for.

---

## What Cypilot provides

Cypilot has two main layers:

### 1. Core platform

The core provides:

- **Deterministic skill engine**
- **Universal workflows** for `plan`, `generate`, and `analyze`
- **Agent integrations** for Windsurf, Cursor, Claude, Copilot, and OpenAI-compatible environments
- **CLI command** through `cpt`
- **Configuration and kit management**
- **Traceability infrastructure** for IDs and code markers
- **Execution plans** for phased work
- **Optional delegation support** through RalphEx

### 2. SDLC kit

The SDLC kit provides an artifact-first pipeline with templates, rules, checklists, examples, and validation for documents such as:

- **PRD**
- **DESIGN**
- **ADR**
- **DECOMPOSITION**
- **FEATURE**

This is one concrete kit that makes structured document-to-document and document-to-code flows practical.

Repository: **[cyberfabric/cyber-pilot-kit-sdlc](https://github.com/cyberfabric/cyber-pilot-kit-sdlc)**

---

## How to use Cypilot correctly

### Start with the right request shape

- **Use `analyze`** when you want inspection, validation, comparison, or review.
- **Use `generate`** when you want creation, modification, or implementation.
- **Use `plan`** when the task is large enough that a single conversation will likely drift or overload context.

### Give Cypilot structured inputs

The better your inputs, the more Cypilot can help.

Good inputs look like:

- **A clear target artifact or code area**
- **A clear change goal**
- **Relevant source documents**
- **Explicit constraints or acceptance criteria**

### Use deterministic validation early

Do not wait until the end to check whether the structure, IDs, or artifact rules are broken.

### Treat Cypilot as a system, not just a prompt prefix

Its value comes from workflows, config, kits, rules, validation, and planning working together.

---

## Prerequisites

- **Python 3.11+**
  
  Required for the CLI and skill engine.

- **Git**
  
  Used for project detection, workspace handling, and normal repository workflows.

- **An AI agent**
  
  Cypilot is designed to work through tools such as Windsurf, Cursor, Claude Code, Copilot, and OpenAI-compatible environments.

- **`pipx`**
  
  Recommended for installing the CLI globally.

- **`gh` CLI** *(optional)*
  
  Useful for PR review and PR status workflows.

---

## Quick start

### 1. Install the CLI

🖥️ **Terminal**:

```bash
pipx install git+https://github.com/cyberfabric/cyber-pilot.git
```

Update later with:

```bash
pipx upgrade cypilot
```

This installs `cpt` globally.

The CLI is a thin entrypoint. On use, it resolves to the cached or project-local Cypilot engine.

**macOS note**

If `pipx` installed the binary into a path that is not yet on your shell `PATH`, run:

```bash
pipx ensurepath
source ~/.zshrc
```

**Windows note**

If `pipx` installed the binary into a path that is not yet on your shell `PATH`, run:

```bash
pipx ensurepath
```

Then open a new terminal so the updated `PATH` is picked up.

### 2. Initialize a project

🖥️ **Terminal**:

```bash
cpt init
cpt generate-agents
```

This creates the Cypilot directory for your project and prepares agent-specific integrations.

`cpt init` creates three main areas:

| Directory | Purpose | Editable? |
|---|---|---|
| `.core/` | Read-only core workflows, skills, schemas, and requirements | No |
| `.gen/` | Generated aggregate files for agent consumption | No |
| `config/` | Project configuration and installed kit material | Yes |

It also creates `config/core.toml` and `config/artifacts.toml`, defines a root system, and injects the managed root `AGENTS.md` block.

`cpt generate-agents` supports: `windsurf`, `cursor`, `claude`, `copilot`, `openai`.

It generates workflow entry points, skill outputs, and subagents where the host tool supports them.

### 2.5 Update an existing installation

🖥️ **Terminal**:

```bash
cpt update
```

This refreshes `.core/`, regenerates `.gen/`, and updates kit files in `config/kits/` with file-level diffs.

### 3. Enable Cypilot mode in your AI tool

💬 **AI agent chat**:

```text
cypilot on
```

### 4. Start with one of the three main workflows

**Analyze**

💬 **AI agent chat**:

```text
cypilot analyze: validate architecture/DESIGN.md
```

**Generate**

💬 **AI agent chat**:

```text
cypilot generate: implement the approved auth feature from the current FEATURE spec
```

**Plan**

💬 **AI agent chat**:

```text
cypilot plan: break this migration into safe implementation phases
```

---

## Configuration at a glance

All user-editable configuration lives under `config/` inside your Cypilot directory.

| File | What it controls |
|---|---|
| `core.toml` | Project settings, installed kits, workspace configuration, and resource bindings |
| `artifacts.toml` | Registered systems, artifact kinds, codebase paths, and traceability modes |
| `AGENTS.md` | Navigation rules for what the agent should load for which tasks |
| `SKILL.md` | Always-on project-specific skill instructions |
| `rules/*.md` | Topic-specific project rules, conventions, architecture, testing, and patterns |

To inspect resolved kit resource paths:

🖥️ **Terminal**:

```bash
cpt resolve-vars --flat
```

For full configuration details, see **[Configuration guide](guides/CONFIGURATION.md)**.

---

## Workflow model

Cypilot has three core workflows:

💬 **AI agent chat**:

- **`/cypilot-plan`**
  
  Use it when the task is too large, too risky, or too context-heavy for one conversation.

- **`/cypilot-generate`**
  
  Use it when you want to create, update, implement, or configure something.

- **`/cypilot-analyze`**
  
  Use it when you want to validate, review, inspect, compare, or audit.

Operationally, routing priority is usually:

- **plan**
- **delegate**
- **generate**
- **analyze**

That means a large request should usually become a plan first instead of forcing everything through one overloaded generate call.

---

## Example prompts

All examples below are **💬 AI agent chat prompts**.

### Setup and project understanding

💬 **AI agent chat**:

- **Enable Cypilot mode**
  
  `cypilot on`

- **Scan and configure a project**
  
  `cypilot auto-config`

- **Regenerate agent files**
  
  `cypilot generate-agents --agent claude`

### Artifact generation and transformation

💬 **AI agent chat**:

- **Create a PRD**
  
  `cypilot make PRD for user authentication system`

- **Transform PRD into design**
  
  `cypilot make DESIGN from PRD.md`

- **Decompose work**
  
  `cypilot decompose auth feature into tasks`

- **Create an implementation-ready feature spec**
  
  `cypilot make FEATURE for login flow`

### Planning and phased execution

💬 **AI agent chat**:

- **Create a plan for a large task**
  
  `cypilot plan generate PRD for task manager`

- **Check plan progress**
  
  `cypilot plan status`

- **Execute the next phase**
  
  `cypilot execute next phase`

### Validation and review

💬 **AI agent chat**:

- **Validate one artifact**
  
  `cypilot validate PRD.md`

- **Validate everything**
  
  `cypilot validate all`

- **Review a design with a checklist**
  
  `cypilot review DESIGN.md with consistency-checklist`

- **Review a PR**
  
  `cypilot review PR #123`

---

## Agent integrations and subagents

Cypilot is projected into multiple AI tools rather than tied to one host.

`cpt generate-agents` creates workflow commands, skill outputs, and, where supported, isolated subagents.

Common subagents include:

- **`cypilot-codegen`**
  
  Implements already-specified work with minimal back-and-forth.

- **`cypilot-pr-review`**
  
  Runs structured PR review in isolated context.

- **`cypilot-ralphex`**
  
  Owns delegation handoff to RalphEx.

- **`cypilot-phase-compiler`**
  
  Compiles a single plan phase from its brief.

- **`cypilot-phase-runner`**
  
  Executes the next generated phase in a dedicated context.

Windsurf does not support subagents, but still receives the workflow and skill integrations.

---

## Multi-repo workspaces

Cypilot supports **multi-repo workspaces** so artifacts, code, and kits do not all have to live in one repository.

This is useful when:

- **docs and code live in different repos**
- **shared kits live in another repo**
- **you need cross-repo traceability and ID resolution**

Quick setup examples:

🖥️ **Terminal**:

```bash
cpt workspace-init
cpt workspace-add --name docs --path ../docs-repo --role artifacts
cpt workspace-add --name shared-kits --path ../shared-kits --role kits
```

When a workspace is active, the current repo remains primary, while other sources contribute artifacts, code, and kits for cross-reference resolution.

One practical way to reduce overhead for many smaller repos is to keep a dedicated **orchestration repository** with the full Cyber Pilot setup and a preconfigured workspace, then connect multiple smaller product or service repos into that workspace. That keeps the orchestration weight centralized instead of fully reproducing it inside every small repository.

Useful commands:

🖥️ **Terminal**:

```bash
cpt workspace-info
cpt validate --local-only
cpt where-defined --id cpt-myapp-fr-auth
```

For the full model and configuration rules, see **[requirements/workspace.md](requirements/workspace.md)**.

---

## RalphEx delegation

RalphEx support is optional.

When available, Cyber Pilot can delegate entire execution plans through the dedicated `cypilot-ralphex` path.

Operationally, RalphEx can run an autonomous execution loop such as:

- **generate**
- **validate**
- **fix**
- **validate**
- **fix**
- **validate**

This loop is typically driven through **Claude Code**, with **Codex** available as an optional additional execution path depending on the setup.

That can be powerful, but it also means you should monitor what is happening.

If validation produces a **false positive**, an autonomous fix loop can start optimizing for the wrong signal and lead to unpredictable results.

The main mitigation is that RalphEx commits changes **granularly** as it goes. If a validation step goes wrong, you can roll back to a known-good commit and continue from that point instead of losing the whole execution trail.

Typical flow:

1. Create a plan with `/cypilot-plan`
2. Ask Cypilot to delegate it to RalphEx

Examples:

💬 **AI agent chat**:

- 💬 `cypilot delegate to ralphex`
- 💬 `cypilot delegate this plan to ralphex`

Environment check:

🖥️ **Terminal**:

```bash
cpt doctor
```

`cpt delegate` exists as the underlying advanced/manual CLI path, but it is not the primary end-user entrypoint.

---

## Extensibility

Cypilot is extensible through **kits**.

A kit can define:

- **artifact kinds**
- **templates**
- **rules**
- **checklists**
- **constraints**
- **examples**
- **workflows**

The built-in SDLC kit is one important example, but the architecture is meant to support additional domains and project-specific structure layers.

---

## When to reach for Cypilot

Use Cypilot when you need one or more of these:

- **A reliable path from one structured artifact to another, or from artifacts to code**
- **A repeatable artifact workflow**
- **Checklist-based review and validation**
- **Traceability between docs and code**
- **A safer way to run large tasks without context collapse**
- **A common process across multiple AI tools**

---

## When not to reach for Cypilot first

You may want another tool or workflow first when:

- **You are still doing open-ended product discovery**
- **You need free-form UI ideation before the structure exists**
- **You only need a tiny one-file edit with no meaningful workflow overhead**
- **You do not yet have enough source information to define the task cleanly**

In those cases, Cypilot often becomes more useful one step later, once the task has enough shape to benefit from structure and validation.

---

## Further reading

- **[Configuration guide](guides/CONFIGURATION.md)**
- **[Story-driven walkthrough](guides/STORY.md)**
- **[Architecture and ADRs](architecture/)**
- **[Requirements and checklists](requirements/)**
- **[Workspace specification](requirements/workspace.md)**
- **[Contributing guide](CONTRIBUTING.md)**
- **Kit, traceability, and schema specs:** [architecture/specs/](architecture/specs/) and [schemas/](schemas/)

---

## Bottom line

Cypilot is best understood as a **deterministic transformation, structure, and validation layer for AI-assisted engineering**.

It is strongest when you need:

- **document-to-document and document-to-code transformation**
- **deterministic validation**
- **structured review**
- **traceability**
- **planning for large tasks**

It is weakest when you expect it to replace:

- **thinking**
- **discovery**
- **good documents**
- **good code review**
- **specialized tools**

Used correctly, it does not replace your stack.

It makes your stack work together more reliably.

---

## Contributing

If you want to contribute, start with **[CONTRIBUTING.md](CONTRIBUTING.md)**.

---

## License

Cyber Pilot is licensed under the **Apache License 2.0**. See **[LICENSE](LICENSE)** for details.
