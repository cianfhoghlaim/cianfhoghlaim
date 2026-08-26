"""dlt_sources/european_nations/_factory.py — single source of truth for the 40 EU + UK + UA + TR + GE + XK nations.

This module replaces the 40 per-nation stub files that previously lived at
``dlt_sources/european_nations/<nation>/__init__.py`` with a single
factory that parameterises on the canonical 40-row ISO-3 table.

Each factory-built DLT source conforms to the canonical
``NationSource`` contract (see ``._shared.nation_source``): every
emitted row carries ``country_code`` + ``language`` + ``domain`` +
the canonical DuckLake namespace.

Per the **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** openspec
change (Phase 1.1), the 40 per-nation stub ``__init__.py`` files
collapse to 1-line re-export shims:
    from dlt_sources.european_nations._factory import poland_source

Each per-nation ``__init__.py`` exposes exactly the same
``<nation_slug>_source`` binding that the factory injects at module
load time, so any caller that previously did
``from dlt_sources.european_nations.poland import poland_source``
continues to work.
"""
from __future__ import annotations

import importlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any, Literal

import dlt
from pydantic import BaseModel, ConfigDict, Field


# ─── Canonical cache root (mirrors the merged §11 helper) ────────────────

EU_NATIONS_CACHE_ROOT: Path = Path(
    os.environ.get(
        "EU_NATIONS_SCRAPE_CACHE_ROOT",
        str(
            Path(__file__).resolve().parents[3]
            / "stedding"
            / "ingest_queue"
            / "european_nations"
        ),
    )
)
"""Canonical local scrape cache root for the EU nations pipeline.

Mirrors the constant exposed by both
``dlt_sources.european_nations._shared.nation_source`` (the legacy
pre-§11 module, now deprecated) and the merged
``dlt_sources.british_isles._cross.jurisdiction_pipeline_base``
(§11 of the multi-repo scaffold change).
"""


@dataclass
class _NationCore:
    """Minimal per-nation primitive used by the factory.

    Mirrors the pre-§11 ``NationSource`` dataclass (the API the 51
    per-nation source files were originally written against). Avoids
    the BI-jurisdiction validation that the §11-merged
    ``JurisdictionPipelineBase`` adds — the EU + UK + UA + TR + GE
    + XK ISO-3 codes are not BI jurisdictions and would otherwise be
    rejected at construction time.

    The shape is intentionally compatible with
    ``row_from_cache(...)`` (exposes ``country_code`` / ``domain`` /
    ``document_type`` / ``source_slug`` attributes) so the factory
    can delegate row construction to the canonical helper.
    """

    country_code: str
    domain: str
    source_slug: str
    supported_languages: tuple[str, ...] = ("en",)
    default_language: str | None = None
    document_type: str = "official_document"
    extra_metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.default_language:
            self.default_language = self.supported_languages[0]

    @property
    def source_id(self) -> str:
        return (
            f"european_nations.{self.country_code}.{self.domain}"
            f".{self.source_slug}"
        )

    @property
    def ducklake_table(self) -> str:
        return f"oideachais.{self.domain}.european_nations.{self.country_code}"

    def cache_path(self, language: str | None = None) -> Path:
        lang = language or self.default_language
        return EU_NATIONS_CACHE_ROOT / self.country_code / self.domain / lang

    def iter_local_cache(self):
        lang_dir = self.cache_path(self.default_language)
        if not lang_dir.exists():
            return
        for json_path in sorted(lang_dir.glob("*.json")):
            yield json_path


def _row_from_cache(cache_path: Path, nation: _NationCore, *, document_id_key: str = "document_id") -> dict[str, Any]:
    """Parse a per-nation cache JSON snapshot into a DLT row.

    Mirrors ``dlt_sources.european_nations._shared.nation_source.row_from_cache``
    (now deprecated) and the §11-merged version in
    ``jurisdiction_pipeline_base.py``. Inlined here so the factory
    carries no dependency on either module.
    """
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
        "region": "european_nations",
        "official_status": metadata.get("official_status", "in_force"),
        "extracted_at": datetime.now(UTC).isoformat(),
        "source": nation.source_slug,
        "source_file": str(cache_path),
    }

VERTICAL = Literal["education", "government", "law", "medicine", "statistics"]


class NationConfig(BaseModel):
    """Canonical 40-row ISO-3 table for the European-nations subtree.

    Mirrors the CocoIndex precedent at
    ``cocoindex_flows/european_nations/_factory.py:NationConfig`` —
    same ISO-3 codes, same display names, same vertical list, so the
    CocoIndex embedder surface and the DLT source surface stay
    in lock-step.
    """

    model_config = ConfigDict(frozen=True)

    country_code: str = Field(..., min_length=3, max_length=3, description="ISO 3166-1 alpha-3 in lowercase (e.g. 'pol').")
    country_slug: str = Field(..., min_length=2, description="snake_case directory slug (e.g. 'bosnia_and_herzegovina').")
    display_name_en: str = Field(..., description="English display name (e.g. 'Poland').")
    display_name_local: str = Field(default="", description="Local-language display name (e.g. 'Polska'); empty for English-only.")
    iso2: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 in lowercase.")
    default_language: str = Field(..., description="Default language tag (ISO 639-1, e.g. 'pl').")
    supported_languages: tuple[str, ...] = Field(default=("en",), description="Official language tags.")
    verticals: list[VERTICAL] = Field(
        default_factory=lambda: ["education", "government", "law", "medicine", "statistics"],
    )


# ─── The canonical 40-row ISO-3 table ──────────────────────────────────────

NATION_CONFIGS: list[NationConfig] = [
    NationConfig(country_code="alb", country_slug="albania",                     display_name_en="Albania",                display_name_local="Shqipëria",      iso2="al", default_language="sq", supported_languages=("sq", "en")),
    NationConfig(country_code="aut", country_slug="austria",                     display_name_en="Austria",                display_name_local="Österreich",      iso2="at", default_language="de", supported_languages=("de", "en")),
    NationConfig(country_code="bel", country_slug="belgium",                     display_name_en="Belgium",                display_name_local="België",          iso2="be", default_language="nl", supported_languages=("nl", "fr", "de", "en")),
    NationConfig(country_code="bih", country_slug="bosnia_and_herzegovina",     display_name_en="Bosnia and Herzegovina", display_name_local="Bosna i Hercegovina", iso2="ba", default_language="bs", supported_languages=("bs", "hr", "sr", "en")),
    NationConfig(country_code="bgr", country_slug="bulgaria",                   display_name_en="Bulgaria",               display_name_local="България",        iso2="bg", default_language="bg", supported_languages=("bg", "en")),
    NationConfig(country_code="hrv", country_slug="croatia",                    display_name_en="Croatia",                display_name_local="Hrvatska",        iso2="hr", default_language="hr", supported_languages=("hr", "en")),
    NationConfig(country_code="cyp", country_slug="cyprus",                     display_name_en="Cyprus",                 display_name_local="Κύπρος",          iso2="cy", default_language="el", supported_languages=("el", "tr", "en")),
    NationConfig(country_code="cze", country_slug="czechia",                    display_name_en="Czechia",                display_name_local="Česko",           iso2="cz", default_language="cs", supported_languages=("cs", "en")),
    NationConfig(country_code="dnk", country_slug="denmark",                    display_name_en="Denmark",                display_name_local="Danmark",         iso2="dk", default_language="da", supported_languages=("da", "en")),
    NationConfig(country_code="est", country_slug="estonia",                    display_name_en="Estonia",                display_name_local="Eesti",           iso2="ee", default_language="et", supported_languages=("et", "en")),
    NationConfig(country_code="fin", country_slug="finland",                    display_name_en="Finland",                display_name_local="Suomi",           iso2="fi", default_language="fi", supported_languages=("fi", "sv", "en")),
    NationConfig(country_code="fra", country_slug="france",                     display_name_en="France",                 display_name_local="France",          iso2="fr", default_language="fr", supported_languages=("fr", "en")),
    NationConfig(country_code="geo", country_slug="georgia",                    display_name_en="Georgia",                display_name_local="საქართველო",    iso2="ge", default_language="ka", supported_languages=("ka", "en")),
    NationConfig(country_code="deu", country_slug="germany",                    display_name_en="Germany",                display_name_local="Deutschland",     iso2="de", default_language="de", supported_languages=("de", "en")),
    NationConfig(country_code="grc", country_slug="greece",                     display_name_en="Greece",                 display_name_local="Ελλάδα",          iso2="gr", default_language="el", supported_languages=("el", "en")),
    NationConfig(country_code="hun", country_slug="hungary",                    display_name_en="Hungary",                display_name_local="Magyarország",    iso2="hu", default_language="hu", supported_languages=("hu", "en")),
    NationConfig(country_code="isl", country_slug="iceland",                    display_name_en="Iceland",                display_name_local="Ísland",          iso2="is", default_language="is", supported_languages=("is", "en")),
    NationConfig(country_code="ita", country_slug="italy",                      display_name_en="Italy",                  display_name_local="Italia",          iso2="it", default_language="it", supported_languages=("it", "en")),
    NationConfig(country_code="xkx", country_slug="kosovo",                     display_name_en="Kosovo",                 display_name_local="Kosova",          iso2="xk", default_language="sq", supported_languages=("sq", "sr", "en")),
    NationConfig(country_code="lva", country_slug="latvia",                     display_name_en="Latvia",                 display_name_local="Latvija",         iso2="lv", default_language="lv", supported_languages=("lv", "en")),
    NationConfig(country_code="lie", country_slug="liechtenstein",              display_name_en="Liechtenstein",          display_name_local="Liechtenstein",   iso2="li", default_language="de", supported_languages=("de", "en")),
    NationConfig(country_code="ltu", country_slug="lithuania",                  display_name_en="Lithuania",              display_name_local="Lietuva",         iso2="lt", default_language="lt", supported_languages=("lt", "en")),
    NationConfig(country_code="lux", country_slug="luxembourg",                 display_name_en="Luxembourg",             display_name_local="Lëtzebuerg",      iso2="lu", default_language="fr", supported_languages=("fr", "de", "lb", "en")),
    NationConfig(country_code="mlt", country_slug="malta",                      display_name_en="Malta",                  display_name_local="Malta",           iso2="mt", default_language="mt", supported_languages=("mt", "en")),
    NationConfig(country_code="mda", country_slug="moldova",                    display_name_en="Moldova",                display_name_local="Moldova",         iso2="md", default_language="ro", supported_languages=("ro", "en")),
    NationConfig(country_code="mne", country_slug="montenegro",                 display_name_en="Montenegro",             display_name_local="Crna Gora",       iso2="me", default_language="sr", supported_languages=("sr", "en")),
    NationConfig(country_code="nld", country_slug="netherlands",                 display_name_en="Netherlands",             display_name_local="Nederland",       iso2="nl", default_language="nl", supported_languages=("nl", "en")),
    NationConfig(country_code="mkd", country_slug="north_macedonia",            display_name_en="North Macedonia",        display_name_local="Северна Македонија", iso2="mk", default_language="mk", supported_languages=("mk", "en")),
    NationConfig(country_code="nor", country_slug="norway",                     display_name_en="Norway",                 display_name_local="Norge",           iso2="no", default_language="nb", supported_languages=("nb", "nn", "en")),
    NationConfig(country_code="pol", country_slug="poland",                     display_name_en="Poland",                 display_name_local="Polska",          iso2="pl", default_language="pl", supported_languages=("pl", "en")),
    NationConfig(country_code="prt", country_slug="portugal",                   display_name_en="Portugal",               display_name_local="Portugal",        iso2="pt", default_language="pt", supported_languages=("pt", "en")),
    NationConfig(country_code="rou", country_slug="romania",                    display_name_en="Romania",                display_name_local="România",         iso2="ro", default_language="ro", supported_languages=("ro", "en")),
    NationConfig(country_code="srb", country_slug="serbia",                     display_name_en="Serbia",                 display_name_local="Србија",          iso2="rs", default_language="sr", supported_languages=("sr", "en")),
    NationConfig(country_code="svk", country_slug="slovakia",                   display_name_en="Slovakia",               display_name_local="Slovensko",       iso2="sk", default_language="sk", supported_languages=("sk", "en")),
    NationConfig(country_code="svn", country_slug="slovenia",                   display_name_en="Slovenia",               display_name_local="Slovenija",       iso2="si", default_language="sl", supported_languages=("sl", "en")),
    NationConfig(country_code="esp", country_slug="spain",                      display_name_en="Spain",                  display_name_local="España",          iso2="es", default_language="es", supported_languages=("es", "ca", "gl", "eu", "en")),
    NationConfig(country_code="swe", country_slug="sweden",                     display_name_en="Sweden",                 display_name_local="Sverige",         iso2="se", default_language="sv", supported_languages=("sv", "en")),
    NationConfig(country_code="che", country_slug="switzerland",                display_name_en="Switzerland",            display_name_local="Schweiz/Suisse",  iso2="ch", default_language="de", supported_languages=("de", "fr", "it", "rm", "en")),
    NationConfig(country_code="tur", country_slug="turkey",                     display_name_en="Turkey",                 display_name_local="Türkiye",         iso2="tr", default_language="tr", supported_languages=("tr", "en")),
    NationConfig(country_code="ukr", country_slug="ukraine",                    display_name_en="Ukraine",                display_name_local="Україна",         iso2="ua", default_language="uk", supported_languages=("uk", "en")),
]

assert len(NATION_CONFIGS) == 40, f"expected 40 European nations, got {len(NATION_CONFIGS)}"

CONFIG_BY_SLUG: dict[str, NationConfig] = {cfg.country_slug: cfg for cfg in NATION_CONFIGS}
CONFIG_BY_ISO3: dict[str, NationConfig] = {cfg.country_code: cfg for cfg in NATION_CONFIGS}


# ─── The factory ──────────────────────────────────────────────────────────


def _build_vertical_resource(
    config: NationConfig,
    vertical: VERTICAL,
    *,
    source_module: str | None = None,
) -> "dlt.resource":
    """Build one ``@dlt.resource`` per (nation, vertical) pair.

    Each resource wraps the per-vertical package at
    ``dlt_sources/european_nations/<country_slug>/<vertical>/`` —
    importing it lazily so the factory stays decoupled from any
    specific per-vertical module that may not exist (e.g. Liechtenstein
    has no ``medicine/`` vertical yet).

    The resource yields the canonical ``row_from_cache(...)`` shape for
    every JSON snapshot in
    ``stedding/ingest_queue/european_nations/<iso3>/<vertical>/<lang>/``,
    honouring the AGENTS.md "Respect the Ingestion Cache" rule.
    """
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

        # If the per-vertical package exposes a callable ``iter_rows``,
        # delegate to it (the BIEP v3 contract). Otherwise, fall back to
        # the canonical cache walk (AGENTS.md §Ingestion Cache rule).
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
    source_module_prefix: str = "dlt_sources.european_nations",
) -> "dlt.source":
    """Build the per-nation ``@dlt.source`` for one European nation.

    Emits 5 ``@dlt.resource`` (one per vertical:
    ``education | government | law | medicine | statistics``). The
    resulting source's name is
    ``european_nations.<country_slug>``.

    Callers (the per-nation ``__init__.py`` shims) bind the result
    into module globals as ``<country_slug>_source`` at import time.
    """
    resources = []
    for vertical in config.verticals:
        source_module = f"{source_module_prefix}.{config.country_slug}.{vertical}"
        resources.append(_build_vertical_resource(config, vertical, source_module=source_module))

    @dlt.source(name=f"european_nations_{config.country_slug}")
    def _source():
        return resources

    _source.__name__ = f"{config.country_slug}_source"
    _source.__qualname__ = f"{config.country_slug}_source"
    return _source


# Build all 40 per-nation source bindings + inject into module globals.
# Backwards-compat: callers can do
#     from dlt_sources.european_nations._factory import poland_source
# or (legacy)
#     from dlt_sources.european_nations import poland
#     poland.poland_source
__all__ = ["NATION_CONFIGS", "NationConfig", "CONFIG_BY_SLUG", "CONFIG_BY_ISO3", "nation_source_factory"]

for _config in NATION_CONFIGS:
    _source_name = f"{_config.country_slug}_source"
    globals()[_source_name] = nation_source_factory(_config)
    __all__.append(_source_name)
