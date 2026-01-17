# Implementation Plan: Task CRUD Operations

**Feature**: `task-crud`  
**Version**: 1.0  
**Last Updated**: 2025-01-17  
**Status**: 🔄 IN_PROGRESS

**Feature DESIGN**: [DESIGN.md](DESIGN.md)

---

## Summary

**Total Changes**: 2  
**Completed**: 0  
**In Progress**: 1  
**Not Started**: 1

**Estimated Effort**: 8 story points

---

## Change 1: Task Repository and Models

**ID**: `fdd-task-api-feature-task-crud-change-repository`  
**Status**: 🔄 IN_PROGRESS  
**Priority**: HIGH  
**Effort**: 3 story points  
**Implements**: `fdd-task-api-feature-task-crud-req-create-endpoint`, `fdd-task-api-feature-task-crud-req-get-endpoint`  
**Phases**: `ph-1`

---

### Objective
Create data models and database repository layer for task CRUD operations.

### Requirements Coverage

**Implements**:
- **`fdd-task-api-feature-task-crud-req-create-endpoint`**: Task creation endpoint
- **`fdd-task-api-feature-task-crud-req-get-endpoint`**: Task retrieval endpoint

**References**:
- Flow: `fdd-task-api-feature-task-crud-flow-create-task` (Section B)
- Flow: `fdd-task-api-feature-task-crud-flow-get-task` (Section B)
- Algorithm: `fdd-task-api-feature-task-crud-algo-validate-input` (Section C)

### Tasks

## 1. Implementation

### 1.1 Create Task Model
- [ ] 1.1.1 Create `src/features/task_crud/models.rs` with Task struct
- [ ] 1.1.2 Add required FDD comment tags (with `:ph-1` postfix) at file header
- [ ] 1.1.3 Derive serde::Serialize and serde::Deserialize for Task
- [ ] 1.1.4 Add UUID, timestamps, and optional fields
- [ ] 1.1.5 Create CreateTaskRequest struct with validator derives
- [ ] 1.1.6 Create UpdateTaskRequest struct

### 1.2 Create Repository Layer
- [ ] 1.2.1 Create `src/features/task_crud/repository.rs` with TaskRepository trait
- [ ] 1.2.2 Add required FDD comment tags (with `:ph-1` postfix) at file header
- [ ] 1.2.3 Implement create_task(request) -> Result<Task, DbError> `inst-insert-task`
- [ ] 1.2.4 Implement get_task_by_id(id) -> Result<Option<Task>, DbError> `inst-query-task`
- [ ] 1.2.5 Implement update_task(id, request) -> Result<Task, DbError> `inst-save-changes`
- [ ] 1.2.6 Implement delete_task(id) -> Result<(), DbError> (soft delete)
- [ ] 1.2.7 Add SQLx query macros for type-safe SQL

### 1.3 Database Migrations
- [ ] 1.3.1 Create migration `001_create_tasks_table.sql`
- [ ] 1.3.2 Add required FDD comment tags (with `:ph-1` postfix) in migration header
- [ ] 1.3.3 Define tasks table schema with all columns
- [ ] 1.3.4 Add indexes for status, assignee_id, project_id
- [ ] 1.3.5 Test migration up/down

## 2. Testing

### 2.1 Repository Tests
- [ ] 2.1.1 Test create_task stores task in database `test-create-success`
- [ ] 2.1.2 Test get_task_by_id returns correct task `test-get-success`
- [ ] 2.1.3 Test get_task_by_id returns None for missing ID `test-get-not-found`
- [ ] 2.1.4 Test update_task modifies existing task `test-update-success`
- [ ] 2.1.5 Test delete_task sets deleted_at timestamp `test-soft-delete`

### Specification

**Domain Model Changes**:
- Type: `Task`
- Fields: id, title, description, status, assignee_id, due_date, created_at, updated_at, deleted_at
- Relationships: belongs_to Project (optional), belongs_to User as assignee (optional)

**API Changes**: None (internal layer)

**Database Changes**:
- Table: `tasks`
- Schema: See migration 001_create_tasks_table.sql
- Migrations: 001_create_tasks_table (up/down)

**Code Changes**:
- Module: `src/features/task_crud/`
- Files: models.rs, repository.rs
- Dependencies: sqlx, serde, validator, uuid, chrono

---

## Change 2: HTTP Handlers and Routes

**ID**: `fdd-task-api-feature-task-crud-change-handlers`  
**Status**: ⏳ NOT_STARTED  
**Priority**: HIGH  
**Effort**: 5 story points  
**Implements**: `fdd-task-api-feature-task-crud-req-create-endpoint`, `fdd-task-api-feature-task-crud-req-get-endpoint`  
**Phases**: `ph-1`

---

### Objective
Create HTTP handlers and register routes for task CRUD endpoints.

### Requirements Coverage

**Implements**:
- **`fdd-task-api-feature-task-crud-req-create-endpoint`**: POST /api/v1/tasks
- **`fdd-task-api-feature-task-crud-req-get-endpoint`**: GET /api/v1/tasks/{id}

**References**:
- Flow: `fdd-task-api-feature-task-crud-flow-create-task` (Section B)
- Flow: `fdd-task-api-feature-task-crud-flow-get-task` (Section B)
- Flow: `fdd-task-api-feature-task-crud-flow-update-task` (Section B)

### Tasks

## 1. Implementation

### 1.1 Create HTTP Handlers
- [ ] 1.1.1 Create `src/features/task_crud/handlers.rs` with handler functions
- [ ] 1.1.2 Add required FDD comment tags (with `:ph-1` postfix) at file header
- [ ] 1.1.3 Implement create_task_handler(Json<CreateTaskRequest>) -> Result<(StatusCode, Json<Task>), ApiError> `inst-receive-request`
- [ ] 1.1.4 Implement get_task_handler(Path<Uuid>) -> Result<Json<Task>, ApiError> `inst-receive-request`
- [ ] 1.1.5 Implement update_task_handler(Path<Uuid>, Json<UpdateTaskRequest>) -> Result<Json<Task>, ApiError>
- [ ] 1.1.6 Implement delete_task_handler(Path<Uuid>) -> Result<StatusCode, ApiError>

### 1.2 Input Validation
- [ ] 1.2.1 Create `src/features/task_crud/validation.rs` with validation logic
- [ ] 1.2.2 Add required FDD comment tags (with `:ph-1` postfix) at file header
- [ ] 1.2.3 Implement validate_create_request using validator crate `inst-validate-input`
- [ ] 1.2.4 Check title presence and length constraints `inst-check-title`
- [ ] 1.2.5 Return 400 with error details if validation fails `inst-handle-validation-error`

### 1.3 Register Routes
- [ ] 1.3.1 Create `src/features/task_crud/mod.rs` with public API
- [ ] 1.3.2 Add required FDD comment tags (with `:ph-1` postfix) at file header
- [ ] 1.3.3 Export task_crud_routes() function returning Router
- [ ] 1.3.4 Register POST /tasks -> create_task_handler
- [ ] 1.3.5 Register GET /tasks/:id -> get_task_handler
- [ ] 1.3.6 Register PUT /tasks/:id -> update_task_handler
- [ ] 1.3.7 Register DELETE /tasks/:id -> delete_task_handler

## 2. Testing

### 2.1 Handler Integration Tests
- [ ] 2.1.1 Test POST /api/v1/tasks returns 201 with valid input `test-create-success`
- [ ] 2.1.2 Test POST /api/v1/tasks returns 400 with missing title `test-create-missing-title`
- [ ] 2.1.3 Test GET /api/v1/tasks/{id} returns 200 for existing task `test-get-success`
- [ ] 2.1.4 Test GET /api/v1/tasks/{id} returns 404 for missing task `test-get-not-found`
- [ ] 2.1.5 Test PUT /api/v1/tasks/{id} returns 200 with updated task
- [ ] 2.1.6 Test DELETE /api/v1/tasks/{id} returns 204

### Specification

**Domain Model Changes**: None

**API Changes**:
- Endpoint: `POST /api/v1/tasks`
- Method: POST
- Request: JSON CreateTaskRequest
- Response: 201 Created with Task JSON

- Endpoint: `GET /api/v1/tasks/{id}`
- Method: GET
- Request: UUID path parameter
- Response: 200 OK with Task JSON or 404 Not Found

**Database Changes**: None

**Code Changes**:
- Module: `src/features/task_crud/`
- Files: handlers.rs, validation.rs, mod.rs (router registration)
- Dependencies: axum, tower-http

---

## Dependencies

### Blocks
None

### Blocked By
None

### Depends On
- Database connection pool setup
- Error handling middleware
- Authentication middleware (for protected endpoints)
