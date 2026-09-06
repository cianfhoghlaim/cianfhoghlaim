"""PR0.2 — content-based language detector (Requirement §content-based).

This module is the single canonical implementation of the
`language_detector.py` declared by `openspec/specs/ciancheiltis/spec.md`.
It MUST NOT trust any `metadata["language"]` tag from upstream sources —
the SI 2007/1484 page on `legislation.gov.uk` ships with
`metadata["language"] = "eng"` while its body is predominantly Welsh.

The detector uses the `lingua-py` library on the **first 5 KB of the
page body** to return a `{language_iso: probability}` dictionary.
"""
from __future__ import annotations

from typing import Any


def detect_languages(body: str | bytes, *, top_k: int = 2) -> dict[str, float]:
    """Return the top-k languages detected in `body`.

    Args:
        body: The page body (markdown, HTML, or plain text).
        top_k: How many of the top-detected languages to return.

    Returns:
        A dict `{iso_code: probability}` summing to ~1.0.

    Raises:
        ImportError: If `lingua` is not installed (lazy, so absence is
            not fatal at import time).
    """
    try:
        from lingua import LanguageDetectorBuilder  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError(
            "`lingua-py` is required for ciancheiltis content-based "
            "language detection. Install with "
            "`uv add lingua-language-detector`."
        ) from exc

    text = body[:5120] if isinstance(body, (str, bytes)) else str(body)[:5120]
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")

    detector = (
        LanguageDetectorBuilder.from_all_languages()
        .with_preloaded_language_models()
        .build()
    )
    confidence_values = detector.compute_language_confidence_values(text)
    out: dict[str, float] = {}
    for cv in confidence_values[:top_k]:
        out[cv.language.iso_code_639_1.name.lower()] = float(cv.value)
    if not out:
        return {"unknown": 0.0}
    total = sum(out.values()) or 1.0
    return {code: round(prob / total, 4) for code, prob in out.items()}


def is_predominantly(body: str | bytes, *, expected_iso: str, threshold: float = 0.6) -> bool:
    """Return True if `body` is mostly in `expected_iso`."""
    detected = detect_languages(body, top_k=1)
    if not detected:
        return False
    top_code, top_prob = next(iter(detected.items()))
    return top_code == expected_iso.lower() and top_prob >= threshold


def metadata_mismatch(
    body: str | bytes,
    metadata: dict[str, Any],
    *,
    expected_iso: str,
) -> dict[str, Any]:
    """Return a `{mismatch: bool, ...}` summary when metadata lies.

    Use this in DLT sources where the upstream `language` tag is
    unreliable — the canonical SI 2007/1484 example.
    """
    detected = detect_languages(body, top_k=1)
    metadata_lang = (metadata.get("language") or "").lower()
    expected = expected_iso.lower()
    return {
        "detected_languages": detected,
        "metadata_language": metadata_lang or None,
        "expected_iso": expected,
        "mismatch": detected and next(iter(detected)) != metadata_lang[:2],
    }


__all__ = [
    "detect_languages",
    "is_predominantly",
    "metadata_mismatch",
]
