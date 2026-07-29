## MODIFIED Requirements

### Requirement: 24-model 4-backend v4 registry

The system SHALL provide an OCR/VLM model registry at
`cianfhoghlaim/meaisinfhoghlaim/models/registry.py:VISION_MODELS`
with **26 entries** (extended from the v4 24 — adds `unstract-api` and
`docling-serve` for the BIEP v2 ensemble pipeline from Change 3).

Each entry SHALL have the 6-backend schema:
- `LITELLM`, `MLX`, `TRANSFORMERS`, `LLAMASWAP` (the v4 four), plus
- **`DOCLING`** (the IBM Docling HTTP REST API at :5001)
- **`UNSTRACT`** (the Unstract REST API at :8000)

and the 11-entry `ModelCapability` enum (extended from the v4 9 — adds
`UNISTRUCT_WORKFLOW` and `DOCLING_LAYOUT`).

#### Scenario: 26 entries registry audit (post BIEP v2)

- **WHEN** `mise run registry:lint` runs against the v5 registry (post Change 3)
- **THEN** it reports **26 model entries** with **6 backends**
- **AND** both `unstract-api` and `docling-serve` are listed with their
  full dataclass field values
- **AND** every Ireland / England / Scotland / Wales / NI / IoM / Jersey /
  Guernsey BAML function can select any of the 26 entries via
  `select_ocr_backend()`

#### Scenario: Unstract workflow + Docling layout are first-class capabilities

- **WHEN** a developer calls `registry.VISION_MODELS["unstract-api"].capabilities`
- **THEN** the result MUST include `ModelCapability.UNISTRUCT_WORKFLOW`
- **WHEN** a developer calls `registry.VISION_MODELS["docling-serve"].capabilities`
- **THEN** the result MUST include `ModelCapability.DOCLING_LAYOUT`

### Requirement: Ensemble consensus (BIEP v2)

The system SHALL provide a canonical ensemble extractor at
`cianfhoghlaim/meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`
that runs **4 paths in parallel** for any incoming PDF, lands each path's
output in a separate per-path DuckLake table, and votes the canonical row
via the RAGAS `biiep_extraction_consensus` metric:

- **Path 1** (BAML): `Docling-serve` → text → BAML function (e.g.
  `b.ExtractJCCurriculum`)
- **Path 2** (Unstract): `Docling-serve` → Unstract workflow → JSON
- **Path 3** (qwen3-vl-8b): page-level image → qwen3-vl-8b raw response
- **Path 4** (gemma-4-26B-A4B): page-level image → gemma-4-26B-A4B raw response

Each path output lands in
`cianfhoghlaim.education.british_isles.<jurisdiction>.<scope>.<subject>.<path>`:

- `.baml_canonical` (Path 1)
- `.unstract_json` (Path 2)
- `.qwen3_vl` (Path 3)
- `.gemma4` (Path 4)

The `voted_output` row is the RAGAS-voted canonical BAML object and lands
in `<...>.voted_canonical`.

#### Scenario: 4-path ensemble on a JC English PDF

- **GIVEN** a new NCCA JC English PDF lands in
  `s3://garage/cianfhoghlaim/junior_cycle/english/en/2026/Q1.pdf`
- **WHEN** the `biiep_ocr_ensemble` Dagster asset materialises
- **THEN** Path 1 (BAML) runs `b.ExtractJCCurriculum(subject="english", language="en", year=1, text=...)`
- **AND** Path 2 (Unstract) runs the `ncca_jc_cba` workflow
- **AND** Path 3 (qwen3-vl-8b) renders page 1 + runs OCR
- **AND** Path 4 (gemma-4-26B-A4B) renders page 1 + runs OCR
- **AND** all 4 outputs land in `cianfhoghlaim.education.british_isles.ireland.junior_cycle.english.en.{baml_canonical,unstract_json,qwen3_vl,gemma4}`
- **AND** the RAGAS `biiep_extraction_consensus` metric ranks the 4 outputs
- **AND** the highest-scoring output lands in `...voted_canonical`
- **AND** the asset check `ragas_score >= 0.70` passes

#### Scenario: Ensemble regression on England AQA

- **GIVEN** the Change 2 England pipeline is in production
- **WHEN** the ensemble runs on an AQA GCSE mathematics PDF
- **THEN** Path 1 invokes `b.ExtractAQAQualSpec(text=...)`
- **AND** Path 2 invokes the `aqa_gcse_spec` Unstract workflow
- **AND** the 4-path output follows the same DuckLake landing convention
- **AND** the Change 2 81-asset pipeline continues to pass regression
