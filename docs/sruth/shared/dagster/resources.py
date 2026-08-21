"""Dagster resources for common integrations.

Provides resources for:
- LakeKeeper (Iceberg catalog management)
- Browser stack (for browser-based assets)
- DLT (for data loading)
"""

from __future__ import annotations

import os
from typing import Any

import dagster as dg

try:
    from pydantic import Field

    pydantic_available = True
except ImportError:
    # Fallback for older Dagster versions
    from dagster import Field

    pydantic_available = True


class LakeKeeperResource(dg.ConfigurableResource):
    """Resource for LakeKeeper Iceberg catalog management.

    LakeKeeper provides:
    - REST catalog API for Iceberg tables
    - Namespace and table registration
    - Metadata tracking
    - Integration with Garage/R2 for storage

    Example:
        @asset(resource_defs={"lakekeeper": lakekeeper_resource})
        def my_asset(lakekeeper: LakeKeeperResource):
            table = lakekeeper.register_table(
                namespace="curriculum",
                table_name="documents",
                schema={"id": "VARCHAR", "content": "TEXT"},
            )
            return table
    """

    catalog_uri: str = Field(
        default_factory=lambda: os.getenv("LAKEKEEPER_CATALOG_URI", "http://lakekeeper:8181"),
        description="LakeKeeper REST catalog API endpoint",
    )

    warehouse: str = Field(
        default_factory=lambda: os.getenv(
            "ICEBERG_WAREHOUSE",
            "s3://garage/warehouse",
        ),
        description="Iceberg warehouse location (S3-compatible)",
    )

    namespace: str = Field(
        default="default",
        description="Default namespace for table registration",
    )

    access_key: str = Field(
        default_factory=lambda: os.getenv("GARAGE_ACCESS_KEY", "garage_key"),
        description="S3 access key",
    )

    secret_key: str = Field(
        default_factory=lambda: os.getenv("GARAGE_SECRET_KEY", "garage_secret"),
        description="S3 secret key",
    )

    endpoint_url: str = Field(
        default_factory=lambda: os.getenv("GARAGE_ENDPOINT_URL", "http://garage:3900"),
        description="S3 endpoint URL",
    )

    @property
    def client(self) -> Any:
        """Get LakeKeeper client (lazy import)."""
        try:
            from lakekeeper_client import LakeKeeperClient
        except ImportError:
            # Use built-in HTTP client for REST API
            return self._http_client()

        return LakeKeeperClient(
            catalog_uri=self.catalog_uri,
            warehouse=self.warehouse,
        )

    def _http_client(self) -> Any:
        """Simple HTTP client for LakeKeeper REST API."""
        import requests

        class SimpleLakeKeeperClient:
            def __init__(self, catalog_uri: str, warehouse: str):
                self.catalog_uri = catalog_uri
                self.warehouse = warehouse

            def register_table(self, namespace: str, table_name: str, schema: dict):
                """Register a table in the catalog."""
                response = requests.post(
                    f"{self.catalog_uri}/v1/namespaces/{namespace}/tables",
                    json={
                        "name": table_name,
                        "schema": schema,
                        "location": f"{self.warehouse}/{namespace}/{table_name}",
                    },
                )
                response.raise_for_status()
                return response.json()

        return SimpleLakeKeeperClient(
            catalog_uri=self.catalog_uri,
            warehouse=self.warehouse,
        )

    def register_table(
        self,
        namespace: str,
        table_name: str,
        schema: dict[str, str],
        properties: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Register a table in the Iceberg catalog.

        Args:
            namespace: Namespace (e.g., "curriculum", "exam_materials")
            table_name: Table name
            schema: Column schema {col_name: col_type}
            properties: Table properties (format, partitioning, etc.)

        Returns:
            Table metadata
        """
        return self.client.register_table(namespace, table_name, schema)

    def register_embedding_table(
        self,
        namespace: str,
        table_name: str,
        dimension: int,
        metric: str = "cosine",
    ) -> dict[str, Any]:
        """Register a vector embedding table.

        Args:
            namespace: Namespace for the table
            table_name: Table name
            dimension: Vector dimension
            metric: Distance metric (cosine, euclidean, dot)

        Returns:
            Table metadata
        """
        schema = {
            "id": "VARCHAR",
            "vector": f"FLOAT[{dimension}]",
            "text": "VARCHAR",
            "metadata": "JSON",
        }

        properties = {
            "format": "lance",
            "vector_dimension": str(dimension),
            "vector_metric": metric,
        }

        return self.register_table(namespace, table_name, schema, properties)


# Resource factory function
def lakekeeper_resource(**kwargs) -> LakeKeeperResource:
    """Factory for LakeKeeper resource with default configuration.

    Usage:
        @asset(resource_defs={"lakekeeper": lakekeeper_resource()})
        def my_asset(lakekeeper: LakeKeeperResource):
            ...
    """
    return LakeKeeperResource(**kwargs)


class BrowserResource(dg.ConfigurableResource):
    """Resource for browser-based scraping within Dagster assets.

    Integrates with the sruth browser stack to provide:
    - Stagehand (AI-powered navigation)
    - Crawl4AI (bulk extraction)
    - Browserbase/Firecrawl (cloud fallback)

    Example:
        @asset(resource_defs={"browser": browser_resource()})
        def scrape_data(browser: BrowserResource):
            results = browser.scrape(
                url="https://example.com",
                instruction="Extract all article links",
            )
            return results
    """

    preferred_backend: str = "stagehand"
    """Preferred backend (stagehand, crawl4ai, browserbase)"""

    headless: bool = True
    """Run browser in headless mode"""

    timeout: float = 30.0
    """Navigation timeout in seconds"""

    async def scrape(
        self,
        url: str,
        instruction: str,
        formats: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Scrape a URL using the browser stack.

        Args:
            url: URL to scrape
            instruction: Extraction instruction
            formats: Desired output formats

        Returns:
            List of extracted items
        """
        from sruth.browser.sruth_browser.backends.initializer import ensure_initialized
        from sruth.browser.sruth_browser.backends.router import get_router
        from sruth.browser.sruth_browser.browser_types import BrowserOperation

        # Ensure backends are initialized
        await ensure_initialized()

        router = get_router()
        backend_type = await router.select_backend(BrowserOperation.EXTRACTION)

        if backend_type is None:
            raise RuntimeError("No browser backends available")

        backend = router.get_backend(backend_type)

        # Navigate and extract
        await backend.navigate(url)
        result = await backend.extract(
            instruction=instruction,
            format=formats or ["structured"],
        )

        if result.success and result.data:
            if isinstance(result.data, list):
                return result.data
            elif isinstance(result.data, dict):
                for key in ["items", "results", "data"]:
                    if key in result.data and isinstance(result.data[key], list):
                        return result.data[key]
            return [result.data]

        return []

    async def screenshot(
        self,
        url: str,
        full_page: bool = False,
    ) -> bytes | None:
        """Capture a screenshot of a URL.

        Args:
            url: URL to screenshot
            full_page: Capture full page scroll

        Returns:
            Screenshot image bytes
        """
        from sruth.browser.sruth_browser.backends.initializer import ensure_initialized
        from sruth.browser.sruth_browser.backends.router import get_router
        from sruth.browser.sruth_browser.browser_types import BrowserOperation

        await ensure_initialized()

        router = get_router()
        backend_type = await router.select_backend(BrowserOperation.SCREENSHOT)

        if backend_type is None:
            raise RuntimeError("No browser backends available")

        backend = router.get_backend(backend_type)
        result = await backend.screenshot(url=url, full_page=full_page)

        if result.success and result.image_data:
            import base64

            return base64.b64decode(result.image_data)

        return None


# Resource factory function
def browser_resource(**kwargs) -> BrowserResource:
    """Factory for Browser resource with default configuration."""
    return BrowserResource(**kwargs)


# ============================================================================
# MotherDuck Resource
# ============================================================================


class MotherDuckResource(dg.ConfigurableResource):
    """Resource for MotherDuck cloud data warehouse.

    MotherDuck provides:
    - Serverless DuckDB in the cloud
    - Hybrid OLTP/OLAP with PlanetScale via pg_duckdb extension
    - Fast analytical queries on large datasets
    - Integration with PlanetScale for transactional workloads

    Example:
        @asset(resource_defs={"motherduck": motherduck_resource()})
        def query_data(motherduck: MotherDuckResource):
            df = motherduck.query("SELECT * FROM curriculum.documents")
            return df
    """

    token: str = Field(
        default_factory=lambda: os.getenv("MOTHERDUCK_TOKEN"),
        description="MotherDuck service token",
    )

    database: str = Field(
        default="sruth",
        description="MotherDuck database name",
    )

    schemas: list[str] = Field(
        default_factory=lambda: ["curriculum", "exam_materials", "embeddings"],
        description="Schemas to create/use",
    )

    # PlanetScale integration for hybrid OLTP/OLAP
    planetscale_host: str | None = Field(
        default_factory=lambda: os.getenv("PLANETSCALE_HOST"),
        description="PlanetScale host for pg_duckdb integration",
    )

    planetscale_database: str | None = Field(
        default_factory=lambda: os.getenv("PLANETSCALE_DATABASE"),
        description="PlanetScale database name",
    )

    planetscale_user: str | None = Field(
        default_factory=lambda: os.getenv("PLANETSCALE_USER"),
        description="PlanetScale username",
    )

    planetscale_password: str | None = Field(
        default_factory=lambda: os.getenv("PLANETSCALE_PASSWORD"),
        description="PlanetScale password",
    )

    @property
    def conn_str(self) -> str:
        """Get MotherDuck connection string."""
        return f"md:?motherduck_token={self.token}&database={self.database}"

    def get_connection(self) -> Any:
        """Get MotherDuck connection.

        Returns:
            DuckDB connection object
        """
        import duckdb

        conn = duckdb.connect(self.conn_str)

        # Attach PlanetScale if configured for hybrid OLTP/OLAP
        if self.planetscale_host and self.planetscale_database:
            self._attach_planetscale(conn)

        return conn

    def _attach_planetscale(self, conn: Any) -> None:
        """Attach PlanetScale PostgreSQL as a foreign database.

        This enables hybrid OLTP/OLAP via the pg_duckdb extension.
        Transactional data lives in PlanetScale, analytics in MotherDuck.
        """
        try:
            # Build PostgreSQL connection string
            pg_conn_str = (
                f"postgresql://{self.planetscale_user}:{self.planetscale_password}"
                f"@{self.planetscale_host}/{self.planetscale_database}"
            )

            # Attach PlanetScale as 'pscale' schema
            conn.execute(f"""
                ATTACH '{pg_conn_str}' AS pscale (TYPE postgres);
            """)
        except Exception as e:
            # Log warning but don't fail - PlanetScale is optional
            import warnings

            warnings.warn(f"Failed to attach PlanetScale: {e}")

    def query(self, sql: str, params: dict[str, Any] | None = None) -> Any:
        """Execute a SQL query.

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            Query result (typically a relation or dataframe)
        """
        conn = self.get_connection()
        try:
            if params:
                return conn.execute(sql, params)
            return conn.execute(sql)
        finally:
            conn.close()

    def create_schema(self, schema: str) -> None:
        """Create a schema if it doesn't exist.

        Args:
            schema: Schema name
        """
        self.query(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    def init_schemas(self) -> None:
        """Initialize all configured schemas."""
        for schema in self.schemas:
            self.create_schema(schema)

    def table_exists(self, schema: str, table: str) -> bool:
        """Check if a table exists.

        Args:
            schema: Schema name
            table: Table name

        Returns:
            True if table exists
        """
        result = self.query(f"""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = '{schema}' AND table_name = '{table}'
        """).fetchone()
        return result[0] > 0 if result else False

    def export_to_parquet(
        self,
        schema: str,
        table: str,
        path: str,
    ) -> None:
        """Export table to Parquet file.

        Args:
            schema: Source schema
            table: Source table
            path: Destination path (S3 or local)
        """
        self.query(f"""
            COPY {schema}.{table} TO '{path}' (FORMAT PARQUET);
        """)

    def import_from_parquet(
        self,
        schema: str,
        table: str,
        path: str,
    ) -> None:
        """Import Parquet file into table.

        Args:
            schema: Target schema
            table: Target table
            path: Source path (S3 or local)
        """
        self.query(f"""
            CREATE OR REPLACE TABLE {schema}.{table} AS
            SELECT * FROM read_parquet('{path}');
        """)

    def sync_from_planetscale(
        self,
        pg_table: str,
        md_schema: str,
        md_table: str,
    ) -> None:
        """Sync data from PlanetScale to MotherDuck.

        Args:
            pg_table: PlanetScale table name (from pscale schema)
            md_schema: MotherDuck target schema
            md_table: MotherDuck target table
        """
        self.query(f"""
            CREATE OR REPLACE TABLE {md_schema}.{md_table} AS
            SELECT * FROM pscale.{pg_table};
        """)


# Resource factory function
def motherduck_resource(**kwargs) -> MotherDuckResource:
    """Factory for MotherDuck resource with default configuration.

    Usage:
        @asset(resource_defs={"motherduck": motherduck_resource()})
        def my_asset(motherduck: MotherDuckResource):
            result = motherduck.query("SELECT * FROM my_table")
            ...
    """
    return MotherDuckResource(**kwargs)


# ============================================================================
# FalkorDB Resource
# ============================================================================


class FalkorDBResource(dg.ConfigurableResource):
    """Resource for FalkorDB graph database.

    FalkorDB is a Redis-based graph database that provides:
    - Fast graph traversals
    - Cypher query language support
    - Integration with Graphiti for temporal graphs
    - Caching layer for AI agent memory

    Example:
        @asset(resource_defs={"falkordb": falkordb_resource()})
        def graph_asset(falkordb: FalkorDBResource):
            result = falkordb.query(
                "MATCH (n:Curriculum)-[r]-(m) RETURN n, r, m"
            )
            return result
    """

    uri: str = Field(
        default_factory=lambda: os.getenv("FALKORDB_URI", "redis://localhost:6379"),
        description="FalkorDB connection URI",
    )

    username: str | None = Field(
        default_factory=lambda: os.getenv("FALKORDB_USER"),
        description="FalkorDB username",
    )

    password: str | None = Field(
        default_factory=lambda: os.getenv("FALKORDB_PASSWORD"),
        description="FalkorDB password",
    )

    graph_name: str = Field(
        default="graphiti_graph",
        description="Default graph name",
    )

    @property
    def client(self) -> Any:
        """Get FalkorDB client."""
        try:
            from redis import Redis
            from redis.graph import Graph
        except ImportError:
            raise ImportError("Redis with graph support required. Install: pip install redis")

        client = Redis.from_url(
            self.uri,
            username=self.username,
            password=self.password,
            decode_responses=True,
        )
        return client

    def query(self, cypher: str, graph_name: str | None = None) -> list[dict]:
        """Execute Cypher query on FalkorDB.

        Args:
            cypher: Cypher query string
            graph_name: Graph name (default from config)

        Returns:
            Query results
        """
        from redis.graph import Graph

        graph = Graph(
            graph_name or self.graph_name,
            self.client,
        )

        result = graph.query(cypher)
        return result.result_set

    def add_node(
        self,
        label: str,
        properties: dict[str, Any],
    ) -> str:
        """Add a node to the graph.

        Args:
            label: Node label
            properties: Node properties

        Returns:
            Node ID
        """
        props_str = ", ".join([f"{k}: {repr(v)}" for k, v in properties.items()])
        cypher = f"CREATE (n:{label} {{{props_str}}}) RETURN n"
        result = self.query(cypher)
        return str(result) if result else ""

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: dict[str, Any] | None = None,
    ) -> str:
        """Add an edge to the graph.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            relation_type: Edge label
            properties: Edge properties

        Returns:
            Edge ID
        """
        props_str = ""
        if properties:
            props_str = " {" + ", ".join([f"{k}: {repr(v)}" for k, v in properties.items()]) + "}"

        cypher = f"""
        MATCH (source), (target)
        WHERE id(source) = '{source_id}' AND id(target) = '{target_id}'
        CREATE (source)-[r:{relation_type}{props_str}]->(target)
        RETURN r
        """
        result = self.query(cypher)
        return str(result) if result else ""

    def get_neighbors(
        self,
        node_id: str,
        direction: str = "both",
        relation_type: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Get neighboring nodes.

        Args:
            node_id: Center node ID
            direction: "in", "out", or "both"
            relation_type: Filter by relation type
            limit: Result limit

        Returns:
            List of neighboring nodes and edges
        """
        dir_map = {
            "in": "<-",
            "out": "->",
            "both": "-",
        }

        rel_filter = f":{relation_type}" if relation_type else ""
        arrow = dir_map.get(direction, "-")

        cypher = f"""
        MATCH (n)-[r{rel_filter}{arrow}](m)
        WHERE id(n) = '{node_id}'
        RETURN n, r, m
        LIMIT {limit}
        """

        return self.query(cypher)


# Resource factory function
def falkordb_resource(**kwargs) -> FalkorDBResource:
    """Factory for FalkorDB resource."""
    return FalkorDBResource(**kwargs)


# ============================================================================
# Cognee Resource
# ============================================================================


class CogneeResource(dg.ConfigurableResource):
    """Resource for Cognee AI memory service.

    Cognee provides:
    - Entity extraction from text
    - Knowledge graph construction
    - Semantic clustering
    - Integration with FalkorDB and LanceDB

    Example:
        @asset(resource_defs={"cognee": cognee_resource()})
        def knowledge_asset(context, cognee: CogneeResource):
            result = await cognee.extract_and_store(
                document_text=context.op_config["text"]
            )
            return result
    """

    # FalkorDB connection
    graph_uri: str = Field(
        default_factory=lambda: os.getenv(
            "COGNEE_GRAPH_URI", os.getenv("FALKORDB_URI", "redis://localhost:6379")
        ),
        description="Graph database URI",
    )

    graph_username: str | None = Field(
        default_factory=lambda: os.getenv("COGNEE_GRAPH_USER", os.getenv("FALKORDB_USER")),
        description="Graph database username",
    )

    graph_password: str | None = Field(
        default_factory=lambda: os.getenv("COGNEE_GRAPH_PASSWORD", os.getenv("FALKORDB_PASSWORD")),
        description="Graph database password",
    )

    # LanceDB connection
    vector_uri: str = Field(
        default_factory=lambda: os.getenv(
            "COGNEE_VECTOR_URI", os.getenv("LANCEDB_URI", "./lancedb_data")
        ),
        description="Vector database URI",
    )

    # LLM configuration
    llm_provider: str = Field(
        default="openai",
        description="LLM provider for extraction",
    )

    llm_model: str = Field(
        default="gpt-4o",
        description="LLM model",
    )

    llm_api_key: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", os.getenv("LLM_API_KEY")),
        description="LLM API key",
    )

    def get_service(self) -> Any:
        """Get Cognee service instance."""
        from sruth.shared.memory.cognee_service import CogneeService, CogneeConfig

        config = CogneeConfig(
            graph_uri=self.graph_uri,
            graph_username=self.graph_username,
            graph_password=self.graph_password,
            vector_uri=self.vector_uri,
            llm_provider=self.llm_provider,
            llm_model=self.llm_model,
            llm_api_key=self.llm_api_key,
        )

        return CogneeService(config)

    async def extract_and_store(
        self,
        text: str,
        dataset_name: str = "default",
    ) -> dict[str, Any]:
        """Extract knowledge graph from text.

        Args:
            text: Input text
            dataset_name: Dataset name

        Returns:
            Extraction results
        """
        service = self.get_service()
        return await service.extract_and_store(text, dataset_name)


# Resource factory function
def cognee_resource(**kwargs) -> CogneeResource:
    """Factory for Cognee resource."""
    return CogneeResource(**kwargs)


# ============================================================================
# LanceDB Resource
# ============================================================================


class LanceDBResource(dg.ConfigurableResource):
    """Resource for LanceDB vector database.

    LanceDB provides:
    - Fast vector similarity search
    - S3-backed storage via Lance format
    - Integration with Lakekeeper via "trojan horse" pattern
    - Namespace management for multi-tenant embeddings

    Example:
        @asset(resource_defs={"lancedb": lancedb_resource()})
        def embedding_asset(lancedb: LanceDBResource):
            results = await lancedb.search(
                namespace="curriculum",
                table_name="documents",
                query_vector=embedding,
            )
            return results
    """

    # S3 storage configuration
    s3_bucket: str = Field(
        default_factory=lambda: os.getenv("LANCEDB_S3_BUCKET", "lance"),
        description="S3 bucket for Lance table storage",
    )

    s3_endpoint: str = Field(
        default_factory=lambda: os.getenv("GARAGE_ENDPOINT_URL", "http://garage:3900"),
        description="S3 endpoint",
    )

    s3_access_key: str = Field(
        default_factory=lambda: os.getenv("GARAGE_ACCESS_KEY", "garage_key"),
        description="S3 access key",
    )

    s3_secret_key: str = Field(
        default_factory=lambda: os.getenv("GARAGE_SECRET_KEY", "garage_secret"),
        description="S3 secret key",
    )

    # Lakekeeper integration
    register_with_lakekeeper: bool = Field(
        default=True,
        description="Register Lance tables with Lakekeeper catalog",
    )

    lakekeeper_uri: str = Field(
        default_factory=lambda: os.getenv("LAKEKEEPER_CATALOG_URI", "http://lakekeeper:8181"),
        description="Lakekeeper REST catalog URI",
    )

    # Default embedding config
    default_dimension: int = Field(
        default=1024,
        description="Default vector dimension",
    )

    default_metric: str = Field(
        default="cosine",
        description="Default distance metric (cosine, euclidean, dot)",
    )

    async def search(
        self,
        namespace: str,
        table_name: str,
        query_vector: list[float],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors.

        Args:
            namespace: Table namespace
            table_name: Table name
            query_vector: Query embedding
            limit: Result limit

        Returns:
            Search results with scores
        """
        from sruth.shared.storage.lance_namespace import LanceNamespaceManager

        manager = LanceNamespaceManager(
            s3_bucket=self.s3_bucket,
            s3_endpoint=self.s3_endpoint,
            s3_access_key=self.s3_access_key,
            s3_secret_key=self.s3_secret_key,
            lakekeeper_uri=self.lakekeeper_uri,
        )

        return await manager.search_vector(
            namespace=namespace,
            table_name=table_name,
            query_vector=query_vector,
            limit=limit,
        )

    async def upsert(
        self,
        namespace: str,
        table_name: str,
        ids: list[str],
        vectors: list[list[float]],
        metadata: list[dict[str, Any]] | None = None,
        dimension: int | None = None,
    ) -> int:
        """Upsert embeddings to a table.

        Args:
            namespace: Table namespace
            table_name: Table name
            ids: Document IDs
            vectors: Embedding vectors
            metadata: Optional metadata
            dimension: Vector dimension (default from config)

        Returns:
            Number of vectors upserted
        """
        from sruth.shared.storage.lance_namespace import LanceNamespaceManager, LanceTableConfig

        # Create table config
        config = LanceTableConfig(
            namespace=namespace,
            table_name=table_name,
            dimension=dimension or self.default_dimension,
            metric=self.default_metric,
            s3_bucket=self.s3_bucket,
            register_with_lakekeeper=self.register_with_lakekeeper,
            lakekeeper_uri=self.lakekeeper_uri,
        )

        # Register with Lakekeeper if needed
        if self.register_with_lakekeeper:
            manager = LanceNamespaceManager(
                s3_bucket=self.s3_bucket,
                lakekeeper_uri=self.lakekeeper_uri,
            )
            await manager.register_table(config)

        # Upsert embeddings
        return await manager.upsert_embeddings(
            namespace=namespace,
            table_name=table_name,
            ids=ids,
            vectors=vectors,
            metadata=metadata,
        )

    async def create_table(
        self,
        namespace: str,
        table_name: str,
        dimension: int | None = None,
        metric: str | None = None,
    ) -> dict[str, Any]:
        """Create a new Lance table.

        Args:
            namespace: Table namespace
            table_name: Table name
            dimension: Vector dimension
            metric: Distance metric

        Returns:
            Table metadata
        """
        from sruth.shared.storage.lance_namespace import LanceNamespaceManager, LanceTableConfig

        manager = LanceNamespaceManager(
            s3_bucket=self.s3_bucket,
            lakekeeper_uri=self.lakekeeper_uri,
        )

        # Create namespace
        await manager.create_namespace(namespace)

        # Create table config
        config = LanceTableConfig(
            namespace=namespace,
            table_name=table_name,
            dimension=dimension or self.default_dimension,
            metric=metric or self.default_metric,
            s3_bucket=self.s3_bucket,
            register_with_lakekeeper=self.register_with_lakekeeper,
            lakekeeper_uri=self.lakekeeper_uri,
        )

        # Register with Lakekeeper
        if self.register_with_lakekeeper:
            return await manager.register_table(config)

        return {"table": table_name, "namespace": namespace, "registered": False}

    def get_table_path(self, namespace: str, table_name: str) -> str:
        """Get S3 path for a table.

        Args:
            namespace: Table namespace
            table_name: Table name

        Returns:
            S3 path
        """
        bucket = self.s3_bucket
        prefix = namespace.replace(".", "/")
        return f"s3://{bucket}/{prefix}/{table_name}.lance"


# Resource factory function
def lancedb_resource(**kwargs) -> LanceDBResource:
    """Factory for LanceDB resource."""
    return LanceDBResource(**kwargs)
