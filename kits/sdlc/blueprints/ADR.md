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
sections = ["structural", "versioning", "semantic", "scope", "status_traceability", "constraints"]

[tasks]
phases = ["setup", "content_creation", "ids_and_structure", "quality_check"]

[validation]
sections = ["structural", "semantic"]

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
- [ ] Read adapter `artifacts.toml` to determine ADR directory
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
- [ ] ADR has unique ID: `cpt-{hierarchy-prefix}-adr-{slug}`
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
1. Locate ADR file
2. Update frontmatter status
3. Add status history
4. For SUPERSEDED: add `superseded_by` reference
5. For REJECTED: add `rejection_reason`
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
- [ ] Automated validation: `cypilot validate` enforces ADR coverage in DESIGN
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
- [ ] Read adapter `artifacts.toml` to determine ADR directory
- [ ] Determine next ADR number (ADR-NNNN)
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
- [ ] Generate ID: `cpt-{hierarchy-prefix}-adr-{slug}`
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
- [ ] ADR Immutability Rule: after ACCEPTED, do not modify decision/rationale
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
```markdown
- [ ] If ADR number conflict detected (file already exists):
  - Verify existing ADRs
  - Assign next available number
  - If duplicate content: consider updating existing ADR instead
```
`@/cpt:rule`

#### Missing Directory

`@cpt:rule`
```toml
kind = "error_handling"
section = "missing_directory"
```
```markdown
- [ ] If ADR directory doesn't exist:
  - Create: `mkdir -p architecture/ADR`
  - Start numbering at 0001
```
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
- [ ] Run `cypilot validate --artifact <path>` for:
  - Template structure compliance
  - ID format validation
  - No placeholders
```
`@/cpt:rule`

#### Semantic Validation

`@cpt:rule`
```toml
kind = "validation"
section = "semantic"
```
```markdown
- [ ] Verify context explains why decision needed
- [ ] Verify options have pros/cons
- [ ] Verify decision has clear rationale
- [ ] Verify consequences documented
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
- [ ] ADR PROPOSED → share for review, then update status to ACCEPTED
- [ ] ADR ACCEPTED → `/cypilot-generate DESIGN` — incorporate decision into design
- [ ] Related ADR needed → `/cypilot-generate ADR` — create related decision record
- [ ] ADR supersedes another → update original ADR status to SUPERSEDED
- [ ] Want checklist review only → `/cypilot-analyze semantic` — semantic validation
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
[severity]
levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

[review]
priority = ["ARCH", "SEC", "BIZ"]

[[domain]]
abbr = "ARCH"
name = "Architecture"
standards = ["Michael Nygard ADR Template (2011)", "ISO/IEC/IEEE 42010:2022"]

[[domain]]
abbr = "PERF"
name = "Performance"
standards = ["ISO/IEC 25010:2011"]

[[domain]]
abbr = "SEC"
name = "Security"
standards = ["OWASP ASVS 5.0", "ISO/IEC 27001:2022"]

[[domain]]
abbr = "REL"
name = "Reliability"
standards = ["ISO/IEC 25010:2011"]

[[domain]]
abbr = "DATA"
name = "Data"
standards = ["IEEE 1016-2009"]

[[domain]]
abbr = "INT"
name = "Integration"
standards = ["IEEE 1016-2009"]

[[domain]]
abbr = "OPS"
name = "Operations"
standards = []

[[domain]]
abbr = "MAINT"
name = "Maintainability"
standards = ["ISO/IEC 25010:2011"]

[[domain]]
abbr = "TEST"
name = "Testing"
standards = ["ISO/IEC/IEEE 29119-3:2021"]

[[domain]]
abbr = "COMPL"
name = "Compliance"
standards = ["ISO/IEC 27001:2022"]

[[domain]]
abbr = "UX"
name = "Usability"
standards = []

[[domain]]
abbr = "BIZ"
name = "Business"
standards = ["ISO/IEC/IEEE 29148:2018"]

[[domain]]
abbr = "QUALITY"
name = "Writing Quality"
standards = ["Michael Nygard ADR Template"]
```
`@/cpt:checklist`

### Architecture Checks (ARCH)

Core ADR quality: decision significance, context, options, rationale, traceability.

`@cpt:check`
```toml
id = "ARCH-ADR-001"
domain = "ARCH"
title = "Decision Significance"
severity = "CRITICAL"
ref = "ISO 42010 §6.7.1"
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
ref = "Michael Nygard ADR Template; ISO 42010 §6.7.2"
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
ref = "ISO 42010 §6.7.3"
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
ref = "Michael Nygard ADR Template; ISO 42010 §6.7.2"
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
ref = "ISO 29148 §5.2.8; ISO 42010 §5.7"
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
ref = "Michael Nygard ADR Template"
kind = "must_have"
```
```markdown
- [ ] Title is descriptive and action-oriented
- [ ] Date is present and unambiguous
- [ ] Status is present and uses consistent vocabulary (PROPOSED, ACCEPTED, REJECTED, DEPRECATED, SUPERSEDED)
- [ ] Decision owner/approver is identified (person/team)
- [ ] Scope / affected systems are stated
- [ ] If this record supersedes another, the superseded record is linked
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-007"
domain = "ARCH"
title = "Decision Drivers"
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
severity = "HIGH"
kind = "must_have"
applicable_when = "ADR supersedes another ADR"
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

### Performance Checks (PERF)

Applicable when the decision affects performance-sensitive systems.

`@cpt:check`
```toml
id = "PERF-ADR-001"
domain = "PERF"
title = "Performance Impact"
severity = "HIGH"
ref = "ISO 25010 §4.2.2"
kind = "must_have"
applicable_when = "Performance-sensitive systems"
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
severity = "MEDIUM"
kind = "must_have"
applicable_when = "Performance-sensitive systems"
```
```markdown
- [ ] How to verify performance claims documented
- [ ] Performance acceptance criteria stated
- [ ] Load testing approach outlined
- [ ] Performance monitoring approach outlined
```
`@/cpt:check`

### Security Checks (SEC)

Applicable when the decision involves user data, network, or authentication.

`@cpt:check`
```toml
id = "SEC-ADR-001"
domain = "SEC"
title = "Security Impact"
severity = "CRITICAL"
ref = "OWASP ASVS V1.2; ISO 27001 Annex A.8"
kind = "must_have"
applicable_when = "User data, network, auth"
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
severity = "HIGH"
ref = "ISO 27001 §9.2; OWASP ASVS V1.2.4"
kind = "must_have"
applicable_when = "Security-sensitive decisions"
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
severity = "HIGH"
ref = "OWASP ASVS V2, V4"
kind = "must_have"
applicable_when = "Auth-related decisions"
```
```markdown
- [ ] AuthN mechanism changes documented
- [ ] AuthZ model changes documented
- [ ] Session management changes documented
- [ ] Token/credential handling changes documented
- [ ] Backward compatibility for auth documented
```
`@/cpt:check`

### Reliability Checks (REL)

Applicable for production systems with SLAs.

`@cpt:check`
```toml
id = "REL-ADR-001"
domain = "REL"
title = "Reliability Impact"
severity = "HIGH"
ref = "ISO 25010 §4.2.5"
kind = "must_have"
applicable_when = "Production systems, SLAs"
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

### Data Checks (DATA)

Applicable when the decision affects persistent storage or data migrations.

`@cpt:check`
```toml
id = "DATA-ADR-001"
domain = "DATA"
title = "Data Impact"
severity = "HIGH"
ref = "IEEE 1016 §5.6"
kind = "must_have"
applicable_when = "Persistent storage, migrations"
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
severity = "MEDIUM"
ref = "ISO 27001 Annex A.5.9-5.14"
kind = "must_have"
applicable_when = "Data classification or privacy impact"
```
```markdown
- [ ] Data ownership impact documented
- [ ] Data classification impact documented
- [ ] Data retention impact documented
- [ ] Privacy impact analyzed
- [ ] Compliance impact documented
```
`@/cpt:check`

### Integration Checks (INT)

Applicable when the decision affects external APIs or contracts.

`@cpt:check`
```toml
id = "INT-ADR-001"
domain = "INT"
title = "Integration Impact"
severity = "HIGH"
ref = "IEEE 1016 §5.3"
kind = "must_have"
applicable_when = "External APIs, contracts"
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
severity = "HIGH"
kind = "must_have"
applicable_when = "API contract changes"
```
```markdown
- [ ] Contract changes documented
- [ ] Backward compatibility analyzed
- [ ] Consumer notification requirements documented
- [ ] Testing requirements for consumers documented
```
`@/cpt:check`

### Operations Checks (OPS)

Applicable for deployed services.

`@cpt:check`
```toml
id = "OPS-ADR-001"
domain = "OPS"
title = "Operational Impact"
severity = "HIGH"
kind = "must_have"
applicable_when = "Deployed services"
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

### Maintainability Checks (MAINT)

`@cpt:check`
```toml
id = "MAINT-ADR-001"
domain = "MAINT"
title = "Maintainability Impact"
severity = "MEDIUM"
ref = "ISO 25010 §4.2.7"
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

### Testing Checks (TEST)

`@cpt:check`
```toml
id = "TEST-ADR-001"
domain = "TEST"
title = "Testing Impact"
severity = "MEDIUM"
ref = "ISO 29119-3 §8; ISO 25010 §4.2.7.5"
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
ref = "ISO 29119-3 §9"
kind = "must_have"
```
```markdown
- [ ] How to validate decision documented
- [ ] Acceptance criteria stated
- [ ] Success metrics defined
- [ ] Timeframe for validation stated
```
`@/cpt:check`

### Compliance Checks (COMPL)

Applicable when the decision has regulatory implications.

`@cpt:check`
```toml
id = "COMPL-ADR-001"
domain = "COMPL"
title = "Compliance Impact"
severity = "CRITICAL"
ref = "ISO 27001 §4.2, §6.1"
kind = "must_have"
applicable_when = "Regulated industries"
```
```markdown
- [ ] Regulatory impact analyzed
- [ ] Certification impact documented
- [ ] Audit requirements documented
- [ ] Legal review requirements documented
- [ ] Privacy impact assessment requirements documented
```
`@/cpt:check`

### Usability Checks (UX)

Applicable when the decision impacts user experience.

`@cpt:check`
```toml
id = "UX-ADR-001"
domain = "UX"
title = "User Impact"
severity = "MEDIUM"
kind = "must_have"
applicable_when = "End-user impact"
```
```markdown
- [ ] User experience impact documented
- [ ] User migration requirements documented
- [ ] User communication requirements documented
- [ ] Training requirements documented
- [ ] Documentation updates required documented
```
`@/cpt:check`

### Business Checks (BIZ)

`@cpt:check`
```toml
id = "BIZ-ADR-001"
domain = "BIZ"
title = "Business Alignment"
severity = "HIGH"
ref = "ISO 29148 §5.2"
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

### Writing Quality Checks (QUALITY)

Document clarity, conciseness, and formatting standards.

`@cpt:check`
```toml
id = "QUALITY-001"
domain = "QUALITY"
title = "Neutrality"
severity = "MEDIUM"
ref = "Michael Nygard — options presented neutrally"
kind = "must_have"
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
ref = "ISO 29148 §5.2.5; IEEE 1016 §4.2"
kind = "must_have"
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
ref = "Michael Nygard — Decision section specifies what to do"
kind = "must_have"
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
ref = "ISO 42010 §6.7"
kind = "must_have"
```
```markdown
- [ ] Can be reviewed in a reasonable time
- [ ] Evidence and references provided
- [ ] Assumptions verifiable
- [ ] Consequences measurable
- [ ] Success criteria verifiable
```
`@/cpt:check`

### Anti-Pattern Checks (must_not_have)

These checks flag content that does NOT belong in an ADR.
ADRs should be focused on one decision — not restate the full architecture,
include implementation details, or embed full PRD content.

`@cpt:check`
```toml
id = "ARCH-ADR-NO-001"
domain = "ARCH"
title = "No Complete Architecture Description"
severity = "CRITICAL"
kind = "must_not_have"
belongs_to = "System/Architecture design documentation"
```
```markdown
- [ ] No full system architecture restatement
- [ ] No complete component model
- [ ] No full domain model
- [ ] No comprehensive API specification
- [ ] No full infrastructure description
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-NO-002"
domain = "ARCH"
title = "No Spec Implementation Details"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "Spec specification / implementation design"
```
```markdown
- [ ] No feature user flows
- [ ] No feature algorithms
- [ ] No feature state machines
- [ ] No step-by-step implementation guides
- [ ] No low-level implementation pseudo-code
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-ADR-NO-001"
domain = "BIZ"
title = "No Product Requirements"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "PRD"
```
```markdown
- [ ] No business vision statements
- [ ] No actor definitions
- [ ] No functional requirement definitions
- [ ] No use case definitions
- [ ] No NFR definitions
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-ADR-NO-002"
domain = "BIZ"
title = "No Implementation Tasks"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "Project management tools"
```
```markdown
- [ ] No sprint/iteration plans
- [ ] No detailed task breakdowns
- [ ] No effort estimates
- [ ] No developer assignments
- [ ] No project timelines
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DATA-ADR-NO-001"
domain = "DATA"
title = "No Complete Schema Definitions"
severity = "MEDIUM"
kind = "must_not_have"
belongs_to = "Source code repository or architecture documentation"
```
```markdown
- [ ] No full database schemas
- [ ] No complete JSON schemas
- [ ] No full API specifications
- [ ] No migration scripts
```
`@/cpt:check`

`@cpt:check`
```toml
id = "MAINT-ADR-NO-001"
domain = "MAINT"
title = "No Code Implementation"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "Source code repository"
```
```markdown
- [ ] No production code
- [ ] No complete code examples
- [ ] No library implementations
- [ ] No configuration files
- [ ] No infrastructure code
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-ADR-NO-001"
domain = "SEC"
title = "No Security Secrets"
severity = "CRITICAL"
kind = "must_not_have"
belongs_to = "Secret management system"
```
```markdown
- [ ] No API keys
- [ ] No passwords
- [ ] No certificates
- [ ] No private keys
- [ ] No connection strings with credentials
```
`@/cpt:check`

`@cpt:check`
```toml
id = "TEST-ADR-NO-001"
domain = "TEST"
title = "No Test Implementation"
severity = "MEDIUM"
kind = "must_not_have"
belongs_to = "Test documentation or test code"
```
```markdown
- [ ] No test case code
- [ ] No test data
- [ ] No test scripts
- [ ] No complete test plans
```
`@/cpt:check`

`@cpt:check`
```toml
id = "OPS-ADR-NO-001"
domain = "OPS"
title = "No Operational Procedures"
severity = "MEDIUM"
kind = "must_not_have"
belongs_to = "Operations documentation or runbooks"
```
```markdown
- [ ] No complete runbooks
- [ ] No incident response procedures
- [ ] No monitoring configurations
- [ ] No alerting configurations
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-NO-003"
domain = "ARCH"
title = "No Trivial Decisions"
severity = "MEDIUM"
kind = "must_not_have"
belongs_to = "Team conventions, coding standards"
```
```markdown
- [ ] No variable naming decisions
- [ ] No code formatting decisions
- [ ] No obvious technology choices (no alternatives)
- [ ] No easily reversible decisions
- [ ] No team-local decisions with no broader impact
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-ADR-NO-004"
domain = "ARCH"
title = "No Incomplete Decisions"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "Complete the ADR before publishing, or use PROPOSED status"
```
```markdown
- [ ] No "TBD" in critical sections
- [ ] No missing context
- [ ] No missing options analysis
- [ ] No missing rationale
- [ ] No missing consequences
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
