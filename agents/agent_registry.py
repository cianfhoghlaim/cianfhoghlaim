"""Agent fleet registry.

The single source of truth for the 14 main agents in the
Cianfhoghlaim agent fleet. The 8 NCCA subject agents are
re-exported through ``agents/tuatha/wiring.py`` for back-compat.

The 14 main agents are:

- ``root_agent`` (Custom) — the query router + orchestrator
- ``curriculum_agent`` (ADK) — 5-nation curriculum search
- ``translation_agent`` (ADK) — 6-Celtic-language translation
- ``corpus_agent`` (ADK) — Dúchas + Gaois + UD + Canúint + Téarma
- ``research_agent`` (ADK) — long-form research + citations
- ``education_research_agent`` (Agno) — cross-nation policy research
- ``bunchloch_research_agent`` (Agno) — M4 MacBook-local research
- ``geospatial_agent`` (ADK) — LSOA / Data Zone spatial analysis
- ``statistics_agent`` (ADK) — education metrics + benchmarking
- ``curriculum_comparison_agent`` (ADK) — cross-nation mapping
- ``agui_curriculum_agent`` (Agno) — AG-UI streaming (CopilotKit consumer)
- ``mcp_curriculum_agent`` (ADK) — MCP-server-bridged curriculum agent
- ``image_generation_agent`` (ADK) — consumes the 5 ``image_gen``
  MODEL_REGISTRY entries for 2D assets + Babylon.js textures
- ``students_union_root_agent`` (ADK) — UoG Students' Union root
  orchestrator + 5 SU specialists (moved from ciandlithe per the
  ``2026-09-23-consolidate-uog-tertiary-pipeline-v1`` change)

Reference: openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1.
Extended by openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/
(Phase L — image_generation_agent).
Extended by openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/
(13th→14th specialist — students_union_root_agent).
"""
from __future__ import annotations

import logging
from typing import Any

from .wiring import AgentFleetWiring, AgentFramework

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# The 13-agent fleet registry.
# ---------------------------------------------------------------------------


AGENT_REGISTRY: dict[str, AgentFleetWiring] = {
    "root_agent": AgentFleetWiring(
        agent_name="root_agent",
        module_slug="cian_root",
        module_path="cianfhoghlaim.agents.adk.cian_root_agent",
        # Per the openspec change
        # `2026-09-06-adk-gemini-deep-research-control-plane-v1`,
        # the root_agent is now an ADK `SequentialAgent` named
        # `cian_root` (replacing the prior Custom LiteLLM router).
        # The legacy `agents.adk.root_agent` module remains for
        # back-compat (imported by `enhanced_orchestrator.py` +
        # `curriculum_agent.py`); new code SHOULD import from
        # `agents.adk.cian_root_agent` instead.
        framework=AgentFramework.ADK,
        display_name="Cian Root Agent (ADK)",
        baml_prefix="Root",
        langfuse_trace_name="agent.root.route",
        cognee_dataset="oideachais_root",
        letta_agent_id="kcg-root-agent",
        litellm_routing_key="router",
    ),
    "curriculum_agent": AgentFleetWiring(
        agent_name="curriculum_agent",
        module_slug="curriculum",
        module_path="cianfhoghlaim.agents.adk.curriculum_agent",
        framework=AgentFramework.ADK,
        display_name="Curriculum Agent",
        baml_prefix="Curr",
        langfuse_trace_name="agent.curriculum.search",
        cognee_dataset="oideachais_curriculum",
        letta_agent_id="kcg-curriculum-agent",
        litellm_routing_key="curriculum",
    ),
    "translation_agent": AgentFleetWiring(
        agent_name="translation_agent",
        module_slug="translation",
        module_path="cianfhoghlaim.agents.adk.translation_agent",
        framework=AgentFramework.ADK,
        display_name="Translation Agent",
        baml_prefix="Trans",
        langfuse_trace_name="agent.translation.translate",
        cognee_dataset="oideachais_translation",
        letta_agent_id="kcg-translation-agent",
        litellm_routing_key="translation",
    ),
    "corpus_agent": AgentFleetWiring(
        agent_name="corpus_agent",
        module_slug="corpus",
        module_path="cianfhoghlaim.agents.adk.corpus_agent",
        framework=AgentFramework.ADK,
        display_name="Corpus Agent",
        baml_prefix="Corp",
        langfuse_trace_name="agent.corpus.search",
        cognee_dataset="oideachais_corpus",
        letta_agent_id="kcg-corpus-agent",
        litellm_routing_key="corpus",
    ),
    "research_agent": AgentFleetWiring(
        agent_name="research_agent",
        module_slug="research",
        module_path="cianfhoghlaim.agents.adk.research_agent",
        framework=AgentFramework.ADK,
        display_name="Research Agent",
        baml_prefix="Res",
        langfuse_trace_name="agent.research.deep",
        cognee_dataset="oideachais_research",
        letta_agent_id="kcg-research-agent",
        litellm_routing_key="research",
    ),
    "education_research_agent": AgentFleetWiring(
        agent_name="education_research_agent",
        module_slug="education_research",
        module_path="cianfhoghlaim.agents.agno.education_team",
        framework=AgentFramework.AGNO,
        display_name="Education Research Agent",
        baml_prefix="EduRes",
        langfuse_trace_name="agent.education_research.policy",
        cognee_dataset="oideachais_education_research",
        letta_agent_id="kcg-education-research-agent",
        litellm_routing_key="education_research",
    ),
    "bunchloch_research_agent": AgentFleetWiring(
        agent_name="bunchloch_research_agent",
        module_slug="bunchloch_research",
        module_path="cianfhoghlaim.agents.agno.education_team",
        framework=AgentFramework.AGNO,
        display_name="Bunchloch Research Agent",
        baml_prefix="BunchRes",
        langfuse_trace_name="agent.bunchloch_research.local",
        cognee_dataset="oideachais_bunchloch_research",
        letta_agent_id="kcg-bunchloch-research-agent",
        litellm_routing_key="bunchloch_research",
    ),
    "geospatial_agent": AgentFleetWiring(
        agent_name="geospatial_agent",
        module_slug="geospatial",
        module_path="cianfhoghlaim.agents.adk.geospatial_agent",
        framework=AgentFramework.ADK,
        display_name="Geospatial Agent",
        baml_prefix="Geo",
        langfuse_trace_name="agent.geospatial.spatial",
        cognee_dataset="oideachais_geospatial",
        letta_agent_id="kcg-geospatial-agent",
        litellm_routing_key="geospatial",
    ),
    "statistics_agent": AgentFleetWiring(
        agent_name="statistics_agent",
        module_slug="statistics",
        module_path="cianfhoghlaim.agents.adk.statistics_agent",
        framework=AgentFramework.ADK,
        display_name="Statistics Agent",
        baml_prefix="Stat",
        langfuse_trace_name="agent.statistics.benchmark",
        cognee_dataset="oideachais_statistics",
        letta_agent_id="kcg-statistics-agent",
        litellm_routing_key="statistics",
    ),
    "curriculum_comparison_agent": AgentFleetWiring(
        agent_name="curriculum_comparison_agent",
        module_slug="curriculum_comparison",
        module_path="cianfhoghlaim.agents.adk.curriculum_comparison_agent",
        framework=AgentFramework.ADK,
        display_name="Curriculum Comparison Agent",
        baml_prefix="CurrComp",
        langfuse_trace_name="agent.curriculum_comparison.map",
        cognee_dataset="oideachais_curriculum_comparison",
        letta_agent_id="kcg-curriculum-comparison-agent",
        litellm_routing_key="curriculum_comparison",
    ),
    "agui_curriculum_agent": AgentFleetWiring(
        agent_name="agui_curriculum_agent",
        module_slug="agui_curriculum",
        module_path="cianfhoghlaim.agents.adk.agui_curriculum_agent",
        framework=AgentFramework.AGNO,
        display_name="AG-UI Curriculum Agent",
        baml_prefix="AGUICurr",
        langfuse_trace_name="agent.agui_curriculum.stream",
        cognee_dataset="oideachais_agui_curriculum",
        letta_agent_id="kcg-agui-curriculum-agent",
        litellm_routing_key="agui_curriculum",
    ),
    "mcp_curriculum_agent": AgentFleetWiring(
        agent_name="mcp_curriculum_agent",
        module_slug="mcp_curriculum",
        module_path="cianfhoghlaim.agents.adk.mcp_curriculum_agent",
        framework=AgentFramework.ADK,
        display_name="MCP Curriculum Agent",
        baml_prefix="MCPCurr",
        langfuse_trace_name="agent.mcp_curriculum.bridge",
        cognee_dataset="oideachais_mcp_curriculum",
        letta_agent_id="kcg-mcp-curriculum-agent",
        litellm_routing_key="mcp_curriculum",
    ),
    # ---------------------------------------------------------------------
    # Image generation agent (per 2026-08-13-web-monorepo-
    # consolidation-and-agent-integration-v1, Phase L)
    # ---------------------------------------------------------------------
    "image_generation_agent": AgentFleetWiring(
        agent_name="image_generation_agent",
        module_slug="image_generation",
        module_path="cianfhoghlaim.agents.adk.image_generation_agent",
        framework=AgentFramework.ADK,
        display_name="Image Generation Agent",
        baml_prefix="ImageGen",
        langfuse_trace_name="agent.image_generation.generate",
        cognee_dataset="oideachais_image_generation",
        letta_agent_id="kcg-image-generation-agent",
        litellm_routing_key="image_generation",
    ),
    # ---------------------------------------------------------------------
    # Students' Union root orchestrator (per 2026-09-23-consolidate-
    # uog-tertiary-pipeline-v1) — moved from ciandlithe; the 13th→14th
    # specialist in the 12-agent fleet
    # ---------------------------------------------------------------------
    "students_union_root_agent": AgentFleetWiring(
        agent_name="students_union_root_agent",
        module_slug="students_union",
        module_path="cianfhoghlaim.agents.meaisinfhoghlaim.educational.students_union.root_agent",
        framework=AgentFramework.ADK,
        display_name="Students' Union Root Agent (UoG)",
        baml_prefix="SU",
        langfuse_trace_name="agent.students_union.route",
        cognee_dataset="oideachais_students_union",
        letta_agent_id="kcg-students-union-agent",
        litellm_routing_key="students_union",
    ),
    # ---------------------------------------------------------------------
    # K-12 Teacher Agents (per 2026-09-23-k12-teacher-student-pipeline-v1).
    # The fleet grows 14 → 24 with 5 teacher + 5 student specialists.
    # ---------------------------------------------------------------------
    "lesson_planner_agent": AgentFleetWiring(
        agent_name="lesson_planner_agent",
        module_slug="lesson_planner",
        module_path="cianfhoghlaim.agents.meaisinfhoghlaim.educational.teachers.lesson_planner_agent",
        framework=AgentFramework.ADK,
        display_name="Lesson Planner Agent (K-12)",
        baml_prefix="LP",
        langfuse_trace_name="agent.lesson_planner.generate",
        cognee_dataset="oideachais_k12_lesson_plans",
        letta_agent_id="kcg-lesson-planner-agent",
        litellm_routing_key="lesson_planner",
    ),
    "assessment_scorer_agent": AgentFleetWiring(
        agent_name="assessment_scorer_agent",
        module_slug="assessment_scorer",
        module_path="cianfhoghlaim.agents.meaisinfhoghlaim.educational.teachers.assessment_scorer_agent",
        framework=AgentFramework.ADK,
        display_name="Assessment Scorer Agent (K-12)",
        baml_prefix="Score",
        langfuse_trace_name="agent.assessment_scorer.score",
        cognee_dataset="oideachais_k12_assessments",
        letta_agent_id="kcg-assessment-scorer-agent",
        litellm_routing_key="assessment_scorer",
    ),
    "sen_pastoral_care_agent": AgentFleetWiring(
        agent_name="sen_pastoral_care_agent",
        module_slug="sen_pastoral_care",
        module_path="cianfhoghlaim.agents.meaisinfhoghlaim.educational.teachers.sen_pastoral_care_agent",
        framework=AgentFramework.ADK,
        display_name="SEN + Pastoral Care Agent (K-12)",
        baml_prefix="SEN",
        langfuse_trace_name="agent.sen_pastoral.coordinate",
        cognee_dataset="oideachais_k12_sen_records",
        letta_agent_id="kcg-sen-pastoral-agent",
        litellm_routing_key="sen_pastoral_care",
    ),
    "parent_meeting_agent": AgentFleetWiring(
        agent_name="parent_meeting_agent",
        module_slug="parent_meeting",
        module_path="cianfhoghlaim.agents.meaisinfhoghlaim.educational.teachers.parent_meeting_agent",
        framework=AgentFramework.ADK,
        display_name="Parent Meeting Prep Agent (K-12)",
        baml_prefix="Parent",
        langfuse_trace_name="agent.parent_meeting.prepare",
        cognee_dataset="oideachais_k12_parent_meetings",
        letta_agent_id="kcg-parent-meeting-agent",
        litellm_routing_key="parent_meeting",
    ),
    "professional_learning_agent": AgentFleetWiring(
        agent_name="professional_learning_agent",
        module_slug="professional_learning",
        module_path="cianfhoghlaim.agents.meaisinfhoghlaim.educational.teachers.professional_learning_agent",
        framework=AgentFramework.ADK,
        display_name="Professional Learning Agent (OIDE/PDST Recommender)",
        baml_prefix="PD",
        langfuse_trace_name="agent.professional_learning.recommend",
        cognee_dataset="oideachais_k12_professional_learning",
        letta_agent_id="kcg-professional-learning-agent",
        litellm_routing_key="professional_learning",
    ),
    # ---------------------------------------------------------------------
    # K-12 Student Agents (per 2026-09-23-k12-teacher-student-pipeline-v1).
    # Post-primary only (JC + LC + TY + LCA).
    # ---------------------------------------------------------------------
    "homework_tracker_agent": AgentFleetWiring(
        agent_name="homework_tracker_agent",
        module_slug="homework_tracker",
        module_path="cianfhoghlaim.agents.meaisinfhoghlaim.educational.students_jc.homework_tracker_agent",
        framework=AgentFramework.ADK,
        display_name="Homework Tracker Agent (JC + LC Student)",
        baml_prefix="HW",
        langfuse_trace_name="agent.homework.track",
        cognee_dataset="oideachais_k12_homework",
        letta_agent_id="kcg-homework-tracker-agent",
        litellm_routing_key="homework_tracker",
    ),
    "cba_planner_agent": AgentFleetWiring(
        agent_name="cba_planner_agent",
        module_slug="cba_planner",
        module_path="cianfhoghlaim.agents.meaisinfhoghlaim.educational.students_jc.cba_planner_agent",
        framework=AgentFramework.ADK,
        display_name="CBA Planner Agent (JC Student)",
        baml_prefix="CBA",
        langfuse_trace_name="agent.cba_planner.plan",
        cognee_dataset="oideachais_k12_cbas",
        letta_agent_id="kcg-cba-planner-agent",
        litellm_routing_key="cba_planner",
    ),
    "study_plan_agent": AgentFleetWiring(
        agent_name="study_plan_agent",
        module_slug="study_plan",
        module_path="cianfhoghlaim.agents.meaisinfhoghlaim.educational.students_jc.study_plan_agent",
        framework=AgentFramework.ADK,
        display_name="Study Plan Agent (LC + TY Student)",
        baml_prefix="SP",
        langfuse_trace_name="agent.study_plan.build",
        cognee_dataset="oideachais_k12_study_plans",
        letta_agent_id="kcg-study-plan-agent",
        litellm_routing_key="study_plan",
    ),
    "wellbeing_agent": AgentFleetWiring(
        agent_name="wellbeing_agent",
        module_slug="wellbeing",
        module_path="cianfhoghlaim.agents.meaisinfhoghlaim.educational.students_jc.wellbeing_agent",
        framework=AgentFramework.ADK,
        display_name="Wellbeing Check-in Agent (K-12 Student)",
        baml_prefix="WB",
        langfuse_trace_name="agent.wellbeing.checkin",
        cognee_dataset="oideachais_k12_wellbeing",
        letta_agent_id="kcg-wellbeing-agent",
        litellm_routing_key="wellbeing",
    ),
    "exam_timetable_agent": AgentFleetWiring(
        agent_name="exam_timetable_agent",
        module_slug="exam_timetable",
        module_path="cianfhoghlaim.agents.meaisinfhoghlaim.educational.students_jc.exam_timetable_agent",
        framework=AgentFramework.ADK,
        display_name="Exam Timetable Agent (JC + LC Student)",
        baml_prefix="ExamTT",
        langfuse_trace_name="agent.exam_timetable.surface",
        cognee_dataset="oideachais_k12_exam_timetables",
        letta_agent_id="kcg-exam-timetable-agent",
        litellm_routing_key="exam_timetable",
    ),
    # ---------------------------------------------------------------------
    # K-12 Root Orchestrators (per 2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1).
    # ADK 2 Pillar-2 collaborative mode (`sub_agents` + `mode="single_turn"`).
    # ---------------------------------------------------------------------
    "teacher_root": AgentFleetWiring(
        agent_name="teacher_root",
        module_slug="teacher_root",
        module_path="cianfhoghlaim.agents.meaisinfhoghlaim.educational.teachers._root",
        framework=AgentFramework.ADK,
        display_name="K-12 Teacher Root Orchestrator (Pillar 2 collaborative)",
        baml_prefix="TeacherRoot",
        langfuse_trace_name="agent.teacher_root.fanout",
        cognee_dataset="oideachais_k12_teacher_root",
        letta_agent_id="kcg-teacher-root-agent",
        litellm_routing_key="teacher_root",
    ),
    "student_root": AgentFleetWiring(
        agent_name="student_root",
        module_slug="student_root",
        module_path="cianfhoghlaim.agents.meaisinfhoghlaim.educational.students_jc._root",
        framework=AgentFramework.ADK,
        display_name="K-12 Student Root Orchestrator (Pillar 2 collaborative)",
        baml_prefix="StudentRoot",
        langfuse_trace_name="agent.student_root.fanout",
        cognee_dataset="oideachais_k12_student_root",
        letta_agent_id="kcg-student-root-agent",
        litellm_routing_key="student_root",
    ),
    # ---------------------------------------------------------------------
    # ADK 2 Pillar-1 Workflow Graphs (per 2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1).
    # 3 Workflow(edges=...) graphs that explicitly route + sequence agents.
    # ---------------------------------------------------------------------
    "teacher_daily_workflow": AgentFleetWiring(
        agent_name="teacher_daily_workflow",
        module_slug="teacher_daily_workflow",
        module_path="cianfhoghlaim.agents.workflows.teacher_daily_workflow",
        framework=AgentFramework.ADK,
        display_name="Teacher Daily Workflow (Pillar 1 graph)",
        baml_prefix="TDW",
        langfuse_trace_name="workflow.teacher_daily.run",
        cognee_dataset="oideachais_k12_workflows",
        letta_agent_id="kcg-teacher-daily-workflow",
        litellm_routing_key="teacher_daily_workflow",
    ),
    "student_secondary_workflow": AgentFleetWiring(
        agent_name="student_secondary_workflow",
        module_slug="student_secondary_workflow",
        module_path="cianfhoghlaim.agents.workflows.student_secondary_workflow",
        framework=AgentFramework.ADK,
        display_name="Student Secondary Workflow (Pillar 1 graph)",
        baml_prefix="SSW",
        langfuse_trace_name="workflow.student_secondary.run",
        cognee_dataset="oideachais_k12_workflows",
        letta_agent_id="kcg-student-secondary-workflow",
        litellm_routing_key="student_secondary_workflow",
    ),
    "tertiary_personal_workflow": AgentFleetWiring(
        agent_name="tertiary_personal_workflow",
        module_slug="tertiary_personal_workflow",
        module_path="cianfhoghlaim.agents.workflows.tertiary_personal_workflow",
        framework=AgentFramework.ADK,
        display_name="Tertiary Personal Workflow (Pillar 1 graph)",
        baml_prefix="TPW",
        langfuse_trace_name="workflow.tertiary_personal.run",
        cognee_dataset="oideachais_tertiary_workflows",
        letta_agent_id="kcg-tertiary-personal-workflow",
        litellm_routing_key="tertiary_personal_workflow",
    ),
    # ---------------------------------------------------------------------
    # ADK 2 Pillar-3 Dynamic Deep-Research Pipelines (per the umbrella change).
    # 5 `@node(parallel_worker=True)` + recursive `ctx.run_node` pipelines.
    # ---------------------------------------------------------------------
    "aistear_deep_research": AgentFleetWiring(
        agent_name="aistear_deep_research",
        module_slug="aistear_deep_research",
        module_path="cianfhoghlaim.agents.workflows.aistear_deep_research",
        framework=AgentFramework.ADK,
        display_name="Aistear Deep Research (Pillar 3 dynamic)",
        baml_prefix="ADR",
        langfuse_trace_name="workflow.aistear_deep_research.run",
        cognee_dataset="oideachais_k12_workflows",
        letta_agent_id="kcg-aistear-deep-research",
        litellm_routing_key="aistear_deep_research",
    ),
    "primary_deep_research": AgentFleetWiring(
        agent_name="primary_deep_research",
        module_slug="primary_deep_research",
        module_path="cianfhoghlaim.agents.workflows.primary_deep_research",
        framework=AgentFramework.ADK,
        display_name="Primary Deep Research (Pillar 3 dynamic)",
        baml_prefix="PDR",
        langfuse_trace_name="workflow.primary_deep_research.run",
        cognee_dataset="oideachais_k12_workflows",
        letta_agent_id="kcg-primary-deep-research",
        litellm_routing_key="primary_deep_research",
    ),
    "jc_deep_research": AgentFleetWiring(
        agent_name="jc_deep_research",
        module_slug="jc_deep_research",
        module_path="cianfhoghlaim.agents.workflows.jc_deep_research",
        framework=AgentFramework.ADK,
        display_name="JC Deep Research (Pillar 3 dynamic)",
        baml_prefix="JDR",
        langfuse_trace_name="workflow.jc_deep_research.run",
        cognee_dataset="oideachais_k12_workflows",
        letta_agent_id="kcg-jc-deep-research",
        litellm_routing_key="jc_deep_research",
    ),
    "sc_deep_research": AgentFleetWiring(
        agent_name="sc_deep_research",
        module_slug="sc_deep_research",
        module_path="cianfhoghlaim.agents.workflows.sc_deep_research",
        framework=AgentFramework.ADK,
        display_name="SC Deep Research (Pillar 3 dynamic)",
        baml_prefix="SDR",
        langfuse_trace_name="workflow.sc_deep_research.run",
        cognee_dataset="oideachais_k12_workflows",
        letta_agent_id="kcg-sc-deep-research",
        litellm_routing_key="sc_deep_research",
    ),
    "tertiary_deep_research": AgentFleetWiring(
        agent_name="tertiary_deep_research",
        module_slug="tertiary_deep_research",
        module_path="cianfhoghlaim.agents.workflows.tertiary_deep_research",
        framework=AgentFramework.ADK,
        display_name="Tertiary Deep Research (Pillar 3 dynamic)",
        baml_prefix="TDR",
        langfuse_trace_name="workflow.tertiary_deep_research.run",
        cognee_dataset="oideachais_tertiary_workflows",
        letta_agent_id="kcg-tertiary-deep-research",
        litellm_routing_key="tertiary_deep_research",
    ),
}


# ---------------------------------------------------------------------------
# The 5 framework stubs (Pipecat + CopilotKit + 3 future frameworks).
# These provide slot for future work without changing the contract.
# ---------------------------------------------------------------------------


FRAMEWORK_AVAILABLE: dict[AgentFramework, bool] = {
    AgentFramework.CUSTOM: True,
    AgentFramework.ADK: True,
    AgentFramework.AGNO: True,
    AgentFramework.PIPECAT: False,  # voice channel deferred
    AgentFramework.COPILOTKIT: False,  # consumer agent deferred
}


# ---------------------------------------------------------------------------
# Convenience helpers.
# ---------------------------------------------------------------------------


def list_agent_names() -> list[str]:
    """Return the sorted list of the 14 main agent names."""
    return sorted(AGENT_REGISTRY.keys())


def get_framework(agent_name: str) -> AgentFramework:
    """Return the framework for an agent name."""
    return AGENT_REGISTRY[agent_name].framework


def is_framework_live(framework: AgentFramework) -> bool:
    """Return whether a framework's loader is currently live."""
    return FRAMEWORK_AVAILABLE.get(framework, False)


def framework_summary() -> dict[str, int]:
    """Return a count of agents per framework."""
    out: dict[str, int] = {}
    for wiring in AGENT_REGISTRY.values():
        key = wiring.framework.value
        out[key] = out.get(key, 0) + 1
    return out


def register_agent(wiring: AgentFleetWiring) -> None:
    """Register a new agent in the fleet (used by tests).

    This is a runtime mutation helper for the test suite. Production
    agent additions should go through the canonical registration
    path in ``agents/wiring.py`` + this module.
    """
    AGENT_REGISTRY[wiring.agent_name] = wiring
    logger.info(
        "register_agent(%s): added to fleet (framework=%s)",
        wiring.agent_name,
        wiring.framework,
    )


def unregister_agent(agent_name: str) -> None:
    """Remove an agent from the fleet (used by tests)."""
    AGENT_REGISTRY.pop(agent_name, None)
    logger.info("unregister_agent(%s): removed from fleet", agent_name)


__all__ = [
    "AGENT_REGISTRY",
    "FRAMEWORK_AVAILABLE",
    "framework_summary",
    "get_framework",
    "is_framework_live",
    "list_agent_names",
    "register_agent",
    "unregister_agent",
]