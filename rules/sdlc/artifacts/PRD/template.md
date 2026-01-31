---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: PRD
  unknown_sections: warn
---

<!-- fdd:#:prd -->
# PRD

<!-- fdd:##:vision -->
## A. Vision

<!-- fdd:paragraph:purpose -->
**Purpose**: <1-3 sentences describing what the product/system is>
<!-- fdd:paragraph:purpose -->

<!-- fdd:paragraph:context -->
<1-2 short paragraphs providing high-level context.>
<!-- fdd:paragraph:context -->

**Target Users**:
<!-- fdd:list:target-users required="true" -->
- <who uses it>
- <who else>
<!-- fdd:list:target-users -->

**Key Problems Solved**:
<!-- fdd:list:key-problems required="true" -->
- <problem>
- <problem>
<!-- fdd:list:key-problems -->

**Success Criteria**:
<!-- fdd:list:success-criteria required="true" -->
- <measurable outcome>
- <measurable outcome>
<!-- fdd:list:success-criteria -->

**Capabilities**:
<!-- fdd:list:capabilities required="true" -->
- <capability>
- <capability>
<!-- fdd:list:capabilities -->
<!-- fdd:##:vision -->

<!-- fdd:##:actors -->
## B. Actors

<!-- fdd:###:actor-title repeat="many" -->
### <Actor Name>

<!-- fdd:id:actor has="task" -->
**ID**: [ ] `fdd-<project>-actor-<slug>`
<!-- fdd:id:actor -->

<!-- fdd:line:actor-role repeat="many" -->
**Role**: <1-3 sentences describing responsibilities and goals>
<!-- fdd:line:actor-role -->

<Add more actors as needed.>
<!-- fdd:###:actor-title repeat="many" -->
<!-- fdd:##:actors -->

<!-- fdd:##:frs -->
## C. Functional Requirements

<!-- fdd:###:fr-title repeat="many" -->
### FR-{NUMBER, like FR-001} { Functional Requirement Title }

<!-- fdd:id:fr has="priority,task" covered_by="design" -->
**ID**: [ ] `p1` - `fdd-<project>-fr-<slug>`
<!-- fdd:id:fr -->

<!-- fdd:paragraph:fr-summary -->
{ 3-5 sentences about the requirements for this product, what it does, and why it is needed }
<!-- fdd:paragraph:fr-summary -->

<!-- fdd:id-ref:actor -->
**Actors**: `fdd-<project>-actor-<slug-1>`, `fdd-<project>-actor-<slug-2>`
<!-- fdd:id-ref:actor -->
<!-- fdd:###:fr-title repeat="many" -->
<!-- fdd:##:frs -->

<!-- fdd:##:usecases -->
## D. Use Cases

<!-- fdd:###:uc-title repeat="many" -->
### UC-{NUMBER, like UC-001} { Case Title }

<!-- fdd:id:usecase -->
**ID**: `fdd-<project>-usecase-<slug>`
<!-- fdd:id:usecase -->

<!-- fdd:id-ref:actor -->
**Actors**: `fdd-<project>-actor-<slug-1>`, `fdd-<project>-actor-<slug-2>`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: <what must already be true>
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**: { optional name of the flow }
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. <step>
2. <step>
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: <what becomes true>
<!-- fdd:paragraph:postconditions -->

**Alternative Flows**:
<!-- fdd:list:alternative-flows -->
- **<condition>**: <what happens, may reference other use cases>
<!-- fdd:list:alternative-flows -->

<Add more use cases as needed.>
<!-- fdd:###:uc-title repeat="many" -->
<!-- fdd:##:usecases -->

<!-- fdd:##:nfrs -->
## E. Non-functional requirements

<!-- fdd:###:nfr-title repeat="many" -->
### <NFR Name>

<!-- fdd:id:nfr has="priority,task" covered_by="design" -->
**ID**: [ ] `p1` - `fdd-<project>-nfr-<slug>`
<!-- fdd:id:nfr -->

<!-- fdd:list:nfr-statements -->
- <NFR statement>
- <NFR statement>
<!-- fdd:list:nfr-statements -->

<Add more non-functional requirements as needed.>
<!-- fdd:###:nfr-title repeat="many" -->

<!-- fdd:###:intentional-exclusions -->
### Intentional Exclusions

<!-- fdd:list:exclusions -->
- **<Category>** (<Checklist IDs>): Not applicable — <reason>
<!-- fdd:list:exclusions -->
<!-- fdd:###:intentional-exclusions -->
<!-- fdd:##:nfrs -->

<!-- fdd:##:nongoals -->
## F. Non-Goals & Risks

<!-- fdd:###:nongoals-title -->
### Non-Goals

<!-- fdd:list:nongoals -->
- <non-goal>
- <non-goal>
<!-- fdd:list:nongoals -->
<!-- fdd:###:nongoals-title -->

<!-- fdd:###:risks-title -->
### Risks

<!-- fdd:list:risks -->
- <risk>
- <risk>
<!-- fdd:list:risks -->
<!-- fdd:###:risks-title -->
<!-- fdd:##:nongoals -->

<!-- fdd:##:assumptions -->
## G. Assumptions & Open Questions

<!-- fdd:###:assumptions-title -->
### Assumptions

<!-- fdd:list:assumptions -->
- <assumption>
- <assumption>
<!-- fdd:list:assumptions -->
<!-- fdd:###:assumptions-title -->

<!-- fdd:###:open-questions-title -->
### Open Questions

<!-- fdd:list:open-questions -->
- <question> — Owner: <name>, Target: <date>
<!-- fdd:list:open-questions -->
<!-- fdd:###:open-questions-title -->
<!-- fdd:##:assumptions -->

<!-- fdd:##:context -->
## H. Additional context

<!-- fdd:###:context-title repeat="many" -->
### <Context Item>

<!-- fdd:list:prd-context-notes -->
- <notes>
<!-- fdd:list:prd-context-notes -->

<This section is optional. Use it for stakeholder notes, business context, market notes, research links, etc.>
<!-- fdd:###:context-title repeat="many" -->
<!-- fdd:##:context -->
<!-- fdd:#:prd -->