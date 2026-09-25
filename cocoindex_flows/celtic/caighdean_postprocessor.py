"""Caighdean post-processor for the Gaeilge CocoIndex embedding App.

Phase 1.6 (2026-09-25 5-phase Celtic overhaul) — the caighdean post-processor
wraps `cocoindex_flows/_shared/caighdean_standardize.CaighdeanTransform` so the
Gaeilge embedding pipeline can call it as a per-chunk transform.

The post-processor:
  1. Strips wikitext markup (ref, template, image, span)
  2. Strips TN6 hyperlinks (markdown + HTML + bare URLs)
  3. Captures Teanglann.ie audio links (returned separately; not embedded)
  4. Applies Caighdean Oifigiúil standardisation (pre-1936 → modern)
  5. Returns (standardised, raw, change_count)

The function is pure-Python (no I/O, no LLM calls), so it adds no
latency to the embedding pipeline. It runs BEFORE the BGE-M3 embed
so the embedding captures modern standard Irish consistently.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the caighdean_standardize module importable (Phase 1.3).
_THIS_DIR = Path(__file__).parent
_SHARED_DIR = _THIS_DIR.parent / "_shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

# Lazily imported CaighdeanTransform — only instantiated on first call.
# This avoids the ~1s startup cost (loading 4.9MB pairs.txt + 73KB multi.txt)
# for tests / scripts that don't need the post-processor.
_caighdean: object | None = None


def _get_caighdean() -> object:
    """Lazy-singleton CaighdeanTransform (Phase 1.3)."""
    global _caighdean
    if _caighdean is None:
        from caighdean_standardize import CaighdeanTransform
        _caighdean = CaighdeanTransform()
    return _caighdean


def standardize_gaeilge_chunk(text: str) -> tuple[str, str, int]:
    """Standardise a single Gaeilge chunk via the full caighdean pipeline.

    Returns:
        (standardised_text, raw_text, change_count)
          - standardised_text: the chunk after Phase 1.3 cleanup + Caighdean
          - raw_text: the original chunk (preserved for the marimo notebook diff view)
          - change_count: the number of word-level changes applied

    The chunk is processed through the full Phase 1.3 pipeline:
      1. strip_wikitext (ref / template / image / span)
      2. strip_tn6_hyperlinks (markdown + HTML + bare URLs)
      3. capture_teanglann_audio_links (returned separately — not embedded)
      4. Caighdean Oifigiúil standardisation (pre-1936 → modern)

    Note: For the per-chunk embedding pipeline, the Teanglann audio
    links are NOT attached to the chunk (they would inflate the chunk
    size). They're stored separately in `notebooks/36_gaeilge_full_curriculum.py`
    via the MotherDuck Dive (Phase 1.9).
    """
    from caighdean_standardize import standardize_full_clean

    # Phase 1.3 step 1 + 2: full pre-clean (wikitext + TN6 hyperlinks).
    cleaned, audio_links = standardize_full_clean(text)

    # Phase 1.3 step 3: caighdean standardisation.
    caighdean = _get_caighdean()
    standardised = caighdean.transform(cleaned).transformed  # type: ignore[attr-defined]

    # Compute the word-level change count (cleaned → standardised).
    original_words = cleaned.split()
    standardised_words = standardised.split()
    change_count = sum(
        1 for o, s in zip(original_words, standardised_words) if o != s
    )
    # Account for word-count differences (Caighdean may add/remove words).
    change_count += abs(len(original_words) - len(standardised_words))

    return standardised, text, change_count
