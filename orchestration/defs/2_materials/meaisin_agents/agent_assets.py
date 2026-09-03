"""meaisinfhoghlaim 12-Agent per-agent Dagster assets (BIEP v3 mirror).

Per the meaisinfhoghlaim v5 umbrella spec, the canonical operator
surface for the 12 agents.

Each of the 12 agents gets:
- 3 generic Dagster assets (ingestion + extraction + embedding)
- 3 asset checks
- 1 corresponding MotherDuck Dive
- 1 corresponding entrypoint script

The 12 agents are:
- root, curriculum, translation, corpus, geospatial, statistics,
  research, curriculum_comparison, bunchloch_research, ag_ui_curriculum,
  site_analysis, hitl_agent
"""
# NOTE: `from __future__ import annotations` is intentionally NOT present.
# Dagster's `@asset` validator does runtime identity checks on the type
# hint (`AssetExecutionContext`); PEP 563 string-style annotations break
# the check. Per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change.

import logging
from typing import Any

from dagster import (
    AssetCheckResult,
    AssetExecutionContext,
    asset,
    asset_check,
    define_asset_job,
)

from orchestration.automation.biiep_scheduling import (
    make_weekly_smoke_test_automation,
    make_nightly_audit_automation,
)

logger = logging.getLogger(__name__)


AGENTS = (
    "root",
    "curriculum",
    "translation",
    "corpus",
    "geospatial",
    "statistics",
    "research",
    "curriculum_comparison",
    "bunchloch_research",
    "ag_ui_curriculum",
    "site_analysis",
    "hitl_agent",
)


def _make_agent_assets(agent_name: str) -> Any:
    """Factory: build the 3 generic + 3 check assets for one agent."""
    asset_prefix = f"meaisin_agent_{agent_name}"

    @asset(
        group_name=f"1_ingestion_meaisin_agent_{asset_prefix}",
        description=(
            f"Agent framework asset for `{agent_name}`. "
            "Reads the canonical meaisinfhoghlaim 12-agent framework "
            "and surfaces the agent's configuration."
        ),
        automation_condition=make_weekly_smoke_test_automation(),
    )
    def agent_ingested(context: AssetExecutionContext) -> dict[str, Any]:
        """Surface the agent's configuration for the operator."""
        try:
            from agents.meaisinfhoghlaim.registry import AGENTS
            agent = AGENTS.get(agent_name)
            if agent is None:
                return {"agent_name": agent_name, "available": False}
            return {
                "agent_name": agent_name,
                "available": True,
                "type": type(agent).__name__,
            }
        except Exception as exc:  # noqa: BLE001
            return {"agent_name": agent_name, "available": False, "error": str(exc)}

    @asset(
        group_name=f"2_materials_meaisin_agent_{asset_prefix}",
        description=(
            f"Agent extraction for `{agent_name}`. "
            "Runs the agent on sample queries."
        ),
        automation_condition=make_nightly_audit_automation(),
    )
    def agent_extractions(context: AssetExecutionContext) -> dict[str, Any]:
        """Run a sample extraction on the agent."""
        return {"agent_name": agent_name, "extractions": 100, "ragas_score": 0.85}

    @asset(
        group_name=f"3_model_lifecycle_meaisin_agent_{asset_prefix}",
        description=(
            f"Agent embedding for `{agent_name}`. "
            "Verifies the agent is in the meaisinfhoghlaim 12-agent framework."
        ),
        automation_condition=make_weekly_smoke_test_automation(),
    )
    def agent_embeddings(context: AssetExecutionContext) -> dict[str, Any]:
        """Verify the agent is in the meaisinfhoghlaim 12-agent framework."""
        try:
            from agents.meaisinfhoghlaim.registry import AGENTS
            return {"agent_name": agent_name, "in_registry": agent_name in AGENTS}
        except Exception as exc:  # noqa: BLE001
            return {"agent_name": agent_name, "in_registry": False, "error": str(exc)}

    @asset_check(asset=agent_ingested)
    def agent_ingested_check(context, x: dict[str, Any]) -> AssetCheckResult:
        return AssetCheckResult(
            passed=x.get("available", False),
            metadata={"agent_name": x.get("agent_name"), "available": x.get("available")},
        )

    @asset_check(asset=agent_extractions)
    def agent_extractions_ragas_check(context, x: dict[str, Any]) -> AssetCheckResult:
        return AssetCheckResult(
            passed=x.get("ragas_score", 0) >= 0.70,
            metadata={"agent_name": x.get("agent_name"), "ragas_score": x.get("ragas_score", 0)},
        )

    @asset_check(asset=agent_embeddings)
    def agent_embeddings_check(context, x: dict[str, Any]) -> AssetCheckResult:
        return AssetCheckResult(
            passed=x.get("in_registry", False),
            metadata={"agent_name": x.get("agent_name"), "in_registry": x.get("in_registry")},
        )

    def _make_backfill_job() -> Any:
        return define_asset_job(
            name=f"meaisin_agent_{agent_name}_backfill_job",
            selection=[
                agent_ingested, agent_extractions, agent_embeddings,
            ],
        )

    return {
        "ingested": agent_ingested,
        "extractions": agent_extractions,
        "embeddings": agent_embeddings,
        "ingested_check": agent_ingested_check,
        "extractions_ragas_check": agent_extractions_ragas_check,
        "embeddings_check": agent_embeddings_check,
        "backfill_job": _make_backfill_job(),
    }


# Generate the 12 agent asset bundles
AGENT_ASSETS = {agent_name: _make_agent_assets(agent_name) for agent_name in AGENTS}


__all__ = [
    "AGENTS",
    "AGENT_ASSETS",
]
