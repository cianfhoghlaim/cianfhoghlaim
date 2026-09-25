# Change: CLARIN-UK + Institutional Sources Integration (Phase 3)

## Why

This is **Phase 3** of the 5-phase × 10-stage Celtic pipeline overhaul.

Cianfhoghlaim currently has **zero direct references** to CLARIN-UK or institutional Celtic-language corpora. The ciancheiltis sister repo carries `dlt_sources/language/clarin.py` (the CLARIN Virtual Language Observatory HTTP loader) and the 5 sister spec files (`ciancheiltis-en-{ga-roi,ga-ni,gd,gv,cy,ga-eu}`) reference CLARIN via spec text but no actual code.

This phase integrates:

### Institutional corpora (require access requests filed at Action 0.3)

1. **Corpas Náisiúnta na Gaeilge** (100M words, 2000-2024, Foras na Gaeilge + DCU Gaois) — `corpas.ie`
2. **Royal Irish Academy Corpas** (historical 1600-1926) — `corpas.ria.ie`
3. **NCCA syllabus** (LC + JC + Primary) — `ncca.ie`
4. **curriculumonline.ie** (JC prescribed material) — `curriculumonline.ie`
5. **Dúchas Schools' Collection** (already partially exists; strengthen)
6. **Canúint.ie** (dialect audio corpus; already exists; strengthen)
7. **ABAIR** (TTS/ASR; Trinity College Dublin) — `abair.ie`

### Dictionaries (public APIs)

8. **teanglann.ie** (Niall Ó Dónaill dictionary + grammar) — `teanglann.ie`
9. **focloir.ie** (new English-Irish dictionary, 2025) — `focloir.ie`
10. **Nua-Chorpas na hÉireann** (English-Irish Dictionary project) — `focloir.sketchengine.eu`

### Placenames (public APIs)

11. **Logainm.ie** (Irish placenames) — already exists in `baml_src/celtic/gaois/logainm.baml`; strengthen with full DLT source
12. **Ainm.ie** (biographical gazetteer) — `ainm.ie`

### Folklore (already exists; strengthen)

13. **Dúchas Schools' Collection** (already partially exists) — strengthen
14. **Heritage Sites** (Gaeltacht + heritage locations) — strengthen
15. **Hidden Heritages** — strengthen

## What changes (10 stages)

### Stage 3.1 — LC: Corpas Náisiúnta na Gaeilge
- Wholesale-copy ciancheiltis `dlt_sources/language/clarin.py` → cianfhoghlaim `dlt_sources/language/clarin.py`
- New: `dlt_sources/language/cng.py` (Corpas Náisiúnta adapter)
- Stage is partially blocked on the 4-week access-request lead time (Action 0.3)

### Stage 3.2 — JC: NCCA syllabus + curriculumonline.ie + gov.ie JC
- New: `dlt_sources/education/ireland/british_isles/jc_gaeilge_syllabus.py` (uses BAML `ExtractCurriculumSyllabus`)
- New: `dlt_sources/education/ireland/british_isles/jc_gaeilge_curriculumonline.py`

### Stage 3.3 — Dictionaries: teanglann + focloir + Nua-Chorpas
- New: `dlt_sources/language/dictionaries/__init__.py` (3 DLT sources)

### Stage 3.4 — Placenames: Logainm + Ainm
- Strengthen existing `baml_src/celtic/gaois/{logainm,ainm}.baml` with full DLT sources

### Stage 3.5 — Folklore: Dúchas + Heritage Sites + Hidden Heritages
- Strengthen existing `dlt_sources/cultural_heritage/{duchas,heritage,hidden_heritages}.py`

### Stage 3.6 — Dialect: Canúint + ABAIR + Royal Irish Academy Corpas
- Strengthen existing `dlt_sources/lexicographic/canuint_*.py`
- New: `dlt_sources/language/dialect/abair.py` (Trinity College Dublin TTS/ASR)
- New: `dlt_sources/language/dialect/ria_corpas.py` (Royal Irish Academy, historical 1600-1926; needs access request)

### Stage 3.7 — CocoIndex: institutional_embedding.py
- New: `cocoindex_flows/celtic/institutional_embedding.py` (Corpas Náisiúnta + NCCA + dictionaries cross-source RAG)

### Stage 3.8 — DLT: 6 institutional sources registered
- 3 new: cng, ria_corpas, abair
- 3 strengthen: teanglann, focloir, duchas, canuint
- All registered to `celtic.{dictionaries, placenames, folklore, dialect}.{...}` DuckLake namespaces

### Stage 3.9 — Dagster: 12 assets
- New: `orchestration/defs/2_materials/institutional/gaelic_institutional_assets.py` (2 per source × 6 sources = 12 assets)

### Stage 3.10 — Per-phase verify + archive

## Impact

- **Affected code**: ~12 new files (3 new DLT sources + 1 wholesale-copied clarin.py + 1 strengthen file + 1 CocoIndex App + 1 Dagster asset file + 1 MotherDuck Dive + 1 marimo notebook + 1 wholesale-copied teanga_registry.py + 2 modification records)
- **Affected specs**: NEW `celtic-language-pipeline` (added by the umbrella change)

## Out of scope

- HuggingFace dataset integration (Phase 2 — already done)
- Welsh + Manx + Cornish + Breton (Phase 4)
- Tuatha sister-repo wholesale-copy (separate)
