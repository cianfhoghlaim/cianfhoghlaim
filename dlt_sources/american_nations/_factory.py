"""dlt_sources/american_nations/_factory.py — single source of truth for the 4 American nations.

This module replaces the 4 per-nation stub files that previously
lived at ``dlt_sources/american_nations/<nation>/__init__.py``
with a single factory that parameterises on the canonical 4-row
ISO-3 table (Brazil, Mexico, United States, Venezuela).

Per the **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** openspec
change (Phase 1.2), the per-nation stub ``__init__.py`` files
collapse to 1-line re-export shims:
    from dlt_sources.american_nations._factory import brazil_source

Each shim exposes exactly the same ``<nation_slug>_source`` binding
that the factory injects at module load time, so any caller that
previously did
``from dlt_sources.american_nations.brazil import brazil_source``
continues to work.
"""
from __future__ import annotations

import importlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import dlt
from pydantic import BaseModel, ConfigDict, Field


# ─── Canonical cache root (mirrors the European + Commonwealth pattern) ──


_AMERICAN_NATIONS_CACHE_ROOT: Path = Path(
    os.environ.get(
        "AMERICAN_NATIONS_SCRAPE_CACHE_ROOT",
        str(
            Path(__file__).resolve().parents[2]
            / "stedding"
            / "ingest_queue"
            / "american_nations"
        ),
    )
)
"""Canonical local scrape cache root for the American-nations pipeline."""


VERTICAL = Literal["education", "government", "law", "medicine", "statistics"]


@dataclass
class _NationCore:
    """Minimal per-nation primitive used by the American-nations factory.

    Mirrors the ``NationSource`` contract (pre-§11 dataclass) so the
    factory can yield the canonical row shape. Avoids the BI-jurisdiction
    validation that the §11-merged ``JurisdictionPipelineBase`` adds.
    """

    country_code: str
    domain: str
    source_slug: str
    region: str = "american_nations"
    supported_languages: tuple[str, ...] = ("en",)
    default_language: str | None = None
    document_type: str = "official_document"
    extra_metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.default_language:
            self.default_language = self.supported_languages[0]

    @property
    def source_id(self) -> str:
        return f"{self.region}.{self.country_code}.{self.domain}.{self.source_slug}"

    @property
    def ducklake_table(self) -> str:
        return f"oideachais.{self.domain}.{self.region}.{self.country_code}"

    def cache_path(self, language: str | None = None) -> Path:
        lang = language or self.default_language
        return _AMERICAN_NATIONS_CACHE_ROOT / self.country_code / self.domain / lang

    def iter_local_cache(self):
        lang_dir = self.cache_path(self.default_language)
        if not lang_dir.exists():
            return
        for json_path in sorted(lang_dir.glob("*.json")):
            yield json_path


def _row_from_cache(cache_path: Path, nation: _NationCore, *, document_id_key: str = "document_id") -> dict[str, Any]:
    """Parse a per-nation cache JSON snapshot into a DLT row."""
    import json
    from datetime import UTC, datetime

    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}

    source_url = metadata.get("sourceURL") or metadata.get("url") or ""
    title = payload.get("title") or metadata.get("title") or ""
    markdown = payload.get("markdown") or ""

    document_id = (
        metadata.get(document_id_key)
        or metadata.get("id")
        or cache_path.stem
    )
    content_hash = (
        f"sha256:{hash(markdown) & 0xFFFFFFFFFFFFFFFF:016x}"
        if markdown
        else ""
    )

    return {
        "country_code": nation.country_code,
        "language": cache_path.parent.name,
        "domain": nation.domain,
        document_id_key: document_id,
        "title": title,
        "source_url": source_url,
        "content_hash": content_hash,
        "document_type": nation.document_type,
        "region": nation.region,
        "official_status": metadata.get("official_status", "in_force"),
        "extracted_at": datetime.now(UTC).isoformat(),
        "source": nation.source_slug,
        "source_file": str(cache_path),
    }


# ─── Pydantic config model ──────────────────────────────────────────────


class NationConfig(BaseModel):
    """Canonical 4-row ISO-3 table for the 4 American nations.

    Sourced from ``dlt_sources/LEGACY_ALIASES.md`` (the v7
    ISO-3 → snake_case rename map). Brazil + Venezuela use Spanish
    (and Brazil uses Portuguese); Mexico + the United States use
    Spanish + English respectively.
    """

    model_config = ConfigDict(frozen=True)

    country_code: str = Field(..., min_length=3, max_length=3, description="ISO 3166-1 alpha-3 in lowercase.")
    country_slug: str = Field(..., description="snake_case directory slug.")
    display_name_en: str
    iso2: str = Field(..., min_length=2, max_length=2)
    default_language: str = "en"
    supported_languages: tuple[str, ...] = ("en",)
    region: Literal["american_nations"] = "american_nations"
    verticals: list[VERTICAL] = Field(
        default_factory=lambda: ["education", "government", "law", "medicine", "statistics"],
    )


# ─── The canonical 4-row ISO-3 table ─────────────────────────────────────


NATION_CONFIGS: list[NationConfig] = [
    NationConfig(country_code="bra", country_slug="brazil",         display_name_en="Brazil",         iso2="br", default_language="pt", supported_languages=("pt", "en")),
    NationConfig(country_code="mex", country_slug="mexico",         display_name_en="Mexico",         iso2="mx", default_language="es", supported_languages=("es", "en")),
    NationConfig(country_code="usa", country_slug="united_states",  display_name_en="United States",  iso2="us", default_language="en", supported_languages=("en", "es")),
    NationConfig(country_code="ven", country_slug="venezuela",      display_name_en="Venezuela",      iso2="ve", default_language="es", supported_languages=("es", "en")),
]

assert len(NATION_CONFIGS) == 4, f"expected 4 American nations, got {len(NATION_CONFIGS)}"

CONFIG_BY_SLUG: dict[str, NationConfig] = {cfg.country_slug: cfg for cfg in NATION_CONFIGS}


# ─── The factory ──────────────────────────────────────────────────────────


def _build_vertical_resource(
    config: NationConfig,
    vertical: VERTICAL,
    *,
    source_module: str | None = None,
) -> "dlt.resource":
    """Build one ``@dlt.resource`` per (nation, vertical) pair."""
    nation = _NationCore(
        country_code=config.country_code,
        domain=vertical,
        source_slug=f"{config.country_slug}-{vertical}",
        supported_languages=config.supported_languages,
        default_language=config.default_language,
    )

    @dlt.resource(
        name=f"{config.country_slug}_{vertical}",
        write_disposition="merge",
        primary_key="document_id",
    )
    def _resource() -> "list[dict]":
        if source_module:
            try:
                mod = importlib.import_module(source_module)
            except ImportError:
                mod = None
        else:
            mod = None

        if mod is not None and hasattr(mod, "iter_rows"):
            yield from mod.iter_rows(nation)
            return

        for cache_path in nation.iter_local_cache():
            row = _row_from_cache(cache_path, nation)
            if row:
                yield row

    return _resource


def nation_source_factory(
    config: NationConfig,
    *,
    source_module_prefix: str = "dlt_sources.american_nations",
) -> "dlt.source":
    """Build the per-nation ``@dlt.source`` for one American nation.

    Emits 5 ``@dlt.resource`` (one per vertical). The source name is
    ``american_nations_<country_slug>``.
    """
    resources = []
    for vertical in config.verticals:
        source_module = f"{source_module_prefix}.{config.country_slug}.{vertical}"
        resources.append(_build_vertical_resource(config, vertical, source_module=source_module))

    @dlt.source(name=f"american_nations_{config.country_slug}")
    def _source():
        return resources

    _source.__name__ = f"{config.country_slug}_source"
    _source.__qualname__ = f"{config.country_slug}_source"
    return _source


# Build all 4 per-nation source bindings + inject into module globals.
__all__ = ["NATION_CONFIGS", "NationConfig", "CONFIG_BY_SLUG", "nation_source_factory"]

for _config in NATION_CONFIGS:
    _source_name = f"{_config.country_slug}_source"
    globals()[_source_name] = nation_source_factory(_config)
    __all__.append(_source_name)
