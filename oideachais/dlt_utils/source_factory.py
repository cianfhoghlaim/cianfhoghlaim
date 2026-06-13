"""
oideachais.dlt_utils.source_factory — Canonical source-of-truth factory.

`SourceFactory.from_yaml(path)` parses `oideachais/sources.yaml` and
returns a factory exposing the 7‑method contract:

    factory.source(id)              -> callable DLT source
    factory.dlt_asset(id)           -> @dlt_assets decorator
    factory.dagster_asset(id)       -> @asset decorator
    factory.lance_table(id)         -> "oideachais.{domain}.{nation}.{entity}"
    factory.cognee_dataset(id)      -> "oideachais_{domain}_{nation}"
    factory.marimo_path(id)         -> Path under oideachais/notebooks/dashboards/
    factory.tests_path(id)          -> Path under oideachais/tests/dlt_sources/

The factory is a **stub** at this commit — it parses and validates but
does not yet construct runtime DLT sources / Dagster assets. The methods
return the *address* the runtime artefact SHOULD live at; phase 5 of the
openspec change wires the actual constructors.

This module also exposes the `pydantic` models used to validate the YAML.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Union

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ── Type aliases / enums ──────────────────────────────────────────────────

NationCode = Literal["ie", "ni", "en", "sct", "wls", "iom", "jey", "ggy"]
Domain = Literal["education", "medicine", "law", "statistics", "site_analysis"]
Kind = Literal[
    "firecrawl_pages",
    "stagehand_papers",
    "browserbase_extract",
    "api_table",
    "api_xml",
    "filesystem_csv",
    "filesystem_parquet",
]
Sensor = Literal["sitemap_hash", "rss", "webhook", "polling"]


# ── Nested config models ────────────────────────────────────────────────


class FirecrawlDefaults(BaseModel):
    model_config = ConfigDict(extra="forbid")
    only_main_content: bool = True
    formats: list[str] = Field(default_factory=lambda: ["markdown", "links", "html"])
    max_pages: int = 200
    max_depth: int = 3
    include_paths: list[str] = Field(default_factory=list)
    exclude_paths: list[str] = Field(default_factory=list)


class BrowserbaseDefaults(BaseModel):
    model_config = ConfigDict(extra="forbid")
    stagehand_model: str = "deepseek/deepseek-chat"
    wait_for: str = "networkidle"


class ScheduleConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cron: str = "0 4 * * *"
    timezone: str = "Europe/Dublin"


class ComplianceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    respect_robots_txt: bool = True
    licence: str = "TBD"
    contact: str | None = None
    retain_raw_snapshots_days: int = 30


class TestsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pytest_marker: str = "integration"
    uses_local_scrape_cache: bool = True


class SensorsDefaults(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sitemap_hash_check: bool = True


class CrawlConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    include_paths: list[str] = Field(default_factory=list)
    exclude_paths: list[str] = Field(default_factory=list)
    max_pages: int = 200
    max_depth: int = 3


class PaginationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["offset", "cursor", "page_number"]
    page_size: int = 100


class IncrementalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cursor_path: str = "$.next"
    field: str = "id"
    initial: str | int = "0"


class EmbeddingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    table: str
    kind: str = "page_markdown"


class KGConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dataset: str
    edges: list[str] = Field(default_factory=list)


# ── Top-level models ────────────────────────────────────────────────────


class Defaults(BaseModel):
    model_config = ConfigDict(extra="forbid")
    destination: Literal["ducklake", "iceberg", "duckdb"] = "ducklake"
    destination_database: str = "oideachais"
    embedding_model: str = "BAAI/bge-m3"
    firecrawl: FirecrawlDefaults = Field(default_factory=FirecrawlDefaults)
    browserbase: BrowserbaseDefaults = Field(default_factory=BrowserbaseDefaults)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    compliance: ComplianceConfig = Field(default_factory=ComplianceConfig)
    tests: TestsConfig = Field(default_factory=TestsConfig)
    sensors: SensorsDefaults = Field(default_factory=SensorsDefaults)


class Nation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: NationCode
    name: str
    jurisdiction: str


class SourceEntry(BaseModel):
    """One source entry from `sources.yaml`."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    domain: Domain
    nation: NationCode
    kind: Kind
    urls: list[str]
    crawl: CrawlConfig | None = None
    pagination: PaginationConfig | None = None
    incremental: IncrementalConfig | None = None
    asset_key: list[str] = Field(min_length=1)
    embedding: EmbeddingConfig | None = None
    kg: KGConfig | None = None
    schedule: ScheduleConfig | None = None
    sensors: list[Sensor] = Field(default_factory=list)
    compliance: ComplianceConfig | None = None

    @field_validator("id")
    @classmethod
    def _check_id_shape(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError(
                f"id must be of the form '{{nation}}.{{domain}}.{{entity}}' (got {v!r})"
            )
        return v

    @field_validator("urls")
    @classmethod
    def _check_urls(cls, v: list[str]) -> list[str]:
        for u in v:
            if not (u.startswith("http://") or u.startswith("https://") or u.startswith("file://") or "{" in u):
                raise ValueError(f"url {u!r} must be http(s) or contain a template placeholder")
        return v

    @model_validator(mode="after")
    def _check_asset_key(self) -> "SourceEntry":
        expected_prefix = [self.nation, self.domain]
        if self.asset_key[: len(expected_prefix)] != expected_prefix:
            raise ValueError(
                f"asset_key {self.asset_key!r} must start with nation+domain "
                f"{expected_prefix!r}"
            )
        return self


class SourcesYAML(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int
    defaults: Defaults = Field(default_factory=Defaults)
    nations: list[Nation]
    kinds: list[Kind]
    sources: list[SourceEntry]


# ── Factory ─────────────────────────────────────────────────────────────


@dataclass
class SourceFactory:
    """Single source of truth for the asset graph derived from sources.yaml.

    Phase 2 of the openspec change is the *stub*: parsing & address
    computation only. Phase 5 wires the real DLT / Dagster constructors.
    """

    yaml_path: Path
    spec: SourcesYAML
    _by_id: dict[str, SourceEntry]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "SourceFactory":
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"sources.yaml not found at {path}")
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        spec = SourcesYAML.model_validate(raw)
        return cls(yaml_path=path, spec=spec, _by_id={s.id: s for s in spec.sources})

    # ── Lookups ───────────────────────────────────────────────────────

    def get(self, source_id: str) -> SourceEntry:
        if source_id not in self._by_id:
            raise KeyError(f"source id {source_id!r} not in sources.yaml")
        return self._by_id[source_id]

    def all_ids(self) -> list[str]:
        return list(self._by_id)

    def filter(self, *, domain: str | None = None, nation: str | None = None) -> list[SourceEntry]:
        out = list(self.spec.sources)
        if domain:
            out = [s for s in out if s.domain == domain]
        if nation:
            out = [s for s in out if s.nation == nation]
        return out

    # ── Address methods (Phase 2 stub) ───────────────────────────────

    def lance_table(self, source_id: str) -> str:
        """LanceDB table address (e.g. `oideachais.education.ni.ccea_pages`)."""
        s = self.get(source_id)
        if s.embedding and s.embedding.table:
            return s.embedding.table
        return f"oideachais.{s.domain}.{s.nation}.{'_'.join(s.asset_key[2:])}"

    def cognee_dataset(self, source_id: str) -> str:
        """Cognee dataset name (e.g. `oideachais_education_ni`)."""
        s = self.get(source_id)
        if s.kg and s.kg.dataset:
            return s.kg.dataset
        return f"oideachais_{s.domain}_{s.nation}"

    def marimo_path(self, source_id: str) -> Path:
        """Path under oideachais/notebooks/dashboards/{domain}/{nation}/{entity}.py."""
        s = self.get(source_id)
        entity = s.asset_key[2] if len(s.asset_key) >= 3 else s.id.split(".")[-1]
        return Path("oideachais/notebooks/dashboards") / s.domain / s.nation / f"{entity}.py"

    def tests_path(self, source_id: str) -> Path:
        """Path under oideachais/tests/dlt_sources/{domain}/{nation}/test_{entity}.py."""
        s = self.get(source_id)
        entity = s.asset_key[2] if len(s.asset_key) >= 3 else s.id.split(".")[-1]
        return Path("oideachais/tests/dlt_sources") / s.domain / s.nation / f"test_{entity}.py"

    def asset_key(self, source_id: str) -> list[str]:
        return list(self.get(source_id).asset_key)

    # ── Runtime constructors (Phase 5 stub) ─────────────────────────
    #
    # These three are the only methods that import DLT / Dagster. They
    # currently raise NotImplementedError so the rest of the test suite
    # (and CI) can exercise the *parsing* layer without needing either.

    def source(self, source_id: str) -> Any:  # pragma: no cover - stub
        raise NotImplementedError(
            f"SourceFactory.source({source_id!r}) is wired in Phase 5 of the openspec change"
        )

    def dlt_asset(self, source_id: str) -> Any:  # pragma: no cover - stub
        raise NotImplementedError(
            f"SourceFactory.dlt_asset({source_id!r}) is wired in Phase 5 of the openspec change"
        )

    def dagster_asset(self, source_id: str) -> Any:  # pragma: no cover - stub
        raise NotImplementedError(
            f"SourceFactory.dagster_asset({source_id!r}) is wired in Phase 5 of the openspec change"
        )


# ── Convenience: a module-level default for tests ────────────────────────

DEFAULT_SOURCES_PATH = Path(__file__).resolve().parents[1] / "sources.yaml"


def get_default_factory() -> SourceFactory:
    """Return the canonical factory loaded from `oideachais/sources.yaml`."""
    return SourceFactory.from_yaml(DEFAULT_SOURCES_PATH)
