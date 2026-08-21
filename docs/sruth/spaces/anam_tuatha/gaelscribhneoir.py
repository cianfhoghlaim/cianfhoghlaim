"""
spaces/anam_tuatha/gaelscribhneoir.py
Tine theme: OCR Gaelscribhneoir (Gaelic-script quality checker).

A simplified version of the fada/tironian/punctum metrics from
meaisinfhoghlaim/ocr/gaelic_metrics.py:195-242. This is *not* a real
OCR model - it's a character-level quality check that scores how
"good" a piece of Irish-language text is on three axes:
  1. Fada coverage: does every accented vowel have its fada?
  2. Tironian 'eclipsis: are the eclipsis markers (n-, h-, t-, m-, b-,
     d-, g-, s-) present where expected?
  3. Punctum (dot-bubble) health: are the dot-bubbles consistent?

The Space can be used to:
  - Check the quality of an LLM-generated Irish paragraph
  - Demonstrate the difference between "raw output" and "post-OCR
    cleaned" text
  - Show the metric values that the meaisinfhoghlaim/ocr pipeline
    would emit (this is the demo "thin" version)
"""

from __future__ import annotations

import re
from dataclasses import dataclass


# Irish vowels and the words that should carry a fada
_VOWELS = "aeiouáéíóú"
_FADA_MAP = str.maketrans(
    {
        "a": "á",
        "e": "é",
        "i": "í",
        "o": "ó",
        "u": "ú",
    }
)
# Reverse map for detecting missing fada
_UNFADA_MAP = str.maketrans(
    {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
    }
)

# Words that *must* have a fada in standard Irish
_FADA_REQUIRED: set[str] = {
    "an",
    "is",
    "ar",
    "ag",
    "do",
    "go",
    "ba",
    "ní",
    "sé",
    "sí",
    "tá",
    "cá",
    "má",
    "dá",
    "sara",
    "ionas",
}


@dataclass
class GaelicMetrics:
    fada_coverage: float  # 0.0 - 1.0
    fada_required_missing: list[str]  # words that should have fada but don't
    tironian_eclipsis_count: int  # count of n-, h-, t-, etc. sequences
    punctum_health: float  # 0.0 - 1.0
    overall_score: float  # 0.0 - 1.0
    word_count: int
    issues: list[str]


# Pattern for eclipsis: a vowel initial word preceded by d', n', h', t',
# m', b' (in orthography these are written as separate words or with hyphens)
_ECLIPSIS_PATTERN = re.compile(
    r"\b[d|h|t|m|b|g|n]'[aeiouáéíóú]",
    re.UNICODE,
)

# Punctum (dot-bubble) check: count of "." in the text per sentence
_PUNCTUM_PATTERN = re.compile(r"\.")


def check_irish_text(text: str) -> GaelicMetrics:
    """Score an Irish text on the 3 axes + overall.

    Args:
        text: The Irish text to check.

    Returns:
        A GaelicMetrics with the 4 scores and a list of issues.
    """
    if not text.strip():
        return GaelicMetrics(
            fada_coverage=0.0,
            fada_required_missing=[],
            tironian_eclipsis_count=0,
            punctum_health=0.0,
            overall_score=0.0,
            word_count=0,
            issues=["Empty input."],
        )

    words = re.findall(r"[\w']+", text)
    word_count = len(words)
    issues: list[str] = []

    # 1. Fada coverage: count vowels that ARE fada-marked, vs total vowel instances
    vowel_count = sum(1 for c in text.lower() if c in _VOWELS)
    fada_count = sum(1 for c in text.lower() if c in "áéíóú")
    fada_coverage = fada_count / max(vowel_count, 1)

    # Check required fada words (only those that are unambiguous)
    # Most Irish function words (an, is, ar, ag, do, go) are unaccented
    # in most contexts. We only flag words where the fada is required
    # in 100% of contexts (very short list, kept conservative for the
    # demo).
    fada_missing: list[str] = []
    for word in words:
        w_lower = word.lower()
        # In the demo we only check the unambiguous fada-bearing forms
        if w_lower in {"tá", "ní", "sé", "sí", "cá", "má", "dá", "sara"}:
            if not any(c in word for c in "áéíóú"):
                fada_missing.append(word)
                issues.append(f"Missing fada on '{word}'")

    # 2. Tironian eclipsis count
    eclipsis = _ECLIPSIS_PATTERN.findall(text)
    eclipsis_count = len(eclipsis)

    # 3. Punctum health: sentences should end with "." (not too dense, not too sparse)
    sentence_count = len(_PUNCTUM_PATTERN.findall(text))
    ideal_sentences = max(1, word_count // 15)  # ~15 words per sentence ideal
    punctum_density = sentence_count / ideal_sentences
    # Penalise if too dense (>2x ideal) or too sparse (<0.5x)
    if 0.5 <= punctum_density <= 2.0:
        punctum_health = 1.0 - abs(punctum_density - 1.0) * 0.3
    else:
        punctum_health = 0.3
        if punctum_density > 2.0:
            issues.append("Too many short sentences (run-ons?)")
        else:
            issues.append("Too few sentence ends (no punctuation?)")

    # 4. Overall score: weighted average
    fada_penalty = 0.2 * len(fada_missing) if fada_missing else 0.0
    overall = (
        fada_coverage * 0.5
        + min(1.0, eclipsis_count / max(word_count / 50, 1)) * 0.2
        + punctum_health * 0.3
    ) - fada_penalty
    overall = max(0.0, min(1.0, overall))

    return GaelicMetrics(
        fada_coverage=fada_coverage,
        fada_required_missing=fada_missing,
        tironian_eclipsis_count=eclipsis_count,
        punctum_health=punctum_health,
        overall_score=overall,
        word_count=word_count,
        issues=issues,
    )


# Sample Irish text (well-formed) for the demo
SAMPLE_GOOD_TEXT = """Tá fáilte romhat chuig an spás seo. Is é an aidhm atá againn ná an
Ghaeilge a chur chun cinn ar líne. Táimid ag obair ar uirlisí nua a
chruthú don oideachas. Is í an Ghaeilge teanga álainn ár sinsear."""

# Sample Irish text (poorly formed - missing fada, no eclipsis)
SAMPLE_BAD_TEXT = """ta failte romhat chuig an spas seo. is e an aidhm ata againn na an
Ghaeilge a cur chun cinn ar line. taimid ag obair ar uirlisi nua a
chruthu don oideachas. is i an Ghaeilge teanga alainn ar sinsear."""


def render_metrics_html(metrics: GaelicMetrics) -> str:
    """Render the metrics as an HTML card."""
    overall_color = (
        "#28955e"
        if metrics.overall_score > 0.8
        else "#d68c1c"
        if metrics.overall_score > 0.5
        else "#a83a2a"
    )
    issues_html = ""
    if metrics.issues:
        issues_items = "".join(f"<li>{i}</li>" for i in metrics.issues)
        issues_html = (
            f'<div style="margin-top:0.8em; padding:0.8em; '
            f'background:#1a1d2e; border-left:3px solid #a83a2a;">'
            f'<strong style="color:#a83a2a;">Issues:</strong>'
            f'<ul style="margin:0.3em 0 0 1em; color:#d8d4cc;">{issues_items}</ul>'
            f"</div>"
        )

    return (
        f'<div class="gaelscribhneoir-card" '
        f'style="background:#1a1d2e; padding:1.5em; border:2px solid #d68c1c; '
        f'border-radius:4px;">'
        f'<h3 style="color:#d68c1c; margin:0 0 0.5em 0; '
        f'font-family:Cinzel,serif;">Gaelscribhneoir</h3>'
        f'<div style="display:grid; grid-template-columns:1fr 1fr; '
        f'gap:0.5em; font-family:Inter,sans-serif;">'
        f'<div><span style="color:#bcb8b0;">Fada coverage:</span> '
        f'<strong style="color:#28955e;">{metrics.fada_coverage:.1%}</strong></div>'
        f'<div><span style="color:#bcb8b0;">Eclipsis count:</span> '
        f'<strong style="color:#5a4fcf;">{metrics.tironian_eclipsis_count}</strong></div>'
        f'<div><span style="color:#bcb8b0;">Punctum health:</span> '
        f'<strong style="color:#1e80c6;">{metrics.punctum_health:.1%}</strong></div>'
        f'<div><span style="color:#bcb8b0;">Word count:</span> '
        f'<strong style="color:#d8d4cc;">{metrics.word_count}</strong></div>'
        f'<div style="grid-column:1 / -1; margin-top:0.5em;">'
        f'<span style="color:#bcb8b0;">Overall score:</span> '
        f'<strong style="color:{overall_color}; font-size:1.4em;">'
        f"{metrics.overall_score:.1%}</strong></div>"
        f"</div>" + issues_html + "</div>"
    )
