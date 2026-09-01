"""agents.meaisinfhoghlaim.media_intel — back-compat
re-export shim.

Per 2026-08-25-tuatha-british-isles-mmo-consolidation-v1
(Step 2.2): the 3 media_intel files (the 10-tool ADK agent +
the records helper + this __init__.py) were moved to the
new `tuatha/` independent sub-project at
/Users/cianmacandeisigh/dev/tuatha/agents/media_intel/.

This shim re-exports the canonical symbols from the new
location so any existing parent-repo code that imports from
`agents.meaisinfhoghlaim.media_intel.*` continues to work
during the transition period.

The shim will be removed in a subsequent change after the
new tuatha repo is published.
"""
from __future__ import annotations

# Back-compat re-exports — pull the canonical symbols from the
# new tuatha/ location.
try:
    from tuatha.agents.media_intel.media_descriptor_agent import (  # type: ignore
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
        make_media_descriptor_record,
        media_descriptor_agent,
        media_descriptor_agent_wire,
        run_tool,
        search_descriptors,
        summarise_corpus,
    )

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
except ImportError:
    # The new tuatha/ location may not be importable in all
    # configurations (e.g., when running tests in isolation).
    # In that case the parent's callers should import directly
    # from the new location.
    __all__ = []
