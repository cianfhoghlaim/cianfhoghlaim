"""cianfhoghlaim — Grants & Funding matcher.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/, Case Study 2.

Matches grant applications to the 4 SU funding pots (per the SU Funding
Policy 2025/26) and calculates partial awards based on the documented
scoring rubric. Pure-Python, deterministic.

Funding pots:
  - TRAVEL      — up to €600 per academic year (competitions, conferences, field trips)
  - EQUIPMENT   — up to €1,500 per academic year (society kit, lab consumables, software licences)
  - EVENT       — up to €2,000 per academic year (one-off events, balls, showcases)
  - WELFARE     — up to €400 per academic year (hardship top-ups, exam breakfasts, period products)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FundingPot:
    name: str
    max_eur: int
    eligible_purposes: tuple[str, ...]
    eligible_society_types: tuple[str, ...]


# The canonical 4 SU funding pots
SU_FUNDING_POTS: tuple[FundingPot, ...] = (
    FundingPot(
        name="TRAVEL",
        max_eur=600,
        eligible_purposes=("competition", "conference", "field_trip", "exchange", "study_visit"),
        eligible_society_types=("academic", "sports", "cultural", "performing_arts", "political"),
    ),
    FundingPot(
        name="EQUIPMENT",
        max_eur=1_500,
        eligible_purposes=("equipment", "software_licence", "consumables", "venue_hire_recurring"),
        eligible_society_types=("academic", "sports", "cultural", "performing_arts", "political", "social_cause"),
    ),
    FundingPot(
        name="EVENT",
        max_eur=2_000,
        eligible_purposes=("one_off_event", "ball", "showcase", "cultural_celebration", "charity_event"),
        eligible_society_types=tuple(),  # all types eligible
    ),
    FundingPot(
        name="WELFARE",
        max_eur=400,
        eligible_purposes=("hardship_topup", "exam_breakfast", "period_products", "mental_health_initiative"),
        eligible_society_types=tuple(),  # all types eligible
    ),
)


@dataclass(frozen=True)
class GrantApplication:
    """A submitted grant application."""
    applicant_name: str
    society_name: str
    society_type: str
    amount_requested_eur: int
    purpose: str  # one of the eligible_purposes per pot
    description: str
    has_receipts: bool
    is_first_time_applicant: bool
    previously_awarded_eur_this_year: int = 0


@dataclass(frozen=True)
class GrantAward:
    """The result of matching an application to a funding pot."""
    matched_pot: str | None  # None = no eligible pot
    awarded_eur: int
    cap_reason: str | None  # why we capped below the requested amount
    eligible: bool
    rejection_reason: str | None


def match_grant_to_pot(application: GrantApplication) -> GrantAward:
    """Match the application to the single best-fit pot + calculate award.

    Selection logic:
      1. Filter pots whose eligible_purposes contains application.purpose
      2. Filter further by eligible_society_types (empty tuple = all types)
      3. Pick the first match (deterministic, in declared order)
      4. Award = min(application.amount_requested_eur, pot.max_eur)
      5. Subtract previously_awarded_eur_this_year from the cap
      6. Apply +20% bonus for first-time applicants (within the cap)
    """
    eligible_pots = [
        pot for pot in SU_FUNDING_POTS
        if application.purpose in pot.eligible_purposes
        and (not pot.eligible_society_types or application.society_type in pot.eligible_society_types)
    ]

    if not eligible_pots:
        return GrantAward(
            matched_pot=None,
            awarded_eur=0,
            cap_reason=None,
            eligible=False,
            rejection_reason=(
                f"no_eligible_pot: purpose={application.purpose!r} + "
                f"society_type={application.society_type!r} does not match any SU funding pot"
            ),
        )

    # First match wins (deterministic)
    chosen = eligible_pots[0]

    # Calculate effective cap (minus what's already been awarded this year)
    effective_cap = max(0, chosen.max_eur - application.previously_awarded_eur_this_year)

    # Base award
    base_award = min(application.amount_requested_eur, effective_cap)

    cap_reason: str | None = None
    if application.amount_requested_eur > effective_cap:
        cap_reason = (
            f"requested_{application.amount_requested_eur}_eur_exceeds_effective_cap_{effective_cap}_eur_"
            f"(max_{chosen.max_eur}_eur_minus_{application.previously_awarded_eur_this_year}_eur_already_awarded)"
        )

    # First-time applicant bonus (+20%, capped at the effective_cap)
    if application.is_first_time_applicant:
        base_award = min(int(base_award * 1.20), effective_cap)

    # Receipts requirement: no receipts = -50% (still award if > 0)
    if not application.has_receipts and base_award > 0:
        base_award = base_award // 2
        cap_reason = (cap_reason or "") + " [receipts_missing: -50% applied]"

    return GrantAward(
        matched_pot=chosen.name,
        awarded_eur=base_award,
        cap_reason=cap_reason,
        eligible=True,
        rejection_reason=None,
    )
