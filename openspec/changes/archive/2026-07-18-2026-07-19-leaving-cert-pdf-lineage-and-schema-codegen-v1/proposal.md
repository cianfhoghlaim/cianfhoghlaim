# 2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1

## Why

The existing 6-subject BIEP web surface at
`web/apps/cianfhoghlaim-leaving-cert/` renders 5 visualization cards per subject, but
those cards currently display **descriptions of marimo cells**, not real data — and
nothing in the UI tells the user that what they are looking at came from a specific
NCCA PDF page + BAML extraction + marimo notebook. This change adds a
**CocoInsight-style 2-pane document-lineage viewer** (per subject at
`/[lang]/leaving-cert/[subject]/lineage`) plus a `bun run schema:generate` CLI that
emits Zod + TanStack DB collections from the canonical
`md:oideachais.leaving_cert.<subject>.*` DuckLake tables.

The viewer shows the PDF → OCR → BAML → marimo → web-component lineage with
click-to-highlight (blue upstream / green downstream / purple selected), per-page
PDF.js in-browser source view, and a marimo + MotherDuck cell mapping that ties the
lineage to the existing analytics surface. Junior Cycle is explicitly out of scope
(BIEP v2) but the architecture is designed to extend to it. WASM compatibility is
preserved by using `pdfjs-dist`'s WASM build + Hono oRPC endpoints + no native FS
access; the deployment target remains Cloudflare Pages (V8 runtime, free tier).

This change continues the openspec numbering on the existing
`cianfhoghlaim-leaving-cert-portal` spec (R1–R10 are live, R11–R25 are in flight
under `2026-07-18-british-isles-portal-activation-v3`). R26–R33 are 8 ADDED
Requirements that complement the v3 portal activation work without depending on it.

## What changes

### 1. New spec delta: R26–R33 ADDED Requirements to `cianfhoghlaim-leaving-cert-portal`

The 8 new requirements cover:

| ID | Title | Origin |
|:--|:--|:--|
| **R26** | Per-subject `/[lang]/leaving-cert/[subject]/lineage` route × 6 subjects | New |
| **R27** | PDF source registry + filesystem walk + CI drift gate | New |
| **R28** | BAML `LineageTrace` extension on the 5 canonical LC extraction functions | New |
| **R29** | Marimo + MotherDuck Dive + Flight cell mapping on `BIEPVisualizations` | New |
| **R30** | `bun run schema:generate` CLI — DuckLake → Zod + TanStack DB collections | New |
| **R31** | PDF.js in-browser viewer with citation deep-links (`?page=&rect=`) | New |
| **R32** | CocoInsight-style click-to-highlight (purple/blue/green/dim) | New |
| **R33** | WASM-compatible deployment + CI gate (`bun run lineage:smoke`) | New |

### 2. New code artifacts (in `web/apps/cianfhoghlaim-leaving-cert/`)

| File | Purpose |
|:--|:--|
| `apps/web/src/routes/en/leaving-cert/<subject>/lineage.tsx` × 6 | Per-subject lineage viewer route (mathematics / chemistry / geography / gaeilge / english / computer_science) |
| `apps/web/src/routes/ga/leaving-cert/<gaSlug>/lineage.tsx` × 6 | GA mirror (mata / ceimic / tíreolaíocht / gaeilge / béarla / ríomheolaíocht) |
| `apps/web/packages/lineage/LineageViewer.tsx` | The 2-pane viewer shell |
| `apps/web/packages/lineage/LineageDag.tsx` | D3 v8 force-directed DAG (PDF → OCR → BAML → marimo → web) |
| `apps/web/packages/lineage/StepPreview.tsx` | Left-pane step-by-step preview (CocoInsight-style cell preview) |
| `apps/web/packages/lineage/PdfViewer.tsx` | PDF.js WASM viewer with citation deep-links |
| `apps/web/packages/lineage/lineage-store.ts` | Zustand store for the click-to-highlight state machine |
| `apps/web/packages/lineage/tokens.ts` | The 4 lineage design tokens (`--ci-lineage-{selected,upstream,downstream,dim}`) |

### 3. Generated files (committed + CI-validated)

| File | Purpose |
|:--|:--|
| `apps/web/src/lib/bi-ep.gen.ts` | The auto-generated Zod schemas + TanStack DB collections per BIEP v1 table |
| `apps/web/src/lib/bi-ep.gen.lock.json` | Schema-version + file-hash lock for drift detection |
| `apps/web/src/lib/lineage-registry.ts` | Auto-derived PDF registry (paths + SHA-256 + page counts) |

### 4. CLI scripts (in repo root)

| File | Purpose |
|:--|:--|
| `scripts/schema-generate.ts` | `bun run schema:generate` — DuckLake → Zod + TanStack DB + lineage registry |
| `scripts/zod-from-duckdb.ts` | DuckDB column-type → Zod schema mapper (one function per SQL type) |
| `scripts/lineage-validate.ts` | `bun run lineage:validate` — filesystem vs registry diff |
| `scripts/schema-validate.ts` | `bun run schema:validate` — committed vs regenerated `bi-ep.gen.ts` diff |
| `scripts/lineage-smoke.ts` | `bun run lineage:smoke` — Playwright WASM smoke test |

### 5. Hono endpoints (in `web/hono-api/`)

| File | Purpose |
|:--|:--|
| `src/routes/lineage/[subject].ts` | `GET /api/lineage/:subject` — returns lineage rows from DuckLake |
| `src/routes/pdf/[...r2-key].ts` | `GET /api/pdf/*` — issues 15-min signed R2 URLs (extends R14) |

### 6. BAML extensions (additive — no breaking changes)

| File | Change |
|:--|:--|
| `baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml` | Add `LineageTrace` class + populate from `ExtractCurriculumSyllabus` |
| `baml_src/british_isles/ireland/education/lc_extraction/exam_paper_layout.baml` | Add `LineageTrace` class + populate from `ExtractExamPaperLayout` |
| `baml_src/british_isles/ireland/education/lc_extraction/marking_scheme.baml` | Add `LineageTrace` class + populate from `ExtractMarkingSchemeGuideline` |
| `baml_src/british_isles/ireland/education/lc_extraction/cross_linguistic.baml` | Add `LineageTrace` class + populate from `ExtractCrossLinguisticConcept` |
| `baml_src/british_isles/ireland/education/lc_extraction/syllabus_diagram.baml` | Add `LineageTrace` class + populate from `ExtractSyllabusDiagram` |

## Existing scaffolding reused (no duplication)

| What | Where | Status |
|:--|:--|:--|
| 6 LC subject routes + 5 sub-routes each | `apps/web/src/routes/en/subjects/<subject>/{index,syllabus,exam-papers,marking-schemes,study-plan}.tsx` | Live (from `2026-07-16-biiep-v1-lc-per-subject-web-surface-v1`) |
| 6 GA mirror routes | `apps/web/src/routes/ga/subjects/<gaSlug>/{index,syllabus,exam-papers,marking-schemes,study-plan}.tsx` | Live |
| BAML `ExtractCurriculumSyllabus` + 4 sibling extractors | `baml_src/british_isles/ireland/education/lc_extraction/*.baml` | Live — `LineageTrace` is additive |
| 7 per-subject `qpack_<subject>.baml` schemas | `baml_src/british_isles/ireland/education/subjects/` | Live |
| 6 per-subject marimo notebooks | `notebooks/03_leaving_cert/<subject>_biep_v1.py` | Live |
| CocoIndex parameterised App | `cocoindex_flows/subjects/lc_subject_embedding.py` | Live (BIEP v1 canonical) |
| BIEPSubjectPage + BIEPVisualizations metadata | `apps/web/src/{components/BIEPSubjectPage.tsx, lib/bi-ep.ts}` | Live — R29 extends `BIEPVisualizations` |
| Hono + Convex + BetterAuth + Storybook + 12 `<Ci*>` components | `apps/web/` | Live |
| The 13 PDF directories + 4 root PDFs | `leaving_certificate/<subject>/{en,ga}/*.pdf` + `leaving_certificate/*.pdf` | The source of truth |
| `ncca_root_pdfs` DLT resource (already emits SHA-256 + page count) | `dlt/british_isles/ireland/ncca_root_pdfs.py` | Live |
| 4 MotherDuck Dives + daily `lc_pdf_sync_flight` | `motherduck/` + `orchestration/` | Live — R29 references them |
| `getGASlug` / `getEnglishSlugFromGA` helpers | `apps/web/src/lib/bi-ep.ts` | Live — R26 reuses |

## Open questions — RESOLVED 2026-07-19

1. **Junior Cycle in v1 or v2?** — **DEFERRED to v2**. The 6 LC subjects are
   in-scope; JC adds the same lineage viewer pattern over JC subjects. The
   BIEP v2 spec already covers JC; this change extends to it in a follow-up.
2. **5 NCCA root-level PDFs in v1 or v2?** — **INCLUDED in the registry
   (R27) but no dedicated route**. The 4 root PDFs (Key Competencies / SC
   Advisory Report / Online Learning / Online Certification) appear in the
   `lineage-registry.ts` so the lineage viewer can cite them when a BAML
   extraction references one. Dedicated `/foundations/<slug>/lineage` routes
   are deferred.
3. **Aistear + Primary stages in v1?** — **DEFERRED** (consistent with the
   v3 portal change R17).
4. **BAML `LineageTrace` extension strategy** — **EXTEND the existing
   BAML files** (additive field, no breaking change). The new class lives
   in `lc_extraction/_shared/lineage_trace.baml` and is composed into the 5
   canonical extraction functions.
5. **PDF.js WASM bundle CDN** — **SELF-HOST** at `/assets/pdf.worker.mjs`
   (CSP-friendly + no third-party dependency + works offline).

## Cross-references

- [`openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md`](../../specs/cianfhoghlaim-leaving-cert-portal/spec.md) — extends R1–R10 + (in-flight) R11–R25 with R26–R33
- [`openspec/specs/british-isles-education-pipeline/spec.md`](../../specs/british-isles-education-pipeline/spec.md) — the 6 LC priority subjects + the canonical DuckLake tables
- [`openspec/specs/cianfhoghlaim-baml-schemas/spec.md`](../../specs/cianfhoghlaim-baml-schemas/spec.md) — the 9 BAML files that the `LineageTrace` extends
- [`openspec/specs/agentic-frontend-frameworks/spec.md`](../../specs/agentic-frontend-frameworks/spec.md) — the 5th canonical surface (TanStack Start + Convex + Hono + Cloudflare R2 + CopilotKit v2)
- [`openspec/specs/cianfhoghlaim-cocoindex-v1-migration/spec.md`](../../specs/cianfhoghlaim-cocoindex-v1-migration/spec.md) — the R1–R4 CocoIndex v1 conformance contract
- [`openspec/specs/dagster-5-layer-component-architecture/spec.md`](../../specs/dagster-5-layer-component-architecture/spec.md) — the 5-layer pipeline that emits the BIEP v1 assets
- [`.agents/skills/cocoindex/SKILL.md`](../../../.agents/skills/cocoindex/SKILL.md) — the CocoIndex v1 App canonical pattern
- [`.agents/skills/lancedb/SKILL.md`](../../../.agents/skills/lancedb/SKILL.md) — the LanceDB companion tables
- [`.agents/skills/motherduck/SKILL.md`](../../../.agents/skills/motherduck/SKILL.md) — the 4 MotherDuck Dives + daily Flight (referenced by R29)
- [`.agents/skills/marimo/SKILL.md`](../../../.agents/skills/marimo/SKILL.md) — the marimo embed pattern + WASM compatibility
- [`.agents/skills/agentic-frontend-frameworks/SKILL.md`](../../../.agents/skills/agentic-frontend-frameworks/SKILL.md) — the 5th surface stack conventions
- [`.agents/skills/tanstack-start/SKILL.md`](../../../.agents/skills/tanstack-start/SKILL.md) — TanStack Start file-based routing + server functions

## Dependencies

```yaml
Blocked by: none  # R26-R33 are independent of the v3 portal change.
Blocked by (soft):
  - 2026-07-18-british-isles-portal-activation-v3  # R26-R33 extend the same spec; soft ordering so the v3 archives first.
  - 2026-07-16-biiep-v1-lc-per-subject-web-surface-v1  # The 30 + 36 + 6 per-subject route/Convex/BAML files (already archived).
  - 2026-07-13-biep-v1-lc-per-subject-agent-workflows-v1  # The 18 BAML workflow handlers that surface lineage metadata.
Affected repos: cianfhoghlaim (single-repo change — no cross-repo-sync.md required).
```

## Risks

1. **DuckLake schema drift** — the `bi-ep.gen.ts` file will go stale if the
   upstream Dagster assets add columns. Mitigation: R30's CI gate (`bun run
   schema:validate`) catches drift on every PR; `bi-ep.gen.lock.json` records
   the schema-version + generated-file hash.
2. **PDF.js bundle size** — `pdf.worker.mjs` is ~1 MB. Mitigation: load via
   dynamic `import()` only when the viewer mounts (lazy), and use Cloudflare
   Pages (no Workers size limit, 25 MB max per file).
3. **Cloudflare Pages free-tier** — 100k requests/day, 25 MB max per file. The
   `pdf.worker.mjs` is 1 MB so well within budget. R2 free tier (10 GB) is the
   binding constraint — the 4 root PDFs + 13 subject directories × en/ga ≈ 2 GB,
   so we have headroom for ~5× growth before hitting the cap.
4. **BAML `LineageTrace` backward compat** — adding a field to the existing BAML
   `SyllabusDocument` class is additive (no breaking change). The new field is
   optional in the BAML output (clients can ignore it).
5. **Junior Cycle deferred** — the user explicitly said JC is "planned but the
   pipeline isn't fully up". Mitigation: the architecture (per-subject routes +
   per-subject BAML + per-subject DuckLake tables) extends to JC; the JC paths
   will land in a follow-up openspec change.

## Out of scope (deferred to follow-up changes)

- **Junior Cycle lineage viewer** — BIEP v2 (per `british-isles-education-pipeline`
  spec; the existing `junior_cycle_embedding.py` CocoIndex App exists but the
  BAML extraction files are not yet per-subject).
- **5 NCCA root-level PDFs lineage routes** — the 4 root PDFs (Key Competencies /
  SC Advisory Report / Online Learning / Online Certification) are in the lineage
  registry (R27) but their dedicated `/foundations/<slug>/lineage` routes are
  deferred.
- **CocoIndex embedding lineage** — the parameterised `lc_subject_embedding.py`
  App produces LanceDB chunks that are 1 level downstream of BAML. Showing the
  embedding lineage would require a `cocoindex server -ci` integration; deferred.
- **MotherDuck Dive + Flight live data** — the lineage viewer references the
  MotherDuck Dive/Flights as pills (R29) but doesn't embed the live Dive UI.
- **A2UI surfaces for lineage** — the lineage UI uses React + D3 directly, not
  A2UI. A future change could expose the lineage via A2UI surfaces.

## Archive plan

- Archive after R26–R33 land and `/en/leaving-cert/mathematics/lineage` resolves
  to a working 2-pane viewer with at least the Mathematics subject showing a
  PDF.js source view + D3 lineage DAG + marimo + MotherDuck pills.
- Follow-up change adds the Junior Cycle lineage viewer (BIEP v2).
- Follow-up change adds the 5 NCCA root-level PDFs lineage routes
  (`/foundations/<slug>/lineage`).
- Follow-up change wires the CocoIndex embedding lineage
  (BAML → CocoIndex → LanceDB → marimo).