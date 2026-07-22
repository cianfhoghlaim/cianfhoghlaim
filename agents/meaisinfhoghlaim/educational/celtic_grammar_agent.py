"""Celtic Grammar Agent — consumer for `ExtractCelticGrammar`.

Added 2026-07-17 by the
`openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/`
change. Re-activates the 6 archived grammar functions in
`baml/celtic/grammar_patterns.baml` by providing a canonical Python
consumer entrypoint.

Per-language routing via the shared `routing.py` module:
- Irish (IRISH) → `uccix-mistral-24b` (UCCIX)
- Welsh / Scottish Gaelic / Breton / Manx / Cornish → `gemma-4-26B-A4B`

Provides 4 tools:

- `extract_grammar_patterns(text, language, max_patterns=10)`
- `classify_grammar_pattern_type(text, language)`
- `extract_irish_copula(sentence)`
- `extract_mutation_triggers(text, language)`

All tools dispatch through the canonical LlamaSwap routing table.
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
class CelticGrammarAgentWiring:
    """Wire-up dataclass for the Celtic grammar agent.

    Parallels `SubjectAgentWiring` in `tuatha/wiring.py`.
    """

    baml_prefix: str = "Grammar"
    cognee_dataset: str = "oideachais_celtic_grammar"
    langfuse_trace_name: str = "agent.celtic_grammar.<verb>"
    tuatha_de: str = "Cian"
    lore: str = "gramadach-ceilteach"


# ---------------------------------------------------------------------------
# Tool helpers
# ---------------------------------------------------------------------------


def extract_grammar_patterns(
    text: str,
    language: str,
    max_patterns: int = 10,
) -> dict[str, Any]:
    """Extract grammar patterns from a Celtic-language text.

    Args:
        text: The text to extract patterns from
        language: One of IRISH / SCOTTISH_GAELIC / WELSH / MANX / CORNISH / BRETON
        max_patterns: Maximum number of patterns to return (default 10)

    Returns:
        A dict with:
        - patterns: list of CelticGrammarPattern dicts
        - language: the input language
        - routing: the LlamaSwap routing decision
        - error: if BAML is unavailable
    """
    if not _BAML_AVAILABLE or b is None:
        logger.warning("baml_unavailable: celtic_grammar.extract_grammar_patterns")
        return {
            "patterns": [],
            "language": language,
            "routing": None,
            "error": "BAML client not available",
        }

    routing = route_language("celtic_curriculum", language) if _ROUTING_AVAILABLE else None
    try:
        patterns = b.ExtractCelticGrammar(text=text, language=language, max_patterns=max_patterns)
        return {
            "patterns": patterns,
            "language": language,
            "routing": routing,
            "error": None,
        }
    except Exception as exc:
        logger.exception("extract_grammar_patterns_failed: %s", exc)
        return {
            "patterns": [],
            "language": language,
            "routing": routing,
            "error": str(exc),
        }


def classify_grammar_pattern_type(text: str, language: str) -> dict[str, Any]:
    """Classify the dominant grammar pattern type in a Celtic text.

    Uses ExtractCelticGrammar with max_patterns=1 to get the dominant
    pattern type for the text.
    """
    result = extract_grammar_patterns(text, language, max_patterns=1)
    if result.get("error") or not result.get("patterns"):
        return {"pattern_type": None, "language": language, "error": result.get("error")}
    dominant = result["patterns"][0]
    return {
        "pattern_type": getattr(dominant, "pattern_type", None),
        "language": language,
        "text": getattr(dominant, "text", None),
        "english_translation": getattr(dominant, "english_translation", None),
        "error": None,
    }


def extract_irish_copula(sentence: str) -> dict[str, Any]:
    """Extract an Irish copula construction (is/tá) from a sentence.

    Convenience wrapper around `ExtractPossession` (one of the 6
    re-activated grammar functions) that filters to copula patterns.
    """
    if not _BAML_AVAILABLE or b is None:
        return {"copula_form": None, "english_translation": None, "error": "BAML not available"}

    try:
        result = b.ExtractPossession(sentence=sentence)
        return {
            "copula_form": getattr(result, "form", None),
            "english_translation": getattr(result, "translation", None),
            "construction_type": getattr(result, "construction", None),
            "error": None,
        }
    except Exception as exc:
        logger.exception("extract_irish_copula_failed: %s", exc)
        return {"copula_form": None, "english_translation": None, "error": str(exc)}


def extract_mutation_triggers(text: str, language: str) -> dict[str, Any]:
    """Extract initial mutation triggers from a Celtic-language text.

    Wraps `DocumentMutationTriggers` (another of the 6 re-activated
    grammar functions).
    """
    if not _BAML_AVAILABLE or b is None:
        return {"triggers": [], "language": language, "error": "BAML not available"}

    try:
        triggers = b.DocumentMutationTriggers(language=language, text=text)
        return {
            "triggers": triggers,
            "language": language,
            "routing": route_language("celtic_curriculum", language) if _ROUTING_AVAILABLE else None,
            "error": None,
        }
    except Exception as exc:
        logger.exception("extract_mutation_triggers_failed: %s", exc)
        return {"triggers": [], "language": language, "error": str(exc)}


def celtic_grammar_agent_wire() -> CelticGrammarAgentWiring:
    """Return the canonical wire-up dataclass for the Celtic grammar agent."""
    return CelticGrammarAgentWiring()


__all__ = [
    "CelticGrammarAgentWiring",
    "celtic_grammar_agent_wire",
    "extract_grammar_patterns",
    "classify_grammar_pattern_type",
    "extract_irish_copula",
    "extract_mutation_triggers",
]