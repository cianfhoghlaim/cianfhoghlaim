"""Subjects package for Cianfhoghlaim Oideachais.

Bilingual EN/GA manifest of all stages, subjects, and HEIs, plus BAML
context files per stage. See `manifest.py` for the lookup API.
"""
from .manifest import (
    lookup,
    all_stages,
    all_lc_subjects,
    all_hei,
    all_qqi_awards,
)

__all__ = [
    "lookup",
    "all_stages",
    "all_lc_subjects",
    "all_hei",
    "all_qqi_awards",
]
