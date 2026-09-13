# `apps/cianfhoghlaim/` — The Central Cianfhoghlaim Homepage

> **The Cianfhoghlaim brand homepage — the canonical
> agentic entry point that aggregates the 6 per-subject
> apps (Mathematics, Chemistry, Geography, Gaeilge, English,
> Computer Science) + the 60 per-subject agents + the BIEP v3
> pipeline health + the Cognee 7-cluster knowledge graph +
> the AG-UI 17-event streaming chat.** Lives at
> `web/apps/cianfhoghlaim/` (added by the
> 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
> change, Phase T).

## Routing

Load this AGENTS.md when:

- You need to add / modify the central Cianfhoghlaim homepage
- You need to wire the agentic chat to the per-subject agents
  (Phase U) via TanStack AI + CopilotKit v2 + AG-UI 17 events
- You need to add / modify the per-subject aggregation
  (the 60 subjects across LC + JC + GCSE + A-Level)
- You need to add / modify a homepage component (PipelineStatus,
  SubjectAgentGrid, KnowledgeGraphPanel, RecentActivityFeed,
  AgenticChat)
- You need to deploy the homepage to Cloudflare Pages

For platform-wide context, load [`../../../AGENTS.md`](../../../AGENTS.md).
For the agent-routing contract, load
[`../../../agents/WEB_INTEGRATION.md`](../../../agents/WEB_INTEGRATION.md).

## Quick start

```bash
# From /web/apps/cianfhoghlaim/
bun run dev                       # TanStack Start dev server
bun run typecheck                 # tsc --noEmit
bun run build                     # TanStack Start build
bun run start                     # node .output/server/index.mjs
```

## Key sources

| Path | Why it matters |
|:--|:--|
| `apps/cianfhoghlaim/routes/index.tsx` | The central homepage (`/`) — agentic chat + 60 subject cards + pipeline health + KG panel |
| `apps/cianfhoghlaim/components/PipelineStatus.tsx` | The BIEP v3 pipeline health grid (DLT + BAML + CocoIndex + RAGAS) |
| `apps/cianfhoghlaim/components/SubjectAgentGrid.tsx` | The 60 per-subject agent cards (the 6 LC + 8 JC + 9 GCSE + 15+ A-Level subjects) |
| `apps/cianfhoghlaim/components/KnowledgeGraphPanel.tsx` | The Cognee 7-cluster knowledge graph panel |
| `apps/cianfhoghlaim/components/RecentActivityFeed.tsx` | The last-24h pipeline activity feed |
| `apps/cianfhoghlaim/components/_shared/A2UISurfaceGenerator.tsx` | The shared A2UI generative-UI surface (CopilotKit v2 a2ui-renderer) |
| `apps/cianfhoghlaim/components/a2ui/` | The per-widget A2UI components |
| `apps/cianfhoghlaim/convex/schema.ts` | The homepage Convex schema (chat_messages, annotations, progress, pipeline_health, knowledge_graph, activity_events) |
| `apps/cianfhoghlaim/app.config.ts` | The TanStack Start config |
| `web/packages/ui-kit/` | The shared UI surface |

## The 6 per-subject apps (aggregated by the homepage)

The central Cianfhoghlaim homepage aggregates the 6 per-subject
apps — the BIEP v1 flagship subjects. Each subject card on
the homepage links to the corresponding per-subject surface:

| Stage | Subject | Per-subject route |
|:--|:--|:--|
| LC | Mathematics | `/lc/mathematics` |
| LC | Chemistry | `/lc/chemistry` |
| LC | Geography | `/lc/geography` |
| LC | Gaeilge | `/lc/gaeilge` |
| LC | English | `/lc/english` |
| LC | Computer Science | `/lc/computer_science` |

The remaining 54 subjects (8 JC + 9 GCSE + 15+ A-Level + 8
additional LC) are surfaced in the
`SubjectAgentGrid` component as filterable cards.

## Adjacent specs

- [`central-cianfhoghlaim-homepage`](../../../openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/specs/central-cianfhoghlaim-homepage/spec.md) — the formal spec for this app
- [`web-monorepo-consolidation`](../../../openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/specs/web-monorepo-consolidation/spec.md) — the consolidation this app is part of
- [`per-subject-coverage`](../../../openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/specs/per-subject-coverage/spec.md) — the 60-subject coverage matrix
- [`per-subject-agents`](../../../openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/specs/per-subject-agents/spec.md) — the 60 per-subject agents this chat routes to
- [`tanstack-ai-agui-integration`](../../../openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/specs/tanstack-ai-agui-integration/spec.md) — TanStack AI + AG-UI compliance
- [`agentic-frontend-frameworks`](../../../openspec/specs/agentic-frontend-frameworks/spec.md) — the canonical 4-surface architecture

## DO NOT

- **Never** import a hardcoded model string — route through `MODEL_REGISTRY`
- **Never** add a per-app Convex deployment — share the umbrella deployment with `apps/oideachais-dashboard/convex/`
- **Never** add a per-app Hono API — extend `web/hono-api/src/routes/copilotkit/`
- **Never** add a per-app Tailwind config — extend from `web/packages/ui-kit/theme/tailwind.config.ts`
- **Never** create per-subject Convex tables — filter the umbrella tables by `subject` + `stage` fields
- **Never** bypass the AG-UI 17-event protocol — emit events via the canonical `chatParamsFromRequest` + `toServerSentEventsResponse` flow

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`tanstack-start`](../../../.agents/skills/tanstack-start/SKILL.md) | React framework (file-based routing, server functions, RSC v1.94+) |
| [`copilotkit-develop`](../../../.agents/skills/copilotkit-develop/SKILL.md) | CopilotKit v2 chat interfaces (the central chat surface) |
| [`copilotkit-agui`](../../../.agents/skills/copilotkit/skills/copilotkit-agui/SKILL.md) | AG-UI protocol wiring for the 17-event stream |
| [`a2ui-renderer`](../../../.agents/skills/copilotkit/skills/a2ui-renderer/SKILL.md) | A2UI generative-UI surfaces (the per-widget components) |
| [`ag-ui`](../../../.agents/skills/ag-ui/SKILL.md) | The AG-UI SSE protocol (agent↔UI streaming) |
| [`centralized-registry`](../../../.agents/skills/centralized-registry/SKILL.md) | The model + schema registry (the canonical model routing) |
| [`schema-codegen`](../../../.agents/skills/schema-codegen/SKILL.md) | The BAML → Zod → Convex → CopilotKit codegen pipeline |

<!-- created: 2026-08-13 (per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change, Phase T) -->
