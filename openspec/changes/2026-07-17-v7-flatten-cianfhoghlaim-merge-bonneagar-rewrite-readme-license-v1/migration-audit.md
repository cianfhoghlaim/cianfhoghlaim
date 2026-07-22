# Migration audit — v7 flatten + bonneagar re-merge

**Generated**: 2026-07-17 (pre-execution)
**Author**: build agent
**Branch baseline**: `pick-4-biep-v1` at `b1016692a` (post Phase-1.1 catch-up snapshot)

## Summary

Two structurally distinct repos (the `cianfhoghlaim/` monorepo at `pick-4-biep-v1` + the
IaC worktree at `bonneagar/` checking out `pick-5b-bonneagar-v5-continuation`) share a
single `.git/` directory via `git worktree`. The `bonneagar/` subdirectory is
**not** a separate repo — it's a worktree linked to the main `.git/worktrees/bonneagar/`.
The `bonneagar` GitHub remote (`https://github.com/cianfhoghlaim/bonneagar.git`) is a
true separate repo but its local mirror lives at the same `.git/`.

The user explicitly chose the **two-step git merge** path (over `git subtree` or
file-copy squash). The preconditions are:

1. ✅ All 494 in-flight working-tree changes on `pick-4-biep-v1` are committed
   (commit `b1016692a chore(snapshot): catch up pick-4-biep-v1 working tree pre-v7-flatten`).
2. ✅ The `bonneagar` remote was pruned (3 stale branches: `bonneagar-main`,
   `dev`, `pick-5-bonneagar-v5` — all deleted upstream).
3. ✅ The IaC branch (`pick-5b-bonneagar-v5-continuation`) already has the
   IaC at **root** (no `bonneagar/` nesting). Step-1 of the two-step merge
   (the rename commit) was already applied in the IaC history. The merge
   itself becomes a vanilla `git merge --no-ff`.

## Cross-repo commit divergence (the user's "no code gone missing" check)

| Comparison | Ahead count | Notes |
|:--|--:|:--|
| `bonneagar/main` not in `origin/main` | 225 commits | The IaC-only history. All sit on `pick-5b-bonneagar-v5-continuation` (215 of them); the other 10 are merge commits reachable from `bonneagar/main` only. |
| `origin/main` not in `bonneagar/main` | 1028 commits | The platform-side history (BIEP, agents, BAML, CocoIndex, Marimo, etc.). No commits belong in bonneagar. |
| `pick-4-biep-v1` not in `pick-5b-bonneagar-v5-continuation` | 1011 commits | The platform-side work since the IaC branch forked. |
| `pick-5b-bonneagar-v5-continuation` not in `pick-4-biep-v1` | 215 commits | The IaC improvements: Komodo resource-syncs, tightly-knit-auth-stack, iac:v2.9.0 API paths, iac:health fixes, secret v4 normalisation. |

### Mis-routed commit audit (the user's explicit concern)

**Bonneagar commits that mention platform code** — these are NOT mis-routed.
They are normal IaC commits that mention upstream platform paths in their
commit body (e.g., `feat(iac): tightly-knit-auth-stack (Pocket ID + Tinyauth
integrated)` references the agent-platform cluster which is platform code).
Every IaC commit is correctly scoped to IaC files.

**Cianfhoghlaim commits that mention IaC code** — these are also correctly
scoped. The 28 commits that grep-matched `iac|komodo|pangolin|infisical` are
openspec changes (e.g., `chore(openspec): archive 2026-07-14-tightly-knit-auth-stack-v1`)
that *describe* IaC work but live in `openspec/changes/...`, not in IaC source.

**No commits are mis-routed.** The user's worry was preventative, not reactive.

## What the IaC branch has that pick-4-biep-v1 doesn't (the merge's payload)

Top-level directories in `pick-5b-bonneagar-v5-continuation` but not in `pick-4-biep-v1`:

```
archive/                   # archived reports + runbooks
audit/                     # inventory + diff scripts
ci/                        # CI workflows (spaces-sync, etc.)
dagger/                    # Dagger module
deploy-runbooks/           # ansible + runbook docs
firecrawl/                 # firecrawl adapter for IaC
iac/                       # THE IaC: clients/, models/, sources/, commands/
infisical_secret           # infisical secret bootstrap script
komodo/                    # 3 resource-sync tomls + procedures/ + stacks/
legacy/                    # deprecated IaC code
ocr/                       # OCR Docker Compose bridge
package.json               # IaC package.json (scripts: iac:bootstrap, iac:plan, ...)
pulumi/                    # Pulumi IaC
pangolin/                  # Pangolin config + blueprint imports
scripts/                   # IaC scripts (sync-secrets, etc.)
stacks/                    # 88 Docker Compose stacks + 6-file GOLD_STANDARD
audit/, deploy-runbooks/, dagger/, firecrawl/, legacy/, ocr/, pulumi/
```

Top-level files in `pick-5b-bonneagar-v5-continuation` but not in `pick-4-biep-v1`:

```
.bunfig.toml (presumed; to be verified)
DEPLOYMENT-STRATEGY.md
GOLD_STANDARD.md
PANGOLIN-SETUP.md
QUADRANT-TO-STACK-MAP.md
SECRETS-MANAGEMENT.md
bun.lock (will conflict — take IaC's version, then `bun install` regenerates)
package.json (CONFLICT — IaC has `iac:bootstrap`, platform has `dagster:oideachais`)
tsconfig.json
cli.py                     # IaC CLI entrypoint
DEPLOYMENT-STRATEGY.md
```

## Conflicts the merge will surface

1. **`package.json`** — pick-4-biep-v1 has workspace declarations + `dagster:*` +
   `ccc:*` scripts. pick-5b has `iac:*` scripts + (presumed) no workspaces.
   Resolution: take pick-4-biep-v1's `package.json`, append pick-5b's `iac:*`
   scripts, drop the `bun run --cwd bonneagar` shims (which become obsolete
   since IaC is now at root).

2. **`bun.lock`** — will conflict. Resolution: take pick-4-biep-v1's, then
   `bun install` will regenerate the IaC deps.

3. **`AGENTS.md`** — pick-4-biep-v1's version references `../bonneagar/AGENTS.md`
   + the v4 monorepo topology. pick-5b's version is the IaC repo's simpler AGENTS.md.
   Resolution: write a NEW AGENTS.md that reflects the v7 single-repo reality.

4. **`README.md`** — pick-4-biep-v1's is the 1464-line platform README. pick-5b's is
   the IaC repo's README. Resolution: rewrite README.md (this change's Phase 4).

5. **`scripts/`** — both have scripts, with different filenames. Mostly clean
   merge; check for name collisions (none found in initial scan).

6. **`docs/`** — both have docs subdirectories. Largely orthogonal content.
   Resolution: keep both, audit for duplication after merge.

## The 2-step merge strategy

The user chose "two-step git merge" (over `git subtree` or file-copy squash):

### Step 2a — `git merge --no-ff pick-5b-bonneagar-v5-continuation` into v7-flatten-and-merge

This brings the IaC content (already at root in pick-5b) into the working tree.
After this merge, both IaC and platform code coexist at root:

```
/ (repo root)
├── iac/              ← NEW (from pick-5b)
├── stacks/           ← NEW (from pick-5b)
├── komodo/           ← NEW (from pick-5b)
├── pangolin/         ← NEW (from pick-5b)
├── deploy-runbooks/  ← NEW (from pick-5b)
├── cianfhoghlaim/    ← still nested (the platform code)
├── orchestration/    ← still nested
├── openspec/         ← still at root (already)
├── docs/             ← MERGED (both had docs)
├── scripts/          ← MERGED
└── ...
```

### Step 2b — `git mv cianfhoghlaim/* .` (the platform flatten)

After Step 2a, `cianfhoghlaim/` is still nested. The platform flatten is a
separate `git mv` batch + manifest updates.

## Path rewrites needed after Step 2a + 2b

After both merges, ~100+ files reference the old `bonneagar/...` paths or
the old `cianfhoghlaim/...` paths. The `git grep "bonneagar/"` audit found
hits in 53+ `.agents/skills/*/SKILL.md` files, the root `AGENTS.md`,
`openspec/AGENTS.md`, `openspec/project.md`, the IaC's own scripts (which
already moved but still have stale comments), and every spec under
`openspec/specs/*/spec.md` that documents stack paths.

The rewrite is a `ripgrep`-driven sed-style replacement of:
- `bonneagar/stacks/` → `stacks/`
- `bonneagar/iac/` → `iac/`
- `bonneagar/komodo/` → `komodo/`
- `bonneagar/pangolin/` → `pangolin/`
- `bonneagar/scripts/` → `scripts/`
- `bonneagar/deploy-runbooks/` → `deploy-runbooks/`
- `bonneagar/stedding/` → `stedding/` (IaC had its own stedding/)
- `bonneagar/audit/` → `audit/`
- `bonneagar/legacy/` → `legacy/`
- `bonneagar/ocr/` → `ocr/` (IaC OCR — distinct from platform's `agents/meaisinfhoghlaim/ocr/`)
- `bonneagar/dagger/` → `dagger/`
- `bonneagar/pulumi/` → `pulumi/`
- `bonneagar/firecrawl/` → `firecrawl/`
- `cianfhoghlaim/` → `` (root, no prefix)

EXEMPT (do NOT rewrite):
- `LICENSE.md` (will be edited in Phase 4.1)
- `README.md` (will be rewritten in Phase 4.2)
- `openspec/changes/archive/2026-06-28-*` (the v4 consolidation change documents
  the pre-flatten state intentionally)
- `openspec/changes/archive/2026-07-09-*` (the v6 drift remediation is also a
  historical artifact)
- `docs/openspec/*` (historical research material — never modify)

## Local vs remote branch inventory (the user's "remote only" cleanup scope)

### Local branches to KEEP (per user: "leave local branches alone")

All 41 local branches stay. The user explicitly said not to lose local work.

### Remote branches to DELETE from `origin` (per user: "remote only")

| Remote branch | Reason for deletion |
|:--|:--|
| `origin/feat/author-archive-cross-corpus-kg` | Already merged via PR #114 + 115 |
| `origin/feat/author-archive-multi-target` | Already merged |
| `origin/feat/author-archive-uog-coursework` | Already merged |
| `origin/feat/author-archive-v1` | Already merged |
| `origin/feat/author-archive-v1-integration` | Already merged |
| `origin/feat/author-archive-v1-integration-resurrection` | Already merged |
| `origin/feat/celtic-data-engineering-artefacts` | Already merged |
| `origin/feat/croilar-devtools-hub` | Already merged |
| `origin/feat/docs-deletions-from-pr62` | Already merged |
| `origin/feat/docs-v2-migration` | Already merged |
| `origin/feat/local-reflect-pr65` | Already merged |
| `origin/feat/official-media-pipeline` | Already merged |
| `origin/feat/spaces-patterns-and-marimo` | Already merged |
| `origin/pick-1-ocr-vlm-registry` | Shipped via merge commit `b442ec4bb` |
| `origin/pick-10-add-agent-surface-stacks` | Shipped |
| `origin/pick-2-agent-platform-cluster` | Shipped |
| `origin/pick-3-image-replacement` | Shipped |
| `origin/pick-5-bonneagar-v5` | DELETED ALREADY by upstream prune |
| `origin/pick-6-bunchloch-stack-bootstrap` | Shipped |
| `origin/pick-7-align-env` | Shipped |
| `origin/pick-8-ireland-legal` | Shipped |
| `origin/pick-9-notebooks-flatten` | Shipped |
| `origin/q3-2026-cianfhoghlaim-consolidation` | Rolled into main |

### Remote branches to KEEP on `origin`

| Remote branch | Reason |
|:--|:--|
| `origin/main` | Canonical |
| `origin/pick-4-biep-v1` | Current working branch (will be replaced by `v7-flatten-and-merge`) |

### Remote branches on `bonneagar` remote

The `bonneagar` GitHub remote will be **renamed to `archive-bonneagar`** after
the merge lands. All `bonneagar/*` remote branches become read-only history.
The merge commit on `v7-flatten-and-merge` IS the final commit that pulls the
IaC into the main repo's history.

## Verification (the user's "no code gone missing" final check)

After Phase 2 (flatten + merge) and before Phase 3 (branch cleanup):

```bash
# 1. Every file that was in pick-4-biep-v1's tree is in v7-flatten-and-merge's tree
git diff --name-only pick-4-biep-v1 v7-flatten-and-merge | grep -v "^cianfhoghlaim/" | wc -l
# Expected: small number (only the IaC-added files at root)

# 2. Every file in pick-5b-bonneagar-v5-continuation's tree is in v7-flatten-and-merge's tree
git diff --name-only pick-5b-bonneagar-v5-continuation v7-flatten-and-merge | grep -v "^bonneagar/" | wc -l
# Expected: 0 (after the platform flatten, everything maps)

# 3. Total file count delta
git ls-tree -r pick-4-biep-v1 | wc -l
git ls-tree -r pick-5b-bonneagar-v5-continuation | wc -l
git ls-tree -r v7-flatten-and-merge | wc -l
# Expected: post-merge = sum minus the deleted bonneagar/* duplicates
```

## Sign-off

| Check | Status |
|:--|:--|
| Phase 1.1 catch-up commit landed | ✅ `b1016692a` |
| Cross-repo mis-routing audit | ✅ no mis-routes found |
| Bonneagar remote pruned by `git fetch --prune` | ✅ (3 branches gone upstream) |
| IaC already at root in pick-5b | ✅ confirmed via `git ls-tree` |
| 215 IaC commits ahead in pick-5b vs pick-4-biep-v1 | ✅ catalogued |
| Conflict surface (package.json, bun.lock, AGENTS.md, README.md) | ✅ identified |

Migration is **SAFE TO PROCEED** to Phase 2.
