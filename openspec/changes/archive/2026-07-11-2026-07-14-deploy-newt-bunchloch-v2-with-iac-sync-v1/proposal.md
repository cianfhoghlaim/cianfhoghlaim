# Change: 2026-07-14-deploy-newt-bunchloch-v2-with-iac-sync-v1

## Why

The existing `deploy-newt-bunchloch` procedure (v1) brings up the 4 bunchloch-site services (locket + newt + komodo-periphery + beszel-agent) on this Mac, but it has 2 gaps:

1. **No integration with the IaC** — the newt `newtId` + `newtSecret` must be pre-minted manually via the Pangolin UI + manually written to Infisical. The v2 procedure integrates with the new `iac:sync:sites` command (delivered by `2026-07-14-iac-sync-sites-pangolin-integrations-api-v1`).
2. **No version assertion** — v1 just runs `docker exec bunchloch-newt -- newt --version` and prints the output. v2 asserts the version equals `1.14.0` (the bump delivered by `2026-07-14-bump-newt-v1.14.0-cross-cluster-v1`).
3. **No WireGuard handshake verification** — v1 just waits for the "tunnel established" log line. v2 also runs `docker exec bunchloch-newt -- wg show` to dump the peer + handshake time.

## What Changes

### 1. New file: `komodo/procedures/deploy-newt-bunchloch-v2.toml` (~150 LOC)

5 stages:
1. **preflight** (5-check): docker present, env vars hydrated, locket healthy
2. **iac-provision**: `bun run iac:sync:sites` (auto-provisions the site + writes credentials)
3. **stackup**: `mkdir -p ~/.local/newt && docker compose up -d` (creates the run-directory on first use)
4. **wireguard-tunnel**: waits up to 60s for "tunnel established" + dumps `wg show`
5. **health-checks** (5-point): all 4 services Up, locket secrets resolved, newt version = 1.14.0, WireGuard handshake present, komodo-core reachable

### 2. Update `komodo/procedures/server_id_legend.md`

Mark `deploy-newt-bunchloch.toml` as LEGACY (v1); add `deploy-newt-bunchloch-v2.toml` as RECOMMENDED.

## Affected specs

| Spec | Why |
|:--|:--|
| `agent-platform-cluster` | Adds 1 ADDED Requirement: "deploy-newt-bunchloch-v2 integrates with iac:sync:sites + asserts newt v1.14.0" |

## Acceptance gates

- [ ] `openspec validate 2026-07-14-deploy-newt-bunchloch-v2-with-iac-sync-v1 --strict` returns 0
- [ ] `km run procedure deploy-newt-bunchloch-v2` succeeds end-to-end (after auth fix)
- [ ] Stage 4 health-checks all 5 pass

## Dependencies

`Blocked by: 2026-07-14-bump-newt-v1.14.0-cross-cluster-v1` (the v1.14.0 pin)

`Blocked by: 2026-07-14-iac-sync-sites-pangolin-integrations-api-v1` (the iac:sync:sites command)

`Blocked by (soft): 2026-07-14-repair-bonneagar-iac-3-way-auth-v1` (needed to test)

`Affected repos: bonneagar, cianfhoghlaim`

## Cross-repo sync

See `cross-repo-sync.md` — **bonneagar first** (the procedure + legend), then **cianfhoghlaim** (the openspec change).
