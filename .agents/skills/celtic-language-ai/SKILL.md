---
name: celtic-language-ai
description: Celtic-language AI for Irish (Gaeilge), Scottish Gaelic (Gàidhlig), Welsh (Cymraeg), Manx (Gaelg), Cornish (Kernewek), Breton (Brezhoneg). BAML extraction patterns + curated model catalog by language (GaBERT, UCCIX, Helsinki OPUS-MT, NLLB-200, wav2vec2-XLSR-Irish, Chatterbox TTS, BGE-M3 multilingual embeddings) + the 6 living Celtic languages + the 8 ISO codes.
---

# Celtic Language AI

## When to use this skill

Use when you need to:

- "Extract structured data from an Irish Leaving Cert PDF"
- "Translate an English document to all 6 Celtic languages"
- "Transcribe an Irish oral exam audio"
- "Generate an Irish pronunciation guide via TTS"
- "Fine-tune a model on the Irish curriculum"
- "Choose between the 3 LLM / 2 NMT / 2 ASR / 2 TTS models
  for the Celtic stack"

## The 6 living Celtic languages

| Language | ISO | Native speakers | LLM | Translation | ASR | TTS |
|:--|:--|--:|:--|:--|:--|:--|
| **Irish (Gaeilge)** | `ga` | 180k | UCCIX-Llama3.1-70B | Helsinki OPUS-MT en↔ga | wav2vec2-XLSR-Irish | Chatterbox `ga-IE-female-1` |
| **Scottish Gaelic (Gàidhlig)** | `gd` | 60k | (no dedicated LLM) | Helsinki OPUS-MT en↔gd | MMS-1B-fl102 | MMS-TTS `gd-GB-female-1` |
| **Welsh (Cymraeg)** | `cy` | 880k | BangorAI/Mistral-7B-Cymraeg | Helsinki OPUS-MT en↔cy | MMS-1B-fl102 | MMS-TTS `cy-GB-female-1` |
| **Manx (Gaelg)** | `gv` | 2k | (no dedicated LLM) | NLLB-200 distilled-600M | MMS-1B-fl102 | (no native TTS) |
| **Cornish (Kernewek)** | `kw` | 600 | (no dedicated LLM) | NLLB-200 distilled-600M | MMS-1B-fl102 | (no native TTS) |
| **Breton (Brezhoneg)** | `br` | 200k | (no dedicated LLM) | NLLB-200 distilled-600M | MMS-1B-fl102 | (no native TTS) |

## BAML extraction (the canonical pattern)

```baml
// oideachais/baml_src/celtic_linguistics.baml
class IrishGrammarConcept {
  ga_term string
  en_translation string
  example_ga string
  example_en string
  register "formal" | "informal" | "archaic"
  @@description #"An Irish-language grammar concept with English translation and usage examples."#
}

function ExtractIrishGrammarConcepts(
  document_text: string
) -> IrishGrammarConcept[] {
  client "openai/gpt-4o-mini"
  prompt #"Extract all Irish grammar concepts from the following NCCA document. Each concept MUST have a `ga_term` (the Irish word/phrase) and an `en_translation`. The `register` field tracks dialect (formal/informal/archaic). {{ ctx.output_format }}"#
}
```

## Translation stack (Helsinki OPUS-MT + NLLB-200)

```python
from transformers import MarianMTModel, MarianTokenizer

# Helsinki OPUS-MT for accuracy on en↔ga, en↔cy pairs
model_name = "Helsinki-NLP/opus-mt-en-ga"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Translate English → Irish
texts = ["Hello, how are you?"]
inputs = tokenizer(texts, return_tensors="pt", padding=True)
outputs = model.generate(**inputs)
translated = tokenizer.batch_decode(outputs, skip_special_tokens=True)
# → ["Dia duit, conas atá tú?"]
```

**NLLB-200 distilled-600M** as the fallback for all 6 Celtic
languages (especially low-resource Manx / Cornish / Breton):

```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")

# Manx: gaelg_Latn
# Cornish: cor_Latn
# Breton: bre_Latn
inputs = tokenizer("Hello", return_tensors="pt", src_lang="eng_Latn", tgt_lang="cor_Latn")
outputs = model.generate(**inputs)
```

## ASR stack (wav2vec2-XLSR-Irish + Whisper large-v3 + MMS)

See `.agents/skills/asr/SKILL.md` for the full stack. The
canonical routing rule is:

- **wav2vec2-XLSR-Irish** for accuracy-critical Irish
  (oral exams, TG4 broadcasts)
- **Whisper large-v3 via faster-whisper** for general
  multilingual
- **MMS-1B-fl102** for low-resource Celtic languages

## TTS stack (Chatterbox + MMS-TTS + Piper)

See `.agents/skills/tts/SKILL.md` for the full stack. The
canonical engine is **Chatterbox** (9.7 GB, MIT-licensed) for
Irish pronunciation guides and AI tutor speech.

## BGE-M3 multilingual embeddings

For cross-Celtic RAG retrieval, use BGE-M3 (1024-d,
multilingual, 100+ languages including all 6 Celtic):

```python
from lancedb.embeddings import get_registry

embedder = get_registry().get("huggingface").create(
    name="BAAI/bge-m3",
    device="cuda",  # or "mps" for M4 Mac
)
```

## Curated model catalog (KCG-recommended)

### Irish LLMs

| Model | Params | License | Use case |
|:--|--:|:--|:--|
| `ReliableAI/UCCIX-Llama2-13B-Instruct` | 13B | Apache 2.0 | Irish curriculum Q&A |
| `ReliableAI/UCCIX-Llama3.1-70B-Instruct` | 70B | Apache 2.0 | High-accuracy Irish generation |
| `DCU-NLP/bert-base-irish-cased-v1` (GaBERT) | 117M | Apache 2.0 | Irish text classification |
| `jimregan/BERTreach` (RoBERTa) | 125M | Apache 2.0 | Irish NER |
| `DCU-NLP/electra-base-irish-cased-v1` | 110M | Apache 2.0 | Irish token classification |

### Welsh LLM

| Model | Params | License | Use case |
|:--|--:|:--|:--|
| `BangorAI/Mistral-7B-Cymraeg-Welsh-v2` | 7B | Apache 2.0 | Welsh curriculum Q&A |

### Translation

| Model | Pairs | Use case |
|:--|:--|:--|
| `Helsinki-NLP/opus-mt-en-ga` | en↔ga | English-Irish translation |
| `Helsinki-NLP/opus-mt-en-cy` | en↔cy | English-Welsh translation |
| `Helsinki-NLP/opus-mt-en-gd` | en↔gd | English-Scottish Gaelic |
| `Helsinki-NLP/opus-mt-ga-en` | ga→en | Irish-English translation |
| `Helsinki-NLP/opus-mt-cy-en` | cy→en | Welsh-English translation |
| `facebook/nllb-200-distilled-600M` | 200+ langs | Low-resource fallback |
| `facebook/m2m100_418M` | many-to-many | Direct Celtic↔Celtic (no English pivot) |

### Speech (ASR)

| Model | Language | License | WER (Common Voice) |
|:--|:--|:--|:--|
| `cpierse/wav2vec2-large-xlsr-53-irish` | Irish | Apache 2.0 | **5.2%** |
| `openai/whisper-large-v3` (faster-whisper) | 99 langs | MIT | 12.8% (ga) |
| `facebook/mms-1b-fl102` | 1000+ langs | Apache 2.0 | varies |

### Speech (TTS)

| Model | Language | License | Quality |
|:--|:--|:--|:--|
| `ResembleAI/chatterbox` | 23+ langs | MIT | High |
| `facebook/mms-tts-*` | 1000+ langs | Apache 2.0 | Good |
| `rhasspy/piper-*` | 30+ langs | MIT | Decent (on-device) |

### Embeddings

| Model | Dim | License | Use case |
|:--|--:|:--|:--|
| `BAAI/bge-m3` | 1024 | MIT | Multilingual RAG (100+ langs) |
| `intfloat/multilingual-e5-large` | 1024 | MIT | Multilingual RAG |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 384 | Apache 2.0 | Lightweight multilingual RAG |

## Datasets

| Dataset | Languages | Size | Use case |
|:--|:--|--:|:--|
| Common Voice 18.0 | ga, gd, cy, gv, br, kw | varies | ASR training/eval |
| CC-100 | ga, gd, cy, br | 108M Irish tokens | LLM pre-training |
| OSCAR | ga, cy | 1.5M Irish docs | LLM pre-training |
| CulturaX | ga, gd, cy, br, gv, kw | 60M+ Irish docs | LLM pre-training |
| Wikipedia | ga, gd, cy, br, gv, kw | 70k Irish articles | LLM pre-training |
| ParaCrawl | ga↔en, cy↔en | 5M+ pairs | NMT training |

## KCG integration

- `oideachais/baml_src/celtic_linguistics.baml` — the
  canonical BAML schema for Irish grammar extraction
- `oideachais/baml_src/celtic_sources.baml` — the canonical
  BAML schema for source attribution
- `meaisinfhoghlaim/language/` — the 6 Celtic-language
  subdirs (`brezhoneg/`, `cymraeg/`, `gaeilge/`, `gaelg/`,
  `gaidhlig/`, `kernowek/`) + the `cognates.yaml` cross-Celtic
  cognate database
- `meaisinfhoghlaim/catalog/sources.yaml` — the Celtic data
  sources registry
- Dagster assets: `meaisinfhoghlaim/dagster_assets/`
  (`celtic_curriculum.py`, `mythology_content.py`,
  `*_embeddings.py`)

## KCG: Production model fallback chains

The KCG production rule: **never let a single model failure
cascade**. Every category has a 2-3 step fallback chain
(see `.agents/skills/kcg-ml-models/SKILL.md` for the full
70+ model registry):

```yaml
vision:        glm-4.6v-flash → qwen3-vl → moondream2
ocr:           olmocr-2 → granite-docling
reasoning:     nemotron-3-nano → gemma-3n
celtic_irish:  qomhra-mistral → uccix → britllm
celtic_gaelic: britllm → qomhra-mistral  # BritLLM is stronger for Gàidhlig
```

**Implementation**: BAML `client` blocks chain the fallback
models. If `qomhra-mistral` returns empty or errors, BAML
auto-retries with `uccix`, then `britllm`. The fallback is
**per-call** (not per-session). The 3 inference backends
(llama-swap :8080 for GGUF, mlx-omni-server :10240 for MLX,
invokeai :9090 for safetensors) all run on the same M4 Max
workload host.

## KCG Celtic LLMs (BritLLM + EuroLLM + Qomhrá 2025)

### BritLLM (Caernarfon 3B) — UCL NLP, 2025

- **Repo:** `britllm/britllm-3b-v0.1` (Hugging Face)
- **License:** ODC-By v1.0 (truly open)
- **Pre-training:** 1.4T tokens, SlimPajama (627B English)
  + ~1B unique British-language tokens + ~10B in-context
  learning tokens
- **British-language data:** full Wikipedia for
  Irish / Welsh / Scots / Scottish Gaelic, plus NLLB
  parallel data adapted to ICL format
- **Languages:** English, Scots, Welsh, Irish, Scottish Gaelic
- **Benchmarks:** beats OpenLLaMA-7B v2 and
  TinyLLaMA-v1.1 on OpenLLM leaderboard; on BritEval
  (Irish + Welsh + Scots + Scottish Gaelic) it beats
  Mistral-7B, Phi-2, Bloom-7B
- **BritEval benchmark:** AI2 ARC + PIQA + XNLI translated
  to all 4 British languages

KCG use: prefer `britllm-3b-v0.1` over `britllm` for
Gàidhlig, Welsh, and Scots, where it out-performs
`qomhra-mistral`. Quantise GGUF `Q4_K_M` for the
llama-swap :8080 backend.

### EuroLLM-22B-Instruct-2512 — utter-project, 2025-12

- **Repo:** `utter-project/EuroLLM-22B-Instruct-2512`
  (Apache 2.0, fully open)
- **Developers:** Instituto Superior Técnico (Lisbon),
  Instituto de Telecomunicações, University of Edinburgh,
  Aveni, Unbabel, Paris-Saclay, Artefact, UvA, Naver Labs,
  Sorbonne
- **Funding:** European Union (EuroHPC extreme-scale)
- **Languages:** all 24 official EU languages
  **including Irish** + Arabic, Catalan, Chinese, Galician,
  Hindi, Japanese, Korean, Norwegian, Russian, Turkish,
  Ukrainian (35 total)
- **Pre-training:** 4T tokens on MareNostrum 5
  (400 × H100) in 3 phases: 3.6T web+parallel+wiki+arxiv,
  400B annealing (CometKiwi-22 + EuroFilter quality
  filtering), 100B annealing-to-zero with long-context
  up-sampling to 32k
- **Architecture:** dense Transformer, GQA (8 KV heads),
  RoPE Θ=1M, RMSNorm, SwiGLU, 56 layers, 6144 emb,
  16384 FFN, 22.6B params total (21B non-embedding)
- **Post-training:** EuroBlocks instruction-tuning
  dataset (general instruction + MT focus); best EU-made
  fully open model on HellaSwag/MMLU/MMLU-Pro/ARC-C/
  MGSM/FLORES/WMT24++ matching Gemma-3-27B and Qwen-3-32B
  on translation
- **Usage:**
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  m = "utter-project/EuroLLM-22B-Instruct-2512"
  tok = AutoTokenizer.from_pretrained(m)
  model = AutoModelForCausalLM.from_pretrained(m)
  msgs = [
      {"role": "system", "content": "You are EuroLLM ..."},
      {"role": "user", "content": "Aistriú anseo go Gaeilge."},
  ]
  ids = tok.apply_chat_template(msgs, tokenize=True,
                                add_generation_prompt=True,
                                return_tensors="pt")
  print(tok.decode(model.generate(ids, max_new_tokens=1024)[0],
                   skip_special_tokens=True))
  ```

KCG use: the canonical **en→ga** and **ga→en** model
when translation fidelity matters more than speed. ~21B
non-embedding params, BF16 = ~42 GB; run GGUF `Q3_K_M`
on the llama-swap :8080 backend (or GGUF `Q4_K_M` on
arm1-oci with the GPU stack).

### Qomhrá 2025

- 8B bilingual Irish-English; fine-tuned from Mistral
- Trained on Gaois + UCC corpora + Gemini-1.5-Pro
  translations of Dolly V2 → Irish
- Up to **+29%** on Irish benchmarks vs Mistral-7B base
- KCG fallback: the `celtic_irish` chain's
  `qomhra-mistral` primary step

### BritEval benchmark (KCG use)

BritEval is the KCG-preferred evaluation suite for any
new British-language LLM fine-tune. It covers 4 languages
(Scots, Irish, Welsh, Scottish Gaelic) with ARC-c
(multiple-choice science), PIQA (physical commonsense),
and XNLI (cross-lingual NLI). When adding a new Celtic
LLM to the registry, **always** report BritEval numbers
in `models/registry.yaml`.

## Diffusion NMT for low-resource Irish

The autoregressive (AR) Transformer is reaching an
asymptotic limit for Irish-English translation. AR models
**propagate errors left-to-right** — a single hallucinated
preposition corrupts the subsequent mutation (eclipsis,
lenition) in a VSO language. The KCG direction (Q1 2026)
is **diffusion NMT**, specifically the **NeoDiff** and
**Block Diffusion** architectures.

### NeoDiff (SOTA 2025)

NeoDiff disentangles **extrinsic time** (the global
denoising step) from **intrinsic time** (the per-token
progress) via a **Poisson process**. This gives the model
a "curriculum" generation: easy tokens (determiners,
conjunctions) resolve first and act as anchors for the
harder ones.

Why this matters for Irish: the noun *bád* must eclipsise
to *mbád* after the preposition *ar*. An AR model has to
predict *ar*, then *an*, then *mbád*; if it hallucinates
*ag* instead, the mutation is wrong. NeoDiff generates
the whole sequence iteratively and can **fix backwards**
when the context-aware time predictor sees the
morphosyntactic conflict.

### Block Diffusion

Block Diffusion hybridises AR + diffusion to get the
**KV-cache benefit of AR** and the **bidirectional
refinement of diffusion**. It generates chunks of K
tokens (typically 4-16) at a time, with full
bidirectional attention *within* the block and AR
conditioning *across* blocks. This is the
**practically deployable** diffusion NMT — it can be
warm-started from Qwen3-VL weights (modify the attention
mask + add a diffusion head) which is critical for the
~50k-100k Irish sentence-pair data regime.

### KCG diffusion NMT stack (Multimodal Data Foundry)

For training data, KCG uses a 4-phase agentic pipeline:

1. **Archivist Agent** (Browserbase + Qwen3-VL): navigates
   Tipperary Studies, Dúchas.ie, Project Gutenberg; downloads
   bilingual manuscripts; saves to ADK Artifacts.
2. **Analyst Agent** (Qwen3-VL "Thinking" mode): reads
   each page, identifies the layout (Irish left / English
   right), transcribes with a "Thinking" prompt that asks
   for spatial alignment; preserves the **punctum delens**
   (ḃ → bh) via a forced substitution rule.
3. **Translator Agent** (UCCIX or Qwen3-VL): generates
   synthetic translations for monolingual Irish; runs a
   back-translation cycle + BLEU/BERTScore filter
   (drop pairs < 0.7).
4. **Curator Agent** (LanceDB): stores validated
   `(image, irish_text, english_text)` triplets in a
   `LanceModel` schema; the column `irish_vector` is
   auto-generated via the embedding function for
   retrieval during training.

The LanceDB schema uses **zero-copy `LanceDataset`** for
PyTorch so the diffusion model streams batches directly
from object storage — critical when training > 1M
iterations on consumer hardware.

See [`celtic-asset-generation/references/diffusion-irish-translation.md`](../celtic-asset-generation/references/diffusion-irish-translation.md) for the
full 354-line technical deep dive (NeoDiff math, Block
Diffusion gradients, multimodal data foundry code).

## English-pivoted CoT translation (T5Gemma-2 + Gemini 3 + ADK)

For **high-stakes** en↔ga translation (legal deeds,
archival deeds, exam rubrics), KCG runs a neuro-symbolic
**Draft-Critique-Refine** loop orchestrated by Google ADK.
This is the "agentic translation" pattern that complements
the diffusion NMT above (diffusion is good for high-volume,
agentic CoT is good for low-volume high-stakes).

### The 4 roles

| Role | Model | Why |
|:--|:--|:--|
| **Drafter** | T5Gemma-2 (270M / 4B / 27B) | Encoder-decoder; reads full source before generating; tied embeddings save ~10.5% params; 140+ multilingual transfer |
| **Critic** | Gemini 3 Pro | System-2 reasoning, multimodal OCR, "Thought Signatures" audit trail |
| **Ingestor** | Gemini 3 Flash | Cheap OCR + layout analysis (€0.10/M input vs €0.50/M for Pro) |
| **Compliance** | ADK ontology tool | Hard replacement of "mostly right" terms against `tearma.ie` glossary |

### The 5-phase execution

1. **Ingestion** — SigLIP encoder reads the scanned page,
   preserves layout (`{"header": "...", "body": "..."}`),
   extracts context vector (domain / dialect / register).
2. **Drafting** — T5Gemma-2 reads the full source via
   its encoder before decoding; respects the
   `Dialect=Connacht` and `Register=Formal` hints.
3. **Critique** — Gemini 3 Pro does System-2 checks:
   *Does the translation reflect the legal meaning?
   Are séimhiú/urú correct after ar/ag? Is the
   terminology Connacht-consistent?* Returns a
   structured **Critique Report** JSON.
4. **Refinement** — Drafter produces `Draft v2` with
   the Critique Report in context.
5. **Compliance** — ADK Compliance Agent runs the
   **Truth Anchoring Network** against `tearma.ie`:
   if the model wrote "Ráiteas faoi mhionn" instead of
   the mandated "Mionnscríbhinn", the symbolic layer
   forces a hard replacement.

### Why English-pivoted CoT?

The Celtic-language CoT literature shows the best
Irish reasoning is **via English** — the model thinks
in English ("the legal subject is X, the Connacht
dialect uses form Y"), then produces the Irish output.
This is enforced at the prompt level: T5Gemma-2 is
given a `ChainOfThought: en` slot that must be filled
before the Irish output. The critic then scores both
the CoT reasoning (in English) and the final Irish
output separately.

### Tiered compute (cost control)

T5Gemma-2-4B (Drafter) + Gemini 3 Flash (Ingestor) do
the heavy lifting at €0.10-0.30 / M tokens. Gemini 3
Pro (Critic) is reserved for the high-value critique
step at €0.50 / M tokens. Net: the "PhD-level
reasoning" cost is paid only on the section being
refined, not on the bulk.

### Infrastructure (Transformers v5 + ADK)

Run T5Gemma-2 locally via `transformers serve`
(OpenAI-compatible API on `:8080`) to eliminate network
latency in the loop. Use **continuous batching** (v5
delivers up to +217% throughput) for the parallel
sections and **paged attention** for the 128k
contexts needed to keep the audit log.

See [`celtic-asset-generation/references/neuro-symbolic-translation-engine.md`](../celtic-asset-generation/references/neuro-symbolic-translation-engine.md)
for the full neuro-symbolic Gaeilge translation
blueprint (Masked-CFM + InkSpire + the agent stack).

## Related skills

- `.agents/skills/asr/SKILL.md` — speech recognition
- `.agents/skills/tts/SKILL.md` — text-to-speech
- `.agents/skills/baml/SKILL.md` — BAML extraction
- `.agents/skills/trl/SKILL.md` — preference optimisation
- `.agents/skills/peft/SKILL.md` — LoRA / QLoRA fine-tuning
- `.agents/skills/unsloth/SKILL.md` — Unsloth wrapper
- `.agents/skills/lancedb/SKILL.md` — BGE-M3 + hybrid search
- `.agents/skills/irish-edtech/SKILL.md` — Irish-only
  comprehensive reference (344 lines)
- `.agents/skills/celtic-language-ai/SKILL.md` — this skill
  (covers all 6 Celtic languages)
