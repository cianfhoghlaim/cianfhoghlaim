# Tasks: datasets-cleanup

## Phase 1: Pre-deletion audit

- [ ] Confirm no Python code imports from `oideachais.datasets`
  - `grep -r "oideachais\.datasets" --include="*.py" /Users/cianmacandeisigh/dev/kings_college_galway/`
  - Expected: 0 hits
- [ ] Confirm no Markdown / YAML / BAML / TOML references the directory
  - `grep -r "sruth/oideachais/datasets" --include="*.md" --include="*.yaml" --include="*.yml" --include="*.toml" --include="*.baml" /Users/cianmacandeisigh/dev/kings_college_galway/`
  - Expected: 0 hits outside `sruth/oideachais/datasets/` itself
- [ ] Confirm `sruth/oideachais/samplaí/` is the canonical sample-data location
  - `ls /Users/cianmacandeisigh/dev/kings_college_galway/sruth/oideachais/samplaí/`
  - Expected: brezhoneg, cognates.yaml, cymraeg, gaeilge, gaelg, gaidhlig, kernowek, README.md

## Phase 2: Privacy file removal (PRIORITY)

- [ ] **Delete the privacy-sensitive file** `sruth/oideachais/datasets/emily_rachel_2022_2026_gaeilge_ard.pdf`
- [ ] **Delete its byte-identical twin** `sruth/oideachais/datasets/gaeilge.pdf`
- [ ] Verify deletion: `ls sruth/oideachais/datasets/emily*` → "No such file or directory"
- [ ] Verify byte-identical: `md5 sruth/oideachais/datasets/emily_rachel_2022_2026_gaeilge_ard.pdf sruth/oideachais/datasets/gaeilge.pdf` (if both still exist, both MD5s match)

## Phase 3: Wholesale directory deletion

- [ ] Delete the entire `sruth/oideachais/datasets/` directory tree
  - `rm -rf /Users/cianmacandeisigh/dev/kings_college_galway/sruth/oideachais/datasets/`
  - Expected: removes 12 top-level entries + 100+ sub-entries (~3 MB)
- [ ] Verify deletion: `ls sruth/oideachais/datasets/` → "No such file or directory"
- [ ] Verify with git: `git status` should show the deletion

## Phase 4: Documentation migration

- [ ] Add a 2-paragraph "Secrets migration note" to the root `AGENTS.md`
  - Pointer to the existing `## Secrets Bootstrap (do not skip)` section (line 32-58)
  - Brief note that the 1Password+SOPS+Komodo plan in the deleted file is superseded
- [ ] Verify root `AGENTS.md` still references the Infisical + Locket + mise flow correctly

## Phase 5: .gitignore

- [ ] Add `sruth/oideachais/datasets/` to the root `.gitignore`
  - Add a comment: `# stale scratch directory — see openspec/changes/datasets-cleanup/`
- [ ] Verify `.gitignore` syntax is correct (no broken patterns)

## Phase 6: Validation

- [ ] `git status` shows only:
  - `D sruth/oideachais/datasets/` (the deleted tree)
  - `M AGENTS.md` (the documentation migration)
  - `M .gitignore` (the gitignore addition)
- [ ] `openspec validate datasets-cleanup --strict` passes
- [ ] `mise turbo lint` passes (or the configured linter)
- [ ] `mise turbo test` passes (or the configured test runner)
- [ ] No new imports in any Python file
- [ ] No broken references in any docs/ files

## Phase 7: Land the plane

- [ ] `git add -A && git commit -m "datasets-cleanup: delete stale scratch directory + privacy-sensitive file"`
- [ ] `git pull --rebase`
- [ ] `git push origin q3-2026-oideachais-consolidation`
- [ ] Open a PR (or push directly if main is acceptable)
- [ ] `git status` → "up to date with origin"
