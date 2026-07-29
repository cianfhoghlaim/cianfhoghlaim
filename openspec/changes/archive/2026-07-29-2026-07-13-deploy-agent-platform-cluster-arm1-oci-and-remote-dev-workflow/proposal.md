## Superseded by recent IaC commits

All work proposed here has been shipped in the IaC cluster's recent commits. See the bons-locker-shim v0.2.0 release + the IaC stack contract reconciliation + the agent-platform cluster deploy for the authoritative record.

## Superseded by recent IaC commits

All work proposed here has been shipped in the IaC cluster's recent commits. See the bons-locker-shim v0.2.0 release + the IaC stack contract reconciliation + the agent-platform cluster deploy for the authoritative record.

# Change: 2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow

## Why

The Cianfhoghlaim platform has 3 agent surfaces — **hermes** + **openclaw** + **openchamber** — currently deployed only on `bunchloch` (this MacBook, the workload + dev host) in dev mode. The user has confirmed all 3 should be deployed to `arm1-oci` (the control-plane host on Oracle Cloud Free Tier, Frankfurt) behind the Pangolin private resource mesh, reachable at `https://<service>.cianfhoghlaim.ie/api/health` from anywhere on the mesh.

Two missing infrastructure pieces block the arm1-oci deploy:

1. **The 3 arm1-oci stack TOMLs for the agent surfaces** — only `openclaw-arm1-oci.toml` and `openchamber-arm1-oci.toml` exist; `hermes-arm1-oci.toml` is missing. Plus the supporting infrastructure: `deploy-langfuse-arm1-oci`, `deploy-observability-arm1-oci`, and the omnibus `deploy-agent-platform-cluster-arm1-oci`.
2. **The `newt` (Pangolin client) on this Mac is not running** — its config exists at `.local/newt/docker-compose.yaml` (4 services: locket + newt + periphery + beszel-agent) but the container is dead and there's no Komodo management. Without `newt`, the Mac can't reach the arm1-oci services via `*.cianfhoghlaim.ie` from outside the cluster.

Plus the cross-cutting prerequisites (`pangolin-first`, `komodo-core`, `infisical-first`, `locket-deploy`) that the new `cross-cutting` resource-sync expects are missing — they need to exist before any arm1-oci deploy.

A `preflight:arm-oci` safety script (added by the in-flight `2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1` change) checks 4 pre-conditions before any arm-oci deploy (Pangolin health, Komodo health, Infisical health, process namespace isolation). This change makes the preflight a hard dep of every new arm1-oci procedure.

Companion integration: **ccc (CocoIndex Code)**, the canonical semantic code search tool, is bunchloch-only today (`cron-ccc-reindex-bunchloch` runs daily at 03:00 UTC on the Mac, with a `ccc-freshness` CI gate). The v1 index is host-agnostic — agents on arm1-oci will query the same index via the `ccc` MCP server in `opencode.json`. No arm1-oci-specific ccc work is needed in this change.

The remote dev workflow goal: the operator sits at this MacBook, runs `opencode` locally, and connects to `hermes` + `openclaw` + `openchamber` running on `arm1-oci` via the Pangolin mesh. The `newt` client bridges the Mac into that mesh.

## What Changes

This omnibus bundles 7 classes of changes that all share the same arm1-oci + remote-dev deploy path.

### 1. New Komodo stack: `hermes-arm1-oci`

Create `bonneagar/komodo/stacks/hermes-arm1-oci.toml` mirroring the existing `hermes-bunchloch.toml` but adapted for arm1-oci:
- `server_id = "arm1-oci"`
- `tags = ["host:arm1-oci", "tier:control-plane", "type:agent-runtime", "domain:hermes.cianfhoghlaim.ie"]`
- `run_directory = "/etc/komodo/sruth/bonneagar/stacks/hermes"`
- Uses the **public** `nousresearch/hermes-agent:v2026.7.1` (the `0.17.0` tag is private at GHCR; verified 200 at Docker Hub)

### 2. Four new Komodo procedures for arm1-oci

| Path | Stages | Notes |
|:--|:--|:--|
| `komodo/procedures/deploy-hermes-arm1-oci.toml` | 5: pre-reqs → `deploy-langfuse-arm1-oci` → `DeployStack hermes` → `ApplyBlueprint` + `init-allowlist.sh` → health | Hermes needs langfuse for the `langfuse` MCP server |
| `komodo/procedures/deploy-langfuse-arm1-oci.toml` | 4: pre-reqs → lakehouse data plane → `DeployStack langfuse` → `ApplyBlueprint` + health | Required by openclaw's arm1-oci Stage 1 |
| `komodo/procedures/deploy-observability-arm1-oci.toml` | 3: pre-reqs → `DeployStack observability + logfire + dozzle + beszel` → health | Foundation observability for the agent cluster |
| `komodo/procedures/deploy-agent-platform-cluster-arm1-oci.toml` | 6: pre-reqs (incl. `preflight:arm-oci`) → control-plane foundation (pangolin + langfuse + observability) → 3 agent surfaces (hermes + openclaw + openchamber) → Pangolin routes → health → `validate-stacks` | The omnibus. Accepts `--skip=<stage>` flags like the bunchloch omnibus |

All 4 get `server_id = "arm1-oci"` at the top of the file.

### 3. Three new Komodo `Build` resources (code-owned images)

Create the `bonneagar/komodo/builds/` directory (currently absent) and 3 build resources:

| Build | Source | Output |
|:--|:--|:--|
| `openchamber-arm1-oci` | `bonneagar/stacks/openchamber/Dockerfile.openchamber-web` | `ghcr.io/cianfhoghlaim/openchamber:1.14.1-arm1` |
| `openclaw-arm1-oci` | `bonneagar/stacks/openclaw/Dockerfile.openclaw` | `ghcr.io/cianfhoghlaim/openclaw:2026.6-arm1` |
| `hermes-arm1-oci` | (no Dockerfile — uses public Docker Hub image) | (no output; references `nousresearch/hermes-agent:v2026.7.1` directly) |

For the 2 private GHCR upstream images, the repo now builds them from local Dockerfiles. The build resources are added to the `arm1-oci.toml` resource-sync's `resource_path` so Komodo picks them up on its 60s pull.

### 4. New remote-dev workflow stack: `newt` (Pangolin client on this Mac)

| Path | Change |
|:--|:--|
| `bonneagar/stacks/newt/docker-compose.yaml` | NEW (extracted from `.local/newt/docker-compose.yaml`; 4 services: locket + newt + periphery + beszel-agent) |
| `bonneagar/stacks/newt/{sidecar,secrets.env,pangolin,blueprint}.yaml` + `.env.example` | NEW (6-file GOLD_STANDARD contract) |
| `bonneagar/komodo/stacks/newt-bunchloch.toml` | NEW (server_id="bunchloch", tags `host:bunchloch`, `tier:control-plane`, `type:remote-tunnel`) |
| `bonneagar/komodo/procedures/deploy-newt-bunchloch.toml` | NEW (5 stages: pre-reqs → `StackUp newt-bunchloch` → check WireGuard tunnel → check Komodo periphery registration → health) |

The newt stack runs on this Mac (bunchloch), not on arm1-oci. It bridges the Mac into the Pangolin mesh so services on arm1-oci (e.g. `hermes.cianfhoghlaim.ie`) are reachable from a browser on this Mac via the Pangolin private resource route.

### 5. Four cross-cutting prerequisite procedures (unblock the `cross-cutting` resource-sync)

The `komodo/resource-syncs/cross-cutting.toml` expects 4 procedures that don't exist yet. Create them so the cross-cutting sync is consistent:

| Path | Stages |
|:--|:--|
| `komodo/procedures/pangolin-first.toml` | 3: ssh check + Pangolin health + Pocket ID OIDC ready |
| `komodo/procedures/komodo-core.toml` | 3: Komodo Core pod alive + REST API + periphery registration |
| `komodo/procedures/infisical-first.toml` | 3: Vault reachable + project=dev-baile + machine identities seeded |
| `komodo/procedures/locket-deploy.toml` | 3: locket binary present + `infisical_secret` mounted + secrets resolved ≥ 1 key |

All 4 are host-agnostic (run on every host that joins the mesh) and include the `preflight:arm-oci` step from the v6-drift change.

### 6. `server_id` field backfill across all bunchloch procedures

Add a top-level `server_id = "bunchloch"` field to the 14 existing bunchloch procedures under `komodo/procedures/` that don't have one. This is the backbone of the cross-host resource-sync filtering — without it, arm1-oci's resource-sync pulls the bunchloch procedures and shows them in its `km` UI as procedures that don't apply.

### 7. Resource-sync TOML updates

| Path | Change |
|:--|:--|
| `komodo/resource-syncs/bunchloch.toml` | MODIFIED — add comment block documenting the `server_id` convention; expand `resource_path` to include the 3 new builds + newt-bunchloch stack |
| `komodo/resource-syncs/arm1-oci.toml` | MODIFIED — add the 3 build resources + hermes-arm1-oci stack to `resource_path`; document `server_id` |
| `komodo/resource-syncs/cross-cutting.toml` | MODIFIED — explicit comment that the 4 prerequisite procedures are now in the path |

### 8. New convention doc

| Path | Change |
|:--|:--|
| `komodo/procedures/server_id_legend.md` | NEW — explains the `server_id` field, lists each procedure + its server_id, the back-compat behavior, the deprecation warning, and how to add a new procedure |

## Impact

### Affected specs (3 deltas, 0 new specs)

- **MODIFIED `agent-platform-cluster`** — +1 ADDED Requirement: "3 agent surfaces on arm1-oci (control plane)" with 3 Scenarios (openclaw / openchamber / hermes reachable via Pangolin)
- **MODIFIED `infrastructure-stacks`** — +2 ADDED Requirements: "Procedure `server_id` field for cross-host dispatch" + "Komodo `Build` resource for code-owned images" (2 Scenarios each)
- **MODIFIED `agentic-frontend-frameworks`** — +1 ADDED Requirement: "Remote dev workflow via newt (Pangolin client) on bunchloch" with 2 Scenarios

### NEW files (~24)

`openspec/changes/2026-07-13-.../`:
- `proposal.md` (~280 lines), `tasks.md` (~140 lines), `cross-repo-sync.md` (~80 lines)
- 3 spec deltas in `specs/`

`bonneagar/`:
- `stacks/openchamber/Dockerfile.openchamber-web` (the multi-stage build that landed `openchamber:local-1.14.1` last turn)
- `stacks/openclaw/Dockerfile.openclaw` (synthetic Dockerfile for openclaw)
- `stacks/newt/{docker-compose,sidecar,secrets.env,pangolin,blueprint}.yaml` + `.env.example` (6 files)
- `komodo/builds/{openchamber-arm1-oci,openclaw-arm1-oci,hermes-arm1-oci}.toml`
- `komodo/stacks/{hermes-arm1-oci,newt-bunchloch}.toml`
- `komodo/procedures/{deploy-hermes-arm1-oci,deploy-langfuse-arm1-oci,deploy-observability-arm1-oci,deploy-agent-platform-cluster-arm1-oci,deploy-newt-bunchloch,pangolin-first,komodo-core,infisical-first,locket-deploy,server_id_legend}.md` (9 procedure files + 1 doc)

### MODIFIED files (~17)

- `komodo/stacks/openchamber-arm1-oci.toml` — point image at `ghcr.io/cianfhoghlaim/openchamber:1.14.1-arm1`
- `komodo/stacks/openclaw-arm1-oci.toml` — point image at `ghcr.io/cianfhoghlaim/openclaw:2026.6-arm1`
- `komodo/resource-syncs/{bunchloch,arm1-oci,cross-cutting}.toml` — comment blocks + resource_path updates
- All 14 existing bunchloch `komodo/procedures/*-bunchloch.toml` get `server_id = "bunchloch"` (+1 line each)

### Affected hosts

- **`arm1-oci`** — receives 3 new agent surfaces (hermes + openclaw + openchamber) behind Pangolin
- **`bunchloch`** — receives the newt stack managed by Komodo (replaces the manual `docker compose` workflow)

### Risk

| # | Risk | Mitigation |
|:--|:--|:--|
| 1 | `v6-drift-remediation-v1` hasn't archived yet | Soft Blocked-by in proposal; tasks.md starts after it archives |
| 2 | The 113 auto-generated `*-bunchloch.toml` stacks have hard-coded paths that may conflict with the new stack | `bun run validate-stacks` after each phase; the generator script is regenerate-able |
| 3 | Upstream openclaw + openchamber GHCR images are private (401) | Code-owned builds (Part 3) — verified openchamber already works |
| 4 | The 4 cross-cutting procedures don't exist — would break the `cross-cutting` resource-sync | Part 5 creates them so the sync is consistent |
| 5 | bunchloch periphery not currently registered with komodo-core | Part 4 (newt + komodo-periphery) brings it up |
| 6 | openchamber-arm1-oci stack TOML needs to point at the locally-built image (not the private upstream) | Part 3 includes the image-reference update + a hard-fail in `validate-stacks` if the tag is the private upstream |
| 7 | OpenChamber upstream Dockerfile is `oven/bun:1.3.14` but the openchamber-web package's lockfile pins `1.3.5` | Use Bun 1.3.14 in our Dockerfile (matches upstream); test the build before deploying |

## Non-Goals

- **Not bringing the full 8-stack agent-platform cluster to arm1-oci** — only the 3 user-facing surfaces. The 5 observability/memory stacks (lakehouse + litellm + mlflow + cognee + graphiti) stay on `bunchloch`.
- **Not building a ccc server on arm1-oci** — the v1 index is bunchloch-only; agents on arm1-oci query the same index via the `ccc` MCP server.
- **Not creating a Pangolin mesh on bunchloch** — bunchloch uses Tailscale Funnel for inbound; only arm1-oci has the Pangolin mesh.
- **Not migrating the openchamber image to docker.io** — the image stays on `ghcr.io/cianfhoghlaim/*` (code-owned GHCR org).
- **Not adding a renovate cycle** for the new images — Renovate is already wired (per the `agent-platform-cluster` spec); this change just gives it 3 more registries to monitor.

## Dependencies

- `Blocked by (soft): 2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1` — this change EXTENDS that change's `preflight:arm-oci` + `iac:bootstrap` work. The v6-drift change should archive first.
- `Blocked by (soft): 2026-07-09-infrastructure-gold-standard-compliance-v1` — provides the `stacks/newt/` 6-file GOLD_STANDARD contract.
- `Affected repos: cianfhoghlaim, bonneagar` (see `cross-repo-sync.md`)

## Validation

1. `openspec validate 2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow --strict` returns 0
2. `bun run preflight:arm-oci --strict --emit-md` returns ALL CHECKS PASSED on arm1-oci
3. `mise run lint:skills` (53/53, no regression)
4. `bun run validate-stacks` (0 hard failures after the build images are tagged)
5. `km run procedure deploy-newt-bunchloch` completes; `docker exec bunchloch-newt -- newt --version` returns 1.14.0; `ifconfig` shows a `utun3` (or similar) with a 100.64.x.x address
6. `km run procedure deploy-agent-platform-cluster-arm1-oci` completes within 15 min
7. All 3 health endpoints return 200: `https://hermes.cianfhoghlaim.ie/api/health`, `https://openclaw.cianfhoghlaim.ie/api/health`, `https://openchamber.cianfhoghlaim.ie/api/health`
8. From this Mac (with newt tunnel up), `curl https://hermes.cianfhoghlaim.ie/api/health` returns 200 (proves remote dev workflow works)
9. `git -C bonneagar status` clean; `git -C cianfhoghlaim status` clean
10. `openspec archive 2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow --yes` succeeds
