# Chatterbox — Text-to-Speech (TTS)

## Overview

Chatterbox is a text-to-speech (TTS) model by Resemble AI that generates natural-sounding speech from text input. It supports multiple voices, emotional expressiveness, and fine-grained control over prosody. The model is designed for conversational AI applications requiring human-like speech synthesis.

## Why This Matters for Kings' College Galway

The curriculum platform generates spoken content for Irish-language learners: pronunciation guides for Irish vocabulary, audio versions of study notes for visually impaired students, and spoken feedback from the AI tutor in the web app. Chatterbox converts BAML-extracted Irish text into natural speech, enabling auditory learning pathways alongside visual and text-based ones. The multi-voice support means different characters (teacher, peer student, narrator) can have distinct voices in interactive learning scenarios.

## Key Features

- **Natural speech** — Human-like prosody and intonation
- **Multi-voice** — Multiple speaker profiles for different characters
- **Emotional control** — Adjust expressiveness and tone
- **Lightweight** — 9.7 GB model, efficient inference
- **Resemble AI** — Built by a leading voice AI company

## Installation

```bash
uv add resemble-ai  # or use HuggingFace Transformers
# Model: ResembleAI/chatterbox
```

## Integration with Our Stack

Chatterbox is served via HuggingFace passthrough. The model is cached in `stedding/huggingface/hub/` (~9.7 GB). BAML extraction output feeds into Chatterbox for Irish-language TTS generation, and audio files are stored in Garage S3 for streaming through the web app.

## Upstream

- **Model**: <https://huggingface.co/ResembleAI/chatterbox>
- **Resemble AI**: <https://www.resemble.ai>
- **Latest**: Chatterbox model — TTS with emotional control and multi-voice support

## Screenshot

Chatterbox is a model accessed via Python API. Generated audio is saved as WAV/MP3 files. The model card on HuggingFace shows voice samples and supported parameters (speed, pitch, emotion). Audio quality is evaluated by mean opinion score (MOS) benchmarks.
