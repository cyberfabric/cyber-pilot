# Features: TaskFlow

## A. Status Overview

**Status Overview**: 2 features total (0 implemented, 1 in development, 1 design ready, 0 in design, 0 not started)

**Meaning**:
- ⏳ NOT_STARTED: planned
- 📝 IN_DESIGN: being designed
- 📘 DESIGN_READY: design completed and ready for development
- 🔄 IN_DEVELOPMENT: being implemented
- ✅ IMPLEMENTED: done

## B. Entries

### 1. [Task CRUD](feature-task-crud/) 🔄 HIGH

**ID**: `fdd-taskflow-feature-task-crud`

- **Purpose**: Enable users to create, view, edit, and delete tasks with full lifecycle management.
- **Status**: IN_DEVELOPMENT
- **Depends On**: None
- **Blocks**: `fdd-taskflow-feature-notifications`
- **Scope**:
  - Task creation with title, description, priority, due date
  - Task assignment to team members
  - Status transitions (BACKLOG → IN_PROGRESS → DONE)
  - Task deletion with soft-delete
- **Requirements Covered**:
  - `fdd-taskflow-req-task-crud`
  - `fdd-taskflow-nfr-performance-reliability`
- **Design Principles Covered**:
  - `fdd-taskflow-principle-realtime-first`
  - `fdd-taskflow-principle-simplicity-over-features`
- **Design Constraints Covered**:
  - `fdd-taskflow-constraint-supported-platforms`
- **Domain Model Entities**:
  - Task
  - User
- **Design Components**:
  - React SPA
  - API Server
  - PostgreSQL
  - Redis PubSub
- **API**:
  - `POST /api/tasks`
  - `GET /api/tasks`
- **Sequences**:
  - Task creation flow (Member -> API Server -> PostgreSQL -> Redis -> React SPA)
- **Data**:
  - `fdd-taskflow-db-table-tasks`
- **Phases**:
  - `ph-1`: ✅ IMPLEMENTED — basic CRUD API
  - `ph-2`: 🔄 IN_DEVELOPMENT — assignment and status transitions

### 2. [Notifications](feature-notifications/) 📘 MEDIUM

**ID**: `fdd-taskflow-feature-notifications`

- **Purpose**: Notify users about task assignments, due dates, and status changes.
- **Status**: DESIGN_READY
- **Depends On**: `fdd-taskflow-feature-task-crud`
- **Blocks**: None
- **Scope**:
  - Push notifications for task assignments
  - Email alerts for overdue tasks
  - In-app notification center
- **Requirements Covered**:
  - `fdd-taskflow-req-notifications`
- **Design Principles Covered**:
  - `fdd-taskflow-principle-realtime-first`
  - `fdd-taskflow-principle-mobile-first`
- **Design Constraints Covered**:
  - `fdd-taskflow-constraint-supported-platforms`
- **Domain Model Entities**:
  - Task
  - User
- **Design Components**:
  - React SPA
  - API Server
  - Redis PubSub
- **API**:
  - `POST /api/notifications`
  - `GET /api/notifications`
- **Sequences**:
  - Notification delivery flow
- **Data**:
  - None
- **Phases**:
  - `ph-1`: ⏳ NOT_STARTED — push notifications
  - `ph-2`: ⏳ NOT_STARTED — email alerts
