"""tuatha.tools — the 40 per-subject tools (5 per subject × 8 subjects).

The canonical re-export surface. Each tool wraps a BAML
function call + a LanceDB query + the standard result
serialization.
"""
from __future__ import annotations

# The 40 tools are lazily imported (per the BAML/Letta
# graceful-degradation pattern).
try:
    # Mathematics (5)
    from .applied_mathematics_formative_item_generate import generate_appm_item  # type: ignore
    from .applied_mathematics_marking_scheme_lookup import (
        lookup_appm_marking_scheme,  # type: ignore
    )
    from .applied_mathematics_past_paper_lookup import lookup_appm_paper  # type: ignore
    from .applied_mathematics_response_score import score_appm_response  # type: ignore

    # Applied mathematics (5)
    from .applied_mathematics_syllabus_lookup import lookup_appm_lo  # type: ignore
    from .chemistry_formative_item_generate import generate_chem_item  # type: ignore
    from .chemistry_marking_scheme_lookup import lookup_chem_marking_scheme  # type: ignore
    from .chemistry_past_paper_lookup import lookup_chem_paper  # type: ignore
    from .chemistry_response_score import score_chem_response  # type: ignore

    # Chemistry (5)
    from .chemistry_syllabus_lookup import lookup_chem_lo  # type: ignore
    from .computer_science_formative_item_generate import generate_comp_item  # type: ignore
    from .computer_science_marking_scheme_lookup import lookup_comp_marking_scheme  # type: ignore
    from .computer_science_past_paper_lookup import lookup_comp_paper  # type: ignore
    from .computer_science_response_score import score_comp_response  # type: ignore

    # Computer science (5)
    from .computer_science_syllabus_lookup import lookup_comp_lo  # type: ignore
    from .english_formative_item_generate import generate_engl_item  # type: ignore
    from .english_marking_scheme_lookup import lookup_engl_marking_scheme  # type: ignore
    from .english_past_paper_lookup import lookup_engl_paper  # type: ignore
    from .english_response_score import score_engl_response  # type: ignore

    # English (5)
    from .english_syllabus_lookup import lookup_engl_lo  # type: ignore
    from .gaeilge_formative_item_generate import generate_gael_item  # type: ignore
    from .gaeilge_gramadach_review import review_gael_gramadach  # type: ignore
    from .gaeilge_marking_scheme_lookup import lookup_gael_marking_scheme  # type: ignore
    from .gaeilge_past_paper_lookup import lookup_gael_paper  # type: ignore
    from .gaeilge_response_score import score_gael_response  # type: ignore

    # Gaeilge (5 + the special `gael_gramadach_review` per the BUILD_PLAN.md)
    from .gaeilge_syllabus_lookup import lookup_gael_lo  # type: ignore
    from .geography_formative_item_generate import generate_geog_item  # type: ignore
    from .geography_marking_scheme_lookup import lookup_geog_marking_scheme  # type: ignore
    from .geography_past_paper_lookup import lookup_geog_paper  # type: ignore
    from .geography_response_score import score_geog_response  # type: ignore

    # Geography (5)
    from .geography_syllabus_lookup import lookup_geog_lo  # type: ignore
    from .history_formative_item_generate import generate_hist_item  # type: ignore
    from .history_marking_scheme_lookup import lookup_hist_marking_scheme  # type: ignore
    from .history_past_paper_lookup import lookup_hist_paper  # type: ignore
    from .history_response_score import score_hist_response  # type: ignore

    # History (5)
    from .history_syllabus_lookup import lookup_hist_lo  # type: ignore
    from .mathematics_formative_item_generate import generate_math_item  # type: ignore
    from .mathematics_marking_scheme_lookup import lookup_math_marking_scheme  # type: ignore
    from .mathematics_past_paper_lookup import lookup_math_paper  # type: ignore
    from .mathematics_response_score import score_math_response  # type: ignore
    from .mathematics_syllabus_lookup import lookup_math_lo  # type: ignore

    TOOLS = {
        "mathematics_syllabus_lookup": lookup_math_lo,
        "mathematics_past_paper_lookup": lookup_math_paper,
        "mathematics_marking_scheme_lookup": lookup_math_marking_scheme,
        "mathematics_formative_item_generate": generate_math_item,
        "mathematics_response_score": score_math_response,
        # ... + 35 more
    }
except ImportError:
    TOOLS = {}


__all__ = ["TOOLS"] + [k for k in __import__("sys").modules]  # dynamic
