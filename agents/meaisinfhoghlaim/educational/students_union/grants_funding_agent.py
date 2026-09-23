"""cianfhoghlaim — Grants & Funding Triage Agent (Case Study 2).

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

A Google ADK LlmAgent that uses the `match_grant_to_pot` FunctionTool
to systematically review grant applications and produce a structured
award decision per the SU Funding Policy 2025/26.

Wraps `tools/grants_matcher.py` (the pure-Python implementation) as a
Google ADK FunctionTool, then composes an LlmAgent that decides the
final award amount + writes the SU Funding Officer handoff note.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from .config import config
from .tools.grants_matcher import (
    GrantApplication,
    GrantAward,
    match_grant_to_pot,
)


# ---------------------------------------------------------------------------
# ADK FunctionTool wrappers
# ---------------------------------------------------------------------------


async def match_grant_to_pot_tool(
    applicant_name: str,
    society_name: str,
    society_type: str,
    amount_requested_eur: int,
    purpose: str,
    description: str,
    has_receipts: bool,
    is_first_time_applicant: bool,
    previously_awarded_eur_this_year: int = 0,
) -> dict:
    """Match a grant application to the best-fit SU funding pot.

    Returns:
        dict with keys: matched_pot (str | None), awarded_eur (int),
        cap_reason (str | None), eligible (bool),
        rejection_reason (str | None).
    """
    app = GrantApplication(
        applicant_name=applicant_name,
        society_name=society_name,
        society_type=society_type,
        amount_requested_eur=amount_requested_eur,
        purpose=purpose,
        description=description,
        has_receipts=has_receipts,
        is_first_time_applicant=is_first_time_applicant,
        previously_awarded_eur_this_year=previously_awarded_eur_this_year,
    )
    award: GrantAward = match_grant_to_pot(app)
    return {
        "matched_pot": award.matched_pot,
        "awarded_eur": award.awarded_eur,
        "cap_reason": award.cap_reason,
        "eligible": award.eligible,
        "rejection_reason": award.rejection_reason,
    }


match_grant_to_pot_fn = FunctionTool(func=match_grant_to_pot_tool)


# ---------------------------------------------------------------------------
# Specialist agent
# ---------------------------------------------------------------------------


grants_funding_agent = LlmAgent(
    name="grants_funding_agent",
    model=config.default_model,
    description="Matches student society grant applications to the 4 SU funding pots.",
    instruction=f"""
You are the Grants & Funding Triage Agent for the University of
Galway Students' Union ({config.su_name_english} / {config.su_name_irish}).

For every submitted grant application you MUST call the
`match_grant_to_pot_tool` exactly once and then synthesise a structured
response with these 4 sections:

  1. **Decision** — one of `AWARD` / `PARTIAL_AWARD` / `REJECT`
  2. **Amount** — exact Euro value (e.g. €450)
  3. **Pot + cap explanation** — which of the 4 pots matched (TRAVEL /
     EQUIPMENT / EVENT / WELFARE) and why the award may differ from the
     requested amount
  4. **Staff handoff notes** — for the SU Funding Officer to action:
     - If receipts are missing: list the receipts that must be supplied
       before the award is released
     - If first-time applicant: flag for the 1:1 onboarding session
     - If `cap_reason` is set: quote it verbatim

Decision rules:
  - `eligible=False` → `REJECT`. Quote the rejection_reason.
  - `eligible=True` AND `awarded_eur == amount_requested_eur` → `AWARD`
  - `eligible=True` AND `awarded_eur < amount_requested_eur` → `PARTIAL_AWARD`
  - Always state the pot's max cap (per {config.su_academic_year} Funding Policy).

Funding pot caps:
  - TRAVEL:    up to €{config.max_travel_grant_eur}
  - EQUIPMENT: up to €{config.max_equipment_grant_eur}
  - EVENT:     up to €{config.max_event_grant_eur}
  - WELFARE:   up to €{config.max_welfare_grant_eur}

Tone: procedural + warm. Grant applicants are student volunteers
scrounging for every Euro; quote exact numbers and explain the cap
in plain English.

Current academic year: {config.su_academic_year}.
""",
    tools=[match_grant_to_pot_fn],
    output_key="grants_funding_decision",
)
