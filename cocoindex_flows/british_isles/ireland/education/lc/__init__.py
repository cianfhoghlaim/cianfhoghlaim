"""cocoindex_flows.british_isles.ireland.education.lc
-- the 6 Irish Leaving Certificate (NCCA) per-subject CocoIndex
v1 Apps (BIEP v3 umbrella).

The 6 modules in this package — `mathematics.py`,
`chemistry.py`, `geography.py`, `english.py`, `gaeilge.py`,
`computer_science.py` — together cover the 12 BIEP v3
Ireland-LC cohorts (6 subjects × 2 languages, minus 1 for
Gaeilge which is Irish-only).

Each module follows the canonical BIEP v3 contract:
- R1: imports `shared_lifespan` + `LANCE_DB` + `EMBEDDER` from
  `....._shared._lifespan`
- R3: declares `app = coco.App(coco.AppConfig(name=...))` at
  module scope (R3 enforced by `cocoindex_v1_conformance.py`)
- R4: at least one `@coco.fn(...)` decorator present

The 6 modules are validated by `tests/biep_parity_lc/test_<subject>.py`,
which exercises the full load → embed → store → query pipeline
against a small per-subject fixture (3 rows). See
`_shared.py` for the BAML fallback + embedder substitute
helpers used by these tests.
"""
from ._shared import (
    LC_SUBJECTS,
    LCSubjectSpec,
    SUBJECT_SLUGS,
    baml_available,
    build_subject_fixture,
    chunk_text,
    get_subject_spec,
    iter_subjects,
    pure_python_embed,
    python_baml_fallback_extract,
)

__all__ = [
    "LC_SUBJECTS",
    "LCSubjectSpec",
    "SUBJECT_SLUGS",
    "baml_available",
    "build_subject_fixture",
    "chunk_text",
    "get_subject_spec",
    "iter_subjects",
    "pure_python_embed",
    "python_baml_fallback_extract",
]
