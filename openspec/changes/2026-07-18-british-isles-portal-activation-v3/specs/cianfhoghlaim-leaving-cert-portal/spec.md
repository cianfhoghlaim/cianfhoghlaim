## ADDED Requirements

### Requirement: study_plan.baml BAML schema (ExtractStudyPlan) (R11)

The system SHALL provide a BAML file at `baml/portal/study_plan.baml`
that defines the `StudyPlan` class + the `ExtractStudyPlan` function +
the `GenerateStudyPlanAssets` function. The BAML file SHALL be the
**single source of truth** for all four agentic-chat outputs (JSON +
PDF + marimo + Convex).

The `StudyPlan` class SHALL contain: `subject` (one of 8 NCCA LC subjects),
`subnation` (one of 6: Éire / NI / Scotland / England / Wales / IsleOfMan),
`language` (`"en"` or `"ga"`), `student_level` (`"ordinary"` or `"higher"`),
`objectives` (StudyObjective[]), `topics` (StudyTopic[] ordered by
marks ÷ study-hours), `total_hours` (int), `assets` (AssetDescriptor[]),
`notebook_ref` (string?), `pdf_ref` (string?).

#### Scenario: A developer reads the study-plan schema

- **GIVEN** a developer reads `baml/portal/study_plan.baml`
- **WHEN** they look at the `StudyPlan` class
- **THEN** they see all 10 fields documented with EN + GA descriptions
- **AND** the BAML file passes `mise run baml:cli:test`

#### Scenario: ExtractStudyPlan dispatches through LlamaSwap

- **GIVEN** the user asks the agentic chat for a Mathematics Higher study plan in GA
- **WHEN** `ExtractStudyPlan` is invoked
- **THEN** the dispatcher routes to `uccix-mistral-24b` (Irish)
- **AND** the resulting JSON has `language = "ga"`

### Requirement: CocoIndex v1 App portal_study_plan_embedding (R12)

The system SHALL provide a CocoIndex v1 App at
`cocoindex/portal_study_plan_embedding.py` that conforms to the R1-R4
contract documented in `openspec/specs/oideachais-cocoindex-v1-migration/spec.md`.

The App SHALL mount its target on the canonical LanceDB table
`oideachais.portal.study_plan_chunks` using `BAAI/bge-m3` (1024-d)
as the shared embedder via the canonical `_lifespan.py` shared home.

#### Scenario: A developer reads the App skeleton

- **WHEN** the developer opens `cocoindex/portal_study_plan_embedding.py`
- **THEN** they see the 4 wrapper files (`_lifespan.py`, `_assets.py`, `__init__.py`, `test_smoke.py`)
- **AND** the R1-R4 conformance contract check passes

### Requirement: MotherDuck Dive + daily Flight (R13)

The system SHALL provide a MotherDuck Dive named `lc_study_plan_dive`
that renders a KPI strip + a filterable table + a trend chart over the
`oideachais.portal.study_plan_chunks` LanceDB companion.

The system SHALL also provide a daily MotherDuck Flight named
`lc_study_plan_flight` that runs `dagster materialise -a study_plan_extract`
once per day.

#### Scenario: A user opens the Dive

- **GIVEN** `oideachais.portal.study_plan_chunks` has at least 1 row
- **WHEN** the user opens the Dive URL
- **THEN** the KPI strip renders with ≥ 3 metrics (study plans / week, subnation coverage %, asset fan-out histogram)
- **AND** the filterable table renders all rows

#### Scenario: The daily Flight runs

- **WHEN** the cron fires
- **THEN** `lc_study_plan_flight` materialises the `study_plan_extract` Dagster asset
- **AND** the BAML row backfill runs against the freshest MotherDuck rows
- **AND** the marimo notebook is regenerated

### Requirement: Cloudflare R2 + Hono-issued signed URLs (R14)

The system SHALL provide a Cloudflare R2 bucket named `oideachais-pdfs`
plus a Hono route on the `hono-api` service that issues **signed GET
URLs** valid for 15 minutes. (No Cloudflare Worker is required — the
Hono service already has S3 credentials via the Garage S3 backend, so
signed URLs are issued from `hono-api` directly. This keeps the project
on the Cloudflare free tier with no Workers Paid subscription required.)

The R2 bucket is provisioned by the `portal-cloudflare-r2` stack at
`bonneagar/stacks/portal-cloudflare-r2/` (in the `bonneagar/` worktree
per `cross-repo-sync.md`) following the 6-file GOLD_STANDARD pattern
documented in `openspec/specs/infrastructure-stacks/spec.md`.

#### Scenario: A user clicks a PDF in the library

- **GIVEN** the user opens `/en/leaving-cert/mathematics` and clicks "Maths HL 2024 PDF"
- **WHEN** the click fires
- **THEN** the Hono route calls `hono-api` `/api/r2/sign?key=...`
- **AND** `hono-api` returns a signed R2 URL valid for 15 minutes
- **AND** the browser downloads the PDF (200 response)

#### Scenario: Free-tier guardrail

- **WHEN** the operator reads `bonneagar/stacks/portal-cloudflare-r2/README.md`
- **THEN** the document calls out the Cloudflare free-tier limits (10 GB storage, 1M Class A ops/mo)
- **AND** the document notes that signed URLs are issued from Hono (no Workers Paid required)

### Requirement: Marimo notebook deployed to Cloudflare (R15)

The system SHALL deploy the 6 existing per-subject marimo study tools at
`notebooks/12_subject_study_tools/<subject>.py` to Cloudflare Workers +
Container on TCP 8080, served from `portal-marimo.cianfhoghlaim.ie`.

This pattern follows `openspec/specs/official-media-marimo/spec.md` R4
(the canonical marimo-on-Cloudflare deployment).

#### Scenario: A user opens the embedded marimo notebook

- **GIVEN** the user is on `/ga/leaving-cert/mata` and clicks "Féach ar an bplean staidéir"
- **WHEN** the click fires
- **THEN** the `<MarimoEmbed>` mounts the `*.workers.dev` URL in an iframe
- **AND** the notebook loads in the user's locale

### Requirement: Storybook design system (R16)

The system SHALL provide a Storybook 8 + Vite-plugin instance at
`cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web/.storybook/`
with ≥ 18 stories + the `<Ci*>` component family + the bilingual EN+GA
labels + dark/light themes.

#### Scenario: A developer opens Storybook

- **GIVEN** the developer runs `bun run storybook` in the leaving-cert app
- **WHEN** Storybook loads
- **THEN** they see ≥ 18 stories
- **AND** every story has both EN + GA label sets
- **AND** the dark/light theme toggle works

### Requirement: 4-stage pipeline → UI loop (Aistear → Primary → JC → LC + Tertiary) (R17)

The system SHALL render 4 (+1) stage breadcrumbs on the central portal
home page. The **primary 3 stages** (Primary / Junior Cycle / Leaving
Cycle) are populated in v1 from the existing per-stage BAML extraction
files + CocoIndex apps + notebooks. The **Aistear + Tertiary stages**
are **deferred to v2** (a follow-up openspec change) — their tabs
render with a "Phase 2 coming soon" badge and link to the BAML
extraction function documentation.

| Stage | BAML source | CocoIndex app | Notebook(s) | v1 status |
|---|---|---|---|---|
| **Aistear** | `baml/education/stages/aistear.baml` | (deferred — does not exist yet) | `notebooks/07_educational_stages/aistear.py` | **Phase 2 badge** |
| **Primary** | `baml/education/stages/primary.baml` + `baml/education/primary/primary_extraction.baml` | `primary_embedding.py` | `notebooks/07_educational_stages/primary.py` | **v1 active** |
| **Junior Cycle** | `baml/education/stages/junior_cycle.baml` + `baml/education/junior_cycle/junior_cycle_extraction.baml` | `junior_cycle_embedding.py` | `notebooks/07_educational_stages/junior_cycle.py` | **v1 active** |
| **Leaving Cycle** | `baml/education/stages/senior_cycle.baml` + `baml/education/lc_extraction/*.baml` + 6 `<subject>_web.baml` | 8 per-subject `*_embedding.py` + `cross_subject_competency_embedding.py` | 23 + 7 + 6 notebooks | **v1 active** |
| **Tertiary** | `baml/education/stages/tertiary.baml` | (deferred — does not exist yet) | `notebooks/07_educational_stages/tertiary.py` | **Phase 2 badge** |

The stage breadcrumbs SHALL be populated dynamically from the 5 stage
BAML extraction files via the `ExtractAistearFramework` /
`ExtractPrimaryLearningOutcomes` / `ExtractJCSpec` /
`ExtractSeniorCycleSubject` / `ExtractTertiaryProgramme` functions
(declared in `baml/education/stages/{aistear,primary,junior_cycle,senior_cycle,tertiary}.baml`).

For v2 (deferred), the `Aistear` and `Tertiary` CocoIndex apps
(`aistear_embedding.py`, `tertiary_embedding.py`) will be added to
`cianfhoghlaim/cocoindex/` as CocoIndex v1 Apps (R1–R4 conformant)
following the pattern of the existing `primary_embedding.py` +
`junior_cycle_embedding.py` apps.

#### Scenario: A user clicks the Aistear tab (v1 deferred state)

- **GIVEN** the user is on `portal.cianfhoghlaim.ie/en`
- **WHEN** they click the "Aistear" breadcrumb
- **THEN** the page renders the 4 Aistear themes from the BAML extraction
- **AND** a "Phase 2 — CocoIndex embedding coming soon" badge is shown
- **AND** the underlying data is sourced from `ExtractAistearFramework`

#### Scenario: A user clicks the Primary tab

- **GIVEN** the user clicks the "Primary" breadcrumb
- **WHEN** the page loads
- **THEN** it renders 4 cards: English / Gaeilge / Mathematics / SESE
- **AND** each card shows the learning outcomes extracted by `ExtractPrimaryLearningOutcomes`
- **AND** no Phase 2 badge is shown (v1 active)

#### Scenario: A user clicks the Junior Cycle tab

- **GIVEN** the user clicks the "Junior Cycle" breadcrumb
- **WHEN** the page loads
- **THEN** it renders a grid of 24 JC subjects
- **AND** each subject shows the assessment components + CBA tasks extracted by `ExtractJCSpec`
- **AND** no Phase 2 badge is shown (v1 active)

#### Scenario: A user clicks the Leaving Cycle tab

- **GIVEN** the user clicks the "Leaving Cycle" breadcrumb
- **WHEN** the page loads
- **THEN** it renders 6 LC subject cards (Mathematics / Chemistry / Geography / Gaeilge / English / Computer Science)
- **AND** each card shows the 5 NCCA Key Competency weights (populated from `cross_subject_competency_embedding.py`)
- **AND** clicking a subject navigates to the existing per-subject route at `routes/en/subjects/<subject>/`
- **AND** no Phase 2 badge is shown (v1 active)

#### Scenario: A user clicks the Tertiary tab (v1 deferred state)

- **GIVEN** the user clicks the "Tertiary" breadcrumb
- **WHEN** the page loads
- **THEN** a "Phase 2 — coming soon" badge is shown
- **AND** the page links to the `ExtractTertiaryProgramme` BAML function documentation

### Requirement: A2UI declarative surfaces emitted by the 8 NCCA ADK specialists (R18)

The system SHALL enable CopilotKit v2 A2UI (`runtime.a2ui: {}`) on the
server + `<CopilotKit a2ui={{ theme, catalog }}>` on the client. The
A2UI catalog at
`cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web/packages/ui/a2ui-catalog.tsx`
SHALL map each of the 6 per-subject BAML `<subject>_web.baml` output
classes to an A2UI component definition + renderer:

| BAML class | A2UI definition | A2UI renderer |
|---|---|---|
| `MathematicsWebStudyPlanResponse` (+ 5 siblings) | `StudyPlanCard` | `<StudyPlanCard>` |
| `MathematicsStudyWeek` (+ 5 siblings) | `WeekTimeline` | `<WeekTimeline>` |
| `MathematicsStudyMilestone` (+ 5 siblings) | `MilestoneBadge` | `<MilestoneBadge>` |
| `MathematicsWebExamPaperDiscussionResponse` (+ 5 siblings) | `ExamPaperCard` | `<ExamPaperCard>` |
| `MathematicsMarksBreakdown` (+ 5 siblings) | `MarksBreakdownTable` | `<MarksBreakdownTable>` |
| `MathematicsKCWeight` (+ 5 siblings) | `KCWeightsBar` | `<KCWeightsBar>` |
| (per-stage BAML output) | `StageOverview` | `<StageOverview>` |
| (per-subject CocoIndex query) | `SubjectCard` | `<SubjectCard>` |
| (marimo embed) | `MarimoEmbed` | `<MarimoEmbed>` |
| (R2 signed URL) | `PdfLibraryPanel` | `<PdfLibraryPanel>` |
| (existing) | `TranslationToggle` | `<CiTranslationToggle>` |

The 8 NCCA ADK specialists
(`cianfhoghlaim/agents/tuatha/{math,chem,geog,gael,engl,comp,appm,hist}_agent.py`)
SHALL be registered as CopilotKit dispatch targets and SHALL emit A2UI
operations (`createSurface` / `updateComponents` / `updateDataModel`)
when responding to user queries.

The 18 per-subject workflow handlers
(`_workflow_handlers.py::make_study_plan_handler` /
`discuss_exam_paper_handler` / `explain_marking_scheme_handler` × 6
subjects) SHALL be the dispatcher entry points for the A2UI surface
generation.

#### Scenario: A user asks Mathematics agent for a study plan

- **GIVEN** the user is on `/en/leaving-cert/mathematics` and opens the CopilotKit sidebar
- **WHEN** they type "give me a 12-week study plan for HL Maths"
- **THEN** the orchestrator dispatches to `math_agent`
- **AND** `make_study_plan_handler` invokes `b.WebStudyPlan(subject="mathematics", weeks_until_exam=12, target_level="LC_HL", language="en")`
- **AND** the agent emits `createSurface({ surfaceId: "study-plan-card", ... })` with the BAML output
- **AND** the client auto-mounts `<StudyPlanCard>` via `createA2UIMessageRenderer`

#### Scenario: A user asks Gaeilge agent for a past paper discussion (in Irish)

- **GIVEN** the user is on `/ga/leaving-cert/gaeilge`
- **WHEN** they type "déan plé ar Pháipéar 2 2024" (discuss Paper 2 2024)
- **THEN** the orchestrator dispatches to `gael_agent`
- **AND** `discuss_exam_paper_handler` invokes `b.WebExamPaperDiscussion(subject="gaeilge", paper_year=2024, paper_level="LC_HL", paper_language="ga", question_text="...")`
- **AND** the agent emits `createSurface({ surfaceId: "exam-paper-card", ... })` with bilingual EN+GA labels

### Requirement: Central portal entry — British Isles map click-through (R19)

The system SHALL provide a central portal entry at
`portal.cianfhoghlaim.ie` that renders:

1. The British Isles map (R7 — accurate OSM base, 6 subnations, 5 NCCA Key Competencies as land-marks, 8 NCCA subjects as overlay buttons)
2. The 4-stage breadcrumbs (R17)
3. The 6 LC subject cards (R18) reachable from the LC tab
4. The A2UI catalog (R18) wired to the 8 NCCA ADK specialists

The central portal SHALL be the **single entry point** for all 30
existing per-subject routes
(`apps/.../routes/en/subjects/<subject>/{index,syllabus,exam-papers,marking-schemes,study-plan}.tsx`).

#### Scenario: A user opens the central portal

- **GIVEN** the user navigates to `portal.cianfhoghlaim.ie`
- **WHEN** the page loads
- **THEN** the British Isles map renders with Éire active
- **AND** the 4-stage breadcrumbs render (Aistear / Primary / JC / LC / Tertiary)
- **AND** clicking "Leaving Cycle" shows the 6 LC subject cards
- **AND** clicking "Mathematics" navigates to `/en/subjects/mathematics/`

#### Scenario: A user clicks Mathematics then asks for a study plan

- **GIVEN** the user is on `/en/subjects/mathematics/`
- **WHEN** they click "Generate study plan" in the CopilotKit sidebar
- **THEN** the A2UI surface `<StudyPlanCard>` mounts via `createA2UIMessageRenderer`
- **AND** the plan is sourced from `b.WebStudyPlan(subject="mathematics", ...)`

### Requirement: Machine-readable infrastructure (R21) — PDF-REF

The system SHALL publish design tokens, component schemas, and layout
contracts in **machine-readable form**: CSS custom properties (consumed
by every `<Ci*>` component) + TypeScript types (consumed by every React
component) + JSON Schema (consumed by the A2UI catalog) + BAML classes
(consumed by the BAML extraction layer) + A2UI catalog definitions
(consumed by the agent runtime).

No design decision SHALL be encoded only in prose, screenshots, or
Figma files. Every visual property MUST be traceable to a
machine-readable source.

#### Scenario: A designer updates the primary colour

- **GIVEN** the designer changes `--color-primary` in `tokens.css`
- **WHEN** the change is committed
- **THEN** every `<Ci*>` component + every A2UI catalog entry + every Storybook story + every marimo notebook cell re-renders with the new colour
- **AND** the CI gate `bun run tokens:validate` confirms the change propagated to all 5 sources (`.css`, `.ts`, `.schema.json`, `.baml`, `a2ui-catalog.tsx`)

#### Scenario: A new component is added

- **GIVEN** a developer adds `<CiFoo>` to `packages/ui/`
- **WHEN** the CI runs
- **THEN** the new component imports from `tokens.ts` (verified by `bun run tokens:validate`)
- **AND** the A2UI catalog is updated (verified by snapshot test)
- **AND** a Storybook story is added (verified by Storybook build)

### Requirement: Design-tokens-as-code pipelines (R22) — PDF-REF

The system SHALL treat design tokens as code: `tokens.css` SHALL be the
**single source of truth**, version-controlled, validated in CI, and
consumed by every `<Ci*>` component, A2UI catalog entry, Storybook
story, and marimo notebook cell.

The CI gate SHALL be `bun run tokens:validate`, which:
1. Parses `tokens.css` and emits a normalized JSON token set
2. Compares the JSON against `tokens.ts` (TypeScript types) + `tokens.schema.json` + `tokens.baml`
3. Fails the build if any source is out of sync

#### Scenario: A token drift is detected

- **GIVEN** a developer adds a new token to `tokens.css` but forgets to update `tokens.ts`
- **WHEN** the CI runs
- **THEN** `bun run tokens:validate` fails with a diff message
- **AND** the PR is blocked until the developer updates `tokens.ts`

### Requirement: MCP-driven AI UI generation + self-heal (R23) — PDF-REF

The system SHALL expose the design tokens + A2UI catalog + Storybook
via a **Model Context Protocol (MCP) server** so that AI agents can
autonomously generate, test, and self-heal UI surfaces WITHOUT
violating the design system or generating unusable code.

The MCP server SHALL live at
`cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web/packages/mcp/design-system-server.py`
and SHALL expose 4 tools:

| Tool | Purpose |
|---|---|
| `tokens_get()` | Returns the full token set as JSON |
| `catalog_list()` | Returns the A2UI catalog (definitions + renderers) |
| `catalog_render(component, props)` | Validates a component + props against the catalog schema; refuses to emit invalid combinations |
| `storybook_stories(component)` | Returns the Storybook stories for a component |

`catalog_render` SHALL refuse to emit components that violate the
design system contract (banned colours, wrong fonts, invalid layouts).
On failure, it SHALL return a `suggested_fix` field with a
machine-readable remediation.

#### Scenario: An AI agent generates a StudyPlanCard

- **GIVEN** the agent has access to the MCP server
- **WHEN** it calls `catalog_render("StudyPlanCard", { weeks: 12, ... })`
- **THEN** the server validates the component + props against the catalog schema
- **AND** returns the rendered React JSX
- **AND** returns a `storybook_snapshot_id` for visual regression testing

#### Scenario: An AI agent violates the design system

- **GIVEN** the agent calls `catalog_render("StudyPlanCard", { color: "#FF0000" })`
- **WHEN** the server validates the props
- **THEN** the server refuses to emit the component
- **AND** returns `{ error: "banned_colour", suggested_fix: { color: "var(--color-primary)" } }`

#### Scenario: Self-heal after validation failure

- **GIVEN** the agent receives the `suggested_fix`
- **WHEN** it retries with the suggested props
- **THEN** the second call succeeds
- **AND** the result is committed to the codebase via `git apply`

### Requirement: Pocket ID SSO unification (R24) — PDF-REF

The system SHALL use Pocket ID OIDC as the **single** SSO provider
across all 5 canonical surfaces + the central portal. The 5 OIDC
audiences SHALL be:

| Audience | Surface |
|---|---|
| `convex_backend` | Convex (all surfaces) |
| `croilar_web` | `croilar-web` |
| `croilar_portal` | `croilar-portal` |
| `leaving_cert_portal` | `cianfhoghlaim-leaving-cert` (5th surface) |
| `portal` | `portal.cianfhoghlaim.ie` (central portal entry) |

The 5th surface SHALL wire `@croilar/auth` from
`web/packages/auth/` (already populated per the existing
`agentic-frontend-frameworks` spec R-BetterAuth).

#### Scenario: A user logs into the central portal

- **GIVEN** the user opens `portal.cianfhoghlaim.ie`
- **WHEN** they click "Sign in with Pocket ID"
- **THEN** they are redirected to the Pocket ID OIDC issuer
- **AND** on success, the JWT contains the `portal` audience claim
- **AND** the user can access all per-subject routes behind the same SSO

#### Scenario: SSO audience mismatch

- **GIVEN** a JWT issued for `croilar_web` is presented to the 5th surface
- **WHEN** the 5th surface validates the JWT
- **THEN** the validation fails with `audience_mismatch`
- **AND** the user is redirected to Pocket ID for re-authentication

### Requirement: Sequential domain-by-domain migration (R25) — PDF-REF

The system SHALL NOT execute big-bang cutovers. Each new portal
feature SHALL be deployed behind a **feature flag** with a phased
rollout: 10% of traffic for 24 hours → 50% for 24 hours → 100% after
48 hours of green metrics. Rollback SHALL be automatic on any error
rate > 1%.

The rollout pattern SHALL use the Dagster 5-layer Declarative
Automation sensor pattern (per
`openspec/specs/dagster-5-layer-component-architecture/spec.md`).

The rollout for the central portal entry SHALL be gated by the
`portal_rollout` feature flag (env var `PORTAL_ROLLOUT=10|50|100`).

#### Scenario: The central portal rolls out

- **GIVEN** the central portal is deployed behind the `portal_rollout` feature flag
- **WHEN** the rollout sensor fires
- **THEN** the flag moves to 10% for 24 hours
- **AND** then 50% for 24 hours
- **AND** then 100% if error rate stays below 1%
- **AND** any error rate spike triggers automatic rollback

#### Scenario: Rollback on error spike

- **GIVEN** the flag is at 50%
- **WHEN** the error rate exceeds 1%
- **THEN** the rollout sensor fires a rollback
- **AND** the flag moves back to 10%
- **AND** a Slack alert is sent to `#cianfhoghlaim-ops`
