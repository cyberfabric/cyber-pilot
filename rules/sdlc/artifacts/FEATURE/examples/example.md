# Feature: Task CRUD

## A. Feature Context

**ID**: `fdd-taskflow-feature-task-crud`
**Status**: IN_PROGRESS

### 1. Overview
Core task management functionality for creating, viewing, updating, and deleting tasks.

### 2. Purpose

Enable team members to manage their work items with full lifecycle tracking.

### 3. Actors

<List the actors involved in this feature by backticked `fdd-*-actor-*` IDs.>

- `fdd-taskflow-actor-member`
- `fdd-taskflow-actor-lead`

### 4. References

- Overall Design: [DESIGN](../../DESIGN.md)

## B. Actor Flows (FDL)
### Create Task

- [ ] **ID**: `fdd-taskflow-feature-task-crud-flow-create`

<!-- fdd-id-content -->
1. [x] - `ph-1` - User fills task form (title, description, priority) - `inst-fill-form`
2. [x] - `ph-1` - API: POST /api/tasks (body: title, description, priority, due_date) - `inst-api-create`
3. [x] - `ph-1` - Algorithm: validate task input using `fdd-taskflow-feature-task-crud-algo-validate` - `inst-run-validate`
4. [x] - `ph-1` - DB: INSERT tasks(title, description, priority, due_date, status=BACKLOG) - `inst-db-insert`
5. [ ] - `ph-2` - User optionally assigns task to team member - `inst-assign`
6. [ ] - `ph-2` - API: POST /api/tasks/{task_id}/assignees (body: assignee_id) - `inst-api-assign`
7. [ ] - `ph-2` - DB: INSERT task_assignees(task_id, assignee_id) - `inst-db-assign-insert`
8. [x] - `ph-1` - API: RETURN 201 Created (task_id, status=BACKLOG) - `inst-return-created`
<!-- fdd-id-content -->

## C. Algorithms (FDL)
### Validate Task

- [x] **ID**: `fdd-taskflow-feature-task-crud-algo-validate`

<!-- fdd-id-content -->
1. [x] - `ph-1` - **IF** title is empty **RETURN** error "Title required" - `inst-check-title`
2. [x] - `ph-1` - **IF** priority not in [LOW, MEDIUM, HIGH] **RETURN** error - `inst-check-priority`
3. [x] - `ph-1` - **IF** due_date is present AND due_date is in the past **RETURN** error - `inst-check-due-date`
4. [x] - `ph-1` - DB: SELECT tasks WHERE title=? AND status!=DONE (dedupe check) - `inst-db-dedupe-check`
5. [x] - `ph-1` - **IF** duplicate exists **RETURN** error - `inst-return-duplicate`
6. [x] - `ph-1` - **RETURN** valid - `inst-return-valid`
<!-- fdd-id-content -->

## D. States (FDL)
### Task Status

- [ ] **ID**: `fdd-taskflow-feature-task-crud-state-status`

<!-- fdd-id-content -->
1. [x] - `ph-1` - **FROM** BACKLOG **TO** IN_PROGRESS **WHEN** user starts work - `inst-start`
2. [ ] - `ph-2` - **FROM** IN_PROGRESS **TO** DONE **WHEN** user completes - `inst-complete`
3. [ ] - `ph-2` - **FROM** DONE **TO** BACKLOG **WHEN** user reopens - `inst-reopen`
<!-- fdd-id-content -->

## E. Requirements
### Task Creation

- [ ] **ID**: `fdd-taskflow-feature-task-crud-req-create`

<!-- fdd-id-content -->
**Status**: 🔄 IN_PROGRESS

**Description**: Users can create tasks with title, description, priority, and due date.

**Implementation details**:

- API: `POST /api/tasks` with JSON body `{title, description, priority, due_date}`
- DB: insert into `tasks` table (columns: title, description, priority, due_date, status)
- Domain entities: `Task` (id, title)

**References**:

- [Create Task](#create-task)

**Implements**:

- `fdd-taskflow-feature-task-crud-flow-create`
- `fdd-taskflow-feature-task-crud-algo-validate`

**Phases**:

- [x] `ph-1`: basic creation
- [ ] `ph-2`: assignment support
<!-- fdd-id-content -->

## F. Additional Context

### Notes

**ID**: `fdd-taskflow-feature-task-crud-context-notes`

<!-- fdd-id-content -->
The feature must keep task status transitions consistent with the Task Status state machine in Section D.
<!-- fdd-id-content -->
