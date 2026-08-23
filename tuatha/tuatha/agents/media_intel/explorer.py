"""tuatha.agents.media_intel.explorer — the per-medium + cross-medium explorer (NEW).

Marimo-backed notebook surface for the per-medium coverage
table + the cross-medium consistency score.

Per the BUILD_PLAN.md this is one of the 2 new media_intel
files added by the consolidation change.
"""
from __future__ import annotations

from typing import Any


async def per_medium_coverage(media_descriptors: list[dict[str, Any]]) -> dict[str, int]:
    """Count the descriptors per medium class.

    Returns a {medium: count} dict (e.g., {'comic': 100, 'prose': 50,
    'animation': 25, 'gameplay': 200, 'official': 30}).
    """
    counts: dict[str, int] = {}
    for d in media_descriptors:
        medium = d.get("medium", "unknown")
        counts[medium] = counts.get(medium, 0) + 1
    return counts


async def cross_medium_consistency(
    media_descriptors: list[dict[str, Any]],
    element: str,
) -> dict[str, float]:
    """Compute the per-medium cosine similarity over the 7-axis
    descriptor space for a given element. Returns a {medium:
    avg_similarity} dict.

    The element with the lowest variance in similarity across
    the 5 media classes is the most *consistently* described.
    """
    # Stub implementation (the real one uses LanceDB vector search
    # over the media_descriptors_lance table).
    return {
        "comic": 0.0,
        "prose": 0.0,
        "animation": 0.0,
        "gameplay": 0.0,
        "official": 0.0,
    }


async def summarise_corpus(media_descriptors: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a bilingual EN/GA summary of the corpus state."""
    counts = await per_medium_coverage(media_descriptors)
    total = sum(counts.values())
    return {
        "corpus": "media_intel",
        "total_descriptors": total,
        "per_medium": counts,
        "summary_en": f"The 5-class media-intel corpus has {total} descriptors.",
        "summary_ga": f"Tá {total} tuairiscí sa chorpas 5-aicme.",
    }


__all__ = [
    "cross_medium_consistency",
    "per_medium_coverage",
    "summarise_corpus",
]
