# Tasks: 2026-07-14-repair-bonneagar-iac-3-way-auth-v1

## Phase 0 — Read baseline

- [x] Read `iac/auth.ts` to confirm the TODO at line 36
- [x] Read `iac/config.ts` to see what env vars are expected
- [x] Read `iac/clients/pangolin-client.ts` to see the API call pattern
- [x] Read `PANGOLIN-SETUP.md` in bonneagar to understand the manual setup procedure

## Phase 1 — Bonneagar code changes (DEFERRED — requires design review)

> **Implementation deferred to a follow-up session.** This change creates the openspec contract
> (proposal + tasks + spec delta) so the work is visible + tracked, but the actual
> implementation of `auth-pocketid.ts` + `rotate-auth.ts` requires:
> 1. Discovery of the Pocket ID `client_id` + `client_secret` (these need to be created
>    manually via Pocket ID web UI first)
> 2. The discovery URL of the Pocket ID `.well-known/openid-configuration` endpoint
> 3. The Pangolin form-login URL + CSRF flow (the form-login exchange is non-trivial)
>
> A future session with a working Pocket ID OIDC client + the Pangolin login form
> can implement this change in ~4 hours.

- [ ] Create `iac/auth-pocketid.ts` (DEFERRED)
- [ ] Create `iac/commands/rotate-auth.ts` (DEFERRED)
- [ ] Edit `iac/auth.ts` to call `pocketIdLogin()` (DEFERRED)
- [ ] Edit `iac/cli.ts` to add `rotate-auth` case (DEFERRED)
- [ ] Edit `package.json` to add `iac:rotate-auth` script (DEFERRED)

## Phase 2 — Openspec change (DONE this session)

- [x] Write `proposal.md`
- [x] Write `cross-repo-sync.md`
- [x] Write `tasks.md` (this file)
- [x] Write `specs/agent-platform-cluster/spec.md` with 1 ADDED Requirement:
  - `### Requirement: iac:rotate-auth mints fresh Pangolin + Komodo + Infisical credentials via Pocket ID OIDC`
  - 3 Scenarios: rotation succeeds, rotation fails, rotated credentials used by iac:sync:sites

## Phase 3 — Validate + commit + push (after Phase 1 implementation lands)

- [ ] `openspec validate 2026-07-14-repair-bonneagar-iac-3-way-auth-v1 --strict` returns 0
- [ ] `bun run iac:rotate-auth` succeeds (after the implementation lands)
- [ ] `bun run iac:health` exits 0 (proves the rotation worked)
- [ ] Commit on `pick-5b-bonneagar-v5-continuation`
- [ ] Push bonneagar branch
- [ ] Commit on `pick-4-biep-v1`
- [ ] Push cianfhoghlaim branch

## Phase 4 — Archive

- [ ] `openspec archive 2026-07-14-repair-bonneagar-iac-3-way-auth-v1 --yes`

## Phase 5 — Smoke-test (after auth works)

- [ ] `bun run iac:health` returns: 4 surfaces healthy
- [ ] `bun run iac:plan` discovers 18 services + 1 newt site
- [ ] `bun run iac:sync:sites` provisions the bunchloch-newt site
- [ ] `km run procedure deploy-newt-bunchloch-v2` succeeds end-to-end
- [ ] `km run procedure deploy-pangolin-newt-arm1-oci` succeeds end-to-end
- [ ] `curl https://hermes.cianfhoghlaim.ie/api/health` returns 200
