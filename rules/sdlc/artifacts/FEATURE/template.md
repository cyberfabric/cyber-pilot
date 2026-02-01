---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: FEATURE
  unknown_sections: warn
---

<!-- fdd:#:feature-design -->
# Feature: {Feature Name}

<!-- fdd:id-ref:feature has="task" -->
[ ] - `fdd-{system}-feature-{feature-slug}`
<!-- fdd:id-ref:feature -->

<!-- fdd:##:context -->
## 1. Feature Context

<!-- fdd:overview -->
### 1. Overview
{1-2 paragraphs summarizing what this feature does and why it exists.}

{Include:
- Problem statement
- Primary user value
- Key assumptions}
<!-- fdd:overview -->

<!-- fdd:paragraph:purpose -->
### 2. Purpose
{1-3 sentences describing the intended outcome of this feature.}

{Optionally include measurable success criteria.}
<!-- fdd:paragraph:purpose -->

### 3. Actors
<!-- fdd:id-ref:actor -->
- `fdd-{system}-actor-{slug}`
- `fdd-{system}-actor-{slug}`
<!-- fdd:id-ref:actor -->

<!-- fdd:list:references -->
### 4. References
- Overall Design: [DESIGN.md](../../DESIGN.md)
- ADRs: `fdd-{system}-adr-{slug}`
- Related feature: `fdd-{system}-feature-{slug}`
<!-- fdd:list:references -->
<!-- fdd:##:context -->

<!-- fdd:##:flows -->
## 2. Actor Flows

<!-- fdd:###:flow-title repeat="many" -->
### {Flow Name}

<!-- fdd:id:flow has="task" to_code="true" -->
- [ ] **ID**: `fdd-{system}-feature-{feature}-flow-{slug}`

**Actors**:
<!-- fdd:id-ref:actor -->
- `fdd-{system}-actor-{slug}`
<!-- fdd:id-ref:actor -->

<!-- fdd:fdl:flow-steps -->
1. [ ] - `p1` - Actor fills form (field1, field2) - `inst-fill-form`
2. [ ] - `p1` - API: POST /api/{resource} (body: field1, field2) - `inst-api-call`
3. [ ] - `p2` - Algorithm: validate input using <!-- fdd:id-ref:algo has="task" required="false" -->[ ] - `fdd-{system}-feature-{feature}-algo-{slug}`<!-- fdd:id-ref:algo --> - `inst-run-algo`
4. [ ] - `p1` - DB: INSERT {table}(field1, field2, status) - `inst-db-insert`
5. [ ] - `p1` - DB: SELECT * FROM {table} WHERE condition - `inst-db-query`
6. [ ] - `p1` - File: READ config from {path} - `inst-file-read`
7. [ ] - `p1` - CLI: run `command --flag value` - `inst-cli-exec`
8. [ ] - `p1` - State: transition using <!-- fdd:id-ref:state has="task" required="false" --> [ ] - `fdd-{system}-feature-{feature}-state-{slug}`<!-- fdd:id-ref:state --> - `inst-state-ref`
9. [ ] - `p2` - **IF** {condition}: - `inst-if`
   1. [ ] - `p2` - {nested step} - `inst-if-nested`
10. [ ] - `p1` - API: RETURN 201 Created (id, status) - `inst-return`
<!-- fdd:fdl:flow-steps -->
<!-- fdd:id:flow -->
<!-- fdd:###:flow-title repeat="many" -->
<!-- fdd:##:flows -->

<!-- fdd:##:algorithms -->
## 3. Algorithms

<!-- fdd:###:algo-title repeat="many" -->
### {Algorithm Name}

<!-- fdd:id:algo has="task" to_code="true" -->
- [ ] **ID**: `fdd-{system}-feature-{feature}-algo-{slug}`

<!-- fdd:fdl:algo-steps -->
1. [ ] - `p1` - **IF** {field} is empty **RETURN** error "{validation message}" - `inst-validate`
2. [ ] - `p1` - retrieve {entity} from repository by {criteria} - `inst-fetch`
3. [ ] - `p1` - calculate {result} based on {business rule description} - `inst-calc`
4. [ ] - `p1` - transform {source data} into {target format} - `inst-transform`
5. [ ] - `p1` - **FOR EACH** {item} in {collection}: - `inst-loop`
   1. [ ] - `p1` - apply {operation} to {item} - `inst-loop-body`
6. [ ] - `p1` - normalize {data} according to {domain rules} - `inst-normalize`
7. [ ] - `p1` - **RETURN** {result description} - `inst-return`
<!-- fdd:fdl:algo-steps -->
<!-- fdd:id:algo -->
<!-- fdd:###:algo-title repeat="many" -->
<!-- fdd:##:algorithms -->

<!-- fdd:##:states -->
## 4. States

<!-- fdd:###:state-title repeat="many" -->
### {State Machine Name}

<!-- fdd:id:state has="task" to_code="true" -->
- [ ] **ID**: `fdd-{system}-feature-{feature}-state-{slug}`

<!-- fdd:fdl:state-transitions -->
1. [ ] - `p1` - **FROM** {STATE} **TO** {STATE} **WHEN** {trigger} - `inst-transition-1`
2. [ ] - `p1` - **FROM** {STATE} **TO** {STATE} **WHEN** {trigger} - `inst-transition-2`
<!-- fdd:fdl:state-transitions -->
<!-- fdd:id:state -->
<!-- fdd:###:state-title repeat="many" -->
<!-- fdd:##:states -->

<!-- fdd:##:requirements -->
## 5. Definition of Done

<!-- fdd:###:req-title repeat="many" -->
### {Requirement Name}

<!-- fdd:id:req has="priority,task" to_code="true" -->
- [ ] `p1` - **ID**: `fdd-{system}-feature-{feature}-req-{slug}`

<!-- fdd:paragraph:req-body -->
{Describe what must be true when this requirement is satisfied.}
<!-- fdd:paragraph:req-body -->

<!-- fdd:list:req-impl -->
**Implementation details**:
- API: {endpoints}
- DB: {tables/queries}
- Domain: {entities}
<!-- fdd:list:req-impl -->

**Implements**:
<!-- fdd:id-ref:flow has="priority" -->
- `p1` - `fdd-{system}-feature-{feature}-flow-{slug}`
<!-- fdd:id-ref:flow -->

<!-- fdd:id-ref:algo has="priority" -->
- `p1` - `fdd-{system}-feature-{feature}-algo-{slug}`
<!-- fdd:id-ref:algo -->

**Covers (PRD)**:
<!-- fdd:id-ref:fr -->
- `fdd-{system}-fr-{slug}`
<!-- fdd:id-ref:fr -->

<!-- fdd:id-ref:nfr -->
- `fdd-{system}-nfr-{slug}`
<!-- fdd:id-ref:nfr -->

**Covers (DESIGN)**:
<!-- fdd:id-ref:principle -->
- `fdd-{system}-principle-{slug}`
<!-- fdd:id-ref:principle -->

<!-- fdd:id-ref:constraint -->
- `fdd-{system}-constraint-{slug}`
<!-- fdd:id-ref:constraint -->

<!-- fdd:id-ref:component -->
- `fdd-{system}-component-{slug}`
<!-- fdd:id-ref:component -->

<!-- fdd:id-ref:seq -->
- `fdd-{system}-seq-{slug}`
<!-- fdd:id-ref:seq -->

<!-- fdd:id-ref:dbtable -->
- `fdd-{system}-dbtable-{slug}`
<!-- fdd:id-ref:dbtable -->

<!-- fdd:id:req -->
<!-- fdd:###:req-title repeat="many" -->
<!-- fdd:##:requirements -->

<!-- fdd:##:additional-context -->
## 6. Additional Context (optional)

<!-- fdd:free:context-notes -->
{Optional notes, decisions, constraints, links, and rationale.}
<!-- fdd:free:context-notes -->
<!-- fdd:##:additional-context -->

<!-- fdd:#:feature-design -->
