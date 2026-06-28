"""
ml_graph.py — ML & AI cluster graph model.

Cluster: docs-ml
Entities: FineTunedModel, TrainingDataset, MlflowExperiment,
          UnslothConfig, LanceDBCollection
"""

from __future__ import annotations

GRAPH_NODE_TYPES: tuple[str, ...] = (
    "FineTunedModel",
    "TrainingDataset",
    "MlflowExperiment",
    "UnslothConfig",
    "LanceDBCollection",
)

GRAPH_EDGE_TYPES: tuple[str, ...] = (
    "FineTunedModel TRAINED_ON TrainingDataset",
    "MlflowExperiment TRACKS FineTunedModel",
    "UnslothConfig CONFIGURES FineTunedModel",
    "FineTunedModel EMBEDDED_IN LanceDBCollection",
    "TrainingDataset STORED_IN LanceDBCollection",
)

CLUSTER_NAME = "docs-ml"
CLUSTER_DESCRIPTION = (
    "The ML/AI/finetuning stack: 70+ models via the kcg-ml-models "
    "registry, 6 Celtic languages, Unsloth + PEFT + TRL on the M4 "
    "MacBook (bunchloch), 5 fallback chains, 3 inference backends."
)


def get_graph_model() -> dict[str, tuple[str, ...]]:
    return {"nodes": GRAPH_NODE_TYPES, "edges": GRAPH_EDGE_TYPES}
