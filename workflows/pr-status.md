---
cypilot: true
type: workflow
name: cypilot-pr-status
description: Generate status reports for GitHub PRs with severity assessment and resolved-comment audit
version: 1.0
purpose: Fetch latest PR data, generate status reports, assess comment severity, audit resolved comments
---

# PR Status Workflow

ALWAYS open and follow `{cypilot_path}/skills/cypilot/SKILL.md` FIRST WHEN {cypilot_mode} is `off`

**Type**: Analysis
**Role**: Reviewer
**Output**: `.prs/{ID}/status.md`

---

## Routing

| User Intent | Route | Example |
|-------------|-------|---------|
| Check PR status | **pr-status.md** | "PR status 123", `/cypilot-pr-status 123` |
| Check all PR statuses | **pr-status.md** | "status of all PRs", `/cypilot-pr-status ALL` |
| Review a PR | **pr-review.md** | "review PR 123", `/cypilot-pr-review 123` |

---

## Overview

Accepts one argument: a PR number (e.g. `123`) or `ALL`.
Also triggered by natural-language prompts like `cypilot PR status 123`.

**IMPORTANT**: Every status request MUST re-fetch and re-analyze from scratch.
NEVER reuse data or analysis from a previous run in this conversation.
Previous results are stale the moment a new status request arrives.

---

## Paths

- **Script**: `python3 {cypilot_path}/skills/scripts/pr.py`
- **Config**: `{cypilot_path}/config/pr-review.json`
- **Templates**: `{cypilot_path}/.core/templates/pr/`
- **PR data**: `.prs/{ID}/`
- **Exclude list**: `.prs/config.yaml` → `exclude_prs`

## Prerequisite Checklist

- [ ] `gh` CLI installed and authenticated (`gh auth status`)
- [ ] Repository has GitHub remote configured

---

## Steps

## Step 1: List open PRs (when needed)
// turbo
Run: `python3 {cypilot_path}/skills/scripts/pr.py list`
ALWAYS run this step WHEN target is `ALL` or no PR number was specified.
Present the list to the user so they can select a PR or confirm ALL.
This respects the `.prs/config.yaml` exclude list.
**NEVER use `gh pr list` directly — ALWAYS use `pr.py list`.**

## Step 2: Generate status reports (MANDATORY — always re-fetch)
// turbo
Run: `python3 {cypilot_path}/skills/scripts/pr.py status <ARG>`
The `status` command auto-fetches the **latest** PR data from GitHub
before generating each report — no stale data is possible.
This creates `.prs/{ID}/status.md` for each PR.
**ALWAYS run this step, even if the same PR was processed earlier in this conversation.**
Do NOT skip this step. Do NOT reuse previously generated reports.

## Step 3: Assess severity (LLM task)
For each generated status report, read `.prs/{ID}/status.md`.
For every unreplied comment with `Severity: TBD`:
- Read the comment body and its context.
- Assign a severity: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`.
- Edit the `Severity: TBD` line in the status report file to the chosen value.

## Step 4: Audit resolved comments (LLM task)
The status report contains a "Resolved Comments (Audit Required)" section.
Each entry defaults to `- **Status**: ✅ RESOLVED — AI VERIFIED`.
For each resolved comment, apply these checks **in order**:

a. **Check for unanswered concerns**
Count the participants in the thread. If the comment author is
different from the PR author AND the PR author (or another team
member) never replied, the concern was left unanswered.
→ Mark as **SUSPICIOUS**: "Concern by @{author} was resolved
without a reply from the PR author."

b. **Check the code**
Read the original concern. Open the **current version** of the
file at the referenced path/line. Determine whether the concern
was addressed by a code change, a valid explanation in a reply,
or is genuinely not applicable.
- **Addressed by code change**: the diff or current file shows
  the concern was fixed → **VERIFIED**.
- **Addressed by explanation**: the PR author replied with a
  valid technical rationale for not changing the code → **VERIFIED**.
- **Not addressed**: no code change AND no reply (or reply does
  not address the concern) → **SUSPICIOUS**.

c. **Apply verdict**
- If **verified**: leave the status line as-is.
- If **suspicious**: change the status to
  `- **Status**: ⚠️ RESOLVED — SUSPICIOUS`
  and append a warning: `> ⚠️ **SUSPICIOUS**: <reason>`.
  Then move the entire entry to the "Suspicious Resolutions" section.

Update the suspicious counts in the header table accordingly.

## Step 5: Reorder by severity
// turbo
For each PR, run: `python3 {cypilot_path}/skills/scripts/pr.py reorder {ID}`
This re-sorts the unreplied comment sections by severity (CRITICAL first).

## Step 6: Present results
Read the final `.prs/{ID}/status.md` and present a summary to the
user highlighting:
- Total unreplied comments and their severity distribution
- Any CRITICAL or HIGH items that need immediate attention
- CI/merge conflict status
- Any suspicious resolved comments flagged during the audit

---

## Validation Criteria

- [ ] `gh` CLI authenticated and functional
- [ ] PR data fetched successfully (meta.json exists)
- [ ] Status report generated (status.md exists)
- [ ] All `Severity: TBD` entries assessed
- [ ] Resolved comments audited against current code
- [ ] Suspicious resolutions moved to correct section
- [ ] Comments reordered by severity
- [ ] Results presented to user with severity distribution

---

## Next Steps

After completion:

- If the report contains CRITICAL/HIGH items: prioritize addressing those threads first.
- If suspicious resolutions were found: ask the PR author to confirm the resolution with evidence (reply link, code change, or test results).
- Re-run this workflow after new commits or new review comments.
