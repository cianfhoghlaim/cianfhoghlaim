# Tasks — Extend `cianfhoghlaim-marimo-dashboards` (Phase 2)

## 1. Audit existing 10 dashboards + spec

- [x] Read `openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md`
- [x] List `notebooks/10_marimo_dashboards/` (10 dashboards
  from commit `44cabc151`)
- [x] Understand the existing pattern (PEP 723 inline deps, md:oideachais
  with fallback, altair charts, health banner)

## 2. Ship 10 additional dashboards at `notebooks/11_marimo_dashboards_v2/`

- [x] `01_leabharlann_corpus_overview.py` — 6-subdir corpus, language pie,
  file-size violin, year trend, health banner
- [x] `02_leabharlann_subdir_matrix.py` — subdir × language matrix,
  subdir × year-quadrant matrix, top-12 topic pairs, avg pages
- [x] `03_bge_m3_embedding_coverage.py` — per-subdir embedder coverage,
  embedding density by mode, cosine-similarity histogram, lang parity
- [x] `04_university_institution_matrix.py` — 13 HEI catalogue (8
  universities + 4 TUs + 1 college), type distribution, NFQ matrix,
  CAO coverage, NUI constituent membership
- [x] `05_qqi_nfq_ladder.py` — 8 QQI awards × 13 HEIs ladder matrix,
  NFQ distribution, ladder density by NFQ, per-HEI ladder coverage
- [x] `06_biep_leabharlann_edges.py` — 6×6×3×2 cross-archive matrix,
  edge-type distribution, top-15 strongest edges, language parity
- [x] `07_biep_official_media_edges.py` — 6 subjects × 5 resolvers
  (Wikipedia, Companies House, CRO, Mastodon, Bluesky) match matrix,
  resolver distribution, top-15 strongest edges, confidence violin
- [x] `08_leabharlann_culture_heritage_edges.py` — 6 subdirs × 5
  culture-heritage datasets (Dúchas, National Museum, Digital Repository
  of Ireland, ITMA, Cultural Heritage Agency) cross-archive matrix,
  edge-type distribution, top-15 strongest edges, language parity
- [x] `09_k12_university_pipeline_matrix.py` — 5 stages × 3 LC levels
  depth matrix, stage × HEI pipeline matrix, per-stage depth,
  enrolment funnel
- [x] `10_year_level_coverage.py` — 5 stages × 10 years coverage,
  per-year topic volume, per-year HEI distribution, bilingual coverage

## 3. Register the new subdir in `cli.py`

- [x] Add `"11_marimo_dashboards_v2"` to the `GROUPS` tuple in
  `notebooks/cli.py`

## 4. Verify

- [x] All 10 new dashboards AST-parse cleanly
- [x] `uv run cianfhoghlaim-marimo list 11_marimo_dashboards_v2`
  discovers all 10 new entries
- [x] The 10 existing dashboards still AST-parse OK
- [x] The other 15+ leaving_cert / biep_motherduck / semantic_search
  notebooks still AST-parse OK (modulo 1 pre-existing indentation issue
  in `04_biep_motherduck/01_curriculum_educator.py` from commit
  `3b7dcbd22` — NOT my regression)

## 5. Write the openspec change

- [x] Create `openspec/changes/2026-07-15-cianfhoghlaim-marimo-dashboards-extension-v1/`
- [x] `proposal.md` — explain the 10 new dashboards
- [x] `tasks.md` — the 5 steps above
- [x] `specs/cianfhoghlaim-marimo-dashboards/spec.md` — MODIFIED: add
  1 ADDED requirement "Phase 2 complete: 10 additional marimo
  dashboards at `notebooks/11_marimo_dashboards_v2/0[1-9]_*.py` +
  `10_*.py` ship the leabharlann corpus + university extraction +
  cross-archive edges + K-12 → university pipeline coverage"

## 6. Commit + push

- [ ] `git add -A`
- [ ] Commit with the canonical message (the one in the task brief)
- [ ] `git push --set-upstream origin pick-4-biep-v1`