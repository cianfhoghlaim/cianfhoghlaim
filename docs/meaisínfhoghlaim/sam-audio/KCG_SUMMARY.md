# SAM-Audio — KCG Summary

## What It Is
SAM-Audio (Meta FAIR) is a foundation model for isolating any sound in audio using text, visual, or temporal prompts. It separates specific sounds from complex audio mixtures based on natural language descriptions, visual cues from video, or time spans. Built on the Perception-Encoder Audio-Visual (PE-AV) backbone, it represents the audio-domain extension of Meta's Segment Anything paradigm.

## Why This Matters for Kings' College Galway
Irish-language speech data is one of the scarcest resources in Celtic NLP. SAM-Audio's text-prompted sound separation could isolate Irish speech from noisy classroom recordings, improving ASR training data quality for Whisper-Irish fine-tuning. The visual prompting capability could segment Irish-language content from educational videos (TG4, RTÉ archive), extracting clean audio for the Common Voice Irish dataset. Temporal prompting enables isolating specific Irish phrases from long-form recordings — critical for building pronunciation datasets for Leaving Certificate Irish oral exam preparation.

## Key Patterns Preserved
- `README.md` — Main documentation: setup, text prompting, visual prompting, temporal prompting, evaluation
- `CONTRIBUTING.md` — Contribution guidelines for Meta open-source projects
- `CODE_OF_CONDUCT.md` — Meta's code of conduct
- `eval/README.md` — Evaluation methodology and benchmarks

## Source Files
Full source removed (2026-06-06). Available at:
- GitHub: https://github.com/facebookresearch/sam-audio
- Hugging Face: https://huggingface.co/facebook/sam-audio-large

## What Was Removed
Python source code (.py, .pxd, .pyx, Cython), CUDA kernels, C++ source, model checkpoint files, audio sample files (.wav, .mp3), Dockerfiles, CI/CD configs, package dependencies (setup.py, pyproject.toml), compiled extensions (.so), evaluation data, Git metadata.
