<!-- cpt:#:adr -->
# ADR-0001: Use CLI daemon + LaunchAgent (no menubar UI)

<!-- cpt:id:adr has="priority,task" covered_by="DESIGN" -->
- [x] `p1` - **ID**: `cpt-overwork-alert-adr-cli-daemon-launchagent-no-menubar`

<!-- cpt:##:meta -->
## Meta

<!-- cpt:paragraph:adr-title -->
**Title**: ADR-0001 Use CLI daemon + LaunchAgent (no menubar UI)
<!-- cpt:paragraph:adr-title -->

<!-- cpt:paragraph:date -->
**Date**: 2026-02-06
<!-- cpt:paragraph:date -->

<!-- cpt:paragraph:status -->
**Status**: Accepted
<!-- cpt:paragraph:status -->
<!-- cpt:##:meta -->

<!-- cpt:##:body -->
## Body

<!-- cpt:context -->
**Context**:
Overwork Alert is a minimal macOS example tool intended to demonstrate an end-to-end Cypilot SDLC chain inside this repository. The tool must run continuously, track active work time (idle-aware), and notify the user when their configured limit is exceeded.

We need an execution model that supports background operation and simple user controls (status/pause/resume/reset) with low implementation complexity. The v1 scope explicitly excludes a menubar UI.
<!-- cpt:context -->

<!-- cpt:decision-drivers -->
**Decision Drivers**:
- Keep v1 implementation small and easy to reason about.
- Prefer local-only integration points and minimal runtime dependencies.
- Support continuous background operation with optional autostart on login.
- Avoid UI-specific complexity (app lifecycle, menubar UI, packaging/signing).
<!-- cpt:decision-drivers -->

<!-- cpt:options repeat="many" -->
**Option 1: Menubar application**

- Description: Implement Overwork Alert as a native menubar app that owns the tracker loop and provides controls directly in a UI.
- Pros:
  - Best user experience and discoverability.
  - Natural place to show status and quick actions.
- Cons:
  - Requires UI lifecycle, packaging, and potentially signing/notarization considerations.
  - Adds significant complexity for a minimal example.
- Trade-offs: Better UX at the cost of increased implementation and distribution complexity.
<!-- cpt:options repeat="many" -->

<!-- cpt:options repeat="many" -->
**Option 2: CLI daemon + LaunchAgent (chosen)**

- Description: Provide a CLI that can start a long-running background process (daemon loop) and optionally install a LaunchAgent for autostart.
- Pros:
  - Minimal surface area and dependencies.
  - Fits a repository-local example and is easy to iterate on.
  - Works well with Cypilot traceability (CLI commands map cleanly to specs).
- Cons:
  - Less discoverable and less polished UX than a menubar app.
  - Requires a control channel between CLI and daemon.
- Trade-offs: Simplicity and maintainability over UI-driven convenience.
<!-- cpt:options repeat="many" -->

<!-- cpt:options repeat="many" -->
**Option 3: Scheduled launchd job (periodic execution)**

- Description: Use a LaunchAgent to run a short-lived command on a schedule that checks whether the user is over the limit.
- Pros:
  - Very simple process model.
  - No long-running daemon.
- Cons:
  - Weaker real-time behavior and less accurate active-time tracking.
  - Harder to provide responsive pause/resume/status controls.
- Trade-offs: Reduced complexity at the cost of accuracy and responsiveness.
<!-- cpt:options repeat="many" -->

<!-- cpt:decision-outcome -->
**Decision Outcome**:
Chosen option: **Option 2 (CLI daemon + LaunchAgent)**.

This option best fits the goals of a small, local-first example: it supports continuous background operation and autostart without adding UI concerns. It also keeps the implementation straightforward and easy to connect to PRD requirements and downstream specs.
<!-- cpt:decision-outcome -->

<!-- cpt:list:consequences -->
- Positive: Implementation remains small and repository-friendly.
- Positive: Clear separation between CLI controls and the background tracking loop.
- Negative: User experience is less discoverable than a menubar app.
- Negative: Requires defining a local control interface (e.g., a local socket or similar).
- Follow-up: Reference this ADR from the system DESIGN and define the control contract at a high level.
<!-- cpt:list:consequences -->

<!-- cpt:list:links -->
- [`PRD`](../../PRD.md)
- [`DESIGN`](../../DESIGN.md)
- `cpt-overwork-alert-fr-autostart` — Autostart requirement influenced the use of LaunchAgent.
- `cpt-overwork-alert-fr-cli-controls` — CLI control requirements influenced the CLI/daemon approach.
<!-- cpt:list:links -->
<!-- cpt:##:body -->

<!-- cpt:id:adr -->
<!-- cpt:#:adr -->
