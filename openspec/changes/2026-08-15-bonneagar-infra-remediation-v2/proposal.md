# Change: Bonneagar infrastructure remediation v2 (Pangolin client-mgmt API + IaC env loader + newt-arm1-oci stack + 10-phase deploy:full)

## Why

The Cianfhoghlaim mesh on the 2-host topology (`arm1-oci` + `bunchloch`) needs a comprehensive remediation pass. The IaC clients are already in place (`pangolin-client.ts`, `komodo-client.ts`, `infisical-client.ts`), but the IaC auth chain was broken:

1. **`iac:health` exits 1** — `KOMODO_JWT or KOMODO_PASSWORD required` + `PANGOLIN_API_KEY required and no Pocket ID OIDC client configured`.
2. **`iac:rotate-auth` had a bug** — wrote the whole `PocketIdAdminKey` object to `PANGOLIN_API_KEY` instead of just the `.apiKey` string.
3. **`iac:cli.ts` did not auto-load the repo-root `.env`** — bun's auto-load only looks for `.env` in cwd, but the IaC runs from `bonneagar/iac/`. This was the root cause of the auth failures.
4. **The Pangolin Integrations API client-mgmt surface was missing** — the 4 methods (`listClients`/`getClient`/`createClient`/`deleteClient`) are NOT exposed in `pangolin-client.ts`, even though the docs at https://docs.pangolin.net/manage/clients/install-client document the canonical setup flow.
5. **No `iac:bootstrap-pangolin-client` command** — the IaC has 24 commands but no canonical "mint a Pangolin client + install the pangolin CLI + render the newt compose" workflow.
6. **No `newt-arm1-oci` stack** — the bunchloch side has `stacks/newt/`, but the arm1-oci side uses an older `stacks/pangolin/newt.yaml` pattern.
7. **`deploy:full` has 8 phases** — doesn't include the IaC auth-rotation phases.

This change files as a smaller, focused openspec change (`v2`) with 2 spec deltas (down from the 5 in my failed `v1`). The scope is:

- IaC TypeScript: 7 files (5 modified + 2 new)
- Stack: 1 new stack (6 GOLD_STANDARD files)
- Komodo: 2 new procedures + 1 resource-sync update
- Scripts: 2 modified (deploy-full.ts + deploy-full.sh)
- Misc: 2 package.json scripts + 2 AGENTS.md drift updates + 1 new IaC env loader

## What changes

- **NEW `iac:bootstrap-pangolin-client` command** (capability `bonneagar-iac-merge`): installs the pangolin CLI binary + mints a Pangolin client via the new 4 client-mgmt methods + writes the credentials to `.env` + Infisical + renders the newt docker-compose.yaml.
- **NEW `iac:sync:clients` command** (capability `bonneagar-iac-merge`): walks `bonneagar/iac/clients/*.yaml`, ensures every declared client exists in the Pangolin Integrations API.
- **PangolinClient extended to 20 methods** (capability `bonneagar-iac-merge`): 4 NEW methods on `/api/v1/integration/clients` (`listClients`/`getClient`/`createClient`/`deleteClient`) + the `PangolinClientCert` typed model.
- **`iac:rotate-auth` bug fix** (capability `bonneagar-iac-merge`): the Pangolin rotation now correctly extracts `.apiKey` from the `PocketIdAdminKey` object and records the metadata in the audit record.
- **NEW `bonneagar/iac/load-env.ts`** (capability `bonneagar-iac-merge`): the missing piece — explicitly loads the repo-root `.env` into `process.env` so the IaC commands work when invoked from `bonneagar/iac/`.
- **NEW `stacks/newt-arm1-oci/`** (capability `infrastructure-stacks`): 6 GOLD_STANDARD files for the arm1-oci newt container (compose.yaml with bons-locket-shim:infisical-0.2.0 sidecar + sidecar.yaml sentinel + secrets.env with 2 `infisical://dev-baile/pangolin/clients/arm1-oci/{id,secret}` URIs + pangolin.yaml no-op + blueprint.yaml no-op + .env.example).
- **2 NEW Komodo procedures** (capability `bonneagar-komodo-gitops`): `deploy-pangolin-client-arm1-oci` (calls `iac:bootstrap-pangolin-client --host=arm1-oci --type=machine`) + `deploy-pangolin-client-bunchloch` (calls `--type=user` for the operator-laptop).
- **`cross-cutting.toml` resource-sync extended** (capability `bonneagar-komodo-gitops`): references the 2 NEW procedures.
- **`scripts/deploy-full.ts` extended to 10 phases** (capability `infrastructure-stacks`): inserts 3 NEW phases (2 = iac-auth-rotate, 3 = pocketid-oidc-wire, 4 = pangolin-client-install) + combines dagster-materialize + dagster-sensor-health-gate into a single phase 10.
- **`scripts/deploy-full.sh` extended to 10 phases** (capability `infrastructure-stacks`): `PHASE_NAMES` array + phase validation regex (`^[1-8]$` → `^(10|[1-9])$`).
- **AGENTS.md drift updates** (capability `infrastructure-stacks`): root AGENTS.md + bonneagar/AGENTS.md counts updated.

## Out of scope

- The `hermes` restart loop (issue #XXX — tracked separately).
- The `lakehouse-nimtable` + `lakehouse-olake` unhealthy alpine containers (separate TODO; they use `alpine + sh -c`).
- The `komodo-recover.sh` flow (the IaC Komodo password reset is a separate procedure; this change just adds the iac:rotate-auth bug fix).
- Cross-repo changes (`leabharlann/` is a read-only consumer).
- Cloudflare R2 production deployment.

## Dependencies

```markdown
## Dependencies

`Blocked by: none`

`Blocked by (soft): 2026-08-08-full-local-bunchloch-ireland-england-platform-deploy-v1`
(That change ships the 7-phase deploy:full; this change extends it to 10 phases and adds the auth-rotation phases. The 10-phase v2 is backwards-compatible — the new phases are inserted between the existing preflight (1) and control-plane (5) phases.)

`Blocked by (soft): 2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1`
(The Qwen DashScope API is DEFERRED 2026-08-09 per issue #147; this change does not depend on it.)

`Affected repos: cianfhoghlaim, bonneagar`
```

## Impact

- **Affected specs** (5 ADDED Requirements across 2 specs):
  - `bonneagar-iac-merge` — 3 ADDED Requirements
  - `infrastructure-stacks` — 2 ADDED Requirements
- **Affected code/config** (~17 files):
  - 7 IaC TypeScript files (`iac/clients/pangolin-client.ts` + `iac/models/pangolin.ts` + `iac/commands/{bootstrap-pangolin-client,sync-clients}.ts` + `iac/cli.ts` + `iac/commands/rotate-auth.ts` + `iac/commands/bootstrap.ts` + NEW `iac/load-env.ts`)
  - 6 new stack files at `bonneagar/stacks/newt-arm1-oci/`
  - 2 new Komodo procedures + 1 resource-sync update
  - 2 script files (`deploy-full.ts` + `deploy-full.sh`)
  - 2 `package.json` scripts (`iac:bootstrap-pangolin-client` + `iac:sync:clients`)
  - 1 root AGENTS.md drift count update
- **No secret values written to disk**: all `infisical://dev-baile/...` refs hydrated by mise + Locket + the new `load-env.ts`.
- **Backwards-compatible**: the existing 8-phase `deploy:full` continues to work because phases 2-4 are NEW (inserted between the existing preflight and control-plane phases; the renumbering 2→5, 3→6, 4→7, 5→8, 6→9, 7+8→10 is intentional).
- **Cross-cutting observability**: every IaC command emits a JSON audit record to `/tmp/{command-name}-{ts}.json`.

## Cross-references

- `openspec/specs/bonneagar-iac-merge/spec.md` — the IaC capability spec
- `openspec/specs/infrastructure-stacks/spec.md` — the 92-stack catalogue spec
- `openspec/changes/archive/2026-08-01-lakehouse-and-reproducible-deploy-v1/` — the 7-phase deploy:full that this extends
- `openspec/changes/archive/2026-07-14-iac-sync-sites-pangolin-integrations-api-v1/` — the canonical Pangolin Integrations API change
- `bonneagar/AGENTS.md` — the IaC subdirectory guide
- `bonneagar/PANGOLIN-SETUP.md` — the manual-step setup guide
- `bonneagar/deploy-runbooks/pocketid-pangolin-komodo-onboarding.md` — the 1-shot OIDC wiring script
- https://docs.pangolin.net/manage/clients/install-client — the canonical Pangolin client-install docs