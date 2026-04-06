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

## Overview

Cyber Pilot is a traceable delivery system for requirements, design, plans, and code.

Stable identifiers and references connect requirements, design, plans, and implementation so drift is surfaced early instead of being reconstructed ad hoc during review and delivery.

For teams already using an AI coding tool, Cyber Pilot provides the operating controls needed to keep requirements, design, plans, and code traceable, reviewable, and enforceable as artifacts and implementation change:

  - **stable identifiers and cross-link validation** to prove alignment across requirements, design, plans, and code
  - **deterministic `cpt` validation** to check structure, references, consistency, and traceability locally and in CI 
  - **templates, checklists, and staged workflows** to gate generation, review, and validation through explicit stages with defined inputs, outputs, and checks
 
 **Jump to:** [Product shape](#product-shape) | [Fit and non-fit](#fit-and-non-fit) | [Operating model](#operating-model) | [Traceability and validation model](#traceability-and-validation-model) | [Workflow model](#workflow-model) | [Typical delivery sequence](#typical-delivery-sequence) | [Supported hosts](#supported-hosts) | [Evaluate Cyber Pilot](#evaluate-cyber-pilot) | [Installation and setup reference](#installation-and-setup-reference)
 
 ## Product shape
 
  ### Authoritative delivery artifacts
 
  - **Requirements and design artifacts** become the approved, file-backed source of scope, intent, and constraints for downstream work.
  - **Plans** turn that approved intent into bounded execution shape before implementation sprawls across one long chat.
  - **Checklists** make review and validation expectations visible instead of leaving them implicit in chat or memory.
  - **Implementation changes** are reviewed against those approved artifacts rather than as isolated code diffs.
 
  ### What Cyber Pilot adds to a repo
 
  After `cpt init` and `cpt generate-agents`, Cyber Pilot typically adds a setup directory such as `cypilot/` or `.cpt/`, generated AI coding tool integration files, and user-editable configuration under `config/` inside the chosen setup directory.
 
  This repo-installed control surface is how Cyber Pilot becomes operationally real inside a repository rather than staying a chat convention. It is also the first concrete proof surface most teams can inspect directly: what is generated, what remains user-editable, what is optional, and what deterministic validation can see.
 
  - **Generated** — AI coding tool integration files and repository wiring
  - **User-editable** — project configuration, rules, and any installed kit content meant for local use
  - **Optional** — installed kit content extends the base platform only when you want a more opinionated delivery model
  - **Validator-visible** — artifacts, plans, and configuration participate in deterministic `cpt` checks when those configured surfaces are in use
 
  ### Core platform and optional kits
 
  Cyber Pilot has two main parts:
 
  - **Core platform** — the repository wiring, workflow routing, configuration surfaces, deterministic validation, and chat-facing skill that make the delivery model operational and repeatable
  - **Kits** — optional add-ons that specialize that same delivery model with domain-specific templates, rules, workflows, and validation material
 
  Most teams should start with the core platform and add a kit later only if they want a ready-made delivery model for a specific domain or way of working. Kits extend the same underlying system rather than introducing a separate product shape.
 
  ### How teams encounter Cyber Pilot
 
  In practice, teams usually encounter and touch Cyber Pilot through four main surfaces in the repository and toolchain:
 
  | Surface | Form | Role |
  |---|---|---|
  | Primary AI surface | `cypilot <workflow>: <request>` | Main chat entry point for `plan`, `generate`, and `analyze` requests |
  | Deterministic CLI | `cpt <command>` | Setup, validation, updates, and repeatable local or CI checks |
  | Generated AI coding tool integration files | generated files in the repository | Connect the repository or workspace to supported tools without manual setup in each host |
 | Optional kit content | installed kit content | Add domain-specific templates, rules, workflows, and validation material |

 ## Fit and non-fit

 Use Cyber Pilot if you already work with an AI coding tool and the cost of ambiguity, rework, or review failure is high enough to justify more structure and control.

 ### Helps most when you are responsible for

  - **Implementation work** that needs to stay bounded, inspectable, and safer to continue across more than one step
  - **Alignment across handoffs or review checkpoints** so requirements, design, plans, and implementation do not drift apart
  - **Review or delivery accountability** when approved scope needs reviewable evidence, clearer status surfaces, or deterministic checks before merge

 ### Good fit when

  - you have a multi-step, higher-risk, or review-sensitive change where the cost of ambiguity or rework is higher than the cost of added structure
  - the work needs bounded execution and reviewable alignment across approved inputs, implementation, and review, not just a quick diff
  - you are working in a brownfield or unfamiliar area and need understanding before editing, not just speed while editing
  - coordination, handoffs, or deterministic validation materially reduce risk before review or merge

 ### Not the best fit when

  - the task is a tiny edit, throwaway spike, or open-ended exploration
  - the change is already well understood, low risk, and fast to make locally without added coordination or review structure
  - speed matters more than structure and the shape of the work is still unclear
  - you do not want artifact-backed process, staged review, or deterministic validation overhead even when the task is non-trivial
  - your team rejects workflow discipline or does not want to maintain the delivery surfaces that make review and validation easier

 ### Where value appears first

  - a first bounded plan that makes a risky or unfamiliar change easier to execute in stages
  - a first inspectable understanding surface for an unfamiliar area before you start changing code
  - a first deterministic validation result or drift signal before review or merge instead of trusting one generation pass
  - a first reviewable linkage between approved inputs and the implementation under review

 ## Operating model

 ### System boundary and control model

Cyber Pilot is best understood as the **workflow, context, and validation layer around your AI coding tool**.

Your AI coding tool gives you the chat interface and model access. The agent does the reasoning and writing. Cyber Pilot adds structured workflows, task-matched context, and deterministic checks around that work.

- **Use the agent for**
  - reasoning
  - writing
  - transformation
  - implementation judgment

- **Use Cyber Pilot for**
  - workflow selection
  - task-matched context loading
  - templates, rules, and checklists
  - keeping requirements, design, and code linked through the same identifiers
  - planning large tasks into bounded steps

 ### Deterministic vs non-deterministic boundary

- **Deterministic**
  - config and resource resolution
  - routing into workflows and specialized commands
  - repeatable command behavior for the same configured project surface

- **Non-deterministic**
  - the agent's reasoning, writing quality, and implementation judgment
  - human review decisions

- **What tradeoff does Cyber Pilot make?**
  - more process and context in exchange for more control, auditability, and repeatability

For the full fit / non-fit guidance, practical anti-patterns, planning heuristics, and workflow-choice rules, use **[guides/USAGE-GUIDE.md](guides/USAGE-GUIDE.md)**.

## Traceability and validation model

Cyber Pilot is strongest when the delivery surface is explicit and checkable.

The inspectable surface is the repository material you can review directly. The configured enforcement surface is the subset of that material that the repository has chosen to make validator-visible to deterministic `cpt` checks.

### Inspectable delivery surface

- **File-backed artifacts** keep requirements, design, plans, and implementation visible as inspectable delivery inputs and outputs.
- **Stable identifiers and cross-links** connect those artifacts through one shared traceability surface.
- **Templates, checklists, and file-backed plans** create review surfaces that can be inspected and repeated.
- **Validation and review outputs** become visible evidence when the repository uses Cyber Pilot's traceability model.
- **Drift signals** surface through broken links, failed checks, and missing required structure instead of being reconstructed ad hoc later.

### Configured enforcement surface

- **Not every inspectable artifact is automatically enforced**; deterministic enforcement applies only to validator-visible material the repository has configured `cpt` to check.
- **IDs, required links, document structure, plans, and stage completeness** become enforceable when they are part of that configured validation surface.
- **The same configured surface can be checked locally and in CI** so enforcement is repeatable instead of chat-dependent.

### Evidence chain across a change

- **Requirement** captures the approved scope.
- **Design** records the intended structure, constraints, or boundary decisions.
- **Plan** breaks the change into bounded execution steps.
- **Implementation** maps code changes back to that approved scope.
- **Validation result** shows whether the configured structure, links, and review surfaces still hold.

### What `cpt` enforces

These are the main deterministic enforcement classes applied to that configured surface.

- **Artifact and document structure** such as required shape, expected sections, and validator-visible files
- **Identifier and reference integrity** across requirements, design, plans, code, and their cross-links
- **Required links and traceability rules** that keep artifacts aligned through the same stable identifiers
- **TOC and document consistency** where those checks are part of the configured validation surface
- **Plan, checklist, and stage completeness** when the repository uses file-backed planning and review surfaces
- **Repeatable local and CI validation outputs** for the same configured validation surface

### What Cyber Pilot cannot prove

- **Generation quality and implementation judgment** remain non-deterministic and still require review.
- **Human approval decisions** remain judgment-based even when the artifacts, structure, and links are checkable.

## Workflow model

Cyber Pilot has three core workflows. Each has a portable chat form and, in some hosts, a matching slash-command alias.

| Workflow | Portable chat form | Matching alias in some hosts | Use it when |
|---|---|---|---|
| Plan | 💬 `cypilot plan: ...` | 💬 `/cypilot-plan` | the task is too large, risky, or context-heavy for one conversation |
| Generate | 💬 `cypilot generate: ...` | 💬 `/cypilot-generate` | you want to create, update, implement, or configure something |
| Analyze | 💬 `cypilot analyze: ...` | 💬 `/cypilot-analyze` | you want to validate, review, inspect, compare, or audit |

The portable 💬 `cypilot <workflow>: ...` form is the best default. Slash commands are host-specific aliases, not separate capabilities.

Use `plan` to bound large work, `generate` to implement within approved scope, and `analyze` to review, validate, or inspect the result.

For default routing priorities and detailed workflow-choice advice, use **[guides/USAGE-GUIDE.md](guides/USAGE-GUIDE.md)**.

## Typical delivery sequence

Cyber Pilot is strongest when an early idea or PoC needs to become a production-ready change without losing scope or design intent.

In practice, teams usually move through four visible stages:

1. **Approve the requirement and design** so the change starts from explicit scope and constraints.
2. **Use `plan` to split larger work into bounded phases** before execution sprawls across one long chat.
3. **Use `generate` within approved scope** so implementation stays tied to the intended change.
4. **Use `analyze` and deterministic checks before merge** so review sees both the implementation and its validation surface.

In practice, this creates clearer boundaries, earlier drift detection, and more reliable review evidence than one long mixed-purpose chat.

## Supported hosts

Cyber Pilot works across multiple AI coding tools, but some hosts support its structured workflows more fully than others.

| Host | Best first use | Notes |
|---|---|---|
| Claude Code | Best starting point for full workflow support | Strongest support for isolated task flow, subagents, and separate generation/review passes |
| Cursor | Good editor-first starting point | Strong everyday IDE choice, with a smoother general workflow than the more orchestration-heavy hosts |
| GitHub Copilot | Good for familiar editor and GitHub-centered workflows | Supports structured Cyber Pilot use, but with less control over task orchestration than Claude Code |
| OpenAI Codex | Best for narrow, well-scoped tasks | Works best when task boundaries are tight and validation steps are clearly specified |
| Windsurf | Usable with manual workflow discipline | Works without subagents, but you should separate generation and review into different chats |

If you are unsure where to start, **Claude Code** currently gives the clearest first experience for the full Cyber Pilot workflow.

For host-specific setup guidance, deeper tradeoffs, and the full support matrix, use **[guides/AGENT-TOOLS.md](guides/AGENT-TOOLS.md)**.

## Evaluate Cyber Pilot

Use this path if you are evaluating Cyber Pilot in a real repository and want one concrete result quickly.

### Minimal evaluation path

1. **Pick one real repository and one real input** such as a requirement, design note, or change request.
2. **Install and initialize once** with 🖥️ `pipx install git+https://github.com/cyberfabric/cyber-pilot.git`, 🖥️ `cpt init`, and 🖥️ `cpt generate-agents`.
3. **Activate Cyber Pilot in chat** with 💬 `cypilot on` in the AI coding tool attached to that repository.
4. **Run one focused request** with 💬 `cypilot analyze: ...` or 💬 `cypilot plan: ...` against that real input.

### Validation checkpoint

- **Run one deterministic check** with 🖥️ `cpt validate --local-only` when you want to verify only the current repository, or 🖥️ `cpt validate` when cross-repo or workspace resolution is part of the trial.
- **Treat either a clean pass or an actionable failure as useful evidence**; the point is to see whether Cyber Pilot makes drift visible operationally instead of leaving it implicit in chat.

### What success looks like

- **Activation is confirmed** in the repository attached to the AI coding tool chat.
- **One useful output appears** such as a bounded plan, clearer system summary, or validation surface you could act on immediately.
- **One deterministic validation signal appears** as either a clean local pass or a concrete failure you can inspect and act on.
- **The next step is clearer** than it was before the trial, even if you stop after one pass.

 ### What to inspect after the trial

 - **Scope anchoring** — whether the output stayed tied to the real requirement, design note, or change request.
 - **Reviewability** — whether the resulting artifacts, plans, or validation outputs are easier to inspect than one long mixed-purpose chat.
 - **Trust signal** — whether you would trust the resulting surface enough to continue with a larger change.

 **Jump to:** [Installation and setup reference](#installation-and-setup-reference) | [Configuration files](#configuration-files) | [Extended operating modes](#extended-operating-modes) | [Project extensibility](#project-extensibility) | [Further reading](#further-reading)

 ## Installation and setup reference

### Prerequisites

For a first trial, you need Python 3.11+, Git, and one supported AI coding tool such as Claude Code, Cursor, Windsurf, GitHub Copilot, or OpenAI Codex.

`pipx` is recommended for installing the CLI globally. `gh` is optional for PR review and PR status workflows.

> **Convention**: 💬 = paste into AI coding tool chat. 🖥️ = run in terminal.

### Setup commands

Use this section as the exact procedural path after the evaluation section above.

1. **Install the CLI**

    🖥️ **Terminal**:
    ```bash
    pipx install git+https://github.com/cyberfabric/cyber-pilot.git
    cpt --version
    ```

2. **Initialize the repository**

    🖥️ **Terminal**:
    ```bash
    cpt init
    cpt generate-agents
    ```

    This creates a setup directory such as `cypilot/` or `.cpt/`, generated AI coding tool integration files, and user-editable configuration under `config/` inside the chosen setup directory.

3. **Activate Cyber Pilot in chat**

    💬 **AI coding tool chat**:
    ```text
    cypilot on
    ```

4. **Run one focused request** with 💬 `cypilot analyze: ...` or 💬 `cypilot plan: ...`

For detailed host-specific setup, troubleshooting, and operational walkthroughs, use **[guides/AGENT-TOOLS.md](guides/AGENT-TOOLS.md)** and **[guides/USAGE-GUIDE.md](guides/USAGE-GUIDE.md)**.

## Configuration files

All user-editable configuration lives under `config/` inside your Cyber Pilot setup directory.

You do not need to understand all of this on day one. Most new users can start with 🖥️ `cpt init`, use the three Cyber Pilot workflows, and come back here later.

| File | What it controls |
|---|---|
| `core.toml` | Project settings, installed kits, and workspace-level configuration |
| `artifacts.toml` | How artifacts, systems, codebases, and traceability are mapped in the project |
| `AGENTS.md` | Task navigation rules that tell the agent which files to load for each job |
| `SKILL.md` | Always-on project instructions that apply across requests |
| `rules/*.md` | Optional topic-specific rules the agent loads for relevant tasks |

For full configuration details, see **[Configuration guide](guides/CONFIGURATION.md)**.

## Extended operating modes

You do not need these on day one. Add them when your use case justifies the extra surface area.

### Multi-repo workspaces

Cyber Pilot supports **multi-repo workspaces** so related docs, code, and shared kit assets can live in separate repositories and still stay aligned.

Use this when docs, code, or shared kit assets live in separate repos and still need to stay aligned.

For practical guidance, see **[guides/USAGE-GUIDE.md](guides/USAGE-GUIDE.md)**. For the full model and configuration rules, see **[requirements/workspace.md](requirements/workspace.md)**.

### RalphEx delegation

RalphEx support is optional.

When available, Cyber Pilot can hand off selected execution work to RalphEx under human supervision.

Use this when you want supervised execution handoff for bounded tasks instead of keeping all work interactive inside the current AI coding tool.

For when to delegate and how human review fits, see **[guides/USAGE-GUIDE.md](guides/USAGE-GUIDE.md)**.

## Project extensibility

Cyber Pilot supports **project-level extensibility**, not just installable kits.

Cyber Pilot can also load project-defined skills, subagents, workflows, and rules, so teams can extend behavior without packaging everything as a kit.

For the full model and examples, see **[guides/PROJECT-EXTENSIBILITY.md](guides/PROJECT-EXTENSIBILITY.md)**.

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
- **Environment details** such as OS, AI coding tool, model, and Cyber Pilot version if known

---

## Contributing

If you want to contribute, start with **[CONTRIBUTING.md](CONTRIBUTING.md)**.

---

## License

Cyber Pilot is licensed under the **Apache License 2.0**. See **[LICENSE](LICENSE)** for details.
