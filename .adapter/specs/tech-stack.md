# Tech Stack

**Version**: 1.0  
**Last Updated**: 2025-01-17  
**Purpose**: Define technology stack for FDD project

---

## Languages

**Python 3**
- Primary language for all tooling
- Version: Python 3.6+ (standard library only)
- No external dependencies required

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
- `unittest` (Python standard library)
- No test runners needed beyond Python itself

---

## Source

**Discovered from**:
- `skills/fdd/scripts/fdd.py` - Main tool (4317 lines)
- `skills/fdd/tests/*.py` - Test files
- Import analysis - Only standard library imports

---

## Validation Checklist

Agent MUST verify before implementation:
- [ ] Python 3.6+ is available
- [ ] No external dependencies installed
- [ ] Standard library modules are sufficient
- [ ] Code uses type hints from `typing` module

**Self-test**:
- [ ] Did I check all criteria?
- [ ] Are examples concrete and project-specific?
- [ ] Do commands work on target platform?
