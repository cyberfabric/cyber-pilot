# Build & Deploy

**Version**: 2.1
**Last Updated**: 2026-02-01
**Purpose**: Define build, deployment, and execution procedures

---

## Build Process

**No build required** - Pure Python project

**Why no build**:
- Python is interpreted language
- No compilation step needed
- No bundling or packaging required
- No runtime dependencies to install

---

## Execution

### Direct Execution

**FDD Tool**:
```bash
# From project root (as module)
python3 -m skills.fdd.scripts.fdd.cli <command> [options]
```

**Examples**:
```bash
# Discover adapter
python3 -m skills.fdd.scripts.fdd.cli adapter-info --root .

# Validate artifact
python3 -m skills.fdd.scripts.fdd.cli validate --artifact architecture/DESIGN.md

# Search IDs
python3 -m skills.fdd.scripts.fdd.cli list-ids --artifact architecture/PRD.md

# Self-check templates
python3 -m skills.fdd.scripts.fdd.cli self-check
```

---

## Makefile Targets

### Testing

| Target | Description |
|--------|-------------|
| `make test` | Run all tests |
| `make test-verbose` | Run tests with verbose output |
| `make test-quick` | Run fast tests only (skip slow integration tests) |
| `make test-coverage` | Run tests with coverage report (requires 90% minimum) |

### Validation

| Target | Description |
|--------|-------------|
| `make validate` | Validate core methodology feature |
| `make validate-feature FEATURE=name` | Validate specific feature DESIGN.md |
| `make validate-code-feature FEATURE=name` | Validate code traceability for specific feature |
| `make validate-examples` | Validate requirements examples |
| `make self-check` | Validate SDLC examples against templates |

### Code Quality

| Target | Description |
|--------|-------------|
| `make vulture` | Scan for dead code (report only) |
| `make vulture-ci` | Scan for dead code (fails if findings) |

### Setup & Maintenance

| Target | Description |
|--------|-------------|
| `make install` | Install Python dependencies (pytest via pipx) |
| `make clean` | Remove Python cache files |
| `make help` | Show all available targets |

### Coverage Requirements

**Minimum coverage**: 90%

Coverage is enforced via `scripts/check_coverage.py`:
```bash
make test-coverage
# Fails if coverage < 90%
```

---

## Dependencies

**Runtime**: Python 3.6+

**Runtime dependencies**: None (standard library only)

**Dev/Test tooling** (via pipx):
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `vulture` - Dead code detection

**Installation**:
```bash
make install
# or manually:
pipx install pytest
pipx inject pytest pytest-cov
```

---

## Project Configuration

### .fdd-config.json

**Location**: Project root

**Purpose**: Configure FDD adapter location

**Format**:
```json
{
  "fddAdapterPath": ".adapter"
}
```

**Optional fields**:
```json
{
  "fddAdapterPath": ".adapter",
  "fddCorePath": ".fdd"
}
```

---

## Directory Setup

### For New Projects

**Minimal setup**:
- Create `.fdd-config.json` at project root with `fddAdapterPath` pointing to the adapter directory.
- Create `{adapter-directory}/AGENTS.md` with `**Extends**: ../AGENTS.md`.

---

## Version Control

### Git

**Ignored files** (from `.gitignore`):
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
htmlcov/
coverage.json
```

**Tracked files**:
- All `.py` source files
- All `.md` documentation
- `.fdd-config.json`
- Test files

---

## Deployment

**Current**: No deployment needed (tool runs locally)

**Future considerations**:
- Package as Python module
- Distribute via PyPI
- Create CLI wrapper script

---

## Development Workflow

### Quick Start

```bash
python3 --version

# Install dev dependencies
make install

# Run tests to verify setup
make test

# Use FDD tool
python3 -m skills.fdd.scripts.fdd.cli adapter-info --root .
```

### Making Changes

```bash
# 1. Make code changes in skills/fdd/scripts/fdd/

# 2. Add/update tests in tests/

# 3. Run tests with coverage
make test-coverage

# 4. Check for dead code
make vulture

# 5. Commit changes
git add .
git commit -m "Description"
```

---

## Platform Compatibility

**Supported platforms**:
- ✅ macOS
- ✅ Linux
- ✅ Windows (with Python 3.6+)

**Requirements**:
- Python 3.6 or higher
- Standard library only (no external dependencies)
- File system access (read/write)

---

## Source

**Discovered from**:
- `Makefile` - All build targets
- Import analysis (standard library only)
- README.md execution examples
- .gitignore patterns

---

## Validation Checklist

Agent MUST verify before implementation:
- [ ] Python 3.6+ is available
- [ ] No build step required
- [ ] Tool runs as module: `python3 -m skills.fdd.scripts.fdd.cli`
- [ ] Tests run via `make test` (preferred)
- [ ] Coverage meets 90% minimum via `make test-coverage`
- [ ] Test tooling is available via `pipx`

**Self-test**:
- [ ] Did I check all criteria?
- [ ] Are commands correct for this platform?
- [ ] Do paths match project structure?
