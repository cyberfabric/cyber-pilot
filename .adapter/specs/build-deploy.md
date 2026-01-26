# Build & Deploy

**Version**: 1.0  
**Last Updated**: 2025-01-17  
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
# From project root
python3 skills/fdd/scripts/fdd.py <command> [options]

# From skills/fdd directory
python3 scripts/fdd.py <command> [options]
```

**Examples**:
```bash
# Discover adapter
python3 skills/fdd/scripts/fdd.py adapter-info --root .

# Validate artifact
python3 skills/fdd/scripts/fdd.py validate --artifact architecture/DESIGN.md

# Search IDs
python3 skills/fdd/scripts/fdd.py list-ids --artifact architecture/PRD.md
```

---

## Testing

### Run Tests

```bash
make test

# Coverage
make test-coverage
```

---

## Dependencies

**Runtime**: Python 3.6+

**Runtime dependencies**: None (standard library only)

**Dev/Test tooling**:
- `pipx`
- `pytest` and `pytest-cov` (installed and executed via `pipx`)

**Verification**:
```bash
# Check Python version
python3 --version

# Should be Python 3.6 or higher
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

# Run tests to verify setup
make test

# Use FDD tool
python3 skills/fdd/scripts/fdd.py adapter-info --root .
```

### Making Changes

```bash
# 1. Make code changes in skills/fdd/scripts/fdd.py

# 2. Add/update tests in tests/

# 3. Run tests
make test

# 4. Commit changes
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
- Absence of build configuration files
- Import analysis (standard library only)
- README.md execution examples
- .gitignore patterns

---

## Validation Checklist

Agent MUST verify before implementation:
- [ ] Python 3.6+ is available
- [ ] No build step required
- [ ] Tool runs directly with `python3 scripts/fdd.py`
- [ ] Tests run via `make test` (preferred)
- [ ] Test tooling is available via `pipx`

**Self-test**:
- [ ] Did I check all criteria?
- [ ] Are commands correct for this platform?
- [ ] Do paths match project structure?
