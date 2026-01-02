# Initialize Features from Overall Design

**Phase**: 2 - Feature Planning  
**Purpose**: Analyze Overall Design and generate feature list with dependencies

---

## Prerequisites

- Overall Design validated (run `02-validate-architecture.md` first)
- `architecture/DESIGN.md` complete with all sections
- `architecture/features/` directory exists

## Input Parameters

- **module-name**: Name of the module (lowercase)

---

## Requirements

### 1. Analyze System Capabilities

**Requirement**: Extract and understand core capabilities from Overall Design

**Input Source**:
- Section A (Vision & Capabilities) of `architecture/DESIGN.md`
- Specifically the "Core Capabilities" subsection

**Required Understanding**:
- What main functional areas system provides
- How capabilities relate to each other
- Which capabilities are foundational vs. dependent

**Expected Outcome**: Clear list of system capabilities ready for feature mapping

**Validation Criteria**:
- All capabilities from Section A identified
- Capability relationships understood
- Capability scope clear

---

### 2. Map Capabilities to Features

**Requirement**: Break down capabilities into implementable features

**Planning Guidelines**:
- **First feature**: Always `feature-init` (infrastructure, no dependencies)
- **Capability mapping**: Create 1-3 features per major capability
- **Feature scope**: Each feature focused and independently testable
- **Dependencies**: Define clear dependency relationships

**Feature Naming**:
- Format: `feature-{descriptive-name}`
- Lowercase with hyphens
- Descriptive of functionality

**Expected Outcome**: Complete feature breakdown with dependencies

**Validation Criteria**:
- All capabilities covered by features
- Feature scopes clearly defined
- Dependencies identified
- init is first feature

---

### 3. Create Features Manifest Document

**Requirement**: Document all planned features in structured manifest

**Required File**: `architecture/features/FEATURES.md`

**Required Content Structure**:

**Header**:
- Module name
- Overall status (PLANNING initially)

**For Each Feature**:
- **Feature slug**: Unique identifier (e.g., `feature-init`)
- **Status**: Current state (⏳ NOT_STARTED, 🔄 IN_PROGRESS, ✅ IMPLEMENTED)
- **Priority**: Importance level (CRITICAL, HIGH, MEDIUM, LOW)
- **Depends On**: List of prerequisite features or "None"
- **Blocks**: List of features that depend on this feature or "None" (calculated from reverse "Depends On" relationships)
- **Purpose**: One-line description of feature goal
- **Scope**: Bulleted list of what feature creates/implements

**Additional Sections**:
- **Feature Dependencies**: Visual dependency graph
- **Implementation Order**: Numbered list in execution order

**Critical Requirements**:
- `feature-init` MUST be feature #1
- init MUST have "Depends On: None"
- Dependencies must form valid DAG (no cycles)
- Implementation order must respect dependencies

**Expected Outcome**: Complete feature manifest ready for implementation

**Validation Criteria**:
- File `architecture/features/FEATURES.md` exists
- All features documented with required fields
- init is first feature
- Dependency graph is acyclic
- Implementation order valid

---

### 4. Initialize Init Design Document

**Requirement**: Create design document for init feature

**Required File**: `architecture/features/feature-init/DESIGN.md`

**Content Requirements**:
- **Section A**: Feature context (minimal for init)
- **Section B**: Actor flows (intentionally minimal - structural task)
- **Section C**: Algorithms (intentionally minimal - structural task)
- **Section D**: States (not applicable)
- **Section E**: Technical details (structure being created)
- **Section F**: Validation & implementation (compilation tests)

**Critical Constraints**:
- Init is **structural only** - NO business logic
- Minimal sections B and C acceptable for init
- Focus on what structure is created, not what it does

**Note**: Framework-specific init templates defined in project adapter documentation

**Expected Outcome**: Init design document exists

**Validation Criteria**:
- File `architecture/features/feature-init/DESIGN.md` exists
- Contains all sections A-F
- Clearly defines structural scope
- No business logic described

**Commands**:
```bash
mkdir -p features/feature-init

# Generic init template
cat > features/feature-init/DESIGN.md << 'EOF'
# Init - Feature Design

**Status**: ⏳ NOT_STARTED  
**Module**: {Module Name}

---

## A. Feature Context

### Overview

Create minimal project structure. This establishes the compilable skeleton for business features.

**Critical Scope Constraint**: Init creates **structure only**, NO business logic.

### Purpose

Initialize the project with:
- Empty compilable structure
- Framework integration
- Layer folders ready for features

### Actors

- **Developer/Architect**: Creates project structure

### References

- Overall Design: `@/architecture/DESIGN.md`

### What Init IS vs IS NOT

**Init creates** (✅):
- Project structure
- Configuration scaffolding
- Empty layers/folders

**Init does NOT create** (❌):
- Business logic
- API definitions
- Database entities
- Any domain-specific code

---

## B. Actor Flows

*Intentionally minimal for init.*

Developer runs init → creates skeleton → verifies compilation.

---

## C. Algorithms

*Intentionally minimal for init.*

See implementation for details.

---

## D. States

*Not applicable* (use FDL if needed - see `../FDL.md`)

---

## E. Technical Details

### Structure Created

(Framework-specific - see adapter documentation)

---

## F. Validation & Implementation

### Testing

1. **Compilation Test**: Verify structure compiles
2. **Integration Test**: Verify framework registration

### Implementation

Implementation steps defined in framework adapter.

---
EOF
```

**Expected Result**: Init DESIGN.md created

**Note**: For framework-specific init templates, see project adapter documentation

---

### 5. Create Placeholder Design Documents

**Requirement**: Initialize design documents for all other features

**Required Files**:
- One DESIGN.md per feature in `architecture/features/feature-{slug}/`
- Exclude init (already created in previous requirement)

**Content Requirements**:
- Basic template with sections A-F
- Status: ⏳ NOT_STARTED
- Placeholder text indicating design pending
- Reference to Overall Design

**Purpose**: Establish feature structure, content filled during feature initialization workflow

**Expected Outcome**: All feature directories have initial DESIGN.md

**Validation Criteria**:
- Each feature has directory `architecture/features/feature-{slug}/`
- Each directory contains `DESIGN.md`
- Files have basic structure
- Status marked as NOT_STARTED

**Commands**:
```bash
# For each feature (except init)
for FEATURE in feature-{name} feature-{name2}; do
  mkdir -p features/$FEATURE
  
  cat > features/$FEATURE/DESIGN.md << EOF
# {Feature Name} - Feature Design

**Status**: ⏳ NOT_STARTED

## A. Feature Context

### Overview

{To be designed after Overall Design is finalized}

### Purpose

{Define purpose}

---

## B. Actor Flows

{To be designed}

---

## C. Algorithms

{To be designed}

---

## D. States

{To be designed if needed - use FDL, see `../FDL.md`}

---

## E. Technical Details

{To be designed}

---

## F. Validation & Implementation

{To be designed}

---
EOF
done
```

**Expected Result**: Placeholder designs created

---

### 6. Validate Features Manifest Structure

**Action**: Run validation on FEATURES.md

**Commands**:
```bash
# Check init is first
FIRST_FEATURE=$(grep "^### [0-9]\." features/FEATURES.md | head -1)
if ! echo "$FIRST_FEATURE" | grep -q "feature-init"; then
  echo "ERROR: init must be first feature"
  exit 1
fi

# Check dependencies valid
echo "✓ init is first feature"
echo "✓ Features manifest created"
```

**Expected Result**: Validation passes

---

## Completion Criteria

Feature initialization is complete when:

- [ ] FEATURES.md created with all features listed
- [ ] init is first feature
- [ ] All features have: status, priority, dependencies, blocks, purpose, scope
- [ ] Blocks field consistent with Depends On (reverse dependencies)
- [ ] feature-init/DESIGN.md created
- [ ] Placeholder designs created for other features
- [ ] Feature dependency graph valid (no cycles)

---

## Common Challenges

### Challenge: Feature Granularity

**Resolution**: Each feature should be implementable in 1-4 weeks. If larger, break into multiple features. If smaller, consider combining. Aim for 3-7 initial features.

### Challenge: Complex Dependencies

**Resolution**: Create dependency diagram before documenting. Ensure no circular dependencies. If dependencies complex, may indicate need for feature restructuring.

### Challenge: Unclear Feature Boundaries

**Resolution**: Each feature should have single clear purpose. If feature scope unclear, likely combining multiple concerns. Split into separate features.

---

## Next Activities

After feature initialization:

1. **Develop Init**: Start feature development workflow for init
   - Complete init DESIGN.md
   - Validate design
   - Implement structure

2. **Develop Remaining Features**: Follow implementation order from manifest
   - Initialize next feature
   - Complete design
   - Validate
   - Implement

---

## References

- **Core FDD**: `../AGENTS.md` - Feature planning
- **Next Workflow**: `04-validate-features.md` then `05-init-feature.md`
