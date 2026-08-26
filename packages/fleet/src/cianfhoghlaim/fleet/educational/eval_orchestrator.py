"""Eval-Orchestrator — RAGAS eval across the 24 OCR/VLM models.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Runs RAGAS faithfulness + CER + WER + chrF for a model against a PDF + ground truth.
Compares against baseline (no fine-tune) to show improvement.
"""

from __future__ import annotations

from typing import Any

from google.adk.agents import LlmAgent

from ..config import TuathaConfig


config = TuathaConfig.from_env()


eval_orchestrator_agent = LlmAgent(
    name="eval_orchestrator_agent",
    model=config.litellm.resolve_model("text_llm", "eval"),
    description=(
        "Eval-Orchestrator runs RAGAS (faithfulness + relevancy + recall + precision) + "
        "CER + WER + chrF for a model against a PDF + ground truth. Compares against "
        "baseline (no fine-tune) to show improvement. Logs to MLflow + Langfuse."
    ),
    instruction=(
        "You are the Eval-Orchestrator agent. When the user provides a PDF + ground "
        "truth text, invoke eval_orchestrator(model_key, pdf_path, ground_truth). "
        "Return the per-metric scores + comparison vs baseline. Logs to MLflow + "
        "Langfuse for cross-agent observability."
    ),
    tools=[],
)


async def run_eval(
    model_key: str,
    pdf_path: str,
    ground_truth: str | None = None,
) -> dict[str, Any]:
    """Run RAGAS eval on a model against a PDF + ground truth."""
    from ..tools.eval_orchestrator import eval_orchestrator
    return await eval_orchestrator(model_key, pdf_path, ground_truth)


__all__ = ["eval_orchestrator_agent", "run_eval"]
