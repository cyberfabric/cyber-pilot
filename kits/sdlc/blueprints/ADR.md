# ADR Blueprint
<!-- 
  Blueprint for Architecture Decision Records (ADR).
  
  This file is the single source of truth for:
  - template.md generation (from @cpt:heading + @cpt:prompt markers)
  - example.md generation (from @cpt:heading examples + @cpt:example markers)
  - rules.md generation (from @cpt:rules + @cpt:rule markers)
  - checklist.md generation (from @cpt:checklist + @cpt:check markers)
  - constraints.toml contributions (from @cpt:heading + @cpt:id markers)
  
  All text between markers is ignored by the generator — it serves as
  human-readable documentation for anyone editing this blueprint.
  
  Based on: Michael Nygard's ADR template (2011), ISO/IEC/IEEE 42010:2022
-->

## Metadata

`@cpt:blueprint`
```toml
version = 1
kit = "sdlc"
artifact = "ADR"
codebase = false
template_frontmatter = """
status: accepted
date: {YYYY-MM-DD}
decision-makers: {optionally fill decision makers names, accounts or remove that field}"""
example_frontmatter = """
status: accepted
date: 2026-02-16"""
```
`@/cpt:blueprint`

## Skill Integration

Commands and workflows exposed to AI agents for ADR operations.

`@cpt:skill`
```markdown
### ADR Commands
- `cypilot validate --artifact <ADR.md>` — validate ADR structure and IDs
- `cypilot list-ids --kind adr` — list all ADRs
- `cypilot where-defined <id>` — find where an ADR ID is defined
- `cypilot where-used <id>` — find where an ADR ID is referenced in DESIGN
### ADR Workflows
- **Generate ADR**: create a new ADR from template with guided prompts per section
- **Analyze ADR**: validate structure (deterministic) then semantic quality (checklist-based)
```
`@/cpt:skill`

---

## Rules Definition

Rules are organized into sections that map to the generated `rules.md`.
The `@cpt:rules` skeleton defines the section structure; individual `@cpt:rule`
markers provide the content for each section.

### Rules Skeleton

`@cpt:rules`
```toml
[prerequisites]
sections = ["load_dependencies"]

[requirements]
sections = ["structural", "versioning", "semantic", "scope", "status_traceability", "constraints", "deliberate_omissions", "writing_quality"]
[requirements.names]
deliberate_omissions = "Deliberate Omissions (MUST NOT HAVE)"
writing_quality = "ADR Writing Quality"

[tasks]
phases = ["setup", "content_creation", "ids_and_structure", "quality_check"]
[tasks.names]
ids_and_structure = "IDs and Structure"

[validation]
phases = ["structural", "semantic", "validation_report", "applicability", "review_scope", "report_format", "reporting", "pr_review"]
[validation.names]
structural = "Structural Validation (Deterministic)"
semantic = "Semantic Validation (Checklist-based)"
applicability = "Applicability Context"
review_scope = "Review Scope Selection"
report_format = "Report Format"
reporting = "Reporting Commitment"
pr_review = "PR Review Focus (ADR)"

[error_handling]
sections = ["number_conflict", "missing_directory", "escalation"]

[next_steps]
sections = ["options"]
```
`@/cpt:rules`

### Prerequisites

Dependencies that must be loaded before working with an ADR artifact.

`@cpt:rule`
```toml
kind = "prerequisites"
section = "load_dependencies"
```
```markdown
- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read `{cypilot_path}/config/artifacts.toml` to determine ADR directory
- [ ] Load `{cypilot_path}/.core/architecture/specs/traceability.md` for ID formats
- [ ] Load `{cypilot_path}/config/kits/sdlc/constraints.toml` for kit-level constraints
- [ ] Load `{cypilot_path}/.core/architecture/specs/kit/constraints.md` for constraints specification
```
`@/cpt:rule`

### Requirements

Structural and semantic rules that every ADR must satisfy.

#### Structural Requirements

`@cpt:rule`
```toml
kind = "requirements"
section = "structural"
```
```markdown
- [ ] ADR follows `template.md` structure
- [ ] Artifact frontmatter is required
- [ ] ADR has unique ID: `cpt-{hierarchy-prefix}-adr-{slug}` (e.g., `cpt-myapp-adr-use-postgresql`)
- [ ] ID has priority marker (`p1`-`p9`)
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs
```
`@/cpt:rule`

#### Versioning Rules

ADR immutability and supersession policy.

`@cpt:rule`
```toml
kind = "requirements"
section = "versioning"
```
```markdown
- [ ] ADR version in filename: `NNNN-{slug}-v{N}.md`
- [ ] When PROPOSED: minor edits allowed without version change
- [ ] When ACCEPTED: **immutable** — do NOT edit decision/rationale
- [ ] To change accepted decision: create NEW ADR with SUPERSEDES reference
- [ ] Superseding ADR: `cpt-{hierarchy-prefix}-adr-{new-slug}` with status SUPERSEDED on original
```
`@/cpt:rule`

#### Semantic Quality

Content quality standards for ADR sections.

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
**Reference**: `checklist.md` for detailed criteria

- [ ] Problem/context clearly stated
- [ ] At least 2-3 options considered
- [ ] Decision rationale explained
- [ ] Consequences documented (pros and cons)
- [ ] Valid status (PROPOSED, ACCEPTED, REJECTED, DEPRECATED, SUPERSEDED)
```
`@/cpt:rule`

#### Decision Scope

Guidelines for what constitutes an ADR-worthy decision.

`@cpt:rule`
```toml
kind = "requirements"
section = "scope"
```
```markdown
**One ADR per decision**. Avoid bundling multiple decisions.

| Scope | Examples | Guideline |
|-------|----------|-----------|
| **Too broad** | "Use microservices and React and PostgreSQL" | Split into separate ADRs |
| **Right size** | "Use PostgreSQL for persistent storage" | Single architectural choice |
| **Too narrow** | "Use VARCHAR(255) for email field" | Implementation detail, not ADR-worthy |

**ADR-worthy decisions**:
- Technology choices (languages, frameworks, databases)
- Architectural patterns (monolith vs microservices, event-driven)
- Integration approaches (REST vs GraphQL, sync vs async)
- Security strategies (auth mechanisms, encryption approaches)
- Infrastructure decisions (cloud provider, deployment model)

**NOT ADR-worthy** (handle in code/design docs):
- Variable naming conventions
- File organization within modules
- Specific library versions (unless security-critical)
- UI component styling choices
```
`@/cpt:rule`

#### Status & Traceability

Valid statuses and transition rules for ADR lifecycle.

`@cpt:rule`
```toml
kind = "requirements"
section = "status_traceability"
```
```markdown
**Valid Statuses**: PROPOSED, ACCEPTED, REJECTED, DEPRECATED, SUPERSEDED

**Status Transitions**:

| From | To | Trigger | Action |
|------|-----|---------|--------|
| PROPOSED | ACCEPTED | Decision approved | Update status, begin implementation |
| PROPOSED | REJECTED | Decision declined | Update status, document rejection reason |
| ACCEPTED | DEPRECATED | Decision no longer applies | Update status, note why |
| ACCEPTED | SUPERSEDED | Replaced by new ADR | Update status, add `superseded_by` reference |

**Status Change Procedure**:

1. **Locate ADR file**: `architecture/ADR/NNNN-{slug}.md`
2. **Update frontmatter status**: Change `status: {OLD}` → `status: {NEW}`
3. **Add status history** (if present): Append `{date}: {OLD} → {NEW} ({reason})`
4. **For SUPERSEDED**: Add `superseded_by: cpt-{hierarchy-prefix}-adr-{new-slug}`
5. **For REJECTED**: Add `rejection_reason: {brief explanation}`

**REJECTED Status**:

Use when:
- Decision was reviewed but not approved
- Alternative approach was chosen (document which)
- Requirements changed before acceptance

Keep REJECTED ADRs for historical record — do not delete.
```
`@/cpt:rule`

#### Constraints Integration

How ADR relates to kit-level constraints validation.

`@cpt:rule`
```toml
kind = "requirements"
section = "constraints"
```
```markdown
- [ ] ALWAYS open and follow `{cypilot_path}/config/kits/sdlc/constraints.toml` (kit root)
- [ ] Treat `constraints.toml` as primary validator for:
  - where IDs are defined
  - where IDs are referenced
  - which cross-artifact references are required / optional / prohibited

**References**:
- `{cypilot_path}/.core/requirements/kit-constraints.md`
- `{cypilot_path}/.core/schemas/kit-constraints.schema.json`

**Validation Checks**:
- `cypilot validate` enforces `identifiers[<kind>].references` rules for ADR coverage in DESIGN
```
`@/cpt:rule`

#### Deliberate Omissions (MUST NOT HAVE)

`@cpt:rule`
```toml
kind = "requirements"
section = "deliberate_omissions"
```
```markdown
ADRs must NOT contain the following — report as violation if found:

- **ARCH-ADR-NO-001**: No Complete Architecture Description (CRITICAL) — ADR is a decision record, not an architecture document
- **ARCH-ADR-NO-002**: No Spec Implementation Details (HIGH) — ADR captures *why*, not *how* to implement
- **BIZ-ADR-NO-001**: No Product Requirements (HIGH) — requirements belong in PRD
- **BIZ-ADR-NO-002**: No Implementation Tasks (HIGH) — tasks belong in DECOMPOSITION/FEATURE
- **DATA-ADR-NO-001**: No Complete Schema Definitions (MEDIUM) — schemas belong in DESIGN
- **MAINT-ADR-NO-001**: No Code Implementation (HIGH) — code belongs in implementation
- **SEC-ADR-NO-001**: No Security Secrets (CRITICAL) — secrets must never appear in documentation
- **TEST-ADR-NO-001**: No Test Implementation (MEDIUM) — tests belong in code
- **OPS-ADR-NO-001**: No Operational Procedures (MEDIUM) — procedures belong in runbooks
- **ARCH-ADR-NO-003**: No Trivial Decisions (MEDIUM) — ADRs are for significant decisions only
- **ARCH-ADR-NO-004**: No Incomplete Decisions (HIGH) — ADR must have a clear decision, not "TBD"
```
`@/cpt:rule`

#### ADR Writing Quality

`@cpt:rule`
```toml
kind = "requirements"
section = "writing_quality"
```
```markdown
**Standards**: Michael Nygard ADR Template — writing style guidance

**QUALITY-001: Neutrality** (MEDIUM)
- [ ] Options described neutrally (no leading language)
- [ ] Pros and cons balanced for all options
- [ ] No strawman arguments
- [ ] Honest about chosen option's weaknesses

**QUALITY-002: Clarity** (HIGH) — Ref: ISO 29148 §5.2.5, IEEE 1016 §4.2
- [ ] Decision can be understood without insider knowledge
- [ ] Acronyms expanded on first use
- [ ] Technical terms defined if unusual
- [ ] No ambiguous language

**QUALITY-003: Actionability** (HIGH) — Ref: Michael Nygard "Decision" section
- [ ] Clear what action to take based on decision
- [ ] Implementation guidance provided
- [ ] Scope of application clear
- [ ] Exceptions documented

**QUALITY-004: Reviewability** (MEDIUM) — Ref: ISO 42010 §6.7
- [ ] Can be reviewed in a reasonable time
- [ ] Evidence and references provided
- [ ] Assumptions verifiable
- [ ] Consequences measurable
```
`@/cpt:rule`

### Task Phases

Step-by-step workflow for creating an ADR.

#### Setup

`@cpt:rule`
```toml
kind = "tasks"
section = "setup"
```
```markdown
- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read `{cypilot_path}/config/artifacts.toml` to determine ADR directory
- [ ] Determine next ADR number (ADR-NNNN)

**ADR path resolution**:
1. List existing ADRs from `artifacts` array where `kind: "ADR"`
2. For new ADR, derive default path:
   - Read system's `artifacts_dir` from `artifacts.toml` (default: `architecture`)
   - Use kit's default subdirectory for ADRs: `ADR/`
   - Create at: `{artifacts_dir}/ADR/{NNNN}-{slug}.md`
3. Register new ADR in `artifacts.toml` with FULL path

**ADR Number Assignment**:

1. List existing ADRs from `artifacts` array where `kind: "ADR"`
2. Extract highest number: parse `NNNN` from filenames
3. Assign next sequential: `NNNN + 1`
```
`@/cpt:rule`

#### Content Creation

How to use the example as a reference when writing each ADR section.

`@cpt:rule`
```toml
kind = "tasks"
section = "content_creation"
```
```markdown
**Use example as reference:**

| Section | Example Reference | Checklist Guidance |
|---------|-------------------|-------------------|
| Context | How example states problem | ADR-001: Context Clarity |
| Options | How example lists alternatives | ADR-002: Options Analysis |
| Decision | How example explains choice | ADR-003: Decision Rationale |
| Consequences | How example documents impact | ADR-004: Consequences |
```
`@/cpt:rule`

#### IDs & Structure

ID generation and structural verification.

`@cpt:rule`
```toml
kind = "tasks"
section = "ids_and_structure"
```
```markdown
- [ ] Generate ID: `cpt-{hierarchy-prefix}-adr-{slug}` (e.g., `cpt-myapp-adr-use-postgresql`)
- [ ] Assign priority based on impact
- [ ] Link to DESIGN if applicable
- [ ] Verify uniqueness with `cypilot list-ids`
```
`@/cpt:rule`

#### Quality Check

Final self-review before completion.

`@cpt:rule`
```toml
kind = "tasks"
section = "quality_check"
```
```markdown
- [ ] Compare to `examples/example.md`
- [ ] Self-review against `checklist.md`
- [ ] Verify rationale is complete

**ADR Immutability Rule**:
- After ACCEPTED: do not modify decision/rationale
- To change: create new ADR with SUPERSEDES reference
```
`@/cpt:rule`

### Error Handling

Recovery procedures for common ADR authoring issues.

#### Number Conflict

`@cpt:rule`
```toml
kind = "error_handling"
section = "number_conflict"
```
````markdown
**If number conflict detected** (file already exists):
```
⚠ ADR number conflict: {NNNN} already exists
→ Verify existing ADRs: ls architecture/ADR/
→ Assign next available number: {NNNN + 1}
→ If duplicate content: consider updating existing ADR instead
```
````
`@/cpt:rule`

#### Missing Directory

`@cpt:rule`
```toml
kind = "error_handling"
section = "missing_directory"
```
````markdown
**If ADR directory doesn't exist**:
```
⚠ ADR directory not found
→ Create: mkdir -p architecture/ADR
→ Start numbering at 0001
```
````
`@/cpt:rule`

#### Escalation

When to involve the user.

`@cpt:rule`
```toml
kind = "error_handling"
section = "escalation"
```
```markdown
- [ ] Ask user when decision significance is unclear
- [ ] Ask user when options require domain expertise to evaluate
- [ ] Ask user when compliance or security implications are uncertain
```
`@/cpt:rule`

### Validation

Post-creation validation steps.

#### Structural Validation

`@cpt:rule`
```toml
kind = "validation"
section = "structural"
```
```markdown
Run `cypilot validate` for:
- [ ] Template structure compliance
- [ ] ID format validation
- [ ] No placeholders
```
`@/cpt:rule`

#### Semantic Validation

`@cpt:rule`
```toml
kind = "validation"
section = "semantic"
```
```markdown
Apply `checklist.md`:
1. Verify context explains why decision needed
2. Verify options have pros/cons
3. Verify decision has clear rationale
4. Verify consequences documented
```
`@/cpt:rule`

#### Validation Report

`@cpt:rule`
```toml
kind = "validation"
section = "validation_report"
```
````markdown
```
ADR Validation Report
═════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```
````
`@/cpt:rule`

#### Applicability Context

`@cpt:rule`
```toml
kind = "validation"
section = "applicability"
```
```markdown
Before evaluating each checklist item, the expert MUST:

1. **Understand the artifact's domain** — What kind of system/project is this ADR for? (e.g., CLI tool, web service, data pipeline, methodology framework)

2. **Determine applicability for each requirement** — Not all checklist items apply to all ADRs:
   - A CLI tool ADR may not need Security Impact analysis
   - A methodology framework ADR may not need Performance Impact analysis
   - A local development tool ADR may not need Operational Readiness analysis

3. **Require explicit handling** — For each checklist item:
   - If applicable: The document MUST address it (present and complete)
   - If not applicable: The document MUST explicitly state "Not applicable because..." with reasoning
   - If missing without explanation: Report as violation

4. **Never skip silently** — The expert MUST NOT skip a requirement just because it's not mentioned. Either:
   - The requirement is met (document addresses it), OR
   - The requirement is explicitly marked not applicable (document explains why), OR
   - The requirement is violated (report it with applicability justification)

**Key principle**: The reviewer must be able to distinguish "author considered and excluded" from "author forgot"

For each major checklist category (ARCH, PERF, SEC, REL, DATA, INT, OPS, MAINT, TEST, COMPL, UX, BIZ), confirm:

- [ ] Category is addressed in the document, OR
- [ ] Category is explicitly marked "Not applicable" with reasoning in the document, OR
- [ ] Category absence is reported as a violation (with applicability justification)
```
`@/cpt:rule`

#### Review Scope Selection

`@cpt:rule`
```toml
kind = "validation"
section = "review_scope"
```
```markdown
Select review depth based on ADR complexity and impact:

| ADR Type | Review Mode | Domains to Check |
|----------|-------------|------------------|
| Simple (single component, low risk) | **Quick** | ARCH only |
| Standard (multi-component, moderate risk) | **Standard** | ARCH + relevant domains |
| Complex (architectural, high risk) | **Full** | All applicable domains |

**Quick Review (ARCH Only)** — For simple, low-risk decisions:
- ARCH-ADR-001 through ARCH-ADR-006, QUALITY-002, QUALITY-003
- Skip all domain-specific sections (PERF, SEC, REL, etc.)

**Standard Review** — Select domains by ADR subject:

| ADR Subject | Required Domains |
|-------------|------------------|
| Technology choice | ARCH, MAINT, OPS |
| Security mechanism | ARCH, SEC, COMPL |
| Database/storage | ARCH, DATA, PERF |
| API/integration | ARCH, INT, SEC |
| Infrastructure | ARCH, OPS, REL, PERF |
| User-facing spec | ARCH, UX, BIZ |

**Full Review** — All applicable domains.

**Domain Applicability Quick Reference**:

| Domain | When Required | When N/A |
|--------|--------------|----------|
| PERF | Performance-sensitive systems | Methodology, documentation |
| SEC | User data, network, auth | Local-only tools |
| REL | Production systems, SLAs | Dev tools, prototypes |
| DATA | Persistent storage, migrations | Stateless components |
| INT | External APIs, contracts | Self-contained systems |
| OPS | Deployed services | Libraries, frameworks |
| MAINT | Long-lived code | Throwaway prototypes |
| TEST | Quality-critical systems | Exploratory work |
| COMPL | Regulated industries | Internal tools |
| UX | End-user impact | Backend infrastructure |
```
`@/cpt:rule`

#### Report Format

`@cpt:rule`
```toml
kind = "validation"
section = "report_format"
```
````markdown
**Format Selection**:

| Review Mode | Report Format |
|-------------|---------------|
| Quick | Compact (table) |
| Standard | Compact or Full |
| Full | Full (detailed) |

**Compact Format** (for Quick/Standard reviews):

```markdown
## ADR Review: {title}
| # | ID | Sev | Issue | Fix |
|---|-----|-----|-------|-----|
| 1 | ARCH-002 | CRIT | Missing problem statement | Add 2+ sentences describing the problem |
| 2 | ARCH-003 | HIGH | Only 1 option listed | Add at least 1 viable alternative |
**Review mode**: Quick (ARCH core only)
**Domains checked**: ARCH
**Domains N/A**: PERF, SEC, REL, DATA, INT, OPS (methodology ADR)
```

**Full Format** — For each issue:
- **Why Applicable**: Explain why this requirement applies to this ADR's context
- **Checklist Item**: `{CHECKLIST-ID}` — {Checklist item title}
- **Severity**: CRITICAL|HIGH|MEDIUM|LOW
- **Issue**: What is wrong
- **Evidence**: Quote or "No mention found"
- **Why it matters**: Impact (risk, cost, user harm, compliance)
- **Proposal**: Concrete fix with clear acceptance criteria
````
`@/cpt:rule`

#### Reporting Commitment

`@cpt:rule`
```toml
kind = "validation"
section = "reporting"
```
```markdown
- [ ] I reported all issues I found
- [ ] I used the exact report format defined in this checklist (no deviations)
- [ ] I included Why Applicable justification for each issue
- [ ] I included evidence and impact for each issue
- [ ] I proposed concrete fixes for each issue
- [ ] I did not hide or omit known problems
- [ ] I verified explicit handling for all major checklist categories
- [ ] I am ready to iterate on the proposals and re-review after changes
```
`@/cpt:rule`

#### PR Review Focus (ADR)

`@cpt:rule`
```toml
kind = "validation"
section = "pr_review"
```
```markdown
When reviewing PRs that add or change Architecture Decision Records, additionally focus on:

- [ ] Ensure the problem is module/system scoped, not generic and repeatable
- [ ] Compliance with `template.md` structure (generated from blueprint)
- [ ] Ensure the problem is not already solved by other existing ADRs in the project ADR directory (see `{cypilot_path}/config/artifacts.toml` for path)
- [ ] Alternatives are genuinely different approaches (not straw men)
- [ ] Decision rationale is concrete and traceable to project constraints
```
`@/cpt:rule`

### Next Steps

Recommended actions after completing an ADR.

`@cpt:rule`
```toml
kind = "next_steps"
section = "options"
```
```markdown
| Condition | Suggested Next Step |
|-----------|---------------------|
| ADR PROPOSED | Share for review, then update status to ACCEPTED |
| ADR ACCEPTED | `/cypilot-generate DESIGN` — incorporate decision into design |
| Related ADR needed | `/cypilot-generate ADR` — create related decision record |
| ADR supersedes another | Update original ADR status to SUPERSEDED |
| Want checklist review only | `/cypilot-analyze semantic` — semantic validation (skip deterministic) |
```
`@/cpt:rule`

---

## Checklist Definition

The `@cpt:checklist` defines severity levels and review domains.
Each `@cpt:check` is an individual checklist item grouped by domain.

Domains are prioritized: ARCH → SEC → BIZ are reviewed first.
Check severity: CRITICAL items block acceptance; HIGH/MEDIUM/LOW are advisory.

### Checklist Skeleton

`@cpt:checklist`
```toml
[sections]
adr_specific_quality_checks = "ADR-Specific Quality Checks"

[severity]
levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

[review]
priority = ["ARCH", "PERF", "SEC", "REL", "DATA", "INT", "OPS", "MAINT", "TEST", "COMPL", "UX", "BIZ"]

[[domain]]
abbr = "ARCH"
name = "🏗️ ARCHITECTURE Expertise"
header = "🏗️ ARCHITECTURE Expertise (ARCH)"
standards_text = """**Standards**: Michael Nygard's ADR Template (2011), ISO/IEC/IEEE 42010:2022 §6.7"""

[[domain]]
abbr = "PERF"
name = "⚡ PERFORMANCE Expertise"
header = "⚡ PERFORMANCE Expertise (PERF)"
standards_text = """**Standards**: ISO/IEC 25010:2011 §4.2.2 (Performance Efficiency)"""

[[domain]]
abbr = "SEC"
name = "🔒 SECURITY Expertise"
header = "🔒 SECURITY Expertise (SEC)"
standards_text = """**Standards**: OWASP ASVS 5.0 V1.2 (Architecture), ISO/IEC 27001:2022 (ISMS)"""

[[domain]]
abbr = "REL"
name = "🛡️ RELIABILITY Expertise"
header = "🛡️ RELIABILITY Expertise (REL)"
standards_text = """**Standards**: ISO/IEC 25010:2011 §4.2.5 (Reliability)"""

[[domain]]
abbr = "DATA"
name = "📊 DATA Expertise"
header = "📊 DATA Expertise (DATA)"
standards_text = """**Standards**: IEEE 1016-2009 §5.6 (Information Viewpoint)"""

[[domain]]
abbr = "INT"
name = "🔌 INTEGRATION Expertise"
header = "🔌 INTEGRATION Expertise (INT)"
standards_text = """**Standards**: IEEE 1016-2009 §5.3 (Interface Viewpoint)"""

[[domain]]
abbr = "OPS"
name = "🖥️ OPERATIONS Expertise"
header = "🖥️ OPERATIONS Expertise (OPS)"
standards = []

[[domain]]
abbr = "MAINT"
name = "🔧 MAINTAINABILITY Expertise"
header = "🔧 MAINTAINABILITY Expertise (MAINT)"
standards_text = """**Standards**: ISO/IEC 25010:2011 §4.2.7 (Maintainability)"""

[[domain]]
abbr = "TEST"
name = "🧪 TESTING Expertise"
header = "🧪 TESTING Expertise (TEST)"
standards_text = """**Standards**: ISO/IEC/IEEE 29119-3:2021 (Test Documentation)"""

[[domain]]
abbr = "COMPL"
name = "📜 COMPLIANCE Expertise"
header = "📜 COMPLIANCE Expertise (COMPL)"
standards_text = """**Standards**: ISO/IEC 27001:2022 (ISMS), domain-specific regulations (GDPR, HIPAA, SOC 2)"""

[[domain]]
abbr = "UX"
name = "👤 USABILITY Expertise"
header = "👤 USABILITY Expertise (UX)"
standards = []

[[domain]]
abbr = "BIZ"
name = "🏢 BUSINESS Expertise"
header = "🏢 BUSINESS Expertise (BIZ)"
standards_text = """**Standards**: ISO/IEC/IEEE 29148:2018 §5.2 (Stakeholder requirements)"""

```
````markdown
# ADR (Architecture Decision Record) Expert Checklist

**Artifact**: Architecture Decision Record (ADR)
**Version**: 2.0
**Purpose**: Comprehensive quality checklist for ADR artifacts

---

## Referenced Standards

This checklist incorporates requirements and best practices from:

| Standard | Scope | Key Sections Used |
|----------|-------|-------------------|
| **Michael Nygard's ADR Template (2011)** | De facto standard for ADR format | Title, Status, Context, Decision, Consequences structure |
| **ISO/IEC/IEEE 42010:2022** | Architecture Description | §5.7 AD elements, §6.7 Architecture decisions and rationale |
| **ISO/IEC 25010:2011** | SQuaRE Software Quality Model | §4.2 Quality characteristics (performance, security, reliability, maintainability) |
| **ISO/IEC/IEEE 29148:2018** | Requirements Engineering | §6.5 Behavioral requirements, traceability |
| **OWASP ASVS 5.0** | Application Security Verification | V1.2 Architecture, V2 Authentication, V5 Validation |
| **ISO/IEC 27001:2022** | Information Security Management | Annex A controls, risk assessment |
| **ISO/IEC/IEEE 29119-3:2021** | Test Documentation | Test specification, acceptance criteria |
---

## Prerequisites

Before starting the review, confirm:

- [ ] I understand this checklist validates ADR artifacts
- [ ] I will follow the Applicability Context rules below
- [ ] I will check ALL items in MUST HAVE sections
- [ ] I will verify ALL items in MUST NOT HAVE sections
- [ ] I will document any violations found
- [ ] I will provide specific feedback for each failed check
- [ ] I will complete the Final Checklist and provide a review report

---

## Applicability Context

Before evaluating each checklist item, the expert MUST:

1. **Understand the artifact's domain** — What kind of system/project is this ADR for? (e.g., CLI tool, web service, data pipeline, methodology framework)

2. **Determine applicability for each requirement** — Not all checklist items apply to all ADRs:
   - A CLI tool ADR may not need Security Impact analysis
   - A methodology framework ADR may not need Performance Impact analysis
   - A local development tool ADR may not need Operational Readiness analysis

3. **Require explicit handling** — For each checklist item:
   - If applicable: The document MUST address it (present and complete)
   - If not applicable: The document MUST explicitly state "Not applicable because..." with reasoning
   - If missing without explanation: Report as violation

4. **Never skip silently** — The expert MUST NOT skip a requirement just because it's not mentioned. Either:
   - The requirement is met (document addresses it), OR
   - The requirement is explicitly marked not applicable (document explains why), OR
   - The requirement is violated (report it with applicability justification)

**Key principle**: The reviewer must be able to distinguish "author considered and excluded" from "author forgot"

---

## Severity Dictionary

- **CRITICAL**: Unsafe/misleading/unverifiable; blocks downstream work.
- **HIGH**: Major ambiguity/risk; should be fixed before approval.
- **MEDIUM**: Meaningful improvement; fix when feasible.
- **LOW**: Minor improvement; optional.

---

## Review Scope Selection

Select review depth based on ADR complexity and impact:

### Review Modes

| ADR Type | Review Mode | Domains to Check |
|----------|-------------|------------------|
| Simple (single component, low risk) | **Quick** | ARCH only |
| Standard (multi-component, moderate risk) | **Standard** | ARCH + relevant domains |
| Complex (architectural, high risk) | **Full** | All applicable domains |

### Quick Review (ARCH Only)

For simple, low-risk decisions, check only core architecture items:

**MUST CHECK**:
- [ ] ARCH-ADR-001: Decision Significance
- [ ] ARCH-ADR-002: Context Completeness
- [ ] ARCH-ADR-003: Options Quality
- [ ] ARCH-ADR-004: Decision Rationale
- [ ] ARCH-ADR-006: ADR Metadata Quality
- [ ] QUALITY-002: Clarity
- [ ] QUALITY-003: Actionability

**SKIP**: All domain-specific sections (PERF, SEC, REL, etc.)

Note: `Quick review: checked ARCH core items only`

### Standard Review (ARCH + Relevant Domains)

Select applicable domains based on ADR subject:

| ADR Subject | Required Domains |
|-------------|------------------|
| Technology choice | ARCH, MAINT, OPS |
| Security mechanism | ARCH, SEC, COMPL |
| Database/storage | ARCH, DATA, PERF |
| API/integration | ARCH, INT, SEC |
| Infrastructure | ARCH, OPS, REL, PERF |
| User-facing spec | ARCH, UX, BIZ |

### Full Review

For architectural decisions with broad impact, check ALL applicable domains.

### Domain Applicability Quick Reference

| Domain | When Required | When N/A |
|--------|--------------|----------|
| **PERF** | Performance-sensitive systems | Methodology, documentation |
| **SEC** | User data, network, auth | Local-only tools |
| **REL** | Production systems, SLAs | Dev tools, prototypes |
| **DATA** | Persistent storage, migrations | Stateless components |
| **INT** | External APIs, contracts | Self-contained systems |
| **OPS** | Deployed services | Libraries, frameworks |
| **MAINT** | Long-lived code | Throwaway prototypes |
| **TEST** | Quality-critical systems | Exploratory work |
| **COMPL** | Regulated industries | Internal tools |
| **UX** | End-user impact | Backend infrastructure |
| **BIZ** | Business alignment needed | Technical decisions |
````
`@/cpt:checklist`

`@cpt:check`
```toml
id = "ARCH-ADR-001"
domain = "ARCH"
title = "Decision Significance"
severity = "CRITICAL"
ref = "ISO 42010 §6.7.1 — Architecture decisions shall be documented when they affect the system's fundamental structure"
kind = "must_have"
```
```markdown
- [ ] Decision is architecturally significant (not trivial)
- [ ] Decision affects multiple components or teams
- [ ] Decision is difficult to reverse
- [ ] Decision has long-term implications
- [ ] Decision represents a real choice between alternatives
- [ ] Decision is worth documenting for future reference
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-002"
domain = "ARCH"
title = "Context Completeness"
severity = "CRITICAL"
ref = "Michael Nygard ADR Template — \"Context\" section; ISO 42010 §6.7.2 — Decision rationale shall include the context"
kind = "must_have"
```
```markdown
- [ ] Problem statement is clear and specific
- [ ] Business context explained
- [ ] Technical context explained
- [ ] Constraints identified
- [ ] Assumptions stated
- [ ] Timeline/urgency documented
- [ ] Stakeholders identified
- [ ] ≥2 sentences describing the problem
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-003"
domain = "ARCH"
title = "Options Quality"
severity = "CRITICAL"
ref = "ISO 42010 §6.7.3 — Decision rationale shall document considered alternatives"
kind = "must_have"
```
```markdown
- [ ] ≥2 distinct options considered
- [ ] Options are genuinely viable
- [ ] Options are meaningfully different
- [ ] Chosen option clearly marked
- [ ] Option descriptions are comparable
- [ ] No strawman options (obviously inferior just for comparison)
- [ ] All options could realistically be implemented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-004"
domain = "ARCH"
title = "Decision Rationale"
severity = "CRITICAL"
ref = "Michael Nygard ADR Template — \"Decision\" & \"Consequences\" sections; ISO 42010 §6.7.2 — rationale documentation"
kind = "must_have"
```
```markdown
- [ ] Chosen option clearly stated
- [ ] Rationale explains WHY this option was chosen
- [ ] Rationale connects to context and constraints
- [ ] Trade-offs acknowledged
- [ ] Consequences documented (good and bad)
- [ ] Risks of chosen option acknowledged
- [ ] Mitigation strategies for risks documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-005"
domain = "ARCH"
title = "Traceability"
severity = "HIGH"
ref = "ISO 29148 §5.2.8 — Requirements traceability; ISO 42010 §5.7 — AD element relationships"
kind = "must_have"
```
```markdown
- [ ] Links to related requirements, risks, or constraints are provided
- [ ] Links to impacted architecture and design documents are provided (when applicable)
- [ ] Links to impacted feature specifications are provided (when applicable)
- [ ] Each link has a short explanation of relevance
- [ ] Scope of impact is explicitly stated (what changes, what does not)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-006"
domain = "ARCH"
title = "ADR Metadata Quality"
severity = "CRITICAL"
ref = "Michael Nygard ADR Template — Title, Status, Date fields"
kind = "must_have"
```
```markdown
- [ ] Title is descriptive and action-oriented
- [ ] Date is present and unambiguous
- [ ] Status is present and uses a consistent vocabulary (e.g., Proposed, Accepted, Rejected, Deprecated, Superseded)
- [ ] Decision owner/approver is identified (person/team)
- [ ] Scope / affected systems are stated
- [ ] If this record supersedes another decision record, the superseded record is linked
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-007"
domain = "ARCH"
title = "Decision Drivers (if present)"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Drivers are specific and measurable where possible
- [ ] Drivers are prioritized
- [ ] Drivers trace to business or technical requirements
- [ ] Drivers are used to evaluate options
- [ ] No vague drivers ("good", "better", "fast")
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-008"
domain = "ARCH"
title = "Supersession Handling"
severity = "HIGH (if applicable)"
ref = "Michael Nygard ADR Template — Status values include \"Superseded by [ADR-XXX]\""
kind = "must_have"
```
```markdown
- [ ] Superseding ADR referenced
- [ ] Reason for supersession explained
- [ ] Migration guidance provided
- [ ] Deprecated specs identified
- [ ] Timeline for transition documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-009"
domain = "ARCH"
title = "Review Cadence"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] A review date or trigger is defined (when the decision should be revisited)
- [ ] Conditions that would invalidate this decision are documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-010"
domain = "ARCH"
title = "Decision Scope"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Decision scope is clearly defined
- [ ] Boundaries of the decision are explicitly stated
- [ ] Assumptions about the scope are documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "PERF-ADR-001"
domain = "PERF"
title = "Performance Impact"
severity = "HIGH (if applicable)"
ref = "ISO 25010 §4.2.2 — Time behavior, resource utilization, capacity sub-characteristics"
kind = "must_have"
```
```markdown
- [ ] Performance requirements referenced
- [ ] Performance trade-offs documented
- [ ] Latency impact analyzed
- [ ] Throughput impact analyzed
- [ ] Resource consumption impact analyzed
- [ ] Scalability impact analyzed
- [ ] Benchmarks or estimates provided where applicable
```
`@/cpt:check`

`@cpt:check`
```toml
id = "PERF-ADR-002"
domain = "PERF"
title = "Performance Testing"
severity = "MEDIUM (if applicable)"
kind = "must_have"
```
```markdown
- [ ] How to verify performance claims documented
- [ ] Performance acceptance criteria stated
- [ ] Load testing approach outlined
- [ ] Performance monitoring approach outlined
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-ADR-001"
domain = "SEC"
title = "Security Impact"
severity = "CRITICAL (if applicable)"
ref = "OWASP ASVS V1.2 — Security architecture requirements; ISO 27001 Annex A.8 — Asset management"
kind = "must_have"
```
```markdown
- [ ] Security requirements referenced
- [ ] Security trade-offs documented
- [ ] Threat model impact analyzed
- [ ] Attack surface changes documented
- [ ] Security risks of each option analyzed
- [ ] Compliance impact analyzed
- [ ] Data protection impact analyzed
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-ADR-002"
domain = "SEC"
title = "Security Review"
severity = "HIGH (if applicable)"
ref = "ISO 27001 §9.2 — Internal audit; OWASP ASVS V1.2.4 — Security architecture review"
kind = "must_have"
```
```markdown
- [ ] Security review conducted
- [ ] Security reviewer identified
- [ ] Security concerns addressed
- [ ] Penetration testing requirements documented
- [ ] Security monitoring requirements documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-ADR-003"
domain = "SEC"
title = "Authentication/Authorization Impact"
severity = "HIGH (if applicable)"
ref = "OWASP ASVS V2 — Authentication, V4 — Access Control"
kind = "must_have"
```
```markdown
- [ ] AuthN mechanism changes documented
- [ ] AuthZ model changes documented
- [ ] Session management changes documented
- [ ] Token/credential handling changes documented
- [ ] Backward compatibility for auth documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "REL-ADR-001"
domain = "REL"
title = "Reliability Impact"
severity = "HIGH (if applicable)"
ref = "ISO 25010 §4.2.5 — Maturity, availability, fault tolerance, recoverability"
kind = "must_have"
```
```markdown
- [ ] Availability impact analyzed
- [ ] Failure mode changes documented
- [ ] Recovery impact analyzed
- [ ] Single point of failure analysis
- [ ] Resilience pattern changes documented
- [ ] SLA impact documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "REL-ADR-002"
domain = "REL"
title = "Operational Readiness"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Deployment complexity analyzed
- [ ] Rollback strategy documented
- [ ] Monitoring requirements documented
- [ ] Alerting requirements documented
- [ ] Runbook updates required documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DATA-ADR-001"
domain = "DATA"
title = "Data Impact"
severity = "HIGH (if applicable)"
ref = "IEEE 1016 §5.6 — Information viewpoint: data entities, relationships, integrity constraints"
kind = "must_have"
```
```markdown
- [ ] Data model changes documented
- [ ] Migration requirements documented
- [ ] Backward compatibility analyzed
- [ ] Data integrity impact analyzed
- [ ] Data consistency impact analyzed
- [ ] Data volume impact analyzed
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DATA-ADR-002"
domain = "DATA"
title = "Data Governance"
severity = "MEDIUM (if applicable)"
ref = "ISO 27001 Annex A.5.9-5.14 — Information classification, handling"
kind = "must_have"
```
```markdown
- [ ] Data ownership impact documented
- [ ] Data classification impact documented
- [ ] Data retention impact documented
- [ ] Privacy impact analyzed
- [ ] Compliance impact documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "INT-ADR-001"
domain = "INT"
title = "Integration Impact"
severity = "HIGH (if applicable)"
ref = "IEEE 1016 §5.3 — Interface viewpoint: services, protocols, data formats"
kind = "must_have"
```
```markdown
- [ ] API breaking changes documented
- [ ] Protocol changes documented
- [ ] Integration partner impact analyzed
- [ ] Version compatibility documented
- [ ] Migration path documented
- [ ] Deprecation timeline documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "INT-ADR-002"
domain = "INT"
title = "Contract Changes"
severity = "HIGH (if applicable)"
kind = "must_have"
```
```markdown
- [ ] Contract changes documented
- [ ] Backward compatibility analyzed
- [ ] Consumer notification requirements documented
- [ ] Testing requirements for consumers documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "OPS-ADR-001"
domain = "OPS"
title = "Operational Impact"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Deployment impact analyzed
- [ ] Infrastructure changes documented
- [ ] Configuration changes documented
- [ ] Monitoring changes documented
- [ ] Logging changes documented
- [ ] Cost impact analyzed
```
`@/cpt:check`

`@cpt:check`
```toml
id = "OPS-ADR-002"
domain = "OPS"
title = "Transition Plan"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Rollout strategy documented
- [ ] Spec flag requirements documented
- [ ] Canary/gradual rollout requirements documented
- [ ] Rollback triggers documented
- [ ] Success criteria documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "MAINT-ADR-001"
domain = "MAINT"
title = "Maintainability Impact"
severity = "MEDIUM"
ref = "ISO 25010 §4.2.7 — Modularity, reusability, analysability, modifiability, testability"
kind = "must_have"
```
```markdown
- [ ] Code complexity impact analyzed
- [ ] Technical debt impact documented
- [ ] Learning curve for team documented
- [ ] Documentation requirements documented
- [ ] Long-term maintenance burden analyzed
```
`@/cpt:check`

`@cpt:check`
```toml
id = "MAINT-ADR-002"
domain = "MAINT"
title = "Evolution Path"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Future evolution considerations documented
- [ ] Extension points preserved or documented
- [ ] Deprecation path documented
- [ ] Migration to future solutions documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "TEST-ADR-001"
domain = "TEST"
title = "Testing Impact"
severity = "MEDIUM"
ref = "ISO 29119-3 §8 — Test design specification; ISO 25010 §4.2.7.5 — Testability"
kind = "must_have"
```
```markdown
- [ ] Test strategy changes documented
- [ ] Test coverage requirements documented
- [ ] Test automation impact analyzed
- [ ] Integration test requirements documented
- [ ] Performance test requirements documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "TEST-ADR-002"
domain = "TEST"
title = "Validation Plan"
severity = "MEDIUM"
ref = "ISO 29119-3 §9 — Test case specification; acceptance criteria"
kind = "must_have"
```
```markdown
- [ ] How to validate decision documented
- [ ] Acceptance criteria stated
- [ ] Success metrics defined
- [ ] Timeframe for validation stated
```
`@/cpt:check`

`@cpt:check`
```toml
id = "COMPL-ADR-001"
domain = "COMPL"
title = "Compliance Impact"
severity = "CRITICAL (if applicable)"
ref = "ISO 27001 §4.2 — Interested parties; §6.1 — Risk assessment; Annex A — Controls"
kind = "must_have"
```
```markdown
- [ ] Regulatory impact analyzed
- [ ] Certification impact documented
- [ ] Audit requirements documented
- [ ] Legal review requirements documented
- [ ] Privacy impact assessment requirements documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "UX-ADR-001"
domain = "UX"
title = "User Impact"
severity = "MEDIUM (if applicable)"
kind = "must_have"
```
```markdown
- [ ] User experience impact documented
- [ ] User migration requirements documented
- [ ] User communication requirements documented
- [ ] Training requirements documented
- [ ] Documentation updates required documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-ADR-001"
domain = "BIZ"
title = "Business Alignment"
severity = "HIGH"
ref = "ISO 29148 §5.2 — Stakeholder requirements definition; business value traceability"
kind = "must_have"
```
```markdown
- [ ] Business requirements addressed
- [ ] Business value of decision explained
- [ ] Time-to-market impact documented
- [ ] Cost implications documented
- [ ] Resource requirements documented
- [ ] Stakeholder buy-in documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-ADR-002"
domain = "BIZ"
title = "Risk Assessment"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Business risks identified
- [ ] Risk mitigation strategies documented
- [ ] Risk acceptance documented
- [ ] Contingency plans documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-NO-001"
domain = "ARCH"
title = "No Complete Architecture Description"
severity = "CRITICAL"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No full system architecture restatement
- [ ] No complete component model
- [ ] No full domain model
- [ ] No comprehensive API specification
- [ ] No full infrastructure description

**Where it belongs**: System/Architecture design documentation
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-NO-002"
domain = "ARCH"
title = "No Spec Implementation Details"
severity = "HIGH"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No feature user flows
- [ ] No feature algorithms
- [ ] No feature state machines
- [ ] No step-by-step implementation guides
- [ ] No low-level implementation pseudo-code

**Where it belongs**: Spec specification / implementation design documentation
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-ADR-NO-001"
domain = "BIZ"
title = "No Product Requirements"
severity = "HIGH"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No business vision statements
- [ ] No actor definitions
- [ ] No functional requirement definitions
- [ ] No use case definitions
- [ ] No NFR definitions

**Where it belongs**: Requirements / Product specification document
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-ADR-NO-002"
domain = "BIZ"
title = "No Implementation Tasks"
severity = "HIGH"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No sprint/iteration plans
- [ ] No detailed task breakdowns
- [ ] No effort estimates
- [ ] No developer assignments
- [ ] No project timelines

**Where it belongs**: Project management tools
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DATA-ADR-NO-001"
domain = "DATA"
title = "No Complete Schema Definitions"
severity = "MEDIUM"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No full database schemas
- [ ] No complete JSON schemas
- [ ] No full API specifications
- [ ] No migration scripts

**Where it belongs**: Source code repository or architecture documentation
```
`@/cpt:check`

`@cpt:check`
```toml
id = "MAINT-ADR-NO-001"
domain = "MAINT"
title = "No Code Implementation"
severity = "HIGH"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No production code
- [ ] No complete code examples
- [ ] No library implementations
- [ ] No configuration files
- [ ] No infrastructure code

**Where it belongs**: Source code repository
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-ADR-NO-001"
domain = "SEC"
title = "No Security Secrets"
severity = "CRITICAL"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No API keys
- [ ] No passwords
- [ ] No certificates
- [ ] No private keys
- [ ] No connection strings with credentials

**Where it belongs**: Secret management system
```
`@/cpt:check`

`@cpt:check`
```toml
id = "TEST-ADR-NO-001"
domain = "TEST"
title = "No Test Implementation"
severity = "MEDIUM"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No test case code
- [ ] No test data
- [ ] No test scripts
- [ ] No complete test plans

**Where it belongs**: Test documentation or test code
```
`@/cpt:check`

`@cpt:check`
```toml
id = "OPS-ADR-NO-001"
domain = "OPS"
title = "No Operational Procedures"
severity = "MEDIUM"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No complete runbooks
- [ ] No incident response procedures
- [ ] No monitoring configurations
- [ ] No alerting configurations

**Where it belongs**: Operations documentation or runbooks
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-NO-003"
domain = "ARCH"
title = "No Trivial Decisions"
severity = "MEDIUM"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No variable naming decisions
- [ ] No code formatting decisions
- [ ] No obvious technology choices (no alternatives)
- [ ] No easily reversible decisions
- [ ] No team-local decisions with no broader impact

**Where it belongs**: Team conventions, coding standards, or not documented at all
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-NO-004"
domain = "ARCH"
title = "No Incomplete Decisions"
severity = "HIGH"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No "TBD" in critical sections
- [ ] No missing context
- [ ] No missing options analysis
- [ ] No missing rationale
- [ ] No missing consequences

**Where it belongs**: Complete the ADR before publishing, or use "Proposed" status
```
`@/cpt:check`

`@cpt:check`
```toml
id = "QUALITY-001"
domain = "QUALITY"
title = "Neutrality"
severity = "MEDIUM"
ref = "Michael Nygard — \"Options should be presented neutrally\""
kind = "adr_specific_quality_checks"
```
```markdown
- [ ] Options described neutrally (no leading language)
- [ ] Pros and cons balanced for all options
- [ ] No strawman arguments
- [ ] Honest about chosen option's weaknesses
- [ ] Fair comparison of alternatives
```
`@/cpt:check`

`@cpt:check`
```toml
id = "QUALITY-002"
domain = "QUALITY"
title = "Clarity"
severity = "HIGH"
ref = "ISO 29148 §5.2.5 — Requirements shall be unambiguous; IEEE 1016 §4.2 — SDD comprehensibility"
kind = "adr_specific_quality_checks"
```
```markdown
- [ ] Decision can be understood without insider knowledge
- [ ] Acronyms expanded on first use
- [ ] Technical terms defined if unusual
- [ ] No ambiguous language
- [ ] Clear, concrete statements
```
`@/cpt:check`

`@cpt:check`
```toml
id = "QUALITY-003"
domain = "QUALITY"
title = "Actionability"
severity = "HIGH"
ref = "Michael Nygard — \"Decision\" section specifies what to do"
kind = "adr_specific_quality_checks"
```
```markdown
- [ ] Clear what action to take based on decision
- [ ] Implementation guidance provided
- [ ] Scope of application clear
- [ ] Exceptions documented
- [ ] Expiration/review date set (if applicable)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "QUALITY-004"
domain = "QUALITY"
title = "Reviewability"
severity = "MEDIUM"
ref = "ISO 42010 §6.7 — AD rationale shall be verifiable"
kind = "adr_specific_quality_checks"
```
```markdown
- [ ] Can be reviewed in a reasonable time
- [ ] Evidence and references provided
- [ ] Assumptions verifiable
- [ ] Consequences measurable
- [ ] Success criteria verifiable
```
`@/cpt:check`


---

## Template Structure

Headings, prompts, IDs, and examples that define the generated `template.md`
and `example.md` files.

Each `@cpt:heading` defines a section in the template with its level, numbering,
and pattern for validation. `@cpt:prompt` provides the placeholder content that
appears in the generated template. `@cpt:example` provides example content.
`@cpt:id` defines identifier schemas used in those sections.

### Title (H1)

`@cpt:heading`
```toml
id = "adr-h1-title"
level = 1
required = true
numbered = false
multiple = false
template = "{Short title describing problem and chosen solution}"
prompt = "Describe the problem and chosen solution in the title"
description = "ADR document title (H1)."
examples = ["# ADR-0001: Use PostgreSQL for Task Storage"]
```
`@/cpt:heading`

`@cpt:id`
```toml
kind = "adr"
name = "Architecture Decision Record"
description = "A documented architecture decision with context, options, outcome, and consequences; referenced from DESIGN."
required = true
task = false
priority = false
template = "cpt-{system}-adr-{slug}"
examples = ["cpt-cypilot-adr-template-centric-architecture", "cpt-ex-ovwa-adr-cli-daemon-launchagent"]
to_code = false
headings = ["adr-h1-title"]
```
`@/cpt:id`

`@cpt:prompt`
```markdown
**ID**: `cpt-{system}-adr-{slug}`
```
`@/cpt:prompt`

`@cpt:example`
```markdown
**ID**: `cpt-ex-task-flow-adr-postgres-storage`
```
`@/cpt:example`

### Context and Problem Statement

`@cpt:heading`
```toml
id = "adr-context"
level = 2
required = true
numbered = false
multiple = false
pattern = "Context and Problem Statement"
description = "Problem context and motivating forces."
examples = ["## Context and Problem Statement"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
{Describe the context and problem statement in 2-3 sentences. You may articulate the problem as a question.}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
TaskFlow needs persistent storage for tasks, users, and audit history. We need to choose between SQL and NoSQL databases considering query patterns, data relationships, and team expertise.

The system will handle:

- Task CRUD operations with complex filtering
- User and team relationships
- Assignment history and audit trail
- Real-time updates via change notifications
```
`@/cpt:example`

### Decision Drivers

`@cpt:heading`
```toml
id = "adr-decision-drivers"
level = 2
required = true
numbered = false
multiple = false
pattern = "Decision Drivers"
description = "Key decision drivers and constraints."
examples = ["## Decision Drivers"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
* {Decision driver 1, e.g., a force, facing concern, …}
* {Decision driver 2, e.g., a force, facing concern, …}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
- Strong consistency required for task state transitions
- Relational queries needed for assignments and team structures
- Team has existing PostgreSQL expertise
- Operational maturity and hosting options important
```
`@/cpt:example`

### Considered Options

`@cpt:heading`
```toml
id = "adr-considered-options"
level = 2
required = true
numbered = false
multiple = false
pattern = "Considered Options"
description = "Options that were considered."
examples = ["## Considered Options"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
* {Title of option 1}
* {Title of option 2}
* {Title of option 3}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
1. **PostgreSQL** — Relational database with strong ACID guarantees, mature ecosystem, team expertise
2. **MongoDB** — Document store with flexible schema, good for rapid iteration, less suited for relational data
3. **SQLite** — Embedded database for simpler deployment, limited concurrent access, no built-in replication
```
`@/cpt:example`

### Decision Outcome

`@cpt:heading`
```toml
id = "adr-decision-outcome"
level = 2
required = true
numbered = false
multiple = false
pattern = "Decision Outcome"
description = "Selected decision and outcome."
examples = ["## Decision Outcome"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
Chosen option: "{title of option 1}", because {justification, e.g., only option which meets k.o. criterion decision driver | resolves force | comes out best}.
```
`@/cpt:prompt`

`@cpt:example`
```markdown
Chosen option: **PostgreSQL**, because tasks have relational data (users, assignments, comments) that benefit from joins, strong consistency is needed for status transitions and assignments, team has existing PostgreSQL expertise, and it supports JSON columns for flexible metadata if needed later.
```
`@/cpt:example`

#### Consequences

`@cpt:heading`
```toml
id = "adr-decision-outcome-consequences"
level = 3
required = true
numbered = false
multiple = false
pattern = "Consequences"
description = "Consequences of the decision."
examples = ["### Consequences"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
* Good, because {positive consequence, e.g., improvement of one or more desired qualities}
* Bad, because {negative consequence, e.g., compromising one or more desired qualities}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
- Positive: ACID transactions ensure data integrity during concurrent updates
- Positive: Efficient queries for filtering tasks by status, assignee, due date
- Negative: Requires separate database server (vs embedded SQLite)
- Negative: Schema migrations needed for model changes
- Follow-up: Set up connection pooling for scalability
```
`@/cpt:example`

#### Confirmation

How the decision will be validated after implementation.

`@cpt:heading`
```toml
id = "adr-decision-outcome-confirmation"
level = 3
required = true
numbered = false
multiple = false
pattern = "Confirmation"
description = "How/when the decision will be confirmed."
examples = ["### Confirmation"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
{Describe how the implementation/compliance of the ADR can be confirmed. E.g., design/code review, ArchUnit test, etc.}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
Confirmed when:

- A prototype persists tasks and assignments with required relational queries
- Migration story is documented and validated on a schema change
```
`@/cpt:example`

### Pros and Cons of the Options

Detailed evaluation of each considered option.

`@cpt:heading`
```toml
id = "adr-pros-cons"
level = 2
required = true
numbered = false
multiple = false
pattern = "Pros and Cons of the Options"
description = "Pros and cons analysis for the options."
examples = ["## Pros and Cons of the Options"]
```
`@/cpt:heading`

`@cpt:heading`
```toml
id = "adr-pros-cons-entry"
level = 3
required = true
numbered = false
multiple = true
template = "{Title of option 1}"
description = "A single option evaluation entry (pros/cons)."
examples = ["### PostgreSQL", "### MongoDB", "### SQLite"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
{Description or pointer to more information}

* Good, because {argument a}
* Good, because {argument b}
* Neutral, because {argument c}
* Bad, because {argument d}

### {Title of option 2}

{Description or pointer to more information}

* Good, because {argument a}
* Bad, because {argument b}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
- Pros: Strong consistency, rich SQL queries, mature ecosystem
- Cons: Operational overhead (DB server, backups, migrations)

### MongoDB

- Pros: Flexible schema, quick iteration
- Cons: Harder relational queries and consistency model trade-offs

### SQLite

- Pros: Simple deployment, minimal ops
- Cons: Limited concurrent writes and scaling options
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "adr-more-info"
level = 2
required = false
numbered = false
multiple = false
pattern = "More Information"
description = "Optional additional information and links."
examples = ["## More Information"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
{Additional evidence, team agreement, links to related decisions and resources.}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
- [`cpt-ex-task-flow-fr-task-management`](../PRD.md) — Primary requirement for task storage
- [`cpt-ex-task-flow-feature-task-crud`](../specs/task-crud/DESIGN.md) — Spec implementing task persistence
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "adr-traceability"
level = 2
required = false
numbered = false
multiple = false
pattern = "Traceability"
description = "Optional traceability links back to requirements/decisions."
examples = []
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
- **PRD**: [PRD.md](../PRD.md)
- **DESIGN**: [DESIGN.md](../DESIGN.md)

This decision directly addresses the following requirements or design elements:

* `cpt-{system}-fr-{slug}` — {Brief description of how this decision satisfies/constrains this requirement}
* `cpt-{system}-nfr-{slug}` — {Brief description of how this decision satisfies/constrains this requirement}
* `cpt-{system}-usecase-{slug}` — {Brief description of the interaction/use case impacted}
* `cpt-{system}-design-{slug}` — {Brief description of design element affected}
```
`@/cpt:prompt`

`@/cpt:example`
