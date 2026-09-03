# `agents/WEB_INTEGRATION.md` — The Router for `agents/` ↔ `web/apps/`

> **The single router for the agent-frontend integration surface.**
> Every agent in `agents/agent_registry.py:AGENT_REGISTRY` MUST
> have a `web_integration` field that names the web app(s) the
> agent is bound to. This file is the canonical mapping of every
> agent to its web surface.

## Routing

Load this file when:

- You need to add / modify a `web_integration` field for an agent
- You need to wire an agent to a new web app (CopilotKit actions
  or AG-UI streaming)
- You need to add / modify a per-app Hono API CopilotKit endpoint
- You need to surface an agent on the central Cianfhoghlaim homepage

For platform-wide context, load [`../AGENTS.md`](../AGENTS.md).
For the per-agent wiring, see [`./agent_registry.py`](./agent_registry.py).

## The 4 web apps (post-consolidation)

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
change (Phase T), the `web/` surface has 4 apps:

| App | Domain | Subjects covered | Routing key |
|:--|:--|:--|:--|
| `oideachais` | `cianfhoghlaim.ie` | LC + JC + GCSE + A-Level (per-subject pages) | `<stage>/<subject>` |
| `croilar` | `croilar.cianfhoghlaim.ie` | Multi-persona portfolio | `/persona/$slug` |
| `oideachais-dashboard` | `dashboard.cianfhoghlaim.ie` | Operator dashboard | `/health/`, `/dagster/`, `/kg/` |
| `cianfhoghlaim` | `cianfhoghlaim.ie` (homepage) | Central homepage with agentic chat | `/` (with `routes/<stage>/<subject>`) |

## The agent fleet (13 agents) → web app binding

| Agent | Framework | web_integration.app | web_integration.route | Notes |
|:--|:--|:--|:--|:--|
| `root_agent` | Custom | `cianfhoghlaim` | `/` | The query router; surfaces in the homepage chat as the fallback agent |
| `curriculum_agent` | ADK | `oideachais` + `cianfhoghlaim` | `/<stage>/<subject>/` | 5-nation curriculum search; chat-routed from the homepage |
| `translation_agent` | ADK | `oideachais` | `/<stage>/<subject>/` | 6-Celtic-language translation |
| `corpus_agent` | ADK | `oideachais` | `/<stage>/<subject>/` | Dúchas + Gaois + UD + Canúint + Téarma |
| `research_agent` | ADK | `cianfhoghlaim` | `/` (homepage chat) | Long-form research with citations |
| `education_research_agent` | Agno | `cianfhoghlaim` | `/` (homepage chat) | Cross-nation education policy research |
| `bunchloch_research_agent` | Agno | `none` | (no web binding) | M4 MacBook-local research; headless pipeline |
| `geospatial_agent` | ADK | `oideachais` | `/<stage>/<subject>/` (geospatial layer) | LSOA / Data Zone spatial analysis |
| `statistics_agent` | ADK | `oideachais-dashboard` | `/health/` | Education metrics + benchmarking |
| `curriculum_comparison_agent` | ADK | `oideachais` + `cianfhoghlaim` | `/<stage>/<subject>/compare/` | Cross-nation curriculum mapping |
| `agui_curriculum_agent` | Agno | `cianfhoghlaim` | `/` (homepage chat) | AG-UI streaming (CopilotKit consumer) |
| `mcp_curriculum_agent` | ADK | `oideachais` | `/<stage>/<subject>/` (MCP bridge) | MCP-server-bridged curriculum agent |
| `image_generation_agent` | ADK | `oideachais` + `oideachais-dashboard` | `/assets/image_gen/$id` | Consumes the 5 `image_gen` MODEL_REGISTRY entries (per Phase L) |

## The `web_integration` field (per agent)

The `AgentFleetWiring` dataclass in
[`./wiring.py`](./wiring.py) includes the canonical
`web_integration` field:

```python
@dataclass(frozen=True)
class AgentFleetWiring:
    agent_name: str
    module_slug: str
    module_path: str
    framework: AgentFramework
    display_name: str
    baml_prefix: str
    langfuse_trace_name: str
    cognee_dataset: str
    letta_agent_id: str
    litellm_routing_key: str
    # Per Phase N — the central Cianfhoghlaim homepage binding:
    # - `app` = "cianfhoghlaim" | "oideachais" | "croilar" | "oideachais-dashboard"
    # - `route` = the per-subject route (e.g. "/lc/mathematics")
    # - `subject_agent_cards` = True (surfaces in the homepage grid)
    # - `homepage_chat_routing` = True (dispatchable from the chat)
    web_integration: dict[str, Any] = field(default_factory=dict)
```

## The Hono API gateway (per-app CopilotKit actions)

Per Phase G, all per-app CopilotKit actions live at
`web/hono-api/src/routes/copilotkit/<app>.<subject>.ts`:

```
web/hono-api/src/routes/copilotkit/
├── oideachais/
│   ├── lc.mathematics.ts
│   ├── lc.chemistry.ts
│   ├── lc.physics.ts
│   ├── lc.biology.ts
│   ├── lc.english.ts
│   ├── lc.gaeilge.ts
│   ├── lc.french.ts
│   ├── lc.history.ts
│   ├── lc.geography.ts
│   ├── lc.business.ts
│   ├── jc.mathematics.ts
│   ├── jc.english.ts
│   ├── ... (60+ subject routes)
├── croilar.ts
├── oideachais-dashboard.ts
└── cianfhoghlaim.ts  # the central homepage chat
```

Each file exposes the per-subject actions at
`/api/copilotkit/<app>.<subject>/<action>` (namespaced by app +
subject).

## The central Cianfhoghlaim homepage (Phase T)

The homepage at `web/apps/cianfhoghlaim/routes/index.tsx` provides:

1. **The agentic chat** at the center, wired to
   `web/hono-api/src/routes/copilotkit/cianfhoghlaim.ts`
2. **Subject-aware routing** — the homepage detects the subject from
   the user's query (via LLM extraction) and dispatches to the
   appropriate per-subject agent
3. **The 60 subject agent cards** (LC + JC + GCSE + A-Level)
4. **The pipeline health grid** (Dagster + BAML + CocoIndex + DLT)
5. **The Cognee 7-cluster knowledge graph panel**
6. **The recent activity feed** (last 24h)

## DO NOT

- **Never** hardcode a model string in the web_integration binding
- **Never** create a per-app `apps/<app>/apps/api/src/` for
  CopilotKit actions — they live at `web/hono-api/src/routes/copilotkit/`
- **Never** skip the `web_integration` field when adding a new agent

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`agent-fleet-orchestration`](../.agents/skills/agent-fleet-orchestration/SKILL.md) | The 12-agent fleet wiring + the 5-framework runtime + the LiteLLM routing keyword map |
| [`agentic-frontend-frameworks`](../.agents/skills/agentic-frontend-frameworks/SKILL.md) | TanStack Start + CopilotKit + AG-UI + Hono + Convex |
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | The model + schema registry (the 52-entry MODEL_REGISTRY + the 7 schema helpers) |
| [`schema-codegen`](../.agents/skills/schema-codegen/SKILL.md) | The BAML → Zod → Convex → CopilotKit codegen pipeline |

<!-- created: 2026-08-13 (per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change, Phase M) -->
