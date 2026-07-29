# `meaisinfhoghlaim/` — OCR/HTR/Alignment Sub-Package

> **The canonical post-v7 Python sub-package for the OCR/HTR/alignment work — 24 VISION_MODELS (v4 registry), 6 CLASSICAL_OCR backends, 4 alignment methods, 4 educational agents, 1 BIEP v2 4-path ensemble.** Houses the centralized model registry, the OCR evaluation harness, and the cross-archive alignment primitives.

## Routing

Load this AGENTS.md when:

- You need to add / modify an OCR model or VISION_MODEL entry
- You need to evaluate an OCR backend against the canonical test corpus
- You need to wire a model into a BAML client or agent
- You need to audit the registry for hardcoded model strings

For platform-wide context, load [`../AGENTS.md`](../AGENTS.md).

## Quick start

```bash
mise run cic:ocr:test               # Run pytest on the OCR evaluation harness
mise run cic:ocr:registry-lint      # Verify all 24 VISION_MODELS are live on HF Hub
mise run lint:registry              # Audit agents/, baml_src/, notebooks/ for hardcoded model strings
mise run cic:meaisin:litellm-regenerate  # Regenerate litellm/config.yaml from the v4 VISION_MODELS
```

## Key sources

| Path | Why it matters |
|:--|:--|
| `meaisinfhoghlaim/models/` | The canonical model registry + `MODEL_REGISTRY` Python surface |
| `meaisinfhoghlaim/models/registry.py` | The 24 VISION_MODELS + 6 CLASSICAL_OCR entries (v4) |
| `meaisinfhoghlaim/evaluation/` | The OCR evaluation harness (multi-backend comparison) |
| `meaisinfhoghlaim/alignment/` | The 4 alignment methods (cross-frame, cross-archive, cross-nation, fuzzy) |
| `meaisinfhoghlaim/document_factory/` | The 7 PDF-to-structured converters (Docling, Marker, etc.) |
| `meaisinfhoghlaim/federated/` | The federated OCR ensemble (BIEP v2 4-path) |

## Adjacent specs

- [`centralized-model-registry`](../openspec/specs/centralized-model-registry/spec.md) — the 52-entry model registry that drives this sub-package
- [`meaisinfhoghlaim-ocr-htr`](../openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md) — the 10 OCR backends across the canonical 6 (post-v7 phantom-agents fix)
- [`celtic-language-pipeline`](../openspec/specs/celtic-language-pipeline/spec.md) — the 6 Celtic-language OCR consumer

## DO NOT

- **Never** hardcode a model string anywhere — route through `MODEL_REGISTRY.filter(family=...)` or `model_for(family, role)`.
- **Never** call `HuggingFaceInferenceAPI("model_name")` with a literal string — resolve via the registry first.
- **Never** ship a new OCR backend without registering it in `meaisinfhoghlaim/models/registry.py:CLASSICAL_OCR` (the canonical 6 is enforced by the phantom-agents fix).

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | The `MODEL_REGISTRY` + `schema.py` + `deployment-choice.yaml` triplet |
| [`dignified-python`](../.agents/skills/dignified-python/SKILL.md) | Production Python standards (LBYL, pathlib, ABC interfaces) |
| [`ccc`](../.agents/skills/ccc/SKILL.md) | Semantic code search across the registry + evaluation harness |
| [`browser-tools`](../.agents/skills/browser-tools/SKILL.md) | When evaluating a model on live web pages |

<!-- generated: 2026-07-29; do not hand-edit -->
