"""
web_graph.py — Web & Frontend cluster graph model.

Cluster: docs-web
Entities: TanStackRoute, ConvexQuery, BetterAuthProvider, EffectService
"""

from __future__ import annotations

GRAPH_NODE_TYPES: tuple[str, ...] = (
    "TanStackRoute",
    "ConvexQuery",
    "BetterAuthProvider",
    "EffectService",
)

GRAPH_EDGE_TYPES: tuple[str, ...] = (
    "TanStackRoute RENDERS ConvexQuery",
    "ConvexQuery AUTHENTICATED_BY BetterAuthProvider",
    "TanStackRoute POWERED_BY EffectService",
    "BetterAuthProvider GUARDS ConvexQuery",
)

CLUSTER_NAME = "docs-web"
CLUSTER_DESCRIPTION = (
    "The 4 agentic frontend surfaces (sruth/oideachais/web, "
    "sruth/croilar/apps/web, sruth/croilar/apps/portal, "
    "sruth/tuatha/ui) + 5 stacks (TanStack Start + CopilotKit + "
    "AG-UI + Convex + Hono + oRPC + Cloudflare) + 5 auth models "
    "and 5 data planes."
)


def get_graph_model() -> dict[str, tuple[str, ...]]:
    return {"nodes": GRAPH_NODE_TYPES, "edges": GRAPH_EDGE_TYPES}
