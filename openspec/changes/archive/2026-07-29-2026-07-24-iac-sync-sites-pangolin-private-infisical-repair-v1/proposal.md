## Superseded by recent IaC commits

All work proposed here has been shipped in the IaC cluster's recent commits. See the bons-locker-shim v0.2.0 release + the IaC stack contract reconciliation + the agent-platform cluster deploy for the authoritative record.

# Change: 2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1

## Why

The Cianfhoghlaim control plane routes `infisical.cianfhoghlaim.ie`
through Pangolin as a **private resource** to the Infisical container
on `arm1-oci`. As of 2026-07-24 this private resource is returning
HTTP 502 Bad Gateway at the WireGuard hop, blocking every Locket
sidecar on the platform (openclaw + hermes + openchamber + 6
consumer stacks) from resolving secrets.

Verified 2026-07-24:
- `curl -ksS -o /dev/null -w '%{http_code}' https://infisical.cianfhoghlaim.ie/api/status` returns `502`
- `bun run iac:sync:sites` (the bons IaC's Pangolin Integrations API
  reconciler) has not been run since the upstream Pangolin EE upgrade
  on 2026-07-XX — drift in the private-resource YAML on Pangolin
  Core's Postgres
- `mise run iac:rotate-auth` has not been re-run since the bons-iac
  Universal Auth client_secret was last rotated (2026-06-XX); the
  WireGuard tunnel's mutual-TLS may carry stale cert fingerprints

This change runs the 2-step repair: `iac:sync:sites` to re-emit
the private resource declaration, then `iac:rotate-auth` to mint a
fresh client_secret + push it into the bons IaC vault + re-derive
`/etc/komodo/secrets/infisical_secret`. After the repair, the
canonical OCI path is restored and Change 1's local fallback vault
can be torn down.

## What changes

- 1 new Komodo procedure `repair-pangolin-private-infisical-arm1-oci-v1`
  that runs `iac:sync:sites` -> poll `infisical.cianfhoghlaim.ie/api/status`
  for 200 -> `iac:rotate-auth` -> re-derive
  `/etc/komodo/secrets/infisical_secret` -> smoke-test locket on
  bunchloch against the OCI vault -> health check
- 1 new ADDED Requirement to `infrastructure-stacks` covering the
  "Pangolin private-resource drift is detected and repaired via
  iac:sync:sites" failure mode
- 1 new ADDED Requirement to `infrastructure-stacks` covering the
  "iac:rotate-auth must run after every Pangolin EE upgrade" policy
- 1 new runbook
  `bonneagar/deploy-runbooks/repair-pangolin-private-infisical-2026-07.md`
  (the operator's 1-command fix: `km run procedure
  repair-pangolin-private-infisical-arm1-oci-v1`)
- 0 modifications to existing bons IaC CLI commands — both
  `iac:sync:sites` and `iac:rotate-auth` already exist; this change
  only sequences them correctly into a procedure

## Impact

- **Affected specs:** `infrastructure-stacks` (shared) only
- **Affected hosts:** `arm1-oci` (the broken resource) + `bunchloch`
  (smoke test). pangolin-newt is on both.
- **Risk:** medium — touches the production control plane private
  resource; a bad reap could 502 every Locket-using stack. Mitigation:
  the procedure gates each step on a 200 OK before proceeding, AND
  Change 1's local fallback stays up until Change 2 confirms green
- **Audit gates:** `openspec validate <id> --strict` (MUST pass),
  `mise run lint:skills`, `bun run validate-stacks`
- **Order of operations:**
  1. Keep Change 1's local fallback UP (don't tear down yet)
  2. Run `iac:sync:sites` to re-emit the Pangolin private resource
  3. Poll `/api/status` until 200
  4. Run `iac:rotate-auth` to refresh the bons-iac client_secret
  5. Smoke-test by pointing bunchloch locket at the OCI vault
  6. Tear down Change 1's local fallback only after step 5 is green

## Non-goals

- Not upgrading Pangolin EE (out of scope; tracked separately)
- Not rotating the WireGuard tunnel keys (the WireGuard hop is not
  the failing layer; the 502 is at the Pangolin -> Traefik private
  resource mapping)
- Not deleting the bunchloch-local fallback permanently — it
  remains as a future fallback (Change 1 archives with this status)

## Dependencies

`Blocked by: 2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1`
  (the local fallback MUST be green so the operator has a working
   surface during the OCI repair window)
`Blocked by (soft):`
  - `2026-07-12-iac-ify-infisical-bootstrap-v1` (uses its CLI)
  - `2026-07-14-iac-sync-sites-pangolin-integrations-api-v1` (provides `iac:sync:sites`)
  - `2026-07-14-repair-bonneagar-iac-3-way-auth-v1` (provides `iac:rotate-auth`)
`Affected repos: cianfhoghlaim` (single-repo change)

## Spec delta

See `specs/infrastructure-stacks/spec.md` for the 2 ADDED Requirements:
1. "Pangolin private-resource drift is detected and repaired via iac:sync:sites"
2. "iac:rotate-auth must run after every Pangolin EE upgrade"

## Open follow-up issues

| Issue | Tracking change |
|:--|:--|
| Promote the bunchloch-local Infisical fallback to a permanent dev environment (not just emergency) | `2026-07-XX-bunchloch-dev-infisical-promotion-v1` |
| Add a Dagster sensor that pings `https://infisical.cianfhoghlaim.ie/api/status` every 5 minutes and pages on 5xx | `2026-07-XX-dagster-sensor-pangolin-private-health-v1` |
| Move WireGuard tunnel key rotation from manual to a scheduled Komodo procedure | `2026-07-XX-wireguard-key-rotation-automation-v1` |