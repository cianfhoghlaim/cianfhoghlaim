---
title: "Build Small 2026 — Model Fallback Chains"
domain: hackathons
status: draft
description: "LiteLLM-equivalent model fallback chains for each role in the 4 Hackathon Spaces. All models ≤ 32B. Primary: HF Inference (cloud). Fallback: bundled GGUF Q4_K_M. The Spaces are hosted on HuggingFace Spaces; the BAML clients are re-pointed to HF Inference per the locked hybrid strategy (2026-06-08)."
entities:
  - HFInference
  - LiteLLM
  - Qwen25
  - Llama31
  - Gemma2
  - BGE-M3
  - BriaFIBO
  - BuildSmall2026
related_skills:
  - .agents/skills/dlt/SKILL.md
  - .agents/skills/dagster/SKILL.md
ccc_query_hints:
  - "litellm fallback chain HF Inference"
  - "32B model route BAML extraction"
  - "GGUF bundled Q4_K_M Space"
  - "OCR VLM fallback chain"
  - "Celtic language model fallback"
last_reviewed: 2026-06-08
---

# Build Small 2026 — Model Fallback Chains

> Per the locked hybrid strategy (2026-06-08):
> - **Chat / NPC dialogue** → HF Inference (no local infra)
> - **BAML extraction** → BAML-compatible cloud model (no LiteLLM tunnel needed)
> - **Image gen (FIBO substitute)** → HF Inference hosted models
> - **Embeddings** → HF feature-extraction endpoint
> - **Anvil sidecar** (Space 4) → CuchulainnNFT.sol mounted locally, no chain needed
> - **Infrastructure archived** — no Pangolin, no Pocket ID, no Locket
> - **All models ≤ 32B** to satisfy the hackathon constraint

---

## 0. Naming convention

Each fallback chain has:
- **Primary** (HF Inference, cloud-hosted)
- **Fallback 1** (same family, smaller / faster)
- **Fallback 2** (cross-family, last resort)
- A short **justification** for why the model is in this slot

All models are ≤ 32B and on the HF Inference tier.

---

## 1. BAML extraction (used by Spaces 1, 2, 3, 4)

Used by:
- Space 1 (An Scrúdú): `ExtractCurriculumSyllabus`, `ExtractPastPaper`, `ExtractMarkingScheme`, `ExtractLeavingCertSyllabus`, the new `ExtractCircularMeta`, `GenerateExitCardQuestions`, `ScoreExitCardResponse`, `ComposeMarkingSchemeDiff`
- Space 2 (Meaisín Cliste): `CompareCurricula`, `GenerateAssessment`, `AnalyzePlayerResponse`, the new `CrossBorderAlignment`, `TerminologueEntry`
- Space 3 (Cianfhoghlaim): `MythologicalCharacter`, `MythologicalStory`, `GenerateNPCDialogue`, the new `ExtractWikipediaArticle`, `EvaluateRiddleResponse`
- Space 4 (Anam: Tuatha na nGaelscoil): all of the above

| Slot | Model | Provider | Size | Justification |
|:--|:--|:--|:--|:--|
| Primary | `Qwen/Qwen2.5-7B-Instruct` | HF Inference | 7B | Strong JSON schema adherence; well-known BAML-friendly; multilingual including 30+ languages; reliable on HF Inference tier |
| Fallback 1 | `meta-llama/Llama-3.1-8B-Instruct` | HF Inference | 8B | Best-in-class instruction following; widely deployed on HF Inference; good BAML compliance; explicit function-calling support |
| Fallback 2 | `google/gemma-2-9b-it` | HF Inference | 9B | Gemma 2 strong on structured output; long context (8K → 1M with Gemma 2); good fallback when Qwen/Llama quota exceeded |

**Hackathon client config** (`sruth/tuatha/baml_src/clients_hackathon.baml` — fork of `tuatha_clients.baml`):

```baml
client<BAML_HACKATHON_PRIMARY> {
  provider openai-generic
  base_url "https://api-inference.huggingface.co/v1"
  api_key env.HF_TOKEN
  model "Qwen/Qwen2.5-7B-Instruct"
  max_tokens 4096
  temperature 0.0
  retry_policy {
    max_retries 3
    initial_delay_ms 200
    backoff_factor 2.0
  }
}

client<BAML_HACKATHON_FALLBACK_1> {
  provider openai-generic
  base_url "https://api-inference.huggingface.co/v1"
  api_key env.HF_TOKEN
  model "meta-llama/Llama-3.1-8B-Instruct"
  max_tokens 4096
  temperature 0.0
}

client<BAML_HACKATHON_FALLBACK_2> {
  provider openai-generic
  base_url "https://api-inference.huggingface.co/v1"
  api_key env.HF_TOKEN
  model "google/gemma-2-9b-it"
  max_tokens 4096
  temperature 0.0
}
```

BAML function routing:
```baml
function ExtractCurriculumSyllabus(pdf_text: string) -> CurriculumExtraction {
  client BAML_HACKATHON_PRIMARY
  // BAML compiler will auto-fallback to BAML_HACKATHON_FALLBACK_1, then _2
  // on any of: timeout, schema validation failure, rate limit, 5xx
  ...
}
```

---

## 2. Chat / NPC dialogue (used by Spaces 3, 4)

Used by:
- Space 3 (Cianfhoghlaim): the 6 NPC dialogue trees (Uí Liatháin lord, Brec/Óengus, Manannán, Rhiannon, Dian Cécht, Cian) — level-gated via `player_assessment.baml:GenerateNPCDialogue`
- Space 4 (Anam: Tuatha na nGaelscoil): the integrated "Tri-Naomh" persona switcher (An Scrúdaí / An Teangeolaí / An Gaiscíoch) — actually dropped in favour of the 5-element framework per re-themes

| Slot | Model | Provider | Size | Justification |
|:--|:--|:--|:--|:--|
| Primary | `meta-llama/Llama-3.1-8B-Instruct` | HF Inference | 8B | Best-in-class chat; BAML function-calling support; 128K context window accommodates long NPC monologues |
| Fallback 1 | `mistralai/Mistral-7B-Instruct-v0.3` | HF Inference | 7B | Strong on creative writing; well-tuned for character voice; robust on poetry and verse (relevant for BAML `celtic_text` fields) |
| Fallback 2 | `Qwen/Qwen2.5-7B-Instruct` | HF Inference | 7B | Multilingual including 30+ languages; reliable on HF Inference; good fallback when Mistral quota exceeded |

---

## 3. OCR / VLM (used by Spaces 2, 4)

Used by:
- Space 2 (Meaisín Cliste, OCR race mode in Foclóir na Sé Náisiún): 10-model parallel OCR competition, ranked by gaelic_metrics.py (fada, tironian, punctum delens)
- Space 4 (Anam: Tuatha na nGaelscoil, Tine feature): single OCR model for exam paper transformer pipeline

| Slot | Model | Provider | Size | Justification |
|:--|:--|:--|:--|:--|
| Primary | `Qwen/Qwen2-VL-7B-Instruct` | HF Inference | 7B | Strong multilingual OCR; excellent on handwritten text; native support for Qwen2.5 ecosystem; widely available on HF Inference |
| Fallback 1 | `microsoft/Phi-3.5-vision-instruct` | HF Inference | 4.2B | Microsoft's strongest small VLM; excellent document understanding; good fallback when Qwen-VL quota exceeded |
| Fallback 2 | `google/paligemma-3b-mix-448` | HF Inference | 3B | Lightest viable VLM; 448-resolution sweet spot; last-resort fallback; cost-optimised |

**For Space 4's Tine feature (the single OCR model path)**, prefer `Qwen/Qwen2-VL-7B-Instruct` as the primary. The 10-model OCR race from `meaisínfhoghlaim/ocr/model_registry.py:330-543` is *not* used in the Space itself (the race is a research harness); the Space calls a single model via HF Inference.

---

## 4. Image generation (FIBO substitute) (used by Space 4)

Used by:
- Space 4 (Anam: Tuatha na nGaelscoil, Uisce feature): chemistry/biology visual asset generation (flame tests, titration endpoints, molecular geometry, with PPE safety in negative prompts)
- Space 4 (Anam: Tuatha na nGaelscoil, Anam feature): the on-chain SVG for the Anam SBT (deterministic Celtic-knot SVG)

**Note:** Bria FIBO does not have a public HF Inference endpoint in time for the hackathon. SDXL and FLUX are the substitutes.

| Slot | Model | Provider | Size | Justification |
|:--|:--|:--|:--|:--|
| Primary | `stabilityai/stable-diffusion-xl-base-1.0` | HF Inference | 2.6B (base + refiner) | Most battle-tested image gen; reliable on HF Inference; good for chemistry diagram-style prompts |
| Fallback 1 | `black-forest-labs/FLUX.1-schnell` | HF Inference | 12B (distilled) | Schnell (fast) variant for lower latency; high quality; good for educational visual gen |

**For the Anam SBT SVG (Space 4, Anam feature):** generated client-side via Python's `svgwrite` library (deterministic from a hash of the credential JSON-LD). No model call needed.

---

## 5. Embeddings (used by Spaces 1, 2, 3, 4)

Used by:
- Space 1 (An Scrúdú): curriculum vector search, marking-scheme similarity
- Space 2 (Meaisín Cliste): RAG-powered vocabulary tutoring, cross-curriculum Q&A
- Space 3 (Cianfhoghlaim): mythology extraction, NPC dialogue context
- Space 4 (Anam: Tuatha na nGaelscoil): unified search across all 4 Spaces

| Slot | Model | Provider | Size | Justification |
|:--|:--|:--|:--|:--|
| Primary | `BAAI/bge-m3` | HF feature-extraction | 568M | Multilingual (100+ languages including Irish); 1024-dim; strong on technical/educational content; native LanceDB integration |
| Fallback 1 | `sentence-transformers/all-MiniLM-L6-v2` | HF feature-extraction | 22M | Lightest viable embedding; 384-dim; ultra-fast; widely cached on HF Inference |

**LanceDB schema:** all 4 Spaces use the same `BGE_M3_EMBEDDING` table with 1024-dim vectors. Fallback to `all-MiniLM-L6-v2` at 384-dim is acceptable for Space 2's Foclóir (small corpus) but NOT for Space 1's curriculum (large corpus, dimensional mismatch requires re-index).

---

## 6. Speech recognition (Whisper) (used by Space 2)

Used by:
- Space 2 (Meaisín Cliste, Aer theme, G2P Playground): user speaks Irish; Whisper transcribes
- Space 2 (Meaisín Cliste, Aer theme, Voice Pipeline feature): full ASR → LLM → TTS loop

| Slot | Model | Provider | Size | Justification |
|:--|:--|:--|:--|:--|
| Primary | `openai/whisper-large-v3` | HF Inference | 1.5B | Best-in-class multilingual ASR; 99 languages including Irish; reliable on HF Inference |
| Fallback 1 | `openai/whisper-large-v3-turbo` | HF Inference | 809M | Distilled variant; 6× faster; minimal quality loss; good for real-time voice pipeline |

**For the G2P Playground (Space 2, Aer):** user input is Irish, so `whisper-large-v3` is preferred (better Irish accuracy). For the real-time voice pipeline, `whisper-large-v3-turbo` (latency matters more than absolute accuracy).

---

## 7. Text-to-speech (TTS) (used by Space 2)

Used by:
- Space 2 (Meaisín Cliste, Aer theme, G2P Playground): plays the G2P IPA in 3 dialects (Connacht / Munster / Ulster)
- Space 2 (Meaisín Cliste, Aer theme, Voice Pipeline feature): speaks the LLM response back in Irish

| Slot | Model | Provider | Size | Justification |
|:--|:--|:--|:--|:--|
| Primary | `ResembleAI/chatterbox` | HF Inference | ~500M | Strong multilingual TTS; supports voice cloning for the 6 NPC voices; widely available |
| Fallback 1 | `facebook/mms-tts-ga` | HF Inference | ~300M | Meta's Massively Multilingual Speech model with explicit Irish (`ga`) support; best fallback for Irish TTS |

**For Irish G2P playback (Space 2, Aer):** prefer `facebook/mms-tts-ga` (explicit Irish) over `chatterbox` (multilingual but no explicit Irish quality guarantee).

---

## 8. Anam SBT mounter (Space 4, Anam feature)

**Anvil sidecar (bundled Docker image):**
- Container: `ghcr.io/foundry-rs/foundry:latest` (Anvil)
- Solidity contract: `CuchulainnNFT.sol` from `sruth/tuatha/apps/crypteolas_demo/anam-contracts/src/CuchulainnNFT.sol`
- Mount path: `/app/contracts/CuchulainnNFT.sol`
- Anvil RPC: `http://anvil:8545` (from the Space's Gradio backend)
- Deploy script: `forge script script/DeployCuchulainnNFT.s.sol --rpc-url http://anvil:8545 --broadcast`

**The 5-element SBT system** (from `CuchulainnNFT.sol:162-168`):
- Knowledge (Talamh, emerald)
- Skill (Uisce, azure)
- Creativity (Tine, amber)
- Community (Aer, indigo)
- Sovereignty (Anam, gold)

Each SBT has:
- `stage`: Sétanta → Cúchulainn → Ríastrad (from `CuchulainnNFT.sol:142-146`)
- `knotComplexity`: simple → medium → complex (from `CuchulainnNFT.sol:179`)
- `element`: one of the 5 above
- `tokenURI`: base64-encoded on-chain SVG (from `CuchulainnNFT.sol:208-231`)

---

## 9. LiteLLM gateway aliases (re-pointed for the hackathon)

The existing `infrastructure/stacks/litellm/config/config.yaml` aliases are re-pointed for the hackathon to use HF Inference as the primary backend (no local LiteLLM gateway). The aliases are kept for documentation purposes.

| Alias | Old primary (local) | New primary (HF Inference) | Use |
|:--|:--|:--|:--|
| `extract` | `gemini-2.5-pro` (cloud) | `Qwen/Qwen2.5-7B-Instruct` (HF Inference) | BAML extraction (all 4 Spaces) |
| `irish` | `uccix-llama2-13b` (GGUF) | `Qwen/Qwen2.5-7B-Instruct` (HF Inference) | Irish generation |
| `math` | `qwen2.5-math-7b` (GGUF) | `Qwen/Qwen2.5-Math-7B-Instruct` (HF Inference) | Math reasoning |
| `ocr` | `olmocr-2-7b-mlx` (MLX) | `Qwen/Qwen2-VL-7B-Instruct` (HF Inference) | OCR (Space 4 Tine) |
| `vision` | `qwen2.5-vl-7b` (GGUF) | `Qwen/Qwen2-VL-7B-Instruct` (HF Inference) | Vision (Space 2) |
| `document` | `granite-docling` (MLX) | `Qwen/Qwen2-VL-7B-Instruct` (HF Inference) | Document understanding |
| `image` | `z-image-turbo` (GGUF) | `stabilityai/stable-diffusion-xl-base-1.0` (HF Inference) | FIBO substitute |
| `embedding` | `bge-m3` (HF passthrough) | `BAAI/bge-m3` (HF feature-extraction) | Embeddings (all 4 Spaces) |
| `embedding-curriculum` | `BAAI/bge-m3` (HF passthrough) | `BAAI/bge-m3` (HF feature-extraction) | Curriculum embeddings (Space 1) |
| `general` | `opencode-go/deepseek-v4-flash` | `meta-llama/Llama-3.1-8B-Instruct` (HF Inference) | General chat (Space 4) |
| `whisper-irish` | `celtic/asr/wav2vec2-irish` | `openai/whisper-large-v3` (HF Inference) | Irish ASR (Space 2) |
| `chatterbox` | `ResembleAI/chatterbox` | `ResembleAI/chatterbox` (HF Inference) | TTS (Space 2) |

**Hackathon config file:** `infrastructure/stacks/litellm/config_hackathon.yaml` — frozen snapshot for documentation, not deployed.

---

## 10. HF Inference token management

The hackathon uses **one HF account token** (the user's personal account), provisioned via HuggingFace Spaces secrets:

- `HF_TOKEN` — primary auth token, scope: `inference-api`, `read`
- `HF_TOKEN_BACKUP` — backup token, scope: same, for failover (optional)

**Cost estimate (8-day hackathon):**
- BAML extraction (4 Spaces): ~50K requests × 2K tokens average = 100M tokens = ~$0.50
- Chat / NPC dialogue (Spaces 3+4): ~10K requests × 1K tokens = 10M tokens = ~$0.05
- OCR / VLM (Spaces 2+4): ~5K requests × 1.5K tokens = 7.5M tokens = ~$0.40
- Image gen (Space 4): ~500 images = ~$2.00
- Embeddings (all 4 Spaces): ~1M documents × 1024-dim = 1B tokens = ~$0.10
- Speech (Space 2): ~100 audio minutes = ~$0.50

**Total estimate: ~$3.55** (well within free tier + trial credits).

---

## 11. Fallback chain decision tree

When a BAML extraction or chat request fails:

```
1. Try BAML_HACKATHON_PRIMARY (Qwen2.5-7B)
   ├─ Success → return response
   └─ Failure:
       2. Try BAML_HACKATHON_FALLBACK_1 (Llama-3.1-8B)
          ├─ Success → return response
          └─ Failure:
              3. Try BAML_HACKATHON_FALLBACK_2 (Gemma-2-9B)
                 ├─ Success → return response
                 └─ Failure:
                     4. Return cached response (if any, from prior session)
                        └─ If no cache:
                            5. Return 502 + graceful error to Gradio frontend
                               (frontend shows "Try again" button, no crash)
```

BAML's built-in retry + fallback is configured in `clients_hackathon.baml`. The cascade is automatic.

---

## 12. Off-the-Grid badge (Space 4 only, optional)

If the user wants the **Off the Grid bonus quest badge** on Space 4, the BAML clients can be re-pointed to a **bundled GGUF Q4_K_M Qwen2.5-7B** served via `llama.cpp` running inside the Space's Docker image. This requires:
- A 5GB GGUF file in the Space's repo
- A `llama-cpp-python` Python wrapper
- A modified BAML client pointing at `http://localhost:8080/v1`

**Trade-off:** +5GB in the Space, 2-3× slower inference, but completely offline. Decided NOT to include by default (the Spaces are small and fast on HF Inference). If the badge is needed, see `meaisínfhoghlaim/llama-swap-config.yaml` for the GGUF model list.

---

## 13. What is NOT in scope (architectural decisions locked 2026-06-08)

- **No local LiteLLM gateway** — Spaces call HF Inference directly.
- **No Pocket ID / Pangolin / Traefik / WireGuard** — the infrastructure quadrant is archived for this hackathon.
- **No Locket sidecar** — secrets are in HF Space secrets manager.
- **No x402 micropayments** — Anam SBTs are mounted on local Anvil (no real chain, no gas).
- **No Pipecat voice agent** — replaced with HF Inference Whisper + MMS-TTS for Space 2.
- **No real SpacetimeDB game server** — Space 3's Babylon.js scene runs locally; no real-time multiplayer (out of scope for the hackathon).

---

*End of model fallback doc. Approve and exit plan mode when ready; 2 file writes pending (OpenSpec change bundle, plan patch).*
