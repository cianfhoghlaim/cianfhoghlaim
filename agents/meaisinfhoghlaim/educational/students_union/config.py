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

    # Module code → snake_case full-name canonical form (per
    # openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1).
    # The snake_case form is the FK that joins to the 4-tier tertiary
    # Module schema at dlt_sources/british_isles/ireland/tertiary/uog/modules.py.
    module_full_names: dict[str, str] = None  # type: ignore[assignment]  # filled below


# Module code → snake_case full-name canonical form (Phase 2 — the
# UoG tertiary pipeline real-data upgrade). Each entry maps the bare
# module code (e.g. "CS203") to its snake_case full-name form
# (e.g. "cs203_data_structures") so the SU agents + tools can JOIN with
# the tertiary Module schema.
MODULE_FULL_NAMES: dict[str, str] = {
    "CS101": "cs101_intro_to_computer_science",
    "CS102": "cs102_problem_solving_with_python",
    "CS201": "cs201_algorithms_and_complexity",
    "CS202": "cs202_object_oriented_programming",
    "CS203": "cs203_data_structures",
    "CS204": "cs204_databases",
    "CS301": "cs301_operating_systems_and_networks",
    "CS302": "cs302_software_engineering",
    "CS401": "cs401_final_year_project",
    "CS402": "cs402_machine_learning",
    "MA101": "ma101_calculus_1",
    "MA102": "ma102_calculus_2",
    "MA103": "ma103_linear_algebra",
    "MA201": "ma201_real_analysis",
    "MA335": "ma335_stochastic_processes",
    "MA347": "ma347_numerical_analysis",
    "MA410": "ma410_linear_models",
    "ST311": "st311_statistical_inference",
    "ST412": "st412_regression_modelling",
    "ST419": "st419_multivariate_methods",
    "ED101": "ed101_foundations_of_education",
    "ED116": "ed116_history_of_irish_education",
    "GA101": "ga101_gramadach_na_gaeilge",
    "GA102": "ga102_litriocht_na_gaeilge",
    "PH101": "ph101_classical_mechanics",
    "ME101": "me101_engineering_mechanics",
    "CH101": "ch101_general_chemistry",
    "LW101": "lw101_constitutional_law",
    "EC101": "ec101_microeconomics",
    "MD101": "md101_anatomy",
    "PS101": "ps101_intro_to_psychology",
    "GG101": "gg101_intro_to_geography",
}


def module_full_name(module_code: str) -> str | None:
    """Resolve bare module code (e.g. 'CS203') → snake_case full-name (e.g. 'cs203_data_structures')."""
    return MODULE_FULL_NAMES.get(module_code)


def get_config() -> StudentsUnionAgentConfig:
    """Return the runtime config. Reads env vars for model overrides."""
    cfg = StudentsUnionAgentConfig(
        default_model=os.environ.get("SU_ADK_MODEL", "gemini-2.5-flash"),
        irish_model=os.environ.get("SU_ADK_MODEL_IRISH", "gemini-2.5-flash"),
        module_full_names=MODULE_FULL_NAMES,
    )
    return cfg


config = get_config()
