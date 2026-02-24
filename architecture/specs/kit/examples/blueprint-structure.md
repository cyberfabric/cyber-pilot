Blueprint File Structure Example — illustrates the ordering and structure of all
marker types in a single blueprint file. This text is outside any marker block
and is ignored by the processor. It serves as human-readable documentation.

---

1. Identity marker (required, must be first)

`@cpt:blueprint`
```toml
version = 1
kit = "sdlc"
artifact = "PRD"
description = "Product Requirements Document — actors, problems, FR/NFR, use cases, success criteria"
codebase = false
```
`@/cpt:blueprint`

2. SKILL.md extension (optional)

`@cpt:skill`
```markdown
### PRD Commands
- `cypilot validate --artifact <PRD.md>` — validate PRD
```
`@/cpt:skill`

3. Workflow definitions (zero or more)

`@cpt:workflow`
```toml
name = "generate-prd"
description = "Generate a new PRD from template with guided prompts"
```
```markdown
## Steps
1. Load template.md, checklist.md, example.md
2. Collect information via batch questions
3. Generate artifact following template structure
4. Run validation automatically
```
`@/cpt:workflow`

4. Rules structure skeleton (optional)

`@cpt:rules`
```toml
[prerequisites]
sections = ["load_dependencies"]
[requirements]
sections = ["structural", "semantic"]
```
`@/cpt:rules`

5. Individual rule entries (zero or more)

`@cpt:rule`
```toml
kind = "prerequisites"
section = "load_dependencies"
```
```markdown
- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
```
`@/cpt:rule`

6. Checklist structure skeleton (optional)

`@cpt:checklist`
```toml
[severity]
levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
[[domain]]
abbr = "BIZ"
name = "Business"
standards = ["ISO/IEC/IEEE 29148:2018"]
```
`@/cpt:checklist`

7. Individual check items (zero or more)

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
```
`@/cpt:check`

8. Template section — headings, prompts, examples

`@cpt:heading`
```toml
id = "prd-h1-title"
level = 1
required = true
pattern = "PRD\\s*[—–-]\\s*.+"
template = "PRD — {Title of product}"
examples = ["# PRD — TaskFlow"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
Write 1-2 paragraphs: what is this system and what problem does it solve.
```
`@/cpt:prompt`

`@cpt:example`
```markdown
Overwork Alert monitors employee work hours and sends automated alerts
when thresholds are exceeded.
```
`@/cpt:example`
