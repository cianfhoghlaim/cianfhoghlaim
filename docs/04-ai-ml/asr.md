---
title: 'Speech Recognition (ASR) — Whisper/faster-whisper & wav2vec2-XLSR-Irish: Reference & Skill Card'
domain: 'ai_ml'
status: 'stable'
description: 'Complete ASR (Automatic Speech Recognition) reference — Whisper/faster-whisper (OpenAI multilingual, 99 languages, large-v3, 4x CTranslate2 speedup) and wav2vec2-XLSR-Irish (specialised Irish Gaelic fine-tune, XLSR-53 backbone, 2.4 GB lightweight). Plus skill card for each with KCG context, HuggingFace passthrough, BAML extraction pipeline integration, and MacBook M4 48GB deployment.'
read_when:
  - transcribing audio
  - looking for documentation on this topic
  - choosing between general vs Irish-specific ASR
  - working with Irish Gaelic speech
updated: 2026-06-13
supersedes:
  - docs/ai-ml/whisper-faster-whisper.md
  - docs/ai-ml/wav2vec2-xlsr-irish.md
truth: sole
ccc_query_hints:
  - whisper faster-whisper speech recognition
  - wav2vec2 xlsr irish speech recognition
  - irish gaelic asr
  - multilingual speech to text
  - huggingface asr passthrough
---

# Speech Recognition (ASR) — Whisper/faster-whisper & wav2vec2-XLSR-Irish: Reference & Skill Card

> **Merged from 2 canonical sources**:
> - `whisper-faster-whisper.md` (55 lines) — general multilingual ASR
> - `wav2vec2-xlsr-irish.md` (54 lines) — Irish-specific ASR fine-tune
>
> Both serve complementary roles in the speech pipeline: Whisper for general multilingual transcription, wav2vec2-XLSR-Irish for accuracy-critical Irish-language content.

---

## Whisper / faster-whisper — Speech Recognition (ASR)

### Overview

Whisper is OpenAI's open-source automatic speech recognition (ASR) model supporting 99 languages, including Irish Gaelic. faster-whisper is a reimplementation using CTranslate2 that achieves 4x speedup and lower memory usage while maintaining identical accuracy. The large-v3 variant provides the highest accuracy across all supported languages.

### Why This Matters for Kings' College Galway

Irish-language audio content — TG4 broadcasts, Raidió na Gaeltachta segments, oral exam recordings, classroom lectures, and student pronunciation practice — needs accurate transcription before it can enter the curriculum pipeline. Whisper's multilingual training includes Irish, and faster-whisper's optimised inference means the 23 GB large-v3 model runs efficiently on the MacBook M4. Transcribed Irish audio feeds into the BAML extraction pipeline for structured content generation and the embedding pipeline for semantic search.

### Key Features

- **99 languages** — Including Irish Gaelic (Gaeilge)
- **large-v3** — Highest accuracy variant, 23 GB
- **faster-whisper** — 4x speedup, lower memory via CTranslate2
- **Word-level timestamps** — Accurate word alignment for subtitles
- **Noise-robust** — Handles background noise and varying audio quality

### Installation

```bash
uv add faster-whisper
# Model downloads automatically on first use
```

### Integration with Our Stack

Whisper is served via HuggingFace passthrough in the LiteLLM gateway's `whisper-irish` alias. The model is cached in `stedding/huggingface/hub/` (23 GB). faster-whisper is used in production for lower latency. Transcriptions feed into BAML extraction and LanceDB indexing.

### Upstream

- **Whisper**: <https://github.com/openai/whisper>
- **faster-whisper**: <https://github.com/SYSTRAN/faster-whisper>
- **Model**: <https://huggingface.co/openai/whisper-large-v3>
- **Latest**: large-v3 (2023) — improved multilingual accuracy, especially for low-resource languages

### Screenshot

Whisper is a CLI and Python library. The CLI: `whisper audio.mp3 --language irish --model large-v3` outputs transcribed text with timestamps. The Python API returns segments with start/end times and confidence scores. faster-whisper provides identical output at 4x speed.

---

## wav2vec2-XLSR-Irish — Irish Speech Recognition

### Overview

wav2vec2-XLSR-Irish is a fine-tuned variant of Facebook's wav2vec2-XLSR-53 model, specifically trained for Irish Gaelic speech recognition. It uses the XLSR-53 cross-lingual speech representation model fine-tuned on Irish speech data, providing specialised Irish ASR with better accuracy on Irish phonology than general multilingual models.

### Why This Matters for Kings' College Galway

Irish Gaelic has phonological features that general ASR models struggle with: broad/slender consonant distinctions, initial mutations (séimhiú, urú) that change word-initial sounds, and dialectal variation across Connacht, Munster, and Ulster Irish. A model specifically fine-tuned on Irish speech data captures these features, producing more accurate transcriptions for Irish-language educational content. This specialised model is used alongside Whisper for Irish audio — Whisper for general transcription, wav2vec2-XLSR-Irish for accuracy-critical Irish-language content.

### Key Features

- **Irish-specific** — Fine-tuned on Irish Gaelic speech data
- **XLSR-53 backbone** — Cross-lingual speech representations from 53 languages
- **Phonology-aware** — Handles Irish-specific sound distinctions
- **Lightweight** — 2.4 GB model, efficient inference
- **Wav2Vec2 architecture** — Transformer-based speech encoder

### Installation

```bash
uv add transformers
# Model: cpierse/wav2vec2-large-xlsr-53-irish
```

### Integration with Our Stack

The model is served via HuggingFace passthrough and cached in `stedding/huggingface/hub/` (~2.4 GB). It is used as a specialised Irish ASR route in the speech processing pipeline, complementing Whisper for general multilingual ASR.

### Upstream

- **Model**: <https://huggingface.co/cpierse/wav2vec2-large-xlsr-53-irish>
- **Base model**: <https://huggingface.co/facebook/wav2vec2-large-xlsr-53>
- **Latest**: Community fine-tuned model on the Common Voice Irish dataset

### Screenshot

The model is accessed via HuggingFace Transformers: `Wav2Vec2ForCTC.from_pretrained("cpierse/wav2vec2-large-xlsr-53-irish")`. Output is token-level text with timestamps. Word Error Rate (WER) on Irish test sets is reported on the model card. The Common Voice Irish dataset provides training and evaluation data.
