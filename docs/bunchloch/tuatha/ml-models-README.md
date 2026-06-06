# ML Models

This directory contains research on AI/ML models for the Anam platform.

## Contents

- `whisper-celtic-asr.md` - Speech recognition for Celtic languages
- `celtic-ocr.md` - Handwriting recognition (FedOCR)
- `qwen-vlm-assessment.md` - Visual assessment validation
- `fibo-asset-generation.md` - Celtic art/NFT generation
- `fine-tuning-strategy.md` - Unsloth + federated approaches

## Model Catalog

### Speech & Language
| Model | Purpose | Languages |
|-------|---------|-----------|
| Whisper (fine-tuned) | ASR | Irish, Scottish Gaelic, Manx, Welsh |
| gaBERT | NLU | Irish |
| UCCIX | Translation | Celtic languages |

### Vision & Generation
| Model | Purpose | Use Case |
|-------|---------|----------|
| Qwen2.5-VL | Assessment | Validate generated content |
| FIBO (Bria) | Image Gen | Celtic art NFTs |
| ColPali | Embeddings | Document visual search |

### Fine-Tuning Stack
- **Unsloth** - Efficient LoRA/QLoRA training
- **MLX** - Apple Silicon optimization
- **Flower** - Federated learning orchestration

## Proof of Learn (PoL) Validation

```
Student Submission (Voice/Handwriting)
    ↓ (Whisper/OCR on-device)
Local Transcription
    ↓ (Consensus validation)
Verified Learning
    ↓ (Tuath minting)
Token Reward
```

## Celtic Art Generation Pipeline

1. **Reference**: SVG Celtic knot patterns
2. **ControlNet**: Enforce topology
3. **FIBO**: JSON-native generation
4. **Metadata**: Embed provenance in NFT
