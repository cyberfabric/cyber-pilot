# FDD Adapter: Bootstrap (Minimal Initialization)

**Type**: Operation  
**Role**: Any  
**Artifact**: `{adapter-directory}/AGENTS.md` (minimal)

---

**ALWAYS open and follow**: `../requirements/core.md` WHEN editing this file

ALWAYS open and follow `../requirements/workflow-execution.md` WHEN executing this workflow

## Purpose

Create minimal adapter for new projects - just `AGENTS.md` with `Extends` declaration.

**No specs yet** - specs will be added later through:
- Design decisions → trigger-based evolution
- Manual updates → `adapter-manual` workflow
- Project scanning → `adapter-auto` workflow

---

## Requirements

**ALWAYS open and follow**: `../requirements/adapter-structure.md`

Extract:
- Minimal AGENTS.md format
- Bootstrap validation criteria (100/100 if Extends present)

---

## Prerequisites

**Prerequisites**:
- [ ] Project repository exists - validate: Check .git directory exists
- [ ] Write permissions - validate: Can create directories and files

**No other prerequisites** - This is typically first workflow

---

## Steps

### 1. Choose Adapter Location and Name

Ask user to select adapter directory and name:

**Directory name** (customizable):
- Default: `FDD-Adapter` (recommended for consistency)
- Custom: `.fdd-adapter`, `project-adapter`, etc. (any name)

**Location options**:
1. `{name}/` at project root (recommended, e.g., `/FDD-Adapter/`)
2. `spec/{name}/` (for technical projects, e.g., `spec/FDD-Adapter/`)
3. `docs/{name}/` (for documentation-focused projects)
4. `guidelines/{name}/` (alternative)
5. Custom parent directory

**Default**: `/FDD-Adapter/` (default name at root)

**Note**: Directory name is stored in `.fdd-config.json` as `fddAdapterPath`

Store as: `ADAPTER_DIR`

### 2. Calculate Relative Path

Calculate path from `ADAPTER_DIR` to FDD core:

```yaml
If /FDD-Adapter/:
  relative_path = ../FDD/AGENTS.md

If spec/FDD-Adapter/:
  relative_path = ../..//FDD/AGENTS.md

If docs/FDD-Adapter/:
  relative_path = ../..//FDD/AGENTS.md

If custom/{path}/FDD-Adapter/:
  Calculate: relative path to /FDD/AGENTS.md
```

Store as: `RELATIVE_PATH`

### 3. Get Project Name

Ask user for project name or detect from:
- Repository directory name
- package.json `name` field
- pyproject.toml `[project] name`
- Cargo.toml `[package] name`

Store as: `PROJECT_NAME`

### 4. Show Summary

```
═══════════════════════════════════════════════
Minimal Adapter Bootstrap

Location: {ADAPTER_DIR}/
Project: {PROJECT_NAME}
Extends: {RELATIVE_PATH}
Config path: {relative} (in .fdd-config.json)

Files to create:
  - .fdd-config.json (project root)
  - AGENTS.md (minimal, no specs)

Note: Specs will be added later through:
  - Design workflow triggers
  - Manual updates (adapter-manual)
  - Auto-scan (adapter-auto)
═══════════════════════════════════════════════

Proceed? [Yes] [No] [Change Location]
```

### 5. Create .fdd-config.json

Calculate relative adapter path from project root:
```yaml
If ADAPTER_DIR = "/FDD-Adapter":
  relative = "FDD-Adapter"
  
If ADAPTER_DIR = "spec/FDD-Adapter":
  relative = "spec/FDD-Adapter"
  
If ADAPTER_DIR = "docs/FDD-Adapter":
  relative = "docs/FDD-Adapter"
```

Create config at project root:
```json
{
  "fddAdapterPath": "{relative}"
}
```

Store as: `{project-root}/.fdd-config.json`

### 6. Create Directory

```bash
mkdir -p {ADAPTER_DIR}/FDD-Adapter/
```

### 7. Create Minimal AGENTS.md

```markdown
# FDD Adapter: {PROJECT_NAME}

**Extends**: `{RELATIVE_PATH}`
```

### 8. Verify

Check:
- Config exists: `{project-root}/.fdd-config.json`
- Config valid JSON
- Config contains: `"fddAdapterPath": "{relative}"`
- Directory exists: `{ADAPTER_DIR}/FDD-Adapter/`
- File exists: `{ADAPTER_DIR}/FDD-Adapter/AGENTS.md`
- File contains: `**Extends**: {RELATIVE_PATH}`

### 9. Run Validation

**Execute**: `adapter-validate` workflow

```yaml
Validation will:
  1. Check .fdd-config.json exists and valid
  2. Locate adapter using config
  3. Detect Phase 1 (Bootstrap)
  4. Check 4 requirements:
     - .fdd-config.json exists ✓
     - fddAdapterPath points to valid directory ✓
     - AGENTS.md exists ✓
     - Extends declaration ✓
  5. Score: 100/100
  6. Output to chat
```

Expected result:
```
## Validation: FDD Adapter (Bootstrap)

Location: {ADAPTER_DIR}
Phase: Bootstrap (Minimal)
Score: 100/100
Status: PASS ✅

Minimal adapter validated. No specs required yet.
```

---

## Validation

Automatically runs `adapter-validate` at completion

---

## Next Steps

**Recommended**:
- `business-context` - Start business requirements
- `design` - Start architecture design
  - When design completed → Adapter evolution triggered
  
**Optional**:
- `adapter-auto` - Scan project for existing patterns (if codebase exists)
- `adapter-manual` - Manually add specifications

---

## Examples

### Example Output

```
✓ Created: /FDD-Adapter/
✓ Created: /FDD-Adapter/AGENTS.md

Content:
# FDD Adapter: Acronis MCP Server

**Extends**: `../FDD/AGENTS.md`

Validation: 100/100 (PASS)

Next: Run 'design' workflow to start architecture design
```
