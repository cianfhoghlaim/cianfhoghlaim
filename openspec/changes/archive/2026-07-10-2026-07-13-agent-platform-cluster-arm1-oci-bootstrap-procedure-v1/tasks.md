# Tasks: 2026-07-13-agent-platform-cluster-arm1-oci-bootstrap-procedure-v1

## Phase 0 — Read baseline + verify dependencies

- [x] Read `deploy-bunchloch-stack-bootstrap.toml` as the bunchloch equivalent template
- [x] Verify `iac/commands/bootstrap.ts` exists and accepts `arm1-oci` as an arg
- [x] Verify the 3 Komodo Build resources exist (`openchamber-arm1-oci`, `openclaw-arm1-oci`, `hermes-arm1-oci`)
- [x] Confirm Improvement 3 (preflight hard-gate) is committed (gives Stage 4 its hard-gate)

## Phase 1 — Author the procedure

- [x] Write `komodo/procedures/agent-platform-cluster-arm1-oci-bootstrap.toml` with 7 stages:
  1. pre-reqs (9 env vars + resource ceiling)
  2. parallel-image-builds (3 RunBuild in parallel)
  3. iac-bootstrap (RunShellCommand: pnpm tsx .../bootstrap.ts arm1-oci)
  4. omnibus-deploy (RunProcedure: deploy-agent-platform-cluster-arm1-oci)
  5. health-checks (3 RunShellCommand curl probes, all require_success=true)
  6. emit-artifact (RunShellCommand: write JSON to /tmp/agent-platform-cluster/)
  7. validate (RunShellCommand: bun run validate-stacks)

## Phase 2 — Create the openspec change

- [x] Write `proposal.md`
- [x] Write `cross-repo-sync.md`
- [x] Write `tasks.md` (this file)
- [x] Write `specs/agent-platform-cluster/spec.md` with 1 ADDED Requirement:
  - `### Requirement: Bootstrap procedure composes 7 stages into one km invocation`
  - 3 Scenarios: all 3 builds succeed in parallel, 1 build fails, omnibus preflight fails

## Phase 3 — Validate

- [ ] `openspec validate 2026-07-13-agent-platform-cluster-arm1-oci-bootstrap-procedure-v1 --strict` returns 0

## Phase 4 — Commit + push

- [ ] Commit on `pick-5b-bonneagar-v5-continuation`
- [ ] Push bonneagar branch
- [ ] Commit on `pick-4-biep-v1`
- [ ] Push cianfhoghlaim branch

## Phase 5 — Archive

- [ ] `openspec archive 2026-07-13-agent-platform-cluster-arm1-oci-bootstrap-procedure-v1 --yes`
- [ ] Update `<root>/.audit.local.md` §6 — Improvement 4 → DONE