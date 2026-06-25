"""
Configuration loader for crypto data pipelines.

Loads YAML configuration files and provides typed access to source
and database configurations.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class RateLimitConfig:
    """Rate limiting configuration for API sources."""

    requests_per_second: float = 5.0
    requests_per_minute: Optional[int] = None
    retry_attempts: int = 3
    retry_backoff: float = 2.0


@dataclass
class IncrementalConfig:
    """Incremental loading configuration."""

    cursor_path: str
    initial_value: Any = None
    end_value: Optional[Any] = None


@dataclass
class TransformConfig:
    """Data transformation configuration."""

    data_selector: Optional[str] = None
    mappings: dict[str, str] = field(default_factory=dict)
    static_fields: dict[str, Any] = field(default_factory=dict)
    computed_fields: dict[str, str] = field(default_factory=dict)


@dataclass
class ResourceConfig:
    """Configuration for a single API resource/endpoint."""

    name: str
    endpoint: str
    params: dict[str, Any] = field(default_factory=dict)
    primary_key: list[str] = field(default_factory=list)
    write_disposition: str = "merge"
    incremental: Optional[IncrementalConfig] = None
    transform: Optional[TransformConfig] = None
    schedule: Optional[str] = None
    base_url: Optional[str] = None  # Override source base_url


@dataclass
class AuthConfig:
    """Authentication configuration."""

    type: str  # "none", "api_key", "bearer", "oauth2"
    header: Optional[str] = None
    secret_key: Optional[str] = None


@dataclass
class SourceConfig:
    """Configuration for an API source."""

    name: str
    base_url: str
    auth: AuthConfig
    rate_limit: RateLimitConfig
    resources: dict[str, ResourceConfig]
    openapi_spec: Optional[str] = None


@dataclass
class DatabaseConfig:
    """Database connection configuration."""

    type: str
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    uri: Optional[str] = None
    dataset_name: Optional[str] = None


def _expand_env_vars(value: Any) -> Any:
    """Recursively expand environment variables in config values."""
    if isinstance(value, str):
        # Handle ${VAR:-default} syntax
        import re

        pattern = r"\$\{([^}:]+)(?::-([^}]*))?\}"

        def replace(match):
            var_name = match.group(1)
            default = match.group(2) or ""
            return os.environ.get(var_name, default)

        return re.sub(pattern, replace, value)
    elif isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_expand_env_vars(item) for item in value]
    return value


def _get_config_dir() -> Path:
    """Get the configuration directory path."""
    # Check for environment override
    if config_dir := os.environ.get("CRYPTO_CONFIG_DIR"):
        return Path(config_dir)

    # Default to config/ relative to this file's parent
    return Path(__file__).parent.parent.parent / "config"


def load_sources_config(config_path: Optional[Path] = None) -> dict[str, Any]:
    """
    Load the sources.yaml configuration file.

    Args:
        config_path: Optional path to config file. Defaults to config/sources.yaml

    Returns:
        Parsed and environment-expanded configuration dictionary
    """
    if config_path is None:
        config_path = _get_config_dir() / "sources.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    return _expand_env_vars(config)


def load_databases_config(config_path: Optional[Path] = None) -> dict[str, Any]:
    """
    Load the databases.yaml configuration file.

    Args:
        config_path: Optional path to config file. Defaults to config/databases.yaml

    Returns:
        Parsed and environment-expanded configuration dictionary
    """
    if config_path is None:
        config_path = _get_config_dir() / "databases.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    return _expand_env_vars(config)


def get_source_config(source_id: str, config: Optional[dict] = None) -> SourceConfig:
    """
    Get typed configuration for a specific API source.

    Args:
        source_id: Source identifier (e.g., "coingecko", "defillama")
        config: Optional pre-loaded config dict

    Returns:
        SourceConfig dataclass with typed configuration
    """
    if config is None:
        config = load_sources_config()

    # Check api_sources first
    if source_id in config.get("api_sources", {}):
        source_data = config["api_sources"][source_id]
    elif source_id in config.get("subgraph_sources", {}):
        source_data = config["subgraph_sources"][source_id]
    else:
        raise ValueError(f"Unknown source: {source_id}")

    # Parse auth config
    auth_data = source_data.get("auth", {"type": "none"})
    auth = AuthConfig(
        type=auth_data.get("type", "none"),
        header=auth_data.get("header"),
        secret_key=auth_data.get("secret_key"),
    )

    # Parse rate limit config
    rate_data = source_data.get("rate_limit", {})
    defaults = config.get("defaults", {}).get("rate_limit", {})
    rate_limit = RateLimitConfig(
        requests_per_second=rate_data.get(
            "requests_per_second", defaults.get("requests_per_second", 5.0)
        ),
        requests_per_minute=rate_data.get("requests_per_minute"),
        retry_attempts=rate_data.get(
            "retry_attempts", defaults.get("retry_attempts", 3)
        ),
        retry_backoff=rate_data.get("retry_backoff", defaults.get("retry_backoff", 2.0)),
    )

    # Parse resources
    resources = {}
    for res_name, res_data in source_data.get("resources", {}).items():
        # Parse incremental config
        inc_config = None
        if inc_data := res_data.get("incremental"):
            inc_config = IncrementalConfig(
                cursor_path=inc_data["cursor_path"],
                initial_value=inc_data.get("initial_value"),
                end_value=inc_data.get("end_value"),
            )

        # Parse transform config
        transform_config = None
        if trans_data := res_data.get("transform"):
            transform_config = TransformConfig(
                data_selector=trans_data.get("data_selector"),
                mappings=trans_data.get("mappings", {}),
                static_fields=trans_data.get("static_fields", {}),
                computed_fields=trans_data.get("computed_fields", {}),
            )

        # Handle primary_key as list
        primary_key = res_data.get("primary_key", [])
        if isinstance(primary_key, str):
            primary_key = [primary_key]

        resources[res_name] = ResourceConfig(
            name=res_name,
            endpoint=res_data["endpoint"],
            params=res_data.get("params", {}),
            primary_key=primary_key,
            write_disposition=res_data.get("write_disposition", "merge"),
            incremental=inc_config,
            transform=transform_config,
            schedule=res_data.get("schedule"),
            base_url=res_data.get("base_url"),
        )

    # Parse queries for subgraph sources
    for query_name, query_data in source_data.get("queries", {}).items():
        inc_config = None
        if inc_data := query_data.get("incremental"):
            inc_config = IncrementalConfig(
                cursor_path=inc_data["cursor_path"],
                initial_value=inc_data.get("initial_value"),
            )

        transform_config = None
        if trans_data := query_data.get("transform"):
            transform_config = TransformConfig(
                data_selector=trans_data.get("data_selector"),
                computed_fields=trans_data.get("computed_fields", {}),
            )

        primary_key = query_data.get("primary_key", [])
        if isinstance(primary_key, str):
            primary_key = [primary_key]

        resources[query_name] = ResourceConfig(
            name=query_name,
            endpoint="",  # GraphQL uses POST to base URL
            params={"query": query_data["query"], "variables": query_data.get("variables", {})},
            primary_key=primary_key,
            write_disposition=query_data.get("write_disposition", "merge"),
            incremental=inc_config,
            transform=transform_config,
            schedule=query_data.get("schedule"),
        )

    return SourceConfig(
        name=source_data["name"],
        base_url=source_data.get("base_url", source_data.get("endpoint", "")),
        auth=auth,
        rate_limit=rate_limit,
        resources=resources,
        openapi_spec=source_data.get("openapi_spec"),
    )


def get_database_config(db_type: str, config: Optional[dict] = None) -> DatabaseConfig:
    """
    Get typed configuration for a specific database.

    Args:
        db_type: Database type (e.g., "duckdb", "memgraph", "lancedb")
        config: Optional pre-loaded config dict

    Returns:
        DatabaseConfig dataclass with typed configuration
    """
    if config is None:
        config = load_databases_config()

    if db_type not in config:
        raise ValueError(f"Unknown database type: {db_type}")

    db_data = config[db_type]

    # Handle nested configs (local vs production)
    env = os.environ.get("ENVIRONMENT", "local")
    if env in db_data:
        db_data = {**db_data, **db_data[env]}

    return DatabaseConfig(
        type=db_type,
        host=db_data.get("host"),
        port=db_data.get("port"),
        database=db_data.get("database"),
        username=db_data.get("username"),
        password=db_data.get("password"),
        uri=db_data.get("uri"),
        dataset_name=db_data.get("dataset_name"),
    )


def get_defaults(config: Optional[dict] = None) -> dict[str, Any]:
    """Get default configuration values."""
    if config is None:
        config = load_sources_config()
    return config.get("defaults", {})


def get_documentation_sources(config: Optional[dict] = None) -> dict[str, Any]:
    """Get documentation sources configuration for scraping."""
    if config is None:
        config = load_sources_config()
    return config.get("documentation_sources", {})


def get_pdf_sources(config: Optional[dict] = None) -> dict[str, Any]:
    """Get PDF sources configuration for direct downloads."""
    if config is None:
        config = load_sources_config()
    return config.get("pdf_sources", {})


def get_knowledge_graph_schema(config: Optional[dict] = None) -> dict[str, Any]:
    """Get knowledge graph schema configuration."""
    if config is None:
        config = load_sources_config()
    return config.get("knowledge_graph", {})
