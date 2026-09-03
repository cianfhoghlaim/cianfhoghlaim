# Tasks: 2026-07-15-eu-multilingual-irish-english-v1

## 1. OpenSpec scaffolding

- [ ] 1.1 Create `openspec/changes/2026-07-15-eu-multilingual-irish-english-v1/`
- [ ] 1.2 Write `proposal.md` + `tasks.md` + spec deltas
- [ ] 1.3 `openspec validate 2026-07-15-eu-multilingual-irish-english-v1 --strict` passes

## 2. BAML updates

- [ ] 2.1 Add `BilingualTextEnGa` class to `baml/european_union/_shared/eu_document.baml`
- [ ] 2.2 Add `EUExtractableBilingualDocument` class
- [ ] 2.3 Add `ExtractEUDocumentBilingualEnGa` function

## 3. Per-source `language_availability` metadata

For each of the 12 EU institutional DLT sources (in
`dlt/european_union/`):
- `eur_lex/regulations.py`
- `eur_lex/directives.py`
- `eur_lex/decisions.py`
- `eur_lex/treaties.py`
- `eur_lex/cjeu_case_law.py`
- `education/eurydice.py`
- `education/cedefop.py`
- `education/school_education_gateway.py`
- `medicine/ema_medicines_register.py`
- `medicine/ecdc_surveillance.py`
- `statistics/eurostat.py`
- `publications_office/eu_publications.py`

Add the `language_availability` metadata field to each source's
`extra_metadata`.

## 4. Dagster L2 assets

- [ ] 4.1 Create `orchestration/defs/2_materials/eu_multilingual/__init__.py`
- [ ] 4.2 Create `english_coverage_monitor.py` (cron `0 5 * * *`)
- [ ] 4.3 Create `irish_coverage_monitor.py` (cron `0 5 * * *`)
- [ ] 4.4 Create `language_alignment_mapper.py` (cron `0 5 * * *`)
- [ ] 4.5 Create `defs.yaml` (3 L2 assets grouped)

## 5. CocoIndex v1 App

- [ ] 5.1 Create
  `cocoindex/eu_multilingual_alignment_embedding.py`
- [ ] 5.2 Imports `from ._lifespan import shared_lifespan`
- [ ] 5.3 Embeds with `BAAI/bge-m3` 1024-d
- [ ] 5.4 Partitions on `(institution, language)`
- [ ] 5.5 Create the corresponding L3 defs

## 6. MotherDuck Dive + Flight

- [ ] 6.1 Create
  `motherduck/dives/eu_multilingual_coverage.py`
- [ ] 6.2 Create
  `motherduck/flights/eu_multilingual_daily_sync_flight.py`
- [ ] 6.3 Append the flight to
  `motherduck/flights/config.yaml` (cron `0 5 * * *`)

## 7. Cache fixtures

For each of the 12 institutional sources, create `en` + `ga` cache
fixtures under `stedding/ingest_queue/eu/<institution>/<lang>/sample.json`
(24 fixtures total).

## 8. Spec deltas

- [ ] 8.1 MODIFIED delta on `european-union-official-language-pipeline/spec.md`
  declaring the BilingualTextEnGa extraction + language_availability metadata
- [ ] 8.2 MODIFIED delta on `cross-region-pipeline/spec.md` cross-referencing
- [ ] 8.3 MODIFIED delta on `cianfhoghlaim-pipeline/spec.md` cross-referencing

## 9. Validate

- [ ] 9.1 `openspec validate 2026-07-15-eu-multilingual-irish-english-v1 --strict` passes
- [ ] 9.2 All Python files AST-parse
- [ ] 9.3 All Dagster defs YAML-parse
- [ ] 9.4 All BAML files parse
- [ ] 9.5 `dg check yaml` passes
- [ ] 9.6 `mise run lint:skills` still passes (53/53)

## 10. Commit + push

- [ ] 10.1 Single commit with message
  `feat(eu-multilingual): bilingual English + Irish BAML extraction + coverage monitors + alignment mapping (later Ireland / NI alignment)`
- [ ] 10.2 `git push origin pick-4-biep-v1`
