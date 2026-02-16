# Feature: CLI Control

- [x] `p1` - **ID**: `cpt-overwork-alert-featstatus-cli-control`

- [x] - `cpt-overwork-alert-feature-cli-control`

## 1. Feature Context

### 1. Overview
This feature defines user-facing CLI controls and the local-only control channel contract between the CLI and the daemon. It covers status reporting, pause/resume, manual reset, and stop.

Key assumptions:
- Control communication is local-only.
- Reset is explicit and does not happen automatically.

Control channel contract (v1):
- Transport: Unix domain socket at control_socket_path (default: /tmp/overwork-alert.sock)
- Encoding: JSON request/response
- Commands: status, pause, resume, reset, stop
- CLI timeout: 2 seconds

Error handling expectations:
- If the daemon is not running or the socket is unreachable, the CLI MUST return a clear error and non-zero exit.
- If a request times out or the response is invalid JSON, the CLI MUST return a clear error and non-zero exit.

Acceptance criteria (timing):
- status MUST return within 2 seconds when the daemon is healthy.
- reset MUST complete within 2 seconds when the daemon is healthy.

### 2. Purpose
Allow the user to inspect and control the tracker in a predictable, explicit manner using CLI commands.

### 3. Actors
- `cpt-overwork-alert-actor-user`

### 4. References
- Overall Design: [DESIGN.md](../DESIGN.md)
- Related feature: tracker-core.md

## 2. Actor Flows

### View status

- [x] **ID**: `cpt-overwork-alert-flow-cli-control-status`

**Actors**:
- `cpt-overwork-alert-actor-user`

1. [x] - `p1` - User runs `overwork-alert status` - `inst-run-status`
2. [x] - `p1` - CLI sends local control request {cmd:"status"} - `inst-send-status-request`
3. [x] - `p1` - **IF** CLI cannot connect to daemon within timeout: **RETURN** error - `inst-status-daemon-unreachable`
4. [x] - `p1` - Daemon returns current TrackerState snapshot - `inst-return-status`
5. [x] - `p1` - **IF** response is invalid: **RETURN** error - `inst-status-invalid-response`
6. [x] - `p1` - CLI prints active time, limit, and paused/running state - `inst-print-status`

### Reset session

- [x] **ID**: `cpt-overwork-alert-flow-cli-control-reset`

**Actors**:
- `cpt-overwork-alert-actor-user`

1. [x] - `p1` - User runs `overwork-alert reset` - `inst-run-reset`
2. [x] - `p1` - CLI sends local control request {cmd:"reset"} - `inst-send-reset-request`
3. [x] - `p1` - **IF** CLI cannot connect to daemon within timeout: **RETURN** error - `inst-reset-daemon-unreachable`
4. [x] - `p1` - Daemon clears active_time_seconds and over-limit reminder state - `inst-clear-state`
5. [x] - `p1` - CLI prints confirmation - `inst-print-confirm`

### Pause tracking

- [x] **ID**: `cpt-overwork-alert-flow-cli-control-pause`

**Actors**:
- `cpt-overwork-alert-actor-user`

1. [x] - `p1` - User runs `overwork-alert pause` - `inst-run-pause`
2. [x] - `p1` - CLI sends local control request {cmd:"pause"} - `inst-send-pause-request`
3. [x] - `p1` - **IF** CLI cannot connect to daemon within timeout: **RETURN** error - `inst-pause-daemon-unreachable`
4. [x] - `p1` - Daemon sets TrackerState.status=PAUSED and **RETURN** ok - `inst-daemon-pause`
5. [x] - `p1` - CLI prints confirmation - `inst-print-pause-confirm`

### Resume tracking

- [x] **ID**: `cpt-overwork-alert-flow-cli-control-resume`

**Actors**:
- `cpt-overwork-alert-actor-user`

1. [x] - `p1` - User runs `overwork-alert resume` - `inst-run-resume`
2. [x] - `p1` - CLI sends local control request {cmd:"resume"} - `inst-send-resume-request`
3. [x] - `p1` - **IF** CLI cannot connect to daemon within timeout: **RETURN** error - `inst-resume-daemon-unreachable`
4. [x] - `p1` - Daemon sets TrackerState.status=RUNNING and **RETURN** ok - `inst-daemon-resume`
5. [x] - `p1` - CLI prints confirmation - `inst-print-resume-confirm`

### Stop daemon

- [x] **ID**: `cpt-overwork-alert-flow-cli-control-stop`

**Actors**:
- `cpt-overwork-alert-actor-user`

1. [x] - `p1` - User runs `overwork-alert stop` - `inst-run-stop`
2. [x] - `p1` - CLI sends local control request {cmd:"stop"} - `inst-send-stop-request`
3. [x] - `p1` - **IF** CLI cannot connect to daemon within timeout: **RETURN** error - `inst-stop-daemon-unreachable`
4. [x] - `p1` - Daemon begins graceful shutdown and **RETURN** ok - `inst-daemon-stop`
5. [x] - `p1` - CLI prints confirmation - `inst-print-stop-confirm`


## 3. Processes / Business Logic (CDSL)

### Handle control command

- [x] **ID**: `cpt-overwork-alert-algo-cli-control-handle-command`

1. [x] - `p1` - Parse command from request payload - `inst-parse-cmd`
2. [x] - `p1` - **IF** cmd is missing or not recognized **RETURN** error - `inst-handle-invalid-cmd`
3. [x] - `p1` - **IF** cmd="status" **RETURN** current state snapshot - `inst-handle-status`
4. [x] - `p1` - **IF** cmd="pause" set status=PAUSED and **RETURN** ok - `inst-handle-pause`
5. [x] - `p1` - **IF** cmd="resume" set status=RUNNING and **RETURN** ok - `inst-handle-resume`
6. [x] - `p1` - **IF** cmd="reset" clear accumulation and **RETURN** ok - `inst-handle-reset`
7. [x] - `p1` - **IF** cmd="stop" request daemon shutdown and **RETURN** ok - `inst-handle-stop`


## 4. States

### Control channel request lifecycle

- [x] **ID**: `cpt-overwork-alert-state-cli-control-request-lifecycle`

1. [x] - `p1` - **FROM** RECEIVED **TO** VALIDATED **WHEN** request payload is parsed - `inst-transition-validated`
2. [x] - `p1` - **FROM** VALIDATED **TO** RESPONDED **WHEN** daemon sends response - `inst-transition-responded`


## 5. Definitions of Done

### Manual reset and CLI control semantics

- [x] `p1` - **ID**: `cpt-overwork-alert-dod-cli-control-reset-and-controls`

The CLI must provide status, pause, resume, reset, and stop commands. Reset clears the in-memory accumulated active time and over-limit reminder state, and there is no automatic reset.

**Implementation details**:
- Component: `cpt-overwork-alert-component-cli`
- Component: `cpt-overwork-alert-component-control-channel`
- Data: `cpt-overwork-alert-dbtable-tracker-state`

**Implements**:
- `p1` - `cpt-overwork-alert-flow-cli-control-status`
- `p1` - `cpt-overwork-alert-flow-cli-control-reset`
- `p1` - `cpt-overwork-alert-flow-cli-control-pause`
- `p1` - `cpt-overwork-alert-flow-cli-control-resume`
- `p1` - `cpt-overwork-alert-flow-cli-control-stop`

- `p1` - `cpt-overwork-alert-algo-cli-control-handle-command`

**Covers (PRD)**:
- `cpt-overwork-alert-fr-cli-controls`
- `cpt-overwork-alert-fr-manual-reset`

- `cpt-overwork-alert-nfr-privacy-local-only`

**Covers (DESIGN)**:
- `cpt-overwork-alert-principle-explicit-control`

- `cpt-overwork-alert-constraint-macos-cli-only`

- `cpt-overwork-alert-component-cli`
- `cpt-overwork-alert-component-control-channel`
- `cpt-overwork-alert-component-daemon`

- `cpt-overwork-alert-seq-cli-reset`

- `cpt-overwork-alert-dbtable-tracker-state`



## 6. Acceptance Criteria

- [ ] `status` returns within 2 seconds when the daemon is healthy.
- [ ] `reset` completes within 2 seconds when the daemon is healthy.
- [ ] CLI returns clear non-zero exit codes when daemon is unreachable or response is invalid.

## 7. Additional Context (optional)

Pause/resume flows follow the same control channel pattern as reset/status and are handled by the same command handler algorithm.

Out of scope / not applicable (v1):
- No authentication/authorization beyond local-only transport and filesystem permissions on the Unix socket.
- No remote control interface; no TCP listener.
- No encryption in transit (local-only).

