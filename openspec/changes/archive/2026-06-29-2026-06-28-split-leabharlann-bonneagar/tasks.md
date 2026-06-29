# Tasks for 2026-06-28-split-leabharlann-bonneagar — **AMENDED 2026-06-29**

> The original proposal called for `git subtree`s. That approach was
> attempted and **reverted on 2026-06-29** because the 3.4 GB leabharlann
> PDF corpus inflated every push to 3 GB. The new approach uses `git
> worktree`s at the root of the workspace. The original subtree tasks
> are preserved below with the `[SUBTREE — REVERTED]` prefix so the
> history is auditable.

## 1. Push infrastructure history to cianfhoghlaim/bonneagar

- [x] Clone kings_college_galway locally to a fresh clone
- [x] Install `git-filter-repo` via `uv tool install`
- [x] Run `git filter-repo --path infrastructure/ --strip-blobs-bigger-than 5M --replace-text <expressions> --path-rename infrastructure/:` to extract infrastructure history
- [x] Add standalone `README.md` and `AGENTS.md` to the new repo
- [x] Force-push to https://github.com/cianfhoghlaim/bonneagar.git main
- [x] Verify on GitHub that the repo is 30 KB (well under the 2 GB limit)

## 2. Push leabharlann history to cianfhoghlaim/leabharlann

- [x] Run `git filter-repo --path cianfhoghlaim/leabharlann/ --path-rename cianfhoghlaim/leabharlann/:` to extract leabharlann history
- [x] Add standalone `README.md` to the new repo
- [x] Force-push to https://github.com/cianfhoghlaim/leabharlann.git main

## 3. Rename repo

- [x] User renamed `kings_college_galway` → `cianfhoghlaim` on GitHub
- [x] Update local `origin` URL to `https://github.com/cianfhoghlaim/cianfhoghlaim.git`
- [x] Update `LICENSE.md` to reference the sibling repos

## 4. [SUBTREE — REVERTED] Replace infrastructure/ with subtree

- [x] `git rm -rf infrastructure/` in monorepo
- [x] `git subtree add --prefix=infrastructure bonneagar main --squash` (added 973 files, 6.9 MB)
- [x] **REVERTED 2026-06-29** — `git reset --hard 33500d388` undid the 4 subtree commits (good for size; the bonsai of `infrastructure/` content is no longer in the monorepo's git history)

## 5. [SUBTREE — REVERTED] Replace cianfhoghlaim/leabharlann/ with subtree

- [x] `git rm -rf cianfhoghlaim/leabharlann/` in monorepo
- [x] `git subtree add --prefix=cianfhoghlaim/leabharlann leabharlann main --squash` (added 2,400 files, **3.4 GB** — was the primary reason for the revert)
- [x] **REVERTED 2026-06-29** — same `git reset --hard 33500d388` as task 4

## 6. Add worktrees at the root of the workspace (current approach)

- [x] `git worktree add ./bonneagar bonneagar/main` — created worktree at the root; local branch `bonneagar-main` tracks `bonneagar/main`
- [x] `git worktree add ./leabharlann leabharlann/main` — created worktree at the root; local branch `leabharlann-main` tracks `leabharlann/main`
- [x] Set up `git config user.email` and `git config user.name` in each worktree

## 7. Documentation updates

- [x] Update `README.md` — repo constellation, worktree approach, History section (sruth → cianfhoghlaim + GitOps split), Skills section (post-cleanup inventory + retired skills), Multi-agent section (subagent names updated to cianfhoghlaim specialists), full rewrite for v4 + research program + planned restructuring
- [x] Update `pyproject.toml` — `description` field
- [x] Update `LICENSE.md` — reference sibling repos
- [x] Add standalone `README.md` and `AGENTS.md` to bonneagar

## 8. OpenSpec updates

- [x] Create `openspec/changes/2026-06-28-split-leabharlann-bonneagar/`
- [x] Write `proposal.md` (Why / What changes / Impact / Tasks)
- [x] Write `tasks.md` (this file)
- [x] Amend proposal + tasks to reflect the worktree approach (this amendment)
- [x] Write `specs/` deltas for affected specs (infrastructure-stacks + oideachais-leabharlann)
- [x] `openspec validate 2026-06-28-split-leabharlann-bonneagar --strict` (verified 2026-06-29)
- [x] `openspec archive 2026-06-28-split-leabharlann-bonneagar --yes` (verified 2026-06-29)

## 9. Push

- [ ] Push the README + openspec changes to `origin/main` (deferred to user — they own push)

## Notes

- Bonneagar is a leaner version of infrastructure — large blobs (>5
  MB) were stripped via filter-repo to keep the repo under GitHub's
  2 GB hard limit. The dropped blobs were mostly UCAS dataset CSVs
  that had been temporarily committed under
  `infrastructure/datasets/` and later moved out. They live in
  oideachais.
- Leabharlann is re-imported as-is from
  [cianfhoghlaim/leabharlann](https://github.com/cianfhoghlaim/leabharlann)
  (which already had 6 commits at the time of the subtree-add).
- **The subtree approach was reverted on 2026-06-29** because the
  3.4 GB leabharlann corpus made every `git push` upload 3 GB of
  binary data. The worktree approach avoids this by not committing
  the sibling content to the monorepo.
- The 6.9 MB `infrastructure/` subtree was also reverted as part of
  the same `git reset --hard 33500d388`, for consistency.
- After the revert, the monorepo's push size is 0 MB ahead of
  `origin/main` until the README + openspec changes are committed.
