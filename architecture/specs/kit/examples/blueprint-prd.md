PRD Blueprint Example (SDLC Kit) — a representative PRD blueprint showing
skills, workflows, rules, checklist, and template markers in use.

`@cpt:blueprint`
```toml
version = 1
kit = "sdlc"
artifact = "PRD"
description = "Product Requirements Document — actors, problems, FR/NFR, use cases, success criteria"
codebase = false
```
`@/cpt:blueprint`

SKILL.md extension — these commands and workflows appear in the agent's SKILL.md.

`@cpt:skill`
```markdown
### PRD Commands
- `cypilot validate --artifact <PRD.md>` — validate PRD
- `cypilot list-ids --kind fr` — list all functional requirements
### PRD Workflows
- **Generate PRD**: create a new PRD from template with guided prompts
- **Analyze PRD**: validate structure then semantic quality
```
`@/cpt:skill`

Workflow: generate-prd — creates a new PRD from template with guided prompts.

`@cpt:workflow`
```toml
name = "generate-prd"
description = "Generate a new PRD from template with guided prompts"
```
```markdown
## Steps
1. Load template.md, checklist.md, example.md
2. Collect information via batch questions with proposals
3. Generate artifact following template structure and checklist criteria
4. Run validation automatically
```
`@/cpt:workflow`

Workflow: analyze-prd — validates PRD structure then semantic quality.

`@cpt:workflow`
```toml
name = "analyze-prd"
description = "Validate PRD structure then semantic quality"
```
```markdown
## Steps
1. Run `cypilot validate --artifact <PRD.md>`
2. Review structural issues (headings, IDs, placeholders)
3. Review semantic quality against checklist
4. Report findings with actionable remediation
```
`@/cpt:workflow`

Rules structure — defines sections for the generated rules.md.

`@cpt:rules`
```toml
[prerequisites]
sections = ["load_dependencies"]
[requirements]
sections = ["structural", "semantic"]
[tasks]
phases = ["setup", "content_creation"]
[validation]
sections = ["structural", "semantic"]
```
`@/cpt:rules`

`@cpt:rule`
```toml
kind = "prerequisites"
section = "load_dependencies"
```
```markdown
- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
```
`@/cpt:rule`

`@cpt:rule`
```toml
kind = "requirements"
section = "semantic"
```
```markdown
- [ ] Purpose MUST be ≤ 2 paragraphs
- [ ] Purpose MUST NOT contain implementation details
- [ ] Vision MUST explain WHY the product exists
```
`@/cpt:rule`

Checklist structure — defines domains and severity levels for the generated checklist.md.

`@cpt:checklist`
```toml
[severity]
levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
[review]
priority = ["BIZ", "ARCH", "SEC", "TEST"]
[[domain]]
abbr = "BIZ"
name = "Business"
standards = ["ISO/IEC/IEEE 29148:2018"]
```
`@/cpt:checklist`

`@cpt:check`
```toml
id = "BIZ-PRD-001"
domain = "BIZ"
title = "Vision Clarity"
severity = "CRITICAL"
kind = "must_have"
```
```markdown
- [ ] Purpose statement explains WHY the product exists
- [ ] Target users clearly identified with specificity
- [ ] Success criteria are quantifiable
```
`@/cpt:check`

Template section — headings, prompts, and examples that generate template.md,
constraints.toml, example.md, and section-scoped rules in rules.md.

`@cpt:heading`
```toml
id = "prd-h1-title"
level = 1
required = true
multiple = false
pattern = "PRD\\s*[—–-]\\s*.+"
template = "PRD — {Title of product}"
examples = ["# PRD — Overwork Alert"]
```
`@/cpt:heading`

`@cpt:heading`
```toml
id = "prd-overview"
level = 2
required = true
multiple = false
numbered = true
pattern = "Overview"
examples = ["## 1. Overview"]
```
`@/cpt:heading`

`@cpt:heading`
```toml
id = "prd-overview-purpose"
level = 3
required = true
multiple = false
numbered = true
pattern = "Purpose"
description = "What the product is and what problem it solves."
examples = ["### 1.1 Purpose"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
Write 1-2 paragraphs: what is this system/module and what problem does it solve.
Reference the system name from project config.
```
`@/cpt:prompt`

`@cpt:example`
```markdown
Overwork Alert is a system that monitors employee work hours across the organization
and sends automated alerts when individuals exceed configurable weekly thresholds.
The system integrates with existing time tracking tools and provides real-time
dashboards for management oversight.
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "prd-overview-background"
level = 3
required = true
multiple = false
numbered = true
pattern = "Background.*|Problem Statement.*"
description = "Context, current pain points, why this capability is needed now."
examples = ["### 1.2 Background / Problem Statement"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
Write 2-3 paragraphs: context, current pain points, why this capability is needed now.
```
`@/cpt:prompt`

`@cpt:example`
```markdown
Currently, managers rely on manual timesheet reviews to identify employees at risk of
burnout. This process is error-prone, delayed by up to two weeks, and provides no
real-time visibility. Several incidents of employee burnout in Q3 2025 were only
detected after the fact, resulting in extended medical leave and project delays.
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "prd-overview-goals"
level = 3
required = true
multiple = false
numbered = true
pattern = "Goals.*"
description = "Measurable business outcomes."
examples = ["### 1.3 Goals (Business Outcomes)"]
```
`@/cpt:heading`

`@cpt:example`
```markdown
- Reduce burnout incidents by 60% within 6 months of deployment
- Provide real-time alerts within 1 hour of threshold breach
- Achieve 90% manager adoption within first quarter
```
`@/cpt:example`
