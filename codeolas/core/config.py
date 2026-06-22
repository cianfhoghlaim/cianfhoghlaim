"""
Configuration for códeolas.

Centralizes all configuration with environment variable support.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class Config:
    """
    Configuration for códeolas.

    All settings can be overridden via environment variables with CODEOLAS_ prefix.
    """

    # Repository settings
    repo_path: str = field(
        default_factory=lambda: os.getenv(
            "CODEOLAS_REPO_PATH", str(Path.cwd())
        )
    )

    # LanceDB settings
    lancedb_uri: str = field(
        default_factory=lambda: os.getenv(
            "LANCEDB_URI", "./storage/data/lancedb"
        )
    )
    lancedb_table_prefix: str = field(
        default_factory=lambda: os.getenv("LANCEDB_TABLE_PREFIX", "codeolas_")
    )

    # Embedding settings
    embedding_model: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    )
    embedding_dimension: int = field(
        default_factory=lambda: int(os.getenv("EMBEDDING_DIMENSION", "1024"))
    )

    # HNSW index settings
    hnsw_num_partitions: int = field(
        default_factory=lambda: int(os.getenv("HNSW_NUM_PARTITIONS", "256"))
    )
    hnsw_num_sub_vectors: int = field(
        default_factory=lambda: int(os.getenv("HNSW_NUM_SUB_VECTORS", "96"))
    )
    hnsw_drop_threshold: int = field(
        default_factory=lambda: int(os.getenv("HNSW_DROP_THRESHOLD", "50"))
    )

    # Batching (CRITICAL: minimum 100 for performance)
    min_batch_size: int = field(
        default_factory=lambda: int(os.getenv("CODEOLAS_MIN_BATCH_SIZE", "100"))
    )
    max_batch_size: int = field(
        default_factory=lambda: int(os.getenv("CODEOLAS_MAX_BATCH_SIZE", "1000"))
    )

    # Graph database settings
    memgraph_uri: str = field(
        default_factory=lambda: os.getenv("MEMGRAPH_URI", "bolt://localhost:7687")
    )
    memgraph_user: str = field(
        default_factory=lambda: os.getenv("MEMGRAPH_USER", "")
    )
    memgraph_password: str = field(
        default_factory=lambda: os.getenv("MEMGRAPH_PASSWORD", "")
    )

    # Reranking settings
    rerank_provider: Literal["jina", "cohere", "aliyun", "none"] = field(
        default_factory=lambda: os.getenv("RERANK_PROVIDER", "none")  # type: ignore
    )
    rerank_api_key: str = field(
        default_factory=lambda: os.getenv("RERANK_API_KEY", "")
    )
    rerank_model: str = field(
        default_factory=lambda: os.getenv(
            "RERANK_MODEL", "jina-reranker-v2-base-multilingual"
        )
    )

    # Search settings
    default_search_limit: int = field(
        default_factory=lambda: int(os.getenv("CODEOLAS_SEARCH_LIMIT", "10"))
    )
    multihop_max_iterations: int = field(
        default_factory=lambda: int(os.getenv("CODEOLAS_MULTIHOP_MAX_ITER", "5"))
    )
    multihop_convergence_threshold: float = field(
        default_factory=lambda: float(
            os.getenv("CODEOLAS_MULTIHOP_CONVERGENCE", "0.85")
        )
    )

    # File patterns
    include_patterns: list[str] = field(
        default_factory=lambda: [
            "**/*.py",
            "**/*.ts",
            "**/*.tsx",
            "**/*.js",
            "**/*.jsx",
            "**/*.rs",
            "**/*.go",
            "**/*.java",
            "**/*.md",
            "**/*.yaml",
            "**/*.yml",
            "**/*.toml",
            "**/*.json",
            "**/*.sql",
            "**/*.sh",
        ]
    )
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            "**/node_modules/**",
            "**/.git/**",
            "**/dist/**",
            "**/build/**",
            "**/__pycache__/**",
            "**/.venv/**",
            "**/venv/**",
            "**/.pytest_cache/**",
            "**/target/**",
            "**/*.min.js",
            "**/*.min.css",
        ]
    )

    # Agent settings
    agno_storage_dir: str = field(
        default_factory=lambda: os.getenv(
            "AGNO_STORAGE_DIR", "./storage/sessions"
        )
    )

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls()

    def validate(self) -> list[str]:
        """Validate configuration, return list of warnings."""
        warnings = []

        if self.min_batch_size < 100:
            warnings.append(
                f"min_batch_size ({self.min_batch_size}) below recommended 100"
            )

        if self.embedding_dimension not in [384, 768, 1024, 1536, 4096]:
            warnings.append(
                f"embedding_dimension ({self.embedding_dimension}) is non-standard"
            )

        repo = Path(self.repo_path)
        if not repo.exists():
            warnings.append(f"repo_path does not exist: {self.repo_path}")

        return warnings


# Global config singleton
_config: Config | None = None


def get_config() -> Config:
    """Get the global config singleton."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def set_config(config: Config) -> None:
    """Set the global config."""
    global _config
    _config = config
