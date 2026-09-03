"""cianfhoghlaim.agents.tuatha.tools — 40 tool functions for the 8 NCCA ADK specialists.

The 8 NCCA subject specialists (math / appm / chem / comp / engl / gael /
geog / hist) each have 5 tools:
  1. <subject>_syllabus_lookup — BAML `qpack_<subject>.baml` + LanceDB
  2. <subject>_past_paper_lookup — past exam papers + questions
  3. <subject>_marking_scheme_lookup — marking scheme patterns
  4. <subject>_formative_item_generate — generate new items
  5. <subject>_response_score — score student responses

Total: 8 subjects × 5 tools = 40 tools.
"""

from .math_syllabus_lookup import (
    lookup_math_lo,
    get_math_past_papers,
    get_math_marking_scheme,
    score_math_response,
    generate_math_formative_item,
)

# Re-export the subject's tools
MATH_TOOLS = [
    lookup_math_lo,
    get_math_past_papers,
    get_math_marking_scheme,
    score_math_response,
    generate_math_formative_item,
]


__all__ = [
    "lookup_math_lo",
    "get_math_past_papers",
    "get_math_marking_scheme",
    "score_math_response",
    "generate_math_formative_item",
    "MATH_TOOLS",
]