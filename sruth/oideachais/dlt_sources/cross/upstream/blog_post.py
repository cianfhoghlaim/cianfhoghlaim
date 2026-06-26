"""
oideachais.dlt_sources.cross.upstream.blog_post — DLT incremental
source for Firecrawl-monitor payloads from upstream package blogs.

The 7th dlt_sources domain. Phase 1 of the `upstream-package-monitoring`
openspec change.

Source: n8n workflow `engineering/n8n/workflows/upstream-blog-monitor.json`
writes one JSONL file per Firecrawl-monitor webhook to
`s3://oideachais-upstream-webhooks/<package>/<YYYY-MM-DD>/<blog_post_id>.jsonl`.

Each line of each JSONL is one Firecrawl payload (see
`domains/cross/upstream/__init__.py` for the schema). The DLT source
yields one row per line, with primary key
`(package, blog_post_id, first_seen_at)`.

Incremental loading is cursor-based on `first_seen_at` — DLT will only
load rows whose first_seen_at is > the high-water mark on the previous
run. This avoids re-processing the entire blog history on every run.

The schema is enforced by the BAML `ExtractBlogPostMetadata` function
defined in `oideachais/baml_src/upstream_monitoring.baml`.

Reference: openspec/changes/upstream-package-monitoring/proposal.md
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import dlt

logger_module_name = __name__


# Default payload root: the S3/Garage bucket mounted by the dlt
# filesystem connector in production. Override with
# `UPSTREAM_PAYLOADS_ROOT` for local dev (the n8n workflow can also
# write to a local path when running in dev-baile).
DEFAULT_PAYLOADS_ROOT = Path(
    os.getenv(
        "UPSTREAM_PAYLOADS_ROOT",
        "s3://oideachais-upstream-webhooks/",
    )
)

# Package enum — must match `oideachais/baml_src/upstream_monitoring.baml:Package`
PACKAGES = frozenset({"motherduck", "dlthub", "lancedb", "cocoindex"})


def _iter_payloads(payloads_root: Path) -> Iterator[dict[str, Any]]:
    """Walk the payloads directory and yield one row per JSONL line.

    Expected layout::

        <payloads_root>/<package>/<YYYY-MM-DD>/<blog_post_id>.jsonl

    Anything that does not match this layout (e.g. partially-written
    files during n8n append, unrelated files) is silently skipped.
    """
    if not payloads_root.exists():
        return
    for package_dir in sorted(payloads_root.iterdir()):
        if not package_dir.is_dir():
            continue
        package = package_dir.name
        if package not in PACKAGES:
            continue
        for date_dir in sorted(package_dir.iterdir()):
            if not date_dir.is_dir():
                continue
            for jsonl_file in sorted(date_dir.glob("*.jsonl")):
                with jsonl_file.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            payload = json.loads(line)
                        except json.JSONDecodeError:
                            # Skip malformed lines; n8n will retry.
                            continue
                        metadata = payload.get("metadata", {})
                        if metadata.get("package") != package:
                            # Cross-package contamination — skip.
                            continue
                        blog_post_id = (
                            f"{package}:{jsonl_file.stem[:16]}"
                        )
                        yield {
                            "blog_post_id": blog_post_id,
                            "package": package,
                            "blog_post_type": metadata.get(
                                "blog_post_type", "unknown"
                            ),
                            "first_seen_at": metadata.get(
                                "first_seen_at",
                                datetime.now(timezone.utc).isoformat(),
                            ),
                            "firecrawl_monitor_id": metadata.get(
                                "firecrawl_monitor_id", ""
                            ),
                            "change_severity": metadata.get(
                                "change_severity", "medium"
                            ),
                            "url": metadata.get("url", ""),
                            "title": metadata.get("title", ""),
                            "summary": metadata.get("summary", ""),
                            "is_meaningful": bool(
                                metadata.get("is_meaningful", False)
                            ),
                            "judgment_confidence": metadata.get(
                                "judgment_confidence", "low"
                            ),
                            "blog_post": payload.get("blog_post", {}),
                            "api_change": payload.get("api_change", {}),
                            "_loaded_at": datetime.now(
                                timezone.utc
                            ).isoformat(),
                        }


@dlt.source(name="upstream_blog_post")
def upstream_blog_post_source(
    payloads_root: Path = DEFAULT_PAYLOADS_ROOT,
) -> list:
    """Upstream package blog payloads source.

    Two resources:

    1. `upstream_blog_post` — incremental on `first_seen_at`. Primary
       key `(package, blog_post_id)`. The main table.

    2. `upstream_blog_post_audit` — append-only audit log of every
       payload that n8n delivered (one row per webhook delivery).
       Primary key `(delivery_id)` where delivery_id is computed
       from the S3 object key. This lets us prove that no payload was
       silently dropped between Firecrawl and the LanceDB vector store.
    """

    @dlt.resource(
        name="upstream_blog_post",
        primary_key=("package", "blog_post_id"),
        write_disposition="merge",
    )
    def upstream_blog_post(  # type: ignore[no-redef]
        cursor: dlt.sources.incremental[str] = dlt.sources.incremental(  # type: ignore[attr-defined]
            "first_seen_at",
            initial_value="1970-01-01T00:00:00Z",
        ),
    ) -> Iterator[dict[str, Any]]:
        for row in _iter_payloads(payloads_root):
            # Apply the incremental cursor filter.
            if not cursor.start_value or row["first_seen_at"] >= cursor.start_value:
                yield row

    @dlt.resource(
        name="upstream_blog_post_audit",
        primary_key="delivery_id",
        write_disposition="append",
    )
    def upstream_blog_post_audit() -> Iterator[dict[str, Any]]:
        if not payloads_root.exists():
            return
        for package_dir in sorted(payloads_root.iterdir()):
            if not package_dir.is_dir():
                continue
            package = package_dir.name
            if package not in PACKAGES:
                continue
            for date_dir in sorted(package_dir.iterdir()):
                if not date_dir.is_dir():
                    continue
                for jsonl_file in sorted(date_dir.glob("*.jsonl")):
                    yield {
                        "delivery_id": (
                            f"{package}/{date_dir.name}/{jsonl_file.name}"
                        ),
                        "package": package,
                        "date_dir": date_dir.name,
                        "filename": jsonl_file.name,
                        "size_bytes": jsonl_file.stat().st_size,
                        "first_seen_at": datetime.now(
                            timezone.utc
                        ).isoformat(),
                    }

    return [upstream_blog_post, upstream_blog_post_audit]


__all__ = [
    "DEFAULT_PAYLOADS_ROOT",
    "PACKAGES",
    "upstream_blog_post_source",
]