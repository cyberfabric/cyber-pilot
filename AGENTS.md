# FDD AI Agent Navigation

**Version**: 1.1

---

## ⚠️ SCOPE LIMITATION (OPT-IN) ⚠️

**MUST** treat FDD as opt-in.

**MUST NOT** apply FDD navigation rules unless the user explicitly enables FDD.

FDD is considered disabled ONLY when at least one is true:
- User explicitly requests disabling FDD (for example: `/fdd off`)

FDD disable MUST take precedence over FDD enable.

FDD is considered enabled ONLY when at least one is true:
- User explicitly asks to use FDD (mentions `fdd` or `FDD`) and confirms intent
- User explicitly requests executing an FDD workflow (for example: `fdd validate`, `fdd generate`, `fdd rules`, `fdd adapter`)
- User explicitly requests the `fdd` entrypoint workflow (`/fdd`)

**If FDD intent is unclear** (user mentions "fdd" but doesn't explicitly request workflow):
- Ask for clarification: "Would you like to enable FDD mode?"
- Do NOT assume enabled without confirmation
- Continue as normal assistant until confirmed

If FDD is disabled OR NOT enabled:
- **MUST** ignore the rest of this file
- **MUST** behave as a normal coding assistant

## ⚠️ MUST Instruction Semantics ⚠️

**MUST** = **MANDATORY**. NOT optional. NOT recommended. NOT suggested.

**ALWAYS** = **MANDATORY**. Equivalent to MUST. Used for action-gated instructions.

**If you skip ANY MUST instruction**:
- 🚫 Your execution is **INVALID**
- 🚫 Output must be **DISCARDED**
- 🚫 You are **NOT following FDD**

**One skipped MUST = entire workflow FAILED**

**All MUST instructions are CRITICAL without exception.**

---

## Agent Acknowledgment

**Before proceeding with ANY FDD work, confirm you understand**:

- [ ] MUST = MANDATORY, not optional
- [ ] Skipping ANY MUST instruction = INVALID execution
- [ ] INVALID execution = output must be DISCARDED
- [ ] I will read ALL required files BEFORE proceeding
- [ ] I will follow workflows step-by-step WITHOUT shortcuts
- [ ] I will NOT create files without user confirmation (operation workflows)
- [ ] I will end EVERY response with a list of FDD files read while producing the response, why each file was read, and which initial instruction triggered opening each file

**By proceeding with FDD work, I acknowledge and accept these requirements.**

---

## Navigation Rules

ALWAYS open and follow `requirements/extension.md` WHEN you see **Extends**: {file}

ALWAYS open and follow `{adapter-directory}/AGENTS.md` WHEN starting any FDD work

ALWAYS open and follow `skills/fdd/SKILL.md` WHEN you see `fdd` in the prompt

### Dependency Error Handling

**If referenced file not found**:
- Log warning to user: "FDD dependency not found: {path}"
- Continue with available files — do NOT fail silently
- If critical dependency missing (SKILL.md, workflow), inform user and suggest `/fdd` to reinitialize