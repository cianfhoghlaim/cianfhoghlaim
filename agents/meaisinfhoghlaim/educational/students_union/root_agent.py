"""cianfhoghlaim — Students' Union root orchestrator (umbrella for the 5 case studies).

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

The root agent routes incoming SU queries to the correct specialist
based on the intent classifier at the bottom of this file. The 5
sub_agents cover the 5 case studies (clubs/socs, grants, class rep,
complaints, elections).

This is the canonical "Google ADK + 5 sub_agents" pattern; the
marimo notebook at `notebooks/students_union_adk_case_studies.py`
showcases each case study end-to-end.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from __future__ import annotations

import datetime

from google.adk.agents import LlmAgent
from google.adk.apps.app import App

from .class_rep_aggregator_agent import class_rep_aggregator_agent
from .clubs_socs_agent import clubs_socs_agent
from .complaints_welfare_agent import complaints_welfare_agent
from .config import config
from .elections_agent import elections_agent
from .grants_funding_agent import grants_funding_agent


# ---------------------------------------------------------------------------
# Root orchestrator
# ---------------------------------------------------------------------------


root_agent = LlmAgent(
    name="students_union_root_agent",
    model=config.default_model,
    # Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/
    # Pillar 2 collaborative mode (parallel invocation + synthesis).
    mode="single_turn",
    description=(
        "University of Galway Students' Union root agent — routes "
        "queries to the correct specialist (clubs/socs, grants, class "
        "rep, complaints, elections). Pillar 2 collaborative mode fans the "
        "relevant subset of the 5 specialists out in parallel and synthesizes."
    ),
    instruction=f"""
You are the root orchestrator for the University of Galway Students'
Union ({config.su_name_english} / {config.su_name_irish} /
"Comhaltas na Mac Léinn"). You coordinate 5 specialist agents that
cover the most common SU workflows.

**YOUR ROLE:**
Classify the incoming query + route to the appropriate specialist
agent. Synthesise a unified response if multiple specialists are
involved (rare).

**SPECIALIST AGENTS:**

  1. **clubs_socs_agent** — Clubs & Societies registration review
     (validate applications against SU bylaws)
     Use for: "I want to start a society", "review my club
     application", "is my application complete?"

  2. **grants_funding_agent** — Grants & Funding triage (match
     applications to the 4 SU funding pots)
     Use for: "apply for a travel grant", "funding for our event",
     "how much can my society claim?"

  3. **class_rep_aggregator_agent** — Class Rep feedback
     aggregation (theme extraction across reports)
     Use for: "summarise class rep feedback", "what are the main
     concerns this semester?"

  4. **complaints_welfare_agent** — Complaints & Welfare triage
     (route to the correct SU officer)
     Use for: "I want to make a complaint", "I have a welfare
     concern", "who do I report X to?"

  5. **elections_agent** — Election & Referendum workflow
     (candidate eligibility validation)
     Use for: "I want to run for sabbatical president", "validate my
     candidacy", "how many nominators do I need?"

**WORKFLOW:**

  1. Read the user's query carefully.
  2. Run the `classify_su_query` function (defined below) to determine
     the intent.
  3. Route to the matching specialist agent.
  4. Optionally, for multi-intent queries (e.g. "I'm starting a new
     society AND want to apply for a starter grant"), invoke both
     specialists and synthesise the responses.

**LANGUAGE:**
  - The SU is bilingual. The user may write in English or in Irish
    (Gaeilge). Recognise both.
  - Your output should be in the same language as the user's query
    unless they explicitly ask for English.

**TONE:**
  - Student-friendly. SU staff are approachable; mirror that tone.
  - Procedural + concrete (specific Euro amounts, specific dates,
    specific officer names).

**TIME:**
  - Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
  - Current academic year: {config.su_academic_year}
  - Constitution version applied: {config.su_constitution_version}
""",
    sub_agents=[
        clubs_socs_agent,
        grants_funding_agent,
        class_rep_aggregator_agent,
        complaints_welfare_agent,
        elections_agent,
    ],
    output_key="students_union_response",
)


# ---------------------------------------------------------------------------
# ADK App wrapper
# ---------------------------------------------------------------------------


students_union_app = App(
    root_agent=root_agent,
    name="students_union_orchestrator",
)


# ---------------------------------------------------------------------------
# Intent classifier (used by the root agent + by the marimo notebook
# to demonstrate the routing decision independently of the LLM)
# ---------------------------------------------------------------------------


def classify_su_query(query: str) -> str:
    """Classify the query to determine the correct specialist agent.

    Returns one of: "clubs_socs" | "grants" | "class_rep" |
    "complaints" | "elections" | "ambiguous".
    """
    q = query.lower()

    # Clubs & Societies
    if any(kw in q for kw in [
        "club", "society", "soc ", "socs", "affiliate",
        "registration form", "start a society",
    ]):
        return "clubs_socs"

    # Grants & Funding
    if any(kw in q for kw in [
        "grant", "funding", "budget", "subsid", "€", "eur",
        "travel grant", "equipment grant", "welfare grant", "event grant",
    ]):
        return "grants"

    # Class Rep
    if any(kw in q for kw in [
        "class rep", "rep report", "feedback", "module review",
        "lecturer concerns", "assessment feedback", "survey",
    ]):
        return "class_rep"

    # Complaints & Welfare
    if any(kw in q for kw in [
        "complaint", "complain", "harassment", "discrimination",
        "hardship", "welfare concern", "safeguard", "report",
        "bullying", "issue with",
    ]):
        return "complaints"

    # Elections
    if any(kw in q for kw in [
        "election", "candidate", "nominat", "sabbatical", "sabbat",
        "referendum", "vote", "ballot", "president", "vp ",
    ]):
        return "elections"

    return "ambiguous"


__all__ = [
    "root_agent",
    "students_union_app",
    "classify_su_query",
    "clubs_socs_agent",
    "grants_funding_agent",
    "class_rep_aggregator_agent",
    "complaints_welfare_agent",
    "elections_agent",
]
