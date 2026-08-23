"""dlt.british_isles.ireland.education.university — University DLT sources.

Hosts the per-university ingestion layers. v1 covers:

  - `university_of_galway_deep.py` — public-website UniversityDeepExtraction
    (course / module / programme / handbook / lecturer pages).
  - `exam_papers/` — authenticated SSO-driven past exam papers,
    BAML extraction, CocoIndex embedding, Cognee cross-archive edges
    (the M.Sc. AI thesis pipeline; see
    openspec/changes/2026-08-23-uog-exam-papers-sso-v1/).
  - `official_docs/` — Stage-0-audited public UoG official docs +
    NUI federation + UoG Students' Union
    (2026-08-23-uog-official-docs-and-nui-superset-v1/).
"""
from __future__ import annotations

__all__: list[str] = ["exam_papers", "official_docs"]
