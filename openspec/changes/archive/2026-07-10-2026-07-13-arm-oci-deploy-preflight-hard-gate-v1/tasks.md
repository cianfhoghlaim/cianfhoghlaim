# Tasks: 2026-07-13-arm-oci-deploy-preflight-hard-gate-v1

## Phase 0 — Read baseline + verify dependencies

- [x] Read `bonneagar/komodo/procedures/deploy-agent-platform-cluster-arm1-oci.toml` (Stage 0 preflight).
- [x] Confirm `scripts/preflight-arm-oci.ts` exists and is wired into `package.json` as `preflight:arm-oci` + `--strict` + `--emit-md`.
- [x] Confirm `2026-07-13-v6-drift-remediation-final-v1` is archived (the hard dep).

## Phase 1 — Edit the bonneagar procedure

- [x] Edit Stage 0 `preflight` RunShellCommand in `deploy-agent-platform-cluster-arm1-oci.toml`:
  - [x] Wrap the command so the `--emit-md` report is captured to `/tmp/preflight-reports/arm-oci/<utc-ts>.md`
  - [x] Add `require_success = true` to the execution params
  - [x] Annotate the comment block to call out the hard-gate
- [x] Verify the TOML is valid (Komodo's TOML parser is strict about table arrays).

## Phase 2 — Create the openspec change

- [x] Write `proposal.md` (Why, What Changes, Affected specs, Acceptance gates, Dependencies, Cross-repo sync, Out of scope).
- [x] Write `cross-repo-sync.md` (bonneagar first, then cianfhoghlaim).
- [x] Write `tasks.md` (this file).
- [x] Write `specs/infrastructure-stacks/spec.md` with 1 ADDED Requirement:
  - `### Requirement: preflight:arm-oci hard-gates arm1-oci cluster deployment`
  - 3 Scenarios: preflight exits 0, preflight exits non-zero, `--skip=preflight` rejected

## Phase 3 — Validate

- [ ] `openspec validate 2026-07-13-arm-oci-deploy-preflight-hard-gate-v1 --strict` returns 0

## Phase 4 — Commit + push (bonneagar first, then cianfhoghlaim)

- [ ] Commit on `pick-5b-bonneagar-v5-continuation`: "fix(komodo): hard-gate preflight:arm-oci with require_success=true + versioned report path"
- [ ] Push bonneagar branch
- [ ] Commit on `pick-4-biep-v1`: "feat(openspec): arm-oci deploy preflight hard-gate v1 (Improvement 3)"
- [ ] Push cianfhoghlaim branch

## Phase 5 — Archive

- [ ] `openspec archive 2026-07-13-arm-oci-deploy-preflight-hard-gate-v1 --yes`
- [ ] Verify `openspec list` no longer shows it
- [ ] Update `<root>/.audit.local.md` §6 — Improvement 3 → DONE