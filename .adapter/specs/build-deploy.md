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
- No external dependencies to install

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
python3 skills/fdd/scripts/fdd.py list-ids --artifact architecture/BUSINESS.md
```

---

## Testing

### Run Tests

```bash
# From skills/fdd directory
python3 -m unittest discover -s tests -p 'test_*.py'

# Verbose output
python3 -m unittest discover -s tests -p 'test_*.py' -v

# Specific test file
python3 -m unittest tests.test_validate
```

---

## Dependencies

**Runtime**: Python 3.6+

**External dependencies**: None (standard library only)

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
```bash
# Create adapter directory
mkdir -p .adapter

# Create config
echo '{"fddAdapterPath": ".adapter"}' > .fdd-config.json

# Create minimal AGENTS.md
cat > .adapter/AGENTS.md << 'EOF'
# FDD Adapter: ProjectName

**Extends**: `../AGENTS.md`
EOF
```

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
# 1. Clone/navigate to FDD project
cd /path/to/FDD

# 2. Verify Python version
python3 --version

# 3. Run tests to verify setup
cd skills/fdd
python3 -m unittest discover -s tests -p 'test_*.py'

# 4. Use FDD tool
cd ../..
python3 skills/fdd/scripts/fdd.py adapter-info --root .
```

### Making Changes

```bash
# 1. Make code changes in skills/fdd/scripts/fdd.py

# 2. Add/update tests in skills/fdd/tests/

# 3. Run tests
cd skills/fdd
python3 -m unittest discover -s tests -p 'test_*.py'

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
- [ ] Tests run with standard unittest
- [ ] No external dependencies needed

**Self-test**:
- [ ] Did I check all criteria?
- [ ] Are commands correct for this platform?
- [ ] Do paths match project structure?
