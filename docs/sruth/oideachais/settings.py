"""
Centralized settings for oideachais pipeline.

All configuration should be loaded from environment variables
with sensible defaults. Use OIDEACHAIS_ prefix for all settings.

Usage:
    from sruth.oideachais.settings import settings

    # Access settings
    url = settings.curriculum_url
    batch_size = settings.embed_batch_size
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class OideachasSettings(BaseSettings):
    """
    Configuration settings for the oideachais Celtic Education pipeline.

    All settings can be overridden via environment variables with
    OIDEACHAIS_ prefix. For example:
        OIDEACHAIS_EMBED_BATCH_SIZE=200
    """

    model_config = SettingsConfigDict(
        env_prefix="OIDEACHAIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ===========================================================================
    # Environment
    # ===========================================================================

    env: Literal["development", "staging", "production", "test"] = Field(
        default="development",
        description="Environment name",
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    # ===========================================================================
    # Data Source URLs
    # ===========================================================================

    curriculum_url: str = Field(
        default="https://curriculumonline.ie",
        description="Base URL for Curriculum Online",
    )

    ncca_url: str = Field(
        default="https://ncca.ie",
        description="Base URL for NCCA",
    )

    sec_url: str = Field(
        default="https://examinations.ie",
        description="Base URL for State Examinations Commission",
    )

    duchas_url: str = Field(
        default="https://duchas.ie",
        description="Base URL for Dúchas.ie Schools Collection",
    )

    tearma_url: str = Field(
        default="https://tearma.ie",
        description="Base URL for Téarma.ie terminology",
    )

    # ===========================================================================
    # Embedding Settings
    # ===========================================================================

    embed_model: str = Field(
        default="BAAI/bge-m3",
        description="Default embedding model",
    )

    embed_batch_size: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Batch size for embedding operations (min 100 for performance)",
    )

    embed_dimensions: int = Field(
        default=1024,
        description="Embedding dimensions (BGE-M3 default)",
    )

    embed_timeout: int = Field(
        default=60,
        ge=10,
        le=600,
        description="Timeout for embedding API calls in seconds",
    )

    # ===========================================================================
    # LanceDB Settings
    # ===========================================================================

    lancedb_uri: str = Field(
        default="~/.lancedb/oideachais",
        description="LanceDB connection URI (local path or db://cloud)",
    )

    lancedb_api_key: str = Field(
        default="",
        description="LanceDB Cloud API key",
    )

    lancedb_region: str = Field(
        default="eu-west-1",
        description="LanceDB Cloud region",
    )

    # ===========================================================================
    # DuckDB Settings
    # ===========================================================================

    duckdb_path: str = Field(
        default="~/.duckdb/oideachais.duckdb",
        description="Path to DuckDB database file",
    )

    duckdb_memory_limit: str = Field(
        default="4GB",
        description="DuckDB memory limit",
    )

    # ===========================================================================
    # Kafka Settings
    # ===========================================================================

    kafka_bootstrap_servers: str = Field(
        default="localhost:9092",
        description="Kafka bootstrap servers",
    )

    kafka_security_protocol: str = Field(
        default="PLAINTEXT",
        description="Kafka security protocol (PLAINTEXT, SASL_SSL)",
    )

    kafka_sasl_mechanism: str = Field(
        default="",
        description="Kafka SASL mechanism (PLAIN, SCRAM-SHA-256)",
    )

    kafka_api_key: str = Field(
        default="",
        description="Kafka API key (for Confluent Cloud)",
    )

    kafka_api_secret: str = Field(
        default="",
        description="Kafka API secret (for Confluent Cloud)",
    )

    kafka_topic_prefix: str = Field(
        default="oideachais",
        description="Prefix for Kafka topics",
    )

    # ===========================================================================
    # Rate Limiting
    # ===========================================================================

    max_requests_per_second: float = Field(
        default=10.0,
        ge=0.1,
        le=100.0,
        description="Maximum requests per second to external APIs",
    )

    request_timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Default HTTP request timeout in seconds",
    )

    # ===========================================================================
    # Retry Settings
    # ===========================================================================

    max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts",
    )

    retry_base_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=30.0,
        description="Base delay between retries in seconds",
    )

    retry_max_delay: float = Field(
        default=60.0,
        ge=1.0,
        le=300.0,
        description="Maximum delay between retries in seconds",
    )

    # ===========================================================================
    # Circuit Breaker Settings
    # ===========================================================================

    circuit_failure_threshold: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Failures before opening circuit",
    )

    circuit_recovery_time: float = Field(
        default=60.0,
        ge=5.0,
        le=600.0,
        description="Seconds to wait before testing recovery",
    )

    # ===========================================================================
    # Modal Settings
    # ===========================================================================

    modal_app_name: str = Field(
        default="oideachais",
        description="Modal application name",
    )

    modal_gpu_type: str = Field(
        default="A10G",
        description="Default GPU type for Modal functions",
    )

    modal_timeout: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Modal function timeout in seconds",
    )

    # ===========================================================================
    # MLflow Settings
    # ===========================================================================

    mlflow_tracking_uri: str = Field(
        default="http://localhost:5000",
        description="MLflow tracking server URI",
    )

    mlflow_experiment_name: str = Field(
        default="oideachais",
        description="Default MLflow experiment name",
    )

    # ===========================================================================
    # Observability
    # ===========================================================================

    langfuse_public_key: str = Field(
        default="",
        description="Langfuse public key for LLM tracing",
    )

    langfuse_secret_key: str = Field(
        default="",
        description="Langfuse secret key",
    )

    langfuse_host: str = Field(
        default="https://cloud.langfuse.com",
        description="Langfuse host URL",
    )

    # ===========================================================================
    # Validators
    # ===========================================================================

    @field_validator("lancedb_uri", "duckdb_path")
    @classmethod
    def expand_path(cls, v: str) -> str:
        """Expand ~ in paths."""
        return str(Path(v).expanduser())

    @field_validator("embed_batch_size")
    @classmethod
    def validate_batch_size(cls, v: int) -> int:
        """Warn if batch size is below recommended minimum."""
        if v < 100:
            import warnings

            warnings.warn(
                f"embed_batch_size={v} is below recommended minimum of 100. "
                "Performance may be significantly degraded."
            )
        return v

    # ===========================================================================
    # Computed Properties
    # ===========================================================================

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.env == "development"

    @property
    def is_test(self) -> bool:
        """Check if running in test mode."""
        return self.env == "test"

    @property
    def kafka_config(self) -> dict:
        """Get Kafka configuration dictionary."""
        config = {
            "bootstrap.servers": self.kafka_bootstrap_servers,
            "security.protocol": self.kafka_security_protocol,
        }
        if self.kafka_sasl_mechanism:
            config["sasl.mechanism"] = self.kafka_sasl_mechanism
            config["sasl.username"] = self.kafka_api_key
            config["sasl.password"] = self.kafka_api_secret
        return config


@lru_cache()
def get_settings() -> OideachasSettings:
    """
    Get cached settings instance.

    The settings are cached to avoid re-reading environment on every access.
    """
    return OideachasSettings()


# Global settings instance
settings = get_settings()
