# Tasks: delete-anti-phish-space

## 1. Move the Space to the private archive

- [x] `git mv spaces/anti-phish/ archive/anti-phish-2022-academic/`
- [x] Rename the original `README.md` to `README.md.bak`
      (preserves the original content)
- [x] Create a new `archive/anti-phish-2022-academic/README.md`
      that explains the move + the future path for re-publication

## 2. Validate + commit + push + archive

- [x] `openspec validate delete-anti-phish-space --strict`
- [x] Commit with message
      `delete-anti-phish-space: move 2022 academic project to private archive`
- [x] Archive the openspec change
- [x] `git push`
