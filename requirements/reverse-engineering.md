---
fdd: true
type: requirement
name: Reverse Engineering Methodology
version: 1.0
purpose: Technology-agnostic methodology for systematic project analysis
---

# Reverse Engineering Methodology

**Scope**: Any software project regardless of language, framework, or architecture

---

## Table of Contents

- [Agent Instructions](#agent-instructions)
- [Overview](#overview)
- [Analysis Layers](#analysis-layers)
- [Layer 1: Surface Reconnaissance](#layer-1-surface-reconnaissance)
- [Layer 2: Entry Point Analysis](#layer-2-entry-point-analysis)
- [Layer 3: Structural Decomposition](#layer-3-structural-decomposition)
- [Layer 4: Data Flow Tracing](#layer-4-data-flow-tracing)
- [Layer 5: Dependency Mapping](#layer-5-dependency-mapping)
- [Layer 6: State Management Analysis](#layer-6-state-management-analysis)
- [Layer 7: Integration Boundary Scan](#layer-7-integration-boundary-scan)
- [Layer 8: Pattern Recognition](#layer-8-pattern-recognition)
- [Layer 9: Knowledge Synthesis](#layer-9-knowledge-synthesis)
- [Execution Protocol](#execution-protocol)
- [Error Handling](#error-handling)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)
- [References](#references)

---

## Agent Instructions

**ALWAYS open and follow**: This file WHEN user requests to analyze codebase, search in code, search in project documentation, or generate artifacts/code based on existing project structure

**ALWAYS open and follow**: `execution-protocol.md` for workflow context

**Prerequisite**: Agent confirms understanding before proceeding:
- [ ] Agent has read and understood this methodology
- [ ] Agent has access to source code repository
- [ ] Agent will execute layers in order 1-9
- [ ] Agent will checkpoint findings after each layer

---

## Overview

This methodology provides a systematic approach to understanding any software project through progressive layers of analysis. Each layer builds on the previous, creating a comprehensive mental model of the system.

**Core Principle**: Observe patterns, not technologies. Every project, regardless of stack, exhibits universal patterns in how it organizes code, handles data, manages state, and communicates between components.

---

## Analysis Layers

```
Layer 1: Surface Reconnaissance     → What does this project look like?
Layer 2: Entry Point Analysis       → Where does execution begin?
Layer 3: Structural Decomposition   → How is code organized?
Layer 4: Data Flow Tracing          → How does data move through the system?
Layer 5: Dependency Mapping         → What depends on what?
Layer 6: State Management Analysis  → How is state created, modified, persisted?
Layer 7: Integration Boundary Scan  → Where does the system touch the outside world?
Layer 8: Pattern Recognition        → What conventions and idioms are used?
Layer 9: Knowledge Synthesis        → What have we learned?
```

---

# Layer 1: Surface Reconnaissance

**Goal**: Form initial impressions without reading code

## 1.1 Repository Structure Scan

### 1.1.1 Top-Level Directory Inventory

- [ ] List all top-level directories
- [ ] Identify standard directory names (src, lib, pkg, app, cmd, internal, test, docs)
- [ ] Identify non-standard directories (domain-specific names)
- [ ] Note directory naming convention (kebab-case, snake_case, camelCase, PascalCase)
- [ ] Note presence of hidden directories (.git, .github, .vscode, .idea)
- [ ] Note presence of configuration directories (config, settings, env)

### 1.1.2 File Inventory

- [ ] List all top-level files
- [ ] Identify configuration files (package.json, pyproject.toml, Cargo.toml, go.mod, pom.xml, build.gradle, *.csproj)
- [ ] Identify documentation files (README, CHANGELOG, CONTRIBUTING, LICENSE)
- [ ] Identify CI/CD files (.github/workflows, .gitlab-ci.yml, Jenkinsfile, .circleci)
- [ ] Identify container/infra files (Dockerfile, docker-compose.yml, k8s/, terraform/)
- [ ] Identify editor/IDE config (.editorconfig, .prettierrc, .eslintrc, .rubocop.yml)

### 1.1.3 Git History Analysis

- [ ] Check repository age (first commit date)
- [ ] Check recent activity (last commit date)
- [ ] Identify most active directories (frequently changed)
- [ ] Identify stale directories (rarely changed)
- [ ] Count contributors
- [ ] Identify commit message patterns (conventional commits, ticket references)

## 1.2 Language Detection

### 1.2.1 Primary Language Identification

- [ ] Scan for file extensions (.ts, .js, .py, .rs, .go, .java, .cs, .rb, .php, .kt, .swift, .cpp, .c)
- [ ] Count files per extension
- [ ] Identify primary language (highest file count in source directories)
- [ ] Identify secondary languages (scripts, tests, tools)

### 1.2.2 Multi-Language Patterns

- [ ] Check for polyglot structure (different languages in different directories)
- [ ] Check for FFI/bindings (native extensions, WASM, JNI)
- [ ] Check for generated code (protobuf, graphql codegen, ORM models)
- [ ] Check for DSLs (SQL files, template files, config schemas)

## 1.3 Documentation Inventory

### 1.3.1 Explicit Documentation

- [ ] Read README.md (project purpose, setup instructions)
- [ ] Check for docs/ directory structure
- [ ] Check for architecture documentation (ARCHITECTURE.md, ADR/, decisions/)
- [ ] Check for API documentation (openapi.yml, swagger.json, postman collections)
- [ ] Check for inline code documentation patterns (docstrings, JSDoc, rustdoc)

### 1.3.2 Implicit Documentation

- [ ] Analyze test names (describe behavior)
- [ ] Analyze type definitions (reveal domain model)
- [ ] Analyze error messages (reveal business rules)
- [ ] Analyze log statements (reveal important operations)

---

# Layer 2: Entry Point Analysis

**Goal**: Understand where and how execution begins

## 2.1 Application Entry Points

### 2.1.1 Identify Main Entry Points

- [ ] Search for main function/file patterns:
  - Go: `func main()` in `main.go` or `cmd/*/main.go`
  - Python: `if __name__ == "__main__"` or `__main__.py`
  - Node.js: `main` in package.json, `index.js`, `app.js`, `server.js`
  - Java: `public static void main` or `@SpringBootApplication`
  - Rust: `fn main()` in `src/main.rs` or `src/bin/`
  - C#: `static void Main` or `Program.cs`
  - Ruby: script files, `config.ru`, `Rakefile`

### 2.1.2 Multiple Entry Points

- [ ] Check for CLI commands (subcommands, multiple binaries)
- [ ] Check for worker processes (background jobs, queue consumers)
- [ ] Check for scheduled tasks (cron, scheduled functions)
- [ ] Check for event handlers (webhooks, serverless functions)
- [ ] Check for migration scripts (database migrations, data scripts)

## 2.2 Request Entry Points (for services)

### 2.2.1 HTTP Entry Points

- [ ] Find route definitions (Express routes, FastAPI endpoints, Spring controllers)
- [ ] List all HTTP endpoints with methods (GET/POST/PUT/DELETE)
- [ ] Identify middleware chains (authentication, logging, rate limiting)
- [ ] Map URL patterns to handlers

### 2.2.2 Event Entry Points

- [ ] Find message queue consumers (RabbitMQ, Kafka, SQS handlers)
- [ ] Find event listeners (pub/sub, webhooks, websocket handlers)
- [ ] Find scheduled job handlers
- [ ] Find file watchers or stream processors

### 2.2.3 CLI Entry Points

- [ ] Find command definitions (argparse, cobra, clap, commander)
- [ ] List all commands and subcommands
- [ ] Identify command hierarchy

## 2.3 Bootstrap Sequence

### 2.3.1 Initialization Order

- [ ] Trace from entry point to first business logic
- [ ] Identify configuration loading
- [ ] Identify dependency injection/service container setup
- [ ] Identify database connection initialization
- [ ] Identify external service client initialization
- [ ] Identify middleware/interceptor registration
- [ ] Note initialization order dependencies

---

# Layer 3: Structural Decomposition

**Goal**: Understand how code is organized into logical units

## 3.1 High-Level Structure

### 3.1.1 Architectural Pattern Recognition

- [ ] Identify dominant architecture pattern:
  - Layered (controller → service → repository → database)
  - Hexagonal/Ports & Adapters (core domain isolated from infrastructure)
  - Clean Architecture (entities → use cases → interfaces → frameworks)
  - Microservices (independent deployable services)
  - Monolith (single deployable unit)
  - Modular Monolith (modules within single deployment)
  - Event-Driven (message/event centric)
  - Serverless (functions as deployment unit)

### 3.1.2 Module/Package Boundaries

- [ ] Identify top-level modules/packages
- [ ] Map module responsibilities (single sentence each)
- [ ] Identify module dependencies (which modules import which)
- [ ] Check for circular dependencies
- [ ] Identify shared/common modules
- [ ] Identify vendor/third-party wrappers

## 3.2 Code Organization Patterns

### 3.2.1 Grouping Strategy

- [ ] Identify grouping strategy:
  - By layer (controllers/, services/, repositories/, models/)
  - By feature (users/, orders/, payments/)
  - By domain (bounded contexts)
  - Hybrid (layers within features or features within layers)

### 3.2.2 File Organization

- [ ] Identify file naming patterns
- [ ] Identify file-per-class vs file-per-module patterns
- [ ] Identify index/barrel file usage (re-exports)
- [ ] Identify test file locations (adjacent, separate directory, nested)

## 3.3 Component Inventory

### 3.3.1 Core Components

For each identified module, document:

- [ ] Module name and location
- [ ] Primary responsibility (one sentence)
- [ ] Public interface (exported functions/classes/types)
- [ ] Key dependencies (other modules it imports)
- [ ] Persistence involvement (does it access storage?)
- [ ] External integration (does it call external services?)

### 3.3.2 Cross-Cutting Components

- [ ] Identify logging infrastructure
- [ ] Identify error handling infrastructure
- [ ] Identify configuration management
- [ ] Identify security/authentication
- [ ] Identify caching layer
- [ ] Identify validation layer

---

# Layer 4: Data Flow Tracing

**Goal**: Understand how data moves through the system

## 4.1 Request-Response Tracing

### 4.1.1 Trace Representative Flows

Select 3-5 representative operations and trace:

- [ ] Entry point (HTTP handler, CLI command, event handler)
- [ ] Input validation and transformation
- [ ] Business logic invocation
- [ ] Data persistence operations
- [ ] External service calls
- [ ] Response construction
- [ ] Error handling paths

### 4.1.2 Document Data Transformations

For each traced flow:

- [ ] Input shape (what data comes in)
- [ ] Intermediate shapes (how data transforms)
- [ ] Output shape (what data goes out)
- [ ] Side effects (what persists, what notifies)

## 4.2 Data Model Analysis

### 4.2.1 Domain Entities

- [ ] Identify core domain entities
- [ ] For each entity:
  - [ ] Name and location of definition
  - [ ] Key attributes
  - [ ] Relationships to other entities
  - [ ] Invariants/validation rules
  - [ ] Lifecycle states (if stateful)

### 4.2.2 Data Transfer Objects

- [ ] Identify DTO patterns (request/response objects)
- [ ] Map DTO to entity transformations
- [ ] Identify serialization formats (JSON, protobuf, XML)
- [ ] Check for versioning patterns (API versions)

## 4.3 Persistence Layer

### 4.3.1 Storage Technologies

- [ ] Identify databases (relational, document, key-value, graph)
- [ ] Identify file storage (local, S3, blob storage)
- [ ] Identify caches (Redis, Memcached, in-memory)
- [ ] Identify search indices (Elasticsearch, Algolia)

### 4.3.2 Data Access Patterns

- [ ] Identify ORM/query builder usage
- [ ] Identify raw SQL patterns
- [ ] Identify repository/DAO patterns
- [ ] Check for database migrations (location, tool)
- [ ] Check for seed data (location, format)

---

# Layer 5: Dependency Mapping

**Goal**: Understand internal and external dependencies

## 5.1 Internal Dependencies

### 5.1.1 Module Dependency Graph

- [ ] Build module import graph (which modules import which)
- [ ] Identify acyclic core (modules with no circular deps)
- [ ] Identify dependency hubs (modules imported by many)
- [ ] Identify leaf modules (modules that import nothing internal)
- [ ] Check dependency direction (do lower layers depend on higher?)

### 5.1.2 Dependency Injection

- [ ] Identify DI container/framework (if any)
- [ ] Identify service registration patterns
- [ ] Identify injection patterns (constructor, property, method)
- [ ] Map interface to implementation bindings

## 5.2 External Dependencies

### 5.2.1 Third-Party Libraries

- [ ] List direct dependencies from package manager
- [ ] Categorize by purpose:
  - Framework (web, CLI)
  - Database/ORM
  - HTTP client
  - Serialization
  - Validation
  - Testing
  - Utilities
- [ ] Identify critical dependencies (hard to replace)
- [ ] Check for outdated/deprecated dependencies
- [ ] Check for security vulnerabilities

### 5.2.2 External Services

- [ ] Identify external API calls
- [ ] For each external service:
  - [ ] Service name/purpose
  - [ ] Client location (where is it called)
  - [ ] Authentication method
  - [ ] Error handling approach
  - [ ] Retry/resilience patterns

---

# Layer 6: State Management Analysis

**Goal**: Understand how state is created, modified, and persisted

## 6.1 Application State

### 6.1.1 In-Memory State

- [ ] Identify singleton/global state
- [ ] Identify request-scoped state (context objects)
- [ ] Identify cached state (what is cached, where)
- [ ] Identify configuration state (runtime settings)

### 6.1.2 State Lifecycle

- [ ] How is state initialized?
- [ ] How is state accessed (direct, through accessors)?
- [ ] How is state modified (direct mutation, immutable updates)?
- [ ] How is state invalidated/cleared?

## 6.2 Persistent State

### 6.2.1 Database State

- [ ] Schema definition location
- [ ] Migration history (versions, tools)
- [ ] Index definitions
- [ ] Constraint definitions
- [ ] Trigger/stored procedure usage

### 6.2.2 State Machines

- [ ] Identify stateful entities (status fields, state enums)
- [ ] Document state transitions:
  - [ ] Valid states
  - [ ] Allowed transitions
  - [ ] Transition triggers
  - [ ] Transition side effects

## 6.3 Distributed State

### 6.3.1 Session/User State

- [ ] Where is session stored (cookie, JWT, server)?
- [ ] What data is in session?
- [ ] Session expiration/cleanup

### 6.3.2 Distributed Coordination

- [ ] Check for distributed locks
- [ ] Check for leader election
- [ ] Check for distributed caching
- [ ] Check for event sourcing/CQRS patterns

---

# Layer 7: Integration Boundary Scan

**Goal**: Map all system boundaries and external touchpoints

## 7.1 Inbound Boundaries

### 7.1.1 Public APIs

- [ ] HTTP REST endpoints
- [ ] GraphQL endpoints
- [ ] gRPC services
- [ ] WebSocket endpoints
- [ ] Webhook receivers

### 7.1.2 Internal APIs

- [ ] Internal service-to-service APIs
- [ ] Admin/management APIs
- [ ] Health/metrics endpoints

### 7.1.3 Asynchronous Inputs

- [ ] Message queue consumers
- [ ] Event subscribers
- [ ] Scheduled job triggers
- [ ] File system watchers

## 7.2 Outbound Boundaries

### 7.2.1 External API Calls

For each external API:

- [ ] Service name and purpose
- [ ] Base URL configuration
- [ ] Authentication/authorization
- [ ] Request/response formats
- [ ] Timeout configuration
- [ ] Retry policy
- [ ] Circuit breaker presence
- [ ] Fallback behavior

### 7.2.2 Database Connections

For each database:

- [ ] Database type and version
- [ ] Connection string location
- [ ] Connection pool configuration
- [ ] Read/write split (if any)
- [ ] Replica usage

### 7.2.3 External Outputs

- [ ] Message queue publishing
- [ ] Email/SMS sending
- [ ] File storage writes
- [ ] External notification webhooks

## 7.3 Infrastructure Boundaries

### 7.3.1 Container/Runtime

- [ ] Container base image
- [ ] Runtime configuration
- [ ] Environment variables used
- [ ] Secrets management

### 7.3.2 Network Configuration

- [ ] Port bindings
- [ ] Host configuration
- [ ] TLS/SSL setup
- [ ] Proxy configuration

---

# Layer 8: Pattern Recognition

**Goal**: Identify idioms, conventions, and patterns used throughout

## 8.1 Code Patterns

### 8.1.1 Creational Patterns

- [ ] Factory patterns (where objects are created)
- [ ] Builder patterns (complex object construction)
- [ ] Singleton patterns (global instances)
- [ ] Dependency injection patterns

### 8.1.2 Structural Patterns

- [ ] Adapter/wrapper patterns
- [ ] Decorator patterns
- [ ] Facade patterns (simplified interfaces)
- [ ] Proxy patterns

### 8.1.3 Behavioral Patterns

- [ ] Strategy patterns (interchangeable algorithms)
- [ ] Observer patterns (event handling)
- [ ] Command patterns (encapsulated operations)
- [ ] State patterns (behavior based on state)

## 8.2 Project Conventions

### 8.2.1 Naming Conventions

- [ ] Variable naming (camelCase, snake_case, etc.)
- [ ] Function naming (verbs, prefixes)
- [ ] Class/type naming (nouns, suffixes)
- [ ] File naming (case, separators)
- [ ] Directory naming (singular vs plural)

### 8.2.2 Code Style

- [ ] Indentation (spaces vs tabs, size)
- [ ] Line length limits
- [ ] Import organization
- [ ] Comment style
- [ ] Documentation format

### 8.2.3 Error Handling Convention

- [ ] Exception vs result types
- [ ] Error message format
- [ ] Error code patterns
- [ ] Logging on errors
- [ ] Error propagation strategy

## 8.3 Testing Conventions

### 8.3.1 Test Organization

- [ ] Test file location pattern
- [ ] Test naming convention
- [ ] Test structure (describe/it, given/when/then, arrange/act/assert)
- [ ] Setup/teardown patterns
- [ ] Fixture patterns

### 8.3.2 Test Types

- [ ] Unit test patterns
- [ ] Integration test patterns
- [ ] E2E test patterns
- [ ] Test data management
- [ ] Mocking/stubbing patterns

---

# Layer 9: Knowledge Synthesis

**Goal**: Consolidate findings into actionable knowledge

## 9.1 Architecture Summary

### 9.1.1 System Overview

Produce single-paragraph system description covering:

- [ ] Primary purpose
- [ ] Key technologies
- [ ] Architectural style
- [ ] Major components
- [ ] Primary data flows

### 9.1.2 Component Map

Produce visual or textual component map:

- [ ] All major components
- [ ] Component relationships
- [ ] Data flow directions
- [ ] Integration points

## 9.2 Domain Model Summary

### 9.2.1 Core Entities

- [ ] List all identified entities with one-line descriptions
- [ ] Entity relationship summary
- [ ] Key business rules/invariants

### 9.2.2 Key Operations

- [ ] List critical business operations
- [ ] Map operation to entry point
- [ ] Summarize data flow for each

## 9.3 Technical Debt & Risks

### 9.3.1 Identified Issues

- [ ] Circular dependencies
- [ ] Overly complex modules
- [ ] Inconsistent patterns
- [ ] Missing error handling
- [ ] Security concerns
- [ ] Performance concerns

### 9.3.2 Knowledge Gaps

- [ ] Areas not fully understood
- [ ] Missing documentation
- [ ] Unclear business logic
- [ ] Untested code paths

## 9.4 Entry Points Summary

### 9.4.1 For Developers

- [ ] Where to start reading code
- [ ] Key files to understand first
- [ ] Critical abstractions to learn
- [ ] Common modification patterns

### 9.4.2 For Operations

- [ ] Deployment process
- [ ] Configuration options
- [ ] Monitoring/alerting setup
- [ ] Troubleshooting guides

---

# Execution Protocol

## Prerequisites

Before starting reverse engineering:

- [ ] Access to source code repository
- [ ] Ability to search/grep codebase
- [ ] Read permissions for all directories
- [ ] (Optional) Ability to run the code locally
- [ ] (Optional) Access to running instance

## Execution Order

Layers MUST be executed in order 1-9. Each layer builds on previous findings.

**Checkpointing**: After each layer, summarize findings before proceeding.

**Time Boxing**: Set time limits per layer based on project size:

| Project Size | Layer 1-2 | Layer 3-4 | Layer 5-7 | Layer 8-9 |
|--------------|-----------|-----------|-----------|-----------|
| Small (<10k LOC) | 15min | 30min | 30min | 15min |
| Medium (10k-100k) | 30min | 1hr | 1hr | 30min |
| Large (>100k) | 1hr | 2hr | 2hr | 1hr |

## Output Artifacts

After completing all layers, produce:

1. **System Overview** (1 page max)
   - Purpose, tech stack, architecture style
   - Key components and relationships

2. **Domain Model** (entities and relationships)

3. **Entry Points Catalog** (all ways to invoke the system)

4. **Integration Map** (external dependencies and boundaries)

5. **Conventions Guide** (naming, patterns, idioms)

6. **Technical Debt List** (issues and risks identified)

---

## Applicability

This methodology applies to:

- **Greenfield projects**: Validate understanding before implementation
- **Brownfield projects**: Understand before modification
- **Acquisitions/transfers**: Due diligence and onboarding
- **Legacy modernization**: Identify boundaries for strangler fig pattern
- **Documentation generation**: Input for FDD artifact creation

## Integration with FDD

This methodology feeds into FDD workflows:

- **Adapter workflow**: Uses Layer 1-3 for project scan
- **Generate workflow**: Uses all layers for artifact creation
- **Validate workflow**: Uses Layer 4-7 for traceability verification

---

## Error Handling

### Repository Access Failed

**If source code repository cannot be accessed**:
```
⚠️ Repository access failed: {error}
→ Check file permissions
→ Verify path exists
→ Confirm VCS (git) is accessible
```
**Action**: STOP — cannot analyze without source access.

### Layer Incomplete

**If a layer cannot be fully completed**:
```
⚠️ Layer {N} incomplete: {reason}
→ Completed: {list of completed items}
→ Skipped: {list of skipped items}
→ Reason: {blocking issue}
```
**Action**: Document gaps explicitly, proceed to next layer with caveat.

### External Dependencies Unavailable

**If external services/dependencies cannot be inspected**:
```
⚠️ External dependency unavailable: {service}
→ Cannot verify: integration patterns, authentication, data formats
→ Marking integration boundary as UNVERIFIED
```
**Action**: WARN and continue — document as knowledge gap.

### Large Codebase Timeout

**If analysis exceeds time box for layer**:
```
⚠️ Time box exceeded for Layer {N}
→ Completed: {percentage}% of checklist items
→ Save checkpoint and resume later OR
→ Proceed with partial findings (document gaps)
```
**Action**: Save checkpoint, note incompleteness, proceed to next layer.

### Obfuscated or Generated Code

**If significant portions are obfuscated/generated**:
```
⚠️ Obfuscated/generated code detected: {location}
→ Skipping detailed analysis of generated files
→ Focusing on source templates/generators instead
```
**Action**: Analyze generators/templates, not generated output.

---

## Consolidated Validation Checklist

**Use this single checklist for all reverse engineering validation.**

### Surface Analysis (L1-L2)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| L1.1 | Repository structure documented | YES | Directory tree captured |
| L1.2 | Primary language identified | YES | File extension counts analyzed |
| L1.3 | Documentation inventory complete | YES | README, docs/, ADRs listed |
| L2.1 | Main entry points identified | YES | Entry files/functions listed |
| L2.2 | Bootstrap sequence traced | YES | Initialization order documented |

### Structural Analysis (L3-L4)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| L3.1 | Architecture pattern identified | YES | Pattern name stated with evidence |
| L3.2 | Module boundaries mapped | YES | Modules listed with responsibilities |
| L3.3 | Component inventory complete | YES | Core + cross-cutting components listed |
| L4.1 | Representative flows traced | YES | 3-5 flows documented entry-to-exit |
| L4.2 | Domain entities identified | YES | Entities with attributes listed |
| L4.3 | Persistence layer documented | YES | Storage technologies and patterns noted |

### Dependency Analysis (L5-L6)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| L5.1 | Module dependency graph built | YES | Import relationships mapped |
| L5.2 | External dependencies cataloged | YES | Libraries categorized by purpose |
| L5.3 | External services documented | YES | API calls with auth/error handling noted |
| L6.1 | Application state locations identified | YES | Global, request-scoped, cached state listed |
| L6.2 | State machines documented | CONDITIONAL | If stateful entities exist, transitions mapped |
| L6.3 | Distributed state patterns noted | CONDITIONAL | If distributed, coordination mechanisms listed |

### Integration Analysis (L7-L8)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| L7.1 | Inbound boundaries cataloged | YES | APIs, consumers, triggers listed |
| L7.2 | Outbound boundaries cataloged | YES | External calls, databases, outputs listed |
| L7.3 | Infrastructure boundaries noted | YES | Container, network, secrets documented |
| L8.1 | Code patterns identified | YES | Creational, structural, behavioral patterns listed |
| L8.2 | Project conventions documented | YES | Naming, style, error handling patterns noted |
| L8.3 | Testing conventions documented | YES | Test organization and patterns noted |

### Synthesis (L9)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| L9.1 | System overview produced | YES | Single-paragraph description complete |
| L9.2 | Component map produced | YES | Visual or textual map created |
| L9.3 | Domain model summarized | YES | Entities and relationships listed |
| L9.4 | Technical debt identified | YES | Issues and risks documented |
| L9.5 | Knowledge gaps listed | YES | Unclear areas explicitly noted |
| L9.6 | Entry points summary for developers | YES | Where to start reading documented |

### Final (F)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| F.1 | All Surface Analysis checks pass | YES | L1.1-L2.2 verified |
| F.2 | All Structural Analysis checks pass | YES | L3.1-L4.3 verified |
| F.3 | All Dependency Analysis checks pass | YES | L5.1-L6.3 verified (conditionals where applicable) |
| F.4 | All Integration Analysis checks pass | YES | L7.1-L8.3 verified |
| F.5 | All Synthesis checks pass | YES | L9.1-L9.6 verified |
| F.6 | Output artifacts produced | YES | 6 artifacts from Execution Protocol created |

---

## References

- Adapter workflow: `../workflows/adapter.md`
- Generate workflow: `../workflows/generate.md`
- Execution protocol: `./execution-protocol.md`
