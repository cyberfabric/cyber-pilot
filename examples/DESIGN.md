# Technical Design: Task Management API

**Project**: task-api  
**Version**: 1.0  
**Last Updated**: 2025-01-17

**Business Context**: [BUSINESS.md](BUSINESS.md)

---

## A. ARCHITECTURE OVERVIEW

### Architectural Style
RESTful API with WebSocket support for real-time features

### Key Components
1. **API Server** (Rust + Axum): HTTP request handling, business logic
2. **Database** (PostgreSQL): Task/project/user persistence
3. **Cache Layer** (Redis): Session storage, pub/sub for WebSocket
4. **API Gateway** (Nginx): Load balancing, rate limiting, TLS termination

### Technology Stack
- **Language**: Rust 1.70+
- **Web Framework**: Axum 0.6
- **Database**: PostgreSQL 15
- **ORM**: SQLx (async)
- **Cache**: Redis 7.0
- **Authentication**: JWT (jsonwebtoken crate)

### Deployment Architecture
```
[Client] → [Nginx] → [Axum Server 1-N] → [PostgreSQL]
                                       ↓
                                    [Redis]
```

---

## B. REQUIREMENTS & PRINCIPLES

### Functional Requirements

#### FR-001: Task CRUD Operations
**ID**: `fdd-task-api-req-task-crud`  
**Priority**: CRITICAL  
**Actors**: `fdd-task-api-actor-developer`

Create, read, update, delete tasks via REST endpoints.

**Acceptance Criteria**:
- POST /api/v1/tasks creates task, returns 201
- GET /api/v1/tasks/{id} returns task or 404
- PUT /api/v1/tasks/{id} updates task, returns 200
- DELETE /api/v1/tasks/{id} soft-deletes task, returns 204

#### FR-002: Real-time Task Updates
**ID**: `fdd-task-api-req-realtime-updates`  
**Priority**: HIGH  
**Actors**: `fdd-task-api-actor-developer`, `fdd-task-api-actor-notification-service`

WebSocket endpoint broadcasts task changes to subscribed clients.

**Acceptance Criteria**:
- WebSocket at /api/v1/ws
- Clients receive updates within 100ms
- Supports 10,000 concurrent connections
- Graceful reconnection with message replay

#### FR-003: Project Management
**ID**: `fdd-task-api-req-project-management`  
**Priority**: HIGH  
**Actors**: `fdd-task-api-actor-team-lead`

Create projects, add tasks, track progress.

**Acceptance Criteria**:
- POST /api/v1/projects creates project
- GET /api/v1/projects/{id}/tasks lists project tasks
- Progress calculated as (completed tasks / total tasks)

### Design Principles

#### API-First Design
**ID**: `fdd-task-api-principle-api-first`

Design OpenAPI spec before implementation, generate client SDKs.

#### Fail-Fast Validation
**ID**: `fdd-task-api-principle-fail-fast`

Validate all inputs at API boundary, return 400 with detailed errors.

### Non-Functional Requirements

#### NFR-001: Performance
**ID**: `fdd-task-api-nfr-performance`  
**Metric**: p95 latency <200ms for all endpoints

**Implementation**: Connection pooling, query optimization, Redis caching

#### NFR-002: Availability
**ID**: `fdd-task-api-nfr-availability`  
**Metric**: 99.9% uptime (max 43 minutes downtime/month)

**Implementation**: Health checks, graceful shutdown, circuit breakers

### Constraints

#### CONSTRAINT-001: PostgreSQL Required
**ID**: `fdd-task-api-constraint-postgres`

Must use PostgreSQL 15+ for ACID guarantees and JSON support.

---

## C. TECHNICAL ARCHITECTURE

### API Endpoints

**Tasks**:
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks/{id}` - Get task by ID
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `GET /api/v1/tasks?status={status}` - List tasks by status

**Projects**:
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project
- `GET /api/v1/projects/{id}/tasks` - List project tasks

**WebSocket**:
- `WS /api/v1/ws` - Real-time updates

### Data Models

**Task**:
```rust
struct Task {
    id: Uuid,
    title: String,
    description: Option<String>,
    status: TaskStatus, // TODO | IN_PROGRESS | DONE
    assignee_id: Option<Uuid>,
    project_id: Option<Uuid>,
    due_date: Option<DateTime<Utc>>,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}
```

**Project**:
```rust
struct Project {
    id: Uuid,
    name: String,
    description: Option<String>,
    owner_id: Uuid,
    created_at: DateTime<Utc>,
}
```

### Database Schema

**tasks** table:
- `id` UUID PRIMARY KEY
- `title` VARCHAR(255) NOT NULL
- `description` TEXT
- `status` VARCHAR(20) NOT NULL
- `assignee_id` UUID REFERENCES users(id)
- `project_id` UUID REFERENCES projects(id)
- `due_date` TIMESTAMP
- `created_at` TIMESTAMP NOT NULL
- `updated_at` TIMESTAMP NOT NULL
- `deleted_at` TIMESTAMP (soft delete)

**Indexes**:
- `idx_tasks_status` on (status) WHERE deleted_at IS NULL
- `idx_tasks_assignee` on (assignee_id)
- `idx_tasks_project` on (project_id)

### Error Handling

All errors return JSON:
```json
{
  "error": "TASK_NOT_FOUND",
  "message": "Task with ID abc-123 not found",
  "details": {}
}
```

**Status Codes**:
- 400: Bad Request (validation errors)
- 401: Unauthorized (invalid/missing token)
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

---

## D. ADDITIONAL CONTEXT

### Architecture Decisions
See [ADR.md](ADR.md) for detailed decisions on:
- ADR-0001: Use Axum web framework
- ADR-0002: JWT for authentication
- ADR-0003: Soft delete for tasks

### Security Considerations
- All endpoints require JWT authentication
- Rate limiting: 1000 req/hour per API key
- Input validation using serde + validator
- SQL injection prevention via SQLx prepared statements

### Monitoring & Observability
- Prometheus metrics at /metrics
- Structured logging with tracing crate
- Health check at /health
