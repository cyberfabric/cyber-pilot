# ADR Rules

**Artifact**: ADR
**Kit**: sdlc

**Dependencies**:
- `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/template.md` — structural reference
- `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/checklist.md` — semantic quality criteria
- `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/examples/example.md` — reference implementation

## Table of Contents

1. [Prerequisites](#prerequisites)
   - [Load Dependencies](#load-dependencies)
2. [Requirements](#requirements)
   - [Structural](#structural)
   - [Versioning](#versioning)
   - [Semantic](#semantic)
   - [Scope](#scope)
   - [Status Traceability](#status-traceability)
   - [Constraints](#constraints)
   - [Deliberate Omissions (MUST NOT HAVE)](#deliberate-omissions-must-not-have)
   - [ADR Writing Quality](#adr-writing-quality)
3. [Tasks](#tasks)
   - [Phase 1: Setup](#phase-1-setup)
   - [Phase 2: Content Creation](#phase-2-content-creation)
   - [Phase 3: IDs and Structure](#phase-3-ids-and-structure)
   - [Phase 4: Quality Check](#phase-4-quality-check)
4. [Validation](#validation)
   - [Phase 1: Structural Validation (Deterministic)](#phase-1-structural-validation-deterministic)
   - [Phase 2: Semantic Validation (Checklist-based)](#phase-2-semantic-validation-checklist-based)
   - [Phase 3: Validation Report](#phase-3-validation-report)
   - [Phase 4: Applicability Context](#phase-4-applicability-context)
   - [Phase 5: Review Scope Selection](#phase-5-review-scope-selection)
   - [Phase 6: Report Format](#phase-6-report-format)
   - [Phase 7: Reporting Commitment](#phase-7-reporting-commitment)
   - [Phase 8: PR Review Focus (ADR)](#phase-8-pr-review-focus-adr)
5. [Error Handling](#error-handling)
   - [Number Conflict](#number-conflict)
   - [Missing Directory](#missing-directory)
   - [Escalation](#escalation)
6. [Next Steps](#next-steps)
   - [Options](#options)

---

## Prerequisites

### Load Dependencies

- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/template.md` for structure
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/checklist.md` for semantic guidance
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/examples/example.md` for reference style
- [ ] Read `{cypilot_path}/config/artifacts.toml` to determine ADR directory
- [ ] Load `{cypilot_path}/.core/architecture/specs/traceability.md` for ID formats
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/constraints.toml` for kit-level constraints
- [ ] Load `{cypilot_path}/.core/architecture/specs/kit/constraints.md` for constraints specification

---

## Requirements

### Structural

- [ ] ADR follows `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/template.md` structure
- [ ] Artifact frontmatter is required
- [ ] ADR has unique ID: `cpt-{hierarchy-prefix}-adr-{slug}` (e.g., `cpt-myapp-adr-use-postgresql`)
- [ ] ID has priority marker (`p1`-`p9`)
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs

### Versioning

- [ ] ADR version in filename: `NNNN-{slug}-v{N}.md`
- [ ] When PROPOSED: minor edits allowed without version change
- [ ] When ACCEPTED: **immutable** — do NOT edit decision/rationale
- [ ] To change accepted decision: create NEW ADR with SUPERSEDES reference
- [ ] Superseding ADR: `cpt-{hierarchy-prefix}-adr-{new-slug}` with status SUPERSEDED on original

### Semantic

**Reference**: `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/checklist.md` for detailed criteria

- [ ] Problem/context clearly stated
- [ ] At least 2-3 options considered
- [ ] Decision rationale explained
- [ ] Consequences documented (pros and cons)
- [ ] Valid status (PROPOSED, ACCEPTED, REJECTED, DEPRECATED, SUPERSEDED)

### Scope

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

### Status Traceability

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

### Constraints

- [ ] ALWAYS open and follow `{cypilot_path}/.gen/kits/sdlc/constraints.toml` (kit root)
- [ ] Treat `constraints.toml` as primary validator for:
  - where IDs are defined
  - where IDs are referenced
  - which cross-artifact references are required / optional / prohibited

**References**:
- `{cypilot_path}/.core/requirements/kit-constraints.md`
- `{cypilot_path}/.core/schemas/kit-constraints.schema.json`

**Validation Checks**:
- `cypilot validate` enforces `identifiers[<kind>].references` rules for ADR coverage in DESIGN

### Deliberate Omissions (MUST NOT HAVE)

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

### ADR Writing Quality

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

---

## Tasks

### Phase 1: Setup

- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/template.md` for structure
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/checklist.md` for semantic guidance
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/examples/example.md` for reference style
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

### Phase 2: Content Creation

**Use example as reference:**

| Section | Example Reference | Checklist Guidance |
|---------|-------------------|-------------------|
| Context | How example states problem | ADR-001: Context Clarity |
| Options | How example lists alternatives | ADR-002: Options Analysis |
| Decision | How example explains choice | ADR-003: Decision Rationale |
| Consequences | How example documents impact | ADR-004: Consequences |

### Phase 3: IDs and Structure

- [ ] Generate ID: `cpt-{hierarchy-prefix}-adr-{slug}` (e.g., `cpt-myapp-adr-use-postgresql`)
- [ ] Assign priority based on impact
- [ ] Link to DESIGN if applicable
- [ ] Verify uniqueness with `cypilot list-ids`

### Phase 4: Quality Check

- [ ] Compare to `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/examples/example.md`
- [ ] Self-review against `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/checklist.md`
- [ ] Verify rationale is complete

**ADR Immutability Rule**:
- After ACCEPTED: do not modify decision/rationale
- To change: create new ADR with SUPERSEDES reference

---

## Validation

### Phase 1: Structural Validation (Deterministic)

Run `cypilot validate` for:
- [ ] Template structure compliance
- [ ] ID format validation
- [ ] No placeholders

### Phase 2: Semantic Validation (Checklist-based)

Apply `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/checklist.md`:
1. Verify context explains why decision needed
2. Verify options have pros/cons
3. Verify decision has clear rationale
4. Verify consequences documented

### Phase 3: Validation Report

```
ADR Validation Report
═════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```

### Phase 4: Applicability Context

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

### Phase 5: Review Scope Selection

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

### Phase 6: Report Format

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

### Phase 7: Reporting Commitment

- [ ] I reported all issues I found
- [ ] I used the exact report format defined in this checklist (no deviations)
- [ ] I included Why Applicable justification for each issue
- [ ] I included evidence and impact for each issue
- [ ] I proposed concrete fixes for each issue
- [ ] I did not hide or omit known problems
- [ ] I verified explicit handling for all major checklist categories
- [ ] I am ready to iterate on the proposals and re-review after changes

### Phase 8: PR Review Focus (ADR)

When reviewing PRs that add or change Architecture Decision Records, additionally focus on:

- [ ] Ensure the problem is module/system scoped, not generic and repeatable
- [ ] Compliance with `{cypilot_path}/.gen/kits/sdlc/artifacts/ADR/template.md` structure (generated from blueprint)
- [ ] Ensure the problem is not already solved by other existing ADRs in the project ADR directory (see `{cypilot_path}/config/artifacts.toml` for path)
- [ ] Alternatives are genuinely different approaches (not straw men)
- [ ] Decision rationale is concrete and traceable to project constraints

---

## Error Handling

### Number Conflict

**If number conflict detected** (file already exists):
```
⚠ ADR number conflict: {NNNN} already exists
→ Verify existing ADRs: ls architecture/ADR/
→ Assign next available number: {NNNN + 1}
→ If duplicate content: consider updating existing ADR instead
```

### Missing Directory

**If ADR directory doesn't exist**:
```
⚠ ADR directory not found
→ Create: mkdir -p architecture/ADR
→ Start numbering at 0001
```

### Escalation

- [ ] Ask user when decision significance is unclear
- [ ] Ask user when options require domain expertise to evaluate
- [ ] Ask user when compliance or security implications are uncertain

---

## Next Steps

### Options

| Condition | Suggested Next Step |
|-----------|---------------------|
| ADR PROPOSED | Share for review, then update status to ACCEPTED |
| ADR ACCEPTED | `/cypilot-generate DESIGN` — incorporate decision into design |
| Related ADR needed | `/cypilot-generate ADR` — create related decision record |
| ADR supersedes another | Update original ADR status to SUPERSEDED |
| Want checklist review only | `/cypilot-analyze semantic` — semantic validation (skip deterministic) |
