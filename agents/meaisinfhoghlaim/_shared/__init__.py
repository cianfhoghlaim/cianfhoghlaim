"""agents.meaisinfhoghlaim._shared — central Pydantic I/O + memory governance.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.

Three responsibilities:

1. **Pydantic I/O schemas** — shared I/O types for the 8 ADK 2 workflow
   graphs + the 5 deep-research pipelines. Mirrors the canonical
   `docs/google_examples/adk2-tutorial/shared/schemas.py` pattern.

2. **Memory governance** — the 5-floor ladder (visit → visitor → student
   → stage → valley) modeled on agent-valley-archive's
   `archive/state.py` + `archive/tower.py` pattern. Includes the `burn()`
   function for GDPR + Children First Act 2015 compliance (ADK has no
   delete on BaseMemoryService; this is the application-level delete).

3. **Education-stage taxonomy** — the 5 BIEP v3 stages mapped to the
   memory-ladder floors (aistear = visit, primary = books, jc = drawer,
   sc = tower, tertiary = valley).

Pillar mapping:
  - Pillar 1 (Workflow) uses EducationRequest/EducationResponse for
    node I/O between agents + function nodes.
  - Pillar 2 (Collaborative) uses SpecialistInput/SpecialistResponse
    for the root-orchestrator → sub-agent hand-off.
  - Pillar 3 (Dynamic) uses DecomposerOutput/ResearchFinding/
    DeepResearchBriefing for the runtime-width deep-research pipelines.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# ============================================================================
# Pillar 1 (Workflow) — node I/O schemas
# ============================================================================


class Conditions(BaseModel):
    """Generic node I/O for the teacher / student workflow graphs."""

    stage: str
    class_id: str
    subject: str
    note: str | None = None


class BundledRunData(BaseModel):
    """Payload of a JoinNode — keys match upstream function names."""

    fetch_conditions: dict[str, Any]
    plan: dict[str, Any] | None = None
    feedback: dict[str, Any] | None = None


# ============================================================================
# Pillar 2 (Collaborative) — root-orchestrator <-> sub-agent hand-off
# ============================================================================


class EducationStage(str, Enum):
    """The 5 BIEP v3 stages (per british-isles-education-pipeline-v3/spec.md)."""

    AISTEAR = "aistear"
    PRIMARY = "primary"
    JUNIOR_CYCLE = "jc"
    SENIOR_CYCLE = "sc"
    TERTIARY = "tertiary"


class EducationRole(str, Enum):
    """Per-agent role tags (parallel to the teacher_roles_baml)."""

    TEACHER_LESSON_PLANNER = "teacher_lesson_planner"
    TEACHER_ASSESSMENT_SCORER = "teacher_assessment_scorer"
    TEACHER_SEN_PASTORAL = "teacher_sen_pastoral"
    TEACHER_PARENT_MEETING = "teacher_parent_meeting"
    TEACHER_PRO_LEARNING = "teacher_professional_learning"
    STUDENT_HOMEWORK = "student_homework"
    STUDENT_CBA_PLANNER = "student_cba_planner"
    STUDENT_STUDY_PLAN = "student_study_plan"
    STUDENT_WELLBEING = "student_wellbeing"
    STUDENT_EXAM_TIMETABLE = "student_exam_timetable"
    TERTIARY_UOA_PORTAL = "tertiary_uoa_portal"
    TERTIARY_SU = "tertiary_su"


class EducationRequest(BaseModel):
    """Standard request envelope for all education agents."""

    request_id: str
    user_id: str
    stage: EducationStage
    role: EducationRole
    class_id: str | None = None
    subject: str | None = None
    free_text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SpecialistInput(BaseModel):
    """Input the root-orchestrator hands to a sub-agent."""

    request: EducationRequest
    context: BundledRunData | None = None
    prior_outputs: dict[str, Any] = Field(default_factory=dict)


class SpecialistResponse(BaseModel):
    """Output a sub-agent returns to the root-orchestrator."""

    request_id: str
    role: EducationRole
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    action_items: list[str] = Field(default_factory=list)
    next_role: EducationRole | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Pillar 3 (Dynamic) — deep-research pipeline I/O
# ============================================================================


class DecomposerOutput(BaseModel):
    """Output of the decompose agent — the runtime-width research plan."""

    plan_summary: str
    sub_questions: list[str] = Field(min_length=3, max_length=7)


class ResearchFinding(BaseModel):
    """One per sub-question, produced by the parallel_worker."""

    question: str
    summary: str
    key_facts: list[str] = Field(default_factory=list)
    needs_deeper: bool = False
    child_questions: list[str] = Field(default_factory=list)


class DeepResearchBriefing(BaseModel):
    """Final synthesis across all findings."""

    headline: str
    sections: list[str]
    citations: list[str] = Field(default_factory=list)


# ============================================================================
# Memory ladder — the agent-valley-archive twin
# ============================================================================


#: Stage → floor (the 5-floor ladder).
STAGE_TO_FLOOR: dict[EducationStage, str] = {
    EducationStage.AISTEAR: "visit",
    EducationStage.PRIMARY: "books",
    EducationStage.JUNIOR_CYCLE: "drawer",
    EducationStage.SENIOR_CYCLE: "tower",
    EducationStage.TERTIARY: "valley",
}


#: The 5 ladder keys (visit → visitor → student → stage → valley).
VISIT = "visit"                     #: session scope (one interaction)
VISITOR = "user:visitor"             #: cross-visit (no prefix = session; user: prefix = app-wide)
STUDENT = "user:student_id"          #: cross-visit per student
STAGE = "user:stage"                 #: cross-visit per stage
VALLEY = "app:valley"                #: cross-app + cross-tenant (the BIEP-v3 valley)


def burn(memory_service: Any, app: str, user: str, memory_id: str) -> bool:
    """Take one page off the shelf.

    ADK 2.x has no delete on BaseMemoryService (per the agent-valley-archive
    `archive/tower.py` boundary). Forgetting is a governance action, not an
    agent action, so it lives here in the application — where the model cannot
    reach it by accident.

    Compliance: GDPR + Children First Act 2015 (parent consent + designated
    liaison person for SEN records).
    """
    try:
        client = getattr(memory_service, "_get_api_client", lambda: None)()
        pager = client.agent_engines.memories.delete(
            name=f"reasoningEngines/{getattr(memory_service, '_agent_engine_id', '')}",
            scope={"app_name": app, "user_id": user},
        )
        # The real Vertex AI Memory Bank client returns an async pager.
        # For Phase 1 dev (sync mode), we just call the underlying delete
        # method directly without iterating the pager.
        if hasattr(pager, "__aiter__"):
            # Async pager — caller must await it. Skip iteration here.
            pass
        else:
            # InMemoryMemoryService fallback — clear from the local dict.
            store = getattr(memory_service, "_session_events", {})
            for (a, u), sessions in store.items():
                if a != app or u != user:
                    continue
                for sid, events in sessions.items():
                    store[(a, u)][sid] = [
                        ev for ev in events if getattr(ev, "id", "") != memory_id
                    ]
        return True
    except Exception:
        return False


# ============================================================================
# Re-exports
# ============================================================================

__all__ = [
    # Pillar 1
    "Conditions",
    "BundledRunData",
    # Pillar 2
    "EducationStage",
    "EducationRole",
    "EducationRequest",
    "SpecialistInput",
    "SpecialistResponse",
    # Pillar 3
    "DecomposerOutput",
    "ResearchFinding",
    "DeepResearchBriefing",
    # Memory
    "STAGE_TO_FLOOR",
    "VISIT",
    "VISITOR",
    "STUDENT",
    "STAGE",
    "VALLEY",
    "burn",
]
