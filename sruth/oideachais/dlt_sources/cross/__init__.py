"""oideachais.dlt_sources.cross — the 7th dlt_sources domain.

The `cross/` domain holds sources that span multiple downstream
quadrants rather than mapping to a single educational jurisdiction.
Examples:

- `cross/upstream/blog_post.py` — Firecrawl-monitor payloads from
  motherduck/dlthub/lancedb/cocoindex blogs, written by the n8n
  `upstream-blog-monitor` workflow to `s3://oideachais-upstream-webhooks/`.

Future additions will land here:

- `cross/infrastructure/audit_event.py` — audit-script events from
  `infrastructure/audit/inventory/<host>-<UTC>.json`.
- `cross/observability/langfuse_trace.py` — Langfuse traces for
  the cross-quadrant observability contract.

Each new sub-package must:

1. Be importable as `dlt_sources.cross.<area>`.
2. Define at least one `@dlt.source(name=...)` with a primary_key on
   each resource.
3. Document its schema in a `README.md` next to the source.
"""
from __future__ import annotations

from dlt_sources.cross import upstream

__all__ = ["upstream"]