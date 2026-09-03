# BIEP v3 — Quickstart (the canonical "first 30 minutes" guide)

> Per the `2026-08-13-biep-v3-systematic-download-ireland-england-v1`
> openspec change. The "first 30 minutes" guide for a newcomer to set
> up the BIEP v3 in their own environment.

## Before you start

You'll need:
- **Docker Desktop** (or Docker Engine on Linux)
- **mise** (the dev tool manager — `curl https://mise.jdx.dev/install.sh | sh`)
- **uv** (Python package manager — installed by mise)
- **Infisical CLI** (for secrets — installed by mise)

## Step 1: Clone + bootstrap (2 minutes)

```bash
git clone https://github.com/cianfhoghlaim/cianfhoghlaim.git
cd cianfhoghlaim
mise install
uv sync
```

## Step 2: Bring up the lakehouse stack (5 minutes)

```bash
docker compose -f bonneagar/stacks/lakehouse/compose.yaml up -d
```

This brings up 13 services:
- Garage S3 (port 3900)
- Lakekeeper Iceberg REST (port 8181)
- Lance REST namespace (port 8182)
- DuckLake Postgres (port 5433)
- ClickHouse (port 8123)
- Redis (port 6379)
- Nimtable (port 3018)
- Olake (admin)
- LanceDB Viewer (port 8081)
- + 4 helpers (Garage init, Lakekeeper migrate, Lance init, etc.)

## Step 3: Run `mise run biep:v3:setup` (10 minutes)

```bash
mise run biep:v3:setup
```

This single command:
1. Checks Docker is running
2. Brings up the lakehouse stack (13 services)
3. Smoke-tests the 13 services
4. Runs `baml-cli generate` to compile the BAML client
5. Runs `seed_registry()` to populate the 428-cohort British Isles registry
6. Creates the `cianhoghlaim` Lance namespace in Lakekeeper
7. Validates the 4 openspec changes (`2026-08-13-biep-v3-systematic-download-ireland-england-v1` + 3 follow-ups)
8. Runs `mise run lint:skills` (53/53 pass)

## Step 4: Run `mise run biep:v3:status` (30 seconds)

```bash
mise run biep:v3:status
```

This shows the current state of the entire BIEP v3 system:
- The 13 lakehouse service health
- The 428-cohort registry status
- The Dagster asset count
- The MotherDuck Dive + Flight count
- The Mise task count
- The 4 openspec changes status

## Step 5: Run the foundation + M1 (Ireland LC) (5 minutes)

```bash
mise run biep:v3:m0  # Foundation entrypoint
```

This runs the 6 foundation steps + the 4 M0 foundation assets (lakehouse
smoke test, BAML codegen gate, registry seed count, lance namespace
ready) + 4 asset checks.

```bash
mise run biep:v3:m1  # Ireland LC pipeline (12 cohorts, EN+GA)
```

This runs the 5-phase pattern for the 12 Ireland LC cohorts.

## Step 6: Verify the assets are working

```bash
# Open the Ireland LC notebook
uv run cianfhoghlaim-marimo edit 19_ireland_pipeline_dashboard
```

You should see:
- The 100-row Ireland cohort matrix (12 LC + 88 JC)
- The drill-down table with per-cohort RAGAS scores
- The schedule (yearly 1st September)
- The asset check status (all 3 should pass)

## Step 7: Run the 6 deferred jurisdictions (M5-M10) (one-off, per year)

```bash
mise run biep:v3:m5   # Scotland (150 cohorts)
mise run biep:v3:m6   # Wales (160 cohorts)
mise run biep:v3:m7   # Northern Ireland (70 cohorts)
mise run biep:v3:m8   # Jersey (120 cohorts)
mise run biep:v3:m9   # Guernsey (120 cohorts)
mise run biep:v3:m10  # Isle of Man (120 cohorts)
```

Each one runs the 5-phase pattern for that jurisdiction's cohorts.

## Step 8: Run the 2 scanner domains (monthly)

```bash
mise run biep:v3:filesystem:monthly:sync  # 11 filesystem DLT sources
mise run biep:v3:language:monthly:sync    # 19 language DLT sources
```

## Step 9: Verify the full BIEP v3 system

```bash
# Total cohorts: 12 + 88 + 147 + 129 + 150 + 160 + 70 + 120 + 120 + 120 = 1,116
# Plus 11 filesystem + 19 language = 30 scanner sources
# Total: 1,146 active items

# Check the unified 8-jurisdiction overview notebook
uv run cianfhoghlaim-marimo edit 23_8_jurisdiction_overview
```

## What to do next

- **Read the canonical docs**: `docs/agents/biiep-v3-systematic-download.md` + `biiep-v3-faq.md`
- **Browse the 8 jurisdiction dashboards**: notebooks 19, 20, 21, 22, 23
- **Browse the 2 catalog consoles**: notebooks 10_03, 10_04
- **Explore the MotherDuck Dives**: 14 BIEP v3 dives in `motherduck/dives/`
- **Check the Dagster assets**: 200+ assets across the 5 layers

## What to do if something goes wrong

| Symptom | Fix |
|:--|:--|
| `mise run biep:v3:setup` fails at step 3 (lakehouse smoke) | Check Docker is running, then `docker compose -f bonneagar/stacks/lakehouse/compose.yaml ps` |
| `mise run biep:v3:setup` fails at step 4 (BAML codegen) | Run `cd baml_src && uv run baml-cli generate` to see the error |
| `mise run biep:v3:setup` fails at step 5 (registry seed) | Check the MotherDuck + DuckLake connection |
| `mise run biep:v3:m<N>` fails at asset check | Run `mise run biep:v3:gate --milestone=m<N>` to see the failed checks |
| A BAML Extract* function raises an error | Check the PDF text in the test block (Phase 4 BAML Test) |
| A MotherDuck Dive returns 0 rows | Check the DuckLake table exists: `duckdb -c "SELECT 1 FROM cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.voted_canonical"` |

## See also

- `docs/agents/biiep-v3-systematic-download.md` — the canonical newcomer guide
- `docs/agents/biiep-v3-faq.md` — the canonical FAQ
- `docs/agents/biiep-v3-baml-client.md` — how to invoke the 6 new Extract* functions from Python
- `docs/agents/biiep-v3-storage-layout.md` — the DuckLake + Lance + MotherDuck layout
- `docs/agents/biiep-v3-cron-schedule.md` — the 4-cadence scheduling policy in detail
- `docs/agents/biiep-v3-bie-8-jurisdictions.md` — the 8-jurisdiction rollout + the 2 scanner domains
