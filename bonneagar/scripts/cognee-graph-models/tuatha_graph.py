"""
tuatha_graph.py — Tuatha MMO cluster graph model.

Cluster: docs-tuatha
Entities: GameAsset, SpacetimeDBTable, X402Payment, NpcCharacter
"""

from __future__ import annotations

GRAPH_NODE_TYPES: tuple[str, ...] = (
    "GameAsset",
    "SpacetimeDBTable",
    "X402Payment",
    "NpcCharacter",
)

GRAPH_EDGE_TYPES: tuple[str, ...] = (
    "GameAsset RENDERED_IN NpcCharacter",
    "NpcCharacter STORED_IN SpacetimeDBTable",
    "X402Payment UNLOCKS GameAsset",
    "NpcCharacter QUESTS GameAsset",
)

CLUSTER_NAME = "docs-tuatha"
CLUSTER_DESCRIPTION = (
    "The British Isles Formative Assessment MMO + crypteolas "
    "educational-achievement ledger: Babylon.js 7 + WebGPU client, "
    "Rust + SpacetimeDB server, x402 micropayments, SIWE auth, "
    "Pent-Elemental Cosmology (Spirit/Water/Fire/Earth/Air + Anam "
    "Cara)."
)


def get_graph_model() -> dict[str, tuple[str, ...]]:
    return {"nodes": GRAPH_NODE_TYPES, "edges": GRAPH_EDGE_TYPES}
