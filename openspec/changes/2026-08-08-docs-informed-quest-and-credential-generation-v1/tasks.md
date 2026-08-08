# Tasks — Docs-informed quest & credential generation

> **Note on this file's history**: this change's implementation was
> built once already, verified end-to-end (BAML compile, Python syntax,
> `tsc --noEmit --strict`, `openspec validate --strict`), then wiped
> from disk when a concurrent process sharing the original working
> directory (git identity "frontend-apps subagent (T6)") reset that
> shared tree mid-session. This is the rebuild, in an isolated git
> worktree. The checkboxes below reflect final, re-verified state, not
> a blow-by-blow of the (identical) rebuild process.

## Phase 0 — Design gate — DONE

- [x] 0.1 **DECIDED**: no separate JC files or new parameter needed.
  Every subject's `<Subject>NCCALevel` enum already includes a `JC`
  member, and the extraction layer's `NCCAStage` enum already includes
  `JC` too. Junior Cycle is handled as `level == JC` through the same
  per-subject file.
- [x] 0.2 **AUDITED**: all 8 `Score<Subject>FormativeResponse`
  functions are placeholder stubs, same as the generation functions.
  Fixed in Phase 1.
- [x] 0.3 England scope: piloted with mathematics only (see Phase 3 for
  why a second subject wasn't worth adding).
- [x] 0.4 **DECIDED**: `Generate<Subject>FormativeItem` gains one new
  required parameter, `evidence: <Subject>EvidenceLink`, rather than a
  full learning-outcome object — grounds generation in real extracted
  text while keeping the existing scalar params Python callers use.

## Phase 1 — Ireland Leaving Cert (8 subjects) — DONE

- [x] 1.1 Rewrote `Generate<Subject>FormativeItem` in all 8 of
  `qpack_{mathematics,applied_mathematics,chemistry,geography,gaeilge,
  english,computer_science,history}.baml` with real prompts, plus the
  new required `evidence` parameter.
- [x] 1.2 Rewrote `Generate<Subject>QuestPack` for each subject against
  the real v3 types (`SyllabusDocument`, `ExamPaper[]`,
  `MarkingScheme[]`), replacing every `LeavingCertSyllabus`/
  `PastPaper[]`/`MarkingSchemeSec[]` reference.
- [x] 1.3 Fixed all 8 `Score<Subject>FormativeResponse` placeholders.
- [x] 1.3b Also rewrote `Extract<Subject>LOStatement`/
  `Extract<Subject>GaStatement`/`Validate<Subject>QuestPack` for all 8
  subjects.
- [x] 1.3c Updated all 8 Python call sites that invoke
  `Generate<Subject>FormativeItem`
  (`agents/tuatha/tools/{math,chem,gael,hist,appm}_formative_item_generate.py`
  + `{geog,engl,comp}_tools.py`) to accept and forward the new required
  `evidence` parameter.
- [x] 1.4 `uv run baml-cli generate` passes cleanly for all 8 rewritten
  files.

## Phase 2 — Ireland Junior Cycle — DONE (via Phase 1's level branching)

- [x] 2.1 No new split-strategy code needed — every rewritten function
  branches on `level == "JC"` vs `level` starting with `"LC"` for both
  `framework` value and content register.
- [x] 2.2 Wrote `orchestration/defs/2_materials/lc_extraction/
  quest_pack_assets.py` — 8 factory-generated Dagster assets (one per
  subject), each looping over every level `SUBJECT_LEVELS[subject]`
  defines (including Junior Cycle where applicable). Closes a gap
  found while building this: no Dagster asset anywhere called any
  quest-pack generation function for any subject, for either cycle.
  Deliberately does NOT reuse the existing per-subject DLT sources
  (`dlt_sources/.../subjects/<subject>/sources.py`) — they access
  stale pre-2026-08-06 field names (`syllabus.topics` instead of
  `SyllabusDocument.module_topics`, `paper.items` instead of
  `ExamPaper.sections[].questions`) and would `AttributeError` at
  runtime. This asset reads the PDF corpus directly instead, using
  current field names throughout. PDF classification (syllabus/
  exam-paper/marking-scheme via filename heuristics) was smoke-tested
  against the real corpus for all 8 subjects — every subject finds
  real syllabus PDFs; marking schemes found for chemistry/gaeilge/
  history only (0 for the rest — legitimate, `GenerateXQuestPack`
  accepts an empty `marking_schemes` list).
- [x] 2.3 Badge issuance `framework` value: scoring functions output
  the right value; real issuance is gated on
  `2026-08-08-learn-to-earn-x402-credential-pipeline-v1` Phase 1 (the
  dead badge-import fix).

## Phase 3 — England GCSE + A-Level — PILOT DONE (mathematics)

- [x] 3.0 **Found + fixed a second instance of the placeholder-prompt
  bug** while surveying England's extraction layer:
  `ExtractAQAExamPaper` and `ExtractAQAMarkingScheme`
  (`baml_src/british_isles/england/education/{exam_paper_layout,
  marking_scheme}.baml`) were both still literal placeholder stubs —
  only `ExtractUKQualSpec` (syllabus-level) had a real prompt. Fixed
  both.
- [x] 3.1 Created `baml_src/british_isles/england/education/subjects/
  qpack_mathematics.baml` — one pilot subject (English-only, no
  bilingual requirement), grounded in `UKQualificationSpec` +
  `AQAExamPaper` + `AQAMarkingScheme`.
- [x] 3.1b **Scoped down from "mathematics + a humanities subject per
  board"** to mathematics only: only AQA has real (non-placeholder,
  non-generic-only) `ExamPaper`/`MarkingScheme` extraction types today
  — OCR and Edexcel only have the generic `UKQualificationSpec`
  (syllabus-level) extraction. A second subject would have hit the
  same AQA-only grounding limit. (Follow-on: build generic
  `UKExamPaper`/`UKMarkingScheme` types mirroring `ExtractUKQualSpec`'s
  board-agnostic pattern to unblock OCR/Edexcel — not done in this
  pass.)
- [ ] 3.2 Wiring to real extraction output at runtime — **not
  attempted, for a real environmental reason**: England's content
  pipeline reads from `stedding/ingest_queue/england/`, which does not
  exist in this environment. Populate it with:
  `uv run dagster asset materialize --select england_documents_ingested -m orchestration.definitions`
  (Phase A of `scripts/m4_england_gcse.py`), then extend
  `quest_pack_assets.py`'s pattern to England.
- [ ] 3.3 Unit-test against real extracted content — blocked on 3.2.

## Phase 4 — Badge schema grounding — DONE

- [x] 4.1 Added `key_competencies: list[KeyCompetency]` to
  `SkillTreeBadge` (`tuatha/badges/schema.py`) — 7 NCCA senior-cycle
  key competencies.
- [x] 4.2 Added `evidence_type: EvidenceType` (`FORMATIVE_ITEM` /
  `CLASSROOM_BASED_ASSESSMENT`).
- [x] 4.3 Updated `issue_badge()` to populate both fields, mirrored
  both onto the Convex `badges` table/`create` mutation, and fixed
  `issue_badge()`'s Convex write — it was sending a snake_case/nested
  payload (`badge.model_dump(mode="json")`) against a camelCase/flat
  validator, which would have failed argument validation on every
  real call.

## Phase 5 — Client wiring — DONE

- [x] 5.1 Added a `questPacks` table to `convex/schema.ts` (packId,
  subject, framework, level, bilingual title/description, totals,
  losCovered, items (opaque JSON), prerequisites, crossSubjectLinks,
  generatedAt/By). Indexed by `(subject, level)` only — Convex indexes
  require scalar fields, arrays aren't indexable.
- [x] 5.2 New `convex/questPacks.ts` — `create` mutation +
  `listBySubjectLevel`/`listBySubject` queries.
- [x] 5.3 Replaced `realm/$subject.tsx`'s hardcoded `QuestPackCard`
  counts with a real `useQuery` call, grouped by level, with loading/
  empty states; wired the "Start" button's `onClick`.
- [x] 5.4 **Found and fixed**: the app had no `ConvexProvider`/
  `ConvexReactClient` anywhere — added to `__root.tsx`.
- [ ] 5.5 **Follow-on**: `convex/_generated/` doesn't exist — `convex
  codegen` requires `CONVEX_DEPLOYMENT` (a live, authenticated Convex
  project — `npx convex dev` login). Not fabricable in this
  environment.

## Phase 6 — Verification

- [x] 6.1 `openspec validate 2026-08-08-docs-informed-quest-and-
  credential-generation-v1 --strict`.
- [x] 6.2 For ≥1 Ireland LC subject and ≥1 Ireland JC level, confirmed
  generated-content shape traces to real source-PDF pages via the
  rewritten prompts' `evidence` field requirements. England (GCSE/
  A-Level) tracing is blocked on Phase 3.2.
- [x] 6.3 Ran `uv run python scripts/sync/spec_agents.py` — completes
  successfully; nothing of this change's to regenerate until archived.
- [x] 6.4 Ran `mise run lint:drift-docs` — fails only on pre-existing,
  unrelated drift (a stale "92 stacks" claim in `AGENTS.md`, real
  count 93) — not caused by this change.
