# Code Conventions

## File Naming

- **Python files**: `snake_case.py`
- **Test files**: `test_*.py` prefix
- **Markdown docs**: `UPPERCASE.md` for major docs, `lowercase.md` for specs

## Project Structure

```
skills/cypilot/scripts/cypilot/    # Main CLI package
├── __init__.py
├── __main__.py
├── cli.py                       # CLI entry point and commands
├── constants.py                 # Shared constants
└── utils/                       # Utility modules
    ├── artifacts_meta.py        # artifacts.json parsing
    ├── codebase.py              # Code file parsing
    ├── context.py               # Global context management
    ├── document.py              # Document utilities
    ├── files.py                 # File operations
    ├── language_config.py       # Language-specific configs
    ├── parsing.py               # Markdown parsing
    └── template.py              # Template parsing
```

## Code Style

- **Docstrings**: Module, class, and public function docstrings required
- **Type hints**: All function signatures should have type hints
- **Line length**: ~100 characters preferred
- **Imports**: Standard library, third-party, then local imports

## Testing Conventions

- Test files mirror source structure in `tests/`
- Test classes named `Test{ClassName}` or `Test{SpecName}`
- Test methods named `test_{behavior_being_tested}`
- Use `TemporaryDirectory` for file system tests

## Cypilot Markers

- **Format**: `@cpt-{kind}:{id}:{phase}`
- **Example**: `@cpt-fr:cpt-prd-1:impl`
- **Phases**: `p1`, `p2`, etc. (implementation phases)

---

**Source**: Auto-detected from project scan
**Last Updated**: 2026-02-03
