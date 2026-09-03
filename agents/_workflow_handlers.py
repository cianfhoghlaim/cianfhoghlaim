"""Shared async dispatchers for the agent fleet.

The 4 dispatchers:

- :func:`dispatch_study_plan` — route a StudyPlanContext to the
  curriculum + 8 NCCA subject agents
- :func:`dispatch_deep_research` — route a ResearchQuery to the
  research + education_research + bunchloch_research agents
- :func:`dispatch_literature_review` — route a LiteratureReviewQuery
  to the corpus + research agents
- :func:`dispatch_summary` — route a SummaryRequest to the
  corpus + translation + statistics agents

Each dispatcher SHALL route to the appropriate agent via the
``AGENT_REGISTRY`` based on the ``domain`` field of the input
context, and SHALL gracefully degrade (returning ``{}`` or a
stub response) when the target agent is unavailable.

Reference: openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Input context dataclasses for the 4 dispatchers.
# ---------------------------------------------------------------------------


@dataclass
class StudyPlanContext:
    """The input context for :func:`dispatch_study_plan`."""

    domain: str
    subject: str
    student_level: str | None = None
    duration_weeks: int = 12
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchQuery:
    """The input context for :func:`dispatch_deep_research`."""

    domain: str
    question: str
    sources: list[str] = field(default_factory=list)
    max_results: int = 10
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LiteratureReviewQuery:
    """The input context for :func:`dispatch_literature_review`."""

    domain: str
    topic: str
    years: tuple[int, int] | None = None
    languages: tuple[str, ...] = ("en", "ga")
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SummaryRequest:
    """The input context for :func:`dispatch_summary`."""

    domain: str
    content: str
    max_tokens: int = 500
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Dispatcher 1: dispatch_study_plan
# ---------------------------------------------------------------------------


async def dispatch_study_plan(ctx: StudyPlanContext) -> dict[str, Any]:
    """Dispatch a study plan request to the appropriate agent.

    Routes to the curriculum_agent by default; if a subject is
    specified, also looks up the matching NCCA subject agent
    (gael/math/chem/comp/engl/geog) and merges the results.

    Returns a dict with the per-subject ``lectionary`` and
    per-student ``progress`` keys. Returns ``{}`` when no
    agents are reachable.
    """
    from .agent_registry import AGENT_REGISTRY

    target_agents = ["curriculum_agent"]

    # Map subject → NCCA slug.
    subject_to_slug = {
        "gaeilge": "gael_agent",
        "mathematics": "math_agent",
        "chemistry": "chem_agent",
        "computer_science": "comp_agent",
        "english": "engl_agent",
        "geography": "geog_agent",
        "applied_mathematics": "appm_agent",
        "history": "hist_agent",
    }
    ncca_slug = subject_to_slug.get(ctx.subject)
    if ncca_slug:
        target_agents.append(ncca_slug)

    out: dict[str, Any] = {
        "lectionary": {},
        "progress": {},
    }

    for agent_name in target_agents:
        if agent_name not in AGENT_REGISTRY:
            logger.debug(
                "dispatch_study_plan: agent %s not in AGENT_REGISTRY",
                agent_name,
            )
            continue
        try:
            # In a full implementation, this would call the agent's
            # ``generate_study_plan()`` method. For the wiring layer
            # we return a stub.
            out["lectionary"][agent_name] = {
                "subject": ctx.subject,
                "student_level": ctx.student_level,
                "duration_weeks": ctx.duration_weeks,
            }
            out["progress"][agent_name] = {"weeks_completed": 0}
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "dispatch_study_plan(%s): %s", agent_name, exc
            )
            continue

    return out


# ---------------------------------------------------------------------------
# Dispatcher 2: dispatch_deep_research
# ---------------------------------------------------------------------------


async def dispatch_deep_research(query: ResearchQuery) -> dict[str, Any]:
    """Dispatch a deep-research query to the research agent.

    Routes to the research_agent first; falls back to
    education_research_agent for policy queries or
    bunchloch_research_agent for on-device queries.

    Returns a dict with ``answer`` + ``citations`` + ``sources``.
    Returns ``{}`` when no agents are reachable.
    """
    from .agent_registry import AGENT_REGISTRY

    # Map domain → target agent.
    domain_to_agent = {
        "policy": "education_research_agent",
        "education": "education_research_agent",
        "local": "bunchloch_research_agent",
        "on_device": "bunchloch_research_agent",
    }
    target = domain_to_agent.get(query.domain, "research_agent")

    if target not in AGENT_REGISTRY:
        logger.debug(
            "dispatch_deep_research: agent %s not in AGENT_REGISTRY",
            target,
        )
        return {}

    try:
        # In a full implementation, this would call the agent's
        # ``research()`` method. For the wiring layer we return
        # a stub.
        return {
            "answer": f"[stub] {query.question}",
            "citations": query.sources[: query.max_results],
            "sources": query.sources[: query.max_results],
            "agent": target,
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "dispatch_deep_research(%s): %s", target, exc
        )
        return {}


# ---------------------------------------------------------------------------
# Dispatcher 3: dispatch_literature_review
# ---------------------------------------------------------------------------


async def dispatch_literature_review(
    query: LiteratureReviewQuery,
) -> dict[str, Any]:
    """Dispatch a literature-review query to the corpus + research agents.

    Routes to corpus_agent (corpus search) first, then to
    research_agent (citation lookup) for the cross-language literature
    review.

    Returns a dict with ``corpus_hits`` + ``citations`` + ``years``.
    Returns ``{}`` when no agents are reachable.
    """
    from .agent_registry import AGENT_REGISTRY

    targets = ["corpus_agent", "research_agent"]
    out: dict[str, Any] = {
        "corpus_hits": [],
        "citations": [],
        "years": query.years or (2000, 2026),
    }

    for agent_name in targets:
        if agent_name not in AGENT_REGISTRY:
            continue
        try:
            # In a full implementation, this would call the agent's
            # ``literature_review()`` method. For the wiring layer
            # we return a stub.
            out["corpus_hits"].append(
                {
                    "agent": agent_name,
                    "topic": query.topic,
                    "languages": list(query.languages),
                }
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "dispatch_literature_review(%s): %s",
                agent_name, exc,
            )
            continue

    return out


# ---------------------------------------------------------------------------
# Dispatcher 4: dispatch_summary
# ---------------------------------------------------------------------------


async def dispatch_summary(req: SummaryRequest) -> dict[str, Any]:
    """Dispatch a summary request to the appropriate agent.

    Routes to corpus_agent (text summarization), translation_agent
    (cross-language summary), or statistics_agent (numeric summary)
    based on the ``domain`` field.

    Returns a dict with ``summary`` + ``tokens_used``. Returns ``{}``
    when no agents are reachable.
    """
    from .agent_registry import AGENT_REGISTRY

    domain_to_agent = {
        "text": "corpus_agent",
        "translation": "translation_agent",
        "numeric": "statistics_agent",
        "statistics": "statistics_agent",
    }
    target = domain_to_agent.get(req.domain, "corpus_agent")

    if target not in AGENT_REGISTRY:
        logger.debug(
            "dispatch_summary: agent %s not in AGENT_REGISTRY", target
        )
        return {}

    try:
        # Naive truncation for the wiring layer stub.
        truncated = req.content[: req.max_tokens * 4]
        return {
            "summary": truncated,
            "tokens_used": min(len(truncated) // 4, req.max_tokens),
            "agent": target,
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "dispatch_summary(%s): %s", target, exc
        )
        return {}


__all__ = [
    "LiteratureReviewQuery",
    "ResearchQuery",
    "StudyPlanContext",
    "SummaryRequest",
    "dispatch_deep_research",
    "dispatch_literature_review",
    "dispatch_study_plan",
    "dispatch_summary",
]