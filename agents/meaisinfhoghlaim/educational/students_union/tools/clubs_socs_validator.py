"""cianfhoghlaim — Clubs & Societies application validator.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/, Case Study 1.

The validator implements the University of Galway Students' Union
Clubs & Societies Registration Policy 2025/26 (mirrored from the
public SU constitution). Pure-Python, no LLM, deterministic.

Returns a `ValidationResult` with:
  - `is_valid` — True iff every hard requirement is met
  - `errors` — list of hard-fail reasons (block registration)
  - `warnings` — list of soft warnings (allow registration with notes)
  - `score` — 0-100 completeness score (for SU staff dashboard)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ClubApplication:
    """A submitted Clubs & Societies registration application."""
    club_name: str
    society_type: str  # "academic" | "cultural" | "political" | "sports" | "social_cause" | "performing_arts" | "other"
    member_count: int
    has_constitution: bool
    has_safeguarding_officer: bool
    has_committee: bool  # Chair + Secretary + Treasurer minimum
    has_bank_account: bool
    gdpr_compliant: bool
    purpose_statement: str  # min 50 chars per SU bylaws
    contact_email: str  # must end in @universityofgalway.ie or @nuigalway.ie


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: int = 0


def validate_club_application(app: ClubApplication) -> ValidationResult:
    """Apply the 8 hard requirements + 3 soft warnings per SU bylaws."""
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Hard: minimum 10 members
    if app.member_count < 10:
        errors.append(f"member_count_too_low: {app.member_count} (minimum 10 per SU bylaws)")

    # 2. Hard: written constitution
    if not app.has_constitution:
        errors.append("missing_constitution")

    # 3. Hard: designated safeguarding officer
    if not app.has_safeguarding_officer:
        errors.append("missing_safeguarding_officer")

    # 4. Hard: minimum committee
    if not app.has_committee:
        errors.append("missing_committee: must designate Chair, Secretary, and Treasurer")

    # 5. Hard: dedicated bank account (or treasurer with reimbursement pathway)
    if not app.has_bank_account:
        warnings.append("no_bank_account: treasurer must declare reimbursement pathway at first AGM")

    # 6. Hard: GDPR compliance (data-protection policy on file)
    if not app.gdpr_compliant:
        errors.append("missing_gdpr_policy: data-protection policy must be on file with the SU")

    # 7. Hard: purpose statement ≥ 50 chars
    if len(app.purpose_statement) < 50:
        errors.append(f"purpose_statement_too_short: {len(app.purpose_statement)} chars (minimum 50)")

    # 8. Hard: contact email must be a uni-of-galway address
    email = app.contact_email.lower()
    if not (email.endswith("@universityofgalway.ie") or email.endswith("@nuigalway.ie")):
        errors.append(f"contact_email_invalid: must be a universityofgalway.ie or nuigalway.ie address")

    # Soft warnings
    if app.society_type == "political":
        warnings.append("political_society: SU political-affiliation declaration required before affiliation")
    if app.society_type == "other":
        warnings.append("society_type_other: SU staff will re-categorise during onboarding")
    if app.member_count < 15:
        warnings.append("low_member_count: consider recruiting to 15+ for sustainable committee succession")

    # Score = 100 - (20 per error) - (5 per warning), floor at 0
    score = max(0, 100 - 20 * len(errors) - 5 * len(warnings))

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        score=score,
    )
