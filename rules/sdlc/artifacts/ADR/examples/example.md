# ADR-0001: Use PostgreSQL for Task Storage

**Date**: 2025-01-10

**Status**: Accepted

**ID**: `fdd-taskflow-adr-postgres-storage`

## Context and Problem Statement

TaskFlow needs persistent storage for tasks, users, and audit history. We need to choose between SQL and NoSQL databases considering query patterns, data relationships, and team expertise.

## Decision Drivers

We need a storage system with strong consistency for task state transitions, good support for relational queries, and a mature operational model.

## Considered Options

We considered PostgreSQL (relational database with strong ACID guarantees), MongoDB (document store with flexible schema), and SQLite (embedded database for simpler deployment).

## Decision Outcome

Chosen option: **PostgreSQL**, because:
- Tasks have relational data (users, assignments, comments) that benefit from joins
- Strong consistency needed for status transitions and assignments
- Team has existing PostgreSQL expertise
- Supports JSON columns for flexible metadata if needed later

### Consequences

**Good**:
- ACID transactions ensure data integrity during concurrent updates
- Efficient queries for filtering tasks by status, assignee, due date

**Bad**:
- Requires separate database server (vs embedded SQLite)
- Schema migrations needed for model changes

## Links

Related items: `fdd-taskflow-req-task-crud` (primary requirement for task storage) and `fdd-taskflow-feature-task-crud` (feature implementing task persistence).
