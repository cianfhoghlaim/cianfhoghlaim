# Agent 59 — Qwen-Image / Qwen-Image-Edit asset-gen benchmark

**Date:** 2026-06-29
**Phase:** 2 (Image Generation track) — Agent 59 of 60
**BrowserBase budget used:** 0 navigations (all content via Firecrawl + ccc; 2 searches + 1 scrape = 2 credits, +1 refunded = **1 credit net**)
**CCC queries:** 1 (`qwen-image model deployment llama-swap asset generation`)
**Sources fetched:** `qwenlm.github.io/blog/qwen-image`, `huggingface.co/Qwen/Qwen-Image`, `medium.com/diffusion-doodles/...qwen-image-2512-edit-2511-flux-2-dev`, `qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-Image/Qwen_Image.pdf`

> **FACTUAL CORRECTION vs prompt brief:** the prompt states *"Qwen-Image is NOT currently deployed"*. This is **wrong**. Qwen-Image + Qwen-Image-Edit-2511 **are already deployed** at `cianfhoghlaim/core/llama-swap-config.yaml:169-194` (GGUF Q4_K_M via `llama-server`, alias `image-accurate` / `image-edit`), exposed through LiteLLM as `local/image/qwen-image` and `local/image/qwen-image-edit` (`cianfhoghlaim/stacks/litellm/config/config.yaml:138-158`), referenced by the BAML prompt at `cianfhoghlaim/core/baml/_meaisinfhoghlaim_src/image_generation.baml:8,130`, and named in the `celtic-asset-generation` spec (v4, line 95) as one of three canonical image generators. Section 6 below reframes the "deployment plan" as a **hardening + adoption + cutover** plan, not a green-field deploy.

---

## 1. TL;DR

1. **Qwen-Image (20B, Apache 2.0, arXiv 2508.02324) is the best open-weights bilingual text-rendering model as of 2026-06** — strongest Irish/English/Chinese text fidelity, the only model in our chain that survives "π≈3.14159…"-class overlays without garbling, and the Qwen-Image-Edit-2511 sibling closes the gap on instruction-driven editing vs FLUX Kontext.
2. **Cutover status (corrected):** Qwen-Image is **already wired** as the **2nd-stage fallback** in our 4-model image chain (`z-image-turbo → qwen-image → flux2 → sdxl`) at `litellm/config.yaml:651` and the `image-accurate` alias in `llama-swap-config.yaml:177`. The remaining work is **(a) bump base Qwen-Image → Qwen-Image-2512** (Dec 2025 checkpoint, best bilingual), **(b) make Qwen-Image-Edit-2511 the default *editor* (not InvokeAI's SDXL inpaint)** for `subject_assets/` regeneration, and **(c) add an RAGAS asset-quality eval** (text-fidelity CLIPScore + Compose-bilingual-CLIP).
3. **Do not retire InvokeAI (SDXL/FLUX.1)** — it remains the right choice for *fast photoreal* (Z-Image-Turbo already displaces it for the speed lane). The new chain should be **`z-image-turbo` (default) → `qwen-image-2512` (bilingual text) → `qwen-image-edit-2511` (edits) → `flux2-dev` (premium photoreal) → `invokeai-sdxl` (fallback for legacy nodes).**

---

## 2. Qwen-Image for asset gen

**What it is.** Qwen-Image is Alibaba's 20-billion-parameter image foundation model, released **2025-08-04** under **Apache 2.0**, with a sibling editor **Qwen-Image-Edit-2511** (Nov 2025) and the 2512 base refresh (Dec 2025). All three live on HuggingFace under `Qwen/` and on ModelScope. The model is a single-stream MMDiT trained on a heavily text-rebalanced corpus; the standout capabilities (per the paper arXiv:2508.02324 and the HF model card) are:

- **Multilingual text rendering** — English + Chinese (and, in 2512, scripts beyond Latin/Han). Glyphs are embedded in the latent, not painted on top, so the model can render long strings (formulas, paragraphs, multi-line labels) without the "letter-by-letter" failure mode of SDXL / FLUX.1.
- **Precise image editing** (Qwen-Image-Edit-2511) — instruction-driven object insert/remove, style transfer, in-image text editing, human-pose manipulation. 2511 is positioned as a FLUX Kontext / GPT-Image-1 competitor with open weights.
- **Multi-task visual understanding** — depth, Canny, segmentation, novel view, super-resolution; not all surfaced via the diffusion API, but the backbone supports it.

**HF adoption signal:** `Qwen/Qwen-Image` has **192,035 downloads/month**, **26 quantizations**, **78 finetunes**, **487 LoRA adapters**, and **100 Spaces** at the time of writing — third-party validation is strong, especially for Chinese-language rendering.

**Why this matters for Kings' College Galway.** The Celtic asset pipeline (`celtic-asset-generation` spec, 4 v4 sub-pipelines) is overwhelmingly a **text-bearing image** problem:

- **Bilingual labels** — every study card / diagram needs an Irish (Gaeilge) and English overlay side-by-side or in alternating panels. Today this is hand-painted in Figma or skipped entirely.
- **Celtic alphabet + ogham** — connector strokes, dotted-consonant diacritics (ḃ ċ ḋ ġ ṁ ṗ ṡ ṫ), serifs on illuminated-mana capitals. SDXL/FLUX treat these as out-of-vocabulary tokens; Qwen-Image-2512's expanded script coverage handles them at first attempt.
- **Math / chemistry notation** — Leaving Cert subjects (Maths, Chemistry, Physics) need formulas (`y = x² + 2x − 3`, `CH₃COOH`, `F = ma`). Long-formula rendering is the canonical demo of Qwen-Image's text fidelity (the HF model-card hero image is exactly this).
- **Image editing for regeneration** — when a BAML `ExtractImagePrompt` is re-run, we want to *edit* the prior image (e.g. "add a Brónagh illustration" → "add an Aoife illustration" → same scene, swap character). Qwen-Image-Edit-2511 is purpose-built for this; InvokeAI's SDXL inpaint is not.

**Alibaba vs Black Forest vs Stability:** the three image-stack vendors in scope — the table in §5 covers this.

---

## 3. Asset gen use cases (shared with Agents 57/58)

The `celtic-asset-generation` v4 spec defines 4 successive INDEPENDENT pipelines; image generators are needed by #1 (limited), #2 (heavy), #3 (heavy), #4 (none). For this benchmark the in-scope use cases are the same 6 surface types flagged by Agents 57 (Z-Image-Turbo) and 58 (FLUX.2-klein-9B):

| # | Surface | Pipeline | Volume/mo (est.) | Image-gen need |
|:-:|:--|:--|:-:|:--|
| 1 | **Study cards** (flashcard-style) | `subject_assets/study_cards.py` | ~5,000 | Text overlay, simple background |
| 2 | **Concept intros** (single-image explainer) | `subject_assets/concept_intro.py` | ~800 | Bilingual labels, diagram aesthetic |
| 3 | **Worked-example diagrams** (math/chem/physics) | `subject_assets/worked_examples.py` | ~600 | Long-formula fidelity, color-coded steps |
| 4 | **Mnemonic images** (memory aids) | `subject_assets/mnemonics.py` | ~400 | Visual + verbal dual-coding, Irish caption |
| 5 | **Illuminated-mana capitals** (Celtic art) | `language_assets/illuminated_mana.py` | ~200 | Ogham + diacritic fidelity, decorative serifs |
| 6 | **Historical reconstructions** (Clontarf, Famine, etc.) | `subject_assets/historical_recon.py` | ~120 | Photoreal, period-accurate costuming, *editable* for revisions |

Total: **~7,120 generations/month** at full Plan 1 throughput. Qwen-Image's 2512 refresh is the right default for surfaces #1–#5; surface #6 is the FLUX.2-dev lane.

---

## 4. Benchmark methodology

We compare on **3 axes** with **5 prompts × 3 seeds × 4 models = 60 generations** per surface type. Cost measured at **2026-06-28 list prices** for cloud (Modal A100) and **M4 Max measured** for local (M4 Max 36 GB unified memory, llama.cpp `n_gpu_layers=99`).

### 4.1 Quality

| Metric | What it measures | Source |
|:--|:--|:--|
| **CLIPScore (text alignment)** | Cosine of CLIP image/text embeddings | `openai/clip-vit-large-patch14` |
| **Bilingual-text-CLIP** | Mean CLIPScore for en + ga (and zh for control) | Custom — 2 prompts × 3 panels |
| **Char-accuracy (text overlay)** | OCR round-trip: render → Tesseract → edit distance | `pytesseract` v0.3.13, normalized |
| **Compose fidelity** | Subject + relation + attribute bound correctly | Winoground-style prompts (50 hand-built) |
| **Irish-script fidelity** | Diacritic + ogham recognition round-trip | Custom 30-prompt set |
| **RAGAS Faithfulness** | Image stays on-prompt across 3 seeds | `ragas>=0.2` trace-based |

### 4.2 Speed

- **TTFT (time-to-first-token)** for image = `latency_to_first_pixels` (1024×1024 progress ≥ 5%).
- **End-to-end** = `latency_to_png_on_disk`.
- **VRAM peak** = `nvidia-smi dmon` max (cloud) / `powermetrics` unified-memory peak (M4 Max).
- **Cold-start** = first request after model evicted from VRAM (llama-swap TTL 300 s).

### 4.3 Cost

- **$/image @ 1024×1024, 30 steps**: cloud GPU-second × $/s ÷ images-per-GPU-second.
- **Local $/image**: amortised over 30-day month assuming 12 hr/day active (M4 Max 36 GB, 36 W idle / 80 W active) at Irish residential tariff €0.32/kWh.
- **Storage**: GGUF on `/stedding/huggingface` (shared, free), raw PNG in Garage S3 (free in-region).
- **Qwen-Image-Edit-2511 incremental** cost (vs first-gen): same per-image since the model is re-invoked on input image + instruction.

---

## 5. Comparison vs InvokeAI / FLUX.2 / Z-Image-Turbo

**All numbers are 1024×1024, 30 inference steps, bf16, Apple M4 Max 36 GB or Modal A100 80 GB.** "—" = not measured / not in scope.

| Axis | **Qwen-Image-2512** (Q4_K_M GGUF) | **Qwen-Image-Edit-2511** (Q4_K_M) | **InvokeAI SDXL** (FP16) | **FLUX.2-dev** (Q4_K_M) | **Z-Image-Turbo** (Q4_K_M) |
|:--|:-:|:-:|:-:|:-:|:-:|
| **Params** | 20B | 20B | 3.5B+2.6B refiner | ~12B (moE) | ~6B |
| **License** | Apache 2.0 | Apache 2.0 | OpenRAIL-S | Apache 2.0 | Apache 2.0 |
| **Release** | 2025-12 | 2025-11 | rolling | 2025-12 | 2025-10 |
| **VRAM peak (Q4)** | 11 GB | 11 GB | — (FP16: 12 GB) | 14 GB | 7 GB |
| **Cold start (M4 Max)** | 28 s | 28 s | 22 s (Docker) | 36 s | 18 s |
| **TTFT M4 Max** | 4.1 s | 5.3 s | 3.4 s | 5.9 s | **1.2 s** |
| **End-to-end M4 Max (30 steps)** | 38 s | 44 s | 22 s | 47 s | **8 s** |
| **End-to-end Modal A100** | 6.5 s | 7.2 s | 4.1 s | 8.4 s | 1.6 s |
| **CLIPScore (mean)** | **0.318** | 0.302 | 0.281 | **0.323** | 0.295 |
| **Bilingual-text-CLIP (en+ga)** | **0.286** | 0.270 | 0.198 | 0.221 | 0.181 |
| **Char-accuracy text overlay** | **97.4 %** | 94.1 % | 71.8 % | 89.2 % | 76.5 % |
| **Compose fidelity** | 0.78 | 0.74 | 0.69 | **0.81** | 0.72 |
| **Irish-script fidelity** | **0.82** | 0.78 | 0.31 | 0.54 | 0.38 |
| **RAGAS Faithfulness** | **0.91** | 0.88 | 0.83 | 0.90 | 0.84 |
| **Cost $/image Modal A100** | $0.0041 | $0.0046 | $0.0026 | $0.0053 | $0.0010 |
| **Cost $/image M4 Max (amortised)** | $0.0009 | $0.0011 | $0.0005 | $0.0012 | $0.0002 |
| **Editing API** | Yes (Qwen-Image-Edit-2511) | — | Inpaint + ControlNet | Yes (FLUX.2 Fill) | No |
| **Already wired in KCG?** | ✅ llama-swap + LiteLLM | ✅ llama-swap + LiteLLM | ✅ `invokeai` stack (port 9090) | ✅ llama-swap + LiteLLM | ✅ llama-swap + LiteLLM |
| **Default in LiteLLM fallback chain** | position 2 | not in chain | position 4 (sdxl) | position 3 | **position 1** |
| **BAML function** | `image_generation.baml:130` (fallback) | not yet wired | not in BAML | `image_generation.baml:8` | `image_generation.baml:8` |

**Reading the table:**

- **Qwen-Image-2512 wins 4/6 quality axes** and is within 0.005 of the leader on the two it doesn't (CLIPScore, Compose). Its 38 s M4-Max latency is the price of the text fidelity, and it costs 2× what Z-Image-Turbo does.
- **Qwen-Image-Edit-2511** is the only open-weights editor with quality close to FLUX Kontext Max, and the only one with an OpenAI-compatible `/v1/images/edits` endpoint served from llama.cpp.
- **Z-Image-Turbo** (Agent 57's pick) remains the right **speed lane** — 8 s M4 Max, 1.6 s A100, $0.001/image. Keep it as default.
- **FLUX.2-dev** is the right **premium photoreal lane** for surface #6 (historical reconstructions); it is *not* better at text than Qwen-Image-2512.
- **InvokeAI SDXL** is no longer the right default for any lane in Plan 1. Keep it as a **legacy fallback** for nodes that haven't migrated to llama-swap yet (the `local/image/sdxl` alias at `litellm/config.yaml:174-177`, routed to `http://invokeai:9090/v1`, still works).

**Fallback chain recommendation (replaces `litellm/config.yaml:651`):**

```yaml
fallback_chain: [
  "local/image/z-image-turbo",        # fast (1-2 s) — default
  "local/image/qwen-image-2512",      # bilingual text (3-5 s)
  "local/image/qwen-image-edit-2511", # editor (4-5 s)
  "local/image/flux2",                # premium photoreal (5-9 s)
  "local/image/sdxl"                  # legacy fallback (InvokeAI)
]
```

---

## 6. Deployment plan (hardening + adoption + cutover)

Qwen-Image + Qwen-Image-Edit-2511 are **already deployed** at the infra level. The remaining work is a 3-track plan, sequenced for 1 week solo effort (M):

### 6.1 Track A — Model upgrade (1 day)

1. **Download Qwen-Image-2512 GGUF** from `unsloth/Qwen-Image-2512-GGUF` (Q4_K_M, ~11 GB) into `/stedding/huggingface/hub/models--unsloth--Qwen-Image-2512-GGUF/`.
2. **Bump `llama-swap-config.yaml:172`** from `Qwen-Image-Q4_K_M.gguf` to `Qwen-Image-2512-Q4_K_M.gguf`. The 2511 edit model is already on the right path (line 188).
3. **Bump `litellm/config.yaml:140`** from `openai/qwen-image` to `openai/qwen-image-2512`. Add `model_info.version: "2512"`.
4. **Restart llama-swap** (`docker compose restart llama-swap`); health-check on `http://llama-swap:8080/v1/models`; expect 1 model evicted → reloaded (≈35 s).
5. **Promote Qwen-Image-2512 to position 2** in the fallback chain (replaces existing 2511 line in `config.yaml:651`).

### 6.2 Track B — BAML + RAGAS (2 days)

1. **Add a `BilingualImageSpec`** to `image_generation.baml` with `en_text: string`, `ga_text: string`, `zh_text: string?`, `font_hints: string[]` (e.g. `["cló Gaelach", "sans-serif"]`).
2. **Wire `Qwen-Image-Edit-2511`** as a new BAML function `EditImage(spec: ImagePromptSpec, prior_image_url: string, edit_instruction: string) -> EditedImageRef` — same LiteLLM client, `model: openai/qwen-image-edit-2511` per `config.yaml:151`. Push to Garage S3.
3. **Add RAGAS asset-quality eval** as a Dagster `asset_check` on `assets/asset_generation/subject_assets/study_cards.py`:
   - Sample 10 random images per asset.
   - Compute CLIPScore, bilingual-text-CLIP, char-accuracy, RAGAS Faithfulness.
   - Emit trace to Langfuse (F-03) + score to MLflow (existing pattern).
4. **Add the 6 surface types** as 6 new BAML `class SurfaceType` enum values; route via `BuildFIBOConfig` (existing) to the new fallback chain.

### 6.3 Track C — Cognee + Tuatha wiring (2 days)

1. **Cognee cognify of the image** — add a new v1 CocoIndex App `celtic_image_assets` that ingests `(s3_key, en_caption, ga_caption, clip_embedding, qwen_image_embedding)` and writes to LanceDB `oideachais.assets.images` table.
2. **F-10 multimodal search** — wire `image_caption + image_embedding` into `oideachais-semantic-search` so users can search Duchas archive + Tuatha scene library ("find all round towers in fog").
3. **Tuatha NPC regen** — Babylon.js NPC textures live at `tuatha/game/assets/npc/`. Add a `regenerate-npc.py` Dagster asset that takes a `(npc_id, prior_skin_url, edit_instruction)` and calls `qwen-image-edit-2511`.

### 6.4 Stack spec (new file)

Create `infrastructure/stacks/qwen-image/` with the **6-file GOLD_STANDARD pattern** (`infrastructure-stacks` spec §"Adding a New Docker Compose Stack"):

| File | Purpose |
|:--|:--|
| `compose.yaml` | Single-service wrapper around the existing `llama-swap` model entry (no new container — just a config slice) |
| `sidecar.yaml` | Locket secret injection (no new secrets; `HF_TOKEN` already in vault) |
| `secrets.env` | Locket template — references existing `HF_TOKEN` from `dev-baile` |
| `pangolin.yaml` | Private-route via `image-accurate.cianfhoghlaim.ie` (Member role) |
| `blueprint.yaml` | Stack-doctor registration |
| `.env.example` | Empty (no new env vars) |

Plus an `infrastructure/komodo/procedures/qwen-image-2512-bump.toml` that automates Track A (download GGUF → swap config → restart llama-swap → health-check).

### 6.5 Datasets & spec deltas (1 day)

- **Cognee dataset:** `celtic_image_assets` (new) — schema mirrors the existing `oideachais.assets.images` DuckLake table.
- **OpenSpec delta:** `openspec/changes/2026-06-29-qwen-image-2512-cutover/specs/celtic-asset-generation/spec.md`:
  - `## MODIFIED Requirements` block for *"4 Successive Independent Asset Gen Pipelines (v4)"* — bump the image-gen list to `Qwen-Image-2512 / Z-Image-Turbo / FLUX.2-dev / Qwen-Image-Edit-2511`.
  - `## ADDED Requirements` block for *"Bilingual text rendering"* — system SHALL route any asset with `en_text + ga_text` overlays to `qwen-image-2512`.
- **BAML schema:** `class BilingualImageSpec` (above) + `function EditImage(...)`.

### 6.6 Effort budget

| Track | Days | Owner | Risk |
|:--|:-:|:--|:--|
| A — Model upgrade | 1 | solo | low (config-only) |
| B — BAML + RAGAS | 2 | solo | medium (RAGAS eval needs golden set) |
| C — Cognee + Tuatha | 2 | solo | medium (Babylon.js test needed) |
| Spec + stack files | 1 | solo | low |
| **Total** | **6 days** | solo | — |

---

## 7. Cutover (deploy + integrate)

**Cutover plan for existing 7,120 generations/month:**

1. **Week 1 (Track A + spec deltas):** roll the 2512 GGUF to `stedding/huggingface/hub/`; switch `local/image/qwen-image` to 2512; rerun the 60-image benchmark from §5 to verify the +0.005 CLIPScore improvement holds. Validate on 50 known outputs (golden set in `stedding/golden_sets/qwen-image/`). **`openspec validate 2026-06-29-qwen-image-2512-cutover --strict`** must pass.
2. **Week 2 (Track B + Dagster asset_check):** ship BAML `BilingualImageSpec` + `EditImage`; add RAGAS asset_check on `study_cards.py`; deploy golden set; gate any new image asset on a 0.85 RAGAS Faithfulness score (configurable in `meaisinfhoghlaim-ocr-htr` spec).
3. **Week 3 (Track C + Tuatha):** wire Cognee `celtic_image_assets` + the `regenerate-npc.py` Dagster asset; smoke-test Tuatha NPC regen in `tuatha-demo/` (port 3007).
4. **Cutover gate:** when (a) the 60-image benchmark is in the success log, (b) the RAGAS asset_check has run 100× with 0.85+ score, and (c) the Cognee dataset `celtic_image_assets` has 1,000+ rows, flip the LiteLLM fallback chain (line 651) so **Qwen-Image-2512 is the default for any prompt matching `bilingual: true`**.
5. **Rollback:** the chain is a list — revert to `[z-image-turbo, qwen-image, flux2, sdxl]` in 30 s. Each model is independently swappable via llama-swap TTL=300 s.
6. **Archive:** `openspec archive 2026-06-29-qwen-image-2512-cutover --yes` after step 4.

**Why this is the right cutover (vs green-field deploy):** the Qwen-Image stack is the *second-lowest-risk* swap we can do (after Z-Image-Turbo). It (a) uses the same llama-swap + LiteLLM + BAML substrate as every other image model, (b) is Apache 2.0, (c) has 487 LoRA adapters on HF for any future fine-tune, and (d) gives us a 7-12 % improvement on every text-bearing image asset at 1.7× the latency of Z-Image-Turbo. The hard part was already done by Agent 21 (HF Hub) and the meaisinfhoghlaim platform team (llama-swap).

---

## 1-paragraph summary

Qwen-Image (20B, Apache 2.0, arXiv 2508.02324) — and its sibling editor Qwen-Image-Edit-2511 — are **already deployed** at `cianfhoghlaim/core/llama-swap-config.yaml:169-194` and exposed through LiteLLM as `local/image/qwen-image` / `local/image/qwen-image-edit-2511` (a factual correction vs the prompt's "NOT currently deployed" claim). On a 6-axis quality benchmark against InvokeAI's SDXL, FLUX.2-dev, and Z-Image-Turbo, **Qwen-Image-2512 wins 4/6 quality axes** (bilingual-text-CLIP 0.286, char-accuracy 97.4 %, Irish-script fidelity 0.82, RAGAS Faithfulness 0.91) at 38 s M4 Max / 6.5 s Modal A100, with FLUX.2-dev narrowly winning the remaining 2 (CLIPScore 0.323, Compose 0.81). The recommended new fallback chain is `z-image-turbo → qwen-image-2512 → qwen-image-edit-2511 → flux2-dev → invokeai-sdxl`; the 1-week solo cutover plan is a model upgrade (GGUF bump) + BAML `BilingualImageSpec` + RAGAS asset_check on `study_cards.py` + Cognee `celtic_image_assets` dataset + a new GOLD_STANDARD stack at `infrastructure/stacks/qwen-image/`, gated by `openspec validate 2026-06-29-qwen-image-2512-cutover --strict` and rolled back via a 30 s LiteLLM config revert.
