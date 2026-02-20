# ADR-0001: Use CLI daemon + LaunchAgent (no menubar UI)

**ID**: `cpt-ex-ovwa-adr-cli-daemon-launchagent-no-menubar`

## Context and Problem Statement

Overwork Alert is a minimal macOS example tool intended to demonstrate an end-to-end Cypilot SDLC chain inside this repository. The tool must run continuously, track active work time (idle-aware), and notify the user when their configured limit is exceeded.

We need an execution model that supports background operation and simple user controls (status/pause/resume/reset) with low implementation complexity. The v1 scope explicitly excludes a menubar UI.

## Decision Drivers

* Keep v1 implementation small and easy to reason about.
* Prefer local-only integration points and minimal runtime dependencies.
* Support continuous background operation with optional autostart on login.
* Avoid UI-specific complexity (app lifecycle, menubar UI, packaging/signing).

## Considered Options

* Menubar application
* CLI daemon + LaunchAgent (chosen)
* Scheduled launchd job (periodic execution)

## Decision Outcome

Chosen option: "CLI daemon + LaunchAgent", because it provides continuous background tracking and optional autostart while keeping the example small, local-first, and traceability-friendly.

### Consequences

* Good, because the implementation remains small and repository-friendly.
* Good, because it creates a clean separation between user-facing CLI controls and the background tracking loop.
* Bad, because the UX is less discoverable than a menubar app.
* Bad, because it requires defining and implementing a local control channel between CLI and daemon.

### Confirmation

This ADR is confirmed when:

* The system can start the daemon via CLI and keep it running in background.
* Autostart can be installed/uninstalled idempotently.
* CLI control flows (status/pause/resume/reset/stop) work through a local-only channel.

## Pros and Cons of the Options

### Menubar application

Description: Implement Overwork Alert as a native menubar app that owns the tracker loop and provides controls directly in a UI.

* Good, because it provides best UX and discoverability.
* Good, because it is a natural place to show status and quick actions.
* Bad, because it requires UI lifecycle, packaging, and potentially signing/notarization considerations.
* Bad, because it adds significant complexity for a minimal example.

### CLI daemon + LaunchAgent (chosen)

Description: Provide a CLI that can start a long-running background process (daemon loop) and optionally install a LaunchAgent for autostart.

* Good, because it has minimal surface area and dependencies.
* Good, because it fits a repository-local example and is easy to iterate on.
* Good, because CLI commands map cleanly to FEATURE flows and code markers.
* Bad, because it is less discoverable and less polished UX than a menubar app.
* Bad, because it requires a control channel between CLI and daemon.

### Scheduled launchd job (periodic execution)

Description: Use a LaunchAgent to run a short-lived command on a schedule that checks whether the user is over the limit.

* Good, because it is a very simple process model.
* Good, because there is no long-running daemon.
* Bad, because it has weaker real-time behavior and less accurate active-time tracking.
* Bad, because it is harder to provide responsive pause/resume/status controls.

## More Information

**Date**: 2026-02-06

**Status**: Accepted

## Traceability

- **PRD**: [PRD.md](../../PRD.md)
- **DESIGN**: [DESIGN.md](../../DESIGN.md)

This decision directly addresses the following requirements:

* `cpt-ex-ovwa-fr-autostart` — Autostart requirement influenced the use of LaunchAgent.
* `cpt-ex-ovwa-fr-cli-controls` — CLI control requirements influenced the CLI/daemon approach.

