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
short_description: Human review for the 6-stage Oideachais PDF processing pipeline
---

# Oideachais PDF Review

A Gradio interface for human review of Stage 4 topic-validation
mismatches from the **6-stage Oideachais PDF processing pipeline**
(`oideachais-pdf-processing` spec). The pipeline processes NCCA
syllabus PDFs, SEC past paper PDFs, and SEC marking-scheme PDFs
through:

1. **OCR (VLM dispatch)** — picks the optimal (model, backend) pair
   from the 24-entry VISION_MODELS registry.
2. **Diagram detection** — Granite-Docling + Molmo2-8B
3. **BAML extraction** — `ExtractLeavingCertSyllabus` /
   `ExtractPastPaper` / `ExtractMarkingScheme`
4. **Topic validation** — fuzzy-match against NCCA taxonomy
5. **Semantic chunking** — CocoIndex v1 + BGE-M3
6. **Lakehouse + Cognee + Graphiti** — DuckLake + KG + temporal

When Stage 4 flags a topic as mis-categorised, a reviewer can:

- See the record details (subject, year, paper, question number,
  original topic, suggested topic, match score)
- Get a suggested correction from `gemma-3-4b` (Unsloth GGUF)
- Get a 2-3 sentence explanation from `gemma-4-26B-A4B` (Unsloth
  MoE GGUF) about why the BAML extraction mis-tagged the topic
- Approve the correction (writes back to DuckLake)
- Reject the correction (flags for second-pass review)

The 6-stage pipeline + 24-entry VISION_MODELS registry + this
Gradio interface are documented in the openspec change
`2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority/` and
the spec at `openspec/specs/oideachais-pdf-processing/spec.md`.

## Local development

```bash
# Install requirements
pip install -r requirements.txt

# Run locally (requires llama-swap on http://localhost:8080)
python app.py
```

## Production deployment

Deployed via the `spaces-cicd-pipeline` spec at
`infrastructure/ci/spaces-sync.yml`.

## Models used (Unsloth GGUFs via llama-swap)

- `unsloth/gemma-3-4b-it-GGUF` (4 GB) — in-app "suggested correction"
- `unsloth/gemma-4-26B-A4B-it-GGUF` (14 GB MoE) — in-app "explain why
  this is mis-categorised"

Both are served by the llama-swap service at
`http://llama-swap:8080/v1/chat/completions` per
`cianfhoghlaim/ocr/models/llama_swap_config.yaml`.
