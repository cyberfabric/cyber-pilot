# Using AI Agent Tools with Cypilot

How to use **Cypilot** with different AI agent hosts, what each tool supports, where the rough edges are, and how to work around them.

> **Convention**: 💬 = paste into AI agent chat. 🖥️ = run in terminal.

---

## Table of Contents

- [1. What Cypilot generates into host tools](#1-what-cypilot-generates-into-host-tools)
- [2. Quick recommendation by tool](#2-quick-recommendation-by-tool)
- [3. Support matrix](#3-support-matrix)
- [4. Shared best practices across all tools](#4-shared-best-practices-across-all-tools)
  - [Model requirements by operation and prompt type](#model-requirements-by-operation-and-prompt-type)
  - [How host limitations affect model choice](#how-host-limitations-affect-model-choice)
- [5. Claude Code](#5-claude-code)
- [6. Cursor](#6-cursor)
- [7. GitHub Copilot](#7-github-copilot)
- [8. OpenAI Codex](#8-openai-codex)
- [9. Windsurf](#9-windsurf)
- [10. Common problems and fixes](#10-common-problems-and-fixes)
- [11. How to think about subagents vs manual chat separation](#11-how-to-think-about-subagents-vs-manual-chat-separation)
- [Further reading](#further-reading)

---

## 1. What Cypilot generates into host tools

Cypilot is not tied to one AI host.

Instead, it projects its workflows and instructions into the host tool you use.

In practice, `cpt generate-agents --agent <tool>` generates some combination of:

- **workflow commands**
  - entry points for `plan`, `generate`, `analyze`, workspace flows, and kit workflows

- **skill outputs**
  - host-tool-visible Cypilot skill entry points that route into the core instructions

- **subagents**
  - isolated task-specific agents with scoped permissions and dedicated prompts, where the host supports them

Claude Code is the **canonical full-fidelity format** for generated subagents.

Other tools receive the best adaptation their host format supports, with **graceful degradation** where a capability has no equivalent.

Typical setup:

🖥️ **Terminal**:
```bash
cpt generate-agents --agent claude
cpt generate-agents --agent cursor
cpt generate-agents --agent copilot
cpt generate-agents --agent openai
cpt generate-agents --agent windsurf
```

Subagents are not equally supported across all tools.

That is one of the most important practical differences when using Cypilot.

---

## 2. Quick recommendation by tool

- **Claude Code**
  - Best overall fit when you want the fullest Cypilot experience, especially for **generation**, strong subagent support, read-only review isolation, model selection, and worktree isolation.

- **Cursor**
  - Good general-purpose IDE host for Cypilot. Supports subagents, and its **multi-model** nature is a real advantage because you can pair Anthropic for generation with GPT-style models for review. The isolation model is still weaker than Claude Code.

- **GitHub Copilot**
  - Usable with Cypilot and supports subagents. It is especially attractive when you want **strong review behavior** with GPT-style models, though host-level control is less expressive than Claude Code.

- **OpenAI Codex**
  - Strong option for **review**, bounded analysis, and artifact-heavy work when you want GPT-style strictness and carefulness. Works best when tasks stay narrow and validation is explicit.

- **Windsurf**
  - Still usable with Cypilot workflows and skills, and its **multi-model** nature is a practical plus. But it does **not** support subagents, so treat it as a single-agent host and manually separate contexts.

---

## 3. Support matrix

| Capability | Claude Code | Cursor | GitHub Copilot | OpenAI Codex | Windsurf |
|---|:---:|:---:|:---:|:---:|:---:|
| Workflow / skill integration | Yes | Yes | Yes | Yes | Yes |
| Host-native subagents | Yes | Yes | Yes | Yes | No |
| Read-only review enforcement | Strong | Strong | Partial | Weaker / prompt-led | No host-native subagent enforcement |
| Worktree isolation | Yes | No | No | No | No |
| Model selection in generated subagents | Yes | Yes | No equivalent | Tool-dependent / less central | N/A |
| Subagent-scoped hooks | Yes | No | Tool-specific / narrower current surface | No | No |
| Multi-model host advantage | No | Yes | Yes | No | Yes |
| Best use mode with Cypilot | Full orchestration | Strong daily-driver | Structured assistance | Bounded execution | Manual separation |

**Important distinction**:

- if a host does **not** support subagents, that is a **host limitation**, not a Cypilot limitation
- Cypilot still gives you workflows, skill routing, validation, traceability, and planning

---

## 4. Shared best practices across all tools

1. **Regenerate integrations after setup changes**
   - If you changed workflows, skills, kits, or agent config, rerun `cpt generate-agents --agent <tool>`.

2. **Use `plan` before large work**
   - Do not push a large ambiguous request straight into `generate`.

3. **Separate generation from review**
   - If the host supports subagents, use them.
   - If it does not, use separate chats.

4. **Use a fresh chat for a new task**
   - Especially for generation and review.
   - If you stay in the same session, clear the context first.
   - In tools such as Claude Code or Codex-style shells, `💬 /clear` is the practical reset.

5. **Validate after generation**
   - A successful generation step is not the end.
   - Run validation, review, fix, and validate again.

6. **Keep tasks bounded**
   - Narrow requests are easier for every host tool to execute safely and correctly.

7. **Require human review at the end**
   - Host tooling, subagents, validation, and AI review raise confidence.
   - They do not replace final human judgment.

### Model requirements by operation and prompt type

Use these tiers as the practical default:

- **fast-tier model**
  - good for high-volume, lower-complexity work where speed matters more than deep reasoning

- **default / inherit model**
  - use the user's current session model; this should usually be the default choice

- **strong reasoning model required**
  - use your best available model tier for tasks with ambiguity, architecture judgment, long dependencies, or expensive mistakes

The current subagent defaults already follow this rule of thumb:

- prefer **`inherit`** unless a cheaper or faster tier is clearly enough
- use **`fast`** only for high-volume, lower-complexity tasks such as structured PR review

### Practical model-family guidance

In current practical use with Cypilot, the model-family tendency is usually:

- **GPT-thinking models**
  - usually better for **review**, especially when you want stricter, more careful, more exact analysis
  - often better for **artifact generation** too, though usually not by a dramatic margin; the main difference is that they tend to make **fewer mistakes**

- **Claude / Anthropic models**
  - usually better for **generation**, especially **code generation**
  - often faster and stronger when turning an approved spec into implementation
  - usually somewhat weaker than GPT-style models for artifact-heavy work, though the gap is not huge

This is a practical default, not a hard law.

The right choice still depends on the host, the task shape, and the exact model version available in your setup.

| Operation or prompt type | Recommended model tier | When fast-tier is acceptable | Notes |
|---|---|---|---|
| `show config`, `where-defined`, `list-ids`, simple lookup, shallow repo navigation | fast-tier or default / inherit | usually yes | Mostly bounded retrieval and formatting work. |
| Small formatting fixes, marker recovery, narrow edits with explicit target | fast-tier or default / inherit | yes, if scope is tight | Still validate after the change. |
| Structured PR review first pass | fast-tier by default, ideally GPT-style review model | yes | This matches the current `cypilot-pr-review` default. Escalate if review becomes architectural or cross-artifact. |
| Deterministic validation triage and checklist scanning | fast-tier or default / inherit | often yes | Good for first-pass issue grouping, but escalate when interpretation becomes non-trivial. |
| `plan` for large, risky, or multi-phase work | strong reasoning model required | usually no | Decomposition quality matters; weak planning creates downstream drift. |
| Artifact generation or transformation such as `PRD -> DESIGN -> DECOMPOSITION -> FEATURE` | strong reasoning model required, often GPT-style model preferred | only for tiny bounded rewrites | These tasks mix structure, interpretation, and consistency pressure. GPT-style models often make slightly fewer artifact-level mistakes. |
| Brownfield understanding, reverse engineering, architecture review, migration planning | strong reasoning model required | usually no | High ambiguity and hidden dependencies make weaker tiers risky. |
| Code generation from an approved FEATURE or DESIGN | default / inherit, often Claude / Anthropic preferred in practice | only for small well-specified local changes | For anything non-trivial, prefer the best code-generation model available in the session. Claude-style models are often the stronger default here. |
| Phase compilation, phase execution planning, RalphEx orchestration handoff | default / inherit or strong reasoning | rarely | These are coordination-heavy tasks; mistakes compound across steps. |
| Final acceptance decision | human review required | no | No model tier replaces final human judgment. |

### How host limitations affect model choice

- **Claude Code**
  - best fit when you want the host integration to carry explicit model hints together with isolation and tool scoping

- **Cursor**
  - supports generated model selection and is useful as a **multi-model host**; a common practical split is Anthropic for generation and GPT-style models for review. It still lacks Claude-style worktree isolation.

- **GitHub Copilot**
  - generated agent files do not have the same direct model-selection surface, so choose the right model in the host environment or session before invoking Cypilot workflows. Its multi-model nature is useful when you want stronger review behavior from GPT-style models.

- **OpenAI Codex**
  - treat model choice as mostly session-level and prompt-level rather than strongly host-enforced metadata; use stronger GPT-style models for planning, review, architecture, and brownfield work

- **Windsurf**
  - because there are no subagents, model choice is entirely manual per chat; its multi-model nature is still useful because you can choose one model family for generation and another for review

---

## 5. Claude Code

### Why it fits Cypilot well

Claude Code is the strongest fit for the full Cypilot model.

It is the highest-fidelity host for:

- **subagent definitions**
- **scoped tools**
- **read-only review setup**
- **model selection**
- **worktree isolation**
- **subagent-level hooks**

This makes it the closest match to how Cypilot wants generation and review to be separated.

### Best use cases

- **fully specified code generation**
- **isolated PR review**
- **phase compilation and phase execution**
- **complex multi-step work where context hygiene matters**

### Typical problems

- **You mix generation and review in one long parent chat**
  - Even with subagents available, the parent session can still accumulate stale context.

- **You expect codegen edits to behave like direct inline edits**
  - Claude Code is the one host where worktree isolation is available, so isolation behavior can differ from your expectations.

- **You forget to regenerate integrations after config changes**
  - Then the host may still be using old workflow or subagent definitions.

### How to mitigate

- use a fresh parent chat for a new major task
- prefer subagents for codegen and review instead of doing everything in one session
- rerun `cpt generate-agents --agent claude` after integration-relevant changes
- still validate and review after codegen

### Practical recommendation

If you want the most complete Cypilot host today, use **Claude Code**.

It is also the strongest default when the main task is **code generation**.

---

## 6. Cursor

### What works well

Cursor supports Cypilot subagents and is a strong day-to-day host for normal coding workflows.

It supports:

- **subagent definitions**
- **read-only review flag**
- **model selection in generated definitions**

### Where it is weaker than Claude Code

Cursor does **not** give you the same worktree-isolated model as Claude Code.

That means the overall separation is still useful, but not as strong as the Claude Code path.

### Typical problems

- **You assume Cursor subagents give the same isolation guarantees as Claude Code**
- **You let one large task sprawl instead of using phased execution**
- **You use subagents, but still keep too much stale context in the parent chat**

### How to mitigate

- keep tasks narrower
- prefer `plan` for large work
- validate after each meaningful implementation step
- start a new chat before review work
- treat Cursor as strong, but not “full Claude-equivalent isolation”

### Practical recommendation

Use **Cursor** when you want solid Cypilot support inside an interactive IDE workflow and do not strictly depend on Claude-style worktree isolation.

It becomes especially attractive when you want one host where:

- **Anthropic models** can handle generation
- **GPT-style models** can handle review

---

## 7. GitHub Copilot

### What works well

GitHub Copilot supports generated Cypilot subagents and can participate in structured generation and review flows.

It is useful for:

- **structured implementation tasks**
- **read-oriented review flows**
- **teams already standardized on Copilot**

### Main limitation

Copilot's generated agent surface is less expressive than Claude Code.

The result is still useful, but some control that Claude can express more directly is thinner here.

### Typical problems

- **You expect Copilot subagents to enforce as much as Claude Code does**
- **You rely too much on the host tool and not enough on Cypilot validation**
- **You have existing GitHub-side instruction files and assume Cypilot will overwrite everything**

### How to mitigate

- keep the tasks explicit and bounded
- lean more on Cypilot workflows and deterministic validation
- inspect generated `.github/agents/` outputs when debugging setup issues
- do not treat host integration as the source of truth; treat Cypilot workflows and validation as the source of truth

### Practical recommendation

Use **GitHub Copilot** when it is already your team standard, but compensate for weaker host-level expressiveness with tighter prompts and stronger validation discipline.

It is especially reasonable when your review culture benefits from **GPT-style thinking models**.

---

## 8. OpenAI Codex

### What works well

OpenAI Codex can be used with Cypilot and supports generated agent definitions.

It works best for:

- **bounded execution tasks**
- **well-specified implementation work**
- **clear, explicit, low-ambiguity instructions**

### Main limitation

Compared with Claude Code, more of the intended behavior is carried by the prompt and workflow instructions rather than by rich host-native enforcement.

That means you should expect less safety from the host layer itself.

### Typical problems

- **You give Codex an oversized or ambiguous task and expect the host to keep it on rails**
- **You reuse a polluted session for review after generation**
- **You treat one clean run as sufficient evidence of correctness**

### How to mitigate

- keep tasks tightly scoped
- use `plan` before big execution
- validate after each phase
- use a new chat for a new task
- in Codex-style shells, use `💬 /clear` before switching task type if you remain in the same session

### Practical recommendation

Use **OpenAI Codex** when the task is explicit and bounded.

Do not rely on the host alone to provide the same isolation guarantees you would expect from Claude Code.

It is particularly strong for:

- **review**
- **strict analysis**
- **artifact-heavy work**

---

## 9. Windsurf

### The key limitation

Windsurf does **not** support subagents.

This is the most important thing to understand before using Cypilot there.

Cypilot still works through:

- **workflow integrations**
- **skill outputs**
- **workflow routing**
- **validation and traceability**

But Windsurf does **not** give you host-native isolated child agents for codegen and review.

### What this changes in practice

In Windsurf, you should manually do what subagents would otherwise help with automatically:

- use one chat for **planning**
- use another chat for **generation**
- use another chat for **review**
- keep validation separate and explicit

### Typical problems

- **You expect `cypilot-codegen` or `cypilot-pr-review` to exist as host-native subagents**
- **You run generation and review in the same long session**
- **You let generation context contaminate review quality**
- **You expect least-privilege separation that the host cannot enforce**

### How to mitigate

- use fresh chats aggressively
- keep one role per chat
- use `plan` for larger work so each phase stays bounded
- run validation and review explicitly after generation
- accept that Windsurf is a **single-agent host** from Cypilot's point of view

### Practical recommendation

Use **Windsurf** with Cypilot when you want the workflow and skill layer, but do not expect host-native subagent orchestration.

Think of Windsurf as **manual context orchestration** rather than **subagent orchestration**.

Its main practical upside is that it can still be valuable as a **multi-model host**, even without subagents.

---

## 10. Common problems and fixes

### Problem: subagents are not available where you expected them

**Likely causes**:

- the host does not support subagents
- integrations were not regenerated
- you assumed host parity that does not exist

**Fix**:

- rerun `🖥️ cpt generate-agents --agent <tool>`
- check whether that host actually supports subagents
- if not, switch to manual chat separation

### Problem: review quality is poor after a long generation session

**Likely cause**:

- stale generation context polluted the review context

**Fix**:

- use a separate review subagent where supported
- otherwise start a new chat
- in Claude Code or Codex-style sessions, use `💬 /clear` before the review task if you stay in the same shell

### Problem: the host appears to support read-only review, but you still do not trust it fully

**Likely cause**:

- host-level control is not equally strong across tools

**Fix**:

- treat host permissions as helpful, not as your only safety mechanism
- rely on Cypilot validation, review workflow, and final human review

### Problem: one giant task keeps going off the rails

**Likely cause**:

- the task should have gone through `plan` first

**Fix**:

- use `💬 /cypilot-plan`
- execute phase by phase
- validate after each meaningful step

### Problem: Windsurf feels worse than tools with subagents

**Likely cause**:

- Windsurf lacks the host-native isolation layer

**Fix**:

- split work by chat manually
- separate generation from review
- keep tasks smaller and more explicit

One practical workaround is to use Cypilot to generate the **next-chat prompt** for you.

Example:

- in the current chat:
  - 💬 `cypilot analyze: generate a bounded prompt for a fresh Windsurf chat that should implement only phase 2 of the approved plan, list the exact files to inspect first, preserve @cpt-* markers, and end by running validation and summarizing any remaining issues`
  - 💬 `cypilot analyze: generate a bounded prompt for a fresh Windsurf chat that should review the code changed for phase 2 against the approved FEATURE and DESIGN, check for missing @cpt-* markers, and return a structured list of issues by severity`

- then open a **new Windsurf chat** and paste the generated prompt there

This partially simulates what a dedicated codegen or review subagent would have given you:

- a cleaner context boundary
- a bounded task
- explicit files and constraints
- a stronger separation between orchestration and execution

---

## 11. How to think about subagents vs manual chat separation

### If the host supports subagents

Prefer:

- **parent chat for orchestration**
- **subagent for generation**
- **subagent for review**
- **fresh parent chat when switching to a new major task**

This gives you:

- cleaner context boundaries
- better least-privilege separation
- more stable long-running workflows

### If the host does not support subagents

Manually simulate the same separation:

- **one chat for planning**
- **one chat for generation**
- **one chat for review**
- **explicit validation between them**

This is especially important in **Windsurf**.

### Core rule

Whether the host supports subagents or not, the operating model should still be:

- **plan or generate**
- **validate**
- **review**
- **fix**
- **validate again**
- **human review before acceptance**

---

## Further reading

- **[README](../README.md)**
- **[Usage guide](USAGE-GUIDE.md)**
- **[Configuration guide](CONFIGURATION.md)**
- **[ADR-0016: Subagent registration](../architecture/ADR/0016-cpt-cypilot-adr-ai-cli-extensibility-subagents-v1.md)**
- **[Workspace specification](../requirements/workspace.md)**
