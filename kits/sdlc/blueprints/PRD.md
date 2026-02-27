# PRD Blueprint
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

## Metadata

> **`@cpt:blueprint`** — Blueprint metadata: artifact kind, kit slug, version. Internal; not output to any file.

`@cpt:blueprint`
```toml
# Blueprint version (semver)
version = 1
# Kit slug this blueprint belongs to
kit = "sdlc"
# Artifact kind: PRD | ADR | DESIGN | DECOMPOSITION | FEATURE | CODE
artifact = "PRD"
codebase = false
```
`@/cpt:blueprint`

## Skill Integration

Commands and workflows exposed to AI agents for PRD operations.

> **`@cpt:skill`** — Skill content. Agent-facing navigation and instructions. Output: `.gen/kits/{slug}/SKILL.md`.

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

> **`@cpt:rules`** — Rules skeleton. Defines section structure (prerequisites, requirements, tasks, validation, etc.) for `rules.md`.

`@cpt:rules`
```toml
# Prerequisite steps (load dependencies, read configs)
[prerequisites]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["load_dependencies"]

# Requirement sections (structural, semantic, constraints, etc.)
[requirements]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["structural", "versioning", "semantic", "traceability", "constraints", "deliberate_omissions"]
# Display names for non-obvious requirement section keys
[requirements.names]
deliberate_omissions = "Deliberate Omissions (MUST NOT HAVE)"

# Task phases — step-by-step workflow for creating the artifact
[tasks]
# Ordered list of phase keys (each needs a matching @cpt:rule block)
phases = ["setup", "content_creation", "ids_and_structure", "quality_check"]
# Display names for non-obvious task phase keys
[tasks.names]
ids_and_structure = "IDs and Structure"

# Validation phases — ordered checks run after artifact is written
[validation]
# Ordered list of phase keys (each needs a matching @cpt:rule block)
phases = ["structural", "semantic", "validation_report", "applicability", "review_priority", "report_format", "reporting", "pr_review"]
# Display names for non-obvious validation phase keys
[validation.names]
structural = "Structural Validation (Deterministic)"
semantic = "Semantic Validation (Checklist-based)"
applicability = "Applicability Context"
review_priority = "Review Priority"
report_format = "Report Format"
reporting = "Reporting Commitment"
pr_review = "PR Review Focus (Requirements)"

# Error handling sections — what to do when things go wrong
[error_handling]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["missing_dependencies", "missing_adapter", "escalation"]

# Next steps — recommended actions after completing the artifact
[next_steps]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["options"]
```
`@/cpt:rules`

### Prerequisites

Dependencies that must be loaded before working with a PRD artifact.

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "prerequisites"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "load_dependencies"
```
```markdown
- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read project config for ID prefix
- [ ] Load `{cypilot_path}/.core/architecture/specs/traceability.md` for ID formats
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/constraints.toml` for kit-level constraints
- [ ] Load `{cypilot_path}/.core/architecture/specs/kit/constraints.md` for constraints specification
```
`@/cpt:rule`

### Requirements

#### Structural Requirements

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "traceability"
```
```markdown
- [ ] Capabilities traced through: PRD → DESIGN → DECOMPOSITION → FEATURE → CODE
- [ ] When capability fully implemented (all specs IMPLEMENTED) → mark capability `[x]`
- [ ] When all capabilities `[x]` → product version complete
```
`@/cpt:rule`

#### Constraints Integration

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "constraints"
```
```markdown
- [ ] ALWAYS open and follow `{cypilot_path}/.gen/kits/sdlc/constraints.toml` (kit root)
- [ ] Treat `constraints.toml` as primary validator for:
  - where IDs are defined
  - where IDs are referenced
  - which cross-artifact references are required / optional / prohibited

**References**:
- `{cypilot_path}/.core/requirements/kit-constraints.md`
- `{cypilot_path}/.core/schemas/kit-constraints.schema.json`

**Validation Checks**:
- `cypilot validate` enforces `identifiers[<kind>].references` rules (required / optional / prohibited)
- `cypilot validate` enforces headings scoping for ID definitions and references
- `cypilot validate` enforces "checked ref implies checked def" consistency
```
`@/cpt:rule`

#### Deliberate Omissions (MUST NOT HAVE)

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "deliberate_omissions"
```
```markdown
PRDs must NOT contain the following — report as violation if found:

- **ARCH-PRD-NO-001**: No Technical Implementation Details (CRITICAL) — PRD captures *what*, not *how*
- **ARCH-PRD-NO-002**: No Architectural Decisions (CRITICAL) — decisions belong in ADR
- **BIZ-PRD-NO-001**: No Implementation Tasks (HIGH) — tasks belong in DECOMPOSITION
- **BIZ-PRD-NO-002**: No Spec-Level Design (HIGH) — specs belong in FEATURE
- **DATA-PRD-NO-001**: No Data Schema Definitions (HIGH) — schemas belong in DESIGN
- **INT-PRD-NO-001**: No API Specifications (HIGH) — API specs belong in DESIGN/FEATURE
- **TEST-PRD-NO-001**: No Test Cases (MEDIUM) — tests belong in FEATURE/code
- **OPS-PRD-NO-001**: No Infrastructure Specifications (MEDIUM) — infra belongs in DESIGN
- **SEC-PRD-NO-001**: No Security Implementation Details (HIGH) — implementation belongs in DESIGN/code
- **MAINT-PRD-NO-001**: No Code-Level Documentation (MEDIUM) — code docs belong in code
```
`@/cpt:rule`

### Task Phases

#### Setup

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "setup"
```
```markdown
- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `example.md` for reference style
- [ ] Read project config for ID prefix
```
`@/cpt:rule`

#### Content Creation

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "ids_and_structure"
```
```markdown
- [ ] Generate actor IDs: `cpt-{hierarchy-prefix}-actor-{slug}` (e.g., `cpt-myapp-actor-admin-user`)
- [ ] Generate capability IDs: `cpt-{hierarchy-prefix}-fr-{slug}` (e.g., `cpt-myapp-fr-user-management`)
- [ ] Assign priorities based on business impact
- [ ] Verify uniqueness with `cypilot list-ids`
```
`@/cpt:rule`

#### Quality Check

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
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

#### Validation Report

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "validation_report"
```
````markdown
```
PRD Validation Report
═════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```
````
`@/cpt:rule`

#### Applicability Context

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "applicability"
```
```markdown
Before evaluating each checklist item, the expert MUST:

1. **Understand the product's domain** — What kind of product is this PRD for? (e.g., consumer app, enterprise platform, developer tool, internal system)

2. **Determine applicability for each requirement** — Not all checklist items apply to all PRDs:
   - An internal tool PRD may not need market positioning analysis
   - A developer framework PRD may not need end-user personas
   - A methodology PRD may not need regulatory compliance analysis

3. **Require explicit handling** — For each checklist item:
   - If applicable: The document MUST address it (present and complete)
   - If not applicable: The document MUST explicitly state "Not applicable because..." with reasoning
   - If missing without explanation: Report as violation

4. **Never skip silently** — Either:
   - The requirement is met (document addresses it), OR
   - The requirement is explicitly marked not applicable (document explains why), OR
   - The requirement is violated (report it with applicability justification)

**Key principle**: The reviewer must be able to distinguish "author considered and excluded" from "author forgot"

For each major checklist category (BIZ, ARCH, SEC, TEST, MAINT), confirm:

- [ ] Category is addressed in the document, OR
- [ ] Category is explicitly marked "Not applicable" with reasoning, OR
- [ ] Category absence is reported as a violation (with applicability justification)
```
`@/cpt:rule`

#### Review Priority

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "review_priority"
```
```markdown
**Review Priority**: BIZ → ARCH → SEC → TEST → (others as applicable)

> **New in v1.2**: Safety was added as a distinct quality characteristic in ISO/IEC 25010:2023. Applicable for systems that could cause harm to people, property, or the environment.
```
`@/cpt:rule`

#### Report Format

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "report_format"
```
````markdown
Report **only** problems (do not list what is OK).

For each issue include:

- **Why Applicable**: Explain why this requirement applies to this specific PRD's context
- **Checklist Item**: `{CHECKLIST-ID}` — {Checklist item title}
- **Severity**: CRITICAL|HIGH|MEDIUM|LOW
- **Issue**: What is wrong (requirement missing or incomplete)
- **Evidence**: Quote the exact text or "No mention found"
- **Why it matters**: Impact (risk, cost, user harm, compliance)
- **Proposal**: Concrete fix with clear acceptance criteria

```markdown
## Review Report (Issues Only)

### 1. {Short issue title}

**Checklist Item**: `{CHECKLIST-ID}` — {Checklist item title}

**Severity**: CRITICAL|HIGH|MEDIUM|LOW

#### Why Applicable

{Explain why this requirement applies to this PRD's context}

#### Issue

{What is wrong}

#### Evidence

{Quote or "No mention found"}

#### Why It Matters

{Impact}

#### Proposal

{Concrete fix}
```
````
`@/cpt:rule`

#### Reporting Commitment

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
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

#### PR Review Focus (Requirements)

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "pr_review"
```
```markdown
When reviewing PRs that add or change PRD/requirements documents, additionally focus on:

- [ ] Completeness and clarity of requirements
- [ ] Testability and acceptance criteria for every requirement
- [ ] Traceability to business goals and stated problems
- [ ] Compliance with `template.md` structure (generated from blueprint)
- [ ] Alignment with best industry standard practices for large SaaS systems and platforms
- [ ] Critical assessment of requirements quality — challenge vague, overlapping, or untestable items
- [ ] Split findings by checklist category and rate each 1-10
- [ ] Ensure requirements are aligned with the project's existing architecture (see DESIGN artifacts)
```
`@/cpt:rule`

### Error Handling

#### Missing Dependencies

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "error_handling"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "missing_dependencies"
```
```markdown
- [ ] If `template.md` cannot be loaded → STOP, cannot proceed without template
- [ ] If `checklist.md` cannot be loaded → warn user, skip semantic validation
- [ ] If `examples/example.md` cannot be loaded → warn user, continue with reduced guidance
```
`@/cpt:rule`

#### Missing Config

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "error_handling"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "missing_config"
```
```markdown
- [ ] If project config unavailable → use default project prefix `cpt-{dirname}`
- [ ] Ask user to confirm or provide custom prefix
```
`@/cpt:rule`

#### Escalation

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "error_handling"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "next_steps"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:checklist`** — Checklist preamble. Static markdown placed at the top of `checklist.md` (standards, prerequisites, severity dictionary).

`@cpt:checklist`
```toml
[severity]
levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

[review]
priority = ["BIZ", "ARCH", "SEC", "SAFE", "PERF", "REL", "UX", "MAINT", "COMPL", "DATA", "INT", "OPS", "TEST", "DOC"]

[[domain]]
abbr = "BIZ"
name = "BUSINESS Expertise"
header = "BUSINESS Expertise (BIZ)"
standards_text = """> **Standards**: [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) §6.2 (StRS content), §6.4 (SRS content)"""

[[domain]]
abbr = "ARCH"
name = "ARCHITECTURE Expertise"
header = "ARCHITECTURE Expertise (ARCH)"
standards_text = """> **Standards**: [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) (Maintainability, Flexibility), [ISO/IEC/IEEE 29148](https://www.iso.org/standard/72089.html) §6.3 (SyRS)"""

[[domain]]
abbr = "SEC"
name = "🔒 SECURITY Expertise"
header = "🔒 SECURITY Expertise (SEC)"
standards_text = """> **Standards**: [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) §4.2.6 (Security), [OWASP ASVS 5.0](https://owasp.org/www-project-application-security-verification-standard/), [NIST SP 800-53 Rev.5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final), [ISO/IEC 27001:2022](https://www.iso.org/standard/27001)"""

[[domain]]
abbr = "SAFE"
name = "🛡️ SAFETY Expertise"
header = "🛡️ SAFETY Expertise (SAFE)"
standards_text = """> **Standards**: [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) §4.2.9 (Safety characteristic) — **NEW in 2023 edition**"""

[[domain]]
abbr = "PERF"
name = "⚡ PERFORMANCE Expertise"
header = "⚡ PERFORMANCE Expertise (PERF)"
standards_text = """> **Standards**: [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) §4.2.2 (Performance Efficiency)"""

[[domain]]
abbr = "REL"
name = "🛡️ RELIABILITY Expertise"
header = "🛡️ RELIABILITY Expertise (REL)"
standards_text = """> **Standards**: [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) §4.2.5 (Reliability), [ISO 22301:2019](https://www.iso.org/standard/75106.html) (Business Continuity), SOC 2 Availability TSC"""

[[domain]]
abbr = "UX"
name = "👤 USABILITY Expertise"
header = "👤 USABILITY Expertise (UX)"
standards_text = """> **Standards**: [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) §4.2.4 (Interaction Capability), [ISO 9241-11:2018](https://www.iso.org/standard/63500.html), [ISO 9241-210:2019](https://www.iso.org/standard/77520.html), [WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/)"""

[[domain]]
abbr = "MAINT"
name = "🔧 MAINTAINABILITY Expertise"
header = "🔧 MAINTAINABILITY Expertise (MAINT)"
standards_text = """> **Standards**: [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) §4.2.7 (Maintainability)"""

[[domain]]
abbr = "COMPL"
name = "📜 COMPLIANCE Expertise"
header = "📜 COMPLIANCE Expertise (COMPL)"
standards_text = """> **Standards**: [GDPR](https://gdpr-info.eu/), [HIPAA](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html), [PCI DSS 4.0.1](https://blog.pcisecuritystandards.org/pci-dss-v4-0-resource-hub), [SOC 2 TSC](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022), [SOX](https://www.sec.gov/about/laws/soa2002.pdf)"""

[[domain]]
abbr = "DATA"
name = "📊 DATA Expertise"
header = "📊 DATA Expertise (DATA)"
standards_text = """> **Standards**: [GDPR](https://gdpr-info.eu/) (personal data), [ISO/IEC 25012](https://www.iso.org/standard/35736.html) (Data Quality)"""

[[domain]]
abbr = "INT"
name = "🔌 INTEGRATION Expertise"
header = "🔌 INTEGRATION Expertise (INT)"
standards_text = """> **Standards**: [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) §4.2.3 (Compatibility — Interoperability)"""

[[domain]]
abbr = "OPS"
name = "🖥️ OPERATIONS Expertise"
header = "🖥️ OPERATIONS Expertise (OPS)"
standards_text = """> **Standards**: [ISO 22301:2019](https://www.iso.org/standard/75106.html) (Business Continuity), NIST 800-53 CM/CP families"""

[[domain]]
abbr = "TEST"
name = "🧪 TESTING Expertise"
header = "🧪 TESTING Expertise (TEST)"
standards_text = """> **Standards**: [ISO/IEC/IEEE 29119](https://www.iso.org/standard/81291.html) (Software Testing), [ISO/IEC/IEEE 29148](https://www.iso.org/standard/72089.html) §5.2.8 (Verification)"""

[[domain]]
abbr = "DOC"
name = "DOC"
header = "DOC (DOC)"
standards = []

```
````markdown
# PRD Expert Checklist

**Artifact**: Product Requirements Document (PRD)
**Version**: 1.2
**Last Updated**: 2026-02-03
**Purpose**: Comprehensive quality checklist for PRD artifacts

---

## Referenced Standards

This checklist incorporates requirements and best practices from the following international standards:

| Standard | Domain | Description |
|----------|--------|-------------|
| [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) | Requirements Engineering | Life cycle processes for requirements engineering (supersedes IEEE 830) |
| [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) | Software Quality | Product quality model with 9 characteristics |
| [ISO/IEC 27001:2022](https://www.iso.org/standard/27001) | Information Security | ISMS requirements |
| [ISO 22301:2019](https://www.iso.org/standard/75106.html) | Business Continuity | BCMS requirements |
| [ISO 9241-11:2018](https://www.iso.org/standard/63500.html) | Usability | Usability definitions and framework |
| [ISO 9241-210:2019](https://www.iso.org/standard/77520.html) | Human-Centred Design | HCD for interactive systems |
| [WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/) | Accessibility | Web Content Accessibility Guidelines |
| [OWASP ASVS 5.0](https://owasp.org/www-project-application-security-verification-standard/) | Application Security | Security verification requirements |
| [NIST SP 800-53 Rev.5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) | Security Controls | Security and privacy controls catalog |
| [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749) | Authentication | OAuth 2.0 Authorization Framework |
| [GDPR Art. 25](https://gdpr-info.eu/art-25-gdpr/) | Privacy | Data protection by design and default |
| [HIPAA](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html) | Healthcare Privacy | Health information privacy and security |
| [PCI DSS 4.0.1](https://blog.pcisecuritystandards.org/pci-dss-v4-0-resource-hub) | Payment Security | Payment card data security |
| [SOC 2 TSC](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022) | Trust Services | Security, availability, confidentiality, processing integrity, privacy |
---

## Prerequisites

Before starting the review, confirm:

- [ ] I understand this checklist validates PRD artifacts
- [ ] I will follow the Applicability Context rules below
- [ ] I will check ALL items in MUST HAVE sections
- [ ] I will verify ALL items in MUST NOT HAVE sections
- [ ] I will document any violations found
- [ ] I will provide specific feedback for each failed check
- [ ] I will complete the Final Checklist and provide a review report
- [ ] I will use the [Reporting](#reporting) format for output (see end of document)

---

## Applicability Context

Before evaluating each checklist item, the expert MUST:

1. **Understand the product's domain** — What kind of product is this PRD for? (e.g., consumer app, enterprise platform, developer tool, internal system)

2. **Determine applicability for each requirement** — Not all checklist items apply to all PRDs:
   - An internal tool PRD may not need market positioning analysis
   - A developer framework PRD may not need end-user personas
   - A methodology PRD may not need regulatory compliance analysis

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

## Applicability Determination

**For items marked "(if applicable)"**, determine applicability using these criteria:

| Domain | Applicable When | Not Applicable When |
|--------|-----------------|---------------------|
| Market positioning (BIZ-PRD-002) | External product, competitive market | Internal tool, no competitors |
| SSO/federation (SEC-PRD-001) | Enterprise product, multi-tenant | Single-user tool, local-only |
| Privacy by Design (SEC-PRD-005) | Handles EU personal data, PII | No personal data processing |
| Safety (SAFE-PRD-001/002) | Could harm people/property/environment, medical devices, vehicles, industrial | Pure information system, no physical interaction |
| Regulatory (COMPL-PRD-001) | Handles PII, financial data, healthcare | Internal dev tool, no user data |
| Accessibility (UX-PRD-002) | Public-facing, government, enterprise | Internal tool with known user base |
| Inclusivity (UX-PRD-005) | Diverse user base, public-facing | Narrow technical audience, internal tool |
| Internationalization (UX-PRD-003) | Multi-region deployment planned | Single-locale deployment |
| Offline capability (UX-PRD-004) | Mobile app, unreliable network | Server-side tool, always-connected |

**When uncertain**: Mark as applicable and let the PRD author explicitly exclude with reasoning.

---

## Checkpointing (Long Reviews)

This checklist is 700+ lines. For reviews that may exceed context limits:

### Checkpoint After Each Domain

After completing each expertise domain (BIZ, ARCH, SEC, etc.), output:
```
✓ {DOMAIN} complete: {N} items checked, {M} issues found
Issues: {list issue IDs}
Remaining: {list unchecked domains}
```

### If Context Runs Low

1. **Save progress**: List completed domains and issues found so far
2. **Note position**: "Stopped at {DOMAIN}-{ID}"
3. **Resume instruction**: "Continue from {DOMAIN}-{ID}, issues so far: {list}"

### Minimum Viable Review

If full review impossible, prioritize in this order:
1. **BIZ** (CRITICAL) — Vision, Requirements, Use Cases
2. **ARCH-PRD-001** (CRITICAL) — Scope Boundaries
3. **SEC-PRD-001/002** (CRITICAL) — Auth/Authorization
4. **DOC-PRD-001** (CRITICAL) — Deliberate Omissions
5. **MUST NOT HAVE** (all CRITICAL/HIGH items)

Mark review as "PARTIAL" if not all domains completed.
````
`@/cpt:checklist`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "Vision Clarity"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148 §5.2.5 (Stakeholder requirements definition)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-PRD-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "Stakeholder Coverage"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148 §6.2.2 (Stakeholders), ISO 9241-210 §4 (HCD principles)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-PRD-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "Requirements Completeness"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148 §5.2.6 (Requirements analysis), §6.4.3 (Specific requirements)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-PRD-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "Use Case Coverage"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-PRD-005"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "Success Metrics"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148 §6.2.4 (Operational concept), ISO 9241-11 §5 (Measures of usability)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-PRD-006"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "Terminology & Definitions"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Key domain terms are defined (glossary or inline)
- [ ] Acronyms are expanded on first use
- [ ] Terms are used consistently (no synonyms that change meaning)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-PRD-007"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "Assumptions & Open Questions"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Key assumptions are explicitly stated
- [ ] Open questions are listed with owners and desired resolution time
- [ ] Dependencies on external teams/vendors are called out
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-PRD-008"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "Risks & Non-Goals"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Major risks/uncertainties are listed
- [ ] Explicit non-goals/out-of-scope items are documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "Scope Boundaries"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148 §6.3.2 (System overview), §6.3.4 (System interfaces)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-PRD-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "Modularity Enablement"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.7.2 (Modularity subcharacteristic)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-PRD-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "Scalability Considerations"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.8.4 (Scalability subcharacteristic of Flexibility)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-PRD-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "System Actor Clarity"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148 §6.3.4 (System interfaces)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-PRD-005"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "Compatibility Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "[ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) §4.2.3 (Compatibility characteristic)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
> **New in v1.2**: Added per ISO/IEC 25010:2023 which defines Compatibility as a distinct quality characteristic covering co-existence and interoperability.

- [ ] Co-existence requirements documented (operation alongside other products without adverse impact)
- [ ] Interoperability requirements stated (ability to exchange information with other systems)
- [ ] Data format compatibility requirements captured (file formats, protocols)
- [ ] Hardware/software environment compatibility stated
- [ ] Backward compatibility requirements documented (if applicable)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEC-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEC"
# Human-readable check title
title = "Authentication Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "OWASP ASVS V2 (Authentication), [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749) (OAuth 2.0), NIST 800-53 IA family"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] User authentication needs stated
- [ ] Multi-factor requirements captured (if applicable)
- [ ] SSO/federation requirements documented
- [ ] Session management expectations stated
- [ ] Password/credential policies referenced
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEC-PRD-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEC"
# Human-readable check title
title = "Authorization Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "OWASP ASVS V4 (Access Control), NIST 800-53 AC family, ISO 27001 A.9"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEC-PRD-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEC"
# Human-readable check title
title = "Data Classification"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.6.2 (Confidentiality), NIST 800-53 SC family, [GDPR Art. 9](https://gdpr-info.eu/art-9-gdpr/)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEC-PRD-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEC"
# Human-readable check title
title = "Audit Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.6.5 (Accountability), NIST 800-53 AU family, SOC 2 CC6/CC7"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEC-PRD-005"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEC"
# Human-readable check title
title = "Privacy by Design"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH (if applicable)"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "[GDPR Article 25](https://gdpr-info.eu/art-25-gdpr/), [EDPB Guidelines 4/2019](https://www.edpb.europa.eu/sites/default/files/files/file1/edpb_guidelines_201904_dataprotection_by_design_and_by_default_v2.0_en.pdf)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
> **New in v1.2**: Added per GDPR Article 25 requirement for data protection by design and by default. Applicable when processing personal data of EU residents or when building products that will handle PII.

- [ ] Privacy requirements embedded from project inception (not retrofitted)
- [ ] Data minimization principle stated (collect only what is necessary)
- [ ] Purpose limitation documented (data used only for stated purposes)
- [ ] Storage limitation requirements captured (retention periods defined)
- [ ] Privacy by default requirements stated (most privacy-protective settings as default)
- [ ] Pseudonymization/anonymization requirements documented where applicable
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SAFE-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SAFE"
# Human-readable check title
title = "Operational Safety Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL (if applicable)"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.9.1 (Operational constraint), §4.2.9.2 (Risk identification)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Safety-critical operations identified
- [ ] Operational constraints for safe operation documented
- [ ] Potential hazards identified and documented
- [ ] Risk levels assessed for identified hazards
- [ ] User actions that could lead to harm documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SAFE-PRD-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SAFE"
# Human-readable check title
title = "Fail-Safe and Hazard Prevention"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL (if applicable)"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.9.3 (Fail safe), §4.2.9.4 (Hazard warning), §4.2.9.5 (Safe integration)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Fail-safe behavior requirements documented (safe state on failure)
- [ ] Hazard warning requirements stated (alerts for dangerous conditions)
- [ ] Emergency shutdown/stop requirements captured (if applicable)
- [ ] Safe integration requirements with other systems documented
- [ ] Human override capabilities defined where needed
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "PERF-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "PERF"
# Human-readable check title
title = "Response Time Expectations"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.2.2 (Time behaviour)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "PERF-PRD-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "PERF"
# Human-readable check title
title = "Throughput Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.2.3 (Resource utilization), §4.2.2.4 (Capacity)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "PERF-PRD-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "PERF"
# Human-readable check title
title = "Capacity Planning Inputs"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "REL-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "REL"
# Human-readable check title
title = "Availability Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.5.2 (Availability), SOC 2 A1.1"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "REL-PRD-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "REL"
# Human-readable check title
title = "Recovery Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.5.4 (Recoverability), [ISO 22301:2019](https://www.iso.org/standard/75106.html) §8.4 (Business continuity plans), NIST 800-53 CP family"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "REL-PRD-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "REL"
# Human-readable check title
title = "Error Handling Expectations"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.5.3 (Fault tolerance)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "UX-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "UX"
# Human-readable check title
title = "User Experience Goals"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO 9241-11 §5 (Framework for usability), ISO/IEC 25010:2023 §4.2.4 (Interaction Capability)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "UX-PRD-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "UX"
# Human-readable check title
title = "Accessibility Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "[WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/) (A/AA/AAA levels), ISO/IEC 25010:2023 §4.2.4.7 (Accessibility), [EN 301 549](https://www.etsi.org/standards/en-301-549)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Accessibility standards referenced (WCAG 2.2 level — typically AA)
- [ ] Assistive technology support requirements stated
- [ ] Keyboard navigation requirements documented (WCAG 2.1.1)
- [ ] Screen reader compatibility requirements stated (WCAG 4.1.2)
- [ ] Color/contrast requirements noted (WCAG 1.4.3, 1.4.11)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "UX-PRD-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "UX"
# Human-readable check title
title = "Internationalization Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Supported languages listed
- [ ] Localization requirements documented
- [ ] Regional format requirements stated (dates, numbers, currency)
- [ ] RTL language support requirements noted
- [ ] Cultural considerations documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "UX-PRD-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "UX"
# Human-readable check title
title = "Device/Platform Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.8 (Flexibility — Installability, Adaptability)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Supported platforms listed (web, mobile, desktop)
- [ ] Browser requirements stated
- [ ] Mobile device requirements documented
- [ ] Offline capability requirements stated
- [ ] Responsive design requirements documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "UX-PRD-005"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "UX"
# Human-readable check title
title = "Inclusivity Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM (if applicable)"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "[ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) §4.2.4.8 (Inclusivity) — **NEW subcharacteristic in 2023 edition**"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
> **New in v1.2**: Inclusivity was added as a subcharacteristic of Interaction Capability in ISO/IEC 25010:2023. It addresses the widest possible range of users, including those with different backgrounds, abilities, and characteristics.

- [ ] Diverse user populations considered (age, culture, language, ability)
- [ ] Cognitive accessibility requirements documented (beyond WCAG)
- [ ] Support for users with temporary situational limitations considered
- [ ] Cultural sensitivity requirements stated (if applicable)
- [ ] Design for neurodiverse users considered (if applicable)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "MAINT-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "MAINT"
# Human-readable check title
title = "Documentation Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148 §6.6 (Information items)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "MAINT-PRD-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "MAINT"
# Human-readable check title
title = "Support Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "COMPL-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "COMPL"
# Human-readable check title
title = "Regulatory Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL (if applicable)"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "GDPR (EU personal data), HIPAA (US healthcare), PCI DSS (payment cards), SOX (financial reporting)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Applicable regulations identified (GDPR, HIPAA, SOX, PCI DSS, etc.)
- [ ] Compliance certification requirements stated
- [ ] Audit requirements documented
- [ ] Reporting requirements captured
- [ ] Data sovereignty requirements stated (GDPR Art. 44-49)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "COMPL-PRD-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "COMPL"
# Human-readable check title
title = "Industry Standards"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO 27001 (security), ISO 22301 (continuity), SOC 2 (trust services), ISO 9001 (quality)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "COMPL-PRD-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "COMPL"
# Human-readable check title
title = "Legal Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH (if applicable)"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "GDPR Art. 12-23 (Data subject rights), GDPR Art. 6-7 (Consent)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DATA-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DATA"
# Human-readable check title
title = "Data Ownership"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "GDPR Art. 4 (Definitions — controller, processor), GDPR Art. 26 (Joint controllers)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DATA-PRD-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DATA"
# Human-readable check title
title = "Data Quality Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "[ISO/IEC 25012](https://www.iso.org/standard/35736.html) (Data Quality model), GDPR Art. 5(1)(d) (Accuracy principle)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DATA-PRD-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DATA"
# Human-readable check title
title = "Data Lifecycle"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "GDPR Art. 5(1)(e) (Storage limitation), GDPR Art. 17 (Right to erasure)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "INT-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "INT"
# Human-readable check title
title = "External System Integration"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.3.2 (Interoperability), ISO/IEC/IEEE 29148 §6.3.4 (System interfaces)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "INT-PRD-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "INT"
# Human-readable check title
title = "API Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "[OpenAPI Specification](https://spec.openapis.org/oas/latest.html), RFC 6749 (OAuth for API auth)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "OPS-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "OPS"
# Human-readable check title
title = "Deployment Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "NIST 800-53 CM family (Configuration Management)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "OPS-PRD-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "OPS"
# Human-readable check title
title = "Monitoring Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "NIST 800-53 AU family (Audit and Accountability), SI family (System and Information Integrity)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Alerting requirements stated
- [ ] Dashboard requirements documented
- [ ] Log retention requirements captured
- [ ] Incident response requirements stated (NIST 800-53 IR family)
- [ ] Capacity monitoring requirements documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "TEST-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "TEST"
# Human-readable check title
title = "Acceptance Criteria"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148 §5.2.8 (Requirements verification), ISO/IEC/IEEE 29119-1 §4 (Test concepts)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "TEST-PRD-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "TEST"
# Human-readable check title
title = "Testability"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148 §5.2.5 (Characteristics of well-formed requirements), ISO/IEC 25010:2023 §4.2.7.4 (Testability)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DOC-PRD-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DOC"
# Human-readable check title
title = "Explicit Non-Applicability"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] If a section or requirement is intentionally omitted, it is explicitly stated in the document (e.g., "Not applicable because...")
- [ ] No silent omissions — every major checklist area is either present or has a documented reason for absence
- [ ] Reviewer can distinguish "author considered and excluded" from "author forgot"
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-PRD-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "No Technical Implementation Details"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No database schema definitions
- [ ] No API endpoint specifications
- [ ] No technology stack decisions
- [ ] No code snippets or pseudocode
- [ ] No infrastructure specifications
- [ ] No framework/library choices

**Where it belongs**: `DESIGN` (Overall Design)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-PRD-NO-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "No Architectural Decisions"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No microservices vs monolith decisions
- [ ] No database choice justifications
- [ ] No cloud provider selections
- [ ] No architectural pattern discussions
- [ ] No component decomposition

**Where it belongs**: `ADR` (Architecture Decision Records)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-PRD-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "No Implementation Tasks"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No sprint/iteration plans
- [ ] No task breakdowns
- [ ] No effort estimates
- [ ] No developer assignments
- [ ] No implementation timelines

**Where it belongs**: Project management tools (Jira, Linear, etc.) or Spec DESIGN
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-PRD-NO-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "No Spec-Level Design"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No detailed user flows
- [ ] No wireframes or UI specifications
- [ ] No algorithm descriptions
- [ ] No state machine definitions
- [ ] No detailed error handling logic

**Where it belongs**: `Spec DESIGN` (Spec Design)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DATA-PRD-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DATA"
# Human-readable check title
title = "No Data Schema Definitions"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No entity-relationship diagrams
- [ ] No table definitions
- [ ] No JSON schema specifications
- [ ] No data type specifications
- [ ] No field-level constraints

**Where it belongs**: Architecture and design documentation (domain model and schemas)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "INT-PRD-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "INT"
# Human-readable check title
title = "No API Specifications"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No REST endpoint definitions
- [ ] No request/response schemas
- [ ] No HTTP method specifications
- [ ] No authentication header specifications
- [ ] No error response formats

**Where it belongs**: API contract documentation (e.g., OpenAPI) or architecture and design documentation
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "TEST-PRD-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "TEST"
# Human-readable check title
title = "No Test Cases"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No detailed test scripts
- [ ] No test data specifications
- [ ] No automation code
- [ ] No test environment specifications

**Where it belongs**: Test plans, test suites, or QA documentation
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "OPS-PRD-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "OPS"
# Human-readable check title
title = "No Infrastructure Specifications"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No server specifications
- [ ] No Kubernetes manifests
- [ ] No Docker configurations
- [ ] No CI/CD pipeline definitions
- [ ] No monitoring tool configurations

**Where it belongs**: Infrastructure-as-code repositories or operations/infrastructure documentation
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEC-PRD-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEC"
# Human-readable check title
title = "No Security Implementation Details"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No encryption algorithm specifications
- [ ] No key management procedures
- [ ] No firewall rules
- [ ] No security tool configurations
- [ ] No penetration test results

**Where it belongs**: Security architecture documentation or ADRs
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "MAINT-PRD-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "MAINT"
# Human-readable check title
title = "No Code-Level Documentation"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No code comments
- [ ] No function/class documentation
- [ ] No inline code examples
- [ ] No debugging instructions

**Where it belongs**: Source code, README files, or developer documentation
```
`@/cpt:check`


---

## Template Structure

Headings, prompts, IDs, and examples that define the generated `template.md`
and `example.md` files. The PRD template covers: overview, actors, operational
context, scope, functional/non-functional requirements, interfaces, use cases,
acceptance criteria, dependencies, assumptions, and risks.

### Title (H1)

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-h1-title"
# Markdown heading level (1=H1 … 6=H6)
level = 1
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = false
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "PRD\\s*[—–-]\\s*.+"
# Suggested heading text template for authors
template = "PRD — {Module/Feature Name}"
# Brief writing instruction for content under this heading
prompt = "Title of product"
# Human description of this heading's purpose
description = "PRD document title (H1)."
# Example heading texts showing correct usage
examples = ["# PRD — TaskFlow"]
```
`@/cpt:heading`

### Overview

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-overview"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Overview"
# Human description of this heading's purpose
description = "High-level overview of the product and problem."
# Example heading texts showing correct usage
examples = ["## 1. Overview"]
```
`@/cpt:heading`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-overview-purpose"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Purpose"
# Human description of this heading's purpose
description = "Purpose of the PRD and the product."
# Example heading texts showing correct usage
examples = ["### 1.1 Purpose"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
{1-2 paragraphs: What is this system/module and what problem does it solve? What are the key features?}
```
`@/cpt:prompt`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

`@cpt:example`
```markdown
TaskFlow is a lightweight task management system for small teams, enabling task creation, assignment, and progress tracking with real-time notifications.
```
`@/cpt:example`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-overview-background"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Background / Problem Statement"
# Human description of this heading's purpose
description = "Background and problem statement."
# Example heading texts showing correct usage
examples = ["### 1.2 Background / Problem Statement"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
{2-3 paragraphs: Context, current pain points, why this capability is needed now.}
```
`@/cpt:prompt`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "semantic"
```
```markdown
- [ ] Background MUST describe current state and specific pain points
- [ ] MUST include target users and key problems solved
```
`@/cpt:rule`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

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

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-overview-goals"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Goals (Business Outcomes)"
# Human description of this heading's purpose
description = "Business outcomes and goals."
# Example heading texts showing correct usage
examples = ["### 1.3 Goals (Business Outcomes)"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
- {Goal 1: measurable business outcome}
- {Goal 2: measurable business outcome}
```
`@/cpt:prompt`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "semantic"
```
```markdown
- [ ] All goals MUST be measurable with concrete targets
  - VALID: "Reduce validation time from 15min to <30s" (quantified with baseline)
  - INVALID: "Improve validation speed" (no baseline, no target)
- [ ] Success criteria MUST include baseline, target, and timeframe
```
`@/cpt:rule`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

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

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-overview-glossary"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Glossary"
# Human description of this heading's purpose
description = "Definitions of key terms."
# Example heading texts showing correct usage
examples = ["### 1.4 Glossary"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
| Term | Definition |
|------|------------|
| {Term} | {Definition} |
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

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

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-actors"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Actors"
# Human description of this heading's purpose
description = "Actors (human and system) that interact with the product."
# Example heading texts showing correct usage
examples = ["## 2. Actors"]
```
`@/cpt:heading`

> **`@cpt:id`** — Identifier constraint. Defines an ID kind (template, references, task/priority rules). Output: `constraints.toml`.

`@cpt:id`
```toml
kind = "actor"
name = "Actor"
description = "An entity (human or system) that interacts with the product; used in PRD, and referenced by requirements/use cases."
required = false          # true = at least one ID of this kind must exist in artifact
task = false               # true = must carry task attr | false = prohibited | omit = optional
priority = false           # true = must carry priority attr | false = prohibited | omit = optional
template = "cpt-{system}-actor-{slug}"
examples = ["cpt-cypilot-actor-ai-assistant", "cpt-ex-ovwa-actor-user", "cpt-ex-ovwa-actor-macos"]
to_code = false              # true = ID is expected to appear in code via @cpt-* markers
headings = ["prd-actors"]  # heading constraint IDs where this identifier must be placed
```
`@/cpt:id`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
> **Note**: Stakeholder needs are managed at project/task level by steering committee. Document **actors** (users, systems) that interact with this module.
```
`@/cpt:prompt`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-actors-human"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Human Actors"
# Human description of this heading's purpose
description = "Human actors."
# Example heading texts showing correct usage
examples = ["### 2.1 Human Actors"]
```
`@/cpt:heading`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

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

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
**ID**: `cpt-{system}-actor-{slug}`

**Role**: {Description of what this actor does and their relationship to the system.}
**Needs**: {What this actor needs from the system.}
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

`@cpt:example`
```markdown
**ID**: `cpt-ex-task-flow-actor-member`

**Role**: Creates tasks, updates progress, and collaborates on assignments.

#### Team Lead

**ID**: `cpt-ex-task-flow-actor-lead`

**Role**: Assigns tasks, sets priorities, and monitors team workload.
```
`@/cpt:example`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-actors-system"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "System Actors"
# Human description of this heading's purpose
description = "System and external actors."
# Example heading texts showing correct usage
examples = ["### 2.2 System Actors"]
```
`@/cpt:heading`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

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

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
**ID**: `cpt-{system}-actor-{slug}`

**Role**: {Description of what this system actor does (external service, scheduler, etc.)}
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

`@cpt:example`
```markdown
**ID**: `cpt-ex-task-flow-actor-notifier`

**Role**: Sends alerts for due dates, assignments, and status changes.
```
`@/cpt:example`

### Operational Concept & Environment

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-operational-concept"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Operational Concept & Environment"
# Human description of this heading's purpose
description = "Operational concept and environment constraints."
# Example heading texts showing correct usage
examples = ["## 3. Operational Concept & Environment"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
> **Note**: Project-wide runtime, OS, architecture, lifecycle policy, and integration patterns defined in root PRD. Document only module-specific deviations here. **Delete this section if no special constraints.**
```
`@/cpt:prompt`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-operational-concept-constraints"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Module-Specific Environment Constraints"
# Human description of this heading's purpose
description = "Module-specific environment constraints beyond project defaults."
# Example heading texts showing correct usage
examples = ["### 3.1 Module-Specific Environment Constraints"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
{Only if this module has constraints beyond project defaults:}

- {Constraint 1, e.g., "Requires GPU acceleration for X"}
- {Constraint 2, e.g., "Incompatible with async runtime due to Y"}
- {Constraint 3, e.g., "Requires external dependency: Z library v2.0+"}
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

`@cpt:example`
```markdown
None.
```
`@/cpt:example`

### Scope

In-scope and out-of-scope boundaries.

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-scope"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Scope"
# Human description of this heading's purpose
description = "Scope of the product and release."
# Example heading texts showing correct usage
examples = ["## 4. Scope"]
```
`@/cpt:heading`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-scope-in"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "In Scope"
# Human description of this heading's purpose
description = "In-scope items."
# Example heading texts showing correct usage
examples = ["### 4.1 In Scope"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
- {Capability or feature that IS included}
- {Another capability}
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

`@cpt:example`
```markdown
- Task creation, assignment, and lifecycle tracking
- Real-time updates for task status changes
- Deadline notifications
```
`@/cpt:example`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-scope-out"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Out of Scope"
# Human description of this heading's purpose
description = "Out-of-scope items."
# Example heading texts showing correct usage
examples = ["### 4.2 Out of Scope"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
- {Capability explicitly NOT included in this PRD}
- {Future consideration not addressed now}
```
`@/cpt:prompt`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "semantic"
```
```markdown
- [ ] Non-goals MUST explicitly state what product does NOT do
```
`@/cpt:rule`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

`@cpt:example`
```markdown
- Time tracking, billing, or invoicing
- Cross-organization collaboration
```
`@/cpt:example`

### Functional Requirements

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-fr"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Functional Requirements"
# Human description of this heading's purpose
description = "Functional requirements section."
# Example heading texts showing correct usage
examples = ["## 5. Functional Requirements"]
```
`@/cpt:heading`

> **`@cpt:id`** — Identifier constraint. Defines an ID kind (template, references, task/priority rules). Output: `constraints.toml`.

`@cpt:id`
```toml
kind = "fr"
name = "Functional Requirement"
description = "A testable statement of required system behavior (WHAT the system must do)."
required = true          # true = at least one ID of this kind must exist in artifact
# task: omitted (optional) # true = must carry task attr | false = prohibited | omit = optional
priority = true            # true = must carry priority attr | false = prohibited | omit = optional
template = "cpt-{system}-fr-{slug}"
examples = ["cpt-cypilot-fr-validation", "cpt-ex-ovwa-fr-track-active-time", "cpt-ex-ovwa-fr-cli-controls"]
to_code = false              # true = ID is expected to appear in code via @cpt-* markers
headings = ["prd-fr"]  # heading constraint IDs where this identifier must be placed

[references.DECOMPOSITION]  # how this ID is referenced in DECOMPOSITION artifacts
# coverage: omitted (optional) # true = must reference | false = prohibited | omit = optional
# task: omitted (optional) # true = ref must carry task | false = prohibited | omit = optional
# priority: omitted (optional) # true = ref must carry priority | false = prohibited | omit = optional
headings = ["decomposition-entry"]  # target heading constraint in DECOMPOSITION
[references.DESIGN]  # how this ID is referenced in DESIGN artifacts
coverage = true            # true = must reference | false = referencing prohibited | omit = optional
# task: omitted (optional) # true = ref must carry task | false = prohibited | omit = optional
# priority: omitted (optional) # true = ref must carry priority | false = prohibited | omit = optional
headings = ["design-arch-overview-drivers"]  # target heading constraint in DESIGN
[references.FEATURE]  # how this ID is referenced in FEATURE artifacts
# coverage: omitted (optional) # true = must reference | false = prohibited | omit = optional
# task: omitted (optional) # true = ref must carry task | false = prohibited | omit = optional
# priority: omitted (optional) # true = ref must carry priority | false = prohibited | omit = optional
headings = ["feature-context-purpose"]  # target heading constraint in FEATURE
```
`@/cpt:id`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
> **Testing strategy**: All requirements verified via automated tests (unit, integration, e2e) targeting 90%+ code coverage unless otherwise specified. Document verification method only for non-test approaches (analysis, inspection, demonstration).

Functional requirements define WHAT the system must do. Group by feature area or priority tier.
```
`@/cpt:prompt`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

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

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

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

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

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

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

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

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-nfr"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Non-Functional Requirements"
# Human description of this heading's purpose
description = "Non-functional requirements section."
# Example heading texts showing correct usage
examples = ["## 6. Non-Functional Requirements"]
```
`@/cpt:heading`

> **`@cpt:id`** — Identifier constraint. Defines an ID kind (template, references, task/priority rules). Output: `constraints.toml`.

`@cpt:id`
```toml
kind = "nfr"
name = "Non-functional Requirement"
description = "A measurable quality attribute requirement (performance, security, reliability, usability, etc.)."
required = true          # true = at least one ID of this kind must exist in artifact
# task: omitted (optional) # true = must carry task attr | false = prohibited | omit = optional
priority = true            # true = must carry priority attr | false = prohibited | omit = optional
template = "cpt-{system}-nfr-{slug}"
examples = ["cpt-cypilot-nfr-validation-performance", "cpt-ex-ovwa-nfr-privacy-local-only", "cpt-ex-ovwa-nfr-low-overhead"]
to_code = false              # true = ID is expected to appear in code via @cpt-* markers
headings = ["prd-nfr"]  # heading constraint IDs where this identifier must be placed

[references.DECOMPOSITION]  # how this ID is referenced in DECOMPOSITION artifacts
# coverage: omitted (optional) # true = must reference | false = prohibited | omit = optional
# task: omitted (optional) # true = ref must carry task | false = prohibited | omit = optional
# priority: omitted (optional) # true = ref must carry priority | false = prohibited | omit = optional
headings = ["decomposition-entry"]  # target heading constraint in DECOMPOSITION
[references.DESIGN]  # how this ID is referenced in DESIGN artifacts
coverage = true            # true = must reference | false = referencing prohibited | omit = optional
# task: omitted (optional) # true = ref must carry task | false = prohibited | omit = optional
# priority: omitted (optional) # true = ref must carry priority | false = prohibited | omit = optional
headings = ["design-arch-overview-drivers"]  # target heading constraint in DESIGN
[references.FEATURE]  # how this ID is referenced in FEATURE artifacts
# coverage: omitted (optional) # true = must reference | false = prohibited | omit = optional
# task: omitted (optional) # true = ref must carry task | false = prohibited | omit = optional
# priority: omitted (optional) # true = ref must carry priority | false = prohibited | omit = optional
headings = ["feature-context-purpose"]  # target heading constraint in FEATURE
```
`@/cpt:id`

`@/cpt:prompt`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "semantic"
```
```markdown
- [ ] NFRs MUST have measurable thresholds with units and conditions
- [ ] NFR exclusions MUST have explicit reasoning
```
`@/cpt:rule`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-nfr-inclusions"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = false
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "NFR Inclusions"
# Human description of this heading's purpose
description = "Non-functional requirements that deviate from or extend project defaults."
# Example heading texts showing correct usage
examples = ["### 6.1 Module-Specific NFRs"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
{Only include this section if there are NFRs that deviate from or extend project defaults.}
```
`@/cpt:prompt`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

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

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
- [ ] `p1` - **ID**: `cpt-{system}-nfr-{slug}`

The system **MUST** {measurable NFR with specific thresholds, e.g., "respond within 50ms at p95" (stricter than project default)}.

**Threshold**: {Quantitative target with units and conditions}

**Rationale**: {Why this module needs different/additional NFR}

**Verification Method** (optional): {Only if non-standard approach needed}
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

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

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-nfr-exclusions"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "NFR Exclusions"
# Human description of this heading's purpose
description = "Explicit non-functional requirement exclusions."
# Example heading texts showing correct usage
examples = ["### 6.2 NFR Exclusions"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
{Document any project-default NFRs that do NOT apply to this module}

- {Default NFR name}: {Reason for exclusion}
```
`@/cpt:prompt`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "semantic"
```
```markdown
- [ ] Intentional exclusions MUST list N/A checklist categories with reasoning
```
`@/cpt:rule`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

`@cpt:example`
```markdown
- **Accessibility** (UX-PRD-002): Not applicable — MVP targets internal teams with standard desktop browsers
- **Internationalization** (UX-PRD-003): Not applicable — English-only for initial release
- **Regulatory Compliance** (COMPL-PRD-001/002/003): Not applicable — No PII or regulated data in MVP scope
```
`@/cpt:example`

### Public Interfaces

API surface and external integration contracts.

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-public-interfaces"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Public Library Interfaces"
# Human description of this heading's purpose
description = "Public library interfaces and integration contracts."
# Example heading texts showing correct usage
examples = ["## 7. Public Library Interfaces"]
```
`@/cpt:heading`

> **`@cpt:id`** — Identifier constraint. Defines an ID kind (template, references, task/priority rules). Output: `constraints.toml`.

`@cpt:id`
```toml
kind = "interface"
name = "Public Interface"
description = "A public API surface (library interface, protocol, CLI contract) provided by the system."
required = false          # true = at least one ID of this kind must exist in artifact
# task: omitted (optional) # true = must carry task attr | false = prohibited | omit = optional
# priority: omitted (optional) # true = must carry priority | false = prohibited | omit = optional
template = "cpt-{system}-interface-{slug}"
examples = ["cpt-cypilot-interface-cli-json", "cpt-ex-ovwa-interface-cli", "cpt-ex-ovwa-interface-ipc-protocol"]
to_code = false              # true = ID is expected to appear in code via @cpt-* markers
headings = ["prd-public-interfaces"]  # heading constraint IDs where this identifier must be placed

[references.DESIGN]  # how this ID is referenced in DESIGN artifacts
coverage = true            # true = must reference | false = referencing prohibited | omit = optional
# task: omitted (optional) # true = ref must carry task | false = prohibited | omit = optional
# priority: omitted (optional) # true = ref must carry priority | false = prohibited | omit = optional
headings = ["design-tech-arch-api-contracts"]  # target heading constraint in DESIGN
```
`@/cpt:id`

> **`@cpt:id`** — Identifier constraint. Defines an ID kind (template, references, task/priority rules). Output: `constraints.toml`.

`@cpt:id`
```toml
kind = "contract"
name = "Integration Contract"
description = "An external integration contract (data format/protocol/compatibility expectations) with another system."
required = false          # true = at least one ID of this kind must exist in artifact
# task: omitted (optional) # true = must carry task attr | false = prohibited | omit = optional
# priority: omitted (optional) # true = must carry priority | false = prohibited | omit = optional
template = "cpt-{system}-contract-{slug}"
examples = ["cpt-ex-ovwa-contract-macos-notification-center", "cpt-ex-ovwa-contract-launchd", "cpt-cypilot-contract-openai-api"]
to_code = false              # true = ID is expected to appear in code via @cpt-* markers
headings = ["prd-public-interfaces"]  # heading constraint IDs where this identifier must be placed

[references.DESIGN]  # how this ID is referenced in DESIGN artifacts
coverage = true            # true = must reference | false = referencing prohibited | omit = optional
# task: omitted (optional) # true = ref must carry task | false = prohibited | omit = optional
# priority: omitted (optional) # true = ref must carry priority | false = prohibited | omit = optional
headings = ["design-tech-arch-api-contracts"]  # target heading constraint in DESIGN
```
`@/cpt:id`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
Define the public API surface, versioning/compatibility guarantees, and integration contracts provided by this library.
```
`@/cpt:prompt`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-public-interfaces-api"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Public API Surface"
# Human description of this heading's purpose
description = "Public API surface."
# Example heading texts showing correct usage
examples = ["### 7.1 Public API Surface"]
```
`@/cpt:heading`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

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

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
- [ ] `p1` - **ID**: `cpt-{system}-interface-{slug}`

**Type**: {Rust module/trait/struct | REST API | CLI | Protocol | Data format}

**Stability**: {stable | unstable | experimental}

**Description**: {What this interface provides}

**Breaking Change Policy**: {e.g., Major version bump required}
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

`@cpt:example`
```markdown
None.
```
`@/cpt:example`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-public-interfaces-external-contracts"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "External Integration Contracts"
# Human description of this heading's purpose
description = "External integration contracts."
# Example heading texts showing correct usage
examples = ["### 7.2 External Integration Contracts"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
Contracts this library expects from external systems or provides to downstream clients.
```
`@/cpt:prompt`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

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

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
- [ ] `p2` - **ID**: `cpt-{system}-contract-{slug}`

**Direction**: {provided by library | required from client}

**Protocol/Format**: {e.g., HTTP/REST, gRPC, JSON Schema}

**Compatibility**: {Backward/forward compatibility guarantees}
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

`@cpt:example`
```markdown
None.
```
`@/cpt:example`

### Use Cases

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-use-cases"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Use Cases"
# Human description of this heading's purpose
description = "Use cases section."
# Example heading texts showing correct usage
examples = ["## 8. Use Cases"]
```
`@/cpt:heading`

> **`@cpt:id`** — Identifier constraint. Defines an ID kind (template, references, task/priority rules). Output: `constraints.toml`.

`@cpt:id`
```toml
kind = "usecase"
name = "Use Case"
description = "An end-to-end interaction scenario (actor + goal + flow) that clarifies behavior beyond individual requirements."
required = true          # true = at least one ID of this kind must exist in artifact
# task: omitted (optional) # true = must carry task attr | false = prohibited | omit = optional
# priority: omitted (optional) # true = must carry priority | false = prohibited | omit = optional
template = "cpt-{system}-usecase-{slug}"
examples = ["cpt-ex-ovwa-usecase-run-and-alert", "cpt-ex-ovwa-usecase-configure-limit", "cpt-ex-ovwa-usecase-control-session"]
to_code = false              # true = ID is expected to appear in code via @cpt-* markers
headings = ["prd-use-cases"]  # heading constraint IDs where this identifier must be placed

[references.DESIGN]  # how this ID is referenced in DESIGN artifacts
# coverage: omitted (optional) # true = must reference | false = prohibited | omit = optional
# task: omitted (optional) # true = ref must carry task | false = prohibited | omit = optional
# priority: omitted (optional) # true = ref must carry priority | false = prohibited | omit = optional
headings = ["design-tech-arch-seq"]  # target heading constraint in DESIGN
[references.FEATURE]  # how this ID is referenced in FEATURE artifacts
# coverage: omitted (optional) # true = must reference | false = prohibited | omit = optional
# task: omitted (optional) # true = ref must carry task | false = prohibited | omit = optional
# priority: omitted (optional) # true = ref must carry priority | false = prohibited | omit = optional
headings = ["feature-actor-flow"]  # target heading constraint in FEATURE
```
`@/cpt:id`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
Optional: Include when interaction flows add clarity beyond requirement statements.
```
`@/cpt:prompt`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

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

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "semantic"
```
```markdown
- [ ] Use cases MUST cover primary user journeys
- [ ] Use cases MUST include alternative flows for error scenarios
- [ ] Use case IDs follow: `cpt-{system}-usecase-{slug}`
```
`@/cpt:rule`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

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

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-acceptance-criteria"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Acceptance Criteria"
# Human description of this heading's purpose
description = "Acceptance criteria for delivery."
# Example heading texts showing correct usage
examples = ["## 9. Acceptance Criteria"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
Business-level acceptance criteria for the PRD as a whole.

- [ ] {Testable criterion that validates a key business outcome}
- [ ] {Another testable criterion}
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

`@cpt:example`
```markdown
- [ ] Tasks can be created/assigned in under 30 seconds
- [ ] Task updates propagate to all clients within 2 seconds
- [ ] Overdue alerts are delivered within 1 minute
```
`@/cpt:example`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-dependencies"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Dependencies"
# Human description of this heading's purpose
description = "Dependencies required to deliver the PRD."
# Example heading texts showing correct usage
examples = ["## 10. Dependencies"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
| Dependency | Description | Criticality |
|------------|-------------|-------------|
| {Service/System} | {What it provides} | {p1/p2/p3} |
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

`@cpt:example`
```markdown
| Dependency | Description | Criticality |
|------------|-------------|-------------|
| Notification delivery | Push notification channel for deadlines/status changes | p2 |
```
`@/cpt:example`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-assumptions"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Assumptions"
# Human description of this heading's purpose
description = "Assumptions that must hold."
# Example heading texts showing correct usage
examples = ["## 11. Assumptions"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
- {Assumption about environment, users, or dependent systems}
```
`@/cpt:prompt`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "semantic"
```
```markdown
- [ ] Key assumptions MUST be explicitly stated
- [ ] Open questions MUST have owners and target resolution dates
```
`@/cpt:rule`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

`@cpt:example`
```markdown
- Users have modern browsers and reliable connectivity for real-time updates
- The initial deployment is cloud-hosted
```
`@/cpt:example`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "prd-risks"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Risks"
# Human description of this heading's purpose
description = "Risks and mitigations."
# Example heading texts showing correct usage
examples = ["## 12. Risks"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `template.md`.

`@cpt:prompt`
```markdown
| Risk | Impact | Mitigation |
|------|--------|------------|
| {Risk description} | {Potential impact} | {Mitigation strategy} |
```
`@/cpt:prompt`

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "semantic"
```
```markdown
- [ ] Risks and uncertainties MUST be documented with impact and mitigation
```
`@/cpt:rule`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `examples/example.md`.

`@cpt:example`
```markdown
| Risk | Impact | Mitigation |
|------|--------|------------|
| Adoption risk | Teams may resist switching tools | Focus on migration path and quick wins |
| Scale risk | Real-time may not scale beyond 50 concurrent users | Load testing before launch |
```
`@/cpt:example`
