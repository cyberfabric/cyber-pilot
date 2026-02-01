# Tech Stack

**Version**: 2.0
**Last Updated**: 2026-02-01  
**Purpose**: Define technology stack for FDD project

---

## Languages

**Python 3**
- Primary language for all tooling
- Version: Python 3.6+ (standard library only)
- No runtime dependencies required

---

## Frameworks & Libraries

**Standard Library Only**
- `argparse` - Command-line interface
- `json` - Configuration and output
- `re` - Pattern matching and validation
- `pathlib` - File system operations
- `unittest` - Testing framework

**No external dependencies** - Project uses only Python standard library

---

## Tools

**Development**:
- Python interpreter (3.6+)
- Text editor / IDE
- Git for version control

**Testing**:
- `pipx` (recommended for isolated CLI tooling)
- `pytest` (executed via `pipx`) for repository test suite in `tests/`
- `pytest-cov` (executed via `pipx`) for coverage runs

---

## Source

**Discovered from**:
- `skills/fdd/scripts/fdd/cli.py` - Main CLI entry point
- `tests/` - Repository test suite (17 test files)
- `Makefile` - Test and coverage targets
- Import analysis - Only standard library imports

---

## Validation Checklist

Agent MUST verify before implementation:
- [ ] Python 3.6+ is available
- [ ] Runtime dependencies are standard library only
- [ ] Test tooling is available via `pipx`
- [ ] Code uses type hints from `typing` module

**Self-test**:
- [ ] Did I check all criteria?
- [ ] Are examples concrete and project-specific?
- [ ] Do commands work on target platform?
