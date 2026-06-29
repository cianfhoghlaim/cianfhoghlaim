# Agent 63 — Google ADK Usage Audit (Cianfhoghlaim)

**Date:** 2026-06-29 · **Agent 63 of 63 (program-2)** · **Wall clock:** ~12 min · **BrowserBase credits:** 0 (read-only audit)
**Inputs:** `synthesis/27-feature-backlog.md`, `synthesis/26-refactor-prioritizer.md`, `openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md`, `agent-06-litellm.md`, `SHARED_DISCOVERY_LOG.md`, `openspec/research/.../30-documentation-gaps.md`
**Scope:** All `import google.adk` / `from google.adk` references in v4-consolidated `cianfhoghlaim/`.

---

## 1. TL;DR

Google ADK is in **active use** by 5 specialised agents in `meaisínfhoghlaim/agents/` (32 `LlmAgent`, 3 `SequentialAgent`, 2 `LoopAgent`, 1 custom `BaseAgent`, 6 `BuiltInPlanner`) plus 22 more `LlmAgent` in the deprecated `adk/agents/adk/` mirror facade, plus a 7-file browser tool surface. **Every single `LlmAgent(model=config.model_name)` constructor hardcodes `model_name="gemini-2.0-flash"` and routes directly to Google's native Gemini API via `GOOGLE_API_KEY` — this BYPASSES the LiteLLM `minimax` 7-tier fallback alias** (P0-#1 in `agent-06-litellm.md`). ADK 1.5+ ships `from google.adk.models.lite_llm import LiteLlm`, making the LiteLLM wire-up a 1-line swap per agent. Recommended: 1 PR (12 files, +25/-5 lines) that replaces `model="gemini-2.0-flash"` with `LiteLlm(model="minimax", api_base=...)` across the 5+ agents, gated on the existing `minimax_alias_health` Dagster asset check (`llm_gateway_assets.py:200-215`).

---

## 2. Audit — every `import google.adk` reference

**Method:** `bun run ccc:v1:search "google.adk"` + recursive `grep` over `cianfhoghlaim/` (excluding `.agents/skills_backup/` + `copilotkit/examples/` which are vendored docs).

### 2.1 `meaisínfhoghlaim/agents/` — 8 files, 28 LlmAgent sites

| File | LlmAgent | Other ADK | Notes |
|:--|:-:|:--|:--|
| `research_agent.py` | 4 | `SequentialAgent` (L194), `LoopAgent` (L185) | planner→loop→composer research pipeline |
| `education_research_agent.py` | 7 | `SequentialAgent` (L237), `LoopAgent` (L242), `BaseAgent` `ResearchEscalationChecker` (L51) | Deep research + custom escalation |
| `bunchloch_research_agent.py` | 4 | `SequentialAgent` (L455) | Hunter→Gatherer→Analyst (migrated Agno→ADK) |
| `curriculum_comparison_agent.py` | 5 | `BuiltInPlanner` (5 sites) | 5 specialised sub-agents + planner |
| `statistics_agent.py` | 5 | `BuiltInPlanner` (L11) | Nation-comparison |
| `geospatial_agent.py` | 5 | `BuiltInPlanner` (L11) | 5 spatial sub-agents |
| `agui_curriculum_agent.py` | 2 | `BuiltInPlanner` (L20) | AG-UI streaming facade |
| `callbacks/citation_callbacks.py` | 0 | `CallbackContext` (L11) | Cross-cutting citation callback |

### 2.2 `adk/agents/adk/` (deprecated ADK facade, still deployed)

14 files, ~22 `LlmAgent` mirror of meaisínfhoghlaim + 4 tuatha/MMO agents:
- `curriculum_comparison_agent.py`, `statistics_agent.py`, `bunchloch_research_agent.py`, `research_assistant_agent.py`, `quest_guide_agent.py`, `mythology_narrator_agent.py`, `celtic_tutor_agent.py` — `LlmAgent` + `FunctionTool`
- `tuatha_root_agent.py:10-11` — `LlmAgent` + `from google.adk.apps.app import App` (A2A Protocol)
- `callbacks/citation_callbacks.py:11` — `CallbackContext`
- `tools/{curriculum_search,spatial_query,statistics_query}.py` — `ToolContext`

### 2.3 `core/browser/sruth_browser/` + `stacks/browser/sruth_browser/` (mirror-tree duplication)

7 files import `from google.adk.tools import FunctionTool`:
- `agents/{gatherer,hunter,operator,evaluator}.py` — `LlmAgent` + `FunctionTool`
- `agents/orchestrator.py:10-14` — `BaseAgent, LlmAgent, LoopAgent, SequentialAgent, FunctionTool, AgentTool, InvocationContext, Event, EventActions` (custom orchestration)
- `agents/durable_orchestrator.py:18-21` — `BaseAgent` + `InvocationContext, Event, EventActions`
- `tools/{research,forms,extraction,approval,navigation,screenshot}.py` — `FunctionTool`
- `adapters/registry.py:385` — dynamic `from google.adk.tools import FunctionTool`

### 2.4 `infrastructure/stacks/oideachais/compose.yaml:278-291`

```yaml
# ADK AGENTS (Google ADK) - Multi-agent orchestrator (port 7778)
adk_agents:
  image: oideachais-dev-adk-agents:latest
  ports: ["7778:7778"]
  environment: [GOOGLE_API_KEY, LANCEDB_URI, NEO4J_URI]   # ← bypass env, no LITELLM_API_BASE
  depends_on: [lakehouse, litellm]
```

`openspec/changes/oideachais-agent-services/proposal.md:97-124` documents the `adk_agents` container image and explicitly wires `GOOGLE_API_KEY` (NOT `OPENAI_BASE_URL`/`LITELLM_API_KEY`).

### 2.5 Pyproject / lockfile evidence

`_oideachais_pyproject.toml`, `_tuatha_pyproject.toml`, `_meaisinfhoghlaim_pyproject.toml` all pin `google-adk>=1.0.0`; `stacks/browser/pyproject.toml` + `core/browser/pyproject.toml` pin `google-adk` for browser tools. **No `langfuse` or `litellm` direct dep** in any of these — ADK agents emit no traces unless Langfuse is wired at the LiteLLM side (which today they don't go through).

### 2.6 Spec cross-references

- `openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md:34-35, 66-69` — Research Agent uses "Google ADK SequentialAgent" + spec mandates "Agno (>=2.0.0) + Google ADK (>=1.0.0) + LiteLLM"
- `openspec/specs/agentic-frontend-frameworks/spec.md` — `google-adk` listed as framework dep
- `openspec/research/.../30-documentation-gaps.md:59` — `google-adk/SKILL.md` is PASS (no gaps flagged)

---

## 3. Current state — what 3 (actually 5+) agents do

### 3.1 The 3 agent-06 references

`agent-06-litellm.md` finding #1 names **3 ADK agents** that bypass the LiteLLM gateway. Per `spec.md:34` + `__init__.py:14-21`:

| # | Agent | File:line | What it does |
|:-:|:--|:--|:--|
| 1 | **Research Agent** | `meaisínfhoghlaim/agents/research_agent.py:194` | `SequentialAgent` (planner→`LoopAgent`(researcher, evaluator)→composer) for Celtic education deep research with citations |
| 2 | **Education Research Agent** | `meaisínfhoghlaim/agents/education_research_agent.py:237` | `SequentialAgent` with `LoopAgent` + custom `BaseAgent` `ResearchEscalationChecker` (L51) for escalation |
| 3 | **Bunchloch Research Agent** | `meaisínfhoghlaim/agents/bunchloch_research_agent.py:455` | `SequentialAgent` (Hunter→Gatherer→Analyst) over `bunchloch` local academic collection |

### 3.2 The 5+ ADK agents actually in the fleet

Per `__init__.py:1-27`, the ADK section also lists `RootAgent`, `CurriculumAgent`, `GeospatialAgent`, `TranslationAgent`, `CorpusAgent`, `StatisticsAgent`. Counting active `LlmAgent` imports gives **32 `LlmAgent` instances** across 5+ files (research 4, education_research 7, bunchloch 4, curriculum_comparison 5, statistics 5, geospatial 5, agui_curriculum 2).

`mcp_curriculum_agent.py`, `corpus_agent.py`, `curriculum_agent.py`, `root_agent.py`, `translation_agent.py`, `voice_agent.py` do **NOT** use ADK (use Agno or MCP directly).

### 3.3 The actual current state (the bypass)

Every `LlmAgent(...)` constructor passes `model=config.model_name`, where `config.model_name = "gemini-2.0-flash"` (`agents/config.py:18`):

```python
# cianfhoghlaim/agents/meaisinfhoghlaim/agents/config.py:18
model_name: str = "gemini-2.0-flash"
# agents/config.py:61-63
google_api_key: str | None = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))
```

Implications:
1. LLM call goes to `https://generativelanguage.googleapis.com/...` directly via the `google-genai` SDK
2. **Not** through `https://litellm.cianfhoghlaim.ie/v1` (the unified OpenCode Go gateway)
3. **No fallback chain** — if Gemini is rate-limited, the agent raises (no `glm-5.1`, no `minimax-m3`, no `deepseek-v4-flash` fallback)
4. **No cost tracking** — Langfuse never sees the call (LiteLLM callback is the only wire point)
5. **No Cognee/Graphiti memory** — `cognee.search()` is only invoked by the BAML/RAG path, not the ADK LLM calls

### 3.4 Spec vs reality drift

`spec.md:73-77` mandates:
> **Scenario: LiteLLM routing** — GIVEN Root Agent is configured with `model="kimi-k2.6"` via LiteLLM, WHEN the agent makes an LLM call, THEN LiteLLM routes the call to the kimi-k2.6 model via the OpenCode Go API (`OPENAI_BASE_URL`).

**Today this scenario is FALSE** — the ADK agents have no `OPENAI_BASE_URL` env var set; they go directly to Google. The spec describes the *target* state, not the *current* state.

---

## 4. Migration opportunities — ADK 1.5+ new APIs

### 4.1 Native LiteLLM integration (`google.adk.models.lite_llm.LiteLlm`)

ADK 1.5+ ships `from google.adk.models.lite_llm import LiteLlm` (already used by CopilotKit examples at `.agents/skills/copilotkit/examples/showcases/.../a2a-agent/agent/agent.py:18`). The `LiteLlm` class accepts an OpenAI-compatible base URL + model name:

```python
from google.adk.models.lite_llm import LiteLlm

agent = LlmAgent(
    name="celtic_education_research_planner",
    model=LiteLlm(                                # ← NEW: native LiteLLM routing
        model="minimax",                          # ← the 7-tier alias
        api_base="https://litellm.cianfhoghlaim.ie",
    ),
    description="...",
    instruction="...",
)
```

**1-line change per agent** (replace string `"gemini-2.0-flash"` with `LiteLlm(...)` object), and the `LiteLlm` constructor accepts `fallbacks=[...]` so the LiteLLM-side fallback chain is preserved.

### 4.2 `SequentialAgent` + `LoopAgent` (already 3+2 uses) — ADK 1.5+ adds

- **Typed intermediate state** — pass `output_schema=IntermediateState` between sub-agents with Pydantic validation (catches drift planner→researcher→composer)
- **Async-first** — `await research_agent.run_async(query)` instead of `.run()` (we currently use sync)
- **Streaming** — `async for event in research_agent.run_live(...)` for AG-UI CopilotKit side
- **`max_iterations`** (already used via `config.max_research_iterations` = 3) + custom `TerminationStrategy` + `EscalationStrategy` (for F-14 Celtic Teacher Corpus)

### 4.3 `LlmAgent` v2 (ADK 1.5+ `Agent` class)

The new `Agent` class adds: `input_schema` (typed input contracts — none today), `static_instruction` (immutable system prompt) vs `instruction` (templated), `before_agent_callback` / `after_agent_callback` for citation injection (already used in `research_agent.py:198,189`), `planner=BuiltInPlanner(thinking_config=...)` (already used in 6 sites).

### 4.4 Neuro-symbolic OWL truth-anchoring (per `google-adk/SKILL.md:25-27`)

ADK 1.5+ ships OWL constraint enforcement on LLM outputs. Could replace the BAML `@@assert sum == total` runtime evals (P2-39) with ADK-side OWL for the 4-quadrant curriculum checks. **Not recommended** — BAML runtime evals are 1 file per quadrant; OWL is a heavier lift. Park as P3.

### 4.5 A2A Protocol (`/.well-known/agent.json` Agent Cards)

ADK 1.5+ supports the A2A Protocol for inter-agent communication. The `tuatha_root_agent.py:11` already imports `from google.adk.apps.app import App` — the A2A pattern. Relevant for **Cluster E (Content + Sites)** feature backlog (F-13/F-14) where IoM/Jersey/Guernsey legal agents need to coordinate.

---

## 5. Integration with LiteLLM `minimax` alias

### 5.1 Current wire-up (the bypass)

```
ADK agent (LlmAgent(model="gemini-2.0-flash"))
  → google-genai SDK (GOOGLE_API_KEY)
  → https://generativelanguage.googleapis.com
     (direct, no fallback, no tracing, no cost)
```

### 5.2 Target wire-up (LiteLlm + `minimax` alias)

```
ADK agent (LlmAgent(model=LiteLlm(model="minimax", api_base=...)))
  → LiteLLM gateway (port 4000)
  → minimax alias (7-tier fallback):
       1. minimax-m3-slot{0,1,2} (3-key round-robin)
       2. qwen3.7-max
       3. kimi-k2.6
       4. glm-4.6
       5. local qwen-math GGUF (llama-swap)
       6. deepseek-v4-flash
       7. mimo-v2.5
  → Langfuse v3 OTEL traces + RAGAS eval + BAML Collector(name) cost
```

### 5.3 Config change (1 file, ~10 lines)

**`cianfhoghlaim/agents/meaisinfhoghlaim/agents/config.py`:**

```python
# CURRENT (config.py:18)
model_name: str = "gemini-2.0-flash"

# AFTER
from google.adk.models.lite_llm import LiteLlm
from collections.abc import Callable

def _minimax_model() -> LiteLlm:
    """Resolve the KCG `minimax` 7-tier LiteLLM alias at agent-construction time."""
    return LiteLlm(
        model="minimax",                                                  # KCG canonical alias
        api_base=os.getenv("LITELLM_API_BASE", "https://litellm.cianfhoghlaim.ie"),
        # api_key resolved from Locket/Infisical via envsubst at container start
    )

# Keep `model_name` for backward-compat (callers that pass a string still work),
# but add `model_resolver: Callable[[], LiteLlm]`.
model_name: str = "gemini-2.0-flash"                                     # legacy
model_resolver: Callable[[], LiteLlm] = field(default_factory=_minimax_model)  # canonical
```

### 5.4 Per-agent change (mechanical, 1 line each)

Replace `model=config.model_name` with `model=config.model_resolver()` across 32 `LlmAgent` sites (5+ files). Mechanical sed: `s/model=config.model_name/model=config.model_resolver()/g`. For `bunchloch_research_agent.py:342,383,419` which use `worker_model` / `coordinator_model` (fields that don't exist on `config` today — need to add 2 new resolver fields, or alias both to `_minimax_model()`).

### 5.5 `google_search` tool — keep or replace?

`research_agent.py:112` uses `from google.adk.tools import google_search` (Google's built-in search tool — separate from the LLM call, separate quota). Two options:
- **Keep** — most reliable search, no extra LLM cost, semantic decision deferred
- **Replace with Firecrawl MCP** — `tools=[firecrawl_search]` would route through our stack (F-23 / Agent 25 pattern). **Recommended for next PR**, not this one.

### 5.6 Failure mode comparison

| Scenario | Today (Gemini direct) | After (LiteLlm minimax) |
|:--|:--|:--|
| Google rate-limit | `ResourceExhausted`, agent raises | LiteLLM tier-1 fails → tier-2 (qwen3.7-max) → … |
| Google outage | `ServiceUnavailable`, agent raises | All 7 tiers fail, LiteLLM raises `APIConnectionError` |
| Litellm gateway down | n/a (not on the path) | First LLM call raises; subsequent calls retry with backoff |
| Tracing | None (no Langfuse wire) | Langfuse v3 OTEL captures all calls + tier transitions |
| Cost | No signal (Google API key, no metering) | BAML `Collector(name)` + Langfuse cost per agent per call |
| Backpressure | None | `minimax_alias_health` Dagster asset check (`llm_gateway_assets.py:200-215`) gates downstream |

**No regression** in failure mode; significant gain in observability.

---

## 6. Refactor plan — file:line + diff

**PR title:** `refactor(adk): route 5 ADK agents through LiteLLM minimax alias (32 LlmAgent sites)`

| File | Change | Sites | Risk |
|:--|:--|:-:|:-:|
| `agents/config.py` | Add `LiteLlm` import + `model_resolver` field; keep `model_name` for back-compat | L18, L70 | low |
| `agents/research_agent.py` | `model=config.model_name` → `model=config.model_resolver()` | L58, 87, 125, 157 (4) | low |
| `agents/education_research_agent.py` | same | L73, 108, 148, 182, 203, 258, +1 (7) | low |
| `agents/bunchloch_research_agent.py` | same + add `worker_model_resolver` + `coordinator_model_resolver` | L342, 383, 419, +1 (4) | low |
| `agents/curriculum_comparison_agent.py` | same | L49, 112, 138, 179, +1 (5) | low |
| `agents/statistics_agent.py` | same | 5 sites | low |
| `agents/geospatial_agent.py` | same | 5 sites | low |
| `agents/agui_curriculum_agent.py` | same | L268, +1 (2) | low |
| `infrastructure/stacks/oideachais/compose.yaml` | Drop `GOOGLE_API_KEY`; add `LITELLM_API_BASE` + `LITELLM_API_KEY` (Locket-injected) | L278-291 | low |
| `infrastructure/stacks/oideachais/Dockerfile.adk` | `google-adk>=1.0.0` → `>=1.5.0` (for `LiteLlm` class) | depends on lock | low |
| `openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md` | Bump requirement to `google-adk>=1.5.0`; mark LiteLLM-routing scenario as `passing` (was `aspirational`); add "Scenario: minimax alias fallback" | L67-69, 73-77 | low |
| `.agents/skills/google-adk/SKILL.md` | Add a "KCG LiteLLM wire-up" section with the `LiteLlm(model="minimax", api_base=...)` example | new section | low |

**Total: 12 files, +25 / -5 lines.**

### 6.1 Representative diff (`research_agent.py`)

```diff
@@ research_planner = LlmAgent(
     name="celtic_education_research_planner",
-    model=config.model_name,           # ← "gemini-2.0-flash"
+    model=config.model_resolver(),      # ← LiteLlm(model="minimax", api_base=...)
     description="Plans Celtic education research by generating targeted search queries.",
@@ researcher = LlmAgent(
     name="celtic_education_researcher",
-    model=config.model_name,
+    model=config.model_resolver(),
@@ evaluator = LlmAgent(
     name="celtic_education_research_evaluator",
-    model=config.model_name,
+    model=config.model_resolver(),
@@ composer = LlmAgent(
     name="celtic_education_research_composer",
-    model=config.model_name,
+    model=config.model_resolver(),
```

### 6.2 Risks

- **`google_search` tool** still calls Google's API — but it's a search tool, not the LLM; semantically separate. (Mitigation: future PR replaces with Firecrawl MCP.)
- **`google_search` quota** — independent of LLM quota; double-counts against Google free tier. **Document in PR description**.
- **`bunchloch_research_agent.py` `worker_model` / `coordinator_model`** — fields don't exist on `config` today; need 2 new resolver fields in `config.py` (or alias both to `_minimax_model()`).
- **ADK 1.5+ `LiteLlm` class** — only ships in `google-adk>=1.5.0`; lock-bump required.

---

## 7. Cutover — 1 PR

### 7.1 PR title

```
refactor(adk): route 5 ADK agents through LiteLLM minimax alias (32 LlmAgent sites)
```

### 7.2 PR body

**What:** Replace 32 `LlmAgent(model=config.model_name)` string references with `LlmAgent(model=config.model_resolver())` (a `LiteLlm(model="minimax", api_base=...)` callable). Routes 5 specialised agents (research, education_research, bunchloch_research, curriculum_comparison, statistics, geospatial, agui_curriculum) through the KCG `minimax` 7-tier LiteLLM fallback alias instead of calling `generativelanguage.googleapis.com` directly.

**Why:** Closes the Agent 06 P0-#1 drift finding. Today the spec says "Root Agent routes to kimi-k2.6 via LiteLLM" but in fact the ADK agents call Gemini directly. Fixing this:
- Activates the 7-tier fallback chain (no more `ResourceExhausted` on Gemini rate-limit)
- Activates Langfuse v3 OTEL tracing for ADK calls (was zero traces today)
- Activates BAML `Collector(name)` cost tracking (was zero cost signal)
- Gates downstream on `minimax_alias_health` Dagster asset check (`llm_gateway_assets.py:200-215`)
- Bumps `google-adk>=1.0.0` → `>=1.5.0` for the `LiteLlm` class

**Risk:** low. Mechanical find-and-replace + 1 config file. `google_search` tool continues to call Google's API directly (separate concern, future PR).

**Files:** 12 files, +25 / -5 lines.

**Spec:** `openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md` LiteLLM-routing scenario flips from `aspirational` → `passing`. Add a new "Scenario: minimax alias fallback" requirement.

**Tests:**
- `mise run dagster:oideachais` → check `minimax_alias_health` asset check passes
- Manually invoke `research_agent.run_async("Cén fáth a bhfuil Gaeilge tábhachtach?")` → verify it routes through LiteLLM (Langfuse trace visible, no `google.api_core` import in stack trace)
- Verify `google_search` still works (tool call succeeds, citations present)
- Verify the 3 `SequentialAgent` and 2 `LoopAgent` orchestrations still produce output

**Rollback:** `git revert` is safe — `LiteLlm` is constructed at agent-construction time, not module-import time, so reverting the diff restores hardcoded `gemini-2.0-flash` strings and re-routes to Google directly.

**Closes:** `agent-06-litellm.md` finding #1 (ADK agents bypass LiteLLM gateway).
**Opens:** the foundation for F-03 (Langfuse v3 OTEL dashboard for per-agent cost), F-25 (self-improving BAML loop using RAGAS eval failures), and the A2A Protocol pattern for the `tuatha_root_agent.py:11` import.

### 7.3 Effort / Risk

- **Effort:** S (1 day solo). Mechanical change + 1 config file.
- **Risk:** low. No new external deps (`LiteLlm` ships with `google-adk>=1.5.0`). Backward-compat preserved (string `model_name` still works).
- **Wall clock:** 15 min grep audit + 1 hr edits + 1 hr test. 1 PR.

### 7.4 What this PR does NOT do (deferred)

- **F-14 (TCA-gated curriculumonline)** — needs `EscalationStrategy` + Locket-injected teacher credentials
- **F-25 (RAGAS → BAML self-improving loop)** — needs `Collector(name)` wired per agent (P2-7)
- **F-03 (Langfuse v3 OTEL dashboard)** — this PR unblocks traces, dashboard is next
- **Replace `google_search` with Firecrawl MCP** — semantic decision, separate PR
- **`adk/agents/adk/` (deprecated facade)** — 14 files of mirror-tree duplication; refactor in P1-6 (`CelticDltSourceComponent` style drop-in)
- **`stacks/browser/sruth_browser/` (browser tool surface)** — 7 files use `FunctionTool` only; no `LlmAgent` in browser tools so the `LiteLlm` switch doesn't apply

---

## 1-paragraph summary

Google ADK is in active use across 5+ specialised agents in `meaisínfhoghlaim/agents/` (32 `LlmAgent` instances, 3 `SequentialAgent`, 2 `LoopAgent`, 1 custom `BaseAgent`, 6 `BuiltInPlanner`, plus 22 more `LlmAgent` in the deprecated `adk/agents/adk/` mirror facade) plus a 7-file browser tool surface in `core/browser/sruth_browser/`, but every single `LlmAgent(model=config.model_name)` constructor hardcodes `"gemini-2.0-flash"` and routes through Google's native `generativelanguage.googleapis.com` endpoint via `GOOGLE_API_KEY`, BYPASSING the KCG `minimax` 7-tier LiteLLM fallback alias that every other BAML / Agno / opencode / Marimo call honours — this is the Agent 06 P0-#1 drift finding and contradicts the spec's "LiteLLM routing" scenario; ADK 1.5+ ships `from google.adk.models.lite_llm import LiteLlm` which is a 1-line swap per agent (replace the string with `LiteLlm(model="minimax", api_base="https://litellm.cianfhoghlaim.ie")` via a new `config.model_resolver()` field); the recommended 1 PR does this across 12 files (+25/-5 lines) and unblocks Langfuse v3 OTEL tracing, BAML `Collector(name)` cost tracking, the `minimax_alias_health` Dagster asset check, and 3 feature backlog items (F-03 observability dashboard, F-25 self-improving BAML loop, A2A Protocol for `tuatha_root_agent.py`).
