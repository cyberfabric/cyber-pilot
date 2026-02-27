# PR Review & Status Blueprint

`@cpt:blueprint`
```toml
kit = "cypilot-sdlc"
```
`@/cpt:blueprint`

---

## Skill

`@cpt:skill`
`````markdown
## PR Review & Status (Shortcut Routing)

ALWAYS re-fetch and re-analyze from scratch WHEN a PR review or status request is detected — even if the same PR was reviewed earlier in this conversation. Previous results are stale the moment a new request arrives. NEVER skip fetch or reuse earlier analysis.

ALWAYS run `python3 {cypilot_path}/.gen/kits/sdlc/scripts/pr.py list` WHEN user intent matches PR list patterns:
- `list PRs`, `list open PRs`, `cypilot list PRs`
- `show PRs`, `show open PRs`, `what PRs are open`
- Any request to enumerate or browse open pull requests

AVOID use `gh pr list` directly — ALWAYS use `pr.py list` for listing PRs.

ALWAYS route to the `cypilot-pr-review` workflow WHEN user intent matches PR review patterns:
- `review PR {number}`, `review PR #{number}`, `review PR https://...`
- `cypilot review PR {number}`, `PR review {number}`
- `code review PR {number}`, `check PR {number}`

ALWAYS route to the `cypilot-pr-status` workflow WHEN user intent matches PR status patterns:
- `PR status {number}`, `cypilot PR status {number}`
- `status of PR {number}`, `check PR status {number}`

### PR List (Quick Command)

When routed to list PRs:
1. Run `python3 {cypilot_path}/.gen/kits/sdlc/scripts/pr.py list`
2. Present the output to the user (respects `.prs/config.yaml` exclude list)
3. No Protocol Guard or workflow loading required — this is a quick command

### PR Review Workflow

When routed to PR review:
1. **ALWAYS fetch fresh data first** — run `pr.py fetch` even if data exists from a prior run
2. Read `{cypilot_path}/.gen/kits/sdlc/workflows/pr-review.md` and follow its steps
3. Use `python3 {cypilot_path}/.gen/kits/sdlc/scripts/pr.py` as the script
4. When target is `ALL` or no PR number given, run `pr.py list` first to show available PRs
5. Select prompt and checklist from `{cypilot_path}/config/pr-review.json` → `prompts`
6. Load prompt from `promptFile` and checklist from `checklist` in matched entry
7. Use templates from `{cypilot_path}/.gen/kits/sdlc/artifacts/PR-CODE-REVIEW-TEMPLATE/template.md` and `{cypilot_path}/.gen/kits/sdlc/artifacts/PR-STATUS-REPORT-TEMPLATE/template.md`

### PR Status Workflow

When routed to PR status:
1. **ALWAYS fetch fresh data first** — `pr.py status` auto-fetches, but never assume prior data is current
2. Read `{cypilot_path}/.gen/kits/sdlc/workflows/pr-status.md` and follow its steps
3. Use `python3 {cypilot_path}/.gen/kits/sdlc/scripts/pr.py` as the script
4. When target is `ALL` or no PR number given, run `pr.py list` first to show available PRs
`````
`@/cpt:skill`

---

## Workflows

### PR Review

`@cpt:workflow`
```toml
name = "pr-review"
description = "Review GitHub PRs using LLM-powered analysis with configurable prompts and checklists"
version = "1.0"
purpose = "Read-only PR review — fetch diffs/metadata from GitHub, analyze against checklists, produce structured review reports"
```
`````markdown
# PR Review Workflow

ALWAYS open and follow `{cypilot_path}/.core/skills/cypilot/SKILL.md` FIRST WHEN {cypilot_mode} is `off`

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

- **Script**: `python3 {cypilot_path}/.gen/kits/sdlc/scripts/pr.py`
- **Config**: `{cypilot_path}/config/pr-review.json`
- **Code review template**: `{cypilot_path}/.gen/kits/sdlc/artifacts/PR-CODE-REVIEW-TEMPLATE/template.md`
- **Status report template**: `{cypilot_path}/.gen/kits/sdlc/artifacts/PR-STATUS-REPORT-TEMPLATE/template.md`
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
Run: `python3 {cypilot_path}/.gen/kits/sdlc/scripts/pr.py list`
ALWAYS run this step WHEN target is `ALL` or no PR number was specified.
Present the list to the user so they can select a PR or confirm ALL.
This respects the `.prs/config.yaml` exclude list.
**NEVER use `gh pr list` directly — ALWAYS use `pr.py list`.**

## Step 2: Fetch PR data (MANDATORY — always re-fetch)
// turbo
Run: `python3 {cypilot_path}/.gen/kits/sdlc/scripts/pr.py fetch <ARG>`
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
Read the template at `{cypilot_path}/.gen/kits/sdlc/artifacts/PR-CODE-REVIEW-TEMPLATE/template.md` and
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
`````
`@/cpt:workflow`

---

### PR Status

`@cpt:workflow`
```toml
name = "pr-status"
description = "Generate status reports for GitHub PRs with severity assessment and resolved-comment audit"
version = "1.0"
purpose = "Fetch latest PR data, generate status reports, assess comment severity, audit resolved comments"
```
`````markdown
# PR Status Workflow

ALWAYS open and follow `{cypilot_path}/.core/skills/cypilot/SKILL.md` FIRST WHEN {cypilot_mode} is `off`

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

- **Script**: `python3 {cypilot_path}/.gen/kits/sdlc/scripts/pr.py`
- **Config**: `{cypilot_path}/config/pr-review.json`
- **Status report template**: `{cypilot_path}/.gen/kits/sdlc/artifacts/PR-STATUS-REPORT-TEMPLATE/template.md`
- **PR data**: `.prs/{ID}/`
- **Exclude list**: `.prs/config.yaml` → `exclude_prs`

## Prerequisite Checklist

- [ ] `gh` CLI installed and authenticated (`gh auth status`)
- [ ] Repository has GitHub remote configured

---

## Steps

## Step 1: List open PRs (when needed)
// turbo
Run: `python3 {cypilot_path}/.gen/kits/sdlc/scripts/pr.py list`
ALWAYS run this step WHEN target is `ALL` or no PR number was specified.
Present the list to the user so they can select a PR or confirm ALL.
This respects the `.prs/config.yaml` exclude list.
**NEVER use `gh pr list` directly — ALWAYS use `pr.py list`.**

## Step 2: Generate status reports (MANDATORY — always re-fetch)
// turbo
Run: `python3 {cypilot_path}/.gen/kits/sdlc/scripts/pr.py status <ARG>`
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
For each PR, run: `python3 {cypilot_path}/.gen/kits/sdlc/scripts/pr.py reorder {ID}`
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
`````
`@/cpt:workflow`
