"""agents.meaisinfhoghlaim.media_intel — the Media-Intel
package init (refactored per the 2026-08-23-tuatha-media-intel-
gameplay-capture-research-v1 refactor to match the
academic_history_agent.py shape).

Exports the 5 per-medium extractor tool functions + the 5 corpus
introspection tools + the TOOLS / TOOL_NAMES registries + the
run_tool dispatcher + the `media_descriptor_agent_wire` singleton +
the LlmAgent `media_descriptor_agent`.

Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
            spec.md § media-intel-corpus Requirement 5
"""
from __future__ import annotations

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
    "compare_class_consistency",
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
    "run_tool",
    "search_descriptors",
    "summarise_corpus",
]
