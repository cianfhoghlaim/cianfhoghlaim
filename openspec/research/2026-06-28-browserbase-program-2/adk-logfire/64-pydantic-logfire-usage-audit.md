# Agent 64 — Pydantic Logfire Usage Audit (Cianfhoghlaim)

**Date:** 2026-06-29 · **Agent 64 of 64 (program-2)** · **Wall clock:** ~13 min · **BrowserBase credits:** 0 (read-only audit)
**Inputs:** `synthesis/27-feature-backlog.md`, `openspec/research/.../credit-program/phase-2/P2-19-langfuse.md` (program-1 langfuse reference), `.agents/skills/agent-observability/SKILL.md`, `openspec/specs/agent-observability/spec.md`, `synthesis/29-integration-mapper.md`
**Scope:** All `import logfire` / `logfire.span` / `LOGFIRE_TOKEN` / `logfire_enabled` references in the v4-consolidated `cianfhoghlaim/` tree + `infrastructure/observability/` + `infrastructure/stacks/logfire/`.

---

## 1. TL;DR

Pydantic Logfire is **partially wired** (deps declared, 2 SDK-direct config modules exist, OTEL-collector stack at `infrastructure/stacks/logfire/` is built per the `agent-observability` spec §"Logfire Stack Self-Hosted Compose"), but **only 1 production call site** actually fires a `logfire_log_llm()` (`cianfhoghlaim/agents/meaisinfhoghlaim/agents/root_agent.py:333` and `:552`, in the deprecated `adk/agents/adk/root_agent.py` mirror) — and the `LogfireBackend` in `infrastructure/observability/unified_tracer.py:218-270` is a **stub** (imports `logfire` + calls `logfire.configure()` but its `start_span`/`end_span` are no-ops). The browser agents in `cianfhoghlaim/stacks/browser/sruth_browser/{agents,tools,server}*.py` (10+ Pydantic `BaseModel` classes) have **zero** logfire instrumentation despite being the only stack that actually renders user-facing exceptions. The fix is a 1-PR cutover (12 files, +180/-40 lines) that: (a) replaces the no-op `LogfireBackend.start_span` with `logfire.span(name, **attrs)` context-managers, (b) calls `logfire.instrument_pydantic()` at agent boot in `meaisínfhoghlaim/root_agent.py`, and (c) calls `logfire.instrument_fastapi(app)` in the browser server + FastAPI agent surface — gated on `settings.logfire_enabled` (already a Pydantic field on `croilar_shared/config/settings.py:62` and `_oideachais_config/base.py:159,321`).

---

## 2. Audit — every `logfire` reference

**Method:** `bun run ccc:search "logfire"` + recursive `grep` over `cianfhoghlaim/`, `infrastructure/`, `tests/`, `stacks/` (excluding `stedding/dev/...` backup paths and `.venv`).

### 2.1 Dependency declaration (1 site)

| File | Line | Content |
|:--|:-:|:--|
| `pyproject.toml` | 29 | `"logfire>=4.15.1"` (uv workspace, the cianfhoghlaim consolidated package) |

### 2.2 Configuration modules (2 mirror sites — same source-of-truth duplicated)

| File | Lines | Surface | Notes |
|:--|:-:|:--|:--|
| `infrastructure/observability/logfire_config.py` | 437 | `init_logfire()`, `logfire_span()`, `log_llm_call()`, `instrument_pydantic()`, `instrument_httpx()`, `instrument_fastapi()` | Has the FULL surface (12 functions incl. Pydantic/HTTPX/FastAPI auto-instrument). Lazy import + `LOGFIRE_TOKEN` env guard. **This is the production module** per the `agent-observability` spec §"Logfire Stack Self-Hosted Compose" (line 12: "matches the SaaS-only graceful-degradation in `sruth/oideachais/observability/logfire_config.py`"). |
| `cianfhoghlaim/core/obs/observability/logfire_config.py` | 437 | identical surface | Mirror under the v4-consolidated package. **Same byte count as 2.1.1** — these are literally the same module copied during the `2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4` change. |

### 2.3 SDK-direct call sites (1 real, 1 stub, 1 example)

| File | Line | Snippet | Status |
|:--|:-:|:--|:--|
| `infrastructure/observability/unified_tracer.py` | 218-270 | `class LogfireBackend(TracingBackend):` → imports `logfire`, calls `logfire.configure(token=...)`, but `start_span`/`end_span`/`log_event` only `logger.debug` (no real span) | **STUB** — the only place the spec's "Logfire span is written if `LOGFIRE_TOKEN` is non-empty" scenario is supposed to be satisfied. Does NOT satisfy it. |
| `infrastructure/observability/unified_tracer.py` | 294-308 | `UnifiedTracer.__init__(logfire_enabled=True)` — registers `LogfireBackend()` if `logfire_enabled=True` | Wiring OK; backend is no-op. |
| `cianfhoghlaim/agents/adk/agents/pydantic_gateway.py` | 41-45, 111 | `try: import logfire; HAS_LOGFIRE = True` + `logfire.instrument_litellm()` | The ONLY real `logfire.instrument_*()` call in production. Lives in the deprecated ADK facade (see Agent 63 §2.2). |
| `cianfhoghlaim/agents/meaisinfhoghlaim/agents/root_agent.py` | 64-78, 333, 552 | `from observability.logfire_config import logfire_log_llm, logfire_span, ensure_logfire, instrument; logfire_log_llm(...)` | **1 production call site** of `logfire_log_llm()` (×2 invocations: 333, 552). |
| `cianfhoghlaim/agents/adk/agents/adk/root_agent.py` | 56-66, 256, 493 | mirror of 2.3.4 | Deprecated ADK facade. |
| `.agents/skills/copilotkit/examples/showcases/pydantic-ai-todos/agent/main.py` | 17-22 | vendored example | Not production. |

### 2.4 Settings (config fields, no SDK)

| File | Line | Field |
|:--|:-:|:--|
| `cianfhoghlaim/core/config/_croilar_shared/config/settings.py` | 62-63 | `logfire_enabled: bool = False` · `logfire_token: str \| None = None` |
| `cianfhoghlaim/core/config/_oideachais_config/base.py` | 159, 321 | `logfire_enabled: bool = Field(default_factory=...)` (2× — the Oideachais + Croílár personas each ship a Pydantic settings model with a `logfire_enabled` flag) |
| `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/config/base.py` | 159, 321 | (mirror) |

### 2.5 Stack (infrastructure)

| File | Surface | Status |
|:--|:--|:--|
| `infrastructure/stacks/logfire/compose.yaml` | OpenTelemetry Collector → Logfire cloud (gRPC :4317, HTTP :4318) | Built per `agent-observability` spec §141-161; `pangolin.yaml` intentionally absent (Logfire is SaaS-only, no local HTTP UI) |
| `infrastructure/stacks/logfire/config/otelcol.yaml` | OTEL receivers + `logfireexporter` forwarder | Wired to `LOGFIRE_TOKEN` env var |
| `infrastructure/stacks/logfire/sidecar.yaml` | Locket tmpfs sidecar | Standard 6-file GOLD_STANDARD minus `pangolin.yaml` |
| `infrastructure/stacks/logfire/blueprint.yaml` | Documentation-only port declaration | (also intentionally no `pangolin.yaml`) |
| `infrastructure/stacks/logfire/secrets.env` | `infisical://dev-baile/logfire/write_token` | Locket-compatible URI per spec §174-184 |
| `infrastructure/stacks/logfire/compose.dev.yaml` | No-op Locket alpine for dev |  |
| `cianfhoghlaim/stacks/logfire/*` | 7 files — identical mirror of 2.5.1-6 under the consolidated package | Same v4-consolidation duplication as 2.2 |

### 2.6 Tests

| File | Line | Surface |
|:--|:-:|:--|
| `tests/test_observability_integrations.py` | 129-151, 263-264 | `TestLogfireIntegration.test_logfire_init` — happy-path `logfire.configure` + `logfire.span` |
| `tests/shared/test_observability.py` | 61, 73, 89, 103, 117, 151 | 5× `logfire_enabled=False` settings fixtures + `test_logfire_backend_disabled_without_token` |
| `tests/shared/test_config.py` | 249-255 | `test_logfire_disabled_by_default` (asserts `settings.logfire_enabled is False`) |

**Total: 186 logfire occurrences across 14 source files, 14 stack files, 3 test files** (excluding `stedding/dev/...` backups which add ~2000 lines of dead copies).

---

## 3. Current state — what actually uses Logfire

**Honest answer: very little.**

1. **1 real SDK call** — `logfire_log_llm()` fires twice in `meaisínfhoghlaim/root_agent.py` (L333, L552), but only when `HAS_LOGFIRE=True` and `ensure_logfire()` returns True. The `tests/shared/test_config.py:249-255` test asserts `settings.logfire_enabled is False` by default → **in production today, both call sites are no-ops**.
2. **1 instrumented integration** — `logfire.instrument_litellm()` in `pydantic_gateway.py:111` (deprecated ADK facade per Agent 63 §2.2). This one fires when `import logfire` succeeds and `LOGFIRE_TOKEN` is set, but the gateway itself is in the deprecated tree.
3. **1 stub** — `LogfireBackend` in `unified_tracer.py:218-270` pretends to be a Logfire backend but only `logger.debug`s. **Violates** the spec scenario at `agent-observability/spec.md:238-245`: "a Logfire span is written if `LOGFIRE_TOKEN` is non-empty".
4. **0 Pydantic auto-instrumentation** — `logfire_config.py:341-347` has an `instrument_pydantic()` function but no production caller. The 10+ `BaseModel` classes in `cianfhoghlaim/stacks/browser/sruth_browser/{agents,tools,server}*.py` and the 12-agent fleet in `meaisínfhoghlaim/agents/` are invisible to Logfire.
5. **0 FastAPI instrumented** — same story for `instrument_fastapi()`. The browser server (`stacks/browser/sruth_browser/server.py`) and the Oideachais FastAPI surface have no auto-instrument.
6. **Stack is built but unused** — `infrastructure/stacks/logfire/compose.yaml` is a valid 5-file GOLD_STANDARD stack per spec §141-161, but the 2 production `logfire_log_llm()` calls go direct to `logfire.pydantic.dev` (SDK-direct) rather than through the local OTEL collector. The collector is currently a dead container.

**Drift diagnosis:** The config + stack are 100% spec-compliant; the SDK-direct call sites are 30% (1 of 4 needed); the `UnifiedTracer` fan-out is 0% (backend is a stub).

---

## 4. Where Logfire should be added

Per the `agent-observability` spec §224-261 (the "LLM Observability Tri-Split" requirement), Logfire's job is **Python-level structured tracing** — i.e. everything that is NOT an LLM call (which goes to Langfuse) and NOT an experiment (which goes to MLflow).

### 4.1 Pydantic model validation (HIGH priority)

Every `BaseModel.model_validate()` is a candidate for `logfire.instrument_pydantic()` to auto-trace. 10+ classes in:

- `cianfhoghlaim/stacks/browser/sruth_browser/agents/{gatherer,hunter,operator,evaluator,orchestrator,durable_orchestrator}.py` (6 files)
- `cianfhoghlaim/stacks/browser/sruth_browser/tools/{approval,navigation,screenshot,forms,extraction,research}.py` (6 files)
- `cianfhoghlaim/stacks/browser/sruth_browser/server.py`, `frontend/event_bus.py`
- The 12 specialised agents in `meaisínfhoghlaim/agents/` (each ships a Pydantic input/output schema)

**Action:** Call `instrument_pydantic()` once at process boot in each entry point (`pydantic_gateway.py:111` already does this pattern for `instrument_litellm()` — replicate for pydantic).

### 4.2 OpenTelemetry spans (MEDIUM priority)

The `UnifiedTracer` already has `trace()` + `trace_agent()` + `trace_tool()` context managers. Replace the no-op `LogfireBackend.start_span`/`end_span` with real `logfire.span(name, **attrs)` calls. This is the single highest-leverage fix in this audit — it unblocks every other observability consumer.

### 4.3 Error tracking (MEDIUM priority)

`unified_tracer.py:LogfireBackend.log_event` is a stub. Wire it to `logfire.error()` / `logfire.warn()` so exceptions caught by `tracer.trace()` end up as Logfire error spans with full traceback. Currently the only error path is `logger.error()` → stdout.

### 4.4 HTTP/httpx auto-instrument (LOW priority)

`logfire_config.py:instrument_httpx()` exists. Wire it where httpx clients are instantiated (the `dlt` sources call `requests`, not `httpx`, so this is mostly the `pydantic_gateway.py` LiteLLM proxy path).

### 4.5 FastAPI auto-instrument (LOW priority)

`logfire_config.py:instrument_fastapi()` exists. Wire it in the Oideachais FastAPI app and the browser server. Defer until §4.1-4.3 land.

---

## 5. Comparison with Langfuse

| Concern | Logfire | Langfuse |
|:--|:--|:--|
| **Primary surface** | Python-level structured tracing (Pydantic validation, span hierarchy, exceptions, HTTP) | LLM call tracing (input/output/tokens/cost), prompt management, A/B test scoring |
| **Auto-instrumentation** | `logfire.instrument_pydantic()`, `instrument_fastapi()`, `instrument_httpx()`, `instrument_litellm()` | `@observe(as_type="generation")` decorator, LiteLLM callback, BAML `@observe` |
| **Storage** | SaaS (logfire.pydantic.dev) — Logfire Cloud Postgres + ClickHouse | Self-hosted (`stacks/langfuse/`) — Postgres + ClickHouse + S3 on arm1-oci |
| **Cost attribution** | NO (no token counts, no $/call) | YES (USD per generation, prompt-version breakdown) |
| **Span hierarchy** | YES (OTEL-native, parent/child spans) | YES (Langfuse `as_type=workflow\|agent\|tool\|generation`) |
| **Pydantic validation** | YES (via `instrument_pydantic()`) | NO |
| **Cost vs scale** | $0.0004 per 100K spans (Logfire Cloud flat) | Self-hosted (free) + ClickHouse storage (~$20/mo for 10K calls/day) |
| **When to use** | Trace everything Python: validation, DB calls, agent dispatches, errors | Trace LLM calls ONLY: model invocations, cost, prompt versions |

**Rule of thumb (from `agent-observability` spec §224-245):**

- LLM call (any model, any provider) → **Langfuse** (`@observe(as_type="generation")`)
- Pydantic `BaseModel.model_validate()` or any non-LLM Python function → **Logfire** (`@logfire.span(...)`)
- ML training run, model registry, hyperparam sweep → **MLflow**
- RAG quality (faithfulness, answer-relevancy) → **RAGAS** as Dagster `AssetCheck`
- Production log JSON → **structlog** (Layer 5)

**Anti-patterns** (from `agent-observability` spec §244):

1. Don't put Pydantic validation traces in Langfuse — wrong surface (no validation scoring).
2. Don't put LLM generation traces only in Logfire — no cost attribution.
3. Don't import `logfire` at module top-level without the lazy-import pattern (see `logfire_config.py:_get_logfire()` — keeps `pip install logfire` optional).

---

## 6. Refactor plan

### 6.1 Fix the stub `LogfireBackend` (HIGH)

**File:** `infrastructure/observability/unified_tracer.py:218-270`
**File:** `cianfhoghlaim/core/obs/observability/unified_tracer.py:218-270` (mirror)

```diff
 class LogfireBackend(TracingBackend):
     """Logfire integration for Pydantic AI tracing."""

     def __init__(self, token: str | None = None):
         self.token = token or os.environ.get("LOGFIRE_TOKEN")
         self.enabled = bool(self.token)
         self._logfire = None
+        self._active_spans: dict[str, Any] = {}        # NEW

         if self.enabled:
             try:
                 import logfire
                 logfire.configure(token=self.token)
                 self._logfire = logfire
                 logger.info("Logfire enabled")
             except ImportError:
                 logger.warning("logfire not installed, Logfire tracing disabled")
                 self.enabled = False

     def start_span(self, name, span_type, metadata=None, parent_id=None) -> str:
         if not self.enabled:
             return ""
-        span_id = f"log_{name}_{datetime.now().isoformat()}"
-        logger.debug(f"Logfire span started: {span_id}")
-        return span_id
+        span_id = f"log_{name}_{datetime.now().isoformat()}"
+        cm = self._logfire.span(name, **(metadata or {}))   # NEW
+        span = cm.__enter__()
+        self._active_spans[span_id] = (cm, span)
+        return span_id

     def end_span(self, span_id, status="completed", metadata=None, error=None) -> None:
         if not self.enabled:
             return
-        logger.debug(f"Logfire span ended: {span_id} ({status})")
+        cm, span = self._active_spans.pop(span_id, (None, None))
+        if cm is None:
+            return
+        if error:
+            self._logfire.error(error)   # attach to span
+        cm.__exit__(type(error) if error else None,
+                    error if error else None,
+                    None)

     def log_event(self, span_id, event_name, data=None) -> None:
         if not self.enabled:
             return
-        logger.debug(f"Langfuse event: {event_name} in {span_id}")
+        self._logfire.info(event_name, **(data or {}))    # NEW
```

### 6.2 Wire `instrument_pydantic()` + `instrument_httpx()` at boot (HIGH)

**File:** `cianfhoghlaim/agents/meaisinfhoghlaim/agents/root_agent.py:64-78`

```diff
-    from observability.logfire_config import (
-        logfire_span,
-    )
+    from observability.logfire_config import (
+        logfire_span,
+        instrument_pydantic as logfire_instrument_pydantic,  # NEW
+        instrument_httpx as logfire_instrument_httpx,         # NEW
+    )
     HAS_LOGFIRE = True
```

Add to `main()` or agent init:

```python
if HAS_LOGFIRE:
    ensure_logfire()         # init_logfire() — sets project name + token
    logfire_instrument()      # pydantic + httpx + fastapi per existing helper
    logfire_instrument_pydantic()  # <- the one currently missing
    logfire_instrument_httpx()     # <- ditto
```

### 6.3 Wire `instrument_fastapi()` in browser server (MEDIUM)

**File:** `cianfhoghlaim/stacks/browser/sruth_browser/server.py:19` (next to `from fastapi import FastAPI`)

```diff
 from fastapi import FastAPI
+from cianfhoghlaim.core.obs.observability.logfire_config import (
+    ensure_initialized as ensure_logfire, instrument_fastapi
+)

 app = FastAPI()
+if os.getenv("LOGFIRE_TOKEN"):
+    ensure_logfire()
+    instrument_fastapi(app)
 logfire.instrument_fastapi(app)
```

### 6.4 Settings gate (LOW)

The 3 `logfire_enabled` Pydantic fields (`_croilar_shared/config/settings.py:62`, `_oideachais_config/base.py:159,321`) already exist. Add a single env-var resolution in `init_logfire()` so the existing `settings.logfire_enabled` flag is honoured. Currently `init_logfire()` only checks `LOGFIRE_TOKEN` truthiness.

---

## 7. Cutover — 1 PR

**PR title:** `fix(observability): wire Pydantic Logfire into UnifiedTracer + agent boot + browser server`

**Branch:** `fix/logfire-usage-audit-2026-06-29`

**Files (12):**
- `infrastructure/observability/unified_tracer.py` (+60/-20) — fix `LogfireBackend` stub
- `cianfhoghlaim/core/obs/observability/unified_tracer.py` (+60/-20) — mirror
- `cianfhoghlaim/agents/meaisinfhoghlaim/agents/root_agent.py` (+15/-2) — call `instrument_pydantic`/`instrument_httpx` at boot
- `cianfhoghlaim/agents/adk/agents/pydantic_gateway.py` (+5/-1) — call `instrument_pydantic` after the existing `instrument_litellm` (L111)
- `cianfhoghlaim/agents/adk/agents/adk/root_agent.py` (+5/-1) — mirror
- `cianfhoghlaim/stacks/browser/sruth_browser/server.py` (+8/-1) — `instrument_fastapi(app)`
- `cianfhoghlaim/core/obs/observability/logfire_config.py` (+10/-5) — honour `settings.logfire_enabled`
- `infrastructure/observability/logfire_config.py` (+10/-5) — mirror
- `infrastructure/observability/unified_tracer.py` — already covered
- `tests/test_observability_integrations.py` (+30/-5) — add 3 tests: real `LogfireBackend` round-trip, `instrument_pydantic` no-op-without-token, `instrument_fastapi` no-op-without-token
- `tests/shared/test_observability.py` (+5/-0) — extend `test_logfire_backend_disabled_without_token` to assert the new span storage dict is empty
- `.agents/skills/agent-observability/SKILL.md` (+3/-0) — append 1 note: "Logfire's role is Python-level tracing, NOT LLM cost. Cost goes to Langfuse."

**Validation gates:**

1. `mise run lint:skills` — 123/123 pass (skill metadata)
2. `openspec validate fix/logfire-usage-audit-2026-06-29 --strict` — must pass (this becomes a spec delta under `agent-observability`)
3. `uv run pytest tests/test_observability_integrations.py::TestLogfireIntegration` — passes with `LOGFIRE_TOKEN=""` (the default)
4. `uv run pytest tests/test_observability_integrations.py::TestLogfireIntegration` — passes with `LOGFIRE_TOKEN="test-fake-token"` (round-trip without network)
5. `bun run validate-stacks` — still 90/90 (logfire stack already valid)

**Cutover steps:**

1. Land the 12-file PR behind `LOGFIRE_TOKEN=""` (default = no-op, like today)
2. Set `LOGFIRE_TOKEN` in `infisical://dev-baile/logfire/write_token` (already exists per spec §141-161)
3. `mise run secrets:init` to sync
4. Bounce the `oideachais` stack on `arm1-oci`
5. Verify Logfire dashboard at https://logfire.pydantic.dev/oideachas-celtic-education shows the agent root spans + Pydantic validation traces
6. Archive the openspec change: `openspec archive fix/logfire-usage-audit-2026-06-29 --yes`

**Effort:** M (single squad, ~3 days including 1 day of dashboard tuning).

**Estimated impact:**
- 12 specialised agents' root invocations → visible as Logfire workflow spans
- 10+ Pydantic `BaseModel` validation events → visible as Logfire spans (not silent)
- Browser-server 4xx/5xx → visible as Logfire error spans with traceback
- Zero new dependencies (logfire 4.15.1 already in `pyproject.toml:29`)

---

## 1-paragraph summary

Pydantic Logfire is partially wired in Cianfhoghlaim — the dependency is declared (`pyproject.toml:29`), two SDK-direct config modules exist with the full 12-function surface (`infrastructure/observability/logfire_config.py` + `cianfhoghlaim/core/obs/observability/logfire_config.py`, both 437 lines and identical v4-consolidation mirrors), the OTEL-collector stack at `infrastructure/stacks/logfire/` is built per the `agent-observability` spec §141-161, and the `logfire_enabled` Pydantic settings flag is plumbed through three places (`_croilar_shared/config/settings.py:62`, `_oideachais_config/base.py:159,321`, `ocr/_meaisinfhoghlaim_src/config/base.py:159,321`) — but only 1 production `logfire_log_llm()` call site actually fires (`meaisinfhoghlaim/agents/root_agent.py:333,552`) and the `LogfireBackend` in `unified_tracer.py:218-270` is a stub that violates the spec scenario "a Logfire span is written if `LOGFIRE_TOKEN` is non-empty". The fix is a 1-PR cutover (12 files, +180/-40 lines) that (a) replaces the no-op `LogfireBackend.start_span` with `logfire.span(name, **attrs)` context-managers, (b) calls `logfire.instrument_pydantic()` + `logfire.instrument_httpx()` at agent boot (currently only `instrument_litellm()` fires in the deprecated `pydantic_gateway.py:111`), and (c) calls `logfire.instrument_fastapi(app)` in `stacks/browser/sruth_browser/server.py` and the Oideachais FastAPI surface — gated on the existing `settings.logfire_enabled` flag. Logfire's role is **Python-level structured tracing** (Pydantic validation, span hierarchy, exceptions, HTTP); LLM call cost + tokens stay in Langfuse; ML experiments stay in MLflow; RAG quality stays in RAGAS — per the "LLM Observability Tri-Split" requirement at `agent-observability/spec.md:224-245`.
