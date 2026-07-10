# Change: 2026-07-13-archive-agent-platform-cluster-arm1-oci-automation-v1

## Why

Today, after the arm1-oci agent platform comes up, the operator has to
manually run 5 `openspec archive` commands to close out the 5 changes
that shipped the deployment:

1. `2026-07-13-backfill-server-id-on-12-procedures`
2. `2026-07-13-arm-oci-deploy-preflight-hard-gate-v1`
3. `2026-07-13-agent-platform-cluster-arm1-oci-bootstrap-procedure-v1`
4. `2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow` (the parent change)

This is fragile: the operator can forget one, run them out of order, or
archive before the cluster is actually live. We want a one-command,
idempotent, audit-friendly close-out: **one** `km run procedure`
invocation that verifies the cluster is live (3 health probes) and
archives all 5 changes atomically.

## What Changes

### 1. Add `bonneagar/komodo/procedures/archive-agent-platform-cluster-arm1-oci.toml`

A new Komodo procedure with 3 stages:

1. **health-checks** — 3 curl probes (hermes, openclaw, openchamber),
   each with `require_success = true`. If ANY returns non-200, the
   procedure aborts at Stage 1.
2. **archive-changes** — 5 idempotent `RunShellCommand`s that run
   `openspec archive <change-id> --yes` for each of the 5 changes.
   Each uses `|| true` so already-archived is treated as success.
3. **emit-success-artifact** — Writes
   `/tmp/agent-platform-cluster/archived-on-<utc-ts>.json` capturing
   the timestamp + the 5 archived change IDs.

### 2. ADD 1 Requirement to `agent-platform-cluster` spec

Documents the health-gated auto-archive contract.

## Affected specs

| Spec | Why |
|:--|:--|
| `agent-platform-cluster` | Adds 1 ADDED Requirement: "Auto-archive procedure gates on 3 health endpoints returning 200" |

## Acceptance gates

- [ ] `openspec validate 2026-07-13-archive-agent-platform-cluster-arm1-oci-automation-v1 --strict` passes
- [ ] `git -C bonneagar push` succeeds
- [ ] `git push origin pick-4-biep-v1` succeeds
- [ ] Re-running the procedure on an already-archived set exits 0 (idempotent)

## Dependencies

`Blocked by: 2026-07-13-agent-platform-cluster-arm1-oci-bootstrap-procedure-v1` (the bootstrap is what gets the cluster up so this archive can run)

`Blocked by (soft): 2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow` (the parent change)

`Affected repos: bonneagar, cianfhoghlaim`

## Cross-repo sync

See `cross-repo-sync.md` — **bonneagar first**, then **cianfhoghlaim**.

## Out of scope

- Rolling back an archive (irreversible; the archived change is preserved).
- Auto-archiving changes beyond the 5 agent-platform-cluster set.