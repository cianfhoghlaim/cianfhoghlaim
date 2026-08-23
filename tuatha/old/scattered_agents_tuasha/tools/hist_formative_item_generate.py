"""hist_formative_item_generate — Generate a History formative item."""
from __future__ import annotations

import uuid
from typing import Any


async def generate_hist_item(
    lo_code: str,
    difficulty: int,
    evidence: dict[str, Any],
    level: str = "lc_hl",
    topic: str = "",
) -> dict[str, Any]:
    """`evidence` (`HistEvidenceLink`-shaped: source_pdf, source_page,
    excerpt_en, excerpt_ga, ncca_url) is required — see
    `docs-informed-quest-and-credential-generation-v1`.
    """
    try:
        from cianfhoghlaim.baml_client import b

        item = b.GenerateHistFormativeItem(
            lo_code=lo_code,
            difficulty=difficulty,
            level=level,
            topic=topic,
            evidence=evidence,
        )
        return {
            "id": item.id or str(uuid.uuid4()),
            "lo_code": item.lo_code,
            "level": item.level,
            "topic": item.topic,
            "item_type": item.item_type,
            "difficulty": item.difficulty,
            "prompt_en": item.prompt.text_en,
            "prompt_ga": item.prompt.text_ga,
            "expected_answer_en": item.expected_answer.text_en,
            "expected_answer_ga": item.expected_answer.text_ga,
            "marking_scheme_en": item.marking_scheme.text_en,
            "marking_scheme_ga": item.marking_scheme.text_ga,
            "common_errors": [
                {"en": e.text_en, "ga": e.text_ga} for e in item.common_errors
            ],
            "hints": [
                {"en": h.text_en, "ga": h.text_ga} for h in item.hints
            ],
            "evidence": item.evidence.model_dump() if item.evidence else {},
            "feedback_channel": item.feedback_channel,
            "est_time_minutes": item.est_time_minutes,
        }
    except Exception as exc:
        return {"lo_code": lo_code, "error": f"Item generation failed: {exc}"}