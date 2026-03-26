# Phase 1 Message Priority Order

## Rollout rule

Later phases must enable diagnostics strictly in the order defined below. A later phase must not enable out-of-order diagnostics from a lower-priority phase, even if the implementation looks convenient.

## Authoritative priority order

### Phase 2 — Critical runtime errors

Priority: P0

Enable only:

- `E0602`
- `E1135`
- `E0102`

Rule:

- Phase 2 must not enable any `W*`, `R*`, or `C*` diagnostics.

### Phase 3 — High-risk warnings

Priority: P1

Enable only:

- `W0718`
- `W1510`
- `W0707`
- `W0404`
- `W0212`
- `W0603`
- `W0612`
- `W0613`
- `W0611`

Rule:

- Phase 3 may assume Phase 2 diagnostics remain enabled.
- Phase 3 must not enable any `R*` or `C*` diagnostics.

### Phase 4 — Control-flow hotspots I

Priority: P2

Enable only:

- `R0914`
- `R0912`
- `R0915`

Rule:

- Phase 4 may keep earlier enabled P0-P1 diagnostics active.
- Phase 4 must not enable any P3-P6 diagnostics.

### Phase 5 — Control-flow hotspots II

Priority: P3

Enable only:

- `R0911`
- `R1702`
- `R1705`
- `R0913`
- `R0917`
- `R0902`

Rule:

- Phase 5 may keep earlier enabled P0-P2 diagnostics active.
- Phase 5 must not enable any P4-P6 diagnostics.

### Phase 6 — Architecture and duplication hygiene

Priority: P4

Enable only:

- `R0401`
- `R0801`

Rule:

- Phase 6 may keep earlier enabled P0-P3 diagnostics active.
- Phase 6 must not enable any P5-P6 diagnostics.

### Phase 7 — Import and format normalization

Priority: P5

Enable only:

- `C0415`
- `C0413`
- `C0411`
- `C0414`
- `C0301`
- `C0302`
- `C0303`
- `C0305`

Rule:

- Phase 7 may keep earlier enabled P0-P4 diagnostics active.
- Phase 7 must not enable any P6 diagnostics.

### Phase 8 — Naming, docstrings, and steady-state

Priority: P6

Enable only:

- `C0103`
- `C0114`
- `C0115`
- `C0116`

Rule:

- Phase 8 may keep earlier enabled P0-P5 diagnostics active.
- Phase 8 completes the staged rollout.

## Deterministic enablement policy

- Use explicit message IDs or tightly-coupled families only.
- Do not replace this order with broad category enables.
- Do not bypass `make pylint`.
- Do not change lint targets away from:
  - `src/cypilot_proxy`
  - `skills/cypilot/scripts/cypilot`
- When a phase is complete, the next phase may extend the enabled set only with that phase's assigned diagnostics.
