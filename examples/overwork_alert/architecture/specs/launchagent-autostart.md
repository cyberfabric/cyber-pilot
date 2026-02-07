<!-- cpt:#:spec -->
# Spec: LaunchAgent Autostart

<!-- cpt:id-ref:spec has="task" -->
- [x] - `cpt-overwork-alert-spec-launchagent-autostart`
<!-- cpt:id-ref:spec -->

<!-- cpt:##:context -->
## 1. Spec Context

<!-- cpt:overview -->
### 1. Overview
This spec defines how the tool is started automatically on user login using a macOS user LaunchAgent, and how the CLI installs and uninstalls that LaunchAgent.

Key assumptions:
- Autostart is implemented using user-level LaunchAgents only.
- The daemon remains a CLI-launched process; there is no custom UI.

Acceptance criteria:
- Installing autostart MUST be idempotent (running install twice results in a single installed LaunchAgent).
- Uninstalling autostart MUST be idempotent (running uninstall when not installed succeeds with a clear message).
- After a successful install, the daemon MUST start automatically at the next user login.
<!-- cpt:overview -->

<!-- cpt:paragraph:purpose -->
### 2. Purpose
Allow the user to opt into login-time autostart so tracking can run continuously in the background.
<!-- cpt:paragraph:purpose -->

### 3. Actors
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-user`
- `cpt-overwork-alert-actor-login-runner`
- `cpt-overwork-alert-actor-macos`
<!-- cpt:id-ref:actor -->

### 4. References
<!-- cpt:list:references -->
- Overall Design: [DESIGN.md](../DESIGN.md)
- ADRs: `cpt-overwork-alert-adr-cli-daemon-launchagent-no-menubar`
<!-- cpt:list:references -->
<!-- cpt:##:context -->

<!-- cpt:##:flows -->
## 2. Actor Flows

<!-- cpt:###:flow-title repeat="many" -->
### Install autostart

<!-- cpt:id:flow has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-launchagent-autostart-flow-install`

**Actors**:
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->

<!-- cpt:cdsl:flow-steps -->
1. [x] - `p1` - User runs `overwork-alert install-autostart` - `inst-run-install`
2. [x] - `p1` - **IF** LaunchAgent already installed: ensure it matches expected content and continue - `inst-install-idempotent`
3. [x] - `p1` - CLI builds LaunchAgent plist content using `cpt-overwork-alert-spec-launchagent-autostart-algo-build-plist` - `inst-build-plist`
4. [x] - `p1` - CLI writes plist to the user LaunchAgents directory - `inst-write-plist`
5. [x] - `p1` - **IF** plist cannot be written: **RETURN** error - `inst-write-plist-error`
6. [x] - `p1` - CLI loads/starts LaunchAgent via launchctl - `inst-launchctl-load`
7. [x] - `p1` - **IF** launchctl fails: **RETURN** error - `inst-launchctl-load-error`
<!-- cpt:cdsl:flow-steps -->
<!-- cpt:id:flow -->
<!-- cpt:###:flow-title repeat="many" -->

<!-- cpt:###:flow-title repeat="many" -->
### Uninstall autostart

<!-- cpt:id:flow has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-launchagent-autostart-flow-uninstall`

**Actors**:
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->

<!-- cpt:cdsl:flow-steps -->
1. [x] - `p1` - User runs `overwork-alert uninstall-autostart` - `inst-run-uninstall`
2. [x] - `p1` - **IF** LaunchAgent is not installed: **RETURN** ok (idempotent) - `inst-uninstall-idempotent`
3. [x] - `p1` - CLI stops/unloads LaunchAgent via launchctl - `inst-launchctl-unload`
4. [x] - `p1` - **IF** launchctl fails: continue to plist deletion and **RETURN** warning - `inst-launchctl-unload-warn`
5. [x] - `p1` - CLI deletes the LaunchAgent plist - `inst-delete-plist`
6. [x] - `p1` - **IF** plist cannot be deleted: **RETURN** error - `inst-delete-plist-error`
<!-- cpt:cdsl:flow-steps -->
<!-- cpt:id:flow -->
<!-- cpt:###:flow-title repeat="many" -->

<!-- cpt:##:flows -->

<!-- cpt:##:algorithms -->
## 3. Algorithms

<!-- cpt:###:algo-title repeat="many" -->
### Build LaunchAgent plist

<!-- cpt:id:algo has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-launchagent-autostart-algo-build-plist`

<!-- cpt:cdsl:algo-steps -->
1. [x] - `p1` - Choose a stable LaunchAgent label for the tool - `inst-choose-label`
2. [x] - `p1` - Set ProgramArguments to run the daemon start command - `inst-set-args`
3. [x] - `p1` - Set RunAtLoad=true and KeepAlive=true - `inst-set-options`
4. [x] - `p1` - Set launchd restart throttling options to avoid rapid crash loops - `inst-set-throttle`
5. [x] - `p1` - **RETURN** plist text content - `inst-return-plist`
<!-- cpt:cdsl:algo-steps -->
<!-- cpt:id:algo -->
<!-- cpt:###:algo-title repeat="many" -->

<!-- cpt:##:algorithms -->

<!-- cpt:##:states -->
## 4. States

<!-- cpt:###:state-title repeat="many" -->
### LaunchAgent installation state

<!-- cpt:id:state has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-launchagent-autostart-state-installation`

<!-- cpt:cdsl:state-transitions -->
1. [x] - `p1` - **FROM** NOT_INSTALLED **TO** INSTALLED **WHEN** plist is written and launchctl load succeeds - `inst-transition-installed`
2. [x] - `p1` - **FROM** INSTALLED **TO** NOT_INSTALLED **WHEN** launchctl unload succeeds and plist is removed - `inst-transition-removed`
<!-- cpt:cdsl:state-transitions -->
<!-- cpt:id:state -->
<!-- cpt:###:state-title repeat="many" -->

<!-- cpt:##:states -->

<!-- cpt:##:requirements -->
## 5. Definition of Done

<!-- cpt:###:req-title repeat="many" -->
### Login autostart via user LaunchAgent

<!-- cpt:id:req has="priority,task" to_code="true" -->
- [x] `p1` - **ID**: `cpt-overwork-alert-spec-launchagent-autostart-req-install-and-run`

<!-- cpt:paragraph:req-body -->
The user can install a LaunchAgent that starts the daemon at login. The user can also uninstall the LaunchAgent to disable autostart.
<!-- cpt:paragraph:req-body -->

**Implementation details**:
<!-- cpt:list:req-impl -->
- Component: `cpt-overwork-alert-component-launchagent-manager`
- Component: `cpt-overwork-alert-component-cli`
- Data: `cpt-overwork-alert-dbtable-config`
<!-- cpt:list:req-impl -->

**Implements**:
<!-- cpt:id-ref:flow has="priority" -->
- `p1` - `cpt-overwork-alert-spec-launchagent-autostart-flow-install`
- `p1` - `cpt-overwork-alert-spec-launchagent-autostart-flow-uninstall`
<!-- cpt:id-ref:flow -->

<!-- cpt:id-ref:algo has="priority" -->
- `p1` - `cpt-overwork-alert-spec-launchagent-autostart-algo-build-plist`
<!-- cpt:id-ref:algo -->

**Covers (PRD)**:
<!-- cpt:id-ref:fr -->
- `cpt-overwork-alert-fr-autostart`
<!-- cpt:id-ref:fr -->
 
<!-- cpt:id-ref:nfr -->
- `cpt-overwork-alert-nfr-privacy-local-only`
<!-- cpt:id-ref:nfr -->

**Covers (DESIGN)**:
<!-- cpt:id-ref:principle -->
- `cpt-overwork-alert-principle-local-only-minimal-state`
<!-- cpt:id-ref:principle -->

<!-- cpt:id-ref:constraint -->
- `cpt-overwork-alert-constraint-macos-cli-only`
<!-- cpt:id-ref:constraint -->

<!-- cpt:id-ref:component -->
- `cpt-overwork-alert-component-launchagent-manager`
- `cpt-overwork-alert-component-cli`
<!-- cpt:id-ref:component -->

<!-- cpt:id-ref:seq -->
- `cpt-overwork-alert-seq-run-and-alert`
<!-- cpt:id-ref:seq -->

<!-- cpt:id-ref:dbtable -->
- `cpt-overwork-alert-dbtable-config`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:req -->
<!-- cpt:###:req-title repeat="many" -->

<!-- cpt:##:requirements -->

<!-- cpt:##:additional-context -->
## 6. Additional Context (optional)

<!-- cpt:free:context-notes -->
The exact LaunchAgent label and ProgramArguments are implementation details; they must remain stable so install/uninstall behaves predictably.

Out of scope / not applicable (v1):
- No system-wide (root) daemon installation.
- No automatic self-update or signed installer packaging.
- No network access and no privileged escalation.
<!-- cpt:free:context-notes -->
<!-- cpt:##:additional-context -->

<!-- cpt:#:spec -->
