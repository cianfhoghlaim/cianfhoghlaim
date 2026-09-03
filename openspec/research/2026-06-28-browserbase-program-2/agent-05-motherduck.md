# Agent 05 — MotherDuck (managed DuckDB)

**Wave:** 1 (Phase 2 — BrowserBase Program 2)
**Date:** 2026-06-28
**Budget used:** ~30 BrowserBase credits (Firecrawl primary; BrowserBase for the live nav + extract loop)
**Sources:** motherduck.com/docs/*, motherduck.com/pricing, GitHub `motherduckdb/mcp-server-motherduck`, codebase CCC

## TL;DR

MotherDuck's "managed DuckDB" surface is now **two parallel stacks**, both heavily used in Cianfhoghlaim:

1. **`mcp-server-motherduck`** — the open-source **local** MCP server (stdin, `uvx mcp-server-motherduck`). This is what `opencode.json` registers and what `agent-observability/references/mcp/MCP_SERVERS.md` documents. The Phase 0.3 runbook confirms it ships as the KCG-preferred agent path.
2. **Remote MCP at `https://api.motherduck.com/mcp`** — fully-managed, OAuth, 25 tools, used by Claude Desktop / ChatGPT / Cursor / Claude Code / Copilot Studio. Multi-region (4 AWS regions), request-routed.

Both stacks use the same `md:` SQL prefix for ATTACH. The four regions (`us-east-1`, `us-west-2`, `eu-central-1`, `eu-west-1`) — **Ireland region `eu-west-1` (Dublin) is the natural KCG primary**, but the codebase org is not declared in the docs we scraped.

**Pricing drift**: P1A-05 said "MOTHERDUCK 0.5". Current production is **DuckDB 1.5.4** (us-east-1 also accepts 1.4.0+). Compute instances: Pulse $0.60/hr (only instance on Lite), Standard $2.40, Jumbo $4.80, Mega $12, Giga $36. Storage $0.04/GB/mo. AI Units $1/each. **Lite = $0** (3 users, 2 service accounts, 10 GB, 10 Pulse-hrs/mo). **Business = $250/org/mo + usage** (10 users, unlimited SAs, Flights, 90d snapshots, 99.9% SLA). Enterprise = custom (PrivateLink, HIPAA BAA, SSO).

**Dives are the showpiece feature** — created via the MCP server (not raw SQL), live React components, versioned history, shareable via URL with state encoding. `REQUIRED_DATABASES` constant in Dive React code triggers automatic `ATTACH` of share-backed databases.

## Code (KCG-side)

| Path | Purpose |
|:--|:--|
| `cianfhoghlaim/core/dlt/_oideachais_dlt_utils/motherduck_options.py` | **Canonical** 3-mode factory: `managed` / `byob` / `byoc` (DuckLake 1.0 hosting options) |
| `spaces/data-engineering/package_analytics/kcg_data_layer/motherduck_destination.py` | Spaces-aligned MotherDuck destination w/ local DuckDB fallback |
| `infrastructure/stacks/motherduck/{blueprint.yaml,README.md,secrets.env}` | Stack stub for the MotherDuck cloud service (not a real container) |
| `infrastructure/stacks/motherduck/blueprint.yaml:62` | `destination=dlt.destinations.motherduck(...)` reference |
| `infrastructure/firecrawl/monitors/upstream_packages/motherduck_blog.yml` | **4-target Firecrawl monitor** (blog / docs / changelog / engineering blog) → n8n webhook → Dagster |
| `cianfhoghlaim/assets/_croilar_assets/dlt_assets.py:267-321` | `motherduck_sync` Dagster asset — copies DuckDB tables to MotherDuck (Dive embedding) |
| `openspec/research/.../phase-1a/P1A-05-motherduck.md` | Phase 1A research (slightly stale on pricing/version) |
| `openspec/research/.../phase-2/P2-29-motherduck-recheck.md` | Phase 2 recheck (drift not yet measured) |
| `.agents/skills/motherduck/SKILL.md` + 4 sub-skills (`motherduck-architecture`, `motherduck-data-modeling`, `motherduck-analytics`, `motherduck-connections`) | Canonical skill router |
| `.agents/skills/motherduck/references/motherduck-mcp-server.md` | 320 lines of `mcp-server-motherduck` config examples for Claude Desktop, Cursor, VS Code, Zed, Windsurf, Claude Code, Goose, Copilot Studio, SSE stdio |
| `.agents/skills/agent-observability/references/mcp/MCP_SERVERS.md:106-108` | The exact `opencode.json` MCP entry: `["uvx", "mcp-server-motherduck", "--db-path", ":memory:", "--read-write", "--allow-switch-databases"]` |
| `.infisical.env:240` | `MOTHERDUCK_TOKEN=infisical://dev-baile/motherduck/token` |
| `.env.enc:18` | Encrypted MOTHERDUCK_TOKEN (Locket-injected at runtime) |
| `pyproject.toml:24` | `dlt[motherduck]` extra in cianfhoghlaim |

**Canonical ATTACH pattern** (`motherduck_options.py:89-93`):

```python
credentials = DuckLakeCredentials(
    ducklake_name=database,                # e.g. "oideachais"
    catalog=f"motherduck:?motherduck_token={token}",
    storage=storage_config,                # S3 URL + creds + region
)
return dlt.destinations.ducklake(credentials=credentials)
```

**Canonical croilar sync asset** (`dlt_assets.py:267-321`):

```python
@asset(name="motherduck_sync", group_name="cross_link", compute_kind="motherduck")
def motherduck_sync_asset(context: AssetExecutionContext) -> MaterializeResult:
    """Copy all DuckDB tables to MotherDuck cloud for Dive embedding."""
    local = duckdb.connect("./data/croilar.duckdb", read_only=True)
    md    = duckdb.connect(f"md:?motherduck_token={os.environ['MOTHERDUCK_TOKEN']}")
    for schema, table in [("spotify_data","tracks"), ("github_data","repos"), ...]:
        md.execute(f"CREATE OR REPLACE TABLE {schema}.{table} AS SELECT * FROM local.{full_name}")
```

**Upstream monitor** (`infrastructure/firecrawl/monitors/upstream_packages/motherduck_blog.yml`):

```yaml
name: "motherduck_blog"
schedule: { text: "every 30 minutes", timezone: "UTC" }
targets:
  - type: scrape
    urls:
      - "https://motherduck.com/blog/"
      - "https://motherduck.com/docs/"          # <-- changelog at /changelog 404'd in scrape (Next.js 404 page)
      - "https://motherduck.com/changelog/"     # <-- this one too — but is in the canonical monitor
      - "https://motherduck.com/blog/category/engineering/"
goal: |  # Firecrawl LLM-judge
  Alert on product/architecture changes — DuckLake releases, hosting
  options (managed/BYOB/BYOC), new SQL syntax, Cortex Code updates.
notification.webhook:
  url: "https://n8n.cianfhoghlaim.ie/webhook/upstream-blog"
  headers: { X-Package: "motherduck" }
retentionDays: 90
```

**Where MCP motherduck config actually lives** (`.agents/skills/agent-observability/references/mcp/MCP_SERVERS.md:106-108`):

```json
"motherduck": {
  "command": ["uvx", "mcp-server-motherduck",
              "--db-path", ":memory:",
              "--read-write",
              "--allow-switch-databases"]
}
```

This is the entry referenced by the Phase 1A spec (`P1A-05-motherduck.md:87`). P1A's `MCP_MOTHERDUCK_COMMAND` env var is a verbatim mirror.

## Env (deployed configuration)

| Env var | Value | Source | Notes |
|:--|:--|:--|:--|
| `MOTHERDUCK_TOKEN` | `infisical://dev-baile/motherduck/token` | `.infisical.env:240` → Infisical `dev-baile` → Locket sidecar | Cloud service token |
| `MOTHERDUCK_MODE` | `byob` (default) / `managed` / `byoc` | env var | Set by `motherduck_options._resolve_mode()` |
| `MOTHERDUCK_DATABASE` | `oideachais` (default) | env var | DB name in MotherDuck org |
| `MOTHERDUCK_S3_BUCKET` | `ducklake` | env var | BYOB / BYOC storage |
| `MOTHERDUCK_S3_ENDPOINT` | `http://localhost:3900` (Garage local) | env var | Switch to `https://garage.bunchloch.cianfhoghlaim.ie` in prod |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Infisical dev-baile | env var | S3 creds for Garage |
| `MCP_MOTHERDUCK_COMMAND` | `uvx mcp-server-motherduck --db-path :memory: --read-write --allow-switch-databases` | opencode.json | **MCP stdio launch** |
| `MOTHERDUCK_ORG` | `cianfhoghlaim` | MotherDuck dashboard | Org name (region not declared in scrape) |
| `DUCKDB_DATABASE` | `md:oideachais?motherduck_token=$MOTHERDUCK_TOKEN` | `openspec/changes/celtic-data-engineering-patterns/specs/celtic-data-engineering-pipeline/spec.md:26` | Marimo binding |

**DuckDB client compatibility** (Python install page, scraped 2026-06-28):

| Region | DuckDB versions accepted |
|:--|:--|
| us-east-1 | 1.4.0 – 1.5.4 |
| us-west-2 | 1.4.1 – 1.5.4 |
| eu-central-1 | 1.4.1 – 1.5.4 |
| eu-west-1 | 1.4.1 – 1.5.4 |

KCG spec mandates `duckdb==1.5.4`. **OK in all 4 regions.**

## CCC anchors (where this code lives)

```
MotherDuck option factory:    cianfhoghlaim/core/dlt/_oideachais_dlt_utils/motherduck_options.py:1-158
MotherDuck Spaces dest:       spaces/data-engineering/package_analytics/kcg_data_layer/motherduck_destination.py:23-44
croilar motherduck_sync:      cianfhoghlaim/assets/_croilar_assets/dlt_assets.py:267-321
Stack stub:                   infrastructure/stacks/motherduck/{blueprint.yaml,README.md,secrets.env}
Upstream monitor:             infrastructure/firecrawl/monitors/upstream_packages/motherduck_blog.yml:1-63
MCP config reference:         .agents/skills/agent-observability/references/mcp/MCP_SERVERS.md:106-108
Infisical reference:         .infisical.env:240
dlt extra:                    cianfhoghlaim/pyproject.toml:24
marimo → md:oideachais:       cianfhoghlaim/notebooks/_oideachais/exam_papers_explorer.py:167-168, 262-263
                             cianfhoghlaim/notebooks/_oideachais/marking_scheme_analyzer.py:130-131
                             cianfhoghlaim/notebooks/_oideachais/syllabus_visualizer.py:100
syllabus dive button:         cianfhoghlaim/notebooks/_oideachais/syllabus_visualizer.py:249-260
Author-archive multi-target:  cianfhoghlaim/docs/legacy/crypteolas/dagster_assets/components/rest_pipeline_component.yaml:297
Stack blueprint ref:          infrastructure/stacks/motherduck/blueprint.yaml:62
Drift recheck (pending):      openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-29-motherduck-recheck.md
```

CCC semantic search terms to use next time:

```
"MOTHERDUCK_TOKEN"             → 13 references across monorepo
"motherduck_options"           → the canonical factory
"md:?motherduck_token="        → 4 notebook attach sites
"destination=motherduck"       → 6 dlt pipeline destinations
"motherduck_sync"              → 1 Dagster asset (croilar)
"CREATE SHARE"                 → none in codebase yet (canonical docs only)
"REQUIRED_DATABASES"           → not yet adopted (Dive manifest pattern)
"mcp-server-motherduck"        → referenced in 6 skill files
```

## Drift log

| Date | Event | Source / Action |
|:--|:--|:--|
| 2025-12-16 | MotherDuck / DuckDB / DuckLake / dlt 4-way integration blog | `infrastructure/stacks/lakehouse/examples/DuckLake to MotherDuck_ Validate locally, deploy to cloud in minutes.md:1-198` |
| 2026-01 | Initial MotherDuck MCP server (cross-host queries) | P1A-05 |
| 2026-02 | Switched `motherduck-duckdb-driver` → `mcp-server-motherduck` | P1A-05 (drift log) |
| 2026-04 | DuckLake 1.0 launched on MotherDuck → 3 hosting options (managed / BYOB / BYOC) | `motherduck_options.py:1-29` docstring |
| 2026-04 | Created 4 shares (`oideachais_public`, `oideachais_team`, `leabharlann_public`, `leabharlann_team`) | P1A-05 |
| 2026-04-13 | DuckLake 1.0 — data inlining (default `data_inlining_row_limit=100`), `SORTED BY`, `PARTITIONED BY (bucket(1000, id))`, `GEOMETRY`, `VARIANT` | `cianfhoghlaim/core/dlt/_oideachais_dlt_utils/ducklake_options.py:1-26` |
| 2026-05 | Upgraded to MotherDuck 0.5 | P1A-05 (drift log) — but **current DuckDB client is 1.5.4** |
| 2026-05 | MotherDuck's **Dives feature** replaced bespoke marimo dashboards | P1A-05 (drift log) |
| 2026-06-26 | docs site restructure: `/docs/dives` → `/docs/key-tasks/ai-and-motherduck/dives/`; `/docs/connect/python` → `/docs/getting-started/interfaces/client-apis/python/installation-authentication/`; `/docs/key-concepts/sharing` → `/docs/key-tasks/sharing-data/sharing-overview` | Direct scrape on 2026-06-28 — **404'd on old URLs** |
| 2026-06-27 | `motherduck.com/changelog` returns Next.js 404 (page moved) | Firecrawl scrape on 2026-06-28 — needs recheck |
| 2026-06-28 | MCP Server split into **Remote** (`https://api.motherduck.com/mcp`, OAuth, read-write) and **Local** (`mcp-server-motherduck` on GitHub, customizable) | https://motherduck.com/docs/sql-reference/mcp/ |
| 2026-06-28 | Pricing page re-confirms Lite/Business/Enterprise + 5 instance tiers (Pulse→Giga) + 99.9% SLA on Business | https://motherduck.com/pricing |
| 2026-06-28 | v4 consolidation: `sruth/oideachais/dlt_utils/motherduck_init.py` → `cianfhoghlaim/core/dlt/_oideachais_dlt_utils/motherduck_options.py` (rename only) | P1A-05 (drift log) |
| 2026-06-28 | Found P1A spec drift: says `--read-write` is OK in dev only, but real `opencode.json` per `MCP_SERVERS.md:106-108` does use `--read-write --allow-switch-databases` | This audit |

## Anti-patterns (don't do this)

1. **Don't hardcode `motherduck_token` in connection strings** like `duckdb.connect("md:?motherduck_token=abc...")`. Use `os.environ["MOTHERDUCK_TOKEN"]` and let Locket inject. **The 4 marimo notebooks all violate this pattern** (`exam_papers_explorer.py:167-168` etc.) — they interpolate `os.environ` into the URL string, which logs the token.
2. **Don't run MotherDuck with `--read-write` in production MCP configs.** The `opencode.json` MCP entry uses `--read-write --allow-switch-databases` for dev convenience. Production should be `--read-only` with a read-scaling token (per `motherduck-create-customer-facing-analytics` skill guidance).
3. **Don't create shares with `ACCESS UNRESTRICTED`** unless you genuinely want any MotherDuck user in your region to attach. Default is `ACCESS ORGANIZATION` (only your org's users).
4. **Don't `CREATE OR REPLACE SHARE`** carelessly — the share URL changes, and clients must re-attach within minutes (CREATE SHARE docs).
5. **Don't bypass Dives for production dashboards.** Dives provide versioning + `REQUIRED_DATABASES` auto-attach + shareable state via URL. Raw SQL queries don't.
6. **Don't use MotherDuck for the actual data writes.** DuckLake writes go through DuckDB (local) → Garage S3 (or MotherDuck-managed storage in BYOB). MotherDuck is the **compute** layer; data sovereignty in BYOB mode means the Parquet files stay in your S3 bucket.
7. **Don't alias shares differently from the source DB name** if the database contains views with fully-qualified references (`my_db.main.my_table`). Use `ATTACH 'md:_share/.../id' AS my_db` to preserve view resolution.
8. **Don't use `database_name` starting with a number** for direct connect — it requires quoted `USE DATABASE` workaround.
9. **Don't attach shares with a read-scaling token** — share attachment needs read-write first, then read-scaling tokens can query.
10. **Don't bypass Dives' `REQUIRED_DATABASES`** in custom React components — call `ATTACH` from inside `useSQLQuery` and viewers without the right DB see "Catalog does not exist" errors. Export the constant instead.

## Decision matrix (Phase 2 conclusion)

| Decision | Choice | Rationale |
|:--|:--|:--|
| MCP server (agent path) | Local `mcp-server-motherduck` (KCG-canonical, stdio) | Open-source, full DuckDB SQL, no MotherDuck-side state. The Phase 0.3 runbook says this is canonical. |
| MCP server (Claude Desktop / Cloud IDEs) | Remote `https://api.motherduck.com/mcp` (OAuth) | Zero setup; OAuth flow is now first-class. 25 tools. |
| Auth method | Access token via `MOTHERDUCK_TOKEN` env var (Locket-injected) | Recommended best-practice on docs page (line 1,054: *"This is the best practice for security reasons"*). |
| DuckDB client version | `duckdb==1.5.4` (all 4 regions accept) | Current MotherDuck-recommended version. |
| DuckLake hosting mode | **BYOB** (default `MOTHERDUCK_MODE=byob`) | Data sovereignty in Garage S3; MotherDuck handles catalog + compute. P1A calls this the "sweet spot". |
| Storage backend | Garage S3 (`MOTHERDUCK_S3_ENDPOINT=http://localhost:3900`) | The KCG-managed S3-compatible lakehouse. |
| Sharing policy | `ACCESS ORGANIZATION` + `VISIBILITY DISCOVERABLE` + `UPDATE AUTOMATIC` for shared `lakehouse.oideachais` | Default for org-internal data shares. |
| Pricing plan | **Business** ($250/org/mo + usage) | 10 users, unlimited service accounts, Flights (scheduled Python on MotherDuck compute), 99.9% SLA. Lite is too small (3 users, Pulse only). |
| Compute tier (default) | **Standard** ($2.40/hr, by-second) | "Built to handle common data warehouse workloads, including loads and transforms" — matches DLT ingest jobs. |
| Database alias for shares | Match source DB name (e.g. `lakehouse`) | Preserves view references in shared DBs. |
| Share refresh | `REFRESH DATABASE <name>` after producer runs `UPDATE SHARE` | Manual refresh needed for sub-minute freshness. |
| Dive required DBs pattern | Export `REQUIRED_DATABASES` from React component | Auto-attaches shares before queries fire. |
| DLT destination | `dlt.destinations.ducklake(credentials=DuckLakeCredentials(catalog="motherduck:?token=...", storage=s3_config))` | The dlt 1.24 + MotherDuck + BYOB canonical pattern. |
| Local dev fallback | `dlt.destinations.duckdb(credentials={"database": "./kcg_pypi.duckdb"})` | Spaces pattern: `motherduck_destination.py:42-44`. |
| Org region | **`eu-west-1` (Dublin)** — not yet declared | Irish data sovereignty. MotherDuck supports it. |
| MCP stdio flags | `--db-path :memory: --read-write --allow-switch-databases` (dev only) | From `MCP_SERVERS.md:108`. Production = `--read-only --saas-mode`. |

## Anti-pattern priority for Phase 3 (synthesis)

When cross-correlating with Phase 1B and 2 agents, look for:

- **Agent 02 (LanceDB)** — confirm `REQUIRED_DATABASES` pattern is implemented in croilar's Dive React components (not just docs).
- **Agent 04 (Garage S3)** — verify `MOTHERDUCK_S3_ENDPOINT` resolves to the Garage stack at `arm1-oci` in prod, not `localhost:3900`.
- **Agent 06 (Infisical)** — confirm the `dev-baile/motherduck/token` vault entry exists and the token is a Business-tier (not Lite) token.
- **Agent 09 (Dagster)** — `motherduck_sync_asset` in `_croilar_assets/dlt_assets.py` lacks an upstream sensor; if croilar DuckDB drifts, MotherDuck dives show stale data silently.
- **Agent 11 (Pangolin)** — confirm `motherduck.cianfhoghlaim.ie` (or equivalent subdomain) is wired through Pangolin for web-UI access.
- **Agent 17 (DuckLake)** — `ducklake_options.py` references DuckLake 1.0 features (GEOMETRY, VARIANT, SORTED BY); confirm `motherduck_options.py` passes these through to the MotherDuck `DuckLakeCredentials` constructor.
- **Agent 23 (MCP / Cognee)** — MCP token rotation: the remote MCP server uses OAuth, the local uses `MOTHERDUCK_TOKEN`. Doc rotation playbook.

## §8 Refactor opportunities (specific to MotherDuck in KCG)

These are concrete refactors the build agent should consider, ordered by impact:

1. **Move the 4 marimo notebooks off the inline-token pattern** to a single shared helper.
   - Sites: `cianfhoghlaim/notebooks/_oideachais/{exam_papers_explorer.py:167-168,262-263, marking_scheme_analyzer.py:130-131, syllabus_visualizer.py:100}` all duplicate the `os.environ.get("MOTHERDUCK_TOKEN")` → `duckdb.connect(f"md:?motherduck_token={_token}")` pattern.
   - Refactor: import `from cianfhoghlaim.core.dlt._oideachais_dlt_utils.motherduck_options import get_motherduck_destination` (DLT) **or** create a thin `connect_motherduck()` helper that uses `SET motherduck_token = '...'` rather than URL interpolation (URL form logs the token in DuckDB query logs).
   - Files to create: `cianfhoghlaim/core/duckdb/connect_motherduck.py` (10 lines).
   - Risk: low. Reward: removes 4 token-leak surfaces, unifies config.

2. **Add `REQUIRED_DATABASES` to the croilar Dive React components**.
   - Sites: croilar Dive manifests (under `oideachais_mission_control/` or wherever the Dive specs live — *not currently in the audited files; cross-reference with Agent 09*).
   - Refactor: export `REQUIRED_DATABASES = [{type: "share", path: "md:_share/lakehouse/<uuid>", alias: "lakehouse"}]` from each Dive JSX module. Viewers without share access currently see "Catalog does not exist".
   - Risk: medium (Dive manifest format is opinionated). Reward: removes a class of viewer runtime errors.

3. **Promote the cross-link `motherduck_sync` asset into a template**.
   - Sites: only 1 in `dlt_assets.py:267-321`. Oideachais / tuatha quadrants each have their own DuckLake → MotherDuck sync that's duplicated.
   - Refactor: extract `motherduck_sync_asset()` into `cianfhoghlaim/assets/_common/cross_link/motherduck_sync.py` and parameterise on the source DuckDB path + table manifest.
   - Risk: low. Reward: 1 source of truth for sync semantics (e.g., `CREATE OR REPLACE` vs `INSERT`, retry behaviour).

4. **Tighten the MCP stdio flags for any non-dev host**.
   - The `opencode.json` MCP entry (per `MCP_SERVERS.md:108`) uses `--read-write --allow-switch-databases`. The Phase 1A spec's anti-pattern #3 says production must drop these. Audit whether any opencode install outside MacBook dev uses these flags.
   - Refactor: introduce an `MCP_MOTHERDUCK_FLAGS` env var that defaults to `--db-path :memory: --read-write --allow-switch-databases` on `bunchloch` (MacBook dev) and `--read-only --saas-mode` elsewhere. Or split into two MCP entries (`motherduck_dev`, `motherduck_prod`).
   - Risk: medium (production safety vs dev DX). Reward: closes the write-tunnel that an attacker with a stolen token could exploit.

5. **Wire the upstream monitor's `/changelog/` 404 into the goal text**.
   - The Firecrawl monitor's 4 URLs include `https://motherduck.com/changelog/` — this returns Next.js 404 as of 2026-06-28. The LLM judge treats the 404 page as "no change" so the monitor still fires silently on real changelog content (if the URL moves).
   - Refactor: update the monitor goal text to explicitly ignore 404 / Next.js "Page Not Found" markers, AND add the new canonical changelog URL once discovered (likely `/blog/category/engineering/` or a dedicated `/changelog` route).
   - Risk: low. Reward: prevents silent drift misses.

6. **Replace `MOTHERDUCK_DATABASE=oideachais` with the **org-scoped** name once we pick the region**.
   - Currently every notebook/dlt pipeline assumes the database is `oideachais`. Once the KCG MotherDuck org lands in `eu-west-1` (Dublin), database names are namespace-scoped to the org. Should align with the DuckLake `lakehouse` database (per `P1A-05:38`).
   - Refactor: introduce `MOTHERDUCK_DATABASE=lakehouse` as the new default, deprecate `oideachais` in 2026-Q3.
   - Risk: medium (breaks 4 marimo notebooks). Reward: one DB across all quadrants, cleaner share alias.

7. **Add a `motherduck_dive_explorer` skill** for navigating the Dive UI from inside opencode.
   - The Dives API (via MCP `list_dives`, `read_dive`, `save_dive`, `share_dive_data`) is exposed but the KCG skill catalogue has no dive-navigator. Phase 1A's `oideachais-marimo-dashboards` spec is the closest analog (marimo → Dives).
   - Refactor: create `.agents/skills/motherduck/motherduck-dives-explorer/SKILL.md` referencing the 7 Dive MCP tools (`list_dives`, `read_dive`, `save_dive`, `update_dive`, `delete_dive`, `view_dive`, `share_dive_data`).
   - Risk: low. Reward: agents can author + iterate Dives conversationally without leaving opencode.

8. **Document the OAuth vs token tradeoff** in the skill router.
   - Currently `motherduck-connections` SKILL.md lines 76-200 cover local MCP + token auth. The remote MCP server (OAuth) is now first-class per https://motherduck.com/docs/key-tasks/ai-and-motherduck/mcp-setup/ but the KCG skill doesn't fully document it.
   - Refactor: add a "Remote MCP (managed)" section to `motherduck-connections/SKILL.md` with the canonical config JSON (Cursor / Claude Code / VS Code / Copilot Studio / Windsurf / Zed).
   - Risk: low. Reward: enables the Cloud IDE path that the Phase 0.3 runbook anticipated.

## Cross-references for downstream agents

- Phase 1A research: [`openspec/research/2026-06-28-browserbase-credit-program/phase-1a/P1A-05-motherduck.md`](../../2026-06-28-browserbase-credit-program/phase-1a/P1A-05-motherduck.md)
- Drift recheck spec: [`openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-29-motherduck-recheck.md`](../../2026-06-28-browserbase-credit-program/phase-2/P2-29-motherduck-recheck.md)
- Canonical skill: [`.agents/skills/motherduck/SKILL.md`](../../../../.agents/skills/motherduck/SKILL.md)
- Upstream monitor: [`infrastructure/firecrawl/monitors/upstream_packages/motherduck_blog.yml`](../../../../infrastructure/firecrawl/monitors/upstream_packages/motherduck_blog.yml)
- OpenSpec spec: [`oideachais-pipeline/spec.md`](../../../../openspec/specs/oideachais-pipeline/spec.md) lines 141, 158, 1270 (the `md:oideachais` binding)
- OpenSpec change: [`refactor-dlt-dagster-2026-stack-align/proposal.md`](../../../../openspec/changes/refactor-dlt-dagster-2026-stack-align/proposal.md) lines 111-124 (origin of `motherduck_options.py`)
- KCG manifest: `openspec/project.md:56, 90` (the 16 sub-packages + 33 user-stacks)