# 2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1

## Why

The 3rd audit of the BIEP v1 + BAML + marimo + cognify + leabharlann
openspec change trail (commit `cd61b36a5` and earlier on
`pick-4-biep-v1`) found **5 inconsistencies** in the spec-delta trail
that need consolidation before the BIEP v1 + BAML v0.223 + leabharlann
v1 stack can be archived as a coherent unit:

1. **british-isles-education-pipeline spec**: 8 separate ADDED
   Requirements spread across 7 archived-but-not-yet changes —
   `2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1` (2 ADDEDs)
   + `2026-07-13-baml-final-cleanup-v1` (1) +
   `2026-07-13-biep-v1-phase-1-1-english-wiring-v1` (1) +
   `2026-07-13-biep-v1-phases-6-7-unblock-v1` (2) +
   `2026-07-13-fix-baml-50-out-of-scope-errors-v1` (1) +
   `2026-07-16-biiep-v1-lc-per-subject-syllabus-ingestion-v1` (1) +
   `2026-07-16-biiep-v1-lc-per-subject-marking-grading-v1` (1).
   These were shipped in feature-burst order (Phase 1.1 → 1.1 verify →
   4-5 BAML → 6 → 7 → BIEP-foundation → BIEP-marking) rather than
   the canonical R-group history. The canonical spec at
   `openspec/specs/british-isles-education-pipeline/spec.md` should
   carry the consolidated R0–R7 sequential history.

2. **oideachais-baml-schemas spec**: 6 separate ADDED Requirements
   spread across 5 changes —
   `2026-07-10-fix-baml-codegen-v4-syntax-v1` (2) +
   `2026-07-12-baml-cli-test-ci-gate-v1` (1) +
   `2026-07-12-baml-type-builder-ncca-v1` (1) +
   `2026-07-13-baml-final-cleanup-v1` (1) +
   `2026-07-13-fix-baml-50-out-of-scope-errors-v1` (1). These need
   consolidation into 4 logical change groups (v0.212+ migration /
   v0.223 test CI gate / v0.223 type-builder / Option-2 50-error fix).

3. **oideachais-cognify-knowledge-graph spec**: the "Leabharlann
   cognify" requirement says "the 3 leabharlann corpora (books,
   zotero, takeout)" — but the canonical leabharlann spec covers 6
   sub-corpora (`aigne/`, `gaeilge/`, `gemini_deep_research/`, `mata/`,
   `ollscoil_na_gaillimhe/`, `zotero/`) = 225 documents on disk. The
   cognify spec delta (and the parent change's claim) need to mention
   the 6 sub-corpora, not the legacy 3.

4. **oideachais-marimo-dashboards spec**: 4 stale count claims across
   4 change subdirs:
   - `2026-07-14-oideachais-marimo-dashboards-v1` claims "11 BIEP
     notebooks" (the BIEP motherduck subdir count, accurate) but the
     change's "10 follow-up dashboards" claim is the 10 v1 dashboards.
   - `2026-07-15-oideachais-marimo-dashboards-extension-v1` claims
     "Existing 15+10=25 notebooks" — but the on-disk count of all
     marimo notebooks at the time was the current
     `ls notebooks/**/*.py | wc -l` count (134 clean
     notebooks on disk today).
   - `2026-07-16-biiep-v1-lc-per-subject-marimo-study-tools-v1` claims
     "Existing 30+10+10=50 notebooks" — same: should be aligned to
     the actual on-disk count.
   - `2026-07-12-baml-cocoindex-tutorials-v1` claims "5 new BAML
     tutorials" — accurate (the 5 EN tutorials are the "new" additions;
     the 5 GA siblings come from the later
     `2026-07-13-baml-cocoindex-tutorials-ga-v1` change).

   The canonical spec at
   `openspec/specs/oideachais-marimo-dashboards/spec.md` should
   document that **the on-disk count from
   `ls notebooks/**/*.py | wc -l` is the source of
   truth** for all marimo notebook count claims, and the canonical
   cross-reference at line 250 ("the 11 Marimo notebooks") should be
   updated to reflect the current on-disk count.

5. **Cross-archive leabharlann → culture-heritage edge duplicate**:
   the same `(:LeabharlannAuthor)-[:COREFERS_WITH]->(:CultureHeritagePerson)`
   + `(:LeabharlannDoc)-[:ABOUT]->(:CultureHeritagePlace)` edges are
   shipped by **two files**:
   - `storage/cognify/rules/cross_archive_biep_edges.py`
     (the BIEP cross-archive file, owned by the cognify change)
   - `storage/cognify/rules/leabharlann_culture_heritage.py`
     (the leabharlann orchestrator, owned by the leabharlann change)

   The leabharlann change owns the 4 leabharlann-X rules
   (`leabharlann_cross_archive.py` + `leabharlann_official_media.py`
   + `leabharlann_culture_heritage.py` + `leabharlann_authors_archive.py`);
   the cognify change owns the 2 BIEP-X rules
   (`cross_archive_biep_edges.py` + `university_cross_archive.py`).
   The leabharlann → culture-heritage edge belongs in
   `leabharlann_culture_heritage.py` (it's a leabharlann-aware rule).
   **The spec delta should declare this ownership boundary in the
   canonical specs.** Per the "Do NOT modify the existing
   cross-archive code" hard rule in this change's brief, the
   duplicate code in `cross_archive_biep_edges.py` is left in place
   for a follow-up change to actually remove it (logged as a
   blocker).

## What changes

This change is a **spec-delta consolidation** — 4 MODIFIED spec
deltas against the canonical specs, no code changes:

| File | Action | Why |
|:--|:--|:--|
| `openspec/specs/british-isles-education-pipeline/spec.md` | MODIFIED (via delta) | Re-namespace the 9 ADDED Requirements from 7 changes into R0–R7 sequential R-group history |
| `openspec/specs/oideachais-baml-schemas/spec.md` | MODIFIED (via delta) | Re-namespace the 6 ADDED Requirements from 5 changes into 4 logical change groups |
| `openspec/specs/oideachais-cognify-knowledge-graph/spec.md` | MODIFIED (via delta) | Update the "3 leabharlann corpora" claim to "6 sub-corpora" |
| `openspec/specs/oideachais-marimo-dashboards/spec.md` | MODIFIED (via delta) | Declare the on-disk count (`ls notebooks/**/*.py \| wc -l`) as the canonical source of truth; align the cross-reference |

The spec deltas live at:
- `openspec/changes/2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1/specs/british-isles-education-pipeline/spec.md`
- `openspec/changes/2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1/specs/oideachais-baml-schemas/spec.md`
- `openspec/changes/2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1/specs/oideachais-cognify-knowledge-graph/spec.md`
- `openspec/changes/2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1/specs/oideachais-marimo-dashboards/spec.md`

## Out of scope

- The 50+ archived openspec changes under `openspec/changes/archive/*`
  are NOT touched (hard rule).
- The 7 `baml/education/lc_extraction/*.baml` files
  (owned by the BIEP v1 change) are NOT modified (hard rule).
- The `cross_archive_biep_edges.py` source code is NOT modified
  (hard rule — the duplicate leabharlann → culture-heritage edges
  remain in 2 files; the consolidation change only re-namespace the
  spec deltas to declare the ownership boundary).
- The 4 source change subdirs
  (`2026-07-14-oideachais-marimo-dashboards-v1` /
  `2026-07-15-oideachais-marimo-dashboards-extension-v1` /
  `2026-07-16-biiep-v1-lc-per-subject-marimo-study-tools-v1` /
  `2026-07-12-baml-cocoindex-tutorials-v1`) are NOT modified —
  the stale count claims remain in the change subdirs as historical
  artifacts; the canonical spec delta adds a new requirement
  documenting the on-disk count as the source of truth.

## Dependencies

```yaml
Blocked by: none
Blocked by (soft):
  - 2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1
    (Phase 1.1 English wiring — the 2 ADDEDs consolidated into R1)
  - 2026-07-13-baml-final-cleanup-v1
    (the MarkingPoint classes rename — the 1 ADDED consolidated into R4)
  - 2026-07-13-biep-v1-phase-1-1-english-wiring-v1
    (Phase 1.1 verification gates — the 1 ADDED consolidated into R2)
  - 2026-07-13-biep-v1-phases-6-7-unblock-v1
    (Phase 6 + Phase 7 — the 2 ADDEDs consolidated into R5 + R6)
  - 2026-07-13-fix-baml-50-out-of-scope-errors-v1
    (the v0.212+ canonical syntax fix — the 1 ADDED consolidated into R4)
  - 2026-07-16-biiep-v1-lc-per-subject-syllabus-ingestion-v1
    (BIEP 6-subject foundation — the 1 ADDED consolidated into R7)
  - 2026-07-16-biiep-v1-lc-per-subject-marking-grading-v1
    (BIEP 6-subject marking — the 1 ADDED consolidated into R8)
  - 2026-07-10-fix-baml-codegen-v4-syntax-v1
    (v0.212+ migration — the 2 ADDEDs consolidated into the v0.212+
    migration requirement)
  - 2026-07-12-baml-cli-test-ci-gate-v1
    (v0.223 test CI gate — the 1 ADDED consolidated into the v0.223
    CI gate requirement)
  - 2026-07-12-baml-type-builder-ncca-v1
    (v0.223 type-builder — the 1 ADDED consolidated into the v0.223
    type-builder requirement)
  - 2026-07-13-fix-baml-50-out-of-scope-errors-v1 (BAML side)
    (Option 2 fix — the 1 ADDED consolidated into the Option-2
    50-error fix requirement)
  - 2026-07-14-oideachais-cognify-knowledge-graph-v1
    (the 3 corpora claim — the 1 MODIFIED requirement consolidates
    to 6 sub-corpora)
  - 2026-07-14-oideachais-marimo-dashboards-v1
  - 2026-07-15-oideachais-marimo-dashboards-extension-v1
  - 2026-07-16-biiep-v1-lc-per-subject-marimo-study-tools-v1
  - 2026-07-12-baml-cocoindex-tutorials-v1
    (the 4 marimo count claims — the 1 MODIFIED requirement declares
    the on-disk count as the source of truth)

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1 --strict`
  passes (4 MODIFIED spec deltas, all well-formed)
- The 9 + 6 + 1 + 1 = 17 spec deltas across the 4 canonical specs
  are now sequential + consistent (R0–R7 history for BIEP,
  4 logical change groups for BAML, 6 sub-corpora for cognify,
  on-disk count for marimo)
- The 225 leabharlann doc count is consistent across the leabharlann
  spec + the cognify spec (the cognify spec now references 6
  sub-corpora)
- The leabharlann → culture-heritage edge ownership is declared in
  the spec delta (the leabharlann change owns the
  `leabharlann_culture_heritage.py` rule; the cognify change owns
  the `cross_archive_biep_edges.py` rule minus the leabharlann →
  culture-heritage edges)
- Pushed to `origin/pick-4-biep-v1` (NOT `main`)

## Open questions / blockers

- **Cross-archive code duplicate** (logged but not fixed): the
  `(:LeabharlannAuthor)-[:COREFERS_WITH]->(:CultureHeritagePerson)` +
  `(:LeabharlannDoc)-[:ABOUT]->(:CultureHeritagePlace)` edges are
  implemented in BOTH
  `storage/cognify/rules/cross_archive_biep_edges.py`
  (owned by the cognify change) AND
  `storage/cognify/rules/leabharlann_culture_heritage.py`
  (owned by the leabharlann change). Per the "Do NOT modify the
  existing cross-archive code" hard rule in this change's brief, the
  duplicate code is left in place. The spec delta declares the
  ownership boundary (leabharlann change owns the leabharlann-X
  rules; cognify change owns the BIEP-X rules minus the
  leabharlann → culture-heritage edges) but the actual code
  consolidation is a follow-up task for a separate change.
- **Parallel-agent dirty state**: there are 30+ modified + untracked
  files in the working tree from parallel agents. Per the change
  brief, the pre-flight `git pull --rebase` was NOT run (dirty
  state present); all commits + pushes are independent of those
  changes. The final report will list the untracked dirty files.