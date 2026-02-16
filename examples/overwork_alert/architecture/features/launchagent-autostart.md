# Feature: LaunchAgent Autostart

- [x] `p1` - **ID**: `cpt-overwork-alert-featstatus-launchagent-autostart`

- [x] - `cpt-overwork-alert-feature-launchagent-autostart`

## 1. Feature Context

### 1. Overview
This feature defines how the tool is started automatically on user login using a macOS user LaunchAgent, and how the CLI installs and uninstalls that LaunchAgent.

Key assumptions:
- Autostart is implemented using user-level LaunchAgents only.
- The daemon remains a CLI-launched process; there is no custom UI.

Acceptance criteria:
- Installing autostart MUST be idempotent (running install twice results in a single installed LaunchAgent).
- Uninstalling autostart MUST be idempotent (running uninstall when not installed succeeds with a clear message).
- After a successful install, the daemon MUST start automatically at the next user login.

### 2. Purpose
Allow the user to opt into login-time autostart so tracking can run continuously in the background.

### 3. Actors
- `cpt-overwork-alert-actor-user`
- `cpt-overwork-alert-actor-login-runner`
- `cpt-overwork-alert-actor-macos`

### 4. References
- Overall Design: [DESIGN.md](../DESIGN.md)
- ADRs: `cpt-overwork-alert-adr-cli-daemon-launchagent-no-menubar`

## 2. Actor Flows

### Install autostart

- [x] **ID**: `cpt-overwork-alert-flow-launchagent-autostart-install`

**Actors**:
- `cpt-overwork-alert-actor-user`

1. [x] - `p1` - User runs `overwork-alert install-autostart` - `inst-run-install`
2. [x] - `p1` - **IF** LaunchAgent already installed: ensure it matches expected content and continue - `inst-install-idempotent`
3. [x] - `p1` - CLI builds LaunchAgent plist content using `cpt-overwork-alert-algo-launchagent-autostart-build-plist` - `inst-build-plist`
4. [x] - `p1` - CLI writes plist to the user LaunchAgents directory - `inst-write-plist`
5. [x] - `p1` - **IF** plist cannot be written: **RETURN** error - `inst-write-plist-error`
6. [x] - `p1` - CLI loads/starts LaunchAgent via launchctl - `inst-launchctl-load`
7. [x] - `p1` - **IF** launchctl fails: **RETURN** error - `inst-launchctl-load-error`

### Uninstall autostart

- [x] **ID**: `cpt-overwork-alert-flow-launchagent-autostart-uninstall`

**Actors**:
- `cpt-overwork-alert-actor-user`

1. [x] - `p1` - User runs `overwork-alert uninstall-autostart` - `inst-run-uninstall`
2. [x] - `p1` - **IF** LaunchAgent is not installed: **RETURN** ok (idempotent) - `inst-uninstall-idempotent`
3. [x] - `p1` - CLI stops/unloads LaunchAgent via launchctl - `inst-launchctl-unload`
4. [x] - `p1` - **IF** launchctl fails: continue to plist deletion and **RETURN** warning - `inst-launchctl-unload-warn`
5. [x] - `p1` - CLI deletes the LaunchAgent plist - `inst-delete-plist`
6. [x] - `p1` - **IF** plist cannot be deleted: **RETURN** error - `inst-delete-plist-error`


## 3. Processes / Business Logic (CDSL)

### Build LaunchAgent plist

- [x] **ID**: `cpt-overwork-alert-algo-launchagent-autostart-build-plist`

1. [x] - `p1` - Choose a stable LaunchAgent label for the tool - `inst-choose-label`
2. [x] - `p1` - Set ProgramArguments to run the daemon start command - `inst-set-args`
3. [x] - `p1` - Set RunAtLoad=true and KeepAlive=true - `inst-set-options`
4. [x] - `p1` - Set launchd restart throttling options to avoid rapid crash loops - `inst-set-throttle`
5. [x] - `p1` - **RETURN** plist text content - `inst-return-plist`


## 4. States

### LaunchAgent installation state

- [x] **ID**: `cpt-overwork-alert-state-launchagent-autostart-installation`

1. [x] - `p1` - **FROM** NOT_INSTALLED **TO** INSTALLED **WHEN** plist is written and launchctl load succeeds - `inst-transition-installed`
2. [x] - `p1` - **FROM** INSTALLED **TO** NOT_INSTALLED **WHEN** launchctl unload succeeds and plist is removed - `inst-transition-removed`


## 5. Definitions of Done

### Login autostart via user LaunchAgent

- [x] `p1` - **ID**: `cpt-overwork-alert-dod-launchagent-autostart-install-and-run`

The user can install a LaunchAgent that starts the daemon at login. The user can also uninstall the LaunchAgent to disable autostart.

**Implementation details**:
- Component: `cpt-overwork-alert-component-launchagent-manager`
- Component: `cpt-overwork-alert-component-cli`
- Data: `cpt-overwork-alert-dbtable-config`

**Implements**:
- `p1` - `cpt-overwork-alert-flow-launchagent-autostart-install`
- `p1` - `cpt-overwork-alert-flow-launchagent-autostart-uninstall`

- `p1` - `cpt-overwork-alert-algo-launchagent-autostart-build-plist`

**Covers (PRD)**:
- `cpt-overwork-alert-fr-autostart`
 
- `cpt-overwork-alert-nfr-privacy-local-only`

**Covers (DESIGN)**:
- `cpt-overwork-alert-principle-local-only-minimal-state`

- `cpt-overwork-alert-constraint-macos-cli-only`

- `cpt-overwork-alert-component-launchagent-manager`
- `cpt-overwork-alert-component-cli`

- `cpt-overwork-alert-seq-run-and-alert`

- `cpt-overwork-alert-dbtable-config`



## 6. Acceptance Criteria

- [ ] Installing autostart is idempotent.
- [ ] Uninstalling autostart is idempotent.
- [ ] After successful install, the daemon starts automatically at next user login.

## 7. Additional Context (optional)

The exact LaunchAgent label and ProgramArguments are implementation details; they must remain stable so install/uninstall behaves predictably.

Out of scope / not applicable (v1):
- No system-wide (root) daemon installation.
- No automatic self-update or signed installer packaging.
- No network access and no privileged escalation.

