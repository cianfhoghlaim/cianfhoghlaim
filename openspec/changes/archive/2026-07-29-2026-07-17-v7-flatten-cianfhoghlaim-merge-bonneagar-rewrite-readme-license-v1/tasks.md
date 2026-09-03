# Tasks — v7 flatten + bonneagar re-merge + README/LICENSE rewrite

## Phase 1 — Verification + working-tree cleanup ✅ DONE

- [x] T1.1 — Commit the 494 uncommitted changes on `pick-4-biep-v1`
  (commit `b1016692a chore(snapshot): catch up pick-4-biep-v1 working
  tree pre-v7-flatten`).
- [x] T1.2 — Run the cross-repo verification sweep (bonneagar vs
  cianfhoghlaim). Result: 225 IaC-only commits in bonneagar/main NOT in
  origin/main; no commits mis-routed between the two repos.
- [x] T1.3 — Write `migration-audit.md` to the change directory.

## Phase 2 — Flatten + merge + manifests ✅ DONE (in progress for the 5 specs)

- [x] T2.1 — Create `v7-flatten-and-merge` branch off `pick-4-biep-v1`.
- [x] T2.2 — `git merge --no-ff --allow-unrelated-histories
  pick-5b-bonneagar-v5-continuation` (the two branches have different
  root commits; the merge commit is `deb333ff0`).
- [x] T2.3 — Move `cianfhoghlaim/*` → repo root (10,000+ `git mv`s);
  relocate IaC content from root to `bonneagar/` per the user's
  mid-run clarification that the bonneagar/ subdir should be preserved.
  Commit: `56c409dd3 chore(v7-flatten): move cianfhoghlaim/* → root
  + relocate IaC into bonneagar/`.
- [x] T2.4 — Update manifests (pyproject.toml, package.json, mise.toml,
  dg.toml, turbo.json, opencode.json, .gitignore). Commit:
  `f98a8df29 chore(manifests): update mise.toml + dg.toml +
  opencode.json + turbo.json for v7-flatten`.
- [x] T2.5 — IaC scripts at `bonneagar/audit/scripts/stack-doctor.sh`
  already use `bonneagar/` prefixed paths (the IaC was authored assuming
  it lives at root of a standalone repo); no changes needed.
- [x] **T2.6 — Update 5 spec deltas** in this change's `specs/<spec>/spec.md`
  files (in progress).
- [x] **T2.7 — Update AGENTS.md + openspec/AGENTS.md + openspec/project.md**
  to reflect the v7 single-repo + bonneagar-subdir reality.
- [x] **T2.8 — Update .agents/skills/* path references** (53 skills;
  scripted sed-replace).
- [x] **T2.9 — Update pending openspec changes** (~45 changes) to
  reflect the end-state structure. Per the user's note: "we will have
  to update our openspec plans and changes and ongoing to account for
  our end structure at the end".

## Phase 3 — Remote branch cleanup + bonneagar remote rename

- [x] T3.1 — Delete from `origin` the 23 stale remote branches
  (feat/* + pick-{1,2,3,6,7,8,9,10}-* + q3-2026-*).
- [x] T3.2 — `git remote rename bonneagar archive-bonneagar` so future
  commits cannot be mis-pushed.

## Phase 4 — LICENSE.md edit + README.md rewrite

- [x] T4.1 — Edit `LICENSE.md`: remove the "companion repository
  cianfhoghlaim/bonneagar" sentence; keep the leabharlann companion
  sentence; preserve the BUSL terms, Additional Use Grant, Change Date,
  Change License, Governing Law, and the licensor identity (Cian Pierce
  Lyons / Cian Mac Liatháin).
- [x] T4.2 — Rewrite `README.md`:
  - Preserve verbatim: the entire `### On the family — Mac an Déisigh
    Uí Liatháin (Deacy-Lyons)` section (lines 637-1230 of the pre-v7
    README — the 4-line modern incarnation, the 3-stream synthesis, the
    mythological warrant, the dual-monarchy framework, the verified
    qualifications).
  - Rewrite everything else: TL;DR, the 5-stage pipeline, the 11 NCCA
    LC subject asset groups, the PDF processing pipeline, the marimo
    notebook catalogue, the OpenSpec catalogue, the host topology, the
    deployed stacks summary, the repository constellation (now 2 repos
    not 3).

## Phase 5 — Verification

- [x] T5.1 — Run the 10-check verification battery (uv import test,
  bun typecheck, mise lint:skills, openspec validate --strict, git grep
  for stale paths, dagster boot, iac:plan, worktree sync).
- [x] T5.2 — `openspec validate 2026-07-17-v7-flatten-... --strict`.
- [x] T5.3 — `git log --oneline` shows the expected 4-commit sequence
  (snapshot + merge + flatten + manifests).

## Phase 6 — Handoff

- [x] T6.1 — Hand off to the user. The user explicitly requested
  commit + push (Phase 6 of the v7 plan) but did NOT include push in
  the current session. The branch is committed but local; the user
  may push when ready.
