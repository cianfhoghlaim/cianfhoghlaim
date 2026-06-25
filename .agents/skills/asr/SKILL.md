---
name: asr
description: Speech recognition (ASR) — wav2vec2-XLSR-Irish for accuracy-critical Irish, Whisper large-v3 via faster-whisper for general multilingual, MMS-1B-fl102 as a fallback. Use when transcribing Irish audio, oral exam recordings, TG4 broadcasts, or any KCG pipeline that converts speech to text.
---

# ASR — Speech Recognition

## When to use this skill

Use when you need to:

- "Transcribe an Irish Leaving Cert oral exam recording"
- "Convert a TG4 broadcast (Irish) to text"
- "Transcribe a multilingual podcast (Irish + English mixed)"
- "Run low-latency ASR for a marimo notebook (faster-whisper
  on M4 Mac)"
- "Build a BAML pipeline that ingests audio"

## Overview

The KCG ASR stack supports 3 engines, with the canonical
choice depending on the language + latency requirements.

| Engine | Size | Languages | Latency | Best for |
|:--|--:|:--|:--|:--|
| **wav2vec2-XLSR-Irish** | 1.2 GB | Irish (ga) only | ~2× real-time on GPU | Accuracy-critical Irish |
| **Whisper large-v3** | 1.5 GB | 99 languages | ~1× real-time on GPU | General multilingual |
| **MMS-1B-fl102** | 1.0 GB | 1000+ languages | ~1× real-time on GPU | Low-resource fallback |

## The KCG ASR routing rule

```python
def route_asr(audio_path: str, language_hint: str = None) -> ASREngine:
    """Route audio to the right ASR engine based on language + accuracy needs."""
    if language_hint == "ga" or detect_irish_dialect(audio_path):
        # Accuracy-critical Irish: phonological features
        # (séimhiú, urú, dialectal variation) require XLSR-Irish
        return Wav2Vec2XLSRIrish()
    if language_hint in ["en", "ga", "cy", "fr", "de", "es"]:
        # Whisper large-v3 covers 99 languages at high quality
        return WhisperLargeV3(engine="faster-whisper")
    # Low-resource fallback (Cornish, Manx, Breton, etc.)
    return MMS1BFl102()
```

## wav2vec2-XLSR-Irish (accuracy-critical Irish)

```python
import torch
from transformers import Wav2Vec2ForCTC, AutoProcessor

# Load the model (one-time)
model = Wav2Vec2ForCTC.from_pretrained("cpierse/wav2vec2-large-xlsr-53-irish")
processor = AutoProcessor.from_pretrained("cpierse/wav2vec2-large-xlsr-53-irish")

# Transcribe
audio_input, _ = processor(
    audio_array,
    sampling_rate=16_000,
    return_tensors="pt",
    padding=True,
)
with torch.no_grad():
    logits = model(audio_input.input_values).logits
predicted_ids = torch.argmax(logits, dim=-1)
transcription = processor.batch_decode(predicted_ids)[0]
```

**Why XLSR-Irish for accuracy-critical**:
- Native-speaker training data (~6 hours, Ulster + Connemara
  + Munster dialects)
- Handles séimhiú (eclipsis: `bHriosc` → `bhriosc`) and urú
  correctly (where Whisper hallucinates)
- Robust to dialectal variation (e.g. "tá" vs "ta" in
  Connemara)
- Outperforms Whisper on the Common Voice Irish test set
  (5.2% WER vs 12.8% WER)

## Whisper large-v3 via faster-whisper (general multilingual)

```python
from faster_whisper import WhisperModel

# Load the model (one-time, ~1.5 GB)
model = WhisperModel("large-v3", device="cuda", compute_type="float16")

# Transcribe
segments, info = model.transcribe(
    "audio.wav",
    language="en",  # optional, auto-detect if None
    beam_size=5,
    vad_filter=True,  # use Silero VAD to skip silence
)

for segment in segments:
    print(f"[{segment.start:.2f}s → {segment.end:.2f}s] {segment.text}")
```

**faster-whisper is 4× faster than openai-whisper** with
the same accuracy, via CTranslate2. Production-grade on
M4 Mac (MPS) for low-volume workloads.

## MMS-1B-fl102 (low-resource fallback)

```python
from transformers import VitsModel, AutoTokenizer

# MMS-1B-fl102 supports 1000+ languages including Cornish,
# Manx, Breton (low-resource Celtic languages)
model = VitsModel.from_pretrained("facebook/mms-tts-flb-cy")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-flb-cy")
```

## CTranslate2 / faster-whisper for M4 Mac

The canonical KCG production deployment of Whisper is
**faster-whisper** running on the M4 Mac (via MPS):

```python
from faster_whisper import WhisperModel

model = WhisperModel(
    "large-v3",
    device="cpu",  # or "cuda" for GPU
    compute_type="int8",  # 4× speedup, <1% accuracy loss
    cpu_threads=8,  # M4 has 8 performance cores
)

segments, info = model.transcribe(
    "audio.wav",
    beam_size=3,  # smaller beam for faster inference
    vad_filter=True,
)
```

## Common Voice Irish (evaluation set)

The canonical evaluation set for Irish ASR is
**Common Voice 18.0 (Irish)**, hosted on HuggingFace:

```python
from datasets import load_dataset

ds = load_dataset("mozilla-foundation/common_voice_18_0", "ga", split="test")
# Each row: { audio, sentence, ... }
# Compute WER against the model output
```

The KCG quality bar is **≤ 8% WER** on Common Voice Irish
(held-out test split).

## BAML integration

For a BAML pipeline that ingests audio:

```baml
// oideachais/baml_src/audio_extraction.baml
function ExtractSpeechFromAudio(audio_base64: string) -> SpeechTranscript {
  client "openai/gpt-4o-audio-preview"  // or local Whisper via LiteLLM
  prompt #"Transcribe the following audio. Return the text and the detected language."#
}
```

```python
import baml_py
from baml_client import b

with open("audio.wav", "rb") as f:
    audio = baml_py.Audio.from_base64("audio/wav", base64.b64encode(f.read()).decode())
transcript = b.ExtractSpeechFromAudio(audio_base64=audio)
```

## KCG integration

- The `sruth/meaisinfhoghlaim/asr/` service is the canonical ASR
  pipeline (Dagster asset group `asr_assets`)
- The `sruth/meaisinfhoghlaim/ocr/` service also uses ASR for
  scanned-document audio (e.g. dictation recordings)
- The BAML `audio_extraction.baml` schema feeds the
  multimodal extraction pipeline
- The Dagster asset `transcribe_tg4_broadcast` runs daily,
  using the routing rule above

## When to use which engine

✅ **wav2vec2-XLSR-Irish**: oral exams, TG4 broadcasts, any
  accuracy-critical Irish audio
✅ **Whisper large-v3 / faster-whisper**: multilingual
  podcasts, marimo notebooks (CPU-deployable), production
  at scale
✅ **MMS-1B-fl102**: Cornish, Manx, Breton, or other
  low-resource Celtic languages

## Resources

- wav2vec2-XLSR-Irish: <https://huggingface.co/cpierse/wav2vec2-large-xlsr-53-irish>
- Whisper large-v3: <https://huggingface.co/openai/whisper-large-v3>
- faster-whisper: <https://github.com/SYSTRAN/faster-whisper>
- MMS-1B-fl102: <https://huggingface.co/facebook/mms-1b-fl102>
- Common Voice 18 (Irish): <https://huggingface.co/datasets/mozilla-foundation/common_voice_18_0>
- KCG ASR service: `sruth/meaisinfhoghlaim/asr/`
- Related: `.agents/skills/baml/`, `.agents/skills/dagster/`,
  `.agents/skills/modal/`
