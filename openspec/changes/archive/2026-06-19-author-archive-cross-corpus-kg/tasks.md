# Author-Archive Cross-Corpus Knowledge Graph: Implementation Tasks

## Stage 3 — Cross-corpus KG (this change)

### 3.0 Cognee helper (DONE)

- [x] Create
      `oideachais/cognee_integration/author_archive_cognify.py`
      with `cognify_author_archive_rows()` and `cognify_all_corpora()`
- [x] Define `DATASET_NAME = "oideachais_author_archive"` and
      `EDGE_TYPES` (the 8 edge types)
- [x] Stub-mode behaviour (no-op when `USE_LOCAL_SCRAPES=true`)

### 3.1 Cross-corpus edge rules (DONE)

- [x] Create
      `oideachais/cognify_rules/author_archive_cross_corpus.py`
- [x] 5 deterministic rules:
      1. OfficialMediaSource-[:PUBLISHES]->ZoteroPaper
      2. OfficialMediaSource-[:DISCUSSES]->UoGArtifact
      3. PersonalRecord-[:AWARDED]->UoGArtifact
      4. UoGArtifact-[:LOCATED_IN]->OfficialMediaSource
      5. PersonalRecord-[:AFFILIATED_WITH]->OfficialMediaSource
- [x] `populate_cross_corpus_edges()` runs all 5 rules + returns
      a summary

### 3.2 Dagster assets (DONE)

- [x] Create
      `oideachais/dagster_defs/assets/official_media/author_archive_kg_assets.py`
      with 3 assets:
      - `author_archive_cognify` (compute_kind="cognee")
      - `author_archive_cross_edges` (compute_kind="falkordb")
      - `author_archive_kg_summary` (writes
        `oideachais/official_media/kg_summary.json`)
- [x] Register in
      `oideachais/dagster_defs/assets/official_media/__init__.py`
- [x] Register in
      `oideachais/dagster_defs/assets/__init__.py` `all_assets`

### 3.3 Marimo unified dashboard (DONE)

- [x] Create
      `oideachais/notebooks/dashboards/author_archive/unified_dashboard.py`
      with 4 tabs:
      - Source provenance (Stage 1)
      - UoG coursework (Stage 2)
      - Cross-corpus knowledge graph (Stage 3)
      - Credit usage (Stage 0.5)
- [x] Strong-stance footer card (non-dismissible)

### 3.4 OpenSpec change (DONE — this commit)

- [x] Create
      `openspec/changes/author-archive-cross-corpus-kg/` with
      proposal + tasks + 1 spec delta
- [ ] `openspec validate author-archive-cross-corpus-kg --strict`

### 3.5 Tests (TODO)

- [ ] `oideachais/tests/test_author_archive_cognify.py` covering the
      8 edge types, the 5 rules, and the asset registration

## Stage 4 — Multi-target deployment (deferred)

`oideachais/dlt_utils/target_factory.py` + 3 targets (dev=DuckDB,
staging=MotherDuck, prod=Garage S3 + Lakekeeper) + `make_target.sh`.

## Validation

```bash
# 1. Validate OpenSpec change
openspec validate author-archive-cross-corpus-kg --strict

# 2. Run the cognify tests
cd oideachais
pytest tests/test_author_archive_cognify.py -v

# 3. Smoke-test the cross-corpus rule builder
python -c "
from oideachais.cognify_rules.author_archive_cross_corpus import (
    build_all_cross_corpus_queries,
)
queries = build_all_cross_corpus_queries(
    official_media_sources=[
        {'source_id': 'cps_gov_uk', 'url': 'https://www.cps.gov.uk',
         'site_structure_summary': 'Crown Prosecution Service - legal guidance',
         'primary_content_types': ['legal_guidance']},
    ],
    zotero_papers=[
        {'file_hash': 'abc123', 'title': 'CPS legal guidance on sexual offences',
         'arxiv_id': '2402.02890'},
    ],
    uog_modules=[],
    personal_records=[],
)
print(f'Built {len(queries)} queries:')
for name, cypher, params in queries:
    print(f'  {name}: {len(params.get(\"edges\", []))} edges')
"
```

## Push status

This branch is **blocked by GitHub Push Protection** on a pre-existing
Cloudflare DNS API Token in `92de91dd6` (the ancestor of this
branch). The user must rotate the token (it's a real token, not a
false positive) and rebase the branch.
