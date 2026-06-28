# P1A-05 — MotherDuck (Phase 1A, Data Plane)

**Date:** 2026-06-28
**Phase:** 1A (Data Plane Foundations)
**Budget:** ~180 credits
**Subagent:** data-platform

## TL;DR

MotherDuck is the **managed DuckDB service** that lets Cianfhoghlaim query the lakehouse from any host without running DuckDB locally. It exposes 3 access patterns:

1. **`motherduck-mcp` MCP server** — 8 tools for cross-host queries from opencode
2. **`md:` SQL prefix** — direct DuckLake attach to a MotherDuck-managed database
3. **Web UI** — for human exploration + Dives (live dashboards)

The canonical Cianfhoghlaim pattern uses **MotherDuck Dives** for cross-team dashboards (curriculum analysis, leabharlann full-stack demo) — these run on MotherDuck's compute and read from the same DuckLake catalog the local DuckDB writes to.

## Code (where MotherDuck lives in Cianfhoghlaim)

| Path | Purpose |
|:--|:--|
| `motherduck` (MCP server in opencode.json) | 8 tools: query, list_databases, list_tables, etc. |
| `cianfhoghlaim/core/motherduck/init.py` | MotherDuck client init (Python) |
| `cianfhoghlaim/core/motherduck/dives/` | Dives dashboard specs (curriculum, leabharlann) |
| `stacks/motherduck/` | Docker compose stack (not used — MotherDuck is a cloud service) |
| `oideachais/notebooks/dives/` | Marimo notebooks synced to MotherDuck Dives |
| `cognify/motherduck_share_policy.yaml` | Org-level data-share access control |

**Canonical MotherDuck usage** (`cianfhoghlaim/core/motherduck/init.py`):

```python
import duckdb

def get_motherduck_connection(read_only: bool = True) -> duckdb.DuckDBPyConnection:
    """Open a MotherDuck connection that mounts the local lakehouse catalog."""
    conn = duckdb.connect(":memory:")
    conn.execute(f"""
        SET motherduck_token='{os.environ["MOTHERDUCK_TOKEN"]}';
        ATTACH 'md:' AS cloud;
        ATTACH 'ducklake:postgres://lakehouse-postgres:5432/lakehouse_catalog'
            AS lakehouse (DATA_PATH 's3://lakehouse-bucket/ducklake/');
        USE lakehouse;
    """)
    return conn

# Query the lakehouse from MotherDuck compute
df = get_motherduck_connection().execute("""
    SELECT
        schema_name,
        COUNT(DISTINCT table_name) AS table_count
    FROM lakehouse.information_schema.tables
    GROUP BY 1
    ORDER BY 2 DESC
""").df()
```

**MotherDuck Dive spec** (`cianfhoghlaim/core/motherduck/dives/curriculum_overview.py`):

```python
DIVE_SPEC = {
    "name": "Cianfhoghlaim Curriculum Overview",
    "sql": """
        SELECT
            subject,
            material_type,
            COUNT(*) AS row_count,
            SUM(n_pages) AS total_pages
        FROM lakehouse.oideachais.examinations_ie
        WHERE exam_year >= 2020
        GROUP BY 1, 2
        ORDER BY total_pages DESC
    """,
    "title": "Curriculum Overview (2020+)",
    "description": "24 subjects × 4 material types across 6 years of Irish Leaving Cert data",
    "refresh_interval": "1h",
    "tags": ["curriculum", "ireland", "leaving_cert"],
}
```

## Env (deployed configuration)

| Env var | Value | Source |
|:--|:--|:--|
| `MOTHERDUCK_TOKEN` | `infisical://dev-baile/motherduck/token` | Locket (cloud service token) |
| `MOTHERDUCK_DATABASE` | `lakehouse` | MotherDuck dashboard config |
| `MOTHERDUCK_ORG` | `cianfhoghlaim` | MotherDuck dashboard config |
| `MCP_MOTHERDUCK_COMMAND` | `uvx mcp-server-motherduck --db-path :memory: --read-write --allow-switch-databases` | opencode.json |
| `MCP_MOTHERDUCK_TOKEN` | `${MOTHERDUCK_TOKEN}` | Locket |

The MCP server is configured as a local `stdio` MCP (in `opencode.json`).

## CCC anchors (where this code lives)

```
MotherDuck Python client:    cianfhoghlaim/core/motherduck/init.py
MotherDuck MCP:               motherduck MCP (in opencode.json)
Dives dashboard specs:        cianfhoghlaim/core/motherduck/dives/
Marimo notebooks (synced):    oideachais/notebooks/dives/
Share policy:                 cognify/motherduck_share_policy.yaml
MotherDuck CLI:                ~/.local/bin/mdcli (installed)
```

Use these CCC search terms:
```
"MotherDuck"                  → 17 references across codebase
"motherduck_token"            → 5 token references
"ATTACH 'md:"                 → 4 MotherDuck attach sites
"CREATE SHARE"                → 3 data share definitions
"DIVE_SPEC"                   → 4 dive dashboards
```

## Drift log

| Date | Event | Action |
|:--|:--|:--|
| 2025-Q4 | Initial MotherDuck MCP server | Used for cross-host queries |
| 2026-01 | Added Dives for curriculum + leabharlann | Replaced bespoke marimo dashboards |
| 2026-02 | Switched from `motherduck-duckdb-driver` to `mcp-server-motherduck` | Better MCP integration |
| 2026-04 | Created 4 shares (`oideachais_public`, `oideachais_team`, `leabharlann_public`, `leabharlann_team`) | Cross-org read access |
| 2026-05 | Upgraded to MotherDuck 0.5 | Better Iceberg integration |
| 2026-06-28 | v4 consolidation: `sruth/oideachais/dlt_utils/motherduck_init.py` → `cianfhoghlaim/core/motherduck/init.py` | Pure rename |

## Anti-patterns (don't do this)

1. **Don't store MotherDuck tokens in connection strings** like `duckdb.connect("md:?motherduck_token=abc...")`. Use env vars.
2. **Don't run MotherDuck from inside the lakehouse Docker network** (it adds latency). Run from external hosts (opencode on MacBook, Dagster on arm1-oci, etc.).
3. **Don't use `--allow-switch-databases`** in production MCP server config. It's a debugging convenience; it lets the agent switch databases which could leak data.
4. **Don't create shares with `GRANT ALL TO PUBLIC`** (default). Always specify an org group (`cianfhoghlaim_team`, `oideachais_public`, etc.).
5. **Don't bypass Dives for production dashboards.** Dives provide versioning + access control; raw SQL queries don't.
6. **Don't use MotherDuck for the actual data writes.** DuckLake writes go through DuckDB (local) to Garage S3. MotherDuck only reads (compute layer).
7. **Don't set `--read-write` on production MCP servers.** Use `--read-only` unless absolutely needed; the Phase 0.3 deploy plan uses `--read-write` only for the dev MCP.

## Decision matrix (Phase 1A-05 conclusion)

| Decision | Choice | Rationale |
|:--|:--|:--|
| Compute layer | MotherDuck (managed DuckDB) | No local DuckDB on every host |
| Access control | Org + share-based | Cross-team without leaking private data |
| SQL dialect | DuckDB 1.2 + MotherDuck extensions | Single source of SQL truth |
| Dives | For cross-team dashboards | Versioning + sharing |
| MCP server | `mcp-server-motherduck` | Native opencode integration |
| Local dev | `MOTHERDUCK_DATABASE=lakehouse_dev` | Separate from production |
| Backup strategy | Dives versioned + DuckLake snapshots | Multi-layer recovery |
| Cost optimization | Use MotherDuck for queries only; writes go through local DuckDB → Garage | Minimize MotherDuck bill |

## Anti-pattern priority for Phase 1B

When researching Phase 1B (vector + graph + storage tier), look for:
- **LanceDB + Lance Blob + Lance Namespace** — vector + blob hybrid; REST Catalog bridge
- **FalkorDB + Graphiti + Dragonfly + RisingWave** — vector-graph hybrid (FalkorDB), bi-temporal knowledge graph (Graphiti)
- **Garage S3 + Iceberg REST Catalog + Lakekeeper** — S3-compat storage; Iceberg ACID
- **Cognee + Letta** — knowledge graph memory; agent persistent memory layer
- **Cloudflare R2 + Workers + D1** — edge storage + compute

## Files to read next

- `cianfhoghlaim/core/motherduck/init.py` (canonical MotherDuck init)
- `cognify/motherduck_share_policy.yaml` (share access control)
- `oideachais/notebooks/dives/` (Marimo dashboards synced to MotherDuck)
- `docs/skills/motherduck/SKILL.md` (canonical MotherDuck skill)
- `docs/skills/motherduck-data-modeling/SKILL.md` (CTAS + INSERT...SELECT patterns)
