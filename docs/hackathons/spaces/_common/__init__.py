"""
spaces/_common/__init__.py
Cianfhoghlaim Build-Small 2026 shared bundle.

This bundle is the cross-cutting infrastructure for the 4 HF Spaces:
  - Space 1 "An Scrúdú" (oideachais, Talamh)
  - Space 2 "Meaisín Cliste" (meaisínfhoghlaim, Uisce + Aer)
  - Space 3 "Cianfhoghlaim" (tuatha, Aer + Anam)
  - Space 4 "Anam: Tuatha na nGaelscoil" (croílár, all 5 elements)

Re-exports:
  - theme:           Celtic 5-element palette + Hades Shadow-First
  - anam_bonneagar:  per-Space footer (Pobal HP + 32B alias + linter score)
  - soulbound_svg:   deterministic Celtic-knot SVG generator
  - social_card:     HF social card auto-renderer
  - i18n:            bilingual EN/GA toggle
  - baml_client:     re-pointed HF Inference client (3-tier fallback)
"""

from spaces._common.theme import (
    CELTIC_PALETTE,
    HADES_PALETTE,
    GRADIO_CSS,
    apply_celtic_theme,
)
from spaces._common.anam_bonneagar import render_anam_bonneagar_footer
from spaces._common.soulbound_svg import render_soulbound_svg
from spaces._common.social_card import render_social_card
from spaces._common.i18n import I18N_STRINGS, translate
from spaces._common.baml_client import (
    HACKATHON_PRIMARY_MODEL,
    HACKATHON_FALLBACK_1_MODEL,
    HACKATHON_FALLBACK_2_MODEL,
    HF_INFERENCE_BASE_URL,
    get_hackathon_client_config,
)

__all__ = [
    "CELTIC_PALETTE",
    "HADES_PALETTE",
    "GRADIO_CSS",
    "apply_celtic_theme",
    "render_anam_bonneagar_footer",
    "render_soulbound_svg",
    "render_soulbound_html",
    "render_social_card",
    "render_social_card_html",
    "I18N_STRINGS",
    "translate",
    "HACKATHON_PRIMARY_MODEL",
    "HACKATHON_FALLBACK_1_MODEL",
    "HACKATHON_FALLBACK_2_MODEL",
    "HF_INFERENCE_BASE_URL",
    "get_hackathon_client_config",
]
