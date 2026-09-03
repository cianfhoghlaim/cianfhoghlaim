# Change: 2026-07-14-iac-sync-sites-pangolin-integrations-api-v1

## Why

The bonneagar IaC has 2 of 3 layers that programmatically sync state to live services:

1. **`iac:sync:secrets`** → Infisical (POST secrets to `dev-baile` vault)
2. **`iac:sync:resources`** → Pangolin private resources (PUT `/org/{orgId}/site-resource`)

The **3rd layer — newt site provisioning** — is **missing**. The current `iac:bootstrap` Phase 6 logs a TODO: *"Newt deploy not yet automated; pull the fosrl/newt image manually"*. This means newt sites are created manually via the Pangolin UI, then the `newtId` + `newtSecret` are manually copy-pasted into Infisical + the Locket sidecar pattern. That workflow is fragile and undocumented.

The Pangolin Integrations API has a clean endpoint: **`POST /org/{orgId}/site`** which creates a newt site and returns the credentials in the response (`data.newtId` + `data.newtSecret`). The bons iac already has a `PangolinClient.createSite()` method — it's just never wired into a command.

## What Changes

### 1. New file: `iac/commands/sync-sites.ts` (~120 LOC)

Walks `stacks/*/site.yaml`; for each declared site:
1. `GET /org/{orgId}/site/{niceId}` to check if it already exists
2. If not, `POST /org/{orgId}/site` to create it → returns `{ id, newtId, newtSecret }`
3. Write the credentials back to `~/.env` (local) AND to Infisical (so other hosts can fetch via Locket)

### 2. New file: `iac/sources/discover-sites.ts` (~60 LOC)

The discoverer for `stacks/*/site.yaml`. Mirrors `discover-resources.ts` but for sites.

### 3. New convention file: `stacks/newt/site.yaml`

The bunchloch-newt site declaration. Defines `niceId` + `name` + `address` (WireGuard IP range) + `type: local` + `infisicalSecretPrefix` (the env-var names the credentials get written to).

### 4. Wire into `iac:bootstrap` Phase 6 (replace the TODO)

```ts
// Phase 6: Newt (Pangolin tunnel client) — automate via iac:sync:sites
logStep("Phase 6: Newt (Pangolin tunnel client) — sync-sites");
await syncSites();
```

### 5. Wire into `iac:cli.ts` dispatcher

Add the `sync:sites` case to the switch statement.

### 6. Wire into `package.json` scripts

Add `"iac:sync:sites": "bun run iac/cli.ts sync:sites"`.

## Affected specs

| Spec | Why |
|:--|:--|
| `agent-platform-cluster` | Adds 1 ADDED Requirement: "iac:sync:sites provisions newt sites via the Pangolin Integrations API" |

## Acceptance gates

- [ ] `openspec validate 2026-07-14-iac-sync-sites-pangolin-integrations-api-v1 --strict` returns 0
- [ ] `bun run iac:plan` discovers the bunchloch-newt site
- [ ] `bun run iac:sync:sites --dry-run` reports the correct action
- [ ] (After auth fix from the auth-repair change) `bun run iac:sync:sites` successfully creates the site + writes credentials to .env

## Dependencies

`Blocked by: none` (can be developed in isolation; auth required to test)

`Blocked by (soft): 2026-07-14-repair-bonneagar-iac-3-way-auth-v1` (the auth must be fixed before smoke-test)

`Affected repos: bonneagar` (the code is all in bonneagar)

## Cross-repo sync

See `cross-repo-sync.md` — **bonneagar only** (no cianfhoghlaim files touched directly; the openspec change tracks the work).

## Out of scope

- Implementing Pocket ID OIDC client_credentials flow (tracked in `2026-07-14-repair-bonneagar-iac-3-way-auth-v1`)
- The arm1-oci side newt provisioning (tracked in `2026-07-14-deploy-pangolin-newt-arm1-oci-v1`)
