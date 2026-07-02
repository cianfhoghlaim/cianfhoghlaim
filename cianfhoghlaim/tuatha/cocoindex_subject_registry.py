"""Per-subject cocoindex embeddings registry.

Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md
T6.13, this module re-exports the 8 NCCA subject cocoindex v1 Apps
for the new deployment. The existing 8 apps at
`cianfhoghlaim.cocoindex.<subject>_embedding.py` are the canonical
homes.

The 8 subjects are:
  - mathematics
  - applied_mathematics
  - chemistry
  - geography
  - history
  - english
  - gaeilge
  - computer_science
"""

from __future__ import annotations

from typing import Any


SUBJECT_COCOINDEX_APPS = {
    "mathematics": "cianfhoghlaim.cocoindex.mathematics_embedding",
    "applied_mathematics": "cianfhoghlaim.cocoindex.applied_mathematics_embedding",
    "chemistry": "cianfhoghlaim.cocoindex.chemistry_embedding",
    "geography": "cianfhoghlaim.cocoindex.geography_embedding",
    "history": "cianfhoghlaim.cocoindex.history_embedding",
    "english": "cianfhoghlaim.cocoindex.english_embedding",
    "gaeilge": "cianfhoghlaim.cocoindex.gaeilge_embedding",
    "computer_science": "cianfhoghlaim.cocoindex.computer_science_embedding",
}


SUBJECT_ROOT_PDFS_TABLE = {
    "key_competencies": "oideachais.lc.root.key_competencies",
    "online_learning": "oideachais.lc.root.online_learning",
    "certification": "oideachais.lc.root.certification",
    "scr_advisory": "oideachais.lc.root.scr_advisory",
    "programme_statement": "oideachais.lc.root.programme_statement",
}


CROSS_SUBJECT_TABLE = "oideachais.lc.cross_subject.competencies"


def get_subject_table(subject: str, level: str, language: str) -> str:
    """Return the LanceDB table name for the given NCCA subject + level + language."""
    return f"oideachais.lc.{subject}.{level}_{language}"


def list_subject_cocoindex_apps() -> list[str]:
    """List the 8 NCCA subject cocoindex v1 App module paths."""
    return list(SUBJECT_COCOINDEX_APPS.values())


__all__ = [
    "SUBJECT_COCOINDEX_APPS",
    "SUBJECT_ROOT_PDFS_TABLE",
    "CROSS_SUBJECT_TABLE",
    "get_subject_table",
    "list_subject_cocoindex_apps",
]