---
name: motherduck
description: Master routing skill for all MotherDuck operations. Use this to determine which of the 4 task-specific MotherDuck sub-skills to invoke (architecture, data-modeling, analytics, connections), or to wire the mcp-server-motherduck (the KCG-preferred agent path).
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
| `--db-path` | `md:` | Use `/path/to/local.duckdb` for local-only; `md:oideachais` for the read-only KCG lakehouse; `s3://bucket/path.duckdb` for object-storage |
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
  --db-path /Users/cianmacandeisigh/dev/kings_college_galway/stedding/oideachais.duckdb \
  --read-only

# MotherDuck cloud (KCG read-only consumer)
uvx mcp-server-motherduck \
  --db-path md:oideachais \
  --motherduck-token "$MOTHERDUCK_TOKEN" \
  --read-only --saas-mode

# Production: streaming HTTP + timeout
uvx mcp-server-motherduck \
  --transport stream \
  --db-path md:oideachais \
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
        "--db-path", "md:oideachais",
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
- `.agents/skills/oideachais-storage/SKILL.md` — for
  the DuckLake / MotherDuck read-only mental model

See [`docs/teanga/motherduck_mcp.md`](../../../docs/teanga/motherduck_mcp.md)
for the full 457-line reference including all transport
modes, the SaaS-mode security model, and the
data-sharing semantics.
