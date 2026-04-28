---
status: accepted
date: 2026-04-01
---

# ADR-0019: Structural Traceability Graph for Codebase Indexing


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [stdlib ast + custom TraceGraph + JSON cache](#stdlib-ast--custom-tracegraph--json-cache)
  - [tree-sitter + networkx + SQLite](#tree-sitter--networkx--sqlite)
  - [Content-hash anchoring + flat JSON](#content-hash-anchoring--flat-json)
  - [tree-sitter + custom graph + JSON](#tree-sitter--custom-graph--json)
- [More Information](#more-information)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-structural-traceability-graph`

## Context and Problem Statement

Current codebase indexing in Cypilot uses flat row dictionaries keyed by line number (`defs_by_id`, `refs_by_id`). This approach has three fundamental limitations: line-number keys break on any edit above the target line (fragility), the entire index must be rebuilt on every invocation (no incremental updates), and flat dictionaries cannot express or query relationships between code and documentation elements (no graph traversal). How should we restructure the indexing system to provide stable identity, incremental validation, and graph-based traceability queries while remaining stdlib-only?

## Decision Drivers

* Stable identity that survives refactoring (rename, move, reorder) without invalidating the index
* Incremental cache validation to avoid full rebuilds on every `cpt validate` invocation
* Graph-based queries for multi-hop traceability (e.g., "which code blocks implement this FR?")
* stdlib-only constraint (ADR-0002: zero external dependencies for pipx installability)
* Backward compatibility with existing consumers of the line-based index (`cross_validate_artifacts`, `cross_validate_code`)

## Considered Options

1. **stdlib ast + custom TraceGraph + JSON cache** (chosen)
2. **tree-sitter + networkx + SQLite**
3. **Content-hash anchoring + flat JSON**
4. **tree-sitter + custom graph + JSON** (hybrid)

## Decision Outcome

Chosen option: **stdlib ast + custom TraceGraph + JSON cache**, because it satisfies the stdlib-only constraint while providing structural anchoring, graph queries, and incremental validation. The approach uses Python's built-in `ast` module for structural parsing of `.py` files, a custom dual adjacency-list `TraceGraph` class for graph operations, and JSON for cache persistence. A shadow-then-replace migration strategy ensures backward compatibility. The 4-phase implementation (structural anchoring, incremental cache, traceability graph, session sync) allows incremental delivery with each phase independently valuable.

### Consequences

* Good, because stable identity (heading-tree paths for docs, AST container paths for code) survives refactoring
* Good, because incremental cache validation (mtime + content hash) avoids full index rebuilds
* Good, because graph queries enable multi-hop traceability between code and documentation anchors
* Good, because zero external dependencies maintains pipx installability per ADR-0002
* Good, because shadow-then-replace migration ensures safe rollback to line-based index if issues arise
* Bad, because stdlib `ast` is limited to Python; other languages get only regex-based container detection
* Bad, because JSON cache is less performant than SQLite for repositories with 10,000+ files
* Bad, because custom `TraceGraph` requires more implementation and testing effort than adopting networkx

### Confirmation

Confirmed when:

- `TraceGraph` class passes unit tests for node/edge CRUD and all query operations (forward/reverse traversal, affected-by-change)
- JSON cache round-trips correctly with structural anchors and content hashes
- Shadow index produces identical validation results to the existing line-based index for all current test cases
- `ast`-based anchoring correctly resolves enclosing function/class for `@cpt-` markers in Python files
- Incremental index correctly identifies changed files and re-parses only those files

## Pros and Cons of the Options

### stdlib ast + custom TraceGraph + JSON cache

Use Python `ast` module for structural anchoring in `.py` files with regex fallback for other languages, a custom `TraceGraph` class with dual adjacency lists for graph operations, JSON for cache persistence, and shadow-then-replace migration for backward compatibility.

* Good, because `ast` is stdlib (no dependencies) and provides reliable structural parsing for Python
* Good, because custom graph class can be optimized for the specific 5 node types and 4 edge types needed
* Good, because JSON cache is human-readable, diffable, and easy to debug
* Good, because shadow-then-replace migration is safe and allows incremental validation
* Neutral, because regex fallback for non-Python languages provides basic but limited container detection
* Bad, because `ast` only works for Python files; adding new language support requires individual parsers
* Bad, because JSON serialization/deserialization is slower than SQLite for large datasets

### tree-sitter + networkx + SQLite

Use tree-sitter for multi-language AST parsing, networkx for graph operations, and SQLite for cache persistence.

* Good, because tree-sitter supports 130+ languages out of the box
* Good, because networkx provides mature, tested graph algorithms (PageRank, shortest path, cycle detection)
* Good, because SQLite provides efficient indexed queries and concurrent access
* Bad, because tree-sitter, networkx, and sqlite3 bindings are external dependencies violating ADR-0002
* Bad, because tree-sitter requires per-language grammar binaries (50+ MB for common languages)
* Bad, because networkx API surface is much larger than needed for the 4-5 specific queries required

### Content-hash anchoring + flat JSON

Use content hashing (SHA-256) without AST parsing for identity, keeping the flat dictionary structure but replacing line-number keys with content-hash keys.

* Good, because simplest implementation with minimal code changes
* Good, because content hashes detect changes accurately without parsing
* Good, because flat structure is familiar and backward-compatible
* Bad, because no structural information (cannot determine enclosing function/class)
* Bad, because hash collisions across unrelated blocks could cause false matches
* Bad, because no graph queries; flat structure cannot express containment or traceability relationships

### tree-sitter + custom graph + JSON

Use tree-sitter for multi-language AST parsing with a custom graph class and JSON cache. A hybrid approach combining the best language coverage with stdlib-compatible graph and cache.

* Good, because tree-sitter provides structural anchoring for all languages
* Good, because custom graph avoids the networkx dependency
* Good, because JSON cache avoids the SQLite dependency
* Bad, because tree-sitter itself is still an external dependency violating ADR-0002
* Bad, because tree-sitter grammar binaries add significant distribution weight
* Neutral, because this option would be reconsidered if ADR-0002 is ever relaxed

## More Information

* GitHub Issue: [#132 — Smart codebase indexing: structural traceability graph instead of row/line-based index](https://github.com/cyberfabric/cyber-pilot/issues/132)
* Related: ADR-0002 (`cpt-cypilot-adr-python-stdlib-only`) constrains all dependencies to the Python standard library
* Related: Aider's repomap uses tree-sitter + PageRank for context selection (different goal but validates AST-based approach)
* Market context: No existing tool (CodeScene, Augment, Qodo, Sourcegraph) provides spec-to-code traceability at the source code level; this is Cypilot's unique differentiator

## Traceability

- **PRD**: [PRD.md](../PRD.md)

This decision directly addresses the following requirements:

* `cpt-cypilot-fr-structural-anchoring` — structural anchoring and content hashing (P1) require AST-based parsing and hash computation
* `cpt-cypilot-fr-incremental-index` — incremental diff-aware index (P2) requires the JSON cache format decision
* `cpt-cypilot-fr-traceability-graph` — traceability graph (P3) requires the custom TraceGraph class decision
* `cpt-cypilot-fr-session-sync` — real-time session sync (P4) builds on the incremental index and graph infrastructure
