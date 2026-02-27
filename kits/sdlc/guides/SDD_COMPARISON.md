# Cypilot vs OpenSpec vs Spec Kit vs MCAF vs BMAD vs Ralph

## Scope and framing
This comparison focuses on how each framework/toolkit structures work for AI-assisted software development:
- How you express intent (requirements/specs)
- How you plan and execute implementation
- What validation gates exist
- How traceability and documentation are handled

## One-paragraph summaries

### Cypilot (Spec-Driven Design)
A design-first methodology with a layered artifact hierarchy (adapter → PRD → DESIGN (+ ADR) → DECOMPOSITION → FEATURE → code), strict artifact structure requirements (sections, IDs, cross-links), and deterministic validation gates with scoring. It emphasizes plain-English behavioral designs (Cypilot DSL (CDSL)) and traceability from design to code.

### OpenSpec
A change-first, spec-driven workflow centered on explicit change folders and “delta specs” that patch a source-of-truth spec set. It is optimized for brownfield evolution and multi-spec updates by separating current truth (`{project-root}/openspec/specs/`) from proposals (`{project-root}/openspec/changes/`).

### Spec Kit
A spec-driven development toolkit that bootstraps a repo template and provides slash commands to generate a constitution, functional spec, technical plan, tasks, and then execute implementation through agent workflows (e.g., `/speckit.constitution` → `/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`). It is oriented around phase checkpoints and a “spec → plan → tasks → implement” pipeline.

### MCAF (managedcode/MCAF)
A process framework focused on predictability via repository-local context, verification gates (tests + static analysis as decision makers), and codified agent instructions in `AGENTS.md`. It is less about a fixed spec format and more about repository governance, testing discipline, and repeatable agent workflows.

### BMAD Method (BMAD-METHOD)
An AI-driven agile development framework built around guided workflows across four phases (analysis → planning → solutioning → implementation), specialized agent personas, and scale-adaptive tracks (Quick Flow vs BMad Method vs Enterprise). It generates and updates planning artifacts (PRD, architecture, epics/stories, sprint tracking) as workflow outputs and emphasizes one-story-at-a-time implementation.

### Ralph (loop agents)
A loop-based autonomy technique and tooling where an outer loop reruns an AI coding agent in fresh context until objective verification passes (tests/typecheck/build and/or an explicit completion signal). State lives on disk (specs/tasks/scratchpad), and quality gates act as “backpressure.” Orchestration can be minimal (a bash loop) or configurable via presets and specialized personas.

---

## Cross-capability matrix

Legend:
- **✅ Native**: explicitly defined as a first-class concept in the framework
- **⚠️ Supported**: possible and described, but not the core organizing primitive
- **❌ Out of scope**: not a primary concern / not prescribed

| Capability | Cypilot | OpenSpec | Spec Kit | MCAF | BMAD | Ralph |
|---|---|---|---|---|---|---|
| **🎯 Primary organizing unit** | Spec + artifact layers | Change folder | Spec spec folder (numbered) | Repo + docs + gates | Workflow phases + stories (epics/stories + sprint tracking) | Loop iterations + task list (PRD stories/tasks) |
| **🌱 Greenfield (0→1) fit** | ✅ Native | ⚠️ Supported (but optimized for evolution) | ✅ Native | ⚠️ Supported | ✅ Native | ⚠️ Supported |
| **🏗️ Brownfield (1→n) fit** | ✅ Native | ✅ Native (explicitly emphasized) | ⚠️ Supported | ✅ Native | ✅ Native | ⚠️ Supported |
| **💼 PRD artifact** | ✅ Native (`{project-root}/architecture/PRD.md`) | ❌ Out of scope | ⚠️ Supported (inside spec; no dedicated artifact) | ⚠️ Supported (docs; no dedicated artifact) | ⚠️ Supported (product brief / PRD outputs) | ⚠️ Supported (PRD/spec files; repo-defined) |
| **🏛️ Overall architecture artifact** | ✅ Native (`{project-root}/architecture/DESIGN.md` + ADR) | ⚠️ Supported (optional `design.md` per change; not global) | ⚠️ Supported (plan + supporting docs) | ⚠️ Supported (recommended docs/Architecture overview) | ✅ Native (architecture workflow outputs) | ⚠️ Supported |
| **📋 Spec catalog / roadmap artifact** | ✅ Native (`{project-root}/architecture/DECOMPOSITION.md`) | ❌ Out of scope | ⚠️ Supported (via multiple specs; not a single manifest) | ⚠️ Supported | ⚠️ Supported (epics/stories + sprint tracking) | ❌ Out of scope |
| **🔄 Change management artifact** | ❌ Out of scope | ✅ Native (`{project-root}/openspec/changes/<id>/...`) | ⚠️ Supported (tasks + branch per spec) | ⚠️ Supported (plan recorded in issue/doc) | ✅ Native (story/sprint tracking) | ⚠️ Supported |
| **📜 Spec-as-source-of-truth (regenerate mindset)** | ✅ Native (design artifacts are source of truth; code validated vs design) | ⚠️ Supported (specs are source of truth; changes archived into specs) | ✅ Native (spec drives plan/tasks/implementation) | ⚠️ Supported (docs + tests are truth gates) | ⚠️ Supported | ⚠️ Supported |
| **🔁 Living specs update model** | Artifacts are updated directly; design remains the source of truth | Archive merges approved deltas back into `{project-root}/openspec/specs/` | Specs live in `specs/<nnn-spec>/...` and evolve via branch/PR lifecycle | Truth is proven by tests/analyzers; docs must reflect the system that exists | Workflow outputs evolve via re-runs (e.g., `_bmad-output/` artifacts + status files) | Specs/tasks evolve via git; loop re-reads disk state each iteration |
| **🔀 Delta/patch spec format** | ❌ Out of scope | ✅ Native (ADDED/MODIFIED/REMOVED/RENAMED requirements) | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope |
| **📐 Formal requirement format constraints** | ✅ Native (Cypilot DSL (CDSL) for behaviors; no code in designs) | ✅ Native (requirements + scenarios; SHALL/MUST) | ⚠️ Supported (templates; constitution; process) | ⚠️ Supported (English docs; defined test flows) | ⚠️ Supported | ⚠️ Supported |
| **🔒 Artifact schema strictness (required sections/IDs)** | ✅ Native (requirements define exact structure per artifact) | ✅ Native (change folder + delta format are prescribed) | ⚠️ Supported (templates; constitution) | ⚠️ Supported (recommended doc layout; repo conventions) | ✅ Native (standards + create/validate/edit modes) | ⚠️ Supported |
| **🧾 Workflow spec strictness (prereqs/steps/criteria/checklists)** | ✅ Native (workflow file structure is prescribed; checklists + criteria) | ⚠️ Supported (schema-driven workflow + docs; not checklist-centric) | ⚠️ Supported (phase pipeline + prerequisites; less of a formal workflow schema) | ⚠️ Supported (AGENTS.md + DoD/gates; less of a workflow file schema) | ✅ Native (multi-step workflows + progressive disclosure) | ❌ Out of scope |
| **🧩 Progressive disclosure workflow execution (step isolation)** | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ✅ Native (AI sees only the current step) | ❌ Out of scope |
| **⏸️ Continuable workflows (pause/resume with persisted step state)** | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ✅ Native (continuable workflows) | ⚠️ Supported (disk state enables resuming) |
| **🔁 Fresh-context iteration loop (context reset per cycle)** | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ✅ Native (fresh context is a core tenet) |
| **🧪 Tri-modal workflows (Create / Validate / Edit modes)** | ⚠️ Supported (create/update workflows + separate validators) | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ✅ Native (create/validate/edit pattern) | ❌ Out of scope |
| **🔗 Cross-artifact integrity across a layered doc stack (IDs/refs/coverage)** | ✅ Native (ID conventions + cross-reference checks across layers) | ❌ Out of scope (change folder is the organizing unit; not a layered doc stack) | ❌ Out of scope | ⚠️ Supported (via repo discipline; not prescribed as a validator) | ❌ Out of scope | ❌ Out of scope |
| **✅ Deterministic doc/schema validator (format/placeholders/required fields)** | ✅ Native (`cypilot validate ...`) | ✅ Native (`openspec validate ... --strict`) | ⚠️ Supported (templates + structured analysis/checklists; not a strict doc validator) | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope |
| **🔍 Deterministic cross-reference validator (doc↔doc)** | ✅ Native (cascading dependency + cross-ref checks) | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope |
| **🏷️ Deterministic code traceability validator (design/spec → code markers)** | ✅ Native (scans for `@cpt-*` tags) | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope |
| **🔬 Traceability granularity** | Instruction-level (`p*` + `inst-*`) + code markers | Change-level (proposal/tasks/deltas per change) | Task-level (spec → plan → tasks; tasks include file paths) | Verification-level (docs ↔ tests/analyzers; repo conventions) | Task/story-level (PRD → stories → implementation) | Verification-level (tests/typecheck/build gates + disk state) |
| **📊 Scoring / thresholds (beyond pass/fail)** | ✅ Native (100-point scoring + thresholds per workflow) | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope |
| **🚧 Strict phase gates** | ✅ Native (layer-by-layer validation chain) | ⚠️ Supported (legacy workflow is phase-based; OPSX is actions-not-phases) | ✅ Native (phase checkpoints: spec → plan → tasks → implement) | ✅ Native (tests/analyzers gate completion) | ✅ Native (phase pipeline + workflow prerequisites) | ✅ Native (verification-driven loop stop conditions) |
| **🤖 Agent instructions single source** | ✅ Native (`AGENTS.md` hierarchy) | ⚠️ Supported (generated tool-specific instruction files via `openspec init` / `openspec update`) | ⚠️ Supported (slash commands + generated repo files) | ✅ Native (`AGENTS.md` governance + local AGENTS.md) | ✅ Native (specialized agents are core) | ⚠️ Supported |
| **⚙️ Repeatable automation packages ("skills")** | ✅ Native (Cypilot skill tool + scripts) | ⚠️ Supported (CLI + agent instructions) | ⚠️ Supported (scripts/templates) | ✅ Native (skills packages with scripts/references/assets) | ✅ Native (workflow library/modules) | ⚠️ Supported |
| **🧪 Executable gates (tests/analyzers) as decision makers** | ⚠️ Supported (methodology expects tests; adapter-driven) | ⚠️ Supported | ⚠️ Supported (constitution can mandate TDD; agents run real tools) | ✅ Native (tests + static analysis are decision makers) | ⚠️ Supported | ✅ Native |
| **🌐 Integration/UI/API testing emphasis** | ⚠️ Supported (tooling can validate code vs spec; test strategy is adapter-driven) | ⚠️ Supported | ⚠️ Supported | ✅ Native (explicitly emphasized as "hard gate") | ⚠️ Supported | ⚠️ Supported |
| **🎭 Mocks/fakes policy** | ❌ Out of scope (adapter-defined) | ❌ Out of scope | ❌ Out of scope | ✅ Native (restricted; prefer real containers for internal systems) | ❌ Out of scope | ❌ Out of scope |
| **👮 Governance of instruction changes** | ⚠️ Supported (via repo process; not the central concept) | ⚠️ Supported | ⚠️ Supported | ✅ Native (AGENTS.md changes require human approval) | ❌ Out of scope | ❌ Out of scope |
| **🗂️ Multi-repo / workspace planning** | ❌ Out of scope (core) | 🚀 Emerging (workspaces "coming soon") | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope | ❌ Out of scope |
| **🔧 Tech stack dependency** | Python (CLI tooling; stdlib-focused) | Node.js (CLI) | Python (specify CLI; commonly installed via `uv`); agent integrations vary | None (process; repo-specific) | Node.js (npx installer/modules) | Node.js/TypeScript (agent libs/orchestrators) |

### Quantitative scoring analysis

**Scoring methodology:**
- ✅ **Native = 3 points** (full first-class support)
- ⚠️ **Supported = 1 point** (partial/possible support)
- ❌ **Out of scope = 0 points** (absence is not penalized)
- 🚀 **Emerging = 0.5 points** (planned/in development)

This is a simple linear weighting system for the matrix. "Out of scope" receives 0 (not negative) because frameworks intentionally specialize—absence of a spec is not a deficiency if it's outside the framework's design goals.

**Scoring results:**

| Framework | Native (×3) | Supported (×1) | Out of scope (×0) | Emerging (×0.5) | **Total Score** |
|-----------|-------------|----------------|-------------------|-----------------|-----------------|
| **Cypilot** | 17 × 3 = 51 | 4 × 1 = 4 | 7 × 0 = 0 | 0 × 0.5 = 0 | **55** |
| **BMAD** | 12 × 3 = 36 | 6 × 1 = 6 | 10 × 0 = 0 | 0 × 0.5 = 0 | **42** |
| **MCAF** | 8 × 3 = 24 | 10 × 1 = 10 | 10 × 0 = 0 | 0 × 0.5 = 0 | **34** |
| **OpenSpec** | 6 × 3 = 18 | 10 × 1 = 10 | 11 × 0 = 0 | 1 × 0.5 = 0.5 | **28.5** |
| **Spec Kit** | 3 × 3 = 9 | 14 × 1 = 14 | 11 × 0 = 0 | 0 × 0.5 = 0 | **23** |
| **Ralph** | 3 × 3 = 9 | 12 × 1 = 12 | 13 × 0 = 0 | 0 × 0.5 = 0 | **21** |

**Breakdown by framework:**

**Cypilot (55 points):**
- Native: Greenfield fit, Brownfield fit, PRD artifact, Overall architecture artifact, Spec catalog / roadmap artifact, Spec-as-source-of-truth (regenerate mindset), Formal requirement format constraints, Artifact schema strictness (required sections/IDs), Workflow spec strictness (prereqs/steps/criteria/checklists), Cross-artifact integrity across a layered doc stack (IDs/refs/coverage), Deterministic doc/schema validator (format/placeholders/required fields), Deterministic cross-reference validator (doc↔doc), Deterministic code traceability validator (design/spec → code markers), Scoring / thresholds (beyond pass/fail), Strict phase gates, Agent instructions single source, Repeatable automation packages ("skills")
- Supported: Tri-modal workflows (Create / Validate / Edit modes), Executable gates (tests/analyzers) as decision makers, Integration/UI/API testing emphasis, Governance of instruction changes
- Strengths: Strongest in **artifact structure**, **traceability**, and **deterministic validation**

**BMAD (42 points):**
- Native: Greenfield fit, Brownfield fit, Overall architecture artifact, Change management artifact, Artifact schema strictness (required sections/IDs), Workflow spec strictness (prereqs/steps/criteria/checklists), Progressive disclosure workflow execution (step isolation), Continuable workflows (pause/resume with persisted step state), Tri-modal workflows (Create / Validate / Edit modes), Strict phase gates, Agent instructions single source, Repeatable automation packages ("skills")
- Supported: PRD artifact, Spec catalog / roadmap artifact, Spec-as-source-of-truth (regenerate mindset), Formal requirement format constraints, Executable gates (tests/analyzers) as decision makers, Integration/UI/API testing emphasis
- Strengths: Strongest in **guided workflow pipelines** and **workflow-driven artifact generation**

**MCAF (34 points):**
- Native: Brownfield fit, Strict phase gates, Agent instructions single source, Repeatable automation packages ("skills"), Executable gates (tests/analyzers) as decision makers, Integration/UI/API testing emphasis, Mocks/fakes policy, Governance of instruction changes
- Supported: Greenfield fit, PRD artifact, Overall architecture artifact, Spec catalog / roadmap artifact, Change management artifact, Spec-as-source-of-truth (regenerate mindset), Formal requirement format constraints, Artifact schema strictness (required sections/IDs), Workflow spec strictness (prereqs/steps/criteria/checklists), Cross-artifact integrity across a layered doc stack (IDs/refs/coverage)
- Strengths: Strongest in **verification gates** and **testing discipline**

**OpenSpec (28.5 points):**
- Native: Brownfield fit, Change management artifact, Delta/patch spec format, Formal requirement format constraints, Artifact schema strictness (required sections/IDs), Deterministic doc/schema validator (format/placeholders/required fields)
- Supported: Greenfield fit, Overall architecture artifact, Spec-as-source-of-truth (regenerate mindset), Workflow spec strictness (prereqs/steps/criteria/checklists), Repeatable automation packages ("skills"), Executable gates (tests/analyzers) as decision makers, Integration/UI/API testing emphasis, Governance of instruction changes, Strict phase gates, Agent instructions single source
- Emerging: Multi-repo / workspace planning
- Strengths: Strongest in **change-centric workflows** and **delta tracking**

**Spec Kit (23 points):**
- Native: Greenfield fit, Spec-as-source-of-truth (regenerate mindset), Strict phase gates
- Supported: Brownfield fit, PRD artifact, Overall architecture artifact, Spec catalog / roadmap artifact, Change management artifact, Formal requirement format constraints, Artifact schema strictness (required sections/IDs), Workflow spec strictness (prereqs/steps/criteria/checklists), Deterministic doc/schema validator (format/placeholders/required fields), Agent instructions single source, Repeatable automation packages ("skills"), Executable gates (tests/analyzers) as decision makers, Integration/UI/API testing emphasis, Governance of instruction changes
- Strengths: Strongest in **bootstrap/setup** and **guided pipeline**

**Ralph (21 points):**
- Native: Fresh-context iteration loop (context reset per cycle), Strict phase gates, Executable gates (tests/analyzers) as decision makers
- Supported: Greenfield fit, Brownfield fit, PRD artifact, Overall architecture artifact, Change management artifact, Spec-as-source-of-truth (regenerate mindset), Formal requirement format constraints, Artifact schema strictness (required sections/IDs), Continuable workflows (pause/resume with persisted step state), Agent instructions single source, Repeatable automation packages ("skills"), Integration/UI/API testing emphasis
- Strengths: Strongest in **verification-driven iteration** and **fresh-context loop discipline**

**Key insights:**

1. **Cypilot leads in total capability coverage** (55 points), particularly excelling in structured documentation, cross-artifact integrity, and multi-layer traceability.

2. **BMAD stands out for workflow execution capabilities** (42 points), primarily due to progressive disclosure, continuable workflows, and tri-modal create/validate/edit patterns.

3. **OpenSpec and MCAF cluster in the middle** (~28–34 points), but with different specializations:
   - OpenSpec: Change management and delta tracking
   - MCAF: Verification gates and testing discipline

4. **Spec Kit has broad "Supported" coverage** (14 capabilities) but fewer "Native" specs (3), indicating a generalist approach with lighter enforcement.

5. **Ralph scores lower on artifact/validator breadth** (21 points) because it is primarily an autonomy/loop technique; its strongest “native” specs are verification gates, fresh-context loops, and iteration/stop conditions.

6. **Specialization vs. breadth trade-off:**
   - Cypilot: Deep native support for design-first methodology
   - OpenSpec: Deep native support for change-first workflow
   - MCAF: Deep native support for verification-first process
   - Spec Kit: Broad support across many areas with lighter enforcement
   - BMAD: Deep native support for workflow-driven planning and execution
   - Ralph: Deep native support for fresh-context iteration and verification loops

7. **No framework scores on "Tech stack dependency"** (informational row, not a capability).


---

## Deep comparison (dimensions)

### 1) “Center of gravity”
- **Cypilot**: Design hierarchy + traceability (prd → architecture → feature decomposition → features manifest → feature designs → code).
- **OpenSpec**: Change proposal + delta spec + archiving into living specs.
- **Spec Kit**: Spec-driven pipeline with a constitution + artifacts generated via slash commands (constitution → spec → plan → tasks → implement).
- **MCAF**: Predictability via shared repo context + tests/analyzers as gates + explicit agent instructions.
- **BMAD**: Workflow-driven agile planning + story-centric execution across phases (analysis → planning → solutioning → implementation).
- **Ralph**: Fresh-context iteration loops with verification/backpressure (repeat until objective completion criteria pass).

### 2) Artifact model and where truth lives
- **Cypilot**
  - Truth is captured in a layered architecture of Markdown artifacts.
  - Strong separation of concerns: PRD vs architecture vs feature designs vs implementation plans.
  - Living evolution: implementation planning and status live in feature artifacts and are updated iteratively during implementation.
- **OpenSpec**
  - Truth lives in `openspec/specs/`.
  - Proposals and deltas live in `openspec/changes/<change-id>/` and are later archived/merged into specs.
  - Living evolution: `archive` is the explicit mechanism for folding approved deltas back into the source-of-truth specs.
- **Spec Kit**
  - Truth is in generated spec/plan/task documents under a spec spec directory; the constitution constrains downstream work.
  - Living evolution: specs live in `specs/<nnn-spec>/...` and naturally evolve via a branch/PR lifecycle.
- **MCAF**
  - Truth is in the repository as a whole: code + docs + tests + instructions; tests/analyzers arbitrate correctness.
  - Living evolution: documentation is updated to reflect actual behavior; “truth” is proven by tests and analyzers.
- **BMAD**
  - Truth is distributed across workflow outputs (planning docs + story tracking) that are regenerated/updated by running workflows.
  - Living evolution: outputs evolve via reruns; progress is tracked via story/sprint status artifacts.
- **Ralph**
  - Truth is “whatever passes verification”: the loop writes state to disk, runs gates (tests/build/typecheck), and continues until verified complete.
  - Living evolution: PRD/tasks/progress logs on disk are updated each iteration; git commits become durable memory.

### 3) Validation gates and failure modes
- **Cypilot**: Explicit validation chain per layer; dependent artifacts require validated parents.
- **OpenSpec**: Validate change folder (strict) and keep work proposal-first; archive after deployment.
- **Spec Kit**: Workflow emphasizes not moving to next phase until validated, but enforcement is primarily via process discipline + templates.
- **MCAF**: Spec docs and ADR are updated when needed; failing tests (including integration/API/UI) and analyzers block completion.
- **BMAD**: Workflow prerequisites and phase sequencing act as gates; Quick Flow emphasizes auto-validation of readiness; failures typically route back to earlier planning/workflow steps.
- **Ralph**: Gates are the loop stop condition: if tests/typecheck/build fail (or `verifyCompletion` returns false), the loop continues.

### 3.5) Types of determinism (what is “validated”)
- **Cypilot**: Deterministic validators for doc/schema, cross-artifact references, and code traceability via `@cpt-*` markers.
- **OpenSpec**: Deterministic validator for change folder structure and spec/delta format; `archive` is the gate back into living specs.
- **Spec Kit**: Deterministic setup tooling plus template constraints; validation is primarily agent/human-driven (analysis/checklists) rather than a strict spec validator.
- **MCAF**: Deterministic executable gates (tests + static analysis) are the decision makers.
- **BMAD**: Determinism is primarily workflow-structure-driven (progressive disclosure, step sequencing, continuable workflows, tri-modal create/validate/edit) rather than a strict deterministic validator across a layered doc stack.
- **Ralph**: Determinism is primarily executable-gate-driven (tests/build/typecheck) with a fresh-context loop and explicit completion verification functions.

### 4) Traceability
- **Cypilot**: First-class traceability from design IDs to code via tags and validation tooling, down to instruction-level granularity.
- **OpenSpec**: Traceability is “change-centric”: proposals/tasks/deltas are co-located per change.
- **Spec Kit**: Traceability is “spec pipeline-centric”: spec → plan → tasks → implement.
- **MCAF**: Traceability is “repo-centric”: docs link to tests and code; instructions standardize commands and workflow.
- **BMAD**: Traceability is “story-centric”: planning artifacts decompose into epics/stories which drive implementation.
- **Ralph**: Traceability is “verification-centric”: tasks map to commits and passing checks; progress is recorded on disk and reflected in git history.

### 5) Best-fit use cases
- **Cypilot** fits best when you need:
  - Business-reviewable behavior specs (plain English), strong layered documentation, and design→code traceability.
  - Multi-spec systems where cross-spec consistency matters.
- **OpenSpec** fits best when you need:
  - Clear audit trail of changes, explicit deltas, and a workflow optimized for evolving existing behavior across multiple specs.
- **Spec Kit** fits best when you want:
  - A bootstrap template + a guided pipeline that turns “what/why” into plan and tasks and then drives implementation.
- **MCAF** fits best when you need:
  - Strong engineering hygiene: verification gates, disciplined AGENTS.md governance, and repo-local “single shared context.”
- **BMAD** fits best when you want:
  - A guided end-to-end agile workflow that produces planning artifacts (PRD, architecture, epics/stories) and supports story-based implementation loops.
- **Ralph** fits best when you want:
  - An autonomy “engine” that iterates until verified complete, especially in repos where tests/typecheck/build are reliable signals.

### 6) Artifact strictness and integrity controls
- **Cypilot**: Treats artifacts as a schema-driven system: each artifact has a required structure (section order/naming), strict ID formats, payload blocks, and cross-artifact reference rules; validation is designed to detect missing sections, broken links, placeholder content, invalid IDs, and cross-layer inconsistencies.
- **OpenSpec**: Strictness is concentrated in the change proposal: you get a prescribed change folder layout and delta spec conventions with validation on the proposal itself; it is less focused on global cross-artifact integrity across a layered documentation stack.
- **Spec Kit**: Strictness is primarily constitutional/template-driven (process discipline), not enforced by a dedicated deterministic validator across documents.
- **MCAF**: Strictness is enforced via repository gates (tests/analyzers) and governance (instructions), rather than a required schema for architecture/spec artifacts.
- **BMAD**: Strictness is enforced through workflow standards for planning artifacts and step-by-step execution patterns (including create/validate/edit modes), but it is less focused on deterministic cross-artifact integrity checks across a layered doc stack.
- **Ralph**: Strictness is enforced through passing gates and small tasks; document structure and artifact schemas are repo-dependent.

### 7) Where Cypilot is unusually strong
- Layered artifacts are backed by explicit structure requirements and an execution protocol (workflows and requirements are first-class).
- Workflows themselves are structured specs (prerequisites, ordered steps, validation criteria/checklists), which reduces ambiguity for AI agents.
- Deterministic tooling is not only format checking: it includes cascading dependency validation and cross-artifact integrity checks.
- Traceability is explicit and can be made instruction-level (phases + instruction IDs), enabling design→code auditability.
- Scoring/threshold gates encourage consistent quality and make “done” more objective.

---

## Practical interoperability patterns

### Pattern A: Cypilot + OpenSpec (layered design + delta change tracking)
- Use **Cypilot** for layered artifacts and feature decomposition.
- Use **OpenSpec** for change proposals/deltas when you need an external-facing audit trail, or when multiple specs must be patched in a controlled way.

### Pattern B: Spec Kit for bootstrap, then migrate to Cypilot-style layering
- Use Spec Kit templates and constitution to generate initial spec/plan/tasks.
- When the system grows, adopt a layered approach (e.g., separate PRD, global design, and per-spec designs).

### Pattern C: MCAF verification doctrine applied to any of the above
- Regardless of spec system, apply MCAF’s “tests + analyzers are decision makers” and strict instructions governance.

### Pattern D: BMAD for planning and artifact generation, then Cypilot/OpenSpec for long-lived specs
- Use **BMAD** to generate planning artifacts and maintain story-level execution flow.
- Use **Cypilot** (layered design + deterministic validation) and/or **OpenSpec** (delta change proposals) when you need long-lived, auditable specs with stronger format/validator guarantees.

### Pattern E: Ralph as an implementation loop for any methodology
- Use **Ralph** to execute small, verifiable work units in a loop until tests/typecheck/build pass.
- Pair with **Cypilot/OpenSpec/Spec Kit/BMAD** for planning/spec artifacts; treat Ralph as the “executor.”

---

## Primary sources consulted

### Cypilot
- `README.md`, `{cypilot_path}/.core/skills/cypilot/README.md`, `{cypilot_path}/.core/kits/sdlc/guides/QUICKSTART.md`
- Cypilot workflow execution requirements and protocols in `requirements/` and `workflows/`

### OpenSpec
- https://github.com/Fission-AI/OpenSpec
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/README.md
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/opsx.md
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/commands.md
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/workflows.md
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/cli.md
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

### BMAD
- https://github.com/bmad-code-org/BMAD-METHOD
- https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/README.md
- https://docs.bmad-method.org/llms-full.txt

### Ralph
- https://github.com/vercel-labs/ralph-loop-agent
- https://raw.githubusercontent.com/vercel-labs/ralph-loop-agent/main/README.md
- https://raw.githubusercontent.com/vercel-labs/ralph-loop-agent/main/packages/ralph-loop-agent/README.md
- https://github.com/mikeyobrien/ralph-orchestrator
- https://raw.githubusercontent.com/mikeyobrien/ralph-orchestrator/main/README.md
- https://raw.githubusercontent.com/mikeyobrien/ralph-orchestrator/main/AGENTS.md
- https://github.com/snarktank/ralph
- https://raw.githubusercontent.com/snarktank/ralph/main/README.md
