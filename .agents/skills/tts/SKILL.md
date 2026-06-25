---
name: tts
description: Text-to-speech synthesis via Chatterbox (primary, Resemble AI 9.7 GB), MMS-TTS, or Piper. Use for Irish-language pronunciation guides, audio study notes, AI tutor speech, or any KCG pipeline that converts BAML-extracted text to audio.
---

# TTS — Text-to-Speech

## When to use this skill

Use when you need to:

- "Generate an Irish pronunciation guide for a BAML-extracted
  curriculum passage"
- "Add AI tutor speech to a marimo notebook"
- "Create audio study notes from BAML-extracted text"
- "Stream TTS to a TanStack Start front-end"
- "Run on-device TTS (Chatterbox is too big for CPU; use Piper
  for CPU-only)"

## Overview

The KCG stack supports 3 TTS engines, with the canonical
choice being **Chatterbox** (Resemble AI's open-source TTS
model, 9.7 GB, MIT-licensed, 6+ voices, emotion control).

| Engine | Size | Quality | Speed | Best for |
|:--|--:|:--|:--|:--|
| **Chatterbox** | 9.7 GB | High | GPU | Irish pronunciation, AI tutor |
| **MMS-TTS** | 1.2 GB | Good | CPU | Multilingual fallback |
| **Piper** | 60 MB | Decent | CPU (fast) | On-device, low-latency |

## Chatterbox (canonical KCG choice)

```python
import torchaudio
from chatterbox.tts import ChatterboxTTS

# Load the model (one-time, GPU recommended)
model = ChatterboxTTS.from_pretrained(device="cuda")

# Synthesise
text = "An bhfuil cead agam dul go dtí an leithreas?"
wav = model.generate(text)
torchaudio.save("output.wav", wav, model.sr)
```

### Voices (Chatterbox)

| Voice ID | Language | Notes |
|:--|:--|:--|
| `ga-IE-female-1` | Irish | Native speaker, ~6hr training data |
| `ga-IE-male-1` | Irish | Native speaker, Connemara dialect |
| `en-US-female-1` | English | Default |
| `en-US-male-1` | English | |
| `cy-GB-female-1` | Welsh | |
| `gd-GB-female-1` | Scottish Gaelic | |

### Emotion + prosody control

```python
wav = model.generate(
    text,
    exaggeration=0.6,   # 0.0 = flat, 1.0 = very expressive
    cfg_weight=0.5,    # classifier-free guidance
    temperature=0.8,   # sampling temperature
    top_p=0.95,
)
```

## BAML→TTS pipeline (KCG canonical)

```python
from baml_client import b
import baml_py
import torchaudio
from chatterbox.tts import ChatterboxTTS

async def synthesize_curriculum_passage(
    baml_output: CurriculumPassage,
    voice: str = "ga-IE-female-1",
) -> str:
    """Render a BAML-extracted curriculum passage as audio; return the S3 URL."""
    # 1. Build the text from the BAML output
    text = baml_output.introduction + "\n\n" + baml_output.explanation
    text = text.strip()

    # 2. Synthesise
    model = ChatterboxTTS.from_pretrained(device="cuda")
    wav = model.generate(
        text,
        voice=voice,
        exaggeration=0.5,
    )

    # 3. Upload to Garage S3 with a deterministic key
    key = f"kcg-tts/{voice}/{hashlib.sha256(text.encode()).hexdigest()}.wav"
    s3_url = upload_to_garage(key, wav, content_type="audio/wav")

    return s3_url
```

## FastAPI endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "ga-IE-female-1"
    exaggeration: float = 0.5


class SynthesizeResponse(BaseModel):
    url: str
    duration_sec: float
    voice: str


@app.post("/api/tts/synthesize", response_model=SynthesizeResponse)
async def synthesize(req: SynthesizeRequest):
    if not req.text.strip():
        raise HTTPException(400, "Empty text")
    # ... (call the BAML→TTS pipeline) ...
    return SynthesizeResponse(url=url, duration_sec=duration, voice=req.voice)
```

## Marimo integration

The marimo skill includes a `mo.ui.chat` with optional audio
output. To add TTS:

```python
@app.cell
def _():
    import requests
    if chat.value:
        last = chat.value[-1]
        response = requests.post(
            "http://localhost:8000/api/tts/synthesize",
            json={"text": last.content, "voice": "ga-IE-female-1"},
        )
        if response.ok:
            audio_url = response.json()["url"]
            mo.Html(f'<audio controls src="{audio_url}"></audio>')
    return
```

## GPU considerations

Chatterbox requires a GPU for acceptable latency:
- A100: ~10× real-time (1 min audio in 6s)
- H100: ~20× real-time
- M4 Mac (MPS): ~1.5× real-time (usable for dev, slow for prod)
- CPU: ~0.1× real-time (not viable)

For production, use Modal H100 (see
`.agents/skills/modal/SKILL.md`) for burst TTS workloads.

## When to use which engine

✅ **Chatterbox**: high-quality Irish pronunciation, AI
  tutor speech, audio study notes
✅ **MMS-TTS**: low-resource Celtic languages (Cornish,
  Breton, Manx); CPU deployment
✅ **Piper**: ultra-low-latency (sub-100ms), on-device
  pronunciation hints in marimo

## Resources

- Chatterbox GitHub: <https://github.com/resemble-ai/chatterbox>
- Chatterbox models: <https://huggingface.co/ResembleAI/chatterbox>
- MMS-TTS: <https://huggingface.co/facebook/mms-tts>
- Piper: <https://github.com/rhasspy/piper>
- KCG TTS service: `sruth/meaisinfhoghlaim/tts/` (planned)
- BAML→TTS pipeline example: `sruth/meaisinfhoghlaim/pipelines/`
- Related: `.agents/skills/baml/`, `.agents/skills/modal/`
