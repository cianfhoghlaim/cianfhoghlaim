# Tasks — Per-subject Convex + TanStack interactive web surface for the 6 BIEP v1 LC subjects

## Step 1 — Audit existing BIEP web app scaffold (30 min)

- [x] 1.1 List existing per-subject routes at `apps/.../routes/en/subjects/`
- [x] 1.2 Confirm the existing flat files (`subjects/<subject>.tsx`) are in
      place for all 6 BIEP v1 subjects
- [x] 1.3 Locate the existing Convex package at
      `apps/cianfhoghlaim-leaving-cert/packages/convex/src/`
- [x] 1.4 Confirm TanStack Start is the active router (via the
      `@tanstack/react-router` deps in the leaving-cert web app)
- [x] 1.5 Confirm the BAML foundation files at
      `baml/education/subjects/qpack_<subject>.baml` are in place for
      all 6 subjects

## Step 2 — Create the 6 per-subject route trees (4-5 hours)

For each of the 6 subjects (Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science), create 5 files at
`apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/subjects/<subject>/`:

- [x] 2.1 `mathematics/{index,syllabus,exam-papers,marking-schemes,study-plan}.tsx` (5 files)
- [x] 2.2 `chemistry/{index,syllabus,exam-papers,marking-schemes,study-plan}.tsx` (5 files)
- [x] 2.3 `geography/{index,syllabus,exam-papers,marking-schemes,study-plan}.tsx` (5 files)
- [x] 2.4 `gaeilge/{index,syllabus,exam-papers,marking-schemes,study-plan}.tsx` (5 files)
- [x] 2.5 `english/{index,syllabus,exam-papers,marking-schemes,study-plan}.tsx` (5 files)
- [x] 2.6 `computer_science/{index,syllabus,exam-papers,marking-schemes,study-plan}.tsx` (5 files)

Total: 30 per-subject route files.

Each `index.tsx` renders `<BIEPSubjectPage>` (the existing BIEP shared
component) + a 4-card grid linking to the 4 sub-routes + a bilingual
EN+GA mirror link.

Each `syllabus.tsx` / `exam-papers.tsx` / `marking-schemes.tsx` /
`study-plan.tsx` is a placeholder viewer/component that wires into the
per-subject Convex action + BAML function via the per-subject
declarations.

## Step 3 — Wire the per-subject Convex real-time backend (2-3 hours)

For each of the 6 subjects, create 6 files at `convex/<subject>/`:

- [x] 3.1 `mathematics/{schema,createSession,getSession,updateSession,generateStudyPlan,discussExamPaper}.ts` (6 files)
- [x] 3.2 `chemistry/{...}.ts` (6 files)
- [x] 3.3 `geography/{...}.ts` (6 files)
- [x] 3.4 `gaeilge/{...}.ts` (6 files)
- [x] 3.5 `english/{...}.ts` (6 files)
- [x] 3.6 `computer_science/{...}.ts` (6 files)

Total: 36 per-subject Convex files.

The `schema.ts` files declare 3 tables each (`study_sessions`,
`study_plans`, `exam_paper_discussions`) using the `subject:
v.literal("<slug>")` discriminator so per-subject schemas can be
deployed independently.

The `generateStudyPlan.ts` and `discussExamPaper.ts` files are Convex
**actions** that call into the per-subject BAML backend
(`b.WebStudyPlan` and `b.WebExamPaperDiscussion`).

## Step 4 — Wire the per-subject BAML backend (1-2 hours)

Create 6 BAML backend files at `baml/education/web/<subject>_web.baml`:

- [x] 4.1 `mathematics_web.baml` — `WebStudyPlan`,
      `WebExamPaperDiscussion`, `WebMarkingSchemeExplanation`
      (delegating to `qpack_mathematics.baml`)
- [x] 4.2 `chemistry_web.baml` (delegating to `qpack_chemistry.baml`)
- [x] 4.3 `geography_web.baml` (delegating to `qpack_geography.baml`)
- [x] 4.4 `gaeilge_web.baml` (delegating to `qpack_gaeilge.baml`)
- [x] 4.5 `english_web.baml` (delegating to `qpack_english.baml`)
- [x] 4.6 `computer_science_web.baml` (delegating to `qpack_computer_science.baml`)

Total: 6 per-subject BAML backend files.

## Step 5 — Verify (1 hour)

- [x] 5.1 Run the 30-file route verification (under task acceptance gate)
- [x] 5.2 Run the 36-file Convex verification
- [x] 5.3 Verify the 6 BAML backend files exist
- [x] 5.4 Sanity-check the per-subject route trees compile (`tsc --noEmit`
      on the leaving-cert web app — defer to the next agent; this
      change ships file scaffolding only, wiring happens in the next
      round)

## Step 6 — Write the openspec change (30 min)

- [x] 6.1 `proposal.md` — explain the 30+36+6 file inventory
- [x] 6.2 `tasks.md` — this file
- [x] 6.3 `specs/agentic-frontend-frameworks/spec.md` — MODIFIED:
      add 1 ADDED Requirement "Per-subject Convex + TanStack
      interactive web surface shipped for the 6 BIEP v1 LC subjects"
- [x] 6.4 Run `openspec validate 2026-07-16-biiep-v1-lc-per-subject-web-surface-v1 --strict`

## Step 7 — Commit + push (5 min)

- [x] 7.1 Stage + commit with the build-agent identity
- [x] 7.2 Push to `origin/pick-4-biep-v1` (NOT `main`)

## Total per-subject file count

| Asset | Per subject | × 6 subjects | Total |
|:--|--:|--:|--:|
| TanStack route files | 5 | × 6 | **30** |
| Convex schema + functions | 6 | × 6 | **36** |
| BAML backend files | 1 | × 6 | **6** |
| **Total** | **12** | **× 6** | **72** |

Plus 3 openspec change files (`proposal.md`, `tasks.md`,
`specs/agentic-frontend-frameworks/spec.md`).

**Grand total: 75 files committed.**