<!-- cpt:#:prd -->
# PRD

<!-- cpt:##:overview -->
## 1. Overview

<!-- cpt:paragraph:purpose -->
**Purpose**: {1-3 sentences describing what the product/system is and why it exists}
<!-- cpt:paragraph:purpose -->

<!-- cpt:paragraph:context -->
{1-2 short paragraphs providing high-level context: target audience, market gap, key differentiator}
<!-- cpt:paragraph:context -->

**Target Users**:
<!-- cpt:list:target-users required="true" -->
- {Specific user role and what they do}
- {Another specific user role}
<!-- cpt:list:target-users -->

**Key Problems Solved**:
<!-- cpt:list:key-problems required="true" -->
- {Problem + impact on users/business}
- {Another problem + impact}
<!-- cpt:list:key-problems -->

**Success Criteria**:
<!-- cpt:list:success-criteria required="true" -->
- {Metric + baseline + target, e.g. "Task creation under 30s (baseline: N/A, target: v1.0)"}
- {Another measurable criterion}
<!-- cpt:list:success-criteria -->

**Capabilities**:
<!-- cpt:list:capabilities required="true" -->
- {Capability + value it provides}
- {Another capability}
<!-- cpt:list:capabilities -->
<!-- cpt:##:overview -->

<!-- cpt:##:actors -->
## 2. Actors

<!-- cpt:###:actor-title repeat="many" -->
### {Actor Name 1}

<!-- cpt:id:actor has="task" -->
- [ ] **ID**: `cpt-{system}-actor-{slug}`

<!-- cpt:paragraph:actor-role -->
**Role**: {1-3 sentences describing responsibilities and goals}
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### {Actor Name 2}

<!-- cpt:id:actor has="task" -->
- [ ] **ID**: `cpt-{system}-actor-{slug}`

<!-- cpt:paragraph:actor-role -->
**Role**: {1-3 sentences describing responsibilities and goals}
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### {Actor Name 3}

<!-- cpt:id:actor has="task" -->
- [ ] **ID**: `cpt-{system}-actor-{slug}`

<!-- cpt:paragraph:actor-role -->
**Role**: {1-3 sentences describing responsibilities and goals}
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:##:actors -->

<!-- cpt:##:frs -->
## 3. Functional Requirements

<!-- cpt:###:fr-title repeat="many" -->
### FR-001 {Requirement Title}

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `cpt-{system}-fr-{slug}`

<!-- cpt:free:fr-summary -->
{Describe the requirement: what system MUST/SHOULD do. Use paragraphs, bullets, or combination based on complexity.}
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-{system}-actor-{slug-1}`, `cpt-{system}-actor-{slug-2}`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-002 {Requirement Title}

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `cpt-{system}-fr-{slug}`

<!-- cpt:free:fr-summary -->
{Describe the requirement}
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-{system}-actor-{slug}`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:##:frs -->

<!-- cpt:##:usecases -->
## 4. Use Cases

<!-- cpt:###:uc-title repeat="many" -->
### UC-001 {Use Case Title}

<!-- cpt:id:usecase -->
**ID**: `cpt-{system}-usecase-{slug}`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-{system}-actor-{slug}`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: {what must already be true before this flow starts}
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**: {optional flow name}
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. {Actor does action}
2. {System responds}
3. {Actor does action}
4. {System completes}
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: {what becomes true after successful completion}
<!-- cpt:paragraph:postconditions -->

**Alternative Flows**:
<!-- cpt:list:alternative-flows -->
- **{condition}**: {what happens, may reference other use cases}
<!-- cpt:list:alternative-flows -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

<!-- cpt:##:usecases -->

<!-- cpt:##:nfrs -->
## 5. Non-functional requirements

<!-- cpt:###:nfr-title repeat="many" -->
### {NFR Category 1, e.g. Security}

<!-- cpt:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `cpt-{system}-nfr-{slug}`

<!-- cpt:list:nfr-statements -->
- {Specific constraint with MUST/SHOULD}
- {Another measurable requirement}
<!-- cpt:list:nfr-statements -->
<!-- cpt:id:nfr -->
<!-- cpt:###:nfr-title repeat="many" -->

<!-- cpt:###:nfr-title repeat="many" -->
### {NFR Category 2, e.g. Performance}

<!-- cpt:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [ ] `p2` - **ID**: `cpt-{system}-nfr-{slug}`

<!-- cpt:list:nfr-statements -->
- {Specific constraint with MUST/SHOULD}
- {Another measurable requirement}
<!-- cpt:list:nfr-statements -->
<!-- cpt:id:nfr -->
<!-- cpt:###:nfr-title repeat="many" -->

<!-- cpt:###:intentional-exclusions -->
### Intentional Exclusions

<!-- cpt:list:exclusions -->
- **{Category 1}** ({Checklist IDs}): Not applicable — {reason why this category doesn't apply}
- **{Category 2}** ({Checklist IDs}): Not applicable — {reason}
- **{Category 3}** ({Checklist IDs}): Not applicable — {reason}
<!-- cpt:list:exclusions -->
<!-- cpt:###:intentional-exclusions -->
<!-- cpt:##:nfrs -->

<!-- cpt:##:nongoals -->
## 6. Non-Goals & Risks

<!-- cpt:###:nongoals-title -->
### Non-Goals

<!-- cpt:list:nongoals -->
- {What product explicitly does NOT do and why}
- {Another explicit non-goal with rationale}
<!-- cpt:list:nongoals -->
<!-- cpt:###:nongoals-title -->

<!-- cpt:###:risks-title -->
### Risks

<!-- cpt:list:risks -->
- **{Risk name}**: {Description + impact + mitigation strategy}
- **{Risk name}**: {Description + impact + mitigation strategy}
<!-- cpt:list:risks -->
<!-- cpt:###:risks-title -->
<!-- cpt:##:nongoals -->

<!-- cpt:##:assumptions -->
## 7. Assumptions & Open Questions

<!-- cpt:###:assumptions-title -->
### Assumptions

<!-- cpt:list:assumptions -->
- {Assumption + potential impact if wrong}
- {Another assumption with rationale}
<!-- cpt:list:assumptions -->
<!-- cpt:###:assumptions-title -->

<!-- cpt:###:open-questions-title -->
### Open Questions

<!-- cpt:list:open-questions -->
- {Question requiring resolution} — Owner: {name}, Target: {date}
- {Another open question} — Owner: {name}, Target: {date}
<!-- cpt:list:open-questions -->
<!-- cpt:###:open-questions-title -->
<!-- cpt:##:assumptions -->

<!-- cpt:##:context -->
## 8. Additional context

<!-- cpt:###:context-title repeat="many" -->
### {Context Topic 1, e.g. Stakeholder Notes}

<!-- cpt:free:prd-context-notes -->
{Context notes, links, or background information}
<!-- cpt:free:prd-context-notes -->
<!-- cpt:###:context-title repeat="many" -->

<!-- cpt:###:context-title repeat="many" -->
### {Context Topic 2, e.g. Market Research}

<!-- cpt:free:prd-context-notes -->
{More context notes}
<!-- cpt:free:prd-context-notes -->
<!-- cpt:###:context-title repeat="many" -->

<!-- cpt:###:context-title repeat="many" -->
### {Context Topic 3, e.g. Technical Constraints}

<!-- cpt:free:prd-context-notes -->
{Additional context}
<!-- cpt:free:prd-context-notes -->
<!-- cpt:###:context-title repeat="many" -->

<!-- cpt:##:context -->
<!-- cpt:#:prd -->
