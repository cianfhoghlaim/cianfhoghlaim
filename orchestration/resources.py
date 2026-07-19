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
from cianfhoghlaim.observability.env_config import (
    FALKORDB_HOST as _CIANFHOGHLAIM_FALKORDB_HOST,
)
from cianfhoghlaim.observability.env_config import (
    FALKORDB_PASSWORD as _CIANFHOGHLAIM_FALKORDB_PASSWORD,
)
from cianfhoghlaim.observability.env_config import (
    FALKORDB_PORT as _CIANFHOGHLAIM_FALKORDB_PORT,
)
from cianfhoghlaim.observability.env_config import (
    LANCEDB_URL as _CIANFHOGHLAIM_LANCEDB_URL,
)
from cianfhoghlaim.observability.env_config import (
    LITELLM_URL as _CIANFHOGHLAIM_LITELLM_URL,
)
from cianfhoghlaim.observability.env_config import (
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
    - oideachas.*: Irish curriculum embeddings
    - oileain.*: British Isles curriculum and policy
    - teanga.*: Celtic language and folklore
    """

    database_path: str = str(LANCEDB_PATH)
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384

    def get_db(self):
        import lancedb
        return lancedb.connect(self.database_path)

    def get_table(self, namespace: str, table_name: str):
        """Get a namespaced table (creates if not exists)."""
        db = self.get_db()
        full_name = f"{namespace}.{table_name}"
        return db.open_table(full_name) if full_name in db.table_names() else None


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
        from ..graph.memgraph_client import MemgraphClient
        return MemgraphClient(
            uri=self.uri,
            username=self.username if self.username else None,
            password=self.password if self.password else None,
        )


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
        from neo4j import GraphDatabase
        return GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password) if self.password else None,
        )


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
        from ..memory.cognee_config import CogneeConfig
        from ..memory.cognee_service import EducationMemoryService

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
    """DuckLake ACID lakehouse for training datasets."""

    storage_path: str = str(DUCKLAKE_PATH)

    def get_client(self):
        from ..storage.ducklake_client import DuckLakeClient
        return DuckLakeClient(storage_path=self.storage_path)


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
        from dlt_sources.british_isles.ireland.education.agentic_discovery import AgenticCrawler
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
        from cianfhoghlaim.ocr.models import ModelRegistry as _V4ModelRegistry
        return _V4ModelRegistry(custom_models=None)


class GaelicMetricsResource(ConfigurableResource):
    """Metrics for evaluating Gaelic OCR quality."""

    def get_evaluator(self):
        from ..ocr.gaelic_metrics import GaelicMetrics
        return GaelicMetrics()


class UnslothTrainingResource(ConfigurableResource):
    """Unsloth configuration for efficient model fine-tuning."""

    model_name: str = "unsloth/Qwen2.5-7B-Instruct"
    max_seq_length: int = 4096
    lora_r: int = 32

    def get_config(self):
        from ..training.unsloth_config import UnslothConfig
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
        from ..agents.baml_integration import EnhancedBAMLExtractionPipeline
        return EnhancedBAMLExtractionPipeline()


class ImageGenerationResource(ConfigurableResource):
    """Image generation for educational content."""

    provider: str = "replicate"
    model: str = "stability-ai/sdxl"

    def get_generator(self):
        from ..agents.image_generation import ImageGenerator
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
        from ..agents.translation import CelticTranslator
        return CelticTranslator(
            primary_model=self.primary_model,
            fallback_model=self.fallback_model,
        )


class TerminologyResource(ConfigurableResource):
    """Irish educational terminology from Téarma.ie."""

    cache_path: str = str(OUTPUT_PATH / "terminology_cache.json")

    def get_lookup(self):
        from ..agents.terminology import TerminologyLookup
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
        from ..observability.progress_tracker import ProgressTracker
        return ProgressTracker(
            redis_url=self.redis_url
            or os.getenv("REDIS_URL", "redis://lakehouse-redis:6379")
        )


# ============================================================================
# LLM Gateway Resource (LiteLLM)
# ============================================================================


class LiteLLMResource(ConfigurableResource):
    """OpenAI-compatible client wrapping the canonical LiteLLM gateway.

    The gateway lives at infrastructure/stacks/litellm and exposes
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
}
