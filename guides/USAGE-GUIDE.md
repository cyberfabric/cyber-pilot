# Cypilot Usage Guide

How to use **Cypilot** effectively across common situations, and how to avoid the most common failure modes.

> **Convention**: 💬 = paste into AI agent chat. 🖥️ = run in terminal.

---

## Table of Contents

- [1. What this guide is for](#1-what-this-guide-is-for)
- [2. The shortest mental model](#2-the-shortest-mental-model)
- [3. When Cypilot is a good fit](#3-when-cypilot-is-a-good-fit)
- [4. When Cypilot is not the best first move](#4-when-cypilot-is-not-the-best-first-move)
- [5. Choosing the right workflow](#5-choosing-the-right-workflow)
- [6. Best practices](#6-best-practices)
- [7. Bad practices and anti-patterns](#7-bad-practices-and-anti-patterns)
- [8. Situation-by-situation guidance](#8-situation-by-situation-guidance)
- [9. Prompt patterns that usually work well](#9-prompt-patterns-that-usually-work-well)
- [10. Prompt patterns that usually go wrong](#10-prompt-patterns-that-usually-go-wrong)
- [11. Workspace federation and orchestration repo pattern](#11-workspace-federation-and-orchestration-repo-pattern)
- [12. Brownfield projects](#12-brownfield-projects)
- [13. Delegation and autonomous execution](#13-delegation-and-autonomous-execution)
- [14. Quick decision checklist](#14-quick-decision-checklist)
- [Further reading](#further-reading)

---

## 1. What this guide is for

This guide is for the classic practical questions:

- **What should I do in this situation?**
- **What should I avoid?**
- **When should I use `plan`, `generate`, or `analyze`?**
- **When is Cypilot useful, and when is it just overhead?**
- **How do I get the benefits without using the product badly?**

The focus is not abstract theory.

The focus is operational behavior: how to use Cypilot well in real projects.

---

## 2. The shortest mental model

Cypilot is best understood as a **deterministic orchestration, validation, and traceability layer** for AI-assisted engineering.

Use the LLM for:

- **reasoning**
- **writing**
- **transformation**
- **implementation judgment**

Use Cypilot for:

- **workflow routing**
- **context loading**
- **rules and templates**
- **deterministic validation**
- **traceability**
- **planning large tasks**

If you use Cypilot like a generic prompt prefix, you will miss most of its value.

---

## 3. When Cypilot is a good fit

Cypilot is a strong fit when one or more of these are true:

- **You are transforming one structured artifact into another**
  
  Example: `PRD -> DESIGN -> DECOMPOSITION -> FEATURE`.

- **You need deterministic validation**
  
  Example: structure, IDs, references, consistency, or checklist-driven review.

- **The task is large enough to overflow one conversation**
  
  Example: migrations, refactors, multi-file changes, or big feature delivery.

- **You need traceability between docs and code**
  
  Example: regulated environments, auditability, or spec-driven development.

- **You want one repeatable workflow across multiple AI tools**
  
  Example: the team uses Claude Code, Cursor, Windsurf, Copilot, or multiple hosts.

- **You need cross-repo coordination**
  
  Example: docs in one repo, code in another, shared kits in a third.

- **You want checklist-based review to be repeatable**
  
  Example: design review, PR review, or status reporting that should follow the same structure across runs.

- **You want team-level process standardization**
  
  Example: multiple engineers or AI hosts should follow the same planning, validation, and review discipline.

---

## 4. When Cypilot is not the best first move

Cypilot is often not the best first move when:

- **The task is tiny**
  
  Example: a one-file typo fix or a very small local change.

- **You are still doing open-ended discovery**
  
  Example: "let's brainstorm five different product directions."

- **You want maximum first-draft speed with minimum ceremony**
  
  Example: throwaway prototypes or disposable spikes.

- **You do not yet have enough structure to anchor the work**
  
  Example: no source docs, no clear scope, no acceptance criteria.

- **You do not need validation, traceability, rules, or planning**
  
  Example: a small repo with lightweight expectations and low risk.

- **Your token budget is very tight**
  
  Example: the task is small enough that loading workflow context, rules, and validation logic costs more than it helps.

- **You are doing pure visual or frontend exploration**
  
  Example: the UI direction is still open-ended and design exploration matters more than structure.

- **You want the fastest possible first draft with minimal ceremony**
  
  Example: quick spec drafting, loose ideation, or throwaway first passes where controlled transformation is not yet the priority.

- **You are exploring many disposable alternatives**
  
  Example: branching into multiple speculative directions with little commitment to stable structure.

That is not a bug.

It is the tradeoff of using a more structured system.

For these cases, lighter approaches or direct agent prompting can be a better starting point.

---

## 5. Choosing the right workflow

### Use `plan` when

- the task is large
- the task is risky
- the task touches many files or systems
- the context will likely overflow one conversation
- you need inspectable phases and recovery points

### What counts as a large task

A task is usually large enough for `plan` if one or more of these are true:

- it will likely take **multiple implementation steps** rather than one clean edit
- it touches **multiple files, modules, services, or artifacts**
- it depends on **ordering**, such as migration first, refactor second, rollout third
- it has meaningful **risk of drift**, breakage, or hidden dependency mistakes
- it will require **multiple validate-review-fix cycles**
- you cannot describe the safe implementation in one short bounded prompt without dropping important constraints
- you already expect follow-up requests such as “now do the next part”, “now validate”, or “now review what changed”

In practice, “large” does not only mean many lines of code.

It also means **too much coordination, risk, or context to trust to one generation step**.

### Quick check: should you use `plan` first?

Ask yourself:

- do I need more than one meaningful step to do this safely?
- do I need checkpoints or recovery points?
- will the agent need to remember many constraints at once?
- will I probably review intermediate results before continuing?
- would a bad first pass be expensive to unwind?

If the answer is **yes** to two or more of these, `plan` is usually the safer default.

If you are unsure, prefer `plan`.

Why this matters:

- planning keeps context smaller
- planning makes instructions more stable
- planning makes progress inspectable
- planning turns long work into an operational sequence instead of one overloaded request

**Good prompt shape**:

- 💬 `cypilot plan: break this auth migration into safe implementation phases`

### Use `generate` when

- you want to create or update an artifact
- you want to implement already-structured work
- the target and source materials are known
- the main need is execution, not diagnosis

**Good prompt shape**:

When a prompt below references `PRD`, `DESIGN`, `DECOMPOSITION`, or `FEATURE`, it assumes the built-in SDLC kit is installed.

- 💬 `cypilot generate: implement the approved FEATURE for login rate limiting` *(requires SDLC kit)*

### Use `analyze` when

- you want to validate something
- you want a review or audit
- you want to compare two artifacts
- you want to inspect gaps, drift, or consistency

**Good prompt shape**:

- `cypilot analyze: validate architecture/DESIGN.md against the current FEATURE docs` *(requires SDLC kit)*

### What `analyze` can do in practice

`/cypilot-analyze` is not only for generic validation. In practice, it covers several distinct review and inspection modes.

Examples in this section that reference `PRD`, `DESIGN`, `DECOMPOSITION`, or `FEATURE` assume the built-in SDLC kit is installed.

- **Artifact and traceability validation**
  - Use it when you want deterministic checks for structure, IDs, references, checklists, and code-marker traceability.
  - Good fit for: validating a PRD, DESIGN, FEATURE, or checking whether code and artifacts still line up when those artifact kinds come from the SDLC kit.
  - Typical prompt shape: 💬 `cypilot analyze: validate this FEATURE and its code traceability` *(requires SDLC kit)*

- **Prompt and instruction review**
  - Use it for system prompts, skills, workflows, methodologies, `AGENTS.md`, and other AI-instruction documents.
  - This is the right path when you want clarity review, anti-pattern detection, context-engineering review, compact-prompts opportunities, or improvement guidance.
  - Typical prompt shape: 💬 `cypilot analyze: review this workflow for prompt engineering quality`

- **Prompt bug finding**
  - Use it when the goal is not just instruction quality, but hidden behavioral defects: unsafe behavior, routing defects, missing guards, bad completion criteria, regressions, or instruction conflicts.
  - Ask for this explicitly when you want defect-oriented review rather than a general style review.
  - Typical prompt shape: 💬 `cypilot analyze: find prompt bugs in this workflow and agent instruction stack`

- **Code review**
  - Use it for structured checklist-based code review, including quality, security, error handling, testing, performance, and observability concerns.
  - Good fit when you want a disciplined review of code changes instead of an unstructured opinion.
  - Typical prompt shape: 💬 `cypilot analyze: review these code changes for correctness, security, and test gaps`

- **Code bug finding**
  - Use it when you want maximum-recall search for logic bugs, edge cases, regressions, hidden failure modes, or root-cause analysis.
  - This is stronger than a generic code review when the main objective is to find defects, not just assess quality.
  - Typical prompt shape: 💬 `cypilot analyze: find bugs, edge cases, and regression risks in this module`

- **Consistency, contradiction, gap, and drift analysis**
  - Use it when docs or artifacts may disagree, duplicate each other, use inconsistent terminology, contain stale claims, or leave important requirements unspecified.
  - Good fit for README/guide cleanup, cross-document consistency review, or checking whether a downstream artifact drifted away from its source.
  - Typical prompt shape: 💬 `cypilot analyze: find consistency gaps and contradictions across these guides`

- **Reverse engineering and brownfield understanding**
  - Use it when you need Cypilot to map entry points, structure, dependencies, data flow, state, integration boundaries, and recurring patterns in an existing project.
  - Good fit before planning changes in an unfamiliar codebase.
  - Typical prompt shape: 💬 `cypilot analyze: explain the current architecture boundaries, entry points, and likely conventions`

- **PR review**
  - Use it for structured pull-request review when you want checklist-based findings rather than ad hoc comments.
  - Good fit for isolated review passes, especially before merge or when you want a first-pass issue sweep.
  - Typical prompt shape: 💬 `cypilot analyze: review PR #123 for correctness, regression risk, and checklist violations`

- **Traceability lookup and impact inspection**
  - Use Cypilot's search and validation tools when you need to know where an ID is defined, where it is used, what content it points to, or what may be affected by a change.
  - Good fit for gap analysis, change impact checks, and artifact-to-code audits.
  - Typical tools and commands include `validate`, `list-ids`, `get-content`, `where-defined`, and `where-used`.

How to choose between them:

- if you want **deterministic structure and reference checks**, start with validation
- if you want **quality review of prompts/instructions**, ask for prompt review
- if you want **behavioral defects in prompts**, ask explicitly for prompt bug finding
- if you want **quality review of code**, ask for code review
- if you want **maximum-recall defect hunting in code**, ask explicitly for bug finding
- if you want **cross-document alignment**, ask for consistency, contradiction, gap, or drift analysis
- if you first need to **understand an unfamiliar system**, start with reverse engineering or brownfield analysis before generation
- if your request depends on `PRD`, `DESIGN`, `DECOMPOSITION`, or `FEATURE`, make the SDLC kit dependency explicit instead of implying those artifact kinds exist everywhere

For large reviews, multi-file audits, or anything likely to exceed one safe context, route through `plan` first and then execute the analysis in bounded phases.

### Default routing rule

If a request is both **large** and **generative**, prefer:

- **plan first**
- **generate second**
- **analyze throughout**

A large request should usually become a plan first instead of being forced through one overloaded `generate` call.

### Recommended execution loop for artifacts and code

For most non-trivial work on artifacts or code, the safest default loop is:

- **plan or generate**
- **validate**
- **review**
- **fix errors and gaps**
- **validate again**
- **repeat until known issues are found and addressed**

This applies both to:

- **artifact work** such as `PRD -> DESIGN -> DECOMPOSITION -> FEATURE`
- **code work** such as implementing a FEATURE, refactoring a module, or aligning code with a DESIGN

This loop improves quality, but it does **not** guarantee correctness.

A final **human review is still required** before treating the result as done.

---

## 6. Best practices

1. **Start from a clear target**
   - Name the artifact, code area, workflow, or outcome.

2. **Prefer structured inputs over vague intent**
   - Give the agent source docs, constraints, and boundaries.

3. **Use `plan` before context gets out of control**
   - Do not wait until the conversation is already overloaded.

4. **Validate early, not only at the end**
   - Run deterministic checks before downstream drift accumulates.

5. **Use Cypilot for what is deterministic**
   - Structure, routing, validation, IDs, rules, templates.

6. **Use the LLM for what is judgment-heavy**
   - Reasoning, writing, tradeoffs, interpretation.

7. **Keep upstream artifacts healthy**
   - Weak PRDs and weak DESIGN docs create weak downstream results.

8. **Use workspaces when the system is multi-repo**
   - Do not force all artifacts and code into one repo model if reality is different.

9. **Make review repeatable**
   - Use checklists and analysis flows before human review, not instead of human review.

10. **Treat delegation as supervised automation**
    - Especially when validation may produce false positives.

11. **Be explicit about what must not change**
    - Say what is in scope and what is out of scope.

12. **Use the smallest workflow that still preserves control**
    - Do not over-apply heavyweight flows to trivial tasks.

13. **Keep artifacts and code in sync**
    - When implementing from a spec, treat the artifact and the codebase as one connected system.

14. **If code markers are missing, ask the agent to add them**
    - If the agent implemented the code but did not place `@cpt-*` markers where they are required, explicitly ask it to add the missing markers.

15. **Use the same loop for code that you use for artifacts**
    - Generate or implement, validate, review, fix, validate again, and repeat until the remaining known issues are resolved.

16. **Require final human review for code changes**
    - Validation and AI review help catch many issues, but they do not replace engineering judgment.

17. **Use a fresh chat for generation and review tasks**
    - For substantial `generate` and `analyze` or review tasks, prefer a new chat. If you stay in the same session, clear context before the next task. In environments such as Claude or Codex-style chat shells, `💬 /clear` is a practical reset.

18. **Use Cypilot deterministic checks in CI, not only in chat**
    - If a check can be run through `cpt` or the repo Makefile, put it into your local pre-PR routine and your CI pipeline so structural regressions are caught automatically.

19. **Name SDLC kit dependencies explicitly**
    - If a prompt, example, or workflow depends on `PRD`, `DESIGN`, `DECOMPOSITION`, `FEATURE`, SDLC templates, or SDLC example validation, say that it requires the SDLC kit instead of implying those artifact kinds are universal.

### CI with `cpt` tools

The main Cypilot-oriented CI checks should be expressed in terms of direct `cpt` commands:

- 🖥️ `cpt validate`
- 🖥️ `cpt self-check`
- 🖥️ `cpt validate-kits`
- 🖥️ `cpt validate-kits kits/sdlc`
- 🖥️ `cpt spec-coverage --system cypilot --min-coverage 90 --min-file-coverage 60 --min-granularity 0.45`

Use them as deterministic gates around artifact and methodology changes.

What they are for:

- **`cpt validate`**
  - Validates artifacts and code with deterministic checks for structure, cross-references, task status consistency, and traceability markers.

- **`cpt self-check`**
  - Validates examples against templates and is especially useful for SDLC example/template synchronization.

- **`cpt validate-kits`**
  - Validates kit configuration, templates, constraints, and resource paths across registered kits.

- **`cpt validate-kits kits/sdlc`**
  - Focuses kit validation specifically on the SDLC kit.

- **`cpt spec-coverage --system cypilot --min-coverage 90 --min-file-coverage 60 --min-granularity 0.45`**
  - Measures marker coverage with explicit thresholds so CI can fail on traceability regressions.

Practical recommendation:

- run the most relevant checks locally before opening a PR
- keep the same checks in CI so review is not the first place they run
- use narrower checks during iteration and broader checks before merge

Good default pattern:

- for general methodology changes: 🖥️ `cpt validate`
- for SDLC artifact/template changes: 🖥️ `cpt self-check`
- for kit changes: 🖥️ `cpt validate-kits` or 🖥️ `cpt validate-kits kits/sdlc`
- for spec-traceability discipline: 🖥️ `cpt spec-coverage --system cypilot --min-coverage 90 --min-file-coverage 60 --min-granularity 0.45`

Typical CI snippets:

- 🖥️ `cpt validate --local-only`
- 🖥️ `cpt self-check`
- 🖥️ `cpt validate-kits`
- 🖥️ `cpt validate-toc PRD.md guides/USAGE-GUIDE.md`
- 🖥️ `cpt spec-coverage --system cypilot --min-coverage 90 --min-file-coverage 60 --min-granularity 0.45`

If your repository also provides a `Makefile`, treat it as a convenience wrapper around these `cpt` commands, not as the canonical description of the checks themselves.

The goal is simple: let humans review meaning and tradeoffs, while CI enforces the deterministic rules every time.

---

## 7. Bad practices and anti-patterns

1. **Using Cypilot as just another chat prefix**
   - This ignores workflows, validation, kits, and structure.

2. **Starting with `generate` on a huge ambiguous task**
   - This usually creates drift, missed constraints, and context overload.

3. **Expecting IDs to guarantee good code**
   - IDs improve traceability, not architecture quality. They help link artifacts, track what was specified and implemented, and detect drift, but they do not guarantee good requirements, good design, or good implementation judgment.

4. **Skipping validation until the end**
   - By then the system may already have amplified upstream errors.

5. **Using Cypilot for purely open-ended ideation**
   - It is built for structure, not maximum free-form exploration.

6. **Treating deterministic checks as full review**
   - Validation is not equivalent to human engineering judgment.

7. **Applying full orchestration setup to every tiny repo by default**
   - This creates avoidable overhead in small projects.

8. **Ignoring workspace federation when the real system is multi-repo**
   - That causes artificial constraints and path confusion.

9. **Delegating autonomous loops without monitoring**
   - False positives can send automation in the wrong direction.

10. **Asking for outcomes without naming source-of-truth artifacts**
    - The agent then guesses instead of transforming.

11. **Loading too much context when less would do**
    - More context is not always better; it can reduce clarity and stability.

12. **Using Cypilot where plain editing is enough**
    - Sometimes the structured workflow costs more than the task.

13. **Implementing code from artifacts without validating traceability**
    - That breaks the artifact-to-code chain and makes later review and maintenance harder.

14. **Leaving missing code markers uncorrected**
    - If markers are required and missing, do not just accept the code as-is; ask the agent to place the markers correctly.

15. **Treating repeated validate-fix cycles as a guarantee of correctness**
    - Iteration improves confidence, but it does not eliminate the need for final human review.

16. **Reusing stale context across unrelated generation or review tasks**
    - Old context can leak assumptions into the next task. Start a new chat or clear the context first.

---

## 8. Situation-by-situation guidance

### Situation: new project setup

**Do**:

- 🖥️ `cpt init`
- 🖥️ `cpt generate-agents`
- 💬 `cypilot on`

**Do not**:

- assume the AI tool already knows the project structure
- skip agent generation and then expect integrated workflows to exist

### Situation: existing repo with no conventions captured

**Do**:

- 💬 `cypilot auto-config`
- inspect generated rules and config
- refine what auto-config inferred

**Do not**:

- assume auto-config is perfect
- treat inferred conventions as unquestionable truth

### Situation: create or update a document

**Do**:

- use `generate`
- point at the source artifact explicitly
- state the exact target artifact

**Do not**:

- ask for “a better spec” without naming the current source
- mix five unrelated artifact changes into one prompt

### Situation: large implementation request

**Do**:

- start with `plan`
- execute phase by phase
- validate after meaningful steps
- review the produced code against the relevant artifacts
- fix issues and re-run validation until the known problems are addressed

**Do not**:

- try to push the full change through a single huge `generate` request
- treat one successful generation pass as final proof that the result is correct

### Situation: implementing code from an approved artifact

**Do**:

- use `generate` if the implementation target is already clear
- point to the exact FEATURE, DESIGN, or DECOMPOSITION artifact *(requires SDLC kit when using those SDLC artifact kinds)*
- ask the agent to preserve or add required `@cpt-*` markers in code
- validate and review after implementation

**Do not**:

- ask for implementation without naming the governing artifact
- let code drift away from the approved artifact set
- assume traceability markers will always be added automatically

### Situation: the agent changed code but did not place markers

**Do**:

- explicitly ask the agent to add the missing `@cpt-*` markers
- point to the relevant artifact IDs if needed
- re-run validation after the markers are added

**Do not**:

- manually assume traceability is fine without checking
- continue downstream review while known required markers are still missing

### Situation: code review or design review

**Do**:

- use `analyze`
- compare implementation against artifacts or checklists
- keep deterministic validation in the loop

**Do not**:

- use free-form review only when structured review is possible

### Situation: small low-risk fix

**Do**:

- ask whether Cypilot is actually needed
- use the smallest flow that preserves enough control

**Do not**:

- force a full structured process onto trivial edits

### Context hygiene

- 💬 start a new chat before a new generation or review task
- 💬 `/clear` before the next task if you stay in the same Claude or Codex-style session

---

## 9. Prompt patterns that usually work well

Prompts in this section that reference `PRD`, `DESIGN`, `DECOMPOSITION`, or `FEATURE` assume the built-in SDLC kit is installed.

### Structured generation

- 💬 `cypilot generate: create a DESIGN from architecture/PRD.md for the billing service` *(requires SDLC kit)*
- 💬 `cypilot generate: update the FEATURE spec for password reset based on the latest DESIGN` *(requires SDLC kit)*
- 💬 `cypilot generate: implement the approved FEATURE for rate limiting in the auth service and preserve required @cpt-* code markers` *(requires SDLC kit)*
- 💬 `cypilot generate: update the codebase to match architecture/FEATURE-login.md, then list which IDs were implemented in code` *(requires SDLC kit)*

### Structured analysis

- 💬 `cypilot analyze: validate architecture/FEATURE-login.md` *(requires SDLC kit)*
- 💬 `cypilot analyze: compare the current implementation against the approved FEATURE for user invite flow` *(requires SDLC kit)*
- 💬 `cypilot analyze: review the current code against the approved FEATURE and report missing traceability markers, validation issues, and likely implementation gaps` *(requires SDLC kit)*

### Planning

- 💬 `cypilot plan: break this monolith-to-service extraction into safe phases with validation points`
- 💬 `cypilot plan: break this FEATURE implementation into artifact-aware coding phases with validation and review checkpoints` *(requires SDLC kit)*

### Context-bounded execution

- 💬 `cypilot generate: implement only phase 2 of the approved migration plan`
- 💬 `cypilot generate: implement only phase 2 of the approved plan, then validate and summarize any remaining errors before continuing`

### Brownfield understanding

- 💬 `cypilot auto-config`
- 💬 `cypilot analyze: explain the current project conventions and likely architecture boundaries`

### Marker recovery

- 💬 `cypilot generate: add the missing @cpt-* markers to the code changed for this FEATURE and keep the implementation behavior unchanged` *(requires SDLC kit)*
- 💬 `cypilot analyze: find code paths that should contain @cpt-* markers for the approved FEATURE but do not` *(requires SDLC kit)*

---

## 10. Prompt patterns that usually go wrong

- 💬 `cypilot generate: build the whole system`
- 💬 `cypilot generate: make this project enterprise grade`
- 💬 `cypilot generate: improve everything`
- 💬 `cypilot analyze: tell me if this code is good`
- 💬 `cypilot generate: rewrite the app based on best practices`
- 💬 `cypilot generate: implement this spec in code, skip validation for now`
- 💬 `cypilot generate: add the feature, markers are not important`

Why these go wrong:

- **scope is undefined**
- **target is undefined**
- **source-of-truth is missing**
- **success criteria are missing**
- **the workflow is under-specified**

Better versions:

- 💬 `cypilot plan: break the auth rewrite into phases constrained to backend API first`
- 💬 `cypilot analyze: validate this DESIGN against the current PRD and list missing sections` *(requires SDLC kit)*
- 💬 `cypilot generate: update only the login FEATURE spec using the approved auth DESIGN` *(requires SDLC kit)*

---

## 11. Workspace federation and orchestration repo pattern

Cyber Pilot can feel heavy in smaller repos because the system includes a meaningful amount of:

- **orchestration logic in scripts**
- **behavioral instructions in Markdown**
- **rules, templates, validation, and routing structure**

That overhead is real.

It is the price paid for stronger control, repeatability, traceability, and validation.

A practical mitigation is **workspace federation**.

### Good pattern

Keep one dedicated **orchestration repository** with the full Cyber Pilot setup, then connect multiple smaller repos through a workspace.

That gives you:

- centralized orchestration weight
- shared rules and kits
- cross-repo traceability
- less duplication of setup across many small repos

### Bad pattern

Clone the full heavy setup into every tiny service repo even when those repos mostly need shared orchestration and occasional validation.

### Typical commands

🖥️ **Terminal**:
```bash
cpt workspace-init
cpt workspace-add --name docs --path ../docs-repo --role artifacts
cpt workspace-add --name services --path ../services-repo --role codebase
cpt workspace-info
```

---

## 12. Brownfield projects

Brownfield projects are often a strong Cypilot use case, but only if you are disciplined.

### Good approach

- start with auto-config
- inspect inferred rules
- identify the real source-of-truth artifacts
- use analysis before generation when the current system is still unclear

### Bad approach

- start implementing immediately in an unfamiliar codebase with no conventions loaded
- assume existing code is internally consistent
- treat inferred architecture as guaranteed truth

### Good sequence

1. 🖥️ `cpt init`
2. 🖥️ `cpt generate-agents`
3. 💬 `cypilot on`
4. 💬 `cypilot auto-config`
5. 💬 `cypilot analyze: summarize current conventions and likely architecture boundaries`
6. 💬 `cypilot plan: break the requested change into safe brownfield phases`

---

## 13. Delegation and autonomous execution

Delegation can be powerful, especially for repetitive generate-validate-fix cycles.

A delegated loop often looks like:

- generate
- validate
- fix
- validate again
- repeat while the loop still seems trustworthy

### Good use

- bounded plan already exists
- validation loop is well understood
- you are monitoring progress
- rollback points exist
- final human review is still planned before acceptance

### Risk

If validation produces a false positive, an autonomous loop can optimize for the wrong signal.

### Mitigation

- prefer delegated flows that preserve granular changes and rollback points
- use RalphEx safeguards where available instead of assuming every guardrail must be manual
- inspect status, outputs, and validation results while the loop is running
- stop or roll back to a known-good point if the loop goes off track
- require human review before treating the delegated result as done

In practice, some of these safeguards may already be provided by RalphEx itself, such as granular commit behavior or clearer rollback points.

The human responsibility is not to manually reproduce every safeguard, but to set boundaries, monitor whether the loop still looks trustworthy, and make the final acceptance decision.

### Example

- 💬 `cypilot delegate this plan to ralphex`

Even after a clean delegated loop, the result is still not automatically guaranteed correct.

A final **human review remains mandatory**.

---

## 14. Quick decision checklist

Use Cypilot if most answers are **yes**:

- **Is there a clear target artifact, code area, or review object?**
- **Is structure important?**
- **Is deterministic validation useful?**
- **Is traceability useful?**
- **Is the task large enough that planning helps?**
- **Would repeatability across tools or contributors help?**

Be cautious if most answers are **yes** here instead:

- **Is the task tiny?**
- **Is the task highly ambiguous?**
- **Is this mostly ideation?**
- **Would a lightweight direct prompt be enough?**
- **Would the workflow overhead exceed the task value?**

---

## Further reading

- **[README](../README.md)**
- **[Configuration guide](CONFIGURATION.md)**
- **[Project extensibility guide](PROJECT-EXTENSIBILITY.md)**
- **[Story-driven walkthrough](STORY.md)**
- **[Workspace specification](../requirements/workspace.md)**
- **[Prompt engineering methodology](../requirements/prompt-engineering.md)**
- **[Prompt bug-finding methodology](../requirements/prompt-bug-finding.md)**
