"""cianfhoghlaim — Tools shared by the 5 Students' Union ADK agents.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

The 5 tools are pure-Python (no LLM, no network) so each can be smoke-
tested in isolation and used both by the ADK agents AND by the marimo
notebook directly.

The BAML schemas for the I/O shapes live at
`baml_src/cianfhoghlaim/case_studies/students_union_grievances.baml` —
this file is the canonical implementation; the BAML file is the
canonical documentation.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from .clubs_socs_validator import (
    ClubApplication,
    ValidationResult,
    validate_club_application,
)
from .grants_matcher import (
    FundingPot,
    GrantApplication,
    GrantAward,
    match_grant_to_pot,
)
from .complaint_router import (
    Complaint,
    ComplaintRoute,
    route_complaint,
)
from .election_validator import (
    Candidate,
    EligibilityResult,
    validate_candidate_eligibility,
)
from .class_rep_themer import (
    ClassRepReport,
    ThemeAggregation,
    aggregate_class_rep_themes,
)

__all__ = [
    "ClubApplication",
    "ValidationResult",
    "validate_club_application",
    "FundingPot",
    "GrantApplication",
    "GrantAward",
    "match_grant_to_pot",
    "Complaint",
    "ComplaintRoute",
    "route_complaint",
    "Candidate",
    "EligibilityResult",
    "validate_candidate_eligibility",
    "ClassRepReport",
    "ThemeAggregation",
    "aggregate_class_rep_themes",
]
