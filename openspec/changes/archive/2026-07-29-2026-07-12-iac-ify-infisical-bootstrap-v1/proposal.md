## Deferred - Blocked on cross-region-pipeline spec

This change is **deferred** pending the `cross-region-pipeline` capability spec (currently `requirements 0` in `openspec/specs/cross-region-pipeline/spec.md`).

When that spec is added, this work can be re-scoped under the British Isles / Americas / EU / Commonwealth umbrella. No code has been written for this change.

## Deferred - Blocked on cross-region-pipeline spec

This change is **deferred** pending the `cross-region-pipeline` capability spec (currently `requirements 0` in `openspec/specs/cross-region-pipeline/spec.md`).

When that spec is added, this work can be re-scoped under the British Isles / Americas / EU / Commonwealth umbrella. No code has been written for this change.

# IaC-ify the Infisical Stack — Replace the Undocumented Deployment with a Reproducible Komodo-Managed One

## Why

The bons IaC currently has 4 separate Infisical-related issues:

1. **Undocumented deployment on arm1-oci** — container `3c1be3d92f88` was deployed via raw `docker run` (not in the bons IaC), so its secrets, admin credentials, and stack topology are invisible to GitOps. No one knows the admin password.

2. **A second, redundant Infisical** — `infisical-backend` runs locally on bunchloch as a dev instance. The user has been told this is redundant and wants it gone.

3. **`infisical-first` Komodo procedure uses raw `ssh arm1-oci`** — this is an operator step that defeats the entire IaC premise. It cannot run from a CI agent, dagger workflow, or a remote operator laptop without SSH credentials to arm1-oci.

4. **`@infisical/sdk@5.0.2` is broken** — the bons IaC's `iac/clients/infisical-client.ts` uses this SDK and we've hit bugs in three places (silent auth failures, JSON vs form-encoded bodies, missing high-level methods). The `rotate-auth` already has a working direct-REST fallback at the bottom of the file that we should promote to the canonical client.

Combined, this means: **the bons IaC's 3-way credential rotation cannot complete, the Locket sidecar pattern relies on a manually-maintained secrets vault, and there's no IaC-driven way to recover if Infisical is ever rebuilt.**

## What Changes

### Architecture decision: single canonical Infisical on arm1-oci

The bons AGENTS.md names Infisical as an `infrastructure` stack that belongs on arm1-oci. The bons IaC already has `komodo/stacks/infisical-arm1-oci.toml` and `stacks/infisical/` with a 6-file GOLD_STANDARD contract — the deployment definition is ready, just never executed through Komodo.

We abandon the undocumented `3c1be3d92f88` container (after exporting any unique secrets), and the bunchloch local Infisical. The fresh Komodo-managed Infisical becomes the only one. Locket on every other host fetches from this one.

### 5 deliverables (in implementation order)

1. **Replace `@infisical/sdk` with direct REST** in `iac/clients/infisical-client.ts`. Promote the `fetchInfisicalSecret` working pattern from `iac/commands/rotate-auth.ts`. Use form-encoded bodies for `/api/v1/auth/universal-auth/login` (server expects this, not JSON). Add fallback URL discovery: `INFISICAL_URL` env → `http://localhost:8081` (dev) → `https://infisical.cianfhoghlaim.ie` (production).

2. **New `iac:bootstrap-infisical` command** mirroring `iac:bootstrap-pocketid-admin`. Detects if Infisical has any admin user. If no: use Chrome MCP (available in this environment via `chrome_*` tools) to drive the `/signup/setup` wizard, create the first admin via email/password (Infisical uses passkey OR email/password — v0.161+ supports both), then bootstrap a `bons-iac` machine identity with Admin role. If yes: skip to identity verification + machine identity seeding. Writes machine identity client_id + client_secret to `.env`.

3. **New `komodo/procedures/deploy-infisical-arm1-oci.toml`** that orchestrates the full deploy: preflight (Docker + Komodo reachability), volume ensure, pull image, deploy via Komodo's stack runner, health check, and finally invoke `bun run iac:bootstrap-infisical` as a sub-stage. Writes a JSON audit record to `/tmp/infisical-bootstrap-{ts}.json`.

4. **Rewrite `komodo/procedures/infisical-first.toml`** to remove the `ssh arm1-oci` operator step. Replace with: HTTP check on `/api/status`, HTTP check on the dev-baile project via the Infisical API (using the machine identity), and HTTP check that all 8 required machine identities are seeded (bons-iac, pocket-id, komodo, pangolin, tinyauth, openclaw, openchamber, hermes).

5. **Update `komodo/resource-syncs/cross-cutting.toml`** to add the new `deploy-infisical-arm1-oci` procedure and fix the outdated "4 procedures" comment.

### Cross-cutting implications

- The 6-file `stacks/infisical/` contract already has the bootstrap pattern (hardcoded secrets in `compose.yaml` for first deploy, `infisical://` references for subsequent deploys via Locket). No changes needed there.
- The chicken-and-egg is solved by hardcoding the bootstrap creds in `compose.yaml`'s environment section for the first deploy, then having `iac:bootstrap-infisical` move them into Infisical after the first admin is created.
- All other stacks already use `infisical://dev-baile/...` references resolved by Locket — they automatically benefit from this work.

## Impact

- **`iac:rotate-auth`** will finally succeed for all 3 surfaces (Pangolin, Komodo, Infisical)
- **`iac:health`** will show `✓ infisical` instead of skipping
- **`bun run iac:bootstrap`** will work end-to-end from zero to all-6-healthy
- **One single source of truth for secrets** — no more local-vs-remote Infisical split
- **Chrome MCP** handles the only manual-feeling step (initial admin creation) — but it's fully automated, just runs in a browser session the agent drives
- **The bunchloch local Infisical can be torn down** after this change is in place (not part of this change, but enabled by it)

## Decisions

| Question | Answer |
|:--|:--|
| Q1: Single canonical Infisical? | **A** — arm1-oci is canonical; bunchloch local torn down |
| Q2: First admin bootstrap approach? | **C** — abandon the undocumented `3c1be3d92f88` container; deploy fresh Komodo-managed one; Chrome MCP drives the `/signup/setup` wizard for the first admin |
| Q3: Scope? | **A** — Infisical-only (this change); Komodo + Pangolin integration improvements are a follow-up |

## Non-goals

- Not migrating secrets from the old `3c1be3d92f88` container to the new one (operator can do this manually if they care; fresh Infisical starts clean)
- Not tearing down the bunchloch local Infisical (separate, follow-up)
- Not improving the Komodo + Pangolin IaC integrations beyond what they need for the Infisical procedure to work (separate, follow-up)
- Not migrating the 8 machine identities across Infisical versions (created fresh)

## Dependencies

- **Blocked by**: none
- **Blocked by (soft)**: `2026-07-14-repair-bonneagar-iac-3-way-auth-v1` (this change is the IaC-ification it implicitly assumed; soft because both can proceed independently, but archive ordering matters)
- **Affected repos**: bonneagar (all IaC code changes), cianfhoghlaim (this openspec change — proposal + tasks + 2 spec deltas)
- **External**: Pocket ID OIDC bootstrap (already complete on `pick-5b-bonneagar-v5-continuation` at `d06125c0b` and `2230c3c3b`), Komodo Core on bunchloch (already healthy), Chrome MCP in agent runtime (already available)
- **Chicken-and-egg resolution**: the first `iac:bootstrap-infisical` deploy hardcodes Infisical bootstrap secrets (`ENCRYPTION_KEY`, `AUTH_SECRET`, `POSTGRES_PASSWORD`, etc.) in `stacks/infisical/compose.yaml` so the stack can start before Infisical itself exists. After the first admin is created + the bons-iac machine identity is seeded, the next deploy sources those same secrets from Infisical via Locket (chicken-and-egg resolved).

## Cross-repo sync

This change spans 2 repos: **bonneagar** (the IaC) and **cianfhoghlaim** (the openspec).

```
COMMIT ORDER:
1. cianfhoghlaim   — openspec/changes/2026-07-12-iac-ify-infisical-bootstrap-v1/
                     (proposal.md + tasks.md + 2 spec deltas + cross-repo-sync.md)
2. bonneagar       — iac/clients/infisical-rest.ts (new)
                     iac/clients/infisical-client.ts (rewrite to use the REST helper)
                     iac/commands/bootstrap-infisical.ts (new)
                     iac/commands/rotate-auth.ts (use the fixed client)
                     iac/commands/health.ts (use the API not local sqlite)
                     iac/cli.ts (register the new command)
                     package.json (drop @infisical/sdk if no other consumer)
                     komodo/procedures/deploy-infisical-arm1-oci.toml (new)
                     komodo/procedures/infisical-first.toml (rewrite, no more ssh)
                     komodo/resource-syncs/cross-cutting.toml (add the new procedure)
                     stacks/komodo/secrets.env (use infisical:// for the admin password)
                     stacks/pangolin/secrets.env (add PANGOLIN_API_KEY via infisical://)

PUSH TARGETS:
- cianfhoghlaim  → https://github.com/cianfhoghlaim/cianfhoghlaim.git
                   branch: main (no bons worktree in this repo — openspec lives in-tree)
                   PR: not required (openspec changes archive via openspec archive command)
- bonneagar      → https://github.com/cianfhoghlaim/bonneagar.git
                   branch: pick-5b-bonneagar-v5-continuation
                   PR: updates PR #7 (the existing pick-5b-pr)

WHY THIS ORDER:
- The cianfhoghlaim/openspec change MUST be committed first so that
  the bons IaC implementation has the spec it implements against.
- The bonneagar IaC changes implement the spec — they can be merged
  independently.
- The cianfhoghlaim openspec change CANNOT archive until the bons
  IaC deploy has been verified end-to-end (the `archive` command in
  the openspec change should be wired to a 3-way health check, similar
  to `archive-agent-platform-cluster-arm1-oci-automation-v1`).

DEPLOYMENT:
1. Merge bonneagar PR → IaC is live on the main bons worktree
2. `cd bonneagar && bun run iac:bootstrap-infisical` (operator one-shot)
3. Verify `bun run iac:health` shows ✓ infisical
4. `cd cianfhoghlaim/openspec && openspec archive 2026-07-12-iac-ify-infisical-bootstrap-v1 --yes`
```

## Non-goals
