# FEATURES (Features Manifest) Expert Checklist

**Artifact**: Features Manifest (FEATURES)  
**Version**: 1.0  
**Purpose**: Comprehensive quality checklist for Features Manifest artifacts

---

## Prerequisites

Before starting the review, confirm:

- [ ] I understand this checklist validates FEATURES artifacts
- [ ] I will follow the Applicability Context rules below
- [ ] I will check ALL items in MUST HAVE sections
- [ ] I will verify ALL items in MUST NOT HAVE sections
- [ ] I will document any violations found
- [ ] I will provide specific feedback for each failed check
- [ ] I will complete the Final Checklist and provide a review report

---

## Applicability Context

Before evaluating each checklist item, the expert MUST:

1. **Understand the project's domain** — What kind of project is this FEATURES manifest for? (e.g., product application, framework, library, platform)

2. **Determine applicability for each requirement** — Not all checklist items apply to all features manifests:
   - A small utility project may not need complex dependency tracking
   - A framework project may not need user-facing feature prioritization
   - A library project may not need stakeholder visibility tracking

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

# MUST HAVE

---

## BUSINESS Expertise (BIZ)

### BIZ-FEAT-001: Requirements Coverage
**Severity**: CRITICAL

- [ ] ALL functional requirements from the requirements source are covered by at least one feature
- [ ] ALL non-functional requirements from the requirements source are covered by at least one feature
- [ ] No orphaned requirements (requirements not assigned to any feature)
- [ ] Coverage mapping is explicit (Requirements Covered field)
- [ ] Coverage references are consistent (IDs/links/names match the source requirements)
- [ ] Priority alignment between requirements and features

### BIZ-FEAT-002: Feature Scope Clarity
**Severity**: CRITICAL

- [ ] Each feature has a clear, one-line Purpose
- [ ] Scope bullets are concrete and actionable
- [ ] Scope boundaries are clear (what's in vs out)
- [ ] Features don't overlap in scope
- [ ] Features are decomposed to implementable units
- [ ] Feature names are descriptive and domain-meaningful

### BIZ-FEAT-003: Status Accuracy
**Severity**: HIGH

- [ ] Status reflects actual implementation state
- [ ] Status values use a consistent vocabulary (e.g., Planned, In Design, In Progress, Done)
- [ ] Status is consistent with evidence (specs exist, code exists, release notes, etc.)
- [ ] "Done" features have acceptance criteria met and validation evidence captured (where applicable)

### BIZ-FEAT-004: Value Delivery Tracking
**Severity**: MEDIUM

- [ ] Features ordered by priority (implicit or explicit)
- [ ] Core/foundational features listed first
- [ ] Dependencies reflect implementation order
- [ ] MVP features identifiable
- [ ] Feature groupings support incremental delivery

### BIZ-FEAT-005: Stakeholder Visibility
**Severity**: MEDIUM

- [ ] Status overview provides at-a-glance progress
- [ ] Feature list is navigable and scannable
- [ ] Status meanings are documented
- [ ] Progress is trackable over time
- [ ] Blockers are visible through status

### BIZ-FEAT-006: Ownership & Targeting
**Severity**: MEDIUM

- [ ] Each feature has an owner (person or team) when applicable
- [ ] Target release/milestone is specified when applicable

---

## ARCHITECTURE Expertise (ARCH)

### ARCH-FEAT-001: Dependency Graph Quality
**Severity**: CRITICAL

- [ ] All dependencies are explicit (Depends On field)
- [ ] All blocks are explicit (Blocks field)
- [ ] No circular dependencies
- [ ] Dependencies form a valid DAG (Directed Acyclic Graph)
- [ ] Foundation features have no dependencies
- [ ] Dependency links are valid (reference existing features)

### ARCH-FEAT-002: Phase Decomposition
**Severity**: HIGH

- [ ] Every feature defines at least one milestone/phase
- [ ] Phases represent meaningful implementation milestones
- [ ] Phase descriptions are clear and actionable
- [ ] Phase status aligns with overall feature status
- [ ] "Done" features have ALL milestones completed
- [ ] Phase dependencies are satisfiable

### ARCH-FEAT-003: Modularity
**Severity**: HIGH

- [ ] Features are cohesive (related functionality grouped)
- [ ] Features have low coupling (minimal dependencies)
- [ ] Features map to architectural components/modules
- [ ] Features can be implemented independently (given dependencies)
- [ ] Features support parallel development

### ARCH-FEAT-004: Principles Coverage
**Severity**: MEDIUM

- [ ] Principles from DESIGN are referenced where relevant
- [ ] Features that embody principles reference them
- [ ] Principle coverage is traceable
- [ ] No principles are orphaned (if applicable)

### ARCH-FEAT-005: Constraints Coverage
**Severity**: MEDIUM

- [ ] Constraints from DESIGN are referenced where relevant
- [ ] Features affected by constraints document them
- [ ] Constraint impact is traceable
- [ ] Constraint compliance is trackable

### ARCH-FEAT-006: Feature Directory Structure
**Severity**: HIGH

- [ ] Each feature has a canonical location where details live (link to a spec, doc, epic, or ticket)
- [ ] Any feature that is not in a planned/not-started state has a detailed spec available
- [ ] Links are valid and point to the correct feature
- [ ] No orphaned specs/docs that are not referenced by any feature entry

---

## ⚡ PERFORMANCE Expertise (PERF)

### PERF-FEAT-001: Performance Requirements Distribution
**Severity**: MEDIUM

- [ ] Performance-related NFRs assigned to relevant features
- [ ] Latency requirements distributed appropriately
- [ ] Throughput requirements distributed appropriately
- [ ] Resource constraints assigned to relevant features
- [ ] No performance requirements orphaned

### PERF-FEAT-002: Performance Impact Visibility
**Severity**: MEDIUM

- [ ] Features with significant performance impact identified
- [ ] Performance-critical features prioritized appropriately
- [ ] Performance dependencies considered in ordering
- [ ] Caching features in correct dependency order
- [ ] Optimization features scheduled after baseline

---

## 🔒 SECURITY Expertise (SEC)

### SEC-FEAT-001: Security Requirements Distribution
**Severity**: CRITICAL

- [ ] Authentication requirements assigned to feature(s)
- [ ] Authorization requirements assigned to feature(s)
- [ ] Data protection requirements assigned to feature(s)
- [ ] Audit requirements assigned to feature(s)
- [ ] Security features prioritized appropriately (early)

### SEC-FEAT-002: Security Feature Dependencies
**Severity**: HIGH

- [ ] Security features are foundational (early in dependency chain)
- [ ] Features depending on security reference security features
- [ ] No security-dependent features skip security feature dependencies
- [ ] Security constraints referenced in affected features
- [ ] Compliance features scheduled appropriately

### SEC-FEAT-003: Security Coverage
**Severity**: HIGH

- [ ] No security-sensitive functionality without security feature dependency
- [ ] User data features depend on data protection features
- [ ] API features depend on authentication features
- [ ] Admin features depend on authorization features
- [ ] Audit trail features complete before audit-required features

---

## 🛡️ RELIABILITY Expertise (REL)

### REL-FEAT-001: Reliability Requirements Distribution
**Severity**: HIGH

- [ ] Availability requirements assigned to relevant features
- [ ] Error handling requirements distributed appropriately
- [ ] Recovery requirements assigned to relevant features
- [ ] Resilience patterns assigned to relevant features
- [ ] No reliability requirements orphaned

### REL-FEAT-002: Reliability Feature Dependencies
**Severity**: MEDIUM

- [ ] Error handling features foundational
- [ ] Monitoring features scheduled early
- [ ] Recovery features in correct dependency order
- [ ] Graceful degradation features properly sequenced
- [ ] Health check features scheduled before dependent features

---

## 📊 DATA Expertise (DATA)

### DATA-FEAT-001: Data Requirements Distribution
**Severity**: HIGH

- [ ] Data model features foundational
- [ ] Data validation features in correct order
- [ ] Data migration features properly sequenced
- [ ] Data governance features appropriately placed
- [ ] No data requirements orphaned

### DATA-FEAT-002: Data Feature Dependencies
**Severity**: HIGH

- [ ] Schema features before data manipulation features
- [ ] Validation features before data entry features
- [ ] Data access features before data presentation features
- [ ] Data integrity features properly sequenced
- [ ] Backup/recovery features in correct order

---

## 🔌 INTEGRATION Expertise (INT)

### INT-FEAT-001: Integration Requirements Distribution
**Severity**: HIGH

- [ ] External integration requirements assigned to features
- [ ] API features properly sequenced
- [ ] Protocol features foundational
- [ ] Integration testing features scheduled appropriately
- [ ] No integration requirements orphaned

### INT-FEAT-002: Integration Feature Dependencies
**Severity**: MEDIUM

- [ ] API foundation features before consuming features
- [ ] Authentication features before protected API features
- [ ] Contract features before implementation features
- [ ] Integration features depend on core features
- [ ] Third-party integration features properly sequenced

---

## 🖥️ OPERATIONS Expertise (OPS)

### OPS-FEAT-001: Operational Requirements Distribution
**Severity**: MEDIUM

- [ ] Deployment requirements assigned to features
- [ ] Monitoring requirements assigned to features
- [ ] Logging requirements assigned to features
- [ ] Configuration requirements assigned to features
- [ ] No operational requirements orphaned

### OPS-FEAT-002: Operational Feature Dependencies
**Severity**: MEDIUM

- [ ] Infrastructure features foundational
- [ ] Configuration features early in dependency chain
- [ ] Logging features before features that need logging
- [ ] Monitoring features appropriately sequenced
- [ ] Alerting features after monitoring features

---

## 🔧 MAINTAINABILITY Expertise (MAINT)

### MAINT-FEAT-001: Maintainability Considerations
**Severity**: MEDIUM

- [ ] Documentation features appropriately scheduled
- [ ] Technical debt features identified and scheduled
- [ ] Refactoring features properly sequenced
- [ ] Migration features in correct order
- [ ] Deprecation features tracked

### MAINT-FEAT-002: Feature Organization
**Severity**: MEDIUM

- [ ] Feature naming consistent
- [ ] Feature slugs follow kebab-case
- [ ] Feature numbering sequential
- [ ] Feature grouping logical
- [ ] Feature descriptions consistent in style

---

## 🧪 TESTING Expertise (TEST)

### TEST-FEAT-001: Testing Requirements Distribution
**Severity**: MEDIUM

- [ ] Testing infrastructure features scheduled early
- [ ] Test data features appropriately placed
- [ ] Test automation features properly sequenced
- [ ] Testing dependencies explicit
- [ ] No testing requirements orphaned

### TEST-FEAT-002: Testability Tracking
**Severity**: MEDIUM

- [ ] Features with complex testing needs identified
- [ ] Integration testing features in correct order
- [ ] E2E testing features after all dependencies
- [ ] Performance testing features after baseline
- [ ] Security testing features after security features

---

## 📜 COMPLIANCE Expertise (COMPL)

### COMPL-FEAT-001: Compliance Requirements Distribution
**Severity**: HIGH (if applicable)

- [ ] Regulatory requirements assigned to features
- [ ] Audit trail features appropriately scheduled
- [ ] Compliance reporting features in correct order
- [ ] Privacy features properly sequenced
- [ ] No compliance requirements orphaned

### COMPL-FEAT-002: Compliance Feature Dependencies
**Severity**: MEDIUM (if applicable)

- [ ] Privacy features before data collection features
- [ ] Consent features before data processing features
- [ ] Audit features before auditable operations
- [ ] Compliance validation features appropriately placed
- [ ] Reporting features after data collection features

---

## 👤 USABILITY Expertise (UX)

### UX-FEAT-001: User Experience Requirements Distribution
**Severity**: MEDIUM

- [ ] Accessibility requirements assigned to relevant features
- [ ] Internationalization requirements distributed
- [ ] Responsive design requirements distributed
- [ ] User workflow features properly sequenced
- [ ] No UX requirements orphaned

### UX-FEAT-002: UX Feature Dependencies
**Severity**: MEDIUM

- [ ] Core UI features foundational
- [ ] Navigation features before detailed features
- [ ] Feedback features appropriately placed
- [ ] Help/documentation features scheduled
- [ ] Onboarding features in correct order

---

## Deliberate Omissions

### DOC-FEAT-001: Explicit Non-Applicability
**Severity**: CRITICAL

- [ ] If a section or requirement is intentionally omitted, it is explicitly stated in the document (e.g., "Not applicable because...")
- [ ] No silent omissions — every major checklist area is either present or has a documented reason for absence
- [ ] Reviewer can distinguish "author considered and excluded" from "author forgot"

---

# MUST NOT HAVE

---

## ❌ ARCH-FEAT-NO-001: No Feature Implementation Details
**Severity**: CRITICAL

**What to check**:
- [ ] No user flows or algorithms
- [ ] No state machines or decision trees
- [ ] No detailed error handling logic
- [ ] No step-by-step implementation guides
- [ ] No low-level implementation pseudo-code
- [ ] No code snippets

**Where it belongs**: Feature specification / implementation design documentation

---

## ❌ ARCH-FEAT-NO-002: No Architectural Details
**Severity**: HIGH

**What to check**:
- [ ] No domain model definitions
- [ ] No API contract specifications
- [ ] No component interaction details
- [ ] No database schema details
- [ ] No infrastructure specifications

**Where it belongs**: `DESIGN`

---

## ❌ ARCH-FEAT-NO-003: No Decision Rationales
**Severity**: HIGH

**What to check**:
- [ ] No "why we chose X" explanations
- [ ] No pros/cons analysis
- [ ] No alternative considerations
- [ ] No decision justifications
- [ ] No historical context

**Where it belongs**: Decision record / architecture decision log

---

## ❌ BIZ-FEAT-NO-001: No Product Requirements
**Severity**: HIGH

**What to check**:
- [ ] No vision statements
- [ ] No actor definitions
- [ ] No functional requirement definitions
- [ ] No use case definitions
- [ ] No NFR definitions

**Where it belongs**: Requirements / Product specification document

---

## ❌ BIZ-FEAT-NO-002: No Task-Level Tracking
**Severity**: MEDIUM

**What to check**:
- [ ] No individual developer tasks
- [ ] No sprint/iteration assignments
- [ ] No effort estimates
- [ ] No daily/weekly progress notes
- [ ] No bug tracking

**Where it belongs**: Project management tools (Jira, Linear, etc.)

---

## ❌ DATA-FEAT-NO-001: No Data Schema Details
**Severity**: MEDIUM

**What to check**:
- [ ] No entity definitions
- [ ] No table structures
- [ ] No field specifications
- [ ] No relationship diagrams
- [ ] No migration scripts

**Where it belongs**: Central data model documentation or a feature specification

---

## ❌ INT-FEAT-NO-001: No API Specifications
**Severity**: MEDIUM

**What to check**:
- [ ] No endpoint definitions
- [ ] No request/response schemas
- [ ] No authentication details
- [ ] No rate limiting specs
- [ ] No versioning details

**Where it belongs**: API contract documentation (e.g., OpenAPI) or central architecture design

---

## ❌ TEST-FEAT-NO-001: No Test Cases
**Severity**: MEDIUM

**What to check**:
- [ ] No test implementations
- [ ] No test data
- [ ] No acceptance test scripts
- [ ] No test automation code
- [ ] No test results

**Where it belongs**: Test documentation or test code

---

## ❌ OPS-FEAT-NO-001: No Operational Details
**Severity**: MEDIUM

**What to check**:
- [ ] No deployment scripts
- [ ] No configuration details
- [ ] No monitoring configurations
- [ ] No runbook procedures
- [ ] No incident response procedures

**Where it belongs**: Operations documentation or infrastructure code

---

## ❌ MAINT-FEAT-NO-001: No Code Content
**Severity**: HIGH

**What to check**:
- [ ] No source code
- [ ] No configuration files
- [ ] No build scripts
- [ ] No infrastructure code
- [ ] No documentation content (just references)

**Where it belongs**: Source code repository

---

# Format Validation

---

## FORMAT-001: Feature Entry Format
**Severity**: CRITICAL

- [ ] Each feature entry has a unique name/title
- [ ] Each feature entry includes a stable identifier (ID) or a stable link
- [ ] Entries are consistently formatted across the document
- [ ] If numbering is used, it is sequential and stable

## FORMAT-002: Required Fields Present
**Severity**: CRITICAL

- [ ] **Purpose**: One-line description
- [ ] **Status**: Valid status value
- [ ] **Depends On**: None or feature links
- [ ] **Blocks**: None or feature links
- [ ] **Scope**: Bulleted list
- [ ] **Requirements Covered**: References to requirements (IDs, links, or names)
- [ ] **Phases**: Phase list with status

## FORMAT-003: Phase Format
**Severity**: HIGH

- [ ] Phase naming is consistent
- [ ] Phase status vocabulary is consistent
- [ ] Phase description meaningful
- [ ] Sequential phase numbering within feature
- [ ] Phase dependencies properly formatted (if present)

## FORMAT-004: Identifier Consistency
**Severity**: HIGH

- [ ] Identifiers (if used) follow a single agreed convention
- [ ] Identifiers are unique within the document
- [ ] References to other artifacts use the same convention consistently

---

# Validation Summary

## Final Checklist

Confirm before reporting results:

- [ ] I checked ALL items in MUST HAVE sections
- [ ] I verified ALL items in MUST NOT HAVE sections
- [ ] I documented all violations found
- [ ] I provided specific feedback for each failed check
- [ ] All critical issues have been reported

### Explicit Handling Verification

For each major checklist category (BIZ, ARCH, MAINT, TEST), confirm:

- [ ] Category is addressed in the document, OR
- [ ] Category is explicitly marked "Not applicable" with reasoning in the document, OR
- [ ] Category absence is reported as a violation (with applicability justification)

**No silent omissions allowed** — every category must have explicit disposition

---

## Reporting Readiness Checklist

- [ ] I will report every identified issue (no omissions)
- [ ] I will report only issues (no "everything looks good" sections)
- [ ] I will use the exact report format defined below (no deviations)
- [ ] Each reported issue will include Why Applicable (applicability justification)
- [ ] Each reported issue will include Evidence (quote/location)
- [ ] Each reported issue will include Why it matters (impact)
- [ ] Each reported issue will include a Proposal (concrete fix + acceptance criteria)
- [ ] I will avoid vague statements and use precise, verifiable language

---

## Reporting

Report **only** problems (do not list what is OK).

For each issue include:

- **Why Applicable**: Explain why this requirement applies to this specific FEATURES manifest's context (e.g., "This project has multiple interdependent features, therefore dependency tracking is required")
- **Issue**: What is wrong (requirement missing or incomplete)
- **Evidence**: Quote the exact text or describe the exact location in the artifact (or note "No mention found")
- **Why it matters**: Impact (risk, cost, user harm, compliance)
- **Proposal**: Concrete fix (what to change/add/remove) with clear acceptance criteria

Recommended output format for chat:

```markdown
## Review Report (Issues Only)

### 1. {Short issue title}

**Checklist Item**: `{CHECKLIST-ID}` — {Checklist item title}

**Severity**: CRITICAL|HIGH|MEDIUM|LOW

#### Why Applicable

{Explain why this requirement applies to this FEATURES manifest's context. E.g., "This project targets multiple releases, therefore milestone tracking is required."}

#### Issue

{What is wrong — requirement is missing, incomplete, or not explicitly marked as not applicable}

#### Evidence

{Quote the exact text or describe the exact location in the artifact. If requirement is missing entirely, state "No mention of [requirement] found in the document"}

#### Why It Matters

{Impact: risk, cost, user harm, compliance}

#### Proposal

{Concrete fix: what to change/add/remove, with clear acceptance criteria}

---

### 2. {Short issue title}

**Checklist Item**: `{CHECKLIST-ID}` — {Checklist item title}

**Severity**: CRITICAL|HIGH|MEDIUM|LOW

#### Why Applicable

{...}

#### Issue

{...}

---

...
```

---

## Reporting Commitment

- [ ] I reported all issues I found
- [ ] I used the exact report format defined in this checklist (no deviations)
- [ ] I included Why Applicable justification for each issue
- [ ] I included evidence and impact for each issue
- [ ] I proposed concrete fixes for each issue
- [ ] I did not hide or omit known problems
- [ ] I verified explicit handling for all major checklist categories
- [ ] I am ready to iterate on the proposals and re-review after changes
