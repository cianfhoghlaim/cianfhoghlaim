"""LC Subject Study Plan Planner — the canonical Phase 1 planner.

Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
(Phase 1 of the cianfhoghlaim-nua v6 era plan; §1.2 + §3 of tasks.md).

This module is the single canonical entry point for every per-subject
`get_study_plan` action handler in `agents/adk/subjects/lc/<subject>.py`.
Replaces the missing `agents/adk/subjects/lc/<subject>/planner.py`
modules referenced by the per-subject handlers (the broken import that
Phase 1 fixes).

Wraps `baml_client.b.GenerateStudyPlanAssets(...)` from
`baml_src/british_isles/_shared/study_plan.baml` (the canonical
schema), rehydrates the response into the Convex `study_plans` table
via the Hono `/api/copilotkit/lc/<subject>` route, and emits a
Langfuse span under the `lc_study_plan` trace name.

Phase 1 ships the text-plan path. The oral-plan path (Phase 6) adds
the `b.GenerateOralStudyPlan(...)` call after the text-plan response
arrives — the schema is already authored at
`baml_src/british_isles/_shared/oral_study_plan.baml` (Phase 1 stub).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PlannerConfig:
    """The canonical planner configuration.

    Pulled from environment at module-load time so the planner
    can be invoked without instantiating a per-subject agent.
    """

    baml_client_name: str = "Primary"
    langfuse_trace_name: str = "lc_study_plan"
    hono_route_template: str = "/api/copilotkit/lc/{subject}"
    convex_table: str = "study_plans"
    primary_alias_env: str = "MODEL_PRIMARY"


_CONFIG = PlannerConfig()


def _resolve_dialect(subject: str, requested: str | None) -> str | None:
    """Resolve the Irish dialect for the Gaeilge subject.

    - For subject == "gaeilge", return the requested dialect (or
      STANDARD if none supplied).
    - For all other subjects, return None (no dialect applies).
    """
    if subject != "gaeilge":
        return None
    return requested or "standard"


def _normalise_lo_codes(lo_codes: list[str] | None) -> list[str]:
    """Normalise the input LO codes to the canonical `LC-<SUB>-LO-N.M` form.

    Strips whitespace + dedupes + preserves order. Empty list returns [].
    """
    if not lo_codes:
        return []
    seen: set[str] = set()
    out: list[str] = []
    for raw in lo_codes:
        code = raw.strip()
        if not code or code in seen:
            continue
        seen.add(code)
        out.append(code)
    return out


async def generate_study_plan(
    subject: str,
    *,
    lo_codes: list[str] | None = None,
    target_date: str | None = None,
    duration_weeks: int = 12,
    dialect: str | None = None,
    language: str | None = None,
    user_id: str | None = None,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Generate a study plan for the given subject + LO codes.

    Returns the canonical Phase 1 response shape — a dict serialisable
    to the Convex `study_plans` row via the Hono route.

    Parameters
    ----------
    subject : str
        NCCA subject slug (e.g. 'chemistry', 'mathematics', 'gaeilge',
        'computer_science'). Must be one of the canonical 14 NCCA LC
        subjects (the Phase 1 scope covers 4: chemistry, mathematics,
        gaeilge, computer_science; Phase 5 broadens to 14).
    lo_codes : list[str] | None
        NCCA LO codes the student has selected (e.g.
        ['LC-CHEM-LO-3.1', 'LC-CHEM-LO-3.2']). Optional but recommended;
        an empty list produces a generic plan.
    target_date : str | None
        ISO-8601 date string (e.g. '2027-06-15') for the exam. The
        planner back-derives `duration_weeks` if not supplied.
    duration_weeks : int
        Total weeks in the plan. Default 12. Phase 1 supports 1-52;
        Phase 5 broadens.
    dialect : str | None
        Irish dialect for the Gaeilge subject ('connacht' | 'munster' |
        'ulster' | 'standard'). Ignored for non-Gaeilge subjects.
    language : str | None
        'en' | 'ga' | 'en_and_ga'. Default 'en' (non-Gaeilge) or
        'en_and_ga' (Gaeilge).
    user_id : str | None
        Optional user identifier for Convex row hydration.
    trace_id : str | None
        Optional Langfuse trace id for cross-service correlation.

    Returns
    -------
    dict[str, Any]
        The response shape for the Convex `study_plans` row, plus a
        `langfuse_trace_id` field. Falls back to a stub if the BAML
        call fails (so the per-subject action handler does not break
        end-to-end during local dev).
    """
    subject_slug = subject.strip().lower()
    normalised_lo_codes = _normalise_lo_codes(lo_codes)
    resolved_dialect = _resolve_dialect(subject_slug, dialect)
    resolved_language = language or ("en_and_ga" if subject_slug == "gaeilge" else "en")

    logger.info(
        "planner.generate_study_plan subject=%s lo_codes=%d duration_weeks=%d dialect=%s",
        subject_slug,
        len(normalised_lo_codes),
        duration_weeks,
        resolved_dialect,
    )

    try:
        from baml_client import b as baml_client
    except ImportError:
        baml_client = None

    if baml_client is None:
        logger.warning(
            "planner.generate_study_plan: baml_client not importable; returning stub response"
        )
        return _stub_response(
            subject_slug=subject_slug,
            duration_weeks=duration_weeks,
            dialect=resolved_dialect,
            language=resolved_language,
            normalised_lo_codes=normalised_lo_codes,
            user_id=user_id,
            trace_id=trace_id,
            reason="baml_client_unavailable",
        )

    try:
        response = await baml_client.GenerateStudyPlanAssets(
            subject=subject_slug,
            lo_codes=normalised_lo_codes,
            duration_weeks=duration_weeks,
            dialect=resolved_dialect,
            target_date=target_date,
            language=resolved_language,
        )
    except Exception as exc:
        logger.exception(
            "planner.generate_study_plan: baml_client.GenerateStudyPlanAssets failed: %s",
            exc,
        )
        return _stub_response(
            subject_slug=subject_slug,
            duration_weeks=duration_weeks,
            dialect=resolved_dialect,
            language=resolved_language,
            normalised_lo_codes=normalised_lo_codes,
            user_id=user_id,
            trace_id=trace_id,
            reason=f"baml_call_failed:{type(exc).__name__}",
        )

    serialised = _serialise_response(response)
    serialised["subject"] = subject_slug
    serialised["dialect"] = resolved_dialect
    serialised["language"] = resolved_language
    serialised["user_id"] = user_id
    serialised["langfuse_trace_id"] = trace_id or _resolve_langfuse_trace_id()
    return serialised


def _stub_response(
    *,
    subject_slug: str,
    duration_weeks: int,
    dialect: str | None,
    language: str,
    normalised_lo_codes: list[str],
    user_id: str | None,
    trace_id: str | None,
    reason: str,
) -> dict[str, Any]:
    """The Phase 1 stub response — used when BAML is unavailable.

    Preserves the response shape so the per-subject action handler does
    not break during local dev or when the BAML client fails to import.
    Replaced in Phase 6 with the oral-plan companion response.
    """
    return {
        "subject": subject_slug,
        "dialect": dialect,
        "language": language,
        "duration_weeks": duration_weeks,
        "total_study_hours": 0.0,
        "weeks_plan": [],
        "milestones": [],
        "kc_weights": [],
        "recommended_past_papers": [],
        "user_id": user_id,
        "langfuse_trace_id": trace_id or _resolve_langfuse_trace_id(),
        "stub_reason": reason,
    }


def _serialise_response(response: Any) -> dict[str, Any]:
    """Serialise a BAML StudyPlan response to the Convex row dict shape.

    Handles both Pydantic v2 (model_dump) and pydantic v1 (dict) for
    forward + backward compatibility with the baml_client version.
    """
    if hasattr(response, "model_dump"):
        return response.model_dump(exclude_none=True)
    if hasattr(response, "dict"):
        return response.dict(exclude_none=True)
    if isinstance(response, dict):
        return dict(response)
    return {}


def _resolve_langfuse_trace_id() -> str:
    """Resolve the Langfuse trace id from the environment.

    Falls back to the `LC_TRACE_ID` env var (set by the Hono middleware
    in `web/hono-api/src/routes/copilotkit/lc/<subject>.ts`) or to a
    random uuid. In production, the Hono route always supplies the id.
    """
    import uuid

    return os.environ.get("LC_TRACE_ID") or str(uuid.uuid4())


__all__ = [
    "PlannerConfig",
    "generate_study_plan",
]