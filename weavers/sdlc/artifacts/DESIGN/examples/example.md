<!-- spd:#:design -->
# Technical Design: TaskFlow

<!-- spd:##:architecture-overview -->
## 1. Architecture Overview

<!-- spd:###:architectural-vision -->
### Architectural Vision

<!-- spd:architectural-vision-body -->
TaskFlow uses a layered architecture with clear separation of concerns: React SPA frontend, Node.js REST API, and PostgreSQL database. WebSocket connections enable real-time updates for collaborative task management.

The architecture prioritizes simplicity and developer productivity while supporting real-time collaboration. System boundaries are clearly defined between presentation, business logic, and data persistence layers.
<!-- spd:architectural-vision-body -->
<!-- spd:###:architectural-vision -->

<!-- spd:###:architecture-drivers -->
### Architecture drivers

<!-- spd:####:prd-requirements -->
#### Product requirements

<!-- spd:fr-title repeat="many" -->
##### Task Management

<!-- spd:id-ref:fr has="priority,task" -->
- [ ] `p1` - `spd-taskflow-fr-task-management`
<!-- spd:id-ref:fr -->

**Solution**: REST API with idempotent endpoints and PostgreSQL persistence for task CRUD.
<!-- spd:fr-title repeat="many" -->

<!-- spd:fr-title repeat="many" -->
##### Notifications

<!-- spd:id-ref:fr has="priority,task" -->
- [ ] `p1` - `spd-taskflow-fr-notifications`
<!-- spd:id-ref:fr -->

**Solution**: WebSocket push with Redis PubSub for real-time notification delivery.
<!-- spd:fr-title repeat="many" -->

<!-- spd:nfr-title repeat="many" -->
##### Security

<!-- spd:id-ref:nfr has="priority,task" -->
- [ ] `p1` - `spd-taskflow-nfr-security`
<!-- spd:id-ref:nfr -->

**Solution**: JWT authentication with role-based authorization middleware.
<!-- spd:nfr-title -->

<!-- spd:nfr-title repeat="many" -->
##### Performance

<!-- spd:id-ref:nfr has="priority,task" -->
- [ ] `p2` - `spd-taskflow-nfr-performance`
<!-- spd:id-ref:nfr -->

**Solution**: Connection pooling and query optimization for sub-500ms responses.
<!-- spd:nfr-title -->
<!-- spd:####:prd-requirements -->

<!-- spd:####:adr-records -->
#### Architecture Decisions Records

<!-- spd:adr-title repeat="many" -->
##### PostgreSQL for Storage

<!-- spd:id-ref:adr has="priority,task" -->
- [ ] `p1` - `spd-taskflow-adr-postgres-storage`
<!-- spd:id-ref:adr -->

Use PostgreSQL for durable task storage. Chosen for strong ACID guarantees, relational query support, and team expertise. Trade-off: requires separate DB server vs embedded SQLite.
<!-- spd:adr-title -->
<!-- spd:####:adr-records -->
<!-- spd:###:architecture-drivers -->

<!-- spd:###:architecture-layers -->
### Architecture Layers

<!-- spd:table:architecture-layers -->
| Layer | Responsibility | Technology |
|-------|---------------|------------|
| Presentation | User interface, state management | React, TypeScript |
| API | REST endpoints, WebSocket handling | Node.js, Express |
| Business Logic | Task operations, authorization | TypeScript |
| Data Access | Database queries, caching | PostgreSQL, Redis |
<!-- spd:table:architecture-layers -->
<!-- spd:###:architecture-layers -->
<!-- spd:##:architecture-overview -->

<!-- spd:##:principles-and-constraints -->
## 2. Principles & Constraints

<!-- spd:###:principles -->
### 2.1: Design Principles

<!-- spd:####:principle-title repeat="many" -->
#### Real-time First

<!-- spd:id:principle has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `spd-taskflow-principle-realtime-first`

<!-- spd:paragraph:principle-body -->
Prefer architectures that keep task state and notifications consistent and observable for all users. Changes should propagate to all connected clients within 2 seconds.
<!-- spd:paragraph:principle-body -->
<!-- spd:id:principle -->
<!-- spd:####:principle-title repeat="many" -->

<!-- spd:####:principle-title repeat="many" -->
#### Simplicity over Specs

<!-- spd:id:principle has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p2` - **ID**: `spd-taskflow-principle-simplicity`

<!-- spd:paragraph:principle-body -->
Choose simpler solutions over spec-rich ones. Avoid premature optimization and unnecessary abstractions. Code should be readable by junior developers.
<!-- spd:paragraph:principle-body -->
<!-- spd:id:principle -->
<!-- spd:####:principle-title repeat="many" -->
<!-- spd:###:principles -->

<!-- spd:###:constraints -->
### 2.2: Constraints

<!-- spd:####:constraint-title repeat="many" -->
#### Supported Platforms

<!-- spd:id:constraint has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `spd-taskflow-constraint-platforms`

<!-- spd:paragraph:constraint-body -->
Must run on Node.js 18+. PostgreSQL 14+ required for JSONB support. Browser support: last 2 versions of Chrome, Firefox, Safari, Edge.
<!-- spd:paragraph:constraint-body -->
<!-- spd:id:constraint -->
<!-- spd:####:constraint-title repeat="many" -->
<!-- spd:###:constraints -->
<!-- spd:##:principles-and-constraints -->

<!-- spd:##:technical-architecture -->
## 3. Technical Architecture

<!-- spd:###:domain-model -->
### 3.1: Domain Model

<!-- spd:paragraph:domain-model -->
Core entities: **Task** (id, title, description, status, priority, dueDate, assigneeId, createdBy, createdAt, updatedAt) and **User** (id, email, name, role). Task status follows state machine: TODO -> IN_PROGRESS -> DONE. Invariants: assignee must be team member, due date must be future.
<!-- spd:paragraph:domain-model -->
<!-- spd:###:domain-model -->

<!-- spd:###:component-model -->
### 3.2: Component Model

<!-- spd:code:component-model -->
```mermaid
graph LR
    A[React SPA] -->|REST/WS| B[API Server]
    B --> C[PostgreSQL]
    B --> D[Redis PubSub]
    D --> B
```
<!-- spd:code:component-model -->

<!-- spd:####:component-title repeat="many" -->
#### API Server

<!-- spd:id:component has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `spd-taskflow-component-api-server`

<!-- spd:list:component-payload -->
- Responsibilities: Handle HTTP requests, enforce authorization, coordinate business logic
- Boundaries: Exposes REST API and WebSocket endpoint, no direct database access from handlers
- Dependencies: Express, pg-pool, ioredis
- Key interfaces: TaskController, AuthMiddleware, WebSocketManager
<!-- spd:list:component-payload -->
<!-- spd:id:component -->
<!-- spd:####:component-title repeat="many" -->
<!-- spd:###:component-model -->

<!-- spd:###:api-contracts -->
### 3.3: API Contracts

<!-- spd:paragraph:api-contracts -->
REST API at `/api/v1/` with JSON request/response. Authentication via Bearer JWT token. Standard endpoints: `POST /tasks`, `GET /tasks`, `PATCH /tasks/:id`, `DELETE /tasks/:id`. WebSocket at `/ws` for real-time events: `task.created`, `task.updated`, `task.deleted`.
<!-- spd:paragraph:api-contracts -->
<!-- spd:###:api-contracts -->

<!-- spd:###:interactions -->
### 3.4: Interactions & Sequences

<!-- spd:####:sequence-title repeat="many" -->
#### Create Task Flow

<!-- spd:id:seq has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `spd-taskflow-seq-create-task`

<!-- spd:code:sequences -->
```mermaid
sequenceDiagram
    Member->>API: POST /tasks
    API->>PostgreSQL: INSERT task
    API->>Redis: PUBLISH task.created
    Redis-->>API: FAN-OUT
    API-->>Member: WS task.created
```
<!-- spd:code:sequences -->

<!-- spd:paragraph:sequence-body -->
Lead or member creates task via REST API. Server validates input, inserts into database, then publishes event to Redis for real-time distribution. All connected clients receive WebSocket notification within 2 seconds.
<!-- spd:paragraph:sequence-body -->
<!-- spd:id:seq -->
<!-- spd:####:sequence-title repeat="many" -->
<!-- spd:###:interactions -->

<!-- spd:###:database -->
### 3.5 Database schemas & tables (optional)

<!-- spd:####:db-table-title repeat="many" -->
#### Table tasks

<!-- spd:id:dbtable has="priority,task" covered_by="DECOMPOSITION,SPEC" -->
- [ ] `p1` - **ID**: `spd-taskflow-dbtable-tasks`

Schema
<!-- spd:table:db-table-schema -->
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Task ID (PK) |
| title | text | Task title (required) |
| description | text | Task description |
| status | enum | TODO, IN_PROGRESS, DONE |
| assignee_id | uuid | FK to users.id |
<!-- spd:table:db-table-schema -->

PK: `id`

Constraints: `status IN ('TODO', 'IN_PROGRESS', 'DONE')`, `assignee_id REFERENCES users(id)`

Example
<!-- spd:table:db-table-example -->
| id | title | status |
|----|-------|--------|
| 550e8400... | Implement login | IN_PROGRESS |
<!-- spd:table:db-table-example -->
<!-- spd:id:dbtable -->
<!-- spd:####:db-table-title repeat="many" -->
<!-- spd:###:database -->

<!-- spd:###:topology -->
### 3.6: Topology (optional)

<!-- spd:id:topology has="task" -->
- [ ] **ID**: `spd-taskflow-topology-local`

<!-- spd:free:topology-body -->
Local development: React SPA (port 3000) + API server (port 4000) + PostgreSQL (port 5432) + Redis (port 6379) on single machine. Production: Kubernetes deployment with horizontal scaling of API pods.
<!-- spd:free:topology-body -->
<!-- spd:id:topology -->
<!-- spd:###:topology -->

<!-- spd:###:tech-stack -->
### 3.7: Tech stack (optional)

<!-- spd:paragraph:status -->
**Status**: Accepted
<!-- spd:paragraph:status -->

<!-- spd:paragraph:tech-body -->
Backend: Node.js 18 LTS, TypeScript 5.x, Express 4.x, pg-pool for PostgreSQL, ioredis for Redis. Frontend: React 18, TypeScript, Vite build tool. Testing: Jest, React Testing Library. Rationale: Team familiarity, mature ecosystem, strong TypeScript support.
<!-- spd:paragraph:tech-body -->
<!-- spd:###:tech-stack -->
<!-- spd:##:technical-architecture -->

<!-- spd:##:design-context -->
## 4. Additional Context

<!-- spd:free:design-context-body -->
TaskFlow prioritizes real-time collaboration and predictable REST semantics. Future considerations include mobile app support and Slack integration. Trade-offs accepted: PostgreSQL requires operational overhead vs SQLite simplicity.
<!-- spd:free:design-context-body -->

<!-- spd:paragraph:date -->
**Date**: 2025-01-15
<!-- spd:paragraph:date -->
<!-- spd:##:design-context -->

<!-- spd:#:design -->
