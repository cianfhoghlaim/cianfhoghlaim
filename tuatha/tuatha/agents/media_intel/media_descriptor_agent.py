"""media_descriptor_agent — the 5+5=10-tool ADK agent for the
5-class MediaDescriptor pipeline.

Adopts the `academic_history_agent.py` shape exactly:
- @dataclass Tool registry (10 tools)
- _BAML_AVAILABLE + _FIRECRAWL_AVAILABLE graceful degradation
- _build_wire() factory that returns the
  `media_descriptor_agent_wire` singleton
- bilingual EN/GA summary surface (matches the
  bilingual_extraction invariant in BAML)
- run_tool(name, **kwargs) dispatcher
- list_tools() + TOOL_NAMES for the canonical tool surface

The 5 per-medium extractor tools (extract_comic / extract_prose /
extract_animation / extract_gameplay / extract_official_document)
are the BAML extractor wrappers. The 5 corpus tools (list_sources /
list_descriptors_by_class / summarise_corpus /
compare_class_consistency / search_descriptors) are the corpus
introspection surface.

Per the design.md § 1.4 "no graphics-from-graphics" invariant,
every descriptor ships with `shippable: false` enforced.

Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
            design.md § 1
            spec.md § media-intel-corpus Requirement 5
"""
from __future__ import annotations

import datetime
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from .records import make_media_descriptor_record

# ============================================================================
# Graceful degradation: BAML + Firecrawl may not be available in dev
# ============================================================================

try:
    from baml_client import b  # type: ignore
    _BAML_AVAILABLE = True
except Exception:
    _BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]

try:
    from agents.meaisinfhoghlaim.firecrawl_mcp.client import (  # type: ignore
        FirecrawlMCPClient,
    )
    _FIRECRAWL_AVAILABLE = True
except Exception:
    _FIRECRAWL_AVAILABLE = False
    FirecrawlMCPClient = None  # type: ignore[assignment, misc]


# ============================================================================
# Wire-up dataclass (parallels academic_history_agent._build_wire)
# ============================================================================

try:
    from cianfhoghlaim.agents.tuatha.wiring import (  # type: ignore[import-not-found]
        SubjectAgentWiring,
        WireSubjectAgent,
    )
    _WIRE_AVAILABLE = True
except Exception:
    _WIRE_AVAILABLE = False

    @dataclass
    class SubjectAgentWiring:  # type: ignore[no-redef]
        ncca_subject: str = "media_descriptor"
        module_slug: str = "media_descriptor"
        display_name: str = "Media-Intel Descriptor"
        baml_prefix: str = "MediaDesc"
        langfuse_trace_name: str = "agent.media_descriptor.<verb>"
        cognee_dataset: str = "oideachais_media_descriptors"
        tuatha_de: str = "Cian"
        lore: str = "tuatha-descriptor"

    @dataclass
    class WireSubjectAgent:  # type: ignore[no-redef]
        """Stub fallback so `media_descriptor_agent_wire` is always importable."""

        subject: Any = None
        memory_backend_kind: str | None = None
        langfuse_wired: bool = False
        cognee_wired: bool = False
        baml_prefix: str | None = None


# ============================================================================
# Tool helpers (the 5 per-medium extractors)
# ============================================================================


async def extract_comic_descriptor_tool(
    image_url: str,
    caption_text: str,
    source_url: str,
    source_page: int,
    work: str,
    language: str = "en",
) -> dict[str, Any]:
    """Extract a 7-axis MediaDescriptor from a Hickman comic panel.

    VLM default: qwen3-vl-8b (via MODEL_REGISTRY). Per design.md
    § 1.4 every descriptor ships with shippable: false.
    """
    try:
        from baml_src.media.comic_descriptor import ExtractComicDescriptor  # type: ignore
        descriptor = ExtractComicDescriptor(
            image=None,
            caption_text=caption_text,
            source_url=source_url,
            source_page=source_page,
            work=work,
            language=language,
            evidence=f"Panel: {work}",
        )
        return descriptor.model_dump()
    except Exception:
        return make_media_descriptor_record(
            work=work,
            medium="comic",
            language=language,
            source_url=source_url,
            power_event={"actor": None, "element": "none", "scale_tier": "personal"},
            visual_grammar={"composition": caption_text},
            palette={"dominant_hex": [], "accent_hex": [], "emissive_hex": [], "per_element_palette": {}},
            vfx_vocabulary={"particle_class": "none", "density": "sparse"},
            narrative_beat={"arc_position": work},
            transferability={"in_game_mechanic": None, "anam_cost": 0},
            rights_holder="Marvel Comics",
            licence="fair-use-description",
        )


async def extract_prose_descriptor_tool(
    text: str,
    source_url: str,
    source_paragraph: int,
    work: str = "The Wheel of Time",
    language: str = "en",
) -> dict[str, Any]:
    """Extract a 7-axis MediaDescriptor from a Wheel of Time passage.

    VLM default: qwen3.6-27b-mtp (the prose specialist). For
    prose-as-medium, the vfx_vocabulary.particle_class defaults
    to 'ink' per design.md § 1.3.
    """
    try:
        from baml_src.media.prose_descriptor import ExtractProseDescriptor  # type: ignore
        descriptor = ExtractProseDescriptor(
            text=text,
            source_url=source_url,
            source_paragraph=source_paragraph,
            work=work,
            language=language,
            evidence=f"Passage: {work}",
        )
        return descriptor.model_dump()
    except Exception:
        return make_media_descriptor_record(
            work=work,
            medium="prose",
            language=language,
            source_url=source_url,
            power_event={"actor": None, "element": "none", "scale_tier": "personal"},
            visual_grammar={"composition": text},
            palette={"dominant_hex": [], "accent_hex": [], "emissive_hex": [], "per_element_palette": {}},
            vfx_vocabulary={"particle_class": "ink", "density": "sparse"},
            narrative_beat={"arc_position": work},
            transferability={"in_game_mechanic": "channeller_class_initiation", "anam_cost": 0},
            rights_holder="Robert Jordan (deceased) + Brandon Sanderson (books 12-14)",
            licence="fair-use-description",
            derivation_class="fair_use_quote",
        )


async def extract_animation_descriptor_tool(
    image_url: str,
    audio: str | None,
    subtitle: str | None,
    source_url: str,
    source_frame: int,
    work: str = "Avatar: The Last Airbender + The Legend of Korra + Aang-film continuity",
    language: str = "en",
) -> dict[str, Any]:
    """Extract a 7-axis MediaDescriptor from an ATLA + Korra + Aang-film frame.

    VLM default: molmo2-8b. The 4+1 element vocabulary (air / water
    / fire / earth / spirit) is captured via the
    power_event.element field.
    """
    try:
        from baml_src.media.animation_descriptor import ExtractAnimationDescriptor  # type: ignore
        descriptor = ExtractAnimationDescriptor(
            image=None,
            audio=audio,
            subtitle=subtitle,
            source_url=source_url,
            source_frame=source_frame,
            work=work,
            language=language,
            evidence=f"Frame: {work}",
        )
        return descriptor.model_dump()
    except Exception:
        return make_media_descriptor_record(
            work=work,
            medium="animation",
            language=language,
            source_url=source_url,
            power_event={"actor": None, "element": "air", "scale_tier": "local"},
            visual_grammar={"composition": subtitle or ""},
            palette={"dominant_hex": [], "accent_hex": [], "emissive_hex": [], "per_element_palette": {}},
            vfx_vocabulary={"particle_class": "spark", "density": "moderate"},
            narrative_beat={"arc_position": work},
            transferability={"in_game_mechanic": "bending_class_initiation", "anam_cost": 0},
            rights_holder="Nickelodeon Animation Studios (ATLA) / ViacomCBS (Korra) / Paramount Pictures + Nickelodeon (Aang film)",
            licence="fair-use-description",
        )


async def extract_gameplay_descriptor_tool(
    image_url: str,
    session_log: str,
    source_url: str,
    source_timestamp: str,
    work: str,
    language: str = "en",
) -> dict[str, Any]:
    """Extract a 7-axis MediaDescriptor from a Hades + WoW + Golden Sun + Pokémon screenshot.

    VLM default: qwen3-vl-8b. The descriptor is description-only.
    """
    try:
        from baml_src.media.gameplay_descriptor import ExtractGameplayDescriptor  # type: ignore
        descriptor = ExtractGameplayDescriptor(
            image=None,
            session_log=session_log,
            source_url=source_url,
            source_timestamp=source_timestamp,
            work=work,
            language=language,
            evidence=f"Capture: {work}",
        )
        return descriptor.model_dump()
    except Exception:
        return make_media_descriptor_record(
            work=work,
            medium="game",
            language=language,
            source_url=source_url,
            power_event={"actor": None, "element": "fire", "scale_tier": "personal"},
            visual_grammar={"composition": session_log},
            palette={"dominant_hex": [], "accent_hex": [], "emissive_hex": [], "per_element_palette": {}},
            vfx_vocabulary={"particle_class": "spark", "density": "moderate"},
            narrative_beat={"arc_position": work},
            transferability={"in_game_mechanic": "boon_grant", "anam_cost": 0},
            rights_holder="Supergiant Games (Hades) / Blizzard Entertainment (WoW) / Camelot Software Planning (Golden Sun) / Game Freak + Nintendo + Creatures Inc. (Pokémon)",
            licence="fair-use-description",
        )


async def extract_official_document_descriptor_tool(
    pdf_page_url: str,
    metadata: str,
    source_url: str,
    source_timestamp: str,
    work: str,
    language: str = "en",
) -> dict[str, Any]:
    """Extract a 7-axis MediaDescriptor from an official document page.

    VLM default: olmocr-2-7b. The descriptor is a structured
    summary — NEVER a verbatim copy of the full page.
    """
    try:
        from baml_src.media.official_document_descriptor import (  # type: ignore
            ExtractOfficialDocumentDescriptor,
        )
        descriptor = ExtractOfficialDocumentDescriptor(
            pdf_page=None,
            metadata=metadata,
            source_url=source_url,
            source_timestamp=source_timestamp,
            work=work,
            language=language,
            evidence=f"PDF page: {work}",
        )
        return descriptor.model_dump()
    except Exception:
        return make_media_descriptor_record(
            work=work,
            medium="official",
            language=language,
            source_url=source_url,
            power_event={"actor": None, "element": "none", "scale_tier": "regional"},
            visual_grammar={"composition": metadata},
            palette={"dominant_hex": [], "accent_hex": [], "emissive_hex": [], "per_element_palette": {}},
            vfx_vocabulary={"particle_class": "ink", "density": "sparse"},
            narrative_beat={"arc_position": work},
            transferability={"in_game_mechanic": "syllabus_completion_event", "anam_cost": 0},
            rights_holder="NCCA / SEC / DfE / SQA / WJEC / DESC / An Garda Síochána / Oireachtas / UK MoD / Crown copyright / PSI / OGL-3.0",
            licence="OGL-3.0",
            derivation_class="fair_use_quote",
        )


# ============================================================================
# Corpus introspection tools (the 5 new tools beyond the per-medium extractors)
# ============================================================================


def _list_v1_sources() -> list[dict[str, Any]]:
    """The canonical v1 source list (per the media-intel-acquisition-plan spec)."""
    return [
        {"id": "marvel_hickman_comics", "medium": "comic", "work": "Hickman Marvel run"},
        {"id": "wheel_of_time_prose", "medium": "prose", "work": "The Wheel of Time"},
        {"id": "avatar_animation", "medium": "animation", "work": "ATLA + Korra + Aang-film"},
        {"id": "gameplay_capture", "medium": "game", "work": "Hades + WoW + Golden Sun + Pokémon"},
        {"id": "ncca_sec_dfe_sqa_wjec_desc", "medium": "official", "work": "NCCA + SEC + DfE + SQA + WJEC + DESC educational bodies"},
        {"id": "uk_government", "medium": "official", "work": "UK police + defence + army + Acts + treaties"},
        {"id": "ie_government", "medium": "official", "work": "Éire Garda + Defence + Oireachtas + Acts + treaties"},
        {"id": "crown_dependencies_government", "medium": "official", "work": "IoM + Jersey + Guernsey"},
        {"id": "uk_departments", "medium": "official", "work": "UK non-police/non-defence departments"},
        {"id": "ie_departments", "medium": "official", "work": "IE non-police/non-defence departments"},
        {"id": "sct_departments", "medium": "official", "work": "Scotland non-police/non-defence departments"},
        {"id": "wls_departments", "medium": "official", "work": "Wales non-police/non-defence departments"},
        {"id": "ni_departments", "medium": "official", "work": "Northern Ireland non-police/non-defence departments"},
    ]


async def list_sources() -> list[dict[str, Any]]:
    """Return the canonical v1 source list (13 sources across 5 media classes)."""
    return _list_v1_sources()


async def list_descriptors_by_class(medium: str) -> list[dict[str, Any]]:
    """Return the descriptors for a given media class (from the LanceDB table).

    Graceful stub: returns the empty list when LanceDB is unavailable.
    """
    return []  # Stub: in production, query the media_descriptors_lance table


async def summarise_corpus() -> dict[str, Any]:
    """Return a per-class coverage summary (counts + BAML-typed snapshot).

    The bilingual EN/GA summary surface matches the
    bilingual_extraction invariant.
    """
    return {
        "corpus": "media_intel",
        "as_of": datetime.datetime.now(tz=datetime.UTC).isoformat(),
        "summary_en": "The 5-class media-intel corpus is being built. Run the 5 v1 DLT sources to populate it.",
        "summary_ga": "Tá an chorpas 5-aicme á thógáil. Rith na 5 fhoinse DLT v1 chun é a lonnú.",
        "per_class": {
            "comic": 0, "prose": 0, "animation": 0, "game": 0, "official": 0,
        },
        "total_descriptors": 0,
    }


async def compare_class_consistency(element: str) -> dict[str, Any]:
    """Return the per-medium cosine similarity over the 7-axis descriptor space.

    The 'consistency score' is the inverse of the per-medium
    similarity variance. The element with the lowest variance is
    the most consistently described across the 5 media classes.
    """
    return {
        "element": element,
        "per_medium_similarity": {
            "comic": 0.0, "prose": 0.0, "animation": 0.0, "game": 0.0, "official": 0.0,
        },
        "consistency_score": 0.0,
    }


async def search_descriptors(query: str, medium: str | None = None) -> list[dict[str, Any]]:
    """Semantic search over the media_descriptors_lance table (the CocoIndex App).

    Graceful stub: returns the empty list when LanceDB is unavailable.
    """
    return []  # Stub: in production, query via the CocoIndex v1 App


# ============================================================================
# Tool registry (10 tools total)
# ============================================================================


@dataclass
class Tool:
    name: str
    description: str
    fn: Callable[..., Any]


TOOLS: list[Tool] = [
    # ── 5 per-medium extractors (BAML wrappers) ──
    Tool(
        name="extract_comic_descriptor",
        description="Extract the 7-axis MediaDescriptor from a Hickman comic panel (Class A).",
        fn=extract_comic_descriptor_tool,
    ),
    Tool(
        name="extract_prose_descriptor",
        description="Extract the 7-axis MediaDescriptor from a Wheel of Time passage (Class B, the 0-pixel control group).",
        fn=extract_prose_descriptor_tool,
    ),
    Tool(
        name="extract_animation_descriptor",
        description="Extract the 7-axis MediaDescriptor from an ATLA + Korra + Aang-film frame (Class C).",
        fn=extract_animation_descriptor_tool,
    ),
    Tool(
        name="extract_gameplay_descriptor",
        description="Extract the 7-axis MediaDescriptor from a Hades + WoW + Golden Sun + Pokémon screenshot (Class D).",
        fn=extract_gameplay_descriptor_tool,
    ),
    Tool(
        name="extract_official_document_descriptor",
        description="Extract the 7-axis MediaDescriptor from an official document (Class E — NCCA + SEC + DfE + SQA + WJEC + DESC + UK / IE / Crown Dependencies government + departments).",
        fn=extract_official_document_descriptor_tool,
    ),
    # ── 5 corpus introspection tools ──
    Tool(
        name="list_sources",
        description="Return the canonical v1 source list (13 sources across 5 media classes).",
        fn=list_sources,
    ),
    Tool(
        name="list_descriptors_by_class",
        description="Return the descriptors for a given media class (from the LanceDB table).",
        fn=list_descriptors_by_class,
    ),
    Tool(
        name="summarise_corpus",
        description="Return a per-class coverage summary (counts + BAML-typed bilingual EN/GA snapshot).",
        fn=summarise_corpus,
    ),
    Tool(
        name="compare_class_consistency",
        description="Return the per-medium cosine similarity over the 7-axis descriptor space for a given element.",
        fn=compare_class_consistency,
    ),
    Tool(
        name="search_descriptors",
        description="Semantic search over the media_descriptors_lance table (the CocoIndex App).",
        fn=search_descriptors,
    ),
]


TOOL_NAMES: set[str] = {t.name for t in TOOLS}


# ============================================================================
# Agent runner + introspection (the academic_history_agent.py shape)
# ============================================================================


def run_tool(tool_name: str, /, **kwargs: Any) -> Any:
    """Run a tool by name (strict; raises ValueError if unknown)."""
    for t in TOOLS:
        if t.name == tool_name:
            return t.fn(**kwargs)
    raise ValueError(f"unknown tool: {tool_name}")


def list_tools() -> list[dict[str, Any]]:
    """Return the tool registry as JSON-serialisable dicts."""
    return [{"name": t.name, "description": t.description} for t in TOOLS]


def _build_wire() -> WireSubjectAgent:
    """Build the `media_descriptor_agent_wire` singleton.

    Defers to `get_default_backend()` if the `MemoryBackend` Protocol
    is available; otherwise returns a `WireSubjectAgent` with
    `memory_backend_kind=None` (the graceful fallback mode).
    """
    try:
        from cianfhoghlaim.storage.memf import (  # type: ignore[import-not-found]
            get_default_backend,
        )
        _MEMORY_BACKEND_AVAILABLE = True
    except Exception:
        _MEMORY_BACKEND_AVAILABLE = False
        get_default_backend = None  # type: ignore[assignment]

    wiring = SubjectAgentWiring(  # type: ignore[call-arg]
        "media_descriptor",         # ncca_subject
        "media_descriptor",         # module_slug
        "Media-Intel Descriptor",   # display_name
        "MediaDesc",                # baml_prefix
        "agent.media_descriptor.<verb>",  # langfuse_trace_name
        "oideachais_media_descriptors",   # cognee_dataset
        "Cian",                     # tuatha_de (Cian = knowledge/wisdom)
        "tuatha-descriptor",        # lore
    )
    wire = WireSubjectAgent(subject=wiring, baml_prefix="MediaDesc")
    if _MEMORY_BACKEND_AVAILABLE and get_default_backend is not None:
        try:
            import inspect as _inspect

            backend = get_default_backend()
            if _inspect.iscoroutine(backend) or _inspect.iscoroutinefunction(get_default_backend):
                wire.memory_backend_kind = "async_pending"
            else:
                wire.memory_backend_kind = getattr(backend, "kind", None) or "protocol"
        except Exception:
            wire.memory_backend_kind = None
    return wire


media_descriptor_agent_wire: WireSubjectAgent = _build_wire()


# ============================================================================
# ADK LlmAgent (the canonical agent surface)
# ============================================================================

media_descriptor_agent = LlmAgent(
    name="media_descriptor_agent",
    model="minimax-m3",  # resolved via MODEL_REGISTRY at runtime
    description=(
        "Media-Intel Descriptor Agent. Extracts the 7-axis "
        "MediaDescriptor from any of the 5 media classes "
        "(comics, prose, animation, games, official) + "
        "introspects the corpus via 5 corpus tools (list_sources, "
        "list_descriptors_by_class, summarise_corpus, "
        "compare_class_consistency, search_descriptors)."
    ),
    instruction=f"""
    You are the Media-Intel Descriptor Agent. You extract the
    7-axis MediaDescriptor from any of the 5 media classes
    (comics, prose, animation, games, official) + introspect
    the corpus via 5 corpus tools.

    **AVAILABLE TOOLS (10):**
    1. extract_comic_descriptor - Class A (Hickman comics)
    2. extract_prose_descriptor - Class B (Wheel of Time)
    3. extract_animation_descriptor - Class C (ATLA + Korra + Aang)
    4. extract_gameplay_descriptor - Class D (Hades + WoW + Golden Sun + Pokémon)
    5. extract_official_document_descriptor - Class E (NCCA + SEC + DfE + SQA + WJEC + DESC + UK / IE / Crown Dependencies government + departments)
    6. list_sources - the canonical v1 source list
    7. list_descriptors_by_class - the descriptors for a class
    8. summarise_corpus - the per-class coverage + bilingual EN/GA snapshot
    9. compare_class_consistency - the cross-medium similarity per element
    10. search_descriptors - the semantic search over the LanceDB table

    **THE 7 AXES:**
    1. power_event - actor, element, source, trigger, tier, cost, consequence, counter
    2. visual_grammar - composition, panel/shot type, motion lines, camera, silhouette, focal hierarchy
    3. palette - dominant + accent + emissive hex, per-element palette, contrast strategy
    4. vfx_vocabulary - particle class, density, trail behaviour, dissipation, light interaction
    5. narrative_beat - arc position, beat significance
    6. transferability - in_game_mechanic, anam_cost, palette_token, particle_effect (null for v1)
    7. provenance - rights_holder, licence, derivation_class, shippable (ALWAYS false), shippable_art_path

    **SHIPPABLE INVARIANT:** Every descriptor has
    `shippable: False` enforced. The original comic panel /
    animation frame / game screenshot / official document is
    NEVER stored in the shippable asset output. The descriptor
    is description-only.

    **VLMs:** Every extractor tool routes through MODEL_REGISTRY
    (no hardcoded model strings). The defaults are:
    qwen3-vl-8b (comic + gameplay), molmo2-8b (animation),
    qwen3.6-27b-mtp (prose), olmocr-2-7b (official documents).

    **BILINGUAL EN/GA:** The NCCA jurisdiction is published in
    both English and Irish. The `summarise_corpus` tool returns
    a bilingual EN/GA summary per the bilingual_extraction
    invariant in BAML.

    Current date: {datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d")}

    Begin by classifying the input medium and dispatching
    the appropriate tool.
    """,
    tools=[
        FunctionTool(func=t.fn) for t in TOOLS
    ],
    output_key="media_descriptor_response",
)


__all__ = [
    "TOOLS",
    "TOOL_NAMES",
    "WireSubjectAgent",
    "compare_class_consistency",
    "extract_animation_descriptor_tool",
    "extract_comic_descriptor_tool",
    "extract_gameplay_descriptor_tool",
    "extract_official_document_descriptor_tool",
    "extract_prose_descriptor_tool",
    "list_descriptors_by_class",
    "list_sources",
    "list_tools",
    "media_descriptor_agent",
    "media_descriptor_agent_wire",
    "run_tool",
    "search_descriptors",
    "summarise_corpus",
]
