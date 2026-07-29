# Cross-Repo Sync: 2026-07-15-iac-ify-arm1-oci-control-plane-v1

This change touches **2 repos**: `cianfhoghlaim` (openspec) and `bonneagar` (IaC code). They MUST be committed in this order:

## Order of Operations

```
[1] cianfhoghlaim  → openspec/changes/2026-07-15-iac-ify-arm1-oci-control-plane-v1/
                     (proposal.md + tasks.md + 2 spec deltas + cross-repo-sync.md)
                          ↓
[2] bonneagar      → iac/pulumi/oci/{deploy,setup}.ts (Pulumi IaC migration)
                     iac/commands/{bootstrap-locket-binary,bootstrap-control-plane,
                                     wire-pocketid-as-oidc,deploy-periphery,deploy-newt}.ts
                     iac/commands/bootstrap.ts (Phase 1 wire-up)
                     iac/commands/bootstrap-pocketid-admin.ts (--api-only flag)
                     iac/cli.ts + iac/package.json (register new commands)
                     iac/docs/locket.md (port from /stedding/locket)
                     stacks/control-plane/{compose,sidecar,secrets,pangolin,
                                            blueprint}.yaml + .env.example + README.md
                          ↓
                   (push to bons standalone repo's pick-5b-bonneagar-v5-continuation branch)
                          ↓
[3] operator       → cd bonneagar && bun run iac:bootstrap-control-plane-bunchloch
                     (Phase 1: local dev/canary)
                          ↓
[4] operator       → cd bonneagar && bun run iac:bootstrap-control-plane-arm1-oci
                     (Phase 2: production via Pulumi IaC)
                          ↓
[5] cianfhoghlaim  → openspec archive 2026-07-15-iac-ify-arm1-oci-control-plane-v1 --yes
                     (after iac:health shows ✓ on both bunchloch + arm1-oci)
```

## Repo 1: cianfhoghlaim

**Files to commit** (under `openspec/changes/2026-07-15-iac-ify-arm1-oci-control-plane-v1/`):

- `proposal.md` (with `## Dependencies` + `## Cross-repo sync` sections)
- `tasks.md`
- `specs/agent-platform-cluster/spec.md` (delta)
- `specs/infrastructure-stacks/spec.md` (delta)
- `cross-repo-sync.md` (this file)

**Branch**: `main` (openspec changes archive via `openspec archive`, not via PR)

**Push target**: `https://github.com/cianfhoghlaim/cianfhoghlaim.git`

**Commit message**: `feat(openspec): iac-ify the arm1-oci control plane (bundled stack + IaC orchestrator)`

## Repo 2: bonneagar

**Files to commit** (under `bonneagar/`):

| File | Action | Description |
|:--|:--|:--|
| `iac/pulumi/oci/deploy.ts` | UPDATED | Replace `@infisical/sdk` with `iac/clients/infisical-rest.ts` |
| `iac/pulumi/oci/setup.ts` | UPDATED | Replace `@infisical/sdk` with `iac/clients/infisical-rest.ts` |
| `iac/commands/bootstrap.ts` | UPDATED | Phase 1: replace TODO with actual Pulumi IaC call |
| `iac/commands/bootstrap-pocketid-admin.ts` | UPDATED | Add `--api-only` flag (Q4: prefer admin API over Chrome MCP) |
| `iac/commands/bootstrap-locket-binary.ts` | NEW | Downloads locket binary locally for IaC use |
| `iac/commands/wire-pocketid-as-oidc.ts` | NEW | Wires Pocket ID as OIDC IdP for Komodo + Pangolin |
| `iac/commands/deploy-periphery.ts` | NEW | Provisions Komodo Periphery on a managed host |
| `iac/commands/deploy-newt.ts` | NEW | Provisions Newt tunnel on a managed host |
| `iac/commands/bootstrap-control-plane.ts` | NEW | The operator's one-shot (runs all 8 phases) |
| `iac/cli.ts` | UPDATED | Register 6 new commands |
| `iac/package.json` | UPDATED | Add 8 new bun scripts (6 commands + 2 host-specific one-shots) |
| `iac/docs/locket.md` | NEW | Port provider patterns from `/stedding/locket` |
| `komodo/resource-syncs/cross-cutting.toml` | UPDATED | Add Pulumi IaC to the cross-cutting prereq order (position 0) |
| `stacks/control-plane/compose.yaml` | NEW | 7 services + 5 locket sidecars + 3 data store services + traefik |
| `stacks/control-plane/sidecar.yaml` | NEW | Locket Infisical provider config |
| `stacks/control-plane/secrets.env` | NEW | `infisical:///` refs for each service's secrets |
| `stacks/control-plane/pangolin.yaml` | NEW | Traefik routes for the 5 public services |
| `stacks/control-plane/blueprint.yaml` | NEW | Komodo Resource Sync manifest |
| `stacks/control-plane/.env.example` | NEW | Bootstrap-mode env vars |
| `stacks/control-plane/README.md` | NEW | Operator handoff |

**Branch**: `pick-5b-bonneagar-v5-continuation` (existing bons worktree branch)

**Push target**: `https://github.com/cianfhoghlaim/bonneagar.git` (remote: `archive-bonneagar`)

**PR**: updates the existing PR #7 (the pick-5b-pr from prior commits)

**Commit message**: `feat(iac): IaC-ify arm1-oci control plane (bundled stack + bootstrap orchestrator)`

## Why This Order

1. **cianfhoghlaim first** — the spec change MUST exist before the IaC code that implements it. The bons IaC code (step 2) is what makes the openspec archive (step 5) possible.
2. **bonneagar second** — the IaC code implements the spec. It can be merged independently of the openspec change. The IaC's own CI validates that the code compiles.
3. **Operator deploy third + fourth** — Phase 1 (bunchloch local) then Phase 2 (arm1-oci production) — the user explicitly chose B (bunchloch first).
4. **cianfhoghlaim archive last** — only after the operator has verified the deploy works on both bunchloch AND arm1-oci.

## What Cannot Be Done Without Both

The bons IaC code (Repo 2) cannot compile without the openspec spec (Repo 1) describing what the behavior SHOULD be. The openspec spec cannot archive without the bons IaC code (Repo 2) being deployed and verified.

If you try to merge Repo 2 before Repo 1, the spec delta will be missing — the IaC code will be implementing undocumented behavior. Bad.
If you try to archive Repo 1 before Repo 2 deploys, the spec will claim a behavior that doesn't exist yet. Bad.

## Rollback Plan

If the bons IaC change breaks something:
- `git revert` the bons IaC commit
- The openspec change is still in `openspec/changes/` (not yet archived) — no rollback needed
- The arm1-oci Infisical can be left running (it's idempotent — re-deploy just hits the existing instance)

If the openspec change archives prematurely:
- `openspec unarchive 2026-07-15-iac-ify-arm1-oci-control-plane-v1` brings it back to `openspec/changes/`
- The spec text is still valid — it's just moved to `archive/`

## Branch Names

- cianfhoghlaim: `main` (openspec archive uses the default branch)
- bonneagar: `pick-5b-bonneagar-v5-continuation` (existing bons worktree branch)

## Verification Commands

After both repos merge:

```bash
# On bons IaC
cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar

# Phase 1: local canary
bun run iac:bootstrap-control-plane-bunchloch

# Phase 2: production
bun run iac:bootstrap-control-plane-arm1-oci

# Verify
bun run iac:health
# Expected: ✓ komodo + ✓ pangolin + ✓ infisical + ✓ newt + ✓ pocket-id + ✓ tinyauth

# On openspec
cd /Users/cianmacandeisigh/dev/kings_college_galway
openspec validate 2026-07-15-iac-ify-arm1-oci-control-plane-v1 --strict
# Expected: Validation passes

openspec archive 2026-07-15-iac-ify-arm1-oci-control-plane-v1 --yes
# Expected: Change moves to openspec/changes/archive/
```
