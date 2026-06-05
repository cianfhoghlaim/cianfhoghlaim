# Nimtable — Iceberg Catalog Web UI

## Overview

Nimtable is a web-based table explorer for Apache Iceberg catalogs. It provides a browser UI for discovering, inspecting, and querying Iceberg tables — showing schemas, partition specs, snapshots, and data previews. Think of it as pgAdmin but for Iceberg instead of PostgreSQL.

## Why This Matters for Kings' College Galway

The curriculum lakehouse contains dozens of Iceberg tables (one per subject, per cycle, per examination type). Nimtable provides a graphical way to explore these tables without writing Iceberg API calls or DuckDB queries. A curriculum researcher can browse the `leaving_cert_mathematics` table, inspect its schema (unit, strand, learning outcome), view partition information (by year), and preview sample rows — all from a browser. This makes the data platform accessible to non-engineers, which is essential for a project that bridges education and engineering.

## Key Features

- **Catalog browser** — List databases, schemas, and tables in an Iceberg catalog
- **Schema inspection** — View column names, types, and comments
- **Snapshot history** — Browse table snapshots with timestamps
- **Partition view** — See partition specs and data distribution
- **Data preview** — Sample rows without writing SQL

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/machine_learning/nimtable
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Connects to the Lakekeeper REST catalog.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `ICEBERG_CATALOG_URL` | Yes | Lakekeeper REST catalog URL | `http://lakekeeper:8181` |
| `NIMTABLE_PORT` | No | Web UI port | `4000` |

## Access

- **Web UI**: `https://nimtable.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/nimtable/nimtable>
- **Latest**: Active development — Iceberg REST catalog support, snapshot browser, partition inspection

## Screenshot

Nimtable's web UI shows a three-panel layout: a left sidebar with a catalog tree (database → schema → table), a main panel showing the selected table's schema (column names, types, descriptions), and a bottom panel for data preview and snapshot history browsing. Partition information is displayed in a separate tab.
