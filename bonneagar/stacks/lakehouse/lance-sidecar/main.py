"""
Lance-Namespace Sidecar (2026-08-23 rewrite).

Thin FastAPI wrapper around the official `lance-namespace-impls[iceberg]`
library (the `IcebergNamespace` class). Registers Lance tables as "trojan
horse" Iceberg tables in Lakekeeper via the `table_type=lance` property.

CHANGED 2026-08-23 (lakehouse-production-config-and-lance-sidecar-modernization-v1):
  - Replaced the hand-rolled urllib3 Iceberg REST client (567 LOC) with the
    official `lance-namespace-impls[iceberg]` library.
  - All namespace + table CRUD is delegated to `IcebergNamespace`.
  - This wrapper only handles the HTTP-to-SDK translation (~150 LOC).
  - Upstream bug fixes come automatically when we bump the library version.
"""
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from lance_namespace_impls.iceberg import IcebergNamespace

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# =============================================================================
# Configuration (env-driven, matches the legacy sidecar's contract)
# =============================================================================


def _build_iceberg_config() -> Dict[str, Any]:
    """Build the IcebergNamespace config dict from env vars.

    Mirrors the legacy sidecar's IcebergConfig fields so existing compose
    + secrets.env continue to work without changes.
    """
    cfg: Dict[str, Any] = {
        "endpoint": os.getenv("ICEBERG_ENDPOINT", "http://lakekeeper:8181"),
        "root": os.getenv("LANCE_ROOT", "s3://lance/"),
    }
    # Optional auth token (empty default keeps dev working)
    auth_token = os.getenv("ICEBERG_AUTH_TOKEN", "")
    if auth_token:
        cfg["auth_token"] = auth_token
    # Timeouts (millis → seconds for the official SDK)
    cfg["connect_timeout"] = int(os.getenv("ICEBERG_CONNECT_TIMEOUT_MILLIS", "10000")) // 1000
    cfg["read_timeout"] = int(os.getenv("ICEBERG_READ_TIMEOUT_MILLIS", "30000")) // 1000
    cfg["max_retries"] = int(os.getenv("ICEBERG_MAX_RETRIES", "3"))
    return cfg


# =============================================================================
# FastAPI app + lifespan (init IcebergNamespace once, reuse for all requests)
# =============================================================================
iceberg_ns: Optional[IcebergNamespace] = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize the IcebergNamespace on startup."""
    global iceberg_ns
    try:
        cfg = _build_iceberg_config()
        iceberg_ns = IcebergNamespace(**cfg)
        logger.info(
            "Lance-Namespace sidecar connected to Iceberg REST catalog at %s",
            cfg["endpoint"],
        )
    except Exception as e:
        logger.error("Failed to initialize IcebergNamespace: %s", e)
    yield
    if iceberg_ns:
        try:
            iceberg_ns.close()
        except Exception:
            pass
    logger.info("Lance-Namespace sidecar shutdown.")


app = FastAPI(
    title="Lance-Namespace Sidecar",
    description="Thin FastAPI wrapper around IcebergNamespace (lance-namespace-impls[iceberg])",
    version="0.3.0",
    lifespan=lifespan,
)


# =============================================================================
# Health endpoints (unchanged from the legacy sidecar)
# =============================================================================


@app.get("/health")
async def health() -> Dict[str, str]:
    """Liveness check — always returns OK if the process is up."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/ready")
async def ready() -> Dict[str, str]:
    """Readiness check — verifies IcebergNamespace is initialized."""
    if iceberg_ns is None:
        raise HTTPException(status_code=503, detail="IcebergNamespace not initialized")
    return {"status": "ready", "iceberg": "connected"}


@app.get("/health/deep")
async def deep_health() -> Dict[str, Any]:
    """Deep health check with dependency status."""
    checks: Dict[str, str] = {"iceberg": "unknown"}
    try:
        if iceberg_ns is not None:
            iceberg_ns.namespace_id()
            checks["iceberg"] = "healthy"
        else:
            checks["iceberg"] = "unhealthy: not initialized"
    except Exception as e:
        checks["iceberg"] = f"unhealthy: {e}"
    overall = "healthy" if all("healthy" in str(v) for v in checks.values()) else "degraded"
    return {"status": overall, "checks": checks}


# =============================================================================
# Namespace endpoints (delegated to IcebergNamespace)
# =============================================================================


@app.get("/namespaces")
async def list_namespaces(
    parent: Optional[str] = Query(None, description="Parent namespace (dot-separated)"),
    page_token: Optional[str] = Query(None, description="Pagination token"),
) -> Dict[str, Any]:
    """List all namespaces."""
    from lance_namespace_urllib3_client.models import ListNamespacesRequest

    if iceberg_ns is None:
        raise HTTPException(status_code=503, detail="not initialized")
    try:
        # Pass warehouse as first element of id, then optional parent namespace
        if parent:
            parent_parts = parent.split(".")
            req_id = ["lakehouse"] + parent_parts
        else:
            req_id = ["lakehouse"]
        req = ListNamespacesRequest(id=req_id, page_token=page_token)
        resp = iceberg_ns.list_namespaces(req)
        namespaces = []
        for ns in resp.namespaces or []:
            # ns is like "lakehouse.foo.bar" — strip the warehouse prefix
            parts = ns.split(".")
            namespaces.append(".".join(parts[1:]) if len(parts) > 1 else parts[0])
        return {"namespaces": sorted(set(namespaces))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/namespaces")
async def create_namespace(body: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new namespace."""
    from lance_namespace_urllib3_client.models import CreateNamespaceRequest

    if iceberg_ns is None:
        raise HTTPException(status_code=503, detail="not initialized")
    try:
        ns_path = body.get("namespace", [])
        if not ns_path:
            raise HTTPException(status_code=400, detail="namespace required")
        req_id = ["lakehouse"] + ns_path
        req = CreateNamespaceRequest(id=req_id, properties=body.get("properties", {}))
        resp = iceberg_ns.create_namespace(req)
        return {"namespace": ns_path, "properties": resp.properties}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/namespaces/{namespace}")
async def describe_namespace(namespace: str) -> Dict[str, Any]:
    """Describe a namespace."""
    from lance_namespace_urllib3_client.models import DescribeNamespaceRequest

    if iceberg_ns is None:
        raise HTTPException(status_code=503, detail="not initialized")
    try:
        ns_parts = namespace.split(".")
        req_id = ["lakehouse"] + ns_parts
        req = DescribeNamespaceRequest(id=req_id)
        resp = iceberg_ns.describe_namespace(req)
        return {"namespace": ns_parts, "properties": resp.properties}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/namespaces/{namespace}")
async def drop_namespace(namespace: str) -> Dict[str, Any]:
    """Drop a namespace."""
    from lance_namespace_urllib3_client.models import DropNamespaceRequest

    if iceberg_ns is None:
        raise HTTPException(status_code=503, detail="not initialized")
    try:
        ns_parts = namespace.split(".")
        req_id = ["lakehouse"] + ns_parts
        req = DropNamespaceRequest(id=req_id)
        iceberg_ns.drop_namespace(req)
        return {"status": "dropped", "namespace": ns_parts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Table endpoints (delegated to IcebergNamespace, with table_type=lance hack)
# =============================================================================

TABLE_TYPE_KEY = "table_type"
TABLE_TYPE_LANCE = "lance"


@app.get("/namespaces/{namespace}/tables")
async def list_tables(
    namespace: str,
    page_token: Optional[str] = Query(None, description="Pagination token"),
) -> Dict[str, Any]:
    """List Lance tables in a namespace (filters by table_type=lance property)."""
    from lance_namespace_urllib3_client.models import ListTablesRequest

    if iceberg_ns is None:
        raise HTTPException(status_code=503, detail="not initialized")
    try:
        ns_parts = namespace.split(".")
        req_id = ["lakehouse"] + ns_parts
        req = ListTablesRequest(id=req_id, page_token=page_token)
        resp = iceberg_ns.list_tables(req)
        # The official list_tables already filters by table_type=lance via
        # the IcebergNamespace._should_include_lance_table() helper
        return {"tables": sorted(set(resp.tables or []))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/namespaces/{namespace}/tables")
async def declare_lance_table(namespace: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """Declare a Lance table (registers as a "trojan horse" Iceberg table)."""
    from lance_namespace_urllib3_client.models import DeclareTableRequest

    if iceberg_ns is None:
        raise HTTPException(status_code=503, detail="not initialized")
    try:
        ns_parts = namespace.split(".")
        table_name = body.get("name")
        if not table_name:
            raise HTTPException(status_code=400, detail="name required")
        # Force table_type=lance on every declaration
        props = body.get("properties") or {}
        props[TABLE_TYPE_KEY] = TABLE_TYPE_LANCE
        req_id = ["lakehouse"] + ns_parts + [table_name]
        req = DeclareTableRequest(
            id=req_id,
            location=body.get("location"),
            properties=props,
        )
        resp = iceberg_ns.declare_table(req)
        return {
            "name": table_name,
            "namespace": ns_parts,
            "location": resp.location,
            "table_type": TABLE_TYPE_LANCE,
            "properties": resp.properties,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/namespaces/{namespace}/tables/{table}")
async def describe_table(namespace: str, table: str) -> Dict[str, Any]:
    """Describe a Lance table."""
    from lance_namespace_urllib3_client.models import DescribeTableRequest

    if iceberg_ns is None:
        raise HTTPException(status_code=503, detail="not initialized")
    try:
        ns_parts = namespace.split(".")
        req_id = ["lakehouse"] + ns_parts + [table]
        req = DescribeTableRequest(id=req_id)
        resp = iceberg_ns.describe_table(req)
        # Verify it's a Lance table (the official SDK raises InvalidInput
        # if the table_type is wrong)
        return {
            "name": table,
            "namespace": ns_parts,
            "location": resp.location,
            "table_type": TABLE_TYPE_LANCE,
            "properties": resp.properties,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/namespaces/{namespace}/tables/{table}")
async def deregister_table(namespace: str, table: str) -> Dict[str, Any]:
    """Deregister a Lance table (keeps data on S3, removes from catalog)."""
    from lance_namespace_urllib3_client.models import DeregisterTableRequest

    if iceberg_ns is None:
        raise HTTPException(status_code=503, detail="not initialized")
    try:
        ns_parts = namespace.split(".")
        req_id = ["lakehouse"] + ns_parts + [table]
        req = DeregisterTableRequest(id=req_id)
        iceberg_ns.deregister_table(req)
        return {"status": "dropped", "namespace": ns_parts, "table": table}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Main entry point
# =============================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("SIDECAR_HOST", "0.0.0.0"),
        port=int(os.getenv("SIDECAR_PORT", "8182")),
    )
