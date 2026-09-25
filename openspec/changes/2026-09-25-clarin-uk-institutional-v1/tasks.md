# Tasks: CLARIN-UK + Institutional Sources Integration (Phase 3)

## Stage 3.1 — LC: Corpas Náisiúnta na Gaeilge (100M words)

- [ ] 3.1.1. Wholesale-copy ciancheiltis `dlt_sources/language/clarin.py` → cianfhoghlaim `dlt_sources/language/clarin.py` (via `scripts/sister_lifts.py add`)
- [ ] 3.1.2. Verify: `uv run python -c "from dlt_sources.language.clarin import ClarinVLOClient; c = ClarinVLOClient(); print(c.search('gaeilge', limit=5))"`
- [ ] 3.1.3. New: `dlt_sources/language/cng.py` (Corpas Náisiúnta adapter — uses `requests` + the corpus URL once access granted)
- [ ] 3.1.4. New: `dlt_sources/language/cng_helpers.py` (parse NIF XML, lemmatization, POS tagging)

## Stage 3.2 — JC: NCCA + curriculumonline + gov.ie

- [ ] 3.2.1. New: `dlt_sources/education/ireland/british_isles/jc_gaeilge_syllabus.py` (NCCA JC Gaeilge T1/T2 syllabi)
- [ ] 3.2.2. New: `dlt_sources/education/ireland/british_isles/jc_gaeilge_curriculumonline.py` (curriculumonline.ie)
- [ ] 3.2.3. New: `dlt_sources/education/ireland/british_isles/jc_gaeilge_gov.py` (gov.ie JC prescribed material)
- [ ] 3.2.4. Verify: smoke import of all 3

## Stage 3.3 — Dictionaries: teanglann + focloir + Nua-Chorpas

- [ ] 3.3.1. New: `dlt_sources/language/dictionaries/__init__.py`
- [ ] 3.3.2. New: `dlt_sources/language/dictionaries/teanglann.py` (teanglann.ie lookup API)
- [ ] 3.3.3. New: `dlt_sources/language/dictionaries/focloir.py` (focloir.ie + Nua-Chorpas)
- [ ] 3.3.4. Verify: smoke imports + a 1-query live fetch

## Stage 3.4 — Placenames: Logainm + Ainm

- [ ] 3.4.1. Strengthen existing `baml_src/celtic/gaois/logainm.baml` (already has 32 county codes + LogainmPlace class)
- [ ] 3.4.2. New: `dlt_sources/language/placenames/logainm.py` (DLT source over the Logainm API)
- [ ] 3.4.3. Strengthen existing `baml_src/celtic/gaois/tearma.baml` — add `AinmPerson` BAML extractor
- [ ] 3.4.4. New: `dlt_sources/language/placenames/ainm.py`

## Stage 3.5 — Folklore: Dúchas + Heritage + Hidden Heritages

- [ ] 3.5.1. Strengthen existing `dlt_sources/cultural_heritage/duchas.py` + `_duchas_images_helpers.py` + `duchas_images.py`
- [ ] 3.5.2. Strengthen existing `dlt_sources/cultural_heritage/heritage.py`
- [ ] 3.5.3. Strengthen existing `dlt_sources/cultural_heritage/hidden_heritages.py` + `hidden_heritages_extended.py`

## Stage 3.6 — Dialect: Canúint + ABAIR + RIA Corpas

- [ ] 3.6.1. Strengthen existing `dlt_sources/lexicographic/canuint.py` + 5 sibling files
- [ ] 3.6.2. New: `dlt_sources/language/dialect/abair.py` (Trinity College Dublin TTS/ASR)
- [ ] 3.6.3. New: `dlt_sources/language/dialect/ria_corpas.py` (Royal Irish Academy historical 1600-1926)
- [ ] 3.6.4. New: `baml_src/celtic/_shared/historical_extract.baml` with `ExtractRIAEntry` + `ExtractDuchasManuscript`

## Stage 3.7 — CocoIndex: institutional_embedding

- [ ] 3.7.1. New: `cocoindex_flows/celtic/institutional_embedding.py` (embeds Corpas Náisiúnta + NCCA + dictionaries cross-source RAG into LanceDB `cianhoghlaim.celtic.institutional.{cng, ncca, dictionaries, placenames}_chunks`)

## Stage 3.8 — DLT consolidation

- [ ] 3.8.1. Register all 6 institutional sources (`cng`, `ria_corpas`, `abair`, `teanglann`, `focloir`, `duchas_corpus`) to `dlt_sources/language/__init__.py`

## Stage 3.9 — Dagster

- [ ] 3.9.1. New: `orchestration/defs/2_materials/institutional/__init__.py` (aggregator)
- [ ] 3.9.2. New: `orchestration/defs/2_materials/institutional/gaelic_institutional_assets.py` (12 assets: 2 per source × 6 sources)

## Stage 3.10 — Per-phase verify + archive

- [ ] 3.10.1. `bash scripts/verify.sh` → 8/8
- [ ] 3.10.2. `mise run lint:registry` → 0 hardcoded model strings
- [ ] 3.10.3. `openspec validate --strict` → valid
- [ ] 3.10.4. `uv run pytest tests/dlt/test_clarin_loaders.py` (new test) → pass
- [ ] 3.10.5. `openspec archive 2026-09-25-clarin-uk-institutional-v1 -y --skip-specs`
- [ ] 3.10.6. `git push origin main`
