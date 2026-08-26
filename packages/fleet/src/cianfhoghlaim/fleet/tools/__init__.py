"""fleet.tools — the 8-tool canonical registry for meaisinfhoghlaim.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
The 8 tools are dispatched via Hermes (API + channels) + OpenClaw (consumer gateway)
+ OpenChamber (operator surface). Each invocation is traced in Langfuse + scored in MLflow.
"""

from __future__ import annotations

from typing import Any

# Tool registry — the canonical 8 tools
TOOL_REGISTRY: dict[str, dict[str, Any]] = {
    # OCR backends (via Unsloth Studio + litellm)
    "ocr_qwen3_vl_8b": {
        "module": "fleet.tools.ocr_qwen3_vl_8b",
        "function": "ocr_qwen3_vl_8b",
        "backend": "litellm → unsloth_studio",
        "model": "local/unsloth/qwen3-vl-8b-instruct",
        "description": "OCR via Qwen3-VL-8B-Instruct on Unsloth Studio (host.docker.internal:8888)",
        "inputs": {"file_path": str, "languages": list[str] | None},
        "outputs": {"text": str, "regions": list[dict]},
    },
    "ocr_gemma4_26b": {
        "module": "fleet.tools.ocr_gemma4_26b",
        "function": "ocr_gemma4_26b",
        "backend": "litellm → llama-swap",
        "model": "local/vision/gemma-4-26B-A4B",
        "description": "OCR via Gemma 4 26B-A4B on llama-swap (fallback when Unsloth Studio unavailable)",
        "inputs": {"file_path": str, "languages": list[str] | None},
        "outputs": {"text": str, "regions": list[dict]},
    },
    "ocr_unstract": {
        "module": "fleet.tools.ocr_unstract",
        "function": "ocr_unstract",
        "backend": "http://unstract:8002",
        "description": "Schema-driven extraction via Unstract",
        "inputs": {"file_path": str, "schema": dict | None},
        "outputs": {"extracted": dict, "confidence": float},
    },
    "ocr_docling": {
        "module": "fleet.tools.ocr_docling",
        "function": "ocr_docling",
        "backend": "http://docling-serve:5001",
        "description": "Docling DocTags XML output for layout-aware extraction",
        "inputs": {"file_path": str},
        "outputs": {"text": str, "doctags_xml": str},
    },
    # HTR fine-tuning
    "htr_finetune_unsloth_local": {
        "module": "fleet.tools.htr_finetune_unsloth_local",
        "function": "htr_finetune_unsloth_local",
        "backend": "unsloth + modal_h100",
        "description": "HTR fine-tune via Unsloth + Modal H100 (QLoRA r=8 default)",
        "inputs": {
            "base_model": str,
            "dataset_path": str,
            "lora_r": int,
            "epochs": int,
            "backend": str,
        },
        "outputs": {"adapter_path": str, "metrics": dict, "hub_url": str},
    },
    # Bilingual alignment
    "bilingual_align": {
        "module": "fleet.tools.bilingual_align",
        "function": "bilingual_align",
        "backend": "fast_align + eflomal",
        "description": "EU IR-EN + NCCA bilingual alignment for Gemma 4 4B fine-tune",
        "inputs": {"source_text": str, "target_text": str, "lang_pair": str},
        "outputs": {"alignment": list[dict], "score": float},
    },
    # Agentic interactions
    "web_form_fill": {
        "module": "fleet.tools.web_form_fill",
        "function": "web_form_fill",
        "backend": "playwright-mcp",
        "description": "Auto-fill web forms via Playwright browser automation",
        "inputs": {"url": str, "fields": dict},
        "outputs": {"screenshot": str, "submitted": bool},
    },
    "bash_execute": {
        "module": "fleet.tools.bash_execute",
        "function": "bash_execute",
        "backend": "local_sandbox",
        "description": "Execute shell commands in /tmp/agent-sandbox/",
        "inputs": {"command": str, "cwd": str | None, "timeout": int},
        "outputs": {"stdout": str, "stderr": str, "exit_code": int},
    },
    "eval_orchestrator": {
        "module": "fleet.tools.eval_orchestrator",
        "function": "eval_orchestrator",
        "backend": "ragas",
        "description": "RAGAS eval orchestrator (faithfulness + CER + WER + chrF)",
        "inputs": {"model_key": str, "pdf_path": str, "ground_truth": str | None},
        "outputs": {"faithfulness": float, "cer": float, "wer": float, "chrf": float},
    },
}


def get_tool(name: str) -> dict[str, Any]:
    """Get the canonical tool spec by name."""
    if name not in TOOL_REGISTRY:
        raise KeyError(f"Unknown tool: {name}. Available: {list(TOOL_REGISTRY.keys())}")
    return TOOL_REGISTRY[name]


def list_tools() -> list[str]:
    """List all canonical tool names."""
    return list(TOOL_REGISTRY.keys())


__all__ = ["TOOL_REGISTRY", "get_tool", "list_tools"]
