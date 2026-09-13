# Change: Edge routing + offline-site remediation (register 7 missing Traefik routers + rebind 3 offline Pangolin resources)

## Why

Per the `2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1`
change's `specs/infrastructure-stacks/spec.md:45-53` finding:

> Traefik has no router for `litellm`/`langfuse`/`vikunja`/`n8n`/
> `glance`/`changedetection`/`paperless` at all — they were never
> registered as Pangolin resources. And a second, independent fault
> produces `HTTP 000` on tunnel hostnames for `infisical`,
> `openchamber`, and `komodo`: their Pangolin `siteResources` rows
> are bound to sites that are offline.

This means **10 of 17 documented `*.cianfhoghlaim.ie` hostnames are
unreachable through the public mesh**:

- **7 hostnames** (`litellm`/`langfuse`/`vikunja`/`n8n`/`glance`/
  `changedetection`/`paperless`) — requests fall through to
  `CN=TRAEFIK DEFAULT CERT` (verify code 21).
- **3 hostnames** (`infisical`/`openchamber`/`komodo`) — bound to
  offline sites; requests return `HTTP 000` (no connection).

The platform's `iac:health` check
(`bonneagar/iac/commands/health.ts`) claims 6-way coverage but does
NOT invoke `scripts/check-edge-tls.sh --strict --all` (the gate
required to catch this bug), so the broken state is masked by a
false-positive health signal.

## What Changes

- **Add 7 missing Traefik routers** to
  `bonneagar/pangolin/config/traefik/traefik_config.yml` — one
  per affected hostname (`litellm`/`langfuse`/`vikunja`/`n8n`/
  `glance`/`changedetection`/`paperless`).
- **Use the new Pangolin client-mgmt API** (added by the
  `2026-08-15-bonneagar-infra-remediation-v2` change, just archived)
  to CREATE 10 missing `siteResources` rows in Pangolin.
- **Rebind 3 offline-site rows** (`infisical`/`openchamber`/`komodo`)
  to a live site (the canonical `arm1-oci` Pangolin site).
- **Wire `scripts/check-edge-tls.sh --strict --all` into `iac:health`** —
  add the edge-tls gate invocation to
  `bonneagar/iac/commands/health.ts` so `mise run iac:health` now
  reports the actual cert state.
- **Add a `cron-edge-tls-probe-both.toml` Komodo procedure** for
  hourly probing of all 10 hostnames.
- Add an `infrastructure-stacks` spec requirement formalising the
  "every `*.cianfhoghlaim.ie` hostname MUST have a live Traefik
  router AND a live Pangolin siteResource" invariant.

## Dependencies

`Blocked by: none`. `Blocked by (soft):
2026-08-15-bonneagar-infra-remediation-v2` (the Pangolin
client-mgmt API + `iac:bootstrap-pangolin-client` /
`iac:sync:clients` commands were added in that change). `Affected
repos: cianfhoghlaim (single repo) + 10 Pangolin `siteResources`
CREATE calls`.

## Impact

- Capabilities: MODIFIED `infrastructure-stacks` (1 ADDED Requirement).
- Code: 7 new Traefik `router.Rule` entries + 10 Pangolin
  `siteResources` CREATE calls + 3 site-rebinding UPDATEs + 1
  `iac:health` integration + 1 new Komodo procedure.
- Risk: medium — creating Traefik routers can shadow existing services
  if the `Host(` rules conflict; mitigated by the dry-run flag in the
  Pangolin client-mgmt API + the edge-tls probe gate before each
  apply.

## Success criteria

1. `bash scripts/check-edge-tls.sh --strict --all` exits 0 for all 10
   affected hostnames (and remains green for the 7 already-working
   ones).
2. `mise run iac:health` invokes the gate and reports any failure
   mode in its output.
3. Every `*.cianfhoghlaim.ie` hostname returns
   `verify return code: 0` (live cert) OR a documented offline-site
   exit (graceful degradation, no `HTTP 000`).
4. `openspec validate
   2026-08-13-edge-routing-and-offline-site-remediation-v1 --strict`
   returns 0 errors.
