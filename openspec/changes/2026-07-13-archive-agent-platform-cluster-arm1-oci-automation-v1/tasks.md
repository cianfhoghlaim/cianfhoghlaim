# Tasks: 2026-07-13-archive-agent-platform-cluster-arm1-oci-automation-v1

## Phase 0 — Read baseline + verify dependencies

- [x] Confirm Improvement 3 (preflight hard-gate) is committed
- [x] Confirm Improvement 4 (bootstrap procedure) is committed
- [x] Verify `openspec archive --help` exits 0 and idempotent semantics

## Phase 1 — Author the procedure

- [x] Write `komodo/procedures/archive-agent-platform-cluster-arm1-oci.toml` with 3 stages:
  1. health-checks (3 curl probes, require_success=true)
  2. archive-changes (5 idempotent `openspec archive --yes || true` shell commands)
  3. emit-success-artifact (JSON output to /tmp/agent-platform-cluster/)

## Phase 2 — Create the openspec change

- [x] Write `proposal.md`
- [x] Write `cross-repo-sync.md`
- [x] Write `tasks.md` (this file)
- [x] Write `specs/agent-platform-cluster/spec.md` with 1 ADDED Requirement:
  - `### Requirement: Auto-archive procedure gates on 3 health endpoints returning 200`
  - 3 Scenarios: all 3 endpoints return 200, any returns non-200, already-archived idempotent

## Phase 3 — Validate

- [ ] `openspec validate 2026-07-13-archive-agent-platform-cluster-arm1-oci-automation-v1 --strict` returns 0

## Phase 4 — Commit + push

- [ ] Commit on `pick-5b-bonneagar-v5-continuation`
- [ ] Push bonneagar branch
- [ ] Commit on `pick-4-biep-v1`
- [ ] Push cianfhoghlaim branch

## Phase 5 — Archive

- [ ] `openspec archive 2026-07-13-archive-agent-platform-cluster-arm1-oci-automation-v1 --yes`
- [ ] Update `<root>/.audit.local.md` §6 — Improvement 5 → DONE