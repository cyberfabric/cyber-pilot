# FDD vs OpenSpec vs Spec Kit vs MCAF

## Scope and framing
This comparison focuses on how each framework/toolkit structures work for AI-assisted software development:
- How you express intent (requirements/specs)
- How you plan and execute implementation
- What validation gates exist
- How traceability, change management, and documentation are handled

## One-paragraph summaries

### FDD (Feature-Driven Design)
A design-first methodology with a layered artifact hierarchy (adapter → business context → overall design → features manifest → feature design → changes → code), strict artifact structure requirements (sections, IDs, cross-links), and deterministic validation gates with scoring. It emphasizes plain-English behavioral specs (FDL) and traceability from design to code.

### OpenSpec
A change-first, spec-driven workflow centered on explicit change folders and “delta specs” that patch a source-of-truth spec set. It is optimized for brownfield evolution and multi-spec updates by separating current truth (`openspec/specs/`) from proposals (`openspec/changes/`).

### Spec Kit
A spec-driven development toolkit that bootstraps a repo template and provides slash commands to generate a constitution, functional spec, technical plan, tasks, and then execute implementation through agent workflows (e.g., `/speckit.constitution` → `/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`). It is oriented around phase checkpoints and a “spec → plan → tasks → implement” pipeline.

### MCAF (managedcode/MCAF)
A process framework focused on predictability via repository-local context, verification gates (tests + static analysis as decision makers), and codified agent instructions in `AGENTS.md`. It is less about a fixed spec format and more about repository governance, testing discipline, and repeatable agent workflows.

---

## Cross-capability matrix

Legend:
- **✅ Native**: explicitly defined as a first-class concept in the framework
- **⚠️ Supported**: possible and described, but not the core organizing primitive
- **❌ Out of scope**: not a primary concern / not prescribed

| Capability | FDD | OpenSpec | Spec Kit | MCAF |
|---|---|---|---|---|
| **🎯 Primary organizing unit** | Feature + artifact layers | Change folder | Feature spec folder (numbered) | Repo + docs + gates |
| **🌱 Greenfield (0→1) fit** | ✅ Native | ⚠️ Supported (but optimized for evolution) | ✅ Native | ⚠️ Supported |
| **🏗️ Brownfield (1→n) fit** | ✅ Native | ✅ Native (explicitly emphasized) | ⚠️ Supported | ✅ Native |
| **💼 Business context artifact** | ✅ Native (`architecture/BUSINESS.md`) | ❌ Out of scope | ⚠️ Supported (inside spec; no dedicated artifact) | ⚠️ Supported (docs; no dedicated artifact) |
| **🏛️ Overall architecture artifact** | ✅ Native (`architecture/DESIGN.md` + ADR) | ⚠️ Supported (optional `design.md` per change; not global) | ⚠️ Supported (plan + supporting docs) | ⚠️ Supported (recommended docs/Architecture overview) |
| **📋 Feature catalog / roadmap artifact** | ✅ Native (`architecture/features/FEATURES.md`) | ❌ Out of scope | ⚠️ Supported (via multiple specs; not a single manifest) | ⚠️ Supported |
| **🔄 Change management artifact** | ✅ Native (`CHANGES.md` per feature) | ✅ Native (`openspec/changes/<id>/...`) | ⚠️ Supported (tasks + branch per feature) | ⚠️ Supported (plan recorded in issue/doc) |
| **📜 Spec-as-source-of-truth (regenerate mindset)** | ✅ Native (design artifacts are source of truth; code validated vs design) | ⚠️ Supported (specs are source of truth; changes archived into specs) | ✅ Native (spec drives plan/tasks/implementation) | ⚠️ Supported (docs + tests are truth gates) |
| **🔁 Living specs update model** | Changes planned in `CHANGES.md`; history in `archive/` per feature | Archive merges approved deltas back into `openspec/specs/` | Specs live in `specs/<nnn-feature>/...` and evolve via branch/PR lifecycle | Truth is proven by tests/analyzers; docs must reflect the system that exists |
| **🔀 Delta/patch spec format** | ❌ Out of scope | ✅ Native (ADDED/MODIFIED/REMOVED/RENAMED requirements) | ❌ Out of scope | ❌ Out of scope |
| **📐 Formal requirement format constraints** | ✅ Native (FDL for behaviors; no code in designs) | ✅ Native (requirements + scenarios; SHALL/MUST) | ⚠️ Supported (templates; constitution; process) | ⚠️ Supported (English docs; defined test flows) |
| **🔒 Artifact schema strictness (required sections/IDs)** | ✅ Native (requirements define exact structure per artifact) | ✅ Native (change folder + delta format are prescribed) | ⚠️ Supported (templates; constitution) | ⚠️ Supported (recommended doc layout; repo conventions) |
| **🧾 Workflow spec strictness (prereqs/steps/criteria/checklists)** | ✅ Native (workflow file structure is prescribed; checklists + criteria) | ⚠️ Supported (strong checklists; less of a global workflow file schema) | ⚠️ Supported (phase pipeline + prerequisites; less of a formal workflow schema) | ⚠️ Supported (AGENTS.md + DoD/gates; less of a workflow file schema) |
| **🔗 Cross-artifact integrity across a layered doc stack (IDs/refs/coverage)** | ✅ Native (ID conventions + cross-reference checks across layers) | ❌ Out of scope (change folder is the organizing unit; not a layered doc stack) | ❌ Out of scope | ⚠️ Supported (via repo discipline; not prescribed as a validator) |
| **✅ Deterministic doc/schema validator (format/placeholders/required fields)** | ✅ Native (`fdd validate ...`) | ✅ Native (`openspec validate ... --strict`) | ⚠️ Supported (templates + structured analysis/checklists; not a strict doc validator) | ❌ Out of scope |
| **🔍 Deterministic cross-reference validator (doc↔doc)** | ✅ Native (cascading dependency + cross-ref checks) | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope |
| **🏷️ Deterministic code traceability validator (design/spec → code markers)** | ✅ Native (scans for `@fdd-*` tags) | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope |
| **🔬 Traceability granularity** | Instruction-level (`ph-*` + `inst-*`) + code markers | Change-level (proposal/tasks/deltas per change) | Task-level (spec → plan → tasks; tasks include file paths) | Verification-level (docs ↔ tests/analyzers; repo conventions) |
| **📊 Scoring / thresholds (beyond pass/fail)** | ✅ Native (100-point scoring + thresholds per workflow) | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope |
| **🚧 Strict phase gates** | ✅ Native (layer-by-layer validation chain) | ✅ Native (default workflow); experimental OPSX can be fluid (no strict gates) | ✅ Native (phase checkpoints: spec → plan → tasks → implement) | ✅ Native (tests/analyzers gate completion) |
| **🤖 Agent instructions single source** | ✅ Native (`AGENTS.md` hierarchy) | ✅ Native (`openspec/AGENTS.md` + root hand-off) | ⚠️ Supported (slash commands + generated repo files) | ✅ Native (`AGENTS.md` governance + local AGENTS.md) |
| **⚙️ Repeatable automation packages ("skills")** | ✅ Native (FDD skill tool + scripts) | ⚠️ Supported (CLI + agent instructions) | ⚠️ Supported (scripts/templates) | ✅ Native (skills packages with scripts/references/assets) |
| **🧪 Executable gates (tests/analyzers) as decision makers** | ⚠️ Supported (methodology expects tests; adapter-driven) | ⚠️ Supported | ⚠️ Supported (constitution can mandate TDD; agents run real tools) | ✅ Native (tests + static analysis are decision makers) |
| **🌐 Integration/UI/API testing emphasis** | ⚠️ Supported (tooling can validate code vs spec; test strategy is adapter-driven) | ⚠️ Supported | ⚠️ Supported | ✅ Native (explicitly emphasized as "hard gate") |
| **🎭 Mocks/fakes policy** | ❌ Out of scope (adapter-defined) | ❌ Out of scope | ❌ Out of scope | ✅ Native (restricted; prefer real containers for internal systems) |
| **👮 Governance of instruction changes** | ⚠️ Supported (via repo process; not the central concept) | ⚠️ Supported | ⚠️ Supported | ✅ Native (AGENTS.md changes require human approval) |
| **🗂️ Multi-repo / workspace planning** | ❌ Out of scope (core) | 🚀 Emerging (workspaces "coming soon") | ❌ Out of scope | ❌ Out of scope |
| **🔧 Tech stack dependency** | None (methodology; tool is Python stdlib) | Node.js (CLI) | Python (specify CLI; commonly installed via `uv`); agent integrations vary | None (process; repo-specific) |

### Quantitative scoring analysis

**Scoring methodology:**
- ✅ **Native = 3 points** (full first-class support)
- ⚠️ **Supported = 1 point** (partial/possible support)
- ❌ **Out of scope = 0 points** (absence is not penalized)
- 🚀 **Emerging = 0.5 points** (planned/in development)

This is an industry-standard linear weighting system for feature comparison matrices. "Out of scope" receives 0 (not negative) because frameworks intentionally specialize—absence of a feature is not a deficiency if it's outside the framework's design goals.

**Scoring results:**

| Framework | Native (×3) | Supported (×1) | Out of scope (×0) | Emerging (×0.5) | **Total Score** |
|-----------|-------------|----------------|-------------------|-----------------|-----------------|
| **FDD** | 16 × 3 = 48 | 6 × 1 = 6 | 6 × 0 = 0 | 0 × 0.5 = 0 | **54** |
| **OpenSpec** | 9 × 3 = 27 | 9 × 1 = 9 | 9 × 0 = 0 | 1 × 0.5 = 0.5 | **36.5** |
| **Spec Kit** | 4 × 3 = 12 | 14 × 1 = 14 | 10 × 0 = 0 | 0 × 0.5 = 0 | **26** |
| **MCAF** | 8 × 3 = 24 | 12 × 1 = 12 | 8 × 0 = 0 | 0 × 0.5 = 0 | **36** |

**Breakdown by framework:**

**FDD (54 points):**
- Native: Greenfield fit, Brownfield fit, Business context, Architecture artifact, Feature catalog, Change management, Spec-as-source-of-truth, Formal requirements, Schema strictness, Workflow spec strictness, Cross-artifact integrity, Doc validator, Cross-reference validator, Code traceability validator, Scoring/thresholds, Phase gates
- Supported: Agent instructions, Repeatable automation, Executable gates, Integration testing, Governance, Multi-repo (out of scope core)
- Strengths: Strongest in **artifact structure**, **traceability**, and **deterministic validation**

**OpenSpec (36.5 points):**
- Native: Brownfield fit, Change management, Delta/patch format, Formal requirements, Schema strictness, Doc validator, Phase gates, Agent instructions
- Supported: Greenfield fit, Architecture artifact, Spec-as-source-of-truth, Workflow spec strictness, Repeatable automation, Executable gates, Integration testing, Governance
- Emerging: Multi-repo/workspace planning
- Strengths: Strongest in **change-centric workflows** and **delta tracking**

**MCAF (36 points):**
- Native: Brownfield fit, Phase gates, Agent instructions, Repeatable automation, Executable gates, Integration testing, Mocks/fakes policy, Governance
- Supported: Greenfield fit, Business context, Architecture artifact, Feature catalog, Change management, Spec-as-source-of-truth, Formal requirements, Schema strictness, Workflow spec strictness, Cross-artifact integrity
- Strengths: Strongest in **verification gates** and **testing discipline**

**Spec Kit (26 points):**
- Native: Greenfield fit, Spec-as-source-of-truth, Phase gates
- Supported: Brownfield fit, Business context, Architecture artifact, Feature catalog, Change management, Formal requirements, Schema strictness, Workflow spec strictness, Doc validator, Agent instructions, Repeatable automation, Executable gates, Integration testing, Governance
- Strengths: Strongest in **bootstrap/setup** and **guided pipeline**

**Key insights:**

1. **FDD leads in total capability coverage** (54 points), particularly excelling in structured documentation, cross-artifact integrity, and multi-layer traceability.

2. **OpenSpec and MCAF are close in practical terms** (~36 points each), but with different specializations:
   - OpenSpec: Change management and evolution tracking
   - MCAF: Testing discipline and verification gates

3. **Spec Kit has the broadest "Supported" coverage** (14 capabilities) but fewer "Native" features (4), indicating a generalist approach with less opinionated enforcement.

4. **Specialization vs. breadth trade-off:**
   - FDD: Deep native support for design-first methodology
   - OpenSpec: Deep native support for change-first workflow
   - MCAF: Deep native support for verification-first process
   - Spec Kit: Broad support across many areas with lighter enforcement

5. **No framework scores on "Tech stack dependency"** (informational row, not a capability).

**Important caveat:** This scoring reflects **capability breadth**, not **fitness for a specific use case**. A framework with a lower score may be the perfect choice for your specific needs. See "Best-fit use cases" section for guidance.

---

## Deep comparison (dimensions)

### 1) “Center of gravity”
- **FDD**: Design hierarchy + traceability (business → architecture → feature decomposition → features manifest → feature designs → changes → code).
- **OpenSpec**: Change proposal + delta spec + archiving into living specs.
- **Spec Kit**: Spec-driven pipeline with a constitution + artifacts generated via slash commands (constitution → spec → plan → tasks → implement).
- **MCAF**: Predictability via shared repo context + tests/analyzers as gates + explicit agent instructions.

### 2) Artifact model and where truth lives
- **FDD**
  - Truth is captured in a layered architecture of Markdown artifacts.
  - Strong separation of concerns: business context vs architecture vs feature designs vs implementation plans.
  - Living evolution: implementation planning captured in `CHANGES.md`; historical change plans archived per feature.
- **OpenSpec**
  - Truth lives in `openspec/specs/`.
  - Proposals and deltas live in `openspec/changes/<change-id>/` and are later archived/merged into specs.
  - Living evolution: `archive` is the explicit mechanism for folding approved deltas back into the source-of-truth specs.
- **Spec Kit**
  - Truth is in generated spec/plan/task documents under a feature spec directory; the constitution constrains downstream work.
  - Living evolution: specs live in `specs/<nnn-feature>/...` and naturally evolve via a branch/PR lifecycle.
- **MCAF**
  - Truth is in the repository as a whole: code + docs + tests + instructions; tests/analyzers arbitrate correctness.
  - Living evolution: documentation is updated to reflect actual behavior; “truth” is proven by tests and analyzers.

### 3) Validation gates and failure modes
- **FDD**: Explicit validation chain per layer; dependent artifacts require validated parents.
- **OpenSpec**: Validate change folder (strict) and do not implement before proposal is approved; archive after deployment.
- **Spec Kit**: Workflow emphasizes not moving to next phase until validated, but enforcement is primarily via process discipline + templates.
- **MCAF**: Feature docs and ADR are updated when needed; failing tests (including integration/API/UI) and analyzers block completion.

### 3.5) Types of determinism (what is “validated”)
- **FDD**: Deterministic validators for doc/schema, cross-artifact references, and code traceability via `@fdd-*` markers.
- **OpenSpec**: Deterministic validator for change folder structure and spec/delta format; `archive` is the gate back into living specs.
- **Spec Kit**: Deterministic setup tooling plus template constraints; validation is primarily agent/human-driven (analysis/checklists) rather than a strict spec validator.
- **MCAF**: Deterministic executable gates (tests + static analysis) are the decision makers.

### 4) Traceability
- **FDD**: First-class traceability from design IDs to code via tags and validation tooling, down to instruction-level granularity.
- **OpenSpec**: Traceability is “change-centric”: proposals/tasks/deltas are co-located per change.
- **Spec Kit**: Traceability is “spec pipeline-centric”: spec → plan → tasks → implement.
- **MCAF**: Traceability is “repo-centric”: docs link to tests and code; instructions standardize commands and workflow.

### 5) Best-fit use cases
- **FDD** fits best when you need:
  - Business-reviewable behavior specs (plain English), strong layered documentation, and design→code traceability.
  - Multi-feature systems where cross-feature consistency matters.
- **OpenSpec** fits best when you need:
  - Clear audit trail of changes, explicit deltas, and a workflow optimized for evolving existing behavior across multiple specs.
- **Spec Kit** fits best when you want:
  - A bootstrap template + a guided pipeline that turns “what/why” into plan and tasks and then drives implementation.
- **MCAF** fits best when you need:
  - Strong engineering hygiene: verification gates, disciplined AGENTS.md governance, and repo-local “single shared context.”

### 6) Artifact strictness and integrity controls
- **FDD**: Treats artifacts as a schema-driven system: each artifact has a required structure (section order/naming), strict ID formats, payload blocks, and cross-artifact reference rules; validation is designed to detect missing sections, broken links, placeholder content, invalid IDs, and cross-layer inconsistencies.
- **OpenSpec**: Strictness is concentrated in the change proposal: you get a prescribed change folder layout and delta spec conventions with validation on the proposal itself; it is less focused on global cross-artifact integrity across a layered documentation stack.
- **Spec Kit**: Strictness is primarily constitutional/template-driven (process discipline), not enforced by a dedicated deterministic validator across documents.
- **MCAF**: Strictness is enforced via repository gates (tests/analyzers) and governance (instructions), rather than a required schema for architecture/spec artifacts.

### 7) Where FDD is unusually strong
- Layered artifacts are backed by explicit structure requirements and an execution protocol (workflows and requirements are first-class).
- Workflows themselves are structured specs (prerequisites, ordered steps, validation criteria/checklists), which reduces ambiguity for AI agents.
- Deterministic tooling is not only format checking: it includes cascading dependency validation and cross-artifact integrity checks.
- Traceability is explicit and can be made instruction-level (phases + instruction IDs), enabling design→code auditability.
- Scoring/threshold gates encourage consistent quality and make “done” more objective.

---

## Practical interoperability patterns

### Pattern A: FDD + OpenSpec (layered design + delta change tracking)
- Use **FDD** for layered artifacts and feature decomposition.
- Use **OpenSpec** for change proposals/deltas when you need an external-facing audit trail, or when multiple specs must be patched in a controlled way.

### Pattern B: Spec Kit for bootstrap, then migrate to FDD-style layering
- Use Spec Kit templates and constitution to generate initial spec/plan/tasks.
- When the system grows, adopt a layered approach (e.g., separate business context, global design, and per-feature designs).

### Pattern C: MCAF verification doctrine applied to any of the above
- Regardless of spec system, apply MCAF’s “tests + analyzers are decision makers” and strict instructions governance.

---

## Primary sources consulted

### FDD
- `README.md`, `WORKFLOW.md`, `QUICKSTART.md`, `ADAPTER_GUIDE.md`
- FDD workflow execution requirements and protocols in `requirements/` and `workflows/`

### OpenSpec
- https://github.com/Fission-AI/OpenSpec
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/README.md
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/openspec/AGENTS.md
- https://openspec.dev/

### Spec Kit
- https://github.com/github/spec-kit
- https://raw.githubusercontent.com/github/spec-kit/main/README.md
- https://raw.githubusercontent.com/github/spec-kit/main/spec-driven.md
- https://raw.githubusercontent.com/github/spec-kit/main/AGENTS.md
- https://raw.githubusercontent.com/github/spec-kit/main/memory/constitution.md
- https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/

### MCAF
- https://github.com/managedcode/MCAF
- https://mcaf.managed-code.com/
