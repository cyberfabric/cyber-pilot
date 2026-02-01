# Project Structure

**Version**: 2.0
**Last Updated**: 2026-02-01
**Purpose**: Define FDD project directory organization

---

## Root Structure

```
FDD/
├── .adapter/              # Project adapter (this directory)
│   ├── AGENTS.md         # Adapter navigation
│   ├── artifacts.json    # Artifact registry
│   └── specs/            # Adapter specifications
├── architecture/          # Architecture artifacts
├── requirements/          # 11 requirement files
├── workflows/            # 6 workflow files
├── rules/                # Rules packages
│   ├── core/            # Core FDD rules
│   └── sdlc/            # SDLC artifact rules
├── skills/               # FDD skills/tools
│   └── fdd/             # Unified FDD tool
├── schemas/              # JSON schemas
├── tests/                # Pytest tests (17 files)
├── guides/               # User guides
├── images/              # Documentation assets
├── .fdd-config.json     # Project configuration
├── .gitignore
├── LICENSE
├── README.md            # Human-readable overview
├── AGENTS.md            # Core AI agent navigation
├── QUICKSTART.md        # Quick start guide
├── Makefile             # Build automation
└── fdd-flow-layers.drawio.svg  # Architecture diagram
```

---

## Core Directories

### `/requirements/`
- **Purpose**: Content requirements for FDD framework
- **Count**: 10 files
- **Files**:
  - `execution-protocol.md` - Workflow execution rules
  - `adapter-structure.md` - Adapter validation rules
  - `adapter-triggers.md` - Adapter evolution triggers
  - `rules-format.md` - Rules package format
  - `template.md` - Template requirements
  - `FDL.md` - Flow Description Language spec
  - `traceability.md` - ID traceability rules
  - `artifacts-registry.md` - Artifact registry rules
  - `extension.md` - Extension requirements
  - `agent-compliance.md` - Agent compliance rules

### `/workflows/`
- **Purpose**: Executable workflow definitions
- **Pattern**: `{workflow-name}.md`
- **Count**: 6 files
- **Files**:
  - `README.md` - Workflow overview
  - `fdd.md` - Core FDD workflow
  - `generate.md` - Artifact generation
  - `validate.md` - Artifact validation
  - `adapter.md` - Adapter management
  - `rules.md` - Rules management

### `/rules/`
- **Purpose**: Rules packages for artifact validation and generation
- **Structure**:
  ```
  rules/
  ├── core/                    # Core FDD rules
  │   ├── README.md
  │   ├── template/           # Template rules
  │   ├── checklist/          # Checklist rules
  │   └── examples/           # Example rules
  └── sdlc/                    # SDLC artifact rules
      ├── artifacts/          # Per-artifact rules
      │   ├── PRD/
      │   │   ├── template.md
      │   │   ├── checklist.md
      │   │   ├── rules.md
      │   │   └── examples/
      │   ├── DESIGN/
      │   ├── FEATURES/
      │   ├── ADR/
      │   └── FEATURE/
      └── codebase/           # Code-level rules
          ├── rules.md
          └── checklist.md
  ```

### `/skills/`
- **Purpose**: Executable tools and skills
- **Structure**:
  ```
  skills/
  ├── SKILLS.md           # Skills registry
  └── fdd/               # FDD unified tool
      ├── SKILL.md       # Tool documentation
      ├── README.md      # Tool overview
      ├── fdd.clispec    # CLI specification
      └── scripts/
          └── fdd/
              ├── __init__.py
              ├── cli.py          # Main CLI entry point
              ├── constants.py    # Shared constants
              ├── utils/          # Utility modules
              └── validation/     # Validation modules
  ```

### `/schemas/`
- **Purpose**: JSON Schema definitions
- **Files**:
  - `artifacts.schema.json` - Artifact registry schema
  - `fdd-template-frontmatter.schema.json` - Template frontmatter schema

### `/tests/`
- **Purpose**: Pytest test suite
- **Count**: 17 test files
- **Pattern**: `test_*.py`
- **Key tests**:
  - `test_validate.py` - Validation tests
  - `test_cli_integration.py` - CLI integration tests
  - `test_core_structure.py` - Core structure tests
  - `test_workflow_parsing.py` - Workflow parsing tests
  - `test_files_utils.py` - File utility tests

---

## Adapter Structure

**Location**: `.adapter/` (customizable via `.fdd-config.json`)

```
.adapter/
├── AGENTS.md             # Adapter-specific navigation
├── artifacts.json        # Artifact registry
└── specs/                # Project-specific specifications
    ├── tech-stack.md
    ├── project-structure.md
    ├── conventions.md
    ├── testing.md
    ├── build-deploy.md
    ├── domain-model.md
    ├── patterns.md
    └── language-config.md
```

---

## File Naming Conventions

**Markdown documentation**:
- Core docs: `SCREAMING_SNAKE.md` (README.md, AGENTS.md)
- Requirements: `kebab-case.md`
- Workflows: `kebab-case.md`
- Specs: `kebab-case.md`

**Python code**:
- Scripts: `snake_case.py`
- Tests: `test_*.py`

---

## Source

**Discovered from**:
- Root directory listing
- `find` command scan
- Analysis of file patterns

---

## Validation Checklist

Agent MUST verify before implementation:
- [ ] New files follow naming conventions
- [ ] Specs go in `.adapter/specs/`
- [ ] Workflows reference correct paths
- [ ] Structure matches project layout

**Self-test**:
- [ ] Did I check all criteria?
- [ ] Are paths absolute or correctly relative?
- [ ] Do examples match actual project structure?
