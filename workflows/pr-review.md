---
cypilot: true
type: workflow
name: cypilot-pr-review
description: Review GitHub PRs using LLM-powered analysis with configurable prompts and checklists
version: 1.0
purpose: Read-only PR review — fetch diffs/metadata from GitHub, analyze against checklists, produce structured review reports
---

# PR Review Workflow

ALWAYS open and follow `{cypilot_path}/skills/cypilot/SKILL.md` FIRST WHEN {cypilot_mode} is `off`

**Type**: Analysis
**Role**: Reviewer
**Output**: `.prs/{ID}/review.md`

---

## Routing

| User Intent | Route | Example |
|-------------|-------|---------|
| Review a specific PR | **pr-review.md** | "review PR 123", `/cypilot-pr-review 123` |
| Review all open PRs | **pr-review.md** | "review all PRs", `/cypilot-pr-review ALL` |
| Check PR status | **pr-status.md** | "PR status 123", `/cypilot-pr-status ALL` |

---

## Overview

Accepts one argument: a PR number (e.g. `123`) or `ALL`.
Also triggered by natural-language prompts like `cypilot review PR 123`,
`review PR #59`, or `cypilot review PR https://github.com/org/repo/pull/123`.

All review is **read-only** — the LLM reads the downloaded diff file and
the current repo source without modifying the local working tree.

**IMPORTANT**: Every review request MUST re-fetch and re-analyze from scratch.
NEVER reuse data or analysis from a previous run in this conversation.
Previous results are stale the moment a new review request arrives.

---

## Paths

- **Script**: `python3 {cypilot_path}/skills/scripts/pr.py`
- **Config**: `{cypilot_path}/config/pr-review.json`
- **Templates**: `{cypilot_path}/.core/templates/pr/`
- **Checklists**: `docs/checklists/` (PRD.md, DESIGN.md, ADR.md, etc.)
- **Prompts**: `{cypilot_path}/.core/prompts/pr/`
- **PR data**: `.prs/{ID}/`
- **Exclude list**: `.prs/config.yaml` → `exclude_prs`

## Prerequisite Checklist

- [ ] `gh` CLI installed and authenticated (`gh auth status`)
- [ ] Repository has GitHub remote configured
- [ ] `{cypilot_path}/config/pr-review.json` has `prompts` configured

---

## Steps

## Step 1: List open PRs (when needed)
// turbo
Run: `python3 {cypilot_path}/skills/scripts/pr.py list`
ALWAYS run this step WHEN target is `ALL` or no PR number was specified.
Present the list to the user so they can select a PR or confirm ALL.
This respects the `.prs/config.yaml` exclude list.
**NEVER use `gh pr list` directly — ALWAYS use `pr.py list`.**

## Step 2: Fetch PR data (MANDATORY — always re-fetch)
// turbo
Run: `python3 {cypilot_path}/skills/scripts/pr.py fetch <ARG>`
This downloads the **latest** PR metadata, diff, and comments from
GitHub into `.prs/{ID}/`. Fetch never uses cached data — it always
overwrites any previously fetched files.
**ALWAYS run this step, even if the same PR was fetched earlier in this conversation.**
Do NOT skip this step. Do NOT reuse previously fetched data.

## Step 3: Select review prompt and checklist
Read `{cypilot_path}/config/pr-review.json` → `prompts` list. For each prompt
entry, read the `description` field. Based on the PR title, body (in
`meta.json`), and the files changed (in `diff.patch`), select the most
appropriate review prompt. If unsure, default to "Code Review".
Load the corresponding `promptFile` and `checklist` from the matched entry.
**Resolve `{placeholder}` variables** in the prompt using the fields from
the matched entry (e.g. `{project_domain}`, `{checklist}`, `{template}`,
`{existing_artifacts}`, `{architecture}`, `{coding_guidelines}`,
`{security_guidelines}`, etc.). Each prompt entry in `pr-review.json`
provides the project-specific paths that the submodule prompts de-reference.
Use the checklist criteria to guide the review depth and structure.

## Step 4: Review each PR (read-only)
For each PR (if ALL, iterate; otherwise single):

a. **Understand scope of changes**
Parse `.prs/{ID}/diff.patch` headers to get a list of affected files
and lines added/removed per file. Use this to **focus the review on
the files and areas actually changed by the PR**.

b. **Analyze existing PR feedback**
Read `.prs/{ID}/review_threads.json` and the `comments` array in
`.prs/{ID}/meta.json`. For each reviewer comment or thread:
- Note the concern raised and whether it is resolved or open.
- Assess relevance: does the concern point to a real issue in the
  code, or is it a style nit / false positive?
- Track which concerns were addressed (resolved threads with matching
  code changes) and which were dismissed without action.
Use this analysis to inform the final verdict — if reviewers raised
valid unresolved concerns, those should lower the confidence to
approve. If all concerns are addressed, that supports approval.

c. **Review the changes (read-only)**
Read `.prs/{ID}/diff.patch` to understand what changed.
For each affected file, open the **current version in the repo** and
review it in context of the diff. This is the standard agentic IDE
flow — no local modifications are made.
Prioritise files with the largest delta first. Produce a thorough
review covering the areas specified in the prompt and checklist.

d. **Write review output**
Read the template at `{cypilot_path}/.core/templates/pr/code-review.md` and
use it to structure the review. Save the review to
`.prs/{ID}/review.md`.
The review must follow the template format, including the mandatory
**"Reviewer Comment Analysis"** section. The final verdict must
factor in unresolved valid concerns from reviewers.

## Step 5: Present results
Summarize the review findings to the user, including:
- Own findings from the code review.
- Reviewer comment analysis: which concerns are valid, addressed, or
  still open.
- Final verdict factoring in both own findings and reviewer feedback.
If ALL, provide a brief summary per PR and note which PRs need the
most attention.

---

## Validation Criteria

- [ ] `gh` CLI authenticated and functional
- [ ] PR data fetched successfully (meta.json, diff.patch exist)
- [ ] Review prompt selected and loaded
- [ ] Checklist loaded for selected review type
- [ ] Diff parsed and scope of changes understood
- [ ] Existing reviewer feedback analyzed
- [ ] Review covers all areas from prompt and checklist
- [ ] Review output follows template format
- [ ] Reviewer Comment Analysis section is present and complete
- [ ] Review saved to `.prs/{ID}/review.md`
- [ ] Results presented to user

---

## Next Steps

After completion:

- If the PR needs changes: share the key issues and suggested fixes.
- If the PR is good to merge: confirm that CI is green and no unresolved critical concerns remain.
- Re-run this workflow after new commits or new review comments.
