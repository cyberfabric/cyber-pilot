---
cypilot: true
type: project-rule
topic: project-structure
generated-by: auto-config
version: 1.0
---

# Project Structure


<!-- toc -->

- [Root Directory](#root-directory)
- [CLI Package Structure](#cli-package-structure)
- [Kit Package Structure](#kit-package-structure)
- [Key Files](#key-files)

<!-- /toc -->

## Root Directory

```
./
├── cypilot/                   # Cypilot directory (v3 layout)
│   ├── .core/                # Read-only core (from cache, do not edit)
│   │   ├── architecture/
│   │   ├── requirements/
│   │   ├── schemas/
│   │   ├── skills/
│   │   └── workflows/
│   ├── .gen/                 # Auto-generated (do not edit)
│   │   ├── AGENTS.md
│   │   ├── SKILL.md
│   │   └── kits/sdlc/
│   └── config/               # User-editable configuration
│       ├── AGENTS.md         # Custom navigation rules
│       ├── SKILL.md          # Custom skill extensions
│       ├── core.toml         # Project config
│       ├── artifacts.toml    # Artifacts registry
│       ├── rules/            # Project rules (per-topic)
│       └── kits/sdlc/blueprints/
│
├── AGENTS.md                 # Root navigation rules
├── README.md                 # Project documentation
├── Makefile                  # Build automation
├── LICENSE                   # License file
│
├── architecture/             # Design artifacts
│   ├── PRD.md
│   ├── DESIGN.md
│   ├── DECOMPOSITION.md
│   └── specs/
│
├── kits/                     # Kit packages (source)
│   └── sdlc/
│       ├── blueprints/
│       ├── guides/
│       └── scripts/
│
├── workflows/                # Cypilot workflows (source)
│   ├── generate.md
│   └── analyze.md
│
├── requirements/             # Cypilot requirements specs (source)
│   ├── execution-protocol.md
│   ├── auto-config.md
│   └── ...
│
├── schemas/                  # JSON schemas (source)
│   ├── artifacts.schema.json
│   └── core-config.schema.json
│
├── skills/                   # Cypilot skills (source)
│   └── cypilot/
│       ├── SKILL.md
│       └── scripts/cypilot/  # CLI package
│
├── src/                      # Proxy package (source)
│   └── cypilot_proxy/
│       ├── cli.py
│       ├── resolve.py
│       └── cache.py
│
├── tests/                    # Test suite
│   ├── test_*.py
│   └── conftest.py
│
├── scripts/                  # Utility scripts
│   ├── check_coverage.py
│   └── score_comparison_matrix.py
│
└── guides/                   # User guides
    ├── STORY.md
    └── TAXONOMY.md
```

## CLI Package Structure

```
skills/cypilot/scripts/cypilot/
├── __init__.py              # Package init (version info)
├── __main__.py              # Entry point for `python -m cypilot`
├── cli.py                   # Main CLI — command dispatch only
├── constants.py             # Shared constants and regex patterns
│
├── commands/                # One module per CLI subcommand
│   ├── validate.py
│   ├── init.py
│   ├── adapter_info.py
│   ├── agents.py
│   ├── toc.py
│   └── ...
│
└── utils/                   # Shared utility modules
    ├── __init__.py          # Re-exports all utilities
    ├── artifacts_meta.py    # artifacts.toml parsing → ArtifactsMeta
    ├── codebase.py          # Code file parsing → CodeFile, ScopeMarker
    ├── constraints.py       # constraints.toml parsing → KitConstraints
    ├── context.py           # CypilotContext singleton
    ├── document.py          # Document utilities
    ├── files.py             # File operations, project root discovery
    ├── language_config.py   # Language-specific configs
    ├── parsing.py           # Markdown parsing, section splitting
    ├── toc.py               # Table of Contents generation
    └── toml_utils.py        # TOML read/write helpers (stdlib tomllib)
```

## Kit Package Structure

```
kits/sdlc/
├── README.md
├── artifacts/
│   ├── PRD/
│   │   ├── template.md
│   │   ├── rules.md
│   │   ├── checklist.md
│   │   └── examples/
│   ├── DESIGN/              # Same structure
│   ├── DECOMPOSITION/
│   ├── FEATURE/
│   └── ADR/
├── codebase/
│   ├── rules.md
│   └── checklist.md
└── guides/
```

## Key Files

| File | Purpose |
|------|---------|
| `cypilot/config/artifacts.toml` | Artifact registry |
| `cypilot/config/AGENTS.md` | Custom navigation rules |
| `cypilot/.gen/AGENTS.md` | Generated navigation rules |
| `AGENTS.md` | Root navigation (routes to above) |
| `Makefile` | Build/test commands |
