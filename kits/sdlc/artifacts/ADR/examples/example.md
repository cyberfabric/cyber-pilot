<!-- cpt:#:adr -->
# ADR-0001: Use PostgreSQL for Task Storage

<!-- cpt:id:adr has="priority,task" covered_by="DESIGN" -->
- [ ] `p1` - **ID**: `cpt-taskflow-adr-postgres-storage`

<!-- cpt:##:meta -->
## Meta

<!-- cpt:paragraph:adr-title -->
**Title**: ADR-0001 Use PostgreSQL for Task Storage
<!-- cpt:paragraph:adr-title -->

<!-- cpt:paragraph:date -->
**Date**: 2025-01-10
<!-- cpt:paragraph:date -->

<!-- cpt:paragraph:status -->
**Status**: Accepted
<!-- cpt:paragraph:status -->
<!-- cpt:##:meta -->

<!-- cpt:##:body -->
## Body

<!-- cpt:context -->
**Context**:
TaskFlow needs persistent storage for tasks, users, and audit history. We need to choose between SQL and NoSQL databases considering query patterns, data relationships, and team expertise.

The system will handle:
- Task CRUD operations with complex filtering
- User and team relationships
- Assignment history and audit trail
- Real-time updates via change notifications
<!-- cpt:context -->

<!-- cpt:decision-drivers -->
**Decision Drivers**:
- Strong consistency required for task state transitions
- Relational queries needed for assignments and team structures
- Team has existing PostgreSQL expertise
- Operational maturity and hosting options important
<!-- cpt:decision-drivers -->

<!-- cpt:options repeat="many" -->
**Considered Options**:
1. **PostgreSQL** — Relational database with strong ACID guarantees, mature ecosystem, team expertise
2. **MongoDB** — Document store with flexible schema, good for rapid iteration, less suited for relational data
3. **SQLite** — Embedded database for simpler deployment, limited concurrent access, no built-in replication
<!-- cpt:options -->

<!-- cpt:decision-outcome -->
**Decision Outcome**:
Chosen option: **PostgreSQL**, because tasks have relational data (users, assignments, comments) that benefit from joins, strong consistency is needed for status transitions and assignments, team has existing PostgreSQL expertise, and it supports JSON columns for flexible metadata if needed later.
<!-- cpt:decision-outcome -->

**Consequences**:
<!-- cpt:list:consequences -->
- Positive: ACID transactions ensure data integrity during concurrent updates
- Positive: Efficient queries for filtering tasks by status, assignee, due date
- Negative: Requires separate database server (vs embedded SQLite)
- Negative: Schema migrations needed for model changes
- Follow-up: Set up connection pooling for scalability
<!-- cpt:list:consequences -->

**Links**:
<!-- cpt:list:links -->
- [`cpt-taskflow-fr-task-management`](../PRD.md) — Primary requirement for task storage
- [`cpt-taskflow-spec-task-crud`](../specs/task-crud/DESIGN.md) — Spec implementing task persistence
<!-- cpt:list:links -->
<!-- cpt:##:body -->

<!-- cpt:id:adr -->
<!-- cpt:#:adr -->
