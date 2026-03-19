---
cypilot: true
type: requirement
name: Compilation Brief Template
version: 2.0
purpose: Template for per-phase compilation briefs — filled by LLM during plan Phase 3.2
---

# Compilation Brief Template


<!-- toc -->

- [Overview](#overview)
- [Template](#template)
- [Load Instructions: How to Fill](#load-instructions-how-to-fill)
- [Example](#example)
- [Fill Rules](#fill-rules)

<!-- /toc -->

## Overview

A compilation brief tells the executing agent what to read, how to use it, and how to compile one phase file. This template is task-agnostic.

## Template

~~~markdown
# Compilation Brief: Phase {number}/{total} — {title}

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
number = {number}
total = {total}
type = "{type}"
title = "{title}"
depends_on = {depends_on}
input_files = {input_files}
output_files = {output_files}
outputs = {outputs}
inputs = {inputs}
```

## Load Instructions
{numbered list of load items}

**Do NOT load**: {irrelevant files}

## Compile Phase File
Write to: `{plan_dir}/{phase_file}`

Required sections:
1. TOML frontmatter
2. Preamble — use the verbatim preamble from `plan-template.md`
3. What
4. Prior Context
5. User Decisions
6. Rules
7. Input
8. Task — add `Read <file>` steps for runtime-read items
9. Acceptance Criteria
10. Output Format — use the required completion report + next-phase prompt from `plan-template.md`

## Context Budget
- Phase file target: ≤ 600 lines
- Inlined content estimate: ~{N} lines
- Total execution context: ≤ 2000 lines
- If Rules exceeds 300 lines, narrow scope — NEVER drop rules

## After Compilation
Report: "Phase {number} compiled → {phase_file} (N lines)"
Then apply context boundary and proceed to the next brief.
~~~

## Load Instructions: How to Fill

Use this item format:

```text
N. **Label**: Read `{path}` (lines {from}-{to}, ~{N} lines)
   - Action: inline or runtime read
   - Scope: what to keep/skip
```

Range rules: use `lines {from}-{to}` for partial reads, omit ranges for whole-file reads, and use `~` when exact ranges are unknown.

| Action | Meaning | Goes into |
|--------|---------|-----------|
| Inline | Copy content into the compiled phase file | Rules, Input, or both |
| Runtime read | Read during phase execution only | Task |

Inline stable structural content such as rules, templates, checklists, examples, and standards.

Runtime-read dynamic or large content such as project files, source code, prior outputs, config, and external docs.

## Example

```text
1. **Rules**: Read `{kit}/artifacts/ADR/rules.md` (lines 30-450, ~420 lines)
   - Inline → Rules section
   - Keep MUST/MUST NOT requirements; skip Prerequisites, Load Dependencies, Tasks, Next Steps
2. **Template**: Read `{kit}/artifacts/ADR/template.md` (lines 10-48, ~38 lines)
   - Inline → Input section
3. **Project context**: Read `workflows/plan.md` (lines 1-80, ~80 lines)
   - Runtime read → add `Read workflows/plan.md` to Task
```

## Fill Rules

1. Include only what the phase needs.
2. Provide line counts via `wc -l` or a reasonable estimate.
3. Generate one brief per phase and apply the context boundary between briefs.
4. Name files `brief-{NN}-{slug}.md`.
5. If inline content exceeds ~500 lines, narrow load scope or move items to runtime reads.
