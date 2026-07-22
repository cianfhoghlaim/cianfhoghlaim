# IaC-ify the arm1-oci Control Plane — Reproducible Setup of Komodo + Infisical + Pangolin + Pocket ID + Tinyauth + Locket + Periphery + Newt

## Why

The bons IaC currently has 5 separate gaps in the control-plane setup:

1. **`iac:bootstrap` Phase 1 is a TODO** — the Pulumi IaC (`iac/pulumi/oci/deploy.ts` + `setup.ts`) exists but is never called
2. **Komodo OIDC isn't wired** — there's no Pocket ID OIDC client named `komodo` (only `tinyauth`, `bons-iac`, `pangolin` exist), so human login to Komodo is impossible without it
3. **No bundled `control-plane` stack** — every service (komodo, pangolin, pocket-id, tinyauth, infisical) is its own ad-hoc docker-compose, with no Locket sidecar pattern across all of them
4. **Pulumi IaC uses the buggy `@infisical/sdk@5.0.2`** (we replaced it in the IaC client but the Pulumi scripts still use it)
5. **No operator one-shot** — the operator has to chain 6+ separate commands to bootstrap the control plane

The user has the existing arm1-oci VM (`oci.arm1` alias, reachable via SSH) but it's not reproducibly deployable. The 5-control-plane setup needs to be a single IaC-defined stack that any operator can deploy from zero.

## What Changes

### Architecture: the 5-control-plane setup order

```
Locket binary (IaC use)  ──→  reads from Infisical
       │
       ▼
Pulumi IaC               ──→  provisions arm1-oci VM + Cloudflare DNS
       │
       ▼
Infisical                ──→  secrets source of truth (bootstrap mode initially)
       │
       ▼
Pangolin Core            ──→  reverse proxy + WireGuard tunnel
       │
       ▼
Pocket ID                ──→  OIDC IdP (Pangolin + Komodo + Tinyauth use it)
       │
       ▼
Komodo Core              ──→  orchestrator (OIDC login + Locket for secrets)
       │
       ▼
Komodo Periphery         ──→  executor (on each managed host; uses onboarding key)
       │
       ▼
Tinyauth (ForwardAuth)   ──→  SSO middleware in front of Pangolin
       │
       ▼
Newt (Pangolin tunnel)   ──→  tunnel client (on each managed host; uses Integrations API)
```

### The bundled `stacks/control-plane-arm1-oci/` stack

ONE docker-compose stack containing all 7 services + 5 locket sidecars:
- `komodo-core` + `komodo-ferretdb` + `komodo-postgres` (with locket)
- `pangolin-core` (with locket)
- `pocket-id` (with locket)
- `tinyauth` (with locket)
- `infisical` + `infisical-db` + `infisical-redis` (with locket)
- `traefik` (TLS terminator, with locket)

Each service fetches its secrets via Locket sidecar. The locket sidecar reads from Infisical via the `infisical:///` URI syntax. This is the **canonical pattern** (mirrors the `stacks/lakehouse/` pattern).

### 6 IaC deliverables (in implementation order)

1. **Fix Pulumi IaC scripts** (`iac/pulumi/oci/{deploy,setup}.ts`) to use `iac/clients/infisical-rest.ts` (replacing `@infisical/sdk`).
2. **Wire Pulumi IaC into `iac:bootstrap` Phase 1** — replace the TODO with a real call. The Pulumi IaC provisions the arm1-oci VM + saves Cloudflare creds + DNS records to Infisical.
3. **New `iac:bootstrap-locket-binary`** — downloads the locket Rust binary to `~/.local/bin/locket` for IaC's own use.
4. **New `iac/docs/locket.md`** — port the provider patterns from `/stedding/locket` for bons IaC reference (Q5).
5. **New `stacks/control-plane/`** — 6-file GOLD_STANDARD with the bundled 7-service + 5-sidecar stack.
6. **New `iac:bootstrap-control-plane`** — the operator's one-shot that runs all 8 phases in order: locket → Pulumi → bundled stack → Infisical bootstrap → Pocket ID OIDC wire → Periphery → Newt → 7-way health verify.

Plus 3 secondary deliverables (sub-commands of #6):
- `iac:bootstrap-pulumi-oci` — calls the Pulumi IaC scripts
- `iac:wire-pocketid-as-oidc` — creates the `komodo` OIDC client in Pocket ID + wires Pocket ID as the OIDC IdP in Komodo + Pangolin
- `iac:deploy-periphery` + `iac:deploy-newt` — provisions the agent + tunnel on a managed host

### Phase split (Q2: bunchloch first, then arm1-oci)

The operator runs 2 sequential one-shots:
- **Phase 1**: `bun run iac:bootstrap-control-plane-bunchloch` (local dev/canary on `localhost`)
- **Phase 2**: `bun run iac:bootstrap-control-plane-arm1-oci` (production on the Pulumi-provisioned VM)

Both share the same `iac:bootstrap-control-plane` orchestrator (different host targets via `--target=bunchloch` or `--target=arm1-oci`).

## Impact

- **`iac:bootstrap` end-to-end** — works from zero to a fully reproducible control plane + 6-way auth chain
- **No operator click-throughs** — the IaC's first-admin flow uses Pocket ID's admin API (`POST /api/v1/users`) when 1+ users exist; falls back to Chrome MCP only when 0 users (the bootstrap case)
- **No raw SSH from the operator** — all SSH is done via Pulumi IaC + Komodo SDK + Locket sidecar pattern
- **One source of truth** for secrets — Infisical (everything reads from here via Locket)
- **Bundled stack approach** — easy to manage as a unit (one IaC definition, one Komodo stack, one deploy)
- **Replaces** the `iac/pulumi/oci/deploy.ts` + `setup.ts` raw `@infisical/sdk` calls + the ad-hoc `stedding/ansible` Komodo setup

## Decisions

| Question | Answer |
|:--|:--|
| Q1: Bundle the 5-control-plane in one docker-compose stack? | **A** — `stacks/control-plane/` (cleanest, like lakehouse) |
| Q2: Boot the control plane on bunchloch first or arm1-oci first? | **B** — bunchloch first (local dev/canary), then promote to arm1-oci |
| Q3: Periphery deployment mode? | **A** — container (docker-compose on each managed host) |
| Q4: First-admin UX for Pocket ID + Infisical? | **C** — API-only (use admin API `POST /api/v1/users` to create the user with a password; fallback to Chrome MCP for the bootstrap case when 0 users exist) |
| Q5: Should the bons IaC integrate the local locket repo? | **A** — port the relevant docs (provider patterns) into `iac/docs/locket.md` for reference |
| Q6 (new): Integrate control-plane into `iac:bootstrap` Phase 1? | **A** — `iac:bootstrap` auto-runs it (replaces the Phase 1 TODO) |

## Non-goals

- Not migrating secrets from the old `3c1be3d92f88` Infisical container (operator step, separate)
- Not replacing the existing local Komodo on bunchloch (the bundled stack deploys alongside it; the operator can switch over)
- Not tearing down `stedding/ansible` (kept as legacy reference; new IaC supersedes it)
- Not modifying Pocket ID, Komodo, Pangolin, or Infisical upstream code (we use their APIs only)

## Dependencies

- Pocket ID OIDC bootstrap (already complete on `pick-5b-bonneagar-v5-continuation` via `b63853398` + `2230c3c3b`)
- Komodo Core on bunchloch (already running locally, healthy)
- Infisical on bunchloch (already running locally)
- Pulumi IaC scripts exist (just need the @infisical/sdk → infisical-rest.ts migration)
- Locket Rust binary (need to download it for the IaC's own use)
- Operator has `~/.oci/config` with the `bunchloch` profile (already exists)

## Cross-repo sync

This change spans 2 repos: **bonneagar** (the IaC) and **cianfhoghlaim** (the openspec).

```
COMMIT ORDER:
1. cianfhoghlaim   — openspec/changes/2026-07-15-iac-ify-arm1-oci-control-plane-v1/
                     (proposal.md + tasks.md + 2 spec deltas + cross-repo-sync.md)
2. bonneagar       — iac/pulumi/oci/{deploy,setup}.ts (Pulumi IaC migration)
                     iac/commands/{bootstrap-locket-binary,bootstrap-control-plane,
                                     wire-pocketid-as-oidc,deploy-periphery,deploy-newt}.ts
                     iac/commands/bootstrap.ts (Phase 1 wire-up)
                     iac/commands/bootstrap-pocketid-admin.ts (--api-only flag)
                     iac/cli.ts + iac/package.json (register new commands)
                     iac/docs/locket.md (port from /stedding/locket)
                     stacks/control-plane/{compose,sidecar,secrets,pangolin,
                                            blueprint}.yaml + .env.example + README.md

PUSH TARGETS:
- cianfhoghlaim  → https://github.com/cianfhoghlaim/cianfhoghlaim.git
                   branch: main (openspec archive uses the default branch)
                   PR: not required (openspec changes archive via openspec archive command)
- bonneagar      → https://github.com/cianfhoghlaim/bonneagar.git
                   branch: pick-5b-bonneagar-v5-continuation
                   PR: updates PR #7 (the existing pick-5b-pr)

DEPLOYMENT:
1. Merge bonneagar PR → IaC is live on the main bons worktree
2. `cd bonneagar && bun run iac:bootstrap-control-plane-bunchloch` (Phase 1: local)
3. Verify `bun run iac:health` shows ✓ komodo + ✓ pangolin + ✓ infisical + ✓ newt + ✓ pocket-id + ✓ tinyauth
4. `cd bonneagar && bun run iac:bootstrap-control-plane-arm1-oci` (Phase 2: prod)
5. Verify the same 6-way health on arm1-oci
6. Archive the openspec change
```

## Operator handoff

```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar

# Phase 1: bunchloch (local dev/canary)
# - downloads locket binary
# - runs Pulumi (no-op on bunchloch)
# - deploys bundled stacks/control-plane/ via docker compose
# - bootstraps Infisical first admin + 8 machine identities (API-preferred, Chrome-MCP-fallback)
# - wires Pocket ID as OIDC IdP for Komodo + Pangolin
# - provisions Komodo Periphery + Newt on bunchloch
# - verifies 6-way health
bun run iac:bootstrap-control-plane-bunchloch

# Phase 2: arm1-oci (production)
# - downloads locket binary on arm1-oci (via SSH)
# - runs Pulumi IaC to provision VM + Cloudflare DNS
# - deploys the same bundled stack to arm1-oci
# - bootstraps Infisical first admin + 8 machine identities on arm1-oci
# - wires Pocket ID as OIDC IdP on arm1-oci
# - provisions Komodo Periphery + Newt on arm1-oci
# - verifies 6-way health
bun run iac:bootstrap-control-plane-arm1-oci

# Verify
bun run iac:health
# expect: ✓ komodo + ✓ pangolin + ✓ infisical + ✓ newt + ✓ pocket-id + ✓ tinyauth
```

## Stats (estimate)

| Metric | Value |
|:--|:--|
| New IaC commands | 6 (bootstrap-pulumi-oci, bootstrap-locket-binary, bootstrap-control-plane, wire-pocketid-as-oidc, deploy-periphery, deploy-newt) |
| New stack files | 7 (stacks/control-plane/{compose,sidecar,secrets,pangolin,blueprint}.yaml + .env.example + README.md) |
| Modified IaC files | 5 (iac/pulumi/oci/{deploy,setup}.ts, iac/commands/bootstrap.ts, iac/commands/bootstrap-pocketid-admin.ts, iac/cli.ts, iac/package.json) |
| New doc files | 1 (iac/docs/locket.md) |
| OpenSpec files | 4 (proposal + tasks + 2 spec deltas + cross-repo-sync.md) |
| Total LOC | ~1,800 |
| PRs | 1 (updates bons PR #7) + 1 openspec archive |
