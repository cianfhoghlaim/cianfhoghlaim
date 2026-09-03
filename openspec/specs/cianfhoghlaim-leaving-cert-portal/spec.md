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
contract documented in `openspec/specs/cianfhoghlaim-cocoindex-v1-migration/spec.md`.

The App SHALL mount its target on the canonical LanceDB table
`cianfhoghlaim.portal.study_plan_chunks` using `BAAI/bge-m3` (1024-d)
as the shared embedder via the canonical `_lifespan.py` shared home.

#### Scenario: A developer reads the App skeleton

- **WHEN** the developer opens `cocoindex/portal_study_plan_embedding.py`
- **THEN** they see the 4 wrapper files (`_lifespan.py`, `_assets.py`, `__init__.py`, `test_smoke.py`)
- **AND** the R1-R4 conformance contract check passes

### Requirement: MotherDuck Dive + daily Flight (R13)

The system SHALL provide a MotherDuck Dive named `lc_study_plan_dive`
that renders a KPI strip + a filterable table + a trend chart over the
`cianfhoghlaim.portal.study_plan_chunks` LanceDB companion.

The system SHALL also provide a daily MotherDuck Flight named
`lc_study_plan_flight` that runs `dagster materialise -a study_plan_extract`
once per day.

#### Scenario: A user opens the Dive

- **GIVEN** `cianfhoghlaim.portal.study_plan_chunks` has at least 1 row
- **WHEN** the user opens the Dive URL
- **THEN** the KPI strip renders with ≥ 3 metrics (study plans / week, subnation coverage %, asset fan-out histogram)
- **AND** the filterable table renders all rows

#### Scenario: The daily Flight runs

- **WHEN** the cron fires
- **THEN** `lc_study_plan_flight` materialises the `study_plan_extract` Dagster asset
- **AND** the BAML row backfill runs against the freshest MotherDuck rows
- **AND** the marimo notebook is regenerated

### Requirement: Cloudflare R2 + Hono-issued signed URLs (R14)

The system SHALL provide a Cloudflare R2 bucket named `cianfhoghlaim-pdfs`
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
`web/apps/cianfhoghlaim-leaving-cert/apps/web/.storybook/`
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
`cocoindex/` as CocoIndex v1 Apps (R1–R4 conformant)
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
`web/apps/cianfhoghlaim-leaving-cert/apps/web/packages/ui/a2ui-catalog.tsx`
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
(`agents/tuatha/{math,chem,geog,gael,engl,comp,appm,hist}_agent.py`)
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
`web/apps/cianfhoghlaim-leaving-cert/apps/web/packages/mcp/design-system-server.py`
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

## See also

- [cianfhoghlaim-educational-mmo](../cianfhoghlaim-educational-mmo/spec.md) — the 8 NCCA ADK specialists
- [retro-game-asset-pipeline](../retro-game-asset-pipeline/spec.md) — the 2D + 3D asset generator
- [ncca-leaving-cert-root-pdfs](../ncca-leaving-cert-root-pdfs/spec.md) — the 5 NCCA root-level PDFs
- [agentic-frontend-frameworks](../agentic-frontend-frameworks/spec.md) — the 5th canonical surface (R5 + R6 + R7)