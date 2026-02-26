# PRD Blueprint
<!-- 
  Blueprint for Product Requirements Documents (PRD).
  
  This file is the single source of truth for:
  - template.md generation (from @cpt:heading + @cpt:prompt markers)
  - example.md generation (from @cpt:heading examples + @cpt:example markers)
  - rules.md generation (from @cpt:rules + @cpt:rule markers)
  - checklist.md generation (from @cpt:checklist + @cpt:check markers)
  - constraints.toml contributions (from @cpt:heading + @cpt:id markers)
  
  All text between markers is ignored by the generator — it serves as
  human-readable documentation for anyone editing this blueprint.
  
  Based on: ISO/IEC/IEEE 29148:2018, ISO/IEC 25010:2011
-->

## Metadata

`@cpt:blueprint`
```toml
version = 1
kit = "sdlc"
artifact = "PRD"
codebase = false
```
`@/cpt:blueprint`

## Skill Integration

Commands and workflows exposed to AI agents for PRD operations.

`@cpt:skill`
```markdown
### PRD Commands
- `cypilot validate --artifact <PRD.md>` — validate PRD structure and IDs
- `cypilot list-ids --kind fr` — list all functional requirements
- `cypilot list-ids --kind actor` — list all actors
- `cypilot where-defined <id>` — find where a PRD ID is defined
- `cypilot where-used <id>` — find where a PRD ID is referenced downstream
### PRD Workflows
- **Generate PRD**: create a new PRD from template with guided prompts per section
- **Analyze PRD**: validate structure (deterministic) then semantic quality (checklist-based)
```
`@/cpt:skill`

---

## Rules Definition

Rules are organized into sections that map to the generated `rules.md`.

### Rules Skeleton

`@cpt:rules`
```toml
[prerequisites]
sections = ["load_dependencies"]

[requirements]
sections = ["structural", "versioning", "semantic", "traceability", "constraints"]

[tasks]
phases = ["setup", "content_creation", "ids_and_structure", "quality_check"]

[validation]
sections = ["structural", "semantic"]

[error_handling]
sections = ["missing_dependencies", "missing_adapter", "escalation"]

[next_steps]
sections = ["options"]
```
`@/cpt:rules`

### Prerequisites

Dependencies that must be loaded before working with a PRD artifact.

`@cpt:rule`
```toml
kind = "prerequisites"
section = "load_dependencies"
```
```markdown
- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read adapter config for project ID prefix
- [ ] Load `{cypilot_path}/.core/architecture/specs/traceability.md` for ID formats
- [ ] Load `{cypilot_path}/config/kits/sdlc/constraints.toml` for kit-level constraints
- [ ] Load `{cypilot_path}/.core/architecture/specs/kit/constraints.md` for constraints specification
```
`@/cpt:rule`

### Requirements

#### Structural Requirements

`@cpt:rule`
```toml
kind = "requirements"
section = "structural"
```
```markdown
- [ ] PRD follows `template.md` structure
- [ ] Artifact frontmatter (optional): use `cpt:` format for document metadata
- [ ] All required sections present and non-empty
- [ ] All IDs follow `cpt-{hierarchy-prefix}-{kind}-{slug}` convention
- [ ] All capabilities have priority markers (`p1`–`p9`)
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document
```
`@/cpt:rule`

#### Versioning Rules

`@cpt:rule`
```toml
kind = "requirements"
section = "versioning"
```
```markdown
- [ ] When editing existing PRD: increment version in frontmatter
- [ ] When changing capability definition: add `-v{N}` suffix to ID or increment existing version
  - Format: `cpt-{hierarchy-prefix}-cap-{slug}-v2`, `cpt-{hierarchy-prefix}-cap-{slug}-v3`, etc.
- [ ] Keep changelog of significant changes
```
`@/cpt:rule`

#### Traceability

`@cpt:rule`
```toml
kind = "requirements"
section = "traceability"
```
```markdown
- [ ] Capabilities traced through: PRD → DESIGN → DECOMPOSITION → FEATURE → CODE
- [ ] When capability fully implemented (all specs IMPLEMENTED) → mark capability `[x]`
- [ ] When all capabilities `[x]` → product version complete
```
`@/cpt:rule`

#### Constraints Integration

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
- [ ] Automated validation: `cypilot validate` enforces identifier reference rules, headings scoping, and checkbox consistency
```
`@/cpt:rule`

### Task Phases

#### Setup

`@cpt:rule`
```toml
kind = "tasks"
section = "setup"
```
```markdown
- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `example.md` for reference style
- [ ] Read adapter config for project ID prefix
```
`@/cpt:rule`

#### Content Creation

`@cpt:rule`
```toml
kind = "tasks"
section = "content_creation"
```
```markdown
- [ ] Write each section guided by blueprint prompts and examples
- [ ] Use example as reference for content depth:
  - Vision → how example explains purpose (BIZ-PRD-001)
  - Actors → how example defines actors (BIZ-PRD-002)
  - Capabilities → how example structures caps (BIZ-PRD-003)
  - Use Cases → how example documents journeys (BIZ-PRD-004)
  - NFRs + Exclusions → how example handles N/A categories (DOC-PRD-001)
  - Non-Goals & Risks → how example scopes product (BIZ-PRD-008)
  - Assumptions → how example states assumptions (BIZ-PRD-007)
```
`@/cpt:rule`

#### IDs & Structure

`@cpt:rule`
```toml
kind = "tasks"
section = "ids_and_structure"
```
```markdown
- [ ] Generate actor IDs: `cpt-{hierarchy-prefix}-actor-{slug}`
- [ ] Generate capability IDs: `cpt-{hierarchy-prefix}-fr-{slug}`
- [ ] Assign priorities based on business impact
- [ ] Verify uniqueness with `cypilot list-ids`
```
`@/cpt:rule`

#### Quality Check

`@cpt:rule`
```toml
kind = "tasks"
section = "quality_check"
```
```markdown
- [ ] Compare output quality to `examples/example.md`
- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations
```
`@/cpt:rule`

### Validation

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
  - Priority markers present
  - No placeholders
  - No duplicate IDs
```
`@/cpt:rule`

#### Semantic Validation

`@cpt:rule`
```toml
kind = "validation"
section = "semantic"
```
```markdown
- [ ] Read `checklist.md` in full
- [ ] For each MUST HAVE item: check if requirement is met
  - If not met: report as violation with severity
  - If not applicable: verify explicit "N/A" with reasoning
- [ ] For each MUST NOT HAVE item: scan document for violations
- [ ] Compare content depth to `examples/example.md`
  - Flag significant quality gaps
```
`@/cpt:rule`

### Error Handling

#### Missing Dependencies

`@cpt:rule`
```toml
kind = "error_handling"
section = "missing_dependencies"
```
```markdown
- [ ] If `template.md` cannot be loaded → STOP, cannot proceed without template
- [ ] If `checklist.md` cannot be loaded → warn user, skip semantic validation
- [ ] If `examples/example.md` cannot be loaded → warn user, continue with reduced guidance
```
`@/cpt:rule`

#### Missing Adapter

`@cpt:rule`
```toml
kind = "error_handling"
section = "missing_adapter"
```
```markdown
- [ ] If adapter config unavailable → use default project prefix `cpt-{dirname}`
- [ ] Ask user to confirm or provide custom prefix
```
`@/cpt:rule`

#### Escalation

`@cpt:rule`
```toml
kind = "error_handling"
section = "escalation"
```
```markdown
- [ ] Ask user when cannot determine appropriate actor roles for the domain
- [ ] Ask user when business requirements are unclear or contradictory
- [ ] Ask user when success criteria cannot be quantified without domain knowledge
- [ ] Ask user when uncertain whether a category is truly N/A or just missing
```
`@/cpt:rule`

### Next Steps

Recommended actions after completing a PRD.

`@cpt:rule`
```toml
kind = "next_steps"
section = "options"
```
```markdown
- [ ] PRD complete → `/cypilot-generate DESIGN` — create technical design
- [ ] Need architecture decision → `/cypilot-generate ADR` — document key decision
- [ ] PRD needs revision → continue editing PRD
- [ ] Want checklist review only → `/cypilot-analyze semantic` — semantic validation
```
`@/cpt:rule`

---

## Checklist Definition

Severity levels, review domains, and individual check items for PRD quality.

### Checklist Skeleton

`@cpt:checklist`
```toml
[severity]
# Descending order; each check item assigns exactly one
levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
# CRITICAL — blocks downstream work
# HIGH     — fix before approval
# MEDIUM   — fix when feasible
# LOW      — optional improvement

[review]
# Recommended review order (subset of domains)
priority = ["BIZ", "ARCH", "SEC", "TEST"]

# Domain order below defines section sequence in generated checklist.md
# Each @cpt:check references a domain by its `abbr`

[[domain]]
abbr = "BIZ"
name = "Business"
standards = ["ISO/IEC/IEEE 29148:2018 §6.2 (StRS), §6.4 (SRS)"]

[[domain]]
abbr = "ARCH"
name = "Architecture"
standards = ["ISO/IEC 25010:2023 §4.2.7–8", "ISO/IEC/IEEE 29148 §6.3"]

[[domain]]
abbr = "SEC"
name = "Security"
standards = ["ISO/IEC 25010:2023 §4.2.6", "OWASP ASVS 5.0", "NIST SP 800-53 Rev.5", "ISO/IEC 27001:2022"]

[[domain]]
abbr = "SAFE"
name = "Safety"
standards = ["ISO/IEC 25010:2023 §4.2.9"]

[[domain]]
abbr = "TEST"
name = "Testing"
standards = ["ISO/IEC/IEEE 29119", "ISO/IEC/IEEE 29148 §5.2.8"]

[[domain]]
abbr = "PERF"
name = "Performance"
standards = ["ISO/IEC 25010:2023 §4.2.2"]

[[domain]]
abbr = "REL"
name = "Reliability"
standards = ["ISO/IEC 25010:2023 §4.2.5", "ISO 22301:2019", "SOC 2 Availability"]

[[domain]]
abbr = "UX"
name = "Usability"
standards = ["ISO/IEC 25010:2023 §4.2.4", "ISO 9241-11:2018", "ISO 9241-210:2019", "WCAG 2.2"]

[[domain]]
abbr = "DATA"
name = "Data"
standards = ["GDPR", "ISO/IEC 25012"]

[[domain]]
abbr = "INT"
name = "Integration"
standards = ["ISO/IEC 25010:2023 §4.2.3"]

[[domain]]
abbr = "COMPL"
name = "Compliance"
standards = ["GDPR", "HIPAA", "PCI DSS 4.0.1", "SOC 2 TSC"]

[[domain]]
abbr = "MAINT"
name = "Maintainability"
standards = ["ISO/IEC 25010:2023 §4.2.7"]

[[domain]]
abbr = "OPS"
name = "Operations"
standards = ["ISO 22301:2019", "NIST 800-53 CM/CP"]

[[domain]]
abbr = "DOC"
name = "Documentation"
standards = []
```
`@/cpt:checklist`

### Business Checks (BIZ)

Product vision, actors, scope, use cases, acceptance criteria.

`@cpt:check`
```toml
id = "BIZ-PRD-001"
domain = "BIZ"
title = "Vision Clarity"
severity = "CRITICAL"
ref = "ISO/IEC/IEEE 29148 §5.2.5 (Stakeholder requirements definition)"
kind = "must_have"
```
```markdown
- [ ] Purpose statement explains WHY the product exists
- [ ] Target users clearly identified with specificity (not just "users")
- [ ] Key problems solved are concrete and measurable
- [ ] Success criteria are quantifiable (numbers, percentages, timeframes)
- [ ] Capabilities list covers core value propositions
- [ ] Business context is clear without requiring insider knowledge
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-PRD-002"
domain = "BIZ"
title = "Stakeholder Coverage"
severity = "HIGH"
ref = "ISO/IEC/IEEE 29148 §6.2.2 (Stakeholders), ISO 9241-210 §4"
kind = "must_have"
```
```markdown
- [ ] All relevant user personas represented as actors
- [ ] Business sponsors' needs reflected in requirements
- [ ] End-user needs clearly articulated
- [ ] Organizational constraints acknowledged
- [ ] Market positioning context provided (if applicable)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-PRD-003"
domain = "BIZ"
title = "Requirements Completeness"
severity = "CRITICAL"
ref = "ISO/IEC/IEEE 29148 §5.2.6, §6.4.3"
kind = "must_have"
```
```markdown
- [ ] All business-critical capabilities have corresponding functional requirements
- [ ] Requirements trace back to stated problems
- [ ] No capability is mentioned without a supporting requirement
- [ ] Requirements are prioritized (implicit or explicit)
- [ ] Dependencies between requirements are identified
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-PRD-004"
domain = "BIZ"
title = "Use Case Coverage"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] All primary user journeys represented as use cases
- [ ] Critical business workflows documented
- [ ] Edge cases and exception flows considered
- [ ] Use cases cover the "happy path" and error scenarios
- [ ] Use cases are realistic and actionable
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-PRD-005"
domain = "BIZ"
title = "Success Metrics"
severity = "HIGH"
ref = "ISO/IEC/IEEE 29148 §6.2.4, ISO 9241-11 §5"
kind = "must_have"
```
```markdown
- [ ] Success criteria are SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
- [ ] Metrics can actually be measured with available data
- [ ] Baseline values established where possible
- [ ] Target values are realistic
- [ ] Timeframes for achieving targets specified
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-PRD-006"
domain = "BIZ"
title = "Terminology & Definitions"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Key domain terms are defined (glossary or inline)
- [ ] Acronyms are expanded on first use
- [ ] Terms are used consistently (no synonyms that change meaning)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-PRD-007"
domain = "BIZ"
title = "Assumptions & Open Questions"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Key assumptions are explicitly stated
- [ ] Open questions are listed with owners and desired resolution time
- [ ] Dependencies on external teams/vendors are called out
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-PRD-008"
domain = "BIZ"
title = "Risks & Non-Goals"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Major risks/uncertainties are listed
- [ ] Explicit non-goals/out-of-scope items are documented
```
`@/cpt:check`

### Architecture Checks (ARCH)

FR/NFR quality, measurability, and design-readiness.

`@cpt:check`
```toml
id = "ARCH-PRD-001"
domain = "ARCH"
title = "Scope Boundaries"
severity = "CRITICAL"
ref = "ISO/IEC/IEEE 29148 §6.3.2, §6.3.4"
kind = "must_have"
```
```markdown
- [ ] System boundaries are clear (what's in vs out of scope)
- [ ] Integration points with external systems identified
- [ ] Organizational boundaries respected
- [ ] Technology constraints acknowledged at high level
- [ ] No implementation decisions embedded in requirements
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-PRD-002"
domain = "ARCH"
title = "Modularity Enablement"
severity = "MEDIUM"
ref = "ISO/IEC 25010:2023 §4.2.7.2"
kind = "must_have"
```
```markdown
- [ ] Requirements are decomposable into specs
- [ ] No monolithic "do everything" requirements
- [ ] Clear separation of concerns in requirement grouping
- [ ] Requirements support incremental delivery
- [ ] Dependencies don't create circular coupling
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-PRD-003"
domain = "ARCH"
title = "Scalability Considerations"
severity = "MEDIUM"
ref = "ISO/IEC 25010:2023 §4.2.8.4"
kind = "must_have"
```
```markdown
- [ ] User volume expectations stated (current and projected)
- [ ] Data volume expectations stated (current and projected)
- [ ] Geographic distribution requirements captured
- [ ] Growth scenarios considered in requirements
- [ ] Performance expectations stated at business level
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-PRD-004"
domain = "ARCH"
title = "System Actor Clarity"
severity = "HIGH"
ref = "ISO/IEC/IEEE 29148 §6.3.4"
kind = "must_have"
```
```markdown
- [ ] System actors represent real external systems
- [ ] System actor interfaces are clear
- [ ] Integration direction specified (inbound/outbound/bidirectional)
- [ ] System actor availability requirements stated
- [ ] Data exchange expectations documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-PRD-005"
domain = "ARCH"
title = "Compatibility Requirements"
severity = "MEDIUM"
ref = "ISO/IEC 25010:2023 §4.2.3"
kind = "must_have"
```
```markdown
- [ ] Co-existence requirements documented (operation alongside other products without adverse impact)
- [ ] Interoperability requirements stated (ability to exchange information with other systems)
- [ ] Data format compatibility requirements captured (file formats, protocols)
- [ ] Hardware/software environment compatibility stated
- [ ] Backward compatibility requirements documented (if applicable)
```
`@/cpt:check`

### Security Checks (SEC)

`@cpt:check`
```toml
id = "SEC-PRD-001"
domain = "SEC"
title = "Authentication Requirements"
severity = "CRITICAL"
ref = "OWASP ASVS V2, RFC 6749, NIST 800-53 IA"
kind = "must_have"
applicable_when = "Enterprise product, multi-tenant"
not_applicable_when = "Single-user tool, local-only"
```
```markdown
- [ ] User authentication needs stated
- [ ] Multi-factor requirements captured (if applicable)
- [ ] SSO/federation requirements documented
- [ ] Session management expectations stated
- [ ] Password/credential policies referenced
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-PRD-002"
domain = "SEC"
title = "Authorization Requirements"
severity = "CRITICAL"
ref = "OWASP ASVS V4, NIST 800-53 AC, ISO 27001 A.9"
kind = "must_have"
```
```markdown
- [ ] Role-based access clearly defined through actors
- [ ] Permission levels distinguished between actors
- [ ] Data access boundaries specified per actor
- [ ] Administrative vs user roles separated
- [ ] Delegation/impersonation needs captured
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-PRD-003"
domain = "SEC"
title = "Data Classification"
severity = "HIGH"
ref = "ISO/IEC 25010:2023 §4.2.6.2, NIST 800-53 SC, GDPR Art. 9"
kind = "must_have"
```
```markdown
- [ ] Sensitive data types identified
- [ ] PII handling requirements stated
- [ ] Data retention expectations documented
- [ ] Data deletion/anonymization needs captured
- [ ] Cross-border data transfer considerations noted
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-PRD-004"
domain = "SEC"
title = "Audit Requirements"
severity = "MEDIUM"
ref = "ISO/IEC 25010:2023 §4.2.6.5, NIST 800-53 AU, SOC 2 CC6/CC7"
kind = "must_have"
```
```markdown
- [ ] Audit logging needs identified
- [ ] User action tracking requirements stated
- [ ] Compliance reporting needs captured
- [ ] Forensic investigation support requirements noted
- [ ] Non-repudiation requirements documented (ISO 25010 §4.2.6.6)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-PRD-005"
domain = "SEC"
title = "Privacy by Design"
severity = "HIGH"
ref = "GDPR Article 25, EDPB Guidelines 4/2019"
kind = "must_have"
applicable_when = "Handles EU personal data, PII"
not_applicable_when = "No personal data processing"
```
```markdown
- [ ] Privacy requirements embedded from project inception (not retrofitted)
- [ ] Data minimization principle stated (collect only what is necessary)
- [ ] Purpose limitation documented (data used only for stated purposes)
- [ ] Storage limitation requirements captured (retention periods defined)
- [ ] Privacy by default requirements stated (most privacy-protective settings as default)
- [ ] Pseudonymization/anonymization requirements documented where applicable
```
`@/cpt:check`

### Safety Checks (SAFE)

`@cpt:check`
```toml
id = "SAFE-PRD-001"
domain = "SAFE"
title = "Operational Safety Requirements"
severity = "CRITICAL"
ref = "ISO/IEC 25010:2023 §4.2.9.1, §4.2.9.2"
kind = "must_have"
applicable_when = "Could harm people/property/environment, medical, vehicles, industrial"
not_applicable_when = "Pure information system, no physical interaction"
```
```markdown
- [ ] Safety-critical operations identified
- [ ] Operational constraints for safe operation documented
- [ ] Potential hazards identified and documented
- [ ] Risk levels assessed for identified hazards
- [ ] User actions that could lead to harm documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SAFE-PRD-002"
domain = "SAFE"
title = "Fail-Safe and Hazard Prevention"
severity = "CRITICAL"
ref = "ISO/IEC 25010:2023 §4.2.9.3–5"
kind = "must_have"
applicable_when = "Could harm people/property/environment, medical, vehicles, industrial"
not_applicable_when = "Pure information system, no physical interaction"
```
```markdown
- [ ] Fail-safe behavior requirements documented (safe state on failure)
- [ ] Hazard warning requirements stated (alerts for dangerous conditions)
- [ ] Emergency shutdown/stop requirements captured (if applicable)
- [ ] Safe integration requirements with other systems documented
- [ ] Human override capabilities defined where needed
```
`@/cpt:check`

### Testing Checks (TEST)

`@cpt:check`
```toml
id = "TEST-PRD-001"
domain = "TEST"
title = "Acceptance Criteria"
severity = "HIGH"
ref = "ISO/IEC/IEEE 29148 §5.2.8, ISO/IEC/IEEE 29119-1 §4"
kind = "must_have"
```
```markdown
- [ ] Each functional requirement has verifiable acceptance criteria
- [ ] Use cases define expected outcomes
- [ ] NFRs have measurable thresholds
- [ ] Edge cases are testable
- [ ] Negative test cases implied
```
`@/cpt:check`

`@cpt:check`
```toml
id = "TEST-PRD-002"
domain = "TEST"
title = "Testability"
severity = "MEDIUM"
ref = "ISO/IEC/IEEE 29148 §5.2.5, ISO/IEC 25010:2023 §4.2.7.4"
kind = "must_have"
```
```markdown
- [ ] Requirements are unambiguous enough to test (ISO 29148 §5.2.5)
- [ ] Requirements don't use vague terms ("fast", "easy", "intuitive")
- [ ] Requirements specify concrete behaviors
- [ ] Requirements avoid compound statements (multiple "and"s)
- [ ] Requirements can be independently verified
```
`@/cpt:check`

### Performance Checks (PERF)

`@cpt:check`
```toml
id = "PERF-PRD-001"
domain = "PERF"
title = "Response Time Expectations"
severity = "HIGH"
ref = "ISO/IEC 25010:2023 §4.2.2.2"
kind = "must_have"
```
```markdown
- [ ] User-facing response time expectations stated
- [ ] Batch processing time expectations stated
- [ ] Report generation time expectations stated
- [ ] Search/query performance expectations stated
- [ ] Expectations are realistic for the problem domain
```
`@/cpt:check`

`@cpt:check`
```toml
id = "PERF-PRD-002"
domain = "PERF"
title = "Throughput Requirements"
severity = "MEDIUM"
ref = "ISO/IEC 25010:2023 §4.2.2.3–4"
kind = "must_have"
```
```markdown
- [ ] Concurrent user expectations documented
- [ ] Transaction volume expectations stated
- [ ] Peak load scenarios identified
- [ ] Sustained load expectations documented
- [ ] Growth projections factored in
```
`@/cpt:check`

`@cpt:check`
```toml
id = "PERF-PRD-003"
domain = "PERF"
title = "Capacity Planning Inputs"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Data volume projections provided
- [ ] User base growth projections provided
- [ ] Seasonal/cyclical patterns identified
- [ ] Burst scenarios documented
- [ ] Historical growth data referenced (if available)
```
`@/cpt:check`

### Reliability Checks (REL)

`@cpt:check`
```toml
id = "REL-PRD-001"
domain = "REL"
title = "Availability Requirements"
severity = "HIGH"
ref = "ISO/IEC 25010:2023 §4.2.5.2, SOC 2 A1.1"
kind = "must_have"
```
```markdown
- [ ] Uptime expectations stated (e.g., 99.9%)
- [ ] Maintenance window expectations documented
- [ ] Business hours vs 24/7 requirements clear
- [ ] Geographic availability requirements stated
- [ ] Degraded mode expectations documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "REL-PRD-002"
domain = "REL"
title = "Recovery Requirements"
severity = "HIGH"
ref = "ISO/IEC 25010:2023 §4.2.5.4, ISO 22301:2019 §8.4, NIST 800-53 CP"
kind = "must_have"
```
```markdown
- [ ] Data loss tolerance stated (RPO — Recovery Point Objective)
- [ ] Downtime tolerance stated (RTO — Recovery Time Objective)
- [ ] Backup requirements documented
- [ ] Disaster recovery expectations stated
- [ ] Business continuity requirements captured
```
`@/cpt:check`

`@cpt:check`
```toml
id = "REL-PRD-003"
domain = "REL"
title = "Error Handling Expectations"
severity = "MEDIUM"
ref = "ISO/IEC 25010:2023 §4.2.5.3"
kind = "must_have"
```
```markdown
- [ ] User error handling expectations stated
- [ ] System error communication requirements documented
- [ ] Graceful degradation expectations captured
- [ ] Retry/recovery user experience documented
- [ ] Support escalation paths identified
```
`@/cpt:check`

### Usability Checks (UX)

`@cpt:check`
```toml
id = "UX-PRD-001"
domain = "UX"
title = "User Experience Goals"
severity = "HIGH"
ref = "ISO 9241-11 §5, ISO/IEC 25010:2023 §4.2.4"
kind = "must_have"
```
```markdown
- [ ] Target user skill level defined
- [ ] Learning curve expectations stated (ISO 9241-11: efficiency)
- [ ] Efficiency goals for expert users documented
- [ ] Discoverability requirements for new users stated (ISO 25010 §4.2.4.3 Learnability)
- [ ] User satisfaction targets defined (ISO 9241-11: satisfaction)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "UX-PRD-002"
domain = "UX"
title = "Accessibility Requirements"
severity = "HIGH"
ref = "WCAG 2.2, ISO/IEC 25010:2023 §4.2.4.7, EN 301 549"
kind = "must_have"
applicable_when = "Public-facing, government, enterprise"
not_applicable_when = "Internal tool with known user base"
```
```markdown
- [ ] Accessibility standards referenced (WCAG 2.2 level — typically AA)
- [ ] Assistive technology support requirements stated
- [ ] Keyboard navigation requirements documented (WCAG 2.1.1)
- [ ] Screen reader compatibility requirements stated (WCAG 4.1.2)
- [ ] Color/contrast requirements noted (WCAG 1.4.3, 1.4.11)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "UX-PRD-003"
domain = "UX"
title = "Internationalization Requirements"
severity = "MEDIUM"
kind = "must_have"
applicable_when = "Multi-region deployment planned"
not_applicable_when = "Single-locale deployment"
```
```markdown
- [ ] Supported languages listed
- [ ] Localization requirements documented
- [ ] Regional format requirements stated (dates, numbers, currency)
- [ ] RTL language support requirements noted
- [ ] Cultural considerations documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "UX-PRD-004"
domain = "UX"
title = "Device/Platform Requirements"
severity = "MEDIUM"
ref = "ISO/IEC 25010:2023 §4.2.8"
kind = "must_have"
applicable_when = "Mobile app, unreliable network"
not_applicable_when = "Server-side tool, always-connected"
```
```markdown
- [ ] Supported platforms listed (web, mobile, desktop)
- [ ] Browser requirements stated
- [ ] Mobile device requirements documented
- [ ] Offline capability requirements stated
- [ ] Responsive design requirements documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "UX-PRD-005"
domain = "UX"
title = "Inclusivity Requirements"
severity = "MEDIUM"
ref = "ISO/IEC 25010:2023 §4.2.4.8"
kind = "must_have"
applicable_when = "Diverse user base, public-facing"
not_applicable_when = "Narrow technical audience, internal tool"
```
```markdown
- [ ] Diverse user populations considered (age, culture, language, ability)
- [ ] Cognitive accessibility requirements documented (beyond WCAG)
- [ ] Support for users with temporary situational limitations considered
- [ ] Cultural sensitivity requirements stated (if applicable)
- [ ] Design for neurodiverse users considered (if applicable)
```
`@/cpt:check`

### Data Checks (DATA)

`@cpt:check`
```toml
id = "DATA-PRD-001"
domain = "DATA"
title = "Data Ownership"
severity = "HIGH"
ref = "GDPR Art. 4, Art. 26, Art. 28"
kind = "must_have"
```
```markdown
- [ ] Data ownership clearly defined
- [ ] Data stewardship responsibilities identified (controller vs processor)
- [ ] Data sharing expectations documented
- [ ] Third-party data usage requirements stated (GDPR Art. 28)
- [ ] User-generated content ownership defined
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DATA-PRD-002"
domain = "DATA"
title = "Data Quality Requirements"
severity = "MEDIUM"
ref = "ISO/IEC 25012, GDPR Art. 5(1)(d)"
kind = "must_have"
```
```markdown
- [ ] Data accuracy requirements stated (ISO 25012 §4.2.1)
- [ ] Data completeness requirements documented (ISO 25012 §4.2.2)
- [ ] Data freshness requirements captured (ISO 25012 §4.2.8 Currentness)
- [ ] Data validation requirements stated
- [ ] Data cleansing requirements documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DATA-PRD-003"
domain = "DATA"
title = "Data Lifecycle"
severity = "MEDIUM"
ref = "GDPR Art. 5(1)(e), Art. 17"
kind = "must_have"
```
```markdown
- [ ] Data retention requirements stated (GDPR storage limitation)
- [ ] Data archival requirements documented
- [ ] Data purging requirements captured (right to erasure)
- [ ] Data migration requirements stated
- [ ] Historical data access requirements documented
```
`@/cpt:check`

### Integration Checks (INT)

`@cpt:check`
```toml
id = "INT-PRD-001"
domain = "INT"
title = "External System Integration"
severity = "HIGH"
ref = "ISO/IEC 25010:2023 §4.2.3.2, ISO/IEC/IEEE 29148 §6.3.4"
kind = "must_have"
```
```markdown
- [ ] Required integrations listed
- [ ] Integration direction specified
- [ ] Data exchange requirements documented
- [ ] Integration availability requirements stated
- [ ] Fallback requirements for integration failures documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "INT-PRD-002"
domain = "INT"
title = "API Requirements"
severity = "MEDIUM"
ref = "OpenAPI Specification, RFC 6749"
kind = "must_have"
```
```markdown
- [ ] API exposure requirements stated
- [ ] API consumer requirements documented
- [ ] API versioning requirements stated
- [ ] Rate limiting expectations documented
- [ ] API documentation requirements stated (OpenAPI/Swagger)
```
`@/cpt:check`

### Compliance Checks (COMPL)

`@cpt:check`
```toml
id = "COMPL-PRD-001"
domain = "COMPL"
title = "Regulatory Requirements"
severity = "CRITICAL"
ref = "GDPR, HIPAA, PCI DSS, SOX"
kind = "must_have"
applicable_when = "Handles PII, financial data, healthcare"
not_applicable_when = "Internal dev tool, no user data"
```
```markdown
- [ ] Applicable regulations identified (GDPR, HIPAA, SOX, PCI DSS, etc.)
- [ ] Compliance certification requirements stated
- [ ] Audit requirements documented
- [ ] Reporting requirements captured
- [ ] Data sovereignty requirements stated (GDPR Art. 44-49)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "COMPL-PRD-002"
domain = "COMPL"
title = "Industry Standards"
severity = "MEDIUM"
ref = "ISO 27001, ISO 22301, SOC 2, ISO 9001"
kind = "must_have"
```
```markdown
- [ ] Industry standards referenced (ISO, NIST, OWASP, etc.)
- [ ] Best practice frameworks identified
- [ ] Certification requirements stated (ISO 27001, SOC 2, etc.)
- [ ] Interoperability standards documented
- [ ] Security standards referenced (OWASP ASVS, NIST 800-53)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "COMPL-PRD-003"
domain = "COMPL"
title = "Legal Requirements"
severity = "HIGH"
ref = "GDPR Art. 12-23, Art. 6-7"
kind = "must_have"
```
```markdown
- [ ] Terms of service requirements stated
- [ ] Privacy policy requirements documented
- [ ] Consent management requirements captured (GDPR Art. 7)
- [ ] Data subject rights requirements stated (access, rectification, erasure, portability)
- [ ] Contractual obligations documented
```
`@/cpt:check`

### Maintainability Checks (MAINT)

`@cpt:check`
```toml
id = "MAINT-PRD-001"
domain = "MAINT"
title = "Documentation Requirements"
severity = "MEDIUM"
ref = "ISO/IEC/IEEE 29148 §6.6"
kind = "must_have"
```
```markdown
- [ ] User documentation requirements stated
- [ ] Admin documentation requirements stated
- [ ] API documentation requirements stated
- [ ] Training material requirements documented
- [ ] Help system requirements captured
```
`@/cpt:check`

`@cpt:check`
```toml
id = "MAINT-PRD-002"
domain = "MAINT"
title = "Support Requirements"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Support tier expectations documented
- [ ] SLA requirements stated
- [ ] Self-service support requirements captured
- [ ] Diagnostic capability requirements stated
- [ ] Troubleshooting support requirements documented
```
`@/cpt:check`

### Operations Checks (OPS)

`@cpt:check`
```toml
id = "OPS-PRD-001"
domain = "OPS"
title = "Deployment Requirements"
severity = "MEDIUM"
ref = "NIST 800-53 CM"
kind = "must_have"
```
```markdown
- [ ] Deployment environment requirements stated
- [ ] Release frequency expectations documented
- [ ] Rollback requirements captured
- [ ] Blue/green or canary requirements stated
- [ ] Environment parity requirements documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "OPS-PRD-002"
domain = "OPS"
title = "Monitoring Requirements"
severity = "MEDIUM"
ref = "NIST 800-53 AU, SI"
kind = "must_have"
```
```markdown
- [ ] Alerting requirements stated
- [ ] Dashboard requirements documented
- [ ] Log retention requirements captured
- [ ] Incident response requirements stated (NIST 800-53 IR)
- [ ] Capacity monitoring requirements documented
```
`@/cpt:check`

### Documentation Checks (DOC)

`@cpt:check`
```toml
id = "DOC-PRD-001"
domain = "DOC"
title = "Explicit Non-Applicability"
severity = "CRITICAL"
kind = "must_have"
```
```markdown
- [ ] If a section or requirement is intentionally omitted, it is explicitly stated (e.g., "Not applicable because...")
- [ ] No silent omissions — every major checklist area is either present or has a documented reason for absence
- [ ] Reviewer can distinguish "author considered and excluded" from "author forgot"
```
`@/cpt:check`

### Anti-Pattern Checks (must_not_have)

Content that does NOT belong in a PRD.

`@cpt:check`
```toml
id = "ARCH-PRD-NO-001"
domain = "ARCH"
title = "No Technical Implementation Details"
severity = "CRITICAL"
kind = "must_not_have"
belongs_to = "DESIGN"
```
```markdown
- [ ] No database schema definitions
- [ ] No API endpoint specifications
- [ ] No technology stack decisions
- [ ] No code snippets or pseudocode
- [ ] No infrastructure specifications
- [ ] No framework/library choices
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-PRD-NO-002"
domain = "ARCH"
title = "No Architectural Decisions"
severity = "CRITICAL"
kind = "must_not_have"
belongs_to = "ADR"
```
```markdown
- [ ] No microservices vs monolith decisions
- [ ] No database choice justifications
- [ ] No cloud provider selections
- [ ] No architectural pattern discussions
- [ ] No component decomposition
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-PRD-NO-001"
domain = "BIZ"
title = "No Implementation Tasks"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "Project management tools or DESIGN"
```
```markdown
- [ ] No sprint/iteration plans
- [ ] No task breakdowns
- [ ] No effort estimates
- [ ] No developer assignments
- [ ] No implementation timelines
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-PRD-NO-002"
domain = "BIZ"
title = "No Spec-Level Design"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "DESIGN"
```
```markdown
- [ ] No detailed user flows
- [ ] No wireframes or UI specifications
- [ ] No algorithm descriptions
- [ ] No state machine definitions
- [ ] No detailed error handling logic
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DATA-PRD-NO-001"
domain = "DATA"
title = "No Data Schema Definitions"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "DESIGN (domain model and schemas)"
```
```markdown
- [ ] No entity-relationship diagrams
- [ ] No table definitions
- [ ] No JSON schema specifications
- [ ] No data type specifications
- [ ] No field-level constraints
```
`@/cpt:check`

`@cpt:check`
```toml
id = "INT-PRD-NO-001"
domain = "INT"
title = "No API Specifications"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "API contract documentation (OpenAPI) or DESIGN"
```
```markdown
- [ ] No REST endpoint definitions
- [ ] No request/response schemas
- [ ] No HTTP method specifications
- [ ] No authentication header specifications
- [ ] No error response formats
```
`@/cpt:check`

`@cpt:check`
```toml
id = "TEST-PRD-NO-001"
domain = "TEST"
title = "No Test Cases"
severity = "MEDIUM"
kind = "must_not_have"
belongs_to = "Test plans, test suites, QA documentation"
```
```markdown
- [ ] No detailed test scripts
- [ ] No test data specifications
- [ ] No automation code
- [ ] No test environment specifications
```
`@/cpt:check`

`@cpt:check`
```toml
id = "OPS-PRD-NO-001"
domain = "OPS"
title = "No Infrastructure Specifications"
severity = "MEDIUM"
kind = "must_not_have"
belongs_to = "Infrastructure-as-code repositories or OPS documentation"
```
```markdown
- [ ] No server specifications
- [ ] No Kubernetes manifests
- [ ] No Docker configurations
- [ ] No CI/CD pipeline definitions
- [ ] No monitoring tool configurations
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-PRD-NO-001"
domain = "SEC"
title = "No Security Implementation Details"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "Security architecture documentation or ADRs"
```
```markdown
- [ ] No encryption algorithm specifications
- [ ] No key management procedures
- [ ] No firewall rules
- [ ] No security tool configurations
- [ ] No penetration test results
```
`@/cpt:check`

`@cpt:check`
```toml
id = "MAINT-PRD-NO-001"
domain = "MAINT"
title = "No Code-Level Documentation"
severity = "MEDIUM"
kind = "must_not_have"
belongs_to = "Source code, README files, developer documentation"
```
```markdown
- [ ] No code comments
- [ ] No function/class documentation
- [ ] No inline code examples
- [ ] No debugging instructions
```
`@/cpt:check`

---

## Template Structure

Headings, prompts, IDs, and examples that define the generated `template.md`
and `example.md` files. The PRD template covers: overview, actors, operational
context, scope, functional/non-functional requirements, interfaces, use cases,
acceptance criteria, dependencies, assumptions, and risks.

### Title (H1)

`@cpt:heading`
```toml
id = "prd-h1-title"
level = 1
required = true
numbered = false
multiple = false
pattern = "PRD\\s*[—–-]\\s*.+"
template = "PRD — {Module/Feature Name}"
prompt = "Title of product"
description = "PRD document title (H1)."
examples = ["# PRD — TaskFlow"]
```
`@/cpt:heading`

### Overview

`@cpt:heading`
```toml
id = "prd-overview"
level = 2
required = true
numbered = true
multiple = false
pattern = "Overview"
description = "High-level overview of the product and problem."
examples = ["## 1. Overview"]
```
`@/cpt:heading`

`@cpt:heading`
```toml
id = "prd-overview-purpose"
level = 3
required = true
numbered = true
multiple = false
pattern = "Purpose"
description = "Purpose of the PRD and the product."
examples = ["### 1.1 Purpose"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
{1-2 paragraphs: What is this system/module and what problem does it solve? What are the key features?}
```
`@/cpt:prompt`

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
- [ ] Purpose MUST be ≤ 2 paragraphs
- [ ] Purpose MUST NOT contain implementation details
- [ ] Vision MUST explain WHY the product exists
  - VALID: "Enables developers to validate artifacts against templates" (explains purpose)
  - INVALID: "A tool for Cypilot" (doesn't explain why it matters)
```
`@/cpt:rule`

`@cpt:example`
```markdown
TaskFlow is a lightweight task management system for small teams, enabling task creation, assignment, and progress tracking with real-time notifications.
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "prd-overview-background"
level = 3
required = true
numbered = true
multiple = false
pattern = "Background / Problem Statement"
description = "Background and problem statement."
examples = ["### 1.2 Background / Problem Statement"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
{2-3 paragraphs: Context, current pain points, why this capability is needed now.}
```
`@/cpt:prompt`

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
- [ ] Background MUST describe current state and specific pain points
- [ ] MUST include target users and key problems solved
```
`@/cpt:rule`

`@cpt:example`
```markdown
The system focuses on simplicity and speed, allowing teams to manage their daily work without the overhead of complex project management tools. TaskFlow bridges the gap between simple to-do lists and enterprise-grade solutions.

**Target Users**:

- Team leads managing sprints
- Developers tracking daily work
- Project managers monitoring progress

**Key Problems Solved**:

- Scattered task tracking across multiple tools
- Lack of visibility into team workload
- Missing deadline notifications
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "prd-overview-goals"
level = 3
required = true
numbered = true
multiple = false
pattern = "Goals (Business Outcomes)"
description = "Business outcomes and goals."
examples = ["### 1.3 Goals (Business Outcomes)"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
- {Goal 1: measurable business outcome}
- {Goal 2: measurable business outcome}
```
`@/cpt:prompt`

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
- [ ] All goals MUST be measurable with concrete targets
  - VALID: "Reduce validation time from 15min to <30s" (quantified with baseline)
  - INVALID: "Improve validation speed" (no baseline, no target)
- [ ] Success criteria MUST include baseline, target, and timeframe
```
`@/cpt:rule`

`@cpt:example`
```markdown
**Success Criteria**:

- Tasks created and assigned in under 30 seconds (Baseline: not measured; Target: v1.0)
- Real-time status updates visible to all team members within 2 seconds (Baseline: N/A; Target: v1.0)
- Overdue task alerts delivered within 1 minute of deadline (Baseline: N/A; Target: v1.0)

**Capabilities**:

- Manage team tasks and assignments
- Track task status and progress in real time
- Send notifications for deadlines and status changes
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "prd-overview-glossary"
level = 3
required = true
numbered = true
multiple = false
pattern = "Glossary"
description = "Definitions of key terms."
examples = ["### 1.4 Glossary"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
| Term | Definition |
|------|------------|
| {Term} | {Definition} |
```
`@/cpt:prompt`

`@cpt:example`
```markdown
| Term | Definition |
|------|------------|
| Task | A tracked work item owned by a team member with status and due date |
| Assignment | Mapping a task to an assignee (team member) |
| Notification | An alert emitted when tasks change or become overdue |
```
`@/cpt:example`

### Actors

Human and system actors that interact with the module.

`@cpt:heading`
```toml
id = "prd-actors"
level = 2
required = true
numbered = true
multiple = false
pattern = "Actors"
description = "Actors (human and system) that interact with the product."
examples = ["## 2. Actors"]
```
`@/cpt:heading`

`@cpt:id`
```toml
kind = "actor"
name = "Actor"
description = "An entity (human or system) that interacts with the product; used in PRD, and referenced by requirements/use cases."
required = false
task = false      # true = required | false = prohibited
priority = false  # true = required | false = prohibited
template = "cpt-{system}-actor-{slug}"
examples = ["cpt-cypilot-actor-ai-assistant", "cpt-ex-ovwa-actor-user", "cpt-ex-ovwa-actor-macos"]
to_code = false
headings = ["prd-actors"]
```
`@/cpt:id`

`@cpt:prompt`
```markdown
> **Note**: Stakeholder needs are managed at project/task level by steering committee. Document **actors** (users, systems) that interact with this module.
```
`@/cpt:prompt`

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
- [ ] All actors MUST be identified with specific roles (not just "users")
  - VALID: "Framework Developer", "Project Maintainer", "CI Pipeline"
  - INVALID: "Users", "Developers" (too generic)
- [ ] Each actor MUST have defined capabilities/needs
- [ ] Actor IDs follow: `cpt-{system}-actor-{slug}`
```
`@/cpt:rule`

`@cpt:heading`
```toml
id = "prd-actors-human"
level = 3
required = true
numbered = true
multiple = false
pattern = "Human Actors"
description = "Human actors."
examples = ["### 2.1 Human Actors"]
```
`@/cpt:heading`

`@cpt:heading`
```toml
id = "prd-actor-entry"
level = 4
required = true
numbered = false
# multiple = true|false  # allowed by default (can repeat)
template = "{Actor Name}"
description = "Individual human actor entry."
examples = ["#### Team Member", "#### Team Lead"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
**ID**: `cpt-{system}-actor-{slug}`

**Role**: {Description of what this actor does and their relationship to the system.}
**Needs**: {What this actor needs from the system.}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
**ID**: `cpt-ex-task-flow-actor-member`

**Role**: Creates tasks, updates progress, and collaborates on assignments.

#### Team Lead

**ID**: `cpt-ex-task-flow-actor-lead`

**Role**: Assigns tasks, sets priorities, and monitors team workload.
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "prd-actors-system"
level = 3
required = true
numbered = true
multiple = false
pattern = "System Actors"
description = "System and external actors."
examples = ["### 2.2 System Actors"]
```
`@/cpt:heading`

`@cpt:heading`
```toml
id = "prd-actor-system-entry"
level = 4
required = true
numbered = false
# multiple = true|false  # allowed by default (can repeat)
template = "{System Actor Name}"
description = "Individual system actor entry."
examples = ["#### Notification Service", "#### External Auth Provider"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
**ID**: `cpt-{system}-actor-{slug}`

**Role**: {Description of what this system actor does (external service, scheduler, etc.)}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
**ID**: `cpt-ex-task-flow-actor-notifier`

**Role**: Sends alerts for due dates, assignments, and status changes.
```
`@/cpt:example`

### Operational Concept & Environment

`@cpt:heading`
```toml
id = "prd-operational-concept"
level = 2
required = true
numbered = true
multiple = false
pattern = "Operational Concept & Environment"
description = "Operational concept and environment constraints."
examples = ["## 3. Operational Concept & Environment"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
> **Note**: Project-wide runtime, OS, architecture, lifecycle policy, and integration patterns defined in root PRD. Document only module-specific deviations here. **Delete this section if no special constraints.**
```
`@/cpt:prompt`

`@cpt:heading`
```toml
id = "prd-operational-concept-constraints"
level = 3
required = true
numbered = true
multiple = false
pattern = "Module-Specific Environment Constraints"
description = "Module-specific environment constraints beyond project defaults."
examples = ["### 3.1 Module-Specific Environment Constraints"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
{Only if this module has constraints beyond project defaults:}

- {Constraint 1, e.g., "Requires GPU acceleration for X"}
- {Constraint 2, e.g., "Incompatible with async runtime due to Y"}
- {Constraint 3, e.g., "Requires external dependency: Z library v2.0+"}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
None.
```
`@/cpt:example`

### Scope

In-scope and out-of-scope boundaries.

`@cpt:heading`
```toml
id = "prd-scope"
level = 2
required = true
numbered = true
multiple = false
pattern = "Scope"
description = "Scope of the product and release."
examples = ["## 4. Scope"]
```
`@/cpt:heading`

`@cpt:heading`
```toml
id = "prd-scope-in"
level = 3
required = true
numbered = true
multiple = false
pattern = "In Scope"
description = "In-scope items."
examples = ["### 4.1 In Scope"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
- {Capability or feature that IS included}
- {Another capability}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
- Task creation, assignment, and lifecycle tracking
- Real-time updates for task status changes
- Deadline notifications
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "prd-scope-out"
level = 3
required = true
numbered = true
multiple = false
pattern = "Out of Scope"
description = "Out-of-scope items."
examples = ["### 4.2 Out of Scope"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
- {Capability explicitly NOT included in this PRD}
- {Future consideration not addressed now}
```
`@/cpt:prompt`

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
- [ ] Non-goals MUST explicitly state what product does NOT do
```
`@/cpt:rule`

`@cpt:example`
```markdown
- Time tracking, billing, or invoicing
- Cross-organization collaboration
```
`@/cpt:example`

### Functional Requirements

`@cpt:heading`
```toml
id = "prd-fr"
level = 2
required = true
numbered = true
multiple = false
pattern = "Functional Requirements"
description = "Functional requirements section."
examples = ["## 5. Functional Requirements"]
```
`@/cpt:heading`

`@cpt:id`
```toml
kind = "fr"
name = "Functional Requirement"
description = "A testable statement of required system behavior (WHAT the system must do)."
required = true
# task = true|false    # optional by default
priority = true
template = "cpt-{system}-fr-{slug}"
examples = ["cpt-cypilot-fr-validation", "cpt-ex-ovwa-fr-track-active-time", "cpt-ex-ovwa-fr-cli-controls"]
to_code = false
headings = ["prd-fr"]

[ref.DESIGN]
coverage = true
headings = ["design-arch-overview-drivers"]

[ref.DECOMPOSITION]
# coverage = true|false  # optional by default
headings = ["decomposition-entry"]

[ref.FEATURE]
# coverage = true|false  # optional by default
headings = ["feature-context-purpose"]
```
`@/cpt:id`

`@cpt:prompt`
```markdown
> **Testing strategy**: All requirements verified via automated tests (unit, integration, e2e) targeting 90%+ code coverage unless otherwise specified. Document verification method only for non-test approaches (analysis, inspection, demonstration).

Functional requirements define WHAT the system must do. Group by feature area or priority tier.
```
`@/cpt:prompt`

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
- [ ] Every FR MUST use observable behavior language (MUST, MUST NOT, SHOULD)
- [ ] Every FR MUST have a unique ID: `cpt-{system}-fr-{slug}`
- [ ] Every FR MUST have a priority marker (`p1`–`p9`)
- [ ] Every FR MUST have a rationale explaining business value
- [ ] Every FR MUST reference at least one actor
- [ ] Capabilities MUST trace to business problems
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document
- [ ] All requirements verified via automated tests (unit, integration, e2e) targeting 90%+ code coverage unless otherwise specified
- [ ] Document verification method only for non-test approaches (analysis, inspection, demonstration)
```
`@/cpt:rule`

`@cpt:heading`
```toml
id = "prd-fr-group"
level = 3
required = true
numbered = true
# multiple = true|false  # allowed by default (can repeat)
template = "{Feature Area / Priority Tier}"
description = "Feature area or priority tier grouping."
examples = []
```
`@/cpt:heading`

`@cpt:heading`
```toml
id = "prd-fr-entry"
level = 4
required = true
numbered = false
# multiple = true|false  # allowed by default (can repeat)
template = "{Requirement Name}"
description = "Individual functional requirement entry."
examples = []
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
- [ ] `p1` - **ID**: `cpt-{system}-fr-{slug}`

The system **MUST** {do something specific and verifiable}.

**Rationale**: {Why this requirement exists — business value or stakeholder need.}

**Actors**: `cpt-{system}-actor-{slug}`

**Verification Method** (optional): {Only if non-standard: analysis | inspection | demonstration | specialized test approach}

**Acceptance Evidence** (optional): {Only if non-obvious: specific test suite path, analysis report, review checklist}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
### FR-001 Task Management

- [ ] `p1` - **ID**: `cpt-ex-task-flow-fr-task-management`

The system MUST allow creating, editing, and deleting tasks. The system MUST allow assigning tasks to team members. The system MUST allow setting due dates and priorities. Tasks should support rich text descriptions and file attachments.

**Actors**:

`cpt-ex-task-flow-actor-member`, `cpt-ex-task-flow-actor-lead`

### FR-002 Notifications

- [ ] `p1` - **ID**: `cpt-ex-task-flow-fr-notifications`

The system MUST send push notifications for task assignments. The system MUST send alerts for overdue tasks. Notifications should be configurable per user to allow opting out of certain notification types.

**Actors**:

`cpt-ex-task-flow-actor-notifier`, `cpt-ex-task-flow-actor-member`
```
`@/cpt:example`

### Non-Functional Requirements

`@cpt:heading`
```toml
id = "prd-nfr"
level = 2
required = true
numbered = true
multiple = false
pattern = "Non-Functional Requirements"
description = "Non-functional requirements section."
examples = ["## 6. Non-Functional Requirements"]
```
`@/cpt:heading`

`@cpt:id`
```toml
kind = "nfr"
name = "Non-functional Requirement"
description = "A measurable quality attribute requirement (performance, security, reliability, usability, etc.)."
required = true
# task = true|false    # optional by default
priority = true
template = "cpt-{system}-nfr-{slug}"
examples = ["cpt-cypilot-nfr-validation-performance", "cpt-ex-ovwa-nfr-privacy-local-only", "cpt-ex-ovwa-nfr-low-overhead"]
to_code = false
headings = ["prd-nfr"]

[ref.DESIGN]
coverage = true
headings = ["design-arch-overview-drivers"]

[ref.DECOMPOSITION]
# coverage = true|false  # optional by default
headings = ["decomposition-entry"]

[ref.FEATURE]
# coverage = true|false  # optional by default
headings = ["feature-context-purpose"]
```
`@/cpt:id`

`@/cpt:prompt`

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
- [ ] NFRs MUST have measurable thresholds with units and conditions
- [ ] NFR exclusions MUST have explicit reasoning
```
`@/cpt:rule`

`@cpt:heading`
```toml
id = "prd-nfr-inclusions"
level = 3
required = false
numbered = true
multiple = false
pattern = "NFR Inclusions"
description = "Non-functional requirements that deviate from or extend project defaults."
examples = ["### 6.1 Module-Specific NFRs"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
{Only include this section if there are NFRs that deviate from or extend project defaults.}
```
`@/cpt:prompt`

`@cpt:heading`
```toml
id = "prd-nfr-entry"
level = 4
required = false
numbered = false
# multiple = true|false  # allowed by default (can repeat)
template = "{NFR Name}"
description = "Individual non-functional requirement entry."
examples = ["#### Security", "#### Performance"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
- [ ] `p1` - **ID**: `cpt-{system}-nfr-{slug}`

The system **MUST** {measurable NFR with specific thresholds, e.g., "respond within 50ms at p95" (stricter than project default)}.

**Threshold**: {Quantitative target with units and conditions}

**Rationale**: {Why this module needs different/additional NFR}

**Verification Method** (optional): {Only if non-standard approach needed}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
- [ ] `p1` - **ID**: `cpt-ex-task-flow-nfr-security`

- Authentication MUST be required for all user actions
- Authorization MUST enforce team role permissions
- Passwords MUST be stored using secure hashing algorithms

#### Performance

- [ ] `p2` - **ID**: `cpt-ex-task-flow-nfr-performance`

- Task list SHOULD load within 500ms for teams under 100 tasks
- Real-time updates SHOULD propagate within 2 seconds
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "prd-nfr-exclusions"
level = 3
required = true
numbered = true
multiple = false
pattern = "NFR Exclusions"
description = "Explicit non-functional requirement exclusions."
examples = ["### 6.2 NFR Exclusions"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
{Document any project-default NFRs that do NOT apply to this module}

- {Default NFR name}: {Reason for exclusion}
```
`@/cpt:prompt`

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
- [ ] Intentional exclusions MUST list N/A checklist categories with reasoning
```
`@/cpt:rule`

`@cpt:example`
```markdown
- **Accessibility** (UX-PRD-002): Not applicable — MVP targets internal teams with standard desktop browsers
- **Internationalization** (UX-PRD-003): Not applicable — English-only for initial release
- **Regulatory Compliance** (COMPL-PRD-001/002/003): Not applicable — No PII or regulated data in MVP scope
```
`@/cpt:example`

### Public Interfaces

API surface and external integration contracts.

`@cpt:heading`
```toml
id = "prd-public-interfaces"
level = 2
required = true
numbered = true
multiple = false
pattern = "Public Library Interfaces"
description = "Public library interfaces and integration contracts."
examples = ["## 7. Public Library Interfaces"]
```
`@/cpt:heading`

`@cpt:id`
```toml
kind = "interface"
name = "Public Interface"
description = "A public API surface (library interface, protocol, CLI contract) provided by the system."
required = false
# task = true|false      # optional by default
# priority = true|false  # optional by default
template = "cpt-{system}-interface-{slug}"
examples = ["cpt-cypilot-interface-cli-json", "cpt-ex-ovwa-interface-cli", "cpt-ex-ovwa-interface-ipc-protocol"]
to_code = false
headings = ["prd-public-interfaces"]

[ref.DESIGN]
coverage = true
headings = ["design-tech-arch-api-contracts"]
```
`@/cpt:id`

`@cpt:id`
```toml
kind = "contract"
name = "Integration Contract"
description = "An external integration contract (data format/protocol/compatibility expectations) with another system."
required = false
# task = true|false      # optional by default
# priority = true|false  # optional by default
template = "cpt-{system}-contract-{slug}"
examples = ["cpt-ex-ovwa-contract-macos-notification-center", "cpt-ex-ovwa-contract-launchd", "cpt-cypilot-contract-openai-api"]
to_code = false
headings = ["prd-public-interfaces"]

[ref.DESIGN]
coverage = true
headings = ["design-tech-arch-api-contracts"]
```
`@/cpt:id`

`@cpt:prompt`
```markdown
Define the public API surface, versioning/compatibility guarantees, and integration contracts provided by this library.
```
`@/cpt:prompt`

`@cpt:heading`
```toml
id = "prd-public-interfaces-api"
level = 3
required = true
numbered = true
multiple = false
pattern = "Public API Surface"
description = "Public API surface."
examples = ["### 7.1 Public API Surface"]
```
`@/cpt:heading`

`@cpt:heading`
```toml
id = "prd-interface-entry"
level = 4
required = false
numbered = false
# multiple = true|false  # allowed by default (can repeat)
template = "{Interface Name}"
description = "Individual public interface entry."
examples = []
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
- [ ] `p1` - **ID**: `cpt-{system}-interface-{slug}`

**Type**: {Rust module/trait/struct | REST API | CLI | Protocol | Data format}

**Stability**: {stable | unstable | experimental}

**Description**: {What this interface provides}

**Breaking Change Policy**: {e.g., Major version bump required}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
None.
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "prd-public-interfaces-external-contracts"
level = 3
required = true
numbered = true
multiple = false
pattern = "External Integration Contracts"
description = "External integration contracts."
examples = ["### 7.2 External Integration Contracts"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
Contracts this library expects from external systems or provides to downstream clients.
```
`@/cpt:prompt`

`@cpt:heading`
```toml
id = "prd-contract-entry"
level = 4
required = false
numbered = false
# multiple = true|false  # allowed by default (can repeat)
template = "{Contract Name}"
description = "Individual external integration contract entry."
examples = []
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
- [ ] `p2` - **ID**: `cpt-{system}-contract-{slug}`

**Direction**: {provided by library | required from client}

**Protocol/Format**: {e.g., HTTP/REST, gRPC, JSON Schema}

**Compatibility**: {Backward/forward compatibility guarantees}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
None.
```
`@/cpt:example`

### Use Cases

`@cpt:heading`
```toml
id = "prd-use-cases"
level = 2
required = true
numbered = true
multiple = false
pattern = "Use Cases"
description = "Use cases section."
examples = ["## 8. Use Cases"]
```
`@/cpt:heading`

`@cpt:id`
```toml
kind = "usecase"
name = "Use Case"
description = "An end-to-end interaction scenario (actor + goal + flow) that clarifies behavior beyond individual requirements."
required = true
# task = true|false      # optional by default
# priority = true|false  # optional by default
template = "cpt-{system}-usecase-{slug}"
examples = ["cpt-ex-ovwa-usecase-run-and-alert", "cpt-ex-ovwa-usecase-configure-limit", "cpt-ex-ovwa-usecase-control-session"]
to_code = false
headings = ["prd-use-cases"]

[ref.DESIGN]
# coverage = true|false  # optional by default
headings = ["design-tech-arch-seq"]

[ref.FEATURE]
# coverage = true|false  # optional by default
headings = ["feature-actor-flow"]
```
`@/cpt:id`

`@cpt:prompt`
```markdown
Optional: Include when interaction flows add clarity beyond requirement statements.
```
`@/cpt:prompt`

`@cpt:heading`
```toml
id = "prd-usecase-entry"
level = 4
required = false
numbered = false
# multiple = true|false  # allowed by default (can repeat)
template = "{Use Case Name}"
description = "Individual use case entry."
examples = []
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
- [ ] `p2` - **ID**: `cpt-{system}-usecase-{slug}`

**Actor**: `cpt-{system}-actor-{slug}`

**Preconditions**:
- {Required state before execution}

**Main Flow**:
1. {Actor action or system response}
2. {Next step}

**Postconditions**:
- {State after successful completion}

**Alternative Flows**:
- **{Condition}**: {What happens instead}
```
`@/cpt:prompt`

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
- [ ] Use cases MUST cover primary user journeys
- [ ] Use cases MUST include alternative flows for error scenarios
- [ ] Use case IDs follow: `cpt-{system}-usecase-{slug}`
```
`@/cpt:rule`

`@cpt:example`
```markdown
### UC-001 Create and Assign Task

**ID**: `cpt-ex-task-flow-usecase-create-task`

**Actors**:

`cpt-ex-task-flow-actor-lead`

**Preconditions**: User is authenticated and has team lead permissions.

**Main Flow**:

1. Lead creates a new task with title and description
2. Lead assigns task to a team member
3. Lead sets due date and priority
4. System validates task data
5. System sends notification to assignee

**Postconditions**: Task appears in assignee's task list; notification sent.

**Alternative Flows**:

- **Validation fails**: If step 4 fails validation (e.g., no assignee selected), system displays error and returns to step 2
```
`@/cpt:example`

### Acceptance Criteria, Dependencies, Assumptions, Risks

`@cpt:heading`
```toml
id = "prd-acceptance-criteria"
level = 2
required = true
numbered = true
multiple = false
pattern = "Acceptance Criteria"
description = "Acceptance criteria for delivery."
examples = ["## 9. Acceptance Criteria"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
Business-level acceptance criteria for the PRD as a whole.

- [ ] {Testable criterion that validates a key business outcome}
- [ ] {Another testable criterion}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
- [ ] Tasks can be created/assigned in under 30 seconds
- [ ] Task updates propagate to all clients within 2 seconds
- [ ] Overdue alerts are delivered within 1 minute
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "prd-dependencies"
level = 2
required = true
numbered = true
multiple = false
pattern = "Dependencies"
description = "Dependencies required to deliver the PRD."
examples = ["## 10. Dependencies"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
| Dependency | Description | Criticality |
|------------|-------------|-------------|
| {Service/System} | {What it provides} | {p1/p2/p3} |
```
`@/cpt:prompt`

`@cpt:example`
```markdown
| Dependency | Description | Criticality |
|------------|-------------|-------------|
| Notification delivery | Push notification channel for deadlines/status changes | p2 |
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "prd-assumptions"
level = 2
required = true
numbered = true
multiple = false
pattern = "Assumptions"
description = "Assumptions that must hold."
examples = ["## 11. Assumptions"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
- {Assumption about environment, users, or dependent systems}
```
`@/cpt:prompt`

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
- [ ] Key assumptions MUST be explicitly stated
- [ ] Open questions MUST have owners and target resolution dates
```
`@/cpt:rule`

`@cpt:example`
```markdown
- Users have modern browsers and reliable connectivity for real-time updates
- The initial deployment is cloud-hosted
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "prd-risks"
level = 2
required = true
numbered = true
multiple = false
pattern = "Risks"
description = "Risks and mitigations."
examples = ["## 12. Risks"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
| Risk | Impact | Mitigation |
|------|--------|------------|
| {Risk description} | {Potential impact} | {Mitigation strategy} |
```
`@/cpt:prompt`

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
- [ ] Risks and uncertainties MUST be documented with impact and mitigation
```
`@/cpt:rule`

`@cpt:example`
```markdown
| Risk | Impact | Mitigation |
|------|--------|------------|
| Adoption risk | Teams may resist switching tools | Focus on migration path and quick wins |
| Scale risk | Real-time may not scale beyond 50 concurrent users | Load testing before launch |
```
`@/cpt:example`
