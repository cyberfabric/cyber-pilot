<!-- @cpt:root-agents -->
# Cypilot AI Agent Navigation

**Version**: 1.2

---

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `{cypilot}` | `@/.cypilot` | Cypilot install directory |

## Navigation Rules

ALWAYS open and follow `{cypilot}/config/AGENTS.md` FIRST

<!-- /@cpt:root-agents -->

# Cypilot AI Agent Navigation

**Version**: 1.1

---

## Navigation Rules

ALWAYS open and follow `{adapter-directory}/AGENTS.md` WHEN starting any Cypilot work

### Dependency Error Handling

**If referenced file not found**:
- Log warning to user: "Cypilot dependency not found: {path}"
- Continue with available files — do NOT fail silently
- If critical dependency missing (SKILL.md, workflow), inform user and suggest `/cypilot` to reinitialize
