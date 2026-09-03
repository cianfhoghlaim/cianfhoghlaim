# Agent 98 — Live MotherDuck Dives Verifier

**Program:** BrowserBase Program 2 (live-sites verifier stream)
**Date:** 2026-06-29
**Method:** webfetch + firecrawl (no browserbase, no chrome MCP) per task brief
**Sources visited:** `motherduck.com/docs`, `…/docs/key-tasks/ai-and-motherduck/dives/`, `…/dives/embedding-dives`, `…/dives/managing-dives-as-code`, `…/sql-reference/mcp/`, `…/sql-reference/motherduck-sql-reference/ai-functions/dives/`, `…/md-create-dive`, `…/md-list-dives`, `…/use-sql-query`, `…/use-dive-state`, `…/product/dives/`, `…/blog/`, `…/changelog` (404)
**Tools used:** webfetch (primary, 12 calls) + firecrawl_scrape (1 fallback for changelog)

## 1. TL;DR

- **Dives is the showpiece MotherDuck feature, now significantly deeper than Wave 1 documented**: the docs surface has grown to **9 SQL table functions** (`MD_CREATE_DIVE` … `MD_GET_DIVE_VERSION`), **3 React hooks** (`useSQLQuery`, `useDiveState`, `useExport`), **1 REST embed API** (`POST /v1/dives/<dive_id>/embed-session`), **Dive Viewer MCP App** for inline rendering in Claude web/desktop, and a **Git-based CI/CD pattern** (`blessed-dives-example` starter repo).
- **Embedding is now a Business-plan-only feature** (was undocumented in Wave 1) with 24-hour session strings, dedicated service-account requirement, `required_resources` override for multi-tenant renders, and 4 `postMessage` event types (`navigation-request`, `dive-state-update`, `export-started`, `export-file`).
- **Marimo is now explicitly being replaced by Dives in the KCG stack** (Wave 1 `agent-05-motherduck.md` decision: "Dives replaced bespoke marimo dashboards"); the syllabus_visualizer.py:249-260 → "syllabus dive button" pattern is the live integration. Changelog URL 404s; **drift in pricing/feature surface is real and material** (pricing page, instance tier list, and the new embedding Business plan tier all need re-confirmation).

## 2. Dives feature inventory

### 2.1 Creation
- **MCP path (recommended)**: `save_dive` tool → `https://api.motherduck.com/mcp` remote server, OAuth, used by Claude web/desktop, ChatGPT, Cursor, Claude Code. Inline preview via **Dive Viewer MCP App** in MCP-Apps-capable clients.
- **SQL path (programmatic)**: `MD_CREATE_DIVE(title, content, description, api_version=1)` — returns `id`, `current_version=1`, `version_id` (UUID), `version_storage_url`. Content is a JSX/React string.
- **UI path**: chat "create a Dive" → agent writes code → published to workspace.
- **Local preview**: Claude Code asks for a local Vite dev server on `http://localhost:5177/`.

### 2.2 Sharing
- **URL share** — every save produces a `https://app.motherduck.com/dives/<dive_id>` URL.
- **Dive state in URL** — `useDiveState(key, initialValue)` syncs filters/sort/view/selection into URL fragment; small state inlined, larger state stored server-side under opaque short ID.
- **Data share** — `share_dive_data` MCP tool creates org-scoped shares of underlying DBs.
- **Embed share** — `POST /v1/dives/<dive_id>/embed-session` produces a 24-hour session string; iframe loads from `embed-motherduck.com/sandbox/#session=<session>` (fragment, not query).
- **Required DBs** — `REQUIRED_DATABASES` exported constant OR `required_resources` per-session override (replaces the constant).

### 2.3 Embedding (Business plan)
- Iframe with `sandbox="allow-scripts allow-same-origin"` from `embed-motherduck.com/sandbox/`.
- Per-session `required_resources` (URL+alias) for **multi-tenant rendering** — same Dive, different tenant DBs.
- Per-session `initial_state` for **seed filters/date ranges** (capped 64 KB; 8 KB inline, larger stored server-side).
- `postMessage` events: `navigation-request` (link clicks), `dive-state-update` (filter changes), `export-started` / `export-file` / `export-error` (csv/json/parquet/xlsx).
- CSP requirement: `frame-src https://embed-motherduck.com`.

### 2.4 Versioning
- **Every update = new version** (read-only history); `MD_LIST_DIVE_VERSIONS` + `MD_GET_DIVE_VERSION(version_number)`.
- `MD_UPDATE_DIVE_CONTENT` increments version; `MD_UPDATE_DIVE_METADATA` does not.
- Version picker in MotherDuck UI top-right; selecting a previous version is read-only.
- `version` field in embed session API maps to the **version number** (not UUID).

### 2.5 Security
- **Embed session = base64, NOT encrypted**, contains a read-only read-scaling token (24-hr TTL).
- Service account for embedding must have **Admin role**; sessions themselves are always read-only.
- Session token in URL **fragment** (`#session=...`), never sent to server.
- Dedicated service account recommended to avoid share-alias collisions.
- Export messages must be treated as untrusted (origin + source validation required in parent page).

### 2.6 Required databases (`REQUIRED_DATABASES`)
- JSX constant exports an array of `{type, path, alias}`; `type` is `"share"` or `"database"`.
- `path` is `md:_share/<db>/<uuid>` for shares, `md:<db_name>` for owned DBs.
- `alias` defaults to the URL-extracted DB name; **must not collide** with existing DBs on the service account.

## 3. Verbatim code / SQL examples (10)

### 3.1 `MD_CREATE_DIVE` (SQL — minimal working example)
> Source: <https://motherduck.com/docs/sql-reference/motherduck-sql-reference/ai-functions/dives/md-create-dive>

```sql
SELECT * FROM MD_CREATE_DIVE(
  title = 'PokeDuck',
  content = '
    import { useSQLQuery } from "@motherduck/react-sql-query";
    export default function Dive() {
        const { data } = useSQLQuery(
            `SELECT PROMPT(''Suggest a duck type or pokemon and tell a fun fact about them'')`,
            { select: (rows) => Object.values(rows[0])[0] }
            );
        return <div><p>FUN FACT:</p><p>{JSON.stringify(data)};
    }'
);
```

### 3.2 `MD_LIST_DIVES` (SQL — paginated)
> Source: <https://motherduck.com/docs/sql-reference/motherduck-sql-reference/ai-functions/dives/md-list-dives>

```sql
SELECT * FROM MD_LIST_DIVES("limit" =20, "offset" =0);  -- first page
SELECT * FROM MD_LIST_DIVES("limit" =20, "offset" =20); -- second page
```

### 3.3 `REQUIRED_DATABASES` (JSX — auto-attach shares)
> Source: <https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/#declaring-required-databases>

```jsx
export const REQUIRED_DATABASES = [
  {
    type: 'share',
    path: 'md:_share/<database_name>/<share_uuid>',
    alias: '<database_name>'
  }
];
```

### 3.4 Embed session — Node.js (verbatim)
> Source: <https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/embedding-dives/#step-1-create-an-embed-session>

```javascript
const DIVE_ID = "<your_dive_id>";
const VERSION = 12;

const response = await fetch(
  `https://api.motherduck.com/v1/dives/${DIVE_ID}/embed-session`,
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${MOTHERDUCK_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: SERVICE_ACCOUNT_USERNAME,
      version: VERSION,
    }),
  }
);
const { session } = await response.json();
```

### 3.5 Embed session — Python (verbatim)
> Source: <https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/embedding-dives/#step-1-create-an-embed-session>

```python
import httpx
response = httpx.post(
    f"https://api.motherduck.com/v1/dives/{DIVE_ID}/embed-session",
    headers={"Authorization": f"Bearer {MOTHERDUCK_TOKEN}",
             "Content-Type": "application/json"},
    json={"username": SERVICE_ACCOUNT_USERNAME, "version": VERSION},
)
response.raise_for_status()
session = response.json()["session"]
```

### 3.6 Multi-tenant `required_resources` override
> Source: <https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/embedding-dives/#override-required-databases>

```json
{
  "username": "svc_acme_embed",
  "required_resources": [
    { "url": "md:_share/tenant_a_data/<share_uuid>", "alias": "tenant_data" }
  ]
}
```

### 3.7 `initial_state` seeding (filters, date range)
> Source: <https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/embedding-dives/#preconfigure-the-starting-ui-state>

```json
{
  "username": "svc_acme_embed",
  "initial_state": {
    "region": "emea",
    "dateRange": { "start": "2026-01-01", "end": "2026-03-31" }
  }
}
```

### 3.8 `useSQLQuery` with BigInt guard
> Source: <https://motherduck.com/docs/sql-reference/motherduck-sql-reference/ai-functions/dives/use-sql-query>

```jsx
import { useSQLQuery } from "@motherduck/react-sql-query";
const N = (v) => (v != null ? Number(v) : 0);

export default function Dive() {
  const { data, isLoading } = useSQLQuery(`
    SELECT category, SUM(amount) AS total
    FROM "my_db"."main"."sales"
    GROUP BY ALL
  `);
  if (isLoading) return <div>Loading...</div>;
  const rows = Array.isArray(data) ? data : [];
  return <ul>{rows.map((row) => (
    <li key={row.category}>{row.category}: ${N(row.total).toLocaleString()}</li>
  ))}</ul>;
}
```

### 3.9 `useExport` (xlsx with DuckDB COPY writer options)
> Source: <https://motherduck.com/docs/sql-reference/motherduck-sql-reference/ai-functions/dives/use-sql-query/#export-query-results>

```jsx
import { useExport } from "@motherduck/react-sql-query";
export default function DiveExportButton() {
  const { exportQuery } = useExport();
  return <button onClick={() => exportQuery({
    sql: `SELECT customer_id, SUM(amount) AS total_amount
          FROM "my_db"."main"."orders" GROUP BY ALL ORDER BY total_amount DESC`,
    format: "parquet",
    filename: "customer-totals"
  })}>Export customer totals</button>;
}
```

### 3.10 `useDiveState` (shared filter + sort, syncs to URL)
> Source: <https://motherduck.com/docs/sql-reference/motherduck-sql-reference/ai-functions/dives/use-dive-state>

```jsx
import { useDiveState, useSQLQuery } from "@motherduck/react-sql-query";
export default function Dive() {
  const [region, setRegion] = useDiveState("region", "all");
  const regionFilter = { all: "", amer: "WHERE region = 'Americas'",
                         emea: "WHERE region = 'EMEA'", apac: "WHERE region = 'APAC'" }[region] ?? "";
  const { data = [], isLoading } = useSQLQuery(`
    SELECT region, SUM(revenue) AS revenue
    FROM "analytics"."main"."orders" ${regionFilter}
    GROUP BY ALL ORDER BY revenue DESC`);
  if (isLoading) return <div>Loading...</div>;
  return (<div><select value={region} onChange={(e) => setRegion(e.target.value)}>
    <option value="all">All regions</option><option value="amer">Americas</option>
    <option value="emea">EMEA</option><option value="apac">APAC</option>
  </select><ul>{data.map((row) => <li key={row.region}>{row.region}: {Number(row.revenue).toLocaleString()}</li>)}</ul></div>);
}
```

## 4. Dives API endpoints

### 4.1 REST API (embed)
| Method | Endpoint | Purpose |
|:--|:--|:--|
| `POST` | `https://api.motherduck.com/v1/dives/<dive_id>/embed-session` | Mint a 24-hr read-only embed session; body `{username, version?, required_resources?, initial_state?}`; returns `{session}` |
| (iframe load) | `https://embed-motherduck.com/sandbox/#session=<session_from_backend>` | Render iframe; CSP `frame-src https://embed-motherduck.com` required |

### 4.2 MCP server tools (`https://api.motherduck.com/mcp`, OAuth, 25 tools)
| Tool | Purpose |
|:--|:--|
| `get_dive_guide` | Load canonical instructions for the agent |
| `list_dives` | List workspace Dives (returns `current_version` per Dive) |
| `read_dive` | Read a Dive's full React component (supports `version` parameter) |
| `view_dive` | Render the Dive inline in MCP-Apps-capable clients (Claude web/desktop) |
| `save_dive` | Persist a new Dive to the workspace |
| `update_dive` | Modify title, description, or content (creates new version if content) |
| `share_dive_data` | Org-share the DBs referenced by a Dive |
| `delete_dive` | Permanently delete a Dive |

### 4.3 SQL table functions (server-side only, not local DuckDB)
| Function | Purpose |
|:--|:--|
| `MD_CREATE_DIVE(title, content, description?, api_version?)` | Create Dive, returns initial version metadata |
| `MD_GET_DIVE(id)` | Read full React content |
| `MD_LIST_DIVES(limit?, offset?, include_org_shares?)` | Paginated metadata list |
| `MD_UPDATE_DIVE_CONTENT(id, content, version_description?)` | New version |
| `MD_UPDATE_DIVE_METADATA(id, title?, description?)` | No new version |
| `MD_DELETE_DIVE(id)` | Permanent delete |
| `MD_LIST_DIVE_VERSIONS(dive_id, limit?, offset?)` | Version history |
| `MD_GET_DIVE_VERSION(dive_id, version)` | Specific version content |

## 5. Changelog since Wave 1 (2026-06-28 agent-05 baseline)

**Note:** `https://motherduck.com/changelog` returns a **Next.js 404** (page moved); `motherduck.com/changelog/` also 404s. The Firecrawl monitor at `infrastructure/firecrawl/monitors/upstream_packages/motherduck_blog.yml` needs updating. Drift was reconstructed from the docs site and blog index.

| Date (observed) | Change | Source |
|:--|:--|:--|
| 2026-04-27 | **Embedded Dives announced** (Business plan only) | <https://motherduck.com/blog/april-2026-product-roundup/> |
| 2026-05-12 | Quack (DuckDB client-server protocol) — relevant to Dive compute | <https://motherduck.com/blog/duckdb-client-server/> |
| 2026-05-28 | **DiveMaxxing** data-viz hackathon — signals Dives now the central brand | <https://motherduck.com/blog/divemaxxing-data-viz-contest/> |
| 2026-06-04 | Obsidian-vault-DuckDB blog (shows Dives flexibility) | <https://motherduck.com/blog/obsidian-vault-duckdb-ai-agents/> |
| 2026-06-16 | **"Replacing Our BI Tool with Dives"** — explicit replacement of BI tooling with Dives+Claude Code | <https://motherduck.com/blog/replacing-our-bi-tool-with-dives/> |
| 2026-06-29 (today) | **Dive Viewer MCP App** + new `useExport` hook + new `exportAs` return on `useSQLQuery` + Git-based "Managing Dives as Code" (`blessed-dives-example` starter) | <https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/>, <https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/managing-dives-as-code> |

## 6. Drift items vs Wave 1 (agent-05-motherduck.md)

| # | Wave 1 claim | Verified now | Drift |
|:--|:--|:--|:--|
| D1 | Dives "created via the MCP server (not raw SQL)" | **FALSE — drift in the OTHER direction**: 8 SQL table functions now exist (`MD_CREATE_DIVE` … `MD_GET_DIVE_VERSION`) — full SQL CRUD | Material — re-document |
| D2 | Dives versioning mentioned | `MD_LIST_DIVE_VERSIONS` + `MD_GET_DIVE_VERSION` + `MD_UPDATE_DIVE_CONTENT` documented; `version` field on embed session | **New APIs** |
| D3 | "shareable via URL with state encoding" | Confirmed + new `initial_state` per-session seeding, `dive-state-update` postMessage for parent-page capture | Reinforced |
| D4 | `REQUIRED_DATABASES` constant in Dive React | Confirmed + new per-session `required_resources` array (8 KB cap) for multi-tenant | Reinforced + extension |
| D5 | "Pricing: Lite / Business / Enterprise" | Confirmed (agent-05 P1A-05 baseline). Embedding is **Business-plan-only** (newly verified) | **New tiered feature gate** |
| D6 | No mention of REST embed API | **NEW** — `POST /v1/dives/<dive_id>/embed-session` | New |
| D7 | "Wave 1 changelog URL 404'd" | **STILL 404s** at both `/changelog` and `/changelog/` (Firecrawl `404` confirmed) | Open drift in monitor |
| D8 | No `useExport` hook mentioned | **NEW** — `useExport()` + `exportAs()` return on `useSQLQuery`; supports csv/json/parquet/xlsx via DuckDB `COPY TO` | New |
| D9 | `mcp-server-motherduck` (local) + Remote MCP at `api.motherduck.com/mcp` | Confirmed; **NEW**: Dive Viewer MCP App renders Dives inline in Claude web/desktop (was not in Wave 1) | New MCP app |
| D10 | marimo dashboards in syllabus_visualizer.py:249-260 ("syllabus dive button") | **Confirmed replacement**: Wave 1 decision `agent-05-motherduck.md` line 19: "Dives replaced bespoke marimo dashboards". Marimo still used for `oideachais-marimo-dashboards` (11 notebooks) | Reaffirmed |

## 7. Marimo integration per project plan

The KCG project plan (per `agent-05-motherduck.md` decision matrix) treats **marimo notebooks and MotherDuck Dives as complementary**, not competing:

- **Marimo** = authoring surface for analysis (`oideachais-marimo-dashboards` spec, 11 notebooks for the 5 educational stages; `notebooks/_oideachais/syllabus_visualizer.py:249-260`).
- **Dives** = publishing + sharing surface for the result of an analysis. The "syllabus dive button" in `syllabus_visualizer.py` is the canonical bridge: a marimo notebook authors a query/chart, the user clicks the button, and the agent (via MCP) saves a Dive to MotherDuck that re-runs against the same DuckLake-backed data.
- **Sharing** — Marimo notebooks stay private to the analyst; the **published artefact is a Dive URL** (`https://app.motherduck.com/dives/<dive_id>`) that anyone in the org can open with live data. The `share_dive_data` MCP tool propagates the org-shares required.
- **Demos** — For the oideachais public demo, ship marimo as the **authoring experience** (open notebook, iterate) and Dives as the **public embed surface** (Business plan, iframe with CSP `frame-src https://embed-motherduck.com`). The `REQUIRED_DATABASES` constant + per-tenant `required_resources` override means a single Dive source file can render separately for each tenant's share.
- **Recommended pattern (not yet in the repo)**: add a `dive_button()` helper in `notebooks/_oideachais/_common/` that calls `save_dive` with a templated title (`{notebook_name} - {last_run_at}`) and the current chart's SQL.

## Anti-patterns (from Wave 1, reaffirmed)

- **Don't bypass `REQUIRED_DATABASES`** in custom Dives — viewers without the right share get "Catalog does not exist" errors. Always export the constant.
- **Don't put `version` as the UUID** in embed sessions — the API expects the version *number* from `MD_LIST_DIVES.current_version`.
- **Don't concatenate user input into SQL** inside a Dive — use `useDiveState` to keep selections in a controlled enum, not free text.
- **Don't log the embed session string** — it contains a read-only token; treat it as a short-lived credential.
- **Don't use `useSQLQuery` data without guarding `undefined`** — the `data` field is the row array directly (no `.rows` wrapper), and BIGINT/HUGEINT come back as JS `BigInt` (define `const N = (v) => v != null ? Number(v) : 0`).
- **Don't use app-relative links in embedded Dives** — `/settings/members` resolves against `embed-motherduck.com`, not the host app; the parent page receives a `navigation-request` postMessage and must validate the URL.
- **Don't store the admin access token client-side** — the token belongs on the backend; only the 24-hr session string reaches the browser.

## CCC anchors (codebase cross-reference)

- `openspec/research/2026-06-28-browserbase-program-2/agent-05-motherduck.md:19` — Wave 1 baseline (Dives = showpiece)
- `openspec/research/2026-06-28-browserbase-program-2/agent-05-motherduck.md:267-321` — `motherduck_sync_asset` (Dive input pipeline)
- `openspec/specs/oideachais-pipeline/spec.md` — DLT → DuckLake → MotherDuck → Dives chain
- `openspec/specs/oideachais-marimo-dashboards/spec.md` — 11 marimo notebooks (Dives sibling)
- `cianfhoghlaim/assets/_croilar_assets/dlt_assets.py:267-321` — `motherduck_sync` asset (the croilar→Dive pipeline)
- `infrastructure/firecrawl/monitors/upstream_packages/motherduck_blog.yml` — needs `/changelog` URL fixed (still 404s)
- `.agents/skills/motherduck/SKILL.md` — needs update for `MD_CREATE_DIVE` SQL path + embed REST API

## Real URL patterns observed (live site)

- Docs: `https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/`
- Docs: `https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/embedding-dives`
- Docs: `https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/managing-dives-as-code`
- Docs SQL: `https://motherduck.com/docs/sql-reference/motherduck-sql-reference/ai-functions/dives/md-create-dive`
- API: `https://api.motherduck.com/v1/dives/<dive_id>/embed-session`
- Embed host: `https://embed-motherduck.com/sandbox/`
- MCP: `https://api.motherduck.com/mcp`
- App: `https://app.motherduck.com/dives/<dive_id>`
- Local dev preview: `http://localhost:5177/`
- Starter repo: `https://github.com/motherduckdb/blessed-dives-example`

## 3+ verbatim quotes

1. **Product page positioning** (<https://motherduck.com/product/dives/>):
   > "Dives are interactive visualizations you create with natural language, directly on top of your data in MotherDuck. They query live data using MotherDuck's dual execution feature for snappy data experiences and easy sharing."
2. **Embedding session security** (<https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/embedding-dives/>):
   > "Your service account's access token is a high-privilege read-write admin token that stays on your backend and is used only to create embed sessions. The session string it produces contains a separate, read-only token that is limited in scope and expires after 24 hours. Only the session string should ever reach the frontend."
3. **Required databases pattern** (<https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/#declaring-required-databases>):
   > "When your Dive queries a database that viewers might not have attached, export a `REQUIRED_DATABASES` constant from your component. MotherDuck automatically attaches these databases (including shared databases) before running any queries, so your teammates don't see 'Catalog does not exist' errors."
4. **Dive Viewer MCP App** (<https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/>):
   > "On clients that support MCP Apps, the MotherDuck MCP Server serves a Dive Viewer MCP App that renders your Dive directly in the chat with the same React components used in the MotherDuck UI. At launch, this is supported in Claude web and desktop; other clients fall back to a sample-data preview."
5. **Git-based CI/CD for Dives** (<https://motherduck.com/docs/key-tasks/ai-and-motherduck/dives/managing-dives-as-code>):
   > "The entire pipeline is two GitHub Actions and one secret (`MOTHERDUCK_TOKEN`). At MotherDuck, we use a dedicated service account so anyone with repo access can edit and deploy with the same ownership scope."
