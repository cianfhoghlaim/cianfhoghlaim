"""dlt_sources/commonwealth/_factory.py — single source of truth for the Commonwealth nations + Canada provinces + Nigeria states.

This module replaces the 56 per-jurisdiction stub files that previously
lived at
``dlt_sources/commonwealth/<nation>/__init__.py`` +
``dlt_sources/commonwealth/canada/provinces/<province>/__init__.py`` +
``dlt_sources/commonwealth/nigeria/states/<state>/__init__.py``
with a single factory that parameterises on the canonical config
tables (6 nations + 13 provinces + 37 states).

Per the **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** openspec
change (Phase 1.2), the per-jurisdiction stub ``__init__.py`` files
collapse to 1-line re-export shims:
    from dlt_sources.commonwealth._factory import nigeria_source
    from dlt_sources.commonwealth._factory import alberta_source
    from dlt_sources.commonwealth._factory import abia_source

Each shim exposes exactly the same ``<jurisdiction_slug>_source``
binding that the factory injects at module load time, so any caller
that previously did
``from dlt_sources.commonwealth.nigeria import nigeria_source``
continues to work.

Note: per the v2 plan the Commonwealth factory also covers the 13
Canadian provinces (under ``canada/provinces/``) and the 36+1
Nigerian states (under ``nigeria/states/``). The factory exposes
them as flat bindings (``alberta_source``, ``abia_source``) so the
import path matches the user-confirmed "BCP-47-friendly" convention
— callers do not need to know whether a jurisdiction lives under
``/canada/provinces/`` or ``/nigeria/states/``.
"""
from __future__ import annotations

import importlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import dlt
from pydantic import BaseModel, ConfigDict, Field


# ─── Canonical cache root (mirrors the European nations pattern) ──────────

_COMMONWEALTH_CACHE_ROOT: Path = Path(
    os.environ.get(
        "COMMONWEALTH_SCRAPE_CACHE_ROOT",
        str(
            Path(__file__).resolve().parents[2]
            / "stedding"
            / "ingest_queue"
            / "commonwealth"
        ),
    )
)
"""Canonical local scrape cache root for the Commonwealth pipeline."""


VERTICAL = Literal["education", "government", "law", "medicine", "statistics"]


@dataclass
class _JurisdictionCore:
    """Minimal per-jurisdiction primitive used by the Commonwealth factory.

    Mirrors the ``NationSource`` contract (pre-§11 dataclass) so the
    factory can yield the canonical row shape. Supports the broader
    "jurisdiction" abstraction (Commonwealth nations + sub-national
    provinces/states) without dragging in the BI-jurisdiction
    validation that the §11-merged ``JurisdictionPipelineBase`` adds.
    """

    country_code: str
    domain: str
    source_slug: str
    region: str = "commonwealth"
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
        return _COMMONWEALTH_CACHE_ROOT / self.country_code / self.domain / lang

    def iter_local_cache(self):
        lang_dir = self.cache_path(self.default_language)
        if not lang_dir.exists():
            return
        for json_path in sorted(lang_dir.glob("*.json")):
            yield json_path


def _row_from_cache(cache_path: Path, nation: _JurisdictionCore, *, document_id_key: str = "document_id") -> dict[str, Any]:
    """Parse a per-jurisdiction cache JSON snapshot into a DLT row."""
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


# ─── Pydantic config models ──────────────────────────────────────────────


class NationConfig(BaseModel):
    """Canonical 6-row ISO-3 table for the 6 Commonwealth nations.

    Sourced from ``dlt_sources/LEGACY_ALIASES.md`` (the v7
    ISO-3 → snake_case rename map).
    """

    model_config = ConfigDict(frozen=True)

    country_code: str = Field(..., min_length=3, max_length=3, description="ISO 3166-1 alpha-3 in lowercase.")
    country_slug: str = Field(..., description="snake_case directory slug.")
    display_name_en: str
    iso2: str = Field(..., min_length=2, max_length=2)
    default_language: str = "en"
    supported_languages: tuple[str, ...] = ("en",)
    region: Literal["commonwealth"] = "commonwealth"
    verticals: list[VERTICAL] = Field(
        default_factory=lambda: ["education", "government", "law", "medicine", "statistics"],
    )


class SubNationalConfig(BaseModel):
    """Canonical config for a sub-national jurisdiction (province or state).

    Distinct from ``NationConfig`` because the parent country is
    implicit (the binding name carries the province/state slug), and
    the ``country_code`` field holds the sub-national code (the ISO-3
    code for Canadian provinces uses the 2-letter ISO 3166-2 code,
    while Nigerian states use the NGA-XXX code).
    """

    model_config = ConfigDict(frozen=True)

    jurisdiction_slug: str = Field(..., description="snake_case directory slug.")
    jurisdiction_code: str = Field(..., description="Sub-national code (ISO 3166-2 for Canadian provinces, NGA-XXX for Nigerian states).")
    parent_country: str = Field(..., description="Parent country slug (e.g. 'canada', 'nigeria').")
    parent_country_code: str = Field(..., description="Parent country ISO-3 code (e.g. 'can', 'nga').")
    display_name_en: str
    verticals: list[VERTICAL] = Field(
        default_factory=lambda: ["education", "government", "law", "medicine", "statistics"],
    )


# ─── The canonical 6-row Commonwealth nation table ───────────────────────


NATION_CONFIGS: list[NationConfig] = [
    NationConfig(country_code="aus", country_slug="australia",    display_name_en="Australia",     iso2="au", default_language="en", supported_languages=("en",)),
    NationConfig(country_code="can", country_slug="canada",       display_name_en="Canada",        iso2="ca", default_language="en", supported_languages=("en", "fr")),
    NationConfig(country_code="ind", country_slug="india",        display_name_en="India",         iso2="in", default_language="en", supported_languages=("en", "hi")),
    NationConfig(country_code="nga", country_slug="nigeria",      display_name_en="Nigeria",       iso2="ng", default_language="en", supported_languages=("en",)),
    NationConfig(country_code="nzl", country_slug="new_zealand",  display_name_en="New Zealand",   iso2="nz", default_language="en", supported_languages=("en", "mi")),
    NationConfig(country_code="zaf", country_slug="south_africa", display_name_en="South Africa",  iso2="za", default_language="en", supported_languages=("en", "af", "zu", "xh", "st", "tn", "ss", "ve", "ts", "nr")),
]

assert len(NATION_CONFIGS) == 6, f"expected 6 Commonwealth nations, got {len(NATION_CONFIGS)}"


# ─── The 13 Canadian provinces (under canada/provinces/) ─────────────────


PROVINCE_CONFIGS: list[SubNationalConfig] = [
    SubNationalConfig(jurisdiction_slug="alberta",                  jurisdiction_code="ca-ab", parent_country="canada", parent_country_code="can", display_name_en="Alberta"),
    SubNationalConfig(jurisdiction_slug="british_columbia",        jurisdiction_code="ca-bc", parent_country="canada", parent_country_code="can", display_name_en="British Columbia"),
    SubNationalConfig(jurisdiction_slug="manitoba",                 jurisdiction_code="ca-mb", parent_country="canada", parent_country_code="can", display_name_en="Manitoba"),
    SubNationalConfig(jurisdiction_slug="new_brunswick",            jurisdiction_code="ca-nb", parent_country="canada", parent_country_code="can", display_name_en="New Brunswick"),
    SubNationalConfig(jurisdiction_slug="newfoundland_and_labrador", jurisdiction_code="ca-nl", parent_country="canada", parent_country_code="can", display_name_en="Newfoundland and Labrador"),
    SubNationalConfig(jurisdiction_slug="nova_scotia",              jurisdiction_code="ca-ns", parent_country="canada", parent_country_code="can", display_name_en="Nova Scotia"),
    SubNationalConfig(jurisdiction_slug="ontario",                  jurisdiction_code="ca-on", parent_country="canada", parent_country_code="can", display_name_en="Ontario"),
    SubNationalConfig(jurisdiction_slug="prince_edward_island",     jurisdiction_code="ca-pe", parent_country="canada", parent_country_code="can", display_name_en="Prince Edward Island"),
    SubNationalConfig(jurisdiction_slug="quebec",                   jurisdiction_code="ca-qc", parent_country="canada", parent_country_code="can", display_name_en="Quebec"),
    SubNationalConfig(jurisdiction_slug="saskatchewan",             jurisdiction_code="ca-sk", parent_country="canada", parent_country_code="can", display_name_en="Saskatchewan"),
    # The 3 Canadian territories are co-equal with provinces for this
    # factory surface (they have legislatures + statute books + education
    # ministries, just not "province" in the strict constitutional sense).
    SubNationalConfig(jurisdiction_slug="northwest_territories",    jurisdiction_code="ca-nt", parent_country="canada", parent_country_code="can", display_name_en="Northwest Territories"),
    SubNationalConfig(jurisdiction_slug="nunavut",                  jurisdiction_code="ca-nu", parent_country="canada", parent_country_code="can", display_name_en="Nunavut"),
    SubNationalConfig(jurisdiction_slug="yukon",                    jurisdiction_code="ca-yt", parent_country="canada", parent_country_code="can", display_name_en="Yukon"),
]

assert len(PROVINCE_CONFIGS) == 13, f"expected 13 Canadian provinces/territories, got {len(PROVINCE_CONFIGS)}"


# ─── The 37 Nigerian states + FCT (under nigeria/states/) ────────────────


STATE_CONFIGS: list[SubNationalConfig] = [
    SubNationalConfig(jurisdiction_slug="abia",                       jurisdiction_code="nga-abi", parent_country="nigeria", parent_country_code="nga", display_name_en="Abia"),
    SubNationalConfig(jurisdiction_slug="adamawa",                    jurisdiction_code="nga-ada", parent_country="nigeria", parent_country_code="nga", display_name_en="Adamawa"),
    SubNationalConfig(jurisdiction_slug="akwa_ibom",                  jurisdiction_code="nga-aki", parent_country="nigeria", parent_country_code="nga", display_name_en="Akwa Ibom"),
    SubNationalConfig(jurisdiction_slug="anambra",                    jurisdiction_code="nga-ana", parent_country="nigeria", parent_country_code="nga", display_name_en="Anambra"),
    SubNationalConfig(jurisdiction_slug="bauchi",                     jurisdiction_code="nga-bau", parent_country="nigeria", parent_country_code="nga", display_name_en="Bauchi"),
    SubNationalConfig(jurisdiction_slug="bayelsa",                    jurisdiction_code="nga-bay", parent_country="nigeria", parent_country_code="nga", display_name_en="Bayelsa"),
    SubNationalConfig(jurisdiction_slug="benue",                      jurisdiction_code="nga-ben", parent_country="nigeria", parent_country_code="nga", display_name_en="Benue"),
    SubNationalConfig(jurisdiction_slug="borno",                      jurisdiction_code="nga-bor", parent_country="nigeria", parent_country_code="nga", display_name_en="Borno"),
    SubNationalConfig(jurisdiction_slug="cross_river",                jurisdiction_code="nga-crs", parent_country="nigeria", parent_country_code="nga", display_name_en="Cross River"),
    SubNationalConfig(jurisdiction_slug="delta",                      jurisdiction_code="nga-del", parent_country="nigeria", parent_country_code="nga", display_name_en="Delta"),
    SubNationalConfig(jurisdiction_slug="ebonyi",                     jurisdiction_code="nga-ebi", parent_country="nigeria", parent_country_code="nga", display_name_en="Ebonyi"),
    SubNationalConfig(jurisdiction_slug="edo",                        jurisdiction_code="nga-edo", parent_country="nigeria", parent_country_code="nga", display_name_en="Edo"),
    SubNationalConfig(jurisdiction_slug="ekiti",                      jurisdiction_code="nga-eki", parent_country="nigeria", parent_country_code="nga", display_name_en="Ekiti"),
    SubNationalConfig(jurisdiction_slug="enugu",                      jurisdiction_code="nga-en", parent_country="nigeria", parent_country_code="nga", display_name_en="Enugu"),
    SubNationalConfig(jurisdiction_slug="federal_capital_territory",  jurisdiction_code="nga-fct", parent_country="nigeria", parent_country_code="nga", display_name_en="Federal Capital Territory (Abuja)"),
    SubNationalConfig(jurisdiction_slug="gombe",                      jurisdiction_code="nga-gom", parent_country="nigeria", parent_country_code="nga", display_name_en="Gombe"),
    SubNationalConfig(jurisdiction_slug="imo",                        jurisdiction_code="nga-imo", parent_country="nigeria", parent_country_code="nga", display_name_en="Imo"),
    SubNationalConfig(jurisdiction_slug="jigawa",                     jurisdiction_code="nga-jig", parent_country="nigeria", parent_country_code="nga", display_name_en="Jigawa"),
    SubNationalConfig(jurisdiction_slug="kaduna",                     jurisdiction_code="nga-kad", parent_country="nigeria", parent_country_code="nga", display_name_en="Kaduna"),
    SubNationalConfig(jurisdiction_slug="kano",                       jurisdiction_code="nga-kan", parent_country="nigeria", parent_country_code="nga", display_name_en="Kano"),
    SubNationalConfig(jurisdiction_slug="katsina",                    jurisdiction_code="nga-kat", parent_country="nigeria", parent_country_code="nga", display_name_en="Katsina"),
    SubNationalConfig(jurisdiction_slug="kebbi",                      jurisdiction_code="nga-keb", parent_country="nigeria", parent_country_code="nga", display_name_en="Kebbi"),
    SubNationalConfig(jurisdiction_slug="kogi",                       jurisdiction_code="nga-kog", parent_country="nigeria", parent_country_code="nga", display_name_en="Kogi"),
    SubNationalConfig(jurisdiction_slug="kwara",                      jurisdiction_code="nga-kwa", parent_country="nigeria", parent_country_code="nga", display_name_en="Kwara"),
    SubNationalConfig(jurisdiction_slug="lagos",                      jurisdiction_code="nga-los", parent_country="nigeria", parent_country_code="nga", display_name_en="Lagos"),
    SubNationalConfig(jurisdiction_slug="nasarawa",                   jurisdiction_code="nga-nas", parent_country="nigeria", parent_country_code="nga", display_name_en="Nasarawa"),
    SubNationalConfig(jurisdiction_slug="niger",                      jurisdiction_code="nga-ngr", parent_country="nigeria", parent_country_code="nga", display_name_en="Niger"),
    SubNationalConfig(jurisdiction_slug="ogun",                       jurisdiction_code="nga-ogn", parent_country="nigeria", parent_country_code="nga", display_name_en="Ogun"),
    SubNationalConfig(jurisdiction_slug="ondo",                       jurisdiction_code="nga-ond", parent_country="nigeria", parent_country_code="nga", display_name_en="Ondo"),
    SubNationalConfig(jurisdiction_slug="osun",                       jurisdiction_code="nga-osn", parent_country="nigeria", parent_country_code="nga", display_name_en="Osun"),
    SubNationalConfig(jurisdiction_slug="oyo",                        jurisdiction_code="nga-oyo", parent_country="nigeria", parent_country_code="nga", display_name_en="Oyo"),
    SubNationalConfig(jurisdiction_slug="plateau",                    jurisdiction_code="nga-plt", parent_country="nigeria", parent_country_code="nga", display_name_en="Plateau"),
    SubNationalConfig(jurisdiction_slug="rivers",                     jurisdiction_code="nga-riv", parent_country="nigeria", parent_country_code="nga", display_name_en="Rivers"),
    SubNationalConfig(jurisdiction_slug="sokoto",                     jurisdiction_code="nga-sok", parent_country="nigeria", parent_country_code="nga", display_name_en="Sokoto"),
    SubNationalConfig(jurisdiction_slug="taraba",                     jurisdiction_code="nga-tar", parent_country="nigeria", parent_country_code="nga", display_name_en="Taraba"),
    SubNationalConfig(jurisdiction_slug="yobe",                       jurisdiction_code="nga-yob", parent_country="nigeria", parent_country_code="nga", display_name_en="Yobe"),
    SubNationalConfig(jurisdiction_slug="zamfara",                    jurisdiction_code="nga-zam", parent_country="nigeria", parent_country_code="nga", display_name_en="Zamfara"),
]

# The v2 plan §1.2 states 36 states; the filesystem + LEGACY_ALIASES.md
# include the FCT (federal_capital_territory) for a total of 37 entries.
# The factory accepts 37; the v2 plan count of "36 states" excludes the
# FCT because it is technically the federal capital territory, not a
# state. Both counts are tracked in the post-collapse report.
assert len(STATE_CONFIGS) == 37, f"expected 37 Nigerian states+FCT, got {len(STATE_CONFIGS)}"


CONFIG_BY_SLUG: dict[str, NationConfig] = {cfg.country_slug: cfg for cfg in NATION_CONFIGS}
SUBNATIONAL_BY_SLUG: dict[str, SubNationalConfig] = {
    cfg.jurisdiction_slug: cfg for cfg in PROVINCE_CONFIGS + STATE_CONFIGS
}


# ─── The factory ──────────────────────────────────────────────────────────


def _build_vertical_resource(
    country_code: str,
    region: str,
    country_slug: str,
    verticals: list[VERTICAL],
    vertical: VERTICAL,
    *,
    source_module: str | None = None,
    default_language: str = "en",
    supported_languages: tuple[str, ...] = ("en",),
) -> "dlt.resource":
    """Build one ``@dlt.resource`` per (jurisdiction, vertical) pair.

    Mirrors the European-nations factory — imports the per-vertical
    package lazily + falls back to the canonical cache walk when the
    per-vertical module exposes an ``iter_rows`` callable.
    """
    nation = _JurisdictionCore(
        country_code=country_code,
        domain=vertical,
        source_slug=f"{country_slug}-{vertical}",
        region=region,
        supported_languages=supported_languages,
        default_language=default_language,
    )

    @dlt.resource(
        name=f"{country_slug}_{vertical}",
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


def _build_nation_source(config: NationConfig, *, source_module_prefix: str = "dlt_sources.commonwealth") -> "dlt.source":
    """Build the per-nation ``@dlt.source`` for one Commonwealth nation.

    Emits 5 ``@dlt.resource`` (one per vertical). The source name is
    ``commonwealth_<country_slug>``.
    """
    resources = []
    for vertical in config.verticals:
        source_module = f"{source_module_prefix}.{config.country_slug}.{vertical}"
        resources.append(
            _build_vertical_resource(
                country_code=config.country_code,
                region=config.region,
                country_slug=config.country_slug,
                verticals=config.verticals,
                vertical=vertical,
                source_module=source_module,
                default_language=config.default_language,
                supported_languages=config.supported_languages,
            )
        )

    @dlt.source(name=f"commonwealth_{config.country_slug}")
    def _source():
        return resources

    _source.__name__ = f"{config.country_slug}_source"
    _source.__qualname__ = f"{config.country_slug}_source"
    return _source


def _build_subnational_source(config: SubNationalConfig, *, source_module_prefix: str = "dlt_sources.commonwealth") -> "dlt.source":
    """Build the per-sub-national ``@dlt.source`` for one province / state.

    Emits 5 ``@dlt.resource``. The source name is
    ``commonwealth_<parent>_<jurisdiction_slug>``.
    """
    resources = []
    for vertical in config.verticals:
        source_module = f"{source_module_prefix}.{config.parent_country}.{('provinces' if config.parent_country == 'canada' else 'states')}.{config.jurisdiction_slug}.{vertical}"
        resources.append(
            _build_vertical_resource(
                country_code=config.jurisdiction_code,
                region=f"commonwealth.{config.parent_country}",
                country_slug=f"{config.parent_country}_{config.jurisdiction_slug}",
                verticals=config.verticals,
                vertical=vertical,
                source_module=source_module,
            )
        )

    @dlt.source(name=f"commonwealth_{config.parent_country}_{config.jurisdiction_slug}")
    def _source():
        return resources

    _source.__name__ = f"{config.jurisdiction_slug}_source"
    _source.__qualname__ = f"{config.jurisdiction_slug}_source"
    return _source


def nation_source_factory(
    config: NationConfig | SubNationalConfig,
    *,
    source_module_prefix: str = "dlt_sources.commonwealth",
) -> "dlt.source":
    """Dispatch to ``_build_nation_source`` or ``_build_subnational_source``.

    Single entry point so callers (per-jurisdiction ``__init__.py``
    shims) do not need to discriminate between the two config types.
    """
    if isinstance(config, SubNationalConfig):
        return _build_subnational_source(config, source_module_prefix=source_module_prefix)
    return _build_nation_source(config, source_module_prefix=source_module_prefix)


# Build all 56 per-jurisdiction source bindings + inject into module globals.
__all__ = ["NATION_CONFIGS", "PROVINCE_CONFIGS", "STATE_CONFIGS", "NationConfig", "SubNationalConfig",
           "CONFIG_BY_SLUG", "SUBNATIONAL_BY_SLUG", "nation_source_factory"]

for _config in NATION_CONFIGS:
    _source_name = f"{_config.country_slug}_source"
    globals()[_source_name] = nation_source_factory(_config)
    __all__.append(_source_name)

for _config in PROVINCE_CONFIGS + STATE_CONFIGS:
    _source_name = f"{_config.jurisdiction_slug}_source"
    globals()[_source_name] = nation_source_factory(_config)
    __all__.append(_source_name)
