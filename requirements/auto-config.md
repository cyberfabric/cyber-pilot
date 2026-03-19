---
cypilot: true
type: requirement
name: Auto-Configuration Methodology
version: 1.0
purpose: Systematic methodology for scanning brownfield projects and generating project-specific agent rules
---

# Auto-Configuration Methodology
 

<!-- toc -->

- [Phase 1.5: Documentation Discovery](#phase-15-documentation-discovery)
- [Phase 2: System Detection](#phase-2-system-detection)
- [Phase 3: Rule Generation](#phase-3-rule-generation)
- [Phase 4: AGENTS.md Integration](#phase-4-agentsmd-integration)
- [Phase 5: Registry Update](#phase-5-registry-update)
- [Phase 6: Validation](#phase-6-validation)
- [Output Specification](#output-specification)
- [Rule File Format](#rule-file-format)
- [WHEN Rule Patterns](#when-rule-patterns)
- [Error Handling](#error-handling)
- [References](#references)

<!-- /toc -->

 **Scope**: Brownfield projects where Cypilot is installed but no project-specific rules or specs exist yet.
 
 **Out of scope**: Greenfield projects with no code to scan, and projects that already have configured specs/rules.
 
 ## Agent Instructions
 
 **ALWAYS open and follow** this file WHEN the user asks to configure Cypilot for a project or an auto-config workflow is triggered.
 
 **ALWAYS open and follow** `{cypilot_path}/.core/requirements/reverse-engineering.md` for scan methodology (`L1-L3`, `L8`).
 
 **ALWAYS open and follow** `{cypilot_path}/.core/requirements/prompt-engineering.md` for rule-quality validation.
 
 **Prerequisites**: confirm the agent has read this methodology, has source access, will follow phases `1 -> 6` in order, will checkpoint after each phase, and will **NOT** write files without user confirmation.
 
 ## Overview
 
 Auto-config scans a brownfield project and generates **per-topic** rule files in `{cypilot_path}/config/rules/` plus contextual `WHEN` rules in `{cypilot_path}/config/AGENTS.md`. Files are split by **topic** (`conventions`, `architecture`, `patterns`, etc.), not by system path, so the agent loads only the guidance relevant to the current activity.
 
 **Core principle**: extract conventions from code, do not impose them.
 
 | Output | Location | Purpose |
 |---|---|---|
 | Per-topic rule files | `{cypilot_path}/config/rules/{topic}.md` | Focused rules per semantic topic |
 | Doc navigation rules | `{cypilot_path}/config/AGENTS.md` | `WHEN` rules for existing project docs with heading anchors |
 | Rule-file navigation rules | `{cypilot_path}/config/AGENTS.md` | `WHEN` rules that load generated topic files contextually |
 | Registry entries | `{cypilot_path}/config/artifacts.toml` | Detected systems with source paths |
 | TOC updates | Existing docs + generated rule files | Navigability for docs and rules |
 
 **Upstream methodologies used**:
 - **Reverse Engineering** (`L1-L3`, `L8`): surface scan, entry points, structure, pattern recognition
 - **Prompt Engineering** (`L2`, `L5`, `L6`): clarity, anti-pattern prevention, context efficiency
 
 ## Preconditions
 
 **Trigger conditions** (`ANY`):
 - Automatic brownfield detection with no project specs in config (`cypilot.py info` reports `specs: []` or no specs dir, and source-code directories exist)
 - Manual invocation via `cypilot auto-config` or equivalent user request
 - Rescan via `cpt init --rescan` or equivalent reconfigure request
 
 **Pre-checks**:
 - [ ] Cypilot is initialized (`cypilot.py info` returns `FOUND`)
 - [ ] Source-code repository is accessible
 - [ ] `{cypilot_path}/config/` exists and is writable
 - [ ] `{cypilot_path}/config/rules/` is empty, or `--force` is explicitly in use

 ## Phase 1: Project Scan
 
 **Goal**: extract raw project data using reverse-engineering methodology.
 
 **Use**: `{cypilot_path}/.core/requirements/reverse-engineering.md` Layers `1`, `2`, `3`, and `8`.
 
 | Subphase | Focus | Capture |
 |---|---|---|
 | `1.1` Surface Reconnaissance | Repository structure scan (`1.1.1-1.1.3`), language detection (`1.2.1-1.2.2`), documentation inventory (`1.3.1-1.3.2`) | `project_surface` — structure, languages, docs, git patterns |
 | `1.2` Entry Point Analysis | Application entry points (`2.1.1-2.1.2`), request entry points (`2.2.1-2.2.3`), bootstrap sequence (`2.3.1`) | `entry_points` — main files, HTTP routes, CLI commands, workers |
 | `1.3` Structural Decomposition | Architecture pattern (`3.1.1`), module/package boundaries (`3.1.2`), organization patterns (`3.2.1-3.2.2`), component inventory (`3.3.1-3.3.2`) | `structure` — architecture style, modules, boundaries, components |
 | `1.4` Pattern Recognition | Code patterns (`8.1.1-8.1.3`), project conventions (`8.2.1-8.2.3`), testing conventions (`8.3.1-8.3.2`) | `conventions` — naming, style, error handling, testing patterns |
 
 **Scan checkpoint**: after `1.1-1.4`, present and confirm:
 
 ```markdown
 ### Auto-Config Scan Summary
 
 **Project**: {name}
 **Languages**: {primary}, {secondary}
 **Architecture**: {pattern}
 **Entry points**: {count} ({types})
 **Modules**: {count} ({list})
 **Key conventions**:
 - Naming: {convention}
 - Error handling: {pattern}
 - Testing: {pattern}
 - File organization: {pattern}
 
 **Systems detected**: {count}
 ```

## Phase 1.5: Documentation Discovery

**Goal**: find project docs/specs, add TOCs where missing, and create heading-level navigation rules.

**Scan + capture**:
- [ ] Search `docs/`, `documentation/`, `guides/`, `wiki/`, `.github/`, standalone guides, ADR dirs, API docs, `README.md` links, `architecture/`, and `{cypilot_path}/config/`
- [ ] Build `docs_inventory` with `path`, title from first `H1`, TOC present, heading count, estimated topic/scope
- [ ] For each doc, parse `H1-H4`, identify scope/topic, classify as `Guide` / `Reference` / `Standard` / `Decision`, define `WHEN`, and identify the most useful headings

**TOC flow**: offer `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py toc {doc_path}`; show missing-TOC docs as `# | File | Headings | Topic`; on approval, run `cypilot toc` per selected doc and verify success.

**Documentation map output**:

```markdown
### Project Documentation Found
| # | File | Type | Has TOC | Key Sections | WHEN Condition |
|---|---|---|---|---|---|
| 1 | `docs/architecture.md` | Reference | ✓ | System Overview, Components, Data Flow | writing architecture code |
| 2 | `CONTRIBUTING.md` | Guide | ✓ (generated) | Setup, Code Style, PR Process | contributing or submitting PRs |
| 3 | `docs/api/endpoints.md` | Reference | ✓ | Auth, Users, Billing | writing API endpoints |

### Proposed Navigation Rules
ALWAYS open and follow `docs/architecture.md#system-overview` WHEN modifying system architecture or adding new components
ALWAYS open and follow `CONTRIBUTING.md#code-style` WHEN writing any code
ALWAYS open and follow `docs/api/endpoints.md#authentication` WHEN writing authentication code
```

Present this to the user for confirmation.

## Phase 2: System Detection

**Goal**: identify logical systems, subsystems, and semantic rule topics.

**System detection**: classify as `Monolith`, `Monorepo`, `Microservices`, or `Library`; record `Name`, `Slug`, `Root path`, `Language`, `Type`, inter-system `Dependencies`; identify domain, infrastructure, and shared modules.

**System map checkpoint**:

```markdown
### Detected Systems
| # | Name | Slug | Root | Language | Type |
|---|---|---|---|---|---|
| 1 | {name} | {slug} | {path} | {lang} | {type} |

### Subsystems
**{system-name}**:
- {subsystem}: {path} — {description}
```

Present for confirmation and naming adjustments.

**Topic detection**: topics are semantic, not structural.

| Topic | Typical `WHEN` | Focus |
|---|---|---|
| `conventions` | writing or reviewing code | Naming, code style, imports, file organization |
| `architecture` | modifying architecture, adding components, or refactoring module boundaries | System design, boundaries, data flow, abstractions |
| `patterns` | implementing features or writing business logic | Error handling, data access, state management, DI, idioms |
| `testing` | writing or running tests | Structure, naming, bootstrap helpers, fixtures, coverage |
| `api-contracts` | writing API endpoints or CLI commands | Request/response shape, error codes, output contracts, versioning |
| `infrastructure` | building, deploying, or configuring CI/CD | Build, dependencies, environment, release process |
| `security` | writing security-sensitive code or handling user input | Auth, secrets, sanitization, permission checks |
| `anti-patterns` | reviewing code or refactoring | Project-specific prohibitions with rationale |

**Topic selection rules**: [ ] only if `>= 3` project-specific rules [ ] complement existing `config/specs/` rather than duplicate [ ] merge topics with `<3` rules [ ] split topics `>120` lines [ ] custom topics allowed.

**Topic map checkpoint**:

```markdown
### Proposed Rule Files
| # | Topic | File | Rules | WHEN condition |
|---|---|---|---|---|
| 1 | Conventions | `rules/conventions.md` | ~{n} rules | writing or reviewing code |
| 2 | Architecture | `rules/architecture.md` | ~{n} rules | modifying architecture or module boundaries |
| 3 | Patterns | `rules/patterns.md` | ~{n} rules | implementing features |
→ Confirm topic split before generating? [yes / adjust]
```

Present this to the user before Phase `3`.

## Phase 3: Rule Generation

**Goal**: generate project-specific rule files from scan data.

**Quality gate**: apply `{cypilot_path}/.core/requirements/prompt-engineering.md` Layer `2` and Layer `5` to every generated rule.

**Base rule-file template**:

```markdown
---
cypilot: true
type: project-rule
topic: {topic-slug}
generated-by: auto-config
version: 1.0
---
# {Topic Title}
{One-paragraph scope statement}
## {Rule Group}
### {Rule Name}
{Imperative rule statement}
Evidence: `{file}:{line}` — {what was observed}
```

**Topic structure guidance**: `conventions.md` → Naming / Imports / File Organization / Code Style; `architecture.md` → Package Design / Module Boundaries / Communication Patterns / Key Abstractions + `Source Layout`; `patterns.md` → Error Handling / Data Access / State Management; `testing.md` → Structure / Naming / Fixtures / Coverage + bootstrap helpers; `api-contracts.md` → Output Format / Error Codes / Exit Codes / Versioning; `anti-patterns.md` → flat list of anti-pattern / why / safer alternative.

**Required checks**: [ ] focused [ ] has TOC [ ] specific [ ] observable [ ] grounded [ ] actionable [ ] `<120` lines [ ] no hallucination [ ] no overlap. One topic file, usually `architecture.md`, **MUST** include a `Critical Files` table.

**Generation protocol**: 1) filter by topic 2) merge/skip if `<3` rules 3) synthesize 4) validate against `AP-VAGUE`, `AP-CONTEXT-BLOAT`, `AP-HALLUCINATION-PRONE` 5) present batch to user 6) write after confirmation 7) run `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py toc {rule_file_path}`.

## Phase 4: AGENTS.md Integration

**Goal**: generate `WHEN` rules for topic files and existing project docs.

**Principle**: one topic file normally gets one whole-file `WHEN` rule; split by heading only if the file exceeds about `120` lines.

**Generated topic rules**:

```markdown
ALWAYS open and follow `{cypilot_path}/config/rules/conventions.md` WHEN writing or reviewing code
ALWAYS open and follow `{cypilot_path}/config/rules/architecture.md` WHEN modifying architecture, adding components, or refactoring module boundaries
ALWAYS open and follow `{cypilot_path}/config/rules/patterns.md` WHEN implementing features or writing business logic
ALWAYS open and follow `{cypilot_path}/config/rules/testing.md` WHEN writing or running tests
ALWAYS open and follow `{cypilot_path}/config/rules/api-contracts.md` WHEN writing API endpoints or CLI commands
ALWAYS open and follow `{cypilot_path}/config/rules/anti-patterns.md` WHEN reviewing code or refactoring
```

**Project-doc rules**: point to actionable headings such as `#code-style`, `#pr-process`, `#deployment`, and `#authentication`.

**Checks**: [ ] most specific actionable heading [ ] skip purely informational headings [ ] group related rules [ ] activity-based conditions, not location-based; multi-system example `WHEN implementing features in the auth service`; single-system example `WHEN implementing features or writing business logic`.

**AGENTS.md update** (preserve all existing user-written content):

```markdown
## Project Documentation (auto-configured)
<!-- auto-config:docs:start -->
{WHEN rules for existing project docs, with heading anchors}
<!-- auto-config:docs:end -->
## Project Rules (auto-configured)
<!-- auto-config:rules:start -->
{WHEN rules for generated rule files, with heading anchors if needed}
<!-- auto-config:rules:end -->
```

## Phase 5: Registry Update

**Goal**: register detected systems in `{cypilot_path}/config/artifacts.toml`.

```toml
[[systems]]
name = "{System Name}"
slug = "{slug}"
kits = "cypilot-sdlc"
source_paths = ["{path1}", "{path2}"]
[[systems.artifacts]]
path = "{source-root}"
kind = "CODEBASE"
```

**Registry validation**: [ ] unique slugs [ ] existing/readable source paths [ ] no duplicates [ ] valid TOML.

## Phase 6: Validation

**Goal**: verify auto-config output is correct and useful.

**Validation**:
- Structural: [ ] all rule files exist [ ] all `WHEN` rules resolve [ ] registry entries point to existing directories [ ] TOML valid
- Quality + functional: [ ] Layer `2` → no ambiguity [ ] Layer `5` → no `AP-VAGUE`, `AP-CONTEXT-BLOAT`, `AP-HALLUCINATION-PRONE` [ ] Layer `6` → under `200` lines, efficient token use [ ] rules actionable and project-specific [ ] no generic boilerplate

**Validation report**:

```markdown
## Auto-Config Validation
**Systems detected**: {count}
**Topic files generated**: {count} ({list of topic slugs})
**WHEN rules added**: {count} (topic rules + doc rules)
**Registry entries added**: {count}
- Topic file quality: {PASS|WARN} (focused, <120 lines, no overlap)
- WHEN rule validity: {PASS|FAIL}
- Registry validity: {PASS|FAIL}
- {path}: {status}
```

## Output Specification

**Directory structure**:

```text
{cypilot_path}/config/
├── AGENTS.md
├── artifacts.toml
└── rules/ (`conventions.md`, `architecture.md`, `patterns.md`, `testing.md`, `api-contracts.md`, `anti-patterns.md`)
```

Generate only topic files with at least `3` project-specific rules. Existing project docs stay preserved; only TOCs may be added where missing.

**Scripted JSON output**:

```json
{"status":"PASS","systems_detected":2,"topics_generated":["conventions","architecture","patterns","testing"],"agents_rules_added":4,"registry_entries_added":2,"files_written":["{cypilot_path}/config/rules/conventions.md","{cypilot_path}/config/rules/architecture.md","{cypilot_path}/config/rules/patterns.md","{cypilot_path}/config/rules/testing.md"],"docs_found":3,"docs_toc_generated":2,"doc_navigation_rules_added":5}
```

## Rule File Format

**Frontmatter**:

```yaml
---
cypilot: true
type: project-rule
topic: {topic-slug}
generated-by: auto-config
version: 1.0
---
```

**TOC requirements**:
- [ ] Immediately after frontmatter and `H1`
- [ ] Covers `H2`/`H3` with GitHub-style anchors
- [ ] Validate with `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py toc {rule_file_path}`

**Content guidelines**:
- [ ] Max `120` lines; imperative mood; specific file refs
- [ ] Evidence-based; no language-default boilerplate; no cross-topic content

## WHEN Rule Patterns

**Valid activity-based conditions**:

```text
WHEN writing or reviewing code
WHEN modifying architecture, adding components, or refactoring module boundaries
WHEN implementing features or writing business logic
WHEN writing or running tests
WHEN writing API endpoints or CLI commands
WHEN reviewing code or refactoring
WHEN building, deploying, or configuring CI/CD
WHEN writing security-sensitive code or handling user input
WHEN writing or reviewing code in the {system-name}
WHEN implementing features for {system-name}
WHEN {doc-specific-activity}
```

**WHEN-rule quality**: [ ] activity not location [ ] specific enough [ ] broad enough [ ] no overlap [ ] one rule per topic file unless `>120` lines [ ] heading anchors for project docs.

## Error Handling

| Condition | Response | Action |
|---|---|---|
| No source code found | `No source code detected in project` → use `cypilot generate` for greenfield work. | **STOP** |
| Existing rules found | `Existing rules found in {cypilot_path}/config/rules/` → list files → use `--force` or merge manually. | **STOP** unless `--force` |
| Scan incomplete | `Project scan incomplete: {reason}` → completed list → skipped list → rules generated from partial scan data. | **WARN** and continue |
| Large codebase | `Large codebase detected ({file_count} files)` → scan top-level structure only → offer `cypilot auto-config --system {slug}`. | Limit scan depth |

## References

- Reverse Engineering: `{cypilot_path}/.core/requirements/reverse-engineering.md`
- Prompt Engineering: `{cypilot_path}/.core/requirements/prompt-engineering.md`
- Execution Protocol: `{cypilot_path}/.core/requirements/execution-protocol.md`
- Generate Workflow: `{cypilot_path}/.core/workflows/generate.md` (triggers auto-config in Brownfield prerequisite)
