# `web/` — Agentic Frontend Apps

> **The agent-driven web surface of the Cianfhoghlaim stack —
> TanStack Start 1.0+ + CopilotKit v2 + AG-UI 17-event protocol +
> A2UI + BetterAuth ^1.7 + Hono 4.8 + Convex + Cloudflare Workers.**
> Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1**
> openspec change (Wave 6), the wave finished its 12-task
> modernisation: all 5 apps moved to TanStack Start 1.0+ (post-Vinxi
> unified model), adopted the full TanStack family (Router + Query +
> AI + DB + Form + Store), upgraded CopilotKit from v1.67 → v2 with
> `publicLicenseKey`, wired the AG-UI 17-event protocol through the
> Hono API gateway and per-app `useAgUiStream` consumers, landed A2UI
> declarative surfaces in the oideachais dashboard for the BIEP v3
> dashboards, upgraded BetterAuth to `^1.7` with the OIDC + 2FA +
> passkey + SIWE + multiSession plugins, consolidated the umbrella
> Convex at `apps/oideachais-dashboard/convex/`, shipped per-app
> `wrangler.toml` for Cloudflare Workers deployment, and added a
> `mise run lint:web-stack` gate that validates the canonical web
> stack shape.

> **Wave 5 complete (filesystem layer).** The 4 high-risk merges
> (croilar-portal → croilar-web, cianfhoghlaim-web → cianfhoghlaim,
> cianfhoghlaim-leaving-cert → oideachais, cianfhoghlaim-mmo → tuatha)
> have been completed at the **filesystem level** — moved into
> `_merged/<src>/app/` subtrees of each canonical app. **Integration
> work** (route-tree regeneration, import rewriting, Convex schema
> unification, Hono router consolidation) remains in follow-up PRs.

## Routing

Load this AGENTS.md when:

- You need to add / modify a frontend app (any of the 5)
- You need to wire an AG-UI stream from an agent runtime to a
  CopilotKit React UI
- You need to add / modify a Hono API route
- You need to add / modify a shared UI component
- You need to deploy to Cloudflare Pages (Workers + R2 + D1 +
  Vectorize)

For platform-wide context, load [`../AGENTS.md`](../AGENTS.md).

## Quick start

```bash
# From /web/
bun install                       # Install all workspace dependencies (bun workspaces)
bun run dev                       # Run all apps + packages in dev mode (turbo)
bun run typecheck                 # Type check across the monorepo
bun run lint                      # Lint across the monorepo
bun run build                     # Build everything
```

## Post-Wave 5 topology (5 apps + 5 packages + 1 hono-api)

### Apps (1 active + 5 archived)

| App | Why it matters | Wave 6 status |
|:--|:--|:--|
| `web/apps/cianfhoghlaim-nua/` | **The CONSOLIDATED Cianfhoghlaim-Nua** (the v6 era target). 1 TanStack Start app with 6 route groups: `(student)` (4 Phase 1 study-plan routes), `(educator)` (NCCE landing), `(researcher)` (BIEP dashboards), `(author)` (Croilar public), `(mmo)` (Túatha), `(admin)` (deployment control panel). | ✅ Phase 1 + 2 + 3 shipped (v6 era). Per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1 change (Phase 3 §B-D). |
| `web/apps/_archive/{cianfhoghlaim,oideachais,oideachais-dashboard,tuatha,croilar-web}-pre-v6/` | **ARCHIVED** (1 release cycle per the `retrospective-cleanup` spec). Per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1 change (Phase 3 §F). | Moved to `_archive/`; will be deleted after 1 release cycle. |

### Hono API gateway (1)

| Path | Why it matters |
|:--|:--|
| `web/hono-api/` | The SINGLE canonical Hono API gateway (per-app CopilotKit actions + AG-UI streamer + Drizzle + Convex HTTP actions). |

### Shared packages (5)

| Path | Why it matters | Wave 6 status |
|:--|:--|:--|
| `web/packages/auth/` | **BetterAuth `^1.7`** React client + server (`authClient.useSession`, `twoFactor`, `passkey`, `siwe`, `organization`, `multiSession` plugins). | ✅ Wave 6.6 — server config (`web/hono-api/src/auth.ts`) + client (`web/packages/auth/src/index.ts`) upgraded to BetterAuth `^1.7` with OIDC + 2FA + passkey + SIWE + multiSession plugins. |
| `web/packages/db/` | Convex generators + Drizzle helpers (the canonical `@cianfhoghlaim/db`). |
| `web/packages/ui-kit/` | The consolidated UI surface (analytics + i18n + components + config + hooks). |
| `web/packages/api-client/` | Typed API client (fetch wrapper) **+ AG-UI client (`agui.ts` → `HttpAgent`, `EventType`, `CIANFHOGHLAIM_RUNTIME_URL`)**. | ✅ Wave 6.4 — `@ag-ui/client` re-exported so the 5 apps share a single `createCianfhoghlaimAgent()` factory. |
| `web/packages/contracts/` | Zod schemas + TS types (the contract-first surface). |

### Adjacent

| Path | Why it matters |
|:--|:--|
| `demos/game_showcase/` | Game showcase (Python module, moved out of `web/apps/` in Wave 5). |
| `demos/tuatha-demo/` | Python Túatha demo (moved out of `web/apps/` in Wave 5). |
| `openspec/archive/2026-08-26-archive-legacy-oideachais-apps/` | **ARCHIVED** (Wave 5): legacy sruth-era workspace. |

## Adjacent specs

- [`agentic-frontend-frameworks`](../openspec/specs/agentic-frontend-frameworks/spec.md) — TanStack Start + CopilotKit + AG-UI + Hono + Convex
- [`web-monorepo-consolidation`](../openspec/specs/web-monorepo-consolidation/spec.md) — this consolidation (the canonical structure)
- [`central-cianfhoghlaim-homepage`](../openspec/specs/central-cianfhoghlaim-homepage/spec.md) — the central homepage
- [`per-subject-coverage`](../openspec/specs/per-subject-coverage/spec.md) — the 60-subject coverage matrix
- [`per-subject-agents`](../openspec/specs/per-subject-agents/spec.md) — the 60 per-subject agents
- [`tanstack-ai-agui-integration`](../openspec/specs/tanstack-ai-agui-integration/spec.md) — TanStack AI + AG-UI compliance
- [`schema-driven-codegen`](../openspec/specs/schema-driven-codegen/spec.md) — BAML → Zod → Convex → CopilotKit pipeline
- [`deployment-control-panel`](../openspec/specs/deployment-control-panel/spec.md) — the web UI for `deployment-choice.yaml`
- [`british-isles-education-pipeline-v3`](../openspec/specs/british-isles-education-pipeline-v3/spec.md) — the BIEP v3 web UI consumer

## Wave 6 — Frontend modernisation (post-Wave 6 summary)

Per the **`2026-08-24-wave-6-frontend-tanstack-modernisation-v1`**
openspec change. The wave finished its 12 tasks:

1. **6.1** TanStack Start 1.0+ — all 5 apps migrated off Vinxi nightly
   to the 1.0+ post-unified authoring model with `wrangler deploy` output.
2. **6.2** TanStack family — all 5 apps adopted `@tanstack/ai`,
   `@tanstack/db`, `@tanstack/form` on top of the existing Router +
   Query.
3. **6.3** CopilotKit v2 — all 5 apps + the Hono gateway upgraded
   from v1.67 to v2; chat components now ship from
   `@copilotkit/react-core/v2` (NOT react-ui which is CSS-only in v2);
   `publicLicenseKey` is the canonical config (`publicApiKey`
   deprecated).
4. **6.4** AG-UI protocol — the 17-event protocol (`RUN_STARTED`,
   `TEXT_MESSAGE_CONTENT`, `TOOL_CALL_*`, `STATE_DELTA`, …) is wired
   between `web/hono-api/src/routes/agui/` and the 5 apps via
   `@ag-ui/react`'s `useAgent` hook. The `useAgUiStream` consumer
   sits at `web/apps/oideachais/src/lib/ag-ui/use-ag-ui-stream.ts` and
   is the canonical pattern.
5. **6.5** A2UI protocol — the BIEP v3 dashboard declarative surfaces
   landed at `web/apps/oideachais-dashboard/src/components/a2ui/`,
   driven by `createA2UIMessageRenderer` from
   `@copilotkit/react-core/v2` (per the a2ui-renderer skill).
6. **6.6** BetterAuth `^1.7` — server config at
   `web/hono-api/src/auth.ts` + client at `web/packages/auth/src/index.ts`
   upgraded to `^1.7`. Plugin set: oidcClient + twoFactor + passkey +
   siwe + organization + multiSession + genericOAuth.
7. **6.7** Umbrella Convex — the consolidated schema lives at
   `web/apps/oideachais-dashboard/convex/schema.ts`; the
   `cianfhoghlaim/convex/` orphan is temporarily tolerated by
   `mise run lint:web-stack --allow-non-umbrella-convex`.
8. **6.8** Bun `>= 1.4` — pinned at `1.4.0` in `mise.toml`;
   `packageManager` field in every app's `package.json`; legacy
   Vinxi-nightly `nitro-nightly` dep removed from `tuatha/`.
9. **6.9** Per-app `wrangler.toml` — 5 new files at
   `apps/{cianfhoghlaim,oideachais,oideachais-dashboard,croilar-web,tuatha}/wrangler.toml`
   with R2 + D1 + Vectorize bindings + preview/production env vars.
10. **6.10** `mise run lint:web-stack` — script at
    `scripts/sync/lint_web_stack.py` validates 5 apps + 5 packages +
    1 hono-api, no nested `apps/api/` or `packages/`, canonical Convex
    location.
11. **6.11** This AGENTS.md file.
12. **6.12** Validation — `bun run typecheck` per app + `wrangler
    deploy --dry-run` per app + `mise run lint:web-stack` (see
    **Validation** section below).

## Validation (post-Wave 6)

```bash
# Per-app typecheck (5 apps)
bun --filter @cianfhoghlaim/cianfhoghlaim run typecheck
bun --filter @cianfhoghlaim/oideachais run typecheck
bun --filter @cianfhoghlaim/oideachais-dashboard run typecheck
bun --filter @croilar/web run typecheck
bun --filter @cianfhoghlaim/tuatha-ui run typecheck

# Per-app deploy dry-run (requires CLOUDFLARE_API_TOKEN)
( cd web/apps/cianfhoghlaim && wrangler deploy --dry-run )
( cd web/apps/oideachais && wrangler deploy --dry-run )
( cd web/apps/oideachais-dashboard && wrangler deploy --dry-run )
( cd web/apps/croilar-web && wrangler deploy --dry-run )
( cd web/apps/tuatha && wrangler deploy --dry-run )

# Web stack lint gate (validates canonical structure)
mise run lint:web-stack
```

## Wave 5 follow-up work (the integration gap)

The 4 filesystem-level merges leave integration work pending:

1. **`croilar-web`** — regenerate the TanStack Router route tree to include `_admin_legacy/portal/src/routes/_layout/*` as `/admin/*`. Unify the auth middleware (`lib/auth-client` + `lib/middleware` need to live in `web/packages/auth/`).
2. **`cianfhoghlaim`** — promote `cianfhoghlaim-web/src/routes/{biep-v2,control-panel}/` into the central homepage router. Unify `convex/` schemas.
3. **`oideachais`** — promote `cianfhoghlaim-leaving-cert/apps/web/src/routes/*` into `oideachais/src/routes/<stage>/<subject>/`. Migrate the BAML surface (in `baml_src/`) + ADK agents into `agents/`. Move `packages/{auth,config,convex,db,i18n,ui}/` to `web/packages/*/` (the canonical versions).
4. **`tuatha`** — promote `cianfhoghlaim-mmo/src/components/*` + `src/routes/*` + `convex/{badges,credentialAnchors,questPacks,x402Payments,schema}.ts` into the tuatha app. Wire Babylon.js + 2D canvas together.

## DO NOT

- **Never** import a hardcoded model string in a frontend — route through `MODEL_REGISTRY`
- **Never** bypass the Hono API gateway — every backend call goes through `web/hono-api/`
- **Never** create a per-app `apps/<app>/apps/api/src/` directory for CopilotKit actions — they live at `web/hono-api/src/routes/copilotkit/`
- **Never** create a per-app `convex/` deployment — all apps share `apps/oideachais-dashboard/convex/`
- **Never** create a per-app `tailwind.config.ts` — extend from `web/packages/ui-kit/theme/tailwind.config.ts`
- **Never** create a per-app AGENTS.md without cross-linking `agents/WEB_INTEGRATION.md`
- **Never** delete a `_merged/<src>/app/` subtree without first completing the integration tasks above — those are the source-of-truth for the merge

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`tanstack-start`](../.agents/skills/tanstack-start/SKILL.md) | React framework (file-based routing, server functions, RSC v1.94+) |
| [`copilotkit-develop`](../.agents/skills/copilotkit-develop/SKILL.md) | CopilotKit v2 (chat interfaces, frontend tools, runtime wiring) |
| [`ag-ui`](../.agents/skills/ag-ui/SKILL.md) | The AG-UI SSE protocol (agent↔UI streaming) |
| [`hono`](../.agents/skills/hono/SKILL.md) | The Hono API gateway pattern |
| [`cloudflare`](../.agents/skills/cloudflare/SKILL.md) | Workers + Pages + R2 + D1 + Vectorize |
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | The model + schema registry |
| [`schema-codegen`](../.agents/skills/schema-codegen/SKILL.md) | The BAML → Zod → Convex → CopilotKit codegen pipeline (NEW) |

<!-- generated: 2026-07-29; updated per 2026-08-26-wave-5-web-consolidation-v2 PR (filesystem layer) -->
