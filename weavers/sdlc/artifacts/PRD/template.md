<!-- spd:#:prd -->
# PRD

<!-- spd:##:overview -->
## 1. Overview

<!-- spd:paragraph:purpose -->
**Purpose**: {1-3 sentences describing what the product/system is and why it exists}
<!-- spd:paragraph:purpose -->

<!-- spd:paragraph:context -->
{1-2 short paragraphs providing high-level context: target audience, market gap, key differentiator}
<!-- spd:paragraph:context -->

**Target Users**:
<!-- spd:list:target-users required="true" -->
- {Specific user role and what they do}
- {Another specific user role}
<!-- spd:list:target-users -->

**Key Problems Solved**:
<!-- spd:list:key-problems required="true" -->
- {Problem + impact on users/business}
- {Another problem + impact}
<!-- spd:list:key-problems -->

**Success Criteria**:
<!-- spd:list:success-criteria required="true" -->
- {Metric + baseline + target, e.g. "Task creation under 30s (baseline: N/A, target: v1.0)"}
- {Another measurable criterion}
<!-- spd:list:success-criteria -->

**Capabilities**:
<!-- spd:list:capabilities required="true" -->
- {Capability + value it provides}
- {Another capability}
<!-- spd:list:capabilities -->
<!-- spd:##:overview -->

<!-- spd:##:actors -->
## 2. Actors

<!-- spd:###:actor-title repeat="many" -->

### {Actor Name 1}

<!-- spd:id:actor has="task" -->
- [ ] **ID**: `spd-{system}-actor-{slug}`

<!-- spd:paragraph:actor-role -->
**Role**: {1-3 sentences describing responsibilities and goals}
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->

### {Actor Name 2}

<!-- spd:id:actor has="task" -->
- [ ] **ID**: `spd-{system}-actor-{slug}`

<!-- spd:paragraph:actor-role -->
**Role**: {1-3 sentences describing responsibilities and goals}
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->

### {Actor Name 3}

<!-- spd:id:actor has="task" -->
- [ ] **ID**: `spd-{system}-actor-{slug}`

<!-- spd:paragraph:actor-role -->
**Role**: {1-3 sentences describing responsibilities and goals}
<!-- spd:paragraph:actor-role -->
<!-- spd:id:actor -->

<!-- spd:###:actor-title repeat="many" -->
<!-- spd:##:actors -->

<!-- spd:##:frs -->
## 3. Functional Requirements

<!-- spd:###:fr-title repeat="many" -->

### FR-001 {Requirement Title}

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `spd-{system}-fr-{slug}`

<!-- spd:free:fr-summary -->
{Describe the requirement: what system MUST/SHOULD do. Use paragraphs, bullets, or combination based on complexity.}
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-{system}-actor-{slug-1}`, `spd-{system}-actor-{slug-2}`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->

### FR-002 {Requirement Title}

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `spd-{system}-fr-{slug}`

<!-- spd:free:fr-summary -->
{Describe the requirement}
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-{system}-actor-{slug}`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->

<!-- spd:###:fr-title repeat="many" -->
<!-- spd:##:frs -->

<!-- spd:##:usecases -->
## 4. Use Cases

<!-- spd:###:uc-title repeat="many" -->

### UC-001 {Use Case Title}

<!-- spd:id:usecase -->
**ID**: `spd-{system}-usecase-{slug}`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-{system}-actor-{slug}`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: {what must already be true before this flow starts}
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**: {optional flow name}
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. {Actor does action}
2. {System responds}
3. {Actor does action}
4. {System completes}
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: {what becomes true after successful completion}
<!-- spd:paragraph:postconditions -->

**Alternative Flows**:
<!-- spd:list:alternative-flows -->
- **{condition}**: {what happens, may reference other use cases}
<!-- spd:list:alternative-flows -->
<!-- spd:id:usecase -->

<!-- spd:###:uc-title repeat="many" -->
<!-- spd:##:usecases -->

<!-- spd:##:nfrs -->
## 5. Non-functional requirements

<!-- spd:###:nfr-title repeat="many" -->

### {NFR Category 1, e.g. Security}

<!-- spd:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `spd-{system}-nfr-{slug}`

<!-- spd:list:nfr-statements -->
- {Specific constraint with MUST/SHOULD}
- {Another measurable requirement}
<!-- spd:list:nfr-statements -->
<!-- spd:id:nfr -->

### {NFR Category 2, e.g. Performance}

<!-- spd:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [ ] `p2` - **ID**: `spd-{system}-nfr-{slug}`

<!-- spd:list:nfr-statements -->
- {Specific constraint with MUST/SHOULD}
- {Another measurable requirement}
<!-- spd:list:nfr-statements -->
<!-- spd:id:nfr -->

<!-- spd:###:nfr-title repeat="many" -->

<!-- spd:###:intentional-exclusions -->
### Intentional Exclusions

<!-- spd:list:exclusions -->
- **{Category 1}** ({Checklist IDs}): Not applicable — {reason why this category doesn't apply}
- **{Category 2}** ({Checklist IDs}): Not applicable — {reason}
- **{Category 3}** ({Checklist IDs}): Not applicable — {reason}
<!-- spd:list:exclusions -->
<!-- spd:###:intentional-exclusions -->
<!-- spd:##:nfrs -->

<!-- spd:##:nongoals -->
## 6. Non-Goals & Risks

<!-- spd:###:nongoals-title -->
### Non-Goals

<!-- spd:list:nongoals -->
- {What product explicitly does NOT do and why}
- {Another explicit non-goal with rationale}
<!-- spd:list:nongoals -->
<!-- spd:###:nongoals-title -->

<!-- spd:###:risks-title -->
### Risks

<!-- spd:list:risks -->
- **{Risk name}**: {Description + impact + mitigation strategy}
- **{Risk name}**: {Description + impact + mitigation strategy}
<!-- spd:list:risks -->
<!-- spd:###:risks-title -->
<!-- spd:##:nongoals -->

<!-- spd:##:assumptions -->
## 7. Assumptions & Open Questions

<!-- spd:###:assumptions-title -->
### Assumptions

<!-- spd:list:assumptions -->
- {Assumption + potential impact if wrong}
- {Another assumption with rationale}
<!-- spd:list:assumptions -->
<!-- spd:###:assumptions-title -->

<!-- spd:###:open-questions-title -->
### Open Questions

<!-- spd:list:open-questions -->
- {Question requiring resolution} — Owner: {name}, Target: {date}
- {Another open question} — Owner: {name}, Target: {date}
<!-- spd:list:open-questions -->
<!-- spd:###:open-questions-title -->
<!-- spd:##:assumptions -->

<!-- spd:##:context -->
## 8. Additional context

<!-- spd:###:context-title repeat="many" -->

### {Context Topic 1, e.g. Stakeholder Notes}

<!-- spd:free:prd-context-notes -->
{Context notes, links, or background information}
<!-- spd:free:prd-context-notes -->

### {Context Topic 2, e.g. Market Research}

<!-- spd:free:prd-context-notes -->
{More context notes}
<!-- spd:free:prd-context-notes -->

### {Context Topic 3, e.g. Technical Constraints}

<!-- spd:free:prd-context-notes -->
{Additional context}
<!-- spd:free:prd-context-notes -->

<!-- spd:###:context-title repeat="many" -->
<!-- spd:##:context -->
<!-- spd:#:prd -->
