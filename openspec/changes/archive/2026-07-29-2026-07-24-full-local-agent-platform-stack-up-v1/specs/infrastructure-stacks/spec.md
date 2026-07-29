## ADDED Requirements

### Requirement: Locket sidecar pattern for Infisical v0.161+ requires locket >= v0.18 or a request transformer

The system SHALL ensure that the locket sidecar (`ghcr.io/bpbradley/locket:infisical`)
used by every agent surface (openclaw, hermes, litellm, langfuse) is
compatible with the Infisical server version it authenticates against.

#### Scenario: Locket v0.17.3 with Infisical v0.161+ server

- **GIVEN** a stack with locket sidecar image
  `ghcr.io/bpbradley/locket:infisical` (tag ≤ `v0.17.3`)
- **AND** an Infisical server image `infisical/infisical` (tag ≥ `v0.161.0`)
- **WHEN** the locket sidecar starts in `watch` or `one-shot` mode
- **THEN** the locket sends `GET /api/v4/secrets/<KEY>?project_id=...&secret_path=...&secret_type=...`
  with **snake_case** query parameter names
- **AND** the Infisical server returns HTTP 422 `ValidationFailure`
  because v0.161+ requires **camelCase** query parameter names
  (`projectId`, `secretPath`, `secretType`)
- **AND** the locket catches the 422 and falls back to "policy=passthrough"
  — writing the raw `{{ infisical://... }}` template to the destination
  instead of the resolved secrets
- **AND** the consumer container (openclaw, hermes) tries to `source
  /run/secrets/locket/secrets.env` in `/bin/sh`, which interprets each
  `{{ infisical:///... }}` line as a command and fails with
  `not found`, causing the container to crash

**Acceptable workarounds (any one):**

1. **Upgrade locket** to a version that uses camelCase field names
   (e.g. `ghcr.io/bpbradley/locket:infisical-v0.18` or a `bons-locket:infisical`
   fork) — the canonical fix.
2. **Downgrade Infisical** to a version that accepts snake_case
   field names (e.g. `infisical/infisical:v0.160.0`).
3. **Add a request transformer** in the locket sidecar
   (e.g. a `mitmproxy` sidecar that rewrites `project_id` → `projectId`
   in outgoing requests).
4. **Patch the locket source** in `stedding/locket/src/provider/infisical.rs`
   (change the `SecretQueryParams` struct's `serde(rename_all = "snake_case")`
   to `"camelCase"`) and rebuild the image.

**Verification:** `curl http://<infisical>/api/v4/secrets/<KEY>?projectId=...&secretPath=...`
returns HTTP 200 with the resolved secret value (NOT 422).

### Requirement: Hermes s6-overlay requires running as root with cap_add [SETUID, SETGID]

The system SHALL ensure that any NousResearch/hermes-agent container
(image tag ≥ `v2026.7.1`) is configured to satisfy s6-overlay's init
constraints when deployed via docker compose.

#### Scenario: Hermes s6-overlay init phase

- **GIVEN** a hermes container with `image: nousresearch/hermes-agent:v2026.7.1`
- **AND** the image's s6-overlay init phase requires:
  - `/run` writable by the container user (s6-overlay checks
    `fatal: /run belongs to uid X instead of Y`)
  - `/opt/data` accessible by the internal `hermes` user (uid 10000)
    which the `main-wrapper.sh: cd /opt/data` step needs
  - `SETUID` + `SETGID` capabilities for s6-overlay's `suexec` to
    transition between root and the `hermes` user
- **WHEN** the container is configured with:
  - `user: 10000:10000` (the internal hermes user) + `read_only: true`
    + `no-new-privileges: true` + `cap_drop: [ALL]`
- **THEN** s6-overlay fails with `fatal: /run belongs to uid 0 instead of
  10000, ... lacking the privileges to fix it`
- **AND** the `tmpfs: /run:mode:1777` workaround is REJECTED by the
  Docker daemon with `invalid tmpfs option ["mode:1777"]` when
  `no-new-privileges: true` is set

**Acceptable configurations (any one):**

1. **Canonical upstream pattern** (recommended): `user: "0:0"` (root),
   no `read_only`, no `no-new-privileges`, `cap_drop: [ALL]`. The s6-overlay
   entrypoint runs as root (allowed to chown /run + /opt/data), then
   transitions to user 10000 via the s6 service definitions. This is the
   upstream pattern documented in the hermes-agent image.

2. **Sidecar pattern** (if root is unacceptable): add a chmod
   `init` container that runs as root before the main hermes container,
   performs the necessary chowns on /run + /opt/data, then EXITS
   (the main container is started only after the init exits).
   The main container then starts with `user: 10000:10000` and the
   pre-chowned /run + /opt/data.

3. **Custom base image** (most invasive): fork hermes-agent to
   remove s6-overlay (replace with a pure dumb-init or tini). Allows
   running as non-root from the start.