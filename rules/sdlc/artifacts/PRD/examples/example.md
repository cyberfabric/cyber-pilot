# PRD
 
## A. Vision
 
**Purpose**: TaskFlow is a lightweight task management system for small teams, enabling task creation, assignment, and progress tracking with real-time notifications.

The system focuses on simplicity and speed, allowing teams to manage their daily work without the overhead of complex project management tools. TaskFlow bridges the gap between simple to-do lists and enterprise-grade solutions.

**Target Users**:
- Team leads managing sprints
- Developers tracking daily work
- Project managers monitoring progress

**Key Problems Solved**:
- Scattered task tracking across multiple tools
- Lack of visibility into team workload
- Missing deadline notifications

**Success Criteria**:
- Tasks created and assigned in under 30 seconds
- Real-time status updates visible to all team members
- Overdue task alerts delivered within 1 minute

**Capabilities**:
- Manage team tasks and assignments
- Track task status and progress in real time
- Send notifications for deadlines and status changes
 
## B. Actors
 
### Human Actors

#### Team Member

**ID**: `fdd-taskflow-actor-member`

**Role**: Creates tasks, updates progress, and collaborates on assignments.

#### Team Lead

**ID**: `fdd-taskflow-actor-lead`

**Role**: Assigns tasks, sets priorities, and monitors team workload.

### System Actors

#### Notification Service

**ID**: `fdd-taskflow-actor-notifier`

**Role**: Sends alerts for due dates, assignments, and status changes.
 
## C. Functional Requirements
 
#### Task Management

**ID**: `fdd-taskflow-fr-task-management`

- The system MUST allow creating, editing, and deleting tasks.
- The system MUST allow assigning tasks to team members.
- The system MUST allow setting due dates and priorities.

**Actors**: `fdd-taskflow-actor-member`, `fdd-taskflow-actor-lead`

#### Notifications

**ID**: `fdd-taskflow-fr-notifications`

- The system MUST send push notifications for assignments.
- The system MUST send alerts for overdue tasks.

**Actors**: `fdd-taskflow-actor-notifier`
 
## D. Use Cases
 
#### UC-001: Create and Assign Task

**ID**: `fdd-taskflow-usecase-create-task`

**Actor**: `fdd-taskflow-actor-lead`

**Preconditions**: User is authenticated and has team lead permissions.

**Flow**:
1. Lead creates a new task with title and description
2. Lead assigns task to a team member
3. System sends notification to assignee

**Postconditions**: Task appears in assignee's task list.
 
## E. Non-functional requirements
 
#### Security

**ID**: `fdd-taskflow-nfr-security`

- Authentication MUST be required for all user actions.
- Authorization MUST enforce team role permissions.
 
## F. Additional context
 
#### Stakeholder Notes

**ID**: `fdd-taskflow-prd-context-stakeholder-notes`

- This product targets teams of 3-20 people initially.
