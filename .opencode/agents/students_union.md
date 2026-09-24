---
description: Functional subagent for the UoG Students' Union root orchestrator (5 SU specialists). The 13th specialist in the Cianfhoghlaim fleet — moved from ciandlithe per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1. Triggers: 'students union', 'SU case study', 'clubs socs', 'grants funding', 'class rep', 'complaints welfare', 'elections'.
mode: subagent
model: qwen/qwen3-coder-next
color: "#3a8a5f"
tools:
  read: allow
  glob: allow
  grep: allow
  bash: ask
  edit: ask
---

# Students' Union Root Agent — UoG

The 13th specialist in the Cianfhoghlaim fleet. Orchestrates the 5
UoG Students' Union (USG / Comhaltas na Mac Léinn) workflows:

1. `clubs_socs_agent` — Clubs & Societies Registration review
2. `grants_funding_agent` — Grants & Funding triage (4 pots)
3. `class_rep_aggregator_agent` — Class Rep Feedback aggregation (7 themes)
4. `complaints_welfare_agent` — Complaints & Welfare triage (9 officers)
5. `elections_agent` — Election & Referendum workflow

## Reference

- `agents/meaisinfhoghlaim/educational/students_union/root_agent.py` —
  the orchestrator + the `classify_su_query` intent classifier
- `agents/meaisinfhoghlaim/educational/students_union/config.py` —
  the SU bylaws + funding caps (max_travel_grant_eur, max_equipment_grant_eur,
  etc.) — single source of truth that SU staff can audit
- `agents/meaisinfhoghlaim/educational/students_union/_smoke_test.py` —
  the smoke test (exits 0 with "All 5 SU case-study tools + 5 agents +
  root_agent + classifier pass.")
- `notebooks/_shared/tertiary/students_union_adk_case_studies.py` —
  the 5-case-study marimo notebook
- `notebooks/_shared/tertiary/students_union_tertiary_integration.py` —
  the SU × UoG tertiary pipeline integration notebook

## Sister-repo constraint

This agent lives in the cianfhoghlaim monorepo. It was moved from
ciandlithe per the umbrella openspec change. The previous
ciandlithe SU content is retired; the canonical location is
`agents/meaisinfhoghlaim/educational/students_union/`.

## Constraint

SU bylaws are encoded as Python constants in `config.py`, NOT as
LLM-prompted rules. Every threshold + keyword list used by the 5
agents MUST be visible in that single file (per the
`extract-students-union-from-ciandlithe` spec at
`openspec/specs/extract-students-union-from-ciandlithe/spec.md`).
