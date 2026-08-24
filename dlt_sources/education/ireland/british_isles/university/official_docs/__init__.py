"""UoG official docs + NUI + Students' Union pipeline package.

The 5 new DLT sources lifted by the
2026-08-23-uog-official-docs-and-nui-superset-v1 change:

  - `uog_official_docs_source` — the UoG official documents surface.
  - `nui_federation_source` — the NUI umbrella (UCD, UCC, MU, UoG + historical QUB).
  - `uog_students_union_source` — the UoG Students' Union.
  - `bitertiary_universities_factory` — generalised British Isles
    factory (QUB + Ulster + the wider universe).
"""

from __future__ import annotations

from .nui_federation_source import (
    NUI_CURRENT_CONSTITUENTS,
    NUI_HISTORICAL_MEMBERS,
    NUI_PORTAL_URLS,
    nui_archive,
    nui_constituent_circulars,
    nui_federation_source,
    nui_members,
)
from .uog_official_docs_source import (
    UOG_OFFICIAL_HOMEPAGES,
    academic_register,
    exam_board_minutes,
    key_pages,
    official_documents,
    uog_official_docs_source,
    url_discovery_log,
)
from .uog_official_docs_vlm import (
    OfficialDocEvalRow,
    UniversityOfficialDocVLMConfig,
    run_official_doc_vlm_eval,
    run_thesis_official_docs_eval,
)
from .uog_students_union_source import (
    UOG_SU_BASE,
    UOG_SU_CANONICAL_POLICIES,
    class_rep_handbooks,
    students_union_documents,
    uog_students_union_source,
)

__all__ = [
    "NUI_CURRENT_CONSTITUENTS",
    "NUI_HISTORICAL_MEMBERS",
    "NUI_PORTAL_URLS",
    "UOG_OFFICIAL_HOMEPAGES",
    "UOG_SU_BASE",
    "UOG_SU_CANONICAL_POLICIES",
    "OfficialDocEvalRow",
    # VLM
    "UniversityOfficialDocVLMConfig",
    "academic_register",
    "class_rep_handbooks",
    "exam_board_minutes",
    "key_pages",
    "nui_archive",
    "nui_constituent_circulars",
    # NUI
    "nui_federation_source",
    "nui_members",
    "official_documents",
    "run_official_doc_vlm_eval",
    "run_thesis_official_docs_eval",
    "students_union_documents",
    # UoG official docs
    "uog_official_docs_source",
    # UoG Students' Union
    "uog_students_union_source",
    "url_discovery_log",
]
