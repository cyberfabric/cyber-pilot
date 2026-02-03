---
spider-template:
  version:
    major: 1
    minor: 0
  kind: PRD
  unknown_sections: warn
---

<!-- spd:#:prd -->
# PRD

<!-- spd:##:overview -->
## 1. Overview

<!-- spd:paragraph:purpose -->
**Purpose**: {1-3 sentences describing what the product/system is}
<!-- spd:paragraph:purpose -->

<!-- spd:paragraph:context -->
{1-2 short paragraphs providing high-level context.}
<!-- spd:paragraph:context -->

**Target Users**:
<!-- spd:list:target-users required="true" -->
- {Primary user type and their role}
- {Secondary user type and their role}
<!-- spd:list:target-users -->

**Key Problems Solved**:
<!-- spd:list:key-problems required="true" -->
- {1-3 sentences describing a key problem this product solves}
- {1-3 sentences describing another key problem}
<!-- spd:list:key-problems -->

**Success Criteria**:
<!-- spd:list:success-criteria required="true" -->
- {Measurable outcome with target metric and timeline}
- {Another measurable outcome with target metric}
<!-- spd:list:success-criteria -->

**Capabilities**:
<!-- spd:list:capabilities required="true" -->
- {1-2 sentences describing a core capability}
- {1-2 sentences describing another capability}
<!-- spd:list:capabilities -->
<!-- spd:##:overview -->

<!-- spd:##:actors -->
## 2. Actors

<!-- spd:###:actor-title repeat="many" -->
### {Actor Name}

<!-- spd:id:actor -->
**ID**: `spd-{system}-actor-{slug}`

<!-- spd:paragraph:actor-role repeat="many" -->
**Role**: {1-3 sentences describing responsibilities and goals}
<!-- spd:paragraph:actor-role -->

{Add more actors as needed.}
<!-- spd:id:actor -->
<!-- spd:###:actor-title repeat="many" -->
<!-- spd:##:actors -->

<!-- spd:##:frs -->
## 3. Functional Requirements

<!-- spd:###:fr-title repeat="many" -->
### FR-{NUMBER, like FR-001} { Functional Requirement Title }

<!-- spd:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [ ] `p1` - **ID**: `spd-{system}-fr-{slug}`

<!-- spd:free:fr-summary -->
{Describe the functional requirement in appropriate detail. You should choose suitable format - paragraphs, bullet points, or a combination - based on content complexity.}
<!-- spd:free:fr-summary -->

**Actors**:
<!-- spd:id-ref:actor -->
`spd-{system}-actor-{slug-1}`, `spd-{system}-actor-{slug-2}`
<!-- spd:id-ref:actor -->
<!-- spd:id:fr -->
<!-- spd:###:fr-title repeat="many" -->
<!-- spd:##:frs -->

<!-- spd:##:usecases -->
## 4. Use Cases

<!-- spd:###:uc-title repeat="many" -->
### UC-{NUMBER, like UC-001} { Case Title }

<!-- spd:id:usecase -->
**ID**: `spd-{system}-usecase-{slug}`

**Actors**:
<!-- spd:id-ref:actor -->
`spd-{system}-actor-{slug-1}`, `spd-{system}-actor-{slug-2}`
<!-- spd:id-ref:actor -->

<!-- spd:paragraph:preconditions -->
**Preconditions**: {what must already be true}
<!-- spd:paragraph:preconditions -->

<!-- spd:paragraph:flow -->
**Flow**: { optional name of the flow }
<!-- spd:paragraph:flow -->

<!-- spd:numbered-list:flow-steps -->
1. {step description}
2. {step description}
<!-- spd:numbered-list:flow-steps -->

<!-- spd:paragraph:postconditions -->
**Postconditions**: {what becomes true}
<!-- spd:paragraph:postconditions -->

**Alternative Flows**:
<!-- spd:list:alternative-flows -->
- **{condition}**: {what happens, may reference other use cases}
<!-- spd:list:alternative-flows -->

{Add more use cases as needed.}
<!-- spd:id:usecase -->
<!-- spd:###:uc-title repeat="many" -->
<!-- spd:##:usecases -->

<!-- spd:##:nfrs -->
## 5. Non-functional requirements

<!-- spd:###:nfr-title repeat="many" -->
### {NFR Name}

<!-- spd:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,FEATURE" -->
- [ ] `p1` - **ID**: `spd-{system}-nfr-{slug}`

<!-- spd:list:nfr-statements -->
- {Specific, measurable non-functional requirement statement}
- {Another specific, measurable NFR statement}
<!-- spd:list:nfr-statements -->

{Add more non-functional requirements as needed.}
<!-- spd:id:nfr -->
<!-- spd:###:nfr-title repeat="many" -->

<!-- spd:###:intentional-exclusions -->
### Intentional Exclusions

<!-- spd:list:exclusions -->
- **{Category}** ({Checklist IDs}): Not applicable — {reason}
<!-- spd:list:exclusions -->
<!-- spd:###:intentional-exclusions -->
<!-- spd:##:nfrs -->

<!-- spd:##:nongoals -->
## 6. Non-Goals & Risks

<!-- spd:###:nongoals-title -->
### Non-Goals

<!-- spd:list:nongoals -->
- {1-2 sentences describing what is explicitly out of scope and why}
- {Another explicit non-goal with rationale}
<!-- spd:list:nongoals -->
<!-- spd:###:nongoals-title -->

<!-- spd:###:risks-title -->
### Risks

<!-- spd:list:risks -->
- {Risk description with potential impact and mitigation strategy}
- {Another risk with impact and mitigation}
<!-- spd:list:risks -->
<!-- spd:###:risks-title -->
<!-- spd:##:nongoals -->

<!-- spd:##:assumptions -->
## 7. Assumptions & Open Questions

<!-- spd:###:assumptions-title -->
### Assumptions

<!-- spd:list:assumptions -->
- {Assumption statement with basis and potential impact if wrong}
- {Another assumption with rationale}
<!-- spd:list:assumptions -->
<!-- spd:###:assumptions-title -->

<!-- spd:###:open-questions-title -->
### Open Questions

<!-- spd:list:open-questions -->
- {Open question requiring resolution} — Owner: {name}, Target: {date}
<!-- spd:list:open-questions -->
<!-- spd:###:open-questions-title -->
<!-- spd:##:assumptions -->

<!-- spd:##:context -->
## 8. Additional context

<!-- spd:###:context-title repeat="many" -->
### {Context Item}

<!-- spd:free:prd-context-notes -->
{Context notes, links, or background information. This section is optional. Use it for stakeholder notes, business context, market notes, research links, etc.}
<!-- spd:free:prd-context-notes -->
<!-- spd:###:context-title repeat="many" -->
<!-- spd:##:context -->
<!-- spd:#:prd -->