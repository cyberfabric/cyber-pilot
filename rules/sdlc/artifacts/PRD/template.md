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

<!-- fdd:##:overview -->
## 1. Overview

<!-- fdd:paragraph:purpose -->
**Purpose**: {1-3 sentences describing what the product/system is}
<!-- fdd:paragraph:purpose -->

<!-- fdd:paragraph:context -->
{1-2 short paragraphs providing high-level context.}
<!-- fdd:paragraph:context -->

**Target Users**:
<!-- fdd:list:target-users required="true" -->
- {Primary user type and their role}
- {Secondary user type and their role}
<!-- fdd:list:target-users -->

**Key Problems Solved**:
<!-- fdd:list:key-problems required="true" -->
- {1-3 sentences describing a key problem this product solves}
- {1-3 sentences describing another key problem}
<!-- fdd:list:key-problems -->

**Success Criteria**:
<!-- fdd:list:success-criteria required="true" -->
- {Measurable outcome with target metric and timeline}
- {Another measurable outcome with target metric}
<!-- fdd:list:success-criteria -->

**Capabilities**:
<!-- fdd:list:capabilities required="true" -->
- {1-2 sentences describing a core capability}
- {1-2 sentences describing another capability}
<!-- fdd:list:capabilities -->
<!-- fdd:##:overview -->

<!-- fdd:##:actors -->
## 2. Actors

<!-- fdd:###:actor-title repeat="many" -->
### {Actor Name}

<!-- fdd:id:actor -->
**ID**: `fdd-{system}-actor-{slug}`

<!-- fdd:paragraph:actor-role repeat="many" -->
**Role**: {1-3 sentences describing responsibilities and goals}
<!-- fdd:paragraph:actor-role -->

{Add more actors as needed.}
<!-- fdd:id:actor -->
<!-- fdd:###:actor-title repeat="many" -->
<!-- fdd:##:actors -->

<!-- fdd:##:frs -->
## 3. Functional Requirements

<!-- fdd:###:fr-title repeat="many" -->
### FR-{NUMBER, like FR-001} { Functional Requirement Title }

<!-- fdd:id:fr has="priority,task" covered_by="DESIGN,FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-{system}-fr-{slug}`

<!-- fdd:free:fr-summary -->
{Describe the functional requirement in appropriate detail. You should choose suitable format - paragraphs, bullet points, or a combination - based on content complexity.}
<!-- fdd:free:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-{system}-actor-{slug-1}`, `fdd-{system}-actor-{slug-2}`
<!-- fdd:id-ref:actor -->
<!-- fdd:id:fr -->
<!-- fdd:###:fr-title repeat="many" -->
<!-- fdd:##:frs -->

<!-- fdd:##:usecases -->
## 4. Use Cases

<!-- fdd:###:uc-title repeat="many" -->
### UC-{NUMBER, like UC-001} { Case Title }

<!-- fdd:id:usecase -->
**ID**: `fdd-{system}-usecase-{slug}`

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-{system}-actor-{slug-1}`, `fdd-{system}-actor-{slug-2}`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: {what must already be true}
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**: { optional name of the flow }
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. {step description}
2. {step description}
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: {what becomes true}
<!-- fdd:paragraph:postconditions -->

**Alternative Flows**:
<!-- fdd:list:alternative-flows -->
- **{condition}**: {what happens, may reference other use cases}
<!-- fdd:list:alternative-flows -->

{Add more use cases as needed.}
<!-- fdd:id:usecase -->
<!-- fdd:###:uc-title repeat="many" -->
<!-- fdd:##:usecases -->

<!-- fdd:##:nfrs -->
## 5. Non-functional requirements

<!-- fdd:###:nfr-title repeat="many" -->
### {NFR Name}

<!-- fdd:id:nfr has="priority,task" covered_by="DESIGN,FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-{system}-nfr-{slug}`

<!-- fdd:list:nfr-statements -->
- {Specific, measurable non-functional requirement statement}
- {Another specific, measurable NFR statement}
<!-- fdd:list:nfr-statements -->

{Add more non-functional requirements as needed.}
<!-- fdd:id:nfr -->
<!-- fdd:###:nfr-title repeat="many" -->

<!-- fdd:###:intentional-exclusions -->
### Intentional Exclusions

<!-- fdd:list:exclusions -->
- **{Category}** ({Checklist IDs}): Not applicable — {reason}
<!-- fdd:list:exclusions -->
<!-- fdd:###:intentional-exclusions -->
<!-- fdd:##:nfrs -->

<!-- fdd:##:nongoals -->
## 6. Non-Goals & Risks

<!-- fdd:###:nongoals-title -->
### Non-Goals

<!-- fdd:list:nongoals -->
- {1-2 sentences describing what is explicitly out of scope and why}
- {Another explicit non-goal with rationale}
<!-- fdd:list:nongoals -->
<!-- fdd:###:nongoals-title -->

<!-- fdd:###:risks-title -->
### Risks

<!-- fdd:list:risks -->
- {Risk description with potential impact and mitigation strategy}
- {Another risk with impact and mitigation}
<!-- fdd:list:risks -->
<!-- fdd:###:risks-title -->
<!-- fdd:##:nongoals -->

<!-- fdd:##:assumptions -->
## 7. Assumptions & Open Questions

<!-- fdd:###:assumptions-title -->
### Assumptions

<!-- fdd:list:assumptions -->
- {Assumption statement with basis and potential impact if wrong}
- {Another assumption with rationale}
<!-- fdd:list:assumptions -->
<!-- fdd:###:assumptions-title -->

<!-- fdd:###:open-questions-title -->
### Open Questions

<!-- fdd:list:open-questions -->
- {Open question requiring resolution} — Owner: {name}, Target: {date}
<!-- fdd:list:open-questions -->
<!-- fdd:###:open-questions-title -->
<!-- fdd:##:assumptions -->

<!-- fdd:##:context -->
## 8. Additional context

<!-- fdd:###:context-title repeat="many" -->
### {Context Item}

<!-- fdd:free:prd-context-notes -->
{Context notes, links, or background information. This section is optional. Use it for stakeholder notes, business context, market notes, research links, etc.}
<!-- fdd:free:prd-context-notes -->
<!-- fdd:###:context-title repeat="many" -->
<!-- fdd:##:context -->
<!-- fdd:#:prd -->