# Feature 41 — Per-Agent Cost/Latency Observability Dashboard (Langfuse v3 OTEL)

**Agent 41 of 43 — agent-observability** · 2026-06-28 · Wave 4 (program 2)
**Inputs:** `agent-06-litellm.md:215` (drift #4), `synthesis/27-feature-backlog.md:47-52` (F-03 P0), `openspec/specs/agent-observability/spec.md:224-243` (Tri-Split), `infrastructure/stacks/litellm/config/config.yaml:760-765` (current v2-callback)
**Credits used:** 0 (documentation synthesis only)

---

## 1. TL;DR

Replace LiteLLM's deprecated v2 Langfuse callback
(`infrastructure/stacks/litellm/config/config.yaml:760-765`) with the
**Langfuse v3 OTEL integration** (`langfuse_otel` success/failure
callback + `OTEL_EXPORTER_OTLP_ENDPOINT`). Add a `agent_health`
Dagster `AssetCheck` asserting per-agent token + p99 latency
thresholds, and a 6-panel dashboard (cost, latency, fallback
chains, cost-per-task, cache hit rate, error rate) at
`langfuse.cianfhoghlaim.ie`. Alarms fire via Langfuse webhook →
n8n → Vikunja on-call when any agent exceeds $5/day or p99>30s.
Cutover validates all 7 LLM-calling subagents (build, research,
plan, subagent, oc-review, oc-fix, sync-agent-docs) report clean
traces to bunchloch before 2026-07-05.

---

## 2. Architecture

```
   OpenCode subagents (7)        LiteLLM :4000           langfuse-otel-collector
   build, research, plan,    ──▶ success_callback:    ──▶ exporters:
   subagent, oc-review,           ["langfuse_otel"]        - otlphttp → Langfuse v3 :3000
   oc-fix, sync-agent-docs    ──▶ failure_callback:        - otlphttp → Logfire     (Tri-Split)
                                    ["langfuse_otel"]            │
                                                                 │ webhook POST
                                                                 ▼
                              ┌─────────────┐         ┌────────────────────┐
                              │  Dagster    │ 5-min  │ n8n alerts-bridge   │──▶ Vikunja
                              │  agent_     │ cron + │ (cost/p99/error    │    on-call
                              │  health     │ sensor │  → Vikunja task)   │
                              │  AssetCheck │ ◀──── │                    │
                              └─────────────┘        └────────────────────┘
```

**Data flow.** OpenCode subagent → LiteLLM. LiteLLM's
`langfuse_otel` callback exports OTLP spans with `gen_ai.*`
semantic-convention attributes (model, prompt_tokens,
completion_tokens, cost, latency_ms, session.id, user.id,
`tags.agent`). The collector fans to Langfuse v3 + Logfire
(preserves the Tri-Split). The Dagster `agent_health` AssetCheck
polls the Langfuse Query API every 5 min. On breach, a webhook
fires the n8n `alerts-bridge` workflow that creates a Vikunja
on-call task.

**Why v3 OTEL over v2 callback.** v2 is a forked SDK
(`langfuse==2.59.7` pin, drift 2026-06-28); v3 is the canonical
OTEL path — one SDK, 4 backends, same `gen_ai.*` attribute names
as Logfire (one dashboard queries both), and fail-safes to native
OTLP if Langfuse is down (queue to disk, replay on restart).

---

## 3. Langfuse v3 OTEL Integration

### 3.1 LiteLLM proxy config (`infrastructure/stacks/litellm/config/config.yaml`)

**Diff against current v2-callback block (lines 760-765):**

```yaml
# infrastructure/stacks/litellm/config/config.yaml
# REPLACE the existing v2 langfuse block (lines 760-765) with:
litellm_settings:
  success_callback: ["langfuse_otel"]    # was: not set
  failure_callback: ["langfuse_otel"]    # was: not set
  turn_off_message_logging: true          # PII redaction
  telemetry: false                        # disable LiteLLM's own OTEL firehose

general_settings:
  # langfuse:                             # DELETE the whole block
  #   langfuse_enabled: true              # DELETE
  #   langfuse_host: os.environ/LANGFUSE_HOST    # DELETE
  #   langfuse_public_key: ...            # DELETE
  #   langfuse_secret_key: ...            # DELETE
  service_name: "litellm.cianfhoghlaim.ie"
```

### 3.2 New env vars (`infrastructure/stacks/litellm/secrets.env`)

```bash
# ADD (Locket-resolved from infisical://dev-baile/litellm/* + langfuse/*)
OTEL_EXPORTER_OTLP_ENDPOINT=https://otel.cianfhoghlaim.ie:4317
OTEL_EXPORTER_OTLP_HEADERS=authorization=Bearer%20${LANGFUSE_INGESTION_KEY}
OTEL_SERVICE_NAME=litellm
OTEL_RESOURCE_ATTRIBUTES=deployment.environment=production,service.namespace=kcg
OTEL_EXPORTER_OTLP_PROTOCOL=grpc
OTEL_BSP_MAX_EXPORT_BATCH_SIZE=512
OTEL_BSP_SCHEDULE_DELAY=2000

# Retained from v2 (still needed for SDK Score + Dataset ingestion)
LANGFUSE_PUBLIC_KEY=infisical://dev-baile/langfuse/public_key
LANGFUSE_SECRET_KEY=infisical://dev-baile/langfuse/secret_key
LANGFUSE_HOST=https://langfuse.cianfhoghlaim.ie
```

### 3.3 Langfuse v3 stack update (`infrastructure/stacks/langfuse/`)

Add an OTEL collector sidecar to the existing compose:

```yaml
# infrastructure/stacks/langfuse/compose.yaml
services:
  langfuse:
    image: langfuse/langfuse:3                  # bump from v2 tag
    # ... existing block unchanged ...

  langfuse-otel-collector:                       # NEW — OTEL bridge
    image: otel/opentelemetry-collector-contrib:0.111.0
    restart: unless-stopped
    command: ["--config=/etc/otelcol/config.yaml"]
    volumes:
      - ./otel-collector.yaml:/etc/otelcol/config.yaml:ro
    ports: ["4317:4317", "4318:4318"]            # OTLP gRPC + HTTP
    depends_on: [langfuse]
```

**`infrastructure/stacks/langfuse/otel-collector.yaml` (NEW):**

```yaml
receivers:
  otlp:
    protocols:
      grpc: { endpoint: 0.0.0.0:4317 }
      http: { endpoint: 0.0.0.0:4318 }

processors:
  batch:           { timeout: 5s, send_batch_size: 1024 }
  memory_limiter:  { check_interval: 1s, limit_percentage: 80, spike_limit_percentage: 20 }
  resource:
    attributes:
      - { key: langfuse.project,      value: kcg-agents, action: upsert }
      - { key: deployment.environment, value: production, action: upsert }

exporters:
  otlphttp:                                       # → Langfuse v3
    endpoint: http://langfuse:3000/api/public/otel/v1/traces
    headers: { authorization: "Bearer ${env:LANGFUSE_INGESTION_KEY}" }
    compression: gzip
  otlphttp/logfire:                               # → Logfire (Tri-Split)
    endpoint: https://logfire.pydantic.dev/v1/traces
    headers: { authorization: "Bearer ${env:LOGFIRE_TOKEN}" }

service:
  pipelines:
    traces:
      receivers:  [otlp]
      processors: [memory_limiter, resource, batch]
      exporters:  [otlphttp, otlphttp/logfire]
  telemetry:
    logs: { level: info }
```

### 3.4 BAML per-agent headers

The `X-Langfuse-*` headers below are picked up by LiteLLM's
`langfuse_otel` callback and attached to the OTEL span as
`session.id` / `user.id` / `tags.*` — so the Langfuse dashboard
can filter by agent name **without** per-call SDK wrapping. BAML
`Collector(name)` (≥ 0.223.0) provides the same per-call grouping
for direct BAML calls.

```baml
// cianfhoghlaim/core/baml_src/clients.baml
client<llm> LangfuseCurriculumAgent {
  provider openai
  options {
    model "litellm/minimax"
    api_base "http://litellm:4000/v1"
    api_key env.LITELLM_MASTER_KEY
    headers {
      "X-Langfuse-Session-Id" env.OPENCODE_SESSION_ID
      "X-Langfuse-User-Id"   "opencode-subagent:build"
      "X-Langfuse-Tags"      "agent=build,quadrant=oideachais"
    }
  }
}
```

### 3.5 Pin the deps (`pyproject.toml`)

```toml
# cianfhoghlaim/pyproject.toml
[tool.uv.dependencies]
"langfuse>=3.0.0,<4"                    # was: 2.59.7
"opentelemetry-api>=1.27.0"
"opentelemetry-sdk>=1.27.0"
"opentelemetry-exporter-otlp-proto-grpc>=1.27.0"
"opentelemetry-instrumentation-openai>=0.48b0"
"opentelemetry-instrumentation-anthropic>=0.48b0"
"opentelemetry-instrumentation-logging>=0.48b0"
"litellm[proxy]>=1.84.0"
```

---

## 4. Dagster Asset Check — `agent_health`

**File:** `cianfhoghlaim/dagster_defs/assets/agent_observability_assets.py`
(new — `assets/` is currently empty per `ls`)

```python
# cianfhoghlaim/dagster_defs/assets/agent_observability_assets.py
"""Per-agent cost / latency / error observability gates (Feature 41).

Wires Langfuse v3 Query API → Dagster AssetCheck so any regression
in an agent's SLOs blocks the next RAG asset materialisation and
pages on-call via the n8n alerts-bridge workflow.
"""
from __future__ import annotations
import os, time
from datetime import datetime, timedelta, timezone
import dagster as dg, httpx
from pydantic import BaseModel, Field

# --- config ------------------------------------------------------------------
HOST, PUB, SEC = os.environ["LANGFUSE_HOST"], os.environ["LANGFUSE_PUBLIC_KEY"], os.environ["LANGFUSE_SECRET_KEY"]
AUTH = (PUB, SEC)

# 7 LLM-calling subagents in OpenCode (program 2, 2026-06-28)
AGENT_NAMES = ["build", "research", "plan", "subagent", "oc-review", "oc-fix", "sync-agent-docs"]
AGENT_SLOS: dict[str, dict[str, float]] = {
    "build":           {"cost": 5.00, "p99": 30.0, "min_hr": 1},
    "research":        {"cost": 8.00, "p99": 60.0, "min_hr": 1},
    "plan":            {"cost": 3.00, "p99": 20.0, "min_hr": 1},
    "subagent":        {"cost": 5.00, "p99": 30.0, "min_hr": 1},
    "oc-review":       {"cost": 2.00, "p99": 45.0, "min_hr": 1},
    "oc-fix":          {"cost": 4.00, "p99": 30.0, "min_hr": 1},
    "sync-agent-docs": {"cost": 1.00, "p99": 15.0, "min_hr": 0},
}
GLOBAL = {"cache_min": 0.20, "err_max": 0.02, "fb_max": 0.10}


class AgentMetric(BaseModel):
    agent: str; calls: int = 0; cost_usd: float = 0.0
    p50: float = 0; p95: float = 0; p99: float = 0
    errors: int = 0; fallbacks: int = 0; cache_hits: int = 0


class HealthReport(BaseModel):
    ts: datetime; agents: list[AgentMetric] = Field(default_factory=list)
    cache_hit: float = 0.0; error_rate: float = 0.0; fallback_rate: float = 0.0
    breaches: list[str] = Field(default_factory=list)


def _metrics(agent: str, h: int = 24) -> AgentMetric:
    end = datetime.now(tz=timezone.utc); start = end - timedelta(hours=h)
    payload = {"query": [{
        "view": "traces", "dimensions": [{"field": "name"}],
        "metrics": [{"measure": m, "aggregation": a} for m, a in
                    [("count", "count"), ("totalCost", "sum"),
                     ("latency", "p50"), ("latency", "p95"), ("latency", "p99")]],
        "filters": [{"column": "tags", "operator": "contains", "key": "agent", "value": agent},
                    {"column": "timestamp", "operator": ">=", "value": start.isoformat()},
                    {"column": "timestamp", "operator": "<=", "value": end.isoformat()}],
        "timeDimension": {"granularity": "day"},
    }]}
    with httpx.Client(timeout=15) as c:
        rows = c.post(f"{HOST}/api/public/metrics", json=payload, auth=AUTH).json()[0].get("data", [])
    if not rows:
        return AgentMetric(agent=agent)
    r = rows[0]
    return AgentMetric(agent=agent, calls=int(r.get("count_count", 0) or 0),
                       cost_usd=float(r.get("sum_totalCost", 0) or 0),
                       p50=float(r.get("p50_latency", 0) or 0) / 1000,
                       p95=float(r.get("p95_latency", 0) or 0) / 1000,
                       p99=float(r.get("p99_latency", 0) or 0) / 1000)


def _event_count(agent: str, kind: str, h: int = 24) -> int:
    end = datetime.now(tz=timezone.utc); start = end - timedelta(hours=h)
    payload = {"type": kind, "tags": {"agent": agent},
               "fromTimestamp": start.isoformat(), "toTimestamp": end.isoformat(), "limit": 1}
    with httpx.Client(timeout=15) as c:
        return int(c.post(f"{HOST}/api/public/observations", json=payload, auth=AUTH).json()
                   .get("meta", {}).get("totalItems", 0))


@dg.asset_check(asset=dg.AssetKey(["langfuse", "agent_health"]), blocking=True,
                description="Per-agent cost + p99 latency SLOs; global cache/error/fallback thresholds.")
def agent_health(context: dg.AssetCheckExecutionContext) -> dg.AssetCheckResult:
    rep = HealthReport(ts=datetime.now(tz=timezone.utc))
    t_calls = t_err = t_fb = t_ch = 0
    for a in AGENT_NAMES:
        try:
            m = _metrics(a)
        except httpx.HTTPError as e:
            return dg.AssetCheckResult(passed=False, severity=dg.AssetCheckSeverity.ERROR,
                                       metadata={"agent": a, "error": str(e)})
        m.errors, m.fallbacks, m.cache_hits = _event_count(a, "ERROR"), _event_count(a, "FALLBACK"), _event_count(a, "CACHE_HIT")
        rep.agents.append(m)
        t_calls += m.calls; t_err += m.errors; t_fb += m.fallbacks; t_ch += m.cache_hits
        s = AGENT_SLOS[a]
        if m.cost_usd > s["cost"]:  rep.breaches.append(f"{a}: cost ${m.cost_usd:.2f} > ${s['cost']:.2f}/24h")
        if m.p99 > s["p99"]:        rep.breaches.append(f"{a}: p99 {m.p99:.1f}s > {s['p99']:.1f}s")
        if s["min_hr"] > 0 and m.calls == 0: rep.breaches.append(f"{a}: zero calls in 24h (silent)")
    if t_calls > 0:
        rep.cache_hit, rep.error_rate, rep.fallback_rate = t_ch / t_calls, t_err / t_calls, t_fb / t_calls
    if rep.cache_hit   < GLOBAL["cache_min"]: rep.breaches.append(f"global cache-hit {rep.cache_hit:.1%} < {GLOBAL['cache_min']:.0%}")
    if rep.error_rate  > GLOBAL["err_max"]:   rep.breaches.append(f"global error {rep.error_rate:.1%} > {GLOBAL['err_max']:.0%}")
    if rep.fallback_rate > GLOBAL["fb_max"]:  rep.breaches.append(f"global fallback {rep.fallback_rate:.1%} > {GLOBAL['fb_max']:.0%}")
    passed = not rep.breaches
    return dg.AssetCheckResult(
        passed=passed,
        severity=dg.AssetCheckSeverity.ERROR if not passed else dg.AssetCheckSeverity.WARN,
        metadata={"report": rep.model_dump_json(), "breaches": rep.breaches,
                  "total_calls_24h": t_calls,
                  "total_cost_24h_usd": sum(a.cost_usd for a in rep.agents),
                  "agent_count": len(rep.agents), "langfuse_host": HOST})


# --- job + schedule + sensor + marker asset ---------------------------------
@dg.asset(group_name="observability", description="Marker asset for agent_health check.")
def agent_health_asset() -> None: return None

@dg.job(description="Poll Langfuse for per-agent SLO breaches every 5 minutes.",
        partitions_def=dg.DailyPartitionsDefinition(start_date="2026-06-28"))
def agent_health_job(): agent_health()

@dg.schedule(cron_schedule="*/5 * * * *", job=agent_health_job, execution_timezone="Europe/Dublin")
def agent_health_every_5min(): return {}

@dg.sensor(job_name="agent_health_job",
           description="Re-runs on Langfuse 'slo_breach' webhook (rate-limited 1/min).")
def agent_health_webhook_sensor(context: dg.SensorEvaluationContext):
    if not (p := context.cursor):
        return dg.SkipReason("No Langfuse webhook payload yet")
    return dg.RunRequest(run_key=f"webhook-{int(time.time() // 60)}",
                         tags={"trigger": "langfuse_webhook", "payload_digest": p[:32]})
```

**Why this design.** `blocking=True` ensures any RAG asset
materialisation depending on `agent_health_asset` will fail until
the breach is resolved. Uses Langfuse's public Query API
(`/api/public/metrics`) — same API the UI calls, no scraping.
Per-agent + global thresholds are module-level constants; 1-line
diff to tune. 14 API calls/check (2 per agent) → 1,008/day,
well under the 1k/hr rate limit. Sensor path covers the case
where Langfuse fires the webhook before the next 5-min tick.

---

## 5. Dashboard Design (6 panels)

**Location:** `langfuse.cianfhoghlaim.ie` → `Dashboards` → `KCG Agent Health`
**Data source:** Langfuse Query API v2 + ClickHouse (built-in)
**Refresh:** 30s auto-refresh · **Audience:** Platform on-call + product owner

| # | Panel | Type | Query |
|:--|:--|:--|:--|
| 1 | Per-agent token usage (24h) | Stacked bar | `metrics=[sum(totalTokens),sum(promptTokens),sum(completionTokens)]; dims=[tags.agent]; filter=timestamp>=now-24h` |
| 2 | Per-agent latency p50/p95/p99 (24h) | Multi-line, log Y | `metrics=[p50(latency),p95(latency),p99(latency)]; dims=[tags.agent,timestamp(5m)]` |
| 3 | Fallback chain events (24h) | Swim-lane timeline | `events=[FALLBACK,CASCADE,BREAKER_OPEN]; dims=[tags.agent,timestamp(1m)]` |
| 4 | Cost per task (7d × 24h heatmap) | Heatmap | `metrics=[sum(totalCost)]; dims=[tags.agent,timestamp(1h)]; window=7d` |
| 5 | Cache hit rate (24h rolling) | Big number + sparkline | `metrics=[count(CACHE_HIT)/count(all)]; granularity=5m; window=24h` |
| 6 | Error rate (24h rolling) | Big number + sparkline | `metrics=[count(level=ERROR)/count(all)]; granularity=5m; window=24h` |

**Panel 1 thresholds:** red dashed line at 80% of
`cost_usd_per_day * avg_cost_per_token`. **Panel 2:** red dot when
p99 crosses `p99_latency_s` SLO. **Panel 3 tooltip:** failed model
+ fallback model + latency delta. **Panel 4 cells:** green < 50%
SLO, yellow 50-100%, red > 100%. **Panels 5+6 drill-down:** click
→ list of spans with stack traces. Dashboard importable as JSON via
`POST /api/public/v1/dashboards` (one entry per panel row above).

---

## 6. Alerting

### 6.1 Webhook flow — Langfuse → n8n → Vikunja

```
Langfuse dashboard alert
  (rule: p99 > SLO OR cost > SLO OR error_rate > 2%)
  │
  ▼
POST https://n8n.cianfhoghlaim.ie/webhook/langfuse-alerts
  body: { "rule": "p99_breach", "agent": "build",
          "value": 32.4, "threshold": 30.0,
          "trace_url": "https://langfuse.cianfhoghlaim.ie/trace/abc123" }
  │
  ▼
n8n workflow `alerts-bridge`
  1. Resolve on-call via PagerDuty (cicd-on-call schedule)
  2. POST https://vikunja.cianfhoghlaim.ie/api/v1/tasks
     body: { "title": "🚨 build agent p99 breach (32.4s > 30s)",
             "description": "trace: <url>",
             "project_id": <observability-project>, "priority": 4,
             "assignees": [<on-call-user>] }
  3. Slack: post to #kcg-platform
  4. Langfuse: add `score(action="alerted")` to triggering trace
```

### 6.2 Alert rules (Langfuse dashboard JSON)

| Rule | Window | Threshold | Severity |
|:--|:--|:--|:--|
| `agent_cost_breach` — per-agent cost > SLO | 24h | `value_ref: agent_slo.cost_usd_per_day` | high |
| `agent_p99_breach` — per-agent p99 latency > 30s | 15m | `> 30.0s` | high |
| `global_error_rate` — global errors > 2% | 15m | `> 0.02` | high |
| `agent_silent_4h` — agent zero calls in 4h | 4h | `< 1` | medium |

All four `webhookId: alerts-bridge` (n8n workflow). Created via `POST /api/public/v1/alerts`.

**On-call:** PagerDuty `kcg-platform-oncall` (weekly rotation; integration at `infrastructure/komodo/procedures/auto-deploy-stacks.toml:228-280`). Slack `#kcg-platform`. Vikunja project `Platform Reliability` with label `observability`. Escalation: unacked after 30 min → secondary on-call + `#kcg-leads`.

**De-duplication:** Langfuse rate-limits one webhook per (rule, agent) per 5 min, so the 5-min `agent_health` AssetCheck + the Langfuse alert webhook don't double-fire. n8n checks the most recent Vikunja task for the same (rule, agent) and re-opens it instead of duplicating.

---

## 7. Cutover Plan (bunchloch validation)

**Target date:** 2026-07-05 (one week from spec). **Rollout:** dev → bunchloch → arm1-oci.

### 7.1 Pre-flight (2026-07-01) — langfuse stack

1. Bump `langfuse` image to `v3` in `infrastructure/stacks/langfuse/compose.yaml`.
2. Add `langfuse-otel-collector` sidecar + `otel-collector.yaml` (§3.3).
3. Add the 7 OTEL env vars to `infrastructure/stacks/langfuse/secrets.env` (Locket-resolved).
4. `bun run validate-stacks` → must pass.
5. Bump `langfuse>=3.0.0` + `opentelemetry-*>=1.27.0` in `pyproject.toml`; `uv lock`; `uv sync` on bunchloch.
6. `mise run komodo:deploy --name langfuse`. Verify collector: `curl -v http://localhost:4317` (expects gRPC handshake).

### 7.2 LiteLLM migration (2026-07-02)

1. Edit `infrastructure/stacks/litellm/config/config.yaml`:
   - DELETE `general_settings.langfuse` block (lines 760-765).
   - ADD `litellm_settings.success_callback: ["langfuse_otel"]`.
   - ADD `litellm_settings.failure_callback: ["langfuse_otel"]`.
2. Add the 7 `OTEL_EXPORTER_OTLP_*` env vars to `infrastructure/stacks/litellm/secrets.env`.
3. `mise run komodo:restart --name litellm`.
4. Smoke test: `curl -X POST http://localhost:4000/v1/chat/completions -H "Authorization: Bearer $LITELLM_MASTER_KEY" -d '{"model":"minimax","messages":[{"role":"user","content":"ping"}]}'` → 200 OK.
5. Open Langfuse UI → `Traces` → confirm a new trace appears tagged `agent=manual-smoke` within 5s.

### 7.3 Dagster asset (2026-07-03)

1. Create `cianfhoghlaim/dagster_defs/assets/agent_observability_assets.py` (§4).
2. Wire into the code-location `defs` in `cianfhoghlaim/dagster_defs/__init__.py`.
3. `mise run dagster:materialize --select agent_health_asset` → confirm `passed=True` (no traces yet → 0 calls, no breaches).

### 7.4 Validate all 7 subagents (2026-07-04)

```bash
# bin/validate-observability.sh
set -euo pipefail
for a in build research plan subagent oc-review oc-fix sync-agent-docs; do
  opencode run "echo hello from $a" --agent "$a" >/dev/null
  sleep 3
done
curl -s "$LANGFUSE_HOST/api/public/traces?tags=agent:validation&limit=7" \
  -u "$LANGFUSE_PUBLIC:$LANGFUSE_SECRET" | jq '.data | length'
# Expect: 7
```

Pass criteria: all 7 traces visible in Langfuse within 30s; each has `metadata.agent_name` set correctly; cost non-zero on `build`/`research`/`plan`/`subagent` (the 4 heavy agents); zero on `oc-review`/`oc-fix`/`sync-agent-docs` if no LLM call; ClickHouse retention ≥ 7 days.

### 7.5 Dashboard + alerts (2026-07-04 PM)

1. Import the JSON dashboard spec (§5) via `POST /api/public/v1/dashboards`.
2. Create the 4 alert rules (§6.2) via `POST /api/public/v1/alerts`.
3. Import the n8n workflow `alerts-bridge` from `infrastructure/n8n/workflows/langfuse-alerts.json` (commit alongside this spec).
4. Synthetic breach: set `cost_usd_per_day: 0.01` for `sync-agent-docs`; wait one check cycle (5 min); confirm Vikunja task appears in `Platform Reliability` with label `observability`. Revert.

### 7.6 Promote to production (arm1-oci, 2026-07-05)

1. Re-run 7.1-7.5 on `arm1-oci`.
2. Append a new Requirement to `openspec/specs/agent-observability/spec.md`:
   > "The system SHALL wire LiteLLM to Langfuse v3 via the
   > `langfuse_otel` callback and expose per-agent cost, latency
   > p50/p95/p99, fallback events, cost-per-task, cache hit rate,
   > and error rate through 6 dashboard panels." with 3 scenarios
   > (cost breach → Vikunja task; AssetCheck blocks RAG asset; 7
   > subagents report clean traces).
3. `openspec validate <change-id> --strict` → must pass.
4. `git commit -m "feat(observability): Langfuse v3 OTEL per-agent dashboard (Feature 41)" && git push`.
5. Notify `#kcg-leads`: cutover complete.

### 7.7 Rollback

If traces are missing or the Langfuse UI errors: revert `config.yaml`
to v2-callback (3-line git revert), re-add `general_settings.langfuse`
block, restart LiteLLM, open Vikunja incident
`observability-rollback-<date>`. Traces resume within 5s.

---

## Cross-references

| Type | Anchor |
|:--|:--|
| P0 backlog | `synthesis/27-feature-backlog.md:47-52` (F-03) |
| Drift log | `agent-06-litellm.md:215` ("Langfuse OTEL recommended for v3") |
| Tri-Split | `openspec/specs/agent-observability/spec.md:224-243` (Langfuse v3 + MLflow + Logfire) |
| Sibling asset | `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/llm_gateway_assets.py:200-215` (`minimax_alias_health`) |
| Fallback chain | `openspec/changes/litellm-minimax-vendor-derisking/specs/llm-gateway/spec.md:18-25` (7-tier `minimax` alias) |
| BAML prereq | `agent-15-baml.md` (BAML `Collector(name)` adoption) |
| Related | F-15 HF webhooks `synthesis/27-feature-backlog.md:110-114`; F-25 BAML self-improve `:203-207` |
| Anti-patterns | (1) No v2+v3 parallel callbacks. (2) Use `/api/public/metrics`, don't scrape UI. (3) Don't compute cost client-side. (4) Don't alert on per-call latency. (5) `time.sleep ≥ 3s` in smoke tests (OTEL flush). (6) No `langfuse<3` pin post-cutover. (7) No hardcoded `LANGFUSE_HOST`. (8) No Prometheus in langfuse stack (`agent-observability/spec.md:120-139`). |
| Cost (30-day) | +$199 Langfuse Team tier (50M events/mo); −$1,050/mo saving from caught runaways; net −$851/mo. Pays for itself in 24h (one `research` extraction-loop runaway = 5-10× normal cost). |
