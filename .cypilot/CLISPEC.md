# CLISPEC - CLI Command Specification Format

**Version**: 1.0  
**Purpose**: Human and machine-readable format for CLI command documentation

---

## Overview

CLISPEC is a simple, structured text format for documenting CLI commands. It is designed to be:
- **Human-readable**: Easy to write and read in plain text
- **Machine-parseable**: Structured format for tooling and AI agents
- **Expressive**: Captures all essential CLI command information
- **Minimal**: No complex syntax, just clear sections

**Primary audience**: AI agents implementing or using CLI tools

**Use cases**:
- CLI tool documentation
- Command validation
- AI agent command understanding
- Auto-completion generation
- Help text generation

---

## Format Specification

### Basic Structure

```
COMMAND <command-name>
SYNOPSIS: <tool> <command> [options] [arguments]
DESCRIPTION: <brief description>
WORKFLOW: <workflow-reference> (optional)

ARGUMENTS:
  <arg-name>  <type>  [required|optional]  <description>

OPTIONS:
  --long-name, -s  <type>  [default: value]  <description>

EXIT CODES:
  <code>  <description>

EXAMPLE:
  $ <example-usage>

RELATED: (optional)
  - @CLI.other-command
  - @Workflow.workflow-name
---
```

**Separator**: Commands separated by `---` on its own line

---

## Sections

### Required Sections

**COMMAND**: Command name (kebab-case)
```
COMMAND init-spec
```

**SYNOPSIS**: Command usage pattern
```
SYNOPSIS: cypilot init-spec <slug> [options]
```

**DESCRIPTION**: Brief description (1-2 sentences)
```
DESCRIPTION: Initialize a new spec with DESIGN.md template
```

**ARGUMENTS**: Positional arguments (one per line)
```
ARGUMENTS:
  slug  <slug>  required  Spec identifier (lowercase-with-dashes)
  name  <string>  optional  Human-readable spec name
```

**OPTIONS**: Named options/flags (one per line)
```
OPTIONS:
  --template, -t  <string>  [default: standard]  Template to use
  --skip-validation  <boolean>  Skip architecture validation
  --verbose, -v  <boolean>  Enable verbose output
```

**EXIT CODES**: Exit codes and their meanings
```
EXIT CODES:
  0  Success
  1  General error
  2  Validation failure
  3  Workflow error
```

**EXAMPLE**: Usage examples (one or more)
```
EXAMPLE:
  $ cypilot init-spec user-authentication
  $ cypilot init-spec data-export --template minimal
  $ cypilot init-spec payment --skip-validation
```

### Optional Sections

**WORKFLOW**: Reference to Cypilot workflow
```
WORKFLOW: 05-init-spec
```

**RELATED**: Related commands/workflows
```
RELATED:
  - @CLI.validate-feature
  - @CLI.init-specs
  - @Workflow.05-init-spec
```

---

## Type System

### Supported Types

- `<string>` - Any text value
- `<number>` - Numeric value (integer or float)
- `<boolean>` - True/false flag
- `<path>` - File system path
- `<slug>` - Kebab-case identifier (lowercase-with-dashes)
- `<url>` - URL/URI
- `<email>` - Email address
- `<json>` - JSON string

### Type Constraints

Types can have constraints in description:
```
ARGUMENTS:
  port  <number>  required  Port number (1-65535)
  count  <number>  optional  Item count (positive integer)
```

---

## Syntax Rules

### Formatting Rules

1. **Command names**: kebab-case (e.g., `init-spec`, `validate-architecture`)
2. **Section headers**: UPPERCASE followed by colon
3. **One item per line**: Arguments and options on separate lines
4. **Indentation**: 2 spaces for items under sections
5. **Separator**: `---` on its own line between commands
6. **Required/optional**: Explicitly mark with keywords
7. **Defaults**: In square brackets `[default: value]`

### Option Format

```
--long-name, -s  <type>  [default: value]  <description>
```

- Long form: `--long-name` (required)
- Short form: `-s` (optional)
- Type: `<type>` (required)
- Default: `[default: value]` (optional)
- Description: text (required)

### Argument Format

```
<arg-name>  <type>  [required|optional]  <description>
```

- Name: lowercase, hyphens allowed
- Type: from supported types
- Required/optional: explicit keyword
- Description: text

---

## Linking Syntax

Reference other commands, workflows, or entities:

### Command References

```
@CLI.command-name              # Reference to another command
@CLI.command-name.--option     # Reference to specific option
@CLI.command-name.<arg-name>   # Reference to specific argument
```

### Workflow References

```
@Workflow.NN-workflow-name     # Reference to Cypilot workflow
@Workflow.adapter-config       # Reference to workflow file
```

### Spec References

```
@Feature.{slug}                # Reference to feature
@DomainModel.{TypeName}        # Reference to domain type
```

---

## Complete Example

```
COMMAND init-spec
SYNOPSIS: cypilot init-spec <slug> [options]
DESCRIPTION: Initialize a new spec with DESIGN.md template
WORKFLOW: 05-init-spec

ARGUMENTS:
  slug  <slug>  required  Spec identifier (lowercase-with-dashes)

OPTIONS:
  --template, -t  <string>  [default: standard]  Template to use (standard|minimal|full)
  --skip-validation  <boolean>  Skip architecture validation check
  --force  <boolean>  Overwrite existing spec directory

EXIT CODES:
  0  Spec initialized successfully
  1  File system error or invalid slug
  2  Architecture validation failed
  3  Spec directory already exists

EXAMPLE:
  $ cypilot init-spec user-authentication
  $ cypilot init-spec data-export --template minimal
  $ cypilot init-spec payment --skip-validation

RELATED:
  - @CLI.validate-feature
  - @CLI.init-specs
  - @Workflow.05-init-spec
---
```

---

## Validation Rules

### Required Elements

- ✅ COMMAND section with valid command name
- ✅ SYNOPSIS section with usage pattern
- ✅ DESCRIPTION section (non-empty)
- ✅ ARGUMENTS section (can be empty if no arguments)
- ✅ OPTIONS section (can be empty if no options)
- ✅ EXIT CODES section with at least code 0
- ✅ EXAMPLE section with at least one example

### Content Rules

- ✅ Command names must be kebab-case
- ✅ Types must be from supported types list
- ✅ Exit codes must be numeric (0-255)
- ✅ Examples must start with `$ `
- ✅ Required/optional keywords for arguments
- ✅ Defaults in square brackets format
- ✅ One argument/option per line

### Style Rules

- ✅ Section headers in UPPERCASE
- ✅ 2-space indentation for items
- ✅ Separator `---` between commands
- ✅ No trailing whitespace
- ✅ Consistent spacing

---

## Benefits for AI Agents

### Easy Parsing

Simple structure with clear sections:
```python
def parse_clispec(text):
    commands = text.split('---')
    for cmd_block in commands:
        sections = parse_sections(cmd_block)
        # sections['COMMAND'], sections['ARGUMENTS'], etc.
```

### Clear Semantics

- Explicit required/optional markers
- Type information for validation
- Exit codes for error handling
- Examples for understanding usage

### Workflow Integration

- Direct workflow references
- Command relationships via RELATED
- Integration with Cypilot methodology

### Tool Generation

From CLISPEC, generate:
- Help text (`--help`)
- Argument parsers
- Validation logic
- Auto-completion
- Documentation

---

## Usage in Cypilot

### In Adapter Configuration

CLISPEC is a built-in option for CLI API contracts:

```
Q4: API Contract Technology
Options:
  ...
  4. CLISPEC (for CLI tools)
  ...
```

### File Location

Standard location: `architecture/cli-specs/commands.clispec`

### Validation

```bash
# Validate CLISPEC format
cypilot validate-cli-specs

# Or custom validator
your-tool validate-clispec architecture/cli-specs/commands.clispec
```

### Linking from DESIGN.md

```markdown
## API Contracts

**Format**: CLISPEC
**Location**: `architecture/cli-specs/commands.clispec`

**Commands**:
- @CLI.init-spec - Initialize spec
- @CLI.validate-spec - Validate spec design
```

---

## Comparison with Alternatives

### vs. OpenAPI

- ✅ Simpler format (text vs. YAML/JSON)
- ✅ CLI-specific (not REST API)
- ✅ Human-readable in plain text
- ❌ Less tooling ecosystem

### vs. man pages

- ✅ Structured format (parseable)
- ✅ Machine-readable
- ✅ Workflow integration
- ❌ Not Unix standard

### vs. Markdown

- ✅ More structured
- ✅ Enforced sections
- ✅ Type system
- ❌ Less flexible

**Best for**: CLI tools in Cypilot projects where agent-readability is priority

---

## Implementation Notes

### Parser Implementation

Recommended approach:
1. Split by `---` separator
2. Parse each command block
3. Extract sections by header pattern
4. Parse arguments/options line by line
5. Validate structure

### Generator Implementation

From code to CLISPEC:
1. Extract command metadata
2. Format sections
3. Add examples
4. Generate separator

### Editor Support

Syntax highlighting:
- Section headers as keywords
- Types as types
- Commands as functions
- Comments with `#` prefix

---

## Version History

- **v1.0** (2026-01): Initial specification
  - Basic structure
  - Type system
  - Linking syntax
  - Validation rules

---

## References

- **Cypilot Methodology**: `AGENTS.md`
- **Adapter Guide**: `guides/ADAPTER.md`
- **Example Usage**: See `../cypilot-cli-adapter/AGENTS.md` for real-world CLISPEC

---

## License

This specification is part of the Cypilot (Spec-Driven Development) methodology.
