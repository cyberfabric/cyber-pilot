Minimal Blueprint Example — a blueprint with only core markers and one heading.
This is the simplest valid blueprint that generates all output files.

Generates: template.md, constraints.toml, example.md, rules.md

`@cpt:blueprint`
```toml
version = 1
kit = "custom"
artifact = "MEMO"
description = "Internal memo"
```
`@/cpt:blueprint`

`@cpt:heading`
```toml
id = "memo-title"
level = 1
required = true
template = "Memo — {Topic of the memo}"
examples = ["# Memo — Q1 Planning"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
Write a short memo on the given topic.
```
`@/cpt:prompt`
