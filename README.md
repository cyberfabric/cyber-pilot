# **Spider**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0-green.svg)]()
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()

**Version**: 2.0 | **Status**: Active | **Language**: English

**Audience**: Prompt engineers, AI developers, software architects, engineering teams

**Spider** is a platform for weaving agentic systems: its threads (like prompts, templates, DSL, rules) run through the whole project, turning intent into consistent artifacts. **Spider** focuses on four principles — **feedback**, **transformation**, **determinism**, and **quality** — so you can derive documents from documents, code from documents, or documents from code while keeping everything aligned. Each transformation is a controlled step in a pipeline: feedback tightens the web, deterministic validation removes LLM variability, and traceability keeps every derived piece connected and reviewable.

As an **extensible platform**, **Spider** can be "trained" by registering thread packages called **Weavers**. Each **Weaver** bundles templates, rules, checklists and examples for a specific domain or use case. 

**Spider** comes with a built-in **SDLC Weaver** that implements a full Software Development Life Cycle (SDLC) pipeline from Product Requirements Document (PRD) to code, with traceability and validation at every step.

---

## Table of Contents

- [**Spider**](#spider)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Project Setup (Spider + Agents)](#project-setup-spider--agents)
  - [Using Spider](#using-spider)
    - [Example Prompts](#example-prompts)
    - [Agent Skill](#agent-skill)
    - [Workflow Commands](#workflow-commands)
    - [Checklists and Quality Gates](#checklists-and-quality-gates)
  - [Weaver: **Spider SDLC**](#weaver-spider-sdlc)
  - [Contributing](#contributing)

---

## Prerequisites

Before using **Spider**, ensure you have:

- **Python 3.8+** — Required for `spider` tool execution
- **Git** — For version control and submodule installation (recommended)
- **AI Agent** — Claude Code, Windsurf, Cursor, GH Copilot, or similar LLM-powered coding assistant integrated with your IDE

---

## Project Setup (Spider + Agents)

Add Spider to your repo, then initialize and generate agent proxy files.

```bash
# Option A: git submodule (recommended)
git submodule add https://github.com/cyberfabric/Spider spider
git submodule update --init --recursive

# Option B: plain clone
git clone https://github.com/cyberfabric/Spider spider
```

```bash
# Agent-safe invocation (recommended)
python3 spider/skills/spider/scripts/spider.py init
python3 spider/skills/spider/scripts/spider.py agents --agent windsurf
```

Supported agents: `windsurf`, `cursor`, `claude`, `copilot`.

If you update the Spider submodule later, re-run:

```bash
python3 spider/skills/spider/scripts/spider.py agents --agent windsurf
```

## Using Spider

### Example Prompts

**Enable / Disable**

| Prompt | What the agent does |
|--------|---------------------|
| `spider on` | Enables Spider mode — discovers adapter, loads project context, shows available workflows |
| `spider off` | Disables Spider mode — returns to normal assistant behavior |

**Setup & Adapter Configuration**

| Prompt | What the agent does |
|--------|---------------------|
| `spider init` | Scans project structure, creates `.spider-adapter/` with `artifacts.json`, `AGENTS.md`, and domain specs |
| `spider configure adapter for Python monorepo with FastAPI` | Generates adapter with tech-stack specs, testing conventions, and codebase mappings |
| `spider add src/api/ to tracked codebase` | Updates `artifacts.json` to include directory in traceability scanning |
| `spider register SPEC at docs/specs/payments.md` | Adds artifact entry to `artifacts.json` with kind, path, and system mapping |
| `spider add tech-stack spec for PostgreSQL + Redis` | Creates `specs/tech-stack.md` with database and caching conventions |
| `spider update testing conventions` | Modifies `specs/testing.md` with project-specific test patterns |
| `spider show adapter config` | Displays `artifacts.json` structure, registered artifacts, and codebase mappings |
| `spider regenerate AGENTS.md` | Rebuilds navigation rules based on current artifact registry |

**Artifact Generation**

| Prompt | What the agent does |
|--------|---------------------|
| `spider make PRD for user authentication system` | Generates PRD with actors, capabilities, requirements, flows, and constraints following the template |
| `spider make DESIGN from PRD.md` | Transforms PRD into architecture design with components, interfaces, data models, and full traceability |
| `spider decompose auth spec into tasks` | Creates DECOMPOSITION artifact breaking the spec into ordered, dependency-mapped implementation units |
| `spider make SPEC spec for login flow` | Produces detailed spec design with acceptance criteria, edge cases, and code implementation instructions |

**Validation & Quality**

| Prompt | What the agent does |
|--------|---------------------|
| `spider validate PRD.md` | Runs deterministic template validation + semantic quality scoring against PRD checklist (50+ criteria) |
| `spider validate all` | Validates entire artifact hierarchy, checks cross-references, reports broken links and missing IDs |
| `spider validate code for auth module` | Scans code for `@spider-*` markers, verifies coverage against SPEC specs, reports unimplemented items |
| `spider review DESIGN.md with consistency-checklist` | Performs multi-phase consistency analysis detecting contradictions and alignment issues |

**With Checklists (Deep Review)**

| Prompt | What the agent does |
|--------|---------------------|
| `spider review PRD with PRD checklist, focus on requirements` | Applies 50+ expert criteria: completeness, testability, atomicity, no implementation leakage |
| `spider review SPEC spec with code-checklist` | Checks implementation readiness: error handling, security, edge cases, testing strategy |
| `spider validate codebase with reverse-engineering checklist` | Systematic code archaeology: identifies patterns, dependencies, undocumented behaviors |
| `spider improve this prompt with prompt-engineering checklist` | Applies prompt design guidelines: clarity, constraints, examples, output format |

**Traceability & Search**

| Prompt | What the agent does |
|--------|---------------------|
| `spider find requirements related to authentication` | Searches artifacts for IDs matching pattern, returns definitions and all references |
| `spider trace REQ-AUTH-001` | Traces requirement through DESIGN → SPEC → code, shows implementation locations |
| `spider list unimplemented specs` | Cross-references SPEC specs with code markers, reports items without `@spider-*` tags |

**Code Review & Pull Requests**

| Prompt | What the agent does |
|--------|---------------------|
| `spider review PR https://github.com/org/repo/pull/123` | Fetches PR diff, validates changes against design specs, checks traceability markers, reports coverage gaps |
| `spider review PR #59` | Reviews local PR by number — checks code quality, design alignment, and Spider marker consistency |
| `spider review PR with code-checklist` | Deep PR review applying code quality criteria: error handling, security, edge cases, testing |
| `spider analyze PR against SPEC spec` | Verifies PR implements all items from linked SPEC spec, reports missing or extra changes |
| `spider check PR traceability` | Scans PR diff for `@spider-*` markers, validates they reference existing design IDs |

**Weavers & Extensions**

| Prompt | What the agent does |
|--------|---------------------|
| `spider make weaver for API documentation` | Scaffolds weaver directory with template, rules, checklist, and examples for custom artifact kind |
| `spider register weaver at weavers/api-docs` | Adds weaver entry with format and path to artifact registry |
| `spider add ENDPOINT kind to api-docs weaver` | Creates template structure for new artifact kind with markers and validation rules |
| `spider show weaver SDLC` | Displays weaver directory layout, available artifact kinds, and their templates |
| `spider analyze weavers` | Checks template marker pairing, frontmatter, and rule syntax across all weavers |

### Agent Skill

Spider provides a single **Agent Skill** (`spider`) following the [Agent Skills specification](https://agentskills.io/specification). The skill is defined in `skills/spider/SKILL.md` and gets loaded into the agent's context when invoked.

The skill provides:
- Artifact validation and search capabilities
- ID lookup and traceability across documents and code
- Protocol guard for consistent context loading
- Integration with project adapter

When the skill is loaded, the agent gains access to Spider's CLI commands and workflow triggers.

### Workflow Commands

For agents that don't support the Agent Skills specification, Spider provides **workflow commands** — slash commands that load structured prompts guiding the agent through deterministic pipelines:

| Command | Workflow | Description |
|---------|----------|-------------|
| `/spider` | — | Enable Spider mode, discover adapter, show available workflows |
| `/spider-generate` | `workflows/generate.md` | Create/update artifacts (PRD, DESIGN, DECOMPOSITION, ADR, SPEC) or implement code with traceability markers |
| `/spider-analyze` | `workflows/analyze.md` | Validate artifacts against templates or code against design (deterministic + semantic) |
| `/spider-adapter` | `workflows/adapter.md` | Create/update project adapter — scan structure, configure rules, generate `AGENTS.md` and `artifacts.json` |

Each workflow includes feedback loops, quality gates, and references to relevant checklists and rules.

### Checklists and Quality Gates

Spider provides **expert-level checklists** for validation at each stage.

**Artifact checklists** in `weavers/sdlc/artifacts/{KIND}/`:
- [**PRD checklist**](weavers/sdlc/artifacts/PRD/checklist.md) — 300+ criteria for requirements completeness, stakeholder coverage, constraint clarity
- [**DESIGN checklist**](weavers/sdlc/artifacts/DESIGN/checklist.md) — 380+ criteria for architecture validation, component boundaries, integration points
- [**DECOMPOSITION checklist**](weavers/sdlc/artifacts/DECOMPOSITION/checklist.md) — 130+ criteria for spec breakdown quality, dependency mapping
- [**SPEC checklist**](weavers/sdlc/artifacts/SPEC/checklist.md) — 380+ criteria for implementation readiness, acceptance criteria, edge cases
- [**ADR checklist**](weavers/sdlc/artifacts/ADR/checklist.md) — 270+ criteria for decision rationale, alternatives analysis, consequences

**Generic checklists** in `requirements/`:
- [**Code checklist**](requirements/code-checklist.md) — 200+ criteria for code quality, security, error handling, testing
- [**Consistency checklist**](requirements/consistency-checklist.md) — 45+ criteria for cross-artifact consistency and contradiction detection
- [**Reverse engineering**](requirements/reverse-engineering.md) — 270+ criteria for legacy code analysis methodology
- [**Prompt engineering**](requirements/prompt-engineering.md) — 220+ criteria for AI prompt design guidelines

Use checklists by referencing them in `/spider-analyze` or manually during review.

---

## Weaver: **Spider SDLC**

**Spider SDLC** is a production-ready software development life cycle (SDLC) SDD built on **Spider**. It fully leverages Spider’s capabilities — identifier-based **traceability**, reliable **workflows** that follow a strict protocol, and Weaver-defined rules and tasks, structured templates and quality checklists. Each Weaver can both generate (transform/derive) content and evaluate it: scoring semantic quality, validating artifact-to-artifact alignment (e.g., requirements → design → implementation), and enforcing structure against the templates defined in the weaver.

See the [SDLC Pipeline](weavers/sdlc/README.md) for a detailed overview of the **Spider SDLC** pipeline, artifact kinds, generation and validation processes, and references to related documentation.

---

## Contributing

We welcome contributions to **Spider**.

**How to contribute**:

1. **Report issues**: Use GitHub Issues for bugs, spec requests, or questions
2. **Submit pull requests**: Fork the repository, create a branch, submit PR with description
3. **Follow** **Spider** **methodology**: Use **Spider** workflows when making changes to **Spider** itself
4. **Update documentation**: Include doc updates for any user-facing changes

**Guidelines**:
- Follow existing code style and conventions
- Update workflows with real-world examples when possible
- Maintain backward compatibility
- Document breaking changes in version history
- Add tests for new functionality

**Development setup**:
```bash
git clone <spider-repo-url>
cd spider
make test-coverage
make self-check
make validate
```
