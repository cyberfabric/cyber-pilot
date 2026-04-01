# Feature: Smart Codebase Indexing


<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1. Overview](#1-overview)
  - [2. Purpose](#2-purpose)
  - [3. Actors](#3-actors)
  - [4. References](#4-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Build Structural Index](#build-structural-index)
  - [Incremental Validation](#incremental-validation)
  - [Query Traceability Graph](#query-traceability-graph)
  - [Session Sync](#session-sync)
- [3. Processes / Business Logic (CDSL)](#3-processes--business-logic-cdsl)
  - [Compute Structural Anchor](#compute-structural-anchor)
  - [Compute Content Hash](#compute-content-hash)
  - [Build/Update Index Cache](#buildupdate-index-cache)
  - [Build Trace Graph](#build-trace-graph)
  - [Detect Affected Nodes](#detect-affected-nodes)
  - [Session File Watcher](#session-file-watcher)
- [4. States (CDSL)](#4-states-cdsl)
  - [Index Lifecycle](#index-lifecycle)
- [5. Definitions of Done](#5-definitions-of-done)
  - [Structural Anchoring](#structural-anchoring)
  - [Incremental Index](#incremental-index)
  - [Traceability Graph](#traceability-graph)
  - [Session Sync](#session-sync-1)
- [6. Implementation Modules](#6-implementation-modules)
- [7. Acceptance Criteria](#7-acceptance-criteria)

<!-- /toc -->

- [ ] `p1` - **ID**: `cpt-cypilot-featstatus-smart-indexing`

## 1. Feature Context

- [ ] `p1` - `cpt-cypilot-feature-smart-indexing`

### 1. Overview

Smart codebase indexing replaces fragile line-number-based references with structural anchors (heading-tree paths for docs, AST container paths for `.py` code), provides content-hash-based change detection, maintains a persistent incremental index, builds a queryable traceability graph, and keeps the index synchronized with the filesystem in real time. All modules are stdlib-only.

### 2. Purpose

Addresses PRD requirements for structural anchoring (`cpt-cypilot-fr-structural-anchoring`), incremental indexing (`cpt-cypilot-fr-incremental-index`), traceability graph (`cpt-cypilot-fr-traceability-graph`), and session sync (`cpt-cypilot-fr-session-sync`). Extends the existing traceability-validation feature with persistent indexing and graph capabilities.

### 3. Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Invokes indexing, graph query, and session sync commands from CLI |
| `cpt-cypilot-actor-ai-agent` | Triggers indexing after artifact/code generation; uses graph queries for navigation |

### 4. References

- **PRD**: [PRD.md](../PRD.md)
- **ADR**: [ADR-0019](../ADR/0019-cpt-cypilot-adr-structural-traceability-graph-v1.md)
- **Dependencies**: [traceability-validation](traceability-validation.md) (validation pipeline this feature extends)

## 2. Actor Flows (CDSL)

### Build Structural Index

- [ ] `p1` - **ID**: `cpt-cypilot-flow-smart-indexing-build-index`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- Full index built from scratch for a project with artifacts and code files

**Error Scenarios**:
- File read failure (permission denied, encoding error) — skip file and report warning

**Steps**:
1. [ ] - `p1` - Actor invokes build-index command on project root - `inst-invoke-build`
2. [ ] - `p1` - Discover all artifact files from registry and all code files from codebase entries - `inst-discover-files`
3. [ ] - `p1` - **FOR EACH** artifact file: compute heading-tree anchors using markdown heading parser - `inst-anchor-docs`
4. [ ] - `p1` - **FOR EACH** `.py` code file: compute AST container paths using `ast.parse()` - `inst-anchor-code-py`
5. [ ] - `p1` - **FOR EACH** non-`.py` code file: compute container paths using regex fallback - `inst-anchor-code-other`
6. [ ] - `p1` - **FOR EACH** file with `@cpt-` blocks: compute SHA-256 content hash per block - `inst-hash-blocks`
7. [ ] - `p1` - Persist index to `.cypilot-cache/trace-index.json` - `inst-persist-index`
8. [ ] - `p1` - **RETURN** index summary (file count, anchor count, hash count) - `inst-return-summary`

### Incremental Validation

- [ ] `p2` - **ID**: `cpt-cypilot-flow-smart-indexing-incremental-update`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- Only changed files re-indexed; unchanged files skipped

**Error Scenarios**:
- Cache missing or corrupt — fall back to full rebuild

**Steps**:
1. [ ] - `p1` - Actor invokes incremental update - `inst-invoke-incremental`
2. [ ] - `p1` - Load existing index cache from `.cypilot-cache/trace-index.json` - `inst-load-cache`
3. [ ] - `p1` - **IF** cache missing or corrupt: fall back to full build-index flow - `inst-fallback-full`
4. [ ] - `p1` - Detect changed files via mtime comparison against cache - `inst-detect-mtime`
5. [ ] - `p1` - Optionally narrow stale set using `git diff --name-only` - `inst-git-narrow`
6. [ ] - `p1` - **FOR EACH** stale file: re-compute anchors and hashes - `inst-reparse-stale`
7. [ ] - `p1` - Remove entries for deleted files - `inst-remove-deleted`
8. [ ] - `p1` - Persist updated index - `inst-persist-updated`
9. [ ] - `p1` - **RETURN** update summary (files re-indexed, files removed, files unchanged) - `inst-return-update`

### Query Traceability Graph

- [ ] `p3` - **ID**: `cpt-cypilot-flow-smart-indexing-query-graph`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- Graph query returns correct affected nodes for a given file change

**Error Scenarios**:
- Index not yet built — prompt user to run build-index first

**Steps**:
1. [ ] - `p3` - Actor invokes graph query (affected-by-change, where-used, or where-defined) - `inst-invoke-query`
2. [ ] - `p3` - Load index and build TraceGraph if not already in memory - `inst-load-graph`
3. [ ] - `p3` - **IF** index not found: **RETURN** error prompting build-index - `inst-no-index-error`
4. [ ] - `p3` - Execute query using TraceGraph traversal methods - `inst-execute-query`
5. [ ] - `p3` - **RETURN** query results (list of affected node IDs with edge paths) - `inst-return-results`

### Session Sync

- [ ] `p4` - **ID**: `cpt-cypilot-flow-smart-indexing-session-sync`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- File changes detected within one poll interval; stale notifications pushed

**Error Scenarios**:
- Polling interrupted — clean exit with final sync

**Steps**:
1. [ ] - `p4` - Actor starts session sync mode with configurable poll interval (default 2s) - `inst-start-session`
2. [ ] - `p4` - Load or build index and graph - `inst-load-session-index`
3. [ ] - `p4` - Record mtime snapshot for all watched files - `inst-snapshot-mtime`
4. [ ] - `p4` - **FOR EACH** poll cycle: compare current mtime to snapshot - `inst-poll-changes`
5. [ ] - `p4` - **IF** change detected: emit stale notification with file path and affected IDs - `inst-emit-stale`
6. [ ] - `p4` - Trigger incremental graph refresh for changed files - `inst-refresh-graph`
7. [ ] - `p4` - Update mtime snapshot - `inst-update-snapshot`
8. [ ] - `p4` - **IF** session end signal received: **RETURN** session summary - `inst-end-session`

## 3. Processes / Business Logic (CDSL)

### Compute Structural Anchor

- [ ] `p1` - **ID**: `cpt-cypilot-algo-smart-indexing-compute-anchor`

**Input**: File path, file content, file type (doc or code)

**Output**: List of structural anchors with positions

**Steps**:
1. [ ] - `p1` - **IF** file is `.md`: parse heading hierarchy using regex heading detection - `inst-parse-headings`
2. [ ] - `p1` - Build heading-tree path for each `@cpt-` ID by walking ancestor headings - `inst-build-heading-path`
3. [ ] - `p1` - **IF** file is `.py`: parse AST using `ast.parse()` to extract class/function nodes - `inst-parse-ast`
4. [ ] - `p1` - Map each `@cpt-` marker line to its enclosing class/function by comparing line ranges - `inst-map-containers`
5. [ ] - `p1` - **IF** file is other code: detect `def`/`function`/`class` patterns via regex - `inst-regex-fallback`
6. [ ] - `p1` - **RETURN** list of StructuralAnchor (heading_path or container, line, id) - `inst-return-anchors`

### Compute Content Hash

- [ ] `p1` - **ID**: `cpt-cypilot-algo-smart-indexing-compute-hash`

**Input**: File content, list of `@cpt-` block boundaries (start_line, end_line)

**Output**: Dict mapping block ID to SHA-256 hex digest

**Steps**:
1. [ ] - `p1` - **FOR EACH** `@cpt-begin`/`@cpt-end` pair: extract content lines between markers - `inst-extract-content`
2. [ ] - `p1` - Normalize whitespace (strip trailing, normalize line endings) - `inst-normalize`
3. [ ] - `p1` - Compute SHA-256 hash of normalized content - `inst-compute-sha`
4. [ ] - `p1` - **RETURN** dict of {block_id: hex_digest} - `inst-return-hashes`

### Build/Update Index Cache

- [ ] `p2` - **ID**: `cpt-cypilot-algo-smart-indexing-manage-cache`

**Input**: File list, existing cache (optional)

**Output**: Updated IndexCache object

**Steps**:
1. [ ] - `p1` - **IF** no existing cache: initialize empty IndexCache - `inst-init-cache`
2. [ ] - `p1` - **FOR EACH** file in file list: compare mtime against cache entry - `inst-check-mtime`
3. [ ] - `p1` - **IF** mtime changed or no cache entry: re-compute anchors and hashes - `inst-recompute`
4. [ ] - `p1` - **IF** file deleted: remove entry from cache - `inst-remove-entry`
5. [ ] - `p1` - Serialize cache to JSON at `.cypilot-cache/trace-index.json` - `inst-serialize`
6. [ ] - `p1` - **RETURN** updated IndexCache - `inst-return-cache`

### Build Trace Graph

- [ ] `p3` - **ID**: `cpt-cypilot-algo-smart-indexing-build-graph`

**Input**: IndexCache with anchors, hashes, and references

**Output**: TraceGraph instance with dual adjacency lists

**Steps**:
1. [ ] - `p3` - Create nodes for each artifact file (type: ARTIFACT) - `inst-create-artifact-nodes`
2. [ ] - `p3` - Create nodes for each heading section (type: SECTION) with CONTAINS edges from artifact - `inst-create-section-nodes`
3. [ ] - `p3` - Create nodes for each ID definition (type: DEFINITION) with DEFINES edges from section - `inst-create-def-nodes`
4. [ ] - `p3` - Create nodes for each ID reference (type: REFERENCE) with REFERENCES edges to definition - `inst-create-ref-nodes`
5. [ ] - `p3` - Create nodes for each code block marker (type: CODE_BLOCK) with IMPLEMENTS edges to definition - `inst-create-code-nodes`
6. [ ] - `p3` - Build forward and reverse adjacency lists from all edges - `inst-build-adjacency`
7. [ ] - `p3` - **RETURN** TraceGraph instance - `inst-return-graph`

### Detect Affected Nodes

- [ ] `p3` - **ID**: `cpt-cypilot-algo-smart-indexing-detect-affected`

**Input**: Changed file path, TraceGraph

**Output**: List of affected node IDs with edge paths

**Steps**:
1. [ ] - `p3` - Find all nodes in graph belonging to the changed file - `inst-find-file-nodes`
2. [ ] - `p3` - **FOR EACH** node: traverse REFERENCES and IMPLEMENTS edges (reverse) to find dependents - `inst-traverse-reverse`
3. [ ] - `p3` - Collect unique set of affected nodes across all traversals - `inst-collect-affected`
4. [ ] - `p3` - **RETURN** affected nodes with edge paths (for display) - `inst-return-affected`

### Session File Watcher

- [ ] `p4` - **ID**: `cpt-cypilot-algo-smart-indexing-file-watcher`

**Input**: Watched file list, poll interval (seconds)

**Output**: List of StaleNotification objects

**Steps**:
1. [ ] - `p4` - Record initial mtime snapshot for all watched files - `inst-initial-snapshot`
2. [ ] - `p4` - **FOR EACH** poll cycle at configured interval - `inst-poll-loop`
3. [ ] - `p4` - **FOR EACH** file: compare current mtime to snapshot - `inst-compare-mtime`
4. [ ] - `p4` - **IF** mtime changed: create StaleNotification (file_path, old_hash, new_hash) - `inst-create-notification`
5. [ ] - `p4` - **RETURN** list of StaleNotification objects for this cycle - `inst-return-notifications`

## 4. States (CDSL)

### Index Lifecycle

- [ ] `p1` - **ID**: `cpt-cypilot-state-smart-indexing-index-lifecycle`

**States**: Fresh, Stale, Rebuilding, Ready

**Initial State**: Fresh

**Transitions**:
1. [ ] - `p1` - **FROM** Fresh **TO** Rebuilding **WHEN** build-index command invoked - `inst-fresh-to-rebuilding`
2. [ ] - `p1` - **FROM** Rebuilding **TO** Ready **WHEN** index build completes successfully - `inst-rebuilding-to-ready`
3. [ ] - `p1` - **FROM** Ready **TO** Stale **WHEN** file change detected (mtime divergence) - `inst-ready-to-stale`
4. [ ] - `p1` - **FROM** Stale **TO** Rebuilding **WHEN** incremental update triggered - `inst-stale-to-rebuilding`
5. [ ] - `p1` - **FROM** Rebuilding **TO** Stale **WHEN** build fails (partial update) - `inst-rebuilding-to-stale`
6. [ ] - `p1` - **FROM** Stale **TO** Rebuilding **WHEN** full rebuild requested - `inst-stale-full-rebuild`

## 5. Definitions of Done

### Structural Anchoring

- [ ] `p1` - **ID**: `cpt-cypilot-dod-smart-indexing-structural-anchoring`

The system **MUST** replace line-number references with heading-tree paths for `.md` files and AST container paths for `.py` files. The system **MUST** compute SHA-256 content hashes per `@cpt-` block.

**Implements**:
- `cpt-cypilot-flow-smart-indexing-build-index`
- `cpt-cypilot-algo-smart-indexing-compute-anchor`
- `cpt-cypilot-algo-smart-indexing-compute-hash`

**Covers**: `cpt-cypilot-fr-structural-anchoring`

### Incremental Index

- [ ] `p2` - **ID**: `cpt-cypilot-dod-smart-indexing-incremental-index`

The system **MUST** detect file changes via mtime and git diff, re-parse only stale files, and persist the index as JSON at `.cypilot-cache/trace-index.json`.

**Implements**:
- `cpt-cypilot-flow-smart-indexing-incremental-update`
- `cpt-cypilot-algo-smart-indexing-manage-cache`

**Covers**: `cpt-cypilot-fr-incremental-index`

### Traceability Graph

- [ ] `p3` - **ID**: `cpt-cypilot-dod-smart-indexing-traceability-graph`

The system **MUST** build a typed graph with nodes (Artifact, Section, Definition, Reference, CodeBlock) and edges (CONTAINS, DEFINES, REFERENCES, IMPLEMENTS), queryable via affected-by-change, where-used, and where-defined.

**Implements**:
- `cpt-cypilot-flow-smart-indexing-query-graph`
- `cpt-cypilot-algo-smart-indexing-build-graph`
- `cpt-cypilot-algo-smart-indexing-detect-affected`

**Covers**: `cpt-cypilot-fr-traceability-graph`

### Session Sync

- [ ] `p4` - **ID**: `cpt-cypilot-dod-smart-indexing-session-sync`

The system **MUST** watch files via mtime polling, emit stale notifications when content hashes diverge, and trigger incremental graph refresh.

**Implements**:
- `cpt-cypilot-flow-smart-indexing-session-sync`
- `cpt-cypilot-algo-smart-indexing-file-watcher`

**Covers**: `cpt-cypilot-fr-session-sync`

## 6. Implementation Modules

| Module | Purpose |
|--------|---------|
| `skills/cypilot/scripts/cypilot/utils/trace_graph.py` | TraceGraph class, StructuralAnchor, ContentFingerprint, AnchoredHit, IndexCache, SessionIndex |
| `skills/cypilot/scripts/cypilot/utils/document.py` | Extended with `scan_cpt_ids_anchored()` for heading-tree anchor computation |
| `skills/cypilot/scripts/cypilot/utils/codebase.py` | Extended with AST container detection and `content_fingerprints()` |
| `skills/cypilot/scripts/cypilot/utils/constraints.py` | Extended with `precomputed_hits` parameter and graph build integration |
| `skills/cypilot/commands/validate.py` | Extended with `--incremental`, `--graph`, `--watch` flags |

## 7. Acceptance Criteria

- [ ] Heading-tree anchors resolve correctly for nested markdown headings up to 6 levels
- [ ] AST container paths resolve correctly for Python classes, methods, nested functions, and module-level definitions
- [ ] Content hashes change when `@cpt-` block content changes and remain stable when surrounding code changes
- [ ] Incremental index re-parses only files with changed mtime (verified by counter)
- [ ] Index cache round-trips correctly: serialize to JSON, deserialize, produce identical anchors and hashes
- [ ] Full rebuild produces identical results to incremental rebuild from clean state
- [ ] Graph CONTAINS edges correctly model artifact -> section -> definition hierarchy
- [ ] Graph REFERENCES edges correctly link cross-artifact ID references to definitions
- [ ] Graph IMPLEMENTS edges correctly link code blocks to their specification definitions
- [ ] `affected-by-change` query returns all nodes reachable via reverse REFERENCES/IMPLEMENTS edges
- [ ] Session watcher detects file changes within one poll interval (configurable, default 2s)
- [ ] Stale notifications include file path, affected IDs, and affected files
- [ ] All modules use stdlib only (zero external dependencies)
- [ ] Existing `cpt validate` tests continue to pass unchanged (backward compatibility)
