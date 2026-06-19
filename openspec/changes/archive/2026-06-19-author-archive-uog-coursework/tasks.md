# Author-Archive v1: UoG Coursework Implementation Tasks

## Stage 2 — UoG coursework (this change)

### 2.0 BAML extension (DONE)

- [x] Add 5 new BAML functions to `baml_src/author_archive.baml`
      (ExtractUoGMathModule, ExtractUoGSoftwareModule,
      ExtractUoGIrishModule, ExtractUoGEducationModule,
      ExtractPersonalRecord)
- [x] Add 3 new types (UoGSubject, UoGDocumentKind,
      UoGModuleExtraction)
- [x] 5 golden-sample test cases in the BAML file
- [x] `baml-cli generate` succeeds (45 new entries in
      `baml_client/sync_client.py`)

### 2.1 DLT sources (DONE)

- [x] `oideachais/dlt_sources/author_archive/olscoil_mata.py` —
      mata/ (Mathematics / Statistics / Cryptography)
- [x] `oideachais/dlt_sources/author_archive/olscoil_software.py` —
      software_development/ (CT511/CT545/CT853/CT861/CT870)
- [x] `oideachais/dlt_sources/author_archive/olscoil_irish.py` —
      irish/ (Gaeilge essays, translations, reviews)
- [x] `oideachais/dlt_sources/author_archive/olscoil_education.py` —
      education/ (B.Ed / PGCE / BME)
- [x] `oideachais/dlt_sources/author_archive/personal_records.py` —
      `cian_mac_an_déisigh_uí_liatháin/{achievement,teaching}/`
      with `identity/` excluded by default

### 2.2 Dagster assets (DONE)

- [x] Create
      `oideachais/dagster_defs/assets/official_media/uog_coursework_assets.py`
      with 10 new assets (5 modules × 2 resources each)
- [x] Register in `oideachais/dagster_defs/assets/official_media/__init__.py`
- [x] Register in `oideachais/dagster_defs/assets/__init__.py` `all_assets`

### 2.3 OpenSpec change (DONE — this commit)

- [x] Create
      `openspec/changes/author-archive-uog-coursework/` with
      proposal + tasks + 1 spec delta
- [ ] `openspec validate author-archive-uog-coursework --strict`

### 2.4 Tests (TODO)

- [ ] `oideachais/tests/test_uog_coursework_assets.py` covering
      asset registration, sample sources, and the personal_records
      identity exclusion guard

## Stage 3 — Cross-corpus knowledge graph (deferred)

Independent of the coursework layer. Will land in
`author-archive-v3` after the UoG and Gemini corpora are flowing.

## Stage 4 — Multi-target deployment (deferred)

`oideachais/dlt_utils/target_factory.py` + 3 targets (dev=DuckDB,
staging=MotherDuck, prod=Garage S3 + Lakekeeper) + `make_target.sh`.

## Validation

```bash
# 1. Validate OpenSpec change
openspec validate author-archive-uog-coursework --strict

# 2. Run the BAML tests (the 5 new test cases)
cd oideachais && baml-cli generate

# 3. Run the asset tests
cd oideachais
pytest tests/test_uog_coursework_assets.py -v

# 4. Smoke-test the DLT sources locally
cd oideachais
python -c "
from dlt_sources.author_archive.olscoil_mata import mata_source
for r in list(mata_source(max_files=3).mata_documents)[:3]:
    print(r)
"
```

## Push status

This branch is **blocked by GitHub Push Protection** on a pre-existing
Cloudflare User API Token in `92de91dd6` (the ancestor of this
branch). The user must rotate the token (it's a real token, not a
false positive) and rebase the branch.
