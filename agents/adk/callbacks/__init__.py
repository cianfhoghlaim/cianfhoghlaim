"""
Callback functions for Celtic Education ADK Agents.
"""
from .citation_callbacks import (
    citation_replacement_callback,
    classify_celtic_source,
    classify_education_source,
    # Celtic language callbacks
    collect_celtic_sources_callback,
    # British Isles education callbacks
    collect_education_sources_callback,
    enhance_celtic_source_title,
    enhance_education_source_title,
    format_education_citations_callback,
)

__all__ = [
    "citation_replacement_callback",
    "classify_celtic_source",
    "classify_education_source",
    # Celtic language
    "collect_celtic_sources_callback",
    # British Isles education
    "collect_education_sources_callback",
    "enhance_celtic_source_title",
    "enhance_education_source_title",
    "format_education_citations_callback",
]
