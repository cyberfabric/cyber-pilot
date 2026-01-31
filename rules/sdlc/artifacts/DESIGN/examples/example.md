# Technical Design: TaskFlow

## A. Architecture Overview

TaskFlow uses a layered architecture: React SPA frontend, Node.js REST API, PostgreSQL database. WebSocket connections enable real-time updates.

### Architecture drivers

#### Product requirements

| FDD ID | Solution short description |
|--------|----------------------------|
| `fdd-taskflow-fr-task-crud` | Use REST API with idempotent endpoints and PostgreSQL persistence. |
| `fdd-taskflow-fr-realtime-notifications` | Use WebSocket updates with Redis PubSub fan-out. |

#### Architecture Decisions Records

| FDD ADR ID | Summary |
|------------|---------|
| `fdd-taskflow-adr-postgres-storage` | Use PostgreSQL for durable task storage to support relational queries and strong consistency. |

## B. Principles & Constraints

### B.1: Design Principles

#### Real-time First

**ID**: `fdd-taskflow-principle-realtime-first`

<!-- fdd-id-content -->
**ADRs**: `fdd-taskflow-adr-postgres-storage`

Prefer architectures that keep task state and notifications consistent and observable for all users.
<!-- fdd-id-content -->

#### Simplicity over Features

**ID**: `fdd-taskflow-principle-simplicity-over-features`

<!-- fdd-id-content -->
**ADRs**: `fdd-taskflow-adr-postgres-storage`

Simplicity is preferred over features.
<!-- fdd-id-content -->

#### Mobile-first Responsive Design

**ID**: `fdd-taskflow-principle-mobile-first`

<!-- fdd-id-content -->
**ADRs**: `fdd-taskflow-adr-postgres-storage`

Design for mobile devices first.
<!-- fdd-id-content -->

### B.2: Constraints

#### Supported Platforms

**ID**: `fdd-taskflow-constraint-supported-platforms`

<!-- fdd-id-content -->
**ADRs**: `fdd-taskflow-adr-postgres-storage`

Must run on Node.js 18+. PostgreSQL 14+ required. Browser support: last 2 versions.
<!-- fdd-id-content -->

## C. Technical Architecture

### C.1: Domain Model

**Technology**: TypeScript
**Location**: [domain-model.ts](domain-model.ts)

- **Task**: id, title, description, status, priority, dueDate, assigneeId, createdBy
- **User**: id, email, name, role (MEMBER | LEAD)

### C.2: Component Model

```
[React SPA] <--REST/WS--> [API Server] <---> [PostgreSQL]
                              |
                         [Redis PubSub]
```

### C.3: API Contracts

**Technology**: REST/OpenAPI
**Location**: [openapi.yaml](openapi.yaml)

- `POST /api/tasks` - Create task
- `GET /api/tasks` - List tasks with filters
- `PATCH /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task

### C.4: Interactions & Sequences

```
Member -> API Server: POST /api/tasks
API Server -> PostgreSQL: INSERT task
API Server -> Redis PubSub: PUBLISH task.created
Redis PubSub -> API Server: FAN-OUT
API Server -> React SPA: WS task.created
```

Use cases: `fdd-taskflow-usecase-create-task`

Actors: `fdd-taskflow-actor-member`, `fdd-taskflow-actor-lead`

### C.5 Database schemas & tables (optional)

#### Table tasks

ID: `fdd-taskflow-db-table-tasks`

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Task ID (PK) |
| title | text | Task title |

### C.6: Topology (optional)

**ID**: `fdd-taskflow-topology-local-dev`

<!-- fdd-id-content -->
React SPA + API server + PostgreSQL + Redis on a single developer machine.
<!-- fdd-id-content -->

### C.7: Tech stack (optional)

**ID**: `fdd-taskflow-tech-node-postgres`

<!-- fdd-id-content -->
Node.js 18+, React, PostgreSQL 14+, Redis.
<!-- fdd-id-content -->

## D. Additional Context

**ID**: `fdd-taskflow-design-context-notes`

<!-- fdd-id-content -->
TaskFlow prioritizes real-time collaboration and predictable REST semantics.
<!-- fdd-id-content -->
