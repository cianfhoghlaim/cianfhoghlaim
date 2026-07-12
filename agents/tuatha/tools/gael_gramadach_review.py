"""gael_gramadach_review — Look up the NCCA Gaeilge grammar review.

Backed by BAML `qpack_gaeilge.baml` + a small Gramadach table for
common Irish-language grammar rules (réimíreanna, aimsirí, etc.).
"""
from __future__ import annotations

from typing import Any

# Small canonical Irish grammar reference (curated subset).
GRAMADACH_REFERENCE: dict[str, dict[str, str]] = {
    "AIMSIR_CHAITE": {
        "title_ga": "An Aimsir Chaite",
        "title_en": "Past Tense",
        "explanation_ga": "An aimsir chaite, críochnaíonn gach briathar le -igh, -aigh, -íl, nó -iomar.",
        "explanation_en": "In the past tense, most verbs end in -igh, -aigh, -íl, or -iomar.",
        "example_ga": "Chuaigh mé abhaile. (I went home.)",
        "example_en": "Chuaigh mé abhaile. — I went home.",
    },
    "AIMSIR_LAITEOIREACHTA": {
        "title_ga": "An Aimsir Láithreach",
        "title_en": "Present Tense",
        "explanation_ga": "An aimsir láithreach, críochnaíonn gach briathar le -ann (sé/sí) nó -imid (sinn).",
        "explanation_en": "In the present tense, verbs end in -ann (he/she) or -imid (we).",
        "example_ga": "Tá mé ag léamh. (I am reading.)",
        "example_en": "Tá mé ag léamh. — I am reading.",
    },
    "REIMIR": {
        "title_ga": "An Réimír",
        "title_en": "The Preposition + Article",
        "explanation_ga": "Na réimíreanna simplí: ar, ag, as, ag, chuig, de, do, faoi, i, le, ó, roimh, thar, trí, um.",
        "explanation_en": "Simple prepositions: ar (on), ag (at), as (out of), chuig (to), de (of), do (to/for), faoi (under), i (in), le (with), ó (from), roimh (before), thar (across), trí (through), um (about).",
    },
    "SEIMHIU": {
        "title_ga": "An Séimhiú",
        "title_en": "Lenition",
        "explanation_ga": "Cuirtear séimhiú (h) ar chonsan b, c, d, g, m, p, s, t nuair a leanann sé gutaí áirithe.",
        "explanation_en": "Lenition (h) is added to consonants b, c, d, g, m, p, s, t when followed by certain vowels.",
    },
    "URU": {
        "title_ga": "An Urú",
        "title_en": "Eclipsis",
        "explanation_ga": "Cuirtear urú ar chonsan nuair a leanann sé gutaí áirithe: b→mb, c→gc, d→nd, g→ng, p→bp, t→dt.",
        "explanation_en": "Eclipsis is the addition of a prefix to consonants in certain grammatical contexts.",
    },
}


async def lookup_gael_gramadach(topic: str) -> dict[str, Any]:
    """Return the grammar review for the given Irish grammar topic.

    Args:
        topic: Grammar topic key, e.g. "AIMSIR_CHAITE", "REIMIR", "SEIMHIU", "URU",
               or a free-text query like "past tense" / "prepositions".

    Returns:
        A dict with `topic`, `title_ga`, `title_en`, `explanation_ga`,
        `explanation_en`, `example_ga`, `example_en`.
    """
    # Normalize the topic query
    topic_upper = topic.upper().replace(" ", "_")
    for key in GRAMADACH_REFERENCE:
        if key in topic_upper or topic.upper() in key:
            ref = GRAMADACH_REFERENCE[key]
            return {
                "topic": key,
                "title_ga": ref["title_ga"],
                "title_en": ref["title_en"],
                "explanation_ga": ref["explanation_ga"],
                "explanation_en": ref["explanation_en"],
                "example_ga": ref.get("example_ga", ""),
                "example_en": ref.get("example_en", ""),
            }

    # Fallback: BAML search
    try:
        from cianfhoghlaim.baml_client import b

        explanation = b.ExplainGaelGramadach(topic)
        return {
            "topic": topic,
            "explanation_ga": explanation,
            "explanation_en": None,
        }
    except Exception:
        return {
            "topic": topic,
            "error": "gramadach topic not found",
            "available_topics": list(GRAMADACH_REFERENCE.keys()),
        }