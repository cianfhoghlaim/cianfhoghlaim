# Change: 2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1

## Why

The Cianfhoghlaim agent-platform cluster has three surfaces (hermes +
openclaw + openchamber) on arm1-oci, all fronted by Locket sidecars that
read `infisical://dev-baile/<stack>/<key>` paths from a Pangolin private
resource pointing at `infisical.cianfhoghlaim.ie` on arm1-oci.

Verified 2026-07-24:
- Running `docker compose -f compose.yaml -f sidecar.yaml up -d` against
  `bonneagar/stacks/openclaw/` (or `hermes/`) fails at config-parse time
  with:
  `env file /run/secrets/locket/secrets.env not found: stat
   /run/secrets/locket/secrets.env: no such file or directory`
  That path is **only ever materialised by the locket sidecar** at runtime
  on the `stack-secrets` tmpfs volume — docker compose validates
  `env_file` host paths at parse time and refuses to start regardless of
  `depends_on: condition: service_healthy`.
- The locket sidecar's upstream call to Infisical also fails because the
  Pangolin private resource `infisical.cianfhoghlaim.ie` is returning
  HTTP 502 Bad Gateway at the WireGuard hop (the destination `infisical`
  container on arm1-oci is unhealthy / being recreated). Even with the
  parse-time error fixed, locket cannot resolve any secret.
- `docker ps` on bunchloch shows zero `infisical-*` containers, zero
  `locket-*` containers, zero `openclaw-*` containers, and the
  `cianfhoghlaim` external network does not exist on this host (only the
  `lakehouse` fleet is running locally).
- arm1-oci itself IS reachable (the operator confirmed `ssh arm1-oci`
  works), so the OCI repair path (`iac:sync:sites` to rebuild the
  Pangolin private resource, then `iac:rotate-auth`) is viable but
  needs a separate follow-up change; it is **out of scope** for this
  immediate unblock.

## What changes

- 1 new bootstrap script `bonneagar/scripts/seed-bunchloch-fallback-vault.sh`
  that:
    1. Creates a fresh `dev-baile` project on the local Infisical
    2. Seeds the **9 infisical paths** consumed by openclaw + hermes
       (the same set the `iac:bootstrap-infisical` workflow produces on
       arm1-oci: `gateway_token`, `openai_api_key`, the 8 channel
       tokens, `telegram_bot_token`, etc.)
    3. Writes the bons-iac Universal Auth client_id + client_secret to
       `~/.env` (the canonical path the IaC expects) and to
       `/etc/komodo/secrets/infisical_secret` (the Komodo Periphery
       mount path).
- 1 new `bonneagar/deploy-runbooks/openclaw-hermes-bunchloch-local-2026-07.md`
  runbook (the operator's quick-start: 5 commands from cold to
  green)
- 1 new ADDED Requirement to `infrastructure-stacks` covering the
  parse-time env_file failure mode (so the stack-doctor gate can
  enforce it for future Locket-using stacks)
- 1 new ADDED Requirement to `infrastructure-stacks` covering the
  "Pangolin private resource unhealthy → fall back to local Infisical"
  failure mode
- 0 modifications to `openclaw/sidecar.yaml` or `hermes/sidecar.yaml`
  (the parse-time failure is a docker-compose limitation, not a
  bug in the YAML; the IaC-managed Komodo stack already runs the
  containers in the correct order and `depends_on` works there)
- 0 changes to the OCI path. The Pangolin private resource repair is
  tracked as a follow-up change
  (`2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1`).

## Impact

- **Affected specs:** `infrastructure-stacks` (shared) only.
- **Affected hosts:** `bunchloch` only. arm1-oci is untouched.
- **Risk:** low — fresh-infra vault on this Mac only; rolled back with
  `docker compose -f bonneagar/stacks/infisical/compose.yaml down -v`.
- **Audit gates:** `openspec validate <id> --strict` (MUST pass),
  `mise run lint:skills`, `bun run validate-stacks`.
- **Disk:** ~750 MB pulled (3 images + layer cache).
- **RAM headroom:** ~400 MB resident (Infisical 250 MB + pg 80 MB +
  redis 40 MB + locket 30 MB). Comfortable on M4.

## Non-goals

- Not fixing the arm1-OCI Pangolin private resource (tracked as
  follow-up `2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1`).
- Not migrating the production arm1-OCI `dev-baile` vault — we are
  creating a fresh, bunchloch-local-only vault with fresh secrets.
- Not exposing the local Infisical via Pangolin (port 8081 stays on
  `127.0.0.1`).
- Not yet wiring Langfuse / LiteLLM. The omnibus
  `deploy-agent-platform-cluster-bunchloch` procedure will pull those in
  on the next session.

## Dependencies

`Blocked by: none`
`Blocked by (soft):`
  - `2026-07-12-iac-ify-infisical-bootstrap-v1` (uses its CLI)
  - `2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical` (archived; provides the bons IaC CLI)
  - `2026-07-06-deploy-infisical-bunchloch-local` (archived; pattern reference)
`Affected repos: cianfhoghlaim` (single-repo change)

## Spec delta

See `specs/infrastructure-stacks/spec.md` for the 2 ADDED Requirements:
1. "Locket sidecar env_file must be runtime-mounted, not host-validated"
2. "Bunchloch fallback Infisical vault when arm1-OCI private resource is unhealthy"

## Open follow-up issues

| Issue | Tracking change |
|:--|:--|
| Repair the arm1-OCI Pangolin private resource for `infisical.cianfhoghlaim.ie` (re-run `iac:sync:sites` + `iac:rotate-auth`) | `2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1` |
| Wire Langfuse + LiteLLM onto the bunchloch openclaw once locket is healthy | omnibus `deploy-agent-platform-cluster-bunchloch` (existing) |
| Add stack-doctor gate that flags `env_file:` pointing at `/run/secrets/...` without an accompanying locket sidecar | `2026-07-XX-stack-doctor-env-file-parse-time-gate-v1` |
| Decide long-term: local Infisical on bunchloch as a permanent dev env (not just fallback) | `2026-07-XX-bunchloch-dev-infisical-promotion-v1` |