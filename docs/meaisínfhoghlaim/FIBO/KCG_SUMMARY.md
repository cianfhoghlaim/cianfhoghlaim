# FIBO — KCG Summary

## What It Is
FIBO (Bria AI) is the first open-source, JSON-native text-to-image model trained exclusively on long structured captions (1,000+ words). With 8B parameters, it enables precise, reproducible control over lighting, composition, colour, and camera settings via VLM-guided JSON prompting. Supports iterative refinement, disentangled attribute control, and image-inspired generation. Trained on 100% licensed data.

## Why This Matters for Kings' College Galway
Structured, controllable image generation opens possibilities for generating culturally authentic Irish-language educational illustrations — from Celtic art and historical reconstructions to Leaving Certificate biology diagrams with bilingual labels. The JSON-structured prompt format aligns with the platform's BAML/structured-output pipeline for education content. FIBO's fine-tuning support (LoRA/LoKr) could adapt the model to Irish artistic styles and medieval manuscript illumination patterns, creating unique visual assets for Celtic Studies curriculum. The licensed-data training provides enterprise-grade legal clarity for commercial educational publishing.

## Key Patterns Preserved
- `README.md` — Full model documentation: features, quick start, inference, ComfyUI integration
- `CONTRIBUTING.md` — Contribution guidelines for the FIBO open-source project
- `src/fine_tuning/README.md` — Fine-tuning guide: LoRA/LoLKr adapters, regional prompting, inference
- `examples/README.md` — Example usage patterns and prompts

## Source Files
Full source removed (2026-06-06). Available at:
- GitHub: https://github.com/briaai/FIBO
- Hugging Face: https://huggingface.co/briaai/FIBO

## What Was Removed
Python source code, model weights/checkpoints (58M of .safetensors, .bin files), ComfyUI node definitions, Dockerfiles, CI/CD configs, example images (PNG/JPEG), package dependencies (pyproject.toml, requirements.txt), evaluation scripts, Git metadata.
