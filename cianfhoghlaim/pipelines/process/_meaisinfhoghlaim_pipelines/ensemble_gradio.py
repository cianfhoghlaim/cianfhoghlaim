"""Ensemble Gradio helper.

Codifies the ensemble UI pattern from
`spaces/anti-phish/6_Gradio_Front_End.ipynb:cell-8` (the prior-art project;
pattern B1+B4 from `spaces/README.md` §1.2). Returns a `gradio.Interface`
with **one output Textbox per model** + an Examples component.

Why this exists:

The prior-art Gradio front-end exposes 5 classical ML models + 1 fine-tuned
DistilBERT transformer, all in a single Interface with one output per model.
This is the canonical "compare all my models side by side" UI for any
classification task. The pattern is reusable for any of the 10 OCR models
in `meaisinfhoghlaim/ocr/`, the 12 agents in `meaisinfhoghlaim/agents/`, or
the 3 dbt-built data products in `oideachais/dbt_project/`.

Usage:

    from meaisinfhoghlaim.pipelines.ensemble_gradio import build_ensemble_interface

    def classify_sklearn(text: str) -> str:
        return "phishing" if sklearn_model.predict([text])[0] == 1 else "legit"

    def classify_distilbert(text: str) -> str:
        return distilbert_pipeline(text)[0]["label"]

    iface = build_ensemble_interface(
        title="Phishing email classifier",
        description="Compare 2 models side by side.",
        examples=["top 20 netflix films", "verify your account"],
        models={
            "sklearn": classify_sklearn,
            "distilbert": classify_distilbert,
        },
    )
    iface.launch()

The 3 `gradio-ensemble-pattern` scenarios in
`openspec/changes/celtic-data-engineering-patterns/specs/gradio-ensemble-pattern/spec.md`
are validated by `meaisinfhoghlaim/tests/test_ensemble_gradio.py`.

Anti-pattern (do NOT copy from the prior-art):

- The prior-art notebook saves models to local disk and loads them with
  `urllib.request.urlopen(S3_URL)` at app boot. This is slow and incurs
  egress. Use `huggingface_hub.hf_hub_download` (or the
  `spaces/_common/hf_hub_push.py` helper) instead.

See also:
- `spaces/_common/hf_hub_push.py` (the HF Hub push companion)
- `spaces/anti-phish/6_Gradio_Front_End.ipynb:cell-8` (the prior-art UI)
"""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import gradio as gr


def build_ensemble_interface(
    models: Mapping[str, Callable[[str], Any]],
    examples: Sequence[str],
    title: str,
    description: str = "",
) -> gr.Interface:
    """Build a Gradio Interface with one output Textbox per model.

    Args:
        models: Dict mapping `display_name` -> `predict_fn` (callable that
            takes a `str` and returns anything string-coercible).
        examples: List of example input strings rendered in the Gradio
            Examples component.
        title: Interface title (rendered as the H1).
        description: Optional Markdown description rendered below the title.

    Returns:
        A `gradio.Interface` with:
        - 1 input Textbox (the input text)
        - N output Textboxes (one per model, in the same order as `models`)
        - `allow_flagging="never"` (per the prior-art anti-pattern note)
        - `examples=` populated

    Raises:
        ValueError: If `models` is empty or any `predict_fn` does not
            accept exactly 1 positional argument.
    """
    if not models:
        raise ValueError("models must be non-empty")

    for name, fn in models.items():
        sig = inspect.signature(fn)
        # Count only required positional params (POSITIONAL_ONLY or
        # POSITIONAL_OR_KEYWORD without a default). Optional kwargs with
        # defaults are allowed (e.g. `text: str, threshold: float = 0.5`).
        required_positional = [
            p for p in sig.parameters.values()
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            and p.default is p.empty
        ]
        if len(required_positional) != 1:
            raise ValueError(
                f"model {name!r} must accept exactly 1 required positional argument, "
                f"got {len(required_positional)}"
            )

    model_names = list(models.keys())
    predict_fns = list(models.values())

    def _ensemble_predict(text: str) -> list[Any]:
        return [fn(text) for fn in predict_fns]

    return gr.Interface(
        fn=_ensemble_predict,
        inputs=gr.Textbox(label="Input text", lines=4, placeholder="Type or paste text…"),
        outputs=[gr.Textbox(label=name) for name in model_names],
        examples=[[ex] for ex in examples] if examples else None,
        title=title,
        description=description,
        # Flagging was removed in Gradio 6. In Gradio 4.x the equivalent
        # was `allow_flagging="never"`. The current default is opt-in
        # (no flag button rendered) so omitting the kwarg is correct.
    )


__all__ = ["build_ensemble_interface"]
