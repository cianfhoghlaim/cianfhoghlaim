"""
Lance-Namespace Iceberg REST Sidecar.

Exposes Lance namespace operations as a REST API, registering Lance tables
as 'trojan horse' Iceberg tables in Lakekeeper with table_type=lance property.

This sidecar wraps the lance-namespace IcebergNamespace implementation,
providing a REST interface for Lance table registration and discovery.
"""

import os
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncIterator, Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import urllib3
import urllib.parse

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

class IcebergConfig:
    """Configuration for Iceberg REST Catalog connection."""

    def __init__(self):
        self.endpoint = os.getenv("ICEBERG_ENDPOINT", "http://lakekeeper:8181")
        self.warehouse = os.getenv("ICEBERG_WAREHOUSE", "lakehouse")
        self.prefix = os.getenv("ICEBERG_PREFIX", "")
        self.auth_token = os.getenv("ICEBERG_AUTH_TOKEN", "")
        self.lance_root = os.getenv("LANCE_ROOT", "s3://lance/")
        self.connect_timeout = int(os.getenv("ICEBERG_CONNECT_TIMEOUT_MILLIS", "10000"))
        self.read_timeout = int(os.getenv("ICEBERG_READ_TIMEOUT_MILLIS", "30000"))
        self.max_retries = int(os.getenv("ICEBERG_MAX_RETRIES", "3"))

    def get_full_api_url(self) -> str:
        """Get the full API URL with prefix."""
        base = self.endpoint.rstrip('/')
        if self.prefix:
            return f"{base}/{self.prefix}"
        return base


# =============================================================================
# REST Client for Iceberg API
# =============================================================================

class RestClient:
    """Simple REST client for Iceberg REST Catalog API."""

    def __init__(self, config: IcebergConfig):
        self.base_url = config.get_full_api_url()
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if config.auth_token:
            self.headers['Authorization'] = f"Bearer {config.auth_token}"
        if config.warehouse:
            self.headers['X-Iceberg-Access-Delegation'] = 'vended-credentials'

        timeout = urllib3.Timeout(
            connect=config.connect_timeout / 1000,
            read=config.read_timeout / 1000
        )
        self.http = urllib3.PoolManager(
            timeout=timeout,
            retries=urllib3.Retry(total=config.max_retries, backoff_factor=0.3)
        )

    def _make_request(self, method: str, path: str, params: Optional[Dict] = None,
                      body: Optional[Any] = None) -> Any:
        """Make HTTP request to Iceberg API."""
        url = f"{self.base_url}{path}"

        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

        body_data = None
        if body is not None:
            body_data = json.dumps(body).encode('utf-8')

        try:
            response = self.http.request(
                method, url, headers=self.headers, body=body_data
            )

            if response.status >= 400:
                raise HTTPException(
                    status_code=response.status,
                    detail=response.data.decode('utf-8')
                )

            if response.data:
                return json.loads(response.data.decode('utf-8'))
            return None

        except urllib3.exceptions.HTTPError as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get(self, path: str, params: Optional[Dict] = None) -> Any:
        return self._make_request('GET', path, params=params)

    def post(self, path: str, body: Any) -> Any:
        return self._make_request('POST', path, body=body)

    def delete(self, path: str, params: Optional[Dict] = None) -> None:
        self._make_request('DELETE', path, params=params)

    def close(self):
        self.http.clear()


# =============================================================================
# Pydantic Models
# =============================================================================

class HealthResponse(BaseModel):
    status: str
    timestamp: str


class NamespaceCreate(BaseModel):
    namespace: List[str]
    properties: Optional[Dict[str, str]] = None


class NamespaceResponse(BaseModel):
    namespace: List[str]
    properties: Optional[Dict[str, str]] = None


class TableCreate(BaseModel):
    name: str
    location: Optional[str] = None
    properties: Optional[Dict[str, str]] = None


class TableResponse(BaseModel):
    name: str
    namespace: List[str]
    location: str
    table_type: str = "lance"
    properties: Optional[Dict[str, str]] = None


# =============================================================================
# Constants
# =============================================================================

NAMESPACE_SEPARATOR = '\x1F'
TABLE_TYPE_KEY = "table_type"
TABLE_TYPE_LANCE = "lance"


def create_dummy_schema() -> Dict[str, Any]:
    """Create a dummy Iceberg schema for Lance tables."""
    return {
        "type": "struct",
        "schema-id": 0,
        "fields": [
            {
                "id": 1,
                "name": "dummy",
                "required": False,
                "type": "string"
            }
        ]
    }


def encode_namespace(namespace: List[str]) -> str:
    """Encode namespace for URL path."""
    encoded_parts = [urllib.parse.quote(s, safe='') for s in namespace]
    joined = NAMESPACE_SEPARATOR.join(encoded_parts)
    return urllib.parse.quote(joined, safe='')


# =============================================================================
# Global State
# =============================================================================

config: Optional[IcebergConfig] = None
client: Optional[RestClient] = None


def get_client() -> RestClient:
    """Get the REST client singleton."""
    global client, config
    if client is None:
        config = IcebergConfig()
        client = RestClient(config)
    return client


def get_config() -> IcebergConfig:
    """Get the config singleton."""
    global config
    if config is None:
        config = IcebergConfig()
    return config


# =============================================================================
# FastAPI Application
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager."""
    logger.info("Lance-Namespace sidecar starting...")

    # Initialize client on startup
    try:
        c = get_client()
        cfg = get_config()
        logger.info(f"Connected to Iceberg catalog at: {cfg.endpoint}")
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")

    yield

    # Cleanup
    if client:
        client.close()
    logger.info("Lance-Namespace sidecar shutdown.")


app = FastAPI(
    title="Lance-Namespace Sidecar",
    description="REST API for managing Lance tables via Iceberg REST Catalog",
    version="0.1.0",
    lifespan=lifespan,
)


# =============================================================================
# Health Endpoints
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health():
    """Liveness check."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/ready")
async def ready():
    """Readiness check - verifies Lakekeeper connectivity."""
    try:
        c = get_client()
        c.get('/v1/namespaces')
        return {"status": "ready", "lakekeeper": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Not ready: {e}")


@app.get("/health/deep")
async def deep_health():
    """Deep health check with dependency status."""
    checks = {"lakekeeper": "unknown", "s3": "unknown"}

    # Check Lakekeeper
    try:
        c = get_client()
        c.get('/v1/namespaces')
        checks["lakekeeper"] = "healthy"
    except Exception as e:
        checks["lakekeeper"] = f"unhealthy: {e}"

    # Check S3 (basic check via boto3 if available)
    try:
        import boto3
        s3 = boto3.client(
            's3',
            endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'garage')
        )
        s3.list_buckets()
        checks["s3"] = "healthy"
    except Exception as e:
        checks["s3"] = f"unhealthy: {e}"

    overall = "healthy" if all("healthy" in str(v) for v in checks.values()) else "degraded"
    return {"status": overall, "checks": checks}


# =============================================================================
# Namespace Endpoints
# =============================================================================

@app.get("/namespaces")
async def list_namespaces(
    parent: Optional[str] = Query(None, description="Parent namespace (dot-separated)"),
    page_token: Optional[str] = Query(None, description="Pagination token")
):
    """List all namespaces."""
    try:
        c = get_client()
        params = {}
        if parent:
            namespace_parts = parent.split(".")
            params['parent'] = encode_namespace(namespace_parts)
        if page_token:
            params['pageToken'] = page_token

        response = c.get('/v1/namespaces', params=params if params else None)

        namespaces = []
        if response and 'namespaces' in response:
            for ns in response['namespaces']:
                if ns:
                    namespaces.append(ns[-1] if isinstance(ns, list) else ns)

        return {"namespaces": sorted(set(namespaces))}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/namespaces", response_model=NamespaceResponse)
async def create_namespace(body: NamespaceCreate):
    """Create a new namespace."""
    try:
        c = get_client()
        request_body = {
            "namespace": body.namespace,
            "properties": body.properties or {}
        }
        response = c.post('/v1/namespaces', request_body)

        return {
            "namespace": body.namespace,
            "properties": response.get('properties') if response else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/namespaces/{namespace}", response_model=NamespaceResponse)
async def describe_namespace(namespace: str):
    """Describe a namespace."""
    try:
        c = get_client()
        namespace_parts = namespace.split(".")
        namespace_path = encode_namespace(namespace_parts)
        response = c.get(f"/v1/namespaces/{namespace_path}")

        return {
            "namespace": namespace_parts,
            "properties": response.get('properties') if response else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/namespaces/{namespace}")
async def drop_namespace(namespace: str):
    """Drop a namespace."""
    try:
        c = get_client()
        namespace_parts = namespace.split(".")
        namespace_path = encode_namespace(namespace_parts)
        c.delete(f"/v1/namespaces/{namespace_path}")
        return {"status": "dropped", "namespace": namespace_parts}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Table Endpoints (Lance-specific)
# =============================================================================

@app.get("/namespaces/{namespace}/tables")
async def list_tables(
    namespace: str,
    page_token: Optional[str] = Query(None, description="Pagination token")
):
    """List Lance tables in a namespace."""
    try:
        c = get_client()
        namespace_parts = namespace.split(".")
        namespace_path = encode_namespace(namespace_parts)

        params = {}
        if page_token:
            params['pageToken'] = page_token

        response = c.get(
            f"/v1/namespaces/{namespace_path}/tables",
            params=params if params else None
        )

        # Filter to only Lance tables
        tables = []
        if response and 'identifiers' in response:
            for table_id in response['identifiers']:
                table_name = table_id.get('name')
                if table_name:
                    # Check if it's a Lance table
                    try:
                        encoded_name = urllib.parse.quote(table_name, safe='')
                        table_info = c.get(
                            f"/v1/namespaces/{namespace_path}/tables/{encoded_name}"
                        )
                        if table_info and 'metadata' in table_info:
                            props = table_info['metadata'].get('properties', {})
                            if props.get(TABLE_TYPE_KEY, '').lower() == TABLE_TYPE_LANCE:
                                tables.append(table_name)
                    except Exception:
                        pass

        return {"tables": sorted(set(tables))}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/namespaces/{namespace}/tables", response_model=TableResponse)
async def create_lance_table(namespace: str, body: TableCreate):
    """Create a Lance table (trojan horse Iceberg table)."""
    try:
        c = get_client()
        cfg = get_config()
        namespace_parts = namespace.split(".")
        namespace_path = encode_namespace(namespace_parts)

        # Determine table location
        table_location = body.location
        if not table_location:
            table_location = f"{cfg.lance_root.rstrip('/')}/{'/'.join(namespace_parts)}/{body.name}"

        # Build properties with table_type=lance
        properties = {TABLE_TYPE_KEY: TABLE_TYPE_LANCE}
        if body.properties:
            properties.update(body.properties)

        # Create table request with dummy schema
        create_request = {
            "name": body.name,
            "location": table_location,
            "schema": create_dummy_schema(),
            "properties": properties
        }

        response = c.post(f"/v1/namespaces/{namespace_path}/tables", create_request)

        return {
            "name": body.name,
            "namespace": namespace_parts,
            "location": table_location,
            "table_type": TABLE_TYPE_LANCE,
            "properties": response.get('metadata', {}).get('properties') if response else properties
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/namespaces/{namespace}/tables/{table}", response_model=TableResponse)
async def describe_table(namespace: str, table: str):
    """Describe a Lance table."""
    try:
        c = get_client()
        namespace_parts = namespace.split(".")
        namespace_path = encode_namespace(namespace_parts)
        encoded_table = urllib.parse.quote(table, safe='')

        response = c.get(f"/v1/namespaces/{namespace_path}/tables/{encoded_table}")

        if not response or 'metadata' not in response:
            raise HTTPException(status_code=404, detail="Table not found")

        metadata = response['metadata']
        props = metadata.get('properties', {})

        # Verify it's a Lance table
        if props.get(TABLE_TYPE_KEY, '').lower() != TABLE_TYPE_LANCE:
            raise HTTPException(
                status_code=400,
                detail="Not a Lance table (missing table_type=lance property)"
            )

        return {
            "name": table,
            "namespace": namespace_parts,
            "location": metadata.get('location', ''),
            "table_type": TABLE_TYPE_LANCE,
            "properties": props
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/namespaces/{namespace}/tables/{table}")
async def drop_table(namespace: str, table: str):
    """Drop a Lance table."""
    try:
        c = get_client()
        namespace_parts = namespace.split(".")
        namespace_path = encode_namespace(namespace_parts)
        encoded_table = urllib.parse.quote(table, safe='')

        # Get table info before deletion
        table_location = None
        try:
            response = c.get(f"/v1/namespaces/{namespace_path}/tables/{encoded_table}")
            if response and 'metadata' in response:
                table_location = response['metadata'].get('location')
        except Exception:
            pass

        # Delete the table
        c.delete(
            f"/v1/namespaces/{namespace_path}/tables/{encoded_table}",
            params={'purgeRequested': 'false'}
        )

        return {
            "status": "dropped",
            "namespace": namespace_parts,
            "table": table,
            "location": table_location
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("SIDECAR_HOST", "0.0.0.0"),
        port=int(os.getenv("SIDECAR_PORT", "8182")),
    )
