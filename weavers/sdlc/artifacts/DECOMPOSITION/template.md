<!-- spd:#:decomposition -->
# Decomposition: {PROJECT_NAME}

<!-- spd:##:overview -->
## 1. Overview

{ Description of how the DESIGN was decomposed into specs, the decomposition strategy, and any relevant decomposition rationale. }


<!-- spd:##:overview -->

<!-- spd:##:entries -->
## 2. Entries

**Overall implementation status:**
<!-- spd:id:status has="priority,task" -->
- [ ] `p1` - **ID**: `spd-{system}-status-overall`

<!-- spd:###:spec-title repeat="many" -->
### 1. [{Spec Title 1}](spec-{slug}/) - HIGH

<!-- spd:id:spec has="priority,task" -->
- [ ] `p1` - **ID**: `spd-{system}-spec-{slug}`

<!-- spd:paragraph:spec-purpose required="true" -->
- **Purpose**: {Few sentences describing what this spec accomplishes and why it matters}
<!-- spd:paragraph:spec-purpose -->

<!-- spd:paragraph:spec-depends -->
- **Depends On**: None
<!-- spd:paragraph:spec-depends -->

<!-- spd:list:spec-scope -->
- **Scope**:
  - {in-scope item 1}
  - {in-scope item 2}
<!-- spd:list:spec-scope -->

<!-- spd:list:spec-out-scope -->
- **Out of scope**:
  - {out-of-scope item 1}
  - {out-of-scope item 2}
<!-- spd:list:spec-out-scope -->

- **Requirements Covered**:
<!-- spd:id-ref:fr has="priority,task" -->
  - [ ] `p1` - `spd-{system}-fr-{slug}`
  - [ ] `p1` - `spd-{system}-nfr-{slug}`
<!-- spd:id-ref:fr -->

- **Design Principles Covered**:
<!-- spd:id-ref:principle has="priority,task" -->
  - [ ] `p1` - `spd-{system}-principle-{slug}`
<!-- spd:id-ref:principle -->

- **Design Constraints Covered**:
<!-- spd:id-ref:constraint has="priority,task" -->
  - [ ] `p1` - `spd-{system}-constraint-{slug}`
<!-- spd:id-ref:constraint -->

<!-- spd:list:spec-domain-entities -->
- **Domain Model Entities**:
  - {entity 1}
  - {entity 2}
<!-- spd:list:spec-domain-entities -->

- **Design Components**:
<!-- spd:id-ref:component has="priority,task" -->
  - [ ] `p1` - `spd-{system}-component-{slug}`
<!-- spd:id-ref:component -->

<!-- spd:list:spec-api -->
- **API**:
  - POST /api/{resource}
  - GET /api/{resource}/{id}
  - {CLI command}
<!-- spd:list:spec-api -->

- **Sequences**:
<!-- spd:id-ref:seq has="priority,task" -->
  - [ ] `p1` - `spd-{system}-seq-{slug}`
<!-- spd:id-ref:seq -->

- **Data**:
<!-- spd:id-ref:dbtable has="priority,task" -->
  - [ ] `p1` - `spd-{system}-dbtable-{slug}`
<!-- spd:id-ref:dbtable -->

<!-- spd:id:spec -->
<!-- spd:###:spec-title repeat="many" -->

<!-- spd:###:spec-title repeat="many" -->
### 2. [{Spec Title 2}](spec-{slug}/) - MEDIUM

<!-- spd:id:spec has="priority,task" -->
- [ ] `p2` - **ID**: `spd-{system}-spec-{slug}`

<!-- spd:paragraph:spec-purpose required="true" -->
- **Purpose**: {Few sentences describing what this spec accomplishes and why it matters}
<!-- spd:paragraph:spec-purpose -->

<!-- spd:paragraph:spec-depends -->
- **Depends On**: `spd-{system}-spec-{slug}` (previous spec)
<!-- spd:paragraph:spec-depends -->

<!-- spd:list:spec-scope -->
- **Scope**:
  - {in-scope item 1}
  - {in-scope item 2}
<!-- spd:list:spec-scope -->

<!-- spd:list:spec-out-scope -->
- **Out of scope**:
  - {out-of-scope item 1}
<!-- spd:list:spec-out-scope -->

- **Requirements Covered**:
<!-- spd:id-ref:fr has="priority,task" -->
  - [ ] `p2` - `spd-{system}-fr-{slug}`
<!-- spd:id-ref:fr -->

- **Design Principles Covered**:
<!-- spd:id-ref:principle has="priority,task" -->
  - [ ] `p2` - `spd-{system}-principle-{slug}`
<!-- spd:id-ref:principle -->

- **Design Constraints Covered**:
<!-- spd:id-ref:constraint has="priority,task" -->
  - [ ] `p2` - `spd-{system}-constraint-{slug}`
<!-- spd:id-ref:constraint -->

<!-- spd:list:spec-domain-entities -->
- **Domain Model Entities**:
  - {entity}
<!-- spd:list:spec-domain-entities -->

- **Design Components**:
<!-- spd:id-ref:component has="priority,task" -->
  - [ ] `p2` - `spd-{system}-component-{slug}`
<!-- spd:id-ref:component -->

<!-- spd:list:spec-api -->
- **API**:
  - PUT /api/{resource}/{id}
  - DELETE /api/{resource}/{id}
<!-- spd:list:spec-api -->

- **Sequences**:
<!-- spd:id-ref:seq has="priority,task" -->
  - [ ] `p2` - `spd-{system}-seq-{slug}`
<!-- spd:id-ref:seq -->

- **Data**:
<!-- spd:id-ref:dbtable has="priority,task" -->
  - [ ] `p2` - `spd-{system}-dbtable-{slug}`
<!-- spd:id-ref:dbtable -->

<!-- spd:id:spec -->
<!-- spd:###:spec-title repeat="many" -->

<!-- spd:###:spec-title repeat="many" -->
### 3. [{Spec Title 3}](spec-{slug}/) - LOW

<!-- spd:id:spec has="priority,task" -->
- [ ] `p3` - **ID**: `spd-{system}-spec-{slug}`

<!-- spd:paragraph:spec-purpose required="true" -->
- **Purpose**: {Few sentences describing what this spec accomplishes and why it matters}
<!-- spd:paragraph:spec-purpose -->

<!-- spd:paragraph:spec-depends -->
- **Depends On**: `spd-{system}-spec-{slug}`
<!-- spd:paragraph:spec-depends -->

<!-- spd:list:spec-scope -->
- **Scope**:
  - {in-scope item}
<!-- spd:list:spec-scope -->

<!-- spd:list:spec-out-scope -->
- **Out of scope**:
  - {out-of-scope item}
<!-- spd:list:spec-out-scope -->

- **Requirements Covered**:
<!-- spd:id-ref:fr has="priority,task" -->
  - [ ] `p3` - `spd-{system}-fr-{slug}`
<!-- spd:id-ref:fr -->

- **Design Principles Covered**:
<!-- spd:id-ref:principle has="priority,task" -->
  - [ ] `p3` - `spd-{system}-principle-{slug}`
<!-- spd:id-ref:principle -->

- **Design Constraints Covered**:
<!-- spd:id-ref:constraint has="priority,task" -->
  - [ ] `p3` - `spd-{system}-constraint-{slug}`
<!-- spd:id-ref:constraint -->

<!-- spd:list:spec-domain-entities -->
- **Domain Model Entities**:
  - {entity}
<!-- spd:list:spec-domain-entities -->

- **Design Components**:
<!-- spd:id-ref:component has="priority,task" -->
  - [ ] `p3` - `spd-{system}-component-{slug}`
<!-- spd:id-ref:component -->

<!-- spd:list:spec-api -->
- **API**:
  - GET /api/{resource}/stats
<!-- spd:list:spec-api -->

- **Sequences**:
<!-- spd:id-ref:seq has="priority,task" -->
  - [ ] `p3` - `spd-{system}-seq-{slug}`
<!-- spd:id-ref:seq -->

- **Data**:
<!-- spd:id-ref:dbtable has="priority,task" -->
  - [ ] `p3` - `spd-{system}-dbtable-{slug}`
<!-- spd:id-ref:dbtable -->

<!-- spd:id:spec -->
<!-- spd:###:spec-title repeat="many" -->

<!-- spd:id:status -->
<!-- spd:##:entries -->
<!-- spd:#:decomposition -->
