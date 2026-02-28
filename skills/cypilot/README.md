# Cypilot Skill Engine

Deterministic agent tool for structured workflows, artifact validation, traceability, and multi-agent integration.

## Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize Cypilot config directory (`.core/`, `.gen/`, `config/`) and root `AGENTS.md` |
| `update` | Update `.core/` from cache, regenerate `.gen/` from user blueprints, ensure `config/` scaffold |
| `agents` | Generate agent-specific entry points (skills, workflows, commands) for supported agents |
| `auto-config` | Scan project structure and generate per-system convention rules |
| `validate` | Validate artifacts against templates (structure, IDs, cross-references) |
| `validate-kits` | Validate kit configuration, blueprint markers, and constraints |
| `validate-code` | Validate `@cpt-*` traceability markers in code (pairing, coverage, orphans) |
| `list-ids` | List all Cypilot IDs from registered artifacts |
| `list-id-kinds` | List ID kinds that exist in artifacts |
| `get-content` | Get content block for a specific Cypilot ID |
| `where-defined` | Find where a Cypilot ID is defined |
| `where-used` | Find all references to a Cypilot ID |
| `info` | Discover Cypilot configuration and show project status |
| `self-check` | Validate kit examples against their own templates |

## Usage

### Via global CLI (recommended)

```bash
cypilot init
cypilot validate
cypilot validate-code
cypilot agents --agent windsurf
cypilot update
```

### Via direct script invocation

```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py validate
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py validate --artifact architecture/PRD.md
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py validate-code
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py list-ids
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py where-defined --id cpt-myapp-fr-auth
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py init --yes
```

All commands output JSON to stdout.

## Testing

```bash
make test
make test-coverage
```

## Documentation

- `SKILL.md` — complete skill definition with mandatory instructions, workflow routing, and command reference
- `cypilot.clispec` — CLI specification (commands, flags, output formats)
