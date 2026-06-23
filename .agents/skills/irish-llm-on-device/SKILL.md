---
name: irish-llm-on-device
description: On-device Celtic LLM + on-device OCR / HTR + Celtic fine-tuning for Apple Silicon. Covers MLX + llama.cpp + AnyLanguageModel inference; Unsloth + GGUF quantisation; ColPali + weak-supervision for Gaelic handwriting alignment; Qwen2-VL / Qwen3-VL fine-tuning; ASR / TTS corpus scraping (Teanglann, Canúint, Dúchas). Use when running a Celtic model locally on the M4 MacBook or on iPhone, fine-tuning Qwen-VL on a Gaelic manuscript, scraping a dialectal audio corpus, quantising a model to GGUF for llama.cpp, deploying a Swift Transformers iOS app, or asking "how does an Irish LLM get on an iPhone?".
---

# Irish LLM on Apple Silicon (on-device)

## When to use this skill

Use when you need to:

- "Run a Celtic LLM on the M4 MacBook or on iPhone"
- "Quantise a model to GGUF for llama.cpp"
- "Fine-tune Qwen2-VL or Qwen3-VL on a Gaelic manuscript"
- "Align handwriting to a VLM with ColPali (weak supervision)"
- "Scrape Teanglann or Canúint for dialectal ASR / TTS data"
- "Deploy an Irish HTR app on iPadOS (Apple Pencil)"
- "Wire AnyLanguageModel for unified Apple-platform inference"
- "Wire Swift Transformers 1.0 in an iOS / macOS app"
- "Train a ColPali-style visual retriever for handwritten Irish"

## Overview

The Irish LLM on-device skill is the **Celtic-language
counterpart of `kcg-ml-models`**, narrowed to Apple Silicon
+ on-device OCR / HTR. It covers four intertwined topics:

1. **Inference backends** — MLX (Apple's native array
   framework), llama.cpp (the GGUF runtime), and
   AnyLanguageModel (Apple's unified Swift API).
2. **Quantisation + fine-tuning** — Unsloth (for LoRA /
   QLoRA fine-tuning) + GGUF export (for llama.cpp).
3. **Vision-language fine-tuning** — Qwen2-VL + Qwen3-VL
   fine-tuning on Gaelic manuscripts, ColPali + weak
   supervision for bounding-box alignment.
4. **Corpus scraping** — Teanglann (pronunciation audio) +
   Canúint (dialectal audio) + Dúchas (handwritten archive) +
   DU Gaois (bilingual dataset registry).

The same four topics are sequenced in the on-device LLM
playbook: scrape the corpus, fine-tune a VLM with the
handwritten samples, quantise the result to GGUF, ship it
on-device via MLX (M4) or llama.cpp (iPhone).

## The 4 inference backends

| Backend | Run-time | Best for | Where it ships |
|:--|:--|:--|:--|
| **MLX** (`mlx-omni-server`) | Native Apple Silicon | M4 MacBook, MLX-LM / MLX-VLM, GGUF + safetensors | `bunchloch` M4 Max |
| **llama.cpp** (via `llama-swap`) | GGUF runtime | iPhone, iPad, Raspberry Pi, GGUF quantised models | iOS app, `bunchloch` |
| **AnyLanguageModel** | Swift API | Unified Apple-platform inference (macOS / iOS / visionOS) | iOS / macOS apps |
| **Swift Transformers 1.0** | Pure Swift | On-device transformers in Swift (no Python) | iOS / macOS apps |

The M4 Max `bunchloch` host serves all 3 server-side
backends (llama-swap :8080, mlx-omni-server :10240,
invokeai :9090). The client-side iOS apps use llama.cpp +
AnyLanguageModel + Swift Transformers 1.0.

```
                ┌────────────────────────────────────┐
                │       Apple Silicon (M4 / A18)     │
                ├────────────────────────────────────┤
                │                                    │
                │   Server-side (bunchloch M4 Max)   │
                │   ─ llama-swap :8080 (GGUF)        │
                │   ─ mlx-omni-server :10240 (MLX)   │
                │   ─ invokeai :9090 (safetensors)   │
                │                                    │
                │   Client-side (iOS / iPadOS)       │
                │   ─ llama.cpp (GGUF)               │
                │   ─ AnyLanguageModel (Swift)       │
                │   ─ Swift Transformers 1.0         │
                │                                    │
                └────────────────────────────────────┘
```

## The fine-tuning pipeline

```
┌────────────────────────────────────────────────────────────────────┐
│                  IRISH LLM ON-DEVICE PIPELINE                     │
└────────────────────────────────────────────────────────────────────┘

[1] Corpus scrape
    Teanglann (audio) + Canúint (dialectal) + Dúchas (manuscripts)
    + DCU Gaois (bilingual dataset registry)
    ↓
[2] Pre-processing
    yt-dlp (if video) + WhisperX (transcribe) + Docling (PDF)
    + ColPali (visual embeddings of handwriting)
    ↓
[3] Alignment (weak supervision)
    ColPali page-level embeddings + Qwen2-VL bounding-box head
    + IoU loss (weakly-supervised)
    ↓
[4] Fine-tune
    Unsloth + LoRA / QLoRA + PEFT + TRL
    on Qwen2-VL or Qwen3-VL (or MLX-VLM for native Apple)
    ↓
[5] Quantise
    llama.cpp `convert.py` → GGUF Q4_K_M
    (or MLX `mlx_lm.quantize` for native Apple)
    ↓
[6] Ship on-device
    iOS app embeds GGUF in the bundle
    + llama.cpp C++ runtime + AnyLanguageModel Swift wrapper
```

The same pipeline appears (in slightly different forms) in
3 KCG skills: `celtic-asset-generation` (the curriculum
side), `kcg-ml-models` (the model-fallback side), and this
skill (the Apple Silicon / on-device side).

## The vision-language fine-tuning stack

| Tool | Role | Why |
|:--|:--|:--|
| **ColPali** | Visual retriever (page-level embeddings) | "What does a manuscript page look like?" |
| **Qwen2-VL / Qwen3-VL** | VLM backbone (NaViT, dynamic resolution) | Native bilingual (en + zh) + Irish fine-tunes well |
| **Unsloth** | LoRA / QLoRA wrapper | 70% VRAM reduction, 2× speedup |
| **PEFT** | LoRA / QLoRA primitives | Unsloth sits on top of PEFT |
| **TRL** | SFTTrainer + DPOTrainer + GRPOTrainer | Fine-tuning + preference optimisation |
| **MLflow** | Experiment tracking | Loss curves, hyperparams, model registry |
| **Ragas** | RAG evaluation | Faithfulness + answer relevance for the trained model |

The "weakly-supervised" pattern: ColPali produces page-level
embeddings; Qwen2-VL produces token-level bounding-box
predictions; an IoU loss is computed between ColPali's
visual page coverage and Qwen's token boxes. The result is a
Gaelic manuscript alignment model with no manual box labels
(see `references/colpali-qwenvl-gaelic-alignment.md`).

## The corpus scrape stack

| Source | Content | Use case |
|:--|:--|:--|
| **Teanglann** (teanglann.ie) | Pronunciation audio for Irish + Scottish Gaelic + Welsh + Manx + Cornish + Breton | TTS / ASR training, pronunciation guides |
| **Canúint** (canuint.ie) | Dialectal audio with geo metadata | Dialect-aware ASR, Ulster / Connacht / Munster balance |
| **Dúchas** (duchas.ie) | Handwritten Irish manuscripts + folklore | HTR training, handwriting generation |
| **DCU Gaois** (gaois.ie) | Bilingual dataset registry | Dataset acquisition, legal/licensing metadata |
| **NDLR** (ncca.ie) | Recorded Leaving Cert oral exams | ASR training, oral exam grading |
| **TG4** (tg4.ie) | Irish-language broadcast archive | Conversational ASR, dialect coverage |

The scrape uses Skyvern + an LLM agent for JS-heavy sites
(see `references/skyvern-celtic-scrape.md` from
`celtic-asset-generation`); for static pages, plain `dlt`
filesystem + crawl4ai is enough.

## The on-device HTR / OCR stack

| Tool | Run-time | Use case |
|:--|:--|:--|
| **Qwen2-VL** fine-tuned | MLX (M4) or llama.cpp (iPhone) | iPadOS handwritten-Irish capture with Apple Pencil |
| **ColPali** | MLX (M4) or PyTorch (server) | Visual retriever over the manuscript page |
| **Docling** | Server-side (Dagster) | PDF → structured markdown for the manuscript |
| **DeepSeek-Math** | MLX (M4) | Math HTR (LaTeX recognition in handwritten Irish maths) |
| **Granite-Docling** | Server-side (Dagster) | Table extraction in manuscripts |

The iPadOS handwriting app uses **Apple Pencil** capture →
**Qwen2-VL** (quantised GGUF, running on-device via
llama.cpp) → structured JSON → **Swift Transformers 1.0**
for the UI feedback loop. The full architecture is in
`references/irish-htr-mlx-pencil.md`.

## Model fallback chain (on-device)

```yaml
# KCG production rule: never let a single model fail.
vision_on_device: mlx-vlm (Qwen2-VL) → llama.cpp (Qwen2-VL)
asr_on_device:     whisper.cpp (faster-whisper) → wav2vec2.cpp
tts_on_device:     piper (native) → MMS-TTS
embeddings_on_device: MLXEmbedders (BGE-M3) → CoreML (BGE-M3)
```

The fallback is **per-call**, not per-session. The
LiteLLM-equivalent for Apple is **AnyLanguageModel**, which
unifies the 3 backends behind a single Swift API.

## KCG integration

- `oideachais/baml_src/celtic_linguistics.baml` — the
  BAML schema for Irish grammar extraction (the target of
  the fine-tuned model).
- `oideachais/baml_src/celtic_sources.baml` — the
  BAML schema for source attribution.
- `meaisinfhoghlaim/language/gaeilge/` — the Irish-language
  subdir (corpus, lexicons, cognates).
- `meaisinfhoghlaim/dagster_assets/ocr_htr.py` — the
  Dagster assets for OCR / HTR.
- `infrastructure/bunchloch/llama-swap/` — the llama-swap
  service that serves GGUF on the M4.
- `infrastructure/bunchloch/mlx-omni-server/` — the
  MLX server (Apple's native array framework).

## References (in this skill)

- `references/irish-llm-unsloth-ios.md` — Unsloth + Qomhrá +
  UCCIX iOS deployment (canonical).
- `references/irish-llm-ios-unsloth.md` — same content
  (teanga alt copy).
- `references/irish-htr-mlx-pencil.md` — MLX + Apple Pencil
  Irish HTR iPadOS (canonical).
- `references/irish-handwriting-mlx.md` — same content
  (teanga alt copy).
- `references/celtic-ocr-colpali-unsloth.md` — bilingual iOS
  HTR (canonical).
- `references/ios-bilingual-htr.md` — same content (teanga
  alt copy).
- `references/qwen-vl-celtic-ocr.md` — Qwen2-VL / Qwen3-VL
  fine-tuning on Celtic HTR (canonical).
- `references/qwen3-vl-gaelic-finetuning.md` — NaViT + MLflow
  + Ragas Qwen3-VL Gaelic fine-tuning.
- `references/colpali-qwenvl-gaelic-alignment.md` —
  weakly-supervised bounding-box via ColPali for Qwen2-VL
  fine-tuning.
- `references/duchas-qwen-vl-htr.md` — Dúchas + ColPali +
  Docling + DeepSeek-Math heritage HTR.
- `references/teanglann-canuint-audio-scrape.md` — Teanglann
  + Canúint dialectal ASR corpus extraction.
- `references/clippings/anylanguagemodel-apple.md` —
  AnyLanguageModel Apple SDK.
- `references/clippings/fastvlm-apple-cvpr-2025.md` —
  FastVLM Apple CVPR 2025.
- `references/clippings/swift-transformers-1-0.md` — Swift
  Transformers 1.0.
- `references/clippings/unsloth-model-catalog.md` — Unsloth
  model catalog.

## Cross-references

- `.agents/skills/kcg-ml-models/SKILL.md` — the 70+ model
  registry (the server-side counterpart).
- `.agents/skills/unsloth/SKILL.md` — the Unsloth wrapper
  (LoRA / QLoRA / 70% VRAM reduction).
- `.agents/skills/trl/SKILL.md` — TRL fine-tuning
  (SFTTrainer + DPOTrainer + GRPOTrainer).
- `.agents/skills/peft/SKILL.md` — PEFT LoRA / QLoRA
  primitives.
- `.agents/skills/embedding-pipeline/SKILL.md` — the BGE-M3
  + CocoIndex embedding rules.
- `.agents/skills/tts/SKILL.md` — the TTS stack
  (Chatterbox / MMS-TTS / Piper).
- `.agents/skills/asr/SKILL.md` — the ASR stack
  (wav2vec2-XLSR-Irish / Whisper / MMS).
- `.agents/skills/celtic-language-ai/SKILL.md` — the 6
  Celtic languages + curated model catalog.
- `.agents/skills/irish-edtech/SKILL.md` — the Irish-only
  comprehensive reference (Qwen2.5-Math + 7-tier Bardic
  grade progression).
- `.agents/skills/celtic-asset-generation/SKILL.md` — the
  asset-generation side (BAML / CocoIndex / Cognee).
- `infrastructure/bunchloch/llama-swap/` — the llama-swap
  service on the M4.
- `infrastructure/bunchloch/mlx-omni-server/` — the MLX
  service on the M4.
