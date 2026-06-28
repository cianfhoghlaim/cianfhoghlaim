"""CocoIndex Configuration.

Defines configuration dataclasses for code and documentation indexing.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CodeIndexingConfig:
    """Configuration for code indexing flows.

    Attributes:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        git_ref: Git reference (branch, tag, commit)
        path: Subdirectory to index (optional)
        included_patterns: File patterns to include (e.g., ["*.py", "*.md"])
        excluded_patterns: File patterns to exclude (e.g., ["**/.*", "node_modules"])
        chunk_size: Target chunk size in characters
        min_chunk_size: Minimum chunk size
        chunk_overlap: Overlap between chunks
        embedding_model: SentenceTransformer model name
        lancedb_uri: Path to LanceDB database
        table_name: Name of the LanceDB table
    """
    repo_owner: str
    repo_name: str
    git_ref: str = "main"
    path: str | None = None
    included_patterns: list[str] = field(default_factory=lambda: ["*.py", "*.md"])
    excluded_patterns: list[str] = field(default_factory=lambda: ["**/.*", "**/__pycache__", "**/node_modules"])
    chunk_size: int = 1000
    min_chunk_size: int = 300
    chunk_overlap: int = 300
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    lancedb_uri: str = "./data/github_intelligence.lancedb"
    table_name: str | None = None  # Defaults to {owner}_{repo}_code

    def __post_init__(self):
        if self.table_name is None:
            self.table_name = f"{self.repo_owner}_{self.repo_name}_code"

    @property
    def flow_name(self) -> str:
        """Generate a unique flow name."""
        return f"code_indexing_{self.repo_owner}_{self.repo_name}"


@dataclass
class DocsIndexingConfig:
    """Configuration for documentation indexing flows.

    Attributes:
        name: Unique name for this docs source
        source_path: Local path to documentation files
        included_patterns: File patterns to include
        excluded_patterns: File patterns to exclude
        chunk_size: Target chunk size
        embedding_model: Embedding model name
        lancedb_uri: Path to LanceDB database
        table_name: Name of the LanceDB table
    """
    name: str
    source_path: str
    included_patterns: list[str] = field(default_factory=lambda: ["*.md", "*.mdx"])
    excluded_patterns: list[str] = field(default_factory=lambda: ["**/.*"])
    chunk_size: int = 1000
    min_chunk_size: int = 300
    chunk_overlap: int = 300
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    lancedb_uri: str = "./data/github_intelligence.lancedb"
    table_name: str | None = None

    def __post_init__(self):
        if self.table_name is None:
            self.table_name = f"{self.name}_docs"

    @property
    def flow_name(self) -> str:
        """Generate a unique flow name."""
        return f"docs_indexing_{self.name}"


@dataclass
class GitHubAppConfig:
    """Configuration for GitHub App authentication.

    Used by CocoIndex for authenticated GitHub access.
    """
    app_id: int
    private_key_path: str
    rate_limit_rows_per_second: float = 1.0


def load_config_from_yaml(config_path: str | Path) -> dict[str, CodeIndexingConfig]:
    """Load repository configurations from YAML file.

    Args:
        config_path: Path to repos.yaml

    Returns:
        Dictionary mapping repo keys to CodeIndexingConfig objects
    """
    import yaml

    with open(config_path) as f:
        raw_config = yaml.safe_load(f)

    defaults = raw_config.get("defaults", {})
    repositories = raw_config.get("repositories", {})
    databases = raw_config.get("databases", {})

    configs = {}
    for key, repo in repositories.items():
        if not repo.get("index_code", True):
            continue

        configs[key] = CodeIndexingConfig(
            repo_owner=repo["owner"],
            repo_name=repo["repo"],
            git_ref=repo.get("git_ref", "main"),
            path=repo.get("path"),
            included_patterns=repo.get("included_patterns", defaults.get("included_patterns", ["*.py", "*.md"])),
            excluded_patterns=repo.get("excluded_patterns", defaults.get("excluded_patterns", ["**/.*"])),
            chunk_size=defaults.get("chunk_size", 1000),
            min_chunk_size=defaults.get("min_chunk_size", 300),
            chunk_overlap=defaults.get("chunk_overlap", 300),
            embedding_model=defaults.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"),
            lancedb_uri=databases.get("lancedb", {}).get("uri", "./data/github_intelligence.lancedb"),
        )

    return configs
