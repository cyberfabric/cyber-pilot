# Feature Design: Task CRUD Operations

**Feature**: `task-crud`  
**Version**: 1.0  
**Last Updated**: 2025-01-17  
**Status**: 🔄 IN_PROGRESS

**Overall Design**: [../../DESIGN.md](../../DESIGN.md)

---

## A. FEATURE CONTEXT

### 1. Overview
Implements REST API endpoints for creating, reading, updating, and deleting tasks.

### 2. Purpose
Enable developers to manage tasks programmatically via HTTP requests.

### 3. Actors
- **Developer**: `fdd-task-api-actor-developer` (from BUSINESS.md)
- **API Gateway**: `fdd-task-api-actor-api-gateway`
- **Database**: `fdd-task-api-actor-database`

### 4. References
- **Overall Design**: [DESIGN.md](../../DESIGN.md)
- **Business Context**: [BUSINESS.md](../../BUSINESS.md)

---

## B. ACTOR FLOWS (FDL)

### Flow: Create Task
**ID**: `fdd-task-api-feature-task-crud-flow-create-task`  
**Actor**: Developer  
**Trigger**: POST /api/v1/tasks

**Steps**:
- [ ] `ph-1` Receive HTTP POST request with task data `inst-receive-request`
- [ ] `ph-1` Validate request body against CreateTaskRequest schema `inst-validate-input`
- [ ] `ph-1` IF validation fails THEN return 400 Bad Request `inst-handle-validation-error`
- [ ] `ph-1` Generate UUID for new task `inst-generate-id`
- [ ] `ph-1` Set created_at and updated_at timestamps `inst-set-timestamps`
- [ ] `ph-1` Insert task into database `inst-insert-task`
- [ ] `ph-1` IF database error THEN return 500 Internal Server Error `inst-handle-db-error`
- [ ] `ph-1` Return 201 Created with task JSON `inst-return-success`

### Flow: Get Task by ID
**ID**: `fdd-task-api-feature-task-crud-flow-get-task`  
**Actor**: Developer  
**Trigger**: GET /api/v1/tasks/{id}

**Steps**:
- [ ] `ph-1` Receive HTTP GET request with task ID `inst-receive-request`
- [ ] `ph-1` Validate UUID format `inst-validate-uuid`
- [ ] `ph-1` IF invalid UUID THEN return 400 Bad Request `inst-handle-invalid-uuid`
- [ ] `ph-1` Query database for task WHERE id = {id} AND deleted_at IS NULL `inst-query-task`
- [ ] `ph-1` IF task not found THEN return 404 Not Found `inst-handle-not-found`
- [ ] `ph-1` Return 200 OK with task JSON `inst-return-task`

### Flow: Update Task
**ID**: `fdd-task-api-feature-task-crud-flow-update-task`  
**Actor**: Developer  
**Trigger**: PUT /api/v1/tasks/{id}

**Steps**:
- [ ] `ph-1` Receive HTTP PUT request with task ID and update data `inst-receive-request`
- [ ] `ph-1` Validate UUID and request body `inst-validate-input`
- [ ] `ph-1` Query database to check task exists `inst-check-exists`
- [ ] `ph-1` IF task not found THEN return 404 Not Found `inst-handle-not-found`
- [ ] `ph-1` Update task fields `inst-update-fields`
- [ ] `ph-1` Set updated_at to current timestamp `inst-set-updated-at`
- [ ] `ph-1` Save changes to database `inst-save-changes`
- [ ] `ph-1` Return 200 OK with updated task JSON `inst-return-updated`

---

## C. ALGORITHMS (FDL)

### Algorithm: Validate Task Input
**ID**: `fdd-task-api-feature-task-crud-algo-validate-input`  
**Purpose**: Validate task creation/update data

**Steps**:
- [ ] `ph-1` Check title is present and non-empty `inst-check-title`
- [ ] `ph-1` Check title length ≤ 255 characters `inst-check-title-length`
- [ ] `ph-1` IF description provided THEN check length ≤ 10000 characters `inst-check-description`
- [ ] `ph-1` IF status provided THEN check status IN (TODO, IN_PROGRESS, DONE) `inst-check-status`
- [ ] `ph-1` IF due_date provided THEN check valid ISO 8601 format `inst-check-due-date`
- [ ] `ph-1` Return validation result with list of errors `inst-return-result`

---

## D. STATES (FDL)

### State Machine: Task Lifecycle
**ID**: `fdd-task-api-feature-task-crud-state-task-lifecycle`  
**Entity**: Task

**States**:

#### TODO
**Initial State**: Yes  
**Description**: Task created but not started

**Transitions**:
- WHEN status updated to IN_PROGRESS THEN transition to IN_PROGRESS `trans-start-task`
- WHEN task deleted THEN transition to DELETED `trans-delete-from-todo`

#### IN_PROGRESS
**Description**: Task actively being worked on

**Transitions**:
- WHEN status updated to DONE THEN transition to DONE `trans-complete-task`
- WHEN status updated to TODO THEN transition to TODO `trans-reopen-task`
- WHEN task deleted THEN transition to DELETED `trans-delete-from-progress`

#### DONE
**Description**: Task completed

**Transitions**:
- WHEN status updated to TODO THEN transition to TODO `trans-reopen-completed`
- WHEN task deleted THEN transition to DELETED `trans-delete-from-done`

#### DELETED
**Final State**: Yes  
**Description**: Task soft-deleted (deleted_at IS NOT NULL)

---

## E. TECHNICAL DETAILS

### Implementation Notes
- Use Axum router with typed extractors
- Use SQLx for async database queries
- Use serde for JSON serialization
- Use validator crate for input validation

### Dependencies
- axum = "0.6"
- sqlx = { version = "0.7", features = ["postgres", "uuid", "chrono"] }
- serde = { version = "1.0", features = ["derive"] }
- validator = { version = "0.16", features = ["derive"] }
- uuid = { version = "1.0", features = ["serde", "v4"] }
- chrono = { version = "0.4", features = ["serde"] }

### Module Structure
```
src/
  features/
    task_crud/
      mod.rs          # Public module interface
      handlers.rs     # HTTP handlers
      models.rs       # Task struct, CreateTaskRequest, etc.
      repository.rs   # Database queries
      validation.rs   # Input validation
```

---

## F. REQUIREMENTS

### Feature Requirements

#### FR-TASK-001: Create Task Endpoint
**ID**: `fdd-task-api-feature-task-crud-req-create-endpoint`  
**Priority**: CRITICAL  
**Implements**: `fdd-task-api-req-task-crud` (from Overall Design)

POST /api/v1/tasks accepts JSON and returns created task with 201 status.

**Acceptance Criteria**:
- Accepts title (required), description (optional), assignee_id (optional)
- Generates UUID and timestamps automatically
- Returns 400 if title missing or too long
- Returns 201 with task JSON if successful

#### FR-TASK-002: Get Task Endpoint
**ID**: `fdd-task-api-feature-task-crud-req-get-endpoint`  
**Priority**: CRITICAL  
**Implements**: `fdd-task-api-req-task-crud`

GET /api/v1/tasks/{id} returns task or 404.

**Acceptance Criteria**:
- Returns 400 if ID is invalid UUID
- Returns 404 if task not found or deleted
- Returns 200 with task JSON if found

---

## G. ADDITIONAL CONTEXT

### Testing Scenarios

#### TS-001: Create Task Success
**ID**: `fdd-task-api-feature-task-crud-test-create-success`  
**Type**: Integration Test

**Given**: Valid CreateTaskRequest with title "Write docs"  
**When**: POST /api/v1/tasks  
**Then**: Returns 201, response contains id and timestamps

#### TS-002: Create Task Missing Title
**ID**: `fdd-task-api-feature-task-crud-test-create-missing-title`  
**Type**: Integration Test

**Given**: CreateTaskRequest with empty title  
**When**: POST /api/v1/tasks  
**Then**: Returns 400 with validation error "title is required"

#### TS-003: Get Non-existent Task
**ID**: `fdd-task-api-feature-task-crud-test-get-not-found`  
**Type**: Integration Test

**Given**: Random UUID not in database  
**When**: GET /api/v1/tasks/{id}  
**Then**: Returns 404 with error "Task not found"
