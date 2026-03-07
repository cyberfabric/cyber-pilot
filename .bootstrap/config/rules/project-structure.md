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
├── .bootstrap/                # Cypilot adapter directory (cypilot_path = ".bootstrap")
│   ├── .core/                # Read-only core (from cache, do not edit)
│   │   ├── architecture/
│   │   ├── requirements/
│   │   ├── schemas/
│   │   ├── skills/
│   │   └── workflows/
│   ├── .gen/                 # Auto-generated aggregates only (do not edit)
│   │   ├── AGENTS.md
│   │   ├── SKILL.md
│   │   └── README.md
│   ├── config/               # User-editable configuration + generated kit outputs
│   │   ├── AGENTS.md         # Custom navigation rules
│   │   ├── SKILL.md          # Custom skill extensions
│   │   ├── core.toml         # Project config
│   │   ├── artifacts.toml    # Artifacts registry
│   │   ├── rules/            # Project rules (per-topic, auto-config)
│   │   └── kits/sdlc/        # Generated kit outputs (constraints, artifacts/, scripts/)
│   └── kits/sdlc/            # User-editable kit data
│       ├── blueprints/       # User-editable blueprints
│       └── conf.toml         # Kit version metadata
│
├── .github/
│   └── workflows/ci.yml      # GitHub Actions CI (single source of truth)
│
├── AGENTS.md                 # Root navigation rules
├── CONTRIBUTING.md           # Development guide
├── README.md                 # Project documentation
├── Makefile                  # Build automation + local CI
├── pyproject.toml            # PyPI package config
│
├── architecture/             # Design artifacts
│   ├── PRD.md
│   ├── DESIGN.md
│   ├── DECOMPOSITION.md
│   ├── features/             # Feature specs
│   └── specs/                # Technical specs (CDSL, CLISPEC, etc.)
│
├── kits/                     # Kit packages (canonical source)
│   └── sdlc/
│       ├── blueprints/
│       ├── guides/
│       ├── scripts/
│       └── blueprint_hashes.toml
│
├── skills/                   # Cypilot skills (canonical source)
│   └── cypilot/
│       ├── SKILL.md
│       └── scripts/cypilot/  # CLI package (skill engine)
│
├── src/                      # Proxy package (canonical source)
│   └── cypilot_proxy/
│       ├── cli.py
│       ├── resolve.py
│       └── cache.py
│
├── tests/                    # Test suite (35 test modules)
│   ├── test_*.py
│   ├── conftest.py
│   └── _test_helpers.py
│
├── scripts/                  # Utility scripts
│   ├── check_coverage.py
│   ├── check_versions.py
│   └── score_comparison_matrix.py
│
└── guides/                   # User guides
    ├── STORY.md
    ├── TAXONOMY.md
    └── MIGRATION.md
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
| `.bootstrap/config/artifacts.toml` | Artifact registry |
| `.bootstrap/config/AGENTS.md` | Custom navigation rules |
| `.bootstrap/.gen/AGENTS.md` | Generated navigation rules |
| `.github/workflows/ci.yml` | CI pipeline (single source of truth) |
| `AGENTS.md` | Root navigation (routes to above) |
| `Makefile` | Build/test/CI commands |
