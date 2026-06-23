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
