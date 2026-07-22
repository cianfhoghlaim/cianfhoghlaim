# Cianfhoghlaim Leaving Cert Portal Capability

## Purpose

`cianfhoghlaim-leaving-cert-portal` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/` (TanStack Start
front-end + Hono oRPC API + Convex `conic-leaving-cert` deployment) +
`cianfhoghlaim/{baml,cocoindex,dagster,dlt,leaving_certificate,notebooks}/<subject>/`
(per-subject end-to-end pipelines for the 8 NCCA Leaving Certificate
subjects + the 5 NCCA root-level programme PDFs).

This is the canonical openspec spec for the Leaving Cert portal. It
**supersedes** the deprecated `cianfhoghlaim-web` app (which is retired
as a prototype) and integrates with the `cianfhoghlaim-educational-mmo`
spec for the 8 NCCA ADK specialists + the `retro-game-asset-pipeline`
spec for the Diagram Generator + 3D Asset Gallery + the
`ncca-leaving-cert-root-pdfs` spec for the 5 NCCA root-level programme
PDFs.

## Background

Cianfhoghlaim is building the bilingual (EN + GA) educational portal
for the Republic of Ireland's **NCCA Leaving Certificate** curriculum.
The portal renders 8 NCCA LC subjects with 6 sections per subject +
4 diagram modes + a 2D + 3D asset gallery + a CopilotKit v2 chat +
an accurate British Isles map split into 6 subnations.

The 6 subnations are: Éire (Ireland, v1 active) + Northern Ireland +
Scotland + England + Wales + Isle of Man.

The 8 NCCA LC subjects are:

- mathematics
- applied_mathematics
- chemistry
- geography
- history
- english
- gaeilge
- computer_science

The public theming is currently professional + minimal (no mythological
overlay). The 8 NCCA subject specialists are referenced as the 8 subject
agents. The land is the British Isles; the wound is the language loss;
the healing is education.

The mythology / historical-sources theming layer will be introduced
**long after the full BIEP v1 lands** (see the
`british-isles-education-pipeline` spec for the cross-nation foundation
and the `2026-07-09-remove-brown-ajah-theming-v1` change for the
removal of the Brown Ajah / Wheel of Time lens).

The lore document `docs/CIANFHLOGHLAIM_LORE.md` (the operator's personal
triple-crown lineage — Cian Mac an Déisigh Uí Liatháin + Deacy + Lyons +
Morris + Conroy) is operator-only and NEVER displayed on the public
surface.
## Requirements
### Requirement: 8 NCCA LC Subjects × EN+GA (R1)

The system SHALL provide per-subject landing pages for the 8 NCCA Leaving
Certificate subjects (mathematics, applied_mathematics, chemistry, geography,
history, english, gaeilge, computer_science) in both EN and GA, with the
Leaving Cert 2026 exam-window compat for 7 legacy subjects
(mathematics, irish, biology, french, history, business, construction-studies).

#### Scenario: Mathematics bilingual landing page

- **GIVEN** the user navigates to `/en/leaving-cert/mathematics` or `/ga/leaving-cert/mata`
- **WHEN** the page loads
- **THEN** the syllabus section renders ≥1 topic per `qpack_mathematics.baml` topic
- **AND** the CopilotKit sidebar mounts in the same language
- **AND** the `TranslationToggle` swaps EN↔GA labels without page reload

### Requirement: 6-section per-subject shell (R2)

The system SHALL render each per-subject landing page with exactly 6 sections,
in this order: (1) Syllabus analysis, (2) Past exam question table, (3) Marking
scheme patterns, (4) Topic prioritisation (marks ÷ study-hours), (5) Exam layout
tips, (6) PDF library (original NCCA syllabus + SEC exam papers + marking
schemes, all served as signed R2 URLs).

#### Scenario: Mathematics 6-section shell renders

- **GIVEN** the user navigates to `/en/leaving-cert/mathematics`
- **WHEN** the page loads
- **THEN** the 6 sections render in order: SyllabusAnalysis / PastExamTable / MarkingSchemePatterns / TopicPrioritisation / ExamLayoutTips / PdfLibrary
- **AND** each section has the bilingual EN+GA heading
- **AND** the PDF library shows signed R2 URLs

### Requirement: Syllabus + Exam Diagram Generator (R3)

The system SHALL render 4 diagram modes for each per-subject page:

1. **Concept-map** — syllabus concept-map (uses `b.ExtractSyllabusStructure`)
2. **Topic-frequency heatmap** — question × paper × topic × year (D3 v8 + Vega-Lite)
3. **PCLM marking flow** — Partial Credit, Logical Marking flowchart (React Flow + dagre)
4. **Question-paper-topic Sankey** — question → topic → difficulty → year Sankey

#### Scenario: Concept-map diagram renders from the 5 NCCA Key Competencies

- **GIVEN** the user navigates to `/en/leaving-cert/mathematics?window=diagram-concept-map`
- **WHEN** the diagram loads
- **THEN** the diagram renders 5 root nodes (one per NCCA Key Competency) + child nodes for each Mathematics LO + bilingual EN + GA labels

### Requirement: 2D + 3D Asset Gallery — Hades dual-mode (R4)

The system SHALL render both 3D meshes and 2D sprite atlases for each subject.

#### Scenario: Mathematics asset gallery shows 3D + 2D

- **GIVEN** the user navigates to `/en/assets/mathematics`
- **WHEN** the page loads
- **THEN** the Gallery shows ≥1 GLB rendered in Babylon.js + ≥1 sprite atlas rendered as a CSS sprite

### Requirement: CopilotKit v2 Factory Mode + AG-UI (R5)

The system SHALL mount a `<CopilotSidebar defaultOpen>` from
`@copilotkit/react-core/v2` at the root layout. The 8 NCCA subject ADK
specialists SHALL be registered as CopilotKit dispatch targets.

#### Scenario: Mathematics student asks "what topics should I revise first?"

- **GIVEN** the user opens the CopilotKit sidebar on `/en/leaving-cert/mathematics`
- **WHEN** the user types "what topics should I revise first?"
- **THEN** the orchestrator dispatches to `math_agent`
- **AND** the `useRenderTool` hook renders the prioritisation as an inline component

### Requirement: BetterAuth + Pocket ID OIDC + optional SIWE (R6)

The system SHALL use BetterAuth + Pocket ID OIDC + optional SIWE on the
fresh standalone `conic-leaving-cert` Convex deployment with 5
carried-over + 3 new tables.

#### Scenario: A user signs in via Pocket ID on the 5th surface

- **GIVEN** the user navigates to `cianfhoghlaim-leaving-cert.cianfhoghlaim.ie`
- **WHEN** they click "Sign in with Pocket ID"
- **THEN** the JWT contains the `leaving_cert_portal` audience claim
- **AND** on success, the JWT is accepted by all 5 surfaces of the central portal

### Requirement: Accurate British Isles map + 6 subnations (R7)

The system SHALL render an accurate OpenStreetMap-based map of the
British Isles split into 6 subnations (Éire + Northern Ireland +
Scotland + England + Wales + Isle of Man) with 5 NCCA Key Competencies
as 5 land-marks + 8 NCCA subjects as 8 overlay buttons.

#### Scenario: A user opens the British Isles map on the central portal

- **GIVEN** the user navigates to `portal.cianfhoghlaim.ie`
- **WHEN** the map renders
- **THEN** the 6 subnations are visible with Éire active + the 5 NCCA Key Competencies appear as land-marks
- **AND** clicking a subnation shows the 8 NCCA subjects as overlay buttons

### Requirement: Celtic UI Design System (R9)

The system SHALL implement the design tokens + 12 reusable `<Ci*>` components
documented in `docs/ui-inspiration/CIANFHLOGHLAIM_DESIGN_TOKENS.css`.

#### Scenario: A designer updates the primary colour

- **GIVEN** the designer changes `--color-primary` in `tokens.css`
- **WHEN** the change is committed
- **THEN** every `<Ci*>` component re-renders with the new colour
- **AND** `bun run tokens:validate` confirms the change propagated to all source files

### Requirement: Cianfhoghlaim OS PostHog-style window manager (R10)

The system SHALL implement a `<CianfhoghlaimOS>` provider with
`{windows, activeId, dispatch}` state machine + Framer Motion physics.

#### Scenario: A user opens 3 windows and toggles between them

- **GIVEN** the user opens the central portal
- **WHEN** they click the 3 window buttons
- **THEN** `<CianfhoghlaimOS>` mounts with 3 windows in `{windows}` state
- **AND** clicking a window's title dispatches `{type: 'focus', id}` and animates it to the front via Framer Motion physics

### Requirement: Per-subject `/[lang]/leaving-cert/[subject]/lineage` route × 6 subjects (R26)

The system SHALL provide a TanStack Start route at
`/[lang]/leaving-cert/[subject]/lineage` for each of the 6 BIEP v1 LC subjects
(mathematics / chemistry / geography / gaeilge / english / computer_science) in EN,
plus the 6 GA mirror routes at `/ga/leaving-cert/[gaSlug]/lineage` (mata / ceimic /
tíreolaíocht / gaeilge / béarla / ríomheolaíocht). Each route SHALL mount the
`<LineageViewer>` component from `web/apps/cianfhoghlaim-leaving-cert/apps/web/packages/lineage/`.

The route SHALL resolve the subject via a `getSubjectFromSlug(slug)` helper that
returns a `BIEPSubjectDef` from `apps/web/src/lib/bi-ep.ts` (extended as needed for
GA slug ↔ EN slug resolution via the existing `getGASlug` / `getEnglishSlugFromGA`
helpers).

#### Scenario: A teacher opens Mathematics lineage

- **GIVEN** the teacher navigates to `/en/leaving-cert/mathematics/lineage`
- **WHEN** the page loads
- **THEN** the route resolves `getSubjectFromSlug("mathematics")` from
  `apps/web/src/lib/bi-ep.gen.ts`
- **AND** the route fetches the lineage rows from the Hono endpoint
  `/api/lineage/mathematics` via the TanStack Start `loader`
- **AND** the `<LineageViewer>` mounts with the 2-pane layout (left: step-by-step
  preview; right: D3 lineage DAG; bottom: PDF.js viewer)
- **AND** the page responds with HTTP 200 within 2 seconds

#### Scenario: Gaeilge mirror route resolves

- **GIVEN** the user opens `/ga/leaving-cert/mata/lineage`
- **WHEN** the route resolves
- **THEN** `getGASlug("mathematics")` returns `"mata"` (per the existing
  `lib/bi-ep.ts::getGASlug` function)
- **AND** the bilingual labels render in Irish
- **AND** all PDF page citations resolve to GA PDFs when present (else fallback to EN)

#### Scenario: A non-existent subject slug returns 404

- **GIVEN** the user navigates to `/en/leaving-cert/physics/lineage`
- **WHEN** the route resolves
- **THEN** `getSubjectFromSlug("physics")` returns `undefined`
- **AND** the TanStack Start `notFoundComponent` renders with the canonical 404 UI

### Requirement: PDF source registry + filesystem walk + CI drift gate (R27)

The system SHALL provide a TypeScript registry at
`apps/web/src/lib/lineage-registry.ts` that maps each
`(subject, lang, document_type)` tuple to a `LineagePDFEntry` carrying:
`pdf_path`, `filename`, `sha256`, `page_count`, `byte_size`, `ingested_at`. The
registry SHALL be auto-derived by `scripts/schema-generate.ts` from the canonical
`leaving_certificate/<subject>/{en,ga}/*.pdf` filesystem walk plus the 4 NCCA
root-level PDFs (Key Competencies / SC Advisory Report / Online Learning / Online
Certification) at `leaving_certificate/*.pdf`.

The registry output SHALL be checked into git. A CI task `bun run lineage:validate`
SHALL re-walk the filesystem, diff against the committed registry, and fail the
build if any file is added, removed, or its SHA-256 / page_count has changed.

#### Scenario: schema-generate walks the PDF filesystem

- **GIVEN** `leaving_certificate/mathematics/en/SCSEC25_Maths_syllabus_examination-2015_English.pdf`
  exists
- **WHEN** the developer runs `bun run schema:generate`
- **THEN** the script enumerates the 13 subject directories × {en, ga} × PDF
- **AND** computes SHA-256 + page_count (via the existing
  `dlt/british_isles/ireland/ncca_root_pdfs.py::_estimate_page_count` heuristic)
  + byte_size + ingested_at
- **AND** emits `apps/web/src/lib/lineage-registry.ts` with one entry per PDF
- **AND** the emitted file passes `bun run typecheck`

#### Scenario: Registry drift detected

- **GIVEN** a new PDF is added to `leaving_certificate/biology/en/`
- **WHEN** CI runs `bun run lineage:validate`
- **THEN** the script walks the filesystem, diffs against `lineage-registry.ts`,
  detects the missing entry, and fails the build with a diff message
- **AND** the developer runs `bun run schema:generate` to regenerate

#### Scenario: PDF checksum change detected

- **GIVEN** an existing PDF is re-saved (e.g. NCCA re-publishes a syllabus)
- **WHEN** CI runs `bun run lineage:validate`
- **THEN** the script detects the SHA-256 change
- **AND** fails the build with a `sha256_mismatch` diff entry
- **AND** the developer re-runs `bun run schema:generate` to update the registry

#### Scenario: 4 NCCA root-level PDFs are in the registry

- **GIVEN** the 4 NCCA root-level PDFs exist at `leaving_certificate/*.pdf`
- **WHEN** the developer runs `bun run schema:generate`
- **THEN** the registry includes the 4 root PDFs (Key Competencies / SC Advisory
  Report / Online Learning / Online Certification)
- **AND** each carries `subject: null` (they are not subject-scoped)

### Requirement: BAML `LineageTrace` extension on the 5 canonical LC extraction functions (R28)

The system SHALL extend the existing per-subject BAML extraction functions
(`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`,
`ExtractMarkingSchemeGuideline`, `ExtractCrossLinguisticConcept`,
`ExtractSyllabusDiagram`) to emit a `LineageTrace` payload as part of their BAML
output. The `LineageTrace` class SHALL be defined in
`baml_src/british_isles/ireland/education/lc_extraction/_shared/lineage_trace.baml`
and composed into each extraction function's return type.

The `LineageTrace` class SHALL carry:
- `source_pdf: string` — absolute path or R2 key to the source PDF
- `source_page: int` — 1-indexed PDF page number
- `extraction_function: string` — the BAML function name
- `extraction_client: string` — the BAML client used (ExtractEn / ExtractGa /
  ExtractEnStrong / LocalVision)
- `extracted_at: string` — ISO 8601 timestamp
- `confidence: float?` — optional confidence score (0.0–1.0)
- `chunk_id: string?` — the CocoIndex chunk ID when this row was embedded
  (nullable in v1)

The BAML `LineageTrace` extension SHALL be additive (no breaking change to existing
extraction output consumers). The new field SHALL be optional in the BAML output so
existing callers can ignore it.

#### Scenario: ExtractCurriculumSyllabus returns LineageTrace

- **GIVEN** the BAML function runs against
  `leaving_certificate/mathematics/en/SCSEC25_Maths_syllabus_examination-2015_English.pdf`
  page 14 (Algebra module)
- **WHEN** the call returns
- **THEN** the `SyllabusDocument` payload carries `lineage.source_pdf` =
  the absolute PDF path, `lineage.source_page` = 14,
  `lineage.extraction_function` = `"ExtractCurriculumSyllabus"`,
  `lineage.extraction_client` = `"ExtractEn"`, `lineage.extracted_at` =
  current UTC ISO 8601
- **AND** the parent `module_topics[i].learning_outcomes[j]` row inherits the same
  lineage metadata

#### Scenario: The lineage UI reads LineageTrace

- **GIVEN** the lineage viewer fetches `/api/lineage/mathematics`
- **WHEN** the Hono endpoint returns rows
- **THEN** each row carries a `lineage` field that the lineage UI renders
- **AND** clicking a row's lineage badge opens the PDF.js viewer to
  `?page=<source_page>`

#### Scenario: BAML backward compatibility

- **GIVEN** an existing consumer reads `SyllabusDocument` without reading `lineage`
- **WHEN** the BAML function returns the extended output
- **THEN** the existing consumer sees the same fields it always did
- **AND** the new `lineage` field is ignored
- **AND** `mise run baml:cli:test` still passes

### Requirement: Marimo + MotherDuck Dive + Flight cell mapping on `BIEPVisualizations` (R29)

The system SHALL extend `apps/web/src/lib/bi-ep.ts::BIEPVisualizations` with a new
`marimo_cell_id: string` field and a `motherduck_ref: { dive_name: string;
flight_name: string; dive_url: string }` field on each `BIEPVisualization`,
mapping each visualization to:

- The marimo notebook cell that renders it (e.g. `mathematics_topic_frequency_cell`)
- The MotherDuck Dive (e.g. `lc_syllabus_topics`) + the MotherDuck Flight (e.g.
  `lc_pdf_sync_flight`) that own the underlying data

The lineage viewer SHALL render the marimo cell + MotherDuck reference as a
clickable pill; clicking the marimo pill opens the marimo embed iframe; clicking
the MotherDuck pill opens the Dive URL in a new tab.

#### Scenario: Mathematics topic-frequency visualization links to marimo + MotherDuck

- **GIVEN** the user is on `/en/leaving-cert/mathematics/lineage`
- **WHEN** the lineage viewer renders the topic_frequency step
- **THEN** a pill `"marimo: 03_leaving_cert/23_mathematics_biep_v1.py :: topic_frequency_cell"`
  renders below the step
- **AND** a pill `"MotherDuck Dive: lc_syllabus_topics · Flight: lc_pdf_sync_flight"`
  renders alongside
- **AND** clicking the marimo pill expands the marimo iframe inline
- **AND** clicking the MotherDuck pill opens
  `https://app.motherduck.com/dive/lc_syllabus_topics` in a new tab

#### Scenario: Junior Cycle visualizations show "out of scope" badge

- **GIVEN** a BIEP v1 LC subject has only BIEP v1 marimo notebooks
- **WHEN** the lineage viewer renders any step
- **THEN** the marimo + MotherDuck pills reference BIEP v1 resources (no JC badge)
- **AND** no "out of scope" badge is shown (BIEP v1 is fully active)

### Requirement: `bun run schema:generate` CLI — DuckLake → Zod + TanStack DB collections (R30)

The system SHALL provide a `scripts/schema-generate.ts` CLI that connects to the
canonical DuckLake database `md:oideachais` (or the local
`ducklake:postgres:lakehouse-postgres:5432/lakehouse` fallback when running offline),
introspects the schema of every BIEP v1 table:

- `oideachais.leaving_cert.mathematics_{syllabus,papers,marking_schemes,topics}`
- `oideachais.leaving_cert.chemistry_{...}`
- `oideachais.leaving_cert.geography_{...}`
- `oideachais.leaving_cert.english_{...}`
- `oideachais.leaving_cert.gaeilge_{...}`
- `oideachais.leaving_cert.cs_{...}`

and emits `apps/web/src/lib/bi-ep.gen.ts` containing, per table:

- A Zod schema derived from the DuckLake column types (via the column-type mapper
  at `scripts/zod-from-duckdb.ts`)
- A TanStack DB collection config (the canonical `@tanstack/db` `createCollection`
  wiring + the per-subject query helpers)

The CLI SHALL be idempotent (running it twice produces the same output) and SHALL
emit a `apps/web/src/lib/bi-ep.gen.lock.json` file that records the DuckLake schema
version + the generated-file hash. A CI task `bun run schema:validate` SHALL fail
the build if the committed `bi-ep.gen.ts` is out of sync with the live DuckLake
schema.

#### Scenario: schema-generate emits a Zod schema for mathematics_topics

- **GIVEN** `md:oideachais.leaving_cert.mathematics_topics` exists with columns
  `(topic_id VARCHAR, name_en VARCHAR, name_ga VARCHAR, blooms_level VARCHAR, weight DOUBLE, lineage JSON)`
- **WHEN** the developer runs `bun run schema:generate`
- **THEN** the script connects via the canonical
  `ibis.duckdb.connect("md:oideachais")` entrypoint
- **AND** runs `DESCRIBE leaving_cert.mathematics_topics`
- **AND** emits a `mathematicsTopicsSchema = z.object({ topic_id: z.string(), ... })`
- **AND** emits a `createMathematicsTopicsCollection()` TanStack DB helper
- **AND** the emitted file passes `bun run typecheck`

#### Scenario: CI fails on schema drift

- **GIVEN** a Dagster asset adds a new column `extraction_confidence DOUBLE` to
  `md:oideachais.leaving_cert.mathematics_topics`
- **WHEN** CI runs `bun run schema:validate`
- **THEN** the script regenerates `bi-ep.gen.ts` in-memory, diffs against the
  committed file, and fails with a list of drifted types
- **AND** the PR is blocked until the developer commits the regenerated file

#### Scenario: Idempotent regeneration

- **GIVEN** the developer runs `bun run schema:generate` twice in a row
- **WHEN** the second run completes
- **THEN** the second `bi-ep.gen.ts` is byte-identical to the first
- **AND** the `bi-ep.gen.lock.json` hash matches

### Requirement: PDF.js in-browser viewer with citation deep-links (R31)

The system SHALL mount a `<PdfViewer>` component inside the lineage viewer, powered
by `pdfjs-dist`'s WASM build (`pdf.mjs` + `pdf.worker.mjs`). The viewer SHALL
fetch signed R2 URLs from the Hono endpoint `GET /api/pdf/:r2Key` (which extends
the existing R14 endpoint by adding the BIEP lineage subject-prefix routing),
open the PDF in the browser, and expose deep-link navigation via URL params
(`?page=<n>&rect=<x,y,w,h>`).

Each lineage row's `lineage.source_pdf` field SHALL resolve to an `r2_key` (the
registry row in R27 carries it), and the citation link SHALL render as
`/en/leaving-cert/mathematics/lineage?page=14&r2_key=leaving_cert/mathematics/en/SCSEC25_Maths_syllabus_examination-2015_English.pdf`.

The `pdf.worker.mjs` bundle SHALL be self-hosted at `/assets/pdf.worker.mjs`
(bundled at build time via `vite.config.ts`), not loaded from a CDN. This is
CSP-friendly, offline-capable, and avoids the third-party dependency.

#### Scenario: A student clicks a citation link

- **GIVEN** the user is on `/en/leaving-cert/mathematics/lineage` and sees a row
  with `lineage.source_pdf = "leaving_cert/mathematics/en/SCSEC25_Maths_syllabus_examination-2015_English.pdf"`,
  `lineage.source_page = 14`
- **WHEN** they click "View source page"
- **THEN** the lineage viewer calls
  `GET /api/pdf/leaving_cert/mathematics/en/SCSEC25_Maths_syllabus_examination-2015_English.pdf?page=14`
- **AND** the Hono endpoint returns a 15-min signed R2 URL within 500ms
- **AND** the `<PdfViewer>` loads the PDF + scrolls to page 14
- **AND** the page is highlighted with a yellow overlay (the "citation" rect)

#### Scenario: PDF.js WASM bundle serves from self-host

- **GIVEN** the app is deployed to Cloudflare Pages
- **WHEN** the `<PdfViewer>` mounts
- **THEN** the WASM build (`pdf.worker.mjs`) is loaded from
  `/assets/pdf.worker.mjs` (bundled at build time, not from a CDN)
- **AND** the WASM initialisation completes within 2 seconds on a typical
  connection
- **AND** no `eval()` calls are made (CSP-compliant)

#### Scenario: PDF.js handles bilingual content

- **GIVEN** a user opens `/ga/leaving-cert/mata/lineage` and clicks a citation
  pointing to a GA PDF
- **WHEN** the PDF.js viewer loads
- **THEN** the PDF renders the Irish-language content
- **AND** the marimo + MotherDuck pills render in Irish

### Requirement: CocoInsight-style click-to-highlight (R32)

The system SHALL implement the CocoInsight interaction pattern in the lineage
viewer: clicking any field in the left "step-by-step preview" pane OR any node
in the right "lineage DAG" pane SHALL:

1. Set the clicked element to **purple** (`var(--ci-lineage-selected)`)
2. Highlight direct upstream dependencies in **blue** (`var(--ci-lineage-upstream)`)
3. Highlight direct downstream consumers in **green**
   (`var(--ci-lineage-downstream)`)
4. Dim unrelated fields/nodes to **40% opacity** (`var(--ci-lineage-dim)`)

The lineage DAG SHALL be a directed acyclic graph rendered with D3 v8 force layout,
showing nodes for: `pdf_page → ocr_chunk → baml_extraction → marimo_cell →
web_component`. Edges SHALL carry labels indicating the field-mapped relationship
(e.g. `module_topics[0].name_en`).

The click-to-highlight state SHALL live in a Zustand store at
`apps/web/packages/lineage/lineage-store.ts` with three pieces of state:
`selectedId: string | null`, `upstreamIds: Set<string>`,
`downstreamIds: Set<string>`.

#### Scenario: User clicks a BAML extracted field

- **GIVEN** the user is on `/en/leaving-cert/mathematics/lineage` and sees
  `module_topics[0].learning_outcomes[2]` in the left pane
- **WHEN** they click it
- **THEN** the field turns purple
- **AND** the upstream `pdf_page` node turns blue
- **AND** the downstream `marimo_cell` node turns green
- **AND** the 5 unrelated modules + 18 unrelated marimo cells dim to 40% opacity

#### Scenario: User clicks a DAG node

- **GIVEN** the lineage DAG is rendered
- **WHEN** the user clicks the `baml_extraction` node for
  `ExtractCurriculumSyllabus`
- **THEN** all 5 fields it produced highlight in purple in the left pane
- **AND** the 1 PDF page node + the 3 marimo cell nodes it feeds highlight
  appropriately (upstream blue + downstream green)

#### Scenario: User clears the selection

- **GIVEN** the user has clicked a field and the lineage is highlighted
- **WHEN** they click the same field again (or press `Escape`)
- **THEN** the lineage store clears the selection
- **AND** all fields/nodes return to their default colour (no dimming)

### Requirement: WASM-compatible deployment + CI gate (R33)

The system SHALL deploy the 5th surface
(`web/apps/cianfhoghlaim-leaving-cert/`) to Cloudflare Pages (V8 runtime, free
tier) with the lineage viewer functioning without any native FS access.
Specifically:

1. All PDFs are fetched via `fetch(signedR2Url)` — never `fs.readFileSync`
2. The `pdfjs-dist` WASM build is bundled at build time (output to
   `apps/web/dist/assets/pdf.worker.mjs`)
3. The DuckLake connection goes through the Hono endpoint
   `/api/lineage/:subject` — no browser-side DuckDB connection
4. The `bun run schema:generate` CLI runs in CI (not in the browser)
5. A `bun run lineage:smoke` Playwright test verifies the viewer mounts + renders
   the 2-pane layout + a PDF page in under 3 seconds

The CI gate SHALL include `bun run lineage:validate` (R27) +
`bun run schema:validate` (R30) + `bun run storybook:build` (R16) +
`bun run lineage:smoke` (R33) +
`openspec validate 2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1 --strict`.

#### Scenario: WASM deployment smoke test

- **GIVEN** the app is built with `bun run build:web` + the WASM PDF.js bundle
  is emitted to `dist/assets/pdf.worker.mjs`
- **WHEN** the CI runs `bun run lineage:smoke`
- **THEN** Playwright launches a headless Chromium
- **AND** navigates to `/en/leaving-cert/mathematics/lineage`
- **AND** asserts the lineage viewer mounts + the 2-pane layout is visible
- **AND** asserts the PDF.js viewer loads `pdf.worker.mjs` (no 404)
- **AND** asserts the page-14 citation link returns a signed R2 URL within
  500ms
- **AND** the total smoke test runtime is under 3 seconds

#### Scenario: Cloudflare Pages deployment

- **GIVEN** `apps/web/dist/` is built
- **WHEN** the developer runs
  `wrangler pages deploy apps/web/dist --project-name cianfhoghlaim-leaving-cert`
- **THEN** the deployment succeeds within 60 seconds
- **AND** the free-tier limits are respected (10 GB R2 storage + 1M Class A
  ops/mo + 25 MB max per file)
- **AND** no Workers Paid subscription is required

#### Scenario: CI gate enforces all checks

- **GIVEN** a PR adds a new PDF to `leaving_certificate/biology/en/`
- **WHEN** the CI runs the lineage workflow
- **THEN** `bun run lineage:validate` fails (registry drift)
- **AND** the PR is blocked
- **AND** the developer runs `bun run schema:generate` + commits the updated
  registry
- **AND** the next CI run passes all gates

## See also

- [cianfhoghlaim-educational-mmo](../cianfhoghlaim-educational-mmo/spec.md) — the 8 NCCA ADK specialists
- [retro-game-asset-pipeline](../retro-game-asset-pipeline/spec.md) — the 2D + 3D asset generator
- [ncca-leaving-cert-root-pdfs](../ncca-leaving-cert-root-pdfs/spec.md) — the 5 NCCA root-level PDFs
- [agentic-frontend-frameworks](../agentic-frontend-frameworks/spec.md) — the 5th canonical surface (R5 + R6 + R7)