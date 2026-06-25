"""Dagster assets for the Croílár Stream registry.

Replaces the legacy hard-coded `aleyummusic` / `aleyum` assets with a
generic factory that walks the Stream registry and emits one
`AssetKey(stream.id, source.type)` per registered source.

Asset key shape:

    ("music", "spotify"),     ("music", "soundcloud"),  ("music", "labels"),  ("music", "artwork")
    ("teaching", "github"),   ("teaching", "linkedin"), ("teaching", "researchgate")
    ("cv", "cv"),             ("cv", "filesystem")
    ("research", ...)         # placeholder; no sources registered yet

The motherduck_sync and artwork_processing assets remain as concrete
composers; their `deps` are computed dynamically from the registry.

Reference:
    https://docs.dagster.io/integrations/libraries/dlt/dlt-pythonic
"""

# IMPORTANT: do NOT add `from __future__ import annotations` to this file.
# The `@asset` decorator inspects `context: AssetExecutionContext` at
# decoration time; PEP-563 string annotations would defeat that check.

from typing import Any, Iterable

from dagster import (
    AssetExecutionContext,
    AssetKey,
    MaterializeResult,
    asset,
)

from _shared.streams import (
    Stream,
    StreamSource,
    StreamSourceType,
    get_stream,
    iter_asset_keys,
    list_streams,
)


def _source_asset_keys(stream: Stream) -> list[AssetKey]:
    """Return the AssetKeys for every (stream, source) pair on this stream."""
    return [AssetKey(list(pair)) for pair in iter_asset_keys(stream)]


def _source_key(stream: Stream, source_type: StreamSourceType) -> AssetKey:
    return AssetKey([stream.id, source_type.value])


# =============================================================================
# Per-source asset definitions
# =============================================================================
# Each function is bound to a (stream, source) pair at module-import time.
# The generic `make_dlt_asset` factory is the recommended way to add new
# (stream, source) pairs in the future; the explicit functions below are
# kept for backwards compatibility with the Dagster UI group_names.


def make_dlt_asset(
    stream_id: str,
    source_type: str | StreamSourceType,
    compute_fn,
    group_name: str | None = None,
    description: str | None = None,
    deps: Iterable[AssetKey] = (),
) -> Any:
    """Build a Dagster asset for a single (stream, source) pair.

    The asset name is `f"{stream_id}__{source_type.value}"`; the
    AssetKey is `(stream_id, source_type.value)`. The `compute_fn` is
    called at materialization time and must return a `MaterializeResult`
    (or a `LoadInfo` that we wrap in one).
    """
    src = source_type.value if isinstance(source_type, StreamSourceType) else str(source_type)
    stream = get_stream(stream_id)
    src_source = stream.get_source(src)
    name = f"{stream_id}__{src}"
    group = group_name or f"{stream_id}__dlt"
    desc = description or (
        f"Run DLT pipeline for stream `{stream_id}` source `{src}` "
        f"(owner={stream.owner_display_name}, local_only={src_source.local_only})"
    )

    @asset(
        name=name,
        group_name=group,
        description=desc,
        compute_kind="dlt",
        deps=list(deps),
    )
    def _asset(context: AssetExecutionContext) -> MaterializeResult:
        info = compute_fn(context=context, stream=stream, source=src_source)
        if isinstance(info, MaterializeResult):
            return info
        loads = getattr(info, "loads_ids", None) or []
        return MaterializeResult(
            metadata={
                "load_ids": str(loads),
                "loads_count": len(loads),
                "stream_id": stream_id,
                "source": src,
                "local_only": src_source.local_only,
            }
        )

    return _asset


# =============================================================================
# Concrete compute functions (one per registered source type)
# =============================================================================


def _run_spotify(context, stream: Stream, source: StreamSource) -> Any:
    from pipelines.spotify import run_spotify_pipeline
    return run_spotify_pipeline(
        artist_id=source.config.get("artist_id", ""),
        cache_images=False,
        fetch_audio_features=True,
    )


def _run_soundcloud(context, stream: Stream, source: StreamSource) -> Any:
    from pipelines.soundcloud import run_soundcloud_pipeline
    return run_soundcloud_pipeline(username=source.config.get("username", ""))


def _run_labels(context, stream: Stream, source: StreamSource) -> Any:
    from pipelines.labels import run_labels_pipeline
    return run_labels_pipeline(
        artist_slug=source.config.get("artist_slug", ""),
        labels=["monstercat", "lemongrass"],
    )


def _run_artwork(context, stream: Stream, source: StreamSource) -> Any:
    from pipelines.artwork import run_artwork_pipeline

    import duckdb
    conn = duckdb.connect("./data/croilar.duckdb")
    urls: list[dict[str, Any]] = []
    try:
        for url, entity_id, entity_type, label in conn.execute(
            "SELECT url, id, 'album', 'spotify' FROM spotify_data.cached_images"
        ).fetchall():
            urls.append({"url": url, "entity_id": entity_id, "entity_type": entity_type, "label": label})
    except Exception:
        pass
    try:
        for url, entity_id, entity_type, label in conn.execute(
            "SELECT url, entity_id, entity_type, label FROM label_data.artwork"
        ).fetchall():
            urls.append({"url": url, "entity_id": entity_id, "entity_type": entity_type, "label": label})
    except Exception:
        pass
    conn.close()
    context.log.info(f"Processing {len(urls)} artwork images")
    return run_artwork_pipeline(artwork_urls=urls)


def _run_github(context, stream: Stream, source: StreamSource) -> Any:
    from pipelines.github import run_github_pipeline
    return run_github_pipeline(username=source.config.get("username", ""))


def _run_linkedin(context, stream: Stream, source: StreamSource) -> Any:
    from pipelines.linkedin import run_linkedin_pipeline
    return run_linkedin_pipeline(
        profile_url=source.config.get("profile_url", ""),
        stream_id=stream.id,
        owner_display_name=stream.owner_display_name,
    )


def _run_researchgate(context, stream: Stream, source: StreamSource) -> Any:
    from pipelines.researchgate import run_researchgate_pipeline
    return run_researchgate_pipeline(
        profile_url=source.config.get("profile_url", ""),
        stream_id=stream.id,
        owner_display_name=stream.owner_display_name,
    )


def _run_cv(context, stream: Stream, source: StreamSource) -> Any:
    from pipelines.cv import run_cv_pipeline
    return run_cv_pipeline()


def _run_filesystem(context, stream: Stream, source: StreamSource) -> Any:
    from pipelines.fs_author import run_fs_author_pipeline
    context.log.info(
        f"Local-only filesystem ingest for stream {stream.id!r} "
        f"(owner={stream.owner_display_name}); excludes zotero/"
    )
    return run_fs_author_pipeline()


# Map StreamSourceType -> compute function
_COMPUTE_REGISTRY: dict[StreamSourceType, Any] = {
    StreamSourceType.SPOTIFY: _run_spotify,
    StreamSourceType.SOUNDCLOUD: _run_soundcloud,
    StreamSourceType.LABELS: _run_labels,
    StreamSourceType.ARTWORK: _run_artwork,
    StreamSourceType.GITHUB: _run_github,
    StreamSourceType.LINKEDIN: _run_linkedin,
    StreamSourceType.RESEARCHGATE: _run_researchgate,
    StreamSourceType.CV: _run_cv,
    StreamSourceType.FILESYSTEM: _run_filesystem,
}


# =============================================================================
# Build the asset list from the Stream registry
# =============================================================================


def build_stream_assets() -> list[Any]:
    """Walk the Stream registry and build one asset per (stream, source) pair."""
    assets: list[Any] = []
    for stream in list_streams():
        for source in stream.sources:
            fn = _COMPUTE_REGISTRY.get(source.type)
            if fn is None:
                continue
            assets.append(
                make_dlt_asset(
                    stream_id=stream.id,
                    source_type=source.type,
                    compute_fn=fn,
                    group_name=f"{stream.id}__dlt",
                )
            )
    return assets


# Eagerly build the module-level assets so Dagster can discover them.
_stream_assets = build_stream_assets()


# =============================================================================
# Cross-cutting composer assets (preserved)
# =============================================================================


@asset(
    name="artwork_processing",
    group_name="music__composer",
    description="Download and process artwork images for the music stream",
    compute_kind="dlt",
    deps=[
        _source_key(get_stream("music"), StreamSourceType.SPOTIFY),
        _source_key(get_stream("music"), StreamSourceType.SOUNDCLOUD),
        _source_key(get_stream("music"), StreamSourceType.LABELS),
    ],
)
def artwork_processing_asset(context: AssetExecutionContext) -> MaterializeResult:
    music = get_stream("music")
    artwork_source = music.get_source(StreamSourceType.ARTWORK)
    info = _run_artwork(context, music, artwork_source)
    loads = getattr(info, "loads_ids", None) or []
    return MaterializeResult(metadata={"load_ids": str(loads), "loads_count": len(loads)})


@asset(
    name="motherduck_sync",
    group_name="cross_link",
    description="Sync DuckDB tables to MotherDuck cloud for Dive embedding",
    compute_kind="motherduck",
)
def motherduck_sync_asset(context: AssetExecutionContext) -> MaterializeResult:
    """Copy all DuckDB tables to MotherDuck cloud.

    MotherDuck provides a cloud-hosted DuckDB with the Dive UI for
    self-service SQL exploration by collaborators.

    The MotherDuck token comes from env var MOTHERDUCK_TOKEN (set via
    Infisical dev-baile/croilar/motherduck/).

    Runs after all upstream DLT ingestion assets to keep Dive in sync.
    """
    import os
    import duckdb

    token = os.environ.get("MOTHERDUCK_TOKEN")
    if not token:
        context.log.warning("MOTHERDUCK_TOKEN not set — MotherDuck sync skipped")
        return MaterializeResult(
            metadata={"synced_tables": 0, "reason": "missing_token"},
        )

    local = duckdb.connect("./data/croilar.duckdb", read_only=True)
    md = duckdb.connect(f"md:?motherduck_token={token}")
    synced = 0

    tables = [
        ("spotify_data", "tracks"),
        ("spotify_data", "artists"),
        ("spotify_data", "albums"),
        ("github_data", "repos"),
        ("cv_data", "cv_raw"),
        ("teaching_data", "cv_raw"),
    ]

    for schema, table in tables:
        try:
            full_name = f"{schema}.{table}"
            count = local.execute(f"SELECT COUNT(*) FROM {full_name}").fetchone()[0]
            if count > 0:
                md.execute(f"CREATE OR REPLACE TABLE {schema}.{table} AS SELECT * FROM local.{full_name}")
                synced += 1
                context.log.info(f"Synced {full_name} ({count} rows) to MotherDuck")
        except Exception as e:
            context.log.warning(f"Failed to sync {schema}.{table}: {e}")

    local.close()
    md.close()

    return MaterializeResult(
        metadata={
            "synced_tables": synced,
            "total_tables": len(tables),
        }
    )


# Expose the per-source stream assets at module scope for Dagster to discover.
for _asset_obj in _stream_assets:
    globals()[_asset_obj.op.name if hasattr(_asset_obj, "op") else _asset_obj.name] = _asset_obj


__all__ = [
    "make_dlt_asset",
    "build_stream_assets",
    "artwork_processing_asset",
    "motherduck_sync_asset",
]
