"""cognee_client — the 7 typed cognee cluster pinger.

Per the `indexing-and-cognition` spec + the
2026-08-23-dlt-sources-ccc-audit-and-realignment-v1 audit.

The 7 typed cognee clusters are the canonical Cognee dataset shape
(per `.agents/skills/cognee/references/cluster-model/cognee_readiness_audit.md`).
"""

from __future__ import annotations

import os
from typing import Final

import requests

# The 7 canonical cognee clusters
COGNEE_CLUSTERS: Final[list[str]] = [
    "docs-data-eng",
    "docs-bonneagar",
    "docs-agents",
    "docs-ml",
    "docs-teanga",
    "docs-web",
    "docs-tuatha",
]

# The cognee API endpoint (from the env var matrix)
COGNEE_API_URL: Final[str] = os.environ.get("COGNEE_API_URL", "http://localhost:8100")


def ping_cluster(cluster: str) -> bool:
    """Ping the cognee cluster. Returns True if healthy."""
    try:
        resp = requests.post(
            f"{COGNEE_API_URL}/api/v1/cognify",
            json={"datasets": [cluster], "runInBackground": True},
            timeout=30,
        )
        return resp.status_code == 200
    except (requests.RequestException, ConnectionError):
        return False
