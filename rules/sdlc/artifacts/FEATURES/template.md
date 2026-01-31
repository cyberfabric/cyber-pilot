---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: FEATURES
  unknown_sections: warn
---

# Features: {PROJECT_NAME}

<!-- fdd:#:features -->
# Features

<!-- fdd:##:status-overview -->
## A. Status Overview

<!-- fdd:line:status-overview required="true" -->
**Status Overview**: {N} features total ({N} implemented, {N} in development, {N} design ready, {N} in design, {N} not started)
<!-- fdd:line:status-overview -->

**Meaning**:
<!-- fdd:list:status-meaning required="true" -->
- ⏳ NOT_STARTED
- 📝 IN_DESIGN
- 📘 DESIGN_READY
- 🔄 IN_DEVELOPMENT
- ✅ IMPLEMENTED
<!-- fdd:list:status-meaning -->

<!-- fdd:line:status-separator -->
---
<!-- fdd:line:status-separator -->
<!-- fdd:##:status-overview -->

<!-- fdd:##:entries -->
## B. Entries

<!-- fdd:###:feature-title repeat="many" -->
### 1. [{Feature Title}](feature-{slug}/) ⏳ MEDIUM

<!-- fdd:id:feature has="priority,task" -->
**ID**: [ ] `p1` - `fdd-{project}-feature-{slug}`
<!-- fdd:id:feature -->

<!-- fdd:list:feature-entry -->
- **Purpose**: {Few sentences}
- **Status**: NOT_STARTED
- **Depends On**: None
- **Blocks**: None
- **Scope**:
  - {in-scope item}
  - {in-scope item}
- **Requirements Covered**:
  - `fdd-{project}-fr-{slug}`
  - `fdd-{project}-nfr-{slug}`
- **Design Principles Covered**:
  - `fdd-{project}-principle-{slug}`
- **Design Constraints Covered**:
  - `fdd-{project}-constraint-{slug}`
- **Domain Model Entities**:
  - {entity/type/object}
- **Design Components**:
  - `fdd-{project}-component-{slug}`
- **API**:
  - /{resource-name}
  - {CLI command}
- **Sequences**:
  - `fdd-{project}-seq-{slug}`
- **Data**:
  - `fdd-{project}-db-table-{slug}`
- **Phases**:
  - `p1`: ⏳ NOT_STARTED — {scope}
  - `p2`: ⏳ NOT_STARTED — {scope}
<!-- fdd:list:feature-entry -->

<!-- fdd:###:feature-title repeat="many" -->
<!-- fdd:##:entries -->
<!-- fdd:#:features -->
