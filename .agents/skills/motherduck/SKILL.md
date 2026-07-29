---
name: motherduck
description: Master routing skill for all MotherDuck operations. Use this to determine which of the 4 task-specific MotherDuck sub-skills to invoke (architecture, data-modeling, analytics, connections), or to wire the mcp-server-motherduck (the KCG-preferred agent path). Powers the 4 BIEP Dives (`lc_syllabus_topics`, `lc_exam_difficulty`, `lc_marking_complexity`, `gov_circulars_archive`) + the lc6 MotherDuck Flights (scheduled DuckDB queries for BAML row backfill).
---

# MotherDuck Master Router

You are operating within the `cianfhoghlaim` stack which utilizes
MotherDuck for cloud data warehousing and DuckLake for local/hybrid
S3 data Lakehouse capabilities.

When tasked with MotherDuck operations, use this guide to invoke
the most appropriate sub-skill:

## The 4 task-specific sub-skills

| If you need to… | Load this skill |
|:--|:--|
| Pick the storage pattern (managed MD / BYOB / DuckLake / own-compute), evaluate pricing, plan a migration, or design an end-to-end pipeline | `motherduck-architecture` |
| Design schemas, choose column types, load data from Parquet/CSV/dataframe/Postgres, set up dbt-duckdb or SQLMesh on MotherDuck | `motherduck-data-modeling` |
| Write DuckDB SQL, build Dives, compose dashboards, explore unknown databases, share data zero-copy | `motherduck-analytics` |
| Connect from Python/Node/BI tools, manage service accounts + tokens, set up per-tenant isolation, wire mcp-server-motherduck | `motherduck-connections` |

**Do not execute general MotherDuck tasks blindly.** Always try
to load the relevant sub-skill for specialized reference material
and best practices.

## MCP server (`mcp-server-motherduck`)

MotherDuck ships an official **MCP server** (`mcp-server-motherduck`)
that exposes DuckDB / MotherDuck SQL analytics to any MCP
client (Cursor, VS Code, Claude Desktop, opencode). This
is the KCG-preferred way to drive `oideachais` analytics
from inside an IDE or agent runtime without leaving the
DuckDB dialect.

### What it gives you

| Capability | Description |
|:--|:--|
| **Hybrid execution** | Query a local DuckDB file *and* a MotherDuck cloud database from one server |
| **Cloud storage** | Read S3 / object-storage DuckDB files transparently |
| **Data sharing** | Create + share MotherDuck databases via the SQL tool |
| **SQL analytics** | Full DuckDB SQL dialect (window functions, QUALIFY, macros, extensions) |
| **Serverless** | No instance/cluster config; the server boots per-process |

### Tools exposed

- **`query` (the only tool)**: execute a SQL string. All
  interaction with DuckDB + MotherDuck goes through SQL.
  Results are auto-truncated to **`--max-rows 1024`**
  (default) and **`--max-chars 50000`** (default) so a
  single SELECT cannot blow out the agent's context.

- **`duckdb-motherduck-initial-prompt`**: the one
  `prompt` the server provides, used to initialise the
  connection in a chat client.

### CLI flags you'll actually use

| Flag | Default | When to override |
|:--|:--|:--|
| `--db-path` | `md:` | Use `/path/to/local.duckdb` for local-only; `md:cianfhoghlaim` for the read-only KCG lakehouse (post-v7 canonical); `s3://bucket/path.duckdb` for object-storage |
| `--motherduck-token` | `$motherduck_token` env | Required for any `md:` access |
| `--read-only` | `false` | **Always set true** for the KCG read-only consumer pattern |
| `--saas-mode` | `false` | Enable in production for security: disables filesystem + write perms for local DuckDB |
| `--max-rows` | 1024 | Lower to 256 for chat contexts; raise to 4096 for marimo notebooks |
| `--max-chars` | 50000 | Raise to 200000 for marimo notebooks; lower to 5000 for narrow chat contexts |
| `--query-timeout` | -1 (off) | Set 300 (5 min) for production to prevent runaway scans |
| `--transport` | `stdio` | Use `stream` (HTTP streaming) for web clients; `sse` for legacy clients |
| `--port` / `--host` | 8000 / 127.0.0.1 | Required for `sse` and `stream` transports |

### Install + run

```bash
# Install (one-time, via uvx)
uvx mcp-server-motherduck --help

# Local DuckDB file (read-only)
uvx mcp-server-motherduck \
  --db-path /Users/cianmacandeisigh/dev/kings_college_galway/stedding/cianfhoghlaim.duckdb \
  --read-only

# MotherDuck cloud (KCG read-only consumer)
uvx mcp-server-motherduck \
  --db-path md:cianfhoghlaim \
  --motherduck-token "$MOTHERDUCK_TOKEN" \
  --read-only --saas-mode

# Production: streaming HTTP + timeout
uvx mcp-server-motherduck \
  --transport stream \
  --db-path md:cianfhoghlaim \
  --motherduck-token "$MOTHERDUCK_TOKEN" \
  --saas-mode \
  --max-rows 4096 --max-chars 200000 \
  --query-timeout 300
```

### Wire into Cursor / VS Code / Claude Desktop

**Cursor** (`~/.cursor/mcp.json` or per-project
`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "mcp-server-motherduck": {
      "command": "uvx",
      "args": [
        "mcp-server-motherduck",
        "--db-path", "md:cianfhoghlaim",
        "--motherduck-token", "<YOUR_MOTHERDUCK_TOKEN_HERE>",
        "--read-only", "--saas-mode"
      ]
    }
  }
}
```

**VS Code** (`.vscode/mcp.json` or user `mcp.json`):
use the `inputs: [{type: promptString, id: motherduck_token, password: true}]`
pattern so the token is prompted once and stored in
the secret store, then referenced as
`"${input:motherduck_token}"`.

**Claude Desktop** (`claude_desktop_config.json`): same
`mcpServers` shape as Cursor.

### KCG production rules

- **Always `--read-only --saas-mode`** for the
  `oideachais` consumer pattern. The agent must not be
  able to `CREATE TABLE`, `INSERT`, or write to local
  disk.
- **Always set `--query-timeout 300`** (or lower) in
  production. MotherDuck's serverless compute will not
  kill a runaway scan for you; the agent could issue
  a cross-database join that scans 50M rows.
- **Always use `--max-rows 256` for chat contexts**;
  raise only for marimo / notebook agents that
  explicitly need large result sets.
- **Never put the MotherDuck token in `.env` plain**;
  it should come from the Infisical `dev-baile` vault
  via `mise` (the `MOTHERDUCK_TOKEN` env var) and
  never be written to disk in plaintext.

### Pair this skill with

- `motherduck-connect` — for the native-DuckDB vs
  Postgres-endpoint decision tree
- `motherduck-duckdb-sql` — for the full DuckDB SQL
  dialect reference (the MCP tool will only execute
  valid DuckDB SQL)
- `motherduck-security-governance` — for the
  service-account + read-only token policy
- `.agents/skills/motherduck/` + `.agents/skills/iceberg-lakekeeper/SKILL.md` —
  for the DuckLake / MotherDuck / Lakekeeper read-only mental model

See [`docs/teanga/motherduck_mcp.md`](../../../docs/teanga/motherduck_mcp.md)
for the full 457-line reference including all transport
modes, the SaaS-mode security model, and the
data-sharing semantics.

## 2026-06 updates (from the `upstream-package-monitoring` openspec change)

- **DuckLake 1.0** launched 2026-04-16 on MotherDuck. The KCG
  production lakehouse (`cianfhoghlaim/`) uses DuckLake 1.0. New
  features in 1.0:
  - **Data inlining** — also applies to updates and deletes (not
    just inserts), so small DuckLake tables can live entirely on the
    catalog.
  - **Data clustering** — 10× faster reads on clustered tables via
    the new `set_sorted_by` helper in
    `dlt/dlt_utils/ducklake_options.py`.
  - **Bucket partitioning** — new `set_bucket_partition` helper for
    multi-tenant workloads where row counts vary by 10× across
    partitions.
  - **Geometry + variant types** — DuckLake 1.0 adds first-class
    support for the `GEOMETRY` and `VARIANT` types, useful for the
    geospatial assets in
    `orchestration/defs/2_materials/geospatial_assets.py`.
- **3 hosting options** — fully managed (MotherDuck SaaS, default
  for KCG dev), BYOB (your own Garage S3 bucket, default for KCG
  production per `dlt/dlt_utils/motherduck_options.py:byob_destination`),
  and BYOC (your own compute + your own bucket — for regulated
  workloads).
- **MotherDuck upstream monitor** — `motherduck_blog.yml` in
  `infrastructure/firecrawl/monitors/upstream_packages/` is the
  Firecrawl monitor that detects DuckLake / BYOB / Cortex Code
  releases via the LLM-judge `--goal` filter. See the
  `change-detection` skill (Layer 4) for the architecture.

## Verified 2026-06-29 — Dives MCP tool list (8 tools, was 7)

| Tool | Description | Parameters |
|:--|:--|:--|
| `list_dives` | List all Dives in the workspace (returns `current_version` per Dive) | SELECT * |
| `read_dive` | Read a single Dive; supports `version` param | `id`, `version`? |
| `read_dive_version` | Read a specific historical version of a Dive (read-only) | `id`, `version` |
| `save_dive` | Persist a Dive to the workspace (creates version 1) | spec JSON |
| `update_dive` | Update an existing Dive (creates a new version) | `id` + spec JSON |
| `delete_dive` | Delete a Dive | `id` |
| `view_dive` | Open a Dive in the UI | `id` |
| `share_dive_data` | Create org-scoped shares for a Dive's data | `id` |

Source: `/docs/key-tasks/ai-and-motherduck/dives/` and `/sql-reference/mcp/`.

## MotherDuck token — Business-tier required (carry forward)

KCG notebooks use 4 shared databases (`cianfhoghlaim_public`, `cianfhoghlaim_team`, `leabharlann_public`, `leabharlann_team`). Lite is 3 users, 2 service accounts, 10 GB — too small. The token must be a **Business-tier** PAT.

## British-Isles Education pipeline — Canonical KCG pattern (post-v4)

The post-v4 lc6 pipeline (`openspec/changes/lc6-biep/`) consumes
the BAML-extracted DuckLake tables via **4 MotherDuck Dives**
(the read-only consumer surface) and **6 MotherDuck Flights**
(the scheduled backfill surface). All 10 are wired into the
`oideachais` MotherDuck database under the
`cianfhoghlaim.leaving_cert.*` and `cianfhoghlaim.education.ie.*`
schemas.

**The 4 Dives (read-only dashboards):**

1. `lc_syllabus_topics` — module / topic coverage per LC subject,
   partitioned by `language` (en/ga) and `level` (higher/ordinary)
2. `lc_exam_difficulty` — per-topic difficulty score derived from
   BAML `ExtractExamPaperLayout` over the last 10 years of SEC
   past papers
3. `lc_marking_complexity` — annotation density per topic from
   BAML `ExtractMarkingSchemeGuideline`
4. `gov_circulars_archive` — every `gov.ie/.../circulars/...` PDF
   extracted by the `government_circulars` v1 CocoIndex App

```python
from motherduck.dives import save_dive

save_dive(
    name="lc_syllabus_topics",
    sql="""
        SELECT
            subject,
            level || '_' || language AS partition,
            module_id,
            title,
            hours,
            cardinality(learning_outcomes) AS n_outcomes
        FROM cianfhoghlaim.leaving_cert.curriculum_syllabus
        WHERE subject IN (
            'mathematics', 'chemistry', 'geography',
            'gaeilge', 'english', 'computer_science'
        )
    """,
)
```

**The 6 Flights (scheduled backfills):**

- `flight_lc_mathematics_backfill` — re-extracts the BAML
  rows for Mathematics from `cianfhoghlaim.leaving_cert.mathematics_*`
  on the 1st of every month
- `flight_lc_chemistry_backfill`, `flight_lc_geography_backfill`,
  `flight_lc_gaeilge_backfill`, `flight_lc_english_backfill`,
  `flight_lc_computer_science_backfill` — same template,
  per-subject
- `flight_gov_circulars_backfill` — runs daily at 02:00 UTC to
  ingest new `gov.ie` circulars

**British-Isles Education pipeline use case:**

- **6 LC subjects × 2 languages × 2 levels** — Mathematics,
  Chemistry, Geography, Gaeilge, English, Computer Science, each
  partitioned by `en`/`ga` and `higher`/`ordinary` (24 partitions
  per BAML extraction stage).
- **`gov.ie` circulars** — the 7th subject (the
  `government_circulars` partition) ingests circulars from
  `gov.ie/.../circulars/...` for cross-referencing with NCCA
  syllabus changes.
- **Cross-Dive joins** — the marimo notebooks use
  `duckdb.connect("md:cianfhoghlaim")` to join across all 4 Dives
  for end-to-end analytics.

Cross-references:
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — the DuckLake
  tables the Dives consume
- [`.agents/skills/cocoindex/SKILL.md`](../cocoindex/SKILL.md) —
  the 7 v1 Apps that populate the LanceDB companion tables
- [`.agents/skills/marimo/SKILL.md`](../marimo/SKILL.md) — the 6
  per-subject marimo notebooks that read the Dives
- [`.agents/skills/dagster/SKILL.md`](../dagster/SKILL.md) —
  the 42 lc5/lc6 assets that drive the Flights
- [`.agents/skills/ducklake/SKILL.md`](../ducklake/SKILL.md) —
  the DuckLake sink layer

## v7 flattening migration notes (added 2026-07-19)

Per openspec/changes/2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1:

- The canonical MotherDuck database alias is `md:cianfhoghlaim` (NOT `md:cianfhoghlaim`
  which was the pre-v7 name). The pre-v7 BIEP Dives that referenced `md:cianfhoghlaim`
  were migrated to `md:cianfhoghlaim` in the P1 lakehouse-population change.
- MotherDuck Flights are now configured via
  `openspec/changes/2026-08-02-biep-v3-motherduck-flights-v1/` (the canonical
  per-day BIEP Flights `lc_pdf_sync_flight` etc.)
- For BIEP analytics, the 4 canonical Dives are:
  - `lc_syllabus_topics`
  - `lc_exam_paper_difficulty`
  - `lc_marking_complexity`
  - `gov_circulars_archive`

