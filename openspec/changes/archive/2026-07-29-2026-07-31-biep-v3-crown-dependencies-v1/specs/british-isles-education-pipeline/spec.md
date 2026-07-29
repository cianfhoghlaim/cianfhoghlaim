## ADDED Requirements

### Requirement: All 8 British Isles jurisdictions are covered (BIEP v3 complete)

The system SHALL provide a generic Crown Dependencies DLT pipeline
(`dlt/british_isles/crown_dependencies/education/crown_dependencies_jurisdiction_pipeline.py`)
that handles the 3 Crown Dependencies (Jersey + Guernsey + Isle of Man).

This completes the BIEP v3 rollout: **all 8 British Isles
jurisdictions** are now covered by generic jurisdiction pipelines
driven by the canonical British Isles subject registry.

Coverage summary:

| Jurisdiction | Awarding body | Cohorts |
|---|---|---|
| Ireland (NCCA + SEC) | NCCA + SEC | 384 LC + 108 JC + 16 short courses + 36 CBAs = 544 |
| England (AQA + OCR + Edexcel) | 3 boards | 43 GCSE × 3 + 49 A-Level × 3 = 276 |
| Scotland (SQA) | SQA | 50 × 3 = 150 |
| Wales (WJEC) | WJEC | 80 × 2 = 160 |
| Northern Ireland (CCEA) | CCEA | 35 × 2 = 70 |
| Jersey | States of Jersey | 30 × 4 = 120 |
| Guernsey | States of Guernsey | 30 × 4 = 120 |
| Isle of Man | Isle of Man DESC | 30 × 4 = 120 |
| **TOTAL** | | **~1,560** |

#### Scenario: 8 jurisdictions all have non-zero registry counts

- **WHEN** `seed_registry()` is run
- **THEN** every one of the 8 British Isles jurisdictions has ≥90 rows
  in `cianfhoghlaim.education._registry.subjects`
- **AND** the companion notebook Tab 2 (Nation comparison) shows
  non-zero row counts for all 8

#### Scenario: BIEP v3 8-jurisdiction pipeline infrastructure is complete

- **WHEN** `dg list assets | grep -E "(ireland_|england_|sct_wls_ni_|crown_dependencies_)"` runs
- **THEN** 16 generic assets are listed (8 jurisdictions × 2 assets each
  in 2 of the 3 layers: ingestion + extraction — the embedding layer
  is shared across jurisdictions)
- **AND** zero per-jurisdiction per-subject per-board assets exist