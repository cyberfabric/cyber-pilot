# Business Context: Task Management API

**Project**: task-api  
**Version**: 1.0  
**Last Updated**: 2025-01-17

---

## A. VISION

### Purpose
A RESTful API for managing tasks, projects, and teams with real-time collaboration features.

### Target Users
- **Development Teams**: Using API for internal task tracking
- **Third-party Apps**: Integrating task management into their products
- **Mobile Apps**: Building iOS/Android task management clients

### Key Problems Solved
- **Manual task tracking**: Eliminates spreadsheet-based task management
- **Poor collaboration**: Enables real-time updates and notifications
- **Integration gaps**: Provides standard REST API for all platforms

### Success Criteria
- API response time <200ms for 95% of requests
- 99.9% uptime SLA
- Support 10,000 concurrent users
- Complete API documentation with examples

---

## B. ACTORS

**Human Actors**:

#### Developer
**ID**: `fdd-task-api-actor-developer`  
**Role**: Consumes API to build applications  
**Goals**: Easy integration, clear documentation, predictable behavior

#### Team Lead
**ID**: `fdd-task-api-actor-team-lead`  
**Role**: Manages projects and team members via API  
**Goals**: Bulk operations, reporting, team analytics

**System Actors**:

#### API Gateway
**ID**: `fdd-task-api-actor-api-gateway`  
**Role**: Routes requests, enforces rate limits, handles authentication  
**Interacts with**: All external clients

#### Database
**ID**: `fdd-task-api-actor-database`  
**Role**: Persists tasks, projects, users  
**Technology**: PostgreSQL

#### Notification Service
**ID**: `fdd-task-api-actor-notification-service`  
**Role**: Sends real-time updates via WebSocket  
**Technology**: Redis Pub/Sub

---

## C. CAPABILITIES

### Create and Manage Tasks
**ID**: `fdd-task-api-cap-task-management`  
**Actors**: `fdd-task-api-actor-developer`, `fdd-task-api-actor-team-lead`

**Features**:
- Create tasks with title, description, assignee, due date
- Update task status (TODO, IN_PROGRESS, DONE)
- Assign tasks to team members
- Add comments and attachments
- Set task priority and labels

**Use Cases**:
- **Create Task**: `fdd-task-api-uc-create-task`
- **Update Task Status**: `fdd-task-api-uc-update-task-status`
- **Assign Task**: `fdd-task-api-uc-assign-task`

### Organize Projects
**ID**: `fdd-task-api-cap-project-organization`  
**Actors**: `fdd-task-api-actor-team-lead`

**Features**:
- Create projects with milestones
- Group tasks into projects
- Track project progress
- Generate project reports

**Use Cases**:
- **Create Project**: `fdd-task-api-uc-create-project`
- **Add Task to Project**: `fdd-task-api-uc-add-task-to-project`

### Real-time Collaboration
**ID**: `fdd-task-api-cap-realtime-collab`  
**Actors**: `fdd-task-api-actor-developer`, `fdd-task-api-actor-notification-service`

**Features**:
- WebSocket connection for live updates
- Task change notifications
- Online presence indicators
- Optimistic UI updates

**Use Cases**:
- **Subscribe to Updates**: `fdd-task-api-uc-subscribe-updates`
- **Broadcast Task Change**: `fdd-task-api-uc-broadcast-change`

---

## D. ADDITIONAL CONTEXT

### Constraints
- Must use PostgreSQL for persistence
- Maximum payload size: 10MB
- API keys expire after 90 days
- Rate limit: 1000 requests/hour per API key

### Assumptions
- Clients handle network failures gracefully
- Task IDs are UUIDs
- Timestamps use ISO 8601 format

### Out of Scope (v1.0)
- Time tracking features
- Gantt chart generation
- Email notifications (WebSocket only)
- File storage (external URLs only)
