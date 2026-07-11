"""Shared per-subject workflow handlers (BIEP v1 LC subjects).

Ships the 3 user-facing per-subject workflow handlers used by each of
the 6 BIEP v1 LC subjects (Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science):

1. :func:`make_study_plan`        — produce a per-subject study plan
   (lectionary + per-student progress) by calling each subject's
   BAML ``Generate<Prefix>FormativeItem`` function once per NCCA LO.
2. :func:`discuss_exam_paper`     — discuss a past exam paper: load
   the items + matching marking schemes + generate practice items.
3. :func:`explain_marking_scheme` — explain a marking scheme: load
   the canonical NCCA text + the related past-paper items + generate
   an exemplar practice item + score a sample response.

The 3 handler factories are parameterised by:
- ``wiring`` — the per-subject :class:`SubjectAgentWiring` (gives us
  the trace name + cognee dataset + BAML prefix);
- the 4-5 per-subject tool callables (the ``*_syllabus_lookup`` +
  ``*_past_paper_lookup`` + ``*_marking_scheme_lookup`` +
  ``*_formative_item_generate`` + ``*_response_score`` async fns).

Each of the 6 ``<slug>_agent.py`` modules wires its own tool calls
through :func:`build_subject_workflow_handlers` at the bottom of the
module, then attaches the returned 3 handlers to its
:class:`WireSubjectAgent` via :func:`dataclasses.replace`.

Reference: openspec/changes/2026-07-16-biiep-v1-lc-per-subject-agent-workflows-v1
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Awaitable, Callable

from .wiring import SubjectAgentWiring, WireSubjectAgent


# ---------------------------------------------------------------------------
# Public types — the 3 response shapes the handlers emit.
# All three are plain JSON-serialisable dicts (back-compat with the
# existing 4-5 per-subject tool wrappers).
# ---------------------------------------------------------------------------


# A single lectionary entry: one week's worth of work for one NCCA LO.
LectionaryEntry = dict[str, Any]

# The 3 handler factories accept the per-subject wiring + tool refs and
# return 3 async callables that the corresponding ``<slug>_agent``
# attaches to its WireSubjectAgent.  See ``build_subject_workflow_handlers``.

StudyPlanFn = Callable[["StudyPlanContext"], Awaitable[dict[str, Any]]]
ExamPaperFn = Callable[[str], Awaitable[dict[str, Any]]]
MarkingSchemeFn = Callable[[str], Awaitable[dict[str, Any]]]


@dataclass(frozen=True)
class StudyPlanContext:
    """Inputs to the study-plan handler.

    Attributes:
        level: One of ``"jc"``, ``"lc_fl"``, ``"lc_ol"``, ``"lc_hl"``.
        language: ``"en"`` (canonical) or ``"ga"`` (canonical for Gaeilge).
        topic: Free-text topic seed (e.g. ``"differentiation"``); empty
            string means "general syllabus walk".
        weeks: Number of weeks to plan for (default 12).
        target_date: Optional ISO date string when the student wants to
            have finished (e.g. ``"2026-06-05"`` for the LC exam).
        completed_los: Optional list of already-mastered NCCA LO codes.
        student_id: Optional student identifier (lets downstream traces
            tag per-student progress).
    """

    level: str = "lc_hl"
    language: str = "en"
    topic: str = ""
    weeks: int = 12
    target_date: str = ""
    completed_los: tuple[str, ...] = ()
    student_id: str = ""


@dataclass(frozen=True)
class SubjectWorkflowHandlers:
    """The 3 per-subject workflow handlers returned by the factory.

    All three are bound to the per-subject wiring + tool callables and
    are attached to ``<slug>_agent_wire.study_plan_handler`` etc. via
    :func:`dataclasses.replace` on the :class:`WireSubjectAgent`.
    """

    study_plan: StudyPlanFn
    exam_paper: ExamPaperFn
    marking_scheme: MarkingSchemeFn


# ---------------------------------------------------------------------------
# Tool refs — a typed callable alias for each of the 5 per-subject tool
# functions the handlers delegate to.  We intentionally use ``Callable``
# rather than the typed async functions so each subject's slightly
# different tool signatures (e.g. ``chem_response_score_tool`` takes
# ``response_format="text"`` while ``comp_response_score_tool`` takes
# ``response_format="code"``) still resolve at call-time without
# ``mypy --strict`` complaining.
# ---------------------------------------------------------------------------


ToolRef = Callable[..., Awaitable[Any]]


# ---------------------------------------------------------------------------
# The 3 handlers — generic across subjects, parameterised by the wiring
# + tool refs.  Each handler returns a plain ``dict`` (matching the
# existing tool return convention) so CopilotKit + AG-UI can serialise
# the response directly.
# ---------------------------------------------------------------------------


async def make_study_plan(
    wiring: SubjectAgentWiring,
    syllabus_lookup_fn: ToolRef,
    formative_item_fn: ToolRef,
    ctx: StudyPlanContext,
) -> dict[str, Any]:
    """Produce a per-subject study plan.

    1. Call ``syllabus_lookup_fn`` to fetch NCCA LOs for the level/topic.
    2. For each week (up to ``ctx.weeks``), pick an LO and call
       ``formative_item_fn`` (which under-the-hood calls BAML
       ``Generate<Prefix>FormativeItem``) to generate a single
       per-subject practice item.
    3. Emit a flat ``lectionary`` list with per-week entries + a
       ``progress`` summary that downstream marimo notebooks + RAGAS
       evals can read.

    Graceful: when a tool raises we catch + emit an error entry so the
    caller still gets a plan (with degraded items rather than a
    hard failure).
    """
    level = ctx.level or "lc_hl"
    language = ctx.language or "en"
    weeks = max(1, min(int(ctx.weeks or 12), 52))
    topic = ctx.topic or ""

    try:
        los = await syllabus_lookup_fn(topic=topic, level=level, language=language)
    except Exception as exc:  # noqa: BLE001
        los = []

    completed = set(ctx.completed_los or ())

    lectionary: list[LectionaryEntry] = []
    for week_idx in range(weeks):
        if los:
            lo = los[week_idx % len(los)]
            lo_code = lo.get("lo_code") or f"LC-{wiring.baml_prefix.upper()}-LO-{week_idx + 1}.1"
        else:
            lo = {}
            lo_code = f"LC-{wiring.baml_prefix.upper()}-LO-{week_idx + 1}.1"
        difficulty = max(1, min((week_idx // 2) + 1, 5))
        try:
            item = await formative_item_fn(
                lo_code=lo_code,
                difficulty=difficulty,
                level=level,
                topic=topic,
            )
        except Exception as exc:  # noqa: BLE001
            item = {"lo_code": lo_code, "error": f"item generation failed: {exc}"}
        lectionary.append(
            {
                "week": week_idx + 1,
                "lo_code": lo_code,
                "topic": topic or (lo.get("topic") if isinstance(lo, dict) else ""),
                "difficulty": difficulty,
                "formative_item": item,
                "completed": lo_code in completed,
            }
        )

    return {
        "subject": wiring.ncca_subject,
        "level": level,
        "language": language,
        "weeks": weeks,
        "target_date": ctx.target_date,
        "student_id": ctx.student_id,
        "lectionary": lectionary,
        "progress": {
            "completed_los": sorted(completed),
            "remaining_los": sorted(
                {entry["lo_code"] for entry in lectionary} - completed
            ),
            "weeks_planned": weeks,
            "agent": wiring.langfuse_trace_name,
            "cognee_dataset": wiring.cognee_dataset,
        },
    }


async def discuss_exam_paper(
    wiring: SubjectAgentWiring,
    syllabus_lookup_fn: ToolRef,
    past_paper_lookup_fn: ToolRef,
    marking_scheme_lookup_fn: ToolRef,
    formative_item_fn: ToolRef,
    exam_paper_id: str,
) -> dict[str, Any]:
    """Discuss a past exam paper by id.

    1. Call ``past_paper_lookup_fn`` and pick items whose ``item_id``
       begins with ``exam_paper_id`` (canonical `<subject>.paperN.loNN`
       naming).
    2. For each matched item pull the matching marking scheme.
    3. Generate a per-LO practice item via ``formative_item_fn``.
    4. Emit the flat discussion dict with the items + marking-scheme
       crosswalk + a top-level ``analysis`` summary.
    """
    level = "lc_hl"
    try:
        items = await past_paper_lookup_fn(topic="", level=level, year=None)
    except Exception:
        items = []

    paper_items: list[dict[str, Any]] = []
    if isinstance(items, list):
        for it in items:
            if not isinstance(it, dict):
                continue
            iid = it.get("item_id") or ""
            if iid.startswith(exam_paper_id):
                paper_items.append(it)
                if len(paper_items) >= 10:
                    break

    per_lo_ms: list[dict[str, Any]] = []
    generated: list[dict[str, Any]] = []
    for it in paper_items or [
        {"lo_code": f"LC-{wiring.baml_prefix.upper()}-LO-2.4"}
    ]:
        lo_code = it.get("lo_code") or ""
        if not lo_code:
            continue
        try:
            ms = await marking_scheme_lookup_fn(lo_code=lo_code)
            if isinstance(ms, dict) and not ms.get("error"):
                per_lo_ms.append({"lo_code": lo_code, "marking_scheme": ms})
        except Exception:
            pass
        if len(generated) < 3:
            try:
                gen = await formative_item_fn(
                    lo_code=lo_code,
                    difficulty=3,
                    level=level,
                    topic="",
                )
                generated.append({"lo_code": lo_code, "formative_item": gen})
            except Exception as exc:  # noqa: BLE001
                generated.append(
                    {"lo_code": lo_code, "error": f"item generation failed: {exc}"}
                )

    return {
        "subject": wiring.ncca_subject,
        "level": level,
        "exam_paper_id": exam_paper_id,
        "items": paper_items,
        "marking_schemes": per_lo_ms,
        "analysis": {
            "items_discussed": len(paper_items),
            "marking_schemes_crosswalked": len(per_lo_ms),
            "formative_items_for_practice": generated,
            "agent": wiring.langfuse_trace_name,
        },
    }


async def explain_marking_scheme(
    wiring: SubjectAgentWiring,
    past_paper_lookup_fn: ToolRef,
    marking_scheme_lookup_fn: ToolRef,
    formative_item_fn: ToolRef,
    response_score_fn: ToolRef,
    marking_scheme_id: str,
) -> dict[str, Any]:
    """Explain a per-subject marking scheme + produce an exemplar.

    1. Call ``marking_scheme_lookup_fn`` for the canonical scheme text.
    2. Look up related past-paper items (``past_paper_lookup_fn``).
    3. Generate an exemplar practice item via ``formative_item_fn``.
    4. Optionally score a sample response via ``response_score_fn``.
    5. Emit a per-subject explanation dict with the rationale text
       (English canonical + Irish secondary), the exemplar + score.
    """
    try:
        scheme = await marking_scheme_lookup_fn(lo_code=marking_scheme_id)
    except Exception as exc:  # noqa: BLE001
        scheme = {"lo_code": marking_scheme_id, "error": f"lookup failed: {exc}"}

    try:
        related = await past_paper_lookup_fn(
            topic=marking_scheme_id, level="lc_hl", year=None
        )
    except Exception:
        related = []

    try:
        exemplar = await formative_item_fn(
            lo_code=marking_scheme_id,
            difficulty=4,
            level="lc_hl",
            topic=marking_scheme_id,
        )
    except Exception as exc:  # noqa: BLE001
        exemplar = {"lo_code": marking_scheme_id, "error": f"item generation failed: {exc}"}

    score: dict[str, Any] | None = None
    if (
        isinstance(exemplar, dict)
        and not exemplar.get("error")
        and exemplar.get("expected_answer_en")
    ):
        try:
            score = await response_score_fn(
                item_id=exemplar.get("id", ""),
                student_response=exemplar.get("expected_answer_en", ""),
                response_format="text",
                time_taken_seconds=0,
                hints_used=0,
            )
        except Exception:
            score = None

    rationale = {
        "lo_code": marking_scheme_id,
        "explanation_en": (
            f"For {marking_scheme_id}, the marking scheme rewards "
            "step-by-step reasoning and explicit notation. Each "
            "logical step in the chain earns independent marks; "
            "common errors lose one mark per slip unless the student "
            "recovers in a later step."
        ),
        "explanation_ga": (
            f"Maidir le {marking_scheme_id}, tugann an scéim mharcanna "
            "luach saothair do réasúnaíocht céim ar chéim agus do nodaireacht "
            "shonrach. G céim loighciúil sa slabhra tuilleann marcanna "
            "neamhspleácha."
        ),
        "language_primary": "en",
        "language_secondary": "ga",
    }

    return {
        "subject": wiring.ncca_subject,
        "marking_scheme_id": marking_scheme_id,
        "scheme": scheme,
        "rationale": rationale,
        "exemplar_formative_item": exemplar,
        "exemplar_score": score,
        "related_past_paper_items": related[:5] if isinstance(related, list) else [],
        "agent": wiring.langfuse_trace_name,
        "cognee_dataset": wiring.cognee_dataset,
    }


# ---------------------------------------------------------------------------
# The factory the 6 ``<slug>_agent.py`` modules call once at the bottom.
# ---------------------------------------------------------------------------


def build_subject_workflow_handlers(
    wiring: SubjectAgentWiring,
    syllabus_lookup_fn: ToolRef,
    past_paper_lookup_fn: ToolRef,
    marking_scheme_lookup_fn: ToolRef,
    formative_item_fn: ToolRef,
    response_score_fn: ToolRef,
) -> SubjectWorkflowHandlers:
    """Bind the 3 per-subject workflow handlers to the wiring + tool refs.

    Returns a ``SubjectWorkflowHandlers`` whose 3 async callables the
    agent module attaches to its ``WireSubjectAgent`` via the
    :func:`attach_subject_workflow_handlers` helper (or directly via
    :func:`dataclasses.replace`).
    """

    async def _study_plan(ctx: StudyPlanContext) -> dict[str, Any]:
        return await make_study_plan(
            wiring,
            syllabus_lookup_fn,
            formative_item_fn,
            ctx,
        )

    async def _exam_paper(exam_paper_id: str) -> dict[str, Any]:
        return await discuss_exam_paper(
            wiring,
            syllabus_lookup_fn,
            past_paper_lookup_fn,
            marking_scheme_lookup_fn,
            formative_item_fn,
            exam_paper_id,
        )

    async def _marking_scheme(marking_scheme_id: str) -> dict[str, Any]:
        return await explain_marking_scheme(
            wiring,
            past_paper_lookup_fn,
            marking_scheme_lookup_fn,
            formative_item_fn,
            response_score_fn,
            marking_scheme_id,
        )

    return SubjectWorkflowHandlers(
        study_plan=_study_plan,
        exam_paper=_exam_paper,
        marking_scheme=_marking_scheme,
    )


def attach_subject_workflow_handlers(
    wire: WireSubjectAgent,
    handlers: SubjectWorkflowHandlers,
) -> WireSubjectAgent:
    """Return a new :class:`WireSubjectAgent` with the 3 handlers attached.

    Mutating a frozen-dataclass-equivalent via :func:`dataclasses.replace`
    preserves back-compat with any existing reader that holds the
    original ``wire`` object (the original is left untouched).
    """
    return replace(
        wire,
        study_plan_handler=handlers.study_plan,
        exam_paper_handler=handlers.exam_paper,
        marking_scheme_handler=handlers.marking_scheme,
    )


__all__ = [
    "LectionaryEntry",
    "MarkingSchemeFn",
    "ExamPaperFn",
    "StudyPlanContext",
    "StudyPlanFn",
    "SubjectWorkflowHandlers",
    "ToolRef",
    "attach_subject_workflow_handlers",
    "build_subject_workflow_handlers",
    "discuss_exam_paper",
    "explain_marking_scheme",
    "make_study_plan",
]
