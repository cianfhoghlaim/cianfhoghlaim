"""Shared sub-agent: SourceCiter.

Always returns a NCCA/SEC/CAO/HEI source URL alongside every fact.
"""
from __future__ import annotations

from typing import Literal


class SourceCiter:
    """Generates a citation chip for a given fact."""

    def cite(self, fact: str, *, source_type: Literal["ncca", "sec", "cao", "hei", "aistear", "qqi"],
             url: str, document_title: str | None = None) -> dict:
        return {
            "fact": fact,
            "source_type": source_type,
            "url": url,
            "document_title": document_title,
        }
