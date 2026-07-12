"""Deployment manifest for the Cianfhoghlaim dltHub Platform workspace.

This module is the canonical `dlthub deploy` entry point. Each entry in
`__all__` registers as a job on the dltHub Platform runtime. The convention
is one decorated function or one imported module per `__all__` entry — keep
them coarse-grained.

Batch jobs (pipelines + scripts) live here, decorated with
`@run.pipeline("name")` from `dlt.hub`. Interactive jobs (notebooks,
dashboards) belong in `__interactive__.py` (not yet created) so the
`dlthub run` auto-matcher doesn't pick them up by mistake — see
`docs/agents/dlthub-run-vs-serve.md`.

See `openspec/changes/2026-07-06-wire-dlthub-platform-toolkits-and-deployment/`
for the wiring contract.
"""
from __future__ import annotations

# First BIEP batch job: ingest government circulars (gov.ie / Oide) from
# the curated `stedding/site_scrape_samples/oide.ie/` snapshot. See the
# `2026-07-06-wire-dlthub-platform-toolkits-and-deployment` change for the
# design rationale; the full BAML extraction pipeline lands in Phase 3.3
# of `2026-07-06-british-isles-education-pipeline-v1`.
from cianfhoghlaim.dlt.jobs import government_circulars_job

__all__: list[str] = [
    "government_circulars_job",
]
