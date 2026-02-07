<!-- cpt:#:prd -->
# PRD

<!-- cpt:##:overview -->
## 1. Overview

<!-- cpt:paragraph:purpose -->
**Purpose**: TaskFlow is a lightweight task management system for small teams, enabling task creation, assignment, and progress tracking with real-time notifications.
<!-- cpt:paragraph:purpose -->

<!-- cpt:paragraph:context -->
The system focuses on simplicity and speed, allowing teams to manage their daily work without the overhead of complex project management tools. TaskFlow bridges the gap between simple to-do lists and enterprise-grade solutions.
<!-- cpt:paragraph:context -->

**Target Users**:
<!-- cpt:list:target-users required="true" -->
- Team leads managing sprints
- Developers tracking daily work
- Project managers monitoring progress
<!-- cpt:list:target-users -->

**Key Problems Solved**:
<!-- cpt:list:key-problems required="true" -->
- Scattered task tracking across multiple tools
- Lack of visibility into team workload
- Missing deadline notifications
<!-- cpt:list:key-problems -->

**Success Criteria**:
<!-- cpt:list:success-criteria required="true" -->
- Tasks created and assigned in under 30 seconds (Baseline: not measured; Target: v1.0)
- Real-time status updates visible to all team members within 2 seconds (Baseline: N/A; Target: v1.0)
- Overdue task alerts delivered within 1 minute of deadline (Baseline: N/A; Target: v1.0)
<!-- cpt:list:success-criteria -->

**Capabilities**:
<!-- cpt:list:capabilities required="true" -->
- Manage team tasks and assignments
- Track task status and progress in real time
- Send notifications for deadlines and status changes
<!-- cpt:list:capabilities -->
<!-- cpt:##:overview -->

<!-- cpt:##:actors -->
## 2. Actors

<!-- cpt:###:actor-title repeat="many" -->
### Team Member

<!-- cpt:id:actor has="task" -->
- [ ] **ID**: `cpt-taskflow-actor-member`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Creates tasks, updates progress, and collaborates on assignments.
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Team Lead

<!-- cpt:id:actor has="task" -->
- [ ] **ID**: `cpt-taskflow-actor-lead`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Assigns tasks, sets priorities, and monitors team workload.
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Notification Service

<!-- cpt:id:actor has="task" -->
- [ ] **ID**: `cpt-taskflow-actor-notifier`

<!-- cpt:paragraph:actor-role repeat="many" -->
**Role**: Sends alerts for due dates, assignments, and status changes.
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->
<!-- cpt:##:actors -->

<!-- cpt:##:frs -->
## 3. Functional Requirements

<!-- cpt:###:fr-title repeat="many" -->
### FR-001 Task Management

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `cpt-taskflow-fr-task-management`

<!-- cpt:free:fr-summary -->
The system MUST allow creating, editing, and deleting tasks. The system MUST allow assigning tasks to team members. The system MUST allow setting due dates and priorities. Tasks should support rich text descriptions and file attachments.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-taskflow-actor-member`, `cpt-taskflow-actor-lead`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-002 Notifications

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `cpt-taskflow-fr-notifications`

<!-- cpt:free:fr-summary -->
The system MUST send push notifications for task assignments. The system MUST send alerts for overdue tasks. Notifications should be configurable per user to allow opting out of certain notification types.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-taskflow-actor-notifier`, `cpt-taskflow-actor-member`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->
<!-- cpt:##:frs -->

<!-- cpt:##:usecases -->
## 4. Use Cases

<!-- cpt:###:uc-title repeat="many" -->
### UC-001 Create and Assign Task
<!-- cpt:###:uc-title repeat="many" -->

<!-- cpt:id:usecase -->
**ID**: `cpt-taskflow-usecase-create-task`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-taskflow-actor-lead`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: User is authenticated and has team lead permissions.
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**: Create Task Flow
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. Lead creates a new task with title and description
2. Lead assigns task to a team member
3. Lead sets due date and priority
4. System validates task data
5. System sends notification to assignee
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: Task appears in assignee's task list; notification sent.
<!-- cpt:paragraph:postconditions -->

**Alternative Flows**:
<!-- cpt:list:alternative-flows -->
- **Validation fails**: If step 4 fails validation (e.g., no assignee selected), system displays error and returns to step 2
<!-- cpt:list:alternative-flows -->
<!-- cpt:id:usecase -->

<!-- cpt:##:usecases -->

<!-- cpt:##:nfrs -->
## 5. Non-functional requirements

<!-- cpt:###:nfr-title repeat="many" -->
### Security

<!-- cpt:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `cpt-taskflow-nfr-security`

<!-- cpt:list:nfr-statements -->
- Authentication MUST be required for all user actions
- Authorization MUST enforce team role permissions
- Passwords MUST be stored using secure hashing algorithms
<!-- cpt:list:nfr-statements -->
<!-- cpt:id:nfr -->
<!-- cpt:###:nfr-title repeat="many" -->

<!-- cpt:###:nfr-title repeat="many" -->
### Performance

<!-- cpt:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [ ] `p2` - **ID**: `cpt-taskflow-nfr-performance`

<!-- cpt:list:nfr-statements -->
- Task list SHOULD load within 500ms for teams under 100 tasks
- Real-time updates SHOULD propagate within 2 seconds
<!-- cpt:list:nfr-statements -->
<!-- cpt:id:nfr -->
<!-- cpt:###:nfr-title repeat="many" -->

<!-- cpt:###:intentional-exclusions -->
### Intentional Exclusions

<!-- cpt:list:exclusions -->
- **Accessibility** (UX-PRD-002): Not applicable — MVP targets internal teams with standard desktop browsers
- **Internationalization** (UX-PRD-003): Not applicable — English-only for initial release
- **Regulatory Compliance** (COMPL-PRD-001/002/003): Not applicable — No PII or regulated data in MVP scope
<!-- cpt:list:exclusions -->
<!-- cpt:###:intentional-exclusions -->
<!-- cpt:##:nfrs -->

<!-- cpt:##:nongoals -->
## 6. Non-Goals & Risks

<!-- cpt:###:nongoals-title -->
### Non-Goals

<!-- cpt:list:nongoals -->
- TaskFlow does NOT replace full project management suites (Jira, Asana)
- TaskFlow does NOT include time tracking or billing specs
- TaskFlow does NOT support cross-organization collaboration in v1.0
<!-- cpt:list:nongoals -->
<!-- cpt:###:nongoals-title -->

<!-- cpt:###:risks-title -->
### Risks

<!-- cpt:list:risks -->
- **Adoption risk**: Teams may resist switching from existing tools. Mitigation: focus on migration path and quick wins.
- **Scale risk**: Real-time specs may not scale beyond 50 concurrent users. Mitigation: load testing before launch.
<!-- cpt:list:risks -->
<!-- cpt:###:risks-title -->
<!-- cpt:##:nongoals -->

<!-- cpt:##:assumptions -->
## 7. Assumptions & Open Questions

<!-- cpt:###:assumptions-title -->
### Assumptions

<!-- cpt:list:assumptions -->
- Teams have reliable internet connectivity for real-time specs
- Users have modern browsers (Chrome, Firefox, Safari, Edge)
- Initial deployment will be cloud-hosted (no on-premise requirement)
<!-- cpt:list:assumptions -->
<!-- cpt:###:assumptions-title -->

<!-- cpt:###:open-questions-title -->
### Open Questions

<!-- cpt:list:open-questions -->
- Should we support mobile apps in v1.0? — Owner: PM, Target: 2024-02-15
- What notification channels beyond push (email, Slack)? — Owner: Engineering, Target: 2024-02-01
<!-- cpt:list:open-questions -->
<!-- cpt:###:open-questions-title -->
<!-- cpt:##:assumptions -->

<!-- cpt:##:context -->
## 8. Additional context

<!-- cpt:###:context-title repeat="many" -->
### Stakeholder Notes

<!-- cpt:free:prd-context-notes -->
This product targets teams of 3-20 people initially. Competitive analysis shows gap between free tools and enterprise solutions. Budget approved for 6-month MVP development cycle.
<!-- cpt:free:prd-context-notes -->
<!-- cpt:###:context-title repeat="many" -->
<!-- cpt:##:context -->
<!-- cpt:#:prd -->
