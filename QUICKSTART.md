<!-- @fdd-change:fdd-fdd-feature-core-methodology-change-quickstart-docs:ph-1 -->
<!-- fdd-begin fdd-fdd-feature-core-methodology-flow-user-onboard:ph-1:inst-open-quickstart -->
# FDD Quick Start

**Learn FDD in 10 minutes with real prompts and examples**
<!-- fdd-end   fdd-fdd-feature-core-methodology-flow-user-onboard:ph-1:inst-open-quickstart -->

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
2. Overall Design
   ↓ (validated)
3. Features Manifest
   ↓ (validated)
4. Feature Design
   ↓ (validated)
5. Changes/Tasks
   ↓ (validated)
6. Implementation
   ↓ (validated)
7. Code
```

**Key principle**: If code contradicts design, fix design first, then regenerate code.

---

<!-- fdd-begin fdd-fdd-feature-core-methodology-flow-user-onboard:ph-1:inst-check-prereqs -->
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

**Recommended IDEs with AI agents:**

**Option 1: Windsurf (Recommended)**
- Full FDD support with Claude/GPT models
- Built-in agent for interactive workflows
- Download: [codeium.com/windsurf](https://codeium.com/windsurf)

**Option 2: VSCode + Continue/Cody**
- VSCode with Continue extension (GPT-4, Claude)
- VSCode with Cody extension (Claude)
- Multiple model support

**Option 3: Cursor**
- Claude Sonnet 3.5, GPT-4o support
- Native AI integration
- Download: [cursor.sh](https://cursor.sh)

**Option 4: JetBrains + AI Assistant**
- IntelliJ IDEA, PyCharm, WebStorm with AI Assistant
- Multiple model support

<!-- fdd-end   fdd-fdd-feature-core-methodology-flow-user-onboard:ph-1:inst-check-prereqs -->

---

<!-- fdd-begin fdd-fdd-feature-core-methodology-flow-user-onboard:ph-1:inst-read-overview -->
## What is FDD?

**FDD (Feature-Driven Documentation)** is a methodology for architecting software through structured documentation.
<!-- fdd-end   fdd-fdd-feature-core-methodology-flow-user-onboard:ph-1:inst-read-overview -->

---

## Complete Example: Task Management API

Let's build a simple task management API step-by-step with actual prompts.

**Three scenarios covered in each step:**
1. 🆕 **New Project** - Starting from scratch
2. 📚 **Existing Project + Docs** - Have architecture docs, API specs, etc.
3. 💻 **Existing Project (Code Only)** - Have working code, no design docs

Choose the path that matches your situation.

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

### Step 3: Start with Business Context (15 minutes)

**What it does**: Describe what you're building (no tech details yet)

**Recommended model**: Thinking model (e.g., Claude Opus Thinking, Claude Sonnet Thinking)

---

<!-- fdd-begin fdd-fdd-feature-core-methodology-flow-user-onboard:ph-1:inst-follow-quickstart -->
#### 🆕 New Project

**Prompt**:
```
fdd create business requirements for task management service
```
<!-- fdd-end   fdd-fdd-feature-core-methodology-flow-user-onboard:ph-1:inst-follow-quickstart -->

<!-- fdd-begin fdd-fdd-feature-core-methodology-flow-user-onboard:ph-1:inst-create-first-artifact -->
**What happens**:
- Agent runs `workflows/business-context.md`
- Reads `requirements/business-context-structure.md`
- Agent asks interactive questions with proposed answers:
<!-- fdd-end   fdd-fdd-feature-core-methodology-flow-user-onboard:ph-1:inst-create-first-artifact -->
  - **Q1**: System vision - proposes from README.md if exists
  - **Q2**: Key actors (3-5) - proposes based on vision
  - **Q3**: Core capabilities (3-7) - proposes based on vision/actors
  - **Q4**: Additional context (optional)
- **Creates artifact**: `architecture/BUSINESS.md`

---

#### 📚 Existing Project + Docs

**Prompt**:
```
fdd generate business context from existing docs:
- architecture: docs/architecture.md
- product requirements: docs/product-spec.md
```

**What happens**:
- Agent runs `workflows/business-context.md`
- Reads `requirements/business-context-structure.md`
- Agent reads your existing documentation
- Extracts vision, actors, capabilities
- Maps to FDD structure
- **Creates artifact**: `architecture/BUSINESS.md`

---

#### 💻 Existing Project (Code Only)

**Prompt**:
```
fdd analyze codebase and create business requirements
```

**What happens**:
- Agent runs `workflows/business-context.md`
- Reads `requirements/business-context-structure.md`
- Agent analyzes code structure, endpoints, data models
- Infers actors from user types/roles in code
- Infers capabilities from main features
- Asks you to confirm and refine
- **Creates artifact**: `architecture/BUSINESS.md`

**Result**: `architecture/BUSINESS.md` created

---

### Step 4: Validate Business Context (5 minutes)

**What it does**: Ensures business requirements are complete and clear

**Recommended model**: Reasoning model (e.g., GPT o1, GPT 4.5 Medium Reasoning Fast) - strictly follows validation instructions

**All scenarios use same prompt**:
```
fdd validate architecture/BUSINESS.md
```
<!-- fdd-begin fdd-fdd-feature-core-methodology-flow-user-onboard:ph-1:inst-validate-artifact -->
### Step 4: Validate Business Context (5 minutes)

**What it does**: Ensures business requirements are complete and clear

**Recommended model**: Reasoning model (e.g., GPT o1, GPT 4.5 Medium Reasoning Fast) - strictly follows validation instructions

**All scenarios use same prompt**:
```
fdd validate architecture/BUSINESS.md
```
<!-- fdd-end   fdd-fdd-feature-core-methodology-flow-user-onboard:ph-1:inst-validate-artifact -->

**What happens**:
- Agent runs `workflows/business-validate.md`
- Reads `requirements/business-context-structure.md`
- Agent performs systematic deterministic validation using skills
- Validates BUSINESS.md structure and completeness
- Must score ≥90/100
- Checks all actors and capabilities are properly defined
- Works same for all scenarios

**Result**: Business context approved or issues found to fix

---

### Step 5: Create Overall Design (1 hour)

**What it does**: Defines architecture, domain model, and API contracts

**Recommended model**: Thinking model (e.g., Claude Opus Thinking, Claude Sonnet Thinking)

---

#### 🆕 New Project

**Prompt**:
```
fdd create overall design for task management service
```

**What happens**:
- Agent runs `workflows/design.md`
- Reads `requirements/overall-design-structure.md`
- Agent asks interactive questions with proposed answers:
  - **Q1**: Architecture style (Monolithic, Microservices, Layered, Hexagonal, Event-Driven)
  - **Q2**: Key components (3-7 main system components)
  - **Q3**: Technical stack (technologies, frameworks, libraries)
  - **Q4**: Design principles (3-5 architectural principles)
  - **Q5**: NFRs (performance, security, scalability)
- **Creates artifacts**: 
  - `architecture/DESIGN.md` (domain model, API contracts)
  - `architecture/ADR.md` (ADR-0001: Initial Architecture)

---

#### 📚 Existing Project + Docs

**Prompt**:
```
fdd generate design from existing docs:
- architecture: docs/architecture.md
- api specs: docs/openapi.yaml
- data model: docs/database-schema.md
```

**What happens**:
- Agent runs `workflows/design.md`
- Reads `requirements/overall-design-structure.md`
- Agent reads existing technical docs
- Maps to FDD DESIGN.md structure
- **Creates artifacts**:
  - `architecture/DESIGN.md`
  - `architecture/ADR.md` (ADR-0001: Initial Architecture)

---

#### 💻 Existing Project (Code Only)

**Prompt**:
```
fdd reverse engineer design from codebase
```

**What happens**:
- Agent runs `workflows/design.md`
- Reads `requirements/overall-design-structure.md`
- Agent analyzes code: models, controllers, services, APIs
- Extracts domain model from classes/types
- Extracts API contracts from routes/controllers
- Infers architecture from code structure
- **Creates artifacts**:
  - `architecture/DESIGN.md`
  - `architecture/ADR.md` (ADR-0001: Initial Architecture)

**What you get** (example snippet):
```markdown
## C. Technical Architecture

### Domain Model

@DomainModel.Task:
- id: UUID
- title: string
- description: string
- status: "todo" | "in_progress" | "done"
- assigneeId: UUID (optional)
- projectId: UUID
- createdAt: timestamp
- updatedAt: timestamp

@DomainModel.Project:
- id: UUID
- name: string
- ownerId: UUID
- createdAt: timestamp

### API Contracts

@API.POST:/tasks - Create task
@API.GET:/tasks - List tasks
@API.GET:/tasks/:id - Get task
@API.PUT:/tasks/:id - Update task
@API.DELETE:/tasks/:id - Delete task
```

**Result**: `architecture/DESIGN.md` and `architecture/ADR.md` created

---

### Step 6: Validate Design (5 minutes)

**Recommended model**: Reasoning model (e.g., GPT o1, GPT 4.5 Medium Reasoning Fast) - strictly follows validation instructions

**All scenarios use same prompt**:
```
fdd validate overall design
```

**What happens**:
- Agent runs `workflows/design-validate.md`
- Reads `requirements/overall-design-structure.md` and `requirements/adr-structure.md`
- Agent performs systematic deterministic validation using skills
- Validates structure and completeness
- Must score ≥90/100
- Auto-validates ADR.md
- Works same for all scenarios

**Result**: Design approved or issues found to fix

---

### Step 7: Decompose Design into Features (5 minutes)

**Recommended model**: Thinking model (e.g., Claude Opus Thinking, Claude Sonnet Thinking)

**All scenarios use same prompt**:
```
fdd extract features from design
```

**What happens**:
- Agent runs `workflows/features.md`
- Reads `requirements/features-manifest-structure.md`
- Agent analyzes DESIGN.md (created in Step 5)
- Decomposes design into discrete features
- Identifies features from capabilities and API contracts
- **Creates artifact**: `architecture/features/FEATURES.md` (features manifest)

**Note**: Works same for all scenarios - always based on DESIGN.md

**What you get**:
```markdown
## Features

### feature-task-crud
**Priority**: CRITICAL  
**Status**: ⏳ NOT_STARTED  
**Description**: Create, read, update, delete tasks

### feature-project-management
**Priority**: HIGH  
**Status**: ⏳ NOT_STARTED  
**Description**: Organize tasks into projects
```

**Result**: `architecture/features/FEATURES.md` created

---

### Step 8: Design First Feature (30 minutes)

**Recommended model**: Thinking model (e.g., Claude Opus Thinking, Claude Sonnet Thinking)

---

#### 🆕 New Project

**Prompt**:
```
fdd design feature task-crud
```

**What happens**:
- Agent runs `workflows/feature.md`
- Reads `requirements/feature-design-structure.md` and `requirements/FDL.md`
- Agent asks interactive questions per section:
  - **Section A**: Feature purpose and scope boundaries
  - **Section B**: Actor flows (main flow, alternative flows) in FDL
  - **Section C**: Algorithms (business logic, state transitions) in FDL
  - **Section D**: State machines (if applicable) in FDL
  - **Section E**: Technical details (DB schemas, API endpoints, integrations)
  - **Section F**: Requirements mapping from DESIGN.md
  - **Section G**: Test scenarios (acceptance criteria, edge cases)
- Uses FDL (plain English), no code
- References domain model from Overall Design
- **Creates artifact**: `architecture/features/feature-task-crud/DESIGN.md`

---

#### 📚 Existing Project + Docs

**Prompt**:
```
fdd design feature task-crud based on:
- user stories: docs/user-stories.md
- feature specs: docs/features/task-management.md
```

**What happens**:
- Agent runs `workflows/feature.md`
- Reads `requirements/feature-design-structure.md` and `requirements/FDL.md`
- Agent reads existing feature documentation
- Maps user stories to actor flows
- Creates feature DESIGN.md in FDD format
- **Creates artifact**: `architecture/features/feature-task-crud/DESIGN.md`

---

#### 💻 Existing Project (Code Only)

**Prompt**:
```
fdd reverse engineer feature task-crud from code
```

**What happens**:
- Agent runs `workflows/feature.md`
- Reads `requirements/feature-design-structure.md` and `requirements/FDL.md`
- Agent analyzes code for task CRUD operations
- Infers actor flows from controllers/handlers
- Creates feature DESIGN.md documenting what code does
- **Creates artifact**: `architecture/features/feature-task-crud/DESIGN.md`

**What you get** (example):
```markdown
## B. Actor Flows (FDL)

### Flow 1: Create Task

1. User submits task form with title, description, projectId
2. System validates title is not empty
3. System validates projectId exists in database
4. IF project not found:
   - Return "Project not found" error (404)
5. System creates Task record with status "todo"
6. System returns created task to User

### Flow 2: List Tasks

1. User requests task list with optional filters (projectId, status)
2. System queries database with filters
3. System returns paginated task list to User

### Flow 3: Update Task

1. User submits update with taskId and changed fields
2. System finds Task by id
3. IF task not found:
   - Return "Task not found" error (404)
4. System updates allowed fields (title, description, status, assigneeId)
5. System saves Task to database
6. System returns updated task to User
```

**Result**: `architecture/features/feature-task-crud/DESIGN.md` created

---

### Step 9: Validate Feature (5 minutes)

**Recommended model**: Reasoning model (e.g., GPT o1, GPT 4.5 Medium Reasoning Fast) - strictly follows validation instructions

**All scenarios use same prompt**:
```
fdd validate feature task-crud
```

**What happens**:
- Agent runs `workflows/feature-validate.md`
- Reads `requirements/feature-design-structure.md` and `requirements/FDL.md`
- Agent performs systematic deterministic validation using skills
- Validates feature design
- Must score 100/100 + 100% completeness
- Checks FDL usage, no code in design
- Works same for all scenarios

**Result**: Feature approved or issues found to fix

---

### Step 10: Create Implementation Plan (15 minutes)

**Recommended model**: Thinking model (e.g., Claude Opus Thinking, Claude Sonnet Thinking)

---

#### 🆕 New Project

**Prompt**:
```
fdd create implementation plan for feature-task-crud
```

**What happens**:
- Agent runs `workflows/feature-changes.md`
- Reads `requirements/feature-changes-structure.md`
- Agent decomposes feature design into atomic implementation changes
- Creates task checklists from scratch
- **Creates artifact**: `architecture/features/feature-task-crud/CHANGES.md`

---

#### 📚 & 💻 Existing Projects

**Prompt**:
```
fdd create implementation plan for feature-task-crud
Consider existing code structure
```

**What happens**:
- Agent runs `workflows/feature-changes.md`
- Reads `requirements/feature-changes-structure.md`
- Agent analyzes existing codebase
- Decomposes feature into changes that fit existing architecture
- May include refactoring tasks if needed
- **Creates artifact**: `architecture/features/feature-task-crud/CHANGES.md`

**What you get**:
```markdown
## Change 001: Task API Endpoints

**Purpose**: Implement REST API endpoints for task operations

**Tasks**:
- [ ] Create POST /tasks endpoint
- [ ] Create GET /tasks endpoint with filtering
- [ ] Create GET /tasks/:id endpoint
- [ ] Create PUT /tasks/:id endpoint
- [ ] Create DELETE /tasks/:id endpoint
- [ ] Add request validation
- [ ] Add error handling
- [ ] Write integration tests

**Status**: NOT_STARTED
```

**Result**: `architecture/features/feature-task-crud/CHANGES.md` created

---

### Step 11: Implement (varies)

**Recommended model**: Thinking model (e.g., Claude Opus Thinking, Claude Sonnet Thinking)

---

#### 🆕 New Project

**Prompt**:
```
fdd implement change 001 from feature-task-crud
```

**What happens**:
- Agent runs `workflows/feature-change-implement.md`
- Reads feature DESIGN.md and CHANGES.md
- Agent creates new files/modules
- Implements from scratch following DESIGN.md
- Writes tests

---

#### 📚 & 💻 Existing Projects

**Prompt**:
```
fdd implement change 001 from feature-task-crud
Update existing code
```

**What happens**:
- Agent runs `workflows/feature-change-implement.md`
- Reads feature DESIGN.md and CHANGES.md
- Agent modifies existing files
- Integrates with current codebase
- Updates or adds tests
- May refactor if needed

**Result**: Code implemented, tests written

---

### Step 12: Final Validation

**Recommended model**: Reasoning model (e.g., GPT o1, GPT 4.5 Medium Reasoning Fast) - strictly follows validation instructions

**All scenarios use same prompt**:
```
fdd validate feature code task-crud
```

**What happens**:
- Agent runs `workflows/feature-code-validate.md`
- Reads feature DESIGN.md and implementation code
- Agent performs systematic deterministic validation using skills
- Validates code matches design
- Checks all flows implemented
- Verifies no design contradictions
- Works same for all scenarios

**Result**: Feature complete ✅

---

### Step 13: Create or Update Project Adapter (optional, can run anytime)

**What it does**: Configure tech stack details for your project

**When to use**: Run this workflow anytime you need to define or update tech stack configuration. Not required for basic FDD workflows.

**Prompt to type**:
```
fdd create adapter
```

**What happens**:
- Agent runs `workflows/adapter.md`
- Creates `spec/FDD-Adapter/AGENTS.md` (minimal, with Extends only)
- Creates `specs/domain-model.md` and `specs/api-contracts.md` placeholders
- You configure tech stack details as needed
- **Creates artifact**: `spec/FDD-Adapter/AGENTS.md` and spec files

**Result**: `spec/FDD-Adapter/` folder with configuration

---

**Auto-Discovery Alternative**: For existing projects, use `adapter-auto`:

**Prompt**:
```
fdd auto-scan adapter
```

**What it does**:
- Agent runs `workflows/adapter-auto.md`
- Automatically scans your existing project:
  - Documentation (README, ARCHITECTURE, CONTRIBUTING)
  - ADRs (architecture decision records)
  - Config files (package.json, docker-compose.yml, etc.)
  - Code structure (frameworks, patterns, conventions)
  - API definitions (OpenAPI, GraphQL schemas)
  - Domain models (entities, schemas)
- Generates adapter specs from discovered patterns:
  - `specs/tech-stack.md` (detected technologies, frameworks, libraries)
  - `specs/domain-model.md` (extracted from code entities/schemas)
  - `specs/api-contracts.md` (from OpenAPI/GraphQL definitions)
  - `specs/patterns.md` (architectural patterns found)
  - `specs/conventions.md` (code style, naming conventions)
  - `specs/build-deploy.md` (CI/CD, deployment instructions)
  - `specs/testing.md` (test frameworks, strategies)

**When to use**: Perfect for existing projects with established codebase. Saves time by discovering tech stack automatically instead of manual configuration.

**Note**: This workflow can be executed at any point in your FDD process, whenever you need to formalize tech stack specifications.

---

## Common Scenarios

### Scenario 1: Requirements Changed (Business Context)

**Situation**: Need to add "Task Comments" capability

**Prompts**:
```
1. fdd update business context - add Task Comments capability

2. fdd validate business context

3. fdd update overall design - add Comment domain model and API

4. fdd validate overall design

5. fdd add feature task-comments

6. fdd design feature task-comments

7. fdd validate feature task-comments
```

**Result**: New feature added to roadmap

---

### Scenario 2: Design Changed (Overall Design)

**Situation**: Realized Task needs "priority" field

**Prompts**:
```
1. fdd update Task model - add priority field

2. fdd validate overall design

3. fdd update feature task-crud - add priority handling

4. fdd validate feature task-crud

5. fdd update implementation plan - add priority migration
```

**Result**: Design updated, feature updated, implementation plan adjusted

---

### Scenario 3: Feature Design Changed

**Situation**: Need to add validation - tasks must have assignee

**Prompts**:
```
1. fdd update feature task-crud - add assignee validation

2. fdd validate feature task-crud

3. fdd update implementation plan - add validation task

4. fdd implement validation

5. fdd validate feature code task-crud
```

**Result**: Validation added to flow, implementation updated

---

## Quick Reference: What to Type

### Starting New Project
```
1. fdd create adapter
2. fdd create business requirements
3. fdd create overall design
4. fdd validate overall design
5. fdd extract features
6. fdd design feature [name]
7. fdd validate feature [name]
8. fdd create implementation plan
9. fdd implement changes
```

### Updating Existing Project
```
# Update business context
fdd update business context - add [capability]

# Update design
fdd update overall design - add [domain type or API]

# Add new feature
fdd add feature [slug]

fdd design feature [slug]
```

### When Code Contradicts Design
```
1. STOP coding immediately
2. fdd update feature design - fix contradiction
3. fdd validate feature
4. fdd regenerate code
```

---

## Next Steps

1. **Try the example** - Follow prompts above for task management API
2. **Read full docs** - See `README.md` for complete methodology
3. **Learn FDL syntax** - See `FDL.md` for all keywords
4. **Understand workflows** - See `workflows/AGENTS.md` for workflow guide
5. **Create your adapter** - Use `ADAPTER_GUIDE.md` for details (TODO: update doc)

---

## Get Help

**Validation failed?**
- Read error message carefully
- Check specific section mentioned
- Use FDL for flows (no code)
- Reference domain types from Overall Design

**Feature too large?**
- Break into multiple features
- Each feature = one capability
- Target ≤3000 lines per DESIGN.md

**Code contradicts design?**
- Fix design first
- Re-validate design
- Then regenerate code

**Need to change Overall Design?**
- Update DESIGN.md
- Re-validate with design-validate.md
- Update affected features
- Re-validate features

---

## Remember

✅ Design before code  
✅ Validate before implementing  
✅ Use FDL, not code in designs  
✅ Reference, don't redefine  
✅ Fix design first, code second  

**Now start with the example above!** 🚀
