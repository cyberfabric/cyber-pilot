# FDD Artifact Templates

**Version**: 1.0

---

## Overview

This directory contains templates for all FDD artifacts. Templates define the **exact structure** that must be used when generating artifacts.

**Purpose**:
- Provide consistent structure for all artifacts
- Enable agents to generate valid artifacts
- Separate structure (templates) from validation rules (requirements)

---

## Template Files

| Template | Artifact | Location |
|----------|----------|----------|
| `PRD.template.md` | PRD | `architecture/PRD.md` |
| `DESIGN.template.md` | Overall Design | `architecture/DESIGN.md` |
| `ADR.template.md` | Architecture Decision Records | `architecture/ADR/` |
| `FEATURES.template.md` | Features Manifest | `architecture/features/FEATURES.md` |
| `feature-DESIGN.template.md` | Feature Design | `architecture/features/feature-{slug}/DESIGN.md` |
| `adapter-AGENTS.template.md` | Adapter AGENTS | `{adapter-directory}/AGENTS.md` |

---

## Usage

**Agent instructions**:

1. **ALWAYS read the template** before generating any artifact
2. **Follow the structure exactly** - do not add/remove sections
3. **Replace placeholders** with actual content:
   - `{PROJECT_NAME}` → actual project name
   - `{project-name}` → kebab-case project name
   - `{YYYY-MM-DD}` → actual date
   - `{description}` → actual description
4. **Preserve markers**:
   - `<!-- fdd-id-content -->` blocks around ID-related content
   - `<!-- TODO: ... -->` for sections needing user input

---

## Placeholder Conventions

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{PROJECT_NAME}` | Display name | `Analytics Platform` |
| `{project-name}` | Kebab-case identifier | `analytics-platform` |
| `{feature-slug}` | Feature identifier | `user-auth` |
| `{YYYY-MM-DD}` | ISO date | `2025-01-23` |
| `{N}` | Sequential number | `1`, `2`, `3` |
| `{description}` | Free text | `User authentication` |

---

## References

**Related files**:
- `requirements/*-structure.md` - Validation rules for each artifact
- `workflows/*.md` - Workflows that use these templates
- `AGENTS.md` - Navigation rules
