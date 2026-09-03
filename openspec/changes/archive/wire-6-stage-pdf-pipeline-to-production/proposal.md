## Why

The `2026-06-29-fix-ocr-vlm-registry-with-unfastened-priority` change
created the 6-stage PDF processing pipeline at
`oideachais-pdf-processing/spec.md`, but the actual ML model calls
(Stages 1, 2, 3) were stubbed. This change wires the pipeline to
production:

- Stage 1: litellm + the v4 Unsloth GGUF (via llama-swap)
- Stage 2: Granite-Docling + Molmo2-8B (via transformers)
- Stage 3: BAML extraction with the regenerated baml_client
- Stage 4: NCCA taxonomy loaded from DuckLake
- Stage 5: CocoIndex v1 + BGE-M3 embeddings written to LanceDB
- Stage 6: DuckLake + Cognee cognify + Graphiti episode

## What changes

- Wire 6 Dagster assets at
  `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing_assets.py`
- Replace all ML stubs in the 4 pipeline modules with real
  litellm / transformers / DuckDB / LanceDB / Cognee / Graphiti calls
- Wire the observability layer (Langfuse + MLflow + RAGAS + Logfire)
- Add the 3 new BAML files (`leaving_cert_marking_scheme_extraction.baml`,
  `clients_llama_swap.baml`) to the baml_client codegen
- Run the 6-stage pipeline on the existing 108,000 pages of NCCA
  syllabi + SEC past papers + SEC marking schemes
- Materialise the results in DuckLake + Cognee + LanceDB

## Impact

- 6-stage pipeline runs in production on the arm1-oci + M4 Max
- The marimo dashboard at `/dashboards/pdf-processing` shows the
  6-stage status for any (subject, year, paper) tuple
- The Gradio HF Space at `spaces/oideachais-pdf-review/` allows
  human reviewers to correct mis-categorised questions
- The full Celtic curriculum pipeline (syllabus + past paper +
  marking scheme) is now queryable via the LanceDB HNSW index

## Out of scope

- Multi-nation expansion (UK, Scotland, Wales, etc. — separate
  openspec change per openspec/changes/2026-06-28-...)
- The image-generation models (Qwen-Image-2512, Z-Image-Turbo,
  FLUX.2-klein-9B) — covered by `celtic-asset-generation/spec.md`
