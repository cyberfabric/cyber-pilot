<!-- fdd:#:features -->
# Features: TaskFlow

<!-- fdd:##:overview -->
## 1. Overview

TaskFlow features are organized around core task management capabilities. The decomposition follows a dependency order where foundational CRUD operations enable higher-level features like notifications and reporting.

<!-- fdd:##:overview -->

<!-- fdd:##:entries -->
## 2. Entries

**Overall implementation status:**
<!-- fdd:id:status has="priority,task" -->
- [ ] `p1` - **ID**: `fdd-taskflow-status-overall`

<!-- fdd:###:feature-title repeat="many" -->
### 1. [Task CRUD](feature-task-crud/) 🔄 HIGH

<!-- fdd:id:feature has="priority,task" -->
- [ ] `p1` - **ID**: `fdd-taskflow-feature-task-crud`

<!-- fdd:paragraph:feature-purpose required="true" -->
- **Purpose**: Enable users to create, view, edit, and delete tasks with full lifecycle management.
<!-- fdd:paragraph:feature-purpose -->

<!-- fdd:paragraph:feature-depends -->
- **Depends On**: None
<!-- fdd:paragraph:feature-depends -->

<!-- fdd:list:feature-scope -->
- **Scope**:
  - Task creation with title, description, priority, due date
  - Task assignment to team members
  - Status transitions (BACKLOG → IN_PROGRESS → DONE)
  - Task deletion with soft-delete
<!-- fdd:list:feature-scope -->

<!-- fdd:list:feature-out-scope -->
- **Out of scope**:
  - Recurring tasks
  - Task templates
<!-- fdd:list:feature-out-scope -->

- **Requirements Covered**:
<!-- fdd:id-ref:fr has="priority,task" -->
  - [ ] `p1` - `fdd-taskflow-fr-task-crud`
  - [ ] `p2` - `fdd-taskflow-nfr-performance-reliability`
<!-- fdd:id-ref:fr -->

- **Design Principles Covered**:
<!-- fdd:id-ref:principle has="priority,task" -->
  - [ ] `p1` - `fdd-taskflow-principle-realtime-first`
  - [ ] `p2` - `fdd-taskflow-principle-simplicity-over-features`
<!-- fdd:id-ref:principle -->

- **Design Constraints Covered**:
<!-- fdd:id-ref:constraint has="priority,task" -->
  - [ ] `p1` - `fdd-taskflow-constraint-supported-platforms`
<!-- fdd:id-ref:constraint -->

<!-- fdd:list:feature-domain-entities -->
- **Domain Model Entities**:
  - Task
  - User
<!-- fdd:list:feature-domain-entities -->

- **Design Components**:
<!-- fdd:id-ref:component has="priority,task" -->
  - [ ] `p1` - `fdd-taskflow-component-react-spa`
  - [ ] `p1` - `fdd-taskflow-component-api-server`
  - [ ] `p1` - `fdd-taskflow-component-postgresql`
  - [ ] `p2` - `fdd-taskflow-component-redis-pubsub`
<!-- fdd:id-ref:component -->

<!-- fdd:list:feature-api -->
- **API**:
  - POST /api/tasks
  - GET /api/tasks
  - PUT /api/tasks/{id}
  - DELETE /api/tasks/{id}
<!-- fdd:list:feature-api -->

- **Sequences**:
<!-- fdd:id-ref:seq has="priority,task" -->
  - [ ] `p1` - `fdd-taskflow-seq-task-creation`
<!-- fdd:id-ref:seq -->

- **Data**:
<!-- fdd:id-ref:dbtable has="priority,task" -->
  - [ ] `p1` - `fdd-taskflow-dbtable-tasks`
<!-- fdd:id-ref:dbtable -->

<!-- fdd:id:feature -->
<!-- fdd:###:feature-title repeat="many" -->

<!-- fdd:###:feature-title repeat="many" -->
### 2. [Notifications](feature-notifications/) 📘 MEDIUM

<!-- fdd:id:feature has="priority,task" -->
- [ ] `p2` - **ID**: `fdd-taskflow-feature-notifications`

<!-- fdd:paragraph:feature-purpose required="true" -->
- **Purpose**: Notify users about task assignments, due dates, and status changes.
<!-- fdd:paragraph:feature-purpose -->

<!-- fdd:paragraph:feature-depends -->
- **Depends On**: `fdd-taskflow-feature-task-crud`
<!-- fdd:paragraph:feature-depends -->

<!-- fdd:list:feature-scope -->
- **Scope**:
  - Push notifications for task assignments
  - Email alerts for overdue tasks
  - In-app notification center
<!-- fdd:list:feature-scope -->

<!-- fdd:list:feature-out-scope -->
- **Out of scope**:
  - SMS notifications
  - Custom notification templates
<!-- fdd:list:feature-out-scope -->

- **Requirements Covered**:
<!-- fdd:id-ref:fr has="priority,task" -->
  - [ ] `p2` - `fdd-taskflow-fr-notifications`
<!-- fdd:id-ref:fr -->

- **Design Principles Covered**:
<!-- fdd:id-ref:principle has="priority,task" -->
  - [ ] `p1` - `fdd-taskflow-principle-realtime-first`
  - [ ] `p2` - `fdd-taskflow-principle-mobile-first`
<!-- fdd:id-ref:principle -->

- **Design Constraints Covered**:
<!-- fdd:id-ref:constraint has="priority,task" -->
  - [ ] `p1` - `fdd-taskflow-constraint-supported-platforms`
<!-- fdd:id-ref:constraint -->

<!-- fdd:list:feature-domain-entities -->
- **Domain Model Entities**:
  - Task
  - User
  - Notification
<!-- fdd:list:feature-domain-entities -->

- **Design Components**:
<!-- fdd:id-ref:component has="priority,task" -->
  - [ ] `p1` - `fdd-taskflow-component-react-spa`
  - [ ] `p1` - `fdd-taskflow-component-api-server`
  - [ ] `p2` - `fdd-taskflow-component-redis-pubsub`
<!-- fdd:id-ref:component -->

<!-- fdd:list:feature-api -->
- **API**:
  - POST /api/notifications
  - GET /api/notifications
  - PUT /api/notifications/{id}/read
<!-- fdd:list:feature-api -->

- **Sequences**:
<!-- fdd:id-ref:seq has="priority,task" -->
  - [ ] `p2` - `fdd-taskflow-seq-notification-delivery`
<!-- fdd:id-ref:seq -->

- **Data**:
<!-- fdd:id-ref:dbtable has="priority,task" -->
  - [ ] `p2` - `fdd-taskflow-dbtable-notifications`
<!-- fdd:id-ref:dbtable -->

<!-- fdd:id:feature -->
<!-- fdd:###:feature-title repeat="many" -->

<!-- fdd:id:status -->
<!-- fdd:##:entries -->
<!-- fdd:#:features -->
