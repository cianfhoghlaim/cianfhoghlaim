"""tuatha.routing — the canonical SubjectAgentWiring factory.

Per the academic_history_agent.py pattern (the canonical 8-field
SubjectAgentWiring dataclass), the new tuatha/ project
adopts the same shape. The factory is the canonical mount
point for every per-subject agent + per-educational agent +
per-hackathon feature.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SubjectAgentWiring:
    """The per-subject / per-educational / per-hackathon wiring.

    Pattern (verbatim from the parent's
    `agents/agent_registry.py:AGENT_REGISTRY`):
    - 5 positional fields: ncca_subject / module_slug / display_name /
      baml_prefix / langfuse_trace_name / cognee_dataset
    - Plus: letta_agent_id (the Letta memory ID)
    - Plus: litellm_routing_key (the LiteLLM routing key)

    Every agent in the new tuatha/ project carries one of these.
    The factory `build_wire()` produces the canonical instances.
    """

    ncca_subject: str
    module_slug: str
    display_name: str
    baml_prefix: str
    langfuse_trace_name: str
    cognee_dataset: str
    letta_agent_id: str
    litellm_routing_key: str = "minimax"  # the canonical 7-tier fallback


def build_wire(
    ncca_subject: str,
    module_slug: str,
    display_name: str,
    baml_prefix: str,
    langfuse_trace_name: str,
    cognee_dataset: str,
    letta_agent_id: str,
    litellm_routing_key: str = "minimax",
) -> SubjectAgentWiring:
    """Build the canonical SubjectAgentWiring for a subject / educational / hackathon.

    Per the parent's `agents/agent_registry.py:register_ncca_subjects_in_agent_registry()`
    pattern: the factory produces the canonical SubjectAgentWiring
    that the parent repo registers in the AGENT_REGISTRY.
    """
    return SubjectAgentWiring(
        ncca_subject=ncca_subject,
        module_slug=module_slug,
        display_name=display_name,
        baml_prefix=baml_prefix,
        langfuse_trace_name=langfuse_trace_name,
        cognee_dataset=cognee_dataset,
        letta_agent_id=letta_agent_id,
        litellm_routing_key=litellm_routing_key,
    )


# ── The canonical 8-subject wire registry ──────────────────────


SUBJECT_WIRING_REGISTRY: dict[str, SubjectAgentWiring] = {
    "mathematics": build_wire(
        ncca_subject="mathematics",
        module_slug="math",
        display_name="Mathematics",
        baml_prefix="Math",
        langfuse_trace_name="agent.mathematics.<verb>",
        cognee_dataset="oideachais_lc_mathematics",
        letta_agent_id="kcg-mathematics-agent",
    ),
    "applied_mathematics": build_wire(
        ncca_subject="applied_mathematics",
        module_slug="appm",
        display_name="Applied Mathematics",
        baml_prefix="AppM",
        langfuse_trace_name="agent.applied_mathematics.<verb>",
        cognee_dataset="oideachais_lc_applied_mathematics",
        letta_agent_id="kcg-applied-mathematics-agent",
    ),
    "chemistry": build_wire(
        ncca_subject="chemistry",
        module_slug="chem",
        display_name="Chemistry",
        baml_prefix="Chem",
        langfuse_trace_name="agent.chemistry.<verb>",
        cognee_dataset="oideachais_lc_chemistry",
        letta_agent_id="kcg-chemistry-agent",
    ),
    "geography": build_wire(
        ncca_subject="geography",
        module_slug="geog",
        display_name="Geography",
        baml_prefix="Geog",
        langfuse_trace_name="agent.geography.<verb>",
        cognee_dataset="oideachais_lc_geography",
        letta_agent_id="kcg-geography-agent",
    ),
    "history": build_wire(
        ncca_subject="history",
        module_slug="hist",
        display_name="History",
        baml_prefix="Hist",
        langfuse_trace_name="agent.history.<verb>",
        cognee_dataset="oideachais_lc_history",
        letta_agent_id="kcg-history-agent",
    ),
    "english": build_wire(
        ncca_subject="english",
        module_slug="engl",
        display_name="English",
        baml_prefix="Engl",
        langfuse_trace_name="agent.english.<verb>",
        cognee_dataset="oideachais_lc_english",
        letta_agent_id="kcg-english-agent",
    ),
    "gaeilge": build_wire(
        ncca_subject="gaeilge",
        module_slug="gael",
        display_name="Gaeilge",
        baml_prefix="Gael",
        langfuse_trace_name="agent.gaeilge.<verb>",
        cognee_dataset="oideachais_lc_gaeilge",
        letta_agent_id="kcg-gaeilge-agent",
    ),
    "computer_science": build_wire(
        ncca_subject="computer_science",
        module_slug="comp",
        display_name="Computer Science",
        baml_prefix="Comp",
        langfuse_trace_name="agent.computer_science.<verb>",
        cognee_dataset="oideachais_lc_computer_science",
        letta_agent_id="kcg-computer-science-agent",
    ),
}


# ── The canonical 3-educational wire registry ────────────────


EDUCATIONAL_WIRING_REGISTRY: dict[str, SubjectAgentWiring] = {
    "academic_history": build_wire(
        ncca_subject="academic_history",
        module_slug="academic_history",
        display_name="Academic History",
        baml_prefix="AcadHist",
        langfuse_trace_name="agent.academic_history.<verb>",
        cognee_dataset="oideachais_academic_history",
        letta_agent_id="kcg-academic-history-agent",
    ),
    "celtic_grammar": build_wire(
        ncca_subject="celtic_grammar",
        module_slug="celtic_grammar",
        display_name="Celtic Grammar",
        baml_prefix="CeltGram",
        langfuse_trace_name="agent.celtic_grammar.<verb>",
        cognee_dataset="oideachais_celtic_grammar",
        letta_agent_id="kcg-celtic-grammar-agent",
    ),
    "celtic_morphology": build_wire(
        ncca_subject="celtic_morphology",
        module_slug="celtic_morphology",
        display_name="Celtic Morphology",
        baml_prefix="CeltMorph",
        langfuse_trace_name="agent.celtic_morphology.<verb>",
        cognee_dataset="oideachais_celtic_morphology",
        letta_agent_id="kcg-celtic-morphology-agent",
    ),
}


# ── The canonical 4-hackathon wire registry ─────────────────


HACKATHON_WIRING_REGISTRY: dict[str, SubjectAgentWiring] = {
    "marking_grader": build_wire(
        ncca_subject="marking_grader",
        module_slug="marking_grader",
        display_name="Marking Grader",
        baml_prefix="MarkGrade",
        langfuse_trace_name="agent.marking_grader.<verb>",
        cognee_dataset="oideachais_marking_grader",
        letta_agent_id="kcg-marking-grader-agent",
    ),
    "adaptive_tutor": build_wire(
        ncca_subject="adaptive_tutor",
        module_slug="adaptive_tutor",
        display_name="Adaptive Tutor",
        baml_prefix="AdaptTutor",
        langfuse_trace_name="agent.adaptive_tutor.<verb>",
        cognee_dataset="oideachais_adaptive_tutor",
        letta_agent_id="kcg-adaptive-tutor-agent",
    ),
    "equivalency_generator": build_wire(
        ncca_subject="equivalency_generator",
        module_slug="equivalency_generator",
        display_name="Equivalency Generator",
        baml_prefix="EquivGen",
        langfuse_trace_name="agent.equivalency_generator.<verb>",
        cognee_dataset="oideachais_equivalency_generator",
        letta_agent_id="kcg-equivalency-generator-agent",
    ),
    "curriculum_change_sensor": build_wire(
        ncca_subject="curriculum_change_sensor",
        module_slug="curriculum_change_sensor",
        display_name="Curriculum Change Sensor",
        baml_prefix="CurrChgSens",
        langfuse_trace_name="agent.curriculum_change_sensor.<verb>",
        cognee_dataset="oideachais_curriculum_change_sensor",
        letta_agent_id="kcg-curriculum-change-sensor-agent",
    ),
}


__all__ = [
    "EDUCATIONAL_WIRING_REGISTRY",
    "HACKATHON_WIRING_REGISTRY",
    "SUBJECT_WIRING_REGISTRY",
    "SubjectAgentWiring",
    "build_wire",
]
