# Project Structure

## Root Directory

```
FDD/
├── .cypilot-adapter/          # Project adapter (this directory)
├── .cypilot-config.json       # Cypilot configuration
├── AGENTS.md                 # Root navigation rules
├── README.md                 # Project documentation
├── Makefile                  # Build automation
├── LICENSE                   # License file
│
├── architecture/             # Design artifacts
│   ├── PRD.md               # Product Requirements Document
│   ├── DESIGN.md            # Technical Design
│   ├── specs/
│   │   └── DECOMPOSITION.md      # Specs Manifest
│   └── ADR/
│       └── general/         # Architecture Decision Records
│
├── kits/                  # Kit packages
│   └── sdlc/                # SDLC kit
│       ├── artifacts/       # Artifact templates
│       ├── codebase/        # Code rules
│       └── guides/          # Usage guides
│
├── workflows/                # Cypilot workflows
│   ├── generate.md          # Generation workflow
│   ├── analyze.md          # Analysis/validation workflow
│   └── adapter.md           # Adapter workflow
│
├── requirements/             # Cypilot requirements specs
│   ├── execution-protocol.md
│   ├── adapter-structure.md
│   ├── artifacts-registry.md
│   ├── traceability.md
│   └── ...
│
├── schemas/                  # JSON schemas
│   ├── artifacts.schema.json
│   └── cypilot-template-frontmatter.schema.json
│
├── skills/                   # Cypilot skills
│   └── cypilot/
│       ├── SKILL.md         # Skill definition
│       └── scripts/
│           └── cypilot/      # CLI package
│
├── tests/                    # Test suite
│   ├── test_*.py            # Test modules
│   └── __init__.py
│
├── scripts/                  # Utility scripts
│   ├── check_coverage.py
│   └── score_comparison_matrix.py
│
└── guides/                   # User guides
    ├── ADAPTER.md
    └── TAXONOMY.md
```

---

## CLI Package Structure

```
skills/cypilot/scripts/cypilot/
├── __init__.py              # Package init (version info)
├── __main__.py              # Entry point for `python -m cypilot`
├── cli.py                   # Main CLI (2398 lines)
│                            # - All subcommands
│                            # - Agent config generation
│                            # - Validation logic
├── constants.py             # Shared constants
│                            # - ARTIFACTS_REGISTRY_FILENAME
│                            # - CONFIG_FILENAME
│                            # - ADAPTER_AGENTS_FILENAME
│
└── utils/                   # Utility modules
    ├── __init__.py          # Re-exports all utilities
    ├── artifacts_meta.py    # artifacts.json parsing
    │                        # - Kit, Artifact, SystemNode
    │                        # - ArtifactsMeta class
    ├── codebase.py          # Code file parsing
    │                        # - CodeFile, ScopeMarker
    │                        # - Cypilot marker detection
    ├── context.py           # Global context
    │                        # - CypilotContext
    │                        # - LoadedKit
    ├── document.py          # Document utilities
    ├── files.py             # File operations
    │                        # - find_project_root
    │                        # - find_adapter_directory
    │                        # - load_artifacts_registry
    ├── language_config.py   # Language-specific configs
    │                        # - Comment syntax detection
    ├── parsing.py           # Markdown parsing
    │                        # - Section splitting
    │                        # - ID extraction
    └── template.py          # Template parsing (1211 lines)
                             # - Template class
                             # - TemplateBlock
                             # - Artifact validation
```

---

## Kit Package Structure

```
kits/sdlc/
├── README.md                 # Kit documentation
├── artifacts/
│   ├── README.md            # Artifacts overview
│   ├── PRD/
│   │   ├── template.md      # PRD template with markers
│   │   ├── rules.md         # Generation/validation rules
│   │   ├── checklist.md     # Review checklist
│   │   └── examples/
│   │       └── example.md   # Canonical example
│   ├── DESIGN/              # Same structure
│   ├── DECOMPOSITION/            # Same structure
│   ├── SPEC/             # Same structure
│   └── ADR/                 # Same structure
├── codebase/
│   ├── rules.md             # Code implementation rules
│   └── checklist.md         # Code review checklist
└── guides/
    ├── QUICKSTART.md
    ├── GREENFIELD.md
    ├── BROWNFIELD.md
    └── MONOLITH.md
```

---

## Agent Integration Directories

```
.cursor/
├── commands/                 # Cursor slash commands
│   ├── cypilot.md
│   ├── cypilot-adapter.md
│   ├── cypilot-generate.md
│   └── cypilot-analyze.md
└── rules/                    # Cursor rules

.claude/
├── commands/                 # Claude slash commands
└── settings.local.json       # Claude settings

.windsurf/
├── workflows/                # Windsurf workflows
└── skills/
    └── cypilot/
        └── SKILL.md

.github/
├── copilot-instructions.md   # GitHub Copilot instructions
└── prompts/                  # Copilot prompts
```

---

## Key Files

| File | Purpose |
|------|---------|
| `.cypilot-config.json` | Cypilot config (adapter path) |
| `.cypilot-adapter/artifacts.json` | Artifact registry |
| `.cypilot-adapter/AGENTS.md` | Navigation rules |
| `AGENTS.md` | Root navigation (extends) |
| `Makefile` | Build/test commands |

---

**Source**: Project directory analysis
**Last Updated**: 2026-02-03
