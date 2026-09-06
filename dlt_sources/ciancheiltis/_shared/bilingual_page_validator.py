"""PR0.2 — bilingual page validator (Requirement §cross-pipeline integration).

Heuristic check that two URLs are the same article in two different
languages — for the `en-cy`, `en-ga`, `en-gd`, `en-gv` and `en-ga (EU)`
pairs. Used to deduplicate bilingual pairs in the lakehouse and to
gate the `metadata_language_mismatch` rate at < 5%.
"""
from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse


_LANG_PREFIX_RE = re.compile(r"^/(en|ga|cy|gd|gv|ga-ie)/", re.IGNORECASE)


def normalize_for_compare(url: str) -> str:
    """Strip the language prefix (en/ga/cy/gd/gv/ga-ie) from a URL.

    Used to canonicalise `ncca.ie/en/resources/...` vs
    `ncca.ie/ga/resources/...` to the same key.
    """
    parsed = urlparse(url)
    path = parsed.path
    stripped = _LANG_PREFIX_RE.sub("/", path, count=1)
    return f"{parsed.scheme}://{parsed.netloc}{stripped}{parsed.query}"


def structural_similarity(body_a: str, body_b: str) -> float:
    """Return a Jaccard-similarity score between two bodies.

    Used as the heuristic gate for `is_same_article`. The threshold
    is set conservatively at 0.5 (configurable) because bilingual
    pages commonly have very different word orderings.
    """
    if not body_a or not body_b:
        return 0.0
    set_a = set(body_a.lower().split())
    set_b = set(body_b.lower().split())
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return round(len(intersection) / len(union), 4)


def is_same_article(
    body_a: str,
    body_b: str,
    *,
    url_a: str,
    url_b: str,
    threshold: float = 0.5,
) -> dict[str, Any]:
    """Combine path-normalisation + structural similarity."""
    same_path = normalize_for_compare(url_a) == normalize_for_compare(url_b)
    sim = structural_similarity(body_a, body_b)
    return {
        "same_path": same_path,
        "structural_similarity": sim,
        "is_same_article": same_path or sim >= threshold,
        "threshold": threshold,
    }


__all__ = [
    "normalize_for_compare",
    "structural_similarity",
    "is_same_article",
]
