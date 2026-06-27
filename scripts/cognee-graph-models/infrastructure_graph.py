"""
infrastructure_graph.py — Infrastructure cluster graph model.

Cluster: docs-bonneagar (bonnéagar = Irish for "infrastructure")
Entities: KomodoStack, PangolinTunnel, DaggerPipeline, PulumiResource,
          AnsibleRole
"""

from __future__ import annotations

GRAPH_NODE_TYPES: tuple[str, ...] = (
    "KomodoStack",
    "PangolinTunnel",
    "DaggerPipeline",
    "PulumiResource",
    "AnsibleRole",
)

GRAPH_EDGE_TYPES: tuple[str, ...] = (
    "KomodoStack DEPLOYS PangolinTunnel",
    "DaggerPipeline BUILDS KomodoStack",
    "KomodoStack CONSUMES PulumiResource",
    "AnsibleRole CONFIGURES KomodoStack",
    "PangolinTunnel ROUTES_TO KomodoStack",
)

CLUSTER_NAME = "docs-bonneagar"
CLUSTER_DESCRIPTION = (
    "The 94-stack Komodo + Pangolin + Locket + Infisical mesh that "
    "runs the Cianfhoghlaim platform on the 3-tier KCG topology "
    "(arm1-oci + bunchloch + cax41-hetzner)."
)


def get_graph_model() -> dict[str, tuple[str, ...]]:
    return {"nodes": GRAPH_NODE_TYPES, "edges": GRAPH_EDGE_TYPES}
