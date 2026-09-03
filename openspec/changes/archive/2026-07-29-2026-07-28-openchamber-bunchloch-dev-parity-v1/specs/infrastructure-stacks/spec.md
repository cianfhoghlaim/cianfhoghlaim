# `infrastructure-stacks` capability delta

## ADDED Requirements

### Requirement: Bunchloch OpenChamber external-development stack

The Bunchloch OpenChamber development stack MUST pin OpenChamber to version
`1.16.3` and SHALL run in explicit external OpenCode mode. The stack SHALL
configure `OPENCODE_HOST` for the host OpenCode server at port `4096`, set
`OPENCODE_PORT=4096`, and set `OPENCODE_SKIP_START=true`; it MUST NOT start a
second bundled OpenCode server in the container.

#### Scenario: External mode is selected explicitly

- **WHEN** the Bunchloch OpenChamber development container starts
- **THEN** its resolved environment contains the external OpenCode host,
  port `4096`, and `OPENCODE_SKIP_START=true`
- **AND** the container does not launch a bundled OpenCode daemon

#### Scenario: The image is reproducible and git-capable

- **WHEN** the OpenChamber image is inspected and executed
- **THEN** its OpenChamber version is exactly `1.16.3`
- **AND** `git --version` succeeds inside the container

### Requirement: Identical absolute repository mount

The Bunchloch OpenChamber development stack SHALL mount the host repository
`/Users/cianmacandeisigh/dev/kings_college_galway` at that identical absolute
path inside the container. The stack MUST preserve the path identity used by
the host OpenCode server so session directory filters, worktrees, and git
operations resolve to the same project.

#### Scenario: Session project paths resolve identically

- **WHEN** a user opens the canonical repository from OpenChamber
- **THEN** the external OpenCode server receives
  `/Users/cianmacandeisigh/dev/kings_college_galway` as the project path
- **AND** git status and file discovery operate on the host checkout rather
  than a container-only path

### Requirement: Persistent OpenChamber configuration without application shadowing

The Bunchloch development stack SHALL persist OpenChamber configuration and
UI-owned state in a dedicated config volume under
`/home/bun/.config/openchamber` (or an equivalent XDG config path). It MUST NOT
mount that volume over `/home/bun/.openchamber` or any other application work
directory containing the installed OpenChamber files.

#### Scenario: Config survives recreation

- **WHEN** the OpenChamber container is recreated
- **THEN** UI configuration and preferences remain available from the
  dedicated persistent config volume
- **AND** the installed application files and runtime entrypoint remain visible
  and executable

#### Scenario: Application files are not shadowed

- **WHEN** the running container is inspected
- **THEN** `/home/bun/.openchamber` contains the installed OpenChamber runtime
- **AND** no persistent config mount covers that application directory

### Requirement: Infisical/Locket-only secret delivery

The Bunchloch OpenChamber stack SHALL obtain runtime secrets through the
canonical Infisical/Locket sidecar contract. It MUST NOT commit, bake, print,
or pass plaintext secret values through stack files, image layers, example
files, verification artifacts, or ordinary container environment declarations.

#### Scenario: Secret injection succeeds

- **WHEN** Locket becomes healthy and OpenChamber starts
- **THEN** the required runtime secrets are available from the mounted
  Locket-managed secret file
- **AND** the OpenChamber service starts without a plaintext secret value in
  the repository or image

#### Scenario: Secret leakage is rejected

- **WHEN** the implementation is inspected for secret delivery
- **THEN** all secret entries resolve to Infisical references or runtime mounts
- **AND** no secret value appears in `compose.yaml`, `.env.example`, the
  Dockerfile, committed logs, or a deployment receipt

### Requirement: Loopback-only Bunchloch exposure and correct health endpoints

The Bunchloch OpenChamber development UI SHALL bind its host port to
`127.0.0.1` only. Its health check MUST target OpenChamber's `/health` path,
and the external host OpenCode health check MUST target `/global/health` on
port `4096`; implementations MUST NOT substitute the legacy `/api/health`
path for the OpenChamber dev check.

#### Scenario: Local UI health is green

- **WHEN** the Bunchloch stack is running
- **THEN** `curl -fsS http://127.0.0.1:<dev-port>/health` returns HTTP 200
- **AND** the published port is not bound to `0.0.0.0` or a public interface

#### Scenario: External OpenCode health is green

- **WHEN** host OpenCode 1.17.9 is running on port `4096`
- **THEN** `curl -fsS http://127.0.0.1:4096/global/health` returns HTTP 200
- **AND** the same `/global/health` endpoint is reachable from OpenChamber via
  `host.docker.internal:4096`
