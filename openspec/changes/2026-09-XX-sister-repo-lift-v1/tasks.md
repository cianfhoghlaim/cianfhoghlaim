# Tasks — Sister-Repo Lift v1

> 5 sections, 12 tasks. All tasks MUST pass before
> `openspec archive 2026-09-XX-sister-repo-lift-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [x] **A.1** Author `proposal.md` (with the customisation matrix
  covering all 6 sisters: bonneagar + tuatha + ciancheiltis +
  ciandlithe + cianchosaint + gemini_hackathon) + `tasks.md` +
  `specs/sister-repo-customisation/spec.md`
- [ ] **A.2** `uv run openspec validate 2026-09-XX-sister-repo-lift-v1 --strict` → exits 0

## Phase B — Create the 6 lift patches in `openspec/sister-lifts/` (10 min)

- [ ] **B.1** `openspec/sister-lifts/bonneagar-iac-gcp-mirror-lift-v1.md` — 5 files (B.1-B.5), 3 PRs, ≥ 3 items per PR
- [ ] **B.2** `openspec/sister-lifts/tuatha-adk-pipecat-lift-v1.md` — 5 files (T.1-T.5), 3 PRs, ≥ 3 items per PR
- [ ] **B.3** `openspec/sister-lifts/ciancheiltis-celtic-baml-lift-v1.md` — 5 files (C.1-C.5), 3 PRs, ≥ 3 items per PR
- [ ] **B.4** `openspec/sister-lifts/ciandlithe-legal-baml-lift-v1.md` — 5 files (L.1-L.5), 3 PRs, ≥ 3 items per PR
- [ ] **B.5** `openspec/sister-lifts/cianchosaint-defence-baml-lift-v1.md` — 5 files (D.1-D.5), 3 PRs, ≥ 3 items per PR
- [ ] **B.6** `openspec/sister-lifts/gemini-hackathon-oss-substrate-lift-v1.md` — 5 files (G.1-G.5), 3 PRs, ≥ 3 items per PR

## Phase C — Write the test (5 min)

- [ ] **C.1** `tests/test_phase12_sister_repo_lift.py` with at least these assertions:
  - All 6 lift-patch files exist in `openspec/sister-lifts/`
  - All referenced source files in cianfhoghlaim exist (22 source files)
  - Each lift-patch has a per-PR checklist with ≥ 3 items
  - The customisation matrix in `proposal.md` mentions all 6 sisters

## Phase D — Quality gates (1 min)

- [ ] **D.1** `uv run openspec validate 2026-09-XX-sister-repo-lift-v1 --strict` → exits 0
- [ ] **D.2** `uv run pytest tests/test_phase12_sister_repo_lift.py -v` → all assertions pass

## Phase E — Update the v6 era plan (1 min)

- [ ] **E.1** Update
  `openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`
  with the Phase 12 status (AUTHORED + 6 lift patches + 1 test).

## Out of task scope

- The actual per-sister-repo PRs (deferred to the sister repo
  maintainers; each sister repo openspec change proposes its own
  PR with the per-sister customisation from the lift patches).
- Wholesale copy of the cianfhoghlaim substrate into the sister
  repos — the operator's earlier directive forbids this.
- Phase 10 v7 rewrite — handled in
  `2026-09-01-v7-from-the-ground-up-v1/`.
- Updating the v7 architecture doc.
