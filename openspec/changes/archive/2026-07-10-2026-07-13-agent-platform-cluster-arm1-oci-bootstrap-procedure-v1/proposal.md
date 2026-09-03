# Change: 2026-07-13-agent-platform-cluster-arm1-oci-bootstrap-procedure-v1

## Why

Today, bringing up the arm1-oci agent-platform cluster (hermes + openclaw
+ openchamber + langfuse + observability + pangolin) requires **5+
separate `km run procedure` invocations**:

1. `km run procedure deploy-langfuse-arm1-oci`
2. `km run procedure deploy-observability-arm1-oci`
3. `km run procedure deploy-openclaw-arm1-oci`
4. `km run procedure deploy-openchamber-arm1-oci`
5. `km run procedure deploy-hermes-arm1-oci`
6. `km run procedure deploy-agent-platform-cluster-arm1-oci` (the omnibus)
7. (manual) `iac:bootstrap` step
8. (manual) 3 image builds
9. (manual) 3 curl health checks
10. (manual) JSON artifact emit

This is fragile — operators forget steps, run them out of order, or skip
the preflight check. We want **one** `km run procedure` invocation that
brings up the cluster end-to-end with a deterministic, retryable,
audit-friendly flow.

## What Changes

### 1. Add `bonneagar/komodo/procedures/agent-platform-cluster-arm1-oci-bootstrap.toml`

A new Komodo procedure with 7 stages:

1. **pre-reqs** — Check 9 env vars + resource ceiling (CPU 85% / MEM 90%)
2. **parallel-image-builds** — 3 Komodo `RunBuild` calls in parallel:
   - `openchamber-arm1-oci` → `ghcr.io/cianfhoghlaim/openchamber:1.14.1-arm1`
   - `openclaw-arm1-oci`    → `ghcr.io/cianfhoghlaim/openclaw:2026.6-arm1`
   - `hermes-arm1-oci`      → no-op (uses public `nousresearch/hermes-agent:v2026.7.1`)
3. **iac-bootstrap** — Run `pnpm tsx bonneagar/iac/commands/bootstrap.ts arm1-oci`
4. **omnibus-deploy** — Run `deploy-agent-platform-cluster-arm1-oci` (preflight-gated by Improvement 3)
5. **health-checks** — 3 `curl` probes (hermes, openclaw, openchamber)
6. **emit-artifact** — Write `/tmp/agent-platform-cluster/arm-oci-<ts>.json` with the resolved cluster fingerprint
7. **validate** — `bun run validate-stacks`

### 2. ADD 1 Requirement to `agent-platform-cluster` spec

Documents the 7-stage composition contract.

## Affected specs

| Spec | Why |
|:--|:--|
| `agent-platform-cluster` | Adds 1 ADDED Requirement: "Bootstrap procedure composes 7 stages into one km invocation" |

## Acceptance gates

- [ ] `openspec validate 2026-07-13-agent-platform-cluster-arm1-oci-bootstrap-procedure-v1 --strict` passes
- [ ] `git -C bonneagar push` succeeds
- [ ] `git push origin pick-4-biep-v1` succeeds
- [ ] `komodo get-procedure agent-platform-cluster-arm1-oci-bootstrap` returns the 7 stages

## Dependencies

`Blocked by: 2026-07-13-arm-oci-deploy-preflight-hard-gate-v1` (Stage 4 inherits the preflight gate)

`Blocked by (soft): 2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow` (the parent change; this is its one-shot bootstrap)

`Affected repos: bonneagar, cianfhoghlaim`

## Cross-repo sync

See `cross-repo-sync.md` — **bonneagar first**, then **cianfhoghlaim**.

## Out of scope

- Migrating the bunchloch equivalent `deploy-bunchloch-stack-bootstrap`
  to the same 7-stage shape. (Possible follow-up change.)
- Rolling back on partial failure. (Each stage is idempotent; rollback
  is the operator's responsibility via `km run procedure` on the sub-
  procedures.)