"""uoa_vision — the Gemini 2.5 Pro vision tool for the UoA portal pipeline.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

Phase 2 stub — sends the screenshot to Gemini 2.5 Pro via LiteLLM
for interpretation. Returns structured fields + the "which subset?"
question to ask the user.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


async def uoa_vision_interpret(
    screenshot_b64: str | None,
    page_url: str,
    service: str,
) -> dict[str, Any]:
    """Interpret a UoG portal screenshot via Gemini 2.5 Pro vision.

    Args:
        screenshot_b64: base64-encoded PNG screenshot
        page_url: the URL the screenshot was taken at
        service: 'regexam' or 'canvas'

    Returns:
        dict with keys: module_code, paper_year, file_type, title,
        selection_question
    """
    if screenshot_b64 is None:
        return {
            "module_code": None,
            "paper_year": None,
            "file_type": None,
            "title": None,
            "selection_question": "Which modules do you want to download? (or 'all')",
        }

    return {
        "module_code": None,
        "paper_year": None,
        "file_type": None,
        "title": None,
        "selection_question": "Phase 2: Gemini 2.5 Pro will interpret the screenshot.",
    }


def uoa_vision_interpret_tool() -> Any:
    return uoa_vision_interpret


__all__ = ["uoa_vision_interpret", "uoa_vision_interpret_tool"]
