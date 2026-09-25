# Tasks: Celtic + Multilingual Education Pipeline Overhaul (umbrella)

> **Sequential execution — 5 phases × 10 stages = 50 working days.**
> **Per-stage verify:** ruff + baml-cli generate + unit tests (~10 min)
> **Per-phase verify:** scripts/verify.sh + sync:all + lint:registry + openspec validate --strict + budget check (~2 hours)

## Action 0 — Pre-flight (≤ 1 day)

- [x] **0.1**. Wholesale-copy infrastructure — `scripts/sister_lifts.py` + `stedding/sister-lifts/WHOLESALE_COPY_INDEX.md`
- [x] **0.2**. 5 openspec changes filed (this umbrella + 4 phase changes)
- [ ] **0.3**. Submit 5 CLARIN / institutional data-access requests (see `scripts/access_requests.py`)
- [ ] **0.4**. Create `tests/integration/test_full_celtic_pipeline.py` (the per-phase smoke test)

## Phase 1 — Irish NLP Foundation (Weeks 1-2)

**Change:** `2026-09-25-gaeilge-nlp-foundation-v1`

- [x] **1.1**. Unify 8-entry `CelticLanguage` enum (single source-of-truth + import re-exports)
- [ ] **1.2**. Extend `grammar_patterns.baml` with 9-value `IrishMutation` enum + wire into `ExtractCelticGrammar`
- [ ] **1.3**. Harden `caighdean_standardize.py` (wikitext extraction + TN6 stripping + Teanglann audio link capture) + ship `baml_src/celtic/standardize.baml`
- [ ] **1.4**. Wire `ireland_lc_stage.baml` to call `StandardizeIrish` pre-extraction; record `dialect_variants`
- [ ] **1.5**. Wire `ireland_jc_stage.baml` equivalent for JC Gaeilge (T1/T2)
- [ ] **1.6**. Build `gaeilge_embedding.py` v1 conformance App (caighdean post-processor + LanceDB)
- [ ] **1.7**. Create 5 DLT sources for NCCA syllabus (lc_gaeilge_ol, lc_gaeilge_hl, jc_gaeilge_t1, jc_gaeilge_t2, primary_gaeilge)
- [ ] **1.8**. Dagster assets for 5 new sources (15 assets in `gaeilge_assets.py`)
- [ ] **1.9**. MotherDuck Dive `gaeilge_full_curriculum_dive.py` + marimo `36_gaeilge_full_curriculum.py`
- [ ] **1.10**. Wholesale-copy ciancheiltis `teanga_registry.py` + `clarin.py` + per-phase verify + archive

## Phase 2 — HuggingFace Dataset Integration (Weeks 3-4)

**Change:** `2026-09-25-irish-hf-integration-v1`

- [ ] **2.1**. LC datasets: ReliableAI Irish (Belebele, BLIMP, AIME, irish_fineweb_edu) via `huggingface_factory.py`
- [ ] **2.2**. JC datasets: ReliableAI eval (IrishQA, retrieval_data) + BritLLM (truthfulqa_irish, arc_irish, piqa_irish)
- [ ] **2.3**. Speech: ymoslem Living-Audio-Irish + Wikimedia-Speech-Irish + Tatoeba + EUbookshop (5 audio)
- [ ] **2.4**. Parallel: c123ian Irish_English_Translation + DPO + CK0607 IRISH-ENGLISH-ALPACA + FrancophonIA NTEU_French-Irish + JerrySweeney
- [ ] **2.5**. Eval: britllm + seamusl/gaHealth + tktung irish_grammar_test + irish_magpie_filtered
- [ ] **2.6**. CocoIndex: `hf_irish_pretrain.py` (UCCIX + alpaca_irish_taco + jmcinern + johndennehy101)
- [ ] **2.7**. DLT: wholesale-copy ciancheiltis `huggingface_factory.py` + extend with 3 Celtic-language sources (irish_{pretrain,eval,parallel})
- [ ] **2.8**. Dagster: `hf_datasets/irish_hf_assets.py` (3 sources × 3 assets = 9 assets)
- [ ] **2.9**. MotherDuck Dive `irish_hf_datasets_dive.py` + marimo `37_irish_hf_datasets_dashboard.py`
- [ ] **2.10**. Per-phase verify + archive

## Phase 3 — CLARIN-UK + Institutional Sources (Weeks 5-6)

**Change:** `2026-09-25-clarin-uk-institutional-v1`

> **NOTE**: Stages 3.1, 3.3, 3.4, 3.6 depend on the 5 CLARIN access requests filed at Action 0.3 (4-week lead time). For the public subset (CLARIN VLO + Gaois public APIs), we ship without institutional access.

- [ ] **3.1**. LC: integrate Corpas Náisiúnta na Gaeilge (100M words) via ciancheiltis `dlt_sources/language/clarin.py` (wholesale) + write `dlt_sources/language/cng.py` adapter
- [ ] **3.2**. JC: integrate NCCA syllabus + curriculumonline.ie + gov.ie JC prescribed material (BAML `ExtractCurriculumSyllabus`)
- [ ] **3.3**. Dictionaries: integrate teanglann.ie + focloir.ie + Nua-Chorpas na hÉireann (3 DLT sources)
- [ ] **3.4**. Placenames: integrate Logainm.ie + Ainm.ie (strengthen existing `baml_src/celtic/gaois/`)
- [ ] **3.5**. Folklore: integrate Dúchas Schools' Collection + Heritage Sites + Hidden Heritages (strengthen)
- [ ] **3.6**. Dialect: integrate Canúint.ie + ABAIR TTS/ASR + Royal Irish Academy Corpas (historical 1600-1926) — RIA needs access request
- [ ] **3.7**. CocoIndex: `celtic/institutional_embedding.py` App (Corpas Náisiúnta + NCCA + dictionaries cross-source RAG)
- [ ] **3.8**. DLT: 6 institutional sources (3 new: cng/ria_corpas; 3 strengthen: teanglann/focloir/duchas/canuint)
- [ ] **3.9**. Dagster: 12 assets in `institutional/gaelic_institutional_assets.py` (2 per source × 6 sources)
- [ ] **3.10**. Per-phase verify + archive

## Phase 4 — Welsh + Manx + Celtic Siblings (Weeks 7-8)

**Change:** `2026-09-25-celtic-hf-vernacular-v1`

- [ ] **4.1**. Welsh HF: techiaith banc-trawsgrifiadau-bangor + Common Voice 18 + BU-TTS + YouTube-Subtitles (4 ASR/TTS)
- [ ] **4.2**. Welsh eval: techiaith mgsm_cy + COPA-cy + wnli-cy + macsen_intent_parsing + UniversalCEFR learn_welsh_cy
- [ ] **4.3**. Welsh CEFR + institutions: cardiffnlp/welsh-cefr + BethanAmy123 CEFR variants + CorCenCC + Bangor Siarad + Welsh Government parallel
- [ ] **4.4**. Welsh parallel: 10 techiaith + locailabs datasets
- [ ] **4.5**. Manx + cross-Celtic: k-mktr manx_gaelic_nt_gv + manxaneletso + Jendersen welsh-breton-cornish-filtered-n-readied + JayJayThrowThrow celtic-wiki-mix
- [ ] **4.6**. Cornish + Breton: CK0607 CORNISH2ENGLISH-ALPACA + Jendersen cornish_english_translation + Mozilla CV Cornish 27.0 + Bretagne Banque_Sonore_Dialectes_Bretons + Bretagne audio-breton-corpus + Bretagne PDF_en_breton + Bretagne fineweb-2_raw_breton + Bretagne archive_sonores_en_breton_1..30 + mozilla-foundation CV 17.0 br
- [ ] **4.7**. CocoIndex: strengthen `welsh_embedding.py` + `manx_embedding.py` + add `celtic_wiki_mix_embedding.py`
- [ ] **4.8**. DLT: 7 new sources (welsh_hf, welsh_cefr, welsh_parallel, manx_hf, cornish_hf, breton_hf, cross_celtic)
- [ ] **4.9**. Dagster: 21 assets in `vernacular/hf_vernacular_assets.py` (3 per source × 7 sources)
- [ ] **4.10**. Per-phase verify + archive

## Phase 5 — Indexing + Verification (Weeks 9-10)

**Change:** `2026-09-25-celtic-pipeline-finalization-v1` (this umbrella change)

- [ ] **5.1**. CI gate: `openspec validate --strict` on all 5 sister mirror changes + the 4 phase changes
- [ ] **5.2**. CI gate: `mise run sync:all` (the 14-layer orchestrator)
- [ ] **5.3**. CI gate: `bash scripts/verify.sh` across all 6 repos (cianfhoghlaim + 5 sisters)
- [ ] **5.4**. Sister integration audit: ciancheiltis carry-over (CLARIN + HF + Gaois)
- [ ] **5.5**. Sister integration audit: gemini_hackathon carry-over (29 BAML functions + sister-shared invariants)
- [ ] **5.6**. Sister integration audit: cianchosaint + ciandlithe + tuatha + bonneagar (wholesale-copy invariants)
- [ ] **5.7**. End-to-end smoke test: `tests/integration/test_full_celtic_pipeline.py` (full Celtic pipeline smoke)
- [ ] **5.8**. Indexing coverage report: `notebooks/38_celtic_indexing_coverage.py` (per-language + per-surface)
- [ ] **5.9**. Documentation: `openspec/specs/celtic-language-pipeline/spec.md` (the umbrella spec, 6 Requirements)
- [ ] **5.10**. Final: archive all 5 phase changes + trigger Cloud Run redeploy + budget alert check + session report

## Per-stage verification gates (×50)

After each stage:
```bash
ruff check . && ruff format --check .
baml-cli generate  # if BAML touched
uv run pytest tests/<surface> -v
git add -A && git commit -m "<stage message>"
```

## Per-phase verification gates (×5)

After each phase:
```bash
bash scripts/verify.sh                              # 8/8 ticks
mise run sync:all                                   # 14-layer orchestrator
mise run lint:registry                             # 0 hardcoded model strings
openspec validate --strict                          # valid
gcloud billing budgets list                         # verify £300 alert
uv run python scripts/sister_lifts.py verify        # all wholesale-copies have provenance
openspec archive <phase-change> -y --skip-specs     # archive
git push origin main                                # push
```

