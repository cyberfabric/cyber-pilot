<!-- spd:#:spec -->
# Spec: {Spec Name}

<!-- spd:id-ref:spec has="task" -->
- [ ] - `spd-{system}-spec-{spec-slug}`
<!-- spd:id-ref:spec -->

<!-- spd:##:context -->
## 1. Spec Context

<!-- spd:overview -->
### 1. Overview
{1-2 paragraphs summarizing what this spec does and why it exists.}

{Include:
- Problem statement
- Primary user value
- Key assumptions}
<!-- spd:overview -->

<!-- spd:paragraph:purpose -->
### 2. Purpose
{1-3 sentences describing the intended outcome of this spec.}

{Optionally include measurable success criteria.}
<!-- spd:paragraph:purpose -->

### 3. Actors
<!-- spd:id-ref:actor -->
- `spd-{system}-actor-{slug}`
- `spd-{system}-actor-{slug}`
<!-- spd:id-ref:actor -->

<!-- spd:list:references -->
### 4. References
- Overall Design: [DESIGN.md](../../DESIGN.md)
- ADRs: `spd-{system}-adr-{slug}`
- Related spec: `spd-{system}-spec-{slug}`
<!-- spd:list:references -->
<!-- spd:##:context -->

<!-- spd:##:flows -->
## 2. Actor Flows

<!-- spd:###:flow-title repeat="many" -->

### {Flow Name 1}

<!-- spd:id:flow has="task" to_code="true" -->
- [ ] **ID**: `spd-{system}-spec-{spec}-flow-{slug}`

**Actors**:
<!-- spd:id-ref:actor -->
- `spd-{system}-actor-{slug}`
<!-- spd:id-ref:actor -->

<!-- spd:sdsl:flow-steps -->
1. [ ] - `p1` - Actor fills form (field1, field2) - `inst-fill-form`
2. [ ] - `p1` - API: POST /api/{resource} (body: field1, field2) - `inst-api-call`
3. [ ] - `p1` - Algorithm: validate input using <!-- spd:id-ref:algo has="task" required="false" -->[ ] - `spd-{system}-spec-{spec}-algo-{slug}`<!-- spd:id-ref:algo --> - `inst-run-algo`
4. [ ] - `p1` - DB: INSERT {table}(field1, field2, status) - `inst-db-insert`
5. [ ] - `p1` - API: RETURN 201 Created (id, status) - `inst-return`
<!-- spd:sdsl:flow-steps -->
<!-- spd:id:flow -->

### {Flow Name 2}

<!-- spd:id:flow has="task" to_code="true" -->
- [ ] **ID**: `spd-{system}-spec-{spec}-flow-{slug}`

**Actors**:
<!-- spd:id-ref:actor -->
- `spd-{system}-actor-{slug}`
<!-- spd:id-ref:actor -->

<!-- spd:sdsl:flow-steps -->
1. [ ] - `p1` - Actor requests resource by ID - `inst-request`
2. [ ] - `p1` - API: GET /api/{resource}/{id} - `inst-api-get`
3. [ ] - `p1` - DB: SELECT * FROM {table} WHERE id = {id} - `inst-db-query`
4. [ ] - `p2` - **IF** resource not found: - `inst-if-not-found`
   1. [ ] - `p2` - API: RETURN 404 Not Found - `inst-return-404`
5. [ ] - `p1` - API: RETURN 200 OK (resource) - `inst-return-ok`
<!-- spd:sdsl:flow-steps -->
<!-- spd:id:flow -->

<!-- spd:###:flow-title repeat="many" -->
<!-- spd:##:flows -->

<!-- spd:##:algorithms -->
## 3. Algorithms

<!-- spd:###:algo-title repeat="many" -->

### {Algorithm Name 1}

<!-- spd:id:algo has="task" to_code="true" -->
- [ ] **ID**: `spd-{system}-spec-{spec}-algo-{slug}`

<!-- spd:sdsl:algo-steps -->
1. [ ] - `p1` - **IF** {field} is empty **RETURN** error "{validation message}" - `inst-validate`
2. [ ] - `p1` - retrieve {entity} from repository by {criteria} - `inst-fetch`
3. [ ] - `p1` - calculate {result} based on {business rule description} - `inst-calc`
4. [ ] - `p1` - **RETURN** {result description} - `inst-return`
<!-- spd:sdsl:algo-steps -->
<!-- spd:id:algo -->

### {Algorithm Name 2}

<!-- spd:id:algo has="task" to_code="true" -->
- [ ] **ID**: `spd-{system}-spec-{spec}-algo-{slug}`

<!-- spd:sdsl:algo-steps -->
1. [ ] - `p1` - **FOR EACH** {item} in {collection}: - `inst-loop`
   1. [ ] - `p1` - transform {source data} into {target format} - `inst-transform`
   2. [ ] - `p2` - **IF** {condition}: - `inst-if-condition`
      1. [ ] - `p2` - apply {special operation} - `inst-special-op`
2. [ ] - `p1` - normalize {data} according to {domain rules} - `inst-normalize`
3. [ ] - `p1` - **RETURN** {transformed collection} - `inst-return`
<!-- spd:sdsl:algo-steps -->
<!-- spd:id:algo -->

<!-- spd:###:algo-title repeat="many" -->
<!-- spd:##:algorithms -->

<!-- spd:##:states -->
## 4. States

<!-- spd:###:state-title repeat="many" -->

### {State Machine Name 1}

<!-- spd:id:state has="task" to_code="true" -->
- [ ] **ID**: `spd-{system}-spec-{spec}-state-{slug}`

<!-- spd:sdsl:state-transitions -->
1. [ ] - `p1` - **FROM** PENDING **TO** ACTIVE **WHEN** user activates - `inst-transition-activate`
2. [ ] - `p1` - **FROM** ACTIVE **TO** COMPLETED **WHEN** task finishes - `inst-transition-complete`
3. [ ] - `p2` - **FROM** ACTIVE **TO** CANCELLED **WHEN** user cancels - `inst-transition-cancel`
<!-- spd:sdsl:state-transitions -->
<!-- spd:id:state -->

### {State Machine Name 2}

<!-- spd:id:state has="task" to_code="true" -->
- [ ] **ID**: `spd-{system}-spec-{spec}-state-{slug}`

<!-- spd:sdsl:state-transitions -->
1. [ ] - `p1` - **FROM** DRAFT **TO** SUBMITTED **WHEN** user submits - `inst-transition-submit`
2. [ ] - `p1` - **FROM** SUBMITTED **TO** APPROVED **WHEN** reviewer approves - `inst-transition-approve`
3. [ ] - `p2` - **FROM** SUBMITTED **TO** REJECTED **WHEN** reviewer rejects - `inst-transition-reject`
<!-- spd:sdsl:state-transitions -->
<!-- spd:id:state -->

<!-- spd:###:state-title repeat="many" -->
<!-- spd:##:states -->

<!-- spd:##:requirements -->
## 5. Definition of Done

<!-- spd:###:req-title repeat="many" -->

### {Requirement Name 1}

<!-- spd:id:req has="priority,task" to_code="true" -->
- [ ] `p1` - **ID**: `spd-{system}-spec-{spec}-req-{slug}`

<!-- spd:paragraph:req-body -->
{Describe what must be true when this requirement is satisfied. Be specific and testable.}
<!-- spd:paragraph:req-body -->

<!-- spd:list:req-impl -->
**Implementation details**:
- API: POST /api/{resource}, GET /api/{resource}/{id}
- DB: {table} table with fields (field1, field2, status)
- Domain: {Entity} with validation rules
<!-- spd:list:req-impl -->

**Implements**:
<!-- spd:id-ref:flow has="priority" -->
- `p1` - `spd-{system}-spec-{spec}-flow-{slug}`
<!-- spd:id-ref:flow -->

<!-- spd:id-ref:algo has="priority" -->
- `p1` - `spd-{system}-spec-{spec}-algo-{slug}`
<!-- spd:id-ref:algo -->

**Covers (PRD)**:
<!-- spd:id-ref:fr -->
- `spd-{system}-fr-{slug}`
<!-- spd:id-ref:fr -->

<!-- spd:id-ref:nfr -->
- `spd-{system}-nfr-{slug}`
<!-- spd:id-ref:nfr -->

**Covers (DESIGN)**:
<!-- spd:id-ref:principle -->
- `spd-{system}-principle-{slug}`
<!-- spd:id-ref:principle -->

<!-- spd:id-ref:constraint -->
- `spd-{system}-constraint-{slug}`
<!-- spd:id-ref:constraint -->

<!-- spd:id-ref:component -->
- `spd-{system}-component-{slug}`
<!-- spd:id-ref:component -->

<!-- spd:id-ref:seq -->
- `spd-{system}-seq-{slug}`
<!-- spd:id-ref:seq -->

<!-- spd:id-ref:dbtable -->
- `spd-{system}-dbtable-{slug}`
<!-- spd:id-ref:dbtable -->

<!-- spd:id:req -->

### {Requirement Name 2}

<!-- spd:id:req has="priority,task" to_code="true" -->
- [ ] `p2` - **ID**: `spd-{system}-spec-{spec}-req-{slug}`

<!-- spd:paragraph:req-body -->
{Describe what must be true when this requirement is satisfied. Be specific and testable.}
<!-- spd:paragraph:req-body -->

<!-- spd:list:req-impl -->
**Implementation details**:
- API: PUT /api/{resource}/{id}
- DB: UPDATE query on {table}
- Domain: {Entity} update logic
<!-- spd:list:req-impl -->

**Implements**:
<!-- spd:id-ref:flow has="priority" -->
- `p2` - `spd-{system}-spec-{spec}-flow-{slug}`
<!-- spd:id-ref:flow -->

<!-- spd:id-ref:algo has="priority" -->
- `p2` - `spd-{system}-spec-{spec}-algo-{slug}`
<!-- spd:id-ref:algo -->

**Covers (PRD)**:
<!-- spd:id-ref:fr -->
- `spd-{system}-fr-{slug}`
<!-- spd:id-ref:fr -->

<!-- spd:id-ref:nfr -->
- `spd-{system}-nfr-{slug}`
<!-- spd:id-ref:nfr -->

**Covers (DESIGN)**:
<!-- spd:id-ref:principle -->
- `spd-{system}-principle-{slug}`
<!-- spd:id-ref:principle -->

<!-- spd:id-ref:constraint -->
- `spd-{system}-constraint-{slug}`
<!-- spd:id-ref:constraint -->

<!-- spd:id-ref:component -->
- `spd-{system}-component-{slug}`
<!-- spd:id-ref:component -->

<!-- spd:id-ref:seq -->
- `spd-{system}-seq-{slug}`
<!-- spd:id-ref:seq -->

<!-- spd:id-ref:dbtable -->
- `spd-{system}-dbtable-{slug}`
<!-- spd:id-ref:dbtable -->

<!-- spd:id:req -->

<!-- spd:###:req-title repeat="many" -->
<!-- spd:##:requirements -->

<!-- spd:##:additional-context -->
## 6. Additional Context (optional)

<!-- spd:free:context-notes -->
{Optional notes, decisions, constraints, links, and rationale.}
<!-- spd:free:context-notes -->
<!-- spd:##:additional-context -->

<!-- spd:#:spec -->
