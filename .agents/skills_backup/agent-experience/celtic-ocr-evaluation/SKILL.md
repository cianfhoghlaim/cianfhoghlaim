---
name: celtic-ocr-evaluation
description: The KCG Celtic OCR evaluation harness for the 9-model × 6-backend registry in `sruth/meaisinfhoghlaim/ocr/`. Covers the 9 OCR models (olmocr-7b, qwen2.5-vl-7b, qwen2.5-vl-7b-mlx, deepseek-ocr, granite-docling, gpt-4o, claude-3.5-sonnet, llama-3.2-vision-11b, uccix-13b), the 6 backends (litellm, mlx, transformers, ollama, openai, anthropic), the Irish-specific evaluation metrics in `gaelic_metrics.py` (CER, WER, tironian detection, punctum-delens normalisation, fada consistency), the `_normalize_irish_text` (NFC) rules, the 3-method comparison runner, and the canonical home for the 9-model × 6-backend registry. Use when adding the 11th OCR model, interpreting a CER number, comparing 2 OCR backends on the same document, or evaluating a new fine-tune (e.g. the `models/llama-3.2-3b-irish` LoRA).
---

# Celtic OCR Evaluation

## Purpose

The `sruth/meaisinfhoghlaim/ocr/` directory houses a **9-model × 6-backend**
OCR registry + a Celtic-specific evaluation harness. This skill
captures the registry anatomy, the evaluation metrics, the
3-method comparison runner, and the canonical add-a-new-model
workflow. There is no other skill that documents the 9-model
registry, the `gaelic_metrics.py` evaluation, or the `_normalize_irish_text`
NFC rules.

## When to use this skill

Use when you need to:

- "Add the 11th OCR model"
- "Compare 2 OCR backends on the same document"
- "Interpret a CER number for Irish text"
- "Evaluate a new fine-tune (e.g. the `llama-3.2-3b-irish` LoRA)"
- "Understand the difference between CER and WER for Celtic text"
- "Test a new Irish-language HTR dataset"

## The 9 OCR models (the registry)

| Model | Backend | License | Notes |
|:--|:--|:--|:--|
| `olmocr-7b` | transformers | Apache 2.0 | The Allen AI document OCR model; the default for new documents |
| `qwen2.5-vl-7b` | transformers + mlx | Apache 2.0 | The Qwen2.5-VL vision-language model; fast + good |
| `qwen2.5-vl-7b-mlx` | mlx | Apache 2.0 | The Apple Silicon MLX variant of Qwen2.5-VL |
| `deepseek-ocr` | transformers | MIT | The DeepSeek OCR model; best for handwritten text |
| `granite-docling` | transformers | Apache 2.0 | The IBM Docling model; best for tables + structured forms |
| `gpt-4o` | openai | Proprietary | The OpenAI multimodal model; the highest-accuracy fallback |
| `claude-3.5-sonnet` | anthropic | Proprietary | The Anthropic multimodal model; the best document-Q&A model |
| `llama-3.2-vision-11b` | transformers + litellm | Llama community | The Meta Vision model; good for hand-written Irish |
| `uccix-13b` | transformers | CC-BY-NC-4.0 | The UCCIX (Údarás na Gaeltachta) Llama2-13B fine-tune for Irish; the canonical Irish-text model |

The 9 models are registered in `sruth/meaisinfhoghlaim/ocr/model_registry.py`
via the `OCR_MODELS` dict (the canonical home for the registry).

## The 6 backends (the runtime)

| Backend | Implementation | Use when |
|:--|:--|:--|
| `litellm` | The LiteLLM proxy at `litellm.cianfhoghlaim.ie:4000` | Production (the default) |
| `mlx` | Apple Silicon MLX inference (the `mlx-omni` server at port 10240) | The bunchloch M4 MacBook for fast local inference |
| `transformers` | Direct HuggingFace transformers | Local dev + the on-prem OCI server |
| `ollama` | The Ollama server at `ollama.cianfhoghlaim.ie:11434` | Local-only models (e.g. uccix-13b) |
| `openai` | The OpenAI API at `api.openai.com` | The gpt-4o fallback |
| `anthropic` | The Anthropic API at `api.anthropic.com` | The claude-3.5-sonnet fallback |

The 6 backends are registered in `sruth/meaisinfhoghlaim/ocr/model_registry.py`
via the `ModelBackend` enum (the canonical home).

## The 4 Irish-specific metrics (`gaelic_metrics.py`)

The `sruth/meaisinfhoghlaim/ocr/gaelic_metrics.py` module computes 4
Celtic-specific metrics on top of the standard CER/WER:

1. **CER** (Character Error Rate) — `edit_distance(ground_truth, pred) / len(ground_truth)`
2. **WER** (Word Error Rate) — same but at the word level
3. **Tironian detection** — the `⁊` character (the Irish/Scottish
   abbreviation for "agus" / "and") should not be confused with
   `7` or `+`; the metric is `1.0 - (correct_tironian_count / expected_tironian_count)`
4. **Punctum-delens normalisation** — the `ḃ`, `ċ`, `ḋ`, `ġ`, `ṁ`, `ṗ`, `ṡ`, `ṫ`
   characters (Irish "dot-above" consonants) should be normalised
   to their non-dotted counterparts before CER; the metric is
   `1.0 - (correctly_dotted_count / total_dotted_count)`
5. **Fada consistency** — the vowels `á`, `é`, `í`, `ó`, `ú` should
   appear in the predicted text where they appear in the
   ground truth; the metric is `1.0 - (correctly_fada_count / total_fada_count)`

The 4 metrics are reported as a single `GaelicOcrScore` dataclass.

## The 3-method comparison runner (`comparison_runner.py`)

```python
# sruth/meaisinfhoghlaim/ocr/comparison_runner.py
from sruth.meaisinfhoghlaim.ocr.model_registry import OCR_MODELS
from sruth.meaisinfhoghlaim.ocr.gaelic_metrics import compute_gaelic_score

def compare_3_methods(
    image_path: str,
    method_a: str,  # e.g. "olmocr-7b"
    method_b: str,  # e.g. "qwen2.5-vl-7b"
    method_c: str,  # e.g. "uccix-13b"
) -> ComparisonResult:
    """Run 3 OCR methods on the same image; return a ComparisonResult with the 5 metrics per method."""
    results = {}
    for method_name in [method_a, method_b, method_c]:
        model = OCR_MODELS[method_name]
        text = model.recognize(image_path)
        score = compute_gaelic_score(ground_truth=ground_truth, prediction=text)
        results[method_name] = score
    return ComparisonResult(results=results, winner=min(results, key=lambda k: results[k].cer))
```

The runner is invoked by `sruth/meaisinfhoghlaim/evaluation/ragas_pipeline.py`
to compare the 9 models on the same curriculum documents.

## The `_normalize_irish_text` NFC rules

```python
# sruth/meaisinfhoghlaim/ocr/gaelic_metrics.py
def _normalize_irish_text(text: str) -> str:
    """Normalise Irish text for CER/WER. Apply NFC + lowercase + strip punctuation."""
    import unicodedata
    text = unicodedata.normalize("NFC", text)
    text = text.lower()
    # Strip all punctuation except the fada + the punctum-delens
    text = "".join(c for c in text if c.isalnum() or c in "áéíóúḃĊḊĠṀṖṠṪ")
    return text
```

The NFC normalisation is critical because Irish has 8 dotted
consonants (`ḃ`, `ċ`, `ḋ`, `ġ`, `ṁ`, `ṗ`, `ṡ`, `ṫ`) that can be
misencoded as the non-dotted base + a combining dot above (NFD).
Without NFC, the CER is artificially inflated.

## Worked example: add the 11th OCR model

1. Add the model to `sruth/meaisinfhoghlaim/ocr/model_registry.py:OCR_MODELS`:

   ```python
   OCR_MODELS["gemma-3-vision"] = GemmaVisionModel(
       name="gemma-3-vision",
       backend=ModelBackend.TRANSFORMERS,
       hf_repo="google/gemma-3-vision-9b-it",
       license="gemma-terms",
       languages_supported=["en", "ga", "gd", "cy", "br", "kw", "gv"],
   )
   ```

2. Add the BAML extraction function (if needed) in
   `sruth/oideachais/baml_src/ocr_validation.baml`.

3. Add a new test in `sruth/meaisinfhoghlaim/tests/test_ensemble_gradio.py`
   that runs the 3-method comparison with `gemma-3-vision` as one
   of the 3 methods.

4. Update the openspec change `meaisinfhoghlaim-ocr-spec-clarify` to
   bump the registry to 10 models (or, since we're adding
   `gemma-3-vision`, to 10 + the planned additions, document the
   target of 11).

5. Update `sruth/meaisinfhoghlaim/llama-swap-config.yaml` to add the
   GGUF-quantised variant for Apple Silicon.

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| CER > 50% on a known document | The model is not normalising NFC | Call `_normalize_irish_text()` before CER |
| Tironian detection = 0.0 | The model is OCRing `⁊` as `+` or `7` | Switch to `uccix-13b` or `qwen2.5-vl-7b` (better at tironian) |
| WER is fine but CER is bad | The model is collapsing 2+ words into 1 (common with `granite-docling`) | Switch to `olmocr-7b` |
| The model is hanging at load time | The Apple Silicon MLX variant is being loaded on Linux | Use the `transformers` backend instead |
| The 3-method comparison reports all 3 with the same CER | The ground truth is the same for all 3 (test bug) | Pass different ground truths |

## Cross-references

- `.agents/skills/document-intelligence/SKILL.md` — the general doc-AI patterns
- `.agents/skills/irish-llm-on-device/SKILL.md` — the Apple Silicon MLX stack
- `.agents/skills/asr/SKILL.md` — the ASR stack (for the audio side of the curriculum)
- `.agents/skills/unsloth/SKILL.md` — for the `llama-3.2-3b-irish` fine-tune workflow
- `sruth/meaisinfhoghlaim/ocr/model_registry.py` — the canonical 9-model × 6-backend registry
- `sruth/meaisinfhoghlaim/ocr/gaelic_metrics.py` — the 5 Celtic metrics
- `sruth/meaisinfhoghlaim/ocr/comparison_runner.py` — the 3-method comparison runner
- `sruth/meaisinfhoghlaim/llama-swap-config.yaml` — the 11 GGUF-quantised models for Apple Silicon
- `sruth/oideachais/baml_src/ocr_validation.baml` — the OCR validation BAML schema
