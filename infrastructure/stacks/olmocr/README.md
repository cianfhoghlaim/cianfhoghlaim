# OLMOCR — MLX-Accelerated OCR for Exam Papers

## Overview

OLMOCR (Open Language Model OCR) is a server that exposes MLX-format OCR models as an OpenAI-compatible API. It runs specialised OCR models — trained to recognise text in scanned documents, handwritten notes, and complex layouts — on Apple Silicon via MLX acceleration.

## Why This Matters for Kings' College Galway

State Examination Commission (SEC) exam papers from older years (pre-2010) are scanned images, not born-digital PDFs. Traditional OCR engines (Tesseract) struggle with the mathematical notation, Irish language diacritics, and mixed-language content in these scans. OLMOCR's MLX models are specifically trained on document OCR and handle mathematical equations, Irish fada characters, and English/Irish mixed text far more accurately. This is the first step in the exam paper pipeline — if the OCR is wrong, every downstream extraction (BAML, embeddings, RAGAS) inherits the error.

## Key Features

- **MLX-native** — Optimised for Apple Silicon unified memory
- **OpenAI-compatible API** — Drop-in with any OpenAI SDK client
- **Math-aware OCR** — Recognises equations, Greek letters, and mathematical notation
- **Multi-language** — Handles Irish diacritics and mixed-language documents
- **GGUF fallback** — Also available as a GGUF model via llama-swap

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/olmocr
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on bunchloch (MacBook M4). The `ocr` LiteLLM alias routes to this service as the first choice, falling back to DeepSeek-OCR GGUF and then Gemini Flash.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `OLMOCR_PORT` | No | API port | `8000` |
| `OLMOCR_MODEL` | No | Model path | `/models/olmocr-mlx` |
| `MLX_METAL_DEVICE` | No | Metal device ID | `0` |

## Access

- **API**: `http://localhost:8000/v1` (OpenAI-compatible)
- **Auth**: Internal-only

## Upstream

- **Repository**: <https://github.com/vikhyat/olmocr>
- **Latest**: Active development — MLX backend, improved math OCR, batch processing support

## Screenshot

Headless HTTP API. The OpenAI-compatible endpoint at `/v1/chat/completions` accepts images and returns structured text. The LiteLLM gateway routes the `ocr` alias to this service. Output quality is measured by downstream RAGAS evaluation — OCR accuracy directly correlates with extraction faithfulness scores.
