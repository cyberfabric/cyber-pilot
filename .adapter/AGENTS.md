# FDD Adapter: FDD

---

## ⚠️ SCOPE LIMITATION ⚠️

**MUST SKIP this file** UNLESS working on FDD framework development

**MUST IGNORE this adapter** WHEN using FDD for other projects

**ONLY FOLLOW this adapter** WHEN developing or modifying the FDD framework itself

This adapter is for FDD project development, not for projects using FDD.

### Verification Checklist

**MUST verify ALL criteria before following this adapter**:

- [ ] Workspace root contains `.fdd-config.json` with `"project": "FDD"` OR current directory path ends with `/FDD` OR `/FDD/`
- [ ] Task is NOT about using FDD in another project
- [ ] No `.fdd-config.json` exists in the 3 immediate parent directories (excluding workspace root)

**If ANY criterion fails**: STOP, IGNORE this adapter, use parent `../AGENTS.md` only

**If ALL criteria pass**: Proceed with this adapter

### Confirmation Output

After verification, agent MUST output:
```
FDD Adapter: ACTIVE
- Project: FDD (verified via {method})
- Parent check: CLEAR (no conflicting projects)
```

Or if skipping:
```
FDD Adapter: SKIPPED
- Reason: {criterion that failed}
- Using: ../AGENTS.md only
```

---

**Extends**: `../AGENTS.md`

**Version**: 1.1
**Last Updated**: 2025-02-01
**Tech Stack**: Python 3 (runtime stdlib-only) + pytest via pipx

---

## Context Loading Rules

### Schema & Registry (for artifacts.json work)

ALWAYS open and follow `../schemas/artifacts.schema.json` WHEN working with artifacts.json

ALWAYS open and follow `../requirements/artifacts-registry.md` WHEN working with artifacts.json

### Artifact-Specific Specs

ALWAYS open and follow `artifacts.json` WHEN FDD follows rules `fdd-sdlc` for artifact kinds: PRD, DESIGN, FEATURES, ADR, FEATURE OR codebase

ALWAYS open and follow `specs/tech-stack.md` WHEN FDD follows rules `fdd-sdlc` for artifact kinds: DESIGN, ADR OR codebase

ALWAYS open and follow `specs/domain-model.md` WHEN FDD follows rules `fdd-sdlc` for artifact kinds: DESIGN, ADR, FEATURES, FEATURE OR codebase

ALWAYS open and follow `specs/api-contracts.md` WHEN FDD follows rules `fdd-sdlc` for artifact kinds: DESIGN, ADR, FEATURE OR codebase

ALWAYS open and follow `specs/patterns.md` WHEN FDD follows rules `fdd-sdlc` for artifact kinds: DESIGN, ADR, FEATURE OR codebase

ALWAYS open and follow `specs/project-structure.md` WHEN FDD follows rules `fdd-sdlc` for artifact kinds: FEATURE

### Codebase-Specific Specs

ALWAYS open and follow `specs/conventions.md` WHEN FDD follows rules `fdd-sdlc` for codebase

ALWAYS open and follow `specs/build-deploy.md` WHEN FDD follows rules `fdd-sdlc` for codebase

ALWAYS open and follow `specs/testing.md` WHEN FDD follows rules `fdd-sdlc` for codebase

ALWAYS open and follow `specs/language-config.md` WHEN FDD follows rules `fdd-sdlc` for codebase

### Error Handling

**If a spec file cannot be read**:
```
⚠ Spec file not found: {path}
→ Check file exists: ls {path}
→ Continue without this spec (reduced guidance)
→ Note missing spec in output
```

**If parent ../AGENTS.md cannot be read**:
```
⚠ Parent AGENTS.md not found
→ This adapter is standalone for this session
→ Proceed with this adapter only
```
