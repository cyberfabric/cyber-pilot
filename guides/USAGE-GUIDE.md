# Cypilot Usage Guide

How to use **Cypilot** well in common real-world situations: when to use it, when to skip it, and how to choose the right workflow without unnecessary overhead.

> **Convention**: 💬 = paste into AI coding tool chat. 🖥️ = run in terminal.

---

## Table of Contents

- [1. What this guide is for](#1-what-this-guide-is-for)
- [2. The shortest mental model](#2-the-shortest-mental-model)
- [3. When Cypilot is a good fit](#3-when-cypilot-is-a-good-fit)
- [4. When Cypilot is not the best first move](#4-when-cypilot-is-not-the-best-first-move)
- [5. Choosing the right workflow](#5-choosing-the-right-workflow)
- [6. Practical usage habits](#6-practical-usage-habits)
- [7. Common mistakes and anti-patterns](#7-common-mistakes-and-anti-patterns)
- [8. Situation-by-situation guidance](#8-situation-by-situation-guidance)
- [9. Prompt patterns that usually work well](#9-prompt-patterns-that-usually-work-well)
- [10. Prompt patterns that usually go wrong](#10-prompt-patterns-that-usually-go-wrong)
- [11. Using Cyber Pilot across multiple repositories](#11-using-cyber-pilot-across-multiple-repositories)
- [12. Brownfield projects](#12-brownfield-projects)
- [13. Delegation and autonomous execution](#13-delegation-and-autonomous-execution)
- [14. Quick decision checklist](#14-quick-decision-checklist)
- [Further reading](#further-reading)

---

## 1. What this guide is for

This guide is for the practical questions that come up after onboarding:

- **What should I do in this situation?**
- **What should I avoid?**
- **When should I use `plan`, `generate`, or `analyze`?**
- **When is Cypilot useful, and when is it just overhead?**
- **How do I get the benefits without using the product badly?**

Use this guide when you already know what Cypilot is and now need help choosing the right workflow in common real-world situations.

The focus is not abstract theory.

The focus is operational behavior: how to use Cypilot well in real projects.

---

## 2. The shortest mental model

Cypilot is most useful when a task needs more than raw prompting.

Use your AI coding tool and agent for:

- **reasoning**
- **writing**
- **transformation**
- **implementation judgment**

Use Cypilot for:

- **choosing the right workflow**
- **loading the right context**
- **applying rules and templates**
- **running deterministic validation**
- **keeping requirements, design, and code linked through stable identifiers**
- **breaking large tasks into phases**

If the task is tiny or exploratory, direct prompting may be enough.

If the task needs structure, validation, or safe multi-step execution, Cypilot is usually the better fit.

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

- **You want one repeatable workflow across multiple AI coding tools**
  
  Example: the team uses Claude Code, Cursor, Windsurf, GitHub Copilot, or more than one AI coding tool.

- **You need cross-repo coordination**
  
  Example: docs in one repo, code in another, shared kits in a third.

- **You want checklist-based review to be repeatable**
  
  Example: design review, PR review, or status reporting that should follow the same structure across runs.

- **You need a repeatable way to handle multi-step work safely**
  
  Example: multiple engineers or AI coding tools should follow the same planning, validation, and review discipline.

---

## 4. When Cypilot is not the best first move

Cypilot is often not the best first move when:

- **The task is tiny**
  
  Example: a one-file typo fix or a very small local change.

- **You are still doing open-ended discovery**
  
  Example: "let's brainstorm five different product directions."

- **You want maximum first-draft speed with minimum ceremony**
  
  Example: throwaway prototypes, loose ideation, or disposable spikes.

- **You do not yet have enough structure to anchor the work**
  
  Example: no source docs, no clear scope, no acceptance criteria.

- **You do not need validation, traceability, rules, or planning**
  
  Example: a small repo with lightweight expectations and low risk.

- **Your token budget is very tight**
  
  Example: the task is small enough that loading workflow context, rules, and validation logic costs more than it helps.

- **You are exploring many open-ended alternatives**
  
  Example: visual direction finding, branching into speculative options, or broad product brainstorming.

That is not a bug.

It is the tradeoff of using a more structured system.

For these cases, lighter approaches or direct prompting can be a better starting point.

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
- the main job is producing or updating something, not diagnosing uncertainty

**Good prompt shape**:

When a prompt below references `PRD`, `DESIGN`, `DECOMPOSITION`, or `FEATURE`, it assumes the built-in SDLC kit is installed.

- 💬 `cypilot generate: implement the approved FEATURE for login rate limiting` *(requires SDLC kit)*

### Use `analyze` when

- you want to validate something
- you want a review or audit
- you want to compare two artifacts
- you want to inspect gaps, drift, or consistency
- you need to understand what is wrong, unclear, or missing before you change anything

**Good prompt shape**:

- 💬 `cypilot analyze: validate architecture/DESIGN.md against the current FEATURE docs` *(requires SDLC kit)*

### What `analyze` is for in practice

`analyze` is the review and inspection workflow.

In day-to-day use, reach for it when you need one of five things:

- **validation** of structure, references, or traceability
- **review** of prompts, instructions, or code
- **comparison** between documents, artifacts, or versions
- **drift / gap detection** across related sources
- **brownfield understanding** before you plan or generate changes in an unfamiliar codebase

If the main job is understanding what is wrong, inconsistent, missing, or risky, `analyze` is usually the right starting point.

How to choose between them:

- **Need deterministic checks?** Start with validation.
- **Need quality feedback on prompts or code?** Ask for review.
- **Need defect hunting?** Ask explicitly for bug finding.
- **Need cross-document alignment?** Ask for consistency, contradiction, gap, or drift analysis.
- **Need to understand an unfamiliar codebase first?** Start with reverse engineering or brownfield analysis before generation.
- **Need a large review?** Use `plan` first, then execute the analysis in bounded phases.

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

## 6. Practical usage habits

1. **Start from a clear target**
   - Name the artifact, code area, workflow, or outcome.

2. **Prefer structured inputs over vague intent**
   - Give the agent source docs, constraints, and boundaries.

3. **Use `plan` before context gets out of control**
   - Do not wait until the conversation is already overloaded.

4. **Validate early and keep validation in the loop**
   - Generate or implement, validate, review, fix, and validate again before drift accumulates.

5. **Use Cypilot for structure; use the agent for judgment**
   - Let Cypilot enforce structure, validation, routing, and templates. Use the agent for interpretation, tradeoffs, and writing.

6. **Be explicit about what must not change**
   - Say what is in scope and what is out of scope.

7. **Use the smallest workflow that still preserves control**
   - Do not over-apply heavyweight flows to trivial tasks.

8. **Make review repeatable, then make a final human call**
   - Use repeatable checks to improve consistency, but keep final engineering judgment with a human reviewer.

9. **Use a fresh chat for new generation or review work**
   - For substantial `generate` or `analyze` tasks, prefer a new chat. If you stay in the same session, clear context before the next task.

### CI with `cpt` tools

Use the relevant deterministic `cpt` checks locally before opening a PR, and keep the same checks in CI so review is not the first place they run.

For specialized work such as template/example synchronization or kit changes, include the matching focused checks as well.

Use narrower checks while iterating and broader checks before merge. Let humans review meaning and tradeoffs, while CI enforces the deterministic rules every time.

---

## 7. Common mistakes and anti-patterns

1. **Using Cyber Pilot like a generic chat tool**
   - That bypasses the workflows, structure, and validation that make it useful.

2. **Starting with `generate` on a huge ambiguous task**
   - This usually creates drift, missed constraints, and context overload.

3. **Skipping validation until the end**
   - By then the system may already have amplified upstream errors.

4. **Treating deterministic checks or repeated validate-fix loops as proof of correctness**
   - Iteration improves confidence, but it does not replace final human review.

5. **Using it for wide-open brainstorming when structure is not the goal**
   - It works best when you want guided structure, not maximum free-form exploration.

6. **Applying a full structured workflow when a small direct edit would do**
   - Sometimes the process costs more than the task.

7. **Asking for outcomes without naming the governing artifact or source**
   - The agent then guesses instead of transforming from clear input.

8. **Reusing stale context across unrelated generation or review tasks**
   - Old context can leak assumptions into the next task. Start a new chat or clear the context first.

---

## 8. Situation-by-situation guidance

### Situation: new project setup

**Do**:

- 🖥️ `cpt init`
- 🖥️ `cpt generate-agents`
- 💬 `cypilot on`

**Do not**:

- assume the AI coding tool already knows the project structure
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
- name the governing artifact explicitly
- preserve required traceability markers if your workflow uses them
- validate and review after implementation

**Do not**:

- ask for implementation without naming the governing artifact
- let code drift away from the approved artifact set
- ignore known missing required markers before downstream review

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
- 💬 clear the chat context before the next task if you stay in the same session

---

## 9. Prompt patterns that usually work well

Examples that reference `PRD`, `DESIGN`, `DECOMPOSITION`, or `FEATURE` assume the SDLC kit is installed; otherwise substitute your own project artifact types.

### Structured generation

- 💬 `cypilot generate: create a DESIGN from architecture/PRD.md for the billing service`
- 💬 `cypilot generate: implement the approved FEATURE for rate limiting in the auth service and preserve required @cpt-* code markers`

### Structured analysis

- 💬 `cypilot analyze: validate architecture/FEATURE-login.md`
- 💬 `cypilot analyze: review the current code against the approved FEATURE and report missing traceability markers, validation issues, and likely implementation gaps`

### Planning

- 💬 `cypilot plan: break this monolith-to-service extraction into safe phases with validation points`
- 💬 `cypilot plan: break this FEATURE implementation into artifact-aware coding phases with validation and review checkpoints`

### Context-bounded execution

- 💬 `cypilot generate: implement only phase 2 of the approved migration plan`
- 💬 `cypilot generate: implement only phase 2 of the approved plan, then validate and summarize any remaining errors before continuing`

### Brownfield understanding

- 💬 `cypilot auto-config`
- 💬 `cypilot analyze: explain the current project conventions and likely architecture boundaries`

### Marker recovery

- 💬 `cypilot generate: add the missing @cpt-* markers to the code changed for this FEATURE and keep the implementation behavior unchanged`

---

## 10. Prompt patterns that usually go wrong

- 💬 `cypilot generate: build the whole system`
- 💬 `cypilot generate: make this project enterprise grade`
- 💬 `cypilot generate: improve everything`
- 💬 `cypilot analyze: tell me if this code is good`
- 💬 `cypilot generate: rewrite the app based on best practices`
- 💬 `cypilot generate: implement this spec in code and treat the first pass as done without validation`
- 💬 `cypilot generate: add the feature, markers are not important`

Why these go wrong:

- **scope is undefined**
- **target is undefined**
- **source-of-truth is missing**
- **success criteria are missing**
- **the workflow is under-specified**

Better versions:

- Instead of `cypilot generate: build the whole system`: 💬 `cypilot plan: break the auth rewrite into phases constrained to backend API first`
- Instead of `cypilot analyze: tell me if this code is good`: 💬 `cypilot analyze: review this module for correctness, regression risk, and missing tests`
- Instead of `cypilot generate: rewrite the app based on best practices`: 💬 `cypilot analyze: find the three highest-risk design and implementation issues in this module`
- Instead of `cypilot generate: implement this spec in code and treat the first pass as done without validation`: 💬 `cypilot generate: update only the login FEATURE spec using the approved auth DESIGN, then validate the result`

---

## 11. Using Cyber Pilot across multiple repositories

If you work across several small repositories, avoid copying the full Cyber Pilot setup into each one.

A better pattern is to keep one main orchestration repository and connect related repositories through a workspace.

### Good pattern

Keep one dedicated **orchestration repository** with the full Cyber Pilot setup, then connect multiple smaller repos through a workspace.

That gives you:

- one place for orchestration setup
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

Here, "brownfield" means an existing system with partial docs, unclear conventions, or mixed quality.

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

Delegation can be useful, but only when three things are clear:

- the task is bounded
- the validation loop is trustworthy enough to monitor
- a human will still make the final acceptance decision

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

- prefer delegated flows that keep changes granular and preserve rollback points
- inspect status, outputs, and validation results while the loop is running
- if your AI coding tool or execution environment provides safeguards, use them, but do not treat them as a substitute for boundaries, monitoring, and final review
- stop or roll back to a known-good point if the loop goes off track
- require human review before treating the delegated result as done

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
- **Would repeatability across AI coding tools or contributors help?**

Be cautious if most answers are **yes** here instead:

- **Is the task tiny?**
- **Is the task highly ambiguous?**
- **Is this mostly ideation?**
- **Would a lightweight direct prompt be enough?**
- **Would the workflow overhead exceed the task value?**

If the left-hand answers are mostly yes, Cyber Pilot is probably a good fit. If the right-hand answers dominate, use a lighter workflow or your AI coding tool directly.

---

## Further reading

- **[README](../README.md)** — product overview and setup context
- **[Configuration guide](CONFIGURATION.md)** — tune rules, kits, and behavior
- **[Story-driven walkthrough](STORY.md)** — see an end-to-end example
- **[Workspace specification](../requirements/workspace.md)** — use this if you are running Cyber Pilot across multiple repositories
