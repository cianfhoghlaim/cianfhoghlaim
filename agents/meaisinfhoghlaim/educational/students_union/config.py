"""cianfhoghlaim — Students' Union ADK config.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

Mirrors the cianfhoghlaim MODEL_REGISTRY fallback pattern but keeps
the SU-specific defaults local so the SU agents don't pull in the
whole meaisinfhoghlaim.models module (which is cianfhoghlaim-specific).

Default model choice for the SU agents: Gemini 2.5 Flash (cheap + fast
+ good enough for the SU workflows). The 4-tier fallback chain is
the same as the parent monorepo: Unsloth Studio (primary) → LiteLLM
proxy → MiniMax Token Plan → Gemini API.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class StudentsUnionAgentConfig:
    """Runtime config for the 5 SU agents + 1 root."""

    # Default model (cheap + fast for student workflows)
    default_model: str = "gemini-2.5-flash"
    irish_model: str = "gemini-2.5-flash"  # SU is bilingual EN/GA

    # Workflow defaults — these mirror real USG SU bylaws (2025/26)
    su_academic_year: str = "2025/26"
    su_constitution_version: str = "v3.2"
    su_name_english: str = "University of Galway Students' Union"
    su_name_irish: str = "Comhaltas na Mac Léinn, Ollscoil na Gaillimhe"

    # Funding pot caps (per the SU Funding Policy 2025/26)
    max_travel_grant_eur: int = 600
    max_equipment_grant_eur: int = 1_500
    max_event_grant_eur: int = 2_000
    max_welfare_grant_eur: int = 400

    # Welfare / complaint routing thresholds
    welfare_urgent_keywords: tuple[str, ...] = (
        "harassment", "sexual harassment", "assault", "suicide",
        "self-harm", "safeguarding", "vulnerable", "emergency",
        "danger", "abuse", "discrimination", "racism", "homophobia",
    )

    # Election rules
    min_nominator_signatures: int = 10
    hustings_min_days_before_vote: int = 7

    # Class rep
    min_class_reps_for_aggregation: int = 3  # below this, no theme extraction


def get_config() -> StudentsUnionAgentConfig:
    """Return the runtime config. Reads env vars for model overrides."""
    return StudentsUnionAgentConfig(
        default_model=os.environ.get("SU_ADK_MODEL", "gemini-2.5-flash"),
        irish_model=os.environ.get("SU_ADK_MODEL_IRISH", "gemini-2.5-flash"),
    )


config = get_config()
