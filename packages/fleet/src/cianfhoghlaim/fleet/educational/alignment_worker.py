"""Alignment-Worker — bilingual EU IR-EN + NCCA alignment pipeline.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Aligns parallel Irish-English text from EUR-Lex + NCCA syllabus for
fine-tuning Gemma 4 4B EN-GA alignment adapter.
"""

from __future__ import annotations

from typing import Any

from google.adk.agents import LlmAgent

from ..config import TuathaConfig


config = TuathaConfig.from_env()


alignment_worker_agent = LlmAgent(
    name="alignment_worker_agent",
    model=config.litellm.resolve_model("text_llm", "coding"),
    description=(
        "Alignment-Worker aligns parallel Irish-English text from EUR-Lex "
        "+ NCCA Leaving Certificate syllabus using fast_align + eflomal. "
        "Produces a word-level alignment dataset for fine-tuning the Gemma 4 4B "
        "EN-GA alignment adapter."
    ),
    instruction=(
        "You are the Alignment-Worker agent. When the user provides parallel "
        "source_text + target_text, invoke bilingual_align(lang_pair='ga-en'). "
        "The alignment is written to the ciancheiltis.language.bilingual_alignment "
        "DuckLake schema. Return the alignment score + the word-level alignments."
    ),
    tools=[],
)


async def run_alignment(
    source_text: str,
    target_text: str,
    lang_pair: str = "ga-en",
) -> dict[str, Any]:
    """Run bilingual alignment."""
    from ..tools.bilingual_align import bilingual_align
    return await bilingual_align(source_text, target_text, lang_pair)


__all__ = ["alignment_worker_agent", "run_alignment"]
