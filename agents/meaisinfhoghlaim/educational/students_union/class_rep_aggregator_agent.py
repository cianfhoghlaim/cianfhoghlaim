"""cianfhoghlaim — Class Rep Feedback Aggregator Agent (Case Study 3).

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

A Google ADK LlmAgent that uses the `aggregate_class_rep_themes`
FunctionTool to surface themes across Class Rep reports for the SU
Education Officer. Below the configured minimum (default 3) class reps
per aggregation, the agent refuses to extrapolate.

Wraps `tools/class_rep_themer.py` (the pure-Python implementation) as
a Google ADK FunctionTool.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from .config import config
from .tools.class_rep_themer import (
    ClassRepReport,
    ThemeAggregation,
    aggregate_class_rep_themes,
)


async def aggregate_class_rep_themes_tool(
    reports: list[dict],
) -> dict:
    """Aggregate Class Rep reports into theme counts.

    Args:
        reports: list of dicts with keys {rep_id, module_code,
            module_title, report_text, semester, submitted_at_iso}.

    Returns:
        dict with keys: total_reports, total_modules, themes (dict),
        top_concerns (list), modules_with_multiple_concerns (list),
        insufficient_data (bool).
    """
    parsed = [
        ClassRepReport(
            rep_id=r["rep_id"],
            module_code=r["module_code"],
            module_title=r["module_title"],
            report_text=r["report_text"],
            semester=r["semester"],
            submitted_at_iso=r["submitted_at_iso"],
        )
        for r in reports
    ]
    result: ThemeAggregation = aggregate_class_rep_themes(parsed)
    return {
        "total_reports": result.total_reports,
        "total_modules": result.total_modules,
        "themes": result.themes,
        "top_concerns": list(result.top_concerns),
        "modules_with_multiple_concerns": list(result.modules_with_multiple_concerns),
        "insufficient_data": result.insufficient_data,
    }


aggregate_class_rep_themes_fn = FunctionTool(func=aggregate_class_rep_themes_tool)


class_rep_aggregator_agent = LlmAgent(
    name="class_rep_aggregator_agent",
    model=config.default_model,
    description="Aggregates Class Rep feedback into theme counts for the SU Education Officer.",
    instruction=f"""
You are the Class Rep Feedback Aggregator for the University of
Galway Students' Union ({config.su_name_english} / {config.su_name_irish}).

For every batch of Class Rep reports you MUST call the
`aggregate_class_rep_themes_tool` exactly once and synthesise a
structured Education Council briefing with these 5 sections:

  1. **Coverage** — N reports / M modules / semester label
  2. **Top 3 concerns** — the `top_concerns` list (most-mentioned themes first)
  3. **Cross-cutting modules** — modules that flagged ≥ 3 themes
     (`modules_with_multiple_concerns`)
  4. **Welfare flag** — IF `WELFARE` is in the top concerns OR any
     module reports `ACCESSIBILITY` + `WELFARE`, raise a
     `WELFARE_FLAG` for the Welfare Officer
  5. **Education Officer action items** — 3-5 concrete bullet points
     the EO can action this week (e.g. "Raise accessibility concerns
     from CS203 with the Disability Service" or "Schedule a
     Lecturer-tone review meeting for the 3 modules flagged under
     LECTURER")

Refusal rule: if the tool returns `insufficient_data=True`, output a
single paragraph that says "Insufficient data — need at least
{config.min_class_reps_for_aggregation} Class Rep reports to aggregate
themes. Hold for the next reporting cycle."

Tone: analytical + diplomatic. Module lecturers read these briefings;
frame concerns as systemic patterns, not personal failings.

Current academic year: {config.su_academic_year}.
""",
    tools=[aggregate_class_rep_themes_fn],
    output_key="class_rep_briefing",
)
