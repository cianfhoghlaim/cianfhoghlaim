# Change: 2026-07-13-arm-oci-deploy-preflight-hard-gate-v1

## Why

The omnibus procedure `deploy-agent-platform-cluster-arm1-oci` (in
`bonneagar/komodo/procedures/`) currently has a Stage 0 `preflight` step
that runs `bun run preflight:arm-oci --strict --emit-md`, but it lacks
`require_success = true` — so if the preflight script returns non-zero,
the omnibus silently continues to Stage 1 (control-plane foundation) and
beyond. This defeats the safety contract documented in the parent change
`2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow`
proposal § Why: "the preflight a hard dep of every new arm1-oci
procedure".

Additionally, the `--emit-md` flag's report was being emitted to stdout
(or to a temp location decided by the script), making it hard to find
post-mortem after a failed deploy. The fix captures the report to a
versioned, timestamped path under `/tmp/preflight-reports/arm-oci/` so
every deploy attempt leaves an auditable artifact.

## What Changes

### 1. Edit `bonneagar/komodo/procedures/deploy-agent-platform-cluster-arm1-oci.toml`

In Stage 0 `preflight`:
- Wrap the command so the preflight report is written to
  `/tmp/preflight-reports/arm-oci/<utc-timestamp>.md`.
- Add `require_success = true` to the execution params — Komodo will
  abort the omnibus at Stage 0 if preflight exits non-zero.
- Annotate the comment block to call out the hard-gate.

### 2. ADD 1 Requirement to `infrastructure-stacks` spec

A new Requirement documents the hard-gate contract for any arm1-oci
cluster procedure.

## Affected specs

| Spec | Why |
|:--|:--|
| `infrastructure-stacks` | Adds 1 ADDED Requirement: "preflight:arm-oci hard-gates arm1-oci cluster deployment" |

## Acceptance gates

- [ ] `openspec validate 2026-07-13-arm-oci-deploy-preflight-hard-gate-v1 --strict` passes
- [ ] `git -C bonneagar push` succeeds (the procedure file lives there)
- [ ] `git push origin pick-4-biep-v1` succeeds (the openspec change lives here)
- [ ] After archive: `komodo get-procedure deploy-agent-platform-cluster-arm1-oci` shows the `require_success=true` flag in the YAML

## Dependencies

`Blocked by: 2026-07-13-v6-drift-remediation-final-v1` (archived 2026-07-10; provides the `preflight:arm-oci` script)

`Blocked by (soft): none`

`Affected repos: bonneagar, cianfhoghlaim`

## Cross-repo sync

See `cross-repo-sync.md` — the order is **bonneagar first**, then
**cianfhoghlaim**. The bonneagar procedure file is the actual code
change; the cianfhoghlaim openspec change is the documentation/spec
delta.

## Out of scope

- Adding `require_success=true` to the 4 sub-procedures
  (`deploy-hermes-arm1-oci`, `deploy-langfuse-arm1-oci`,
  `deploy-observability-arm1-oci`, `deploy-openchamber-arm1-oci`) — they
  each have their own Stage 0 preflight already and already pass through
  the omnibus; the omnibus's hard-gate covers all of them transitively.
- Modifying `preflight:arm-oci` itself — that's owned by the
  v6-drift-remediation-final-v1 change.