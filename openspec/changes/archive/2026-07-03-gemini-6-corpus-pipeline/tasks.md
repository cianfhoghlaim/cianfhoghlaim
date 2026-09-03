# Tasks: 2026-07-03-gemini-6-corpus-pipeline

## Phase 1 — File authoring (30 min)

- [x] 1.1 Create `cianfhoghlaim/baml/processing/legal_case_profile.baml`
- [x] 1.2 Create `cianfhoghlaim/baml/processing/topic_profile.baml`
- [x] 1.3 Create `cianfhoghlaim/dlt/filesystem/gemini_corpus_source.py`
- [x] 1.4 Create 2 defs.yaml (1_ingestion/legal_research/gemini_corpus, 3_model_lifecycle/legal_research/gemini_corpus)
- [x] 1.5 Create `gemini_corpus_assets.py` (6 L1 + 6 L2 + 6 L3 + 1 cross = 19 assets)
- [x] 1.6 Create 6 per-corpus overview notebooks (law/medical/politics/culture/technology/other)
- [x] 1.7 Create 3 cross-corpus notebooks (timeline, jurisdictional_map, pattern_detection)
- [x] 1.8 Write proposal.md + tasks.md + 1 spec delta

## Phase 2 — Validate (2 min)

- [ ] 2.1 `openspec validate 2026-07-03-gemini-6-corpus-pipeline --strict`
- [ ] 2.2 Verify all 13 new files parse

## Phase 3 — Smoke tests (5 min)

- [ ] 3.1 `ls /Users/.../leabharlann/gemini_deep_research/{law,medical,politics,culture,technology,other}/ | wc -l` → 224
- [ ] 3.2 `marimo parse notebooks/dashboards/law/01_law_corpus_overview.py` parses

## Phase 4 — Stage commits

- [ ] 4.1 `git add cianfhoghlaim/baml/processing/legal_case_profile.baml cianfhoghlaim/baml/processing/topic_profile.baml`
- [ ] 4.2 `git commit -m "feat(baml): create 2 Gemini-corpus BAML files (legal_case_profile + topic_profile)"`
- [ ] 4.3 `git add cianfhoghlaim/dlt/filesystem/gemini_corpus_source.py`
- [ ] 4.4 `git commit -m "feat(dlt): add gemini_corpus_source.py (224 PDFs across 6 corpora + filename-based classification)"`
- [ ] 4.5 `git add cianfhoghlaim/dagster/defs/`
- [ ] 4.6 `git commit -m "feat(dagster): add gemini 6-corpus assets + 2 defs.yaml (L1 ingestion + L3 cognify)"`
- [ ] 4.7 `git add cianfhoghlaim/notebooks/dashboards/{law,medical,politics,culture,technology,other}/`
- [ ] 4.8 `git commit -m "feat(notebooks): create 9 Gemini-corpus dev notebooks (6 overviews + 3 cross-corpus)"`
- [ ] 4.9 `git add openspec/changes/2026-07-03-gemini-6-corpus-pipeline/`
- [ ] 4.10 `git commit -m "docs(openspec): 2026-07-03-gemini-6-corpus-pipeline change (proposal + tasks + 1 spec delta)"`
