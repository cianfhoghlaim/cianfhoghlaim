"""tuatha.agents.media_intel — the Media-Intel package init (refactored per the 2026-08-25-tuatha-british-isles-mmo-consolidation-v1 refactor).

The 10-tool ADK `media_descriptor_agent` + the 2 new files
(`classifier.py` + `explorer.py`). The canonical mount point
for the 5-class source registry + the 7-axis `MediaDescriptor`
schema.

Reference: openspec/changes/2026-08-25-tuatha-british-isles-mmo-consolidation-v1
"""
from __future__ import annotations

from .classifier import classify_medium
from .explorer import (
    cross_medium_consistency,
    per_medium_coverage,
)
from .explorer import (
    summarise_corpus as summarise_corpus_full,
)
from .media_descriptor_agent import (
    TOOL_NAMES,
    TOOLS,
    compare_class_consistency,
    extract_animation_descriptor_tool,
    extract_comic_descriptor_tool,
    extract_gameplay_descriptor_tool,
    extract_official_document_descriptor_tool,
    extract_prose_descriptor_tool,
    list_descriptors_by_class,
    list_sources,
    list_tools,
    media_descriptor_agent,
    media_descriptor_agent_wire,
    run_tool,
    search_descriptors,
    summarise_corpus,
)
from .records import make_media_descriptor_record

__all__ = [
    "TOOLS",
    "TOOL_NAMES",
    "classify_medium",
    "compare_class_consistency",
    "cross_medium_consistency",
    "extract_animation_descriptor_tool",
    "extract_comic_descriptor_tool",
    "extract_gameplay_descriptor_tool",
    "extract_official_document_descriptor_tool",
    "extract_prose_descriptor_tool",
    "list_descriptors_by_class",
    "list_sources",
    "list_tools",
    "make_media_descriptor_record",
    "media_descriptor_agent",
    "media_descriptor_agent_wire",
    "per_medium_coverage",
    "run_tool",
    "search_descriptors",
    "summarise_corpus",
    "summarise_corpus_full",
]
