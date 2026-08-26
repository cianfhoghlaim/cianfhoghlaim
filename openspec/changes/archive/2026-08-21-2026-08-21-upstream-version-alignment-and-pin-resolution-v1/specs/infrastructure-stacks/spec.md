## ADDED Requirements

### Requirement: Locket-shim version policy (v0.2.0 → v0.2.1 — fix-the-bug)

The system SHALL pin the Locket shim to `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.1` (per the 2026-08-20 audit & fix). v0.2.1 fixes the regex mismatch (the v0.2.0 regex `\{\{\s*infisical:///([A-Za-z0-9_.\-]+)\?...` required Jinja braces + `?path=` query, but the canonical secrets.env uses the unwrapped `KEY=infisical://<workspace>/<path>/<key>` form) AND fixes the Dockerfile CMD (`["watch"]` → `["--mode", "watch"]` via ENTRYPOINT).

#### Scenario: A new stack is added to `bonneagar/stacks/<name>/`

- **GIVEN** the new stack has a `sidecar.yaml` declaring `image: ghcr.io/cianfhoghlaim/locket-shim`
- **WHEN** `mise run devops:validate-stacks --strict` runs
- **THEN** the image tag MUST be `infisical-0.2.1` or later
- **AND** older tags `0.1.x`, `0.2.0` MUST fail with the message "Locket shim < 0.2.1 has the regex/CMD regression; bump to >= 0.2.1"

### Requirement: Infisical-version policy (server-only pin + CLI hygiene)

The system SHALL keep the self-hosted Infisical SERVER pinned to `v0.161.x` (the v0.161.12 image confirmed running on bunchloch). The Infisical CLI (managed via `mise tool install infisical@latest`) tracks the upstream `v0.43.x` release train. The audit's "v0.161.9 CLI" was incorrect — `v0.161.x` is the server, not the CLI.

#### Scenario: A new IaC sidecar refers to Infisical

- **GIVEN** a new `secrets.env` file declares `infisical://dev-baile/<svc>/<key>` refs
- **WHEN** the Locket sidecar resolves the refs at container start
- **THEN** the sidecar MUST point at `INFISICAL_URL` matching the target server (e.g. `http://host.docker.internal:8081` for local bunchloch; `http://132.145.27.89:8080` for the OCI master)
- **AND** `.infisical.env` SHALL document the canonical comment explaining the server-pin vs CLI-hygiene split.

### Requirement: Lakekeeper version policy (resolve the v0.13.1 vs v0.6.x naming ambiguity)

The system SHALL resolve the Lakekeeper pin ambiguity: the running bunchloch image is `quay.io/lakekeeper/catalog:v0.13.1` while the upstream docs list the current line as `0.6.x`. Operator decision: 0.13.1 is either (a) a private fork's tag, or (b) a typo for the upstream `0.6.x` source. The `bonneagar/komodo/stacks/lakehouse-oci.toml` image tag MUST be reconciled to either pattern, NOT both.

#### Scenario: A new IaC deployment references Lakekeeper

- **WHEN** `iac:bootstrap` brings up a new lakehouse
- **THEN** the Lakekeeper container image tag MUST be one of:
  - `quay.io/lakekeeper/catalog:v0.13.1` (private fork pattern)
  - `quay.io/lakekeeper/catalog:0.6.x` (upstream line; resolve the x from the docs)
- **AND** the resolution SHALL be documented in the IaC TOML as a comment
