"""oideachais.dlt_sources.domains.cross.upstream — upstream package
monitoring payloads.

The 7th dlt_sources domain. See `domains/cross/__init__.py` for the
rationale (sources that span multiple quadrants).

The single source here is `upstream_blog_post_source` which reads the
n8n-workflow payloads written to S3/Garage by the `upstream-blog-monitor`
n8n workflow (see `engineering/n8n/workflows/upstream-blog-monitor.json`).

Payload format (one JSON object per line in `<package>/<YYYY-MM-DD>/<blog_post_id>.jsonl`):

    {
        "metadata": {
            "package": "motherduck",           # Package enum (motherduck | dlthub | lancedb | cocoindex)
            "blog_post_type": "release_notes", # BlogPostType enum (announcement | tutorial | benchmark | case_study | release_notes | api_doc)
            "first_seen_at": "2026-06-25T12:34:56Z",
            "firecrawl_monitor_id": "mon_...",
            "change_severity": "high",
            "url": "https://motherduck.com/blog/...",
            "title": "Announcing DuckLake 1.0 on MotherDuck",
            "summary": "DuckLake 1.0 introduces ...",
            "is_meaningful": true,
            "judgment_confidence": "high",
        },
        "blog_post": {
            "author": "...",
            "published_at": "2026-06-25T00:00:00Z",
            "markdown": "...",
            "key_changes": ["..."],
            "code_snippets": ["..."],
            "linked_prs": ["..."],
        },
        "api_change": {                         # only for cocoindex_docs payload
            "function_signature": "...",
            "is_breaking": true,
            "migration_notes": "...",
            "affected_v1_apps": ["upstream_blog_monitor"],
        }
    }

Each payload maps to a single primary-key row in `oideachais.upstream_blog_posts`
via `metadata.blog_post_id` (computed by n8n as
`<package>:<sha256(markdown)[:16]>`).

The incremental cursor is `metadata["first_seen_at"]` — DLT will only
load rows whose first_seen_at is > the high-water mark on the previous run.
"""
from __future__ import annotations

from dlt_sources.domains.cross.upstream import blog_post

__all__ = ["blog_post"]