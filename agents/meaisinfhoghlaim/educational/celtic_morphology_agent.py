"""Celtic Morphology Agent — consumer for `ExtractCelticMorphology`.

Added 2026-07-17 by the
`openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/`
change. Re-activates the 4 archived morphology functions in
`baml/celtic/morphology.baml` by providing a canonical Python
consumer entrypoint.

Per-language routing via the shared `routing.py` module:
- Irish (IRISH) → `uccix-mistral-24b` (UCCIX)
- Welsh / Scottish Gaelic / Breton / Manx / Cornish → `gemma-4-26B-A4B`

Provides 4 tools:

- `extract_morphology(text, language, word_class_hint=None)`
- `extract_verb_conjugation(verb, language)`
- `extract_noun_declension(noun, language, gender=None)`
- `compare_adjective(adjective, language)`
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# BAML client (graceful degradation)
try:
    from baml_client import b  # type: ignore[import-not-found]

    _BAML_AVAILABLE = True
except Exception:
    _BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]


# Routing table (shared module)
try:
    from cianfhoghlaim.meaisinfhoghlaim.models.routing import (  # type: ignore[import-not-found]
        route_language,
    )

    _ROUTING_AVAILABLE = True
except Exception:
    _ROUTING_AVAILABLE = False
    route_language = None  # type: ignore[assignment]


@dataclass
class CelticMorphologyAgentWiring:
    """Wire-up dataclass for the Celtic morphology agent.

    Parallels `SubjectAgentWiring` in `tuatha/wiring.py`.
    """

    baml_prefix: str = "Morphology"
    cognee_dataset: str = "oideachais_celtic_morphology"
    langfuse_trace_name: str = "agent.celtic_morphology.<verb>"
    tuatha_de: str = "Cian"
    lore: str = "cruth-ceilteach"


# ---------------------------------------------------------------------------
# Tool helpers
# ---------------------------------------------------------------------------


def extract_morphology(
    text: str,
    language: str,
    word_class_hint: str | None = None,
) -> dict[str, Any]:
    """Extract morphology from a Celtic-language text.

    Args:
        text: The text to extract morphology from
        language: One of IRISH / SCOTTISH_GAELIC / WELSH / MANX / CORNISH / BRETON
        word_class_hint: Optional focus — "verb", "noun", "adjective", etc.

    Returns:
        A dict with:
        - specs: list of CelticMorphologySpec dicts
        - language: the input language
        - routing: the LlamaSwap routing decision
        - error: if BAML is unavailable
    """
    if not _BAML_AVAILABLE or b is None:
        logger.warning("baml_unavailable: celtic_morphology.extract_morphology")
        return {
            "specs": [],
            "language": language,
            "routing": None,
            "error": "BAML client not available",
        }

    routing = route_language("celtic_curriculum", language) if _ROUTING_AVAILABLE else None
    try:
        specs = b.ExtractCelticMorphology(text=text, language=language, word_class_hint=word_class_hint)
        return {
            "specs": specs,
            "language": language,
            "routing": routing,
            "error": None,
        }
    except Exception as exc:
        logger.exception("extract_morphology_failed: %s", exc)
        return {
            "specs": [],
            "language": language,
            "routing": routing,
            "error": str(exc),
        }


def extract_verb_conjugation(verb: str, language: str) -> dict[str, Any]:
    """Extract the full verb conjugation paradigm for a Celtic verb.

    Wraps `ExtractVerbConjugation` (one of the 4 re-activated
    morphology functions).
    """
    if not _BAML_AVAILABLE or b is None:
        return {"verb": verb, "paradigm": [], "language": language, "error": "BAML not available"}

    try:
        result = b.ExtractVerbConjugation(verb=verb, language=language)
        return {
            "verb": verb,
            "paradigm": result,
            "language": language,
            "routing": route_language("celtic_curriculum", language) if _ROUTING_AVAILABLE else None,
            "error": None,
        }
    except Exception as exc:
        logger.exception("extract_verb_conjugation_failed: %s", exc)
        return {"verb": verb, "paradigm": [], "language": language, "error": str(exc)}


def extract_noun_declension(noun: str, language: str, gender: str | None = None) -> dict[str, Any]:
    """Extract the full noun declension paradigm for a Celtic noun.

    Wraps `ExtractNounDeclension` (another of the 4 re-activated
    morphology functions).
    """
    if not _BAML_AVAILABLE or b is None:
        return {"noun": noun, "paradigm": [], "language": language, "error": "BAML not available"}

    try:
        result = b.ExtractNounDeclension(noun=noun, language=language, gender=gender)
        return {
            "noun": noun,
            "paradigm": result,
            "language": language,
            "routing": route_language("celtic_curriculum", language) if _ROUTING_AVAILABLE else None,
            "error": None,
        }
    except Exception as exc:
        logger.exception("extract_noun_declension_failed: %s", exc)
        return {"noun": noun, "paradigm": [], "language": language, "error": str(exc)}


def compare_adjective(adjective: str, language: str) -> dict[str, Any]:
    """Provide the comparative + superlative forms for a Celtic adjective.

    Wraps `CompareAdjective` (the 4th of the 4 re-activated morphology
    functions).
    """
    if not _BAML_AVAILABLE or b is None:
        return {
            "adjective": adjective,
            "comparative": None,
            "superlative": None,
            "language": language,
            "error": "BAML not available",
        }

    try:
        result = b.CompareAdjective(adjective=adjective, language=language)
        return {
            "adjective": adjective,
            "comparative": getattr(result, "comparative", None),
            "superlative": getattr(result, "superlative", None),
            "language": language,
            "routing": route_language("celtic_curriculum", language) if _ROUTING_AVAILABLE else None,
            "error": None,
        }
    except Exception as exc:
        logger.exception("compare_adjective_failed: %s", exc)
        return {
            "adjective": adjective,
            "comparative": None,
            "superlative": None,
            "language": language,
            "error": str(exc),
        }


def celtic_morphology_agent_wire() -> CelticMorphologyAgentWiring:
    """Return the canonical wire-up dataclass for the Celtic morphology agent."""
    return CelticMorphologyAgentWiring()


__all__ = [
    "CelticMorphologyAgentWiring",
    "celtic_morphology_agent_wire",
    "extract_morphology",
    "extract_verb_conjugation",
    "extract_noun_declension",
    "compare_adjective",
]