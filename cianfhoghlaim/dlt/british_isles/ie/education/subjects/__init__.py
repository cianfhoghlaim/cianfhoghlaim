"""Subjects package for Cianfhoghlaim Oideachais.

Bilingual EN/GA manifest of all stages, subjects, and HEIs, plus BAML
context files per stage. See `manifest.py` for the lookup API.
"""
from .manifest import (
    all_hei,
    all_lc_subjects,
    all_qqi_awards,
    all_stages,
    lookup,
)

__all__ = [
    "all_hei",
    "all_lc_subjects",
    "all_qqi_awards",
    "all_stages",
    "lookup",
]
