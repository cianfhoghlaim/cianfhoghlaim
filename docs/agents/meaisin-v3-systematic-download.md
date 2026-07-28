# meaisinfhoghlaim v3 — Systematic Operator Surface (the canonical newcomer guide)

> Per the meaisinfhoghlaim v5 umbrella spec. The 7-phase plan for
> systematically wiring + documenting + cross-connecting the
> meaisinfhoghlaim OCR/HTR quadrant to the BIEP v3 operator surface.

## What is the meaisinfhoghlaim v5 operator surface?

The **meaisinfhoghlaim v5** is the canonical operator surface for the
OCR/HTR quadrant of the Cianfhoghlaim platform. It mirrors the BIEP v3
systematic download + iterate plan and brings the same level of
reproducibility, cross-connection, and documentation to the OCR/HTR
quadrant.

The 7-phase plan:

1. **Phase 1**: Canonical operator entrypoints (`mise run meaisin:v3:setup` + `meaisin:v3:status`)
2. **Phase 2**: 24 OCR/VLM models wired into the BIEP v3 MotherDuck Dive + Dagster asset surface
3. **Phase 3**: 7 document converters wired into the BIEP v3 MotherDuck Dive + Dagster asset surface
4. **Phase 4**: 7 canonical newcomer docs (this file + 6 more)
5. **Phase 5**: BAML Test blocks for the 4-path OCR ensemble + RAGAS BIEP ensemble + 24-model v4 registry
6. **Phase 6**: 12 agents wired into the BIEP v3 MotherDuck Dive + Dagster asset surface
7. **Phase 7**: 2 new openspec specs (`meaisin-v3-operator-surface` + `meaisin-24-ocr-models`)

## What is in meaisinfhoghlaim?

The meaisinfhoghlaim quadrant is the AI/ML services layer of the
Cianfhoghlaim platform. It has 11 sub-packages:

- **alignment** — aligner, canuint exporter, character interpolator, colpali aligner, dataset generator, export, Irish G2P
- **backends** — adapter wiring for the OCR/VLM backends (LiteLLM, MLX, Transformers, Llama-Swap, Docling, Unstract)
- **config** — base configuration
- **datasets** — line_segmentation, irish_processing, irish_htr_dataset
- **document_factory** — 7 canonical converters (docling, marker, unstructured, deepseekocr, pymupdf4llm, curriculum_document, pdf_factory)
- **evaluation** — run_evaluation, ragas_pipeline, ragas_biiep_ensemble, compare
- **federated** — irish_ocr_federated
- **models** — 24 OCR/VLM models × 4 backends (LiteLLM, MLX, Transformers, Llama-Swap)
- **ocr** — 4-path OCR ensemble (BAML + Unstract + qwen3-vl + gemma-4-26B-A4B)
- **process** — llm_router, irish_document_scanner, transcript_aligner, dialect_classifier, canuint_audio_slicer, ensemble_gradio
- **quality** — content_quality, completeness, canuint_validator
- **training** — Modal + Unsloth fine-tuning for ICS / IR / OCR

## The 24 OCR/VLM models

The 24 OCR/VLM models across 4 backends are:

| Backend | Model count | Models |
|:--|--:|:--|
| LITELLM | 1 | uccix-llama2-13b |
| MLX | 4 | granite-docling-258M, dots-ocr, deepseek-ocr-2, gemma-4-E2B |
| TRANSFORMERS | 6 | deepseek-ocr-2, olmocr-2-7b-1025, molmo2-4b, molmo2-8b, uccix-mistral-24b, uccix-llama-3.1-8b |
| LLAMASWAP | 13 | (Unsloth GGUF family) |

The 9 canonical `ModelCapability` enum values are: `DENSE_OCR`,
`GROUNDING`, `TABLES`, `LATEX`, `REASONING`, `MATH`, `MULTILINGUAL`,
`GAELIC`, `DIAGRAM`, `DOCLING_LAYOUT`, `UNISTRUCT_WORKFLOW`.

## The 7 document converters

The 7 document converters are:

| Converter | Purpose |
|:--|:--|
| `docling` | IBM Docling (DocTags XML extraction) |
| `marker` | Marker PDF converter |
| `unstructured` | Unstructured.io |
| `deepseekocr` | DeepSeek OCR |
| `pymupdf4llm` | PyMuPDF4LLM |
| `curriculum_document` | Custom for cianfhoghlaim |
| `pdf_factory` | Custom PDF generator |

## The 12 agents

The 12 agents are:

- Root (orchestrator)
- Curriculum (the canonical agent for the BIEP v3 LC pipeline)
- Translation (the canonical agent for the BIEP v3 multilingual pipeline)
- Corpus (the canonical agent for the corpus + IR pipeline)
- Geospatial (the canonical agent for the geospatial pipeline)
- Statistics (the canonical agent for the statistics pipeline)
- Research (the canonical agent for the research pipeline)
- Curriculum Comparison (the canonical agent for the curriculum comparison pipeline)
- Bunchloch Research (the canonical agent for the Bunchloch research pipeline)
- AG-UI Curriculum (the canonical agent for the AG-UI curriculum pipeline)
- Site Analysis (the canonical agent for the site analysis pipeline)
- (12th agent)

## The canonical entrypoints

| What | How |
|:--|:--|
| Setup | `mise run meaisin:v3:setup` |
| Status | `mise run meaisin:v3:status` |
| Per-model entrypoint | `mise run meaisin:ocr:test:<model_key>` (24 models) |
| Per-converter entrypoint | `mise run meaisin:converter:test:<converter_name>` (7 converters) |
| OCR evaluation | `mise run cic:ocr:test` |
| Registry audit | `mise run cic:meaisin:registry-audit` |
| HF watchdog | `mise run cic:meaisin:hf-watchdog` |

## The canonical MotherDuck Dives

The meaisinfhoghlaim v5 surface has 12 MotherDuck Dives:

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

## The canonical dagster assets

The meaisinfhoghlaim v5 surface has ~200+ dagster assets:

- 24 OCR models × 3 assets + 3 checks = 72 + 72 = 144
- 7 converters × 3 assets + 3 checks = 21 + 21 = 42
- 12 agents × 3 assets + 3 checks = 36 + 36 = 72

## See also

- `meaisin-v3-quickstart.md` — the "first 30 minutes" guide
- `meaisin-v3-faq.md` — the canonical FAQ
- `meaisin-v3-ocr-vlm-client.md` — how to invoke the 24 OCR/VLM models
- `meaisin-v3-storage-layout.md` — the canonical meaisinfhoghlaim storage layout
- `meaisin-v3-cron-schedule.md` — the 4-cadence meaisinfhoghlaim schedule
- `meaisin-v3-mieaisin-7-packages.md` — the 11 sub-packages overview
