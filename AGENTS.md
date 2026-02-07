# Cypilot AI Agent Navigation

**Version**: 1.1

---

## ⚠️ MUST Instruction Semantics ⚠️

**MUST** = **MANDATORY**. NOT optional. NOT recommended. NOT suggested.

**ALWAYS** = **MANDATORY**. Equivalent to MUST. Used for action-gated instructions.

**If you skip ANY MUST instruction**:
- 🚫 Your execution is **INVALID**
- 🚫 Output must be **DISCARDED**
- 🚫 You are **NOT following Cypilot**

**One skipped MUST = entire workflow FAILED**

**All MUST instructions are CRITICAL without exception.**

## ⚠️ SCOPE LIMITATION (OPT-IN) ⚠️

**MUST** treat Cypilot as opt-in.

**MUST NOT** apply Cypilot navigation rules unless the user explicitly enables Cypilot.

Cypilot is considered disabled ONLY when at least one is true:
- User explicitly requests disabling Cypilot (for example: `/cypilot off`)

Cypilot disable MUST take precedence over Cypilot enable.

Cypilot is considered enabled ONLY when at least one is true:
- User explicitly asks to use Cypilot (mentions `cypilot` or `Cypilot`) and confirms intent
- User explicitly requests executing an Cypilot workflow (for example: `cypilot analyze`, `cypilot generate`, `cypilot rules`, `cypilot adapter`)
- User explicitly requests the `cypilot` entrypoint workflow (`/cypilot`)

**If Cypilot intent is unclear** (user mentions "cypilot" but doesn't explicitly request workflow):
- Ask for clarification: "Would you like to enable Cypilot mode?"
- Do NOT assume enabled without confirmation
- Continue as normal assistant until confirmed

If Cypilot is disabled OR NOT enabled:
- **MUST** ignore the rest of this file
- **MUST** behave as a normal coding assistant


---

## Agent Acknowledgment

**Before proceeding with ANY Cypilot work, confirm you understand**:

- [ ] MUST = MANDATORY, not optional
- [ ] Skipping ANY MUST instruction = INVALID execution
- [ ] INVALID execution = output must be DISCARDED
- [ ] I will read ALL required files BEFORE proceeding
- [ ] I will follow workflows step-by-step WITHOUT shortcuts
- [ ] I will NOT create files without user confirmation (operation workflows)
- [ ] I will end EVERY response with a list of Cypilot files read while producing the response, why each file was read, and which initial instruction triggered opening each file

**By proceeding with Cypilot work, I acknowledge and accept these requirements.**

---

## Variables

**While Cypilot is enabled**, remember these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `{cypilot_path}` | Directory containing this AGENTS.md | Project root for Cypilot navigation |
| `{cypilot_mode}` | `on` or `off` | Current Cypilot mode state |

**Setting `{cypilot_mode}`**:
- Explicit command: `cypilot on` / `cypilot off`
- Cypilot prompts that activate/deactivate Cypilot workflows

Use `{cypilot_path}` as the base path for all relative Cypilot file references.

---

## Navigation Rules

ALWAYS open and follow `requirements/extension.md` WHEN you see **Extends**: {file}

ALWAYS open and follow `{adapter-directory}/AGENTS.md` WHEN starting any Cypilot work

ALWAYS open and follow `skills/cypilot/SKILL.md` WHEN you see `cypilot` in the prompt

## Skill registration

<available_skills>
  <skill>
    <name>cypilot</name>
    <description>Framework for Documentation and Development - AI agent toolkit. Use when user works with PRD, DESIGN, DECOMPOSITION, ADR, spec specs, architecture documentation, requirements, or mentions Cypilot/workflow/artifact/adapter/traceability. Provides structured artifact templates, validation, design-to-code traceability, and guided code implementation with traceability markers. Opt-in - suggest enabling when design/architecture activities detected.</description>
    <location>skills/cypilot/SKILL.md</location>
  </skill>
</available_skills>

### Dependency Error Handling

**If referenced file not found**:
- Log warning to user: "Cypilot dependency not found: {path}"
- Continue with available files — do NOT fail silently
- If critical dependency missing (SKILL.md, workflow), inform user and suggest `/cypilot` to reinitialize

---

## Execution Logging

ALWAYS provide execution visibility WHEN Cypilot is enabled.

ALWAYS notify the user WHEN entering a major section (H2 heading `##`) of any Cypilot prompt (workflow, rules, requirements).

ALWAYS notify the user WHEN completing a checklist task (a Markdown task line starting with `- [ ]`).

ALWAYS use this notification format WHEN emitting execution logs:

```
📟 [CONTEXT]: MESSAGE
```

ALWAYS set **CONTEXT** to the file or section being executed WHEN emitting execution logs (e.g., `workflows/generate.md`, `DESIGN rules`, `execution-protocol`).

ALWAYS set **MESSAGE** to what Cypilot is doing and why WHEN emitting execution logs.

ALWAYS ensure execution logging supports these goals WHEN Cypilot is enabled:
- Help the user understand which Cypilot prompts are being followed
- Help the user track decision points and branching logic
- Help the user debug unexpected behavior
- Help the user learn the Cypilot workflow

ALWAYS consider these examples as valid execution logs WHEN Cypilot is enabled:

```
📟 [execution-protocol]: Entering "Load Rules" — target is CODE, loading codebase/rules.md
📟 [DESIGN rules]: Completing "Validate structure" — all required sections present
📟 [workflows/generate.md]: Entering "Determine Target" — user requested code implementation
```