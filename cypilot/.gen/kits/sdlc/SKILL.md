---
name: cypilot-sdlc
description: "Artifacts: ADR, CODEBASE, DECOMPOSITION, DESIGN, FEATURE, PR-CODE-REVIEW-TEMPLATE, PR-REVIEW, PR-STATUS-REPORT-TEMPLATE, PRD; Workflows: pr-review, pr-status"
---

# Cypilot Skill — Kit `sdlc`

Generated from kit `sdlc` blueprints.

## ADR

### ADR Commands
- `cypilot validate --artifact <ADR.md>` — validate ADR structure and IDs
- `cypilot list-ids --kind adr` — list all ADRs
- `cypilot where-defined <id>` — find where an ADR ID is defined
- `cypilot where-used <id>` — find where an ADR ID is referenced in DESIGN
### ADR Workflows
- **Generate ADR**: create a new ADR from template with guided prompts per section
- **Analyze ADR**: validate structure (deterministic) then semantic quality (checklist-based)

## CODEBASE

### CODE Commands
- `cypilot validate --artifact <code-path>` — validate code traceability and quality
- `cypilot where-defined <id>` — find where an ID is defined in artifacts
- `cypilot where-used <id>` — find where an ID is referenced in code via `@cpt-*` markers
### CODE Workflows
- **Generate CODE**: implement FEATURE design with optional `@cpt-*` traceability markers
- **Analyze CODE**: validate implementation coverage, traceability, tests, and quality

## DECOMPOSITION

### DECOMPOSITION Commands
- `cypilot validate --artifact <DECOMPOSITION.md>` — validate DECOMPOSITION structure and IDs
- `cypilot list-ids --kind feature` — list all features
- `cypilot list-ids --kind status` — list status indicators
- `cypilot where-defined <id>` — find where a feature ID is defined
- `cypilot where-used <id>` — find where a feature ID is referenced in FEATURE artifacts
### DECOMPOSITION Workflows
- **Generate DECOMPOSITION**: create feature manifest from DESIGN with guided prompts
- **Analyze DECOMPOSITION**: validate structure (deterministic) then decomposition quality (checklist-based)

## DESIGN

### DESIGN Commands
- `cypilot validate --artifact <DESIGN.md>` — validate DESIGN structure and IDs
- `cypilot list-ids --kind component` — list all components
- `cypilot list-ids --kind principle` — list all design principles
- `cypilot where-defined <id>` — find where a DESIGN ID is defined
- `cypilot where-used <id>` — find where a DESIGN ID is referenced downstream
### DESIGN Workflows
- **Generate DESIGN**: create a new DESIGN from template with guided prompts per section
- **Analyze DESIGN**: validate structure (deterministic) then semantic quality (checklist-based)

## FEATURE

### FEATURE Commands
- `cypilot validate --artifact <FEATURE.md>` — validate FEATURE structure and IDs
- `cypilot list-ids --kind flow` — list all flows
- `cypilot list-ids --kind algo` — list all algorithms
- `cypilot list-ids --kind state` — list all state machines
- `cypilot list-ids --kind dod` — list all definitions of done
- `cypilot where-defined <id>` — find where a FEATURE ID is defined
- `cypilot where-used <id>` — find where a FEATURE ID is referenced in code
### FEATURE Workflows
- **Generate FEATURE**: create a new FEATURE from template with guided CDSL prompts
- **Analyze FEATURE**: validate structure (deterministic) then semantic quality (checklist-based)

## PR-REVIEW

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

## PRD

### PRD Commands
- `cypilot validate --artifact <PRD.md>` — validate PRD structure and IDs
- `cypilot list-ids --kind fr` — list all functional requirements
- `cypilot list-ids --kind actor` — list all actors
- `cypilot where-defined <id>` — find where a PRD ID is defined
- `cypilot where-used <id>` — find where a PRD ID is referenced downstream
### PRD Workflows
- **Generate PRD**: create a new PRD from template with guided prompts per section
- **Analyze PRD**: validate structure (deterministic) then semantic quality (checklist-based)
