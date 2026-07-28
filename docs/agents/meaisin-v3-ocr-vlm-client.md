# meaisinfhoghlaim v3 — OCR/VLM Client

> Per the meaisinfhoghlaim v5 umbrella spec. How to invoke the 24
> OCR/VLM models from Python code.

## Overview

The meaisinfhoghlaim v4 registry exposes **24 OCR/VLM models across 4
backends** (LiteLLM, MLX, Transformers, Llama-Swap). The canonical
Python client is at `meaisinfhoghlaim/models/registry.py`.

The 4 backends are:

- **LITELLM** (1 entry: uccix-llama2-13b) — proxied via `litellm.cianfhoghlaim.ie:4000`
- **MLX** (4 entries: granite-docling-258M, dots-ocr, deepseek-ocr-2, gemma-4-E2B) — Apple Silicon MLX
- **TRANSFORMERS** (6 entries: deepseek-ocr-2, olmocr-2-7b-1025, molmo2-4b, molmo2-8b, uccix-mistral-24b, uccix-llama-3.1-8b) — Python inline
- **LLAMASWAP** (13 entries: the Unsloth GGUF family) — served via `llama-swap` at `ghcr.io/mostlygeek/llama-swap:v166`

## Basic usage (from Python)

```python
from meaisinfhoghlaim.models.registry import VISION_MODELS, select_ocr_backend

# 1. Iterate the 24 OCR/VLM models
for key, model in VISION_MODELS.items():
    print(f"{key}: {model.unsloth_id or model.upstream_id}")

# 2. Get the optimal model for the M4 Max 48 GB target
from meaisinfhoghlaim.models.registry import get_optimal_for_m4
model = get_optimal_for_m4()
print(f"Optimal for M4 Max 48 GB: {model.key}")

# 3. Pick a model for a given PDF
from pathlib import Path
selection = select_ocr_backend(Path("syllabus.pdf"))
```

## Advanced usage (with the 4-path OCR ensemble + RAGAS voting)

The 4-path OCR ensemble is at `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`.
The canonical call pattern:

```python
from meaisinfhoghlaim.ocr.ensemble.ensembled_extractor import EnsembledExtractor

# 1. The 4-path ensemble (per the 2026-07-22 change)
extractor = EnsembledExtractor()
result = extractor.extract(
    pdf_path="s3://garage/cianfhoghlaim/sample.pdf",
    baml_function="b.ExtractPrimaryLearningOutcomes",
    jurisdiction="ireland",
    scope="education",
    subject="sample",
    board="ncca",
    qualification_level="higher",
    language="en",
)

# 2. The result contains per-path rows + the RAGAS-voted_canonical row
print(result.baml_canonical_row)   # Path 1 (Docling → BAML)
print(result.unstract_json_row)    # Path 2 (Docling → Unstract)
print(result.qwen3_vl_row)          # Path 3 (qwen3-vl-8b)
print(result.gemma4_row)           # Path 4 (gemma-4-26B-A4B)
print(result.voted_canonical_row)   # The RAGAS-voted_canonical row
print(result.ragas_score)          # 0.0-1.0 (must be >= 0.70 for the asset check to pass)
```

## Error handling

The canonical error handling pattern:

```python
try:
    result = extractor.extract(
        pdf_path="s3://garage/cianfhoghlaim/sample.pdf",
        baml_function="b.ExtractPrimaryLearningOutcomes",
        jurisdiction="ireland",
        scope="education",
        subject="sample",
        board="ncca",
        qualification_level="higher",
        language="en",
    )
except Exception as exc:
    # Fall back to the canonical heuristic extractor
    result = heuristic_extract(pdf_path)
    log_warning(f"OCR ensemble failed: {exc}; using heuristic fallback")
```

## Testing the 24 OCR models

Per the canonical pattern, the 24 OCR models have BAML Test blocks
for v5 validation. To run the BAML tests:

```bash
cd baml_src
uv run baml-cli test
```

The 24 model Test blocks are in `meaisinfhoghlaim/ocr/ensemble/tests.baml`.

## Per-meaisin canonical imports

The meaisinfhoghlaim v4 Pydantic models are at
`meaisinfhoghlaim.models.registry`:

```python
from meaisinfhoghlaim.models.registry import (
    OCRModel,           # The 24-model Pydantic config
    VISION_MODELS,      # The 24-key dict
    ModelBackend,       # The 4-backend enum
    ModelCapability,    # The 9-capability enum
    ModelRole,          # The tier enum (tier1/2/3)
    ClassicalOCRStack,  # The 6-stack classical config
    all_models,         # Iterator over all 24 models
    all_classical_stacks,  # Iterator over all 6 classical stacks
    get_optimal_for_m4,  # Selector for M4 Max 48 GB target
    select_ocr_backend,  # The 4-path ensemble coordinator
)
```

## See also

- `meaisin-v3-systematic-download.md` — the canonical newcomer guide
- `meaisin-v3-quickstart.md` — the "first 30 minutes" guide
- `meaisin-v3-faq.md` — the canonical FAQ
- `meaisin-v3-storage-layout.md` — the canonical meaisinfhoghlaim storage layout
- `meaisin-v3-cron-schedule.md` — the 4-cadence meaisinfhoghlaim schedule
- `meaisin-v3-mieaisin-7-packages.md` — the 11 sub-packages overview
