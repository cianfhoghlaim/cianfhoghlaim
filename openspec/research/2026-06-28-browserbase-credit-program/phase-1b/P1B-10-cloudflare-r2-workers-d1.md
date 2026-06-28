# P1B-10 — Cloudflare R2 + Workers + D1 (Phase 1B, Vector + Graph + Storage)

**Date:** 2026-06-28
**Phase:** 1B (Vector + Graph + Storage Tier)
**Budget:** ~180 credits
**Subagent:** research

## TL;DR

Cloudflare R2 is the **S3-compatible object storage** that powers the `oideachais-web` static asset hosting + the leabharlann public-facing media. Cloudflare Workers is the **edge compute** that runs BAML extraction on PDF uploads (low-latency, zero-egress). Cloudflare D1 is the **serverless SQLite** that backs the OAuth session table.

The canonical Cianfhoghlaim pattern uses R2 for **public-facing assets** (Garage is private), Workers for **edge BAML** (low-latency inference at the edge), and D1 for **session metadata** (zero-DBA).

## Code

| Path | Purpose |
|:--|:--|
| `oideachais/web/apps/oideachais-web/wrangler.toml` | Cloudflare Workers config |
| `oideachais/web/apps/oideachais-web/src/workers/` | Cloudflare Workers (BAML edge inference) |
| `oideachais/web/apps/oideachais-web/migrations/` | D1 schema migrations (sessions, OAuth) |
| `cognify/rules/cloudflare_secrets.py` | Lists 4 R2 buckets + D1 DB IDs |

**Canonical wrangler.toml**:

```toml
name = "oideachais-web"
main = "src/workers/index.ts"
compatibility_date = "2026-06-28"

# R2 buckets (binding)
[[r2_buckets]]
binding = "LEABHARLANN_BUCKET"
bucket_name = "leabharlann-public"

[[r2_buckets]]
binding = "STATIC_ASSETS"
bucket_name = "oideachais-static"

# D1 database (binding)
[[d1_databases]]
binding = "DB"
database_name = "oideachais-sessions"
database_id = "infisical://dev-baile/cloudflare/d1_database_id"

# Environment variables
[vars]
LITELLM_BASE_URL = "https://litellm.cianfhoghlaim.ie/v1"
COGNEE_API_URL = "https://cognee.cianfhoghlaim.ie"

# Secrets (managed via `wrangler secret put`)
# - LITELLM_MASTER_KEY
# - COGNEE_API_KEY
# - BETTER_AUTH_SECRET
```

**Canonical Worker** (`oideachais/web/apps/oideachais-web/src/workers/index.ts`):

```typescript
import { extractEn } from "./baml_client";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // /api/extract endpoint: runs BAML extraction on a PDF from R2
    if (url.pathname === "/api/extract") {
      const { key } = await request.json();
      const obj = await env.LEABHARLANN_BUCKET.get(key);
      if (!obj) return new Response("Not found", { status: 404 });
      const pdfBytes = await obj.arrayBuffer();
      const result = await extractEn({ pdf: pdfBytes });
      return new Response(JSON.stringify(result), {
        headers: { "content-type": "application/json" },
      });
    }

    // /api/sessions: OAuth session lookup via D1
    if (url.pathname === "/api/sessions") {
      const sessionId = url.searchParams.get("id");
      const result = await env.DB.prepare(
        "SELECT user_id, expires_at FROM sessions WHERE id = ?"
      ).bind(sessionId).first();
      return new Response(JSON.stringify(result), {
        headers: { "content-type": "application/json" },
      });
    }

    return new Response("Not found", { status: 404 });
  },
};
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `CLOUDFLARE_ACCOUNT_ID` | `infisical://dev-baile/cloudflare/account_id` | Locket |
| `CLOUDFLARE_API_TOKEN` | `infisical://dev-baile/cloudflare/api_token` | Locket |
| `LITELLM_MASTER_KEY` | (Worker secret, not in env) | `wrangler secret put` |
| `COGNEE_API_KEY` | (Worker secret) | `wrangler secret put` |
| `BETTER_AUTH_SECRET` | (Worker secret) | `wrangler secret put` |

## CCC anchors

`oideachais/web/apps/oideachais-web/wrangler.toml` · `oideachais/web/apps/oideachais-web/src/workers/` · `oideachais/web/apps/oideachais-web/migrations/`

Search terms: `"wrangler.toml"`, `"R2"`, `"D1"`, `"Workers"`.

## Drift log

| Date | Event |
|--:|:--|
| 2025-09 | Initial R2 deployment (static assets) |
| 2025-12 | Added D1 (OAuth sessions) |
| 2026-02 | Added Workers (BAML edge extraction) |
| 2026-04 | Wired to LiteLLM `minimax` alias |

## Anti-patterns

1. Don't use R2 for private data (use Garage instead) — R2 is for public assets
2. Don't store secrets in wrangler.toml — use `wrangler secret put`
3. Don't run BAML extraction in the browser — use the edge Worker
4. Don't use D1 for high-throughput analytics — use MotherDuck

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Edge compute | Cloudflare Workers (not Lambda@Edge) | Lower latency + simpler DX |
| Object storage | R2 (public) + Garage (private) | Per-asset visibility |
| Session DB | D1 (SQLite) | Zero-DBA + low-latency |
| Static assets | R2 (not S3 + CloudFront) | Cheaper + native CF integration |
| Edge BAML | LiteLLM (via Workers) | Centralized model routing |
| Auth | BetterAuth (with D1 session table) | Modern + BAML-friendly |

## Files to read next

`oideachais/web/apps/oideachais-web/wrangler.toml` · `oideachais/web/apps/oideachais-web/src/workers/` · `cognify/rules/cloudflare_secrets.py` · `.agents/skills/cloudflare/SKILL.md` · `.agents/skills/cloudflare-workers/SKILL.md`
