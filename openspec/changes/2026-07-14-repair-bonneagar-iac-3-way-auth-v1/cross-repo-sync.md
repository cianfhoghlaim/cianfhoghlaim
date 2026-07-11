# Cross-repo Sync Plan: 2026-07-14-repair-bonneagar-iac-3-way-auth-v1

## Commit 1 — bonneagar repo

- **Branch:** `pick-5b-bonneagar-v5-continuation`
- **Files (4 NEW + 2 EDIT):**
  - `iac/auth-pocketid.ts` (NEW, ~120 LOC)
  - `iac/commands/rotate-auth.ts` (NEW, ~80 LOC)
  - `iac/auth.ts` (EDIT — replace the Pocket ID OIDC TODO with `await pocketIdLogin()`)
  - `iac/cli.ts` (EDIT — add `rotate-auth` case to dispatcher)
  - `package.json` (EDIT — add `iac:rotate-auth` script)

```
git -C kings_college_galway/bonneagar add iac/auth-pocketid.ts iac/commands/rotate-auth.ts iac/auth.ts iac/cli.ts package.json
git -C kings_college_galway/bonneagar commit -m "feat(iac): rotate-auth — Pocket ID OIDC client_credentials + 3-way auth repair"
git -C kings_college_galway/bonneagar push origin pick-5b-bonneagar-v5-continuation
```

## Commit 2 — cianfhoghlaim repo

- **Branch:** `pick-4-biep-v1`
- **Files (4):**
  - `openspec/changes/2026-07-14-repair-bonneagar-iac-3-way-auth-v1/proposal.md` (NEW)
  - `openspec/changes/2026-07-14-repair-bonneagar-iac-3-way-auth-v1/tasks.md` (NEW)
  - `openspec/changes/2026-07-14-repair-bonneagar-iac-3-way-auth-v1/cross-repo-sync.md` (NEW, this file)
  - `openspec/changes/2026-07-14-repair-bonneagar-iac-3-way-auth-v1/specs/agent-platform-cluster/spec.md` (NEW, 1 ADDED Requirement)

```
git add openspec/changes/2026-07-14-repair-bonneagar-iac-3-way-auth-v1/
git commit -m "feat(openspec): repair bonneagar iac 3-way auth v1 (Pocket ID OIDC + rotate-auth)"
git push origin pick-4-biep-v1
```

## Post-push: archive

```
openspec archive 2026-07-14-repair-bonneagar-iac-3-way-auth-v1 --yes
```
