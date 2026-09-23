"""cianfhoghlaim — Students' Union (USG / Ollscoil na Gaillimhe) Google ADK agents.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

5 specialist agents + 1 root orchestrator covering the 5 most common
Students' Union workflows:

  1. Clubs & Societies Registration (clubs_socs_agent)
  2. Grants & Funding Triage (grants_funding_agent)
  3. Class Rep Feedback Aggregator (class_rep_aggregator_agent)
  4. Complaints & Welfare Triage (complaints_welfare_agent)
  5. Election & Referendum Workflow (elections_agent)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from .root_agent import root_agent, students_union_app

__all__ = [
    "root_agent",
    "students_union_app",
    "clubs_socs_agent",
    "grants_funding_agent",
    "class_rep_aggregator_agent",
    "complaints_welfare_agent",
    "elections_agent",
]
