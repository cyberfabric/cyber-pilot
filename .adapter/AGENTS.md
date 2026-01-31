# FDD Adapter: FDD

---

## ⚠️ SCOPE LIMITATION ⚠️

**MUST SKIP this file** UNLESS working on FDD framework development

**MUST IGNORE this adapter** WHEN using FDD for other projects

**ONLY FOLLOW this adapter** WHEN developing or modifying the FDD framework itself

This adapter is for FDD project development, not for projects using FDD.

### Verification Checklist

**MUST verify ALL criteria before following this adapter**:

- [ ] Workspace root contains `.fdd-config.json` with `"project": "FDD"` or repository name is "FDD"
- [ ] Task is NOT about using FDD in another project
- [ ] No parent directory contains another project's `.fdd-config.json` or project files

**If ANY criterion fails**: STOP, IGNORE this adapter, use parent `../AGENTS.md` only

**If ALL criteria pass**: Proceed with this adapter

---

**Extends**: `../AGENTS.md`

**Version**: 1.0  
**Last Updated**: 2025-01-17  
**Tech Stack**: Python 3 (runtime stdlib-only) + pytest via pipx

---

ALWAYS open and follow `../schemas/artifacts.schema.json` WHEN working with artifacts.json

ALWAYS open and follow `../requirements/artifacts-registry.md` WHEN working with artifacts.json

ALWAYS open and follow `artifacts.json` WHEN executing any FDD workflow

ALWAYS open and follow `specs/tech-stack.md` WHEN executing workflows: adapter.md, design.md, design-validate.md, adr.md, adr-validate.md, code.md, code-validate.md

ALWAYS open and follow `specs/domain-model.md` WHEN executing workflows: design.md, design-validate.md, adr.md, adr-validate.md, features.md, features-validate.md, feature.md, feature-validate.md, code.md, code-validate.md

ALWAYS open and follow `specs/api-contracts.md` WHEN executing workflows: design.md, design-validate.md, adr.md, adr-validate.md, feature.md, feature-validate.md, code.md, code-validate.md

ALWAYS open and follow `specs/patterns.md` WHEN executing workflows: design.md, design-validate.md, adr.md, adr-validate.md, feature.md, feature-validate.md, code.md, code-validate.md

ALWAYS open and follow `specs/conventions.md` WHEN executing workflows: adapter.md, code.md, code-validate.md

ALWAYS open and follow `specs/build-deploy.md` WHEN executing workflows: code.md, code-validate.md

ALWAYS open and follow `specs/testing.md` WHEN executing workflows: code.md, code-validate.md

ALWAYS open and follow `specs/language-config.md` WHEN executing workflows: code-validate.md

ALWAYS open and follow `specs/project-structure.md` WHEN executing workflows: adapter.md, feature.md, feature-validate.md
