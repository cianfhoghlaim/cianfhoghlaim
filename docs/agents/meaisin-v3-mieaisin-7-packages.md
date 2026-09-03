# meaisinfhoghlaim v3 — 11 Sub-Packages Overview

> Per the meaisinfhoghlaim v5 umbrella spec. The 11 sub-packages
> overview of the meaisinfhoghlaim AI/ML quadrant.

## Overview

The meaisinfhoghlaim quadrant has 11 sub-packages, each with a
specific responsibility:

| Sub-package | Files | Purpose |
|:--|--:|:--|
| `alignment` | 9 | Aligners + Canúint exporter + G2P (grapheme-to-phoneme) |
| `backends` | 4 | Adapter wiring for the OCR/VLM backends (LiteLLM, MLX, Transformers, Llama-Swap) |
| `config` | 2 | Base configuration |
| `datasets` | 4 | Line segmentation + Irish processing + Irish HTR dataset |
| `document_factory` | 12 | 7 canonical converters (docling, marker, unstructured, deepseekocr, pymupdf4llm, curriculum_document, pdf_factory) |
| `evaluation` | 5 | RAGAS evaluation pipeline + run_evaluation driver + RAGAS BIEP ensemble + compare |
| `federated` | 2 | Federated OCR (the Irish OCR federated training pipeline) |
| `models` | 5 | 24 OCR/VLM model registry (v4 canonical home) |
| `ocr` | 4 | 4-path OCR ensemble (BAML + Unstract + qwen3-vl + gemma4) |
| `process` | 7 | LLM router + Irish document scanner + transcript aligner + dialect classifier + Canúint audio slicer + Gradio ensemble |
| `quality` | 4 | Content quality + completeness + Canúint validator |
| `training` | 12 | Modal + Unsloth fine-tuning (ICS / IR / OCR) |

**Total: 72 Python files, 23,914 lines of code.**

## Per-sub-package detail

### 1. `alignment` (9 files)

The alignment sub-package contains the per-document alignment
pipelines plus the Canúint (Irish intonation) exporter + the G2P
(grapheme-to-phoneme) converter + the dataset generator + the ColPali
aligner (multi-modal retrieval).

- `aligner.py` (523 lines) — the canonical text alignment pipeline
- `colpali_aligner.py` (471 lines) — the ColPali multi-modal aligner
- `canuint_exporter.py` — the Canúint audio exporter
- `character_interpolator.py` — the character interpolator
- `dataset_generator.py` — the alignment dataset generator
- `export.py` — the alignment exporter
- `irish_g2p.py` — the Irish grapheme-to-phoneme converter
- `__init__.py` (61 lines) — the canonical exports

### 2. `backends` (4 files)

The backends sub-package contains the adapter wiring for the OCR/VLM
backends:

- `adapters.py` — the adapter wiring for the 4 backends
- `gaelic_metrics.py` — the gaelic metrics
- `author_archive_ocr.py` — the author archive OCR backend
- `__init__.py` — the canonical exports

### 3. `datasets` (4 files)

The datasets sub-package contains the Irish-specific datasets:

- `line_segmentation.py` — the line segmentation dataset
- `irish_processing.py` — the Irish processing pipeline
- `irish_htr_dataset.py` — the Irish HTR dataset
- `__init__.py` — the canonical exports

### 4. `document_factory` (12 files)

The document factory sub-package contains the 7 canonical converters:

- `pdf_factory.py` — the custom PDF generator
- `format_detectors.py` — the format detectors
- `converters/` — the 7 converters:
  - `docling_converter.py` (158 lines) — IBM Docling DocTags XML
  - `marker_converter.py` (132 lines) — Marker PDF converter
  - `unstructured_converter.py` — Unstructured.io
  - `deepseekocr_converter.py` — DeepSeek OCR
  - `pymupdf4llm_converter.py` — PyMuPDF4LLM
  - (`curriculum_document.py` — the custom cianfhoghlaim converter)
  - (more)
- `__init__.py` (61 lines) — the canonical exports

### 5. `evaluation` (5 files)

The evaluation sub-package contains the RAGAS evaluation pipeline:

- `run_evaluation.py` — the run_evaluation driver
- `ragas_pipeline.py` — the RAGAS evaluation pipeline
- `ragas_biiep_ensemble.py` (187 lines) — the RAGAS BIEP ensemble
- `compare.py` — the comparison tool
- `__init__.py` (11 lines) — the canonical exports

### 6. `federated` (2 files)

The federated sub-package contains the federated OCR pipeline:

- `irish_ocr_federated.py` — the Irish OCR federated training pipeline
- `__init__.py` (52 lines) — the canonical exports

### 7. `models` (5 files)

The models sub-package contains the 24 OCR/VLM model registry:

- `registry.py` (1031 lines) — the 24 OCR/VLM model registry (v4 canonical home)
- `routing.py` — the model routing
- `ci/` — the CI integration
  - `hf_watchdog.py` — the HuggingFace watchdog
- `__init__.py` (84 lines) — the canonical exports

### 8. `ocr` (4 files)

The OCR sub-package contains the 4-path OCR ensemble:

- `ensemble/ensembled_extractor.py` (518 lines) — the 4-path OCR ensemble
- `models/registry.py` — the OCR models registry (back-compat shim)
- `__init__.py` — the canonical exports

### 9. `process` (7 files)

The process sub-package contains the document processing pipeline:

- `llm_router.py` — the LLM router
- `irish_document_scanner.py` (740 lines) — the Irish document scanner
- `transcript_aligner.py` — the transcript aligner
- `dialect_classifier.py` — the dialect classifier
- `canuint_audio_slicer.py` — the Canúint audio slicer
- `ensemble_gradio.py` — the Gradio ensemble
- `__init__.py` — the canonical exports

### 10. `quality` (4 files)

The quality sub-package contains the content quality pipeline:

- `content_quality.py` — the content quality
- `completeness.py` — the completeness
- `canuint_validator.py` — the Canúint validator
- `__init__.py` (39 lines) — the canonical exports

### 11. `training` (12 files)

The training sub-package contains the Modal + Unsloth fine-tuning:

- `modal_finetune/finetune_irish.py` — the Modal fine-tuning
- `modal_finetune/embed_batch.py` — the embed batch
- `training/htr_training.py` (117 lines) — the HTR training
- `training/llm_training.py` — the LLM training
- `training/unsloth_config.py` — the Unsloth config
- `training/unsloth_trainer.py` — the Unsloth trainer
- (more)
- `__init__.py` — the canonical exports

## See also

- `meaisin-v3-systematic-download.md` — the canonical newcomer guide
- `meaisin-v3-quickstart.md` — the "first 30 minutes" guide
- `meaisin-v3-faq.md` — the canonical FAQ
- `meaisin-v3-ocr-vlm-client.md` — how to invoke the 24 OCR/VLM models
- `meaisin-v3-storage-layout.md` — the canonical meaisinfhoghlaim storage layout
- `meaisin-v3-cron-schedule.md` — the 4-cadence meaisinfhoghlaim schedule
