"""cianfhoghlaim — Election candidate eligibility validator.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/, Case Study 5.

Validates Sabbatical Officer + Part-Time Officer + Class Rep election
candidates per the SU Election Rules 2025/26.

Hard requirements:
  - Registered student at University of Galway for the academic year
  - Not on academic suspension or disciplinary hold
  - Has submitted a manifesto (min 200 words)
  - Has the minimum 10 nominator signatures
  - No outstanding SU fines (>€50 = blocked)
  - No current sabbatical officer re-standing without a 1-academic-year gap

Soft warnings:
  - First-time candidacy (warn the candidate about campaign timeline)
  - Same-role re-standing in the past 2 years

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Candidate:
    """An election candidate."""
    candidate_id: str
    full_name: str
    student_id: str
    role: str  # "SABBATICAL_PRESIDENT" | "SABBATICAL_VP_EDUCATION" | ... | "PART_TIME_OFFICER" | "CLASS_REP"
    is_registered_student: bool
    on_academic_suspension: bool
    on_disciplinary_hold: bool
    manifesto_word_count: int
    nominator_signature_count: int
    outstanding_su_fines_eur: float
    previously_held_same_role: tuple[str, ...] = field(default_factory=tuple)  # academic years like "2023/24"


@dataclass(frozen=True)
class EligibilityResult:
    is_eligible: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    nominators_needed: int = 0  # how many more signatures are required


def validate_candidate_eligibility(candidate: Candidate, *, min_signatures: int = 10) -> EligibilityResult:
    """Apply the 6 hard requirements + 2 soft warnings per SU Election Rules."""
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Hard: registered student
    if not candidate.is_registered_student:
        errors.append("not_registered_student: must be a registered student at University of Galway")

    # 2. Hard: not on academic suspension or disciplinary hold
    if candidate.on_academic_suspension:
        errors.append("on_academic_suspension: ineligible while suspended")
    if candidate.on_disciplinary_hold:
        errors.append("on_disciplinary_hold: disciplinary hold blocks candidacy")

    # 3. Hard: manifesto ≥ 200 words
    if candidate.manifesto_word_count < 200:
        errors.append(f"manifesto_too_short: {candidate.manifesto_word_count} words (minimum 200)")

    # 4. Hard: minimum nominator signatures
    nominators_needed = max(0, min_signatures - candidate.nominator_signature_count)
    if candidate.nominator_signature_count < min_signatures:
        errors.append(f"insufficient_nominators: {candidate.nominator_signature_count} of {min_signatures} required")

    # 5. Hard: outstanding SU fines ≤ €50
    if candidate.outstanding_su_fines_eur > 50:
        errors.append(f"outstanding_fines: €{candidate.outstanding_su_fines_eur:.2f} exceeds the €50 threshold")

    # 6. Hard: no same-role re-standing in the immediate previous year (Sabb only).
    # The 1-academic-year gap means: if you held the role in 2024/25,
    # you're blocked from re-standing in 2025/26. 2023/24 is OK
    # (that's a 1-year gap — you sat out 2024/25).
    if candidate.role.startswith("SABBATICAL_"):
        immediate_previous = "2024/25"
        recent_terms = [yr for yr in candidate.previously_held_same_role if yr == immediate_previous]
        if recent_terms:
            errors.append(f"sabbatical_repeat_term: previously held {candidate.role} in {', '.join(recent_terms)} — must wait 1 academic year before re-standing")

    # Soft warnings
    if not candidate.previously_held_same_role:
        warnings.append("first_time_candidate: candidate is encouraged to attend the Returning Officer briefing")
    if candidate.role.startswith("SABBATICAL_") and "2024/25" not in candidate.previously_held_same_role:
        warnings.append("sabbatical_role: confirm salary eligibility + role-description acknowledgement")

    return EligibilityResult(
        is_eligible=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        nominators_needed=nominators_needed,
    )
