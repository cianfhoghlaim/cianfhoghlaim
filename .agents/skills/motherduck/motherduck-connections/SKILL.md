---
name: motherduck-connections
description: Wire applications to MotherDuck. Use when connecting from a Python service, a Node app, a BI tool, a notebook, or a different data warehouse via the Postgres endpoint, the native DuckDB API, pg_duckdb, JDBC, the MotherDuck REST API (control plane), or the mcp-server-motherduck. Covers connection strings, authentication, SSL, environment variable configuration, service-account provisioning, access-token lifecycle, read-only patterns, RBAC, security boundaries, residency, isolation, and self-serve analytics rollout. Triggers: 'connect to MotherDuck', 'Postgres endpoint', 'pg_duckdb', 'JDBC', 'REST API', 'MCP server', 'service account', 'token rotation', 'RBAC', 'read-only token', 'self-serve analytics'.
---

# MotherDuck — Connections, Auth & Governance

Wire applications to MotherDuck and govern access. Absorbs the
former `motherduck-connect`, `motherduck-rest-api`,
`motherduck-build-cfa-app`, `motherduck-enable-self-serve-analytics`,
and `motherduck-security-governance` skills.

## When to use this skill

Use this skill when:

- Connecting from a Python / Node / Go / JVM application.
- Connecting a BI tool (Metabase, Tableau, Evidence) via the
  Postgres endpoint.
- Building a customer-facing analytics (CFA) app and need
  per-tenant isolation patterns.
- Setting up service accounts, tokens, and read-only access
  for agents.
- Using the mcp-server-motherduck (the KCG-preferred agent path).
- Talking to a security / compliance owner about residency,
  access boundaries, or isolation.

For storage pattern decisions, use `motherduck-architecture`.
For SQL / Dives, use `motherduck-analytics`.

## 4 connection methods

### 1. Native DuckDB API (Python / Node / Go / R / Java)

The KCG-preferred connection. Use `duckdb` >= 1.1.

```python
import duckdb

con = duckdb.connect("md:cianfhoghlaim?motherduck_token=...")
# OR, preferred for KCG:
con = duckdb.connect("md:cianfhoghlaim", config={"motherduck_token": token})
```

```typescript
import { Database } from "duckdb";
const db = new Database("md:cianfhoghlaim?motherduck_token=...");
```

Pros: full DuckDB SQL, `mcp-server-motherduck` compatible, no
network hops. Cons: requires the `duckdb` driver on the client.

### 2. Postgres endpoint (BI tools + cross-warehouse)

For Metabase, Tableau, Evidence, dbt-postgres, or any tool that
speaks the Postgres wire protocol.

```
host:  md-{org}.motherduck.com
port:  5432
user:  {service_account_name}
password:  {token}
database:  oideachais
sslmode:  require
```

Pros: every Postgres-speaking tool works. Cons: not all DuckDB
SQL features are exposed; some analytics-specific functions
return errors.

### 3. pg_duckdb (in-process DuckDB inside Postgres)

For workloads that need DuckDB's analytics inside a Postgres
transaction. Not used in KCG; mentioned for completeness.

### 4. mcp-server-motherduck (KCG agent path)

See `motherduck/SKILL.md` §"MCP server" for the full reference.
TL;DR:

```bash
uvx mcp-server-motherduck \
    --db-path md:cianfhoghlaim \
    --motherduck-token "$MOTHERDUCK_TOKEN" \
    --read-only --saas-mode \
    --max-rows 256 --max-chars 50000 \
    --query-timeout 300
```

For KCG agents, this is the default. The `--read-only --saas-mode`
flags are non-negotiable for any agent that does not own the
data it queries.

## Service account + token lifecycle

```python
# 1. Create a service account in MotherDuck (one-time, via UI)
#    Org → Settings → Service Accounts → "Create"
#    Name: "kcg-cianfhoghlaim-readonly"
#    Role: "Read-only" (never "Admin" for an agent)

# 2. Mint a token (one-time, via UI)
#    Service Account → Tokens → "Generate"
#    Scope: read-only on database "cianfhoghlaim"
#    Expiry: 90 days (rotate quarterly)

# 3. Store the token in Infisical
#    Path: dev-baile/motherduck/cianfhoghlaim_readonly_token
#    Reference: "infisical://dev-baile/motherduck/cianfhoghlaim_readonly_token"

# 4. Reference from code
#    .env (auto-hydrated by mise):
MOTHERDUCK_TOKEN=infisical://dev-baile/motherduck/cianfhoghlaim_readonly_token
```

**Token rotation policy** (the KCG standard):

| Token type | Lifetime | Rotation |
|:--|:--|:--|
| Agent read-only | 90 days | Quarterly |
| Agent read-write | 30 days | Monthly |
| Admin / break-glass | 7 days | Weekly; logged + paged |
| Developer personal | 365 days | Annual; SSO-gated |

## Customer-Facing Analytics (CFA) — per-tenant isolation

For CFA apps where multiple external users query shared
infrastructure:

- **One database per tenant** inside one MotherDuck organisation
  (e.g. `tenant_acme`, `tenant_globex`). Never share a database
  across tenants.
- **One service account per tenant**, scoped to its database
  only. Tokens never cross tenants.
- **Row-level security via views**: each tenant's queries are
  rewritten to filter by `tenant_id`. MotherDuck supports
  `CREATE VIEW ... WITH (security_invoker = true)`.
- **Connection pool with a per-tenant token** in the
  application server. Never share a connection across tenants.

## Read-only consumer pattern (the KCG default for agents)

For agents that consume but do not own the data (most agents):

1. Mint a read-only token scoped to the specific database
2. Store in Infisical under the agent's name
3. The agent's mcp-server-motherduck runs with `--read-only --saas-mode`
4. The agent **cannot** issue `CREATE`, `INSERT`, `UPDATE`,
   `DELETE`, or any write. Verify by running
   `CREATE TABLE __test_write_guard__ (x INT)` and expect an error.
5. The agent's `--query-timeout 300` (5 min) prevents runaway
   scans.

## Self-serve analytics rollout

For teams adopting MotherDuck as the warehouse for an internal
team (the "first team" rollout pattern):

1. Pick the **first governed dataset** — a small, stable
   dataset the team already uses (e.g. a single Salesforce
   extract).
2. Pick the **first Dive** — a single KPI from that dataset
   that the team checks daily.
3. Pick the **owner** — a single person who curates the Dive
   and answers questions.
4. **Share with the team** via a zero-copy share.
5. After 2 weeks: add the second Dive, then the first
   breakdown, then expand to the second team.
6. After 8 weeks: you have 4 teams sharing 8 Dives. Stop;
   re-evaluate the data contracts before adding the 5th team.

Do not "roll out to the whole org" on day 1. Each team needs
its own first-Dive moment.

## Security & governance — the 8 things security will ask

| Question | The KCG answer |
|:--|:--|
| Where is the data physically? | Pinned to the org's region (US-East, EU-West, AP-South). Use the MotherDuck `REGION` setting. |
| Is the data encrypted at rest? | Yes — AES-256 by MotherDuck. KMS-backed if the org is on the Enterprise plan. |
| In transit? | TLS 1.3. The `--saas-mode` flag enforces TLS for all mcp-server-motherduck connections. |
| Who can see the data? | RBAC per database + per share. Service-account tokens are scoped. |
| Audit log? | MotherDuck logs every query (user, database, query text, row count, latency). Retained 90 days on Standard, 1 year on Enterprise. |
| Row-level access? | Via `WITH (security_invoker = true)` views or external Postgres-side filtering. |
| Can we revoke a token? | Yes — instant. The MotherDuck UI shows the active-token list with a "Revoke" button. |
| Backup / DR? | MotherDuck retains 7 days of PITR (point-in-time recovery) on the Standard plan, 30 days on Enterprise. |

## Pair this skill with

- `motherduck/SKILL.md` — the master router + MCP section
- `motherduck-architecture/SKILL.md` — storage pattern
- `secrets-management/SKILL.md` — Infisical + Locket pattern for
  storing the MotherDuck token
- `dignified-python/SKILL.md` — Python idioms for the DuckDB client

## Cross-references

- [MotherDuck authentication](https://motherduck.com/docs/auth)
- [MotherDuck security](https://motherduck.com/docs/security)
- [mcp-server-motherduck on GitHub](https://github.com/motherduckdb/mcp-server-motherduck)
- [DuckDB client drivers](https://duckdb.org/docs/api/overview)
