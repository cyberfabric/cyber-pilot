# API Contracts

**Version**: 2.0
**Last Updated**: 2025-02-01
**Purpose**: Define CLI command contracts for FDD skill

---

## Overview

FDD skill provides a CLI tool (`fdd.py`) for artifact management, validation, and traceability.

**Authoritative source**: `skills/fdd/SKILL.md` - Complete command documentation

**Philosophy**:
- JSON output for machine consumption
- Human-readable help via `--help`
- Exit codes for automation
- Integration with FDD workflows

---

## Contract Location

**Primary documentation**: `skills/fdd/SKILL.md`

**Structure**:
```
skills/fdd/
├── SKILL.md             # Command documentation (authoritative)
├── scripts/
│   └── fdd.py           # CLI entrypoint
│   └── fdd/             # Implementation
└── README.md            # Overview
```

---

## Available Commands

### Validation Commands

| Command | Description | Required Args |
|---------|-------------|---------------|
| `validate` | Validate FDD artifacts against templates | None (validates all) or `--artifact <path>` |
| `validate-code` | Validate traceability markers in code | None or `<path>` |
| `validate-rules` | Validate rules configuration and templates | None or `--rule <id>` |

### Search Commands

| Command | Description | Required Args |
|---------|-------------|---------------|
| `list-ids` | List FDD IDs from artifacts | None (all) or `--artifact <path>` |
| `list-id-kinds` | List ID kinds that exist | None or `--artifact <path>` |
| `get-content` | Get content block for specific ID | `--id <id>` + (`--artifact` or `--code`) |
| `where-defined` | Find where ID is defined | `--id <id>` |
| `where-used` | Find all references to ID | `--id <id>` |

### Adapter & Setup Commands

| Command | Description | Required Args |
|---------|-------------|---------------|
| `adapter-info` | Discover FDD adapter configuration | None |
| `init` | Initialize FDD config and adapter | None |
| `agents` | Generate agent-specific workflow proxies | `--agent <name>` |
| `self-check` | Validate examples against templates | None or `--rule <id>` |

---

## Exit Code Semantics

**Standard exit codes**:
| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | File system error or resource not found |
| `2` | Validation failure or ID not found |

---

## Command Invocation

### ✅ Correct Invocation

```bash
# From project root - ALWAYS use this pattern
python3 skills/fdd/scripts/fdd.py <command> [options]

# Examples:
python3 skills/fdd/scripts/fdd.py validate
python3 skills/fdd/scripts/fdd.py validate --artifact architecture/PRD.md --verbose
python3 skills/fdd/scripts/fdd.py validate-code
python3 skills/fdd/scripts/fdd.py list-ids --pattern "-req-"
python3 skills/fdd/scripts/fdd.py where-defined --id fdd-myapp-actor-admin
python3 skills/fdd/scripts/fdd.py adapter-info
python3 skills/fdd/scripts/fdd.py init --yes
python3 skills/fdd/scripts/fdd.py agents --agent claude
```

### ❌ Incorrect Invocation

```bash
# Missing script path
python3 fdd.py validate

# Wrong module invocation (only works from specific directory)
python3 -m fdd.cli validate

# Non-existent command
python3 scripts/fdd.py search --query "auth"

# Wrong option name
python3 scripts/fdd.py list-ids --file architecture/DESIGN.md
# Correct: --artifact architecture/DESIGN.md
```

---

## Integration with Workflows

**Validation workflow** (`workflows/validate.md`):
- Uses `validate --artifact <path>` for artifact validation
- Uses `validate-code` for traceability validation

**Generate workflow** (`workflows/generate.md`):
- Uses `where-defined` and `where-used` for traceability
- Uses `list-ids` to check existing IDs

**Adapter workflow** (`workflows/adapter.md`):
- Uses `adapter-info` to discover configuration
- Uses `init` to bootstrap new projects

---

## Error Handling

**If command fails**:
```
⚠ Command failed: {command}
Exit code: {code}
→ Check --help for correct usage: python3 scripts/fdd.py {command} --help
→ Verify paths exist and are readable
→ Check artifacts.json for registered artifacts
```

**If command not found**:
```
⚠ Unknown command: {command}
→ Available commands: validate, validate-code, validate-rules, list-ids,
   list-id-kinds, get-content, where-defined, where-used, adapter-info,
   init, agents, self-check
→ Run: python3 scripts/fdd.py --help
```

---

## Validation Checklist

Agent MUST verify before using FDD CLI:
- [ ] Using correct invocation: `python3 skills/fdd/scripts/fdd.py <command>`
- [ ] Command exists (check Available Commands table above)
- [ ] Required arguments provided
- [ ] Option names match exactly (including `--`)
- [ ] Exit codes handled appropriately

**Self-test** (MUST answer YES to all):
- [ ] Did I check SKILL.md for command signature?
- [ ] Are all required arguments present?
- [ ] Am I using the full script path?
- [ ] Did I handle potential errors?

---

## Output Format

All commands output **JSON** to stdout:

```json
{
  "status": "PASS" | "FAIL" | "ERROR",
  "message": "Human-readable summary",
  ...command-specific fields...
}
```

**Verbose mode** (`--verbose`): Includes detailed information in output.

---

## References

**Used by workflows**:
- `workflows/validate.md` - Validation commands
- `workflows/generate.md` - Traceability commands
- `workflows/adapter.md` - Setup commands

**Related files**:
- `skills/fdd/SKILL.md` - Authoritative command documentation
- `skills/fdd/scripts/fdd.py` - CLI implementation
