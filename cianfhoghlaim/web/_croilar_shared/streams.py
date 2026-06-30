"""Stream registry for the Croílár portfolio platform.

Replaces the legacy persona model (`aleyum` / `cianfhoghlaim` / `carlcashman`)
with a domain-driven `Stream` model:

    Stream.id   = "music" | "teaching" | "cv" | "research"   (domain id)
    Stream.owner = "aleyum" | "cianfhoghlaim"                 (historical alias)
    Stream.owner_display_name                                  (canonical name)

Sources are loaded from `croilar/config/sources.yaml` under the `streams:` key.
The registry is the single source of truth for:

- Which DLT sources feed which stream
- Where each stream's data lives (R2 prefix, DuckDB dataset)
- Whether a source is local-only (no R2 uploads)
- Which agent-OS port the stream's research agents listen on

Usage:

    from croilar._shared.streams import get_stream, list_streams

    music = get_stream("music")
    for source in music.sources:
        ...

    for stream in list_streams():
        for asset_key in stream_asset_keys(stream):
            ...
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator


class StreamSourceType(StrEnum):
    """The set of source types that can be attached to a Stream.

    New types are added by:
      1. Adding the value here
      2. Adding a `pipelines/<type>/` module
      3. Adding a BAML extraction schema (if structured extraction is needed)
      4. Wiring the asset factory in `croilar/dagster_assets/dlt_assets.py`
    """

    GITHUB = "github"
    LINKEDIN = "linkedin"
    RESEARCHGATE = "researchgate"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    LABELS = "labels"
    CV = "cv"
    ARTWORK = "artwork"
    FILESYSTEM = "filesystem"
    ZOTERO_SQL = "zotero_sql"


class StreamSourceModel(BaseModel):
    """Pydantic mirror of a single source entry under a Stream.

    `local_only=True` gates the R2 upload step in every destination helper.
    Use it for sensitive or local-only corpora (CV PDFs, identity documents).
    """

    type: StreamSourceType
    config: dict[str, Any] = Field(default_factory=dict)
    local_only: bool = False

    @field_validator("type", mode="before")
    @classmethod
    def _coerce_type(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip().lower()
        return value


class StreamModel(BaseModel):
    """Pydantic mirror of a single Stream entry under `streams:`."""

    id: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_]*$")
    owner: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_]*$")
    owner_display_name: str = Field(min_length=1)
    r2_prefix: str = Field(min_length=1)
    duckdb_dataset: str = Field(min_length=1)
    agent_port: int = Field(default=7774, ge=1024, le=65535)
    sources: list[StreamSourceModel] = Field(default_factory=list)


class StreamsFile(BaseModel):
    """Top-level shape of `croilar/config/sources.yaml`."""

    streams: dict[str, StreamModel] = Field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class StreamSource:
    """Frozen dataclass for ergonomic Python access to a stream source.

    Mirrors `StreamSourceModel` but is hashable + immutable.
    """

    type: StreamSourceType
    config: Mapping[str, Any]
    local_only: bool = False


@dataclass(frozen=True, slots=True)
class Stream:
    """Frozen dataclass for ergonomic Python access to a stream."""

    id: str
    owner: str
    owner_display_name: str
    r2_prefix: str
    duckdb_dataset: str
    agent_port: int
    sources: tuple[StreamSource, ...] = field(default_factory=tuple)

    def has_source(self, source_type: StreamSourceType | str) -> bool:
        target = StreamSourceType(source_type) if not isinstance(source_type, StreamSourceType) else source_type
        return any(s.type == target for s in self.sources)

    def get_source(self, source_type: StreamSourceType | str) -> StreamSource:
        target = StreamSourceType(source_type) if not isinstance(source_type, StreamSourceType) else source_type
        for s in self.sources:
            if s.type == target:
                return s
        raise KeyError(
            f"stream {self.id!r} has no source of type {target!r}; "
            f"available: {[s.type.value for s in self.sources]}"
        )


def _model_to_dataclass(model: StreamModel) -> Stream:
    return Stream(
        id=model.id,
        owner=model.owner,
        owner_display_name=model.owner_display_name,
        r2_prefix=model.r2_prefix,
        duckdb_dataset=model.duckdb_dataset,
        agent_port=model.agent_port,
        sources=tuple(
            StreamSource(
                type=s.type,
                config=s.config,
                local_only=s.local_only,
            )
            for s in model.sources
        ),
    )


def load_streams_from_mapping(data: Mapping[str, Any]) -> list[Stream]:
    """Validate a parsed YAML mapping and return a list of Stream dataclasses.

    Raises `pydantic.ValidationError` on any schema violation.
    """
    parsed = StreamsFile.model_validate(data)
    return [_model_to_dataclass(s) for s in parsed.streams.values()]


def load_streams_from_yaml(path: str | Path) -> list[Stream]:
    """Load and validate `croilar/config/sources.yaml`."""
    p = Path(path)
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, Mapping):
        raise ValidationError.from_exception_data(
            "sources.yaml",
            [
                {
                    "type": "value_error",
                    "loc": (),
                    "msg": f"sources.yaml root must be a mapping, got {type(raw).__name__}",
                    "input": raw,
                }
            ],
        )
    return load_streams_from_mapping(raw)


# Default config path is anchored at the croilar package root.
DEFAULT_SOURCES_PATH = Path(__file__).resolve().parent.parent / "config" / "sources.yaml"


@lru_cache(maxsize=1)
def _registry_cached(path_str: str) -> tuple[Stream, ...]:
    return tuple(load_streams_from_yaml(Path(path_str)))


def list_streams(path: str | Path | None = None) -> list[Stream]:
    """Return all streams from the registry.

    Pass `path` to override the default config (used by tests).
    """
    p = str(path) if path is not None else str(DEFAULT_SOURCES_PATH)
    return list(_registry_cached(p))


def get_stream(stream_id: str, path: str | Path | None = None) -> Stream:
    """Look up a single stream by id.

    Raises `KeyError` if the stream is not registered.
    """
    for s in list_streams(path):
        if s.id == stream_id:
            return s
    available = [s.id for s in list_streams(path)]
    raise KeyError(
        f"stream {stream_id!r} not registered; available: {available}"
    )


def reset_cache() -> None:
    """Clear the registry cache. Test-only."""
    _registry_cached.cache_clear()


def iter_asset_keys(stream: Stream) -> list[tuple[str, str]]:
    """Yield the `(stream.id, source.type.value)` asset-key tuples for a stream."""
    return [(stream.id, source.type.value) for source in stream.sources]


__all__ = [
    "DEFAULT_SOURCES_PATH",
    "Stream",
    "StreamModel",
    "StreamSource",
    "StreamSourceModel",
    "StreamSourceType",
    "StreamsFile",
    "get_stream",
    "iter_asset_keys",
    "list_streams",
    "load_streams_from_mapping",
    "load_streams_from_yaml",
    "reset_cache",
]
