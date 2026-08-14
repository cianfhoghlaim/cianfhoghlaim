# 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1

## Why

The `web/` subdirectory has accumulated drift across the v4–v7
flattening cycles: 7 separate apps, 6 stub packages, 4 Hono
surfaces, 3 Convex deployments, 6 themes, 2 stale `_underscore-
prefixed` directories, and no consolidated monorepo tooling.

The `agents/` tree has 12 agents + 4 educational agents wired
through 5 frameworks, but the binding to the web surface is
one-off per app. The data platform pipeline (per the 2026-08-10
through 2026-08-15 changes) has BAML extraction + CocoIndex v1
+ DLT + DuckLake + Dagster + OCR/VLM ensemble + 5-stage cognify
+ centralized registries — but the schema-to-UI pipeline ends
at Zod (`bi-ep.gen.ts`); it does NOT extend to Convex schemas +
CopilotKit actions + AG-UI event types + per-subject routes.

Per the user's direction, the change also adds:

1. **A clear central Cianfhoghlaim homepage** (`apps/cianfhoghlaim/`)
   that visualizes all data engineering pipeline outputs in one
   place with an agentic chat (TanStack Start + TanStack AI +
   Convex + CopilotKit v2 + AG-UI 17-event protocol + generative UI)
   querying DuckLake + LanceDB + Cognee + 60 subject agents.

2. **60 per-subject agents** (one per subject × stage across LC +
   JC + GCSE + A-Level) fully integrated with DuckLake +
   CocoIndex + BAML extraction, registered in `AGENENT_REGISTRY`,
   and bound to the per-subject web routes.

This mega-change ships 21 sub-phases across 10 PRs.

## What Changes

### Phase A — web/packages/ consolidation (6 → 3)

- MERGE `web/packages/{analytics,i18n,ui,config}/` → `web/packages/ui-kit/`
- KEEP `web/packages/auth/`
- KEEP `web/packages/db/`

### Phase B — Monorepo tooling

- NEW `web/package.json` (bun workspaces root)
- NEW `web/turbo.json` + `web/.gitignore` + `web/tsconfig.base.json` + `web/.npmrc`

### Phase C — Archive stale dirs

- MOVE `web/_oideachais_apps/` → `.archive/web-historical/`
- MOVE `web/_croilar_shared/` → `.archive/web-historical/`

### Phase D — Merge 5 apps → apps/oideachais/

- MERGE `cianfhoghlaim-web` + `cianfhoghlaim-leaving-cert` + `cianfhoghlaim-mmo` + `tuatha-ui` + `tuatha-demo` → `web/apps/oideachais/`

### Phase E — Merge 3 apps → apps/croilar/

- MERGE `croilar-web` + `croilar-portal` + `game_showcase` → `web/apps/croilar/`

### Phase F — Move dashboard

- MOVE `web/_oideachais_dashboard/` → `web/apps/oideachais-dashboard/`

### Phase G — Unify Hono API

- MOVE per-app CopilotKit action directories → `web/hono-api/src/routes/copilotkit/`

### Phase H — Unify Convex

- MERGE 3 deployments → 1 (per-subject schemas)

### Phase I — Unify themes

- NEW `web/packages/ui-kit/theme/tailwind.config.ts` + `tokens.css`

### Phase J — Cleanup

- DELETE stale dirs (`web/_croilar_shared/`, `web/packages/{analytics,config,i18n}/`)

### Phase K — Agent-frontend integration

- For each app: CopilotKit + Hono + Convex + per-app AGENTS.md

### Phase L — Image-gen agent consumer

- NEW `agents/adk/image_generation_agent.py` + BAML + CocoIndex

### Phase M — Cross-links + router

- NEW `agents/WEB_INTEGRATION.md`

### Phase N — New openspec specs

- NEW `web-monorepo-consolidation` + `image-generation-agent`
- DELTA `agent-registry` (web-binding requirement)

### Phase O — Schema-driven codegen pipeline

- NEW `scripts/schema-codegen/{index,baml-to-ts,convex-from-zod,copilotkit-actions,ag-ui-types,per-subject-routes}.ts`

### Phase P — Per-subject coverage (60 subjects)

- 60 × 8 BAML functions = 480 new functions
- 60 DLT sources + 60 CocoIndex flows + 60 Convex schemas
- ~500 CopilotKit actions + 240+ routes

### Phase Q — TanStack AI + AG-UI integration

- NEW `web/apps/oideachais/src/lib/tanstack-ai-client.ts`
- NEW `web/apps/oideachais/src/lib/convex-client.ts`

### Phase R — E2E verification per subject

- NEW `tests/e2e/subjects/<subject>.test.ts` (×60)

### Phase S — Recent pipeline integration

- 8 openspec changes wired into the consolidated web/

### Phase T — Central Cianfhoghlaim homepage (NEW 4th app)

- NEW `web/apps/cianfhoghlaim/` (the BRAND HOMEPAGE)
- Central agentic chat at `routes/index.tsx`
- 60 subject agent cards + DuckLake + LanceDB + Cognee + BAML
- Generative UI: Components as Tools, Tool Call Rendering, State Rendering, A2UI, MCP Apps

### Phase U — 60 subject-specific agents

- NEW `agents/adk/subjects/base.py` (SubjectAgentBase)
- NEW `agents/adk/subjects/_factory.py` (60-agent factory)
- 60 new agent files at `agents/adk/subjects/<stage>/<subject>_agent.py`
- All 60 registered in `agents/agent_registry.py:AGENT_REGISTRY` with `web_integration` field
- Each fully integrated with DuckLake + CocoIndex + BAML

## Dependencies

`Blocked by: 2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1` (Change 3, merged).

`Blocks: none` (final change in the v3 cycle).

`Affected repos: cianfhoghlaim` (single-repo change).

## Out of scope (intentionally)

- Babylon.js 3D integration with `image_generation_agent` (the asset pipeline for game textures is a separate change)
- x402 + learn-to-earn credential pipeline (per `2026-08-12-2026-08-08-learn-to-earn-x402-credential-pipeline-v1`) — separate change
- Apple Photos ingestion (per `apple-photos-ingestion` skill) — already covered by `apple-photos` MCP + spec
- The 55 deprecated skills in `.agents/skills_backup/` — left alone per the user's instruction
- `sruth/` directory leftovers — preserved as historical pattern references per the user's instruction

## Verification (per PR)

```bash
# After each PR:
bun install                              # workspace sync
bun run typecheck                      # TS gates
bun run lint                            # lint gates
bun run build                            # build gates

# After all 10 PRs:
openspec validate 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 --strict
mise run lint:skills                    # 67 skills pass
mise run lint:drift-docs                # 0 violations
mise run lint:guides-yml                # all 26 guides valid
```

## Risks

| Phase | Risk | Mitigation |
|:--|:--|:--|
| A | Stub packages break imports | Keep `index.ts` re-exports during the move |
| B | Turbo misconfiguration | Match root `turbo.json` exactly |
| C-J | Big-bang refactor breaks working apps | Each phase gates on `bun run typecheck && bun run lint && bun run build` |
| D | Route conflicts | Each app's routes live under a unique top-level prefix |
| G | Hono route conflicts | Namespace routes by app prefix |
| H | Convex schema conflicts | Union schemas; filter by `app` + `subject` field |
| I | Theme regressions | Per-app `theme-overrides.ts` for backward compat |
| K | CopilotKit wiring misses actions | Use the canonical 13-action pattern from `cianfhoghlaim-leaving-cert` |
| O | Schema generator complexity | Start with the 6 existing LC subjects; generalize after |
| P | Per-subject route explosion | TanStack Start's file-based routing handles this natively |
| Q | TanStack AI + AG-UI compliance | Use the canonical `chatParamsFromRequest` + `toServerSentEventsResponse` |
| R | E2E tests fail intermittently | Use Playwright's auto-waiting + Convex's deterministic queries |
| T | Homepage chat latency | Subject-aware routing + DuckLake caching + Convex realtime |
| U | 60 agents = 60 maintenance points | `SubjectAgentBase` + factory pattern |

## Rollback strategy

Each PR is a separate git commit. Each commit can be reverted with
`git revert`. The openspec change is not archived until all 10 PRs land.

## Estimated scope

- **LOC:** ~13,400 (net new)
- **New files:** ~300 (codegen scripts + per-subject schemas + routes + agents + e2e tests)
- **Modified files:** ~100 (per-area BAML extensions + AGENTS.md + skills)
- **Openspec changes:** 1 (this mega-change with 8 spec files)
- **PRs:** 10 (one per phase grouping)
- **Estimated effort:** ~10 weeks of focused work

## Cross-references

- `openspec/changes/2026-08-13-skill-consolidation-and-extension-v1/` (Change 1, merged)
- `openspec/changes/2026-08-13-guides-yml-repair-and-docs-integrations-index-v1/` (Change 2, merged)
- `openspec/changes/2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1/` (Change 3, merged)
- `openspec/specs/british-isles-education-pipeline-v3/` (the BIEP flagship)
- `openspec/specs/agentic-frontend-frameworks/` (the canonical 4-surface architecture)
- `openspec/specs/centralized-model-registry/` (the 52-entry model registry)
- `openspec/specs/per-subject-coverage/` (the 60-subject coverage matrix)
- `openspec/specs/central-cianfhoghlaim-homepage/` (the central homepage)
