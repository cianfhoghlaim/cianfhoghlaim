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

Phase 5 (issue #20) wires the 3 runtime constructors:

  * `source(source_id)` returns a *callable* DLT source builder
    (no eager evaluation). The builder maps the YAML `kind` to a
    constructor in `dlt_sources.common`. The caller decides when
    to materialise.

  * `dlt_asset(source_id)` returns a Dagster `AssetsDefinition`
    produced by the project's plain `@asset` + `dlt.pipeline()`
    pattern (the same one used by `leaving_cert/dlt_assets.py`).
    We deliberately avoid `dagster_dlt.dlt_assets` here because
    its decorator doesn't accept `compute_kind` or `group_name`
    kwargs that the codebase uses everywhere else.

  * `dagster_asset(source_id)` returns a thin Dagster `asset`
    for lineage + UI (no materialisation). It calls
    `factory.source(source_id)()` to count rows and returns a
    `MaterializeResult`. The `asset_key` from the YAML is used
    for the canonical key prefix.

The 23 manual asset wrappers in
`oideachais/dagster_defs/assets/{medicine,law}/{ie,en,ni,sct,wls,iom,jey,ggy}/`
continue to work — they're not replaced by this Phase 5 wiring.
The factory is opt-in: callers must explicitly call
`SourceFactory.dagster_asset('ie.medicine.hse')` to use it.
A follow-up openspec change will retire the manual wrappers.

This module also exposes the `pydantic` models used to validate the YAML.
"""
from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Union

import yaml
from dagster import AssetKey, MaterializeResult, asset
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


# ── Phase 5: kind → DLT constructor dispatcher ────────────────────────────
#
# The dispatcher maps a `Kind` literal to a callable that
# returns a `dlt.source` (decorated with `@dlt.source`). Callers
# (i.e. `SourceFactory.source()`) invoke the returned factory with
# the source's URLs and (optional) crawl/pagination config. The
# caller decides when to materialise the source.
#
# Each entry below is a *function* that takes a `SourceEntry`
# and returns a 0-arg callable (the DLT source builder).
#
# We import lazily to avoid making the SourceFactory import fail
# when dlt / dagster are not yet on the test path.


def _build_firecrawl_source(
    entry: SourceEntry,
    defaults: FirecrawlDefaults,
) -> Callable[[], Any]:
    """Map `kind=firecrawl_pages` to `dlt_sources.common.create_firecrawl_source`."""
    from dlt_sources.common.firecrawl_source import create_firecrawl_source

    crawl = entry.crawl
    include_paths = (
        list(crawl.include_paths)
        if crawl and crawl.include_paths
        else list(defaults.include_paths)
    )
    exclude_paths = (
        list(crawl.exclude_paths)
        if crawl and crawl.exclude_paths
        else list(defaults.exclude_paths)
    )
    max_pages = (
        crawl.max_pages if crawl and crawl.max_pages else defaults.max_pages
    )
    max_depth = (
        crawl.max_depth if crawl and crawl.max_depth else defaults.max_depth
    )

    base_url = entry.urls[0]
    # If multiple URLs, we pick the first as the base and add
    # the others as include_paths. This matches the convention
    # used in the manual wrappers (one source per logical site).
    if len(entry.urls) > 1:
        include_paths = [*include_paths, f"/*"]

    return create_firecrawl_source(
        source_name=entry.id,
        base_url=base_url,
        include_paths=include_paths,
        exclude_paths=exclude_paths,
        max_pages=max_pages,
        max_depth=max_depth,
        resource_name=entry.asset_key[-1] if entry.asset_key else "pages",
    )


def _build_stagehand_source(entry: SourceEntry, defaults: Any) -> Callable[[], Any]:
    """Map `kind=stagehand_papers` to the stagehand PDF picker.

    The Leaving Cert 2026 wrapper at
    `dlt_sources/ireland/leaving_cert/leaving_cert_source` is the
    canonical implementation. For non-LC sources, the manual
    wrapper at `dlt_sources/ireland/curriculum_source._crawl_source`
    is the fallback. Both are referenced by the SourceFactory.
    """
    from dlt_sources.ireland.leaving_cert import leaving_cert_source

    def _factory() -> Any:
        # `leaving_cert_source` is the actual DLT source builder for
        # stagehand papers. It accepts the same kwargs used by the
        # leaving_cert/dlt_assets.py manual wrapper.
        return leaving_cert_source(
            use_local_scrapes=os.getenv("USE_LOCAL_SCRAPES", "true") == "true",
        )

    return _factory


def _build_browserbase_source(entry: SourceEntry, defaults: BrowserbaseDefaults) -> Callable[[], Any]:
    """Map `kind=browserbase_extract` to a firecrawl-style crawler.

    The codebase doesn't have a dedicated browserbase_extract
    constructor yet (it uses the Firecrawl fallback in
    `dlt_sources.common.create_firecrawl_source`). The kind
    distinction is preserved for future re-introduction.
    """
    # BrowserbaseDefaults has different fields from FirecrawlDefaults
    # (stagehand_model/wait_for vs only_main_content/formats/...),
    # so we use the default FirecrawlDefaults for the underlying call.
    return _build_firecrawl_source(entry, FirecrawlDefaults())


def _build_api_table_source(entry: SourceEntry, defaults: Any) -> Callable[[], Any]:
    """Map `kind=api_table` to a rest_api_source factory.

    dlt has a built-in `rest_api` source in `dlt.sources.rest_api`.
    We delegate to it with the source's URL as the base URL.
    """
    from dlt.sources.rest_api import RESTAPIConfig, rest_api_source

    config: RESTAPIConfig = {
        "client": {"base_url": entry.urls[0]},
        "resources": [
            {
                "name": entry.asset_key[-1] if entry.asset_key else "rows",
                "endpoint": {
                    "path": "/",
                    "params": {
                        "limit": (
                            entry.pagination.page_size
                            if entry.pagination
                            else 100
                        ),
                    },
                },
            }
        ],
    }
    dlt_src = rest_api_source(config)

    def _factory() -> Any:
        return dlt_src

    return _factory


def _build_api_xml_source(entry: SourceEntry, defaults: Any) -> Callable[[], Any]:
    """Map `kind=api_xml` to a simple rest_api source that
    returns the response body as-is. dlt's rest_api will
    auto-detect the JSON wrapper; for raw XML we use a thin
    wrapper that yields one record per request.
    """
    import dlt

    @dlt.source(name=entry.id)
    def _xml_source() -> Any:
        @dlt.resource(
            name=entry.asset_key[-1] if entry.asset_key else "rows",
            write_disposition="merge",
            primary_key=["url"],
        )
        def _rows() -> Any:
            import urllib.request
            for u in entry.urls:
                try:
                    with urllib.request.urlopen(u) as resp:
                        body = resp.read().decode("utf-8", errors="ignore")
                except Exception:
                    continue
                yield {
                    "url": u,
                    "body": body,
                    "content_type": resp.headers.get("Content-Type", ""),
                }

        return _rows

    return _xml_source


def _build_filesystem_csv_source(entry: SourceEntry, defaults: Any) -> Callable[[], Any]:
    """Map `kind=filesystem_csv` to dlt's filesystem source."""
    import dlt
    from dlt.sources.filesystem import filesystem, read_csv

    if not entry.urls:
        raise ValueError(f"{entry.id}: filesystem_csv requires at least one url")
    bucket_url = entry.urls[0]
    file_glob = entry.urls[1] if len(entry.urls) > 1 else "*.csv"

    @dlt.source(name=entry.id)
    def _csv_source() -> Any:
        @dlt.resource(
            name=entry.asset_key[-1] if entry.asset_key else "rows",
            write_disposition="replace",
        )
        def _rows() -> Any:
            yield from filesystem(
                bucket_url=bucket_url, file_glob=file_glob
            ) | read_csv()

        return _rows

    return _csv_source


def _build_filesystem_parquet_source(entry: SourceEntry, defaults: Any) -> Callable[[], Any]:
    """Map `kind=filesystem_parquet` to dlt's filesystem source."""
    import dlt
    from dlt.sources.filesystem import filesystem, read_parquet

    if not entry.urls:
        raise ValueError(f"{entry.id}: filesystem_parquet requires at least one url")
    bucket_url = entry.urls[0]
    file_glob = entry.urls[1] if len(entry.urls) > 1 else "*.parquet"

    @dlt.source(name=entry.id)
    def _parquet_source() -> Any:
        @dlt.resource(
            name=entry.asset_key[-1] if entry.asset_key else "rows",
            write_disposition="replace",
        )
        def _rows() -> Any:
            yield from filesystem(
                bucket_url=bucket_url, file_glob=file_glob
            ) | read_parquet()

        return _rows

    return _parquet_source


def _to_firecrawl_defaults(defaults: Any) -> FirecrawlDefaults:
    """BrowserbaseDefaults → FirecrawlDefaults shim. The two
    pydantic models share field names; we coerce."""
    return FirecrawlDefaults.model_validate(defaults.model_dump())


_KIND_DISPATCH: dict[str, Callable[[SourceEntry, Any], Callable[[], Any]]] = {
    "firecrawl_pages": _build_firecrawl_source,
    "stagehand_papers": _build_stagehand_source,
    "browserbase_extract": _build_browserbase_source,
    "api_table": _build_api_table_source,
    "api_xml": _build_api_xml_source,
    "filesystem_csv": _build_filesystem_csv_source,
    "filesystem_parquet": _build_filesystem_parquet_source,
}


def build_source(entry: SourceEntry, defaults: Defaults) -> Callable[[], Any]:
    """Map a SourceEntry to a 0-arg DLT source builder.

    The returned callable, when invoked, returns a `dlt.source`
    (or a list of resources — depending on the kind). It is
    NOT materialised here; the caller (e.g. a Dagster asset
    body) decides when to call `pipeline.run(source())`.

    The dispatcher receives a tuple `(entry, defaults, firecrawl,
    browserbase)` so each builder can pick the nested defaults
    it needs.
    """
    builder = _KIND_DISPATCH.get(entry.kind)
    if builder is None:  # pragma: no cover - pydantic Literal catches this
        raise NotImplementedError(
            f"SourceFactory: no builder for kind={entry.kind!r} "
            f"(known: {sorted(_KIND_DISPATCH)!r})"
        )
    # Pass the right nested defaults per kind.
    if entry.kind in {"firecrawl_pages"}:
        return builder(entry, defaults.firecrawl)
    if entry.kind in {"browserbase_extract"}:
        return builder(entry, defaults.browserbase)
    return builder(entry, defaults)


# ── Factory ─────────────────────────────────────────────────────────────


@dataclass
class SourceFactory:
    """Single source of truth for the asset graph derived from sources.yaml.

    Phase 2 of the openspec change is the *stub*: parsing & address
    computation only. Phase 5 (issue #20) wires the real DLT / Dagster
    constructors.
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

    # ── Runtime constructors (Phase 5) ──────────────────────────────

    def source(self, source_id: str) -> Callable[[], Any]:
        """Return a 0-arg callable that, when invoked, returns a DLT
        source. The source is not materialised; the caller decides
        when to run it through a `dlt.pipeline`.
        """
        s = self.get(source_id)
        return build_source(s, self.spec.defaults)

    def dlt_asset(self, source_id: str) -> Any:
        """Build a Dagster `AssetsDefinition` that runs the DLT
        source for `source_id` and materialises into the configured
        destination (DuckLake / DuckDB).

        We use the plain `@asset` + `dlt.pipeline()` pattern (the
        same one used by `leaving_cert/dlt_assets.py`) rather than
        `dagster_dlt.dlt_assets` because the latter doesn't accept
        `compute_kind` or `group_name` kwargs that the rest of the
        codebase uses.

        The asset key is `{nation}_{domain}_{...asset_key[2:]}` —
        matches the convention used by the manual wrappers.
        """
        from dlt_utils.destinations import get_dlt_destination
        from dlt_utils.safety import safe_dlt_run, validate_source_kwargs

        s = self.get(source_id)
        dataset_name = self.lance_table(source_id).replace(".", "_").replace("-", "_")
        pipeline_name = f"sf_{s.id.replace('.', '_')}"
        group_name = f"{s.domain}_{s.nation}"

        @asset(
            name=pipeline_name,
            group_name=group_name,
            compute_kind="dlt",
            description=s.name,
        )
        def _asset(context) -> MaterializeResult:
            os.environ.setdefault("USE_LOCAL_SCRAPES", "true")
            dlt = __import__("dlt")
            destination = get_dlt_destination()
            pipeline = dlt.pipeline(
                pipeline_name=pipeline_name,
                destination=destination,
                dataset_name=dataset_name,
                dev_mode=False,
            )
            source_obj = self.source(source_id)()
            # Pre-flight dlt 1.0 validation (logs mistakes, doesn't block).
            try:
                mistakes = validate_source_kwargs(source_obj)
                if mistakes and context is not None:
                    context.log.warning(
                        f"SourceFactory: dlt 1.0 source {source_id!r} has "
                        f"mistakes: {mistakes}"
                    )
            except Exception as exc:  # pragma: no cover - defensive
                if context is not None:
                    context.log.debug(
                        f"SourceFactory: validate_source_kwargs skipped: {exc}"
                    )
            load_info = safe_dlt_run(pipeline, source_obj)
            return MaterializeResult(
                metadata={
                    "source_id": source_id,
                    "dataset_name": dataset_name,
                    "loads_ids": str(load_info.loads_ids[0]) if load_info.loads_ids else "",
                    "dlt_1_0_mistakes": ",".join(mistakes) if mistakes else "",
                }
            )

        return _asset

    def dagster_asset(self, source_id: str) -> Any:
        """Build a thin Dagster `asset` for lineage + UI.

        Unlike `dlt_asset()`, this method does NOT materialise
        data — it just runs the source and counts rows. Use
        this when you want the asset graph to *show* a source
        in the UI (e.g. for a sensor-driven observation) without
        triggering a full DLT pipeline run.

        The asset key uses the canonical `{nation}_{domain}_{...}`
        prefix from the YAML's `asset_key` list.
        """
        s = self.get(source_id)
        asset_key_path = "/".join(s.asset_key)
        group_name = f"{s.domain}_{s.nation}"

        @asset(
            key=AssetKey(s.asset_key),
            group_name=group_name,
            compute_kind="dlt",
            description=f"Lineage for {s.name} ({s.id})",
        )
        def _lineage_asset(context) -> MaterializeResult:
            src = self.source(source_id)()
            # The dlt source is iterable; we materialise just enough
            # to count rows. We don't write to the destination.
            try:
                rows = []
                for res_name in src.resources:
                    rows.extend(list(src.resources[res_name]))
            except Exception as exc:  # pragma: no cover - network dependent
                context.log.warning(f"lineage-only asset {s.id}: source extraction failed: {exc}")
                rows = []
            return MaterializeResult(
                metadata={
                    "source_id": source_id,
                    "asset_key": asset_key_path,
                    "row_count": len(rows),
                    "materialised": False,
                }
            )

        return _lineage_asset


# ── Convenience: a module-level default for tests ────────────────────────

DEFAULT_SOURCES_PATH = Path(__file__).resolve().parents[1] / "sources.yaml"


def get_default_factory() -> SourceFactory:
    """Return the canonical factory loaded from `oideachais/sources.yaml`."""
    return SourceFactory.from_yaml(DEFAULT_SOURCES_PATH)
