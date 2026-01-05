# Workflow: Configure Agent for FDD

**ID**: `config-agent-tools`  
**Phase**: Phase 0 (Pre-Project Setup)  
**Purpose**: Set up AI agent to use FDD natively

---

## Overview

This workflow configures your AI agent to work natively with FDD by creating:

1. **Rules file** - Tells agent to read FDD adapter
2. **Workflow wrappers** - Shortcuts to call FDD workflows

**Goal**: Agent reads adapter AGENTS.md and uses FDD workflows naturally.

**When to use**: After creating FDD adapter.

---

## Prerequisites

- ✅ FDD adapter exists at `spec/FDD-Adapter/AGENTS.md`

**If adapter not found**:
```
❌ STOP: Run workflow adapter-config first
```

---

## Questions

### Q1: Which AI agent?

```
Which AI agent will you use?

Options:
  1. Windsurf Cascade
  2. Cursor AI
  3. Cline
  4. Aider
  5. Custom (specify)
  6. Multiple

Your choice: ___
```

**If Multiple**: Ask which agents (comma-separated)

**Store as**: `AGENT_LIST[]`

**Built-in specifications**:
- **Windsurf Cascade**: `.windsurf/rules.md`, `.windsurf/workflows/` (separate wrapper files)
- **Cursor AI**: `.cursorrules` (single file with inline workflow references)
- **Cline**: `.clinerules` (single file with inline workflow references)
- **Aider**: `.aider.conf.yml` (YAML config with inline workflow references)

**Wrapper Support**:
- **Separate files**: Windsurf Cascade
- **Inline references**: Cursor AI, Cline, Aider

---

### Q2: Custom Agent Specification (if Custom selected)

```
For custom agent, specify how to configure it:

1. Rules file location: ___ (e.g., .myagent/rules.md or .myagentrules)
2. Supports separate workflow files? ___ (yes/no)
3. Workflow wrappers location: ___ (e.g., .myagent/workflows/ or N/A if no)
4. Format: ___ (markdown / yaml / json / plain text)

Example configurations:
- Windsurf: rules=.windsurf/rules.md, workflows=.windsurf/workflows/, format=markdown
- Cursor: rules=.cursorrules, workflows=N/A, format=markdown
```

**Store as**: `AGENT_SPEC[agent_name]`

---

### Q3: Confirm Configuration

**Display Summary**:
```
Agent Configuration Summary:
────────────────────────────────────
{For each agent in AGENT_LIST}
Agent: {AGENT_NAME}
Files to create:
{If Windsurf}
- .windsurf/rules.md (points to spec/FDD-Adapter/AGENTS.md)
- .windsurf/workflows/ (separate workflow wrappers for all FDD workflows)
{End if}
{If Cursor}
- .cursorrules (single file with inline workflow references)
{End if}
{If Cline}
- .clinerules (single file with inline workflow references)
{End if}
{If Aider}
- .aider.conf.yml (single YAML file with inline workflow references)
{End if}
{If Custom and supports separate files}
- {rules_file} (points to spec/FDD-Adapter/AGENTS.md)
- {workflows_dir}/ (separate workflow wrappers for all FDD workflows)
{End if}
{If Custom and single file}
- {rules_file} (includes inline workflow references)
{End if}
{End for}

Proceed with configuration? (y/n)
```

**Expected Outcome**: User confirms or cancels

---

## Workflow Steps

### Step 1: Validate Prerequisites

```bash
if [ ! -f "spec/FDD-Adapter/AGENTS.md" ]; then
  echo "❌ ERROR: FDD adapter not found"
  echo "Run: adapter-config"
  exit 1
fi
```

---

### Step 2: Create Agent Files

**Requirement**: Follow agent specification to create files

For each agent:

**If agent = Windsurf Cascade**:
```bash
mkdir -p .windsurf/workflows
```

**If agent = Cursor AI**:
```bash
# Cursor uses single .cursorrules file (no directory needed)
```

**If agent = Cline**:
```bash
# Cline uses single .clinerules file (no directory needed)
```

**If agent = Aider**:
```bash
# Aider uses .aider.conf.yml file (no directory needed)
```

**If agent = Custom**:
```bash
# Follow AGENT_SPEC[agent_name] from Q2
# Create directories/files as specified by user
```

---

### Step 3: Generate Content

**Requirement**: Follow agent specification to generate content

#### For Windsurf Cascade:

Create `.windsurf/rules.md`:
```markdown
# Windsurf Cascade Rules for {PROJECT_NAME}

**Read and follow**: `spec/FDD-Adapter/AGENTS.md`

This file contains all FDD rules, workflows, and conventions.

## Quick Reference

- **FDD Core**: `spec/FDD/AGENTS.md`
- **FDD Adapter**: `spec/FDD-Adapter/AGENTS.md`
- **FDD Workflows**: `spec/FDD/workflows/AGENTS.md`
- **Workflow Wrappers**: See `.windsurf/workflows/`

**Always start by reading `spec/FDD-Adapter/AGENTS.md`**
```

#### For Cursor AI:

Create `.cursorrules`:
```markdown
# Cursor AI Rules for {PROJECT_NAME}

**Read and follow**: `spec/FDD-Adapter/AGENTS.md`

This file contains all FDD rules, workflows, and conventions.

## FDD Workflows

To use FDD workflows:
- `@spec/FDD/workflows/adapter-config.md` - Create adapter
- `@spec/FDD/workflows/01-init-project.md` - Initialize project
- `@spec/FDD/workflows/02-validate-architecture.md` - Validate architecture
- `@spec/FDD/workflows/05-init-feature.md` - Create feature
- `@spec/FDD/workflows/06-validate-feature.md` - Validate feature
- Full list: `@spec/FDD/workflows/AGENTS.md`

**Always start by reading `spec/FDD-Adapter/AGENTS.md`**
```

#### For Cline:

Create `.clinerules`:
```markdown
# Cline Rules for {PROJECT_NAME}

**Read and follow**: `spec/FDD-Adapter/AGENTS.md`

FDD workflows: `spec/FDD/workflows/AGENTS.md`

**Always start by reading `spec/FDD-Adapter/AGENTS.md`**
```

#### For Aider:

Create `.aider.conf.yml`:
```yaml
# Aider configuration for {PROJECT_NAME}

# Read FDD adapter first
read:
  - spec/FDD-Adapter/AGENTS.md
  - spec/FDD/AGENTS.md
  - spec/FDD/workflows/AGENTS.md

# Custom instructions
instructions: |
  Always read spec/FDD-Adapter/AGENTS.md before starting work.
  Follow FDD workflows in spec/FDD/workflows/.
```

#### For Custom Agent:

Follow `AGENT_SPEC[agent_name]` from Q2 to generate appropriate files.

---

### Step 4: Generate Workflow Wrappers

**For agents with separate workflow file support** (Windsurf Cascade, Custom agents with wrapper support):

**Discovery**: Scan `spec/FDD/workflows/` for all workflow files dynamically:
```bash
# Find all workflow .md files (exclude AGENTS.md and README.md)
cd spec/FDD/workflows
find . -maxdepth 1 -name "*.md" ! -name "AGENTS.md" ! -name "README.md" -type f | sort
```

**Mapping Rules** (workflow filename → wrapper filename):
```bash
# For each workflow file, generate wrapper name with "fdd-" prefix:
# - Remove number prefix: "01-init-project.md" → "fdd-init-project.md"
# - Keep name with prefix: "adapter-config.md" → "fdd-adapter-config.md"
# - Handle sub-numbers: "10-1-openspec-code-validate.md" → "fdd-openspec-code-validate.md"

# Bash logic:
for file in $(find . -maxdepth 1 -name "*.md" ! -name "AGENTS.md" ! -name "README.md" -type f | sort); do
  filename=$(basename "$file")
  # Remove leading digits and hyphens (e.g., "01-", "10-1-"), then add "fdd-" prefix
  base_name=$(echo "$filename" | sed 's/^[0-9]*-*[0-9]*-*//')
  wrapper_name="fdd-$base_name"
  echo "$wrapper_name → spec/FDD/workflows/$filename"
done
```

**Template for each wrapper**:
```markdown
# {WORKFLOW_TITLE}

**FDD Workflow**: `spec/FDD/workflows/{workflow-filename}`

---

## Execute

```
Follow @spec/FDD/workflows/{workflow-filename}
```

---

**Note**: This wrapper calls FDD workflow. All logic is in `spec/FDD/workflows/{workflow-filename}`
```

**Workflow Title Extraction**:
```bash
# Extract title from first markdown header in workflow file
head -1 "spec/FDD/workflows/$filename" | sed 's/^# //'
```

**Agent-Specific Wrapper Locations**:
- **Windsurf Cascade**: `.windsurf/workflows/fdd-{workflow-name}.md`
- **Custom with wrapper support**: `{AGENT_SPEC.workflows_dir}/fdd-{workflow-name}.md`

**For agents without wrapper support** (Cursor AI, Cline, Aider): Skip this step - they use inline workflow references in single rules file

---

### Step 5: Show Summary

```
═══════════════════════════════
FDD AGENT SETUP COMPLETE
═══════════════════════════════

Agent Files Created:
{For each agent}
✓ {AGENT_NAME}
  {If Windsurf}
  - Rules: .windsurf/rules.md
  - Workflows: .windsurf/workflows/ ({WORKFLOW_COUNT} wrappers)
  {End if}
  {If Cursor}
  - Rules: .cursorrules (inline workflow references)
  {End if}
  {If Cline}
  - Rules: .clinerules (inline workflow references)
  {End if}
  {If Aider}
  - Config: .aider.conf.yml (inline workflow references)
  {End if}
  {If Custom and supports separate files}
  - Rules: {rules_file}
  - Workflows: {workflows_dir}/ ({WORKFLOW_COUNT} wrappers)
  {End if}
  {If Custom and single file}
  - Rules: {rules_file} (inline workflow references)
  {End if}
{End for}

Next Steps:
1. Read your agent's configuration file
2. Agent will automatically read spec/FDD-Adapter/AGENTS.md
3. Use FDD workflows via @spec/FDD/workflows/{workflow-id}.md

═══════════════════════════════
```

---

## Completion Criteria

- [ ] User selected agent(s) (Q1)
- [ ] Custom agent spec provided if needed (Q2)
- [ ] User confirmed configuration (Q3)
- [ ] Agent directories created per spec
- [ ] Rules file generated for each agent
- [ ] Workflow wrappers generated (for agents with separate file support: all FDD workflows)
- [ ] Summary displayed with created files

---

## Example: Windsurf Setup

### .windsurf/rules.md

```markdown
# Windsurf Cascade Rules for My Project

**Read and follow**: `spec/FDD-Adapter/AGENTS.md`

This file contains all FDD rules, workflows, and conventions.

---

## Quick Reference

- **FDD Core**: `spec/FDD/AGENTS.md`
- **FDD Adapter**: `spec/FDD-Adapter/AGENTS.md`
- **FDD Workflows**: `spec/FDD/workflows/AGENTS.md`
- **Workflow Wrappers**: See `.windsurf/workflows/`

---

**Always start by reading `spec/FDD-Adapter/AGENTS.md`**
```

### .windsurf/workflows/init-project.md

```markdown
# Initialize Project

**FDD Workflow**: `spec/FDD/workflows/01-init-project.md`

---

## Execute

```
Follow @spec/FDD/workflows/01-init-project.md
```

---

**Note**: This wrapper calls FDD workflow. All logic is in `spec/FDD/workflows/01-init-project.md`
```

---

## References

- **FDD Adapter**: `spec/FDD-Adapter/AGENTS.md`
- **FDD Workflows**: `spec/FDD/workflows/AGENTS.md`
