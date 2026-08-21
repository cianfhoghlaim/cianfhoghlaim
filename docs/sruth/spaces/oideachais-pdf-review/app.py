"""Gradio HF Space for human review of Stage 4 mismatches.

Per `openspec/specs/oideachais-pdf-processing/spec.md` — Requirement:
"Gradio interface for human review".

Human reviewers can:
- Approve / reject topic validations flagged in Stage 4
- Correct mis-categorised questions
- Add notes to marking-scheme ambiguities
- Export validated records back to the lakehouse

Deployed to HuggingFace Spaces with ZeroGPU (free tier).

The in-app LLM features use HuggingFace transformers directly
(loaded fresh on each @spaces.GPU call):
- `unsloth/gemma-3-4b-it-GGUF` for the in-app "suggested correction" feature
- `unsloth/gemma-4-26B-A4B-it-GGUF` for the "explain why this is mis-categorised" feature

Per the v4 trim (2026-06-29), the registry now has 20 models
that fit on M4 Max 48GB; the 4 largest (qwen3-vl-235b-a22b, glm-4.6v-full,
qwen3.6-35b-a3b-mtp, gemma-4-31B) are removed since they don't fit.

Deployed via the `spaces-cicd-pipeline` spec at
`infrastructure/ci/spaces-sync.yml`.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import gradio as gr

logger = logging.getLogger(__name__)


# Default Space env vars (overridden by HuggingFace Space settings).
# The two model strings are resolved via MODEL_REGISTRY (the
# centralized-model-registry openspec change). The SUGGESTION_MODEL
# env var can still override (for prod / A/B test convenience).
def _suggestion_model() -> str:
    override = os.getenv("SUGGESTION_MODEL")
    if override:
        return override
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY

        return MODEL_REGISTRY.resolve("text_llm", "pdf_review_suggestion")
    except Exception:  # noqa: BLE001 — registry unavailable in dev
        return "unsloth/gemma-3-4b-it-GGUF"


def _explanation_model() -> str:
    override = os.getenv("EXPLANATION_MODEL")
    if override:
        return override
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY

        return MODEL_REGISTRY.resolve("text_llm", "pdf_review_explanation")
    except Exception:  # noqa: BLE001 — registry unavailable in dev
        return "unsloth/gemma-4-26B-A4B-it-GGUF"


SUGGESTION_MODEL = _suggestion_model()
EXPLANATION_MODEL = _explanation_model()
SUGGESTION_DURATION = int(os.getenv("SUGGESTION_DURATION", "60"))  # seconds
EXPLANATION_DURATION = int(os.getenv("EXPLANATION_DURATION", "120"))

# Stub for now: in production this reads from
# `motherduck://oideachais.pdf_processing.*.validated`
MISMATCHED_RECORDS: list[dict[str, Any]] = [
    {
        "id": "irish_2024_p1_q3",
        "subject": "Irish",
        "year": 2024,
        "paper": "paper-1",
        "question_number": 3,
        "original_topic": "Litríocht na Nua-Ghaeilge",
        "suggested_topic": "Litríocht Chomhaimseartha",
        "match_score": 0.78,
        "reason": "Question 3 of the 2024 LC Irish paper-1 mentions both Nua-Ghaeilge and Chomhaimseartha literature; the BAML extraction picked the older period but the actual question is about contemporary poetry.",
    },
    {
        "id": "maths_2024_p2_q5b",
        "subject": "Mathematics",
        "year": 2024,
        "paper": "paper-2",
        "question_number": 5,
        "part_label": "(b)",
        "original_topic": "Integration",
        "suggested_topic": "Differential Equations",
        "match_score": 0.81,
        "reason": "Question 5(b) on the 2024 LC Maths paper-2 asks to solve a first-order differential equation; the BAML extraction mis-tagged it as Integration.",
    },
]


# ============================================================================
# ZeroGPU-backed inference
# ============================================================================
# Per .agents/skills/huggingface-zerogpu/SKILL.md, the @spaces.GPU decorator
# is required for any ML inference in a ZeroGPU Space. The model is loaded
# fresh on each call (module-scope warmup doesn't carry across the worker
# boundary).
#
# The model is loaded via the `transformers` library (the ZeroGPU backing
# card is CUDA-only). The model name uses the v4 Unsloth GGUF HF IDs.
# ============================================================================


def _load_suggestion_pipeline():
    """Lazy-load the suggestion pipeline (Gemma 3 4B) for ZeroGPU."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    tokenizer = AutoTokenizer.from_pretrained(SUGGESTION_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        SUGGESTION_MODEL,
        torch_dtype=torch.float16,
        device_map="cuda",
    )
    return tokenizer, model


def _load_explanation_pipeline():
    """Lazy-load the explanation pipeline (Gemma 4 26B-A4B MoE) for ZeroGPU."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    tokenizer = AutoTokenizer.from_pretrained(EXPLANATION_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        EXPLANATION_MODEL,
        torch_dtype=torch.float16,
        device_map="cuda",
    )
    return tokenizer, model


def get_suggested_correction(record: dict[str, Any]) -> str:
    """Use Gemma 3 4B (Unsloth GGUF) on ZeroGPU to suggest a topic correction.

    Args:
        record: A mismatched BAML record from Stage 4

    Returns:
        A 1-2 sentence suggested correction
    """
    # Stub: in production this calls ZeroGPU with @spaces.GPU
    # For now, return the suggested topic from the record
    return f"Suggested correction: {record.get('suggested_topic', 'unknown')}"


def explain_miscategorisation(record: dict[str, Any]) -> str:
    """Use Gemma 4 26B-A4B (Unsloth GGUF) on ZeroGPU to explain why the record is mis-categorised.

    Args:
        record: A mismatched BAML record from Stage 4

    Returns:
        A 2-3 sentence explanation
    """
    # Stub: in production this calls ZeroGPU with @spaces.GPU
    return f"Explanation: {record.get('reason', 'unknown')}"


def approve_correction(record_id: str, corrected_topic: str) -> str:
    """Approve a correction and write it back to DuckLake.

    Args:
        record_id: The record ID (e.g. "irish_2024_p1_q3")
        corrected_topic: The corrected topic (e.g. "Litríocht Chomhaimseartha")

    Returns:
        Status message
    """
    # Stub: in production this writes to
    # `motherduck://oideachais.pdf_processing.{subject}.{year}.{paper}.validated`
    return f"Approved correction for {record_id}: {corrected_topic}"


def build_interface() -> gr.Blocks:
    """Build the Gradio interface for HF Spaces ZeroGPU.

    The @spaces.GPU decorator is on the model-loading functions (lazy).
    The Gradio UI itself runs on CPU and just calls the GPU-backed
    functions when the user clicks the buttons.

    Returns:
        The Gradio Blocks interface
    """
    with gr.Blocks(title="Oideachais PDF Review", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            f"""
            # Oideachais PDF Review

            Human review interface for Stage 4 mismatches of the 6-stage
            PDF processing pipeline. Reviewers can:
            - Approve / reject topic validations flagged in Stage 4
            - Correct mis-categorised questions
            - Add notes to marking-scheme ambiguities
            - Export validated records back to the lakehouse

            **Models used (Unsloth GGUFs via HF Spaces ZeroGPU):**
            - `{SUGGESTION_MODEL}` (4 GB) — in-app "suggested correction" feature
            - `{EXPLANATION_MODEL}` (14 GB MoE) — "explain why this is mis-categorised" feature

            **Registry:** 20 v4 models that fit on M4 Max 48 GB
            (the 4 largest — 235B, 107B, 22GB marginal, 19GB marginal —
            were removed in the 2026-06-29 trim).
            """
        )

        with gr.Row():
            mismatch_dropdown = gr.Dropdown(
                choices=[r["id"] for r in MISMATCHED_RECORDS],
                value=MISMATCHED_RECORDS[0]["id"] if MISMATCHED_RECORDS else None,
                label="Mismatched record",
            )
            refresh_btn = gr.Button("Refresh list", variant="secondary")

        with gr.Row():
            with gr.Column():
                record_display = gr.JSON(
                    label="Record details",
                    value=MISMATCHED_RECORDS[0] if MISMATCHED_RECORDS else {},
                )

        with gr.Row():
            suggest_btn = gr.Button("Get suggested correction", variant="primary")
            explain_btn = gr.Button("Explain why this is mis-categorised", variant="primary")

        with gr.Row():
            suggestion_output = gr.Textbox(label="Suggested correction", lines=2, interactive=False)
            explanation_output = gr.Textbox(label="Explanation", lines=4, interactive=False)

        with gr.Row():
            corrected_topic = gr.Textbox(
                label="Corrected topic (edit before approving)",
                value=MISMATCHED_RECORDS[0].get("suggested_topic", "")
                if MISMATCHED_RECORDS
                else "",
            )
            approve_btn = gr.Button("Approve correction", variant="primary")
            reject_btn = gr.Button("Reject correction", variant="stop")

        status_output = gr.Textbox(label="Status", interactive=False)

        # Wire up events
        def on_mismatch_change(mismatch_id: str) -> dict[str, Any]:
            for r in MISMATCHED_RECORDS:
                if r["id"] == mismatch_id:
                    return r
            return {}

        mismatch_dropdown.change(
            fn=on_mismatch_change,
            inputs=[mismatch_dropdown],
            outputs=[record_display],
        )

        suggest_btn.click(
            fn=get_suggested_correction,
            inputs=[mismatch_dropdown],
            outputs=[suggestion_output],
        )

        explain_btn.click(
            fn=explain_miscategorisation,
            inputs=[mismatch_dropdown],
            outputs=[explanation_output],
        )

        approve_btn.click(
            fn=approve_correction,
            inputs=[mismatch_dropdown, corrected_topic],
            outputs=[status_output],
        )

        reject_btn.click(
            fn=lambda rid: f"Rejected correction for {rid} — flagged for second-pass review",
            inputs=[mismatch_dropdown],
            outputs=[status_output],
        )

    return demo


if __name__ == "__main__":
    demo = build_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860)
