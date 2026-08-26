#!/usr/bin/env python3
"""
Seed the local Infisical `dev-baile/dev` environment with the 33 secrets
required by the 4 consumer stacks. Each secret is freshly generated with
`secrets.token_hex()` / `secrets.token_urlsafe()` (no production-leakage risk).

Usage:
    /usr/bin/env python3 /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar/scripts/seed-infisical-vault.py
or (recommended, sets env vars first):
    source /Users/cianmacandeisigh/dev/kings_college_galway/.scratch/infisical-bootstrap.sh
    python3 /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar/scripts/seed-infisical-vault.py
"""

import json
import os
import secrets
import subprocess
import sys
import urllib.request
import urllib.error

# Read from environment
TOKEN = os.environ.get("INFISICAL_TOKEN", "")
PROJECT_ID = os.environ.get("INFISICAL_PROJECT_ID", "")
API_URL = os.environ.get("INFISICAL_API_URL", "http://localhost:8081/api")
CLIENT_ID = os.environ.get("INFISICAL_LOCKET_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("INFISICAL_LOCKET_CLIENT_SECRET", "")

if not all([TOKEN, PROJECT_ID]):
    print("ERROR: INFISICAL_TOKEN and INFISICAL_PROJECT_ID must be set", file=sys.stderr)
    print(
        "Run: source /Users/cianmacandeisigh/dev/kings_college_galway/.scratch/infisical-bootstrap.sh",
        file=sys.stderr,
    )
    sys.exit(1)


def gen(n: int) -> str:
    return secrets.token_hex(n)


def ensure_folder(path: str):
    """Create the folder if it doesn't exist."""
    if path in ("", "/"):
        return  # root folder always exists
    url = f"{API_URL}/v1/folders"
    body = json.dumps(
        {
            "workspaceId": PROJECT_ID,
            "environment": "dev",
            "name": path,
            "path": f"/{path}",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=10).read()
        print(f"  [folder] /{path} (created)")
    except urllib.error.HTTPError as e:
        if e.code == 400 or e.code == 409:
            pass  # already exists
        else:
            print(f"  [folder] /{path} -> HTTP {e.code} (continuing)")


def upsert(path: str, key: str, value: str):
    # Use v3 raw-secrets endpoint (POST /api/v3/secrets/raw/{secretName})
    url = f"{API_URL}/v3/secrets/raw/{key}"
    body = json.dumps(
        {
            "environment": "dev",
            "workspaceId": PROJECT_ID,
            "secretPath": f"/{path}",
            "secretValue": value,
            "type": "shared",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if resp.status in (200, 201):
                print(f"[ok] {path}/{key}")
            else:
                print(f"[FAIL] {path}/{key} -> HTTP {resp.status}: {data}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        print(f"[FAIL] {path}/{key} -> HTTP {e.code}: {body}")


# Generate fresh secret values
SECRETS = {
    "infisical/encryption_key": gen(16),
    "infisical/auth_secret": secrets.token_urlsafe(32),
    "infisical/postgres_password": gen(24),
    "infisical/client_id": CLIENT_ID,
    "infisical/client_secret": CLIENT_SECRET,
    "infisical/project_id": PROJECT_ID,
    "lakehouse/postgres_password": gen(24),
    "lakehouse/rpc_secret": gen(32),
    "lakehouse/admin_token": gen(32),
    "lakehouse/access_key_id": gen(16),
    "lakehouse/secret_access_key": gen(32),
    "lakehouse/encryption_key": gen(32),
    "lakehouse/jdbc_password": gen(24),
    "lakehouse/dashboard_secret": gen(32),
    "lakehouse/source_pg_password": gen(24),
    "lakehouse/writer_s3_secret_key": gen(32),
    "lakehouse/lancedb_viewer_admin_token": gen(32),
    "lakehouse-garage/access_key_id": gen(16),
    "lakehouse-garage/secret_access_key": gen(32),
    "lakehouse-clickhouse/user": "oideachais",
    "lakehouse-clickhouse/password": gen(24),
    "lakehouse-clickhouse/db": "oideachais",
    "lakehouse-redis/password": gen(24),
    "litellm/master_key": "sk-" + gen(32),
    "litellm/salt_key": gen(16),
    "litellm/postgres_user": "lakekeeper",
    "litellm/postgres_password": gen(24),
    "litellm/postgres_db": "litellm",
    "litellm/database_url": f"postgresql://lakekeeper:{gen(24)}@lakehouse-postgres:5432/litellm",
    "mlflow/postgres_user": "lakekeeper",
    "mlflow/postgres_password": gen(24),
    "mlflow/aws_default_region": "garage",
    "mlflow/default_artifact_root": "s3://mlflow-artifacts/",
    "mlflow/uri": "http://mlflow:5000",
}

# =============================================================================
# 2026-08-15-lakehouse-memory-stack-deep-integration-v1 — Phase B additions
# =============================================================================
# The 30 new keys required by the unified memory-stack secrets contract.
# See proposal.md "The ~30 new Infisical keys" section.
SECRETS.update(
    {
        # Cognee — Galileo + LanceDB companion + PlanetScale override
        "cognee/galileo_api_key": "placeholder-set-via-infisical-ui-" + gen(8),
        "cognee/lancedb_namespace_token": gen(32),
        "cognee/planetscale_database_url": "postgresql://placeholder:placeholder@placeholder.psdb.cloud:5432/cognee?sslmode=require",
        # Graphiti — LiteLLM base URL + FalkorDB vector index + LanceDB companion
        "graphiti/openai_base_url": "http://litellm:4000/v1",
        "graphiti/falkordb_vector_index": "graphiti_temporal_" + gen(8),
        # (LANCEDB_API_KEY already exists at the lancedb/ path — see below)
        # FalkorDB — vector.so module URL + cluster mode toggle
        "falkordb/vector_module_url": "https://github.com/FalkorDB/FalkorDB/releases/download/v4.18.11/vector.so",
        "falkordb/cluster_mode": "no",
        # Memgraph — Enterprise license + OTLP + Langfuse fan-out
        "memgraph/license_file_path": "/etc/memgraph/license.json",
        # (MEMGRAPH_OTEL_EXPORTER_OTLP_ENDPOINT reuses logfire/otel_endpoint — see below)
        # LanceDB — Namespace token + Garage endpoint
        "lancedb/namespace_token": gen(32),
        "lancedb/garage_endpoint": "http://lakehouse-garage:3900",
        # Langfuse — OTLP fan-out + ClickHouse URL + Redis URL + PlanetScale override
        "langfuse/clickhouse_url": "clickhouse://oideachais:"
        + gen(16)
        + "@lakehouse-clickhouse:9000/oideachais",
        "langfuse/redis_url": "redis://:" + gen(16) + "@lakehouse-redis:6379/0",
        "langfuse/planetscale_database_url": "postgresql://placeholder:placeholder@placeholder.psdb.cloud:5432/langfuse?sslmode=require",
        # MLflow — PlanetScale override + Garage S3 endpoint
        "mlflow/planetscale_database_url": "postgresql://placeholder:placeholder@placeholder.psdb.cloud:5432/mlflow?sslmode=require",
        "mlflow/s3_endpoint": "http://lakehouse-garage:3900",
        # LiteLLM — OTLP fan-out + Gemini preview + Galileo observability
        "litellm/langfuse_otel_endpoint": "http://logfire-otel:4317",
        "litellm/gemini_api_key": "placeholder-set-via-infisical-ui-" + gen(8),
        "litellm/galileo_api_key": "placeholder-set-via-infisical-ui-" + gen(8),
        # Lakehouse — PlanetScale component creds + ClickHouse/Redis TLS + R2 endpoint
        "lakehouse/planetscale_username": "placeholder",
        "lakehouse/planetscale_host": "placeholder.psdb.cloud",
        "lakehouse-clickhouse/tls_cert": "placeholder-tls-cert-" + gen(8),
        "lakehouse-redis/tls_cert": "placeholder-tls-cert-" + gen(8),
        "lakehouse/r2_endpoint_url": "https://placeholder.r2.cloudflarestorage.com",
    }
)

# Group by prefix
prefixes = {}
for k in SECRETS:
    prefix = k.split("/")[0]
    prefixes.setdefault(prefix, []).append(k)

# Pre-create folders (parent first)
print("--- Pre-creating folders ---")
for prefix in sorted(prefixes.keys()):
    ensure_folder(prefix)

for prefix in sorted(prefixes.keys()):
    print(f"\n--- {prefix}/ ---")
    for path_key in prefixes[prefix]:
        path, key = path_key.split("/", 1)
        upsert(path, key, SECRETS[path_key])

# Save to a local seed snapshot (NEVER committed)
SNAPSHOT_PATH = "/Users/cianmacandeisigh/dev/kings_college_galway/.scratch/seeded-secrets.json"
with open(SNAPSHOT_PATH, "w") as f:
    json.dump(SECRETS, f, indent=2)
os.chmod(SNAPSHOT_PATH, 0o600)
print(f"\n[ok] {len(SECRETS)} secrets seeded across {len(prefixes)} paths")
print(f"[ok] snapshot saved to {SNAPSHOT_PATH}")
