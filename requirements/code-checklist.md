---
cypilot: true
type: requirement
name: Code Quality Expert Checklist
version: 1.0
purpose: Generic (kit-agnostic) quality checklist for code changes and reviews
---

# Code Quality Expert Checklist (Generic)

<!-- toc -->

- [Procedure](#procedure)
- [Severity](#severity)
- [Review Modes](#review-modes)
- [Engineering Best Practices (ENG)](#engineering-best-practices-eng)
- [Code Quality (QUAL)](#code-quality-qual)
- [Error Handling (ERR)](#error-handling-err)
- [Security (SEC)](#security-sec)
- [Performance (PERF)](#performance-perf)
- [Observability (OBS)](#observability-obs)
- [Testing (TEST)](#testing-test)
- [Validation Summary](#validation-summary)
- [Conflict Resolution](#conflict-resolution)
- [Reporting](#reporting)
- [Reporting Commitment](#reporting-commitment)

<!-- /toc -->

## Procedure
- [ ] Identify the code domain and decide applicability per checklist item.
- [ ] Mark each item `PASS`, `FAIL`, `N/A` with rationale, or `NOT REVIEWED` when excluded by review mode.
- [ ] Never skip silently; missing rationale for an inapplicable item is a violation.
- [ ] Report issues only; each issue includes checklist ID, severity, location, evidence, why it matters, and a concrete fix.
## Severity
- CRITICAL: unsafe/broken/security issue; blocks merge.
- HIGH: major quality issue; fix before merge.
- MEDIUM: meaningful improvement; fix when feasible.
- LOW: minor improvement; optional.
## Review Modes
- Quick: `<50` LOC, low risk; must check `SEC-CODE-001/002/003`, `SEC-CODE-NO-001/002`, `ERR-CODE-001/003`, `ERR-CODE-NO-001`, `QUAL-CODE-NO-002`; spot-check `ENG-CODE-001`, `QUAL-CODE-001`; mark the rest `NOT REVIEWED`.
- Standard: `50-200` LOC, medium risk; check all CRITICAL and HIGH items plus all MUST NOT items.
- Full: `>200` LOC or architectural; check all items; triage order is `SEC`, `ERR`, `QUAL/TEST`, `ENG/QUAL`, `PERF`, `OBS`.
# MUST HAVE
## Engineering Best Practices (ENG)
### ENG-CODE-001: Test-Driven Development (TDD) [HIGH]
- [ ] New behavior has corresponding tests.
- [ ] Tests were written before or alongside implementation.
- [ ] Tests fail if implementation is removed.
- [ ] Tests verify outcomes, not just no-crash behavior.
- [ ] Test names describe the behavior under test.
- [ ] Tests run independently.
### ENG-CODE-002: Single Responsibility Principle (SRP) [HIGH]
- [ ] Each module, class, or function has one reason to change.
- [ ] Functions do one thing well.
- [ ] Classes have a single clear purpose.
- [ ] No god objects or kitchen-sink modules exist.
- [ ] UI, business logic, and data access responsibilities are separated.
### ENG-CODE-003: Open/Closed Principle (OCP) [MEDIUM]
- [ ] Behavior is extended through composition or configuration.
- [ ] New functionality does not require unrelated working code to change.
- [ ] Extension points are clear and intentional.
- [ ] Existing working code is not modified just to add unrelated features.
### ENG-CODE-004: Liskov Substitution Principle (LSP) [HIGH]
- [ ] Implementations honor interface contracts.
- [ ] Subtypes remain substitutable for their base types.
- [ ] Polymorphic use does not cause surprising behavior.
- [ ] Subtypes do not strengthen preconditions.
- [ ] Subtypes do not weaken postconditions.
### ENG-CODE-005: Interface Segregation Principle (ISP) [MEDIUM]
- [ ] Interfaces are small and purpose-driven.
- [ ] Fat interfaces are avoided.
- [ ] Clients depend only on the methods they use.
- [ ] Role interfaces are preferred over header interfaces.
### ENG-CODE-006: Dependency Inversion Principle (DIP) [HIGH]
- [ ] High-level modules do not depend directly on low-level modules.
- [ ] Both layers depend on abstractions.
- [ ] Dependencies are injectable.
- [ ] Core logic is testable without heavy integration setup.
- [ ] External dependencies sit behind interfaces.
### ENG-CODE-007: Don't Repeat Yourself (DRY) [MEDIUM]
- [ ] Copy-paste duplication is absent.
- [ ] Shared logic is extracted with clear ownership.
- [ ] Abstraction happens only after a real repeated pattern appears.
- [ ] Constants are defined once.
- [ ] Common patterns are abstracted appropriately.
### ENG-CODE-008: Keep It Simple, Stupid (KISS) [HIGH]
- [ ] The simplest correct solution was chosen.
- [ ] Unnecessary complexity was avoided.
- [ ] Code remains readable without heavy explanation.
- [ ] Clever tricks were avoided in favor of clarity.
- [ ] Standard patterns were preferred over novelty.
### ENG-CODE-009: You Aren't Gonna Need It (YAGNI) [HIGH]
- [ ] No speculative features were added.
- [ ] No unused abstractions remain.
- [ ] No configuration exists only for hypothetical scenarios.
- [ ] No unused extension points were introduced.
- [ ] Capability was added only for current use cases.
### ENG-CODE-010: Refactoring Discipline [MEDIUM]
- [ ] Refactoring happens only after tests pass.
- [ ] Behavior stays unchanged during refactoring.
- [ ] Structure improves without introducing features.
- [ ] Refactoring occurs in small incremental steps.
- [ ] Refactoring and feature work are not mixed in one commit.
## Code Quality (QUAL)
### QUAL-CODE-001: Readability [HIGH]
- [ ] Naming is clear and descriptive.
- [ ] Naming conventions stay consistent.
- [ ] Code reads clearly.
- [ ] Complex logic is explained when needed.
- [ ] Misleading names and abbreviations are absent.
### QUAL-CODE-002: Maintainability [HIGH]
- [ ] Code is easy to modify.
- [ ] Changes stay localized.
- [ ] Dependencies are explicit and minimal.
- [ ] Hidden coupling is absent.
- [ ] Module boundaries are clear.
### QUAL-CODE-003: Testability [HIGH]
- [ ] Core logic is testable without external systems.
- [ ] Dependencies are injectable for tests.
- [ ] Side effects are isolated and mockable.
- [ ] Behavior is deterministic.
- [ ] Outcomes are observable.
## Error Handling (ERR)
### ERR-CODE-001: Explicit Error Handling [CRITICAL]
- [ ] Errors fail explicitly.
- [ ] Error conditions are handled.
- [ ] Exceptions are not swallowed.
- [ ] Error messages are actionable.
- [ ] Stack traces remain available for debugging without leaking into production UI.
### ERR-CODE-002: Graceful Degradation [HIGH]
- [ ] Partial failures are handled.
- [ ] Recovery actions are defined.
- [ ] Fallback behavior is defined.
- [ ] User-facing errors stay friendly.
- [ ] System-facing errors stay detailed.
### ERR-CODE-003: Input Validation [CRITICAL]
- [ ] All external inputs are validated at system boundaries.
- [ ] Validation rules are clear and consistent.
- [ ] Invalid input is rejected early.
- [ ] Validation errors are specific.
- [ ] Internal code is not redundantly revalidated.
## Security (SEC)
### SEC-CODE-001: Injection Prevention [CRITICAL]
- [ ] Queries are parameterized.
- [ ] Command injection is blocked.
- [ ] XSS is blocked.
- [ ] Path traversal is blocked.
- [ ] User input never enters dangerous contexts unsanitized.
### SEC-CODE-002: Authentication & Authorization [CRITICAL]
- [ ] Required authentication checks exist at relevant entry points.
- [ ] Required authorization checks exist for protected operations.
- [ ] Privilege escalation is prevented.
- [ ] Session management is secure.
- [ ] Credentials are not hardcoded.
### SEC-CODE-003: Data Protection [CRITICAL]
- [ ] Sensitive data is not logged.
- [ ] PII is handled appropriately.
- [ ] Secrets stay out of code.
- [ ] Encryption is used where required.
- [ ] Sensitive data is transmitted securely.
## Performance (PERF)
### PERF-CODE-001: Efficiency [MEDIUM]
- [ ] Obvious performance anti-patterns are absent.
- [ ] N+1 query patterns are avoided.
- [ ] Unnecessary allocations are avoided.
- [ ] Resources are cleaned up properly.
- [ ] Appropriate data structures are chosen.
### PERF-CODE-002: Scalability [MEDIUM]
- [ ] Algorithmic complexity matches expected data size.
- [ ] Hot paths avoid blocking operations.
- [ ] Caching is used where beneficial.
- [ ] Batch operations are used where appropriate.
- [ ] Large datasets use pagination where appropriate.
## Observability (OBS)
### OBS-CODE-001: Logging [MEDIUM]
- [ ] Meaningful boundary events are logged.
- [ ] Log levels are used appropriately.
- [ ] Secrets are not logged.
- [ ] Correlation IDs are propagated.
- [ ] Logs include enough debugging context.
### OBS-CODE-002: Metrics & Tracing [LOW]
- [ ] Key operations expose metrics when applicable.
- [ ] Tracing is integrated where beneficial.
- [ ] Health checks exist.
- [ ] Alertable conditions are identified.
- [ ] Performance baselines are established.
- [ ] `N/A` is used only when the service has no long-running or SLO/SLA requirements.
## Testing (TEST)
### TEST-CODE-001: Test Coverage [HIGH]
- [ ] Public APIs are covered.
- [ ] Happy paths are covered.
- [ ] Error paths are covered.
- [ ] Edge cases are covered.
- [ ] Boundary conditions are covered.
### TEST-CODE-002: Test Quality [HIGH]
- [ ] Tests are fast.
- [ ] Tests are reliable.
- [ ] Tests are independent.
- [ ] Tests are readable.
- [ ] Assertions are clear.
### TEST-CODE-003: Test Completeness [MEDIUM]
- [ ] Business logic has unit tests.
- [ ] External dependencies have integration tests.
- [ ] Critical paths have E2E tests when applicable.
- [ ] Regression scenarios are covered.
- [ ] Tests document expected behavior.
# MUST NOT HAVE
### QUAL-CODE-NO-001: No Incomplete Work Markers [HIGH]
- [ ] Untracked TODO markers are absent.
- [ ] FIXME markers are absent.
- [ ] XXX markers are absent.
- [ ] HACK markers are absent.
- [ ] Temporary production fixes that became permanent are absent.
- [ ] Incomplete work is either finished or tracked in an issue.
### QUAL-CODE-NO-002: No Placeholder Implementations [CRITICAL]
- [ ] `unimplemented!()` / `todo!()` are absent from production logic.
- [ ] `NotImplementedException`-style placeholders are absent from production paths.
- [ ] Python `pass` plus TODO placeholders are absent from production paths.
- [ ] Empty catch blocks are absent.
- [ ] Stub methods that do nothing are absent.
- [ ] Placeholder implementations are either removed or completed.
### ERR-CODE-NO-001: No Silent Failures [CRITICAL]
- [ ] Empty catch blocks are absent.
- [ ] Swallowed exceptions are absent.
- [ ] Fallible return values are not ignored.
- [ ] `_ = might_fail()` patterns without handling are absent.
- [ ] `try/except: pass` patterns are absent.
- [ ] Errors are handled or propagated explicitly.
### ERR-CODE-NO-002: No Unsafe Panic Patterns [HIGH]
- [ ] Bare `unwrap()` is absent from production paths.
- [ ] Bare `panic!()` is absent from production paths.
- [ ] `expect()` calls have meaningful messages.
- [ ] Force-unwrapping without guards is absent.
- [ ] Assertions are absent from production paths.
- [ ] Proper error handling is used instead.
### TEST-CODE-NO-001: No Ignored Tests [MEDIUM]
- [ ] Ignored tests have documented reasons.
- [ ] Disabled tests have documented reasons.
- [ ] Skip markers have explanations.
- [ ] Commented-out tests are absent.
- [ ] Placeholder tests are absent.
- [ ] Ignored tests are fixed or removed.
### SEC-CODE-NO-001: No Hardcoded Secrets [CRITICAL]
- [ ] API keys are absent from code.
- [ ] Passwords are absent from code.
- [ ] Tokens are absent from code.
- [ ] Credentialed connection strings are absent from code.
- [ ] Private keys are absent from code.
- [ ] Secrets are stored in environment variables or secret management.
### SEC-CODE-NO-002: No Dangerous Patterns [CRITICAL]
- [ ] `eval()` with user input is absent.
- [ ] `exec()` with user input is absent.
- [ ] `system()` with user input is absent.
- [ ] `innerHTML` with user input is absent.
- [ ] SQL string concatenation is absent.
- [ ] Safe alternatives are used.
## Validation Summary
- [ ] All required MUST HAVE items for the selected review mode were checked.
- [ ] All MUST NOT items in scope were checked.
- [ ] Build or compilation passes, or exceptions are explicitly justified.
- [ ] Unit, integration, and E2E test status is verified, or exceptions are explicitly justified.
- [ ] Linting passes, or exceptions are explicitly justified.
- [ ] Coverage requirements are met, or exceptions are explicitly justified.
- [ ] All violations and critical issues are documented with specific feedback.
## Conflict Resolution
- Priority: `SEC > ERR > QUAL/TEST > ENG/QUAL > PERF > OBS`.
- Use these defaults: `KISS > DRY` when abstraction is wrong, `YAGNI > OCP` for hypothetical extension points, readability before premature optimization, coverage before speed on critical paths, and detailed logs with friendly user messages.
- When uncertain, choose the safer failure mode: security/data loss > inconvenience > performance, and document the trade-off.
## Reporting
- Report only problems.
- Quick: compact table `| # | ID | Sev | Location | Issue | Fix |` plus review-mode note.
- Standard: compact or full format.
- Full: for each issue include `Issue`, `Location`, `Evidence`, `Why It Matters`, and `Proposal`.
## Reporting Commitment
- [ ] Every found issue is reported.
- [ ] The required report format is used.
- [ ] Each issue includes evidence and impact.
- [ ] Each issue includes a concrete fix.
- [ ] No known problems are hidden or omitted.
- [ ] The report is ready for iteration and re-review.
