# Whisper / faster-whisper — Speech Recognition (ASR)

## Overview

Whisper is OpenAI's open-source automatic speech recognition (ASR) model supporting 99 languages, including Irish Gaelic. faster-whisper is a reimplementation using CTranslate2 that achieves 4x speedup and lower memory usage while maintaining identical accuracy. The large-v3 variant provides the highest accuracy across all supported languages.

## Why This Matters for Kings' College Galway

Irish-language audio content — TG4 broadcasts, Raidió na Gaeltachta segments, oral exam recordings, classroom lectures, and student pronunciation practice — needs accurate transcription before it can enter the curriculum pipeline. Whisper's multilingual training includes Irish, and faster-whisper's optimised inference means the 23 GB large-v3 model runs efficiently on the MacBook M4. Transcribed Irish audio feeds into the BAML extraction pipeline for structured content generation and the embedding pipeline for semantic search.

## Key Features

- **99 languages** — Including Irish Gaelic (Gaeilge)
- **large-v3** — Highest accuracy variant, 23 GB
- **faster-whisper** — 4x speedup, lower memory via CTranslate2
- **Word-level timestamps** — Accurate word alignment for subtitles
- **Noise-robust** — Handles background noise and varying audio quality

## Installation

```bash
uv add faster-whisper
# Model downloads automatically on first use
```

## Integration with Our Stack

Whisper is served via HuggingFace passthrough in the LiteLLM gateway's `whisper-irish` alias. The model is cached in `stedding/huggingface/hub/` (23 GB). faster-whisper is used in production for lower latency. Transcriptions feed into BAML extraction and LanceDB indexing.

## Upstream

- **Whisper**: <https://github.com/openai/whisper>
- **faster-whisper**: <https://github.com/SYSTRAN/faster-whisper>
- **Model**: <https://huggingface.co/openai/whisper-large-v3>
- **Latest**: large-v3 (2023) — improved multilingual accuracy, especially for low-resource languages

## Screenshot

Whisper is a CLI and Python library. The CLI: `whisper audio.mp3 --language Irish --model large-v3` outputs transcribed text with timestamps. The Python API returns segments with start/end times and confidence scores. faster-whisper provides identical output at 4x speed.
