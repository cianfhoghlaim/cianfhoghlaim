"""cianfhoghlaim — Election & Referendum Workflow Agent (Case Study 5).

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/, Case Study 5.

A Google ADK LlmAgent that uses the `validate_candidate_eligibility`
FunctionTool to systematically review election candidacy submissions
per the SU Election Rules 2025/26.

Wraps `tools/election_validator.py` (the pure-Python implementation)
as a Google ADK FunctionTool.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from .config import config
from .tools.election_validator import (
    Candidate,
    EligibilityResult,
    validate_candidate_eligibility,
)


async def validate_candidate_eligibility_tool(
    candidate_id: str,
    full_name: str,
    student_id: str,
    role: str,
    is_registered_student: bool,
    on_academic_suspension: bool,
    on_disciplinary_hold: bool,
    manifesto_word_count: int,
    nominator_signature_count: int,
    outstanding_su_fines_eur: float,
    previously_held_same_role: list[str] | None = None,
) -> dict:
    """Apply the SU Election Rules eligibility rubric to a candidacy."""
    cand = Candidate(
        candidate_id=candidate_id,
        full_name=full_name,
        student_id=student_id,
        role=role,
        is_registered_student=is_registered_student,
        on_academic_suspension=on_academic_suspension,
        on_disciplinary_hold=on_disciplinary_hold,
        manifesto_word_count=manifesto_word_count,
        nominator_signature_count=nominator_signature_count,
        outstanding_su_fines_eur=outstanding_su_fines_eur,
        previously_held_same_role=tuple(previously_held_same_role or []),
    )
    result: EligibilityResult = validate_candidate_eligibility(
        cand, min_signatures=config.min_nominator_signatures,
    )
    return {
        "is_eligible": result.is_eligible,
        "errors": result.errors,
        "warnings": result.warnings,
        "nominators_needed": result.nominators_needed,
    }


validate_candidate_eligibility_fn = FunctionTool(func=validate_candidate_eligibility_tool)


elections_agent = LlmAgent(
    name="elections_agent",
    model=config.default_model,
    description="Validates student candidacy per the SU Election Rules.",
    instruction=f"""
You are the Election & Referendum Workflow Agent for the University
of Galway Students' Union ({config.su_name_english} / {config.su_name_irish}).

For every candidacy submission you MUST call the
`validate_candidate_eligibility_tool` exactly once and synthesise a
structured Returning Officer briefing with these 4 sections:

  1. **Eligibility decision** — one of `CONFIRM` / `RETURN_FOR_FIXES`
     / `REJECT`
  2. **Outstanding requirements** — if not eligible, bullet the
     specific errors + the number of additional nominators needed
  3. **Warnings** — first-time candidate flag + sabbatical
     salary-eligibility flag (if applicable)
  4. **Returning Officer handoff notes** — timeline of next steps:
     hustings date (≥{config.hustings_min_days_before_vote} days before
     voting opens), manifesto archive upload, candidate photo capture,
     online Q&A scheduling

Eligibility rules:
  - `is_eligible=True` → `CONFIRM`
  - `is_eligible=False` AND `nominators_needed > 0` AND
    `len(errors) == 1` → `RETURN_FOR_FIXES`
  - `is_eligible=False` AND `len(errors) >= 2` → `REJECT`

Tone: procedural + respectful. The Returning Officer is the only
audience; you do not interact with candidates directly.

Current academic year: {config.su_academic_year}.
""",
    tools=[validate_candidate_eligibility_fn],
    output_key="elections_decision",
)
