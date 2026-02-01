<!-- fdd:#:prd -->
# PRD

<!-- fdd:##:overview -->
## A. Vision

<!-- fdd:paragraph:purpose -->
**Purpose**: TaskFlow is a lightweight task management system for small teams, enabling task creation, assignment, and progress tracking with real-time notifications.
<!-- fdd:paragraph:purpose -->

<!-- fdd:paragraph:context -->
The system focuses on simplicity and speed, allowing teams to manage their daily work without the overhead of complex project management tools. TaskFlow bridges the gap between simple to-do lists and enterprise-grade solutions.
<!-- fdd:paragraph:context -->

**Target Users**:
<!-- fdd:list:target-users required="true" -->
- Team leads managing sprints
- Developers tracking daily work
- Project managers monitoring progress
<!-- fdd:list:target-users -->

**Key Problems Solved**:
<!-- fdd:list:key-problems required="true" -->
- Scattered task tracking across multiple tools
- Lack of visibility into team workload
- Missing deadline notifications
<!-- fdd:list:key-problems -->

**Success Criteria**:
<!-- fdd:list:success-criteria required="true" -->
- Tasks created and assigned in under 30 seconds (Baseline: not measured; Target: v1.0)
- Real-time status updates visible to all team members within 2 seconds (Baseline: N/A; Target: v1.0)
- Overdue task alerts delivered within 1 minute of deadline (Baseline: N/A; Target: v1.0)
<!-- fdd:list:success-criteria -->

**Capabilities**:
<!-- fdd:list:capabilities required="true" -->
- Manage team tasks and assignments
- Track task status and progress in real time
- Send notifications for deadlines and status changes
<!-- fdd:list:capabilities -->
<!-- fdd:##:overview -->

<!-- fdd:##:actors -->
## B. Actors

<!-- fdd:###:actor-title repeat="many" -->
### Team Member

<!-- fdd:id:actor has="task" -->
- [ ] **ID**: `fdd-taskflow-actor-member`

<!-- fdd:paragraph:actor-role repeat="many" -->
**Role**: Creates tasks, updates progress, and collaborates on assignments.
<!-- fdd:paragraph:actor-role -->
<!-- fdd:id:actor -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### Team Lead

<!-- fdd:id:actor has="task" -->
- [ ] **ID**: `fdd-taskflow-actor-lead`

<!-- fdd:paragraph:actor-role repeat="many" -->
**Role**: Assigns tasks, sets priorities, and monitors team workload.
<!-- fdd:paragraph:actor-role -->
<!-- fdd:id:actor -->
<!-- fdd:###:actor-title repeat="many" -->

<!-- fdd:###:actor-title repeat="many" -->
### Notification Service

<!-- fdd:id:actor has="task" -->
- [ ] **ID**: `fdd-taskflow-actor-notifier`

<!-- fdd:paragraph:actor-role repeat="many" -->
**Role**: Sends alerts for due dates, assignments, and status changes.
<!-- fdd:paragraph:actor-role -->
<!-- fdd:id:actor -->
<!-- fdd:###:actor-title repeat="many" -->
<!-- fdd:##:actors -->

<!-- fdd:##:frs -->
## C. Functional Requirements

<!-- fdd:###:fr-title repeat="many" -->
### FR-001 Task Management

<!-- fdd:id:fr has="priority,task" covered_by="DESIGN,FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-taskflow-fr-task-management`

<!-- fdd:free:fr-summary -->
The system MUST allow creating, editing, and deleting tasks. The system MUST allow assigning tasks to team members. The system MUST allow setting due dates and priorities. Tasks should support rich text descriptions and file attachments.
<!-- fdd:free:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-taskflow-actor-member`, `fdd-taskflow-actor-lead`
<!-- fdd:id-ref:actor -->
<!-- fdd:id:fr -->
<!-- fdd:###:fr-title repeat="many" -->

<!-- fdd:###:fr-title repeat="many" -->
### FR-002 Notifications

<!-- fdd:id:fr has="priority,task" covered_by="DESIGN,FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-taskflow-fr-notifications`

<!-- fdd:free:fr-summary -->
The system MUST send push notifications for task assignments. The system MUST send alerts for overdue tasks. Notifications should be configurable per user to allow opting out of certain notification types.
<!-- fdd:free:fr-summary -->

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-taskflow-actor-notifier`, `fdd-taskflow-actor-member`
<!-- fdd:id-ref:actor -->
<!-- fdd:id:fr -->
<!-- fdd:###:fr-title repeat="many" -->
<!-- fdd:##:frs -->

<!-- fdd:##:usecases -->
## D. Use Cases

<!-- fdd:###:uc-title repeat="many" -->
### UC-001 Create and Assign Task

<!-- fdd:id:usecase -->
**ID**: `fdd-taskflow-usecase-create-task`

**Actors**:
<!-- fdd:id-ref:actor -->
`fdd-taskflow-actor-lead`
<!-- fdd:id-ref:actor -->

<!-- fdd:paragraph:preconditions -->
**Preconditions**: User is authenticated and has team lead permissions.
<!-- fdd:paragraph:preconditions -->

<!-- fdd:paragraph:flow -->
**Flow**: Create Task Flow
<!-- fdd:paragraph:flow -->

<!-- fdd:numbered-list:flow-steps -->
1. Lead creates a new task with title and description
2. Lead assigns task to a team member
3. Lead sets due date and priority
4. System validates task data
5. System sends notification to assignee
<!-- fdd:numbered-list:flow-steps -->

<!-- fdd:paragraph:postconditions -->
**Postconditions**: Task appears in assignee's task list; notification sent.
<!-- fdd:paragraph:postconditions -->

**Alternative Flows**:
<!-- fdd:list:alternative-flows -->
- **Validation fails**: If step 4 fails validation (e.g., no assignee selected), system displays error and returns to step 2
<!-- fdd:list:alternative-flows -->
<!-- fdd:id:usecase -->
<!-- fdd:###:uc-title repeat="many" -->
<!-- fdd:##:usecases -->

<!-- fdd:##:nfrs -->
## E. Non-functional requirements

<!-- fdd:###:nfr-title repeat="many" -->
### Security

<!-- fdd:id:nfr has="priority,task" covered_by="DESIGN,FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-taskflow-nfr-security`

<!-- fdd:list:nfr-statements -->
- Authentication MUST be required for all user actions
- Authorization MUST enforce team role permissions
- Passwords MUST be stored using secure hashing algorithms
<!-- fdd:list:nfr-statements -->
<!-- fdd:id:nfr -->
<!-- fdd:###:nfr-title repeat="many" -->

<!-- fdd:###:nfr-title repeat="many" -->
### Performance

<!-- fdd:id:nfr has="priority,task" covered_by="DESIGN,FEATURES,FEATURE" -->
- [ ] `p2` - **ID**: `fdd-taskflow-nfr-performance`

<!-- fdd:list:nfr-statements -->
- Task list SHOULD load within 500ms for teams under 100 tasks
- Real-time updates SHOULD propagate within 2 seconds
<!-- fdd:list:nfr-statements -->
<!-- fdd:id:nfr -->
<!-- fdd:###:nfr-title repeat="many" -->

<!-- fdd:###:intentional-exclusions -->
### Intentional Exclusions

<!-- fdd:list:exclusions -->
- **Accessibility** (UX-PRD-002): Not applicable — MVP targets internal teams with standard desktop browsers
- **Internationalization** (UX-PRD-003): Not applicable — English-only for initial release
- **Regulatory Compliance** (COMPL-PRD-001/002/003): Not applicable — No PII or regulated data in MVP scope
<!-- fdd:list:exclusions -->
<!-- fdd:###:intentional-exclusions -->
<!-- fdd:##:nfrs -->

<!-- fdd:##:nongoals -->
## F. Non-Goals & Risks

<!-- fdd:###:nongoals-title -->
### Non-Goals

<!-- fdd:list:nongoals -->
- TaskFlow does NOT replace full project management suites (Jira, Asana)
- TaskFlow does NOT include time tracking or billing features
- TaskFlow does NOT support cross-organization collaboration in v1.0
<!-- fdd:list:nongoals -->
<!-- fdd:###:nongoals-title -->

<!-- fdd:###:risks-title -->
### Risks

<!-- fdd:list:risks -->
- **Adoption risk**: Teams may resist switching from existing tools. Mitigation: focus on migration path and quick wins.
- **Scale risk**: Real-time features may not scale beyond 50 concurrent users. Mitigation: load testing before launch.
<!-- fdd:list:risks -->
<!-- fdd:###:risks-title -->
<!-- fdd:##:nongoals -->

<!-- fdd:##:assumptions -->
## G. Assumptions & Open Questions

<!-- fdd:###:assumptions-title -->
### Assumptions

<!-- fdd:list:assumptions -->
- Teams have reliable internet connectivity for real-time features
- Users have modern browsers (Chrome, Firefox, Safari, Edge)
- Initial deployment will be cloud-hosted (no on-premise requirement)
<!-- fdd:list:assumptions -->
<!-- fdd:###:assumptions-title -->

<!-- fdd:###:open-questions-title -->
### Open Questions

<!-- fdd:list:open-questions -->
- Should we support mobile apps in v1.0? — Owner: PM, Target: 2024-02-15
- What notification channels beyond push (email, Slack)? — Owner: Engineering, Target: 2024-02-01
<!-- fdd:list:open-questions -->
<!-- fdd:###:open-questions-title -->
<!-- fdd:##:assumptions -->

<!-- fdd:##:context -->
## H. Additional context

<!-- fdd:###:context-title repeat="many" -->
### Stakeholder Notes

<!-- fdd:free:prd-context-notes -->
This product targets teams of 3-20 people initially. Competitive analysis shows gap between free tools and enterprise solutions. Budget approved for 6-month MVP development cycle.
<!-- fdd:free:prd-context-notes -->
<!-- fdd:###:context-title repeat="many" -->
<!-- fdd:##:context -->
<!-- fdd:#:prd -->
