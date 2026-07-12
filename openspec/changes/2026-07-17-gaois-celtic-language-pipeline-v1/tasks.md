# Tasks — Gaois + Celtic Language Pipeline v1

## 1. OpenSpec change skeleton (30 min)

- [x] `openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/proposal.md` (this file)
- [x] `tasks.md`
- [x] `specs/celtic-language-pipeline/spec.md` (new umbrella spec — 7 Requirements + 7 Scenarios)
- [x] MODIFIED delta on `oideachais-pipeline/spec.md` (cross-reference)
- [x] MODIFIED delta on `british-isles-education-pipeline/spec.md` (cross-reference)

## 2. Phase 2 — Fill the 6 BAML extraction gaps (3-5 hours)

### 2.1 Dúchas BAML functions (new file additions to `baml/celtic/gaois/duchas.baml`)

- [ ] `function ExtractDuchasManuscript(xml_record: string) -> DuchasManuscriptRecord`
- [ ] `function ExtractDuchasImageBoundingBox(image_path: string, transcript: string) -> DuchasBoundingBox[]`
- [ ] `function ExtractDuchasTranscription(handwritten_image: string) -> DuchasTranscriptionLine[]`

### 2.2 Celtic curriculum BAML function (new addition to `baml/celtic/curriculum/celtic_curriculum.baml`)

- [ ] `function ExtractCelticCurriculum(text: string, language: CelticLanguageCurriculum) -> CelticCurriculumSpec`

### 2.3 Re-activate `baml/celtic/grammar_patterns.baml` + add consumer

- [ ] Move `baml/celtic/_archive/grammar_patterns.baml` → `baml/celtic/grammar_patterns.baml`
- [ ] Remove ARCHIVED header
- [ ] `function ExtractCelticGrammar(text: string, language: CelticLanguageCurriculum) -> CelticGrammarPattern[]`
- [ ] New consumer: `meaisinfhoghlaim/agents/celtic_grammar.py`

### 2.4 Re-activate `baml/celtic/morphology.baml` + add consumer

- [ ] Move `baml/celtic/_archive/morphology.baml` → `baml/celtic/morphology.baml`
- [ ] Remove ARCHIVED header
- [ ] `function ExtractCelticMorphology(text: string, language: CelticLanguageCurriculum) -> CelticMorphologySpec`
- [ ] New consumer: `meaisinfhoghlaim/agents/celtic_morphology.py`

### 2.5 Verify BAML compiles

- [ ] `mise run baml:generate` shows 0 errors (no new BAML parse errors)

## 3. Phase 3 — 7 new CocoIndex v1 Apps (R1-R4 conformant, 14 hours)

For each of the 7 source groups, create the CocoIndex App + the 4 wrapper files:

### 3.1 Gaois APIs — `cocoindex/gaois_embedding.py` + 4 wrappers

- [ ] `cocoindex/gaois_embedding.py` — CocoIndex v1 App (R1-R4 conformant) for gaois terminology
- [ ] `cocoindex/gaois_embedding/_lifespan.py` — App-specific lifespan
- [ ] `cocoindex/gaois_embedding/_assets.py` — Dagster assets wrapper
- [ ] `cocoindex/gaois_embedding/__init__.py` — package init
- [ ] `cocoindex/gaois_embedding/test_smoke.py` — smoke test

### 3.2 Dúchas — `cocoindex/duchas_embedding.py` + 4 wrappers (with bbox)

- [ ] `cocoindex/duchas_embedding.py` — CocoIndex v1 App with bbox alignment
- [ ] `cocoindex/duchas_embedding/_lifespan.py`
- [ ] `cocoindex/duchas_embedding/_assets.py`
- [ ] `cocoindex/duchas_embedding/__init__.py`
- [ ] `cocoindex/duchas_embedding/test_smoke.py`

### 3.3 Heritage — `cocoindex/heritage_embedding.py` + 4 wrappers

- [ ] `cocoindex/heritage_embedding.py`
- [ ] `cocoindex/heritage_embedding/_lifespan.py`
- [ ] `cocoindex/heritage_embedding/_assets.py`
- [ ] `cocoindex/heritage_embedding/__init__.py`
- [ ] `cocoindex/heritage_embedding/test_smoke.py`

### 3.4 Canuint — `cocoindex/canuint_embedding.py` + 4 wrappers

- [ ] `cocoindex/canuint_embedding.py`
- [ ] `cocoindex/canuint_embedding/_lifespan.py`
- [ ] `cocoindex/canuint_embedding/_assets.py`
- [ ] `cocoindex/canuint_embedding/__init__.py`
- [ ] `cocoindex/canuint_embedding/test_smoke.py`

### 3.5 Universal Dependencies Celtic — `cocoindex/ud_celtic_embedding.py` + 4 wrappers

- [ ] `cocoindex/ud_celtic_embedding.py`
- [ ] `cocoindex/ud_celtic_embedding/_lifespan.py`
- [ ] `cocoindex/ud_celtic_embedding/_assets.py`
- [ ] `cocoindex/ud_celtic_embedding/__init__.py`
- [ ] `cocoindex/ud_celtic_embedding/test_smoke.py`

### 3.6 Local documents by subject — `cocoindex/local_documents_embedding.py` + 4 wrappers

- [ ] `cocoindex/local_documents_embedding.py`
- [ ] `cocoindex/local_documents_embedding/_lifespan.py`
- [ ] `cocoindex/local_documents_embedding/_assets.py`
- [ ] `cocoindex/local_documents_embedding/__init__.py`
- [ ] `cocoindex/local_documents_embedding/test_smoke.py`

### 3.7 Celtic curriculum — `cocoindex/celtic_curriculum_embedding.py` + 4 wrappers

- [ ] `cocoindex/celtic_curriculum_embedding.py`
- [ ] `cocoindex/celtic_curriculum_embedding/_lifespan.py`
- [ ] `cocoindex/celtic_curriculum_embedding/_assets.py`
- [ ] `cocoindex/celtic_curriculum_embedding/__init__.py`
- [ ] `cocoindex/celtic_curriculum_embedding/test_smoke.py`

### 3.8 Shared LlamaSwap routing module

- [ ] `meaisinfhoghlaim/models/routing.py` — shared per-language + per-source routing table

### 3.9 Verify R1-R4 conformance

- [ ] `cocoindex_v1_conformance` App passes for all 7 new CocoIndex v1 Apps

## 4. Phase 4 — 21 new Dagster defs (7 groups × 3 layers, 7 hours)

For each of the 7 source groups:

### 4.1 Gaois group

- [ ] `orchestration/defs/1_ingestion/language/gaois/defs.yaml` — daily 04:00 UTC cron
- [ ] `orchestration/defs/2_materials/baml_extraction/language/gaois/_assets.py`
- [ ] `orchestration/defs/3_model_lifecycle/cocoindex_v1/gaois_embedding/defs.yaml`

### 4.2 Dúchas group

- [ ] `orchestration/defs/1_ingestion/language/duchas/defs.yaml` — daily 03:00 UTC cron
- [ ] `orchestration/defs/2_materials/baml_extraction/language/duchas/_assets.py`
- [ ] `orchestration/defs/3_model_lifecycle/cocoindex_v1/duchas_embedding/defs.yaml`

### 4.3 Heritage group

- [ ] `orchestration/defs/1_ingestion/language/heritage/defs.yaml` — weekly cron
- [ ] `orchestration/defs/2_materials/baml_extraction/language/heritage/_assets.py`
- [ ] `orchestration/defs/3_model_lifecycle/cocoindex_v1/heritage_embedding/defs.yaml`

### 4.4 Canuint group

- [ ] `orchestration/defs/1_ingestion/language/canuint/defs.yaml` — monthly cron
- [ ] `orchestration/defs/2_materials/baml_extraction/language/canuint/_assets.py`
- [ ] `orchestration/defs/3_model_lifecycle/cocoindex_v1/canuint_embedding/defs.yaml`

### 4.5 Universal Dependencies Celtic group

- [ ] `orchestration/defs/1_ingestion/language/ud_celtic/defs.yaml` — quarterly cron
- [ ] `orchestration/defs/2_materials/baml_extraction/language/ud_celtic/_assets.py`
- [ ] `orchestration/defs/3_model_lifecycle/cocoindex_v1/ud_celtic_embedding/defs.yaml`

### 4.6 Local documents group

- [ ] `orchestration/defs/1_ingestion/language/local_documents/defs.yaml` — on-demand
- [ ] `orchestration/defs/2_materials/baml_extraction/language/local_documents/_assets.py`
- [ ] `orchestration/defs/3_model_lifecycle/cocoindex_v1/local_documents_embedding/defs.yaml`

### 4.7 Celtic curriculum group

- [ ] `orchestration/defs/1_ingestion/language/celtic_curriculum/defs.yaml` — monthly cron
- [ ] `orchestration/defs/2_materials/baml_extraction/language/celtic_curriculum/_assets.py`
- [ ] `orchestration/defs/3_model_lifecycle/cocoindex_v1/celtic_curriculum_embedding/defs.yaml`

### 4.8 Verify Dagster defs

- [ ] `dg check yaml` passes on all 21 new `defs.yaml` files

## 5. Phase 5 — 7 MotherDuck Dives + 7 marimo notebooks (10 hours)

For each of the 7 source groups:

### 5.1 Gaois group

- [ ] `motherduck/dives/gaois_terminology_dive.py` — Téarma + Logainm + Ainm coverage
- [ ] `notebooks/16_celtic_language/01_gaois_terminology_explorer.py` — marimo

### 5.2 Dúchas group

- [ ] `motherduck/dives/duchas_folklore_dive.py` — page-level summaries (not 74M row word-level)
- [ ] `notebooks/16_celtic_language/02_duchas_folklore_with_bboxes.py` — Altair bbox visualization

### 5.3 Heritage group

- [ ] `motherduck/dives/heritage_sites_dive.py` — heritage + hidden heritages
- [ ] `notebooks/16_celtic_language/03_heritage_sites_map.py` — marimo

### 5.4 Canuint group

- [ ] `motherduck/dives/canuint_dialect_dive.py` — pronunciation + word alignment
- [ ] `notebooks/16_celtic_language/04_canuint_dialect_player.py` — marimo

### 5.5 Universal Dependencies Celtic group

- [ ] `motherduck/dives/ud_celtic_dive.py` — Celtic treebank coverage
- [ ] `notebooks/16_celtic_language/05_ud_celtic_treebank_viewer.py` — marimo

### 5.6 Local documents group

- [ ] `motherduck/dives/local_documents_dive.py` — per-subject PDF coverage
- [ ] `notebooks/16_celtic_language/06_local_documents_subject_viewer.py` — marimo

### 5.7 Celtic curriculum group

- [ ] `motherduck/dives/celtic_curriculum_dive.py` — Celtic-language curriculum coverage
- [ ] `notebooks/16_celtic_language/07_celtic_curriculum_browser.py` — marimo

### 5.8 Verify marimo notebooks

- [ ] Each notebook runs via `marimo edit` and `uv run`
- [ ] Each notebook connects to `md:oideachais` via `nb_utils.connect_biep_lakehouse()`

## 6. Validate (30 min)

- [ ] `openspec validate 2026-07-17-gaois-celtic-language-pipeline-v1 --strict` passes
- [ ] `dg check yaml` passes on all new `defs.yaml` files
- [ ] `mise run lint:skills` still passes
- [ ] `mise run baml:generate` shows 0 new errors

## 7. Commit + push (5 min)

- [ ] Single commit with message
  `feat(celtic): Gaois + Celtic language pipeline v1 (7 source groups × 5 layers)`
- [ ] Push to `origin/pick-4-biep-v1`