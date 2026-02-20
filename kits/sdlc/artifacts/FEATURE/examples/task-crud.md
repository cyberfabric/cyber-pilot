
# Feature: Task CRUD


- [ ] `p1` - **ID**: `cpt-ex-task-flow-featstatus-task-crud`


- [ ] `p2` - `cpt-ex-task-flow-feature-task-crud`



## Feature Context


### 1. Overview
Core task management functionality for creating, viewing, updating, and deleting tasks. This feature provides the foundation for team collaboration by enabling users to track work items through their lifecycle.

Problem: Teams need a central place to track tasks with status, priority, and assignments.
Primary value: Enables organized task tracking with clear ownership.
Key assumptions: Users have accounts and belong to at least one team.



### 2. Purpose
Enable team members to manage their work items with full lifecycle tracking from creation through completion.

Success criteria: Users can create, view, update, and delete tasks within 500ms response time.


### 3. Actors

- `cpt-ex-task-flow-actor-member`
- `cpt-ex-task-flow-actor-lead`


### 4. References

- Overall Design: [DESIGN.md](../../DESIGN.md)
- ADRs: `cpt-ex-task-flow-adr-postgres-storage`
- Related feature: [Notifications](../notifications.md)




## Actor Flows


### Create Task


- [ ] `p1` - **ID**: `cpt-ex-task-flow-flow-create-task`

**Actors**:

- `cpt-ex-task-flow-actor-member`
- `cpt-ex-task-flow-actor-lead`



1. [x] - `p1` - User fills task form (title, description, priority) - `inst-fill-form`
2. [x] - `p1` - API: POST /api/tasks (body: title, description, priority, due_date) - `inst-api-create`
3. [x] - `p1` - Algorithm: validate task input using `cpt-ex-task-flow-algo-validate-task` - `inst-run-validate`
4. [x] - `p1` - DB: INSERT tasks(title, description, priority, due_date, status=BACKLOG) - `inst-db-insert`
5. [ ] - `p2` - User optionally assigns task to team member - `inst-assign`
6. [ ] - `p2` - API: POST /api/tasks/{task_id}/assignees (body: assignee_id) - `inst-api-assign`
7. [ ] - `p2` - DB: INSERT task_assignees(task_id, assignee_id) - `inst-db-assign-insert`
8. [x] - `p1` - API: RETURN 201 Created (task_id, status=BACKLOG) - `inst-return-created`






## Processes / Business Logic


### Validate Task


- [ ] `p1` - **ID**: `cpt-ex-task-flow-algo-validate-task`


1. [x] - `p1` - **IF** title is empty **RETURN** error "Title required" - `inst-check-title`
2. [x] - `p1` - **IF** priority not in [LOW, MEDIUM, HIGH] **RETURN** error - `inst-check-priority`
3. [x] - `p1` - **IF** due_date is present AND due_date is in the past **RETURN** error - `inst-check-due-date`
4. [x] - `p1` - DB: SELECT tasks WHERE title=? AND status!=DONE (dedupe check) - `inst-db-dedupe-check`
5. [ ] - `p2` - **IF** duplicate exists **RETURN** error - `inst-return-duplicate`
6. [x] - `p1` - **RETURN** valid - `inst-return-valid`






## States


### Task Status


- [ ] `p1` - **ID**: `cpt-ex-task-flow-state-task-status`


1. [x] - `p1` - **FROM** BACKLOG **TO** IN_PROGRESS **WHEN** user starts work - `inst-start`
2. [ ] - `p2` - **FROM** IN_PROGRESS **TO** DONE **WHEN** user completes - `inst-complete`
3. [ ] - `p2` - **FROM** DONE **TO** BACKLOG **WHEN** user reopens - `inst-reopen`






## Definitions of Done


### Task Creation


- [ ] `p1` - **ID**: `cpt-ex-task-flow-dod-task-create`


Users can create tasks with title, description, priority, and due date. The system validates input and stores the task with BACKLOG status.


**Implementation details**:

- API: `POST /api/tasks` with JSON body `{title, description, priority, due_date}`
- DB: insert into `tasks` table (columns: title, description, priority, due_date, status)
- Domain: `Task` entity (id, title, description, priority, due_date, status)


**Implements**:

- `cpt-ex-task-flow-flow-create-task`



- `cpt-ex-task-flow-algo-validate-task`


**Covers (PRD)**:

- `cpt-ex-task-flow-fr-task-management`



- `cpt-ex-task-flow-nfr-performance`


**Covers (DESIGN)**:

- `cpt-ex-task-flow-principle-realtime-first`



- `cpt-ex-task-flow-constraint-supported-platforms`



- `cpt-ex-task-flow-component-api-server`
- `cpt-ex-task-flow-component-postgresql`



- `cpt-ex-task-flow-seq-task-creation`



- `cpt-ex-task-flow-dbtable-tasks`






## Acceptance Criteria

- [ ] The feature supports task creation and assignment flow end-to-end
- [ ] Validation rules reject invalid titles, priorities, and past due dates
- [ ] State transitions follow the Task Status state machine


## Additional Context (optional)


The feature must keep task status transitions consistent with the Task Status state machine in Section D. All state changes should emit events for the notification system.




