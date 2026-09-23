"""cianfhoghlaim — Complaints & Welfare triage router.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/, Case Study 4.

Routes incoming student complaints to the correct SU officer per
the SU Bylaws 2025/26. Detects urgent welfare concerns via keyword
list (per the SU Safeguarding Policy) and flags them for the Welfare
Officer regardless of category.

Pure-Python, deterministic, regex-based. The urgency keyword list
lives in `config.py` so it can be tuned without redeploying the agent.

Officer routing:
  ACADEMIC          → Education Officer
  HARASSMENT         → Welfare Officer (URGENT — bypass normal triage)
  SEXUAL_HARASSMENT  → Welfare Officer + President (URGENT)
  ACCOMMODATION      → Welfare Officer
  FINANCIAL          → Welfare Officer + Ents Officer (hardship pathway)
  CLUBS_SOCS         → Clubs & Services Officer
  ELECTORAL          → Returning Officer
  SOCIETAL           → Welfare Officer + Equality Officer
  GENERAL            → President (catch-all)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..config import config as _config


@dataclass(frozen=True)
class Complaint:
    """An incoming complaint / welfare concern."""
    complainant_id_hash: str  # hashed student ID; never store raw
    complaint_text: str
    is_anonymous: bool
    has_already_contacted_su: bool
    submitted_at_iso: str  # for the routing audit trail


@dataclass(frozen=True)
class ComplaintRoute:
    """The result of routing a complaint to an SU officer."""
    primary_officer: str
    secondary_officers: tuple[str, ...] = field(default_factory=tuple)
    category: str = "GENERAL"
    is_urgent: bool = False
    escalation_required: bool = False
    rationale: str = ""


# Keyword → category map. Order matters: first match wins.
_KEYWORD_RULES: tuple[tuple[str, str], ...] = (
    (r"\bsexual\s+harassment\b|\brape\b|\bsexual\s+assault\b", "SEXUAL_HARASSMENT"),
    (r"\bharassment\b|\bbullying\b|\bintimidation\b", "HARASSMENT"),
    (r"\bracism\b|\bracist\b|\bhomophobia\b|\btransphobia\b|\bdiscrimination\b", "SOCIETAL"),
    (r"\baccommodation\b|\bresidences\b|\bhousing\b|\blandlord\b", "ACCOMMODATION"),
    (r"\bhardship\b|\bfees?\b|\bgrant\b|\bsus\b|\bbudget\b", "FINANCIAL"),
    (r"\bexam\b|\bgrade\b|\blecturer\b|\bmodule\b|\bacademic\b|\bplagiarism\b", "ACADEMIC"),
    (r"\bclub\b|\bsociety\b|\bsocs?\b", "CLUBS_SOCS"),
    (r"\belection\b|\bcandidate\b|\bvoting\b|\breferendum\b", "ELECTORAL"),
)


def _detect_urgent(text: str) -> bool:
    """Return True iff the text contains any URGENT-keyword (per SU Safeguarding Policy)."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in config.welfare_urgent_keywords)


def _categorize(text: str) -> str:
    """Return the canonical category for the complaint text."""
    for pattern, category in _KEYWORD_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return category
    return "GENERAL"


def _route(category: str, is_urgent: bool) -> tuple[str, tuple[str, ...]]:
    """Return (primary_officer, secondary_officers) for the category."""
    if category == "SEXUAL_HARASSMENT":
        return ("Welfare Officer", ("President",))
    if category == "HARASSMENT":
        return ("Welfare Officer", ())
    if category == "SOCIETAL":
        return ("Welfare Officer", ("Equality Officer",))
    if category == "ACCOMMODATION":
        return ("Welfare Officer", ())
    if category == "FINANCIAL":
        return ("Welfare Officer", ("Ents Officer",))
    if category == "ACADEMIC":
        return ("Education Officer", ())
    if category == "CLUBS_SOCS":
        return ("Clubs & Services Officer", ())
    if category == "ELECTORAL":
        return ("Returning Officer", ("President",))
    # GENERAL
    if is_urgent:
        return ("President", ("Welfare Officer",))
    return ("President", ())


# Re-export config so callers can introspect without importing both
config = _config


def route_complaint(complaint: Complaint) -> ComplaintRoute:
    """Apply the routing rubric. URGENT keywords always escalate to Welfare."""
    is_urgent = _detect_urgent(complaint.complaint_text)
    category = _categorize(complaint.complaint_text)
    primary, secondary = _route(category, is_urgent)

    # Build rationale (audit trail)
    rationale_parts = [
        f"category={category}",
        f"urgent={is_urgent}",
        f"anonymous={complaint.is_anonymous}",
        f"previously_contacted_su={complaint.has_already_contacted_su}",
    ]
    rationale = "; ".join(rationale_parts)

    return ComplaintRoute(
        primary_officer=primary,
        secondary_officers=secondary,
        category=category,
        is_urgent=is_urgent,
        escalation_required=is_urgent or category in {"SEXUAL_HARASSMENT", "HARASSMENT", "SOCIETAL"},
        rationale=rationale,
    )
