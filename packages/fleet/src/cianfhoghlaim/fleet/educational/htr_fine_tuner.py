"""HTR-FineTuner — fine-tunes Gemma 4 4B / Qwen3-VL-8B on Dúchas transcriptions.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Triggers QLoRA / LoRA fine-tuning via Unsloth + Modal H100. Outputs
the adapter to HuggingFace Hub for downstream Unsloth Studio loading.
"""

from __future__ import annotations

import os
from typing import Any

from google.adk.agents import LlmAgent

from ..config import TuathaConfig


config = TuathaConfig.from_env()


htr_fine_tuner_agent = LlmAgent(
    name="htr_fine_tuner_agent",
    model=config.litellm.resolve_model("text_llm", "coding"),
    description=(
        "HTR-FineTuner triggers local (M4 Max) or cloud (Modal H100) fine-tuning "
        "of Gemma 4 4B / Qwen3-VL-8B on the Dúchas transcriptions dataset. "
        "Outputs adapters to HuggingFace Hub for Unsloth Studio loading."
    ),
    instruction=(
        "You are the HTR-FineTuner agent. When the user wants to fine-tune a model on "
        "Dúchas.ie manuscript transcriptions, invoke htr_finetune_unsloth_local.py with:\n"
        "1. base_model='unsloth/gemma-4-E2B-it-GGUF' (default) OR 'unsloth/Qwen3-VL-8B-Instruct-GGUF'\n"
        "2. dataset_path='oideachais.cultural_heritage.cbes'\n"
        "3. lora_r=8 (default fits in M4 Max 48 GB)\n"
        "4. epochs=3 (default)\n"
        "5. backend='m4_max' (default) OR 'modal_h100'\n"
        "Return the adapter_path + metrics + hub_url."
    ),
    tools=[],  # HTR-FineTuner dispatches the subprocess, not a tool_use
)


async def run_htr_finetune(
    base_model: str = "unsloth/gemma-4-E2B-it-GGUF",
    dataset_path: str = "oideachais.cultural_heritage.cbes",
    lora_r: int = 8,
    epochs: int = 3,
    backend: str = "m4_max",
    hub_model_id: str | None = None,
) -> dict[str, Any]:
    """Run HTR fine-tune via Unsloth + Modal H100 / M4 Max."""
    from ..tools.htr_finetune_unsloth_local import htr_finetune_unsloth_local
    return await htr_finetune_unsloth_local(
        base_model=base_model,
        dataset_path=dataset_path,
        lora_r=lora_r,
        epochs=epochs,
        backend=backend,
        hub_model_id=hub_model_id,
    )


__all__ = ["htr_fine_tuner_agent", "run_htr_finetune"]
