# Tasks: 2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1

## Step 1: Consolidate the 9 ADDED Requirements to `british-isles-education-pipeline` spec (1.5h)

- [ ] Read the 7 source spec deltas to understand each ADDED Requirement
- [ ] Map the 9 ADDEDs to 8 R-groups (R0–R7):
  - R0: Phase 0 foundation (pre-existing canonical requirements)
  - R1: Phase 1.1 English lc5 wiring + duplicates cleanup
    (change 1: 2 ADDEDs combined)
  - R2: Phase 1.1 verification gates (change 3: 1 ADDED)
  - R3: BIEP 6-subject foundation — per-subject NCCA syllabus
    ingestion (change 6: 1 ADDED)
  - R4: Phase 4-5 BAML fix — MarkingPoint classes + v0.212+ syntax
    (changes 2 + 5: 2 ADDEDs combined)
  - R5: Phase 6 — 6 per-subject marimo notebooks (change 4: 1 ADDED)
  - R6: Phase 7 — Daily MotherDuck lc_pdf_sync_flight (change 4: 1 ADDED)
  - R7: BIEP 6-subject marking + interactive grading (change 7: 1 ADDED)
- [ ] Write the MODIFIED spec delta at
  `openspec/changes/2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1/specs/british-isles-education-pipeline/spec.md`
  with `## ADDED Requirements` (8 new R-group requirements) + `## MODIFIED Requirements`
  (cross-reference update)

## Step 2: Consolidate the 6 ADDED Requirements to `cianfhoghlaim-baml-schemas` spec (1h)

- [ ] Read the 5 source spec deltas to understand each ADDED Requirement
- [ ] Map the 6 ADDEDs to 4 logical change groups:
  - Group 1: v0.212+ migration (change 1 fix-baml-codegen: 2 ADDEDs
    + change 4 baml-final-cleanup: 1 ADDED = 3 ADDEDs combined)
  - Group 2: v0.223 test CI gate (change 2 baml-cli-test-ci-gate:
    1 ADDED)
  - Group 3: v0.223 type-builder NCCA (change 3 baml-type-builder-ncca:
    1 ADDED)
  - Group 4: Option-2 50-error fix (change 5 fix-baml-50-out-of-scope:
    1 ADDED)
- [ ] Write the MODIFIED spec delta at
  `openspec/changes/2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1/specs/cianfhoghlaim-baml-schemas/spec.md`
  with `## ADDED Requirements` (4 new logical-change requirements)

## Step 3: Reconcile the leabharlann doc + sub-corpora counts (30 min)

- [ ] Update the canonical `cianfhoghlaim-cognify-knowledge-graph/spec.md`
  "Leabharlann cognify" requirement (line 61) and "Cross-archive edges"
  requirement (line 88) to reference 6 sub-corpora instead of 3 corpora
- [ ] Write the MODIFIED spec delta at
  `openspec/changes/2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1/specs/cianfhoghlaim-cognify-knowledge-graph/spec.md`
  with `## MODIFIED Requirements` for those 2 requirements

## Step 4: Reconcile the 4 marimo count claims (30 min)

- [ ] Confirm the actual on-disk count via
  `ls notebooks/**/*.py | wc -l` (clean: 134 files;
  raw: 160 files including __init__.py + __pycache__)
- [ ] Write the MODIFIED spec delta at
  `openspec/changes/2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1/specs/cianfhoghlaim-marimo-dashboards/spec.md`
  adding 1 new requirement declaring the on-disk count as the
  source of truth + 1 MODIFIED requirement updating the
  cross-reference at line 250 from "the 11 Marimo notebooks" to
  "the on-disk count of Marimo notebooks (per
  `ls notebooks/**/*.py | wc -l`)"

## Step 5: Consolidate the leabharlann → culture-heritage edge ownership (30 min)

- [ ] Update the canonical `cianfhoghlaim-cognify-knowledge-graph/spec.md`
  "Cross-archive edges" requirement to declare the ownership
  boundary: leabharlann change owns the 4 leabharlann-X rules
  (including `leabharlann_culture_heritage.py`); cognify change owns
  the 2 BIEP-X rules (minus the leabharlann → culture-heritage
  edges)
- [ ] Note in the spec delta: the actual code consolidation
  (removing the duplicate from `cross_archive_biep_edges.py`) is
  deferred to a follow-up change (per the "Do NOT modify the
  existing cross-archive code" hard rule)

## Step 6: Commit + push (10 min)

- [ ] Run `openspec validate 2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1 --strict`
  and ensure 0 errors
- [ ] Stage all 4 spec deltas + proposal.md + tasks.md
- [ ] Commit with the canonical message:
  ```
  chore(openspec): consolidate 8 BIEP + 6 BAML + 4 dashboard spec deltas

  Implements openspec change 2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1
  (4 MODIFIED spec deltas on british-isles-education-pipeline +
  cianfhoghlaim-baml-schemas + cianfhoghlaim-cognify-knowledge-graph +
  cianfhoghlaim-marimo-dashboards).
  ```
- [ ] Push to `origin/pick-4-biep-v1` (NOT `main`)

## Verification checklist

- [ ] `openspec validate --strict` passes for all 4 affected specs
- [ ] 9 + 6 + 1 + 1 = 17 spec deltas are now sequential + consistent
- [ ] The 225 leabharlann doc count is consistent
- [ ] The 6 sub-corpora count is consistent
- [ ] The leabharlann → culture-heritage edge ownership is declared
  in the spec delta (leabharlann change owns the leabharlann-X
  rules; cognify change owns the BIEP-X rules minus the leabharlann
  → culture-heritage edges)
- [ ] Pushed to `origin/pick-4-biep-v1` (NOT `main`)