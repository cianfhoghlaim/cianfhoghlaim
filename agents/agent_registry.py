"""Agent fleet registry.

The single source of truth for the 13 main agents in the
Cianfhoghlaim agent fleet. The 8 NCCA subject agents are
re-exported through ``agents/tuatha/wiring.py`` for back-compat.

The 13 main agents are:

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

Reference: openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1.
Extended by openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/
(Phase L — image_generation_agent).
"""
from __future__ import annotations

import logging

from .wiring import AgentFleetWiring, AgentFramework

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# The 13-agent fleet registry.
# ---------------------------------------------------------------------------


AGENT_REGISTRY: dict[str, AgentFleetWiring] = {
    "root_agent": AgentFleetWiring(
        agent_name="root_agent",
        module_slug="root",
        module_path="cianfhoghlaim.agents.adk.root_agent",
        framework=AgentFramework.CUSTOM,
        display_name="Root Agent",
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
    # Media-Intel Descriptor agent (per 2026-08-23-tuatha-media-
    # intel-gameplay-capture-research-v1). The 10-tool ADK agent
    # that orchestrates the 5 per-medium BAML extractor
    # functions in baml_src/media/. The reference-corpus spine
    # for the Hickman + WoT + ATLA + Hades+WoW+Golden Sun +
    # NCCA+SEC+CELT+Dúchas+Wikipedia ingestion.
    # Re-routed 2026-08-25 (per 2026-08-25-tuatha-british-isles-
    # mmo-consolidation-v1): the module now lives in the new
    # tuatha/ independent sub-project at
    # /Users/cianmacandeisigh/dev/kings_college_galway/tuatha/
    # (the British Isles Formative Assessment MMO). The
    # cianfhoghlaim.agents.meaisinfhoghlaim.media_intel
    # location is retained as a back-compat re-export until
    # the parent's meaisinfhoghlaim/media_intel/ is removed
    # in a subsequent change.
    # ---------------------------------------------------------------------
    "media_descriptor_agent": AgentFleetWiring(
        agent_name="media_descriptor_agent",
        module_slug="media_descriptor",
        module_path="tuatha.agents.media_intel.media_descriptor_agent",
        framework=AgentFramework.ADK,
        display_name="Media-Intel Descriptor Agent",
        baml_prefix="MediaDesc",
        langfuse_trace_name="agent.media_descriptor.extract",
        cognee_dataset="oideachais_media_descriptors",
        letta_agent_id="kcg-media-descriptor-agent",
        litellm_routing_key="media_descriptor",
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
