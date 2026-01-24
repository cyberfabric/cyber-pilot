# FDD Quick Start

**Learn FDD in 10 minutes with real prompts and examples**

This Quickstart shows examples in a Windsurf-friendly style (slash commands like `/fdd-adr`).
You can apply the same flow in any agent by opening the corresponding workflow files under `workflows/`.

---

## What You'll Learn

1. **Exact prompts to type** - Copy-paste into your AI chat
2. **Complete example** - Task management API from start to finish
3. **Common scenarios** - What to do when requirements change
4. **Working with existing docs** - Use what you already have

---

## The Basics

FDD = **Design First, Code Second**

```
1. Business Context
   ↓ (validated)
2. ADR + Overall Design
   ↓ (validated)
3. Features Manifest
   ↓ (validated)
4. Feature Design
   ↓ (validated)
5. Implementation plan (optional)
   ↓ (validated)
6. Implementation
   ↓ (validated)
7. Code
```

**Key principle**: If code contradicts design, fix design first, then regenerate code.

Learn what each artifact means: [guides/TAXONOMY.md](guides/TAXONOMY.md)

---

## Live Example

[Taskman (FDD example project)](https://github.com/cyberfabric/fdd-examples-taskman) — a complete task management project with the full FDD artifact set and implementation.

---

## Prerequisites

Before starting with FDD, you need:

### 1. Git (Required)

FDD uses Git submodules to include the framework in your project.

**Check if installed:**
```bash
git --version
```

**If not installed:**
- **macOS**: `brew install git` or download from [git-scm.com](https://git-scm.com)
- **Linux**: `sudo apt install git` or `sudo yum install git`
- **Windows**: Download from [git-scm.com](https://git-scm.com)

### 2. IDE with AI Agent (Required)

FDD requires an IDE with integrated AI coding assistant to execute workflows interactively.

Prefer agents that support:
- Large context windows (for reading design/spec files)
- Reliable reasoning (for validation workflows)
- Fast modes (for codebase scanning and navigation)

**Recommended IDEs with AI agents:**

**Option 1: Windsurf (Recommended)**
- Full FDD support with Claude/GPT models
- Built-in agent for interactive workflows
- Download: [codeium.com/windsurf](https://codeium.com/windsurf)

**Option 2: VSCode + Continue/Cody**
- VSCode with Continue extension (multiple providers)
- VSCode with Cody extension
- Multiple model support

**Option 3: Cursor**
- Multiple provider support (flagship/reasoning/fast model classes)
- Native AI integration
- Download: [cursor.sh](https://cursor.sh)

**Option 4: JetBrains + AI Assistant**
- IntelliJ IDEA, PyCharm, WebStorm with AI Assistant
- Multiple model support


---

## What is FDD?

**FDD (Feature-Driven Design)** is a methodology for architecting software through structured documentation.

---

## Complete Example: Task Management API

Let's use this section to set up FDD in your project.
After Step 2.5, continue in the guides.

### Step 1: Add FDD to Your Project (2 minutes)

**What it does**: Setup FDD Framework

**Option A: Git Project (recommended)**
```bash
# In your project root
git submodule add https://github.com/cyberfabric/fdd FDD
git submodule update --init --recursive
```

**Option B: Non-Git Project**
```bash
# Clone FDD into your project
cd your-project
git clone https://github.com/cyberfabric/fdd FDD
```

**Result**: `/FDD/` folder in your project root

---

### Step 2: Create Project AGENTS.md (1 minute, optional but recommended)

**What it does**: Links your project to FDD

**Create file** `AGENTS.md` in project root:
```markdown
# Project AI Agent Instructions

ALWAYS open and follow `/FDD/AGENTS.md`
```

**Result**: Root `AGENTS.md` created with FDD reference

---

### Step 2.5: Generate Agent Integration Files (1 minute, optional)

This creates agent-specific proxy files that redirect back to the canonical FDD workflows and the `fdd` skill.

```bash
python3 FDD/skills/fdd/scripts/fdd.py init
python3 FDD/skills/fdd/scripts/fdd.py agent-workflows --agent windsurf
python3 FDD/skills/fdd/scripts/fdd.py agent-skills --agent windsurf
```

**After this step, you can use FDD directly from your agent chat**:

**Workflow commands (from chat)**

Once the workflow proxies are generated, you can trigger workflows by name from the chat (the exact UX depends on your IDE/agent).

Examples:
```text
/fdd-adapter
/fdd-business-context
/fdd-design
/fdd-features
/fdd-feature
/fdd-feature-implement
/fdd-feature-changes
```

Each of these opens a small proxy file that redirects the agent to the canonical workflow under `FDD/workflows/`.

**Tool/skill commands (from chat)**

Once the skill proxy is generated, you can ask your agent to run `fdd` commands directly (validation + search are JSON-output, machine-friendly).

Examples:
```text
fdd help
fdd validate help

fdd adapter info

fdd validate skip code traceability

fdd get ids from design 
fdd search postgres in design

fdd where-defined fdd-yourproj-req-some-id
fdd where-used fdd-yourproj-req-some-id
```

**Why this is powerful (tool + agent together)**

You type short intent like the examples above. The agent:
- Runs the precise `fdd` command under the hood (with correct flags/paths)
- Reads the JSON output
- Turns it into next steps (what to fix, which workflow to run, where the ID lives)

Examples:
```text
fdd validate
# Agent reads FAIL report and tells you exactly which artifact/section failed and what workflow to run next.

fdd where-defined fdd-yourproj-req-some-id
# Agent finds the canonical definition and can open that section and help you edit it safely.

fdd agent-workflows windsurf
# Agent updates the workflow proxies after you updated the FDD submodule.
```

Your agent will execute these via the underlying Python entrypoint, but from chat you only need to type `fdd ...`.

**Update agent workflow proxies via the tool/skill**

If you update the FDD submodule (new workflows appear, names change, etc.), just regenerate the proxies:
```text
fdd agent-workflows windsurf
fdd agent-skills windsurf
```

**Supported agents**:
- `windsurf`
- `cursor`
- `claude`
- `copilot`

---

## Next

Continue with the guide that matches your situation:

- Greenfield (new project): [guides/GREENFIELD.md](guides/GREENFIELD.md)
- Brownfield (existing code/docs): [guides/BROWNFIELD.md](guides/BROWNFIELD.md)

Modular monolith (modules inside one repo/deployable): [guides/MONOLITH.md](guides/MONOLITH.md)

Adapter guide: [guides/ADAPTER.md](guides/ADAPTER.md)

Learn what each artifact means: [guides/TAXONOMY.md](guides/TAXONOMY.md)

