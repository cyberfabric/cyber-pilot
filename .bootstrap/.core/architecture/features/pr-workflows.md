# Feature: PR Workflows


<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1. Overview](#1-overview)
  - [2. Purpose](#2-purpose)
  - [3. Actors](#3-actors)
  - [4. References](#4-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [PR Review](#pr-review)
  - [PR Status](#pr-status)
- [3. Processes / Business Logic (CDSL)](#3-processes-business-logic-cdsl)
  - [Fetch PR Data](#fetch-pr-data)
  - [Analyze PR Changes](#analyze-pr-changes)
  - [Classify Unreplied Comments](#classify-unreplied-comments)
- [4. States (CDSL)](#4-states-cdsl)
  - [PR Review State](#pr-review-state)
- [5. Definitions of Done](#5-definitions-of-done)
  - [PR Review Workflow](#pr-review-workflow)
  - [PR Status Workflow](#pr-status-workflow)
- [6. Implementation Modules](#6-implementation-modules)
- [7. Acceptance Criteria](#7-acceptance-criteria)

<!-- /toc -->

- [ ] `p1` - **ID**: `cpt-cypilot-featstatus-pr-workflows`

## 1. Feature Context

- [ ] `p1` - `cpt-cypilot-feature-pr-workflows`

### 1. Overview

Structured GitHub PR review and status assessment via `gh` CLI with configurable prompts and checklists. PR workflows are agent-driven — the AI agent fetches PR data, analyzes changes against review criteria, and produces structured reports. All operations are read-only (no local working tree modifications) and always re-fetch data from scratch.

### 2. Purpose

Provides consistent, structured PR reviews that follow project-specific criteria rather than ad-hoc analysis. Enables severity-based triage of unreplied comments and detection of suspicious resolved comments. Addresses PRD requirements for PR review (`cpt-cypilot-fr-sdlc-pr-review`) and PR status (`cpt-cypilot-fr-sdlc-pr-status`).

### 3. Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Requests PR review or status check |
| `cpt-cypilot-actor-ai-agent` | Fetches PR data, analyzes changes, produces reports |

### 4. References

- **PRD**: [PRD.md](../PRD.md) — `cpt-cypilot-fr-sdlc-pr-review`, `cpt-cypilot-fr-sdlc-pr-status`
- **Design**: [DESIGN.md](../DESIGN.md) — `cpt-cypilot-seq-pr-review`
- **Dependencies**: `cpt-cypilot-feature-sdlc-kit`, `cpt-cypilot-feature-agent-integration`

## 2. Actor Flows (CDSL)

### PR Review

- [ ] `p1` - **ID**: `cpt-cypilot-flow-pr-workflows-review`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User requests PR review → agent fetches latest data, analyzes against checklist, writes structured review report
- User requests review of all open PRs → agent iterates over each open PR

**Error Scenarios**:
- `gh` CLI not authenticated → error with `gh auth login` instructions
- PR not found → error with PR number and repo
- Network failure → error with retry instructions

**Steps**:
1. - `p1` - User requests PR review (e.g., "review PR 123") - `inst-user-review`
2. - `p1` - Agent fetches latest PR data: diff, metadata, comments via `gh` CLI - `inst-fetch-data`
3. - `p1` - Agent selects review prompt and checklist based on PR content - `inst-select-prompt`
4. - `p1` - Agent analyzes changes against checklist criteria - `inst-analyze-changes`
5. - `p1` - Agent analyzes existing reviewer comments for validity and resolution status - `inst-analyze-comments`
6. - `p1` - Agent writes structured review report to `.prs/{ID}/review.md` - `inst-write-report`
7. - `p1` - Agent presents summary with findings and verdict - `inst-present-summary`

### PR Status

- [ ] `p1` - **ID**: `cpt-cypilot-flow-pr-workflows-status`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User requests PR status → agent fetches data, classifies unreplied comments by severity, audits resolved comments, outputs report

**Error Scenarios**:
- Same as PR Review error scenarios

**Steps**:
1. - `p1` - User requests PR status (e.g., "PR status 123") - `inst-user-status`
2. - `p1` - Agent fetches latest PR data and comment threads via `gh` CLI - `inst-fetch-status-data`
3. - `p1` - Agent classifies unreplied comments by severity (CRITICAL/HIGH/MEDIUM/LOW) - `inst-classify-comments`
4. - `p1` - Agent audits resolved comments: checks code for actual fixes, detects suspicious resolutions - `inst-audit-resolved`
5. - `p1` - Agent checks CI status and merge conflict state - `inst-check-ci`
6. - `p1` - Agent reorders report by severity and presents summary - `inst-present-status`

## 3. Processes / Business Logic (CDSL)

### Fetch PR Data

- [ ] `p1` - **ID**: `cpt-cypilot-algo-pr-workflows-fetch-data`

1. - `p1` - Invoke `gh pr view <number> --json ...` to fetch metadata - `inst-fetch-metadata`
2. - `p1` - Invoke `gh pr diff <number>` to fetch diff - `inst-fetch-diff`
3. - `p1` - Invoke `gh pr view <number> --json comments,reviews` to fetch comments - `inst-fetch-comments`
4. - `p1` - **IF** any `gh` call fails **RETURN** error with actionable message - `inst-if-gh-fails`

### Analyze PR Changes

- [ ] `p1` - **ID**: `cpt-cypilot-algo-pr-workflows-analyze-changes`

1. - `p1` - Load review prompt from kit config (`{cypilot_path}/config/kits/sdlc/`) - `inst-load-prompt`
2. - `p1` - Load checklist from kit config - `inst-load-checklist`
3. - `p1` - Evaluate each checklist item against PR diff - `inst-evaluate-checklist`
4. - `p1` - Produce structured findings with file paths and line numbers - `inst-produce-findings`

### Classify Unreplied Comments

- [ ] `p1` - **ID**: `cpt-cypilot-algo-pr-workflows-classify-comments`

1. - `p1` - Identify unreplied reviewer comments (no author reply after reviewer comment) - `inst-identify-unreplied`
2. - `p1` - Classify each by severity: CRITICAL (blocking), HIGH (significant), MEDIUM (suggestion), LOW (nit) - `inst-classify-severity`
3. - `p1` - Reorder by severity (CRITICAL first) - `inst-reorder`

## 4. States (CDSL)

### PR Review State

- [ ] `p1` - **ID**: `cpt-cypilot-state-pr-workflows-review`

```
[NOT_REVIEWED] --review--> [REVIEWED]
[REVIEWED] --new-commits--> [STALE] --review--> [REVIEWED]
```

## 5. Definitions of Done

### PR Review Workflow

- [ ] `p1` - **ID**: `cpt-cypilot-dod-pr-workflows-review`

- [ ] - `p1` - PR review fetches latest data on every invocation (no caching)
- [ ] - `p1` - Review is read-only (no local working tree modifications)
- [ ] - `p1` - Structured review report written to `.prs/{ID}/review.md`
- [ ] - `p1` - Review includes existing reviewer comment analysis

### PR Status Workflow

- [ ] `p1` - **ID**: `cpt-cypilot-dod-pr-workflows-status`

- [ ] - `p1` - Status report classifies unreplied comments by severity
- [ ] - `p1` - Resolved-comment audit detects suspicious resolutions
- [ ] - `p1` - CI and merge conflict status included
- [ ] - `p1` - Supports single PR and ALL modes

## 6. Implementation Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| PR Script | `kits/sdlc/scripts/pr.py` | PR review and status workflow entry point, `gh` CLI integration |
| PR Review Prompts | `prompts/pr/*.md` | Review prompts for code, design, ADR reviews |

## 7. Acceptance Criteria

- [ ] PR review workflow produces structured report matching template format
- [ ] PR status workflow classifies unreplied comments by severity
- [ ] Both workflows fail gracefully when `gh` CLI is unavailable or not authenticated
- [ ] Both workflows always re-fetch data (no stale cache)
- [ ] Review reports are read-only — no local file modifications beyond report output
