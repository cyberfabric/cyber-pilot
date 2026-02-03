# Skills System Specification

**Version**: 1.1  
**Purpose**: Define how agents discover, select, and use Claude-compatible skills in this repository  
**Scope**: All agent work in this repository (all Spider workflows and non-Spider tasks)

**Path base**: All paths in this document are relative to the Spider repository root (the directory containing `AGENTS.md`).

**How to locate the path base in a monorepo**: The Spider repository root is the directory that contains `AGENTS.md` and is the parent directory of `skills/` (this file is `skills/SKILLS.md`).

**Skill root directory**: `skills/`

---

## Core Rules

**MUST**:
- Treat every directory under `skills/` (except this file) as an Agent Skills skill.
- Require each skill directory to contain `SKILL.md` with valid YAML frontmatter.
- Use progressive disclosure:
  - Read only `name` + `description` for discovery.
  - Read SKILL.md body only after selecting a skill.
  - Read `references/` files only when explicitly needed.

**MUST NOT**:
- Load multiple full SKILL bodies into context during discovery.
- Invent skill behavior that is not defined in the skill’s `SKILL.md`.
- Enumerate skills from any other repository root (e.g., monorepo root) instead of the path base defined above.

---

## Toolchain Preflight (MANDATORY)

**Before doing any work that relies on skill scripts, agent MUST verify**:
- `python` OR `python3` is available and runnable

**Minimum checks**:
- `python --version` OR `python3 --version`

**If ANY tool is missing**:
- STOP.
- Do NOT proceed with the workflow/task.
- Propose an installation approach.
- The agent chooses how to install (method is not prescribed here).
- The user must approve any commands that modify the system.

---

## Adding a New Skill (Repository Policy)

A new skill directory under `skills/` MUST:
- Contain `SKILL.md`
- Use a `name` that matches the directory name
- Keep SKILL.md body concise and use `references/` for detailed material

If a skill contains `scripts/`, it MUST:
- Contain `tests/` with unit tests for the scripts
- Use Python standard library `unittest` (no external test dependencies)
- Be deterministic (no network access, no time-based assertions, no random data)
- Avoid modifying repository state (use temporary files/directories for test artifacts)
- Cover both PASS and FAIL cases for every supported artifact kind/branch in the script

To run tests:
- `python3 -m unittest discover -s /Spider/skills/<skill>/tests -p 'test_*.py'`

---

## Available Skills

### spider

**Name**: `spider`  
**Description**: Unified Spider tool for artifact validation, search, and traceability. Validates Spider artifacts (PRD, DESIGN, ADR, DECOMPOSITION, FEATURE) against structure requirements, provides search and ID lookup across artifacts, and enables full bidirectional traceability between documentation and code.

**Primary capabilities**:
- Artifact validation with deterministic pass/fail
- Search and query Spider artifacts
- ID extraction and lookup (actors, capabilities, requirements, flows, etc.)
- Repository-wide traceability (where-defined, where-used)
- Code traceability scanning (@spider-* tags)
- Support for qualified IDs (:ph-N:inst-*)

**Location**: `skills/spider/`  
**See**: `skills/spider/SKILL.md` for complete documentation

---

## References

- Agent Skills specification: https://agentskills.io/specification
- Anthropic reference skills: https://github.com/anthropics/skills
