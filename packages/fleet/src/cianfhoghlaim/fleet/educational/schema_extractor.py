"""Schema-Extractor — BAML structured field extraction from OCR text.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Uses Unsloth Studio Qwen3-VL-8B + BAML function calls to extract structured
fields (jurisdiction, exam_paper, year, LO code, etc.) from OCR'd paper text.
"""

from __future__ import annotations

from typing import Any

from google.adk.agents import LlmAgent

from ..config import TuathaConfig
from ..tools.ocr_qwen3_vl_8b import ocr_qwen3_vl_8b


config = TuathaConfig.from_env()


schema_extractor_agent = LlmAgent(
    name="schema_extractor_agent",
    model=config.litellm.resolve_model("ocr_vision", "primary"),
    description=(
        "Schema-Extractor uses Unsloth Studio Qwen3-VL-8B + BAML to extract "
        "structured fields from OCR'd paper text: jurisdiction, exam_paper, year, "
        "LO code (NCCA syllabus), grade band, marking scheme."
    ),
    instruction=(
        "You are the Schema-Extractor agent. When the user provides OCR text, extract:\n"
        "1. jurisdiction (ireland, england, scotland, wales, ni, jersey, guernsey, iom)\n"
        "2. exam_paper (LC, JC, A-Level, GCSE, WJEC, CCEA, SQA)\n"
        "3. year (integer)\n"
        "4. lo_code (NCCA syllabus LO code, e.g., LO-1.1.1)\n"
        "5. grade_band (H1-H8 / A*-G / 1-9)\n"
        "6. marking_scheme_url (if applicable)\n"
        "Use the BAML GenerateGaeilgeSyllabus / GenerateEnglSyllabus / "
        "GenerateMarkingScheme / etc. functions per the canonical qpack_*.baml "
        "templates. Return as a structured Pydantic type."
    ),
    tools=[ocr_qwen3_vl_8b],  # uses OCR as fallback if no text provided
)


async def run_schema_extract(
    pdf_path: str | None = None,
    text: str | None = None,
    schema_class: str = "GaeilgeSyllabus",
) -> dict[str, Any]:
    """Run BAML schema extraction on OCR text or PDF."""
    if text is None:
        if pdf_path is None:
            raise ValueError("Either pdf_path or text must be provided")
        ocr_result = await ocr_qwen3_vl_8b(pdf_path)
        text = ocr_result["text"]

    # TODO: invoke the canonical BAML GenerateXxx function per schema_class
    # For now, return a structured placeholder
    return {
        "schema_class": schema_class,
        "text_length": len(text),
        "extracted": {
            "jurisdiction": "ireland",
            "exam_paper": "LC",
            "year": 2024,
            "lo_code": "LO-1.1.1",
        },
    }


__all__ = ["schema_extractor_agent", "run_schema_extract"]
