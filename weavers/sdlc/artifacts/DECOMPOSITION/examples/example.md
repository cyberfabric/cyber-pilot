<!-- spd:#:decomposition -->
# Decomposition: TaskFlow

<!-- spd:##:overview -->
## 1. Overview

TaskFlow design is decomposed into features organized around core task management capabilities. The decomposition follows a dependency order where foundational CRUD operations enable higher-level features like notifications and reporting.

**Decomposition Strategy**:
- Features grouped by functional cohesion (related capabilities together)
- Dependencies minimize coupling between features
- Each feature covers specific components and sequences from DESIGN
- 100% coverage of all DESIGN elements verified

<!-- spd:##:overview -->

<!-- spd:##:entries -->
## 2. Entries

**Overall implementation status:**
<!-- spd:id:status has="priority,task" -->
- [ ] `p1` - **ID**: `spd-taskflow-status-overall`

<!-- spd:###:feature-title repeat="many" -->
### 1. [Task CRUD](feature-task-crud/) ⏳ HIGH

<!-- spd:id:feature has="priority,task" -->
- [ ] `p1` - **ID**: `spd-taskflow-feature-task-crud`

<!-- spd:paragraph:feature-purpose required="true" -->
- **Purpose**: Enable users to create, view, edit, and delete tasks with full lifecycle management.
<!-- spd:paragraph:feature-purpose -->

<!-- spd:paragraph:feature-depends -->
- **Depends On**: None
<!-- spd:paragraph:feature-depends -->

<!-- spd:list:feature-scope -->
- **Scope**:
  - Task creation with title, description, priority, due date
  - Task assignment to team members
  - Status transitions (BACKLOG → IN_PROGRESS → DONE)
  - Task deletion with soft-delete
<!-- spd:list:feature-scope -->

<!-- spd:list:feature-out-scope -->
- **Out of scope**:
  - Recurring tasks
  - Task templates
<!-- spd:list:feature-out-scope -->

- **Requirements Covered**:
<!-- spd:id-ref:fr has="priority,task" -->
  - [ ] `p1` - `spd-taskflow-fr-task-crud`
  - [ ] `p2` - `spd-taskflow-nfr-performance-reliability`
<!-- spd:id-ref:fr -->

- **Design Principles Covered**:
<!-- spd:id-ref:principle has="priority,task" -->
  - [ ] `p1` - `spd-taskflow-principle-realtime-first`
  - [ ] `p2` - `spd-taskflow-principle-simplicity-over-features`
<!-- spd:id-ref:principle -->

- **Design Constraints Covered**:
<!-- spd:id-ref:constraint has="priority,task" -->
  - [ ] `p1` - `spd-taskflow-constraint-supported-platforms`
<!-- spd:id-ref:constraint -->

<!-- spd:list:feature-domain-entities -->
- **Domain Model Entities**:
  - Task
  - User
<!-- spd:list:feature-domain-entities -->

- **Design Components**:
<!-- spd:id-ref:component has="priority,task" -->
  - [ ] `p1` - `spd-taskflow-component-react-spa`
  - [ ] `p1` - `spd-taskflow-component-api-server`
  - [ ] `p1` - `spd-taskflow-component-postgresql`
  - [ ] `p2` - `spd-taskflow-component-redis-pubsub`
<!-- spd:id-ref:component -->

<!-- spd:list:feature-api -->
- **API**:
  - POST /api/tasks
  - GET /api/tasks
  - PUT /api/tasks/{id}
  - DELETE /api/tasks/{id}
<!-- spd:list:feature-api -->

- **Sequences**:
<!-- spd:id-ref:seq has="priority,task" -->
  - [ ] `p1` - `spd-taskflow-seq-task-creation`
<!-- spd:id-ref:seq -->

- **Data**:
<!-- spd:id-ref:dbtable has="priority,task" -->
  - [ ] `p1` - `spd-taskflow-dbtable-tasks`
<!-- spd:id-ref:dbtable -->

<!-- spd:id:feature -->
<!-- spd:###:feature-title repeat="many" -->

<!-- spd:###:feature-title repeat="many" -->
### 2. [Notifications](feature-notifications/) ⏳ MEDIUM

<!-- spd:id:feature has="priority,task" -->
- [ ] `p2` - **ID**: `spd-taskflow-feature-notifications`

<!-- spd:paragraph:feature-purpose required="true" -->
- **Purpose**: Notify users about task assignments, due dates, and status changes.
<!-- spd:paragraph:feature-purpose -->

<!-- spd:paragraph:feature-depends -->
- **Depends On**: `spd-taskflow-feature-task-crud`
<!-- spd:paragraph:feature-depends -->

<!-- spd:list:feature-scope -->
- **Scope**:
  - Push notifications for task assignments
  - Email alerts for overdue tasks
  - In-app notification center
<!-- spd:list:feature-scope -->

<!-- spd:list:feature-out-scope -->
- **Out of scope**:
  - SMS notifications
  - Custom notification templates
<!-- spd:list:feature-out-scope -->

- **Requirements Covered**:
<!-- spd:id-ref:fr has="priority,task" -->
  - [ ] `p2` - `spd-taskflow-fr-notifications`
<!-- spd:id-ref:fr -->

- **Design Principles Covered**:
<!-- spd:id-ref:principle has="priority,task" -->
  - [ ] `p1` - `spd-taskflow-principle-realtime-first`
  - [ ] `p2` - `spd-taskflow-principle-mobile-first`
<!-- spd:id-ref:principle -->

- **Design Constraints Covered**:
<!-- spd:id-ref:constraint has="priority,task" -->
  - [ ] `p1` - `spd-taskflow-constraint-supported-platforms`
<!-- spd:id-ref:constraint -->

<!-- spd:list:feature-domain-entities -->
- **Domain Model Entities**:
  - Task
  - User
  - Notification
<!-- spd:list:feature-domain-entities -->

- **Design Components**:
<!-- spd:id-ref:component has="priority,task" -->
  - [ ] `p1` - `spd-taskflow-component-react-spa`
  - [ ] `p1` - `spd-taskflow-component-api-server`
  - [ ] `p2` - `spd-taskflow-component-redis-pubsub`
<!-- spd:id-ref:component -->

<!-- spd:list:feature-api -->
- **API**:
  - POST /api/notifications
  - GET /api/notifications
  - PUT /api/notifications/{id}/read
<!-- spd:list:feature-api -->

- **Sequences**:
<!-- spd:id-ref:seq has="priority,task" -->
  - [ ] `p2` - `spd-taskflow-seq-notification-delivery`
<!-- spd:id-ref:seq -->

- **Data**:
<!-- spd:id-ref:dbtable has="priority,task" -->
  - [ ] `p2` - `spd-taskflow-dbtable-notifications`
<!-- spd:id-ref:dbtable -->

<!-- spd:id:feature -->
<!-- spd:###:feature-title repeat="many" -->

<!-- spd:id:status -->
<!-- spd:##:entries -->
<!-- spd:#:decomposition -->
