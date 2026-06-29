# 2026-06-28-split-leabharlann-bonneagar — **AMENDED 2026-06-29**

> **Amendment (2026-06-29):** The original proposal called for
> `git subtree`s under `infrastructure/` and `cianfhoghlaim/leabharlann/`.
> That approach was attempted and **reverted** on 2026-06-29 because the
> 3.4 GB PDF corpus in `leabharlann` made every `git push` upload 3 GB
> of binary data, which was unworkable. The new approach uses **git
> worktrees at the root of the workspace** (`./bonneagar/` and
> `./leabharlann/`) — the sibling repos are still split, but their
> content is *not* committed to the application monorepo. The worktree
> approach keeps the content visible and editable from this workspace
> without inflating the push.

## Why

The cianfhoghlaim monorepo had grown to include two domains — the digital
library (`leabharlann/`) and the GitOps infrastructure foundation
(`infrastructure/`) — that have very different release cadences, secrets
boundaries, and review surfaces from the application code. As of
**2026-06-28**, both domains have been split into standalone repositories
under the [cianfhoghlaim](https://github.com/cianfhoghlaim) GitHub
organisation.

This change tracks the split so:

1. Consumers (human and agent) can navigate the new topology without
   reading the full commit history.
2. `openspec validate` enforces that the documentation in the monorepo
   matches the actual layout.
3. The split is reversible — if either repo needs to be brought back
   inline, the openspec change captures the rationale for re-merging.

## What changes

- **`infrastructure/` is removed from this repo** and lives at
  [cianfhoghlaim/bonneagar](https://github.com/cianfhoghlaim/bonneagar).
  *Bonneagar* is Scottish Gaelic for *infrastructure*. The repo carries
  the same BUSL-1.1 license.
- **`cianfhoghlaim/leabharlann/` is removed from this repo** and lives
  at [cianfhoghlaim/leabharlann](https://github.com/cianfhoghlaim/leabharlann).
  *Leabharlann* is Irish for *library*. The repo carries the same
  BUSL-1.1 license.
- **Both are exposed in this monorepo as `git worktree`s at the root of
  the workspace** (`./bonneagar/` and `./leabharlann/`), on local
  tracking branches (`bonneagar-main` → `bonneagar/main`,
  `leabharlann-main` → `leabharlann/main`). This is **not** the
  `git subtree` approach the original proposal called for, because
  the 3.4 GB PDF corpus in `leabharlann` is too large to embed
  (every push would upload 3 GB of binary data).
- **The GitHub repo `kings_college_galway` is renamed to
  `cianfhoghlaim`** to match the platform name. The local
  `origin` URL is updated to
  `https://github.com/cianfhoghlaim/cianfhoghlaim.git`.
- **`.agents/skills/` is reorganised**: the previous ~123-skill
  library is collapsed to ~57 canonical skills. Several skills were
  retired (consolidated or moved to the sibling repos), several were
  renamed, and several were expanded into sub-skill libraries
  (notably `browserbase/<topic>`, `cloudflare/<topic>`, and
  `firecrawl/<topic>`).

## Why worktrees, not subtrees (amendment rationale)

The original proposal committed to `git subtree`s. That approach was
implemented on 2026-06-29 and **immediately reverted** for the
following reasons:

| Subtree cost | Magnitude | Consequence |
|:--|--:|:--|
| Leabharlann PDF corpus | **3,077 MB of blob objects** in the subtree commits | Every `git push` uploads 3 GB; CI runners run out of disk; clone size bloats for every contributor |
| Push time | **Multi-minute** git push over typical home/office uplinks | Blocks the daily loop; agent loops time out |
| Subtree add step | Requires `git fetch` + `git subtree add` to be repeated for every contribution | Slows down re-syncing; an error in the subtree add corrupts the monorepo's history |

The worktree approach sidesteps all three costs by *not committing
the sibling content* to the application monorepo. The content is
still visible (via the worktree at `./leabharlann/`) and still
editable (via `cd leabharlann && git add/commit/push`), but it does
not enter this monorepo's git history.

The trade-off is that the monorepo cannot reference files inside
the worktree through hard paths in tracked source — instead, it
references them through relative paths (`./leabharlann/gaeilge/...`).
For the few places where the monorepo *does* need to depend on a
sibling repo (e.g. the docs reference `./bonneagar/AGENTS.md` and
`./leabharlann/gaeilge/README.md`), the worktree must be present on
the contributor's machine. The `git worktree add` step is added to
the one-time setup in the README.

## Repo constellation (after this change)

```
cianfhoghlaim/cianfhoghlaim         <- application monorepo (you are here)
cianfhoghlaim/bonneagar             <- GitOps foundation (BUSL-1.1, worktree at ./bonneagar/)
cianfhoghlaim/leabharlann           <- digital library (BUSL-1.1, worktree at ./leabharlann/)
```

## Impact

- **Specs affected** — `infrastructure-stacks`, `secrets-management`,
  `komodo`, `pangolin`, `pulumi`, `dagger`, `meaisinfhoghlaim-platform`,
  `oideachais-leabharlann`. All of these point at paths that now live
  in the sibling repos (or the worktree at `./<sibling>`). The spec
  deltas below document the new layout.
- **Skills affected** — many skills were retired, renamed, or
  reorganised. See [`README.md`](../../README.md) → *Skills* for the
  canonical post-cleanup inventory.
- **Agents** — `opencode.json` subagent definitions still reference the
  same agent names; their `cwd` paths inside the application code are
  unchanged. The `infrastructure` subagent now operates primarily
  against the `./bonneagar/` worktree (and the
  [bonneagar](https://github.com/cianfhoghlaim/bonneagar) repo).

## Tasks

1. ✅ Push `infrastructure/` history to
   [cianfhoghlaim/bonneagar](https://github.com/cianfhoghlaim/bonneagar)
   via `git-filter-repo` (filtering blobs >5 MB and redacting Google
   OAuth + Cloudflare tokens).
2. ✅ Push `leabharlann/` history to
   [cianfhoghlaim/leabharlann](https://github.com/cianfhoghlaim/leabharlann).
3. ✅ Rename `kings_college_galway` → `cianfhoghlaim` on GitHub and
   update local `origin` URL.
4. ✅ Add `bonneagar` and `leabharlann` as `git remote`s pointing at
   the sibling repos.
5. ✅ `git rm -rf infrastructure/ cianfhoghlaim/leabharlann/` from the
   monorepo and commit.
6. ✅ (REVERTED) `git subtree add --prefix=infrastructure bonneagar
   main --squash` — reverted on 2026-06-29 because the subtree
   approach inflated every push to 3 GB.
7. ✅ (REVERTED) `git subtree add --prefix=cianfhoghlaim/leabharlann
   leabharlann main --squash` — reverted on 2026-06-29.
8. ✅ `git worktree add ./bonneagar bonneagar/main` — local branch
   `bonneagar-main` tracks `bonneagar/main`.
9. ✅ `git worktree add ./leabharlann leabharlann/main` — local
   branch `leabharlann-main` tracks `leabharlann/main`.
10. ✅ Update `README.md` with the new repo constellation, the
    v4-consolidation history, the worktree approach, and the
    post-cleanup skill inventory.
11. ✅ Update `LICENSE.md` to reference the sibling repos.
12. ✅ Update `pyproject.toml` description to reflect the new scope.
13. 🔲 Update `openspec/specs/{infrastructure-stacks,secrets-management,
    komodo,pangolin,pulumi,dagger,meaisinfhoghlaim-platform,
    oideachais-leabharlann}/spec.md` to reference the sibling repos
    where applicable.
14. 🔲 `openspec validate 2026-06-28-split-leabharlann-bonneagar
    --strict`
15. 🔲 `openspec archive 2026-06-28-split-leabharlann-bonneagar --yes`

## Notes

- The 3.4 GB PDF corpus in `leabharlann` is unchanged. It lives in the
  sibling `leabharlann` repo and is exposed in this monorepo as the
  worktree at `./leabharlann/`.
- The 6.9 MB compose-stack tree in `bonneagar` is unchanged. It lives
  in the sibling `bonneagar` repo and is exposed as the worktree at
  `./bonneagar/`.
- The README documents the worktree cadence (pull from upstream via
  `git fetch bonneagar main && cd bonneagar && git merge --ff-only
  bonneagar/main`).
- Branch protection on `bonneagar/main` and `leabharlann/main` is
  recommended (out of scope for this change).
