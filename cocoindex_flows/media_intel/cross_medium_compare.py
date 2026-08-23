"""media_intel CocoIndex v1 App: cross_medium_compare.

The multihop search that surfaces the *consistent visual
grammar* across the 5 source classes. The canonical question
the App answers: "which element's visual grammar is most
consistent across WoT prose + ATLA animation + Hickman
comics?"

Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
            design.md § 1 (the 7-axis descriptor schema)
            spec.md § media-intel-corpus Requirement 6
"""
from __future__ import annotations

from cocoindex import App, dataclass
from cocoindex.op import LanceDB

# Per the shared `BAAI/bge-m3` 1024-d embedder convention.


@dataclass
class CrossMediumRecord:
    element: str                 # earth | air | water | fire | spirit
    comic_similarity: float       # average similarity across Hickman descriptors
    prose_similarity: float       # average similarity across WoT descriptors
    animation_similarity: float   # average similarity across ATLA descriptors
    game_similarity: float        # average similarity across game descriptors
    official_similarity: float    # average similarity across NCCA + Wikipedia descriptors
    total_consistency: float      # the consistency score (variance across the 5 media classes)
    descriptor_count: int         # the number of descriptors that contributed


# The CocoIndex v1 App. The App decorator follows the pattern
# in `cocoindex_flows/codebase_indexing.py` (the codebase
# indexing surface per the `media_intel_corpus/AGENTS.md`
# reference).
cross_medium_compare = App(
    name="cross_medium_compare",
    description=(
        "The multihop search that surfaces the *consistent "
        "visual grammar* across the 5 source classes. The "
        "canonical question the App answers: 'which element's "
        "visual grammar is most consistent across WoT prose "
        "+ ATLA animation + Hickman comics?' Mounts the "
        "media_descriptors_cross_medium_lance LanceDB table. "
        "R1-R4 conformant per the "
        "dagster-5-layer-component-architecture spec."
    ),
)

# The LanceDB target.
cross_medium_compare.target_table = LanceDB(
    table_name="media_descriptors_cross_medium_lance",
    vector_dim=1024,
    vector_index=LanceDB.HnswIndex(
        distance=LanceDB.Distance.COSINE,
    ),
)
