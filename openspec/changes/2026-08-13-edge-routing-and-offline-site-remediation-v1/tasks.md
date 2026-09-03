# Tasks: Edge routing + offline-site remediation

## Phase A — Add 7 missing Traefik routers (1 task, ~1 hour)

- [ ] A1 Read
  `bonneagar/pangolin/config/traefik/traefik_config.yml` to find
  the canonical router template.
- [ ] A2 Add 7 new `router.Rule: Host(...)` entries for the
  affected hostnames: `litellm.cianfhoghlaim.ie`,
  `langfuse.cianfhoghlaim.ie`, `vikunja.cianfhoghlaim.ie`,
  `n8n.cianfhoghlaim.ie`, `glance.cianfhoghlaim.ie`,
  `changedetection.cianfhoghlaim.ie`,
  `paperless.cianfhoghlaim.ie`.
- [ ] A3 Each router points at the corresponding internal service
  (e.g. `litellm.cianfhoghlaim.ie` → `http://litellm:4000`).

## Phase B — Use the Pangolin client-mgmt API to CREATE 10 siteResources (1 task, ~1 hour)

- [ ] B1 Use `iac:bootstrap-pangolin-client` (from the archived
  `2026-08-15-bonneagar-infra-remediation-v2` change) to provision
  the Pangolin client-mgmt credentials.
- [ ] B2 Run `iac:sync:clients --add-resources` to CREATE 10
  missing `siteResources` rows for the 7 newly-routed hostnames + 3
  offline-site rebindings.

## Phase C — Rebind 3 offline-site resources (1 task, ~30 minutes)

- [ ] C1 Update `pangolin.yaml` for `infisical`, `openchamber`, and
  `komodo` so each resource's `site_id` points at the canonical
  live `arm1-oci` site (not the offline `bunchloch` or `macbook`
  site).
- [ ] C2 Re-run `bash scripts/check-edge-tls.sh --strict --all` —
  all 3 should now return `verify return code: 0`.

## Phase D — Wire `check-edge-tls.sh` into `iac:health` (1 task, ~30 minutes)

- [ ] D1 Read `bonneagar/iac/commands/health.ts` to find the
  integration point.
- [ ] D2 Add the `bash scripts/check-edge-tls.sh --strict --all`
  invocation as the 7th health check (alongside the existing 6).
- [ ] D3 Update the `health.ts` CLI output to include the edge-tls
  status.

## Phase E — Add hourly probe procedure (1 task, ~15 minutes)

- [ ] E1 Create
  `bonneagar/komodo/procedures/cron-edge-tls-probe-both.toml` —
  hourly cron that runs `bash scripts/check-edge-tls.sh --strict --all`
  and emits a Komodo alert on failure.

## Phase F — Validate (3 tasks, ~15 minutes)

- [ ] F1 `bash scripts/check-edge-tls.sh --strict --all` exits 0
  for all 17 hostnames (the 10 newly-fixed + the 7 already-working).
- [ ] F2 `mise run iac:health` invokes the edge-tls gate and reports
  the new "edge-tls" check status.
- [ ] F3 `openspec validate
  2026-08-13-edge-routing-and-offline-site-remediation-v1 --strict`
  returns 0 errors.

## Out of scope (flagged for follow-up)

- The 4 known NEW Traefik cert-management hazards documented in
  `2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1`
  (Traefik auto-renewal config + wildcard cert provisioning) —
  covered by `2026-08-13-bonneagar-infra-remediation-v3` (Plan I-C)
  for the working-tree fixes, and the new openspec change
  `2026-08-14-tinyauth-traefik-cert-renewal-v1` (not yet proposed)
  for the cert-renewal automation.
