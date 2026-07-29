# Per-subject Convex + TanStack interactive web surface for the 6 BIEP v1 LC subjects

## Why

The BIEP v1 web surface ships per-subject landing pages at
`apps/.../routes/en/subjects/<subject>.tsx` (flat files), but those pages
do not expose the **per-subject interactive workflows** the 6 BIEP v1
LC subjects need for production: per-subject syllabus viewer + per-subject
past-exam-paper viewer + per-subject marking-scheme viewer + per-subject
study-plan generator. Each of those workflows needs its own route, its
own Convex real-time backend (session state + progress), and its own
per-subject BAML backend (study-plan + exam-paper-discussion +
marking-scheme-explanation).

This change ships the **per-subject interactive web surface** for the
6 BIEP v1 LC subjects — Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science — as a complete vertical slice per subject
(routes + Convex + BAML). The flat per-subject landing pages are kept
in place; the new per-subject directories live alongside them and
**supersede them for interactive use** (the existing flat files remain
the deep-link target so existing book-marks still resolve).

## What changes

| File group | Count | Status |
|:--|--:|:--|
| `apps/.../routes/en/subjects/<subject>/{index,syllabus,exam-papers,marking-schemes,study-plan}.tsx` | 30 | NEW |
| `convex/<subject>/{schema,createSession,getSession,updateSession,generateStudyPlan,discussExamPaper}.ts` | 36 | NEW |
| `baml/education/web/<subject>_web.baml` | 6 | NEW |
| `openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/{proposal,tasks}.md` | 2 | NEW |
| `openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/specs/agentic-frontend-frameworks/spec.md` | 1 | MODIFIED (1 ADDED Requirement) |

Total: **30 + 36 + 6 = 72 per-subject source files** + 3 openspec change files.

The 6 BIEP v1 LC subjects (per the user's locked plan) are:
1. `mathematics`
2. `chemistry`
3. `geography`
4. `gaeilge`
5. `english`
6. `computer_science`

Applied Maths and History are **out of scope** (excluded from this
change per the user's locked plan — they belong to BIEP v2).

## Subject-level breakdown

### Mathematics (Mata)

Per-subject routes (5):
- `apps/.../routes/en/subjects/mathematics/index.tsx` — landing page with 4 sub-route cards
- `apps/.../routes/en/subjects/mathematics/syllabus.tsx` — NCCA syllabus + learning outcomes viewer
- `apps/.../routes/en/subjects/mathematics/exam-papers.tsx` — past exam paper viewer (DiscussExamPaper)
- `apps/.../routes/en/subjects/mathematics/marking-schemes.tsx` — PCLM marking-scheme viewer
- `apps/.../routes/en/subjects/mathematics/study-plan.tsx` — study plan generator (WebStudyPlan)

Per-subject Convex files (6):
- `convex/mathematics/schema.ts` — study_sessions, study_plans, exam_paper_discussions tables
- `convex/mathematics/createSession.ts` — start a Mathematics study session
- `convex/mathematics/getSession.ts` — fetch the active Mathematics session
- `convex/mathematics/updateSession.ts` — update Mathematics session progress
- `convex/mathematics/generateStudyPlan.ts` — call `b.WebStudyPlan(subject="mathematics", ...)`
- `convex/mathematics/discussExamPaper.ts` — call `b.WebExamPaperDiscussion(subject="mathematics", ...)`

Per-subject BAML backend (1):
- `baml/education/web/mathematics_web.baml` — `WebStudyPlan`,
  `WebExamPaperDiscussion`, `WebMarkingSchemeExplanation`
  functions (delegating to `baml/education/subjects/qpack_mathematics.baml`).

### Chemistry (Ceimic)

Same 5+6+1 layout at:
- `apps/.../routes/en/subjects/chemistry/`
- `convex/chemistry/`
- `baml/education/web/chemistry_web.baml` (delegating to `qpack_chemistry.baml`)

### Geography (Tireolaiocht)

Same 5+6+1 layout at:
- `apps/.../routes/en/subjects/geography/`
- `convex/geography/`
- `baml/education/web/geography_web.baml` (delegating to `qpack_geography.baml`)

### Gaeilge (Gaeilge)

Same 5+6+1 layout at:
- `apps/.../routes/en/subjects/gaeilge/`
- `convex/gaeilge/`
- `baml/education/web/gaeilge_web.baml` (delegating to `qpack_gaeilge.baml`)

### English (Bearla)

Same 5+6+1 layout at:
- `apps/.../routes/en/subjects/english/`
- `convex/english/`
- `baml/education/web/english_web.baml` (delegating to `qpack_english.baml`)

### Computer Science (Riomheolaiocht)

Same 5+6+1 layout at:
- `apps/.../routes/en/subjects/computer_science/`
- `convex/computer_science/`
- `baml/education/web/computer_science_web.baml` (delegating to `qpack_computer_science.baml`)

## Why this layout — vertical-slice per subject

Each subject is a **vertical slice** (route + Convex + BAML). This
keeps the per-subject logic colocated and avoids cross-subject imports
in the schema, which would force a single deployment-wide schema
upgrade on every per-subject schema change. Instead:

- Per-subject Convex files declare their own tables (`study_sessions`
  is the shared shape across subjects; `study_plans` and
  `exam_paper_discussions` are per-subject namespaced by the
  `subject: v.literal("<slug>")` discriminator).
- Per-subject BAML files layer the web-facing functions on top of the
  existing per-subject foundation (`qpack_<subject>.baml`).
- Per-subject TanStack route trees mount each subject independently.

The vertical slice matches the per-subject agent-fleet pattern in
`meaisínfhoghlaim` (one agent per LC subject) and the per-subject
marimo-notebook pattern in `notebooks/`.

## Hard rules respected

- **Do NOT push to `main`** — push target is `origin/pick-4-biep-v1`
  (the existing feature branch where all prior BIEP work landed).
- **Do NOT touch the 50+ archived openspec changes** under
  `openspec/changes/archive/*`.
- **Do NOT include Applied Maths + History** (out of scope per the
  user's locked plan).
- **Do NOT modify the existing `apps/.../routes/en/subjects/` scaffold**
  — the 30 new route files live in 6 new sub-directories
  (`<subject>/`) alongside the existing flat files.
- **Do NOT touch the existing `baml/processing/_shared/video_kg.baml`**
  (parallel agent's work — outside this change's scope).
- **Do NOT modify the existing `packages/convex/src/index.ts`**
  single-schema scaffold — the new per-subject Convex files live in
  a parallel `convex/` tree.

## How to verify

```bash
# Verify the 30 per-subject route files
for s in mathematics chemistry geography gaeilge english computer_science; do
  for f in index syllabus exam-papers marking-schemes study-plan; do
    file="apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/subjects/$s/$f.tsx"
    [ -f "$file" ] && echo "  $file: OK" || echo "  $file: MISSING"
  done
done

# Verify the 36 per-subject Convex files
for s in mathematics chemistry geography gaeilge english computer_science; do
  for f in schema createSession getSession updateSession generateStudyPlan discussExamPaper; do
    file="convex/$s/$f.ts"
    [ -f "$file" ] && echo "  $file: OK" || echo "  $file: MISSING"
  done
done

# Verify the 6 per-subject BAML backend files
ls -1 baml/education/web/*_web.baml
```

## Dependencies

This change is **standalone** (no openspec blockers). It builds on
the prior BIEP work landed on `pick-4-biep-v1`:

- `2026-07-09-biep-6-subject-web-surfaces-v1` (archived) — the flat
  per-subject landing pages (`subjects/<subject>.tsx`).
- `2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1` — the
  English LC5 wiring.
- `2026-07-13-biep-v1-phase-1-1-english-wiring-v1` — Phase 1.1 verification.

This change does **not** block any other change.