# Tasks — British Isles Portal Activation v3

> **Demo chosen:** B v3 (Activate the 5th surface + pipeline-driven
> A2UI + PDF-REF items folded in). Total estimate: ~84 h across 6 phases.
> Pre-reqs: Convex deployment status, Workers Paid sign-off, Aistear +
> Tertiary CocoIndex app existence.

## Phase 0 — OpenSpec change skeleton (2 h)

- [ ] `openspec/changes/2026-07-18-british-isles-portal-activation-v3/proposal.md` (this file)
- [ ] `openspec/changes/2026-07-18-british-isles-portal-activation-v3/tasks.md` (this file)
- [ ] `openspec/changes/2026-07-18-british-isles-portal-activation-v3/cross-repo-sync.md`
- [ ] `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md` (MODIFIED +R11–R25)
- [ ] `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/agentic-frontend-frameworks/spec.md` (MODIFIED + 5th-surface lock)
- [ ] `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-baml-schemas/spec.md` (MODIFIED + cross-ref)
- [ ] `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/british-isles-education-pipeline/spec.md` (MODIFIED + central portal entry)
- [ ] `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/ireland-primary-jc-dlt-baml/spec.md` (MODIFIED + Primary + JC tabs)
- [ ] `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/official-media-marimo/spec.md` (MODIFIED + cross-ref)
- [ ] `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/meaisinfhoghlaim-agent-frameworks/spec.md` (MODIFIED + 8 ADK specialists + 18 handlers)
- [ ] `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/infrastructure-stacks/spec.md` (MODIFIED + portal-cloudflare-r2 stack + Pocket ID SSO)
- [ ] `openspec validate 2026-07-18-british-isles-portal-activation-v3 --strict` passes

## Phase 1 — A2UI catalog + central portal entry (24 h) → R18 + R19

### 1.1 A2UI runtime middleware (4 h)

- [ ] `apps/api/src/runtime.ts` — `CopilotRuntime({ a2ui: { catalog } })`
- [ ] `apps/web/src/root.tsx` — `<CopilotKit a2ui={{ theme: <CiTheme>, catalog }}>`
- [ ] Verify `/info` returns `a2uiEnabled: true`

### 1.2 A2UI catalog (`packages/ui/a2ui-catalog.tsx`) (16 h)

- [ ] `StudyPlanCard`, `WeekTimeline`, `MilestoneBadge`, `ExamPaperCard`, `MarksBreakdownTable`, `KCWeightsBar`, `StageOverview`, `SubjectCard`, `MarimoEmbed`, `PdfLibraryPanel`, `TranslationToggle`
- [ ] Bilingual EN+GA labels verified

### 1.3 Central portal entry (4 h)

- [ ] `routes/index.tsx` — British Isles map (SVG + D3 + Babylon.js overlay)
- [ ] `routes/en/[stage]/index.tsx`, `routes/ga/[stage]/index.tsx` — Primary + JC + LC render with v1 data; Aistear + Tertiary render with "Phase 2 coming soon" badge (R17 deferred scope)
- [ ] `routes/en/[stage]/[subject]/index.tsx`, `routes/ga/[stage]/[subject]/index.tsx`

## Phase 2 — Marimo embedding + R2 + IaC (24 h) → R14 + R15

### 2.1 Marimo on Cloudflare (8 h)

- [ ] Deploy 6 existing `notebooks/12_subject_study_tools/<subject>.py` to `portal-marimo.cianfhoghlaim.ie`

### 2.2 Cloudflare R2 + Hono-issued signed URLs (8 h)

- [ ] `bonneagar/stacks/portal-cloudflare-r2/` (compose.yaml + wrangler.jsonc + README + docs/STACK.md — **NO Worker block**)
- [ ] `bonneagar/komodo/resource-syncs/portal.yaml`
- [ ] `bonneagar/pangolin/resources/portal.yaml` → `portal.cianfhoghlaim.ie`
- [ ] Hono route added to `hono-api` at `/api/r2/sign` that returns a signed R2 URL (15-min TTL) using Garage S3 credentials
- [ ] Leaving-cert `apps/api/src/routes/pdf-library.ts` calls `/api/r2/sign` instead of a Cloudflare Worker

### 2.3 MotherDuck Dive + daily Flight (8 h)

- [ ] `lc_study_plan_dive` + `lc_study_plan_flight`

## Phase 3 — Storybook + observability (12 h) → R16

### 3.1 Storybook 8 + Vite-plugin (8 h)

- [ ] `apps/web/.storybook/main.ts`
- [ ] `apps/web/src/styles/tokens.css`
- [ ] ≥ 18 stories
- [ ] Dark/light themes + bilingual EN+GA labels

### 3.2 Observability — Langfuse + MLflow + RAGAS (4 h)

- [ ] Langfuse `@observe` + MLflow experiment + RAGAS `asset_check`

## Phase 4 — PDF-REF items R21–R25 (16 h)

### 4.1 R21 — Machine-readable infrastructure (3 h)

- [ ] Publish `tokens.css` + `tokens.ts` + `tokens.schema.json` + `tokens.baml`
- [ ] CI validation: every `<Ci*>` component imports from `tokens.ts`

### 4.2 R22 — Design-tokens-as-code pipeline (3 h)

- [ ] `apps/web/src/styles/tokens.css` as single source of truth
- [ ] CI gate: `bun run tokens:validate` (catches drift between `.css` + `.ts` + `.baml`)
- [ ] Every Storybook story consumes tokens (verified in 3.1)

### 4.3 R23 — MCP-driven AI UI generation (6 h) ← NEW

- [ ] `packages/mcp/design-system-server.py` — MCP server exposing:
  - `tokens_get()` — returns the full token set
  - `catalog_list()` — returns the A2UI catalog
  - `catalog_render(component, props)` — validates a component + props against the catalog schema
  - `storybook_stories(component)` — returns the Storybook stories for a component
- [ ] Validation gate: `catalog_render` refuses to emit components that violate the design system contract
- [ ] Self-heal: `catalog_render` returns a `suggested_fix` when validation fails
- [ ] Smoke test: AI agent successfully generates a `<StudyPlanCard>` via the MCP server

### 4.4 R24 — Pocket ID SSO unification (3 h) ← NEW

- [ ] Verify Pocket ID is the SSO provider on the 5th surface
- [ ] Add 2 new OIDC audiences: `leaving_cert_portal`, `portal`
- [ ] Document the 5 OIDC audiences in `infrastructure-stacks/spec.md`

### 4.5 R25 — Sequential domain-by-domain migration (1 h) ← NEW

- [ ] Document the feature-flag rollout pattern via the Dagster Declarative Automation sensor (10% → 50% → 100% over 7 days, error rate > 1% triggers auto-rollback)
- [ ] Wire `portal_rollout` to the existing Dagster sensor
- [ ] Apply feature flag to the central portal entry

## Phase 5 — IaC deploy + spec archive (6 h)

> **BLOCKER:** Phase 5 cannot run until the `conic-leaving-cert` Convex
> deployment is live (kick off `2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow`
> if not already in flight).

- [ ] `bun run preflight:arm-oci` BEFORE any `iac:bootstrap`
- [ ] `bun run iac:plan --stack portal-cloudflare-r2`
- [ ] `bun run iac:deploy --stack portal-cloudflare-r2`
- [ ] `bun run spec:validate 2026-07-18-british-isles-portal-activation-v3 --strict` passes
- [ ] `bun run spec:archive 2026-07-18-british-isles-portal-activation-v3 --yes`

## Cross-repo-sync plan

| Repo | Branch | Commits | Push target |
|---|---|---|---|
| `cianfhoghlaim` | `feat/2026-07-18-british-isles-portal-activation-v3` | 5 (one per phase) | `origin` |
| `bonneagar` | `feat/2026-07-18-portal-cloudflare-r2-stack-v3` | 1 (the IaC subtree) | `origin` |
