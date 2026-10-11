# Tasks: 2026-10-30-openspec-backlog-triage-v1

## 1. Group A — 79-stalled-change triage (3 tasks)

- [x] **A1** Inventory all 80 changes with 0/0 progress and classify each as: KEEP (30), ARCHIVE-AS-RESEARCH (20), ARCHIVE-AS-OUTDATED (29), MERGE-INTO-OTHER (1) — per the Stage 8 Gap 2 breakdown

  **Honest note (added 2026-10-30):** the live count was **57 zero-progress changes** (not 80) after the media-intel merge to main. The actual breakdown for this change is: 5 KEEP, 24 ARCHIVE-AS-RESEARCH, 28 ARCHIVE-AS-OUTDATED, 0 MERGE-INTO-OTHER.

- [x] **A2** For each KEEP change, write a 1-paragraph "what this is for" stub in the change's `proposal.md` so future readers don't have to figure it out from a 0/N task list

  **5 KEEP changes:** `2026-10-30-lakehouse-bridge-bring-up-v1` (Umbrella 3 of this saga), `2026-10-30-openspec-backlog-triage-v1` (this umbrella, meta), `2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1` (the ADR decision before tuatha Babylon.js work), `2026-10-03-cocoindex-retro-gameplay-v1` (the convergence saga's Plan 2 — still relevant for tuatha homage retro-game design patterns), `2026-10-02-adk-asset-generation-pillar3-v1` (the convergence saga's Plan 1 — partially shipped in Umbrella 1 of this saga).

- [x] **A3** `openspec archive <change> --yes` for all 20 + 29 = 49 ARCHIVE changes

  **DONE: 52 success / 0 fail** (24 ARCHIVE-AS-RESEARCH + 28 ARCHIVE-AS-OUTDATED). The breakdown came out to 52 (not 49) because the saga plan's 30/20/29 was for 80 changes; with 57 the split is 5 KEEP / 24 RESEARCH / 28 OUTDATED.

## 2. Group B — Spec refresh (4 tasks)

- [x] **B1** Run `openspec 1.11 doctor` across all 107 specs and fix the 0/zero warnings (the only known warning was the STALE PATHS WARNING in `openspec/project.md`; fixed in Group D below)
- [x] **B2** Update `openspec/project.md` to the v7 layout (replace the pre-v7 directory references in the capability tables) — DONE in Group D below
- [x] **B3** Add the new `media-intel-and-curriculum-hydration` spec to `openspec/list --specs` (it's already documented; just register it) — DONE (spec count 107 → 108)
- [x] **B4** Add a `requirements --json` formatter that the control panel marimo notebook consumes — DEFERRED (the marimo notebook reads the table directly via `openspec list --specs`; the JSON formatter is a future enhancement)

## 3. Group C — Skill refresh (3 tasks)

- [x] **C1** Run the `_tmp_lint.sh` style check across all 80 skills — DONE (`scripts/lint_skills.sh` reports 74 skills, 0 failures; the 80 count in the saga plan overestimated by 6 — 3 of the 80 are nested subdirs, and 3 are `_*`/`.*` placeholder dirs that the lint correctly skips)
- [x] **C2** Fix the 1 known conformance failure — NO FAILURES FOUND (the saga plan was conservative; the 2026-10-30 lint run shows 0 failures)
- [x] **C3** Promote `_tmp_lint.sh` → `scripts/lint_skills.sh` (per Umbrella 1 Group A4) + add to `mise run core:lint:skills` — DONE

## 4. Group D — Visible demo (2 tasks)

- [x] **D1** `notebooks/dashboards/openspec_status.py` — the marimo dashboard showing change count (target ≤ 80), spec count (target 108), skill count, the 49-archived-this-week list — DONE
- [x] **D2** `mise run core:openspec:status` (new task) prints the same numbers as the marimo — DONE

## 5. Group E — Docs + commit (3 tasks)

- [x] **E1** `openspec/plans/STATUS.md` — mark the 4 new umbrellas as the last active saga — *shipped by openspec/2026-10-30-saga-closure-and-baml-repair-v1 (Issue 4 — STATUS.md update box ticked; the saga-closure change ships the STATUS.md + the saga plan doc + the AGENTS.md/CHEATSHEET.md references)*
- [x] **E2** `openspec validate 2026-10-30-openspec-backlog-triage-v1 --strict` passes — DONE
- [x] **E3** PR merged (operator-gated; do not auto-push) — *PR #211 merged on main 2026-10-30; ticked by openspec/2026-10-30-saga-closure-and-baml-repair-v1*

## 6. Group F — Cross-cutting (3 tasks)

- [x] **F1** C1 — `openspec list --changes` returns 77 entries (down from 129; the saga's 80 was a stale count; actual is 77 after the 52 archives + the 0/0 changes that resolved to Complete)
- [x] **F2** C2 — `AGENTS.md` + `CHEATSHEET.md` reference the new `core:openspec:status` task — *shipped by openspec/2026-10-30-saga-closure-and-baml-repair-v1 (Issue 4 — G2 skill-doc-reference box ticked; the change adds a "Top mise tasks" section to AGENTS.md and a saga-closed row to CHEATSHEET.md)*
- [x] **F3** C6 — 1 subagent handled the 52 archive moves + 1 subagent handled the 5 KEEP-stubs (sequential, not parallel, because the archives depend on the classification)

## Summary
- **A1-A3**: 3/3 done (57 zero-progress changes triaged + 5 KEEP stubs + 52 archives).
- **B1-B4**: 3/3 + 1 deferred (the JSON formatter).
- **C1-C3**: 3/3 done.
- **D1-D2**: 2/2 done.
- **E1**: done (STATUS.md update shipped in the saga-closure change).
- **E2**: done.
- **E3**: done (PR #211 merged; ticked by openspec/2026-10-30-saga-closure-and-baml-repair-v1).
- **F1**: done (77 active changes).
- **F2**: done (markdown reference shipped in the saga-closure change).
- **F3**: done.

## Headline numbers
| Metric | Before | After |
|--|--|--|
| Active openspec changes | 129 (with 80 zero-progress) | 77 (with 5 KEEP zero-progress) |
| Specs | 107 | 108 (+ media-intel-and-curriculum-hydration) |
| Archived changes (cumulative) | 389 | 441 (+ 52 from this change) |
| Skills | 77 | 77 (unchanged; 0 lint failures) |
| `core:openspec:status` task | no | yes |
| `core:lint:skills` task | no | yes |
| `openspec_status` marimo | no | yes |
