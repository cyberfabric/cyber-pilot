# Feature Design Structure Requirements

**Purpose**: Define required structure for `architecture/features/feature-{slug}/DESIGN.md`

**Used by**:
- Workflow 05 (init-feature): Generate feature DESIGN.md template
- Workflow 06 (validate-feature): Validate feature DESIGN.md completeness

---

## File Location

**Path**: `architecture/features/feature-{slug}/DESIGN.md`

**Size limits**:
- Recommended: ≤3000 lines
- Hard limit: ≤4000 lines

---

## Required Sections

### Section A: Feature Context

**Purpose**: Feature overview, purpose, actors, and references

**Size Constraint**: ≤200 lines recommended

**Required subsections**:
1. **Overview**: What this feature does
2. **Purpose**: Why it exists, what problem it solves
3. **Actors**: Who interacts with this feature (must match Overall Design actors)
4. **References**: Links to Overall Design sections and dependencies

**Content requirements**:
- Clear feature scope definition
- References to Overall Design (architecture/DESIGN.md)
- List of dependencies on other features (if any)
- Actor names must match Overall Design Section A exactly

---

### Section B: Actor Flows

**Purpose**: Document how actors interact with the feature

**Size Constraint**: ≥50 lines (standard features)

**Content requirements**:
- Written in FDL (see `../FDL.md` for syntax)
- Each flow includes: Actor, Steps, Success Scenarios, Error Scenarios
- Flows are comprehensive and cover main use cases
- **NO code blocks** - only FDL syntax
- **FDL Keywords**: Only valid FDL keywords (see `../FDL.md`):
  - ✅ Allowed: **IF**, **ELSE IF**, **ELSE**, **FOR EACH**, **WHILE**, **TRY**, **CATCH**, **RETURN**, **PARALLEL**, **MATCH**, **CASE**, **GO TO**, **SKIP TO**, **FROM**, **TO**
  - ❌ Prohibited bold keywords: **WHEN** (in flows), **THEN**, **SET**, **VALIDATE**, **CHECK**, **LOAD**, **READ**, **WRITE**, **CREATE**, **ADD**, **AND**
  - Plain English actions (not bold) are allowed: "Set variable", "Load template"

**Exceptions**:
- Init/structural features may have minimal flows
- Infrastructure features with minimal user interaction may have shorter flows

---

### Section C: Algorithms

**Purpose**: Document algorithms in FDL (not code)

**Size Constraint**: ≥100 lines (standard features)

**Content requirements**:
- Algorithms written in FDL (see `../FDL.md`)
- Each algorithm: Input, Output, Steps in FDL
- **NO programming language code** (`rust`, `typescript`, `javascript`, `python`, etc.)
- **NO programming syntax** (`fn`, `function`, `def`, `class`, `interface`)
- Use FDL control structures: **IF**, **FOR EACH**, **WHILE**, **TRY/CATCH**, **RETURN**
- **FDL Keywords**: Same as Section B (see above)

**Exception**: Init/structural features may have minimal algorithms

---

### Section D: States

**Purpose**: Document state machines and state transitions in FDL

**Content requirements**:
- States written in FDL (see `../FDL.md`)
- State definitions with **WHEN** keyword (only valid in state machines)
- State transitions clearly documented
- **FDL Keywords for States**:
  - ✅ Allowed: **WHEN** (states only), **FROM**, **TO**, **IF**, **ELSE**
  - State machine format: numbered list with bold **WHEN** transitions

**Note**: Optional if feature has no state management

---

### Section E: Technical Details

**Purpose**: Implementation-specific technical information

**Size Constraint**: ≥200 lines recommended

**Required subsections**:
1. **Database Schema**: Tables/entities, columns, relationships (if applicable)
2. **API Endpoints**: Endpoint list with descriptions, reference API specification
3. **Security**: Authorization rules, access control
4. **Error Handling**: Error types and handling approaches

**Reference Requirements**:
- **Domain Model references**: Must be clickable links to domain model files
  - Format: `@/path/to/domain-model-file` or markdown links to GTS/schema files
  - Example: `User` type → link to `@/gts/user.gts` or domain model section
- **API Spec references**: Must be clickable links to API specification files
  - Format: `@/path/to/api-spec-file` or markdown links to OpenAPI/spec files
  - Example: `POST /users` → link to `@/openapi/users.yaml` or API spec section
- All external references must be verifiable and navigable

**Content requirements**:
- References to Overall Design domain model (no type redefinitions)
- References to Overall Design API contracts (no endpoint redefinitions)
- Sufficient detail for implementation
- External spec references where appropriate

---

### Section F: Requirements

**Purpose**: Formalized requirements with traceability

**Requirement ID Format**: `fdd-{project-name}-feature-{feature-slug}-req-{short-name}`
- **Components**:
  - `fdd-` - Prefix indicating FDD methodology
  - `{project-name}` - Project name in kebab-case (from project context)
  - `-feature-` - Feature scope indicator
  - `{feature-slug}` - Feature identifier in kebab-case
  - `-req-` - Requirement indicator
  - `{short-name}` - Short descriptive name in kebab-case (2-4 words)
- **Example**: `fdd-payment-system-feature-user-auth-req-login-flow`
- **Usage**: ID appears before requirement title for referencing from Section G

**Required content per requirement**:
- **ID**: Requirement ID in format above (for traceability)
- **Title**: `### {Title}` (simple title, no numbering)
- **Status**: ⏳ NOT_STARTED, 🔄 IN_PROGRESS, or ✅ IMPLEMENTED
- **Description**: Clear description with SHALL/MUST statements
- **References**: Markdown anchors to sections B-E (≥1 reference)
- **Testing Scenarios**: ≥1 test scenario in FDL format (numbered lists + plain English)
  - ❌ **NO Gherkin/BDD keywords**: **GIVEN**, **WHEN**, **THEN**, **AND** prohibited in Testing Scenarios
  - ✅ Use plain English: "User provides command", "System parses", "Verify output"
- **Acceptance Criteria**: ≥2 specific, testable criteria

**Validation**:
- ≥1 requirement present
- All requirements have all required fields
- References are valid (target sections exist)
- Testing scenarios use FDL format (not Gherkin)

---

### Section G: Implementation Plan

**Purpose**: List of OpenSpec changes implementing requirements

**Change Name Format**: `fdd-{project-name}-feature-{feature-slug}-change-{short-name}`
- **Components**:
  - `fdd-` - Prefix indicating FDD methodology
  - `{project-name}` - Project name in kebab-case (from project context)
  - `-feature-` - Feature scope indicator
  - `{feature-slug}` - Feature identifier in kebab-case
  - `-change-` - Change indicator
  - `{short-name}` - Short descriptive name in kebab-case (2-4 words)
- **Example**: `fdd-payment-system-feature-user-auth-change-login-implementation`
- **Must match**: OpenSpec change directory naming convention

**Required content per change**:
- **Format**: `1. **change-name** [status]` (numbered list, not subsections)
- **Change numbering**: 1, 2, 3, 4, etc. (sequential)
- **Status**: ⏳ NOT_STARTED, 🔄 IN_PROGRESS, ✅ COMPLETED
- **Description**: What will be implemented
- **Implements Requirements**: List of requirement IDs from Section F (1-5 per change)
  - Format: `fdd-{project}-feature-{feature}-req-{short-name}` (use actual requirement IDs)
  - Example: `fdd-payment-system-feature-user-auth-req-login-flow`, `fdd-payment-system-feature-user-auth-req-token-validation`
- **Dependencies**: Other change names or "None"

**Prohibited content**:
- ❌ Subsections like `### Active Changes`, `### Planned Changes`
- ❌ Grouping changes by status
- ❌ Any `###` headings within Section G

**Validation**:
- ≥1 change present
- All changes at same level (no subsections)
- Each change implements 1-5 requirements from Section F
- All Section F requirements referenced by ≥1 change
- Dependencies are valid

---

## Validation Criteria

### File-Level Validation

1. **File exists and size**
   - File `architecture/features/feature-{slug}/DESIGN.md` exists
   - File ≤4000 lines (warning if >3000)
   - File has substantial content

### Structure Validation

1. **All required sections present**
   - Sections A, B, C, D, E, F, G (7 sections)
   - Correct section order (A → B → C → D → E → F → G)
   - Each section has proper heading (`## A.`, `## B.`, etc.)
   - No duplicate sections

### Content Validation

1. **Section A (Feature Context)**
   - ≤500 lines
   - All required subsections present
   - References to Overall Design included
   - Actor names match Overall Design

2. **Section B (Actor Flows)**
   - ≥50 lines (standard features)
   - Uses FDL syntax (not code)
   - Only valid FDL keywords used
   - No prohibited keywords (**WHEN** in flows, **THEN**, **SET**, etc.)

3. **Section C (Algorithms)**
   - ≥100 lines (standard features)
   - Uses FDL syntax (not code)
   - No programming language code blocks
   - Only valid FDL keywords used

4. **Section D (States)**
   - Uses FDL syntax if applicable
   - **WHEN** keyword only in states (not flows/algorithms)

5. **Section E (Technical Details)**
   - ≥200 lines recommended
   - All technical aspects covered
   - References to Overall Design specs

6. **Section F (Requirements)**
   - ≥1 requirement present
   - Each requirement has all required fields
   - Testing Scenarios use FDL (not Gherkin)
   - References are valid markdown anchors
   - **Requirement ID Format Validation**:
     - All requirement IDs match format: `fdd-{project-name}-feature-{feature-slug}-req-{short-name}`
     - All IDs are unique within Section F
     - IDs use kebab-case (lowercase with hyphens)
     - Each requirement has its ID before title

7. **Section G (Implementation Plan)**
   - ≥1 change present
   - No subsections (flat structure)
   - All requirements from F covered
   - Dependencies valid
   - **Change Name Format Validation**:
     - All change names match format: `fdd-{project-name}-feature-{feature-slug}-change-{short-name}`
     - All change names are unique within Section G
     - Change names use kebab-case (lowercase with hyphens)
   - **Requirement Reference Validation**:
     - All requirement IDs referenced in "Implements Requirements" exist in Section F
     - Every requirement from Section F is referenced by ≥1 change
     - Each change implements 1-5 requirements (not 0, not >5)
   - **Dependency Validation**:
     - All dependencies reference valid change names from Section G
     - No circular dependencies between changes

### Cross-Validation with Overall Design

**CRITICAL**: Feature Design must align with Overall Design

**Domain Types**:
- ✅ All types referenced (not redefined) from Overall Design Section C
- ❌ No new type definitions in feature DESIGN.md
- Use DML notation per adapter

**API Endpoints**:
- ✅ All endpoints referenced from Overall Design Section C
- ❌ No new endpoint definitions in feature DESIGN.md

**Actors**:
- ✅ Only actors from Overall Design Section A
- ❌ No new actors invented in feature
- Actor roles match Overall Design

**Capabilities**:
- ✅ Feature aligns with Overall Design capabilities
- Feature scope matches Overall Design

### Completeness Validation

1. **No placeholders**
   - No TODO, TBD, FIXME, XXX markers
   - No `{placeholder}` content
   - All sections fully written

2. **No type redefinitions**
   - No phrases like "type definition"
   - No schema definitions in JSON/YAML blocks
   - All types referenced from Overall Design

---

## Output Requirements

### For Generator (Workflow 05)

**Generate**:
- File at `architecture/features/feature-{slug}/DESIGN.md`
- All required sections with headers
- Template content for each section
- Comments guiding what to fill

### For Validator (Workflow 06)

**Validate**:
1. File-level (exists, size)
2. Structure (all sections present, correct order)
3. Content (FDL syntax, no code, sufficient detail)
4. Cross-validation (alignment with Overall Design)
5. Completeness (no placeholders, no type redefinitions)

**Report format**:
- Score: X/100 (must be 100)
- Completeness: X% (must be 100%)
- Issues: List of missing/invalid items
- Recommendations: What to fix

**Scoring**:
- Structure (20 points): All sections present
- FDL Compliance (30 points): Sections B, C, D use valid FDL
- Technical Details (20 points): Section E complete
- Requirements (15 points): Section F formalized with tests
- Implementation Plan (15 points): Section G complete

---

## References

**Workflows using this**:
- `workflows/05-init-feature.md` - Generate feature DESIGN.md
- `workflows/06-validate-feature.md` - Validate feature DESIGN.md

**Related specifications**:
- `../FDL.md` - FDL syntax for flows, algorithms, states
- `overall-design-structure.md` - Overall Design structure
- `../AGENTS.md` - Core FDD rules

**Related workflows**:
- `workflows/02-validate-architecture.md` - Overall Design validation
- `workflows/09-openspec-change-next.md` - Next step after validation
