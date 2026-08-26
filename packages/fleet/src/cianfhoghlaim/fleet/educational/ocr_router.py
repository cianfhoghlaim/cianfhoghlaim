"""OCR-Router — picks the best OCR backend per PDF.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Uses all 4 OCR tools to pick the best per PDF:
- Handwritten → ocr_docling + ocr_qwen3_vl_8b (Unsloth Studio)
- Typed → ocr_qwen3_vl_8b (primary, Unsloth Studio)
- Schema-driven → ocr_unstract
- Fallback → ocr_gemma4_26b (llama-swap)
"""

from __future__ import annotations

from typing import Any

from google.adk.agents import LlmAgent

from ..config import TuathaConfig
from ..tools.ocr_docling import ocr_docling
from ..tools.ocr_gemma4_26b import ocr_gemma4_26b
from ..tools.ocr_qwen3_vl_8b import ocr_qwen3_vl_8b
from ..tools.ocr_unstract import ocr_unstract


config = TuathaConfig.from_env()

ocr_router_agent = LlmAgent(
    name="ocr_router_agent",
    model=config.litellm.resolve_model("ocr_vision", "primary"),
    description=(
        "OCR-Router picks the best OCR backend per PDF. Uses Unsloth Studio "
        "Qwen3-VL-8B-Instruct as the primary backend (via litellm), falls back to "
        "Gemma 4 26B-A4B (llama-swap), Docling, or Unstract based on the PDF type."
    ),
    instruction=(
        "You are the OCR-Router agent. When the user provides a PDF path, "
        "decide which OCR backend to use:\n"
        "1. If the PDF is handwritten (e.g., Dúchas.ie manuscripts), use ocr_docling + ocr_qwen3_vl_8b\n"
        "2. If the PDF is typed (e.g., NCCA syllabus, AQA papers), use ocr_qwen3_vl_8b\n"
        "3. If the PDF needs schema-driven extraction, use ocr_unstract\n"
        "4. If Unsloth Studio is unavailable, fall back to ocr_gemma4_26b\n"
        "Return the OCR result + per-backend CER for the comparison."
    ),
    tools=[ocr_docling, ocr_gemma4_26b, ocr_qwen3_vl_8b, ocr_unstract],
)


async def run_ocr_router(pdf_path: str) -> dict[str, Any]:
    """Pick the best OCR backend for the given PDF and return the result.

    Returns:
        {"backend": str, "text": str, "regions": list[dict]}
    """
    # Primary: Unsloth Studio (Qwen3-VL-8B)
    try:
        result = await ocr_qwen3_vl_8b(pdf_path)
        return {"backend": "ocr_qwen3_vl_8b (unsloth_studio)", **result}
    except Exception:
        # Fallback: llama-swap (Gemma 4 26B-A4B)
        result = await ocr_gemma4_26b(pdf_path)
        return {"backend": "ocr_gemma4_26b (llama_swap)", **result}


__all__ = ["ocr_router_agent", "run_ocr_router"]
