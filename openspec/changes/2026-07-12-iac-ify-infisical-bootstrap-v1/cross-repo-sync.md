# Cross-Repo Sync: 2026-07-12-iac-ify-infisical-bootstrap-v1

This change touches **2 repos**: `cianfhoghlaim` (openspec) and `bonneagar` (IaC code). They MUST be committed in this order:

## Order of Operations

```
[1] cianfhoghlaim  → openspec/CHANGES/2026-07-12-iac-ify-infisical-bootstrap-v1/
                     (proposal + tasks + 2 spec deltas + this file)
                          ↓
[2] bonneagar      → iac/ + komodo/ + stacks/ + package.json (the IaC implementation)
                          ↓
                   (push to pick-5b-bonneagar-v5-continuation, update PR #7)
                          ↓
[3] operator       → cd bonneagar && bun run iac:bootstrap-infisical
                          ↓
                   (Chrome MCP drives the /signup/setup wizard for first admin)
                          ↓
[4] cianfhoghlaim  → openspec archive 2026-07-12-iac-ify-infisical-bootstrap-v1 --yes
                     (after iac:health shows ✓ infisical)
```

## Repo 1: cianfhoghlaim

**Files to commit** (under `openspec/changes/2026-07-12-iac-ify-infisical-bootstrap-v1/`):

- `proposal.md` (with `## Dependencies` + `## Cross-repo sync` sections)
- `tasks.md`
- `specs/agent-platform-cluster/spec.md` (delta)
- `specs/infrastructure-stacks/spec.md` (delta)
- `cross-repo-sync.md` (this file)

**Branch**: `main` (openspec changes archive via `openspec archive`, not via PR)

**Push target**: `https://github.com/cianfhoghlaim/cianfhoghlaim.git`

**Commit message**: `feat(openspec): iac-ify the Infisical stack + bootstrap command`

## Repo 2: bonneagar

**Files to commit** (under `bonneagar/`):

| File | Action | Description |
|:--|:--|:--|
| `iac/clients/infisical-rest.ts` | new | 4 direct-REST helpers (login, listProjects, listMachineIdentities, createMachineIdentity) |
| `iac/clients/infisical-client.ts` | rewrite | Use `infisical-rest.ts` helpers; drop `@infisical/sdk` dependency |
| `iac/commands/bootstrap-infisical.ts` | new | Mirror of `bootstrap-pocketid-admin.ts` for Infisical first-admin + machine identity seeding |
| `iac/commands/rotate-auth.ts` | refactor | Replace inline `fetchInfisicalSecret` with a call to the new client |
| `iac/commands/health.ts` | fix | Query Infisical via API not local SQLite |
| `iac/cli.ts` | add command | Register `iac:bootstrap-infisical` |
| `package.json` | drop dep | Remove `@infisical/sdk` if no other consumer (verify first) |
| `komodo/procedures/deploy-infisical-arm1-oci.toml` | new | 6-stage deploy + sub-bootstrap |
| `komodo/procedures/infisical-first.toml` | rewrite | Remove the `ssh arm1-oci` operator step; HTTP-only checks |
| `komodo/resource-syncs/cross-cutting.toml` | update | Add `deploy-infisical-arm1-oci` to the deploy order; fix the "4 procedures" comment |
| `stacks/komodo/secrets.env` | update | `KOMODO_PASSWORD=infisical://dev-baile/komodo/password` |
| `stacks/pangolin/secrets.env` | update | Add `PANGOLIN_API_KEY=infisical://dev-baile/pangolin/api_key` |

**Branch**: `pick-5b-bonneagar-v5-continuation` (existing)

**Push target**: `https://github.com/cianfhoghlaim/bonneagar.git`

**PR**: updates the existing PR #7 (the pick-5b-pr from prior commits)

**Commit message**: `feat(iac): replace buggy @infisical/sdk + add iac:bootstrap-infisical + deploy-infisical-arm1-oci`

## Why This Order

1. **cianfhoghlaim first** — the spec change MUST exist before the IaC code that implements it. The bons IaC's CLAUDE.md says "Per the bonneagar-v5 drift refactor: ... IaC tests in bonneagar are a prerequisite for the cianfhoghlaim openspec archive." So the bons IaC code (step 2) is what makes the openspec archive (step 4) possible.

2. **bonneagar second** — the IaC code implements the spec. It can be merged independently of the openspec change. The IaC's own CI validates that the code compiles.

3. **Operator deployment third** — `bun run iac:bootstrap-infisical` is the one-shot that creates the first admin via Chrome MCP. No operator click-throughs required (the agent drives the browser).

4. **cianfhoghlaim archive last** — only after the operator has verified the deploy worked (`bun run iac:health` shows ✓ infisical).

## What Cannot Be Done Without Both

The bons IaC code (Repo 2) cannot compile without the openspec spec (Repo 1) describing what the behavior SHOULD be. The openspec spec cannot archive without the bons IaC code (Repo 2) being deployed and verified.

If you try to merge Repo 2 before Repo 1, the spec delta will be missing — the IaC code will be implementing undocumented behavior. Bad.
If you try to archive Repo 1 before Repo 2 deploys, the spec will claim a behavior that doesn't exist yet. Bad.

## Rollback Plan

If the bons IaC change breaks something:
- `git revert` the bons IaC commit
- The openspec change is still in `openspec/changes/` (not yet archived) — no rollback needed
- The arm1-oci Infisical can be left running (it's idempotent — re-deploy just hits the existing instance)
- The bunchloch local Infisical (which we're going to tear down) is still there as a fallback

If the openspec change archives prematurely:
- `openspec unarchive 2026-07-12-iac-ify-infisical-bootstrap-v1` brings it back to `openspec/changes/`
- The spec text is still valid — it's just moved to `archive/`

## Branch Names

- cianfhoghlaim: `main` (openspec archive uses the default branch)
- bonneagar: `pick-5b-bonneagar-v5-continuation` (existing)

## Verification Commands

After both repos merge:

```bash
# On bons IaC
cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar
bun run iac:health
# Expected: ✓ infisical (HTTP 200 from https://infisical.cianfhoghlaim.ie/api/status)

bun run iac:rotate-auth
# Expected: All 3 surfaces (pangolin, komodo, infisical) succeed

# On openspec
cd /Users/cianmacandeisigh/dev/kings_college_galway/openspec
openspec validate 2026-07-12-iac-ify-infisical-bootstrap-v1 --strict
# Expected: Validation passes

openspec archive 2026-07-12-iac-ify-infisical-bootstrap-v1 --yes
# Expected: Change moves to openspec/changes/archive/
```
