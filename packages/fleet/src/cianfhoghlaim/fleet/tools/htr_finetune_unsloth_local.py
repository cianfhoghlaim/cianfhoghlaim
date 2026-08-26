"""htr_finetune_unsloth_local — HTR fine-tune tool via Unsloth + Modal H100.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Triggers `finetune_unsloth_local.py` for local M4 Max QLoRA or Modal H100 LoRA.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", "/Users/cianmacandeisigh/dev/cianfhoghlaim"))


async def htr_finetune_unsloth_local(
    base_model: str = "unsloth/gemma-4-E2B-it-GGUF",
    dataset_path: str = "oideachais.cultural_heritage.cbes",
    lora_r: int = 8,
    epochs: int = 3,
    backend: str = "m4_max",  # "m4_max" or "modal_h100"
    hub_model_id: str | None = None,
) -> dict[str, Any]:
    """Trigger HTR fine-tune via Unsloth + Modal H100 / M4 Max.

    Args:
        base_model: Unsloth GGUF model ID (e.g., 'unsloth/gemma-4-E2B-it-GGUF').
        dataset_path: DuckLake schema path or local dataset path.
        lora_r: LoRA rank (default 8 fits in M4 Max 48 GB).
        epochs: Number of training epochs.
        backend: "m4_max" (local) or "modal_h100" (cloud).
        hub_model_id: Optional HuggingFace Hub model ID to push the adapter.

    Returns:
        {"adapter_path": str, "metrics": dict, "hub_url": str}
    """
    cmd = [
        "python3",
        str(WORKSPACE_ROOT / "meaisinfhoghlaim/training/modal_finetune/finetune_unsloth_local.py"),
        "--base-model", base_model,
        "--dataset", dataset_path,
        "--lora-r", str(lora_r),
        "--epochs", str(epochs),
    ]
    if hub_model_id:
        cmd.extend(["--hub-model-id", hub_model_id])

    if backend == "modal_h100":
        # TODO: invoke the Modal H100 variant via `modal run`
        # For now, this delegates to the local script which has a Modal fallback
        pass

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE_ROOT))
    return {
        "adapter_path": f"{WORKSPACE_ROOT}/checkpoints/{base_model.split('/')[-1].replace('.gguf', '')}-gaeilge-htr",
        "metrics": {
            "loss": 0.5,  # placeholder
            "epochs": epochs,
            "lora_r": lora_r,
            "backend": backend,
        },
        "stdout": result.stdout[-1000:] if result.stdout else "",
        "stderr": result.stderr[-500:] if result.stderr else "",
        "hub_url": f"https://huggingface.co/{hub_model_id}" if hub_model_id else "",
    }


__all__ = ["htr_finetune_unsloth_local"]
