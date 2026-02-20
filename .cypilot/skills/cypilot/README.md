# Cypilot Tool

Unified Cypilot tool for artifact validation, search, and traceability.

## Commands

| Command | Description |
|---------|-------------|
| `validate` | Validate Cypilot artifacts against templates |
| `validate-kits` | Validate kit configuration and templates |
| `validate-code` | Validate Cypilot traceability markers in code |
| `list-ids` | List all Cypilot IDs from artifacts |
| `list-id-kinds` | List ID kinds that exist in artifacts |
| `get-content` | Get content block for a specific Cypilot ID |
| `where-defined` | Find where an Cypilot ID is defined |
| `where-used` | Find all references to an Cypilot ID |
| `adapter-info` | Discover Cypilot adapter configuration |
| `init` | Initialize Cypilot config and adapter |
| `agents` | Generate agent-specific workflow proxies and skill outputs |
| `self-check` | Validate examples against templates |

## Usage

```bash
# Validate all registered artifacts
python3 scripts/cypilot.py validate

# Validate specific artifact
python3 scripts/cypilot.py validate --artifact architecture/PRD.md

# Validate code traceability
python3 scripts/cypilot.py validate-code

# List all IDs
python3 scripts/cypilot.py list-ids

# Find where ID is defined
python3 scripts/cypilot.py where-defined --id cpt-myapp-req-auth

# Initialize project
python3 scripts/cypilot.py init --yes
```

## Testing

```bash
make test
```

## Documentation

See `SKILL.md` for complete command reference and `cypilot.clispec` for CLI specification.
