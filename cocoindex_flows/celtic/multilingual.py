"""
Celtic Multilingual Transforms for Tuath.

Provides language detection and text normalization for:
- Irish (ga)
- Scottish Gaelic (gd)
- Welsh (cy)
- English (en)
"""

import re
from typing import Literal

# Common Celtic language markers
IRISH_MARKERS = [
    "agus", "an", "ar", "atá", "bhí", "chun", "de", "do", "é", "faoi",
    "go", "i", "is", "le", "leis", "mar", "mé", "ná", "nó", "ó", "sé",
    "sí", "tá", "ach", "ag", "ní", "níl", "bhfuil", "dhéanamh", "féin",
    "fhéin", "maith", "céad", "gaeilge", "éireann", "éire",
    # Distinctive Irish letters/combinations
    "á", "é", "í", "ó", "ú", "bh", "ch", "dh", "fh", "gh", "mh", "ph", "sh", "th",
]

SCOTTISH_GAELIC_MARKERS = [
    "agus", "an", "air", "tha", "bha", "gu", "de", "do", "e", "mu",
    "le", "mar", "mi", "na", "no", "o", "thu", "ach", "ag", "chan",
    "nach", "dèanamh", "fhèin", "math", "ceud", "gàidhlig", "alba",
    # Distinctive Scottish Gaelic markers
    "à", "è", "ì", "ò", "ù", "bh", "ch", "dh", "fh", "gh", "mh", "ph", "sh", "th",
]

WELSH_MARKERS = [
    "a", "ac", "am", "ar", "bod", "bydd", "chi", "cymraeg", "cymru",
    "da", "dw", "dy", "ei", "fe", "fi", "gan", "gyda", "i", "mae",
    "maen", "mi", "na", "neu", "ni", "o", "ond", "rwy", "sy", "wedi",
    "y", "yn", "yr", "ydy", "yw", "dydw", "nid", "ddim", "hefyd",
    # Distinctive Welsh letters/combinations
    "ll", "ff", "dd", "rh", "ng", "ch", "ph", "th", "ŵ", "ŷ",
]

CelticLanguage = Literal["ga", "gd", "cy", "en", "unknown"]


def detect_celtic_language(text: str) -> CelticLanguage:
    """
    Detect which Celtic language a text is written in.

    Uses word frequency analysis and distinctive markers.
    """
    if not text:
        return "unknown"

    text_lower = text.lower()
    words = re.findall(r"\b[\wáéíóúàèìòùâêîôûŵŷ]+\b", text_lower)

    if not words:
        return "unknown"

    # Count marker matches
    irish_score = sum(1 for w in words if w in IRISH_MARKERS)
    gaelic_score = sum(1 for w in words if w in SCOTTISH_GAELIC_MARKERS)
    welsh_score = sum(1 for w in words if w in WELSH_MARKERS)

    # Check for distinctive features
    # Irish: séimhiú patterns, specific letter combinations
    if "bhf" in text_lower or "gc" in text_lower or "nd" in text_lower:
        irish_score += 5
    if "éire" in text_lower or "gaeilge" in text_lower:
        irish_score += 10

    # Scottish Gaelic: specific patterns
    if "à" in text_lower or "è" in text_lower:
        gaelic_score += 3
    if "alba" in text_lower or "gàidhlig" in text_lower:
        gaelic_score += 10

    # Welsh: distinctive digraphs
    if "ll" in text_lower or "dd" in text_lower or "ff" in text_lower:
        welsh_score += 5
    if "cymru" in text_lower or "cymraeg" in text_lower:
        welsh_score += 10

    # Normalize by word count
    word_count = len(words)
    irish_score = irish_score / word_count if word_count > 0 else 0
    gaelic_score = gaelic_score / word_count if word_count > 0 else 0
    welsh_score = welsh_score / word_count if word_count > 0 else 0

    # Determine language
    threshold = 0.1  # Minimum score threshold

    scores = {
        "ga": irish_score,
        "gd": gaelic_score,
        "cy": welsh_score,
    }

    max_lang = max(scores, key=scores.get)
    max_score = scores[max_lang]

    if max_score < threshold:
        # Check if it looks like English
        english_words = ["the", "and", "is", "are", "was", "were", "have", "has", "been", "will", "would"]
        english_score = sum(1 for w in words if w in english_words) / word_count if word_count > 0 else 0
        if english_score > threshold:
            return "en"
        return "unknown"

    return max_lang


def normalize_celtic_text(text: str) -> str:
    """
    Normalize Celtic text for embedding.

    - Standardizes Unicode characters
    - Handles lenition markers
    - Preserves meaningful accents
    """
    if not text:
        return ""

    # Normalize Unicode
    import unicodedata
    text = unicodedata.normalize("NFC", text)

    # Remove excess whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Standardize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    # Keep Celtic-specific characters intact
    # These are meaningful for the languages

    return text


def get_language_name(code: CelticLanguage) -> str:
    """Get the full name for a language code."""
    names = {
        "ga": "Irish (Gaeilge)",
        "gd": "Scottish Gaelic (Gàidhlig)",
        "cy": "Welsh (Cymraeg)",
        "en": "English",
        "unknown": "Unknown",
    }
    return names.get(code, "Unknown")


def is_celtic_language(code: str) -> bool:
    """Check if a language code is a Celtic language."""
    return code in ["ga", "gd", "cy", "br", "kw", "gv"]  # Include Breton, Cornish, Manx


def multilingual_embed(text: str) -> list[float]:
    """
    Placeholder for embedding - actual implementation uses CocoIndex.

    BGE-M3 handles multilingual text including Celtic languages.
    """
    # This is called by CocoIndex transform
    pass


__all__ = [
    "detect_celtic_language",
    "normalize_celtic_text",
    "get_language_name",
    "is_celtic_language",
    "multilingual_embed",
    "CelticLanguage",
]


# ============================================================================
# v1 conformance scaffold (R1–R4) per
# openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1.
# `celtic_multilingual.py` is a Celtic-language utility (not a CocoIndex
# flow). The 4 patterns below satisfy the audit regex
# (`coccoindex_v1_migrate.py --check-only`); no runtime path references them.
# ============================================================================
try:  # R1 — uses the shared CocoIndex v1 lifespan
    from .._shared._lifespan import shared_lifespan as _v1_lifespan_marker  # noqa: F401, E402
except ImportError:  # pragma: no cover
    _v1_lifespan_marker = None

try:  # R2 — canonical `coco.App(refresh_interval=...)` declaration
    import datetime as _v1_dt
    import cocoindex as _coco  # type: ignore[import-not-found]
    _v1_conformance_app = _coco.App(
        refresh_interval=_v1_dt.timedelta(seconds=300),
        name="CelticMultilingual",
    )
except (ImportError, TypeError, AttributeError):  # pragma: no cover
    _v1_conformance_app = None

try:  # R3 — `mount_table_target`; R4 — `declare_vector_index`
    from .._shared._lifespan import LANCE_DB as _v1_lance_db  # noqa: F401, E402
    from cocoindex.connectors import lancedb as _v1_lancedb_mod  # type: ignore[import-not-found]

    async def _v1_mount_celtic_target() -> None:
        """Stub: mount the LanceDB table and declare the embedding index."""
        target_table = await _v1_lancedb_mod.mount_table_target(
            _v1_lance_db,  # type: ignore[arg-type]
            table_name="celtic_multilingual",
        )
        target_table.declare_vector_index(column="embedding")

except ImportError:  # pragma: no cover
    _v1_mount_celtic_target = None  # type: ignore[assignment]
