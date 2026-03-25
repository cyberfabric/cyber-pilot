---
cypilot: true
type: requirement
name: Bug-Finding Methodology
version: 1.0
purpose: Compact language-agnostic methodology for high-recall bug discovery in source code
---

# Bug-Finding Methodology

**Scope**: Source-code analysis for correctness, logic, reliability, security, concurrency, performance, and integration defects across programming languages.

**Non-goal**: guarantee `100%` bug detection. That is not achievable in the general case because programs depend on incomplete specifications, runtime environment, dynamic inputs, external systems, and nondeterministic behavior. The practical target is **maximum recall with explicit uncertainty, evidence, and escalation paths**.

## Core Principles

- Combine complementary signals. Pattern rules, semantic reasoning, data-flow review, dynamic checks, and historical evidence catch different bug classes.
- Optimize for recall first, then calibrate precision with evidence. Missing a bug is usually worse than investigating one plausible candidate.
- When recall and compactness conflict, keep the smallest slice that still covers the full invariant or boundary under test. Expand immediately when a plausible bug depends on unseen callers, callees, shared state, config, or cross-language contracts.
- Work from **invariants and failure modes**, not from language syntax alone. This keeps the method portable across languages.
- Never claim `all bugs found`. Report confidence and residual uncertainty explicitly.
- Load only the code needed for the current reasoning slice. Expand context only when call graph, state flow, or boundary contracts require it.
- A single LLM pass is insufficient. CodeRabbit-like quality requires a **layered review stack**, not just a better prompt.

## Context Budget & Expansion Control

- This section is the single canonical hotspot budget and escalation rule for the methodology.
- Start each hotspot with a working set of `<= 5` files and `<= 800` active code lines.
- Summarize and drop already-processed context before expanding.
- Expand only when the current slice cannot confirm or refute a plausible bug in the active invariant, state transition, or boundary contract.
- For companion requirements or checklists, load the smallest decisive slice first: TOC, then review-mode or reporting slices, then only the specific item sections required by the chosen review mode or the active hotspot, then one contiguous line range if needed. A slice is decisive only when the inspected text is sufficient to resolve the hotspot-relevant normative effect: whether that dependency changes the active invariant, required check, status rule, boundary contract, or validation obligation for the hotspot under review. Do not whole-file load a companion dependency by default.
- Keep companion coverage bounded to `<= 2` dependency files and `<= 240` raw dependency lines in active context for one review pass; summarize and drop raw dependency text before loading the next slice.
- Treat a companion as proved non-material only when the inspected slice is sufficient to show that the remaining unseen text cannot change those hotspot-relevant obligations and any remaining mentions are purely descriptive, duplicative, or outside the reviewed hotspot. If that proof is missing, the companion remains unresolved.
- If a hotspot still needs more than `1500` active code lines, more than `2` expansion rounds, or companion coverage beyond the dependency budget, stop broadening, emit a checkpoint with the unresolved boundary, and mark the review `PARTIAL` unless a confirmed material defect already makes it `FAIL`.
- Recommend a focused follow-up pass or dynamic validation instead of claiming broader coverage.

## Layer Map

| Layer | Question |
|---|---|
| L1 | Where are the real risk hotspots? |
| L2 | What contracts and invariants must always hold? |
| L3 | Which paths, states, and interleavings can violate them? |
| L4 | Which universal bug classes apply here? |
| L5 | Can a concrete counterexample be constructed? |
| L6 | What dynamic check would confirm or refute the finding? |
| L7 | What is the overall review status, confidence, impact, and next action? |

## L1: Risk Hotspot Mapping

Focus first on code that is most likely to contain high-impact defects.

- Start from changed code, entry points, trust boundaries, persistence boundaries, async boundaries, and externally visible behavior.
- Prioritize authentication, authorization, money movement, state transitions, retries, parsing, serialization, migrations, caching, and cleanup logic.
- Expand to callers, callees, shared utilities, and configuration only when they influence the active path.
- Use repository signals when available: churn, incident history, bug-fix patterns, flaky tests, complex functions, and modules with many dependencies.

## L2: Contract & Invariant Extraction

Extract what must be true before, during, and after execution.

- Preconditions: input shape, nullability, permissions, ordering, initialization, feature flags, units, and schema assumptions.
- Postconditions: returned value, persisted state, emitted events, side effects, idempotency, and cleanup guarantees.
- Cross-step invariants: uniqueness, monotonicity, ownership, transactional boundaries, retry safety, and consistency between cache, database, and outbound messages.
- If the contract is not explicit, infer it from tests, names, types, assertions, error messages, docs, and call sites, but mark it as inferred rather than proven.

## L3: Path, State, and Interleaving Exploration

Trace how bugs emerge when the happy path breaks.

- Check the main path, unhappy path, edge values, repeated invocation, partial failure, timeout, retry, stale state, invalid config, startup, shutdown, and rollback behavior.
- For stateful logic, trace creation, mutation, persistence, invalidation, and cleanup.
- For async or concurrent logic, examine races, double delivery, out-of-order completion, missing awaits, lock ordering, cancellation, and duplicate side effects.
- For distributed flows, examine retries, deduplication, eventual consistency gaps, and split-brain assumptions between services.

## L4: Universal Bug-Class Sweep

Apply the same defect lenses regardless of language.

| Class | Typical failures |
|---|---|
| Correctness & logic | Wrong branch, inverted condition, off-by-one, missing case, unreachable branch, bad default |
| Input & boundary | Missing validation, parse mismatch, encoding mismatch, unit mismatch, schema drift |
| Error handling & resilience | Swallowed error, wrong fallback, retry storm, partial commit, misleading success |
| State & lifecycle | Wrong initialization order, stale cache, missing cleanup, duplicate apply, broken rollback |
| Security & trust boundary | Authz gap, injection path, traversal, unsafe deserialization, secret or PII leak |
| Concurrency & async | Race, deadlock, lost update, double execution, missing await, cancellation bug |
| Performance & resources | N+1, unbounded loop, leak, blocking hot path, missing backpressure |
| Integration & config | Version drift, env mismatch, clock/timezone bug, feature-flag inversion, protocol mismatch |
| Testing gaps | Missing regression coverage for critical or failure paths |

## L5: Counterexample Construction

A suspected bug becomes stronger when you can describe exactly how it fails.

- Build the smallest trigger: input, prior state, ordering, timing, or configuration needed to break the invariant.
- Express the failure as `condition -> execution path -> bad outcome`.
- Search for contradictory code, assertions, tests, or guards that disprove the hypothesis.
- If no plausible trigger can be constructed, lower confidence or discard the finding.

## L6: Dynamic Escalation Strategy

When static reasoning is insufficient, specify the cheapest next proof.

- Use targeted unit tests for local logic and boundary conditions.
- Use integration tests for persistence, network, serialization, configuration, and cross-service behavior.
- Use property-based tests or fuzzing for parsers, protocol handlers, validators, and state machines.
- Use semantic static analysis or data-flow engines for taint, authorization, and multi-hop flow issues.
- Use runtime traces, logs, metrics, and production incidents for nondeterministic or environment-sensitive failures.

**Practical layered stack**:

- Hotspot triage plus invariant and failure-path review on bounded local slices
- Universal bug-class sweep plus counterexample construction on the highest-risk paths
- Cheapest confirming proof next: targeted tests, semantic/static analyzers, runtime evidence, then feedback from escaped defects or incidents

## L7: Reporting, Review Status, and Residual Risk

Overall review status is mandatory:

- `PASS`: the stated scope was completed, every hotspot in scope was checked enough to resolve the active bug hypotheses, every required companion slice for the final report was covered within budget, no confirmed or high-confidence material defect remains open, and residual risk is explicitly bounded.
- `PARTIAL`: coverage is incomplete, a hotspot or companion dependency was checkpointed, a material hypothesis still needs more bounded context, or dynamic validation is still required before the review can close safely.
- `FAIL`: the review path was invalid or at least one confirmed or high-confidence material defect remains open.

Mandatory status triggers:

- Use `PARTIAL` when the canonical hotspot budget forced a stop, any required companion slice remains unresolved, or follow-up validation is still required for a material hotspot.
- Use `FAIL` when methodology requirements were not followed well enough for a valid review or when an open material defect still stands at report time.
- Never use `PASS` when unresolved hotspots, unresolved companion effects, or required follow-up validation remain.
- A companion counts as checked only after its inspected slice resolved the hotspot-relevant normative effect or proved the dependency non-material by the decision rule in `Context Budget & Expansion Control`; otherwise it stays unresolved and forces `PARTIAL`.

Report each finding with:

- Bug class
- Severity
- Confidence: `CONFIRMED`, `HIGH`, `MEDIUM`, or `LOW`
- Location
- Violated invariant or contract
- Minimal trigger or counterexample
- Impact
- Evidence
- Proposed fix
- Best validation step

Residual uncertainty is mandatory:

- List unproven high-risk areas.
- List required dynamic checks not yet run.
- State which bug classes were checked and which were only partially checked.
- State why the final status is `PARTIAL` or `FAIL` whenever either value is used.
- Never collapse uncertainty into a blanket `PASS`.

Final review output is mandatory. This methodology defines the authoritative bug-finding content contract, but a host workflow may still control the outer response wrapper.

For a standalone bug-finding report, use these sections in order; this order is authoritative even when companion checklists are loaded:

- `Review Summary`: review status, target scope, hotspots reviewed, files inspected, whether the review stayed local or expanded, and which companion slices were loaded.
- `Findings`: severity-sorted findings using the required per-finding fields above. Report only problems. If none, state `No confirmed findings`.
- `Coverage & Residual Risk`: bug classes checked, bug classes only partially checked, unchecked high-risk hotspots, dynamic checks not yet run, checklist mode used, any checklist items or companion coverage still unverified, and a checklist ledger for item-level status accounting when `code-checklist.md` is in scope.
- `Next Actions`: cheapest confirming validations, required context expansions, or an explicit statement that no further action is currently justified.

When a host workflow already defines mandatory top-level headings, keep that outer structure and map this methodology into it instead of replacing the workflow headings. For `/cypilot-analyze`, keep the six-section `Validation Report` wrapper, place `Review Summary`, `Coverage & Residual Risk`, and `Next Actions` inside the bug-finding portion of `### 3. Semantic Review (MANDATORY)`, and surface actual defects from `Findings` in `### 6. Issues (if any)`. Do not introduce competing top-level headings.

Inside `Coverage & Residual Risk`, include a compact checklist ledger for checklist items required by the selected review mode or explicitly loaded and assessed in the current pass, using the columns `ID | Status | Rationale`. Allowed status values are `PASS`, `FAIL`, `N/A`, and `NOT REVIEWED`. Preserve item-level accounting for review-mode-excluded items without forcing whole-checklist expansion: record each excluded item as `NOT REVIEWED` with rationale `excluded by review mode`, but compact rows are allowed only when they still enumerate the exact checklist IDs covered by that row, using exact ID lists or contiguous ID ranges/lists only when every ID in that row shares the same status and rationale. Use `NOT REVIEWED` for explicitly checkpointed loaded items only after their governing slice was identified. Keep `Findings` problem-only; record `PASS`, `N/A`, and `NOT REVIEWED` entries in the ledger instead of inventing extra top-level sections, and summarize any other unloaded checklist remainder as unresolved coverage rather than implying whole-checklist review.

Companion checklist integration rules:

- When `code-checklist.md` is in scope, keep this section order instead of replacing it with a separate quick/standard/full top-level format.
- Satisfy the checklist's reporting minimums inside `Findings` by making `Location`, `Evidence`, `Impact`, and `Proposed fix` explicit in every reported problem; do not duplicate the same content under a second heading set.
- Put checklist acceptance/reporting evidence in `Coverage & Residual Risk`, not in a competing report preamble.
- This four-section contract supersedes only `code-checklist.md`'s top-level report shape when this methodology is the outer report contract. It does **not** waive that checklist's item-by-item applicability decisions, item-level `NOT REVIEWED` accounting for review-mode-excluded items, status labels, rationale requirements, or review-mode obligations.

## Integration with Cypilot

- Use this methodology when the user asks to find bugs, logic errors, edge cases, regressions, hidden failure modes, or "all problems" in code.
- Load `reverse-engineering.md` WHEN the bug review needs structure beyond the local hotspot: entry points, module boundaries, dependency direction, state lifecycle, or integration boundaries. Start with a TOC, section, or contiguous line-range read, then summarize and drop it before loading the next slice. Skip it for bounded local reviews where those are already clear.
- Load `code-checklist.md` before final output as a mandatory acceptance and reporting checklist, but start with only the reporting, procedure, review-mode, conflict-resolution, and specific checklist-item slices required by the chosen review mode or already implicated by the hotspot. Do not load unrelated checklist sections by default.
- Companion dependency loading is bounded by `Context Budget & Expansion Control`. If required review-mode coverage or other required companion coverage cannot be completed safely within that budget, checkpoint the unresolved dependency, set the final review status to `PARTIAL`, and recommend a focused follow-up instead of forcing a broader ledger or `PASS`.
- Use this methodology as the **search procedure** that drives what code paths and failure modes to inspect first.

## Execution Protocol

Use this sequence for each hotspot:

1. Map the boundary and impacted path.
2. Extract explicit and inferred invariants.
3. Walk the happy path and the most dangerous unhappy paths.
4. Sweep all universal bug classes.
5. Build or refute a concrete counterexample.
6. Propose the cheapest confirming dynamic check.
7. Report confidence and residual risk.

Efficiency rules:

- Apply `Context Budget & Expansion Control` as the single canonical hotspot budget and escalation rule for every hotspot.
- Keep only the active path, invariant, and evidence in working context; summarize and drop processed code before expanding.
- Expand to adjacent files or companion requirements only when a plausible bug depends on that boundary and the current slice cannot resolve it.
- If the canonical budget forces a stop, emit a checkpoint and set status per `L7` instead of broadening implicitly.

## Validation

Review is complete when:

- [ ] Risk hotspots were identified and prioritized
- [ ] Explicit and inferred invariants were extracted
- [ ] Happy path and failure paths were both examined
- [ ] All universal bug classes were swept for the target scope
- [ ] Each reported issue includes a plausible trigger or counterexample
- [ ] Missing proof was converted into a concrete dynamic follow-up
- [ ] Review status, bounded companion coverage, and residual uncertainty were reported explicitly
- [ ] Any unresolved companion dependency or required follow-up validation forced `PARTIAL` instead of `PASS`
- [ ] Final output either used the standalone four-section order or mapped it into the host workflow's mandatory wrapper without competing top-level headings
- [ ] No claim of `100%` detection or blanket coverage was made
