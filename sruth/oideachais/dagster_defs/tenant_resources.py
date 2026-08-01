"""
Tenant-Aware Resources for Multi-Tenant Data Pipelines
========================================================

Provides isolated DuckDB and LanceDB resources per tenant,
reading configuration from config/tenants/*.yaml files.

Usage:
    tenant_duckdb = TenantAwareDuckDBResource(tenant_id="aleyum")
    conn = tenant_duckdb.get_connection()
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from dagster import ConfigurableResource, EnvVar


# ============================================================================
# Configuration Loading
# ============================================================================

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", Path(__file__).parent.parent.parent.parent))


@lru_cache(maxsize=10)
def load_tenant_config(tenant_id: str) -> dict[str, Any]:
    """Load tenant configuration from YAML file with caching."""
    config_path = PROJECT_ROOT / "config" / "tenants" / f"{tenant_id}.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Tenant config not found: {config_path}")

    with open(config_path) as f:
        return yaml.safe_load(f)


def list_tenant_ids() -> list[str]:
    """List all available tenant IDs."""
    config_dir = PROJECT_ROOT / "config" / "tenants"
    if not config_dir.exists():
        return []
    return [p.stem for p in config_dir.glob("*.yaml")]


def get_tenant_storage_path(tenant_id: str, storage_type: Literal["duckdb", "lancedb", "assets"]) -> Path:
    """Get the storage path for a tenant."""
    config = load_tenant_config(tenant_id)
    storage = config.get("storage", {})

    path_key = {
        "duckdb": "duckdbPath",
        "lancedb": "lancedbPath",
        "assets": "assetsPath",
    }[storage_type]

    path_str = storage.get(path_key, f"./storage/data/tenants/{tenant_id}/{storage_type}")

    if path_str.startswith("./"):
        return PROJECT_ROOT / path_str[2:]
    return Path(path_str)


# ============================================================================
# Tenant-Aware DuckDB Resource
# ============================================================================


class TenantAwareDuckDBResource(ConfigurableResource):
    """
    DuckDB resource that provides isolated databases per tenant.

    Each tenant gets their own DuckDB file with tenant-specific schemas
    based on their tenant type (education vs portfolio).

    Usage:
        @asset
        def my_asset(context, tenant_duckdb: TenantAwareDuckDBResource):
            tenant_id = context.partition_key  # Or from config
            conn = tenant_duckdb.get_connection(tenant_id)
            # Use connection...
    """

    default_tenant: str = "cianfhoghlaim"
    enable_spatial: bool = True

    def get_database_path(self, tenant_id: str | None = None) -> Path:
        """Get the DuckDB path for a tenant."""
        tid = tenant_id or self.default_tenant
        return get_tenant_storage_path(tid, "duckdb")

    def get_connection(self, tenant_id: str | None = None):
        """Get a DuckDB connection for a tenant."""
        import duckdb

        db_path = self.get_database_path(tenant_id)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = duckdb.connect(str(db_path))

        if self.enable_spatial:
            try:
                conn.execute("INSTALL spatial; LOAD spatial;")
            except Exception:
                pass  # Spatial extension may not be available

        return conn

    def execute(self, query: str, params: list | None = None, tenant_id: str | None = None):
        """Execute a query for a specific tenant."""
        with self.get_connection(tenant_id) as conn:
            if params:
                return conn.execute(query, params).fetchall()
            return conn.execute(query).fetchall()

    def get_tenant_type(self, tenant_id: str | None = None) -> str:
        """Get the tenant type (education, portfolio, etc.)."""
        tid = tenant_id or self.default_tenant
        config = load_tenant_config(tid)
        return config.get("tenant", {}).get("type", "education")


# ============================================================================
# Tenant-Aware LanceDB Resource
# ============================================================================


class TenantAwareLanceDBResource(ConfigurableResource):
    """
    LanceDB resource that provides isolated vector databases per tenant.

    Each tenant gets their own LanceDB directory with tenant-specific tables.

    Usage:
        @asset
        def embedding_asset(context, tenant_lancedb: TenantAwareLanceDBResource):
            tenant_id = context.partition_key
            db = tenant_lancedb.get_db(tenant_id)
            # Use database...
    """

    default_tenant: str = "cianfhoghlaim"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384

    def get_database_path(self, tenant_id: str | None = None) -> Path:
        """Get the LanceDB path for a tenant."""
        tid = tenant_id or self.default_tenant
        return get_tenant_storage_path(tid, "lancedb")

    def get_db(self, tenant_id: str | None = None):
        """Get a LanceDB connection for a tenant."""
        import lancedb

        db_path = self.get_database_path(tenant_id)
        db_path.mkdir(parents=True, exist_ok=True)

        return lancedb.connect(str(db_path))

    def get_table(self, table_name: str, tenant_id: str | None = None):
        """Get or create a table for a tenant."""
        db = self.get_db(tenant_id)
        if table_name in db.table_names():
            return db.open_table(table_name)
        return None

    def create_table(self, table_name: str, data, tenant_id: str | None = None):
        """Create a table with initial data for a tenant."""
        db = self.get_db(tenant_id)
        return db.create_table(table_name, data, mode="overwrite")


# ============================================================================
# Tenant-Aware Asset Storage Resource
# ============================================================================


class TenantAssetStorageResource(ConfigurableResource):
    """
    Asset storage resource for tenant-specific files (images, media, etc.).

    Usage:
        @asset
        def media_asset(context, tenant_storage: TenantAssetStorageResource):
            path = tenant_storage.get_path("images/logo.png", tenant_id="aleyum")
            # Use path...
    """

    default_tenant: str = "cianfhoghlaim"

    def get_base_path(self, tenant_id: str | None = None) -> Path:
        """Get the assets base path for a tenant."""
        tid = tenant_id or self.default_tenant
        return get_tenant_storage_path(tid, "assets")

    def get_path(self, relative_path: str, tenant_id: str | None = None) -> Path:
        """Get full path for a tenant asset."""
        base = self.get_base_path(tenant_id)
        return base / relative_path

    def ensure_dir(self, relative_path: str, tenant_id: str | None = None) -> Path:
        """Ensure a directory exists for a tenant."""
        path = self.get_path(relative_path, tenant_id)
        path.mkdir(parents=True, exist_ok=True)
        return path


# ============================================================================
# Tenant Configuration Resource
# ============================================================================


class TenantConfigResource(ConfigurableResource):
    """
    Resource for accessing tenant configuration.

    Provides access to all tenant settings including:
    - Theme configuration
    - Enabled features
    - Data source configurations
    - Route settings

    Usage:
        @asset
        def config_asset(context, tenant_config: TenantConfigResource):
            config = tenant_config.get_config("aleyum")
            if config.get("features", {}).get("musicPlayer"):
                # Handle music features...
    """

    default_tenant: str = "cianfhoghlaim"

    def get_config(self, tenant_id: str | None = None) -> dict[str, Any]:
        """Get full configuration for a tenant."""
        tid = tenant_id or self.default_tenant
        return load_tenant_config(tid)

    def get_features(self, tenant_id: str | None = None) -> dict[str, bool]:
        """Get enabled features for a tenant."""
        config = self.get_config(tenant_id)
        return config.get("features", {})

    def is_feature_enabled(self, feature: str, tenant_id: str | None = None) -> bool:
        """Check if a feature is enabled for a tenant."""
        features = self.get_features(tenant_id)
        return features.get(feature, False)

    def get_data_sources(self, tenant_id: str | None = None) -> dict[str, list]:
        """Get data source configuration for a tenant."""
        config = self.get_config(tenant_id)
        return config.get("dataSources", {})

    def get_external_sources(self, tenant_id: str | None = None) -> list[dict]:
        """Get external data sources (Spotify, GitHub, etc.) for a tenant."""
        sources = self.get_data_sources(tenant_id)
        return sources.get("external", [])

    def list_tenants(self) -> list[str]:
        """List all available tenant IDs."""
        return list_tenant_ids()


# ============================================================================
# Resource Instances
# ============================================================================

tenant_duckdb_resource = TenantAwareDuckDBResource()
tenant_lancedb_resource = TenantAwareLanceDBResource()
tenant_storage_resource = TenantAssetStorageResource()
tenant_config_resource = TenantConfigResource()

# Export all tenant resources
tenant_resources = {
    "tenant_duckdb": tenant_duckdb_resource,
    "tenant_lancedb": tenant_lancedb_resource,
    "tenant_storage": tenant_storage_resource,
    "tenant_config": tenant_config_resource,
}
