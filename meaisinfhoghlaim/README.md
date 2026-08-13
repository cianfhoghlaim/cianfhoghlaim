# `meaisinfhoghlaim/` — OCR/HTR/Alignment Sub-Package

> **The canonical post-v7 Python sub-package for the OCR/HTR/alignment work — 26 VISION_MODELS, 6 CLASSICAL_OCR backends, 4 alignment methods, 4 educational agents, 1 BIEP v2 4-path ensemble.**

## Quick start

```bash
# The 6 canonical CLASSICAL_OCR backends (post-v7)
python -c "from meaisinfhoghlaim.models.registry import CLASSICAL_OCR; print(len(CLASSICAL_OCR))"
# -> 6

# The 26 VISION_MODELS (24 v4 + 2 v5 BIEP v2 entrants)
python -c "from meaisinfhoghlaim.models.registry import VISION_MODELS; print(len(VISION_MODELS))"
# -> 24

# The M4-Max dispatch helper (returns the optimal model for the M4 Max 64GB)
python -c "from meaisinfhoghlaim.models.registry import select_optimal_for_m4_max; print(select_optimal_for_m4_max())"
# -> gemma-4-26B-A4B

# The BIEP v2 4-path ensemble extractor
python -c "from meaisinfhoghlaim.ocr.ensemble.ensembled_extractor import EnsembledExtractor; print(EnsembledExtractor)"

# The Irish-English aligner with 4 alignment methods
python -c "from meaisinfhoghlaim.alignment import aligner; print(aligner.IrishEnglishAligner)"

# The 3 educational agents (academic_history + celtic_grammar + celtic_morphology)
python -c "from agents.meaisinfhoghlaim.educational import academic_history_agent, celtic_grammar_agent, celtic_morphology_agent"
```

## Layout — 13 sub-trees

```
meaisinfhoghlaim/
├── __init__.py                       # (empty — canonical home is at root)
├── alignment/                        # Irish-English alignment + ColPali + char interpolation
│   ├── aligner.py                    # IrishEnglishAligner (VecAlign + HunAlign + GaoisAlign + Hybrid)
│   ├── colpali_aligner.py            # ColPaliAligner (manuscript bbox extraction)
│   ├── character_interpolator.py     # word→char timestamp interpolation for ASR
│   ├── dataset_generator.py          # HF/JSONL/Parquet/TMX dataset generator
│   ├── export.py                     # HuggingFace dataset export
│   ├── quality.py                    # Alignment quality scoring
│   ├── irish_g2p.py                   # Irish grapheme-to-phoneme
│   └── canuint_exporter.py           # Canúint dialect export
├── backends/                         # OCR backend adapters (PaddleOCR + Docling + Dots + Unstract)
│   ├── adapters.py                   # OCRAdapterRegistry + compare_ocr_models()
│   ├── author_archive_ocr.py         # OCR for the author-archive corpus
│   └── gaelic_metrics.py             # Irish-language quality metrics (fada accuracy)
├── config/                           # Base config + cache_config + lightrag + pdf_extractors YAMLs
├── datasets/                         # Irish HTR + line segmentation + processing
│   ├── irish_htr_dataset.py          # The HTR training dataset (25KB)
│   ├── irish_processing.py           # Irish document processing
│   └── line_segmentation.py          # Manuscript line segmentation
├── document_factory/                 # PDF → md/dict converters
│   ├── docling.py                    # IBM Docling converter
│   ├── marker.py                     # Marker converter
│   ├── unstructured.py               # Unstructured converter
│   ├── deepseekocr.py                # DeepSeek-OCR converter
│   ├── pymupdf4llm.py                # PyMuPDF4LLM converter
│   ├── curriculum_document.py        # Curriculum document representation
│   ├── pdf_factory.py                # PDF factory (orchestrates converters)
│   └── format_detectors.py           # File format detectors
├── evaluation/                       # OCR + RAGAS + BIEP ensemble evaluation
│   ├── compare.py                    # OCR comparison harness
│   ├── ragas_pipeline.py             # RAGAS-based scoring
│   ├── ragas_biiep_ensemble.py       # RAGAS biiep_extraction_consensus metric
│   └── run_evaluation.py             # Standalone runner
├── federated/                        # Federated OCR (Irish OCR ensemble)
│   └── irish_ocr_federated.py        # Irish OCR federated smoke
├── models/                           # CANONICAL home for the OCR/VLM registry
│   ├── registry.py                   # 26 VISION_MODELS + 6 CLASSICAL_OCR + 3 TEXT_MODELS
│   ├── routing.py                    # LlamaSwap routing table
│   └── ci/                           # CI fixtures
├── ocr/                              # Back-compat shim + 4-path ensemble
│   ├── __init__.py                   # Package marker
│   ├── ensemble/                     # BIEP v2 4-path ensemble (baml + unstract + qwen3_vl + gemma4)
│   │   └── ensembled_extractor.py    # The asyncio.gather 4-path orchestrator
│   └── models/                       # Back-compat shim (deprecation warning)
│       ├── __init__.py               # Re-exports VISION_MODELS from canonical home
│       └── registry.py               # Same
├── process/                          # Pipeline processors
│   ├── irish_document_scanner.py     # Irish document scanner
│   ├── transcript_aligner.py         # ASR transcript alignment
│   ├── dialect_classifier.py         # Irish dialect classifier
│   ├── canuint_audio_slicer.py       # Canúint audio slicer
│   ├── llm_router.py                 # LLM routing helper
│   └── ensemble_gradio.py            # Gradio UI for the ensemble
├── quality/                          # Content quality scoring
│   ├── content_quality.py            # Irish content quality (fada + grammar)
│   ├── completeness.py               # Document completeness scoring
│   └── canuint_validator.py          # Canúint validation
├── training/                         # Model fine-tuning (Modal + local)
│   ├── modal_finetune/               # Modal.com cloud GPU finetuning
│   │   ├── finetune_irish.py         # Irish LoRA/QLoRA finetune
│   │   └── embed_batch.py            # Batch embedding on Modal A100
│   └── training/                     # Local HTR/LLM/TTS training
│       ├── unsloth_trainer.py        # Unsloth 2x speedup QLoRA
│       ├── unsloth_config.py         # Unsloth config templates
│       ├── llm_training.py           # Generic LLM training entrypoint
│       ├── htr_training.py           # HTR training
│       ├── tts_training.py           # TTS training
│       ├── tts_dataset_generator.py  # TTS dataset generation
│       ├── mlflow_callbacks.py       # MLflow integration
│       └── langfuse_callbacks.py     # Langfuse integration
├── federated/                        # Federated OCR (Irish)
└── cli.py                            # 48-line argparse CLI (`cianfhoghlaim-ocr`)
```

## The 6 CLASSICAL_OCR backends

| Backend | Purpose | Port | Docker stack |
|:--|:--|--:|:--|
| **Docling-serve** | Document layout + table extraction | 5001 | `bonneagar/stacks/docling-serve/` |
| **PaddleOCR** | Multilingual OCR (100+ languages) | 8888 | `bonneagar/stacks/paddleocr/` |
| **Tesseract** | The classic OCR engine | 8889 | _(not deployed)_ |
| **Tesseract-shadow** | Tesseract 4 shadow variant for A/B testing | 8890 | _(not deployed)_ |
| **Unstract** | No-code LLM-powered extraction | 8002 | `bonneagar/stacks/unstract/` |
| **Dots-OCR** | High-fidelity OCR for handwritten text | 8001 | `bonneagar/stacks/dots-ocr/` |

`OlmOCR` is also deployed at `bonneagar/stacks/olmocr/` but is not in
the canonical `CLASSICAL_OCR` registry (it's reserved for v5 BIEP
v2 entrants via `VISION_MODELS`).

## The 26 VISION_MODELS

The canonical 26 VLM + OCR-vision models in
`models/registry.py:VISION_MODELS`:

- **Gemma 4 family** (4): `gemma-4-E2B`, `gemma-4-E4B`, `gemma-4-12B`,
  `gemma-4-26B-A4B` (M4 Max default)
- **GLM-4.6V Flash** (1) (Z.ai)
- **Qwen 3-VL** (3): `qwen3-vl-4b`, `qwen3-vl-8b` (workhorse),
  `qwen3-vl-30b-a3b`
- **Qwen 3.6 27B MTP** (1) (text-only)
- **DeepSeek-OCR-2** (1)
- **olmOCR-2-7B-1025** (1)
- **Granite-Docling 258M** (1)
- **UCCIX** (3): `uccix-mistral-24b`, `uccix-llama-3.1-8b`,
  `uccix-llama2-13b` (DEPRECATED, `available=False`)
- **Dots-OCR** (1)
- **PaddleOCR-VL 1.6** (1)
- **Molmo2** (2): `molmo2-4b`, `molmo2-8b`
- **InternVL3-8B** (1)
- **Llama 3.2 Vision 11B** (1) (legacy)
- **Gemma 3 4B** (1) (legacy)
- **v5 BIEP v2** (2): `unstract-api`, `docling-serve`

Total: 24 v4 + 2 v5 = 26.

## The 4 alignment methods

`meaisinfhoghlaim/alignment/aligner.py` exposes
`IrishEnglishAligner` with 4 alignment methods (not the 3
"primitives" that earlier docs called out):

| Method | Description |
|:--|:--|
| **VecAlign** | Vector-based sentence alignment (multilingual embedding cosine) |
| **HunAlign** | The HunAlign statistical aligner (Gale-Church variant) |
| **GaoisAlign** | The Gaois.ie terminology-aware aligner |
| **Hybrid** | Combine VecAlign + GaoisAlign (fallback to HunAlign for low-confidence pairs) |

Plus two specialised aligners:

| Module | Purpose |
|:--|:--|
| `colpali_aligner.py` | `ColPaliAligner` for manuscript bbox extraction |
| `character_interpolator.py` | word→char timestamp interpolation for ASR alignment |

## The 3 educational agents + 1 manifest

`agents/meaisinfhoghlaim/educational/`:

| Agent / file | Framework | Purpose |
|:--|:--|:--|
| `academic_history_agent.py` | ADK | The cross-archive academic history (research paper retrieval + citation extraction) |
| `academic_history_manifest.py` | (manifest) | The academic history manifest schema (Pydantic v2) |
| `celtic_grammar_agent.py` | ADK | The Celtic grammar specialist (Irish + Welsh + Scottish Gaelic + Breton + Cornish + Manx) |
| `celtic_morphology_agent.py` | ADK | The Celtic morphology specialist (verb conjugation + noun declension + adjective agreement) |

## The 19 per-model OCR mise tasks

```bash
mise run meaisin:ocr:test:deepseek-ocr-2
mise run meaisin:ocr:test:docling-serve
mise run meaisin:ocr:test:dots-ocr
mise run meaisin:ocr:test:gemma-3-4b
mise run meaisin:ocr:test:glm-4.6v-flash
mise run meaisin:ocr:test:internvl3-8b
mise run meaisin:ocr:test:llama-3.2-vision-11b
mise run meaisin:ocr:test:molmo2-4b
mise run meaisin:ocr:test:molmo2-8b
mise run meaisin:ocr:test:olmocr-2-7b-1025
mise run meaisin:ocr:test:paddleocr-vl-1.6
mise run meaisin:ocr:test:qwen3-vl-30b-a3b
mise run meaisin:ocr:test:qwen3-vl-4b
mise run meaisin:ocr:test:qwen3-vl-8b
mise run meaisin:ocr:test:qwen3.6-27b-mtp
mise run meaisin:ocr:test:uccix-llama-3.1-8b
mise run meaisin:ocr:test:uccix-llama2-13b
mise run meaisin:ocr:test:uccix-mistral-24b
mise run meaisin:ocr:test:unstract-api
```

## The 7 converter mise tasks

```bash
mise run meaisin:converter:docling
mise run meaisin:converter:marker
mise run meaisin:converter:unstructured
mise run meaisin:converter:deepseekocr
mise run meaisin:converter:pymupdf4llm
mise run meaisin:converter:curriculum_document
mise run meaisin:converter:pdf_factory
```

## The 12 agent mise tasks

```bash
mise run meaisin:agent:root
mise run meaisin:agent:curriculum
mise run meaisin:agent:translation
mise run meaisin:agent:corpus
mise run meaisin:agent:geospatial
mise run meaisin:agent:statistics
mise run meaisin:agent:research
mise run meaisin:agent:curriculum_comparison
mise run meaisin:agent:bunchloch_research
mise run meaisin:agent:ag_ui_curriculum
mise run meaisin:agent:site_analysis
mise run meaisin:agent:hitl_agent
```

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new OCR backend | `models/registry.py` (add to `CLASSICAL_OCR`) + create the Docker stack at `bonneagar/stacks/<name>/` |
| Add a new ensemble pattern | `ocr/ensemble/` |
| Add a new alignment method | `alignment/aligner.py` (extend the `AlignmentMethod` enum) |
| Add a new OCR Docker stack | `bonneagar/stacks/<name>/` (6-file GOLD_STANDARD pattern) |
| Add a new VLM model | `models/registry.py` (add to `VISION_MODELS`) |
| Modify an educational agent | `agents/meaisinfhoghlaim/educational/<slug>_agent.py` |
| Add OCR/HTR Dagster assets | `orchestration/defs/5_agent_ops/ocr_assets/` |
| Deploy the OCR/HTR pipeline | `meaisinfhoghlaim/cli.py` |

## Cross-references

- [`../agents/meaisinfhoghlaim/AGENTS.md`](../agents/meaisinfhoghlaim/AGENTS.md) — the OCR/HTR alignment sub-package doc (agent-facing)
- [`../agents/AGENTS.md`](../agents/AGENTS.md) — the agents quadrant overview
- [`../agents/api/AGENTS.md`](../agents/api/AGENTS.md) — the Hono API routes layer
- [`../agents/tools/AGENTS.md`](../agents/tools/AGENTS.md) — the tools layer
- [`../openspec/AGENTS.md`](../openspec/AGENTS.md) — openspec workflow
- [`../.agents/skills/agent-fleet-orchestration/SKILL.md`](../.agents/skills/agent-fleet-orchestration/SKILL.md) — the 12-agent fleet wiring
- [`../.agents/skills/meaisin-ocr/SKILL.md`](../.agents/skills/meaisin-ocr/SKILL.md) — OCR/HTR skill (if present)

## Data platform router

> **The single router for the 5 per-area data platform docs** is at [`../dlt_sources/DATA_PLATFORM_ROUTER.md`](../dlt_sources/DATA_PLATFORM_ROUTER.md). Documents the 6 critical conventions (relative imports / `USE_LOCAL_SCRAPES` / zero absolute namespaces / R1-R4 conformance / MODEL_REGISTRY-only / factory pattern) that apply ACROSS all 5 sub-packages.