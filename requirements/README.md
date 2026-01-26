<!-- @fdd-algo:fdd-fdd-feature-init-structure-change-requirements-structure:ph-1 -->
# FDD Requirements Directory

This directory contains structure specifications for FDD artifacts.

## Naming Convention

All requirement specification files follow the naming pattern: `*-structure.md`

Examples:
- `feature-design-structure.md` - Structure spec for feature DESIGN.md
- `prd-structure.md` - Structure spec for PRD.md

## File Categories

- **Structure specs** (`*-structure.md`): Artifact format definitions
- **Workflow execution** (`workflow-*.md`): How to run workflows
- **Extension mechanism** (`extension.md`): Inheritance system

## Usage

Requirements files are referenced by:
- Validation workflows (to check artifact compliance)
- AI agents (to understand expected formats)
- `fdd validate` CLI (to enforce structure)
