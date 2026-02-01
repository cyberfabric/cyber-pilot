<!-- fdd:#:design -->
# Technical Design: TaskFlow

<!-- fdd:##:architecture-overview -->
## A. Architecture Overview

<!-- fdd:###:architectural-vision -->
### Architectural Vision

<!-- fdd:architectural-vision-body -->
TaskFlow uses a layered architecture with clear separation of concerns: React SPA frontend, Node.js REST API, and PostgreSQL database. WebSocket connections enable real-time updates for collaborative task management.

The architecture prioritizes simplicity and developer productivity while supporting real-time collaboration. System boundaries are clearly defined between presentation, business logic, and data persistence layers.
<!-- fdd:architectural-vision-body -->
<!-- fdd:###:architectural-vision -->

<!-- fdd:###:architecture-drivers -->
### Architecture drivers

<!-- fdd:####:prd-requirements -->
#### Product requirements

<!-- fdd:fr-title repeat="many" -->
##### Task Management

<!-- fdd:id-ref:fr has="priority,task" -->
[ ] `p1` - `fdd-taskflow-fr-task-management`
<!-- fdd:id-ref:fr -->

**Solution**: REST API with idempotent endpoints and PostgreSQL persistence for task CRUD.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:fr-title repeat="many" -->
##### Notifications

<!-- fdd:id-ref:fr has="priority,task" -->
[ ] `p1` - `fdd-taskflow-fr-notifications`
<!-- fdd:id-ref:fr -->

**Solution**: WebSocket push with Redis PubSub for real-time notification delivery.
<!-- fdd:fr-title repeat="many" -->

<!-- fdd:nfr-title repeat="many" -->
##### Security

<!-- fdd:id-ref:nfr has="priority,task" -->
[ ] `p1` - `fdd-taskflow-nfr-security`
<!-- fdd:id-ref:nfr -->

**Solution**: JWT authentication with role-based authorization middleware.
<!-- fdd:nfr-title -->

<!-- fdd:nfr-title repeat="many" -->
##### Performance

<!-- fdd:id-ref:nfr has="priority,task" -->
[ ] `p2` - `fdd-taskflow-nfr-performance`
<!-- fdd:id-ref:nfr -->

**Solution**: Connection pooling and query optimization for sub-500ms responses.
<!-- fdd:nfr-title -->
<!-- fdd:####:prd-requirements -->

<!-- fdd:####:adr-records -->
#### Architecture Decisions Records

<!-- fdd:adr-title repeat="many" -->
##### PostgreSQL for Storage

<!-- fdd:id-ref:adr has="priority,task" -->
[ ] `p1` - `fdd-taskflow-adr-postgres-storage`
<!-- fdd:id-ref:adr -->

Use PostgreSQL for durable task storage. Chosen for strong ACID guarantees, relational query support, and team expertise. Trade-off: requires separate DB server vs embedded SQLite.
<!-- fdd:adr-title -->
<!-- fdd:####:adr-records -->
<!-- fdd:###:architecture-drivers -->

<!-- fdd:###:architecture-layers -->
### Architecture Layers

<!-- fdd:table:architecture-layers -->
| Layer | Responsibility | Technology |
|-------|---------------|------------|
| Presentation | User interface, state management | React, TypeScript |
| API | REST endpoints, WebSocket handling | Node.js, Express |
| Business Logic | Task operations, authorization | TypeScript |
| Data Access | Database queries, caching | PostgreSQL, Redis |
<!-- fdd:table:architecture-layers -->
<!-- fdd:###:architecture-layers -->
<!-- fdd:##:architecture-overview -->

<!-- fdd:##:principles-and-constraints -->
## B. Principles & Constraints

<!-- fdd:###:principles -->
### B.1: Design Principles

<!-- fdd:####:principle-title repeat="many" -->
#### Real-time First

<!-- fdd:id:principle has="priority,task" covered_by="FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-taskflow-principle-realtime-first`

<!-- fdd:paragraph:principle-body -->
Prefer architectures that keep task state and notifications consistent and observable for all users. Changes should propagate to all connected clients within 2 seconds.
<!-- fdd:paragraph:principle-body -->
<!-- fdd:id:principle -->
<!-- fdd:####:principle-title repeat="many" -->

<!-- fdd:####:principle-title repeat="many" -->
#### Simplicity over Features

<!-- fdd:id:principle has="priority,task" covered_by="FEATURES,FEATURE" -->
- [ ] `p2` - **ID**: `fdd-taskflow-principle-simplicity`

<!-- fdd:paragraph:principle-body -->
Choose simpler solutions over feature-rich ones. Avoid premature optimization and unnecessary abstractions. Code should be readable by junior developers.
<!-- fdd:paragraph:principle-body -->
<!-- fdd:id:principle -->
<!-- fdd:####:principle-title repeat="many" -->
<!-- fdd:###:principles -->

<!-- fdd:###:constraints -->
### B.2: Constraints

<!-- fdd:####:constraint-title repeat="many" -->
#### Supported Platforms

<!-- fdd:id:constraint has="priority,task" covered_by="FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-taskflow-constraint-platforms`

<!-- fdd:paragraph:constraint-body -->
Must run on Node.js 18+. PostgreSQL 14+ required for JSONB support. Browser support: last 2 versions of Chrome, Firefox, Safari, Edge.
<!-- fdd:paragraph:constraint-body -->
<!-- fdd:id:constraint -->
<!-- fdd:####:constraint-title repeat="many" -->
<!-- fdd:###:constraints -->
<!-- fdd:##:principles-and-constraints -->

<!-- fdd:##:technical-architecture -->
## C. Technical Architecture

<!-- fdd:###:domain-model -->
### C.1: Domain Model

<!-- fdd:paragraph:domain-model -->
Core entities: **Task** (id, title, description, status, priority, dueDate, assigneeId, createdBy, createdAt, updatedAt) and **User** (id, email, name, role). Task status follows state machine: TODO -> IN_PROGRESS -> DONE. Invariants: assignee must be team member, due date must be future.
<!-- fdd:paragraph:domain-model -->
<!-- fdd:###:domain-model -->

<!-- fdd:###:component-model -->
### C.2: Component Model

<!-- fdd:code:component-model -->
```mermaid
graph LR
    A[React SPA] -->|REST/WS| B[API Server]
    B --> C[PostgreSQL]
    B --> D[Redis PubSub]
    D --> B
```
<!-- fdd:code:component-model -->

<!-- fdd:####:component-title repeat="many" -->
#### API Server

<!-- fdd:id:component has="priority,task" covered_by="FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-taskflow-component-api-server`

<!-- fdd:list:component-payload -->
- Responsibilities: Handle HTTP requests, enforce authorization, coordinate business logic
- Boundaries: Exposes REST API and WebSocket endpoint, no direct database access from handlers
- Dependencies: Express, pg-pool, ioredis
- Key interfaces: TaskController, AuthMiddleware, WebSocketManager
<!-- fdd:list:component-payload -->
<!-- fdd:id:component -->
<!-- fdd:####:component-title repeat="many" -->
<!-- fdd:###:component-model -->

<!-- fdd:###:api-contracts -->
### C.3: API Contracts

<!-- fdd:paragraph:api-contracts -->
REST API at `/api/v1/` with JSON request/response. Authentication via Bearer JWT token. Standard endpoints: `POST /tasks`, `GET /tasks`, `PATCH /tasks/:id`, `DELETE /tasks/:id`. WebSocket at `/ws` for real-time events: `task.created`, `task.updated`, `task.deleted`.
<!-- fdd:paragraph:api-contracts -->
<!-- fdd:###:api-contracts -->

<!-- fdd:###:interactions -->
### C.4: Interactions & Sequences

<!-- fdd:####:sequence-title repeat="many" -->
#### Create Task Flow

<!-- fdd:id:seq has="priority,task" covered_by="FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-taskflow-seq-create-task`

<!-- fdd:code:sequences -->
```mermaid
sequenceDiagram
    Member->>API: POST /tasks
    API->>PostgreSQL: INSERT task
    API->>Redis: PUBLISH task.created
    Redis-->>API: FAN-OUT
    API-->>Member: WS task.created
```
<!-- fdd:code:sequences -->

<!-- fdd:paragraph:sequence-body -->
Lead or member creates task via REST API. Server validates input, inserts into database, then publishes event to Redis for real-time distribution. All connected clients receive WebSocket notification within 2 seconds.
<!-- fdd:paragraph:sequence-body -->
<!-- fdd:id:seq -->
<!-- fdd:####:sequence-title repeat="many" -->
<!-- fdd:###:interactions -->

<!-- fdd:###:database -->
### C.5 Database schemas & tables (optional)

<!-- fdd:####:db-table-title repeat="many" -->
#### Table tasks

<!-- fdd:id:dbtable has="priority,task" covered_by="FEATURES,FEATURE" -->
- [ ] `p1` - **ID**: `fdd-taskflow-dbtable-tasks`

Schema
<!-- fdd:table:db-table-schema -->
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Task ID (PK) |
| title | text | Task title (required) |
| description | text | Task description |
| status | enum | TODO, IN_PROGRESS, DONE |
| assignee_id | uuid | FK to users.id |
<!-- fdd:table:db-table-schema -->

PK: `id`

Constraints: `status IN ('TODO', 'IN_PROGRESS', 'DONE')`, `assignee_id REFERENCES users(id)`

Example
<!-- fdd:table:db-table-example -->
| id | title | status |
|----|-------|--------|
| 550e8400... | Implement login | IN_PROGRESS |
<!-- fdd:table:db-table-example -->
<!-- fdd:id:dbtable -->
<!-- fdd:####:db-table-title repeat="many" -->
<!-- fdd:###:database -->

<!-- fdd:###:topology -->
### C.6: Topology (optional)

<!-- fdd:id:topology has="task" -->
- [ ] **ID**: `fdd-taskflow-topology-local`

<!-- fdd:free:topology-body -->
Local development: React SPA (port 3000) + API server (port 4000) + PostgreSQL (port 5432) + Redis (port 6379) on single machine. Production: Kubernetes deployment with horizontal scaling of API pods.
<!-- fdd:free:topology-body -->
<!-- fdd:id:topology -->
<!-- fdd:###:topology -->

<!-- fdd:###:tech-stack -->
### C.7: Tech stack (optional)

<!-- fdd:paragraph:status -->
**Status**: Accepted
<!-- fdd:paragraph:status -->

<!-- fdd:paragraph:tech-body -->
Backend: Node.js 18 LTS, TypeScript 5.x, Express 4.x, pg-pool for PostgreSQL, ioredis for Redis. Frontend: React 18, TypeScript, Vite build tool. Testing: Jest, React Testing Library. Rationale: Team familiarity, mature ecosystem, strong TypeScript support.
<!-- fdd:paragraph:tech-body -->
<!-- fdd:###:tech-stack -->
<!-- fdd:##:technical-architecture -->

<!-- fdd:##:design-context -->
## D. Additional Context

<!-- fdd:free:design-context-body -->
TaskFlow prioritizes real-time collaboration and predictable REST semantics. Future considerations include mobile app support and Slack integration. Trade-offs accepted: PostgreSQL requires operational overhead vs SQLite simplicity.
<!-- fdd:free:design-context-body -->

<!-- fdd:paragraph:date -->
**Date**: 2025-01-15
<!-- fdd:paragraph:date -->
<!-- fdd:##:design-context -->

<!-- fdd:#:design -->
