---
cypilot: true
type: requirement
name: Reverse Engineering Methodology
version: 1.0
purpose: Technology-agnostic methodology for systematic project analysis
---

# Reverse Engineering Methodology


<!-- toc -->

- [Agent Instructions](#agent-instructions)
- [Overview](#overview)
- [Layer Map](#layer-map)
- [L1: Surface Reconnaissance](#l1-surface-reconnaissance)
- [L2: Entry Point Analysis](#l2-entry-point-analysis)
- [L3: Structural Decomposition](#l3-structural-decomposition)
- [L4: Data Flow Tracing](#l4-data-flow-tracing)
- [L5: Dependency Mapping](#l5-dependency-mapping)
- [L6: State Management Analysis](#l6-state-management-analysis)
- [L7: Integration Boundary Scan](#l7-integration-boundary-scan)
- [L8: Pattern Recognition](#l8-pattern-recognition)
- [L9: Knowledge Synthesis](#l9-knowledge-synthesis)
- [Execution Protocol](#execution-protocol)
- [Error Handling](#error-handling)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)
- [References](#references)

<!-- /toc -->

**Scope**: Any software project regardless of language, framework, or architecture.

## Agent Instructions

**ALWAYS open and follow** this file WHEN the user asks to analyze a codebase, search project code or docs, or generate artifacts/code from existing project structure.

**ALWAYS open and follow** `{cypilot_path}/.core/requirements/execution-protocol.md` for workflow context.

**Prerequisites**: confirm the agent has read this methodology, has repository access, will execute layers `1 -> 9` in order, and will checkpoint after each layer.

## Overview

Reverse engineering builds a progressive mental model of a system. The rule is: **observe patterns, not technologies**. Every project reveals structure through entry points, organization, data movement, dependency direction, state transitions, and boundary behavior.

## Layer Map

| Layer | Question |
|---|---|
| L1 | What does the repository look like before reading code? |
| L2 | Where and how does execution begin? |
| L3 | How is code organized into logical units? |
| L4 | How does data move through the system? |
| L5 | What depends on what? |
| L6 | How is state created, modified, and persisted? |
| L7 | Where does the system touch the outside world? |
| L8 | What patterns and conventions recur? |
| L9 | What knowledge should be carried forward? |

## L1: Surface Reconnaissance

**Goal**: form initial impressions without deep code reading.

| Area | Required checks |
|---|---|
| Repository structure | List top-level directories; identify standard names (`src`, `lib`, `pkg`, `app`, `cmd`, `internal`, `test`, `docs`); identify non-standard/domain directories; note naming convention (`kebab-case`, `snake_case`, `camelCase`, `PascalCase`); note hidden directories (`.git`, `.github`, `.vscode`, `.idea`); note config directories (`config`, `settings`, `env`). |
| File inventory | List top-level files; identify config files (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `*.csproj`); doc files (`README`, `CHANGELOG`, `CONTRIBUTING`, `LICENSE`); CI/CD files (`.github/workflows`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci`); container/infra files (`Dockerfile`, `docker-compose.yml`, `k8s/`, `terraform/`); editor config (`.editorconfig`, `.prettierrc`, `.eslintrc`, `.rubocop.yml`). |
| Git history | Check repository age, recent activity, most active directories, stale directories, contributor count, and commit message patterns (conventional commits, ticket references). |
| Language detection | Scan extensions (`.ts`, `.js`, `.py`, `.rs`, `.go`, `.java`, `.cs`, `.rb`, `.php`, `.kt`, `.swift`, `.cpp`, `.c`); count files per extension; identify primary language in source dirs; identify secondary languages in scripts, tests, or tools. |
| Multi-language patterns | Check for polyglot layout, FFI/bindings, generated code (`protobuf`, GraphQL codegen, ORM models), and DSLs (SQL, templates, config schemas). |
| Explicit docs | Read `README.md`; inspect `docs/`; look for architecture docs (`ARCHITECTURE.md`, `ADR/`, decisions); API docs (`openapi.yml`, `swagger.json`, Postman); inline docs (docstrings, JSDoc, rustdoc). |
| Implicit docs | Analyze test names, type definitions, error messages, and log statements. |

## L2: Entry Point Analysis

**Goal**: understand where execution starts and how bootstrap reaches business logic.

| Area | Required checks |
|---|---|
| Main entry points | Search language-specific entry patterns: Go `func main()` in `main.go` / `cmd/*/main.go`; Python `if __name__ == "__main__"` or `__main__.py`; Node.js `main` in `package.json`, `index.js`, `app.js`, `server.js`; Java `public static void main` or `@SpringBootApplication`; Rust `fn main()` in `src/main.rs` or `src/bin/`; C# `static void Main` or `Program.cs`; Ruby script files, `config.ru`, `Rakefile`. |
| Multiple entry points | Check for CLI subcommands or multiple binaries, workers/background jobs, scheduled tasks, event handlers/webhooks/serverless functions, and migration scripts. |
| HTTP entry points | Find route definitions; list endpoints with methods; identify middleware chains (auth, logging, rate limiting); map URL patterns to handlers. |
| Event entry points | Find queue consumers, event listeners, scheduled jobs, file watchers, and stream processors. |
| CLI entry points | Find command definitions (`argparse`, `cobra`, `clap`, `commander`), list commands/subcommands, identify hierarchy. |
| Bootstrap sequence | Trace entry point to first business logic; identify config loading, DI/service container setup, DB connection init, external client init, middleware/interceptor registration, and initialization-order dependencies. |

## L3: Structural Decomposition

**Goal**: understand how code is grouped and what each unit owns.

| Area | Required checks |
|---|---|
| Architecture pattern | Identify the dominant pattern: Layered, Hexagonal / Ports & Adapters, Clean Architecture, Microservices, Monolith, Modular Monolith, Event-Driven, or Serverless. |
| Module boundaries | Identify top-level modules/packages; map each module responsibility in one sentence; identify module dependencies; check for circular deps; identify shared/common modules; identify vendor or third-party wrappers. |
| Grouping strategy | Determine whether code is grouped by layer, spec/feature, domain, or a hybrid. |
| File organization | Identify naming patterns; file-per-class vs file-per-module usage; index/barrel files; test file locations (adjacent, separate, nested). |
| Core components | For each module, record module name/location, primary responsibility, public interface, key dependencies, persistence involvement, and external integrations. |
| Cross-cutting components | Identify logging, error handling, configuration management, security/authentication, caching, and validation infrastructure. |

## L4: Data Flow Tracing

**Goal**: explain how requests, commands, or events transform data.

| Area | Required checks |
|---|---|
| Representative flows | Trace `3-5` operations from entry point through input validation/transformation, business logic, persistence, external calls, response construction, and error paths. |
| Data transformations | For each traced flow, record input shape, intermediate shapes, output shape, and side effects (what persists, what notifies). |
| Domain entities | Identify core entities; for each, record definition location, key attributes, relationships, invariants/validation rules, and lifecycle states if stateful. |
| DTOs | Identify request/response DTO patterns, DTO-to-entity transformations, serialization formats (`JSON`, `protobuf`, `XML`), and versioning patterns. |
| Storage technologies | Identify databases, file storage, caches, and search indices. |
| Data access patterns | Identify ORM/query builders, raw SQL, repository/DAO patterns, database migrations (location/tool), and seed data (location/format). |

## L5: Dependency Mapping

**Goal**: make dependency direction and replaceability visible.

| Area | Required checks |
|---|---|
| Internal dependency graph | Build the module import graph; identify acyclic core, hubs, leaf modules, and whether dependency direction is inverted (lower layers depending on higher layers). |
| Dependency injection | Identify DI container/framework, service registration patterns, injection style (constructor/property/method), and interface-to-implementation bindings. |
| Third-party libraries | List direct dependencies from the package manager; categorize by framework, database/ORM, HTTP client, serialization, validation, testing, and utilities; identify critical dependencies, outdated/deprecated dependencies, and security vulnerabilities. |
| External services | Identify external API calls; for each service record name/purpose, client location, authentication method, error handling, and retry/resilience patterns. |

## L6: State Management Analysis

**Goal**: explain where state lives and how it changes.

| Area | Required checks |
|---|---|
| In-memory state | Identify singleton/global state, request-scoped state, cached state, and runtime configuration state. |
| State lifecycle | Explain how state is initialized, accessed, modified (mutation vs immutable updates), and invalidated/cleared. |
| Database state | Record schema definition location, migration history, index definitions, constraint definitions, and trigger/stored-procedure usage. |
| State machines | Identify stateful entities (`status` fields, enums); record valid states, allowed transitions, transition triggers, and transition side effects. |
| Session/user state | Record where session state is stored (cookie, JWT, server), what data is stored, and how expiration/cleanup works. |
| Distributed coordination | Check for distributed locks, leader election, distributed caching, and event-sourcing / CQRS patterns. |

## L7: Integration Boundary Scan

**Goal**: map inbound, outbound, and infrastructure boundaries.

| Area | Required checks |
|---|---|
| Inbound boundaries | Catalog public APIs (HTTP REST, GraphQL, gRPC, WebSocket, webhook receivers), internal APIs (service-to-service, admin/management, health/metrics), and async inputs (queue consumers, event subscribers, scheduled jobs, file watchers). |
| External APIs | For each external API record service name/purpose, base URL config, auth/authz, request/response formats, timeout config, retry policy, circuit breaker presence, and fallback behavior. |
| Database connections | For each database record type/version, connection string location, pool config, read/write split, and replica usage. |
| External outputs | Identify queue publishing, email/SMS sending, file storage writes, and outbound notification webhooks. |
| Runtime boundary | Record container base image, runtime config, environment variables, and secrets management. |
| Network boundary | Record port bindings, host configuration, TLS/SSL setup, and proxy configuration. |

## L8: Pattern Recognition

**Goal**: identify conventions and repeated implementation idioms.

| Area | Required checks |
|---|---|
| Creational patterns | Factory patterns, Builder patterns, Singleton patterns, dependency injection patterns. |
| Structural patterns | Adapter/wrapper patterns, Decorator patterns, Facade patterns, Proxy patterns. |
| Behavioral patterns | Strategy patterns, Observer patterns, Command patterns, State patterns. |
| Naming conventions | Variable naming, function naming, class/type naming, file naming, directory naming. |
| Code style | Indentation, line-length limits, import organization, comment style, documentation format. |
| Error handling conventions | Exception vs result types, error message format, error code patterns, logging on errors, propagation strategy. |
| Test organization | Test file location, naming convention, test structure (`describe/it`, `given/when/then`, `arrange/act/assert`), setup/teardown, fixture patterns. |
| Test types | Unit, integration, E2E, test data management, mocking/stubbing patterns. |

## L9: Knowledge Synthesis

**Goal**: turn findings into reusable knowledge.

| Output | Required content |
|---|---|
| System overview paragraph | Primary purpose, key technologies, architectural style, major components, and primary data flows. |
| Component map | All major components, relationships, data-flow directions, and integration points. |
| Domain model summary | Entities with one-line descriptions, relationship summary, and key business rules/invariants. |
| Key operations | Critical business operations, operation-to-entry-point mapping, and data-flow summary for each. |
| Technical debt & risks | Circular dependencies, overly complex modules, inconsistent patterns, missing error handling, security concerns, performance concerns. |
| Knowledge gaps | Areas not fully understood, missing docs, unclear business logic, untested code paths. |
| Developer entry points | Where to start reading, key files first, critical abstractions, common modification patterns. |
| Operations entry points | Deployment process, configuration options, monitoring/alerting setup, troubleshooting guides. |

## Execution Protocol

**Before starting**: confirm source access, search capability, read permissions, and optionally local-run access or a running instance.

**Order**: execute layers `1 -> 9`, checkpoint after each layer, and carry findings forward.

**Time box by project size**:

| Project Size | L1-L2 | L3-L4 | L5-L7 | L8-L9 |
|---|---|---|---|---|
| Small (`< 10k LOC`) | 15 min | 30 min | 30 min | 15 min |
| Medium (`10k-100k`) | 30 min | 1 hr | 1 hr | 30 min |
| Large (`> 100k`) | 1 hr | 2 hr | 2 hr | 1 hr |

**Required output artifacts**: `System Overview` (max `1` page: purpose, tech stack, architecture style, key components and relationships), `Domain Model`, `Entry Points Catalog`, `Integration Map`, `Conventions Guide`, and `Technical Debt List`.

**Applicability**: greenfield validation before implementation; brownfield understanding before modification; acquisitions/transfers for due diligence and onboarding; legacy modernization to find strangler boundaries; documentation generation as input to Cypilot artifacts.

**Integration with Cypilot**: Adapter workflow uses L1-L3 for project scan; Generate workflow uses all layers for artifact creation; Validate workflow uses L4-L7 for traceability verification.

## Error Handling

| Condition | Response | Action |
|---|---|---|
| Repository access failed | `Repository access failed: {error}`; check file permissions, verify the path exists, confirm VCS access. | **STOP** — source access is required. |
| Layer incomplete | `Layer {N} incomplete: {reason}`; record completed items, skipped items, and blocker. | Document gaps explicitly and continue with caveat. |
| External dependencies unavailable | `External dependency unavailable: {service}`; note unverifiable integration patterns, auth, and data formats; mark boundary `UNVERIFIED`. | **WARN** and continue as a knowledge gap. |
| Large codebase timeout | `Time box exceeded for Layer {N}`; record completion percentage and whether to resume later or proceed with partial findings. | Save a checkpoint, note incompleteness, proceed. |
| Obfuscated/generated code | `Obfuscated/generated code detected: {location}`; skip generated output and analyze source templates/generators instead. | Analyze generators/templates, not generated output. |

## Consolidated Validation Checklist

**Use this single checklist for all reverse-engineering validation.**

### Surface Analysis (L1-L2)

| # | Check | Required | How to Verify |
|---|---|---|---|
| `L1.1` | Repository structure documented | YES | Directory tree captured |
| `L1.2` | Primary language identified | YES | File-extension counts analyzed |
| `L1.3` | Documentation inventory complete | YES | `README`, `docs/`, `ADR`s listed |
| `L2.1` | Main entry points identified | YES | Entry files/functions listed |
| `L2.2` | Bootstrap sequence traced | YES | Initialization order documented |

### Structural Analysis (L3-L4)

| # | Check | Required | How to Verify |
|---|---|---|---|
| `L3.1` | Architecture pattern identified | YES | Pattern named with evidence |
| `L3.2` | Module boundaries mapped | YES | Modules listed with responsibilities |
| `L3.3` | Component inventory complete | YES | Core + cross-cutting components listed |
| `L4.1` | Representative flows traced | YES | `3-5` flows documented entry-to-exit |
| `L4.2` | Domain entities identified | YES | Entities with attributes listed |
| `L4.3` | Persistence layer documented | YES | Storage technologies and patterns noted |

### Dependency Analysis (L5-L6)

| # | Check | Required | How to Verify |
|---|---|---|---|
| `L5.1` | Module dependency graph built | YES | Import relationships mapped |
| `L5.2` | External dependencies cataloged | YES | Libraries categorized by purpose |
| `L5.3` | External services documented | YES | API calls with auth/error handling noted |
| `L6.1` | Application state locations identified | YES | Global, request-scoped, cached state listed |
| `L6.2` | State machines documented | CONDITIONAL | If stateful entities exist, transitions mapped |
| `L6.3` | Distributed state patterns noted | CONDITIONAL | If distributed, coordination mechanisms listed |

### Integration Analysis (L7-L8)

| # | Check | Required | How to Verify |
|---|---|---|---|
| `L7.1` | Inbound boundaries cataloged | YES | APIs, consumers, triggers listed |
| `L7.2` | Outbound boundaries cataloged | YES | External calls, databases, outputs listed |
| `L7.3` | Infrastructure boundaries noted | YES | Container, network, secrets documented |
| `L8.1` | Code patterns identified | YES | Creational, structural, behavioral patterns listed |
| `L8.2` | Project conventions documented | YES | Naming, style, error-handling patterns noted |
| `L8.3` | Testing conventions documented | YES | Test organization and patterns noted |

### Synthesis (L9)

| # | Check | Required | How to Verify |
|---|---|---|---|
| `L9.1` | System overview produced | YES | Single-paragraph description complete |
| `L9.2` | Component map produced | YES | Visual or textual map created |
| `L9.3` | Domain model summarized | YES | Entities and relationships listed |
| `L9.4` | Technical debt identified | YES | Issues and risks documented |
| `L9.5` | Knowledge gaps listed | YES | Unclear areas explicitly noted |
| `L9.6` | Entry points summary for developers | YES | Where to start reading documented |

### Final (F)

| # | Check | Required | How to Verify |
|---|---|---|---|
| `F.1` | All Surface Analysis checks pass | YES | `L1.1-L2.2` verified |
| `F.2` | All Structural Analysis checks pass | YES | `L3.1-L4.3` verified |
| `F.3` | All Dependency Analysis checks pass | YES | `L5.1-L6.3` verified, conditionals where applicable |
| `F.4` | All Integration Analysis checks pass | YES | `L7.1-L8.3` verified |
| `F.5` | All Synthesis checks pass | YES | `L9.1-L9.6` verified |
| `F.6` | Output artifacts produced | YES | Six artifacts from Execution Protocol created |

## References

- Generate workflow: `{cypilot_path}/.core/workflows/generate.md`
- Execution protocol: `{cypilot_path}/.core/requirements/execution-protocol.md`
