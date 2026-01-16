# Project Structure

**Version**: 1.0  
**Last Updated**: 2025-01-17  
**Purpose**: Define FDD project directory organization

---

## Root Structure

```
FDD/
├── .adapter/              # Project adapter (this directory)
│   ├── AGENTS.md         # Adapter navigation
│   └── specs/            # Adapter specifications
├── requirements/          # 22 structure requirement files
├── workflows/            # 22 workflow definition files
├── skills/               # FDD skills/tools
│   └── fdd/             # Unified FDD tool
├── images/              # Documentation assets
├── .fdd-config.json     # Project configuration
├── .gitignore
├── LICENSE
├── README.md            # Human-readable overview
├── AGENTS.md            # Core AI agent navigation
├── QUICKSTART.md        # Quick start guide
├── WORKFLOW.md          # Workflow overview
├── ADAPTER_GUIDE.md     # Adapter creation guide
├── CLISPEC.md           # CLI specification
└── fdd-flow-layers.drawio.svg  # Architecture diagram
```

---

## Core Directories

### `/requirements/`
- **Purpose**: Structure requirements for all FDD artifacts
- **Pattern**: `{artifact}-structure.md`
- **Examples**: 
  - `business-context-structure.md`
  - `overall-design-structure.md`
  - `feature-design-structure.md`
  - `adapter-structure.md`
- **Count**: 22 files

### `/workflows/`
- **Purpose**: Executable workflow definitions
- **Pattern**: `{workflow-name}.md`
- **Types**: Operation workflows, Validation workflows
- **Examples**:
  - `adapter-auto.md`
  - `design.md`, `design-validate.md`
  - `feature.md`, `feature-validate.md`
- **Count**: 22 files

### `/skills/`
- **Purpose**: Executable tools and skills
- **Structure**:
  ```
  skills/
  ├── SKILLS.md           # Skills registry
  └── fdd/               # FDD unified tool
      ├── SKILL.md       # Tool documentation
      ├── README.md      # Tool overview
      ├── scripts/
      │   └── fdd.py    # Main tool (4317 lines)
      └── tests/        # Test suite
          ├── test_validate.py
          ├── test_list_api.py
          └── test_read_search.py
  ```

---

## Adapter Structure

**Location**: `.adapter/` (customizable via `.fdd-config.json`)

```
.adapter/
├── AGENTS.md             # Adapter-specific navigation
└── specs/                # Project-specific specifications
    ├── tech-stack.md
    ├── project-structure.md
    ├── conventions.md
    ├── testing.md
    ├── build-deploy.md
    ├── domain-model.md
    └── patterns.md
```

---

## File Naming Conventions

**Markdown documentation**:
- Core docs: `SCREAMING_SNAKE.md` (README.md, AGENTS.md)
- Requirements: `kebab-case-structure.md`
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
