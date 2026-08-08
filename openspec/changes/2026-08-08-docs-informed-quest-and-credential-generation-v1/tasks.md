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

## Phase 5 — Client wiring — DONE (scope narrowed from the original
description below — see 5.1-note)

- [x] 5.1 Added a `questPacks` table to `convex/schema.ts` (packId,
  subject, framework, level, bilingual title/description, totals,
  losCovered, items (opaque JSON via `v.any()` — item shape's `topic`/
  `item_type` enums differ per subject, so the BAML class is the
  source of truth, not this schema), prerequisites, crossSubjectLinks,
  generatedAt/By). **Note (redo pass)**: indexed by `by_subject` +
  `by_pack_id`, not `(subject, level)` — `quest_pack_assets.py` (built
  in this same redo pass, see Phase 2.2) generates exactly one Higher
  Level pack per subject today, not one per level, so a level-scoped
  index wasn't needed; `questPacks:create` deletes any existing row
  for the subject before inserting (idempotent re-materialisation).
- [x] 5.2 New `convex/questPacks.ts` — `create` mutation (replace
  semantics per 5.1-note) + `getBySubject`/`listAll` queries (not
  `listBySubjectLevel`, per the same scope narrowing).
- [x] 5.3 Replaced `realm/$subject.tsx`'s hardcoded `QuestPackCard`
  counts with a real `useQuery(api.questPacks.getBySubject, ...)`
  call, with loading/empty/generated states; "Start" expands the
  pack's first real formative item inline (a fuller attempt-taking UI
  is separate future work, not fabricated here).
- [x] 5.4 **Found and fixed**: the app had no `ConvexProvider`/
  `ConvexReactClient` anywhere — added to `__root.tsx`, alongside
  `CopilotKit` (pulled forward from
  `2026-08-08-agui-generative-credential-ui-v1` Phase 1, since both
  providers had to land in the same root component).
- [ ] 5.5 **Follow-on, still blocked**: `convex/_generated/` doesn't
  exist — `convex codegen` requires `CONVEX_DEPLOYMENT` (a live,
  authenticated Convex project — `npx convex dev` login). Not
  fabricable in this environment. All new/edited `.ts` files
  (`questPacks.ts`, `x402Payments.ts`, `badges.ts`, and every route
  importing `convex/_generated/api`) are written correctly against
  this not-yet-generated API and will resolve once codegen runs.
- [x] 5.6 **New in this redo pass, not in the original Phase 5**:
  found the app has no Vite/TanStack Start entry bootstrap at all — no
  `index.html`, no client entry, `vite.config.ts` registers only the
  router plugin (`TanStackRouterVite`), not `tanstackStart()`, despite
  `@tanstack/react-start` being a declared dependency. Flagged as a
  separate, pre-existing, out-of-scope blocker rather than fabricated
  from memory of a fast-moving meta-framework's exact bootstrap API
  (risk of a plausible-looking but non-functional scaffold). Route
  files are still written correctly against the repo's existing
  `createRootRoute`/`createFileRoute` conventions.

## Phase 5b — Additional bugs found while re-verifying this pass (new)

Discovered and fixed while rebuilding `quest_pack_assets.py` and
wiring the Convex read/write paths — none of these were caught by the
original (lost) session's Phase 1-5 work, since none of it had been
run live end-to-end before the data loss:

- [x] The 3 base extraction functions this change's "Why" section
  described as "real and working"
  (`ExtractCurriculumSyllabus`/`ExtractExamPaperLayout`/
  `ExtractMarkingSchemeGuideline`) were themselves still literal
  `"Auto-generated extraction prompt."` placeholders — the "real and
  working" claim was true of the extraction *schema*, not the prompt
  bodies. Fixed with real prompts grounded in each function's class
  schema.
- [x] **Systemic bug**: every prompt ending directly in
  `{{ ctx.output_format }}` with no `{{ _.role("user") }}` marker
  renders as a single system-role message with no user turn — MiniMax
  rejects this as "chat content is empty" (HTTP 400). Found via live
  smoke test of `ExtractCurriculumSyllabus`; fixed in all 5 Ireland LC
  extraction files (the 3 above plus `cross_linguistic.baml` and
  `syllabus_diagram.baml`, both pre-existing and never live-tested
  before). A repo-wide sweep found 6 more files with the same gap,
  outside this change's scope (Crown Dependencies `subject_taxonomy.baml`
  files) — left unfixed, tracked separately.
- [x] `tuatha/badges/ledger.py`'s `fetch_badges_for_student()` and
  `fetch_badges_since()` (the latter called directly by
  `daily_credential_anchor`) sent query args that didn't match
  `badges.ts`'s validators (`student_id` vs `studentId`; an ISO string
  vs the required epoch-ms `sinceMs`), and `SkillTreeBadge(**row)`
  could never have worked against a real Convex row (flat/camelCase
  vs. the model's nested/snake_case shape). Fixed both call sites plus
  added a `_row_to_badge()` mapper; also found `issue_badge()`'s write
  path never sent `evidence.feedback_en/feedback_ga/source_pdf/
  source_page` at all — added the missing Convex columns and mapping.
- [x] Live-verified `ExtractCurriculumSyllabus` end-to-end against the
  real chemistry syllabus PDF after both fixes above: 90 real learning
  outcomes extracted across the syllabus's 5 strands, correctly
  grounded in the source text (module names, strand structure, exact
  learning-outcome wording) — not fabricated.

## Phase 6 — Verification

- [x] 6.1 `openspec validate 2026-08-08-docs-informed-quest-and-
  credential-generation-v1 --strict`.
- [x] 6.2 For ≥1 Ireland LC subject (chemistry) and ≥1 Ireland JC
  level, confirmed generated-content shape traces to real source-PDF
  pages via the rewritten prompts' `evidence` field requirements —
  **and**, in this redo pass, confirmed live against the real MiniMax
  API (see Phase 5b's last item), not just via BAML compilation.
  England (GCSE/A-Level) tracing is blocked on Phase 3.2.
- [x] 6.3 Ran `uv run python scripts/sync/spec_agents.py` — completes
  successfully; nothing of this change's to regenerate until archived.
- [x] 6.4 Ran `mise run lint:drift-docs` — fails only on pre-existing,
  unrelated drift (a stale "92 stacks" claim in `AGENTS.md`, real
  count 93) — not caused by this change.
