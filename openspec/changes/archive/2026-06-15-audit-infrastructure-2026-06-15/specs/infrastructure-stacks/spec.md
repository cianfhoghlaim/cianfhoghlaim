# Infrastructure Stacks — Spec Delta (audit-infrastructure-2026-06-15)

## ADDED Requirements

### Requirement: Stack Audit Scripts

The monorepo SHALL provide shell scripts under
`infrastructure/audit/scripts/` that capture the live state of
the 2-host topology (bunchloch + arm1-oci) and surface
divergences from the filesystem `compose.yaml` files.

The scripts SHALL be runnable from the operator's MacBook
(`bunchloch`) and SHALL write JSON snapshots to
`infrastructure/audit/inventory/<host>-<UTC-timestamp>.json`.

#### Scenario: Snapshot bunchloch containers

- **GIVEN** the operator has Docker installed on bunchloch
- **WHEN** the operator runs `bash infrastructure/audit/scripts/inventory-bunchloch.sh`
- **THEN** a JSON file appears at `infrastructure/audit/inventory/bunchloch-<timestamp>.json`
- **AND** the JSON contains: `containers[]` (with name, image, state, ports, mounts, networks), `networks[]`, `volumes[]`, and a top-level `host_info` block

#### Scenario: Snapshot arm1-oci containers

- **GIVEN** the operator's `~/.ssh/config` has an `arm1-oci` host entry
- **AND** the operator has passwordless SSH to arm1-oci
- **WHEN** the operator runs `bash infrastructure/audit/scripts/inventory-arm1-oci.sh`
- **THEN** a JSON file appears at `infrastructure/audit/inventory/arm1-oci-<timestamp>.json`
- **AND** the JSON shape matches the bunchloch snapshot

#### Scenario: Diff against filesystem composes

- **GIVEN** the operator has run both inventory scripts
- **WHEN** the operator runs `bash infrastructure/audit/scripts/diff-against-composes.sh <bunchloch.json> <arm1-oci.json>`
- **THEN** the script prints a table of: orphaned containers (live, not in any compose), missing services (in a compose, not running), port conflicts (same host port, two services)

#### Scenario: Probe public Pangolin URLs

- **GIVEN** the operator has network access to the Pangolin-routable `*.cianfhoghlaim.ie` domains
- **WHEN** the operator runs `bash infrastructure/audit/scripts/probe-public-urls.sh`
- **THEN** the script reads `infrastructure/pangolin/a2a-resources.blueprint.yaml`
- **AND** for each `full-domain` entry, prints the URL, the HTTP status code, and the round-trip time
- **AND** the script returns exit code 0 if all probed URLs are 2xx, 3xx, or 4xx; exit code 1 if any URL is 5xx or unreachable

### Requirement: Deployment Runbook

Every user-named deploy target SHALL have a 1-page Markdown
runbook under `infrastructure/deploy-runbooks/<name>.md` that
documents the deploy steps as shell snippets copy-pastable
into a future AI agent's run loop.

A runbook is in scope for this requirement if it is on the
2026-06-15 user-named list:
`infisical`, `komodo`, `pangolin`, `ansible`, `cal-diy`,
`vikunja`, `n8n`, `changedetection`, `bytebase`.

#### Scenario: A runbook exists for each user-named target

- **GIVEN** the 2026-06-15 audit identified 9 user-named deploy targets
- **WHEN** a future AI agent queries `ls infrastructure/deploy-runbooks/`
- **THEN** the 9 expected `<name>.md` files are present (one per target)

#### Scenario: A runbook contains diagnostic checks

- **GIVEN** a runbook exists at `infrastructure/deploy-runbooks/<name>.md`
- **WHEN** a future AI agent greps the runbook for the section headings `## Pre-flight`, `## First-time deploy`, `## Verify`, `## Rollback`
- **THEN** all 4 sections are present
- **AND** each section has at least one shell snippet prefixed with ```` ```bash ```` and a `curl`-based diagnostic

#### Scenario: A runbook does not execute the deploy itself

- **GIVEN** a runbook exists
- **WHEN** the runbook is opened in a text editor
- **THEN** it is documentation only — no shell script that starts the deploy runs as a result of opening the file
- **AND** every `docker compose up` / `komodo sync` / `infisical` call is guarded by an explicit shell comment noting that the agent must paste the snippet, not auto-execute it
