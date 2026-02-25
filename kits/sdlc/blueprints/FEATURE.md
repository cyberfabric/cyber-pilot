# FEATURE Blueprint
<!-- 
  Blueprint for Feature Specification Documents.
  
  This file is the single source of truth for:
  - template.md generation (from @cpt:heading + @cpt:prompt markers)
  - example.md generation (from @cpt:heading examples + @cpt:example markers)
  - rules.md generation (from @cpt:rules + @cpt:rule markers)
  - checklist.md generation (from @cpt:checklist + @cpt:check markers)
  - constraints.toml contributions (from @cpt:heading + @cpt:id markers)
  
  All text between markers is ignored by the generator.
  
  FEATURE defines precise behavior using CDSL (Context-Driven Specification
  Language): actor flows, processes/algorithms, state machines, definitions
  of done, and acceptance criteria.
-->

## Metadata

`@cpt:blueprint`
```toml
version = 1
kit = "sdlc"
artifact = "FEATURE"
codebase = false
```
`@/cpt:blueprint`

## Skill Integration

`@cpt:skill`
```markdown
### FEATURE Commands
- `cypilot validate --artifact <FEATURE.md>` — validate FEATURE structure and IDs
- `cypilot list-ids --kind flow` — list all flows
- `cypilot list-ids --kind algo` — list all algorithms
- `cypilot list-ids --kind state` — list all state machines
- `cypilot list-ids --kind dod` — list all definitions of done
- `cypilot where-defined <id>` — find where a FEATURE ID is defined
- `cypilot where-used <id>` — find where a FEATURE ID is referenced in code
### FEATURE Workflows
- **Generate FEATURE**: create a new FEATURE from template with guided CDSL prompts
- **Analyze FEATURE**: validate structure (deterministic) then semantic quality (checklist-based)
```
`@/cpt:skill`

---

## Rules Definition

### Rules Skeleton

`@cpt:rules`
```toml
[prerequisites]
sections = ["load_dependencies"]

[requirements]
sections = ["structural", "versioning", "semantic", "traceability", "constraints", "scope", "upstream_traceability", "featstatus", "checkbox_management"]

[tasks]
phases = ["setup", "content_creation", "ids_and_structure", "quality_check"]

[validation]
sections = ["structural", "semantic", "traceability"]

[error_handling]
sections = ["missing_decomposition", "missing_design", "missing_parent", "escalation"]

[next_steps]
sections = ["options"]
```
`@/cpt:rules`

### Prerequisites

`@cpt:rule`
```toml
kind = "prerequisites"
section = "load_dependencies"
```
```markdown
- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/task-crud.md` for reference style
- [ ] Read DECOMPOSITION to get feature ID and context
- [ ] Read DESIGN to understand domain types and components
- [ ] Read adapter `artifacts.toml` to determine FEATURE artifact path
- [ ] Load `../../constraints.json` for kit-level constraints
- [ ] Load `{cypilot_path}/.core/requirements/identifiers.md` for ID formats
```
`@/cpt:rule`

### Requirements

#### Structural

`@cpt:rule`
```toml
kind = "requirements"
section = "structural"
```
```markdown
- [ ] FEATURE follows `template.md` structure
- [ ] References parent feature from DECOMPOSITION manifest
- [ ] All flows, algorithms, states, DoD items have unique IDs
- [ ] All IDs follow `cpt-{system}-{kind}-{slug}` pattern
- [ ] All IDs have priority markers (`p1`-`p9`) when required by constraints
- [ ] CDSL instructions follow format: `N. [ ] - \`pN\` - Description - \`inst-slug\``
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document
```
`@/cpt:rule`

#### Versioning

`@cpt:rule`
```toml
kind = "requirements"
section = "versioning"
```
```markdown
- [ ] When editing existing FEATURE: increment version in frontmatter
- [ ] When flow/algo/state/dod significantly changes: add `-v{N}` suffix to ID
- [ ] Keep changelog of significant changes
- [ ] Versioning code markers must match: `@cpt-{kind}:cpt-{system}-{kind}-{slug}-v2:p{N}`
```
`@/cpt:rule`

#### Semantic

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
**Reference**: `checklist.md` for detailed criteria

- [ ] Actor flows define complete user journeys
- [ ] Algorithms specify processing logic clearly
- [ ] State machines capture all valid transitions
- [ ] DoD items are testable and traceable
- [ ] CDSL instructions describe "what" not "how"
- [ ] Control flow keywords used correctly (IF, RETURN, FROM/TO/WHEN)
```
`@/cpt:rule`

#### Traceability

`@cpt:rule`
```toml
kind = "requirements"
section = "traceability"
```
```markdown
- [ ] All IDs with `to_code="true"` must be traced to code
- [ ] Code must contain markers: `@cpt-{kind}:{cpt-id}:p{N}`
- [ ] Each CDSL instruction maps to code marker
```
`@/cpt:rule`

#### Constraints

`@cpt:rule`
```toml
kind = "requirements"
section = "constraints"
```
```markdown
- [ ] ALWAYS open and follow `../../constraints.json` (kit root)
- [ ] Treat `constraints.json` as primary validator for:
  - where IDs are defined
  - where IDs are referenced
  - which cross-artifact references are required / optional / prohibited
```
`@/cpt:rule`

#### Scope

`@cpt:rule`
```toml
kind = "requirements"
section = "scope"
```
```markdown
**One FEATURE per feature from DECOMPOSITION manifest**.

| Scope | Examples | Guideline |
|-------|----------|-----------|
| **Too broad** | "User management feature" covering auth, profiles, roles | Split into separate FEATUREs |
| **Right size** | "User login flow" covering single capability | Clear boundary, implementable unit |
| **Too narrow** | "Validate email format" | Implementation detail, belongs in flow/algo |

**FEATURE-worthy content**: Actor flows, algorithms, state machines, DoD items, test scenarios.
**NOT FEATURE-worthy**: System architecture (DESIGN), technology decisions (ADR), business requirements (PRD).
```
`@/cpt:rule`

#### Upstream Traceability

`@cpt:rule`
```toml
kind = "requirements"
section = "upstream_traceability"
```
```markdown
- [ ] When all flows/algorithms/states/DoD items `[x]` → mark feature as `[x]` in DECOMPOSITION
- [ ] When feature complete → update status in DECOMPOSITION (→ IMPLEMENTED)
```
`@/cpt:rule`

#### Feature Status

`@cpt:rule`
```toml
kind = "requirements"
section = "featstatus"
```
```markdown
- [ ] FEATURE defines a `featstatus` ID definition directly under the H1 title
- [ ] Template: `cpt-{system}-featstatus-{feature-slug}`
- [ ] `featstatus` is `[x]` only when ALL nested task-tracked IDs and references are `[x]`
- [ ] `featstatus` is a documentation/status rollup marker (not a `to_code` identifier)
```
`@/cpt:rule`

#### Checkbox Management

`@cpt:rule`
```toml
kind = "requirements"
section = "checkbox_management"
```
```markdown
| ID kind | `to_code` | Check when... |
|---------|-----------|---------------|
| `flow` | `true` | ALL `@cpt-flow:` code markers exist |
| `algo` | `true` | ALL `@cpt-algo:` code markers exist |
| `state` | `true` | ALL `@cpt-state:` code markers exist |
| `dod` | `true` | Implementation complete AND tests pass |
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
- [ ] Load `examples/task-crud.md` for reference style
- [ ] Read DECOMPOSITION to get feature ID and context
- [ ] Read DESIGN to understand domain types and components
```
`@/cpt:rule`

#### Content Creation

`@cpt:rule`
```toml
kind = "tasks"
section = "content_creation"
```
```markdown
**CDSL instruction generation:**
- [ ] Each instruction has phase marker: `\`pN\``
- [ ] Each instruction has unique inst ID: `\`inst-{slug}\``
- [ ] Instructions describe what, not how
- [ ] Use **IF**, **RETURN**, **FROM/TO/WHEN** keywords for control flow
- [ ] Nested instructions for conditional branches
```
`@/cpt:rule`

#### IDs & Structure

`@cpt:rule`
```toml
kind = "tasks"
section = "ids_and_structure"
```
```markdown
- [ ] Generate flow IDs: `cpt-{system}-flow-{feature-slug}-{slug}`
- [ ] Generate algorithm IDs: `cpt-{system}-algo-{feature-slug}-{slug}`
- [ ] Generate state IDs: `cpt-{system}-state-{feature-slug}-{slug}`
- [ ] Generate DoD IDs: `cpt-{system}-dod-{feature-slug}-{slug}`
- [ ] Assign priorities (`p1`-`p9`) based on feature priority
- [ ] Verify ID uniqueness with `cypilot list-ids`
```
`@/cpt:rule`

#### Quality Check

`@cpt:rule`
```toml
kind = "tasks"
section = "quality_check"
```
```markdown
- [ ] Compare CDSL style to `examples/task-crud.md`
- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations
- [ ] Verify parent feature reference exists
```
`@/cpt:rule`

### Error Handling

#### Missing Decomposition

`@cpt:rule`
```toml
kind = "error_handling"
section = "missing_decomposition"
```
```markdown
- [ ] Option 1: Run `/cypilot-generate DECOMPOSITION` first (recommended)
- [ ] Option 2: Continue without manifest (FEATURE will lack traceability)
```
`@/cpt:rule`

#### Missing Design

`@cpt:rule`
```toml
kind = "error_handling"
section = "missing_design"
```
```markdown
- [ ] Option 1: Run `/cypilot-generate DESIGN` first (recommended for architectural context)
- [ ] Option 2: Continue without DESIGN (reduced domain model context)
```
`@/cpt:rule`

#### Missing Parent

`@cpt:rule`
```toml
kind = "error_handling"
section = "missing_parent"
```
```markdown
- [ ] Verify feature ID: `cpt-{system}-feature-{slug}`
- [ ] If new feature: add to DECOMPOSITION first
- [ ] If typo: correct the ID reference
```
`@/cpt:rule`

#### Escalation

`@cpt:rule`
```toml
kind = "error_handling"
section = "escalation"
```
```markdown
- [ ] Ask user when flow complexity requires domain expertise
- [ ] Ask user when algorithm correctness uncertain
- [ ] Ask user when state transitions ambiguous
```
`@/cpt:rule`

### Validation

#### Structural

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
  - CDSL instruction format
  - No placeholders
  - Parent feature reference validity
```
`@/cpt:rule`

#### Semantic

`@cpt:rule`
```toml
kind = "validation"
section = "semantic"
```
```markdown
Apply `checklist.md` systematically:
1. For each MUST HAVE item: check if requirement is met
2. For each MUST NOT HAVE item: scan document for violations
3. Use example for quality baseline
```
`@/cpt:rule`

#### Traceability

`@cpt:rule`
```toml
kind = "validation"
section = "traceability"
```
```markdown
For IDs with `to_code="true"`:
- [ ] Verify code markers exist: `@cpt-{kind}:{cpt-id}:p{N}`
- [ ] Report missing markers
- [ ] Report orphaned markers
```
`@/cpt:rule`

### Next Steps

`@cpt:rule`
```toml
kind = "next_steps"
section = "options"
```
```markdown
- [ ] FEATURE design complete → `/cypilot-generate CODE` — implement feature
- [ ] Code implementation done → `/cypilot-analyze CODE` — validate implementation
- [ ] Feature IMPLEMENTED → update status in DECOMPOSITION
- [ ] Another feature to design → `/cypilot-generate FEATURE` — design next feature
- [ ] Want checklist review only → `/cypilot-analyze semantic` — semantic validation
```
`@/cpt:rule`

---

## Checklist Definition

Feature quality checks organized by domain.

### Checklist Skeleton

`@cpt:checklist`
```toml
[severity]
levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

[review]
priority = ["ARCH", "SEC", "BIZ", "SEM"]

[[domain]]
abbr = "ARCH"
name = "Architecture"
standards = ["IEEE 1016-2009"]

[[domain]]
abbr = "SEM"
name = "Semantic Alignment"
standards = ["ISO/IEC/IEEE 29148:2018"]

[[domain]]
abbr = "PERF"
name = "Performance"
standards = ["ISO/IEC 25010:2011"]

[[domain]]
abbr = "SEC"
name = "Security"
standards = ["ISO/IEC 25010:2011", "OWASP ASVS 5.0"]

[[domain]]
abbr = "REL"
name = "Reliability"
standards = ["ISO/IEC 25010:2011"]

[[domain]]
abbr = "DATA"
name = "Data"
standards = []

[[domain]]
abbr = "INT"
name = "Integration"
standards = []

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
standards = []

[[domain]]
abbr = "UX"
name = "Usability"
standards = ["ISO/IEC 25010:2011", "WCAG 2.2"]

[[domain]]
abbr = "BIZ"
name = "Business"
standards = ["ISO/IEC/IEEE 29148:2018"]

[[domain]]
abbr = "DOC"
name = "Deliberate Omissions"
standards = []
```
`@/cpt:checklist`

### Architecture Checks (ARCH)

`@cpt:check`
```toml
id = "ARCH-FDESIGN-001"
domain = "ARCH"
title = "Feature Context Completeness"
severity = "CRITICAL"
ref = "IEEE 1016-2009 §5.4.1"
kind = "must_have"
```
```markdown
- [ ] Feature identifier is present and stable
- [ ] Feature status documented
- [ ] Overall Design reference present
- [ ] Requirements source reference present
- [ ] Actors/user roles defined and referenced consistently
- [ ] Feature scope clearly stated
- [ ] Feature boundaries explicit
- [ ] Out-of-scope items documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-FDESIGN-002"
domain = "ARCH"
title = "Overall Design Alignment"
severity = "CRITICAL"
kind = "must_have"
```
```markdown
- [ ] Shared types/schemas referenced from canonical source
- [ ] Shared APIs/contracts referenced from canonical source
- [ ] Architectural decisions consistent with design baseline
- [ ] Domain concepts referenced consistently with canonical domain model
- [ ] Principles compliance documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-FDESIGN-003"
domain = "ARCH"
title = "Actor Flow Completeness"
severity = "CRITICAL"
kind = "must_have"
```
```markdown
- [ ] Flows/user-journeys section exists and is sufficiently detailed
- [ ] All user-facing functionality has actor flows
- [ ] Each flow has a unique name/identifier
- [ ] Flows cover happy path
- [ ] Flows cover error paths
- [ ] Flows cover edge cases
- [ ] Actor/user roles defined consistently with requirements
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-FDESIGN-004"
domain = "ARCH"
title = "Algorithm Completeness"
severity = "CRITICAL"
kind = "must_have"
```
```markdown
- [ ] Algorithms/business-rules section exists and is sufficiently detailed
- [ ] All business logic has algorithms
- [ ] Each algorithm has a unique name/identifier
- [ ] Algorithms are deterministic and testable
- [ ] Input/output clearly defined
- [ ] Error handling documented
- [ ] Edge cases addressed
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-FDESIGN-005"
domain = "ARCH"
title = "State Management"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] States/state-machine section exists when stateful behavior is present
- [ ] Stateful components have state definitions
- [ ] State transitions define explicit triggers/conditions
- [ ] Valid states enumerated
- [ ] Transition guards documented
- [ ] Invalid state transitions documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-FDESIGN-006"
domain = "ARCH"
title = "Component Interaction"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Inter-component interactions documented
- [ ] Service calls documented
- [ ] Event emissions documented
- [ ] Data flow between components clear
- [ ] Async operations documented
- [ ] Timeout handling documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-FDESIGN-007"
domain = "ARCH"
title = "Extension Points"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Customization points identified
- [ ] Plugin/hook opportunities documented
- [ ] Configuration options documented
- [ ] Feature flags integration documented
```
`@/cpt:check`

### Semantic Alignment Checks (SEM)

`@cpt:check`
```toml
id = "SEM-FDESIGN-001"
domain = "SEM"
title = "PRD Coverage Integrity"
severity = "CRITICAL"
ref = "ISO/IEC/IEEE 29148:2018 §6.5"
kind = "must_have"
```
```markdown
- [ ] All referenced PRD FR/NFR IDs are valid and correctly cited
- [ ] Feature requirements do not contradict PRD scope, priorities, or constraints
- [ ] Feature outcomes preserve PRD intent and success criteria
- [ ] Any PRD trade-offs are explicitly documented and approved
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEM-FDESIGN-002"
domain = "SEM"
title = "Design Principles and Constraints"
severity = "CRITICAL"
kind = "must_have"
```
```markdown
- [ ] Feature design adheres to design principles referenced in the Overall Design
- [ ] Feature design respects all design constraints
- [ ] Any constraint exception is explicitly documented with rationale
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEM-FDESIGN-003"
domain = "SEM"
title = "Architecture and Component Consistency"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Feature responsibilities align with component boundaries in the Overall Design
- [ ] Interactions and sequences match the system interaction design
- [ ] Data models and entities conform to the Overall Design domain model
- [ ] API contracts and integration boundaries match the Overall Design
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEM-FDESIGN-004"
domain = "SEM"
title = "Feature Semantics Completeness"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Actor flows, algorithms, and state machines are consistent with design context
- [ ] DoD mappings cover required design references
- [ ] Any semantic deviation from design is documented and approved
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEM-FDESIGN-005"
domain = "SEM"
title = "Design Decomposition Consistency"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Feature ID matches the entry in the DECOMPOSITION
- [ ] Purpose, scope, and out-of-scope items align with DECOMPOSITION entry
- [ ] Dependencies match the DECOMPOSITION dependency list
- [ ] Requirements covered (FR/NFR) match the DECOMPOSITION mapping
- [ ] Design elements covered match the DECOMPOSITION entry
```
`@/cpt:check`

### Performance Checks (PERF)

`@cpt:check`
```toml
id = "PERF-FDESIGN-001"
domain = "PERF"
title = "Performance-Critical Paths"
severity = "HIGH"
ref = "ISO/IEC 25010:2011 §4.2.2"
kind = "must_have"
applicable_when = "Performance-sensitive features"
```
```markdown
- [ ] Hot paths identified
- [ ] Latency-sensitive operations marked
- [ ] Caching strategy documented
- [ ] N+1 query prevention addressed
- [ ] Database query optimization documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "PERF-FDESIGN-002"
domain = "PERF"
title = "Resource Management"
severity = "HIGH"
kind = "must_have"
applicable_when = "Resource-intensive features"
```
```markdown
- [ ] Memory allocation patterns documented
- [ ] Connection pooling documented
- [ ] Resource cleanup documented
- [ ] Large data handling documented
- [ ] Pagination documented (if applicable)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "PERF-FDESIGN-003"
domain = "PERF"
title = "Scalability Considerations"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Concurrent access handling documented
- [ ] Lock contention minimized
- [ ] Horizontal scaling support documented
- [ ] Rate limiting handled
```
`@/cpt:check`

`@cpt:check`
```toml
id = "PERF-FDESIGN-004"
domain = "PERF"
title = "Performance Acceptance Criteria"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Response time targets stated
- [ ] Throughput targets stated
- [ ] Resource usage limits stated
- [ ] Performance test requirements documented
```
`@/cpt:check`

### Security Checks (SEC)

`@cpt:check`
```toml
id = "SEC-FDESIGN-001"
domain = "SEC"
title = "Authentication Integration"
severity = "CRITICAL"
ref = "OWASP ASVS V2; ISO 25010 §4.2.6"
kind = "must_have"
applicable_when = "User-facing or API features"
```
```markdown
- [ ] Authentication requirements documented
- [ ] Session handling documented
- [ ] Token validation documented
- [ ] Authentication failure handling documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-FDESIGN-002"
domain = "SEC"
title = "Authorization Implementation"
severity = "CRITICAL"
kind = "must_have"
applicable_when = "Features with access control"
```
```markdown
- [ ] Permission checks documented in flows
- [ ] Role-based access documented
- [ ] Resource-level authorization documented
- [ ] Authorization failure handling documented
- [ ] Privilege escalation prevention documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-FDESIGN-003"
domain = "SEC"
title = "Input Validation"
severity = "CRITICAL"
ref = "OWASP ASVS V5"
kind = "must_have"
applicable_when = "Features accepting user input"
```
```markdown
- [ ] All inputs validated
- [ ] Validation rules documented
- [ ] Validation failure handling documented
- [ ] Injection prevention documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-FDESIGN-004"
domain = "SEC"
title = "Data Protection"
severity = "CRITICAL"
kind = "must_have"
applicable_when = "Features handling sensitive data"
```
```markdown
- [ ] Sensitive data handling documented
- [ ] PII handling documented
- [ ] Encryption requirements documented
- [ ] Secure data transmission documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-FDESIGN-005"
domain = "SEC"
title = "Audit Trail"
severity = "HIGH"
kind = "must_have"
applicable_when = "Auditable operations"
```
```markdown
- [ ] Auditable actions identified
- [ ] Audit logging documented
- [ ] User attribution documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-FDESIGN-006"
domain = "SEC"
title = "Security Error Handling"
severity = "HIGH"
kind = "must_have"
applicable_when = "Security-sensitive features"
```
```markdown
- [ ] Security errors don't leak information
- [ ] Error messages are safe
- [ ] Rate limiting on security operations documented
```
`@/cpt:check`

### Reliability Checks (REL)

`@cpt:check`
```toml
id = "REL-FDESIGN-001"
domain = "REL"
title = "Error Handling Completeness"
severity = "CRITICAL"
ref = "ISO/IEC 25010:2011 §4.2.5"
kind = "must_have"
```
```markdown
- [ ] All error conditions identified
- [ ] Error classification documented
- [ ] Recovery actions documented
- [ ] Error propagation documented
- [ ] User-facing error messages documented
- [ ] Logging requirements documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "REL-FDESIGN-002"
domain = "REL"
title = "Fault Tolerance"
severity = "HIGH"
kind = "must_have"
applicable_when = "Features with external dependencies"
```
```markdown
- [ ] External dependency failures handled
- [ ] Timeout handling documented
- [ ] Retry logic documented
- [ ] Fallback behavior documented
- [ ] Graceful degradation documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "REL-FDESIGN-003"
domain = "REL"
title = "Data Integrity"
severity = "CRITICAL"
ref = "ISO/IEC 25010:2011 §4.2.6.2"
kind = "must_have"
applicable_when = "Features with data mutations"
```
```markdown
- [ ] Transaction boundaries documented
- [ ] Consistency guarantees documented
- [ ] Concurrent modification handling documented
- [ ] Idempotency documented (where applicable)
- [ ] Rollback scenarios documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "REL-FDESIGN-004"
domain = "REL"
title = "Resilience Patterns"
severity = "MEDIUM"
kind = "must_have"
applicable_when = "Distributed or high-availability features"
```
```markdown
- [ ] Bulkhead patterns documented (if applicable)
- [ ] Backpressure handling documented
- [ ] Resource exhaustion handling documented
```
`@/cpt:check`

### Data Checks (DATA)

`@cpt:check`
```toml
id = "DATA-FDESIGN-001"
domain = "DATA"
title = "Data Access Patterns"
severity = "HIGH"
kind = "must_have"
applicable_when = "Features with data operations"
```
```markdown
- [ ] Read patterns documented
- [ ] Write patterns documented
- [ ] Query patterns documented
- [ ] Index usage documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DATA-FDESIGN-002"
domain = "DATA"
title = "Data Validation"
severity = "CRITICAL"
kind = "must_have"
applicable_when = "Features accepting data input"
```
```markdown
- [ ] Business rule validation documented
- [ ] Format validation documented
- [ ] Referential integrity validation documented
- [ ] Validation error messages documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DATA-FDESIGN-003"
domain = "DATA"
title = "Data Transformation"
severity = "HIGH"
kind = "must_have"
applicable_when = "Features with data transformations"
```
```markdown
- [ ] Input transformation documented
- [ ] Output transformation documented
- [ ] Null handling documented
- [ ] Default value handling documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DATA-FDESIGN-004"
domain = "DATA"
title = "Data Lifecycle"
severity = "MEDIUM"
kind = "must_have"
applicable_when = "Features with data persistence"
```
```markdown
- [ ] Data creation documented
- [ ] Data update documented
- [ ] Data deletion documented
- [ ] Data retention compliance documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DATA-FDESIGN-005"
domain = "DATA"
title = "Data Privacy"
severity = "HIGH"
kind = "must_have"
applicable_when = "Features handling PII"
```
```markdown
- [ ] PII handling documented
- [ ] Data minimization applied
- [ ] Consent handling documented
- [ ] Anonymization/pseudonymization documented
```
`@/cpt:check`

### Integration Checks (INT)

`@cpt:check`
```toml
id = "INT-FDESIGN-001"
domain = "INT"
title = "API Interactions"
severity = "HIGH"
kind = "must_have"
applicable_when = "Features with API calls"
```
```markdown
- [ ] API calls documented with method + path
- [ ] Request construction documented
- [ ] Response handling documented
- [ ] Error response handling documented
- [ ] Retry behavior documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "INT-FDESIGN-002"
domain = "INT"
title = "Database Operations"
severity = "HIGH"
kind = "must_have"
applicable_when = "Features with DB operations"
```
```markdown
- [ ] DB operations documented with operation + table
- [ ] Query patterns documented
- [ ] Transaction usage documented
- [ ] Query parameterization documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "INT-FDESIGN-003"
domain = "INT"
title = "External Integrations"
severity = "HIGH"
kind = "must_have"
applicable_when = "Features with external system calls"
```
```markdown
- [ ] External system calls documented
- [ ] Integration authentication documented
- [ ] Timeout configuration documented
- [ ] Failure handling documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "INT-FDESIGN-004"
domain = "INT"
title = "Event/Message Handling"
severity = "MEDIUM"
kind = "must_have"
applicable_when = "Features with event/message patterns"
```
```markdown
- [ ] Event publishing documented
- [ ] Event consumption documented
- [ ] Message format documented
- [ ] Delivery guarantees documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "INT-FDESIGN-005"
domain = "INT"
title = "Cache Integration"
severity = "MEDIUM"
kind = "must_have"
applicable_when = "Features using caching"
```
```markdown
- [ ] Cache read/write patterns documented
- [ ] Cache invalidation documented
- [ ] Cache TTL documented
```
`@/cpt:check`

### Operations Checks (OPS)

`@cpt:check`
```toml
id = "OPS-FDESIGN-001"
domain = "OPS"
title = "Observability"
severity = "HIGH"
kind = "must_have"
applicable_when = "Deployed features"
```
```markdown
- [ ] Logging points documented
- [ ] Log levels documented
- [ ] Metrics collection documented
- [ ] Correlation ID handling documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "OPS-FDESIGN-002"
domain = "OPS"
title = "Configuration"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Configuration parameters documented
- [ ] Default values documented
- [ ] Feature flags documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "OPS-FDESIGN-003"
domain = "OPS"
title = "Health & Diagnostics"
severity = "MEDIUM"
kind = "must_have"
applicable_when = "Service features"
```
```markdown
- [ ] Health check contributions documented
- [ ] Troubleshooting guidance documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "OPS-FDESIGN-004"
domain = "OPS"
title = "Rollout & Rollback"
severity = "HIGH"
kind = "must_have"
applicable_when = "Features requiring phased rollout"
```
```markdown
- [ ] Rollout strategy documented when applicable
- [ ] Rollback strategy documented
- [ ] Data migration/backward compatibility addressed when applicable
```
`@/cpt:check`

### Maintainability Checks (MAINT)

`@cpt:check`
```toml
id = "MAINT-FDESIGN-001"
domain = "MAINT"
title = "Code Organization"
severity = "MEDIUM"
ref = "ISO/IEC 25010:2011 §4.2.7"
kind = "must_have"
```
```markdown
- [ ] Module structure implied
- [ ] Separation of concerns evident
- [ ] Single responsibility evident
- [ ] Interface boundaries clear
```
`@/cpt:check`

`@cpt:check`
```toml
id = "MAINT-FDESIGN-002"
domain = "MAINT"
title = "Documentation Quality"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Flows self-documenting
- [ ] Complex logic explained
- [ ] Business rules documented
- [ ] Edge cases documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "MAINT-FDESIGN-003"
domain = "MAINT"
title = "Technical Debt Awareness"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Known limitations documented
- [ ] Workarounds documented
- [ ] Future improvement opportunities noted
```
`@/cpt:check`

### Testing Checks (TEST)

`@cpt:check`
```toml
id = "TEST-FDESIGN-001"
domain = "TEST"
title = "Testability"
severity = "HIGH"
ref = "ISO/IEC 25010:2011 §4.2.7.5; ISO/IEC/IEEE 29119-3:2021"
kind = "must_have"
```
```markdown
- [ ] Flows are testable (deterministic, observable)
- [ ] Algorithms are testable (clear inputs/outputs)
- [ ] States are testable (verifiable transitions)
- [ ] Mock boundaries clear
- [ ] Test data requirements documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "TEST-FDESIGN-002"
domain = "TEST"
title = "Test Coverage Guidance"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Unit test targets identified
- [ ] Integration test targets identified
- [ ] E2E test scenarios documented
- [ ] Edge case tests identified
- [ ] Error path tests identified
```
`@/cpt:check`

`@cpt:check`
```toml
id = "TEST-FDESIGN-003"
domain = "TEST"
title = "Acceptance Criteria"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Each requirement has verifiable criteria
- [ ] Criteria are unambiguous and measurable
- [ ] Criteria cover happy path and error paths
- [ ] Criteria testable automatically
```
`@/cpt:check`

### Compliance Checks (COMPL)

`@cpt:check`
```toml
id = "COMPL-FDESIGN-001"
domain = "COMPL"
title = "Regulatory Compliance"
severity = "HIGH"
kind = "must_have"
applicable_when = "Regulated features"
```
```markdown
- [ ] Compliance requirements addressed
- [ ] Audit trail requirements met
- [ ] Data handling compliant
- [ ] Consent handling compliant
```
`@/cpt:check`

`@cpt:check`
```toml
id = "COMPL-FDESIGN-002"
domain = "COMPL"
title = "Privacy Compliance"
severity = "HIGH"
kind = "must_have"
applicable_when = "Features handling personal data"
```
```markdown
- [ ] Privacy by design evident
- [ ] Data minimization applied
- [ ] Data subject rights supported
```
`@/cpt:check`

### Usability Checks (UX)

`@cpt:check`
```toml
id = "UX-FDESIGN-001"
domain = "UX"
title = "User Experience Flows"
severity = "MEDIUM"
ref = "ISO/IEC 25010:2011 §4.2.4"
kind = "must_have"
applicable_when = "User-facing features"
```
```markdown
- [ ] User journey clear
- [ ] Feedback points documented
- [ ] Error messages user-friendly
- [ ] Loading states documented
- [ ] Confirmation flows documented
```
`@/cpt:check`

`@cpt:check`
```toml
id = "UX-FDESIGN-002"
domain = "UX"
title = "Accessibility"
severity = "MEDIUM"
ref = "WCAG 2.2 Level AA"
kind = "must_have"
applicable_when = "Web/UI features"
```
```markdown
- [ ] Accessibility requirements addressed
- [ ] Keyboard navigation supported
- [ ] Screen reader support documented
```
`@/cpt:check`

### Business Checks (BIZ)

`@cpt:check`
```toml
id = "BIZ-FDESIGN-001"
domain = "BIZ"
title = "Requirements Alignment"
severity = "CRITICAL"
ref = "ISO/IEC/IEEE 29148:2018 §5.2"
kind = "must_have"
```
```markdown
- [ ] All feature requirements (DoD) documented
- [ ] Requirements trace to PRD
- [ ] Business rules accurately captured
- [ ] Edge cases reflect business reality
- [ ] Acceptance criteria business-verifiable
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-FDESIGN-002"
domain = "BIZ"
title = "Value Delivery"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Feature delivers stated value
- [ ] User needs addressed
- [ ] Business process supported
- [ ] Success metrics achievable
```
`@/cpt:check`

### Documentation Checks (DOC)

`@cpt:check`
```toml
id = "DOC-FDESIGN-001"
domain = "DOC"
title = "Explicit Non-Applicability"
severity = "CRITICAL"
kind = "must_have"
```
```markdown
- [ ] If a section or requirement is intentionally omitted, it is explicitly stated
- [ ] No silent omissions
- [ ] Reviewer can distinguish "considered and excluded" from "forgot"
```
`@/cpt:check`

### Anti-Pattern Checks (must_not_have)

Content that does NOT belong in a FEATURE document.

`@cpt:check`
```toml
id = "ARCH-FDESIGN-NO-001"
domain = "ARCH"
title = "No System-Level Type Redefinitions"
severity = "CRITICAL"
kind = "must_not_have"
belongs_to = "Central domain model / schema documentation"
```
```markdown
- [ ] No new system-wide entity/type definitions
- [ ] No new value object definitions
- [ ] No domain model changes
- [ ] No schema definitions
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-FDESIGN-NO-002"
domain = "ARCH"
title = "No New API Endpoints"
severity = "CRITICAL"
kind = "must_not_have"
belongs_to = "API contract documentation"
```
```markdown
- [ ] No new endpoint definitions
- [ ] No new API contracts
- [ ] No request/response schema definitions
- [ ] Reference existing endpoints by ID only
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ARCH-FDESIGN-NO-003"
domain = "ARCH"
title = "No Architectural Decisions"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "ADR"
```
```markdown
- [ ] No "we chose X over Y" discussions
- [ ] No pattern selection justifications
- [ ] No technology choice explanations
- [ ] No pros/cons analysis
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-FDESIGN-NO-001"
domain = "BIZ"
title = "No Product Requirements"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "PRD"
```
```markdown
- [ ] No actor definitions (reference PRD)
- [ ] No functional requirement definitions (reference PRD)
- [ ] No use case definitions (reference PRD)
- [ ] No NFR definitions (reference PRD)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "BIZ-FDESIGN-NO-002"
domain = "BIZ"
title = "No Sprint/Task Breakdowns"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "Project management tools"
```
```markdown
- [ ] No sprint assignments
- [ ] No effort estimates
- [ ] No developer assignments
- [ ] No timeline estimates
```
`@/cpt:check`

`@cpt:check`
```toml
id = "MAINT-FDESIGN-NO-001"
domain = "MAINT"
title = "No Code Snippets"
severity = "HIGH"
kind = "must_not_have"
belongs_to = "Source code repository"
```
```markdown
- [ ] No production code
- [ ] No code diffs
- [ ] No implementation code
- [ ] No SQL queries (describe operations instead)
- [ ] No API request/response JSON
```
`@/cpt:check`

`@cpt:check`
```toml
id = "TEST-FDESIGN-NO-001"
domain = "TEST"
title = "No Test Implementation"
severity = "MEDIUM"
kind = "must_not_have"
belongs_to = "Test directories in source code"
```
```markdown
- [ ] No test code
- [ ] No test scripts
- [ ] No test data files
- [ ] No mock implementations
```
`@/cpt:check`

`@cpt:check`
```toml
id = "SEC-FDESIGN-NO-001"
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
- [ ] No encryption keys
- [ ] No connection strings with credentials
```
`@/cpt:check`

`@cpt:check`
```toml
id = "OPS-FDESIGN-NO-001"
domain = "OPS"
title = "No Infrastructure Code"
severity = "MEDIUM"
kind = "must_not_have"
belongs_to = "Infrastructure code repository"
```
```markdown
- [ ] No Terraform/CloudFormation
- [ ] No Kubernetes manifests
- [ ] No Docker configurations
- [ ] No CI/CD pipeline definitions
```
`@/cpt:check`

---

## Template Structure

Headings, prompts, IDs, and examples that define the generated `template.md`
and `example.md` files. The FEATURE template covers: context (overview,
purpose, actors, references), actor flows with CDSL instructions, processes/
algorithms, state machines, definitions of done, and acceptance criteria.

### Title (H1)

`@cpt:heading`
```toml
id = "feature-h1-title"
level = 1
required = true
numbered = false
multiple = false
template = "Feature: {Feature Name}"
prompt = "Name of the feature from DECOMPOSITION"
description = "FEATURE document title (H1)."
examples = ["# Feature: Task CRUD"]
```
`@/cpt:heading`

`@cpt:id`
```toml
kind = "featstatus"
name = "Feature Status"
description = "A feature-level status/anchor marker used in FEATURE context."
required = true
task = true
priority = false
template = "cpt-{system}-featstatus-{feature-slug}"
examples = ["cpt-cypilot-featstatus-template-system", "cpt-ex-ovwa-featstatus-tracker-core"]
to_code = false
headings = ["feature-h1-title"]
```
`@/cpt:id`

`@cpt:prompt`
```markdown
- [ ] `p1` - **ID**: `cpt-{system}-featstatus-{feature-slug}`
```
`@/cpt:prompt`

`@cpt:example`
```markdown
# Feature: Task CRUD

- [ ] `p1` - **ID**: `cpt-ex-task-flow-featstatus-task-crud`

- [ ] `p2` - `cpt-ex-task-flow-feature-task-crud`
```
`@/cpt:example`

### Feature Context

`@cpt:heading`
```toml
id = "feature-context"
level = 2
required = true
numbered = true
multiple = false
pattern = "Feature Context"
description = "Feature context section."
examples = ["## 1. Feature Context"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
- [ ] `p2` - `cpt-{system}-feature-{slug}`
```
`@/cpt:prompt`

`@cpt:heading`
```toml
id = "feature-context-overview"
level = 3
required = true
numbered = true
multiple = false
pattern = "Overview"
description = "Feature overview."
examples = ["### 1.1 Overview"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
{Brief overview of what this feature does — 1-2 sentences.}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
Core task management functionality for creating, viewing, updating, and deleting tasks. This feature provides the foundation for team collaboration by enabling users to track work items through their lifecycle.

Problem: Teams need a central place to track tasks with status, priority, and assignments.
Primary value: Enables organized task tracking with clear ownership.
Key assumptions: Users have accounts and belong to at least one team.
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "feature-context-purpose"
level = 3
required = true
numbered = true
multiple = false
pattern = "Purpose"
description = "Feature purpose."
examples = ["### 1.2 Purpose"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
{Why this feature exists, what PRD requirements or DESIGN element it addresses.}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
Enable team members to manage their work items with full lifecycle tracking from creation through completion.

Success criteria: Users can create, view, update, and delete tasks within 500ms response time.
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "feature-context-actors"
level = 3
required = true
numbered = true
multiple = false
pattern = "Actors"
description = "Actors involved in the feature."
examples = ["### 1.3 Actors"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
| Actor | Role in Feature |
|-------|-----------------|
| `cpt-{system}-actor-{slug}` | {What this actor does in this feature} |
```
`@/cpt:prompt`

`@cpt:example`
```markdown
- `cpt-ex-task-flow-actor-member`
- `cpt-ex-task-flow-actor-lead`
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "feature-context-references"
level = 3
required = true
numbered = true
multiple = false
pattern = "References"
description = "References to related artifacts."
examples = ["### 1.4 References"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
- **PRD**: [PRD.md](../PRD.md)
- **Design**: [DESIGN.md](../DESIGN.md)
- **Dependencies**: {List feature dependencies or "None"}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
- Overall Design: [DESIGN.md](../../DESIGN.md)
- ADRs: `cpt-ex-task-flow-adr-postgres-storage`
- Related feature: [Notifications](../notifications.md)
```
`@/cpt:example`

### Actor Flows (CDSL)

`@cpt:heading`
```toml
id = "feature-actor-flows"
level = 2
required = true
numbered = true
multiple = false
pattern = "Actor Flows (CDSL)"
description = "Actor flows section."
examples = ["## 2. Actor Flows (CDSL)"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
User-facing interactions that start with an actor (human or external system) and describe the end-to-end flow of a use case. Each flow has a triggering actor and shows how the system responds to actor actions.
```
`@/cpt:prompt`

`@cpt:heading`
```toml
id = "feature-actor-flow"
level = 3
required = true
numbered = false
multiple = true
template = "{Flow Name}"
description = "A single actor flow."
examples = ["### Create Task"]
```
`@/cpt:heading`

`@cpt:id`
```toml
kind = "flow"
name = "Flow"
description = "An actor-facing CDSL flow describing a user/system interaction end-to-end."
required = false
task = false
priority = false
template = "cpt-{system}-flow-{feature-slug}-{slug}"
examples = ["cpt-cypilot-flow-template-system-load", "cpt-ex-ovwa-flow-run-tracker"]
to_code = true
headings = ["feature-actor-flow"]
```
`@/cpt:id`

`@cpt:prompt`
```markdown
- [ ] `p1` - **ID**: `cpt-{system}-flow-{feature-slug}-{slug}`

**Actor**: `cpt-{system}-actor-{slug}`

**Success Scenarios**:
- {Scenario 1}

**Error Scenarios**:
- {Error scenario 1}

**Steps**:
1. [ ] - `p1` - {Actor action} - `inst-{step-id}`
2. [ ] - `p1` - {API: METHOD /path (request/response summary)} - `inst-{step-id}`
3. [ ] - `p1` - {DB: OPERATION table(s) (key columns/filters)} - `inst-{step-id}`
4. [ ] - `p1` - **IF** {condition} - `inst-{step-id}`
   1. [ ] - `p1` - {Action if true} - `inst-{step-id}`
5. [ ] - `p1` - **ELSE** - `inst-{step-id}`
   1. [ ] - `p1` - {Action if false} - `inst-{step-id}`
6. [ ] - `p1` - **RETURN** {result} - `inst-{step-id}`
```
`@/cpt:prompt`

`@cpt:example`
```markdown
### Create Task

- [ ] `p1` - **ID**: `cpt-ex-task-flow-flow-create-task`

**Actors**:
- `cpt-ex-task-flow-actor-member`
- `cpt-ex-task-flow-actor-lead`

1. [x] - `p1` - User fills task form (title, description, priority) - `inst-fill-form`
2. [x] - `p1` - API: POST /api/tasks (body: title, description, priority, due_date) - `inst-api-create`
3. [x] - `p1` - Algorithm: validate task input using `cpt-ex-task-flow-algo-validate-task` - `inst-run-validate`
4. [x] - `p1` - DB: INSERT tasks(title, description, priority, due_date, status=BACKLOG) - `inst-db-insert`
5. [ ] - `p2` - User optionally assigns task to team member - `inst-assign`
6. [ ] - `p2` - API: POST /api/tasks/{task_id}/assignees (body: assignee_id) - `inst-api-assign`
7. [ ] - `p2` - DB: INSERT task_assignees(task_id, assignee_id) - `inst-db-assign-insert`
8. [x] - `p1` - API: RETURN 201 Created (task_id, status=BACKLOG) - `inst-return-created`
```
`@/cpt:example`

### Processes / Business Logic

`@cpt:heading`
```toml
id = "feature-processes"
level = 2
required = true
numbered = true
multiple = false
pattern = "Processes / Business Logic (CDSL)"
description = "Processes / business logic section."
examples = ["## 3. Processes / Business Logic (CDSL)"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
Internal system functions and procedures that do not interact with actors directly. Examples: database layer operations, authorization logic, middleware, validation routines, library functions, background jobs. These are reusable building blocks called by Actor Flows or other processes.
```
`@/cpt:prompt`

`@cpt:heading`
```toml
id = "feature-process"
level = 3
required = true
numbered = false
multiple = true
template = "{Process Name}"
description = "A single process/algorithm."
examples = ["### Validate Task"]
```
`@/cpt:heading`

`@cpt:id`
```toml
kind = "algo"
name = "Algorithm"
description = "A reusable internal process described in CDSL (business logic not directly initiated by an actor)."
required = false
task = false
priority = false
template = "cpt-{system}-algo-{feature-slug}-{slug}"
examples = ["cpt-cypilot-algo-template-system-extract-ids", "cpt-ex-ovwa-algo-track-active-time"]
to_code = true
headings = ["feature-processes"]
```
`@/cpt:id`

`@cpt:prompt`
```markdown
- [ ] `p2` - **ID**: `cpt-{system}-algo-{feature-slug}-{slug}`

**Input**: {Input description}

**Output**: {Output description}

**Steps**:
1. [ ] - `p1` - {Parse/normalize input} - `inst-{step-id}`
2. [ ] - `p1` - {DB: OPERATION table(s) (key columns/filters)} - `inst-{step-id}`
3. [ ] - `p1` - {API: METHOD /path (request/response summary)} - `inst-{step-id}`
4. [ ] - `p1` - **FOR EACH** {item} in {collection} - `inst-{step-id}`
   1. [ ] - `p1` - {Process item} - `inst-{step-id}`
5. [ ] - `p1` - **TRY** - `inst-{step-id}`
   1. [ ] - `p1` - {Risky operation} - `inst-{step-id}`
6. [ ] - `p1` - **CATCH** {error} - `inst-{step-id}`
   1. [ ] - `p1` - {Handle error} - `inst-{step-id}`
7. [ ] - `p1` - **RETURN** {result} - `inst-{step-id}`
```
`@/cpt:prompt`

`@cpt:example`
```markdown
### Validate Task

- [ ] `p1` - **ID**: `cpt-ex-task-flow-algo-validate-task`

1. [x] - `p1` - **IF** title is empty **RETURN** error "Title required" - `inst-check-title`
2. [x] - `p1` - **IF** priority not in [LOW, MEDIUM, HIGH] **RETURN** error - `inst-check-priority`
3. [x] - `p1` - **IF** due_date is present AND due_date is in the past **RETURN** error - `inst-check-due-date`
4. [x] - `p1` - DB: SELECT tasks WHERE title=? AND status!=DONE (dedupe check) - `inst-db-dedupe-check`
5. [ ] - `p2` - **IF** duplicate exists **RETURN** error - `inst-return-duplicate`
6. [x] - `p1` - **RETURN** valid - `inst-return-valid`
```
`@/cpt:example`

### States

`@cpt:heading`
```toml
id = "feature-states"
level = 2
required = true
numbered = true
multiple = false
pattern = "States (CDSL)"
description = "States section."
examples = ["## 4. States (CDSL)"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
Optional: Include when entities have explicit lifecycle states.
```
`@/cpt:prompt`

`@cpt:heading`
```toml
id = "feature-state"
level = 3
required = true
numbered = false
multiple = true
template = "{Entity Name} State Machine"
description = "A single state machine."
examples = ["### Task Status"]
```
`@/cpt:heading`

`@cpt:id`
```toml
kind = "state"
name = "State Machine"
description = "A lifecycle/state machine definition for an entity or subsystem, described in CDSL transitions."
required = false
task = false
priority = false
template = "cpt-{system}-state-{feature-slug}-{slug}"
examples = ["cpt-cypilot-state-template-system-lifecycle", "cpt-ex-ovwa-state-daemon-lifecycle"]
to_code = true
headings = ["feature-state"]
```
`@/cpt:id`

`@cpt:prompt`
```markdown
- [ ] `p2` - **ID**: `cpt-{system}-state-{feature-slug}-{slug}`

**States**: {State1}, {State2}, {State3}

**Initial State**: {State1}

**Transitions**:
1. [ ] - `p1` - **FROM** {State1} **TO** {State2} **WHEN** {condition} - `inst-{step-id}`
2. [ ] - `p1` - **FROM** {State2} **TO** {State3} **WHEN** {condition} - `inst-{step-id}`
```
`@/cpt:prompt`

`@cpt:example`
```markdown
### Task Status

- [ ] `p1` - **ID**: `cpt-ex-task-flow-state-task-status`

1. [x] - `p1` - **FROM** BACKLOG **TO** IN_PROGRESS **WHEN** user starts work - `inst-start`
2. [ ] - `p2` - **FROM** IN_PROGRESS **TO** DONE **WHEN** user completes - `inst-complete`
3. [ ] - `p2` - **FROM** DONE **TO** BACKLOG **WHEN** user reopens - `inst-reopen`
```
`@/cpt:example`

### Definitions of Done

`@cpt:heading`
```toml
id = "feature-dod"
level = 2
required = true
numbered = true
multiple = false
pattern = "Definitions of Done"
description = "Definitions of done section."
examples = ["## 5. Definitions of Done"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
Specific implementation tasks derived from flows/algorithms above.
```
`@/cpt:prompt`

`@cpt:heading`
```toml
id = "feature-dod-entry"
level = 3
required = true
numbered = false
multiple = true
template = "{Requirement Title}"
description = "A single definition of done entry."
examples = ["### Task Creation"]
```
`@/cpt:heading`

`@cpt:id`
```toml
kind = "dod"
name = "Definition of Done"
description = "A concrete implementation task derived from flows/processes/states, with required traceability."
required = true
task = true
priority = true
template = "cpt-{system}-dod-{feature-slug}-{slug}"
examples = ["cpt-cypilot-dod-template-system-validation", "cpt-ex-ovwa-dod-launchagent-autostart"]
to_code = true
headings = ["feature-dod-entry"]
```
`@/cpt:id`

`@cpt:prompt`
```markdown
- [ ] `p1` - **ID**: `cpt-{system}-dod-{feature-slug}-{slug}`

The system **MUST** {clear description of what to implement}.

**Implements**:
- `cpt-{system}-flow-{feature-slug}-{slug}`

**Touches**:
- API: `{METHOD} {/path}`
- DB: `{table}`
- Entities: `{EntityName}`
```
`@/cpt:prompt`

`@cpt:example`
```markdown
### Task Creation

- [ ] `p1` - **ID**: `cpt-ex-task-flow-dod-task-create`

Users can create tasks with title, description, priority, and due date. The system validates input and stores the task with BACKLOG status.

**Implementation details**:
- API: `POST /api/tasks` with JSON body `{title, description, priority, due_date}`
- DB: insert into `tasks` table (columns: title, description, priority, due_date, status)
- Domain: `Task` entity (id, title, description, priority, due_date, status)

**Implements**:
- `cpt-ex-task-flow-flow-create-task`
- `cpt-ex-task-flow-algo-validate-task`

**Covers (PRD)**:
- `cpt-ex-task-flow-fr-task-management`
- `cpt-ex-task-flow-nfr-performance`

**Covers (DESIGN)**:
- `cpt-ex-task-flow-principle-realtime-first`
- `cpt-ex-task-flow-constraint-supported-platforms`
- `cpt-ex-task-flow-component-api-server`
- `cpt-ex-task-flow-component-postgresql`
- `cpt-ex-task-flow-seq-task-creation`
- `cpt-ex-task-flow-dbtable-tasks`
```
`@/cpt:example`

### Acceptance Criteria

`@cpt:heading`
```toml
id = "feature-acceptance-criteria"
level = 2
required = true
numbered = true
multiple = false
pattern = "Acceptance Criteria"
description = "Acceptance criteria for the feature."
examples = ["## 6. Acceptance Criteria"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
- [ ] {Testable criterion for this feature}
- [ ] {Another testable criterion}
```
`@/cpt:prompt`

`@cpt:example`
```markdown
- [ ] The feature supports task creation and assignment flow end-to-end
- [ ] Validation rules reject invalid titles, priorities, and past due dates
- [ ] State transitions follow the Task Status state machine
```
`@/cpt:example`
