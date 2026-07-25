## ADDED Requirements

### Requirement: Pangolin private-resource drift is detected and repaired via iac:sync:sites

The system SHALL detect when any Pangolin private resource (of which
`infisical.cianfhoghlaim.ie` is one of 6) returns HTTP 5xx for
> 5 consecutive minutes, and SHALL provide the
`iac:sync:sites` command as the canonical repair path. The command
MUST be idempotent and MUST re-emit the private-resource YAML via the
Pangolin Integrations API. The system SHALL NOT silently re-emit
without operator confirmation — `iac:sync:sites` is gated behind a
Komodo procedure that pauses for human approval after the dry-run.

#### Scenario: A private resource returns 502 for > 5 minutes

- **GIVEN** `https://infisical.cianfhoghlaim.ie/api/status` returns
  502 across 6 consecutive 60-second polls
- **WHEN** the operator runs
  `km run procedure repair-pangolin-private-infisical-arm1-oci-v1`
- **THEN** stage 2 of the procedure invokes `iac:sync:sites --dry-run`
  and pauses for `--yes` confirmation
- **AND** on `--yes`, `iac:sync:sites` re-emits the private resource
- **AND** `/api/status` returns 200 within 60s of the re-emit
- **AND** a JSON audit record is written to
  `/tmp/infisical-pangolin-private-repair-${TS}.json`

#### Scenario: iac:sync:sites is a no-op when the resource is healthy

- **GIVEN** `/api/status` returns 200 on the first poll
- **WHEN** the operator runs
  `km run procedure repair-pangolin-private-infisical-arm1-oci-v1`
- **THEN** stage 2 exits early with the message
  `pangolin private resource healthy — no repair needed`
- **AND** no re-emit is performed
- **AND** stages 3-6 are skipped

### Requirement: iac:rotate-auth must run after every Pangolin EE upgrade

The system SHALL require `iac:rotate-auth` to be re-run within 24
hours of any Pangolin EE upgrade that touches the Traefik forward-auth
middleware, the Pangolin Integrations API, OR the WireGuard tunnel
mutual-TLS handshake. The upgrade is detected by a mismatch between
`pangolin.cianfhoghlaim.ie/api/v1/version` and the last recorded
version in `~/.cache/bons-iac/pangolin-version.json`. The bons-iac
CLI SHALL emit a `WARN: pangolin EE upgraded; rotate bons-iac
client_secret` message when the operator runs any `iac:*` command
after the mismatch is detected.

#### Scenario: Operator runs iac:plan after a Pangolin upgrade

- **GIVEN** `pangolin.cianfhoghlaim.ie/api/v1/version` returns
  `vX.Y.Z` (newer than the cached version)
- **WHEN** the operator runs `mise run iac:plan`
- **THEN** the command emits
  `WARN: pangolin EE upgraded from vA.B.C to vX.Y.Z; rotate bons-iac client_secret before applying changes`
- **AND** the operator MUST run `mise run iac:rotate-auth` before
  the next `iac:deploy` will succeed (the deploy gate rejects with
  exit code 17)

#### Scenario: iac:rotate-auth re-derives the infisical_secret file

- **WHEN** the operator runs
  `mise run iac:rotate-auth --target=bons-iac`
- **THEN** a fresh client_secret is minted via `openssl rand -hex 32`
- **AND** the new credential is pushed to the dev-baile project on
  Infisical as `bons-iac/client_secret`
- **AND** `/etc/komodo/secrets/infisical_secret` is rewritten with
  the new credential (mode 0600, owner root)
- **AND** `locket healthcheck` against the rotated credential returns
  OK