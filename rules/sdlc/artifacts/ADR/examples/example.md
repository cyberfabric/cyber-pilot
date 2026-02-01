<!-- fdd:#:adr -->
# ADR-0001: Use PostgreSQL for Task Storage

<!-- fdd:id:adr has="priority,task" covered_by="DESIGN" -->
- [ ] `p1` - **ID**: `fdd-taskflow-adr-postgres-storage`

<!-- fdd:##:meta -->
## Meta

<!-- fdd:paragraph:adr-title -->
**Title**: ADR-0001 Use PostgreSQL for Task Storage
<!-- fdd:paragraph:adr-title -->

<!-- fdd:paragraph:date -->
**Date**: 2025-01-10
<!-- fdd:paragraph:date -->

<!-- fdd:paragraph:status -->
**Status**: Accepted
<!-- fdd:paragraph:status -->
<!-- fdd:##:meta -->

<!-- fdd:##:body -->
## Body

<!-- fdd:context -->
**Context**:
TaskFlow needs persistent storage for tasks, users, and audit history. We need to choose between SQL and NoSQL databases considering query patterns, data relationships, and team expertise.

The system will handle:
- Task CRUD operations with complex filtering
- User and team relationships
- Assignment history and audit trail
- Real-time updates via change notifications
<!-- fdd:context -->

<!-- fdd:decision-drivers -->
**Decision Drivers**:
- Strong consistency required for task state transitions
- Relational queries needed for assignments and team structures
- Team has existing PostgreSQL expertise
- Operational maturity and hosting options important
<!-- fdd:decision-drivers -->

<!-- fdd:options repeat="many" -->
**Considered Options**:
1. **PostgreSQL** — Relational database with strong ACID guarantees, mature ecosystem, team expertise
2. **MongoDB** — Document store with flexible schema, good for rapid iteration, less suited for relational data
3. **SQLite** — Embedded database for simpler deployment, limited concurrent access, no built-in replication
<!-- fdd:options -->

<!-- fdd:decision-outcome -->
**Decision Outcome**:
Chosen option: **PostgreSQL**, because tasks have relational data (users, assignments, comments) that benefit from joins, strong consistency is needed for status transitions and assignments, team has existing PostgreSQL expertise, and it supports JSON columns for flexible metadata if needed later.
<!-- fdd:decision-outcome -->

**Consequences**:
<!-- fdd:list:consequences -->
- Positive: ACID transactions ensure data integrity during concurrent updates
- Positive: Efficient queries for filtering tasks by status, assignee, due date
- Negative: Requires separate database server (vs embedded SQLite)
- Negative: Schema migrations needed for model changes
- Follow-up: Set up connection pooling for scalability
<!-- fdd:list:consequences -->

**Links**:
<!-- fdd:list:links -->
- [`fdd-taskflow-fr-task-management`](../PRD.md) — Primary requirement for task storage
- [`fdd-taskflow-feature-task-crud`](../features/task-crud/DESIGN.md) — Feature implementing task persistence
<!-- fdd:list:links -->
<!-- fdd:##:body -->

<!-- fdd:id:adr -->
<!-- fdd:#:adr -->
