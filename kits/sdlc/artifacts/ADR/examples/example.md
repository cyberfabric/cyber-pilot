---
status: accepted
date: 2026-02-16
--- 

# ADR-0001: Use PostgreSQL for Task Storage

**ID**: `cpt-taskflow-adr-postgres-storage`

## Context and Problem Statement

TaskFlow needs persistent storage for tasks, users, and audit history. We need to choose between SQL and NoSQL databases considering query patterns, data relationships, and team expertise.

The system will handle:

- Task CRUD operations with complex filtering
- User and team relationships
- Assignment history and audit trail
- Real-time updates via change notifications


## Decision Drivers

- Strong consistency required for task state transitions
- Relational queries needed for assignments and team structures
- Team has existing PostgreSQL expertise
- Operational maturity and hosting options important


## Considered Options

1. **PostgreSQL** — Relational database with strong ACID guarantees, mature ecosystem, team expertise
2. **MongoDB** — Document store with flexible schema, good for rapid iteration, less suited for relational data
3. **SQLite** — Embedded database for simpler deployment, limited concurrent access, no built-in replication


## Decision Outcome

Chosen option: **PostgreSQL**, because tasks have relational data (users, assignments, comments) that benefit from joins, strong consistency is needed for status transitions and assignments, team has existing PostgreSQL expertise, and it supports JSON columns for flexible metadata if needed later.

### Consequences

- Positive: ACID transactions ensure data integrity during concurrent updates
- Positive: Efficient queries for filtering tasks by status, assignee, due date
- Negative: Requires separate database server (vs embedded SQLite)
- Negative: Schema migrations needed for model changes
- Follow-up: Set up connection pooling for scalability

### Confirmation

Confirmed when:

- A prototype persists tasks and assignments with required relational queries
- Migration story is documented and validated on a schema change


## Pros and Cons of the Options

### PostgreSQL

- Pros: Strong consistency, rich SQL queries, mature ecosystem
- Cons: Operational overhead (DB server, backups, migrations)

### MongoDB

- Pros: Flexible schema, quick iteration
- Cons: Harder relational queries and consistency model trade-offs

### SQLite

- Pros: Simple deployment, minimal ops
- Cons: Limited concurrent writes and scaling options


## More Information

- [`cpt-taskflow-fr-task-management`](../PRD.md) — Primary requirement for task storage
- [`cpt-taskflow-spec-task-crud`](../specs/task-crud/DESIGN.md) — Spec implementing task persistence





