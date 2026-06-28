# Tasks for 2026-06-28-split-leabharlann-bonneagar

## 1. Push infrastructure history to cianfhoghlaim/bonneagar

- [x] Clone kings_college_galway locally to a fresh clone
- [x] Install `git-filter-repo` via `uv tool install`
- [x] Run `git filter-repo --path infrastructure/ --strip-blobs-bigger-than 5M --replace-text <expressions> --path-rename infrastructure/:` to extract infrastructure history
- [x] Add standalone `README.md` and `AGENTS.md` to the new repo
- [x] Force-push to https://github.com/cianfhoghlaim/bonneagar.git main
- [x] Verify on GitHub that the repo is 30 KB (well under the 2 GB limit)

## 2. Rename repo

- [x] User renamed `kings_college_galway` → `cianfhoghlaim` on GitHub
- [x] Update local `origin` URL to `https://github.com/cianfhoghlaim/cianfhoghlaim.git`
- [x] Update `LICENSE.md` to reference the sibling repos

## 3. Replace infrastructure/ with subtree

- [x] `git rm -rf infrastructure/` in monorepo
- [x] `git subtree add --prefix=infrastructure bonneagar main --squash`

## 4. Replace cianfhoghlaim/leabharlann/ with subtree

- [x] `git rm -rf cianfhoghlaim/leabharlann/` in monorepo
- [x] `git subtree add --prefix=cianfhoghlaim/leabharlann leabharlann main --squash`

## 5. Documentation updates

- [x] Update `README.md` — repo constellation, History section (sruth → cianfhoghlaim + GitOps split), Skills section (post-cleanup inventory + retired skills), Multi-agent section (subagent names updated to cianfhoghlaim specialists)
- [x] Update `pyproject.toml` — `description` field
- [x] Update `LICENSE.md` — reference sibling repos
- [x] Add standalone `README.md` and `AGENTS.md` to bonneagar

## 6. OpenSpec updates

- [x] Create `openspec/changes/2026-06-28-split-leabharlann-bonneagar/`
- [x] Write `proposal.md` (Why / What changes / Impact / Tasks)
- [x] Write `tasks.md` (this file)
- [ ] Write `specs/` deltas for affected specs
- [ ] `openspec validate 2026-06-28-split-leabharlann-bonneagar --strict`
- [ ] `openspec archive 2026-06-28-split-leabharlann-bonneagar --yes`

## 7. Push

- [ ] Force-push `chore/split-leabharlann-bonneagar` to `origin/main` (the renamed `cianfhoghlaim` repo)

## Notes

- Bonneagar is a leaner version of infrastructure — large blobs (>5 MB)
  were stripped via filter-repo to keep the repo under GitHub's 2 GB
  hard limit. The dropped blobs were mostly UCAS dataset CSVs that had
  been temporarily committed under `infrastructure/datasets/` and later
  moved out. They live in oideachais.
- Leabharlann is re-imported as-is from
  [cianfhoghlaim/leabharlann](https://github.com/cianfhoghlaim/leabharlann)
  (which already had 6 commits at the time of the subtree-add).
- The `infrastructure/` subtree is 6.9 MB on disk; the
  `cianfhoghlaim/leabharlann/` subtree is 3.4 GB.