# Overall Design Structure Requirements

**Purpose**: Define required structure for `architecture/DESIGN.md`

**Used by**:
- Workflow 01 (init-project): Generate DESIGN.md template
- Workflow 02 (validate-architecture): Validate DESIGN.md completeness

---

## File Location

**Path**: `architecture/DESIGN.md`

**Size limits**:
- Recommended: ≤1000 lines
- Hard limit: No strict limit, but keep concise

---

## Required Sections

### Section A: Business Context

**Purpose**: Project vision, stakeholders, business goals

**Required subsections**:
1. **Project Vision** - High-level purpose and goals (2-3 paragraphs)
2. **Stakeholders** - Primary actors and their needs
3. **Success Criteria** - Measurable outcomes

**Content requirements**:
- Plain English, no technical jargon
- Focus on "why" not "how"
- Clear business value proposition

---

### Section B: Requirements & Principles

**Purpose**: Functional requirements, design principles, constraints

**Required subsections**:
1. **Functional Requirements** - What system must do
2. **Non-Functional Requirements** - Performance, scalability, etc.
3. **Design Principles** - Architectural guidelines
4. **Constraints** - Technical/business limitations

**Content requirements**:
- Requirements numbered (REQ-1, REQ-2, etc.)
- Each requirement: clear, testable, necessary
- Principles: actionable, not generic platitudes

---

### Section C: Technical Architecture

**Purpose**: System architecture, components, technologies

**Required subsections**:

#### C.1: System Architecture
- **Component diagram** (draw.io, Mermaid, or ASCII)
- **Component descriptions** - Purpose of each component
- **Component interactions** - How components communicate

#### C.2: Domain Model
- **Technology** - Specify format (GTS, JSON Schema, OpenAPI, etc.)
- **Location** - Path to domain model files
- **Core entities** - List main domain objects
- **Relationships** - Entity relationships overview

**⚠️ CRITICAL**: Domain model MUST be in machine-readable format
- ✅ Valid: GTS schemas, JSON Schema, OpenAPI, TypeScript types
- ❌ Invalid: Plain English descriptions, diagrams only

**Reference Requirements**:
- **Domain Model files**: Must be clickable links to actual schema/type files
  - Format: `@/path/to/domain-model-file` or markdown links
  - Example: `@/gts/user.gts`, `@/schemas/project.json`
- All domain model references must be verifiable and navigable

#### C.3: API Contracts
- **Technology** - Specify format (REST/OpenAPI, GraphQL, gRPC, CLISPEC)
- **Location** - Path to API contract files
- **Endpoints overview** - List main API surfaces

**⚠️ CRITICAL**: API contracts MUST be in machine-readable format
- ✅ Valid: OpenAPI spec, GraphQL schema, CLISPEC, proto files
- ❌ Invalid: Plain English descriptions, curl examples only

**Reference Requirements**:
- **API Spec files**: Must be clickable links to actual specification files
  - Format: `@/path/to/api-spec-file` or markdown links
  - Example: `@/openapi/users.yaml`, `@/spec/CLI/commands.clispec`
- All API contract references must be verifiable and navigable

#### C.4: Security Model
- Authentication approach
- Authorization approach  
- Data protection
- Security boundaries

**Note**: Can be "No security" for CLI tools, internal systems

#### C.5: Non-Functional Requirements
- Performance requirements
- Scalability requirements
- Reliability/Availability requirements
- Other quality attributes

**Note**: Include NFRs relevant to project type

---

### Section D: Architecture Decision Records (ADR)

**Purpose**: Track all significant architectural decisions and changes to Overall Design

**Format**: Use industry-standard MADR (Markdown Any Decision Records) format

**Content**: See "Architecture Decision Records (ADR)" section below for full format specification

**Required**: At least ADR-0001 documenting initial architecture decisions

---

### Section E: Project-Specific Details (OPTIONAL)

**Purpose**: Additional project context not covered by core FDD structure

**Content**:
- Integration requirements
- Performance constraints
- Compliance requirements
- Migration notes
- Deployment context
- Any other project-specific information

**Note**: This section is optional and only included if project has specific context to document. Not validated by FDD core validation.

---

## Validation Criteria

### File-Level Validation

1. **File exists and has adequate content**
   - File `architecture/DESIGN.md` exists
   - File contains ≥200 lines (recommended: 500-2000 lines)
   - File is not empty or placeholder-only

### Structure Validation

1. **All required sections present**
   - Section A with all subsections
   - Section B with all subsections
   - Section C with all subsections (C.1-C.5)
   - Section D (Architecture Decision Records) - REQUIRED (at least ADR-0001)
   - Section E optional (not validated)

2. **Section order correct**
   - A → B → C → D → E (in this exact order)
   - Section E may be omitted

3. **No prohibited sections**
   - No top-level sections F or beyond (F, G, H, etc.)
   - Only A-E allowed at top level (E is optional)
   - Section C has exactly 5 subsections (C.1-C.5)
   - Section D contains ADR entries

4. **Markdown formatting valid**
   - Headers use proper levels (## for A-D, ### for C.1-C.5)
   - No malformed markdown

### Content Validation

1. **Domain Model accessible**
   - Files at specified location exist
   - Files are in specified format (parseable)
   - No broken references

2. **API Contracts accessible**
   - Files at specified location exist
   - Files are in specified format (parseable)
   - No broken references

3. **Component diagram present**
   - At least one diagram in Section C.1
   - Can be embedded image, Mermaid code, or ASCII art

4. **No placeholders remain**
   - No TODO markers
   - No TBD (To Be Determined) placeholders
   - No FIXME comments
   - No empty or stub sections
   - All sections have substantive content

5. **Domain type identifiers use complete format**
   - Must include namespace/module identifier
   - Must include type name
   - Must include version
   - Format defined by adapter (e.g., `gts.namespace.type.v1` for GTS)
   - No short-form identifiers without namespace
   - Notation consistent throughout document

6. **Capability dependencies are acyclic**
   - If capabilities reference each other, no circular dependencies
   - Dependency graph must be acyclic (DAG)
   - Clear implementation order exists

---

## Output Requirements

### For Generator (Workflow 01)

**Generate**:
- File at `architecture/DESIGN.md`
- All required sections with headers
- Placeholder content for each subsection
- Comments guiding what to fill

**Template markers**:
- Use `<!-- TODO: ... -->` for sections needing input
- Use `[DESCRIBE: ...]` for inline placeholders

### For Validator (Workflow 02)

**Validate**:
1. Structure completeness (sections, subsections)
2. Domain model accessibility (files exist, parseable)
3. API contracts accessibility (files exist, parseable)
4. Content substantiveness (no empty sections)

**Report format**:
- Score: X/100 (must be ≥90)
- Completeness: X% (must be 100%)
- Issues: List of missing/invalid items
- Recommendations: What to fix

**Scoring**:
- Structure (30 points): All sections present
- Domain Model (25 points): Valid machine-readable format
- API Contracts (25 points): Valid machine-readable format
- Content Quality (20 points): Substantive, no placeholders

---

## Examples

### Valid Domain Model Specification

```markdown
#### C.2: Domain Model

**Technology**: GTS (Global Type System) + JSON Schema

**Location**: `gts/`

**Core entities**:
- `user` - User account and profile
- `project` - FDD project container
- `feature` - Individual feature specification

**Relationships**:
- User owns multiple Projects
- Project contains multiple Features
```

### Invalid Domain Model Specification

```markdown
#### C.2: Domain Model

We use a standard entity-relationship model with users, projects, and features.
Users can own projects and projects contain features.
```
❌ No technology specified, no file location, not machine-readable

---

## Architecture Decision Records (ADR)

**Purpose**: Track all significant architectural decisions and changes to Overall Design

**Location**: Section D in `architecture/DESIGN.md`

**Format**: Use industry-standard MADR (Markdown Any Decision Records) format

### ADR Entry Format

```markdown
## ADR-NNNN: [Decision Title]

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated | Superseded
**Deciders**: [Names/Roles]
**Technical Story**: [Issue/Feature reference if applicable]

### Context and Problem Statement

[Describe the context and problem that led to this decision]

### Decision Drivers

- [Driver 1]
- [Driver 2]
- [Driver 3]

### Considered Options

1. **Option 1**: [Brief description]
2. **Option 2**: [Brief description]
3. **Option 3**: [Brief description]

### Decision Outcome

**Chosen option**: "[Option X]", because [justification]

**Positive Consequences**:
- [Consequence 1]
- [Consequence 2]

**Negative Consequences**:
- [Consequence 1]
- [Consequence 2]

### Implementation Notes

[How this decision affects the architecture sections A-D]

**Sections affected**:
- Section A: [Changes if any]
- Section B: [Changes if any]
- Section C: [Changes if any]
```

### ADR Numbering

- **Format**: `ADR-NNNN` where NNNN is a zero-padded 4-digit number
- **Sequence**: Start at ADR-0001, increment for each new decision
- **Examples**: ADR-0001, ADR-0002, ADR-0023, ADR-0142

### ADR Statuses

- **Proposed**: Decision is under discussion, not yet accepted
- **Accepted**: Decision has been approved and is active
- **Deprecated**: Decision is no longer recommended but not yet replaced
- **Superseded**: Decision has been replaced by another ADR (reference new ADR number)

### When to Create ADR

**MUST create ADR for**:
- Technology stack changes (domain model format, API contract format)
- Architectural pattern changes (layering, communication patterns)
- Major component additions or removals
- Security approach changes
- Data storage or persistence strategy changes
- API design principles changes

**SHOULD create ADR for**:
- Non-functional requirement changes
- Capability structure changes
- Actor definition changes

**Optional ADR for**:
- Minor clarifications or wording improvements
- Documentation structure changes
- Non-architectural updates

### ADR Validation

**Required**:
- All ADRs have valid format (all sections present)
- ADR numbers are sequential (no gaps, no duplicates)
- Dates are in YYYY-MM-DD format
- Status is one of: Proposed, Accepted, Deprecated, Superseded
- Superseded ADRs reference the new ADR number

---

## References

**Workflows using this**:
- `workflows/01-init-project.md` - Generate DESIGN.md
- `workflows/02-validate-architecture.md` - Validate DESIGN.md

**Related requirements**:
- `feature-design-structure.md` - Feature DESIGN.md structure
- `adapter-structure.md` - Adapter AGENTS.md structure
