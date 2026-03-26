"""
Lakekeeper integration for Lance Namespace.

This module provides:
- Configuration for connecting to Lakekeeper Iceberg REST Catalog
- Factory functions for creating Lance Namespace instances
- Helper functions for warehouse and namespace management
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

import urllib3

logger = logging.getLogger(__name__)


@dataclass
class LakekeeperConfig:
    """Configuration for Lakekeeper Iceberg REST Catalog."""

    endpoint: str
    warehouse: Optional[str] = None
    auth_token: Optional[str] = None
    connect_timeout: int = 10000
    read_timeout: int = 30000
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> "LakekeeperConfig":
        """Create configuration from environment variables."""
        return cls(
            endpoint=os.getenv("LAKEKEEPER_URL", "http://localhost:8181"),
            warehouse=os.getenv("LAKEKEEPER_WAREHOUSE"),
            auth_token=os.getenv("LAKEKEEPER_TOKEN"),
            connect_timeout=int(os.getenv("LAKEKEEPER_CONNECT_TIMEOUT", "10000")),
            read_timeout=int(os.getenv("LAKEKEEPER_READ_TIMEOUT", "30000")),
            max_retries=int(os.getenv("LAKEKEEPER_MAX_RETRIES", "3")),
        )

    def to_iceberg_properties(self, lance_root: str = "/tmp/lance") -> Dict[str, str]:
        """Convert to Iceberg namespace properties dict."""
        props = {
            "iceberg.endpoint": self.endpoint,
            "iceberg.root": lance_root,
        }
        if self.warehouse:
            props["iceberg.warehouse"] = self.warehouse
        if self.auth_token:
            props["iceberg.auth_token"] = self.auth_token
        props["iceberg.connect_timeout_millis"] = str(self.connect_timeout)
        props["iceberg.read_timeout_millis"] = str(self.read_timeout)
        props["iceberg.max_retries"] = str(self.max_retries)
        return props


class LakekeeperClient:
    """Simple client for Lakekeeper Management API."""

    def __init__(self, config: Optional[LakekeeperConfig] = None):
        self.config = config or LakekeeperConfig.from_env()
        self._init_http()

    def _init_http(self):
        """Initialize HTTP client."""
        timeout = urllib3.Timeout(
            connect=self.config.connect_timeout / 1000,
            read=self.config.read_timeout / 1000
        )
        self.http = urllib3.PoolManager(
            timeout=timeout,
            retries=urllib3.Retry(total=self.config.max_retries, backoff_factor=0.3)
        )
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.config.auth_token:
            self.headers["Authorization"] = f"Bearer {self.config.auth_token}"

    def health(self) -> Dict[str, Any]:
        """Check Lakekeeper health."""
        import json
        response = self.http.request(
            "GET",
            f"{self.config.endpoint}/health",
            headers=self.headers
        )
        if response.status >= 400:
            raise RuntimeError(f"Health check failed: {response.status}")
        return json.loads(response.data.decode("utf-8"))

    def bootstrap(self) -> bool:
        """Bootstrap Lakekeeper (accept terms of use)."""
        import json
        response = self.http.request(
            "POST",
            f"{self.config.endpoint}/management/v1/bootstrap",
            headers=self.headers,
            body=json.dumps({"accept-terms-of-use": True}).encode("utf-8")
        )
        return response.status < 400

    def create_project(self, project_id: str) -> bool:
        """Create a project in Lakekeeper."""
        import json
        response = self.http.request(
            "POST",
            f"{self.config.endpoint}/management/v1/project",
            headers=self.headers,
            body=json.dumps({"project-id": project_id}).encode("utf-8")
        )
        return response.status < 400

    def create_warehouse(
        self,
        warehouse_name: str,
        project_id: str,
        bucket: str,
        endpoint: str,
        access_key: str,
        secret_key: str,
        region: str = "us-east-1",
        path_style: bool = True,
        flavor: str = "minio",
    ) -> Dict[str, Any]:
        """Create a warehouse with S3 storage."""
        import json
        payload = {
            "warehouse-name": warehouse_name,
            "project-id": project_id,
            "storage-profile": {
                "type": "s3",
                "bucket": bucket,
                "region": region,
                "path-style-access": path_style,
                "endpoint": endpoint,
                "flavor": flavor,
                "sts-enabled": False,
            },
            "storage-credential": {
                "type": "s3",
                "credential-type": "access-key",
                "aws-access-key-id": access_key,
                "aws-secret-access-key": secret_key,
            },
        }
        response = self.http.request(
            "POST",
            f"{self.config.endpoint}/management/v1/warehouse",
            headers=self.headers,
            body=json.dumps(payload).encode("utf-8")
        )
        if response.status >= 400:
            error = response.data.decode("utf-8")
            raise RuntimeError(f"Failed to create warehouse: {error}")
        return json.loads(response.data.decode("utf-8"))

    def close(self):
        """Close the HTTP connection pool."""
        self.http.clear()


def get_lance_namespace(**kwargs):
    """
    Get a Lance namespace configured for Lakekeeper.

    Uses the IcebergNamespace from iceberg.py with Lakekeeper configuration.

    Args:
        **kwargs: Override configuration properties

    Returns:
        IcebergNamespace instance
    """
    # Import here to avoid circular imports
    import sys
    from pathlib import Path

    # Add parent directory to path if needed for iceberg.py
    ducklake_root = Path(__file__).parents[2]
    if str(ducklake_root) not in sys.path:
        sys.path.insert(0, str(ducklake_root))

    from lance.iceberg import IcebergNamespace

    config = LakekeeperConfig.from_env()
    properties = config.to_iceberg_properties()
    properties.update(kwargs)

    return IcebergNamespace(**properties)


def setup_lakekeeper_warehouse(
    warehouse_name: str = "dev-warehouse",
    project_id: str = "default",
    bucket: str = "ducklake",
    minio_endpoint: str = "http://minio:9000",
    access_key: str = "minio",
    secret_key: str = "devpassword",
) -> Dict[str, Any]:
    """
    Set up Lakekeeper with a warehouse for local development.

    This bootstraps Lakekeeper, creates a project, and creates a warehouse
    configured for MinIO S3-compatible storage.

    Returns:
        Warehouse creation response
    """
    client = LakekeeperClient()

    # Check health
    health = client.health()
    logger.info(f"Lakekeeper health: {health['health']}")

    # Bootstrap if needed (idempotent)
    client.bootstrap()
    logger.info("Lakekeeper bootstrapped")

    # Create project (may already exist)
    try:
        client.create_project(project_id)
        logger.info(f"Created project: {project_id}")
    except RuntimeError as e:
        if "already exists" not in str(e).lower():
            logger.warning(f"Project creation note: {e}")

    # Create warehouse
    warehouse = client.create_warehouse(
        warehouse_name=warehouse_name,
        project_id=project_id,
        bucket=bucket,
        endpoint=minio_endpoint,
        access_key=access_key,
        secret_key=secret_key,
    )
    logger.info(f"Created warehouse: {warehouse_name}")

    client.close()
    return warehouse


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)

    config = LakekeeperConfig.from_env()
    print(f"Lakekeeper endpoint: {config.endpoint}")

    client = LakekeeperClient(config)
    try:
        health = client.health()
        print(f"Health: {health}")
    except Exception as e:
        print(f"Health check failed: {e}")
    finally:
        client.close()
