"""
Dagster Resources for Celtic Education Platform.

All resource classes and instances are defined here to avoid circular imports.
Both definitions.py and asset files should import from this module.
"""
from __future__ import annotations

import os
from pathlib import Path

from dagster import ConfigurableResource
from dagster_dlt import DagsterDltResource

# Centralised env-var matrix (the CIANFHOGHLAIM_* env vars). Imported
# once at module import; every resource below falls back to the
# canonical defaults when its legacy alias is unset.
from observability.env_config import (
    FALKORDB_HOST as _CIANFHOGHLAIM_FALKORDB_HOST,
)
from observability.env_config import (
    FALKORDB_PASSWORD as _CIANFHOGHLAIM_FALKORDB_PASSWORD,
)
from observability.env_config import (
    FALKORDB_PORT as _CIANFHOGHLAIM_FALKORDB_PORT,
)
from observability.env_config import (
    LANCEDB_URL as _CIANFHOGHLAIM_LANCEDB_URL,
)
from observability.env_config import (
    LITELLM_URL as _CIANFHOGHLAIM_LITELLM_URL,
)
from observability.env_config import (
    resolve_cognee_backend_with_fallback as _resolve_cognee_backend,
)

# ============================================================================
# Configuration
# ============================================================================

OUTPUT_PATH = Path(os.getenv("CELTIC_EDUCATION_DATA_DIR", "./storage/data"))
DUCKDB_PATH = OUTPUT_PATH / "celtic_education.duckdb"
LANCEDB_PATH = OUTPUT_PATH / "lancedb"
DUCKLAKE_PATH = OUTPUT_PATH / "ducklake"
GEOPARQUET_PATH = OUTPUT_PATH / "geoparquet"


# ============================================================================
# Storage Resources (Unified)
# ============================================================================


class DuckDBResource(ConfigurableResource):
    """Unified DuckDB resource with spatial extension support.

    Single database with schemas:
    - education: Irish curriculum content (from oideachas)
    - statistics: Multi-nation education statistics (from oideachas_oileáin)
    - celtic: Celtic language corpus (from teanga)
    - geospatial: Boundaries and spatial data
    - training: ML training datasets
    """

    database_path: str = str(DUCKDB_PATH)
    enable_spatial: bool = True

    def get_connection(self):
        import duckdb
        conn = duckdb.connect(self.database_path)
        if self.enable_spatial:
            conn.execute("INSTALL spatial; LOAD spatial;")
        return conn

    def execute(self, query: str, params: list | None = None):
        with self.get_connection() as conn:
            if params:
                return conn.execute(query, params).fetchall()
            return conn.execute(query).fetchall()

    def init_schemas(self):
        """Initialize all database schemas."""
        with self.get_connection() as conn:
            conn.execute("CREATE SCHEMA IF NOT EXISTS education;")
            conn.execute("CREATE SCHEMA IF NOT EXISTS statistics;")
            conn.execute("CREATE SCHEMA IF NOT EXISTS celtic;")
            conn.execute("CREATE SCHEMA IF NOT EXISTS geospatial;")
            conn.execute("CREATE SCHEMA IF NOT EXISTS training;")


class LanceDBResource(ConfigurableResource):
    """Unified LanceDB resource with namespaced tables.

    Table namespacing:
    - cianfhoghlaim.<jurisdiction>.<stage>.<subject_slug>.<level>_<lang>_chunks
      (BIEP v3 canonical pattern per the
      2026-08-13-biep-v3-systematic-download-ireland-england-v1 change)
    - oideachas.*: legacy Irish curriculum embeddings (pre-v7)
    - oileain.*: legacy British Isles curriculum and policy (pre-v7)
    - teanga.*: Celtic language and folklore

    The canonical embedder is `BAAI/bge-m3` (1024-d, multilingual)
    per the BIEP v3 hardening change. The legacy
    `paraphrase-multilingual-MiniLM-L12-v2` (384-d) embedder is
    preserved as a fallback for backwards compatibility with existing
    pre-v3 tables (call `get_db_legacy()` to use it).
    """

    database_path: str = str(LANCEDB_PATH)
    # BIEP v3 canonical embedder (1024-d, multilingual). Per the
    # 2026-08-07-biep-v3-hardening-v1 change, the legacy 384-d MiniLM
    # embedder is retired in favour of BGE-M3.
    embedding_model: str = "BAAI/bge-m3"
    embedding_dim: int = 1024
    # Legacy embedder (for backwards compat with pre-v3 tables).
    legacy_embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    legacy_embedding_dim: int = 384

    def get_db(self):
        """Return the canonical LanceDB connection (BIEP v3 path).

        Connects to the lakehouse Lance namespace sidecar at
        `rest://lakehouse-lance-namespace:8182` if the
        `LANCEDB_URI` env var is set; otherwise falls back to the
        local path at `LANCEDB_PATH`.
        """
        import lancedb
        lance_uri = os.environ.get("LANCEDB_URI")
        if lance_uri:
            return lancedb.connect(lance_uri)
        return lancedb.connect(self.database_path)

    def get_db_legacy(self):
        """Return the legacy local LanceDB connection (pre-v3 tables)."""
        import lancedb
        return lancedb.connect(self.database_path)

    def get_table(self, namespace: str, table_name: str):
        """Get a namespaced table (creates if not exists)."""
        db = self.get_db()
        full_name = f"{namespace}.{table_name}"
        return db.open_table(full_name) if full_name in db.table_names() else None


class IcebergCatalogResource(ConfigurableResource):
    """PyIceberg REST catalog resource for the BIEP v3 lakehouse.

    Wraps `pyiceberg.catalog.load_catalog("cianfhoghlaim", type="rest", uri=...)`
    at `http://lakehouse-lakekeeper:8181`. The catalog name is `cianfhoghlaim`
    per the iceberg-lakekeeper skill (renamed from the legacy `kcg` label on
    2026-08-27; the name is a client-side label only — the server-side catalog
    is selected by `uri` + `warehouse`, so no Lakekeeper migration is required).
    The catalog is backed by the lakehouse-postgres
    (`ducklake_oideachais` database) and the Garage S3 bucket
    `s3://iceberg/<warehouse>/`.

    Use `get_catalog()` to load the catalog and `get_table(namespace, table)`
    to load a specific Iceberg table.

    Re-gen: cd cianfhoghlaim && uv run baml-cli generate
    Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.
    """

    catalog_name: str = "cianfhoghlaim"
    catalog_uri: str = "http://lakehouse-lakekeeper:8181"
    warehouse: str = "s3://iceberg/"
    s3_endpoint: str = "http://localhost:3900"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""

    def get_catalog(self):
        """Load the PyIceberg REST catalog."""
        from pyiceberg.catalog import load_catalog

        return load_catalog(
            self.catalog_name,
            type="rest",
            uri=self.catalog_uri,
            **{
                "s3.endpoint": self.s3_endpoint,
                "s3.access-key-id": self.s3_access_key_id
                or os.environ.get("GARAGE_ACCESS_KEY_ID", ""),
                "s3.secret-access-key": self.s3_secret_access_key
                or os.environ.get("GARAGE_SECRET_ACCESS_KEY", ""),
                "s3.region": "garage",
                "s3.path-style-access": "true",
            },
        )

    def get_table(self, namespace: str, table_name: str):
        """Load an Iceberg table by namespace + table name."""
        catalog = self.get_catalog()
        return catalog.load_table(f"{namespace}.{table_name}")


class LanceNamespaceResource(ConfigurableResource):
    """Lance namespace resource for the BIEP v3 lakehouse.

    Wraps the `lance.namespace` SDK connection to the Lakekeeper-backed
    Lance namespace sidecar at `rest://lakehouse-lance-namespace:8182`.
    The sidecar exposes the Lakekeeper Iceberg REST catalog to Lance
    tables (per the `bonneagar/stacks/lakehouse/lance-sidecar` stack).

    The canonical namespace is `cianhoghlaim`, with sub-namespaces
    per jurisdiction (e.g. `cianhoghlaim.ireland.leaving_cycle.mathematics`).

    Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.
    """

    namespace_uri: str = "rest://lakehouse-lance-namespace:8182"
    canonical_namespace: str = "cianhoghlaim"
    s3_endpoint: str = "http://localhost:3900"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""

    def get_namespace(self):
        """Connect to the Lance namespace via the official SDK."""
        try:
            import lance.namespace

            return lance.namespace.connect(
                "rest",
                URI=self.namespace_uri,
                S3_ENDPOINT=self.s3_endpoint,
                S3_ACCESS_KEY_ID=self.s3_access_key_id
                or os.environ.get("GARAGE_ACCESS_KEY_ID", ""),
                S3_SECRET_ACCESS_KEY=self.s3_secret_access_key
                or os.environ.get("GARAGE_SECRET_ACCESS_KEY", ""),
            )
        except ImportError:
            # Fallback: use the official SDK form per the lancedb skill
            # (lancedb.connect("rest://..."))
            import lancedb

            return lancedb.connect(self.namespace_uri)

    def create_namespace(self, namespace: str) -> None:
        """Create a Lance namespace (idempotent)."""
        ns = self.get_namespace()
        try:
            ns.create_namespace(namespace)
        except Exception:
            # Already exists — idempotent semantics.
            pass

    def list_namespaces(self) -> list[str]:
        """List all Lance namespaces under the canonical namespace."""
        ns = self.get_namespace()
        return list(ns.list_namespaces())


class GeoParquetResource(ConfigurableResource):
    """GeoParquet storage for spatial data."""

    output_path: str = str(GEOPARQUET_PATH)

    def write(self, table_name: str, gdf):
        """Write GeoDataFrame to GeoParquet."""
        path = Path(self.output_path) / f"{table_name}.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        gdf.to_parquet(path)
        return path


# ============================================================================
# Graph Database Resources
# ============================================================================


class MemgraphResource(ConfigurableResource):
    """Memgraph knowledge graph for curriculum relationships.

    .. deprecated::
        Memgraph is no longer in the Wave 1+2 stack lineup. The
        `agent-observability` spec explicitly removed Memgraph in
        favour of FalkorDB (graph) + lakehouse-postgres (relational).
        The instance is kept for backwards compatibility but should
        not be used in new assets. Use ``FalkorDBResource`` instead.
    """

    uri: str = "bolt://localhost:7687"
    username: str = ""
    password: str = ""

    def get_client(self):
        import warnings
        warnings.warn(
            "MemgraphResource is deprecated; use FalkorDBResource instead. "
            "Returning None — assets that depend on this resource will fail at runtime.",
            DeprecationWarning,
            stacklevel=2,
        )
        return None


class Neo4jResource(ConfigurableResource):
    """Neo4j graph database for linguistic knowledge graphs.

    .. deprecated::
        Neo4j is not in the Wave 1+2 stack lineup. The
        `agent-observability` spec removed Neo4j in favour of
        FalkorDB + lakehouse-postgres. Use ``FalkorDBResource``
        instead.
    """

    uri: str = "bolt://localhost:7687"
    user: str = "neo4j"
    password: str = ""

    def get_driver(self):
        import warnings
        warnings.warn(
            "Neo4jResource is deprecated; use FalkorDBResource instead. "
            "Returning None — assets that depend on this resource will fail at runtime.",
            DeprecationWarning,
            stacklevel=2,
        )
        return None


class FalkorDBResource(ConfigurableResource):
    """FalkorDB for high-performance graph caching.

    The FalkorDB stack is exposed on host port 6380 (port-shifted
    from 6379 to avoid a conflict with dragonfly on the same host).
    Inside docker, the container name ``falkordb`` resolves to the
    container's internal port 6379. The defaults below use env
    vars so the same code works inside-docker AND on-host.

    Env-var precedence (highest to lowest):
      1. ``CIANFHOGHLAIM_FALKORDB_URL`` — full redis:// URL (preferred)
      2. Legacy ``FALKORDB_HOST`` + ``FALKORDB_PORT`` + ``FALKORDB_PASSWORD``
      3. In-docker default ``falkordb:6379``
    """

    # Env-driven defaults.
    host: str = ""
    port: int = 0
    password: str = ""

    def get_client(self):
        from ..graph.falkordb_client import FalkorDBClient
        return FalkorDBClient(
            host=self.host or os.getenv("FALKORDB_HOST") or _CIANFHOGHLAIM_FALKORDB_HOST,
            port=self.port
            or int(os.getenv("FALKORDB_PORT", "0") or "0")
            or _CIANFHOGHLAIM_FALKORDB_PORT,
            password=self.password
            or os.getenv("FALKORDB_PASSWORD")
            or _CIANFHOGHLAIM_FALKORDB_PASSWORD,
        )


class TemporalGraphResource(ConfigurableResource):
    """Temporal knowledge graph for bi-temporal curriculum tracking.

    .. deprecated::
        The temporal graph stack is not in the Wave 1+2 lineup.
        Use ``FalkorDBResource`` + lakehouse-postgres instead. This
        resource is kept for backwards compatibility only.
    """

    uri: str = "bolt://localhost:7687"
    username: str = ""
    password: str = ""

    def get_client(self):
        from ..graph.temporal_client import TemporalGraphClient
        return TemporalGraphClient(
            uri=self.uri,
            username=self.username if self.username else None,
            password=self.password if self.password else None,
        )


# ============================================================================
# Memory & AI Resources
# ============================================================================


class CogneeMemoryResource(ConfigurableResource):
    """Cognee AI memory service for education knowledge.

    The deployed cognee stack uses ``USE_UNIFIED_PROVIDER=pghybrid``
    (postgres + pgvector in the same database, no separate graph DB).
    The previous default of ``bolt://localhost:7687`` (Memgraph)
    was incorrect after the ``centralise-data-plane`` rewrite.

    For the *code-side* Cognee client, the canonical backend is
    FalkorDB (per the ``agent-observability`` spec which removed
    Memgraph + Neo4j from the production stack lineup) with Memgraph
    as the legacy fallback. Set ``CIANFHOGHLAIM_COGNEE_BACKEND``
    (``falkordb`` | ``memgraph`` | ``postgres``) to override.

    Set ``COGNEE_PG_HOST`` (default ``cognee-postgres`` inside docker,
    ``localhost`` on host) and ``COGNEE_PG_PASSWORD`` (default
    ``devpassword``).
    """

    # Postgres URL for the unified (pgvector) backend
    postgres_url: str = ""
    # LanceDB URL for the vector side (the lakehouse-lance-namespace
    # stack is the canonical vector store; this is the per-table layer
    # within the same data plane).
    vector_url: str = ""
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    # Code-side graph backend selection (falkordb|memgraph|postgres).
    # Reads from CIANFHOGHLAIM_COGNEE_BACKEND at construction time.
    backend: str = ""

    async def get_service(self):
        # Canonical post-v7 paths (the ..memory.* imports were broken pre-v7)
        try:
            from memory.cognee_config import CogneeConfig
            from memory.cognee_service import EducationMemoryService
        except ImportError:
            CogneeConfig = None
            EducationMemoryService = None

        # Resolve the code-side Cognee backend with the falkordb →
        # memgraph fallback chain (per dispatch hard-deliverable #2).
        backend = self.backend or _resolve_cognee_backend()

        config = CogneeConfig(
            backend=backend,
            postgres_url=self.postgres_url
            or os.getenv(
                "COGNEE_PG_URL",
                f"postgresql://cognee:{os.getenv('COGNEE_POSTGRES_PASSWORD', 'devpassword')}"
                f"@{os.getenv('COGNEE_PG_HOST', 'cognee-postgres')}:5432/cognee_oideachais",
            ),
            vector_url=self.vector_url
            or os.getenv("LANCEDB_URI")
            or _CIANFHOGHLAIM_LANCEDB_URL,
            embedding_model=self.embedding_model,
        )
        service = EducationMemoryService(config)
        await service.initialize()
        return service


class DuckLakeResource(ConfigurableResource):
    """DuckLake ACID lakehouse for training datasets.

    Per the 2026-08-08-lakehouse-extensive-hydration-v1 change +
    Wave 4 §4.9 of the 2026-08-24 master refactor plan: the canonical
    DuckLake implementation is now
    `dlt_sources.destinations.ducklake` — the only module using dlt's
    first-party `DuckLakeCredentials` config object (vs. hand-rolled
    `ATTACH` SQL strings) + the Wave 4 v1.0 best practices
    (`data_inlining`, `sort expressions`, change feed, encryption,
    snapshot expiry, Iceberg REST interop).
    """

    storage_path: str = str(DUCKLAKE_PATH)
    namespace: str = "ducklake_cianfhoghlaim"

    def get_dlt_destination(
        self,
        *,
        use_ducklake: bool | None = None,
        metadata_schema: str | None = None,
    ):
        """Return a dlt destination for this resource's namespace.

        Use this from any Dagster asset that wants to write via a dlt
        pipeline: ``dlt.pipeline(destination=resource.get_dlt_destination())``.

        Args:
            use_ducklake: Legacy parameter (preserved for back-compat).
                When ``True``, the DuckLake destination is returned;
                when ``False``, the MotherDuck destination is returned.
            metadata_schema: Optional per-quadrant Postgres metadata
                schema name (per the Wave 1 §7.1 layer-grouped
                destinations). Default: ``None`` → the consolidated
                ``DUCKLAKE_NAMESPACE`` schema.

        Returns:
            The dlt-destination for the resource's namespace.
        """
        from dlt_sources.destinations.ducklake import get_ducklake_destination
        from dlt_sources.destinations.motherduck import (
            get_motherduck_destination,
        )

        # The legacy `use_ducklake=False` path falls back to MotherDuck
        # for callers that need the SaaS-managed DuckLake.
        if use_ducklake is False:
            return get_motherduck_destination()
        return get_ducklake_destination(
            metadata_schema=metadata_schema,
        )

    def get_namespace(self) -> str:
        """Return the canonical Wave 4 §4.1 namespace name.

        Convenience accessor for code that wants the
        ``ducklake_cianfhoghlaim`` literal without re-implementing the
        consolidation logic. Delegates to
        ``dlt_sources.destinations.ducklake.get_ducklake_namespace()``.
        """
        from dlt_sources.destinations.ducklake import get_ducklake_namespace

        return get_ducklake_namespace()

    def get_client(self):
        """Return a raw DuckDB connection attached to the DuckLake catalog.

        Use this for direct SQL queries (asset checks, verification
        scripts) rather than dlt pipeline writes.
        """
        import os

        import duckdb

        con = duckdb.connect(":memory:")
        con.execute("INSTALL ducklake; LOAD ducklake;")
        con.execute("INSTALL httpfs; LOAD httpfs;")

        aws_key = os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get(
            "GARAGE_ACCESS_KEY_ID", ""
        )
        aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY") or os.environ.get(
            "GARAGE_SECRET_ACCESS_KEY", ""
        )
        endpoint = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:3900").replace(
            "http://", ""
        )
        if aws_key and aws_secret:
            con.execute(
                f"CREATE SECRET ducklake_s3 (TYPE S3, PROVIDER config, "
                f"KEY_ID '{aws_key}', SECRET '{aws_secret}', REGION 'garage', "
                f"ENDPOINT '{endpoint}', USE_SSL false, URL_STYLE 'path')"
            )

        pg_host = os.environ.get("DUCKLAKE_POSTGRES_HOST", "localhost")
        pg_port = os.environ.get("DUCKLAKE_POSTGRES_PORT", "5433")
        pg_db = os.environ.get("DUCKLAKE_POSTGRES_DB") or os.environ.get(
            "POSTGRES_DB", f"ducklake_{self.namespace}"
        )
        pg_user = os.environ.get("DUCKLAKE_POSTGRES_USER") or os.environ.get(
            "POSTGRES_USER", "lakekeeper"
        )
        pg_pass = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD") or os.environ.get(
            "POSTGRES_PASSWORD", "devpassword"
        )
        # Default must match `dlt_sources/common/destinations_cianfhoghlaim.py`
        # and `mise.toml` — the live-verified bucket is `ducklake`. Attaching
        # with a DATA_PATH the catalog doesn't know fails outright.
        bucket = os.environ.get("DUCKLAKE_BUCKET", "ducklake")
        con.execute(
            f"ATTACH 'ducklake:postgres:dbname={pg_db} host={pg_host} "
            f"port={pg_port} user={pg_user} password={pg_pass}' "
            f"AS {self.namespace} "
            f"(DATA_PATH 's3://{bucket}/{self.namespace}/')"
        )
        con.execute(f"USE {self.namespace};")
        return con


# ============================================================================
# Crawler Resources
# ============================================================================


class FirecrawlResource(ConfigurableResource):
    """Firecrawl for web scraping curriculum sites."""

    api_key: str = ""  # Set via FIRECRAWL_API_KEY env var or config

    def get_client(self):
        import os
        key = self.api_key or os.getenv("FIRECRAWL_API_KEY", "")
        if not key:
            raise ValueError("FIRECRAWL_API_KEY not configured")
        from firecrawl import FirecrawlApp
        return FirecrawlApp(api_key=key)


class BrowserbaseResource(ConfigurableResource):
    """Browserbase for JavaScript-heavy sites."""

    api_key: str = ""  # Set via BROWSERBASE_API_KEY env var or config
    project_id: str = ""  # Set via BROWSERBASE_PROJECT_ID env var or config

    def get_session(self):
        import os
        key = self.api_key or os.getenv("BROWSERBASE_API_KEY", "")
        proj = self.project_id or os.getenv("BROWSERBASE_PROJECT_ID", "")
        if not key or not proj:
            raise ValueError("BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID not configured")
        from browser import BrowserConfig
        from browser.backends.paid.browserbase import BrowserbaseBackend

        config = BrowserConfig(
            browserbase_api_key=key,
            browserbase_project_id=proj,
        )
        return BrowserbaseBackend(config=config)


class AgenticCrawlerResource(ConfigurableResource):
    """Agentic crawler combining Firecrawl + Browserbase + LLM navigation."""

    firecrawl_api_key: str = ""  # Set via env var or config
    browserbase_api_key: str = ""  # Set via env var or config
    browserbase_project_id: str = ""  # Set via env var or config

    def get_crawler(self, mode: str = "hybrid"):
        import os
        fc_key = self.firecrawl_api_key or os.getenv("FIRECRAWL_API_KEY", "")
        bb_key = self.browserbase_api_key or os.getenv("BROWSERBASE_API_KEY", "")
        bb_proj = self.browserbase_project_id or os.getenv("BROWSERBASE_PROJECT_ID", "")
        if not fc_key or not bb_key or not bb_proj:
            raise ValueError("Crawler API keys not fully configured")
        from dlt_sources.education.ireland.british_isles.education.agentic_discovery import AgenticCrawler
        return AgenticCrawler(
            firecrawl_api_key=fc_key,
            browserbase_api_key=bb_key,
            browserbase_project_id=bb_proj,
            mode=mode,
        )


# ============================================================================
# OCR & Training Resources (from teanga)
# ============================================================================


class OCRModelRegistry(ConfigurableResource):
    """Registry for OCR models with Celtic language support."""

    cache_dir: str = "~/.cache/ocr_models"

    def get_registry(self):
        # v4: import from the v4 home `cianfhoghlaim.ocr.models`
        from ocr.models import ModelRegistry as _V4ModelRegistry
        return _V4ModelRegistry(custom_models=None)


class GaelicMetricsResource(ConfigurableResource):
    """Metrics for evaluating Gaelic OCR quality."""

    def get_evaluator(self):
        # Canonical post-v7 path (the ..ocr.* import was broken pre-v7)
        try:
            from meaisinfhoghlaim.models.registry import (
                CLASSICAL_OCR as _CLASSICAL_OCR_REGISTRY,
            )
            GaelicMetrics = _CLASSICAL_OCR_REGISTRY  # type: ignore
        except ImportError:
            GaelicMetrics = None
        return GaelicMetrics()


class UnslothTrainingResource(ConfigurableResource):
    """Unsloth configuration for efficient model fine-tuning."""

    model_name: str = "unsloth/Qwen2.5-7B-Instruct"
    max_seq_length: int = 4096
    lora_r: int = 32

    def get_config(self):
        # Canonical post-v7 path (the ..training.* import was broken pre-v7)
        try:
            from meaisinfhoghlaim.training.training.unsloth_config import UnslothConfig
        except ImportError:
            UnslothConfig = None
        return UnslothConfig(
            model_name=self.model_name,
            max_seq_length=self.max_seq_length,
            lora_r=self.lora_r,
        )


# ============================================================================
# Generation Resources
# ============================================================================


class BAMLGenerationResource(ConfigurableResource):
    """BAML type-safe LLM extraction."""

    cache_dir: str = "~/.cache/baml_schemas"

    def get_pipeline(self):
        # Canonical post-v7 path (the ..agents.* import was broken pre-v7)
        try:
            from agents.baml_integration import EnhancedBAMLExtractionPipeline
        except ImportError:
            EnhancedBAMLExtractionPipeline = None
        return EnhancedBAMLExtractionPipeline()


class ImageGenerationResource(ConfigurableResource):
    """Image generation for educational content."""

    provider: str = "replicate"
    model: str = "stability-ai/sdxl"

    def get_generator(self):
        try:
            from agents.image_generation import ImageGenerator
        except ImportError:
            ImageGenerator = None
        return ImageGenerator(provider=self.provider, model=self.model)


class TranslationResource(ConfigurableResource):
    """Translation between Celtic languages.

    Models:
    - NLLB-200: Best for en↔ga, en↔cy, en↔gd
    - Opus-MT: Helsinki-NLP models for Celtic pairs
    - M2M-100: Fallback for less common pairs (gv, kw, br)
    """

    primary_model: str = "facebook/nllb-200-distilled-600M"
    fallback_model: str = "facebook/m2m100_418M"

    def get_translator(self):
        try:
            from agents.translation import CelticTranslator
        except ImportError:
            CelticTranslator = None
        return CelticTranslator(
            primary_model=self.primary_model,
            fallback_model=self.fallback_model,
        )


class TerminologyResource(ConfigurableResource):
    """Irish educational terminology from Téarma.ie."""

    cache_path: str = str(OUTPUT_PATH / "terminology_cache.json")

    def get_lookup(self):
        try:
            from agents.terminology import TerminologyLookup
        except ImportError:
            TerminologyLookup = None
        return TerminologyLookup(cache_path=self.cache_path)


# ============================================================================
# Progress Tracking
# ============================================================================


class ProgressTrackerResource(ConfigurableResource):
    """Track pipeline progress for UI display.

    Defaults use the env var ``REDIS_URL`` (set by
    ``bonneagar/stacks/dagster/.env.dev`` to
    ``redis://lakehouse-redis:6379`` in docker or
    ``redis://localhost:6390`` on host) so the same code works in
    both environments. Falls back to the local default for legacy
    callers.
    """

    redis_url: str = ""

    def get_tracker(self):
        try:
            from observability.progress_tracker import ProgressTracker
        except ImportError:
            ProgressTracker = None
        return ProgressTracker(
            redis_url=self.redis_url
            or os.getenv("REDIS_URL", "redis://lakehouse-redis:6379")
        )


# ============================================================================
# LLM Gateway Resource (LiteLLM)
# ============================================================================


class LiteLLMResource(ConfigurableResource):
    """OpenAI-compatible client wrapping the canonical LiteLLM gateway.

    The gateway lives at bonneagar/stacks/litellm and exposes
    a unified API for: local GGUF (llama-swap), local MLX (mlx-omni), local
    image gen (InvokeAI), plus all cloud providers (Gemini, GLM, OpenAI,
    Anthropic, OpenCode Go).

    All Dagster assets and BAML extractions should call through this
    resource rather than hitting any provider directly. That way:
      - Failover chains are honoured automatically.
      - Langfuse traces the full lineage per request.
      - Rate limits and spend caps are enforced uniformly.
      - New providers are added in one place (the gateway config.yaml).

    Defaults use the env var ``CIANFHOGHLAIM_LITELLM_URL`` (set by
    ``bonneagar/stacks/dagster/.env.dev``) so the same resource works
    both in-docker (``http://litellm:4000/v1``) and on-host
    (``http://127.0.0.1:4000/v1``). The legacy ``LITELLM_BASE_URL``
    env var is honoured as a backwards-compat alias.
    """

    base_url: str = ""
    master_key: str = ""
    default_model: str = "extract"  # alias from the gateway config
    timeout_s: float = 600.0

    def get_client(self) -> "OpenAI":
        """Return an OpenAI client targeting the LiteLLM gateway."""
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "openai package not installed. Run: uv pip install openai"
            ) from exc

        return OpenAI(
            base_url=self.base_url
            or os.getenv("LITELLM_BASE_URL")
            or _CIANFHOGHLAIM_LITELLM_URL,
            api_key=self.master_key or os.getenv("LITELLM_MASTER_KEY", "sk-1234"),
            timeout=self.timeout_s,
        )

    def completion(
        self,
        messages: list[dict],
        model: str | None = None,
        **kwargs,
    ):
        """OpenAI-compatible chat completion routed through the gateway."""
        client = self.get_client()
        return client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            **kwargs,
        )


# ============================================================================
# Resource Instances
# ============================================================================

duckdb_resource = DuckDBResource()
lancedb_resource = LanceDBResource()
geoparquet_resource = GeoParquetResource()

memgraph_resource = MemgraphResource()
neo4j_resource = Neo4jResource()
falkordb_resource = FalkorDBResource()
temporal_graph_resource = TemporalGraphResource()

cognee_memory_resource = CogneeMemoryResource()
ducklake_resource = DuckLakeResource()

firecrawl_resource = FirecrawlResource()
browserbase_resource = BrowserbaseResource()
agentic_crawler_resource = AgenticCrawlerResource()

ocr_registry_resource = OCRModelRegistry()
gaelic_metrics_resource = GaelicMetricsResource()
unsloth_training_resource = UnslothTrainingResource()

baml_generation_resource = BAMLGenerationResource()
image_generation_resource = ImageGenerationResource()
translation_resource = TranslationResource()
terminology_resource = TerminologyResource()

progress_tracker_resource = ProgressTrackerResource()
litellm_resource = LiteLLMResource()


# ============================================================================
# British Isles State Resource (Wave 2)
# ============================================================================
#
# The canonical Cianfhoghlaim state-backed ConfigurableResource for the 5 high-churn
# British Isles sources (NCCA + SEC + CCEA + SQA + WJEC). Per the
# canonical `dagster-pipeline-components` spec, every per-pipeline
# Component with downstream BIEP consumers uses the `StateBackedComponent`
# pattern (Dagster 1.13+ state-backed components). The 5 high-churn
# sources default to `LOCAL_FILESYSTEM` state (per master plan §3.3) —
# this resource is the canonical Cianfhoghlaim entry point for that state
# backend.
#
# Sister repos (ciancheiltis + cianchosaint + ciandlíthe + cianchosaint)
# can import this resource directly:
#
#   from cianfhoghlaim.orchestration.resources import british_isles_state_resource
#
# (per the `cianfhoghlaim>=1.0,<2.0` workspace pin documented in the
# 2026-08-25-master-refactor-v1 proposal §"Sister-repo export surface").


class BritishIslesStateResource(ConfigurableResource):
    """The canonical Cianfhoghlaim state-backed resource for the 5 high-churn British Isles sources.

    Per master plan §3.3, the 5 high-churn sources (NCCA + SEC + CCEA +
    SQA + WJEC) default to `LOCAL_FILESYSTEM` state. The state files are
    written to `.local_defs_state/` at the repo root (per
    `orchestration.pipelines._shared.state_helpers.local_defs_state_root()`).

    The resource is the canonical `ConfigurableResource` representation
    of the state backend — it's injected into every per-pipeline
    Component's `build_defs_from_state()` method via the canonical
    `context.resources.british_isles_state` lookup.

    Args:
        root: The on-disk root for the `LOCAL_FILESYSTEM` state files.
            Defaults to `~/.local_defs_state/` (the canonical Cianfhoghlaim
            convention; the actual default at runtime is the repo root's
            `.local_defs_state/` directory).
        management_type: The state-management strategy. Defaults to
            `LOCAL_FILESYSTEM` (the canonical Cianfhoghlaim default for the 5
            high-churn sources).
    """

    root: str = ".local_defs_state"
    management_type: str = "LOCAL_FILESYSTEM"

    def state_path_for(self, source_module: str) -> str:
        """Compute the canonical `LOCAL_FILESYSTEM` state file path for
        a given `dlt_sources.<...>` module path.

        Args:
            source_module: The `dlt_sources.<...>` Python module path.

        Returns:
            The on-disk path where the state file lives (relative to
            `self.root`).
        """
        # The state file is named after the leaf component of the
        # module path (the canonical Cianfhoghlaim convention).
        leaf = source_module.rsplit(".", 1)[-1]
        for suffix in ("_source", "_pipeline"):
            if leaf.endswith(suffix):
                leaf = leaf[: -len(suffix)]
                break
        return f"{self.root}/{leaf}.json"


british_isles_state_resource = BritishIslesStateResource()


# ============================================================================
# All Resources Dictionary
# ============================================================================

all_resources = {
    # DLT
    "dlt": DagsterDltResource(),
    # Storage
    "duckdb": duckdb_resource,
    "lancedb": lancedb_resource,
    "geoparquet": geoparquet_resource,
    "ducklake": ducklake_resource,
    # Graph databases
    "memgraph": memgraph_resource,
    "neo4j": neo4j_resource,
    "falkordb": falkordb_resource,
    "temporal_graph": temporal_graph_resource,
    # Memory
    "cognee_memory": cognee_memory_resource,
    # Crawlers
    "firecrawl": firecrawl_resource,
    "browserbase": browserbase_resource,
    "agentic_crawler": agentic_crawler_resource,
    # OCR & Training
    "ocr_registry": ocr_registry_resource,
    "gaelic_metrics": gaelic_metrics_resource,
    "unsloth_training": unsloth_training_resource,
    # Generation
    "baml_gen": baml_generation_resource,
    "image_gen": image_generation_resource,
    "translation": translation_resource,
    "terminology": terminology_resource,
    # LLM Gateway (the canonical entry point for every model call)
    "litellm": litellm_resource,
    # Observability
    "progress_tracker": progress_tracker_resource,
    # Wave 2 — the canonical Cianfhoghlaim state-backed resource for the 5 British Isles
    # high-churn sources (NCCA + SEC + CCEA + SQA + WJEC). Per master plan §3.3.
    "british_isles_state": british_isles_state_resource,
}
