"""cianfhoghlaim — Clubs & Societies Registration Agent (Case Study 1).

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

A Google ADK LlmAgent that uses the `validate_club_application` FunctionTool
to systematically review new club applications and either auto-approve
them (when fully valid) or return a structured rejection-with-feedback
report.

Wraps `tools/clubs_socs_validator.py` (the pure-Python implementation)
as a Google ADK FunctionTool, then composes an LlmAgent that decides
which clubs to auto-approve vs. which to return for human review.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from .config import config
from .tools.clubs_socs_validator import ClubApplication, validate_club_application
from .tools.clubs_socs_validator import ValidationResult as _ValidationResult


# ---------------------------------------------------------------------------
# ADK FunctionTool wrappers
# ---------------------------------------------------------------------------


async def validate_club_application_tool(
    club_name: str,
    society_type: str,
    member_count: int,
    has_constitution: bool,
    has_safeguarding_officer: bool,
    has_committee: bool,
    has_bank_account: bool,
    gdpr_compliant: bool,
    purpose_statement: str,
    contact_email: str,
) -> dict:
    """Apply the University of Galway SU Clubs & Societies validation rubric.

    Returns:
        dict with keys: is_valid (bool), errors (list[str]),
        warnings (list[str]), score (int 0-100).
    """
    app = ClubApplication(
        club_name=club_name,
        society_type=society_type,
        member_count=member_count,
        has_constitution=has_constitution,
        has_safeguarding_officer=has_safeguarding_officer,
        has_committee=has_committee,
        has_bank_account=has_bank_account,
        gdpr_compliant=gdpr_compliant,
        purpose_statement=purpose_statement,
        contact_email=contact_email,
    )
    result: _ValidationResult = validate_club_application(app)
    return {
        "is_valid": result.is_valid,
        "errors": result.errors,
        "warnings": result.warnings,
        "score": result.score,
    }


validate_club_application_fn = FunctionTool(func=validate_club_application_tool)


# ---------------------------------------------------------------------------
# Specialist agent
# ---------------------------------------------------------------------------


clubs_socs_agent = LlmAgent(
    name="clubs_socs_agent",
    model=config.default_model,
    description="Reviews University of Galway SU Clubs & Societies registration applications.",
    instruction=f"""
You are the Clubs & Societies Registration Agent for the University of
Galway Students' Union ({config.su_name_english} / {config.su_name_irish}).

For every submitted application you MUST call the
`validate_club_application_tool` exactly once and then synthesise a
structured response with these 4 sections:

  1. **Decision** — one of `APPROVE` / `REJECT` / `RETURN_FOR_AMENDMENT`
  2. **Rationale** — bullet list referencing the validation result's
     errors + warnings verbatim
  3. **Score** — echo the 0-100 completeness score
  4. **Staff handoff notes** — free-text note to the SU Clubs Officer
     (e.g. "political society — flag the affiliation declaration
     requirement" or "first-time applicant — pair with a returning
     society for committee succession mentoring")

Decision rules:
  - `is_valid=True` AND `score >= 80` → `APPROVE`
  - `is_valid=False` AND `len(errors) <= 2` → `RETURN_FOR_AMENDMENT`
  - `is_valid=False` AND `len(errors) >= 3` → `REJECT`
  - If the application is a `political` society type, ALWAYS add the
    political-affiliation-declaration handoff note.

Tone: supportive + procedural. The applicant is a student volunteer,
not a customer; offer concrete, fixable feedback rather than
rejection-with-no-path-forward.

Current academic year: {config.su_academic_year}.
Constitution version applied: {config.su_constitution_version}.
""",
    tools=[validate_club_application_fn],
    output_key="clubs_socs_decision",
)
