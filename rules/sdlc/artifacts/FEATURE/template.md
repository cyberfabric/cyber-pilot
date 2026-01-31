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

<!-- fdd:##:context -->
## A. Feature Context

<!-- fdd:id-ref:feature has="task" -->
[ ] - `fdd-{project-name}-feature-{feature-slug}`
<!-- fdd:id-ref:feature -->

<!-- fdd:paragraph:status -->
**Status**: NOT_STARTED
<!-- fdd:paragraph:status -->

<!-- fdd:paragraph:overview -->
### 1. Overview
{1-2 paragraphs summarizing what this feature does and why it exists.}

{Include:
- Problem statement
- Primary user value
- Key assumptions}
<!-- fdd:paragraph:overview -->

<!-- fdd:paragraph:purpose -->
### 2. Purpose
{1-3 sentences describing the intended outcome of this feature.}

{Optionally include measurable success criteria.}
<!-- fdd:paragraph:purpose -->

<!-- fdd:list:actors -->
### 3. Actors
{List the actors involved in this feature by backticked `fdd-*-actor-*` IDs.}
- `fdd-{project}-actor-{slug}`
- `fdd-{project}-actor-{slug}`
<!-- fdd:list:actors -->

<!-- fdd:list:references -->
### 4. References
- Overall Design: [DESIGN.md](../../DESIGN.md)
- ADRs: `fdd-{project}-adr-{slug}`
- Related feature: `fdd-{project}-feature-{slug}`
<!-- fdd:list:references -->
<!-- fdd:##:context -->

<!-- fdd:##:flows -->
## B. Actor Flows

<!-- fdd:###:flow-title repeat="many" -->
### {Flow Name}

<!-- fdd:id:flow has="priority,task" covered_by="src" to_code="true" -->
**ID**: [ ] `p1` - `fdd-{project}-feature-{feature}-flow-{slug}`
<!-- fdd:id:flow -->

<!-- fdd:fdl:flow-steps -->
1. [ ] - `ph-1` - {step description} - `inst-step-1`
2. [ ] - `ph-1` - **IF** {condition}: - `inst-if`
   1. [ ] - `ph-1` - {nested step} - `inst-if-nested`
3. [ ] - `ph-1` - {next step} - `inst-step-3`
<!-- fdd:fdl:flow-steps -->
<!-- fdd:###:flow-title repeat="many" -->
<!-- fdd:##:flows -->

<!-- fdd:##:algorithms -->
## C. Algorithms

<!-- fdd:###:algo-title repeat="many" -->
### {Algorithm Name}

<!-- fdd:id:algo has="priority,task" covered_by="src" to_code="true" -->
**ID**: [ ] `p1` - `fdd-{project}-feature-{feature}-algo-{slug}`
<!-- fdd:id:algo -->

<!-- fdd:fdl:algo-steps -->
1. [ ] - `ph-1` - {step description} - `inst-step-1`
2. [ ] - `ph-1` - **RETURN** {result} - `inst-return`
<!-- fdd:fdl:algo-steps -->
<!-- fdd:###:algo-title repeat="many" -->
<!-- fdd:##:algorithms -->

<!-- fdd:##:states -->
## D. States

<!-- fdd:###:state-title repeat="many" -->
### {State Machine Name}

<!-- fdd:id:state has="priority,task" covered_by="src" to_code="true" -->
**ID**: [ ] `p1` - `fdd-{project}-feature-{feature}-state-{slug}`
<!-- fdd:id:state -->

<!-- fdd:fdl:state-transitions -->
1. [ ] - `ph-1` - **FROM** {STATE} **TO** {STATE} **WHEN** {trigger} - `inst-transition-1`
2. [ ] - `ph-1` - **FROM** {STATE} **TO** {STATE} **WHEN** {trigger} - `inst-transition-2`
<!-- fdd:fdl:state-transitions -->
<!-- fdd:###:state-title repeat="many" -->
<!-- fdd:##:states -->

<!-- fdd:##:requirements -->
## E. Requirements

<!-- fdd:###:req-title repeat="many" -->
### {Requirement Name}

<!-- fdd:id:feature-requirement has="priority,task" covered_by="src" to_code="true" -->
**ID**: [ ] `p1` - `fdd-{project}-feature-{feature}-req-{slug}`
<!-- fdd:id:feature-requirement -->

<!-- fdd:paragraph:req-body -->
{Describe what must be true when this requirement is satisfied.}
<!-- fdd:paragraph:req-body -->

<!-- fdd:list:req-impl -->
**Implementation details**:
- API: {endpoints}
- DB: {tables/queries}
- Domain: {entities}
<!-- fdd:list:req-impl -->

<!-- fdd:list:req-implements -->
**Implements**:
- `fdd-{project}-feature-{feature}-flow-{slug}`
- `fdd-{project}-feature-{feature}-algo-{slug}`
<!-- fdd:list:req-implements -->

<!-- fdd:task-list:req-phases has="priority" -->
**Phases**:
- [ ] `p1` - {scope}
- [ ] `p2` - {scope}
<!-- fdd:task-list:req-phases -->
<!-- fdd:###:req-title repeat="many" -->
<!-- fdd:##:requirements -->

<!-- fdd:##:additional-context -->
## F. Additional Context (optional)

<!-- fdd:id:feature-context has="task" -->
**ID**: [ ] `p1` - `fdd-{project}-feature-{feature}-context-{slug}`
<!-- fdd:id:feature-context -->

<!-- fdd:paragraph:context-notes -->
{Optional notes, decisions, constraints, links, and rationale.}
<!-- fdd:paragraph:context-notes -->
<!-- fdd:##:additional-context -->

<!-- fdd:#:feature-design -->
