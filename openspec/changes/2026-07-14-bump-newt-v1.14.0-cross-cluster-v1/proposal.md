# Change: 2026-07-14-bump-newt-v1.14.0-cross-cluster-v1

## Why

The fossorial `newt` Pangolin client (the WireGuard tunnel agent that bridges `bunchloch` and `arm1-oci` into the Pangolin mesh) was running **v1.13.0** on the arm1-oci side and **`:latest`** on the bunchloch side. v1.14.0 was released 2026-07-02 with 3 meaningful changes:

1. **Server-side sync message** to detect lost command-control websocket messages
2. **`--native-main` mode** — creates a native WireGuard interface on the host (instead of netstack). On a Mac laptop (bunchloch) this means the tunnel is visible as a real `utun` interface and can be managed by the OS's standard WireGuard tooling.
3. **Upstream remote subnets** with remote WireGuard — useful for routing services hosted on multiple VPCs.

The pinned `:latest` (bunchloch) is a supply-chain risk: any release pushed by fossorial is automatically trusted. The v1.13.0 pin (arm1-oci) is outdated. Both need to be replaced with **v1.14.0 + the SHA256 digest** for supply-chain integrity.

## What Changes

### 1. New file: `bonneagar/stacks/newt/IMAGE`

The canonical source of truth for the newt image version + SHA. Both `stacks/newt/docker-compose.yaml` (bunchloch) and `stacks/pangolin/newt.yaml` (arm1-oci) reference these constants.

### 2. Bump `stacks/newt/docker-compose.yaml`

`image: fosrl/newt:latest` → `image: ghcr.io/fosrl/newt@sha256:60c78391...`

### 3. Bump `stacks/pangolin/newt.yaml`

`image: fosrl/newt:1.13.0` → `image: ghcr.io/fosrl/newt@sha256:60c78391...`

### 4. ADD 1 Requirement to `infrastructure-stacks` spec

Documents the cross-cluster image-pin contract.

## Affected specs

| Spec | Why |
|:--|:--|
| `infrastructure-stacks` | Adds 1 ADDED Requirement: "newt image is pinned to v1.14.0 + SHA digest across all clusters" |

## Acceptance gates

- [ ] `openspec validate 2026-07-14-bump-newt-v1.14.0-cross-cluster-v1 --strict` returns 0
- [ ] `git -C bonneagar push` succeeds
- [ ] `git push origin pick-4-biep-v1` succeeds
- [ ] After deploy: `docker exec bunchloch-newt -- newt --version` outputs `1.14.0`
- [ ] After deploy: `docker exec pangolin-newt -- newt --version` outputs `1.14.0`

## Dependencies

`Blocked by: none`

`Blocked by (soft): 2026-07-14-iac-sync-sites-pangolin-integrations-api-v1` (provides the API client that the deploy procedures depend on)

`Affected repos: bonneagar, cianfhoghlaim`

## Cross-repo sync

See `cross-repo-sync.md` — **bonneagar first** (the image pins), then **cianfhoghlaim** (the openspec change).

## Out of scope

- Bumping `gerbil` to a newer version (the WireGuard server side; not needed for the newt features we want)
- Bumping `pangolin` itself (the EE container; tracked separately in `agent-platform-cluster`)
