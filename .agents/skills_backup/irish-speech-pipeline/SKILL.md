---
name: irish-speech-pipeline
description: The KCG Irish speech pipeline: ASR (wav2vec2-XLSR-Irish + Whisper-large-v3) → agent → TTS (ABAIR + Chatterbox) → Pipecat transport. Covers the 4 stages of the curriculum audio loop (record → transcribe → translate → synthesise), the 4 Irish dialects (Connacht, Munster, Ulster, Standard) that the TTS supports, the BAML `audio_extraction.baml` schema, the Pipecat transport contract, and the canonical home for the `voice_agent.py` 30-line stub. Use when adding Irish TTS to a new app, building an audio-first agent, evaluating a new ASR model (e.g. the `wav2vec2-large-xlsr-53-irish` fine-tune), wiring Pipecat to a backend, or implementing the 4 Irish dialects.
---

# Irish Speech Pipeline

## Purpose

The KCG platform's Irish speech pipeline is a **4-stage loop**:
record → transcribe → translate → synthesise. Each stage is a
separate service:

1. **Record** — Pipecat transport (WebRTC + WebSocket)
2. **Transcribe** — ASR (wav2vec2-XLSR-Irish for accuracy + Whisper-large-v3 for speed)
3. **Translate** — the `sruth/cianfhoghlaim/baml_src/audio_extraction.baml` schema
4. **Synthesise** — TTS (ABAIR + Chatterbox)

This skill captures the 4-stage contract, the 4 Irish dialects,
the BAML schema, the Pipecat wiring, and the canonical
add-a-new-stage workflow.

## When to use this skill

Use when you need to:

- "Add Irish TTS to a new app"
- "Build an audio-first agent"
- "Evaluate a new ASR model"
- "Wire Pipecat to a backend"
- "Implement the 4 Irish dialects"
- "Add a new TTS model (e.g. the `mms-tts-ga` model)"

## The 4-stage loop

```
┌──────────┐  Pipecat WebRTC   ┌────────────────┐
│ Pipecat  │  ─────────────►  │ ASR (wav2vec2- │
│ transport│                   │  XLSR-Irish)  │
└──────────┘                   └────────────────┘
                                        │
                                        ▼
                               ┌────────────────┐
                               │ BAML extract   │
                               │ (audio_extrac- │
                               │  tion.baml)    │
                               └────────────────┘
                                        │
                                        ▼
                               ┌────────────────┐
                               │ TTS (ABAIR +   │
                               │  Chatterbox)   │
                               └────────────────┘
                                        │
                                        ▼
                               ┌────────────────┐
                               │ Pipecat audio  │
                               │ output         │
                               └────────────────┘
```

## The 4 Irish dialects (the TTS taxonomy)

The KCG TTS supports 4 Irish dialects (the `IrishDialect` enum in
`sruth/meaisinfhoghlaim/agents/voice_agent.py`):

| Dialect | Region | Population | Notes |
|:--|:--|--:|:--|
| `CONNACHT` | Connacht (Gaeltacht na Gaillimhe + Gaeltacht Mhaigh Eo) | ~20,000 | The "schoolbook" dialect; the default for educational content |
| `MUNSTER` | Munster (Gaeltacht Chiarraí + Gaeltacht Chorcaí) | ~30,000 | The "Kerry" dialect; distinct vowel system |
| `ULSTER` | Ulster (Gaeltacht Dhún na nGall) | ~5,000 | The Donegal dialect; closest to Scottish Gaelic |
| `STANDARD` | The official "An Caighdeán Oifigiúil" | n/a | The standard Irish used in schools + government |

The 4 dialects are exposed via the `/tts/synthesize?dialect=<one-of-4>`
endpoint in `sruth/meaisinfhoghlaim/agents/api/routes/tts.py`.

## The ASR backend (wav2vec2-XLSR-Irish)

The canonical ASR model is `wav2vec2-large-xlsr-53-irish` (the
Common Voice Irish fine-tune). The model is registered in
`sruth/meaisinfhoghlaim/asr/model_registry.py:ASR_MODELS`.

```python
# sruth/meaisinfhoghlaim/asr/model_registry.py
ASR_MODELS["wav2vec2-xlsr-irish"] = Wav2Vec2XLSRIrishASR(
    name="wav2vec2-xlsr-irish",
    backend=ASRBackend.TRANSFORMERS,
    hf_repo="ciaran-griffin/wav2vec2-large-xlsr-53-irish",
    sample_rate=16000,
    language="ga",
)
```

The ASR is wrapped in `sruth/meaisinfhoghlaim/agents/voice_agent.py:ASRPipeline`
which exposes the `transcribe(audio_bytes) -> str` method.

## The BAML extraction schema (`audio_extraction.baml`)

```baml
// sruth/cianfhoghlaim/baml_src/audio_extraction.baml
class AudioSegment {
    start_ms int
    end_ms int
    text string
    confidence float
    dialect Dialect
}

class Dialect {
    name string  // "CONNACHT" | "MUNSTER" | "ULSTER" | "STANDARD"
    confidence float
}

function ExtractAudioSegments(audio_url: string) -> AudioSegment[] {
    client "openai/gpt-4o-audio"
    prompt #"
    Transcribe the Irish audio at {{ audio_url }}.
    Return the segments with start_ms, end_ms, text, confidence, and dialect.
    "#
}
```

The BAML function is invoked from `sruth/meaisinfhoghlaim/pipelines/transcript_aligner.py:align_transcript(audio_url)`.

## The TTS backend (ABAIR + Chatterbox)

The KCG TTS uses 2 backends:

- **ABAIR** (the Údarás na Gaeltachta TTS) — the canonical
  Irish-language TTS, 4 dialects, 22kHz mono WAV
- **Chatterbox** (the multilingual fallback) — 24kHz, all 6
  Celtic languages, used when ABAIR is unavailable for a dialect

```python
# meaisinfoghlam/agents/api/services/chatterbox.py
class TTSSynthesizer:
    def synthesize(self, text: str, dialect: str) -> bytes:
        if ABAIR_AVAILABLE and dialect in ABAIR_DIALECTS:
            return ABAIR.synthesize(text, dialect)
        return Chatterbox.synthesize(text, dialect)
```

The TTS is exposed via the `/tts/synthesize` + `/tts/pronounce` +
`/tts/dialects` endpoints in `sruth/meaisinfhoghlaim/agents/api/routes/tts.py`.

## The Pipecat transport contract

The `pipecat` service is exposed at `pipecat.cianfhoghlaim.ie:8765`
(WebRTC + WebSocket). The contract:

- **Inbound:** WebRTC audio stream (Opus codec, 48kHz stereo) or
  WebSocket binary frames (raw PCM, 16kHz mono)
- **Outbound:** WebRTC audio stream (Opus codec, 48kHz stereo) or
  WebSocket binary frames (raw PCM, 24kHz mono)

The Pipecat transport is wired in
`sruth/meaisinfhoghlaim/agents/voice_agent.py:PipecatTransport`.

## Worked example: add a new TTS model (mms-tts-ga)

1. Add the model to `sruth/meaisinfhoghlaim/tts/model_registry.py:TTS_MODELS`:

   ```python
   TTS_MODELS["mms-tts-ga"] = MMSTtsGaTTS(
       name="mms-tts-ga",
       backend=TTSBackend.TRANSFORMERS,
       hf_repo="facebook/mms-tts-ga",
       sample_rate=16000,
       language="ga",
   )
   ```

2. Update `sruth/meaisinfhoghlaim/agents/api/services/chatterbox.py` to
   add the new model to the fallback chain:

   ```python
   if text.startswith("[ga]") and "mms-tts-ga" in TTS_MODELS:
       return TTS_MODELS["mms-tts-ga"].synthesize(text, dialect)
   ```

3. Add a new test in `sruth/meaisinfhoghlaim/tests/test_tts.py` that
   synthesises a sample Irish sentence with `mms-tts-ga` and
   verifies the 4-dialect output.

4. Update `sruth/meaisinfhoghlaim/llama-swap-config.yaml` to add the
   GGUF-quantised variant.

5. Add a BAML extraction function in
   `sruth/cianfhoghlaim/baml_src/audio_extraction.baml` for the new model
   (if needed).

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| ASR returns empty string | The audio is too quiet | Boost the audio gain in Pipecat before sending |
| TTS synthesises wrong dialect | The dialect parameter is missing from the request | Pass `dialect=CONNACHT` (or one of the 4) |
| ABAIR is unavailable | The Údarás server is down | Fall back to Chatterbox |
| The Pipecat connection drops | The WebRTC NAT traversal failed | Add a TURN server (per the Pipecat docs) |
| The transcript alignment is off | The audio sample rate is wrong (44.1kHz instead of 16kHz) | Resample the audio to 16kHz before ASR |

## Cross-references

- `.agents/skills/celtic-language-ai/SKILL.md` — the 6 Celtic languages + 8 ISO codes
- `.agents/skills/irish-llm-on-device/SKILL.md` — the Apple Silicon MLX stack
- `.agents/skills/asr/SKILL.md` — the ASR stack (wav2vec2 + Whisper)
- `.agents/skills/tts/SKILL.md` — the general TTS patterns
- `sruth/meaisinfhoghlaim/agents/voice_agent.py` — the canonical ASR + TTS + Pipecat glue
- `sruth/meaisinfhoghlaim/asr/model_registry.py` — the ASR model registry
- `sruth/meaisinfhoghlaim/tts/model_registry.py` — the TTS model registry
- `sruth/meaisinfhoghlaim/agents/api/services/chatterbox.py` — the TTS synthesizer
- `sruth/cianfhoghlaim/baml_src/audio_extraction.baml` — the audio extraction BAML schema
- `sruth/meaisinfhoghlaim/llama-swap-config.yaml` — the 11 GGUF models for Apple Silicon
