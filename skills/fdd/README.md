# FDD Tool

Unified FDD tool for artifact validation, search, and traceability.

## Commands

| Command | Description |
|---------|-------------|
| `validate` | Validate FDD artifacts against templates |
| `validate-rules` | Validate rules configuration and templates |
| `validate-code` | Validate FDD traceability markers in code |
| `list-ids` | List all FDD IDs from artifacts |
| `list-id-kinds` | List ID kinds that exist in artifacts |
| `get-content` | Get content block for a specific FDD ID |
| `where-defined` | Find where an FDD ID is defined |
| `where-used` | Find all references to an FDD ID |
| `adapter-info` | Discover FDD adapter configuration |
| `init` | Initialize FDD config and adapter |
| `agents` | Generate agent-specific workflow proxies and skill outputs |
| `self-check` | Validate examples against templates |

## Usage

```bash
# Validate all registered artifacts
python3 scripts/fdd.py validate

# Validate specific artifact
python3 scripts/fdd.py validate --artifact architecture/PRD.md

# Validate code traceability
python3 scripts/fdd.py validate-code

# List all IDs
python3 scripts/fdd.py list-ids

# Find where ID is defined
python3 scripts/fdd.py where-defined --id fdd-myapp-req-auth

# Initialize project
python3 scripts/fdd.py init --yes
```

## Testing

```bash
make test
```

## Documentation

See `SKILL.md` for complete command reference and `fdd.clispec` for CLI specification.
