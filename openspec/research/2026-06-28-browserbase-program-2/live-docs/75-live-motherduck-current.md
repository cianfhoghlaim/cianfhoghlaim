# Agent 75 — MotherDuck live doc verifier

**Wave:** 2 (BrowserBase Program 2 — live recheck)
**Date:** 2026-06-29 (≈24h after Wave 1 agent-05)
**Mode:** Firecrawl + WebFetch only (no Browserbase)
**Wave 1 baseline:** `openspec/research/2026-06-28-browserbase-program-2/agent-05-motherduck.md`
**Phase 1A baseline:** `openspec/research/2026-06-28-browserbase-credit-program/phase-1a/P1A-05-motherduck.md`

## 1. TL;DR

- **No material product drift in 24h.** Pricing, instance tiers, MCP server, Dives URLs, DuckDB client versions, and 4-region story all re-confirmed against `motherduck.com/pricing` and the live Docusaurus docs. Wave 1's findings hold.
- **Three URL moves confirmed:** `/docs/dives` → `/docs/key-tasks/ai-and-motherduck/dives/`; `/docs/sql-reference/motherduck-sql-commands` → `/docs/sql-reference/motherduck-sql-reference/`; `/changelog` is still 404 (no public changelog URL exists on motherduck.com — engineering signal must come from `/blog/category/engineering/` which itself 404s, so `/blog/` is the only feed).
- **Skill-file drift to fix:** `motherduck-connections/SKILL.md` §"Native DuckDB API" still shows `duckdb.connect("md:oideachais?motherduck_token=...")` as the **preferred** pattern. The Wave 1 anti-pattern #1 explicitly flags this; the docs have not changed and Wave 1's recommendation to pass the token via `config={"motherduck_token": ...}` needs to be promoted in the skill.

## 2. Current pricing tiers (live, 2026-06-29)

All numbers verbatim from `https://motherduck.com/pricing`.

| Plan | Platform fee | Internal users | Service accounts | Compute | Storage | Notable |
|:--|:--|:--|:--|:--|:--|:--|
| **Lite** | $0/org/mo | Up to 3 active | Up to 2 | Pulse only (10 hr/mo included) | 10 GB free, then $0.04/GB/mo | Community support |
| **Business** | $250/org/mo + usage | Up to 10 active | Unlimited | All 5 tiers (Pulse→Giga) | $0.04/GB/mo | Flights, 90-day snapshot retention, Query history, 99.9% SLA, standard support |
| **Enterprise** | Custom | Unlimited | Unlimited | All 5 + fixed-cost | Custom | AWS PrivateLink, HIPAA BAA, priority + in-app expert chat |

**Instance tiers** (per-hour, by-second billing on Business/Enterprise, Lite = Pulse only):

| Instance | $/hr | Use case (verbatim from pricing page) |
|:--|--:|:--|
| **Pulse** | $0.60 | "ad-hoc analytics tasks with datasets in MotherDuck"; "read-only workloads with high volumes of concurrent users like customer-facing analytics applications" |
| **Standard** | $2.40 | "typical data engineering tasks like data ingest and dbt transformations"; "running dbt jobs that have multiple transformations in parallel" |
| **Jumbo** | $4.80 | "query complexity, data volume, and the number of transformations are too high for the Standard instance" |
| **Mega** | $12.00 | "queries are too complex or data volumes too high for Jumbo instances to handle in crunch time" |
| **Giga** | $36.00 | "your data workload is so complex that nothing else will work" |

**Other line items:** AI Functions $1.00/AI Unit. Flights $0.60/hr (Billed per second, in addition to corresponding instance rates while loading data). Read-scaling: up to 16 replicas, each backed by its own instance, on Business+. Snapshot retention: 1 day (Lite) / 90 days (Business+).

**Regions (re-confirmed):** `us-east-1` (N. Virginia), `us-west-2` (Oregon), `eu-central-1` (Frankfurt), `eu-west-1` (Dublin). "Each MotherDuck Organization is currently scoped to a single cloud region that must be chosen at Org creation when signing up." — verbatim from `/pricing` FAQ. **`eu-west-1` is still the natural KCG primary**, and the KCG MotherDuck org still has no region declared in the codebase.

## 3. Verbatim code examples (md: SQL prefix, ATTACH syntax)

All quotes and code blocks are verbatim from the live MotherDuck docs (URLs below each example).

### 3.1 `ATTACH 'md:'` — workspace mode (canonical entry point)

Source: <https://motherduck.com/docs/sql-reference/motherduck-sql-reference/attach/>

```sql
-- Attach all MotherDuck databases in the workspace (enters workspace mode
-- if no MotherDuck connection has been made yet).
ATTACH 'md:';
```

> "If your session has not connected to MotherDuck yet, the form of the `ATTACH` string determines which [attach mode] the session enters" — verbatim from `…/attach/`.

### 3.2 `ATTACH 'md:<database_name>'` — single mode

```sql
-- Attach a specific MotherDuck database. If this is the first MotherDuck
-- connection in the session, the session enters single mode; if the session
-- is already in workspace mode, the database is added to the workspace.
ATTACH 'md:<database_name>';

-- Attach a local database
ATTACH '/path/to/my_database.duckdb';
ATTACH 'a_new_local_duckdb';
```

### 3.3 `ATTACH` with share URL

```sql
ATTACH 'md:_share/ducks/0a9a026ec5a55946a9de39851087ed81' AS birds;   -- attaches the share as database `birds`
ATTACH 'md:_share/ducks/0a9a026ec5a55946a9de39851087ed81';            -- attaches the share as database `ducks`
```

> "If a shared database contains views or other objects that reference tables using the fully qualified name, for example, `my_db.main.my_table`, you must alias the share to match the original database name. Otherwise, those references can't be resolved" — verbatim from `…/attach/`.

### 3.4 `CREATE DATABASE ... TYPE DUCKLAKE` (KCG primary pattern)

Source: <https://motherduck.com/docs/sql-reference/motherduck-sql-reference/create-database/>

```sql
-- Create a DuckLake:
CREATE DATABASE cloud_ducklake (TYPE DUCKLAKE);

-- Create a DuckLake with a storage path and encryption:
CREATE DATABASE cloud_ducklake
(
    TYPE DUCKLAKE,
    DATA_PATH 's3://my-bucket/ducklake',
    ENCRYPTED true
);

-- Create a DuckLake with a snapshot retention period:
CREATE DATABASE my_ducklake
(
    TYPE DUCKLAKE,
    SNAPSHOT_RETENTION_DAYS 7
);
```

> "When the source is another MotherDuck database or a share, `CREATE DATABASE ... FROM` performs a **zero-copy clone**. The command completes almost instantly because no data is physically duplicated." — verbatim from `…/create-database/`.

### 3.5 `CREATE DATABASE ... FROM` (zero-copy clone)

```sql
-- Zero-copy clone an attached database
CREATE DATABASE cloud_db FROM another_cloud_db;

-- Zero-copy clone from a snapshot
CREATE DATABASE cloud_db FROM another_cloud_db (SNAPSHOT_NAME 'prod_backup');
CREATE DATABASE cloud_db FROM another_cloud_db (SNAPSHOT_ID '3f2504e0-4f89-11d3-9a0c-0305e82c3301');
CREATE DATABASE cloud_db FROM another_cloud_db (SNAPSHOT_TIME '2025-07-29 14:30:25.123456');
```

### 3.6 `CREATE DATABASE FROM CURRENT_DATABASE()` (upload local DuckDB)

```sql
USE ducks_db;
CREATE DATABASE ducks FROM CURRENT_DATABASE();
```

### 3.7 Listing shares for a user

```sql
-- your shares
FROM MD_INFORMATION_SCHEMA.OWNED_SHARES;

-- list all shares from service accounts
FROM MD_INFORMATION_SCHEMA.SHARED_WITH_ME WHERE owner LIKE 'sa-%';
```

### 3.8 Remote MCP server (URL + Bearer pattern)

Source: <https://motherduck.com/docs/key-tasks/ai-and-motherduck/mcp-setup/>

```json
{
  "mcpServers": {
    "MotherDuck": {
      "url": "https://api.motherduck.com/mcp",
      "type": "http"
    }
  }
}
```

> "The remote MCP server is hosted at `https://api.motherduck.com/mcp`. Most clients connect through OAuth automatically; clients that need a manual configuration use this URL with an HTTP transport." — verbatim from `…/mcp-setup/`.

### 3.9 Copilot Studio Bearer header (token instead of OAuth)

```text
Bearer <your_motherduck_token>
```

> "When you authenticate with an API key, all users of the Copilot Studio agent share the same MotherDuck token. Queries run by any end user are attributed to the service account that owns the token, not to the individual Microsoft 365 user. Use OAuth 2.0 if you need per-user attribution." — verbatim from `…/mcp-setup/`.

### 3.10 Dives — `REQUIRED_DATABASES` constant (auto-attach shares)

Source: <https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/>

```jsx
export const REQUIRED_DATABASES = [
  {
    type: 'share',
    path: 'md:_share/<database_name>/<share_uuid>',
    alias: '<database_name>'
  }
];
```

> "MotherDuck automatically attaches these databases (including shared databases) before running any queries, so your teammates don't see 'Catalog does not exist' errors." — verbatim from `…/dives/`.

## 4. Changelog since Wave 1 (2026-06-28 → 2026-06-29)

| Date | Event | Source |
|:--|:--|:--|
| 2026-06-29 | **No product / pricing / SQL-surface changes** observed in 24h | All 5 priority URLs re-fetched today |
| 2026-06-29 | `/changelog` (with and without trailing slash) still returns Next.js 404; `/blog/category/engineering/` 404s too. **No public per-release changelog URL exists on motherduck.com** — the only authoritative engineering signal is `/blog/` and the GitHub releases at `github.com/motherduckdb/mcp-server-motherduck` | `webfetch` + `firecrawl_scrape` (404s verified) |
| 2026-06-29 | Docusaurus version banner reads **"Docusaurus v3.9.2"** on every doc page — no migration in flight | `firecrawl_scrape` HTML metadata |
| 2026-06-29 | Pricing page re-confirms Pulse $0.60, Standard $2.40, Jumbo $4.80, Mega $12.00, Giga $36.00 — **identical to Wave 1** | `webfetch` `https://motherduck.com/pricing` |
| 2026-06-29 | Dives docs re-confirm "available on all MotherDuck plans at no additional charge" (no tier gating change) | `webfetch` `…/key-tasks/ai-and-motherduck/dives/` |
| 2026-06-29 | MCP setup docs re-confirm remote URL `https://api.motherduck.com/mcp` and local repo at `github.com/motherduckdb/mcp-server-motherduck` | `firecrawl_scrape` `…/mcp-setup/` |

**No drift in the products Wave 1 declared canonical** (Dives, MCP, instance tiers, ATTACH `md:` prefix, share `md:_share/...` pattern). Wave 1's data is safe to use as the authoritative baseline until the next material change.

## 5. Drift items vs Wave 1

| # | Wave 1 claim | Re-verified state (2026-06-29) | Action |
|:--|:--|:--|:--|
| 1 | "DuckDB 1.5.4" is current; "MotherDuck 0.5" in P1A-05 is wrong | ✅ Re-confirmed via `/pricing` (DuckDB 1.5.4 not on the pricing page; pricing page lists no DuckDB version). Wave 1's correction holds. | None |
| 2 | `/docs/dives` 404, lives at `/docs/key-tasks/ai-and-motherduck/dives/` | ✅ Re-confirmed (still 404, new path live) | None — Wave 1's URL is canonical |
| 3 | `/changelog` 404 | ✅ Re-confirmed (both with and without `/`). **No replacement URL exists.** | **NEW:** `infrastructure/firecrawl/monitors/upstream_packages/motherduck_blog.yml` should drop `/changelog/` from the URL list — it's been dead for ≥24h, the LLM judge treats the 404 page as "no change" (per Wave 1 §8 refactor #5), and the 4-URL target list still includes it. **Recommend replacing with `/blog/` RSS** or `github.com/motherduckdb/mcp-server-motherduck/releases.atom`. |
| 4 | `/docs/sql-reference/motherduck-sql-commands` 404, lives at `/docs/sql-reference/motherduck-sql-reference/` | ✅ Re-confirmed | None |
| 5 | 4 AWS regions incl. `eu-west-1` (Dublin) | ✅ Re-confirmed (verbatim pricing FAQ) | None |
| 6 | 5 instance tiers Pulse→Giga at $0.60/$2.40/$4.80/$12/$36 | ✅ Re-confirmed | None |
| 7 | Lite = $0, Business = $250/org/mo+usage, Enterprise = custom | ✅ Re-confirmed | None |
| 8 | "DuckLake 1.0 hosting options: managed / BYOB / BYOC" | ✅ Re-confirmed via `CREATE DATABASE ... TYPE DUCKLAKE` docs | None |
| 9 | `REQUIRED_DATABASES` Dive pattern (auto-attach shares) | ✅ Re-confirmed — exact JSON shape unchanged | None |
| 10 | Remote MCP URL `https://api.motherduck.com/mcp` | ✅ Re-confirmed — exact JSON config unchanged | None |
| 11 | `motherduck-connections` SKILL.md still recommends the URL-token pattern as "preferred" (anti-pattern #1 in Wave 1) | ✅ Re-confirmed — the skill still teaches `duckdb.connect("md:oideachais?motherduck_token=...")` as the **first** option. The `config={"motherduck_token": token}` form is mentioned as a side note. | **NEW:** §6 diff to flip the ordering. |
| 12 | Dives MCP skill (7 tools: `list_dives`, `read_dive`, `save_dive`, `update_dive`, `delete_dive`, `view_dive`, `share_dive_data`) | ❌ **New discovery:** `/sql-reference/mcp/` lists 8 tools (adds `read_dive_version`), and the dive docs explicitly mention `from MD_INFORMATION_SCHEMA.OWNED_SHARES` for share URL discovery. The 7-tool list in Wave 1 is now 8. | **NEW:** §6 diff to add `read_dive_version` to the skill. |
| 13 | Wave 1 says MCP read-only tool is `query` and read-write is `query_rw` | ✅ Re-confirmed verbatim in `…/mcp-setup/`: "The MCP Server provides both read-only (`query`) and read-write (`query_rw`) tools." | None |
| 14 | Wave 1 §8 refactor #3: "Promote cross-link `motherduck_sync` into a template" | ✅ Still applies; not yet implemented. | Carry forward |
| 15 | Wave 1 §8 refactor #5: "Wire the upstream monitor's `/changelog/` 404 into the goal text" | ✅ Still applies; **new in Wave 2**: drop `/changelog/` entirely. | §6 diff |

## 6. Skill-file update diffs

### 6.1 `.agents/skills/motherduck/motherduck-connections/SKILL.md` — flip the DuckDB API connection pattern ordering

Wave 1 anti-pattern #1: "Don't hardcode `motherduck_token` in connection strings like `duckdb.connect("md:?motherduck_token=abc...")`". But the skill itself still teaches the URL form as the **primary** example (line ~37-43). The Wave 1 doc-side fix is needed.

**Diff (line 37-46 area):**

```diff
- ```python
- import duckdb
-
- con = duckdb.connect("md:oideachais?motherduck_token=...")
- # OR, preferred for KCG:
- con = duckdb.connect("md:oideachais", config={"motherduck_token": token})
- ```
+ ```python
+ import duckdb
+ import os
+
+ token = os.environ["MOTHERDUCK_TOKEN"]    # Locket-injected; never log this
+
+ # PREFERRED (KCG) — token in config dict, never in URL string:
+ con = duckdb.connect("md:oideachais", config={"motherduck_token": token})
+
+ # Accepted but NOT preferred — token leaks into DuckDB query logs:
+ con = duckdb.connect("md:oideachais?motherduck_token=...")   # anti-pattern
+ ```
```

Rationale: Wave 1 audit §8 refactor #1 explicitly says to move the 4 marimo notebooks off the URL-token pattern. The skill itself must teach the safe pattern first.

### 6.2 `.agents/skills/motherduck/SKILL.md` (or `references/motherduck-mcp-server.md`) — bump Dives MCP tool list from 7 → 8

**Diff (Dives tool list table):**

```diff
- | `list_dives` | List all Dives in the workspace | SELECT *
- | `read_dive` | Read a single Dive by id | `id`
- | `save_dive` | Persist a Dive to the workspace | spec JSON
- | `update_dive` | Update an existing Dive | `id` + spec JSON
- | `delete_dive` | Delete a Dive | `id`
- | `view_dive` | Open a Dive in the UI | `id`
- | `share_dive_data` | Create org-scoped shares for a Dive's data | `id`
+ | `list_dives` | List all Dives in the workspace (returns `current_version` per Dive) | SELECT *
+ | `read_dive` | Read a single Dive; supports `version` param | `id`, `version`?
+ | `read_dive_version` | Read a specific historical version of a Dive (read-only) | `id`, `version`
+ | `save_dive` | Persist a Dive to the workspace (creates version 1) | spec JSON
+ | `update_dive` | Update an existing Dive (creates a new version) | `id` + spec JSON
+ | `delete_dive` | Delete a Dive | `id`
+ | `view_dive` | Open a Dive in the UI | `id`
+ | `share_dive_data` | Create org-scoped shares for a Dive's data | `id`
```

Source: `/docs/key-tasks/ai-and-motherduck/dives/` — "You can also retrieve versions programmatically. Use [`list_dives`](/sql-reference/mcp/list-dives) to see the `current_version` for each Dive, and [`read_dive`](/sql-reference/mcp/read-dive) with the `version` parameter to inspect a specific version." Combined with the `read_dive_version` tool surfaced at `/sql-reference/mcp/`.

### 6.3 `infrastructure/firecrawl/monitors/upstream_packages/motherduck_blog.yml` — drop dead `/changelog/` target

**Diff (lines 70-74):**

```diff
   targets:
     - type: scrape
       urls:
         - "https://motherduck.com/blog/"
-        - "https://motherduck.com/docs/"          # <-- changelog at /changelog 404'd in scrape (Next.js 404 page)
-        - "https://motherduck.com/changelog/"     # <-- this one too — but is in the canonical monitor
-        - "https://motherduck.com/blog/category/engineering/"
+        - "https://motherduck.com/docs/"          # <-- canonical docs (Docusaurus v3.9.2, cacheable)
+        - "https://motherduck.com/pricing"        # <-- pricing drift (instance $/hr, tier inclusion)
+        - "https://github.com/motherduckdb/mcp-server-motherduck/releases.atom"  # <-- MCP server release feed
   goal: |  # Firecrawl LLM-judge
-    Alert on product/architecture changes — DuckLake releases, hosting
-    options (managed/BYOB/BYOC), new SQL syntax, Cortex Code updates.
+    Alert on product/architecture changes — DuckLake releases, hosting
+    options (managed/BYOB/BYOC), new SQL syntax, MCP server releases,
+    pricing tier or instance rate changes. Ignore whitespace, formatting,
+    and Next.js 404 / "Page Not Found" markers on /changelog and
+    /blog/category/* URLs that have not been migrated.
```

### 6.4 `.infisical.env` — confirm token is Business-tier (carry forward from Wave 1 §"Anti-pattern priority")

No code change. The Wave 1 priority list item for Agent 06 (Infisical) still applies: "confirm the `dev-baile/motherduck/token` vault entry exists and the token is a Business-tier (not Lite) token." KCG notebooks use 4 shared databases (`oideachais_public`, `oideachais_team`, `leabharlann_public`, `leabharlann_team`) — Lite is 3 users, 2 service accounts, 10 GB, which is too small for the 4-database fleet. The token must be a Business-tier PAT.

## 7. OpenSpec cross-references

- `openspec/research/2026-06-28-browserbase-program-2/agent-05-motherduck.md` (Wave 1 — this audit's baseline)
- `openspec/research/2026-06-28-browserbase-credit-program/phase-1a/P1A-05-motherduck.md` (Phase 1A — contains the stale "MotherDuck 0.5" claim)
- `openspec/changes/refactor-dlt-dagster-2026-stack-align/proposal.md:110-126` (origin of `motherduck_options.py` and the 3-mode `managed`/`byob`/`byoc` factory)
- `openspec/changes/celtic-data-engineering-patterns/specs/celtic-data-engineering-pipeline/spec.md:26` (the `md:oideachais` marimo binding)
- `openspec/specs/oideachais-pipeline/spec.md:141, 158, 1270` (the same binding in the canonical pipeline spec)
- `.agents/skills/motherduck/SKILL.md` + `motherduck-connections/SKILL.md` (skill files that need diffs in §6.1 and §6.2)
- `.agents/skills/agent-observability/references/mcp/MCP_SERVERS.md:106-108` (the local `mcp-server-motherduck` stdio entry — unchanged)
- `infrastructure/firecrawl/monitors/upstream_packages/motherduck_blog.yml` (the 4-URL monitor — needs the §6.3 diff)
- `infrastructure/stacks/motherduck/{blueprint.yaml,README.md,secrets.env}` (stack stub — unchanged; MotherDuck is a cloud service, not a container)
- `cianfhoghlaim/core/dlt/_oideachais_dlt_utils/motherduck_options.py:1-158` (canonical 3-mode factory — unchanged)
- `cianfhoghlaim/assets/_croilar_assets/dlt_assets.py:267-321` (the `motherduck_sync` Dagster asset — still applies)
- `infrastructure/dagster/.../motherduck_blog.yml` (the upstream monitor that Wave 1 already wired)

## 8. URL pattern observed (live)

The canonical docs URL pattern is `https://motherduck.com/docs/<section>/<subsection>/<page>/`, **not** `https://motherduck.com/docs/<short-name>/`. Wave 1 found `/docs/dives` had been migrated to `/docs/key-tasks/ai-and-motherduck/dives/`; Wave 2 confirms the same pattern across the entire docs surface (e.g. `/docs/sql-reference/motherduck-sql-reference/attach/`, `/docs/sql-reference/motherduck-sql-reference/create-database/`, `/docs/key-tasks/ai-and-motherduck/mcp-setup/`). The Docusaurus `docsearch:docusaurus_tag` metadata in every page is `docs-default-current` and `docusaurus_version: current` — meaning the **current** channel is the single source of truth, and there is no `/v1.0/` archive. KCG skill files that link to motherduck docs (e.g. the `references/motherduck-mcp-server.md` file) should be audited for any short-form `/docs/<page>` URLs and rewritten to the long-form `/docs/<section>/<subsection>/<page>/` pattern. This is a low-priority follow-up; the Wave 1 doc links already use the long form.
