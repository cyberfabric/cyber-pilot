# <img src="cypilot.png" alt="Cypilot" width="256" /> 
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0-green.svg)]()
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()

**Version**: 2.0 | **Status**: Active | **Language**: English

**Audience**: Prompt engineers, AI developers, software architects, engineering teams

<p align="center">
  <img src="images/cypilot-kit.png" alt="Cypilot Banner" width="100%" />
</p>

**Cyber Pilot** (Cypilot) helps you build agentic systems that don’t drift.

It turns intent into a deterministic, reviewable pipeline of artifacts — prompts, templates, rules, checklists, specs, and code — so teams can ship agent-driven changes with confidence.

**What you get**
- **Less drift** — keep prompts, docs, and code aligned as the project evolves
- **More determinism** — validation gates reduce “LLM randomness” in outputs
- **End-to-end traceability** — link PRD → design → tasks → code for easier reviews
- **Reusable building blocks** — standardize workflows via curated domain packs

**How it works**
Cypilot is extensible: you register thread packages called **Kits**. A Kit bundles templates, rules, checklists, and examples for a specific domain or use case.

Cypilot ships with a built-in **SDLC Kit** that runs a full PRD → code pipeline, with traceability and validation at every step.

---

## Table of Contents

- [](#)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Project Setup (Cypilot + Agents)](#project-setup-cypilot--agents)
  - [Using Cypilot](#using-cypilot)
    - [Real Conversation (Prompt Excerpt)](#real-conversation-prompt-excerpt)
      - [1) Enable Cypilot mode](#1-enable-cypilot-mode)
      - [Enabling Cypilot mode](#enabling-cypilot-mode)
      - [Cypilot mode activation (Protocol Guard)](#cypilot-mode-activation-protocol-guard)
      - [Cypilot Mode Enabled](#cypilot-mode-enabled)
      - [Agent acknowledgment (required)](#agent-acknowledgment-required)
      - [What do you want to do next?](#what-do-you-want-to-do-next)
      - [2) Ask what Cypilot can do](#2-ask-what-cypilot-can-do)
      - [How I can help you (in Cypilot mode)](#how-i-can-help-you-in-cypilot-mode)
      - [What I need from you to proceed](#what-i-need-from-you-to-proceed)
      - [Status](#status)
      - [3) Ask what Cypilot can generate](#3-ask-what-cypilot-can-generate)
      - [What you can generate with me (Cypilot generate workflow)](#what-you-can-generate-with-me-cypilot-generate-workflow)
      - [What "generate" will not do blindly](#what-generate-will-not-do-blindly)
      - [How to ask (examples you can copy/paste)](#how-to-ask-examples-you-can-copypaste)
      - [One question so I can start the right "generate" path](#one-question-so-i-can-start-the-right-generate-path)
    - [Example Prompts](#example-prompts)
    - [Agent Skill](#agent-skill)
    - [Workflow Commands](#workflow-commands)
    - [Checklists and Quality Gates](#checklists-and-quality-gates)
  - [Kit: **Cypilot SDLC**](#kit-cypilot-sdlc)
  - [Contributing](#contributing)

---

## Prerequisites

Before using **Cypilot**, ensure you have:

- **Python 3.8+** — Required for `cypilot` tool execution
- **Git** — For version control and submodule installation (recommended)
- **AI Agent** — OpenAI Codex, Claude Code, Windsurf, Cursor, GH Copilot, or similar LLM-powered coding assistant integrated with your IDE

---

## Project Setup (Cypilot + Agents)

Add Cypilot to your repo, then initialize and generate agent proxy files.

```bash
# Option A: git submodule (recommended)
git submodule add https://github.com/cyberfabric/cyber-pilot cypilot
git submodule update --init --recursive

# Option B: plain clone
git clone https://github.com/cyberfabric/cyber-pilot cypilot
```

```bash
# Agent-safe invocation (recommended)
python3 cypilot/skills/cypilot/scripts/cypilot.py init
python3 cypilot/skills/cypilot/scripts/cypilot.py agents --agent windsurf
```

Supported agents: `windsurf`, `cursor`, `claude`, `copilot`, `openai`.

If you update the Cypilot submodule later, re-run:

```bash
python3 cypilot/skills/cypilot/scripts/cypilot.py agents --agent windsurf
```

## Using Cypilot

To use Cypilot, run your IDE with an AI agent (or run an agent in a terminal), and then start your requests with `cypilot`.

That prefix switches the agent into Cypilot mode: it loads the adapter + required rules, routes the request to the right workflow (analyze vs generate), and gates any file writes behind explicit confirmation.

### Real Conversation (Prompt Excerpt)

Below are a few real prompts from the story (with outcomes summarized). The full conversation is in [`guides/STORY.md`](guides/STORY.md).

#### 1) Enable Cypilot mode

Prompt: `cypilot on`

**Summary:** The user enables Cypilot mode. The agent runs Protocol Guard, loads required context files, and confirms the rules it will follow before proceeding.

<details>
  <summary>Expand chat details...</summary>

**USER**

`cypilot on`

**ASSISTANT**

_Thought for 2s_

#### Enabling Cypilot mode

You've explicitly turned **Cypilot mode on**.

Next I'll:

- Confirm I understand the Cypilot MUST rules
- Read the required Cypilot control files (`skills/cypilot/SKILL.md` and `.cypilot-adapter/AGENTS.md`) so I can follow the workflow correctly
- Ask what you want to do (analyze/generate/adapter, etc.)

_Read `SKILL.md` and 2 other files_

_Thought for 4s_

#### Cypilot mode activation (Protocol Guard)

Next I will:

- Read `requirements/extension.md` because the adapter file declares **Extends**.
- Run Cypilot's required **Protocol Guard** command `adapter-info` (read-only) so we can print the "Cypilot Mode Enabled / Adapter: …" status block.

_Read `extension.md`_

Command:

`python3`

_Output (as visible in screenshot; truncated):_

```json
...
"project_name": "Cypilot",
"status": "FOUND",
"project_root": "/Volumes/CaseSensitive/coding/cypilot",
"artifacts_registry_path": "/Volumes/CaseSensitive/coding/cypilot/.cypilot-adapter/artifacts.json",
"artifacts_registry": {
  "version": "1.0",
  "project_root": "..",
  "kits": {
    ...
  }
}
...
```

#### Cypilot Mode Enabled

```
Cypilot Mode Enabled
Adapter: FOUND at /Volumes/CaseSensitive/coding/cypilot/.cypilot-adapter
```

📟 [skills/cypilot/SKILL.md]: Completed "Protocol Guard" — ran `adapter-info` to confirm adapter status and load adapter registry metadata before any workflow action.

📟 [requirements/extension.md]: Entering "## Agent Instructions" — processing `**Extends**:` rules for the adapter instructions file.

📟 [requirements/extension.md]: Completing checklist task — Agent understands extension mechanism concept.

📟 [requirements/extension.md]: Completing checklist task — Agent has identified the base file being extended (`../AGENTS.md`).

📟 [requirements/extension.md]: Completing checklist task — Agent will follow the rules defined here (base loaded, no contradictions, no base-rule removal).

#### Agent acknowledgment (required)

- MUST = MANDATORY, not optional
- Skipping ANY MUST instruction = INVALID execution
- INVALID execution = output must be DISCARDED
- I will read ALL required files BEFORE proceeding
- I will follow workflows step-by-step WITHOUT shortcuts
- I will NOT create files without user confirmation (operation workflows)
- I will end EVERY response with a list of Cypilot files read while producing the response, why each file was read, and which initial instruction triggered opening each file

#### What do you want to do next?

Per Cypilot routing, tell me which workflow you want:

- Analyze (read-only): validate/review/inspect/check artifacts or code.
- Generate (modify): implement/fix/refactor/add/update code or artifacts.

</details>

#### 2) Ask what Cypilot can do

Prompt: `cypilot how can you help me?`

**Summary:** The user asks what Cypilot can do. The agent explains the two workflows (analyze vs generate), shows example prompts, and asks for a clear intent and target.

<details>
  <summary>Expand chat details...</summary>

**USER**

`cypilot how can you help me?`

**ASSISTANT**

_Thought for 5s_

📟 [execution-protocol]: Explaining how I can help under Cypilot mode — mapping your request to Cypilot's two workflows (analyze vs generate) so we follow the correct process.

#### How I can help you (in Cypilot mode)

Cypilot mode means I help you in a structured, workflow-driven way with strong traceability and deterministic checks.

**Analyze workflow (read-only)**

Use this when you want to inspect/validate/review without changing anything.

- Validate artifacts/code structure (schemas, cross-references, traceability)
- Locate IDs and trace usage (where something is defined/used)
- Audit project docs (PRD/DESIGN/ADRs/DECOMPOSITION consistency)

Example prompts you can give me:

- `cypilot analyze: validate all artifacts`
- `cypilot analyze: where-used --id <some-id>`
- `cypilot analyze: review architecture/PRD.md for gaps vs DESIGN.md`

**Generate workflow (modifies files)**

Use this when you want me to implement/fix/refactor/update code or artifacts.

- Implement features / fix bugs in the Cypilot CLI/tooling
- Update docs/artifacts while keeping them compliant
- Add tests and align with project conventions/specs

Example prompts:

- `cypilot generate: fix failing tests`
- `cypilot generate: add a new cypilot.py subcommand for <X>`
- `cypilot generate: refactor <module> to follow conventions`

#### What I need from you to proceed

Your prompt `cypilot how can you help me?` is intent-unclear (could be analyze or generate).

Reply with one of these, plus your goal:

- `cypilot analyze: <what you want to inspect>`
- `cypilot generate: <what you want to change/build>`

#### Status

- Completed: Explained Cypilot-mode capabilities and how to choose the correct workflow.
- Pending: You choose analyze (read-only) or generate (modify) + what target (artifact/code).

</details>

#### 3) Ask what Cypilot can generate

Prompt: `cypilot what can I generate with you?`

**Summary:** The user asks what "generate" can do. The agent lists supported write outcomes (adapter, architecture artifacts, code), what it will not do blindly, and provides copy/paste examples.

<details>
  <summary>Expand chat details...</summary>

**USER**

`cypilot what can I generate with you?`

**ASSISTANT**

_Thought for 18s_

📟 [execution-protocol]: I'm going to re-open `guides/ADAPTER.md` so I can accurately describe what kinds of "generate" actions are supported and what constraints apply, then I'll give you a concrete list of things you can generate and the exact prompts to use.

_Read `ADAPTER.md`_

📟 [execution-protocol]: Entering "Generate capabilities" — I'm mapping "what can I generate?" to Cypilot's supported WRITE outcomes (adapter, artifacts, codebase) and the immutable adapter rules you must not violate.

#### What you can generate with me (Cypilot generate workflow)

1) **Adapter (project context)**

- [Create/update `.cypilot-adapter/`]: `AGENTS.md` + spec files that define your tech stack, conventions, testing strategy, build/deploy, project structure, patterns, etc.
- [Add new adapter specs]: e.g. `security.md`, `performance.md`, `linting.md`, custom API guidelines, module-creation rules.

2) **Architecture artifacts (design → spec → implementation plan)**

- [PRD]: create/update `architecture/PRD.md` (actors, capabilities, requirements).
- [Overall DESIGN]: create/update `architecture/DESIGN.md` (requirements/principles, architecture, ADR index, etc.).
- [ADRs]: create new ADRs in `architecture/ADR/...` in the required format.
- [DECOMPOSITION]: update `architecture/DECOMPOSITION.md` to reflect spec breakdown and traceability.
- [SPEC docs]: create/update spec documents under `architecture/specs/...` (e.g. "template system"-style specs).

3) **Codebase changes (implementation)**

- [Implement/fix/refactor code]: especially the Cypilot CLI (`skills/cypilot/scripts/cypilot.py`) and related modules.
- [Add new CLI subcommands]: plus CLISPEC/docs updates if needed.
- [Add tests]: unit/integration tests aligned to the adapter's testing spec.
- [Build/CI tweaks]: updates to tooling/config consistent with build-deploy spec.

#### What "generate" will not do blindly

- [No surprise file creation]: I will ask for confirmation before creating new files (mandatory rule).
- [No breaking hierarchy]: We won't violate the design chain:

  `ADAPTER → PRD → OVERALL DESIGN → SPEC DESIGN → CODE`

- [No coding in DESIGN.md]: Actor flows / algorithms should be in Cypilot DSL (CDSL) where required, not embedded code.
- [Validation-first mindset]: We'll aim for the required scores (Overall ≥90/100, Spec 100/100) before "locking in" implementation direction.

#### How to ask (examples you can copy/paste)

- Adapter work

  `cypilot generate: create/update adapter specs for a new TypeScript + Next.js app`

- New feature from idea → design → code

  `cypilot generate: add a new feature "<feature>" — update PRD + DESIGN + spec, then implement`

- Code-first change

  `cypilot generate: add a new cypilot.py subcommand "<name>" that does <behavior>`

- Quality work

  `cypilot generate: refactor <module> to match conventions + add tests`

#### One question so I can start the right "generate" path

What do you want to generate right now?

- [Adapter] (project rules/specs)
- [Artifacts] (PRD/DESIGN/ADR/specs)
- [Code] (implementation/tests)

Reply with: `cypilot generate: <your goal>` + which of the three targets.

</details>

**End result of the full story:** A working example application ("Overwork Alert") with CLI + daemon wiring, deterministic validations, unit tests, and a successful manual macOS smoke test.

[Continue reading the story](guides/STORY.md)

### Example Prompts

**Enable / Disable**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot on` | Enables Cypilot mode — discovers adapter, loads project context, shows available workflows |
| `cypilot off` | Disables Cypilot mode — returns to normal assistant behavior |

**Setup & Adapter Configuration**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot configure adapter for Python monorepo with FastAPI` | Generates adapter with tech-stack specs, testing conventions, and codebase mappings |
| `cypilot add src/api/ to tracked codebase` | Updates `artifacts.json` to include directory in traceability scanning |
| `cypilot register SPEC at docs/specs/payments.md` | Adds artifact entry to `artifacts.json` with kind, path, and system mapping |
| `cypilot add tech-stack spec for PostgreSQL + Redis` | Creates `specs/tech-stack.md` with database and caching conventions |
| `cypilot update testing conventions` | Modifies `specs/testing.md` with project-specific test patterns |
| `cypilot show adapter config` | Displays `artifacts.json` structure, registered artifacts, and codebase mappings |
| `cypilot regenerate AGENTS.md` | Rebuilds navigation rules based on current artifact registry |

**Artifact Generation**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot make PRD for user authentication system` | Generates PRD with actors, capabilities, requirements, flows, and constraints following the template |
| `cypilot make DESIGN from PRD.md` | Transforms PRD into architecture design with components, interfaces, data models, and full traceability |
| `cypilot decompose auth spec into tasks` | Creates DECOMPOSITION artifact breaking the spec into ordered, dependency-mapped implementation units |
| `cypilot make SPEC spec for login flow` | Produces detailed spec design with acceptance criteria, edge cases, and code implementation instructions |

**Validation & Quality**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot validate PRD.md` | Runs deterministic template validation + semantic quality scoring against PRD checklist (50+ criteria) |
| `cypilot validate all` | Validates entire artifact hierarchy, checks cross-references, reports broken links and missing IDs |
| `cypilot validate code for auth module` | Scans code for `@cpt-*` markers, verifies coverage against SPEC specs, reports unimplemented items |
| `cypilot review DESIGN.md with consistency-checklist` | Performs multi-phase consistency analysis detecting contradictions and alignment issues |

**With Checklists (Deep Review)**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot review PRD with PRD checklist, focus on requirements` | Applies 50+ expert criteria: completeness, testability, atomicity, no implementation leakage |
| `cypilot review SPEC spec with code-checklist` | Checks implementation readiness: error handling, security, edge cases, testing strategy |
| `cypilot validate codebase with reverse-engineering checklist` | Systematic code archaeology: identifies patterns, dependencies, undocumented behaviors |
| `cypilot improve this prompt with prompt-engineering checklist` | Applies prompt design guidelines: clarity, constraints, examples, output format |

**Traceability & Search**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot find requirements related to authentication` | Searches artifacts for IDs matching pattern, returns definitions and all references |
| `cypilot trace REQ-AUTH-001` | Traces requirement through DESIGN → SPEC → code, shows implementation locations |
| `cypilot list unimplemented specs` | Cross-references SPEC specs with code markers, reports items without `@cpt-*` tags |

**Code Review & Pull Requests**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot review PR https://github.com/org/repo/pull/123` | Fetches PR diff, validates changes against design specs, checks traceability markers, reports coverage gaps |
| `cypilot review PR #59` | Reviews local PR by number — checks code quality, design alignment, and Cypilot marker consistency |
| `cypilot review PR with code-checklist` | Deep PR review applying code quality criteria: error handling, security, edge cases, testing |
| `cypilot analyze PR against SPEC spec` | Verifies PR implements all items from linked SPEC spec, reports missing or extra changes |
| `cypilot check PR traceability` | Scans PR diff for `@cpt-*` markers, validates they reference existing design IDs |

**Kits & Extensions**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot make kit for API documentation` | Scaffolds kit directory with template, rules, checklist, and examples for custom artifact kind |
| `cypilot register kit at kits/api-docs` | Adds kit entry with format and path to artifact registry |
| `cypilot add ENDPOINT kind to api-docs kit` | Creates template structure for new artifact kind with markers and validation rules |
| `cypilot show kit SDLC` | Displays kit directory layout, available artifact kinds, and their templates |
| `cypilot analyze kits` | Checks template marker pairing, frontmatter, and rule syntax across all kits |

### Agent Skill

Cypilot provides a single **Agent Skill** (`cypilot`) following the [Agent Skills specification](https://agentskills.io/specification). The skill is defined in `skills/cypilot/SKILL.md` and gets loaded into the agent's context when invoked.

The skill provides:
- Artifact validation and search capabilities
- ID lookup and traceability across documents and code
- Protocol guard for consistent context loading
- Integration with project adapter

When the skill is loaded, the agent gains access to Cypilot's CLI commands and workflow triggers.

### Workflow Commands

For agents that don't support the Agent Skills specification, Cypilot provides **workflow commands** — slash commands that load structured prompts guiding the agent through deterministic pipelines:

| Command | Workflow | Description |
|---------|----------|-------------|
| `/cypilot` | — | Enable Cypilot mode, discover adapter, show available workflows |
| `/cypilot-generate` | `workflows/generate.md` | Create/update artifacts (PRD, DESIGN, DECOMPOSITION, ADR, SPEC) or implement code with traceability markers |
| `/cypilot-analyze` | `workflows/analyze.md` | Validate artifacts against templates or code against design (deterministic + semantic) |
| `/cypilot-adapter` | `workflows/adapter.md` | Create/update project adapter — scan structure, configure rules, generate `AGENTS.md` and `artifacts.json` |

Each workflow includes feedback loops, quality gates, and references to relevant checklists and rules.

### Checklists and Quality Gates

Cypilot provides **expert-level checklists** for validation at each stage.

**Artifact checklists** in `kits/sdlc/artifacts/{KIND}/`:
- [**PRD checklist**](kits/sdlc/artifacts/PRD/checklist.md) — 300+ criteria for requirements completeness, stakeholder coverage, constraint clarity
- [**DESIGN checklist**](kits/sdlc/artifacts/DESIGN/checklist.md) — 380+ criteria for architecture validation, component boundaries, integration points
- [**DECOMPOSITION checklist**](kits/sdlc/artifacts/DECOMPOSITION/checklist.md) — 130+ criteria for spec breakdown quality, dependency mapping
- [**SPEC checklist**](kits/sdlc/artifacts/SPEC/checklist.md) — 380+ criteria for implementation readiness, acceptance criteria, edge cases
- [**ADR checklist**](kits/sdlc/artifacts/ADR/checklist.md) — 270+ criteria for decision rationale, alternatives analysis, consequences

**Generic checklists** in `requirements/`:
- [**Code checklist**](requirements/code-checklist.md) — 200+ criteria for code quality, security, error handling, testing
- [**Consistency checklist**](requirements/consistency-checklist.md) — 45+ criteria for cross-artifact consistency and contradiction detection
- [**Reverse engineering**](requirements/reverse-engineering.md) — 270+ criteria for legacy code analysis methodology
- [**Prompt engineering**](requirements/prompt-engineering.md) — 220+ criteria for AI prompt design guidelines

Use checklists by referencing them in `/cypilot-analyze` or manually during review.

---

## Kit: **Cypilot SDLC**

**Cypilot SDLC** is a production-ready software development life cycle (SDLC) SDD built on **Cypilot**. It fully leverages Cypilot’s capabilities — identifier-based **traceability**, reliable **workflows** that follow a strict protocol, and Kit-defined rules and tasks, structured templates and quality checklists. Each Kit can both generate (transform/derive) content and evaluate it: scoring semantic quality, validating artifact-to-artifact alignment (e.g., requirements → design → implementation), and enforcing structure against the templates defined in the kit.

See the [SDLC Pipeline](kits/sdlc/README.md) for a detailed overview of the **Cypilot SDLC** pipeline, artifact kinds, generation and validation processes, and references to related documentation.

---

## Contributing

We welcome contributions to **Cypilot**.

**How to contribute**:

1. **Report issues**: Use GitHub Issues for bugs, spec requests, or questions
2. **Submit pull requests**: Fork the repository, create a branch, submit PR with description
3. **Follow** **Cypilot** **methodology**: Use **Cypilot** workflows when making changes to **Cypilot** itself
4. **Update documentation**: Include doc updates for any user-facing changes

**Guidelines**:
- Follow existing code style and conventions
- Update workflows with real-world examples when possible
- Maintain backward compatibility
- Document breaking changes in version history
- Add tests for new functionality

**Development setup**:
```bash
git clone <cypilot-repo-url>
cd cypilot
make test-coverage
make self-check
make validate
```
