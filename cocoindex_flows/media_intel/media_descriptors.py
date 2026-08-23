"""media_intel CocoIndex v1 App: media_descriptors.

The primary storage surface for the 7-axis MediaDescriptor
records emitted by the 5 per-medium BAML extractor functions
in `baml_src/media/`. Mounts the `media_descriptors_lance`
LanceDB table. R1-R4 conformant per the
`dagster-5-layer-component-architecture` spec.

Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
            design.md § 1 (the 7-axis descriptor schema)
            spec.md § media-intel-corpus Requirement 2
"""
from __future__ import annotations

from cocoindex import App, dataclass
from cocoindex.op import LanceDB

# Per the existing `cocoindex_flows/_lifespan.py:107` shared
# embedder, we use the BAAI/bge-m3 1024-d embedding. The
# `MODEL_REGISTRY.resolve(family="ocr_vision", role="media_descriptor")`
# resolution is the canonical way to look up the per-medium VLM;
# for the embedder we use the shared BGE-M3 (the canonical
# embedder across the entire platform).


@dataclass
class MediaDescriptorRecord:
    work: str
    medium: str
    language: str
    source_url: str
    source_timestamp: str
    power_event_json: str
    visual_grammar_json: str
    palette_json: str
    vfx_vocabulary_json: str
    narrative_beat_json: str
    transferability_json: str
    provenance_json: str

    acquisition_id: str
    firecrawl_plan: str


# The CocoIndex v1 App. The App decorator follows the pattern
# in `cocoindex_flows/codebase_indexing.py` (the codebase
# indexing surface per the `media_intel_corpus/AGENTS.md`
# reference).
media_descriptors = App(
    name="media_descriptors",
    description=(
        "The 7-axis MediaDescriptor storage surface for the "
        "5-class source registry (comics, prose, animation, "
        "games, official). Mounts the media_descriptors_lance "
        "LanceDB table. R1-R4 conformant per the "
        "dagster-5-layer-component-architecture spec."
    ),
)

# The LanceDB target.
media_descriptors.target_table = LanceDB(
    table_name="media_descriptors_lance",
    vector_dim=1024,
    vector_index=LanceDB.HnswIndex(
        distance=LanceDB.Distance.COSINE,
    ),
)
