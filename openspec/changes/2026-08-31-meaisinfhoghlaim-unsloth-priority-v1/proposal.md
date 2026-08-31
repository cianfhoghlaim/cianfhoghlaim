# Change: meaisinfhoghlaim Unsloth-Priority Refactor v1

> **Status:** AUTHORED, ready for execution.
>
> **Phase 5 of 6** in the v5 refactor umbrella.
>
> **Anchor:** the gemini_hackathon Gemma + Gemini refocus applied
> to `meaisinfhoghlaim/` (the AI/ML services sub-package). Fully
> prioritises Unsloth Studio models (Gemma 4 family) for local
> training/finetuning + OCR ensemble + alignment + evaluation.

## Why

The `meaisinfhoghlaim/` sub-package currently routes OCR ensemble
+ alignment + evaluation + training through the qwen3-vl +
qwen3.6-27b-mtp path (the qwen token plan + the local GGUF).
Per the v5 model priority change:

1. **OCR ensemble** — `Path 3` switches from `qwen3-vl-8b` to
   `gemma-4-26b-a4b-vision` (the new llama-swap primary).
2. **Backends** — `scanned_detector.py` default recommendation
   swaps from `qwen3-vl-8b` to `gemma-4-26b-a4b-vision`.
3. **Datasets** — `irish_processing.py` swap from `qwen3-vl` to
   `gemma-4-e4b-vision`.
4. **Training** — `modal_finetune/finetune_unsloth_local.py` swaps
   the `irish-qwen3.8` checkpoint dir to `irish-gemma-4-26b-a4b`.
5. **Alignment** — `meaisinfhoghlaim/alignment/` adds the
   Gemma 4 + Opus-MT alignment method.
6. **Federated** — `meaisinfhoghlaim/federated/` adds Gemma 4
   fallback when Unsloth Studio is unreachable.
7. **Evaluation** — `meaisinfhoghlaim/evaluation/` adds the
   Gemma 4 + MiniMax + gemini-3.5-flash comparison harness.
8. **Document factory** — `meaisinfhoghlaim/document_factory/`
   adds Document AI (GCP) primary + Docling-serve (local
   opensource) fallback.

## What changes

### §1 — `meaisinfhoghlaim/ocr/ensemble/` Path 3 swap

- `_PATH_TO_BACKEND["gemma4_vision"]` = `("llama-swap",
  "gemma-4-26B-A4B-vision")` — was `qwen3_vl` with
  `qwen3-vl-8b`.
- `PathName` adds `"gemma4_vision"` literal.
- The 4-path ensemble DuckLake landing stays as
  `{baml_canonical,unstract_json,gemma4,gemma4}`.

### §2 — `meaisinfhoghlaim/backends/scanned_detector.py`

- Default `recommended_backend` = `gemma-4-26b-a4b-vision`.
- Removed the `qwen3-vl-8b` branch.

### §3 — `meaisinfhoghlaim/datasets/irish_processing.py`

- `process_with_fallback(image_bytes, "gemma-4-e4b-vision")` —
  was `"qwen3-vl"`.
- The 5-model fallback chain re-ordered: gemma-4-e4b-vision →
  gemma-4-26b-a4b-vision → molmo2-8b → olmocr-2-7b → paddleocr-vl.

### §4 — `meaisinfhoghlaim/training/`

- `modal_finetune/finetune_unsloth_local.py` — default base
  model `cianfhoghlaim/irish-gemma-4-26b-a4b-instruct` (was
  `irish-qwen3.8-27b-instruct`).
- QLoRA + GGUF export pipeline unchanged.
- `training/langfuse_callbacks.py` — model name key swap
  `qwen3-vl` → `gemma-4-e4b-vision`.

### §5 — `meaisinfhoghlaim/alignment/`

- New method `gemma4_opus_mt` — Gemma 4 + Opus-MT
  cross-frame + cross-archive alignment.
- The 4 alignment methods (cross-frame, cross-archive,
  cross-nation, fuzzy) all gain Gemma 4 fallback.

### §6 — `meaisinfhoghlaim/federated/`

- Gemma 4 fallback when Unsloth Studio is unreachable.
- New `get_optimal_for_federated()` helper.

### §7 — `meaisinfhoghlaim/evaluation/`

- The OCR evaluation harness adds Gemma 4 + MiniMax +
  gemini-3.5-flash comparison.

### §8 — `meaisinfhoghlaim/document_factory/`

- Document AI (GCP) primary + Docling-serve (local opensource)
  fallback.
- The 7 PDF-to-structured converters (Docling, Marker, etc.)
  unchanged.

### §9 — `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` delta

- ADDED Requirement: `ocr/ensemble/` MUST use the Gemma 4 vision
  path as the Tier 1 primary.
- ADDED Requirement: `backends/scanned_detector.py` MUST default
  to `gemma-4-26b-a4b-vision`.
- ADDED Requirement: `datasets/irish_processing.py` MUST default
  to the Gemma 4 chain.

## Impact

- 8 modules in `meaisinfhoghlaim/` updated.
- 1 new alignment method (`gemma4_opus_mt`).
- 0 breaking changes (the qwen3-vl paths become tombstones).

## Dependencies

- Phase 1 (`2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1`)
  — the new MODEL_REGISTRY entries.
- Phase 2 (`2026-08-31-baml-primary-alias-and-fallback-v1`) — the
  BAML Primary alias.

## Out of scope

- Wholesale rewrite of meaisinfhoghlaim (this is the OCR +
  training + alignment + federated + evaluation + document_factory
  surfaces).
- Sister-repo transfer (Phase 4 covers that).

## Quality gates (must pass before archive)

```bash
mise run openspec:validate 2026-08-31-meaisinfhoghlaim-unsloth-priority-v1 --strict
mise run lint:registry       # 0 drift
mise run cic:ocr:test        # 8 OCR backends tested
mise run cic:ocr:registry-lint  # Gemma 4 entries live on HF Hub
```

---

*Last updated by build subagent at 2026-08-31.*