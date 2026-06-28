# 2026-06-28-split-leabharlann-bonneagar

## Why

The cianfhoghlaim monorepo had grown to include two domains — the digital
library (`leabharlann/`) and the GitOps infrastructure foundation
(`infrastructure/`) — that have very different release cadences, secrets
boundaries, and review surfaces from the application code. As of
**2026-06-28**, both domains have been split into standalone repositories
under the [cianfhoghlaim](https://github.com/cianfhoghlaim) GitHub
organisation and are now consumed as `git subtree`s from the application
monorepo.

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
- **`cianfhoghlaim/leabharlann/` is removed from this repo** and lives at
  [cianfhoghlaim/leabharlann](https://github.com/cianfhoghlaim/leabharlann).
  *Leabharlann* is Irish for *library*. The repo carries the same
  BUSL-1.1 license.
- **Both are re-imported as `git subtree`s** so the monorepo continues
  to have local working copies under `infrastructure/` and
  `cianfhoghlaim/leabharlann/`. Updates are pulled manually with
  `git subtree pull --prefix=<path> <remote> main --squash`.
- **The GitHub repo `kings_college_galway` is renamed to
  `cianfhoghlaim`** to match the platform name. The local
  `origin` URL is updated to `https://github.com/cianfhoghlaim/cianfhoghlaim.git`.
- **`.agents/skills/` is reorganised**: the previous ~123-skill library
  is collapsed to ~57 canonical skills. Several skills were retired
  (consolidated or moved to the sibling repos), several were renamed,
  and several were expanded into sub-skill libraries (notably
  `browserbase/<topic>`, `cloudflare/<topic>`, and `firecrawl/<topic>`).

## Repo constellation (after this change)

```
cianfhoghlaim/cianfhoghlaim         <- application monorepo (you are here)
cianfhoghlaim/bonneagar             <- GitOps foundation (BUSL-1.1)
cianfhoghlaim/leabharlann           <- digital library (BUSL-1.1)
```

## Impact

- **Specs affected** — `infrastructure-stacks`, `secrets-management`,
  `komodo`, `pangolin`, `pulumi`, `dagger`, `meaisinfhoghlaim-platform`,
  `oideachais-leabharlann`. All of these point at paths that now live
  in the sibling repos. The spec deltas below document the new URLs.
- **Skills affected** — many skills were retired, renamed, or
  reorganised. See [`README.md`](../../README.md) → *Skills* for the
  canonical post-cleanup inventory.
- **Agents** — `opencode.json` subagent definitions still reference the
  same agent names; their `cwd` paths inside the application code are
  unchanged. The `infrastructure` subagent now operates primarily
  against the [bonneagar](https://github.com/cianfhoghlaim/bonneagar)
  repo.

## Tasks

1. ✅ Push `infrastructure/` history to
   [cianfhoghlaim/bonneagar](https://github.com/cianfhoghlaim/bonneagar)
   via `git-filter-repo` (filtering blobs >5 MB and redacting
   Google OAuth + Cloudflare tokens).
2. ✅ Rename `kings_college_galway` → `cianfhoghlaim` on GitHub and
   update local `origin` URL.
3. ✅ `git rm -rf infrastructure/ cianfhoghlaim/leabharlann/` from the
   monorepo and commit.
4. ✅ `git subtree add --prefix=infrastructure bonneagar main --squash`
   to re-import bonneagar.
5. ✅ `git subtree add --prefix=cianfhoghlaim/leabharlann leabharlann
   main --squash` to re-import leabharlann.
6. ✅ Update `README.md` with the new repo constellation, the
   v4-consolidation history, and the post-cleanup skill inventory.
7. ✅ Update `LICENSE.md` to reference the sibling repos.
8. ✅ Update `pyproject.toml` description to reflect the new scope.
9. 🔲 Update `openspec/specs/{infrastructure-stacks,secrets-management,
   komodo,pangolin,pulumi,dagger,meaisinfhoghlaim-platform,oideachais-
   leabharlann}/spec.md` to reference the sibling repos where applicable.
10. 🔲 `openspec validate 2026-06-28-split-leabharlann-bonneagar --strict`
11. 🔲 `openspec archive 2026-06-28-split-leabharlann-bonneagar --yes`
12. 🔲 Force-push the resulting commits to `origin/main` (the renamed
    `cianfhoghlaim` repo).