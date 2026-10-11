"""marimo notebook: lakehouse_health — the Lakehouse bridge health dashboard.

Per the 2026-10-30-lakehouse-bridge-bring-up-v1 umbrella of
openspec/plans/2026-10-30-platform-reset-saga-v1.md (Umbrella 3 of 4).

A marimo dashboard that displays the lakehouse stack's health:
- The 12 currently-down services (per Stage 8 Gap 4; OrbStack Docker
  daemon missing)
- The 6 per-language `media.image_gen_chunks_<lang>` tables (the
  LanceDB target the media-intel saga's PR #208 populates)
- The 13 DuckLake databases (ducklake_cianfhoghlaim + the 5 sister
  schemas + dagster_local + olake_state + nimtable + langfuse + mlflow
  + litellm + cognee_cianfhoghlaim + olake_source)
- The bring-up runbook (operator-side: 3 scripts + OrbStack recovery)

The same numbers are also printed by:
    mise run core:lakehouse:health

Run with:
    uv run marimo edit notebooks/dashboards/lakehouse_health.py
"""
from __future__ import annotations

import marimo

__generated_with = "0.14.0"
app = marimo.App(width="full")


@app.cell
def _intro() -> None:
    import marimo as mo

    mo.md(
        """
        # Lakehouse Bridge Health (Umbrella 3 of the 2026-10-30 Platform Reset Saga)

        The **lakehouse stack health** for the Cianfhoghlaim monorepo.
        Drives the bring-up of the 12 currently-down services on
        `bunchloch`.

        Target: 12 services green · 6 per-language tables present ·
        13 databases initialized · OrbStack Docker daemon reachable.
        """
    )
    return (mo,)


@app.cell
def _compute() -> None:
    import json
    import os
    import subprocess
    from pathlib import Path

    workspace_root = Path(os.environ.get("WORKSPACE_ROOT", "."))

    # The 12 down services (per Stage 8 Gap 4).
    DOWN_SERVICES = [
        "garage", "garage-init", "redis", "lakekeeper-migrate",
        "lakekeeper", "lance-namespace", "nimtable", "cognee",
        "graphiti", "falkordb", "memgraph", "memgraph-lab", "olake",
    ]
    # 16 services in the unified lakehouse stack (per compose.yaml).
    ALL_SERVICES = [
        *DOWN_SERVICES,
        "postgres", "clickhouse", "lancedb-viewer", "otel-collector",
    ]

    # The 6 per-language media.image_gen_chunks_<lang> tables.
    PER_LANG_TABLES = [
        "image_gen_chunks_ga",  # gaeilge (Irish)
        "image_gen_chunks_cy",  # cymraeg (Welsh)
        "image_gen_chunks_gd",  # gaidhlig (Scottish Gaelic)
        "image_gen_chunks_gv",  # gaelg (Manx)
        "image_gen_chunks_kw",  # kernewek (Cornish)
        "image_gen_chunks_br",  # brezhoneg (Breton)
    ]

    # The 13 DuckLake databases.
    DUCKLAKE_DATABASES = [
        "ducklake_cianfhoghlaim",
        "ducklake_crypteolas", "ducklake_aleyum", "ducklake_croilar",
        "ducklake_tuath", "ducklake_meaisinfhoghlaim",
        "dagster_local", "olake_state", "nimtable",
        "langfuse", "mlflow", "litellm",
        "cognee_cianfhoghlaim", "olake_source",
    ]

    def check_docker() -> bool:
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                cwd=str(workspace_root),
                capture_output=True,
                text=True,
                check=False,
                timeout=2,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def check_verify_bridge() -> dict:
        try:
            result = subprocess.run(
                ["./.venv/bin/python", "scripts/lakehouse/verify_bridge.py", "--json"],
                cwd=str(workspace_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            return {"ok": False, "stub": True, "checks": [], "stub_note": "verify_bridge returned non-zero"}
        except (FileNotFoundError, json.JSONDecodeError):
            return {"ok": False, "stub": True, "checks": []}

    metrics: dict = {
        "down_services": DOWN_SERVICES,
        "all_services": ALL_SERVICES,
        "per_lang_tables": PER_LANG_TABLES,
        "ducklake_databases": DUCKLAKE_DATABASES,
        "docker_ok": check_docker(),
        "verify_bridge": check_verify_bridge(),
    }

    return (metrics, workspace_root)


@app.cell
def _render(metrics) -> None:
    import marimo as mo

    bridge = metrics.get("verify_bridge", {})
    table = mo.ui.table(
        data=[
            ("Metric", "Value", "Target", "Status"),
            (
                "Docker daemon (OrbStack)",
                "reachable" if metrics.get("docker_ok") else "UNREACHABLE",
                "reachable",
                "🟢" if metrics.get("docker_ok") else "🔴",
            ),
            (
                "12 down services",
                str(len(metrics.get("down_services", []))),
                "12 (per Stage 8 Gap 4)",
                "🟡",
            ),
            (
                "Per-language media tables",
                str(len(metrics.get("per_lang_tables", []))),
                "6 (ga/cy/gd/gv/kw/br)",
                "🟡",
            ),
            (
                "DuckLake databases",
                str(len(metrics.get("ducklake_databases", []))),
                "14 (incl. olake_source)",
                "🟡",
            ),
            (
                "Bridge verifier status",
                bridge.get("stub_note", "OK" if bridge.get("ok") else "FAIL"),
                "OK (all 12 services + 6 tables)",
                "🟢" if bridge.get("ok") and not bridge.get("stub") else "🔴",
            ),
        ],
        label="Lakehouse bridge health",
    )
    _ = table
    return (table,)


@app.cell
def _actions() -> None:
    import marimo as mo

    mo.md(
        """
        ## What to do next

        - **Docker daemon UNREACHABLE** (the operator-side blocker):
          1. **Restart OrbStack**: `killall OrbStack; open -a OrbStack`
             (or `osascript -e 'quit app "OrbStack"'; open -a OrbStack`)
          2. **Verify socket**: `ls -la /var/run/docker.sock` (should be a
             symlink to `~/.orbstack/run/docker.sock`). If not:
             `sudo ln -sf ~/.orbstack/run/docker.sock /var/run/docker.sock`
          3. **Verify context**: `docker context ls` (should show
             `orbstack *` as the default). If not:
             `docker context use orbstack`
          4. **Verify with a smoke test**: `docker run --rm hello-world`

          The full runbook is at
          `docs/lakehouse/orbstack-docker-recovery.md` (added in this change).

        - **Bridge verifier FAIL** but docker is up: run the bring-up
          `mise run core:lakehouse:up` (operator-side; brings up the 12
          services in dependency order). Then `mise run core:lakehouse:health`
          to verify.

        - **Bridge verifier FAIL** + the `ducklake_cianfhoghlaim` namespace
          is missing: after bringing the 12 services up, run
          `bash scripts/lakehouse/init_lakehouse_postgres.sh` to create
          the 14 databases.

        - **Bridge verifier OK**: ship Umbrella 4 (the saga closure).

        ## Related tasks

        - `mise run core:lakehouse:health` — the bridge verifier
        - `mise run core:lakehouse:up` — the operator-side bring-up
        - `mise run data:lakehouse-smoke-test` — the 6-service legacy alias
        - `bash scripts/lakehouse/up_lakehouse_bridge.sh` — the raw script
        - `bash scripts/lakehouse/init_lakehouse_postgres.sh` — the 14 DB init
        - `uv run python scripts/lakehouse/verify_bridge.py` — the raw verifier

        ## Saga context

        This dashboard is Umbrella 3 of 4 in the
        [2026-10-30 Platform Reset Saga](../../../openspec/plans/2026-10-30-platform-reset-saga-v1.md):

        1. **Umbrella 1** (PR #209): housekeeping + code de-sprawl — MERGEABLE
        2. **Umbrella 2** (PR #210): BAML repair + schema-naming convergence — MERGEABLE
        3. **Umbrella 3** (this one): lakehouse bridge bring-up
        4. **Umbrella 4** (PR #211): openspec backlog triage — MERGEABLE
        """
    )


if __name__ == "__main__":
    app.run()
