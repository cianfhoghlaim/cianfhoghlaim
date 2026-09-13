# Change: Google ADK + Gemini Deep Research as the Cross-Pipeline Control Plane

## Why

Today the 13-agent fleet in `agents/agent_registry.py` is a **declarative
registry** with no imperative orchestrator. `root_agent` is a Custom
LiteLLM router (`agents/adk/root_agent.py:848`), so the 8 ADK agents in
the fleet cannot coordinate at runtime — `_workflow_handlers.py:299`
returns stub data.

The browser stack at `bonneagar/stacks/browser/sruth_browser/` already
implements a 5-agent ADK `SequentialAgent` + `LoopAgent` pipeline
(`agents/orchestrator.py:10`), but it is:

- Stuck on `gemini-2.0-flash`
- Not wired to any of the DLT / CocoIndex / BAML pipelines
- Disconnected from the 12-agent fleet (separate process, different
  routing layer)
- 12 known issues (Dockerfile CMD broken, `Dockerfile.mcp` missing,
  Restate/Convex not deployed, `agent_os/` is dead code,
  `gemini-3-flash/` and `polymarket-research/` templates never wired)

Meanwhile, the new **Gemini Deep Research API** (the agentic flow at
<https://ai.google.dev/gemini-api/docs/deep-research>) ships a long-form
research capability that is **feature-superior** to Firecrawl `/agent`
for cross-source synthesis. It is referenced 100+ times in this repo as
the *corpus* of past Gemini Deep Research reports
(`leabharlann/gemini_deep_research/`), but is **never called as a live
API**.

This change makes **Google ADK the cross-pipeline orchestrator** for
DLT → BAML → CocoIndex → Browser workflows, with **Gemini Deep
Research** as the default `RESEARCH` backend — bringing feature parity
with the existing Firecrawl / Crawl4AI / Stagehand / Skyvern /
Browserbase / Z.AI vision backends while adding true agentic
multi-source synthesis.

## What changes

### 1. NEW capability `adk-deep-research-control-plane`

A single capability spec covering the 5 ADK orchestrator + 3 backend
+ 3 pipeline integration patterns. Adds 7 Requirements.

### 2. MODIFIED capability `agent-registry`

Flip `root_agent.framework = AgentFramework.CUSTOM` →
`AgentFramework.ADK`. Replace the Custom `QueryRouter` with an ADK
`SequentialAgent` ("cian_root") that classifies → routes → evaluates
→ emits AG-UI events.

### 3. MODIFIED capability `browser-tools` (alias `sruth-browser`)

Add `gemini_deep_research` as the top-priority `RESEARCH` backend
(displacing Firecrawl at that role). Fix the 12 known issues:
`Dockerfile` CMD, missing `Dockerfile.mcp`, GOLD_STANDARD compliance
files, delete dead `agent_os/` + TS templates.

### 4. MODIFIED capability `baml-schemas`

Add `ExtractGeminiDeepResearchReport` to `baml_src/_shared/` + 1
extraction client. Adds a new pipeline-orchestration schema.

### 5. NEW capability `dlt-pipeline-trigger-via-adk`

Wrap DLT pipeline invocations as ADK `FunctionTool`s. The new
`dlt_trigger_agent` invokes `pipeline.run(source())` and emits asset
materialization events.

### 6. NEW capability `cocoindex-pipeline-trigger-via-adk`

Wrap CocoIndex v1 app updates as ADK `FunctionTool`s. The new
`cocoindex_index_agent` invokes `coco.update()` on a named App.

### 7. NEW capability `pipeline-orchestrator-agent`

Three agents (`dlt_trigger_agent`, `cocoindex_index_agent`,
`baml_extract_agent`) wrapped in a `SequentialAgent` + `LoopAgent`
that drives the canonical DLT → BAML → CocoIndex pipeline from inside
the ADK runtime.

## Out of scope

- Migrating the 3 Agno agents (education_research, bunchloch_research,
  agui_curriculum) to ADK — covered by a separate change.
- Replacing the LiteLLM gateway with direct Vertex AI calls.
- The Cloud Run parity work (porting the 11 Terraform modules from
  `gemini_hackathon/cloud/terraform/modules/` into cianfhoghlaim's
  `bonneagar/stacks/cloud/`) — deferred to a follow-up change.
- Tipecat voice integration.

## Dependencies

```markdown
## Dependencies

`Blocked by: 2026-08-26-mega-3a-baml-and-adk-v1` (the BAMLFunctionTool pattern this work extends).

`Blocked by: 2026-08-15-centralized-registry-v1` (MODEL_REGISTRY / schema registry; the new pipeline orchestrator reads from these).

`Blocked by (soft): 2026-08-30-cieanfhoghlaim-biep-on-gcp-v1` (the GCP-first substrate this work ports partial patterns from).

`Affected repos: cianfhoghlaim, cianchosaint, ciancheiltis, tuatha, gemini_hackathon`
```

## Impact

- Affected specs:
  - **NEW**: `adk-deep-research-control-plane` (7 ADDED Requirements)
  - **MODIFIED**: `agent-registry` (1 MODIFIED Requirement — root_agent framework flip)
  - **MODIFIED**: `browser-tools` (3 MODIFIED Requirements — Gemini Deep Research as RESEARCH backend, 12 known issues fixed)
  - **MODIFIED**: `baml-schemas` (1 ADDED Requirement — ExtractGeminiDeepResearchReport)
  - **NEW**: `dlt-pipeline-trigger-via-adk` (2 ADDED Requirements — FunctionTool wrapping + events)
  - **NEW**: `cocoindex-pipeline-trigger-via-adk` (2 ADDED Requirements — FunctionTool wrapping + observability)
  - **NEW**: `pipeline-orchestrator-agent` (3 ADDED Requirements — SequentialAgent + 3 agents)

- Affected code/config:
  - `agents/adk/root_agent.py` — REWRITE (Custom → ADK SequentialAgent)
  - `agents/adk/pipeline_orchestrator/{dlt_trigger_agent,cocoindex_index_agent,baml_extract_agent}.py` — NEW (3 files)
  - `agents/adk/pipeline_orchestrator/orchestrator.py` — NEW (SequentialAgent + LoopAgent)
  - `agents/_workflow_handlers.py` — MODIFY (call new root_agent)
  - `agents/agent_registry.py` — MODIFY (flip root_agent framework)
  - `agents/integrations/agent_registry_runtime.py` — MODIFY (register new orchestrator with CopilotKit)
  - `bonneagar/stacks/browser/sruth_browser/backends/paid/gemini_deep_research.py` — NEW (GoogleDeepResearchBackend)
  - `bonneagar/stacks/browser/sruth_browser/browser_types.py` — MODIFY (add Gemini to BACKEND_PRIORITY)
  - `bonneagar/stacks/browser/sruth_browser/backends/router.py` — MODIFY (wire new backend)
  - `bonneagar/stacks/browser/sruth_browser/agents/orchestrator.py` — MODIFY (promote to minimax alias + gemini-2.5-pro)
  - `bonneagar/stacks/browser/sruth_browser/agents/evaluator.py` — MODIFY (handle Deep Research `interactions` field)
  - `bonneagar/stacks/browser/sruth_browser/frontend/adapters/agui.py` — MODIFY (stream Deep Research events)
  - `bonneagar/stacks/browser/sruth_browser/baml/browser_extraction.baml` — MODIFY (add GeminiDeepResearchReport class)
  - `bonneagar/stacks/browser/Dockerfile` — FIX (sruth.browser.server → sruth_browser.server)
  - `bonneagar/stacks/browser/Dockerfile.mcp` — NEW
  - `bonneagar/stacks/browser/{sidecar,secrets,blueprint}.yaml` + `.env.example` — NEW (gold-standard)
  - `bonneagar/stacks/browser/agent_os/` — DELETE (dead code)
  - `bonneagar/stacks/browser/{gemini-3-flash,polymarket-research}/` — DELETE (unused TS templates)
  - `bonneagar/stacks/browser/litellm_config.yaml` — MODIFY (add gemini-deep-research alias)
  - `baml_src/_shared/gemini_deep_research.baml` — NEW (returns `GeminiDeepResearchOutput` — name chosen to avoid collision with the existing `GeminiDeepResearchReport` class in `baml_src/processing/author_archive.baml` from `2026-06-16-author-archive-gemini-and-uos-ingestion`)
  - `dlt_sources/_shared/gemini_deep_research.py` — NEW (DLT source wrapping the API)
  - `openspec/specs/adk-deep-research-control-plane/{spec.md,AGENTS.md}` — NEW
  - `openspec/specs/dlt-pipeline-trigger-via-adk/{spec.md,AGENTS.md}` — NEW
  - `openspec/specs/cocoindex-pipeline-trigger-via-adk/{spec.md,AGENTS.md}` — NEW
  - `openspec/specs/pipeline-orchestrator-agent/{spec.md,AGENTS.md}` — NEW
  - Cross-repo mirrors: cianchosaint/, ciancheiltis/, tuatha/, gemini_hackathon/ each get a sibling change with their own domain-specific agents wired through the same orchestrator.

## Why 7 specs not 1

The 5 new + 2 modified specs each have **different stakeholders** and
**different lifecycles**:

- `adk-deep-research-control-plane` owns the ADK orchestrator surface
- `agent-registry` owns the declarative registry
- `browser-tools` owns the browser-stack backends
- `baml-schemas` owns extraction schema changes
- `dlt-pipeline-trigger-via-adk` + `cocoindex-pipeline-trigger-via-adk` are
  the two pipeline-orchestration surfaces
- `pipeline-orchestrator-agent` is the bundle of 3 agents that wraps them

This mirrors the existing pattern (`agent-platform-cluster` + `agent-registry`
+ `agent-observability` + `agent-memory-systems` are separate).
