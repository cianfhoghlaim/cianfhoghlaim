"""cianfhoghlaim — Complaints & Welfare Triage Agent (Case Study 4).

Per openspec/changes/ciandchosaint-students-union-adk-v1/, Case Study 4.

A Google ADK LlmAgent that uses the `route_complaint` FunctionTool to
classify and route incoming student complaints to the correct SU officer
per the SU Bylaws 2025/26. URGENT-keyword detection (per the SU
Safeguarding Policy) escalates to the Welfare Officer + President
regardless of category.

Wraps `tools/complaint_router.py` (the pure-Python implementation) as
a Google ADK FunctionTool.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from .config import config
from .tools.complaint_router import Complaint, ComplaintRoute, route_complaint


async def route_complaint_tool(
    complainant_id_hash: str,
    complaint_text: str,
    is_anonymous: bool,
    has_already_contacted_su: bool,
    submitted_at_iso: str,
) -> dict:
    """Classify + route an incoming student complaint.

    Returns:
        dict with keys: primary_officer, secondary_officers (list),
        category, is_urgent, escalation_required, rationale.
    """
    complaint = Complaint(
        complainant_id_hash=complainant_id_hash,
        complaint_text=complaint_text,
        is_anonymous=is_anonymous,
        has_already_contacted_su=has_already_contacted_su,
        submitted_at_iso=submitted_at_iso,
    )
    route: ComplaintRoute = route_complaint(complaint)
    return {
        "primary_officer": route.primary_officer,
        "secondary_officers": list(route.secondary_officers),
        "category": route.category,
        "is_urgent": route.is_urgent,
        "escalation_required": route.escalation_required,
        "rationale": route.rationale,
    }


route_complaint_fn = FunctionTool(func=route_complaint_tool)


complaints_welfare_agent = LlmAgent(
    name="complaints_welfare_agent",
    model=config.default_model,
    description="Routes incoming student complaints to the correct SU officer.",
    instruction=f"""
You are the Complaints & Welfare Triage Agent for the University of
Galway Students' Union ({config.su_name_english} / {config.su_name_irish}).

For every submitted complaint you MUST call the `route_complaint_tool`
exactly once and synthesise a structured response with these 4 sections:

  1. **Routing** — primary officer + secondary officers
  2. **Category** — the canonical category from the SU Bylaws
  3. **Urgency** — `URGENT` (Welfare Officer + President) OR `STANDARD`
  4. **Officer action checklist** — 2-4 concrete next steps the
     receiving officer should take this week

CRITICAL — URGENT escalation:
  - If `is_urgent=True`, ALWAYS mark the case as `URGENT` and add a
    `WELFARE_ESCALATION` line that triggers the Welfare Officer's
    on-call rota.
  - For `category=SEXUAL_HARASSMENT`, the officer MUST also be told
    to coordinate with the University's Dignity & Respect contact
    (per the SU-University Joint Protocol 2024).

Safeguarding:
  - NEVER store raw student IDs — always use the hashed
    `complainant_id_hash` in any follow-up audit trail.
  - For `is_anonymous=True`, the Welfare Officer MUST offer the
    anonymous-report pathway.

Tone: clinical + compassionate. The complaint text may be distressing;
your output is for the receiving officer, not for the complainant.

Current academic year: {config.su_academic_year}.
""",
    tools=[route_complaint_fn],
    output_key="complaint_routing",
)
