<!-- cpt:#:decomposition -->
# Decomposition: {PROJECT_NAME}

<!-- cpt:##:overview -->
## 1. Overview

{ Description of how the DESIGN was decomposed into specs, the decomposition strategy, and any relevant decomposition rationale. }


<!-- cpt:##:overview -->

<!-- cpt:##:entries -->
## 2. Entries

**Overall implementation status:**
<!-- cpt:id:status has="priority,task" -->
- [ ] `p1` - **ID**: `cpt-{system}-status-overall`

<!-- cpt:###:spec-title repeat="many" -->
### 1. [{Spec Title 1}](spec-{slug}/) - HIGH

<!-- cpt:id:spec has="priority,task" -->
- [ ] `p1` - **ID**: `cpt-{system}-spec-{slug}`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: {Few sentences describing what this spec accomplishes and why it matters}
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: None
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - {in-scope item 1}
  - {in-scope item 2}
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - {out-of-scope item 1}
  - {out-of-scope item 2}
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [ ] `p1` - `cpt-{system}-fr-{slug}`
  - [ ] `p1` - `cpt-{system}-nfr-{slug}`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [ ] `p1` - `cpt-{system}-principle-{slug}`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [ ] `p1` - `cpt-{system}-constraint-{slug}`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - {entity 1}
  - {entity 2}
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [ ] `p1` - `cpt-{system}-component-{slug}`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - POST /api/{resource}
  - GET /api/{resource}/{id}
  - {CLI command}
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [ ] `p1` - `cpt-{system}-seq-{slug}`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [ ] `p1` - `cpt-{system}-dbtable-{slug}`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:###:spec-title repeat="many" -->
### 2. [{Spec Title 2}](spec-{slug}/) - MEDIUM

<!-- cpt:id:spec has="priority,task" -->
- [ ] `p2` - **ID**: `cpt-{system}-spec-{slug}`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: {Few sentences describing what this spec accomplishes and why it matters}
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: `cpt-{system}-spec-{slug}` (previous spec)
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - {in-scope item 1}
  - {in-scope item 2}
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - {out-of-scope item 1}
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [ ] `p2` - `cpt-{system}-fr-{slug}`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [ ] `p2` - `cpt-{system}-principle-{slug}`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [ ] `p2` - `cpt-{system}-constraint-{slug}`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - {entity}
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [ ] `p2` - `cpt-{system}-component-{slug}`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - PUT /api/{resource}/{id}
  - DELETE /api/{resource}/{id}
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [ ] `p2` - `cpt-{system}-seq-{slug}`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [ ] `p2` - `cpt-{system}-dbtable-{slug}`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:###:spec-title repeat="many" -->
### 3. [{Spec Title 3}](spec-{slug}/) - LOW

<!-- cpt:id:spec has="priority,task" -->
- [ ] `p3` - **ID**: `cpt-{system}-spec-{slug}`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: {Few sentences describing what this spec accomplishes and why it matters}
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: `cpt-{system}-spec-{slug}`
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - {in-scope item}
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - {out-of-scope item}
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [ ] `p3` - `cpt-{system}-fr-{slug}`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [ ] `p3` - `cpt-{system}-principle-{slug}`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [ ] `p3` - `cpt-{system}-constraint-{slug}`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - {entity}
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [ ] `p3` - `cpt-{system}-component-{slug}`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - GET /api/{resource}/stats
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [ ] `p3` - `cpt-{system}-seq-{slug}`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [ ] `p3` - `cpt-{system}-dbtable-{slug}`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:id:status -->
<!-- cpt:##:entries -->
<!-- cpt:#:decomposition -->
