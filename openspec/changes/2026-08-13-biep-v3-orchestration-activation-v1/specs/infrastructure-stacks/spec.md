## ADDED Requirements

### Requirement: litellm + llama-swap redeployed + GGUF-loaded before BIEP v2 OCR runs

The system SHALL ensure that the litellm proxy
(`http://litellm:4000/v1`) is running with the canonical
`router_settings.fallbacks` config (a list of dicts, not a bare
list of model names — the litellm v1.84+ validation requirement),
AND that the llama-swap container is running with the 17 GGUF model
weights loaded into `stedding/huggingface/gguf/`, BEFORE any Dagster
asset in the `2_materials_curriculum_biiep_ensemble` group is
materialised. A `mise run lint:biiep-v2-orchestration-readiness`
CI gate SHALL fail the build if either condition is not met.

#### Scenario: All 4 paths of the BIEP v2 ensemble reach their backend

- **GIVEN** the litellm proxy is redeployed + llama-swap has the
  GGUF weights loaded
- **WHEN** `EnsembledExtractor.extract(pdf_path=...)` runs
- **THEN** the 4 paths (BAML → docling-serve, Unstract → unstract-api,
  qwen3_vl → litellm → llama-swap → qwen3-vl-8b, gemma4 →
  litellm → llama-swap → gemma-4-26B-A4B) all reach their backend
  endpoints
- **AND** no path's HTTP response is a 404 (the silent-failure mode
  caused by the litellm model alias mismatch)

#### Scenario: RAGAS-voted canonical row lands in ocr_results

- **GIVEN** the litellm + llama-swap readiness is verified
- **WHEN** `python scripts/run_biiep_ocr_ensemble.py --pdf
  <chemistry_syllabus.pdf>` runs
- **THEN** the function returns
  `{"voted_path": "baml|unstract|qwen3_vl|gemma4", "ragas_score": >= 0.70, ...}`
- **AND** 1 canonical row is written to
  `md:cianfhoghlaim.ocr_results` per PDF
- **AND** the canonical row's `model` field matches the model used
  by the voted path

#### Scenario: GGUF-weight download script is idempotent

- **GIVEN** a partial `stedding/huggingface/gguf/` directory (some
  weights already downloaded)
- **WHEN** `python scripts/download_gguf_weights.py` runs
- **THEN** the script skips files that already exist (no re-download)
- **AND** downloads the missing weights only
- **AND** exits 0 when all 17 GGUF files are present
