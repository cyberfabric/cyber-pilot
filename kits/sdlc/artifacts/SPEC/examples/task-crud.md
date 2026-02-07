<!-- cpt:#:spec -->
# Spec: Task CRUD

<!-- cpt:id-ref:spec has="task" -->
- [ ] - `cpt-taskflow-spec-task-crud`
<!-- cpt:id-ref:spec -->

<!-- cpt:##:context -->
## A. Spec Context

<!-- cpt:overview -->
### 1. Overview
Core task management functionality for creating, viewing, updating, and deleting tasks. This spec provides the foundation for team collaboration by enabling users to track work items through their lifecycle.

Problem: Teams need a central place to track tasks with status, priority, and assignments.
Primary value: Enables organized task tracking with clear ownership.
Key assumptions: Users have accounts and belong to at least one team.
<!-- cpt:overview -->

<!-- cpt:paragraph:purpose -->
### 2. Purpose
Enable team members to manage their work items with full lifecycle tracking from creation through completion.

Success criteria: Users can create, view, update, and delete tasks within 500ms response time.
<!-- cpt:paragraph:purpose -->

### 3. Actors
<!-- cpt:id-ref:actor -->
- `cpt-taskflow-actor-member`
- `cpt-taskflow-actor-lead`
<!-- cpt:id-ref:actor -->

### 4. References
<!-- cpt:list:references -->
- Overall Design: [DESIGN.md](../../DESIGN.md)
- ADRs: `cpt-taskflow-adr-postgres-storage`
- Related spec: [Notifications](../notifications.md)
<!-- cpt:list:references -->
<!-- cpt:##:context -->

<!-- cpt:##:flows -->
## B. Actor Flows

<!-- cpt:###:flow-title repeat="many" -->
### Create Task

<!-- cpt:id:flow has="priority,task" to_code="true" -->
- [ ] `p1` - **ID**: `cpt-taskflow-spec-task-crud-flow-create`

**Actors**:
<!-- cpt:id-ref:actor -->
- `cpt-taskflow-actor-member`
- `cpt-taskflow-actor-lead`
<!-- cpt:id-ref:actor -->

<!-- cpt:cdsl:flow-steps -->
1. [x] - `p1` - User fills task form (title, description, priority) - `inst-fill-form`
2. [x] - `p1` - API: POST /api/tasks (body: title, description, priority, due_date) - `inst-api-create`
3. [x] - `p1` - Algorithm: validate task input using `cpt-taskflow-spec-task-crud-algo-validate` - `inst-run-validate`
4. [x] - `p1` - DB: INSERT tasks(title, description, priority, due_date, status=BACKLOG) - `inst-db-insert`
5. [ ] - `p2` - User optionally assigns task to team member - `inst-assign`
6. [ ] - `p2` - API: POST /api/tasks/{task_id}/assignees (body: assignee_id) - `inst-api-assign`
7. [ ] - `p2` - DB: INSERT task_assignees(task_id, assignee_id) - `inst-db-assign-insert`
8. [x] - `p1` - API: RETURN 201 Created (task_id, status=BACKLOG) - `inst-return-created`
<!-- cpt:cdsl:flow-steps -->
<!-- cpt:id:flow -->
<!-- cpt:###:flow-title repeat="many" -->
<!-- cpt:##:flows -->

<!-- cpt:##:algorithms -->
## C. Algorithms

<!-- cpt:###:algo-title repeat="many" -->
### Validate Task

<!-- cpt:id:algo has="priority,task" to_code="true" -->
- [ ] `p1` - **ID**: `cpt-taskflow-spec-task-crud-algo-validate`

<!-- cpt:cdsl:algo-steps -->
1. [x] - `p1` - **IF** title is empty **RETURN** error "Title required" - `inst-check-title`
2. [x] - `p1` - **IF** priority not in [LOW, MEDIUM, HIGH] **RETURN** error - `inst-check-priority`
3. [x] - `p1` - **IF** due_date is present AND due_date is in the past **RETURN** error - `inst-check-due-date`
4. [x] - `p1` - DB: SELECT tasks WHERE title=? AND status!=DONE (dedupe check) - `inst-db-dedupe-check`
5. [ ] - `p2` - **IF** duplicate exists **RETURN** error - `inst-return-duplicate`
6. [x] - `p1` - **RETURN** valid - `inst-return-valid`
<!-- cpt:cdsl:algo-steps -->
<!-- cpt:id:algo -->
<!-- cpt:###:algo-title repeat="many" -->
<!-- cpt:##:algorithms -->

<!-- cpt:##:states -->
## D. States

<!-- cpt:###:state-title repeat="many" -->
### Task Status

<!-- cpt:id:state has="priority,task" to_code="true" -->
- [ ] `p1` - **ID**: `cpt-taskflow-spec-task-crud-state-status`

<!-- cpt:cdsl:state-transitions -->
1. [x] - `p1` - **FROM** BACKLOG **TO** IN_PROGRESS **WHEN** user starts work - `inst-start`
2. [ ] - `p2` - **FROM** IN_PROGRESS **TO** DONE **WHEN** user completes - `inst-complete`
3. [ ] - `p2` - **FROM** DONE **TO** BACKLOG **WHEN** user reopens - `inst-reopen`
<!-- cpt:cdsl:state-transitions -->
<!-- cpt:id:state -->
<!-- cpt:###:state-title repeat="many" -->
<!-- cpt:##:states -->

<!-- cpt:##:requirements -->
## E. Requirements

<!-- cpt:###:req-title repeat="many" -->
### Task Creation

<!-- cpt:id:req has="priority,task" to_code="true" -->
- [ ] `p1` - **ID**: `cpt-taskflow-spec-task-crud-req-create`

<!-- cpt:paragraph:req-body -->
Users can create tasks with title, description, priority, and due date. The system validates input and stores the task with BACKLOG status.
<!-- cpt:paragraph:req-body -->

**Implementation details**:
<!-- cpt:list:req-impl -->
- API: `POST /api/tasks` with JSON body `{title, description, priority, due_date}`
- DB: insert into `tasks` table (columns: title, description, priority, due_date, status)
- Domain: `Task` entity (id, title, description, priority, due_date, status)
<!-- cpt:list:req-impl -->

**Implements**:
<!-- cpt:id-ref:flow has="priority" -->
- `p1` - `cpt-taskflow-spec-task-crud-flow-create`
<!-- cpt:id-ref:flow -->

<!-- cpt:id-ref:algo has="priority" -->
- `p1` - `cpt-taskflow-spec-task-crud-algo-validate`
<!-- cpt:id-ref:algo -->

**Covers (PRD)**:
<!-- cpt:id-ref:fr -->
- `cpt-taskflow-fr-task-management`
<!-- cpt:id-ref:fr -->

<!-- cpt:id-ref:nfr -->
- `cpt-taskflow-nfr-performance`
<!-- cpt:id-ref:nfr -->

**Covers (DESIGN)**:
<!-- cpt:id-ref:principle -->
- `cpt-taskflow-principle-realtime-first`
<!-- cpt:id-ref:principle -->

<!-- cpt:id-ref:constraint -->
- `cpt-taskflow-constraint-supported-platforms`
<!-- cpt:id-ref:constraint -->

<!-- cpt:id-ref:component -->
- `cpt-taskflow-component-api-server`
- `cpt-taskflow-component-postgresql`
<!-- cpt:id-ref:component -->

<!-- cpt:id-ref:seq -->
- `cpt-taskflow-seq-task-creation`
<!-- cpt:id-ref:seq -->

<!-- cpt:id-ref:dbtable -->
- `cpt-taskflow-dbtable-tasks`
<!-- cpt:id-ref:dbtable -->
<!-- cpt:id:req -->
<!-- cpt:###:req-title repeat="many" -->
<!-- cpt:##:requirements -->

<!-- cpt:##:additional-context -->
## F. Additional Context (optional)

<!-- cpt:free:context-notes -->
The spec must keep task status transitions consistent with the Task Status state machine in Section D. All state changes should emit events for the notification system.
<!-- cpt:free:context-notes -->
<!-- cpt:##:additional-context -->

<!-- cpt:#:spec -->
