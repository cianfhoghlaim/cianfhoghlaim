"""
celtic_language_graph.py — Celtic Language cluster graph model.

Cluster: docs-teanga (teanga = Irish for "language")
Entities: LanguageDataset, HuggingFaceModel, GaeltachtBoundary,
          CensusTable
"""

from __future__ import annotations

GRAPH_NODE_TYPES: tuple[str, ...] = (
    "LanguageDataset",
    "HuggingFaceModel",
    "GaeltachtBoundary",
    "CensusTable",
)

GRAPH_EDGE_TYPES: tuple[str, ...] = (
    "HuggingFaceModel FINE_TUNED_ON LanguageDataset",
    "LanguageDataset CONTAINS GaeltachtBoundary",
    "CensusTable COVERS GaeltachtBoundary",
    "HuggingFaceModel SPEAKS LanguageDataset",
)

CLUSTER_NAME = "docs-teanga"
CLUSTER_DESCRIPTION = (
    "The 6 living Celtic languages (Irish, Scottish Gaelic, Welsh, "
    "Manx, Cornish, Breton) + 8 ISO codes + the curated model "
    "catalog (GaBERT, UCCIX, Helsinki OPUS-MT, NLLB-200, "
    "wav2vec2-XLSR-Irish, Chatterbox TTS, BGE-M3)."
)


def get_graph_model() -> dict[str, tuple[str, ...]]:
    return {"nodes": GRAPH_NODE_TYPES, "edges": GRAPH_EDGE_TYPES}
