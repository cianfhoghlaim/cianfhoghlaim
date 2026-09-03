# Tasks: 2026-07-03-specs-and-session-9-health-report

## Phase 1 — Spec edits (5 min)

- [x] 1.1 Rewrite `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` (v4 24-model/4-backend)
- [x] 1.2 Append ADDED section to `openspec/specs/meaisinfhoghlaim-platform/spec.md`
- [x] 1.3 Append ADDED section to `openspec/specs/agent-memory-systems/spec.md`
- [x] 1.4 Append ADDED section to `openspec/specs/oideachais-pipeline/spec.md`

## Phase 2 — HEALTH_REPORT (2 min)

- [x] 2.1 Prepend Session 9 entry to `bonneagar/stacks/HEALTH_REPORT.md`

## Phase 3 — Openspec change files (5 min)

- [x] 3.1 Write `proposal.md` (this file)
- [x] 3.2 Write `tasks.md` (this file)
- [x] 3.3 Write 4 spec deltas under `specs/`

## Phase 4 — Validate (2 min)

- [x] 4.1 `openspec validate 2026-07-03-specs-and-session-9-health-report --strict`
- [x] 4.2 All 4 existing openspec validates still pass (no regression)

## Phase 5 — Stage commits (5 min)

- [x] 5.1 `git add openspec/specs/`
- [x] 5.2 `git commit -m "docs(specs): update 4 specs to v4 (meaisinfhoghlaim-ocr-htr rewrite + 3 addenda)"`
- [x] 5.3 `cd bonneagar && git add stacks/HEALTH_REPORT.md`
- [x] 5.4 `git commit -m "docs(health-report): Session 9 — 4 changes (infrastructure + LC5 + Gemini + specs)"`
- [x] 5.5 `cd .. && git add openspec/changes/2026-07-03-specs-and-session-9-health-report/`
- [x] 5.6 `git commit -m "docs(openspec): 2026-07-03-specs-and-session-9-health-report change"`
