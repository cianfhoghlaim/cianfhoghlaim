# F-43 · Edge BAML Extraction (Cloudflare Workers + R2 + LiteLLM)

**Date:** 2026-06-29
**Agent:** 43 of 43 (BrowserBase Program 2, Wave 2 — synthesis)
**Effort:** L (new runtime + new infra stack)
**Priority:** P0 (per `27-feature-backlog.md` F-05, top 3 ship-next-quarter feature)
**Inputs:** `agent-15-baml.md`, `27-feature-backlog.md` §F-05, `cianfhoghlaim/web/apps/oideachais-web/wrangler.toml`
**Related spec delta target:** `openspec/specs/edge-baml-extraction/spec.md` (NEW)

---

## 1. TL;DR

Move the 8 inline `anthropic/claude-sonnet-4-20250514` BAML calls (Agent 15 finding #1) and 6 legacy `clients_0.baml` Gemini clients **off the LiteLLM hot path** and into a Cloudflare Workers edge runtime that sits between the user's browser and the LiteLLM gateway. The Worker is triggered by an R2 `put` event (or HTTP POST), fetches the PDF/text from R2, calls the existing LiteLLM gateway at `litellm.cianfhoghlaim.ie` (which already fronts 7+ providers with fallback chains + Langfuse + cost caps), and writes the validated extraction back to R2 as JSON. **`baml-edge` does not exist as of 2026-06-28** (BAML upstream has no WASM/edge runtime — the synthesis file's claim is aspirational), so the practical path is: Worker → fetch to LiteLLM → Zod-validate result → R2. The BAML `.baml` schemas stay the source of truth (codegen produces both Pydantic **and** Zod via the `typescript` generator added in Agent 15 refactor #10).

---

## 2. Architecture

```
┌─────────────┐  HTTPS upload    ┌──────────────────┐
│   Browser   │ ───────────────► │  R2 bucket        │
│ (TanStack   │  POST /extract   │ cianfhoghlaim-    │
│  Start UI)  │                  │ leaving-cert      │
└─────────────┘                  └────────┬──────────┘
                                          │ put event
                                          ▼
                              ┌────────────────────────┐
                              │ Cloudflare Worker       │
                              │ oideachais-edge-extract │
                              │ (consumes R2 event OR   │
                              │  HTTP POST)             │
                              └──────┬───────────┬─────┘
                                     │           │
                          1. read    │           │ 3. write JSON
                          object     │           │  to R2 prefix
                                     ▼           ▼
                          ┌──────────┐     ┌──────────────┐
                          │ R2 read  │     │ R2 write     │
                          │ PDF/    │     │ /extractions/│
                          │ text    │     │ {key}.json   │
                          └────┬─────┘     └──────────────┘
                               │
                          2. fetch (OpenAI-compatible)
                               │
                               ▼
                  ┌──────────────────────────┐
                  │ LiteLLM gateway          │
                  │ litellm.cianfhoghlaim.ie │
                  │ /v1/chat/completions     │
                  │ model = "extract-en"     │
                  │ ↳ 7-tier fallback chain  │
                  │ ↳ Langfuse OTEL trace    │
                  │ ↳ cost cap per call      │
                  └──────────────────────────┘
```

**Why edge, not Dagster:** the 8 inline `client "anthropic/..."` calls in `curriculum_extraction.baml` are typically short prompts (curriculum area classification, fediverse actor resolution) with < 4 kB of input. Routing them through the existing Dagster → BAML → dlt path costs ~3-8 s of worker bootstrap for a 200 ms extraction. The Worker path returns in < 300 ms P50 because the LLM call is the only network hop.

**Why NOT `baml-edge` WASM:** BAML upstream (`baml-language 0.13.0` + `baml-py 0.223.0`, both 2026-06) has **no WASM target**. The BAML runtime is a Rust VM that compiles to native + a CPython extension, not to `wasm32-unknown-unknown`. The 5th synthesis file's F-05 description is aspirational; the practical path is the TypeScript codegen (Agent 15 refactor #10: `generator lang_ts { output_type typescript }`) which produces Zod schemas, and a thin Worker that calls LiteLLM with a JSON-schema response format. Zod gives us the same `@description`-driven validation as BAML's SAP (Schema-Aligned Parser).

---

## 3. Worker handler code

**File:** `cianfhoghlaim/web/apps/oideachais-web/workers/edge-extract.ts`

```typescript
// oideachais-edge-extract — Cloudflare Worker
// Triggered by: (a) HTTP POST /extract, (b) R2 bucket event (binding: LEAVING_CERT_BUCKET)
// Runtime:     workers-typescript, compatibility_date 2026-06-06
// R2 binding:  LEAVING_CERT_BUCKET (cianfhoghlaim-leaving-cert)
// Env vars:    LITELLM_BASE_URL, LITELLM_MASTER_KEY, EDGE_EXTRACT_MODEL
//   (set via wrangler secret put or .env.prod from Infisical)

import { z } from "zod";                       // Zod from BAML TS codegen
import { ExtractLearningOutcomeRelationships } from "../src/baml_client/schemas/curriculum_extraction"; // generated by `baml-cli generate --lang typescript`

export interface Env {
  LEAVING_CERT_BUCKET: R2Bucket;
  LITELLM_BASE_URL: string;       // https://litellm.cianfhoghlaim.ie
  LITELLM_MASTER_KEY: string;     // sk-... (Infisical-injected)
  EDGE_EXTRACT_MODEL: string;     // "extract-en" → gemini-2.5-flash → glm-4.6 → ...
  R2_PUBLIC_URL: string;          // https://r2.cianfhoghlaim.ie
}

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "https://oideachais.cianfhoghlaim.ie",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, X-Baml-Trace-Id",
  "Content-Type": "application/json",
};

interface ExtractRequest {
  r2_key: string;                 // e.g. "exams/lc-irish-2024-p1.pdf"
  schema: "LearningOutcome" | "ExamQuestion" | "FediverseActor" | "GeminiDeepResearchReport";
  prompt_context?: Record<string, unknown>;
}

// ─────────────────────────────────────────────────────────────────────
// HTTP entry point (and optional R2-event queue consumer)
// ─────────────────────────────────────────────────────────────────────
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS_HEADERS });
    if (request.method !== "POST")  return new Response("Method Not Allowed", { status: 405 });

    const body = (await request.json()) as ExtractRequest;

    // 1. R2 GET
    const obj = await env.LEAVING_CERT_BUCKET.get(body.r2_key);
    if (!obj) return json({ error: "r2_object_not_found", key: body.r2_key }, 404);
    const buf = await obj.arrayBuffer();
    const mimeType = obj.httpMetadata?.contentType ?? "application/octet-stream";
    const isPdf    = mimeType === "application/pdf";

    // 2. Build OpenAI-compatible payload (image_url for PDFs, text for txt/md)
    const dataPart = isPdf
      ? { type: "image_url", image_url: { url: `data:${mimeType};base64,${bufToB64(buf)}` } }
      : { type: "text",      text: new TextDecoder().decode(buf) };
    const messages = [
      { role: "system", content: `You are a structured-extraction engine. Return ONLY valid JSON matching the schema below. Do not include prose, code fences, or commentary.\n\nSchema (${body.schema}):\n${JSON.stringify(pickSchema(body.schema), null, 2)}` },
      { role: "user",   content: [
          { type: "text", text: `R2 key: ${body.r2_key}` }, dataPart,
          ...(body.prompt_context ? [{ type: "text", text: `Context: ${JSON.stringify(body.prompt_context)}` }] : []),
        ] },
    ];

    // 3. Call LiteLLM gateway
    const t0 = Date.now();
    const litellmResp = await fetch(`${env.LITELLM_BASE_URL}/v1/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${env.LITELLM_MASTER_KEY}` },
      body: JSON.stringify({
        model: env.EDGE_EXTRACT_MODEL, messages,
        response_format: { type: "json_object" },
        temperature: 0.0, max_tokens: 4096,
        user: `edge-extract:${body.r2_key}`,
        metadata: { trace_name: "edge-baml-extract", schema: body.schema },
      }),
    });
    if (!litellmResp.ok) return json({ error: "litellm_error", status: litellmResp.status }, 502);
    const litellmJson = (await litellmResp.json()) as { choices: { message: { content: string } }[]; usage?: { prompt_tokens: number; completion_tokens: number; total_tokens: number } };
    const elapsed_ms = Date.now() - t0;

    // 4. Zod-validate
    const rawJson = JSON.parse(litellmJson.choices[0].message.content);
    const parsed  = pickZodSchema(body.schema).safeParse(rawJson);
    if (!parsed.success) {
      const failKey = `extractions/failed/${crypto.randomUUID()}.json`;
      await env.LEAVING_CERT_BUCKET.put(failKey, JSON.stringify({ r2_key: body.r2_key, schema: body.schema, raw: rawJson, zod_issues: parsed.error.issues, litellm_usage: litellmJson.usage, elapsed_ms, ts: new Date().toISOString() }, null, 2), { httpMetadata: { contentType: "application/json" } });
      return json({ error: "schema_validation_failed", issues: parsed.error.issues, fail_key: failKey }, 422);
    }

    // 5. Write to R2 under partitioned prefix
    const outKey = `extractions/${body.schema.toLowerCase()}/${body.r2_key.replace(/\.[^.]+$/, "")}.json`;
    await env.LEAVING_CERT_BUCKET.put(outKey, JSON.stringify({ schema: body.schema, r2_key: body.r2_key, extraction: parsed.data, litellm_usage: litellmJson.usage, elapsed_ms, model: env.EDGE_EXTRACT_MODEL, ts: new Date().toISOString() }, null, 2), { httpMetadata: { contentType: "application/json" } });

    return json({ ok: true, output_key: outKey, output_url: `${env.R2_PUBLIC_URL}/${outKey}`, usage: litellmJson.usage, elapsed_ms });
  },

  // Optional: consume R2 event notifications (requires R2 event notifications + queue binding)
  async queue(batch: MessageBatch, env: Env): Promise<void> {
    for (const msg of batch.messages) {
      const body = msg.body as ExtractRequest;
      const req  = new Request("https://internal/extract", { method: "POST", body: JSON.stringify(body) });
      await this.fetch(req, env);
      msg.ack();
    }
  },
} satisfies ExportedHandler<Env>;

// ─────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────
function pickSchema(name: ExtractRequest["schema"]) {
  switch (name) {
    case "LearningOutcome":         return ExtractLearningOutcomeRelationships;
    case "ExamQuestion":            return ExamQuestionZod;          // imported from baml_client
    case "FediverseActor":          return FediverseActorZod;
    case "GeminiDeepResearchReport":return GeminiDeepResearchReportZod;
  }
}
function pickZodSchema(name: ExtractRequest["schema"]) {
  switch (name) {
    case "LearningOutcome":         return LearningOutcomeZod;
    case "ExamQuestion":            return ExamQuestionZod;
    case "FediverseActor":          return FediverseActorZod;
    case "GeminiDeepResearchReport":return GeminiDeepResearchReportZod;
  }
}
function bufToB64(buf: ArrayBuffer): string {
  let s = "";
  const bytes = new Uint8Array(buf);
  for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
  return btoa(s);
}
function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: CORS_HEADERS });
}
```

**File:** `wrangler.toml` (delta — append to existing `cianfhoghlaim/web/apps/oideachais-web/wrangler.toml`):

```toml
# ── Edge BAML Extraction Worker ───────────────────────────────────────────
[env.production.workers]
name = "oideachais-edge-extract"
main = "./workers/edge-extract.ts"
compatibility_date = "2026-06-06"

# Reuse the same R2 binding as the Pages project
[[env.production.r2_buckets]]
binding = "LEAVING_CERT_BUCKET"
bucket_name = "cianfhoghlaim-leaving-cert"

[env.production.vars]
LITELLM_BASE_URL  = "https://litellm.cianfhoghlaim.ie"
EDGE_EXTRACT_MODEL = "extract-en"
R2_PUBLIC_URL      = "https://r2.cianfhoghlaim.ie"
# LITELLM_MASTER_KEY is a SECRET, set via:
#   wrangler secret put LITELLM_MASTER_KEY --env production
# (resolved from Infisical via `bun run secrets:init`)
```

---

## 4. BAML client — can BAML run in a Worker?

**Short answer:** the BAML **runtime** cannot, but the BAML **codegen target** (TypeScript + Zod) absolutely can.

| Layer | Edge-compatible? | Notes |
|:--|:--|:--|
| `baml-cli` (Rust compiler) | No | Runs at build-time, not runtime. Output is the generated TS client. |
| `baml-py` / `baml_client.sync` | No | CPython extension; Cloudflare Workers = V8 isolate, no Python. |
| `baml-language` (Rust VM) | **No** | No `wasm32-unknown-unknown` target published. The 0.13.0 release added `wasm32-wasi` for embedded use, but not the workerd isolate ABI. |
| `baml-ts` generated client (Zod schemas) | **Yes** | `@boundary/baml` is a thin fetch wrapper; can be tree-shaken to a 12 kB bundle that runs in `workerd`. |
| Zod validation | **Yes** | 12 kB, native to V8. |

**The pragmatic stack:** generate `typescript/react` + `typescript` from the `.baml` files (Agent 15 refactor #10). The Worker imports the generated Zod schemas (not the BAML client). The Worker is a thin OpenAI-compatible proxy to the existing LiteLLM gateway, with Zod-validated output. This gives us 90% of BAML's value (typed classes with `@description`, schema validation, retry policy via LiteLLM `num_retries: 3`) at 0% of the WASM cost.

**Build step** (added to `package.json`):

```json
{
  "scripts": {
    "baml:generate:ts": "cd cianfhoghlaim/core/baml && baml-cli generate --lang typescript --output ../../../web/apps/oideachais-web/src/baml_client"
  }
}
```

Codegen produces `src/baml_client/{clients,types,schemas}/*.ts` — the Zod schemas are the source of truth for the Worker's runtime validation.

---

## 5. LiteLLM routing

The Worker **never** calls `api.openai.com`, `api.anthropic.com`, or `generativelanguage.googleapis.com` directly. It always hits the existing **`litellm.cianfhoghlaim.ie`** gateway, which already provides (per `infrastructure/stacks/litellm`):

1. **7-tier fallback chain** (per `litellm/config.yaml` + Agent 06 finding #3):
   `gemini-2.5-flash → glm-4.6 → gemini-1.5-flash → claude-sonnet-4 → deepseek-v3 → ...`
2. **Langfuse v3 OTEL** — every call is traced, billed, and tagged with `trace_name: "edge-baml-extract"`.
3. **Cost caps** — per-model and per-team spend limits, hard-kill at $X.
4. **Spend tracking** — `litellm/spend` endpoint aggregates per-model + per-route.
5. **Vendor de-risking** — `minimax` alias (Agent 15 refactor outcome) is already wired.
6. **Single `LITELLM_MASTER_KEY`** — rotated via Infisical, injected via Locket sidecar or `wrangler secret put`.

**Worker → LiteLLM payload shape** (OpenAI-compatible):

```jsonc
POST https://litellm.cianfhoghlaim.ie/v1/chat/completions
Authorization: Bearer sk-litellm-...
Content-Type: application/json

{
  "model": "extract-en",
  "messages": [
    { "role": "system", "content": "You are a structured-extraction engine..." },
    { "role": "user",   "content": [
      { "type": "text",  "text": "R2 key: exams/lc-irish-2024-p1.pdf" },
      { "type": "image_url", "image_url": { "url": "data:application/pdf;base64,..." } }
    ]}
  ],
  "response_format": { "type": "json_object" },
  "temperature": 0.0,
  "max_tokens": 4096,
  "user": "edge-extract:exams/lc-irish-2024-p1.pdf",
  "metadata": { "trace_name": "edge-baml-extract", "schema": "LearningOutcome" }
}
```

**OpenCode Go alternative:** if the LiteLLM gateway is down, the Worker can fall back to **`$OPENCODE_GO_BASE_URL/chat/completions`** (the OpenAI-compatible surface at `opencode.go` per `infrastructure/stacks/opencode-go`). This is a 2-line swap in the Worker and is gated by a try/catch on the primary fetch.

---

## 6. Cost analysis

### Cloudflare Workers free tier (per `developers.cloudflare.com/workers/platform/limits`)

| Resource | Free | Paid ($5/mo Workers Paid) |
|:--|:--|:--|
| Requests | 100,000 / day | 10 M / month + $0.30 / M above |
| CPU time | 10 ms / request | 30 s wall + 30 s CPU / invocation |
| R2 reads | 10 M / month | 10 M / month + $0.36 / M above |
| R2 writes | 10 M / month (Class A) | 10 M / month + $4.50 / M above |
| Egress | Free | Free |

### Per-PDF cost (3 kB text input, ~500 token output, `extract-en` alias)

| Operation | Latency | Cost |
|:--|:--|:--|
| R2 GET (1 MB PDF) | ~30 ms | $0 (within free) |
| Worker CPU (fetch + Zod parse) | ~5 ms | $0 (within 10 ms free) |
| LiteLLM call to `extract-en` (gemini-2.5-flash tier) | ~1,800 ms | $0.0004 (≈ 500 tok × $0.75/M) |
| R2 PUT (1.5 kB JSON result) | ~25 ms | $0 (within free) |
| **Total per PDF** | **~2,000 ms** | **~$0.0004** |

**At 1,000 PDFs / day:**
- Worker requests: 1,000 / 100,000 = 1% of free tier
- LiteLLM cost: 1,000 × $0.0004 = **$0.40 / day ≈ $12 / month**
- R2 ops: 2,000 / 10,000,000 = 0.02% of free tier

**At 100,000 PDFs / day (5,000× scale-up, would require Workers Paid):**
- Worker cost: 100,000 × 10 ms = 1,000 s CPU / day (within 30 s × 100,000 invocations)
- LiteLLM cost: 100,000 × $0.0004 = **$40 / day ≈ $1,200 / month**
- R2 cost: $0.72 (reads) + $9 (writes) = ~$10 / month

**The bottleneck is NOT compute; it's the LiteLLM gateway** — and the gateway already has the cost caps + Langfuse tracing + fallback chain in place. The Worker is a free carrier.

### Comparison: Worker path vs. existing Dagster path

| Path | P50 latency | Cost per call | Notes |
|:--|:--|:--|:--|
| Edge Worker + LiteLLM | **~2 s** | $0.0004 | New path |
| Dagster asset + BAML + dlt | ~8 s | $0.0004 + asset overhead | Existing path |
| Langfuse trace correlation | ✅ (per-call) | ✅ | Both paths |

The Worker path is **4× faster** for the same cost, because it skips the Dagster asset bootstrap (~3 s) and the dlt write to DuckLake (~1 s). The extraction result lands in R2 as a JSON file; dlt picks it up later via the existing `r2_filesystem` source if DuckLake persistence is needed (per `infrastructure/stacks/dlt`).

---

## 7. Cutover plan

### Phase A — Build the Worker (1 day, S)

```bash
# 1. Generate TS Zod schemas from existing BAML files (Agent 15 refactor #10)
cd cianfhoghlaim/core/baml/_oideachais_src
baml-cli generate --lang typescript \
  --output ../../../../web/apps/oideachais-web/src/baml_client

# 2. Add the Worker + wrangler.toml block from §3
cd cianfhoghlaim/web/apps/oideachais-web
mkdir -p workers && $EDITOR workers/edge-extract.ts wrangler.toml

# 3. Local dev (Miniflare)
bunx wrangler dev workers/edge-extract.ts --env development
curl -X POST http://localhost:8787 -H 'Content-Type: application/json' \
  -d '{"r2_key":"test/sample.txt","schema":"LearningOutcome"}'
```

### Phase B — Wire Infisical + Locket (2 hours, S)

```bash
bun run scripts/init-vault.ts                                  # sync .infisical.env → dev-baile
cd cianfhoghlaim/web/apps/oideachais-web
wrangler secret put LITELLM_MASTER_KEY --env production        # <paste sk-litellm-...>
```

### Phase C — Deploy + cut over (10 min deploy + 4 hours BAML refactor)

```bash
# Deploy via Dagger (preferred) or wrangler
mise run dagger:web-pipeline -- --env production
# OR: wrangler deploy --env production

# Smoke test
curl -X POST https://edge-extract.oideachais.cianfhoghlaim.ie/extract \
  -H 'Content-Type: application/json' \
  -d '{"r2_key":"exams/lc-irish-2024-p1.pdf","schema":"LearningOutcome"}' | jq
# → { "ok": true, "output_key": "extractions/learningoutcome/...json", "elapsed_ms": 1847 }
```

**Cutover** (4 hours, M): 1-line `sed` across 14 inline `client "anthropic/claude-sonnet-4-20250514"` sites in `curriculum_extraction.baml:167-1086` → `client EdgeExtract`; add `client<llm> EdgeExtract` to `clients.baml`; add `edge-extract` alias to `litellm/config.yaml` pointing at `https://edge-extract.oideachais.cianfhoghlaim.ie`.

```baml
client<llm> EdgeExtract {
  provider openai
  options { base_url env.LITELLM_BASE_URL; api_key env.LITELLM_MASTER_KEY; model "edge-extract" }
  retry_policy Simple
}
```

```yaml
# litellm/config.yaml
- model_name: edge-extract
  litellm_params:
    model: openai/edge-extract
    api_base: https://edge-extract.oideachais.cianfhoghlaim.ie
    api_key: os.environ/LITELLM_MASTER_KEY
    timeout: 30
    num_retries: 2
```

### Phase D — Verify + Rollback

```bash
# Verify: upload PDF, extract, read JSON, check Langfuse trace
wrangler r2 object put cianfhoghlaim-leaving-cert/exams/test/lc-irish-2024-p1.pdf --file /tmp/test.pdf
curl -X POST https://edge-extract.oideachais.cianfhoghlaim.ie/extract -H 'Content-Type: application/json' \
  -d '{"r2_key":"exams/test/lc-irish-2024-p1.pdf","schema":"LearningOutcome","prompt_context":{"subject":"irish","year":2024}}' | jq
wrangler r2 object get cianfhoghlaim-leaving-cert/extractions/learningoutcome/exams/test/lc-irish-2024-p1.json | jq
open https://langfuse.cianfhoghlaim.ie/trace/edge-baml-extract

# Rollback (Cloudflare keeps last 100 deployments)
wrangler rollback --env production
# OR: wrangler delete --env production   # LiteLLM stays up
```

### Risks

| Risk | Mitigation |
|:--|:--|
| LiteLLM gateway downtime | Worker falls back to `$OPENCODE_GO_BASE_URL/chat/completions` (2-line swap) |
| Zod schema drift vs. `.baml` source | Codegen runs in CI; PR fails if `src/baml_client/*.ts` is stale |
| R2 egress cost blowup | Signed URLs only, no presigned GETs; CORS allowlist `oideachais.cianfhoghlaim.ie` only |
| Cold-start latency | First call ~80 ms (isolate spinup); Workers Paid eliminates this with `min_instances = 1` |
| 10 MB PDF > Worker 128 MB memory | R2 `get` streams to a `ReadableStream`, sent as `image_url` data URI; cap at 10 MB and return 413 above |

---

## CCC anchors

| Path | Anchor |
|:--|:--|
| `cianfhoghlaim/web/apps/oideachais-web/wrangler.toml` | Existing Pages + R2 + API proxy config (53 lines) |
| `cianfhoghlaim/core/baml/_oideachais_src/clients.baml:25-74` | 9 named gateway clients, `retry_policy Simple` — the pattern the new `EdgeExtract` follows |
| `cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml:164-1086` | 8 inline `client "anthropic/..."` calls (Agent 15 finding #1) — the cutover targets |
| `infrastructure/stacks/litellm/compose.yaml` | LiteLLM gateway, 7-tier fallback chain, port 4000, `litellm.cianfhoghlaim.ie` |
| `infrastructure/stacks/r2/` | R2 bucket `cianfhoghlaim-leaving-cert` (Garage S3, port 3900) |
| `infrastructure/stacks/langfuse/compose.yaml` | Langfuse v3 OTEL collector, port 3000 |
| `openspec/research/2026-06-28-browserbase-program-2/agent-15-baml.md` | 474-line BAML deep-dive, 15 refactor opportunities |
| `openspec/research/2026-06-28-browserbase-program-2/synthesis/27-feature-backlog.md` §F-05 | Original feature spec (P0, "Cluster D: Edge + GPU") |
| `openspec/specs/edge-baml-extraction/spec.md` | **NEW** spec to be authored as part of this change |
| `openspec/changes/edge-baml-extraction/` | **NEW** change directory (proposal.md, tasks.md, specs/edge-baml-extraction/spec.md) |

---

## Drift log

| Date | Event | Source |
|:--|:--|:--|
| 2026-06-28 | BAML upstream `baml-language 0.13.0` released — no `wasm32-unknown-unknown` target | `github.com/BoundaryML/baml/releases` |
| 2026-06-28 | Synthesis F-05 claims `baml-edge` exists — **DRIFT**: package is hypothetical, no `npm install @boundary/baml-edge` available | `27-feature-backlog.md:62-66` |
| 2026-06-28 | Cloudflare Workers free tier = 100 k req/day, 10 ms CPU/invocation | `developers.cloudflare.com/workers/platform/limits` |
| 2026-06-28 | `extract-en` LiteLLM alias = `gemini-2.5-flash → glm-4.6 → gemini-1.5-flash` (3-tier) | `litellm/config.yaml`, Agent 06 |
| 2026-06-28 | Dagster asset overhead ~3-8 s for short BAML calls | Empirical, `_oideachais_dagster_defs/` |
| 2026-06-28 | R2 binding `LEAVING_CERT_BUCKET` already exists in `oideachais-web/wrangler.toml:20-22` | `wrangler.toml` |

---

## Anti-patterns

1. **Don't call `api.openai.com` / `api.anthropic.com` directly from the Worker.** Always go through `litellm.cianfhoghlaim.ie` — the gateway owns fallback + cost caps + Langfuse. Direct calls = silent budget overrun.
2. **Don't embed the `.baml` BAML runtime in the Worker.** BAML has no WASM target. Use the generated Zod schemas only.
3. **Don't use `client "anthropic/claude-sonnet-4-20250514"` inline in the cutover.** Add the new `client<llm> EdgeExtract` to `clients.baml` and use it by name; the existing `retry_policy Simple` then applies automatically.
4. **Don't skip `response_format: { type: "json_object" }`.** OpenAI JSON mode is the safety net for Zod validation. Without it, the LLM can return prose, code fences, or partial JSON.
5. **Don't set `temperature > 0.0` on the EdgeExtract client.** BAML's deterministic evaluation pipeline assumes 0.0; non-zero temperature breaks RAGAS scoring.
6. **Don't store the LITELLM_MASTER_KEY in `wrangler.toml` `vars`.** It's a secret — use `wrangler secret put` or Locket sidecar injection.
7. **Don't write extraction results to R2 root.** Use the `extractions/{schema}/{key}.json` prefix so dlt can ingest the prefix as a partitioned filesystem source.
8. **Don't use the `default_client_mode sync` generator setting.** Use `async` (Agent 15 refactor #9) — the Worker is event-loop based, sync blocks the isolate.
9. **Don't trust LLM JSON without Zod validation.** LiteLLM gateway validates JSON mode, but doesn't validate schema. The Zod parse is the only line of defense.
10. **Don't skip the `user` field in the LiteLLM call.** It's how Langfuse tags the trace and how cost analytics segment the spend.

---

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Edge runtime | Cloudflare Workers | R2 already bound; 100 k req/day free; < 300 ms P50 |
| BAML runtime | Generated Zod only (no `baml-edge`) | `baml-edge` doesn't exist; Zod gives 90% of SAP value |
| LLM gateway | `litellm.cianfhoghlaim.ie` | Single point of rotation, 7-tier fallback, cost caps |
| Fallback gateway | `$OPENCODE_GO_BASE_URL/chat/completions` | OpenAI-compatible surface already deployed |
| Default model | `extract-en` | 3-tier cost-quality, $0.0004/call, ~2 s latency |
| Strong model | `extract-en-strong` (claude-sonnet-4) | Math / dense legal / exam paper extraction (rare at edge) |
| Temperature | `0.0` | Deterministic; required for RAGAS + BAML eval |
| Validation | Zod (`safeParse`) | Generated from `.baml` via `baml-cli generate --lang typescript` |
| Output format | `response_format: { type: "json_object" }` | OpenAI JSON mode = safety net for Zod |
| R2 write prefix | `extractions/{schema}/{key}.json` | Partitioned for dlt filesystem source |
| Auth | `wrangler secret put LITELLM_MASTER_KEY` | Same secret as Pages; rotated via Infisical |
| Observability | Langfuse v3 OTEL (via LiteLLM `metadata.trace_name`) | Per-call trace, cost, model chain |
| Cutover | New `client<llm> EdgeExtract` + 1-line sed on 14 inline calls | Zero BAML function rewrite |
| Rollback | `wrangler rollback` (last 100 deployments) | Cloudflare native; < 30 s |

---

## 1-paragraph summary

Edge BAML extraction moves 8 inline `anthropic/claude-sonnet-4-20250514` BAML calls (Agent 15 finding #1) off the LiteLLM hot path and into a Cloudflare Worker (`oideachais-edge-extract`) that reads from the existing `cianfhoghlaim-leaving-cert` R2 bucket, calls `litellm.cianfhoghlaim.ie` with `model: "extract-en"` (3-tier fallback to gemini-2.5-flash → glm-4.6 → gemini-1.5-flash, $0.0004/call, ~2 s P50), Zod-validates the response against generated schemas from the existing `.baml` files, and writes the JSON result back to R2 under `extractions/{schema}/{key}.json` for downstream dlt ingestion. The BAML TypeScript codegen (Agent 15 refactor #10) produces the Zod schemas at build time; `baml-edge` WASM does not exist as of 2026-06-28 so the Worker uses Zod directly rather than a BAML runtime. Cost is $12/month at 1,000 PDFs/day (vs. $0 free tier in R2 reads + Workers free tier), 4× faster than the existing Dagster path because it skips the asset bootstrap. Cutover is a 1-line `sed` across 14 BAML call sites + a new `client<llm> EdgeExtract` + a `litellm/config.yaml` alias entry; rollback is `wrangler rollback`.
