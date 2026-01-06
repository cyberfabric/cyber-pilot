# Create FDD Adapter

**Phase**: 0 - Pre-Project Setup  
**Purpose**: Create project-specific FDD adapter through guided questions

---

## Prerequisites

- FDD specification available somewhere in project
- Understanding of project technology stack
- Project root directory exists

**Note**: FDD specification location is auto-detected at workflow start

---

## Overview

This workflow creates a minimal, focused FDD adapter based on user needs. The adapter extends FDD core methodology with project-specific conventions **without adding unnecessary complexity**.

**Key Principle**: Ask questions, create only what's requested, nothing more.

---

## Workflow Initialization

### Step 0: Detect FDD Specification Location

**Requirement**: Automatically determine FDD specification directory from workflow file location

**Detection Logic**:
1. This workflow file is located at: `{FDD_SPEC_PATH}/workflows/00-create-adapter.md`
2. Therefore `FDD_SPEC_PATH` = parent directory of `workflows/`
3. Calculate from workflow file location:
   - Workflow directory: `dirname(this_workflow_file)` → `{FDD_SPEC_PATH}/workflows/`
   - FDD spec directory: `dirname(workflow_directory)` → `{FDD_SPEC_PATH}`

**Example**:
- Workflow at: `spec/FDD/workflows/00-create-adapter.md`
- FDD spec at: `spec/FDD/`

**Store as**: `FDD_SPEC_PATH` (relative to project root)

**Expected Outcome**: FDD specification path calculated from workflow location

**Validation Criteria**:
- `{FDD_SPEC_PATH}/AGENTS.md` exists
- `{FDD_SPEC_PATH}/workflows/` exists (current directory)
- `{FDD_SPEC_PATH}/ADAPTER_GUIDE.md` exists

**If Validation Fails**:
```
❌ Error: FDD specification structure invalid.

Expected structure:
{FDD_SPEC_PATH}/
├── AGENTS.md
├── ADAPTER_GUIDE.md
├── FDL.md
└── workflows/
    └── 00-create-adapter.md (this file)

Current location: {FDD_SPEC_PATH}
```

**Display to User**:
```
✓ FDD specification: {FDD_SPEC_PATH}
```

---

## Interactive Questions

Ask the user these questions **one by one** to gather requirements:

### Q1: Project Name
```
What is your project name? (used for adapter directory name)
Example: "web-app", "mobile-api", "cli-tool"
```
**Store as**: `PROJECT_NAME`

### Q2: Domain Model Technology
```
What technology will you use for domain model?
Options:
  1. TypeScript interfaces
  2. JSON Schema
  3. GTS (Global Type System) + JSON Schema
  4. Protobuf
  5. GraphQL Schema
  6. Other (specify)
```
**Store as**: `DML_TECH`

**If user selects "GTS (Global Type System) + JSON Schema"**:
Display GTS-specific requirements:
```
⚠️  GTS Identifier Requirements

GTS identifiers MUST follow strict format rules:
- All segments must be LOWERCASE (a-z, 0-9, underscore)
- Format: gts.vendor.package.namespace.type.v<MAJOR>[.<MINOR>]
- Segments: lowercase letters, digits, underscores only
- Segments must start with letter or underscore (NOT digit)
- NO uppercase letters allowed (ValidationResult ❌, validation_result ✅)

Examples:
✅ CORRECT: gts.ainetx.myapp.users.user_profile.v1
✅ CORRECT: gts.acme.billing.payment.invoice_item.v2.1
❌ WRONG: gts.ainetx.myapp.users.UserProfile.v1
❌ WRONG: gts.ainetx.myapp.Users.Profile.v1

Reference: See spec/GTS/README.md for complete specification
```

**If user selects "Other"**, ask:
```
Please specify the domain model technology:
- Technology name: ___
- File location for schemas: ___
- Reference syntax for types (describe how to reference types in this technology): ___
```

**Then ask about specification**:
```
Does this technology have a specification document?
Options:
  1. Yes, specification exists in project (provide path)
  2. Yes, specification exists externally (provide URL)
  3. No, need to create specification
  4. Skip for now (adapter will be incomplete)
```

**Action based on answer**:

**Option 1 - Spec exists in project**:
- Ask: "Path to specification: ___"
- Validate path exists
- Store as: `DML_SPEC_PATH`

**Option 2 - Spec exists externally**:
- Ask: "URL to specification: ___"
- Ask: "Should we download/clone it to project? (y/n)"
- If yes: "Where to place it? (e.g., spec/{tech-name})"
- Store as: `DML_SPEC_URL` and optionally `DML_SPEC_PATH`

**Option 3 - Need to create**:
- Show message:
  ```
  ⚠️  Specification required for custom technology.
  
  Please create specification document:
  - Recommended location: spec/{tech-name}/
  - Should include:
    * Type system rules
    * Reference syntax
    * Validation rules
    * Examples
  
  After creating, provide path: ___
  ```
- Store as: `DML_SPEC_PATH`

**Option 4 - Skip**:
- Set `DML_SPEC_STATUS` = "INCOMPLETE"
- Show warning:
  ```
  ⚠️  Adapter will be created with INCOMPLETE status.
  
  ALL workflows will be BLOCKED until specification is provided.
  
  You can complete adapter later by:
  1. Adding specification to project
  2. Updating adapter AGENTS.md with spec path
  3. Setting status to COMPLETE
  ```

### Q3: Domain Model Location
```
Where will domain model files be located?
Options:
  1. architecture/domain-model/
  2. architecture/types/
  3. src/types/
  4. Other (specify)
```
**Store as**: `DML_LOCATION`

### Q4: API Contract Technology
```
What technology will you use for API contracts?
Options:
  1. OpenAPI 3.x
  2. GraphQL Schema
  3. gRPC (.proto)
  4. CLISPEC (for CLI tools)
  5. Custom format (specify)
  6. None (no API contracts needed)
```
**Store as**: `API_TECH`

**If user selects "CLISPEC"**:
- Set `API_SPEC_PATH` = `../FDD/CLISPEC.md` (relative path from adapter)
- Show message:
  ```
  ✓ CLISPEC selected
  
  CLISPEC is a simple, human and machine-readable format for CLI commands.
  Specification: spec/FDD/CLISPEC.md
  
  Your adapter will reference the built-in CLISPEC specification.
  CLI commands will be documented in: architecture/cli-specs/commands.clispec
  ```

**If user selects "Custom format"**, ask:
```
Please describe your custom API format:
- Format name: ___
- File location: ___
- File extension: ___
- Brief description: ___
```

**Then ask about specification**:
```
Does this format have a specification document?
Options:
  1. Yes, specification exists in project (provide path)
  2. Yes, specification exists externally (provide URL)
  3. No, need to create specification
  4. Skip for now (adapter will be incomplete)
```

**Action based on answer**:

**Option 1 - Spec exists in project**:
- Ask: "Path to specification: ___"
- Validate path exists
- Store as: `API_SPEC_PATH`

**Option 2 - Spec exists externally**:
- Ask: "URL to specification: ___"
- Ask: "Should we download/clone it to project? (y/n)"
- If yes: "Where to place it? (e.g., spec/{format-name})"
- Store as: `API_SPEC_URL` and optionally `API_SPEC_PATH`

**Option 3 - Need to create**:
- Show message:
  ```
  ⚠️  Specification required for custom format.
  
  Please create specification document:
  - Recommended location: spec/{format-name}/
  - Should include:
    * Format structure
    * Validation rules
    * Linking syntax
    * Examples
  
  After creating, provide path: ___
  ```
- Store as: `API_SPEC_PATH`

**Option 4 - Skip**:
- Set `API_SPEC_STATUS` = "INCOMPLETE"
- Show warning:
  ```
  ⚠️  Adapter will be created with INCOMPLETE status.
  
  ALL workflows will be BLOCKED until specification is provided.
  
  You can complete adapter later by:
  1. Adding specification to project
  2. Updating adapter AGENTS.md with spec path
  3. Setting status to COMPLETE
  ```

### Q5: API Contract Location
```
Where will API contract files be located?
Options:
  1. architecture/api-specs/
  2. architecture/openapi/
  3. src/schemas/
  4. Other (specify)
```
**Store as**: `API_LOCATION`

### Q6: Security Model
```
Describe your security model and authentication approach:

Examples:
- JWT tokens with role-based access control
- OAuth 2.0 + API keys for service-to-service
- Session-based auth with CSRF protection
- mTLS for microservices communication
- Public API (no authentication)

Your security model (1-3 sentences): ___
```
**Store as**: `SECURITY_MODEL`

### Q7: Non-Functional Requirements & Architecture
```
What are your key non-functional requirements?

Examples:
- Performance: API response < 200ms, handle 1000 req/s
- Scalability: horizontal scaling, stateless services
- Reliability: 99.9% uptime, circuit breakers
- Observability: structured logging, distributed tracing
- Data consistency: eventual consistency acceptable

Your requirements (one per line, add as many as needed):
- ___
- ___
```
**Store as**: `NFR_LIST[]`

**Note**: List what's important for your project now. You can add more requirements later by re-running this workflow or updating the adapter manually.

### Q8: Additional Context (Section D)
```
Is there any additional context FDD should be aware of?

Examples:
- Integration with existing systems (e.g., "Must integrate with legacy CRM API")
- Technology constraints (e.g., "Must use company's standard Java stack")
- Future plans (e.g., "Will add mobile app in Q3")
- Team conventions (e.g., "Follow company microservices guidelines")
- Compliance requirements (e.g., "GDPR compliant, data residency in EU")

Additional context (optional, free form): ___
```
**Store as**: `ADDITIONAL_CONTEXT`

**Note**: This goes into Section D of DESIGN.md and is NOT validated by FDD workflows.

---

## Requirements

### 1. Create Adapter Directory Structure

**Requirement**: Create minimal adapter structure in `{ADAPTER_BASE_PATH}/FDD-Adapter/`

**Path Calculation**:
- `ADAPTER_BASE_PATH` = parent directory of `FDD_SPEC_PATH`
- Example: If `FDD_SPEC_PATH` is `spec/FDD`, then `ADAPTER_BASE_PATH` is `spec`
- Adapter location: `{ADAPTER_BASE_PATH}/FDD-Adapter/`

**Required Actions**:
- Create directory: `{ADAPTER_BASE_PATH}/FDD-Adapter/`
- Create directory: `{ADAPTER_BASE_PATH}/FDD-Adapter/workflows/`

**Expected Outcome**: Adapter directory structure exists

**Validation Criteria**:
- Directory `{ADAPTER_BASE_PATH}/FDD-Adapter/` exists
- Directory `{ADAPTER_BASE_PATH}/FDD-Adapter/workflows/` exists

---

### 2. Create AGENTS.md

**Requirement**: Generate `{ADAPTER_BASE_PATH}/FDD-Adapter/AGENTS.md` based on answers

**Important**: Calculate relative path from adapter to FDD spec
- From: `{ADAPTER_BASE_PATH}/FDD-Adapter/AGENTS.md`
- To: `{FDD_SPEC_PATH}/AGENTS.md`
- Use relative path in `Extends` directive

**Required Content**:
```markdown
# AI Agent Instructions for {Project Name}

<!-- 
⚠️ AI AGENT NOTICE: This file was generated by workflow adapter-config.
If user wants to modify this adapter, run workflow adapter-config again or edit manually with caution.
Manual edits may be overwritten if workflow is re-run.
-->

**Extends**: `{RELATIVE_PATH_TO_FDD}/AGENTS.md`

---

## Project Context

**Purpose**: {Brief description from Q1}

**Technology Stack**:
{List based on answers}

---

## Core Methodology

**READ FIRST**: `spec/FDD/AGENTS.md`

**CRITICAL**: Follow all rules in `spec/FDD/AGENTS.md` - they are immutable and validated by tooling.

---

## Domain Model

**Technology**: {DML_TECH from Q2}

{If DML_TECH is "GTS (Global Type System) + JSON Schema"}
**Specification**: `spec/GTS`

**⚠️ CRITICAL**: Before using GTS, read the specification at `spec/GTS/README.md`

**⚠️ GTS IDENTIFIER RULES** (STRICTLY ENFORCED):
- ALL segments MUST be lowercase (a-z, 0-9, underscore only)
- NO uppercase letters allowed in identifiers
- Format: `gts.vendor.package.namespace.type.v<MAJOR>[.<MINOR>]`
- Type names: use snake_case (e.g., `user_profile`, NOT `UserProfile`)
- Example: `gts.ainetx.myapp.users.user_profile.v1` ✅
- Invalid: `gts.ainetx.myapp.users.UserProfile.v1` ❌

{End if}

{If custom technology with spec}
**Specification**: `{DML_SPEC_PATH}` or `{DML_SPEC_URL}`

**⚠️ CRITICAL**: Before using this domain model technology, read the specification:
- **Local spec**: `{DML_SPEC_PATH}`
- **External spec**: {DML_SPEC_URL}

{If custom technology WITHOUT spec}
**⚠️ INCOMPLETE**: Specification not provided for custom technology.

This adapter is **INCOMPLETE**. ALL workflows will be **BLOCKED** until:
1. Specification document created at: `spec/{tech-name}/`
2. Path added to this section
3. Adapter status updated to COMPLETE

{End if}

**Location**: `{DML_LOCATION from Q3}`

{If DML_TECH is "GTS (Global Type System) + JSON Schema"}
**DML Syntax**: Use GTS reference format in JSON Schema `$ref` fields:
- Schema $id: `gts.vendor.package.namespace.type.v<version>`
- Schema $ref: `gts://gts.vendor.package.namespace.type.v<version>`
- All identifiers MUST be lowercase with underscores for word separation

**Validation**: Validate JSON schemas per JSON Schema draft-07 specification. Verify GTS identifiers follow lowercase-only format.
{Else}
**DML Syntax**: Defined by the specification above. Read the specification to understand type reference syntax.

**Validation**: {Command based on technology}
{End if}

{Include technology-specific details only if provided by user}

---

## API Contracts

{Only include if API_TECH from Q4 is not "None"}

**Technology**: {API_TECH from Q4}

{If custom format with spec}
**Specification**: `{API_SPEC_PATH}` or `{API_SPEC_URL}`

**⚠️ CRITICAL**: Before using this API format, read the specification:
- **Local spec**: `{API_SPEC_PATH}`
- **External spec**: {API_SPEC_URL}

{If custom format WITHOUT spec}
**⚠️ INCOMPLETE**: Specification not provided for custom format.

This adapter is **INCOMPLETE**. ALL workflows will be **BLOCKED** until:
1. Specification document created at: `spec/{format-name}/`
2. Path added to this section
3. Adapter status updated to COMPLETE

**Location**: `{API_LOCATION from Q5}`

{Include format-specific details only if provided by user}

---

## Technical Architecture (Section C)

### Security Model

{SECURITY_MODEL from Q6}

### Non-Functional Requirements

{If NFR_LIST is not empty, list each item}
{NFR_LIST items, one per line with bullet points}

---

## Additional Context (Section D)

{Only include if ADDITIONAL_CONTEXT from Q8 is provided}

{ADDITIONAL_CONTEXT}

**Note**: This section is optional and NOT validated by FDD workflows.

---

## References

- **Core FDD**: `{FDD_SPEC_PATH}/AGENTS.md`
- **Workflows**: `{FDD_SPEC_PATH}/workflows/`
- **FDL Syntax**: `{FDD_SPEC_PATH}/FDL.md`
- **Adapter Guide**: `{FDD_SPEC_PATH}/ADAPTER_GUIDE.md`
```

**Expected Outcome**: Minimal, focused AGENTS.md exists with only requested content

**Validation Criteria**:
- File `spec/FDD-Adapter/AGENTS.md` exists
- Extends `../FDD/AGENTS.md`
- Contains only sections based on user answers
- No placeholder content for skipped sections
- Domain Model section present (required)
- API Contracts section present only if not "None"

---

### 3. Create workflows/AGENTS.md

**Requirement**: Generate `{ADAPTER_BASE_PATH}/FDD-Adapter/workflows/AGENTS.md` based on needs

**Important**: Calculate relative path from adapter workflows to FDD workflows
- From: `{ADAPTER_BASE_PATH}/FDD-Adapter/workflows/AGENTS.md`
- To: `{FDD_SPEC_PATH}/workflows/AGENTS.md`
- Use relative path in `Extends` directive

**Required Content**:
```markdown
# Workflow Instructions for {Project Name}

<!-- 
⚠️ AI AGENT NOTICE: This file was generated by workflow adapter-config.
If user wants to modify this adapter, run workflow adapter-config again or edit manually with caution.
Manual edits may be overwritten if workflow is re-run.
-->

**Extends**: `{RELATIVE_PATH_TO_FDD_WORKFLOWS}/AGENTS.md`

---

## Pre-Workflow Checks

{Include only checks relevant to specified technologies}

{Example: If DML_TECH is TypeScript}
- [ ] Node.js installed
- [ ] npm dependencies installed

{Example: If TEST_FRAMEWORK is not "Skip"}
- [ ] {TEST_FRAMEWORK} configured

{Example: If BUILD_TOOL is not "Skip"}
- [ ] {BUILD_TOOL} available

---

## Validation Commands

### Domain Model Validation
```bash
{Command based on DML_TECH}
```

{Only include if API_TECH is not "None"}
### API Contracts Validation
```bash
{Command based on API_TECH}
```

---

## References

- **Core Workflows**: `{FDD_SPEC_PATH}/workflows/AGENTS.md`
- **Adapter**: `{ADAPTER_BASE_PATH}/FDD-Adapter/AGENTS.md`
- **FDD Core**: `{FDD_SPEC_PATH}/AGENTS.md`
```

**Expected Outcome**: Minimal workflows/AGENTS.md with only relevant checks

**Validation Criteria**:
- File `spec/FDD-Adapter/workflows/AGENTS.md` exists
- Extends `../../FDD/workflows/AGENTS.md`
- Pre-workflow checks match specified technologies
- Validation commands match specified technologies
- No irrelevant sections included

---

### 4. Validate Adapter Files

**Requirement**: Validate that created adapter files are correct and complete

**Validation Steps**:
1. **Verify file structure**:
   - `{ADAPTER_BASE_PATH}/FDD-Adapter/AGENTS.md` exists
   - `{ADAPTER_BASE_PATH}/FDD-Adapter/workflows/AGENTS.md` exists
   
2. **Verify AGENTS.md content**:
   - Has `Extends` directive with correct relative path to `../FDD/AGENTS.md`
   - Contains AI agent notice comment
   - Contains Project Context section
   - Contains Domain Model section with technology and location
   - Contains API Contracts section (if not skipped)
   - Contains Security Model (from Q6)
   - Contains Non-Functional Requirements (from Q7)
   - Contains Additional Context (if provided in Q8)
   - Contains References section

3. **Verify workflows/AGENTS.md content**:
   - Has `Extends` directive with correct relative path to `../../FDD/workflows/AGENTS.md`
   - Contains AI agent notice comment
   - Contains Pre-Workflow Checks matching selected technologies
   - Contains Validation Commands section with Domain Model validation (if applicable)
   - Contains Validation Commands section with API Contracts validation (if applicable)
   - Contains References section

**Display Validation Results**:
```
✅ Validating adapter files...

✅ File structure correct
✅ AGENTS.md structure valid
✅ workflows/AGENTS.md structure valid
✅ All required sections present
✅ Relative paths correct

Adapter validation passed!
```

**If validation fails**:
```
❌ Adapter validation failed:

Issues found:
- {List of validation errors}

Please fix these issues before proceeding.
```

**Expected Outcome**: Adapter files are validated and correct

**Validation Criteria**:
- All required files exist
- All required sections present
- Relative paths are correct
- No missing content based on user answers

---

### 5. Confirm Adapter Creation

**Requirement**: Show summary and get user confirmation

**Display Summary**:
```
FDD Adapter Summary:
─────────────────────
FDD Spec: {FDD_SPEC_PATH}
Project: {PROJECT_NAME}
Location: {ADAPTER_BASE_PATH}/FDD-Adapter/

Configured:
✓ Domain Model: {DML_TECH} at {DML_LOCATION}
  {Show spec status: ✓ Spec: {DML_SPEC_PATH} or ⚠️ INCOMPLETE}
{✓ or ✗} API Contracts: {API_TECH} at {API_LOCATION}
  {Show spec status if custom: ✓ Spec: {API_SPEC_PATH} or ⚠️ INCOMPLETE}
✓ Security Model: {first 50 chars of SECURITY_MODEL}
✓ NFR: {count of NFR_LIST items} requirements specified
{✓ or ✗} Additional Context: {"Yes" if ADDITIONAL_CONTEXT else "None"}

Adapter Status: {COMPLETE or INCOMPLETE}
{If INCOMPLETE, show warning}

Files to create:
- {ADAPTER_BASE_PATH}/FDD-Adapter/AGENTS.md
- {ADAPTER_BASE_PATH}/FDD-Adapter/workflows/AGENTS.md
{If custom specs, list them}

Proceed? (y/n)
```

**If adapter status is INCOMPLETE**:
```
⚠️ WARNING: Adapter will be created with INCOMPLETE status.

Missing specifications:
{List missing specs for DML and/or API}

ALL workflows will be BLOCKED until specifications are provided.
```

**Expected Outcome**: User confirms or cancels

**Validation Criteria**:
- Summary clearly shows what will be created
- No surprises for user
- Easy to abort if needed

---

## Completion Criteria

Adapter creation is complete when:

- [ ] FDD specification location detected
- [ ] User answered all relevant questions
- [ ] **Specifications validated** (for custom technologies):
  - [ ] Domain Model spec provided (if custom tech)
  - [ ] API Contract spec provided (if custom format)
  - [ ] Spec paths exist and are accessible
- [ ] Adapter directory created at `{ADAPTER_BASE_PATH}/FDD-Adapter/`
- [ ] `AGENTS.md` created with ONLY requested content
- [ ] `AGENTS.md` includes specification references
- [ ] `AGENTS.md` includes Security Model (from Q6)
- [ ] `AGENTS.md` includes Non-Functional Requirements (from Q7)
- [ ] `AGENTS.md` includes Additional Context if provided (from Q8)
- [ ] `AGENTS.md` marked with status (COMPLETE or INCOMPLETE)
- [ ] `workflows/AGENTS.md` created with ONLY relevant checks
- [ ] No placeholder text for skipped features
- [ ] **Adapter files validated** (Requirement 4):
  - [ ] File structure verified
  - [ ] AGENTS.md content validated
  - [ ] workflows/AGENTS.md content validated
  - [ ] All required sections present
  - [ ] Relative paths correct
- [ ] User confirmed the configuration
- [ ] Summary shown with created files and status
- [ ] **Workflow 01-init-project is now unblocked** (adapter provides all required info)

**Adapter Status Rules**:
- **COMPLETE**: All custom technologies have specifications provided
- **INCOMPLETE**: One or more custom technologies missing specifications

**If INCOMPLETE**:
- Add warning comment in `AGENTS.md` header
- Document missing specifications
- Provide instructions for completion

---

**Interactive Mode**: See `../AGENTS.md` for general interactive workflow rules

**Adapter-Specific Rules**:

DO NOT:
- ❌ Add sections user didn't request
- ❌ Include placeholder text for skipped features  
- ❌ Create example implementations
- ❌ Add "nice to have" features without asking
- ❌ Assume technology choices
- ❌ Create files beyond AGENTS.md and workflows/AGENTS.md

DO:
- ✅ Create minimal, focused content
- ✅ Include only what user specified

---

## Common Challenges

### Challenge: User Wants to Add More Later

**Resolution**: Adapter can be edited manually anytime. Run this workflow again to regenerate, or edit `AGENTS.md` directly.

### Challenge: User Unsure About Technology Choices

**Resolution**: Suggest starting minimal (skip optional sections). Can always add later. Better to start simple than overcommit.

### Challenge: Custom Technology Not Listed

**Resolution**: Select "Other" and let user specify exact details. Don't guess or assume.

---

## Next Activities

After adapter creation:

1. **Configure Agent Tools** (recommended): Run workflow `config-agent-tools.md`
   - Sets up AI agent to automatically read adapter AGENTS.md
   - Agent will natively follow FDD workflows without manual reminders
2. **Review Generated Files**: Check `spec/FDD-Adapter/AGENTS.md`
3. **Read Specifications**:
   - Review domain model specification (if custom technology)
   - Review API contract specification (if custom format)
4. **Initialize Project**: Run workflow `01-init-project.md`
5. **Customize if Needed**: Edit adapter files directly for fine-tuning

---

## Example Interaction

```
AI: What is your project name?
User: web-app

AI: What technology will you use for domain model?
User: 3 (GTS + JSON Schema)

AI: Where will domain model files be located?
User: 1 (architecture/domain-model/)

AI: What technology will you use for API contracts?
User: 1 (OpenAPI 3.x)

AI: Where will API contract files be located?
User: 1 (architecture/api-specs/)

AI: What testing framework(s) will you use?
User: 2 (Vitest)

AI: What build/deployment tools will you use?
User: 3 (Vite)

AI: Do you need to specify any additional conventions? (y/n)
User: n

AI: [Shows summary]
    
    FDD Adapter Summary:
    ─────────────────────
    FDD Spec: spec/FDD
    Project: web-app
    Location: spec/web-app-adapter/
    
    Configured:
    ✓ Domain Model: GTS + JSON Schema at architecture/domain-model/
    ✓ API Contracts: OpenAPI 3.x at architecture/api-specs/
    ✓ Testing: Vitest
    ✓ Build: Vite
    
    Files to create:
    - spec/web-app-adapter/AGENTS.md
    - spec/web-app-adapter/workflows/AGENTS.md
    
    Proceed? (y/n)

User: y

AI: ✅ Detected FDD at: spec/FDD
    ✅ Created spec/web-app-adapter/AGENTS.md
    ✅ Created spec/web-app-adapter/workflows/AGENTS.md
    
    Adapter ready! Next: Run workflow 01-init-project.md
```

---

## References

- **Methodology**: `../AGENTS.md` - FDD core methodology
- **Adapter Guide**: `../ADAPTER_GUIDE.md` - Detailed adapter guide
- **Next Workflow**: `01-init-project.md` - Initialize project with adapter
