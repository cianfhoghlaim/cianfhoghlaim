# KCG_SUMMARY: Chatterbox TTS — Fine-Tuning & Inference Kit

## What It Is
A modular infrastructure for fine-tuning the Chatterbox TTS (Text-to-Speech) model with custom datasets, specifically designed to support new languages by building custom tokenizer structures and expanding model vocabulary. Uses an offline preprocessing strategy (speaker embeddings, acoustic tokens) for maximised GPU utilisation, with Voice Encoder (VE), T3 Transformer, and S3Gen vocoder components. Integrates with the TTS Dataset Generator for automated dataset creation from audio/video files.

## Why This Matters for Kings' College Galway
Irish-language speech synthesis is critically underdeveloped — there are no production-quality Irish TTS voices available. For Kings' College Galway's **teanga** platform, the Chatterbox fine-tuning pipeline provides the technical foundation for training custom Irish-language voices using existing Irish speech corpora (ABAIR, Common Voice Irish, TG4 archives). A high-quality Irish TTS voice would enable: spoken Irish feedback in language learning exercises, audio versions of Irish-language curriculum materials for accessibility, pronunciation guides for students, and a voice interface for the entire teanga platform. The multi-language tokenizer design directly supports Irish's unique orthography (síneadh fada, séimhiú, urú).

## Key Patterns Preserved
- `README.md` — Complete end-to-end guide covering installation, dataset preparation (LJSpeech format), training with vocab expansion for new languages, inference with Silero VAD, model architecture (VE/T3/S3Gen), custom tokenizer creation, and multi-language support for 23+ languages

## Source Files
Full source code was removed on 2026-06-06. The original repository is available at github.com/gokhaneraslan/chatterbox-finetuning. This skeleton preserves the technical documentation and training methodology.

## What Was Removed
- Python training and inference scripts (train.py, inference.py, setup.py)
- Source modules (config, dataset, model, preprocess, utils, tokenizer)
- Pre-trained model weights (.safetensors files)
- Tokenizer configuration (tokenizer.json)
- Requirements file
