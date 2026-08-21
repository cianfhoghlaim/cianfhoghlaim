---
title: Oideachais PDF Review
emoji: 📚
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: Human review for the 6-stage Oideachais PDF processing pipeline (ZeroGPU)
---

# Oideachais PDF Review

A Gradio interface for human review of Stage 4 topic-validation
mismatches from the **6-stage Oideachais PDF processing pipeline**
(`oideachais-pdf-processing` spec). The pipeline processes NCCA
syllabus PDFs, SEC past paper PDFs, and SEC marking-scheme PDFs
through:

1. **OCR (VLM dispatch)** — picks the optimal (model, backend) pair
   from the 22-entry VISION_MODELS registry (post-2026-06-29 trim)
2. **Diagram detection** — Granite-Docling + Molmo2-8B
3. **BAML extraction** — `ExtractLeavingCertSyllabus` /
   `ExtractPastPaper` / `ExtractMarkingScheme`
4. **Topic validation** — fuzzy-match against NCCA taxonomy
5. **Semantic chunking** — CocoIndex v1 + BGE-M3
6. **Lakehouse + Cognee + Graphiti** — DuckLake + KG + temporal

This Space runs on **HuggingFace Spaces ZeroGPU** (free tier):
- The Gradio UI runs on CPU
- The in-app LLM features (suggested correction, explanation) run on
  the ZeroGPU backing card via `@spaces.GPU(duration=N)` decorators

The 2 models used are v4 Unsloth GGUFs:
- `unsloth/gemma-3-4b-it-GGUF` (4 GB) for "suggested correction"
- `unsloth/gemma-4-26B-A4B-it-GGUF` (14 GB MoE) for "explanation"

## Post-2026-06-29 trim

The v4 OCR/VLM registry was trimmed from 24 to 20 entries that
fit on M4 Max 48 GB unified memory. The 4 removed models
(qwen3-vl-235b-a22b 130GB, glm-4.6v-full 107GB,
qwen3.6-35b-a3b-mtp 22GB marginal, gemma-4-31B 19GB marginal) were
too large for M4 and are documented in the openspec change
`deploy-v4-ocr-vlm-on-m4-max`.

## Local development

```bash
# Install requirements
pip install -r requirements.txt

# Run locally (requires HF Spaces ZeroGPU credentials)
python app.py
```

## Production deployment

Pushed to HF Spaces via the `spaces-cicd-pipeline` spec at
`infrastructure/ci/spaces-sync.yml`. Auto-builds on push.
