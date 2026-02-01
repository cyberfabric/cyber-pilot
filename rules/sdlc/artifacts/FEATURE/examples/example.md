<!-- fdd:#:feature-design -->
# Feature: Task CRUD

<!-- fdd:id-ref:feature has="task" -->
[ ] - `fdd-taskflow-feature-task-crud`
<!-- fdd:id-ref:feature -->

<!-- fdd:##:context -->
## A. Feature Context

<!-- fdd:overview -->
### 1. Overview
Core task management functionality for creating, viewing, updating, and deleting tasks. This feature provides the foundation for team collaboration by enabling users to track work items through their lifecycle.

Problem: Teams need a central place to track tasks with status, priority, and assignments.
Primary value: Enables organized task tracking with clear ownership.
Key assumptions: Users have accounts and belong to at least one team.
<!-- fdd:overview -->

<!-- fdd:paragraph:purpose -->
### 2. Purpose
Enable team members to manage their work items with full lifecycle tracking from creation through completion.

Success criteria: Users can create, view, update, and delete tasks within 500ms response time.
<!-- fdd:paragraph:purpose -->

### 3. Actors
<!-- fdd:id-ref:actor -->
- `fdd-taskflow-actor-member`
- `fdd-taskflow-actor-lead`
<!-- fdd:id-ref:actor -->

### 4. References
<!-- fdd:list:references -->
- Overall Design: [DESIGN.md](../../DESIGN.md)
- ADRs: `fdd-taskflow-adr-postgres-storage`
- Related feature: `fdd-taskflow-feature-notifications`
<!-- fdd:list:references -->
<!-- fdd:##:context -->

<!-- fdd:##:flows -->
## B. Actor Flows

<!-- fdd:###:flow-title repeat="many" -->
### Create Task

<!-- fdd:id:flow has="priority,task" to_code="true" -->
- [ ] `p1` - **ID**: `fdd-taskflow-feature-task-crud-flow-create`

**Actors**:
<!-- fdd:id-ref:actor -->
- `fdd-taskflow-actor-member`
- `fdd-taskflow-actor-lead`
<!-- fdd:id-ref:actor -->

<!-- fdd:fdl:flow-steps -->
1. [x] - `ph-1` - User fills task form (title, description, priority) - `inst-fill-form`
2. [x] - `ph-1` - API: POST /api/tasks (body: title, description, priority, due_date) - `inst-api-create`
3. [x] - `ph-1` - Algorithm: validate task input using `fdd-taskflow-feature-task-crud-algo-validate` - `inst-run-validate`
4. [x] - `ph-1` - DB: INSERT tasks(title, description, priority, due_date, status=BACKLOG) - `inst-db-insert`
5. [ ] - `ph-2` - User optionally assigns task to team member - `inst-assign`
6. [ ] - `ph-2` - API: POST /api/tasks/{task_id}/assignees (body: assignee_id) - `inst-api-assign`
7. [ ] - `ph-2` - DB: INSERT task_assignees(task_id, assignee_id) - `inst-db-assign-insert`
8. [x] - `ph-1` - API: RETURN 201 Created (task_id, status=BACKLOG) - `inst-return-created`
<!-- fdd:fdl:flow-steps -->
<!-- fdd:id:flow -->
<!-- fdd:###:flow-title repeat="many" -->
<!-- fdd:##:flows -->

<!-- fdd:##:algorithms -->
## C. Algorithms

<!-- fdd:###:algo-title repeat="many" -->
### Validate Task

<!-- fdd:id:algo has="priority,task" to_code="true" -->
- [ ] `p1` - **ID**: `fdd-taskflow-feature-task-crud-algo-validate`

<!-- fdd:fdl:algo-steps -->
1. [x] - `ph-1` - **IF** title is empty **RETURN** error "Title required" - `inst-check-title`
2. [x] - `ph-1` - **IF** priority not in [LOW, MEDIUM, HIGH] **RETURN** error - `inst-check-priority`
3. [x] - `ph-1` - **IF** due_date is present AND due_date is in the past **RETURN** error - `inst-check-due-date`
4. [x] - `ph-1` - DB: SELECT tasks WHERE title=? AND status!=DONE (dedupe check) - `inst-db-dedupe-check`
5. [ ] - `ph-2` - **IF** duplicate exists **RETURN** error - `inst-return-duplicate`
6. [x] - `ph-1` - **RETURN** valid - `inst-return-valid`
<!-- fdd:fdl:algo-steps -->
<!-- fdd:id:algo -->
<!-- fdd:###:algo-title repeat="many" -->
<!-- fdd:##:algorithms -->

<!-- fdd:##:states -->
## D. States

<!-- fdd:###:state-title repeat="many" -->
### Task Status

<!-- fdd:id:state has="priority,task" to_code="true" -->
- [ ] `p1` - **ID**: `fdd-taskflow-feature-task-crud-state-status`

<!-- fdd:fdl:state-transitions -->
1. [x] - `ph-1` - **FROM** BACKLOG **TO** IN_PROGRESS **WHEN** user starts work - `inst-start`
2. [ ] - `ph-2` - **FROM** IN_PROGRESS **TO** DONE **WHEN** user completes - `inst-complete`
3. [ ] - `ph-2` - **FROM** DONE **TO** BACKLOG **WHEN** user reopens - `inst-reopen`
<!-- fdd:fdl:state-transitions -->
<!-- fdd:id:state -->
<!-- fdd:###:state-title repeat="many" -->
<!-- fdd:##:states -->

<!-- fdd:##:requirements -->
## E. Requirements

<!-- fdd:###:req-title repeat="many" -->
### Task Creation

<!-- fdd:id:req has="priority,task" to_code="true" -->
- [ ] `p1` - **ID**: `fdd-taskflow-feature-task-crud-req-create`

<!-- fdd:paragraph:req-body -->
Users can create tasks with title, description, priority, and due date. The system validates input and stores the task with BACKLOG status.
<!-- fdd:paragraph:req-body -->

**Implementation details**:
<!-- fdd:list:req-impl -->
- API: `POST /api/tasks` with JSON body `{title, description, priority, due_date}`
- DB: insert into `tasks` table (columns: title, description, priority, due_date, status)
- Domain: `Task` entity (id, title, description, priority, due_date, status)
<!-- fdd:list:req-impl -->

**Implements**:
<!-- fdd:id-ref:flow has="priority" -->
- `p1` - `fdd-taskflow-feature-task-crud-flow-create`
<!-- fdd:id-ref:flow -->

<!-- fdd:id-ref:algo has="priority" -->
- `p1` - `fdd-taskflow-feature-task-crud-algo-validate`
<!-- fdd:id-ref:algo -->

**Covers (PRD)**:
<!-- fdd:id-ref:fr -->
- `fdd-taskflow-fr-task-management`
<!-- fdd:id-ref:fr -->

<!-- fdd:id-ref:nfr -->
- `fdd-taskflow-nfr-performance`
<!-- fdd:id-ref:nfr -->

**Covers (DESIGN)**:
<!-- fdd:id-ref:principle -->
- `fdd-taskflow-principle-realtime-first`
<!-- fdd:id-ref:principle -->

<!-- fdd:id-ref:constraint -->
- `fdd-taskflow-constraint-supported-platforms`
<!-- fdd:id-ref:constraint -->

<!-- fdd:id-ref:component -->
- `fdd-taskflow-component-api-server`
- `fdd-taskflow-component-postgresql`
<!-- fdd:id-ref:component -->

<!-- fdd:id-ref:seq -->
- `fdd-taskflow-seq-task-creation`
<!-- fdd:id-ref:seq -->

<!-- fdd:id-ref:dbtable -->
- `fdd-taskflow-dbtable-tasks`
<!-- fdd:id-ref:dbtable -->
<!-- fdd:id:req -->
<!-- fdd:###:req-title repeat="many" -->
<!-- fdd:##:requirements -->

<!-- fdd:##:additional-context -->
## F. Additional Context (optional)

<!-- fdd:free:context-notes -->
The feature must keep task status transitions consistent with the Task Status state machine in Section D. All state changes should emit events for the notification system.
<!-- fdd:free:context-notes -->
<!-- fdd:##:additional-context -->

<!-- fdd:#:feature-design -->
