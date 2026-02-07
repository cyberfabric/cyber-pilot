<!-- cpt:#:spec -->
# Spec: CLI Control

<!-- cpt:id-ref:spec has="task" -->
- [x] - `cpt-overwork-alert-spec-cli-control`
<!-- cpt:id-ref:spec -->

<!-- cpt:##:context -->
## 1. Spec Context

<!-- cpt:overview -->
### 1. Overview
This spec defines user-facing CLI controls and the local-only control channel contract between the CLI and the daemon. It covers status reporting, pause/resume, manual reset, and stop.

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
<!-- cpt:overview -->

<!-- cpt:paragraph:purpose -->
### 2. Purpose
Allow the user to inspect and control the tracker in a predictable, explicit manner using CLI commands.
<!-- cpt:paragraph:purpose -->

### 3. Actors
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->

### 4. References
<!-- cpt:list:references -->
- Overall Design: [DESIGN.md](../DESIGN.md)
- Related spec: tracker-core.md
<!-- cpt:list:references -->
<!-- cpt:##:context -->

<!-- cpt:##:flows -->
## 2. Actor Flows

<!-- cpt:###:flow-title repeat="many" -->
### View status

<!-- cpt:id:flow has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-cli-control-flow-status`

**Actors**:
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->

<!-- cpt:cdsl:flow-steps -->
1. [x] - `p1` - User runs `overwork-alert status` - `inst-run-status`
2. [x] - `p1` - CLI sends local control request {cmd:"status"} - `inst-send-status-request`
3. [x] - `p1` - **IF** CLI cannot connect to daemon within timeout: **RETURN** error - `inst-status-daemon-unreachable`
4. [x] - `p1` - Daemon returns current TrackerState snapshot - `inst-return-status`
5. [x] - `p1` - **IF** response is invalid: **RETURN** error - `inst-status-invalid-response`
6. [x] - `p1` - CLI prints active time, limit, and paused/running state - `inst-print-status`
<!-- cpt:cdsl:flow-steps -->
<!-- cpt:id:flow -->
<!-- cpt:###:flow-title repeat="many" -->

<!-- cpt:###:flow-title repeat="many" -->
### Reset session

<!-- cpt:id:flow has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-cli-control-flow-reset`

**Actors**:
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->

<!-- cpt:cdsl:flow-steps -->
1. [x] - `p1` - User runs `overwork-alert reset` - `inst-run-reset`
2. [x] - `p1` - CLI sends local control request {cmd:"reset"} - `inst-send-reset-request`
3. [x] - `p1` - **IF** CLI cannot connect to daemon within timeout: **RETURN** error - `inst-reset-daemon-unreachable`
4. [x] - `p1` - Daemon clears active_time_seconds and over-limit reminder state - `inst-clear-state`
5. [x] - `p1` - CLI prints confirmation - `inst-print-confirm`
<!-- cpt:cdsl:flow-steps -->
<!-- cpt:id:flow -->
<!-- cpt:###:flow-title repeat="many" -->

<!-- cpt:###:flow-title repeat="many" -->
### Pause tracking

<!-- cpt:id:flow has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-cli-control-flow-pause`

**Actors**:
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->

<!-- cpt:cdsl:flow-steps -->
1. [x] - `p1` - User runs `overwork-alert pause` - `inst-run-pause`
2. [x] - `p1` - CLI sends local control request {cmd:"pause"} - `inst-send-pause-request`
3. [x] - `p1` - **IF** CLI cannot connect to daemon within timeout: **RETURN** error - `inst-pause-daemon-unreachable`
4. [x] - `p1` - Daemon sets TrackerState.status=PAUSED and **RETURN** ok - `inst-daemon-pause`
5. [x] - `p1` - CLI prints confirmation - `inst-print-pause-confirm`
<!-- cpt:cdsl:flow-steps -->
<!-- cpt:id:flow -->
<!-- cpt:###:flow-title repeat="many" -->

<!-- cpt:###:flow-title repeat="many" -->
### Resume tracking

<!-- cpt:id:flow has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-cli-control-flow-resume`

**Actors**:
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->

<!-- cpt:cdsl:flow-steps -->
1. [x] - `p1` - User runs `overwork-alert resume` - `inst-run-resume`
2. [x] - `p1` - CLI sends local control request {cmd:"resume"} - `inst-send-resume-request`
3. [x] - `p1` - **IF** CLI cannot connect to daemon within timeout: **RETURN** error - `inst-resume-daemon-unreachable`
4. [x] - `p1` - Daemon sets TrackerState.status=RUNNING and **RETURN** ok - `inst-daemon-resume`
5. [x] - `p1` - CLI prints confirmation - `inst-print-resume-confirm`
<!-- cpt:cdsl:flow-steps -->
<!-- cpt:id:flow -->
<!-- cpt:###:flow-title repeat="many" -->

<!-- cpt:###:flow-title repeat="many" -->
### Stop daemon

<!-- cpt:id:flow has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-cli-control-flow-stop`

**Actors**:
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->

<!-- cpt:cdsl:flow-steps -->
1. [x] - `p1` - User runs `overwork-alert stop` - `inst-run-stop`
2. [x] - `p1` - CLI sends local control request {cmd:"stop"} - `inst-send-stop-request`
3. [x] - `p1` - **IF** CLI cannot connect to daemon within timeout: **RETURN** error - `inst-stop-daemon-unreachable`
4. [x] - `p1` - Daemon begins graceful shutdown and **RETURN** ok - `inst-daemon-stop`
5. [x] - `p1` - CLI prints confirmation - `inst-print-stop-confirm`
<!-- cpt:cdsl:flow-steps -->
<!-- cpt:id:flow -->
<!-- cpt:###:flow-title repeat="many" -->

<!-- cpt:##:flows -->

<!-- cpt:##:algorithms -->
## 3. Algorithms

<!-- cpt:###:algo-title repeat="many" -->
### Handle control command

<!-- cpt:id:algo has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-cli-control-algo-handle-command`

<!-- cpt:cdsl:algo-steps -->
1. [x] - `p1` - Parse command from request payload - `inst-parse-cmd`
2. [x] - `p1` - **IF** cmd is missing or not recognized **RETURN** error - `inst-handle-invalid-cmd`
3. [x] - `p1` - **IF** cmd="status" **RETURN** current state snapshot - `inst-handle-status`
4. [x] - `p1` - **IF** cmd="pause" set status=PAUSED and **RETURN** ok - `inst-handle-pause`
5. [x] - `p1` - **IF** cmd="resume" set status=RUNNING and **RETURN** ok - `inst-handle-resume`
6. [x] - `p1` - **IF** cmd="reset" clear accumulation and **RETURN** ok - `inst-handle-reset`
7. [x] - `p1` - **IF** cmd="stop" request daemon shutdown and **RETURN** ok - `inst-handle-stop`
<!-- cpt:cdsl:algo-steps -->
<!-- cpt:id:algo -->
<!-- cpt:###:algo-title repeat="many" -->

<!-- cpt:##:algorithms -->

<!-- cpt:##:states -->
## 4. States

<!-- cpt:###:state-title repeat="many" -->
### Control channel request lifecycle

<!-- cpt:id:state has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-cli-control-state-request-lifecycle`

<!-- cpt:cdsl:state-transitions -->
1. [x] - `p1` - **FROM** RECEIVED **TO** VALIDATED **WHEN** request payload is parsed - `inst-transition-validated`
2. [x] - `p1` - **FROM** VALIDATED **TO** RESPONDED **WHEN** daemon sends response - `inst-transition-responded`
<!-- cpt:cdsl:state-transitions -->
<!-- cpt:id:state -->
<!-- cpt:###:state-title repeat="many" -->

<!-- cpt:##:states -->

<!-- cpt:##:requirements -->
## 5. Definition of Done

<!-- cpt:###:req-title repeat="many" -->
### Manual reset and CLI control semantics

<!-- cpt:id:req has="priority,task" to_code="true" -->
- [x] `p1` - **ID**: `cpt-overwork-alert-spec-cli-control-req-reset-and-controls`

<!-- cpt:paragraph:req-body -->
The CLI must provide status, pause, resume, reset, and stop commands. Reset clears the in-memory accumulated active time and over-limit reminder state, and there is no automatic reset.
<!-- cpt:paragraph:req-body -->

**Implementation details**:
<!-- cpt:list:req-impl -->
- Component: `cpt-overwork-alert-component-cli`
- Component: `cpt-overwork-alert-component-control-channel`
- Data: `cpt-overwork-alert-dbtable-tracker-state`
<!-- cpt:list:req-impl -->

**Implements**:
<!-- cpt:id-ref:flow has="priority" -->
- `p1` - `cpt-overwork-alert-spec-cli-control-flow-status`
- `p1` - `cpt-overwork-alert-spec-cli-control-flow-reset`
- `p1` - `cpt-overwork-alert-spec-cli-control-flow-pause`
- `p1` - `cpt-overwork-alert-spec-cli-control-flow-resume`
- `p1` - `cpt-overwork-alert-spec-cli-control-flow-stop`
<!-- cpt:id-ref:flow -->

<!-- cpt:id-ref:algo has="priority" -->
- `p1` - `cpt-overwork-alert-spec-cli-control-algo-handle-command`
<!-- cpt:id-ref:algo -->

**Covers (PRD)**:
<!-- cpt:id-ref:fr -->
- `cpt-overwork-alert-fr-cli-controls`
- `cpt-overwork-alert-fr-manual-reset`
<!-- cpt:id-ref:fr -->

<!-- cpt:id-ref:nfr -->
- `cpt-overwork-alert-nfr-privacy-local-only`
<!-- cpt:id-ref:nfr -->

**Covers (DESIGN)**:
<!-- cpt:id-ref:principle -->
- `cpt-overwork-alert-principle-explicit-control`
<!-- cpt:id-ref:principle -->

<!-- cpt:id-ref:constraint -->
- `cpt-overwork-alert-constraint-macos-cli-only`
<!-- cpt:id-ref:constraint -->

<!-- cpt:id-ref:component -->
- `cpt-overwork-alert-component-cli`
- `cpt-overwork-alert-component-control-channel`
- `cpt-overwork-alert-component-daemon`
<!-- cpt:id-ref:component -->

<!-- cpt:id-ref:seq -->
- `cpt-overwork-alert-seq-cli-reset`
<!-- cpt:id-ref:seq -->

<!-- cpt:id-ref:dbtable -->
- `cpt-overwork-alert-dbtable-tracker-state`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:req -->
<!-- cpt:###:req-title repeat="many" -->

<!-- cpt:##:requirements -->

<!-- cpt:##:additional-context -->
## 6. Additional Context (optional)

<!-- cpt:free:context-notes -->
Pause/resume flows follow the same control channel pattern as reset/status and are handled by the same command handler algorithm.

Out of scope / not applicable (v1):
- No authentication/authorization beyond local-only transport and filesystem permissions on the Unix socket.
- No remote control interface; no TCP listener.
- No encryption in transit (local-only).
<!-- cpt:free:context-notes -->
<!-- cpt:##:additional-context -->

<!-- cpt:#:spec -->
