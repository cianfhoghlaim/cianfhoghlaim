# KCG_SUMMARY: TTS Dataset Generator — Automated Speech Dataset Creation

## What It Is
A Python tool for automatically generating high-quality Text-to-Speech (TTS) training datasets from raw audio or video files. It segments media into optimal speech chunks using silence detection (pydub), transcribes each segment using OpenAI Whisper, and outputs in LJSpeech format compatible with most TTS frameworks (VITS, Tacotron, Coqui TTS, XTTS). Supports multiple Whisper model sizes and languages, with GPU acceleration.

## Why This Matters for Kings' College Galway
Creating Irish-language speech datasets is the bottleneck for Irish TTS development — manual segmentation and transcription is prohibitively time-consuming. For Kings' College Galway's **teanga** platform, this tool demonstrates the automated pipeline needed to convert existing Irish audio resources (TG4 broadcasts, Raidió na Gaeltachta archives, ABAIR recordings, oral history collections) into training-ready TTS datasets. Combined with the Chatterbox fine-tuning kit, this forms a complete Irish voice cloning pipeline that could produce student-accessible Irish speech synthesis for pronunciation practice, listening comprehension, and accessible curriculum delivery.

## Key Patterns Preserved
- `README.md` — Complete usage guide covering installation (ffmpeg + Python deps), all CLI parameters, audio segmentation algorithm details, Whisper transcription engine, language support (including Irish via Whisper), LJSpeech output format, and integration examples with major TTS frameworks (Coqui TTS, VITS, Tacotron, XTTS)

## Source Files
Full source code was removed on 2026-06-06. The original repository is available at github.com/gokhaneraslan/tts-dataset-generator. This skeleton preserves the technical documentation and integration patterns.

## What Was Removed
- Python source files (main.py and supporting modules)
- Audio processing and segmentation code
- Whisper transcription integration code
- Requirements file
