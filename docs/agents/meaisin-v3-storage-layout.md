# meaisinfhoghlaim v3 — Storage Layout

> Per the meaisinfhoghlaim v5 umbrella spec. The canonical storage layout
> for the meaisinfhoghlaim OCR/HTR quadrant.

## Overview

The meaisinfhoghlaim v5 storage layout spans 4 layers:

1. **Canonical model registry** — the 24 OCR/VLM models in the v4 registry
2. **DuckLake + DuckDB** — the analytical meaisinfhoghlaim surface
3. **MotherDuck** — the live dashboards + scheduled flights
4. **Dagster** — the orchestration + assets + checks + sensors

## Layer 1: Canonical model registry (the 24 OCR/VLM models)

The canonical 24 OCR/VLM models are at `meaisinfhoghlaim/models/registry.py`:

```python
VISION_MODELS = {
    "deepseek-ocr-2": OCRModel(...),
    "docling-serve": OCRModel(...),
    "dots-ocr": OCRModel(...),
    "gemma-3-4b": OCRModel(...),
    "glm-4.6v-flash": OCRModel(...),
    "internvl3-8b": OCRModel(...),
    "llama-3.2-vision-11b": OCRModel(...),
    "molmo2-4b": OCRModel(...),
    "molmo2-8b": OCRModel(...),
    "olmocr-2-7b-1025": OCRModel(...),
    "paddleocr-vl-1.6": OCRModel(...),
    "qwen3-vl-30b-a3b": OCRModel(...),
    "qwen3-vl-4b": OCRModel(...),
    "qwen3-vl-8b": OCRModel(...),
    "qwen3.6-27b-mtp": OCRModel(...),
    "uccix-llama-3.1-8b": OCRModel(...),
    "uccix-llama2-13b": OCRModel(...),
    "uccix-mistral-24b": OCRModel(...),
    "unstract-api": OCRModel(...),
    # Additional 5 entries (LlamaSwap Unsloth GGUF family)
    ...
}
```

## Layer 2: DuckLake + DuckDB (the analytical surface)

The canonical DuckLake URI for the meaisinfoghhlaim row is
`md:cianfhoghlaim/education/meaisin.<subpackage>.<model_key>.rows` (the
canonical BIEP v3 namespace pattern).

The meaisinfhoghlaim v5 namespaces are:

```text
md:cianfhoghlaim.education.meaisin.models.registry
md:cianfhoghlaim.education.meaisin.ensemble.<path>.rows
md:cianfhoghlaim.education.meaisin.evaluation.ragas_results
md:cianfhoghlaim.education.meaisin.converter.<name>.rows
md:cianfhoghlaim.education.meaisin.agent.<name>.runs
```

## Layer 3: MotherDuck (12 dives)

The 12 meaisinfhoghlaim v5 MotherDuck Dives are:

- `meaisin_ocr_registry_dive` — 24 OCR/VLM model coverage
- `meaisin_ensemble_audit_dive` — 4-path OCR ensemble RAGAS scores
- `meaisin_evaluation_summary_dive` — RAGAS evaluation metrics
- `meaisin_converter_coverage_dive` — 7-converter coverage
- `meaisin_converter_performance_dive` — 7-converter latency
- `meaisin_converter_quality_dive` — 7-converter quality
- `meaisin_agent_registry_dive` — 12-agent coverage
- `meaisin_agent_memory_dive` — agent memory backend state
- `meaisin_agent_observability_dive` — agent langfuse traces
- (3 more agent dives)

## Layer 4: Dagster (the orchestration + assets + checks)

The meaisinfhoghlaim v5 surface has ~200+ Dagster assets:

- 24 OCR models × 3 assets + 3 checks = 72 + 72 = 144
- 7 converters × 3 assets + 3 checks = 21 + 21 = 42
- 12 agents × 3 assets + 3 checks = 36 + 36 = 72

The canonical Dagster groups are:

- `1_ingestion_meaisin_ocr_vlm_ocr_model_<key>`
- `2_materials_meaisin_ocr_vlm_ocr_model_<key>`
- `3_model_lifecycle_meaisin_ocr_vlm_ocr_model_<key>`
- `1_ingestion_meaisin_converter_converter_<name>`
- `2_materials_meaisin_converter_converter_<name>`
- `3_model_lifecycle_meaisin_converter_converter_<name>`
- `1_ingestion_meaisin_agent_agent_<name>`
- `2_materials_meaisin_agent_agent_<name>`
- `3_model_lifecycle_meaisin_agent_agent_<name>`

## Layer 5: BAML (the 24 OCR/VLM Extract* functions)

The canonical BAML files are at
`baml_src/british_isles/ireland/meaisin/`. Each model has
canonical Test blocks per the v1 spec.

## Layer 6: CocoIndex v1 (the per-model indexing)

The canonical CocoIndex v1 Apps are at
`cocoindex/biep_parity/meaisin/`. Each model has a canonical
chunk + embed + index pipeline.

## See also

- `meaisin-v3-systematic-download.md` — the canonical newcomer guide
- `meaisin-v3-quickstart.md` — the "first 30 minutes" guide
- `meaisin-v3-faq.md` — the canonical FAQ
- `meaisin-v3-ocr-vlm-client.md` — how to invoke the 24 OCR/VLM models
- `meaisin-v3-cron-schedule.md` — the 4-cadence meaisinfhoghlaim schedule
- `meaisin-v3-mieaisin-7-packages.md` — the 11 sub-packages overview
