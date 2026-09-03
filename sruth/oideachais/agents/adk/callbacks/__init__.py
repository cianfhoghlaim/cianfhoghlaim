"""
Callback functions for Celtic Education ADK Agents.
"""
from .citation_callbacks import (
    # Celtic language callbacks
    collect_celtic_sources_callback,
    citation_replacement_callback,
    enhance_celtic_source_title,
    classify_celtic_source,
    # British Isles education callbacks
    collect_education_sources_callback,
    format_education_citations_callback,
    enhance_education_source_title,
    classify_education_source,
)

__all__ = [
    # Celtic language
    "collect_celtic_sources_callback",
    "citation_replacement_callback",
    "enhance_celtic_source_title",
    "classify_celtic_source",
    # British Isles education
    "collect_education_sources_callback",
    "format_education_citations_callback",
    "enhance_education_source_title",
    "classify_education_source",
]
