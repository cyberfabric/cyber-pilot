<!-- cpt:#:spec -->
# Spec: {Spec Name}

<!-- cpt:id-ref:spec has="task" -->
- [ ] - `cpt-{system}-spec-{spec-slug}`
<!-- cpt:id-ref:spec -->

<!-- cpt:##:context -->
## 1. Spec Context

<!-- cpt:overview -->
### 1. Overview
{1-2 paragraphs summarizing what this spec does and why it exists.}

{Include:
- Problem statement
- Primary user value
- Key assumptions}
<!-- cpt:overview -->

<!-- cpt:paragraph:purpose -->
### 2. Purpose
{1-3 sentences describing the intended outcome of this spec.}

{Optionally include measurable success criteria.}
<!-- cpt:paragraph:purpose -->

### 3. Actors
<!-- cpt:id-ref:actor -->
- `cpt-{system}-actor-{slug}`
- `cpt-{system}-actor-{slug}`
<!-- cpt:id-ref:actor -->

<!-- cpt:list:references -->
### 4. References
- Overall Design: [DESIGN.md](../../DESIGN.md)
- ADRs: `cpt-{system}-adr-{slug}`
- Related spec: `cpt-{system}-spec-{slug}`
<!-- cpt:list:references -->
<!-- cpt:##:context -->

<!-- cpt:##:flows -->
## 2. Actor Flows

<!-- cpt:###:flow-title repeat="many" -->
### {Flow Name 1}

<!-- cpt:id:flow has="task" to_code="true" -->
- [ ] **ID**: `cpt-{system}-spec-{spec}-flow-{slug}`

**Actors**:
<!-- cpt:id-ref:actor -->
- `cpt-{system}-actor-{slug}`
<!-- cpt:id-ref:actor -->

<!-- cpt:cdsl:flow-steps -->
1. [ ] - `p1` - Actor fills form (field1, field2) - `inst-fill-form`
2. [ ] - `p1` - API: POST /api/{resource} (body: field1, field2) - `inst-api-call`
3. [ ] - `p1` - Algorithm: validate input using <!-- cpt:id-ref:algo has="task" required="false" -->[ ] - `cpt-{system}-spec-{spec}-algo-{slug}`<!-- cpt:id-ref:algo --> - `inst-run-algo`
4. [ ] - `p1` - DB: INSERT {table}(field1, field2, status) - `inst-db-insert`
5. [ ] - `p1` - API: RETURN 201 Created (id, status) - `inst-return`
<!-- cpt:cdsl:flow-steps -->
<!-- cpt:id:flow -->
<!-- cpt:###:flow-title repeat="many" -->

<!-- cpt:###:flow-title repeat="many" -->
### {Flow Name 2}

<!-- cpt:id:flow has="task" to_code="true" -->
- [ ] **ID**: `cpt-{system}-spec-{spec}-flow-{slug}`

**Actors**:
<!-- cpt:id-ref:actor -->
- `cpt-{system}-actor-{slug}`
<!-- cpt:id-ref:actor -->

<!-- cpt:cdsl:flow-steps -->
1. [ ] - `p1` - Actor requests resource by ID - `inst-request`
2. [ ] - `p1` - API: GET /api/{resource}/{id} - `inst-api-get`
3. [ ] - `p1` - DB: SELECT * FROM {table} WHERE id = {id} - `inst-db-query`
4. [ ] - `p2` - **IF** resource not found: - `inst-if-not-found`
   1. [ ] - `p2` - API: RETURN 404 Not Found - `inst-return-404`
5. [ ] - `p1` - API: RETURN 200 OK (resource) - `inst-return-ok`
<!-- cpt:cdsl:flow-steps -->
<!-- cpt:id:flow -->
<!-- cpt:###:flow-title repeat="many" -->

<!-- cpt:##:flows -->

<!-- cpt:##:algorithms -->
## 3. Algorithms

<!-- cpt:###:algo-title repeat="many" -->
### {Algorithm Name 1}

<!-- cpt:id:algo has="task" to_code="true" -->
- [ ] **ID**: `cpt-{system}-spec-{spec}-algo-{slug}`

<!-- cpt:cdsl:algo-steps -->
1. [ ] - `p1` - **IF** {field} is empty **RETURN** error "{validation message}" - `inst-validate`
2. [ ] - `p1` - retrieve {entity} from repository by {criteria} - `inst-fetch`
3. [ ] - `p1` - calculate {result} based on {business rule description} - `inst-calc`
4. [ ] - `p1` - **RETURN** {result description} - `inst-return`
<!-- cpt:cdsl:algo-steps -->
<!-- cpt:id:algo -->
<!-- cpt:###:algo-title repeat="many" -->

<!-- cpt:###:algo-title repeat="many" -->
### {Algorithm Name 2}

<!-- cpt:id:algo has="task" to_code="true" -->
- [ ] **ID**: `cpt-{system}-spec-{spec}-algo-{slug}`

<!-- cpt:cdsl:algo-steps -->
1. [ ] - `p1` - **FOR EACH** {item} in {collection}: - `inst-loop`
   1. [ ] - `p1` - transform {source data} into {target format} - `inst-transform`
   2. [ ] - `p2` - **IF** {condition}: - `inst-if-condition`
      1. [ ] - `p2` - apply {special operation} - `inst-special-op`
2. [ ] - `p1` - normalize {data} according to {domain rules} - `inst-normalize`
3. [ ] - `p1` - **RETURN** {transformed collection} - `inst-return`
<!-- cpt:cdsl:algo-steps -->
<!-- cpt:id:algo -->
<!-- cpt:###:algo-title repeat="many" -->

<!-- cpt:##:algorithms -->

<!-- cpt:##:states -->
## 4. States

<!-- cpt:###:state-title repeat="many" -->
### {State Machine Name 1}

<!-- cpt:id:state has="task" to_code="true" -->
- [ ] **ID**: `cpt-{system}-spec-{spec}-state-{slug}`

<!-- cpt:cdsl:state-transitions -->
1. [ ] - `p1` - **FROM** PENDING **TO** ACTIVE **WHEN** user activates - `inst-transition-activate`
2. [ ] - `p1` - **FROM** ACTIVE **TO** COMPLETED **WHEN** task finishes - `inst-transition-complete`
3. [ ] - `p2` - **FROM** ACTIVE **TO** CANCELLED **WHEN** user cancels - `inst-transition-cancel`
<!-- cpt:cdsl:state-transitions -->
<!-- cpt:id:state -->
<!-- cpt:###:state-title repeat="many" -->

<!-- cpt:###:state-title repeat="many" -->
### {State Machine Name 2}

<!-- cpt:id:state has="task" to_code="true" -->
- [ ] **ID**: `cpt-{system}-spec-{spec}-state-{slug}`

<!-- cpt:cdsl:state-transitions -->
1. [ ] - `p1` - **FROM** DRAFT **TO** SUBMITTED **WHEN** user submits - `inst-transition-submit`
2. [ ] - `p1` - **FROM** SUBMITTED **TO** APPROVED **WHEN** reviewer approves - `inst-transition-approve`
3. [ ] - `p2` - **FROM** SUBMITTED **TO** REJECTED **WHEN** reviewer rejects - `inst-transition-reject`
<!-- cpt:cdsl:state-transitions -->
<!-- cpt:id:state -->
<!-- cpt:###:state-title repeat="many" -->

<!-- cpt:##:states -->

<!-- cpt:##:requirements -->
## 5. Definition of Done

<!-- cpt:###:req-title repeat="many" -->
### {Requirement Name 1}

<!-- cpt:id:req has="priority,task" to_code="true" -->
- [ ] `p1` - **ID**: `cpt-{system}-spec-{spec}-req-{slug}`

<!-- cpt:paragraph:req-body -->
{Describe what must be true when this requirement is satisfied. Be specific and testable.}
<!-- cpt:paragraph:req-body -->

<!-- cpt:list:req-impl -->
**Implementation details**:
- API: POST /api/{resource}, GET /api/{resource}/{id}
- DB: {table} table with fields (field1, field2, status)
- Domain: {Entity} with validation rules
<!-- cpt:list:req-impl -->

**Implements**:
<!-- cpt:id-ref:flow has="priority" -->
- `p1` - `cpt-{system}-spec-{spec}-flow-{slug}`
<!-- cpt:id-ref:flow -->

<!-- cpt:id-ref:algo has="priority" -->
- `p1` - `cpt-{system}-spec-{spec}-algo-{slug}`
<!-- cpt:id-ref:algo -->

**Covers (PRD)**:
<!-- cpt:id-ref:fr -->
- `cpt-{system}-fr-{slug}`
<!-- cpt:id-ref:fr -->

<!-- cpt:id-ref:nfr -->
- `cpt-{system}-nfr-{slug}`
<!-- cpt:id-ref:nfr -->

**Covers (DESIGN)**:
<!-- cpt:id-ref:principle -->
- `cpt-{system}-principle-{slug}`
<!-- cpt:id-ref:principle -->

<!-- cpt:id-ref:constraint -->
- `cpt-{system}-constraint-{slug}`
<!-- cpt:id-ref:constraint -->

<!-- cpt:id-ref:component -->
- `cpt-{system}-component-{slug}`
<!-- cpt:id-ref:component -->

<!-- cpt:id-ref:seq -->
- `cpt-{system}-seq-{slug}`
<!-- cpt:id-ref:seq -->

<!-- cpt:id-ref:dbtable -->
- `cpt-{system}-dbtable-{slug}`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:req -->
<!-- cpt:###:req-title repeat="many" -->

<!-- cpt:###:req-title repeat="many" -->
### {Requirement Name 2}

<!-- cpt:id:req has="priority,task" to_code="true" -->
- [ ] `p2` - **ID**: `cpt-{system}-spec-{spec}-req-{slug}`

<!-- cpt:paragraph:req-body -->
{Describe what must be true when this requirement is satisfied. Be specific and testable.}
<!-- cpt:paragraph:req-body -->

<!-- cpt:list:req-impl -->
**Implementation details**:
- API: PUT /api/{resource}/{id}
- DB: UPDATE query on {table}
- Domain: {Entity} update logic
<!-- cpt:list:req-impl -->

**Implements**:
<!-- cpt:id-ref:flow has="priority" -->
- `p2` - `cpt-{system}-spec-{spec}-flow-{slug}`
<!-- cpt:id-ref:flow -->

<!-- cpt:id-ref:algo has="priority" -->
- `p2` - `cpt-{system}-spec-{spec}-algo-{slug}`
<!-- cpt:id-ref:algo -->

**Covers (PRD)**:
<!-- cpt:id-ref:fr -->
- `cpt-{system}-fr-{slug}`
<!-- cpt:id-ref:fr -->

<!-- cpt:id-ref:nfr -->
- `cpt-{system}-nfr-{slug}`
<!-- cpt:id-ref:nfr -->

**Covers (DESIGN)**:
<!-- cpt:id-ref:principle -->
- `cpt-{system}-principle-{slug}`
<!-- cpt:id-ref:principle -->

<!-- cpt:id-ref:constraint -->
- `cpt-{system}-constraint-{slug}`
<!-- cpt:id-ref:constraint -->

<!-- cpt:id-ref:component -->
- `cpt-{system}-component-{slug}`
<!-- cpt:id-ref:component -->

<!-- cpt:id-ref:seq -->
- `cpt-{system}-seq-{slug}`
<!-- cpt:id-ref:seq -->

<!-- cpt:id-ref:dbtable -->
- `cpt-{system}-dbtable-{slug}`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:req -->
<!-- cpt:###:req-title repeat="many" -->

<!-- cpt:##:requirements -->

<!-- cpt:##:additional-context -->
## 6. Additional Context (optional)

<!-- cpt:free:context-notes -->
{Optional notes, decisions, constraints, links, and rationale.}
<!-- cpt:free:context-notes -->
<!-- cpt:##:additional-context -->

<!-- cpt:#:spec -->
