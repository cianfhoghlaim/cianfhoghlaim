# Scripts

Scripts module for the Oideachais platform.


## Cross-References

This module integrates with other components of the Oideachais platform:
- See the main [Agent Architecture](../../AGENTS.md) for global orchestration rules.
- View the [Skills Library](../../.skills/) for agent capability instructions.
- Relevant modules: [visualization](../visualization/README.md), [clients](../clients/README.md), [ui](../ui/README.md)

## scripts/lakehouse/ (Plan 5 of the 2026-10 convergence saga)

Three lakehouse-bridge helpers:

- **`init_lakehouse_postgres.sh`** — runs the canonical `bonnegar/stacks/lakehouse/init-db.sql` against the running lakehouse-postgres container. Idempotent.
- **`up_lakehouse_bridge.sh`** — brings up the 12 currently-down lakehouse services in dependency order (garage → redis → lakekeeper → lance-namespace → nimtable → graph DB backends → olake → otel-collector).
- **`verify_bridge.py`** — proves the LanceDB → DuckLake → Iceberg bridge works end-to-end (graceful stub fallback when offline).

Run order:
```bash
./scripts/lakehouse/up_lakehouse_bridge.sh   # bring up the 12 services
./scripts/lakehouse/init_lakehouse_postgres.sh   # init the 14 databases
uv run python scripts/lakehouse/verify_bridge.py   # verify the bridge
```

