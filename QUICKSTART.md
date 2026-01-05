# FDD Quick Start Guide

**Get started with Feature-Driven Development in 5 minutes**

---

## What is FDD?

FDD (Feature-Driven Development) is a design-first methodology that ensures your code matches your design through strict validation. It enforces a clear hierarchy: **Overall Design → Feature Design → OpenSpec Changes → Code**.

**Core principle**: Design is source of truth. If code contradicts design, fix design first, then re-validate.

---

## Quick Start

### 1. Create FDD Adapter (Required First Step)

**FDD requires a project-specific adapter before ANY work can begin.**

```bash
# Check for adapter at:
spec/FDD-Adapter/AGENTS.md
```

**No adapter found?** → Follow workflow: **adapter-config** (workflows/adapter-config.md)

This workflow (5-10 minutes) guides you through:
- ✅ Ask guided questions about your project
- ✅ Define domain model format (GTS, JSON Schema, TypeScript, etc.)
- ✅ Define API contract format (OpenAPI, GraphQL, CLISPEC, etc.)
- ✅ Capture security model and non-functional requirements
- ✅ Generate `spec/FDD-Adapter/AGENTS.md` and `spec/FDD-Adapter/workflows/AGENTS.md`

**Result**: Adapter created at `spec/FDD-Adapter/` with status COMPLETE or INCOMPLETE

### 1a. Configure AI Agent (Optional)

**After creating adapter, optionally set up your AI agent:**

Follow workflow: **config-agent-tools** (workflows/config-agent-tools.md)

This workflow (2 minutes) creates agent-specific configuration:
- **Windsurf**: `.windsurf/rules.md` + workflow wrappers in `.windsurf/workflows/`
- **Cursor**: `.cursorrules` (single file with inline workflow references)
- **Cline**: `.clinerules` (minimal single file)
- **Aider**: `.aider.conf.yml` (YAML config)

**All configs**:
- ✅ Tell agent to read `spec/FDD-Adapter/AGENTS.md` first
- ✅ Provide FDD workflow references

### 2. Initialize Project

Follow these manual steps to initialize your project:

1. Create a new directory `architecture/` and add a new file `DESIGN.md` (template)
2. Create a new directory `architecture/features/` (directory)
3. Create a new directory `gts/` or `spec/API/` (if needed)

### 3. Write Overall Design

Edit `architecture/DESIGN.md` with:
- **Section A**: System vision, actors, capabilities
- **Section B**: Business rules, principles, constraints
- **Section C**: Architecture, domain model, API contracts
- **Section D**: Optional context (integrations, future plans)

**Recommended**: Use an AI agent to edit the design. The agent will automatically:
- ✅ Follow FDD requirements and validation rules
- ✅ Apply adapter-specific conventions (DML syntax, API linking)
- ✅ Use FDL (plain English) for flows, never code
- ✅ Reference domain model and API contracts correctly
- ✅ Ensure proper structure and completeness

**Key**: Use **FDL** (plain English) for flows, never write code in DESIGN.md

### 4. Validate Overall Design

Follow workflow: **02-validate-architecture** (workflows/02-validate-architecture.md)

Must score ≥90/100

### 5. Initialize Features

Follow workflow: **03-init-features** (workflows/03-init-features.md)

Extracts features from Overall Design and creates `architecture/features/FEATURES.md` manifest

### 6. Design Each Feature

For each feature in `architecture/features/feature-{slug}/DESIGN.md`:
- **Section A**: Feature overview and scope
- **Section B**: Actor flows in FDL (PRIMARY!)
- **Section C**: Algorithms in FDL
- **Section D**: States in FDL (optional)
- **Section E**: Technical details (DB, operations, errors)
- **Section F**: Testing and OpenSpec changes plan

**Recommended**: Use an AI agent to design features. The agent will automatically:
- ✅ Follow FDD feature requirements (Section A-F structure)
- ✅ Apply adapter conventions (DML references, API linking)
- ✅ Use FDL only, never write code in DESIGN.md
- ✅ Reference Overall Design types (never redefine)
- ✅ Start with Actor Flows (Section B) - the primary driver
- ✅ Ensure 100/100 validation readiness

**Key**: Design Section B (Actor Flows) FIRST - everything flows from there

### 7. Validate Feature

Follow workflow: **06-validate-feature** (workflows/06-validate-feature.md)

Must score 100/100 + 100% completeness

### 8. Implement via OpenSpec

Follow workflows:
1. **09-openspec-change-next** - Create first (or next) change from DESIGN.md
2. **10-openspec-change-implement** - Implement each change
3. **11-openspec-change-complete** - Complete and archive change
4. **09-openspec-change-next** - Create next change (repeat from step 2)

### 9. Complete Feature

Follow workflow: **07-complete-feature** (workflows/07-complete-feature.md)

Validates all tests pass, marks feature complete

---

## Core Concepts

### Design Hierarchy (Never Violate)

```
OVERALL DESIGN
    ↓ reference, never contradict
FEATURE DESIGN
    ↓ reference, never contradict
OPENSPEC CHANGES
    ↓ implement exactly
CODE
```

### FDL - Flow Description Language

Plain English pseudo-code for flows and algorithms. **Never write actual code in DESIGN.md**.

```markdown
✅ Good (FDL):
1. User submits login form with email and password
2. System validates email format
3. System checks credentials against database
4. IF credentials valid:
   - Generate JWT token
   - Return token to user
5. ELSE:
   - Return "Invalid credentials" error

❌ Bad (actual code):
const token = jwt.sign({ userId: user.id }, SECRET);
return res.json({ token });
```

### Actor Flows (Section B)

**Always design Actor Flows first**. They drive everything:
- What each actor (user, system, external service) does
- Step-by-step interactions
- Decision points and branches
- Error cases

### Domain Model

Define types ONCE in Overall Design. Reference them everywhere:
- ✅ `@DomainModel.User` in Feature Design
- ❌ Redefining User type in Feature Design

### OpenSpec Changes

Each change is atomic and deployable:
- `proposal.md` - Why this change
- `tasks.md` - Implementation checklist
- `specs/` - Delta specifications
- `design.md` - Technical decisions (optional)

---

## Best Practices

### Design Phase

1. **Start with Actor Flows** - Section B drives everything
2. **Use FDL only** - Never write code in DESIGN.md
3. **Reference, don't redefine** - Link to Overall Design types
4. **Keep features small** - ≤3000 lines recommended, ≤4000 hard limit
5. **Validate early, validate often** - Catch issues before coding

### Implementation Phase

1. **Design is source of truth** - If contradiction found, fix design first
2. **Atomic changes** - Each OpenSpec change is deployable
3. **Follow the plan** - Feature DESIGN.md Section F has the roadmap
4. **Update as you learn** - Use workflow 08-fix-design when needed
5. **Test continuously** - OpenSpec validates each change

### Team Collaboration

1. **Read the adapter** - Understand project-specific conventions
2. **Check FEATURES.md** - See what's blocked/in-progress
3. **Review designs first** - Before implementation starts
4. **Use workflows** - Don't skip validation steps
5. **Document decisions** - Section D for context, design.md for technical choices

### Common Pitfalls

❌ **Skip adapter creation** → ALL workflows blocked without adapter
❌ **Incomplete adapter** → Create specs or skip optional sections
❌ **Write code in DESIGN.md** → Use FDL instead
❌ **Redefine types** → Reference Overall Design
❌ **Skip validation** → Catch issues early, not late
❌ **Make features too large** → Break into smaller features
❌ **Fix code when design wrong** → Fix design, then re-validate

---

## Examples

### Example 1: Simple REST API

**Overall Design** (architecture/DESIGN.md):
```markdown
## A. Business Context

### System Vision
User management API for authentication and profile management.

### Actors
- **End User**: Can register, login, view/update profile
- **Admin**: Can manage all users
- **System**: Handles token generation and validation

## B. Requirements & Principles

### Business Rules
- Email must be unique
- Passwords hashed with bcrypt
- JWT tokens expire after 24 hours

## C. Technical Architecture

### Domain Model
@DomainModel.User:
- id: UUID
- email: string (unique)
- passwordHash: string
- role: "user" | "admin"
- createdAt: timestamp

### API Contracts
@API.POST:/auth/register - User registration
@API.POST:/auth/login - User login
@API.GET:/users/me - Get current user profile
```

**Feature Design** (architecture/features/feature-user-auth/DESIGN.md):
```markdown
## B. Actor Flows (FDL)

### Flow 1: User Registration
1. End User submits registration form with email and password
2. System validates email format (RFC 5322)
3. System checks email not already registered
4. IF email exists:
   - Return "Email already registered" error
5. System hashes password with bcrypt (cost factor 10)
6. System creates User record in database
7. System generates JWT token with user ID and role
8. Return token and user data to End User

### Flow 2: User Login
1. End User submits login form with email and password
2. System finds User by email in database
3. IF User not found:
   - Return "Invalid credentials" error
4. System compares password hash with bcrypt
5. IF password invalid:
   - Return "Invalid credentials" error
6. System generates JWT token with user ID and role
7. Return token and user data to End User
```

### Example 2: CLI Tool

**Adapter** uses **CLISPEC** for API contracts:
```
COMMAND validate-feature
SYNOPSIS: mytool validate-feature <slug> [options]
DESCRIPTION: Validate feature design completeness
WORKFLOW: 06-validate-feature

ARGUMENTS:
  slug  <slug>  required  Feature identifier

OPTIONS:
  --strict  <boolean>  Enable strict validation mode

EXIT CODES:
  0  Valid (score 100/100)
  2  Validation failed

EXAMPLE:
  $ mytool validate-feature user-authentication
---
```

### Example 3: Domain Model with GTS

**Overall Design** defines types:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "gts://gts.myapp.core.user.v1~",
  "type": "object",
  "properties": {
    "gtsId": { "type": "string" },
    "email": { "type": "string", "format": "email" },
    "role": { "enum": ["user", "admin"] }
  }
}
```

**Feature Design** references it:
```markdown
## E. Technical Details

### Database Schema
Uses @DomainModel[gts.myapp.core.user.v1~]

Operations:
- Create: INSERT INTO users (email, password_hash, role)
- Read: SELECT * FROM users WHERE id = ?
- Update: UPDATE users SET email = ? WHERE id = ?
```

---

## Workflow Cheatsheet

```bash
# Phase 0: Setup (REQUIRED FIRST)
adapter-config                         # Follow workflow to create adapter
                                       # Location: spec/FDD-Adapter/
                                       # Result: AGENTS.md + workflows/AGENTS.md

# Phase 1: Architecture
01-init-project                        # Initialize structure
02-validate-architecture               # Validate Overall Design (≥90/100)

# Phase 2: Feature Planning
03-init-features                       # Generate features from design
04-validate-features                   # Validate FEATURES.md
05-init-feature {slug}                 # Create single feature manually
06-validate-feature {slug}             # Validate Feature Design (100/100)

# Phase 3: Implementation
09-openspec-change-next {slug}         # Create change (first or next)
10-openspec-change-implement {slug} {id}  # Implement change
11-openspec-change-complete {slug} {id}   # Complete change
# Repeat 09→10→11 for each change
12-openspec-validate {slug}            # Validate OpenSpec structure
07-complete-feature {slug}             # Mark feature complete

# Utils
08-fix-design {slug}                   # Fix design issues
```

---

## Next Steps

1. **Read AGENTS.md** - Full FDD methodology
2. **Read workflows/AGENTS.md** - Workflow selection guide
3. **Read FDL.md** - Flow Description Language syntax
4. **Check ADAPTER_GUIDE.md** - How to create adapters
5. **See CLISPEC.md** - CLI command specification format (if building CLI tools)

---

## Resources

- **FDD Core**: `AGENTS.md`
- **Workflows**: `workflows/AGENTS.md`
- **FDL Syntax**: `FDL.md`
- **Adapter Guide**: `ADAPTER_GUIDE.md`
- **CLI Format**: `CLISPEC.md`
- **OpenSpec**: https://openspec.dev

---

## Get Help

**Validation failed?** 
- Check error messages carefully
- Review the specific section mentioned
- Use FDL for flows/algorithms
- Reference domain types from Overall Design

**Feature too large?**
- Break into multiple smaller features
- Each feature should be one capability
- Target ≤3000 lines per DESIGN.md

**Code contradicts design?**
- STOP coding immediately
- Fix design using workflow 08-fix-design
- Re-validate with workflow 06-validate-feature
- Resume coding only after validation passes

**Need to change Overall Design?**
- Update architecture/DESIGN.md
- Re-validate with workflow 02-validate-architecture
- Update affected Feature Designs
- Re-validate features

---

## Remember

✅ **Run adapter-config first** - ALL workflows blocked without adapter at `spec/FDD-Adapter/`
✅ **Design before code** - Always validate designs first
✅ **Actor flows are primary** - Start with Section B
✅ **Use FDL, not code** - Plain English in DESIGN.md
✅ **Reference, don't redefine** - Link to Overall Design
✅ **Validate often** - Catch issues early
✅ **Design is truth** - Fix design first, code second

**Start with adapter-config, then happy designing! 🎨**
