# Template Checklist

## Pre-Generation

- [ ] Identified the artifact kind (PRD, DESIGN, ADR, etc.)
- [ ] Know the main sections needed
- [ ] Know what ID kinds this artifact defines
- [ ] Know cross-reference relationships
- [ ] Understand FDD marker syntax

## Structure

- [ ] Has fdd-template frontmatter
- [ ] Has version (major, minor)
- [ ] Has kind field
- [ ] Has root marker `<!-- fdd:#:{kind} -->`
- [ ] Has section markers `<!-- fdd:##:{section} -->`
- [ ] All markers are paired (open/close)

## Content

- [ ] ID markers have correct format
- [ ] ID markers have appropriate attributes (has, covered_by)
- [ ] Paragraph markers for descriptions
- [ ] List markers where appropriate
- [ ] Repeat attributes set correctly (once, many)
- [ ] Required attributes set where needed

## Post-Generation

- [ ] Frontmatter is valid YAML
- [ ] All markers are properly paired
- [ ] Marker types are valid
- [ ] Template passes validate-rules
- [ ] Example can be generated from template

## Quality

- [ ] Clear placeholder text
- [ ] Logical section order
- [ ] Consistent marker naming
- [ ] Appropriate nesting levels
- [ ] No unnecessary complexity
