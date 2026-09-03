## Deferred - Blocked on cross-region-pipeline spec

This change is **deferred** pending the `cross-region-pipeline` capability spec (currently `requirements 0` in `openspec/specs/cross-region-pipeline/spec.md`).

When that spec is added, this work can be re-scoped under the British Isles / Americas / EU / Commonwealth umbrella. No code has been written for this change.

## Deferred - Blocked on cross-region-pipeline spec

This change is **deferred** pending the `cross-region-pipeline` capability spec (currently `requirements 0` in `openspec/specs/cross-region-pipeline/spec.md`).

When that spec is added, this work can be re-scoped under the British Isles / Americas / EU / Commonwealth umbrella. No code has been written for this change.

# 2026-07-18-british-isles-portal-activation-v3

> **Demo chosen:** B (Activate the 5th canonical surface).
> **v3 revision:** PDF-REF items now RESOLVED as 5 ADDED Requirements
> (R21–R25). The PDF's `cio-web/` target path was a pre-v4 proposal
> that did not land as proposed (the actual v4 consolidation kept the
> existing bun workspace paths + added the 5th surface
> `cianfhoghlaim-leaving-cert/`). The PDF's UI/UX + IaC recommendations
> remain valid and apply to the 5th surface.
> **Status:** Final draft awaiting your confirmation.

## Why

The existing per-subject web surface (72 source files) + the 8 NCCA
ADK specialists + the 18 workflow handlers + the 6 per-subject
marimo study tools + the 5 stage BAML extraction files + the 8
per-subject CocoIndex embedding apps **already exist**. What is
missing is:

1. **A central portal** — the British Isles map + click-through that
   funnels users into the existing per-subject surfaces.
2. **A2UI declarative surfaces** — the per-subject BAML `<subject>_web.baml`
   schemas emit rich structured output that is currently rendered by
   hand-coded React. A2UI lets the **agent emit the UI directly**.
3. **4-stage pipeline → UI loop** — the Aistear → Primary → JC → LC
   breadcrumbs that pull from the existing per-stage BAML extraction
   files + stage CocoIndex apps + the educational-stages notebooks.
4. **Marimo notebook embedding** — student-facing deployment via the
   canonical `marimo-on-Cloudflare-Workers + Container` pattern.
5. **PDF-REF items (R21–R25)** — the 5 recommendations from the
   "AI-Assisted UI/UX and IaC Integration" document: machine-readable
   infrastructure, design-tokens-as-code, MCP-driven AI UI generation,
   Pocket ID SSO unification, sequential domain-by-domain migration.
6. **IaC for the Cloudflare R2 stack** — the new `portal-cloudflare-r2`
   stack + the Komodo sync + the Pangolin route.

## What changes

### 1. No new umbrella spec

The canonical spec is already
`openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md` (R1–R10).
This change extends it with R11–R25 (15 ADDED Requirements) and
locks the 5th surface table in `agentic-frontend-frameworks/spec.md`.

### 2. Architectural cross-references (from the PDF)

The PDF's architectural-context section is a *restatement* of specs
already in the repo. Each PDF claim links to its existing spec:

| PDF claim | Existing spec / file |
|---|---|
| 5-stage Dagster pipeline | `dagster-5-layer-component-architecture/spec.md` |
| `[tool.dg].registry_modules` | `pyproject.toml` |
| DLT → DuckLake (Parquet + Garage S3 + Postgres catalog) | `cianfhoghlaim-pipeline/spec.md` R-DuckLake |
| BAML → CocoIndex v1 → LanceDB HNSW | `cianfhoghlaim-cocoindex-v1-migration/spec.md` |
| Cognee knowledge graph | `agent-memory-systems/spec.md` R-Cognee |
| OCR registry: 9 vision + 4 classical + 3 image-generation | `meaisinfhoghlaim-ocr-htr/spec.md` |
| 12-agent fleet | `meaisinfhoghlaim-platform/spec.md` + `agent-registry/spec.md` |
| Memory: Cognee + Graphiti + LanceDB + FalkorDB + Memgraph | `agent-memory-systems/spec.md` |
| Sequential migration (no big-bang) | R25 (new, this change) |
| Pocket ID SSO unification | R24 (new, this change) |
| 30-40% historical code duplication | resolved by v4 consolidation (2026-06-28) |
| Embedded Hono API gateway | `agentic-frontend-frameworks/spec.md` R-HonoApi |

### 3. 15 ADDED Requirements to `cianfhoghlaim-leaving-cert-portal/spec.md`

| ID | Title | Origin |
|---|---|---|
| R11 | `study_plan.baml` BAML schema (ExtractStudyPlan) | v2 |
| R12 | CocoIndex v1 App `portal_study_plan_embedding` | v2 |
| R13 | MotherDuck Dive `lc_study_plan_dive` + daily Flight | v2 |
| R14 | Cloudflare R2 bucket `cianfhoghlaim-pdfs` + Worker | v2 |
| R15 | marimo notebook deployed to `*.workers.dev` | v2 |
| R16 | Storybook design system (≥ 18 stories + `<Ci*>`) | v2 |
| R17 | 4-stage pipeline → UI loop (Aistear → Primary → JC → LC + Tertiary) | v2 |
| R18 | A2UI declarative surfaces emitted by the 8 NCCA ADK specialists | v2 |
| R19 | Central portal entry — British Isles map click-through | v2 |
| R20 | (placeholder — superseded by R21–R25) | v2 (deferred) |
| **R21** | **Machine-readable infrastructure** | **PDF-REF** |
| **R22** | **Design-tokens-as-code pipelines** | **PDF-REF** |
| **R23** | **MCP-driven AI UI generation + self-heal** | **PDF-REF** |
| **R24** | **Pocket ID SSO unification** | **PDF-REF** |
| **R25** | **Sequential domain-by-domain migration** | **PDF-REF** |

### 4. MODIFIED deltas (8 specs)

| Spec | Reason |
|---|---|
| `cianfhoghlaim-leaving-cert-portal/spec.md` | MODIFIED +R11–R25 |
| `agentic-frontend-frameworks/spec.md` | MODIFIED + 5th-surface lock |
| `cianfhoghlaim-baml-schemas/spec.md` | MODIFIED + cross-ref to per-subject web schemas |
| `british-isles-education-pipeline/spec.md` | MODIFIED + central portal as entry point |
| `ireland-primary-jc-dlt-baml/spec.md` | MODIFIED + Primary + JC tabs |
| `official-media-marimo/spec.md` | MODIFIED + cross-ref |
| `meaisinfhoghlaim-agent-frameworks/spec.md` | MODIFIED + 8 ADK specialists + 18 workflow handlers |
| `infrastructure-stacks/spec.md` | MODIFIED + portal-cloudflare-r2 stack + Pocket ID SSO |

### 5. New code artifacts (in `cianfhoghlaim/`)

| File | Purpose |
|---|---|
| `baml/portal/study_plan.baml` | Single-source-of-truth BAML schema |
| `cocoindex/portal_study_plan_embedding.py` (+ 4 wrappers) | CocoIndex v1 App |
| `web/apps/cianfhoghlaim-leaving-cert/apps/web/packages/ui/a2ui-catalog.tsx` | A2UI catalog (11 component entries) |
| `web/apps/.../routes/index.tsx` (updated) | British Isles map + 4-stage breadcrumbs |
| `web/apps/.../routes/[stage]/index.tsx` | Stage overview |
| `web/apps/.../packages/mcp/design-system-server.py` | **NEW (PDF-REF R23)** — MCP server exposing design tokens + catalog |

### 6. New IaC artifacts (in `bonneagar/` worktree)

| File | Purpose |
|---|---|
| `bonneagar/stacks/portal-cloudflare-r2/compose.yaml` | 6-container compose stack |
| `bonneagar/stacks/portal-cloudflare-r2/wrangler.jsonc` | R2 + Worker + Pages |
| `bonneagar/stacks/portal-cloudflare-r2/README.md` | Free-tier limits called out |
| `bonneagar/stacks/portal-cloudflare-r2/docs/STACK.md` | 6-file GOLD_STANDARD pattern |
| `bonneagar/komodo/resource-syncs/portal.yaml` | Auto-sync to Komodo |
| `bonneagar/pangolin/resources/portal.yaml` | `portal.cianfhoghlaim.ie` route |

### 7. cross-repo-sync.md

2 repos: `cianfhoghlaim` + `bonneagar`.

## Cross-references

- [`openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md`](../specs/cianfhoghlaim-leaving-cert-portal/spec.md)
- [`openspec/specs/agentic-frontend-frameworks/spec.md`](../specs/agentic-frontend-frameworks/spec.md)
- [`openspec/specs/british-isles-education-pipeline/spec.md`](../specs/british-isles-education-pipeline/spec.md)
- [`openspec/specs/ireland-primary-jc-dlt-baml/spec.md`](../specs/ireland-primary-jc-dlt-baml/spec.md)
- [`openspec/specs/cianfhoghlaim-baml-schemas/spec.md`](../specs/cianfhoghlaim-baml-schemas/spec.md)
- [`openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md`](../specs/cianfhoghlaim-marimo-dashboards/spec.md)
- [`openspec/specs/official-media-marimo/spec.md`](../specs/official-media-marimo/spec.md)
- [`openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md`](../specs/meaisinfhoghlaim-agent-frameworks/spec.md)
- [`openspec/specs/infrastructure-stacks/spec.md`](../specs/infrastructure-stacks/spec.md)

## Dependencies

**Blocked by:**

- **`2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow`** — the `conic-leaving-cert` Convex deployment must be live before Phase 5 can run. This change cannot archive until the Convex deployment is verified live.

Soft dependencies (already shipped):

- `2026-07-12-baml-cli-test-ci-gate-v1`
- `2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow`
- `2026-07-16-biiep-v1-lc-per-subject-web-surface-v1` (30 routes + 36 Convex + 6 BAML)
- `2026-07-16-biiep-v1-lc-per-subject-agent-workflows-v1` (18 handlers + 8 ADK specialists)
- `2026-07-16-biiep-v1-lc-per-subject-marimo-study-tools-v1` (6 marimo study tools)
- `2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1`
- `2026-07-14-ireland-primary-jc-dlt-baml-v1`
- `2026-07-15-cianfhoghlaim-university-deep-extraction-v1`

## Risks

1. **R2 signed URL volume** — Cloudflare free tier is 1M Class A ops/mo + 10 GB storage. Mitigation: cache by `(subject, subnation, level)` key, evict after 30 days.
2. **Marimo on Workers Container** — requires Workers Paid ($5/mo). Documented in the stack README.
3. **8-subject scope** — only 6 are in-scope for the BIEP v1 LC web surface. Applied Maths + History are out-of-scope per `2026-07-16-biiep-v1-lc-per-subject-web-surface-v1` and would need a follow-up change.
4. **A2UI catalog drift** — the catalog must stay in sync with the BAML `<subject>_web.baml` output classes. CI gate via `baml-cli test` + a snapshot test for the catalog.
5. **MCP server scope creep** — R23 is bounded by the 4 tools documented in the requirement; any additional tools require a separate openspec change.

## Open questions — RESOLVED 2026-07-12

1. **`conic-leaving-cert` Convex deployment status** — **NOT YET DEPLOYED**. Will be provisioned by the `2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow` change (a hard blocker for this change).
2. **Workers Paid $5/mo sign-off** — **DECLINED**. Signed URLs will be issued from a Hono route on `hono-api` (which already has S3 credentials via Garage S3). Keeps Cloudflare on the free tier.
3. **Aistear + Tertiary CocoIndex apps** — **OUT OF SCOPE FOR v1**. These tabs will render with placeholder data + a "Phase 2" badge; the CocoIndex apps land in a follow-up change.
4. **`portal_rollout` feature flag infra** — **EXISTS** (Dagster Declarative Automation sensor). Phase 4.5 wires `portal_rollout` to it.

## Archive plan

- Archive after R11–R25 land and `portal.cianfhoghlaim.ie` resolves to a working British Isles map with at least Éire active + ≥1 working agentic chat that produces an A2UI surface for Mathematics.
- Follow-up Phase 2 change activates Scotland + Wales + England + NI + Isle of Man.
- Follow-up Phase 3 change adds the Aistear + Tertiary CocoIndex apps (if not already present).
