# Change: 2026-07-14-deploy-pangolin-newt-arm1-oci-v1

## Why

The arm1-oci control plane currently runs `pangolin` (the EE reverse proxy) + `gerbil` (the WireGuard server) + `postgres`, but has **no newt client on the server side**. The primary newt client runs on `bunchloch` (this Mac, the operator-laptop side).

This means: services hosted on arm1-oci (hermes, openclaw, openchamber, langfuse) cannot reach the Pangolin mesh without first establishing a WireGuard tunnel back to bunchloch. That creates a circular dependency — the agent platform is supposed to live on arm1-oci, but the mesh that connects everything only goes through the bunchloch tunnel.

A **secondary newt client on arm1-oci** breaks the cycle: arm1-oci can route its own services through the local gerbil without going back to bunchloch first.

The newt compose template already exists at `stacks/pangolin/newt.yaml` (pinned to v1.14.0 per `2026-07-14-bump-newt-v1.14.0-cross-cluster-v1`), but no Komodo procedure deploys it.

## What Changes

### 1. New file: `komodo/procedures/deploy-pangolin-newt-arm1-oci.toml` (~130 LOC)

5 stages (mirrors `deploy-newt-bunchloch-v2` for the arm1-oci side):
1. **preflight** — Pangolin + Infisical health probes
2. **iac-provision** — `bun run iac:sync:sites` (auto-provisions the arm1-oci newt site)
3. **stackup** — extend the pangolin compose with the newt service
4. **wireguard-tunnel** — wait + `wg show`
5. **health-checks** — pangolin-newt Up, locket secrets resolved, newt version = 1.14.0, WireGuard handshake, pangolin-core reachable

### 2. Update `komodo/procedures/server_id_legend.md`

Add the new procedure to the arm1-oci section.

## Affected specs

| Spec | Why |
|:--|:--|
| `agent-platform-cluster` | Adds 1 ADDED Requirement: "deploy-pangolin-newt-arm1-oci brings the arm1-oci-side newt client online" |

## Acceptance gates

- [ ] `openspec validate 2026-07-14-deploy-pangolin-newt-arm1-oci-v1 --strict` returns 0
- [ ] After deploy: `docker exec pangolin-newt -- newt --version` returns `1.14.0`
- [ ] After deploy: `curl https://hermes.cianfhoghlaim.ie/api/health` returns 200

## Dependencies

`Blocked by: 2026-07-14-bump-newt-v1.14.0-cross-cluster-v1` (the v1.14.0 pin)

`Blocked by: 2026-07-14-iac-sync-sites-pangolin-integrations-api-v1` (the iac:sync:sites command)

`Blocked by (soft): 2026-07-14-repair-bonneagar-iac-3-way-auth-v1`

`Affected repos: bonneagar, cianfhoghlaim`

## Cross-repo sync

See `cross-repo-sync.md` — **bonneagar first** (the procedure), then **cianfhoghlaim** (the openspec change).
