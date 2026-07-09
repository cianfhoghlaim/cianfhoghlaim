# Cross-repo sync plan: 2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1

This change touches **2 of the 3 repos**: cianfhoghlaim + bonneagar.
The leabharlann repo is unaffected.

## Repo 1: `cianfhoghlaim` (this repo)

**Branch**: `pick-4-biep-v1`
**Remote**: `origin` → `https://github.com/cianfhoghlaim/cianfhoghlaim.git`

### Files created (5)

1. `openspec/changes/2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1/{proposal,tasks,cross-repo-sync}.md`
2. `openspec/changes/2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1/specs/{infrastructure-stacks,bonneagar-iac-merge,bonneagar-komodo-gitops,infrastructure-stacks-documentation,indexing-and-cognition}/spec.md`
3. `scripts/preflight-arm-oci.ts`
4. `docs/agents/preflight-report-<timestamp>.md` (only after running with `--emit-md`)

### Files edited (8)

1. `AGENTS.md` — 3 stack-count edits + 2 `sruth/oideachais/...` path fixes + 1 line-280 removal + 3 new sections
2. `openspec/AGENTS.md` — 2 new sections
3. `package.json` — 3 new scripts (`preflight:arm-oci`, `iac:bootstrap`, `iac:plan`, `iac:health`)
4. `mise.toml` — 4 new task aliases
5. `docs/stacks/README.md` — 1 stack-count edit
6. `openspec/specs/dlthub-platform-integration/spec.md` — 1 stack-count edit
7. `openspec/specs/documentation/spec.md` — 1 stack-count edit
8. `openspec/specs/agent-platform-cluster/spec.md` — 1 stack-count edit

### Commit shape

```
fix(drift): v6 drift remediation + repo boundary lockdown + preflight:arm-oci safety script

- New openspec change: 2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1
- Root AGENTS.md: fix 3 stack-count drifts + 2 sruth/... paths + add Repo Boundary / OpenSpec / Safety sections
- AGENTS.md: remove 1Password+SOPS reference (superseded by Infisical)
- openspec/AGENTS.md: add Cross-repo sync + Dependencies conventions
- New: scripts/preflight-arm-oci.ts (Pangolin + Komodo + Infisical health + process namespace isolation)
- New: package.json scripts (preflight:arm-oci, iac:bootstrap, iac:plan, iac:health)
- New: mise.toml task aliases
- 4 spec files: stack-count drift fixes
```

### Push target

`git push origin pick-4-biep-v1`

## Repo 2: `bonneagar` (separate worktree at `./bonneagar/`)

**Branch**: `pick-5b-bonneagar-v5-continuation`
**Remote**: `bonneagar` → `https://github.com/cianfhoghlaim/bonneagar.git`

### Files deleted (5 placeholder dirs)

1. `bonneagar/stacks/backend/`
2. `bonneagar/stacks/platform-service/`
3. `bonneagar/stacks/runner/`
4. `bonneagar/stacks/workers/`
5. `bonneagar/stacks/x2text-service/`

### Files edited (10)

1. `bonneagar/AGENTS.md` — 8 stack-count edits + 1 new `## IaC Repo Boundary` section
2. `bonneagar/GOLD_STANDARD.md` — 3 stack-count edits
3. `bonneagar/package.json` — 1 "88-stack" → "87-stack" edit
4. `bonneagar/stacks/README.md` — 1 stack-count edit
5. `bonneagar/deploy-runbooks/bunchloch-bootstrap.md` — 1 stack-count edit
6. `openspec/specs/bonneagar-iac-merge/spec.md` — (mirror from cianfhoghlaim-side delta)
7. `openspec/specs/bonneagar-komodo-gitops/spec.md` — (mirror from cianfhoghlaim-side delta)
8. `openspec/specs/infrastructure-stacks-documentation/spec.md` — (mirror from cianfhoghlaim-side delta)
9. `openspec/specs/infrastructure-stacks/spec.md` — (mirror from cianfhoghlaim-side delta)
10. `docs/stacks/README.md` — (mirror from cianfhoghlaim-side `docs/stacks/README.md` edit)

> **Note**: The openspec/specs/* files are SHARED between the 2
> repos via the worktree — only the cianfhoghlaim-side openspec
> has the canonical delta files; the bonneagar-side copies are
> just the spec index files and will be updated to point at the
> cianfhoghlaim-side canonical after this change archives.

### Commit shape

```
fix(gold-standard): apply the 5-deletion + count-reference cleanup the v1 openspec change claimed to do

- Delete 5 placeholder stacks/backend,platform-service,runner,workers,x2text-service
- AGENTS.md: 8 stack-count edits + add ## IaC Repo Boundary section
- GOLD_STANDARD.md: 3 stack-count edits
- package.json: 88-stack -> 87-stack
- stacks/README.md: 93/94 -> 87
- deploy-runbooks/bunchloch-bootstrap.md: 86-stack -> 87-stack
- 3 spec files: stack-count drift fixes
- Push to bonneagar/pick-5b-bonneagar-v5-continuation
```

### Push target

`git -C bonneagar push bonneagar pick-5b-bonneagar-v5-continuation`

## Repo 3: `leabharlann` (separate worktree at `./leabharlann/`)

**No changes**. This drift remediation does not touch the
leabharlann repo.

## Order of operations

The 2 repos MUST be committed in this order:

1. **bonneagar first** — the 5-deletion + count updates are
   prerequisites for the IaC tests; if committed after
   cianfhoghlaim, the cross-repo `openspec validate` will fail
2. **cianfhoghlaim second** — the openspec change references
   the new bonneagar state

## Acceptance gates (both repos)

- `openspec validate 2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1 --strict` passes (cianfhoghlaim)
- `bun run validate-stacks` passes (bonneagar)
- `ls -d bonneagar/stacks/*/ | wc -l` returns `87` (bonneagar)
- `bun run preflight:arm-oci` exits 0 (cianfhoghlaim)
- `bun run iac:bootstrap --dry-run` exits 0 (cianfhoghlaim)
- `git status` clean in both worktrees